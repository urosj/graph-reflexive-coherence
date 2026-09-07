#!/usr/bin/env python3
"""Accepted permission, empty conformance sets, and preserved negative subjects."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
from unittest.mock import patch

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer import phase9_verification as api  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


def checks(root):
    policy = api._policy(root)
    status = api.verification_status(root)
    require = policy.require
    notebook = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
    query = next(c for c in notebook["cells"] if c["id"] == "query-status")

    def notebook_query():
        namespace = {
            "Path": Path,
            "PHASE9_REPO_ROOT": root,
            "repo_root": root,
            "verification_status": api.verification_status,
            "pressure_projection": api.pressure_projection,
        }
        exec(
            compile(
                "".join(query["source"]),
                "phase9_verification.ipynb:query-status",
                "exec",
            ),
            namespace,
        )
        return namespace

    require(
        status["dependency_ready_leaves"] == ["P9-2.1", "P9-2.2", "P9-2.3", "P9-2.4", "P9-2.5", "P9-2.6", "P9-3.1", "P9-3.2", "P9-3.3", "P9-3.4", "P9-3.5"]
        and status["harness_acceptance"]["record_digest"] == policy.HARNESS_ACCEPTANCE_DIGEST
        and status["harness_acceptance"]["accepted_iterations"] == ["P9-2.5"]
        and status["geometry_acceptance"]["record_digest"] == policy.GEOMETRY_ACCEPTANCE_DIGEST
        and status["geometry_acceptance"]["accepted_iterations"] == ["P9-3.1"]
        and status["stage_acceptance"]["record_digest"] == policy.STAGE_ACCEPTANCE_DIGEST
        and status["stage_acceptance"]["accepted_iterations"] == ["P9-3.2"]
        and status["resource_acceptance"]["record_digest"] == policy.RESOURCE_ACCEPTANCE_DIGEST
        and status["resource_acceptance"]["accepted_iterations"] == ["P9-3.3"]
        and status["numerical_pressure_acceptance"]["record_digest"] == policy.NUMERICAL_ACCEPTANCE_DIGEST
        and status["numerical_pressure_acceptance"]["accepted_iterations"] == ["P9-3.4"]
        and status["integration_acceptance"]["record_digest"] == policy.INTEGRATION_ACCEPTANCE_DIGEST
        and status["integration_acceptance"]["accepted_iterations"] == ["P9-2.6"]
        and set(['src/pygrc/models/grc_v4_geometry.py', 'src/pygrc/models/grc_v4_transport.py', 'tests/models/test_grc_v4_geometry.py', 'tests/models/test_grc_v4_transport.py']) <= set(status["permitted_runtime_paths"])
        and status["result_acceptance"]["record_digest"] == policy.RESULT_ACCEPTANCE_DIGEST
        and status["result_acceptance"]["accepted_iterations"] == ["P9-2.4"]
        and status["request_acceptance"]["record_digest"] == policy.REQUEST_ACCEPTANCE_DIGEST
        and status["request_acceptance"]["accepted_iterations"] == ["P9-2.3"]
        and status["foundation_acceptance"]["record_digest"] == policy.FOUNDATION_DIGEST
        and status["foundation_acceptance"]["accepted_iterations"] == ["P9-2.1", "P9-2.2"]
        and len(status["permitted_runtime_paths"]) == 23
        and "tests/models/grcv4_conformance_harness.py" in status["permitted_runtime_paths"]
        and "tests/models/grcv4_reference_oracles.py" in status["permitted_runtime_paths"]
        and "pyproject.toml" in status["permitted_runtime_paths"]
        and "src/pygrc/models/__init__.py" in status["permitted_runtime_paths"]
        and "src/pygrc/models/grc_v4_candidate_a.py"
        not in status["permitted_runtime_paths"],
        "G1 bypassed generic leaf dependencies",
    )
    require(status["current_boundary"] == "passed", str(status.get("error")))
    require(
        status["P9_G1_accepted"] is True
        and status["runtime_authorized"] is True
        and status["approval_digest"] == policy.APPROVAL_DIGEST,
        "accepted G1 authority lost",
    )
    require(
        status["accepted_generic_runtime_support"] == []
        and status["admitted_specialization_support_sets"] == [],
        "G1 promoted conformance",
    )
    require(
        status["source_meaning"]["association_count"] == 152
        and status["source_meaning"]["pending_source_obligations"] == 15,
        "source meaning changed",
    )
    negative = api.pressure_projection(root, "normal_entry_forbidden_source")
    positive = api.pressure_projection(root, "accepted_G1_exact_targets")
    require(
        negative["candidate_decision"] == "rejected"
        and negative["assertion_result"] == "passed",
        "negative promoted",
    )
    require(
        positive["candidate_decision"] == "admitted"
        and positive["project_effect"]["runtime_authorized"] is False,
        "probe created authority",
    )
    try:
        api.pressure_projection(root, "accepted_G1_exact_targets-unknown")
    except KeyError:
        pass
    else:
        raise ValueError("unknown full ID resolved")
    with patch.object(api, "_policy", return_value=policy):
        for error in [ValueError("stale approval"), KeyError("missing acceptance")]:
            with patch.object(policy, "current_boundary", side_effect=error):
                held = api.verification_status(root)
                require(
                    held["current_boundary"] == "failed_closed"
                    and held["runtime_authorized"] is False
                    and held["P9_G1_accepted"] is True,
                    "current failure must hold work, not erase recorded acceptance",
                )
        with patch.object(
            policy, "recorded_acceptance", side_effect=ValueError("invalid acceptance")
        ):
            held = api.verification_status(root)
            require(
                not held["P9_G1_accepted"] and not held["runtime_authorized"],
                "invalid acceptance inferred",
            )
        # A failure after the first successful current check must revoke the
        # partially assembled positive payload, not leave true flags behind.
        current = policy.current_boundary(root)
        with patch.object(
            policy,
            "current_boundary",
            side_effect=[current, ValueError("changed during read")],
        ):
            held = api.verification_status(root)
            require(
                held["current_boundary"] == "failed_closed"
                and held["runtime_authorized"] is False
                and held["P9_G1_accepted"] is True
                and "implementation_scope" not in held,
                "API TOCTOU retained authority",
            )
        with tempfile.TemporaryDirectory(prefix="grcv4-g1-receipt-") as scratch:
            with patch.object(policy, "SIDE", scratch):
                destination = (
                    Path(scratch)
                    / "tool/generated/phase9-verification/verification-v3.json"
                )
                destination.parent.mkdir(parents=True)
                missing = api.verification_status(root)
                require(
                    missing["runtime_authorized"] is True
                    and missing["recorded_full_verification"] == "not_current",
                    "receipt confused with approval",
                )
                destination.write_bytes(b"not JSON")
                malformed = api.verification_status(root)
                require(
                    malformed["P9_G1_accepted"]
                    and malformed["runtime_authorized"]
                    and malformed["recorded_full_verification"] == "not_current",
                    "malformed cached execution revoked acceptance",
                )
                value = {
                    "schema": policy.RECEIPT_SCHEMA,
                    "status": "passed",
                    "scope": "historical_current_and_pressure",
                    "policy_digest": current[0]["record_digest"],
                    "tree": current[1],
                    "runtime_authorized": True,
                    "P9_G1_accepted": True,
                    "approval_digest": policy.APPROVAL_DIGEST,
                }
                value["receipt_digest"] = policy.digest_record(value, "receipt_digest")
                destination.write_bytes(policy.canonical(value))
                require(
                    api.verification_status(root)["recorded_full_verification"]
                    == "recorded_pass_matching_current_inputs",
                    "matching receipt lost",
                )
                for key, changed in [
                    ("approval_digest", "0" * 64),
                    ("tree", {}),
                    ("runtime_authorized", False),
                    ("schema", "phase9_verified_receipt_v2"),
                ]:
                    altered = deepcopy(value)
                    altered[key] = changed
                    altered["receipt_digest"] = policy.digest_record(
                        altered, "receipt_digest"
                    )
                    destination.write_bytes(policy.canonical(altered))
                    require(
                        api.verification_status(root)["recorded_full_verification"]
                        == "not_current",
                        "stale receipt promoted: " + key,
                    )
        with tempfile.TemporaryDirectory(prefix="grcv4-handoff-status-") as scratch:
            manifest = Path(scratch) / "manifest.json"
            bundle = Path(scratch) / "P9-G1-outputs.zip"
            published = root / policy.HERE / "handoff"
            shutil.copyfile(published / "P9-G1-manifest.json", manifest)
            check = policy._presentation.status
            with patch.object(
                policy, "handoff_status", side_effect=lambda r: check(r, manifest)
            ):
                for content, expected in [
                    (None, "unavailable"),
                    (b"corrupt ZIP", "invalid"),
                ]:
                    if content is not None:
                        bundle.write_bytes(content)
                    result = api.verification_status(root)
                    require(
                        result["handoff_evidence"]["status"] == expected,
                        "archive failure hidden",
                    )
                    require(
                        result["P9_G1_accepted"]
                        and result["runtime_authorized"]
                        and result["current_boundary"] == "passed",
                        "archive failure changed acceptance or permission",
                    )
                    require(
                        notebook_query()["phase9_status"] == result,
                        "notebook changed archive/acceptance meaning",
                    )
                shutil.copyfile(published / bundle.name, bundle)
                require(
                    api.verification_status(root)["handoff_evidence"]["status"]
                    == "verified",
                    "archive restoration not verified",
                )
                manifest.write_bytes(b"malformed manifest")
                result = api.verification_status(root)
                require(
                    result["handoff_evidence"]["status"] == "invalid"
                    and result["P9_G1_accepted"]
                    and result["runtime_authorized"],
                    "manifest failure changed acceptance",
                )
                manifest.unlink()
                result = api.verification_status(root)
                require(
                    result["handoff_evidence"]["status"] == "unavailable"
                    and result["P9_G1_accepted"]
                    and result["runtime_authorized"],
                    "missing manifest changed acceptance",
                )
    subprocess.run(
        [sys.executable, str(TOOL / "scripts/run_phase9_notebook.py")],
        cwd=root,
        check=True,
    )
    result = subprocess.run(
        [str(managed_node()), str(TOOL / "phase9-web/verification.test.mjs")],
        cwd=TOOL / "phase9-web",
        env=tool_environment(),
        check=True,
        capture_output=True,
        text=True,
    )
    print(result.stdout, end="")
    output = {
        "schema": "phase9_G1_surface_evidence_v1",
        "API": status,
        "negative_probe": negative,
        "accepted_scope_probe": positive,
        "notebook": json.loads(
            (TOOL / "generated/phase9-verification/notebook-status.json").read_text()
        ),
        "node_stdout": result.stdout,
        "runtime_support": [],
    }
    require(output["notebook"] == status, "notebook/API identity differs")
    (TOOL / "generated/phase9-verification/g1-surface-evidence.json").write_bytes(
        policy.canonical(output) + b"\n"
    )
    print(
        "PHASE9_G1_SURFACES_PASS API_notebook_identity=byte_exact negative_candidate=rejected P9_G1=accepted runtime_support=empty"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()
    root = repository_root()
    if Path(sys.prefix).resolve() != (root / ".venv").resolve():
        raise RuntimeError("use the existing .venv")
    if args.browser:
        from test_phase9_surfaces import browser_checks

        browser_checks(root)
    else:
        checks(root)


if __name__ == "__main__":
    main()
