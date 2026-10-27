"""Pinned user acceptance; preserve original delegate execution evidence."""

import json
from pathlib import Path

import p992_compatibility as c

PATH = c.BASE + "P9-9.2-Acceptance.json"
DIGEST = "7ab8d58fcc8dfa2b527c47fc5b58e05f21aac991d4506546bb1e2b094c3b0e92"


def decision(root):
    root = Path(root).resolve()
    value = json.loads((root / PATH).read_bytes())
    if (
        value != c.seal(value)
        or value["record_digest"] != DIGEST
        or value["families"] != list(c.FAMILIES)
        or not value["user_accepted"]
        or not value["bounded_leaf_closed"]
        or value["aggregate_closed"]
        or value["full_GRC9V4_conformance"]
        or value["crossings_executed"]
    ):
        raise ValueError("invalid bounded delegate acceptance")
    for ref in [*value["executions"].values(), value["review"], value["authority"]]:
        path = (root / ref["path"]).resolve()
        if (
            Path(ref["path"]).is_absolute()
            or not path.is_relative_to(root)
            or c.sha(path.read_bytes()) != ref["sha256"]
        ):
            raise ValueError("accepted delegate subject drift: " + ref["path"])
    return value


def status(root):
    root = Path(root).resolve()
    accepted = decision(root)
    view = c.status(root)  # Current source integrity; never executes native steps.
    for row in view["cells"]:
        if row["family"] in c.FAMILIES:
            if (
                row["iteration_id"] not in accepted["accepted_cells"]
                or row["record_digest"]
                != accepted["executions"][row["family"]]["record_digest"]
            ):
                raise ValueError("cell is outside accepted execution scope")
            row["state"] = "bounded_accepted"
    view["user_accepted"] = True
    view["acceptance_digest"] = accepted["record_digest"]
    view["source_refs"].append(
        dict(path=PATH, sha256=c.sha((root / PATH).read_bytes()))
    )
    return view
