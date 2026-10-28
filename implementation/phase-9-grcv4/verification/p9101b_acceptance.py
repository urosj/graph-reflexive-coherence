"""Bounded user acceptance over unchanged expanded-target execution records."""

import json
from pathlib import Path

import p9101b_target_compatibility as execution

PATH = execution.BASE + "P9-10.1b-Acceptance.json"
EVIDENCE = "20d744fd5cad12432303be78166d30ec1c79834b3c7942f134addbcff13d9328"
ACCEPTANCE = "4904615dedd468be3ddafde5d23030709c66fc05d9c481848f6a4cf56ce9c770"


def decision(root, evidence=None):
    root = Path(root).resolve()
    evidence = execution.status(root) if evidence is None else evidence
    if evidence != execution.seal(evidence) or evidence["record_digest"] != EVIDENCE:
        raise ValueError("target acceptance execution evidence changed")
    value = json.loads((root / PATH).read_bytes())
    if (
        value != execution.seal(value)
        or value["record_digest"] != ACCEPTANCE
        or value["status"] != "accepted_bounded_target_compatibility"
        or value["families"] != list(execution.FAMILIES)
        or value["user_accepted"] is not True
        or value["P9_10_1b_closed"] is not True
        or value["P9_10_1_closed"] is not False
        or value["execution_projection_digest"] != EVIDENCE
        or value["evidence"] != evidence["records"]
        or value["full_GRC9V4_conformance"] is not False
    ):
        raise ValueError("target acceptance decision or scope changed")
    for ref in value["review_sources"]:
        path = root / ref["path"]
        if (
            Path(ref["path"]).is_absolute()
            or ".." in Path(ref["path"]).parts
            or not path.resolve().is_relative_to(root)
            or execution.sha(path.read_bytes()) != ref["sha256"]
        ):
            raise ValueError("target acceptance review source changed")
    return value


def status(root=execution.ROOT):
    root = Path(root).resolve()
    evidence = execution.status(root)
    accepted = decision(root, evidence)
    ref = dict(
        path=PATH,
        sha256=execution.sha((root / PATH).read_bytes()),
        record_digest=accepted["record_digest"],
    )
    value = dict(evidence)
    value.update(
        schema="p9101b-target-compatibility-accepted-status-v1",
        user_accepted=True,
        P9_10_1b_closed=True,
        P9_10_1_closed=False,
        remaining_work=accepted["remaining_work"],
        acceptance=ref,
        source_refs=[ref, *accepted["review_sources"]],
    )
    return execution.seal(value)


if __name__ == "__main__":
    print(json.dumps(status(), indent=2))
