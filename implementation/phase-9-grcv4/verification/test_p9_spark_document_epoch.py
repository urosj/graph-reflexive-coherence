"""Historical basin documents remain exact after the finite spark additions."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import p9_spark_document_epoch as epoch
import verify_p9101a_propagation as basin

ROOT = basin.ROOT
sys.path.insert(0, str(ROOT / epoch.INV / 'tools/exploratory-side-tool/tool/src'))
from grcv4_explorer import spark_earlier_sc3_metadata as metadata
from grcv4_explorer.canonical import record_digest


class SparkDocumentEpochTests(unittest.TestCase):
    def test_exact_committed_documents_and_all_reconciliation_context(self):
        for name, (before, after) in epoch.DOCUMENTS.items():
            with self.subTest(path=name):
                raw = epoch.previous_bytes(ROOT, name)
                historical = subprocess.check_output(
                    ['git', 'show', epoch.BASIN_COMMIT + ':' + name], cwd=ROOT)
                self.assertEqual(raw, historical)
                self.assertEqual(epoch.sha(raw), before)
                committed = subprocess.check_output(
                    ['git', 'show', epoch.SPARK_COMMIT + ':' + name], cwd=ROOT)
                self.assertEqual(epoch.sha(committed), after)
        import phase9_implementation_policy as policy
        for row in policy.binding_reconciliation(ROOT)['context_bindings']:
            raw = basin.predecessor_document_bytes(ROOT, row['path'])
            self.assertEqual(policy.planning.blob_id(raw), row['git_blob'], row['path'])
            self.assertEqual(epoch.sha(raw), row['sha256'], row['path'])

    def test_original_basin_insertion_and_manifest_are_still_checked(self):
        manifest = basin.checked_manifest(ROOT)
        for row in manifest['document_successors']:
            raw = basin.predecessor_document_bytes(ROOT, row['path'])
            self.assertEqual(epoch.sha(raw), row['before_sha256'])
        original = Path.read_bytes
        for name in (basin.DOCUMENTS[1], 'specs/grc-9-v4-basin-interface.md'):
            with self.subTest(path=name), patch.object(
                Path, 'read_bytes', lambda p: original(p) + b'\nunreviewed\n'
                if p == ROOT / name else original(p)
            ), self.assertRaises(ValueError):
                basin.checked_manifest(ROOT)

    def test_cached_preimages_do_not_hide_current_document_or_reader_edits(self):
        original = Path.read_bytes
        for name in (*epoch.DOCUMENTS, *epoch.READERS):
            epoch.previous_bytes(ROOT, name)  # populate immutable Git cache
            with self.subTest(path=name), patch.object(
                Path, 'read_bytes', lambda p: original(p) + b'\nunreviewed\n'
                if p == ROOT / name else original(p)
            ), self.assertRaises(ValueError):
                epoch.previous_bytes(ROOT, name)

    def test_rehashed_metadata_cannot_admit_different_preimages_or_scope(self):
        original = metadata.load_json_object
        for defect in ('before', 'after', 'roster'):
            def changed(path):
                value = deepcopy(original(path))
                if path == ROOT / metadata.SOURCE:
                    if defect == 'roster':
                        value['sources'].pop()
                    else:
                        row = next(r for r in value['sources'] if r['path'] == epoch.CHECKLIST)
                        row[defect + '_sha256'] = '0' * 64
                    value['record_digest'] = record_digest(value, 'record_digest')
                return value
            with self.subTest(defect=defect), patch.object(
                metadata, 'load_json_object', changed
            ), self.assertRaises(ValueError):
                epoch.previous_bytes(ROOT, epoch.CHECKLIST)

    def test_old_runtime_reader_rejects_unregistered_registry(self):
        from p994b_runtime_successor import SOURCES, historical_source
        name = 'specs/README.md'
        expected = next(iter(SOURCES[name]['predecessors']))
        self.assertEqual(historical_source(ROOT, name, expected), expected)
        original = Path.read_bytes
        with patch.object(Path, 'read_bytes', lambda p: original(p) + b'\nunreviewed\n'
                          if p == ROOT / name else original(p)):
            self.assertIsNone(historical_source(ROOT, name, expected))
        self.assertEqual(epoch.peel_sha(ROOT, name, '0' * 64), '0' * 64)

    def test_original_test_epoch_and_reader_subjects_are_preserved(self):
        import p9103_source_epoch as previous
        import json
        self.assertEqual(previous.manifest(ROOT), json.loads((ROOT / previous.PATH).read_bytes()))
        for name, expected in epoch.READERS.items():
            self.assertEqual(epoch.sha(previous.previous_bytes(ROOT, name)), expected)
        for name in ('../outside', '/etc/passwd'):
            with self.subTest(path=name), self.assertRaises(ValueError):
                epoch.previous_bytes(ROOT, name)

    def test_fresh_audit_import_order_uses_checkout_and_preserves_package(self):
        code = '''
import sys
from pathlib import Path
sys.path.insert(0, 'implementation/phase-9-grcv4/verification')
import phase9_implementation_policy as policy
policy.check_binding_reconciliation(policy.ROOT)
from verify_p972b_event_package import check
check(policy.ROOT)
import pygrc.models
assert Path(pygrc.models.__file__).resolve().is_relative_to(policy.ROOT / 'src')
'''
        subprocess.run([sys.executable, '-c', code], cwd=ROOT, check=True,
                       capture_output=True, text=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
