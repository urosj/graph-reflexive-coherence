#!/usr/bin/env python3
"""Independent ET-C4 audit over raw graph, source, and scenario records."""

from __future__ import annotations

import hashlib
import json
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
        raise RuntimeError(f"ET-C4 audit failed: {label}")
    checks.append(label)


def result(scenarios: dict[str, dict[str, Any]], scenario_id: str) -> dict[str, Any]:
    return cast(dict[str, Any], scenarios[scenario_id]["result"])


def main() -> int:
    repo_root = next(
        parent
        for parent in SIDE_TOOL_ROOT.parents
        if (parent / "pyproject.toml").is_file()
    )
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    records = SIDE_TOOL_ROOT / "records"
    report = load(records / "ETC4CounterfactualScenarioReport.json")
    gate = load(records / "ETC4BoundedCounterfactualKernel.json")
    et_c3 = load(records / "ETC3ForensicReconstructionSurface.json")
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
        report["graph_digest"] == graph["graph_digest"],
        "graph_binding",
        checks,
    )
    require(
        report["source_bundle_digest"] == manifest["source_bundle_digest"],
        "source_bundle_binding",
        checks,
    )
    require(
        report["predecessor_ET_C3_record_digest"] == et_c3["record_digest"],
        "ET_C3_binding",
        checks,
    )
    require(
        gate["predecessor"]["record_digest"] == et_c3["record_digest"],
        "gate_ET_C3_binding",
        checks,
    )
    require(
        gate["status"] == "accepted",
        "accepted_status",
        checks,
    )
    require(report["status"] == "accepted", "accepted_report_status", checks)
    require(
        gate["acceptance_requirements"]["human_review"] == "accepted",
        "human_review_accepted",
        checks,
    )
    require(
        gate["authority"]["iteration_5_authorized"] is True,
        "iteration_5_authorized",
        checks,
    )

    sources: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for row in manifest["records"]:
        sources[row["record_identifier"]] = (row, load(repo_root / row["path"]))
    graph_edges = {row["edge_id"]: row for row in graph["propagation_edges"]}
    scenarios = {row["scenario_id"]: row for row in report["scenarios"]}
    expected_ids = {
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "D2",
        "D3",
        "D4",
        "D5-B",
        "D5-D",
        "D6",
    }
    require(set(scenarios) == expected_ids, "scenario_identity", checks)
    require(report["scenario_count"] == len(expected_ids), "scenario_count", checks)

    edge_reference_count = 0
    for scenario_id, scenario in sorted(scenarios.items()):
        current = scenario["result"]
        require(
            current["result_digest"]
            == value_digest(
                {k: v for k, v in current.items() if k != "result_digest"}
            ),
            f"{scenario_id}_result_digest",
            checks,
        )
        mutation = current["mutation"]
        mutation_payload = {
            key: value for key, value in mutation.items() if key != "mutation_id"
        }
        require(
            mutation.get("mutation_id")
            == f"ET-C4-MUT-{value_digest(mutation_payload)}",
            f"{scenario_id}_mutation_digest",
            checks,
        )
        require(
            current["output_class"] == "speculative_structural_counterfactual",
            f"{scenario_id}_speculative_class",
            checks,
        )
        boundary = current["claim_boundary"]
        require(
            set(boundary.values()) == {False},
            f"{scenario_id}_claim_boundary_closed",
            checks,
        )
        structural = current["structural_result"]
        require(
            structural.get(
                "historical_must_close_before_D10_used_as_current_authority",
                False,
            )
            is False,
            f"{scenario_id}_historical_debt_not_authority",
            checks,
        )
        require(
            structural.get("fabricated_successor_claims", []) == [],
            f"{scenario_id}_no_fabricated_successor",
            checks,
        )
        for witness in structural.get("claim_predicate_witnesses", []):
            source_ref = witness["claim_source_ref"]
            source_row, source = sources[source_ref["record_id"]]
            require(
                source_ref["record_digest"] == source_row["canonical_digest"],
                f"{scenario_id}_{witness['claim_id']}_predicate_source_digest",
                checks,
            )
            claim_payload = resolve_pointer(source, source_ref["source_json_pointer"])
            require(
                claim_payload["claim_id"] == witness["claim_id"],
                f"{scenario_id}_{witness['claim_id']}_predicate_source_payload",
                checks,
            )
            require(
                witness["activation_condition"]
                == claim_payload["activation_condition"],
                f"{scenario_id}_{witness['claim_id']}_activation_condition",
                checks,
            )
            require(
                [row["record_id"] for row in witness["evidence_refs"]]
                == claim_payload["evidence_refs"],
                f"{scenario_id}_{witness['claim_id']}_evidence_population",
                checks,
            )
            require(
                [row["debt_id"] for row in witness["debt_transformations"]]
                == claim_payload["bearing_debt_ids"],
                f"{scenario_id}_{witness['claim_id']}_debt_population",
                checks,
            )
        for edge_ref in structural.get("source_edge_refs", []):
            edge_reference_count += 1
            actual = graph_edges.get(edge_ref["edge_id"])
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
            source_row, source = sources[actual["source_record_id"]]
            require(
                edge_ref["source_record_digest"] == source_row["canonical_digest"],
                "edge_source_digest",
                checks,
            )
            resolve_pointer(source, edge_ref["source_json_pointer"])

    c1 = result(scenarios, "C1")
    c1s = c1["structural_result"]
    require(
        set(c1["result_statuses"])
        == {
            "exact_route_change",
            "requires_reexecution_from_gate",
            "unknown_beyond_evidence_frontier",
        },
        "C1_disposition",
        checks,
    )
    require(
        c1s["earliest_gates_to_reopen"] == ["GRC9V4-CD-D7V2-v1"],
        "C1_D7v2_root",
        checks,
    )
    require(
        c1s["routes_changed"] == ["D7V2-DEBT-B-FUTURE-SOURCE-BACKED-WRITER"],
        "C1_exact_route",
        checks,
    )
    require(c1s["debts_reactivated"] == [], "C1_no_false_reactivation", checks)
    require(
        any("U_B" in str(row["payload"]) for row in c1s["source_recorded_missing_work"]),
        "C1_names_U_B",
        checks,
    )
    require(
        "D10-CL-O-002" in c1s["known_through_evidence_frontier"],
        "C1_C_only_claim_preserved",
        checks,
    )
    require(
        bool(c1s["unknown_beyond_evidence_frontier"]),
        "C1_nonempty_frontier",
        checks,
    )

    for scenario_id in ("C2", "C5"):
        current = result(scenarios, scenario_id)
        require(
            "exact_invalidation" not in current["result_statuses"],
            f"{scenario_id}_no_false_exact_invalidation",
            checks,
        )
        require(
            "indeterminate_requires_review" in current["result_statuses"],
            f"{scenario_id}_incomplete_semantics_fail_closed",
            checks,
        )
    require(
        "requires_reexecution_from_gate" in result(scenarios, "C5")["result_statuses"],
        "C5_reexecution_required",
        checks,
    )

    c3s = result(scenarios, "C3")["structural_result"]
    require(
        c3s["verification_obligations_at_risk"]
        == ["D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT"],
        "C3_obligation_separate",
        checks,
    )
    require(
        "D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT"
        not in c3s["claims_requiring_reexecution"],
        "C3_obligation_not_claim",
        checks,
    )

    c4s = result(scenarios, "C4")["structural_result"]
    require(
        [row["blocked_overread"] for row in c4s["blocked_overreads_at_risk"]]
        == ["profile_constants_are_not_hidden_universal_constants"],
        "C4_overread_risk",
        checks,
    )
    require(c4s["negative_claims_activated"] == [], "C4_no_overread_activation", checks)
    require(
        "exact_negative_activation" not in result(scenarios, "C4")["result_statuses"],
        "C4_no_false_negative_activation",
        checks,
    )

    c6 = result(scenarios, "C6")
    require(
        c6["result_statuses"] == ["no_propagation_bearing_effect"],
        "C6_no_effect",
        checks,
    )
    require(
        c6["structural_result"]["fixture_authority"]
        == "investigation_local_conformance_only",
        "C6_fixture_authority",
        checks,
    )

    for scenario_id in ("C2", "C7"):
        structural = result(scenarios, scenario_id)["structural_result"]
        require(structural["profiles_affected"] == ["A_CI"], f"{scenario_id}_A_scope", checks)
        require(
            not any(profile.startswith("C_") for profile in structural["profiles_affected"]),
            f"{scenario_id}_no_C_profile_leak",
            checks,
        )

    invalid_reasons = {
        "D2": "mutation_fields_mismatch:['profile_scope']:[]",
        "D3": "mutation_fields_mismatch:[]:['graph_patch']",
        "D6": "numeric_effect_injection_forbidden",
    }
    for scenario_id, reason in invalid_reasons.items():
        current = result(scenarios, scenario_id)
        require(current["result_statuses"] == ["invalid_mutation"], f"{scenario_id}_invalid", checks)
        require(current["structural_result"]["invalid_reason"] == reason, f"{scenario_id}_reason", checks)

    d4 = result(scenarios, "D4")
    require(
        d4["claim_boundary"]["positive_claim_beyond_frontier"] is False,
        "D4_positive_outcome_blocked",
        checks,
    )
    require(
        "unknown_beyond_evidence_frontier" in d4["result_statuses"],
        "D4_unknown_not_predicted",
        checks,
    )

    d5_b = result(scenarios, "D5-B")["structural_result"]
    require(d5_b["fabricated_successor_claims"] == [], "D5_B_no_fabrication", checks)
    d5_d = result(scenarios, "D5-D")["structural_result"]
    require(
        d5_d["earliest_gates_to_reopen"] == ["GRC9V4-CD-D0-v1"],
        "D5_D_reopens_D0",
        checks,
    )
    require(
        any("D0_successor" in str(row["payload"]) for row in d5_d["source_recorded_missing_work"]),
        "D5_D_preserves_uninstantiated_slot",
        checks,
    )

    boundary = report["current_source_boundary"]
    require(boundary["one_of_support_edge_count"] == 0, "source_has_no_one_of", checks)
    require(report["exact_negative_activation_count"] == 0, "no_fabricated_negative", checks)
    require(report["exact_debt_reactivation_count"] == 0, "no_fabricated_reactivation", checks)
    require(edge_reference_count > 0, "source_edges_audited", checks)
    print(
        "ET_C4_AUDIT_PASS "
        f"checks={len(checks)} edge_references={edge_reference_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
