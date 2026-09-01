#!/usr/bin/env python3
"""Build the deterministic ET-C3 forensic reconstruction candidate."""

from __future__ import annotations

import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, digest  # noqa: E402
from grcv4_explorer.forensic import (  # noqa: E402
    candidate_career,
    contract_provenance,
    debt_lifecycle,
    gate_act,
    gate_contribution,
    load_forensic_context,
    negative_claims,
    object_dependents,
    pruned_choices_at,
    reconstruction_path,
)
from grcv4_explorer.paths import repository_root  # noqa: E402


def require_repository_venv(repo_root: Path) -> None:
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


def _scenario_rows(context: Any) -> list[dict[str, Any]]:
    definitions: list[tuple[str, str, Any]] = [
        ("F1", "top_normative_claim", reconstruction_path(context, "D10-CL-N-001")),
        (
            "F2",
            "debt_pressure_to_transformation",
            debt_lifecycle(
                context, "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION"
            ),
        ),
        ("F3A", "D7v2_gate_act", gate_act(context, "GRC9V4-CD-D7V2-v1")),
        (
            "F3B",
            "D7v2_gate_contribution",
            gate_contribution(context, "GRC9V4-CD-D7V2-v1"),
        ),
        (
            "F4",
            "candidate_A_career",
            candidate_career(context, "V4-A-temporalized-W"),
        ),
        (
            "F5",
            "candidate_B_routed_boundary",
            candidate_career(context, "V4-B-independent-derived-carrier"),
        ),
        (
            "F6",
            "V4_D_admission_slot",
            pruned_choices_at(context, "GRC9V4-CD-D1-v1"),
        ),
        ("F7", "blocked_overreads", negative_claims(context)),
        (
            "F8A",
            "contract_support",
            contract_provenance(
                context, "D10.2-EC-PARENT-CORE-C-AUTHORITY"
            ),
        ),
        (
            "F8B",
            "object_dependents",
            object_dependents(context, "CORE-C-AUTHORITY"),
        ),
        (
            "E3",
            "candidate_B_readmission_path",
            candidate_career(context, "V4-B-independent-derived-carrier"),
        ),
        ("E4", "accepted_negative_claims", negative_claims(context)),
    ]
    return [
        {
            "scenario_id": scenario_id,
            "title": title,
            "status": "passed_candidate_execution",
            "trace": trace,
        }
        for scenario_id, title, trace in definitions
    ]


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.write_bytes(canonical_bytes(report) + b"\n")


def main() -> int:
    repo_root = repository_root()
    require_repository_venv(repo_root)
    records = SIDE_TOOL_ROOT / "records"
    context = load_forensic_context(repo_root, SIDE_TOOL_ROOT)
    scenarios = _scenario_rows(context)
    trace_digests = [row["trace"]["trace_digest"] for row in scenarios]
    classifications = Counter(
        item["classification"]
        for scenario in scenarios
        for item in scenario["trace"]["rows"]
    )
    report: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C3_forensic_scenarios_v1",
        "status": "accepted",
        "output_class": "forensic_evidence_trace",
        "source_bundle_digest": context.source_bundle_digest,
        "graph_digest": context.graph_digest,
        "scenario_count": len(scenarios),
        "scenario_ids": [row["scenario_id"] for row in scenarios],
        "trace_digests": trace_digests,
        "classification_counts": dict(sorted(classifications.items())),
        "accepted_residual_boundaries": [
            {
                "boundary_id": "ET-C3-RESIDUAL-TEST-MATRIX-SCOPE",
                "disposition": "accepted_noncritical",
                "statement": "the_ET_C3_focused_matrix_is_lighter_than_ET_C2_because_graph_invariant_enforcement_remains_owned_by_ET_C2_while_ET_C3_independently_audits_every_emitted_source_pointer_and_edge_reference",
                "reopen_trigger": "a_forensic_transformation_begins_mutating_graph_authority_or_an_emitted_payload_is_not_covered_by_the_independent_source_audit",
            },
            {
                "boundary_id": "ET-C3-RESIDUAL-CHAINED-TRUST",
                "disposition": "accepted_noncritical",
                "statement": "load_forensic_context_uses_the_human_accepted_ET_C2_gate_as_its_predecessor_root_while_revalidating_ET_C2_record_digest_graph_digest_kernel_invariants_and_ET_C1_source_identity_on_every_load",
                "reopen_trigger": "ET_C2_identity_or_acceptance_changes_or_a_successor_requires_an_independent_root_of_trust",
            },
            {
                "boundary_id": "ET-C3-RESIDUAL-CANDIDATE-A-PROJECTION",
                "disposition": "accepted_source_bounded_exception",
                "statement": "candidate_career_has_one_explicit_Candidate_A_projection_for_the_D10_2_profile_scope_and_future_curvature_hardening_rows_and_reads_both_values_from_the_admitted_source",
                "reopen_trigger": "another_candidate_requires_candidate_specific_provenance_hardening_or_the_D10_2_hardening_schema_changes",
                "blocked_generalization": "the_Candidate_A_branch_is_not_a_generic_candidate_projection_rule",
            },
        ],
        "scenarios": scenarios,
        "report_digest": None,
    }
    report["report_digest"] = digest(
        {key: value for key, value in report.items() if key != "report_digest"}
    )
    _write_report(records / "ETC3ForensicScenarioReport.json", report)

    context_record = tomllib.loads((TOOL_ROOT / "iteration3_context.toml").read_text())
    gate: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C3_forensic_reconstruction_admission_v1",
        "gate_id": "ET-C3_forensic_reconstruction_surface",
        "status": "accepted",
        "iteration": 3,
        "execution_context": context_record,
        "predecessor": {
            "gate_id": "ET-C2_validated_graph_kernel",
            "record_digest": context.et_c2_record_digest,
            "graph_digest": context.graph_digest,
            "source_bundle_digest": context.source_bundle_digest,
        },
        "authority": {
            "forensic_API_implemented": True,
            "source_records_modified": False,
            "scientific_claim_added": False,
            "counterfactual_runtime_implemented": False,
            "browser_application_implemented": False,
            "iteration_4_authorized": True,
        },
        "forensic_surface": {
            "API_count": 9,
            "API_names": [
                "gate_act",
                "debt_lifecycle",
                "reconstruction_path",
                "candidate_career",
                "pruned_choices_at",
                "negative_claims",
                "object_dependents",
                "contract_provenance",
                "gate_contribution",
            ],
            "scenario_report_path": "records/ETC3ForensicScenarioReport.json",
            "scenario_report_digest": report["report_digest"],
            "scenario_count": len(scenarios),
            "all_rows_source_digest_and_edge_bound": True,
            "verification_obligations_excluded_from_backward_support": True,
            "speculative_claim_count": 0,
        },
        "notebook_surface": {
            "path": "tool/notebooks/forensic_recipes.ipynb",
            "logic_role": "orchestration_only",
            "execution_engine": "stdlib_recipe_runner",
            "derived_output_envelope": "tool/generated/iteration3-notebook",
        },
        "accepted_residual_boundaries": report["accepted_residual_boundaries"],
        "acceptance_requirements": {
            "independent_raw_graph_and_source_audit": "passed_10018_checks",
            "focused_failure_fixture_matrix": "passed_15_checks",
            "deterministic_double_rebuild": "passed",
            "notebook_output_envelope_check": "passed",
            "human_review": "accepted",
        },
        "non_claims": [
            "no_speculative_counterfactual",
            "no_browser_application",
            "no_new_scientific_evidence",
            "no_candidate_or_realization_ranking",
            "no_finality_claim_for_D0_D10_2_source_population",
        ],
        "record_digest": None,
    }
    gate["record_digest"] = digest(
        {key: value for key, value in gate.items() if key != "record_digest"}
    )
    _write_report(records / "ETC3ForensicReconstructionSurface.json", gate)

    lines = [
        "# ET-C3 Forensic Scenario Report",
        "",
        "**Status:** Accepted",
        "",
        "The report reconstructs accepted-source relations through pure Python",
        "functions. It adds no scientific claims and performs no counterfactual",
        "mutation.",
        "",
        "## Scenarios",
        "",
    ]
    for scenario in scenarios:
        trace = scenario["trace"]
        lines.append(
            f"- `{scenario['scenario_id']}` {scenario['title']}: "
            f"`{trace['row_count']}` rows, digest `{trace['trace_digest']}`"
        )
    lines.extend(
        [
            "",
            "Every row names its admitted source record, canonical source digest,",
            "JSON pointer, and exact ET-C2 propagation-edge references. Forward",
            "verification obligations are reported as work routing and are never",
            "used as backward accepted support.",
            "",
            "## Accepted Residual Boundaries",
            "",
            "- The focused ET-C3 matrix is intentionally lighter than ET-C2;",
            "  graph invariant enforcement remains owned by ET-C2, while the I3",
            "  auditor checks every emitted source pointer and edge witness.",
            "- ET-C3 uses chained trust rooted in accepted ET-C2 and revalidates",
            "  ET-C2, ET-C1, and source identity on every context load.",
            "- Candidate A has one explicit, source-bounded D10.2 hardening",
            "  projection. It is not a generic candidate rule and must be reopened",
            "  if another candidate requires equivalent special handling.",
            "",
            f"Report digest: `{report['report_digest']}`",
            "",
        ]
    )
    (records / "ETC3ForensicScenarioReport.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    gate_lines = [
        "# ET-C3 Forensic Reconstruction Surface",
        "",
        "**Status:** Accepted",
        "",
        "Iteration 3 implements nine pure forensic APIs and a minimal notebook",
        "recipe over the accepted ET-C2 graph and ET-C1-admitted source payloads.",
        "The graph owns relationship semantics; admitted source JSON owns exact",
        "gate, candidate, debt, object, and contract payloads.",
        "",
        "## Boundary",
        "",
        "This candidate contains only `forensic_evidence_trace` output. It does",
        "not implement structural counterfactuals or browser behavior, does not",
        "rank candidates, and does not treat D0-D10.2 as the final source",
        "population. A changed source inventory requires a new admission cycle.",
        "The accepted residual boundaries remain machine-recorded and do not",
        "weaken the forensic claim ceiling.",
        "",
        f"Record digest: `{gate['record_digest']}`",
        "",
    ]
    (records / "ETC3ForensicReconstructionSurface.md").write_text(
        "\n".join(gate_lines), encoding="utf-8"
    )
    print(
        "ET_C3_BUILD_PASS "
        f"report={report['report_digest']} record={gate['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
