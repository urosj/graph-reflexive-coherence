"""P9-1.7 authority/composition policy. Planning is never runtime acceptance."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import stat
import tomllib

_HERE = Path(__file__).resolve().parent
_LEGACY = _HERE / "audit_phase9.py"
if (
    hashlib.sha256(_LEGACY.read_bytes()).hexdigest()
    != "baba1eb0aafa86033237992e796ecd3e65744c94937e02bc80506bc0adb35fad"
):
    raise ValueError("P9-1.6 auditor bytes changed")
_spec = importlib.util.spec_from_file_location("p916_verification", _LEGACY)
prior = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prior)
ROOT, PHASE, HERE, INV, SIDE, SCRIPTS = (
    getattr(prior, n) for n in ["ROOT", "PHASE", "HERE", "INV", "SIDE", "SCRIPTS"]
)
require, read, sha, canonical, git, safe_path = (
    getattr(prior, n)
    for n in ["require", "read", "sha", "canonical", "git", "safe_path"]
)
POLICY = HERE + "Phase9VerificationSuccessor.json"
SNAPSHOT = HERE + "history/P9-1.6-ArtifactSnapshot.json"
SNAPSHOT_DIGEST = "30e310a89dfb61e607ac5b576fa71de7f729a13ad9341073323da80fc45d7781"
RECORD = PHASE + "tranche-1/P9-1.7-1.8-ExecutionRecord.json"
RESULTS = PHASE + "tranche-1/P9-1.7-PressureResults.json"
SCENARIOS = PHASE + "tranche-1/P9-1.7-1.8-Scenarios.json"
REPORT = PHASE + "tranche-1/P9-1.7-1.8-VerificationReview.md"
NEW_PATHS = {
    HERE + "pressure_evidence.py",
    HERE + "test_phase9_gap_pressure.py",
    HERE + "phase9_semantics.py",
    HERE + "inputs/P9-1.6-Successor-Verification-Pressure-Guide.md",
    HERE + "inputs/P9-1.7-Adversarial-Mutation-And-Authority-Pressure-Guide.md",
    HERE + "inputs/P9-1.8-Cross-Surface-Verification-Pressure-Guide.md",
    HERE + "inputs/P9-1.6-1.8-QuickAudit.md",
    PHASE + "tranche-1/P9-1.8-SurfaceInventory.json",
    PHASE + "tranche-1/P9-1.6-1.8-AuditClosure.json",
    POLICY,
    SNAPSHOT,
    RECORD,
    RESULTS,
    SCENARIOS,
    REPORT,
    HERE + "phase9_policy.py",
    HERE + "audit_phase9_successor.py",
    HERE + "test_phase9_pressure.py",
    SIDE + "docs/Phase9VerificationGuide.md",
    SCRIPTS + "serve_phase9.py",
    SCRIPTS + "run_phase9_notebook.py",
    SCRIPTS + "test_phase9_surfaces.py",
    SIDE + "tool/src/grcv4_explorer/phase9_verification.py",
    SIDE + "tool/notebooks/phase9_verification.ipynb",
    SIDE + "tool/phase9-web/index.html",
    SIDE + "tool/phase9-web/verification.js",
    SIDE + "tool/phase9-web/verification.css",
    SIDE + "tool/phase9-web/verification.test.mjs",
    SIDE + "tool/phase9-web/browser.spec.mjs",
    SIDE + "tool/phase9-web/playwright.config.mjs",
}
PATHS = set(prior.MUTABLE) | NEW_PATHS
P916_CHANGED = {
    "implementation/Phase-9-GRCV4-ImplementationPlan.md",
    "implementation/Phase-9-GRCV4-ImplementationChecklist.md",
    SIDE + "GRCV4ExploratorySideToolImplementationPlan.md",
    SIDE + "GRCV4ExploratorySideToolImplementationChecklist.md",
    SCRIPTS + "run.py",
    SCRIPTS + "verify_iteration9.py",
    SCRIPTS + "active_phase.py",
}
PRESSURES = [f"P9-REVIEW-PRESSURE-8.{i}" for i in range(1, 7)]
OPTIONAL = {"completed_spark", "hierarchy_tracking"}


def digest_record(value, field="record_digest"):
    return sha(canonical({k: v for k, v in value.items() if k != field}))


def predecessor(root):
    snapshot = read(safe_path(root, SNAPSHOT))
    require(
        digest_record(snapshot, "snapshot_digest")
        == snapshot["snapshot_digest"]
        == SNAPSHOT_DIGEST,
        "P9-1.6 snapshot drift",
    )
    files = snapshot["files"]
    require(
        len(files) == len(prior.MUTABLE)
        and {r["path"] for r in files} == prior.MUTABLE,
        "P9-1.6 snapshot roster drift",
    )
    for row in files:
        require(
            sha(row["utf8"].encode()) == row["sha256"], "snapshot content binding drift"
        )
        if row["path"] not in P916_CHANGED:
            require(
                safe_path(root, row["path"]).read_bytes() == row["utf8"].encode(),
                "immutable P9-1.6 artifact changed: " + row["path"],
            )
    old = json.loads(next(r["utf8"] for r in files if r["path"] == prior.POLICY))
    require(
        digest_record(old)
        == old["record_digest"]
        == "8282d8e0bdaad9eedb7cdb4eb69a8fccf8700fbec46cce3a9418b1f6838b0aab",
        "P9-1.6 policy predecessor mismatch",
    )
    for row in old["artifact_bindings"]:
        require(
            row["sha256"]
            == next(r["sha256"] for r in files if r["path"] == row["path"]),
            "snapshot does not reconstruct P9-1.6 bindings",
        )
    return snapshot


def validate_policy(root):
    for commit in [
        prior.HISTORICAL,
        prior.ACCEPTANCE,
        prior.MERGE,
        prior.OPENING_COMMIT,
        prior.CHECKPOINT,
    ]:
        prior.ancestor(root, commit)
    prior.git_exact(root, prior.OPENING_COMMIT, prior.OPENING)
    opening = read(root / prior.OPENING)
    parents = git(root, "show", "-s", "--format=%P", prior.MERGE).decode().split()
    require(
        parents
        == [opening["specification_branch_closure"]["first_parent"], prior.ACCEPTANCE],
        "no-ff merge parents drift",
    )
    for name in ["predecessor_phase_boundary", "specification_acceptance"]:
        row = opening[name]
        require(
            prior.git_exact(root, prior.ACCEPTANCE, row["path"]) == row["sha256"],
            "acceptance predecessor mismatch",
        )
    predecessor(root)
    policy = read(safe_path(root, POLICY))
    require(
        set(policy)
        == {
            "schema",
            "active_phase",
            "status",
            "baseline_commit",
            "release_id",
            "predecessor_snapshot_digest",
            "authorization_effect",
            "trusted_runtime_approval",
            "accepted_generic_runtime_support",
            "admitted_specialization_support_sets",
            "exact_mutation_paths",
            "artifact_bindings",
            "record_digest",
        },
        "unsupported successor fields or candidate predecessor chain",
    )
    require(
        policy["schema"] == "phase9_verification_successor_v2"
        and policy["active_phase"] == "implementation_planning",
        "unsupported live successor state",
    )
    require(
        policy["record_digest"] == digest_record(policy), "successor digest mismatch"
    )
    require(
        policy["predecessor_snapshot_digest"] == SNAPSHOT_DIGEST
        and policy["baseline_commit"] == prior.CHECKPOINT
        and policy["release_id"] == prior.RELEASE_ID,
        "stale successor predecessor",
    )
    require(
        policy["authorization_effect"] == prior.EFFECT
        and policy["trusted_runtime_approval"] is None,
        "planning cannot grant runtime authority",
    )
    require(
        policy["accepted_generic_runtime_support"] == []
        and policy["admitted_specialization_support_sets"] == [],
        "unexecuted support advertised",
    )
    require(
        policy["status"] == "verified_candidate_pending_P9_G1_review",
        "contradictory successor status",
    )
    require(
        len(policy["exact_mutation_paths"]) == len(PATHS)
        and set(policy["exact_mutation_paths"]) == PATHS,
        "unauthorized mutation scope",
    )
    bindings = policy["artifact_bindings"]
    require(
        len(bindings) == len(PATHS - {POLICY, RECORD})
        and {r["path"] for r in bindings} == PATHS - {POLICY, RECORD},
        "successor binding roster drift",
    )
    for row in bindings:
        require(
            sha(safe_path(root, row["path"]).read_bytes()) == row["sha256"],
            "unauthorized content at permitted path: " + row["path"],
        )
    return policy


def blob_id(content):
    return hashlib.sha1(
        b"blob " + str(len(content)).encode() + b"\0" + content
    ).hexdigest()


def validate_tree(root, policy):
    """Read actual bytes, not index status; assume-unchanged cannot hide drift."""
    tree = git(root, "ls-tree", "-r", "-z", prior.CHECKPOINT).split(b"\0")
    baseline = {}
    for item in filter(None, tree):
        header, raw_path = item.split(b"\t", 1)
        mode, kind, oid = header.decode().split()
        path = raw_path.decode()
        if prior.in_scope(path):
            require(kind == "blob", "unexpected protected Git object")
            baseline[path] = (mode, oid)
    count = 0
    for name, (mode, oid) in baseline.items():
        if name in PATHS:
            continue
        path = safe_path(root, name)
        require(blob_id(path.read_bytes()) == oid, "frozen bytes changed: " + name)
        actual_mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
        require(mode == actual_mode, "frozen mode changed: " + name)
        count += 1
    entries = set(
        filter(
            None,
            git(root, "ls-files", "--cached", "--others", "-z").decode().split("\0"),
        )
    )
    additions = {
        p
        for p in entries
        if prior.in_scope(p) and p not in baseline and not prior.generated(p)
    }
    require(
        additions <= PATHS,
        "unauthorized source/test/planning addition: " + str(sorted(additions - PATHS)),
    )
    for name in additions:
        safe_path(root, name)
    bindings = [
        {"path": name, "sha256": sha(safe_path(root, name).read_bytes())}
        for name in sorted({r["path"] for r in policy["artifact_bindings"]} | {RECORD})
    ]
    return {
        "protected_baseline_files": count,
        "current_artifact_digest": sha(canonical(bindings)),
    }


def dependency_closure(edges, start):
    result, active = set(), set()

    def visit(node):
        require(node not in active, "dependency cycle")
        if node in result:
            return
        require(node in edges or node == "P9-G1", "unresolved dependency: " + node)
        active.add(node)
        for child in edges.get(node, []):
            visit(child)
        active.remove(node)
        result.add(node)

    visit(start)
    return result


def validate_composition(support, expected):
    """Exact children/aliases plus dependency semantics, not population counts."""
    expected_children = {r["iteration_id"]: r for r in expected["child_iterations"]}
    children = support["child_iterations"]
    require(
        len(children) == len(expected_children)
        and {r["iteration_id"] for r in children} == set(expected_children),
        "required child missing or substituted",
    )
    for row in children:
        old = expected_children[row["iteration_id"]]
        require(
            row["parent_id"] == old["parent_id"]
            and row["evidence_alias_of"] == old["evidence_alias_of"],
            "forged child parent/evidence alias",
        )
        require(row["status"] == "planned_not_executed", "unexecuted child promoted")
    edges = {r["iteration_id"]: r["requires"] for r in support["dependency_edges"]}
    require(len(edges) == len(support["dependency_edges"]), "duplicate dependency")
    for key in edges:
        dependency_closure(edges, key)
    required_c = dependency_closure(
        {r["iteration_id"]: r["requires"] for r in expected["dependency_edges"]},
        "P9-G2[C_OS]",
    )
    c = dependency_closure(edges, "P9-G2[C_OS]")
    require(c == required_c, "C_OS prerequisites omitted or unrelated profile barrier")
    require(
        edges["P9-G3[C_OS]"] == ["P9-7.8-C_OS"]
        and edges["P9-7.8-C_OS"] == ["P9-G2[C_OS]"],
        "unrelated singleton G3 barrier",
    )
    require(
        support["accepted_generic_runtime_support"] == []
        and support["admitted_specialization_support_sets"] == [],
        "unexecuted support advertised",
    )
    for row in support["profiles"]:
        require(
            row["exact_accepted_profile_ids"] == []
            and row["current_support"] == "unsupported_not_implemented",
            "unexecuted exact identity advertised",
        )
    require(
        support["conditional_dependencies"] == expected["conditional_dependencies"],
        "optional completion condition drift",
    )
    mandatory = dependency_closure(edges, "P9-9.6")
    expected_mandatory = dependency_closure(
        {r["iteration_id"]: r["requires"] for r in expected["dependency_edges"]},
        "P9-9.6",
    )
    require(
        mandatory == expected_mandatory
        and "P9-9.1a" not in mandatory
        and "P9-9.1" not in mandatory,
        "mandatory lifecycle lost or optional completion universal",
    )
    return edges


def completion_gate(
    edges, evidence, *, evidence_scope, required_scope, advertised=(), handoff=()
):
    require(
        bool(required_scope) and evidence_scope == required_scope,
        "completion evidence belongs to a different exact profile scope",
    )
    selected = set(advertised) | set(handoff)
    require(selected <= OPTIONAL, "unknown completion capability")
    required = dependency_closure(edges, "P9-9.6") - {"P9-9.6", "P9-G1"}
    if selected:
        required |= dependency_closure(edges, "P9-9.1a") - {"P9-G1"}
    return {
        "held": not required <= set(evidence),
        "missing": sorted(required - set(evidence)),
        "scope": "synthetic_evidence_gate_not_runtime_authorization",
    }


def runtime_targets(authority, trusted_digest, *, release_id, predecessor_digest):
    """Future-policy component. The live planning caller has NO trusted digest.

    Tests supply an isolated approval fixture. A self-declared/rehashable record
    cannot install its own trust anchor; P9-1.9 must separately pin real approval.
    """
    require(
        trusted_digest is not None and authority is not None, "runtime authority absent"
    )
    require(
        digest_record(authority) == authority["record_digest"] == trusted_digest,
        "untrusted runtime authority",
    )
    require(
        authority["schema"] == "phase9_runtime_mutation_authority_v1"
        and authority["status"] == "accepted_by_user"
        and authority["P9_G1_accepted"] is True
        and authority["runtime_authorized"] is True,
        "runtime authority not accepted",
    )
    require(
        authority["release_id"] == release_id
        and authority["predecessor_policy_digest"] == predecessor_digest,
        "stale runtime predecessor",
    )
    rows = authority["targets"]
    require(
        rows and len({r["path"] for r in rows}) == len(rows),
        "duplicate/empty runtime target",
    )
    for row in rows:
        name = row["path"]
        parsed = PurePosixPath(name)
        require(
            str(parsed) == name
            and not parsed.is_absolute()
            and ".." not in parsed.parts,
            "unsafe runtime target",
        )
        if row["operation"] == "add":
            allowed = (
                bool(
                    re.fullmatch(
                        r"(?:src/pygrc/models/grc_(?:v4|9_v4)(?:_[a-z0-9_]+)?|tests/models/test_grc_(?:v4|9_v4)(?:_[a-z0-9_]+)?)\.py",
                        name,
                    )
                )
                or name.startswith("src/pygrc/models/grc_v4_assets/")
                or name
                in {
                    "tests/models/grcv4_conformance_harness.py",
                    "tests/models/grcv4_reference_oracles.py",
                }
            )
            require(
                allowed and row["before_sha256"] is None,
                "non-V4 or non-new runtime addition",
            )
        else:
            require(
                row["operation"] == "additive_integration"
                and name in {"src/pygrc/models/__init__.py", "pyproject.toml"}
                and isinstance(row["before_sha256"], str),
                "legacy mutation forbidden",
            )
        require(
            isinstance(row["after_sha256"], str) and len(row["after_sha256"]) == 64,
            "unbound runtime content",
        )
    return {r["path"]: r for r in rows}


def validate_runtime_change(row, before, after):
    require(
        sha(after) == row["after_sha256"]
        and (sha(before) if before is not None else None) == row["before_sha256"],
        "runtime target content mismatch",
    )
    if row["operation"] == "add":
        require(before is None, "runtime addition overwrites existing file")
    elif row["path"] == "pyproject.toml":
        old, new = tomllib.loads(before.decode()), tomllib.loads(after.decode())
        for field in [old, new]:
            extras = field.get("project", {}).get("optional-dependencies", {})
            extras.pop("v4", None)
            package = (
                field.get("tool", {}).get("setuptools", {}).get("package-data", {})
            )
            package.pop("pygrc.models.grc_v4_assets", None)
            if not package and "package-data" in field.get("tool", {}).get(
                "setuptools", {}
            ):
                del field["tool"]["setuptools"]["package-data"]
        require(old == new, "non-additive dependency integration")
    else:
        old, new = ast.parse(before), ast.parse(after)
        require(
            len(new.body) > len(old.body)
            and all(ast.dump(a) == ast.dump(b) for a, b in zip(old.body, new.body)),
            "legacy export prefix changed",
        )
        names = {n.id for n in ast.walk(old) if isinstance(n, ast.Name)} | {
            a.asname or a.name
            for n in ast.walk(old)
            if isinstance(n, (ast.Import, ast.ImportFrom))
            for a in n.names
        }
        for node in new.body[len(old.body) :]:
            require(
                isinstance(node, ast.ImportFrom)
                and node.module
                and re.fullmatch(r"grc_(?:v4|9_v4)(?:_[a-z0-9_]+)?", node.module)
                and node.level == 1,
                "unreviewed integration statement",
            )
            require(
                all(
                    a.name != "*" and (a.asname or a.name) not in names
                    for a in node.names
                ),
                "legacy export rebound",
            )
            names.update(a.asname or a.name for a in node.names)


def current_boundary(root):
    policy = validate_policy(root)
    tree = validate_tree(root, policy)
    support_path = PHASE + "tranche-1/P9-1.4-SupportAndDependencies.json"
    expected = json.loads(git(root, "show", f"{prior.CHECKPOINT}:{support_path}"))
    validate_composition(read(root / support_path), expected)
    record = read(safe_path(root, RECORD))
    require(
        record["baseline_commit"] == prior.CHECKPOINT
        and record["release_id"] == prior.RELEASE_ID
        and record["entry_request"] == "i think now you can do P9 1.7 and 1.8",
        "execution record predecessor/entry mismatch",
    )
    require(
        record["accepted_generic_runtime_support"] == []
        and record["admitted_specialization_support_sets"] == [],
        "execution record advertises unexecuted support",
    )
    require(
        record["schema"] == "phase9_separate_leaf_results_v1"
        and record["policy_digest"] == policy["record_digest"],
        "execution record binding mismatch",
    )
    require(
        record["runtime_authorized"] is False and record["P9_G1_accepted"] is False,
        "execution record promotes authority",
    )
    require(
        [r["iteration_id"] for r in record["iteration_results"]]
        == ["P9-1.7", "P9-1.8"],
        "separate leaf result omitted",
    )
    for row in record["iteration_results"]:
        require(
            row["reviewer_decision"] == "pending_user_review"
            and row["status"] in {"in_progress", "implemented_and_verified"},
            "unrecorded leaf acceptance",
        )
    return policy, tree
