"""Lossless shared storage: original bytes, cold restore and fail-closed reads."""
import io
import json
import lzma
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import evidence_storage as storage, evidence_dedup as dedup


class SharedStorageTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        limit = patch.object(storage, 'LIMIT', 256)
        limit.start(); self.addCleanup(limit.stop)
        common = [float(i) / 7 for i in range(100)]
        self.raws = [dedup.dumps(dict(index=i, same=common, again=common,
            exact=[-0.0, 0.0, 2**80, 1e-100, '∑\\\"\n'])) + b'\n' for i in range(2)]
        self.rows = []
        (self.root/'data').mkdir()
        for i, raw in enumerate(self.raws):
            name = f'data/{i}.json'; packed = lzma.compress(raw)
            (self.root/(name+'.xz')).write_bytes(packed)
            self.rows.append(dict(path=name, size=len(raw), sha256=storage.sha(raw),
                storage_path=name+'.xz', storage_size=len(packed), storage_sha256=storage.sha(packed)))
        self.manifest = dict(schema='exact-evidence-storage-v2', compression_threshold_bytes=256, files=self.rows)
        self.save()
        self.descriptor = dedup.build(self.root, self.rows, 'shared', minimum=256)

    def save(self):
        (self.root/storage.MANIFEST).write_text(json.dumps(self.manifest))

    def register(self):
        return storage.deduplicate(self.root, [r['path'] for r in self.rows], 'shared')

    def cold(self):
        for r in self.rows:
            (self.root/r['path']).unlink(missing_ok=True)
            (self.root/r['storage_path']).unlink(missing_ok=True)

    def test_exact_round_trip_and_actual_object_sharing(self):
        store = dedup.Store(self.root, self.descriptor, self.rows)
        for row, raw in zip(self.rows, self.raws):
            self.assertEqual(store.raw(row), raw)
            self.assertEqual(store.xz(row), (self.root/row['storage_path']).read_bytes())
        references = []
        for name in store.archive.namelist():
            raw = store.archive.read(name)
            if raw.startswith(b'R'):
                references.extend(p['ref'] for p in json.loads(raw[1:]) if isinstance(p, dict))
        self.assertGreater(len(references), len(set(references)))

    def test_cold_restore_both_original_identities_and_idempotence(self):
        self.register(); self.cold()
        result = storage.restore(self.root)
        self.assertEqual(result, {'files': 2, 'restored': 2})
        for row, raw in zip(self.rows, self.raws):
            self.assertEqual((self.root/row['path']).read_bytes(), raw)
            self.assertEqual(storage.sha((self.root/row['storage_path']).read_bytes()), row['storage_sha256'])
        self.assertEqual(storage.restore(self.root)['restored'], 0)
        self.assertTrue(storage.verify(self.root)['byte_exact'])

    def test_scoped_archive_only_restore(self):
        self.register(); self.cold()
        self.assertEqual(storage.restore(self.root, prefix='data/0.', expanded=False)['restored'], 0)
        self.assertTrue((self.root/self.rows[0]['storage_path']).exists())
        self.assertFalse((self.root/self.rows[0]['path']).exists())
        self.assertFalse((self.root/self.rows[1]['storage_path']).exists())

    def test_local_copies_do_not_mask_corrupt_shared_store(self):
        self.register(); storage.restore(self.root)
        manifest = json.loads((self.root/self.descriptor['path']).read_bytes())
        (self.root/manifest['archive']['path']).write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'object archive drift'):
            storage.restore(self.root)
        self.assertEqual((self.root/self.rows[0]['path']).read_bytes(), self.raws[0])
        self.assertEqual(storage.restore(self.root, prefix='unrelated/')['files'], 0)

    def test_edited_raw_and_archive_are_never_overwritten(self):
        self.register(); storage.restore(self.root)
        for key in ('path', 'storage_path'):
            target = self.root/self.rows[0][key]; original = target.read_bytes()
            target.write_bytes(b'local edit')
            with self.subTest(key=key), self.assertRaises(ValueError):
                storage.restore(self.root)
            self.assertEqual(target.read_bytes(), b'local edit')
            target.write_bytes(original)

    def test_manifest_identity_and_members_are_verified(self):
        p = self.root/self.descriptor['path']; original = p.read_bytes()
        p.write_bytes(original+b' ')
        with self.assertRaisesRegex(ValueError, 'manifest drift'):
            dedup.Store(self.root, self.descriptor, self.rows)
        p.write_bytes(original)
        m = json.loads(original)
        m['records'][0]['sha256'] = '0'*64
        p.write_bytes(dedup.dumps(m))
        with self.assertRaisesRegex(ValueError, 'changed original identity'):
            dedup.Store(self.root, dict(path=self.descriptor['path'], sha256=dedup.sha(p.read_bytes())), self.rows)

    def test_resealed_archive_cannot_hide_changed_object(self):
        m = json.loads((self.root/self.descriptor['path']).read_bytes())
        archive = self.root/m['archive']['path']
        data = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(lzma.decompress(archive.read_bytes()))) as source, zipfile.ZipFile(data, 'w') as target:
            for i, info in enumerate(source.infolist()):
                raw = source.read(info)
                target.writestr(info, raw+b'!' if i == 0 else raw)
        packed = lzma.compress(data.getvalue()); archive.write_bytes(packed)
        m['archive'].update(size=len(packed), sha256=dedup.sha(packed), expanded_size=len(data.getvalue()))
        p = self.root/self.descriptor['path']; p.write_bytes(dedup.dumps(m))
        store = dedup.Store(self.root, dict(path=self.descriptor['path'], sha256=dedup.sha(p.read_bytes())), self.rows)
        with self.assertRaisesRegex(ValueError, 'object hash mismatch'):
            store.raw(self.rows[0])

    def test_encoder_mismatch_fails_explicitly_without_altering_json(self):
        store = dedup.Store(self.root, self.descriptor, self.rows)
        with patch.object(dedup.lzma, 'compress', return_value=b'different encoder'):
            with self.assertRaisesRegex(ValueError, 'XZ encoder cannot reproduce'):
                store.xz(self.rows[0])
        self.assertEqual(store.raw(self.rows[0]), self.raws[0])

    def test_writer_refuses_silent_json_normalization(self):
        for raw in (b'{"a": 1}', b'{"a":1,"a":2}', b'{"x":1.000}', b'{"x":NaN}', b'{}\n\n'):
            with self.subTest(raw=raw), zipfile.ZipFile(io.BytesIO(), 'w') as archive:
                with self.assertRaises(ValueError):
                    dedup.Builder(archive, 1).record(raw)

    def test_pack_keeps_shared_registration_and_refuses_repeat_migration(self):
        self.register()
        (self.root/'data/new.json').write_bytes(self.raws[0])
        storage.pack(self.root, ['data/new.json'])
        manifest = json.loads((self.root/storage.MANIFEST).read_bytes())
        self.assertEqual(manifest['schema'], 'exact-evidence-storage-v3')
        self.assertEqual(len(manifest['object_stores']), 1)
        self.assertEqual(storage.verify(self.root)['files'], 3)
        with self.assertRaisesRegex(ValueError, 'already belongs'):
            self.register()

    def test_unsafe_paths_missing_objects_and_limits_fail(self):
        for name in ('../escape', '/absolute', 'a/../b', 'a\\b'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                dedup.path(self.root, name)
        store = dedup.Store(self.root, self.descriptor, self.rows)
        with self.assertRaisesRegex(ValueError, 'missing shared object'):
            store._expand('0'*64, set(), 1000)
        root = store.records[self.rows[0]['path']]['root']
        with self.assertRaisesRegex(ValueError, 'cyclic'):
            store._expand(root, {root}, 1000)
        with self.assertRaises(ValueError):
            store._expand(root, set(), 10)


if __name__ == '__main__':
    unittest.main()
