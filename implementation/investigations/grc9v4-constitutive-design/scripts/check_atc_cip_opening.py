#!/usr/bin/env python3
"""CIP-0: exact root bounds plus native step-staging audit, stdout only.

--check validates retained identities only. The native fixture is not the
nonlinear paired research witness or an autonomous topology-change engine.
"""
import argparse
from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
INV = Path('implementation/investigations/grc9v4-constitutive-design')
SIDE = ROOT / INV / 'tools/exploratory-side-tool'
RECORD = ROOT / INV / 'evidence/atc-cip/ATCCIP0Certificate.json'
sys.path[:0] = [str(ROOT / 'src'), str(ROOT), str(ROOT / INV / 'research'),
               str(SIDE / 'tool/src'), str(ROOT / INV / 'scripts')]

import numpy as np
import atc_cip_domains as domains
from grcv4_explorer import atc_ci
from grcv4_explorer.canonical import digest, record_digest, file_sha256
from audit_atc_ci_pc_boundary import joint_root_evidence
from pygrc.models import grc_v4_ci as ci, grc_v4_pc as pc
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge, StarAssembly
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ResourceBoundaryError
from tests.models.test_grc_v4_cipc import fixture, independent_root

require = domains.require


def boundary():
    graph = GRCV4Graph(('p', 'u0', 'u1', 'v0', 'v1'), tuple(
        OrientedEdge('e'+str(i), 'p', v) for i, v in enumerate(('u0','u1','v0','v1'))))
    z = tuple(.25 if i == j else 0. for i in range(4) for j in range(4))
    rz = tuple(.5 if i == j else 0. for i in range(4) for j in range(4))
    before, backend = fixture('A', graph=graph, C=(1.5,1.,1.,2.,2.),
        W=(.75,.75,.625,.625), z=z, reset_z=rz, weight_lower=.5, weight_upper=1.,
        changes={'candidate': {'zeta_A': .75}})
    before = replace(before, reset=GRCV4AuthoritativeState(
        (1.25,1.125,1.125,2.,2.), (.7,.7,.6,.6), rz))
    original = before.to_payload()
    Read, Step = ci.CandidateCIRoot, ci.ProvisionalCandidateCIStep
    with patch.object(ci, 'CandidateCIRoot', wraps=Read) as reads, \
         patch.object(ci, 'CandidateAWriter', wraps=ci.CandidateAWriter) as writer, \
         patch.object(pc, 'scalar_zoh', wraps=pc.scalar_zoh) as carrier:
        step = Step(before, backend)
    after, selected = step.next_inputs, step.root.selected
    source = tuple(x for row in selected.structural_source.increment for x in row)
    params = before.geometry.reference.profile.params_resolved
    require(reads.call_count == 3, 'reset/live/restart root roster')
    require([call.args[0].current for call in reads.call_args_list] ==
            [before.reset, before.current, after.current], 'role and old/new Z staging')
    require(reads.call_args_list[-1].args[0].dt == 0, 'restart is a read')
    require(writer.call_count == carrier.call_count == step.carrier_writes == 1, 'one W/Z write')
    require(writer.call_args.args[0] is selected.point, 'W consumes selected point')
    require(carrier.call_args.args == (z, source, before.dt, params.realization.tau_PC),
            'Z writer consumes literal selected structural source and old Z')
    require(step.writer.authority.state.Z_4 == z, 'W writer preserves old Z')
    require(step.resource.continuity_evaluations == 1, 'one continuity update')
    require(after.current.C == step.resource.provisional_state.C, 'committed continuity')
    require(after.current.Z_4 != z and after.reset == before.reset, 'live writes / independent reset')
    require(after.step_index == before.step_index+1 and after.time == before.time+before.dt,
            'one temporal advancement')
    # Gain audit: non-unit zeta distinguishes an accidental duplicate gain.
    raw = StarAssembly(selected.point.read_back(selected.point.current).causal_flat).matrix
    expected = tuple(tuple(float(Fraction(params.candidate.zeta_A)*Fraction(x)) for x in row) for row in raw)
    require(selected.structural_source.increment == expected, 'registered source has one outer zeta')
    h, j, s = independent_root(before, backend)
    np.testing.assert_allclose(selected.inputs.geometry.one_form_hodge.matrix, h, rtol=1e-10, atol=1e-11)
    np.testing.assert_allclose(selected.point.current.values, j, rtol=1e-10, atol=1e-11)
    np.testing.assert_allclose(selected.structural_source.increment, s, rtol=1e-10, atol=1e-12)
    fresh = Read(replace(after, dt=0), backend)
    require(fresh == step.restart, 'entire fresh joint root equals restart')
    joint = joint_root_evidence(fresh)
    require(joint == joint_root_evidence(step.restart), 'canonical selected-root evidence')
    require(step.restart.selected.point.current != selected.point.current, 'fixture separates roots')
    with patch.object(ci, 'CandidateAWriter', side_effect=AssertionError('zero beat wrote W')), \
         patch.object(pc, 'scalar_zoh', side_effect=AssertionError('zero beat wrote Z')):
        zero = Step(replace(after, dt=0), backend)
    require(zero.next_inputs == replace(after, dt=0) and zero.resource.continuity_evaluations == 0,
            'zero duration is not an ordinary beat or event')
    calls = []
    def fail_final(inputs, differential):
        calls.append(inputs)
        if len(calls) == 3:
            raise ci.CIStageError('no_admitted_root', 'injected combined restart rejection')
        return Read(inputs, differential)
    with patch.object(ci, 'CandidateCIRoot', side_effect=fail_final):
        try:
            Step(before, backend)
        except ResourceBoundaryError as exc:
            require((exc.stage, exc.code) == ('final_reconstruction','no_admitted_root'), 'failure stage')
        else:
            raise AssertionError('restart rejection was swallowed')
    require(before.to_payload() == original, 'captured state unchanged by success or failure')
    return dict(before=original, after=after.to_payload(), joint_root=joint,
        source=selected.structural_source.increment, consumed_current=selected.point.current.values,
        poststate_current=fresh.current.values, same_source_writer=True,
        independent_fixed_point_oracle=True, full_joint_restart_equality=True,
        zero_duration_identity=True, final_rejection_preserves_captured_state=True,
        scope='shipped zero-site-derivative fixture; not nonlinear research witness or live ATC owner')


def run():
    context = atc_ci.load_current_forensic_context(ROOT, SIDE)
    traces = [atc_ci.reconstruction_path(context, claim) for claim in
        ('ATC-CI-DOMAIN-02','ATC-CI-REFERENCE-03','ATC-PC-CARRIER-03','ATC-PC-DOMAIN-04')]
    require(all(trace['rows'][0]['payload']['claim_class'] == 'conditional' and
        trace['rows'][0]['payload']['support_disposition'] in ('accepted_bounded_A_CI_research','accepted_bounded_A_PC_research')
        for trace in traces), 'bounded accepted predecessor authority')
    traces = [dict(query=t['query'], graph_digest=t['graph_digest'],
        source_bundle_digest=t['source_bundle_digest'], trace_digest=t['trace_digest'],
        classification=t['rows'][0]['classification'], source_ref=t['rows'][0]['source_ref'],
        claim_class=t['rows'][0]['payload']['claim_class'],
        support_disposition=t['rows'][0]['payload']['support_disposition'],
        profile_scope=t['rows'][0]['payload']['profile_scope'],
        edge_ref_count=len(t['rows'][0]['edge_refs']),
        edge_refs_digest=digest(t['rows'][0]['edge_refs'])) for t in traces]
    debt_routes = []
    for number, stage in (('03','CIP-0/CIP-2'),('05','CIP-0/CIP-2'),('06','CIP-0/CIP-2'),
                          ('07','CIP-1'),('15','CIP-1/CIP-2'),('16','CIP-1/CIP-2'),('24','adjudication')):
        t = atc_ci.debt_lifecycle(context, 'ATC7-DB-'+number)
        row, payload = t['rows'][0], t['rows'][0]['payload']
        require(payload['global_discharged'] is False, 'origin debt remains open')
        debt_routes.append(dict(debt_id=payload['origin_debt_id'], title=payload['title'],
            predecessor_scope='A_CI', predecessor_disposition=row['classification'],
            predecessor_trace_digest=t['trace_digest'], predecessor_source_ref=row['source_ref'],
            edge_ref_count=len(row['edge_refs']), edge_refs_digest=digest(row['edge_refs']),
            CIP_status='pending_not_discharged', successor_stage=stage, global_discharged=False))
    certificate, staging = domains.domain_certificate(), boundary()
    paths = {Path(__file__).resolve(), ROOT/INV/'decisions/ATCCIPCoupledProgram.md',
        ROOT/'specs/grc-v4-spec.md', ROOT/INV/'decisions/ATCCIDomainsAndReference.md',
        ROOT/INV/'evidence/atc-cip/CIP-CoupledProgram-Direction.md',
        ROOT/INV/'evidence/atc-cip/CIP-CompositeDomain-Direction.md'}
    for module in tuple(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path:
            p = Path(path).resolve()
            if p.is_relative_to(ROOT) and p.suffix == '.py' and '.venv' not in p.parts:
                paths.add(p)
    value = domains.ci.anchor.a.encode(dict(schema='grcv4_atc_cip0_v1',
        status='prepared_pending_independent_review', scientific_acceptance=False,
        graph_admitted=False, native_ATC_executed=False, ATC2_closed=False,
        authority_graph_digest=context.graph_digest, authority_traces=traces,
        proof=certificate, native_staging=staging, pending_debt_routes=debt_routes,
        proposed_claims=[dict(claim_id='ATC-CIP-ROOT-00', claim_class='proposed_conditional',
            profile_scope=['A_CI_PC'], debt_refs=['ATC7-DB-'+n for n in ('03','05','06','07','15','16','24')],
            local_debt_discharge=False, graph_admitted=False)],
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=file_sha256(p)) for p in sorted(paths)]))
    value['record_digest'] = record_digest(value, 'record_digest')
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        value = json.loads(RECORD.read_text())
        require(value['record_digest'] == record_digest(value, 'record_digest'), 'record digest')
        for item in value['source_bindings']:
            require(file_sha256(ROOT/item['path']) == item['sha256'], 'source drift: '+item['path'])
        require(atc_ci.load_current_forensic_context(ROOT,SIDE).graph_digest == value['authority_graph_digest'],
                'accepted predecessor graph drift')
        print(json.dumps(dict(status='passed', scope='retained identities only', record_digest=value['record_digest'])))
    else:
        print(json.dumps(run(), indent=2))
