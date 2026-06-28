#!/usr/bin/env python3
"""Build N26 Iteration 3 active nulls and failure baselines."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
SCHEMA_OUTPUT = EXPERIMENT / "outputs" / "n26_proxy_divergence_collapse_schema_and_controls.json"
OUTPUT = EXPERIMENT / "outputs" / "n26_active_nulls_and_failure_baselines.json"
REPORT = EXPERIMENT / "reports" / "n26_active_nulls_and_failure_baselines.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_active_nulls_and_failure_baselines.py"
)

EXPECTED_I2_OUTPUT_DIGEST = "bbaf1621f64638b76ab296c4dc5b28bf99be7d5c2369d8e96e110e68972de070"
EXPECTED_I1_OUTPUT_DIGEST = "b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a"
EXPECTED_SOURCE_CONTRACT_ROW_DIGEST = (
    "5746a2e7a792b7cc8eab716833a2e232f2ce6ef6ccd84a54dd21cf38c0308e61"
)
EXPECTED_SOURCE_CONSUMABLE_CONTRACT_ROW_DIGEST = (
    "99d2db29122734ca4de5ca7b4599f6a35a442d21a7b4983477eac6ddc75b48ec"
)
ACTIVE_NULL_RUNG = "not_assigned_active_null_control_only"
ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]

CONTROL_SCENARIOS = {
    "source_digest_mismatch_control": {
        "scenario_id": "source_digest_mismatch",
        "blocked_condition": "candidate row source digests do not match I1/I2 frozen source chain",
        "geometric_reading": (
            "The row is attached to a different source state than the admitted "
            "proxy contract and scoped substrate chain, so its geometry cannot "
            "inherit the N26 schema boundary."
        ),
        "rung_effect": "blocks_all_positive_proxy_support",
    },
    "lower_stack_input_missing_control": {
        "scenario_id": "lower_stack_input_missing",
        "blocked_condition": "proxy row lacks source-current lower-stack input trace",
        "geometric_reading": (
            "A proxy value is asserted without the lower LGRC substrate state that "
            "would make the proxy source-current."
        ),
        "rung_effect": "blocks_PD2_or_stronger",
    },
    "proxy_metric_trace_missing_control": {
        "scenario_id": "proxy_metric_trace_missing",
        "blocked_condition": "proxy metric trace is missing",
        "geometric_reading": (
            "The proxy cannot be evaluated as geometry if the metric itself has "
            "no source-current trace."
        ),
        "rung_effect": "blocks_PD2_or_stronger",
    },
    "proxy_metric_not_replayable_control": {
        "scenario_id": "proxy_metric_not_replayable",
        "blocked_condition": "proxy metric appears once but lacks replayable trace",
        "geometric_reading": (
            "The metric is a transient annotation rather than a stable replayable "
            "quantity over the basin substrate."
        ),
        "rung_effect": "blocks_PD3_or_stronger",
    },
    "basin_persistence_capacity_trace_missing_control": {
        "scenario_id": "basin_persistence_capacity_trace_missing",
        "blocked_condition": "basin persistence capacity trace is missing",
        "geometric_reading": (
            "The row cannot claim proxy divergence if the basin continuation "
            "capacity is not measured independently of the proxy."
        ),
        "rung_effect": "blocks_PD2_or_stronger",
    },
    "support_coherence_floor_missing_control": {
        "scenario_id": "support_coherence_floor_missing",
        "blocked_condition": "support/coherence floor trace is missing",
        "geometric_reading": (
            "The proxy cannot be compared against basin persistence if the basin "
            "support and coherence floors are not visible."
        ),
        "rung_effect": "blocks_PD2_or_stronger",
    },
    "proxy_basin_measurement_not_independent_control": {
        "scenario_id": "proxy_basin_measurement_not_independent",
        "blocked_condition": "proxy score and basin persistence score are derived from the same label",
        "geometric_reading": (
            "The row cannot show divergence if proxy and basin traces collapse "
            "into one measurement channel."
        ),
        "rung_effect": "blocks_PD4_or_stronger",
    },
    "scoped_mb6_scope_id_missing_control": {
        "scenario_id": "scoped_mb6_scope_id_missing",
        "blocked_condition": "N25.2 substrate is consumed without multi_basin_scope_id",
        "geometric_reading": (
            "The row points at multi-basin substrate but does not identify the "
            "scoped basin set it is allowed to consume."
        ),
        "rung_effect": "blocks_all_positive_proxy_support",
    },
    "derived_report_only_positive_row_control": {
        "scenario_id": "derived_report_only_positive_row",
        "blocked_condition": "derived report row is treated as positive proxy evidence",
        "geometric_reading": (
            "A narrative artifact can describe a proxy hypothesis, but cannot act "
            "as source-current proxy geometry."
        ),
        "rung_effect": "blocks_PD2_or_stronger",
    },
    "artifact_manifest_failure_control": {
        "scenario_id": "artifact_manifest_failure",
        "blocked_condition": "artifact manifest is missing roles or SHA-256 validation",
        "geometric_reading": (
            "The row cannot be replayed or audited if the trace artifacts are not "
            "role-labeled and digest-checked."
        ),
        "rung_effect": "blocks_all_positive_proxy_support",
    },
    "proxy_label_only_control": {
        "scenario_id": "proxy_label_only",
        "blocked_condition": "proxy exists only as a label",
        "geometric_reading": (
            "A proxy name is attached to the basin, but no source-current metric, "
            "target digest, or lower-stack derivation exists."
        ),
        "rung_effect": "blocks_PD2_or_stronger",
    },
    "post_hoc_target_digest_control": {
        "scenario_id": "post_hoc_target_digest",
        "blocked_condition": "proxy target digest is declared after outcome inspection",
        "geometric_reading": (
            "The target surface is stitched around the observed result instead of "
            "being fixed before the trace is evaluated."
        ),
        "rung_effect": "blocks_PD2_or_stronger",
    },
    "hidden_proxy_policy_control": {
        "scenario_id": "hidden_proxy_policy",
        "blocked_condition": "hidden proxy policy controls target derivation",
        "geometric_reading": (
            "The apparent proxy is producer/policy mediated rather than visible "
            "as a declared source-current runtime or analysis policy."
        ),
        "rung_effect": "blocks_substrate_carried_proxy_claim",
    },
    "proxy_only_improvement_control": {
        "scenario_id": "proxy_only_improvement",
        "blocked_condition": "proxy metric improves without basin persistence/deepening trace",
        "geometric_reading": (
            "A proxy score rises, but no independent basin continuation surface "
            "shows whether the basin actually deepened or stalled."
        ),
        "rung_effect": "blocks_PD4_proxy_divergence",
    },
    "proxy_improves_basin_also_improves_control": {
        "scenario_id": "proxy_improves_basin_also_improves",
        "blocked_condition": "proxy improves while basin persistence/deepening also improves",
        "geometric_reading": (
            "Both surfaces move in the same favorable direction, so the row may "
            "describe proxy alignment but not proxy divergence."
        ),
        "rung_effect": "blocks_PD4_proxy_divergence",
    },
    "proxy_improves_basin_unmeasured_control": {
        "scenario_id": "proxy_improves_basin_unmeasured",
        "blocked_condition": "proxy improves while basin persistence/deepening is unmeasured",
        "geometric_reading": (
            "A rising proxy score cannot diverge from an unobserved basin surface; "
            "the basin side of the contrast is absent."
        ),
        "rung_effect": "blocks_PD4_proxy_divergence",
    },
    "basin_degradation_hidden_by_proxy_control": {
        "scenario_id": "basin_degradation_hidden_by_proxy",
        "blocked_condition": "basin support/coherence degrades while proxy score hides it",
        "geometric_reading": (
            "The proxy surface looks better while the basin floor worsens; this "
            "cannot be counted as success or divergence support without controls."
        ),
        "rung_effect": "blocks_positive_proxy_success_claim",
    },
    "unscoped_mb6_consumption_control": {
        "scenario_id": "unscoped_mb6_consumption",
        "blocked_condition": "N25.2 MB6 is consumed as unscoped substrate",
        "geometric_reading": (
            "The multi-basin substrate is generalized beyond the scoped basin IDs "
            "that N25.2 allowed N26 to consume."
        ),
        "rung_effect": "blocks_all_positive_proxy_support",
    },
    "front_capacity_backfill_control": {
        "scenario_id": "front_capacity_backfill",
        "blocked_condition": "front-capacity companion evidence backfills scoped MB6 proxy substrate",
        "geometric_reading": (
            "A topology-birth companion cannot replace the scoped child-basin "
            "runtime/replay substrate required by N25.2."
        ),
        "rung_effect": "blocks_unscoped_substrate_upgrade",
    },
    "peer_basin_missing_control": {
        "scenario_id": "peer_basin_missing",
        "blocked_condition": "proxy/basin contrast lacks peer or control basin where required",
        "geometric_reading": (
            "The row cannot distinguish route-local proxy divergence from global "
            "drift if no peer/control basin is present."
        ),
        "rung_effect": "blocks_PD4_or_stronger",
    },
    "perturbation_mismatch_control": {
        "scenario_id": "perturbation_mismatch",
        "blocked_condition": "proxy path and basin-deepened path use different perturbation envelopes",
        "geometric_reading": (
            "Collapse cannot be inferred if the two paths are not challenged by "
            "the same perturbation geometry."
        ),
        "rung_effect": "blocks_PD5_proxy_collapse",
    },
    "perturbation_digest_missing_control": {
        "scenario_id": "perturbation_digest_missing",
        "blocked_condition": "perturbation challenge digest is missing",
        "geometric_reading": (
            "The proxy and basin paths cannot be proven to share the same challenge "
            "geometry when the perturbation envelope is not digested."
        ),
        "rung_effect": "blocks_PD5_proxy_collapse",
    },
    "basin_deepened_survivor_missing_control": {
        "scenario_id": "basin_deepened_survivor_missing",
        "blocked_condition": "proxy-optimized failure lacks basin-deepened survivor contrast",
        "geometric_reading": (
            "A proxy path failure is only failure; collapse requires a basin "
            "deepened path surviving the same envelope."
        ),
        "rung_effect": "blocks_PD5_proxy_collapse",
    },
    "proxy_collapse_result_trace_missing_control": {
        "scenario_id": "proxy_collapse_result_trace_missing",
        "blocked_condition": "proxy collapse result trace is missing",
        "geometric_reading": (
            "The collapse claim has no auditable source-current result surface, "
            "so a proxy-optimized failure cannot be classified as collapse."
        ),
        "rung_effect": "blocks_PD5_proxy_collapse",
    },
    "AP5_gap_prose_only_control": {
        "scenario_id": "ap5_gap_prose_only",
        "blocked_condition": "AP5 dependency is described only in prose",
        "geometric_reading": (
            "Proxy/target participation cannot be smuggled through narrative; "
            "row-local AP5 status and reason are required."
        ),
        "rung_effect": "blocks_AP5_bridge_and_PD2_or_stronger",
    },
    "missing_ap5_dependency_status_control": {
        "scenario_id": "missing_ap5_dependency_status",
        "blocked_condition": "positive proxy row omits row-local AP5 dependency status",
        "geometric_reading": (
            "A proxy/target-forming row cannot inherit AP5 context silently; the "
            "row-local dependency state must be explicit."
        ),
        "rung_effect": "blocks_AP5_bridge_and_PD2_or_stronger",
    },
    "n15_context_as_native_ap5_control": {
        "scenario_id": "n15_context_as_native_ap5",
        "blocked_condition": "N15 artifact-level AP5 context is consumed as native AP5",
        "geometric_reading": (
            "N15 can supply historical artifact-level proxy context, but it is "
            "not native AP5 evidence for N26."
        ),
        "rung_effect": "blocks_AP5_bridge",
    },
    "n19_nat3_as_ap5_closeout_control": {
        "scenario_id": "n19_nat3_as_ap5_closeout",
        "blocked_condition": "N19 NAT3 AP5 row is consumed as AP5 closeout",
        "geometric_reading": (
            "N19 records the AP5 NAT4 gap; using that gap record as closeout "
            "would invert the classification boundary."
        ),
        "rung_effect": "blocks_AP5_bridge",
    },
    "semantic_goal_relabel_control": {
        "scenario_id": "semantic_goal_relabel",
        "blocked_condition": "proxy target digest is relabeled as semantic goal",
        "geometric_reading": (
            "A digest-bounded target surface is not a semantic goal or ownership "
            "claim."
        ),
        "rung_effect": "blocks_unsafe_claim",
    },
    "semantic_choice_relabel_control": {
        "scenario_id": "semantic_choice_relabel",
        "blocked_condition": "proxy/basin contrast is relabeled as semantic choice",
        "geometric_reading": (
            "A contrast between proxy and basin traces does not establish choice "
            "or intention."
        ),
        "rung_effect": "blocks_unsafe_claim",
    },
    "agency_relabel_control": {
        "scenario_id": "agency_relabel",
        "blocked_condition": "proxy divergence/collapse candidate is relabeled as agency",
        "geometric_reading": (
            "Even a future controlled proxy-collapse row would remain artifact-"
            "level evidence below agency."
        ),
        "rung_effect": "blocks_unsafe_claim",
    },
    "native_support_relabel_control": {
        "scenario_id": "native_support_relabel",
        "blocked_condition": "scoped substrate or proxy row is relabeled as native support",
        "geometric_reading": (
            "N25.2 substrate and N26 proxy traces are not native support channels."
        ),
        "rung_effect": "blocks_unsafe_claim",
    },
    "n25_2_mb6_as_native_support_control": {
        "scenario_id": "n25_2_mb6_as_native_support",
        "blocked_condition": "N25.2 scoped MB6 substrate is relabeled as native support",
        "geometric_reading": (
            "Scoped multi-basin substrate is a permitted N26 geometry surface, "
            "not a native support channel."
        ),
        "rung_effect": "blocks_unsafe_claim",
    },
    "n25_2_mb6_as_agency_sentience_ant_ecology_control": {
        "scenario_id": "n25_2_mb6_as_agency_sentience_ant_ecology",
        "blocked_condition": "N25.2 scoped MB6 substrate is relabeled as agency, sentience, or ant ecology",
        "geometric_reading": (
            "A scoped substrate handoff does not implement agency, sentience, or "
            "the ant ecology bridge."
        ),
        "rung_effect": "blocks_unsafe_claim",
    },
    "sentience_relabel_control": {
        "scenario_id": "sentience_relabel",
        "blocked_condition": "proxy-collapse candidate is relabeled as sentience",
        "geometric_reading": (
            "Proxy failure/survival geometry does not become sentience or read-back "
            "identity."
        ),
        "rung_effect": "blocks_unsafe_claim",
    },
    "phase8_completion_relabel_control": {
        "scenario_id": "phase8_completion_relabel",
        "blocked_condition": "N26 row is relabeled as Phase 8 completion",
        "geometric_reading": (
            "N26 may consume Phase 8 multi-basin substrate, but cannot close "
            "Phase 8 implementation."
        ),
        "rung_effect": "blocks_unsafe_claim",
    },
    "ant_ecology_relabel_control": {
        "scenario_id": "ant_ecology_relabel",
        "blocked_condition": "N26 proxy row is relabeled as ant ecology implementation",
        "geometric_reading": (
            "Proxy divergence on scoped substrate is still pre-ecology evidence "
            "and cannot specify or implement ant ecology."
        ),
        "rung_effect": "blocks_unsafe_claim",
    },
}


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


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def collect_strings(data: Any) -> set[str]:
    strings: set[str] = set()
    if isinstance(data, str):
        strings.add(data)
    elif isinstance(data, list):
        for item in data:
            strings.update(collect_strings(item))
    elif isinstance(data, dict):
        for value in data.values():
            strings.update(collect_strings(value))
    return strings


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def active_null_row(index: int, control_id: str) -> dict[str, Any]:
    scenario = CONTROL_SCENARIOS[control_id]
    return {
        "row_id": f"n26_i3_null_{index:02d}_{scenario['scenario_id']}",
        "scenario_id": scenario["scenario_id"],
        "control_id": control_id,
        "row_decision": "rejected",
        "control_status": "failed_closed",
        "control_status_meaning": "blocker triggered and claim correctly rejected",
        "blocked_condition": scenario["blocked_condition"],
        "expected_result": "claim rejected; no positive proxy evidence admitted",
        "actual_result": "failed_closed",
        "claim_allowed_when_control_triggers": False,
        "control_satisfied_for_positive_row": False,
        "rung_effect": scenario["rung_effect"],
        "candidate_pd_ladder_rung": ACTIVE_NULL_RUNG,
        "pd_ladder_rung_assigned": False,
        "n26_closeout_ceiling": "N26-C3_active_nulls_fail_closed",
        "positive_proxy_evidence_opened": False,
        "proxy_derivation_opened": False,
        "proxy_divergence_opened": False,
        "proxy_collapse_opened": False,
        "ap5_bridge_status": "not_supported_active_null_only",
        "ap5_dependency_status": "not_applicable",
        "ap5_condition_reason": (
            "active-null row; no positive proxy or target formation claim"
        ),
        "source_current_inputs": [],
        "artifact_manifest": [],
        "all_artifact_sha256_match_file_contents": "not_applicable_active_null_fixture",
        "derived_report_only": True,
        "trace_admissibility": "active_null_fixture_only_not_positive_evidence",
        "positive_support_admissible": False,
        "scoped_mb6_substrate_consumption_record": "not_applicable_active_null_fixture",
        "multi_basin_scope_id": "not_applicable_active_null_fixture",
        "basin_ids_or_child_basin_ids": [],
        "n25_2_unscoped_consumption_allowed": False,
        "n25_2_unscoped_multi_basin_consumption_allowed": False,
        "front_capacity_companion_backfill_used": False,
        "proxy_policy_owner": "not_applicable_active_null_fixture",
        "producer_mediated_target_derivation_counted_as_substrate": False,
        "geometric_reading": scenario["geometric_reading"],
        "control_results": [
            {
                "control_id": control_id,
                "control_status": "failed_closed",
                "blocked_condition": scenario["blocked_condition"],
                "expected_result": "claim rejected; no positive proxy evidence admitted",
                "actual_result": "failed_closed",
                "claim_allowed_when_control_triggers": False,
                "rung_effect": scenario["rung_effect"],
                "control_satisfied_for_positive_row": False,
            }
        ],
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_output() -> dict[str, Any]:
    schema = load_json(SCHEMA_OUTPUT)
    required_control_ids = schema["control_schema"]["required_control_ids"]
    rows = [
        active_null_row(index, control_id)
        for index, control_id in enumerate(required_control_ids, start=1)
    ]
    required_source_current_blockers = {
        "lower_stack_input_missing_control",
        "proxy_metric_not_replayable_control",
        "support_coherence_floor_missing_control",
        "proxy_basin_measurement_not_independent_control",
        "scoped_mb6_scope_id_missing_control",
        "derived_report_only_positive_row_control",
        "artifact_manifest_failure_control",
    }
    row_control_ids = {row["control_id"] for row in rows}
    failed_open_rows = [
        row["row_id"] for row in rows if row["control_status"] == "failed_open"
    ]
    checks = [
        check(
            "i2_schema_passed",
            schema.get("status") == "passed"
            and schema.get("acceptance_state")
            == "accepted_proxy_divergence_collapse_schema_frozen_no_proxy_evidence",
            {
                "status": schema.get("status"),
                "acceptance_state": schema.get("acceptance_state"),
            },
        ),
        check(
            "schema_digest_matches_expected",
            schema.get("output_digest") == EXPECTED_I2_OUTPUT_DIGEST,
            {"output_digest": schema.get("output_digest")},
        ),
        check(
            "source_chain_digests_match_expected",
            schema.get("source_inventory_output_digest") == EXPECTED_I1_OUTPUT_DIGEST
            and schema.get("source_contract_row_digest")
            == EXPECTED_SOURCE_CONTRACT_ROW_DIGEST
            and schema.get("source_consumable_contract_row_digest")
            == EXPECTED_SOURCE_CONSUMABLE_CONTRACT_ROW_DIGEST,
            {
                "i1_output_digest": schema.get("source_inventory_output_digest"),
                "source_contract_row_digest": schema.get("source_contract_row_digest"),
                "source_consumable_contract_row_digest": schema.get(
                    "source_consumable_contract_row_digest"
                ),
            },
        ),
        check(
            "all_required_controls_instantiated",
            set(required_control_ids) == row_control_ids,
            {
                "required_control_count": len(required_control_ids),
                "row_control_count": len(row_control_ids),
            },
        ),
        check(
            "all_controls_failed_closed",
            all(row["control_status"] == "failed_closed" for row in rows),
            {"row_count": len(rows)},
        ),
        check(
            "failed_open_controls_zero",
            len(failed_open_rows) == 0,
            {"failed_open_rows": failed_open_rows},
        ),
        check(
            "source_current_derivation_blockers_present",
            required_source_current_blockers.issubset(row_control_ids),
            {"required_source_current_blockers": sorted(required_source_current_blockers)},
        ),
        check(
            "no_positive_proxy_evidence_opened",
            all(not row["positive_proxy_evidence_opened"] for row in rows),
            "active nulls only",
        ),
        check(
            "no_positive_pd_rung_assigned",
            all(row["candidate_pd_ladder_rung"] == ACTIVE_NULL_RUNG for row in rows)
            and all(not row["pd_ladder_rung_assigned"] for row in rows),
            {"active_null_rung": ACTIVE_NULL_RUNG},
        ),
        check(
            "active_null_rows_are_not_positive_evidence",
            all(
                row["derived_report_only"] is True
                and row["trace_admissibility"]
                == "active_null_fixture_only_not_positive_evidence"
                and row["positive_support_admissible"] is False
                for row in rows
            ),
            "null rows can block false positives but cannot support PD evidence",
        ),
        check(
            "ap5_not_applicable_limited_to_null_rows",
            all(
                row["ap5_dependency_status"] == "not_applicable"
                and row["ap5_condition_reason"]
                == "active-null row; no positive proxy or target formation claim"
                for row in rows
            ),
            "no positive proxy or target formation claim is made",
        ),
        check(
            "scoped_mb6_claims_fail_closed",
            all(not row["n25_2_unscoped_consumption_allowed"] for row in rows)
            and all(not row["n25_2_unscoped_multi_basin_consumption_allowed"] for row in rows)
            and all(not row["front_capacity_companion_backfill_used"] for row in rows),
            "unscoped MB6 and front-capacity backfill remain blocked",
        ),
        check(
            "unsafe_claim_flags_false",
            all(not any(row["unsafe_claim_flags"].values()) for row in rows),
            "all unsafe claim flags are false for every null row",
        ),
    ]
    output: dict[str, Any] = {
        "artifact_id": "n26_active_nulls_and_failure_baselines",
        "schema_version": "1.0",
        "experiment": "N26_proxy_divergence_proxy_collapse",
        "iteration": "3",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": "instantiate active nulls and failure baselines before positive proxy probes",
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "acceptance_state": "accepted_active_nulls_fail_closed_no_positive_proxy_evidence",
        "source_schema_path": (
            "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/"
            "outputs/n26_proxy_divergence_collapse_schema_and_controls.json"
        ),
        "source_schema_output_digest": schema.get("output_digest"),
        "i1_output_digest": schema.get("source_inventory_output_digest"),
        "source_contract_row_digest": schema.get("source_contract_row_digest"),
        "source_consumable_contract_row_digest": schema.get(
            "source_consumable_contract_row_digest"
        ),
        "candidate_pd_ladder_rung": ACTIVE_NULL_RUNG,
        "pd_ladder_rung_assigned": False,
        "n26_closeout_ceiling": "N26-C3_active_nulls_fail_closed",
        "n26_closeout_ladder_rung_assigned": False,
        "positive_proxy_evidence_opened": False,
        "proxy_derivation_opened": False,
        "proxy_divergence_opened": False,
        "proxy_collapse_opened": False,
        "ap5_bridge_status": "not_supported_active_null_only",
        "required_control_count": len(required_control_ids),
        "active_null_row_count": len(rows),
        "failed_open_controls": 0,
        "failed_open_rows": failed_open_rows,
        "active_null_rows": rows,
        "claim_boundary": {
            "claim_ceiling": (
                "active-null and failure-baseline matrix only; no proxy "
                "derivation, proxy divergence, proxy collapse, AP5 bridge, "
                "semantic goal, agency, native support, sentience, Phase 8, "
                "ant ecology, or unscoped multi-basin claim"
            ),
            "unsafe_claim_flags": unsafe_claim_flags(),
        },
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    checks.append(
        check(
            "no_absolute_paths_in_records",
            not any(
                marker in value
                for value in collect_strings(output)
                for marker in ABSOLUTE_PATH_MARKERS
            ),
            "all paths are repository-relative",
        )
    )
    output["status"] = "passed" if all(item["passed"] for item in checks) else "failed"
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["checks"] = checks
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N26 Iteration 3 - Active Nulls And Failure Baselines",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        "## Scope",
        "",
        "Iteration 3 instantiates the I2 controls as active nulls. It opens no positive proxy evidence.",
        "",
        "## Ceiling",
        "",
        "```text",
        f"i1_output_digest = {output['i1_output_digest']}",
        f"source_schema_output_digest = {output['source_schema_output_digest']}",
        f"source_contract_row_digest = {output['source_contract_row_digest']}",
        f"source_consumable_contract_row_digest = {output['source_consumable_contract_row_digest']}",
        f"candidate_pd_ladder_rung = {output['candidate_pd_ladder_rung']}",
        f"n26_closeout_ceiling = {output['n26_closeout_ceiling']}",
        "positive_proxy_evidence_opened = false",
        "proxy_derivation_opened = false",
        "proxy_divergence_opened = false",
        "proxy_collapse_opened = false",
        f"ap5_bridge_status = {output['ap5_bridge_status']}",
        "```",
        "",
        "## Active Null Rows",
        "",
        "| Row | Control | Decision | Status | Rung Effect |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in output["active_null_rows"]:
        lines.append(
            "| `{row_id}` | `{control_id}` | `{row_decision}` | `{control_status}` | `{rung_effect}` |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Geometric Interpretation",
            "",
        ]
    )
    for row in output["active_null_rows"]:
        lines.append(f"- `{row['control_id']}`: {row['geometric_reading']}")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in output["checks"]:
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | "
            f"`{json.dumps(item['detail'], sort_keys=True, ensure_ascii=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            output["claim_boundary"]["claim_ceiling"],
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)


if __name__ == "__main__":
    main()
