"""Pinned bounded crossing acceptance; original execution records are unchanged."""
import json
from pathlib import Path
import p994a_crossings as c
PATH = c.BASE + "P9-9.4a-Acceptance.json"
DIGEST = "f0a45bfef9b71872442708ffbd17b6ddf9f2480513604504eb518456e8e24e4e"


def decision(root):
    root = Path(root).resolve()
    value = json.loads((root / PATH).read_bytes())
    if value != c.seal(value) or value["record_digest"] != DIGEST:
        raise ValueError("invalid crossing acceptance")
    for ref in [*value["executions"].values(), value["review"]]:
        if c.sha((root/ref["path"]).read_bytes()) != ref["sha256"]:
            raise ValueError("accepted crossing subject drift")
    return value


def status(root):
    root = Path(root).resolve()
    accepted = decision(root)
    view = c.status(root)
    for row in view["records"]:
        if row["record_digest"] != accepted["executions"][row["family"]]["record_digest"]:
            raise ValueError("acceptance mismatch")
    view.update(user_accepted=True, state="bounded_accepted", acceptance_digest=DIGEST)
    view["source_refs"].append(dict(path=PATH,sha256=c.sha((root/PATH).read_bytes())))
    return view
