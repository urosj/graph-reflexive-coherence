"""Read-only implementation-governance status; NOT a forensic claim query."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess


def _policy(root):
    path = root / "implementation/phase-9-grcv4/verification/phase9_policy.py"
    successor = path.with_name("phase9_implementation_policy.py")
    if successor.exists():
        path = successor
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
    recorded = None
    if hasattr(module, "recorded_acceptance"):
        payload["schema"] = "phase9_governance_status_v2"
        try:
            recorded = module.recorded_acceptance(root)
            payload.update(
                P9_G1_accepted=True, approval_digest=recorded["record_digest"]
            )
        except (
            ValueError,
            KeyError,
            OSError,
            TypeError,
            subprocess.CalledProcessError,
        ):
            pass  # No authenticated decision is available; do not infer acceptance.
        payload["handoff_evidence"] = module.handoff_status(root)
    try:
        policy, tree = module.current_boundary(root)
        payload["runtime_authority_state"] = "explicit_planning_authority_runtime_false"
        implementation = policy["active_phase"] == "implementation"
        if implementation:
            approval = module.acceptance(root)
            ready, owners = module.leaf_permissions(root)
            payload.update(
                schema="phase9_governance_status_v2",
                runtime_authorized=True,
                P9_G1_accepted=True,
                runtime_authority_state="accepted_P9_G1_bounded_implementation_not_conformance",
                approval_digest=approval["record_digest"],
                foundation_acceptance={
                    "record_digest": module.accepted_foundation(root)["record_digest"],
                    "accepted_iterations": ["P9-2.1", "P9-2.2"],
                    "path": module.FOUNDATION,
                },
                request_acceptance={
                    "record_digest": module.accepted_requests(root)["record_digest"],
                    "accepted_iterations": ["P9-2.3"],
                    "path": module.REQUEST_ACCEPTANCE,
                },
                result_acceptance={
                    "record_digest": module.accepted_results(root)["record_digest"],
                    "accepted_iterations": ["P9-2.4"],
                    "path": module.RESULT_ACCEPTANCE,
                },
                harness_acceptance={
                    "record_digest": module.accepted_harness(root)["record_digest"],
                    "accepted_iterations": ["P9-2.5"],
                    "path": module.HARNESS_ACCEPTANCE,
                },
                integration_acceptance={
                    "record_digest": module.accepted_integration(root)["record_digest"],
                    "accepted_iterations": ["P9-2.6"],
                    "path": module.INTEGRATION_ACCEPTANCE,
                },
                geometry_acceptance={
                    "record_digest": module.accepted_geometry(root)["record_digest"],
                    "accepted_iterations": ["P9-3.1"],
                    "path": module.GEOMETRY_ACCEPTANCE,
                },
                stage_acceptance={
                    "record_digest": module.accepted_stages(root)["record_digest"],
                    "accepted_iterations": ["P9-3.2"],
                    "path": module.STAGE_ACCEPTANCE,
                },
                resource_acceptance={
                    "record_digest": module.accepted_resources(root)["record_digest"],
                    "accepted_iterations": ["P9-3.3"],
                    "path": module.RESOURCE_ACCEPTANCE,
                },
                numerical_pressure_acceptance={
                    "record_digest": module.accepted_numerical_pressure(root)["record_digest"],
                    "accepted_iterations": ["P9-3.4"],
                    "path": module.NUMERICAL_ACCEPTANCE,
                },
                preservation_acceptance={
                    "record_digest": module.accepted_preservation(root)["record_digest"],
                    "accepted_iterations": ["P9-3.5"],
                    "path": module.PRESERVATION_ACCEPTANCE,
                },
                reference_transport_acceptance={
                    "record_digest": module.accepted_reference_transport(root)["record_digest"],
                    "accepted_iterations": ["P9-4.1"],
                    "path": module.REFERENCE_ACCEPTANCE,
                },
                c_current_acceptance={
                    "record_digest": module.accepted_c_current(root)["record_digest"],
                    "accepted_iterations": ["P9-4.2"],
                    "path": module.CURRENT_ACCEPTANCE,
                },
                c_controls_acceptance={
                    "record_digest": module.accepted_c_controls(root)["record_digest"],
                    "accepted_iterations": ["P9-4.3"],
                    "path": module.CONTROLS_ACCEPTANCE,
                },
                implementation_scope=approval["runtime_targets"],
                dependency_ready_leaves=ready,
                permitted_runtime_paths=sorted(
                    r["path"]
                    for r in approval["runtime_targets"]
                    if r["requires_gate"] == "P9-G1" and set(ready) & owners[r["path"]]
                ),
                next_gate="P9-4.3 Candidate C derivative, covariance and zero-control verification; P9-G2 and P9-G3 remain pending",
                claim_ceiling="Accepted permission to implement reviewed V4 scope is not executed or accepted runtime conformance.",
            )
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
            / (
                "tool/generated/phase9-verification/"
                + getattr(module, "RECEIPT_FILE", "verification-v2.json")
            )
        )
        if path.is_file() and not path.is_symlink():
            try:
                receipt = module.read(path)
            except (ValueError, OSError, TypeError):
                receipt = {}  # A broken execution cache does not revoke approval.
            if not isinstance(receipt, dict):
                receipt = {}
            if (
                receipt.get("schema")
                == getattr(module, "RECEIPT_SCHEMA", "phase9_verified_receipt_v2")
                and receipt.get("status") == "passed"
                and receipt.get("scope") == "historical_current_and_pressure"
                and receipt.get("policy_digest") == policy["record_digest"]
                and receipt.get("tree") == tree
                and receipt.get("runtime_authorized") is implementation
                and receipt.get("P9_G1_accepted") is implementation
                and (
                    not implementation
                    or receipt.get("approval_digest") == module.APPROVAL_DIGEST
                )
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
        if recorded is not None:
            module.require(
                module.recorded_acceptance(root) == recorded,
                "acceptance changed during read",
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
        payload["runtime_authorized"] = False
        # Recheck the decision even when current work is held. Never equate a
        # current-tree/evidence failure with the user withdrawing acceptance.
        try:
            recorded = (
                module.recorded_acceptance(root)
                if hasattr(module, "recorded_acceptance")
                else None
            )
        except (
            ValueError,
            KeyError,
            OSError,
            TypeError,
            subprocess.CalledProcessError,
        ):
            recorded = None
        payload["P9_G1_accepted"] = recorded is not None
        payload["runtime_authority_state"] = (
            "accepted_P9_G1_current_work_held"
            if recorded is not None
            else "unknown_or_unavailable_permission_withheld"
        )
        payload.pop("implementation_scope", None)
        if recorded is not None:
            payload["approval_digest"] = recorded["record_digest"]
        else:
            payload.pop("approval_digest", None)
        payload.pop("dependency_ready_leaves", None)
        payload.pop("foundation_acceptance", None)
        payload.pop("request_acceptance", None)
        payload.pop("result_acceptance", None)
        payload.pop("harness_acceptance", None)
        payload.pop("integration_acceptance", None)
        payload.pop("geometry_acceptance", None)
        payload.pop("stage_acceptance", None)
        payload.pop("resource_acceptance", None)
        payload.pop("numerical_pressure_acceptance", None)
        payload.pop("preservation_acceptance", None)
        payload.pop("reference_transport_acceptance", None)
        payload.pop("c_current_acceptance", None)
        payload.pop("c_controls_acceptance", None)
        payload.pop("permitted_runtime_paths", None)
        payload.pop("source_meaning", None)
        payload.pop("tree", None)
        payload.pop("recorded_receipt_digest", None)
        payload.update(source_refs=[], iterations=[], policy_digest=None)
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
        root
        / module.SIDE
        / (
            "tool/generated/phase9-verification/"
            + getattr(module, "REPORT_FILE", "pressure-results.json")
        )
    )
    report = module.read(path)
    module.require(
        report["schema"]
        == getattr(module, "REPORT_SCHEMA", "phase9_successor_pressure_results_v2")
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
