"""D2 schema-only pass for predictive role separation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from discriminator_harness import EVIDENCE_LABELS, expected_outputs, manifest_schema
from grc9v3_fixture_harness import ARTIFACT_SCHEMA_VERSION, LANE_ID


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DISCRIMINATOR_ID = "d2_predictive_role_separation_schema"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_discriminator_d2_schema.py"
)


def feature_families() -> list[dict[str, Any]]:
    return [
        {
            "feature_family": "degree_adjacency_baseline",
            "role": "H0 baseline",
            "features": [
                "active_degree",
                "incident_edge_count",
                "neighbor_count",
                "conductance_sum",
                "absolute_flux_sum",
                "graph_distance_or_path_membership_where_available",
            ],
            "evidence_label": "direct",
            "source_artifacts": "topology, PortEdge records, edge labels",
        },
        {
            "feature_family": "row",
            "role": "geometric/differential predictor",
            "features": [
                "row_id",
                "row occupancy",
                "row perturbation energy",
                "row-resolved gradient or mismatch response",
                "row-resolved tensor/diagonal signature where available",
            ],
            "evidence_label": "derived",
            "source_artifacts": "Experiment A rows, port_to_rc, state/cached row artifacts",
        },
        {
            "feature_family": "column",
            "role": "interface/refinement/multiscale predictor",
            "features": [
                "column_id",
                "column occupancy",
                "column cancellation score",
                "column pressure proxy",
                "refinement reassignment column",
                "G/Split column profile",
            ],
            "evidence_label": "derived",
            "source_artifacts": "Experiments B, D, E; endpoint ports and expansion payloads",
        },
        {
            "feature_family": "port",
            "role": "edge-local and row-column intersection predictor",
            "features": [
                "port_id",
                "row_id",
                "column_id",
                "port occupancy",
                "port-local flux",
                "dominant port over window",
                "old/new refinement port mapping",
            ],
            "evidence_label": "direct",
            "source_artifacts": "PortEdge records, Experiments D, F, G",
        },
        {
            "feature_family": "random_grouping",
            "role": "negative semantic grouping control",
            "features": [
                "random triple id",
                "non-factorized S9 group id",
                "random grouped occupancy",
                "random grouped score aggregates",
            ],
            "evidence_label": "derived",
            "source_artifacts": "shared transform harness and D1 non-factorized controls",
        },
    ]


def target_classes() -> list[dict[str, Any]]:
    return [
        {
            "target_class": "geometric_differential",
            "example_targets": [
                "K anisotropy",
                "row-resolved gradient response",
                "row-resolved flux stress",
                "Hessian-like row signature",
            ],
            "expected_strongest_family": "row",
            "current_sources": "Experiment A rows",
            "scoring_status": "schema_defined_scoring_deferred",
        },
        {
            "target_class": "interface_routing_refinement",
            "example_targets": [
                "column cancellation",
                "boundary pressure",
                "spark eligibility",
                "spark/refinement event",
                "boundary edge reassignment",
                "post-refinement routing role",
            ],
            "expected_strongest_family": "column",
            "current_sources": "Experiments B, C, D",
            "scoring_status": "schema_defined_scoring_deferred",
        },
        {
            "target_class": "edge_local",
            "example_targets": [
                "dominant port",
                "flux reversal",
                "strongest edge",
                "path membership",
                "route class",
            ],
            "expected_strongest_family": "port",
            "current_sources": "Experiments F, G",
            "scoring_status": "schema_defined_scoring_deferred",
        },
        {
            "target_class": "generic_activity",
            "example_targets": [
                "active degree",
                "total flux magnitude",
                "ordinary sink status",
                "local coherence accumulation",
            ],
            "expected_strongest_family": "degree_adjacency_baseline",
            "current_sources": "A-G summaries and topology rows",
            "scoring_status": "schema_defined_scoring_deferred",
        },
        {
            "target_class": "identity_level_persistence",
            "example_targets": [
                "sink status",
                "basin assignment",
                "child-basin persistence",
                "attractor-count change",
            ],
            "expected_strongest_family": "port_plus_column_plus_global_basin_context",
            "current_sources": "Experiment D persistence rows; later D8 windows",
            "scoring_status": "partial_until_D8",
        },
    ]


def controls() -> list[dict[str, str]]:
    return [
        {
            "control": "random_row_triples",
            "purpose": "test true row grouping against arbitrary triples",
        },
        {
            "control": "random_column_triples",
            "purpose": "test true column grouping against arbitrary triples",
        },
        {
            "control": "arbitrary_s9_port_relabeling",
            "purpose": "test anonymous-port null against structured features",
        },
        {
            "control": "degree_only_features",
            "purpose": "test whether ordinary graph structure explains all targets",
        },
        {
            "control": "shuffled_target_labels",
            "purpose": "detect spurious predictive signal",
        },
        {
            "control": "cross_validation_by_fixture",
            "purpose": "avoid memorizing one fixture or transform family",
        },
    ]


def scoring_contract() -> dict[str, Any]:
    return {
        "allowed_methods": [
            "linear_or_ridge_regression_for_scalar_targets",
            "logistic_regression_for_binary_targets",
            "multinomial_logistic_regression_for_categorical_targets",
            "decision_stumps_or_shallow_trees",
            "mutual_information_for_small_datasets",
            "rank_correlation_for_monotonic_relationships",
        ],
        "primary_split": "cross_validation_by_fixture",
        "comparison_rule": (
            "compare feature-family performance by target class against "
            "degree/adjacency and random grouping controls"
        ),
        "scoring_readiness": {
            "status": "blocked_until_enough_completed_run_data_exist",
            "minimum_inputs": [
                "O-style A-G rows",
                "D1 factorization rows",
                "at least one additional D-style target family beyond D1",
            ],
            "late_scoring_iteration": "Discriminator checklist Iteration 10",
        },
    }


def schema_payload() -> dict[str, Any]:
    return {
        "discriminator_id": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "script_path": SCRIPT_PATH,
        "harness_schema": "outputs/discriminator_harness_schema.json",
        "feature_families": feature_families(),
        "target_classes": target_classes(),
        "controls": controls(),
        "scoring_contract": scoring_contract(),
        "blocked_observation_rules": {
            "missing_feature_family": "mark family blocked for that target",
            "missing_target_artifact": "mark target blocked",
            "insufficient_fixture_count": "mark scoring inconclusive",
            "source_intent_only": "do not promote to supported evidence",
        },
        "expected_outputs_schema_phase": expected_outputs()["D2_schema"],
        "expected_outputs_scoring_phase": expected_outputs()["D2_scoring"],
        "manifest_required_fields": list(manifest_schema()),
        "evidence_labels": list(EVIDENCE_LABELS),
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D2 Predictive Role Separation Target Definitions",
        "",
        "Status: schema complete; final scoring deferred.",
        "",
        "## Scope",
        "",
        "This D2 pass defines feature families, target classes, controls, scoring",
        "contracts, blocked-observation rules, and output schemas. It does not",
        "run predictive scoring.",
        "",
        "## Feature Families",
        "",
        "| Family | Role | Evidence | Source Artifacts |",
        "| --- | --- | --- | --- |",
    ]
    for family in payload["feature_families"]:
        lines.append(
            "| "
            f"{family['feature_family']} | "
            f"{family['role']} | "
            f"{family['evidence_label']} | "
            f"{family['source_artifacts']} |"
        )
    lines.extend(
        [
            "",
            "## Target Classes",
            "",
            "| Target Class | Expected Strongest Family | Current Sources | Status |",
            "| --- | --- | --- | --- |",
        ]
    )
    for target in payload["target_classes"]:
        lines.append(
            "| "
            f"{target['target_class']} | "
            f"{target['expected_strongest_family']} | "
            f"{target['current_sources']} | "
            f"{target['scoring_status']} |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
        ]
    )
    for control in payload["controls"]:
        lines.append(f"- `{control['control']}`: {control['purpose']}")
    lines.extend(
        [
            "",
            "## Scoring Contract",
            "",
            f"- primary split: `{payload['scoring_contract']['primary_split']}`",
            f"- scoring status: `{payload['scoring_contract']['scoring_readiness']['status']}`",
            "- final scoring belongs to discriminator checklist Iteration 10.",
            "",
            "## Blocked Rules",
            "",
        ]
    )
    for key, value in payload["blocked_observation_rules"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "D2 scoring is blocked in this iteration by design. This pass only",
            "defines the schema so later D3-D8 outputs can conform to one target",
            "and feature-family contract.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_blocked(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D2 Blocked Observations",
        "",
        "| Observation | Status | Artifact Source | Notes |",
        "| --- | --- | --- | --- |",
        "| final predictive scoring | blocked | D2 schema only | Final scoring is intentionally deferred until enough O-style and D-style rows exist. |",
        "| identity-level predictive scoring | partial | Experiment D persistence rows; future D8 windows | Identity-level targets require stricter D8 outcome windows before final scoring. |",
        "| reusable held-out discriminator dataset | inconclusive | D1 plus O-style rows | More D-style target families should be added before the late D2 scoring pass. |",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs() -> dict[str, Path]:
    payload = schema_payload()
    schema_path = EXPERIMENT_ROOT / "outputs" / "d2_predictive_role_schema.json"
    report_path = EXPERIMENT_ROOT / "reports" / "d2_target_definitions.md"
    blocked_path = EXPERIMENT_ROOT / "reports" / "d2_blocked_observations.md"
    _write_json(schema_path, payload)
    _write_report(report_path, payload)
    _write_blocked(blocked_path)
    return {
        "schema_json": schema_path,
        "target_definitions_md": report_path,
        "blocked_observations_md": blocked_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-defaults", action="store_true")
    args = parser.parse_args()
    if args.write_defaults:
        paths = write_outputs()
        print(json.dumps({key: str(path) for key, path in paths.items()}, indent=2))
    else:
        print(json.dumps(schema_payload(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
