"""Validate the N06 fixture manifest and control contract.

This script is experiment-local. It validates the Iteration 2 fixture,
context mapping, route-candidate templates, policy, budget, and controls before
any semantic route-choice probe runs. It does not import or mutate `src/pygrc`.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N06 = ROOT / "experiments/2026-05-N06-lgrc-semantic-route-choice"
MANIFEST_PATH = N06 / "configs/n06_fixture_manifest_v1.json"
OUTPUT_PATH = N06 / "outputs/n06_iteration_2_fixture_manifest_validation.json"
REPORT_PATH = N06 / "reports/n06_iteration_2_fixture_manifest_validation.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/"
    "validate_n06_fixture_manifest.py"
)


CLAIM_FLAGS_FALSE = {
    "semantic_choice_claim_allowed",
    "memory_or_trail_claim_allowed",
    "movement_claim_allowed",
    "agency_claim_allowed",
    "agentic_like_claim_allowed",
    "rc_identity_collapse_claim_allowed",
    "identity_acceptance_claim_allowed",
    "goal_proxy_regulation_claim_allowed",
    "locomotion_like_claim_allowed",
    "biological_claim_allowed",
    "ant_colony_claim_allowed",
    "unrestricted_movement_claim_allowed",
}

REQUIRED_CONTROLS = {
    "policy_disabled",
    "no_candidates",
    "unresolved_tie",
    "hidden_context",
    "hidden_route_preference",
    "preselected_sink",
    "experiment_side_if_else",
    "report_side_selection",
    "posthoc_threshold_change",
    "budget_mismatch",
    "order_inversion",
    "stale_candidate",
    "stale_context",
    "duplicate_arbitration",
    "producer_mutation",
    "claim_promotion",
}

PREFERRED_CONTEXT_MAPPING = {
    "score_surface": "candidate_score_components",
    "candidate_context_sources": "candidate_runtime_visible_inputs",
    "arbitration_context_sources": "arbitration_runtime_visible_inputs",
    "compatibility_gate": "native_score_components_with_threshold_interpretation",
}

NATIVE_TOPOLOGY_INTENTS = {"collapse", "reabsorb", "split", "merge"}
NATIVE_TOPOLOGY_EVENT_KIND = "lgrc9v3_causal_collapse"
NATIVE_POLICY = "score_ordered_topology_route_candidates"
ORDER_KEY = "score_desc_then_candidate_id"


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


def _route_chain_valid(
    route: Mapping[str, Any],
    *,
    node_ids: set[int],
    edges_by_id: Mapping[int, Mapping[str, Any]],
) -> bool:
    hops = route.get("route_hops", [])
    if not isinstance(hops, list) or not hops:
        return False
    previous = route.get("source_node_id")
    for hop in hops:
        edge_id = hop.get("edge_id")
        edge = edges_by_id.get(edge_id)
        source = hop.get("source_node_id")
        target = hop.get("target_node_id")
        if edge is None:
            return False
        if source not in node_ids or target not in node_ids:
            return False
        if previous != source:
            return False
        if {source, target} != {edge.get("u"), edge.get("v")}:
            return False
        if not bool(edge.get("route_eligible")):
            return False
        previous = target
    return previous == route.get("target_node_id")


def _score_templates_valid(context: Mapping[str, Any]) -> bool:
    states = context.get("context_states", {})
    if set(states) != {"context_a", "context_b"}:
        return False
    for state in states.values():
        templates = state.get("candidate_score_templates", {})
        if set(templates) != {"route_a", "route_b"}:
            return False
        for template in templates.values():
            components = template.get("candidate_score_components", {})
            score = float(template.get("candidate_route_score", -1.0))
            if not components:
                return False
            if abs(sum(float(value) for value in components.values()) - score) > 1e-12:
                return False
    return True


def _context_selects_expected_routes(context: Mapping[str, Any]) -> bool:
    states = context.get("context_states", {})
    selected: dict[str, str] = {}
    for state_id, state in states.items():
        templates = state.get("candidate_score_templates", {})
        if not templates:
            return False
        selected[state_id] = max(
            templates,
            key=lambda route_id: float(templates[route_id]["candidate_route_score"]),
        )
        if selected[state_id] != state.get("compatible_route_id"):
            return False
    return selected.get("context_a") == "route_a" and selected.get("context_b") == "route_b"


def _candidate_templates_valid(manifest: Mapping[str, Any]) -> bool:
    fixture = manifest.get("fixture", {})
    sink_ids = set(fixture.get("sink_node_ids", []))
    routes = manifest.get("routes", {})
    candidates = manifest.get("candidate_route_templates", [])
    budget_tolerance = float(
        manifest.get("arbitration_policy", {}).get("budget_tolerance", 0.0)
    )
    if len(candidates) != 2:
        return False
    seen_routes: set[str] = set()
    for candidate in candidates:
        route_id = candidate.get("route_id")
        route = routes.get(route_id)
        if route is None:
            return False
        seen_routes.add(str(route_id))
        selected_sink = candidate.get("candidate_selected_sink_id")
        losing_sinks = set(candidate.get("candidate_losing_sink_ids", []))
        competing = set(candidate.get("candidate_competing_sink_ids", []))
        lineage = candidate.get("candidate_lineage_transfer_map", {})
        transferred = {str(value) for value in candidate.get("candidate_transferred_node_ids", [])}
        lineage_semantics = candidate.get("lineage_transfer_map_semantics", {})
        edge_semantics = candidate.get("candidate_edge_set_semantics", {})
        reabsorption_prediction = candidate.get("candidate_reabsorption_prediction", {})
        budget = candidate.get("candidate_budget_prediction", {})
        if candidate.get("route_intent") not in NATIVE_TOPOLOGY_INTENTS:
            return False
        if candidate.get("candidate_topology_event_kind") != NATIVE_TOPOLOGY_EVENT_KIND:
            return False
        if selected_sink != route.get("target_node_id"):
            return False
        if selected_sink not in sink_ids or selected_sink not in competing:
            return False
        if losing_sinks != competing - {selected_sink}:
            return False
        if not transferred.issubset(set(str(key) for key in lineage)):
            return False
        if lineage_semantics.get("key_type") != "string_lineage_id":
            return False
        if lineage_semantics.get("value_type") != "string_lineage_id":
            return False
        if not all(isinstance(key, str) and isinstance(value, str) for key, value in lineage.items()):
            return False
        if not edge_semantics.get("candidate_source_edge_ids", "").startswith(
            "pre-collapse"
        ):
            return False
        if set(reabsorption_prediction.get("predicted_retired_node_ids", [])) != set(
            candidate.get("candidate_retired_node_ids", [])
        ):
            return False
        if set(reabsorption_prediction.get("predicted_retired_edge_ids", [])) != set(
            candidate.get("candidate_retired_edge_ids", [])
        ):
            return False
        if (
            reabsorption_prediction.get(
                "prediction_only_until_selected_topology_event_commits"
            )
            is not True
        ):
            return False
        if budget.get("budget_surface") != "node_plus_packet":
            return False
        if bool(budget.get("budget_surface_ambiguous")):
            return False
        if budget.get("budget_prediction_kind") != "template_expectation_not_runtime_measurement":
            return False
        if budget.get("budget_tolerance_source") != "arbitration_policy.budget_tolerance":
            return False
        if abs(float(budget.get("node_plus_packet_budget_error", 1.0))) > budget_tolerance:
            return False
    return seen_routes == {"route_a", "route_b"}


def _base_checks(manifest: Mapping[str, Any]) -> dict[str, bool]:
    fixture = manifest.get("fixture", {})
    nodes = fixture.get("nodes", [])
    edges = fixture.get("edges", [])
    routes = manifest.get("routes", {})
    context = manifest.get("context_affordance_surface", {})
    source_evidence = manifest.get("candidate_source_evidence", {})
    policy = manifest.get("arbitration_policy", {})
    window = manifest.get("arbitration_window", {})
    selected_event = manifest.get("selected_topology_event_behavior", {})
    default_off = manifest.get("default_off_policy", {})
    runtime_gate = manifest.get("native_runtime_gate", {})
    route_intent = manifest.get("route_intent_policy", {})
    producer_boundary = manifest.get("producer_boundary", {})
    claim_flags = manifest.get("claim_boundary", {}).get("claim_flags", {})
    controls = manifest.get("controls", [])
    context_score_mapping = context.get("context_to_score_component_mapping", {})

    node_ids = [node.get("node_id") for node in nodes]
    node_id_set = set(node_ids)
    edge_ids = [edge.get("edge_id") for edge in edges]
    edges_by_id = {edge.get("edge_id"): edge for edge in edges}
    route_values = list(routes.values())
    control_ids = [control.get("control_id") for control in controls]
    blocker_ids = [control.get("primary_blocker") for control in controls]
    selected_mapping = context.get("selected_mapping", {})

    return {
        "schema_matches": manifest.get("schema") == "n06_semantic_route_choice_fixture_manifest_v1",
        "no_route_choice_probe_run": manifest.get("route_choice_probe_run") is False,
        "no_positive_sc_evidence_generated": manifest.get("positive_sc_evidence_generated") is False,
        "runtime_family_declared": manifest.get("runtime_family") == "LGRC9V3",
        "native_lgrc3_gate_declared": runtime_gate.get("lgrc_runtime_level") == "lgrc3"
        and runtime_gate.get("causal_layer_mode") == "topology_changing_causal_history"
        and runtime_gate.get("native_lgrc_route_arbitration_policy_gate") == "policy != disabled",
        "native_dependencies_declared": all(
            bool(runtime_gate.get(key))
            for key in (
                "causal_topology_integration_allowed",
                "causal_pulse_substrate_surface_enabled",
                "causal_pulse_substrate_surface_validated",
                "causal_pulse_substrate_surface_lineage_transport_enabled",
                "causal_pulse_substrate_surface_lineage_transport_validated",
                "causal_pulse_substrate_surface_lineage_transport_supported",
                "causal_topology_state_reabsorption_enabled",
                "causal_topology_state_reabsorption_validated",
                "causal_topology_state_reabsorption_supported",
            )
        ),
        "native_dependency_chain_policy_declared": runtime_gate.get(
            "dependency_chain_policy"
        )
        == "enabled_validated_supported_chain_required_by_validate_lgrc9v3_causal_modes",
        "lgrc2_native_route_arbitration_blocked": runtime_gate.get(
            "lgrc2_native_route_arbitration_allowed"
        )
        is False,
        "default_off_policy_declared": default_off.get("disabled_policy") == "disabled"
        and default_off.get("disabled_requires_enabled_false") is True
        and default_off.get("native_lgrc_route_arbitration_enabled_when_disabled")
        is False,
        "default_off_no_emission_declared": all(
            default_off.get(key) is False
            for key in (
                "candidate_routes_emitted_when_disabled",
                "candidate_sets_emitted_when_disabled",
                "route_arbitration_records_emitted_when_disabled",
                "topology_events_committed_when_disabled",
                "packets_scheduled_when_disabled",
            )
        ),
        "node_count_matches": len(nodes) == fixture.get("node_count"),
        "edge_count_matches": len(edges) == fixture.get("edge_count"),
        "node_ids_unique": len(node_ids) == len(node_id_set),
        "edge_ids_unique": len(edge_ids) == len(set(edge_ids)),
        "source_branch_and_sinks_exist": {
            fixture.get("source_node_id"),
            fixture.get("branch_node_id"),
            *fixture.get("sink_node_ids", []),
        }.issubset(node_id_set),
        "context_nodes_exist": set(fixture.get("context_node_ids", [])).issubset(node_id_set),
        "edge_endpoints_exist": all(
            edge.get("u") in node_id_set and edge.get("v") in node_id_set
            for edge in edges
        ),
        "two_routes_declared": set(routes) == {"route_a", "route_b"},
        "routes_resolve_to_existing_edges": all(
            _route_chain_valid(route, node_ids=node_id_set, edges_by_id=edges_by_id)
            for route in route_values
        ),
        "context_surface_mapping_preferred_native": all(
            selected_mapping.get(key) == value
            for key, value in PREFERRED_CONTEXT_MAPPING.items()
        ),
        "context_states_a_b_declared": set(context.get("context_states", {}))
        == {"context_a", "context_b"},
        "context_relation_declared": context.get("context_relation")
        == "route matches active context/affordance",
        "context_runtime_visible": context.get("context_runtime_visible") is True,
        "hidden_context_sources_blocked": all(
            context.get(key) is False
            for key in (
                "hidden_context_sources_allowed",
                "experiment_side_if_else_allowed",
                "report_side_selection_allowed",
                "posthoc_threshold_change_allowed",
            )
        ),
        "candidate_scores_equal_component_sums": _score_templates_valid(context),
        "context_a_b_select_different_routes": _context_selects_expected_routes(context),
        "context_to_score_mapping_declared": {
            "context_match",
            "budget_validity",
            "lineage_ready",
        }.issubset(set(context_score_mapping))
        and context_score_mapping.get("context_match", {}).get("source_artifact_kind")
        == "LGRC9V3CausalPulseSubstrateSurfaceRow"
        and context_score_mapping.get("context_match", {}).get(
            "hidden_context_lookup_allowed"
        )
        is False,
        "candidate_source_sc1_required_fields_declared": set(
            source_evidence.get("sc1_required_fields", [])
        )
        == {"candidate_source_surface_digest"},
        "candidate_source_sc1_reabsorption_digest_conditional": (
            "candidate_source_topology_state_reabsorption_digest"
            in set(source_evidence.get("sc1_optional_fields", []))
        )
        and source_evidence.get("topology_state_reabsorption_digest_required_for_sc1")
        is False,
        "candidate_source_post_topology_fields_declared": {
            "candidate_source_surface_digest",
            "candidate_source_topology_state_reabsorption_digest",
        }.issubset(set(source_evidence.get("post_topology_candidate_required_fields", []))),
        "iteration_3_transition_criteria_declared": len(
            source_evidence.get("iteration_3_transition_criteria", [])
        )
        >= 5,
        "candidate_source_requires_native_surface": source_evidence.get("source_surface_kind")
        == "native_causal_pulse_substrate_surface",
        "candidate_source_reabsorption_digest_required_post_topology": source_evidence.get(
            "topology_state_reabsorption_digest_required_for_post_topology_candidates"
        )
        is True,
        "candidate_templates_valid": _candidate_templates_valid(manifest),
        "redirect_caveat_declared": route_intent.get(
            "redirect_is_not_topology_mutating_movement_evidence_by_itself"
        )
        is True,
        "native_route_intents_declared": set(
            route_intent.get("native_topology_changing_intents", [])
        )
        == NATIVE_TOPOLOGY_INTENTS,
        "selected_topology_event_behavior_declared": selected_event.get(
            "selection_authorizes_exactly_one_candidate"
        )
        is True
        and selected_event.get(
            "selected_topology_event_artifact_expected_when_native_validator_replays_selection"
        )
        is True,
        "producer_scheduling_deferred": selected_event.get(
            "producer_scheduling_deferred_until_post_selection_lanes"
        )
        is True,
        "arbitration_policy_declared": policy.get("native_lgrc_route_arbitration_policy")
        == NATIVE_POLICY
        and policy.get("native_lgrc_route_arbitration_policy_id")
        == "n06_score_ordered_context_policy_v1",
        "candidate_ordering_declared": policy.get("candidate_set_order_key") == ORDER_KEY,
        "tie_policy_fail_closed": policy.get("unresolved_tie_policy") == "fail_closed",
        "tiebreaker_fields_serialized": {
            "candidate_set.unresolved_tie_policy",
            "candidate_set.candidate_set_order_key",
            "candidate.candidate_order_key",
            "candidate.candidate_route_digest",
        }.issubset(set(policy.get("declared_tiebreaker_fields", []))),
        "budget_tolerance_declared": float(policy.get("budget_tolerance", -1.0)) == 1e-9,
        "score_invariant_declared": policy.get("score_component_invariant")
        == "candidate_route_score == sum(candidate_score_components)",
        "arbitration_window_declared": window.get("arbitration_window_id")
        == "n06_window_context_state_candidate_emission_v1"
        and bool(window.get("candidate_completeness_rule")),
        "arbitration_window_artifact_mapping_declared": window.get(
            "boundary_artifact_mapping", {}
        ).get("start_event_artifact_kind")
        == "LGRC9V3CausalPulseSubstrateSurfaceRow"
        and window.get("boundary_artifact_mapping", {}).get("end_event_artifact_kind")
        == "LGRC9V3NativeRouteCandidateSetRecord",
        "arbitration_timing_declared": window.get("timing", {}).get("causal_epoch")
        == "n06_epoch_context_candidate_emission_v1"
        and window.get("timing", {}).get("checkpoint_index") == 0
        and window.get("timing", {})
        .get("scheduler_event_index_range", {})
        .get("candidate_records_before_candidate_set")
        is True,
        "candidate_set_frozen_before_arbitration": window.get(
            "candidate_set_is_frozen_before_arbitration"
        )
        is True,
        "sc1_selection_non_actions_declared": selected_event.get(
            "sc1_behavior", {}
        ).get("route_arbitration_record_emitted")
        is False
        and selected_event.get("sc1_behavior", {}).get("selected_topology_event_committed")
        is False
        and selected_event.get("sc1_behavior", {}).get(
            "topology_state_reabsorption_record_required"
        )
        is False,
        "producer_boundary_declared": producer_boundary.get("producer_schedules_only")
        is True
        and producer_boundary.get("step_mutates_packet_state") is True,
        "producer_forbidden_writes_declared": {
            "active_node_coherence",
            "packet_ledger",
            "topology",
            "claim_flags",
        }.issubset(set(producer_boundary.get("producer_forbidden_writes", []))),
        "all_required_controls_declared": REQUIRED_CONTROLS.issubset(set(control_ids)),
        "control_blockers_are_distinct": len(blocker_ids) == len(set(blocker_ids)),
        "claim_flags_complete": CLAIM_FLAGS_FALSE.issubset(set(claim_flags)),
        "claim_flags_all_false": all(value is False for value in claim_flags.values()),
        "route_arbitration_alone_not_semantic_choice": manifest.get(
            "claim_boundary", {}
        ).get("route_arbitration_alone_is_semantic_choice")
        is False,
    }


def _write_report(result: Mapping[str, Any]) -> None:
    manifest = result["manifest"]
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    controls = "\n".join(
        (
            f"| `{control['control_id']}` | `{control['primary_blocker']}` | "
            f"`{control['control_id'] in result['required_controls']}` |"
        )
        for control in manifest["controls"]
    )
    claims = "\n".join(
        f"| `{key}` | `{value}` |"
        for key, value in sorted(manifest["claim_boundary"]["claim_flags"].items())
    )
    transition = "\n".join(
        f"- {item}" for item in manifest["candidate_source_evidence"][
            "iteration_3_transition_criteria"
        ]
    )
    context_mapping = json.dumps(
        manifest["context_affordance_surface"]["context_to_score_component_mapping"],
        indent=2,
        sort_keys=True,
    )
    window_mapping = json.dumps(
        {
            "boundary_artifact_mapping": manifest["arbitration_window"][
                "boundary_artifact_mapping"
            ],
            "timing": manifest["arbitration_window"]["timing"],
        },
        indent=2,
        sort_keys=True,
    )
    score_rows: list[str] = []
    for state_id, state in manifest["context_affordance_surface"][
        "context_states"
    ].items():
        for route_id, template in state["candidate_score_templates"].items():
            score_rows.append(
                "| `{}` | `{}` | `{}` | `{}` |".format(
                    state_id,
                    route_id,
                    template["candidate_route_score"],
                    sum(template["candidate_score_components"].values()),
                )
            )
    REPORT_PATH.write_text(
        f"""# N06 Iteration 2 Fixture Manifest Validation

Status: {result['status']}

Command:

```bash
{COMMAND}
```

Manifest: `{result['manifest_path']}`

Manifest SHA-256: `{result['manifest_sha256']}`

Canonical manifest digest: `{result['manifest_digest']}`

No semantic route-choice probes were run in this iteration.

## Fixture

| Field | Value |
|---|---|
| fixture_id | `{manifest['fixture']['fixture_id']}` |
| source_node_id | `{manifest['fixture']['source_node_id']}` |
| branch_node_id | `{manifest['fixture']['branch_node_id']}` |
| sink_node_ids | `{manifest['fixture']['sink_node_ids']}` |
| context_node_ids | `{manifest['fixture']['context_node_ids']}` |
| native policy | `{manifest['arbitration_policy']['native_lgrc_route_arbitration_policy']}` |
| order key | `{manifest['arbitration_policy']['candidate_set_order_key']}` |
| unresolved tie policy | `{manifest['arbitration_policy']['unresolved_tie_policy']}` |

## Context Score Templates

| Context | Route | Score | Component Sum |
|---|---|---:|---:|
{chr(10).join(score_rows)}

Context-to-score derivation:

```json
{context_mapping}
```

## Iteration 3 Transition Criteria

{transition}

SC1 candidate exposure does not require a topology-state reabsorption digest;
that digest is required only for post-topology candidate sources.

## Arbitration Window

```json
{window_mapping}
```

## Checks

| Check | Passed |
|---|---|
{checks}

## Controls

| Control | Primary Blocker | Required |
|---|---|---|
{controls}

## Claim Flags

| Flag | Value |
|---|---|
{claims}

## Acceptance

Iteration 2 declares the N06 source-plus-two-routes fixture, native
context-score mapping, context A/B states, arbitration window, candidate source
fields, route intents, selected-topology-event behavior, deterministic ordering,
budget tolerance, default-off policy, producer boundary, and fail-closed
controls before any semantic route-choice probe runs.
""",
        encoding="utf-8",
    )


def main() -> None:
    manifest = _load_manifest()
    checks = _base_checks(manifest)
    result: dict[str, Any] = {
        "schema": "n06_semantic_route_choice_report_v1",
        "run_id": "n06_iteration_2_fixture_manifest_validation_v1",
        "iteration": 2,
        "status": "passed",
        "command": COMMAND,
        "manifest_path": _rel(MANIFEST_PATH),
        "manifest_sha256": _file_sha256(MANIFEST_PATH),
        "manifest_digest": _digest(manifest),
        "runtime_family": "LGRC9V3",
        "route_choice_probe_run": False,
        "positive_sc_evidence_generated": False,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "git": {
            "head": _git(["rev-parse", "HEAD"]),
            "status_short": _git(["status", "--short"]),
            "status_short_src": _git(["status", "--short", "src"]),
        },
        "manifest": manifest,
        "checks": checks,
        "required_controls": sorted(REQUIRED_CONTROLS),
        "artifact_digests": {
            "manifest_digest": _digest(manifest),
            "checks_digest": _digest(checks),
            "controls_digest": _digest(manifest.get("controls", [])),
            "claim_boundary_digest": _digest(manifest.get("claim_boundary", {})),
        },
        "acceptance": {
            "manifest_valid": all(checks.values()),
            "no_route_choice_probe_run": True,
            "claim_flags_all_false": checks.get("claim_flags_all_false", False),
            "controls_declared": checks.get("all_required_controls_declared", False),
            "context_mapping_declared": checks.get(
                "context_surface_mapping_preferred_native", False
            ),
        },
    }
    if not all(result["acceptance"].values()):
        result["status"] = "failed"
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "route_choice_probe_run": result["route_choice_probe_run"],
                "manifest": result["manifest_path"],
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
                "checks_passed": all(checks.values()),
                "controls_declared": result["acceptance"]["controls_declared"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
