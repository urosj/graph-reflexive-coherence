"""D5: interface-memory discriminator over Experiment D refinement artifacts."""

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
DISCRIMINATOR_ID = "d5_interface_memory"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_discriminator_d5_interface_memory.py"
)

INPUT_PATHS = {
    "harness_schema": (
        EXPERIMENT_ROOT / "outputs" / "discriminator_harness_schema.json"
    ),
    "d_reassignments": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_reassignments.csv"
    ),
    "d_persistence": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_persistence.csv"
    ),
    "d_thresholds": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_thresholds.csv"
    ),
    "d_conditions": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_conditions.csv"
    ),
    "d_summary": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_summary.json"
    ),
    "d2_schema": EXPERIMENT_ROOT / "outputs" / "d2_predictive_role_schema.json",
}

RANDOM_COLUMN_LABEL_BY_EDGE = {
    0: 2,
    1: 3,
    2: 1,
    3: 2,
    4: 1,
    5: 3,
    6: 3,
    7: 2,
    8: 1,
}
RANDOM_TRIPLE_LABEL_BY_EDGE = {
    0: 2,
    1: 1,
    2: 3,
    3: 3,
    4: 1,
    5: 2,
    6: 1,
    7: 3,
    8: 2,
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


def _int(value: str, default: int = 0) -> int:
    if value == "":
        return default
    return int(value)


def _float(value: str, default: float = 0.0) -> float:
    if value == "":
        return default
    return float(value)


def _condition_key(row: dict[str, str]) -> tuple[str, str]:
    return row["condition_id"], row["transform_id"]


def _condition_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    return {_condition_key(row): row for row in rows}


def _persistent_child_nodes(
    threshold_rows: list[dict[str, str]],
    *,
    window_steps: int,
    min_basin_mass: float,
) -> set[tuple[str, str, int]]:
    nodes: set[tuple[str, str, int]] = set()
    for row in threshold_rows:
        if _int(row["window_steps"]) != window_steps:
            continue
        if _float(row["min_basin_mass"]) != min_basin_mass:
            continue
        if not _truth(row["persistence_pass"]):
            continue
        nodes.add((row["condition_id"], row["transform_id"], _int(row["child_node_id"])))
    return nodes


def _persistence_mass_lookup(
    persistence_rows: list[dict[str, str]],
) -> dict[tuple[str, str, int], float]:
    latest: dict[tuple[str, str, int], tuple[int, float]] = {}
    for row in persistence_rows:
        key = (row["condition_id"], row["transform_id"], _int(row["child_node_id"]))
        window_index = _int(row["window_index"])
        basin_mass = _float(row["child_basin_mass"])
        if key not in latest or window_index > latest[key][0]:
            latest[key] = (window_index, basin_mass)
    return {key: basin_mass for key, (_, basin_mass) in latest.items()}


def edge_rows(
    reassignments: list[dict[str, str]],
    persistence_rows: list[dict[str, str]],
    thresholds: list[dict[str, str]],
    conditions: list[dict[str, str]],
    summary: dict[str, Any],
) -> list[dict[str, Any]]:
    window_steps = int(summary["persistence_window_steps"])
    min_basin_mass = float(summary["min_basin_mass_threshold"])
    persistent_nodes = _persistent_child_nodes(
        thresholds,
        window_steps=window_steps,
        min_basin_mass=min_basin_mass,
    )
    mass_lookup = _persistence_mass_lookup(persistence_rows)
    condition_by_key = _condition_lookup(conditions)
    rows: list[dict[str, Any]] = []
    for row in reassignments:
        edge_id = _int(row["edge_id"])
        old_row = _int(row["old_row"])
        old_column = _int(row["old_column"])
        target_column = _int(row["target_module_column"])
        new_node = _int(row["new_module_node_id"])
        key = _condition_key(row)
        persistent_key = (row["condition_id"], row["transform_id"], new_node)
        endpoint_persistent = persistent_key in persistent_nodes
        true_column_match = old_column == target_column
        row_label_match = old_row == target_column
        random_column_label = RANDOM_COLUMN_LABEL_BY_EDGE[edge_id]
        random_triple_label = RANDOM_TRIPLE_LABEL_BY_EDGE[edge_id]
        condition = condition_by_key[key]
        rows.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "seed": row["seed"],
                "condition_id": row["condition_id"],
                "condition_class": row["condition_class"],
                "transform_id": row["transform_id"],
                "edge_id": edge_id,
                "old_parent_port": _int(row["old_parent_port"]),
                "old_row": old_row,
                "old_column": old_column,
                "new_module_node_id": new_node,
                "new_module_port": _int(row["new_module_port"]),
                "target_module_column": target_column,
                "immediate_column_preserved": true_column_match,
                "immediate_row_label_match": row_label_match,
                "immediate_random_column_match": random_column_label == target_column,
                "immediate_random_triple_match": random_triple_label == target_column,
                "post_window_endpoint_persistent": endpoint_persistent,
                "post_window_child_basin_mass": mass_lookup.get(persistent_key, ""),
                "post_window_column_memory_match": (
                    true_column_match and endpoint_persistent
                ),
                "post_window_row_label_match": row_label_match and endpoint_persistent,
                "post_window_random_column_match": (
                    random_column_label == target_column and endpoint_persistent
                ),
                "post_window_random_triple_match": (
                    random_triple_label == target_column and endpoint_persistent
                ),
                "random_column_label": random_column_label,
                "random_triple_label": random_triple_label,
                "degree_adjacency_endpoint_baseline": endpoint_persistent,
                "post_refinement_flux_window_status": "blocked_unavailable",
                "persistence_window_steps": window_steps,
                "min_basin_mass_threshold": min_basin_mass,
                "budget_error": condition["budget_error"],
                "budget_tolerance": condition["budget_tolerance"],
                "budget_preserved": _truth(condition["budget_preserved"]),
                "evidence_label": "direct",
                "artifact_sources": (
                    "Experiment D reassignment rows; Experiment D runtime "
                    "state persistence rows"
                ),
            }
        )
    return rows


def _mean_bool(rows: list[dict[str, Any]], field: str) -> float:
    if not rows:
        return 0.0
    return sum(1.0 for row in rows if bool(row[field])) / len(rows)


def control_rows(edge_table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in edge_table:
        groups.setdefault((row["condition_id"], row["transform_id"]), []).append(row)
    rows: list[dict[str, Any]] = []
    for (condition_id, transform_id), group in sorted(groups.items()):
        rows.extend(
            [
                _control_row(condition_id, transform_id, "true_old_column", group),
                _control_row(condition_id, transform_id, "old_row_label", group),
                _control_row(condition_id, transform_id, "random_column_label", group),
                _control_row(condition_id, transform_id, "random_triple_label", group),
                _control_row(
                    condition_id,
                    transform_id,
                    "degree_adjacency_endpoint_baseline",
                    group,
                ),
            ]
        )
    return rows


def _control_row(
    condition_id: str,
    transform_id: str,
    predictor: str,
    group: list[dict[str, Any]],
) -> dict[str, Any]:
    immediate_field_by_predictor = {
        "true_old_column": "immediate_column_preserved",
        "old_row_label": "immediate_row_label_match",
        "random_column_label": "immediate_random_column_match",
        "random_triple_label": "immediate_random_triple_match",
        "degree_adjacency_endpoint_baseline": "degree_adjacency_endpoint_baseline",
    }
    post_field_by_predictor = {
        "true_old_column": "post_window_column_memory_match",
        "old_row_label": "post_window_row_label_match",
        "random_column_label": "post_window_random_column_match",
        "random_triple_label": "post_window_random_triple_match",
        "degree_adjacency_endpoint_baseline": "degree_adjacency_endpoint_baseline",
    }
    evidence_label = "direct" if predictor == "true_old_column" else "derived"
    if predictor == "degree_adjacency_endpoint_baseline":
        evidence_label = "partial"
    return {
        "discriminator": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "condition_id": condition_id,
        "transform_id": transform_id,
        "predictor": predictor,
        "edge_count": len(group),
        "immediate_score": _mean_bool(group, immediate_field_by_predictor[predictor]),
        "post_window_score": _mean_bool(group, post_field_by_predictor[predictor]),
        "configured_window_steps": group[0]["persistence_window_steps"],
        "min_basin_mass_threshold": group[0]["min_basin_mass_threshold"],
        "evidence_label": evidence_label,
        "notes": _control_notes(predictor),
    }


def _control_notes(predictor: str) -> str:
    if predictor == "true_old_column":
        return "True parent column label against target module column."
    if predictor == "old_row_label":
        return "Row-label control kept separate from true-column evidence."
    if predictor == "random_column_label":
        return "Deterministic sampled random column-label control."
    if predictor == "random_triple_label":
        return "Deterministic sampled random triple grouping control."
    return (
        "Endpoint persistence baseline only; it does not predict semantic "
        "module column."
    )


def summary_payload(
    edge_table: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    experiment_d_summary: dict[str, Any],
) -> dict[str, Any]:
    identity_edges = [row for row in edge_table if row["transform_id"] == "identity"]
    identity_controls = [
        row for row in controls if row["transform_id"] == "identity"
    ]
    by_predictor = {row["predictor"]: row for row in identity_controls}
    true_column = by_predictor["true_old_column"]
    row_label = by_predictor["old_row_label"]
    random_column = by_predictor["random_column_label"]
    random_triple = by_predictor["random_triple_label"]
    degree_baseline = by_predictor["degree_adjacency_endpoint_baseline"]
    return {
        "discriminator_id": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "classification": "mechanical_supported_post_window_partial",
        "immediate_column_preservation_score_identity": true_column[
            "immediate_score"
        ],
        "post_window_column_memory_score_identity": true_column["post_window_score"],
        "post_window_row_label_score_identity": row_label["post_window_score"],
        "post_window_random_column_score_identity": random_column[
            "post_window_score"
        ],
        "post_window_random_triple_score_identity": random_triple[
            "post_window_score"
        ],
        "degree_adjacency_endpoint_baseline_identity": degree_baseline[
            "post_window_score"
        ],
        "true_column_beats_row_label": (
            true_column["post_window_score"] > row_label["post_window_score"]
        ),
        "true_column_beats_random_column": (
            true_column["post_window_score"] > random_column["post_window_score"]
        ),
        "true_column_beats_random_triple": (
            true_column["post_window_score"] > random_triple["post_window_score"]
        ),
        "persistent_endpoint_edge_count_identity": sum(
            1 for row in identity_edges if row["post_window_endpoint_persistent"]
        ),
        "identity_edge_count": len(identity_edges),
        "all_refinement_rows_budget_preserved": experiment_d_summary[
            "all_refinement_rows_budget_preserved"
        ],
        "persistence_window_steps": experiment_d_summary[
            "persistence_window_steps"
        ],
        "min_basin_mass_threshold": experiment_d_summary[
            "min_basin_mass_threshold"
        ],
        "post_refinement_flux_window_status": "blocked_unavailable",
        "checkpoint_window_status": "inconclusive",
        "evidence_label": "partial",
        "boundary": (
            "Immediate mechanical column memory is direct. Post-window memory "
            "is supported only for module endpoints that are persistent child "
            "sinks in Experiment D runtime-state windows; post-event flux "
            "windows and checkpoint observer windows are unavailable."
        ),
    }


def blocked_observations() -> list[dict[str, str]]:
    return [
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "post-refinement flux window by old boundary edge",
            "status": "blocked",
            "artifact_source": "Experiment D persistence rows",
            "reconstruction_attempt": "Searched available D rows for per-edge post-event flux windows.",
            "notes": "D exposes reassignment rows and child sink/basin runtime snapshots, not per-edge post-event flux windows.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "checkpoint-window interface memory",
            "status": "inconclusive",
            "artifact_source": "Experiment D runtime-state persistence rows",
            "reconstruction_attempt": "Compared runtime persistence rows with persisted checkpoint requirement.",
            "notes": "D5 uses experiment-local runtime snapshots; persisted checkpoint observer windows remain a later addendum.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "dynamic interface memory for module-center endpoint",
            "status": "inconclusive",
            "artifact_source": "Experiment D child persistence rows",
            "reconstruction_attempt": "Joined reassignment endpoint node ids to persistent child sink nodes.",
            "notes": "Module node 414 is a reassignment endpoint but is not a child sink row in the persistence table.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "landscape-general interface memory",
            "status": "inconclusive",
            "artifact_source": "clean raw Experiment D fixtures",
            "reconstruction_attempt": "Reviewed fixture scope.",
            "notes": "D5 inherits the clean raw fixture scope; landscape/seed robustness is not tested.",
        },
    ]


def _write_blocked_report(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# D5 Blocked Observations",
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
    controls: list[dict[str, Any]],
) -> None:
    identity_controls = [
        row for row in controls if row["transform_id"] == "identity"
    ]
    identity_control_by_predictor = {
        row["predictor"]: row for row in identity_controls
    }
    predictor_order = (
        "true_old_column",
        "old_row_label",
        "random_column_label",
        "random_triple_label",
        "degree_adjacency_endpoint_baseline",
    )
    lines = [
        "# D5 Interface-Memory Discriminator Report",
        "",
        "Status: complete.",
        "",
        "Classification: `mechanical_supported_post_window_partial`.",
        "",
        "## Scope",
        "",
        "D5 reuses completed Experiment D refinement artifacts and does not add",
        "runtime behavior. It separates immediate mechanical column preservation",
        "from stricter post-window interface-memory evidence.",
        "",
        "Immediate memory is scored from",
        "`hybrid_mechanical_expansion.payload.reassignment_map`. Post-window",
        "memory is scored by joining reassignment endpoint nodes to Experiment D",
        "runtime-state child sink/basin persistence rows.",
        "",
        "## Identity Transform Scores",
        "",
        "Identity-transform scores are stable across the uniform and custom",
        "column-skewed transfer conditions, so the table reports one aggregate",
        "row per predictor.",
        "",
        "| Predictor | Immediate Score | Post-Window Score | Evidence | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for predictor in predictor_order:
        row = identity_control_by_predictor[predictor]
        lines.append(
            "| "
            f"{row['predictor']} | "
            f"{row['immediate_score']:.6f} | "
            f"{row['post_window_score']:.6f} | "
            f"{row['evidence_label']} | "
            f"{row['notes']} |"
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- immediate column preservation score: `{summary['immediate_column_preservation_score_identity']}`",
            f"- post-window column memory score: `{summary['post_window_column_memory_score_identity']}`",
            f"- post-window row-label score: `{summary['post_window_row_label_score_identity']}`",
            f"- post-window random-column score: `{summary['post_window_random_column_score_identity']}`",
            f"- post-window random-triple score: `{summary['post_window_random_triple_score_identity']}`",
            f"- persistent endpoint edge count: `{summary['persistent_endpoint_edge_count_identity']} / {summary['identity_edge_count']}`",
            f"- budget preserved for all refinement rows: `{summary['all_refinement_rows_budget_preserved']}`",
            f"- persistence window steps: `{summary['persistence_window_steps']}`",
            f"- minimum basin mass threshold: `{summary['min_basin_mass_threshold']}`",
            "",
            "## Interpretation",
            "",
            "D5 supports immediate mechanical column memory directly and supports",
            "post-window column memory only in the narrower runtime-state sense:",
            "old parent column remains more predictive than row labels and sampled",
            "random group controls for endpoints that participate in persistent",
            "child sink/basin rows.",
            "",
            "This does not establish post-event flux-memory behavior, checkpoint",
            "observer-window interface memory, or landscape-general interface",
            "memory.",
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
    reassignments = _read_csv(INPUT_PATHS["d_reassignments"])
    persistence = _read_csv(INPUT_PATHS["d_persistence"])
    thresholds = _read_csv(INPUT_PATHS["d_thresholds"])
    conditions = _read_csv(INPUT_PATHS["d_conditions"])
    d_summary = _read_json(INPUT_PATHS["d_summary"])
    edges = edge_rows(reassignments, persistence, thresholds, conditions, d_summary)
    controls = control_rows(edges)
    summary = summary_payload(edges, controls, d_summary)
    blocked = blocked_observations()

    outputs = {
        "edges": EXPERIMENT_ROOT / "outputs" / "d5_interface_memory_edges.csv",
        "controls": (
            EXPERIMENT_ROOT / "outputs" / "d5_random_column_controls.csv"
        ),
        "summary": EXPERIMENT_ROOT / "outputs" / "d5_interface_memory_summary.json",
        "manifest": EXPERIMENT_ROOT / "outputs" / "d5_interface_memory_manifest.json",
        "report": EXPERIMENT_ROOT / "reports" / "d5_interface_memory_report.md",
        "blocked": EXPERIMENT_ROOT / "reports" / "d5_blocked_observations.md",
    }
    _write_csv(outputs["edges"], edges)
    _write_csv(outputs["controls"], controls)
    _write_json(outputs["summary"], summary)
    _write_blocked_report(outputs["blocked"], blocked)
    _write_report(outputs["report"], summary, controls)

    manifest = {
        "discriminator_id": DISCRIMINATOR_ID,
        "iteration": "6",
        "script_path": SCRIPT_PATH,
        "command": (
            "python experiments/2026-05-N01-grc9v3-properties/scripts/"
            "run_discriminator_d5_interface_memory.py --write-defaults"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_status_short": _git_value(["status", "--short"]),
        "lane_id": LANE_ID,
        "fixture_id": sorted({row["condition_id"] for row in reassignments}),
        "transform_id": sorted({row["transform_id"] for row in reassignments}),
        "seed": 0,
        "runtime_params": {
            "mode": "reuse_completed_experiment_d_outputs",
            "runtime_mutation": "none",
            "persistence_window_steps": summary["persistence_window_steps"],
            "min_basin_mass_threshold": summary["min_basin_mass_threshold"],
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
        reassignments = _read_csv(INPUT_PATHS["d_reassignments"])
        persistence = _read_csv(INPUT_PATHS["d_persistence"])
        thresholds = _read_csv(INPUT_PATHS["d_thresholds"])
        conditions = _read_csv(INPUT_PATHS["d_conditions"])
        d_summary = _read_json(INPUT_PATHS["d_summary"])
        edges = edge_rows(reassignments, persistence, thresholds, conditions, d_summary)
        print(
            json.dumps(
                summary_payload(edges, control_rows(edges), d_summary),
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
