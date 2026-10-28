"""Existing A_OS contract provenance; no authority or claim promotion."""
from pathlib import Path
import sys
import p984d_aos_oracle as o

b=o.b
SELF=b.HERE+'p99_aos_authority.py'
PATH='implementation/phase-9-grcv4/tranche-9/P9-9.2-AOSAuthority.json'
SIDE=b.ROOT/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool'
IDS=tuple('D10.2-EC-DISABLED-A_OS-'+surface for surface in ('TRANSITION','STATE','OBSERVABLE','LIFECYCLE'))


def build():
    sys.path.insert(0,str(SIDE/'tool/src'))
    from grcv4_explorer.basin import load_basin_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context=load_basin_forensic_context(b.ROOT,SIDE)
    traces={key:contract_provenance(context,key) for key in IDS}
    paths={SELF,*(d.path.resolve().relative_to(b.ROOT).as_posix() for d in context.documents)}
    for module in tuple(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename and Path(filename).resolve().is_relative_to(SIDE/'tool/src'):
            paths.add(Path(filename).resolve().relative_to(b.ROOT).as_posix())
    return b.seal(dict(schema='p99-aos-authority-v1',family='A_OS',traces=traces,
        source_bindings=b.bind(paths),new_scientific_claims=False,authority_promoted=False))


def check(value=None):
    sys.path.insert(0,str(SIDE/'tool/src'))
    value=o.read(PATH) if value is None else value
    b.check_digest(value);b.check_bindings(value['source_bindings'])
    b.require(value['schema']=='p99-aos-authority-v1' and value['family']=='A_OS'
        and set(value['traces'])==set(IDS) and value['new_scientific_claims'] is False
        and value['authority_promoted'] is False,'authority scope')
    from grcv4_explorer.canonical import digest
    for key,trace in value['traces'].items():
        b.require(trace['trace_digest']==digest({k:v for k,v in trace.items() if k!='trace_digest'})
            and trace['query']==dict(contract_id=key) and trace['row_count']==1
            and trace['rows'][0]['payload']['support_disposition']=='indeterminate_requires_review',
            'contract provenance or inherited limitation changed')
    return value


if __name__=='__main__':
    value=build();check(value);b.write_new(PATH,value)
    print('A_OS four-surface provenance retained; no scientific promotion')
