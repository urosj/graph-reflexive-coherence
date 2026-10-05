"""Finite A_PC discovery successor; immutable evidence, no hash waivers."""

import phase9_implementation_policy as p

RECORD = 'implementation/phase-9-grcv4/tranche-7/P9-7.7-A_PC-G2SourceReuse.json'
BASE = 'b4909a3'
EXPECTED_DIGEST = 'e7dad0249157485bcf73187804b1f71eb84a16e8c329c539b7f39aba93403626'


def record():
    value = p.read(p.ROOT / RECORD)
    p.require(value['schema'] == 'phase9_exact_discovery_source_reuse_v1'
              and value['record_digest'] == p.digest_record(value) == EXPECTED_DIGEST
              and value['base_commit'] == BASE, 'A_PC discovery source-reuse record drift')
    p.git(p.ROOT, 'merge-base', '--is-ancestor', BASE, 'HEAD')
    return value


def retained_bindings(current):
    from tranche8_source_reuse import through
    return through(current, "a_pc_g2_source_reuse")
