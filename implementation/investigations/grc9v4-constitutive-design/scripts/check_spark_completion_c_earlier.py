"""Write or recheck direct earlier C-family certificates and short prefixes."""
from pathlib import Path
import sys,json,lzma,argparse,time
ROOT=Path(__file__).resolve().parents[4];INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
import spark_completion_c_earlier as e


def output(name,value,compressed=False):
    raw=(json.dumps(value,indent=2)+'\n').encode();path=ROOT/e.EARLIER/name
    path.write_bytes(lzma.compress(raw,preset=9)if compressed else raw)
    return dict(path=str(path.relative_to(ROOT)),record_digest=value['record_digest'],raw_bytes=len(raw),stored_bytes=path.stat().st_size)


def build():
    declaration=e.read_json(e.EARLIER+'CEarlierDomain.json');e.bound_sources(declaration)
    originals,sources=e.original_runs();proofs={};prefixes={};preflight=[]
    for family in e.FAMILIES:
        proof,operands=e.certificate(family,declaration);proofs[family]=proof
        for role in ('current','reset'):
            if family=='C_OS':
                preflight.append(e.preflight_cos(declaration,role))
                value=e.fresh_cos_prefix(declaration,role,operands)
            else:
                original=originals[family,role];old=original['checks']
                e.need(old['targets']['1']['graph']==declaration['graphs']['1'],'prefix target graph')
                origin=dict(kind='authenticated_prefix_extracted_from_accepted_interval_run',
                    original_path=e.BASE+'applicability/'+e.PREFIX[family]+'-'+role+'.json.xz',
                    original_record_digest=original['record_digest'],physical_precision_bits=old['arithmetic']['precision_bits'],
                    original_last_executed_step=old['observations'][-1]['step'],
                    source_and_event_unchanged=True,trajectory_rerun=False)
                value=e.select_prefix(family,role,old['observations'],declaration,operands,origin=origin)
            name=e.PREFIX[family]+'-'+role+'-prefix.json.xz'
            prefixes[family+'/'+role]=output(name,value,True)
            print(family,role,value['entry'],value['completion'],flush=True)
    result=e.sealed(dict(schema='spark-completion-c-earlier-proofs-v1',date='2026-11-01',
        domain_digest=declaration['record_digest'],proofs=proofs,prefixes=prefixes,
        COS_optimization_preflights=preflight,original_sources=sources,accepted_authority=False,
        native_completion=False,additional_event_gain=0))
    output('CEarlierProofs.json',result)
    return result


def check():
    declaration=e.read_json(e.EARLIER+'CEarlierDomain.json');e.bound_sources(declaration)
    saved=e.read_json(e.EARLIER+'CEarlierProofs.json');e.need_seal(saved)
    originals,sources=e.original_runs();e.need(sources==saved['original_sources'],'original source roster')
    decisions={};total=0
    for family in e.FAMILIES:
        proof,operands=e.certificate(family,declaration)
        e.need(proof==saved['proofs'][family],'whole-domain proof changed')
        for role in ('current','reset'):
            ref=saved['prefixes'][family+'/'+role];value=e.read_json(ref['path']);e.need_seal(value)
            e.need(value['record_digest']==ref['record_digest'],'short prefix identity')
            if family!='C_OS':
                original=originals[family,role]
                e.need(value['origin']['original_record_digest']==original['record_digest'] and
                    value['last_executed_step']==value['origin']['original_last_executed_step']==original['checks']['observations'][-1]['step'] and
                    value['observations']==[{k:row[k]for k in ('step','C','Z')if k in row}
                        for row in original['checks']['observations'][:value['completion']]],'original interval prefix changed')
            again=e.select_prefix(family,role,value['observations'],declaration,operands,origin=value['origin'])
            e.need(again==value,'full-state entry/window or zero-tail claim changed')
            decisions[family+'/'+role]=dict(entry=value['entry'],completion=value['completion'],
                supporting_trajectory_steps_after_completion=0,additional_event_gain=0)
            total+=len(value['observations'])
    return dict(status='passed_full_domain_and_short_prefix_checks',decisions=decisions,
        retained_states=total,trajectory_reruns=0,accepted_authority=False,native_completion=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true')
    args=p.parse_args();start=time.monotonic();result=build()if args.write else check()
    print(json.dumps(dict(status='written_pending_review',record_digest=result['record_digest'])if args.write else result,indent=2))
    print('elapsed_seconds',round(time.monotonic()-start,3))
