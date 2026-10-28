"""Bounded P9-9.5 user acceptance; original execution evidence is unchanged."""

import json
from pathlib import Path

import p995_public_conflict as c

PATH = c.BASE + "P9-9.5-Acceptance.json"
DIGEST = "792f1b9640edf2e4ae1e958f09662107ec7fd88ab46110e7820b146661a20bec"


def decision(root):
    root = Path(root).resolve()
    value = json.loads((root / PATH).read_bytes())
    if value != c.seal(value) or value["record_digest"] != DIGEST:
        raise ValueError("invalid public conflict acceptance")
    for ref in [*value["executions"].values(), value["review"], value["authority"]]:
        if c.sha((root / ref["path"]).read_bytes()) != ref["sha256"]:
            raise ValueError("accepted public conflict subject drift")
    return value


def status(root):
    root = Path(root).resolve()
    accepted = decision(root)
    view = c.status(root)
    for row in view["records"]:
        if (
            row["record_digest"]
            != accepted["executions"][row["family"]]["record_digest"]
        ):
            raise ValueError("conflict acceptance differs from checked execution")
    view.update(user_accepted=True, state="bounded_accepted", acceptance_digest=DIGEST)
    view["source_refs"].append(
        dict(path=PATH, sha256=c.sha((root / PATH).read_bytes()))
    )
    return view
