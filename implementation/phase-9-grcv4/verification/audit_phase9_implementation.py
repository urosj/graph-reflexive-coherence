#!/usr/bin/env python3
"""Verify accepted P9-G1 scope; retain planning and historical checks as history."""

import argparse
from pathlib import Path
import shutil
import sys
import tempfile

import phase9_implementation_policy as policy


def predecessor_checks(root, commands):
    """Run the unmodified accepted V2 verifier on its exact committed subject."""
    with tempfile.TemporaryDirectory(prefix="grcv4-p919-predecessor-") as scratch:
        checkout = Path(scratch) / "repository"
        run = policy.prior.run_logged
        run(
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
            "P9_G1_predecessor_clone",
            commands,
        )
        run(
            ["git", "checkout", "--quiet", "--detach", policy.BASELINE],
            checkout,
            "P9_G1_predecessor_checkout",
            commands,
        )
        (checkout / ".venv").symlink_to(
            Path(sys.prefix).resolve(), target_is_directory=True
        )
        with (checkout / ".git/info/exclude").open("a") as stream:
            stream.write("\n/.venv\n")
        for relative in ["tool/web/node_modules", "tool/.tooling", "tool/.cache"]:
            original, link = (
                root / policy.SIDE / relative,
                checkout / policy.SIDE / relative,
            )
            if original.exists():
                # The historical ignore rule exempts contents, not a symlink
                # occupying the directory path itself. Keep real directories.
                link.mkdir(parents=True, exist_ok=True)
                for child in original.iterdir():
                    (link / child.name).symlink_to(
                        child, target_is_directory=child.is_dir()
                    )
        run(
            [sys.executable, str(checkout / policy.HERE / "audit_phase9_successor.py")],
            checkout,
            "accepted_P9_1_6_through_1_8_replay",
            commands,
        )
        # Preserve exact raw predecessor evidence outside the disposable checkout.
        destination = root / policy.GENERATED / "accepted-predecessor"
        destination.mkdir(parents=True, exist_ok=True)
        for name in [
            "verification-v2.json",
            "pressure-results.json",
            "historical-evidence.json",
            "surface-evidence.json",
        ]:
            shutil.copyfile(checkout / policy.GENERATED / name, destination / name)


def verify(root, boundary_only=False):
    boundary, tree = policy.current_boundary(root)
    commands = []
    policy.prior.run_logged(
        [
            sys.executable,
            str(root / policy.PARENT_RELEASE_BUILDER),
            "--check",
        ],
        root,
        "current_accepted_receipt_parent_release",
        commands,
    )
    if not boundary_only:
        predecessor_checks(root, commands)
        for label, script in [
            ("P9492_parent_authority_surfaces", policy.SCRIPTS + "test_p9492_parents.py"),
            ("P9_G1_authority_pressure", policy.HERE + "test_phase9_g1.py"),
            ("P9_G1_API_notebook", policy.SCRIPTS + "test_phase9_g1_surfaces.py"),
        ]:
            policy.prior.run_logged(
                [sys.executable, str(root / script)], root, label, commands
            )
        # The accepted parent run belongs to its immutable Git subject. Shared
        # source changes are now checked by P9-4.9.1's focused successor record.
        policy.parent_runtime_evidence(root)
        policy.prior.run_logged(
            [sys.executable, str(root / policy.HERE / "verify_p9491_facade.py"), "--check"],
            root, "P9491_retained_facade_evidence_current_inputs", commands,
        )
        report = policy.read(root / policy.GENERATED / policy.REPORT_FILE)
        policy.require(
            report["policy_digest"] == boundary["record_digest"]
            and report["tree"] == tree
            and report["report_digest"] == policy.digest_record(report, "report_digest")
            and report["failed"] == 0,
            "G1 pressure evidence mismatch",
        )
    policy.require(
        policy.current_boundary(root) == (boundary, tree),
        "verification inputs changed during execution",
    )
    result = {
        "schema": policy.RECEIPT_SCHEMA,
        "status": "passed",
        "scope": "current_boundary_only"
        if boundary_only
        else "historical_current_and_pressure",
        "policy_digest": boundary["record_digest"],
        "approval_digest": policy.APPROVAL_DIGEST,
        "tree": tree,
        "historical_revision": policy.prior.HISTORICAL,
        "accepted_planning_revision": policy.BASELINE,
        "release_id": policy.current_parent_release(root),
        "predecessor_release_id": policy.CORRECTED_RELEASE_ID,
        "runtime_authorized": True,
        "P9_G1_accepted": True,
        "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
        "commands": commands,
        "handoff_evidence": policy.handoff_status(root),
        "claim_ceiling": "accepted_implementation_permission_not_runtime_conformance",
    }
    result["receipt_digest"] = policy.digest_record(result, "receipt_digest")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boundary-only", action="store_true")
    args = parser.parse_args()
    result = verify(policy.ROOT, args.boundary_only)
    path = (
        policy.ROOT
        / policy.GENERATED
        / ("boundary-v3.json" if args.boundary_only else policy.RECEIPT_FILE)
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(policy.canonical(result) + b"\n")
    print(
        f"PHASE9_IMPLEMENTATION_VERIFICATION_PASS version=3 runtime_authorized=true P9_G1=accepted runtime_support=empty scope={result['scope']} handoff={result['handoff_evidence']['status']}"
    )
    if result["handoff_evidence"]["status"] != "verified":
        print("PHASE9_HANDOFF_WARNING " + result["handoff_evidence"]["detail"])


if __name__ == "__main__":
    main()
