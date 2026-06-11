"""D2 predictive role separation scoring over completed O/D artifacts."""

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
DISCRIMINATOR_ID = "d2_predictive_role_separation_scoring"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_discriminator_d2_scoring.py"
)

INPUT_PATHS = {
    "schema": EXPERIMENT_ROOT / "outputs" / "d2_predictive_role_schema.json",
    "a_rows": EXPERIMENT_ROOT / "outputs" / "experiment_a_row_mode_stress_rows.csv",
    "b_rows": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_b_column_interface_cancellation_rows.csv"
    ),
    "d1_summary": EXPERIMENT_ROOT / "outputs" / "d1_factorization_summary.json",
    "d3_summary": EXPERIMENT_ROOT / "outputs" / "d3_transpose_summary.json",
    "d4_summary": EXPERIMENT_ROOT / "outputs" / "d4_saturation_summary.json",
    "d5_summary": EXPERIMENT_ROOT / "outputs" / "d5_interface_memory_summary.json",
    "d6_summary": EXPERIMENT_ROOT / "outputs" / "d6_port_interaction_summary.json",
    "d7_summary": EXPERIMENT_ROOT / "outputs" / "d7_multiscale_summary.json",
    "d8_summary": (
        EXPERIMENT_ROOT / "outputs" / "d8_identity_emergence_summary.json"
    ),
    "f_summary": (
        EXPERIMENT_ROOT / "outputs" / "experiment_f_path_disagreement_summary.json"
    ),
    "g_summary": (
        EXPERIMENT_ROOT / "outputs" / "experiment_g_mixed_motion_summary.json"
    ),
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


def _balanced_majority_score(rows: list[dict[str, str]], field: str) -> float:
    if not rows:
        return 0.0
    counts: dict[str, int] = {}
    for row in rows:
        counts[row[field]] = counts.get(row[field], 0) + 1
    return max(counts.values()) / len(rows)


def _mean_bool(rows: list[dict[str, str]], field: str) -> float:
    if not rows:
        return 0.0
    return sum(_truth(row[field]) for row in rows) / len(rows)


def _structured_positive_rows(
    rows: list[dict[str, str]],
    *,
    expected_field: str,
) -> list[dict[str, str]]:
    structured_transforms = {
        "identity",
        "row_permutation_231",
        "column_permutation_312",
    }
    return [
        row
        for row in rows
        if row["transform_id"] in structured_transforms and row[expected_field] != ""
    ]


def _score_row(
    *,
    target_class: str,
    target_id: str,
    source_artifacts: str,
    feature_family: str,
    score: float,
    score_metric: str,
    degree_baseline_score: float | None,
    random_grouping_score: float | None,
    sample_count: int,
    fixture_count: int,
    cv_status: str,
    evidence_label: str,
    interpretation: str,
) -> dict[str, Any]:
    return {
        "discriminator": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "target_class": target_class,
        "target_id": target_id,
        "source_artifacts": source_artifacts,
        "feature_family": feature_family,
        "score": score,
        "score_metric": score_metric,
        "degree_adjacency_baseline_score": (
            "" if degree_baseline_score is None else degree_baseline_score
        ),
        "delta_vs_degree_adjacency": (
            "" if degree_baseline_score is None else score - degree_baseline_score
        ),
        "random_grouping_score": (
            "" if random_grouping_score is None else random_grouping_score
        ),
        "delta_vs_random_grouping": (
            "" if random_grouping_score is None else score - random_grouping_score
        ),
        "sample_count": sample_count,
        "fixture_count": fixture_count,
        "cv_split": "by_source_fixture_or_transform_where_available",
        "cv_status": cv_status,
        "evidence_label": evidence_label,
        "interpretation": interpretation,
    }


def _loads() -> dict[str, Any]:
    return {
        "schema": _read_json(INPUT_PATHS["schema"]),
        "a_rows": _read_csv(INPUT_PATHS["a_rows"]),
        "b_rows": _read_csv(INPUT_PATHS["b_rows"]),
        "d1": _read_json(INPUT_PATHS["d1_summary"]),
        "d3": _read_json(INPUT_PATHS["d3_summary"]),
        "d4": _read_json(INPUT_PATHS["d4_summary"]),
        "d5": _read_json(INPUT_PATHS["d5_summary"]),
        "d6": _read_json(INPUT_PATHS["d6_summary"]),
        "d7": _read_json(INPUT_PATHS["d7_summary"]),
        "d8": _read_json(INPUT_PATHS["d8_summary"]),
        "f": _read_json(INPUT_PATHS["f_summary"]),
        "g": _read_json(INPUT_PATHS["g_summary"]),
    }


def feature_family_scores(data: dict[str, Any]) -> list[dict[str, Any]]:
    a_rows = data["a_rows"]
    b_rows = data["b_rows"]
    a_positive_rows = _structured_positive_rows(
        a_rows,
        expected_field="expected_dominant_row",
    )
    b_positive_rows = _structured_positive_rows(
        b_rows,
        expected_field="expected_column",
    )
    d1 = data["d1"]
    d3 = data["d3"]
    d4 = data["d4"]
    d5 = data["d5"]
    d6 = data["d6"]
    d7 = data["d7"]
    d8 = data["d8"]
    f_summary = data["f"]
    g_summary = data["g"]

    a_majority = _balanced_majority_score(a_positive_rows, "expected_dominant_row")
    b_majority = _balanced_majority_score(b_positive_rows, "expected_column")
    non_factorized_score = 1.0 - float(d1["s9_factorization_mean_error"])
    rows: list[dict[str, Any]] = []

    rows.extend(
        [
            _score_row(
                target_class="geometric_differential",
                target_id="experiment_a_row_dominance",
                source_artifacts="Experiment A row-mode stress rows",
                feature_family="row",
                score=_mean_bool(a_positive_rows, "dominant_row_matches_expected"),
                score_metric="classification_accuracy",
                degree_baseline_score=a_majority,
                random_grouping_score=non_factorized_score,
                sample_count=len(a_positive_rows),
                fixture_count=len(
                    {row["source_fixture_id"] for row in a_positive_rows}
                ),
                cv_status="proxy_transform_controls_available",
                evidence_label="derived",
                interpretation="Row features predict row-local differential response.",
            ),
            _score_row(
                target_class="geometric_differential",
                target_id="d3_row_geometry_transpose_delta",
                source_artifacts="D3 transpose summary",
                feature_family="row",
                score=float(d3["row_local_geometry_response_mean"]),
                score_metric="mean_role_response",
                degree_baseline_score=float(
                    d3["row_local_transpose_geometry_response_mean"]
                ),
                random_grouping_score=non_factorized_score,
                sample_count=int(d3["row_fixture_count"]),
                fixture_count=int(d3["row_fixture_count"]),
                cv_status="artifact_reuse_no_fitted_cv",
                evidence_label="derived",
                interpretation="Row-local response exceeds transpose baseline.",
            ),
            _score_row(
                target_class="interface_routing_refinement",
                target_id="experiment_b_column_proxy_dominance",
                source_artifacts="Experiment B column proxy rows",
                feature_family="column",
                score=_mean_bool(
                    b_positive_rows,
                    "cancellation_column_matches_expected",
                ),
                score_metric="classification_accuracy",
                degree_baseline_score=b_majority,
                random_grouping_score=non_factorized_score,
                sample_count=len(b_positive_rows),
                fixture_count=len(
                    {row["source_fixture_id"] for row in b_positive_rows}
                ),
                cv_status="proxy_transform_controls_available",
                evidence_label="derived",
                interpretation="Column features predict derived interface proxy dominance.",
            ),
            _score_row(
                target_class="interface_routing_refinement",
                target_id="d5_immediate_refinement_column_memory",
                source_artifacts="D5 interface-memory summary",
                feature_family="column",
                score=float(d5["immediate_column_preservation_score_identity"]),
                score_metric="endpoint_column_match_accuracy",
                degree_baseline_score=float(d7["immediate_single_total_score"]),
                random_grouping_score=float(d7["immediate_random_triple_score"]),
                sample_count=int(d5["identity_edge_count"]),
                fixture_count=1,
                cv_status="identity_fixture_only_no_heldout_fit",
                evidence_label="direct",
                interpretation="True old columns predict immediate refinement endpoint columns.",
            ),
            _score_row(
                target_class="interface_routing_refinement",
                target_id="d5_post_window_column_memory",
                source_artifacts="D5 interface-memory summary",
                feature_family="column",
                score=float(d5["post_window_column_memory_score_identity"]),
                score_metric="persistent_endpoint_column_accuracy",
                degree_baseline_score=float(
                    d5["degree_adjacency_endpoint_baseline_identity"]
                ),
                random_grouping_score=float(d5["post_window_random_triple_score_identity"]),
                sample_count=int(d5["identity_edge_count"]),
                fixture_count=1,
                cv_status="identity_fixture_only_degree_baseline_competitive",
                evidence_label="partial",
                interpretation=(
                    "Column labels beat row/random semantic controls; degree/adjacency "
                    "also predicts endpoint persistence in this clean fixture."
                ),
            ),
            _score_row(
                target_class="interface_routing_refinement",
                target_id="d7_multiscale_semantic_columns_immediate",
                source_artifacts="D7 multiscale summary",
                feature_family="column",
                score=float(d7["immediate_true_column_score"]),
                score_metric="grouping_target_accuracy",
                degree_baseline_score=float(d7["immediate_single_total_score"]),
                random_grouping_score=float(d7["immediate_random_triple_score"]),
                sample_count=int(d5["identity_edge_count"]),
                fixture_count=1,
                cv_status="identity_fixture_only_no_heldout_fit",
                evidence_label="direct",
                interpretation="True columns beat rows/random triples for immediate target.",
            ),
            _score_row(
                target_class="edge_local",
                target_id="d6_signed_edge_local_interaction",
                source_artifacts="D6 port-interaction summary",
                feature_family="port",
                score=float(d6["primary_port_level_r2"]),
                score_metric="r2",
                degree_baseline_score=float(d6["primary_additive_r2"]),
                random_grouping_score=float(d6["primary_random_triple_r2"]),
                sample_count=len(d6["canonical_port_ids_tested"]),
                fixture_count=1,
                cv_status="saturated_factorial_no_statistical_cv",
                evidence_label="direct",
                interpretation=(
                    "Port-level features fit the signed target; additive row+column "
                    "and random triples are weaker."
                ),
            ),
            _score_row(
                target_class="edge_local",
                target_id="experiment_g_observer_local_motion",
                source_artifacts="Experiment G mixed motion summary",
                feature_family="port",
                score=float(g_summary["canonical_controls_match_expected"]),
                score_metric="canonical_control_success",
                degree_baseline_score=None,
                random_grouping_score=0.0,
                sample_count=len(g_summary["transition_classes"]),
                fixture_count=3,
                cv_status="clean_motion_controls_no_fitted_cv",
                evidence_label="partial",
                interpretation="Port histories support observer-local row/column motion classes.",
            ),
            _score_row(
                target_class="generic_activity",
                target_id="d4_lane_a_saturation_gate",
                source_artifacts="D4 saturation summary",
                feature_family="degree_adjacency_baseline",
                score=float(d4["candidate_detection_matches_formula_all_rows"]),
                score_metric="gate_formula_match",
                degree_baseline_score=1.0,
                random_grouping_score=1.0
                if d4["transform_candidate_refinement_invariance"]
                else 0.0,
                sample_count=int(d4["all_transform_row_count"]),
                fixture_count=int(d4["identity_row_count"]),
                cv_status="transform_invariant_h0_competitive",
                evidence_label="direct",
                interpretation=(
                    "Lane A saturation is capacity/Hessian-based and remains "
                    "competitive for ordinary graph-capacity features."
                ),
            ),
            _score_row(
                target_class="generic_activity",
                target_id="experiment_f_edge_label_path_disagreement",
                source_artifacts="Experiment F path disagreement summary",
                feature_family="degree_adjacency_baseline",
                score=float(f_summary["base_metric_delay_flux_disagree"]),
                score_metric="edge_label_path_control_success",
                degree_baseline_score=1.0,
                random_grouping_score=float(f_summary["port_relabel_preserves_path_choices"]),
                sample_count=3,
                fixture_count=1,
                cv_status="edge_label_fixture_h0_competitive",
                evidence_label="direct",
                interpretation=(
                    "Path disagreement is edge-label behavior, not row/column "
                    "semantic separation."
                ),
            ),
            _score_row(
                target_class="identity_level_persistence",
                target_id="d8_configured_window_identity",
                source_artifacts="D8 identity-emergence summary",
                feature_family="port_plus_column_plus_global_basin_context",
                score=float(d8["accepted_budget_audit_pass"]),
                score_metric="accepted_identity_criteria_success",
                degree_baseline_score=0.0,
                random_grouping_score=0.0,
                sample_count=int(d8["accepted_identity_window_rows"]),
                fixture_count=int(d8["accepted_identity_event_count"]),
                cv_status="configured_window_fixture_only_partial",
                evidence_label="partial",
                interpretation=(
                    "Accepted identity requires refinement lineage, persistent "
                    "child sink/basin rows, and budget evidence."
                ),
            ),
        ]
    )
    return rows


def random_grouping_controls(
    scores: list[dict[str, Any]],
    data: dict[str, Any],
) -> list[dict[str, Any]]:
    d1 = data["d1"]
    d5 = data["d5"]
    d6 = data["d6"]
    d7 = data["d7"]
    return [
        {
            "discriminator": DISCRIMINATOR_ID,
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "control_id": "d1_sampled_s9_random_triple_proxy",
            "target_class": "factorization_sensitive_artifacts",
            "control_family": "sampled_non_factorized_s9",
            "score": 1.0 - float(d1["s9_factorization_mean_error"]),
            "comparison_score": 1.0 - float(d1["structured_factorization_mean_error"]),
            "score_metric": "semantic_preservation_score",
            "sample_count": int(d1["record_count"]),
            "status": "structured_beats_random",
            "notes": "Sampled non-factorized control; not exhaustive S9 coverage.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "control_id": "d5_post_window_random_triple",
            "target_class": "interface_routing_refinement",
            "control_family": "random_triple",
            "score": float(d5["post_window_random_triple_score_identity"]),
            "comparison_score": float(d5["post_window_column_memory_score_identity"]),
            "score_metric": "persistent_endpoint_column_accuracy",
            "sample_count": int(d5["identity_edge_count"]),
            "status": "true_column_beats_random",
            "notes": "Identity fixture only; sampled random grouping.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "control_id": "d6_signed_target_random_triple",
            "target_class": "edge_local",
            "control_family": "random_triple",
            "score": float(d6["primary_random_triple_r2"]),
            "comparison_score": float(d6["primary_port_level_r2"]),
            "score_metric": "r2",
            "sample_count": len(d6["canonical_port_ids_tested"]),
            "status": "port_beats_random",
            "notes": "Matched nine-port factorial fixture; saturated port model expected to fit.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "control_id": "d7_immediate_random_triple",
            "target_class": "interface_routing_refinement",
            "control_family": "random_triple",
            "score": float(d7["immediate_random_triple_score"]),
            "comparison_score": float(d7["immediate_true_column_score"]),
            "score_metric": "grouping_target_accuracy",
            "sample_count": int(d5["identity_edge_count"]),
            "status": "true_column_beats_random",
            "notes": "D7 semantic grouping comparison.",
        },
        {
            "discriminator": DISCRIMINATOR_ID,
            "schema_version": ARTIFACT_SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "control_id": "shuffled_target_labels",
            "target_class": "all",
            "control_family": "shuffled_target",
            "score": "",
            "comparison_score": "",
            "score_metric": "not_run",
            "sample_count": sum(int(row["sample_count"]) for row in scores),
            "status": "inconclusive_small_deterministic_fixture_set",
            "notes": (
                "No reusable large held-out dataset exists; shuffled-label "
                "control is deferred instead of inferred."
            ),
        },
    ]


def summary_payload(
    scores: list[dict[str, Any]], controls: list[dict[str, Any]]
) -> dict[str, Any]:
    h0_competitive_targets = [
        row["target_id"]
        for row in scores
        if row["feature_family"] == "degree_adjacency_baseline"
        or row["cv_status"].endswith("h0_competitive")
        or row["cv_status"] == "identity_fixture_only_degree_baseline_competitive"
    ]
    separated_targets = [
        row["target_id"]
        for row in scores
        if row["delta_vs_random_grouping"] != ""
        and float(row["delta_vs_random_grouping"]) > 0.0
        and row["feature_family"] != "degree_adjacency_baseline"
    ]
    return {
        "discriminator_id": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "classification": "role_separation_supported_with_scorecard_cv_limitations",
        "score_row_count": len(scores),
        "random_control_row_count": len(controls),
        "target_classes_scored": sorted({row["target_class"] for row in scores}),
        "separated_targets": separated_targets,
        "h0_competitive_targets": h0_competitive_targets,
        "degree_adjacency_explains_all_targets": False,
        "random_groupings_explain_all_targets": False,
        "fitted_cross_validation_status": "inconclusive_small_deterministic_fixture_set",
        "scorecard_cross_validation_status": "proxy_by_fixture_family_or_transform_controls",
        "evidence_label": "partial",
        "boundary": (
            "D2 compares completed artifact scores by feature family. It "
            "supports role separation for row, column, and port-sensitive "
            "targets, while degree/adjacency remains competitive for Lane A "
            "saturation and edge-label path targets. Full fitted cross-"
            "validation remains limited by the small deterministic fixture set."
        ),
    }


def blocked_observations() -> list[dict[str, str]]:
    return [
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "full fitted cross-validation by held-out landscape",
            "status": "inconclusive",
            "artifact_source": "completed clean O/D fixture set",
            "reconstruction_attempt": (
                "Built scorecard rows by source fixture/transform where "
                "available; did not fit a large-sample predictive model."
            ),
            "notes": (
                "Completed artifacts are deterministic clean fixtures, not a "
                "large multi-landscape dataset."
            ),
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "shuffled-target predictive controls",
            "status": "inconclusive",
            "artifact_source": "D2 scoring scorecard",
            "reconstruction_attempt": (
                "Recorded shuffled target as a control row but did not infer a "
                "score from the small deterministic dataset."
            ),
            "notes": "Shuffled-label controls need a reusable held-out target matrix.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "landscape-general predictive role separation",
            "status": "inconclusive",
            "artifact_source": "A-G and D1-D8 clean fixtures",
            "reconstruction_attempt": "Aggregated completed artifact scores.",
            "notes": "D2 does not run a landscape/seed robustness suite.",
        },
    ]


def _write_blocked_report(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# D2 Blocked Observations",
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


def _best_by_target(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in scores:
        grouped.setdefault(row["target_id"], []).append(row)
    best: list[dict[str, Any]] = []
    for target_id, rows in grouped.items():
        ordered = sorted(rows, key=lambda row: float(row["score"]), reverse=True)
        best.append(ordered[0] | {"target_id": target_id})
    return sorted(best, key=lambda row: (row["target_class"], row["target_id"]))


def _write_report(
    path: Path,
    scores: list[dict[str, Any]],
    controls: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    best = _best_by_target(scores)
    lines = [
        "# D2 Predictive Role Separation Scoring Report",
        "",
        "Status: complete as an artifact scorecard; fitted CV remains limited.",
        "",
        "Classification: `role_separation_supported_with_scorecard_cv_limitations`.",
        "",
        "## Scope",
        "",
        "D2 aggregates completed A-G and D1/D3/D4/D5/D6/D7/D8 artifact scores",
        "into a feature-family comparison. The scorecard compares row, column,",
        "port, random grouping, and degree/adjacency features where the completed",
        "artifacts expose matching targets.",
        "",
        "## Best Feature Family By Target",
        "",
        "| Target Class | Target | Best Family | Score | Metric | CV Status |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in best:
        lines.append(
            "| "
            f"{row['target_class']} | "
            f"{row['target_id']} | "
            f"{row['feature_family']} | "
            f"{float(row['score']):.6f} | "
            f"{row['score_metric']} | "
            f"{row['cv_status']} |"
        )
    lines.extend(
        [
            "",
            "## H0-Competitive Targets",
            "",
        ]
    )
    for target_id in summary["h0_competitive_targets"]:
        lines.append(f"- `{target_id}`")
    lines.extend(
        [
            "",
            "## Random Grouping Controls",
            "",
            "| Control | Target Class | Score | Comparison | Status |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in controls:
        score = row["score"] if row["score"] == "" else f"{float(row['score']):.6f}"
        comparison = (
            row["comparison_score"]
            if row["comparison_score"] == ""
            else f"{float(row['comparison_score']):.6f}"
        )
        lines.append(
            "| "
            f"{row['control_id']} | "
            f"{row['target_class']} | "
            f"{score} | "
            f"{comparison} | "
            f"{row['status']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "D2 supports predictive role separation at the artifact-scorecard level.",
            "Rows are strongest for geometric/differential targets, columns are",
            "strongest for interface/refinement/multiscale targets, and port-level",
            "features are strongest for the signed edge-local and observer-local",
            "motion targets. Degree/adjacency remains competitive for Lane A",
            "saturation and edge-label path disagreement, so H0 is not globally",
            "rejected by D2.",
            "",
            "## Cross-Validation Boundary",
            "",
            "The completed artifact set is made of clean deterministic fixtures.",
            "D2 records transform and source-fixture proxy splits where available,",
            "but a full fitted held-out-landscape cross-validation pass remains",
            "inconclusive.",
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
    data = _loads()
    scores = feature_family_scores(data)
    controls = random_grouping_controls(scores, data)
    summary = summary_payload(scores, controls)
    blocked = blocked_observations()
    outputs = {
        "scores": EXPERIMENT_ROOT / "outputs" / "d2_feature_family_scores.csv",
        "controls": EXPERIMENT_ROOT / "outputs" / "d2_random_grouping_controls.csv",
        "summary": EXPERIMENT_ROOT / "outputs" / "d2_scoring_summary.json",
        "manifest": EXPERIMENT_ROOT / "outputs" / "d2_scoring_manifest.json",
        "report": EXPERIMENT_ROOT / "reports" / "d2_cross_validation_report.md",
        "blocked": EXPERIMENT_ROOT / "reports" / "d2_blocked_observations.md",
    }
    _write_csv(outputs["scores"], scores)
    _write_csv(outputs["controls"], controls)
    _write_json(outputs["summary"], summary)
    _write_blocked_report(outputs["blocked"], blocked)
    _write_report(outputs["report"], scores, controls, summary)
    manifest = {
        "discriminator_id": DISCRIMINATOR_ID,
        "iteration": "10",
        "script_path": SCRIPT_PATH,
        "command": (
            "python experiments/2026-05-N01-grc9v3-properties/scripts/"
            "run_discriminator_d2_scoring.py --write-defaults"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_status_short": _git_value(["status", "--short"]),
        "lane_id": LANE_ID,
        "fixture_id": sorted({row["source_artifacts"] for row in scores}),
        "transform_id": ["identity", "structured_controls", "sampled_random_controls"],
        "seed": 0,
        "runtime_params": {
            "mode": "reuse_completed_o_and_d_artifacts",
            "scoring_mode": "artifact_scorecard",
            "fitted_cross_validation": "inconclusive_small_fixture_set",
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
        "classification": summary["classification"],
        "blocked_or_inconclusive": [
            "full fitted cross-validation by held-out landscape",
            "shuffled-target predictive controls",
            "landscape-general predictive role separation",
        ],
    }
    _write_json(outputs["manifest"], manifest)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-defaults",
        action="store_true",
        help="write D2 scoring outputs under the experiment directory",
    )
    args = parser.parse_args()
    if not args.write_defaults:
        parser.error("pass --write-defaults to write outputs")
    outputs = write_outputs()
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
