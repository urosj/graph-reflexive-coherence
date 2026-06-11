"""Iteration 10: family-level synthesis for GRC9V3 property experiments."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
from typing import Any

from grc9v3_fixture_harness import ARTIFACT_SCHEMA_VERSION, LANE_ID


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_ID = "family_level_synthesis"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_family_level_synthesis.py"
)


SUMMARY_FILES = {
    "A": EXPERIMENT_ROOT / "outputs" / "experiment_a_row_mode_stress_summary.json",
    "B": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_b_column_interface_cancellation_summary.json"
    ),
    "C": EXPERIMENT_ROOT / "outputs" / "experiment_c_saturation_summary.json",
    "D": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_summary.json"
    ),
    "E": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_e_coarse_graining_split_summary.json"
    ),
    "F": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_f_path_disagreement_summary.json"
    ),
    "G": EXPERIMENT_ROOT / "outputs" / "experiment_g_mixed_motion_summary.json",
}


REPORT_FILES = {
    "A": "reports/experiment_a_row_mode_stress.md",
    "B": "reports/experiment_b_column_interface_cancellation.md",
    "C": "reports/experiment_c_saturation.md",
    "D": "reports/experiment_d_refinement_identity.md",
    "E": "reports/experiment_e_coarse_graining_split.md",
    "F": "reports/experiment_f_path_disagreement.md",
    "G": "reports/experiment_g_mixed_motion.md",
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_summaries() -> dict[str, dict[str, Any]]:
    missing = [str(path) for path in SUMMARY_FILES.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing experiment summaries: {missing}")
    return {key: _load_json(path) for key, path in SUMMARY_FILES.items()}


def _bool(summary: dict[str, Any], key: str) -> bool:
    return bool(summary.get(key))


def _validate_support_inputs(summaries: dict[str, dict[str, Any]]) -> dict[str, bool]:
    checks = {
        "a_row_signature": _bool(summaries["A"], "identity_row_stress_matches")
        and _bool(summaries["A"], "row_permutation_moves_signature")
        and _bool(summaries["A"], "random_relabel_clean_signature_destroyed"),
        "b_column_proxy": _bool(summaries["B"], "identity_column_proxy_matches")
        and _bool(summaries["B"], "column_permutation_moves_proxy")
        and _bool(summaries["B"], "direct_column_h_gate_claim"),
        "c_saturation": _bool(summaries["C"], "degree_9_stressed_refines")
        and _bool(summaries["C"], "active_degree_7_or_8_stressed_nontrigger")
        and _bool(summaries["C"], "degree_9_without_instability_nontrigger"),
        "d_refinement": _bool(summaries["D"], "all_refinement_rows_budget_preserved")
        and _bool(summaries["D"], "all_refinement_rows_column_preserved_by_port")
        and _bool(summaries["D"], "configured_window_identity_support"),
        "e_multiscale": _bool(summaries["E"], "all_eligible_fields_near_exact")
        and _bool(summaries["E"], "signed_flux_j_split_available")
        and _bool(summaries["E"], "compressed_signed_flux_is_lossy"),
        "f_path_disagreement": _bool(summaries["F"], "base_primary_paths_all_distinct")
        and _bool(summaries["F"], "base_metric_delay_flux_disagree")
        and _bool(summaries["F"], "all_equalized_paths_collapse_to_tie_broken_path"),
        "g_motion": _bool(summaries["G"], "canonical_controls_match_expected")
        and _bool(summaries["G"], "row_preserving_column_changing_supported")
        and _bool(summaries["G"], "column_preserving_row_changing_supported"),
    }
    failed = [key for key, value in checks.items() if not value]
    if failed:
        raise ValueError(f"synthesis support prechecks failed: {failed}")
    return checks


def hypothesis_rows(summaries: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    _validate_support_inputs(summaries)
    return [
        {
            "hypothesis": "H0 anonymous-port null",
            "classification": "weakened",
            "scope": "partially weakened across controlled artifact classes",
            "evidence": "A row transforms; B derived column proxy; C saturation; D refinement; E G/Split; F edge-label paths; G motion observer",
            "artifact_refs": "; ".join(REPORT_FILES[key] for key in ("A", "B", "C", "D", "E", "F", "G")),
            "boundaries": "Generic graph activity, landscape generality, and discriminator baselines remain for D-style tests.",
            "next_discriminator": "D1, D2, D6, D7",
        },
        {
            "hypothesis": "O1 rows behave as local differential modes",
            "classification": "supported",
            "scope": "supported in clean row-stress fixtures",
            "evidence": "Row-local stress matches the intended row; row permutation moves the signature; random relabel weakens clean interpretation.",
            "artifact_refs": REPORT_FILES["A"],
            "boundaries": "Isotropic terms can dominate magnitude; result is fixture-level, not landscape-general.",
            "next_discriminator": "D1, D2, D3",
        },
        {
            "hypothesis": "O2 columns behave as interface/refinement/multiscale families",
            "classification": "supported",
            "scope": "partially supported; strongest for derived column proxy, refinement, and G/Split",
            "evidence": "Column proxy transforms correctly; column-preserving refinement and G/Split reconstruction are supported.",
            "artifact_refs": "; ".join(REPORT_FILES[key] for key in ("B", "D", "E")),
            "boundaries": "Direct column-H proxy-branch spark evidence is blocked under Lane A and available only in explicit Lane B/Lane C artifacts; dynamic routing and landscape-general column behavior are not established.",
            "next_discriminator": "D5, D7",
        },
        {
            "hypothesis": "O3 ports carry row-column intersection behavior",
            "classification": "supported",
            "scope": "partially supported by observer-local mixed motion and port-level refinement/mapping",
            "evidence": "G classifies row-preserving/column-changing and column-preserving/row-changing transitions from port histories; D audits port-to-column refinement mapping.",
            "artifact_refs": "; ".join(REPORT_FILES[key] for key in ("D", "G")),
            "boundaries": "Non-additive row x column interaction is not quantified; stronger D6 tests are still needed.",
            "next_discriminator": "D6",
        },
        {
            "hypothesis": "O4 metric, delay, and strongest-flux paths can disagree",
            "classification": "supported",
            "scope": "supported in controlled three-corridor fixture",
            "evidence": "Metric path, temporal-delay path, and strongest flux/coupling path select distinct corridors; equalized controls collapse for intended label reasons.",
            "artifact_refs": REPORT_FILES["F"],
            "boundaries": "Edge-label result, not row/column semantic evidence by itself.",
            "next_discriminator": "D2 if path labels become predictive targets",
        },
        {
            "hypothesis": "D1 factorization discriminator",
            "classification": "supported",
            "scope": "early O-style support only",
            "evidence": "Structured row/column transforms preserve or move intended signatures; arbitrary S9 relabels weaken interpretability in A, B, and G.",
            "artifact_refs": "; ".join(REPORT_FILES[key] for key in ("A", "B", "G")),
            "boundaries": "Formal D1 should score semantic error across more artifacts and baselines.",
            "next_discriminator": "D1",
        },
        {
            "hypothesis": "D2 predictive separation discriminator",
            "classification": "inconclusive",
            "scope": "not run as a predictive scoring discriminator",
            "evidence": "A-G provide feature targets but no predictive model comparison.",
            "artifact_refs": "; ".join(REPORT_FILES[key] for key in ("A", "B", "F", "G")),
            "boundaries": "Needs row-vs-column-vs-port feature scoring against held-out artifact targets.",
            "next_discriminator": "D2",
        },
        {
            "hypothesis": "D3 transpose discriminator",
            "classification": "supported",
            "scope": "partial support from transform controls",
            "evidence": "A/B transpose and random relabel controls remove or alter clean row/column claims.",
            "artifact_refs": "; ".join(REPORT_FILES[key] for key in ("A", "B")),
            "boundaries": "Formal D3 should report transpose-specific deltas across all applicable artifact classes.",
            "next_discriminator": "D3",
        },
        {
            "hypothesis": "D4 saturation discriminator",
            "classification": "supported",
            "scope": "supported under Lane A active-degree-9 signed-Hessian gate",
            "evidence": "Degree 7/8 stressed controls do not refine; degree 9 stressed fixture refines; degree 9 stable-Hessian control does not refine.",
            "artifact_refs": REPORT_FILES["C"],
            "boundaries": "Near-saturation degree-8 policy remains blocked under Lane A.",
            "next_discriminator": "D4 formal report",
        },
        {
            "hypothesis": "D5 interface-memory discriminator",
            "classification": "supported",
            "scope": "mechanical column-preserving lineage supported; longer interface memory not established",
            "evidence": "Mechanical expansion reassigns all old boundary edges and preserves old boundary column to module endpoint column.",
            "artifact_refs": REPORT_FILES["D"],
            "boundaries": "Post-refinement long-window interface memory and checkpoint-window identity persistence remain for later work.",
            "next_discriminator": "D5",
        },
        {
            "hypothesis": "D6 port-interaction discriminator",
            "classification": "inconclusive",
            "scope": "qualitative port-intersection witnesses exist, but no interaction model was fit",
            "evidence": "G and D show port-level mixed behavior and refinement mapping.",
            "artifact_refs": "; ".join(REPORT_FILES[key] for key in ("D", "G")),
            "boundaries": "Needs row-only + column-only additive baseline versus row x column interaction terms.",
            "next_discriminator": "D6",
        },
        {
            "hypothesis": "D7 multiscale discriminator",
            "classification": "supported",
            "scope": "supported for eligible fields and signed flux J+/J- split",
            "evidence": "Eligible nonnegative fields reconstruct near exactly; signed flux reconstructs exactly through J+/J-; compressed signed totals are lossy.",
            "artifact_refs": REPORT_FILES["E"],
            "boundaries": "Semantic grouping superiority over row/random triples is deferred to formal D7.",
            "next_discriminator": "D7",
        },
        {
            "hypothesis": "D8 identity-emergence discriminator",
            "classification": "inconclusive",
            "scope": "configured-window child-basin persistence supported, stronger identity emergence not established",
            "evidence": "D records configured three-step runtime-state child-basin persistence after refinement.",
            "artifact_refs": REPORT_FILES["D"],
            "boundaries": "Identity fission from expansion alone is not claimed; checkpoint-window and landscape-general persistence remain inconclusive.",
            "next_discriminator": "D8",
        },
        {
            "hypothesis": "Motion observer",
            "classification": "supported",
            "scope": "observer-local support in clean checkpoint-overlay fixtures",
            "evidence": "G classifies dominant central-port transitions from port_edges and endpoint metadata.",
            "artifact_refs": REPORT_FILES["G"],
            "boundaries": "Reusable motion-loader full port history, basin-assignment motion, and landscape-general motion remain inconclusive.",
            "next_discriminator": "future motion-loader port-history support",
        },
    ]


def experiment_rows() -> list[dict[str, str]]:
    return [
        {
            "experiment": "A",
            "theme": "row evidence",
            "classification": "supported",
            "summary": "Row-local stress produces expected row signatures in clean fixtures.",
            "artifact_refs": REPORT_FILES["A"],
        },
        {
            "experiment": "B",
            "theme": "derived column evidence",
            "classification": "supported_with_lane_a_boundary",
            "summary": "Column-local cancellation/pressure proxy is observable and transforms correctly; direct column-H gating is blocked.",
            "artifact_refs": REPORT_FILES["B"],
        },
        {
            "experiment": "E",
            "theme": "multiscale evidence",
            "classification": "supported",
            "summary": "G/Split reconstructs eligible nonnegative fields; signed flux is exact through J+/J-.",
            "artifact_refs": REPORT_FILES["E"],
        },
        {
            "experiment": "C",
            "theme": "saturation evidence",
            "classification": "supported",
            "summary": "Degree-9 saturation plus signed-Hessian degeneracy gates mechanical expansion under Lane A.",
            "artifact_refs": REPORT_FILES["C"],
        },
        {
            "experiment": "D",
            "theme": "refinement and child-basin evidence",
            "classification": "supported_with_identity_boundary",
            "summary": "Column-preserving mechanical refinement is supported; configured-window child-basin persistence is thresholded.",
            "artifact_refs": REPORT_FILES["D"],
        },
        {
            "experiment": "F",
            "theme": "path-label evidence",
            "classification": "supported",
            "summary": "Metric, delay, and strongest flux/coupling paths disagree and remain edge-auditable.",
            "artifact_refs": REPORT_FILES["F"],
        },
        {
            "experiment": "G",
            "theme": "motion-observer evidence",
            "classification": "supported_with_observer_local_boundary",
            "summary": "Observer-local row/column motion classification is supported in clean checkpoint-overlay fixtures.",
            "artifact_refs": REPORT_FILES["G"],
        },
    ]


def prediction_comparison_rows() -> list[dict[str, str]]:
    return [
        {
            "prediction": "H0 partially rejected, not uniformly",
            "observed_result": "matched",
            "evidence": "A-G weaken H0 across controlled artifact classes while generic dynamics and landscape generality remain untested.",
        },
        {
            "prediction": "Rows show clean geometry/differential evidence",
            "observed_result": "matched",
            "evidence": "Experiment A supports row-local signatures with transform controls.",
        },
        {
            "prediction": "Columns show strongest support in refinement/coarse-graining",
            "observed_result": "matched",
            "evidence": "Experiments D and E support column-preserving refinement and exact G/Split reconstruction.",
        },
        {
            "prediction": "Direct and dynamic column claims may be caveated",
            "observed_result": "matched",
            "evidence": "Experiment B direct column-H proxy-branch evidence remains blocked under Lane A; Lane C later shows it is available in explicit Lane B rows.",
        },
        {
            "prediction": "Port evidence likely partial and D6 needed",
            "observed_result": "matched",
            "evidence": "Experiment G supports mixed motion classification, while D6 interaction scoring remains inconclusive.",
        },
        {
            "prediction": "O4 path disagreement depends on exposed labels",
            "observed_result": "supported_more_cleanly_than_risk",
            "evidence": "Experiment F exposes fixed edge-label surfaces and demonstrates path disagreement with equalized controls.",
        },
        {
            "prediction": "Identity fission is uncertain",
            "observed_result": "matched",
            "evidence": "Experiment D supports configured-window child-basin persistence only; stronger D8 identity emergence remains inconclusive.",
        },
    ]


def followup_rows() -> list[dict[str, str]]:
    return [
        {
            "surface_or_suite": "grc9v3_column_h_assisted Lane B / Lane C",
            "status": "completed post-pass comparison",
            "reason": "Direct column-H proxy-branch spark evidence is blocked under Lane A but observed in explicit Lane B rows.",
            "must_not_be_inferred_from": "Do not reinterpret Experiment B Lane A rows as direct gate evidence.",
        },
        {
            "surface_or_suite": "near-saturation degree-8 policy",
            "status": "future implementation candidate",
            "reason": "Lane A has no active-degree-8 near-saturation policy.",
            "must_not_be_inferred_from": "Degree-9 saturation support.",
        },
        {
            "surface_or_suite": "inflow-weighted transfer lane",
            "status": "future implementation candidate",
            "reason": "GRC9V3 exposes equal/custom expansion weights, not a true inflow-weighted transfer lane.",
            "must_not_be_inferred_from": "Custom column-skewed runtime weights.",
        },
        {
            "surface_or_suite": "checkpoint-window identity persistence",
            "status": "small addendum or D8 prep",
            "reason": "Experiment D uses experiment-local runtime-state windows.",
            "must_not_be_inferred_from": "Expansion event alone.",
        },
        {
            "surface_or_suite": "reusable motion-loader full port histories",
            "status": "future implementation candidate",
            "reason": "Experiment G uses checkpoint-overlay analysis because current motion loader does not normalize full port histories.",
            "must_not_be_inferred_from": "Observer-local clean fixture support.",
        },
        {
            "surface_or_suite": "landscape/seed robustness suite",
            "status": "future experiment suite",
            "reason": "A-G are clean controlled fixtures, not landscape-general studies.",
            "must_not_be_inferred_from": "Any single clean fixture witness.",
        },
        {
            "surface_or_suite": "D-style discriminator pass D1-D8",
            "status": "next experiment layer",
            "reason": "O-style pass provides witnesses but not all falsification baselines.",
            "must_not_be_inferred_from": "O-style fixture support alone.",
        },
    ]


def build_summary(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    checks = _validate_support_inputs(summaries)
    return {
        "experiment": EXPERIMENT_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "support_prechecks": checks,
        "family_conclusion": (
            "The O-style A-G pass partially weakens the anonymous-port null "
            "across controlled artifact classes while preserving Lane A and "
            "clean-fixture boundaries."
        ),
        "strong_supported_themes": [
            "row-local stress signatures",
            "derived column-local proxy observability",
            "explicit Lane B column-H proxy-branch candidate deltas in Lane C",
            "G/Split reconstruction and signed flux J+/J- exactness",
            "Lane A degree-9 saturation bottleneck",
            "column-preserving mechanical refinement",
            "multi-label edge path disagreement",
            "observer-local mixed row/column motion classification",
        ],
        "bounded_or_inconclusive_themes": [
            "near-saturation degree-8 policy",
            "inflow-weighted transfer",
            "identity fission or landscape-general identity",
            "full reusable motion-loader port histories",
            "landscape/seed generality",
            "formal D-style discriminator baselines",
        ],
        "hypothesis_row_count": len(hypothesis_rows(summaries)),
        "experiment_row_count": len(experiment_rows()),
        "prediction_comparison_row_count": len(prediction_comparison_rows()),
        "followup_row_count": len(followup_rows()),
    }


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
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _build_manifest(output_paths: dict[str, Path], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "iteration": 10,
        "script_path": SCRIPT_PATH,
        "command": (
            "PYTHONPATH=src .venv/bin/python "
            f"{SCRIPT_PATH} --write-defaults"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_branch": _git_value(["branch", "--show-current"]),
        "lane_id": LANE_ID,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "input_summary_paths": {
            key: str(path.relative_to(EXPERIMENT_ROOT))
            for key, path in SUMMARY_FILES.items()
        },
        "support_prechecks": summary["support_prechecks"],
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
                "experiments/2026-05-N01-grc9v3-properties/scripts/grc9v3_fixture_harness.py"
            ),
            (
                ".venv/bin/python -m json.tool "
                "experiments/2026-05-N01-grc9v3-properties/outputs/"
                "family_level_synthesis_summary.json"
            ),
        ],
    }


def _write_report(
    path: Path,
    *,
    hypotheses: list[dict[str, str]],
    experiments: list[dict[str, str]],
    predictions: list[dict[str, str]],
    followups: list[dict[str, str]],
    summary: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Family-Level Synthesis",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "This report synthesizes Experiments A-G under the Lane A",
        "`current_hybrid_signed_hessian` baseline. It promotes only claims backed",
        "by generated experiment artifacts and keeps source-intent-only or",
        "unsupported observations out of the supported bucket.",
        "",
        "## Conclusion",
        "",
        summary["family_conclusion"],
        "",
        "The result is not a global proof of GRC9V3 semantics. It is a controlled",
        "O-style witness set that prepares the D-style falsification pass.",
        "",
        "## Experiment Summary",
        "",
        "| Experiment | Theme | Classification | Summary |",
        "| --- | --- | --- | --- |",
    ]
    for row in experiments:
        lines.append(
            "| "
            f"{row['experiment']} | "
            f"{row['theme']} | "
            f"{row['classification']} | "
            f"{row['summary']} |"
        )
    lines.extend(
        [
            "",
            "## Hypothesis Status",
            "",
            "| Hypothesis | Classification | Scope | Boundary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in hypotheses:
        lines.append(
            "| "
            f"{row['hypothesis']} | "
            f"{row['classification']} | "
            f"{row['scope']} | "
            f"{row['boundaries']} |"
        )
    lines.extend(
        [
            "",
            "## Prediction Check",
            "",
            "| Prediction | Observed Result | Evidence |",
            "| --- | --- | --- |",
        ]
    )
    for row in predictions:
        lines.append(
            "| "
            f"{row['prediction']} | "
            f"{row['observed_result']} | "
            f"{row['evidence']} |"
        )
    lines.extend(
        [
            "",
            "## Lane C Comparison",
            "",
            "Lane C was run as an analysis pass over selected clean fixtures. It is not a",
            "runtime lane and does not change Lane A or Lane B.",
            "",
            "Classification:",
            "    `lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries`",
            "",
            "Result:",
            "",
            "- comparison rows: `60`",
            "- Lane A candidates/refinements: `25 / 25`",
            "- Lane B candidates/refinements: `40 / 40`",
            "- direct Lane B column-H proxy-branch rows: `15`",
            "- candidate/refinement delta rows: `15 / 15`",
            "- degree-8 near-saturation remains blocked",
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
            f"{row['must_not_be_inferred_from']} |"
        )
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- Direct column-H proxy-branch spark evidence remains blocked under Lane A and",
            "  available only in explicit `grc9v3_column_h_assisted` Lane B/Lane C artifacts.",
            "- Near-saturation degree-8 policy remains blocked under Lane A.",
            "- Mechanical refinement is not identity fission.",
            "- Configured-window child-basin persistence is not landscape-general identity.",
            "- Exact G/Split reconstruction is not semantic column superiority over arbitrary groupings.",
            "- Edge-label path disagreement is not direct row/column semantic evidence.",
            "- Observer-local motion classification is not reusable motion-loader port-history support.",
            "",
            "## Next Layer",
            "",
            "Proceed to the D-style discriminator pass. D1-D8 should convert these",
            "fixture witnesses into falsification tests against arbitrary S9 relabels,",
            "degree/adjacency baselines, row-only and column-only predictors,",
            "random triples, additive row+column explanations, and stricter identity",
            "persistence windows.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs() -> dict[str, Path]:
    summaries = _load_summaries()
    hypotheses = hypothesis_rows(summaries)
    experiments = experiment_rows()
    predictions = prediction_comparison_rows()
    followups = followup_rows()
    summary = build_summary(summaries)

    hypothesis_path = EXPERIMENT_ROOT / "outputs" / "family_level_hypothesis_status.csv"
    experiment_path = EXPERIMENT_ROOT / "outputs" / "family_level_experiment_status.csv"
    prediction_path = EXPERIMENT_ROOT / "outputs" / "family_level_prediction_check.csv"
    followup_path = EXPERIMENT_ROOT / "outputs" / "family_level_followup_surfaces.csv"
    summary_path = EXPERIMENT_ROOT / "outputs" / "family_level_synthesis_summary.json"
    manifest_path = EXPERIMENT_ROOT / "outputs" / "family_level_synthesis_manifest.json"
    report_path = EXPERIMENT_ROOT / "reports" / "family_level_synthesis.md"
    output_paths = {
        "hypothesis_status_csv": hypothesis_path,
        "experiment_status_csv": experiment_path,
        "prediction_check_csv": prediction_path,
        "followup_surfaces_csv": followup_path,
        "summary_json": summary_path,
        "manifest_json": manifest_path,
        "report_md": report_path,
    }
    _write_csv(hypothesis_path, hypotheses)
    _write_csv(experiment_path, experiments)
    _write_csv(prediction_path, predictions)
    _write_csv(followup_path, followups)
    _write_json(summary_path, summary)
    _write_json(manifest_path, _build_manifest(output_paths, summary))
    _write_report(
        report_path,
        hypotheses=hypotheses,
        experiments=experiments,
        predictions=predictions,
        followups=followups,
        summary=summary,
    )
    return output_paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-defaults", action="store_true")
    args = parser.parse_args()
    if args.write_defaults:
        paths = write_outputs()
        print(json.dumps({key: str(path) for key, path in paths.items()}, indent=2))
    else:
        summaries = _load_summaries()
        print(
            json.dumps(
                {
                    "summary": build_summary(summaries),
                    "hypotheses": hypothesis_rows(summaries),
                    "experiments": experiment_rows(),
                    "predictions": prediction_comparison_rows(),
                    "followups": followup_rows(),
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
