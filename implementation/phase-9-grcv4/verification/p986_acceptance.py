"""Scoped acceptance projection; original conformance records remain unchanged."""
import p986_first_group as h

ACCEPTANCE = h.BASE + 'P9-8.6-FirstGroupAcceptance.json'
ACCEPTANCE_DIGEST = '45e4b5bdabcc2027bce69036ff710861d5e10f865deff7665f9f66500fdbd01c'


def accepted(value, record):
    h.require(record == h.seal(record) and record['record_digest'] == ACCEPTANCE_DIGEST,
              'unbound 8.6 acceptance')
    h.require(record['decision_digest'] == value['group_record_digest']
              and record['user_accepted'] and record['first_group_closed']
              and not record['aggregate_closed'] and record['limits'] == h.LIMITS
              and set(record['families']) == set(h.FAMILIES), '8.6 acceptance scope drift')
    rows = value['decision']['families'] if value['family'] == 'first_group' else [value['decision']]
    for row in rows:
        h.require(record['families'][row['family']] == row['record_digest'], 'unaccepted family decision')
    return dict(value, status='accepted_bounded_first_group', user_accepted=True,
                first_group_closed=True, acceptance=record)


def status(root=h.ROOT, family='first_group'):
    value = accepted(h.status(root, family), h.load(root, ACCEPTANCE))
    value['source_refs'] = h.handoff.unique_refs([value['source_refs'], h.handoff.reference(root, ACCEPTANCE)])
    return value
