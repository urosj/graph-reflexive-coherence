"""Exact-subject support and retained closure, without inferring acceptance."""
from pathlib import Path
import sys
import p9_arg2b_campaign as c
import p9_arg2b_integration as integration
import p9_arg2b_support as support
b=c.b
SELF=b.HERE+'p9_arg2b_close.py'
AUTHORITY=c.BASE+'9.6-Authority.json'
SIDE='implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/'
IDS=tuple('D10.2-EC-DISABLED-A_RG2b-'+s for s in ('TRANSITION','STATE','OBSERVABLE','LIFECYCLE'))

def authority():
 sys.path.insert(0,str(b.ROOT/SIDE/'tool/src'))
 from grcv4_explorer.basin import load_basin_forensic_context
 from grcv4_explorer.forensic import contract_provenance
 context=load_basin_forensic_context(b.ROOT,b.ROOT/SIDE)
 traces={key:contract_provenance(context,key) for key in IDS}
 refs={SELF,*(d.path.resolve().relative_to(b.ROOT).as_posix() for d in context.documents)}
 for module in tuple(sys.modules.values()):
  filename=getattr(module,'__file__',None)
  if filename and Path(filename).resolve().is_relative_to(b.ROOT/SIDE/'tool/src'):
   refs.add(Path(filename).resolve().relative_to(b.ROOT).as_posix())
 from grcv4_explorer.canonical import digest
 for key,t in traces.items():
  b.require(t['trace_digest']==digest({k:v for k,v in t.items() if k!='trace_digest'}) and t['query']==dict(contract_id=key)
   and t['row_count']==1 and t['rows'][0]['payload']['support_disposition']=='indeterminate_requires_review','authority boundary')
 return b.seal(dict(schema='p9-arg2b-disabled-authority-v1',family='A_RG2b',traces=traces,source_bindings=b.bind(refs),authority_promoted=False))

def build_support():
 rows={key:c.read(integration.path(key)) for key in integration.GROUPS}
 for key in rows:integration.check(key)
 matrix=c.read(support.MATRIX);b.require(matrix==support.matrix(),'exact compatibility roster')
 a=c.read(AUTHORITY);b.check_digest(a);b.check_bindings(a['source_bindings'])
 snapshot=rows['9.1b']['evidence']['mixed_snapshot']
 def subject(v):return dict(model_identity=v['model_identity'],scientific_digest=v['scientific_digest'],
  complete_profile_id=v['inputs']['reference']['profile']['complete_profile_id'])
 return b.seal(dict(schema='p9-arg2b-exact-support-v1',family='A_RG2b',source=subject(snapshot['initial']),
  enabled_target=subject(snapshot['state']),compatibility_source_model=rows['9.2']['evidence']['transition']['model_identity'],
  disabled_surfaces={s:dict(complete_profile_id=r['complete_profile_id'],model_identity=r['model_identity'],target_spec_version=r['target_spec_version'])
    for s,r in rows['9.2']['evidence'].items()},
  authority={k:dict(trace_digest=t['trace_digest'],support_disposition=t['rows'][0]['payload']['support_disposition']) for k,t in a['traces'].items()},
  source_bindings=b.bind({SELF,AUTHORITY,support.MATRIX,*[integration.path(k) for k in rows]}),
  expanded_target_four_surface_compatibility='not_transferred_from_source',basin_policy='unselected',
  C1_regularity_debt='narrowed_unresolved',differentiable_or_spectral_claim=False,
  remaining_family=None,tranche10='deferred',user_accepted=False,aggregate_closed=False))

if __name__=='__main__':
 if not (b.ROOT/AUTHORITY).exists():c.save(AUTHORITY,authority())
 c.save(support.SUPPORT,build_support());print('A_RG2b exact subjects and four authority boundaries retained; no acceptance inferred')
