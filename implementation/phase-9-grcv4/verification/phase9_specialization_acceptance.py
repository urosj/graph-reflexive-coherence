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
