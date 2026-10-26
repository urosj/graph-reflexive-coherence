"""Historical-source authentication pressure; no native execution."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch
import tranche8_evidence as index
import tranche8_execution_sources as history
from tranche8_validation import Snapshot, validation_session


class HistoricalSourcesTests(unittest.TestCase):
    name=history.BASE+'P9-8.4b-CCICompletionCases.json'

    def test_original_roster_survives_later_code_changes_without_current_credit(self):
        sources=index.Sources(index.ROOT);original=sources.current_bytes
        def current(name):
            if name.startswith('src/'):raise AssertionError('historical validation must not consume current runtime code')
            return original(name)
        with patch.object(sources,'current_bytes',side_effect=current):result=history.verify(sources,self.name)
        self.assertEqual(result['revision'],history.REVISIONS[self.name])
        self.assertEqual(result['source_bindings'],106)
        self.assertFalse(result['current_runtime_conformance_inferred'])

    def test_changed_manifest_and_unregistered_record_rejected(self):
        sources=index.Sources(index.ROOT)
        value=json.loads(sources.raw(self.name));value['source_bindings'].pop()
        with patch.object(sources,'raw',return_value=json.dumps(value).encode()),self.assertRaisesRegex(ValueError,'record changed'):
            history.verify(sources,self.name)
        with self.assertRaisesRegex(ValueError,'unregistered'):history.verify(sources,'invented.json')

    def test_wrong_or_missing_historical_source_has_no_live_fallback(self):
        sources=index.Sources(index.ROOT);original=history.git_sha
        path='src/pygrc/models/grc_9_v4_lifecycle.py'
        def wrong(root,rev,name):return '0'*64 if name==path else original(root,rev,name)
        with patch.object(history,'git_sha',side_effect=wrong),self.assertRaisesRegex(ValueError,'source mismatch'):
            history.verify(sources,self.name)
        def missing(root,rev,name):
            if name==path:raise ValueError('missing historical source')
            return original(root,rev,name)
        with patch.object(history,'git_sha',side_effect=missing),self.assertRaisesRegex(ValueError,'missing historical'):
            history.verify(sources,self.name)

    def test_missing_ancestor_rejected(self):
        with patch.object(history,'git',side_effect=subprocess.CalledProcessError(1,['git'])), \
                self.assertRaisesRegex(ValueError,'available ancestor'):
            history.verify(index.Sources(index.ROOT),self.name)

    def test_named_archived_result_inputs_remain_byte_exact(self):
        for record,path in sorted(history.RETAINED_RESULT_INPUTS):
            with self.subTest(record=record):
                sources=index.Sources(index.ROOT)
                self.assertFalse(history.verify(sources,record)['current_runtime_conformance_inferred'])
                original=sources.current_bytes
                with patch.object(sources,'current_bytes',side_effect=lambda n:b'changed' if n==path else original(n)), \
                        self.assertRaisesRegex(ValueError,'source mismatch'):
                    history.verify(sources,record)

    def test_unsafe_paths_rejected(self):
        for name in ('/absolute','../outside','a/../b','a\\b','a//b','a\n'):
            with self.subTest(name=name),self.assertRaises(ValueError):history.safe_name(name)

    def test_historical_metadata_mode_is_explicit_bounded_and_detects_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'source').write_bytes(b'new');(root/'other').write_bytes(b'current')
            old=hashlib.sha256(b'old').hexdigest()
            row=dict(path='source',sha256=old)
            with self.assertRaisesRegex(ValueError,'source drift'):
                Snapshot(root).check_bindings([row])
            snapshot=Snapshot(root,historical_bindings={'source':old})
            snapshot.check_bindings([row]);self.assertEqual(snapshot.bind(['source']),[row])
            self.assertEqual(snapshot.raw('source'),b'new')
            with self.assertRaisesRegex(ValueError,'source drift'):
                snapshot.check_bindings([dict(path='other',sha256=old)])
            with self.assertRaisesRegex(ValueError,'source drift'):
                snapshot.check_bindings([dict(path='source',sha256='0'*64)])
            (root/'source').write_bytes(b'changed during check')
            with self.assertRaisesRegex(ValueError,'changed during'):snapshot.unchanged()

    def test_boundary_epoch_is_closed_and_available(self):
        bindings=history.boundary_bindings(index.ROOT)
        self.assertEqual(len(bindings),39)
        self.assertEqual(set(bindings),set(history.BOUNDARY_SOURCES))
        self.assertNotIn('src/unregistered.py',bindings)
        with patch.object(history,'git',side_effect=subprocess.CalledProcessError(1,['git'])), \
                self.assertRaisesRegex(ValueError,'available ancestor'):
            history.boundary_bindings(index.ROOT)

    def test_historical_g3_cannot_replace_live_admission(self):
        import phase9_specialization_acceptance as admission
        original=admission.accepted
        expected=history.historical_g3(index.ROOT)
        self.assertEqual(len(expected['accepted_generic_runtime_support']),10)
        with self.assertRaisesRegex(ValueError,'explicit index snapshot'):
            with index.historical_index_admission(index.ROOT):pass
        with patch.object(admission,'accepted',return_value={'live':True}) as live:
            with validation_session((),root=index.ROOT,historical_bindings=history.boundary_bindings(index.ROOT)):
                with index.historical_index_admission(index.ROOT):
                    self.assertEqual(admission.accepted(index.ROOT),expected)
                    admission.accepted(index.ROOT)['accepted_generic_runtime_support'].clear()
                    self.assertEqual(admission.accepted(index.ROOT),expected)
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        self.assertEqual(pool.submit(admission.accepted,index.ROOT).result(),{'live':True})
                    with self.assertRaisesRegex(ValueError,'root mismatch'):admission.accepted(index.ROOT.parent)
                self.assertIs(admission.accepted,live)
        self.assertIs(admission.accepted,original)
        with patch.object(history,'git_sha',return_value='0'*64),self.assertRaisesRegex(ValueError,'acceptance changed'):
            history.historical_g3(index.ROOT)


if __name__=='__main__':unittest.main()
