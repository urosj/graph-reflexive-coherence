"""One capped current-code A_CI source beat; no expansion event execution."""
import argparse
import json
import lzma
import multiprocessing as mp
import os
import time

import p984h_aci as prep
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy, GRC9V4ExpansionPlan, GRC9V4ExpansionRequestInput,
)

ROOT, BASE, HERE = prep.ROOT, prep.BASE, prep.HERE
SELF = HERE + 'p984h_aci_source.py'
TEST = HERE + 'test_p984h_aci_source.py'
INPUTS = BASE + 'P9-8.4h-ACISourceInputs.json'
RESULT = BASE + 'P9-8.4h-ACI-source.json.xz'
require, seal, digest = prep.require, prep.seal, prep.digest


def bindings():
    old = json.loads((ROOT / prep.INPUTS).read_text())
    require(old == seal(old), 'preparation seal')
    require(all(prep.sha(p) == h for p, h in old['source_bindings'].items()), 'preparation source drift')
    paths = set(old['source_bindings']) | {prep.INPUTS, SELF, TEST}
    return seal(dict(schema='p984h-aci-source-inputs-v1', preparation_digest=old['record_digest'],
        source_bindings={p: prep.sha(p) for p in sorted(paths)},
        exact_backend=old['exact_backend'], numerical_policy=old['numerical_policy'],
        cap_seconds=prep.CAPS['source'], compressed_budget_bytes=2000000,
        planned_native_steps=1, planned_native_roots=3, planned_native_events=0))


def fresh_binding(post, result, request):
    require(request == prep.fresh_request(post), 'fresh source/history request mismatch')
    trigger = result['poststep_trigger']
    require(trigger['saturated'] and trigger['small_gradient'] and trigger['strict_hessian_condition']
            and not trigger['native_trigger_receipt'], 'postbeat trigger prerequisites')
    plan = GRC9V4ExpansionPlan(post.inputs.geometry.reference.graph.port_graph, post.scientific_digest,
        GRC9V4ExpansionRequestInput.from_payload(request),
        GRC9ExpansionPolicy.from_payload(post.specialization.resolved['expansion']))
    return dict(source_state_digest=post.scientific_digest, request_digest=digest(request),
        event_id=plan.event_id, target_graph_digest=plan.target_graph.graph_digest,
        trigger=trigger, trigger_operand_digest=digest(dict(C=list(post.inputs.current.C),
                                                           W_A=list(post.inputs.current.W_A))),
        scope='source_trigger_and_mechanical_declaration_not_admitted_event',
        source_nodes=len(plan.source_graph.live_node_ids), target_nodes=len(plan.target_graph.live_node_ids),
        source_edges=len(plan.source_graph.edges), target_edges=len(plan.target_graph.edges))


def execute(progress):
    output = prep.source_adapter(progress)
    initial, _, _ = prep.seed()
    post = prep.poststate(initial, output['result'])
    require(output['state'] == post.to_payload(), 'adapter poststate mismatch')
    output['fresh'] = fresh_binding(post, output['result'], output['request'])
    output.update(native_steps=1, native_roots=3, native_events=0,
                  historical_source_digest=prep.accepted_source()['record_digest'])
    progress('postbeat_request_and_history_bound')
    return output


def worker(pipe):
    try:
        value = execute(lambda stage: pipe.send(('progress', stage)))
        pipe.send(('result', value))
    except Exception as exc:
        pipe.send(('error', dict(type=type(exc).__name__, message=str(exc))))
    finally:
        pipe.close()


def run():
    require(not (ROOT / RESULT).exists(), 'refuse overwrite')
    require(all(os.environ.get(k) == '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS')), 'single thread')
    manifest = bindings()
    require(json.loads((ROOT / INPUTS).read_text()) == manifest, 'source manifest drift')
    context = mp.get_context('spawn')
    receive, send = context.Pipe(False)
    child = context.Process(target=worker, args=(send,))
    start = time.monotonic()
    child.start(); send.close()
    result = None
    try:
        while True:
            remaining = manifest['cap_seconds'] - (time.monotonic() - start)
            require(remaining > 0, '600-second source cap reached; no retry or fallback')
            if receive.poll(min(0.25, remaining)):
                try:
                    kind, value = receive.recv()
                except EOFError:
                    break
                if kind == 'progress':
                    print(json.dumps(dict(stage=value, seconds=time.monotonic()-start)), flush=True)
                elif kind == 'error':
                    raise RuntimeError(str(value))
                elif kind == 'result':
                    result = value
                    break
            elif not child.is_alive():
                break
        child.join(timeout=max(0, min(5, manifest['cap_seconds']-(time.monotonic()-start))))
        seconds = time.monotonic() - start
        require(child.exitcode == 0 and result is not None and seconds <= manifest['cap_seconds'],
                'incomplete source execution')
    finally:
        if child.is_alive():
            child.terminate(); child.join(timeout=3)
        if child.is_alive():
            child.kill(); child.join(timeout=3)
        receive.close()
    require(bindings() == manifest, 'sources changed during execution')
    record = seal(dict(schema='p984h-aci-source-v1', manifest_digest=manifest['record_digest'],
        execution=result, seconds=seconds, outcome='completed', user_accepted=False, aggregate_closed=False))
    raw = lzma.compress(json.dumps(record, separators=(',', ':'), allow_nan=False).encode()+b'\n')
    require(len(raw) <= manifest['compressed_budget_bytes'], 'compressed budget exceeded')
    with (ROOT / RESULT).open('xb') as stream:
        stream.write(raw)
    print(json.dumps(dict(outcome='completed', seconds=seconds, compressed_bytes=len(raw))), flush=True)


def check(value=None):
    manifest = bindings()
    require(json.loads((ROOT / INPUTS).read_text()) == manifest, 'source manifest drift')
    value = json.loads(lzma.decompress((ROOT / RESULT).read_bytes())) if value is None else value
    require(value == seal(value) and value['manifest_digest'] == manifest['record_digest'], 'execution binding')
    require(value['outcome'] == 'completed' and 0 < value['seconds'] <= manifest['cap_seconds']
            and value['user_accepted'] is False and value['aggregate_closed'] is False, 'execution scope')
    e = value['execution']; historical = prep.accepted_source()
    prep.compare_source_result(e['result'], historical['result'])
    require(e['historical_source_digest'] == historical['record_digest']
            and (e['native_steps'], e['native_roots'], e['native_events']) == (1, 3, 0), 'execution credit')
    initial, _, _ = prep.seed(); post = prep.poststate(initial, e['result'])
    require(e['state'] == post.to_payload() and e['fresh'] == fresh_binding(post, e['result'], e['request']),
            'retained poststate/request/trigger drift')
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'run', 'check'))
    args = parser.parse_args()
    if args.action == 'prepare':
        with (ROOT / INPUTS).open('x') as stream:
            json.dump(bindings(), stream, indent=2); stream.write('\n')
    elif args.action == 'run':
        run()
    else:
        record = check()
        print(json.dumps(dict(outcome=record['outcome'], retained_only=True, native_rerun=False)))
