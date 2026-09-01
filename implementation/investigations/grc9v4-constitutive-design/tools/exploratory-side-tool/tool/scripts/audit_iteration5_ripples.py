#!/usr/bin/env python3
"""Independent raw-record audit of ET-C5 scenarios, shards, and ripple rows."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import (  # noqa: E402
    canonical_bytes,
    file_sha256,
    load_json_object,
    record_digest,
)
from grcv4_explorer.counterfactual import load_counterfactual_context  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402


PROFILE_INDEPENDENT = "__profile_independent__"
ALL_PROFILES = [
    "A_CI",
    "A_CI_PC",
    "A_OS",
    "A_PC",
    "A_RG2b",
    "C_CI",
    "C_CI_PC",
    "C_OS",
    "C_PC",
    "C_RG2b",
]
EXPECTED_PROFILES = {
    "C1": [PROFILE_INDEPENDENT],
    "C2": ["A_CI"],
    "C3": ALL_PROFILES,
    "C4": ALL_PROFILES,
    "C5": ["A_CI"],
    "C6": [PROFILE_INDEPENDENT],
    "C7": ["A_CI"],
}
PROFILE_CANDIDATES = {
    "A": "V4-A-temporalized-W",
    "C": "V4-C-constitutive-C-sector",
}
SCENARIO_FIELDS = {
    "schema_version",
    "kernel_schema_version",
    "scenario_id",
    "source_scenario_id",
    "source_bundle_digest",
    "graph_digest",
    "baseline_record_id",
    "baseline_record_digest",
    "profile_id",
    "candidate_ids",
    "realization_ids",
    "mutations",
    "source_result_digest",
    "result_class",
    "scenario_digest",
}


def require(condition: bool, label: str, checks: list[str]) -> None:
    if not condition:
        raise RuntimeError(f"ET-C5 audit failed: {label}")
    checks.append(label)


def load_canonical(path: Path, checks: list[str]) -> dict[str, Any]:
    value = load_json_object(path)
    require(path.read_bytes() == canonical_bytes(value) + b"\n", f"canonical:{path.name}", checks)
    return value


def edge_ref(context: Any, edge: dict[str, Any]) -> dict[str, Any]:
    source = context.documents_by_record[edge["source_record_id"]]
    return {
        "edge_id": edge["edge_id"],
        "source": edge["source"],
        "target": edge["target"],
        "relation": edge["relation"],
        "support_semantic": edge["support_semantic"],
        "source_record_id": edge["source_record_id"],
        "source_record_digest": source.declared_digest,
        "source_json_pointer": edge["source_json_pointer"],
    }


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    checks: list[str] = []
    records = SIDE_TOOL_ROOT / "records"
    context = load_counterfactual_context(repo_root, SIDE_TOOL_ROOT)
    et_c4_gate = load_canonical(records / "ETC4BoundedCounterfactualKernel.json", checks)
    et_c4_report = load_canonical(records / "ETC4CounterfactualScenarioReport.json", checks)
    gate = load_canonical(records / "ETC5RippleAndScenarioContract.json", checks)
    bundle = load_canonical(records / "ETC5ScenarioBundle.json", checks)
    index = load_canonical(records / "ETC5RippleShardIndex.json", checks)
    aggregate = load_canonical(records / "ETC5AllProfilesAggregate.json", checks)

    require(et_c4_gate["status"] == "accepted", "ET_C4_accepted", checks)
    require(et_c4_gate["record_digest"] == record_digest(et_c4_gate, "record_digest"), "ET_C4_digest", checks)
    require(et_c4_report["report_digest"] == record_digest(et_c4_report, "report_digest"), "ET_C4_report_digest", checks)
    require(gate["status"] == "accepted", "gate_accepted", checks)
    require(bundle["status"] == "accepted", "bundle_accepted", checks)
    require(index["status"] == "accepted", "index_accepted", checks)
    require(gate["record_digest"] == record_digest(gate, "record_digest"), "gate_digest", checks)
    require(gate["authority"]["browser_application_implemented"] is False, "browser_absent", checks)
    require(gate["authority"]["browser_propagation_rule_embedded"] is False, "browser_rules_absent", checks)
    require(gate["authority"]["iteration_6_authorized"] is True, "iteration_6_authorized", checks)
    require(gate["acceptance_requirements"]["human_review"] == "accepted", "human_review_accepted", checks)
    require(gate["predecessor"]["record_digest"] == et_c4_gate["record_digest"], "ET_C4_binding", checks)
    require(bundle["scenario_bundle_digest"] == record_digest(bundle, "scenario_bundle_digest"), "bundle_digest", checks)
    require(index["index_digest"] == record_digest(index, "index_digest"), "index_digest", checks)
    require(aggregate["aggregate_digest"] == record_digest(aggregate, "aggregate_digest"), "aggregate_digest", checks)
    require(bundle["scenario_bundle_digest"] == index["scenario_bundle_digest"], "bundle_index_binding", checks)
    require(aggregate["aggregate_digest"] == index["all_profiles_aggregate_digest"], "aggregate_index_binding", checks)
    require(bundle["source_bundle_digest"] == context.source_bundle_digest, "source_bundle_binding", checks)
    require(bundle["graph_digest"] == context.graph_digest, "graph_binding", checks)

    source_rows = {row["scenario_id"]: row for row in et_c4_report["scenarios"]}
    scenarios = bundle["scenarios"]
    require(bundle["scenario_count"] == 25 == len(scenarios), "scenario_count", checks)
    require(len({row["scenario_id"] for row in scenarios}) == 25, "scenario_IDs_unique", checks)
    scenario_by_digest: dict[str, dict[str, Any]] = {}
    scenario_counts: Counter[str] = Counter()
    profiles = {
        row["identifier"]: row["attributes"]
        for row in context.nodes.values()
        if row["kind"] == "profile"
    }
    for scenario in scenarios:
        require(set(scenario) == SCENARIO_FIELDS, f"scenario_fields:{scenario['scenario_id']}", checks)
        require(scenario["schema_version"] == "grcv4_exploratory_scenario_v1", f"scenario_schema:{scenario['scenario_id']}", checks)
        require(scenario["kernel_schema_version"] == "grcv4_explorer_ET_C4_counterfactual_result_v1", f"kernel_schema:{scenario['scenario_id']}", checks)
        require(scenario["scenario_digest"] == record_digest(scenario, "scenario_digest"), f"scenario_digest:{scenario['scenario_id']}", checks)
        source_id = scenario["source_scenario_id"]
        source_result = source_rows[source_id]["result"]
        require(source_id in EXPECTED_PROFILES, f"source_scenario_admitted:{source_id}", checks)
        require(scenario["profile_id"] in EXPECTED_PROFILES[source_id], f"profile_scope:{scenario['scenario_id']}", checks)
        require(canonical_bytes(scenario["mutations"]) == canonical_bytes([source_result["mutation"]]), f"mutation_identity:{scenario['scenario_id']}", checks)
        require(scenario["source_result_digest"] == source_result["result_digest"], f"result_identity:{scenario['scenario_id']}", checks)
        require(scenario["baseline_record_id"] == source_result["mutation"]["baseline_record_id"], f"baseline_ID:{scenario['scenario_id']}", checks)
        require(scenario["baseline_record_digest"] == source_result["mutation"]["baseline_record_digest"], f"baseline_digest:{scenario['scenario_id']}", checks)
        require(scenario["source_bundle_digest"] == context.source_bundle_digest, f"scenario_source:{scenario['scenario_id']}", checks)
        require(scenario["graph_digest"] == context.graph_digest, f"scenario_graph:{scenario['scenario_id']}", checks)
        profile_id = scenario["profile_id"]
        if profile_id != PROFILE_INDEPENDENT:
            short = profiles[profile_id]["candidate"]
            require(scenario["candidate_ids"] == [PROFILE_CANDIDATES[short]], f"profile_candidate:{scenario['scenario_id']}", checks)
            require(bool(profiles[profile_id]["V3_reduction"]), f"disabled_reduction:{scenario['scenario_id']}", checks)
        scenario_counts[source_id] += 1
        scenario_by_digest[scenario["scenario_digest"]] = scenario
    require(dict(sorted(scenario_counts.items())) == {key: len(value) for key, value in EXPECTED_PROFILES.items()}, "scenario_profile_expansion", checks)
    require(bundle["zero_ripple_scenario_ids"] == ["ET-C5-C6-__profile_independent__"], "C6_zero_ripple", checks)

    require(index["shard_count"] == 3 == len(index["shards"]), "shard_count", checks)
    require(index["shard_row_limit"] == 8, "shard_limit", checks)
    rows: list[dict[str, Any]] = []
    edge_by_id = {row["edge_id"]: row for row in context.propagation_edges}
    for descriptor in index["shards"]:
        path = SIDE_TOOL_ROOT / descriptor["path"]
        require(not Path(descriptor["path"]).is_absolute(), f"relative_shard_path:{descriptor['shard_id']}", checks)
        shard = load_canonical(path, checks)
        require(shard["payload_digest"] == record_digest(shard, "payload_digest"), f"shard_digest:{descriptor['shard_id']}", checks)
        require(shard["payload_digest"] == descriptor["payload_digest"], f"descriptor_digest:{descriptor['shard_id']}", checks)
        require(shard["row_count"] == descriptor["row_count"] == len(shard["rows"]), f"descriptor_count:{descriptor['shard_id']}", checks)
        require(shard["row_count"] <= 8, f"shard_bound:{descriptor['shard_id']}", checks)
        require(shard["profile_coverage"] == descriptor["profile_coverage"], f"descriptor_profiles:{descriptor['shard_id']}", checks)
        require(shard["target_range"] == descriptor["target_range"], f"descriptor_targets:{descriptor['shard_id']}", checks)
        require(shard["source_bundle_digest"] == context.source_bundle_digest, f"shard_source:{descriptor['shard_id']}", checks)
        rows.extend(shard["rows"])
    require(index["row_count"] == 24 == len(rows), "ripple_row_count", checks)
    require(len({row["ripple_digest"] for row in rows}) == 24, "ripple_IDs_unique", checks)

    row_scenarios: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    for row in rows:
        require(row["schema"] == "grcv4_explorer_ET_C5_profile_ripple_v1", f"ripple_schema:{row['ripple_digest']}", checks)
        require(row["ripple_digest"] == record_digest(row, "ripple_digest"), f"ripple_digest:{row['ripple_digest']}", checks)
        require(row["browser_may_recompute"] is False, f"browser_read_only:{row['ripple_digest']}", checks)
        scenario = scenario_by_digest[row["scenario_digest"]]
        require(canonical_bytes(row["scenario"]) == canonical_bytes(scenario), f"embedded_scenario:{row['ripple_digest']}", checks)
        require(row["ripple_key"]["profile_id"] == scenario["profile_id"], f"ripple_profile:{row['ripple_digest']}", checks)
        require(row["ripple_key"]["candidate_ids"] == scenario["candidate_ids"], f"ripple_candidate:{row['ripple_digest']}", checks)
        require(row["ripple_key"]["realization_ids"] == scenario["realization_ids"], f"ripple_realization:{row['ripple_digest']}", checks)
        require(row["scope_basis"]["profile_id"] == scenario["profile_id"] and row["scope_basis"]["candidate_ids"] == scenario["candidate_ids"] and row["scope_basis"]["realization_ids"] == scenario["realization_ids"], f"scope_basis:{row['ripple_digest']}", checks)
        require(row["scope_basis"]["D10_2_family_counts_used"] is False, f"family_counts_not_scope:{row['ripple_digest']}", checks)
        require(row["source_result_digest"] == scenario["source_result_digest"], f"ripple_result:{row['ripple_digest']}", checks)
        require(canonical_bytes(scenario) + b"\n" == canonical_bytes(row["scenario"]) + b"\n", f"round_trip:{row['ripple_digest']}", checks)
        source_id = scenario["source_scenario_id"]
        row_scenarios[source_id] += 1
        if source_id in {"C2", "C5", "C7"}:
            require(scenario["profile_id"] == "A_CI", f"A_profile_isolation:{source_id}", checks)
            require(scenario["candidate_ids"] == ["V4-A-temporalized-W"], f"A_candidate_isolation:{source_id}", checks)
        for field in (
            "direct_consequences",
            "transitive_consequences",
            "blocked_overreads_at_risk",
            "verification_obligations_at_risk",
        ):
            for consequence in row[field]:
                require(consequence["consequence_digest"] == record_digest(consequence, "consequence_digest"), f"consequence_digest:{row['ripple_digest']}:{consequence['consequence_digest']}", checks)
                require(bool(consequence["source_edge_refs"]), f"consequence_provenance:{consequence['consequence_digest']}", checks)
                for reference in consequence["source_edge_refs"]:
                    require(reference["edge_id"] in edge_by_id, f"edge_resolves:{reference['edge_id']}", checks)
                    require(reference == edge_ref(context, edge_by_id[reference["edge_id"]]), f"edge_exact:{reference['edge_id']}", checks)
                category_counts[consequence["category"]] += 1
        require(all(item["category"] != "verification_obligation_at_risk" for item in row["transitive_consequences"]), f"obligation_not_transitive:{row['ripple_digest']}", checks)
        require(all(item["authority"] == "forward_work_only_not_evidence_or_debt" for item in row["verification_obligations_at_risk"]), f"obligation_authority:{row['ripple_digest']}", checks)
        if source_id == "C4":
            require(bool(row["blocked_overreads_at_risk"]), f"C4_lock_risk:{row['ripple_digest']}", checks)
            require("exact_negative_activation" not in row["result_statuses"], f"C4_no_false_activation:{row['ripple_digest']}", checks)
    require("C6" not in row_scenarios, "C6_emits_no_row", checks)
    require(row_scenarios == Counter({"C1": 1, "C2": 1, "C3": 10, "C4": 10, "C5": 1, "C7": 1}), "ripple_profile_expansion", checks)
    require(category_counts["unknown_beyond_evidence_frontier"] > 0, "unknown_frontier_explicit", checks)
    require(category_counts["verification_obligation_at_risk"] > 0, "forward_obligations_explicit", checks)

    ordered = sorted(rows, key=lambda row: (row["ripple_key"]["target_id"], row["ripple_key"]["profile_id"], row["scenario_digest"]))
    expected_profile_counts = Counter(row["ripple_key"]["profile_id"] for row in ordered)
    require(aggregate["projection_only"] is True, "aggregate_projection_only", checks)
    require(aggregate["row_count"] == len(ordered), "aggregate_row_count", checks)
    require(aggregate["ripple_digests"] == [row["ripple_digest"] for row in ordered], "aggregate_rows_exact", checks)
    require(aggregate["profile_row_counts"] == dict(sorted(expected_profile_counts.items())), "aggregate_profiles_exact", checks)
    require(aggregate["direct_consequence_count"] == sum(len(row["direct_consequences"]) for row in ordered), "aggregate_direct_exact", checks)
    require(aggregate["transitive_consequence_count"] == sum(len(row["transitive_consequences"]) for row in ordered), "aggregate_transitive_exact", checks)
    require(aggregate["verification_obligation_risk_count"] == sum(len(row["verification_obligations_at_risk"]) for row in ordered), "aggregate_obligations_exact", checks)

    manifest = load_json_object(records / "ETC1SourceBundleManifest.json")
    for source in manifest["records"]:
        require(file_sha256(repo_root / source["path"]) == source["file_sha256"], f"source_unchanged:{source['record_identifier']}", checks)
    web_files = {
        path.relative_to(TOOL_ROOT / "web").as_posix()
        for path in (TOOL_ROOT / "web").rglob("*")
        if path.is_file()
    }
    require(
        web_files == {"package-lock.json", "package.json"},
        "browser_not_implemented",
        checks,
    )
    print(
        "ET_C5_AUDIT_PASS "
        f"checks={len(checks)} scenarios={len(scenarios)} rows={len(rows)} "
        f"edge_references={sum(category_counts.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
