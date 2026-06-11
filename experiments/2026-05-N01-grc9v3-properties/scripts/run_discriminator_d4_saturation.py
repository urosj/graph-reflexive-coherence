"""D4: saturation discriminator over completed Experiment C artifacts."""

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
DISCRIMINATOR_ID = "d4_saturation"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_discriminator_d4_saturation.py"
)

INPUT_PATHS = {
    "harness_schema": (
        EXPERIMENT_ROOT / "outputs" / "discriminator_harness_schema.json"
    ),
    "c_rows": EXPERIMENT_ROOT / "outputs" / "experiment_c_saturation_rows.csv",
    "c_summary": (
        EXPERIMENT_ROOT / "outputs" / "experiment_c_saturation_summary.json"
    ),
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


def _int(value: str, default: int = 0) -> int:
    if value == "":
        return default
    return int(value)


def _float(value: str, default: float = 0.0) -> float:
    if value == "":
        return default
    return float(value)


def _best_column_pressure(row: dict[str, str]) -> float:
    return max(
        _float(row["column_1_pressure"]),
        _float(row["column_2_pressure"]),
        _float(row["column_3_pressure"]),
    )


def _best_column_cancellation(row: dict[str, str]) -> float:
    return max(
        _float(row["column_1_cancellation_score"]),
        _float(row["column_2_cancellation_score"]),
        _float(row["column_3_cancellation_score"]),
    )


def gate_table(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output_rows: list[dict[str, Any]] = []
    for row in rows:
        candidate_count = _int(row["candidate_event_count"])
        refinement_count = _int(row["refinement_event_count"])
        budget_error = row["budget_error"]
        output_rows.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "seed": row["seed"],
                "condition_id": row["condition_id"],
                "condition_class": row["condition_class"],
                "transform_id": row["transform_id"],
                "active_degree": _int(row["active_degree"]),
                "inactive_ports": row["inactive_ports"],
                "inactive_port_count": _int(row["inactive_port_count"]),
                "is_sink_before": _truth(row["is_sink_before"]),
                "basin_id_before": row["basin_id_before"],
                "gradient_norm": _float(row["gradient_norm"]),
                "eps_gradient": _float(row["eps_gradient"]),
                "basin_interior_gate": _truth(row["basin_interior_gate"]),
                "min_signed_hessian": _float(row["min_signed_hessian"]),
                "eps_spark": _float(row["eps_spark"]),
                "signed_hessian_degeneracy_gate": _truth(
                    row["signed_hessian_degeneracy_gate"]
                ),
                "saturation_gate": _truth(row["saturation_gate"]),
                "canonical_candidate_predicate": _truth(
                    row["canonical_candidate_predicate"]
                ),
                "candidate_event_count": candidate_count,
                "refinement_event_count": refinement_count,
                "candidate_matches_expected": _truth(
                    row["candidate_matches_expected"]
                ),
                "candidate_event_steps": row["candidate_event_step_indices"],
                "event_sequence": row["event_sequence"],
                "budget_before": row["budget_before"],
                "budget_after": row["budget_after"],
                "budget_error": budget_error,
                "budget_tolerance": row["budget_tolerance"],
                "budget_evidence_available": _truth(
                    row["budget_evidence_available"]
                ),
                "budget_evidence_source": row["budget_evidence_source"],
                "reassignment_map_available": _truth(
                    row["reassignment_map_available"]
                ),
                "reassignment_edge_count": _int(row["reassignment_edge_count"]),
                "near_saturation_policy": row["near_saturation_policy"],
                "derived_column_diagnostic_role": row[
                    "derived_column_diagnostic_role"
                ],
                "best_column_pressure": _best_column_pressure(row),
                "best_column_cancellation": _best_column_cancellation(row),
                "d4_gate_interpretation": _interpret_row(row),
                "evidence_label": "direct",
                "artifact_sources": row["artifact_sources"],
            }
        )
    return output_rows


def _interpret_row(row: dict[str, str]) -> str:
    degree = _int(row["active_degree"])
    stressed = _truth(row["signed_hessian_degeneracy_gate"])
    saturated = _truth(row["saturation_gate"])
    candidate = _int(row["candidate_event_count"]) > 0
    refinement = _int(row["refinement_event_count"]) > 0
    if degree in (7, 8) and stressed and not candidate and not refinement:
        return "stress_without_fullness_does_not_trigger"
    if degree == 9 and stressed and saturated and candidate and refinement:
        return "saturation_plus_instability_triggers_lane_a_expansion"
    if degree == 9 and saturated and not stressed and not candidate and not refinement:
        return "fullness_without_instability_does_not_trigger"
    return "reported_without_stronger_d4_claim"


def summary_payload(
    table_rows: list[dict[str, Any]],
    c_summary: dict[str, Any],
) -> dict[str, Any]:
    identity_rows = [
        row for row in table_rows if row["transform_id"] == "identity"
    ]
    degree7_or_8_stressed = [
        row
        for row in identity_rows
        if row["condition_class"] == "same_instability_without_saturation"
    ]
    degree9_positive = [
        row
        for row in identity_rows
        if row["condition_class"] == "canonical_saturation_with_instability"
    ]
    stable_fullness = [
        row
        for row in identity_rows
        if row["condition_class"] == "same_saturation_without_instability"
    ]
    all_rows_match = all(row["candidate_matches_expected"] for row in table_rows)
    transforms_by_condition: dict[str, list[dict[str, Any]]] = {}
    for row in table_rows:
        transforms_by_condition.setdefault(row["condition_id"], []).append(row)
    transform_invariant = all(
        len({row["candidate_event_count"] for row in group}) == 1
        and len({row["refinement_event_count"] for row in group}) == 1
        for group in transforms_by_condition.values()
    )
    return {
        "discriminator_id": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "classification": "supported_with_lane_a_boundaries",
        "canonical_gate_formula": c_summary["canonical_gate_formula"],
        "candidate_detection_matches_formula_all_rows": all_rows_match,
        "active_degree_7_or_8_stressed_nontrigger": all(
            row["candidate_event_count"] == 0 and row["refinement_event_count"] == 0
            for row in degree7_or_8_stressed
        ),
        "degree_9_stressed_candidate": all(
            row["candidate_event_count"] == 1 for row in degree9_positive
        ),
        "degree_9_stressed_refines": all(
            row["refinement_event_count"] == 1 for row in degree9_positive
        ),
        "degree_9_without_instability_nontrigger": all(
            row["candidate_event_count"] == 0 and row["refinement_event_count"] == 0
            for row in stable_fullness
        ),
        "fullness_alone_insufficient": all(
            row["candidate_event_count"] == 0 and row["refinement_event_count"] == 0
            for row in stable_fullness
        ),
        "signed_hessian_stress_without_saturation_insufficient": all(
            row["candidate_event_count"] == 0 and row["refinement_event_count"] == 0
            for row in degree7_or_8_stressed
        ),
        "budget_evidence_available_for_canonical_positive": all(
            row["budget_evidence_available"] for row in degree9_positive
        ),
        "canonical_positive_budget_error": c_summary[
            "canonical_positive_budget_error"
        ],
        "budget_tolerance": c_summary["budget_tolerance"],
        "canonical_positive_budget_within_tolerance": c_summary[
            "canonical_positive_budget_within_tolerance"
        ],
        "near_saturation_policy": c_summary["near_saturation_policy"],
        "derived_column_diagnostic_role": c_summary["derived_column_diagnostic_role"],
        "transform_candidate_refinement_invariance": transform_invariant,
        "transform_invariance_interpretation": c_summary[
            "transform_invariance_interpretation"
        ],
        "identity_row_count": len(identity_rows),
        "all_transform_row_count": len(table_rows),
        "evidence_label": "direct",
        "boundary": (
            "D4 formalizes Lane A active-degree saturation plus signed-Hessian "
            "degeneracy evidence. It does not claim direct column-H gating or "
            "near-saturation behavior."
        ),
    }


def blocked_observations() -> list[dict[str, str]]:
    return [
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "direct column-H saturation gate",
            "status": "blocked",
            "artifact_source": "Lane A Experiment C rows",
            "reconstruction_attempt": "Checked derived column diagnostic fields and Lane A gate formula.",
            "notes": "Current gate is active degree plus basin-interior and signed-Hessian degeneracy; canonical column-H is a deferred Lane B.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "active-degree-8 near-saturation policy",
            "status": "blocked",
            "artifact_source": "near_saturation_policy field",
            "reconstruction_attempt": "Read Experiment C near_saturation_policy for all rows.",
            "notes": "Experiment C records not_implemented_in_lane_a; D4 reports canonical and optional near-saturation separately.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "column diagnostic as gate evidence",
            "status": "blocked",
            "artifact_source": "derived_column_diagnostic_v1",
            "reconstruction_attempt": "Extracted column pressure and cancellation diagnostics.",
            "notes": "Column diagnostics are analysis_diagnostic_only under Lane A and are not used as the gate predicate.",
        },
        {
            "discriminator_id": DISCRIMINATOR_ID,
            "observation": "identity-level consequence of D4 expansion",
            "status": "inconclusive",
            "artifact_source": "Experiment C event rows",
            "reconstruction_attempt": "Checked completed identity event count and child-basin fields.",
            "notes": "D4 classifies event-level mechanical expansion only; identity emergence belongs to D8.",
        },
    ]


def _write_blocked_report(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# D4 Blocked Observations",
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
    table_rows: list[dict[str, Any]],
) -> None:
    identity_rows = [row for row in table_rows if row["transform_id"] == "identity"]
    lines = [
        "# D4 Saturation Discriminator Report",
        "",
        "Status: complete.",
        "",
        "Classification: `supported_with_lane_a_boundaries`.",
        "",
        "## Scope",
        "",
        "D4 reuses completed Experiment C saturation artifacts and does not add",
        "runtime behavior. The canonical Lane A gate is:",
        "",
        f"```text\n{summary['canonical_gate_formula']}\n```",
        "",
        "This is saturation plus basin-interior / signed-Hessian degeneracy",
        "evidence. It is not direct column-H gating.",
        "",
        "## Canonical Identity Rows",
        "",
        "| Condition | Degree | Instability | Saturated | Candidate | Refinement | Budget Evidence | Interpretation |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in identity_rows:
        lines.append(
            "| "
            f"{row['condition_id']} | "
            f"{row['active_degree']} | "
            f"{row['signed_hessian_degeneracy_gate']} | "
            f"{row['saturation_gate']} | "
            f"{row['candidate_event_count']} | "
            f"{row['refinement_event_count']} | "
            f"{row['budget_evidence_available']} | "
            f"{row['d4_gate_interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- degree 7/8 stressed nontrigger: `{summary['active_degree_7_or_8_stressed_nontrigger']}`",
            f"- degree 9 stressed candidate: `{summary['degree_9_stressed_candidate']}`",
            f"- degree 9 stressed refinement: `{summary['degree_9_stressed_refines']}`",
            f"- degree 9 stable-Hessian nontrigger: `{summary['degree_9_without_instability_nontrigger']}`",
            f"- fullness alone insufficient: `{summary['fullness_alone_insufficient']}`",
            f"- signed-Hessian stress without saturation insufficient: `{summary['signed_hessian_stress_without_saturation_insufficient']}`",
            f"- candidate detection matches formula for all rows: `{summary['candidate_detection_matches_formula_all_rows']}`",
            f"- transform candidate/refinement invariance: `{summary['transform_candidate_refinement_invariance']}`",
            "",
            "## Budget",
            "",
            f"- canonical positive budget error: `{summary['canonical_positive_budget_error']}`",
            f"- budget tolerance: `{summary['budget_tolerance']}`",
            f"- within tolerance: `{summary['canonical_positive_budget_within_tolerance']}`",
            "",
            "## Near-Saturation And Column-H",
            "",
            f"- near-saturation policy: `{summary['near_saturation_policy']}`",
            f"- derived column diagnostic role: `{summary['derived_column_diagnostic_role']}`",
            "",
            "The degree-8 near-saturation policy remains blocked under Lane A.",
            "The column diagnostic is reported separately as an analysis",
            "diagnostic and is not used as direct gate evidence.",
            "",
            "## Interpretation",
            "",
            "D4 supports the Lane A saturation bottleneck discriminator. Degree 7",
            "and degree 8 stressed fixtures do not trigger despite matching the",
            "central signed-Hessian degeneracy of the positive run. The degree 9",
            "stressed fixture triggers one candidate and one mechanical expansion",
            "with budget evidence. The degree 9 stable-Hessian control shows that",
            "fullness alone is insufficient.",
            "",
            "Transform invariance is expected for this Lane A gate and is reported",
            "as capacity/signed-Hessian behavior, not row/column factorization",
            "evidence.",
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
    c_rows = _read_csv(INPUT_PATHS["c_rows"])
    c_summary = _read_json(INPUT_PATHS["c_summary"])
    table_rows = gate_table(c_rows)
    summary = summary_payload(table_rows, c_summary)
    blocked = blocked_observations()

    outputs = {
        "gate_table": EXPERIMENT_ROOT / "outputs" / "d4_saturation_gate_table.csv",
        "summary": EXPERIMENT_ROOT / "outputs" / "d4_saturation_summary.json",
        "manifest": EXPERIMENT_ROOT / "outputs" / "d4_saturation_manifest.json",
        "report": EXPERIMENT_ROOT / "reports" / "d4_saturation_report.md",
        "blocked": EXPERIMENT_ROOT / "reports" / "d4_blocked_observations.md",
    }
    _write_csv(outputs["gate_table"], table_rows)
    _write_json(outputs["summary"], summary)
    _write_blocked_report(outputs["blocked"], blocked)
    _write_report(outputs["report"], summary, table_rows)

    manifest = {
        "discriminator_id": DISCRIMINATOR_ID,
        "iteration": "5",
        "script_path": SCRIPT_PATH,
        "command": (
            "python experiments/2026-05-N01-grc9v3-properties/scripts/"
            "run_discriminator_d4_saturation.py --write-defaults"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_status_short": _git_value(["status", "--short"]),
        "lane_id": LANE_ID,
        "fixture_id": [
            "C1_degree_7_stressed",
            "C2_degree_8_stressed",
            "C3_degree_9_stressed",
            "C5_degree_9_stable_hessian",
        ],
        "transform_id": [
            "identity",
            "row_permutation_231",
            "column_permutation_312",
            "row_column_transpose",
            "degree_preserving_random_relabel",
        ],
        "seed": 0,
        "runtime_params": {
            "mode": "reuse_completed_experiment_c_outputs",
            "runtime_mutation": "none",
            "canonical_gate_formula": summary["canonical_gate_formula"],
            "near_saturation_policy": summary["near_saturation_policy"],
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
        c_rows = _read_csv(INPUT_PATHS["c_rows"])
        c_summary = _read_json(INPUT_PATHS["c_summary"])
        print(
            json.dumps(
                summary_payload(gate_table(c_rows), c_summary),
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
