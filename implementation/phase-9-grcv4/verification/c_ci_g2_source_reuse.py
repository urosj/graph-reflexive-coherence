"""Finite C_CI discovery successor; immutable evidence, no hash waivers."""

import phase9_implementation_policy as p

RECORD = 'implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI-G2SourceReuse.json'
BASE = '8ec744e'
EXPECTED_DIGEST = 'fa704bd13caa4139b020260f9cec6751ab9e96aa47f5e588cd9e2b0bbdd86bf7'


def record():
    value = p.read(p.ROOT / RECORD)
    p.require(value['schema'] == 'phase9_exact_discovery_source_reuse_v1'
              and value['record_digest'] == p.digest_record(value) == EXPECTED_DIGEST
              and value['base_commit'] == BASE, 'C_CI discovery source-reuse record drift')
    p.git(p.ROOT, 'merge-base', '--is-ancestor', BASE, 'HEAD')
    return value


def retained_bindings(current):
    result = dict(current)
    for name, row in record()['changes'].items():
        if name not in result:
            continue
        p.require(p.sha(p.safe_path(p.ROOT, name).read_bytes()) == row['after_sha256'],
                  'unreviewed change after C_CI discovery: ' + name)
        p.require(p.sha(p.git(p.ROOT, 'show', BASE + ':' + name)) == row['before_sha256'],
                  'unrecoverable pre-C_CI source: ' + name)
        p.require(result[name] in (row['before_sha256'], row['after_sha256']),
                  'unrelated source identity cannot use C_CI bridge: ' + name)
        result[name] = row['before_sha256']
    return result
