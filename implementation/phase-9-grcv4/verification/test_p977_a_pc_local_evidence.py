"""Retained A_PC pressure: no repeated numerical campaign."""

from copy import deepcopy
import unittest
from unittest.mock import patch
import verify_p977_a_pc_local as audit


class APCLocalEvidenceTests(unittest.TestCase):
    def test_local_registry_does_not_publish_G2_and_preserves_prior_evidence(self):
        import profile_g2_registry as g
        from pygrc.models.grc_v4_profile import list_supported_profiles
        from test_p977_a_pc_local import NOMINATED
        registry = g.registry(audit.p.ROOT)
        view = registry['reconciliation_views']['a_pc_local_product']
        self.assertEqual(view['complete_profile_id'], NOMINATED)
        self.assertEqual(view['verified_local_cells'], 21)
        self.assertEqual(len(view['remaining_catalog_cases']), 7)
        self.assertFalse(view['G2_accepted'])
        self.assertFalse(view['user_accepted'])
        self.assertNotIn(NOMINATED, list_supported_profiles())
        self.assertEqual(len(list_supported_profiles()), 4)
        self.assertFalse(any(row['complete_profile_id']==NOMINATED for row in registry['records']))
        for name in audit.p.git(audit.p.ROOT,'ls-files',audit.p.PHASE+'tranche-7').decode().splitlines():
            if name.endswith('.json') and not name.endswith('ProfileG2Registry.json'):
                self.assertEqual((audit.p.ROOT/name).read_bytes(),audit.p.git(audit.p.ROOT,'show','c1b8813:'+name))

    def test_retained_product_and_rehashed_mutations(self):
        original = audit.review.read(audit.RECORD)
        audit.validate(original)
        def row(v, case):
            return next(r for r in v['fixture_results'] if r['fixture_id']==case)
        def science(v, edit):
            # Change every shared candidate-stage view coherently, so simple
            # duplicate-view equality cannot substitute for equation validation.
            for r in v['fixture_results']:
                if r['evidence_layer']=='independent_equations_and_provisional_stage_not_public_commit':
                    edit(r['observation'])
        changes = {
            'missing_row':lambda v:v['fixture_results'].pop(),
            'duplicate_row':lambda v:v['fixture_results'].append(deepcopy(v['fixture_results'][0])),
            'result_field':lambda v:v['fixture_results'][0].pop('solver_disposition'),
            'borrowed_profile':lambda v:v['fixture_results'][0].update(complete_profile_id='A_PC'),
            'source':lambda v:v['source_bindings'].update({audit.TEST:'0'*64}),
            'G2':lambda v:v.update(G2_accepted=True),
            'support':lambda v:v.update(new_G2_support=['A_PC']),
            'acceptance':lambda v:v.update(user_accepted=True),
            'authority':lambda v:v.update(authority={}),
            'invented_commit':lambda v:row(v,'PC-ZOH').update(solver_disposition='valid_root'),
            'delta':lambda v:row(v,'COMMON-VALID-ORDINARY-STEP').update(emitted_receipt_ids=[]),
            'failure':lambda v:row(v,'COMMON-CHARGE-MISMATCH').update(failure_code='domain_failure'),
            'current':lambda v:science(v,lambda o:o['stages'][0]['observed'].update(current=[999])),
            'coherent_wrong_Z':lambda v:science(v,lambda o:[o['stages'][0][k].update(written_Z=[999]) for k in ('observed','independent_oracle')]),
            'old_Z':lambda v:science(v,lambda o:o['stages'][1].update(writer_old_Z=[0.])),
            'writer_count':lambda v:science(v,lambda o:o['stages'][0].update(writer_count=2)),
            'carrier_count':lambda v:science(v,lambda o:o['stages'][0].update(carrier_writes=0)),
            'refreshed_source':lambda v:science(v,lambda o:o.update(source_policy='post_continuity_source')),
            'missing_reset':lambda v:science(v,lambda o:o['stages'][0]['admissions'].pop(0)),
            'bad_reset_current':lambda v:science(v,lambda o:o['stages'][0]['admissions'][0].update(current=[999])),
            'formation':lambda v:science(v,lambda o:o.update(supplied_W_is_not_formation=False)),
            'release_is_drop':lambda v:row(v,'A-CHI-ZERO')['observation'].update(written_Z=[0.]),
            'missing_late_failure':lambda v:v['readmission_pressure'].pop(),
            'early_only_failure':lambda v:v['readmission_pressure'][1].update(carrier_writes_before_rejection=0),
        }
        with patch.object(audit,'authority',return_value=original['authority']):
            for name, edit in changes.items():
                value = deepcopy(original); edit(value); value['record_digest']=audit.p.digest_record(value)
                with self.subTest(name=name), self.assertRaises((ValueError,KeyError)):
                    audit.validate(value)


if __name__=='__main__':
    unittest.main()
