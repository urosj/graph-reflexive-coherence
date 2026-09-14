"""Narrow A_CI facade supplement and read-only integrated-review pressure."""

from copy import deepcopy
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
        from test_p977_a_ci_local import NOMINATED

        inputs, backend = fixture('A_CI')
        config = dict(initial=inputs.to_payload(), differential_reference=backend.to_payload())
        source = deepcopy(config)
        owner = GRCV4.from_config(config)
        self.assertIsInstance(owner, GRCModel)
        self.assertEqual(owner.active_model_identity, NOMINATED)
        initial = owner.snapshot()
        config['initial']['current']['C'][0] = 999
        self.assertEqual(owner.snapshot(), initial)
        self.assertEqual(owner.get_params(), inputs.geometry.reference.profile.params_resolved)
        owner.set_state(owner.get_state())
        self.assertEqual(owner.snapshot(), initial)
        self.assertEqual(owner.list_supported_profiles(), frozenset({NOMINATED}))
        self.assertEqual(owner.get_supported_profile(NOMINATED), inputs.geometry.reference.profile)
        self.assertIn(NOMINATED, list_supported_profiles())  # Separate exact G2 acceptance now publishes this declaration.
        self.assertEqual(owner.run(0), [])
        for call, error in ((owner.step, MissingV4StepRequest), (lambda: owner.run(1), MissingV4StepRequest),
                            (lambda: owner.run(True), TypeError), (lambda: owner.run(-1), ValueError),
                            (lambda: owner.step_v4(request(0)), TypeError)):
            with self.assertRaises(error): call()
            self.assertEqual(owner.snapshot(), initial)
        malformed = deepcopy(source); malformed['cache'] = {}
        with self.assertRaises(ValueError): GRCV4.from_config(malformed)
        malformed = deepcopy(source); malformed.pop('differential_reference')
        with self.assertRaises(ValueError): GRCV4.from_config(malformed)
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
        self.assertEqual(after_stream['receipt_ledger'][:-4], before_stream['receipt_ledger'])
        self.assertEqual(after_stream['receipt_ledger'][-4]['identity_payload']['core']['operation_id'], 'stream-zero')
        self.assertEqual(after_stream['commit_records'][:-1], before_stream['commit_records'])
        self.__class__.evidence = dict(source_config=source, initial_snapshot=initial,
            strict_request=strict.to_payload(), strict_result=primitive(result),
            before_stream=before_stream, stream_request=second.to_payload(), after_stream=after_stream,
            checks=dict(configuration_detached=True, immutable_parameters=True, unchanged_assignment=True,
                local_discovery_not_G2=True, missing_default_rejected=True, invalid_run_inputs_rejected=True,
                wrong_request_layer_rejected=True, extraneous_config_rejected=True, missing_backend_rejected=True,
                strict_external_results_equal=True, interrupted_iterator_keeps_prior_commit=True),
            operation_scope='zero_duration_interface_only; positive numerical step/replay remains in local product')


class ReviewTests(unittest.TestCase):
    def test_integrated_product_and_rehashed_false_proposals(self):
        import verify_p977_a_ci_g2 as gate
        expected = review.read(gate.RECORD)
        gate.validate(expected, expected)
        edits = {
            'missing_cell': lambda v: v['catalog_product'].pop(),
            'duplicate_cell': lambda v: v['catalog_product'].append(deepcopy(v['catalog_product'][0])),
            'empty_proposal': lambda v: v.update(proposed_additional_support=[]),
            'family_alias': lambda v: v.update(proposed_additional_support=['A_CI']),
            'borrowed_initializer': lambda v: v.update(proposed_additional_support=[v['ordered_scope']['initializer_target']]),
            'waived_obligation': lambda v: v['obligations'].pop('G2-ORDERED-ENDPOINTS'),
            'invented_acceptance': lambda v: v.update(G2_accepted=True),
            'widened_registry': lambda v: v['accepted_support_unchanged'].append(gate.NOMINATED),
            'all_pairs': lambda v: v['ordered_scope'].update(all_ordered_pairs_verified=True),
            'positive_incoming': lambda v: v['ordered_scope'].update(C_to_nominated_A='positive'),
            'changed_authority': lambda v: v['authority'].clear(),
            'changed_source': lambda v: v['source_bindings'].update({gate.SCRIPT: '0'*64}),
        }
        for name, edit in edits.items():
            with self.subTest(name=name):
                bad = deepcopy(expected); edit(bad); bad['record_digest'] = p.digest_record(bad)
                with self.assertRaises((ValueError, KeyError)): gate.validate(bad, expected)


if __name__ == '__main__':
    unittest.main()
