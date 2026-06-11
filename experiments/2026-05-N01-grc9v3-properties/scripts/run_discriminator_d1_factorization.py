"""D1: factorization discriminator over completed O-style artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
from typing import Any

from grc9v3_fixture_harness import (
    ARTIFACT_SCHEMA_VERSION,
    LANE_ID,
    column_permutation_map,
    degree_preserving_random_relabel_map,
    row_permutation_map,
    transpose_map,
)
from discriminator_harness import EVIDENCE_LABELS, manifest_schema


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DISCRIMINATOR_ID = "d1_factorization"
SCRIPT_PATH = (
    "experiments/2026-05-N01-grc9v3-properties/scripts/"
    "run_discriminator_d1_factorization.py"
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
    "c_rows": EXPERIMENT_ROOT / "outputs" / "experiment_c_saturation_rows.csv",
    "d_reassignments": (
        EXPERIMENT_ROOT
        / "outputs"
        / "experiment_d_refinement_identity_reassignments.csv"
    ),
}

STRUCTURED_TRANSFORMS = {
    "identity",
    "row_permutation_231",
    "column_permutation_312",
}
NON_FACTORING_TRANSFORMS = {"degree_preserving_random_relabel"}
TRANSPOSE_TRANSFORMS = {"row_column_transpose"}
FACTORING_CLASSES = {
    "identity": "row_column",
    "row_permutation_231": "row_column",
    "column_permutation_312": "row_column",
    "row_column_transpose": "transpose",
    "degree_preserving_random_relabel": "non_factorized",
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


def _truth(value: str) -> bool:
    return value.strip().lower() == "true"


def _float(value: str, default: float = 0.0) -> float:
    if value == "":
        return default
    if value.lower() == "inf":
        return float("inf")
    return float(value)


def _transform_maps(seed: int) -> dict[str, dict[int, int]]:
    return {
        "identity": {port: port for port in range(1, 10)},
        "row_permutation_231": row_permutation_map((2, 3, 1)),
        "column_permutation_312": column_permutation_map((3, 1, 2)),
        "row_column_transpose": transpose_map(),
        "degree_preserving_random_relabel": degree_preserving_random_relabel_map(
            seed + 1000
        ),
    }


def _inverse_map(port_map: dict[int, int]) -> dict[int, int]:
    return {target: source for source, target in port_map.items()}


def _semantic_relation(transform_id: str) -> str:
    if transform_id == "identity":
        return "identity"
    if transform_id == "row_permutation_231":
        return "structured_row_permutation"
    if transform_id == "column_permutation_312":
        return "structured_column_permutation"
    if transform_id == "row_column_transpose":
        return "transpose_control"
    if transform_id == "degree_preserving_random_relabel":
        return "s9_random_triple_proxy"
    return "unknown_transform"


def _semantic_error_for_match(transform_id: str, matched: bool) -> float:
    if transform_id in STRUCTURED_TRANSFORMS:
        return 0.0 if matched else 1.0
    if transform_id in TRANSPOSE_TRANSFORMS or transform_id in NON_FACTORING_TRANSFORMS:
        return 1.0 if not matched else 0.0
    return 1.0


def _a_records(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        if "balanced" in row["source_fixture_id"]:
            continue
        transform_id = row["transform_id"]
        matched = _truth(row["dominant_row_matches_expected"])
        dominance = _float(row["response_dominance_ratio"])
        records.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "fixture_id": row["source_fixture_id"],
                "run_id": row["fixture_id"],
                "seed": row["seed"],
                "regime": "core_loop_factorization",
                "artifact_class": "row_differential_signature",
                "transform_id": transform_id,
                "factorization_class": FACTORING_CLASSES[transform_id],
                "semantic_relation": _semantic_relation(transform_id),
                "evidence_label": "derived",
                "source_experiment": "A",
                "artifact_source": row["artifact_sources"],
                "expected_value": row["expected_dominant_row"],
                "observed_value": row["dominant_response_row"],
                "observed_match": matched,
                "semantic_error": _semantic_error_for_match(transform_id, matched),
                "value_error": 1.0 - dominance if dominance != float("inf") else 1.0,
                "supports_factorization": transform_id in STRUCTURED_TRANSFORMS and matched,
                "notes": "Row signature reconstructed from row-resolved response artifacts.",
            }
        )
    return records


def _b_records(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        transform_id = row["transform_id"]
        pressure_match = _truth(row["pressure_column_matches_expected"])
        cancellation_match = _truth(row["cancellation_column_matches_expected"])
        matched = pressure_match and cancellation_match
        best_cancellation = max(
            _float(row["column_1_cancellation_score"]),
            _float(row["column_2_cancellation_score"]),
            _float(row["column_3_cancellation_score"]),
        )
        records.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "fixture_id": row["source_fixture_id"],
                "run_id": row["fixture_id"],
                "seed": row["seed"],
                "regime": "core_loop_factorization",
                "artifact_class": "derived_column_cancellation_proxy",
                "transform_id": transform_id,
                "factorization_class": FACTORING_CLASSES[transform_id],
                "semantic_relation": _semantic_relation(transform_id),
                "evidence_label": "derived",
                "source_experiment": "B",
                "artifact_source": row["artifact_sources"],
                "expected_value": row["expected_column"],
                "observed_value": row["dominant_cancellation_column"],
                "observed_match": matched,
                "semantic_error": _semantic_error_for_match(transform_id, matched),
                "value_error": 1.0 - best_cancellation,
                "supports_factorization": transform_id in STRUCTURED_TRANSFORMS and matched,
                "notes": (
                    "Column cancellation is an analysis proxy under Lane A, "
                    "not direct column-H gate evidence."
                ),
            }
        )
    return records


def _c_records(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        transform_id = row["transform_id"]
        candidate_matches = _truth(row["candidate_matches_expected"])
        budget_available = _truth(row["budget_evidence_available"])
        records.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "fixture_id": row["condition_id"],
                "run_id": f"{row['condition_id']}__{transform_id}",
                "seed": row["seed"],
                "regime": "lane_a_spark_capacity",
                "artifact_class": "lane_a_saturation_gate",
                "transform_id": transform_id,
                "factorization_class": FACTORING_CLASSES[transform_id],
                "semantic_relation": "lane_a_gate_invariant",
                "evidence_label": "direct",
                "source_experiment": "C",
                "artifact_source": row["artifact_sources"],
                "expected_value": row["expected_canonical_candidate"],
                "observed_value": row["candidate_event_count"],
                "observed_match": candidate_matches,
                "semantic_error": 0.0 if candidate_matches else 1.0,
                "value_error": 0.0 if candidate_matches else 1.0,
                "supports_factorization": False,
                "notes": (
                    "Lane A saturation gate is expected to be invariant under "
                    "row/column and S9 relabels; report separately from "
                    "factorization-sensitive artifacts."
                ),
                "budget_evidence_available": budget_available,
            }
        )
    return records


def _d_records(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault((row["condition_id"], row["transform_id"]), []).append(row)

    records: list[dict[str, Any]] = []
    for (condition_id, transform_id), group_rows in sorted(grouped.items()):
        by_port = all(_truth(row["column_preserved_by_port"]) for row in group_rows)
        by_module = all(_truth(row["column_preserved_by_module"]) for row in group_rows)
        edge_count = len(group_rows)
        mechanical_match = by_port and by_module and edge_count == 9
        non_factorized = transform_id in NON_FACTORING_TRANSFORMS
        transpose = transform_id in TRANSPOSE_TRANSFORMS
        semantic_error = 1.0 if non_factorized or transpose else 0.0
        records.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "fixture_id": condition_id,
                "run_id": f"{condition_id}__{transform_id}",
                "seed": group_rows[0]["seed"],
                "regime": "mechanical_refinement_convention",
                "artifact_class": "post_refinement_column_mapping",
                "transform_id": transform_id,
                "factorization_class": FACTORING_CLASSES[transform_id],
                "semantic_relation": _semantic_relation(transform_id),
                "evidence_label": "partial" if non_factorized or transpose else "direct",
                "source_experiment": "D",
                "artifact_source": group_rows[0]["artifact_source"],
                "expected_value": "9 column-preserved boundary reassignments",
                "observed_value": str(edge_count),
                "observed_match": mechanical_match,
                "semantic_error": semantic_error,
                "value_error": 0.0 if mechanical_match else 1.0,
                "supports_factorization": (
                    transform_id in STRUCTURED_TRANSFORMS and mechanical_match
                ),
                "notes": (
                    "Mechanical current-port column preservation is direct; "
                    "semantic equivalence under non-factorized S9 relabel is "
                    "not inferred from the mechanical mapping alone."
                ),
            }
        )
    return records


def _aggregate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for record in records:
        key = (
            record["regime"],
            record["artifact_class"],
            record["transform_id"],
            record["factorization_class"],
        )
        grouped.setdefault(key, []).append(record)

    rows: list[dict[str, Any]] = []
    for (regime, artifact_class, transform_id, factorization_class), group in sorted(
        grouped.items()
    ):
        semantic_errors = [float(row["semantic_error"]) for row in group]
        value_errors = [float(row["value_error"]) for row in group]
        observed_matches = [bool(row["observed_match"]) for row in group]
        rows.append(
            {
                "discriminator": DISCRIMINATOR_ID,
                "schema_version": ARTIFACT_SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "regime": regime,
                "artifact_class": artifact_class,
                "transform_id": transform_id,
                "factorization_class": factorization_class,
                "semantic_relation": _semantic_relation(transform_id)
                if artifact_class != "lane_a_saturation_gate"
                else "lane_a_gate_invariant",
                "record_count": len(group),
                "mean_semantic_error": sum(semantic_errors) / len(semantic_errors),
                "mean_value_error": sum(value_errors) / len(value_errors),
                "match_rate": sum(1 for value in observed_matches if value) / len(group),
                "evidence_labels": " ".join(
                    sorted({str(row["evidence_label"]) for row in group})
                ),
                "supports_factorization_count": sum(
                    1 for row in group if bool(row["supports_factorization"])
                ),
                "artifact_sources": " | ".join(
                    sorted({str(row["source_experiment"]) for row in group})
                ),
            }
        )
    return rows


def run_discriminator(seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    missing = [str(path) for path in INPUT_PATHS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing D1 input artifacts: {missing}")
    harness_schema = json.loads(
        INPUT_PATHS["harness_schema"].read_text(encoding="utf-8")
    )

    records = [
        *_a_records(_read_csv(INPUT_PATHS["a_rows"])),
        *_b_records(_read_csv(INPUT_PATHS["b_rows"])),
        *_c_records(_read_csv(INPUT_PATHS["c_rows"])),
        *_d_records(_read_csv(INPUT_PATHS["d_reassignments"])),
    ]
    matrix_rows = _aggregate(records)

    factorization_sensitive = [
        row
        for row in matrix_rows
        if row["artifact_class"]
        in {"row_differential_signature", "derived_column_cancellation_proxy"}
    ]
    structured_errors = [
        float(row["mean_semantic_error"])
        for row in factorization_sensitive
        if row["transform_id"] in STRUCTURED_TRANSFORMS
    ]
    s9_errors = [
        float(row["mean_semantic_error"])
        for row in factorization_sensitive
        if row["transform_id"] in NON_FACTORING_TRANSFORMS
    ]
    summary = {
        "discriminator": DISCRIMINATOR_ID,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "seed": seed,
        "input_paths": {
            key: str(path.relative_to(EXPERIMENT_ROOT))
            for key, path in INPUT_PATHS.items()
        },
        "transform_maps": {
            transform_id: mapping for transform_id, mapping in _transform_maps(seed).items()
        },
        "inverse_transform_maps": {
            transform_id: _inverse_map(mapping)
            for transform_id, mapping in _transform_maps(seed).items()
        },
        "record_count": len(records),
        "matrix_row_count": len(matrix_rows),
        "structured_factorization_mean_error": (
            sum(structured_errors) / len(structured_errors)
        ),
        "s9_factorization_mean_error": sum(s9_errors) / len(s9_errors),
        "s9_error_exceeds_structured_error": (
            sum(s9_errors) / len(s9_errors)
            > sum(structured_errors) / len(structured_errors)
        ),
        "lane_a_gate_reported_separately": True,
        "mechanical_refinement_convention_reported_separately": True,
        "random_triple_control_status": (
            "proxied_by_degree_preserving_random_relabel_as_non_factorized_grouping"
        ),
        "shared_harness_schema_path": str(
            INPUT_PATHS["harness_schema"].relative_to(EXPERIMENT_ROOT)
        ),
        "shared_harness_schema_version": harness_schema["schema_version"],
        "shared_harness_expected_outputs": harness_schema["expected_outputs"]["D1"],
        "classification": "supported_with_lane_a_boundaries",
        "claim_scope": (
            "D1 supports higher semantic error for non-factorized S9/random-triple "
            "controls on row/column-sensitive artifacts. Lane A saturation and "
            "mechanical refinement convention artifacts are reported separately."
        ),
        "manifest_required_fields": list(manifest_schema()),
        "evidence_labels_preserved": list(EVIDENCE_LABELS),
    }
    return matrix_rows, records, summary


def blocked_observation_lines() -> list[str]:
    return [
        "# D1 Blocked And Inconclusive Observations",
        "",
        "| Observation | Status | Evidence Surface | Notes |",
        "| --- | --- | --- | --- |",
        "| dedicated random-triple runtime replay | inconclusive | O-style transform outputs | D1 uses the degree-preserving non-factorized S9 relabel as a random-triple proxy; no new runtime replay was added. |",
        "| direct column-H factorization | blocked | Lane A runtime | Column-H/cancellation remains derived under Lane A and is not counted as direct spark-gate evidence. |",
        "| post-refinement S9 semantic equivalence | inconclusive | Experiment D mechanical mapping | Mechanical current-port column preservation is direct, but semantic equivalence under non-factorized relabel is not inferred. |",
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
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _build_manifest(
    *,
    seed: int,
    summary: dict[str, Any],
    output_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "discriminator_id": DISCRIMINATOR_ID,
        "iteration": 2,
        "script_path": SCRIPT_PATH,
        "command": (
            "PYTHONPATH=src .venv/bin/python "
            f"{SCRIPT_PATH} --write-defaults --seed {seed}"
        ),
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_branch": _git_value(["branch", "--show-current"]),
        "lane_id": LANE_ID,
        "seed": seed,
        "runtime_params": "reused_completed_o_style_outputs",
        "fixture_ids": "recorded per d1_transform_pair_records.jsonl row",
        "transform_ids": sorted(FACTORING_CLASSES),
        "port_mappings": summary["transform_maps"],
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_source_map": summary["input_paths"],
        "evidence_labels": summary["evidence_labels_preserved"],
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
                "d1_factorization_summary.json"
            ),
        ],
    }


def _write_report(
    path: Path,
    *,
    matrix_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows_for_report = [
        row
        for row in matrix_rows
        if row["artifact_class"]
        in {
            "row_differential_signature",
            "derived_column_cancellation_proxy",
            "lane_a_saturation_gate",
            "post_refinement_column_mapping",
        }
    ]
    lines = [
        "# D1 Factorization Discriminator",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "D1 reuses completed O-style outputs to test whether structured",
        "row/column transforms preserve semantic artifacts better than a",
        "non-factorized S9 relabel. It does not add runtime behavior.",
        "",
        "This run is based on the shared Iteration 1 discriminator harness",
        f"`{summary['shared_harness_schema_path']}`.",
        "",
        "Lane A saturation and mechanical refinement convention artifacts are",
        "reported separately from factorization-sensitive row/column artifacts.",
        "",
        "## Semantic Error Metric",
        "",
        "`semantic_error = 0.0` means the transformed artifact preserves the",
        "expected row/column semantic class for the relevant structured transform",
        "or control.",
        "",
        "`semantic_error = 1.0` means the transformed or regrouped artifact no",
        "longer preserves the expected predefined row/column semantic class.",
        "",
        "The S9/random-triple control is a sampled non-factorized proxy generated",
        "from the deterministic degree-preserving random relabel in the shared",
        "fixture harness. It is not an exhaustive statement over all `9!`",
        "relabelings.",
        "",
        "## Result",
        "",
        "- classification: "
        f"`{summary['classification']}`",
        "- structured factorization mean semantic error: "
        f"`{summary['structured_factorization_mean_error']:.12g}`",
        "- S9/random-triple-proxy mean semantic error: "
        f"`{summary['s9_factorization_mean_error']:.12g}`",
        "- S9 error exceeds structured error: "
        f"`{json.dumps(summary['s9_error_exceeds_structured_error'])}`",
        "",
        "## Equivariance Matrix",
        "",
        "| Regime | Artifact | Transform | Evidence | Mean Semantic Error | Match Rate |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for row in rows_for_report:
        lines.append(
            "| "
            f"{row['regime']} | "
            f"{row['artifact_class']} | "
            f"{row['transform_id']} | "
            f"{row['evidence_labels']} | "
            f"{float(row['mean_semantic_error']):.12g} | "
            f"{float(row['match_rate']):.12g} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "D1 supports the factorization claim for row/column-sensitive artifacts:",
            "structured row and column transforms preserve the expected row and",
            "derived-column signatures, while the non-factorized S9 relabel has",
            "higher semantic error.",
            "",
            "The Lane A saturation gate is direct runtime evidence but is expected to",
            "be invariant under row/column and S9 relabels, so it is not counted as",
            "factorization evidence.",
            "",
            "Post-refinement column preservation is direct mechanical evidence. It is",
            "reported separately because current-port column preservation does not",
            "by itself establish semantic equivalence under non-factorized S9",
            "relabeling.",
            "",
            "## Evidence Labels",
            "",
            "- row differential signature: derived from Experiment A artifacts",
            "- column cancellation proxy: derived under Lane A from Experiment B",
            "- Lane A saturation gate: direct candidate/event evidence from Experiment C",
            "- post-refinement mapping: direct mechanical mapping, partial as S9 semantic evidence",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(seed: int) -> dict[str, Path]:
    matrix_rows, records, summary = run_discriminator(seed)
    matrix_path = EXPERIMENT_ROOT / "outputs" / "d1_equivariance_matrix.csv"
    records_path = EXPERIMENT_ROOT / "outputs" / "d1_transform_pair_records.jsonl"
    summary_path = EXPERIMENT_ROOT / "outputs" / "d1_factorization_summary.json"
    manifest_path = EXPERIMENT_ROOT / "outputs" / "d1_factorization_manifest.json"
    report_path = EXPERIMENT_ROOT / "reports" / "d1_artifact_distance_report.md"
    blocked_path = EXPERIMENT_ROOT / "reports" / "d1_blocked_observations.md"
    output_paths = {
        "equivariance_matrix_csv": matrix_path,
        "transform_pair_records_jsonl": records_path,
        "summary_json": summary_path,
        "manifest_json": manifest_path,
        "artifact_distance_report_md": report_path,
        "blocked_observations_md": blocked_path,
    }
    _write_csv(matrix_path, matrix_rows)
    _write_jsonl(records_path, records)
    _write_json(summary_path, summary)
    _write_json(
        manifest_path,
        _build_manifest(seed=seed, summary=summary, output_paths=output_paths),
    )
    _write_report(report_path, matrix_rows=matrix_rows, summary=summary)
    blocked_path.parent.mkdir(parents=True, exist_ok=True)
    blocked_path.write_text(
        "\n".join(blocked_observation_lines()) + "\n",
        encoding="utf-8",
    )
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
        matrix_rows, records, summary = run_discriminator(args.seed)
        print(
            json.dumps(
                {
                    "summary": summary,
                    "matrix": matrix_rows,
                    "records": records,
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
