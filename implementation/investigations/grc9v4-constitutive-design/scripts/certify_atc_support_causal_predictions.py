#!/usr/bin/env python3
"""Check a proposed content binding and preregister exact Gate-C predictions.

Research arithmetic only: no native admission, step, event, or acceptance.
The stage-rounded oracle is a prediction for a future implementation, not one.
"""
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'
BINDING_DIGEST = 'grcv4-research-potential-sha256:9f4a7d3c69c1e52a4551029e7085d8123f68215647e63706397b3cd8bfcbfd8d'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def binding_identity(payload):
    return 'grcv4-research-potential-sha256:' + sha(canonical(payload))


def checked_binding(record):
    if (set(record) != {'schema', 'status', 'runtime_installed', 'binding_digest', 'identity_payload'}
            or record['schema'] != 'grcv4_atc_research_potential_binding_record_v1'
            or record['status'] != 'proposed_not_admitted'
            or record['runtime_installed'] is not False
            or record['binding_digest'] != BINDING_DIGEST
            or binding_identity(record['identity_payload']) != BINDING_DIGEST):
        raise ValueError('unbound or altered proposed potential declaration')
    return record['identity_payload']


def site(c, roots):
    """Mathematical fixed-degree polynomial, not a registered native evaluator."""
    result = F(1)
    for root in roots:
        result *= c - root
    return result


def binary64_site(c, roots):
    if type(c) is not float or not math.isfinite(c) or c < 0:
        raise ValueError('expected finite nonnegative binary64 coordinate')
    return site(F(c), roots)


def mv(matrix, vector):
    return tuple(sum((F(x)*y for x, y in zip(row, vector, strict=True)), F())
                 for row in matrix)


def transpose(matrix):
    return tuple(zip(*matrix, strict=True))


def plus(a, b):
    return tuple(x+y for x, y in zip(a, b, strict=True))


def minus(a, b):
    return tuple(x-y for x, y in zip(a, b, strict=True))


def scale(k, a):
    return tuple(k*x for x in a)


def strings(a):
    return list(map(str, a))


def field(B, C, roots, coefficients, eta, kappa):
    """Literal incidence route checked against independent expanded dense L."""
    BT = transpose(B)
    L = tuple(tuple(sum(x*y for x, y in zip(r, s, strict=True)) for s in B) for r in B)
    p = tuple(site(c, roots) for c in C)
    expanded = tuple(sum((a*c**i for i, a in enumerate(coefficients)), F()) for c in C)
    assert p == expanded
    phi = plus(minus(scale(kappa, mv(B, mv(BT, C))), p), (sum(p, F())/len(C),)*len(C))
    J = scale(-eta, mv(BT, phi))
    f = scale(F(-1), mv(B, J))
    independent = scale(-eta, mv(L, minus(expanded, scale(kappa, mv(L, C)))))
    assert f == independent and sum(f) == 0
    # These two fixtures are connected. No generic native gauge owner is installed.
    phi64 = tuple(float(x) for x in phi)
    J64 = tuple(float(x) for x in scale(-eta, mv(BT, tuple(map(F, phi64)))))
    f64_exact = scale(F(-1), mv(B, tuple(map(F, J64))))
    assert all(math.isfinite(x) for x in (*phi64, *J64))
    error = max(map(abs, minus(f64_exact, f)))
    assert error <= F(1, 2**48)
    return dict(C=strings(C), p=strings(p), Phi=strings(phi), J=strings(J), f=strings(f),
                rounded_prediction=dict(Phi=phi64, J=J64, f=strings(f64_exact),
                                        max_tendency_error=str(error)))


def run():
    binding_path = REFS / 'ATCSupportPotentialBinding.json'
    binding = checked_binding(json.loads(binding_path.read_text()))
    certificate_path = REFS / 'ATCSupportFixtureCertificate.json'
    certificate = json.loads(certificate_path.read_text())
    assert certificate['record_digest'] == 'f0414b6fa38dbe9c57e265530d96580f12d1f58b9bdb927ee06c8e1f167d4d37'
    assert certificate['record_digest'] == sha(canonical(
        {k: v for k, v in certificate.items() if k != 'record_digest'}))
    roots = tuple(map(F, binding['polynomial']['roots_in_evaluation_order']))
    coefficients = tuple(map(F, binding['polynomial']['coefficients_ascending']))
    assert list(map(str, coefficients)) == certificate['binding']['site_derivative_coefficients_ascending']
    # Check both redundant polynomial representations independently.
    product = [F(1)]
    for r in roots:
        out = [F()]*(len(product)+1)
        for i, c in enumerate(product):
            out[i] -= r*c
            out[i+1] += c
        product = out
    assert tuple(product) == coefficients

    mutations = []
    changes = (
        ('polynomial', ('polynomial', 'coefficients_ascending'), ['0']*6),
        ('units', ('units_id',), 'other_units'),
        ('domain', ('domain', 'max_vertices'), 17),
        ('rounding', ('evaluation', 'potential_rounding'), 'round each factor first'),
        ('work', ('work_bound', 'site_evaluations_per_current_or_reference_pass_max'), 17),
        ('initializer_evidence', ('initializer_successor', 'conformance_evidence'), 'W only'),
        ('symbolic_id', ('symbolic_id',), 'quadratic_site_potential_zero_derivative_v1'),
    )
    for label, path, replacement in changes:
        for rehash in (False, True):
            altered = json.loads(binding_path.read_text())
            target = altered['identity_payload']
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = replacement
            if rehash:
                altered['binding_digest'] = binding_identity(altered['identity_payload'])
            try:
                checked_binding(altered)
            except ValueError:
                mutations.append(dict(field=label, digest_recomputed=rehash, rejected=True))
            else:
                raise AssertionError('mutation inherited the pinned symbolic binding')

    for value in (-1., float('nan'), float('inf'), -float('inf'), True, 1, '1'):
        try:
            binary64_site(value, roots)
        except ValueError:
            pass
        else:
            raise AssertionError('unbounded or invalid input accepted')
    extremes = (0., -0., float.fromhex('0x0.0000000000001p-1022'), sys.float_info.max)
    for c in extremes:
        assert binary64_site(c, roots) == sum((a*F(c)**i for i, a in enumerate(coefficients)), F())

    Bminus = ((1, 0), (-1, 1), (0, -1))
    Bplus = ((1, 0, 0), (0, -1, 0), (-1, 0, 1), (0, 1, -1))
    P = ((1, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 0))
    Cminus, Cplus = tuple(map(F, (1, 3, 1))), (F(1), F(1), F(3, 2), F(3, 2))
    directions = ((1, 0, -2, 1), (0, 1, 1, -2))
    eta, kappa, h, eps = F(1, 4), F(1, 1024), F(1, 64), F(1, 4096)
    assert mv(P, Cplus) == Cminus
    source = field(Bminus, Cminus, roots, coefficients, eta, kappa)
    target = field(Bplus, Cplus, roots, coefficients, eta, kappa)
    fm, fp = tuple(map(F, source['f'])), tuple(map(F, target['f']))
    assert fm == (F(-3, 2048), F(3, 1024), F(-3, 2048))
    assert fp == (F(-1, 4096), F(-1, 4096), F(1, 4096), F(1, 4096))
    assert mv(P, fp) == scale(F(1, 6), fm)
    baseline_delta = minus(mv(P, fp), fm)
    comparisons = []
    for child, direction in enumerate(directions, 2):
        projected = mv(P, tuple(map(F, direction)))
        loaded_source = field(Bminus, plus(Cminus, scale(eps, projected)), roots, coefficients, eta, kappa)
        loaded_target = field(Bplus, plus(Cplus, scale(eps, direction)), roots, coefficients, eta, kappa)
        ds = minus(tuple(map(F, loaded_source['f'])), fm)
        dt = minus(tuple(map(F, loaded_target['f'])), fp)
        projected_dt = mv(P, dt)
        delta_pair = minus(projected_dt, ds)
        assert ds[1] == F(2300284075180035, 4611686018427387904)
        assert projected_dt[1] == F(3940432218817, 144115188075855872)
        qsource, qpair, qchild = h/eps*ds[1], h/eps*projected_dt[1], h/(2*eps)*dt[child]
        assert qsource > qpair > 0 and qchild >= F(certificate['encounter']['positive_individual_response_lower'])
        assert any(delta_pair) and sum(delta_pair) == 0
        comparisons.append(dict(child_index=child, target_direction=list(direction),
            projected_direction=strings(projected), source_loaded=loaded_source,
            target_loaded=loaded_target, source_increment=strings(ds),
            projected_target_increment=strings(projected_dt), delta_pair=strings(delta_pair),
            source_parent_response=str(qsource), target_pair_response=str(qpair),
            addressed_child_Q=str(qchild), aggregate_response_difference=str(qpair-qsource)))

    # Pure arithmetic identities, not a native direct-preparation lifecycle run.
    fields = [source, target] + [row[k] for row in comparisons for k in ('source_loaded', 'target_loaded')]
    record = dict(schema='grcv4_atc_support_causal_preregistration_v1', status='passed_exact_prediction_checks',
        scientific_status='proposed_equations_only_not_native_causal_execution', python=platform.python_version(),
        potential_binding_digest=BINDING_DIGEST, support_certificate_digest=certificate['record_digest'],
        binding_pressure=dict(rejected_mutations=mutations, invalid_inputs_rejected=7,
            finite_extreme_inputs_checked=4, polynomial_forms_agree=True),
        dt=str(h), epsilon=str(eps), source_incidence=Bminus, target_incidence=Bplus,
        projection=P, source=source, target=target,
        baseline=dict(projected_C=strings(mv(P,Cplus)), projected_f=strings(mv(P,fp)),
            projected_to_source_tendency_ratio='1/6', delta_baseline=strings(baseline_delta),
            projected_first_update_difference=strings(scale(h,baseline_delta))),
        encounters=comparisons,
        future_native_comparison=dict(
            stage_oracle='exact polynomial, exact gauge, RN64 potential, exact flux from rounded potential, RN64 flux',
            stage_Phi_and_J='require equality to independently recomputed stage-rounded predictions',
            mathematical_per_coordinate_tendency_error_bound='1/281474976710656',
            delta_baseline_and_delta_pair_absolute_tolerance='1/35184372088832',
            normalized_response_absolute_tolerance='1/549755813888',
            tolerance_basis='per-field bound 2^-48 gives at most 6 such errors in delta_pair; at most 64 times this in shared normalized response',
            max_prechecked_tendency_rounding_error=str(max(F(x['rounded_prediction']['max_tendency_error']) for x in fields))),
        direct_preparation=dict(prediction='equal scientific evolution on matched complete scientific inputs and requests',
            publication='fresh independently admitted research publication; never strip receipts from an event snapshot',
            excluded_equalities=['receipt_ids','snapshots','complete_authoritative_publication']),
        interpretation=dict(causal_subject='whole fission intervention, not incidence alone',
            expected='state-mediated reorganization/addressability, not response capability from absence',
            source_return_certificate=False, native_F_equals_D_test=False,
            native_causal_gate_closed=False, native_bridge_gate_closed=False),
        native_admissions=0,native_steps=0,native_events=0,production_changes=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes())) for p in
            (Path(__file__).resolve(),binding_path,certificate_path)])
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), separators=(',', ':'), ensure_ascii=True, allow_nan=False))
