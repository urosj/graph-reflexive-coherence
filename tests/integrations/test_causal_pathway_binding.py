"""Focused tests for exact causal-pathway linkage and claim provenance."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import ClassVar
from unittest.mock import patch

from pygrc.causal_pathways import (
    BindingStateError,
    CausalPathwayAuthority,
    InvalidCandidateError,
    PathwayBindingSession,
    SymbolBindingError,
    UnbindableCompositionError,
    UnknownCompositionError,
    UnknownPathwayError,
    canonical_digest,
    unbound_execution_classification,
)
from pygrc.core import PortGraphBackend
from pygrc.models import GRC9V3, LGRC9V3, GRC9V3NodeState, GRC9V3State, PortEdge

ROOT = Path(__file__).resolve().parents[2]


def _two_node_runtime() -> LGRC9V3:
    graph = PortGraphBackend()
    source = graph.add_node({"label": "source"})
    target = graph.add_node({"label": "target"})
    edge = graph.connect_ports(source, 0, target, 0, {"kind": "route"})
    state = GRC9V3State(
        topology=graph,
        nodes={
            source: GRC9V3NodeState(coherence=1.0),
            target: GRC9V3NodeState(coherence=1.0),
        },
        port_edges={
            edge: PortEdge(
                source,
                1,
                target,
                1,
                conductance=1.0,
                flux_uv=0.0,
            )
        },
        base_conductance={edge: 1.0},
        geometric_length={edge: 1.0},
        temporal_delay={edge: 1.0},
        flux_coupling={edge: 0.0},
    )
    return LGRC9V3.from_state(state, {"dt": 1.0})


def _two_node_grc_runtime() -> GRC9V3:
    runtime = _two_node_runtime()
    return GRC9V3(
        params=runtime.get_params(),
        state=runtime.get_state().base_state,
    )


class CausalPathwayBindingTest(unittest.TestCase):
    """Validate exact identity, candidate, and callable-link boundaries."""

    authority: ClassVar[CausalPathwayAuthority]

    @classmethod
    def setUpClass(cls) -> None:
        cls.authority = CausalPathwayAuthority.load(ROOT)

    def test_authority_loads_complete_current_stage_map(self) -> None:
        self.assertEqual(
            "a266b33da10778e8caf5ad7d4a4bfe4b71aed9d0df563fd6c74e7d4ed6cb486b",
            self.authority.registry_digest,
        )
        self.assertEqual(
            "73d08edb5734b2dc7790ed475713f6eac503913402bb498800b49497f2ef0556",
            self.authority.binding_map_digest,
        )
        self.assertEqual(
            ("packet_schedule", "source_debit", "target_credit"),
            self.authority.stage_ids("lgrc9v3.explicit_packet_transport"),
        )

    def test_unknown_admitted_identity_fails_closed(self) -> None:
        session = PathwayBindingSession(self.authority)
        with self.assertRaises(UnknownPathwayError):
            session.bind_pathway("experiment.not_admitted")
        with self.assertRaises(UnknownCompositionError):
            session.bind_composition("CMP-NOT-REGISTERED")

    def test_unsupported_and_invalid_rows_are_not_bindable(self) -> None:
        session = PathwayBindingSession(self.authority)
        with self.assertRaises(UnbindableCompositionError):
            session.bind_composition("CMP-06")
        with self.assertRaises(UnbindableCompositionError):
            session.bind_composition("CMP-05")

    def test_pathway_binding_delegates_to_real_schedule_method(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        schedule = packet.symbol("packet_schedule", instance=model)
        session.freeze_lock()

        result = schedule(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
        )

        self.assertIsNone(result)
        packet_ledger = model.get_state().packet_ledger
        self.assertIsNotNone(packet_ledger)
        assert packet_ledger is not None
        self.assertEqual(1, len(packet_ledger.event_queue_records))
        self.assertEqual(1, len(session.invocation_records))
        invocation = session.invocation_records[0]
        self.assertEqual("lgrc9v3.explicit_packet_transport", invocation.pathway_id)
        self.assertEqual("packet_schedule", invocation.stage_id)
        self.assertEqual("returned", invocation.outcome)
        self.assertEqual((), invocation.composition_ids)
        self.assertEqual(
            "LGRC9V3.schedule_packet_departure",
            invocation.callable_identity["qualified_symbol"],
        )

    def test_link_rejects_post_load_p1_to_p2_symbol_substitution(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        with (
            patch.object(
                LGRC9V3,
                "schedule_packet_departure",
                LGRC9V3.step,
            ),
            self.assertRaises(SymbolBindingError),
        ):
            packet.symbol("packet_schedule", instance=model)

        self.assertEqual((), session.invocation_records)

    def test_invocation_rejects_post_lock_callable_identity_drift(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        schedule = packet.symbol("packet_schedule", instance=model)
        session.freeze_lock()
        with (
            patch.object(
                LGRC9V3,
                "schedule_packet_departure",
                LGRC9V3.step,
            ),
            self.assertRaises(SymbolBindingError),
        ):
            schedule()

        self.assertEqual((), session.invocation_records)

    def test_composition_retains_cmp20_producer_identity_and_policy(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        composition = session.bind_composition("CMP-20")

        self.assertEqual("producer_mediated", composition.composition_status)
        self.assertEqual("feedback_eligibility_producer", composition.adapter_id)
        self.assertEqual("installed_producer", composition.adapter_owner)
        producer = composition.pathway("lgrc9v3.feedback_eligibility_producer")
        produce = producer.symbol("feedback_packet_schedule", instance=model)
        session.freeze_lock()

        with self.assertRaises(SymbolBindingError):
            produce(policy="packet_departure_from_flux_route_policy")
        result = produce(policy="packet_departure_from_feedback_eligibility_policy")

        self.assertEqual(
            "packet_departure_from_feedback_eligibility_policy",
            result.producer_policy,
        )
        self.assertEqual(("CMP-20",), session.invocation_records[-1].composition_ids)

    def test_stage_with_multiple_symbols_requires_exact_choice(self) -> None:
        session = PathwayBindingSession(self.authority)
        identity = session.bind_pathway(
            "grc9v3.identity_basin_reconstruction",
            stage_ids=("validate_and_mass_basins",),
        )
        with self.assertRaises(SymbolBindingError):
            identity.symbol("validate_and_mass_basins")
        selected = identity.symbol(
            "validate_and_mass_basins",
            symbol_id=(
                "grc9v3.identity_basin_reconstruction:validate_and_mass_basins:validate"
            ),
        )
        self.assertEqual("validate_geometric_basin_seeds", selected.__name__)

    def test_candidate_is_distinct_unregistered_and_authority_complete(self) -> None:
        session = PathwayBindingSession(self.authority)
        candidate = session.declare_candidate(
            candidate_id="experiment.i112.source_local_packet_admission",
            candidate_kind="composition",
            purpose="Pressure explicit source-local packet admission debt.",
            owner="i112_non_scientific_fixture",
            consumed_pathway_ids=(
                "grc9v3.synchronous_update_cycle",
                "lgrc9v3.explicit_packet_transport",
            ),
            proposed_source_pathway_id="grc9v3.synchronous_update_cycle",
            proposed_target_pathway_id="lgrc9v3.explicit_packet_transport",
            proposed_relation="new source-local eligibility producer",
            authority={"direction": "fixture producer"},
            producer_residue=("source-local eligibility formation",),
            evidence_owner="i112_fixture",
        )

        self.assertEqual("experimental_unregistered", candidate.claim_ceiling)
        self.assertEqual("none", candidate.promotion_status)
        self.assertEqual("fixture producer", candidate.authority["direction"])
        self.assertEqual("unresolved", candidate.authority["funding"])
        self.assertIn("candidate relation is native", candidate.blocked_claims)
        with self.assertRaises(UnknownPathwayError):
            session.bind_pathway(candidate.candidate_id)

    def test_candidate_cannot_collide_with_canonical_identity(self) -> None:
        session = PathwayBindingSession(self.authority)
        with self.assertRaises(InvalidCandidateError):
            session.declare_candidate(
                candidate_id="CMP-20",
                candidate_kind="pathway",
                purpose="collision",
                owner="fixture",
                evidence_owner="fixture",
            )

    def test_dynamic_alternatives_declare_but_do_not_select(self) -> None:
        session = PathwayBindingSession(self.authority)
        alternatives = session.declare_alternatives(
            alternative_set_id="fixture.packet_or_restoration",
            pathway_ids=(
                "lgrc9v3.explicit_packet_transport",
                "pygrc.restoration_replay_identity",
            ),
            selection_authority="consumer_fixture_branch",
        )

        self.assertEqual(2, len(alternatives.pathway_ids))
        self.assertEqual("consumer_fixture_branch", alternatives.selection_authority)
        self.assertFalse(hasattr(alternatives, "select"))

    def test_unbound_execution_is_never_claim_qualified(self) -> None:
        classification = unbound_execution_classification()
        self.assertEqual("unbound", classification["causal_pathway_provenance"])
        self.assertFalse(classification["claim_qualified"])
        self.assertFalse(classification["accepted_binding_receipt"])

    def test_mixed_bound_and_direct_work_is_explicitly_operation_scoped(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        schedule = packet.symbol("packet_schedule", instance=model)
        session.freeze_lock()

        schedule(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
        )
        model.step()
        receipt = session.build_receipt().to_record()

        self.assertTrue(receipt["claim_qualified"])
        self.assertEqual("bound_invocations_only", receipt["claim_scope"])
        self.assertFalse(receipt["whole_run_causal_closure_claimed"])
        self.assertFalse(receipt["untracked_execution_observable_by_binding_plane"])
        self.assertEqual(
            "not_observable_by_binding_plane",
            receipt["external_or_untracked_causal_input"],
        )
        self.assertFalse(receipt["unbound_execution_accepted_as_evidence"])
        self.assertEqual(1, len(receipt["actual_stage_symbol_invocations"]))
        self.assertEqual(
            "packet_schedule",
            receipt["actual_stage_symbol_invocations"][0]["stage_id"],
        )

    def test_bound_call_requires_lock_and_lock_closes_declarations(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        schedule = packet.symbol("packet_schedule", instance=model)

        with self.assertRaises(BindingStateError):
            schedule(
                source_node_id=0,
                target_node_id=1,
                edge_id=0,
                amount=0.25,
            )
        lock = session.freeze_lock()
        with self.assertRaises(BindingStateError):
            session.bind_pathway("pygrc.restoration_replay_identity")
        with self.assertRaises(BindingStateError):
            packet.symbol("packet_schedule", instance=model)

        lock_record = lock.to_record()
        self.assertEqual(
            lock.digest,
            canonical_digest(lock_record, excluding="lock_digest"),
        )

    def test_pathway_receipt_records_actual_use_and_conservative_claim(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        schedule = packet.symbol("packet_schedule", instance=model)
        lock = session.freeze_lock()

        schedule(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
        )
        receipt = session.build_receipt()
        record = receipt.to_record()

        self.assertEqual(lock.digest, record["binding_lock_digest"])
        self.assertEqual(1, len(record["actual_bound_pathways_used"]))
        self.assertEqual([], record["registered_compositions_exercised"])
        self.assertEqual("bound_invocations_only", record["claim_scope"])
        self.assertFalse(record["whole_run_causal_closure_claimed"])
        locked_link = lock.to_record()["declared_pathway_bindings"][0][
            "expected_concrete_symbols"
        ][0]
        self.assertEqual(
            locked_link["callable_identity"],
            record["actual_stage_symbol_invocations"][0]["callable_identity"],
        )
        self.assertEqual(
            "admitted_bounded",
            record["claim_envelope"]["overall_claim_status"],
        )
        node = record["pathway_use_graph"]["nodes"][0]
        self.assertEqual(
            "current_at_iteration_106_freeze",
            node["pathway_status"]["staleness_state"],
        )
        self.assertFalse(record["claim_envelope"]["synthesized_chain_claim"])
        self.assertEqual(
            receipt.digest,
            canonical_digest(record, excluding="receipt_digest"),
        )

    def test_declaration_without_use_remains_visible_and_unqualified(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        packet.symbol("packet_schedule", instance=model)
        session.freeze_lock()

        record = session.build_receipt().to_record()

        self.assertFalse(record["claim_qualified"])
        self.assertEqual([], record["actual_bound_pathways_used"])
        self.assertEqual(
            ["pathway:lgrc9v3.explicit_packet_transport"],
            record["declared_but_unused"]["pathway_binding_ids"],
        )

    def test_failed_invocation_is_recorded_without_behavioral_claim(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        schedule = packet.symbol("packet_schedule", instance=model)
        session.freeze_lock()

        with self.assertRaises(ValueError):
            schedule(
                source_node_id=0,
                target_node_id=1,
                edge_id=0,
                amount=-0.25,
            )
        record = session.build_receipt().to_record()

        self.assertEqual(
            "raised",
            record["actual_stage_symbol_invocations"][0]["outcome"],
        )
        self.assertFalse(record["claim_qualified"])
        self.assertEqual([], record["actual_bound_pathways_used"])

    def test_cmp20_receipt_retains_producer_cut_and_matrix_ceiling(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        composition = session.bind_composition("CMP-20")
        producer = composition.pathway("lgrc9v3.feedback_eligibility_producer")
        transport = composition.pathway("lgrc9v3.explicit_packet_transport")
        produce = producer.symbol("feedback_packet_schedule", instance=model)
        schedule = transport.symbol("packet_schedule", instance=model)
        debit = transport.symbol("source_debit")
        credit = transport.symbol("target_credit")
        lock = session.freeze_lock().to_record()

        with composition.evidence_scope():
            produce(policy="packet_departure_from_feedback_eligibility_policy")
            schedule(
                source_node_id=0,
                target_node_id=1,
                edge_id=0,
                amount=0.25,
            )
            runtime_state = model.get_state()
            ledger = runtime_state.packet_ledger
            assert ledger is not None
            departure = debit(
                runtime_state.base_state,
                ledger,
                queued_departure=ledger.event_queue_records[0],
            )
            credit(
                runtime_state.base_state,
                departure.ledger,
                packet_id=departure.packet_record.packet_id,
            )
        record = session.build_receipt().to_record()

        self.assertTrue(lock["explicit_producers"])
        self.assertEqual(1, len(record["registered_compositions_exercised"]))
        envelope = record["claim_envelope"]
        self.assertTrue(envelope["contains_producer_cut"])
        self.assertEqual(
            "bounded_with_explicit_ownership_cuts",
            envelope["overall_claim_status"],
        )
        self.assertIn("lawful_native", envelope["blocked_claims"])
        edge = record["pathway_use_graph"]["edges"][0]
        self.assertEqual("installed_producer", edge["producer_owner"])
        self.assertEqual("producer_mediated", edge["composition_status"])

    def test_endpoint_co_use_outside_scope_does_not_claim_composition(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        composition = session.bind_composition("CMP-20")
        producer = composition.source_binding
        transport = composition.target_binding
        produce = producer.symbol("feedback_packet_schedule", instance=model)
        schedule = transport.symbol("packet_schedule", instance=model)
        debit = transport.symbol("source_debit")
        credit = transport.symbol("target_credit")
        session.freeze_lock()

        produce(policy="packet_departure_from_feedback_eligibility_policy")
        schedule(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
        )
        runtime_state = model.get_state()
        ledger = runtime_state.packet_ledger
        assert ledger is not None
        departure = debit(
            runtime_state.base_state,
            ledger,
            queued_departure=ledger.event_queue_records[0],
        )
        credit(
            runtime_state.base_state,
            departure.ledger,
            packet_id=departure.packet_record.packet_id,
        )
        record = session.build_receipt().to_record()

        self.assertEqual([], record["composition_crossing_witnesses"])
        self.assertEqual([], record["registered_compositions_exercised"])
        self.assertEqual([], record["pathway_use_graph"]["edges"])
        self.assertEqual(
            ["composition:CMP-20"],
            record["declared_but_unused"]["composition_binding_ids"],
        )

    def test_out_of_order_composition_scope_does_not_claim_edge(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        composition = session.bind_composition("CMP-20")
        producer = composition.source_binding
        transport = composition.target_binding
        produce = producer.symbol("feedback_packet_schedule", instance=model)
        schedule = transport.symbol("packet_schedule", instance=model)
        debit = transport.symbol("source_debit")
        credit = transport.symbol("target_credit")
        session.freeze_lock()

        with composition.evidence_scope():
            schedule(
                source_node_id=0,
                target_node_id=1,
                edge_id=0,
                amount=0.25,
            )
            runtime_state = model.get_state()
            ledger = runtime_state.packet_ledger
            assert ledger is not None
            departure = debit(
                runtime_state.base_state,
                ledger,
                queued_departure=ledger.event_queue_records[0],
            )
            credit(
                runtime_state.base_state,
                departure.ledger,
                packet_id=departure.packet_record.packet_id,
            )
            produce(policy="packet_departure_from_feedback_eligibility_policy")
        record = session.build_receipt().to_record()

        self.assertEqual([], record["composition_crossing_witnesses"])
        self.assertEqual([], record["registered_compositions_exercised"])
        self.assertEqual([], record["pathway_use_graph"]["edges"])

    def test_cmp26_requires_and_records_exact_adapter_crossing(self) -> None:
        grc_model = _two_node_grc_runtime()
        session = PathwayBindingSession(self.authority)
        composition = session.bind_composition("CMP-26")
        front = composition.source_binding
        birth = composition.target_binding
        eligible = front.symbol(
            "front_capacity_growth_eligibility",
            instance=grc_model,
        )
        propagate = front.symbol("front_propagation", instance=grc_model)
        crossing = composition.crossing(source_instance=grc_model)
        produce = birth.symbol(
            "birth_trial_production",
            instance=crossing.result_reference,
        )
        commit = birth.symbol(
            "birth_trial_commit",
            instance=crossing.result_reference,
        )
        lock = session.freeze_lock().to_record()

        with composition.evidence_scope():
            eligible()
            propagate(parent_node_id=0, parent_port_id=2, child_node_id=1)
            lgrc_model = crossing(grc_model)
            produce(policy="boundary_birth_trial_policy")
            commit(
                parent_node_id=0,
                parent_port_id=2,
                outward_flux_pressure=1.0,
                rng_sample=0.5,
            )
        record = session.build_receipt().to_record()

        expected_crossing = lock["declared_composition_bindings"][0][
            "expected_crossing_callable"
        ]
        actual_crossing = record["actual_composition_crossing_invocations"][0]
        witness = record["composition_crossing_witnesses"][0]
        self.assertIs(crossing.result_reference.resolve(), lgrc_model)
        self.assertEqual(
            expected_crossing["callable_identity"],
            actual_crossing["callable_identity"],
        )
        self.assertEqual("returned", actual_crossing["outcome"])
        self.assertTrue(witness["explicit_adapter_required"])
        self.assertTrue(witness["explicit_adapter_observed"])
        self.assertLess(
            max(
                record["actual_stage_symbol_invocations"][index][
                    "execution_event_order"
                ]
                for index in witness["from_invocation_indices"]
            ),
            actual_crossing["execution_event_order"],
        )
        self.assertLess(
            actual_crossing["execution_event_order"],
            min(
                record["actual_stage_symbol_invocations"][index][
                    "execution_event_order"
                ]
                for index in witness["to_invocation_indices"]
            ),
        )
        self.assertEqual(1, len(record["pathway_use_graph"]["edges"]))

    def test_cmp26_lock_rejects_missing_adapter_crossing(self) -> None:
        session = PathwayBindingSession(self.authority)
        session.bind_composition("CMP-26")

        with self.assertRaises(BindingStateError):
            session.freeze_lock()

    def test_cmp26_rejects_target_endpoints_bound_outside_adapter_flow(self) -> None:
        grc_model = _two_node_grc_runtime()
        unrelated_lgrc_model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        composition = session.bind_composition("CMP-26")
        front = composition.source_binding
        birth = composition.target_binding
        front.symbol(
            "front_capacity_growth_eligibility",
            instance=grc_model,
        )
        front.symbol("front_propagation", instance=grc_model)
        composition.crossing(source_instance=grc_model)
        birth.symbol(
            "birth_trial_production",
            instance=unrelated_lgrc_model,
        )
        birth.symbol(
            "birth_trial_commit",
            instance=unrelated_lgrc_model,
        )
        with self.assertRaises(BindingStateError):
            session.freeze_lock()

    def test_candidate_use_builds_distinct_edge_and_experimental_envelope(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        restoration = session.bind_pathway(
            "pygrc.restoration_replay_identity",
            stage_ids=("snapshot_serialization",),
        )
        schedule = packet.symbol("packet_schedule", instance=model)
        snapshot = restoration.symbol("snapshot_serialization", instance=model)
        candidate = session.declare_candidate(
            candidate_id="experiment.i114.packet_to_snapshot_relation",
            candidate_kind="composition",
            purpose="Pressure a noncanonical packet-to-snapshot relation.",
            owner="i114_fixture",
            consumed_pathway_ids=(packet.pathway_id, restoration.pathway_id),
            proposed_source_pathway_id=packet.pathway_id,
            proposed_target_pathway_id=restoration.pathway_id,
            proposed_relation="fixture-only post-packet snapshot relation",
            evidence_owner="i114_fixture",
        )
        session.freeze_lock()

        schedule(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=0.25,
        )
        snapshot()
        session.record_candidate_use(
            candidate.candidate_id,
            evidence_reference="tests/integrations/test_causal_pathway_binding.py",
        )
        record = session.build_receipt().to_record()

        candidate_edges = [
            edge
            for edge in record["pathway_use_graph"]["edges"]
            if edge["edge_kind"] == "experimental_unregistered_candidate"
        ]
        self.assertEqual(1, len(candidate_edges))
        self.assertEqual("none", candidate_edges[0]["promotion_status"])
        self.assertTrue(record["claim_envelope"]["experimental_unregistered"])
        self.assertEqual(
            "experimental_unregistered",
            record["claim_envelope"]["overall_claim_status"],
        )

    def test_dynamic_choice_records_actual_branch_and_unused_alternative(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        restoration = session.bind_pathway(
            "pygrc.restoration_replay_identity",
            stage_ids=("snapshot_serialization",),
        )
        packet.symbol("packet_schedule", instance=model)
        snapshot = restoration.symbol("snapshot_serialization", instance=model)
        session.declare_alternatives(
            alternative_set_id="i114.dynamic_branch",
            pathway_ids=(packet.pathway_id, restoration.pathway_id),
            selection_authority="consumer_fixture_boolean",
        )
        session.freeze_lock()

        snapshot()
        record = session.build_receipt().to_record()

        self.assertEqual(
            ["pygrc.restoration_replay_identity"],
            [item["pathway_id"] for item in record["actual_bound_pathways_used"]],
        )
        self.assertEqual(
            ["pathway:lgrc9v3.explicit_packet_transport"],
            record["declared_but_unused"]["pathway_binding_ids"],
        )
        alternative_use = record["allowed_pathway_alternatives_actual_use"][0]
        self.assertEqual(
            ["pygrc.restoration_replay_identity"],
            alternative_use["actual_pathway_ids_used"],
        )

    def test_registered_chain_does_not_synthesize_larger_claim(self) -> None:
        session = PathwayBindingSession(self.authority)
        first = session.bind_composition("CMP-20")
        second = session.bind_composition("CMP-21")
        for composition in (first, second):
            for endpoint in composition.endpoint_bindings:
                for stage_id in endpoint.stage_ids:
                    symbols = self.authority.symbols(endpoint.pathway_id, stage_id)
                    endpoint.symbol(
                        stage_id,
                        symbol_id=symbols[0].symbol_id,
                    )

        lock = session.freeze_lock().to_record()

        envelope = lock["pre_execution_claim_envelope"]
        self.assertEqual(2, len(envelope["constituent_composition_claim_ceilings"]))
        self.assertFalse(envelope["synthesized_chain_claim"])


if __name__ == "__main__":
    unittest.main()
