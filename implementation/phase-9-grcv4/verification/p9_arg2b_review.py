"""Read-only A_RG2b research/native projection; no numerical producer calls."""
from pathlib import Path
import hashlib,json,lzma
import p9_arg2b_native_review as native
b=native.b
BASE=b.BASE
SELF=b.HERE+'p9_arg2b_review.py'
IDENTITIES=BASE+'P9-ARG2b-ResearchBindings.json'
RESEARCH=tuple(BASE+'P9-ARG2b-'+x for x in ('CompletionFeasibility.json','SectionFeasibility.json.xz',
 'CompanionSections.json.xz','Authority.json','ConnectedCompletionRelease.json','HistoryCompanion.json'))

def identities(root=b.ROOT):
 root=Path(root).resolve();authority=json.loads((root/RESEARCH[3]).read_bytes())
 names={row['source_ref']['path'] for t in (*authority['contracts'].values(),*authority['debts'].values()) for row in t['rows']}
 return b.seal(dict(schema='p9-arg2b-research-bindings-v1',
  artifacts={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in RESEARCH},
  authority_sources={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sorted(names)}))

def checked(root=b.ROOT):
 root=Path(root).resolve();ids=json.loads((root/IDENTITIES).read_bytes())
 b.require(ids==identities(root),'A_RG2b research identity drift')
 names={SELF,IDENTITIES,*RESEARCH,native.SELF,native.PATH}
 records={}
 for name in RESEARCH:
  raw=(root/name).read_bytes();v=json.loads(lzma.decompress(raw) if name.endswith('.xz') else raw)
  b.require(v==native.r.proof.seal(v),'research JSON digest');records[name]=v
  for row in v.get('source_bindings',[]):
   b.require(hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256'],'research source drift: '+row['path']);names.add(row['path'])
 execution=native.checked(root);names.update(row['path'] for row in execution['source_bindings'])
 completion=records[RESEARCH[0]];sections=records[RESEARCH[2]]
 b.require(len(completion['graphs'])==54 and completion['completion_theorem_passes'],'completion coverage')
 authority=records[RESEARCH[3]]
 b.require(len(authority['contracts'])==11 and list(authority['debts'])==['GTRS-RG-DEBT-C1-SECTION-REGULARITY'],'authority roster')
 for t in (*authority['contracts'].values(),*authority['debts'].values()):
  names.update(row['source_ref']['path'] for row in t['rows'])
 return dict(schema='phase9_arg2b_work_v1',family='A_RG2b',realization_number=10,stage=execution['stage'],
  graph_certificates=54,prepared_sections=[dict(graph=x['graph'],role=x['role'],section_passed=x['certificate']['section_tolerance_passes'],
   exact_real_first_step_positive=x['certificate']['exact_real_first_step_positive'],
   section_error_upper=float(native.r.Q(x['certificate']['section_error_upper'])),
   exact_real_resource_lower=float(native.r.Q(x['certificate']['exact_real_next_resource_lower']))) for x in sections['cases']],
  original_reset_exclusion_preserved=True,D94_componentwise_frontier_certificate=True,
  native_execution=execution['checkpoints'],native_review_digest=execution['record_digest'],
  large_covariance_selected=native.SELECTED,large_covariance_deferred=native.DEFERRED,
  remaining_family=None,tranche10='deferred',uniform_trajectory_enclosure=False,
  research_native_steps=0,research_native_events=0,user_accepted=False,aggregate_closed=False,bounded_scope_closed=False,
  acceptance=None,G3_support_added=[],debt_status='C1 regularity remains narrowed and unresolved',
  check_level=execution['check_level'],next_work=execution['next_work'],
  source_refs=[dict(path=p,sha256=hashlib.sha256((root/p).read_bytes()).hexdigest()) for p in sorted(names)])

if __name__=='__main__':
 print(json.dumps(checked(),indent=2))
