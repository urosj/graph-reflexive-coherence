#!/usr/bin/env python3
"""Verify the real Phase 9 API, executable notebook and read-only browser UX."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch
import urllib.request

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer import phase9_verification as api  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


def require(condition, message):
    if not condition:
        raise ValueError(message)


def api_checks(root):
    live = api.verification_status(root)
    require(live["current_boundary"] == "passed", f"live API held: {live.get('error')}")
    require(
        live["runtime_authorized"] is False and live["P9_G1_accepted"] is False,
        "API promotes authority",
    )
    require(
        [r["iteration_id"] for r in live["iterations"]] == ["P9-1.7", "P9-1.8"],
        "missing separate leaves",
    )
    require(
        live["accepted_generic_runtime_support"] == []
        and live["admitted_specialization_support_sets"] == [],
        "unexecuted support advertised",
    )
    module = api._policy(root)
    boundary, tree = module.current_boundary(root)
    with patch.object(api, "_policy", return_value=module):
        # Inject failures at the API boundary; do not modify accepted source bytes.
        for error in [
            ValueError("forged source binding"),
            KeyError("missing authority"),
            subprocess.CalledProcessError(1, "git"),
        ]:
            with patch.object(module, "current_boundary", side_effect=error):
                held = api.verification_status(root)
                require(
                    held["current_boundary"] == "failed_closed"
                    and held["recorded_full_verification"] == "not_current",
                    "API failed to close",
                )

        # Only the disposable recorded-receipt path is redirected. The real
        # current boundary and source checks still execute against this checkout.
        with tempfile.TemporaryDirectory(prefix="grcv4-p918-cache-") as scratch:
            relative = Path(scratch).relative_to("/")
            module.SIDE = "/" + str(relative) + "/"
            receipt_path = (
                root
                / module.SIDE
                / "tool/generated/phase9-verification/verification-v2.json"
            )
            receipt_path.parent.mkdir(parents=True)
            missing = api.verification_status(root)
            require(
                missing["current_boundary"] == "passed"
                and missing["recorded_full_verification"] == "not_current",
                "missing receipt promoted",
            )
            value = {
                "schema": "phase9_verified_receipt_v2",
                "status": "passed",
                "scope": "historical_current_and_pressure",
                "policy_digest": boundary["record_digest"],
                "tree": tree,
                "runtime_authorized": False,
                "P9_G1_accepted": False,
            }
            value["receipt_digest"] = module.digest_record(value, "receipt_digest")
            receipt_path.write_bytes(module.canonical(value))
            match = api.verification_status(root)
            require(
                match["recorded_full_verification"]
                == "recorded_pass_matching_current_inputs",
                "matching recorded receipt unavailable",
            )
            for key, item in [
                ("policy_digest", "0" * 64),
                ("tree", {}),
                ("status", "failed"),
                ("scope", "current_boundary_only"),
                ("runtime_authorized", True),
                ("receipt_digest", "0" * 64),
            ]:
                changed = deepcopy(value)
                changed[key] = item
                if key != "receipt_digest":
                    changed["receipt_digest"] = module.digest_record(
                        changed, "receipt_digest"
                    )
                receipt_path.write_bytes(module.canonical(changed))
                require(
                    api.verification_status(root)["recorded_full_verification"]
                    == "not_current",
                    "stale/forged receipt promoted: " + key,
                )
            receipt_path.write_bytes(b"not JSON")
            require(
                api.verification_status(root)["current_boundary"] == "failed_closed",
                "malformed receipt not held",
            )
    print(
        "PHASE9_API_PASS checks=13 current_bytes_rechecked=true runtime_authorized=false"
    )


def browser_checks(root):
    environment = tool_environment()
    with tempfile.TemporaryFile(mode="w+") as terminal:
        server = subprocess.Popen(
            [sys.executable, str(TOOL / "scripts/serve_phase9.py"), "--port", "0"],
            cwd=root,
            stdout=terminal,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            deadline = time.monotonic() + 15
            url = None
            while time.monotonic() < deadline:
                terminal.seek(0)
                lines = terminal.read().splitlines()
                if lines and lines[0].startswith("PHASE9_VERIFICATION_SERVE "):
                    url = lines[0].split()[1]
                    break
                if server.poll() is not None:
                    raise RuntimeError("Phase 9 server failed: " + "\n".join(lines))
                time.sleep(0.1)
            require(url is not None, "Phase 9 server startup timeout")
            with urllib.request.urlopen(url, timeout=5) as response:
                require(response.status == 200, "Phase 9 page unavailable")
            environment["PHASE9_TEST_URL"] = url
            subprocess.run(
                [
                    str(managed_node()),
                    str(TOOL / "web/node_modules/@playwright/test/cli.js"),
                    "test",
                    "--config",
                    str(TOOL / "phase9-web/playwright.config.mjs"),
                ],
                cwd=TOOL / "phase9-web",
                env=environment,
                check=True,
            )
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
    print(
        "PHASE9_BROWSER_PASS projects=desktop,mobile screenshots=4 API_download_identity=byte_exact"
    )


def cross_surface_checks(root):
    """Real mutation -> rejection -> passing assertion -> API/notebook output."""
    sys.path.insert(0, str(root / "implementation/phase-9-grcv4/verification"))
    import phase9_policy as policy
    from pressure_evidence import protected_manifest
    from test_phase9_pressure import changed

    before = protected_manifest(root)
    negative = api.pressure_projection(root, "normal_entry_forbidden_source")
    positive = api.pressure_projection(root, "future_explicit_approval_exact_targets")
    require(
        negative["candidate_decision"] == "rejected"
        and negative["assertion_result"] == "passed",
        "green negative promoted at API",
    )
    require(
        any(
            t.get("check") == "actual_subprocess"
            and t["exit_code"] != 0
            and "unauthorized source/test/planning addition" in t["stderr"]
            for t in negative["trace"]
        ),
        "negative projection lacks actual normal-entry rejection",
    )
    require(
        positive["candidate_decision"] == "admitted"
        and positive["historical_runtime_authorized"] is False
        and positive["project_effect"]["runtime_authorized"] is False,
        "future fixture and historical authority collapsed",
    )
    require(
        negative["source_meaning"]["specification_authority"] == "accepted_frozen"
        and negative["source_meaning"]["forensic_support_disposition"]
        == "indeterminate_requires_review"
        and negative["source_meaning"]["association_count"] == 152,
        "forensic/specification authority collapsed",
    )
    try:
        api.pressure_projection(root, "normal_entry_forbidden_source-unknown")
    except KeyError:
        pass
    else:
        raise ValueError("unknown exact probe was fuzzy resolved")
    with tempfile.TemporaryDirectory(prefix="grcv4-notebook-freshness-") as scratch:
        clone = Path(scratch) / "repository"
        subprocess.run(
            [
                "git",
                "clone",
                "--shared",
                "--quiet",
                "--no-checkout",
                str(root),
                str(clone),
            ],
            check=True,
        )
        policy.git(clone, "checkout", "--quiet", policy.prior.CHECKPOINT)
        for name in policy.PATHS:
            path = clone / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((root / name).read_bytes())
        (clone / ".venv").symlink_to(
            Path(sys.prefix).resolve(), target_is_directory=True
        )
        raw_name = (
            policy.SIDE + "tool/generated/phase9-verification/pressure-results.json"
        )
        target = clone / raw_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((root / raw_name).read_bytes())
        cells = [
            c
            for c in json.loads(
                (TOOL / "notebooks/phase9_verification.ipynb").read_text()
            )["cells"]
            if c["cell_type"] == "code"
        ]
        namespace = {"PHASE9_REPO_ROOT": clone}
        for i, cell in enumerate(cells):
            exec(
                compile(
                    "".join(cell["source"]),
                    f"phase9_verification.ipynb:cell-{i + 1}",
                    "exec",
                ),
                namespace,
            )
        require(
            namespace["phase9_pressure"] == negative,
            "notebook does not project actual API negative identically",
        )
        snapshot = protected_manifest(clone)
        # Same live kernel, fresh query after actual authority/source mutation.
        with changed(
            clone, "specs/grc-v4-spec.md", b"# stale source after first cell run\n"
        ):
            exec(
                compile(
                    "".join(cells[-1]["source"]), "phase9-notebook-query-rerun", "exec"
                ),
                namespace,
            )
            require(
                namespace["phase9_status"]["current_boundary"] == "failed_closed"
                and namespace["phase9_pressure"] is None,
                "notebook retained earlier success after source mutation",
            )
            # A leftover checkout variable must not override the new selection.
            namespace["PHASE9_REPO_ROOT"] = root
            exec(
                compile(
                    "".join(cells[-1]["source"]),
                    "phase9-notebook-switch-checkout",
                    "exec",
                ),
                namespace,
            )
            require(
                namespace["phase9_pressure"] == negative,
                "notebook ignored changed checkout selection",
            )
        stale = {
            "phase9_status": {"current_boundary": "passed"},
            "phase9_pressure": positive,
        }
        try:
            exec(
                compile(
                    "".join(cells[-1]["source"]), "phase9-out-of-order-cell", "exec"
                ),
                stale,
            )
        except NameError:
            require(
                stale["phase9_status"] is None and stale["phase9_pressure"] is None,
                "out-of-order cell retained misleading output",
            )
        else:
            raise ValueError("query cell unexpectedly ran without initialization")
        require(
            protected_manifest(clone) == snapshot,
            "notebook changed protected fixture bytes",
        )
    require(
        protected_manifest(root) == before,
        "projection checks changed live protected files",
    )
    output = {
        "schema": "phase9_cross_surface_evidence_v1",
        "status": "passed",
        "negative_projection": negative,
        "positive_projection": positive,
        "checks": [
            "actual_normal_entry_rejection",
            "negative_assertion_not_candidate_admission",
            "synthetic_future_positive",
            "specification_and_forensic_support_preserved",
            "unknown_ID_rejected",
            "notebook_exact_projection",
            "notebook_freshness_after_mutation",
            "selected_checkout_rebound",
            "out_of_order_clears_stale_output",
            "protected_before_after_unchanged",
        ],
        "protected_pre_post": {
            "before_sha256": policy.sha(policy.canonical(before)),
            "after_sha256": policy.sha(policy.canonical(protected_manifest(root))),
            "unchanged": True,
        },
        "runtime_authorized": False,
        "P9_G1_accepted": False,
    }
    destination = TOOL / "generated/phase9-verification/surface-evidence.json"
    destination.write_bytes(policy.canonical(output) + b"\n")
    print(
        "PHASE9_CROSS_SURFACE_PASS checks=10 negative_candidate=rejected assertion=passed runtime_authorized=false"
    )


def main():
    from active_phase import PHASE9_AUDITOR
    if PHASE9_AUDITOR.endswith("audit_phase9_implementation.py"):
        from test_phase9_g1_surfaces import main as g1_main
        return g1_main()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    if Path(sys.prefix).resolve() != (root / ".venv").resolve():
        raise RuntimeError("use the existing repository .venv")
    if args.browser:
        browser_checks(root)
    else:
        api_checks(root)
        cross_surface_checks(root)
        subprocess.run(
            [sys.executable, str(TOOL / "scripts/run_phase9_notebook.py")],
            cwd=root,
            check=True,
        )
        node = subprocess.run(
            [str(managed_node()), str(TOOL / "phase9-web/verification.test.mjs")],
            cwd=TOOL / "phase9-web",
            env=tool_environment(),
            check=True,
            capture_output=True,
            text=True,
        )
        print(node.stdout, end="")
        require(
            "# tests 8\n" in node.stdout
            and "# pass 8\n" in node.stdout
            and "# fail 0\n" in node.stdout,
            "Node did not execute all eight assertions",
        )
        print(
            "PHASE9_SURFACES_PASS API_checks=13 cross_surface_checks=10 notebook_cells=2 node_tests=8 runtime_authorized=false P9_G1=pending"
        )


if __name__ == "__main__":
    main()
