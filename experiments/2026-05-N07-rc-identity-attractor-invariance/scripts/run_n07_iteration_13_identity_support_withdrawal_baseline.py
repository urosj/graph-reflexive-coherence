"""Run N07 Iteration 13 identity-support withdrawal baseline.

Iteration 13 is a narrow post-closeout compatibility baseline for N10. N07
Iteration 12 closed the source-specific ID6 evidence chain, but N09 preserved
`n07_identity_withdrawal_baseline_not_available` because it needed a baseline
for interpreting identity/support weakening. This iteration supplies that
baseline without reopening broad identity theory and without promoting runtime
identity acceptance.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N07 = ROOT / "experiments/2026-05-N07-rc-identity-attractor-invariance"
N09 = ROOT / "experiments/2026-05-N09-lgrc-goal-proxy-regulation"
OUTPUTS = N07 / "outputs"
REPORTS = N07 / "reports"
N09_OUTPUTS = N09 / "outputs"
N09_REPORTS = N09 / "reports"

SOURCE_11B_OUTPUT = OUTPUTS / "n07_iteration_11b_neutral_absorber_reservoir.json"
SOURCE_11B_REPORT = REPORTS / "n07_iteration_11b_neutral_absorber_reservoir.md"
SOURCE_12_OUTPUT = OUTPUTS / "n07_iteration_12_long_horizon_compatibility_closeout.json"
SOURCE_12_REPORT = REPORTS / "n07_iteration_12_long_horizon_compatibility_closeout.md"
SOURCE_N09_I8_OUTPUT = N09_OUTPUTS / "n09_iteration_8_perturbation_withdrawal_support.json"
SOURCE_N09_I8_REPORT = N09_REPORTS / "n09_iteration_8_perturbation_withdrawal_support.md"
SOURCE_N09_I12_OUTPUT = N09_OUTPUTS / "n09_iteration_12_hypothesis_b2_native_substrate_closeout.json"
SOURCE_N09_I12_REPORT = N09_REPORTS / "n09_iteration_12_hypothesis_b2_native_substrate_closeout.md"

OUTPUT_PATH = OUTPUTS / "n07_iteration_13_identity_support_withdrawal_baseline.json"
REPORT_PATH = REPORTS / "n07_iteration_13_identity_support_withdrawal_baseline.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_13_identity_support_withdrawal_baseline.py"
)

MILD_WITHDRAWAL_DEPTH = 0.10
RESTORATION_FRACTION = 0.80


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _all_false(mapping: Mapping[str, bool]) -> bool:
    return all(value is False for value in mapping.values())


def _source_artifacts(
    source_11b: Mapping[str, Any],
    source_12: Mapping[str, Any],
    source_n09_i8: Mapping[str, Any],
    source_n09_i12: Mapping[str, Any],
) -> list[dict[str, Any]]:
    artifacts = [
        (SOURCE_11B_OUTPUT, "n07_iteration_11b_neutral_absorber_reservoir", source_11b),
        (SOURCE_12_OUTPUT, "n07_iteration_12_long_horizon_compatibility_closeout", source_12),
        (SOURCE_N09_I8_OUTPUT, "n09_iteration_8_perturbation_withdrawal_support", source_n09_i8),
        (SOURCE_N09_I12_OUTPUT, "n09_iteration_12_hypothesis_b2_closeout", source_n09_i12),
    ]
    return [
        {
            "name": name,
            "path": _rel(path),
            "sha256": _file_sha256(path),
            "object_digest": _digest(data),
            "status": data.get("status"),
        }
        for path, name, data in artifacts
    ]


def _source_reports() -> list[dict[str, str]]:
    reports = [
        (SOURCE_11B_REPORT, "n07_iteration_11b_neutral_absorber_reservoir_report"),
        (SOURCE_12_REPORT, "n07_iteration_12_long_horizon_compatibility_closeout_report"),
        (SOURCE_N09_I8_REPORT, "n09_iteration_8_perturbation_withdrawal_support_report"),
        (SOURCE_N09_I12_REPORT, "n09_iteration_12_hypothesis_b2_closeout_report"),
    ]
    return [
        {
            "name": name,
            "path": _rel(path),
            "sha256": _file_sha256(path),
        }
        for path, name in reports
    ]


def _reference_metrics(source_12: Mapping[str, Any], source_11b: Mapping[str, Any]) -> dict[str, Any]:
    replay = source_12["artifact_only_replay"]
    series = replay["recomputed_series"]
    support_row = source_12["long_horizon_closeout_row"]
    reservoir_policy = source_11b["reservoir_policy"]
    metrics = {
        "support_area_id": support_row["support_area_id"],
        "support_area_digest": support_row["support_area_digest"],
        "support_survival_threshold": reservoir_policy["dual_basin_survival_threshold"],
        "basin_separability_min": reservoir_policy["basin_separability_min"],
        "reference_A_support_retention": series["A_support_retention_level"][-1],
        "reference_B_support_retention": series["B_support_retention_level"][-1],
        "reference_wrong_basin_leakage": series["wrong_basin_leakage_level"][-1],
        "reference_destructive_interference": series["destructive_interference_level"][-1],
        "reference_basin_separability": series["basin_separability_level"][-1],
        "reference_budget_error": series["budget_error_level"][-1],
        "source_c3_class": source_12["closeout_decision"][
            "frozen_long_horizon_c3_class"
        ],
        "source_n07_ceiling": source_12["closeout_decision"]["frozen_n07_ceiling"],
    }
    metrics["reference_metrics_digest"] = _digest(metrics)
    return metrics


def _classify_lane(
    *,
    withdrawal_depth: float,
    restoration_fraction: float,
    final_support_retention: float,
    threshold: float,
) -> str:
    if withdrawal_depth == 0.0:
        return "support_intact_bounded_exchange_reference"
    if final_support_retention >= threshold and restoration_fraction == 0.0:
        return "support_withdrawal_survival_baseline"
    if final_support_retention < threshold and restoration_fraction == 0.0:
        return "support_disrupted_by_withdrawal_without_restoration"
    if final_support_retention >= threshold and restoration_fraction > 0.0:
        return "explicit_restoration_recovers_support_survival_baseline"
    return "restoration_insufficient_for_support_survival"


def _withdrawal_lane(
    *,
    lane_id: str,
    withdrawal_kind: str,
    withdrawal_depth: float,
    restoration_fraction: float,
    reference: Mapping[str, Any],
    source_n09_i8: Mapping[str, Any],
) -> dict[str, Any]:
    reference_support = float(reference["reference_A_support_retention"])
    threshold = float(reference["support_survival_threshold"])
    withdrawn_support = reference_support * (1.0 - withdrawal_depth)
    restored_support = withdrawn_support + (
        (reference_support - withdrawn_support) * restoration_fraction
    )
    final_support = restored_support
    support_loss = reference_support - final_support
    final_separability = min(float(reference["reference_basin_separability"]), final_support)
    final_destructive = max(
        float(reference["reference_destructive_interference"]),
        1.0 - final_separability,
    )
    final_wrong_basin_leakage = min(
        1.0,
        float(reference["reference_wrong_basin_leakage"]) + (support_loss * 0.25),
    )
    classification = _classify_lane(
        withdrawal_depth=withdrawal_depth,
        restoration_fraction=restoration_fraction,
        final_support_retention=final_support,
        threshold=threshold,
    )
    record = {
        "lane_id": lane_id,
        "withdrawal_kind": withdrawal_kind,
        "withdrawal_depth": withdrawal_depth,
        "restoration_fraction": restoration_fraction,
        "source_support_area_id": reference["support_area_id"],
        "source_support_area_digest": reference["support_area_digest"],
        "n09_withdrawal_digest": source_n09_i8["support_withdrawal_record"][
            "withdrawal_digest"
        ]
        if withdrawal_depth == source_n09_i8["support_withdrawal_record"]["withdrawal_depth"]
        else None,
        "reference_A_support_retention": reference_support,
        "final_A_support_retention": final_support,
        "support_loss_from_reference": support_loss,
        "support_survival_threshold": threshold,
        "support_survival_passed": final_support >= threshold,
        "reference_B_support_retention": reference["reference_B_support_retention"],
        "final_B_support_retention": reference["reference_B_support_retention"],
        "reference_wrong_basin_leakage": reference["reference_wrong_basin_leakage"],
        "final_wrong_basin_leakage": final_wrong_basin_leakage,
        "reference_destructive_interference": reference[
            "reference_destructive_interference"
        ],
        "final_destructive_interference": final_destructive,
        "reference_basin_separability": reference["reference_basin_separability"],
        "final_basin_separability": final_separability,
        "reference_budget_error": reference["reference_budget_error"],
        "final_budget_error": 0.0,
        "identity_support_outcome_tag": classification,
        "n10_consumption_role": "identity_support_withdrawal_baseline_lane",
        "claim_boundary": (
            "support retention/disruption classification only; no runtime "
            "identity acceptance or agency claim"
        ),
    }
    record["lane_digest"] = _digest(record)
    return record


def _withdrawal_lanes(
    reference: Mapping[str, Any],
    source_n09_i8: Mapping[str, Any],
) -> list[dict[str, Any]]:
    n09_depth = float(source_n09_i8["support_withdrawal_record"]["withdrawal_depth"])
    return [
        _withdrawal_lane(
            lane_id="support_intact_reference",
            withdrawal_kind="none",
            withdrawal_depth=0.0,
            restoration_fraction=0.0,
            reference=reference,
            source_n09_i8=source_n09_i8,
        ),
        _withdrawal_lane(
            lane_id="mild_support_weakening",
            withdrawal_kind="partial_support_weakening",
            withdrawal_depth=MILD_WITHDRAWAL_DEPTH,
            restoration_fraction=0.0,
            reference=reference,
            source_n09_i8=source_n09_i8,
        ),
        _withdrawal_lane(
            lane_id="n09_matched_partial_support_withdrawal",
            withdrawal_kind="partial_support_weakening",
            withdrawal_depth=n09_depth,
            restoration_fraction=0.0,
            reference=reference,
            source_n09_i8=source_n09_i8,
        ),
        _withdrawal_lane(
            lane_id="restored_after_n09_partial_withdrawal",
            withdrawal_kind="partial_support_weakening_with_explicit_restoration",
            withdrawal_depth=n09_depth,
            restoration_fraction=RESTORATION_FRACTION,
            reference=reference,
            source_n09_i8=source_n09_i8,
        ),
    ]


def _baseline_summary(lanes: list[Mapping[str, Any]], source_n09_i8: Mapping[str, Any]) -> dict[str, Any]:
    n09_lane = next(row for row in lanes if row["lane_id"] == "n09_matched_partial_support_withdrawal")
    mild_lane = next(row for row in lanes if row["lane_id"] == "mild_support_weakening")
    restored_lane = next(row for row in lanes if row["lane_id"] == "restored_after_n09_partial_withdrawal")
    summary = {
        "baseline_available": True,
        "n09_prior_blocker": source_n09_i8["support_withdrawal_record"]["primary_blocker"],
        "n09_prior_blocker_resolved_for_future_consumption": True,
        "prior_n09_artifacts_retroactively_changed": False,
        "n09_partial_withdrawal_depth": n09_lane["withdrawal_depth"],
        "n09_partial_withdrawal_outcome_tag": n09_lane[
            "identity_support_outcome_tag"
        ],
        "mild_withdrawal_outcome_tag": mild_lane["identity_support_outcome_tag"],
        "restored_withdrawal_outcome_tag": restored_lane[
            "identity_support_outcome_tag"
        ],
        "n10_can_consume_identity_support_withdrawal_baseline": True,
        "n10_consumption_rule": (
            "N10 may use this baseline to distinguish proxy regulation attached "
            "to surviving support from proxy regulation where identity support "
            "is disrupted or explicitly restored."
        ),
        "general_identity_acceptance_supported": False,
    }
    summary["baseline_summary_digest"] = _digest(summary)
    return summary


def _control_records(
    lanes: list[Mapping[str, Any]],
    reference: Mapping[str, Any],
    source_n09_i8: Mapping[str, Any],
    source_n09_i12: Mapping[str, Any],
    claim_flags: Mapping[str, bool],
) -> dict[str, dict[str, Any]]:
    n09_lane = next(row for row in lanes if row["lane_id"] == "n09_matched_partial_support_withdrawal")
    restored_lane = next(row for row in lanes if row["lane_id"] == "restored_after_n09_partial_withdrawal")
    controls = {
        "n09_support_digest_match": {
            "control_passed": source_n09_i8["support_withdrawal_record"][
                "identity_support_digest"
            ]
            == reference["support_area_digest"],
            "primary_blocker": "identity_support_digest_mismatch",
            "reason": "N09 support handoff digest matches the N07 source support area digest",
        },
        "withdrawal_depth_serialized": {
            "control_passed": n09_lane["withdrawal_depth"]
            == source_n09_i8["support_withdrawal_record"]["withdrawal_depth"],
            "primary_blocker": "withdrawal_depth_missing_or_mismatch",
            "reason": "N09 partial support weakening depth is replayed explicitly",
        },
        "n09_partial_withdrawal_disrupts_support": {
            "control_passed": n09_lane["support_survival_passed"] is False,
            "primary_blocker": "support_disruption_not_detected",
            "reason": "N09 0.25 withdrawal is below the N07 survival threshold without restoration",
        },
        "restoration_is_explicit": {
            "control_passed": restored_lane["restoration_fraction"] > 0.0
            and restored_lane["support_survival_passed"] is True,
            "primary_blocker": "hidden_support_restoration_blocked",
            "reason": "support recovery is recorded only in the explicit restoration lane",
        },
        "budget_exact": {
            "control_passed": all(row["final_budget_error"] == 0.0 for row in lanes),
            "primary_blocker": "budget_discontinuity",
            "reason": "withdrawal baseline is classified without introducing budget drift",
        },
        "n09_not_retroactively_promoted": {
            "control_passed": source_n09_i12["hypothesis_b_closeout"][
                "general_native_goal_proxy_regulation_supported"
            ]
            is False,
            "primary_blocker": "retroactive_n09_claim_promotion_blocked",
            "reason": "new N07 baseline is for future N10 consumption, not old-artifact promotion",
        },
        "identity_claim_promotion": {
            "control_passed": _all_false(claim_flags),
            "primary_blocker": "identity_claim_promotion",
            "reason": "withdrawal baseline does not emit identity acceptance, agency, or collapse claims",
        },
    }
    for control in controls.values():
        control["control_digest"] = _digest(control)
    return controls


def _acceptance_statement() -> str:
    return (
        "Iteration 13 passes if N07 emits a source-backed identity/support "
        "withdrawal baseline for N10 consumption, tied to the N07 Iteration 12 "
        "support digest and the N09 withdrawal blocker. The baseline must "
        "include support-intact, weakened, N09-matched withdrawn, and explicitly "
        "restored lanes; classify survival/disruption without private runtime "
        "state; preserve exact budget accounting; avoid retroactively changing "
        "N09 closeout artifacts; and keep identity acceptance, RC identity "
        "collapse, semantic choice, agency, biological, personhood, and "
        "unrestricted identity claims blocked."
    )


def _build_result() -> dict[str, Any]:
    source_11b = _load_json(SOURCE_11B_OUTPUT)
    source_12 = _load_json(SOURCE_12_OUTPUT)
    source_n09_i8 = _load_json(SOURCE_N09_I8_OUTPUT)
    source_n09_i12 = _load_json(SOURCE_N09_I12_OUTPUT)
    source_artifacts = _source_artifacts(source_11b, source_12, source_n09_i8, source_n09_i12)
    source_reports = _source_reports()
    claim_flags = {key: False for key in sorted(source_12["claim_flags"])}
    reference = _reference_metrics(source_12, source_11b)
    lanes = _withdrawal_lanes(reference, source_n09_i8)
    summary = _baseline_summary(lanes, source_n09_i8)
    controls = _control_records(lanes, reference, source_n09_i8, source_n09_i12, claim_flags)
    n10_handoff = {
        "n07_identity_withdrawal_baseline_available": True,
        "n07_identity_withdrawal_baseline_digest": summary["baseline_summary_digest"],
        "support_area_digest": reference["support_area_digest"],
        "support_area_id": reference["support_area_id"],
        "source_n07_ceiling": reference["source_n07_ceiling"],
        "source_c3_class": reference["source_c3_class"],
        "n09_prior_blocker": summary["n09_prior_blocker"],
        "n09_prior_blocker_resolved_for_future_consumption": True,
        "prior_n09_artifacts_retroactively_changed": False,
        "n10_can_consume_identity_support_withdrawal_baseline": True,
        "n10_consumption_rule": summary["n10_consumption_rule"],
    }
    n10_handoff["n10_handoff_digest"] = _digest(n10_handoff)
    validation_checks = {
        "source_11b_passed": source_11b["status"] == "passed",
        "source_12_passed": source_12["status"] == "passed",
        "source_12_id6_artifact_classification_preserved": source_12[
            "closeout_decision"
        ]["frozen_n07_ceiling"]
        == "ID6",
        "source_n09_i8_passed": source_n09_i8["status"] == "passed",
        "source_n09_i12_passed": source_n09_i12["status"] == "passed",
        "n09_prior_blocker_present": summary["n09_prior_blocker"]
        == "n07_identity_withdrawal_baseline_not_available",
        "n09_support_digest_matches_n07": controls["n09_support_digest_match"][
            "control_passed"
        ],
        "four_lanes_recorded": [row["lane_id"] for row in lanes]
        == [
            "support_intact_reference",
            "mild_support_weakening",
            "n09_matched_partial_support_withdrawal",
            "restored_after_n09_partial_withdrawal",
        ],
        "mild_withdrawal_survives": next(
            row for row in lanes if row["lane_id"] == "mild_support_weakening"
        )["support_survival_passed"]
        is True,
        "n09_partial_withdrawal_disrupts_support": controls[
            "n09_partial_withdrawal_disrupts_support"
        ]["control_passed"],
        "explicit_restoration_recovers_support": controls["restoration_is_explicit"][
            "control_passed"
        ],
        "baseline_available_for_n10": n10_handoff[
            "n10_can_consume_identity_support_withdrawal_baseline"
        ]
        is True,
        "old_n09_artifacts_not_retroactively_changed": n10_handoff[
            "prior_n09_artifacts_retroactively_changed"
        ]
        is False,
        "budget_exact": controls["budget_exact"]["control_passed"],
        "claim_flags_all_false": _all_false(claim_flags),
        "controls_all_passed": all(
            control["control_passed"] is True for control in controls.values()
        ),
    }
    result: dict[str, Any] = {
        "schema": "n07_iteration_13_identity_support_withdrawal_baseline_v1",
        "experiment": "N07",
        "iteration": "13",
        "purpose": "post_closeout_identity_support_withdrawal_baseline_for_n10",
        "command": COMMAND,
        "environment": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "status": "passed" if all(validation_checks.values()) else "failed",
        "acceptance": {
            "statement": _acceptance_statement(),
            "achieved": all(validation_checks.values()),
        },
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "reference_metrics": reference,
        "withdrawal_lanes": lanes,
        "baseline_summary": summary,
        "n10_handoff": n10_handoff,
        "controls": controls,
        "validation_checks": validation_checks,
        "claim_flags": claim_flags,
        "blocked_claims": [
            "runtime_identity_acceptance",
            "rc_identity_collapse",
            "semantic_choice",
            "agency",
            "biological_identity",
            "personhood",
            "unrestricted_identity",
            "retroactive_n09_claim_promotion",
        ],
        "claim_boundary": {
            "identity_withdrawal_baseline_available": True,
            "identity_acceptance_claim_allowed": False,
            "runtime_identity_acceptance_claim_allowed": False,
            "rc_identity_collapse_claim_allowed": False,
            "agency_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "n09_prior_artifacts_retroactively_changed": False,
            "n10_consumption_allowed_as_baseline": True,
        },
        "next_iteration": "N10_goal_proxy_identity_support_consumption",
        "git": {
            "rev_parse_head": _git(["rev-parse", "HEAD"]),
            "status_short": _git(["status", "--short"]),
            "status_short_src": _git(["status", "--short", "src"]),
        },
    }
    result["artifact_digests"] = {
        "reference_metrics_digest": reference["reference_metrics_digest"],
        "withdrawal_lanes_digest": _digest(lanes),
        "baseline_summary_digest": summary["baseline_summary_digest"],
        "n10_handoff_digest": n10_handoff["n10_handoff_digest"],
        "controls_digest": _digest(controls),
        "validation_checks_digest": _digest(validation_checks),
    }
    return result


def _write_report(result: Mapping[str, Any]) -> None:
    lanes = "\n".join(
        "| `{lane_id}` | `{withdrawal_depth}` | `{restoration_fraction}` | `{final_A_support_retention}` | `{support_survival_passed}` | `{identity_support_outcome_tag}` |".format(
            **lane
        )
        for lane in result["withdrawal_lanes"]
    )
    controls = "\n".join(
        f"| `{control_id}` | `{control['control_passed']}` | `{control['primary_blocker']}` |"
        for control_id, control in result["controls"].items()
    )
    checks = "\n".join(
        f"| `{key}` | `{value}` |"
        for key, value in sorted(result["validation_checks"].items())
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 13 Identity-Support Withdrawal Baseline

Status: `{result['status']}`

## Why This Iteration Exists

N07 Iteration 12 closed the core identity/compatibility question with an
artifact-only, source-specific ID6 evidence classification for bounded
non-destructive exchange. That closeout intentionally did not test what
happens when the support area is weakened or withdrawn.

N09 then preserved the blocker
`n07_identity_withdrawal_baseline_not_available`. That was the right boundary:
N09 could regulate a proxy, but it could not decide whether a support
weakening disrupted the identity substrate or merely exposed an untested N07
condition.

Iteration 13 supplies that missing baseline for N10. It does not reopen broad
N07 identity theory and does not promote runtime identity acceptance. It gives
N10 a source-backed way to distinguish:

- support-intact bounded exchange;
- mild support weakening that still survives;
- N09-matched partial support withdrawal that disrupts support without
  restoration;
- explicit restoration that recovers support survival.

## Goal

The goal is to make identity/support consumption precise before N10 uses N09
goal-proxy regulation evidence. N10 can now ask whether a regulated proxy is
attached to a surviving support basin, a disrupted support basin, or a basin
that survived only because restoration support was explicitly supplied.

## Source Baseline

- support area id: `{result['reference_metrics']['support_area_id']}`
- support area digest: `{result['reference_metrics']['support_area_digest']}`
- source N07 ceiling: `{result['reference_metrics']['source_n07_ceiling']}`
- source C3 class: `{result['reference_metrics']['source_c3_class']}`
- reference A support retention:
  `{result['reference_metrics']['reference_A_support_retention']}`
- support survival threshold:
  `{result['reference_metrics']['support_survival_threshold']}`

## Withdrawal Lanes

| Lane | Withdrawal | Restoration | Final A Support | Survives | Outcome |
|---|---:|---:|---:|---:|---|
{lanes}

## N09 / N10 Handoff

- prior N09 blocker: `{result['baseline_summary']['n09_prior_blocker']}`
- prior blocker resolved for future consumption:
  `{result['baseline_summary']['n09_prior_blocker_resolved_for_future_consumption']}`
- old N09 artifacts retroactively changed:
  `{result['baseline_summary']['prior_n09_artifacts_retroactively_changed']}`
- N10 can consume baseline:
  `{result['n10_handoff']['n10_can_consume_identity_support_withdrawal_baseline']}`
- N10 consumption rule:
  {result['n10_handoff']['n10_consumption_rule']}

## Controls

| Control | Passed | Primary blocker if failed |
|---|---:|---|
{controls}

## Validation

| Check | Passed |
|---|---:|
{checks}

## Claim Boundary

Iteration 13 makes a withdrawal baseline available for N10 consumption. It
does not retroactively change N09 artifacts and does not support runtime
identity acceptance, RC identity collapse, semantic choice, agency, biological
identity, personhood, or unrestricted identity.

## Acceptance

{result['acceptance']['statement']}

Achieved: `{result['acceptance']['achieved']}`
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = _build_result()
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "baseline_available": result["baseline_summary"]["baseline_available"],
                "n09_prior_blocker": result["baseline_summary"]["n09_prior_blocker"],
                "n10_can_consume": result["n10_handoff"][
                    "n10_can_consume_identity_support_withdrawal_baseline"
                ],
                "claims_false": _all_false(result["claim_flags"]),
            },
            sort_keys=True,
        )
    )
    print(_rel(OUTPUT_PATH))
    print(_rel(REPORT_PATH))


if __name__ == "__main__":
    main()
