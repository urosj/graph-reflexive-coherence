"""Scoped user acceptance; original public execution records remain unchanged."""

import json
from pathlib import Path

import p994b_public_api as c

PATH = c.BASE + "P9-9.4b-Acceptance.json"
DIGEST = "eca188da8a0a75ad67e87124136dc89ff5c8d5642aa07ee5d0a15eda9f795c3c"


def decision(root):
    root = Path(root).resolve()
    value = json.loads((root / PATH).read_bytes())
    if value != c.seal(value) or value["record_digest"] != DIGEST:
        raise ValueError("invalid public integration acceptance")
    for ref in [*value["executions"].values(), value["review"], value["architecture"]]:
        if c.sha((root / ref["path"]).read_bytes()) != ref["sha256"]:
            raise ValueError("accepted public integration subject drift")
    return value


def status(root):
    root = Path(root).resolve()
    accepted = decision(root)
    view = c.status(root)
    for row in view["records"]:
        if row["record_digest"] != accepted["executions"][row["family"]]["record_digest"]:
            raise ValueError("public acceptance differs from checked execution")
    view.update(user_accepted=True, state="bounded_accepted", acceptance_digest=DIGEST)
    view["source_refs"].append(dict(path=PATH, sha256=c.sha((root / PATH).read_bytes())))
    return view
