"""Ninth-family native integration; shared obligations with C_RG2b operands."""
import argparse,json,time,unittest
from copy import deepcopy
from concurrent.futures import ProcessPoolExecutor,as_completed
import p9_crg2b_campaign as c
import p9_acipc_integration_compute as compute
from p992_compatibility import seal
b=c.b
SELF=b.HERE+'p9_crg2b_integration.py'
GROUPS={'9.1b':'CRG2bLifecycle','9.2':'CRG2bCompatibility','9.4a':'CRG2bCrossing','9.4b':'CRG2bPublic','9.5':'CRG2bConflict'}
COUNTS={'9.1b':6,'9.2':4,'9.4a':4,'9.4b':5,'9.5':3}

def path(key):return c.BASE+key+'-integration.json.xz'

def sources(test):
 result={p.relative_to(b.ROOT).as_posix() for p in (b.ROOT/'src').rglob('*.py')}
 result|={SELF,c.SELF,c.r.SELF,c.INPUTS,compute.SELF,b.HERE+'p984h_cpc.py',b.HERE+'p984h_validation_reuse.py',
  b.HERE+'p9_cpc_covariance_compute.py',b.HERE+'p9_cpc_wire_reuse.py'}
 result|={m.__file__.replace(str(b.ROOT)+'/', '') for m in (test,test.lifecycle,test.legacy,test.crossing,test.public,test.conflict)}
 return b.bind(result)

def run(key):
 from tests.models import test_grc_9_v4_crg2b_integration as test
 if (b.ROOT/path(key)).exists():
  old=c.read(path(key));b.require(old==seal(old) and old['user_accepted'] is False,'never replace accepted evidence')
  try:return check(key)
  except ValueError:pass  # Reexecute after an unaccepted development-source correction.
 collectors={'9.1b':test.lifecycle.OBSERVATIONS,'9.2':test.legacy.EVIDENCE,'9.4a':test.crossing.EVIDENCE,
  '9.4b':test.public.EVIDENCE,'9.5':test.conflict.EVIDENCE}
 collectors[key].clear();refs=sources(test);suite=unittest.defaultTestLoader.loadTestsFromTestCase(getattr(test,GROUPS[key]));roster=[x.id() for x in suite]
 start=time.monotonic()
 with compute.worker() as policy:result=unittest.TextTestRunner(verbosity=2).run(suite)
 b.require(result.wasSuccessful() and result.testsRun==COUNTS[key] and not result.skipped,'incomplete C_RG2b '+key)
 evidence=deepcopy(collectors[key]);evidence=evidence['C_RG2b'] if key=='9.1b' else evidence
 b.check_bindings(refs)
 value=seal(dict(schema='p9-crg2b-integration-v1',family='C_RG2b',checkpoint=key,tests=roster,tests_run=result.testsRun,
  failures=0,errors=0,skips=0,outcome='passed',elapsed_seconds=time.monotonic()-start,source_bindings=refs,
  compute_policy=policy,evidence=evidence,native_runtime_executed=True,user_accepted=False,aggregate_closed=False))
 # Compatibility payloads legitimately contain signed zero: preserve native JSON.
 import lzma
 target=b.ROOT/path(key)
 with target.open('wb') as stream:stream.write(lzma.compress(json.dumps(value,separators=(',',':'),allow_nan=False).encode()+b'\n'))
 return check(key)

def check(key):
 value=c.read(path(key));b.require(value==seal(value),'integration digest');b.check_bindings(value['source_bindings'])
 b.require(value['family']=='C_RG2b' and value['checkpoint']==key and value['outcome']=='passed'
  and value['tests_run']==len(value['tests'])==COUNTS[key] and value['evidence']
  and all(value[k]==0 for k in ('failures','errors','skips')) and not value['user_accepted'],'integration coverage')
 return dict(checkpoint=key,tests=value['tests_run'],passed=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=('run','check'));p.add_argument('--group',choices=GROUPS);p.add_argument('--workers',type=int,default=2);a=p.parse_args()
 groups=[a.group] if a.group else list(GROUPS)
 if a.action=='run':
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(run,k) for k in groups]):print(f.result(),flush=True)
 else:
  for k in groups:print(check(k))
