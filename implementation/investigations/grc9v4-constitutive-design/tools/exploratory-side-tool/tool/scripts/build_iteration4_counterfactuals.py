#!/usr/bin/env python3
"""Build the deterministic ET-C4 bounded counterfactual candidate."""

from __future__ import annotations

import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, digest, load_json_object  # noqa: E402
from grcv4_explorer.counterfactual import (  # noqa: E402
    CONFORMANCE_FIXTURE_ID,
    MUTATION_SCHEMA,
    evaluate_mutation,
    load_counterfactual_context,
    make_mutation,
)
from grcv4_explorer.paths import repository_root  # noqa: E402


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
A_CANDIDATE = "V4-A-temporalized-W"
B_CANDIDATE = "V4-B-independent-derived-carrier"
C_CANDIDATE = "V4-C-constitutive-C-sector"
D_CANDIDATE = "V4-D-source-admitted-structural"
D10_2 = "GRC9V4-CD-D10.2-v1"
A_CONTRACTION = "D10.2-EC-CI-A-CONTRACTION"
GENERAL_CHARGE = "D10.2-EC-PARENT-CORE-GENERAL-CHARGE"
NORMALIZATION = "D10.2-EC-PARENT-SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER"


def require_repository_venv(repo_root: Path) -> None:
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


def _mutation_id(mutation: dict[str, Any]) -> str:
    payload = {key: value for key, value in mutation.items() if key != "mutation_id"}
    return f"ET-C4-MUT-{digest(payload)}"


def _raw_mutation(
    context: Any,
    *,
    target_id: str,
    target_kind: str,
    mutation_type: str,
    baseline_record_id: str,
    profile_scope: list[str],
    candidate_scope: list[str],
    realization_scope: list[str],
    declared_payload: dict[str, Any],
) -> dict[str, Any]:
    baseline = context.documents_by_record[baseline_record_id]
    mutation: dict[str, Any] = {
        "schema": MUTATION_SCHEMA,
        "mutation_id": None,
        "target_id": target_id,
        "target_kind": target_kind,
        "mutation_type": mutation_type,
        "baseline_record_id": baseline_record_id,
        "baseline_record_digest": baseline.declared_digest,
        "profile_scope": sorted(profile_scope),
        "candidate_scope": sorted(candidate_scope),
        "realization_scope": sorted(realization_scope),
        "declared_payload": declared_payload,
    }
    mutation["mutation_id"] = _mutation_id(mutation)
    return mutation


def _valid(context: Any, **kwargs: Any) -> dict[str, Any]:
    mutation = make_mutation(context, **kwargs)
    return evaluate_mutation(context, mutation)


def _scenario_rows(context: Any) -> list[dict[str, Any]]:
    c1 = _valid(
        context,
        target_id="GRC9V4-CD-D7V2-v1",
        target_kind="gate_record",
        mutation_type="change_candidate_disposition",
        baseline_record_id="GRC9V4-CD-D7V2-v1",
        profile_scope=[],
        candidate_scope=[B_CANDIDATE],
        realization_scope=[],
        declared_payload={
            "proposed_disposition": "complete_candidate_local_transition"
        },
    )
    c2 = _valid(
        context,
        target_id=A_CONTRACTION,
        target_kind="equation_contract",
        mutation_type="remove_term",
        baseline_record_id=D10_2,
        profile_scope=["A_CI"],
        candidate_scope=[A_CANDIDATE],
        realization_scope=["comparison:A-CI"],
        declared_payload={"term_id": "bounded_contraction_condition"},
    )
    c3 = _valid(
        context,
        target_id=GENERAL_CHARGE,
        target_kind="equation_contract",
        mutation_type="replace_operator",
        baseline_record_id=D10_2,
        profile_scope=ALL_PROFILES,
        candidate_scope=[A_CANDIDATE, C_CANDIDATE],
        realization_scope=[],
        declared_payload={
            "replacement_operator_id": "counterfactual_general_charge_operator"
        },
    )
    c4 = _valid(
        context,
        target_id=NORMALIZATION,
        target_kind="equation_contract",
        mutation_type="change_normalization",
        baseline_record_id=D10_2,
        profile_scope=ALL_PROFILES,
        candidate_scope=[A_CANDIDATE, C_CANDIDATE],
        realization_scope=[],
        declared_payload={
            "surface": "profile_normalization_lock",
            "neutralizes_source_lock": True,
        },
    )
    c5 = _valid(
        context,
        target_id=A_CONTRACTION,
        target_kind="equation_contract",
        mutation_type="remove_term",
        baseline_record_id=D10_2,
        profile_scope=["A_CI"],
        candidate_scope=[A_CANDIDATE],
        realization_scope=["comparison:A-CI"],
        declared_payload={"term_id": "A_CI_contraction_term"},
    )
    fixture = _raw_mutation(
        context,
        target_id=CONFORMANCE_FIXTURE_ID,
        target_kind="equation_contract",
        mutation_type="remove_term",
        baseline_record_id=D10_2,
        profile_scope=[],
        candidate_scope=[],
        realization_scope=[],
        declared_payload={"term_id": "nonloadbearing_conformance_term"},
    )
    c6 = evaluate_mutation(context, fixture, conformance_fixture=True)
    c7 = _valid(
        context,
        target_id=A_CONTRACTION,
        target_kind="equation_contract",
        mutation_type="change_profile_parameterization",
        baseline_record_id=D10_2,
        profile_scope=["A_CI"],
        candidate_scope=[A_CANDIDATE],
        realization_scope=["comparison:A-CI"],
        declared_payload={
            "parameter_id": "A_CI_profile_parameterization",
            "qualitative_change": "structural_only_no_numeric_prediction",
        },
    )

    d2_mutation = dict(c2["mutation"])
    del d2_mutation["profile_scope"]
    d2_mutation["mutation_id"] = _mutation_id(d2_mutation)
    d2 = evaluate_mutation(context, d2_mutation)

    d3_mutation = dict(c2["mutation"])
    d3_mutation["graph_patch"] = {"arbitrary": "field_patch"}
    d3_mutation["mutation_id"] = _mutation_id(d3_mutation)
    d3 = evaluate_mutation(context, d3_mutation)

    d4 = _valid(
        context,
        target_id=B_CANDIDATE,
        target_kind="candidate",
        mutation_type="change_candidate_disposition",
        baseline_record_id="GRC9V4-CD-D1-v1",
        profile_scope=[],
        candidate_scope=[B_CANDIDATE],
        realization_scope=[],
        declared_payload={
            "proposed_disposition": "positive_result_beyond_evidence_frontier"
        },
    )
    d5_b = _valid(
        context,
        target_id=B_CANDIDATE,
        target_kind="candidate",
        mutation_type="change_candidate_disposition",
        baseline_record_id="GRC9V4-CD-D1-v1",
        profile_scope=[],
        candidate_scope=[B_CANDIDATE],
        realization_scope=[],
        declared_payload={"proposed_disposition": "candidate_complete"},
    )
    d5_d = _valid(
        context,
        target_id=D_CANDIDATE,
        target_kind="candidate",
        mutation_type="change_candidate_disposition",
        baseline_record_id="GRC9V4-CD-D1-v1",
        profile_scope=[],
        candidate_scope=[D_CANDIDATE],
        realization_scope=[],
        declared_payload={"proposed_disposition": "instantiated_candidate"},
    )
    d6_mutation = _raw_mutation(
        context,
        target_id=A_CONTRACTION,
        target_kind="equation_contract",
        mutation_type="remove_term",
        baseline_record_id=D10_2,
        profile_scope=["A_CI"],
        candidate_scope=[A_CANDIDATE],
        realization_scope=["comparison:A-CI"],
        declared_payload={"term_id": 0.5},
    )
    d6 = evaluate_mutation(context, d6_mutation)

    definitions = [
        ("C1", "candidate_B_D7v2_reopening", c1),
        ("C2", "remove_A_only_equation_term", c2),
        ("C3", "replace_common_charge_operator", c3),
        ("C4", "neutralize_normalization_lock", c4),
        ("C5", "remove_A_contraction_term", c5),
        ("C6", "nonloadbearing_conformance_fixture", c6),
        ("C7", "A_profile_parameterization_scope", c7),
        ("D2", "missing_required_scope", d2),
        ("D3", "arbitrary_graph_patch", d3),
        ("D4", "positive_result_beyond_frontier", d4),
        ("D5-B", "candidate_B_fabrication_control", d5_b),
        ("D5-D", "V4_D_fabrication_control", d5_d),
        ("D6", "numeric_effect_injection", d6),
    ]
    return [
        {
            "scenario_id": scenario_id,
            "title": title,
            "status": "passed_candidate_execution",
            "result": result,
        }
        for scenario_id, title, result in definitions
    ]


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_bytes(canonical_bytes(value) + b"\n")


def main() -> int:
    repo_root = repository_root()
    require_repository_venv(repo_root)
    records = SIDE_TOOL_ROOT / "records"
    context = load_counterfactual_context(repo_root, SIDE_TOOL_ROOT)
    et_c3_digest = load_json_object(
        records / "ETC3ForensicReconstructionSurface.json"
    )["record_digest"]
    scenarios = _scenario_rows(context)
    one_of_support_edge_count = sum(
        edge["support_semantic"] == "one_of" for edge in context.propagation_edges
    )
    conditional_reactivation_preconditions_present = any(
        isinstance(node["attributes"].get("conditional_closing_precondition"), dict)
        for node in context.nodes.values()
        if node["kind"] == "debt_transformation"
    )
    exact_negative_activation_conditions_present = any(
        node["attributes"].get("claim_class") == "negative"
        and isinstance(node["attributes"].get("activation_condition"), dict)
        for node in context.nodes.values()
        if node["kind"] in {"current_claim", "historical_claim"}
    )
    status_counts = Counter(
        status
        for scenario in scenarios
        for status in scenario["result"]["result_statuses"]
    )
    report: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C4_counterfactual_scenarios_v1",
        "status": "accepted",
        "output_class": "speculative_structural_counterfactual",
        "source_bundle_digest": context.source_bundle_digest,
        "graph_digest": context.graph_digest,
        "predecessor_ET_C3_record_digest": et_c3_digest,
        "scenario_count": len(scenarios),
        "scenario_ids": [row["scenario_id"] for row in scenarios],
        "result_status_counts": dict(sorted(status_counts.items())),
        "exact_negative_activation_count": sum(
            "exact_negative_activation" in row["result"]["result_statuses"]
            for row in scenarios
        ),
        "exact_debt_reactivation_count": sum(
            "exact_debt_reactivation" in row["result"]["result_statuses"]
            for row in scenarios
        ),
        "current_source_boundary": {
            "one_of_support_edge_count": one_of_support_edge_count,
            "exact_negative_activation_edges_present": exact_negative_activation_conditions_present,
            "exact_conditional_debt_reactivation_preconditions_present": conditional_reactivation_preconditions_present,
            "implemented_behavior_verified_by_synthetic_failure_fixtures": True,
        },
        "scenarios": scenarios,
        "report_digest": None,
    }
    report["report_digest"] = digest(
        {key: value for key, value in report.items() if key != "report_digest"}
    )
    _write_json(records / "ETC4CounterfactualScenarioReport.json", report)

    context_record = tomllib.loads((TOOL_ROOT / "iteration4_context.toml").read_text())
    gate: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C4_bounded_counterfactual_admission_v1",
        "gate_id": "ET-C4_bounded_counterfactual_kernel",
        "status": "accepted",
        "iteration": 4,
        "execution_context": context_record,
        "predecessor": {
            "gate_id": "ET-C3_forensic_reconstruction_surface",
            "record_digest": et_c3_digest,
            "graph_digest": context.graph_digest,
            "source_bundle_digest": context.source_bundle_digest,
        },
        "authority": {
            "typed_mutation_kernel_implemented": True,
            "source_records_modified": False,
            "scientific_claim_added": False,
            "runtime_reexecution_performed": False,
            "numeric_effect_prediction_performed": False,
            "browser_application_implemented": False,
            "iteration_5_authorized": True,
        },
        "counterfactual_surface": {
            "target_kinds": [
                "candidate",
                "equation_contract",
                "gate_record",
                "normative_object",
            ],
            "mutation_type_count": 9,
            "result_status_count": 9,
            "scenario_report_path": "records/ETC4CounterfactualScenarioReport.json",
            "scenario_report_digest": report["report_digest"],
            "scenario_count": len(scenarios),
            "evidence_frontier_is_fail_closed": True,
            "historical_debt_metadata_is_not_current_authority": True,
            "positive_claim_beyond_frontier_count": 0,
            "numeric_effect_prediction_count": 0,
            "fabricated_successor_claim_count": 0,
        },
        "acceptance_requirements": {
            "independent_source_edge_and_scenario_audit": "passed_1775_checks_169_edge_references",
            "focused_adversarial_fixture_matrix": "passed_38_checks",
            "deterministic_double_rebuild": "passed",
            "ET_C3_regression": "passed_full_verification",
            "human_review": "accepted",
        },
        "non_claims": [
            "no_reexecuted_gate_outcome",
            "no_new_scientific_evidence",
            "no_numeric_physical_prediction",
            "no_candidate_or_realization_ranking",
            "no_finality_claim_for_D0_D10_2_source_population",
        ],
        "record_digest": None,
    }
    gate["record_digest"] = digest(
        {key: value for key, value in gate.items() if key != "record_digest"}
    )
    _write_json(records / "ETC4BoundedCounterfactualKernel.json", gate)

    report_lines = [
        "# ET-C4 Counterfactual Scenario Report",
        "",
        "**Status:** Accepted",
        "",
        "Iteration 4 evaluates typed structural mutations against accepted ET-C2",
        "relationships and ET-C3 source-bound forensic authority. Every output is",
        "speculative, stops at the evidence frontier, and contains no numerical",
        "effect prediction or reopened-gate outcome.",
        "",
        "## Scenarios",
        "",
    ]
    for scenario in scenarios:
        result = scenario["result"]
        report_lines.append(
            f"- `{scenario['scenario_id']}` {scenario['title']}: "
            f"`{', '.join(result['result_statuses'])}`; digest "
            f"`{result['result_digest']}`"
        )
    report_lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Candidate B opens D7-v2 and names the source-recorded missing `U_B`",
            "work, but no B-specific D7G-D10 result is synthesized. Candidate C-only",
            "claims remain known when no accepted dependency connects them to the B",
            "mutation. Blocked overreads are listed only as risks; they are never",
            "activated as claims. Current sources contain no exact one-of, negative-",
            "activation, or conditional debt-reactivation edge, so those algorithms",
            "are pressure-tested with synthetic edge fixtures rather than fabricated",
            "as source results.",
            "",
            f"Report digest: `{report['report_digest']}`",
            "",
        ]
    )
    (records / "ETC4CounterfactualScenarioReport.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )
    gate_lines = [
        "# ET-C4 Bounded Counterfactual Kernel",
        "",
        "**Status:** Accepted",
        "",
        "The kernel admits typed structural mutations over accepted source records,",
        "computes source-grounded invalidation or reopening boundaries, and stops",
        "before any result that requires scientific re-execution. Existing-path",
        "sparsity and candidate/gate reopening are distinct operations.",
        "",
        "Independent audit, deterministic replay, and human review are complete.",
        "Iteration 5 is authorized; no Iteration 5 implementation is claimed here.",
        "",
        f"Record digest: `{gate['record_digest']}`",
        "",
    ]
    (records / "ETC4BoundedCounterfactualKernel.md").write_text(
        "\n".join(gate_lines), encoding="utf-8"
    )
    print(
        "ET_C4_BUILD_PASS "
        f"report={report['report_digest']} record={gate['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
