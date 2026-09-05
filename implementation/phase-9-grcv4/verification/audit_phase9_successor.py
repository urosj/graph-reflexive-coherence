#!/usr/bin/env python3
"""P9-1.7/P9-1.8 verification; acceptance and runtime remain separate gates."""

import argparse
import sys

import phase9_policy as policy
from pressure_evidence import summary


def require_same_subject(before, after):
    policy.require(before == after, "verification inputs changed during execution")


def historical_evidence(root, commands=None):
    """Actual historical sub-result, never an attestation of current bytes.

    The normal path supplies freshly executed checks. A standalone pressure
    run executes them if absent; malformed cached evidence is not repaired.
    """
    path = (
        root
        / policy.SIDE
        / "tool/generated/phase9-verification/historical-evidence.json"
    )
    if commands is None and not path.exists():
        commands = []
        policy.prior.historical_checks(root, commands)
    if commands is not None:
        history = [c for c in commands if c["label"].startswith("historical_audit_")]
        policy.require(
            len(history) == 4 and all(c["exit_code"] == 0 for c in history),
            "historical checks incomplete",
        )
        value = {
            "schema": "phase9_recorded_historical_evidence_v1",
            "historical_revision": policy.prior.HISTORICAL,
            "release_id": policy.prior.RELEASE_ID,
            "commands": history,
            "current_tree_attestation": False,
            "runtime_authorized": False,
        }
        value["evidence_digest"] = policy.digest_record(value, "evidence_digest")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(policy.canonical(value) + b"\n")
    value = policy.read(path)
    policy.require(
        value["schema"] == "phase9_recorded_historical_evidence_v1"
        and value["historical_revision"] == policy.prior.HISTORICAL
        and value["release_id"] == policy.prior.RELEASE_ID
        and value["evidence_digest"] == policy.digest_record(value, "evidence_digest"),
        "historical fixture evidence mismatch",
    )
    return value


def verify(root, boundary_only=False):
    boundary, tree = policy.current_boundary(root)
    commands = []
    script = policy.INV + "scripts/audit_grcv4_specification_release_acceptance.py"
    policy.prior.git_exact(root, policy.prior.ACCEPTANCE, script)
    policy.prior.run_logged(
        [
            sys.executable,
            str(root / script),
            "--audit-file",
            str(root / policy.prior.INPUT),
        ],
        root,
        "accepted_release",
        commands,
    )
    if not boundary_only:
        policy.prior.historical_checks(root, commands)
        historical_evidence(root, commands)
        for label, command in [
            (
                "source_and_architecture",
                [
                    sys.executable,
                    str(root / policy.PHASE / "tranche-1/audit_architecture_review.py"),
                    "--self-test",
                    "--check-rendering",
                ],
            ),
            (
                "successor_pressure",
                [sys.executable, str(root / policy.HERE / "test_phase9_pressure.py")],
            ),
            (
                "api_notebook",
                [
                    sys.executable,
                    str(root / policy.SCRIPTS / "test_phase9_surfaces.py"),
                ],
            ),
        ]:
            policy.prior.run_logged(command, root, label, commands)
        generated = (
            root
            / policy.SIDE
            / "tool/generated/phase9-verification/pressure-results.json"
        )
        policy.require(
            summary(policy.read(generated)) == policy.read(root / policy.RESULTS),
            "retained pressure results do not match actual execution",
        )
        pressure = policy.read(generated)
        policy.require(
            pressure["policy_digest"] == boundary["record_digest"]
            and pressure["tree"] == tree
            and pressure["report_digest"]
            == policy.digest_record(pressure, "report_digest"),
            "pressure run subject or digest mismatch",
        )
    after, current_tree = policy.current_boundary(root)
    require_same_subject((boundary, tree), (after, current_tree))
    result = {
        "schema": "phase9_verified_receipt_v2",
        "status": "passed",
        "scope": "current_boundary_only"
        if boundary_only
        else "historical_current_and_pressure",
        "policy_digest": boundary["record_digest"],
        "tree": tree,
        "historical_revision": policy.prior.HISTORICAL,
        "release_id": policy.prior.RELEASE_ID,
        "runtime_authorized": False,
        "P9_G1_accepted": False,
        "commands": commands,
        "claim_ceiling": "verification_candidate_not_runtime_conformance",
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
        / policy.SIDE
        / "tool/generated/phase9-verification"
        / ("boundary-v2.json" if args.boundary_only else "verification-v2.json")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(policy.canonical(result) + b"\n")
    print(
        f"PHASE9_{'CURRENT_BOUNDARY' if args.boundary_only else 'SUCCESSOR_VERIFICATION'}_PASS version=2 phase=implementation_planning runtime_authorized=false P9_G1=pending receipt={path.relative_to(policy.ROOT)}"
    )


if __name__ == "__main__":
    main()
