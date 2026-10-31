"""C_RG2b fresh section, exact target compatibility, and retained error scope."""
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
from tests.models import test_grc_9_v4_crg2b_integration as prior
import p9101a_basin_oracle as oracle
import p910_crg2b_basin_oracle as section_oracle
import test_p9101b_target_compatibility as targets
import test_p910_aos_basin as shared

EVIDENCE = {}


def source_configuration(family):
    if family != 'C_RG2b':
        raise ValueError('C_RG2b fixture provider')
    return dict(initial=targets.target_seed(family)['initial'],
                exact_backend='flint', numerical_policy='legacy_exact_v1')


class CRG2bNativeBasin(native.NativeBasinTests):
    FAMILY = 'C_RG2b'

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
                self.assertIsNone(read.inputs.current.W_A)
                self.assertIsNone(read.inputs.current.Z_4)
                oracle.captured_inputs(saved, role, captured.observation.to_dict(), read, point)
                roots[role] = oracle.root_payload(read, point)[0]
                equations[role] = section_oracle.capture(read, point, chains[i])
                section_oracle.validate(roots[role], equations[role])
                self.assertNotEqual(read.geometry, read.inputs.geometry.reference.geometry())
                with self.assertRaises(rg.RG2bStageError):
                    read.classical_jacobian()
            # One conserved source-resource redistribution, not invented W/Z.
            C = saved.inputs.current.C
            changed = replace(saved, inputs=replace(saved.inputs, current=replace(saved.inputs.current,
                                C=(C[0]+2**-12,C[1]-2**-12,*C[2:]))))
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
            # Resealed metadata alone cannot turn a different section into this read.
            for field, new in (('enclosure',['0','0']), ('certificate',{}), ('levels',5)):
                bad = deepcopy(roots['current']); bad[field] = new
                with self.assertRaises((ValueError,AssertionError)):
                    section_oracle.validate(bad,equations['current'])
        self.assertEqual(model._operation._published.owner.state.to_payload(),before)
        self.assertEqual(model.lifecycle_digest,lifetime)
        EVIDENCE['scientific'] = dict(source_state=before, source_role_equations=equations,
            selected_sections=roots, source_query_discrimination=True,
            changed_query_equation=other_equation, selected_current_separation=str(separation),
            combined_section_current_error_upper=str(error), no_independent_history=True,
            writer_not_invoked=True, wrong_query_rejected=True, unchanged_J_corrupt_H_rejected=True,
            observation_nonmutating=True, C1_claimed=False, exact_root_signs_claimed=False)


class CRG2bTargetCompatibility(shared.AOSTargetCompatibility):
    FAMILY = 'C_RG2b'

    @classmethod
    def setUpClass(cls):
        stack = ExitStack(); cls.addClassCleanup(stack.close)
        stack.enter_context(patch.object(targets,'legacy_config',prior.legacy_config))
        stack.enter_context(patch.object(shared,'EVIDENCE',EVIDENCE))


class CRG2bRetainedChecks(unittest.TestCase):
    def test_resealed_section_query_completion_geometry_enclosure_and_C1(self):
        import p910_family_basin as campaign
        value = campaign.check('C_RG2b')
        for kind in ('query','completion','geometry','enclosure','certificate','C1','scope'):
            bad = deepcopy(value); case = bad['direct_target']['observations'][0]
            selected = case['selected_roots']['current']
            if kind == 'query': selected['recipe']['inputs']['current']['C'][0] += 0.01
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
