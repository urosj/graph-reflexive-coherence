"""Exact successor discovery-source reuse, composed before the A_OS bridge.

Only pinned before/after identities qualify. No execution record is rewritten;
fresh captures keep actual current source hashes. This does not accept G2.
"""

import phase9_implementation_policy as p

RECORD = p.PHASE + 'tranche-7/P9-7.7-A_CI-G2SourceReuse.json'
BASE = 'fa94cd2'
EXPECTED_DIGEST = '81484b9c23c028fe95b24f63aa77bdaa5f7de09294a11a986009f91d65b155bb'


def record():
    value = p.read(p.ROOT / RECORD)
    p.require(value['schema'] == 'phase9_exact_discovery_source_reuse_v1'
              and value['record_digest'] == p.digest_record(value) == EXPECTED_DIGEST
              and value['base_commit'] == BASE, 'G2 successor source-reuse record drift')
    p.git(p.ROOT, 'merge-base', '--is-ancestor', BASE, 'HEAD')
    return value


def retained_bindings(current):
    from tranche8_source_reuse import through
    return through(current, "g2_source_reuse")

def matches(expected, current):
    from tranche8_source_reuse import retained_bindings as successor, projections
    if not expected.keys() <= current.keys():
        return False
    extras = {n: current[n] for n in current.keys() - expected.keys()}
    if extras and successor(extras):
        return False
    changed = {n: current[n] for n in expected if expected[n] != current[n]}
    if not changed:
        return True
    desired = {n: expected[n] for n in changed}
    return any(desired == value for _, value in projections(changed))
