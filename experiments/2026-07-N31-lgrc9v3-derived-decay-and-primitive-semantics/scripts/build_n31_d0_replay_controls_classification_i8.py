#!/usr/bin/env python3
"""Build N31 Iteration 8 replay, controls, and D0 classification artifacts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

from pygrc.models import (
    LGRC9V3,
    digest_lgrc9v3_restoration_identity_v1,
    digest_lgrc9v3_restoration_identity_v2,
)


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
ARTIFACT_DIR = OUTPUTS / "n31_i8_d0_replay_control_artifacts"
PREREGISTRATION = ARTIFACT_DIR / "n31_i8_replay_and_amount_sweep_preregistration.json"
TRACE = OUTPUTS / "n31_i8_d0_replay_control_trace.json"
OUTPUT = OUTPUTS / "n31_d0_replay_controls_classification_i8.json"
REPORT = REPORTS / "n31_d0_replay_controls_classification_i8.md"
I3 = OUTPUTS / "n31_active_nulls_and_failure_baselines_i3.json"
I5 = OUTPUTS / "n31_d0c_instantaneous_geometry_comparator_i5.json"
I6 = OUTPUTS / "n31_d0b_finite_window_derived_relation_i6.json"
I7 = OUTPUTS / "n31_d0a_source_current_causal_probe_i7.json"
I7_TRACE = OUTPUTS / "n31_i7_d0a_source_current_causal_trace.json"
I7_SCRIPT = EXPERIMENT / "scripts" / "build_n31_d0a_source_current_causal_probe_i7.py"
SOURCE_BUILDERS = {
    "I3": (
        EXPERIMENT / "scripts" / "build_n31_active_nulls_and_failure_baselines_i3.py",
        I3,
    ),
    "I5": (
        EXPERIMENT / "scripts" / "build_n31_d0c_instantaneous_geometry_comparator_i5.py",
        I5,
    ),
    "I6": (
        EXPERIMENT / "scripts" / "build_n31_d0b_finite_window_derived_relation_i6.py",
        I6,
    ),
    "I7": (I7_SCRIPT, I7),
}
SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_d0_replay_controls_classification_i8.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
GOVERNANCE_BASE_REVISION = "42a760376c630fc9d9797ef2d85848b5af628a17"

SOURCE_IDENTITIES = {
    I3: (
        "e95b230d76113691d71282e227c61da15a5a1f7d5fa89c194af26ae4d653ddea",
        "b41d43e6b0a0e411b488ce7a9692ccd9183b9a023da4d479cd2f531e3de026ff",
    ),
    I5: (
        "95d1a1f2c3003a7eeaa1edeaf9a0e843ac92e2c4af010e04a045233b445ac88b",
        "6b4707cd8b7a10d563cb55f5b61fd4d857161c7b644218ed18cdc7b541be7704",
    ),
    I6: (
        "206088cbe96bb37e119aa88a543f728170d206ad3ce15e9da24f1b9a5f77313a",
        "a076c8d78adeb0a92b0d28f1393f73a0e7731e9a39f16374b94d37b69ebf0a22",
    ),
    I7: (
        "ada29118f7c3cad7db308ff0c026ee09270afbad620c3a613d378f28c35086d1",
        "873bbb8bc74aec376ead0b824e8078f4f837ce33cdc558394d031d3d522458e9",
    ),
    I7_TRACE: (
        "f70e6424ef15185968d21a8485f975dcc19078815ce9059b88d6d83d845d9a0a",
        "5826425cc80c2fa6951d59f9d5099f101e018a06e63e0ace973235efd1540ede",
    ),
}

READOUT_AMOUNTS = (0.18, 0.20, 0.21, 0.22, 0.24, 0.25, 0.26)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def git_diff_empty(path: str) -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--quiet", GOVERNANCE_BASE_REVISION, "--", path],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    return value.get("output_digest") == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def source_record(path: Path) -> dict[str, Any]:
    value = load_json(path)
    expected_digest, expected_sha = SOURCE_IDENTITIES[path]
    return {
        "path": relative(path),
        "status": value.get("status", "not_recorded"),
        "acceptance_state": value.get("acceptance_state", "not_recorded"),
        "expected_output_digest": expected_digest,
        "actual_output_digest": value.get("output_digest"),
        "internal_output_digest_exact": internal_output_digest_exact(value),
        "expected_sha256": expected_sha,
        "actual_sha256": sha256_file(path),
        "identity_exact": value.get("output_digest") == expected_digest
        and sha256_file(path) == expected_sha,
    }


def import_i7_module() -> Any:
    spec = importlib.util.spec_from_file_location("n31_i7_runtime_probe", I7_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load N31 I7 runtime builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest_rows(value: Any) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "artifact_manifest" and isinstance(item, list):
                for row in item:
                    if (
                        isinstance(row, dict)
                        and isinstance(row.get("path"), str)
                        and isinstance(row.get("sha256"), str)
                    ):
                        rows.append(
                            {
                                "path": row["path"],
                                "sha256": row["sha256"],
                                "artifact_role": str(
                                    row.get("artifact_role", "not_recorded")
                                ),
                            }
                        )
            rows.extend(manifest_rows(item))
    elif isinstance(value, list):
        for item in value:
            rows.extend(manifest_rows(item))
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        unique[(row["path"], row["sha256"])] = row
    return [unique[key] for key in sorted(unique)]


def artifact_replay(sources: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for source in sources:
        source_path = ROOT / source["path"]
        for item in manifest_rows(load_json(source_path)):
            path = ROOT / item["path"]
            rows.append(
                {
                    **item,
                    "exists": path.exists(),
                    "actual_sha256": sha256_file(path) if path.exists() else None,
                    "sha256_exact": path.exists()
                    and sha256_file(path) == item["sha256"],
                }
            )
    unique_paths = {row["path"] for row in rows}
    return {
        "source_output_identity_exact": all(
            row["identity_exact"] and row["internal_output_digest_exact"]
            for row in sources
        ),
        "manifest_reference_count": len(rows),
        "unique_artifact_path_count": len(unique_paths),
        "duplicate_reference_count": len(rows) - len(unique_paths),
        "manifest_rows": rows,
        "all_reference_hashes_exact": bool(rows)
        and all(row["sha256_exact"] for row in rows),
    }


def source_builder_replay() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for source_iteration, (script, output) in SOURCE_BUILDERS.items():
        before_sha = sha256_file(output)
        before_digest = load_json(output)["output_digest"]
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        after_sha = sha256_file(output)
        after_value = load_json(output)
        rows.append(
            {
                "source_iteration": source_iteration,
                "script": relative(script),
                "output": relative(output),
                "return_code": result.returncode,
                "stderr": result.stderr,
                "before_sha256": before_sha,
                "after_sha256": after_sha,
                "before_output_digest": before_digest,
                "after_output_digest": after_value["output_digest"],
                "internal_output_digest_exact": internal_output_digest_exact(
                    after_value
                ),
                "byte_identical": before_sha == after_sha,
            }
        )
    return {
        "scope": (
            "all positive D0 builders and the I3 active-null builder replayed "
            "directly; I2/I4 governance and representation dependencies verified "
            "transitively through exact source-chain identities"
        ),
        "directly_replayed_iterations": ["I3", "I5", "I6", "I7"],
        "transitively_verified_dependencies": ["I2", "I3R1", "I4", "I4R1", "I5R1"],
        "entire_evidence_stack_directly_rebuilt": False,
        "rows": rows,
        "all_source_builders_replayed_exact": all(
            row["return_code"] == 0
            and row["byte_identical"]
            and row["before_output_digest"] == row["after_output_digest"]
            and row["internal_output_digest_exact"]
            for row in rows
        ),
    }


def snapshot_roundtrip_replay(i7: dict[str, Any]) -> dict[str, Any]:
    snapshot_rows = [
        row
        for row in manifest_rows(i7)
        if row["artifact_role"].endswith("_snapshot")
    ]
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for index, row in enumerate(snapshot_rows):
            source = ROOT / row["path"]
            model = LGRC9V3.load(str(source))
            before_v1 = digest_lgrc9v3_restoration_identity_v1(model)
            before_v2 = digest_lgrc9v3_restoration_identity_v2(model)
            roundtrip = Path(temp_dir) / f"roundtrip_{index}.json"
            model.save(str(roundtrip))
            restored = LGRC9V3.load(str(roundtrip))
            results.append(
                {
                    "source_path": row["path"],
                    "restoration_identity_v1_exact": before_v1
                    == digest_lgrc9v3_restoration_identity_v1(restored),
                    "restoration_identity_v2_exact": before_v2
                    == digest_lgrc9v3_restoration_identity_v2(restored),
                }
            )
    return {
        "snapshot_row_count": len(results),
        "rows": results,
        "all_snapshot_roundtrips_exact": bool(results)
        and all(
            row["restoration_identity_v1_exact"]
            and row["restoration_identity_v2_exact"]
            for row in results
        ),
        "reset_sensitive_row_count": 0,
        "reset_aware_identity_policy": (
            "v2_verified_on_roundtrip; reset execution not applicable because no "
            "consumed candidate invokes reset"
        ),
    }


def reconstruct_attempt(module: Any, mode: str, amount: float) -> dict[str, Any]:
    module.READOUT_PACKET_AMOUNT = amount
    model = module.build_attempt_model(mode)
    baseline = module.route_state(model)
    formation_receipts = module.process_exact_events(model, 2)
    formed = module.route_state(model)
    persistence_receipts = module.process_exact_events(model, 2)
    persisted = module.route_state(model)
    progression_receipts = module.process_exact_events(model, 2)
    progressed = module.route_state(model)
    readout = module.readout(model)
    return {
        "attempt_mode": mode,
        "readout_amount": amount,
        "baseline": baseline,
        "formed": formed,
        "persisted": persisted,
        "progressed": progressed,
        "formation_receipts": formation_receipts,
        "persistence_receipts": persistence_receipts,
        "progression_receipts": progression_receipts,
        "readout": readout,
    }


def selected_attempt_projection(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: row[key]
        for key in (
            "attempt_mode",
            "baseline",
            "formed",
            "persisted",
            "progressed",
            "formation_receipts",
            "persistence_receipts",
            "progression_receipts",
            "readout",
        )
    }


def execution_reconstruction(module: Any, i7_trace: dict[str, Any]) -> dict[str, Any]:
    source = {row["attempt_mode"]: row for row in i7_trace["attempt_rows"]}
    rows: list[dict[str, Any]] = []
    for mode in module.ATTEMPT_MODES:
        first = reconstruct_attempt(module, mode, 0.22)
        second = reconstruct_attempt(module, mode, 0.22)
        source_projection = selected_attempt_projection(source[mode])
        first_projection = selected_attempt_projection(first)
        second_projection = selected_attempt_projection(second)
        rows.append(
            {
                "attempt_mode": mode,
                "source_digest": digest_value(source_projection),
                "first_reconstruction_digest": digest_value(first_projection),
                "second_reconstruction_digest": digest_value(second_projection),
                "source_reconstruction_exact": source_projection == first_projection,
                "duplicate_reconstruction_exact": first_projection
                == second_projection,
            }
        )
    module.READOUT_PACKET_AMOUNT = 0.22
    return {
        "rows": rows,
        "execution_reconstruction_status": (
            "passed_complete"
            if all(row["source_reconstruction_exact"] for row in rows)
            else "failed"
        ),
        "duplicate_replay_status": (
            "passed"
            if all(row["duplicate_reconstruction_exact"] for row in rows)
            else "failed"
        ),
    }


def equal_state_continuation(module: Any) -> dict[str, Any]:
    module.READOUT_PACKET_AMOUNT = 0.22
    model = module.build_attempt_model("disjoint_hold")
    module.process_exact_events(model, 6)
    with tempfile.TemporaryDirectory() as temp_dir:
        snapshot = Path(temp_dir) / "equal_state_branch.json"
        model.save(str(snapshot))
        left = LGRC9V3.load(str(snapshot))
        right = LGRC9V3.load(str(snapshot))
        before_v1_equal = digest_lgrc9v3_restoration_identity_v1(left) == (
            digest_lgrc9v3_restoration_identity_v1(right)
        )
        before_v2_equal = digest_lgrc9v3_restoration_identity_v2(left) == (
            digest_lgrc9v3_restoration_identity_v2(right)
        )
        left_readout = module.readout(left)
        right_readout = module.readout(right)
        after_v1_equal = digest_lgrc9v3_restoration_identity_v1(left) == (
            digest_lgrc9v3_restoration_identity_v1(right)
        )
        after_v2_equal = digest_lgrc9v3_restoration_identity_v2(left) == (
            digest_lgrc9v3_restoration_identity_v2(right)
        )
    return {
        "branch_source": "same_complete_disjoint_hold_pre_readout_snapshot",
        "direction_matrix_consumed_as_equal_state": False,
        "scientific_role": "replay_correctness_only",
        "weakening_selection_evidence_added": False,
        "mediation_evidence_added": False,
        "route_distribution_causality_evidence_added": False,
        "before_identity_v1_equal": before_v1_equal,
        "before_identity_v2_equal": before_v2_equal,
        "continuation_receipts_equal": left_readout == right_readout,
        "after_identity_v1_equal": after_v1_equal,
        "after_identity_v2_equal": after_v2_equal,
        "passed": before_v1_equal
        and before_v2_equal
        and left_readout == right_readout
        and after_v1_equal
        and after_v2_equal,
    }


def readout_amount_sweep(module: Any) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for amount in READOUT_AMOUNTS:
        hold = reconstruct_attempt(module, "disjoint_hold", amount)
        weak = reconstruct_attempt(module, "internal_weakening", amount)
        hold_passed = bool(hold["readout"]["admitted"])
        weak_passed = bool(weak["readout"]["admitted"])
        if amount <= 0.20:
            expected_region = "both_pass_below_or_at_weakened_source_C"
            expected = hold_passed and weak_passed
        elif amount <= 0.24:
            expected_region = "differentiated_threshold_interval"
            expected = hold_passed and not weak_passed
        else:
            expected_region = "both_fail_above_hold_source_C"
            expected = not hold_passed and not weak_passed
        rows.append(
            {
                "readout_amount": amount,
                "boundary_role": (
                    "native_float_eligibility_boundary"
                    if amount == 0.24
                    else "not_upper_native_float_boundary"
                ),
                "expected_region": expected_region,
                "hold_admitted": hold_passed,
                "weakened_admitted": weak_passed,
                "hold_eligibility_margin": hold["readout"]["eligibility_margin"],
                "weakened_eligibility_margin": weak["readout"][
                    "eligibility_margin"
                ],
                "expected_region_behavior_passed": expected,
            }
        )
    module.READOUT_PACKET_AMOUNT = 0.22
    return {
        "rows": rows,
        "differentiated_interval": "0.20 < q <= 0.24",
        "scope": "narrow_native_source_C_departure_threshold_not_general_retuning",
        "upper_endpoint_interpretation": (
            "q=0.24 is the native floating-point eligibility boundary with "
            "effectively zero hold margin, not a meaningful positive margin"
        ),
        "passed": all(row["expected_region_behavior_passed"] for row in rows),
    }


def candidate_controls(source: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidates = source.get("candidate_rows")
    if not isinstance(candidates, list):
        candidate = source.get("candidate_row")
        candidates = [candidate] if isinstance(candidate, dict) else []
    for candidate in candidates:
        for row in candidate.get("control_results", []):
            rows.append(
                {
                    "control_id": row["control_id"],
                    "control_status": row["control_status"],
                    "rung_effect": row.get("rung_effect", "not_recorded"),
                }
            )
    return rows


def control_matrix(i3: dict[str, Any], i5: dict[str, Any], i6: dict[str, Any], i7: dict[str, Any]) -> dict[str, Any]:
    active_null_rows = [
        {
            "control_id": row["control_id"],
            "control_family": row["control_family"],
            "control_status": row["control_status"],
        }
        for row in i3["active_null_rows"]
    ]
    candidate_rows = {
        "I5": candidate_controls(i5),
        "I6": candidate_controls(i6),
        "I7": candidate_controls(i7),
    }
    candidate_flat = [row for rows in candidate_rows.values() for row in rows]
    status_counts: dict[str, int] = {}
    for row in candidate_flat:
        status = row["control_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    d0_and_common = [
        row
        for row in active_null_rows
        if row["control_family"] in {"D0", "common", "schema_relation"}
    ]
    return {
        "active_null_row_count": len(active_null_rows),
        "active_null_replay_scope": (
            "governance_and_validator_baseline_not_direct_per_candidate_consumption"
        ),
        "generic_active_nulls_consumed_as_each_positive_candidate_control": False,
        "D0_common_schema_control_count": len(d0_and_common),
        "all_active_nulls_failed_closed": all(
            row["control_status"] == "failed_closed" for row in active_null_rows
        ),
        "candidate_controls_by_iteration": candidate_rows,
        "candidate_control_status_counts": status_counts,
        "candidate_control_resolution_scope": (
            "candidate_specific_I5_through_I7_executed_rows"
        ),
        "candidate_failed_open_count": sum(
            row["control_status"] == "failed_open" for row in candidate_flat
        ),
        "candidate_not_run_count": sum(
            row["control_status"] == "not_run" for row in candidate_flat
        ),
        "I7_normalized_control_summary": i7["control_summary"],
        "all_required_controls_resolved": all(
            row["control_status"] in {"passed", "failed_closed", "not_applicable"}
            for row in candidate_flat
        ),
        "all_controls_without_failed_open_or_not_run": all(
            row["control_status"] in {"passed", "failed_closed", "not_applicable"}
            for row in candidate_flat
        ),
    }


def build_preregistration() -> dict[str, Any]:
    record = {
        "experiment": "N31",
        "iteration": "8",
        "artifact_kind": "D0_replay_and_amount_sweep_preregistration",
        "artifact_schema_version": "n31_i8_preregistration_v1",
        "generated_at": GENERATED_AT,
        "readout_amounts": list(READOUT_AMOUNTS),
        "expected_regions": {
            "q <= 0.20": "hold_and_weakened_pass",
            "0.20 < q <= 0.24": "hold_passes_weakened_fails",
            "q > 0.24": "hold_and_weakened_fail",
        },
        "direction_matrix_role": "perturbation_control_not_equal_state",
        "native_D0a_ceiling_before_replay": "DR2",
        "full_route_distribution_mediation_before_replay": "unresolved",
        "added_mechanism_lane_before_replay": "open",
        "declared_before_I8_runtime_replay": True,
    }
    record["output_digest"] = digest_value(record)
    return record


def build_trace() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    preregistration = build_preregistration()
    PREREGISTRATION.write_text(canonical_json(preregistration), encoding="utf-8")
    builder_replay = source_builder_replay()
    i3, i5, i6, i7, i7_trace = map(load_json, (I3, I5, I6, I7, I7_TRACE))
    sources = [source_record(path) for path in SOURCE_IDENTITIES]
    module = import_i7_module()
    artifact = artifact_replay(sources)
    snapshot = snapshot_roundtrip_replay(i7)
    reconstruction = execution_reconstruction(module, i7_trace)
    equal_state = equal_state_continuation(module)
    sweep = readout_amount_sweep(module)
    controls = control_matrix(i3, i5, i6, i7)
    cache = {
        "D0c": "not_applicable_no_persisted_derived_cache",
        "D0b": (
            "passed_exact_not_persisted_projection"
            if any(
                row["check_id"] == "cache_removal_recomputation_exact"
                and row["passed"]
                for row in i6["checks"]
            )
            else "failed"
        ),
        "D0a": "not_applicable_no_derived_runtime_cache",
        "execution_reconstruction": reconstruction[
            "execution_reconstruction_status"
        ],
    }
    trace: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "8",
        "artifact_kind": "D0_replay_control_trace",
        "artifact_schema_version": "n31_i8_D0_replay_control_trace_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_D0_replay_controls_and_classification_trace",
        "source_chain": sources,
        "source_builder_replay": builder_replay,
        "artifact_replay": artifact,
        "snapshot_load_replay": snapshot,
        "execution_reconstruction": reconstruction,
        "duplicate_replay": {
            "status": reconstruction["duplicate_replay_status"],
            "source": "two independent fresh reconstructions per I7 attempt",
        },
        "equal_state_branch_continuation": equal_state,
        "readout_amount_sweep": sweep,
        "cache_and_execution_reconstruction": cache,
        "control_matrix": controls,
        "conservation_and_timing_audit": {
            "I5_conservation_checks_passed": all(
                row["passed"]
                for row in i5["checks"]
                if "budget" in row["check_id"] or "invariant" in row["check_id"]
            ),
            "I6_conservation_checks_passed": all(
                row["passed"]
                for row in i6["checks"]
                if "budget" in row["check_id"] or "invariant" in row["check_id"]
            ),
            "I7_conservation_checks_passed": all(
                row["passed"]
                for row in i7_trace["checks"]
                if "budget" in row["check_id"] or "mass" in row["check_id"]
            ),
            "internal_time_owner": "native_LGRC9V3_event_queue",
            "wall_clock_consumed": False,
            "direction_matrix_equal_state_relabel_rejected": True,
        },
        "artifact_manifest": [
            {
                "path": relative(PREREGISTRATION),
                "sha256": sha256_file(PREREGISTRATION),
                "artifact_role": "pre_outcome_I8_replay_and_amount_sweep_preregistration",
            }
        ],
    }
    trace["checks"] = [
        check(
            "source_builders_replayed_exact",
            builder_replay["all_source_builders_replayed_exact"],
            builder_replay["rows"],
        ),
        check("source_chain_exact", all(row["identity_exact"] for row in sources), sources),
        check(
            "artifact_replay_exact",
            artifact["source_output_identity_exact"]
            and artifact["all_reference_hashes_exact"],
            {
                "manifest_reference_count": artifact["manifest_reference_count"],
                "unique_artifact_path_count": artifact["unique_artifact_path_count"],
                "duplicate_reference_count": artifact["duplicate_reference_count"],
            },
        ),
        check(
            "snapshot_load_replay_exact",
            snapshot["all_snapshot_roundtrips_exact"],
            snapshot["snapshot_row_count"],
        ),
        check(
            "execution_reconstruction_complete",
            reconstruction["execution_reconstruction_status"] == "passed_complete",
            reconstruction["rows"],
        ),
        check(
            "duplicate_replay_exact",
            reconstruction["duplicate_replay_status"] == "passed",
            reconstruction["rows"],
        ),
        check("equal_state_continuation_passed", equal_state["passed"], equal_state),
        check(
            "I7_direction_matrix_not_consumed_as_equal_state",
            not equal_state["direction_matrix_consumed_as_equal_state"],
            equal_state["branch_source"],
        ),
        check("readout_amount_sweep_passed", sweep["passed"], sweep["rows"]),
        check(
            "all_D0_controls_resolved",
            controls["all_active_nulls_failed_closed"]
            and controls["all_required_controls_resolved"]
            and controls["all_controls_without_failed_open_or_not_run"]
            and controls["candidate_failed_open_count"] == 0
            and controls["candidate_not_run_count"] == 0,
            controls,
        ),
        check(
            "producer_scheduled_decay_remains_failed_closed",
            controls["I7_normalized_control_summary"][
                "producer_scheduled_D0_decay"
            ]
            == "failed_closed",
            controls["I7_normalized_control_summary"],
        ),
        check(
            "cache_and_execution_reconstruction_separate",
            cache["D0b"] == "passed_exact_not_persisted_projection"
            and cache["execution_reconstruction"] == "passed_complete",
            cache,
        ),
        check(
            "conservation_and_timing_audit_passed",
            all(
                value is True
                for key, value in trace["conservation_and_timing_audit"].items()
                if key.endswith("_passed") or key.endswith("_rejected")
            )
            and not trace["conservation_and_timing_audit"]["wall_clock_consumed"],
            trace["conservation_and_timing_audit"],
        ),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    if trace["failed_checks"]:
        trace["status"] = "failed"
        trace["acceptance_state"] = "blocked_I8_replay_or_control_failure"
    trace["output_digest"] = digest_value(
        {key: value for key, value in trace.items() if key != "output_digest"}
    )
    return trace


def build_payload(trace: dict[str, Any]) -> dict[str, Any]:
    i5, i6, i7 = map(load_json, (I5, I6, I7))
    i5_candidate = i5["candidate_rows"][0]
    i6_candidate = i6["candidate_rows"][0]
    i7_native = i7["evidential_objects"]["native_spatial_D0a"]
    i7_conditional = i7["evidential_objects"][
        "conditional_internal_reorganization"
    ]
    classification = {
        "D0c": {
            "status": "supported_instantaneous_comparator",
            "ladder_rung": i5_candidate["decay_relation_ladder_rung"],
            "persistence": False,
            "causal_mediation": False,
            "claim_ceiling": "instantaneous_current_state_geometry_only",
        },
        "D0b": {
            "status": "supported_finite_window_derived_observable",
            "ladder_rung": i6_candidate["decay_relation_ladder_rung"],
            "persistence": True,
            "weakening": True,
            "causal_mediation": False,
            "claim_ceiling": "observable_only_below_causal_trail",
        },
        "native_spatial_D0a": {
            **i7_native,
            "replay_status": "passed",
            "full_route_distribution_mediation": "unresolved",
        },
        "conditional_internal_reorganization": {
            **i7_conditional,
            "replay_status": "passed",
            "readout_scope": "0.20 < q <= 0.24",
        },
        "D0_R": {
            "status": "not_instantiated_in_executed_D0_fixtures",
            "ordinary_export_observed": False,
            "source_current_D0_R_globally_refuted": False,
            "causal_mediation": False,
            "scope_note": (
                "current internal-cycle and internal-reorganization fixtures do "
                "not constitute a dedicated ordinary-export D0-R attempt"
            ),
        },
    }
    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "8",
        "artifact_kind": "D0_replay_controls_classification",
        "artifact_schema_version": "n31_i8_D0_replay_controls_classification_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_replay_control_backed_D0_classification_with_native_"
            "D0a_DR2_ceiling_and_autonomous_weakening_mechanism_need"
        ),
        "source_trace": {
            "path": relative(TRACE),
            "sha256": sha256_file(TRACE),
            "output_digest": trace["output_digest"],
        },
        "classification": classification,
        "aggregation_invariant": {
            "native_spatial_D0a_and_conditional_reorganization_separate": True,
            "conditional_reorganization_can_raise_native_D0a_rung": False,
            "provisional_DR4_status": "superseded_not_a_native_decay_rung",
            "native_D0a_ladder_ceiling": "DR2",
            "mediation_strength": "bounded_partial_local_source_C",
            "full_route_distribution_mediation": "unresolved",
            "producer_authors_weakening": True,
            "ordinary_autonomous_weakening_generated": False,
        },
        "added_mechanism_decision": {
            "scientifically_justified": True,
            "admission_reason": "d0_insufficient",
            "admission_reason_qualifier": (
                "d0_insufficient_for_autonomous_causal_weakening"
            ),
            "D0_wholly_insufficient": False,
            "reason": (
                "existing LGRC forms and preserves spatial organization and executes "
                "conservative externally specified reorganization, but supplies no "
                "native autonomous weakening trajectory"
            ),
            "I9_A_release_efficacy_lane": "open_for_admission",
            "I9_B_conserved_leakage_lane": "open_for_admission",
            "I9_C_susceptibility_lane": "open_for_admission",
            "I8_does_not_select_candidate": True,
        },
        "n31_closeout_progress": {
            "n31_closeout_progress_rung": "N31-C4",
            "n31_closeout_ceiling": "N31-C4_causal_control_backed_result_and_blocker_available",
            "n31_closeout_ladder_rung_assigned": False,
            "ready_for_iteration_9_added_mechanism_admission": True,
            "final_N31_supported": False,
        },
        "RCAE_return_projection": {
            "projection_status": "provisional_I8_not_final_return_manifest",
            "native_spatial_D0a": classification["native_spatial_D0a"],
            "conditional_internal_reorganization": classification[
                "conditional_internal_reorganization"
            ],
            "added_producer_mechanism_lane": "scientifically_justified_and_open",
            "added_mechanism_scope": "autonomous_causal_weakening_only",
            "automatic_RCAE_adoption_allowed": False,
            "final_return_manifest_emitted": False,
        },
        "claim_boundary": {
            "allowed_claim": (
                "replay_control_backed_native_spatial_D0a_formation_and_"
                "persistence_at_DR2_plus_separate_experiment_authored_"
                "conditional_reorganization_with_bounded_local_C_effect"
            ),
            "blocked_claims": [
                "autonomous_D0a_weakening",
                "native_DR4_decay_relation",
                "full_route_distribution_mediation",
                "induced_geometric_mediation",
                "general_decay_law",
                "native_memory",
                "trail_or_stigmergy",
                "communication",
                "ecology",
                "agency",
                "native_support",
                "Phase_8_completion",
            ],
            "unsafe_claim_flags": {
                "autonomous_D0a_weakening_claim_allowed": False,
                "native_DR4_decay_relation_claim_allowed": False,
                "full_route_distribution_mediation_claim_allowed": False,
                "general_decay_law_claim_allowed": False,
                "native_memory_claim_allowed": False,
                "trail_or_stigmergy_claim_allowed": False,
                "communication_claim_allowed": False,
                "ecology_claim_allowed": False,
                "agency_claim_allowed": False,
                "native_support_claim_allowed": False,
                "phase8_completion_claim_allowed": False,
            },
        },
        "governance": {
            "governance_base_revision": GOVERNANCE_BASE_REVISION,
            "src_diff_empty": git_diff_empty("src"),
            "protected_runtime_contract_diff_empty": all(
                git_diff_empty(path)
                for path in (
                    "src",
                    "lib",
                    "specs",
                    "implementation",
                    "tests",
                    "examples",
                    "scripts",
                    "pyproject.toml",
                    "requirements.txt",
                    "uv.lock",
                )
            ),
        },
        "artifact_manifest": [
            {
                "path": relative(PREREGISTRATION),
                "sha256": sha256_file(PREREGISTRATION),
                "artifact_role": "I8_replay_and_amount_sweep_preregistration",
            },
            {
                "path": relative(TRACE),
                "sha256": sha256_file(TRACE),
                "artifact_role": "I8_replay_control_runtime_trace",
            },
        ],
    }
    payload["checks"] = [
        check("I8_trace_passed", trace["status"] == "passed", trace["failed_checks"]),
        check(
            "D0_classes_remain_separate",
            classification["D0c"]["ladder_rung"] == "DR1"
            and classification["D0b"]["ladder_rung"] == "DR3"
            and classification["native_spatial_D0a"][
                "decay_relation_ladder_rung"
            ]
            == "DR2"
            and not classification["conditional_internal_reorganization"][
                "D0_decay_relation"
            ],
            classification,
        ),
        check(
            "I7_demotion_preserved_on_all_aggregation_surfaces",
            payload["aggregation_invariant"]["native_D0a_ladder_ceiling"]
            == "DR2"
            and not payload["aggregation_invariant"][
                "conditional_reorganization_can_raise_native_D0a_rung"
            ]
            and payload["aggregation_invariant"]["producer_authors_weakening"]
            and not payload["aggregation_invariant"][
                "ordinary_autonomous_weakening_generated"
            ],
            payload["aggregation_invariant"],
        ),
        check(
            "added_mechanism_lane_remains_open",
            payload["added_mechanism_decision"]["scientifically_justified"]
            and payload["added_mechanism_decision"]["admission_reason"]
            == "d0_insufficient"
            and payload["added_mechanism_decision"][
                "admission_reason_qualifier"
            ]
            == "d0_insufficient_for_autonomous_causal_weakening"
            and not payload["added_mechanism_decision"]["D0_wholly_insufficient"]
            and payload["added_mechanism_decision"][
                "I8_does_not_select_candidate"
            ],
            payload["added_mechanism_decision"],
        ),
        check(
            "RCAE_projection_bounded",
            not payload["RCAE_return_projection"]["automatic_RCAE_adoption_allowed"]
            and not payload["RCAE_return_projection"]["final_return_manifest_emitted"],
            payload["RCAE_return_projection"],
        ),
        check(
            "unsafe_claim_flags_false",
            all(
                value is False
                for value in payload["claim_boundary"]["unsafe_claim_flags"].values()
            ),
            payload["claim_boundary"]["unsafe_claim_flags"],
        ),
        check("src_diff_empty", payload["governance"]["src_diff_empty"], GOVERNANCE_BASE_REVISION),
        check(
            "protected_runtime_contract_diff_empty",
            payload["governance"]["protected_runtime_contract_diff_empty"],
            GOVERNANCE_BASE_REVISION,
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(payload), "recursive"),
    ]
    payload["failed_checks"] = [
        row["check_id"] for row in payload["checks"] if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_I8_classification_failure"
        payload["n31_closeout_progress"][
            "ready_for_iteration_9_added_mechanism_admission"
        ] = False
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload


def write_report(payload: dict[str, Any], trace: dict[str, Any]) -> None:
    checks = "\n".join(
        f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |"
        for row in payload["checks"]
    )
    sweep_rows = "\n".join(
        "| {readout_amount:.2f} | {hold} | {weak} | `{region}` |".format(
            readout_amount=row["readout_amount"],
            hold=str(row["hold_admitted"]).lower(),
            weak=str(row["weakened_admitted"]).lower(),
            region=row["expected_region"],
        )
        for row in trace["readout_amount_sweep"]["rows"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 8 - D0 Replay, Controls, And Classification

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
n31_closeout_progress_rung = N31-C4
native_spatial_D0a_ladder_ceiling = DR2
autonomous_D0a_weakening_supported = false
conditional_internal_reorganization_supported = true
conditional_reorganization_is_D0_decay = false
mediation_strength = bounded_partial_local_source_C
full_route_distribution_mediation = unresolved
added_mechanism_admission_scientifically_justified = true
ready_for_iteration_9_added_mechanism_admission = true
final_N31_supported = false
```

I8 replays and classifies the current coherence-only decay evidence without
promoting the I7 perturbation result. Existing LGRC supports spatial formation
and persistence, plus conservative externally specified reorganization, but it
does not supply a native autonomous weakening trajectory.

## Comparative Classification

```text
D0c = DR1 instantaneous current-state geometry; no persistence or mediation
D0b = DR3 finite-window fading derived observable; no causal mediation
native spatial D0a = DR2 formation and persistence; autonomous weakening absent
conditional reorganization = replay-clean perturbation with bounded local-C effect
D0-R = not instantiated in the executed fixtures; ordinary export was not tested
```

The native D0a result and conditional reorganization remain separate
evidential objects. The latter cannot raise the native D0a rung.

## Replay

```text
artifact manifest references replayed = {trace['artifact_replay']['manifest_reference_count']}
unique artifact paths replayed = {trace['artifact_replay']['unique_artifact_path_count']}
duplicate cross-source references = {trace['artifact_replay']['duplicate_reference_count']}
snapshot rows roundtripped = {trace['snapshot_load_replay']['snapshot_row_count']}
execution reconstruction = {trace['execution_reconstruction']['execution_reconstruction_status']}
duplicate replay = {trace['duplicate_replay']['status']}
equal-state continuation = {str(trace['equal_state_branch_continuation']['passed']).lower()}
direction matrix consumed as equal-state = false
```

I8 directly reruns the I3, I5, I6, and I7 builders. It verifies I2, I3R1,
I4, I4R1, and I5R1 transitively through those exact source chains; it does not
claim that every evidence-stack builder was directly rerun. The `45` manifest
references resolve to `25` unique paths, with `20` repeated cross-source
references. Every reference hash is exact.

Restoration identities v1 and v2 remain exact across snapshot/load replay.
No consumed row invokes `reset`; v2 is nevertheless audited on every I7
snapshot roundtrip. Cache recomputation and execution reconstruction remain
separate checks. Equal-state continuation establishes replay correctness only;
it adds no weakening-selection, mediation, or route-distribution-causality
evidence.

## Threshold Scope

| Amount `q` | Hold admitted | Weakened admitted | Region |
|---:|---:|---:|---|
{sweep_rows}

The differentiated effect is confined to `0.20 < q <= 0.24`. The `q = 0.24`
row is the native floating-point eligibility boundary with effectively zero
hold margin, not a meaningful positive-margin endpoint. This is a narrow native
source-C departure threshold, not broad route retuning or full-distribution
mediation.

## Control Boundary

```text
producer_scheduled_D0_decay = failed_closed
forming_packet_exclusion = passed
route_mass_match = passed
direction_matrix = perturbation_control
proper_time_alignment = not_applicable
failed_open candidate controls = {trace['control_matrix']['candidate_failed_open_count']}
not_run candidate controls = {trace['control_matrix']['candidate_not_run_count']}
```

The `70` I3 rows are generic pre-positive nulls. They remain separate from the
candidate-specific I5-I7 controls and are not presented as direct per-candidate
null consumption. All required controls are resolved, with no `failed_open` or
`not_run` dependent control.

## Added-Mechanism Consequence

The existing admission enum remains `d0_insufficient`, qualified precisely as
`d0_insufficient_for_autonomous_causal_weakening`. D0 is not wholly
insufficient: its D0c, D0b, and native spatial D0a results remain supported at
their bounded ceilings. D0-R is uninstantiated in the executed fixtures, not
globally refuted.
I8 does not select A, B, or C, but it keeps all three candidate lanes open.
The purpose is to test a bounded producer-owned lifecycle mechanism that may
supply the missing transition selection, not to relabel the I7 perturbation as
native decay.

## Checks

| Check | Passed |
|---|---:|
{checks}

## Claim Ceiling

```text
{payload['claim_boundary']['allowed_claim']}
```

This is not autonomous D0a weakening, a native DR4 relation, full route
mediation, induced-geometric mediation, a general decay law, memory,
trail/stigmergy, communication, ecology, agency, native support, or Phase 8
completion.

## Reproduction

```bash
{COMMAND}
```

```text
output_digest = {payload['output_digest']}
```
""",
        encoding="utf-8",
    )


def main() -> None:
    trace = build_trace()
    TRACE.write_text(canonical_json(trace), encoding="utf-8")
    if trace["failed_checks"]:
        raise RuntimeError("N31 I8 trace failed: " + ", ".join(trace["failed_checks"]))
    payload = build_payload(trace)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload, trace)
    if payload["failed_checks"]:
        raise RuntimeError("N31 I8 failed: " + ", ".join(payload["failed_checks"]))
    print(canonical_json(payload), end="")


if __name__ == "__main__":
    main()
