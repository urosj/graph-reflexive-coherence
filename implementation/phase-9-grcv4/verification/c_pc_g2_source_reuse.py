"""Finite C_PC discovery successor; immutable evidence, no hash waivers."""

import phase9_implementation_policy as p

RECORD = 'implementation/phase-9-grcv4/tranche-7/P9-7.7-C_PC-G2SourceReuse.json'
BASE = '06475b2'
EXPECTED_DIGEST = '276c609d83854ddc940062f8b3a425c2317516a1e9cfb4b08e63846128a787d4'


def record():
    value = p.read(p.ROOT / RECORD)
    p.require(value['schema'] == 'phase9_exact_discovery_source_reuse_v1'
              and value['record_digest'] == p.digest_record(value) == EXPECTED_DIGEST
              and value['base_commit'] == BASE, 'C_PC discovery source-reuse record drift')
    p.git(p.ROOT, 'merge-base', '--is-ancestor', BASE, 'HEAD')
    return value


def retained_bindings(current):
    from tranche8_source_reuse import through
    return through(current, "c_pc_g2_source_reuse")
