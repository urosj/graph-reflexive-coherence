"""C_RG2b retained sections and bounded scope through real API/browser/notebook."""
from fractions import Fraction as Q
import unittest
from unittest.mock import patch
import test_p910_cpc_surfaces as shared


class CRG2bSurfaces(shared.CPCSurfaces):
    FAMILY = 'C_RG2b'
    ACCEPTED = False
    REMAINING = ['A_RG2b']
    HISTORICAL_FAMILY = 'A_CI_PC'
    CELL = 'p910-crg2b-basin'
    VARIABLE = 'phase9_crg2b_basin'

    def test_native_evidence_roles_and_carrier_loss(self):
        self.assertEqual(self.view['remaining_families'],self.REMAINING)
        self.assertFalse(self.view['user_accepted'])
        for case in self.evidence['direct_target']['observations']:
            for role in ('current','reset'):
                state=case['saved_native_state']['inputs'][role]
                self.assertIsNone(state['W_A']);self.assertIsNone(state['Z_4'])
                equation=case['role_equations'][role]
                self.assertFalse(equation['C1_claimed'])
                self.assertFalse(equation['exact_root_signs_claimed'])
                self.assertGreater(Q(equation['section_current_error_upper']),Q(equation['current_error_upper']))
                self.assertLessEqual(Q(equation['section_error_upper']),Q(1,2**48))
        returned=self.evidence['direct_target']['observations'][1]['saved_native_state']['inputs']
        self.assertNotEqual(returned['current']['C'],returned['reset']['C'])
        for version in ('v1','v2'):
            self.assertEqual(self.evidence['target_compatibility'][version]['history_policy'],
                             'no_independent_candidate_or_carrier_history')

    def test_exact_subjects_meet_independent_oracle_hypotheses(self):
        native, _ = shared.campaign.load(self.FAMILY, 'Native')
        payloads = [native['evidence']['scientific']['source_state'],
                    *[case['saved_native_state'] for case in self.evidence['direct_target']['observations']]]
        # Pin the independent connected proof's coefficients, not values supplied
        # by a producer's successful certificate or by an unrelated C fixture.
        for state in payloads:
            inputs = state['inputs']; ref = inputs['reference']
            params = ref['profile']['params_resolved']
            for key,value in dict(Lambda_C=2**-9,C_ref=1,kappa_M_C=2**-24,
                kappa_Phi_C=1,eta_C=1,tau_C=1,chi_C=16,zeta_C=2**-37).items():
                self.assertEqual(params['candidate'][key],value)
            self.assertEqual(params['geometry']['kappa_H'],0.5)
            self.assertEqual(params['realization']['extension_evaluator_id'],
                             'grc9v4_c_rg2b_connected_signed_argument_completion_v1')
            self.assertEqual(params['realization']['error_tolerance'],2**-48)
            self.assertEqual(params['realization']['iteration_limit'],222)
            self.assertTrue(all(v == 1 for v in params['candidate']['W_C_tr'].values()))
            self.assertTrue(all(v == 0 for row in ref['K4_base'] for v in row))
            self.assertEqual(inputs['context']['contract_id'],'constant_zero_context_v1')
            for role in ('current','reset'):
                self.assertTrue(all(0 <= c <= 4.5 for c in inputs[role]['C']))

    def test_section_chains_are_evidence_not_status_solve(self):
        from pygrc.models.grc_v4_rg2b import CandidateRG2bSection
        with patch.object(CandidateRG2bSection, '__post_init__', side_effect=AssertionError('native section rerun')):
            shared.campaign.check(self.FAMILY)
        import p910_crg2b_basin_oracle as oracle
        for case in self.evidence['direct_target']['observations']:
            for role in ('current','reset'):
                selected=case['selected_roots'][role]
                eq=case['role_equations'][role]
                oracle.validate(selected,eq)
                self.assertEqual(eq['section_record']['chain']['query'],
                                 case['saved_native_state']['inputs'][role]['C'])
                self.assertEqual(selected['levels'],6)
                self.assertEqual(selected['evaluations'],222)


if __name__ == '__main__':
    unittest.main()
