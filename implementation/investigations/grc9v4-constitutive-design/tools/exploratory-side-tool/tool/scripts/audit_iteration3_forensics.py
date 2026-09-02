#!/usr/bin/env python3
"""Independent ET-C3 audit over raw accepted files and emitted traces."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]


def canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def value_digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"non-object JSON: {path.name}")
    return cast(dict[str, Any], value)


def resolve_pointer(value: Any, pointer: str) -> Any:
    if pointer in {"", "/"}:
        return value
    current = value
    for token in pointer.lstrip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(token)]
        elif isinstance(current, dict):
            current = current[token]
        else:
            raise RuntimeError(f"pointer traverses scalar: {pointer}")
    return current


def require(condition: bool, label: str, checks: list[str]) -> None:
    if not condition:
        raise RuntimeError(f"ET-C3 audit failed: {label}")
    checks.append(label)


def main() -> int:
    repo_root = next(
        parent
        for parent in SIDE_TOOL_ROOT.parents
        if (parent / "pyproject.toml").is_file()
    )
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    records = SIDE_TOOL_ROOT / "records"
    report = load(records / "ETC3ForensicScenarioReport.json")
    gate = load(records / "ETC3ForensicReconstructionSurface.json")
    graph = load(records / "ETC2GraphSnapshot.json")
    manifest = load(records / "ETC1SourceBundleManifest.json")
    checks: list[str] = []

    require(
        report["report_digest"]
        == value_digest({k: v for k, v in report.items() if k != "report_digest"}),
        "report_digest",
        checks,
    )
    require(
        gate["record_digest"]
        == value_digest({k: v for k, v in gate.items() if k != "record_digest"}),
        "gate_digest",
        checks,
    )
    require(
        graph["graph_digest"]
        == value_digest({k: v for k, v in graph.items() if k != "graph_digest"}),
        "graph_digest",
        checks,
    )
    require(
        report["graph_digest"] == graph["graph_digest"],
        "report_graph_binding",
        checks,
    )
    require(
        report["source_bundle_digest"] == manifest["source_bundle_digest"],
        "report_source_bundle_binding",
        checks,
    )

    sources: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for row in manifest["records"]:
        source = load(repo_root / row["path"])
        sources[row["record_identifier"]] = (row, source)
    edges = {row["edge_id"]: row for row in graph["propagation_edges"]}
    scenarios = {row["scenario_id"]: row for row in report["scenarios"]}
    require(len(scenarios) == 12, "scenario_population", checks)
    require(
        set(scenarios)
        == {"F1", "F2", "F3A", "F3B", "F4", "F5", "F6", "F7", "F8A", "F8B", "E3", "E4"},
        "scenario_identity",
        checks,
    )

    emitted_rows = 0
    emitted_edges = 0
    for scenario_id, scenario in sorted(scenarios.items()):
        trace = scenario["trace"]
        require(
            trace["trace_digest"]
            == value_digest({k: v for k, v in trace.items() if k != "trace_digest"}),
            f"{scenario_id}_trace_digest",
            checks,
        )
        require(
            trace["output_class"] == "forensic_evidence_trace",
            f"{scenario_id}_forensic_only",
            checks,
        )
        require(
            trace["row_count"] == len(trace["rows"]),
            f"{scenario_id}_row_count",
            checks,
        )
        for row in trace["rows"]:
            emitted_rows += 1
            source_ref = row["source_ref"]
            require(
                source_ref["record_id"] in sources,
                f"{scenario_id}_{row['row_id']}_source_admitted",
                checks,
            )
            manifest_row, source = sources[source_ref["record_id"]]
            require(
                source_ref["record_digest"] == manifest_row["canonical_digest"],
                f"{scenario_id}_{row['row_id']}_source_digest",
                checks,
            )
            resolve_pointer(source, source_ref["source_json_pointer"])
            require(
                bool(row["edge_refs"]),
                f"{scenario_id}_{row['row_id']}_edge_bound",
                checks,
            )
            for edge_ref in row["edge_refs"]:
                emitted_edges += 1
                actual = edges.get(edge_ref["edge_id"])
                require(actual is not None, "edge_exists", checks)
                assert actual is not None
                for key in (
                    "source",
                    "target",
                    "relation",
                    "support_semantic",
                    "source_record_id",
                    "source_json_pointer",
                ):
                    require(
                        edge_ref[key] == actual[key],
                        f"edge_exact_{key}",
                        checks,
                    )
                edge_source = sources[actual["source_record_id"]][0]
                require(
                    edge_ref["source_record_digest"]
                    == edge_source["canonical_digest"],
                    "edge_source_digest",
                    checks,
                )

    f1_nodes = {
        row["node_id"]
        for row in scenarios["F1"]["trace"]["rows"][0]["payload"]["nodes"]
    }
    for required in (
        "gate_record:GRC9V4-CD-D7G-v2",
        "gate_record:GRC9V4-GTRS-COMP-v1",
        "gate_record:GRC9V4-CD-D9-v1",
        "normative_object:CORE-C-AUTHORITY",
        "equation_contract:D10.2-EC-PARENT-CORE-C-AUTHORITY",
    ):
        require(required in f1_nodes, f"F1_contains_{required}", checks)
    require(
        not any(value.startswith("verification_obligation:") for value in f1_nodes),
        "F1_excludes_forward_obligations",
        checks,
    )

    f2 = scenarios["F2"]["trace"]["rows"]
    require(f2[0]["classification"] == "routed", "F2_transformation", checks)
    require(
        f2[0]["payload"]["activation_condition"]
        == "exclusive_preference_or_numeric_ranking_claimed",
        "F2_activation_condition",
        checks,
    )
    require(
        f2[1]["classification"] == "forward_verification_routing",
        "F2_obligation_is_forward",
        checks,
    )

    f3_classes = {row["classification"] for row in scenarios["F3B"]["trace"]["rows"]}
    require(
        {"added", "inherited", "routed", "superseded"} <= f3_classes,
        "F3_contribution_classes",
        checks,
    )
    f3_payloads = [row["payload"] for row in scenarios["F3B"]["trace"]["rows"]]
    b_row = next(
        row
        for row in f3_payloads
        if isinstance(row, dict)
        and row.get("candidate_id") == "V4-B-independent-derived-carrier"
    )
    require(b_row["candidate_rejected"] is False, "F3_B_not_rejected", checks)
    require(
        b_row["complete_candidate_local_transition"] is False,
        "F3_B_not_complete",
        checks,
    )

    f4_branch = next(
        row
        for row in scenarios["F4"]["trace"]["rows"]
        if row["classification"] == "parallel_realization_branches"
    )["payload"]
    require(
        set(f4_branch["profile_nodes"])
        == {"profile:A_CI", "profile:A_OS", "profile:A_RG2b", "profile:A_PC", "profile:A_CI_PC"},
        "F4_parallel_profile_population",
        checks,
    )
    require(
        any(row["classification"] == "narrowed" for row in scenarios["F4"]["trace"]["rows"]),
        "F4_D10_2_promotion_narrowed",
        checks,
    )

    for scenario_id in ("F5", "E3"):
        payloads = [row["payload"] for row in scenarios[scenario_id]["trace"]["rows"]]
        require(
            any(
                isinstance(row, dict)
                and row.get("status") == "routed_not_rejected_no_lifecycle_profile"
                for row in payloads
            ),
            f"{scenario_id}_B_routed_not_rejected",
            checks,
        )
        require(
            any("U_B" in canonical(row).decode("ascii") for row in payloads),
            f"{scenario_id}_B_reopening_writer",
            checks,
        )

    d_row = scenarios["F6"]["trace"]["rows"][0]
    require(
        d_row["payload"]["candidate_status"]
        == "rejected_on_ontology_uninstantiated_admission_slot",
        "F6_uninstantiated_slot",
        checks,
    )
    require(
        "D0_successor" in d_row["payload"]["reopening_rule"],
        "F6_reopening_boundary",
        checks,
    )

    for scenario_id in ("F7", "E4"):
        rows = scenarios[scenario_id]["trace"]["rows"]
        require(
            sum(row["classification"] == "resolved_negative" for row in rows) == 6,
            f"{scenario_id}_negative_claim_count",
            checks,
        )
        require(
            sum(row["classification"] == "conditioned" for row in rows) == 8,
            f"{scenario_id}_hardening_count",
            checks,
        )

    f8 = scenarios["F8A"]["trace"]["rows"][0]["payload"]
    require(
        f8["support_disposition"] == "indeterminate_requires_review",
        "F8_no_inferred_support_logic",
        checks,
    )
    require(
        "normative_object:CORE-C-AUTHORITY"
        in scenarios["F8B"]["trace"]["rows"][0]["payload"]["object"]["node_id"],
        "F8_object_identity",
        checks,
    )
    require(
        gate["authority"]["counterfactual_runtime_implemented"] is False
        and gate["authority"]["browser_application_implemented"] is False,
        "I4_I6_surfaces_closed",
        checks,
    )
    require(
        gate["status"] == "accepted"
        and gate["authority"]["iteration_4_authorized"] is True
        and gate["acceptance_requirements"]["human_review"] == "accepted",
        "human_acceptance_and_I4_authorization",
        checks,
    )
    residuals = gate["accepted_residual_boundaries"]
    require(len(residuals) == 3, "accepted_residual_population", checks)
    require(
        {row["boundary_id"] for row in residuals}
        == {
            "ET-C3-RESIDUAL-TEST-MATRIX-SCOPE",
            "ET-C3-RESIDUAL-CHAINED-TRUST",
            "ET-C3-RESIDUAL-CANDIDATE-A-PROJECTION",
        },
        "accepted_residual_identity",
        checks,
    )
    require(
        gate["accepted_residual_boundaries"]
        == report["accepted_residual_boundaries"],
        "accepted_residual_cross_surface_identity",
        checks,
    )
    require(
        all(math.isfinite(float(value)) for value in (emitted_rows, emitted_edges)),
        "finite_audit_counts",
        checks,
    )
    print(
        "ET_C3_AUDIT_PASS "
        f"checks={len(checks)} rows={emitted_rows} edge_refs={emitted_edges}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
