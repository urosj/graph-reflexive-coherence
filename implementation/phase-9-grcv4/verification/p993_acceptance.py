"""Accepted matrix register, with no new runtime support."""

import json
from pathlib import Path
import p993_matrix as m

PATH = m.c.BASE + "P9-9.3-Acceptance.json"
DIGEST = "8d0b7387bf381b946a9ea40a84cbe1a9194747fc377cabc276c25f937fcc6806"


def decision(root):
    root = Path(root).resolve()
    value = json.loads((root / PATH).read_bytes())
    if value != m.c.seal(value) or value["record_digest"] != DIGEST:
        raise ValueError("invalid matrix acceptance")
    for ref in (value["matrix"], value["review"]):
        if m.c.sha((root / ref["path"]).read_bytes()) != ref["sha256"]:
            raise ValueError("accepted matrix subject drift")
    return value


def status(root):
    root = Path(root).resolve()
    accepted = decision(root)
    view = m.status(root)
    if (
        view["matrix_reconciliation"]["record_digest"]
        != accepted["matrix"]["record_digest"]
    ):
        raise ValueError("matrix acceptance subject mismatch")
    view["matrix_reconciliation"]["user_accepted"] = True
    view["matrix_reconciliation"]["acceptance_digest"] = accepted["record_digest"]
    view["source_refs"].append(
        dict(path=PATH, sha256=m.c.sha((root / PATH).read_bytes()))
    )
    return view
