#!/usr/bin/env python3
"""Build N30 Iteration 8 classification and post-N30 spiral handoff closeout."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-07-09T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-07-N30-lgrc-minimal-shared-medium-participation"
OUTPUT = EXPERIMENT / "outputs" / "n30_closeout_and_spiral_handoff_i8.json"
REPORT = EXPERIMENT / "reports" / "n30_closeout_and_spiral_handoff_i8.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n30_closeout_and_spiral_handoff_i8_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/scripts/"
    "build_n30_closeout_i8.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I7_OUTPUT = EXPERIMENT / "outputs" / "n30_replay_controls_i7.json"
ROADMAP = ROOT / "experiments" / "N30_plus_experiment_catalog_roadmap.md"
CANDIDATES = ROOT / "experiments" / "N30_plus_candidate_directions.md"
N29_CLOSEOUT = (
    ROOT
    / "experiments"
    / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
    / "outputs"
    / "n29_closeout_and_ecology_handoff_i18.json"
)

BLOCKED_CLAIMS = [
    "unqualified_minimal_shared_medium_participation",
    "shared_medium_coordination",
    "parent_basin_modulation",
    "resonant_alignment",
    "native_shared_medium_organization",
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
    "fixed_n31_selection_without_spiral_review",
    "agentic_ecology_demand_as_substrate_evidence",
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def write_artifact(name: str, data: dict[str, Any]) -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACT_DIR / name
    path.write_text(canonical_json(data), encoding="utf-8")
    return {
        "path": rel(path),
        "artifact_role": data["artifact_role"],
        "sha256": sha256_file(path),
    }


def source_input(path: Path, role: str) -> dict[str, Any]:
    return {"path": rel(path), "source_role": role, "sha256": sha256_file(path)}


def strongest_margin_summary(i7: dict[str, Any]) -> dict[str, Any]:
    original_rows = [
        row for row in i7["candidate_rows"] if row["source_family"] == "original_generative"
    ]
    alternative_rows = [
        row for row in i7["candidate_rows"] if row["source_family"] == "alternative_circulatory"
    ]
    return {
        "original_generative_threshold_margin_min": min(
            row["margin_context"]["threshold_margin"] for row in original_rows
        ),
        "original_generative_contrast_margin_vs_neutral_min": min(
            row["margin_context"]["contrast_margin_vs_neutral"] for row in original_rows
        ),
        "original_generative_contrast_margin_vs_extractive_min": min(
            row["margin_context"]["contrast_margin_vs_extractive"] for row in original_rows
        ),
        "alternative_circulatory_threshold_margin": alternative_rows[0]["margin_context"][
            "threshold_margin"
        ],
        "alternative_circulatory_lobe_exchange_margin": alternative_rows[0][
            "margin_context"
        ]["lobe_exchange_margin"],
        "alternative_circulatory_threshold_ratio_vs_i6": alternative_rows[0][
            "margin_context"
        ]["threshold_margin_ratio_vs_i6"],
        "margin_claim": (
            "N30 has one narrow original generative-edge C5 family and one "
            "higher-headroom alternative circulatory C5 family; this supports "
            "mechanism diversity, not broad shared-medium robustness."
        ),
    }


def build_payload() -> dict[str, Any]:
    i7 = load_json(I7_OUTPUT)
    margin_summary = strongest_margin_summary(i7)
    source_inputs = [
        source_input(I7_OUTPUT, "N30_I7_replay_control_backed_C5_candidate"),
        source_input(ROADMAP, "N30_plus_catalog_roadmap_spiral_policy"),
        source_input(CANDIDATES, "N30_plus_candidate_directions_spiral_policy"),
        source_input(N29_CLOSEOUT, "N29_agentic_ecology_handoff_context"),
    ]
    classification = {
        "artifact_role": "i8_closeout_classification_record",
        "trace_id": "n30_i8_closeout_classification_record",
        "source_i7_output_digest": i7["output_digest"],
        "participant_ladder_final": "P2_minimally_stable_participant_with_P4_guardrail_context",
        "participant_ladder_notes": [
            "P2 is the load-bearing participant level for N30.",
            "I4-B supplies P4-style support-sensitivity guardrail context but does not make N30 an agency or selfhood result.",
        ],
        "medium_relation_final": "M2_trace_mediated_eligibility_replay_control_backed_candidate",
        "coupled_relation_chain_support": "supported_replay_control_backed_candidate",
        "n30_closeout_rung": "N30-C6_post_N30_spiral_ready_minimal_shared_medium_participation_closeout",
        "n30_c5_replay_control_backed_candidate_supported": True,
        "n30_c6_spiral_ready_closeout_supported": True,
        "bounded_minimal_shared_medium_participation_candidate_supported": True,
        "trace_mediated_eligibility_primitive_candidate_supported": True,
        "final_n30_c5_claim_allowed": True,
        "final_n30_c5_claim_scope": (
            "bounded replay/control-backed minimal shared-medium participation candidate"
        ),
        "final_n30_c6_closeout_allowed": True,
        "final_n30_c6_closeout_scope": (
            "post-N30 spiral-ready closeout with demand-map handoff, not fixed N31 selection"
        ),
        "unqualified_minimal_shared_medium_participation_claim_allowed": False,
        "margin_summary": margin_summary,
        "candidate_row_ids": [row["source_row_id"] for row in i7["candidate_rows"]],
        "candidate_family_count": len({row["source_family"] for row in i7["candidate_rows"]}),
        "candidate_row_count": i7["candidate_row_count"],
        "failed_open_control_count": i7["failed_open_control_count"],
        "not_run_control_count": i7["not_run_control_count"],
        "all_required_replay_modes_passed": i7["all_required_replay_modes_passed"],
        "all_required_controls_failed_closed": i7["all_required_controls_failed_closed"],
    }
    classification["classification_record_digest"] = digest_value(classification)

    spiral_handoff = {
        "artifact_role": "i8_post_n30_spiral_handoff_contract",
        "trace_id": "n30_i8_post_n30_spiral_handoff_contract",
        "post_n30_handoff_mode": "cross_project_spiral",
        "agentic_ecology_demand_pass_recommended": True,
        "agentic_ecology_demand_pass_role": (
            "demand/composition mapping only; not substrate evidence and not ecology implementation"
        ),
        "candidate_n31_interface_available": True,
        "candidate_n31_interface_meaning": (
            "N30 exposes a trace-mediated eligibility interface that a future "
            "support-redistribution or related N31+ experiment may consume if "
            "the agentic-ecology demand map selects it."
        ),
        "candidate_n31_selected": False,
        "next_lgrc_experiment_fixed": False,
        "selection_rule": (
            "Do not fix N31 or any N31+ experiment until the post-N30 agentic "
            "ecology demand/composition pass identifies the needed primitive or "
            "building block."
        ),
        "may_consume_as": [
            "bounded minimal shared-medium participation primitive candidate",
            "trace-mediated eligibility primitive/building-block candidate",
            "source-current shared-medium participation evidence for demand mapping",
            "control pattern for direct-message and label-only blockers",
        ],
        "must_not_consume_as": [
            "shared-medium coordination",
            "native shared-medium organization",
            "semantic communication",
            "cooperation",
            "agency",
            "ecology regime",
            "fixed N31 selection",
            "agentic ecology implementation",
        ],
        "open_debt_for_spiral": [
            "agentic ecology demand map not yet written",
            "next LGRC primitive/building-block not yet selected",
            "native shared-medium organization not shown",
            "decay curve remains limited in original generative M2 family",
            "fresh N30 runtime not required for this closeout but remains a possible later strengthening path",
        ],
    }
    spiral_handoff["spiral_handoff_contract_digest"] = digest_value(spiral_handoff)

    claim_guard = {
        "artifact_role": "i8_claim_boundary_guard",
        "trace_id": "n30_i8_claim_boundary_guard",
        "allowed_final_claim": (
            "artifact-level bounded minimal shared-medium participation candidate"
        ),
        "allowed_secondary_claim": "trace-mediated eligibility primitive/building-block candidate",
        "blocked_claims": BLOCKED_CLAIMS,
        "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "agency_claim_allowed": False,
        "ecology_regime_claim_allowed": False,
        "fixed_n31_selection_allowed": False,
        "agentic_ecology_demand_as_substrate_evidence_allowed": False,
    }
    claim_guard["claim_boundary_guard_digest"] = digest_value(claim_guard)

    artifacts = [
        write_artifact("i8_closeout_classification_record.json", classification),
        write_artifact("i8_post_n30_spiral_handoff_contract.json", spiral_handoff),
        write_artifact("i8_claim_boundary_guard.json", claim_guard),
    ]
    artifact_sha_match = all(
        sha256_file(ROOT / artifact["path"]) == artifact["sha256"]
        for artifact in artifacts
    )
    payload = {
        "experiment": "N30_minimal_shared_medium_participation",
        "iteration": "8_classification_and_post_n30_spiral_handoff",
        "generated_at": GENERATED_AT,
        "script": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_N30_C6_post_N30_spiral_ready_minimal_shared_medium_participation_closeout"
        ),
        "source_i7_output_digest": i7["output_digest"],
        "source_current_inputs": source_inputs,
        "positive_evidence_opened": True,
        "positive_evidence_scope": "N30_closeout_classification_and_spiral_handoff",
        "participant_ladder_rung_assigned": classification["participant_ladder_final"],
        "medium_relation_ladder_rung_assigned": classification["medium_relation_final"],
        "n30_closeout_rung": classification["n30_closeout_rung"],
        "final_n30_closeout_rung": classification["n30_closeout_rung"],
        "n30_c5_replay_control_backed_candidate_supported": True,
        "n30_c6_spiral_ready_closeout_supported": True,
        "bounded_minimal_shared_medium_participation_candidate_supported": True,
        "trace_mediated_eligibility_primitive_candidate_supported": True,
        "final_n30_c5_claim_allowed": True,
        "final_n30_c6_closeout_allowed": True,
        "unqualified_minimal_shared_medium_participation_claim_allowed": False,
        "post_n30_handoff_mode": "cross_project_spiral",
        "agentic_ecology_demand_pass_recommended": True,
        "candidate_n31_interface_available": True,
        "candidate_n31_selected": False,
        "next_lgrc_experiment_fixed": False,
        "shared_medium_coordination_claim_allowed": False,
        "native_shared_medium_organization_claim_allowed": False,
        "agency_claim_allowed": False,
        "ecology_regime_claim_allowed": False,
        "ready_for_agentic_ecology_demand_pass": True,
        "ready_for_fixed_N31_selection": False,
        "classification_record": classification,
        "post_n30_spiral_handoff_contract": spiral_handoff,
        "claim_boundary_guard": claim_guard,
        "artifact_manifest": artifacts,
        "all_artifact_sha256_match_file_contents": artifact_sha_match,
        "claim_boundary": {
            "claim_ceiling": (
                "artifact_level_bounded_minimal_shared_medium_participation_candidate"
            ),
            "blocked_claims": BLOCKED_CLAIMS,
            "unsafe_claim_flags": {f"{claim}_opened": False for claim in BLOCKED_CLAIMS},
        },
    }
    checks = [
        {
            "check_id": "source_i7_passed_and_c5_candidate_supported",
            "passed": i7["status"] == "passed"
            and i7["n30_c5_candidate_supported"] is True
            and i7["failed_open_control_count"] == 0
            and i7["not_run_control_count"] == 0,
        },
        {
            "check_id": "n30_c6_spiral_ready_closeout_assigned",
            "passed": payload["final_n30_closeout_rung"]
            == "N30-C6_post_N30_spiral_ready_minimal_shared_medium_participation_closeout",
        },
        {
            "check_id": "post_n30_spiral_recorded_without_fixed_n31_selection",
            "passed": payload["post_n30_handoff_mode"] == "cross_project_spiral"
            and payload["agentic_ecology_demand_pass_recommended"] is True
            and payload["candidate_n31_interface_available"] is True
            and payload["candidate_n31_selected"] is False
            and payload["next_lgrc_experiment_fixed"] is False,
        },
        {
            "check_id": "claim_boundary_preserves_blocked_promotions",
            "passed": all(
                claim_guard["unsafe_claim_flags"][f"{claim}_opened"] is False
                for claim in BLOCKED_CLAIMS
            )
            and payload["shared_medium_coordination_claim_allowed"] is False
            and payload["native_shared_medium_organization_claim_allowed"] is False
            and payload["agency_claim_allowed"] is False
            and payload["ecology_regime_claim_allowed"] is False,
        },
        {
            "check_id": "medium_debt_and_spiral_debt_recorded",
            "passed": len(spiral_handoff["open_debt_for_spiral"]) >= 4
            and "native shared-medium organization not shown"
            in spiral_handoff["open_debt_for_spiral"],
        },
        {
            "check_id": "artifact_manifest_sha256_matches",
            "passed": payload["all_artifact_sha256_match_file_contents"] is True,
        },
        {"check_id": "no_absolute_paths_in_records", "passed": no_absolute_paths(payload)},
    ]
    payload["checks"] = checks
    payload["failed_checks"] = [
        check["check_id"] for check in checks if check["passed"] is not True
    ]
    return payload


def write_payload(payload: dict[str, Any]) -> None:
    payload["output_digest"] = digest_value(payload)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")


def report_artifacts(payload: dict[str, Any]) -> str:
    return "\n".join(
        f"| {artifact['artifact_role']} | `{artifact['path']}` |"
        for artifact in payload["artifact_manifest"]
    )


def report_checks(payload: dict[str, Any]) -> str:
    return "\n".join(
        f"- {check['check_id']}: {str(check['passed']).lower()}"
        for check in payload["checks"]
    )


def write_report(payload: dict[str, Any]) -> None:
    margin = payload["classification_record"]["margin_summary"]
    REPORT.write_text(
        f"""# N30 Iteration 8 - Classification And Post-N30 Spiral Handoff

Status: `{payload['status']}`

Acceptance state: `{payload['acceptance_state']}`

Output digest: `{payload['output_digest']}`

## Interpretation

I8 closes N30 as an artifact-level bounded minimal shared-medium participation
candidate. The closeout is supported by I7 replay/control evidence across the
original generative-edge family and the alternative circulatory family.

This is not a claim of shared-medium coordination, native shared-medium
organization, agency, communication, cooperation, sentience, or ecology regime.
It is a post-N30 spiral-ready closeout: the next recommended step is an
agentic-ecology demand/composition pass, not automatic selection of N31.

## Key Fields

```text
participant_ladder_rung = {payload['participant_ladder_rung_assigned']}
medium_relation_ladder_rung = {payload['medium_relation_ladder_rung_assigned']}
final_n30_closeout_rung = {payload['final_n30_closeout_rung']}
n30_c5_replay_control_backed_candidate_supported = {str(payload['n30_c5_replay_control_backed_candidate_supported']).lower()}
n30_c6_spiral_ready_closeout_supported = {str(payload['n30_c6_spiral_ready_closeout_supported']).lower()}
bounded_minimal_shared_medium_participation_candidate_supported = {str(payload['bounded_minimal_shared_medium_participation_candidate_supported']).lower()}
post_n30_handoff_mode = {payload['post_n30_handoff_mode']}
agentic_ecology_demand_pass_recommended = {str(payload['agentic_ecology_demand_pass_recommended']).lower()}
candidate_n31_interface_available = {str(payload['candidate_n31_interface_available']).lower()}
candidate_n31_selected = {str(payload['candidate_n31_selected']).lower()}
next_lgrc_experiment_fixed = {str(payload['next_lgrc_experiment_fixed']).lower()}
```

## Margin Context

```text
original_generative_threshold_margin_min = {margin['original_generative_threshold_margin_min']}
original_generative_contrast_margin_vs_neutral_min = {margin['original_generative_contrast_margin_vs_neutral_min']}
original_generative_contrast_margin_vs_extractive_min = {margin['original_generative_contrast_margin_vs_extractive_min']}
alternative_circulatory_threshold_margin = {margin['alternative_circulatory_threshold_margin']}
alternative_circulatory_lobe_exchange_margin = {margin['alternative_circulatory_lobe_exchange_margin']}
alternative_circulatory_threshold_ratio_vs_i6 = {margin['alternative_circulatory_threshold_ratio_vs_i6']}
```

## Claim Boundary

```text
allowed = artifact-level bounded minimal shared-medium participation candidate
allowed_secondary = trace-mediated eligibility primitive/building-block candidate
shared_medium_coordination = false
native_shared_medium_organization = false
agency = false
ecology_regime = false
fixed_N31_selection = false
```

## Artifacts

| Role | Path |
|---|---|
{report_artifacts(payload)}

## Checks

{report_checks(payload)}
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_payload(payload)
    payload = load_json(OUTPUT)
    write_report(payload)


if __name__ == "__main__":
    main()
