"""Tranche 5 test-maintenance checks; preserve accepted scientific executions."""

import argparse
import ast
import json
import subprocess
import sys

import phase9_implementation_policy as p

ROOT = p.ROOT
BASE = "c61b37cee8b18e87836ea5a690f89ab743401690"
# These finite corrections have fresh focused execution in the handoff.
# The original tests and accepted execution records remain retrievable at BASE.
TEST_SOURCES = {
    "tests/models/test_grc_v4.py": (
        "718a1cb287b5f92ffb900bab4cda14b6b8b4148b28bad38010bd26353ab80edc",
        {
            "AuthoritativeMappedVectorTests.test_current_release_executes_published_request_and_exact_event_identity",
            "LifecycleCompositionAuditTests.test_mixed_reference_charge_lineage_and_continuation",
        },
    ),
    "tests/models/test_grc_v4_candidate_c.py": (
        "10d4d9f2f763803a6c6509389bc834f6e1756ee1a2e1c426a7ad94ba83e13392",
        {
            "_p941_loaded_sources",
            "CandidateCCaptureTests.test_namespace_packages_keep_local_paths_and_child_source_checks",
        },
    ),
    "tests/models/test_grc_v4_geometry.py": (
        "8e954cdf956e0b8aef585c948fc307c2466b9e2a83ac2f6933387297acf73004",
        {"CaptureIntegrityTests.test_capture_resets_observations_in_same_process"},
    ),
    "tests/models/test_grc_v4_lifecycle.py": (
        "3af96fc343d33f94dde2066c2092b21d1143a9fbf5fc6d13b68915c5ca7aa788",
        {"CandidateCOSOperationTests.test_capture_rejects_same_file_method_slot_substitution"},
    ),
}


def corrected_test_source(name, current=None):
    """Check exact corrections and every other AST body; return historical bytes."""
    digest, allowed = TEST_SOURCES[name]
    current = (ROOT / name).read_bytes() if current is None else current
    p.require(p.sha(current) == digest, "unreviewed test correction: " + name)
    original = p.git(ROOT, "show", BASE + ":" + name)

    def retained(tree):
        def prune(body, prefix=""):
            result = []
            for node in body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    qualified = prefix + node.name
                    if qualified in allowed:
                        continue
                    if isinstance(node, ast.ClassDef):
                        node.body = prune(node.body, qualified + ".")
                result.append(node)
            return result

        tree.body = prune(tree.body)
        return ast.dump(tree)

    p.require(
        retained(ast.parse(original)) == retained(ast.parse(current)),
        "test correction changed an unrelated body: " + name,
    )
    return original


def check_sources():
    p.git(ROOT, "merge-base", "--is-ancestor", BASE, "HEAD")
    changed = set(p.git(ROOT, "diff", "--name-only", BASE, "--", "src", "tests").decode().splitlines())
    p.require(changed == set(TEST_SOURCES), "regression correction exceeded test scope")
    p.require(
        not p.git(ROOT, "ls-files", "--others", "--exclude-standard", "--", "src", "tests").strip(),
        "unregistered runtime/test source",
    )
    for name in TEST_SOURCES:
        corrected_test_source(name)
    # Acceptance and scientific execution remain exact historical objects.
    for leaf in range(1, 5):
        for suffix in ("AuditFollowup.json", "ExecutionRecord.json", "Review.md"):
            name = p.PHASE + f"tranche-5/P9-5.{leaf}-" + suffix
            p.require((ROOT / name).read_bytes() == p.git(ROOT, "show", BASE + ":" + name),
                      "changed accepted leaf record: " + name)
    return {"runtime_changed": False, "corrected_test_files": sorted(TEST_SOURCES)}


def check():
    sources = check_sources()
    # Pressure the finite projection itself, without executing numerical tests.
    for name in TEST_SOURCES:
        try:
            corrected_test_source(name, (ROOT / name).read_bytes() + b"\n# unreviewed\n")
        except ValueError as exc:
            p.require("unreviewed test correction" in str(exc), "wrong projection rejection")
        else:
            raise ValueError("test correction admitted changed bytes")
    import verify_p948b_review as c_review

    reuse = c_review.capture_reuse()
    boundary = p.current_boundary(ROOT)
    sys.path.insert(0, str(ROOT / p.SCRIPTS))
    from test_phase9_g1_surfaces import status_only_check, acceptance_status_check

    status_only_check(ROOT)
    acceptance_status_check(ROOT)
    notebook = subprocess.run(
        [sys.executable, str(ROOT / p.SCRIPTS / "run_phase9_notebook.py"), "--status-only"],
        cwd=ROOT, text=True, capture_output=True,
    )
    p.require(notebook.returncode == 0, notebook.stdout + notebook.stderr)
    p.require(p.current_boundary(ROOT) == boundary, "publication changed during check")
    return {
        "status": "passed", "accepted_tranche_5_subject": BASE, **sources,
        "accepted_C_capture_subject": reuse["original_subject"],
        "test_projection_negative_controls": 4,
        "API_notebook_browser_status": "passed",
        "scientific_tests_rerun": 0,
        "A_OS_G2_accepted": False, "G3_accepted": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(check()))
