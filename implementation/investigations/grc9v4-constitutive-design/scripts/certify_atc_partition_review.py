#!/usr/bin/env python3
"""Exact review amendments; retain the original partition checker/certificate.

Correct the finite-roster label and add fixed-step, same-source and bridge
scope pressure. Four exact Euler images, no trajectory/native campaign.
"""
from fractions import Fraction as F
import importlib.util
import json
from math import comb
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def run():
    prior_path = REFS / 'ATCPartitionStabilityCertificate.json'
    prior = json.loads(prior_path.read_text())
    assert prior['record_digest'] == '53ca458e9411e45e5e2931d563edca2638590a3ef864735758603619994290ec'
    assert sha(canonical({k: v for k, v in prior.items() if k != 'record_digest'})) == prior['record_digest']
    for binding in prior['source_bindings']:
        assert sha((ROOT / binding['path']).read_bytes()) == binding['sha256']
    helper_path = INV / 'scripts/certify_atc_partition_stability.py'
    spec = importlib.util.spec_from_file_location('partition_review_base', helper_path)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    assert base.run() == prior

    roster = prior['finite_checks']
    classes = sum(d//2 for d in range(2, 9))
    literal_partitions = sum(2**(d-1)-1 for d in range(2, 9))
    assert classes == roster['unordered_partitions'] == len(roster['rows']) == 16
    assert literal_partitions == 247
    assert comb(4, 2)//2 == 3
    a, h, epsilon = F(19, 4), F(1, 8), F(1, 64)
    p = lambda c: a*c

    def image(L, C):
        f = base.field(L, C, p)
        return tuple(c+h*v for c, v in zip(C, f, strict=True))

    def displacement(C):
        mean = sum(C)/len(C)
        return tuple(c-mean for c in C)

    def norm2(vector):
        return sum((v*v for v in vector), F())

    source_L = base.laplacian(5, [(i, 4) for i in range(4)])
    mode_rows = []
    for name, L, C, eigenvalue, multiplier in (
        ('source_s3', source_L, (F(1),)*4+(F(3),), F(5), F(37, 32)),
        ('target_2_2_s3', base.double_star(2, 2), (F(1),)*4+(F(3, 2),)*2, F(3), F(11, 32)),
    ):
        z = displacement(C)
        assert base.mv(L, z) == tuple(eigenvalue*v for v in z)
        after = image(L, C)
        assert displacement(after) == tuple(multiplier*v for v in z)
        assert sum(after) == sum(C)
        assert multiplier == 1-h*eigenvalue*(a-eigenvalue)
        mode_rows.append(dict(label=name, C=list(map(str, C)), equilibrium=str(sum(C)/len(C)),
            centered_mode=list(map(str, z)), eigenvalue=str(eigenvalue),
            multiplier=str(multiplier), exact_euler_image=list(map(str, after))))

    same_source = (F(1),)*4+(F(5),)
    assert base.field(source_L, same_source, p) == (F(-1),)*4+(F(4),)
    comparisons = []
    for m, n, wanted_d0, wanted_d1, wanted_ratio, wanted_q in (
        (2, 2, F(3), F(363, 1024), F(121, 1024), (F(7, 24), F(7, 24))),
        (1, 3, F(49, 8), F(66211, 8192), F(66211, 50176), (F(15, 32), F(-3, 16))),
    ):
        L = base.double_star(m, n)
        C = (F(1),)*4+(F(5*m, 4), F(5*n, 4))
        after = image(L, C)
        d0, d1 = norm2(displacement(C)), norm2(displacement(after))
        assert (d0, d1, d1/d0) == (wanted_d0, wanted_d1, wanted_ratio)
        assert sum(C) == sum(after) == sum(same_source) == 9
        assert min(C) > 0 and min(after) > 0
        funding = min(C[-2:])-1
        assert funding > 0
        before_field = base.field(L, C, p)
        responses = []
        for i in (4, 5):
            w = tuple(-L[j][i] for j in range(6))
            loaded = tuple(c+epsilon*v for c, v in zip(C, w, strict=True))
            assert min(loaded) > 0 and sum(loaded) == sum(C)
            response = h/(L[i][i]*epsilon)*(base.field(L, loaded, p)[i]-before_field[i])
            responses.append(response)
        assert tuple(responses) == wanted_q
        comparisons.append(dict(m=m, n=n, target_C=list(map(str, C)),
            target_field=list(map(str, before_field)), exact_euler_image=list(map(str, after)),
            funding_margin=str(funding), equilibrium='3/2',
            distance_squared_before=str(d0), distance_squared_after=str(d1),
            distance_squared_ratio=str(d1/d0), individual_Q=list(map(str, responses))))

    # The same compatible affine slope is not stable at an arbitrary Euler h.
    unstable_h = F(1)
    unstable_multiplier = 1-unstable_h*3*(a-3)
    assert unstable_multiplier == F(-17, 4) and abs(unstable_multiplier) > 1

    # Scope pressure only: old edges stay unit; change only the child bridge
    # in the mathematical weighted Laplacian used in BOTH occurrences of L.
    bridge_rows = []
    for m, n in ((1, 1), (1, 3), (2, 2), (2, 3)):
        d = m+n
        critical = F(m*n*(d+1), d*d)
        for tau in (critical/2, critical, critical*2):
            L = base.double_star(m, n)
            for i in (d, d+1):
                L[i][i] += tau-1
            L[d][d+1] -= tau-1
            L[d+1][d] -= tau-1
            S = [[n+1-tau-F(m, d), tau], [tau, m+1-tau-F(n, d)]]
            det_s = base.determinant(S)
            formula = F(d+1, d*d)*(m*n*(d+1)-tau*d*d)
            assert det_s == formula
            assert base.determinant(base.shifted(L, F(d+1))) == d**d*det_s
            if tau < critical:
                assert S[0][0] > 0 and det_s > 0
            elif tau == critical:
                assert det_s == 0 and S[0][0] > 0
            else:
                assert det_s < 0
            bridge_rows.append(dict(m=m, n=n, tau=str(tau), critical_tau=str(critical),
                schur_determinant=str(det_s), within_unit_bridge_theorem=False))
    assert F(1*3*5, 4**2) == F(15, 16)
    assert F(2*2*5, 4**2) == F(5, 4)

    paths = [Path(__file__).resolve(), helper_path, prior_path]
    record = dict(schema='grcv4_atc_partition_review_certificate_v1',
        status='passed_exact_review_corrections_and_pressure',
        scientific_status='mathematical_review_pass_not_formally_admitted',
        scope=prior['scope'],
        reviewed_predecessor=dict(path=prior_path.relative_to(ROOT).as_posix(),
            record_digest=prior['record_digest'], original_reproduced_unchanged=True,
            legacy_label='unordered_partitions means partition-size/isomorphism classes, not literal labeled partitions'),
        review_dispositions=dict(partition_curvature_window='PASS', nonlinear_continuation='PASS',
            affine_funded_return_witness='PASS', funded_instability_control='PASS',
            source='user-supplied independent mathematical review; exact amendments checked here'),
        finite_checks=dict(unordered_partition_size_classes=classes, degrees=[2, 8],
            characteristic_determinant_evaluations=roster['characteristic_determinant_evaluations'],
            labeled_partitions_represented_by_symmetry=literal_partitions,
            labeled_partitions_enumerated=False, class_rows_in_predecessor=True,
            symmetry_basis='fully symmetric unit-weight source; same sizes related by a leaf permutation and possible child exchange'),
        stability_qualification=dict(window='kappa*lambda_max(L_target)<a<kappa*(d+1)',
            exists_iff='kappa>0 and m>=2 and n>=2, for the unit child bridge',
            window_meaning='source participation and target restorative curvature; existence of a stable positive step',
            fixed_step_requirement='0<h*eta*lambda*(a-kappa*lambda)<2 for every nonzero target mode',
            large_step_negative_control=dict(h=str(unstable_h), eigenvalue='3', multiplier=str(unstable_multiplier))),
        actual_state_mode_switch=mode_rows,
        same_source_comparison=dict(source_C=list(map(str, same_source)), source_inward_current='1',
            a=str(a), kappa='1', eta='1', h=str(h), epsilon=str(epsilon), targets=comparisons,
            meaning='same-source supplied-map one-step contrast; not a long-run positive-resource certificate for s=5 or an autonomous selector'),
        bridge_scope=dict(schur_determinant='(d+1)/d^2*(m*n*(d+1)-tau*d^2)',
            singleton_1_3_threshold='15/16', balanced_2_2_threshold='5/4',
            controls=bridge_rows, weighted_runtime_contract=False,
            meaning='scope qualification only; not a weighted continuation campaign or native feedback channel'),
        unresolved_symmetry=dict(labeled_2_2_partitions=3, id_tiebreak_authorized=False),
        counts=dict(exact_euler_images=4, trajectory_campaigns=0, native_steps=0, topology_events=0),
        production_changes=False,
        source_bindings=[dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path.read_bytes()))
                         for path in paths])
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))
