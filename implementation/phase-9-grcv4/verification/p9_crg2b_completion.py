"""Research-only connected-graph C_RG2b completion feasibility.

Reuse the signed argument-retraction theorem, not the tree17 certificate.
Every inequality below is exact FLINT rational arithmetic. No native profile,
section, event or trajectory is executed or authorized by this checker.
"""
from __future__ import annotations

import argparse
from collections import deque
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import time

from flint import fmpq as Q, fmpq_mat

ROOT = Path(__file__).resolve().parents[3]
BASE = "implementation/phase-9-grcv4/"
SELF = BASE + "verification/p9_crg2b_completion.py"
TEST = BASE + "verification/test_p9_crg2b_completion.py"
PLAN = BASE + "tranche-8/P9-CRG2b-Tranches8-9-Plan.md"
NOTE = BASE + "tranche-8/P9-CRG2b-ConnectedCompletion.md"
RESULT = BASE + "tranche-8/P9-CRG2b-CompletionFeasibility.json"
INPUTS = (
    BASE + "tranche-8/P9-8.4d-COSCases.json",
    BASE + "tranche-8/larger-graph-examples/C_RG2b.json",
    BASE + "tranche-8/P9-8.4c-CRG2bCases.json",
)
RHO, LIP, DT = Q(1, 4096), Q(1, 1024), Q(1, 4096)
CHI, ZETA, KM, KH, CUTOFF = Q(16), Q(1, 2**37), Q(1, 2**24), Q(1, 2), Q(1, 512)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=digest(body))


def read(path):
    return json.loads((ROOT / path).read_bytes())


def eye(n):
    return fmpq_mat([[int(i == j) for j in range(n)] for i in range(n)])


def norm(matrix):
    return max((sum((abs(matrix[i, j]) for j in range(matrix.ncols())), Q(0))
                for i in range(matrix.nrows())), default=Q(0))


def graph_algebra(graph):
    """Independent incidence, port ownership, connectivity and exact diameter."""
    nodes, edges = graph["live_node_ids"], graph["edges"]
    require(len(nodes) >= 2 and len(set(nodes)) == len(nodes), "invalid vertex roster")
    require(len({e['edge_id'] for e in edges}) == len(edges), "duplicate edge identity")
    index = {node: i for i, node in enumerate(nodes)}
    b = [[0] * len(edges) for _ in nodes]
    adjacency = [set() for _ in nodes]
    occupied, pairs = set(), set()
    for k, edge in enumerate(edges):
        ends = []
        for side in ('tail', 'head'):
            end = edge[side]
            node, port = end['node_id'], end['port']
            require(node in index and type(port) is int and 1 <= port <= 9,
                    'invalid nine-port endpoint')
            require((node, port) not in occupied, 'port collision')
            occupied.add((node, port)); ends.append(index[node])
        i, j = ends
        require(i != j and frozenset(ends) not in pairs, 'simple loop-free graph required')
        pairs.add(frozenset(ends))
        b[i][k], b[j][k] = 1, -1
        adjacency[i].add(j); adjacency[j].add(i)
    diameter = 0
    for start in range(len(nodes)):
        distances, queue = {start: 0}, deque([start])
        while queue:
            i = queue.popleft()
            for j in adjacency[i] - distances.keys():
                distances[j] = distances[i] + 1; queue.append(j)
        require(len(distances) == len(nodes), 'connected graph required')
        diameter = max(diameter, max(distances.values()))
    b = fmpq_mat(b)
    absolute = fmpq_mat([[abs(b[i, j]) for j in range(b.ncols())] for i in range(b.nrows())])
    gram, mask = b.transpose() * b, absolute.transpose() * absolute / 2
    return b, gram, mask, diameter


def response_bounds(r0, s0, *, rho=RHO, km=KM):
    """Uniform noncommuting resolvent bound over the ENTIRE H/t chart.

    A0=I+D, R0=A0^-1, E=(tH-I)D R0, A=(I+E)A0.
    R=R0(I+E)^-1. This is a norm proof, not a replacement physical read.
    """
    require(0 <= rho < 1 and 0 <= km < 1 and r0 >= 0 and s0 >= 0,
            'invalid response hypothesis')
    t = 1 / (1 - km)
    perturbation = (t - 1 + t * rho) * s0
    require(perturbation < 1, 'resolvent Neumann bound inconclusive')
    r = r0 / (1 - perturbation)
    complement = s0 + r0 * perturbation / (1 - perturbation)
    return dict(t_upper=t, perturbation=perturbation, response_upper=r,
                complement_upper=complement)


def global_bounds(degree, gram, mask, response, *, rho=RHO, lip=LIP):
    """Literal C equation slopes; no commuting H/D or PSD-only H perturbation."""
    require(0 < rho < 1 and lip >= 0 and min(degree, gram, mask) > 0,
            'invalid section hypothesis')
    t, r, s = (response[k] for k in ('t_upper', 'response_upper', 'complement_upper'))
    tx, hinv = t * KM, 1 / (1 - rho)
    theta = CHI * ZETA * r
    require(theta < 1, 'physical current inverse unproved')
    j0, j0x, j0h = t * gram * (1 + rho) * 6, gram * (1 + rho) * (2*t + 6*tx), t*gram*6
    rx, rh = r*r*tx*(1+rho)*gram, r*r*t*gram
    j = j0 / (1 - theta)
    jx, jh = (j0x + CHI*ZETA*rx*j)/(1-theta), (j0h + CHI*ZETA*rh*j)/(1-theta)
    # RJ0=(R-I)b - Rt(DH-HD)b, ||DH-HD|| <= 2 ||D|| rho.
    causal = CHI * (s + r*t*2*gram*rho) * 6 / (1-theta)
    cx, ch = CHI*(rx*j+r*jx), CHI*(rh*j+r*jh)
    v, vx, vh = hinv*causal, hinv*cx, hinv*ch+hinv*hinv*causal
    ax, ah, mf = DT*degree*jx, DT*degree*jh, DT*degree*j
    ms, bx, bh = ZETA*mask*v*v, 2*ZETA*mask*v*vx, 2*ZETA*mask*v*vh
    ell = ax + ah*lip
    require(ell < 1, 'completed base inverse not contractive')
    inv = 1 / (1-ell)
    image, image_lip = KH*ms, KH*(bx+bh*lip)*inv
    contraction = KH*(bh + (bx+bh*lip)*inv*ah)
    checks = dict(physical_current_inverse=theta < 1,
                  signed_chart_containment=mf < Q(1, 4),
                  section_image=image < rho,
                  lipschitz_class=image_lip <= lip,
                  graph_transform=contraction < 1)
    values = dict(A_X=ax, A_H=ah, M_f=mf, M_S=ms, B_X=bx, B_H=bh,
                  inverse_lipschitz=inv, value_radius=image, image_lipschitz=image_lip,
                  contraction=contraction, current_upper=j, current_inverse_margin=1-theta)
    # Tail alone is not the residual+rounding certificate for a finite native chain.
    values['six_level_tail_upper'] = contraction**6 * image
    return values, checks


def graph_certificate(graph):
    started = time.monotonic()
    b, d, mask, diameter = graph_algebra(graph)
    n, m = b.nrows(), b.ncols()
    # Rational vertex solve; never invert the m-edge matrix to obtain these bounds.
    laplacian = b*b.transpose()
    r0 = eye(m) - b.transpose() * (eye(n)+laplacian).solve(b)
    response = response_bounds(norm(r0), norm(eye(m)-r0))
    values, checks = global_bounds(norm(b), norm(d), norm(mask), response)
    # Variance <= n range^2/4; range^2 <= diameter * graph Dirichlet energy.
    gap = (1-RHO) * Q(4, n*diameter)
    checks['constant_selector'] = gap > CUTOFF
    checks['same_six_level_tail_budget'] = values['six_level_tail_upper'] < Q(1, 2**48)
    exact = dict(vertices=n, edges=m, cycle_rank=m-n+1, diameter=diameter,
                 incidence_norm=str(norm(b)), gram_norm=str(norm(d)), star_mask_norm=str(norm(mask)),
                 reference_response_norm=str(norm(r0)), reference_complement_norm=str(norm(eye(m)-r0)),
                 selector_lower=str(gap), selector_margin=str(gap-CUTOFF),
                 response={k: str(v) for k, v in response.items()},
                 bounds={k: str(v) for k, v in values.items()}, checks=checks)
    return dict(exact, graph_digest=digest(graph), elapsed_seconds=time.monotonic()-started)


def subjects():
    deep, large, small = map(read, INPUTS)
    validate_large_recipe(large)
    rows = [('accepted-small/'+c['fixture_id'], c['oracle']['target_graph']) for c in small['cases']]
    rows += [('deep/'+c['fixture_id'], c['oracle']['target_graph']) for c in deep['cases']]
    rows += [('large/'+role, large[role]['graph']) for role in ('source', 'target')]
    require(len(rows) == 54, 'bounded graph roster changed')
    return rows


def validate_large_recipe(large):
    require(large['reference_recipe'] == dict(unit_vertex_measures=True, unit_edge_weights=True,
        K4_base='exact zero m by m in each graph edge order',
        context=dict(contract_id='constant_zero_context_v1', values={})), 'reference recipe drift')
    expected=dict(Lambda_C=Q(1,512),C_ref=Q(1),kappa_M_C=KM,kappa_Phi_C=Q(1),
                  eta_C=Q(1),tau_C=Q(1),chi_C=CHI,zeta_C=ZETA)
    for role in ('source','target'):
        subject=large[role];profile=subject['profile'];params=profile['params_resolved']
        require(profile['identity_payload']['profile_family_id']=='C_RG2b'
                and profile['identity_payload']['realization']=='RG2b','wrong realization')
        for name,value in expected.items():
            raw=params['candidate'][name]
            exact=Q(*float(raw).as_integer_ratio())
            require(exact==value,'scientific parameter changed: '+name)
        weights=params['candidate']['W_C_tr']
        require(set(weights)=={e['edge_id'] for e in subject['graph']['edges']}
                and all(v==1 for v in weights.values()),'nonunit/mismatched transport weights')
        require(params['geometry']['kappa_H']==0.5,'geometry gain changed')
        require(all(v['W_A'] is None and v['Z_4'] is None for v in subject['roles'].values()),
                'unexpected authoritative history')
    require(large['selected_configuration']['ordinary_dt']==float(DT), 'timestep changed')


def worker(subject):
    name, graph = subject
    return dict(subject=name, **graph_certificate(graph))


def bindings():
    paths = (*INPUTS, SELF, TEST, PLAN, NOTE,
             BASE+'tranche-8/P9-8.0-RG2bCompletion.md',
             'src/pygrc/models/grc_9_v4_rg2b.py')
    return [dict(path=p, sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]


def check(record):
    require(record == seal(record), 'research record digest drift')
    require(record['schema']=='p9-crg2b-completion-feasibility-v1','unknown research schema')
    require(record['source_bindings'] == bindings(), 'research source drift')
    require(record['scope'] == scope(), 'research scope drift')
    declared = subjects()
    require([r['subject'] for r in record['graphs']] == [s[0] for s in declared], 'graph roster drift')
    for row, (_, graph) in zip(record['graphs'], declared, strict=True):
        require(row['graph_digest'] == digest(graph), 'graph subject mismatch')
    require(record['completion_theorem_passes'] == all(all(v for k,v in r['checks'].items()
            if k != 'same_six_level_tail_budget') for r in record['graphs']), 'completion verdict mismatch')
    require(record['six_level_tail_budget_passes'] == all(r['checks']['same_six_level_tail_budget']
            for r in record['graphs']), 'finite-tail verdict mismatch')
    return record


def scope():
    return dict(family='C_RG2b', stage='research_completion_feasibility',
                accepted_small_graphs=32, deep_graphs=20, large_graphs=2,
                arithmetic='FLINT_exact_rational', physical_law_changed=False,
                new_completion_domain=True, native_steps=0, native_events=0,
                numerical_chain_certified=False, physical_positivity_certified=False,
                G3_support_added=[], user_accepted=False, aggregate_closed=False,
                C1_debt='GTRS-RG-DEBT-C1-SECTION-REGULARITY_unresolved')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    require(args.run != args.check and 1 <= args.workers <= 12, 'select run/check and 1..12 workers')
    if args.check:
        record = check(read(RESULT))
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            fresh = list(pool.map(worker, subjects()))
        for retained, recomputed in zip(record['graphs'], fresh, strict=True):
            require({k:v for k,v in retained.items() if k != 'elapsed_seconds'} ==
                    {k:v for k,v in recomputed.items() if k != 'elapsed_seconds'},
                    'exact graph certificate changed')
    else:
        require(not (ROOT/RESULT).exists(), 'refuse to overwrite retained research')
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = list(pool.map(worker, subjects()))
        record = seal(dict(schema='p9-crg2b-completion-feasibility-v1', scope=scope(),
            source_bindings=bindings(), graphs=rows,
            completion_theorem_passes=all(all(v for k,v in r['checks'].items()
                if k != 'same_six_level_tail_budget') for r in rows),
            six_level_tail_budget_passes=all(r['checks']['same_six_level_tail_budget'] for r in rows)))
        check(record)
        (ROOT/RESULT).write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({k: record[k] for k in ('completion_theorem_passes','six_level_tail_budget_passes','scope')}, indent=2))


if __name__ == '__main__':
    main()
