"""Real concurrent diagnostic writes and immutable-file rejection boundaries."""
import lzma
import multiprocessing
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import p9_ccipc_raw_store as p


def value():
    read=p.b.seal(dict(selected=[1.0,2.0,3.0]))
    return p.b.seal(dict(inputs=dict(current=1.0),read=read,verifier_sha='test',campaign_credit=False))


def concurrent_write(directory,barrier):
    v=value();path=Path(directory)/(v['read']['record_digest']+'.json.xz')
    with p.private_captures(directory):
        barrier.wait(timeout=30)
        p.storage.save(path,v)


class PrivateCaptureTests(unittest.TestCase):
    def test_concurrent_identical_writers_keep_one_exact_record(self):
        with TemporaryDirectory() as directory:
            context=multiprocessing.get_context('spawn');barrier=context.Barrier(2)
            jobs=[context.Process(target=concurrent_write,args=(directory,barrier)) for _ in range(2)]
            for job in jobs:job.start()
            try:
                for job in jobs:
                    job.join(45);self.assertEqual(job.exitcode,0)
            finally:
                for job in jobs:
                    if job.is_alive():job.terminate();job.join()
            files=list(Path(directory).glob('*.json.xz'));self.assertEqual(len(files),1)
            self.assertEqual(p.storage.read(files[0]),value())

    def test_changed_capture_is_rejected_without_overwrite(self):
        with TemporaryDirectory() as directory,p.private_captures(directory):
            v=value();path=Path(directory)/(v['read']['record_digest']+'.json.xz')
            p.storage.save(path,v);before=path.read_bytes()
            bad=p.b.seal(dict(v,inputs=dict(current=2.0)))
            with self.assertRaisesRegex(ValueError,'changed complete content'):p.storage.save(path,bad)
            self.assertEqual(path.read_bytes(),before)

    def test_corrupt_capture_is_not_replaced(self):
        with TemporaryDirectory() as directory,p.private_captures(directory):
            v=value();path=Path(directory)/(v['read']['record_digest']+'.json.xz')
            path.write_bytes(b'corrupt capture')
            with self.assertRaises(lzma.LZMAError):p.storage.save(path,v)
            self.assertEqual(path.read_bytes(),b'corrupt capture')

    def test_campaign_files_remain_exclusive(self):
        with TemporaryDirectory() as directory,p.private_captures(directory):
            path=Path(directory)/'campaign-result.json.xz';v=value()
            p.storage.save(path,v);before=path.read_bytes()
            with self.assertRaises(FileExistsError):p.storage.save(path,v)
            self.assertEqual(path.read_bytes(),before)


if __name__=='__main__':unittest.main()
