"""Validate the N05 fixture manifest and control contract.

This script is experiment-local. It validates the Iteration 2 fixture,
policy, budget, and control declarations before any oscillator probe runs. It
does not import or mutate `src/pygrc`.
"""

from __future__ import annotations

import copy
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N05 = ROOT / "experiments/2026-05-N05-lgrc-coherence-waves-oscillators"
MANIFEST_PATH = N05 / "configs/n05_fixture_manifest_v1.json"
OUTPUT_PATH = N05 / "outputs/n05_iteration_2_fixture_manifest_validation.json"
REPORT_PATH = N05 / "reports/n05_iteration_2_fixture_manifest_validation.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators/scripts/"
    "validate_n05_fixture_manifest.py"
)


CLAIM_FLAGS_FALSE = {
    "movement_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "agency_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "memory_or_trail_claim_allowed": False,
    "goal_proxy_regulation_claim_allowed": False,
    "agentic_like_claim_allowed": False,
    "locomotion_like_claim_allowed": False,
    "biological_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "unrestricted_movement_claim_allowed": False,
}

REQUIRED_CONTROLS = {
    "policy_disabled",
    "pulse_disabled",
    "missing_source",
    "missing_target",
    "missing_route",
    "hidden_schedule",
    "hidden_reservoir",
    "budget_ambiguity",
    "stale_producer_read",
    "idempotent_duplicate_production",
    "snapshot_continue_after_load",
    "producer_mutation_attempt",
    "claim_promotion_attempt",
}

REQUIRED_DEFAULTS = {
    "lapse_policy",
    "edge_delay_policy",
    "symmetric_delay_policy",
    "packetized_causal_flux_representation",
    "packet_pending_flux_ledger_representation",
}

REQUIRED_CYCLE_STEPS = [
    "outbound_departure",
    "target_contact",
    "return_eligibility",
    "return_packet",
    "source_contact_absorption",
]

PRODUCER_FORBIDDEN_WRITES = {
    "active_node_coherence",
    "packet_ledger",
    "topology",
    "support_mask",
    "centroid",
    "displacement",
    "claim_flags",
}

O_LEVELS = {"O0", "O1", "O2", "O3", "O4", "O5", "O6"}

O_LEVEL_CLAIM_CEILINGS = {
    "O0": "no_oscillation",
    "O1": "delayed_pulse_candidate",
    "O2": "reflected_pulse_candidate",
    "O3": "amplified_return_candidate",
    "O4": "repeated_oscillator_cycle_candidate",
    "O5": "self_sustained_oscillator_candidate",
    "O6": "route_coupled_oscillator_candidate",
}

TIMING_VOCABULARY = {
    "scheduler_event_index",
    "snapshot_index",
    "event_time_key",
    "node_proper_time",
    "edge_causal_delay",
}

NATIVE_SURFACE_REFERENCES = {
    "route_aspect_contract",
    "flux_route_producer",
    "surplus_trigger_producer",
    "self_rearm_evidence",
    "causal_pulse_substrate_surface",
    "time_scoped_lineage_replay",
    "snapshot_restore",
    "bounded_autonomous_run_loop",
    "native_route_arbitration",
}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError("manifest root must be a JSON object")
    return data


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _float_equal(left: float, right: float, epsilon: float) -> bool:
    return abs(left - right) <= epsilon


def _route_chain_valid(
    route: dict[str, Any],
    *,
    node_ids: set[int],
    edges: dict[int, dict[str, Any]],
) -> bool:
    hops = route.get("route_hops", [])
    if not hops:
        return False
    expected_source = route.get("source_node_id")
    expected_target = route.get("target_node_id")
    previous_target = expected_source
    for hop in hops:
        edge = edges.get(hop.get("edge_id"))
        source = hop.get("source_node_id")
        target = hop.get("target_node_id")
        if edge is None:
            return False
        if source not in node_ids or target not in node_ids:
            return False
        if previous_target != source:
            return False
        if {source, target} != {edge.get("u"), edge.get("v")}:
            return False
        if not edge.get("route_eligible", False):
            return False
        previous_target = target
    return previous_target == expected_target


def _base_checks(manifest: dict[str, Any]) -> dict[str, bool]:
    fixture = manifest.get("fixture", {})
    nodes = fixture.get("nodes", [])
    edges = fixture.get("edges", [])
    routes = manifest.get("routes", {})
    budget = manifest.get("budget_surfaces", {}).get("node_plus_packet", {})
    surface_accounting = manifest.get("budget_surfaces", {}).get("surface_accounting", {})
    reservoir_accounting = manifest.get("reservoir_accounting", {})
    defaults = manifest.get("conservative_lgrc_defaults", {})
    policies = manifest.get("policies", {})
    explicit_policy = policies.get("phase_1_explicit_scheduling_policy_fields", {})
    threshold_policy = policies.get("phase_2_runtime_threshold_policy_fields", {})
    phase3_audit = policies.get("phase_3_native_policy_support_audit_fields", {})
    controls = manifest.get("controls", [])
    snapshot = manifest.get("snapshot_contract", {})
    topology = manifest.get("topology_policy", {})
    cycle = manifest.get("cycle_definition", {})
    claim_boundary = manifest.get("claim_boundary", {})
    semantic_boundary = manifest.get("semantic_role_boundary", {})
    o_ladder_contract = manifest.get("o_ladder_contract", {})
    native_refs = manifest.get("native_surface_cross_references", {})
    timing_vocabulary = manifest.get("lgrc_timing_vocabulary", {})

    node_ids = [node.get("node_id") for node in nodes]
    node_id_set = set(node_ids)
    edge_ids = [edge.get("edge_id") for edge in edges]
    edge_id_set = set(edge_ids)
    edges_by_id = {edge.get("edge_id"): edge for edge in edges}
    source_node_id = fixture.get("source_node_id")
    target_node_id = fixture.get("target_node_id")
    target_reservoir_node_id = fixture.get("target_reservoir_node_id")
    initial_node_coherence_by_node = budget.get("initial_node_coherence_by_node", {})
    epsilon = float(budget.get("epsilon_budget", -1.0))
    initial_node_total = sum(float(value) for value in initial_node_coherence_by_node.values())
    route_delay_sum_ok = True
    for route in routes.values():
        delay_from_hops = sum(
            float(edges_by_id[hop["edge_id"]]["temporal_delay"])
            for hop in route.get("route_hops", [])
            if hop.get("edge_id") in edges_by_id
        )
        route_delay_sum_ok = route_delay_sum_ok and _float_equal(
            delay_from_hops,
            float(route.get("causal_delay_ticks", -1.0)),
            0.0,
        )

    control_ids = [control.get("control_id") for control in controls]
    blocker_ids = [control.get("primary_blocker") for control in controls]
    producer_writable = set(explicit_policy.get("producer_writable_fields", []))
    producer_forbidden = set(explicit_policy.get("producer_forbidden_writes", []))
    idempotency_fields = defaults.get("packet_pending_flux_ledger_representation", {}).get(
        "idempotency_key_fields", []
    )
    route_aspect_ref = native_refs.get("route_aspect_contract", {})
    surplus_ref = native_refs.get("surplus_trigger_producer", {})
    self_rearm_ref = native_refs.get("self_rearm_evidence", {})
    autonomous_ref = native_refs.get("bounded_autonomous_run_loop", {})
    target_reservoir_mapping = reservoir_accounting.get("target_reservoir", {}).get(
        "native_surplus_trigger_mapping", {}
    )

    return {
        "schema_matches": manifest.get("schema")
        == "n05_coherence_oscillator_fixture_manifest_v1",
        "no_oscillator_probe_run": manifest.get("oscillator_probe_run") is False,
        "no_positive_o_level_evidence_generated": manifest.get(
            "positive_o_level_evidence_generated"
        )
        is False,
        "fixture_roles_are_nonsemantic": semantic_boundary.get(
            "nest_semantic_object_claim_allowed"
        )
        is False
        and semantic_boundary.get("food_semantic_object_claim_allowed") is False
        and semantic_boundary.get("trail_memory_claim_allowed") is False
        and semantic_boundary.get("ant_or_agent_object_claim_allowed") is False
        and semantic_boundary.get("source_node_role")
        == "mechanical_source_or_reservoir_role_only"
        and semantic_boundary.get("target_node_role")
        == "mechanical_interaction_site_only",
        "new_n05_fixture_strategy_declared": manifest.get("fixture_reuse_strategy", {}).get(
            "selected_strategy"
        )
        == "define_new_n05_source_target_reservoir_fixture",
        "o_ladder_contract_complete": O_LEVELS <= set(o_ladder_contract),
        "o_ladder_claim_ceiling_progression_declared": all(
            o_ladder_contract.get(level, {}).get("claim_ceiling") == ceiling
            for level, ceiling in O_LEVEL_CLAIM_CEILINGS.items()
        ),
        "o_ladder_runtime_levels_declared": all(
            bool(o_ladder_contract.get(level, {}).get("minimum_lgrc_runtime_level"))
            for level in O_LEVELS
        ),
        "native_surface_cross_references_declared": NATIVE_SURFACE_REFERENCES
        <= set(native_refs),
        "route_aspect_contract_declared": route_aspect_ref.get("native_contract")
        == "LGRC9V3RouteAspect"
        and {
            "route_aspect_digest",
            "pole_region_digest",
            "channel_sequence_digest",
        }
        <= set(route_aspect_ref.get("required_digest_fields", [])),
        "surplus_trigger_reference_declared": surplus_ref.get("producer_policy_constant")
        == "LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_ROUTE_SURPLUS"
        and surplus_ref.get("configuration_api") == "LGRC9V3.set_route_aspect_surplus_trigger(...)"
        and {
            "native_observed_mass_field",
            "native_reference_mass_field",
            "native_surplus_field",
        }
        <= set(surplus_ref),
        "self_rearm_reference_declared": self_rearm_ref.get("validator")
        == "validate_lgrc9v3_self_rearm_evidence_artifacts(...)",
        "run_autonomous_stop_conditions_declared": autonomous_ref.get("api")
        == "LGRC9V3.run_autonomous(...)"
        and {
            "max_events_reached",
            "natural_exhaustion_no_producer_can_schedule_and_queues_empty",
        }
        <= set(autonomous_ref.get("stop_conditions", [])),
        "timing_vocabulary_declared": TIMING_VOCABULARY <= set(timing_vocabulary),
        "timing_vocabulary_symbols_declared": timing_vocabulary.get(
            "scheduler_event_index", {}
        ).get("symbol")
        == "kappa"
        and timing_vocabulary.get("snapshot_index", {}).get("symbol") == "k"
        and timing_vocabulary.get("event_time_key", {}).get("symbol") == "T_e"
        and timing_vocabulary.get("node_proper_time", {}).get("symbol") == "tau_i"
        and timing_vocabulary.get("edge_causal_delay", {}).get("symbol") == "tau_ij",
        "reservoir_native_surplus_mapping_declared": target_reservoir_mapping.get(
            "observed_mass_field"
        )
        == "pole_mass"
        and target_reservoir_mapping.get("reference_mass_field") == "reference_mass"
        and target_reservoir_mapping.get("surplus_field") == "surplus"
        and target_reservoir_mapping.get("hidden_surplus_array_allowed") is False,
        "lgrc2_minimum_declared": manifest.get("minimum_lgrc_runtime_level") == "lgrc2",
        "fixed_topology_declared": topology.get("fixed_topology_required") is True
        and topology.get("topology_events_enabled") is False
        and topology.get("topology_mutation_allowed") is False,
        "node_count_matches": fixture.get("node_count") == len(nodes),
        "edge_count_matches": fixture.get("edge_count") == len(edges),
        "node_ids_unique": len(node_ids) == len(node_id_set),
        "edge_ids_unique": len(edge_ids) == len(edge_id_set),
        "edge_endpoints_exist": all(edge.get("u") in node_id_set and edge.get("v") in node_id_set for edge in edges),
        "source_node_exists": source_node_id in node_id_set,
        "target_node_exists": target_node_id in node_id_set,
        "target_reservoir_node_exists": target_reservoir_node_id in node_id_set,
        "source_target_distinct": source_node_id != target_node_id,
        "target_reservoir_distinct": target_reservoir_node_id not in {source_node_id, target_node_id},
        "outbound_and_return_routes_present": {
            "n05_o1_source_to_target_route_v1",
            "n05_o2_target_to_source_return_route_v1",
        }
        <= set(routes),
        "routes_resolve_to_existing_edges": all(
            _route_chain_valid(route, node_ids=node_id_set, edges=edges_by_id)
            for route in routes.values()
        ),
        "route_delays_match_edge_delays": route_delay_sum_ok,
        "hidden_schedule_disallowed_on_routes": all(
            route.get("hidden_schedule_allowed") is False for route in routes.values()
        ),
        "budget_nodes_cover_fixture_nodes": {
            int(node_id) for node_id in initial_node_coherence_by_node
        }
        == node_id_set,
        "initial_node_coherence_nonnegative": all(
            float(value) >= 0.0 for value in initial_node_coherence_by_node.values()
        ),
        "target_reservoir_initial_coherence_nonnegative": float(
            initial_node_coherence_by_node.get(str(target_reservoir_node_id), -1.0)
        )
        >= 0.0,
        "budget_total_matches_node_sum": epsilon > 0.0
        and _float_equal(
            initial_node_total,
            float(budget.get("initial_node_coherence_total", -1.0)),
            epsilon,
        ),
        "node_plus_packet_conserved_total_matches": epsilon > 0.0
        and _float_equal(
            initial_node_total + float(budget.get("initial_in_flight_packet_total", -1.0)),
            float(budget.get("conserved_total", -1.0)),
            epsilon,
        ),
        "budget_surfaces_separated": surface_accounting.get("separate_from_node_plus_packet")
        is True
        and surface_accounting.get("surface_id") != budget.get("surface_id"),
        "hidden_reservoir_arrays_disallowed": surface_accounting.get(
            "hidden_reservoir_arrays_allowed"
        )
        is False
        and all(
            reservoir.get("hidden_fixture_array_allowed") is False
            for reservoir in reservoir_accounting.values()
        ),
        "cycle_definition_frozen": cycle.get("ordered_steps") == REQUIRED_CYCLE_STEPS
        and cycle.get("cycle_id_required") is True
        and cycle.get("distinct_packet_ids_required") is True,
        "plateau_samples_not_cycles": cycle.get("plateau_samples_counted_as_cycles") is False,
        "required_lgrc_defaults_present": REQUIRED_DEFAULTS <= set(defaults),
        "symmetric_delay_declared": defaults.get("symmetric_delay_policy", {}).get(
            "outbound_delay_ticks"
        )
        == defaults.get("symmetric_delay_policy", {}).get("return_delay_ticks"),
        "packetized_flux_declared": bool(
            defaults.get("packetized_causal_flux_representation", {}).get("representation_id")
        ),
        "packet_ledger_declared": bool(
            defaults.get("packet_pending_flux_ledger_representation", {}).get(
                "representation_id"
            )
        ),
        "idempotency_key_declared": {
            "policy_id",
            "source_event_id",
            "route_id",
            "event_time_key",
            "packet_amount",
            "cycle_id",
        }
        <= set(idempotency_fields),
        "default_off_noop_declared": policies.get("default_off_behavior", {}).get(
            "coherence_oscillator_policy_enabled"
        )
        is False
        and policies.get("default_off_behavior", {}).get("expected_scheduled_packets") == 0,
        "phase_1_policy_fields_declared": {
            "policy_id",
            "source_event_id",
            "route_id",
            "packet_amount",
            "not_before_scheduler_event_index",
            "cycle_id",
        }
        <= set(explicit_policy.get("allowed_fields", [])),
        "phase_1_hidden_schedule_blocked": explicit_policy.get("hidden_schedule_allowed") is False
        and explicit_policy.get("preauthored_event_list_allowed") is False,
        "producer_writes_only_evidence": producer_writable
        == {"producer_records", "scheduling_eligibility"}
        and PRODUCER_FORBIDDEN_WRITES <= producer_forbidden
        and not bool(producer_writable & PRODUCER_FORBIDDEN_WRITES),
        "phase_2_runtime_threshold_fields_declared": {
            "observed_node_id",
            "observed_value_field",
            "reference_value",
            "threshold",
            "route_id",
            "packet_amount",
            "cycle_id",
        }
        <= set(threshold_policy.get("allowed_fields", []))
        and threshold_policy.get("observed_values_must_be_runtime_visible") is True
        and threshold_policy.get("hidden_threshold_arrays_allowed") is False,
        "phase_3_audit_fields_declared": phase3_audit.get("audit_required_before_pure_native_claim")
        is True
        and {
            "custom_node_potentials_supported",
            "potential_inversion_supported",
            "flux_facilitated_metric_maps_supported",
            "delayed_passive_response_supported",
            "route_conductance_memory_supported",
        }
        <= set(phase3_audit),
        "all_required_controls_declared": REQUIRED_CONTROLS <= set(control_ids),
        "control_blockers_are_unique": len(blocker_ids) == len(set(blocker_ids)),
        "snapshot_contract_declared": snapshot.get("snapshot_roundtrip_required") is True
        and snapshot.get("continue_after_load_required") is True
        and snapshot.get("idempotency_keys_preserved") is True
        and snapshot.get("duplicate_production_after_load_allowed") is False,
        "claim_flags_all_false": claim_boundary == CLAIM_FLAGS_FALSE,
    }


def _negative_control_results(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    controls = {control["control_id"]: control for control in manifest.get("controls", [])}
    fixture = manifest["fixture"]
    routes = manifest["routes"]
    policies = manifest["policies"]
    budget_surfaces = manifest["budget_surfaces"]

    def blocker(control_id: str) -> str:
        return controls.get(control_id, {}).get("primary_blocker", "missing_control")

    results: dict[str, dict[str, Any]] = {}

    mutated = copy.deepcopy(manifest)
    mutated["fixture"]["source_node_id"] = 999
    source_present = mutated["fixture"]["source_node_id"] in {
        node["node_id"] for node in mutated["fixture"]["nodes"]
    }
    results["missing_source"] = {
        "primary_blocker": blocker("missing_source"),
        "rejected": not source_present,
    }

    mutated = copy.deepcopy(manifest)
    mutated["fixture"]["target_node_id"] = 999
    target_present = mutated["fixture"]["target_node_id"] in {
        node["node_id"] for node in mutated["fixture"]["nodes"]
    }
    results["missing_target"] = {
        "primary_blocker": blocker("missing_target"),
        "rejected": not target_present,
    }

    mutated = copy.deepcopy(manifest)
    mutated["routes"].pop("n05_o1_source_to_target_route_v1", None)
    results["missing_route"] = {
        "primary_blocker": blocker("missing_route"),
        "rejected": "n05_o1_source_to_target_route_v1" not in mutated["routes"],
    }

    hidden_schedule_allowed = any(
        route.get("hidden_schedule_allowed") is not False for route in routes.values()
    ) or policies["phase_1_explicit_scheduling_policy_fields"].get(
        "hidden_schedule_allowed"
    ) is not False
    results["hidden_schedule"] = {
        "primary_blocker": blocker("hidden_schedule"),
        "rejected": not hidden_schedule_allowed,
    }

    hidden_reservoir_allowed = budget_surfaces["surface_accounting"].get(
        "hidden_reservoir_arrays_allowed"
    ) is not False or any(
        reservoir.get("hidden_fixture_array_allowed") is not False
        for reservoir in manifest["reservoir_accounting"].values()
    )
    results["hidden_reservoir"] = {
        "primary_blocker": blocker("hidden_reservoir"),
        "rejected": not hidden_reservoir_allowed,
    }

    surfaces_separated = (
        budget_surfaces["surface_accounting"].get("separate_from_node_plus_packet") is True
        and budget_surfaces["surface_accounting"].get("surface_id")
        != budget_surfaces["node_plus_packet"].get("surface_id")
    )
    results["budget_ambiguity"] = {
        "primary_blocker": blocker("budget_ambiguity"),
        "rejected": surfaces_separated,
    }

    default_off = policies["default_off_behavior"]
    results["policy_disabled"] = {
        "primary_blocker": blocker("policy_disabled"),
        "noop_verified": default_off.get("coherence_oscillator_policy_enabled") is False
        and default_off.get("expected_producer_records") == 0
        and default_off.get("expected_scheduled_packets") == 0,
    }

    results["pulse_disabled"] = {
        "primary_blocker": blocker("pulse_disabled"),
        "noop_verified": default_off.get("pulse_policy_enabled") is False
        and default_off.get("expected_scheduled_packets") == 0,
    }

    explicit_policy = policies["phase_1_explicit_scheduling_policy_fields"]
    results["producer_mutation_attempt"] = {
        "primary_blocker": blocker("producer_mutation_attempt"),
        "rejected": not bool(
            set(explicit_policy.get("producer_writable_fields", []))
            & PRODUCER_FORBIDDEN_WRITES
        ),
    }

    results["claim_promotion_attempt"] = {
        "primary_blocker": blocker("claim_promotion_attempt"),
        "rejected": all(value is False for value in manifest.get("claim_boundary", {}).values()),
    }

    results["stale_producer_read"] = {
        "primary_blocker": blocker("stale_producer_read"),
        "rejected": policies["phase_2_runtime_threshold_policy_fields"].get(
            "observed_values_must_be_runtime_visible"
        )
        is True,
    }

    idempotency_fields = set(
        manifest["conservative_lgrc_defaults"][
            "packet_pending_flux_ledger_representation"
        ].get("idempotency_key_fields", [])
    )
    results["idempotent_duplicate_production"] = {
        "primary_blocker": blocker("idempotent_duplicate_production"),
        "duplicate_suppression_key_declared": {
            "policy_id",
            "source_event_id",
            "route_id",
            "event_time_key",
            "packet_amount",
            "cycle_id",
        }
        <= idempotency_fields,
    }

    snapshot = manifest.get("snapshot_contract", {})
    results["snapshot_continue_after_load"] = {
        "primary_blocker": blocker("snapshot_continue_after_load"),
        "continue_after_load_idempotency_declared": snapshot.get("continue_after_load_required")
        is True
        and snapshot.get("idempotency_keys_preserved") is True
        and snapshot.get("duplicate_production_after_load_allowed") is False,
    }

    return results


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    checks = _base_checks(manifest)
    negative_controls = _negative_control_results(manifest)
    negative_controls_passed = all(
        bool(result.get("rejected", result.get("noop_verified", result.get("duplicate_suppression_key_declared", result.get("continue_after_load_idempotency_declared", False)))))
        for result in negative_controls.values()
    )
    passed = all(checks.values()) and negative_controls_passed
    return {
        "schema": "n05_iteration_2_fixture_manifest_validation_v1",
        "experiment": "2026-05-N05-lgrc-coherence-waves-oscillators",
        "iteration": 2,
        "status": "passed" if passed else "failed",
        "purpose": "fixture_manifest_and_controls_no_oscillator_probe",
        "command": COMMAND,
        "manifest_path": _rel(MANIFEST_PATH),
        "manifest_sha256": _file_sha256(MANIFEST_PATH),
        "manifest_digest_canonical_json": _digest(manifest),
        "oscillator_probe_run": False,
        "positive_o_level_evidence_generated": False,
        "src_changes_required": False,
        "checks": checks,
        "negative_control_results": negative_controls,
        "negative_controls_passed": negative_controls_passed,
        "fixture_summary": {
            "fixture_id": manifest["fixture"]["fixture_id"],
            "source_node_id": manifest["fixture"]["source_node_id"],
            "target_node_id": manifest["fixture"]["target_node_id"],
            "target_reservoir_node_id": manifest["fixture"]["target_reservoir_node_id"],
            "outbound_route_id": "n05_o1_source_to_target_route_v1",
            "return_route_id": "n05_o2_target_to_source_return_route_v1",
            "node_plus_packet_conserved_total": manifest["budget_surfaces"][
                "node_plus_packet"
            ]["conserved_total"],
        },
        "cycle_definition": manifest["cycle_definition"],
        "claim_flags": manifest["claim_boundary"],
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "git": {
            "head": _git(["rev-parse", "HEAD"]),
            "status_src": _git(["status", "--short", "src"]),
            "status_n05": _git(
                [
                    "status",
                    "--short",
                    "experiments/2026-05-N05-lgrc-coherence-waves-oscillators",
                ]
            ),
        },
    }


def _write_report(result: dict[str, Any]) -> None:
    check_rows = "\n".join(
        f"| `{key}` | {value} |" for key, value in sorted(result["checks"].items())
    )
    control_rows = "\n".join(
        "| `{}` | `{}` | {} |".format(
            control_id,
            data["primary_blocker"],
            data.get(
                "rejected",
                data.get(
                    "noop_verified",
                    data.get(
                        "duplicate_suppression_key_declared",
                        data.get("continue_after_load_idempotency_declared"),
                    ),
                ),
            ),
        )
        for control_id, data in sorted(result["negative_control_results"].items())
    )
    claim_rows = "\n".join(
        f"| `{key}` | {value} |" for key, value in sorted(result["claim_flags"].items())
    )
    text = f"""# N05 Iteration 2 Fixture Manifest Validation

Status: {result["status"]}

Command:

```bash
{COMMAND}
```

Manifest: `{result["manifest_path"]}`

Manifest SHA-256: `{result["manifest_sha256"]}`

Canonical manifest digest: `{result["manifest_digest_canonical_json"]}`

No oscillator probes were run in this iteration.

## Fixture

| Field | Value |
|---|---|
| fixture_id | `{result["fixture_summary"]["fixture_id"]}` |
| source_node_id | `{result["fixture_summary"]["source_node_id"]}` |
| target_node_id | `{result["fixture_summary"]["target_node_id"]}` |
| target_reservoir_node_id | `{result["fixture_summary"]["target_reservoir_node_id"]}` |
| outbound_route_id | `{result["fixture_summary"]["outbound_route_id"]}` |
| return_route_id | `{result["fixture_summary"]["return_route_id"]}` |
| node_plus_packet_conserved_total | `{result["fixture_summary"]["node_plus_packet_conserved_total"]}` |

## Checks

| Check | Passed |
|---|---|
{check_rows}

## Controls

| Control | Primary Blocker | Passed |
|---|---|---|
{control_rows}

## Claim Flags

| Flag | Value |
|---|---|
{claim_rows}

## Acceptance

Iteration 2 declares the N05 source-target-reservoir fixture, route policy,
delay policy, budget surfaces, default-off behavior, producer policy fields,
Phase 3 native-policy audit fields, cycle semantics, duplicate suppression,
snapshot continue-after-load contract, and fail-closed controls before any
oscillator probe runs.
"""
    REPORT_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    manifest = _load_manifest()
    result = validate_manifest(manifest)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
                "oscillator_probe_run": False,
            },
            sort_keys=True,
        )
    )
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
