"""A_RG2b bounded evidence through real API/browser/notebook; no native rerun."""
from fractions import Fraction as Q
import math
import unittest
from unittest.mock import patch
import test_p910_cpc_surfaces as shared


class ARG2bSurfaces(shared.CPCSurfaces):
    FAMILY = 'A_RG2b'
    ACCEPTED = True
    REMAINING = []
    HISTORICAL_FAMILY = 'C_RG2b'
    CELL = 'p910-arg2b-basin'
    VARIABLE = 'phase9_arg2b_basin'

    def test_native_evidence_roles_and_carrier_loss(self):
        self.assertEqual(self.view['remaining_families'],self.REMAINING)
        self.assertEqual(self.view['user_accepted'],self.ACCEPTED)
        self.assertTrue(self.view['P9_10_1_closed'])
        self.assertTrue(self.view['P9_10_2_closed'])
        self.assertFalse(self.evidence['user_accepted'])
        self.assertFalse(self.view.get('all_ten_P9_10_1_closed',False))
        self.assertFalse(self.view.get('all_ten_P9_10_2_closed',False))
        for case in self.evidence['direct_target']['observations']:
            for role in ('current','reset'):
                state=case['saved_native_state']['inputs'][role]
                self.assertIsNotNone(state['W_A']);self.assertIsNone(state['Z_4'])
                equation=case['role_equations'][role]
                self.assertFalse(equation['C1_claimed'])
                self.assertFalse(equation['exact_root_signs_claimed'])
                self.assertGreater(Q(equation['section_current_error_upper']),Q(equation['current_error_upper']))
                self.assertLessEqual(Q(equation['section_error_upper']),Q(1,2**48))
                self.assertGreater(Q(equation['input_log_coordinate_error_upper']),0)
        returned=self.evidence['direct_target']['observations'][1]['saved_native_state']['inputs']
        self.assertNotEqual(returned['current']['C'],returned['reset']['C'])
        self.assertNotEqual(returned['current']['W_A'],returned['reset']['W_A'])
        for i,role in enumerate(('current','reset')):
            self.assertEqual(returned[role]['W_A'],self.evidence['target_compatibility']['v2']['return_initializers'][i])
        for version in ('v1','v2'):
            self.assertEqual(self.evidence['target_compatibility'][version]['history_policy'],
                             'explicit_A_archive_loss_and_reference_initialization_no_carrier')

    def test_exact_subjects_meet_independent_oracle_hypotheses(self):
        from pygrc.models.grc_v4_geometry import GeometryStageInputs
        from dataclasses import replace
        import p910_arg2b_basin_oracle as oracle
        native,_=shared.campaign.load(self.FAMILY,'Native')
        payloads=[native['evidence']['scientific']['source_state'],
                  *[c['saved_native_state'] for c in self.evidence['direct_target']['observations']]]
        for state in payloads:
            inputs=GeometryStageInputs.from_payload(state['inputs'])
            for role in ('current','reset'):
                oracle.hypotheses(replace(inputs,current=getattr(inputs,role)))

    def test_section_chains_and_backend_are_evidence_not_status_solve(self):
        from pygrc.models.grc_v4_rg2b import CandidateRG2bSection
        from pygrc.models.grc_9_v4_topology import GRC9V4CandidateADifferentialReference
        with patch.object(CandidateRG2bSection,'__post_init__',side_effect=AssertionError('native section rerun')):
            shared.campaign.check(self.FAMILY)
        import p910_arg2b_basin_oracle as oracle
        for case in self.evidence['direct_target']['observations']:
            for role in ('current','reset'):
                selected=case['selected_roots'][role];eq=case['role_equations'][role]
                oracle.validate(selected,eq)
                state=case['saved_native_state']['inputs'];authority=state[role]
                self.assertEqual(eq['section_record']['chain']['query'],
                                 authority['C']+[512*math.log(w) for w in authority['W_A']])
                backend=GRC9V4CandidateADifferentialReference.from_payload(selected['recipe']['differential_reference'])
                self.assertEqual(backend.port_graph.to_payload(),state['reference']['graph'])
                self.assertEqual(selected['levels'],4);self.assertEqual(selected['evaluations'],148)


if __name__ == '__main__':
    unittest.main()
