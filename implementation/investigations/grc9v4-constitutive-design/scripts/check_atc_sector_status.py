#!/usr/bin/env python3
"""Typed source-status correction over the unchanged reviewed lineage witness.

No target construction or trajectory execution. Physical prescriptions and
outcomes are unchanged; the distinct reasons for unresolved/blocked are exposed.
These research fields are not additions to the native K0 schema.
"""
from fractions import Fraction as F
import json
from pathlib import Path

import certify_atc_sector_lineage as lineage
from certify_atc_os_geometry_feedback import canonical, sha, stringify

ROOT, REFS = lineage.ROOT, lineage.REFS
PREDECESSOR = '787c4a1cf33b3152a228751db98363389a268158614ad7279af79c398adc2521'


def prescribe(n, edges, C, W):
    """Separate partition, arbitration, funding and the fixed size-domain test.

    Per-locus funding/domain fields are diagnostics, never selection weights.
    Aggregate admission fields refer only to a unique selected prescription.
    Construction-domain admission is NOT native readmission or restoration.
    """
    prior = lineage.prescribe(n, edges, C, W)
    result = {k:v for k, v in prior.items() if k not in ('transfer_admission', 'diagnostics')}
    result.update(locus_resolution='undetermined', funding_admission='not_reached',
                  construction_domain_admission='not_reached')
    if 'diagnostics' not in prior:
        return result
    construction = 'admitted' if n+1 <= 16 and len(edges)+1 <= 32 else 'blocked'
    rows = []
    for diagnostic in prior['diagnostics']:
        row = {k:v for k, v in diagnostic.items() if k != 'transfer_admission'}
        row.update(funding_admission=diagnostic['transfer_admission'],
            construction_domain_admission=construction
                if diagnostic['obstruction_status'] == 'certified_present' else 'not_reached')
        rows.append(row)
    result['diagnostics'] = rows
    ambiguous = any(row['decomposition_status'] == 'unresolved' for row in rows)
    count = len(prior['pressure_loci'])
    if count > 1:
        result.update(locus_resolution='multiple_unresolved',
            decomposition_status='unresolved' if ambiguous else 'resolved_per_locus',
            reason='multiple_pressure_loci_and_unresolved_partition' if ambiguous else 'multiple_pressure_loci')
    elif ambiguous:
        result.update(locus_resolution='unresolved_candidates', decomposition_status='unresolved',
                      reason='unresolved_physical_partition')
    elif count == 1:
        selected = prior['prescription']
        assert selected is not None
        row = next(row for row in rows if row['parent'] == selected['parent'])
        result.update(locus_resolution='single_resolved', decomposition_status='resolved',
                      funding_admission=row['funding_admission'],
                      construction_domain_admission=row['construction_domain_admission'])
    else:
        result['locus_resolution'] = 'none_certified'
    return result


def status_checks(prior):
    base = lineage.base
    # Use the pinned, reviewed actual post-beat state; do not rerun dynamics.
    witness = json.loads((ROOT/prior['predecessor']['path']).read_text())
    C1 = tuple(F(v) for v in witness['exact']['ordinary_post_C'])
    blocked_C = (F(1),)*4+(F(11, 10),)
    source, weights = base.SOURCE_EDGES, base.W1
    edges2 = source+tuple((u+5, v+5) for u, v in source)
    edges3 = edges2+tuple((u+10, v+10) for u, v in source)
    cases = {
        'funded_single': (5, source, C1, weights),
        'unfunded_single': (5, source, blocked_C, weights),
        'two_funded': (10, edges2, C1+C1, weights+weights),
        'mixed_funding': (10, edges2, C1+blocked_C, weights+weights),
        'mixed_funding_reversed': (10, edges2, blocked_C+C1, weights+weights),
        'two_unfunded': (10, edges2, blocked_C+blocked_C, weights+weights),
        'funded_size_blocked': (16, source, C1+(F(1),)*11, weights),
        'funding_and_size_blocked': (16, source, blocked_C+(F(1),)*11, weights),
        'ambiguous_partition': (5, source, base.C0, (F(1),)*4),
        'resolved_and_ambiguous': (10, edges2, C1+base.C0, weights+(F(1),)*4),
        'multiple_and_ambiguous': (15, edges3, C1+C1+base.C0, weights+weights+(F(1),)*4),
        'homogeneous': (5, source, (F(9, 5),)*5, weights),
        'invalid_domain': (5, source, base.C0, (F(0),)*4),
    }
    results = {}
    for name, args in cases.items():
        value, old = prescribe(*args), lineage.prescribe(*args)
        for key in ('outcome', 'prescription', 'current', 'pressure_loci', 'obstruction_status'):
            assert value.get(key) == old.get(key), (name, key)
        assert 'transfer_admission' not in value
        assert all('transfer_admission' not in r for r in value.get('diagnostics', []))
        results[name] = value
    for name in ('two_funded', 'mixed_funding', 'mixed_funding_reversed', 'two_unfunded'):
        value = results[name]
        assert value['outcome'] == 'unresolved' and value['prescription'] is None
        assert value['decomposition_status'] == 'resolved_per_locus'
        assert value['locus_resolution'] == 'multiple_unresolved'
        assert all(r['decomposition_status'] == 'resolved' for r in value['diagnostics'])
        assert value['funding_admission'] == value['construction_domain_admission'] == 'not_reached'
    for name, funding in (('funded_single', 'admitted'), ('unfunded_single', 'blocked'),
                          ('funded_size_blocked', 'admitted'), ('funding_and_size_blocked', 'blocked')):
        value = results[name]
        assert value['obstruction_status'] == 'certified_present'
        assert value['decomposition_status'] == 'resolved' and value['locus_resolution'] == 'single_resolved'
        assert value['funding_admission'] == value['diagnostics'][0]['funding_admission'] == funding
        assert value['construction_domain_admission'] == ('blocked' if 'size' in name else 'admitted')
    assert results['unfunded_single']['outcome'] == 'blocked_transfer'
    assert results['funded_size_blocked']['outcome'] == 'uncertified'
    assert results['ambiguous_partition']['decomposition_status'] == 'unresolved'
    assert results['resolved_and_ambiguous']['locus_resolution'] == 'unresolved_candidates'
    assert results['multiple_and_ambiguous']['locus_resolution'] == 'multiple_unresolved'
    assert results['multiple_and_ambiguous']['decomposition_status'] == 'unresolved'
    assert results['homogeneous']['outcome'] == 'no_event'
    assert results['invalid_domain']['outcome'] == 'uncertified'
    # Lineage is a coordinate map with changed incidence, not unchanged endpoints.
    target = prior['exact']['target']
    assert target['old_edge_lineage'] == [[e, e] for e in range(4)]
    assert target['edges'][:4] == [[0, 4], [1, 4], [2, 5], [3, 5]]
    # Even reused integer 4 names a new child, not the deleted source parent.
    assert all(F(x) == y for x, y in zip(target['current_W'][:4], base.W1, strict=True))
    assert all(F(x) == y for x, y in zip(target['reset_W'][:4], base.W0, strict=True))
    return dict(cases=results, case_count=len(results), physical_outcomes_and_prescriptions_unchanged=True,
        lineage_semantics='old edge to successor edge; parent replaced by child; scalar W transported',
        target_constructions=0, trajectory_steps=0, native_events=0)


def run():
    path = REFS/'ATCSectorLineageCertificate.json'
    prior = json.loads(path.read_text())
    assert prior['record_digest'] == PREDECESSOR == sha(canonical({k:v for k,v in prior.items() if k != 'record_digest'}))
    paths = {path, Path(__file__).resolve()}
    for binding in prior['source_bindings']:
        p = ROOT/binding['path']
        assert sha(p.read_bytes()) == binding['sha256'], binding['path']
        paths.add(p)
    record = stringify(dict(schema='grcv4_atc_sector_status_correction_v1',
        status='passed_status_typing_corrections_no_new_mechanism',
        predecessor=dict(path=path.relative_to(ROOT).as_posix(), record_digest=PREDECESSOR),
        review_disposition='independent PASS for predecessor exact and finite mathematics; no full repository run reported',
        checks=status_checks(prior),
        scope='source-only research status typing; neither concurrency policy nor new native authority',
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p.read_bytes())) for p in sorted(paths)],
        scientific_adoption=False, ATC2_closed=False, production_changes=False))
    # Diagnostic edge-index keys must become JSON strings BEFORE canonical sort
    # (indices 10+ otherwise sort numerically here but lexically after reload).
    record = json.loads(json.dumps(record, allow_nan=False))
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, separators=(',', ':'), allow_nan=False))
