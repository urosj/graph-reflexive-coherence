"""Iteration 11: D1-D8 discriminator synthesis against the anonymous-port null."""

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
DISCRIMINATOR_ID = "discriminator_synthesis"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_discriminator_synthesis.py"
)

SUMMARY_FILES = {
    "D1": EXPERIMENT_ROOT / "outputs" / "d1_factorization_summary.json",
    "D2": EXPERIMENT_ROOT / "outputs" / "d2_scoring_summary.json",
    "D3": EXPERIMENT_ROOT / "outputs" / "d3_transpose_summary.json",
    "D4": EXPERIMENT_ROOT / "outputs" / "d4_saturation_summary.json",
    "D5": EXPERIMENT_ROOT / "outputs" / "d5_interface_memory_summary.json",
    "D6": EXPERIMENT_ROOT / "outputs" / "d6_port_interaction_summary.json",
    "D7": EXPERIMENT_ROOT / "outputs" / "d7_multiscale_summary.json",
    "D8": EXPERIMENT_ROOT / "outputs" / "d8_identity_emergence_summary.json",
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


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_summaries() -> dict[str, dict[str, Any]]:
    missing = [str(path) for path in SUMMARY_FILES.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing discriminator summaries: {missing}")
    return {key: _read_json(path) for key, path in SUMMARY_FILES.items()}


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"cannot write empty CSV {path}")
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


def hypothesis_status_rows(summaries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    d1 = summaries["D1"]
    d2 = summaries["D2"]
    d3 = summaries["D3"]
    d4 = summaries["D4"]
    d5 = summaries["D5"]
    d6 = summaries["D6"]
    d7 = summaries["D7"]
    d8 = summaries["D8"]
    return [
        {
            "hypothesis_id": "H0",
            "hypothesis": "anonymous-port null",
            "classification": "partially_weakened_not_globally_refuted",
            "support_status": "weakened",
            "primary_discriminators": "D1;D2;D3;D5;D6;D7;D8",
            "key_evidence": (
                "Structured row/column transforms preserve sensitive artifacts "
                "better than sampled S9/random triples; D2 scorecard separates "
                "row, column, port, and composite target families."
            ),
            "key_numbers": (
                f"structured_error={d1['structured_factorization_mean_error']}; "
                f"s9_error={d1['s9_factorization_mean_error']}; "
                f"separated_targets={len(d2['separated_targets'])}"
            ),
            "h0_competitive_scope": (
                "D4 Lane A saturation; Experiment F edge-label paths; D5 "
                "post-window endpoint availability in the clean fixture"
            ),
            "evidence_label": "partial",
            "artifact_refs": (
                "outputs/d1_factorization_summary.json; "
                "outputs/d2_scoring_summary.json"
            ),
            "boundaries": (
                "No landscape-general refutation, exhaustive S9 proof, or "
                "full fitted held-out predictive CV."
            ),
        },
        {
            "hypothesis_id": "D1",
            "hypothesis": "factorization discriminator",
            "classification": d1["classification"],
            "support_status": "supported",
            "primary_discriminators": "D1",
            "key_evidence": (
                "Structured row/column transforms have zero mean semantic "
                "error on factorization-sensitive artifacts; sampled "
                "non-factorized proxy has error 1.0."
            ),
            "key_numbers": (
                f"structured_error={d1['structured_factorization_mean_error']}; "
                f"s9_error={d1['s9_factorization_mean_error']}; "
                f"records={d1['record_count']}"
            ),
            "h0_competitive_scope": "Lane A saturation reported separately.",
            "evidence_label": "partial",
            "artifact_refs": "outputs/d1_factorization_summary.json",
            "boundaries": "Sampled non-factorized control, not exhaustive S9 coverage.",
        },
        {
            "hypothesis_id": "D2",
            "hypothesis": "predictive role separation",
            "classification": d2["classification"],
            "support_status": "supported_with_cv_limitations",
            "primary_discriminators": "D2",
            "key_evidence": (
                "Rows, columns, ports, composite context, and degree/edge-label "
                "baselines are strongest on different target classes."
            ),
            "key_numbers": (
                f"score_rows={d2['score_row_count']}; "
                f"random_groupings_explain_all={d2['random_groupings_explain_all_targets']}; "
                f"degree_explains_all={d2['degree_adjacency_explains_all_targets']}"
            ),
            "h0_competitive_scope": "; ".join(d2["h0_competitive_targets"]),
            "evidence_label": "partial",
            "artifact_refs": "outputs/d2_scoring_summary.json",
            "boundaries": "Artifact scorecard only; fitted held-out landscape CV inconclusive.",
        },
        {
            "hypothesis_id": "D3",
            "hypothesis": "row/column transpose non-equivalence",
            "classification": d3["classification"],
            "support_status": "supported",
            "primary_discriminators": "D3",
            "key_evidence": (
                "Row-local geometry response and column-local interface proxy "
                "response drop under transpose."
            ),
            "key_numbers": (
                f"role_separation_index={d3['role_separation_index']}; "
                f"row={d3['row_local_geometry_response_mean']}; "
                f"row_transpose={d3['row_local_transpose_geometry_response_mean']}; "
                f"column={d3['column_local_interface_response_mean']}; "
                f"column_transpose={d3['column_local_transpose_interface_response_mean']}"
            ),
            "h0_competitive_scope": "Generic non-role artifacts not tested by D3.",
            "evidence_label": d3["evidence_label"],
            "artifact_refs": "outputs/d3_transpose_summary.json",
            "boundaries": "Direct column-H and event-capable transpose refinement remain blocked/inconclusive.",
        },
        {
            "hypothesis_id": "D4",
            "hypothesis": "saturation bottleneck",
            "classification": d4["classification"],
            "support_status": "supported_with_lane_a_boundaries",
            "primary_discriminators": "D4",
            "key_evidence": (
                "Degree 7/8 stressed nodes do not trigger; degree 9 stressed "
                "node triggers; degree 9 stable-Hessian control does not."
            ),
            "key_numbers": (
                f"gate='{d4['canonical_gate_formula']}'; "
                f"budget_error={d4['canonical_positive_budget_error']}; "
                f"rows={d4['all_transform_row_count']}"
            ),
            "h0_competitive_scope": "Capacity/Hessian gate is not row/column factorization evidence.",
            "evidence_label": d4["evidence_label"],
            "artifact_refs": "outputs/d4_saturation_summary.json",
            "boundaries": "Direct column-H and degree-8 near-saturation remain blocked under Lane A.",
        },
        {
            "hypothesis_id": "D5",
            "hypothesis": "interface memory",
            "classification": d5["classification"],
            "support_status": "mechanical_supported_post_window_partial",
            "primary_discriminators": "D5",
            "key_evidence": (
                "Immediate old-column memory is complete; post-window true "
                "columns beat row/random semantic controls."
            ),
            "key_numbers": (
                f"immediate={d5['immediate_column_preservation_score_identity']}; "
                f"post_window={d5['post_window_column_memory_score_identity']}; "
                f"random_triple={d5['post_window_random_triple_score_identity']}; "
                f"persistent_edges={d5['persistent_endpoint_edge_count_identity']}/{d5['identity_edge_count']}"
            ),
            "h0_competitive_scope": "Degree/adjacency endpoint baseline is competitive in the clean fixture.",
            "evidence_label": d5["evidence_label"],
            "artifact_refs": "outputs/d5_interface_memory_summary.json",
            "boundaries": "Post-refinement flux windows and checkpoint observer windows unavailable.",
        },
        {
            "hypothesis_id": "D6",
            "hypothesis": "port interaction",
            "classification": d6["classification"],
            "support_status": "supported_for_signed_edge_local_target",
            "primary_discriminators": "D6",
            "key_evidence": (
                "Signed edge-local target is not additive row+column, while "
                "port-level and interaction models fit exactly."
            ),
            "key_numbers": (
                f"additive_r2={d6['primary_additive_r2']}; "
                f"interaction_r2={d6['primary_interaction_r2']}; "
                f"port_r2={d6['primary_port_level_r2']}; "
                f"random_triple_r2={d6['primary_random_triple_r2']}"
            ),
            "h0_competitive_scope": "Runtime absolute-flux control is additive in this fixture.",
            "evidence_label": d6["evidence_label"],
            "artifact_refs": "outputs/d6_port_interaction_summary.json",
            "boundaries": "Existence witness only, not universal port non-additivity.",
        },
        {
            "hypothesis_id": "D7",
            "hypothesis": "multiscale discriminator",
            "classification": d7["classification"],
            "support_status": "supported_with_boundaries",
            "primary_discriminators": "D7",
            "key_evidence": (
                "True-column G/Split reconstructs eligible fields; signed flux "
                "is exact through J+/J-; true columns beat rows/random triples "
                "on interface/refinement targets."
            ),
            "key_numbers": (
                f"max_error={d7['max_exact_reconstruction_error']}; "
                f"signed_flux_j_split={d7['signed_flux_j_split_available']}; "
                f"immediate_column={d7['immediate_true_column_score']}; "
                f"random_triple={d7['immediate_random_triple_score']}"
            ),
            "h0_competitive_scope": "Other groupings could be mathematically invertible with their own profiles.",
            "evidence_label": d7["evidence_label"],
            "artifact_refs": "outputs/d7_multiscale_summary.json",
            "boundaries": "Before/after refinement E-style G/Split checkpoints remain blocked.",
        },
        {
            "hypothesis_id": "D8",
            "hypothesis": "identity emergence",
            "classification": d8["classification"],
            "support_status": "supported_with_boundaries",
            "primary_discriminators": "D8",
            "key_evidence": (
                "Configured-window identity requires refinement, persistent "
                "child sink/basin rows, lineage, and budget evidence."
            ),
            "key_numbers": (
                f"accepted_events={d8['accepted_identity_event_count']}; "
                f"accepted_rows={d8['accepted_identity_window_rows']}; "
                f"strict_failures={d8['strict_threshold_failure_rows']}; "
                f"no_refinement_controls={d8['no_refinement_negative_controls']}"
            ),
            "h0_competitive_scope": "Mechanical refinement alone is explicitly rejected as identity fission.",
            "evidence_label": d8["evidence_label"],
            "artifact_refs": "outputs/d8_identity_emergence_summary.json",
            "boundaries": "Checkpoint-window, collapse/reabsorption, and landscape-general identity remain inconclusive.",
        },
    ]


def prediction_comparison_rows() -> list[dict[str, Any]]:
    return [
        {
            "prediction": "H0 will be partially rejected, not completely destroyed.",
            "observed_result": "matched",
            "synthesis": (
                "H0 is weakened for row/column/port-sensitive artifact classes "
                "but remains competitive for generic capacity and edge-label targets."
            ),
        },
        {
            "prediction": "Rows will show clean geometry/differential evidence.",
            "observed_result": "matched",
            "synthesis": "A, D2, and D3 support row-geometric/differential targets.",
        },
        {
            "prediction": "Columns will show strongest mechanical support in refinement/coarse-graining.",
            "observed_result": "matched",
            "synthesis": "D5 and D7 support column refinement/multiscale targets.",
        },
        {
            "prediction": "Direct/dynamic column claims may need caveats.",
            "observed_result": "matched",
            "synthesis": "Direct column-H remains blocked under Lane A; D5 post-window support is partial.",
        },
        {
            "prediction": "Port interaction is fixture-dependent.",
            "observed_result": "matched",
            "synthesis": "D6 supports a signed edge-local witness but runtime absolute flux is additive.",
        },
        {
            "prediction": "Path disagreement depends on exposed labels.",
            "observed_result": "supported",
            "synthesis": "Experiment F and D2 confirm edge-label path disagreement as a generic path-label target.",
        },
        {
            "prediction": "Identity emergence is most uncertain.",
            "observed_result": "partially_supported_with_boundaries",
            "synthesis": "D8 supports configured-window child-basin persistence only with strict thresholds.",
        },
    ]


def followup_rows() -> list[dict[str, Any]]:
    return [
        {
            "surface_or_suite": "grc9v3_column_h_assisted Lane B / Lane C",
            "status": "completed post-pass comparison",
            "reason": "Direct column-H proxy-branch spark evidence remains blocked under Lane A but observed in explicit Lane B rows.",
            "guardrail": "Do not reinterpret Lane A derived B proxies or D4 Lane A sparks as direct column-H branch evidence.",
        },
        {
            "surface_or_suite": "near-saturation degree-8 policy",
            "status": "future implementation candidate",
            "reason": "D4 marks near-saturation blocked because Lane A has no such policy.",
            "guardrail": "Do not treat degree-9 saturation support as degree-8 near-saturation support.",
        },
        {
            "surface_or_suite": "checkpoint-window identity persistence",
            "status": "small addendum candidate",
            "reason": "D8 uses runtime-state windows, not persisted checkpoint observer windows.",
            "guardrail": "Do not promote configured-window runtime support to checkpoint-window support.",
        },
        {
            "surface_or_suite": "reusable motion-loader full port histories",
            "status": "future implementation candidate",
            "reason": "Experiment G used checkpoint-overlay observer reconstruction.",
            "guardrail": "Do not infer reusable loader support from observer-local overlays.",
        },
        {
            "surface_or_suite": "landscape/seed predictive robustness suite",
            "status": "future experiment suite",
            "reason": "D2 fitted held-out-landscape CV remains inconclusive.",
            "guardrail": "Do not report clean-fixture scorecards as landscape-general statistics.",
        },
        {
            "surface_or_suite": "exhaustive or broader S9 sampling",
            "status": "future robustness addendum",
            "reason": "D1/D2 random controls are sampled non-factorized proxies.",
            "guardrail": "Do not describe sampled S9 controls as exhaustive.",
        },
    ]


def synthesis_summary(
    summaries: dict[str, dict[str, Any]],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    supported = [
        row["hypothesis_id"]
        for row in rows
        if row["support_status"].startswith("supported")
        or row["support_status"].startswith("mechanical_supported")
    ]
    return {
        "discriminator_id": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "classification": "anonymous_port_null_partially_rejected_with_lane_a_boundaries",
        "hypothesis_row_count": len(rows),
        "supported_or_partially_supported": supported,
        "h0_status": "partially_weakened_not_globally_refuted",
        "h0_competitive_targets": summaries["D2"]["h0_competitive_targets"],
        "blocked_or_inconclusive_surfaces": [
            "degree-8 near-saturation",
            "checkpoint-window identity persistence",
            "landscape-general identity emergence",
            "full fitted held-out-landscape predictive CV",
            "reusable motion-loader full port histories",
            "exhaustive S9 coverage",
        ],
        "source_intent_only_claims_promoted": False,
        "runtime_mutation": "none",
        "boundary": (
            "D1-D8 partially reject the anonymous-port null for controlled "
            "Lane A artifact classes. The result does not establish landscape-"
            "general semantics, near-saturation policy, "
            "checkpoint-window identity, or exhaustive S9 robustness."
        ),
    }


def _write_report(
    path: Path,
    *,
    rows: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    followups: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    lines = [
        "# Discriminator Synthesis",
        "",
        "Status: complete.",
        "",
        "Classification: `anonymous_port_null_partially_rejected_with_lane_a_boundaries`.",
        "",
        "## Conclusion",
        "",
        "D1-D8 partially reject the anonymous-port null for the controlled Lane A",
        "artifact classes tested here. Rows, columns, ports, composite basin",
        "context, and ordinary graph/edge-label baselines explain different",
        "artifact classes. H0 is no longer competitive for all artifacts, but it",
        "remains competitive for generic capacity and edge-label path behavior.",
        "",
        "## Hypothesis Status",
        "",
        "| ID | Hypothesis | Classification | Key Evidence | Boundaries |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['hypothesis_id']} | "
            f"{row['hypothesis']} | "
            f"{row['classification']} | "
            f"{row['key_evidence']} {row['key_numbers']} | "
            f"{row['boundaries']} |"
        )
    lines.extend(
        [
            "",
            "## H0-Competitive Scope",
            "",
        ]
    )
    for target in summary["h0_competitive_targets"]:
        lines.append(f"- `{target}`")
    lines.extend(
        [
            "",
            "## Prediction Comparison",
            "",
            "| Prediction | Observed Result | Synthesis |",
            "| --- | --- | --- |",
        ]
    )
    for row in predictions:
        lines.append(
            "| "
            f"{row['prediction']} | "
            f"{row['observed_result']} | "
            f"{row['synthesis']} |"
        )
    lines.extend(
        [
            "",
            "## Follow-Up Surfaces",
            "",
            "| Surface Or Suite | Status | Reason | Guardrail |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in followups:
        lines.append(
            "| "
            f"{row['surface_or_suite']} | "
            f"{row['status']} | "
            f"{row['reason']} | "
            f"{row['guardrail']} |"
        )
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- Supported discriminator claims cite generated outputs, not source intent alone.",
            "- Lane A is `current_hybrid_signed_hessian`; direct column-H proxy-branch evidence belongs only to explicit `grc9v3_column_h_assisted` Lane B/Lane C artifacts.",
            "- Mechanical refinement is not identity fission.",
            "- Configured-window child-basin persistence is not checkpoint-window or landscape-general identity.",
            "- D2 is an artifact scorecard, not full fitted held-out-landscape CV.",
            "- Sampled non-factorized controls are not exhaustive S9 coverage.",
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
    summaries = _load_summaries()
    rows = hypothesis_status_rows(summaries)
    predictions = prediction_comparison_rows()
    followups = followup_rows()
    summary = synthesis_summary(summaries, rows)
    outputs = {
        "hypothesis_status": (
            EXPERIMENT_ROOT / "outputs" / "discriminator_hypothesis_status.csv"
        ),
        "prediction_comparison": (
            EXPERIMENT_ROOT / "outputs" / "discriminator_prediction_comparison.csv"
        ),
        "followups": (
            EXPERIMENT_ROOT / "outputs" / "discriminator_followup_surfaces.csv"
        ),
        "summary": EXPERIMENT_ROOT / "outputs" / "discriminator_synthesis_summary.json",
        "manifest": (
            EXPERIMENT_ROOT / "outputs" / "discriminator_synthesis_manifest.json"
        ),
        "report": EXPERIMENT_ROOT / "reports" / "discriminator_synthesis.md",
    }
    _write_csv(outputs["hypothesis_status"], rows)
    _write_csv(outputs["prediction_comparison"], predictions)
    _write_csv(outputs["followups"], followups)
    _write_json(outputs["summary"], summary)
    manifest = {
        "discriminator_id": DISCRIMINATOR_ID,
        "iteration": "11",
        "script_path": SCRIPT_PATH,
        "command": (
            "python experiments/2026-05-N01-grc9v3-properties/scripts/"
            "run_discriminator_synthesis.py --write-defaults"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_status_short": _git_value(["status", "--short"]),
        "lane_id": LANE_ID,
        "fixture_id": ["D1-D8 completed discriminator summaries"],
        "transform_id": ["summary"],
        "seed": 0,
        "runtime_params": {
            "mode": "reuse_completed_discriminator_outputs",
            "runtime_mutation": "none",
        },
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_source_map": {
            key: str(path.relative_to(EXPERIMENT_ROOT))
            for key, path in SUMMARY_FILES.items()
        },
        "output_paths": {
            key: str(path.relative_to(EXPERIMENT_ROOT))
            for key, path in outputs.items()
        },
        "manifest_required_fields": list(manifest_schema()),
        "evidence_labels": list(EVIDENCE_LABELS),
        "classification": summary["classification"],
    }
    _write_json(outputs["manifest"], manifest)
    _write_report(
        outputs["report"],
        rows=rows,
        predictions=predictions,
        followups=followups,
        summary=summary,
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-defaults",
        action="store_true",
        help="write discriminator synthesis outputs under the experiment directory",
    )
    args = parser.parse_args()
    if not args.write_defaults:
        parser.error("pass --write-defaults to write outputs")
    outputs = write_outputs()
    for name, path in outputs.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
