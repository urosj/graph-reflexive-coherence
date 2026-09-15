"""Finite C_RG2b discovery successor; immutable evidence, no hash waivers."""

import phase9_implementation_policy as p

RECORD = 'implementation/phase-9-grcv4/tranche-7/P9-7.7-C_RG2b-G2SourceReuse.json'
BASE = '796229e'
EXPECTED_DIGEST = '139b94df3fd1a200fb586dfefd4b767f281da828db4b1c76d267cfc2498711fd'


def record():
    value = p.read(p.ROOT / RECORD)
    p.require(value['schema'] == 'phase9_exact_discovery_source_reuse_v1'
              and value['record_digest'] == p.digest_record(value) == EXPECTED_DIGEST
              and value['base_commit'] == BASE, 'C_RG2b discovery source-reuse record drift')
    p.git(p.ROOT, 'merge-base', '--is-ancestor', BASE, 'HEAD')
    return value


def retained_bindings(current):
    result = dict(current)
    for name, row in record()['changes'].items():
        if name not in result:
            continue
        p.require(p.sha(p.safe_path(p.ROOT, name).read_bytes()) == row['after_sha256'],
                  'unreviewed change after C_RG2b discovery: ' + name)
        p.require(p.sha(p.git(p.ROOT, 'show', BASE + ':' + name)) == row['before_sha256'],
                  'unrecoverable pre-C_RG2b source: ' + name)
        p.require(result[name] in (row['before_sha256'], row['after_sha256']),
                  'unrelated source identity cannot use C_RG2b bridge: ' + name)
        result[name] = row['before_sha256']
    return result
