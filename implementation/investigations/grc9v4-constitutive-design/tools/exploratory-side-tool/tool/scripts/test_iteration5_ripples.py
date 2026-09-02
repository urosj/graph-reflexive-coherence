#!/usr/bin/env python3
"""Focused ET-C5 scenario, profile, compiler, and round-trip tests."""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any, Callable, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, load_json_object, record_digest  # noqa: E402
from grcv4_explorer.errors import ScenarioValidationError  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.ripple import (  # noqa: E402
    AGGREGATE_SCHEMA,
    INDEX_SCHEMA,
    PROFILE_INDEPENDENT,
    RIPPLE_SCHEMA,
    SCENARIO_BUNDLE_SCHEMA,
    SCENARIO_SCHEMA,
    SHARD_SCHEMA,
    aggregate_rows,
    compile_ripple_row,
    load_ripple_context,
    load_scenario_bytes,
    make_scenario,
    scenario_bytes,
    serialize_selected_row,
    validate_scenario,
)


def expect_error(label: str, call: Callable[[], Any]) -> None:
    try:
        call()
    except ScenarioValidationError:
        return
    raise RuntimeError(f"ET-C5 fixture did not fail closed: {label}")


def refresh_scenario(value: dict[str, Any]) -> dict[str, Any]:
    value["scenario_digest"] = record_digest(value, "scenario_digest")
    return value


def refresh_row(value: dict[str, Any]) -> dict[str, Any]:
    value["ripple_digest"] = record_digest(value, "ripple_digest")
    return value


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    context = load_ripple_context(repo_root, SIDE_TOOL_ROOT)
    checks = 0

    if {
        SCENARIO_SCHEMA,
        RIPPLE_SCHEMA,
        SHARD_SCHEMA,
        INDEX_SCHEMA,
        AGGREGATE_SCHEMA,
        SCENARIO_BUNDLE_SCHEMA,
    } != {
        "grcv4_exploratory_scenario_v1",
        "grcv4_explorer_ET_C5_profile_ripple_v1",
        "grcv4_explorer_ET_C5_ripple_shard_v1",
        "grcv4_explorer_ET_C5_ripple_index_v1",
        "grcv4_explorer_ET_C5_all_profiles_aggregate_v1",
        "grcv4_explorer_ET_C5_scenario_bundle_v1",
    }:
        raise RuntimeError("ET-C5 schema population changed")
    checks += 1

    profiles = {
        "C1": [PROFILE_INDEPENDENT],
        "C2": ["A_CI"],
        "C3": ["A_CI", "A_CI_PC", "A_OS", "A_PC", "A_RG2b", "C_CI", "C_CI_PC", "C_OS", "C_PC", "C_RG2b"],
        "C4": ["A_CI", "A_CI_PC", "A_OS", "A_PC", "A_RG2b", "C_CI", "C_CI_PC", "C_OS", "C_PC", "C_RG2b"],
        "C5": ["A_CI"],
        "C6": [PROFILE_INDEPENDENT],
        "C7": ["A_CI"],
    }
    scenarios = [
        make_scenario(context, source_id, profile_id)
        for source_id, profile_ids in profiles.items()
        for profile_id in profile_ids
    ]
    if len(scenarios) != 25:
        raise RuntimeError("scenario expansion changed")
    checks += 1
    rows = [compile_ripple_row(context, scenario) for scenario in scenarios]
    ripple_rows = [row for row in rows if row is not None]
    if len(ripple_rows) != 24:
        raise RuntimeError("ripple expansion changed")
    checks += 1
    if compile_ripple_row(context, make_scenario(context, "C6", PROFILE_INDEPENDENT)) is not None:
        raise RuntimeError("non-load-bearing C6 emitted a ripple")
    checks += 1
    if [row["scenario"]["profile_id"] for row in ripple_rows if row["scenario"]["source_scenario_id"] == "C3"] != profiles["C3"]:
        raise RuntimeError("C3 profile expansion is incomplete")
    checks += 1
    for source_id in ("C2", "C5", "C7"):
        owned = [row for row in ripple_rows if row["scenario"]["source_scenario_id"] == source_id]
        if len(owned) != 1 or owned[0]["scenario"]["candidate_ids"] != ["V4-A-temporalized-W"]:
            raise RuntimeError(f"{source_id} escaped Candidate A")
        if owned[0]["scenario"]["profile_id"] != "A_CI":
            raise RuntimeError(f"{source_id} escaped A_CI")
        checks += 1

    c3_rows = [row for row in ripple_rows if row["scenario"]["source_scenario_id"] == "C3"]
    if not all(row["verification_obligations_at_risk"] for row in c3_rows):
        raise RuntimeError("C3 lost forward verification obligations")
    checks += 1
    if any(
        consequence["category"] == "verification_obligation_at_risk"
        for row in ripple_rows
        for consequence in row["transitive_consequences"]
    ):
        raise RuntimeError("verification obligation entered scientific transitive output")
    checks += 1
    if any(
        consequence["authority"] != "forward_work_only_not_evidence_or_debt"
        for row in ripple_rows
        for consequence in row["verification_obligations_at_risk"]
    ):
        raise RuntimeError("verification obligation gained evidence authority")
    checks += 1
    c4_rows = [row for row in ripple_rows if row["scenario"]["source_scenario_id"] == "C4"]
    if not all(row["blocked_overreads_at_risk"] for row in c4_rows):
        raise RuntimeError("C4 lost blocked-overread risks")
    checks += 1
    if any("exact_negative_activation" in row["result_statuses"] for row in c4_rows):
        raise RuntimeError("C4 falsely activated a negative claim")
    checks += 1
    if not all(
        any(item["category"] == "unknown_beyond_evidence_frontier" for item in row["transitive_consequences"])
        for row in ripple_rows
        if row["scenario"]["source_scenario_id"] != "C6"
    ):
        raise RuntimeError("unknown evidence frontier was not explicit")
    checks += 1
    if not all(
        consequence["source_edge_refs"]
        for row in ripple_rows
        for field in (
            "direct_consequences",
            "transitive_consequences",
            "blocked_overreads_at_risk",
            "verification_obligations_at_risk",
        )
        for consequence in row[field]
    ):
        raise RuntimeError("a compiled consequence lacks source-edge provenance")
    checks += 1
    if any(row["scope_basis"]["D10_2_family_counts_used"] for row in ripple_rows):
        raise RuntimeError("D10.2 family coverage leaked into profile scope")
    checks += 1
    if not all(
        row["scope_basis"]["profile_id"] == row["scenario"]["profile_id"]
        and bool(row["scope_basis"]["disabled_reduction_or_independent_boundary"])
        for row in ripple_rows
    ):
        raise RuntimeError("profile scope lacks its reduction/boundary receipt")
    checks += 1

    for scenario in scenarios:
        loaded = load_scenario_bytes(context, scenario_bytes(scenario))
        if canonical_bytes(loaded) != canonical_bytes(scenario):
            raise RuntimeError("canonical scenario load changed bytes")
        checks += 1
    for row in ripple_rows:
        if serialize_selected_row(context, row) != scenario_bytes(row["scenario"]):
            raise RuntimeError("selected-row round trip changed scenario bytes")
        checks += 1

    baseline = make_scenario(context, "C2", "A_CI")
    malformed = copy.deepcopy(baseline)
    malformed["unknown_field"] = "not_admitted"
    expect_error("unknown_field", lambda: validate_scenario(context, malformed))
    checks += 1
    malformed = copy.deepcopy(baseline)
    del malformed["profile_id"]
    expect_error("missing_scope", lambda: validate_scenario(context, malformed))
    checks += 1
    stale = refresh_scenario({**baseline, "source_bundle_digest": "0" * 64})
    expect_error("stale_source", lambda: validate_scenario(context, stale))
    checks += 1
    stale = refresh_scenario({**baseline, "graph_digest": "0" * 64})
    expect_error("stale_graph", lambda: validate_scenario(context, stale))
    checks += 1
    stale = refresh_scenario({**baseline, "baseline_record_digest": "0" * 64})
    expect_error("stale_baseline", lambda: validate_scenario(context, stale))
    checks += 1
    changed = copy.deepcopy(baseline)
    changed["mutations"][0]["declared_payload"]["term_id"] = "browser_authored"
    refresh_scenario(changed)
    expect_error("browser_authored_mutation", lambda: validate_scenario(context, changed))
    checks += 1
    changed = copy.deepcopy(baseline)
    changed["mutations"].append(changed["mutations"][0])
    refresh_scenario(changed)
    expect_error("multiple_mutations", lambda: validate_scenario(context, changed))
    checks += 1
    changed = refresh_scenario({**baseline, "profile_id": "C_CI"})
    expect_error("profile_leak", lambda: validate_scenario(context, changed))
    checks += 1
    changed = refresh_scenario({**baseline, "candidate_ids": ["V4-C-constitutive-C-sector"]})
    expect_error("candidate_leak", lambda: validate_scenario(context, changed))
    checks += 1
    changed = refresh_scenario({**baseline, "realization_ids": []})
    expect_error("realization_loss", lambda: validate_scenario(context, changed))
    checks += 1
    changed = refresh_scenario({**baseline, "kernel_schema_version": "future"})
    expect_error("kernel_schema", lambda: validate_scenario(context, changed))
    checks += 1
    changed = refresh_scenario({**baseline, "result_class": "scientific_evidence"})
    expect_error("result_class", lambda: validate_scenario(context, changed))
    checks += 1
    changed = refresh_scenario({**baseline, "source_result_digest": "0" * 64})
    expect_error("result_digest", lambda: validate_scenario(context, changed))
    checks += 1
    changed = refresh_scenario({**baseline, "scenario_id": "browser-authored"})
    expect_error("scenario_id", lambda: validate_scenario(context, changed))
    checks += 1
    changed = refresh_scenario({**baseline, "source_scenario_id": "C8"})
    expect_error("unknown_source_scenario", lambda: validate_scenario(context, changed))
    checks += 1
    expect_error(
        "noncanonical_bytes",
        lambda: load_scenario_bytes(context, canonical_bytes(baseline)),
    )
    checks += 1

    row = cast(dict[str, Any], compile_ripple_row(context, baseline))
    changed_row = copy.deepcopy(row)
    changed_row["direct_consequences"] = []
    expect_error("altered_row", lambda: serialize_selected_row(context, changed_row))
    checks += 1
    changed_row = copy.deepcopy(row)
    changed_row["browser_may_recompute"] = True
    refresh_row(changed_row)
    expect_error("browser_recompute", lambda: serialize_selected_row(context, changed_row))
    checks += 1

    first = aggregate_rows(context, ripple_rows)
    second = aggregate_rows(context, list(reversed(ripple_rows)))
    if canonical_bytes(first) != canonical_bytes(second):
        raise RuntimeError("aggregate depends on input order")
    checks += 1
    if first["projection_only"] is not True or first["row_count"] != 24:
        raise RuntimeError("aggregate gained independent authority")
    checks += 1

    bundle = load_json_object(SIDE_TOOL_ROOT / "records/ETC5ScenarioBundle.json")
    index = load_json_object(SIDE_TOOL_ROOT / "records/ETC5RippleShardIndex.json")
    if bundle["scenario_count"] != 25 or index["row_count"] != 24:
        raise RuntimeError("built bundle population mismatch")
    checks += 1
    if any(shard["row_count"] > index["shard_row_limit"] for shard in index["shards"]):
        raise RuntimeError("shard row bound violated")
    checks += 1
    if sum(shard["row_count"] for shard in index["shards"]) != index["row_count"]:
        raise RuntimeError("shard coverage was truncated")
    checks += 1
    print(f"ET_C5_TEST_PASS checks={checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
