"""Larger C_OS equation preflight, NOT native admission or an event campaign.

Dense current proposals are approximate. FLINT proves geometry/selector/split
inequalities for their represented operands, not a full error enclosure connecting
those operands to a production current. No evidence here grants 8.4h readiness.
"""

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

from flint import fmpq
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE = "implementation/phase-9-grcv4/tranche-8/"
HERE = "implementation/phase-9-grcv4/verification/"
SELF = HERE + "p984g_cos.py"
TEST = HERE + "test_p984g_cos.py"
PLAN = BASE + "P9-8.4g-COSPlan.md"
REVIEW = BASE + "P9-8.4g-COSReview.md"
INPUTS = BASE + "P9-8.4g-COSInputs.json"
RESULTS = BASE + "P9-8.4g-COSResults.json"
PREPARED = BASE + "larger-graph-examples/C_OS.json"
CASES = tuple((graph, role) for graph in ("source", "target") for role in ("current", "reset"))


def require(value, message):
    if not value:
        raise ValueError(message)


def q(value):
    value = float(value)
    require(math.isfinite(value), "nonfinite exact operand")
    return fmpq(*value.as_integer_ratio())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def seal(value):
    value = deepcopy(value)
    value.pop("record_digest", None)
    return dict(value, record_digest=digest(value))


def read(name):
    return json.loads((ROOT / name).read_text())


def make_manifest():
    paths = [SELF, TEST, PLAN, PREPARED, BASE + "P9-8.3-AllRealizationsRequest.json",
             "specs/grc-v4-spec.md", "specs/grc-9-v4-spec.md",
             "src/pygrc/models/grc_v4_realizations.py", "src/pygrc/models/grc_v4_geometry.py",
             "src/pygrc/models/grc_v4_candidate_c.py", "src/pygrc/models/grc_v4_transport.py"]
    return seal(dict(schema="p984g-cos-inputs-v1", family="C_OS", cases=[list(c) for c in CASES],
        source_bindings=[dict(path=p, sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths],
        declaration="unchanged_P9_8_3_larger_C_OS", exact_scalar_backend="python-flint.fmpq",
        dense_comparison=dict(atol=2e-11, rtol=2e-11),
        retained_budget_bytes=500000, consumer=SELF,
        ceiling="independent_equation_preflight_and_exact_bounds_on_represented_oracle_operands",
        native_admission=False, native_steps=0, native_events=0, ready_for_8_4h=False,
        user_accepted=False, aggregate_closed=False))


def graph_data(subject):
    """Independent endpoint/BFS assembly, outward-tail incidence convention."""
    graph = subject["graph"]
    nodes, edges = graph["live_node_ids"], graph["edges"]
    require(len(set(nodes)) == len(nodes) and len(nodes) > 1, "invalid vertices")
    require(len({e['edge_id'] for e in edges}) == len(edges), "duplicate edges")
    index = {n: i for i, n in enumerate(nodes)}
    b = np.zeros((len(nodes), len(edges)))
    adjacency = {n: set() for n in nodes}
    pairs = set()
    for j, e in enumerate(edges):
        u, v = e['tail']['node_id'], e['head']['node_id']
        require(u in index and v in index and u != v and frozenset((u,v)) not in pairs,
                "simple loop-free graph required for gap proof")
        pairs.add(frozenset((u,v)))
        b[index[u],j], b[index[v],j] = 1, -1
        adjacency[u].add(v); adjacency[v].add(u)
    seen, pending = {nodes[0]}, [nodes[0]]
    while pending:
        for n in adjacency[pending.pop()] - seen:
            seen.add(n); pending.append(n)
    require(len(seen) == len(nodes), "connected graph required for gap proof")
    params = subject['profile']['params_resolved']
    weights = params['candidate']['W_C_tr']
    require(set(weights) == {e['edge_id'] for e in edges} and all(x == 1 for x in weights.values()),
            "this prerequisite proof requires unit structural weights")
    return b, params


def dense_point(b, c, h, p):
    """Literal dense C equations, no production current/selector/solve helper."""
    values, vectors = np.linalg.eigh(b @ h @ b.T)
    selected = vectors[:, values < p['Lambda_C']]
    sector = selected @ (selected.T @ c)
    rho = np.tanh(sector / p['C_ref'])
    edge_rho = abs(b).T @ rho / 2
    d = np.exp(p['kappa_M_C'] * edge_rho / 2)
    hm = d[:, None] * h * d[None, :]
    phi = p['kappa_Phi_C'] * b @ hm @ b.T @ c
    baseline = -p['eta_C'] * b.T @ phi
    ident = np.linalg.solve(h.T, hm.T).T
    metric = np.linalg.solve(h.T, ident.T).T
    response_metric = np.linalg.solve(np.eye(len(h)) + p['tau_C'] * b.T @ b @ hm, metric)
    flux_response = np.linalg.solve(metric, response_metric)
    block = np.eye(len(h)) - p['zeta_C'] * p['chi_C'] * flux_response
    current = np.linalg.solve(block, baseline)
    flux = p['chi_C'] * flux_response @ current
    flat = np.linalg.solve(h, flux)
    return dict(current=current.tolist(), read_flux=flux.tolist(), causal_flat=flat.tolist(),
        baseline=baseline.tolist(), potential=phi.tolist(), sector=sector.tolist(),
        selected_rank=int(selected.shape[1]),
        current_residual_inf=float(np.max(abs(block @ current - baseline))),
        sharp_residual_inf=float(np.max(abs(h @ flat - flux))))


def generated_h(b, flat, params):
    """Declared star -> zeta -> kappa -> reference staged binary64 operations.

    FLINT scalar products own each exact dyadic multiplication before rounding.
    No production SPD constructor is called for these independent proposals.
    """
    flat = np.asarray(flat, dtype=float)
    require(flat.shape == (b.shape[1],) and np.isfinite(flat).all(), "invalid flat current")
    overlap = abs(b).T @ abs(b) / 2
    h = np.eye(len(flat))
    zeta, gain = q(params['candidate']['zeta_C']), q(params['geometry']['kappa_H'])
    f = [q(x) for x in flat]
    for i, j in zip(*np.nonzero(overlap), strict=True):
        star = float(q(overlap[i,j]) * f[i] * f[j])
        increment = float(zeta * q(star))
        product = float(gain * q(increment))
        h[i,j] = float(q(h[i,j]) + q(product))
    require(np.isfinite(h).all() and np.array_equal(h,h.T), "invalid generated geometry")
    return h


def row_norm(matrix):
    return max((sum((abs(q(x)) for x in row if x), fmpq(0)) for row in matrix), default=fmpq(0))


def exact_bounds(b, h, regenerated, params):
    """Exact sufficient inequalities for represented oracle H, not root errors."""
    require(h.shape == regenerated.shape == (b.shape[1], b.shape[1]), "geometry shape")
    require(np.isfinite(h).all() and np.isfinite(regenerated).all()
            and np.array_equal(h,h.T) and np.array_equal(regenerated,regenerated.T), "non-symmetric geometry")
    # Do not round the subtraction before testing the residual.
    perturb = max(sum((abs(q(x)-int(i==j)) for j,x in enumerate(row)), fmpq(0)) for i,row in enumerate(h))
    split = max(sum((abs(q(x)-q(y)) for x,y in zip(a,z,strict=True)), fmpq(0))
                for a,z in zip(h,regenerated,strict=True))
    gap = (1-perturb)/fmpq(b.shape[0]*(b.shape[0]-1))
    cutoff = q(params['candidate']['Lambda_C'])
    return dict(geometry_perturbation_inf=str(perturb), affine_path_gap_lower=str(gap),
        cutoff=str(cutoff), split_norm_upper=str(split), split_tolerance=str(q(params['realization']['tolerance'])),
        spd=bool(perturb < 1), selector_path_separated=bool(perturb < 1 and 0 < cutoff < gap),
        split_within_tolerance=bool(split <= q(params['realization']['tolerance'])),
        scope="represented_oracle_operands_only_not_native_or_full_error_bound")


def assess(subject, role, predictor, corrector, dt):
    b, params = graph_data(subject)
    c = np.array(subject['roles'][role]['C'])
    require(c.shape == (b.shape[0],) and np.isfinite(c).all() and min(c)>=0, "invalid resource")
    h = generated_h(b, predictor['causal_flat'], params)
    regenerated = generated_h(b, corrector['causal_flat'], params)
    bounds = exact_bounds(b,h,regenerated,params)
    current = corrector['current']
    require(len(current) == b.shape[1], "current dimension")
    divergence = [float(sum((q(w)*q(j) for w,j in zip(row,current,strict=True) if w),fmpq(0))) for row in b]
    after = [float(x - float(dt*y)) for x,y in zip(c,divergence,strict=True)]
    return dict(bounds=bounds, predictor=predictor, corrector=corrector,
        continuity_proposal=after, minimum_resource=min(after),
        negative_nodes=[subject['graph']['live_node_ids'][i] for i,x in enumerate(after) if x<0],
        represented_charge_drift=str(sum((q(x) for x in after), fmpq(0))-sum((q(x) for x in c), fmpq(0))),
        predictor_corrector_difference=max(abs(x-y) for x,y in zip(predictor['current'],current,strict=True)),
        generated_h_digest=digest(h.tolist()), regenerated_h_digest=digest(regenerated.tolist()))


def calculate():
    prepared = read(PREPARED)
    cases = []
    for graph, role in CASES:
        subject = prepared[graph]
        b, params = graph_data(subject)
        c = np.array(subject['roles'][role]['C'])
        predictor = dense_point(b,c,np.eye(b.shape[1]),params['candidate'])
        h = generated_h(b,predictor['causal_flat'],params)
        corrector = dense_point(b,c,h,params['candidate'])
        cases.append(dict(graph=graph,role=role,**assess(subject,role,predictor,corrector,
            prepared['selected_configuration']['ordinary_dt'])))
    manifest=make_manifest()
    return seal(dict(schema="p984g-cos-equation-preflight-v1",inputs_digest=manifest['record_digest'],cases=cases,
        exact_backend="python-flint.fmpq", dense_backend="numpy.linalg",
        numpy_version=np.__version__, native_admission=False,native_steps=0,native_events=0,
        full_error_enclosure=False,ready_for_8_4h=False,user_accepted=False,aggregate_closed=False))


def check(m, result, *, recheck_numerics=False):
    require(m == make_manifest(), "input/source drift")
    require(result == seal(result) and result['inputs_digest']==m['record_digest'], "result/input identity")
    require(result['schema']=='p984g-cos-equation-preflight-v1' and
        result['exact_backend']=='python-flint.fmpq' and result['dense_backend']=='numpy.linalg', "foreign evidence")
    require(all(result[k] is False for k in ('native_admission','full_error_enclosure','ready_for_8_4h','user_accepted','aggregate_closed'))
            and result['native_steps']==result['native_events']==0, "widened scope")
    require([(c['graph'],c['role']) for c in result['cases']]==list(CASES), "case coverage/order")
    prepared=read(PREPARED)
    for case in result['cases']:
        expected=assess(prepared[case['graph']],case['role'],case['predictor'],case['corrector'],
                        prepared['selected_configuration']['ordinary_dt'])
        require(case == dict(graph=case['graph'],role=case['role'],**expected), "operand/bound/continuity drift")
        require(all(case['bounds'][k] for k in ('spd','selector_path_separated','split_within_tolerance')), "oracle bound failed")
        for point in (case['predictor'],case['corrector']):
            require(point['selected_rank']==1 and 0<=point['current_residual_inf']<=2e-11
                and 0<=point['sharp_residual_inf']<=2e-11, "dense point residual/rank")
    if recheck_numerics:
        fresh=calculate()
        for actual,old in zip(fresh['cases'],result['cases'],strict=True):
            for stage in ('predictor','corrector'):
                for key in ('current','read_flux','causal_flat','baseline','potential','sector'):
                    require(np.allclose(actual[stage][key],old[stage][key],**m['dense_comparison']), "dense oracle drift")
            require(actual['negative_nodes']==old['negative_nodes'], "continuity sign drift")
    return dict(family="C_OS",status="equation_preflight_only",cases=4,
        exact_oracle_geometry_bounds=4,native_admission=False,native_steps=0,native_events=0,
        ready_for_8_4h=False,user_accepted=False,aggregate_closed=False,
        full_error_enclosure=False,numerical_equations_recomputed=recheck_numerics,
        open_obligations=["LG-C-SELECTOR native/validated-current bridge", "LG-OS-SPLIT native/validated-current bridge",
                          "native read completion and subsequent runtime feasibility"])


def write_new(name, value):
    text=json.dumps(value,indent=2,allow_nan=False)+'\n'
    require(len(text.encode())<=500000,"declared retained-data budget exceeded; revise before execution")
    with (ROOT/name).open('x') as output:
        output.write(text)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','run-equations','check'))
    parser.add_argument('--recheck-numerics',action='store_true')
    args=parser.parse_args()
    require(not args.recheck_numerics or args.action=='check','recheck only in check mode')
    if args.action=='prepare':write_new(INPUTS,make_manifest())
    elif args.action=='run-equations':
        require(not (ROOT/RESULTS).exists(),'no overwrite of retained results')
        m=read(INPUTS);require(m==make_manifest(),'input/source drift')
        result=calculate();check(m,result);write_new(RESULTS,result)
    else:print(json.dumps(check(read(INPUTS),read(RESULTS),recheck_numerics=args.recheck_numerics),indent=2))


if __name__=='__main__':main()
