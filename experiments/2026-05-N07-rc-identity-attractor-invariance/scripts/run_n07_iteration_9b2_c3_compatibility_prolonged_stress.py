"""Run N07 Iteration 9-B2 prolonged C3 compatibility stress.

Iteration 9-B was a one-window compatibility probe. This script asks the
follow-up question explicitly: if the observed support loss and wrong-basin
leakage recur without any recovery/re-separation mechanism, does the C3
compatibility gate still hold over a longer stress horizon?

The answer is recorded as a stress boundary, not as a native LGRC dynamic
simulation and not as an ID6 closeout.
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
OUTPUTS = N07 / "outputs"
REPORTS = N07 / "reports"
SCRIPTS = N07 / "scripts"

SOURCE_9B_OUTPUT = OUTPUTS / "n07_iteration_9b_c3_compatibility_interference_probe.json"
SOURCE_9B_REPORT = REPORTS / "n07_iteration_9b_c3_compatibility_interference_probe.md"
OUTPUT_PATH = OUTPUTS / "n07_iteration_9b2_c3_compatibility_prolonged_stress.json"
REPORT_PATH = REPORTS / "n07_iteration_9b2_c3_compatibility_prolonged_stress.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_9b2_c3_compatibility_prolonged_stress.py"
)

STRESS_WINDOW_COUNT = 12


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


def _metric(source: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    for row in source["compatibility_metric_rows"]:
        if row["metric_name"] == name:
            return row
    raise KeyError(name)


def _source_artifacts(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_9b_c3_compatibility_interference_probe",
            "path": _rel(SOURCE_9B_OUTPUT),
            "sha256": _file_sha256(SOURCE_9B_OUTPUT),
            "object_digest": _digest(source),
            "status": source.get("status"),
        },
        {
            "name": "n07_iteration_9b_c3_compatibility_interference_probe_report",
            "path": _rel(SOURCE_9B_REPORT),
            "sha256": _file_sha256(SOURCE_9B_REPORT),
        },
    ]


def _stress_model(source: Mapping[str, Any]) -> dict[str, Any]:
    a_per_window = float(_metric(source, "a_support_retention_near_b")["value"])
    b_per_window = float(_metric(source, "b_support_retention_near_a")["value"])
    wrong_per_window = float(_metric(source, "wrong_basin_leakage_score")["value"])
    ambiguous = float(_metric(source, "ambiguous_overlap_score")["value"])
    hidden = int(_metric(source, "hidden_support_rejection_rule")["value"])
    thresholds = {
        "support_retention_min": float(
            _metric(source, "a_support_retention_near_b")["threshold"]
        ),
        "wrong_basin_leakage_max": float(
            _metric(source, "wrong_basin_leakage_score")["threshold"]
        ),
        "destructive_interference_max": float(
            _metric(source, "destructive_interference_score")["threshold"]
        ),
        "ambiguous_overlap_max": float(_metric(source, "ambiguous_overlap_score")["threshold"]),
        "hidden_support_field_count": int(_metric(source, "hidden_support_rejection_rule")["threshold"]),
    }
    rows: list[dict[str, Any]] = []
    first_failure: dict[str, Any] | None = None
    for window in range(1, STRESS_WINDOW_COUNT + 1):
        a_cumulative_retention = a_per_window**window
        b_cumulative_retention = b_per_window**window
        cumulative_wrong = min(1.0, wrong_per_window * window)
        cumulative_destructive = max(
            1.0 - a_cumulative_retention,
            1.0 - b_cumulative_retention,
        )
        blockers: list[str] = []
        if a_cumulative_retention < thresholds["support_retention_min"]:
            blockers.append("support_drift_beyond_threshold")
        if b_cumulative_retention < thresholds["support_retention_min"]:
            blockers.append("support_drift_beyond_threshold")
        if cumulative_wrong > thresholds["wrong_basin_leakage_max"]:
            blockers.append("wrong_basin")
        if cumulative_destructive > thresholds["destructive_interference_max"]:
            blockers.append("destructive_interference")
        if ambiguous > thresholds["ambiguous_overlap_max"]:
            blockers.append("ambiguous_overlap")
        if hidden != thresholds["hidden_support_field_count"]:
            blockers.append("hidden_support_field")
        blockers = sorted(set(blockers))
        row = {
            "stress_window": window,
            "A_cumulative_support_retention": a_cumulative_retention,
            "B_cumulative_support_retention": b_cumulative_retention,
            "cumulative_wrong_basin_leakage_score": cumulative_wrong,
            "cumulative_destructive_interference_score": cumulative_destructive,
            "ambiguous_overlap_score": ambiguous,
            "hidden_support_field_count": hidden,
            "node_plus_packet_budget_error": 0.0,
            "window_passed": not blockers,
            "primary_blockers": blockers,
        }
        row["stress_window_digest"] = _digest(row)
        rows.append(row)
        if blockers and first_failure is None:
            first_failure = {
                "stress_window": window,
                "primary_blockers": blockers,
                "A_cumulative_support_retention": a_cumulative_retention,
                "B_cumulative_support_retention": b_cumulative_retention,
                "cumulative_wrong_basin_leakage_score": cumulative_wrong,
                "cumulative_destructive_interference_score": cumulative_destructive,
            }
    if first_failure is None:
        first_failure = {
            "stress_window": None,
            "primary_blockers": [],
        }
    model = {
        "stress_model_id": "n07_c3_repeated_window_no_recovery_accumulation_v1",
        "model_scope": "experiment_local_repeated_window_stress_not_native_lgrc_dynamics",
        "dynamic_lgrc_step_count": 0,
        "stress_window_count": STRESS_WINDOW_COUNT,
        "source_window": "n07_iteration_9b_one_window_compatibility_probe",
        "assumption": (
            "The 9-B per-window support loss and wrong-basin leakage recur "
            "without endogenous recovery, re-separation, or corrective "
            "lineage/compatibility policy."
        ),
        "thresholds": thresholds,
        "source_per_window_metrics": {
            "A_support_retention_near_B": a_per_window,
            "B_support_retention_near_A": b_per_window,
            "wrong_basin_leakage_score": wrong_per_window,
            "ambiguous_overlap_score": ambiguous,
            "hidden_support_field_count": hidden,
            "node_plus_packet_budget_error": 0.0,
        },
        "stress_windows": rows,
        "first_failure": first_failure,
        "stress_passed_all_windows": first_failure["stress_window"] is None,
    }
    model["stress_model_digest"] = _digest(model)
    return model


def _claim_flags(source: Mapping[str, Any]) -> dict[str, bool]:
    return {key: False for key in sorted(source["claim_flags"])}


def _interpretation(stress_model: Mapping[str, Any]) -> dict[str, Any]:
    failed = not stress_model["stress_passed_all_windows"]
    first_failure = stress_model["first_failure"]
    return {
        "summary": (
            "Iteration 9-B2 is a negative prolonged-stress result. The 9-B "
            "one-window compatibility pass does not justify multi-window "
            "C3 stability when the observed wrong-basin leakage and support "
            "loss are allowed to recur without a recovery mechanism."
        ),
        "what_it_shows": [
            (
                "The 4% one-window wrong-basin leakage is not negligible under "
                "a repeated-window no-recovery stress model."
            ),
            (
                "The first compatibility failure occurs before the 12-window "
                "stress horizon completes."
            ),
            (
                "9-B should be treated as one-window compatibility evidence, "
                "not as persistent A/B compatibility."
            ),
        ],
        "first_failure": first_failure,
        "identity_ladder_effect": {
            "current_ceiling": "ID5",
            "compatibility_stress_status": "blocked",
            "primary_blocker": (
                first_failure["primary_blockers"][0]
                if first_failure["primary_blockers"]
                else None
            ),
            "id6_claimed": False,
            "why_not_id6": (
                "C3/T7 compatibility does not survive this prolonged stress "
                "model, and Iteration 9-C artifact replay has not yet closed "
                "the evidence chain."
            ),
        },
        "needed_next": (
            "Either record 9-C as a closeout of one-window compatibility plus "
            "a prolonged-stress blocker, or design a recovery/re-separation "
            "probe that can keep wrong-basin leakage and support drift bounded "
            "across repeated windows."
        ),
        "claim_boundary": (
            "This stress result does not emit identity acceptance, RC identity "
            "collapse, semantic choice, agency, biological identity, "
            "personhood, movement, or unrestricted identity claims."
        ),
        "stress_failed": failed,
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    source = result["source_iteration_9b"]
    stress = result["stress_model"]
    first_failure = stress["first_failure"]
    claim_flags = result["claim_flags"]
    return {
        "source_9b_passed": source["status"] == "passed",
        "source_9b_was_one_window": source["interpretation"]["simulation_scope"][
            "probe_window_count"
        ]
        == 1,
        "source_9b_dynamic_lgrc_steps_zero": source["interpretation"][
            "simulation_scope"
        ]["dynamic_lgrc_step_count"]
        == 0,
        "stress_window_count_gt_one": stress["stress_window_count"] > 1,
        "stress_model_not_native_lgrc_dynamics": stress["dynamic_lgrc_step_count"] == 0,
        "first_failure_recorded": first_failure["stress_window"] is not None,
        "first_failure_is_wrong_basin": "wrong_basin"
        in first_failure["primary_blockers"],
        "cumulative_wrong_basin_exceeds_threshold_at_failure": first_failure[
            "cumulative_wrong_basin_leakage_score"
        ]
        > stress["thresholds"]["wrong_basin_leakage_max"],
        "budget_error_zero_all_windows": all(
            row["node_plus_packet_budget_error"] == 0.0
            for row in stress["stress_windows"]
        ),
        "stress_does_not_claim_id6": result["stress_candidate_row"]["id6_claimed"]
        is False,
        "stress_candidate_ceiling_id5": result["stress_candidate_row"][
            "derived_id_ceiling"
        ]
        == "ID5",
        "compatibility_stress_blocked": result["stress_candidate_row"][
            "compatibility_stress_status"
        ]
        == "blocked",
        "claim_flags_false": not any(claim_flags.values()),
        "source_artifact_hashes_present": all(
            "sha256" in row and row["sha256"] for row in result["source_artifacts"]
        ),
        "next_iteration_is_9c": result["next_iteration"]
        == "9C_c3_artifact_only_replay_and_compatibility_closeout",
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "stress_model_digest": result["stress_model"]["stress_model_digest"],
        "stress_candidate_row_digest": result["stress_candidate_row"][
            "stress_candidate_row_digest"
        ],
        "interpretation_digest": _digest(result["interpretation"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _environment() -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }


def _build_result() -> dict[str, Any]:
    source = _load_json(SOURCE_9B_OUTPUT)
    stress_model = _stress_model(source)
    claim_flags = _claim_flags(source)
    interpretation = _interpretation(stress_model)
    source_artifacts = _source_artifacts(source)
    candidate_row = {
        "row_id": "n07_i9b2_c3_compatibility_prolonged_stress_row_v1",
        "source_iteration": "9-B",
        "source_compatibility_record_digest": source["compatibility_record"][
            "compatibility_record_digest"
        ],
        "stress_model_digest": stress_model["stress_model_digest"],
        "id_level": "ID5",
        "derived_id_ceiling": "ID5",
        "compatibility_stress_status": (
            "pass" if stress_model["stress_passed_all_windows"] else "blocked"
        ),
        "primary_blocker": interpretation["identity_ladder_effect"][
            "primary_blocker"
        ],
        "claim_ceiling": "c3_one_window_compatibility_only_prolonged_stress_blocked",
        "id6_claimed": False,
        "id6_blocker": "c3_prolonged_compatibility_stress_failed",
        "runtime_family": "experiment_local",
        "implementation_surface": "experiment_local",
        "native_support_status": "not_native_lgrc_dynamic_simulation",
        "claim_flags": claim_flags,
        "visual_reference": None,
        "visual_is_evidence_source": False,
    }
    candidate_row["stress_candidate_row_digest"] = _digest(candidate_row)
    result: dict[str, Any] = {
        "schema": "n07_iteration_9b2_c3_compatibility_prolonged_stress_v1",
        "experiment": "N07",
        "iteration": "9-B2",
        "purpose": "prolonged_c3_compatibility_stress_no_id6_promotion",
        "command": COMMAND,
        "environment": _environment(),
        "source_iteration_9b": source,
        "source_artifacts": source_artifacts,
        "stress_model": stress_model,
        "interpretation": interpretation,
        "stress_candidate_row": candidate_row,
        "claim_flags": claim_flags,
        "acceptance": {
            "statement": (
                "Iteration 9-B2 passes if it explicitly tests prolonged "
                "compatibility under a serialized stress model, records "
                "whether the 9-B leakage/support-loss boundary remains stable, "
                "and does not promote ID6 or identity claims."
            ),
            "achieved": False,
        },
        "next_iteration": "9C_c3_artifact_only_replay_and_compatibility_closeout",
        "git": {
            "rev_parse_head": _git(["rev-parse", "HEAD"]),
            "status_short": _git(["status", "--short"]),
            "status_short_src": _git(["status", "--short", "src"]),
        },
    }
    result["checks"] = _checks(result)
    result["status"] = "passed" if all(result["checks"].values()) else "failed"
    result["checks"]["status_passed"] = result["status"] == "passed"
    result["acceptance"]["achieved"] = result["status"] == "passed"
    result["artifact_digests"] = _artifact_digests(result)
    return result


def _write_report(result: Mapping[str, Any]) -> None:
    stress = result["stress_model"]
    first = stress["first_failure"]
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    windows = "\n".join(
        "| {stress_window} | {A_cumulative_support_retention:.6f} | "
        "{B_cumulative_support_retention:.6f} | "
        "{cumulative_wrong_basin_leakage_score:.6f} | "
        "{cumulative_destructive_interference_score:.6f} | `{window_passed}` | "
        "`{primary_blockers}` |".format(
            **{**row, "primary_blockers": ",".join(row["primary_blockers"])}
        )
        for row in stress["stress_windows"]
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 9-B2 C3 Compatibility Prolonged Stress

Status: `{result['status']}`

{result['interpretation']['summary']}

This is not a native LGRC dynamic simulation. It is an experiment-local
repeated-window stress model over the source-backed 9-B metrics.

## Result

- stress windows: `{stress['stress_window_count']}`
- native LGRC dynamic steps: `{stress['dynamic_lgrc_step_count']}`
- stress passed all windows: `{stress['stress_passed_all_windows']}`
- first failure window: `{first['stress_window']}`
- first failure blockers: `{first['primary_blockers']}`
- derived ceiling: `{result['stress_candidate_row']['derived_id_ceiling']}`
- ID6 claimed: `{result['stress_candidate_row']['id6_claimed']}`

## Interpretation

What it shows:

{chr(10).join(f"- {item}" for item in result['interpretation']['what_it_shows'])}

Needed next:

{result['interpretation']['needed_next']}

Claim boundary:

{result['interpretation']['claim_boundary']}

## Stress Windows

| Window | A Retention | B Retention | Cumulative Wrong-Basin Leakage | Cumulative Destructive Score | Passed | Blockers |
|---:|---:|---:|---:|---:|---|---|
{windows}

## Checks

| Check | Passed |
|---|---|
{checks}

## Artifact Digests

```json
{json.dumps(result['artifact_digests'], indent=2, sort_keys=True)}
```

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
                "checks": len(result["checks"]),
                "first_failure_window": result["stress_model"]["first_failure"][
                    "stress_window"
                ],
                "primary_blockers": result["stress_model"]["first_failure"][
                    "primary_blockers"
                ],
            },
            sort_keys=True,
        )
    )
    print(_rel(OUTPUT_PATH))
    print(_rel(REPORT_PATH))


if __name__ == "__main__":
    main()
