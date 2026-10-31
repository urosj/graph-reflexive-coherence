"""Finite C_RG2b admission; authenticate and preserve accepted source epochs."""
import p910_arg2b_source_epoch as latest
import ast
import hashlib
import json
from pathlib import Path
import subprocess

BASELINE = "a8be36c7"
BASE = "implementation/phase-9-grcv4/"
SELF = BASE + "verification/p910_crg2b_source_epoch.py"
PATH = BASE + "tranche-10/P9-10-CRG2b-SourceEpochs.json"
CHANGED = {
    "src/pygrc/models/grc_9_v4_basin.py",
    "src/pygrc/models/grc_9_v4_api_lifecycle.py",
    "tests/models/test_grc_9_v4_basin.py",
    "tests/models/test_grc_9_v4_crg2b_integration.py",
    *(BASE + "verification/" + n + ".py" for n in (
        "p910_acipc_source_epoch", "p910_family_basin", "p9101c_target_basin",
        "test_p9101b_target_compatibility", "p9101a_basin_oracle")),
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
    class PriorPaths(ast.NodeTransformer):
        removed = 0
        def visit_If(self, node):
            if (isinstance(node.test, ast.Compare) and len(node.test.comparators) == 1
                    and isinstance(node.test.comparators[0], ast.Constant)
                    and node.test.comparators[0].value == "RG2b"):
                self.removed += 1
                return [self.visit(n) for n in node.orelse]
            return self.generic_visit(node)
        def visit_Tuple(self, node):
            if all(isinstance(e, ast.Constant) for e in node.elts) and any(e.value == "C_RG2b" for e in node.elts):
                node.elts = [e for e in node.elts if e.value != "C_RG2b"]
            return self.generic_visit(node)
    projection = PriorPaths()
    after = projection.visit(after)
    if projection.removed != 2 or ast.dump(before) != ast.dump(after):
        raise ValueError("basin changed beyond C_RG2b admission/read/certificate branches")
    name = "src/pygrc/models/grc_9_v4_api_lifecycle.py"
    before, after = ast.parse(original(root, name)), ast.parse(latest.previous_bytes(root, name))
    branches = [n for n in ast.walk(after) if isinstance(n, ast.Compare)
                and len(n.ops) == 1 and isinstance(n.ops[0], ast.In)
                and ast.dump(n.comparators[0]) == ast.dump(ast.parse('("PC", "RG2b")', mode="eval").body)]
    if len(branches) != 1:
        raise ValueError("RG2b observable projection scope changed")
    branches[0].ops, branches[0].comparators = [ast.Eq()], [ast.Constant(value="PC")]
    if ast.dump(before) != ast.dump(after):
        raise ValueError("old observable projection changed")
    return True


def manifest(root):
    return seal(dict(schema="p910-crg2b-source-epoch-v1", predecessor=BASELINE,
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
    if (value != seal(value) or value["schema"] != "p910-crg2b-source-epoch-v1"
            or value["predecessor"] != BASELINE or set(value["sources"]) != CHANGED
            or value["checker_sha256"] != sha(latest.previous_bytes(root, SELF))
            or value["prior_native_paths_unchanged"] is not True
            or value["accepted_execution_rewritten"] is not False):
        raise ValueError("C_RG2b source epoch identity changed")
    row, old = value["sources"][name], original(root, name)
    if sha(raw) != row["after_sha256"] or sha(old) != row["before_sha256"]:
        raise ValueError("unregistered C_RG2b source successor: " + name)
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
