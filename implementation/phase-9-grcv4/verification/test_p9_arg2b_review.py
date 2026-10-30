"""Scope/source mutations and real API/browser/notebook paths; no native reruns."""
from copy import deepcopy
from io import BytesIO
import importlib.util,json,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
import p9_arg2b_review as review
import p9_arg2b_native_review as native
import p9_arg2b_historical as history
ROOT=native.b.ROOT;TOOL=ROOT/history.SIDE/'tool'
sys.path.insert(0,str(TOOL/'src'))
from grcv4_explorer import arg2b
from grcv4_explorer.tooling import managed_node,tool_environment

class RetainedSurfaces(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with patch.object(native.r.oracle,'certify',side_effect=AssertionError('numerical rerun')):
   cls.status=arg2b.arg2b_status(ROOT)
 def test_scope_and_resealed_mutations(self):
  v=self.status;self.assertFalse(v['user_accepted']);self.assertEqual(v['graph_certificates'],54)
  self.assertEqual(len(v['native_execution']),16);self.assertTrue(v['original_reset_exclusion_preserved'])
  self.assertEqual(v['native_execution']['9.3']['counts'],native.COUNTS)
  read=Path.read_bytes;original=json.loads((ROOT/native.PATH).read_bytes())
  for key,value in [('user_accepted',True),('C1_regularity_debt','resolved'),('large_covariance_deferred',[]),
   ('uniform_trajectory_enclosure',True),('check_level','native_rerun'),('stage','accepted'),('source_bindings',[])]:
   changed=native.b.seal(dict(original,**{key:value}))
   with self.subTest(key=key),patch.object(Path,'read_bytes',lambda p:json.dumps(changed).encode() if p==ROOT/native.PATH else read(p)):
    with self.assertRaises(ValueError):native.checked(ROOT)
 def test_current_source_drift_and_index(self):
  raw,ref=arg2b.arg2b_source(ROOT,review.RESEARCH[0]);self.assertEqual(raw,(ROOT/ref['path']).read_bytes())
  for name in ('../secret','/etc/passwd','unindexed.py'):
   with self.assertRaises(KeyError):arg2b.arg2b_source(ROOT,name)
  read=Path.read_bytes;name='src/pygrc/models/grc_9_v4_arg2b_connected.py'
  with patch.object(Path,'read_bytes',lambda p:read(p)+b'\ndrift' if p==ROOT/name else read(p)):
   with self.assertRaises(ValueError):native.checked(ROOT)
 def test_http_and_notebook(self):
  spec=importlib.util.spec_from_file_location('arg2b_test_server',TOOL/'scripts/serve_phase9.py');server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
  def get(path):
   h=server.Handler.__new__(server.Handler);h.path,h.wfile=path,BytesIO();codes=[]
   h.send_response=codes.append;h.send_header=lambda *args:None;h.end_headers=lambda:None;h.do_GET();return codes[-1],h.wfile.getvalue()
  code,raw=get('/api/arg2b');self.assertEqual(code,200);self.assertEqual(json.loads(raw),self.status)
  self.assertEqual(get('/arg2b.js')[0],200);self.assertEqual(get('/api/arg2b/source?path='+review.RESEARCH[0])[0],200)
  for path in ('/api/arg2b?accept=true','/api/arg2b/source?path=../secret','/api/arg2b/source?path=x&path=y'):
   self.assertEqual(get(path)[0],404)
  with patch.object(server,'arg2b_status',side_effect=ValueError('drift')):
   code,raw=get('/api/arg2b');self.assertEqual(code,503);self.assertEqual(set(json.loads(raw)),{'error'})
  book=json.loads((TOOL/'notebooks/phase9_verification.ipynb').read_bytes());cell=next(c for c in book['cells'] if c.get('id')=='query-arg2b')
  namespace=dict(repo_root=ROOT);code=compile(''.join(cell['source']),'query-arg2b','exec');exec(code,namespace)
  self.assertEqual(namespace['phase9_arg2b'],self.status)
  with patch.object(arg2b,'arg2b_status',side_effect=ValueError('drift')):
   with self.assertRaises(ValueError):exec(code,namespace)
  self.assertIsNone(namespace['phase9_arg2b'])
 def test_browser_does_not_promote_or_widen(self):
  module=(TOOL/'phase9-web/arg2b.js').as_uri();value=json.dumps(self.status)
  script=f'''import {{arg2bRows}} from {json.dumps(module)};
const original={value}; if(arg2bRows(original).length!==4)throw Error('missing rows');
for(const mutate of [v=>v.user_accepted=true,v=>v.aggregate_closed=true,v=>v.remaining_family='A_RG2b',
v=>v.graph_certificates=53,v=>v.large_covariance_deferred=[],v=>v.uniform_trajectory_enclosure=true,
v=>v.native_execution['9.3'].counts.bounded_accepted=40,v=>delete v.native_execution['8.4h'],
v=>v.prepared_sections.reverse(),v=>v.original_reset_exclusion_preserved=false]){{
 const v=structuredClone(original);mutate(v);let rejected=false;try{{arg2bRows(v)}}catch{{rejected=true}}
 if(!rejected)throw Error('scope mutation accepted');
}} console.log('ARG2B_BROWSER_PASS');'''
  result=subprocess.run([str(managed_node()),'--input-type=module','-e',script],env=tool_environment(),text=True,capture_output=True,check=True)
  self.assertIn('ARG2B_BROWSER_PASS',result.stdout)
 def test_historical_acceptance_and_exact_projection(self):
  import p9_crg2b_acceptance as prior
  self.assertTrue(prior.decision(ROOT)['user_accepted']);self.assertFalse(native.checked(ROOT)['user_accepted'])
  rows=history.epochs(ROOT)['sources']
  for name,row in rows.items():
   self.assertEqual(history.peel_sha(ROOT,name,row['after_sha256']),row['before_sha256'])
   self.assertEqual(history.peel_sha(ROOT,name,'untrusted'),'untrusted')

if __name__=='__main__':unittest.main()
