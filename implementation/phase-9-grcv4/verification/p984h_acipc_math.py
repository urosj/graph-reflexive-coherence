"""Independent large A_CI_PC joint residual, signed reads and local update bounds."""
from dataclasses import replace
from flint import arb
import p984g_acipc as g
import p984b_acipc_runtime as r
from p9_ccipc_capture import portable

b,q,a,lo,hi=g.b,g.q,g.a,g.lo,g.hi
SELF=b.HERE+'p984h_acipc_math.py'
LIMITS=dict(baseline=2**-40,drive=2**-44,readback=2**-40,flat=2**-36,source=2**-60)
UPDATE_LIMITS=dict(resource=2**-40,history=2**-40,carrier=2**-40)


def subject(before):
    ref=before.geometry.reference
    b.require(all(x==0 for row in ref.K4_base for x in row)
              and set(ref.edge_weights.values())=={1},'unit reference required')
    return dict(graph=ref.graph.port_graph.to_envelope(),profile=ref.profile.to_payload(),
        roles={role:b.authority_payload(getattr(before,role)) for role in g.ROLES})


def equations(before,value):
    operand=subject(before);md=g.model(operand,'current');bounds=g.local_bounds(operand,'current')
    h=g.staged.matrix(value['H']);out=g.analytic(md,h,value['J'])
    ej=g.staged.norm(out['fj']);eh=g.staged.norm(h-out['generated'])
    b.require(ej*ej+eh*eh<=q(before.geometry.reference.profile.params_resolved.realization.tolerance)**2,
              'independent full joint stopping failure')
    bridge=g.staged.bridge(bounds,md['p'],md['params']['geometry']['kappa_H'],ej,eh)
    drive=g.pc.floored_drive(md['p'],md['ends'],list(map(a,md['c'])),
        [[a(x) for x in row] for row in md['desc']],out['baseline'])
    flux=[a(md['p']['chi_A'])*(a(w)-d)/(a(w)+d)*a(j)
          for w,d,j in zip(md['w'],drive,value['J'],strict=True)]
    exact=dict(baseline=out['baseline'],drive=drive,readback=flux,
               flat=[out['flat'][i,0] for i in range(len(md['w']))])
    errors={key:max(hi(abs(a(x)-y)) for x,y in zip(value['W_hat_A' if key=='drive' else key],xs,strict=True))
            for key,xs in exact.items()}
    errors['source']=max(hi(abs(a(x)-out['source'][i,j])) for i,row in enumerate(value['source']) for j,x in enumerate(row))
    b.require(all(0<=v<q(LIMITS[k]) for k,v in errors.items()),'signed formula error budget')
    return md,bounds,out,bridge,dict(input_identity=before.identity,read_digest=value['record_digest'],
        precision_bits=g.BITS,local_bounds=bounds,errors={k:str(v) for k,v in errors.items()},
        current_residual_upper=str(ej),geometry_residual_upper=str(eh),joint_residual_squared_upper=str(ej*ej+eh*eh),
        joint_root_error=bridge,uniform_trajectory_enclosure=False)


def certificate(before,value):
    with g.ctx.workprec(g.BITS):return equations(before,value)[-1]


def capture_read(root):
    value=portable(r.capture_root(root))
    value['certificate']=certificate(root.inputs,value)
    check_read(root.inputs,value)
    return value


def check_read(before,value,*,numerics=False):
    from pygrc.models.grc_v4_geometry import PhysicalFlux
    raw={k:v for k,v in value.items() if k!='certificate'};b.check_digest(raw)
    ref=before.geometry.reference;real=ref.profile.params_resolved.realization
    b.require(before.geometry==ref.geometry() and before.stage=='pre_read','fresh reference start')
    recipe=dict(schema_version='grcv4-ci-root-recipe-v1',numerics=r.RECIPE,
        inputs=before.to_payload(),differential_reference=r.backend(before).to_payload())
    b.require(value['input_identity']==before.identity and value['domain_id']==real.contraction_domain_id
        and value['recipe']==r.RECIPE and value['identity']=='grcv4-ci-root-sha256:'+b.digest(recipe), 'root input/recipe')
    b.require(type(value['evaluations']) is int and 2<=value['evaluations']<=real.iteration_limit,'confirmed stopping')
    selected=replace(before,geometry=b.GRCV4Geometry(ref,b.OneFormHodge(ref.graph,tuple(map(tuple,value['H'])))),
        stage='cipc_trial',evaluation_index=value['evaluations']-1,trial_current=PhysicalFlux(ref.graph,tuple(value['J'])))
    b.require(selected.identity==value['selected_inputs_identity'] and value['read_current']==value['J']
        and value['read_source']==value['point_identity'],'whole selected root binding')
    p=ref.profile.params_resolved.candidate
    causal=[float(q(p.chi_A)*(q(w)-q(d))/(q(w)+q(d))*q(j)) for w,d,j in
        zip(before.current.W_A,value['W_hat_A'],value['J'],strict=True)]
    b.require(causal==value['readback'],'signed Read-Back operands')
    md=g.model(subject(before),'current');image,source=g.image(md,value['flat'],represented=True)
    b.require([[g.staged.unique(image[i,j]) for j in range(image.ncols())] for i in range(image.nrows())]==value['generated']
        and [[g.staged.unique(source[i,j]) for j in range(source.ncols())] for i in range(source.nrows())]==value['source'],
        'fixed old Z plus same selected instantaneous source')
    native=value['bounds'];radius=q(float.fromhex(real.contraction_domain_id.split(':')[1]));R=q(real.radius)
    b.require(q(native['radius'])==radius and q(native['carrier_radius'])==R
        and q(native['composite_geometry_radius'])==2*abs(q(ref.profile.params_resolved.geometry.kappa_H))*R
        and 0<=q(native['displacement_upper'])<=radius and 0<=q(native['contraction_upper'])<1
        and 0<=q(native['uniform_source_upper'])<R and q(native['uniform_source_slack'])==R-q(native['uniform_source_upper'])
        and 0<=q(value['residual_squared'])<=q(real.tolerance)**2,'native domain/stopping bounds')
    cert=value['certificate'];bounds=cert['local_bounds']
    b.require(cert['input_identity']==before.identity and cert['read_digest']==value['record_digest']
        and cert['precision_bits']==g.BITS and not cert['uniform_trajectory_enclosure']
        and set(cert['errors'])==set(LIMITS) and all(0<=q(x)<q(LIMITS[k]) for k,x in cert['errors'].items()),'certificate binding')
    ej,eh=q(cert['current_residual_upper']),q(cert['geometry_residual_upper'])
    b.require(ej>=0 and eh>=0 and q(cert['joint_residual_squared_upper'])==ej*ej+eh*eh<=q(real.tolerance)**2,
        'independent residual budget')
    with g.ctx.workprec(g.BITS):
        b.require(bounds==g.local_bounds(subject(before),'current'),'local conditional domain')
        b.require(cert['joint_root_error']==g.staged.bridge(bounds,md['p'],md['params']['geometry']['kappa_H'],ej,eh),
            'full current-defect/root bridge')
    if numerics:b.require(cert==certificate(before,raw),'independent equations drift')


def output_certificate(before,value,after):
    """Exact nonlinear update at each saved input; no global trajectory tube."""
    with g.ctx.workprec(g.BITS):
        md,bounds,out,bridge,_=equations(before,value)
        dj=q(bridge['current_error_upper']);dh=q(bridge['geometry_error_upper'])
        J=[g.staged.feasible.inflate(a(x),dj) for x in value['J']]
        C=[a(c)-a(before.dt)*sum((int(x)*j for x,j in zip(row,J)),arb(0)) for c,row in zip(md['c'],md['bv'])]
        desc=g.staged.feasible.descriptors(subject(before),C,list(map(a,md['w'])))
        drive=g.pc.floored_drive(md['p'],md['ends'],C,desc,J)
        W=g.staged.feasible.log_writer(list(map(a,md['w'])),drive,q(before.dt),q(md['p']['tau_A']))
        df=q(bridge['flat_defect_upper'])+q(bounds['flat_lipschitz_upper'])*dh
        ds=abs(q(md['p']['zeta_A']))*(2*q(bounds['flat_upper'])+df)*df
        decay=(-a(before.dt)/a(md['params']['realization']['tau_PC'])).exp()
        Z=[decay*a(md['z'][i][j])+(1-decay)*g.staged.feasible.inflate(out['source'][i,j],ds)
            for i in range(len(md['w'])) for j in range(len(md['w']))]
        errors={key:str(max(hi(abs(a(x)-y)) for x,y in zip(actual,ideal,strict=True)))
            for key,actual,ideal in (('resource',after.current.C,C),('history',after.current.W_A,W),('carrier',after.current.Z_4,Z))}
        b.require(all(0<=q(x)<q(UPDATE_LIMITS[k]) for k,x in errors.items()),'full update error budget')
        b.require(min(lo(x) for x in C)>=0,'exact-root resource positivity unresolved')
    return dict(before_identity=before.identity,after_identity=after.identity,read_digest=value['record_digest'],
        errors=errors,resource_lower=str(min(lo(x) for x in C)),
        W_lower=str(min(lo(x) for x in W)),W_upper=str(max(hi(x) for x in W)),
        pointwise_at_saved_input=True,uniform_trajectory_enclosure=False)
