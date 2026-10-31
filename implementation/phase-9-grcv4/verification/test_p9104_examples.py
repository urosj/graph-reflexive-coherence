"""Publication pressure, public persistence, portability and real read-only UX."""
from copy import deepcopy
from io import BytesIO
import importlib.util
import json
import lzma
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import p9104_examples as c

TOOL=c.ROOT/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool'


class ExampleTests(unittest.TestCase):
    def test_retained_all_ten_and_exact_fixture_extraction_without_running(self):
        with patch.object(c.tour,'run',side_effect=AssertionError('native rerun')):
            self.assertEqual(len(c.check()['family_runs']),10)

    def test_scope_family_history_and_consumed_read_mutations(self):
        original=c.read(c.RESULTS/'C_OS.json.xz')
        for kind in ('family','G4_accepted','completed_spark','consumed','W','rollback','target'):
            value=deepcopy(original);r=value['result']
            if kind=='family':value['family']='A_PC'
            elif kind=='G4_accepted':value[kind]=True
            elif kind=='completed_spark':r['sparks'][kind]=True
            elif kind=='consumed':r['evolution']['steps'][0]['fresh_poststate_observables']['authoritative_current']['consumed_by_continuity']=True
            elif kind=='W':r['evolution']['steps'][0]['after']['W_A']=[1.]*9
            elif kind=='rollback':r['rejection']['final_digest']='wrong'
            else:r['expansion']['target_continuation']['committed']=False
            with self.subTest(kind=kind),self.assertRaises(AssertionError):c.validate_run(value,'C_OS')

    def test_extracted_reset_cannot_be_replaced_with_current(self):
        original=c.fixtures.fixture
        def wrong(family):
            v=original(family)
            if family=='C_OS':v['configuration']['reset']=v['configuration']['current']
            return v
        with patch.object(c.fixtures,'fixture',side_effect=wrong),self.assertRaisesRegex(AssertionError,'authority extraction'):
            c.fixture_links()

    def test_compression_and_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            value={'repeated':'x'*1_000_001};path=Path(folder)/'new.json'
            out=c.tour.write_output(path,value)
            self.assertEqual(out.suffix,'.xz')
            self.assertEqual(json.loads(lzma.decompress(out.read_bytes())),value)
            before=out.read_bytes()
            with self.assertRaises(FileExistsError):c.tour.write_output(path,value)
            self.assertEqual(out.read_bytes(),before)

    def test_public_save_load_and_configuration_portable_off_cwd(self):
        from pygrc.models import GRC9V4
        old=Path.cwd()
        with tempfile.TemporaryDirectory() as folder:
            try:
                os.chdir(folder)
                cfg=c.fixtures.configuration('C_OS')
                model=GRC9V4.from_config(cfg)
                path=Path(folder)/'checkpoint.json';model.save(path)
                self.assertEqual(GRC9V4.load(path).snapshot(),model.snapshot())
            finally:os.chdir(old)

    def test_documentation_successor_does_not_rewrite_old_acceptance(self):
        import p9104_source_epoch as epoch
        import p9103_regressions as previous
        import p9103_acceptance as acceptance
        value=previous.check()
        self.assertTrue(acceptance.decision(c.ROOT,value)['P9_10_3_closed'])
        name='examples/grcv4/grc9v4_api.md'
        self.assertEqual(epoch.previous_bytes(c.ROOT,name),epoch.original(c.ROOT,name))
        original=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:original(p)+b'changed' if p==c.ROOT/name else original(p)):
            with self.assertRaises(ValueError):epoch.previous_bytes(c.ROOT,name)

    def test_api_browser_notebook_and_source_access(self):
        sys.path.insert(0,str(TOOL/'src'))
        from grcv4_explorer import tranche10_examples as api
        from grcv4_explorer.phase9_verification import _profile_next_gate
        from grcv4_explorer.tooling import managed_node,tool_environment
        spec=importlib.util.spec_from_file_location('p9104_server',TOOL/'scripts/serve_phase9.py')
        server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
        def get(path):
            h=server.Handler.__new__(server.Handler);h.path=path;h.wfile=BytesIO();codes=[]
            h.send_response=lambda code,*args:codes.append(code)
            h.send_error=lambda code,*args:codes.append(code)
            h.send_header=lambda *args:None;h.end_headers=lambda:None
            h.do_GET();return codes[-1],h.wfile.getvalue()
        with patch.object(c.tour,'run',side_effect=AssertionError('native rerun')):
            view=api.tranche10_examples_status(c.ROOT)
            code,raw=get('/api/tranche10/examples');self.assertEqual(code,200);self.assertEqual(json.loads(raw),view)
            code,raw=get('/api/tranche10/examples/source?path='+c.GUIDE)
            self.assertEqual(code,200);self.assertEqual(raw,(c.ROOT/c.GUIDE).read_bytes())
            self.assertEqual(get('/api/tranche10/examples/source?path=../secret')[0],404)
            self.assertEqual(get('/api/tranche10/examples?family=C_OS')[0],404)
            self.assertEqual(get('/tranche10-examples.js')[0],200)
            self.assertEqual(_profile_next_gate({'tranche10_examples':view}),view['next_work'])
        process=subprocess.run([str(managed_node()),str(TOOL/'phase9-web/tranche10-examples.test.mjs')],
            input=json.dumps(view),text=True,capture_output=True,cwd=c.ROOT,env=tool_environment())
        self.assertEqual(process.returncode,0,process.stdout+process.stderr)
        notebook=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes())
        cell=next(x for x in notebook['cells'] if x.get('id')=='p9104-examples')
        self.assertIn('tranche10_examples_status',''.join(cell['source']))
        self.assertEqual(cell['outputs'],[])
        with patch('IPython.display.display'),patch.object(c.tour,'run',side_effect=AssertionError('native rerun')):
            exec(''.join(cell['source']),{'repo_root':c.ROOT})


if __name__=='__main__':unittest.main()
