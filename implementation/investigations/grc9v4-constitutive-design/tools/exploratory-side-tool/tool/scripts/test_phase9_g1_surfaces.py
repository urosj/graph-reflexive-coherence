#!/usr/bin/env python3
"""Accepted permission, exact accepted conformance scope, and preserved negative subjects."""

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


def status_only_check(root):
    """Lean notebook mode must omit pressure, not turn stale evidence green."""
    notebook = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
    query = next(c for c in notebook["cells"] if c["id"] == "query-status")
    calls = []

    def stale_pressure(*args):
        calls.append(args)
        raise ValueError("recorded pressure subject is stale")

    namespace = {
        "Path": Path, "PHASE9_REPO_ROOT": root, "repo_root": root,
        "PHASE9_STATUS_ONLY": True,
        "verification_status": api.verification_status,
        "pressure_projection": stale_pressure,
    }
    code = compile("".join(query["source"]), "phase9_verification.ipynb:query-status", "exec")
    exec(code, namespace)
    require = api._policy(root).require
    require(namespace["phase9_status"] == api.verification_status(root)
            and namespace["phase9_status"]["current_boundary"] == "passed"
            and "P9-4.9.1a" in namespace["phase9_status"]["dependency_ready_leaves"]
            and "P9-7.2a" in namespace["phase9_status"]["next_gate"]
            and namespace["phase9_pressure"] is None and not calls,
            "status-only mode queried or promoted pressure evidence")
    namespace["PHASE9_STATUS_ONLY"] = False
    try:
        exec(code, namespace)
    except ValueError as exc:
        require(str(exc) == "recorded pressure subject is stale" and len(calls) == 1
                and namespace["phase9_pressure"] is None,
                "full notebook retained stale pressure")
    else:
        raise AssertionError("full notebook must still reject stale pressure")


def acceptance_status_check(root):
    """Current API/browser identity and fail-closed cleanup, without replay."""
    policy = api._policy(root)
    status = api.verification_status(root)
    require = policy.require
    # Feed the actual API payload to the shipped browser validator, not only a
    # synthetic JS fixture; readiness drift must fail this cross-surface check.
    browser_status = subprocess.run(
        [str(managed_node()), "--input-type=module", "-e",
         "import { verifiedStatus } from './verification.js'; "
         "let raw=''; for await (const chunk of process.stdin) raw+=chunk; "
         "console.log(JSON.stringify(await verifiedStatus(JSON.parse(raw))));"],
        cwd=TOOL / "phase9-web", input=json.dumps(status),
        capture_output=True, text=True, env=tool_environment(), check=True,
    )
    require(json.loads(browser_status.stdout) == status,
            "actual browser/API status differs")
    require(status["g2_acceptance"]["G2_accepted"] is True
            and status["g2_acceptance"]["G3_accepted"] is False
            and status["g2_acceptance"]["tranche_4_status"] == "closed"
            and status["accepted_generic_runtime_support"] == policy.accepted_g2(root)["accepted_generic_runtime_support"],
            "accepted G2 projection differs")
    require(set(policy.LIFECYCLE_LEAVES | policy.MIGRATION_LEAVES) <= set(status["dependency_ready_leaves"])
            and {"tests/models/test_grc_v4_generic_lifecycle.py", "src/pygrc/models/grc_v4_migration.py", "tests/models/test_grc_v4_migration.py"} <= set(status["permitted_runtime_paths"])
            and "C-to-A positive migration remains pending" in status["next_gate"]
            and not {"P9-7.2a-A_OS", "P9-7.2b-A_PC"} & set(status["dependency_ready_leaves"]),
            "7.1/7.2a permission omitted a child or opened a generic event")
    boundary = policy.current_boundary(root)
    with patch.object(api, "_policy", return_value=policy), patch.object(
        policy, "current_boundary", side_effect=[boundary, ValueError("changed during read")]
    ):
        held = api.verification_status(root)
    require(held["current_boundary"] == "failed_closed"
            and held["accepted_generic_runtime_support"] == []
            and "g2_acceptance" not in held, "held status retained current G2 support")


def checks(root):
    status_only_check(root)
    acceptance_status_check(root)
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
        status["dependency_ready_leaves"] == ["P9-2.1","P9-2.2","P9-2.3","P9-2.4","P9-2.5","P9-2.6","P9-3.1","P9-3.2","P9-3.3","P9-3.4","P9-3.5","P9-4.1","P9-4.2","P9-4.3","P9-4.4","P9-4.5","P9-4.6","P9-4.7a","P9-4.7b","P9-4.9.1","P9-4.9.1a","P9-4.9.2","P9-4.9.3","P9-5.1","P9-5.2","P9-5.3","P9-5.4","P9-6.1a","P9-6.1b","P9-6.1c","P9-6.2a","P9-6.2b","P9-6.2c","P9-6.3a","P9-6.3b","P9-6.3c","P9-6.4a","P9-6.4b","P9-6.4c","P9-6.4d","P9-6.5","P9-7.1","P9-7.1-A_CI","P9-7.1-A_CI_PC","P9-7.1-A_OS","P9-7.1-A_PC","P9-7.1-A_RG2b","P9-7.1-C_CI","P9-7.1-C_CI_PC","P9-7.1-C_OS","P9-7.1-C_PC","P9-7.1-C_RG2b","P9-7.2a","P9-7.2a-A_CIPC_PC","P9-7.2a-A_C_DROP","P9-7.2a-A_C_NH","P9-7.2a-A_C_PC","P9-7.2a-A_NH_NH","P9-7.2a-A_NH_PC","P9-7.2a-A_PC_CIPC","P9-7.2a-A_PC_NH","P9-7.2a-C_CIPC_PC","P9-7.2a-C_NH_NH","P9-7.2a-C_NH_PC","P9-7.2a-C_OS-NH-NH","P9-7.2a-C_OS-UNSUPPORTED","P9-7.2a-C_PC_CIPC","P9-7.2a-C_PC_NH","P9-7.2a-C_TO_A_UNRESOLVED","P9-7.2b-C_OS-MAPPED","P9-7.3-C_OS","P9-7.4-C_OS","P9-7.5-C_OS","P9-7.6-C_OS"]
        and status["harness_acceptance"]["record_digest"] == policy.HARNESS_ACCEPTANCE_DIGEST
        and status["harness_acceptance"]["accepted_iterations"] == ["P9-2.5"]
        and status["geometry_acceptance"]["record_digest"] == policy.GEOMETRY_ACCEPTANCE_DIGEST
        and status["geometry_acceptance"]["accepted_iterations"] == ["P9-3.1"]
        and status["stage_acceptance"]["record_digest"] == policy.STAGE_ACCEPTANCE_DIGEST
        and status["stage_acceptance"]["accepted_iterations"] == ["P9-3.2"]
        and status["resource_acceptance"]["record_digest"] == policy.RESOURCE_ACCEPTANCE_DIGEST
        and status["resource_acceptance"]["accepted_iterations"] == ["P9-3.3"]
        and status["preservation_acceptance"]["accepted_iterations"] == ["P9-3.5"]
        and status["reference_transport_acceptance"]["accepted_iterations"] == ["P9-4.1"]
        and status["c_current_acceptance"]["accepted_iterations"] == ["P9-4.2"]
        and status["c_controls_acceptance"]["accepted_iterations"] == ["P9-4.3"]
        and status["c_controls_acceptance"]["record_digest"] == policy.CONTROLS_ACCEPTANCE_DIGEST
        and status["os_pass_acceptance"]["record_digest"] == policy.OS_PASS_ACCEPTANCE_DIGEST
        and status["os_pass_acceptance"]["accepted_iterations"] == ["P9-4.4"]
        and status["os_operations_acceptance"]["record_digest"] == policy.OPERATIONS_ACCEPTANCE_DIGEST
        and status["os_operations_acceptance"]["accepted_iterations"] == ["P9-4.5"]
        and status["lifecycle_batch_authorization"]["record_digest"] == policy.LIFECYCLE_BATCH_DIGEST
        and status["lifecycle_batch_authorization"]["audit_status"] == "findings_closed_after_correction"
        and status["specification_correction"]["record_digest"] == policy.SPECIFICATION_CORRECTION_DIGEST
        and status["specification_correction"]["release_id"] == policy.CORRECTED_RELEASE_ID
        and status["lifecycle_batch_authorization"]["execution_order"] == ["P9-4.7a", "P9-4.7b"]
        and status["reference_transport_acceptance"]["record_digest"] == policy.REFERENCE_ACCEPTANCE_DIGEST
        and status["c_current_acceptance"]["record_digest"] == policy.CURRENT_ACCEPTANCE_DIGEST
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
        and len(status["permitted_runtime_paths"]) == 43
        and "tests/models/grcv4_conformance_harness.py" in status["permitted_runtime_paths"]
        and "tests/models/grcv4_reference_oracles.py" in status["permitted_runtime_paths"]
        and "pyproject.toml" in status["permitted_runtime_paths"]
        and "src/pygrc/models/__init__.py" in status["permitted_runtime_paths"]
        and "src/pygrc/models/grc_v4_candidate_a.py"
        in status["permitted_runtime_paths"]
        and "tests/models/test_grc_v4_candidate_a.py" in status["permitted_runtime_paths"]
        and {"P9-5.4", "P9-6.1a", "P9-6.1b"} <= set(status["dependency_ready_leaves"])
        and "P9-6.1c" in status["dependency_ready_leaves"]
        and {"src/pygrc/models/grc_v4_ci.py", "tests/models/test_grc_v4_ci.py"} <= set(status["permitted_runtime_paths"])
        and {"P9-7.1", "P9-7.1-A_OS", "P9-7.1-C_RG2b", "P9-7.1-A_CI_PC"} <= set(status["dependency_ready_leaves"])
        and "P9-7.2a-A_OS" not in status["dependency_ready_leaves"],
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
        status["accepted_generic_runtime_support"] == policy.accepted_g2(root)["accepted_generic_runtime_support"]
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
                and "implementation_scope" not in held
                and "preservation_acceptance" not in held
                and "reference_transport_acceptance" not in held
                and "c_current_acceptance" not in held
                and "c_controls_acceptance" not in held
                and "os_pass_acceptance" not in held
                and "os_operations_acceptance" not in held
                and "lifecycle_batch_authorization" not in held
                and "specification_correction" not in held,
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
        "runtime_support": status["accepted_generic_runtime_support"],
    }
    require(output["notebook"] == status, "notebook/API identity differs")
    (TOOL / "generated/phase9-verification/g1-surface-evidence.json").write_bytes(
        policy.canonical(output) + b"\n"
    )
    print(
        "PHASE9_G1_SURFACES_PASS API_notebook_identity=byte_exact negative_candidate=rejected P9_G1=accepted runtime_support=accepted_exact_C_OS_singleton"
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
