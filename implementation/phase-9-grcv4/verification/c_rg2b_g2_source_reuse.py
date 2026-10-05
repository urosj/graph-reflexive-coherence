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
    from tranche8_source_reuse import through
    return through(current, "c_rg2b_g2_source_reuse")
