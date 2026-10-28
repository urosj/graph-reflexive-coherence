"""Bounded user acceptance over the unchanged reconciliation and direct-target runs."""

from copy import deepcopy
import json
from pathlib import Path

import p9101c_support_reconciliation as execution

PATH = execution.BASE + "P9-10.1c-Acceptance.json"
REVIEW = execution.REVIEW
EVIDENCE = "4f47c70163ad0575c54a45595648a313f3ef990cab138f9ecde3796ee0f2490a"
ACCEPTANCE = "437506ebaa92a32a2af4579f3af43ba713a2be1fa72fb714e8ce37f3c76b6191"


def decision(root, evidence=None):
    root = Path(root).resolve()
    evidence = execution.check(root) if evidence is None else evidence
    if evidence != execution.seal(evidence) or evidence["record_digest"] != EVIDENCE:
        raise ValueError("accepted reconciliation evidence changed")
    value = json.loads((root / PATH).read_bytes())
    if (
        value != execution.seal(value)
        or value["record_digest"] != ACCEPTANCE
        or value["status"] != "accepted_bounded_support_reconciliation"
        or value["families"] != list(execution.FAMILIES)
        or any(
            value[k] is not True
            for k in ("user_accepted", "P9_10_1c_closed", "P9_10_1_closed")
        )
        or value["reconciliation_digest"] != EVIDENCE
        or value["direct_target_evidence"]
        != [
            row["expanded_target_compatibility"][1]["basin"][
                "direct_independent_check"
            ]["source_ref"]
            for row in evidence["rows"]
        ]
        or any(
            value[k] is not False
            for k in (
                "full_GRC9V4_conformance",
                "G4_accepted",
                "other_six_native_execution",
                "compatibility_capability_advertised",
            )
        )
        or value["new_support"] != []
        or value["remaining_hold_ids"] != [h["id"] for h in evidence["open_items"]]
    ):
        raise ValueError("bounded support acceptance decision or scope changed")
    for ref in value["review_sources"]:
        if execution.ref(root, ref["path"]) != ref:
            raise ValueError("accepted support review source changed")
    return value


def status(root=execution.ROOT):
    root = Path(root).resolve()
    evidence = execution.check(root)
    accepted = decision(root, evidence)
    ref = dict(**execution.ref(root, PATH), record_digest=accepted["record_digest"])
    value = deepcopy(evidence)
    value.update(
        schema="p9101c-support-accepted-status-v1",
        state="accepted_bounded_support_reconciliation",
        user_accepted=True,
        P9_10_1c_closed=True,
        P9_10_1_closed=True,
        acceptance=ref,
        next_work=accepted["next_work"],
        source_refs=[*value["source_refs"], ref, *accepted["review_sources"]],
    )
    value["exact_target_basin_checks"]["user_accepted"] = True
    for row in value["rows"]:
        direct = row["expanded_target_compatibility"][1]["basin"][
            "direct_independent_check"
        ]
        direct["user_accepted"] = True
        direct["status"] = "accepted_direct_independent_check_on_this_exact_v2_target"
    return execution.seal(value)


if __name__ == "__main__":
    print(json.dumps(status(), indent=2))
