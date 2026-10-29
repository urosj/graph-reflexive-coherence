"""Independent saved-operand composite residual and contraction error bridge.

Vertex resolvents evaluate the full physical equations at the represented
joint pair. Fixed old Z enters only the geometry equation. The current defect
is corrected before applying the reduced fixed-point contraction bound.
"""
from dataclasses import replace

import p984g_ccipc as g
import p984g_cci_staged as staged
import p9_ccipc_capture as capture

b, q, a, hi, iv = g.b, g.q, g.a, g.hi, g.iv
SELF = b.HERE + 'p984h_ccipc_math.py'
LIMITS = dict(baseline=2**-40, readback=2**-36, flat=2**-36, source=2**-60)


def subject(before):
    ref = before.geometry.reference
    b.require(all(x == 0 for row in ref.K4_base for x in row)
              and set(ref.edge_weights.values()) == {1}, 'unit reference hypothesis')
    return dict(graph=ref.graph.port_graph.to_envelope(), profile=ref.profile.to_payload(),
                roles={role: b.authority_payload(getattr(before, role)) for role in g.ROLES})


def certificate(before, value):
    with g.ctx.workprec(g.BITS):
        operand = subject(before)
        bv, params, bounds = g.whole_chart(operand)
        p = params['candidate']; n, m = bv.shape
        cs = list(map(q, before.current.C))
        z = g.pc.carrier(operand, 'current', m)
        b.require(min(cs) >= 0 and sum((x*x for x in cs), q(0)) <= q(bounds['resource_norm_upper'])**2
                  and sum((x*x for row in z for x in row), q(0)) <= q(bounds['carrier_radius'])**2
                  and all(z[i][j] == z[j][i] for i in range(m) for j in range(i)), 'actual compact chart')
        bm, h, j = iv.matrix(bv), iv.matrix(value['H']), iv.matrix([[x] for x in value['J']])
        c, ident = iv.matrix([[x] for x in cs]), iv.eye(m)
        b.require(g.frobenius_upper(h-ident) <= q(bounds['root_radius']), 'saved trial outside root ball')
        mask = iv.matrix(abs(bv)).transpose()*iv.matrix(abs(bv))/2
        b.require(all(z[i][k] == 0 for i in range(m) for k in range(m) if mask[i,k].is_zero()), 'carrier support')
        mean = sum(cs, q(0))/n
        t = (a(p['kappa_M_C'])*(a(mean)/a(p['C_ref'])).tanh()).exp()
        baseline = -a(p['eta_C'])*a(p['kappa_Phi_C'])*bm.transpose()*(bm*(t*h*(bm.transpose()*c)))
        response = staged.response(bm, h, j, p, t)
        flux = a(p['chi_C'])*response
        flat = h.solve(flux)
        source = iv.eye(m)*0
        for i in range(m):
            for k in range(m):
                if not mask[i,k].is_zero():
                    source[i,k] = a(p['zeta_C'])*mask[i,k]*flat[i,0]*flat[k,0]
        beta = q(p['zeta_C'])*q(p['chi_C'])
        fj = j-baseline-a(beta)*response
        fh = h-ident-a(params['geometry']['kappa_H'])*(iv.matrix(z)+source)
        ej, eh = g.frobenius_upper(fj), g.frobenius_upper(fh)
        squared = ej*ej+eh*eh
        tolerance = q(params['realization']['tolerance'])
        b.require(squared <= tolerance*tolerance, 'independent full joint residual exceeds declared tolerance')
        bridge = staged.bridge(bounds, p['chi_C'], beta,
            q(params['geometry']['kappa_H'])*q(p['zeta_C']), ej, eh)
        errors = {key: str(max(hi(abs(a(x)-exact[i,0])) for i,x in enumerate(value[key])))
                  for key,exact in (('baseline',baseline), ('readback',flux), ('flat',flat))}
        errors['source'] = str(max(hi(abs(a(value['source'][i][k])-source[i,k]))
                                   for i in range(m) for k in range(m)))
        b.require(all(0 <= q(v) < q(LIMITS[k]) for k,v in errors.items()), 'selected signed formula error: '+str(errors))
    return dict(input_identity=before.identity, read_digest=value['record_digest'], whole_chart=bounds,
                errors=errors, current_residual_upper=str(ej), geometry_residual_upper=str(eh),
                joint_residual_squared_upper=str(squared), declared_tolerance=str(tolerance),
                joint_root_error=bridge, precision_bits=g.BITS, uniform_trajectory_enclosure=False)


def capture_read(root):
    import p984b_ccipc_runtime as r
    value = capture.portable(r.capture_root(root))
    value['certificate'] = certificate(root.inputs, value)
    check_read(root.inputs, value)
    return value


def check_read(before, value, *, numerics=False):
    from pygrc.models.grc_v4_geometry import PhysicalFlux
    raw = {k:v for k,v in value.items() if k != 'certificate'}
    b.check_digest(raw)
    ref = before.geometry.reference
    params = ref.profile.params_resolved.realization
    b.require(before.geometry == ref.geometry() and before.stage == 'pre_read', 'fresh reference start')
    b.require(value['input_identity'] == before.identity and value['domain_id'] == params.contraction_domain_id
              and value['recipe'] == 'cipc_same_root_source_enclosed_zoh_binary64_v1', 'root recipe/input')
    recipe = dict(schema_version='grcv4-ci-root-recipe-v1', numerics=value['recipe'],
                  inputs=before.to_payload(), differential_reference=None)
    b.require(value['identity'] == 'grcv4-ci-root-sha256:'+b.digest(recipe), 'root identity')
    b.require(type(value['evaluations']) is int and 1 <= value['evaluations'] <= params.iteration_limit, 'iteration limit')
    selected = replace(before, geometry=b.GRCV4Geometry(ref,b.OneFormHodge(ref.graph,tuple(map(tuple,value['H'])))),
                       stage='cipc_trial', evaluation_index=value['evaluations']-1,
                       trial_current=PhysicalFlux(ref.graph,tuple(value['J'])))
    b.require(selected.identity == value['selected_inputs_identity'] and value['read_current'] == value['J']
              and value['read_source'] == value['point_identity'], 'selected joint pair/Read-Back identity')
    bv, p, whole = g.whole_chart(subject(before)); m = len(value['J'])
    mask = abs(bv).T@abs(bv)/2
    flat = value['flat']; zeta = q(p['candidate']['zeta_C']); kh = q(p['geometry']['kappa_H'])
    source = [[float(zeta*q(float(q(mask[i,k])*q(x)*q(y)))) for k,y in enumerate(flat)] for i,x in enumerate(flat)]
    generated = [[float(q(int(i==k))+kh*q(float(q(before.current.Z_4[i*m+k])+q(x))))
                  for k,x in enumerate(row)] for i,row in enumerate(source)]
    b.require(source == value['source'] and generated == value['generated'], 'fixed old Z/same-root signed source')
    bounds = value['bounds']; R = q(params.radius); radius = q(whole['root_radius'])
    b.require(0 <= q(value['residual_squared']) <= q(params.tolerance)**2
              and q(bounds['radius']) == radius and q(bounds['carrier_radius']) == R
              and q(bounds['composite_geometry_radius']) == 2*abs(kh)*R
              and 0 <= q(bounds['displacement_upper']) <= radius
              and 0 <= q(bounds['contraction_upper']) < 1
              and 0 <= q(bounds['uniform_source_upper']) < R
              and q(bounds['uniform_source_slack']) == R-q(bounds['uniform_source_upper'])
              and q(bounds['selector_gap_lower']) > 0, 'native whole-chart joint admission')
    cert = value['certificate']
    b.require(cert['input_identity'] == before.identity and cert['read_digest'] == value['record_digest']
              and cert['whole_chart'] == whole and cert['precision_bits'] == g.BITS
              and cert['uniform_trajectory_enclosure'] is False and set(cert['errors']) == set(LIMITS)
              and all(0 <= q(v) < q(LIMITS[k]) for k,v in cert['errors'].items())
              and cert['declared_tolerance'] == str(q(params.tolerance)), 'independent certificate binding/budget')
    ej,eh = q(cert['current_residual_upper']),q(cert['geometry_residual_upper'])
    b.require(ej >= 0 and eh >= 0 and q(cert['joint_residual_squared_upper']) == ej*ej+eh*eh
              and ej*ej+eh*eh <= q(params.tolerance)**2, 'independent joint stopping decision')
    with g.ctx.workprec(g.BITS):
        bridge = staged.bridge(whole,p['candidate']['chi_C'],zeta*q(p['candidate']['chi_C']),kh*zeta,ej,eh)
    b.require(cert['joint_root_error'] == bridge, 'full current-defect contraction bridge')
    if numerics:
        b.require(cert == certificate(before,raw), 'independent equations changed')
