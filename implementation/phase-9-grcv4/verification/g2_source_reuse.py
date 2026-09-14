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
    result = dict(current)
    for name, row in record()['changes'].items():
        if name not in result:
            continue
        p.require(p.sha(p.safe_path(p.ROOT, name).read_bytes()) == row['after_sha256'],
                  'unreviewed change after G2 discovery: ' + name)
        p.require(p.sha(p.git(p.ROOT, 'show', BASE + ':' + name)) == row['before_sha256'],
                  'unrecoverable pre-discovery source: ' + name)
        p.require(result[name] in (row['before_sha256'], row['after_sha256']),
                  'unrelated source identity cannot use G2 discovery bridge: ' + name)
        result[name] = row['before_sha256']
    return result


def matches(expected, current):
    if expected.keys() != current.keys():
        return False
    changed = {n: value for n, value in current.items() if expected[n] != value}
    if not changed:
        return True
    desired = {n: expected[n] for n in changed}
    projected = retained_bindings(changed)
    if desired == projected:
        return True
    from a_os_g2_source_reuse import matches as historical_matches
    return historical_matches(desired, projected)
