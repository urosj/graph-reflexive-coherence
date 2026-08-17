"""Focused tests for exact causal-pathway linkage and claim provenance."""

from __future__ import annotations

import copy
import json
import unittest
from dataclasses import replace
from pathlib import Path
from typing import Any, ClassVar
from unittest.mock import patch

import pygrc.causal_pathways.binding as binding_module
from pygrc.causal_pathways import (
    AuthorityDriftError,
    BindingStateError,
    CausalPathwayAuthority,
    InvalidCandidateError,
    PathwayBindingSession,
    SymbolBindingError,
    UnbindableCompositionError,
    UnknownCompositionError,
    UnknownPathwayError,
    canonical_digest,
    sha256_file,
    unbound_execution_classification,
)
from pygrc.core import GRCParams, PortGraphBackend
from pygrc.models import (
    CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    GRC9V3,
    LAPSE_POLICY_UNIT,
    LGRC9V3,
    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS,
    LGRC_RUNTIME_LEVEL_LGRC2,
    GRC9V3NodeState,
    GRC9V3State,
    PortEdge,
)

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE_ANCHOR_PATH = (
    ROOT
    / "implementation/evidence/causal-pathway-binding/"
    "binding-acceptance-anchor.json"
)
TRUSTED_ACCEPTANCE_ANCHOR_DIGEST = (
    "127382ebd0b8f70a5990971190bec5de614f39f03b47c7ffaffe4f53e5970ae2"
)
CANDIDATE_EVIDENCE_PATH = Path(
    "tests/fixtures/causal_pathway_candidate_mechanism_evidence.json"
)
CMP05_CANDIDATE_EVIDENCE_PATH = Path(
    "tests/fixtures/causal_pathway_candidate_cmp05_distinct_mechanism_evidence.json"
)


def _candidate_mechanism_evidence() -> dict[str, str]:
    return {
        "evidence_kind": "executable_candidate_mechanism",
        "mechanism_id": "fixture.packet_schedule_then_snapshot",
        "path": CANDIDATE_EVIDENCE_PATH.as_posix(),
        "sha256": sha256_file(ROOT / CANDIDATE_EVIDENCE_PATH),
    }


def _cmp05_candidate_mechanism_evidence() -> dict[str, str]:
    return {
        "evidence_kind": "executable_candidate_mechanism",
        "mechanism_id": "fixture.distinct_diagnostic_packet_adapter",
        "path": CMP05_CANDIDATE_EVIDENCE_PATH.as_posix(),
        "sha256": sha256_file(ROOT / CMP05_CANDIDATE_EVIDENCE_PATH),
    }


def _accepted_authority() -> CausalPathwayAuthority:
    return CausalPathwayAuthority.load(
        ROOT,
        acceptance_anchor=json.loads(
            ACCEPTANCE_ANCHOR_PATH.read_text(encoding="utf-8")
        ),
        trusted_anchor_digest=TRUSTED_ACCEPTANCE_ANCHOR_DIGEST,
    )


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
    state = runtime.get_state().base_state
    state.nodes[0] = GRC9V3NodeState(coherence=4.0)
    edge = state.port_edges[0]
    state.port_edges[0] = PortEdge(
        edge.node_u,
        edge.port_u,
        edge.node_v,
        edge.port_v,
        conductance=edge.conductance,
        flux_uv=2.0,
    )
    return GRC9V3(
        params=GRCParams.from_mapping(
            {
                "dt": 1.0,
                "evolution": {
                    "lambda_birth": 1.0,
                    "alpha_seed": 0.25,
                    "w_bond": 1.5,
                },
            }
        ),
        state=state,
    )


def _prepare_front_propagation(model: GRC9V3) -> None:
    model.get_state().cached_quantities[
        "grcl9v3_growth_parent_capacity_sources"
    ] = {
        "0": {
            "construct_id": "M01-fixture-front",
            "inactive_parent_port": 2,
            "propagate_child_front": True,
            "child_front_port": 2,
            "child_front_max_depth": 1,
            "front_generation_depth": 0,
        }
    }


def _feedback_ready_two_node_runtime() -> LGRC9V3:
    state = _two_node_runtime().get_state().base_state
    model = LGRC9V3.from_state(
        state,
        {
            "dt": 1.0,
            "causal_modes": {
                "causal_layer_mode": CAUSAL_LAYER_MODE_PACKETIZED_FIXED_TOPOLOGY,
                "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC2,
                "lapse_policy": LAPSE_POLICY_UNIT,
                "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
                "event_time_policy": "explicit_event_time_key",
                "proper_time_accumulation_policy": "local_event_frontier",
                "causal_pulse_substrate_surface_enabled": True,
                "causal_pulse_substrate_surface_policy": (
                    LGRC9V3_CAUSAL_PULSE_SUBSTRATE_SURFACE_POLICY_EMIT_ROWS
                ),
                "causal_pulse_substrate_surface_validated": False,
            },
        },
    )
    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )
    model.step()
    model.emit_feedback_eligibility_surface_row(
        front_node_ids=(1,),
        rear_node_ids=(0,),
        feedback_threshold=0.0,
    )
    model.set_feedback_coupled_pulse_producer(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        threshold=0.0,
        packet_amount=0.1,
    )
    return model


class CausalPathwayBindingTest(unittest.TestCase):
    """Validate exact identity, candidate, and callable-link boundaries."""

    authority: ClassVar[CausalPathwayAuthority]

    @classmethod
    def setUpClass(cls) -> None:
        cls.authority = _accepted_authority()

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
        self.assertEqual("accepted", self.authority.binding_acceptance_status)
        self.assertEqual(
            TRUSTED_ACCEPTANCE_ANCHOR_DIGEST,
            self.authority.binding_acceptance_anchor_digest,
        )

    def test_self_consistent_authority_without_anchor_cannot_freeze(self) -> None:
        authority = CausalPathwayAuthority.load(ROOT)
        self.assertEqual(
            "pending_independent_review",
            authority.binding_acceptance_status,
        )
        session = PathwayBindingSession(authority)
        session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        with self.assertRaisesRegex(
            AuthorityDriftError,
            "pending independent review",
        ):
            session.freeze_lock()

    def test_anchor_rejects_self_consistent_p1_to_p2_map(self) -> None:
        original_load = binding_module._load_json

        def mutated_load(path: Path) -> dict[str, Any]:
            document = copy.deepcopy(original_load(path))
            if path.name != "grc-lgrc-causal-pathway-bindings.json":
                return document
            stage = next(
                item
                for item in document["stage_bindings"]
                if item["pathway_id"] == "lgrc9v3.explicit_packet_transport"
                and item["stage_id"] == "packet_schedule"
            )
            stage["symbols"][0]["qualified_symbol"] = "LGRC9V3.step"
            document["binding_map_digest"] = canonical_digest(
                document,
                excluding="binding_map_digest",
            )
            return document

        anchor = json.loads(ACCEPTANCE_ANCHOR_PATH.read_text(encoding="utf-8"))
        with (
            patch(
                "pygrc.causal_pathways.binding._load_json",
                side_effect=mutated_load,
            ),
            self.assertRaisesRegex(AuthorityDriftError, "pending independent review"),
        ):
            CausalPathwayAuthority.load(
                ROOT,
                acceptance_anchor=anchor,
                trusted_anchor_digest=TRUSTED_ACCEPTANCE_ANCHOR_DIGEST,
            )

    def test_anchor_rejects_self_consistent_false_source_revision(self) -> None:
        original_load = binding_module._load_json

        def mutated_load(path: Path) -> dict[str, Any]:
            document = copy.deepcopy(original_load(path))
            if path.name != "grc-lgrc-causal-pathway-bindings.json":
                return document
            document["source_revision"] = "0" * 40
            document["binding_map_digest"] = canonical_digest(
                document,
                excluding="binding_map_digest",
            )
            return document

        anchor = json.loads(ACCEPTANCE_ANCHOR_PATH.read_text(encoding="utf-8"))
        with (
            patch(
                "pygrc.causal_pathways.binding._load_json",
                side_effect=mutated_load,
            ),
            self.assertRaisesRegex(AuthorityDriftError, "pending independent review"),
        ):
            CausalPathwayAuthority.load(
                ROOT,
                acceptance_anchor=anchor,
                trusted_anchor_digest=TRUSTED_ACCEPTANCE_ANCHOR_DIGEST,
            )

    def test_anchor_record_cannot_replace_external_trusted_digest(self) -> None:
        anchor = json.loads(ACCEPTANCE_ANCHOR_PATH.read_text(encoding="utf-8"))
        forged_digest = "0" * 64

        with self.assertRaisesRegex(
            AuthorityDriftError,
            "not the independently trusted record",
        ):
            CausalPathwayAuthority.load(
                ROOT,
                acceptance_anchor=anchor,
                trusted_anchor_digest=forged_digest,
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

    def test_candidate_declaration_and_arbitrary_string_are_not_use(self) -> None:
        session = PathwayBindingSession(self.authority)
        candidate = session.declare_candidate(
            candidate_id="experiment.fixture.unused_candidate",
            candidate_kind="pathway",
            purpose="Prove that declaration and prose are not execution evidence.",
            owner="fixture",
            evidence_owner="fixture",
        )
        session.freeze_lock()

        with self.assertRaises(TypeError):
            session.record_candidate_use(  # type: ignore[call-arg]
                candidate.candidate_id,
                evidence_reference="arbitrary string",
            )
        with self.assertRaises(InvalidCandidateError):
            session.record_candidate_use(candidate.candidate_id)

        record = session.build_receipt().to_record()
        self.assertFalse(record["claim_qualified"])
        self.assertEqual([], record["candidate_relations_exercised"])
        self.assertEqual(
            [candidate.candidate_id],
            record["declared_but_unused"]["candidate_ids"],
        )

    def test_candidate_rejects_cmp05_invalid_relabel_laundering(self) -> None:
        session = PathwayBindingSession(self.authority)
        with self.assertRaisesRegex(
            InvalidCandidateError,
            "registered invalid relabels",
        ):
            session.declare_candidate(
                candidate_id="experiment.fixture.diagnostic_as_behavior",
                candidate_kind="composition",
                purpose="Attempt to relabel the CMP-05 diagnostic relation.",
                owner="fixture",
                consumed_pathway_ids=(
                    "lgrc9v3.diagnostic_grc_reconstruction",
                    "lgrc9v3.explicit_packet_transport",
                ),
                proposed_source_pathway_id=("lgrc9v3.diagnostic_grc_reconstruction"),
                proposed_target_pathway_id="lgrc9v3.explicit_packet_transport",
                proposed_relation=(
                    "diagnostic_as_behavior and native packet admission"
                ),
                evidence_owner="fixture",
            )

    def test_candidate_rejects_cmp05_semantic_paraphrase(self) -> None:
        session = PathwayBindingSession(self.authority)
        with self.assertRaisesRegex(
            InvalidCandidateError,
            "registered invalid relabels",
        ):
            session.declare_candidate(
                candidate_id="experiment.fixture.renamed_cmp05",
                candidate_kind="composition",
                purpose="Attempt a prose paraphrase of the CMP-05 relabel.",
                owner="fixture",
                consumed_pathway_ids=(
                    "lgrc9v3.diagnostic_grc_reconstruction",
                    "lgrc9v3.explicit_packet_transport",
                ),
                proposed_source_pathway_id=(
                    "lgrc9v3.diagnostic_grc_reconstruction"
                ),
                proposed_target_pathway_id="lgrc9v3.explicit_packet_transport",
                proposed_relation=(
                    "diagnostic reconstruction governs ordinary runtime packet "
                    "behavior"
                ),
                evidence_owner="fixture",
            )

    def test_candidate_rejects_metadata_only_mechanism_artifact(self) -> None:
        path = Path(
            "tests/fixtures/causal_pathway_candidate_metadata_only_evidence.json"
        )
        session = PathwayBindingSession(self.authority)
        with self.assertRaisesRegex(
            InvalidCandidateError,
            "artifact fields are incomplete",
        ):
            session.declare_candidate(
                candidate_id="experiment.fixture.metadata_only",
                candidate_kind="pathway",
                purpose="Reject stable prose without candidate code.",
                owner="fixture",
                evidence_owner="fixture",
                mechanism_evidence={
                    "evidence_kind": "executable_candidate_mechanism",
                    "mechanism_id": "fixture.metadata-only-candidate",
                    "path": path.as_posix(),
                    "sha256": sha256_file(ROOT / path),
                },
            )

    def test_candidate_alias_detection_ignores_forged_module_name(self) -> None:
        registered = self.authority.symbols(
            "lgrc9v3.diagnostic_grc_reconstruction",
            "diagnostic_model_construction",
        )[0]
        disguised = replace(
            registered,
            symbol_id="candidate-mechanism:fixture.disguised-registered-callable",
            module="tests.fixtures.disguised_candidate_module",
            binding_role="candidate_mechanism_entrypoint",
            call_kind="module_function",
        )

        self.assertTrue(self.authority.callable_is_registered(disguised))

    def test_candidate_endpoint_co_use_outside_scope_is_not_use(self) -> None:
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
            candidate_id="experiment.fixture.unscoped_candidate",
            candidate_kind="composition",
            purpose="Prove ordinary endpoint co-use is not candidate evidence.",
            owner="fixture",
            consumed_pathway_ids=(packet.pathway_id, restoration.pathway_id),
            proposed_source_pathway_id=packet.pathway_id,
            proposed_target_pathway_id=restoration.pathway_id,
            proposed_relation="fixture-only post-packet snapshot relation",
            evidence_owner="fixture",
            mechanism_evidence=_candidate_mechanism_evidence(),
        )
        crossing = candidate.mechanism()
        session.freeze_lock()
        with self.assertRaisesRegex(BindingStateError, "explicit evidence scope"):
            crossing(None)
        schedule(source_node_id=0, target_node_id=1, edge_id=0, amount=0.25)
        snapshot()

        with self.assertRaisesRegex(
            InvalidCandidateError,
            "exactly one completed evidence scope",
        ):
            session.record_candidate_use(candidate.candidate_id)

        record = session.build_receipt().to_record()
        self.assertEqual([], record["candidate_relations_exercised"])
        self.assertFalse(record["claim_envelope"]["experimental_unregistered"])

    def test_invalid_endpoint_pair_requires_distinct_mechanism_evidence(self) -> None:
        session = PathwayBindingSession(self.authority)
        with self.assertRaisesRegex(
            InvalidCandidateError,
            "distinct executable candidate mechanism evidence",
        ):
            session.declare_candidate(
                candidate_id="experiment.fixture.cmp05_new_relation",
                candidate_kind="composition",
                purpose="Propose distinct work across a known invalid pair.",
                owner="fixture",
                consumed_pathway_ids=(
                    "lgrc9v3.diagnostic_grc_reconstruction",
                    "lgrc9v3.explicit_packet_transport",
                ),
                proposed_source_pathway_id=("lgrc9v3.diagnostic_grc_reconstruction"),
                proposed_target_pathway_id="lgrc9v3.explicit_packet_transport",
                proposed_relation="new externally owned diagnostic packet adapter",
                evidence_owner="fixture",
            )

    def test_distinct_cmp05_candidate_retains_structured_invalid_blocks(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        diagnostic = session.bind_pathway(
            "lgrc9v3.diagnostic_grc_reconstruction",
            stage_ids=("diagnostic_model_construction",),
        )
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        prepare = diagnostic.symbol("diagnostic_model_construction")
        schedule = packet.symbol("packet_schedule", instance=model)
        candidate = session.declare_candidate(
            candidate_id="experiment.fixture.distinct_cmp05_mechanism",
            candidate_kind="composition",
            purpose="Exercise a distinct experimental mechanism over CMP-05 endpoints.",
            owner="fixture",
            consumed_pathway_ids=(diagnostic.pathway_id, packet.pathway_id),
            proposed_source_pathway_id=diagnostic.pathway_id,
            proposed_target_pathway_id=packet.pathway_id,
            proposed_relation="new externally owned diagnostic packet adapter",
            evidence_owner="fixture",
            mechanism_evidence=_cmp05_candidate_mechanism_evidence(),
        )
        crossing = candidate.mechanism()
        session.freeze_lock()

        with candidate.evidence_scope():
            diagnostic_result = prepare(model)
            self.assertIs(crossing(diagnostic_result), diagnostic_result)
            schedule(source_node_id=0, target_node_id=1, edge_id=0, amount=0.25)
        session.record_candidate_use(candidate.candidate_id)
        record = session.build_receipt().to_record()
        used = record["candidate_relations_exercised"][0]
        edge = next(
            item
            for item in record["pathway_use_graph"]["edges"]
            if item["candidate_id"] == candidate.candidate_id
        )

        self.assertEqual(["CMP-05"], used["invalid_relabel_conflict_ids"])
        self.assertEqual(
            ["diagnostic_as_behavior", "native packet admission"],
            used["invalid_relabel_blocked_claims"],
        )
        self.assertTrue(
            set(used["invalid_relabel_blocked_claims"])
            <= set(record["blocked_claims"])
        )
        self.assertEqual(
            used["invalid_relabel_conflict_ids"],
            edge["invalid_relabel_conflict_ids"],
        )
        self.assertEqual(
            used["invalid_relabel_blocked_claims"],
            edge["invalid_relabel_blocked_claims"],
        )
        self.assertEqual(used["blocked_claims"], edge["blocked_claims"])
        self.assertEqual(
            "descriptive_unreviewed_not_claim_qualified",
            used["proposed_relation_claim_status"],
        )

    def test_candidate_rejects_stale_mechanism_content_address(self) -> None:
        session = PathwayBindingSession(self.authority)
        stale = _candidate_mechanism_evidence()
        stale["sha256"] = "0" * 64
        with self.assertRaisesRegex(InvalidCandidateError, "content is stale"):
            session.declare_candidate(
                candidate_id="experiment.fixture.stale_candidate_evidence",
                candidate_kind="composition",
                purpose="Reject a stale candidate artifact.",
                owner="fixture",
                consumed_pathway_ids=(
                    "lgrc9v3.explicit_packet_transport",
                    "pygrc.restoration_replay_identity",
                ),
                proposed_source_pathway_id="lgrc9v3.explicit_packet_transport",
                proposed_target_pathway_id="pygrc.restoration_replay_identity",
                proposed_relation="fixture-only post-packet snapshot relation",
                evidence_owner="fixture",
                mechanism_evidence=stale,
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
        self.assertTrue(callable(alternatives.selection_scope))

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

    def test_false_return_is_rejected_and_not_claim_qualified(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        schedule = packet.symbol("packet_schedule", instance=model)
        session.freeze_lock()

        with patch.object(
            schedule,
            "_assert_current_callable",
            return_value=(lambda **_: False, schedule.callable_identity),
        ):
            self.assertIs(schedule(), False)
        record = session.build_receipt().to_record()
        invocation = record["actual_stage_symbol_invocations"][0]

        self.assertEqual("returned", invocation["outcome"])
        self.assertEqual("false", invocation["return_category"])
        self.assertEqual("rejected", invocation["effect_outcome"])
        self.assertFalse(invocation["claim_qualifying_effect"])
        self.assertFalse(record["claim_qualified"])
        self.assertEqual([], record["actual_bound_pathways_used"])
        self.assertEqual(
            [0],
            record["effect_outcome_summary"][
                "non_qualifying_returned_stage_invocation_indices"
            ],
        )

    def test_empty_commit_return_is_no_op_and_not_claim_qualified(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        birth = session.bind_pathway(
            "lgrc9v3.boundary_birth",
            stage_ids=("birth_trial_commit",),
        )
        commit = birth.symbol("birth_trial_commit", instance=model)
        session.freeze_lock()

        self.assertEqual(
            [],
            commit(
                parent_node_id=0,
                parent_port_id=2,
                outward_flux_pressure=1.0,
                rng_sample=0.0,
            ),
        )
        record = session.build_receipt().to_record()
        invocation = record["actual_stage_symbol_invocations"][0]

        self.assertEqual("empty", invocation["return_category"])
        self.assertEqual("no_op", invocation["effect_outcome"])
        self.assertFalse(invocation["claim_qualifying_effect"])
        self.assertFalse(record["claim_qualified"])

    def test_producer_without_state_mutation_is_no_op(self) -> None:
        model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        producer = session.bind_pathway(
            "lgrc9v3.feedback_eligibility_producer",
            stage_ids=("feedback_packet_schedule",),
        )
        produce = producer.symbol("feedback_packet_schedule", instance=model)
        session.freeze_lock()

        result = produce(policy="packet_departure_from_feedback_eligibility_policy")
        self.assertFalse(result.state_mutated)
        record = session.build_receipt().to_record()
        invocation = record["actual_stage_symbol_invocations"][0]

        self.assertEqual("no_op", invocation["effect_outcome"])
        self.assertEqual(
            {
                "kind": "boolean_attribute",
                "attribute": "state_mutated",
                "observed_boolean": False,
            },
            invocation["effect_evidence"],
        )
        self.assertFalse(invocation["claim_qualifying_effect"])
        self.assertFalse(record["claim_qualified"])

    def test_none_return_without_snapshot_change_is_no_op(self) -> None:
        model = _two_node_grc_runtime()
        session = PathwayBindingSession(self.authority)
        growth = session.bind_pathway(
            "grc9v3.front_capacity_growth",
            stage_ids=("front_propagation",),
        )
        propagate = growth.symbol("front_propagation", instance=model)
        session.freeze_lock()

        self.assertIsNone(
            propagate(parent_node_id=0, parent_port_id=2, child_node_id=1)
        )
        record = session.build_receipt().to_record()
        invocation = record["actual_stage_symbol_invocations"][0]

        self.assertEqual("none", invocation["return_category"])
        self.assertEqual("no_op", invocation["effect_outcome"])
        self.assertEqual(False, invocation["effect_evidence"]["changed"])
        self.assertFalse(invocation["claim_qualifying_effect"])
        self.assertFalse(record["claim_qualified"])

    def test_unreviewed_symbol_return_remains_unknown(self) -> None:
        model = _two_node_grc_runtime()
        session = PathwayBindingSession(self.authority)
        growth = session.bind_pathway(
            "grc9v3.front_capacity_growth",
            stage_ids=("growth_commit",),
        )
        commit = growth.symbol("growth_commit", instance=model)
        session.freeze_lock()

        marker = object()
        with patch.object(
            commit,
            "_assert_current_callable",
            return_value=(lambda **_: marker, commit.callable_identity),
        ):
            self.assertIs(commit(), marker)
        record = session.build_receipt().to_record()
        invocation = record["actual_stage_symbol_invocations"][0]

        self.assertIsNone(invocation["effect_contract_id"])
        self.assertEqual("unreviewed", invocation["effect_kind"])
        self.assertEqual("unknown", invocation["effect_outcome"])
        self.assertFalse(invocation["claim_qualifying_effect"])
        self.assertFalse(record["claim_qualified"])

    def test_cmp20_receipt_retains_producer_cut_and_matrix_ceiling(self) -> None:
        model = _feedback_ready_two_node_runtime()
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
            production = produce(
                policy="packet_departure_from_feedback_eligibility_policy"
            )
            schedule(
                source_node_id=0,
                target_node_id=1,
                edge_id=0,
                amount=0.25,
                departure_event_time_key=2.0,
                scheduler_event_index=10,
                packet_index=100,
            )
            runtime_state = model.get_state()
            ledger = runtime_state.packet_ledger
            assert ledger is not None
            produced_event_id = production.production_records[0].scheduled_event_id
            queued_departure = next(
                event
                for event in ledger.event_queue_records
                if event.event_id == produced_event_id
            )
            departure = debit(
                runtime_state.base_state,
                ledger,
                queued_departure=queued_departure,
            )
            credit(
                runtime_state.base_state,
                departure.ledger,
                packet_id=departure.packet_record.packet_id,
            )
        record = session.build_receipt().to_record()

        self.assertTrue(lock["explicit_producers"])
        self.assertEqual(1, len(record["registered_compositions_exercised"]))
        flow_witness = record["composition_crossing_witnesses"][0][
            "dataflow_witness"
        ]
        self.assertEqual(
            "shared_bound_endpoint_instance",
            flow_witness["witness_kind"],
        )
        self.assertEqual(
            "session-instance:0",
            flow_witness["runtime_instance_binding_id"],
        )
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

    def test_cmp20_distinct_endpoint_owners_do_not_create_edge(self) -> None:
        producer_model = _feedback_ready_two_node_runtime()
        transport_model = _two_node_runtime()
        session = PathwayBindingSession(self.authority)
        composition = session.bind_composition("CMP-20")
        producer = composition.source_binding
        transport = composition.target_binding
        produce = producer.symbol(
            "feedback_packet_schedule",
            instance=producer_model,
        )
        schedule = transport.symbol("packet_schedule", instance=transport_model)
        debit = transport.symbol("source_debit")
        credit = transport.symbol("target_credit")
        session.freeze_lock()

        with composition.evidence_scope():
            production = produce(
                policy="packet_departure_from_feedback_eligibility_policy"
            )
            self.assertTrue(production.state_mutated)
            schedule(
                source_node_id=0,
                target_node_id=1,
                edge_id=0,
                amount=0.25,
            )
            runtime_state = transport_model.get_state()
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

    def test_cmp04_unrelated_endpoint_objects_do_not_create_edge(self) -> None:
        source_runtime = _two_node_runtime()
        unrelated_target = _two_node_grc_runtime()
        session = PathwayBindingSession(self.authority)
        composition = session.bind_composition("CMP-04")
        diagnostic = composition.pathway(
            "lgrc9v3.diagnostic_grc_reconstruction"
        )
        prepare = diagnostic.symbol("diagnostic_model_construction")
        rebuild = diagnostic.symbol(
            "diagnostic_rebuild",
            instance=unrelated_target,
        )
        session.freeze_lock()

        with composition.evidence_scope():
            self.assertIs(prepare(source_runtime), source_runtime)
            rebuild()
        record = session.build_receipt().to_record()

        self.assertEqual([], record["composition_crossing_witnesses"])
        self.assertEqual([], record["registered_compositions_exercised"])
        self.assertEqual([], record["pathway_use_graph"]["edges"])
        self.assertIn(
            composition.binding_id,
            record["declared_but_unused"]["composition_binding_ids"],
        )

    def test_cmp26_requires_and_records_exact_adapter_crossing(self) -> None:
        grc_model = _two_node_grc_runtime()
        _prepare_front_propagation(grc_model)
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
        propagation = next(
            invocation
            for invocation in record["actual_stage_symbol_invocations"]
            if invocation["stage_id"] == "front_propagation"
        )
        self.assertEqual("committed", propagation["effect_outcome"])
        self.assertEqual(True, propagation["effect_evidence"]["changed"])

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
            mechanism_evidence=_candidate_mechanism_evidence(),
        )
        crossing = candidate.mechanism()
        session.freeze_lock()

        with candidate.evidence_scope():
            scheduled = schedule(
                source_node_id=0,
                target_node_id=1,
                edge_id=0,
                amount=0.25,
            )
            self.assertIs(crossing(scheduled), scheduled)
            snapshot()
        with self.assertRaisesRegex(
            BindingStateError,
            "returned candidate mechanisms require exact candidate-use witnesses",
        ):
            session.build_receipt()
        session.record_candidate_use(candidate.candidate_id)
        record = session.build_receipt().to_record()

        candidate_edges = [
            edge
            for edge in record["pathway_use_graph"]["edges"]
            if edge["edge_kind"] == "experimental_unregistered_candidate"
        ]
        self.assertEqual(1, len(candidate_edges))
        self.assertEqual("none", candidate_edges[0]["promotion_status"])
        self.assertEqual(
            "identity_verified_candidate_crossing_execution",
            candidate_edges[0]["candidate_execution_witness"]["witness_kind"],
        )
        self.assertEqual(
            "descriptive_unreviewed_not_claim_qualified",
            candidate_edges[0]["proposed_relation_claim_status"],
        )
        self.assertEqual(
            1,
            len(record["actual_candidate_mechanism_invocations"]),
        )
        self.assertTrue(record["claim_envelope"]["experimental_unregistered"])
        self.assertEqual(
            "experimental_unregistered",
            record["claim_envelope"]["overall_claim_status"],
        )

    def test_dynamic_choice_records_actual_branch_and_unused_alternative(self) -> None:
        model = _two_node_runtime()
        grc_model = _two_node_grc_runtime()
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
        unrelated = session.bind_pathway(
            "grc9v3.synchronous_update_cycle",
            stage_ids=("continuity_and_invariants",),
        )
        continuity = unrelated.symbol(
            "continuity_and_invariants",
            instance=grc_model,
        )
        alternatives = session.declare_alternatives(
            alternative_set_id="i114.dynamic_branch",
            pathway_ids=(packet.pathway_id, restoration.pathway_id),
            selection_authority="consumer_fixture_boolean",
        )
        session.freeze_lock()

        continuity()
        with alternatives.selection_scope():
            snapshot()
        record = session.build_receipt().to_record()

        self.assertEqual(
            {
                "grc9v3.synchronous_update_cycle",
                "pygrc.restoration_replay_identity",
            },
            {item["pathway_id"] for item in record["actual_bound_pathways_used"]},
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
        self.assertEqual(
            ["pygrc.restoration_replay_identity"],
            alternative_use["selected_pathway_ids"],
        )
        self.assertEqual(1, len(alternative_use["selection_scopes"]))
        self.assertEqual(
            "consumer",
            alternative_use["selection_scopes"][0]["selection_performed_by"],
        )

    def test_dynamic_choice_rejects_c_inside_ab_scope_before_execution(self) -> None:
        model = _two_node_runtime()
        grc_model = _two_node_grc_runtime()
        session = PathwayBindingSession(self.authority)
        packet = session.bind_pathway(
            "lgrc9v3.explicit_packet_transport",
            stage_ids=("packet_schedule",),
        )
        restoration = session.bind_pathway(
            "pygrc.restoration_replay_identity",
            stage_ids=("snapshot_serialization",),
        )
        unrelated = session.bind_pathway(
            "grc9v3.synchronous_update_cycle",
            stage_ids=("continuity_and_invariants",),
        )
        packet.symbol("packet_schedule", instance=model)
        restoration.symbol("snapshot_serialization", instance=model)
        continuity = unrelated.symbol(
            "continuity_and_invariants",
            instance=grc_model,
        )
        alternatives = session.declare_alternatives(
            alternative_set_id="fixture.packet_or_snapshot",
            pathway_ids=(packet.pathway_id, restoration.pathway_id),
            selection_authority="fixture_boolean",
        )
        session.freeze_lock()

        with (
            self.assertRaisesRegex(BindingStateError, "outside alternative set"),
            alternatives.selection_scope(),
        ):
            continuity()

        self.assertEqual((), session.invocation_records)
        with self.assertRaisesRegex(BindingStateError, "rejected choice"):
            session.build_receipt()

    def test_dynamic_scope_rejects_two_different_allowed_branches(self) -> None:
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
        alternatives = session.declare_alternatives(
            alternative_set_id="fixture.single_choice",
            pathway_ids=(packet.pathway_id, restoration.pathway_id),
            selection_authority="fixture_boolean",
        )
        session.freeze_lock()

        with (
            self.assertRaisesRegex(BindingStateError, "already selected"),
            alternatives.selection_scope(),
        ):
            snapshot()
            schedule(
                source_node_id=0,
                target_node_id=1,
                edge_id=0,
                amount=0.25,
            )

        self.assertEqual(1, len(session.invocation_records))
        self.assertEqual(
            "pygrc.restoration_replay_identity",
            session.invocation_records[0].pathway_id,
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
