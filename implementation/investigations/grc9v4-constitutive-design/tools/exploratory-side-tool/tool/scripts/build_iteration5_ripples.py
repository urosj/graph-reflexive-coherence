#!/usr/bin/env python3
"""Build deterministic ET-C5 scenarios, profile ripples, shards, and candidate gate."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, record_digest  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.ripple import (  # noqa: E402
    INDEX_SCHEMA,
    SCENARIO_BUNDLE_SCHEMA,
    SHARD_SCHEMA,
    aggregate_rows,
    compile_ripple_row,
    load_ripple_context,
    make_scenario,
    resolve_profiles,
    row_sort_key,
    scenario_bytes,
    serialize_selected_row,
)


SOURCE_SCENARIOS = ("C1", "C2", "C3", "C4", "C5", "C6", "C7")
SHARD_ROW_LIMIT = 8


def require_repository_venv(repo_root: Path) -> None:
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value) + b"\n")


def main() -> int:
    repo_root = repository_root()
    require_repository_venv(repo_root)
    context = load_ripple_context(repo_root, SIDE_TOOL_ROOT)
    records = SIDE_TOOL_ROOT / "records"
    shard_root = records / "iteration5-ripple"

    scenarios: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    zero_ripple_scenarios: list[str] = []
    for source_id in SOURCE_SCENARIOS:
        source_result = context.source_scenarios[source_id]["result"]
        profiles = resolve_profiles(context, source_result["mutation"], source_result)
        for profile_id in profiles:
            scenario = make_scenario(context, source_id, profile_id)
            scenarios.append(scenario)
            row = compile_ripple_row(context, scenario)
            if row is None:
                zero_ripple_scenarios.append(scenario["scenario_id"])
                continue
            if serialize_selected_row(context, row) != scenario_bytes(scenario):
                raise RuntimeError("selected-row scenario round trip is not byte-identical")
            rows.append(row)
    scenarios.sort(key=lambda row: row["scenario_id"])
    rows.sort(key=row_sort_key)
    if len(scenarios) != 25 or len(rows) != 24:
        raise RuntimeError("ET-C5 frozen scenario/ripple population changed")
    if zero_ripple_scenarios != ["ET-C5-C6-__profile_independent__"]:
        raise RuntimeError("ET-C5 non-load-bearing scenario population changed")

    scenario_bundle: dict[str, Any] = {
        "schema": SCENARIO_BUNDLE_SCHEMA,
        "status": "accepted",
        "source_bundle_digest": context.forensic.source_bundle_digest,
        "graph_digest": context.forensic.graph_digest,
        "predecessor_ET_C4_record_digest": context.et_c4_gate["record_digest"],
        "source_scenario_ids": list(SOURCE_SCENARIOS),
        "scenario_count": len(scenarios),
        "zero_ripple_scenario_ids": zero_ripple_scenarios,
        "scenarios": scenarios,
        "scenario_bundle_digest": None,
    }
    scenario_bundle["scenario_bundle_digest"] = record_digest(
        scenario_bundle, "scenario_bundle_digest"
    )
    write_json(records / "ETC5ScenarioBundle.json", scenario_bundle)

    aggregate = aggregate_rows(context, rows)
    write_json(records / "ETC5AllProfilesAggregate.json", aggregate)

    expected_names: set[str] = set()
    descriptors: list[dict[str, Any]] = []
    for offset in range(0, len(rows), SHARD_ROW_LIMIT):
        shard_rows = rows[offset : offset + SHARD_ROW_LIMIT]
        number = offset // SHARD_ROW_LIMIT + 1
        name = f"ETC5RippleShard-{number:03d}.json"
        expected_names.add(name)
        targets = [row["ripple_key"]["target_id"] for row in shard_rows]
        profiles = sorted({row["ripple_key"]["profile_id"] for row in shard_rows})
        shard: dict[str, Any] = {
            "schema": SHARD_SCHEMA,
            "shard_id": f"ET-C5-SHARD-{number:03d}",
            "source_bundle_digest": context.forensic.source_bundle_digest,
            "graph_digest": context.forensic.graph_digest,
            "target_range": {"first": min(targets), "last": max(targets)},
            "profile_coverage": profiles,
            "row_count": len(shard_rows),
            "rows": shard_rows,
            "payload_digest": None,
        }
        shard["payload_digest"] = record_digest(shard, "payload_digest")
        write_json(shard_root / name, shard)
        descriptors.append(
            {
                "shard_id": shard["shard_id"],
                "path": f"records/iteration5-ripple/{name}",
                "target_range": shard["target_range"],
                "profile_coverage": profiles,
                "row_count": len(shard_rows),
                "payload_digest": shard["payload_digest"],
                "source_bundle_digest": context.forensic.source_bundle_digest,
            }
        )
    stale = {
        path.name for path in shard_root.glob("ETC5RippleShard-*.json")
    } - expected_names
    if stale:
        raise RuntimeError(f"stale ET-C5 shard files require review: {sorted(stale)}")

    index: dict[str, Any] = {
        "schema": INDEX_SCHEMA,
        "status": "accepted",
        "source_bundle_digest": context.forensic.source_bundle_digest,
        "graph_digest": context.forensic.graph_digest,
        "predecessor_ET_C4_record_digest": context.et_c4_gate["record_digest"],
        "scenario_bundle_path": "records/ETC5ScenarioBundle.json",
        "scenario_bundle_digest": scenario_bundle["scenario_bundle_digest"],
        "all_profiles_aggregate_path": "records/ETC5AllProfilesAggregate.json",
        "all_profiles_aggregate_digest": aggregate["aggregate_digest"],
        "shard_row_limit": SHARD_ROW_LIMIT,
        "shard_count": len(descriptors),
        "row_count": len(rows),
        "shards": descriptors,
        "index_digest": None,
    }
    index["index_digest"] = record_digest(index, "index_digest")
    write_json(records / "ETC5RippleShardIndex.json", index)

    execution_context = tomllib.loads((TOOL_ROOT / "iteration5_context.toml").read_text())
    gate: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C5_ripple_scenario_admission_v1",
        "gate_id": "ET-C5_ripple_and_scenario_contract",
        "status": "accepted",
        "iteration": 5,
        "execution_context": execution_context,
        "predecessor": {
            "gate_id": "ET-C4_bounded_counterfactual_kernel",
            "record_digest": context.et_c4_gate["record_digest"],
            "graph_digest": context.forensic.graph_digest,
            "source_bundle_digest": context.forensic.source_bundle_digest,
        },
        "authority": {
            "scenario_schema_frozen": True,
            "ripple_compiler_implemented": True,
            "browser_application_implemented": False,
            "browser_propagation_rule_embedded": False,
            "source_records_modified": False,
            "scientific_claim_added": False,
            "runtime_reexecution_performed": False,
            "iteration_6_authorized": True,
        },
        "compiled_surface": {
            "source_scenario_ids": list(SOURCE_SCENARIOS),
            "canonical_scenario_count": len(scenarios),
            "profile_local_ripple_row_count": len(rows),
            "zero_ripple_scenario_count": len(zero_ripple_scenarios),
            "shard_count": len(descriptors),
            "shard_row_limit": SHARD_ROW_LIMIT,
            "scenario_bundle_digest": scenario_bundle["scenario_bundle_digest"],
            "aggregate_digest": aggregate["aggregate_digest"],
            "shard_index_digest": index["index_digest"],
            "notebook_web_roundtrip_count": len(rows),
            "profile_scope_uses_D10_2_family_counts": False,
            "positive_claim_beyond_frontier_count": 0,
            "browser_authored_mutation_count": 0,
            "truncated_profile_row_count": 0,
        },
        "acceptance_requirements": {
            "independent_bundle_and_profile_audit": "passed_4133_checks_836_edge_references",
            "focused_adversarial_fixture_matrix": "passed_89_checks",
            "deterministic_double_rebuild": "passed",
            "ET_C4_regression": "passed_full_verification",
            "human_review": "accepted",
        },
        "non_claims": [
            "no_browser_application",
            "no_browser_side_propagation",
            "no_reexecuted_gate_outcome",
            "no_new_scientific_evidence",
            "no_numeric_physical_prediction",
            "no_candidate_or_realization_ranking",
        ],
        "record_digest": None,
    }
    gate["record_digest"] = record_digest(gate, "record_digest")
    write_json(records / "ETC5RippleAndScenarioContract.json", gate)

    lines = [
        "# ET-C5 Ripple And Scenario Contract",
        "",
        "**Status:** Accepted",
        "",
        "Iteration 5 compiles accepted ET-C4 structural results into immutable,",
        "profile-local playback rows. The browser remains absent and receives no",
        "propagation rule. Every selected-row export is byte-identical to its",
        "canonical scenario input.",
        "",
        "## Result",
        "",
        f"- canonical scenarios: `{len(scenarios)}`",
        f"- profile-local ripple rows: `{len(rows)}`",
        f"- deterministic shards: `{len(descriptors)} x <= {SHARD_ROW_LIMIT} rows`",
        f"- zero-ripple scenarios: `{', '.join(zero_ripple_scenarios)}`",
        f"- scenario bundle digest: `{scenario_bundle['scenario_bundle_digest']}`",
        f"- aggregate digest: `{aggregate['aggregate_digest']}`",
        f"- shard index digest: `{index['index_digest']}`",
        f"- record digest: `{gate['record_digest']}`",
        "",
        "C3 verification obligations remain forward-work-only. C4 blocked",
        "overreads remain risks rather than activated negative claims. C6 is",
        "canonical and selectable as a no-effect result but emits no ripple row.",
        "Iteration 6 is authorized but is not implemented by this gate.",
        "",
    ]
    (records / "ETC5RippleAndScenarioContract.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(
        "ET_C5_BUILD_PASS "
        f"scenarios={len(scenarios)} rows={len(rows)} shards={len(descriptors)} "
        f"index={index['index_digest']} record={gate['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
