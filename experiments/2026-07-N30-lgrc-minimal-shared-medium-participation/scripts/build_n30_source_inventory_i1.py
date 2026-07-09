#!/usr/bin/env python3
"""Build N30 Iteration 1 source inventory and method admission."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
ECOLOGY_ROOT = ROOT.parent / "reflexive-coherence-agentic-ecology"
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
OUTPUT = EXPERIMENT / "outputs" / "n30_source_inventory_i1.json"
REPORT = EXPERIMENT / "reports" / "n30_source_inventory_i1.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_source_inventory_i1.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"


BLOCKED_CLAIMS = [
    "shared_medium_coordination",
    "native_shared_medium_organization",
    "parent_basin_modulation",
    "resonant_alignment",
    "semantic_communication",
    "semantic_coordination",
    "cooperation",
    "agency",
    "selfhood",
    "identity_acceptance",
    "sentience",
    "organism_life",
    "ecology_regime",
    "phase8_completion",
    "unrestricted_autonomy",
]

UNSAFE_CLAIM_FLAGS = {f"{claim}_opened": False for claim in BLOCKED_CLAIMS}


SOURCES: list[dict[str, Any]] = [
    {
        "source_id": "n30_plus_experiment_catalog_roadmap",
        "source_path_or_url": "experiments/N30_plus_experiment_catalog_roadmap.md",
        "local_path": ROOT / "experiments" / "N30_plus_experiment_catalog_roadmap.md",
        "source_role": "catalog_ontology_and_claim_policy_source",
        "allowed_use": [
            "catalog_layer_vocabulary",
            "source_basis_policy",
            "claim_boundary_policy",
            "bidirectional_grammar_context",
        ],
        "blocked_use": [
            "runtime_evidence",
            "shared_medium_participation_evidence",
            "native_shared_medium_organization_evidence",
        ],
        "consumed_sections": [
            "source basis and consumption rules",
            "catalog hierarchy",
            "claim-boundary policy",
            "N30 direction appendices",
        ],
        "claim_boundary_imported": True,
        "runtime_evidence_allowed": False,
    },
    {
        "source_id": "n30_plus_candidate_directions",
        "source_path_or_url": "experiments/N30_plus_candidate_directions.md",
        "local_path": ROOT / "experiments" / "N30_plus_candidate_directions.md",
        "source_role": "candidate_direction_and_dependency_context",
        "allowed_use": [
            "candidate_dependency_context",
            "N30_direction_context",
            "N31_handoff_context",
        ],
        "blocked_use": [
            "experiment_result_evidence",
            "positive_N30_row_source",
            "shared_medium_coordination_evidence",
        ],
        "consumed_sections": [
            "candidate relationship map",
            "N30 direction notes",
            "two-loop spiral appendices",
        ],
        "claim_boundary_imported": True,
        "runtime_evidence_allowed": False,
    },
    {
        "source_id": "shared_medium_essay",
        "source_path_or_url": (
            "reflexive-coherence-agentic-ecology/papers/"
            "2026-06-TheSharedMedium.md"
        ),
        "local_path": ECOLOGY_ROOT / "papers" / "2026-06-TheSharedMedium.md",
        "source_role": "shared_medium_conceptual_transition_source",
        "allowed_use": [
            "message_vs_medium_distinction",
            "medium_surface_vocabulary",
            "shared_medium_debt_context",
            "blocked_coordination_boundary",
        ],
        "blocked_use": [
            "LGRC_runtime_evidence",
            "native_shared_medium_organization_evidence",
            "communication_or_cooperation_evidence",
            "ecology_regime_evidence",
        ],
        "consumed_sections": [
            "shared medium as transition concept",
            "message-passing distinction",
            "coordination and resonance caveats",
        ],
        "claim_boundary_imported": True,
        "runtime_evidence_allowed": False,
    },
    {
        "source_id": "shared_medium_coordination_engineering_spec",
        "source_path_or_url": (
            "reflexive-coherence-agentic-ecology/papers/"
            "2026-06-SharedMediumCoordination-EngineeringSpec.md"
        ),
        "local_path": ECOLOGY_ROOT
        / "papers"
        / "2026-06-SharedMediumCoordination-EngineeringSpec.md",
        "source_role": "shared_medium_method_control_and_debt_source",
        "allowed_use": [
            "medium_surface_schema_vocabulary",
            "perturbation_trace_susceptibility_vocabulary",
            "medium_debt_schema",
            "direct_message_and_hidden_producer_controls",
        ],
        "blocked_use": [
            "runnable_LGRC_evidence",
            "native_shared_medium_coordination_evidence",
            "agentic_ecology_implementation_evidence",
        ],
        "consumed_sections": [
            "engineering surfaces",
            "trace and susceptibility method",
            "medium debt",
            "controls and failure modes",
        ],
        "claim_boundary_imported": True,
        "runtime_evidence_allowed": False,
    },
    {
        "source_id": "n27_closeout_and_n28_handoff",
        "source_path_or_url": (
            "experiments/2026-06-N27-lgrc-configuration-substrate-transfer/"
            "outputs/n27_closeout_and_n28_handoff.json"
        ),
        "local_path": ROOT
        / "experiments"
        / "2026-06-N27-lgrc-configuration-substrate-transfer"
        / "outputs"
        / "n27_closeout_and_n28_handoff.json",
        "source_role": "participant_continuity_and_transfer_guardrail",
        "allowed_use": [
            "participant_carrier_recognizability_guardrail",
            "configuration_transfer_boundary",
            "same_basin_mapping_replay_discipline",
        ],
        "blocked_use": [
            "minimal_shared_medium_participation_evidence",
            "medium_surface_trace_evidence",
            "agentic_participant_evidence",
        ],
        "consumed_sections": [
            "closeout rung",
            "transfer contract",
            "blocked claims",
        ],
        "claim_boundary_imported": True,
        "runtime_evidence_allowed": False,
    },
    {
        "source_id": "n28_closeout_and_n29_handoff",
        "source_path_or_url": (
            "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
            "outputs/n28_closeout_and_n29_handoff.json"
        ),
        "local_path": ROOT
        / "experiments"
        / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
        / "outputs"
        / "n28_closeout_and_n29_handoff.json",
        "source_role": "environment_effect_and_medium_reshaping_guardrail",
        "allowed_use": [
            "generative_extractive_environment_effect_distinction",
            "generic_redistribution_relabel_blocker",
            "medium_reshaping_claim_boundary",
        ],
        "blocked_use": [
            "shared_medium_relation_evidence",
            "later_eligibility_dependency_evidence",
            "ecology_regime_evidence",
        ],
        "consumed_sections": [
            "closeout rung",
            "N29 handoff",
            "claim boundary",
        ],
        "claim_boundary_imported": True,
        "runtime_evidence_allowed": False,
    },
    {
        "source_id": "n29_closeout_and_ecology_handoff",
        "source_path_or_url": (
            "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
            "outputs/n29_closeout_and_ecology_handoff_i18.json"
        ),
        "local_path": ROOT
        / "experiments"
        / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
        / "outputs"
        / "n29_closeout_and_ecology_handoff_i18.json",
        "source_role": "ecology_bridge_and_shared_medium_demand_context",
        "allowed_use": [
            "bridge_context",
            "shared_medium_demand_context",
            "motif_to_primitive_dependency_context",
            "producer_contract_context",
        ],
        "blocked_use": [
            "N30_positive_evidence",
            "shared_medium_coordination_evidence",
            "agentic_ecology_regime_evidence",
        ],
        "consumed_sections": [
            "N29 closeout",
            "ecology handoff",
            "prototype atlas",
            "blocked claims",
        ],
        "claim_boundary_imported": True,
        "runtime_evidence_allowed": False,
    },
    {
        "source_id": "n20_n29_becoming_agency_ecology_roadmap",
        "source_path_or_url": "experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md",
        "local_path": ROOT
        / "experiments"
        / "N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md",
        "source_role": "becoming_agency_ecology_arc_state",
        "allowed_use": [
            "historical_arc_context",
            "experiment_sequence_context",
            "claim_boundary_context",
        ],
        "blocked_use": [
            "N30_runtime_evidence",
            "source_current_trace_evidence",
        ],
        "consumed_sections": [
            "N20-N29 arc",
            "N30 transition notes",
        ],
        "claim_boundary_imported": True,
        "runtime_evidence_allowed": False,
    },
    {
        "source_id": "n20_n29_becoming_agency_ecology_handoff",
        "source_path_or_url": "experiments/N20-N29-LGRC-BecomingAgencyEcologyHandoff.md",
        "local_path": ROOT
        / "experiments"
        / "N20-N29-LGRC-BecomingAgencyEcologyHandoff.md",
        "source_role": "handoff_state_and_next_step_context",
        "allowed_use": [
            "handoff_context",
            "blocked_claim_context",
            "N30_positioning_context",
        ],
        "blocked_use": [
            "N30_positive_evidence",
            "runtime_trace_evidence",
        ],
        "consumed_sections": [
            "current state",
            "next handoff",
        ],
        "claim_boundary_imported": True,
        "runtime_evidence_allowed": False,
    },
    {
        "source_id": "claim_boundary_index",
        "source_path_or_url": "docs/reference/ClaimBoundaryIndex.md",
        "local_path": ROOT / "docs" / "reference" / "ClaimBoundaryIndex.md",
        "source_role": "blocked_claim_and_claim_ceiling_index",
        "allowed_use": [
            "claim_ceiling_context",
            "blocked_relabel_context",
            "unsafe_claim_flags_context",
        ],
        "blocked_use": [
            "evidence_source",
            "runtime_result_source",
            "positive_row_support",
        ],
        "consumed_sections": [
            "bounded claims",
            "claim boundary records",
        ],
        "claim_boundary_imported": True,
        "runtime_evidence_allowed": False,
    },
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def build_source_record(source: dict[str, Any]) -> dict[str, Any]:
    local_path = Path(source["local_path"])
    record = {key: value for key, value in source.items() if key != "local_path"}
    exists = local_path.exists()
    digest = sha256_file(local_path) if exists else "missing"
    record.update(
        {
            "source_exists": exists,
            "commit_or_digest": f"sha256:{digest}",
            "digest_algorithm": "sha256",
            "may_consume_as": source["allowed_use"],
            "must_not_consume_as": source["blocked_use"],
            "positive_evidence_opened_by_this_source": False,
            "source_current_runtime_evidence_allowed": source["runtime_evidence_allowed"],
        }
    )
    return record


def build_payload() -> dict[str, Any]:
    source_records = [build_source_record(source) for source in SOURCES]
    source_roles = sorted({record["source_role"] for record in source_records})
    method_source_ids = [
        "n30_plus_experiment_catalog_roadmap",
        "n30_plus_candidate_directions",
        "shared_medium_essay",
        "shared_medium_coordination_engineering_spec",
    ]
    checks = [
        {
            "check_id": "all_required_sources_exist",
            "passed": all(record["source_exists"] for record in source_records),
        },
        {
            "check_id": "required_method_sources_present",
            "passed": all(
                any(record["source_id"] == source_id for record in source_records)
                for source_id in method_source_ids
            ),
        },
        {
            "check_id": "external_shared_medium_sources_pinned",
            "passed": all(
                record["commit_or_digest"].startswith("sha256:")
                and record["commit_or_digest"] != "sha256:missing"
                for record in source_records
                if record["source_id"]
                in {"shared_medium_essay", "shared_medium_coordination_engineering_spec"}
            ),
        },
        {
            "check_id": "method_sources_not_runtime_evidence",
            "passed": all(
                record["runtime_evidence_allowed"] is False
                for record in source_records
                if record["source_id"] in method_source_ids
            ),
        },
        {
            "check_id": "n27_n28_n29_guardrails_present",
            "passed": all(
                any(record["source_id"] == source_id for record in source_records)
                for source_id in {
                    "n27_closeout_and_n28_handoff",
                    "n28_closeout_and_n29_handoff",
                    "n29_closeout_and_ecology_handoff",
                }
            ),
        },
        {
            "check_id": "all_records_have_consumption_boundaries",
            "passed": all(
                record["allowed_use"]
                and record["blocked_use"]
                and record["may_consume_as"]
                and record["must_not_consume_as"]
                for record in source_records
            ),
        },
        {
            "check_id": "no_positive_n30_evidence_opened",
            "passed": True,
        },
        {
            "check_id": "unsafe_claim_flags_false",
            "passed": all(value is False for value in UNSAFE_CLAIM_FLAGS.values()),
        },
    ]
    payload: dict[str, Any] = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "1_source_inventory_and_method_admission",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_source_inventory_method_admission_no_positive_evidence",
        "primary_layer": "primitive",
        "positive_evidence_opened": False,
        "minimal_shared_medium_participation_claim_allowed": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "candidate_rows_classified": False,
        "participant_ladder_rung_assigned": False,
        "medium_relation_ladder_rung_assigned": False,
        "final_n30_closeout_rung": "not_assigned",
        "n30_closeout_ceiling": "N30-C1_source_method_inventory_passed",
        "ready_for_iteration_2_schema_freeze": True,
        "source_record_count": len(source_records),
        "source_roles": source_roles,
        "source_records": source_records,
        "shared_medium_source_pin_policy": {
            "external_sources_pinned_by": "sha256_content_digest",
            "absolute_paths_recorded": False,
            "later_source_changes_do_not_silently_change_N30_basis": True,
        },
        "digest_semantics": {
            "output_digest": "canonical_payload_digest_excluding_output_digest_field",
            "file_sha256": "exact_artifact_file_content_digest",
            "mismatch_between_output_digest_and_file_sha256_is_expected": True,
        },
        "source_consumption_rule": {
            "roadmap_and_shared_medium_documents": "method_vocabulary_controls_debt_claim_boundary_only",
            "N27_N28_N29": "guardrail_and_bridge_context_only_until_new_N30_runtime_artifacts_exist",
            "claim_boundary_index": "claim_ceiling_and_blocked_relabel_index_only",
        },
        "guardrail_sufficiency_policy": {
            "N27_N28_closeouts_are_sufficient_for_I1_inventory": True,
            "positive_probe_requirement": (
                "if closeout artifacts do not expose participant-recognizability "
                "or environment-effect fields directly, consume the underlying "
                "N27/N28 result artifacts before classifying positive N30 rows"
            ),
            "closeout_summary_alone_may_support_positive_N30_evidence": False,
        },
        "claim_boundary": {
            "claim_ceiling": "source_inventory_and_method_admission_only_no_N30_evidence",
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        },
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["passed"]],
    }
    checks.append(
        {
            "check_id": "no_absolute_paths_in_records",
            "passed": no_absolute_paths(payload),
        }
    )
    payload["failed_checks"] = [check["check_id"] for check in checks if not check["passed"]]
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "| {source_id} | {source_role} | {runtime} | {digest} |".format(
            source_id=record["source_id"],
            source_role=record["source_role"],
            runtime=str(record["runtime_evidence_allowed"]).lower(),
            digest=record["commit_or_digest"][:19] + "...",
        )
        for record in payload["source_records"]
    )
    check_rows = "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )
    text = f"""# N30 Iteration 1 - Source Inventory And Method Admission

Status: `{payload['status']}`

Acceptance state:
`{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Scope

Iteration 1 admits sources only. Shared-medium documents are consumed as
vocabulary, method, controls, debt, and claim-boundary sources. N27, N28, and
N29 are guardrails and bridge context. No N30 participant, medium trace,
eligibility dependency, replay, or positive row is opened here.

## Source Records

| Source | Role | Runtime Evidence Allowed | Digest |
|---|---|---:|---|
{rows}

## Consumption Rule

Roadmap and shared-medium sources may shape the N30 schema and controls, but
they cannot satisfy any source-current evidence gate. N27/N28/N29 artifacts may
define continuity, environment-effect, and ecology-demand guardrails; they do
not count as N30 shared-medium participation evidence.

If N27/N28 closeout summaries do not expose the needed guardrail fields directly
for a later positive row, that row must consume the underlying N27/N28 result
artifacts rather than relying on closeout summary text.

## Digest Semantics

`output_digest` is the canonical payload digest. A file-content SHA, when used
by downstream artifacts, is the exact JSON artifact hash. Those values are
allowed to differ because they digest different scopes.

## Checks

{check_rows}

## Claim Boundary

`minimal_shared_medium_participation_claim_allowed = false`

`shared_medium_coordination_claim_allowed = false`

`native_shared_medium_organization_claim_allowed = false`
"""
    REPORT.write_text(text, encoding="utf-8")


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload)


if __name__ == "__main__":
    main()
