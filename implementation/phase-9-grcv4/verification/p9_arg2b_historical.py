"""Finite A_RG2b successor; authenticate live changes before historical projection."""
from functools import lru_cache
import hashlib,json,subprocess
from pathlib import Path

BASE='af397360'
PREFIX='implementation/phase-9-grcv4/'
SIDE='implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/'
SELF=PREFIX+'verification/p9_arg2b_historical.py'
PATH=PREFIX+'tranche-8/P9-ARG2b-SourceEpochs.json'
CHANGED={
 *('tests/models/test_grc_9_v4_'+name+'_integration.py' for name in ('aos','cpc','ccipc','acipc','crg2b')),
 'artifact-storage.json','.gitignore',PREFIX+'runtime/RuntimeWorkManifest.json',
 *(PREFIX+'verification/'+n+'.py' for n in ('p9_crg2b_historical','p9_crg2b_native_review','phase9_implementation_policy','phase9_specialization_acceptance')),
 *('implementation/Phase-9-GRCV4-'+n+'.md' for n in ('ImplementationPlan','ImplementationChecklist','Handoff')),
 *(SIDE+'GRCV4ExploratorySideToolImplementation'+n+'.md' for n in ('Plan','Checklist')),
 *(SIDE+'tool/'+n for n in ('scripts/serve_phase9.py','scripts/run_phase9_notebook.py','src/grcv4_explorer/phase9_verification.py','phase9-web/index.html','notebooks/phase9_verification.ipynb')),
 *('src/pygrc/models/'+n+'.py' for n in ('grc_v4_rg2b','grc_9_v4_api_lifecycle','grc_9_v4_owner','grc_9_v4_legacy')),
}
ADDITIONS={'src/pygrc/models/grc_9_v4_arg2b_connected.py', 'tests/models/test_grc_9_v4_arg2b_integration.py', SIDE+'tool/src/grcv4_explorer/arg2b.py'}

def sha(v):return hashlib.sha256(v).hexdigest()
def seal(v):
 body={k:x for k,x in v.items() if k!='record_digest'}
 return dict(body,record_digest=sha(json.dumps(body,sort_keys=True,separators=(',',':')).encode()))
@lru_cache(maxsize=64)
def original(root,name):return subprocess.check_output(['git','show',BASE+':'+name],cwd=root)

def manifest(root):
 root=Path(root).resolve()
 return seal(dict(schema='p9-arg2b-source-epochs-v1',predecessor=BASE,checker_sha256=sha((root/SELF).read_bytes()),
  sources={n:dict(before_sha256=sha(original(root,n)),after_sha256=sha((root/n).read_bytes())) for n in sorted(CHANGED)},
  additions={n:sha((root/n).read_bytes()) for n in sorted(ADDITIONS)},accepted_execution_rewritten=False,user_acceptance_inferred=False))

def epochs(root):
 root=Path(root).resolve();v=json.loads((root/PATH).read_bytes())
 if v!=seal(v) or v['schema']!='p9-arg2b-source-epochs-v1' or v['predecessor']!=BASE or v['checker_sha256']!=sha((root/SELF).read_bytes()) \
  or set(v['sources'])!=CHANGED or set(v['additions'])!=ADDITIONS or v['accepted_execution_rewritten'] is not False or v['user_acceptance_inferred'] is not False:
  raise ValueError('A_RG2b successor scope drift')
 return v

def peel_sha(root,name,present):
 name=Path(name).as_posix()
 if name not in CHANGED:return present
 root=Path(root).resolve();row=epochs(root)['sources'][name]
 if sha((root/name).read_bytes())!=row['after_sha256'] or sha(original(root,name))!=row['before_sha256']:
  raise ValueError('unregistered A_RG2b successor: '+name)
 return row['before_sha256'] if present==row['after_sha256'] else present

def matches(root,name,expected):
 present=sha((Path(root)/name).read_bytes())
 return present==expected or peel_sha(root,name,present)==expected

def project(root,current):
 root=Path(root).resolve();v=epochs(root)
 result={n:peel_sha(root,n,h) for n,h in current.items()}
 for n in ADDITIONS & result.keys():
  if result[n]!=v['additions'][n] or sha((root/n).read_bytes())!=v['additions'][n]:raise ValueError('unregistered A_RG2b addition: '+n)
  del result[n]
 return result
