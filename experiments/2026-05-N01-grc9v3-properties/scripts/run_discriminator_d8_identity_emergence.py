"""D8: identity-emergence discriminator over Experiment D refinement windows."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
from typing import Any

from discriminator_harness import EVIDENCE_LABELS, manifest_schema
from grc9v3_fixture_harness import ARTIFACT_SCHEMA_VERSION, LANE_ID


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DISCRIMINATOR_ID = "d8_identity_emergence"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_discriminator_d8_identity_emergence.py"
)

INPUT_PATHS = {
    "harness_schema": (
        EXPERIMENT_ROOT / "outputs" / "discriminator_harness_schema.json"
    ),
    "d_conditions": (
        EXPERIMENT_ROOT / "outputs" / "experiment_d_refinement_identity_conditions.csv"
    ),
    "d_persistence": (
        EXPERIMENT_ROOT / "outputs" / "experiment_d_refinement_identity_persistence.csv"
    ),
    "d_thresholds": (
        EXPERIMENT_ROOT / "outputs" / "experiment_d_refinement_identity_thresholds.csv"
    ),
    "d_summary": (
        EXPERIMENT_ROOT / "outputs" / "experiment_d_refinement_identity_summary.json"
    ),
}

CONFIGURED_WINDOW_STEPS = 3
CONFIGURED_MIN_BASIN_MASS = 1.0


def _git_value(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
            cwd=EXPERIMENT_ROOT.parents[1],
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _truth(value: str) -> bool:
    return value.strip().lower() == "true"


def _float(value: str, default: float = 0.0) -> float:
    if value == "":
        return default
    return float(value)


def _int(value: str, default: int = 0) -> int:
    if value == "":
        return default
    return int(value)


def _split_ids(value: str) -> list[str]:
    return [part for part in value.split() if part]


def _key(row: dict[str, str]) -> tuple[str, str]:
    return (row["condition_id"], row["transform_id"])


def _child_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (row["condition_id"], row["transform_id"], row["child_node_id"])


def _threshold_key(row: dict[str, str]) -> tuple[str, str, str, int, float]:
    return (
        row["condition_id"],
        row["transform_id"],
        row["child_node_id"],
        _int(row["window_steps"]),
        _float(row["min_basin_mass"]),
    )


def _index_persistence(
    persistence_rows: list[dict[str, str]],
) -> dict[tuple[str, str, str], list[dict[str, str]]]:
    indexed: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in persistence_rows:
        indexed.setdefault(_child_key(row), []).append(row)
    for rows in indexed.values():
        rows.sort(key=lambda item: _int(item["window_index"]))
    return indexed


def _configured_threshold_pass(
    thresholds: dict[tuple[str, str, str, int, float], dict[str, str]],
    condition_id: str,
    transform_id: str,
    child_node_id: str,
) -> bool:
    row = thresholds.get(
        (
            condition_id,
            transform_id,
            child_node_id,
            CONFIGURED_WINDOW_STEPS,
            CONFIGURED_MIN_BASIN_MASS,
        )
    )
    return bool(row and _truth(row["persistence_pass"]))


def _lineage_values(rows: list[dict[str, str]], field: str) -> str:
    values = sorted({row[field] for row in rows if row.get(field, "")})
    return " ".join(values)


def _event_outcome(
    *,
    has_refinement: bool,
    persistence_pass: bool,
    any_present: bool,
    all_sink: bool,
    budget_preserved: bool,
) -> str:
    if not has_refinement:
        return "blocked"
    if persistence_pass and all_sink and budget_preserved:
        return "persistent_child_identity"
    if any_present:
        return "transient_child_candidate"
    return "mechanical_refinement_only"


def identity_window_rows(
    conditions: list[dict[str, str]],
    persistence_rows: list[dict[str, str]],
    threshold_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    persistence = _index_persistence(persistence_rows)
    thresholds = {_threshold_key(row): row for row in threshold_rows}
    rows: list[dict[str, Any]] = []
    for condition in conditions:
        if _int(condition["refinement_event_count"]) == 0:
            continue
        child_ids = _split_ids(condition["stabilized_child_node_ids"])
        for child_node_id in child_ids:
            child_rows = [
                row
                for row in persistence.get(
                    (
                        condition["condition_id"],
                        condition["transform_id"],
                        child_node_id,
                    ),
                    [],
                )
                if _int(row["window_index"]) <= CONFIGURED_WINDOW_STEPS
            ]
            present = [_truth(row["child_present"]) for row in child_rows]
            sinks = [_truth(row["child_is_sink"]) for row in child_rows]
            masses = [_float(row["child_basin_mass"]) for row in child_rows]
            persistence_pass = _configured_threshold_pass(
                thresholds,
                condition["condition_id"],
                condition["transform_id"],
                child_node_id,
            )
            has_refinement = _int(condition["refinement_event_count"]) > 0
            budget_preserved = _truth(condition["budget_preserved"])
            all_present = bool(present) and all(present)
            any_present = any(present)
            all_sink = bool(sinks) and all(sinks)
            accepted = (
                has_refinement
                and all_present
                and all_sink
                and persistence_pass
                and budget_preserved
            )
            rows.append(
                {
                    "discriminator": DISCRIMINATOR_ID,
                    "schema_version": ARTIFACT_SCHEMA_VERSION,
                    "lane_id": LANE_ID,
                    "source_experiment": condition["experiment"],
                    "condition_id": condition["condition_id"],
                    "condition_class": condition["condition_class"],
                    "transform_id": condition["transform_id"],
                    "seed": condition["seed"],
                    "event_kinds": condition["event_kinds"],
                    "refinement_event_count": condition["refinement_event_count"],
                    "completed_event_count": condition["completed_event_count"],
                    "module_node_ids": condition["module_node_ids"],
                    "child_node_id": child_node_id,
                    "window_steps": CONFIGURED_WINDOW_STEPS,
                    "min_basin_mass_threshold": CONFIGURED_MIN_BASIN_MASS,
                    "observed_window_rows": len(child_rows),
                    "child_present_all_window": all_present,
                    "child_sink_all_window": all_sink,
                    "min_child_basin_mass_observed": min(masses) if masses else 0.0,
                    "max_child_basin_mass_observed": max(masses) if masses else 0.0,
                    "child_parent_ids": _lineage_values(child_rows, "child_parent_id"),
                    "child_depths": _lineage_values(child_rows, "child_depth"),
                    "persistence_pass_configured": persistence_pass,
                    "event_outcome_class": _event_outcome(
                        has_refinement=has_refinement,
                        persistence_pass=persistence_pass,
                        any_present=any_present,
                        all_sink=all_sink,
                        budget_preserved=budget_preserved,
                    ),
                    "accepted_identity_emergence": accepted,
                    "multi_child_count_for_event": condition["persistent_child_count"],
                    "multi_child_fission_flag": (
                        accepted and _int(condition["persistent_child_count"]) > 1
                    ),
                    "mechanical_refinement_claim": (
                        condition["mechanical_refinement_claim"]
                    ),
                    "mechanical_refinement_alone_identity_claim": False,
                    "identity_claim_level": (
                        "configured_window_persistent_child_identity"
                        if accepted
                        else "no_accepted_identity"
                    ),
                    "budget_before": condition["budget_before"],
                    "budget_after": condition["budget_after"],
                    "budget_error": condition["budget_error"],
                    "budget_tolerance": condition["budget_tolerance"],
                    "budget_preserved": budget_preserved,
                    "evidence_label": "partial",
                    "artifact_sources": (
                        "Experiment D expansion event rows; runtime-state "
                        "post-event sink/basin persistence rows"
                    ),
                    "notes": (
                        "Accepted only because persistent sink/basin support, "
                        "lineage, and budget evidence are present over the "
                        "configured runtime-state window."
                        if accepted
                        else "Mechanical refinement is not identity fission."
                    ),
                }
            )
    return rows


def negative_control_rows(
    conditions: list[dict[str, str]],
    threshold_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for condition in conditions:
        if _int(condition["refinement_event_count"]) != 0:
            continue
        rows.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "control_id": "no_refinement_no_identity",
                "condition_id": condition["condition_id"],
                "condition_class": condition["condition_class"],
                "transform_id": condition["transform_id"],
                "seed": condition["seed"],
                "refinement_event_count": condition["refinement_event_count"],
                "completed_event_count": condition["completed_event_count"],
                "child_node_id": "",
                "window_steps": CONFIGURED_WINDOW_STEPS,
                "min_basin_mass": CONFIGURED_MIN_BASIN_MASS,
                "persistence_pass": False,
                "identity_accepted": False,
                "event_outcome_class": "blocked",
                "evidence_label": "direct",
                "notes": (
                    "No refinement event and no persistent child sink/basin "
                    "support; identity emergence is rejected."
                ),
            }
        )
    for row in threshold_rows:
        if _truth(row["persistence_pass"]):
            continue
        rows.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "control_id": "threshold_sensitivity_rejects_child",
                "condition_id": row["condition_id"],
                "condition_class": row["condition_class"],
                "transform_id": row["transform_id"],
                "seed": row["seed"],
                "refinement_event_count": "1",
                "completed_event_count": "1",
                "child_node_id": row["child_node_id"],
                "window_steps": row["window_steps"],
                "min_basin_mass": row["min_basin_mass"],
                "persistence_pass": False,
                "identity_accepted": False,
                "event_outcome_class": "transient_child_candidate",
                "evidence_label": "partial",
                "notes": (
                    "Configured window may pass at lower threshold, but this "
                    "strict sensitivity point rejects the child identity claim."
                ),
            }
        )
    return rows


def blocked_observations() -> list[dict[str, str]]:
    return [
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "mechanical-refinement-only positive control",
            "status": "inconclusive",
            "artifact_source": "Experiment D clean refinement fixtures",
            "reconstruction_attempt": (
                "Searched completed Experiment D conditions for refinement "
                "events without persistent child sink/basin rows."
            ),
            "notes": (
                "Current clean refinement rows all have configured-window "
                "child persistence; no mechanical-only positive refinement "
                "event is available."
            ),
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "checkpoint-window identity persistence",
            "status": "inconclusive",
            "artifact_source": "Experiment D runtime-state persistence rows",
            "reconstruction_attempt": (
                "Used runtime-state post-event windows; checked existing "
                "blocked observations from Experiment D."
            ),
            "notes": (
                "D8 confirms runtime-state configured-window persistence, "
                "not persisted checkpoint observer-window identity."
            ),
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "collapse/reabsorption outcome",
            "status": "inconclusive",
            "artifact_source": "Experiment D clean refinement fixtures",
            "reconstruction_attempt": (
                "Classified available post-window child sink/basin rows."
            ),
            "notes": (
                "No collapse or reabsorption event is present in the completed "
                "clean fixtures."
            ),
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "landscape-general identity emergence",
            "status": "inconclusive",
            "artifact_source": "Experiment D raw central-node fixtures",
            "reconstruction_attempt": (
                "Classified deterministic clean fixture windows only."
            ),
            "notes": (
                "D8 does not run a landscape/seed robustness suite; identity "
                "emergence remains clean-fixture and thresholded."
            ),
        },
    ]


def summary_payload(
    windows: list[dict[str, Any]],
    negatives: list[dict[str, Any]],
    thresholds: list[dict[str, str]],
    d_summary: dict[str, Any],
) -> dict[str, Any]:
    accepted = [row for row in windows if row["accepted_identity_emergence"]]
    accepted_events = {
        (row["condition_id"], row["transform_id"]) for row in accepted
    }
    all_events = {
        (row["condition_id"], row["transform_id"]) for row in windows
    }
    strict_failures = [
        row
        for row in thresholds
        if not _truth(row["persistence_pass"])
        and _float(row["min_basin_mass"]) > CONFIGURED_MIN_BASIN_MASS
    ]
    outcome_counts: dict[str, int] = {}
    for row in windows:
        outcome = row["event_outcome_class"]
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
    negative_outcome_counts: dict[str, int] = {}
    for row in negatives:
        outcome = row["event_outcome_class"]
        negative_outcome_counts[outcome] = negative_outcome_counts.get(outcome, 0) + 1
    return {
        "discriminator_id": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "classification": (
            "configured_window_persistent_child_identity_supported_with_boundaries"
        ),
        "source_experiment": "experiment_d_refinement_identity",
        "source_identity_support_scope": d_summary["identity_support_scope"],
        "configured_window_steps": CONFIGURED_WINDOW_STEPS,
        "configured_min_basin_mass": CONFIGURED_MIN_BASIN_MASS,
        "accepted_identity_window_rows": len(accepted),
        "accepted_identity_event_count": len(accepted_events),
        "refinement_event_count_classified": len(all_events),
        "accepted_identity_requires_persistent_sink_basin": True,
        "mechanical_refinement_alone_identity_claim": False,
        "multi_child_persistence_events": len(
            {
                (row["condition_id"], row["transform_id"])
                for row in accepted
                if row["multi_child_fission_flag"]
            }
        ),
        "multi_child_fission_scope": (
            "configured-window multi-child basin persistence only; not "
            "landscape-general identity fission"
        ),
        "accepted_budget_audit_pass": all(
            bool(row["budget_preserved"])
            and _float(str(row["budget_error"])) <= _float(str(row["budget_tolerance"]))
            for row in accepted
        ),
        "negative_control_rows": len(negatives),
        "no_refinement_negative_controls": sum(
            row["control_id"] == "no_refinement_no_identity" for row in negatives
        ),
        "strict_threshold_failure_rows": len(strict_failures),
        "threshold_sensitivity_recorded": True,
        "outcome_counts": outcome_counts,
        "negative_outcome_counts": negative_outcome_counts,
        "checkpoint_window_identity_status": "inconclusive",
        "collapse_reabsorption_status": "inconclusive",
        "landscape_general_identity_status": "inconclusive",
        "evidence_label": "partial",
        "boundary": (
            "D8 accepts configured-window child identity only when "
            "mechanical refinement, persistent post-event sink/basin support, "
            "lineage, and budget evidence are all present. It does not infer "
            "identity fission from expansion alone."
        ),
    }


def _write_blocked_report(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# D8 Blocked Observations",
        "",
        "| Observation | Status | Artifact Source | Reconstruction Attempt | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['observation']} | "
            f"{row['status']} | "
            f"{row['artifact_source']} | "
            f"{row['reconstruction_attempt']} | "
            f"{row['notes']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_report(
    path: Path,
    summary: dict[str, Any],
    windows: list[dict[str, Any]],
    negatives: list[dict[str, Any]],
) -> None:
    sample_rows = windows[:6]
    lines = [
        "# D8 Identity-Emergence Discriminator Report",
        "",
        "Status: complete.",
        "",
        "Classification: "
        "`configured_window_persistent_child_identity_supported_with_boundaries`.",
        "",
        "## Scope",
        "",
        "D8 tests the identity guardrail directly: mechanical refinement is",
        "classified separately from candidate or accepted identity emergence.",
        "Accepted identity requires post-event child sink/basin persistence,",
        "lineage, and budget evidence over the configured runtime-state window.",
        "",
        "## Acceptance Criteria",
        "",
        f"- persistence window steps: `{summary['configured_window_steps']}`",
        f"- minimum basin mass: `{summary['configured_min_basin_mass']}`",
        "- required evidence: refinement event, child present across the window,",
        "  child remains a sink across the window, lineage parent/depth rows, and",
        "  unit budget preservation within tolerance",
        "- mechanical expansion alone is not an identity-emergence claim",
        "",
        "## Outcome Counts",
        "",
        f"- accepted identity window rows: `{summary['accepted_identity_window_rows']}`",
        f"- accepted identity events: `{summary['accepted_identity_event_count']}`",
        f"- classified refinement events: `{summary['refinement_event_count_classified']}`",
        f"- multi-child persistence events: `{summary['multi_child_persistence_events']}`",
        f"- accepted budget audit pass: `{summary['accepted_budget_audit_pass']}`",
        f"- strict threshold failure rows: `{summary['strict_threshold_failure_rows']}`",
        "",
        "## Sample Accepted Windows",
        "",
        "| Condition | Transform | Child | Min Mass | Outcome | Budget Error |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in sample_rows:
        lines.append(
            "| "
            f"{row['condition_id']} | "
            f"{row['transform_id']} | "
            f"{row['child_node_id']} | "
            f"{row['min_child_basin_mass_observed']} | "
            f"{row['event_outcome_class']} | "
            f"{row['budget_error']} |"
        )
    lines.extend(
        [
            "",
            "## Negative Controls",
            "",
            "| Control | Count | Interpretation |",
            "| --- | ---: | --- |",
            (
                "| no_refinement_no_identity | "
                f"{summary['no_refinement_negative_controls']} | "
                "No accepted identity without refinement or persistent "
                "sink/basin support. |"
            ),
            (
                "| threshold_sensitivity_rejects_child | "
                f"{summary['strict_threshold_failure_rows']} | "
                "Stricter basin-mass thresholds reject some child claims, so "
                "identity support is explicitly thresholded. |"
            ),
            "",
            "## Outcome Classes",
            "",
            "D8 output rows use the configured outcome vocabulary: blocked,",
            "mechanical refinement only, transient child candidate, persistent",
            "child identity, multi-child fission flag, and collapse/reabsorption",
            "status. Available clean-fixture events classify as persistent child",
            "identity under the configured runtime-state window; collapse or",
            "reabsorption is inconclusive because no such event is present.",
            "",
            "## Interpretation",
            "",
            "D8 supports configured-window child-basin identity persistence in",
            "the clean Experiment D refinement fixtures. The accepted claims are",
            "thresholded and artifact-bound: they require persistent sink/basin",
            "rows and budget evidence. The result does not claim that expansion",
            "alone is identity fission, and it does not establish checkpoint-",
            "window or landscape-general identity behavior.",
            "",
            "## Boundaries",
            "",
            "- checkpoint-window identity persistence remains inconclusive;",
            "- no mechanical-refinement-only positive control is available in",
            "  the completed clean fixture set;",
            "- collapse/reabsorption is not observed in the current artifacts;",
            "- landscape-general identity emergence remains inconclusive.",
            "",
            "## Manifest Fields",
            "",
            f"- required manifest fields: `{', '.join(manifest_schema())}`",
            f"- evidence labels: `{', '.join(EVIDENCE_LABELS)}`",
            f"- summary boundary: {summary['boundary']}",
            f"- negative control rows written: `{len(negatives)}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs() -> dict[str, Path]:
    conditions = _read_csv(INPUT_PATHS["d_conditions"])
    persistence = _read_csv(INPUT_PATHS["d_persistence"])
    thresholds = _read_csv(INPUT_PATHS["d_thresholds"])
    d_summary = _read_json(INPUT_PATHS["d_summary"])
    windows = identity_window_rows(conditions, persistence, thresholds)
    negatives = negative_control_rows(conditions, thresholds)
    blocked = blocked_observations()
    summary = summary_payload(windows, negatives, thresholds, d_summary)
    outputs = {
        "windows": (
            EXPERIMENT_ROOT / "outputs" / "d8_identity_emergence_windows.csv"
        ),
        "negatives": EXPERIMENT_ROOT / "outputs" / "d8_negative_controls.csv",
        "summary": (
            EXPERIMENT_ROOT / "outputs" / "d8_identity_emergence_summary.json"
        ),
        "manifest": (
            EXPERIMENT_ROOT / "outputs" / "d8_identity_emergence_manifest.json"
        ),
        "report": (
            EXPERIMENT_ROOT / "reports" / "d8_identity_emergence_report.md"
        ),
        "blocked": EXPERIMENT_ROOT / "reports" / "d8_blocked_observations.md",
    }
    _write_csv(outputs["windows"], windows)
    _write_csv(outputs["negatives"], negatives)
    _write_json(outputs["summary"], summary)
    _write_blocked_report(outputs["blocked"], blocked)
    _write_report(outputs["report"], summary, windows, negatives)
    manifest = {
        "discriminator_id": DISCRIMINATOR_ID,
        "iteration": "9",
        "script_path": SCRIPT_PATH,
        "command": (
            "python experiments/2026-05-N01-grc9v3-properties/scripts/"
            "run_discriminator_d8_identity_emergence.py --write-defaults"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_status_short": _git_value(["status", "--short"]),
        "lane_id": LANE_ID,
        "fixture_id": ["experiment_d_refinement_identity_clean_fixtures"],
        "transform_id": sorted({row["transform_id"] for row in conditions}),
        "seed": 0,
        "runtime_params": {
            "mode": "reuse_experiment_d_runtime_state_outputs",
            "configured_window_steps": CONFIGURED_WINDOW_STEPS,
            "configured_min_basin_mass": CONFIGURED_MIN_BASIN_MASS,
            "runtime_mutation": "none",
        },
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_source_map": {
            key: str(path.relative_to(EXPERIMENT_ROOT))
            for key, path in INPUT_PATHS.items()
        },
        "output_paths": {
            key: str(path.relative_to(EXPERIMENT_ROOT))
            for key, path in outputs.items()
        },
        "evidence_labels": list(EVIDENCE_LABELS),
        "manifest_required_fields": list(manifest_schema()),
        "classification": summary["classification"],
        "blocked_or_inconclusive": [
            "checkpoint-window identity persistence",
            "mechanical-refinement-only positive control",
            "collapse/reabsorption outcome",
            "landscape-general identity emergence",
        ],
    }
    _write_json(outputs["manifest"], manifest)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-defaults",
        action="store_true",
        help="write D8 discriminator outputs under the experiment directory",
    )
    args = parser.parse_args()
    if not args.write_defaults:
        parser.error("pass --write-defaults to write outputs")
    outputs = write_outputs()
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
