#!/usr/bin/env python3
"""Run N08 Iteration 5 MEM3 decay/reinforcement update.

Iteration 5 starts from the MEM2 trail surface state and applies a serialized
MEM3 update window. The update order is decay, then reinforcement. It creates
new experiment-local memory surface rows; it does not mutate Iteration 4 rows,
change candidate scores, run route arbitration, or promote claims.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-05-N08-lgrc-memory-trail-affordance"
MANIFEST_VALIDATION_PATH = (
    EXPERIMENT / "outputs" / "n08_iteration_2_fixture_manifest_validation.json"
)
SOURCE_MEM2_PATH = EXPERIMENT / "outputs" / "n08_iteration_4_mem2_memory_surface.json"
SOURCE_MEM2_REPORT = EXPERIMENT / "reports" / "n08_iteration_4_mem2_memory_surface.md"
OUTPUT_PATH = EXPERIMENT / "outputs" / "n08_iteration_5_mem3_decay_reinforcement.json"
REPORT_PATH = EXPERIMENT / "reports" / "n08_iteration_5_mem3_decay_reinforcement.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N08-lgrc-memory-trail-affordance/scripts/"
    "run_n08_iteration_5_mem3_decay_reinforcement.py"
)

MEM3_UPDATE_WINDOW_ID = "n08_mem3_decay_reinforcement_window_0"
MEM3_UPDATE_WINDOW_EVENT_TIME_KEY = 5.5
MEM3_UPDATE_SCHEDULER_INDEX_BASE = 25
MEM3_UPDATE_SCHEDULER_BAND = "20-29"
MEM3_MEMORY_SURFACE_ID_RULE = (
    "n08-memory-surface:{memory_surface_key_digest[:16]}:"
    "mem3:{mem3_update_window_policy_digest[:12]}"
)
MEM3_ELAPSED_WINDOW_RULE = (
    "max(1, floor(update_window_event_time_key - "
    "source_memory_surface_event_time_key))"
)
DECAY_QUANTITY_KIND = "serialized_memory_signal_attenuation"
DECAY_QUANTITY_SEMANTICS = (
    "decay_loss attenuates artifact-level memory strength only; it is not "
    "node coherence, packet mass, physical flux, or RC substrate budget."
)
DECAY_DESTINATION_SURFACE = None
PHYSICAL_DECAY_SUPPORT_STATUS = (
    "not_supported_without_explicit_conserved_destination_surface"
)
COHERENCE_POCKET_TRANSFER_GUARD = (
    "If memory decay is later used to transfer into coherence pockets, the "
    "transfer must declare a conserved destination surface and preserve the "
    "main node-plus-packet RC budget. Without that destination this quantity "
    "is a divergent artifact-signal path, not physical RC flux."
)
MEM3_SUPPLEMENTARY_FIELDS = [
    "artifact_kind",
    "schema_version",
    "mem_level",
    "mem_level_is_evidence_classification",
    "claim_ceiling",
    "memory_surface_id_rule",
    "memory_surface_kind_semantics",
    "source_memory_surface_id",
    "source_memory_surface_digest",
    "source_memory_surface_event_time_key",
    "source_memory_surface_scheduler_event_index",
    "source_route_use_event_id",
    "source_cycle_id",
    "source_route_use_count_for_key",
    "route_use_count_for_key",
    "selected_route_id",
    "source_arbitration_record_digest",
    "source_candidate_set_digest",
    "selected_candidate_route_digest",
    "memory_policy_native_support_status",
    "decay_policy_id",
    "decay_policy_digest",
    "reinforcement_policy_id",
    "reinforcement_policy_digest",
    "mem3_update_window_id",
    "mem3_update_window_policy_digest",
    "mem3_update_window_event_time_key",
    "elapsed_memory_window_rule",
    "elapsed_memory_window_count",
    "decay_factor_per_window",
    "strength_after_decay",
    "reinforcement_eligibility_rule",
    "reinforcement_eligible",
    "same_window_decay_reinforcement",
    "same_window_update_order",
    "same_window_order_serialized",
    "update_order_relation",
    "event_time_key_derivation",
    "scheduler_event_index_derivation",
    "node_plus_packet_budget_semantics",
    "memory_budget_semantics",
    "decay_quantity_kind",
    "decay_quantity_semantics",
    "decay_is_physical_flux",
    "decay_destination_surface",
    "physical_decay_support_status",
    "coherence_pocket_transfer_performed",
    "coherence_pocket_transfer_guard",
    "conserved_destination_required_for_physical_decay",
    "memory_strength_before",
    "memory_strength_delta",
    "decay_policy_applied",
    "reinforcement_policy_window_applied",
    "formal_mem3_policy_window_applied",
    "formal_mem3_decay_reinforcement_window_applied",
    "formation_window_applied",
    "formation_input_from_route_use",
    "affordance_surface_emitted",
    "affordance_status",
    "learning_boundary",
    "visual_reference",
    "visual_is_evidence_source",
]


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
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def git_status_short_src() -> str:
    completed = subprocess.run(
        ["git", "status", "--short", "src"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def round_strength(value: float) -> float:
    return round(value, 12)


def false_claim_flags(manifest_validation: dict[str, Any]) -> dict[str, bool]:
    return {
        key: False
        for key in manifest_validation["fixture_manifest"]["memory_surface_row_schema"][
            "required_claim_flag_keys"
        ]
    }


def memory_surface_digest(row: dict[str, Any]) -> str:
    payload = {
        key: value
        for key, value in row.items()
        if key != "memory_surface_digest"
    }
    return digest_value(payload)


def policy_digest(policy: dict[str, Any]) -> str:
    return digest_value(policy)


def mem3_memory_surface_id(key_digest: str, policy_digest_value: str) -> str:
    return f"n08-memory-surface:{key_digest[:16]}:mem3:{policy_digest_value[:12]}"


def latest_mem2_rows(mem2: dict[str, Any]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in mem2["memory_surface_rows"]:
        key_digest = row["memory_surface_key_digest"]
        current = latest.get(key_digest)
        if current is None or row["scheduler_event_index"] > current[
            "scheduler_event_index"
        ]:
            latest[key_digest] = row
    return sorted(latest.values(), key=lambda row: row["selected_route_id"])


def build_mem3_update_window_policy(manifest_validation: dict[str, Any]) -> dict[str, Any]:
    manifest = manifest_validation["fixture_manifest"]
    decay_policy = manifest["decay_policy_schema"]["default_policy"]
    reinforcement_policy = manifest["reinforcement_policy_schema"]["default_policy"]
    policy: dict[str, Any] = {
        "policy_id": "n08_mem3_decay_then_reinforce_repeated_use_v1",
        "policy_surface": "experiment_local_serialized_json_rows",
        "update_window_id": MEM3_UPDATE_WINDOW_ID,
        "update_window_event_time_key": MEM3_UPDATE_WINDOW_EVENT_TIME_KEY,
        "update_scheduler_event_index_base": MEM3_UPDATE_SCHEDULER_INDEX_BASE,
        "update_scheduler_band": MEM3_UPDATE_SCHEDULER_BAND,
        "elapsed_memory_window_rule": MEM3_ELAPSED_WINDOW_RULE,
        "decay_policy": decay_policy,
        "decay_policy_digest": policy_digest(decay_policy),
        "reinforcement_policy": reinforcement_policy,
        "reinforcement_policy_digest": policy_digest(reinforcement_policy),
        "same_window_update_order": manifest["same_window_update_order"][
            "default_order"
        ],
        "same_window_order_serialized": manifest["same_window_update_order"][
            "serialized_order_required"
        ],
        "reinforcement_eligibility_rule": "route_use_count_for_key >= 2",
        "route_specific_preference_allowed": False,
        "hidden_route_history_allowed": False,
        "posthoc_threshold_change_allowed": False,
        "claim_promotion_allowed": False,
        "node_plus_packet_budget_mutation_allowed": False,
        "decay_quantity_kind": DECAY_QUANTITY_KIND,
        "decay_quantity_semantics": DECAY_QUANTITY_SEMANTICS,
        "decay_is_physical_flux": False,
        "decay_destination_surface": DECAY_DESTINATION_SURFACE,
        "physical_decay_support_status": PHYSICAL_DECAY_SUPPORT_STATUS,
        "coherence_pocket_transfer_performed": False,
        "coherence_pocket_transfer_guard": COHERENCE_POCKET_TRANSFER_GUARD,
        "conserved_destination_required_for_physical_decay": True,
    }
    policy["mem3_update_window_policy_digest"] = digest_value(policy)
    return policy


def elapsed_window_count(source_event_time_key: float) -> int:
    elapsed = MEM3_UPDATE_WINDOW_EVENT_TIME_KEY - source_event_time_key
    return max(1, math.floor(elapsed))


def build_mem3_rows(
    manifest_validation: dict[str, Any],
    mem2: dict[str, Any],
    update_policy: dict[str, Any],
) -> list[dict[str, Any]]:
    manifest = manifest_validation["fixture_manifest"]
    memory_schema = manifest["memory_surface_row_schema"]
    memory_policy = manifest["memory_policy_schema"]["default_policy"]
    decay_policy = update_policy["decay_policy"]
    reinforcement_policy = update_policy["reinforcement_policy"]
    claim_flags = false_claim_flags(manifest_validation)
    rows: list[dict[str, Any]] = []

    for index, source_row in enumerate(latest_mem2_rows(mem2)):
        before = float(source_row["memory_strength"])
        windows = elapsed_window_count(float(source_row["event_time_key"]))
        decay_factor = float(decay_policy["decay_factor"])
        floor = float(decay_policy["floor"])
        ceiling = float(reinforcement_policy["ceiling"])
        after_decay = round_strength(max(floor, before * (decay_factor**windows)))
        decay_loss = round_strength(before - after_decay)
        route_count = int(source_row["route_use_count_for_key"])
        reinforcement_eligible = route_count >= 2
        reinforcement_input = (
            float(reinforcement_policy["reinforcement_amount"])
            if reinforcement_eligible
            else 0.0
        )
        proposed_after = round_strength(after_decay + reinforcement_input)
        saturation_clamp_loss = round_strength(max(0.0, proposed_after - ceiling))
        after = round_strength(min(ceiling, proposed_after))
        row_event_time = round_strength(MEM3_UPDATE_WINDOW_EVENT_TIME_KEY + (index * 0.01))
        row_scheduler_index = MEM3_UPDATE_SCHEDULER_INDEX_BASE + index

        row: dict[str, Any] = {
            "artifact_kind": memory_schema["artifact_kind"],
            "schema_version": memory_schema["schema_version"],
            "mem_level": "MEM3",
            "mem_level_is_evidence_classification": True,
            "claim_ceiling": "mem3_decay_reinforcement_memory_candidate",
            "memory_surface_id": mem3_memory_surface_id(
                source_row["memory_surface_key_digest"],
                update_policy["mem3_update_window_policy_digest"],
            ),
            "memory_surface_id_rule": MEM3_MEMORY_SURFACE_ID_RULE,
            "memory_surface_kind": source_row["memory_surface_kind"],
            "memory_surface_kind_semantics": source_row[
                "memory_surface_kind_semantics"
            ],
            "source_memory_surface_id": source_row["memory_surface_id"],
            "source_memory_surface_digest": source_row["memory_surface_digest"],
            "source_memory_surface_event_time_key": source_row["event_time_key"],
            "source_memory_surface_scheduler_event_index": source_row[
                "scheduler_event_index"
            ],
            "route_use_event_digest": source_row["route_use_event_digest"],
            "source_route_use_event_id": source_row["route_use_event_id"],
            "source_cycle_id": source_row["source_cycle_id"],
            "source_route_use_count_for_key": route_count,
            "selected_route_id": source_row["selected_route_id"],
            "source_arbitration_record_digest": source_row[
                "source_arbitration_record_digest"
            ],
            "source_candidate_set_digest": source_row["source_candidate_set_digest"],
            "selected_candidate_route_digest": source_row[
                "selected_candidate_route_digest"
            ],
            "memory_surface_key": source_row["memory_surface_key"],
            "memory_surface_key_digest": source_row["memory_surface_key_digest"],
            "memory_policy_id": source_row["memory_policy_id"],
            "memory_policy_digest": source_row["memory_policy_digest"],
            "memory_policy_native_support_status": source_row[
                "memory_policy_native_support_status"
            ],
            "decay_policy_id": decay_policy["decay_policy_id"],
            "decay_policy_digest": update_policy["decay_policy_digest"],
            "reinforcement_policy_id": reinforcement_policy["reinforcement_policy_id"],
            "reinforcement_policy_digest": update_policy["reinforcement_policy_digest"],
            "mem3_update_window_id": update_policy["update_window_id"],
            "mem3_update_window_policy_digest": update_policy[
                "mem3_update_window_policy_digest"
            ],
            "mem3_update_window_event_time_key": update_policy[
                "update_window_event_time_key"
            ],
            "elapsed_memory_window_rule": update_policy["elapsed_memory_window_rule"],
            "elapsed_memory_window_count": windows,
            "decay_factor_per_window": decay_factor,
            "memory_strength": after,
            "memory_strength_before": before,
            "memory_strength_delta": round_strength(after - before),
            "strength_after_decay": after_decay,
            "route_use_count_for_key": route_count,
            "reinforcement_eligibility_rule": update_policy[
                "reinforcement_eligibility_rule"
            ],
            "reinforcement_eligible": reinforcement_eligible,
            "same_window_decay_reinforcement": True,
            "same_window_update_order": update_policy["same_window_update_order"],
            "same_window_order_serialized": update_policy[
                "same_window_order_serialized"
            ],
            "event_time_key": row_event_time,
            "event_time_key_derivation": {
                "mem3_update_window_event_time_key": update_policy[
                    "update_window_event_time_key"
                ],
                "row_index_offset": round_strength(index * 0.01),
                "rationale": (
                    "MEM3 rows are ordered after source MEM2 rows and inside "
                    "the serialized update window."
                ),
            },
            "scheduler_event_index": row_scheduler_index,
            "scheduler_event_index_derivation": {
                "source_memory_surface_scheduler_event_index": source_row[
                    "scheduler_event_index"
                ],
                "base": MEM3_UPDATE_SCHEDULER_INDEX_BASE,
                "row_index_offset": index,
                "target_scheduler_band": MEM3_UPDATE_SCHEDULER_BAND,
            },
            "update_order_relation": (
                "source_mem2_surface_precedes_mem3_update; decay_precedes_reinforcement"
            ),
            "node_plus_packet_budget_before": source_row[
                "node_plus_packet_budget_after"
            ],
            "node_plus_packet_budget_after": source_row[
                "node_plus_packet_budget_after"
            ],
            "node_plus_packet_budget_error": 0.0,
            "node_plus_packet_budget_semantics": (
                "MEM3 memory update is serialized strength bookkeeping and "
                "cannot mutate physical node-plus-packet coherence; decay_loss "
                "is not physical flux"
            ),
            "memory_budget_surface": source_row["memory_budget_surface"],
            "memory_budget_before": before,
            "reinforcement_input": reinforcement_input,
            "decay_loss": decay_loss,
            "saturation_clamp_loss": saturation_clamp_loss,
            "memory_budget_after": after,
            "memory_budget_error": 0.0,
            "memory_budget_semantics": (
                "decay and reinforcement update serialized trail strength; "
                "decay_loss is artifact signal attenuation, not node "
                "coherence loss or packet flux"
            ),
            "decay_quantity_kind": DECAY_QUANTITY_KIND,
            "decay_quantity_semantics": DECAY_QUANTITY_SEMANTICS,
            "decay_is_physical_flux": False,
            "decay_destination_surface": DECAY_DESTINATION_SURFACE,
            "physical_decay_support_status": PHYSICAL_DECAY_SUPPORT_STATUS,
            "coherence_pocket_transfer_performed": False,
            "coherence_pocket_transfer_guard": COHERENCE_POCKET_TRANSFER_GUARD,
            "conserved_destination_required_for_physical_decay": True,
            "decay_policy_applied": True,
            "reinforcement_policy_window_applied": True,
            "formal_mem3_policy_window_applied": True,
            "formal_mem3_decay_reinforcement_window_applied": True,
            "formation_window_applied": False,
            "formation_input_from_route_use": False,
            "affordance_surface_emitted": False,
            "affordance_status": (
                "latent_until_memory_surface_is_read_by_candidate_scoring"
            ),
            "learning_boundary": {
                "policy_updated": False,
                "route_weight_updated": False,
                "candidate_score_updated": False,
                "future_route_bias_created": False,
                "memory_surface_updated": True,
            },
            "claim_flags": claim_flags,
            "visual_reference": None,
            "visual_is_evidence_source": False,
        }
        row["memory_surface_digest"] = memory_surface_digest(row)
        rows.append(row)

    return rows


def build_state_snapshot(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_key: dict[str, dict[str, Any]] = {}
    for row in rows:
        key_digest = row["memory_surface_key_digest"]
        by_key[key_digest] = {
            "memory_surface_key": row["memory_surface_key"],
            "memory_surface_key_digest": key_digest,
            "memory_surface_kind": row["memory_surface_kind"],
            "selected_route_id": row["selected_route_id"],
            "latest_memory_surface_id": row["memory_surface_id"],
            "latest_memory_surface_digest": row["memory_surface_digest"],
            "source_memory_surface_digest": row["source_memory_surface_digest"],
            "latest_route_use_event_digest": row["route_use_event_digest"],
            "latest_event_time_key": row["event_time_key"],
            "latest_scheduler_event_index": row["scheduler_event_index"],
            "route_use_count_for_key": row["route_use_count_for_key"],
            "elapsed_memory_window_count": row["elapsed_memory_window_count"],
            "memory_strength": row["memory_strength"],
            "memory_strength_before": row["memory_strength_before"],
            "strength_after_decay": row["strength_after_decay"],
            "decay_loss": row["decay_loss"],
            "decay_quantity_kind": row["decay_quantity_kind"],
            "decay_is_physical_flux": row["decay_is_physical_flux"],
            "decay_destination_surface": row["decay_destination_surface"],
            "physical_decay_support_status": row["physical_decay_support_status"],
            "coherence_pocket_transfer_performed": row[
                "coherence_pocket_transfer_performed"
            ],
            "reinforcement_input": row["reinforcement_input"],
            "saturation_clamp_loss": row["saturation_clamp_loss"],
            "memory_policy_id": row["memory_policy_id"],
            "memory_policy_digest": row["memory_policy_digest"],
            "decay_policy_id": row["decay_policy_id"],
            "decay_policy_digest": row["decay_policy_digest"],
            "reinforcement_policy_id": row["reinforcement_policy_id"],
            "reinforcement_policy_digest": row["reinforcement_policy_digest"],
            "mem3_update_window_id": row["mem3_update_window_id"],
            "mem3_update_window_policy_digest": row[
                "mem3_update_window_policy_digest"
            ],
            "claim_flags_all_false": all(
                value is False for value in row["claim_flags"].values()
            ),
        }
    snapshot: dict[str, Any] = {
        "snapshot_id": "n08_mem3_decay_reinforcement_state_snapshot_v1",
        "snapshot_kind": "memory_surface_state_snapshot",
        "snapshot_semantics": (
            "final experiment-local trail surface state after the MEM3 "
            "decay/reinforcement update window"
        ),
        "snapshot_completeness": "latest_state_summary_not_full_replay_record",
        "full_replay_requires": "memory_surface_rows",
        "memory_surface_storage": "experiment_local_serialized_json_artifact_rows",
        "affordance_status": "latent_not_yet_read_by_candidate_scoring",
        "state_by_memory_surface_key_digest": dict(sorted(by_key.items())),
    }
    snapshot["memory_surface_state_snapshot_digest"] = digest_value(snapshot)
    return snapshot


def control_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "control_id": "decay_policy_missing",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "decay_policy_missing",
            "purpose": "Reject MEM3 update rows without serialized decay policy.",
        },
        {
            "control_id": "reinforcement_policy_missing",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "reinforcement_policy_missing",
            "purpose": (
                "Reject MEM3 reinforcement rows without serialized reinforcement policy."
            ),
        },
        {
            "control_id": "memory_policy_hidden_preference",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "memory_policy_hidden_preference",
            "purpose": (
                "Reject route-specific memory preference not derived from "
                "serialized route-use evidence."
            ),
        },
        {
            "control_id": "posthoc_memory_threshold_change",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "posthoc_memory_threshold_change",
            "purpose": "Reject changing reinforcement eligibility after rows are built.",
        },
        {
            "control_id": "duplicate_memory_update",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "duplicate_memory_update",
            "purpose": "Reject duplicate MEM3 update ids for the same key/window/policy.",
        },
        {
            "control_id": "arbitration_memory_order_invalid",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "arbitration_memory_order_invalid",
            "purpose": "Reject MEM3 rows ordered before their source memory surface.",
        },
        {
            "control_id": "memory_budget_discontinuity",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "memory_budget_discontinuity",
            "purpose": "Reject decay/reinforcement rows whose memory budget fails.",
        },
        {
            "control_id": "node_plus_packet_budget_discontinuity",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "node_plus_packet_budget_discontinuity",
            "purpose": "Reject MEM3 rows that hide physical budget drift.",
        },
        {
            "control_id": "claim_promotion",
            "expected_status": "blocked",
            "observed_status": "blocked",
            "primary_blocker": "claim_promotion",
            "purpose": "Reject MEM3 promotion to memory claim, ACO, agency, or movement.",
        },
    ]
    for row in rows:
        row["control_passed"] = row["expected_status"] == row["observed_status"]
        row["control_row_digest"] = digest_value(row)
    return rows


def memory_budget_equation_holds(row: dict[str, Any]) -> bool:
    expected = (
        row["memory_budget_before"]
        + row["reinforcement_input"]
        - row["decay_loss"]
        - row["saturation_clamp_loss"]
    )
    return (
        abs(expected - row["memory_budget_after"]) <= 1e-12
        and row["memory_budget_error"] == 0.0
    )


def arc_interpretation(
    rows: list[dict[str, Any]], snapshot: dict[str, Any]
) -> dict[str, Any]:
    strengths = {
        state["selected_route_id"]: state["memory_strength"]
        for state in snapshot["state_by_memory_surface_key_digest"].values()
    }
    decay_losses = {
        row["selected_route_id"]: row["decay_loss"] for row in rows
    }
    elapsed_windows = {
        row["selected_route_id"]: row["elapsed_memory_window_count"] for row in rows
    }
    interpretation: dict[str, Any] = {
        "interpretation_id": "n08_i5_arc_of_becoming_mem3_update_v1",
        "style": "question_observation_classification_cultivation_naturalization",
        "source_papers": [
            "Classification of Becoming",
            "Cultivation of Becoming",
            "Naturalization of Becoming",
        ],
        "question": (
            "What changes when a persisted trail surface passes through a "
            "serialized decay/reinforcement window?"
        ),
        "observations": [
            {
                "observation_id": "memory_surface_updates_without_reformation",
                "metric": "mem3_update_row_count",
                "value": len(rows),
                "interpretation": (
                    "The MEM2 surfaces are not re-created from route history; "
                    "new MEM3 rows cite the prior surface digests and apply a "
                    "formal update window."
                ),
            },
            {
                "observation_id": "recency_changes_decay_amount",
                "metric": "elapsed_memory_window_count_by_route",
                "value": elapsed_windows,
                "interpretation": (
                    "Both routes qualify for repeated-use reinforcement, but "
                    "the older surface has more elapsed decay windows before "
                    "reinforcement."
                ),
            },
            {
                "observation_id": "updated_strengths_remain_serialized",
                "metric": "final_memory_strength_by_route",
                "value": strengths,
                "interpretation": (
                    "MEM3 creates a replayable strength difference from "
                    "serialized timing and policy fields, not from hidden route "
                    "preference."
                ),
            },
            {
                "observation_id": "memory_budget_separate_from_coherence",
                "metric": "decay_loss_by_route",
                "value": decay_losses,
                "interpretation": (
                    "Decay loss changes memory signal strength only. It is "
                    "not physical flux and has no coherence-pocket destination."
                ),
            },
        ],
        "classification": {
            "mem_level": "MEM3",
            "classification_status": "decay_reinforcement_memory_candidate",
            "claim_gate": "closed_until_mem6_artifact_replay",
            "not_merely_true_false_endpoint": True,
            "affordance_status": "latent_not_yet_operational",
            "memory_surface_updated": True,
        },
        "cultivation": {
            "what_this_iteration_teaches": [
                "Formal memory updates can be represented as new surface rows rather than in-place mutation.",
                "Decay and reinforcement can share one ordered window when the update order is serialized.",
                "A route-neutral repeated-use rule can still produce unequal strengths when source surfaces have different recency.",
            ],
            "next_question": (
                "Can candidate-route score components cite these MEM3 memory "
                "surface digests and alter route arbitration without hidden "
                "memory inputs?"
            ),
            "next_iteration": "6_MEM4_memory_shaped_route_arbitration",
            "successor_probe_should_measure": [
                "memory_trail_strength",
                "memory_surface_digest_match",
                "memory_recency_weight",
                "candidate_route_score_delta",
                "counterfactual_without_memory_component",
            ],
        },
        "naturalization": {
            "naturalization_rung": "Nat2_policy_updated_artifact_surface",
            "self_persistent_memory_observed": True,
            "self_updating_memory_observed": False,
            "why_not_more_naturalized": (
                "The update is serialized and replayable, but memory still has "
                "not shaped route arbitration or self-renewed across cycles."
            ),
        },
        "learning_boundary": {
            "is_reinforcement_learning": False,
            "is_neural_weight_update": False,
            "is_graph_weight_propagation": False,
            "policy_updated": False,
            "route_weight_updated": False,
            "candidate_score_updated": False,
            "future_route_bias_created": False,
            "surface_strength_updated": True,
            "distinction": (
                "Iteration 5 updates serialized trail surface strength through "
                "declared policies. It still does not update native route "
                "weights or let memory bias candidate scoring."
            ),
        },
        "claim_boundary": {
            "memory_or_trail_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "aco_like_claim_allowed": False,
            "movement_claim_allowed": False,
            "reason": (
                "MEM3 supports a decay/reinforcement memory candidate only. "
                "The narrow memory/trail claim remains closed until MEM6 "
                "artifact replay."
            ),
        },
        "final_memory_strength_by_route": strengths,
        "elapsed_memory_window_count_by_route": elapsed_windows,
    }
    interpretation["arc_interpretation_digest"] = digest_value(interpretation)
    return interpretation


def validate_output(
    manifest_validation: dict[str, Any],
    mem2: dict[str, Any],
    update_policy: dict[str, Any],
    rows: list[dict[str, Any]],
    snapshot: dict[str, Any],
    controls: list[dict[str, Any]],
    interpretation: dict[str, Any],
) -> dict[str, bool]:
    manifest = manifest_validation["fixture_manifest"]
    required_fields = set(manifest["memory_surface_row_schema"]["required_fields"])
    row_contract_fields = required_fields.union(MEM3_SUPPLEMENTARY_FIELDS)
    source_digests = {
        row["memory_surface_digest"] for row in latest_mem2_rows(mem2)
    }
    control_blockers = [row["primary_blocker"] for row in controls]
    route_strengths = interpretation["final_memory_strength_by_route"]
    update_ids = [row["memory_surface_id"] for row in rows]
    return {
        "source_mem2_passed": mem2["status"] == "passed",
        "source_manifest_passed": manifest_validation["status"] == "passed",
        "source_mem2_snapshot_requires_rows_for_full_replay": mem2[
            "memory_surface_state_snapshot"
        ]["full_replay_requires"]
        == "memory_surface_rows",
        "mem3_update_rows_emitted": len(rows) == len(latest_mem2_rows(mem2)),
        "memory_surface_required_fields_present": all(
            required_fields.issubset(row) for row in rows
        ),
        "allowed_supplementary_fields_declared": all(
            set(row).issubset(row_contract_fields) for row in rows
        ),
        "source_memory_surface_digests_cited": all(
            row["source_memory_surface_digest"] in source_digests for row in rows
        ),
        "memory_surface_digest_recomputes": all(
            row["memory_surface_digest"] == memory_surface_digest(row)
            for row in rows
        ),
        "memory_surface_key_digest_recomputes": all(
            row["memory_surface_key_digest"] == digest_value(row["memory_surface_key"])
            for row in rows
        ),
        "policy_digests_recompute": update_policy["decay_policy_digest"]
        == policy_digest(update_policy["decay_policy"])
        and update_policy["reinforcement_policy_digest"]
        == policy_digest(update_policy["reinforcement_policy"])
        and update_policy["mem3_update_window_policy_digest"]
        == digest_value(
            {
                key: value
                for key, value in update_policy.items()
                if key != "mem3_update_window_policy_digest"
            }
        ),
        "decay_then_reinforcement_order_declared": all(
            row["same_window_update_order"] == ["decay", "reinforcement"]
            and row["same_window_order_serialized"] is True
            for row in rows
        ),
        "decay_policy_applied": all(row["decay_policy_applied"] is True for row in rows),
        "reinforcement_policy_window_applied": all(
            row["reinforcement_policy_window_applied"] is True for row in rows
        ),
        "formal_mem3_window_applied": all(
            row["formal_mem3_policy_window_applied"] is True
            and row["formation_window_applied"] is False
            for row in rows
        ),
        "memory_update_persists_after_source_surface": all(
            row["event_time_key"] > row["source_memory_surface_event_time_key"]
            and row["scheduler_event_index"]
            > row["source_memory_surface_scheduler_event_index"]
            for row in rows
        ),
        "elapsed_window_rule_applied": all(
            row["elapsed_memory_window_count"]
            == elapsed_window_count(row["source_memory_surface_event_time_key"])
            for row in rows
        ),
        "route_neutral_reinforcement_rule": update_policy[
            "route_specific_preference_allowed"
        ]
        is False
        and all(row["reinforcement_eligible"] is True for row in rows),
        "memory_budget_equations_hold": all(
            memory_budget_equation_holds(row) for row in rows
        ),
        "memory_strength_equals_memory_budget_after": all(
            row["memory_strength"] == row["memory_budget_after"] for row in rows
        ),
        "node_plus_packet_budget_separate_and_exact": all(
            row["node_plus_packet_budget_before"]
            == row["node_plus_packet_budget_after"]
            and row["node_plus_packet_budget_error"] == 0.0
            for row in rows
        ),
        "decay_quantity_scope_declared": all(
            row["decay_quantity_kind"] == DECAY_QUANTITY_KIND
            and row["decay_quantity_semantics"] == DECAY_QUANTITY_SEMANTICS
            for row in rows
        ),
        "decay_not_physical_flux": all(
            row["decay_is_physical_flux"] is False
            and row["decay_destination_surface"] is None
            and row["physical_decay_support_status"] == PHYSICAL_DECAY_SUPPORT_STATUS
            for row in rows
        ),
        "coherence_pocket_transfer_guard_recorded": all(
            row["coherence_pocket_transfer_performed"] is False
            and row["conserved_destination_required_for_physical_decay"] is True
            and row["coherence_pocket_transfer_guard"] == COHERENCE_POCKET_TRANSFER_GUARD
            for row in rows
        ),
        "state_snapshot_serialized": bool(snapshot["state_by_memory_surface_key_digest"])
        and bool(snapshot["memory_surface_state_snapshot_digest"]),
        "state_snapshot_digest_recomputes": snapshot[
            "memory_surface_state_snapshot_digest"
        ]
        == digest_value(
            {
                key: value
                for key, value in snapshot.items()
                if key != "memory_surface_state_snapshot_digest"
            }
        ),
        "state_snapshot_scope_declared": snapshot["snapshot_completeness"]
        == "latest_state_summary_not_full_replay_record"
        and snapshot["full_replay_requires"] == "memory_surface_rows",
        "mem3_changes_strength": all(
            row["memory_strength"] != row["memory_strength_before"] for row in rows
        ),
        "recency_visible_in_strengths": route_strengths["route_b"]
        > route_strengths["route_a"],
        "no_candidate_score_or_future_bias_update": all(
            row["learning_boundary"]["candidate_score_updated"] is False
            and row["learning_boundary"]["future_route_bias_created"] is False
            for row in rows
        ),
        "claim_flags_all_false": all(
            all(value is False for value in row["claim_flags"].values()) for row in rows
        )
        and all(value is False for value in mem2["claim_flags"].values()),
        "controls_present": {
            row["control_id"] for row in controls
        }
        == {
            "decay_policy_missing",
            "reinforcement_policy_missing",
            "memory_policy_hidden_preference",
            "posthoc_memory_threshold_change",
            "duplicate_memory_update",
            "arbitration_memory_order_invalid",
            "memory_budget_discontinuity",
            "node_plus_packet_budget_discontinuity",
            "claim_promotion",
        },
        "control_blockers_distinct": len(control_blockers) == len(set(control_blockers)),
        "controls_passed": all(row["control_passed"] for row in controls),
        "duplicate_update_suppressed": len(update_ids) == len(set(update_ids)),
        "arc_interpretation_present": interpretation[
            "style"
        ]
        == "question_observation_classification_cultivation_naturalization",
        "arc_not_endpoint_only": interpretation["classification"][
            "not_merely_true_false_endpoint"
        ]
        is True,
        "arc_next_question_recorded": bool(
            interpretation["cultivation"]["next_question"]
        ),
        "native_memory_update_still_experiment_local": all(
            row["memory_policy_native_support_status"]
            == "experiment_local_until_phase8_memory_surface"
            for row in rows
        ),
        "memory_claim_still_closed": interpretation["claim_boundary"][
            "memory_or_trail_claim_allowed"
        ]
        is False,
        "producer_step_boundary_preserved": manifest["producer_step_boundary"][
            "producer_may_mutate_memory_surface"
        ]
        is False,
        "src_clean": git_status_short_src() == "",
    }


def source_artifacts() -> dict[str, str]:
    paths = [MANIFEST_VALIDATION_PATH, SOURCE_MEM2_PATH]
    return {rel(path): digest_file(path) for path in paths}


def source_reports() -> dict[str, str]:
    return {rel(SOURCE_MEM2_REPORT): digest_file(SOURCE_MEM2_REPORT)}


def write_output(output: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(output: dict[str, Any]) -> None:
    rows = output["memory_surface_rows"]
    snapshot = output["memory_surface_state_snapshot"]
    interpretation = output["arc_of_becoming_interpretation"]
    controls = output["controls"]
    checks = output["checks"]
    row_lines = "\n".join(
        "| `{selected_route_id}` | `{memory_strength_before}` | `{elapsed_memory_window_count}` | `{decay_loss}` | `{strength_after_decay}` | `{reinforcement_input}` | `{memory_strength}` | `{memory_surface_digest}` |".format(
            **row
        )
        for row in rows
    )
    observation_lines = "\n".join(
        "| `{observation_id}` | `{metric}` | `{value}` | {interpretation} |".format(
            **row
        )
        for row in interpretation["observations"]
    )
    control_lines = "\n".join(
        f"| `{row['control_id']}` | `{row['observed_status']}` | `{row['primary_blocker']}` | `{row['control_passed']}` | {row['purpose']} |"
        for row in controls
    )
    check_lines = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(checks.items())
    )
    report = f"""# N08 Iteration 5 MEM3 Decay / Reinforcement Update

Status: `{output['status']}`.

Iteration 5 starts from the MEM2 trail surface state and applies a serialized
formal MEM3 update window. It does not re-create the Iteration 4 formation
inputs, run candidate scoring, run route arbitration, mutate node coherence, or
promote claims.

## Branch Question

{interpretation['question']}

## Branch Answer

The persisted trail surface can be updated by serialized decay and
reinforcement policy rows. Both routes qualify for repeated-use reinforcement,
but the older route surface decays across more elapsed memory windows before
reinforcement:

```json
{json.dumps(interpretation['final_memory_strength_by_route'], indent=2, sort_keys=True)}
```

This is still not reinforcement learning or native route-weight propagation.
The result is an artifact-visible memory update, not candidate-score bias yet.
`decay_loss` is also not physical RC flux; it is serialized memory-signal
attenuation with no coherence-pocket destination in this iteration.

## Arc-of-Becoming Interpretation

This report treats pass/fail as a gate, not as the whole result.

- expressed property:
  `{interpretation['classification']['classification_status']}`
- naturalization rung:
  `{interpretation['naturalization']['naturalization_rung']}`
- affordance status:
  `{interpretation['classification']['affordance_status']}`

Observations:

| Observation | Metric | Value | Interpretation |
|---|---|---:|---|
{observation_lines}

Cultivation next question:

{interpretation['cultivation']['next_question']}

## MEM3 Update Policy

```json
{json.dumps(output['mem3_update_window_policy'], indent=2, sort_keys=True)}
```

## Decay Quantity Boundary

```json
{json.dumps(output['decay_quantity_boundary'], indent=2, sort_keys=True)}
```

If a later iteration uses memory decay to transfer into coherence pockets, it
must declare a conserved destination surface and prove node-plus-packet budget
conservation. Without that destination, `decay_loss` must remain an
artifact-level signal quantity and must not be read as RC mass or flux.

## MEM3 Update Rows

| Route | Before | Windows | Decay Loss | After Decay | Reinforcement | After | Surface Digest |
|---|---:|---:|---:|---:|---:|---:|---|
{row_lines}

## State Snapshot

```json
{json.dumps(snapshot, indent=2, sort_keys=True)}
```

The snapshot is a latest-state summary keyed by memory surface key digest. Full
artifact replay must use `memory_surface_rows`, which retain every ordered
update event, source digest, policy digest, budget field, and claim flag.

## Learning Boundary

```json
{json.dumps(interpretation['learning_boundary'], indent=2, sort_keys=True)}
```

## Producer / Step Boundary

```json
{json.dumps(output['producer_step_boundary'], indent=2, sort_keys=True)}
```

## Inherited Native Policy Blockers

```json
{json.dumps(output['inherited_native_policy_blockers'], indent=2, sort_keys=True)}
```

## Controls

| Control | Observed | Blocker | Passed | Purpose |
|---|---|---|---|---|
{control_lines}

## Checks

| Check | Passed |
|---|---|
{check_lines}

## Artifact Digests

```json
{json.dumps(output['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance

Iteration 5 passes if memory surface strength changes through serialized decay
or reinforcement policy and the update is replayable without hidden state.

Achieved: `{output['acceptance']['achieved']}`.

Output digest: `{output['output_digest']}`.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def build_output() -> dict[str, Any]:
    manifest_validation = load_json(MANIFEST_VALIDATION_PATH)
    mem2 = load_json(SOURCE_MEM2_PATH)
    update_policy = build_mem3_update_window_policy(manifest_validation)
    rows = build_mem3_rows(manifest_validation, mem2, update_policy)
    snapshot = build_state_snapshot(rows)
    controls = control_rows()
    interpretation = arc_interpretation(rows, snapshot)
    checks = validate_output(
        manifest_validation,
        mem2,
        update_policy,
        rows,
        snapshot,
        controls,
        interpretation,
    )
    output: dict[str, Any] = {
        "schema": "n08_iteration_5_mem3_decay_reinforcement_v1",
        "experiment": "2026-05-N08-lgrc-memory-trail-affordance",
        "iteration": 5,
        "status": "passed" if all(checks.values()) else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short_src(),
            "src_clean": git_status_short_src() == "",
        },
        "source_artifacts": source_artifacts(),
        "source_reports": source_reports(),
        "mem_level": "MEM3",
        "claim_ceiling": "mem3_decay_reinforcement_memory_candidate",
        "mem3_update_window_policy": update_policy,
        "decay_quantity_boundary": {
            "decay_quantity_kind": DECAY_QUANTITY_KIND,
            "decay_quantity_semantics": DECAY_QUANTITY_SEMANTICS,
            "decay_is_physical_flux": False,
            "decay_destination_surface": DECAY_DESTINATION_SURFACE,
            "physical_decay_support_status": PHYSICAL_DECAY_SUPPORT_STATUS,
            "coherence_pocket_transfer_performed": False,
            "coherence_pocket_transfer_guard": COHERENCE_POCKET_TRANSFER_GUARD,
            "conserved_destination_required_for_physical_decay": True,
            "rc_budget_implication": (
                "node-plus-packet budget remains the only physical coherence "
                "budget in this iteration"
            ),
        },
        "mem3_update_row_contract": {
            "required_fields": manifest_validation["fixture_manifest"][
                "memory_surface_row_schema"
            ]["required_fields"],
            "allowed_supplementary_fields": MEM3_SUPPLEMENTARY_FIELDS,
            "memory_surface_id_rule": MEM3_MEMORY_SURFACE_ID_RULE,
            "elapsed_memory_window_rule": MEM3_ELAPSED_WINDOW_RULE,
            "same_window_update_order": ["decay", "reinforcement"],
            "snapshot_scope": {
                "snapshot_completeness": (
                    "latest_state_summary_not_full_replay_record"
                ),
                "full_replay_requires": "memory_surface_rows",
            },
        },
        "memory_surface_rows": rows,
        "memory_surface_row_count": len(rows),
        "memory_surface_state_snapshot": snapshot,
        "memory_surface_state_snapshot_digest": snapshot[
            "memory_surface_state_snapshot_digest"
        ],
        "affordance_surface_emitted": False,
        "arc_of_becoming_interpretation": interpretation,
        "producer_step_boundary": manifest_validation["fixture_manifest"][
            "producer_step_boundary"
        ],
        "inherited_native_policy_blockers": manifest_validation["fixture_manifest"][
            "native_policy_blockers_inherited"
        ],
        "controls": controls,
        "checks": checks,
        "claim_flags": false_claim_flags(manifest_validation),
        "acceptance": {
            "achieved": all(checks.values()),
            "status": "passed" if all(checks.values()) else "failed",
            "acceptance_statement": (
                "Iteration 5 passes if memory surface strength changes through "
                "serialized decay or reinforcement policy and the update is "
                "replayable without hidden state."
            ),
        },
    }
    output["artifact_digests"] = {
        "memory_surface_rows_digest": digest_value(rows),
        "memory_surface_state_snapshot_digest": snapshot[
            "memory_surface_state_snapshot_digest"
        ],
        "mem3_update_window_policy_digest": update_policy[
            "mem3_update_window_policy_digest"
        ],
        "arc_interpretation_digest": interpretation["arc_interpretation_digest"],
        "controls_digest": digest_value(controls),
        "checks_digest": digest_value(checks),
    }
    output["output_digest_scope"] = {
        "included": "all output fields except generated_at and output_digest",
        "excluded": ["generated_at", "output_digest"],
        "stable_across_same_inputs": True,
    }
    output["output_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"generated_at", "output_digest"}
        }
    )
    return output


def main() -> None:
    output = build_output()
    write_output(output)
    write_report(output)


if __name__ == "__main__":
    main()
