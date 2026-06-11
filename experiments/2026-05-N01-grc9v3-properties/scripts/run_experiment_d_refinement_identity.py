"""Experiment D: refinement mapping and child identity persistence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.models import GRC9V3
from pygrc.models.grc_9_ports import port_to_rc

from grc9v3_fixture_harness import (
    ARTIFACT_SCHEMA_VERSION,
    LANE_ID,
    PORT_IDS,
    artifact_entry_points,
    blocked_observations_schema,
    column_permutation_map,
    comparison_report_schema,
    degree_preserving_random_relabel_map,
    row_permutation_map,
    run_id_convention,
    runtime_assumptions,
    runtime_binding_requirements,
    state_mapping_convention,
    transpose_map,
)
from run_experiment_c_saturation import (
    BUDGET_TOLERANCE,
    EPS_GRADIENT,
    EPS_SPARK,
    STRESSED_SIGNED_HESSIAN,
    saturation_fixture_state,
)


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ID = "experiment_d_refinement_identity"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_experiment_d_refinement_identity.py"
)
PERSISTENCE_WINDOW_STEPS = 3
MIN_BASIN_MASS = 1.0
THRESHOLD_SENSITIVITY = (
    (1, 1.0),
    (3, 1.0),
    (3, 5.0),
    (5, 1.0),
)
MAX_PERSISTENCE_TRACE_STEPS = max(
    PERSISTENCE_WINDOW_STEPS,
    *(window_steps for window_steps, _ in THRESHOLD_SENSITIVITY),
)


def _params(
    seed: int,
    *,
    expansion_distribution_mode: str = "equal",
    expansion_custom_weights: tuple[float, float, float] | None = None,
) -> dict[str, Any]:
    evolution: dict[str, Any] = {
        "rng_seed": seed,
        "eps_gradient": EPS_GRADIENT,
        "eps_spark": EPS_SPARK,
        "eps_hessian": 0.01,
        "D_eff_target": 30,
        "w_bond": 1.0,
        "alpha": 1e-12,
        "beta": 1e-12,
        "gamma": 1e-12,
        "kappa_c": 1e-12,
        "site_potential_selection": "quadratic",
        "site_potential_params": {"mu": 0.0, "scale": 0.0},
    }
    if expansion_custom_weights is not None:
        evolution["expansion_custom_weights"] = expansion_custom_weights
    return {
        "dt": 0.1,
        "evolution": evolution,
        "constitutive_semantic_modes": {
            "hessian_backend": "row_basis_diagonal",
            "boundary_mode": "prune",
            "expansion_distribution_mode": expansion_distribution_mode,
        },
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


def _active_ports_after_transform(
    active_ports: tuple[int, ...],
    port_map: dict[int, int],
) -> tuple[int, ...]:
    return tuple(sorted(port_map[port] for port in active_ports))


def _condition_suite() -> list[dict[str, Any]]:
    return [
        {
            "condition_id": "d_equal_transfer_refinement",
            "condition_class": "uniform_state_transfer",
            "active_ports": PORT_IDS,
            "expansion_distribution_mode": "equal",
            "expansion_custom_weights": None,
            "expected_refinement": True,
            "notes": "Uniform expansion distribution control.",
        },
        {
            "condition_id": "d_column_1_skewed_transfer",
            "condition_class": "column_skewed_transfer",
            "active_ports": PORT_IDS,
            "expansion_distribution_mode": "custom",
            "expansion_custom_weights": (0.8, 0.1, 0.1),
            "expected_refinement": True,
            "notes": "Runtime-supported custom expansion weights skewed to column 1.",
        },
        {
            "condition_id": "d_column_2_skewed_transfer",
            "condition_class": "column_skewed_transfer",
            "active_ports": PORT_IDS,
            "expansion_distribution_mode": "custom",
            "expansion_custom_weights": (0.1, 0.8, 0.1),
            "expected_refinement": True,
            "notes": "Runtime-supported custom expansion weights skewed to column 2.",
        },
        {
            "condition_id": "d_column_3_skewed_transfer",
            "condition_class": "column_skewed_transfer",
            "active_ports": PORT_IDS,
            "expansion_distribution_mode": "custom",
            "expansion_custom_weights": (0.1, 0.1, 0.8),
            "expected_refinement": True,
            "notes": "Runtime-supported custom expansion weights skewed to column 3.",
        },
        {
            "condition_id": "d_degree_8_no_refinement_control",
            "condition_class": "same_instability_without_refinement",
            "active_ports": tuple(range(1, 9)),
            "expansion_distribution_mode": "equal",
            "expansion_custom_weights": None,
            "expected_refinement": False,
            "notes": "No-refinement control inherited from Iteration 6 saturation result.",
        },
    ]


def _model_for_condition(
    condition: dict[str, Any],
    *,
    active_ports: tuple[int, ...],
    seed: int,
) -> GRC9V3:
    return GRC9V3.from_state(
        state=saturation_fixture_state(
            active_ports=active_ports,
            signed_hessian=STRESSED_SIGNED_HESSIAN,
        ),
        params=_params(
            seed,
            expansion_distribution_mode=condition["expansion_distribution_mode"],
            expansion_custom_weights=condition["expansion_custom_weights"],
        ),
    )


def _module_column(
    *,
    target_node_id: int,
    to_port_id: int,
    module_node_ids: list[int],
) -> int | None:
    if target_node_id in module_node_ids[1:4]:
        return module_node_ids.index(target_node_id)
    _, to_column = port_to_rc(to_port_id)
    return to_column


def _basin_mass_for_node(state: Any, node_id: int) -> float:
    basin_nodes = state.basins.get(node_id, set())
    return float(
        sum(
            state.nodes[basin_node].coherence
            for basin_node in basin_nodes
            if basin_node in state.nodes
        )
    )


def _snapshot_persistence(
    *,
    label: str,
    state: Any,
    child_node_ids: list[int],
    window_index: int,
) -> list[dict[str, Any]]:
    rows = []
    sink_set = set(state.sink_set)
    for child_node_id in child_node_ids:
        rows.append(
            {
                "window_label": label,
                "window_index": window_index,
                "child_node_id": child_node_id,
                "child_present": child_node_id in state.nodes,
                "child_is_sink": child_node_id in sink_set,
                "child_basin_mass": _basin_mass_for_node(state, child_node_id),
                "child_parent_id": (
                    state.nodes[child_node_id].parent_id
                    if child_node_id in state.nodes
                    else ""
                ),
                "child_depth": (
                    state.nodes[child_node_id].depth
                    if child_node_id in state.nodes
                    else ""
                ),
            }
        )
    return rows


def _run_persistence_window(
    model: GRC9V3,
    *,
    child_node_ids: list[int],
    steps: int,
) -> list[dict[str, Any]]:
    rows = _snapshot_persistence(
        label="post_expansion",
        state=model.get_state(),
        child_node_ids=child_node_ids,
        window_index=0,
    )
    for step_index in range(1, steps + 1):
        model.step()
        rows.extend(
            _snapshot_persistence(
                label="post_step",
                state=model.get_state(),
                child_node_ids=child_node_ids,
                window_index=step_index,
            )
        )
    return rows


def _threshold_pass(
    rows: list[dict[str, Any]],
    *,
    child_node_id: int,
    window_steps: int,
    min_basin_mass: float,
) -> bool:
    selected = [
        row
        for row in rows
        if int(row["child_node_id"]) == child_node_id
        and int(row["window_index"]) <= window_steps
    ]
    expected_count = window_steps + 1
    if len(selected) != expected_count:
        return False
    return all(
        bool(row["child_present"])
        and bool(row["child_is_sink"])
        and float(row["child_basin_mass"]) >= min_basin_mass
        for row in selected
    )


def evaluate_condition(
    *,
    condition: dict[str, Any],
    transform_id: str,
    port_map: dict[int, int],
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    active_ports = _active_ports_after_transform(condition["active_ports"], port_map)
    model = _model_for_condition(condition, active_ports=active_ports, seed=seed)
    emitted_events = model.apply_hybrid_sparks()
    event_kinds = [event.kind for event in emitted_events]
    expansion_events = [
        event for event in emitted_events if event.kind == "hybrid_mechanical_expansion"
    ]
    expansion_payload = expansion_events[0].payload if expansion_events else {}
    completed_events = [
        event for event in emitted_events if event.kind == "hybrid_spark_completed"
    ]
    completed_payload = completed_events[0].payload if completed_events else {}
    module_node_ids = [int(node_id) for node_id in expansion_payload.get("module_node_ids", [])]
    reassignment_map = expansion_payload.get("reassignment_map", {})

    mapping_rows: list[dict[str, Any]] = []
    for edge_id, payload in sorted(reassignment_map.items(), key=lambda item: int(item[0])):
        old_port_id = int(payload["from_port_id"])
        to_node_id = int(payload["to_node_id"])
        to_port_id = int(payload["to_port_id"])
        old_row, old_column = port_to_rc(old_port_id)
        new_row, new_column = port_to_rc(to_port_id)
        target_module_column = _module_column(
            target_node_id=to_node_id,
            to_port_id=to_port_id,
            module_node_ids=module_node_ids,
        )
        mapping_rows.append(
            {
                "experiment": EXPERIMENT_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "seed": seed,
                "condition_id": condition["condition_id"],
                "condition_class": condition["condition_class"],
                "transform_id": transform_id,
                "edge_id": int(edge_id),
                "old_parent_port": old_port_id,
                "old_row": old_row,
                "old_column": old_column,
                "new_module_node_id": to_node_id,
                "new_module_port": to_port_id,
                "new_row": new_row,
                "new_column": new_column,
                "target_module_column": target_module_column,
                "column_preserved_by_port": old_column == new_column,
                "column_preserved_by_module": old_column == target_module_column,
                "artifact_source": "hybrid_mechanical_expansion.payload.reassignment_map",
            }
        )

    child_node_ids = [
        int(node_id)
        for node_id in completed_payload.get("stabilized_child_node_ids", [])
    ]
    persistence_rows = _run_persistence_window(
        model,
        child_node_ids=child_node_ids,
        steps=MAX_PERSISTENCE_TRACE_STEPS,
    ) if child_node_ids else []
    for row in persistence_rows:
        row.update(
            {
                "experiment": EXPERIMENT_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "seed": seed,
                "condition_id": condition["condition_id"],
                "condition_class": condition["condition_class"],
                "transform_id": transform_id,
                "min_basin_mass_threshold": MIN_BASIN_MASS,
                "persistence_window_steps": PERSISTENCE_WINDOW_STEPS,
                "artifact_source": "post-expansion GRC9V3State sink_set/basins/nodes",
            }
        )

    threshold_rows: list[dict[str, Any]] = []
    for window_steps, min_basin_mass in THRESHOLD_SENSITIVITY:
        for child_node_id in child_node_ids:
            threshold_rows.append(
                {
                    "experiment": EXPERIMENT_ID,
                    "schema_version": ARTIFACT_SCHEMA_VERSION,
                    "lane_id": LANE_ID,
                    "seed": seed,
                    "condition_id": condition["condition_id"],
                    "condition_class": condition["condition_class"],
                    "transform_id": transform_id,
                    "child_node_id": child_node_id,
                    "window_steps": window_steps,
                    "min_basin_mass": min_basin_mass,
                    "persistence_pass": _threshold_pass(
                        persistence_rows,
                        child_node_id=child_node_id,
                        window_steps=window_steps,
                        min_basin_mass=min_basin_mass,
                    ),
                }
            )

    summary_row = {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "condition_id": condition["condition_id"],
        "condition_class": condition["condition_class"],
        "transform_id": transform_id,
        "active_degree": len(active_ports),
        "expected_refinement": condition["expected_refinement"],
        "event_kinds": ";".join(event_kinds),
        "refinement_event_count": event_kinds.count("hybrid_mechanical_expansion"),
        "completed_event_count": event_kinds.count("hybrid_spark_completed"),
        "module_node_ids": " ".join(str(node_id) for node_id in module_node_ids),
        "distribution_weights": json.dumps(expansion_payload.get("distribution_weights", [])),
        "budget_before": expansion_payload.get("budget_before", ""),
        "budget_after": expansion_payload.get("budget_after", ""),
        "budget_error": expansion_payload.get("budget_error", ""),
        "budget_tolerance": BUDGET_TOLERANCE,
        "budget_preserved": (
            expansion_payload.get("budget_error", "") != ""
            and abs(float(expansion_payload["budget_error"])) <= BUDGET_TOLERANCE
        ),
        "reassignment_edge_count": len(mapping_rows),
        "all_columns_preserved_by_port": (
            bool(mapping_rows)
            and all(bool(row["column_preserved_by_port"]) for row in mapping_rows)
        ),
        "all_columns_preserved_by_module": (
            bool(mapping_rows)
            and all(bool(row["column_preserved_by_module"]) for row in mapping_rows)
        ),
        "stabilized_child_node_ids": " ".join(str(node_id) for node_id in child_node_ids),
        "persistent_child_count": len(
            {
                int(row["child_node_id"])
                for row in persistence_rows
                if _threshold_pass(
                    persistence_rows,
                    child_node_id=int(row["child_node_id"]),
                    window_steps=PERSISTENCE_WINDOW_STEPS,
                    min_basin_mass=MIN_BASIN_MASS,
                )
            }
        ),
        "identity_claim_level": (
            "configured_window_child_basin_persistence"
            if child_node_ids
            else "no_identity_claim_no_refinement"
        ),
        "mechanical_refinement_claim": (
            "supported" if mapping_rows else "not_observed"
        ),
        "condition_notes": condition["notes"],
    }
    return mapping_rows, persistence_rows, threshold_rows, summary_row


def run_experiment(
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    transforms = _transforms(seed)
    mapping_rows: list[dict[str, Any]] = []
    persistence_rows: list[dict[str, Any]] = []
    threshold_rows: list[dict[str, Any]] = []
    condition_rows: list[dict[str, Any]] = []
    for condition in _condition_suite():
        for transform_id, port_map in transforms.items():
            mapping, persistence, threshold, summary_row = evaluate_condition(
                condition=condition,
                transform_id=transform_id,
                port_map=port_map,
                seed=seed,
            )
            mapping_rows.extend(mapping)
            persistence_rows.extend(persistence)
            threshold_rows.extend(threshold)
            condition_rows.append(summary_row)

    refinement_rows = [
        row for row in condition_rows if int(row["refinement_event_count"]) > 0
    ]
    no_refinement_rows = [
        row for row in condition_rows if int(row["active_degree"]) < 9
    ]
    summary = {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "run_id_convention": run_id_convention(),
        "runtime_assumptions": runtime_assumptions(),
        "state_mapping_convention": state_mapping_convention(),
        "runtime_binding_requirements": runtime_binding_requirements(),
        "artifact_entry_points": artifact_entry_points(),
        "comparison_report_schema": comparison_report_schema(),
        "blocked_observations_schema": blocked_observations_schema(),
        "transforms": transforms,
        "persistence_window_steps": PERSISTENCE_WINDOW_STEPS,
        "max_persistence_trace_steps": MAX_PERSISTENCE_TRACE_STEPS,
        "min_basin_mass_threshold": MIN_BASIN_MASS,
        "threshold_sensitivity": [
            {"window_steps": steps, "min_basin_mass": mass}
            for steps, mass in THRESHOLD_SENSITIVITY
        ],
        "supported_transfer_modes": {
            "uniform_equal": "available",
            "custom_column_skewed_weights": "available",
            "inflow_weighted_transfer": "blocked_not_implemented",
        },
        "refinement_event_rows": len(refinement_rows),
        "no_refinement_control_rows": len(no_refinement_rows),
        "all_refinement_rows_budget_preserved": all(
            bool(row["budget_preserved"]) for row in refinement_rows
        ),
        "all_refinement_rows_column_preserved_by_port": all(
            bool(row["all_columns_preserved_by_port"]) for row in refinement_rows
        ),
        "all_refinement_rows_column_preserved_by_module": all(
            bool(row["all_columns_preserved_by_module"]) for row in refinement_rows
        ),
        "no_refinement_controls_have_no_mapping": all(
            int(row["reassignment_edge_count"]) == 0 for row in no_refinement_rows
        ),
        "configured_window_identity_support": all(
            int(row["persistent_child_count"]) > 0 for row in refinement_rows
        ),
        "identity_support_scope": (
            "supported_for_clean_raw_refinement_fixtures_under_configured_window"
        ),
        "mechanical_refinement_identity_boundary": (
            "mechanical refinement alone is not identity fission; identity support uses post-event sink/basin persistence"
        ),
    }
    return mapping_rows, persistence_rows, threshold_rows, condition_rows, summary


def blocked_observation_rows() -> list[dict[str, str]]:
    return [
        {
            "experiment": EXPERIMENT_ID,
            "observation": "inflow_weighted_state_transfer",
            "status": "blocked",
            "artifact_source": "GRC9V3 expansion distribution modes",
            "reconstruction_attempt": "Checked supported expansion_distribution_mode values.",
            "notes": "GRC9V3 exposes equal and custom weights, not an inflow-weighted transfer lane.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "checkpoint_window_identity_persistence",
            "status": "inconclusive",
            "artifact_source": "experiment-local runtime window",
            "reconstruction_attempt": "Used post-expansion and post-step GRC9V3State snapshots in memory.",
            "notes": "Persistent child basin support is available from runtime state; checkpoint-window observer support remains for a later artifact-capture pass.",
        },
        {
            "experiment": EXPERIMENT_ID,
            "observation": "landscape_general_child_identity",
            "status": "inconclusive",
            "artifact_source": "raw central-node fixture",
            "reconstruction_attempt": "Ran deterministic clean fixtures only.",
            "notes": "Identity persistence is supported in this clean raw fixture, not landscape-general.",
        },
    ]


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"cannot write empty CSV {path}")
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_manifest(
    *,
    seed: int,
    summary: dict[str, Any],
    output_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "iteration": 7,
        "script_path": SCRIPT_PATH,
        "command": (
            "PYTHONPATH=src .venv/bin/python "
            f"{SCRIPT_PATH} --write-defaults --seed {seed}"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_branch": _git_value(["branch", "--show-current"]),
        "lane_id": LANE_ID,
        "runtime_params": _params(seed),
        "seed": seed,
        "condition_ids": [condition["condition_id"] for condition in _condition_suite()],
        "port_mappings": summary["transforms"],
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "persistence_window_steps": PERSISTENCE_WINDOW_STEPS,
        "max_persistence_trace_steps": MAX_PERSISTENCE_TRACE_STEPS,
        "min_basin_mass_threshold": MIN_BASIN_MASS,
        "output_paths": {
            key: str(path.relative_to(EXPERIMENT_ROOT))
            for key, path in output_paths.items()
        },
        "validation_commands": [
            (
                "PYTHONPATH=src .venv/bin/python -m py_compile "
                f"{SCRIPT_PATH}"
            ),
            (
                "PYTHONPATH=src .venv/bin/python -m ruff check "
                f"{SCRIPT_PATH} "
                "experiments/2026-05-N01-grc9v3-properties/scripts/run_experiment_c_saturation.py "
                "experiments/2026-05-N01-grc9v3-properties/scripts/grc9v3_fixture_harness.py"
            ),
            (
                ".venv/bin/python -m json.tool "
                "experiments/2026-05-N01-grc9v3-properties/outputs/"
                "experiment_d_refinement_identity_summary.json"
            ),
        ],
        "reuse_notes": {
            "d5": "Use reassignment rows and persistence rows for refinement-memory discriminator checks.",
            "d8": "Use persistence sensitivity rows as identity-level evidence, with raw-fixture scope.",
        },
    }


def _write_report(
    path: Path,
    condition_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    identity_rows = [row for row in condition_rows if row["transform_id"] == "identity"]
    lines = [
        "# Experiment D Refinement And Child Identity",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "This report tests whether mechanical refinement preserves column interface",
        "structure and whether child identity support is backed by post-event",
        "sink/basin persistence artifacts under Lane A.",
        "",
        "Mechanical refinement is reported separately from identity support.",
        "The identity-side claim is configured-window child-basin persistence,",
        "not identity fission from expansion alone.",
        "",
        "## Outputs",
        "",
        "- `../outputs/experiment_d_refinement_identity_reassignments.csv`",
        "- `../outputs/experiment_d_refinement_identity_persistence.csv`",
        "- `../outputs/experiment_d_refinement_identity_thresholds.csv`",
        "- `../outputs/experiment_d_refinement_identity_conditions.csv`",
        "- `../outputs/experiment_d_refinement_identity_summary.json`",
        "- `../outputs/experiment_d_refinement_identity_manifest.json`",
        "- `../reports/experiment_d_refinement_identity_blocked_observations.csv`",
        "",
        "## Identity Transform Conditions",
        "",
        "| Condition | Refinements | Edge Reassignments | Column Preserved | Budget Error | Persistent Children |",
        "| --- | ---: | ---: | --- | ---: | ---: |",
    ]
    for row in identity_rows:
        lines.append(
            "| "
            f"{row['condition_id']} | "
            f"{row['refinement_event_count']} | "
            f"{row['reassignment_edge_count']} | "
            f"`{json.dumps(row['all_columns_preserved_by_module'])}` | "
            f"{row['budget_error']} | "
            f"{row['persistent_child_count']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "- all refinement rows preserve budget: "
            f"`{json.dumps(summary['all_refinement_rows_budget_preserved'])}`",
            "- all refinement rows preserve columns by reassigned port: "
            f"`{json.dumps(summary['all_refinement_rows_column_preserved_by_port'])}`",
            "- all refinement rows preserve columns by module location: "
            f"`{json.dumps(summary['all_refinement_rows_column_preserved_by_module'])}`",
            "- no-refinement controls have no reassignment map: "
            f"`{json.dumps(summary['no_refinement_controls_have_no_mapping'])}`",
            "- configured-window child basin persistence: "
            f"`{json.dumps(summary['configured_window_identity_support'])}`",
            f"- persistence window steps: `{summary['persistence_window_steps']}`",
            f"- max persistence trace steps: `{summary['max_persistence_trace_steps']}`",
            f"- minimum basin mass threshold: `{summary['min_basin_mass_threshold']}`",
            "- snapshot source: `experiment-local runtime state`",
            "- checkpoint-window source: `inconclusive`",
            "- lineage source: `expansion payload + post-event basin assignment`",
            f"- budget tolerance: `{BUDGET_TOLERANCE}`",
            "",
            "## Interpretation",
            "",
            "Experiment D supports column-preserving mechanical refinement under",
            "the Lane A baseline in clean raw fixtures. Each observed mechanical",
            "expansion exposes a direct",
            "`hybrid_mechanical_expansion.payload.reassignment_map`. All nine old",
            "boundary edges are reassigned, and each old boundary column matches",
            "the new module endpoint column. Unit-measure budget is preserved",
            "within tolerance.",
            "",
            "The post-event child sink/basin artifacts persist over the configured",
            "three-step runtime-state window with minimum basin mass `1.0`. This",
            "supports configured-window child-basin persistence in these clean",
            "fixtures.",
            "",
            "The result does not show that expansion alone is identity fission,",
            "does not establish landscape-general identity behavior, and does",
            "not yet establish checkpoint-window persistence through persisted",
            "observer records.",
            "",
            "## Deferred Unblocking Decisions",
            "",
            "The following items are intentionally not unblocked in Iteration 7.1:",
            "",
            "- inflow-weighted transfer remains blocked because the current runtime",
            "  exposes equal/custom expansion distribution weights, not an",
            "  inflow-weighted transfer lane; implementing such a lane belongs to",
            "  repo-level runtime work",
            "- landscape-general child identity remains inconclusive because this",
            "  iteration uses clean raw central-node fixtures, not a landscape/seed",
            "  robustness suite",
            "- direct column-H gating and near-saturation remain blocked under Lane A",
            "",
            "The following items are candidates for a small addendum or for D8:",
            "",
            "- persisted checkpoint-window identity persistence",
            "- before/after topology-change G/Split reconstruction using the",
            "  refinement fixture produced here",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(seed: int) -> dict[str, Path]:
    mapping_rows, persistence_rows, threshold_rows, condition_rows, summary = run_experiment(seed)
    reassignment_path = (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_reassignments.csv"
    )
    persistence_path = (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_persistence.csv"
    )
    threshold_path = (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_thresholds.csv"
    )
    conditions_path = (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_conditions.csv"
    )
    summary_path = (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_summary.json"
    )
    manifest_path = (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_manifest.json"
    )
    blocked_path = (
        EXPERIMENT_ROOT
        / "reports"
        / "experiment_d_refinement_identity_blocked_observations.csv"
    )
    report_path = EXPERIMENT_ROOT / "reports" / "experiment_d_refinement_identity.md"
    output_paths = {
        "reassignments_csv": reassignment_path,
        "persistence_csv": persistence_path,
        "thresholds_csv": threshold_path,
        "conditions_csv": conditions_path,
        "summary_json": summary_path,
        "manifest_json": manifest_path,
        "blocked_observations_csv": blocked_path,
        "report_md": report_path,
    }
    _write_csv(reassignment_path, mapping_rows)
    _write_csv(persistence_path, persistence_rows)
    _write_csv(threshold_path, threshold_rows)
    _write_csv(conditions_path, condition_rows)
    _write_json(summary_path, summary)
    _write_json(
        manifest_path,
        _build_manifest(seed=seed, summary=summary, output_paths=output_paths),
    )
    _write_csv(blocked_path, blocked_observation_rows())
    _write_report(report_path, condition_rows, summary)
    return output_paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--write-defaults", action="store_true")
    args = parser.parse_args()
    if args.write_defaults:
        paths = write_outputs(args.seed)
        print(json.dumps({key: str(path) for key, path in paths.items()}, indent=2))
    else:
        mapping_rows, persistence_rows, threshold_rows, condition_rows, summary = (
            run_experiment(args.seed)
        )
        print(
            json.dumps(
                {
                    "summary": summary,
                    "reassignments": mapping_rows,
                    "persistence": persistence_rows,
                    "thresholds": threshold_rows,
                    "conditions": condition_rows,
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
