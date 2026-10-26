"""Bounded successor scope/identity pressure without native reruns."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import p984h_cos_event_successor as run


class EventSuccessorTests(unittest.TestCase):
    def test_prefix_adapter_cannot_select_event_or_continuation(self):
        token=object();adapter=run.prefix_only(token)
        self.assertIs(adapter('prefix'),token)
        for name in ('event','current','reset'):
            with self.assertRaises(ValueError):adapter(name)

    def test_retained_result_and_resealed_scope_mutations(self):
        if not (run.ROOT/run.RESULTS).exists():self.skipTest('successor not executed')
        with run.native.oracle.exact_backend(run.native.oracle.ExactBackend.FLINT), \
             run.native.oracle.numerical_policy(run.native.oracle.NumericalPolicy.CERTIFIED_ARB_256), \
             patch.object(run.native.native,'CandidateCOSPass',side_effect=AssertionError('numerical rerun')):
            value=run.check();m=run.manifest();prefix=run.authenticated_prefix()
            mutations=[lambda r:r.update(schema='forged'),lambda r:r.update(outcome='unknown'),
                       lambda r:r.update(cap_seconds=2400),lambda r:r.update(user_accepted=True),
                       lambda r:r.update(manifest_digest='forged')]
            if 'retention_revision' in value:
                mutations.append(lambda r:r['retention_revision'].update(execution_payload_digest='forged'))
            if value['outcome']=='completed':
                mutations += [lambda r:r['execution'].update(native_events=2),
                    lambda r:r['execution']['admissions'][2]['resources'].__setitem__(0,123.),
                    lambda r:r['execution']['admissions'][3].update(old_publication_live=False),
                    lambda r:r['execution']['checkpoint']['receipts'][0].update(commit_id='forged')]
            else:mutations.append(lambda r:r.update(native_events=1))
            for mutate in mutations:
                bad=deepcopy(value);mutate(bad)
                with self.assertRaises(ValueError):run.validate(run.seal(bad),m,prefix)


if __name__=='__main__':unittest.main()
