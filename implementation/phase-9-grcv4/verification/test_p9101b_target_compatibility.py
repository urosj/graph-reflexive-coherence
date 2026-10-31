"""Exact expanded subjects, independent V3 projection, both-role public crossings."""

from copy import deepcopy
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
import lzma
from pathlib import Path
import unittest
from unittest.mock import patch

from pygrc.models import GRC9V4
from pygrc.models.grc_9_v3 import GRC9V3
from pygrc.models.grc_9_v4 import GRC9V4BranchRequest
from tests.models.test_grc_9_v4_crossing import initializer_oracle, step_request
from tests.models.test_grc_9_v4_legacy import config as legacy_config

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "implementation/phase-9-grcv4/tranche-9"
EVIDENCE = {}


def encoded(value):
    # Native bytes retain signed zero, unlike the scientific canonical codec.
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def target_seed(family):
    if family == "C_RG2b":
        from p9_crg2b_campaign import read, BASE as connected
        return read(connected + "9.1b-integration.json.xz")["evidence"]["mixed_snapshot"]
    name = {"A_OS": "AOS", "C_PC": "CPC", "C_CI_PC": "CCIPC", "A_CI_PC": "ACIPC"}.get(family, family)
    path = BASE / f"P9-9.1b-{name}.json"
    if path.exists():
        raw = path.read_bytes()
    else:
        raw = lzma.decompress(path.with_suffix(".json.xz").read_bytes())
    return json.loads(raw)["evidence"]["mixed_snapshot"]


def target(family):
    return target_seed(family)["state"]


def subject(model):
    c = model.configuration
    return dict(
        complete_profile_id=c.reference.profile.complete_profile_id,
        specialization_id=c.specialization.specialization_id,
        model_identity=model.active_model_identity,
        graph_content_sha256=digest(c.reference.to_payload()["graph"]),
        graph_vertices=len(c.reference.graph.live_node_ids),
        graph_edges=len(c.reference.graph.live_edge_ids),
    )


def request(model, direction, reference=None):
    if direction == "enable":
        declaration = dict(target_reference=reference.to_payload())
    else:
        family = model.configuration.family.profile_family_id
        cfg = legacy_config(family)
        del cfg["state"]
        cfg["dt"] = 2**-12
        count = len(model.configuration.reference.graph.live_edge_ids)
        declaration = dict(
            legacy_config=cfg,
            current_incoming_weights=[1 + i / 16 for i in range(count)],
            reset_incoming_weights=[0.75 + i / 32 for i in range(count)],
            current_incoming_flux=[0.01 * (i + 1) for i in range(count)],
            reset_incoming_flux=[-0.02 * (i + 1) for i in range(count)],
        )
    return GRC9V4BranchRequest(
        direction + ":" + model.lifecycle_digest,
        model.lifecycle_digest,
        direction,
        declaration,
    )


def independent_entry(configuration, declaration, role):
    """Build V3 directly from saved graph/state, never from the adapter's output."""
    graph = configuration.reference.graph.port_graph
    labels = list(graph.live_node_ids)
    resource = getattr(configuration, role).C
    incidence = {str(i): [] for i in range(len(labels))}
    edges, port_edges = [], {}
    for eid, edge in enumerate(graph.edges):
        endpoints = [(labels.index(e.node_id), e.port) for e in (edge.tail, edge.head)]
        ordered = sorted(endpoints)
        (u, pu), (v, pv) = ordered
        flux = declaration[role + "_incoming_flux"][eid]
        port_edges[str(eid)] = dict(
            node_u=u,
            port_u=pu,
            node_v=v,
            port_v=pv,
            conductance=declaration[role + "_incoming_weights"][eid],
            flux_uv=flux if endpoints == ordered else -flux,
        )
        edges.append(
            dict(
                edge_id=eid,
                endpoint_a=dict(node_id=u, slot=pu - 1),
                endpoint_b=dict(node_id=v, slot=pv - 1),
                payload={},
            )
        )
        incidence[str(u)].append(eid)
        incidence[str(v)].append(eid)
    cfg = deepcopy(declaration["legacy_config"])
    cfg["state"] = dict(
        topology=dict(
            nodes=[dict(node_id=i, payload={}) for i in range(len(labels))],
            edges=edges,
            incidence=incidence,
            port_structure={},
        ),
        nodes={
            str(i): dict(coherence=c, basin_mass=c, basin_id=i)
            for i, c in enumerate(resource)
        },
        port_edges=port_edges,
        step_index=configuration.step_index,
        time=configuration.time,
        budget_target=float(sum(map(Fraction, resource))),
    )
    native = GRC9V3.from_config(cfg)
    weights, gradients = initializer_oracle(native, native.get_params().evolution)
    native.rebuild_differential_state()
    native.rebuild_transport_state()
    native.rebuild_differential_state()
    native.rebuild_identity_state()
    if (
        tuple(native.get_state().base_conductance[i] for i in range(len(edges)))
        != weights
    ):
        raise AssertionError("independent incoming-stage initializer disagrees")
    return native, dict(W=weights, incoming_rows=gradients, input_config=cfg)


def native_pair(configuration, declaration):
    cur, a = independent_entry(configuration, declaration, "current")
    rst, b = independent_entry(configuration, declaration, "reset")
    snap = cur.snapshot()
    snap["reset_baseline"]["snapshot"] = rst._snapshot_payload(reset_baseline=None)
    return GRC9V3._from_snapshot(snap, restore_reset_baseline=True), dict(
        current=a, reset=b
    )


class TargetCompatibility(unittest.TestCase):
    FAMILY = None

    @classmethod
    def setUpClass(cls):
        if cls.FAMILY is None:
            raise unittest.SkipTest("select a family")

    def model(self):
        m = GRC9V4.from_config(
            dict(
                initial=target(self.FAMILY),
                exact_backend="flint",
                numerical_policy="legacy_exact_v1",
            )
        )
        review = json.loads((BASE / "P9-9.6-SupportReview.json").read_bytes())
        row = next(r for r in review["rows"] if r["family"] == self.FAMILY)
        self.assertEqual(subject(m), row["enabled_expansion_target"])
        self.assertNotEqual(m.active_model_identity, row["source"]["model_identity"])
        self.assertEqual(
            (
                len(m.configuration.current.C),
                len(m.configuration.reference.graph.live_edge_ids),
            ),
            (17, 16),
        )
        return m

    def parity(self, m, n):
        self.assertEqual(
            encoded(m.state.lifecycle.delegate_snapshot), encoded(n.snapshot())
        )
        self.assertEqual(m.compute_observables(), n.compute_observables())
        self.assertNotIn("basin_attributes", m.compute_observables())
        self.assertEqual(
            m.active_model_identity, m.state.lifecycle.active_model_identity
        )
        return dict(
            snapshot_sha256=digest(n.snapshot()), observables=n.compute_observables()
        )

    def roundtrip(self, basin):
        m = self.model()
        original_subject = subject(m)
        if basin:
            r = m.migrate_basin_policy("target-basin-opt-in")
            self.assertTrue(r.committed, r.failure)
            self.assertNotEqual(
                subject(m)["model_identity"], original_subject["model_identity"]
            )
            self.assertNotEqual(
                subject(m)["specialization_id"], original_subject["specialization_id"]
            )
            self.assertEqual(
                subject(m)["complete_profile_id"],
                original_subject["complete_profile_id"],
            )
        active_subject = subject(m)
        cfg = m.configuration
        req = request(m, "disable")
        n, projected = native_pair(cfg, req.to_payload()["declaration"])
        self.assertTrue(m.migrate_branch(req).committed)
        entry = m.snapshot()
        observations = [dict(operation="entry", **self.parity(m, n))]
        # Neither enabled numerical evolution nor the new classifier may leak
        # into disabled delegation, including reset and subsequent evolution.
        with (
            patch(
                "pygrc.models.grc_v4_lifecycle._profile_step",
                side_effect=AssertionError("V4 kernel leaked"),
            ),
            patch(
                "pygrc.models.grc_9_v4_basin.capture_pair",
                side_effect=AssertionError("V4 basin leaked"),
            ),
        ):
            for op in ("step", "reset", "step"):
                actual, expected = getattr(m, op)(), getattr(n, op)()
                if op == "step":
                    self.assertEqual(asdict(actual), asdict(expected))
                observations.append(
                    dict(
                        operation=op,
                        output=asdict(expected) if expected is not None else None,
                        **self.parity(m, n),
                    )
                )
        disabled = m.snapshot()
        self.assertEqual(
            encoded(GRC9V4.from_state(disabled).snapshot()), encoded(disabled)
        )
        rst = GRC9V3._from_snapshot(
            n.snapshot()["reset_baseline"]["snapshot"], restore_reset_baseline=False
        )
        roles = (n, rst)
        self.assertNotEqual(
            [v.coherence for v in n.get_state().nodes.values()],
            [v.coherence for v in rst.get_state().nodes.values()],
        )
        expected_history = []
        if self.FAMILY.startswith("A_"):
            p = cfg.reference.profile.params_resolved.candidate
            expected_history = [
                initializer_oracle(v, dict(alpha=p.alpha, beta=p.beta, gamma=p.gamma))[
                    0
                ]
                for v in roles
            ]
        result = m.migrate_branch(request(m, "enable", cfg.reference))
        self.assertTrue(result.committed, result.failure)
        returned = m.configuration
        self.assertEqual(subject(m), active_subject)
        for i, role in enumerate(("current", "reset")):
            state = getattr(returned, role)
            self.assertEqual(
                state.C,
                tuple(roles[i].get_state().nodes[j].coherence for j in range(17)),
            )
            self.assertEqual(
                state.W_A, expected_history[i] if expected_history else None
            )
            if cfg.reference.profile.identity_payload.realization in ("PC", "CI+PC"):
                self.assertTrue(any(getattr(cfg, role).Z_4))
                self.assertEqual(set(state.Z_4), {0.0})
        before_reset = m.step_v4_input(step_request("target-enabled-after-return"))
        self.assertTrue(before_reset.committed, before_reset.failure)
        self.assertNotEqual(m.configuration.current, returned.current)
        clock = (m.configuration.step_index, m.configuration.time)
        self.assertTrue(m.reset().committed)
        self.assertEqual(m.configuration.current, returned.reset)
        self.assertEqual((m.configuration.step_index, m.configuration.time), clock)
        final = m.snapshot()
        self.assertEqual(encoded(GRC9V4.from_state(final).snapshot()), encoded(final))
        self.assertEqual("basin_attributes" in m.compute_observables(), basin)
        # Real successful parents survive the round trip; failure receipts are
        # tested separately and may never enter this committed journal.
        groups = []
        for r in m.receipt_ledger:
            if not groups or groups[-1][0].commit_id != r.commit_id:
                groups.append([])
            groups[-1].append(r)
        for i, group in enumerate(groups):
            for r in group:
                self.assertEqual(
                    list(r.identity_payload["core"]["parent_receipt_ids"]),
                    [] if i == 0 else [groups[i - 1][0].receipt_id],
                )
        EVIDENCE["v2" if basin else "v1"] = dict(
            source_subject=original_subject,
            subject=active_subject,
            outcome="successful_target_compatibility",
            surfaces={
                s: "passed" for s in ("transition", "state", "observable", "lifecycle")
            },
            input_target_digest=digest(target(self.FAMILY)),
            source_role_resources_equal=cfg.current.C == cfg.reset.C,
            distinct_incoming_role_declarations=True,
            distinct_roles_after_legacy_step=True,
            independent_projection=projected,
            entry_checkpoint=entry,
            observations=observations,
            disabled_checkpoint=disabled,
            return_initializers=expected_history,
            returned_roles={
                k: asdict(getattr(returned, k)) for k in ("current", "reset")
            },
            enabled_continuation=asdict(before_reset),
            final_checkpoint=final,
            history_policy=("no_independent_candidate_or_carrier_history" if self.FAMILY == "C_RG2b" else f"explicit_{self.FAMILY}_carrier_loss_and_zero_initialization" if self.FAMILY in ("C_PC", "C_CI_PC")
                            else "explicit_A_archive_loss_and_A_CI_PC_carrier_zero_initialization" if self.FAMILY == "A_CI_PC"
                            else "explicit_A_archive_loss_and_A_PC_carrier_zero_initialization"),
            disabled_replay=True,
            enabled_replay=True,
            full_parent_DAG=True,
        )

    def test_exact_accepted_target_four_surfaces(self):
        self.roundtrip(False)

    def test_explicit_basin_successor_four_surfaces(self):
        self.roundtrip(True)

    def rejected(self, model, callback, *, injected_exception=False):
        before, pub = encoded(model.snapshot()), model._operation._published
        if injected_exception:
            with self.assertRaisesRegex(RuntimeError, "late publication pressure"):
                callback()
            failure = dict(
                kind="injected_exception", exception="RuntimeError", full_rollback=True
            )
        else:
            value = callback()
            self.assertFalse(value.committed)
            self.assertEqual(
                value.failure.prestate_digest, value.failure.poststate_digest
            )
            self.assertEqual(
                value.failure.pre_lifecycle_digest, value.failure.post_lifecycle_digest
            )
            self.assertEqual(value.emitted_receipts, (value.failure.failure_receipt,))
            self.assertNotIn(value.failure.failure_receipt, model.receipt_ledger)
            failure = asdict(value.failure)
        self.assertIs(model._operation._published, pub)
        self.assertEqual(encoded(model.snapshot()), before)
        return failure

    def test_excluded_domain_replay_tampering_and_late_failure(self):
        m = self.model()
        self.assertTrue(m.migrate_basin_policy("pressure-basin-opt-in").committed)
        cfg = m.configuration
        active_subject = subject(m)
        failures = {}
        req = request(m, "disable").to_payload()
        bad = deepcopy(req)
        bad["declaration"]["reset_incoming_weights"][-1] = 0.0
        failures["reset_only_entry"] = self.rejected(
            m, lambda: m.migrate_branch(GRC9V4BranchRequest.from_payload(bad))
        )
        bad = deepcopy(req)
        bad["declaration"]["legacy_config"]["constitutive_semantic_modes"][
            "hessian_backend"
        ] = "weighted_least_squares"
        # This is a valid native legacy mode, explicitly outside the V4 crossing
        # contract. Direct native construction is the passing control.
        direct, _ = independent_entry(cfg, bad["declaration"], "current")
        self.assertEqual(
            direct.get_params().constitutive_semantic_modes["hessian_backend"],
            "weighted_least_squares",
        )
        failures["native_hessian_mode_outside_crossing"] = self.rejected(
            m, lambda: m.migrate_branch(GRC9V4BranchRequest.from_payload(bad))
        )
        with patch.object(
            m._operation,
            "_publish",
            side_effect=RuntimeError("late publication pressure"),
        ):
            failures["late_entry"] = self.rejected(
                m,
                lambda: m.migrate_branch(GRC9V4BranchRequest.from_payload(req)),
                injected_exception=True,
            )
        self.assertTrue(
            m.migrate_branch(GRC9V4BranchRequest.from_payload(req)).committed
        )
        checkpoint = m.snapshot()
        bad = request(m, "enable", cfg.reference).to_payload()
        bad["declaration"]["target_reference"] = target_seed(self.FAMILY)["initial"]["inputs"]["reference"]
        failures["source_graph_substituted_for_target"] = self.rejected(
            m, lambda: m.migrate_branch(GRC9V4BranchRequest.from_payload(bad))
        )
        import pygrc.models.grc_9_v4_crossing as crossing

        native_return = crossing._return_role

        def fail_reset(ref, native, role):
            if role == "reset":
                raise ValueError("reset readmission pressure")
            return native_return(ref, native, role)

        with patch.object(crossing, "_return_role", side_effect=fail_reset):
            failures["reset_only_return"] = self.rejected(
                m, lambda: m.migrate_branch(request(m, "enable", cfg.reference))
            )
        with patch.object(
            m._operation,
            "_publish",
            side_effect=RuntimeError("late publication pressure"),
        ):
            failures["late_return"] = self.rejected(
                m,
                lambda: m.migrate_branch(request(m, "enable", cfg.reference)),
                injected_exception=True,
            )
        tampered = deepcopy(checkpoint)
        tampered["owner"]["journal"][-1]["request"]["declaration"][
            "reset_incoming_flux"
        ][0] += 0.5
        with self.assertRaises(ValueError):
            GRC9V4.from_state(tampered)
        # Failed operations leave a replayable successful prefix unchanged.
        self.assertEqual(
            encoded(GRC9V4.from_state(m.snapshot()).snapshot()), encoded(checkpoint)
        )
        EVIDENCE["pressure"] = dict(
            subject=active_subject,
            outcome="rejection_controls_not_successful_compatibility",
            failures=failures,
            native_hessian_mode_accepted=True,
            replay_tampering_rejected=True,
            complete_publication_rollback=True,
            failed_actions_absent_from_journal=True,
        )


class COSCompatibility(TargetCompatibility):
    FAMILY = "C_OS"


class CCICompatibility(TargetCompatibility):
    FAMILY = "C_CI"


class ACICompatibility(TargetCompatibility):
    FAMILY = "A_CI"


class APCCompatibility(TargetCompatibility):
    FAMILY = "A_PC"
