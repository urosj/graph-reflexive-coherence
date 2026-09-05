"""Accepted P9-G1 scope; implementation integrity is not runtime conformance."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import tomllib

_HERE = Path(__file__).resolve().parent
_old = _HERE / "phase9_policy.py"
if (
    hashlib.sha256(_old.read_bytes()).hexdigest()
    != "c5a1ccb063b97a9a0b8525bf4a48b248aa783e2a3cac4a37403bbbd24596cf83"
):
    raise ValueError("accepted P9-1.7/P9-1.8 checker changed")
_spec = importlib.util.spec_from_file_location("p918_accepted_policy", _old)
planning = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(planning)
prior = planning.prior
ROOT, PHASE, HERE, INV, SIDE, SCRIPTS = (
    getattr(planning, n) for n in ["ROOT", "PHASE", "HERE", "INV", "SIDE", "SCRIPTS"]
)
require, read, sha, canonical, git, safe_path, digest_record = (
    getattr(planning, n)
    for n in [
        "require",
        "read",
        "sha",
        "canonical",
        "git",
        "safe_path",
        "digest_record",
    ]
)
BASELINE = "6e0a507c0fd7e0758392514acce5e79312a2069c"
APPROVAL = PHASE + "tranche-1/P9-1.9-G1Acceptance.json"
APPROVAL_DIGEST = "cd2c52f30477e1042bb903bd0553da237ddccc9cad373afecc1a84e4e0b37ea2"
POLICY = HERE + "Phase9ImplementationBoundary.json"
RECORD = PHASE + "tranche-1/P9-1.9-ExecutionRecord.json"
WORK = PHASE + "runtime/RuntimeWorkManifest.json"
GENERATED = SIDE + "tool/generated/phase9-verification/"
REPORT_SCHEMA = "phase9_G1_pressure_results_v1"
REPORT_FILE = "g1-pressure-results.json"
RECEIPT_SCHEMA = "phase9_verified_receipt_v3"
RECEIPT_FILE = "verification-v3.json"
PATHS = {
    APPROVAL,
    POLICY,
    RECORD,
    WORK,
    HERE + "phase9_implementation_policy.py",
    HERE + "audit_phase9_implementation.py",
    HERE + "test_phase9_g1.py",
    HERE + "inputs/P9-1.9-G1-Acceptance-And-Scoped-Authorization-Pressure-Guide.md",
    PHASE + "tranche-1/P9-1.9-G1Review.md",
    "implementation/Phase-9-GRCV4-ImplementationPlan.md",
    "implementation/ImplementationPhases.md",
    "implementation/Phase-9-GRCV4-ImplementationChecklist.md",
    SIDE + "GRCV4ExploratorySideToolImplementationPlan.md",
    SIDE + "GRCV4ExploratorySideToolImplementationChecklist.md",
    SIDE + "docs/Phase9VerificationGuide.md",
    SCRIPTS + "active_phase.py",
    SCRIPTS + "run.py",
    SCRIPTS + "verify_iteration9.py",
    SCRIPTS + "test_phase9_surfaces.py",
    SCRIPTS + "test_phase9_g1_surfaces.py",
    SCRIPTS + "run_phase9_notebook.py",
    SIDE + "tool/src/grcv4_explorer/phase9_verification.py",
    SIDE + "tool/notebooks/phase9_verification.ipynb",
    SIDE + "tool/phase9-web/index.html",
    SIDE + "tool/phase9-web/verification.js",
    SIDE + "tool/phase9-web/verification.test.mjs",
    SIDE + "tool/phase9-web/browser.spec.mjs",
}


def acceptance(root):
    prior.ancestor(root, BASELINE)
    value = read(safe_path(root, APPROVAL))
    require(
        value["record_digest"] == digest_record(value) == APPROVAL_DIGEST,
        "untrusted P9-G1 acceptance",
    )
    require(
        value["baseline_commit"] == BASELINE
        and value["release_id"] == prior.RELEASE_ID,
        "stale P9-G1 release or predecessor",
    )
    for row in value["review_bindings"]:
        require(
            prior.git_exact(root, BASELINE, row["path"]) == row["sha256"],
            "accepted review binding changed",
        )
    return value


def baseline_files(root):
    result = {}
    for item in filter(None, git(root, "ls-tree", "-r", "-z", BASELINE).split(b"\0")):
        header, name = item.split(b"\t", 1)
        mode, kind, oid = header.decode().split()
        name = name.decode()
        if prior.in_scope(name):
            require(kind == "blob", "unsupported protected object")
            result[name] = (mode, oid)
    return result


def integration(name, before, after):
    """Only optional reviewed dependencies/package data or lazy V4 exports."""
    if name == "pyproject.toml":
        old, new = tomllib.loads(before.decode()), tomllib.loads(after.decode())
        extras = new.get("project", {}).get("optional-dependencies", {}).get("v4", [])
        require(
            isinstance(extras, list)
            and all(
                isinstance(s, str)
                and re.fullmatch(
                    r"(?:numpy|rfc8785|jsonschema)(?:(?:==|!=|~=|<=|>=|<|>)[0-9][A-Za-z0-9.,<>=!~*+-]*)?",
                    s,
                )
                for s in extras
            ),
            "unreviewed V4 dependency",
        )
        for value in [old, new]:
            value.get("project", {}).get("optional-dependencies", {}).pop("v4", None)
            package = (
                value.get("tool", {}).get("setuptools", {}).get("package-data", {})
            )
            data = package.pop("pygrc.models.grc_v4_assets", [])
            require(
                isinstance(data, list)
                and set(data)
                <= {
                    "*.json",
                    "*.sha256",
                    "asset-index.json",
                    "grc-v4-contract-schema.json",
                    "grc-v4-specification-release.json",
                    "grc-v4-specification-release.sha256",
                },
                "unreviewed package data",
            )
            if not package:
                value.get("tool", {}).get("setuptools", {}).pop("package-data", None)
        require(old == new, "non-additive dependency integration")
    else:
        old, new = ast.parse(before), ast.parse(after)
        require(
            len(new.body) == len(old.body) + 1
            and all(ast.dump(a) == ast.dump(b) for a, b in zip(old.body, new.body)),
            "legacy export prefix changed",
        )
        # No eager dependency on optional V4 packages when importing older families.
        expected = ast.parse(
            'def __getattr__(name):\n    if name == "GRCV4":\n        from .grc_v4 import GRCV4\n        return GRCV4\n    raise AttributeError(name)\n'
        ).body[0]
        require(
            ast.dump(new.body[-1]) == ast.dump(expected),
            "unreviewed or eager V4 export",
        )


def leaf_permissions(root):
    """Readiness from accepted dependencies, not a work record's green flag.

    Only G1 has been accepted at this transition. Later leaf acceptances must
    be consumed through the existing controlled successor/review process.
    """
    support = read(
        safe_path(root, PHASE + "tranche-1/P9-1.4-SupportAndDependencies.json")
    )
    crosswalk = read(safe_path(root, PHASE + "tranche-1/P9-1.1-SourceCrosswalk.json"))
    ownership = read(
        safe_path(root, PHASE + "tranche-1/P9-1.5-OwnershipAndLegacyBaseline.json")
    )
    ready = sorted(
        r["iteration_id"]
        for r in support["dependency_edges"]
        if r["requires"] and set(r["requires"]) <= {"P9-G1"}
    )
    owners = {}
    for module in ownership["modules"]:
        leaves = {
            leaf
            for group in module["source_groups"]
            for leaf in crosswalk["groups"][group]["implementation_iterations"]
        }
        if module["module_id"] == "grc_v4_codec":
            leaves = {"P9-2.2", "P9-2.3", "P9-2.6"}
        for field in ["path", "test_path"]:
            owners[module[field]] = leaves
    for name in [
        "tests/models/grcv4_conformance_harness.py",
        "tests/models/grcv4_reference_oracles.py",
    ]:
        owners[name] = {"P9-2.5"}
    for row in read(safe_path(root, APPROVAL))["runtime_targets"]:
        if row["path"].startswith("src/pygrc/models/grc_v4_assets/"):
            owners[row["path"]] = {"P9-2.2", "P9-2.6"}
        elif row["operation"] == "additive_integration":
            owners[row["path"]] = {"P9-2.6"}
    return ready, owners


def work_entries(root, approval):
    value = read(safe_path(root, WORK))
    require(
        set(value)
        == {
            "schema",
            "approval_digest",
            "release_id",
            "entries",
            "accepted_generic_runtime_support",
            "admitted_specialization_support_sets",
            "claim_ceiling",
            "record_digest",
        },
        "work manifest cannot add authority",
    )
    require(
        value["schema"] == "phase9_runtime_work_manifest_v1"
        and value["approval_digest"] == APPROVAL_DIGEST
        and value["release_id"] == prior.RELEASE_ID
        and value["record_digest"] == digest_record(value),
        "stale work manifest",
    )
    require(
        value["accepted_generic_runtime_support"] == []
        and value["admitted_specialization_support_sets"] == [],
        "work manifest cannot grant conformance",
    )
    targets = {r["path"]: r for r in approval["runtime_targets"]}
    checklist = git(
        root,
        "show",
        f"{BASELINE}:implementation/Phase-9-GRCV4-ImplementationChecklist.md",
    ).decode()
    leaves = set(
        re.findall(r"P9-(?:[2-9]|10)\.\d+(?:[a-zA-Z]|-[A-Za-z0-9_-]+)?", checklist)
    )
    rows = value["entries"]
    require(len({r["path"] for r in rows}) == len(rows), "duplicate work target")
    result = {}
    ready, owners = leaf_permissions(root)
    for row in rows:
        require(
            set(row) == {"path", "sha256", "iteration_id"},
            "work entry cannot supply authority",
        )
        name, leaf = row["path"], row["iteration_id"]
        require(leaf in leaves, "unregistered work iteration")
        require(
            not leaf.startswith(("P9-8.", "P9-9.")),
            "specialization requires accepted P9-G3",
        )
        if name in targets:
            require(
                targets[name]["requires_gate"] == "P9-G1",
                "specialization requires accepted P9-G3",
            )
            require(
                leaf in owners.get(name, set()),
                "runtime target belongs to a different owning leaf",
            )
        require(leaf in ready, "owning leaf entry dependencies are not accepted")
        path = safe_path(root, name)
        require(
            not path.stat().st_mode & stat.S_IXUSR, "unapproved executable runtime mode"
        )
        content = path.read_bytes()
        require(sha(content) == row["sha256"], "work content binding mismatch")
        if name in targets:
            target = targets[name]
            require(
                target["requires_gate"] == "P9-G1",
                "specialization requires accepted P9-G3",
            )
            if target["operation"] == "additive_integration":
                before = git(root, "show", f"{BASELINE}:{name}")
                require(
                    sha(before) == target["before_sha256"], "integration baseline drift"
                )
                integration(name, before, content)
            elif name.endswith(".py"):
                ast.parse(content)
            if name.startswith("src/pygrc/models/grc_v4_assets/"):
                filename = Path(name).name
                if filename in {
                    "grc-v4-contract-schema.json",
                    "grc-v4-specification-release.json",
                    "grc-v4-specification-release.sha256",
                }:
                    require(
                        content == safe_path(root, "specs/" + filename).read_bytes(),
                        "packaged accepted asset differs",
                    )
        else:
            tranche = leaf.split("-")[1].split(".")[0]
            records = {
                PHASE + f"tranche-{tranche}/{leaf}-ExecutionRecord.json",
                PHASE + f"tranche-{tranche}/{leaf}-Review.md",
            }
            evidence = re.fullmatch(
                re.escape(PHASE + f"evidence/{leaf}/")
                + r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}/([^/]+)",
                name,
            )
            require(
                name in records
                or (
                    evidence
                    and evidence[1] in approval["execution_policy"]["evidence_files"]
                ),
                "unapproved runtime or evidence target: " + name,
            )
            if name.endswith("-ExecutionRecord.json"):
                record = json.loads(content)
                require(
                    record["iteration_id"] == leaf
                    and record["release_id"] == prior.RELEASE_ID,
                    "execution record subject mismatch",
                )
                require(
                    record["accepted_generic_runtime_support"] == []
                    and record["admitted_specialization_support_sets"] == [],
                    "execution record cannot grant conformance",
                )
        result[name] = row
    return result


def current_boundary(root):
    approval = acceptance(root)
    policy = read(safe_path(root, POLICY))
    require(
        set(policy)
        == {
            "schema",
            "active_phase",
            "baseline_commit",
            "approval_digest",
            "release_id",
            "artifact_bindings",
            "record_digest",
        },
        "unsupported implementation policy fields",
    )
    require(
        policy["schema"] == "phase9_implementation_boundary_v1"
        and policy["active_phase"] == "implementation"
        and policy["baseline_commit"] == BASELINE
        and policy["approval_digest"] == APPROVAL_DIGEST
        and policy["release_id"] == prior.RELEASE_ID
        and policy["record_digest"] == digest_record(policy),
        "implementation policy binding drift",
    )
    rows = policy["artifact_bindings"]
    bound = PATHS - {POLICY, WORK}
    require(
        len(rows) == len(bound) and {r["path"] for r in rows} == bound,
        "implementation maintenance roster drift",
    )
    for row in rows:
        require(
            sha(safe_path(root, row["path"]).read_bytes()) == row["sha256"],
            "implementation maintenance binding drift: " + row["path"],
        )
    work = work_entries(root, approval)
    # G1 grants creation/update, not deletion/rename of published runtime work.
    # Published evidence (including failed runs) is append-only, not replaceable
    # by removing a manifest row or staging its deletion out of the index.
    runtime_names = {
        r["path"] for r in approval["runtime_targets"] if r["before_sha256"] is None
    }
    for item in filter(None, git(root, "ls-tree", "-r", "-z", "HEAD").split(b"\0")):
        header, raw_name = item.split(b"\t", 1)
        name = raw_name.decode()
        if name in runtime_names or name.startswith(PHASE + "evidence/"):
            require(
                name in work and (root / name).is_file(),
                "published runtime/evidence deletion or rename forbidden",
            )
            if name.startswith(PHASE + "evidence/"):
                oid = header.decode().split()[2]
                require(
                    planning.blob_id(safe_path(root, name).read_bytes()) == oid,
                    "published run evidence is immutable",
                )
    baseline = baseline_files(root)
    frozen = 0
    for name, (mode, oid) in baseline.items():
        if name in PATHS or name in work:
            continue
        path = safe_path(root, name)
        require(
            planning.blob_id(path.read_bytes()) == oid, "frozen bytes changed: " + name
        )
        actual_mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
        require(actual_mode == mode, "frozen mode changed: " + name)
        frozen += 1
    entries = set(
        filter(
            None,
            git(root, "ls-files", "--cached", "--others", "-z").decode().split("\0"),
        )
    )
    additions = {
        n
        for n in entries
        if prior.in_scope(n) and n not in baseline and not prior.generated(n)
    }
    require(
        additions <= PATHS | set(work),
        "unauthorized source/test/planning addition: "
        + str(sorted(additions - PATHS - set(work))),
    )
    for name in PATHS:
        path = safe_path(root, name)
        require(not path.stat().st_mode & stat.S_IXUSR, "maintenance mode drift")
    record = read(safe_path(root, RECORD))
    require(
        record["approval_digest"] == APPROVAL_DIGEST
        and record["P9_G1_accepted"] is True
        and record["runtime_authorized"] is True
        and record["accepted_generic_runtime_support"] == []
        and record["admitted_specialization_support_sets"] == [],
        "G1 record authority drift",
    )
    names = PATHS | set(work)
    return policy, {
        "protected_baseline_files": frozen,
        "current_artifact_digest": sha(
            canonical(
                [
                    {"path": n, "sha256": sha(safe_path(root, n).read_bytes())}
                    for n in sorted(names)
                ]
            )
        ),
        "registered_runtime_files": len(work),
    }
