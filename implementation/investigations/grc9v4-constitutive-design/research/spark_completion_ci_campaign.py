"""One explicit C_CI source/event/positive-window research history per process."""
from fractions import Fraction as F
from math import floor,ceil
from pathlib import Path
import hashlib,json,lzma,time
from flint import arb,arb_mat,fmpq,ctx
from spark_completion_ci import CCIReference,trap_certificate
from spark_completion_positive import fixture,content_id,norm_upper,compact_box
from spark_completion_continuation import need,geometric_roster,POLICY,infnorm
import spark_completion_basins as basins

ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
PRECISION=8192
HORIZON=1024
TIME_LIMIT=1800
WINDOW=2


def retained(path):
    raw=(ROOT/INV/'evidence/spark-completion'/path).read_bytes()
    return json.loads(lzma.decompress(raw) if path.endswith('.xz') else raw)


def exact_bounds(x,bits=112):
    scale=2**bits
    return [str(F(floor(F(str(x.lower().fmpq()))*scale),scale)),
            str(F(ceil(F(str(x.upper().fmpq()))*scale),scale))]


def scalar_upper(x):
    return exact_bounds(x)[1]


def box_payload(m,C):
    return {node:exact_bounds(C[i,0])for i,node in enumerate(m.nodes)}


def matrix_payload(M):
    return [[exact_bounds(M[i,j])for j in range(M.ncols())]for i in range(M.nrows())]


def root_payload(root):
    return dict(flat=matrix_payload(root['flat']),H=matrix_payload(root['geometry']),
        J=matrix_payload(root['selected']['current']),root_error_upper=scalar_upper(root['error']),
        root_residual_upper=scalar_upper(root['residual'].upper()),proposal_iterations=root['iterations'])


def prepare_source(old,source,targets,role):
    m=CCIReference(source)
    C=m.vector(old['checks']['prepared']['current_prestate'])
    ordinary=m.ci_step(C);post=ordinary['after'];fresh=m.root(post)
    need(all(post[i,0]>0 for i in range(m.n)),'nonpositive source')
    rosters=geometric_roster(source,post,m.nodes)
    need(rosters=={'p':sorted(m.nodes)},'fresh source has no complete parent')
    edges=[(e['tail']['node_id'],e['tail']['port'],e['head']['node_id'],e['head']['port'],F(1))for e in source['edges']]
    bounds={n:tuple(map(F,exact_bounds(post[i,0])))for i,n in enumerate(m.nodes)}
    rows=basins.row_intervals(m.nodes,edges,{n:v[0]for n,v in bounds.items()},{n:v[1]for n,v in bounds.items()})
    gv=[arb(fmpq(str((l+h)/2)),fmpq(str((h-l)/2)))for l,h in rows['v']]
    gradient=16-sum(x*x for x in gv);spark=arb(fmpq(1,8))-min(-x for x in gv)
    need(gradient>0 and spark>0,'actual CI postbeat trigger not eligible')
    ports=[e[end]['port']for e in source['edges']for end in ('tail','head')if e[end]['node_id']=='v']
    need(sorted(ports)==list(range(1,10)),'source not saturated')
    # This rule uses the actual CI poststate. Reset is not advanced and its CI
    # continuation is new evidence, even though its resource input is unchanged.
    reset=m.vector(old['checks']['prepared']['reset_prestate']);reset_root=m.root(reset)
    operand=post if role=='current' else reset
    target=targets['1'];module=target['module']
    values={n:operand[i,0]for i,n in enumerate(m.nodes)if n!='v'}
    values[module[0]]=m.q(0)
    for n,share in zip(module[1:],('1/64','31/32','1/64')):values[n]=operand[m.nodes.index('v'),0]*m.q(fmpq(share))
    t=CCIReference(target['graph']);after=t.matrix([[values[n]]for n in t.nodes])
    need(sum(F(v)for v in old['checks']['prepared']['current_prestate'].values())==21,'prestate charge')
    need(sum(F(v)for v in old['checks']['prepared']['reset_prestate'].values())==21,'reset charge')
    need(all(sum(m.B[i,j]for i in range(m.n))==0 for j in range(m.m)),'source incidence conservation')
    need(sum(F(v)for v in ('1/64','31/32','1/64'))==1,'transfer conservation')
    need(set(geometric_roster(target['graph'],after,t.nodes))=={'p'},'allocation alone counted as gain')
    source_record=dict(initial_prestate_source='SC2SourceBeat.json.xz /checks/prepared/current_prestate',
        actual_CI_poststate=box_payload(m,post),fresh_joint_root=root_payload(fresh),
        reset_state=box_payload(m,reset),reset_joint_root=root_payload(reset_root),
        complete_parent=rosters,gradient_squared_margin=exact_bounds(gradient),spark_margin=exact_bounds(spark),
        root_domain=m.domain,source_steps=1,reset_advanced=False,allocation_shares=['1/64','31/32','1/64'],
        charge='21',charge_argument='exact incidence identity and shares sum one; intervals enclose that exact trajectory')
    return t,after,source_record


def run(role):
    need(role in ('current','reset'),'unknown role')
    start=time.monotonic();source,_,targets=fixture()
    predecessor=retained('SC2SourceBeat.json.xz');old=retained('SC2PositiveCandidate.json.xz')
    with ctx.workprec(512):
        proof,P=trap_certificate({**targets['1'],'charts':targets},old['checks']['trap'])
    with ctx.workprec(PRECISION):
        m,C,source_record=prepare_source(predecessor,source,targets,role)
        center=m.vector(proof['center']);metric=arb_mat(P);radius=m.q(fmpq(proof['radius']))
        rows=[];entry=None;checkpoints={};gain_step=None
        root=m.root(C);initial=box_payload(m,C);checkpoints['event']=dict(C=initial,root=root_payload(root))
        for step in range(1,HORIZON+1):
            need(time.monotonic()-start<TIME_LIMIT,'explicit research time cap reached')
            C=C-m.q(32)*m.B*root['selected']['current']
            need(all(C[i,0]>0 and C[i,0]<4 for i in range(m.n)),'positive declared resource domain failed')
            need(sum(C[i,0]for i in range(m.n)).contains(arb(21)),'charge enclosure excludes exact invariant')
            root=m.root(C)  # reused as next consumed read on this identical C
            discrepancy=root['selected']['causal_flat']-root['flat']
            need(all(discrepancy[i,0].contains(arb(0))for i in range(m.m)),'joint root residual enclosure failed')
            diff=C-center; distance=((diff.transpose()*metric*diff)[0,0]).sqrt().upper()
            observed=compact_box(m,C)  # diagnostic/storage view only; never feeds evolution
            roster={chi:geometric_roster(t['graph'],observed,m.nodes)for chi,t in targets.items()}
            if roster==proof['complete_basins'] and gain_step is None:gain_step=step
            if distance<radius and entry is None:
                need(roster==proof['complete_basins'],'trap entry lacks complete domains');entry=step
                checkpoints['entry']=dict(C=box_payload(m,C),root=root_payload(root))
            if entry is not None:need(distance<radius and roster==proof['complete_basins'],'window left trap')
            rows.append(dict(step=step,C=box_payload(m,C),minimum_resource=exact_bounds(min(C[i,0].lower()for i in range(m.n))),
                trap_distance_upper=scalar_upper(distance),root_error_upper=scalar_upper(root['error']),
                complete_basins=roster))
            if step%100==0 or (entry is not None and step>=entry):
                print(role,step,'seconds',round(time.monotonic()-start,1),'distance',distance.str(7),flush=True)
            if entry is not None and step==entry+WINDOW:
                checkpoints['completion']=dict(C=box_payload(m,C),root=root_payload(root));break
        need(entry is not None and rows[-1]['step']==entry+WINDOW,'no completed research window within horizon')
        decision=dict(role=role,scientific_completion=role=='current',reset_probe_earns_live_gain=False,
            local_gain=1 if role=='current' else 0,stable_descendants=proof['complete_basins'],
            target_completion_step=rows[-1]['step'],window_beats=WINDOW,window_elapsed='64',
            first_certified_entry=entry,first_spatial_gain=gain_step,
            full_state=['C'],native_completion=False,accepted_authority=False)
        return dict(role=role,source=source_record,source_graph=source,targets=targets,
            proof=proof,root_domain=m.domain,initial_target=initial,observations=rows,
            checkpoints=checkpoints,decision=decision,
            arithmetic=dict(precision_bits=PRECISION,root_proposal_limit=16,maximum_target_steps=HORIZON,
                time_limit_seconds=TIME_LIMIT,automatic_fallback=False,
                retained_coordinates='outward 112-bit dyadic enclosures; full recurrence is reproduced from exact inputs',
                midpoint_usage='root proposals only; actual C evolution always uses full outward enclosure'),
            SC3_predecessor_unchanged=True,OS_trajectory_reused=False,native_steps=0)
