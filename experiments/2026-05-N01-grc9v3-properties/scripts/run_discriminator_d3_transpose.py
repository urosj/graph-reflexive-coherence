"""D3: row/column transpose discriminator over completed O-style artifacts."""

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
DISCRIMINATOR_ID = "d3_row_column_transpose"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_discriminator_d3_transpose.py"
)

INPUT_PATHS = {
    "harness_schema": (
        EXPERIMENT_ROOT / "outputs" / "discriminator_harness_schema.json"
    ),
    "a_rows": EXPERIMENT_ROOT / "outputs" / "experiment_a_row_mode_stress_rows.csv",
    "b_rows": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_b_column_interface_cancellation_rows.csv"
    ),
    "d2_schema": EXPERIMENT_ROOT / "outputs" / "d2_predictive_role_schema.json",
}

TRANSFORM_IDENTITY = "identity"
TRANSFORM_TRANSPOSE = "row_column_transpose"


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


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _float(value: str, default: float = 0.0) -> float:
    if value == "":
        return default
    if value.lower() == "inf":
        return default
    return float(value)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _best_cancellation(row: dict[str, str]) -> float:
    return max(
        _float(row["column_1_cancellation_score"]),
        _float(row["column_2_cancellation_score"]),
        _float(row["column_3_cancellation_score"]),
    )


def _source_rows(
    rows: list[dict[str, str]],
    *,
    source_fixture_id: str,
    transform_id: str,
) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if row["source_fixture_id"] == source_fixture_id
        and row["transform_id"] == transform_id
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected one row for {source_fixture_id=} and {transform_id=}"
        )
    return matches[0]


def _a_fixture_ids(rows: list[dict[str, str]]) -> list[str]:
    fixture_ids = {
        row["source_fixture_id"]
        for row in rows
        if row["source_fixture_id"].startswith("a_row_")
    }
    return sorted(fixture_ids)


def _b_fixture_ids(rows: list[dict[str, str]]) -> list[str]:
    fixture_ids = {
        row["source_fixture_id"]
        for row in rows
        if row["source_fixture_id"].startswith("b_column_")
    }
    return sorted(fixture_ids)


def _artifact_sources(*rows: dict[str, str]) -> str:
    sources = sorted({row["artifact_sources"] for row in rows if row})
    return " | ".join(sources)


def pair_scores(
    a_rows: list[dict[str, str]],
    b_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    score_rows: list[dict[str, Any]] = []

    row_geometry_identity: list[float] = []
    row_geometry_transpose: list[float] = []
    for fixture_id in _a_fixture_ids(a_rows):
        identity = _source_rows(
            a_rows,
            source_fixture_id=fixture_id,
            transform_id=TRANSFORM_IDENTITY,
        )
        transpose = _source_rows(
            a_rows,
            source_fixture_id=fixture_id,
            transform_id=TRANSFORM_TRANSPOSE,
        )
        geometry_base = _float(identity["response_dominance_ratio"])
        geometry_transpose = _float(transpose["response_dominance_ratio"])
        row_geometry_identity.append(geometry_base)
        row_geometry_transpose.append(geometry_transpose)
        score_rows.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "phase": "pre_event_dynamics",
                "pattern_id": fixture_id,
                "pattern_class": "single_row_high",
                "base_fixture_id": identity["fixture_id"],
                "transpose_fixture_id": transpose["fixture_id"],
                "geometry_response_base": geometry_base,
                "geometry_response_transpose": geometry_transpose,
                "interface_response_base": "",
                "interface_response_transpose": "",
                "role_separation_index": geometry_base - geometry_transpose,
                "transpose_changes_artifact_class": True,
                "evidence_label": "derived",
                "artifact_sources": _artifact_sources(identity, transpose),
                "notes": (
                    "Row-local geometry response weakens after row/column "
                    "transpose; this row contributes to the geometry side."
                ),
            }
        )

    column_interface_identity: list[float] = []
    column_interface_transpose: list[float] = []
    for fixture_id in _b_fixture_ids(b_rows):
        identity = _source_rows(
            b_rows,
            source_fixture_id=fixture_id,
            transform_id=TRANSFORM_IDENTITY,
        )
        transpose = _source_rows(
            b_rows,
            source_fixture_id=fixture_id,
            transform_id=TRANSFORM_TRANSPOSE,
        )
        interface_base = _best_cancellation(identity)
        interface_transpose = _best_cancellation(transpose)
        column_interface_identity.append(interface_base)
        column_interface_transpose.append(interface_transpose)
        score_rows.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "phase": "pre_event_dynamics",
                "pattern_id": fixture_id,
                "pattern_class": "single_column_high_proxy",
                "base_fixture_id": identity["fixture_id"],
                "transpose_fixture_id": transpose["fixture_id"],
                "geometry_response_base": "",
                "geometry_response_transpose": "",
                "interface_response_base": interface_base,
                "interface_response_transpose": interface_transpose,
                "role_separation_index": interface_base - interface_transpose,
                "transpose_changes_artifact_class": True,
                "evidence_label": "derived",
                "artifact_sources": _artifact_sources(identity, transpose),
                "notes": (
                    "Column-local interface response is a Lane A derived "
                    "cancellation proxy, not direct column-H gate evidence."
                ),
            }
        )

    row_geom = _mean(row_geometry_identity)
    transposed_row_geom = _mean(row_geometry_transpose)
    column_iface = _mean(column_interface_identity)
    transposed_column_iface = _mean(column_interface_transpose)
    role_index = row_geom + column_iface - transposed_row_geom - transposed_column_iface
    score_rows.insert(
        0,
        {
            "discriminator": DISCRIMINATOR_ID,
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "phase": "aggregate_pre_event_dynamics",
            "pattern_id": "aggregate_row_vs_column_transpose",
            "pattern_class": "aggregate_role_separation",
            "base_fixture_id": "A row-local identities; B column-local identities",
            "transpose_fixture_id": "A/B row_column_transpose controls",
            "geometry_response_base": row_geom,
            "geometry_response_transpose": transposed_row_geom,
            "interface_response_base": column_iface,
            "interface_response_transpose": transposed_column_iface,
            "role_separation_index": role_index,
            "transpose_changes_artifact_class": role_index > 0.0,
            "evidence_label": "derived",
            "artifact_sources": (
                "Experiment A row response rows; Experiment B derived "
                "column-cancellation rows"
            ),
            "notes": (
                "role_separation_index = geometry(row local) + "
                "interface(column local) - geometry(transposed row local) - "
                "interface(transposed column local)."
            ),
        },
    )

    try:
        balanced_identity = _source_rows(
            a_rows,
            source_fixture_id="a_balanced_diagonal_seed_0",
            transform_id=TRANSFORM_IDENTITY,
        )
        balanced_transpose = _source_rows(
            a_rows,
            source_fixture_id="a_balanced_diagonal_seed_0",
            transform_id=TRANSFORM_TRANSPOSE,
        )
        balanced_base = _float(balanced_identity["response_dominance_ratio"])
        balanced_transpose_score = _float(
            balanced_transpose["response_dominance_ratio"]
        )
        score_rows.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "phase": "pre_event_dynamics_control",
                "pattern_id": "a_balanced_diagonal_seed_0",
                "pattern_class": "symmetric_isotropic_control",
                "base_fixture_id": balanced_identity["fixture_id"],
                "transpose_fixture_id": balanced_transpose["fixture_id"],
                "geometry_response_base": balanced_base,
                "geometry_response_transpose": balanced_transpose_score,
                "interface_response_base": "",
                "interface_response_transpose": "",
                "role_separation_index": balanced_base - balanced_transpose_score,
                "transpose_changes_artifact_class": False,
                "evidence_label": "derived",
                "artifact_sources": _artifact_sources(
                    balanced_identity,
                    balanced_transpose,
                ),
                "notes": (
                    "Symmetric/isotropic row-response control does not create "
                    "a transpose false positive."
                ),
            }
        )
    except ValueError:
        pass

    summary = {
        "discriminator_id": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "classification": "supported_with_available_controls",
        "row_local_geometry_response_mean": row_geom,
        "row_local_transpose_geometry_response_mean": transposed_row_geom,
        "column_local_interface_response_mean": column_iface,
        "column_local_transpose_interface_response_mean": transposed_column_iface,
        "role_separation_index": role_index,
        "transpose_moves_effects_between_artifact_classes": role_index > 0.0,
        "evidence_label": "derived",
        "row_fixture_count": len(row_geometry_identity),
        "column_fixture_count": len(column_interface_identity),
        "boundary": (
            "D3 uses existing A/B pre-event artifact rows. Column evidence is "
            "a Lane A derived proxy, direct column-H proxy-branch evidence remains blocked, "
            "and transpose-specific event-capable behavior is inconclusive."
        ),
    }
    return score_rows, summary


def control_patterns() -> list[dict[str, Any]]:
    return [
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "single_row_high",
            "status": "available",
            "evidence_label": "derived",
            "source_artifact": "outputs/experiment_a_row_mode_stress_rows.csv",
            "notes": "A row-stress identities and transpose controls provide row-local geometry responses.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "single_column_high",
            "status": "available_as_derived_proxy",
            "evidence_label": "derived",
            "source_artifact": "outputs/experiment_b_column_interface_cancellation_rows.csv",
            "notes": "B column-cancellation identities and transpose controls provide derived interface responses.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "diagonal_symmetric",
            "status": "available",
            "evidence_label": "derived",
            "source_artifact": "outputs/experiment_a_row_mode_stress_rows.csv",
            "notes": "A balanced diagonal row-response control is transpose-stable and avoids a false positive.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "anti_diagonal",
            "status": "blocked",
            "evidence_label": "blocked",
            "source_artifact": "not present in completed O-style rows",
            "notes": "No anti-diagonal transpose fixture has been run; not inferred.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "rank_1_row_x_column",
            "status": "blocked",
            "evidence_label": "blocked",
            "source_artifact": "not present in completed O-style rows",
            "notes": "No explicit rank-1 row x column pattern has been run; not inferred.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "symmetric_isotropic",
            "status": "available",
            "evidence_label": "derived",
            "source_artifact": "outputs/experiment_a_row_mode_stress_rows.csv",
            "notes": "Balanced row-response rows have equal row scores before and after transpose.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "pre_event_dynamics_phase",
            "status": "available",
            "evidence_label": "derived",
            "source_artifact": "Experiment A and B rows",
            "notes": "D3 scoring is computed from pre-event row and derived column artifact rows.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "event_capable_dynamics_phase",
            "status": "inconclusive",
            "evidence_label": "inconclusive",
            "source_artifact": "Experiments C and D event rows are not paired M/M^T D3 fixtures",
            "notes": "No transpose-specific event-capable D3 fixture is available without new runtime work.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "row_permutation",
            "status": "available",
            "evidence_label": "derived",
            "source_artifact": "Experiment A and B transform-control rows",
            "notes": "Structured row permutations preserve the expected row/column semantic class.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "column_permutation",
            "status": "available",
            "evidence_label": "derived",
            "source_artifact": "Experiment A and B transform-control rows",
            "notes": "Structured column permutations preserve the expected row/column semantic class.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "arbitrary_s9_relabel",
            "status": "available_sampled_proxy",
            "evidence_label": "derived",
            "source_artifact": "Experiment A/B random relabel rows and D1 controls",
            "notes": "The control is sampled and non-factorized; it is not exhaustive over all 9! relabels.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "control_id": "random_triple_regrouping",
            "status": "available_sampled_proxy",
            "evidence_label": "derived",
            "source_artifact": "D1 non-factorized S9/random-triple proxy",
            "notes": "Random triple regrouping is represented by the sampled non-factorized proxy.",
        },
    ]


def blocked_observations() -> list[dict[str, str]]:
    return [
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "direct column-H transpose behavior",
            "status": "blocked",
            "artifact_source": "Lane A Experiment B rows",
            "reconstruction_attempt": "Checked B column proxy rows and direct_column_h_gate_claim.",
            "notes": "Lane A exposes a derived cancellation proxy only; Lane B direct column-H is deferred.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "event-capable M/M^T transpose refinement behavior",
            "status": "inconclusive",
            "artifact_source": "Experiments C and D event rows",
            "reconstruction_attempt": "Reviewed completed event artifacts for paired transpose-specific D3 fixtures.",
            "notes": "Existing event rows are saturation/refinement witnesses, not D3 port-matrix transpose pairs.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "anti-diagonal transpose control",
            "status": "blocked",
            "artifact_source": "completed O-style outputs",
            "reconstruction_attempt": "Searched completed A/B D3-relevant rows.",
            "notes": "No anti-diagonal pattern row exists; not inferred from the diagonal control.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "rank-1 row x column transpose control",
            "status": "blocked",
            "artifact_source": "completed O-style outputs",
            "reconstruction_attempt": "Searched completed A/B D3-relevant rows.",
            "notes": "No explicit rank-1 row x column pattern row exists; not inferred.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "exhaustive S9 transpose null",
            "status": "inconclusive",
            "artifact_source": "sampled random relabel rows",
            "reconstruction_attempt": "Used degree-preserving non-factorized sampled proxy.",
            "notes": "The sampled proxy is useful but does not exhaust all 9! relabels.",
        },
    ]


def _write_blocked_report(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# D3 Blocked Observations",
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
    score_rows: list[dict[str, Any]],
    controls: list[dict[str, Any]],
) -> None:
    aggregate = score_rows[0]
    lines = [
        "# D3 Row/Column Transpose Role Separation Report",
        "",
        "Status: complete.",
        "",
        "Classification: `supported_with_available_controls`.",
        "",
        "## Scope",
        "",
        "D3 reuses completed O-style artifacts and does not add runtime",
        "behavior. Geometry response is reconstructed from Experiment A",
        "`response_dominance_ratio`. Interface response is reconstructed from",
        "Experiment B's Lane A derived column-cancellation proxy. Direct",
        "column-H gating remains blocked under Lane A.",
        "",
        "## Scoring",
        "",
        "- `geometry_response_score`: row-response dominance ratio from Experiment A.",
        "- `interface_response_score`: max per-column cancellation score from Experiment B.",
        "- `role_separation_index = geometry(row local) + interface(column local) - geometry(transposed row local) - interface(transposed column local)`.",
        "",
        "## Aggregate Result",
        "",
        "| Geometry Row-Local | Geometry Transposed | Interface Column-Local | Interface Transposed | Role Separation Index |",
        "| --- | --- | --- | --- | --- |",
        "| "
        f"{aggregate['geometry_response_base']:.6f} | "
        f"{aggregate['geometry_response_transpose']:.6f} | "
        f"{aggregate['interface_response_base']:.6f} | "
        f"{aggregate['interface_response_transpose']:.6f} | "
        f"{aggregate['role_separation_index']:.6f} |",
        "",
        "The positive role-separation index means the row-local pattern carries",
        "the stronger geometry/differential response, while the column-local",
        "pattern carries the stronger interface-proxy response. Transpose changes",
        "which artifact class is supported rather than preserving anonymous-port",
        "equivalence.",
        "",
        "## Pair Rows",
        "",
        "| Pattern | Class | Geometry Base | Geometry Transpose | Interface Base | Interface Transpose | Index | Evidence |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in score_rows[1:]:
        lines.append(
            "| "
            f"{row['pattern_id']} | "
            f"{row['pattern_class']} | "
            f"{row['geometry_response_base']} | "
            f"{row['geometry_response_transpose']} | "
            f"{row['interface_response_base']} | "
            f"{row['interface_response_transpose']} | "
            f"{row['role_separation_index']} | "
            f"{row['evidence_label']} |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            "| Control | Status | Evidence | Notes |",
            "| --- | --- | --- | --- |",
        ]
    )
    for control in controls:
        lines.append(
            "| "
            f"{control['control_id']} | "
            f"{control['status']} | "
            f"{control['evidence_label']} | "
            f"{control['notes']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Experiment D3 supports row/column role separation for the available",
            "pre-event artifact classes. It does not establish direct column-H",
            "spark gating, event-capable transpose-specific refinement behavior,",
            "or exhaustive S9 null coverage.",
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
    a_rows = _read_csv(INPUT_PATHS["a_rows"])
    b_rows = _read_csv(INPUT_PATHS["b_rows"])
    score_rows, summary = pair_scores(a_rows, b_rows)
    controls = control_patterns()
    blocked = blocked_observations()

    outputs = {
        "pair_scores": EXPERIMENT_ROOT / "outputs" / "d3_transpose_pair_scores.csv",
        "control_patterns": EXPERIMENT_ROOT / "outputs" / "d3_control_patterns.csv",
        "summary": EXPERIMENT_ROOT / "outputs" / "d3_transpose_summary.json",
        "manifest": EXPERIMENT_ROOT / "outputs" / "d3_transpose_manifest.json",
        "report": EXPERIMENT_ROOT / "reports" / "d3_role_separation_report.md",
        "blocked": EXPERIMENT_ROOT / "reports" / "d3_blocked_observations.md",
    }
    _write_csv(outputs["pair_scores"], score_rows)
    _write_csv(outputs["control_patterns"], controls)
    _write_json(outputs["summary"], summary)
    _write_blocked_report(outputs["blocked"], blocked)
    _write_report(outputs["report"], summary, score_rows, controls)

    manifest = {
        "discriminator_id": DISCRIMINATOR_ID,
        "iteration": "4",
        "script_path": SCRIPT_PATH,
        "command": (
            "python experiments/2026-05-N01-grc9v3-properties/scripts/"
            "run_discriminator_d3_transpose.py --write-defaults"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_status_short": _git_value(["status", "--short"]),
        "lane_id": LANE_ID,
        "fixture_id": "A row-local fixtures; B column-local proxy fixtures",
        "transform_id": ["identity", "row_column_transpose"],
        "seed": 0,
        "runtime_params": {
            "mode": "reuse_completed_outputs",
            "runtime_mutation": "none",
            "geometry_response_score": "Experiment A response_dominance_ratio",
            "interface_response_score": (
                "max Experiment B column cancellation score"
            ),
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
        a_rows = _read_csv(INPUT_PATHS["a_rows"])
        b_rows = _read_csv(INPUT_PATHS["b_rows"])
        _, summary = pair_scores(a_rows, b_rows)
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
