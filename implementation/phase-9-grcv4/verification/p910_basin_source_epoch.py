"""Finite A_OS basin successor; preserve accepted source epochs without reruns."""
from p910_cpc_source_epoch import previous_bytes, peel_sha as cpc_peel_sha

import ast
import hashlib
import json
from pathlib import Path
import subprocess

BASELINE = "f2333b32"
BASE = "implementation/phase-9-grcv4/"
PATH = BASE + "tranche-10/P9-10-AOS-SourceEpochs.json"
SELF = BASE + "verification/p910_basin_source_epoch.py"
CHANGED = {
    "src/pygrc/models/grc_9_v4_basin.py",
    "tests/models/test_grc_9_v4_basin.py",
    "tests/models/test_grc_9_v4_aos_integration.py",
    *(BASE + "verification/" + n + ".py" for n in
      ("test_p9101b_target_compatibility", "p9101c_target_basin",
       "p9102_verification", "p9_tranches89_closeout")),
}


def sha(raw): return hashlib.sha256(raw).hexdigest()


def original(root, name):
    return subprocess.check_output(["git", "show", BASELINE + ":" + name], cwd=root)


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=sha(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()))


def first_group_unchanged(root):
    name = "src/pygrc/models/grc_9_v4_basin.py"
    tree = ast.parse(previous_bytes(root, name))
    before = ast.parse(original(root, name))
    old = next(n for n in before.body if isinstance(n, ast.FunctionDef) and n.name == "_read_once")
    current = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_read_once")
    # OS-C preserves the exact CandidateCCurrent branch. The only new branch
    # constructs CandidateACurrent; CI/PC and all capture binding logic remain.
    expected = '''def _read_once(inputs, backend):
    identity = inputs.geometry.reference.profile.identity_payload
    realization = identity.realization
    if realization == "OS":
        if identity.candidate == "A":
            from .grc_v4_candidate_a import CandidateACurrent
            read = point = CandidateACurrent(inputs, backend)
        else:
            from .grc_v4_candidate_c import CandidateCCurrent
            read = point = CandidateCCurrent(inputs)
'''
    prefix = ast.parse(expected).body[0]
    # Append the unchanged original CI/PC continuation and return expression.
    prefix.body[2].orelse = old.body[1].orelse
    prefix.body.extend(old.body[2:])
    if ast.dump(current) != ast.dump(prefix):
        raise ValueError("basin read changed beyond the explicit A_OS branch")
    tree.body[tree.body.index(current)] = old
    capture = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "capture")
    tuples = [n for n in ast.walk(capture) if isinstance(n, ast.Tuple)
              and all(isinstance(e, ast.Constant) for e in n.elts)
              and [e.value for e in n.elts] == ["C_OS", "C_CI", "A_CI", "A_PC", "A_OS"]]
    if len(tuples) != 1:
        raise ValueError("basin family scope changed")
    tuples[0].elts.pop()
    if ast.dump(tree) != ast.dump(before):
        raise ValueError("basin changed outside the reviewed A_OS extension")
    return True


def manifest(root):
    root = Path(root).resolve()
    return seal(dict(schema="p910-aos-basin-source-epoch-v1", predecessor=BASELINE,
        checker_sha256=sha(previous_bytes(root, SELF)),
        sources={n: dict(before_sha256=sha(original(root, n)),
                         after_sha256=sha(previous_bytes(root, n))) for n in sorted(CHANGED)},
        first_group_native_path_unchanged=first_group_unchanged(root),
        accepted_execution_rewritten=False, user_acceptance_inferred=False))


def peel_sha(root, name, present):
    present = cpc_peel_sha(root, name, present)
    if name not in CHANGED:
        return present
    root = Path(root).resolve()
    value = json.loads((root / PATH).read_bytes())
    if value != seal(value) or value["schema"] != "p910-aos-basin-source-epoch-v1" \
       or value["predecessor"] != BASELINE or set(value["sources"]) != CHANGED \
       or value["checker_sha256"] != sha(previous_bytes(root, SELF)) \
       or value["accepted_execution_rewritten"] is not False or value["user_acceptance_inferred"] is not False:
        raise ValueError("A_OS basin source-epoch identity changed")
    row = value["sources"][name]
    if sha(previous_bytes(root, name)) != row["after_sha256"] or sha(original(root, name)) != row["before_sha256"]:
        raise ValueError("unregistered A_OS basin source successor: " + name)
    return row["before_sha256"] if present == row["after_sha256"] else present


def references_match(root, expected, current):
    return expected == [dict(path=r["path"], sha256=peel_sha(root, r["path"], r["sha256"]))
                        for r in current]


def read_source(root, ref):
    name = ref["path"]
    raw = (Path(root) / name).read_bytes()
    if sha(raw) == ref["sha256"]:
        return raw, ref
    from p910_cpc_source_epoch import read_source as cpc_read_source
    if name not in CHANGED:
        return cpc_read_source(root, ref)
    if peel_sha(root, name, sha(raw)) != ref["sha256"]:
        raise ValueError("unbound historical basin source: " + name)
    return original(root, name), dict(ref, revision=BASELINE, basis="historical_git")
