#!/usr/bin/env python3
"""Local reduced-equation support and causal experiment; stdout-only evidence.

No production backend, GRC receipts, schema release, native execution or gate
promotion. Fixed binding, F2, inputs, checkpoint ages and predictions are reused.
"""
from dataclasses import replace
from fractions import Fraction as F
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'
sys.path.insert(0, str(INV / 'research'))
import atc_support as model
from test_atc_support import COEFFICIENTS, SupportTests, oracle


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checked_record(name, expected):
    record = json.loads((REFS/name).read_text())
    assert record['record_digest'] == expected == model.digest(
        {k: v for k, v in record.items() if k != 'record_digest'})
    for item in record['source_bindings']:
        assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
    return record


def energy(state):
    c = tuple(map(F, state.C))
    potential = sum((a*x**(i+1)/(i+1) for x in c for i, a in enumerate(COEFFICIENTS)), F())
    index = {v: i for i, v in enumerate(state.graph.live_node_ids)}
    coupling = sum(((c[index[e.tail_node_id]]-c[index[e.head_node_id]])**2
                    for e in state.graph.oriented_edges), F())
    return potential - F(1, 2048)*coupling


def project(vector):
    return (vector[0], vector[2]+vector[3], vector[1])


def difference(a, b):
    return tuple(x-y for x, y in zip(a, b, strict=True))


def str_vector(v):
    return list(map(str, v))


def run():
    predictions = checked_record('ATCSupportCausalPredictions.json',
        '8df7fec0ffeacd9e69182e29f26b1f2bb38c6f89a194651d69c6c6e310d0c360')
    certificate = checked_record('ATCSupportFixtureCertificate.json',
        'f0414b6fa38dbe9c57e265530d96580f12d1f58b9bdb927ee06c8e1f167d4d37')
    stream = io.StringIO()
    tests = unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromTestCase(SupportTests))
    assert tests.wasSuccessful(), stream.getvalue()
    f2_path = INV / 'scripts/probe_atc_source_fission.py'
    rule = load(f2_path, 'local_support_unchanged_f2')
    counts = dict(checked_research_updates=0, independent_read_checks=0)
    max_charge_error = F()

    def read(state):
        point = model.read(state.graph, state.C)
        assert (point.Phi, point.J, point.f) == oracle(state.graph, state.C)
        counts['independent_read_checks'] += 1
        return point

    def advance(state):
        nonlocal max_charge_error
        _, _, expected_f = oracle(state.graph, state.C)
        expected_C = tuple(float(F(c)+F(1,64)*f) for c, f in zip(state.C, expected_f, strict=True))
        result = model.advance(state)
        assert result.C == expected_C and result.reset_C == state.reset_C
        counts['checked_research_updates'] += 1
        error = abs(sum(map(F, result.C), F())-5)
        max_charge_error = max(max_charge_error, error)
        assert error <= model.CHARGE_TOLERANCE
        read(result)
        return result

    def trajectory(state, n):
        states = [state]
        read(state)
        for _ in range(n):
            states.append(advance(states[-1]))
        return states

    def compact(states):
        return dict(resources=[s.C for s in states],
            initial_read=model.read(states[0].graph, states[0].C).to_payload(),
            final_read=model.read(states[-1].graph, states[-1].C).to_payload(),
            energy=[float(energy(s)) for s in states])

    def fresh(state):
        # Fresh scientific construction, not stripping a snapshot or GRC receipt.
        g = model.Graph(tuple(v for v in state.graph.live_node_ids),
            tuple(model.Edge(e.edge_id, e.tail_node_id, e.head_node_id) for e in state.graph.oriented_edges))
        return model.admit(model.State(g, tuple(c for c in state.C), tuple(c for c in state.reset_C)))

    eps = F(1,4096)
    source = model.admit(model.State(model.SOURCE_GRAPH, (1.,3.,1.),
                                    (1.+float(eps),3.-2*float(eps),1.+float(eps))))
    selected = rule.source_prescription(source.graph, source.C, read(source).J)
    assert selected['outcome'] == 'resolved'
    target, initializations = model.fixed_fission(source, selected['prescription'])
    direct = fresh(target)
    assert direct is not target and direct.graph is not target.graph
    assert direct.scientific_payload() == target.scientific_payload()
    # Public initializer evidence for all roles and both scientific graphs.
    initializer_checks = []
    for label, state in (('source',source), ('fission_target',target), ('direct_target',direct)):
        for role, C in (('current',state.C), ('reset',state.reset_C)):
            result = model.initialize(state.graph,C,role)
            model.check_initialization(result,state.graph,C,role)
            phi,j,_ = oracle(state.graph,C)
            assert result['payload']['derived']['Phi_base'] == phi
            assert result['payload']['derived']['J_ref'] == j
            initializer_checks.append(dict(branch=label,construction=result))

    # Initial intervention/no-event controls reproduce the unchanged six-state preregistration.
    fm, fp = read(source).f, read(target).f
    delta = difference(project(fp),fm)
    assert delta == tuple(map(F,predictions['baseline']['delta_baseline']))
    assert project(tuple(map(F,target.C))) == tuple(map(F,source.C))
    directions = ((1,0,-2,1),(0,1,1,-2))
    causal = []
    for index,direction in enumerate(directions):
        source_loaded = model.encounter(source,project(direction))
        target_loaded = model.encounter(target,direction)
        direct_loaded = model.encounter(direct,direction)
        ds = difference(read(source_loaded).f,fm)
        dt = difference(read(target_loaded).f,fp)
        assert read(direct_loaded) == read(target_loaded)
        dp = difference(project(dt),ds)
        expected = predictions['encounters'][index]
        assert dp == tuple(map(F,expected['delta_pair']))
        qs,qp,qi = model.DT/eps*ds[1],model.DT/eps*project(dt)[1],model.DT/(2*eps)*dt[index+2]
        assert (qs,qp,qi) == tuple(F(expected[k]) for k in
            ('source_parent_response','target_pair_response','addressed_child_Q'))
        # Check the loaded ordinary update as well, not just the field.
        advance(source_loaded)
        assert advance(target_loaded).scientific_payload() == advance(direct_loaded).scientific_payload()
        causal.append(dict(operation=index,delta_pair=str_vector(dp),
            source_parent_response=str(qs),target_pair_response=str(qp),child_Q=str(qi),
            loaded_F_D_scientific_equality=True))

    # Sixteen-step observation; extend the target baseline to age 31 ONLY to
    # provide matched unencountered controls for 16-update tails at age 15.
    F_states, D_states = trajectory(target,31), trajectory(direct,31)
    N_states = trajectory(source,16)
    assert all(f.scientific_payload() == d.scientific_payload() for f,d in zip(F_states,D_states,strict=True))
    projected_first = difference(project(tuple(map(F,F_states[1].C))),tuple(map(F,N_states[1].C)))
    assert projected_first == tuple(map(F,predictions['baseline']['projected_first_update_difference']))
    for state in (F_states[16],D_states[16],N_states[16]):
        restored = model.reset(state)
        assert restored.C == state.reset_C
        read(restored)

    # A rational bracket is used for diagnostics only, not a rounded infinite-tail claim.
    def equation(t):
        def p(x): return sum((a*x**i for i,a in enumerate(COEFFICIENTS)),F())
        return p(F(3,2)+t)-p(1-t)-F(1,512)*(F(1,2)+2*t)
    lo,hi = F(0),F(1,256)
    for _ in range(100):
        mid = (lo+hi)/2
        if equation(mid) > 0: hi = mid
        else: lo = mid
    t = (lo+hi)/2
    equilibrium = (1-t,1-t,F(3,2)+t,F(3,2)+t)

    def distance2(state):
        return sum(((F(c)-x)**2 for c,x in zip(state.C,equilibrium,strict=True)),F())

    def in_box(state):
        return all(F(31,32)<=F(c)<=F(33,32) for c in state.C[:2]) and all(
            F(47,32)<=F(c)<=F(49,32) for c in state.C[2:])

    cases = [('child_0',directions[0],0),('child_1',directions[1],1)]
    for a,b in ((-1,-1),(-1,1),(1,-1),(1,1)):
        cases.append((f'joint_{a}_{b}',tuple(a*x+b*y for x,y in zip(*directions,strict=True)),None))
    encounters = []
    for age in (0,8,15):
        baseline = F_states[age]
        for label,direction,child in cases:
            loaded = model.encounter(baseline,direction)
            prepared = model.encounter(D_states[age],direction)
            # Each branch receives ONE load from its unencountered checkpoint.
            chain,control = trajectory(loaded,16),trajectory(prepared,16)
            assert all(x.scientific_payload()==y.scientific_payload() for x,y in zip(chain,control,strict=True))
            energies = [energy(s) for s in chain]
            assert all(in_box(s) for s in chain)
            assert all(b <= a for a,b in zip(energies,energies[1:]))
            response = None
            if child is not None:
                delta_f = difference(read(loaded).f,read(baseline).f)
                response = model.DT/(2*eps)*delta_f[child+2]
                assert response >= F(certificate['encounter']['positive_individual_response_lower'])-F(1,2**39)
            end = chain[-1]
            encounters.append(dict(age=age,label=label,direction=direction,
                child_response=None if response is None else str(response),
                trajectory=compact(chain),F_D_equal=True,
                D_scientific_trajectory_digest=model.digest([s.scientific_payload() for s in control]),
                baseline_tail_resources=[s.C for s in F_states[age:age+17]],
                distance_squared_initial=float(distance2(loaded)),distance_squared_final=float(distance2(end)),
                energy_decreases=True,inside_box=True,reset_restores_baseline=model.reset(end).C==target.reset_C))

    # Equal-charge neutral preparation is only a sign control, not a causal no-event history.
    neutral = model.admit(model.State(model.TARGET_GRAPH,(1.25,)*4,target.reset_C))
    neutral_responses=[]
    for i,d in enumerate(directions):
        loaded=model.encounter(neutral,d)
        q=model.DT/(2*eps)*difference(read(loaded).f,read(neutral).f)[i+2]
        assert q < 0
        advance(loaded)
        neutral_responses.append(str(q))

    paths = [Path(__file__).resolve(),INV/'research/atc_support.py',INV/'research/test_atc_support.py',
             f2_path,REFS/'ATCSupportPotentialBinding.json',REFS/'ATCSupportFixtureCertificate.json',
             REFS/'ATCSupportCausalPredictions.json']
    record = dict(schema='grcv4_atc_local_support_experiment_v1',status='passed_local_research_checks',
        interpretation='investigation-only reduced equations; not substrate/native lifecycle validation',
        python=platform.python_version(),binding_id=model.BINDING_ID,
        predecessor_predictions_digest=predictions['record_digest'],
        research_execution_authorized=True,scientific_acceptance=False,
        tests=dict(run=tests.testsRun,failures=len(tests.failures),errors=len(tests.errors)),counts=counts,
        numerical_boundary=dict(resource_update='RN64(C + (1/64)*f_from_stage_rounded_J)',
            charge_target='5',charge_absolute_tolerance=str(model.CHARGE_TOLERANCE),
            maximum_observed_charge_error=str(max_charge_error),repair=False,
            scope='finite rounded research execution; exact return theorem is a separate result'),
        fission=dict(source=source.scientific_payload(),unchanged_F2=selected,
            target=target.scientific_payload(),initializations=initializations,
            kind='fixed local conservative map, not a production event or automatic invocation'),
        initializers=initializer_checks,
        causal=dict(delta_baseline=str_vector(delta),projected_first_update_difference=str_vector(projected_first),
            encounters=causal,F_D_baseline_equal=True,
            F_experimental_origin='fixed_fission_from_source',D_experimental_origin='fresh_direct_preparation',
            N_experimental_origin='same_source_without_fission',
            F_observation=compact(F_states[:17]),D_observation=compact(D_states[:17]),N_observation=compact(N_states),
            target_unencountered_tail_C=[s.C for s in F_states[17:]],
            no_production_publications_or_receipts=True),
        encounter_protocol=dict(ages=[0,8,15],amplitude=str(eps),independent_loads_per_age=6,
            return_observation_updates=16,never_sequential_loads=True,
            equilibrium_t_bracket=[str(lo),str(hi)],cases=encounters),
        neutral_responses=neutral_responses,
        claim_ceiling=['local_numerical_realization_of_proposed_equations',
            'whole_fission_changes_projected_dynamics_and_response_in_this_model',
            'positive_child_channels_and_positive_source_response',
            'finite_loaded_energy_descent_and_box_membership'],
        not_established=['substrate_native_conformance','production_lifecycle_or_replay',
            'automatic_ATC','new_capability_from_absence','two_independent_identities',
            'source_nonviability','infinite_binary64_return','all_ten_domains'],
        production_changes=False,native_admissions=0,native_steps=0,native_events=0,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths])
    record['record_digest']=model.digest(record)
    return record


if __name__=='__main__':
    print(json.dumps(run(),separators=(',',':'),ensure_ascii=True,allow_nan=False))
