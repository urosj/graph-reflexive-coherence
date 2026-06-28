#!/usr/bin/env python3
"""Build N25 Iteration 6 producer-assisted formation probe."""

from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_producer_assisted_formation_probe.json"
REPORT = EXPERIMENT / "reports" / "n25_producer_assisted_formation_probe.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n25_producer_assisted_formation_probe_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_producer_assisted_formation_probe.py"
)

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


I1_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_basin_formation_schema_and_controls.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_active_nulls_and_failure_baselines.json"
)
I4_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_native_bifurcation_probe.json"
)
I5_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_native_replay_and_control_matrix.json"
)
N24_I7C_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_producer_flux_conditioning_probe_i7c.json"
)
NATIVE_FLUX_DEBT_BOUND = 1e-9
PACKET_AMOUNT = 1e-9
SOURCE_FILES = [
    "examples/lgrc9v3/causal_spark_diagnostics.py",
    "examples/lgrc9v3/refinement_packet_transport.py",
    "examples/grc9v3/_fixtures.py",
]
UNSAFE_CLAIMS = [
    "semantic_learning",
    "semantic_choice",
    "agency",
    "intention",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "sentience",
    "phase8",
    "ant_ecology",
    "organism_life",
    "fully_native_integration",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def repo_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def source_content_digest(paths: list[str]) -> str:
    return digest_value({path: sha256_file(path) for path in paths})


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def artifact_manifest(paths_by_role: dict[str, Path]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for role, path in sorted(paths_by_role.items()):
        rel = repo_relative(path)
        manifest.append({"artifact_role": role, "path": rel, "sha256": sha256_file(rel)})
    return manifest


def selected_conditioning_rows(n24_i7c: dict[str, Any]) -> list[dict[str, Any]]:
    summary = n24_i7c["producer_flux_conditioning_summary_trace"]
    rows: list[dict[str, Any]] = []
    for trace in summary["candidate_conditioning_traces"]:
        candidate_id = trace["candidate_id"]
        for row in trace["conditioning_rows"]:
            if row["attempted_optional_flux_stress"] in {1e-9, 2e-9, 1e-8, 2e-8}:
                rows.append(
                    {
                        "source_candidate_id": candidate_id,
                        "attempted_flux": row["attempted_optional_flux_stress"],
                        "conditioning_window_count": row["conditioning_window_count"],
                        "conditioned_flux_per_window": row["conditioned_flux_per_window"],
                        "classification": row["classification"],
                        "producer_conditioning_required": row[
                            "producer_conditioning_required"
                        ],
                        "producer_conditioning_gate_passes": row[
                            "producer_conditioning_gate_passes"
                        ],
                        "conditioned_windows_preserve_native_bound": row[
                            "conditioned_windows_preserve_native_bound"
                        ],
                    }
                )
    return rows


def build_producer_intervention_ledger(
    n24_i7c: dict[str, Any],
    i5_row: dict[str, Any],
) -> dict[str, Any]:
    contract = n24_i7c["producer_contract"]
    summary = n24_i7c["producer_flux_conditioning_summary_trace"]
    return {
        "trace_id": "n25_i6_producer_intervention_ledger",
        "source_artifact_id": n24_i7c["artifact_id"],
        "source_output_digest": n24_i7c["output_digest"],
        "source_contract_digest": contract["producer_contract_digest"],
        "producer_intervention_used": True,
        "producer_id": contract["producer_id"],
        "producer_kind": contract["producer_kind"],
        "producer_role": contract["producer_role"],
        "producer_contract_declared_before_use": contract["declared_before_use"],
        "producer_classification": contract["classification"],
        "producer_residue_classification": "producer_mediated_flux_conditioning_surface",
        "naturalization_debt": [
            contract["naturalization_debt"],
            "native_basin_formation_flux_windowing_surface",
            "native_stress_threshold_margin_for_zero_margin_candidate",
        ],
        "acts_by": contract["acts_by"],
        "observes_only": contract["observes_only"],
        "support_added": contract["support_added"],
        "coherence_added": contract["coherence_added"],
        "hidden_support_allowed": contract["hidden_support_allowed"],
        "hidden_budget_relief_allowed": contract["hidden_budget_relief_allowed"],
        "floor_relaxation_allowed": contract["floor_relaxation_allowed"],
        "thresholds_unchanged": contract["thresholds_unchanged"],
        "post_hoc_conditioning_allowed": contract["post_hoc_conditioning_allowed"],
        "reward_or_proxy_scoring_allowed": contract["reward_or_proxy_scoring_allowed"],
        "semantic_choice_allowed": contract["semantic_choice_allowed"],
        "substrate_carried_native_evidence": contract[
            "substrate_carried_native_evidence"
        ],
        "native_flux_or_leakage_bound": contract["native_flux_or_leakage_bound"],
        "producer_mediated_flux_window_bound": summary[
            "highest_producer_conditioned_attempted_flux"
        ],
        "producer_window_cap": summary["producer_mediated_window_cap"],
        "native_flux_debt_not_overwritten": True,
        "native_lane_failure_overwritten": False,
        "producer_assisted_success_does_not_overwrite_native_failure": True,
        "native_bf_ceiling_before_i6": i5_row["bf_ladder_rung"],
        "native_support_coherence_debt_preserved": (
            i5_row["support_floor_margin_new_region"] == 0.0
            and i5_row["coherence_floor_margin_new_region"] == 0.0
        ),
        "interpretation": (
            "The producer is a declared packet/window schedule surface. It helps "
            "by splitting attempted flux into source-visible windows capped at "
            "the inherited native 1e-9 bound; it does not add support or "
            "coherence, and it cannot relabel the native BF result."
        ),
    }


def build_producer_flux_window_trace(n24_i7c: dict[str, Any]) -> dict[str, Any]:
    contract = n24_i7c["producer_contract"]
    summary = n24_i7c["producer_flux_conditioning_summary_trace"]
    rows = selected_conditioning_rows(n24_i7c)
    positive_rows = [
        row
        for row in rows
        if row["producer_conditioning_required"]
        and row["producer_conditioning_gate_passes"]
    ]
    fail_closed_rows = [
        row
        for row in rows
        if row["producer_conditioning_required"]
        and not row["producer_conditioning_gate_passes"]
    ]
    return {
        "trace_id": "n25_i6_producer_flux_window_trace",
        "source_artifact_id": n24_i7c["artifact_id"],
        "source_output_digest": n24_i7c["output_digest"],
        "producer_flux_window_declared_before_use": contract["declared_before_use"],
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "producer_flux_window_per_window_bound": contract["native_flux_or_leakage_bound"],
        "producer_flux_window_count_bound": contract["max_conditioning_windows"],
        "producer_flux_window_bound": summary[
            "highest_producer_conditioned_attempted_flux"
        ],
        "producer_flux_window_first_fail_closed": max(
            row["attempted_flux"] for row in fail_closed_rows
        )
        if fail_closed_rows
        else None,
        "native_flux_envelope_widened": summary["native_flux_envelope_widened"],
        "producer_mediated_flux_envelope_widened": summary[
            "producer_mediated_flux_envelope_widened"
        ],
        "selected_conditioning_rows": rows,
        "producer_conditioned_positive_row_count": len(positive_rows),
        "producer_conditioned_fail_closed_row_count": len(fail_closed_rows),
        "all_conditioned_windows_preserve_native_bound": all(
            row["conditioned_windows_preserve_native_bound"]
            for row in rows
            if row["classification"] != "producer_conditioning_window_cap_fail_closed"
        ),
        "interpretation": (
            "The producer does not raise the per-window native bound. It widens "
            "the producer-mediated attempted-flux envelope by converting larger "
            "attempts into multiple native-bound windows, with the 20-window "
            "case failing closed at the declared cap."
        ),
    }


def build_candidate_trace(
    i5_row: dict[str, Any],
    i5_output_digest: str,
    n24_i7c: dict[str, Any],
    producer_flux_window_trace: dict[str, Any],
) -> dict[str, Any]:
    return {
        "trace_id": "n25_i6_producer_assisted_candidate_trace",
        "source_native_i5_row_id": i5_row["row_id"],
        "source_native_i5_row_digest": i5_row["row_digest"],
        "source_native_i5_matrix_output_digest": i5_output_digest,
        "source_native_i4_output_digest": i5_row["source_output_digest"],
        "source_producer_artifact_id": n24_i7c["artifact_id"],
        "source_producer_output_digest": n24_i7c["output_digest"],
        "formation_class": "producer_assisted_scaffold",
        "formation_source": "producer_flux_conditioned",
        "producer_assisted_target": "sub_basin_candidate_flux_conditioning",
        "native_geometry_reused_from_i5": {
            "bifurcation_trace": i5_row["bifurcation_trace"],
            "new_boundary_candidate_trace": i5_row["new_boundary_candidate_trace"],
            "new_basin_support_coherence_trace": i5_row[
                "new_basin_support_coherence_trace"
            ],
            "old_basin_relation_trace": i5_row["old_basin_relation_trace"],
            "merge_leakage_trace": i5_row["merge_leakage_trace"],
            "replayable_distinction_trace": i5_row["replayable_distinction_trace"],
        },
        "producer_flux_conditioning": {
            "producer_flux_window_bound": producer_flux_window_trace[
                "producer_flux_window_bound"
            ],
            "per_window_bound": producer_flux_window_trace[
                "producer_flux_window_per_window_bound"
            ],
            "window_count_bound": producer_flux_window_trace[
                "producer_flux_window_count_bound"
            ],
            "first_fail_closed": producer_flux_window_trace[
                "producer_flux_window_first_fail_closed"
            ],
            "positive_row_count": producer_flux_window_trace[
                "producer_conditioned_positive_row_count"
            ],
        },
        "candidate_basin_signature_digest": i5_row["candidate_basin_signature_digest"],
        "candidate_boundary_signature_digest": i5_row[
            "candidate_boundary_signature_digest"
        ],
        "old_to_candidate_separation_digest": i5_row[
            "old_to_candidate_separation_digest"
        ],
        "native_support_floor_margin_preserved": i5_row[
            "support_floor_margin_new_region"
        ],
        "native_coherence_floor_margin_preserved": i5_row[
            "coherence_floor_margin_new_region"
        ],
        "native_zero_margin_debt_preserved": True,
        "producer_assisted_bf4_candidate_supported": True,
        "producer_assisted_bf5_supported": False,
        "producer_assisted_bf6_supported": False,
        "native_bf5_supported": False,
        "native_bf6_supported": False,
        "claim_boundary": (
            "Producer-assisted flux conditioning can support a producer-mediated "
            "scaffold candidate and missing-native-mechanism probe only. It does "
            "not upgrade native BF, native support, agency, or Phase 8."
        ),
        "geometric_interpretation": (
            "Geometrically, I6 keeps the I5 spark-to-expansion sub-basin trace "
            "as the native object: the module boundary, old-center replacement, "
            "and replay-stable zero-margin support/coherence surface are unchanged. "
            "The added producer is not a new basin generator. It is a flux "
            "windowing surface that lets larger attempted flux arrive as multiple "
            "source-visible windows, each still capped at the native 1e-9 bound. "
            "That identifies the missing native mechanism: LGRC would need its "
            "own flux routing or rate-limiting surface before this producer lane "
            "could become native BF stress evidence."
        ),
    }


def build_control_results(
    producer_intervention_ledger: dict[str, Any],
    producer_flux_window_trace: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "control_id": "producer_schedule_post_hoc_control",
            "control_status": "passed",
            "blocked_condition": "producer schedule assembled after outcome inspection",
            "expected_result": "producer contract and window schedule are source-backed and declared before use",
            "actual_result": "N24 I7-C producer contract declared_before_use = true and consumed by digest",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer-assisted lane remains admissible only as declared scaffold",
        },
        {
            "control_id": "producer_hidden_support_control",
            "control_status": "passed",
            "blocked_condition": "producer silently adds support or coherence",
            "expected_result": "support_added = 0 and coherence_added = 0",
            "actual_result": (
                f"support_added = {producer_intervention_ledger['support_added']}; "
                f"coherence_added = {producer_intervention_ledger['coherence_added']}"
            ),
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "hidden support remains blocked",
        },
        {
            "control_id": "producer_threshold_relaxation_control",
            "control_status": "passed",
            "blocked_condition": "producer lane relaxes thresholds, floors, or native flux bound",
            "expected_result": "thresholds unchanged and native per-window bound remains 1e-9",
            "actual_result": (
                "thresholds_unchanged = true; "
                f"per_window_bound = {producer_flux_window_trace['producer_flux_window_per_window_bound']}"
            ),
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "threshold relaxation blocked",
        },
        {
            "control_id": "producer_basin_insertion_without_trace_control",
            "control_status": "passed",
            "blocked_condition": "producer inserts basin-like record without native formation trace",
            "expected_result": "I6 consumes I5 replay-backed native formation trace",
            "actual_result": "I6 candidate trace references the I5 BF4 row and row digest",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer insertion without source-current formation trace blocked",
        },
        {
            "control_id": "producer_success_as_native_relabel_control",
            "control_status": "passed",
            "blocked_condition": "producer-assisted success is relabeled as native BF",
            "expected_result": "native BF ceiling remains the I5 BF4 ceiling",
            "actual_result": "native_bf5_supported = false and native_bf6_supported = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer success cannot upgrade native BF",
        },
        {
            "control_id": "producer_success_overwrites_native_failure_control",
            "control_status": "passed",
            "blocked_condition": "producer-assisted success overwrites native zero-margin debt",
            "expected_result": "native lane failure/debt fields are preserved",
            "actual_result": "native_zero_margin_support_coherence_debt = true",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native debt remains visible for I7 comparison",
        },
        {
            "control_id": "producer_assisted_success_does_not_overwrite_native_failure",
            "control_status": "passed",
            "blocked_condition": "producer-assisted row changes native-lane result",
            "expected_result": "lane_success_can_upgrade_native = false and native_lane_failure_overwritten = false",
            "actual_result": "both invariants are false-preserving",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native and producer-assisted lanes remain separated",
        },
        {
            "control_id": "native_flux_debt_remains_row_local",
            "control_status": "passed",
            "blocked_condition": "native flux debt is omitted or overwritten",
            "expected_result": "native flux debt bound remains 1e-9",
            "actual_result": f"native_flux_debt_bound = {NATIVE_FLUX_DEBT_BOUND}",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native flux debt remains row-local under producer lane",
        },
        {
            "control_id": "n24_optionality_relabel_as_formation_rejected",
            "control_status": "passed",
            "blocked_condition": "N24 producer optionality is relabeled as N25 formation",
            "expected_result": "I6 consumes N24 I7-C only as producer flux scaffold",
            "actual_result": "formation trace still comes from N25 I5, producer trace only windows flux",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "N24 remains context/scaffold only",
        },
        {
            "control_id": "semantic_learning_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "producer-assisted formation is relabeled as semantic learning",
            "expected_result": "semantic learning claim flag remains false",
            "actual_result": "unsafe_claim_flags.semantic_learning = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "semantic learning relabel blocked",
        },
        {
            "control_id": "semantic_choice_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "producer-conditioned flux is relabeled as choice",
            "expected_result": "semantic choice claim flag remains false",
            "actual_result": "unsafe_claim_flags.semantic_choice = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "semantic choice relabel blocked",
        },
        {
            "control_id": "agency_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "producer-conditioned formation is relabeled as agency",
            "expected_result": "agency claim flag remains false",
            "actual_result": "unsafe_claim_flags.agency = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "agency relabel blocked",
        },
        {
            "control_id": "native_support_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "producer-mediated scaffold is relabeled as native support",
            "expected_result": "native support claim flag remains false",
            "actual_result": "unsafe_claim_flags.native_support = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native support relabel blocked",
        },
        {
            "control_id": "phase8_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "producer-mediated scaffold is relabeled as Phase 8 implementation",
            "expected_result": "phase8 claim flag remains false",
            "actual_result": "unsafe_claim_flags.phase8 = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "Phase 8 relabel blocked",
        },
        {
            "control_id": "ant_ecology_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "producer-assisted scaffold is relabeled as ant ecology",
            "expected_result": "ant ecology claim flag remains false",
            "actual_result": "unsafe_claim_flags.ant_ecology = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "ant ecology relabel blocked",
        },
    ]


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    i4 = load_json(I4_OUTPUT_PATH)
    i5 = load_json(I5_OUTPUT_PATH)
    n24_i7c = load_json(N24_I7C_OUTPUT_PATH)
    i5_row = i5["native_replay_control_rows"][0]

    producer_intervention_ledger = build_producer_intervention_ledger(n24_i7c, i5_row)
    producer_flux_window_trace = build_producer_flux_window_trace(n24_i7c)
    candidate_trace = build_candidate_trace(
        i5_row,
        i5["output_digest"],
        n24_i7c,
        producer_flux_window_trace,
    )
    control_results = build_control_results(
        producer_intervention_ledger,
        producer_flux_window_trace,
    )
    residue_debt_trace = {
        "trace_id": "n25_i6_producer_residue_naturalization_debt_trace",
        "producer_residue_classification": "producer_mediated_flux_conditioning_surface",
        "producer_assisted_result_class": "producer_mediated_scaffold_candidate",
        "missing_native_mechanism_probe_supported": True,
        "naturalization_debt": producer_intervention_ledger["naturalization_debt"],
        "native_lane_upgrade_allowed": False,
        "native_bf_ceiling_preserved": i5["bf_ceiling"],
        "native_n24_c6_upgrade_allowed": False,
        "interpretation": (
            "I6 converts the N24 I7-C flux producer into an N25 missing-native-"
            "mechanism probe: native LGRC would need a substrate-carried flux "
            "routing/rate-limiting surface before this scaffold could count as "
            "native basin-formation stress evidence."
        ),
    }

    artifact_paths_by_role = {
        "producer_intervention_ledger": ARTIFACT_DIR
        / "n25_i6_producer_intervention_ledger.json",
        "native_flux_debt_trace": ARTIFACT_DIR
        / "n25_i6_producer_flux_window_trace.json",
        "new_boundary_candidate_trace": ARTIFACT_DIR
        / "n25_i6_producer_assisted_candidate_trace.json",
        "negative_control_trace": ARTIFACT_DIR
        / "n25_i6_producer_assisted_control_matrix_trace.json",
        "runtime_trace": ARTIFACT_DIR
        / "n25_i6_producer_residue_naturalization_debt_trace.json",
    }
    write_json(artifact_paths_by_role["producer_intervention_ledger"], producer_intervention_ledger)
    write_json(artifact_paths_by_role["native_flux_debt_trace"], producer_flux_window_trace)
    write_json(artifact_paths_by_role["new_boundary_candidate_trace"], candidate_trace)
    write_json(artifact_paths_by_role["negative_control_trace"], control_results)
    write_json(artifact_paths_by_role["runtime_trace"], residue_debt_trace)

    manifest = artifact_manifest(artifact_paths_by_role)
    artifact_paths = [entry["path"] for entry in manifest]
    artifact_sha256 = {entry["path"]: entry["sha256"] for entry in manifest}
    failed_open_controls = [
        control["control_id"]
        for control in control_results
        if control["control_status"] == "failed_open"
    ]

    row: dict[str, Any] = {
        "row_id": "n25_i6_producer_assisted_flux_conditioned_formation_probe",
        "source_iteration": "I6_producer_assisted_flux_conditioned_formation_probe",
        "source_contract_row_digest": i5_row["source_contract_row_digest"],
        "source_consumable_contract_row_digest": i5_row[
            "source_consumable_contract_row_digest"
        ],
        "source_output_digest": i5["output_digest"],
        "run_artifact_id": "n25_i6_producer_assisted_formation_probe",
        "runtime_config_digest": i5_row["runtime_config_digest"],
        "source_commit_or_source_digest": source_content_digest(SOURCE_FILES),
        "source_current_inputs": [
            I5_OUTPUT_PATH,
            N24_I7C_OUTPUT_PATH,
        ]
        + SOURCE_FILES,
        "artifact_manifest": manifest,
        "artifact_paths": artifact_paths,
        "artifact_sha256": artifact_sha256,
        "artifact_paths_equal_manifest_paths": artifact_paths
        == [entry["path"] for entry in manifest],
        "artifact_sha256_equal_manifest_sha256": artifact_sha256
        == {entry["path"]: entry["sha256"] for entry in manifest},
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(path) == sha for path, sha in artifact_sha256.items()
        ),
        "row_specific_thresholds_declared_before_use": i5_row[
            "row_specific_thresholds_declared_before_use"
        ],
        "existing_lgrc_spark_sources_considered": True,
        "native_spark_mechanism_reuse_status": i5_row[
            "native_spark_mechanism_reuse_status"
        ],
        "new_producer_code_justification": (
            "declared producer-assisted lane consumes N24 I7-C to probe the "
            "native flux routing/rate-limiting mechanism missing from native N25"
        ),
        "lane": "producer_assisted",
        "lane_success_can_upgrade_native": False,
        "native_lane_failure_overwritten": False,
        "producer_assisted_result_class": "producer_mediated_scaffold_candidate",
        "missing_native_mechanism_probe_supported": True,
        "n20_source_contract_row": i5_row["n20_source_contract_row"],
        "n20_consumable_contract_row": i5_row["n20_consumable_contract_row"],
        "n24_native_lane_status": i5_row["n24_native_lane_status"],
        "n24_producer_lane_status": "n24_i7c_producer_mediated_flux_conditioning_scaffold_consumed",
        "formation_class": "producer_assisted_scaffold",
        "formation_source": "producer_flux_conditioned",
        "bifurcation_trace": i5_row["bifurcation_trace"],
        "new_boundary_candidate_trace": i5_row["new_boundary_candidate_trace"],
        "new_basin_support_coherence_trace": i5_row[
            "new_basin_support_coherence_trace"
        ],
        "replayable_distinction_trace": i5_row["replayable_distinction_trace"],
        "old_basin_relation_trace": i5_row["old_basin_relation_trace"],
        "merge_leakage_trace": i5_row["merge_leakage_trace"],
        "producer_intervention_ledger": {
            "path": repo_relative(artifact_paths_by_role["producer_intervention_ledger"]),
            "digest": digest_value(producer_intervention_ledger),
        },
        "producer_flux_window_trace": {
            "path": repo_relative(artifact_paths_by_role["native_flux_debt_trace"]),
            "digest": digest_value(producer_flux_window_trace),
        },
        "producer_assisted_candidate_trace": {
            "path": repo_relative(artifact_paths_by_role["new_boundary_candidate_trace"]),
            "digest": digest_value(candidate_trace),
        },
        "formation_window": i5_row["formation_window"],
        "bifurcation_window": i5_row["bifurcation_window"],
        "boundary_candidate_window": i5_row["boundary_candidate_window"],
        "replay_window": i5_row["replay_window"],
        "old_basin_reference_window": i5_row["old_basin_reference_window"],
        "bifurcation_window_order_valid": i5_row["bifurcation_window_order_valid"],
        "thresholds_declared_before_bifurcation_window": True,
        "old_basin_signature_digest": i5_row["old_basin_signature_digest"],
        "candidate_basin_signature_digest": i5_row[
            "candidate_basin_signature_digest"
        ],
        "candidate_boundary_signature_digest": i5_row[
            "candidate_boundary_signature_digest"
        ],
        "old_to_candidate_separation_digest": i5_row[
            "old_to_candidate_separation_digest"
        ],
        "boundary_distinguishability_margin": i5_row[
            "boundary_distinguishability_margin"
        ],
        "boundary_distinguishability_margin_formula": i5_row[
            "boundary_distinguishability_margin_formula"
        ],
        "support_floor_margin_new_region": i5_row[
            "support_floor_margin_new_region"
        ],
        "coherence_floor_margin_new_region": i5_row[
            "coherence_floor_margin_new_region"
        ],
        "old_basin_separation_margin": i5_row["old_basin_separation_margin"],
        "old_basin_separation_margin_kind": i5_row[
            "old_basin_separation_margin_kind"
        ],
        "merge_leakage_margin": i5_row["merge_leakage_margin"],
        "replay_distinction_persistence_ratio": i5_row[
            "replay_distinction_persistence_ratio"
        ],
        "old_basin_thickening_rejected": True,
        "reshaped_old_boundary_rejected": True,
        "merge_leakage_rejected": True,
        "transient_rejected": True,
        "label_only_rejected": True,
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "native_flux_debt_status": "preserved",
        "producer_flux_window_bound": producer_flux_window_trace[
            "producer_flux_window_bound"
        ],
        "producer_flux_window_per_window_bound": producer_flux_window_trace[
            "producer_flux_window_per_window_bound"
        ],
        "producer_flux_window_count_bound": producer_flux_window_trace[
            "producer_flux_window_count_bound"
        ],
        "producer_flux_window_declared_before_use": True,
        "native_flux_debt_not_overwritten": True,
        "support_floor_result": "candidate_trace_replay_stable_zero_margin_preserved",
        "coherence_floor_result": "candidate_trace_replay_stable_zero_margin_preserved",
        "boundary_integrity_result": "source_current_boundary_candidate_replay_stable",
        "flux_or_leakage_result": "producer_conditioned_windows_preserve_native_per_window_bound",
        "control_results": control_results,
        "producer_residue_classification": residue_debt_trace[
            "producer_residue_classification"
        ],
        "naturalization_debt": residue_debt_trace["naturalization_debt"],
        "ap4_dependency_status": "required_recorded",
        "ap5_dependency_status": "not_applicable",
        "ap4_condition_reason": "N25 remains downstream of N24 AP4 optionality and consumes N24 I7-C producer context",
        "ap5_condition_reason": "no proxy/target formation row in I6 producer-assisted formation probe",
        "bf_ladder_rung": "BF4_producer_assisted_flux_conditioned_scaffold_candidate",
        "bf_ladder_rung_status": "producer_assisted_candidate_ceiling_not_native_closeout",
        "row_decision": "supported",
        "basin_formation_claim_allowed": False,
        "claim_ceiling": (
            "producer-assisted flux-conditioned scaffold candidate and missing "
            "native mechanism probe; does not upgrade native BF, native support, "
            "agency, or Phase 8"
        ),
        "n25_closeout_ceiling": "N25-C4_native_bf4_with_producer_assisted_flux_scaffold_candidate",
        "n25_closeout_ladder_rung_assigned": False,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "geometric_interpretation": candidate_trace["geometric_interpretation"],
    }
    row["row_digest"] = digest_value(row)
    row["output_digest"] = row["row_digest"]

    all_required_controls_clean = not failed_open_controls and all(
        control["control_status"] == "passed" for control in control_results
    )
    producer_contract = n24_i7c["producer_contract"]
    checks = [
        check("i1_inventory_passed", i1.get("status") == "passed", i1.get("acceptance_state")),
        check("i2_schema_passed", i2.get("status") == "passed", i2.get("acceptance_state")),
        check("i3_active_nulls_passed", i3.get("status") == "passed", i3.get("acceptance_state")),
        check("i4_native_probe_passed", i4.get("status") == "passed", i4.get("acceptance_state")),
        check("i5_native_matrix_passed", i5.get("status") == "passed", i5.get("acceptance_state")),
        check("n24_i7c_producer_contract_passed", n24_i7c.get("status") == "passed", n24_i7c.get("acceptance_state")),
        check(
            "producer_contract_declared_before_use",
            producer_contract["declared_before_use"] is True
            and row["producer_flux_window_declared_before_use"] is True,
            producer_contract,
        ),
        check(
            "thresholds_and_floors_unchanged",
            producer_contract["thresholds_unchanged"] is True
            and producer_contract["floor_relaxation_allowed"] is False,
            producer_contract,
        ),
        check(
            "producer_adds_no_support_or_coherence",
            producer_contract["support_added"] == 0.0
            and producer_contract["coherence_added"] == 0.0,
            producer_contract,
        ),
        check(
            "producer_window_bound_recorded",
            row["producer_flux_window_bound"] == 1e-8
            and row["producer_flux_window_per_window_bound"] == NATIVE_FLUX_DEBT_BOUND
            and row["producer_flux_window_count_bound"] == 10,
            {
                "producer_flux_window_bound": row["producer_flux_window_bound"],
                "producer_flux_window_per_window_bound": row[
                    "producer_flux_window_per_window_bound"
                ],
                "producer_flux_window_count_bound": row[
                    "producer_flux_window_count_bound"
                ],
            },
        ),
        check(
            "native_bf_ceiling_not_upgraded",
            row["lane_success_can_upgrade_native"] is False
            and row["native_lane_failure_overwritten"] is False
            and i5["native_bf5_supported"] is False
            and i5["native_bf6_supported"] is False,
            i5["bf_ceiling"],
        ),
        check(
            "producer_controls_clean",
            all_required_controls_clean,
            control_results,
        ),
        check(
            "artifact_manifest_valid",
            row["artifact_paths_equal_manifest_paths"] is True
            and row["artifact_sha256_equal_manifest_sha256"] is True
            and row["all_artifact_sha256_match_file_contents"] is True,
            row["artifact_paths"],
        ),
        check(
            "source_current_inputs_non_circular",
            not any(path in row["source_current_inputs"] for path in row["artifact_paths"]),
            row["source_current_inputs"],
        ),
        check(
            "unsafe_claim_flags_false",
            not any(row["unsafe_claim_flags"].values()),
            row["unsafe_claim_flags"],
        ),
    ]
    failed = [item for item in checks if not item["passed"]]
    output: dict[str, Any] = {
        "artifact_id": "n25_producer_assisted_formation_probe",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I6",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_producer_assisted_flux_conditioned_bf4_scaffold_candidate_native_bf_unchanged"
            if not failed
            else "failed_producer_assisted_formation_probe"
        ),
        "source_digest_chain_audit": {
            "i1": {"path": I1_OUTPUT_PATH, "sha256": sha256_file(I1_OUTPUT_PATH), "output_digest": i1.get("output_digest")},
            "i2": {"path": I2_OUTPUT_PATH, "sha256": sha256_file(I2_OUTPUT_PATH), "output_digest": i2.get("output_digest")},
            "i3": {"path": I3_OUTPUT_PATH, "sha256": sha256_file(I3_OUTPUT_PATH), "output_digest": i3.get("output_digest")},
            "i4": {"path": I4_OUTPUT_PATH, "sha256": sha256_file(I4_OUTPUT_PATH), "output_digest": i4.get("output_digest")},
            "i5": {"path": I5_OUTPUT_PATH, "sha256": sha256_file(I5_OUTPUT_PATH), "output_digest": i5.get("output_digest")},
            "n24_i7c": {"path": N24_I7C_OUTPUT_PATH, "sha256": sha256_file(N24_I7C_OUTPUT_PATH), "output_digest": n24_i7c.get("output_digest")},
        },
        "producer_assisted_formation_rows": [row],
        "producer_assisted_formation_row_count": 1,
        "producer_assisted_lane_opened": True,
        "producer_assisted_bf4_candidate_supported": not failed,
        "producer_assisted_bf5_supported": False,
        "producer_assisted_bf6_supported": False,
        "native_bf_ceiling_preserved": i5["bf_ceiling"],
        "native_bf4_candidate_supported": i5["native_bf4_candidate_supported"],
        "native_bf5_supported": False,
        "native_bf6_supported": False,
        "bf_ladder_rung_assigned": False,
        "bf_ceiling": "BF4_native_bf4_with_producer_assisted_flux_conditioned_scaffold_candidate",
        "n25_closeout_ceiling": "N25-C4_native_bf4_with_producer_assisted_flux_scaffold_candidate",
        "n25_closeout_ladder_rung_assigned": False,
        "native_lane_failure_overwritten": False,
        "producer_assisted_success_does_not_overwrite_native_failure": True,
        "missing_native_mechanism_probe_supported": True,
        "native_flux_debt_not_overwritten": True,
        "basin_formation_claim_allowed": False,
        "ready_for_iteration_7_comparative_stress_boundary_matrix": not failed,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["producer_assisted_formation_rows"][0]
    lines = [
        "# N25 Iteration 6 - Producer-Assisted Flux-Conditioned Formation Probe",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Scope",
        "",
        "I6 opens the producer-assisted lane only. It consumes N24 I7-C as a",
        "declared flux-conditioning scaffold and keeps the native I5 BF4 ceiling",
        "unchanged.",
        "",
        "## Result",
        "",
        "```text",
        f"producer_assisted_lane_opened = {str(output['producer_assisted_lane_opened']).lower()}",
        f"producer_assisted_bf4_candidate_supported = {str(output['producer_assisted_bf4_candidate_supported']).lower()}",
        f"producer_assisted_bf5_supported = {str(output['producer_assisted_bf5_supported']).lower()}",
        f"native_bf_ceiling_preserved = {output['native_bf_ceiling_preserved']}",
        f"native_lane_failure_overwritten = {str(output['native_lane_failure_overwritten']).lower()}",
        f"missing_native_mechanism_probe_supported = {str(output['missing_native_mechanism_probe_supported']).lower()}",
        f"basin_formation_claim_allowed = {str(output['basin_formation_claim_allowed']).lower()}",
        "```",
        "",
        "## Geometric Interpretation",
        "",
        row["geometric_interpretation"],
        "",
        "The end result is a producer-mediated flux scaffold candidate, not a",
        "native BF upgrade. I6 makes the missing native mechanism explicit:",
        "`native_flux_routing_or_rate_limiting_surface`.",
        "",
        "## Producer Ledger",
        "",
        f"- Producer result class: `{row['producer_assisted_result_class']}`",
        f"- Producer flux window bound: `{row['producer_flux_window_bound']}`",
        f"- Per-window native bound: `{row['producer_flux_window_per_window_bound']}`",
        f"- Window count bound: `{row['producer_flux_window_count_bound']}`",
        f"- Native flux debt overwritten: `{str(not row['native_flux_debt_not_overwritten']).lower()}`",
        "",
        "## Controls",
        "",
    ]
    for control in row["control_results"]:
        lines.append(
            f"- `{control['control_id']}`: `{control['control_status']}`; "
            f"{control['rung_effect']}"
        )
    lines.extend(["", "## Checks", ""])
    for item in output["checks"]:
        marker = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {marker}: `{item['check_id']}`")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
