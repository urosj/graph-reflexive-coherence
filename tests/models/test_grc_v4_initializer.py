"""P9-7.2a: independent reference-pass oracle and actual crossing pressure."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as F
from math import exp, log
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest
from unittest.mock import patch

from pygrc.models.grc_v4 import GRCV4
from pygrc.models.grc_v4_candidate_a import A_SITE_POTENTIAL, CandidateACurrent
from pygrc.models.grc_v4_codec import (
    INITIALIZER_SNAPSHOT_LAYOUT_ID, INITIALIZER_RELEASE_ID, RELEASE_ID,
    MIGRATION_SNAPSHOT_LAYOUT_ID, V4IdentityError, V4SchemaError,
    canonical_json_bytes, initializer_identity, snapshot_payload, validate_payload,
)
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_initializer import (
    CandidateAReferencePass as Pass, CandidateAReferencePassPair as Pair,
    InitializerStageError, HISTORY_POLICY,
)
from pygrc.models import grc_v4_lifecycle as lifecycle
from pygrc.models.grc_v4_migration import map_migration
from tests.models.test_grc_v4_candidate_a import fixture as raw_fixture
from tests.models.test_grc_v4_migration import (
    fixture, owner_for, migration, changed_reference, restore, request,
    rehash_receipt_chain,
)
from tests.models.test_grc_v4_generic_lifecycle import endpoint

EVIDENCE = {}
FAMILIES = ('A_OS', 'A_CI', 'A_PC', 'A_CI_PC', 'A_RG2b')


def target(family='A_OS', **params):
    inputs, backend = fixture(family)
    ref = changed_reference(inputs.geometry.reference, 'lifecycle', history_policy_id=HISTORY_POLICY)
    ref = changed_reference(ref, 'candidate', **{**dict(alpha=-log(2)/2, beta=.001, gamma=.001), **params})
    return ref, backend


def raw(**kwargs):
    kwargs.setdefault('site_potential_id', A_SITE_POTENTIAL)
    ref, backend = raw_fixture(**kwargs)
    return changed_reference(ref, 'lifecycle', history_policy_id=HISTORY_POLICY), backend


def oracle(ref, backend, C):
    """Independent rational Gaussian elimination, edge accumulation and law.

    Never calls the production gradient, incidence, conductance or initializer.
    Rounding boundaries are explicit; no Decimal process-context dependence.
    """
    nodes = ref.graph.live_node_ids
    edges = [(nodes.index(e.tail_node_id), nodes.index(e.head_node_id), e.edge_id)
             for e in ref.graph.oriented_edges]
    dim = backend.dimension
    gradients = []
    for i in range(len(C)):
        matrix = [[F(backend.regularization) if a == b else F(0) for b in range(dim)] + [F(0)] for a in range(dim)]
        for u, v, eid in edges:
            if i not in (u, v):
                continue
            j = v if i == u else u
            dx = [F(y)-F(x) for x, y in zip(backend.positions[i], backend.positions[j])]
            w = F(backend.reference_weights[eid])
            for a in range(dim):
                matrix[a][-1] += w*dx[a]*(F(C[j])-F(C[i]))
                for b in range(dim):
                    matrix[a][b] += w*dx[a]*dx[b]
        for pivot in range(dim):
            divisor = matrix[pivot][pivot]
            matrix[pivot] = [x/divisor for x in matrix[pivot]]
            for row in range(dim):
                if row != pivot:
                    factor = matrix[row][pivot]
                    matrix[row] = [x-factor*y for x, y in zip(matrix[row], matrix[pivot])]
        gradients.append(tuple(float(row[-1]) for row in matrix))
    p = ref.profile.params_resolved.candidate
    exponents = [-(F(p.alpha)*(F(C[u])+F(C[v])) + F(p.beta)*sum(
        ((F(x)-F(y))**2 for x, y in zip(gradients[u], gradients[v])), F(0)))/2 for u, v, _ in edges]
    weights = [max(p.W_floor, exp(float(e))) if e >= -1000 else p.W_floor for e in exponents]
    potential = [F(0)]*len(C)
    for (u, v, _), w in zip(edges, weights):
        contribution = F(p.kappa_c)*F(w)*(F(C[u])-F(C[v]))
        potential[u] += contribution
        potential[v] -= contribution
    potential = [float(x) or 0.0 for x in potential]
    flux = [float(-F(p.eta*w)*(F(potential[u])-F(potential[v]))) or 0.0 for (u, v, _), w in zip(edges, weights)]
    final = [max(p.W_floor, exp(float(e-F(p.gamma)*F(j)**2/2))) for e, j in zip(exponents, flux)]
    return dict(W_base=weights, Phi_base=potential, J_ref=flux), final


class ProducerTests(unittest.TestCase):
    def test_active_channels_signed_gamma_and_graph_coordinates(self):
        nodes = ('a', 'b', 'c', 'isolate')
        edges = (OrientedEdge('ab', 'a', 'b'), OrientedEdge('ab2', 'a', 'b'),
                 OrientedEdge('bc', 'b', 'c'), OrientedEdge('loop', 'c', 'c'))
        positions = dict(a=(0., 0.), b=(1., .25), c=(.5, 1.), isolate=(2., 3.))
        resources = dict(a=.75, b=1.125, c=.875, isolate=.5)
        outputs = {}
        for gamma in (-.3, .3):
            for permutation in (False, True):
                order = nodes[::-1] if permutation else nodes
                oriented = tuple(OrientedEdge(e.edge_id, e.head_node_id, e.tail_node_id) for e in edges[::-1]) if permutation else edges
                graph = GRCV4Graph(order, oriented)
                ref, backend = raw(graph=graph, positions=tuple(positions[n] for n in order), dimension=2,
                                   weights=dict(ab=.75, ab2=1.25, bc=1.5, loop=.5),
                                   alpha=-.2, beta=.35, gamma=gamma, eta=.3, kappa_c=.4)
                C = tuple(resources[n] for n in order)
                actual = Pass(ref, backend, C, 'current')
                derived, final = oracle(ref, backend, C)
                self.assertEqual(actual.payload.to_dict()['derived'], derived)
                self.assertEqual(list(actual.W_A_init), final)
                self.assertEqual(derived['Phi_base'][order.index('isolate')], 0.)
                self.assertEqual(derived['J_ref'][graph.live_edge_ids.index('loop')], 0.)
                outputs[gamma, permutation] = (dict(zip(graph.live_edge_ids, final)), dict(zip(graph.live_edge_ids, derived['J_ref'])))
                EVIDENCE['oracle_' + str(gamma) + '_' + str(permutation)] = actual.to_record()
            self.assertEqual(outputs[gamma, False][0], outputs[gamma, True][0])
            self.assertEqual(outputs[gamma, False][1], {k: -v or 0. for k, v in outputs[gamma, True][1].items()})
        self.assertNotEqual(outputs[-.3, False][0], outputs[.3, False][0])

    def test_equal_operands_still_invoke_twice_and_separate_roles(self):
        ref, backend = raw(alpha=.1, beta=.2, gamma=.3)
        with patch.object(type(backend), 'rebuild', autospec=True, wraps=None, side_effect=type(backend).rebuild) as calls:
            pair = Pair.construct(ref, backend, (1., 2.), (1., 2.))
        self.assertEqual(calls.call_count, 2)
        self.assertEqual(pair.current.W_A_init, pair.reset.W_A_init)
        self.assertNotEqual(pair.current.to_record()['construction_id'], pair.reset.to_record()['construction_id'])
        self.assertEqual(Pair.from_record(pair.to_record()), pair)

    def test_auxiliary_singular_final_regular_without_total_current_call(self):
        ref, backend = raw(alpha=0., beta=0., gamma=2*log(2), eta=.5, kappa_c=1., chi_A=1., zeta_A=3., W_floor=.25)
        ref = changed_reference(ref, 'solver', absolute_tolerance=1e-12, relative_tolerance=1e-12)
        ref = changed_reference(ref, 'realization', tolerance=10.)
        with patch('pygrc.models.grc_v4_candidate_a.CandidateACurrent', side_effect=AssertionError('auxiliary current is forbidden')):
            actual = Pass(ref, backend, (1., 0.), 'current')
        self.assertEqual(actual.payload['derived']['W_base'], (1.,))
        self.assertEqual(actual.payload['derived']['J_ref'], (-1.,))
        self.assertEqual(actual.W_A_init, (.5,))
        # The regression is about real constitutive admission, not just an output.
        from tests.models.test_grc_v4_realizations import a_os_fixture
        inputs, _ = a_os_fixture(C=(1., 0.), W=(1.,), alpha=0., beta=0., gamma=2*log(2), eta=.5, kappa_c=1., chi_A=1., zeta_A=3., W_floor=.25)
        with self.assertRaises(ValueError) as caught:
            CandidateACurrent(inputs, backend)
        self.assertEqual(caught.exception.disposition, 'singular')
        final = replace(inputs, geometry=ref.geometry(), context=ref.context,
                        current=replace(inputs.current, W_A=actual.W_A_init), reset=replace(inputs.reset, W_A=actual.W_A_init))
        CandidateACurrent(final, backend)
        source, _ = fixture('C_OS')
        state = replace(source.current, C=(1., 0.))
        source = replace(source, current=state, reset=state, Q_target=1.)
        owner, _ = owner_for('C_OS', 'A_OS', source_inputs=source, target_ref=ref)
        result = owner.migrate_profile(migration(owner, ref))
        self.assertTrue(result.committed, result.failure)
        self.assertEqual(owner.state.lifecycle.current.W_A, (.5,))
        EVIDENCE['auxiliary_singular'] = actual.to_record()

    def test_final_law_uses_unfloored_exponent_and_one_combined_sum(self):
        ref, backend = raw(alpha=2., beta=0., gamma=-128., W_floor=.25, eta=1., kappa_c=1.)
        actual = Pass(ref, backend, (1., 0.), 'current')
        derived, expected = oracle(ref, backend, (1., 0.))
        self.assertEqual(actual.W_A_init, tuple(expected))
        # Force the auxiliary floor active: E=-2, J=-1/8, final E=-1.
        ref = changed_reference(ref, 'candidate', alpha=4.)
        actual = Pass(ref, backend, (1., 0.), 'current')
        self.assertEqual(actual.payload['derived']['W_base'], (.25,))
        self.assertEqual(actual.W_A_init, (exp(-1.),))
        self.assertNotEqual(actual.W_A_init, (.25*exp(1.),))
        # Exact cancellation before binary64 rounding, even with huge channels.
        ref, backend = raw(alpha=1e308, beta=0., gamma=-1e308, W_floor=1., eta=.5, kappa_c=1.)
        self.assertEqual(Pass(ref, backend, (1., 0.), 'current').W_A_init, (1.,))

    def test_subnormal_and_signed_zero_are_retained_without_mobility_floor(self):
        tiny = float.fromhex('0x0.0000000000001p-1022')
        ref, backend = raw(alpha=2000., beta=0., gamma=0., W_floor=tiny, eta=1., kappa_c=1.)
        actual = Pass(ref, backend, (1., 0.), 'current')
        self.assertEqual(actual.W_A_init, (tiny,))
        self.assertEqual(actual.payload['derived']['J_ref'], (0.,))
        self.assertNotIn(b'-0', canonical_json_bytes(actual.to_record()))
        ref = changed_reference(ref, 'candidate', eta=.5)
        with self.assertRaises(InitializerStageError) as caught:
            Pass(ref, backend, (1., 0.), 'reset')
        self.assertEqual((caught.exception.role, caught.exception.stage), ('reset', 'auxiliary_mobility'))

    def test_range_failures_preserve_actual_stage(self):
        for stage, values in (
            ('auxiliary_conductance', dict(alpha=-2000.)),
            ('auxiliary_mobility', dict(W_floor=2., eta=1e308)),
            ('reference_potential', dict(W_floor=2., kappa_c=1e308)),
            ('reference_flux', dict(eta=1e308, kappa_c=1.)),
            ('final_conductance', dict(gamma=-2000., eta=.5, kappa_c=1.)),
            ('final_mobility', dict(gamma=-1., eta=1e308, kappa_c=1e-308)),
        ):
            ref, backend = raw(**dict(dict(alpha=0., beta=0., gamma=0.), **values))
            with self.subTest(stage=stage), self.assertRaises(InitializerStageError) as caught:
                Pass(ref, backend, (1., 0.), 'current')
            self.assertEqual(caught.exception.stage, stage)

    def test_potential_rounds_whole_component_not_overflowing_partial_product(self):
        ref, backend = raw(alpha=0., beta=0., gamma=0., W_floor=1e308, eta=1e-308, kappa_c=1e-308)
        actual = Pass(ref, backend, (2., 0.), 'current')
        derived, weights = oracle(ref, backend, (2., 0.))
        self.assertEqual(actual.payload.to_dict()['derived'], derived)
        self.assertEqual(list(actual.W_A_init), weights)
        self.assertEqual(1e308*2., float('inf'))

    def test_rehashed_output_intermediates_and_roles_do_not_certify_production(self):
        ref, backend = raw(alpha=.1, beta=.2, gamma=.3)
        pair = Pair.construct(ref, backend, (1., 2.), (1.5, 1.5)).to_record()
        for field in ('W_A_init', 'W_base', 'Phi_base', 'J_ref'):
            bad = deepcopy(pair)
            row = bad['payload']['current']
            obj = row['payload'] if field == 'W_A_init' else row['payload']['derived']
            obj[field][0] += .125
            row['construction_id'] = initializer_identity('construction_payload', row['payload'])
            bad['initializer_pair_id'] = initializer_identity('pair_payload', bad['payload'])
            with self.subTest(field=field), self.assertRaises(V4IdentityError):
                Pair.from_record(bad)
        row = Pass(ref, backend, (1., 2.), 'current', False).to_record()
        self.assertIsNone(row['payload']['derived'])
        self.assertEqual(Pass.from_record(row).to_record(), row)
        bad = deepcopy(pair)
        bad['payload']['reset'] = deepcopy(bad['payload']['current'])
        with self.assertRaises(ValueError):
            bad['initializer_pair_id'] = initializer_identity('pair_payload', bad['payload'])
            Pair.from_record(bad)


class CrossingTests(unittest.TestCase):
    def positive(self, family):
        ref, backend = target(family)
        owner, _ = owner_for('C_PC', family, target_ref=ref)
        self.assertTrue(owner.step_v4_input(request(0., 'seed')).committed)
        before, prior = owner.snapshot(), owner.state.lifecycle
        declared = migration(owner, ref)
        result = owner.migrate_profile(declared)
        self.assertTrue(result.committed, result.failure)
        after, state = owner.snapshot(), owner.state.lifecycle
        self.assertEqual(after['implementation_layout_id'], INITIALIZER_SNAPSHOT_LAYOUT_ID)
        self.assertEqual(after['specification_release_id'], INITIALIZER_RELEASE_ID)
        archive = after['transition_records'][-1]
        pair = Pair.from_record(archive['initializer_pair'])
        self.assertEqual(state.current.W_A, pair.current.W_A_init)
        self.assertEqual(state.reset.authoritative.W_A, pair.reset.W_A_init)
        self.assertNotEqual(pair.current.W_A_init, pair.reset.W_A_init)
        for old, new in ((prior.current, state.current), (prior.reset.authoritative, state.reset.authoritative)):
            self.assertEqual(old.C, new.C)
            self.assertEqual(new.Z_4, (0.,) if family in ('A_PC', 'A_CI_PC') else None)
        self.assertEqual((prior.time, prior.step_index, prior.Q_target), (state.time, state.step_index, state.Q_target))
        primary = result.emitted_receipts[0].identity_payload
        self.assertEqual(primary['initializer_pair_id'], pair.to_record()['initializer_pair_id'])
        self.assertIsNone(primary['history']['candidate']['source_history_digest'])
        self.assertEqual(primary['core']['information_losses'], ('carrier_history_loss',))
        self.assertEqual(restore(after).snapshot(), after)
        duplicate = owner.duplicate()
        owner.reset()
        self.assertEqual(owner.state.lifecycle.current, state.reset.authoritative)
        self.assertEqual(duplicate.snapshot(), after)
        self.assertEqual(restore(owner.snapshot()).snapshot(), owner.snapshot())
        continuation = duplicate.step_v4_input(request(fixture(family)[0].dt, 'continuation'))
        self.assertTrue(continuation.committed, continuation.failure)
        self.assertNotEqual(duplicate.state.lifecycle.current.W_A, pair.current.W_A_init)
        self.assertEqual(restore(duplicate.snapshot()).snapshot(), duplicate.snapshot())
        if family == 'A_OS':
            with TemporaryDirectory(prefix='p972a-initializer-') as directory:
                path = Path(directory) / 'snapshot.json'
                duplicate.save(str(path))
                code = 'from pygrc.models.grc_v4 import GRCV4; from pygrc.models.grc_v4_codec import canonical_json_bytes; import sys; sys.stdout.buffer.write(canonical_json_bytes(GRCV4.load(sys.argv[1]).snapshot()))'
                loaded = subprocess.run([sys.executable, '-c', code, str(path)], capture_output=True, check=True)
                self.assertEqual(loaded.stdout, canonical_json_bytes(duplicate.snapshot()))
        replay = restore(before)
        self.assertEqual(replay.migrate_profile(declared), result)
        self.assertEqual(replay.snapshot(), after)
        EVIDENCE[family] = dict(initial=fixture('C_PC')[0].to_payload(), target_reference=ref.to_payload(),
                                differential_reference=backend.to_payload(), before=endpoint(before),
                                request=declared.to_payload(), after=endpoint(after), archive=archive,
                                receipts=[row.to_payload() for row in result.emitted_receipts],
                                reset=endpoint(owner.snapshot()), continuation=endpoint(duplicate.snapshot()))

    def test_nontrivial_negative_gamma_migration_and_return_to_C(self):
        from tests.models.test_grc_v4_candidate_c import current_fixture as c_inputs
        from tests.models.test_grc_v4_realizations import a_os_fixture
        graph = GRCV4Graph(('a', 'b', 'c'), (OrientedEdge('ab', 'a', 'b'),
                            OrientedEdge('bc', 'b', 'c'), OrientedEdge('ca', 'c', 'a')))
        C = (2.0625, 2., 1.9375)
        source = c_inputs(graph=graph, resource=C,
                          changes={'realization': {'tolerance': 10.}, 'geometry': {'kappa_H': .001}})
        source = replace(source, reset=replace(source.reset, C=(2., 2., 2.)))
        inputs, backend = a_os_fixture(graph=graph, C=C, W=(2.,)*3, alpha=-log(2)/2,
                                      beta=.1, gamma=-.01, eta=.01, kappa_c=.1)
        ref = changed_reference(inputs.geometry.reference, 'lifecycle', history_policy_id=HISTORY_POLICY)
        owner = GRCV4(source, targets=(ref,), target_differential_references=(backend,))
        declared = migration(owner, ref)
        result = owner.migrate_profile(declared)
        self.assertTrue(result.committed, result.failure)
        archived = owner.snapshot()['transition_records'][0]['initializer_pair']
        for role, c in (('current', C), ('reset', (2., 2., 2.))):
            d, w = oracle(ref, backend, c)
            self.assertEqual(archived['payload'][role]['payload']['derived'], d)
            self.assertEqual(archived['payload'][role]['payload']['W_A_init'], w)
        # Returning to C keeps the A crossing proof, with null on the later row.
        returned = owner.migrate_profile(migration(owner, source.geometry.reference, operation='return'))
        self.assertTrue(returned.committed, returned.failure)
        snap = owner.snapshot()
        self.assertIsNone(snap['transition_records'][1]['initializer_pair'])
        self.assertEqual(restore(snap).snapshot(), snap)
        bad = deepcopy(snap)
        bad['transition_records'][1]['initializer_pair'] = archived
        with self.assertRaises(ValueError):
            restore(bad)
        EVIDENCE['nontrivial_migration'] = dict(initial=source.to_payload(), request=declared.to_payload(),
                                                initializer_pair=archived, return_endpoint=endpoint(snap))

    def test_source_carrier_and_realization_do_not_change_producer(self):
        ref, backend = target()
        records = []
        for source in ('C_OS', 'C_PC'):
            owner, _ = owner_for(source, 'A_OS', target_ref=ref)
            result = owner.migrate_profile(migration(owner, ref))
            self.assertTrue(result.committed, result.failure)
            records.append(owner.snapshot()['transition_records'][0]['initializer_pair'])
        self.assertEqual(records[0], records[1])

    def test_real_reset_only_overflow_and_fixed_chart_failure_roll_back(self):
        source, _ = fixture('C_OS')
        # Same charge, distinct differences. Only reset overflows final gamma law.
        source = replace(source, current=replace(source.current, C=(2., 2.)),
                         reset=replace(source.reset, C=(2.25, 1.75)))
        ref, _ = target()
        ref = changed_reference(ref, 'candidate', gamma=-1e308, eta=1., kappa_c=1.)
        for family, reference, inputs, expected_stage in (
            ('A_OS', ref, source, 'target_construction'),
            ('A_RG2b', changed_reference(target('A_RG2b')[0], 'candidate', alpha=0., beta=0., gamma=0.), None, 'target_readmission'),
        ):
            owner, _ = owner_for('C_OS', family, source_inputs=inputs, target_ref=reference)
            old, snapshot = owner._operation._owned, owner.snapshot()
            result = owner.migrate_profile(migration(owner, reference))
            self.assertFalse(result.committed)
            self.assertEqual(result.failure.stage, expected_stage)
            if inputs is not None:
                self.assertIn('reset:final_conductance', result.failure.message)
            self.assertIs(owner._operation._owned, old)
            self.assertEqual(owner.snapshot(), snapshot)
            EVIDENCE[expected_stage] = dict(request=migration(owner, reference).to_payload(), before=snapshot,
                                            failure=result.failure.to_payload())

    def test_programmer_and_late_publication_failures_propagate_atomically(self):
        ref, _ = target()
        owner, _ = owner_for('C_OS', 'A_OS', target_ref=ref)
        old, snapshot = owner._operation._owned, owner.snapshot()
        for method in ('pygrc.models.grc_v4_initializer.CandidateAReferencePassPair.construct',
                       'pygrc.models.grc_v4_lifecycle._validate_publication'):
            fault = V4IdentityError('deliberate invariant fault')
            with patch(method, side_effect=fault), self.assertRaises(V4IdentityError) as caught:
                owner.migrate_profile(migration(owner, ref))
            self.assertIs(caught.exception, fault)
            self.assertIs(owner._operation._owned, old)
            self.assertEqual(owner.snapshot(), snapshot)

    def test_archive_pair_linkage_and_old_layout_cannot_be_forged(self):
        ref, _ = target()
        owner, _ = owner_for('C_OS', 'A_OS', target_ref=ref)
        self.assertTrue(owner.migrate_profile(migration(owner, ref)).committed)
        good = owner.snapshot()
        forged = deepcopy(good['transition_records'][0]['initializer_pair'])
        row = forged['payload']['current']
        row['payload']['W_A_init'][0] += .1
        row['construction_id'] = initializer_identity('construction_payload', row['payload'])
        forged['initializer_pair_id'] = initializer_identity('pair_payload', forged['payload'])
        before = fixture('C_OS')[0]
        from pygrc.models.grc_v4_migration import migration_history_policy
        with self.assertRaises(V4IdentityError):
            map_migration(before, ref, migration_history_policy(before, ref), forged)
        for alteration in ('missing', 'null', 'duplicate', 'receipt', 'output', 'old_layout'):
            bad = deepcopy(good)
            row = bad['transition_records'][0]
            if alteration == 'missing':
                del row['initializer_pair']
            elif alteration == 'null':
                row['initializer_pair'] = None
            elif alteration == 'duplicate':
                bad['transition_records'].append(deepcopy(row))
            elif alteration == 'old_layout':
                bad['implementation_layout_id'] = MIGRATION_SNAPSHOT_LAYOUT_ID
                bad['specification_release_id'] = RELEASE_ID
                del row['initializer_pair']
            elif alteration == 'receipt':
                bad['receipt_ledger'][0]['identity_payload']['initializer_pair_id'] = 'grcv4-a-reference-pass-pair-sha256:' + '0'*64
                rehash_receipt_chain(bad)
            else:
                pair = row['initializer_pair']
                current = pair['payload']['current']
                current['payload']['W_A_init'][0] += .01
                current['construction_id'] = initializer_identity('construction_payload', current['payload'])
                pair['initializer_pair_id'] = initializer_identity('pair_payload', pair['payload'])
                bad['receipt_ledger'][0]['identity_payload']['initializer_pair_id'] = pair['initializer_pair_id']
                rehash_receipt_chain(bad)
            with self.subTest(alteration=alteration), self.assertRaises(ValueError):
                restore(bad)
        payload = good['receipt_ledger'][0]['identity_payload']
        with self.assertRaises(V4SchemaError):
            validate_payload('migration_receipt_payload', payload)
        unknown = deepcopy(good)
        unknown['specification_release_id'] = 'grcv4-spec-release-sha256:' + '0'*64
        with self.assertRaises(ValueError):
            snapshot_payload(unknown)


for _family in FAMILIES:
    def _positive(self, family=_family):
        self.positive(family)
    setattr(CrossingTests, 'test_positive_' + _family, _positive)


if __name__ == '__main__':
    unittest.main()
