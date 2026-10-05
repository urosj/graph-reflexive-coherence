"""Finite byte-exact reuse of pre-discovery execution sources.

No file-wide waiver: every changed path must match its reviewed after hash,
and its before bytes must exist at the preserved proposal commit. Fresh runs
still bind actual current sources; only retained comparisons use this bridge.
"""

import phase9_implementation_policy as p

RECORD = p.PHASE + 'tranche-7/P9-7.7-A_OS-G2SourceReuse.json'
BASE = 'db36116'
EXPECTED_DIGEST = '5552fa5a4cf58807708221a1d4016594e88c8aff85cd43b060868a8e4a0cf741'


def retained_bindings(current):
    from tranche8_source_reuse import through
    return through(current, "a_os_g2_source_reuse")


def matches(expected, current):
    if expected.keys() != current.keys():
        return False
    # Earlier, independently checked bridges may already have recovered older
    # bytes. Leave matching entries alone; this bridge owns only new differences.
    changed = {name: digest for name, digest in current.items() if expected[name] != digest}
    return not changed or {name: expected[name] for name in changed} == retained_bindings(changed)
