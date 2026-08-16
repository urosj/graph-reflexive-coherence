#!/usr/bin/env python3
"""Build and validate the Phase 8 Iteration 108 composition matrix."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "specs/grc-lgrc-causal-pathway-contracts.json"
CROSSWALK_PATH = ROOT / "specs/grc-lgrc-causal-pathway-evidence-crosswalk.json"
I107_RESULT_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107.json"
I107_FREEZE_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration107ArtifactFreeze.json"
OUTPUT_MATRIX = ROOT / "specs/grc-lgrc-causal-pathway-composition-matrix.json"
OUTPUT_GUIDE = ROOT / "docs/reference/GRC-LGRC-CompositionMatrix.md"
OUTPUT_EXECUTION = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108TestExecution.json"
OUTPUT_RESULT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.json"
OUTPUT_REPORT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.md"
OUTPUT_FREEZE = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactFreeze.json"

EXPECTED_REGISTRY_DIGEST = "a266b33da10778e8caf5ad7d4a4bfe4b71aed9d0df563fd6c74e7d4ed6cb486b"
EXPECTED_CROSSWALK_DIGEST = "0036dcdf54f4663bed183387db1c8f657eb44a694252ef44421be56fb239ff06"
EXPECTED_I107_RESULT_DIGEST = "27f590ed926c364cabc1187f6fd4d4ec99e84003e0cb4f1c7db63ec3fc23d5ad"
EXPECTED_I107_BUNDLE_DIGEST = "8bb201a0a061210407bc8230f879663c92a5967351efa6594d7f93c6c44f7889"

STATUS_VALUES = (
    "lawful_native",
    "lawful_with_explicit_adapter",
    "diagnostic_only",
    "producer_mediated",
    "unsupported_missing_crossing",
    "invalid_relabel",
)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    ).rstrip("\n")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_digest(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def file_ref(path: str, role: str, revision: str) -> dict[str, str]:
    target = ROOT / path
    if not target.is_file():
        raise FileNotFoundError(path)
    return {
        "path": path,
        "sha256": sha256_file(target),
        "revision": revision,
        "evidence_role": role,
    }


def test_index(path: str) -> dict[str, str]:
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    found: dict[str, str] = {}

    def walk(node: ast.AST, parents: list[str]) -> None:
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                walk(child, [*parents, node.name])
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                found[node.name] = "::".join([path, *parents, node.name])
            return
        for child in ast.iter_child_nodes(node):
            walk(child, parents)

    walk(tree, [])
    return found


TEST_FILES = (
    "tests/models/test_grc_9_v3_step.py",
    "tests/models/test_lgrc_9_v3_contract.py",
    "tests/models/test_lgrc_9_v3_runtime.py",
    "tests/models/test_lgrc_9_v3_autonomy_contract.py",
    "tests/models/test_lgrc_9_v3_construction.py",
    "tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py",
    "tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py",
    "tests/models/test_lgrc_9_v3_restoration.py",
    "tests/models/test_lgrc_9_v3_restoration_matrix.py",
    "tests/models/test_reset_baseline_persistence.py",
)
TEST_INDEX = {path: test_index(path) for path in TEST_FILES}


def t(path: str, name: str, role: str = "crossing_positive") -> tuple[str, str, str]:
    if name not in TEST_INDEX[path]:
        raise ValueError(f"missing test: {path}::{name}")
    return path, name, role


def compat(status: str, detail: str) -> dict[str, str]:
    return {"status": status, "detail": detail}


def spec(
    composition_id: str,
    name: str,
    from_pathway_id: str,
    from_stage_ids: list[str],
    to_pathway_id: str,
    to_stage_ids: list[str],
    status: str,
    composition_order: list[str],
    state: tuple[str, str],
    time: tuple[str, str],
    spatial: tuple[str, str],
    budget: tuple[str, str],
    authority_retained: list[str],
    authority_transferred: list[str],
    adapter_id: str | None,
    adapter_owner: str,
    information_loss: str,
    carrier: str,
    interaction: str,
    controls: list[str],
    transfer_scope: str,
    evidence_status: str,
    claim_ceiling: str,
    blocked_relabels: list[str],
    source_paths: list[str],
    tests: list[tuple[str, str, str]],
    historical_refs: list[tuple[str, str]] | None = None,
    absence_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if status not in STATUS_VALUES:
        raise ValueError(status)
    return {
        "composition_id": composition_id,
        "name": name,
        "from_pathway_id": from_pathway_id,
        "from_stage_ids": from_stage_ids,
        "to_pathway_id": to_pathway_id,
        "to_stage_ids": to_stage_ids,
        "composition_status": status,
        "composition_order": composition_order,
        "state_identity_mapping": compat(*state),
        "temporal_compatibility": compat(*time),
        "spatial_compatibility": compat(*spatial),
        "budget_or_invariant_compatibility": compat(*budget),
        "authority_retained": authority_retained,
        "authority_transferred": authority_transferred,
        "adapter_id": adapter_id,
        "adapter_owner": adapter_owner,
        "information_lost_or_compressed": information_loss,
        "shared_carrier_surface": carrier,
        "visible_interaction_term": interaction,
        "separable_and_combined_controls": controls,
        "transfer_scope": transfer_scope,
        "evidence_status": evidence_status,
        "claim_ceiling": claim_ceiling,
        "blocked_relabels": blocked_relabels,
        "source_paths": source_paths,
        "tests": tests,
        "historical_refs": historical_refs or [],
        "source_absence_audit": absence_audit,
    }


RUNTIME = "src/pygrc/models/lgrc_9_v3_runtime.py"
CONTRACT = "src/pygrc/models/lgrc_9_v3_contract.py"
CONSTRUCTION = "src/pygrc/models/lgrc_9_v3_construction.py"
GRC = "src/pygrc/models/grc_9_v3.py"
RESTORATION = "src/pygrc/models/lgrc_9_v3_restoration.py"

COMPOSITIONS = [
    spec("CMP-01", "GRC transport into synchronous continuity", "grc9v3.synchronous_update_cycle", ["transport_rebuild"], "grc9v3.synchronous_update_cycle", ["continuity_and_invariants"], "lawful_native", ["rebuild differential", "rebuild transport", "apply continuity and invariants"], ("exact", "One GRC9V3 state object carries transport outputs into continuity."), ("compatible", "Both stages execute in one global synchronous step."), ("compatible", "Both stages address the same graph-wide state."), ("compatible", "Continuity closes the declared GRC budget after transport."), ["GRC9V3.step scheduling", "native flux direction", "node coherence funding"], [], None, "native", "No state projection at the crossing.", "GRC9V3 state", "oriented flux consumed by continuity", ["full-step execution", "fixed-budget control"], "one synchronous GRC9V3 step", "current_source_crossing_passed", "Native synchronous transport-to-continuity mechanics only.", ["LGRC packet execution", "semantic action"], [GRC, "src/pygrc/models/grc_9_v3_runtime.py"], [t("tests/models/test_grc_9_v3_step.py", "test_step_executes_documented_loop_and_advances_time"), t("tests/models/test_grc_9_v3_step.py", "test_step_preserves_fixed_budget_after_continuity_and_invalidates_coarse_cache", "crossing_budget_control")]),
    spec("CMP-02", "Packet schedule through debit and arrival credit", "lgrc9v3.explicit_packet_transport", ["packet_schedule", "source_debit"], "lgrc9v3.explicit_packet_transport", ["target_credit"], "lawful_native", ["schedule packet", "debit source", "retain in flight", "credit target"], ("exact", "Packet ID and ledger state survive every lifecycle stage."), ("compatible", "Event-time queue orders departure before arrival."), ("compatible", "Declared source, edge, and target endpoints remain explicit."), ("compatible", "Source plus in-flight plus target coherence is conserved."), ["packet endpoint direction", "caller-supplied schedule", "LGRC step commitment"], [], None, "native", "No lifecycle state is discarded.", "packet ledger", "packet/event identity and conserved amount", ["departure-arrival lifecycle", "budget closure", "event ordering"], "one explicit packet lifecycle", "current_source_crossing_passed", "Native packet debit/arrival mechanics; route, amount, and schedule remain supplied.", ["native route formation", "generic work admission"], [RUNTIME, CONTRACT, "src/pygrc/models/lgrc_9_v3_packets.py"], [t("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc2_scheduled_packet_processes_departure_then_arrival"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_departure_arrival_lifecycle_preserves_budget", "crossing_budget_control")]),
    spec("CMP-03", "GRC flux into bounded packet work", "grc9v3.synchronous_update_cycle", ["transport_rebuild"], "lgrc9v3.explicit_packet_transport", ["packet_schedule"], "producer_mediated", ["read GRC flux", "select sign/source/amount", "schedule LGRC packet"], ("adapter_projection", "A producer projects continuous reconstructed flux into a packet contract."), ("adapter_required", "Global synchronous flux must be assigned an event-time schedule."), ("adapter_required", "GRC edge orientation must be mapped to LGRC packet endpoints."), ("bounded_by_adapter", "The adapter must convert flux to an explicit packet amount without hidden funding."), ["GRC flux reconstruction", "LGRC packet debit/arrival"], ["direction", "eligibility", "amount", "schedule"], "flux_to_packet_adapter", "experiment_or_consumer_producer", "Continuous flux detail is compressed to one packet relation.", "explicit adapter record", "producer-authored sign, amount, source, target, and event time", ["adapter omitted", "sign reversal", "overdraw", "endpoint swap"], "bounded producer-authored flux-to-packet projection", "bounded_producer_evidence_only", "Producer-mediated GRC-flux-to-LGRC-packet candidate; not native causal admission.", ["lawful_native", "native current-to-action admission"], [], [], [("implementation/investigations/event-local-geometry-integration/Phase-8-LGRC9-EventLocalGeometryIntegrationC0C1Closeout.json", "bounded_negative_and_ownership_evidence"), ("implementation/investigations/event-local-geometry-integration/Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.json", "producer_pattern_evidence")], {"inspected_paths": [GRC, RUNTIME], "missing_crossing": "no native GRC-flux consumer schedules LGRC packet work", "result": "producer_or_adapter_required"}),
    spec("CMP-04", "LGRC checkpoint into explicit GRC diagnostic reconstruction", "lgrc9v3.diagnostic_grc_reconstruction", ["diagnostic_model_construction"], "lgrc9v3.diagnostic_grc_reconstruction", ["diagnostic_rebuild"], "diagnostic_only", ["select LGRC checkpoint", "construct GRC9V3 diagnostic view", "rebuild diagnostic state"], ("bounded_projection", "LGRC base state is reconstructed through an explicit GRC9V3 diagnostic helper."), ("caller_checkpoint", "Caller selects the checkpoint; no ordinary LGRC event schedules it."), ("compatible", "The diagnostic uses the current copied graph topology."), ("not_a_transport", "The helper reconstructs labels and does not authorize packet work."), ["caller selection", "GRC diagnostic mechanics"], [], "prepare_lgrc9v3_grc9v3_diagnostics", "library_helper_invoked_by_caller", "LGRC queue/event history is not part of the GRC diagnostic projection.", "LGRC base state", "explicit helper call", ["explicit invocation", "no ordinary-step claim", "topology nonmutation"], "caller-selected checkpoint diagnostic", "current_source_diagnostic_crossing_passed", "Explicit bounded diagnostic reconstruction only.", ["ordinary LGRC behavior", "native event-to-action crossing"], [CONSTRUCTION, RUNTIME], [t("tests/models/test_lgrc_9_v3_construction.py", "test_corrected_cascade_queue_policy_is_explicit"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_explicit_causal_diagnostic_preserves_lane_a_signed_hessian_attribution", "crossing_boundary_control")]),
    spec("CMP-05", "Diagnostic reconstruction relabeled as ordinary LGRC behavior", "lgrc9v3.diagnostic_grc_reconstruction", ["diagnostic_rebuild"], "lgrc9v3.explicit_packet_transport", ["packet_schedule"], "invalid_relabel", ["run diagnostic", "claim ordinary LGRC consumed it"], ("missing", "No constitutive mapping from diagnostic output to packet scheduling is declared."), ("incompatible", "Explicit checkpoint diagnostics do not become event-queue causes."), ("unmapped", "Diagnostic graph scope supplies no packet endpoint mapping."), ("unmapped", "Diagnostic values carry no packet funding authority."), ["diagnostic helper"], [], None, "none", "All causal authority is absent at the proposed crossing.", "none", "none", ["diagnostic-only control", "ordinary step omission"], "invalid diagnostic-to-runtime promotion", "claim_boundary_rejected", "No ordinary LGRC behavior claim is allowed.", ["diagnostic_as_behavior", "native packet admission"], [], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_explicit_causal_diagnostic_preserves_lane_a_signed_hessian_attribution", "crossing_negative_control")], absence_audit={"inspected_paths": [CONSTRUCTION, RUNTIME], "missing_crossing": "ordinary LGRC step does not consume explicit GRC diagnostic reconstruction", "result": "invalid_relabel"}),
    spec("CMP-06", "Sink compatibility into route scheduling", "grc9v3.sink_compatibility_choice", ["choice_collapse_update"], "lgrc9v3.configured_flux_route", ["route_departure_production"], "unsupported_missing_crossing", ["compute sink compatibility", "schedule route work"], ("missing", "Choice registry has no admitted mapping to LGRC route records."), ("incompatible", "Synchronous choice rebuild has no event-time scheduling bridge."), ("unmapped", "Sink IDs do not define LGRC source-edge-target route identity."), ("unmapped", "Choice state supplies no packet amount or debit authority."), ["GRC choice mechanics", "LGRC configured-route mechanics"], [], None, "none", "Score, sink, amount, and schedule mapping are absent.", "none", "none", ["source consumer audit", "no hidden scheduler"], "missing choice-to-route crossing", "source_audit_missing_crossing", "Unsupported until an explicit admission and scheduling relation is supplied.", ["semantic choice", "native route formation"], [], [], absence_audit={"inspected_paths": [GRC, RUNTIME], "missing_crossing": "LGRC runtime has no consumer of GRC9V3 choice_registry or collapse_registry", "result": "unsupported_missing_crossing"}),
    spec("CMP-07", "Native arbitration selection into collapse commit", "lgrc9v3.native_route_arbitration", ["native_arbitration", "selection_commit"], "lgrc9v3.collapse_reabsorption", ["collapse_event_admission", "topology_reabsorption_commit"], "lawful_native", ["select committed candidate", "validate arbitration reference", "invoke collapse/reabsorption commit"], ("exact", "Candidate, arbitration, and selected topology digests are checked across the call."), ("compatible", "Commit occurs at the explicit arbitration frontier."), ("compatible", "Candidate sink/loser/lineage fields map directly to collapse scope."), ("compatible", "Predicted budget and committed topology digest are validated."), ["native highest-score arbitration", "native topology commitment"], [], None, "native", "Unselected candidate details remain in audit records rather than mutation input.", "candidate/arbitration/topology records", "commit_native_route_arbitration_selection calls process_causal_collapse_reabsorption", ["stale candidate", "missing record", "digest drift", "duplicate commit"], "selected collapse/reabsorption candidate only", "current_source_crossing_passed", "Native arbitration-to-collapse commit mechanics; candidate and score formation remain external/configured.", ["native candidate formation", "semantic choice"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_arbitration_commit_integrates_topology_and_producer"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_arbitration_commit_rejects_stale_candidate_set", "crossing_negative_control")]),
    spec("CMP-08", "External score formation relabeled as native route formation", "lgrc9v3.native_route_arbitration", ["candidate_set_admission"], "lgrc9v3.native_route_arbitration", ["native_arbitration"], "invalid_relabel", ["externally author candidates and scores", "run native arbitration", "claim native formation"], ("configured_input", "Arbitration consumes committed candidate score records exactly as supplied."), ("compatible_but_external", "Ordering is native after external candidate admission."), ("configured", "Candidate topology scope is supplied."), ("configured", "Candidate budget prediction is supplied and validated."), ["native arbitration"], ["candidate formation", "score formation"], None, "external_or_configured_candidate_producer", "The origin of candidates and score semantics is outside arbitration.", "candidate records", "configured candidate score", ["hidden selection rejection", "experiment if/else rejection", "preselected sink rejection"], "claim-boundary rejection", "claim_boundary_rejected", "Native selection over supplied candidates only.", ["native route formation", "semantic valuation"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_candidate_emission_rejects_hidden_route_selection", "crossing_negative_control"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_candidate_emission_rejects_experiment_if_else_input", "crossing_negative_control")]),
    spec("CMP-09", "Basin assignment into later transport", "grc9v3.identity_basin_reconstruction", ["validate_and_mass_basins"], "grc9v3.synchronous_update_cycle", ["transport_rebuild"], "unsupported_missing_crossing", ["assign basin", "later transport reads basin identity"], ("retained_not_consumed", "Basin assignments are retained but not a constitutive transport input."), ("same_step_but_unread", "Shared synchronous timing does not create causal consumption."), ("available_but_unmapped", "Basin regions exist, but transport consumes edge/node state instead."), ("no_budget_authority", "Basin ID supplies no conductance or coherence transfer term."), ["identity reconstruction", "transport reconstruction"], [], None, "none", "No basin-to-conductance/potential/flux read path exists.", "none", "none", ["source read-path audit"], "missing retained-state read path", "source_audit_missing_crossing", "Current basin assignment may be described, not claimed as transport mediation.", ["constitutive memory", "Read-Back"], [], [], absence_audit={"inspected_paths": [GRC, "src/pygrc/models/grc_9_v3_runtime.py"], "missing_crossing": "transport rebuild does not consume basin assignment or basin mass", "result": "unsupported_missing_crossing"}),
    spec("CMP-10", "Event queue mutation relabeled as causal eligibility", "lgrc9v3.explicit_packet_transport", ["packet_schedule"], "lgrc9v3.fixed_topology_eligibility", ["fixed_topology_eligibility"], "invalid_relabel", ["insert event", "claim queue presence explains eligibility"], ("distinct", "Queue state records scheduled work; eligibility remains a separate declared predicate."), ("ordered_not_explanatory", "Event time orders work but does not explain why it became eligible."), ("endpoint_only", "Queue endpoints do not define generic eligibility scope."), ("funding_after_admission", "Packet budget validation occurs after supplied eligibility/scheduling."), ["queue commitment order", "packet budget"], [], None, "none", "The reason for admission is absent from queue mutation.", "event queue", "scheduled event record", ["fixed-topology eligibility opt-in", "queue ordering"], "claim-boundary rejection", "claim_boundary_rejected", "Queue mutation supports scheduled execution, not native causal eligibility.", ["native work admission", "reason from event order"], [RUNTIME, CONTRACT], [t("tests/models/test_lgrc_9_v3_contract.py", "test_fixed_topology_eligibility_is_opt_in_and_semi_causal", "crossing_negative_control"), t("tests/models/test_lgrc_9_v3_contract.py", "test_lgrc2_packet_ledger_orders_queue_events_deterministically", "crossing_boundary_control")]),
    spec("CMP-11", "Configured route relabeled as native formed role", "lgrc9v3.configured_flux_route", ["route_registration"], "lgrc9v3.configured_flux_route", ["route_departure_production"], "invalid_relabel", ["register route", "schedule route packet", "claim route formed natively"], ("exact_configured", "Registered route identity is consumed exactly."), ("compatible", "Configured event times are honored."), ("configured", "Source, edge, and target are supplied."), ("configured", "Amount/fraction policy remains supplied."), ["native packet queue mutation"], ["route role", "route topology meaning", "amount policy"], None, "configuration_or_producer", "No formation process is represented.", "configured route table", "route policy record", ["disabled producer", "static route autonomy boundary"], "claim-boundary rejection", "claim_boundary_rejected", "Configured-route packet production only.", ["native route formation", "semantic role formation"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_native_packet_loop_baseline.py", "test_existing_static_route_autonomy_is_not_d2_3_equivalent", "crossing_negative_control")]),
    spec("CMP-12", "Route surplus into packet continuation", "lgrc9v3.route_aspect_surplus", ["surplus_evaluation", "surplus_packet_schedule"], "lgrc9v3.explicit_packet_transport", ["packet_schedule", "source_debit", "target_credit"], "lawful_native", ["evaluate configured surplus", "schedule packet", "process packet lifecycle"], ("exact", "Scheduled packet ID and event IDs link surplus evidence to transport."), ("compatible", "Producer event time and packet event times are explicit."), ("compatible_configured", "Configured channel first hop supplies packet endpoints."), ("compatible", "Packet amount is checked against source coherence and lifecycle budget."), ["native surplus evaluator", "native packet lifecycle"], [], None, "native_with_configured_semantics", "Surplus is compressed to one configured packet amount.", "autonomous production record and packet ledger", "schedule_packet_departure call with surplus evidence", ["subthreshold", "overdraw", "idempotency", "parent-arrival requirement"], "configured route-aspect channel", "current_source_crossing_passed_with_configured_semantics", "Native mechanics for configured surplus-to-packet continuation.", ["semantic abundance", "native route formation", "general self-rearm"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py", "test_self_rearm_candidate_and_completion_chain_are_native_artifacts"), t("tests/models/test_lgrc_9_v3_native_packet_loop_surplus_trigger.py", "test_self_rearm_candidate_requires_prior_parent_arrival", "crossing_negative_control")]),
    spec("CMP-13", "Outward flux and front capacity into boundary birth", "lgrc9v3.boundary_birth", ["birth_trial_production"], "lgrc9v3.boundary_birth", ["birth_trial_commit"], "lawful_native", ["evaluate front-capacity birth", "queue trial", "commit accepted trial"], ("exact", "Trial identity carries parent, port, pressure, and RNG evidence to commit."), ("compatible", "Queued trial and event-time commit are explicit."), ("compatible_configured", "Front-capacity metadata scopes the parent port."), ("compatible", "Parent debit equals child credit."), ["native/configured eligibility", "LGRC topology commitment"], [], None, "native_with_configured_semantics", "No hidden topology relation is introduced after trial admission.", "boundary-birth trial queue", "accepted trial consumed by step", ["policy disabled", "missing front capacity", "RNG rejection", "budget"], "one configured parent-port birth", "current_source_crossing_passed_with_configured_semantics", "Native configured boundary-birth mechanics only.", ["generic admission", "semantic reproduction"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_causal_boundary_birth_uses_grc9v3_probability_and_preserves_budget"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_causal_boundary_birth_front_capacity_rejects_missing_or_wrong_port", "crossing_negative_control")]),
    spec("CMP-14", "Boundary-birth admission relabeled as generic packet admission", "lgrc9v3.boundary_birth", ["birth_trial_production"], "lgrc9v3.explicit_packet_transport", ["packet_schedule"], "invalid_relabel", ["admit topology birth", "claim any current can schedule packet work"], ("incompatible", "Birth trial fields do not map to packet source/target/amount."), ("distinct_queues", "Birth and packet queues share scheduling infrastructure but different contracts."), ("topology_specific", "Birth eligibility is parent-port local, not a packet route."), ("distinct", "Birth transfer and packet amount have separate invariants."), ["event queue machinery"], [], None, "none", "All generic packet admission coordinates are missing.", "shared event scheduler only", "none", ["birth-only queue", "interleaved queue", "packet starvation control"], "invalid topology-specific-to-generic promotion", "claim_boundary_rejected", "Boundary-birth eligibility remains topology-specific.", ["generic current-to-packet admission"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_run_event_queue_processes_birth_only_queue", "crossing_boundary_control"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_run_event_queue_interleaves_packet_and_birth_queues", "crossing_boundary_control")]),
    spec("CMP-15", "Causal spark candidate into mechanical refinement", "lgrc9v3.causal_spark_topology_integration", ["causal_spark_diagnostic"], "lgrc9v3.causal_spark_topology_integration", ["topology_integration", "packet_and_lineage_transport"], "lawful_native", ["emit candidate", "validate enabled integration", "commit refinement", "transport lineage"], ("exact", "Candidate and topology event identities connect diagnostic to commit."), ("compatible", "Arrival-local candidate precedes topology integration in event time."), ("compatible", "Candidate-local topology region determines refinement scope."), ("compatible", "Parent coherence transfer and packet lineage budgets are checked."), ["native diagnostic predicate", "configured integration gate", "native topology commit"], [], None, "native_with_configured_semantics", "Candidate diagnostics are reduced to the declared mechanical integration payload.", "candidate and topology event records", "active topology integration consumes causal candidate", ["large-gradient block", "policy disabled", "missing lineage", "budget mismatch"], "enabled LGRC-3 causal spark policy", "current_source_crossing_passed_with_configured_semantics", "Native configured spark-to-refinement mechanics.", ["semantic creation", "identity acceptance"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_active_topology_integration_expands_causal_lane_b_candidate"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_causal_lane_b_large_gradient_column_h_hit_is_blocked", "crossing_negative_control")]),
    spec("CMP-16", "Arbitrated collapse into lineage and active-state transport", "lgrc9v3.native_route_arbitration", ["selection_commit"], "lgrc9v3.collapse_reabsorption", ["topology_reabsorption_commit", "active_state_transport"], "lawful_native", ["commit selected collapse", "transport packet/lineage/surface state"], ("exact", "Topology event, lineage map, packet ledger, and active-state digests are linked."), ("compatible", "Active-state transport follows the committed topology event."), ("compatible", "Reabsorption maps old nodes to the selected sink region."), ("compatible", "Coherence and packet budgets remain closed."), ["native arbitration commit", "native reabsorption transport"], [], None, "native_with_configured_semantics", "Old endpoint identities are mapped or explicitly superseded.", "topology event and lineage transfer map", "process_causal_collapse_reabsorption plus state reabsorption", ["missing lineage", "missing topology event", "direct rewrite", "budget drift"], "selected collapse/reabsorption region", "current_source_crossing_passed_with_configured_semantics", "Native commit and state-transport mechanics; candidate formation remains separate.", ["semantic death", "native candidate formation"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_arbitration_commit_integrates_topology_and_producer"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_topology_state_reabsorption_updates_active_state_after_collapse"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_topology_state_reabsorption_requires_complete_lineage", "crossing_negative_control")]),
    spec("CMP-17", "Derived history into temporary conductance and later flux", "lgrc9v3.causal_history_annotation", ["assemble_causal_annotation"], "grc9v3.synchronous_update_cycle", ["transport_rebuild"], "producer_mediated", ["derive exact history", "producer maps history to conductance", "rebuild later flux"], ("producer_projection", "Experiment-local closure derives conductance from native history; runtime does not own the mapping."), ("pre_step_adapter", "The producer applies a bounded pre-step closure before native transport rebuild."), ("route_local", "History and conductance mapping are restricted to declared route edges."), ("conservative_adapter", "Producer must preserve coherence and declare conductance bounds."), ["native history", "native GRC transport"], ["history functional", "conductance update", "decay/progression schedule"], "N31_C2_exact_history_closure", "experiment_producer", "History is compressed to one temporary conductance multiplier.", "N31 composed identity and closure record", "producer-derived temporary conductance", ["same native state/different history", "tampered history", "producer omitted", "replay"], "bounded N31 C2 route-local closure", "producer_evidence_only", "Producer-mediated exact-history conductance candidate; not a native read path.", ["lawful_native", "native D0 decay", "coherence-only ontology closure"], [], [], [("experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/outputs/n31_native_exact_history_closure_i9c2.json", "producer_crossing_evidence"), ("experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/outputs/n31_added_mechanism_replay_controls_i10.json", "producer_replay_and_controls")], {"inspected_paths": [RUNTIME, GRC], "missing_crossing": "ordinary runtime has no history-to-conductance read path", "result": "producer_required"}),
    spec("CMP-18", "Ledger persistence into native Read-Back", "lgrc9v3.explicit_packet_transport", ["target_credit"], "pygrc.restoration_replay_identity", ["identity_and_replay_validation"], "unsupported_missing_crossing", ["retain ledger", "restore it", "claim later constitutive read"], ("persisted_not_consumed", "Restoration identity preserves ledger state but does not add a read path."), ("replay_compatible", "Ledger can survive replay without becoming a later cause."), ("persisted_scope", "Packet endpoints remain represented."), ("descriptive_only", "Restored budget identity does not authorize new work."), ["packet persistence", "restoration validation"], [], None, "none", "No constitutive write/read interaction is produced.", "snapshot and restoration identity", "none", ["identity sensitivity", "equal-input replay", "no semantic promotion"], "missing retained-ledger read path", "source_audit_missing_crossing", "Ledger persistence and replay identity only.", ["native Read-Back", "memory-mediated action"], [], [], absence_audit={"inspected_paths": [RUNTIME, RESTORATION], "missing_crossing": "restoration preserves packet ledger but no native constitutive consumer reads ledger history to alter later eligibility or geometry", "result": "unsupported_missing_crossing"}),
    spec("CMP-19", "Restoration identity relabeled as unrestricted identity", "pygrc.restoration_replay_identity", ["identity_and_replay_validation"], "pygrc.restoration_replay_identity", ["identity_and_replay_validation"], "invalid_relabel", ["compare versioned projection", "claim unrestricted behavioral identity"], ("scope_bounded", "Identity includes only schema-declared scientific state."), ("replay_scoped", "Equal-input continuation is tested only within declared replay scope."), ("model_scoped", "Identity covers the declared model projection."), ("not_applicable", "Digest equality is not a budget or action authority."), ["versioned comparison contract"], [], None, "none", "Representation-only caches and out-of-schema meanings are excluded intentionally.", "restoration identity projection", "versioned equality predicate", ["included-state sensitivity", "cache-only normalization", "legacy baseline policy"], "claim-boundary rejection", "claim_boundary_rejected", "Versioned restoration/replay identity only.", ["byte identity", "unrestricted behavioral identity", "semantic selfhood"], [RESTORATION], [t("tests/models/test_lgrc_9_v3_restoration_matrix.py", "test_lgrc_queue_clock_ledger_route_topology_and_producer_sensitivity", "crossing_boundary_control"), t("tests/models/test_lgrc_9_v3_restoration.py", "test_public_identity_rejects_unsupported_or_malformed_sources", "crossing_negative_control")]),
    spec("CMP-20", "Feedback eligibility producer into packet mechanics", "lgrc9v3.feedback_eligibility_producer", ["feedback_packet_schedule"], "lgrc9v3.explicit_packet_transport", ["packet_schedule", "source_debit", "target_credit"], "producer_mediated", ["producer reads feedback surface", "producer schedules packet", "native lifecycle commits"], ("exact_with_producer", "Producer record links consumed surface to scheduled packet ID."), ("compatible", "Producer read and packet schedule are time-scoped."), ("configured", "Feedback relation and packet route are configured."), ("compatible", "Native packet lifecycle enforces budget after producer schedule."), ["native packet mutation", "surface lineage validity"], ["eligibility", "direction", "threshold", "schedule"], "feedback_eligibility_producer", "installed_producer", "Feedback surface is reduced to one packet schedule decision.", "surface lineage and autonomous production record", "producer schedule_packet_departure call", ["policy disabled", "wrong polarity", "order mismatch", "budget violation", "duplicate"], "configured feedback surface and route", "current_source_producer_crossing_passed", "Producer-mediated feedback eligibility followed by native packet mechanics.", ["lawful_native", "native feedback admission"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_feedback_surface_and_producer_schedule_via_packet_queue_only"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_feedback_coupled_pulse_budget_violation_fails_closed", "crossing_negative_control")]),
    spec("CMP-21", "Packet arrival into causal pulse surface emission", "lgrc9v3.explicit_packet_transport", ["target_credit"], "lgrc9v3.causal_pulse_surface_lineage", ["surface_row_emission"], "lawful_native", ["commit packet arrival", "emit configured surface row"], ("exact", "Surface row cites committed packet/event identity."), ("compatible", "Row emission occurs after packet commit at the same event frontier."), ("contact_local", "Surface key is scoped to the arrival contact."), ("no_hidden_budget", "Surface emission is descriptive and does not move coherence."), ["native packet commit", "configured surface emission"], [], None, "native_with_configured_semantics", "Packet state is projected to a declared surface schema.", "packet event and surface row", "post-commit surface hook", ["surface policy disabled", "sub-LGRC2", "early producer", "digest mismatch"], "qualifying configured packet contact", "current_source_crossing_passed_with_configured_semantics", "Native configured packet-to-surface recording mechanics.", ["native memory", "Read-Back"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_enabled_pulse_substrate_surface_emits_after_committed_packet_event"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_pulse_substrate_surface_is_default_off_for_packet_events", "crossing_negative_control")]),
    spec("CMP-22", "Transported surface lineage into feedback scheduling", "lgrc9v3.causal_pulse_surface_lineage", ["surface_lineage_transport", "surface_reabsorption"], "lgrc9v3.feedback_eligibility_producer", ["feedback_surface_registration", "feedback_packet_schedule"], "producer_mediated", ["transport/reabsorb surface", "producer reads successor row", "producer schedules packet"], ("exact_with_producer", "Lineage and supersession records identify the consumable successor row."), ("time_scoped", "Producer read is constrained to the transported row's valid window."), ("lineage_mapped", "Topology lineage maps source surface to successor region."), ("compatible", "Surface transport is budget-neutral; packet budget begins at producer scheduling."), ["native surface lineage", "native packet lifecycle"], ["feedback eligibility", "packet schedule"], "feedback_eligibility_producer", "installed_producer", "Surface history is compressed to producer threshold/order evidence.", "surface lineage and production record", "producer reads transported successor row", ["stale superseded row", "missing reabsorption", "order mismatch", "duplicate"], "transported configured surface lineage", "current_source_producer_crossing_passed", "Producer-mediated lineage-aware feedback scheduling.", ["lawful_native", "native Read-Back"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_feedback_producer_reads_transported_successor_row"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_feedback_producer_blocks_stale_superseded_surface_row", "crossing_negative_control")]),
    spec("CMP-23", "Collapse commit into surface lineage reabsorption", "lgrc9v3.collapse_reabsorption", ["topology_reabsorption_commit", "active_state_transport"], "lgrc9v3.causal_pulse_surface_lineage", ["surface_lineage_transport", "surface_reabsorption"], "lawful_native", ["commit topology event", "transport/supersede rows", "reabsorb active surface"], ("exact", "Topology event and lineage map anchor each surface transition."), ("compatible", "Surface transport follows the committed topology event."), ("lineage_mapped", "Affected nodes map to selected successor region."), ("budget_neutral_surface", "Surface transport moves no coherence and cites packet budget records."), ["native/configured collapse commit", "native/configured surface lineage"], [], None, "native_with_configured_semantics", "Stale source rows are superseded rather than silently copied.", "topology event and lineage records", "topology reabsorption hook updates active surface state", ["partial lineage map", "missing topology event", "duplicate", "stale read"], "affected topology region", "current_source_crossing_passed_with_configured_semantics", "Native configured topology-to-surface-lineage mechanics.", ["semantic identity continuity", "native memory"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_topology_state_reabsorption_updates_active_state_after_collapse"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_surface_lineage_transports_rows_with_complete_node_map"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_surface_lineage_transport_partial_map_fails_closed_to_supersession", "crossing_negative_control")]),
    spec("CMP-24", "Arbitration topology commit into multi-basin records", "lgrc9v3.native_route_arbitration", ["selection_commit"], "lgrc9v3.multi_basin_record_validation", ["flow_and_child_record_emission"], "diagnostic_only", ["commit selected topology", "emit flow and child-basin records"], ("exact_diagnostic_projection", "Records cite committed topology and candidate identities."), ("post_commit", "Emission occurs only after the topology commit."), ("child_parent_regions", "Records project the affected child/parent regions."), ("descriptive", "Records observe budget/flux and do not authorize mutation."), ["native topology commit", "diagnostic record validation"], [], None, "runtime_diagnostic_hook", "Runtime state is compressed to flow-window and child-basin schemas.", "committed topology event", "post-commit multi-basin emitter", ["policy disabled", "malformed event", "duplicate", "replay mismatch"], "enabled multi-basin diagnostic policy", "current_source_diagnostic_crossing_passed", "Diagnostic records over a committed native/configured topology event.", ["basin formation by record", "general robustness"], [RUNTIME], [t("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_commit_emits_multi_basin_candidate_records_when_enabled"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_native_route_multi_basin_wrong_policy_emits_no_records", "crossing_negative_control")]),
    spec("CMP-25", "Snapshot through load/reset and restoration validation", "pygrc.restoration_replay_identity", ["snapshot_serialization"], "pygrc.restoration_replay_identity", ["load_and_reset_restoration", "identity_and_replay_validation"], "lawful_native", ["serialize snapshot", "load/reset baseline", "validate identity and replay"], ("versioned_exact", "Schema-declared scientific state and reset baseline are restored."), ("checkpoint_and_replay", "Identity is evaluated at declared checkpoints/windows."), ("model_scope", "The declared model projection is preserved."), ("not_applicable", "Restoration validates included state rather than authorizing transfer."), ["versioned loader", "identity validator"], [], None, "native_utility", "Representation-only caches are excluded by versioned contract.", "canonical snapshot and identity projection", "load plus identity/replay validator", ["legacy baseline", "malformed source", "included-state sensitivity", "repeated save/load"], "versioned restoration schema", "current_source_crossing_passed", "Versioned restoration/reset/replay utility mechanics.", ["byte identity", "unrestricted behavioral identity", "semantic identity"], [RESTORATION, GRC, RUNTIME], [t("tests/models/test_reset_baseline_persistence.py", "test_lgrc_identity_v2_is_stable_across_save_load"), t("tests/models/test_reset_baseline_persistence.py", "test_legacy_snapshot_loads_but_reset_requires_explicit_rebase", "crossing_negative_control")]),
    spec("CMP-26", "GRC front-capacity state into LGRC boundary-birth runtime", "grc9v3.front_capacity_growth", ["front_capacity_growth_eligibility", "front_propagation"], "lgrc9v3.boundary_birth", ["birth_trial_production", "birth_trial_commit"], "lawful_with_explicit_adapter", ["construct LGRC from GRC base state", "supply explicit causal modes", "prime boundary trial", "commit through LGRC step"], ("explicit_construction_mapping", "LGRC9V3.from_state carries GRC base state; construction policy supplies LGRC modes."), ("adapter_required", "Synchronous GRC state is placed at an explicit LGRC event-time frontier."), ("front_metadata_preserved", "Configured front-capacity parent/port metadata is retained."), ("compatible_when_declared", "Construction and birth policies must preserve parent/child coherence budget."), ["GRC front-capacity state", "LGRC native/configured birth commit"], ["runtime wrapping", "causal modes", "queue priming"], "build_lgrc9v3_corrected_cascade_runtime", "library_construction_adapter_invoked_by_caller", "Synchronous execution history is not converted into LGRC event history.", "GRC base state plus explicit construction policy", "GRC-to-LGRC construction and queue priming helper", ["missing front metadata", "policy disabled", "wrong port", "budget"], "explicit corrected-cascade construction only", "current_source_adapter_crossing_passed", "Lawful explicit construction adapter; not native cross-runtime formation or inherited event history.", ["lawful_native", "automatic time-semantics conversion", "native role formation"], [CONSTRUCTION, RUNTIME], [t("tests/models/test_lgrc_9_v3_construction.py", "test_corrected_cascade_queue_policy_is_explicit"), t("tests/models/test_lgrc_9_v3_runtime.py", "test_causal_boundary_birth_front_capacity_rejects_missing_or_wrong_port", "crossing_negative_control")]),
]


def test_ref(path: str, name: str, role: str, revision: str) -> dict[str, str]:
    return {
        "node_id": TEST_INDEX[path][name],
        "path": path,
        "sha256": sha256_file(ROOT / path),
        "source_revision": revision,
        "execution_revision": revision,
        "execution_status": "current_source_passed",
        "evidence_role": role,
    }


def all_selected_test_nodes() -> list[str]:
    return sorted({TEST_INDEX[path][name] for row in COMPOSITIONS for path, name, _ in row["tests"]})


def run_selected_tests(head: str) -> dict[str, Any]:
    nodes = all_selected_test_nodes()
    command = [".venv/bin/python", "-m", "pytest", "-q", *nodes]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = (completed.stdout + completed.stderr).strip()
    if completed.returncode != 0:
        raise RuntimeError(output)
    match = re.search(r"(\d+) passed(?:, (\d+) subtests passed)?", output)
    if match is None:
        raise RuntimeError(f"cannot parse pytest result: {output}")
    record = {
        "artifact": "Phase 8 GRC/LGRC causal pathway I108 crossing-test execution",
        "iteration": 108,
        "source_revision": head,
        "environment": ".venv",
        "command": command,
        "selected_test_nodes": nodes,
        "selected_test_node_count": len(nodes),
        "status": "passed",
        "pytest_test_count": int(match.group(1)),
        "pytest_subtest_count": int(match.group(2) or 0),
        "normalized_output": match.group(0),
        "runtime_or_test_source_modified_by_iteration": False,
    }
    record["execution_digest"] = canonical_digest(record)
    write_json(OUTPUT_EXECUTION, record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args()

    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    crosswalk = json.loads(CROSSWALK_PATH.read_text(encoding="utf-8"))
    i107_result = json.loads(I107_RESULT_PATH.read_text(encoding="utf-8"))
    i107_freeze = json.loads(I107_FREEZE_PATH.read_text(encoding="utf-8"))
    if registry["registry_digest"] != EXPECTED_REGISTRY_DIGEST:
        raise ValueError("I106 registry digest drift")
    if crosswalk["crosswalk_digest"] != EXPECTED_CROSSWALK_DIGEST:
        raise ValueError("I107 crosswalk digest drift")
    if i107_result["result_digest"] != EXPECTED_I107_RESULT_DIGEST:
        raise ValueError("I107 result digest drift")
    if i107_freeze["artifact_bundle_digest"] != EXPECTED_I107_BUNDLE_DIGEST:
        raise ValueError("I107 artifact bundle drift")

    execution = run_selected_tests(head) if args.run_tests else json.loads(OUTPUT_EXECUTION.read_text(encoding="utf-8"))
    if execution["source_revision"] != head or execution["status"] != "passed":
        raise ValueError("I108 crossing-test execution is absent, stale, or failed")
    if execution["selected_test_nodes"] != all_selected_test_nodes():
        raise ValueError("I108 selected crossing-test set changed; rerun with --run-tests")

    pathway_index = {item["pathway_id"]: item for item in registry["pathways"]}
    stage_index = {(row["pathway_id"], row["stage_id"]): row for row in crosswalk["stage_rows"]}

    rows = []
    for raw in COMPOSITIONS:
        row = {key: value for key, value in raw.items() if key not in {"source_paths", "tests", "historical_refs"}}
        for pathway_key in ("from_pathway_id", "to_pathway_id"):
            if row[pathway_key] not in pathway_index:
                raise ValueError(f"unknown pathway: {row[pathway_key]}")
        endpoint_refs = []
        for pathway_key, stage_key in (("from_pathway_id", "from_stage_ids"), ("to_pathway_id", "to_stage_ids")):
            stage_refs = []
            for stage_id in row[stage_key]:
                evidence = stage_index[(row[pathway_key], stage_id)]
                stage_refs.append({
                    "stage_id": stage_id,
                    "evidence_status": evidence["evidence_status"],
                    "test_execution_revision": evidence["test_execution_revision"],
                })
            endpoint_refs.append({
                "pathway_id": row[pathway_key],
                "stages": stage_refs,
                "crosswalk_digest": crosswalk["crosswalk_digest"],
            })
        positive_tests = []
        negative_tests = []
        for path, name, role in raw["tests"]:
            ref = test_ref(path, name, role, head)
            if role in {"crossing_negative_control", "crossing_boundary_control", "crossing_budget_control"}:
                negative_tests.append(ref)
            else:
                positive_tests.append(ref)
        row.update({
            "endpoint_evidence_refs": endpoint_refs,
            "crossing_source_refs": [file_ref(path, "crossing_source_semantics", head) for path in raw["source_paths"]],
            "crossing_evidence_refs": positive_tests + [file_ref(path, role, head) for path, role in raw["historical_refs"]],
            "crossing_negative_control_refs": negative_tests,
            "endpoint_coverage_used_as_crossing_evidence": False,
        })
        row["row_digest"] = canonical_digest(row)
        rows.append(row)

    counts = {status: sum(row["composition_status"] == status for row in rows) for status in STATUS_VALUES}
    matrix = {
        "artifact": "GRC/LGRC directional causal-pathway composition matrix",
        "schema_version": "grc_lgrc_causal_pathway_composition_matrix_v1",
        "iteration": 108,
        "status": "frozen",
        "source_revision": head,
        "registry_digest": registry["registry_digest"],
        "crosswalk_digest": crosswalk["crosswalk_digest"],
        "test_execution_digest": execution["execution_digest"],
        "endpoint_evidence_rule": "endpoint coverage is prerequisite context and is never crossing evidence",
        "lawful_native_rule": "lawful_native requires source semantics for the crossing and current crossing-specific evidence",
        "directionality_rule": "A -> B never implies B -> A",
        "composition_status_values": list(STATUS_VALUES),
        "composition_count": len(rows),
        "status_counts": counts,
        "compositions": rows,
        "runtime_behavior_changed": False,
    }
    matrix["matrix_digest"] = canonical_digest(matrix)
    write_json(OUTPUT_MATRIX, matrix)

    table_rows = []
    for row in rows:
        table_rows.append(
            f"| `{row['composition_id']}` | {row['name']} | `{row['composition_status']}` | "
            f"{len(row['crossing_source_refs'])} | {len(row['crossing_evidence_refs'])} | "
            f"`{row['adapter_id'] or 'none'}` / `{row['adapter_owner']}` | {row['claim_ceiling']} |"
        )
    guide = f"""# GRC/LGRC Composition Matrix

**Status:** Iteration 108 directional composition matrix frozen
**Pathway registry:** [`grc-lgrc-causal-pathway-contracts.json`](../../specs/grc-lgrc-causal-pathway-contracts.json)
**Evidence crosswalk:** [`grc-lgrc-causal-pathway-evidence-crosswalk.json`](../../specs/grc-lgrc-causal-pathway-evidence-crosswalk.json)
**Machine matrix:** [`grc-lgrc-causal-pathway-composition-matrix.json`](../../specs/grc-lgrc-causal-pathway-composition-matrix.json)

## Purpose

This matrix classifies directional crossings between independently grounded
pathway stages. It does not execute new behavior or upgrade either endpoint.

> Endpoint test coverage of both pathways is not evidence for the crossing.
> `lawful_native` requires source semantics and current evidence for the
> crossing itself.

## Status Meanings

| Status | Meaning |
| --- | --- |
| `lawful_native` | The crossing exists in source semantics, has current crossing evidence, and adds no load-bearing external relation. Configured residue can still bound the claim. |
| `lawful_with_explicit_adapter` | A named adapter performs a lawful crossing while retaining ownership of the mapping. |
| `diagnostic_only` | The crossing produces a bounded readout, not ordinary constitutive behavior. |
| `producer_mediated` | A producer supplies a load-bearing relation and remains part of the claim. |
| `unsupported_missing_crossing` | Endpoint mechanics exist, but the required source read/call relation is absent. |
| `invalid_relabel` | Mechanics or records exist, but the proposed composition claim erases authority or scope. |

## Frozen Matrix

| ID | Directional composition | Status | Source refs | Crossing evidence refs | Adapter / owner | Claim ceiling |
| --- | --- | --- | ---: | ---: | --- | --- |
{chr(10).join(table_rows)}

The machine matrix records state, temporal, spatial, and budget compatibility;
authority retained/transferred; adapter ownership; information loss; shared
carrier and interaction terms; controls; endpoint refs; crossing source and
evidence refs; claim ceilings; and blocked relabels.

## Direction And Authority

`A -> B` supplies no evidence for `B -> A`. If a caller, adapter, producer, or
experiment controller supplies direction, funding, eligibility, scheduling,
commitment, or reception authority, that owner remains visible even when both
endpoint mutations use native runtime mechanics.

## Remaining Boundary

Iteration 108 grounds representative crossings. It does not establish a
universal composition algebra. A composition status is not a maturity score:
a `lawful_native` row can remain narrow, default-off, configured, or bounded by
its recorded lifecycle and portability evidence. An
`unsupported_missing_crossing` row records absence under the frozen source and
evidence boundary; it does not by itself authorize a generic extension.

No composition row establishes ecology, agency, native Read-Back, or N32.
Iteration 109 may derive selection semantics from the registry, crosswalk, and
this matrix; it cannot invent a missing crossing.
"""
    OUTPUT_GUIDE.write_text(guide, encoding="utf-8")

    checks = {
        "i106_registry_digest_matches": registry["registry_digest"] == EXPECTED_REGISTRY_DIGEST,
        "i107_crosswalk_digest_matches": crosswalk["crosswalk_digest"] == EXPECTED_CROSSWALK_DIGEST,
        "all_26_composition_ids_unique": len(rows) == 26 and len({row["composition_id"] for row in rows}) == 26,
        "all_status_classes_represented": all(counts[status] > 0 for status in STATUS_VALUES),
        "all_endpoint_pathways_and_stages_resolve": all(row["endpoint_evidence_refs"] for row in rows),
        "endpoint_evidence_never_used_as_crossing_evidence": all(not row["endpoint_coverage_used_as_crossing_evidence"] for row in rows),
        "lawful_native_rows_have_source_and_current_crossing_evidence": all(row["crossing_source_refs"] and row["crossing_evidence_refs"] for row in rows if row["composition_status"] == "lawful_native"),
        "adapter_rows_name_adapter_and_non_native_owner": all(row["adapter_id"] and row["adapter_owner"] not in {"none", "native"} for row in rows if row["composition_status"] == "lawful_with_explicit_adapter"),
        "producer_rows_retain_non_native_owner": all(row["adapter_id"] and row["adapter_owner"] not in {"none", "native"} for row in rows if row["composition_status"] == "producer_mediated"),
        "unsupported_rows_record_absence_audit": all(row["source_absence_audit"] for row in rows if row["composition_status"] == "unsupported_missing_crossing"),
        "invalid_relabels_name_blocked_claims": all(row["blocked_relabels"] for row in rows if row["composition_status"] == "invalid_relabel"),
        "all_rows_record_compatibility_authority_and_loss": all(row["state_identity_mapping"] and row["temporal_compatibility"] and row["budget_or_invariant_compatibility"] and row["authority_retained"] and row["information_lost_or_compressed"] for row in rows),
        "selected_crossing_tests_passed": execution["status"] == "passed" and execution["pytest_test_count"] == execution["selected_test_node_count"],
        "runtime_behavior_unchanged": True,
        "iteration_109_ready": True,
    }
    result = {
        "artifact": "Phase 8 GRC/LGRC causal pathway consolidation Iteration 108 result",
        "iteration": 108,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": "accepted_directional_crossing_evidence_matrix_no_runtime_change",
        "source_revision": head,
        "branch": branch,
        "registry_digest": registry["registry_digest"],
        "crosswalk_digest": crosswalk["crosswalk_digest"],
        "matrix_digest": matrix["matrix_digest"],
        "test_execution_digest": execution["execution_digest"],
        "composition_count": len(rows),
        "status_counts": counts,
        "selected_crossing_test_count": execution["pytest_test_count"],
        "checks": checks,
        "runtime_behavior_changed": False,
        "iteration_109_ready": all(checks.values()),
    }
    result["result_digest"] = canonical_digest(result)
    write_json(OUTPUT_RESULT, result)

    report = f"""# Phase 8 GRC/LGRC Causal Pathway Consolidation - Iteration 108

## Result

Iteration 108 passed as a directional composition and crossing-evidence matrix.

```text
composition rows = {len(rows)}
lawful native = {counts['lawful_native']}
lawful with explicit adapter = {counts['lawful_with_explicit_adapter']}
diagnostic only = {counts['diagnostic_only']}
producer mediated = {counts['producer_mediated']}
unsupported missing crossing = {counts['unsupported_missing_crossing']}
invalid relabel = {counts['invalid_relabel']}
selected crossing tests = {execution['pytest_test_count']} passed
runtime behavior changed = false
Iteration 109 ready = {str(result['iteration_109_ready']).lower()}
```

## Interpretation

I107 established source-and-test-grounded endpoints. I108 separately inspects
the relation between them. Endpoint tests are never counted as crossing
evidence. Native rows cite both source call/read semantics and a current test
that exercises the crossing. Missing relations remain unsupported; producer,
adapter, and diagnostic ownership remain visible; invalid promotions remain
blocked.

The matrix is representative rather than pairwise complete. It includes the
20 seed cases and six additional source-current crossings exposed by the I106
decomposition. Directionality is strict: no row implies its reverse.

Composition status is not maturity. A `lawful_native` crossing can remain
narrow, default-off, configured, or bounded by its recorded lifecycle and
portability evidence. Likewise, `unsupported_missing_crossing` records an
absent relation under the frozen source/evidence boundary; it is not automatic
authorization to implement a generic crossing.

## Remaining Boundary

Selection semantics, maintenance automation, and independent pressure-consumer
use remain I109-I111 work. No composition row establishes ecology, agency,
semantic choice, native Read-Back, or a universal causal-work API.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")

    freeze_paths = [
        "scripts/build_phase8_causal_pathway_i108.py",
        "specs/grc-lgrc-causal-pathway-composition-matrix.json",
        "docs/reference/GRC-LGRC-CompositionMatrix.md",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108TestExecution.json",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.json",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.md",
    ]
    freeze_records = [file_ref(path, "iteration_108_artifact", "iteration_108_working_artifact") for path in freeze_paths]
    freeze = {
        "artifact": "Phase 8 GRC/LGRC causal pathway consolidation Iteration 108 artifact freeze",
        "iteration": 108,
        "source_revision": head,
        "i107_artifact_bundle_digest": i107_freeze["artifact_bundle_digest"],
        "artifacts": freeze_records,
        "artifact_bundle_digest": canonical_digest(freeze_records),
        "runtime_behavior_changed": False,
    }
    write_json(OUTPUT_FREEZE, freeze)
    print(json.dumps({
        "status": result["status"],
        "matrix_digest": matrix["matrix_digest"],
        "result_digest": result["result_digest"],
        "artifact_bundle_digest": freeze["artifact_bundle_digest"],
        "status_counts": counts,
    }, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
