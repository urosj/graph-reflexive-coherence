"""Independent document/record and equation checks for P9-5.4.

This does NOT load pygrc, run verify_p954_claims.py, re-query the forensic API,
or establish runtime/lifecycle/formation conformance. Decimal is an independent
high-precision check of the reported equations at exact binary64 inputs.
Run beside the two supplied P9-5.4 documents, or pass their directory with --input.
"""
from __future__ import annotations
import argparse
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def check(input_dir: Path) -> dict:
    path = input_dir / 'P9-5.4-ExecutionRecord.json'
    review_path = input_dir / 'P9-5.4-Review.md'
    raw = path.read_bytes()
    record = json.loads(raw)
    review = review_path.read_text()
    preimage = {k: v for k, v in record.items() if k != 'record_digest'}
    digest = sha(json.dumps(preimage, sort_keys=True, separators=(',', ':')).encode())
    assert digest == record['record_digest']
    roster = record['runtime_result']['executed_ids']
    assert len(roster) == len(set(roster)) == record['runtime_result']['tests_run'] == 13
    assert len(record['claim_separation']) == 12
    assert len(record['source_review']['contracts']) == 7
    assert len({x['contract_id'] for x in record['source_review']['contracts']}) == 7
    assert all(x['support_disposition'] == 'indeterminate_requires_review'
               for x in record['source_review']['contracts'])
    assert record['accepted_generic_runtime_support'] == []
    assert record['admitted_specialization_support_sets'] == []
    assert record['G2_accepted'] is False and record['G3_accepted'] is False
    follow = record['verification_script_followup']
    verifier_path = 'implementation/phase-9-grcv4/verification/verify_p954_claims.py'
    assert record['source_bindings'][verifier_path] == follow['current_script_sha256']
    assert follow['executed_script_sha256'] != follow['current_script_sha256']
    # Do not claim the patch is reproducible without the actual script bytes.

    ctx = Context(prec=180, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
                  capitals=1, clamp=0, flags=[], traps=[])
    with localcontext(ctx):
        gamma = -2.0 * math.log(2.0)
        def conductance(j: float) -> float:
            e = -Fraction(gamma) * Fraction(j)**2 / 2
            # Declared arithmetic rounds the exponent before exp.
            e64 = float(e)
            return float(Decimal.from_float(e64).exp())

        # 1: partial initializer construction succeeds but reset regularity fails.
        w_current, w_reset = conductance(0.0), conductance(1.0)
        assert (w_current, w_reset) == (1.0, 2.0)
        qc = (Fraction(w_current) - 1) / (Fraction(w_current) + 1)
        qr = (Fraction(w_reset) - 1) / (Fraction(w_reset) + 1)
        assert 1 - 3 * qc == 1
        assert 1 - 3 * qr == 0
        probe1 = dict(initialized_current_W=w_current, initialized_reset_W=w_reset,
                      current_denominator=str(1 - 3 * qc),
                      reset_denominator=str(1 - 3 * qr),
                      interpretation='Positive constructor outputs do not imply regular current/reset admission; supplied initializer currents are not authenticated.')

        # 2: use exact binary64 dt, rather than pretend it equals real ln(2).
        dt = math.log(2.0)
        decay = (-Decimal.from_float(dt)).exp()
        w_next_real_recipe = (Decimal(4).ln() * decay).exp()
        w_next = float(w_next_real_recipe)
        assert w_next == 2.0
        assert conductance(1.0) == conductance(-1.0) == w_next
        assert decay != Decimal('0.5')
        half_ulp = Decimal.from_float(math.ulp(2.0)) / 2
        assert abs(w_next_real_recipe - 2) < half_ulp
        probe2 = dict(old_W=4.0, drive_W=1.0, selected_current=0.0, chi=0.0,
                      dt=dt, decay_at_binary64_dt=str(decay),
                      high_precision_written_W=str(w_next_real_recipe), rounded_written_W=w_next,
                      initialized_W_for_plus_one=conductance(1.0),
                      initialized_W_for_minus_one=conductance(-1.0),
                      interpretation='Equal C/W coordinate projections from different constructions do not establish equal provenance; no live commit is tested.')

        # 3: default one-edge kc=.5, eta=.25, W=2 -> J0=-(Cu-Cv).
        def fixed_stage(C: tuple[float, float]) -> dict:
            difference = Fraction(C[0]) - Fraction(C[1])
            phi = Fraction(1, 2) * 2 * difference
            j0 = -Fraction(1, 4) * 2 * (2 * phi)
            hat = conductance(float(j0))
            q = (Fraction(2) - Fraction(hat)) / (Fraction(2) + Fraction(hat))
            return dict(C=list(C), Q=float(sum(map(Fraction, C))), W=2.0,
                        J0=float(j0), W_hat=hat, q=str(q))
        first, second = fixed_stage((1.0, 1.0)), fixed_stage((2.0, 1.0))
        assert (first['q'], second['q']) == ('1/3', '0')
        assert first['W'] == second['W']
        matched = fixed_stage((1.5, 1.5))
        assert matched['Q'] == second['Q'] == 3.0
        assert matched['q'] == '1/3'
        probe3 = dict(submitted_algebraic_pair=[first, second],
                      additional_same_charge_algebraic_pair=[matched, second],
                      interpretation='Only fixed-state algebraic comparisons, not an executed C transition or native release.')

        # Review's absolute-value typo is invisible for J=0,+1,-1.
        law_probe = []
        for j in (0.0, 1.0, -1.0, 0.5, -0.5, 2.0, -2.0):
            squared = conductance(j)
            wrong_e = float(-Fraction(gamma) * abs(Fraction(j)) / 2)
            absolute = float(Decimal.from_float(wrong_e).exp())
            if abs(j) in (0.0, 1.0):
                assert squared == absolute
            else:
                assert squared != absolute
            law_probe.append(dict(J=j, squared_law=squared, absolute_value_substitution=absolute))
        assert 'abs(J_ref)/2' in review

    return {
        'schema': 'p954_independent_document_equation_checks_v1',
        'scope': 'Document/manifest consistency and independent algebra only; zero production runtime executions.',
        'inputs_sha256': {path.name: sha(raw), review_path.name: sha(review_path.read_bytes())},
        'verified_record_digest': digest,
        'record_hash_convention': 'SHA256 of UTF-8 json.dumps(record without record_digest, sort_keys=True, separators=(comma,colon)); identity consistency, not a signature.',
        'record_inventory': {'source_bindings': len(record['source_bindings']), 'unique_method_ids': len(roster),
                             'claim_separation_entries': len(record['claim_separation']),
                             'source_contracts': len(record['source_review']['contracts']),
                             'reported_preserved_predecessor_bindings': record['integration_validation']['preserved_predecessor_source_bindings']},
        'probe_1': probe1, 'probe_2': probe2, 'probe_3': probe3,
        'squared_vs_absolute_current_probe': law_probe,
        'review_correction': 'Replace abs(J_ref)/2 by J_ref**2/2, or state that the exponent contribution is -gamma*J_ref**2/2.',
        'not_independently_verified': [
            'Production verifier and its 13-test execution',
            '162-file accepted-predecessor preservation check',
            'The seven forensic query trace re-executions',
            'Executed/current verifier patch and body equivalence',
            'Browser component and API/notebook permission checks',
            'Pinned September 9 paper/specification bytes',
        ],
        'historical_source_note': 'Earlier uploaded A source is not substituted for the corrected P9-5.3 dependency named in P9-5.4.'
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path(__file__).parent)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('P9-5.4-AuditChecks.json'))
    args = parser.parse_args()
    result = check(args.input)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'status': 'passed', 'scope': result['scope'],
                      'record_inventory': result['record_inventory'],
                      'review_correction': result['review_correction']}, indent=2))

if __name__ == '__main__':
    main()
