#!/usr/bin/env python3
"""Build the deterministic ET-C0 source and layout contract candidate."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]


def repository_root() -> Path:
    for candidate in SIDE_TOOL_ROOT.parents:
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "implementation/investigations/grc9v4-constitutive-design"
        ).is_dir():
            return candidate
    raise RuntimeError("cannot discover repository root")


REPO_ROOT = repository_root()
DECISIONS = (
    REPO_ROOT / "implementation/investigations/grc9v4-constitutive-design/decisions"
)
RECORDS = SIDE_TOOL_ROOT / "records"


def require_repository_venv() -> None:
    if Path(sys.prefix).resolve() != (REPO_ROOT / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


SOURCE_NAMES = (
    "D0TargetInheritanceAndClaimCeiling.json",
    "D1RetainedRepresentationOntologyAndCandidateAdmission.json",
    "D2FormationRetentionReleaseAndWriteInterface.json",
    "D3ContinuationRequirementsAndStructuralDomain.json",
    "D4GeometryMobilityAndTopologyOwnership.json",
    "D5DirectionalReadBack.json",
    "D6TotalCurrentClosure.json",
    "D7ClosedWriteReadLoop.json",
    "D4v2CandidateGeometryAndCarrierCompletion.json",
    "D5v2DirectionalReadBackCompletion.json",
    "D6v2UpdatedTotalCurrentClosure.json",
    "D7v2CandidateTransitionComparativeAdmission.json",
    "D7GGlobalMetricAndStructuralCultivationClosure.json",
    "D7Gv2GeometryParametricClosureAndFinalization.json",
    "D7GPostv2GraphHodgeTypeCorrection.json",
    "D8ABranchAppropriateStructuralTargetExtraction.json",
    "GeometryTemporalRealizationSuccessorCoupledImplicit.json",
    "D8BCoupledArchitectureLocalContinuationAnalysis.json",
    "GeometryTemporalRealizationSuccessorOperatorSplit.json",
    "GeometryTemporalRealizationSuccessorReconstructedGeometry.json",
    "GeometryTemporalRealizationSuccessorPersistentCarrier.json",
    "GeometryTemporalRealizationComparativeSynthesis.json",
    "GeometryTemporalRealizationHybridCoupledPersistentCarrier.json",
    "D9CompleteStepAndLifecycleContract.json",
    "D9ProfileStateLifecycleRegistry.json",
    "D9LifecycleCoverageMatrix.json",
    "D9ResidualDebtLedger.json",
    "D10DesignSynthesisAndSpecWritingDecision.json",
    "D10NormativeClaimTopology.json",
    "D10DebtClaimTransformationLedger.json",
    "D10SpecificationAuthorizationProfile.json",
    "D10_1PreliminarySubstrateProvenance.json",
    "D10_2FullSubstrateProvenanceAndPromotionAudit.json",
)

EXPECTED_STATUSES = {
    "D0TargetInheritanceAndClaimCeiling.json": "accepted",
    "D10_1PreliminarySubstrateProvenance.json": (
        "accepted_preliminary_bounded_substrate_provenance_separation"
    ),
}

EXPECTED_POPULATIONS = {
    "current_claims": 39,
    "historical_claims": 29,
    "transformed_debts": 29,
    "verification_obligations": 11,
    "D9_predecessor_obligation_occurrences": 4,
    "parent_objects": 67,
    "equation_contract_rows": 152,
}

SCENARIO_OWNERS = {
    "I1": ("D1",),
    "I2": ("F9",),
    "I3": tuple([f"F{i}" for i in range(1, 9)] + ["E3", "E4"]),
    "I4": tuple(["C1", "C4", "C5", "C6"] + [f"D{i}" for i in range(2, 7)]),
    "I5": ("C2", "C3", "C7", "C9"),
    "I6": ("N1", "N2", "N3"),
    "I7": ("N5", "N6", "D7", "E2"),
    "I8": ("N4", "C8", "E1"),
}

DEPENDENCY_FILES = (
    "pyproject.toml",
    "uv.lock",
    "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/pyproject.toml",
    "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/python-requirements.lock",
    "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/toolchain.toml",
    "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/web/package.json",
    "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/web/package-lock.json",
)

AUDITS = (
    "implementation/investigations/grc9v4-constitutive-design/scripts/audit_grc9v4_d10_claim_topology.py",
    "implementation/investigations/grc9v4-constitutive-design/scripts/audit_grc9v4_d10_1_preliminary_provenance.py",
    "implementation/investigations/grc9v4-constitutive-design/scripts/audit_grc9v4_d10_2_full_provenance.py",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def canonical_record_digest(data: dict[str, Any], field: str) -> str:
    return digest({key: value for key, value in data.items() if key != field})


def source_rows() -> list[dict[str, Any]]:
    actual_names = {path.name for path in DECISIONS.glob("*.json")}
    if actual_names != set(SOURCE_NAMES):
        missing = sorted(set(SOURCE_NAMES) - actual_names)
        extra = sorted(actual_names - set(SOURCE_NAMES))
        raise RuntimeError(
            f"source inventory mismatch: missing={missing} extra={extra}"
        )
    rows = []
    for name in SOURCE_NAMES:
        path = DECISIONS / name
        data = json.loads(path.read_text(encoding="utf-8"))
        expected_status = EXPECTED_STATUSES.get(name, "accepted_bounded")
        if data.get("status") != expected_status:
            raise RuntimeError(
                f"unexpected source status for {name}: {data.get('status')}"
            )
        digest_field = (
            "decision_record_digest"
            if "decision_record_digest" in data
            else "artifact_digest"
        )
        declared_digest = data[digest_field]
        recomputed_digest = canonical_record_digest(data, digest_field)
        if declared_digest != recomputed_digest:
            raise RuntimeError(f"canonical digest mismatch for {name}")
        rows.append(
            {
                "source_id": path.stem,
                "path": repo_path(path),
                "status_field": "status",
                "expected_status": expected_status,
                "canonical_digest_field": digest_field,
                "canonical_digest": declared_digest,
                "canonical_digest_policy": (
                    "sha256_canonical_json_without_named_digest_field"
                ),
                "file_sha256": file_sha256(path),
                "file_sha256_policy": "sha256_over_exact_source_bytes",
            }
        )
    return rows


def derive_population_contract() -> dict[str, Any]:
    topology = json.loads(
        (DECISIONS / "D10NormativeClaimTopology.json").read_text(encoding="utf-8")
    )
    debt = json.loads(
        (DECISIONS / "D10DebtClaimTransformationLedger.json").read_text(
            encoding="utf-8"
        )
    )
    provenance = json.loads(
        (DECISIONS / "D10_2FullSubstrateProvenanceAndPromotionAudit.json").read_text(
            encoding="utf-8"
        )
    )
    d9_debt = json.loads(
        (DECISIONS / "D9ResidualDebtLedger.json").read_text(encoding="utf-8")
    )
    derived = {
        "current_claims": len(topology["claims"]),
        "historical_claims": len(topology["historical_claim_nodes"]),
        "transformed_debts": len(debt["debt_transformations"]),
        "verification_obligations": len(debt["verification_obligations"]),
        "D9_predecessor_obligation_occurrences": len(
            d9_debt["post_spec_verification_obligations"]
        ),
        "parent_objects": len(provenance["normatively_load_bearing_objects"]),
        "equation_contract_rows": len(
            provenance["normative_equation_contract_registry"]
        ),
    }
    if derived != EXPECTED_POPULATIONS:
        raise RuntimeError(
            f"source-derived population mismatch: {derived} != {EXPECTED_POPULATIONS}"
        )
    return {
        "derivation_policy": "lengths_read_directly_from_named_authoritative_arrays",
        "source_derived": derived,
        "expected_admission": EXPECTED_POPULATIONS,
        "derived_equals_expected": True,
        "source_pointers": {
            "current_claims": "D10NormativeClaimTopology.json#/claims",
            "historical_claims": (
                "D10NormativeClaimTopology.json#/historical_claim_nodes"
            ),
            "transformed_debts": (
                "D10DebtClaimTransformationLedger.json#/debt_transformations"
            ),
            "verification_obligations": (
                "D10DebtClaimTransformationLedger.json#/verification_obligations"
            ),
            "D9_predecessor_obligation_occurrences": (
                "D9ResidualDebtLedger.json#/post_spec_verification_obligations"
            ),
            "parent_objects": (
                "D10_2FullSubstrateProvenanceAndPromotionAudit.json"
                "#/normatively_load_bearing_objects"
            ),
            "equation_contract_rows": (
                "D10_2FullSubstrateProvenanceAndPromotionAudit.json"
                "#/normative_equation_contract_registry"
            ),
        },
    }


def run_audits() -> list[dict[str, Any]]:
    rows = []
    for relative in AUDITS:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / relative)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"accepted audit failed: {relative}\n{completed.stdout}{completed.stderr}"
            )
        lines = [line for line in completed.stdout.splitlines() if line.strip()]
        rows.append(
            {
                "path": relative,
                "status": "passed_unchanged",
                "terminal_output": lines[-1],
            }
        )
    return rows


def main() -> int:
    require_repository_venv()
    context = tomllib.loads((TOOL_ROOT / "iteration0_context.toml").read_text())
    toolchain = tomllib.loads((TOOL_ROOT / "toolchain.toml").read_text())
    sources_before = source_rows()
    population_contract = derive_population_contract()
    accepted_audits = run_audits()
    sources_after = source_rows()
    if sources_before != sources_after:
        raise RuntimeError("accepted source bytes changed during Iteration 0 build")
    source_identity_payload = {
        "schema": "grcv4_explorer_source_bundle_candidate_v1",
        "records": sources_before,
    }
    dependency_rows = [
        {"path": path, "file_sha256": file_sha256(REPO_ROOT / path)}
        for path in DEPENDENCY_FILES
    ]
    setup_identity = {
        "schema": "grcv4_explorer_setup_identity_v1",
        "dependency_files": dependency_rows,
    }
    owned_scenarios = [item for values in SCENARIO_OWNERS.values() for item in values]
    if len(owned_scenarios) != 35 or len(set(owned_scenarios)) != 35:
        raise RuntimeError("scenario ownership must cover 35 unique scenarios")
    record: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C0_contract_v1",
        "gate_id": "ET-C0_source_and_layout_contract_frozen",
        "status": "accepted",
        "gate_candidate": "ET-C0_source_and_layout_contract_frozen",
        "iteration": 0,
        "execution_context": context,
        "authority": {
            "record_role": "setup_source_and_layout_contract_only",
            "accepted_records_modified": False,
            "scientific_claim_added": False,
            "source_adapter_implemented": False,
            "graph_kernel_implemented": False,
            "browser_application_implemented": False,
            "iteration_1_authorized": True,
        },
        "source_contract": {
            "record_count": len(sources_before),
            "source_bundle_candidate_digest": digest(source_identity_payload),
            "source_bundle_identity_payload_schema": source_identity_payload["schema"],
            "records": sources_before,
            "immutability_check": "source_rows_identical_before_and_after_build",
        },
        "accepted_population_contract": population_contract,
        "accepted_audit_contract": accepted_audits,
        "compatibility_contract": {
            "python_minimum": toolchain["python"]["minimum"],
            "python_upper_bound": None,
            "iteration0_tested_python_versions": toolchain["python"][
                "iteration0_tested_versions"
            ],
            "planned_python_conformance_versions": toolchain["python"][
                "planned_conformance_versions"
            ],
            "node_minimum_for_web_rebuild": toolchain["node"]["minimum"],
            "managed_node_version": toolchain["node"]["managed_version"],
            "package_manager": "npm",
            "package_manager_version": toolchain["node"]["package_manager_version"],
            "prebuilt_bundle_requires_node": False,
            "exact_host_version_is_identity": False,
        },
        "setup_contract": {
            "bootstrap_command_from_side_tool_root": "python tool/scripts/bootstrap.py",
            "python_environment": "<repository>/.venv",
            "python_dependency_policy": (
                "stdlib_only_at_iteration_0_future_hash_pinned_rows_fail_on_conflict"
            ),
            "managed_node_root": "tool/.tooling/node",
            "frontend_dependency_root": "tool/web/node_modules",
            "cache_root": "tool/.cache",
            "browser_binary_root": "tool/.tooling/playwright",
            "global_or_user_site_installation_allowed": False,
            "tool_python_execution": "repository_venv_only",
            "host_python_exception": "create_and_immediately_reexec_bootstrap_only",
            "global_node_or_npm_execution_allowed": False,
            "implicit_upgrade_allowed": False,
            "first_web_setup_requires_network_or_checksum_verified_offline_cache": True,
            "setup_identity_digest": digest(setup_identity),
            "setup_identity": setup_identity,
        },
        "layout_contract": {
            "tracked_roots": [
                "tool/pyproject.toml",
                "tool/toolchain.toml",
                "tool/python-requirements.lock",
                "tool/scripts",
                "tool/src/grcv4_explorer",
                "tool/tests",
                "tool/notebooks",
                "tool/web/package.json",
                "tool/web/package-lock.json",
                "records",
            ],
            "ignored_roots": [
                "<repository>/.venv",
                "tool/.tooling",
                "tool/.cache",
                "tool/web/node_modules",
                "tool/web/dist",
                "tool/generated",
            ],
            "forbidden_write_roots": [
                "implementation/investigations/grc9v4-constitutive-design/decisions",
                "src",
                "specs",
                "tests",
            ],
        },
        "generated_artifact_contract": {
            "scratch": "ignored_under_tool/generated",
            "selected_committed": (
                "explicit_selection_only_with_schema_source_bundle_digest_builder_version_"
                "payload_digest_and_reconstruction_command"
            ),
            "machine_local_absolute_paths_allowed": False,
        },
        "canonical_serializer": {
            "encoding": "UTF-8",
            "mapping_keys": "sorted",
            "unordered_collections": "sorted_before_emission",
            "separators": [",", ":"],
            "ensure_ascii": True,
            "allow_nan": False,
            "finite_number_policy": (
                "JSON_integer_or_shortest_round_trip_finite_IEEE754_decimal_"
                "negative_zero_normalized_to_zero"
            ),
        },
        "scenario_contract": {
            "scenario_count": 35,
            "ownership": {key: list(value) for key, value in SCENARIO_OWNERS.items()},
            "closeout_iteration": "I9_reruns_all_35",
        },
        "output_classes": [
            "forensic_evidence_trace",
            "speculative_structural_counterfactual",
        ],
        "non_claims": [
            "no_runtime_model",
            "no_specification_conformance",
            "no_new_scientific_evidence",
            "no_reopened_gate_prediction",
            "no_browser_side_scientific_propagation",
        ],
        "record_digest": None,
    }
    record["record_digest"] = digest(
        {key: value for key, value in record.items() if key != "record_digest"}
    )
    RECORDS.mkdir(parents=True, exist_ok=True)
    record_path = RECORDS / "ETC0SourceAndLayoutContract.json"
    record_path.write_bytes(canonical_bytes(record) + b"\n")

    report_lines = [
        "# ET-C0 Source And Layout Contract",
        "",
        "**Status:** Accepted",
        "",
        "Iteration 0 freezes setup, source identity, layout, serialization, and",
        "non-authority boundaries. It does not implement a source adapter, graph",
        "kernel, counterfactual engine, notebook, or browser application.",
        "",
        "## Result",
        "",
        f"- source records: `{len(sources_before)}`",
        f"- source-bundle candidate digest: `{record['source_contract']['source_bundle_candidate_digest']}`",
        f"- setup identity digest: `{record['setup_contract']['setup_identity_digest']}`",
        f"- record digest: `{record['record_digest']}`",
        "- accepted D10 audits: `passed unchanged`",
        "- accepted source bytes: `unchanged before/after build`",
        "- accepted populations: `derived from authoritative arrays and matched`",
        "- Iteration 1: `authorized`",
        "",
        "## Source Inventory",
        "",
        "| Record | Status | Digest field | File SHA-256 |",
        "| --- | --- | --- | --- |",
    ]
    for row in sources_before:
        report_lines.append(
            f"| `{row['path']}` | `{row['expected_status']}` | "
            f"`{row['canonical_digest_field']}` | `{row['file_sha256']}` |"
        )
    report_lines.extend(
        [
            "",
            "## Setup Boundary",
            "",
            "Python uses the repository-root ignored `.venv`. Managed Node, npm",
            "state, future browser binaries, frontend dependencies, and caches stay",
            "under the side tool. Iteration 0 admits no additional Python or frontend",
            "package dependency.",
            "",
            "The managed Node archives are pinned by platform and SHA-256 in",
            "`tool/toolchain.toml`. A prebuilt browser bundle does not require Node.",
            "",
            "## Claim Boundary",
            "",
            "This contract records accepted inputs and implementation boundaries. It",
            "does not reinterpret an accepted record or add scientific evidence.",
            "",
        ]
    )
    (RECORDS / "ETC0SourceAndLayoutContract.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )
    print(f"ET_C0_BUILD_PASS digest={record['record_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
