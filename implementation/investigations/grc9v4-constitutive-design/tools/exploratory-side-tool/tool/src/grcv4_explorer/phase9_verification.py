"""Read-only implementation-governance status; NOT a forensic claim query."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess


def _policy(root):
    path = root / "implementation/phase-9-grcv4/verification/phase9_policy.py"
    spec = importlib.util.spec_from_file_location(
        "phase9_governance_status_policy", path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verification_status(repo_root: Path) -> dict:
    """Recheck current authority bytes; label historical execution as recorded.

    No tests, mutations or historical replay are triggered by this query.
    Missing/stale/malformed evidence is not a green result or runtime authority.
    """
    root = repo_root.resolve()
    module = _policy(root)
    payload = {
        "schema": "phase9_governance_status_v1",
        "output_class": "implementation_verification_status_not_forensic_trace",
        "runtime_authorized": False,
        "runtime_authority_state": "unknown_or_unavailable_permission_withheld",
        "P9_G1_accepted": False,
        "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
        "current_boundary": "failed_closed",
        "recorded_full_verification": "not_current",
        "policy_digest": None,
        "source_refs": [],
        "iterations": [],
        "next_gate": "P9-1.9 explicit user review; no runtime work yet",
        "claim_ceiling": "Current planning integrity and recorded tool execution are not scientific authority or runtime conformance.",
    }
    try:
        policy, tree = module.current_boundary(root)
        payload["runtime_authority_state"] = "explicit_planning_authority_runtime_false"
        cross = module.read(
            root / module.PHASE / "tranche-1/P9-1.1-SourceCrosswalk.json"
        )
        routing = module.read(
            root / module.PHASE / "tranche-1/P9-1.3-VerificationRouting.json"
        )
        payload["source_meaning"] = {
            "specification_authority": "accepted_frozen",
            "forensic_support_disposition": "indeterminate_requires_review",
            "association_count": sum(
                "indeterminate_requires_review" in r["accepted_claim_support_semantics"]
                for r in cross["contracts"]
            ),
            "association_denominator": len(cross["contracts"]),
            "pending_source_obligations": routing["summary"][
                "pending_runtime_or_scientific_evidence"
            ],
            "evidence_kind": "source_bound_planning_crosswalk_not_runtime_evidence",
            "source_bindings": [
                {"path": name, "sha256": module.sha((root / name).read_bytes())}
                for name in [
                    module.PHASE + "tranche-1/P9-1.1-SourceCrosswalk.json",
                    module.PHASE + "tranche-1/P9-1.3-VerificationRouting.json",
                ]
            ],
        }
        payload.update(
            current_boundary="passed", policy_digest=policy["record_digest"], tree=tree
        )
        payload["source_refs"] = [
            {"path": p, "sha256": module.sha(module.safe_path(root, p).read_bytes())}
            for p in [
                module.POLICY,
                module.prior.OPENING,
                "specs/grc-v4-specification-release.json",
                module.RECORD,
            ]
        ]
        record = module.read(root / module.RECORD)
        payload["iterations"] = [
            {
                "iteration_id": r["iteration_id"],
                "status": r["status"],
                "reviewer_decision": r["reviewer_decision"],
            }
            for r in record["iteration_results"]
        ]
        path = (
            root
            / module.SIDE
            / "tool/generated/phase9-verification/verification-v2.json"
        )
        if path.is_file() and not path.is_symlink():
            receipt = module.read(path)
            if (
                receipt.get("schema") == "phase9_verified_receipt_v2"
                and receipt.get("status") == "passed"
                and receipt.get("scope") == "historical_current_and_pressure"
                and receipt.get("policy_digest") == policy["record_digest"]
                and receipt.get("tree") == tree
                and receipt.get("runtime_authorized") is False
                and receipt.get("P9_G1_accepted") is False
                and receipt.get("receipt_digest")
                == module.digest_record(receipt, "receipt_digest")
            ):
                payload["recorded_full_verification"] = (
                    "recorded_pass_matching_current_inputs"
                )
                payload["recorded_receipt_digest"] = receipt["receipt_digest"]
        module.require(
            module.current_boundary(root) == (policy, tree),
            "API inputs changed during verification",
        )
    except (
        ValueError,
        KeyError,
        OSError,
        TypeError,
        subprocess.CalledProcessError,
    ) as error:
        payload["current_boundary"] = "failed_closed"
        payload["recorded_full_verification"] = "not_current"
        payload["error"] = str(error)
    payload["status_digest"] = module.digest_record(payload, "status_digest")
    return payload


def pressure_projection(repo_root: Path, case_id: str) -> dict:
    """Project one actual probe: harness success never changes its candidate.

    Recorded fixture admission is not live tree admission or user acceptance.
    Exact full IDs are required; unknown IDs are never replaced by neighbors.
    """
    root = repo_root.resolve()
    module = _policy(root)
    policy, tree = module.current_boundary(root)
    path = (
        root / module.SIDE / "tool/generated/phase9-verification/pressure-results.json"
    )
    report = module.read(path)
    module.require(
        report["schema"] == "phase9_successor_pressure_results_v2"
        and report["report_digest"] == module.digest_record(report, "report_digest"),
        "invalid pressure evidence digest or schema",
    )
    module.require(
        report["policy_digest"] == policy["record_digest"] and report["tree"] == tree,
        "recorded pressure subject is stale",
    )
    matches = [r for r in report["cases"] if r["case_id"] == case_id]
    if len(matches) != 1:
        raise KeyError("unknown or ambiguous exact probe ID: " + case_id)
    row = matches[0]
    module.require(
        row["candidate_decision"] in {"admitted", "rejected", "held", "unverifiable"}
        and row["assertion_result"] in {"passed", "failed"},
        "invalid probe decision",
    )
    module.require(
        row["project_effect"]
        == {
            "runtime_authorized": False,
            "P9_G1_accepted": False,
            "scientific_promotion": False,
        },
        "probe cannot promote live authority",
    )
    payload = {
        "schema": "phase9_pressure_projection_v1",
        "output_class": "isolated_probe_not_current_tree_admission",
        "case_id": case_id,
        "run_id": report["run_id"],
        "report_digest": report["report_digest"],
        "candidate_decision": row["candidate_decision"],
        "assertion_result": row["assertion_result"],
        "subject_scope": row["scope"],
        "evidence_kind": row["evidence_kind"],
        "actual_reason": row["actual_reason"],
        "intended_check_reached": row["intended_check_reached"],
        "project_effect": row["project_effect"],
        "authority": row["authority"],
        "base_fixture_identity": row["base_fixture_identity"],
        "protected_pre_post": row["protected_pre_post"],
        "trace": row["trace"],
        "source_meaning": verification_status(root).get("source_meaning"),
        "historical_runtime_authorized": False,
        "historical_subject": module.prior.HISTORICAL,
        "claim_ceiling": "A passed harness assertion is not candidate admission, live runtime permission, scientific support or P9-G1 acceptance.",
    }
    payload["projection_digest"] = module.digest_record(payload, "projection_digest")
    module.require(
        module.current_boundary(root) == (policy, tree),
        "probe projection inputs changed during verification",
    )
    return payload
