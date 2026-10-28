"""Bounded P9-9.6 acceptance; original evidence and remaining holds are unchanged."""

import json
from pathlib import Path

import p996_support_review as c

PATH = c.BASE + "P9-9.6-Acceptance.json"
DIGEST = "8676df0db54680ca97417fb9bcf657e0cf84fc907bccd2b7c5db47264d8ab861"


def decision(root):
    root = Path(root).resolve()
    value = json.loads((root / PATH).read_bytes())
    if value != c.seal(value) or value["record_digest"] != DIGEST:
        raise ValueError("invalid bounded support acceptance")
    for ref in (value["evidence"], value["review"]):
        if c.sha((root / ref["path"]).read_bytes()) != ref["sha256"]:
            raise ValueError("accepted support subject drift")
    return value


def status(root):
    root = Path(root).resolve()
    accepted = decision(root)
    view = c.status(root)
    if (
        view["record_digest"] != accepted["evidence"]["record_digest"]
        or view["families"] != accepted["families"]
        or [r["id"] for r in view["open_items"]] != accepted["remaining_holds"]
    ):
        raise ValueError("support acceptance differs from checked review")
    view.update(
        user_accepted=True,
        state="bounded_accepted",
        acceptance_digest=DIGEST,
        next_work="P9-10.1a baseline basin interface, P9-10.1b expanded-target compatibility, then P9-10.1c support reconciliation. Full conformance remains held.",
    )
    view["source_refs"].append(c.reference(root, PATH))
    return view
