"""Bounded native acceptance over unchanged P9-10.1a execution records."""

import json
from pathlib import Path

import p9101a_basin_pressure as execution

PATH = execution.BASE + "P9-10.1a-NativeAcceptance.json"
EVIDENCE = "e7de2ccb2b21e778b87cc90bdb8d1529580cc3cf4c43757f819a8d566f762f9f"
ACCEPTANCE = "07ab5fae7e2cb15fe72ec8dd48842633666bf032c5cd70ca03b086a151e8dd01"


def decision(root, evidence=None):
    root = Path(root).resolve()
    evidence = execution.status(root) if evidence is None else evidence
    native = execution.predecessor
    if evidence != native.seal(evidence) or evidence["record_digest"] != EVIDENCE:
        raise ValueError("native acceptance evidence changed")
    value = json.loads((root / PATH).read_bytes())
    if (
        value != native.seal(value)
        or value["record_digest"] != ACCEPTANCE
        or value["status"] != "accepted_bounded_native_conformance"
        or value["families"] != list(native.FAMILIES)
        or value["user_accepted"] is not True
        or value["P9_10_1a_closed"] is not True
        or value["full_GRC9V4_conformance"] is not False
        or value["execution_projection_digest"] != EVIDENCE
        or value["evidence"] != evidence["records"]
    ):
        raise ValueError("native acceptance decision or scope changed")
    for ref in value["review_sources"]:
        path = root / ref["path"]
        if (
            Path(ref["path"]).is_absolute()
            or ".." in Path(ref["path"]).parts
            or not path.resolve().is_relative_to(root)
            or native.sha(path.read_bytes()) != ref["sha256"]
        ):
            raise ValueError("native acceptance review source changed")
    return value


def status(root=execution.ROOT):
    root = Path(root).resolve()
    evidence = execution.status(root)
    accepted = decision(root, evidence)
    native = execution.predecessor
    ref = dict(
        path=PATH,
        sha256=native.sha((root / PATH).read_bytes()),
        record_digest=accepted["record_digest"],
    )
    return native.seal(
        dict(
            **{
                k: v
                for k, v in evidence.items()
                if k
                not in {"record_digest", "schema", "user_accepted", "P9_10_1a_closed"}
            },
            schema="p9101a-native-basin-accepted-status-v1",
            user_accepted=True,
            P9_10_1a_closed=True,
            acceptance=ref,
            verification_obligation_resolution=accepted[
                "verification_obligation_resolution"
            ],
            remaining_work=accepted["remaining_work"],
            source_refs=[ref, *accepted["review_sources"]],
        )
    )


if __name__ == "__main__":
    print(json.dumps(status(), indent=2))
