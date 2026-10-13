"""CI-only bounded tree23 successor of the accepted tree17 interval argument.

No historical checker or production domain is changed. See the deep C_CI
review for the selector-gap and dimension-dependent argument. No PC carrier
sqrt(m)<=4 conversion is imported into this successor.
"""

from contextlib import contextmanager
from fractions import Fraction as Q
from unittest.mock import patch

import numpy as np
import p984b_cci_runtime as r

n = r.numerical
e = n.exact
IV, number, infinity = n.IV, n.number, n.infinity
OLD_CERTIFICATE, OLD_RESOURCE_ERROR = r.independent_certificate, r.resource_error


def graph_bound(model):
    size, m = len(model.nodes), len(model.edges)
    r.b.require(2 <= size <= 23 and m == size - 1 and len(set(model.nodes)) == size
        and len({v['edge_id'] for v in model.edges}) == m, 'tree23 graph size/identity')
    seen = {model.nodes[0]}
    for edge in model.edges:
        ends = {edge['tail']['node_id'], edge['head']['node_id']}
        r.b.require(len(ends) == 2 and ends <= set(model.nodes), 'invalid tree endpoints')
    while True:
        updated = seen | {end['node_id'] for edge in model.edges
            if edge['tail']['node_id'] in seen or edge['head']['node_id'] in seen
            for end in (edge['tail'], edge['head'])}
        if updated == seen: break
        seen = updated
    r.b.require(seen == set(model.nodes), 'tree23 disconnected graph')
    # Unit connected graph gap >= 2/[N(N-1)]; H >= (1-rho)I > I/2.
    margin = Q(1, size * (size - 1)) - Q(1, 512)
    r.b.require(margin > 0, 'tree23 selector gap')
    return margin


def read_bounds(model, c):
    graph_bound(model)
    radius = e.GEOMETRY_RADIUS
    r.b.require(model.params == n.PARAMS and c.rows == len(model.nodes) and c.cols == 1,
        'tree23 parameter/resource shape')
    r.b.require(all(0 <= n.endpoint(x, 0) <= n.endpoint(x, 1) <= 4 for x in c), 'tree23 resource chart')
    h = e.geometry_box(model, radius)
    e.assert_geometry_ball_covered(model, h, radius)
    read = model.read('C', c, None, h)
    bmax, dnorm = infinity(model.B.T*c), infinity(model.D)
    jmax = infinity(read['J'])
    exp = IV.exp(2*sum(c)/len(model.nodes))
    t = IV.exp(number(n.bounds.KAPPA_M)*(exp-1)/(exp+1))
    response = e.inverse(model.I+t*h*model.D)
    response_norm = infinity(response)
    chi, zeta = n.PARAMS.chi_c, n.PARAMS.zeta_c
    theta = zeta*chi*response_norm
    r.b.require(theta < Q(1, 2), 'tree23 current inverse')
    baseline_lip = n.upper_abs(t)*dnorm*bmax
    response_lip = response_norm**2*n.upper_abs(t)*dnorm
    current_lip = (baseline_lip+zeta*chi*response_lip*jmax)/(1-theta)
    causal = number(chi)*response*read['J']
    causal_lip = chi*(response_lip*jmax+response_norm*current_lip)
    hinv = 1/(1-radius)
    flat = e.inverse(h)*causal
    flat_lip = hinv*causal_lip+hinv**2*infinity(causal)
    mask_norm = max(sum(Q(float(x)) for x in row) for row in model.mask)
    source_lip = 2*zeta*mask_norm*infinity(flat)*flat_lip
    squared = sum(n.upper_abs(x)**2 for x in read['source'])
    e.assert_current_frobenius_aggregation(read['source'], squared)
    q = n.bounds.KAPPA_H*source_lip
    r.b.require(q < 1 and n.bounds.KAPPA_H*infinity(read['source']) < radius,
        'tree23 CI self-map/contraction')
    # Preserve the old stronger source ceiling, although CI has no carrier.
    r.b.require(squared < e.CARRIER_RADIUS**2, 'tree23 source ceiling')
    return dict(contraction=q, regularity=1-theta)


def certify(before, value):
    model = r.independent_model(before)
    high = n.IntervalRows(model)
    c = n.vector(before.current.C)
    budget = read_bounds(high, c)
    m = len(model.edges)
    h = np.array(value['H'])
    n.finite_array(h, (m, m))
    r.b.require(np.array_equal(h, h.T) and np.all(h[model.mask == 0] == 0), 'tree23 geometry structure')
    hp = IV.matrix(h.tolist())
    r.b.require(infinity(hp-high.I) <= e.GEOMETRY_RADIUS, 'tree23 geometry ball')
    image = high.I + number(n.bounds.KAPPA_H)*high.read('C', c, None, hp)['source']
    residual = infinity(hp-image)
    root_error = residual/(1-budget['contraction'])
    r.b.require(root_error < n.GEOMETRY_ERROR_LIMIT, 'tree23 root error')
    padding = budget['contraction']*root_error
    exact_h = IV.matrix([[IV.mpf([(image[i,j]-number(padding)).a,
        (image[i,j]+number(padding)).b]) if model.mask[i,j] else number(0)
        for j in range(m)] for i in range(m)])
    read = high.read('C', c, None, exact_h)
    current_error = n.full_error(value['J'], read['J'])
    baseline_error = n.full_error(value['baseline'], read['baseline'])
    source_error = n.matrix_error(np.array(value['source']), read['source'])
    r.b.require(max(current_error, baseline_error) < n.CURRENT_ERROR_LIMIT
        and source_error < n.SOURCE_ERROR_LIMIT, 'tree23 full-formula error')
    return dict(high=high, c=c, read=read, certificate=dict(**budget, residual=residual,
        root_error=root_error, current_error=current_error, source_error=source_error))


def independent_certificate(before, value):
    if len(before.current.C) <= 17:
        return OLD_CERTIFICATE(before, value)
    truth = certify(before, value)
    return dict(input_identity=before.identity, selected_root_digest=value['record_digest'],
        bounds={k:str(v) for k,v in truth['certificate'].items()},
        theorem='C_CI_unit_tree23_pointwise_joint_root_v1')


def resource_error(before, root, after):
    if len(before.current.C) <= 17:
        return OLD_RESOURCE_ERROR(before, root, after)
    truth = certify(before, root)
    expected = truth['c'] - number(before.dt)*truth['high'].B*truth['read']['J']
    return str(n.full_error(after, expected))


@contextmanager
def checker():
    """Only replace independent research certificates; native calls unchanged."""
    with patch.object(r, 'independent_certificate', independent_certificate), patch.object(r, 'resource_error', resource_error):
        yield
