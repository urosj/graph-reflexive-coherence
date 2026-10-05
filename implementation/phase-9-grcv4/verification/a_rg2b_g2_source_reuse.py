"""Finite A_RG2b discovery successor; immutable evidence, no hash waivers."""

import phase9_implementation_policy as p

RECORD = 'implementation/phase-9-grcv4/tranche-7/P9-7.7-A_RG2b-G2SourceReuse.json'
BASE = '504859f'
EXPECTED_DIGEST = '2cad3d3bf022b122350ec43aea3fc98003f25d430635065f07cde4310c12ea0f'


def record():
    value = p.read(p.ROOT / RECORD)
    p.require(value['schema'] == 'phase9_exact_discovery_source_reuse_v1'
              and value['record_digest'] == p.digest_record(value) == EXPECTED_DIGEST
              and value['base_commit'] == BASE, 'A_RG2b discovery source-reuse record drift')
    p.git(p.ROOT, 'merge-base', '--is-ancestor', BASE, 'HEAD')
    return value


def retained_bindings(current):
    from tranche8_source_reuse import through
    return through(current, "a_rg2b_g2_source_reuse")
