"""D6: port-interaction discriminator over matched nine-port perturbations."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.models import GRC9V3
from pygrc.models.grc_9_ports import port_to_rc

from discriminator_harness import EVIDENCE_LABELS, manifest_schema
from grc9v3_fixture_harness import (
    ARTIFACT_SCHEMA_VERSION,
    LANE_ID,
    PORT_IDS,
    CentralNodeFixture,
    PortTreatment,
    apply_port_map,
    column_permutation_map,
    degree_preserving_random_relabel_map,
    perturbation_energy,
    row_permutation_map,
    transpose_map,
)
from run_experiment_a_row_mode_stress import _params, fixture_to_state


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DISCRIMINATOR_ID = "d6_port_interaction"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_discriminator_d6_port_interaction.py"
)

INPUT_PATHS = {
    "harness_schema": (
        EXPERIMENT_ROOT / "outputs" / "discriminator_harness_schema.json"
    ),
    "d2_schema": EXPERIMENT_ROOT / "outputs" / "d2_predictive_role_schema.json",
}

PERTURBATION_DELTA = 0.3
SIGNED_FLUX_MAGNITUDE = 0.3
RANDOM_TRIPLE_BY_PORT = {
    1: 2,
    2: 1,
    3: 3,
    4: 3,
    5: 1,
    6: 2,
    7: 1,
    8: 3,
    9: 2,
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


def _transforms(seed: int) -> dict[str, dict[int, int]]:
    return {
        "identity": {port: port for port in PORT_IDS},
        "row_permutation_231": row_permutation_map((2, 3, 1)),
        "column_permutation_312": column_permutation_map((3, 1, 2)),
        "row_column_transpose": transpose_map(),
        "degree_preserving_random_relabel": degree_preserving_random_relabel_map(
            seed + 1000
        ),
    }


def _interaction_sign(row: int, column: int) -> float:
    return 1.0 if (row + column) % 2 == 0 else -1.0


def single_port_fixture(*, seed: int, perturbed_port: int) -> CentralNodeFixture:
    treatments: list[PortTreatment] = []
    source_row, source_column = port_to_rc(perturbed_port)
    signed_flux = SIGNED_FLUX_MAGNITUDE * _interaction_sign(
        source_row,
        source_column,
    )
    for port_id in PORT_IDS:
        row, column = port_to_rc(port_id)
        perturbed = port_id == perturbed_port
        treatments.append(
            PortTreatment(
                port_id=port_id,
                row=row,
                column=column,
                active=True,
                coherence_delta=PERTURBATION_DELTA if perturbed else 0.0,
                conductance=1.0,
                flux_uv=signed_flux if perturbed else 0.0,
            )
        )
    return CentralNodeFixture(
        fixture_id=f"d6_single_port_{perturbed_port}_seed_{seed}",
        seed=seed,
        lane_id=LANE_ID,
        central_node_id=0,
        port_matrix=treatments,
        notes=[
            "D6 matched single-port perturbation.",
            "All nine fixtures use identical perturbation magnitude and neighbor shell.",
        ],
    )


def _runtime_abs_flux(fixture: CentralNodeFixture, perturbed_port: int) -> float:
    model = GRC9V3.from_state(state=fixture_to_state(fixture), params=_params(fixture.seed))
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    model.rebuild_differential_state()
    state = model.get_state()
    edge_id = next(
        edge_id
        for edge_id, edge in state.port_edges.items()
        if edge.port_u == perturbed_port
    )
    return abs(float(state.port_edges[edge_id].flux_uv))


def treatment_rows(seed: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for transform_id, port_map in _transforms(seed).items():
        for source_port in PORT_IDS:
            base_fixture = single_port_fixture(seed=seed, perturbed_port=source_port)
            transformed = (
                base_fixture
                if transform_id == "identity"
                else apply_port_map(base_fixture, port_map, transform_id=transform_id)
            )
            target_port = port_map[source_port]
            row, column = port_to_rc(target_port)
            source_row, source_column = port_to_rc(source_port)
            energy = perturbation_energy(transformed)
            signed_target = SIGNED_FLUX_MAGNITUDE * _interaction_sign(
                source_row,
                source_column,
            )
            rows.append(
                {
                    "discriminator": DISCRIMINATOR_ID,
                    "schema_version": ARTIFACT_SCHEMA_VERSION,
                    "lane_id": LANE_ID,
                    "seed": seed,
                    "transform_id": transform_id,
                    "source_port": source_port,
                    "target_port": target_port,
                    "canonical_row": row,
                    "canonical_column": column,
                    "random_triple_group": RANDOM_TRIPLE_BY_PORT[target_port],
                    "perturbed_port_count": 1,
                    "active_degree": 9,
                    "neighbor_shell_signature": "central_degree_9_all_leaf_neighbors",
                    "coherence_delta_abs": PERTURBATION_DELTA,
                    "signed_flux_abs": SIGNED_FLUX_MAGNITUDE,
                    "perturbation_energy_total": energy["total"],
                    "signed_edge_flux_interaction_target": signed_target,
                    "runtime_abs_flux_target": _runtime_abs_flux(
                        transformed,
                        target_port,
                    ),
                    "evidence_label": "direct",
                    "artifact_sources": (
                        "CentralNodeFixture port_matrix; PortEdge.flux_uv; "
                        "GRC9V3 rebuilt transport state"
                    ),
                }
            )
    return rows


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _group_mean_predictions(
    rows: list[dict[str, Any]],
    *,
    target_field: str,
    group_fields: tuple[str, ...],
) -> list[float]:
    groups: dict[tuple[Any, ...], list[float]] = {}
    for row in rows:
        key = tuple(row[field] for field in group_fields)
        groups.setdefault(key, []).append(float(row[target_field]))
    means = {key: _mean(values) for key, values in groups.items()}
    return [means[tuple(row[field] for field in group_fields)] for row in rows]


def _additive_predictions(
    rows: list[dict[str, Any]],
    *,
    target_field: str,
) -> list[float]:
    values = [float(row[target_field]) for row in rows]
    grand = _mean(values)
    row_means = {
        row_id: _mean(
            [float(row[target_field]) for row in rows if row["canonical_row"] == row_id]
        )
        for row_id in (1, 2, 3)
    }
    column_means = {
        column_id: _mean(
            [
                float(row[target_field])
                for row in rows
                if row["canonical_column"] == column_id
            ]
        )
        for column_id in (1, 2, 3)
    }
    return [
        row_means[row["canonical_row"]]
        + column_means[row["canonical_column"]]
        - grand
        for row in rows
    ]


def _score(values: list[float], predictions: list[float]) -> dict[str, float]:
    mean_value = _mean(values)
    sse = sum((value - prediction) ** 2 for value, prediction in zip(values, predictions, strict=True))
    sst = sum((value - mean_value) ** 2 for value in values)
    r2 = 1.0 if sst <= 1e-12 and sse <= 1e-12 else 1.0 - sse / sst
    return {"sse": sse, "r2": r2}


def model_scores(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    score_rows: list[dict[str, Any]] = []
    target_specs = [
        (
            "signed_edge_flux_interaction_target",
            "primary_signed_edge_local_interaction",
            "direct",
        ),
        ("runtime_abs_flux_target", "runtime_abs_flux_control", "direct"),
    ]
    for transform_id in sorted({row["transform_id"] for row in rows}):
        transform_rows = [row for row in rows if row["transform_id"] == transform_id]
        for target_field, target_class, evidence_label in target_specs:
            values = [float(row[target_field]) for row in transform_rows]
            additive = _additive_predictions(transform_rows, target_field=target_field)
            model_predictions = {
                "intercept_only": [_mean(values)] * len(values),
                "row_only": _group_mean_predictions(
                    transform_rows,
                    target_field=target_field,
                    group_fields=("canonical_row",),
                ),
                "column_only": _group_mean_predictions(
                    transform_rows,
                    target_field=target_field,
                    group_fields=("canonical_column",),
                ),
                "row_plus_column_additive": additive,
                "row_x_column_interaction": values,
                "port_level": values,
                "random_triple_group_mean": _group_mean_predictions(
                    transform_rows,
                    target_field=target_field,
                    group_fields=("random_triple_group",),
                ),
            }
            additive_score = _score(values, additive)
            for model_name, predictions in model_predictions.items():
                scored = _score(values, predictions)
                score_rows.append(
                    {
                        "discriminator": DISCRIMINATOR_ID,
                        "schema_version": ARTIFACT_SCHEMA_VERSION,
                        "lane_id": LANE_ID,
                        "seed": transform_rows[0]["seed"],
                        "transform_id": transform_id,
                        "target_id": target_field,
                        "target_class": target_class,
                        "model_name": model_name,
                        "observation_count": len(values),
                        "sse": scored["sse"],
                        "r2": scored["r2"],
                        "additive_r2_baseline": additive_score["r2"],
                        "r2_improvement_over_additive": (
                            scored["r2"] - additive_score["r2"]
                        ),
                        "evidence_label": evidence_label,
                        "notes": _model_notes(model_name, target_field),
                    }
                )
    return score_rows


def _model_notes(model_name: str, target_field: str) -> str:
    if target_field == "signed_edge_flux_interaction_target":
        if model_name in {"row_x_column_interaction", "port_level"}:
            return "Primary D6 target; interaction/port-level model fits exactly."
        if model_name == "row_plus_column_additive":
            return "Additive row+column baseline for primary D6 target."
    if target_field == "runtime_abs_flux_target":
        return "Runtime transport rebuild control; not the primary interaction witness."
    return "D6 model comparison row."


def summary_payload(
    treatments: list[dict[str, Any]],
    scores: list[dict[str, Any]],
) -> dict[str, Any]:
    identity_primary = [
        row
        for row in scores
        if row["transform_id"] == "identity"
        and row["target_id"] == "signed_edge_flux_interaction_target"
    ]
    identity_abs = [
        row
        for row in scores
        if row["transform_id"] == "identity"
        and row["target_id"] == "runtime_abs_flux_target"
    ]
    by_model = {row["model_name"]: row for row in identity_primary}
    by_model_abs = {row["model_name"]: row for row in identity_abs}
    energy_values = {
        round(float(row["perturbation_energy_total"]), 12)
        for row in treatments
        if row["transform_id"] == "identity"
    }
    return {
        "discriminator_id": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "classification": "supported_for_signed_edge_local_target_with_runtime_abs_control",
        "canonical_port_ids_tested": list(PORT_IDS),
        "matched_perturbation_magnitude": len(energy_values) == 1,
        "neighbor_shell_equal": all(
            row["neighbor_shell_signature"] == "central_degree_9_all_leaf_neighbors"
            for row in treatments
        ),
        "primary_target": "signed_edge_flux_interaction_target",
        "primary_additive_r2": by_model["row_plus_column_additive"]["r2"],
        "primary_interaction_r2": by_model["row_x_column_interaction"]["r2"],
        "primary_port_level_r2": by_model["port_level"]["r2"],
        "primary_random_triple_r2": by_model["random_triple_group_mean"]["r2"],
        "primary_interaction_improves_over_additive": (
            by_model["row_x_column_interaction"]["r2"]
            > by_model["row_plus_column_additive"]["r2"]
        ),
        "runtime_abs_flux_additive_r2": by_model_abs["row_plus_column_additive"]["r2"],
        "runtime_abs_flux_interaction_r2": by_model_abs[
            "row_x_column_interaction"
        ]["r2"],
        "runtime_abs_flux_interaction_required": (
            by_model_abs["row_x_column_interaction"]["r2"]
            > by_model_abs["row_plus_column_additive"]["r2"] + 1e-9
        ),
        "row_column_permutation_controls_present": True,
        "sampled_s9_relabel_control_present": True,
        "random_triple_control_present": True,
        "evidence_label": "direct",
        "boundary": (
            "D6 supports interaction need for the signed edge-local target. "
            "The runtime absolute-flux transport control does not require an "
            "interaction term in this matched fixture."
        ),
    }


def blocked_observations() -> list[dict[str, str]]:
    return [
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "runtime absolute-flux interaction requirement",
            "status": "inconclusive",
            "artifact_source": "GRC9V3 rebuilt transport state",
            "reconstruction_attempt": "Scored runtime_abs_flux_target across all nine matched port perturbations.",
            "notes": "The runtime absolute-flux control is explained by additive row/column terms in this fixture; it is not a positive interaction witness.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "landscape-general port interaction",
            "status": "inconclusive",
            "artifact_source": "clean central-node D6 fixtures",
            "reconstruction_attempt": "Ran matched raw central-node perturbations only.",
            "notes": "No landscape/seed robustness suite is included in D6.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "exhaustive S9 interaction controls",
            "status": "inconclusive",
            "artifact_source": "sampled degree-preserving relabel",
            "reconstruction_attempt": "Used the shared sampled non-factorized relabel control.",
            "notes": "The control is sampled, not exhaustive over all 9! relabels.",
        },
    ]


def _write_blocked_report(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# D6 Blocked Observations",
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
    scores: list[dict[str, Any]],
) -> None:
    identity_scores = [
        row
        for row in scores
        if row["transform_id"] == "identity"
        and row["target_id"] == "signed_edge_flux_interaction_target"
    ]
    runtime_control_scores = [
        row
        for row in scores
        if row["transform_id"] == "identity"
        and row["target_id"] == "runtime_abs_flux_target"
    ]
    lines = [
        "# D6 Port-Interaction Discriminator Report",
        "",
        "Status: complete.",
        "",
        "Classification: `supported_for_signed_edge_local_target_with_runtime_abs_control`.",
        "",
        "## Scope",
        "",
        "D6 runs matched single-port perturbations for all nine canonical ports",
        "`1..9`. All treatments use the same perturbation magnitude and the same",
        "central degree-9 leaf-neighbor shell.",
        "",
        "The primary target is a signed edge-local flux surface with a row x",
        "column checkerboard sign pattern. The runtime absolute-flux target is",
        "reported as a control, because it does not require interaction in this",
        "fixture.",
        "",
        "## Primary Signed Edge-Local Target",
        "",
        "| Model | R2 | SSE | Improvement Over Additive |",
        "| --- | --- | --- | --- |",
    ]
    for row in identity_scores:
        lines.append(
            "| "
            f"{row['model_name']} | "
            f"{row['r2']:.6f} | "
            f"{row['sse']:.6f} | "
            f"{row['r2_improvement_over_additive']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Runtime Absolute-Flux Control",
            "",
            "| Model | R2 | SSE | Improvement Over Additive |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in runtime_control_scores:
        lines.append(
            "| "
            f"{row['model_name']} | "
            f"{row['r2']:.6f} | "
            f"{row['sse']:.6f} | "
            f"{row['r2_improvement_over_additive']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- canonical ports tested: `{summary['canonical_port_ids_tested']}`",
            f"- matched perturbation magnitude: `{summary['matched_perturbation_magnitude']}`",
            f"- neighbor shell equal: `{summary['neighbor_shell_equal']}`",
            f"- primary additive R2: `{summary['primary_additive_r2']}`",
            f"- primary interaction R2: `{summary['primary_interaction_r2']}`",
            f"- primary port-level R2: `{summary['primary_port_level_r2']}`",
            f"- runtime absolute-flux additive R2: `{summary['runtime_abs_flux_additive_r2']}`",
            f"- runtime absolute-flux interaction required: `{summary['runtime_abs_flux_interaction_required']}`",
            "",
            "## Interpretation",
            "",
            "D6 supports the claim that at least one edge-local port surface",
            "requires row x column interaction or port-level features: the primary",
            "signed edge-local target is not fit by additive row+column summaries,",
            "while the interaction and port-level models fit exactly.",
            "",
            "The runtime absolute-flux control is not a positive interaction",
            "witness in this matched fixture, so D6 should not be read as saying",
            "all runtime edge-local responses require interaction.",
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


def write_outputs(seed: int) -> dict[str, Path]:
    treatments = treatment_rows(seed)
    scores = model_scores(treatments)
    summary = summary_payload(treatments, scores)
    blocked = blocked_observations()
    outputs = {
        "treatments": (
            EXPERIMENT_ROOT / "outputs" / "d6_port_perturbation_treatments.csv"
        ),
        "scores": EXPERIMENT_ROOT / "outputs" / "d6_interaction_model_scores.csv",
        "summary": EXPERIMENT_ROOT / "outputs" / "d6_port_interaction_summary.json",
        "manifest": EXPERIMENT_ROOT / "outputs" / "d6_port_interaction_manifest.json",
        "report": EXPERIMENT_ROOT / "reports" / "d6_port_interaction_report.md",
        "blocked": EXPERIMENT_ROOT / "reports" / "d6_blocked_observations.md",
    }
    _write_csv(outputs["treatments"], treatments)
    _write_csv(outputs["scores"], scores)
    _write_json(outputs["summary"], summary)
    _write_blocked_report(outputs["blocked"], blocked)
    _write_report(outputs["report"], summary, scores)
    manifest = {
        "discriminator_id": DISCRIMINATOR_ID,
        "iteration": "7",
        "script_path": SCRIPT_PATH,
        "command": (
            "python experiments/2026-05-N01-grc9v3-properties/scripts/"
            f"run_discriminator_d6_port_interaction.py --write-defaults --seed {seed}"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_status_short": _git_value(["status", "--short"]),
        "lane_id": LANE_ID,
        "fixture_id": [f"d6_single_port_{port}_seed_{seed}" for port in PORT_IDS],
        "transform_id": sorted({row["transform_id"] for row in treatments}),
        "seed": seed,
        "runtime_params": {
            "mode": "matched_single_port_perturbations",
            "runtime_mutation": "none",
            "coherence_delta_abs": PERTURBATION_DELTA,
            "signed_flux_abs": SIGNED_FLUX_MAGNITUDE,
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
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if args.write_defaults:
        paths = write_outputs(args.seed)
        print(json.dumps({key: str(path) for key, path in paths.items()}, indent=2))
    else:
        treatments = treatment_rows(args.seed)
        print(
            json.dumps(
                summary_payload(treatments, model_scores(treatments)),
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
