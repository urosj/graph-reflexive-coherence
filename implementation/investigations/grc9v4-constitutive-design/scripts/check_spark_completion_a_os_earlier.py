"""Recheck earlier A_OS domains and retained interval entry; no trajectory run."""
from pathlib import Path
import argparse,json,lzma,sys,time
ROOT=Path(__file__).resolve().parents[4]
INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
import spark_completion_a_os_earlier as e


def check():
    actual=e.recompute();retained=e.read_json(e.EARLIER+'AOSEarlierChecks.json.xz');e.need_seal(retained)
    e.need(actual==retained,'earlier-domain proof/entry differs from retained evidence')
    return dict(status='passed_full_interval_proof_and_retained_entry',record_digest=actual['record_digest'],
        decisions={r:{k:v[k] for k in ('anisotropic_entry','anisotropic_window_end','ball_entry','ball_window_end')}
                   for r,v in actual['runs'].items()},retained_states=sum(v['retained_states_checked'] for v in actual['runs'].values()),
        trajectory_reruns=0,additional_event_gain=0,accepted_authority=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--check',action='store_true');g.add_argument('--write',action='store_true')
    args=p.parse_args();start=time.monotonic()
    if args.write:
        value=e.recompute();raw=(json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
        path=ROOT/e.EARLIER/'AOSEarlierChecks.json.xz';path.write_bytes(lzma.compress(raw,preset=9))
        result=dict(status='written_pending_review',record_digest=value['record_digest'],raw_bytes=len(raw),compressed_bytes=path.stat().st_size)
    else:result=check()
    print(json.dumps(dict(**result,elapsed_seconds=round(time.monotonic()-start,3)),indent=2))
