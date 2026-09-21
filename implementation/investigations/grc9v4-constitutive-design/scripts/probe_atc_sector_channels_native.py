#!/usr/bin/env python3
"""Read-only G7 readiness: native primitives, not native ATC execution.

Run from the repository root with PYTHONPATH=src and .venv/bin/python.
Prints portable evidence; does not register profiles or change runtime owners.
"""
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import certify_atc_sector_channels as proof
from pygrc.models.grc_v4_candidate_a import (
    A_SITE_POTENTIAL, CandidateADifferentialReference, candidate_a_log_interpolation,
)
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge, VertexScalar

p, I = proof.p, proof.I


def evidence():
    inputs={
        'paired_source': ('1.16','1.16','1.14','1.14','4.4'),
        'paired_target': ('1.14','1.14','1.12','1.12','2.24','2.24'),
        'embedded_source': ('1','1','1','1','2.2','1','1'),
        'embedded_target': ('1','1','1','1','1.1','1.1','1','1'),
    }
    descriptors=[]
    for name,(n,edges,positions) in proof.GRAPHS.items():
        ids=tuple('n'+str(i) for i in range(n))
        graph=GRCV4Graph(ids,tuple(OrientedEdge('e'+str(i),ids[u],ids[v]) for i,(u,v) in enumerate(edges)))
        backend=CandidateADifferentialReference(graph,1,tuple((float(x),) for x in positions),
                                                {edge:1.0 for edge in graph.live_edge_ids},1.0)
        C=tuple(float(c) for c in inputs[name])
        actual=backend.rebuild(VertexScalar(graph,C))
        expected=tuple((float(x),) for x in proof.prior.mv(
            proof.wls_matrix(n,edges,positions),tuple(F(c) for c in C)))
        proof.require(actual==expected,'native WLS exact-input oracle '+name)
        descriptors.append(dict(graph=name,reference_identity=backend.identity,
            C_binary64=[c.hex() for c in C],gradient_binary64=[[x.hex() for x in row] for row in actual],
            exact_binary64_input_rational_oracle_matches=True))
    # Pin the represented tau, instead of relying on platform libm(log(2)).
    # It approximates the theorem's transcendental tau; the primitive oracle
    # is for this exact represented value, not a theorem-to-runtime bridge.
    tau=float.fromhex('0x1.71547652b82fep-3')
    writers=[]
    # The next float above 3/25 is inside the closed mathematical interval;
    # the usual binary64 spelling 0.12 is just below its lower endpoint.
    for dt in (0.125,float.fromhex('0x1.eb851eb851eb9p-4')):
        proof.require(F(3,25)<=F(dt)<=F(1,8),'represented request inside G6 interval')
        old,drive=0.97,0.99
        rho=(-I(F(dt))/I(F(tau))).exp_nonpositive()
        lo,ld=proof.log_nonpositive(I(F(old))),proof.log_nonpositive(I(F(drive)))
        enclosure=(rho*lo+(1-rho)*ld).exp_nonpositive()
        rounded_lo=float(F(enclosure.lo,p.GRID));rounded_hi=float(F(enclosure.hi,p.GRID))
        proof.require(rounded_lo==rounded_hi,'unique binary64 writer oracle rounding')
        actual=candidate_a_log_interpolation((old,),(drive,),dt,tau)[0]
        proof.require(actual==rounded_lo,'native log writer independent interval oracle')
        half=(I(F(old))*I(F(drive))).sqrt()
        half_lo=float(F(half.lo,p.GRID));half_hi=float(F(half.hi,p.GRID))
        proof.require(half_lo==half_hi,'half writer oracle rounding')
        if dt!=0.125:
            proof.require(actual!=half_lo,'changed request must not retain half writer')
        writers.append(dict(dt_binary64=dt.hex(),tau_binary64=tau.hex(),
            old_binary64=old.hex(),drive_binary64=drive.hex(),result_binary64=actual.hex(),
            exact_input_oracle=enclosure,oracle_matches=True,
            differs_from_half_writer=actual!=half_lo))
    # Source inspection, explicitly not a synthetic native admission run.
    path=p.ROOT/'src/pygrc/models/grc_v4_candidate_a.py'
    tree=ast.parse(path.read_text())
    owner=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CandidateACurrent')
    guard=any(isinstance(n,ast.Compare) and isinstance(n.left,ast.Attribute)
        and n.left.attr=='site_potential_id' and len(n.ops)==1 and isinstance(n.ops[0],ast.NotEq)
        and isinstance(n.comparators[0],ast.Name) and n.comparators[0].id=='A_SITE_POTENTIAL'
        for n in ast.walk(owner))
    proof.require(guard and A_SITE_POTENTIAL=='quadratic_site_potential_zero_derivative_v1',
                  'native potential boundary still explicit')
    return dict(native_descriptor_probes=descriptors,native_writer_probes=writers,
        potential_boundary=dict(method='static AST guard plus exported constant; not executed lifecycle',
            only_declared_id=A_SITE_POTENTIAL,unsupported_research_slope_class=True),
        remaining_G7_obligations=[
            'Independent review and scoped claim/debt adjudication of G5-G6.',
            'Propagate reviewed authority through topology proposal, extension paper and specification.',
            'Admit revision-distinct potential/descriptor/host-transfer/history/request profile and native owners.',
            'Bridge exact-real theorem to represented parameters and all staged numerical error, including share rounding.',
            'Execute native source/target/current/reset, ordinary continuation, rollback, lineage and replay conformance.',
        ])


def main():
    base=p.ROOT/p.INV
    record=dict(schema='grcv4_atc_sector_channels_native_readiness_v1',
        status='primitive_comparisons_pass_native_ATC_not_admitted',
        accepted=False,native_primitives_executed=True,native_ATC_executed=False,
        G7_closed=False,graph_admission=False,ATC2_closed=False,
        evidence=p.encode(evidence()),source_bindings=[])
    for path in (Path(__file__).resolve(),base/'scripts/certify_atc_sector_channels.py',
                 base/'scripts/certify_atc_sector_state_domain.py',
                 base/'scripts/certify_atc_sector_readback_box.py',
                 base/'scripts/certify_atc_sector_readback_point.py',
                 base/'decisions/ATCSectorChannelsAndRequests.md',
                 p.ROOT/'src/pygrc/models/grc_v4_candidate_a.py',
                 p.ROOT/'src/pygrc/models/grc_v4_geometry.py'):
        record['source_bindings'].append(dict(path=str(path.relative_to(p.ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    record['record_digest']=hashlib.sha256(p.canonical(record)).hexdigest()
    print(json.dumps(record,indent=2))


if __name__=='__main__':
    main()
