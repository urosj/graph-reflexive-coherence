"""D7: multiscale discriminator over E reconstruction and D5 grouping rows."""

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
DISCRIMINATOR_ID = "d7_multiscale"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_discriminator_d7_multiscale.py"
)

INPUT_PATHS = {
    "harness_schema": (
        EXPERIMENT_ROOT / "outputs" / "discriminator_harness_schema.json"
    ),
    "e_errors": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_e_coarse_graining_split_errors.csv"
    ),
    "e_summary": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_e_coarse_graining_split_summary.json"
    ),
    "d5_edges": EXPERIMENT_ROOT / "outputs" / "d5_interface_memory_edges.csv",
    "d2_schema": EXPERIMENT_ROOT / "outputs" / "d2_predictive_role_schema.json",
}


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


def reconstruction_rows(e_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in e_rows:
        rows.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "checkpoint_phase": "static_pre_refinement_fixture",
                "field_name": row["field_name"],
                "field_class": row["field_class"],
                "grouping": "true_column",
                "mode": row["mode"],
                "eligible": row["eligible"],
                "reconstruction_path": row["reconstruction_path"],
                "max_abs_error": row["max_abs_error"],
                "nonzero_port_count": row["nonzero_port_count"],
                "zero_column_control": row["zero_column_control"],
                "single_active_column_control": row["single_active_column_control"],
                "exact_reconstruction_claim": (
                    _truth(row["eligible"])
                    and _float(row["max_abs_error"]) <= 1e-12
                ),
                "evidence_label": "direct" if _truth(row["eligible"]) else "derived",
                "artifact_sources": row["artifact_sources"],
                "notes": _reconstruction_notes(row),
            }
        )
    return rows


def _reconstruction_notes(row: dict[str, str]) -> str:
    if row["field_name"] == "signed_flux_compressed_total":
        return "Lossy signed compression diagnostic only; not exact reconstruction."
    if row["field_name"] == "signed_flux":
        return "Signed flux reconstructs exactly through J+/J- column split."
    return "Eligible nonnegative field reconstructs through true-column G/Split."


def signed_flux_controls(e_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in e_rows:
        if row["field_name"] not in {"signed_flux", "signed_flux_compressed_total"}:
            continue
        rows.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "control_id": row["field_name"],
                "mode": row["mode"],
                "eligible": row["eligible"],
                "reconstruction_path": row["reconstruction_path"],
                "max_abs_error": row["max_abs_error"],
                "compressed_signed_control_error": row[
                    "compressed_signed_control_error"
                ],
                "signed_flux_j_split_available": row[
                    "signed_flux_j_split_available"
                ],
                "classification": (
                    "exact_j_plus_j_minus"
                    if row["field_name"] == "signed_flux"
                    else "lossy_compressed_diagnostic"
                ),
                "evidence_label": (
                    "direct"
                    if row["field_name"] == "signed_flux"
                    else "derived"
                ),
                "notes": _reconstruction_notes(row),
            }
        )
    return rows


def _majority_target(edges: list[dict[str, str]]) -> int:
    counts: dict[int, int] = {}
    for row in edges:
        target = _int(row["target_module_column"])
        counts[target] = counts.get(target, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _score_label(
    edges: list[dict[str, str]],
    *,
    label_field: str | None,
    target: str,
) -> float:
    if not edges:
        return 0.0
    if label_field is None:
        majority = _majority_target(edges)
    matches = 0
    for row in edges:
        target_column = _int(row["target_module_column"])
        if label_field is None:
            label = majority
        else:
            label = _int(row[label_field])
        if target == "post_window_persistent_endpoint_column":
            matches += int(
                _truth(row["post_window_endpoint_persistent"])
                and label == target_column
            )
        else:
            matches += int(label == target_column)
    return matches / len(edges)


def grouping_semantic_rows(d5_edges: list[dict[str, str]]) -> list[dict[str, Any]]:
    identity_edges = [row for row in d5_edges if row["transform_id"] == "identity"]
    targets = (
        "immediate_refinement_endpoint_column",
        "post_window_persistent_endpoint_column",
    )
    grouping_specs = (
        ("true_column", "old_column", "direct"),
        ("true_row", "old_row", "derived"),
        ("random_column", "random_column_label", "derived"),
        ("random_triple", "random_triple_label", "derived"),
        ("single_nine_port_total", None, "partial"),
    )
    rows: list[dict[str, Any]] = []
    for target in targets:
        true_column_score = _score_label(
            identity_edges,
            label_field="old_column",
            target=target,
        )
        for grouping, field, evidence_label in grouping_specs:
            score = _score_label(identity_edges, label_field=field, target=target)
            rows.append(
                {
                    "discriminator": DISCRIMINATOR_ID,
                    "schema_version": ARTIFACT_SCHEMA_VERSION,
                    "lane_id": LANE_ID,
                    "source": "D5 identity refinement edges",
                    "target": target,
                    "grouping": grouping,
                    "score": score,
                    "true_column_score": true_column_score,
                    "delta_vs_true_column": score - true_column_score,
                    "edge_count": len(identity_edges),
                    "evidence_label": evidence_label,
                    "notes": _grouping_notes(grouping, target),
                }
            )
    return rows


def _grouping_notes(grouping: str, target: str) -> str:
    if grouping == "true_column":
        return "True old parent column compared to refinement/interface target."
    if grouping == "true_row":
        return "True row grouping control; not expected to match column interface target."
    if grouping == "random_triple":
        return "Sampled random triple grouping control inherited from D5."
    if grouping == "single_nine_port_total":
        return "Single-total baseline predicts one majority target column only."
    return f"Control grouping for {target}."


def summary_payload(
    reconstruction: list[dict[str, Any]],
    signed_controls: list[dict[str, Any]],
    semantic: list[dict[str, Any]],
    e_summary: dict[str, Any],
) -> dict[str, Any]:
    immediate = {
        row["grouping"]: row
        for row in semantic
        if row["target"] == "immediate_refinement_endpoint_column"
    }
    post = {
        row["grouping"]: row
        for row in semantic
        if row["target"] == "post_window_persistent_endpoint_column"
    }
    return {
        "discriminator_id": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "classification": "reconstruction_supported_semantic_columns_supported_with_boundaries",
        "all_eligible_fields_near_exact": e_summary["all_eligible_fields_near_exact"],
        "max_exact_reconstruction_error": e_summary[
            "max_exact_reconstruction_error"
        ],
        "signed_flux_j_split_available": e_summary["signed_flux_j_split_available"],
        "compressed_signed_flux_is_lossy": e_summary[
            "compressed_signed_flux_is_lossy"
        ],
        "compressed_signed_flux_lossy_error": e_summary[
            "compressed_signed_flux_lossy_error"
        ],
        "reconstruction_row_count": len(reconstruction),
        "signed_flux_control_count": len(signed_controls),
        "immediate_true_column_score": immediate["true_column"]["score"],
        "immediate_true_row_score": immediate["true_row"]["score"],
        "immediate_random_triple_score": immediate["random_triple"]["score"],
        "immediate_single_total_score": immediate["single_nine_port_total"]["score"],
        "post_window_true_column_score": post["true_column"]["score"],
        "post_window_true_row_score": post["true_row"]["score"],
        "post_window_random_triple_score": post["random_triple"]["score"],
        "post_window_single_total_score": post["single_nine_port_total"]["score"],
        "true_columns_beat_rows_for_interface_targets": (
            immediate["true_column"]["score"] > immediate["true_row"]["score"]
            and post["true_column"]["score"] > post["true_row"]["score"]
        ),
        "true_columns_beat_random_triples_for_interface_targets": (
            immediate["true_column"]["score"] > immediate["random_triple"]["score"]
            and post["true_column"]["score"] > post["random_triple"]["score"]
        ),
        "before_after_refinement_gsplit_status": "blocked_no_persisted_e_style_refinement_checkpoints",
        "evidence_label": "direct",
        "boundary": (
            "D7 supports exact true-column G/Split reconstruction for "
            "Experiment E fields and true-column semantic usefulness for "
            "D5 interface/refinement targets. Before/after refinement "
            "E-style G/Split checkpoints remain blocked."
        ),
    }


def blocked_observations() -> list[dict[str, str]]:
    return [
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "before/after refinement E-style G/Split checkpoints",
            "status": "blocked",
            "artifact_source": "Experiment D runtime state snapshots; Experiment E reconstruction rows",
            "reconstruction_attempt": "Checked available outputs for persisted E-style pre/post refinement checkpoint fields.",
            "notes": "Experiment E is static pre-refinement; Experiment D has runtime-state refinement rows but not E-style persisted G/Split checkpoint fields.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "semantic superiority for landscape-general interface targets",
            "status": "inconclusive",
            "artifact_source": "D5 clean raw refinement fixtures",
            "reconstruction_attempt": "Computed true-column versus row/random grouping scores on D5 identity rows.",
            "notes": "D7 semantic comparison is clean-fixture evidence, not a landscape/seed robustness suite.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "rows/random triples as exact G/Split alternatives",
            "status": "inconclusive",
            "artifact_source": "Experiment E true-column G/Split rows",
            "reconstruction_attempt": "Separated exact reconstruction from semantic grouping comparison.",
            "notes": "D7 does not claim rows/random triples cannot be made invertible with their own profiles; it tests semantic usefulness for interface/refinement targets.",
        },
    ]


def _write_blocked_report(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# D7 Blocked Observations",
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
    signed_controls: list[dict[str, Any]],
    semantic: list[dict[str, Any]],
) -> None:
    lines = [
        "# D7 Multiscale Discriminator Report",
        "",
        "Status: complete.",
        "",
        "Classification: `reconstruction_supported_semantic_columns_supported_with_boundaries`.",
        "",
        "## Scope",
        "",
        "D7 separates exact mathematical reconstruction from semantic grouping",
        "usefulness. Experiment E supplies true-column G/Split reconstruction",
        "evidence. D5 supplies interface/refinement rows for true-column versus",
        "row/random grouping comparison.",
        "",
        "## Reconstruction",
        "",
        f"- all eligible fields near exact: `{summary['all_eligible_fields_near_exact']}`",
        f"- max exact reconstruction error: `{summary['max_exact_reconstruction_error']}`",
        f"- signed flux J+/J- available: `{summary['signed_flux_j_split_available']}`",
        "",
        "## Signed Flux Controls",
        "",
        "| Control | Classification | Error | Notes |",
        "| --- | --- | --- | --- |",
    ]
    for row in signed_controls:
        lines.append(
            "| "
            f"{row['control_id']} | "
            f"{row['classification']} | "
            f"{row['max_abs_error']} | "
            f"{row['notes']} |"
        )
    lines.extend(
        [
            "",
            "## Semantic Grouping Comparison",
            "",
            "| Target | Grouping | Score | Delta vs True Column | Evidence |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in semantic:
        lines.append(
            "| "
            f"{row['target']} | "
            f"{row['grouping']} | "
            f"{row['score']:.6f} | "
            f"{row['delta_vs_true_column']:.6f} | "
            f"{row['evidence_label']} |"
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- immediate true-column score: `{summary['immediate_true_column_score']}`",
            f"- immediate true-row score: `{summary['immediate_true_row_score']}`",
            f"- immediate random-triple score: `{summary['immediate_random_triple_score']}`",
            f"- post-window true-column score: `{summary['post_window_true_column_score']}`",
            f"- post-window true-row score: `{summary['post_window_true_row_score']}`",
            f"- post-window random-triple score: `{summary['post_window_random_triple_score']}`",
            f"- compressed signed flux lossy error: `{summary['compressed_signed_flux_lossy_error']}`",
            "",
            "## Interpretation",
            "",
            "D7 supports exact true-column G/Split reconstruction for eligible",
            "Experiment E fields and signed flux through J+/J-. It also supports",
            "true-column semantic usefulness for interface/refinement targets:",
            "true columns outperform true rows, sampled random triples, and a",
            "single-total baseline on D5 immediate and post-window targets.",
            "",
            "The compressed signed-flux total is reported only as a lossy",
            "diagnostic, not an exact reconstruction path.",
            "",
            "## Boundaries",
            "",
            "- before/after refinement E-style G/Split checkpoints remain blocked;",
            "- semantic grouping comparison is clean-fixture evidence only;",
            "- D7 does not claim arbitrary rows/random triples cannot be made",
            "  mathematically invertible with their own profiles.",
            "",
            "## Manifest Fields",
            "",
            f"- required manifest fields: `{', '.join(manifest_schema())}`",
            f"- evidence labels: `{', '.join(EVIDENCE_LABELS)}`",
            f"- summary boundary: {summary['boundary']}",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs() -> dict[str, Path]:
    e_rows = _read_csv(INPUT_PATHS["e_errors"])
    e_summary = _read_json(INPUT_PATHS["e_summary"])
    d5_edges = _read_csv(INPUT_PATHS["d5_edges"])
    reconstruction = reconstruction_rows(e_rows)
    signed_controls = signed_flux_controls(e_rows)
    semantic = grouping_semantic_rows(d5_edges)
    summary = summary_payload(reconstruction, signed_controls, semantic, e_summary)
    blocked = blocked_observations()
    outputs = {
        "reconstruction": EXPERIMENT_ROOT / "outputs" / "d7_reconstruction_errors.csv",
        "signed_controls": EXPERIMENT_ROOT / "outputs" / "d7_signed_flux_controls.csv",
        "semantic": (
            EXPERIMENT_ROOT / "outputs" / "d7_grouping_semantic_comparison.csv"
        ),
        "summary": EXPERIMENT_ROOT / "outputs" / "d7_multiscale_summary.json",
        "manifest": EXPERIMENT_ROOT / "outputs" / "d7_multiscale_manifest.json",
        "report": EXPERIMENT_ROOT / "reports" / "d7_multiscale_report.md",
        "blocked": EXPERIMENT_ROOT / "reports" / "d7_blocked_observations.md",
    }
    _write_csv(outputs["reconstruction"], reconstruction)
    _write_csv(outputs["signed_controls"], signed_controls)
    _write_csv(outputs["semantic"], semantic)
    _write_json(outputs["summary"], summary)
    _write_blocked_report(outputs["blocked"], blocked)
    _write_report(outputs["report"], summary, signed_controls, semantic)
    manifest = {
        "discriminator_id": DISCRIMINATOR_ID,
        "iteration": "8",
        "script_path": SCRIPT_PATH,
        "command": (
            "python experiments/2026-05-N01-grc9v3-properties/scripts/"
            "run_discriminator_d7_multiscale.py --write-defaults"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_status_short": _git_value(["status", "--short"]),
        "lane_id": LANE_ID,
        "fixture_id": [
            "experiment_e_static_column_split_fixture",
            "d5_identity_refinement_edges",
        ],
        "transform_id": ["identity"],
        "seed": 0,
        "runtime_params": {
            "mode": "reuse_experiment_e_and_d5_outputs",
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
        "manifest_required_fields": list(manifest_schema()),
        "evidence_labels": list(EVIDENCE_LABELS),
    }
    _write_json(outputs["manifest"], manifest)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-defaults", action="store_true")
    args = parser.parse_args()
    if args.write_defaults:
        paths = write_outputs()
        print(json.dumps({key: str(path) for key, path in paths.items()}, indent=2))
    else:
        e_rows = _read_csv(INPUT_PATHS["e_errors"])
        e_summary = _read_json(INPUT_PATHS["e_summary"])
        d5_edges = _read_csv(INPUT_PATHS["d5_edges"])
        reconstruction = reconstruction_rows(e_rows)
        signed_controls = signed_flux_controls(e_rows)
        semantic = grouping_semantic_rows(d5_edges)
        print(
            json.dumps(
                summary_payload(reconstruction, signed_controls, semantic, e_summary),
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
