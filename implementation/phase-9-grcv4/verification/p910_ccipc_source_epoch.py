"""Authenticate the finite CI+PC extension without rewriting accepted evidence."""
import p910_acipc_source_epoch as latest

import ast
import hashlib
import json
from pathlib import Path
import subprocess

BASELINE = "9fb469c8"
BASE = "implementation/phase-9-grcv4/"
SELF = BASE + "verification/p910_ccipc_source_epoch.py"
PATH = BASE + "tranche-10/P9-10-CCIPC-SourceEpochs.json"
CHANGED = {
    "src/pygrc/models/grc_9_v4_basin.py",
    "tests/models/test_grc_9_v4_basin.py",
    "tests/models/test_grc_9_v4_ccipc_integration.py",
    *(BASE + "verification/" + n + ".py" for n in (
        "p910_cpc_source_epoch", "p910_family_basin", "p9101a_basin_oracle",
        "p9101c_target_basin", "test_p9101b_target_compatibility")),
}


def sha(raw): return hashlib.sha256(raw).hexdigest()


def original(root, name):
    return subprocess.check_output(["git", "show", BASELINE + ":" + name], cwd=root)


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=sha(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()))


def prior_native_paths_unchanged(root):
    name = "src/pygrc/models/grc_9_v4_basin.py"
    before, after = ast.parse(original(root, name)), ast.parse(latest.previous_bytes(root, name))
    capture = next(n for n in after.body if isinstance(n, ast.FunctionDef) and n.name == "capture")
    rosters = [n for n in ast.walk(capture) if isinstance(n, ast.Tuple)
               and all(isinstance(e, ast.Constant) for e in n.elts)
               and [e.value for e in n.elts] == ["C_OS", "C_CI", "A_CI", "A_PC", "A_OS", "C_PC", "C_CI_PC"]]
    if len(rosters) != 1:
        raise ValueError("CI+PC basin family scope changed")
    rosters[0].elts.pop()
    branches = [n for n in ast.walk(after) if isinstance(n, ast.Compare)
                and len(n.ops) == 1 and isinstance(n.ops[0], ast.In)
                and ast.dump(n.comparators[0]) == ast.dump(ast.parse('("CI", "CI+PC")', mode="eval").body)]
    if len(branches) != 2:
        raise ValueError("joint-root successor branches changed")
    for n in branches:
        n.ops, n.comparators = [ast.Eq()], [ast.Constant(value="CI")]
    if ast.dump(before) != ast.dump(after):
        raise ValueError("basin changed beyond CI+PC joint capture admission")
    return True


def manifest(root):
    return seal(dict(schema="p910-ccipc-source-epoch-v1", predecessor=BASELINE,
        checker_sha256=sha(latest.previous_bytes(root, SELF)),
        sources={n: dict(before_sha256=sha(original(root, n)), after_sha256=sha(latest.previous_bytes(root, n)))
                 for n in sorted(CHANGED)},
        prior_native_paths_unchanged=prior_native_paths_unchanged(root), accepted_execution_rewritten=False))


def previous_bytes(root, name):
    root = Path(root).resolve()
    raw = latest.previous_bytes(root, name)
    if name not in CHANGED:
        return raw
    value = json.loads((root / PATH).read_bytes())
    if (value != seal(value) or value["schema"] != "p910-ccipc-source-epoch-v1"
            or value["predecessor"] != BASELINE or set(value["sources"]) != CHANGED
            or value["checker_sha256"] != sha(latest.previous_bytes(root, SELF))
            or value["prior_native_paths_unchanged"] is not True
            or value["accepted_execution_rewritten"] is not False):
        raise ValueError("CI+PC source epoch identity changed")
    row, old = value["sources"][name], original(root, name)
    if sha(raw) != row["after_sha256"] or sha(old) != row["before_sha256"]:
        raise ValueError("unregistered CI+PC source successor: " + name)
    return old


def peel_sha(root, name, present):
    present = latest.peel_sha(root, name, present)
    previous = previous_bytes(root, name)
    return sha(previous) if present == sha(latest.previous_bytes(root, name)) else present


def read_source(root, ref):
    raw = (root / ref["path"]).read_bytes()
    if sha(raw) == ref["sha256"]:
        return raw, ref
    old = previous_bytes(root, ref["path"])
    if sha(old) != ref["sha256"]:
        return latest.read_source(root, ref)
    return old, dict(ref, revision=BASELINE, basis="historical_git")
