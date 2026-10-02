"""Pinned G3 decision and narrow first-leaf entry; not specialization conformance."""
import phase9_implementation_policy as p

RECORD = p.PHASE + 'tranche-7/P9-7.8-G3Acceptance.json'
DIGEST = '5175491685e067a8653f561d497c88f587f90ba2c27926f64d598ce502a57c16'
CHECKPOINT = 'c6925b5f15612204e99bb5140ba9129dd13f12dc'
ENTRY = 'P9-8.1a'
PATHS = ('src/pygrc/models/grc_9_v4_topology.py', 'tests/models/test_grc_9_v4_topology.py')


def accepted(root):
    from profile_g2_registry import checked
    v = p.read(p.safe_path(root, RECORD))
    p.require(v['record_digest'] == p.digest_record(v) == DIGEST
              and v['reviewed_commit'] == CHECKPOINT, 'G3 acceptance identity drift')
    p.git(root, 'merge-base', '--is-ancestor', CHECKPOINT, 'HEAD')
    for ref in (v['review'], v['review_text']):
        data = p.safe_path(root, ref['path']).read_bytes()
        p.require(data == p.git(root, 'show', CHECKPOINT + ':' + ref['path'])
                  and p.sha(data) == ref['sha256'], 'accepted G3 review changed')
    review = p.read(p.safe_path(root, v['review']['path']))
    support = checked(root)['accepted_generic_runtime_support']
    p.require(review['record_digest'] == p.digest_record(review) == v['review']['record_digest']
              and v['accepted_generic_runtime_support'] == review['proposed_consumed_support'] == support
              and v['admitted_specialization_support_sets'] == [support]
              and v['G3_accepted'] is True and v['tranche_7_closed'] is True
              and v['new_runtime_iterations_authorized'] == [ENTRY]
              and v['runtime_paths'] == list(PATHS)
              and v['specialization_runtime_conformance'] is False
              and v['a_expansion_work'] == review['a_expansion_work'], 'G3 accepted scope mismatch')
    return v


def permitted(path, leaf):
    """Call only after accepted(root); neither a label nor a file grants G3."""
    return leaf == ENTRY and path in PATHS


ROW_ENTRY = 'P9-8.1b'
ROW_PREDECESSOR = '75a662916501c59d3d7ff06cee942258ed6d8c4b'
ROW_PREDECESSOR_HASHES = (
    'c085dc3b4a746bf3f0720cb68722fcfa150c4b9a0805392467605b8b597299b9',
    'f9983f0a5de9709a7f25219b51efe3e2c7d72d395aa4b0493562ede3c0d9e11a',
)


def row_bridge_authorization(root):
    """2026-10-02 user request: execute all of .b after committed .a review.

    This is a scoped execution successor, not an amendment to the historical
    G3 decision, acceptance of .b, or permission for another native leaf.
    """
    accepted(root)
    p.git(root, 'merge-base', '--is-ancestor', ROW_PREDECESSOR, 'HEAD')
    for path, expected in zip(PATHS, ROW_PREDECESSOR_HASHES, strict=True):
        p.require(p.sha(p.git(root, 'show', ROW_PREDECESSOR + ':' + path)) == expected,
                  'row bridge requires the committed chart/graph review subject')
    return ROW_ENTRY


def row_bridge_permitted(path, leaf):
    """Call only after row_bridge_authorization(root)."""
    return leaf == ROW_ENTRY and path in PATHS


TRIGGER_ENTRY = 'P9-8.1c'
TRIGGER_PATHS = ('src/pygrc/models/grc_9_v4_lifecycle.py',
                 'tests/models/test_grc_9_v4_lifecycle.py')
TRIGGER_PREDECESSOR = '7f33a42f8850dbae57b63c8ad09d85bececbaf6e'
TRIGGER_PREDECESSOR_HASHES = (
    '1c3136583ba0148ff708ed980597bf47f3ca5c270f0e6e82fd767a66f2865807',
    '00bd5b342011effc413e8a8a0dea3273ad552e84de1863d19a8fc175d411568e',
)


def trigger_authorization(root):
    """User-requested .c after accepted .b; candidate detection only."""
    accepted(root)
    p.git(root, 'merge-base', '--is-ancestor', TRIGGER_PREDECESSOR, 'HEAD')
    for path, expected in zip(PATHS, TRIGGER_PREDECESSOR_HASHES, strict=True):
        p.require(p.sha(p.git(root, 'show', TRIGGER_PREDECESSOR + ':' + path)) == expected,
                  'candidate detection requires the accepted row bridge subject')
    return TRIGGER_ENTRY


def trigger_permitted(path, leaf):
    """Call only after trigger_authorization(root); no later lifecycle entry."""
    return leaf == TRIGGER_ENTRY and path in TRIGGER_PATHS


COARSE_ENTRY = 'P9-8.1d'
COARSE_PREDECESSOR = 'e9dfad748b16d9c67b6368f8e3689137944f8f47'
COARSE_PREDECESSOR_HASHES = (
    *TRIGGER_PREDECESSOR_HASHES,
    'a65ea279b644f8592cd763d16e55e931661f7e8100c0e34002a345669589c5c3',
    'f6a991a8e742361df3a02e0a24d7a9827f484c9d97e56c6697bb6ad042c00b7e',
)


def coarse_authorization(root):
    """User-requested .d after accepted .c; column field algebra only."""
    accepted(root)
    p.git(root, 'merge-base', '--is-ancestor', COARSE_PREDECESSOR, 'HEAD')
    for path, expected in zip((*PATHS, *TRIGGER_PATHS), COARSE_PREDECESSOR_HASHES, strict=True):
        p.require(p.sha(p.git(root, 'show', COARSE_PREDECESSOR + ':' + path)) == expected,
                  'column coarse/Split requires the accepted shared mechanics subject')
    return COARSE_ENTRY


def coarse_permitted(path, leaf):
    """Call only after coarse_authorization(root); reviewed topology owner."""
    return leaf == COARSE_ENTRY and path in PATHS
