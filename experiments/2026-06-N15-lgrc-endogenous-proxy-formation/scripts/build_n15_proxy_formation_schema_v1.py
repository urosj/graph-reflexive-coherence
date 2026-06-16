#!/usr/bin/env python3
"""Build N15 Iteration 2 proxy formation schema and AP5 gate."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N15-lgrc-endogenous-proxy-formation"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
CONFIGS = EXPERIMENT / "configs"
SCRIPTS = EXPERIMENT / "scripts"
INVENTORY_OUTPUT = OUTPUTS / "n15_proxy_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n15_proxy_source_inventory.md"

OUTPUT_PATH = OUTPUTS / "n15_proxy_formation_schema_v1.json"
REPORT_PATH = REPORTS / "n15_proxy_formation_schema_v1.md"
VALIDATOR_SCRIPT = SCRIPTS / "validate_n15_row.py"
CONFIG_PATHS = {
    "source_registry": CONFIGS / "n15_source_registry.json",
    "derivation_policy": CONFIGS / "n15_derivation_policy_v1.json",
    "budget_limits": CONFIGS / "n15_budget_limits_v1.json",
    "control_variants": CONFIGS / "n15_control_variants_v1.json",
    "replay_policy": CONFIGS / "n15_replay_policy_v1.json",
}
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "scripts/build_n15_proxy_formation_schema_v1.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

AP_LADDER = {
    "AP0": {
        "label": "passive integrated replay",
        "n15_interpretation": "source or boundary input with no proxy-formation claim",
    },
    "AP1": {
        "label": "runtime-visible trigger produces bounded response",
        "n15_interpretation": (
            "bounded response or trigger surface exists, but no runtime-derived "
            "proxy/target formation is supported"
        ),
    },
    "AP2": {
        "label": "support-sensitive regulation preserves a declared support condition",
        "n15_interpretation": (
            "direct historic support-derived target evidence can exist at AP2 "
            "scope, but AP5 derivation and uptake remain unproven"
        ),
    },
    "AP3": {
        "label": "self-maintenance candidate",
        "n15_interpretation": (
            "N13 support-seeking regulation is usable as the support axis for "
            "old-best-claims construction"
        ),
    },
    "AP4": {
        "label": "consequence-sensitive selection",
        "n15_interpretation": (
            "N14 consequence-sensitive selection is usable as the selection and "
            "consequence-context axis for old-best-claims construction"
        ),
    },
    "AP5": {
        "label": "endogenous proxy candidate",
        "n15_interpretation": (
            "proxy/target conditions are generated before downstream use from "
            "source-current runtime-visible artifact state under controls"
        ),
    },
    "AP6": {
        "label": "self/environment boundary candidate",
        "n15_interpretation": "reserved for N16",
    },
    "AP7": {
        "label": "closed action-perception loop candidate",
        "n15_interpretation": "reserved for N17",
    },
    "AP8": {
        "label": "long-horizon agentic-like closure candidate",
        "n15_interpretation": "reserved for N18",
    },
}

ROW_SCHEMA_FIELDS = [
    "row_id",
    "source_experiment",
    "source_iteration",
    "source_artifact",
    "source_report",
    "source_sha256",
    "source_report_sha256",
    "mechanism_name",
    "mechanism_role",
    "source_role_classification",
    "evidence_strategy",
    "old_best_claim_inputs",
    "direct_historic_support_status",
    "arc_method_mapping",
    "runtime_state_surface_id",
    "state_source_window",
    "source_current",
    "support_state_descriptor",
    "identity_condition_descriptor",
    "memory_state_descriptor",
    "regulation_state_descriptor",
    "declared_proxy_absent",
    "external_target_input_absent",
    "endogenous_derivation_policy",
    "target_condition_generated_at",
    "target_condition_surface",
    "target_band",
    "target_tolerance",
    "target_center",
    "drift_bound",
    "drift_update_rule",
    "drift_clamp_policy",
    "dependency_trace",
    "budget_cost_surface",
    "budget_units",
    "budget_validity",
    "replay_digest_inputs",
    "replay_digest_algorithm",
    "idempotency_digest_plan",
    "fully_native_integration_opened",
    "artifact_only_replay_status",
    "snapshot_load_status",
    "order_inversion_replay_status",
    "externally_injected_target_control",
    "hidden_target_derivation_control",
    "post_hoc_proxy_formation_control",
    "unbounded_target_drift_control",
    "budget_surface_ambiguity_control",
    "semantic_goal_ownership_relabel_control",
    "identity_acceptance_relabel_control",
    "native_support_relabel_control",
    "provisional_ap_level",
    "provisional_claim_ceiling",
    "blocked_claims",
    "missing_gates",
]

TOP_LEVEL_OUTPUT_FIELDS = [
    "experiment",
    "iteration",
    "artifact_id",
    "purpose",
    "schema_version",
    "generated_at",
    "command",
    "status",
    "acceptance_state",
    "source_artifacts",
    "source_reports",
    "rows",
    "controls",
    "checks",
    "claim_flags",
    "errors",
    "output_digest",
]

TOP_LEVEL_SCHEMA_FREEZE_FIELDS = [
    "experiment",
    "iteration",
    "artifact_id",
    "purpose",
    "schema_version",
    "generated_at",
    "command",
    "status",
    "acceptance_state",
    "target_ap_ceiling",
    "iteration_result",
    "schema_summary",
    "ap_ladder",
    "row_schema_fields",
    "top_level_output_fields",
    "top_level_schema_freeze_fields",
    "ap5_required_gates",
    "endogenous_derivation_policy",
    "old_best_claims_composition",
    "bounded_drift_policy",
    "budget_limits",
    "dependency_trace_format",
    "replay_digest_policy",
    "perturbation_policy",
    "hypothesis_decision_rubric",
    "control_requirements",
    "config_file_contracts",
    "schema_validation_contract",
    "fail_closed_error_labels",
    "rows",
    "controls",
    "claim_flags",
    "checks",
    "source_artifacts",
    "source_reports",
    "errors",
    "git",
    "output_digest",
]

AP5_REQUIRED_GATES = [
    "runtime_visible_source_state_inventory_present",
    "source_artifact_report_digest_for_each_state_input",
    "source_current_freshness_record_present",
    "support_state_descriptor_present",
    "memory_state_descriptor_or_explicit_absence_present",
    "regulation_state_descriptor_or_explicit_absence_present",
    "support_identity_condition_descriptor_or_explicit_absence_present",
    "declared_external_proxy_absent",
    "externally_injected_target_rejection_policy_present",
    "hidden_target_derivation_rejection_policy_present",
    "hidden_target_derivation_control_fails_closed",
    "endogenous_derivation_policy_present",
    "target_condition_generated_before_downstream_use",
    "target_condition_surface_present",
    "target_center_present",
    "target_band_or_threshold_present",
    "target_tolerance_present",
    "bounded_drift_policy_present",
    "drift_clamp_policy_present",
    "budget_cost_surface_present",
    "budget_units_present",
    "budget_validity_policy_present",
    "dependency_trace_from_source_state_to_target_condition_present",
    "idempotency_digest_plan_present",
    "generated_target_consumable_by_rank_or_regulation_without_goal_ownership_relabel",
    "artifact_only_replay_requirement_present",
    "snapshot_load_equivalence_requirement_present",
    "order_inversion_replay_requirement_present",
    "post_hoc_proxy_formation_rejection_policy_present",
    "negative_controls_present",
    "compatibility_checks_present",
    "claim_flags_forced_false",
    "src_diff_empty_true",
    "native_supported_flags_false",
    "phase8_opened_false",
    "fully_native_integration_opened_false",
]

CONTROL_REQUIREMENTS = [
    {
        "control_id": "externally_injected_target_control",
        "expected_status": "blocked",
        "expected_blocker": "externally_injected_target_blocked",
    },
    {
        "control_id": "hidden_target_derivation_control",
        "expected_status": "blocked",
        "expected_blocker": "hidden_target_derivation_blocked",
    },
    {
        "control_id": "semantic_goal_ownership_relabel_control",
        "expected_status": "blocked",
        "expected_blocker": "semantic_goal_ownership_relabel_blocked",
    },
    {
        "control_id": "post_hoc_proxy_formation_control",
        "expected_status": "blocked",
        "expected_blocker": "post_hoc_proxy_formation_blocked",
    },
    {
        "control_id": "unbounded_target_drift_control",
        "expected_status": "blocked",
        "expected_blocker": "unbounded_target_drift_blocked",
    },
    {
        "control_id": "budget_surface_ambiguity_control",
        "expected_status": "blocked",
        "expected_blocker": "budget_surface_ambiguity_blocked",
    },
    {
        "control_id": "identity_acceptance_relabel_control",
        "expected_status": "blocked",
        "expected_blocker": "identity_acceptance_relabel_blocked",
    },
    {
        "control_id": "native_support_relabel_control",
        "expected_status": "blocked",
        "expected_blocker": "native_support_relabel_blocked",
    },
    {
        "control_id": "fixture_label_proxy_control",
        "expected_status": "blocked",
        "expected_blocker": "fixture_label_proxy_blocked",
    },
    {
        "control_id": "stale_source_state_control",
        "expected_status": "blocked",
        "expected_blocker": "stale_source_state_blocked",
    },
    {
        "control_id": "missing_source_state_control",
        "expected_status": "blocked",
        "expected_blocker": "missing_source_state_blocked",
    },
    {
        "control_id": "dependency_trace_omission_control",
        "expected_status": "blocked",
        "expected_blocker": "dependency_trace_omission_blocked",
    },
]

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "selfhood_claim_allowed": False,
    "personhood_claim_allowed": False,
    "biological_behavior_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
}

ENDOGENOUS_DERIVATION_POLICY = {
    "policy_id": "n15_endogenous_proxy_derivation_policy_v1",
    "policy_version": "1.0",
    "policy_kind": "trace_preserving_old_best_claims_construction",
    "input_fields": [
        "support_margin",
        "regulation_recovery_score",
        "memory_context_score",
        "ap4_consequence_context_score",
        "readiness_context_flag",
    ],
    "input_normalization": {
        "numeric_support_fields": "normalize to [-1.0, 1.0] around the frozen support threshold",
        "ordinal_fields": "map by the frozen ordinal codebook",
        "missing_input_policy": "fail_closed",
        "stale_input_policy": "fail_closed",
    },
    "ordinal_codebook": {
        "blocked": -1.0,
        "absent": 0.0,
        "present": 0.5,
        "supported": 1.0,
    },
    "composition_weights": {
        "support_margin": 0.4,
        "regulation_recovery_score": 0.25,
        "memory_context_score": 0.2,
        "ap4_consequence_context_score": 0.15,
        "readiness_context_flag": 0.0,
    },
    "composition_rule": (
        "weighted sum over normalized support, regulation, memory, and AP4 "
        "consequence context; N12 readiness contributes only validation context "
        "and never changes the target value"
    ),
    "target_center_rule": (
        "target_center = clamp(support_threshold + 0.10 * weighted_sum, "
        "support_threshold - 0.10, support_threshold + 0.10)"
    ),
    "target_tolerance_rule": (
        "target_tolerance = clamp(0.05 + 0.02 * max(regulation_recovery_score, 0), "
        "0.03, 0.08)"
    ),
    "target_band_rule": (
        "numeric target_band = [target_center - target_tolerance, "
        "target_center + target_tolerance]; ordinal target_band uses the "
        "codebook category plus one adjacent category only when the drift policy allows it"
    ),
    "drift_bound_rule": "use bounded_drift_policy_v1",
    "clamp_rule": "clamp out-of-bound updates and mark drift_clamped = true",
    "budget_rule": "use budget_limits_v1 before any downstream target use",
    "digest_scope": "use replay_digest_policy_v1",
}

OLD_BEST_CLAIMS_COMPOSITION = {
    "operator_id": "n15_trace_preserving_old_best_claims_composition_v1",
    "source_axes": {
        "N13_AP3": "support-seeking regulation axis",
        "N14_AP4": "consequence-sensitive selection axis",
        "N08": "memory/context axis",
        "N09": "bounded-regulation context axis",
        "N12_NAT4": "readiness-only context",
    },
    "rules": [
        "source rows are consumed only at closed claim ceilings",
        "every source contribution is recorded in old_best_claim_inputs",
        "every target field has a dependency-trace entry",
        "N12 readiness cannot contribute native-support evidence",
        "constructed N14 followout remains constructed followout",
        "result remains AP5_candidate until controls and replay pass",
    ],
}

BOUNDED_DRIFT_POLICY = {
    "policy_id": "n15_bounded_drift_policy_v1",
    "numeric_target_center_max_update": 0.10,
    "numeric_target_tolerance_max_update": 0.05,
    "numeric_scale": "0_to_1_source_scale",
    "ordinal_max_update": "one_adjacent_category_per_derivation_step",
    "clamp_status_field": "drift_clamped",
    "unconfigured_or_unbounded_drift": "fail_closed",
}

BUDGET_LIMITS = {
    "policy_id": "n15_budget_limits_v1",
    "units": [
        "source_row_count",
        "transform_count",
        "canonical_json_input_bytes",
        "canonical_json_output_bytes",
        "replay_count",
        "validation_count",
        "wall_clock_seconds",
    ],
    "limits": {
        "source_row_count": 12,
        "transform_count": 24,
        "canonical_json_input_bytes": 262144,
        "canonical_json_output_bytes": 262144,
        "replay_count": 6,
        "validation_count": 64,
        "wall_clock_seconds": 60,
    },
    "validity_rule": "budget is checked before target use; missing or exceeded limits fail closed",
}

DEPENDENCY_TRACE_FORMAT = {
    "format_id": "n15_dependency_trace_v1",
    "container": "list",
    "required_fields": [
        "target_field",
        "source_row_id",
        "source_artifact",
        "source_sha256",
        "source_field",
        "transform_id",
        "transform_parameters",
        "claim_ceiling_of_source",
    ],
    "completeness_rule": (
        "every emitted target field requires at least one trace entry with a "
        "source row, transform, and claim ceiling"
    ),
}

REPLAY_DIGEST_POLICY = {
    "policy_id": "n15_replay_digest_policy_v1",
    "algorithm": "sha256",
    "encoding": "canonical_json_sorted_keys_ascii",
    "include": [
        "source_artifact_digests",
        "selected_source_rows",
        "endogenous_derivation_policy",
        "old_best_claim_inputs",
        "runtime_state_vector",
        "drift_policy",
        "budget_surface",
        "dependency_trace",
        "target_condition",
        "claim_flags",
    ],
    "exclude": [
        "generated_at",
        "local_filesystem_paths",
        "git_working_tree_metadata",
        "wall_clock_timestamps",
    ],
}

PERTURBATION_POLICY = {
    "policy_id": "n15_iteration6_perturbation_defaults_v1",
    "support_state": "one bounded step lower and higher relative to support threshold",
    "memory_state": "one bounded step across memory/context codebook",
    "regulation_state": "one bounded step across regulation recovery codebook",
    "stale_state": "source_current = false or outside freshness window",
    "budget_invalid": "exceed one frozen budget limit before target use",
    "order_inversion": (
        "reverse and shuffle source rows while preserving row ids and digests; "
        "canonical replay must reproduce the same target"
    ),
}

HYPOTHESIS_DECISION_RUBRIC = {
    "supported": "all required gates validated and associated negative controls fail closed",
    "deferred": "source coverage exists but a required gate, replay, or control has not run",
    "rejected": "a required gate fails or a negative control passes without a valid blocker",
    "partial_or_scope_limited": (
        "a narrower candidate is supported but full AP5 is blocked by explicit "
        "scope caveat"
    ),
}

FAIL_CLOSED_ERROR_LABELS = [
    "source_artifact_missing",
    "sha256_mismatch",
    "stale_source_state",
    "missing_derivation_policy",
    "trace_incomplete",
    "budget_exceeded",
    "derivation_non_deterministic",
    "control_unexpectedly_passed",
    "unsafe_claim_flag_true",
    "absolute_path_recorded",
]

CONFIG_FILE_CONTRACTS = {
    "configs/n15_source_registry.json": {
        "status": "materialized_in_iteration2_gap_closure",
        "required_content": ["portable source paths", "expected sha256 values"],
    },
    "configs/n15_derivation_policy_v1.json": {
        "status": "materialized_in_iteration2_gap_closure",
        "required_content": ["ENDOGENOUS_DERIVATION_POLICY"],
    },
    "configs/n15_budget_limits_v1.json": {
        "status": "materialized_in_iteration2_gap_closure",
        "required_content": ["BUDGET_LIMITS"],
    },
    "configs/n15_control_variants_v1.json": {
        "status": "materialized_in_iteration2_gap_closure",
        "required_content": ["CONTROL_REQUIREMENTS"],
    },
    "configs/n15_replay_policy_v1.json": {
        "status": "materialized_in_iteration2_gap_closure",
        "required_content": ["REPLAY_DIGEST_POLICY", "PERTURBATION_POLICY"],
    },
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": None if artifact is None else artifact.get("status"),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
    }


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def build_config_payloads(inventory: dict[str, Any]) -> dict[Path, dict[str, Any]]:
    source_registry = {
        "experiment": "N15",
        "config_id": "n15_source_registry",
        "generated_at": GENERATED_AT,
        "source_inventory": source_artifact(INVENTORY_OUTPUT, inventory),
        "source_inventory_report": source_report(INVENTORY_REPORT),
        "rows": [
            {
                "row_id": row["row_id"],
                "source_experiment": row["source_experiment"],
                "source_artifact": row["source_artifact"],
                "source_sha256": row["source_sha256"],
                "source_report": row["source_report"],
                "source_report_sha256": row["source_report_sha256"],
                "source_role_classification": row["source_role_classification"],
                "evidence_strategy": row["evidence_strategy"],
                "provisional_ap_level": row["provisional_ap_level"],
                "provisional_claim_ceiling": row["provisional_claim_ceiling"],
            }
            for row in inventory["rows"]
        ],
        "claim_boundary": {
            "final_ap5_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "fully_native_integration_opened": False,
        },
    }
    derivation_policy = {
        "experiment": "N15",
        "config_id": "n15_derivation_policy_v1",
        "generated_at": GENERATED_AT,
        "endogenous_derivation_policy": ENDOGENOUS_DERIVATION_POLICY,
        "old_best_claims_composition": OLD_BEST_CLAIMS_COMPOSITION,
        "bounded_drift_policy": BOUNDED_DRIFT_POLICY,
        "dependency_trace_format": DEPENDENCY_TRACE_FORMAT,
        "target_ap_ceiling": "AP5",
    }
    budget_limits = {
        "experiment": "N15",
        "config_id": "n15_budget_limits_v1",
        "generated_at": GENERATED_AT,
        "budget_limits": BUDGET_LIMITS,
        "bounded_drift_policy": BOUNDED_DRIFT_POLICY,
    }
    control_variants = {
        "experiment": "N15",
        "config_id": "n15_control_variants_v1",
        "generated_at": GENERATED_AT,
        "control_requirements": CONTROL_REQUIREMENTS,
        "required_controls": {
            control["control_id"]: "required_before_ap5"
            for control in CONTROL_REQUIREMENTS
        },
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "fail_closed_error_labels": FAIL_CLOSED_ERROR_LABELS,
    }
    replay_policy = {
        "experiment": "N15",
        "config_id": "n15_replay_policy_v1",
        "generated_at": GENERATED_AT,
        "replay_digest_policy": REPLAY_DIGEST_POLICY,
        "perturbation_policy": PERTURBATION_POLICY,
    }
    return {
        CONFIG_PATHS["source_registry"]: source_registry,
        CONFIG_PATHS["derivation_policy"]: derivation_policy,
        CONFIG_PATHS["budget_limits"]: budget_limits,
        CONFIG_PATHS["control_variants"]: control_variants,
        CONFIG_PATHS["replay_policy"]: replay_policy,
    }


def write_config_files(config_payloads: dict[Path, dict[str, Any]]) -> None:
    CONFIGS.mkdir(parents=True, exist_ok=True)
    for path, payload in config_payloads.items():
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def materialized_config_contracts() -> dict[str, dict[str, Any]]:
    contracts: dict[str, dict[str, Any]] = {}
    for relative_path, contract in CONFIG_FILE_CONTRACTS.items():
        path = EXPERIMENT / relative_path
        materialized = path.exists()
        contracts[relative_path] = {
            **contract,
            "path": relative_path,
            "materialized": materialized,
            "sha256": digest_file(path) if materialized else None,
        }
    return contracts


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        )
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    inventory_rows = inventory["rows"]
    inventory_row_fields = set().union(*(row.keys() for row in inventory_rows))
    row_schema_fields = set(ROW_SCHEMA_FIELDS)
    claim_flags = CLAIM_FLAGS_FORCED_FALSE
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "inventory_acceptance_state_valid": inventory["acceptance_state"]
        == "accepted_proxy_source_inventory_only_no_ap5",
        "row_schema_covers_inventory_rows": inventory_row_fields.issubset(
            row_schema_fields
        ),
        "row_schema_has_budget_units": "budget_units" in row_schema_fields,
        "row_schema_has_idempotency_digest_plan": "idempotency_digest_plan"
        in row_schema_fields,
        "ap5_gate_contains_hidden_target_control": (
            "hidden_target_derivation_control_fails_closed" in AP5_REQUIRED_GATES
        ),
        "ap5_gate_contains_target_consumability": (
            "generated_target_consumable_by_rank_or_regulation_without_goal_ownership_relabel"
            in AP5_REQUIRED_GATES
        ),
        "ap5_gate_contains_fully_native_flag": (
            "fully_native_integration_opened_false" in AP5_REQUIRED_GATES
        ),
        "derivation_policy_frozen": ENDOGENOUS_DERIVATION_POLICY[
            "policy_id"
        ]
        == "n15_endogenous_proxy_derivation_policy_v1",
        "old_best_composition_frozen": OLD_BEST_CLAIMS_COMPOSITION[
            "operator_id"
        ]
        == "n15_trace_preserving_old_best_claims_composition_v1",
        "target_band_contract_frozen": all(
            key in ENDOGENOUS_DERIVATION_POLICY
            for key in [
                "target_center_rule",
                "target_tolerance_rule",
                "target_band_rule",
            ]
        ),
        "dependency_trace_format_frozen": DEPENDENCY_TRACE_FORMAT[
            "required_fields"
        ]
        == [
            "target_field",
            "source_row_id",
            "source_artifact",
            "source_sha256",
            "source_field",
            "transform_id",
            "transform_parameters",
            "claim_ceiling_of_source",
        ],
        "drift_bounds_frozen": BOUNDED_DRIFT_POLICY[
            "numeric_target_center_max_update"
        ]
        == 0.10
        and BOUNDED_DRIFT_POLICY["ordinal_max_update"]
        == "one_adjacent_category_per_derivation_step",
        "budget_units_and_limits_frozen": set(BUDGET_LIMITS["units"])
        == set(BUDGET_LIMITS["limits"].keys()),
        "replay_digest_policy_frozen": REPLAY_DIGEST_POLICY["algorithm"] == "sha256",
        "top_level_runtime_output_shape_frozen": TOP_LEVEL_OUTPUT_FIELDS
        == [
            "experiment",
            "iteration",
            "artifact_id",
            "purpose",
            "schema_version",
            "generated_at",
            "command",
            "status",
            "acceptance_state",
            "source_artifacts",
            "source_reports",
            "rows",
            "controls",
            "checks",
            "claim_flags",
            "errors",
            "output_digest",
        ],
        "top_level_schema_freeze_shape_declared": len(
            TOP_LEVEL_SCHEMA_FREEZE_FIELDS
        )
        == 38,
        "control_requirements_count": len(CONTROL_REQUIREMENTS) == 12,
        "config_file_contracts_materialized": all(
            (EXPERIMENT / relative_path).exists()
            for relative_path in CONFIG_FILE_CONTRACTS
        ),
        "schema_validator_script_present": VALIDATOR_SCRIPT.exists(),
        "perturbation_policy_frozen": PERTURBATION_POLICY["policy_id"]
        == "n15_iteration6_perturbation_defaults_v1",
        "hypothesis_decision_rubric_frozen": set(HYPOTHESIS_DECISION_RUBRIC)
        == {"supported", "deferred", "rejected", "partial_or_scope_limited"},
        "fail_closed_error_labels_frozen": len(FAIL_CLOSED_ERROR_LABELS) == 10,
        "claim_flags_forced_false": all(value is False for value in claim_flags.values()),
        "phase8_opened_false": inventory["iteration_result"]["phase8_opened"]
        is False,
        "native_support_not_opened": inventory["iteration_result"][
            "native_support_opened"
        ]
        is False,
        "fully_native_integration_not_opened": inventory["iteration_result"][
            "fully_native_integration_opened"
        ]
        is False,
        "no_final_ap5_assigned": inventory["iteration_result"][
            "final_ap5_supported"
        ]
        is False,
        "src_diff_empty": git_status_short("src") == "",
    }
    schema_summary = {
        "row_schema_field_count": len(ROW_SCHEMA_FIELDS),
        "ap5_required_gate_count": len(AP5_REQUIRED_GATES),
        "control_requirement_count": len(CONTROL_REQUIREMENTS),
        "materialized_config_file_count": len(CONFIG_FILE_CONTRACTS),
        "fail_closed_error_label_count": len(FAIL_CLOSED_ERROR_LABELS),
        "final_ap5_rows": 0,
    }
    acceptance_state = (
        "accepted_schema_freeze_no_row_validation"
        if all(checks.values())
        else "rejected_schema_freeze"
    )
    output: dict[str, Any] = {
        "experiment": "N15",
        "iteration": 2,
        "artifact_id": "n15_proxy_formation_schema_v1",
        "purpose": "proxy_formation_schema_and_ap5_gate",
        "schema_version": "n15_proxy_formation_schema_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP5",
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "schema_freeze_passed": all(checks.values()),
            "row_validation_started": False,
            "final_ap5_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "fully_native_integration_opened": False,
            "semantic_goal_ownership_opened": False,
            "agency_claim_opened": False,
        },
        "schema_summary": schema_summary,
        "ap_ladder": AP_LADDER,
        "row_schema_fields": ROW_SCHEMA_FIELDS,
        "top_level_output_fields": TOP_LEVEL_OUTPUT_FIELDS,
        "top_level_schema_freeze_fields": TOP_LEVEL_SCHEMA_FREEZE_FIELDS,
        "ap5_required_gates": AP5_REQUIRED_GATES,
        "endogenous_derivation_policy": ENDOGENOUS_DERIVATION_POLICY,
        "old_best_claims_composition": OLD_BEST_CLAIMS_COMPOSITION,
        "bounded_drift_policy": BOUNDED_DRIFT_POLICY,
        "budget_limits": BUDGET_LIMITS,
        "dependency_trace_format": DEPENDENCY_TRACE_FORMAT,
        "replay_digest_policy": REPLAY_DIGEST_POLICY,
        "perturbation_policy": PERTURBATION_POLICY,
        "hypothesis_decision_rubric": HYPOTHESIS_DECISION_RUBRIC,
        "control_requirements": CONTROL_REQUIREMENTS,
        "config_file_contracts": materialized_config_contracts(),
        "schema_validation_contract": {
            "validator_kind": "project_local_python_validator",
            "validator_script": rel(VALIDATOR_SCRIPT),
            "required_checks": [
                "required_fields_present",
                "claim_flags_forced_false",
                "control_outcomes_present",
                "source_digest_presence",
                "digest_reproducibility",
                "absolute_path_absence",
            ],
        },
        "fail_closed_error_labels": FAIL_CLOSED_ERROR_LABELS,
        "rows": [],
        "controls": {
            control["control_id"]: "required_before_ap5"
            for control in CONTROL_REQUIREMENTS
        },
        "claim_flags": claim_flags,
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory)
        },
        "source_reports": {rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT)},
        "errors": [],
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["checks"]["top_level_schema_freeze_shape_matches_output"] = set(
        TOP_LEVEL_SCHEMA_FREEZE_FIELDS
    ) == set(output) | {"output_digest"}
    output["checks"]["no_absolute_paths_recorded"] = not contains_absolute_path(output)
    output["status"] = "passed" if all(output["checks"].values()) else "failed"
    output["acceptance_state"] = (
        "accepted_schema_freeze_no_row_validation"
        if all(output["checks"].values())
        else "rejected_schema_freeze"
    )
    output["iteration_result"]["acceptance_state"] = output["acceptance_state"]
    output["iteration_result"]["schema_freeze_passed"] = output["status"] == "passed"
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N15 Proxy Formation Schema And AP5 Gate",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(output["schema_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 2 freezes the N15 row schema, AP5 gate, derivation policy,",
        "old-best-claims composition operator, drift policy, budget units,",
        "dependency trace format, replay digest scope, perturbation defaults,",
        "control requirements, config-file contracts, output shape, and",
        "fail-closed error labels. Post-review gap closure materializes",
        "the planned config files, splits runtime output fields from I2",
        "schema-freeze metadata fields, and links the local validator.",
        "It does not validate rows beyond the Iteration 1 inventory,",
        "generate a target, run controls, or assign final `AP5`.",
        "",
        "## Top-Level Contracts",
        "",
        "Runtime row outputs must include these fields:",
        "",
        "```json",
        json.dumps(output["top_level_output_fields"], indent=2),
        "```",
        "",
        "The Iteration 2 schema-freeze artifact includes these fields:",
        "",
        "```json",
        json.dumps(output["top_level_schema_freeze_fields"], indent=2),
        "```",
        "",
        "## AP5 Gate",
        "",
        "| Gate |",
        "| --- |",
    ]
    for gate in output["ap5_required_gates"]:
        lines.append(f"| `{gate}` |")
    lines.extend(
        [
            "",
            "## Frozen Derivation Policy",
            "",
            "```json",
            json.dumps(
                output["endogenous_derivation_policy"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Budget And Drift",
            "",
            "```json",
            json.dumps(
                {
                    "bounded_drift_policy": output["bounded_drift_policy"],
                    "budget_limits": output["budget_limits"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Controls",
            "",
            "| Control | Expected status | Blocker |",
            "| --- | --- | --- |",
        ]
    )
    for control in output["control_requirements"]:
        lines.append(
            "| "
            f"`{control['control_id']}` | "
            f"`{control['expected_status']}` | "
            f"`{control['expected_blocker']}` |"
        )
    lines.extend(
        [
            "",
            "## Materialized Config Files",
            "",
            "| Config | SHA-256 |",
            "| --- | --- |",
        ]
    )
    for path, contract in output["config_file_contracts"].items():
        lines.append(f"| `{path}` | `{contract['sha256']}` |")
    lines.extend(
        [
            "",
            "## Schema Validator",
            "",
            "```json",
            json.dumps(
                output["schema_validation_contract"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "schema freeze != AP5 support",
            "derivation policy != generated target",
            "old-best-claims composition contract != semantic goal ownership",
            "N13 AP3 input != selfhood",
            "N14 AP4 input != intention or goal ownership",
            "N12 readiness-only context != native support",
            "N15 Iteration 2 != fully native integration",
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_config_files(build_config_payloads(load_json(INVENTORY_OUTPUT)))
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
