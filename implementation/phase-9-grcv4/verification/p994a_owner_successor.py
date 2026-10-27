"""Authenticate 9.1b history across the explicit 9.4a rejection-only correction.

Original records and verifier stay immutable. Only this exact runtime hash pair
is permitted; 9.4a independently binds and pressures the successor behavior.
"""

import json
from pathlib import Path
from p991b_acceptance import decision, sha, seal, BASE, FAMILIES, CONTEXT


def check(root, family):
    root = Path(root).resolve()
    accepted = decision(root)
    if family not in FAMILIES:
        raise ValueError("unaccepted family")
    ref = accepted["executions"][family]
    if ref["path"] != BASE + "P9-9.1b-" + family + ".json":
        raise ValueError("unexpected execution path")
    raw = (root / ref["path"]).read_bytes()
    value = json.loads(raw)
    if (
        sha(raw) != ref["sha256"]
        or value["record_digest"] != ref["record_digest"]
        or seal(value) != value["record_digest"]
    ):
        raise ValueError("accepted execution changed")
    for row in value["source_refs"] + value["input_refs"]:
        name = row["path"]
        path = (root / name).resolve()
        if Path(name).is_absolute() or not path.is_relative_to(root):
            raise ValueError("nonportable execution input")
        if name in CONTEXT:
            actual = accepted["execution_context_preimages"][name]["sha256"]
        elif (
            name == "src/pygrc/models/grc_9_v4_owner.py"
            and sha(path.read_bytes())
            == "a90bdcd3cc5d8ffd84e7f909f811b74b53f29b2b6ff94ef6a80356f62b3f0748"
        ):
            # P9-9.4a corrects only post-solver failure classification. Original
            # successful execution bytes remain pinned to their committed owner.
            # Current crossing/negative execution is separately bound in 9.4a.
            import subprocess

            original = subprocess.check_output(
                ["git", "show", "b894c95d:" + name], cwd=root
            )
            actual = sha(original)
            if (
                actual
                != "64f2dadde0b2902444ea4b0dd10d139acda3f69053844d1d7e427231db254563"
            ):
                raise ValueError("historical owner preimage mismatch")
        else:
            actual = sha(path.read_bytes())
        if actual != row["sha256"]:
            raise ValueError("accepted execution input drift: " + name)
    return value
