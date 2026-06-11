#!/usr/bin/env python3
"""Build N10 Iteration 15 Hypothesis C closeout and handoff.

Iteration 15 closes N10 by combining:

* Hypothesis A bounded artifact-only closeout;
* Hypothesis B support-sensitive matrix closeout;
* Hypothesis C native-policy gap inventory;
* Hypothesis C native contract requirements.

It does not implement native behavior and does not open native support flags.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
OUTPUT_PATH = (
    EXPERIMENT / "outputs" / "n10_iteration_15_hypothesis_c_closeout_and_handoff.json"
)
REPORT_PATH = (
    EXPERIMENT / "reports" / "n10_iteration_15_hypothesis_c_closeout_and_handoff.md"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N10-lgrc-agentic-like-integration/scripts/"
    "build_n10_iteration_15_hypothesis_c_closeout_and_handoff.py"
)

SOURCE_ARTIFACTS = {
    "n10_hypothesis_a_closeout": (
        EXPERIMENT / "outputs" / "n10_iteration_9_artifact_only_closeout.json"
    ),
    "n10_hypothesis_b_closeout": (
        EXPERIMENT
        / "outputs"
        / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.json"
    ),
    "n10_hypothesis_c_inventory": (
        EXPERIMENT
        / "outputs"
        / "n10_iteration_13_hypothesis_c_native_policy_gap_inventory.json"
    ),
    "n10_hypothesis_c_contract": (
        EXPERIMENT
        / "outputs"
        / "n10_iteration_14_hypothesis_c_native_contract_requirements.json"
    ),
}

SOURCE_REPORTS = {
    "n10_hypothesis_a_closeout": (
        EXPERIMENT / "reports" / "n10_iteration_9_artifact_only_closeout.md"
    ),
    "n10_hypothesis_b_closeout": (
        EXPERIMENT
        / "reports"
        / "n10_iteration_12_hypothesis_b_support_state_matrix_closeout.md"
    ),
    "n10_hypothesis_c_inventory": (
        EXPERIMENT
        / "reports"
        / "n10_iteration_13_hypothesis_c_native_policy_gap_inventory.md"
    ),
    "n10_hypothesis_c_contract": (
        EXPERIMENT
        / "reports"
        / "n10_iteration_14_hypothesis_c_native_contract_requirements.md"
    ),
}

EXPECTED_NATIVE_BLOCKERS = [
    "native_route_conductance_memory_policy_missing",
    "native_response_magnitude_policy_missing_for_unbounded_perturbations",
    "native_identity_acceptance_validator_missing",
    "native_agentic_like_integration_policy_missing",
]

CLAIM_FLAGS = {
    "agentic_like_claim_allowed": False,
    "native_agentic_like_integration_supported": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_identity_claim_allowed": False,
    "unrestricted_movement_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def with_digest(record: dict[str, Any], digest_field: str) -> dict[str, Any]:
    result = dict(record)
    result[digest_field] = digest_value(
        {key: value for key, value in result.items() if key != digest_field}
    )
    return result


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def prior_output_digest_valid(artifact: dict[str, Any]) -> bool:
    if "output_digest" not in artifact:
        return True
    return artifact["output_digest"] == output_digest(artifact)


def build_source_records(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_records = {
        key: {
            "path": rel(path),
            "sha256": digest_file(path),
            "status": artifacts[key].get("status"),
            "output_digest": artifacts[key].get("output_digest"),
            "output_digest_valid": prior_output_digest_valid(artifacts[key]),
        }
        for key, path in SOURCE_ARTIFACTS.items()
    }
    report_records = {
        key: {
            "path": rel(path),
            "sha256": digest_file(path),
        }
        for key, path in SOURCE_REPORTS.items()
        if path.exists()
    }
    return artifact_records, report_records


def build_phase8_handoff(contract: dict[str, Any]) -> dict[str, Any]:
    closeout = contract["hypothesis_c_contract_closeout"]
    phases = [
        {
            "order": row["order"],
            "phase": row["phase"],
            "reason": row["reason"],
            "contract_rows": row["contract_rows"],
        }
        for row in contract["phase_8_absorption_order"]
    ]
    return with_digest(
        {
            "handoff_id": "n10_i15_phase8_native_absorption_handoff_v1",
            "handoff_status": "ready_as_contract_not_implementation",
            "primary_native_blockers": closeout["primary_native_blockers"],
            "required_policy_records": closeout["required_policy_records"],
            "native_absorption_order": phases,
            "not_yet_phase8_work_opened": True,
            "implementation_boundary": (
                "future Phase 8 work may implement selected native LGRC "
                "mechanisms in src/*; N10 Iteration 15 only records the "
                "contract and ordering"
            ),
        },
        "phase8_handoff_digest",
    )


def build_n11_handoff(
    hypothesis_a: dict[str, Any],
    hypothesis_b: dict[str, Any],
    hypothesis_c_contract: dict[str, Any],
) -> dict[str, Any]:
    return with_digest(
        {
            "handoff_id": "n10_i15_n11_consumption_handoff_v1",
            "ready_for_n11": True,
            "consumable_artifacts": [
                {
                    "key": "n10_hypothesis_a_closeout",
                    "path": rel(SOURCE_ARTIFACTS["n10_hypothesis_a_closeout"]),
                    "scope": hypothesis_a["closeout"]["final_n10_ceiling"],
                    "digest": hypothesis_a["closeout"]["closeout_row_digest"],
                },
                {
                    "key": "n10_hypothesis_b_closeout",
                    "path": rel(SOURCE_ARTIFACTS["n10_hypothesis_b_closeout"]),
                    "scope": hypothesis_b["hypothesis_b_closeout"][
                        "hypothesis_b_status"
                    ],
                    "digest": hypothesis_b["hypothesis_b_closeout"][
                        "hypothesis_b_closeout_digest"
                    ],
                },
                {
                    "key": "n10_hypothesis_c_contract",
                    "path": rel(SOURCE_ARTIFACTS["n10_hypothesis_c_contract"]),
                    "scope": hypothesis_c_contract["hypothesis_c_contract_closeout"][
                        "contract_status"
                    ],
                    "digest": hypothesis_c_contract["hypothesis_c_contract_closeout"][
                        "contract_requirements_digest"
                    ],
                },
            ],
            "n11_may_consume": [
                "bounded artifact-only route-memory-support-regulation integration",
                "support-state matrix with intact, mild-withdrawal, disrupted, and restored lanes",
                "native contract requirements as blockers or design constraints",
            ],
            "n11_must_preserve": [
                "N10 evidence is bounded and artifact-only",
                "N06 route context remains selection-only unless a later source broadens it",
                "N08 memory/trail is not native route conductance memory yet",
                "N09 regulation is goal-proxy regulation, not semantic goal ownership",
                "N07 support/invariance is not identity acceptance",
                "disrupted support blocks attempted A6/ALI6 unless explicit restoration is present",
                "fully native agentic-like integration remains blocked until a separate native implementation",
            ],
            "n11_must_not_overread": [
                "agency",
                "intention",
                "semantic goal ownership",
                "identity acceptance",
                "RC identity collapse",
                "ACO or ant-colony behavior",
                "biological behavior",
                "personhood",
                "unrestricted agency",
                "fully native agentic-like integration",
            ],
        },
        "n11_handoff_digest",
    )


def build_final_closeout(
    artifacts: dict[str, dict[str, Any]],
    source_records: dict[str, Any],
    phase8_handoff: dict[str, Any],
    n11_handoff: dict[str, Any],
) -> dict[str, Any]:
    hypothesis_a = artifacts["n10_hypothesis_a_closeout"]
    hypothesis_b = artifacts["n10_hypothesis_b_closeout"]
    hypothesis_c_inventory = artifacts["n10_hypothesis_c_inventory"]
    hypothesis_c_contract = artifacts["n10_hypothesis_c_contract"]
    record = {
        "n10_iteration_15_closeout_row_id": "n10_i15_hypothesis_c_closeout_and_handoff_v1",
        "n10_final_status": (
            "closed_bounded_artifact_only_agentic_like_integration_with_"
            "support_sensitive_and_native_contract_handoff"
        ),
        "final_n10_ceiling": hypothesis_a["closeout"]["final_n10_ceiling"],
        "integration_level": hypothesis_a["closeout"]["integration_level"],
        "n10_category_level": hypothesis_a["closeout"]["n10_category_level"],
        "bounded_artifact_only_agentic_like_integration_supported": hypothesis_a[
            "closeout"
        ]["final_ceiling_supported"],
        "support_sensitive_integration_supported": hypothesis_b[
            "hypothesis_b_closeout"
        ]["hypothesis_b_supported"],
        "hypothesis_b_status": hypothesis_b["hypothesis_b_closeout"][
            "hypothesis_b_status"
        ],
        "hypothesis_c_inventory_status": hypothesis_c_inventory[
            "hypothesis_c_inventory_closeout"
        ]["inventory_status"],
        "hypothesis_c_contract_status": hypothesis_c_contract[
            "hypothesis_c_contract_closeout"
        ]["contract_status"],
        "fully_native_agentic_like_integration_supported": False,
        "native_support_flags_opened": False,
        "artifact_only": True,
        "runtime_state_used": False,
        "source_artifact_records": source_records,
        "phase8_handoff_digest": phase8_handoff["phase8_handoff_digest"],
        "n11_handoff_digest": n11_handoff["n11_handoff_digest"],
        "primary_native_blockers": hypothesis_c_contract[
            "hypothesis_c_contract_closeout"
        ]["primary_native_blockers"],
        "required_policy_records": hypothesis_c_contract[
            "hypothesis_c_contract_closeout"
        ]["required_policy_records"],
        "native_absorption_order": [
            row["phase"] for row in phase8_handoff["native_absorption_order"]
        ],
        "blocked_claims": [
            "agency",
            "intention",
            "semantic_goal_ownership",
            "semantic_goal_understanding",
            "identity_acceptance",
            "runtime_identity_acceptance",
            "rc_identity_collapse",
            "aco_like_behavior",
            "ant_colony_behavior",
            "locomotion_like_behavior",
            "biological_behavior",
            "personhood",
            "unrestricted_identity",
            "unrestricted_movement",
            "unrestricted_agency",
            "fully_native_agentic_like_integration",
        ],
        "claim_flags": CLAIM_FLAGS,
        "next_experiment": "N11_broader_general_agentic_like_integration",
    }
    return with_digest(record, "n10_iteration_15_closeout_digest")


def build_controls(
    final_closeout: dict[str, Any],
    phase8_handoff: dict[str, Any],
    n11_handoff: dict[str, Any],
) -> dict[str, Any]:
    return {
        "bounded_artifact_only_ceiling_preserved": {
            "control_passed": final_closeout["final_n10_ceiling"]
            == "bounded_artifact_only_agentic_like_integration_candidate"
            and final_closeout["bounded_artifact_only_agentic_like_integration_supported"]
            is True,
            "primary_blocker": "bounded_artifact_only_ceiling_missing",
            "reason": "Hypothesis A remains the positive N10 ceiling.",
        },
        "support_sensitive_closeout_preserved": {
            "control_passed": final_closeout["support_sensitive_integration_supported"]
            is True
            and final_closeout["hypothesis_b_status"]
            == "supported_bounded_support_sensitive_full_composition",
            "primary_blocker": "support_sensitive_closeout_missing",
            "reason": "Hypothesis B remains support-sensitive and source-backed.",
        },
        "native_contract_handoff_complete": {
            "control_passed": final_closeout["hypothesis_c_contract_status"]
            == "native_contract_requirements_complete",
            "primary_blocker": "native_contract_requirements_missing",
            "reason": "Hypothesis C has contract requirements for future native absorption.",
        },
        "fully_native_still_blocked": {
            "control_passed": final_closeout[
                "fully_native_agentic_like_integration_supported"
            ]
            is False
            and final_closeout["native_support_flags_opened"] is False,
            "primary_blocker": "fully_native_support_opened_without_phase8",
            "reason": "N10 does not open fully native support.",
        },
        "native_blockers_preserved": {
            "control_passed": set(EXPECTED_NATIVE_BLOCKERS)
            == set(final_closeout["primary_native_blockers"]),
            "primary_blocker": "native_blocker_set_changed",
            "reason": "The exact fully native blocker set is preserved.",
        },
        "phase8_handoff_defined": {
            "control_passed": phase8_handoff["handoff_status"]
            == "ready_as_contract_not_implementation"
            and len(phase8_handoff["native_absorption_order"]) == 6,
            "primary_blocker": "phase8_handoff_missing",
            "reason": "Future native absorption order is recorded without opening implementation.",
        },
        "n11_handoff_defined": {
            "control_passed": n11_handoff["ready_for_n11"] is True
            and len(n11_handoff["n11_must_preserve"]) >= 7
            and len(n11_handoff["n11_must_not_overread"]) >= 8,
            "primary_blocker": "n11_handoff_missing",
            "reason": "N11 may consume N10 only under explicit constraints.",
        },
        "claim_flags_all_false": {
            "control_passed": all(
                value is False for value in final_closeout["claim_flags"].values()
            ),
            "primary_blocker": "claim_promotion_blocked",
            "reason": "No agency, identity, ACO, biological, or native support claims are emitted.",
        },
    }


def build_checks(
    artifacts: dict[str, dict[str, Any]],
    source_records: dict[str, Any],
    report_records: dict[str, Any],
    final_closeout: dict[str, Any],
    phase8_handoff: dict[str, Any],
    n11_handoff: dict[str, Any],
    controls: dict[str, Any],
) -> dict[str, bool]:
    return {
        "all_required_artifacts_present": set(SOURCE_ARTIFACTS).issubset(
            source_records
        ),
        "all_required_reports_present": set(SOURCE_REPORTS).issubset(report_records),
        "all_required_artifacts_passed": all(
            artifact.get("status") == "passed" for artifact in artifacts.values()
        ),
        "prior_output_digests_valid": all(
            record["output_digest_valid"] for record in source_records.values()
        ),
        "hypothesis_a_ceiling_supported": final_closeout[
            "bounded_artifact_only_agentic_like_integration_supported"
        ]
        is True,
        "hypothesis_b_support_sensitive_supported": final_closeout[
            "support_sensitive_integration_supported"
        ]
        is True,
        "hypothesis_c_inventory_complete": final_closeout[
            "hypothesis_c_inventory_status"
        ]
        == "native_policy_gap_inventory_complete",
        "hypothesis_c_contract_complete": final_closeout[
            "hypothesis_c_contract_status"
        ]
        == "native_contract_requirements_complete",
        "fully_native_agentic_like_integration_blocked": final_closeout[
            "fully_native_agentic_like_integration_supported"
        ]
        is False,
        "native_support_flags_not_opened": final_closeout["native_support_flags_opened"]
        is False,
        "native_blockers_preserved": set(EXPECTED_NATIVE_BLOCKERS)
        == set(final_closeout["primary_native_blockers"]),
        "phase8_handoff_digest_valid": phase8_handoff["phase8_handoff_digest"]
        == digest_value(
            {
                key: value
                for key, value in phase8_handoff.items()
                if key != "phase8_handoff_digest"
            }
        ),
        "n11_handoff_digest_valid": n11_handoff["n11_handoff_digest"]
        == digest_value(
            {
                key: value
                for key, value in n11_handoff.items()
                if key != "n11_handoff_digest"
            }
        ),
        "final_closeout_digest_valid": final_closeout[
            "n10_iteration_15_closeout_digest"
        ]
        == digest_value(
            {
                key: value
                for key, value in final_closeout.items()
                if key != "n10_iteration_15_closeout_digest"
            }
        ),
        "claim_flags_all_false": all(
            value is False for value in final_closeout["claim_flags"].values()
        ),
        "controls_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
        "src_clean_for_iteration_15": git_status_short("src") == "",
    }


def build_output() -> dict[str, Any]:
    artifacts = {key: load_json(path) for key, path in SOURCE_ARTIFACTS.items()}
    source_records, report_records = build_source_records(artifacts)
    phase8_handoff = build_phase8_handoff(artifacts["n10_hypothesis_c_contract"])
    n11_handoff = build_n11_handoff(
        artifacts["n10_hypothesis_a_closeout"],
        artifacts["n10_hypothesis_b_closeout"],
        artifacts["n10_hypothesis_c_contract"],
    )
    final_closeout = build_final_closeout(
        artifacts,
        source_records,
        phase8_handoff,
        n11_handoff,
    )
    controls = build_controls(final_closeout, phase8_handoff, n11_handoff)
    checks = build_checks(
        artifacts,
        source_records,
        report_records,
        final_closeout,
        phase8_handoff,
        n11_handoff,
        controls,
    )
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 15 passes if N10 closes with a bounded artifact-only "
            "agentic-like integration candidate, explicit support-sensitive "
            "Hypothesis B evidence, and a named native-policy-gap handoff for "
            "any future fully native implementation. No agency, semantic goal "
            "ownership, identity acceptance, ACO, biological, personhood, "
            "unrestricted agency, or fully native agentic-like integration "
            "claim is emitted."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n10_iteration_15_hypothesis_c_closeout_and_handoff_v1",
        "experiment": "2026-05-N10-lgrc-agentic-like-integration",
        "iteration": 15,
        "purpose": "hypothesis_c_closeout_and_handoff",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "source_artifacts": source_records,
        "source_reports": report_records,
        "phase8_native_absorption_handoff": phase8_handoff,
        "n11_consumption_handoff": n11_handoff,
        "n10_final_closeout": final_closeout,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "next_experiment": "N11_broader_general_agentic_like_integration",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    closeout = output["n10_final_closeout"]
    phase8 = output["phase8_native_absorption_handoff"]
    n11 = output["n11_consumption_handoff"]
    lines = [
        "# N10 Iteration 15 Hypothesis C Closeout And Handoff",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 15 closes N10 with the bounded artifact-only result, the",
        "support-sensitive B-path matrix, and the native contract handoff. It",
        "does not implement native behavior, edit `src/*`, or open native",
        "support flags.",
        "",
        "```text",
        f"n10_final_status = {closeout['n10_final_status']}",
        f"final_n10_ceiling = {closeout['final_n10_ceiling']}",
        f"integration_level = {closeout['integration_level']}",
        f"n10_category_level = {closeout['n10_category_level']}",
        "bounded_artifact_only_agentic_like_integration_supported = true",
        "support_sensitive_integration_supported = true",
        "fully_native_agentic_like_integration_supported = false",
        "native_support_flags_opened = false",
        "```",
        "",
        "## Interpretation",
        "",
        "N10 succeeded at the bounded artifact-only scope. It shows that route",
        "choice, memory-shaped affordance, identity/support evidence, and",
        "goal-proxy regulation compose into a replayable integration candidate,",
        "and that the composition remains support-sensitive. It does not prove",
        "agency, semantic goal ownership, identity acceptance, ACO behavior,",
        "biological behavior, personhood, or fully native agentic-like",
        "integration.",
        "",
        "## Native Handoff",
        "",
        "Fully native agentic-like integration remains blocked by:",
        "",
        "```text",
        "\n".join(closeout["primary_native_blockers"]),
        "```",
        "",
        "Future native absorption order:",
        "",
        "```json",
        json.dumps(phase8["native_absorption_order"], indent=2, sort_keys=True),
        "```",
        "",
        "## N11 Handoff",
        "",
        "N11 may consume these artifacts under the recorded constraints:",
        "",
        "```json",
        json.dumps(n11, indent=2, sort_keys=True),
        "```",
        "",
        "## Final Closeout",
        "",
        "```json",
        json.dumps(closeout, indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(output["controls"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Reproduction",
        "",
        "```text",
        output["command"],
        "```",
        "",
        "Output digest:",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    if output["status"] != "passed":
        raise SystemExit(f"Iteration 15 failed: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
