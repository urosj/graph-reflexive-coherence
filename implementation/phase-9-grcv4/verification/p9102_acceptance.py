"""Bounded user acceptance without rewriting or rerunning verified evidence."""

import json
from pathlib import Path

import p9102_verification as execution

PATH = execution.BASE + "tranche-10/P9-10.2-Acceptance.json"
EVIDENCE = "e8551be42f0c01736382c02922ad9c0a3ebc9dc207a7e09ad9abe7960566fe93"
ACCEPTANCE = "5b0b22bb7effe9428dd238c98c8b10083683b524e0350f6e9141ea3edad596d3"


def decision(root, evidence):
    root = Path(root).resolve()
    execution.require(evidence == execution.seal(evidence)
                      and evidence["record_digest"] == EVIDENCE,
                      "accepted P9-10.2 evidence changed")
    value = json.loads((root / PATH).read_bytes())
    execution.require(value == execution.seal(value)
                      and value["record_digest"] == ACCEPTANCE
                      and value["families"] == list(execution.FAMILIES)
                      and value["user_accepted"] is True
                      and value["P9_10_2_closed"] is True
                      and all(value[k] is False for k in
                              ("all_ten_P9_10_2_closed", "G4_accepted", "full_GRC9V4_conformance"))
                      and value["new_support"] == [], "P9-10.2 acceptance or scope changed")
    execution.require(value["evidence"] == dict(
        **execution.reference(root, execution.PATH), record_digest=EVIDENCE),
        "P9-10.2 accepted evidence binding changed")
    for ref in value["review_sources"]:
        execution.require(ref == execution.reference(root, ref["path"]),
                          "P9-10.2 accepted review changed")
    return value


def status(root=execution.ROOT):
    root = Path(root).resolve()
    evidence = execution.check(root)
    accepted = decision(root, evidence)
    ref = dict(**execution.reference(root, PATH), record_digest=ACCEPTANCE)
    return execution.seal(dict(evidence,
        schema="p9102-retained-verification-accepted-status-v1",
        state=accepted["status"], user_accepted=True, P9_10_2_closed=True,
        all_ten_P9_10_2_closed=False, evidence_record_digest=EVIDENCE,
        acceptance=ref, source_refs=[*evidence["source_refs"], ref],
        next_work=accepted["next_work"]))
