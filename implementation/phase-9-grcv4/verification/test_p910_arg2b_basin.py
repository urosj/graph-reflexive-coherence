"""A_RG2b fresh section, exact target compatibility, and retained error scope."""
from contextlib import ExitStack
from copy import copy, deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

from pygrc.models import grc_9_v4_basin as basin
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge
from tests.models import test_grc_9_v4 as public
from tests.models import test_grc_9_v4_basin as native
from tests.models import test_grc_9_v4_arg2b_integration as prior
import p9101a_basin_oracle as oracle
import p910_arg2b_basin_oracle as section_oracle
import test_p9101b_target_compatibility as targets
import test_p910_aos_basin as shared

EVIDENCE = {}


def source_configuration(family):
    if family != 'A_RG2b':
        raise ValueError('A_RG2b fixture provider')
    return dict(initial=targets.target_seed(family)['initial'],
                exact_backend='flint', numerical_policy='legacy_exact_v1')


class ARG2bNativeBasin(native.NativeBasinTests):
    FAMILY = 'A_RG2b'

    @classmethod
    def setUpClass(cls):
        stack = ExitStack(); cls.addClassCleanup(stack.close)
        stack.enter_context(patch.object(native, 'configuration', source_configuration))
        stack.enter_context(patch.object(native, 'seed', targets.target_seed))
        stack.enter_context(patch.object(public, 'native_config', prior.legacy_config))
        super().setUpClass()

    def test_full_section_query_completion_and_independent_equations(self):
        from pygrc.models import grc_v4_rg2b as rg
        model = self.model(); saved = model._operation._published.owner.state
        before, lifetime = deepcopy(saved.to_payload()), model.lifecycle_digest
        equations, roots = {}, {}
        with exact_backend(ExactBackend.FLINT), patch.object(rg.ProvisionalCandidateRG2bStep, '__post_init__',
                side_effect=AssertionError('diagnostic invoked writer')):
            with section_oracle.capture_chains() as chains:
                pair = basin.capture_pair(saved)
            self.assertEqual(len(chains), 2)
            for i, (role, captured) in enumerate(zip(('current','reset'), pair, strict=True)):
                read, point = captured.read, captured.point
                self.assertEqual(point.inputs.geometry, read.geometry)
                self.assertEqual(point.inputs.stage, 'rg2b_section')
                self.assertIsNotNone(read.inputs.current.W_A)
                self.assertEqual(point.differential_reference,read.differential_reference)
                self.assertIsNone(read.inputs.current.Z_4)
                oracle.captured_inputs(saved, role, captured.observation.to_dict(), read, point)
                roots[role] = oracle.root_payload(read, point)[0]
                equations[role] = section_oracle.capture(read, point, chains[i])
                section_oracle.validate(roots[role], equations[role])
                self.assertNotEqual(read.geometry, read.inputs.geometry.reference.geometry())
                with self.assertRaises(rg.RG2bStageError):
                    read.classical_jacobian()
            # Change only positive W inside the accepted signed-log chart.
            # C, graph, backend and absence of carrier stay fixed.
            W = saved.inputs.current.W_A
            changed = replace(saved, inputs=replace(saved.inputs, current=replace(saved.inputs.current,
                                W_A=(W[0]*(1+2**-16),*W[1:]))))
            with section_oracle.capture_chains() as other_chains:
                other = basin.capture(changed, 'current')
            other_equation = section_oracle.capture(other.read, other.point, other_chains[0])
            separation = max(abs(Q(a)-Q(b)) for a,b in zip(pair[0].point.current.values,other.point.current.values))
            error = Q(equations['current']['section_current_error_upper']) + Q(other_equation['section_current_error_upper'])
            self.assertGreater(separation, error)
            with patch.object(basin, '_read_once', return_value=(other.read,other.point)):
                with self.assertRaisesRegex(ValueError, 'captured role inputs'):
                    model.compute_observables()
            read, point = pair[0].read, pair[0].point
            bad = copy(point); h = [list(r) for r in point.inputs.geometry.one_form_hodge.matrix]
            h[-1][-1] += 2**-8
            object.__setattr__(bad, 'inputs', replace(point.inputs, geometry=GRCV4Geometry(
                point.inputs.geometry.reference, OneFormHodge(point.inputs.geometry.reference.graph,tuple(map(tuple,h))))))
            self.assertEqual(bad.current,point.current)
            with patch.object(basin, '_read_once', return_value=(read,bad)):
                with self.assertRaisesRegex(ValueError, 'full RG2b section'):
                    model.compute_observables()
            bad_backend = copy(point)
            graph = point.differential_reference.port_graph
            edge = graph.edges[0]
            wrong_graph = replace(graph, edges=(replace(edge, tail=edge.head, head=edge.tail), *graph.edges[1:]))
            wrong_backend = type(point.differential_reference)(wrong_graph)
            object.__setattr__(bad_backend, 'differential_reference', wrong_backend)
            with patch.object(basin, '_read_once', return_value=(read,bad_backend)):
                with self.assertRaisesRegex(ValueError, 'RG2b A backend'):
                    model.compute_observables()
            # Resealed metadata alone cannot turn a different section into this read.
            for field, new in (('enclosure',['0','0']), ('certificate',{}), ('levels',5)):
                bad = deepcopy(roots['current']); bad[field] = new
                with self.assertRaises((ValueError,AssertionError)):
                    section_oracle.validate(bad,equations['current'])
        self.assertEqual(model._operation._published.owner.state.to_payload(),before)
        self.assertEqual(model.lifecycle_digest,lifetime)
        EVIDENCE['scientific'] = dict(source_state=before, source_role_equations=equations,
            selected_sections=roots, history_discrimination=True,
            changed_history_equation=other_equation, selected_current_separation=str(separation),
            combined_section_current_error_upper=str(error), fixed_row_A_backend=True, no_carrier=True,
            writer_not_invoked=True, wrong_history_query_rejected=True, wrong_backend_rejected=True, unchanged_J_corrupt_H_rejected=True,
            observation_nonmutating=True, C1_claimed=False, exact_root_signs_claimed=False)


class ARG2bTargetCompatibility(shared.AOSTargetCompatibility):
    FAMILY = 'A_RG2b'

    @classmethod
    def setUpClass(cls):
        stack = ExitStack(); cls.addClassCleanup(stack.close)
        stack.enter_context(patch.object(targets,'legacy_config',prior.legacy_config))
        stack.enter_context(patch.object(shared,'EVIDENCE',EVIDENCE))


class ARG2bRetainedChecks(unittest.TestCase):
    def test_resealed_section_query_completion_geometry_enclosure_and_C1(self):
        import p910_family_basin as campaign
        value = campaign.check('A_RG2b')
        for kind in ('query','history','backend','completion','geometry','enclosure','certificate','C1','scope','log_error'):
            bad = deepcopy(value); case = bad['direct_target']['observations'][0]
            selected = case['selected_roots']['current']
            if kind == 'query': selected['recipe']['inputs']['current']['C'][0] += 0.01
            elif kind == 'history': selected['recipe']['inputs']['current']['W_A'][0] *= 1.0001
            elif kind == 'backend': selected['recipe']['differential_reference'] = {}
            elif kind == 'log_error': case['role_equations']['current']['input_section_error_upper'] = '0'
            elif kind == 'completion': selected['recipe']['numerics'] = 'other'
            elif kind == 'geometry': selected['selected_inputs']['H1_form'][-1][-1] += 0.1
            elif kind == 'enclosure': selected['enclosure'] = ['0','0']
            elif kind == 'certificate': selected['certificate'] = {}
            elif kind == 'C1': case['role_equations']['current']['C1_claimed'] = True
            else: case['role_equations']['current']['exact_root_signs_claimed'] = True
            bad['direct_target'] = campaign.seal(bad['direct_target'])
            with self.subTest(kind=kind), self.assertRaises((ValueError,AssertionError)):
                campaign.validate(campaign.seal(bad),sources=False)


if __name__ == '__main__':
    unittest.main()
