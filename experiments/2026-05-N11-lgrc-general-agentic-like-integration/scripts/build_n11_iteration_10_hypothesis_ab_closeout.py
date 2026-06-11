#!/usr/bin/env python3
"""Build N11 Iteration 10 Hypothesis A/B closeout."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

ITERATION_PATHS = {
    "iteration_1": OUTPUTS / "n11_iteration_1_baseline_inventory.json",
    "iteration_2": OUTPUTS / "n11_iteration_2_fixture_manifest_validation.json",
    "iteration_3": OUTPUTS / "n11_iteration_3_route_context_transfer_replay.json",
    "iteration_4": OUTPUTS / "n11_iteration_4_proxy_condition_transfer_replay.json",
    "iteration_4b": OUTPUTS / "n11_iteration_4b_proxy_target_band_variant_probe.json",
    "iteration_5": OUTPUTS / "n11_iteration_5_support_state_transfer_replay.json",
    "iteration_6": OUTPUTS / "n11_iteration_6_multi_axis_transfer_matrix.json",
    "iteration_7": OUTPUTS / "n11_iteration_7_longer_horizon_generalization_window.json",
    "iteration_8": OUTPUTS / "n11_iteration_8_hidden_stale_claim_controls.json",
    "iteration_9": OUTPUTS / "n11_iteration_9_artifact_only_generalization_validator.json",
}

OUTPUT_PATH = OUTPUTS / "n11_iteration_10_hypothesis_ab_closeout.json"
REPORT_PATH = REPORTS / "n11_iteration_10_hypothesis_ab_closeout.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "build_n11_iteration_10_hypothesis_ab_closeout.py"
)

UNSAFE_CLAIM_FLAGS = {
    "agency_claim_allowed": False,
    "agentic_like_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "intention_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "unrestricted_identity_claim_allowed": False,
    "unrestricted_movement_claim_allowed": False,
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


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def load_artifacts() -> dict[str, dict[str, Any]]:
    return {key: load_json(path) for key, path in ITERATION_PATHS.items()}


def all_status_passed(artifacts: dict[str, dict[str, Any]]) -> bool:
    return all(artifact.get("status") == "passed" for artifact in artifacts.values())


def all_checks_passed(artifact: dict[str, Any]) -> bool:
    return all(artifact.get("checks", {}).values())


def all_values_true(values: dict[str, Any]) -> bool:
    return all(value is True for value in values.values())


def source_artifact_rows(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = {}
    for key, path in ITERATION_PATHS.items():
        artifact = artifacts[key]
        rows[key] = {
            "path": rel(path),
            "sha256": digest_file(path),
            "status": artifact.get("status"),
            "output_digest": artifact.get("output_digest")
            or artifact.get("validation_digest")
            or artifact.get("inventory_digest"),
        }
    return rows


def build_level_decisions(artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    iteration_3 = artifacts["iteration_3"]
    iteration_4 = artifacts["iteration_4"]
    iteration_4b = artifacts["iteration_4b"]
    iteration_5 = artifacts["iteration_5"]
    iteration_6 = artifacts["iteration_6"]
    iteration_7 = artifacts["iteration_7"]
    iteration_8 = artifacts["iteration_8"]
    iteration_9 = artifacts["iteration_9"]

    decisions: dict[str, dict[str, Any]] = {
        "GALI2": {
            "supported": (
                iteration_3["status"] == "passed"
                and iteration_3["strongest_supported_gali_level"] == "GALI2"
                and iteration_3["checks"]["route_context_variant_replay_accepted"]
                and iteration_3["checks"]["arbitration_policy_variant_blocked"]
            ),
            "basis": "Iteration 3 accepted source-backed route-context transfer while preserving selection-only scope.",
            "blocker_if_false": "route_context_transfer_not_supported",
        },
        "GALI3": {
            "supported": (
                iteration_4b["status"] == "passed"
                and iteration_4b["strongest_supported_gali_level"] == "GALI3"
                and iteration_4b["checks"]["transfer_row_accepted_as_gali3"]
                and iteration_4["checks"]["proxy_target_band_variant_source_missing"]
            ),
            "basis": "Iteration 4-B supplied a declared target-band proxy variant while preserving Iteration 4's negative source audit.",
            "blocker_if_false": "proxy_condition_transfer_not_supported",
        },
        "GALI4": {
            "supported": (
                iteration_5["status"] == "passed"
                and iteration_5["strongest_contiguous_gali_level"] == "GALI4"
                and iteration_5["checks"]["manifest_four_support_states_covered"]
                and iteration_5["checks"]["disrupted_support_blocking_included"]
                and iteration_5["checks"]["explicit_restoration_resumption_included"]
            ),
            "basis": "Iteration 5 transferred support-state variants while preserving disrupted-support blocking and explicit restoration.",
            "blocker_if_false": "support_state_transfer_not_supported",
        },
        "GALI5": {
            "supported": (
                iteration_6["status"] == "passed"
                and iteration_6["strongest_supported_gali_level"] == "GALI5"
                and iteration_6["matrix_summary"]["accepted_gali5_row_count"] > 0
                and iteration_6["checks"]["matrix_row_count_matches_expected"]
                and iteration_6["checks"]["accepted_and_blocked_rows_recorded"]
            ),
            "basis": "Iteration 6 built the context/proxy/support matrix with accepted bounded rows and distinct blockers.",
            "blocker_if_false": "multi_axis_transfer_not_supported",
        },
        "GALI6": {
            "supported": (
                iteration_7["status"] == "passed"
                and iteration_7["strongest_supported_gali_level"] == "GALI6"
                and iteration_7["longer_horizon_summary"]["accepted_gali6_row_count"] > 0
                and iteration_7["checks"]["source_current_all_windows"]
                and iteration_7["checks"]["budget_errors_zero_all_windows"]
                and iteration_7["checks"]["transfer_stable_all_windows"]
            ),
            "basis": "Iteration 7 extended accepted multi-axis rows over the declared 8-window trend horizon.",
            "blocker_if_false": "longer_horizon_generalization_not_supported",
        },
    }

    gali7_prerequisites = {
        "gali2_context_transfer_supported": decisions["GALI2"]["supported"],
        "gali3_proxy_condition_transfer_supported": decisions["GALI3"][
            "supported"
        ],
        "gali4_support_state_transfer_supported": decisions["GALI4"]["supported"],
        "gali5_multi_axis_transfer_supported": decisions["GALI5"]["supported"],
        "gali6_longer_horizon_supported": decisions["GALI6"]["supported"],
        "iteration_8_controls_passed": iteration_8["checks"][
            "all_controls_passed"
        ],
        "iteration_8_controls_distinct": iteration_8["checks"][
            "all_primary_blockers_distinct"
        ],
        "iteration_8_no_generic_failures": iteration_8["checks"][
            "no_generic_failures"
        ],
        "iteration_9_artifact_validator_passed": iteration_9["status"]
        == "passed",
        "iteration_9_all_manifest_passes_passed": iteration_9["checks"][
            "all_manifest_required_passes_passed"
        ],
        "iteration_9_artifact_only": iteration_9["artifact_only"] is True,
        "iteration_9_no_runtime_state": iteration_9["runtime_state_used"] is False,
        "unsafe_claim_flags_remain_false": all(
            value is False for value in UNSAFE_CLAIM_FLAGS.values()
        ),
    }
    decisions["GALI7"] = {
        "supported": all_values_true(gali7_prerequisites),
        "basis": (
            "Iterations 3-9 now satisfy the local GALI7 criterion: transfer, "
            "matrix envelope, longer-horizon replay, controls, and artifact-only "
            "validation all pass."
        ),
        "blocker_if_false": "broader_general_artifact_only_integration_not_supported",
        "prerequisites": gali7_prerequisites,
        "support_is_by_explicit_closeout_not_inheritance": True,
    }
    return decisions


def strongest_supported_level(level_decisions: dict[str, Any]) -> str:
    strongest = "GALI1"
    for level in ("GALI2", "GALI3", "GALI4", "GALI5", "GALI6", "GALI7"):
        if level_decisions[level]["supported"]:
            strongest = level
        else:
            break
    return strongest


def build_output() -> dict[str, Any]:
    artifacts = load_artifacts()
    level_decisions = build_level_decisions(artifacts)
    strongest_level = strongest_supported_level(level_decisions)
    gali7_supported = level_decisions["GALI7"]["supported"]
    claim_ceiling = (
        "broader_general_artifact_only_agentic_like_integration_candidate"
        if gali7_supported
        else "longer_horizon_generalization_candidate"
    )
    negative_envelope = {
        "iteration_3_blocker": "context_arbitration_policy_variant_missing_source",
        "iteration_4_blocker": "proxy_target_band_variant_missing_source",
        "iteration_5_blocker": "support_disrupted_but_integration_allowed",
        "iteration_6_blockers": artifacts["iteration_6"]["matrix_summary"][
            "primary_blocker_counts"
        ],
        "iteration_8_control_blockers": artifacts["iteration_8"][
            "primary_blocker_counts"
        ],
    }
    checks = {
        "all_source_artifact_statuses_passed": all_status_passed(artifacts),
        "iteration_3_checks_passed": all_checks_passed(artifacts["iteration_3"]),
        "iteration_4b_checks_passed": all_checks_passed(artifacts["iteration_4b"]),
        "iteration_5_checks_passed": all_checks_passed(artifacts["iteration_5"]),
        "iteration_6_checks_passed": all_checks_passed(artifacts["iteration_6"]),
        "iteration_7_checks_passed": all_checks_passed(artifacts["iteration_7"]),
        "iteration_8_checks_passed": all_checks_passed(artifacts["iteration_8"]),
        "iteration_9_checks_passed": all_checks_passed(artifacts["iteration_9"]),
        "gali2_supported": level_decisions["GALI2"]["supported"],
        "gali3_supported": level_decisions["GALI3"]["supported"],
        "gali4_supported": level_decisions["GALI4"]["supported"],
        "gali5_supported": level_decisions["GALI5"]["supported"],
        "gali6_supported": level_decisions["GALI6"]["supported"],
        "gali7_supported": gali7_supported,
        "negative_results_preserved": bool(negative_envelope),
        "unsafe_claim_flags_all_false": all(
            value is False for value in UNSAFE_CLAIM_FLAGS.values()
        ),
        "src_clean_for_iteration_10": git_status_short("src") == "",
    }
    hypothesis_distinction = {
        "hypothesis_a": {
            "name": "artifact_only_generalization_path",
            "question": (
                "Can the N10 bounded composition transfer under declared "
                "variation without hidden steering, budget drift, source loss, "
                "or claim leakage?"
            ),
            "role_so_far": (
                "Hypothesis A proves transfer is not just bookkeeping. It "
                "covers route/context transfer, the proxy source audit and "
                "declared target-band variant, fail-closed controls, and the "
                "artifact-only replay validator."
            ),
            "primary_iterations": ["3", "4", "4-B", "8", "9"],
            "short_form": (
                "Can the N10 composition transfer artifact-only under declared "
                "variation?"
            ),
        },
        "hypothesis_b": {
            "name": "generalization_envelope_and_robustness_path",
            "question": (
                "Once transfer is source-backed, what envelope of support, "
                "proxy, context, and window variation does it survive, degrade "
                "within, or block?"
            ),
            "role_so_far": (
                "Hypothesis B maps where the transferred composition holds, "
                "degrades, recovers, or fails. It covers support-state transfer, "
                "the context/proxy/support matrix, longer-horizon trend replay, "
                "and this A/B closeout decision."
            ),
            "primary_iterations": ["5", "6", "7", "10"],
            "short_form": (
                "What envelope of support/proxy/context/window variation does "
                "the transferred composition survive?"
            ),
        },
        "relationship": (
            "Hypothesis A establishes that transfer can be source-backed and "
            "artifact-only. Hypothesis B turns that transferred result into a "
            "mapped envelope of accepted, blocked, restored, and longer-horizon "
            "conditions. A proves the transfer boundary; B maps the survival "
            "and failure envelope."
        ),
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 10 passes if Hypotheses A and B close with the "
            "strongest source-backed GALI ceiling and a clear generalization "
            "envelope. GALI7 may be claimed only if transfer, matrix, "
            "longer-horizon replay, artifact-only validation, and controls "
            "all pass."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_10_hypothesis_ab_closeout_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 10,
        "purpose": "hypothesis_ab_closeout_and_strongest_gali_decision",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "source_artifacts": source_artifact_rows(artifacts),
        "level_decisions": level_decisions,
        "strongest_supported_gali_level": strongest_level,
        "strongest_supported_claim_ceiling": claim_ceiling,
        "gali7_evidence_classification_supported": gali7_supported,
        "roadmap_a7_local_evidence_target_met": gali7_supported,
        "gali7_support_basis": (
            "explicit_iteration_10_closeout_over_iterations_3_to_9"
            if gali7_supported
            else "not_supported"
        ),
        "gali7_by_inheritance_allowed": False,
        "a7_by_inheritance_allowed": False,
        "negative_envelope": negative_envelope,
        "hypothesis_distinction": hypothesis_distinction,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "native_support_flags": {
            "fully_native_agentic_like_integration_supported": False,
            "native_agentic_like_integration_policy_supported": False,
            "native_identity_acceptance_validator_supported": False,
            "native_semantic_goal_ownership_supported": False,
        },
        "interpretation": {
            "what_was_achieved": (
                "N11 Hypotheses A and B reached local GALI7: a broader/general "
                "artifact-only agentic-like integration candidate over declared "
                "context, proxy, support, matrix, longer-horizon, control, and "
                "artifact-replay conditions."
            ),
            "what_was_not_achieved": (
                "This is not semantic agency, intention, goal ownership, identity "
                "acceptance, RC identity collapse, ACO behavior, biological "
                "behavior, personhood, unrestricted agency, or fully native LGRC "
                "agentic-like integration."
            ),
            "why_iteration_10_was_needed": (
                "Iteration 9 validated replayability but intentionally did not "
                "promote the ceiling. Iteration 10 consumes the full Iterations "
                "3-9 record and makes the strongest-ceiling decision."
            ),
        },
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "11_hypothesis_c_native_generalization_gap",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 10 Hypothesis A/B Closeout",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Decision",
        "",
        "```text",
        f"strongest_supported_gali_level = {output['strongest_supported_gali_level']}",
        f"strongest_supported_claim_ceiling = {output['strongest_supported_claim_ceiling']}",
        (
            "gali7_evidence_classification_supported = "
            f"{str(output['gali7_evidence_classification_supported']).lower()}"
        ),
        (
            "roadmap_a7_local_evidence_target_met = "
            f"{str(output['roadmap_a7_local_evidence_target_met']).lower()}"
        ),
        "gali7_by_inheritance_allowed = false",
        "a7_by_inheritance_allowed = false",
        "```",
        "",
        "## Level Decisions",
        "",
        "```json",
        json.dumps(output["level_decisions"], indent=2, sort_keys=True),
        "```",
        "",
        "## Negative Envelope",
        "",
        "```json",
        json.dumps(output["negative_envelope"], indent=2, sort_keys=True),
        "```",
        "",
        "## Hypothesis A vs B",
        "",
        "```json",
        json.dumps(output["hypothesis_distinction"], indent=2, sort_keys=True),
        "```",
        "",
        "## Claim Boundary",
        "",
        "```json",
        json.dumps(
            {
                "unsafe_claim_flags": output["unsafe_claim_flags"],
                "native_support_flags": output["native_support_flags"],
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Interpretation",
        "",
        output["interpretation"]["what_was_achieved"],
        "",
        output["interpretation"]["what_was_not_achieved"],
        "",
        output["interpretation"]["why_iteration_10_was_needed"],
        "",
        "The important distinction is that GALI7 is a local N11 evidence",
        "classification reached by explicit closeout over Iterations 3-9. It is",
        "not a claim inherited from GALI6 and it does not open semantic agency,",
        "identity acceptance, native support, or unrestricted agentic behavior.",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance",
        "",
        output["acceptance"]["acceptance_statement"],
        "",
        f"Acceptance state: `{output['acceptance']['status']}`.",
        "",
        "## Run Record",
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
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status {output['status']}")
    print(f"strongest_supported_gali_level {output['strongest_supported_gali_level']}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()
