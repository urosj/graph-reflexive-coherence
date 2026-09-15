"""Narrow C_RG2b facade supplement and read-only integrated-review pressure."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
import unittest

import phase9_implementation_policy as p
import verify_p977_profile_review as review


class InterfaceTests(unittest.TestCase):
    def test_exact_profile_configuration_strict_run_and_missing_defaults(self):
        from pygrc.core.interfaces import GRCModel
        from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequest, MissingV4StepRequest
        from pygrc.models.grc_v4_profile import list_supported_profiles
        from tests.models.test_grc_v4_generic_lifecycle import fixture
        from tests.models.test_grc_v4_lifecycle import request, primitive
        from test_p977_c_rg2b_local import NOMINATED
        from pygrc.models.grc_v4_rg2b_graph import RG2bGraphDomain

        inputs, backend = fixture('C_RG2b')
        self.assertIsNone(backend)
        config = dict(initial=inputs.to_payload())
        source = deepcopy(config)
        owner = GRCV4.from_config(config)
        self.assertIsInstance(owner, GRCModel)
        self.assertEqual(owner.active_model_identity, NOMINATED)
        initial = owner.snapshot()
        config['initial']['current']['C'][0] = 999
        config['initial']['reset']['C'][0] = -999
        self.assertEqual(owner.snapshot(), initial)
        self.assertEqual(owner.get_params(), inputs.geometry.reference.profile.params_resolved)
        with self.assertRaises(FrozenInstanceError):
            owner.get_params().realization.iteration_limit = 0
        owner.set_state(owner.get_state())
        self.assertEqual(owner.snapshot(), initial)
        self.assertEqual(owner.list_supported_profiles(), frozenset({NOMINATED}))
        self.assertEqual(owner.get_supported_profile(NOMINATED), inputs.geometry.reference.profile)
        self.assertNotIn(NOMINATED, list_supported_profiles())  # This G2 decision is still proposed.
        self.assertEqual(owner.run(0), [])
        for call, error in ((owner.step, MissingV4StepRequest), (lambda: owner.run(1), MissingV4StepRequest),
                            (lambda: owner.run(True), TypeError), (lambda: owner.run(-1), ValueError),
                            (lambda: owner.step_v4(request(0)), TypeError)):
            with self.assertRaises(error): call()
            self.assertEqual(owner.snapshot(), initial)
        malformed = deepcopy(source); malformed['cache'] = {}
        with self.assertRaises(ValueError): GRCV4.from_config(malformed)
        malformed = deepcopy(source); malformed['differential_reference'] = {}
        self.assertIsNone(owner._operation._backend)
        with self.assertRaises(ValueError):
            GRCV4.from_config(malformed)
        external = request(0, 'strict-zero')
        payload = external.to_payload(); payload['schema_version'] = 'grcv4-step-request-v1'
        strict = GRCV4StepRequest.from_payload(payload)
        comparison = GRCV4.from_config(source)
        result = owner.step_v4(strict)
        self.assertEqual(result, comparison.step_v4_input(external))
        self.assertTrue(result.committed)
        self.assertEqual(owner.snapshot(), comparison.snapshot())
        self.assertEqual(owner.snapshot()['scientific_state'], initial['scientific_state'])
        before_stream = owner.snapshot()
        payload['operation_id'] = 'stream-zero'
        second = GRCV4StepRequest.from_payload(payload)
        def interrupted():
            yield second
            raise RuntimeError('test-only interrupted request iterator')
        with self.assertRaisesRegex(RuntimeError, 'interrupted request iterator'):
            owner.run_v4(interrupted())
        after_stream = owner.snapshot()
        self.assertEqual(after_stream['scientific_state'], initial['scientific_state'])
        self.assertEqual(after_stream['reset'],initial['reset'])
        self.assertNotEqual(inputs.current.C,inputs.reset.C)
        self.assertIsNone(inputs.current.W_A);self.assertIsNone(inputs.reset.W_A)
        self.assertIsNone(inputs.current.Z_4);self.assertIsNone(inputs.reset.Z_4)
        domain=RG2bGraphDomain.from_identity(owner.get_params().realization.extension_evaluator_id)
        self.assertEqual(domain.beat_dt,inputs.dt)
        self.assertEqual(after_stream['reference'],initial['reference'])
        self.assertEqual(after_stream['receipt_ledger'][:-4], before_stream['receipt_ledger'])
        self.assertEqual(after_stream['receipt_ledger'][-4]['identity_payload']['core']['operation_id'], 'stream-zero')
        self.assertEqual(after_stream['commit_records'][:-1], before_stream['commit_records'])
        self.__class__.evidence = dict(source_config=source, initial_snapshot=initial,
            strict_request=strict.to_payload(), strict_result=primitive(result),
            before_stream=before_stream, stream_request=second.to_payload(), after_stream=after_stream,
            checks=dict(configuration_detached=True, immutable_parameters=True, unchanged_assignment=True,
                local_discovery_not_G2=True, missing_default_rejected=True, invalid_run_inputs_rejected=True,
                wrong_request_layer_rejected=True, extraneous_config_rejected=True, candidate_c_without_A_backend=True,
                strict_external_results_equal=True, interrupted_iterator_keeps_prior_commit=True,
                C_configuration_detached=True,reset_C_preserved=True,no_carrier_slot=True,no_candidate_history=True,frozen_completion_unchanged=True),
            frozen_completion_id=domain.identity,frozen_beat=domain.beat_dt,regularity='Lipschitz_only',
            operation_scope='zero_duration_interface_only; positive numerical step/replay remains in local product')


class ReviewTests(unittest.TestCase):
    def test_rehashed_interface_evidence_rejects_role_completion_and_scope_drift(self):
        import verify_p977_c_rg2b_g2 as gate
        original=review.read(gate.INTERFACE);gate.validate_interface(original)
        edits={
            'acceptance':lambda v:v.update(G2_accepted=True),
            'missing_method':lambda v:v['test_ids'].clear(),
            'source':lambda v:v['source_bindings'].update({gate.TEST:'0'*64}),
            'mutable_C':lambda v:v['evidence']['checks'].update(C_configuration_detached=False),
            'missing_reset':lambda v:v['evidence']['checks'].pop('reset_C_preserved'),
            'positive_duration':lambda v:v['evidence']['strict_request'].update(dt=.125),
            'invented_carrier':lambda v:v['evidence']['initial_snapshot']['scientific_state']['authoritative'].update(Z_4=[0.]),
            'reset_C':lambda v:v['evidence']['after_stream']['reset']['authoritative'].update(C=[2.]*4),
            'zero_completion_beat':lambda v:v['evidence'].update(frozen_beat=0.),
            'completion_id':lambda v:v['evidence'].update(frozen_completion_id='unknown'),
            'C1':lambda v:v['evidence'].update(regularity='C1'),
            'lost_commit':lambda v:v['evidence']['after_stream']['commit_records'].pop(),
            'lost_delta':lambda v:v['evidence']['strict_result']['emitted_receipts'].pop(),
            'numerical_overclaim':lambda v:v['evidence'].update(operation_scope='positive_numerical_campaign'),
        }
        for name,edit in edits.items():
            bad=deepcopy(original);edit(bad);bad['record_digest']=p.digest_record(bad)
            with self.subTest(name=name),self.assertRaises((ValueError,KeyError)):gate.validate_interface(bad)

    def test_integrated_product_and_rehashed_false_proposals(self):
        import verify_p977_c_rg2b_g2 as gate
        expected = review.read(gate.RECORD)
        gate.validate(expected, expected)
        edits = {
            'missing_cell': lambda v: v['catalog_product'].pop(),
            'duplicate_cell': lambda v: v['catalog_product'].append(deepcopy(v['catalog_product'][0])),
            'empty_proposal': lambda v: v.update(proposed_additional_support=[]),
            'family_alias': lambda v: v.update(proposed_additional_support=['C_RG2b']),
            'borrowed_initializer': lambda v: v.update(proposed_additional_support=[v['ordered_scope']['initializer_target']]),
            'waived_obligation': lambda v: v['obligations'].pop('G2-ORDERED-ENDPOINTS'),
            'invented_acceptance': lambda v: v.update(G2_accepted=True),
            'widened_registry': lambda v: v['accepted_support_unchanged'].append(gate.NOMINATED),
            'all_pairs': lambda v: v['ordered_scope'].update(all_ordered_pairs_verified=True),
            'invented_C_history': lambda v: v['ordered_scope'].update(candidate_authority='C_with_W_history'),
            'borrowed_event':lambda v:v.update(proposed_additional_support=[v['ordered_scope']['event_target']]),
            'scalar_as_graph':lambda v:v['ordered_scope'].update(retained_PC_pairs_are_separate_scalar_endpoints=False),
            'C1':lambda v:v['ordered_scope'].update(classical_derivative_or_spectrum_claimed=True),
            'debt_erased':lambda v:v['ordered_scope'].update(C1_debt_resolved=True),
            'all_dt':lambda v:v['ordered_scope'].update(arbitrary_positive_dt_supported=True),
            'K_is_K_minus':lambda v:v['ordered_scope'].update(state_readmission_on_K_is_not_ordinary_entry_on_K_minus=False),
            'zero_beat':lambda v:v['ordered_scope'].update(zero_duration_does_not_select_zero_beat_completion=False),
            'CI_equivalence':lambda v:v['ordered_scope'].update(CI_equivalence_claimed=True),
            'persistent_section':lambda v:v['ordered_scope'].update(section_is_not_persistent_state=False),
            'indefinite_invariance':lambda v:v['ordered_scope'].update(indefinite_base_chart_invariance_claimed=True),
            'specialization':lambda v:v['ordered_scope'].update(disabled_specialization_reductions_verified=True),
            'all_graphs':lambda v:v['ordered_scope'].update(generalized_evaluator_evidence_is_not_arbitrary_graph_G2_support=False),
            'invented_event_loss':lambda v:v['ordered_scope'].update(event_policy='candidate_history_loss'),
            'section_derivative':lambda v:v['ordered_scope'].update(fixed_stratum_C_derivative_is_not_RG_section_derivative=False),
            'mobility_transfer':lambda v:v['ordered_scope'].update(mobility_authority_is_not_geometry_authority=False),
            'incomplete_C_chain':lambda v:v['ordered_scope'].update(complete_C_chain_reconstructed_for_each_role=False),
            'changed_authority': lambda v: v['authority'].clear(),
            'changed_source': lambda v: v['source_bindings'].update({gate.SCRIPT: '0'*64}),
        }
        for name, edit in edits.items():
            with self.subTest(name=name):
                bad = deepcopy(expected); edit(bad); bad['record_digest'] = p.digest_record(bad)
                with self.assertRaises((ValueError, KeyError)): gate.validate(bad, expected)


if __name__ == '__main__':
    unittest.main()
