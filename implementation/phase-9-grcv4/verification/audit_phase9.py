#!/usr/bin/env python3
"""Verify Phase 9 planning and unchanged historical authority, not runtime support.

No flag authorizes implementation. A future P9-G1 successor must be explicitly
reviewed and supported by a new policy; this version fails closed on that state.
Historical checks execute unchanged in a temporary local clone, never against
the later planning tree and never with patched globals or bypassed assertions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PHASE = "implementation/phase-9-grcv4/"
HERE = PHASE + "verification/"
INV = "implementation/investigations/grc9v4-constitutive-design/"
SIDE = INV + "tools/exploratory-side-tool/"
SCRIPTS = SIDE + "tool/scripts/"
OPENING = "implementation/Phase-9-GRCV4-PhaseOpening.json"
POLICY = HERE + "Phase9VerificationBoundary.json"
RECORD = PHASE + "tranche-1/P9-1.6-ExecutionRecord.json"
REVIEW = PHASE + "tranche-1/P9-1.6-SuccessorVerification.md"
INPUT = HERE + "inputs/GRCV4-final-narrow-specification-acceptance-audit.md"
CHECKPOINT = "e0bfc216540ebd70a2aedf1a939b1677e84fb787"
OPENING_COMMIT = "7c772d36bd4cf12b4a444b7b954b74612de2926f"
HISTORICAL = "f1817b8cf41e439cbb18ad82dfab6b39a77ae43d"
MERGE = "e00a8844c045ac4338fa52afb6ab096420fb6161"
ACCEPTANCE = "935cc532c9c8e53f4fc26bc43e9e40401cdb2410"
RELEASE_ID = "grcv4-spec-release-sha256:9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f"
INPUT_SHA = "f136c8552e1c7ef59570c11b26d592430e42058a9d9994e75a09560fda84242e"
MUTABLE = {
    "implementation/Phase-9-GRCV4-ImplementationPlan.md",
    "implementation/Phase-9-GRCV4-ImplementationChecklist.md",
    SIDE + "GRCV4ExploratorySideToolImplementationPlan.md",
    SIDE + "GRCV4ExploratorySideToolImplementationChecklist.md",
    SCRIPTS + "run.py",
    SCRIPTS + "verify_iteration9.py",
    SCRIPTS + "active_phase.py",
    HERE + "audit_phase9.py",
    HERE + "test_phase9_dispatch.py",
    POLICY,
    RECORD,
    REVIEW,
    INPUT,
}
EFFECT = {
    "verification_maintenance_authorized": True,
    "P9_G1_accepted": False,
    "runtime_authorized": False,
    "source_tests_dependency_changes_authorized": False,
    "specification_mutation_authorized": False,
    "scientific_claim_promotion": False,
}
HISTORICAL_AUDITS = [
    "audit_grc9v4_d10_claim_topology.py",
    "audit_grc9v4_d10_1_preliminary_provenance.py",
    "audit_grc9v4_d10_2_full_provenance.py",
    "audit_grcv4_post_d10_specifications.py",
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f"nonfinite JSON constant: {value}")

    return json.loads(
        path.read_bytes(), object_pairs_hook=unique, parse_constant=invalid
    )


def safe_path(root, name):
    require(isinstance(name, str), "non-string repository path")
    relative = PurePosixPath(name)
    require(
        name
        and not relative.is_absolute()
        and ".." not in relative.parts
        and str(relative) == name,
        f"unsafe path: {name}",
    )
    path = root
    for part in relative.parts:
        path = path / part
        require(not path.is_symlink(), f"symlink at protected path: {name}")
    require(path.is_file(), f"missing protected file: {name}")
    return path


def git(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, check=True
    ).stdout


def ancestor(root, commit):
    require(
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=root,
            capture_output=True,
            check=False,
        ).returncode
        == 0,
        f"missing ancestor: {commit}",
    )


def git_exact(root, commit, path):
    expected = git(root, "show", f"{commit}:{path}")
    require(
        safe_path(root, path).read_bytes() == expected,
        f"immutable predecessor changed: {path}",
    )
    return sha(expected)


def validate_policy(root):
    for commit in [HISTORICAL, ACCEPTANCE, MERGE, OPENING_COMMIT, CHECKPOINT]:
        ancestor(root, commit)
    opening_sha = git_exact(root, OPENING_COMMIT, OPENING)
    opening = read(root / OPENING)
    require(
        opening["active_phase"] == "implementation_planning"
        and opening["authorization_effect"]["runtime_or_src_tests_change_authorized"]
        is False,
        "opening is not planning-only",
    )
    parents = git(root, "show", "-s", "--format=%P", MERGE).decode().split()
    closure = opening["specification_branch_closure"]
    require(
        parents == [closure["first_parent"], ACCEPTANCE]
        and closure["merge_commit"] == MERGE
        and closure["completed"] is True
        and closure["merge_strategy"] == "no_ff",
        "no-ff closure mismatch",
    )
    for key in ["predecessor_phase_boundary", "specification_acceptance"]:
        binding = opening[key]
        require(
            git_exact(root, ACCEPTANCE, binding["path"]) == binding["sha256"],
            f"opening binding drift: {key}",
        )
    require(
        opening["accepted_release"]["release_id"] == RELEASE_ID,
        "opening release mismatch",
    )
    policy = read(safe_path(root, POLICY))
    require(
        policy["schema"] == "phase9_verification_boundary_v1",
        "unsupported verification boundary",
    )
    require(
        policy["active_phase"] == "implementation_planning",
        "unsupported successor state: separate accepted P9-G1 policy required",
    )
    require(
        policy["status"] == "implemented_candidate_pending_P9_1_7_and_P9_1_8",
        "verification candidate status mismatch",
    )
    require(
        policy["authorization_effect"] == EFFECT,
        "planning policy cannot grant runtime authority",
    )
    require(
        policy["baseline_commit"] == CHECKPOINT
        and policy["historical_revision"] == HISTORICAL
        and policy["release_id"] == RELEASE_ID,
        "stale policy predecessor/release",
    )
    require(
        policy["opening_binding"] == {"path": OPENING, "sha256": opening_sha},
        "policy opening binding mismatch",
    )
    payload = {k: v for k, v in policy.items() if k != "record_digest"}
    require(
        policy["record_digest"] == sha(canonical(payload)), "policy digest mismatch"
    )
    paths = policy["exact_mutation_paths"]
    require(
        len(paths) == len(set(paths)) and set(paths) == MUTABLE,
        "mutation scope widened or incomplete",
    )
    require(
        policy["accepted_generic_runtime_support"] == []
        and policy["admitted_specialization_support_sets"] == [],
        "planning roster cannot advertise support",
    )
    bindings = policy["artifact_bindings"]
    require(
        len(bindings) == len(MUTABLE - {POLICY, RECORD})
        and {b["path"] for b in bindings} == MUTABLE - {POLICY, RECORD},
        "candidate binding roster mismatch",
    )
    for binding in bindings:
        require(
            sha(safe_path(root, binding["path"]).read_bytes()) == binding["sha256"],
            f"candidate bytes changed: {binding['path']}",
        )
    require(
        sha(safe_path(root, INPUT).read_bytes()) == INPUT_SHA,
        "acceptance audit input drift",
    )
    return policy


def in_scope(path):
    return path.startswith(("src/", "tests/", "specs/", PHASE, INV)) or path in {
        "pyproject.toml",
        "implementation/ImplementationPhases.md",
        OPENING,
        "implementation/Phase-9-GRCV4-ImplementationPlan.md",
        "implementation/Phase-9-GRCV4-ImplementationChecklist.md",
    }


def generated(path):
    # These are outputs of the existing tool, not an exception for source code.
    if path in {
        "src/pygrc.egg-info/" + name
        for name in [
            "PKG-INFO",
            "SOURCES.txt",
            "dependency_links.txt",
            "requires.txt",
            "top_level.txt",
        ]
    }:
        # Existing editable-install metadata, not executable source or the
        # authoritative dependency declaration. Do not exempt arbitrary files
        # under egg-info; pyproject.toml remains protected independently.
        return True
    if path.startswith(
        tuple(
            SIDE + p
            for p in [
                "tool/generated/",
                "tool/web/dist/",
                "tool/web/public/data/",
                "tool/web/node_modules/",
                "tool/.tooling/",
                "tool/.cache/",
            ]
        )
    ):
        return True
    parts = PurePosixPath(path).parts
    return "__pycache__" in parts and path.endswith(".pyc")


def validate_tree(root):
    changed = set(
        git(root, "diff", "--name-only", "-z", CHECKPOINT, "--").decode().split("\0")
    ) - {""}
    # Include ignored source/test additions; .gitignore must not conceal code.
    new = set(git(root, "ls-files", "--others", "-z").decode().split("\0")) - {""}
    scoped = {p for p in changed if in_scope(p)} | {
        p for p in new if in_scope(p) and not generated(p)
    }
    require(
        scoped <= MUTABLE,
        f"unauthorized planning-tree changes: {sorted(scoped - MUTABLE)}",
    )
    baseline = (
        git(
            root,
            "ls-tree",
            "-r",
            "--name-only",
            CHECKPOINT,
            "--",
            "specs",
            "src",
            "tests",
            PHASE,
            INV,
            "pyproject.toml",
            "implementation/ImplementationPhases.md",
            OPENING,
        )
        .decode()
        .splitlines()
    )
    count = 0
    for name in baseline:
        if name not in MUTABLE:
            safe_path(root, name)
            count += 1
    # Git comparison already checks all baseline file content/mode/deletion;
    # these explicit checks also reject symlinked parent directories.
    require(git(root, "diff", "--check") == b"", "diff whitespace errors")
    return {"scoped_changed_paths": sorted(scoped), "protected_baseline_files": count}


def validate_execution_record(root, policy):
    record = read(safe_path(root, RECORD))
    require(
        record["schema"] == "phase9_leaf_execution_record_v1"
        and record["iteration_id"] == "P9-1.6",
        "wrong iteration record",
    )
    require(
        record["baseline_commit"] == CHECKPOINT
        and record["release_id"] == RELEASE_ID
        and record["policy_digest"] == policy["record_digest"],
        "execution record binding drift",
    )
    require(
        record["runtime_authorized"] is False
        and record["gate_effect"] == "none_P9_G1_pending",
        "execution record promotes authority",
    )
    require(
        record["reviewer_decision"] == "pending_user_review"
        and record["P9_1_7_complete"] is False
        and record["P9_1_8_complete"] is False,
        "later iteration acceptance inferred",
    )
    require(
        record["status"]
        in {"implementation_in_progress", "implemented_and_verified_pending_review"},
        "unknown execution status",
    )
    require(
        len(record["changed_paths"]) == len(MUTABLE)
        and set(record["changed_paths"]) == MUTABLE,
        "execution scope mismatch",
    )
    require(
        record["entry_request"] == "you can now continue with P9-1.6",
        "entry authority mismatch",
    )


def run_logged(command, cwd, label, results):
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    completed = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, check=False, env=environment
    )
    result = {
        "label": label,
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    results.append(result)
    require(
        completed.returncode == 0,
        f"{label} failed (exit {completed.returncode}):\n{completed.stdout}\n{completed.stderr}",
    )
    terminal = completed.stdout.strip().splitlines()
    print(
        f"PHASE9_CHECK_PASS label={label} result={terminal[-1] if terminal else 'exit_0'}",
        flush=True,
    )


def historical_checks(root, results):
    # A local shared clone borrows only immutable Git objects. It has its own
    # index/HEAD/worktree, so the user's .git and worktree are never changed.
    with tempfile.TemporaryDirectory(prefix="grcv4-p916-historical-") as temporary:
        checkout = Path(temporary) / "repository"
        run_logged(
            [
                "git",
                "clone",
                "--shared",
                "--no-checkout",
                "--quiet",
                str(root),
                str(checkout),
            ],
            root,
            "historical_clone",
            results,
        )
        run_logged(
            ["git", "checkout", "--quiet", "--detach", HISTORICAL],
            checkout,
            "historical_checkout",
            results,
        )
        # Give the disposable repository the existing tested environment at
        # its normal location; no dependency installation or assertion bypass.
        (checkout / ".venv").symlink_to(
            Path(sys.prefix).resolve(), target_is_directory=True
        )
        # The historical .gitignore's directory-only .venv/ pattern does not
        # match a symlink. Ignore exactly this environment alias in the clone's
        # private metadata, never any source, spec, test, or authority path.
        with (checkout / ".git/info/exclude").open("a", encoding="utf-8") as stream:
            stream.write("\n/.venv\n")
        require(
            git(checkout, "rev-parse", "HEAD").decode().strip() == HISTORICAL,
            "historical checkout revision drift",
        )
        for name in HISTORICAL_AUDITS:
            path = INV + "scripts/" + name
            require(
                safe_path(checkout, path).read_bytes()
                == git(root, "show", f"{HISTORICAL}:{path}"),
                f"historical auditor byte drift: {name}",
            )
            run_logged(
                [sys.executable, str(checkout / path)],
                checkout,
                "historical_" + name,
                results,
            )
        require(
            git(checkout, "status", "--porcelain", "--untracked-files=normal") == b"",
            "historical audit mutated tracked/nonignored files",
        )


def verify(root, *, boundary_only=False):
    policy = validate_policy(root)
    tree = validate_tree(root)
    validate_execution_record(root, policy)
    # Execute only scripts already checked against immutable Git/content bindings.
    acceptance_script = INV + "scripts/audit_grcv4_specification_release_acceptance.py"
    git_exact(root, ACCEPTANCE, acceptance_script)
    results = []
    run_logged(
        [
            sys.executable,
            str(root / acceptance_script),
            "--audit-file",
            str(root / INPUT),
        ],
        root,
        "accepted_release",
        results,
    )
    if not boundary_only:
        historical_checks(root, results)
        run_logged(
            [
                sys.executable,
                str(root / PHASE / "tranche-1/audit_architecture_review.py"),
                "--self-test",
                "--check-rendering",
            ],
            root,
            "current_source_and_architecture",
            results,
        )
    return {
        "schema": "phase9_verification_receipt_v1",
        "status": "passed",
        "scope": "current_boundary_only"
        if boundary_only
        else "historical_and_current_planning",
        "policy_digest": policy["record_digest"],
        "code_head": git(root, "rev-parse", "HEAD").decode().strip(),
        "historical_revision": HISTORICAL,
        "release_id": RELEASE_ID,
        "runtime_authorized": False,
        "P9_G1": "pending",
        "P9_1_7": "pending",
        "P9_1_8": "pending",
        "tree": tree,
        "commands": results,
        "claim_ceiling": "verification_of_planning_and_frozen_authority_not_runtime_conformance",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--boundary-only",
        action="store_true",
        help="Current authority/byte checks only; not a full historical verification pass.",
    )
    args = parser.parse_args()
    receipt = verify(ROOT, boundary_only=args.boundary_only)
    destination = ROOT / SIDE / "tool/generated/phase9-verification"
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / (
        "boundary-receipt.json" if args.boundary_only else "verification-receipt.json"
    )
    path.write_bytes(
        json.dumps(receipt, indent=2, ensure_ascii=False, allow_nan=False).encode()
        + b"\n"
    )
    marker = (
        "PHASE9_CURRENT_BOUNDARY_PASS"
        if args.boundary_only
        else "PHASE9_SUCCESSOR_VERIFICATION_PASS"
    )
    print(
        f"{marker} phase=implementation_planning historical_revision={HISTORICAL} runtime_authorized=false P9_G1=pending P9_1_7=pending P9_1_8=pending receipt={path.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
