"""Reflection comparison and dispatch pressure without native trajectories."""
from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch
import p984h_cos_covariance_transforms as run

c = run.c


class IndividualTransformTests(unittest.TestCase):
    def test_paths_do_not_overwrite_predecessors(self):
        paths = [run.path(k, r) for k in run.KINDS for r in c.ROLES]
        self.assertEqual(len(set(paths)), 14)
        for kind in run.KINDS:
            for role in c.ROLES:
                self.assertNotEqual(run.path(kind, role), c.path(kind, role))
                self.assertNotEqual(run.path(kind, role), run.comparison.path(role))
        for kind in ('combined', 'all', 'unknown'):
            with self.assertRaises(ValueError):
                run.inputs(kind)
        with self.assertRaises(ValueError):
            run.path('reflect', 'event')

    def test_reflection_full_point_and_chart_pressure(self):
        with c.native.oracle.exact_backend(c.native.oracle.ExactBackend.FLINT), \
                c.native.oracle.numerical_policy(c.native.oracle.NumericalPolicy.CERTIFIED_ARB_256):
            seed, request, _, eid, expected = c.subject('reflect')
            baseline_event = c.base()[1]
            self.assertEqual(request['module_chirality'], -baseline_event['request']['module_chirality'])
            self.assertEqual(request['growth_phase'], 1)
            self.assertEqual(request['resource_distribution'], [0.25, 0.25, 0.5])
            source_graph = c.base()[0]['inputs']['reference']['graph']
            wrong = seed.inputs.to_payload()['reference']['graph']
            wrong['edges'][0]['tail']['port'] = 1 + wrong['edges'][0]['tail']['port'] % 9
            with self.assertRaises(ValueError):
                c.mapping(source_graph, wrong, c.declaration('reflect'))
            before = c.continuation.initial('current')
            baseline = c.continuation.read('current', 1)
            ni, ei, signs = c.mapping(before.to_payload()['reference']['graph'],
                expected.to_payload()['reference']['graph'], c.declaration('reflect'), baseline_event['event_id'], eid)
            np = c.native.np
            b, params = c.native.oracle.old.graph_data(dict(
                graph=before.geometry.reference.graph.port_graph.to_payload(),
                profile=before.geometry.reference.profile.to_payload()))
            h = c.native.oracle.old.generated_h(b, np.array(baseline['observation']['predictor']['causal_flat']), params)
            h = (h[np.ix_(ei, ei)] * np.outer(signs, signs)).tolist()
            geometry = dict(predictor=expected.to_payload()['H1_form'], corrector=h, final=h)
            row = deepcopy(baseline['observation'])
            for stage in ('predictor', 'corrector', 'final'):
                for field in ('current', 'baseline', 'read_flux', 'causal_flat'):
                    row[stage][field] = (np.asarray(row[stage][field])[ei] * np.asarray(signs)).tolist()
                row[stage]['input_hodge_digest'] = c.digest(geometry[stage])
            after = replace(expected, current=replace(expected.current,
                C=tuple(np.asarray(baseline['next_inputs']['current']['C'])[ni])))
            with patch.object(c.native, 'ProvisionalCandidateCOSStep', side_effect=AssertionError('native rerun')):
                result = run.comparison.compare_step('reflect', 'current', row, after, geometry)
                self.assertEqual(result['resources'], 0.)
                self.assertEqual(result['generated_geometry'], 0.)
                bad = deepcopy(geometry); bad['corrector'][0][0] = 123.
                with self.assertRaises(ValueError):
                    run.comparison.compare_step('reflect', 'current', row, after, bad)
                bad = deepcopy(row); bad['final']['input_hodge_digest'] = 'stale'
                with self.assertRaises(ValueError):
                    run.comparison.compare_step('reflect', 'current', bad, after, geometry)

    def test_retained_reflection_identity_and_role_pressure(self):
        if not (c.ROOT / run.path('reflect', 'reset')).exists():
            self.skipTest('reflection continuation not yet executed')
        with c.native.oracle.exact_backend(c.native.oracle.ExactBackend.FLINT), \
                c.native.oracle.numerical_policy(c.native.oracle.NumericalPolicy.CERTIFIED_ARB_256), \
                patch.object(c.native, 'ProvisionalCandidateCOSStep', side_effect=AssertionError('native rerun')), \
                patch.object(c.native.native, 'GRC9V4COSOperation', side_effect=AssertionError('event rerun')):
            event = c.read('reflect', 'event')
            old = c.native.oracle.old.read(c.INPUTS)
            for key, value in (('module_chirality', 1), ('growth_phase', 3),
                               ('resource_distribution', [0.5, 0.25, 0.25])):
                bad = deepcopy(event); bad['execution']['request'][key] = value
                with self.assertRaises(ValueError):
                    c.check_record(c.seal(bad), old, 'reflect', 'event')
            declaration = c.native.oracle.old.read(run.inputs('reflect'))
            for role in c.ROLES:
                record = run.read('reflect', role)
                run.check(record, declaration, 'reflect', role)
            record = run.read('reflect', 'current')
            for mutate in (
                lambda r: r.update(kind='rotate'),
                lambda r: r['execution'].update(event_record_digest='foreign'),
                lambda r: r['execution'].update(role='reset'),
                lambda r: r['execution']['observation'].update(split_admitted=False),
                lambda r: r['execution']['next_inputs']['reset']['C'].__setitem__(0, 123.),
            ):
                bad = deepcopy(record); mutate(bad)
                with self.assertRaises(ValueError):
                    run.check(c.seal(bad), declaration, 'reflect', 'current')


if __name__ == '__main__':
    unittest.main()
