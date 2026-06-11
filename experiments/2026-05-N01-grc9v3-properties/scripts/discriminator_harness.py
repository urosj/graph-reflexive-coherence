"""Shared discriminator harness schema for D1-D8.

This module is experiment-local. It defines shared record contracts and writes
the Iteration 1 harness artifacts without changing runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from grc9v3_fixture_harness import ARTIFACT_SCHEMA_VERSION, LANE_ID


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "discriminator_harness.py"
)

EVIDENCE_LABELS = ("direct", "derived", "partial", "blocked", "inconclusive")
CLASSIFICATIONS = ("supported", "weakened", "refuted", "blocked", "inconclusive")
TRANSFORM_CLASSES = (
    "identity",
    "row_permutation",
    "column_permutation",
    "row_column_permutation",
    "row_column_transpose",
    "degree_preserving_s9_relabel",
    "random_triple_regrouping",
)


def run_record_schema() -> dict[str, str]:
    return {
        "discriminator_id": "D1-D8 id such as d1_factorization",
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "fixture_id": "stable fixture id",
        "run_id": "stable run id",
        "seed": "integer seed",
        "transform_id": "identity or named transform",
        "artifact_class": "row, column, port, event, path, basin, or refinement class",
        "evidence_label": "direct | derived | partial | blocked | inconclusive",
        "artifact_source": "input file, runtime field, event payload, or derived formula",
        "classification": "supported | weakened | refuted | blocked | inconclusive",
        "notes": "claim boundary and caveats",
    }


def fixture_description_schema() -> dict[str, str]:
    return {
        "fixture_id": "stable fixture id",
        "source_experiment": "O-style or D-style source",
        "condition_id": "condition id where applicable",
        "active_ports": "space-separated canonical port ids",
        "expected_behavior": "declared expectation before scoring",
        "artifact_inputs": "source rows/reports/events used by discriminator",
    }


def transform_metadata_schema() -> dict[str, str]:
    return {
        "transform_id": "stable transform id",
        "transform_class": "one of transform_classes",
        "port_map": "source port to target port mapping",
        "inverse_port_map": "target port to source port mapping",
        "preserves_row_column_factorization": "boolean",
        "preserves_degree": "boolean",
        "semantic_interpretability": "canonical | transpose | non_factorized",
    }


def artifact_extraction_registry() -> dict[str, dict[str, str]]:
    return {
        "row_differential_signature": {
            "primary_sources": "Experiment A rows; GRC9V3State/cached row artifacts",
            "evidence_label": "derived",
        },
        "derived_column_proxy": {
            "primary_sources": "Experiment B rows; endpoint ports and conductance/coherence/flux",
            "evidence_label": "derived",
        },
        "lane_a_saturation_gate": {
            "primary_sources": "Experiment C rows; spark candidates and event payloads",
            "evidence_label": "direct",
        },
        "refinement_reassignment": {
            "primary_sources": "Experiment D reassignment rows; expansion payload",
            "evidence_label": "direct",
        },
        "coarse_split_reconstruction": {
            "primary_sources": "Experiment E reconstruction rows and summary",
            "evidence_label": "direct",
        },
        "path_label_selection": {
            "primary_sources": "Experiment F edge/path/criteria rows",
            "evidence_label": "direct",
        },
        "motion_port_history": {
            "primary_sources": "Experiment G checkpoint-overlay port history",
            "evidence_label": "partial",
        },
        "identity_persistence": {
            "primary_sources": "Experiment D persistence rows; later D8 windows",
            "evidence_label": "partial",
        },
    }


def blocked_observation_schema() -> dict[str, str]:
    return {
        "discriminator_id": "D1-D8 id",
        "observation": "claim-specific observation",
        "status": "blocked | inconclusive",
        "artifact_source": "attempted artifact surface",
        "reconstruction_attempt": "short extraction/reconstruction note",
        "notes": "why no stronger claim is made",
    }


def manifest_schema() -> dict[str, str]:
    return {
        "discriminator_id": "D1-D8 id",
        "iteration": "checklist iteration number",
        "script_path": "script that generated outputs",
        "command": "reproducible command",
        "git_commit": "repository commit",
        "lane_id": LANE_ID,
        "fixture_id": "or row-level fixture ids if multiple",
        "transform_id": "or list of transform ids if multiple",
        "seed": "integer seed",
        "runtime_params": "runtime params or reused-output declaration",
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_source_map": "input files and runtime surfaces",
        "output_paths": "generated output paths",
    }


def expected_outputs() -> dict[str, list[str]]:
    return {
        "D1": [
            "outputs/d1_equivariance_matrix.csv",
            "reports/d1_artifact_distance_report.md",
            "outputs/d1_transform_pair_records.jsonl",
            "reports/d1_blocked_observations.md",
        ],
        "D2_schema": [
            "reports/d2_target_definitions.md",
            "reports/d2_blocked_observations.md",
        ],
        "D2_scoring": [
            "outputs/d2_feature_family_scores.csv",
            "reports/d2_cross_validation_report.md",
            "outputs/d2_random_grouping_controls.csv",
            "reports/d2_blocked_observations.md",
        ],
        "D3": [
            "outputs/d3_transpose_pair_scores.csv",
            "reports/d3_role_separation_report.md",
            "outputs/d3_control_patterns.csv",
            "reports/d3_blocked_observations.md",
        ],
        "D4": [
            "outputs/d4_saturation_gate_table.csv",
            "reports/d4_saturation_report.md",
            "reports/d4_blocked_observations.md",
        ],
        "D5": [
            "outputs/d5_interface_memory_edges.csv",
            "reports/d5_interface_memory_report.md",
            "outputs/d5_random_column_controls.csv",
            "reports/d5_blocked_observations.md",
        ],
        "D6": [
            "outputs/d6_interaction_model_scores.csv",
            "reports/d6_port_interaction_report.md",
            "reports/d6_blocked_observations.md",
        ],
        "D7": [
            "outputs/d7_reconstruction_errors.csv",
            "reports/d7_multiscale_report.md",
            "outputs/d7_signed_flux_controls.csv",
            "outputs/d7_grouping_semantic_comparison.csv",
            "reports/d7_blocked_observations.md",
        ],
        "D8": [
            "outputs/d8_identity_emergence_windows.csv",
            "reports/d8_identity_emergence_report.md",
            "outputs/d8_negative_controls.csv",
            "reports/d8_blocked_observations.md",
        ],
    }


def harness_schema() -> dict[str, Any]:
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "script_path": SCRIPT_PATH,
        "runtime_mutation_policy": "experiment-local only; do not mutate src/pygrc",
        "evidence_labels": EVIDENCE_LABELS,
        "classifications": CLASSIFICATIONS,
        "transform_classes": TRANSFORM_CLASSES,
        "run_record_schema": run_record_schema(),
        "fixture_description_schema": fixture_description_schema(),
        "transform_metadata_schema": transform_metadata_schema(),
        "artifact_extraction_registry": artifact_extraction_registry(),
        "blocked_observation_schema": blocked_observation_schema(),
        "manifest_schema": manifest_schema(),
        "expected_outputs": expected_outputs(),
        "d2_schema_scoring_split": {
            "schema_iteration": "Iteration 3",
            "scoring_iteration": "Iteration 10",
            "rule": "Do not run final D2 scoring until enough O-style and D-style rows exist.",
        },
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_report(path: Path, schema: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Shared Discriminator Harness",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "This harness defines shared D1-D8 record contracts, evidence labels,",
        "classification labels, transform metadata, manifest fields, blocked",
        "observation format, artifact extraction registry, and expected outputs.",
        "",
        "It is experiment-local and does not change `src/pygrc` runtime behavior.",
        "",
        "## Evidence Labels",
        "",
    ]
    for label in schema["evidence_labels"]:
        lines.append(f"- `{label}`")
    lines.extend(
        [
            "",
            "## Manifest Required Fields",
            "",
        ]
    )
    for field_name in schema["manifest_schema"]:
        lines.append(f"- `{field_name}`")
    lines.extend(
        [
            "",
            "## Artifact Registry",
            "",
            "| Artifact Class | Evidence Label | Primary Sources |",
            "| --- | --- | --- |",
        ]
    )
    for artifact_class, entry in schema["artifact_extraction_registry"].items():
        lines.append(
            "| "
            f"{artifact_class} | "
            f"{entry['evidence_label']} | "
            f"{entry['primary_sources']} |"
        )
    lines.extend(
        [
            "",
            "## D2 Split",
            "",
            "D2 schema definition and D2 scoring are intentionally separate.",
            "Iteration 3 defines targets and feature families; Iteration 10 runs",
            "scoring only after enough O-style and D-style run data exist.",
            "",
            "## Output Coverage",
            "",
            "The machine-readable schema lists expected outputs for D1-D8 and can",
            "represent the current D1 outputs.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs() -> dict[str, Path]:
    schema = harness_schema()
    schema_path = EXPERIMENT_ROOT / "outputs" / "discriminator_harness_schema.json"
    report_path = EXPERIMENT_ROOT / "reports" / "discriminator_harness.md"
    _write_json(schema_path, schema)
    _write_report(report_path, schema)
    return {
        "schema_json": schema_path,
        "report_md": report_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-defaults", action="store_true")
    args = parser.parse_args()
    if args.write_defaults:
        paths = write_outputs()
        print(json.dumps({key: str(path) for key, path in paths.items()}, indent=2))
    else:
        print(json.dumps(harness_schema(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
