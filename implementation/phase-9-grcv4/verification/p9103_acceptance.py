"""Bounded user decision over unchanged P9-10.3 execution and review."""
import json
from pathlib import Path

import p9103_regressions as execution

PATH = execution.BASE + 'tranche-10/P9-10.3-Acceptance.json'
EVIDENCE = '69f99085588531903e5272d10ccfa51734ee1e74dfc3e9470823666651712982'
ACCEPTANCE = '3a658c91960e2f4c8b8fcf8c87191e95ba688359514879d6ceef0786113b1806'


def decision(root, evidence):
    root = Path(root).resolve()
    execution.require(evidence == execution.seal(evidence) and evidence['record_digest'] == EVIDENCE,
                      'accepted P9-10.3 execution changed')
    value = json.loads((root / PATH).read_bytes())
    execution.require(value == execution.seal(value) and value['record_digest'] == ACCEPTANCE
        and value['schema'] == 'p9103-regression-acceptance-v1'
        and value['status'] == 'accepted_bounded_regressions'
        and value['families'] == list(execution.FAMILIES)
        and all(value[k] is True for k in ('user_accepted', 'P9_10_3_closed', 'all_ten_bounded_inputs_reconciled'))
        and all(value[k] is False for k in ('G4_accepted', 'full_GRC9V4_conformance'))
        and value['new_support'] == [] and value['tests_run'] == evidence['tests_run']
        and value['release_id'] == evidence['preservation']['release_id']
        and value['evidence'] == dict(**execution.reference(root, execution.PATH), record_digest=EVIDENCE),
        'P9-10.3 acceptance identity or scope changed')
    for ref in value['review_sources']:
        execution.require(ref == execution.historical_reference(root, ref['path']), 'accepted P9-10.3 review/source changed')
    return value
