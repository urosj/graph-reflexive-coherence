"""Separate bounded user acceptance of the unchanged P9-10.4 publication."""
import json
from pathlib import Path
import p9104_examples as c

PATH = 'implementation/phase-9-grcv4/tranche-10/P9-10.4-Acceptance.json'
EVIDENCE = '5571b97d3e92e14cc1b0ff4b5428591971773f100452f993406fd04b3ade64b4'
ACCEPTANCE = '8508480598a8f672d3f1142634107137ff77118fa039def2ffcac9bff46b972b'


def decision(root, evidence):
    root = Path(root).resolve()
    c.require(root == c.ROOT, 'acceptance repository mismatch')
    c.require(evidence == c.seal(evidence) and evidence['record_digest'] == EVIDENCE,
              'accepted example execution changed')
    value = json.loads((root/PATH).read_bytes())
    c.require(value == c.seal(value) and value['record_digest'] == ACCEPTANCE
        and value['schema'] == 'p9104-example-acceptance-v1'
        and value['status'] == 'accepted_bounded_examples'
        and value['families'] == evidence['families'] and value['lessons'] == evidence['lessons']
        and value['user_accepted'] is True and value['P9_10_4_closed'] is True
        and all(value[k] is False for k in ('full_GRC9V4_conformance','G4_accepted',
                                          'completed_spark','hierarchy_tracking','general_ATC'))
        and value['new_support'] == []
        and value['evidence'] == dict(**c.reference(c.PATH), record_digest=EVIDENCE),
        'example acceptance identity or scope changed')
    for ref in value['review_sources']:
        c.require(ref == c.reference(ref['path']), 'accepted example review/source changed')
    return value
