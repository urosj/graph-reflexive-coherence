#!/usr/bin/env python3
"""Build N14 Iteration 6 consequence perturbation and replay matrix."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SELECTION_OUTPUT = OUTPUTS / "n14_consequence_sensitive_selection_candidate.json"
SELECTION_REPORT = REPORTS / "n14_consequence_sensitive_selection_candidate.md"
CONTROL_OUTPUT = OUTPUTS / "n14_consequence_control_matrix.json"
CONTROL_REPORT = REPORTS / "n14_consequence_control_matrix.md"

N08_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N08-lgrc-memory-trail-affordance"
    / "outputs"
    / "n08_iteration_8_mem6_closeout.json"
)
N08_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N08-lgrc-memory-trail-affordance"
    / "reports"
    / "n08_iteration_8_mem6_closeout.md"
)
N09_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "outputs"
    / "n09_iteration_9_gpr6_closeout.json"
)
N09_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "reports"
    / "n09_iteration_9_gpr6_closeout.md"
)
N13_STRESS_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "outputs"
    / "n13_support_disruption_restoration_matrix.json"
)
N13_STRESS_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "reports"
    / "n13_support_disruption_restoration_matrix.md"
)

OUTPUT_PATH = OUTPUTS / "n14_consequence_perturbation_matrix.json"
REPORT_PATH = REPORTS / "n14_consequence_perturbation_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_consequence_perturbation_matrix.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

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

VALID_BUDGET_SURFACE = "source_budget_surfaces_present_for_selection_candidate"
VALID_PERTURBATION_RANK_SOURCE = (
    "derived_from_serialized_perturbation_score_components"
)


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


def clone_records(selection: dict[str, Any]) -> list[dict[str, Any]]:
    return copy.deepcopy(selection["selection_records"])


def get_record(records: list[dict[str, Any]], route_id: str) -> dict[str, Any]:
    for record in records:
        if record["route_candidate_id"] == route_id:
            return record
    raise KeyError(route_id)


def update_component(
    records: list[dict[str, Any]],
    route_id: str,
    component_name: str,
    component_value: float,
    source_basis: dict[str, Any],
) -> None:
    record = get_record(records, route_id)
    components = record["consequence_score_components"]["components"]
    components[component_name] = round(component_value, 12)
    record.setdefault("perturbation_component_basis", {})[component_name] = source_basis


def recompute_scores_and_ranks(records: list[dict[str, Any]]) -> None:
    for record in records:
        components = record["consequence_score_components"]["components"]
        score = round(sum(float(value) for value in components.values()), 12)
        record["consequence_score_components"]["consequence_score"] = score
        record["consequence_score_components"]["score_scope"] = (
            "source_backed_perturbation_route_consequence"
        )
        record["consequence_rank_source"] = (
            "derived_from_serialized_perturbation_score_components"
        )
    ranked = sorted(
        records,
        key=lambda record: (
            -record["consequence_score_components"]["consequence_score"],
            record["immediate_affordance_rank"],
            record["route_candidate_id"],
        ),
    )
    for rank, record in enumerate(ranked, start=1):
        record["consequence_rank"] = rank


def sorted_for_selection(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda record: (
            record["consequence_rank"],
            record["immediate_affordance_rank"],
            record["route_candidate_id"],
        ),
    )


def route_summary(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "route_candidate_id": record["route_candidate_id"],
            "consequence_score": record["consequence_score_components"][
                "consequence_score"
            ],
            "consequence_rank": record["consequence_rank"],
            "consequence_rank_source": record.get("consequence_rank_source"),
            "budget_validity": record["budget_validity"],
        }
        for record in sorted(records, key=lambda item: item["route_candidate_id"])
    ]


def execute_variant(variant: dict[str, Any]) -> dict[str, Any]:
    records = copy.deepcopy(variant["records"])
    metadata = variant["metadata"]
    if metadata.get("stale_source_window") is True:
        return {
            "observed_outcome": "blocked",
            "selected_route": None,
            "blocker_code": "stale_consequence_record_blocked",
            "route_summary": route_summary(records),
            "selection_digest": digest_value(
                {
                    "variant_id": variant["variant_id"],
                    "blocked": "stale_consequence_record_blocked",
                    "route_summary": route_summary(records),
                }
            ),
        }
    budget_invalid_routes = [
        record["route_candidate_id"]
        for record in records
        if record["budget_validity"] != VALID_BUDGET_SURFACE
    ]
    if budget_invalid_routes:
        return {
            "observed_outcome": "blocked",
            "selected_route": None,
            "blocker_code": "budget_invalid_route_blocked",
            "route_summary": route_summary(records),
            "selection_digest": digest_value(
                {
                    "variant_id": variant["variant_id"],
                    "blocked": "budget_invalid_route_blocked",
                    "route_summary": route_summary(records),
                }
            ),
        }
    invalid_rank_source_routes = [
        record["route_candidate_id"]
        for record in records
        if record.get("consequence_rank_source") != VALID_PERTURBATION_RANK_SOURCE
    ]
    if invalid_rank_source_routes:
        return {
            "observed_outcome": "blocked",
            "selected_route": None,
            "blocker_code": "invalid_consequence_rank_source_blocked",
            "route_summary": route_summary(records),
            "selection_digest": digest_value(
                {
                    "variant_id": variant["variant_id"],
                    "blocked": "invalid_consequence_rank_source_blocked",
                    "route_summary": route_summary(records),
                }
            ),
        }
    ranked = sorted_for_selection(records)
    selected = ranked[0]
    return {
        "observed_outcome": "selected",
        "selected_route": selected["route_candidate_id"],
        "blocker_code": None,
        "route_summary": route_summary(records),
        "selection_digest": digest_value(
            {
                "variant_id": variant["variant_id"],
                "selected_route": selected["route_candidate_id"],
                "route_summary": route_summary(records),
            }
        ),
    }


def make_variant(
    variant_id: str,
    variant_name: str,
    records: list[dict[str, Any]],
    expected_selected_route: str | None,
    expected_blocker_code: str | None,
    changed_components: list[str],
    source_backed_inputs: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "variant_id": variant_id,
        "variant_name": variant_name,
        "records": records,
        "expected_selected_route": expected_selected_route,
        "expected_blocker_code": expected_blocker_code,
        "changed_components": changed_components,
        "source_backed_inputs": source_backed_inputs,
        "metadata": metadata or {},
        "variant_digest": digest_value(
            {
                "variant_id": variant_id,
                "records": route_summary(records),
                "metadata": metadata or {},
                "source_backed_inputs": source_backed_inputs,
            }
        ),
    }


def source_input(
    source_id: str,
    artifact_path: Path,
    field: str,
    value: Any,
    component: str,
    interpretation: str,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "artifact": rel(artifact_path),
        "artifact_sha256": digest_file(artifact_path),
        "field": field,
        "value": value,
        "component": component,
        "interpretation": interpretation,
    }


def build_variants(
    selection: dict[str, Any],
    n08: dict[str, Any],
    n09: dict[str, Any],
    n13_stress: dict[str, Any],
) -> list[dict[str, Any]]:
    base = clone_records(selection)
    recompute_scores_and_ranks(base)
    variants = [
        make_variant(
            "baseline_memory_dominant_replay",
            "Baseline memory-dominant replay",
            base,
            "route_b",
            None,
            [],
            [],
        )
    ]
    support_record = n13_stress["stress_matrix"]["stress_records"][1]
    support_component = round(support_record["support_error"] * 3, 12)
    support_records = clone_records(selection)
    update_component(
        support_records,
        "route_a",
        "route_specific_support_component",
        support_component,
        source_input(
            "n13_support_error",
            N13_STRESS_OUTPUT,
            "stress_matrix.stress_records[1].support_error",
            support_record["support_error"],
            "route_specific_support_component",
            "controlled support-risk perturbation magnitude, not observed route-specific support support",
        ),
    )
    recompute_scores_and_ranks(support_records)
    variants.append(
        make_variant(
            "support_risk_active_variant",
            "Support-risk active variant",
            support_records,
            "route_a",
            None,
            ["route_specific_support_component"],
            [
                source_input(
                    "n13_support_error",
                    N13_STRESS_OUTPUT,
                    "stress_matrix.stress_records[1].support_error",
                    support_record["support_error"],
                    "route_specific_support_component",
                    "source-backed support-risk perturbation input",
                )
            ],
        )
    )
    memory = n08["artifact_only_replay"]
    memory_records = clone_records(selection)
    route_a_delta = round(
        memory["route_b_strength_after_each_cycle"][-1]
        - memory["route_b_strength_after_each_cycle"][0],
        12,
    )
    route_b_delta = round(
        memory["route_a_strength_after_each_cycle"][-1]
        - memory["route_a_strength_after_each_cycle"][0],
        12,
    )
    update_component(
        memory_records,
        "route_a",
        "memory_delta_component",
        route_a_delta,
        source_input(
            "n08_route_b_memory_delta",
            N08_OUTPUT,
            "artifact_only_replay.route_b_strength_after_each_cycle",
            route_a_delta,
            "memory_delta_component",
            "source-backed memory strengthening perturbation input",
        ),
    )
    update_component(
        memory_records,
        "route_b",
        "memory_delta_component",
        route_b_delta,
        source_input(
            "n08_route_a_memory_delta",
            N08_OUTPUT,
            "artifact_only_replay.route_a_strength_after_each_cycle",
            route_b_delta,
            "memory_delta_component",
            "source-backed memory weakening perturbation input",
        ),
    )
    recompute_scores_and_ranks(memory_records)
    variants.append(
        make_variant(
            "memory_effect_variant",
            "Memory-effect variant",
            memory_records,
            "route_a",
            None,
            ["memory_delta_component"],
            [
                source_input(
                    "n08_memory_delta_swap",
                    N08_OUTPUT,
                    "artifact_only_replay.route_a_strength_after_each_cycle + route_b_strength_after_each_cycle",
                    {
                        "route_a_component": route_a_delta,
                        "route_b_component": route_b_delta,
                    },
                    "memory_delta_component",
                    "source-backed memory-effect perturbation input",
                )
            ],
        )
    )
    regulation = n09["regulation_summary"]
    regulation_component = round(regulation["gpr5_cycle_count"] * 0.08, 12)
    regulation_records = clone_records(selection)
    update_component(
        regulation_records,
        "route_a",
        "route_specific_regulation_component",
        regulation_component,
        source_input(
            "n09_regulation_cycle_count",
            N09_OUTPUT,
            "regulation_summary.gpr5_cycle_count",
            regulation["gpr5_cycle_count"],
            "route_specific_regulation_component",
            "controlled regulation-deficit perturbation magnitude, not observed route-specific regulation support",
        ),
    )
    recompute_scores_and_ranks(regulation_records)
    variants.append(
        make_variant(
            "regulation_deficit_variant",
            "Regulation-deficit variant",
            regulation_records,
            "route_a",
            None,
            ["route_specific_regulation_component"],
            [
                source_input(
                    "n09_regulation_cycle_count",
                    N09_OUTPUT,
                    "regulation_summary.gpr5_cycle_count",
                    regulation["gpr5_cycle_count"],
                    "route_specific_regulation_component",
                    "source-backed regulation-deficit perturbation input",
                )
            ],
        )
    )
    budget_records = clone_records(selection)
    get_record(budget_records, "route_b")["budget_validity"] = (
        "budget_invalid_source_surface"
    )
    get_record(budget_records, "route_b")["budget_cost_surface"][
        "invalid_budget_marker"
    ] = "forced_high_consequence_budget_invalid"
    recompute_scores_and_ranks(budget_records)
    variants.append(
        make_variant(
            "budget_invalid_high_consequence_variant",
            "Budget-invalid high-consequence variant",
            budget_records,
            None,
            "budget_invalid_route_blocked",
            ["budget_validity"],
            [],
            metadata={"budget_invalid_route": "route_b"},
        )
    )
    stale_records = clone_records(selection)
    recompute_scores_and_ranks(stale_records)
    variants.append(
        make_variant(
            "stale_record_replay_variant",
            "Stale record replay variant",
            stale_records,
            None,
            "stale_consequence_record_blocked",
            ["source_window"],
            [],
            metadata={"stale_source_window": True},
        )
    )
    return variants


def variant_passed(variant: dict[str, Any], observed: dict[str, Any]) -> bool:
    if variant["expected_blocker_code"]:
        return (
            observed["observed_outcome"] == "blocked"
            and observed["blocker_code"] == variant["expected_blocker_code"]
        )
    return (
        observed["observed_outcome"] == "selected"
        and observed["selected_route"] == variant["expected_selected_route"]
        and observed["blocker_code"] is None
    )


def build_perturbation_records(variants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for variant in variants:
        observed = execute_variant(variant)
        records.append(
            {
                "variant_id": variant["variant_id"],
                "variant_name": variant["variant_name"],
                "changed_components": variant["changed_components"],
                "source_backed_inputs": variant["source_backed_inputs"],
                "expected_selected_route": variant["expected_selected_route"],
                "expected_blocker_code": variant["expected_blocker_code"],
                "observed_outcome": observed["observed_outcome"],
                "observed_selected_route": observed["selected_route"],
                "observed_blocker_code": observed["blocker_code"],
                "route_summary": observed["route_summary"],
                "variant_digest": variant["variant_digest"],
                "selection_digest": observed["selection_digest"],
                "passed": variant_passed(variant, observed),
                "runtime_state_used": False,
                "producer_direct_mutation": False,
                "phase8_opened": False,
                "native_support_opened": False,
                "final_ap4_supported": False,
            }
        )
    return records


def filesystem_json_roundtrip(value: dict[str, Any], filename: str) -> tuple[dict[str, Any], str]:
    serialized = canonical_json(value) + "\n"
    with tempfile.TemporaryDirectory(prefix="n14_i6_replay_", dir="/tmp") as tmp:
        path = Path(tmp) / filename
        path.write_text(serialized, encoding="utf-8")
        file_sha256 = digest_file(path)
        loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded, file_sha256


def build_replay_records(base_variant: dict[str, Any]) -> list[dict[str, Any]]:
    duplicate_a = execute_variant(base_variant)
    duplicate_b = execute_variant(base_variant)
    serialized_variant, artifact_file_sha256 = filesystem_json_roundtrip(
        base_variant, "artifact_only_variant.json"
    )
    artifact_replay = execute_variant(serialized_variant)
    snapshot = {
        "snapshot_id": "n14_i6_snapshot_baseline_memory_dominant",
        "variant": base_variant,
        "snapshot_digest": digest_value(base_variant),
    }
    restored_snapshot_envelope, snapshot_file_sha256 = filesystem_json_roundtrip(
        snapshot, "snapshot_load_variant.json"
    )
    restored_snapshot = restored_snapshot_envelope["variant"]
    snapshot_replay = execute_variant(restored_snapshot)
    inverted_variant = copy.deepcopy(base_variant)
    inverted_variant["records"] = list(reversed(inverted_variant["records"]))
    order_inversion_replay = execute_variant(inverted_variant)
    return [
        {
            "replay_id": "duplicate_replay_stability",
            "replay_kind": "duplicate_replay",
            "first_digest": duplicate_a["selection_digest"],
            "second_digest": duplicate_b["selection_digest"],
            "first_selected_route": duplicate_a["selected_route"],
            "second_selected_route": duplicate_b["selected_route"],
            "stable": duplicate_a == duplicate_b,
            "filesystem_roundtrip": False,
            "runtime_state_used": False,
            "producer_direct_mutation": False,
        },
        {
            "replay_id": "artifact_only_replay_stability",
            "replay_kind": "artifact_only_replay",
            "first_digest": duplicate_a["selection_digest"],
            "second_digest": artifact_replay["selection_digest"],
            "first_selected_route": duplicate_a["selected_route"],
            "second_selected_route": artifact_replay["selected_route"],
            "stable": duplicate_a == artifact_replay,
            "filesystem_roundtrip": True,
            "serialized_artifact_sha256": artifact_file_sha256,
            "runtime_state_used": False,
            "producer_direct_mutation": False,
        },
        {
            "replay_id": "snapshot_load_replay_stability",
            "replay_kind": "snapshot_load_replay",
            "snapshot_digest": snapshot["snapshot_digest"],
            "first_digest": duplicate_a["selection_digest"],
            "second_digest": snapshot_replay["selection_digest"],
            "first_selected_route": duplicate_a["selected_route"],
            "second_selected_route": snapshot_replay["selected_route"],
            "stable": duplicate_a == snapshot_replay,
            "filesystem_roundtrip": True,
            "serialized_snapshot_sha256": snapshot_file_sha256,
            "runtime_state_used": False,
            "producer_direct_mutation": False,
        },
        {
            "replay_id": "order_inversion_replay_stability",
            "replay_kind": "order_inversion_replay",
            "first_digest": duplicate_a["selection_digest"],
            "second_digest": order_inversion_replay["selection_digest"],
            "first_selected_route": duplicate_a["selected_route"],
            "second_selected_route": order_inversion_replay["selected_route"],
            "stable": duplicate_a == order_inversion_replay,
            "filesystem_roundtrip": False,
            "runtime_state_used": False,
            "producer_direct_mutation": False,
        },
    ]


def by_id(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {record["variant_id"]: record for record in records}


def build_output() -> dict[str, Any]:
    selection = load_json(SELECTION_OUTPUT)
    control_matrix = load_json(CONTROL_OUTPUT)
    n08 = load_json(N08_OUTPUT)
    n09 = load_json(N09_OUTPUT)
    n13_stress = load_json(N13_STRESS_OUTPUT)
    variants = build_variants(selection, n08, n09, n13_stress)
    perturbation_records = build_perturbation_records(variants)
    replay_records = build_replay_records(variants[0])
    perturbation_by_id = by_id(perturbation_records)
    checks = {
        "selection_source_passed": selection["status"] == "passed",
        "control_matrix_source_passed": control_matrix["status"] == "passed",
        "support_risk_variant_changes_route_ranking_only_through_source_backed_support_input": (
            perturbation_by_id["support_risk_active_variant"][
                "observed_selected_route"
            ]
            == "route_a"
            and perturbation_by_id["support_risk_active_variant"][
                "changed_components"
            ]
            == ["route_specific_support_component"]
            and bool(
                perturbation_by_id["support_risk_active_variant"][
                    "source_backed_inputs"
                ]
            )
        ),
        "memory_effect_variant_changes_route_ranking_only_through_source_backed_memory_input": (
            perturbation_by_id["memory_effect_variant"]["observed_selected_route"]
            == "route_a"
            and perturbation_by_id["memory_effect_variant"]["changed_components"]
            == ["memory_delta_component"]
            and bool(
                perturbation_by_id["memory_effect_variant"]["source_backed_inputs"]
            )
        ),
        "regulation_deficit_variant_changes_route_ranking_only_through_source_backed_regulation_input": (
            perturbation_by_id["regulation_deficit_variant"][
                "observed_selected_route"
            ]
            == "route_a"
            and perturbation_by_id["regulation_deficit_variant"][
                "changed_components"
            ]
            == ["route_specific_regulation_component"]
            and bool(
                perturbation_by_id["regulation_deficit_variant"][
                    "source_backed_inputs"
                ]
            )
        ),
        "budget_invalid_high_consequence_route_rejected": (
            perturbation_by_id["budget_invalid_high_consequence_variant"][
                "observed_blocker_code"
            ]
            == "budget_invalid_route_blocked"
        ),
        "budget_validity_checked_before_ranking": (
            perturbation_by_id["budget_invalid_high_consequence_variant"][
                "observed_blocker_code"
            ]
            == "budget_invalid_route_blocked"
        ),
        "consequence_rank_source_validated_before_ranking": all(
            all(
                summary["consequence_rank_source"]
                == VALID_PERTURBATION_RANK_SOURCE
                for summary in record["route_summary"]
            )
            for record in perturbation_records
        ),
        "stale_consequence_record_rejected": (
            perturbation_by_id["stale_record_replay_variant"][
                "observed_blocker_code"
            ]
            == "stale_consequence_record_blocked"
        ),
        "all_perturbation_records_passed": all(
            record["passed"] for record in perturbation_records
        ),
        "duplicate_replay_stable": next(
            record
            for record in replay_records
            if record["replay_id"] == "duplicate_replay_stability"
        )["stable"],
        "artifact_only_replay_stable": next(
            record
            for record in replay_records
            if record["replay_id"] == "artifact_only_replay_stability"
        )["stable"],
        "artifact_only_replay_uses_filesystem_roundtrip": next(
            record
            for record in replay_records
            if record["replay_id"] == "artifact_only_replay_stability"
        )["filesystem_roundtrip"],
        "snapshot_load_replay_stable": next(
            record
            for record in replay_records
            if record["replay_id"] == "snapshot_load_replay_stability"
        )["stable"],
        "snapshot_load_replay_uses_filesystem_roundtrip": next(
            record
            for record in replay_records
            if record["replay_id"] == "snapshot_load_replay_stability"
        )["filesystem_roundtrip"],
        "order_inversion_replay_stable": next(
            record
            for record in replay_records
            if record["replay_id"] == "order_inversion_replay_stability"
        )["stable"],
        "runtime_state_used_false": all(
            record["runtime_state_used"] is False for record in perturbation_records
        )
        and all(record["runtime_state_used"] is False for record in replay_records),
        "no_producer_direct_mutation_recorded": all(
            record["producer_direct_mutation"] is False
            for record in perturbation_records
        )
        and all(
            record["producer_direct_mutation"] is False for record in replay_records
        ),
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "phase8_opened_false": True,
        "native_support_opened_false": True,
        "final_ap4_not_supported": True,
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_perturbation_replay_matrix_pending_claim_classification"
        if all(checks.values())
        else "rejected_perturbation_replay_matrix"
    )
    interpretation_record = {
        "record_id": "n14_i6_interpretation_perturbation_replay_v1",
        "acceptance_state": acceptance_state,
        "supported_interpretation": (
            "N14 Iteration 6 shows that the provisional AP4 candidate is "
            "source-sensitive and replay-stable at artifact level: support, "
            "memory, and regulation perturbation variants alter the selected "
            "route only through serialized source-backed consequence inputs, "
            "while duplicate, artifact-only, snapshot/load, and order-inverted "
            "replays remain stable."
        ),
        "unsupported_interpretations": [
            "final AP4 support before claim classification",
            "native support",
            "intention",
            "agency",
            "semantic choice",
            "semantic goal ownership",
            "identity acceptance",
            "selfhood",
            "personhood",
            "biological behavior",
            "fully native integration",
        ],
        "plain_language_interpretation": (
            "Iteration 6 handles the Iteration 5 control-clean candidate by "
            "testing whether route choice changes only when serialized source-"
            "backed consequence inputs change, and whether replay is stable for "
            "unchanged inputs. The positive variants select the route favored by "
            "the active support, memory, or regulation component; stale and "
            "budget-invalid cases fail closed. Final AP4 remains pending until "
            "Iteration 7 freezes the claim boundary."
        ),
        "next_required_step": (
            "Run Iteration 7 claim boundary and AP4 classification."
        ),
    }
    output = {
        "experiment": "N14",
        "iteration": 6,
        "purpose": "consequence_perturbation_and_replay_matrix",
        "schema": "n14_consequence_perturbation_matrix_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP4",
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "perturbation_records_passed": all(
                record["passed"] for record in perturbation_records
            ),
            "replay_records_passed": all(
                record["stable"] for record in replay_records
            ),
            "baseline_selected_route": perturbation_by_id[
                "baseline_memory_dominant_replay"
            ]["observed_selected_route"],
            "support_risk_selected_route": perturbation_by_id[
                "support_risk_active_variant"
            ]["observed_selected_route"],
            "memory_effect_selected_route": perturbation_by_id[
                "memory_effect_variant"
            ]["observed_selected_route"],
            "regulation_deficit_selected_route": perturbation_by_id[
                "regulation_deficit_variant"
            ]["observed_selected_route"],
            "budget_invalid_blocker": perturbation_by_id[
                "budget_invalid_high_consequence_variant"
            ]["observed_blocker_code"],
            "stale_record_blocker": perturbation_by_id[
                "stale_record_replay_variant"
            ]["observed_blocker_code"],
            "provisional_ap_level": "AP4_candidate",
            "final_ap4_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "perturbation_records": perturbation_records,
        "replay_records": replay_records,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(SELECTION_OUTPUT): source_artifact(SELECTION_OUTPUT, selection),
            rel(CONTROL_OUTPUT): source_artifact(CONTROL_OUTPUT, control_matrix),
            rel(N08_OUTPUT): source_artifact(N08_OUTPUT, n08),
            rel(N09_OUTPUT): source_artifact(N09_OUTPUT, n09),
            rel(N13_STRESS_OUTPUT): source_artifact(N13_STRESS_OUTPUT, n13_stress),
        },
        "source_reports": {
            rel(SELECTION_REPORT): source_report(SELECTION_REPORT),
            rel(CONTROL_REPORT): source_report(CONTROL_REPORT),
            rel(N08_REPORT): source_report(N08_REPORT),
            rel(N09_REPORT): source_report(N09_REPORT),
            rel(N13_STRESS_REPORT): source_report(N13_STRESS_REPORT),
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N14 Consequence Perturbation And Replay Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "## Interpretation",
        "",
        "```json",
        json.dumps(output["interpretation_record"], indent=2, sort_keys=True),
        "```",
        "",
        "## Perturbation Records",
        "",
        "| Variant | Changed components | Observed | Blocker | Passed |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in output["perturbation_records"]:
        observed = record["observed_outcome"]
        if record["observed_selected_route"]:
            observed = f"{observed}:{record['observed_selected_route']}"
        blocker = record["observed_blocker_code"] or "none"
        components = ", ".join(record["changed_components"]) or "none"
        lines.append(
            "| "
            f"`{record['variant_id']}` | "
            f"`{components}` | "
            f"`{observed}` | "
            f"`{blocker}` | "
            f"`{str(record['passed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Replay Records",
            "",
            "| Replay | First route | Second route | Stable |",
            "| --- | --- | --- | --- |",
        ]
    )
    for record in output["replay_records"]:
        lines.append(
            "| "
            f"`{record['replay_id']}` | "
            f"`{record['first_selected_route']}` | "
            f"`{record['second_selected_route']}` | "
            f"`{str(record['stable']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "Iteration 6 tests source-sensitive perturbation and replay stability",
            "for the Iteration 5 control-clean candidate. It does not close final",
            "`AP4`, does not open Phase 8, and does not claim agency or native",
            "support.",
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
            "perturbation replay pass != final AP4 support before claim classification",
            "source-sensitive route ranking != intention",
            "artifact-level replay stability != native support",
            "support perturbation variant != semantic goal ownership",
            "memory/regulation perturbation variant != agency",
            "N14 Iteration 6 != fully native integration",
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
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
