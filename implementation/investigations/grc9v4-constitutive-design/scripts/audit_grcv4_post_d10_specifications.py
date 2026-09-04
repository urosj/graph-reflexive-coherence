#!/usr/bin/env python3
"""Audit the post-D10 GRCV4/GRC9V4 specification boundary and content."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[4]
INVESTIGATION = ROOT / "implementation/investigations/grc9v4-constitutive-design"
SIDE_TOOL_ROOT = INVESTIGATION / "tools/exploratory-side-tool"
TOOL_ROOT = SIDE_TOOL_ROOT / "tool"
BOUNDARY_PATH = INVESTIGATION / "specification/PostD10SpecificationBoundary.json"
OUTPUT_DIR = TOOL_ROOT / "generated/agent-queries/post-d10-specification-audit/traces"
GRCV4_SPEC = ROOT / "specs/grc-v4-spec.md"
GRC9V4_SPEC = ROOT / "specs/grc-9-v4-spec.md"
V4_INTERFACE_EXTENSION = ROOT / "specs/grc-common-interface-v4-ext.md"
SOURCE_MANIFEST = ROOT / "specs/grc-v4-source-manifest.json"
CONFORMANCE_FIXTURES = ROOT / "specs/grc-v4-conformance-fixtures.json"
CONFORMANCE_VECTORS = ROOT / "specs/grc-v4-conformance-vectors.json"
CONTRACT_SCHEMA = ROOT / "specs/grc-v4-contract-schema.json"
RELEASE_MANIFEST = ROOT / "specs/grc-v4-specification-release.json"
RELEASE_CHECKSUM = ROOT / "specs/grc-v4-specification-release.sha256"
SPECS_README = ROOT / "specs/README.md"

EXPECTED_SOURCE_BUNDLE_DIGEST = (
    "98c273b3cc097f0d95adfba98ed7dfac0ac494dce9e779bb4b04fe79fef4f6aa"
)
EXPECTED_GRAPH_DIGEST = (
    "44d8c7d33950af5e5f7c61caa4fe6fbd14fc9aedf14218d0a11de7c705542e09"
)
EXPECTED_COUNTS = {
    "current_claim": 41,
    "normative_object": 80,
    "equation_contract": 183,
    "profile": 12,
}
EXPECTED_CLAIM_COUNTS = Counter(
    {
        "normative": 9,
        "optional": 7,
        "conditional": 12,
        "open": 5,
        "negative": 6,
        "optional_profile_normative": 1,
        "GRC9V4_specialization_normative": 1,
    }
)
EXPECTED_D11_SUPPORT_DISPOSITION_OVERRIDES = {
    "D11-C-EC-C-J0-COVARIANCE": (
        "accepted_design_level_algebra_with_implementation_verification_still_pending"
    ),
    "D11-C-EC-C-J0-DERIVATIVE": (
        "accepted_on_the_existing_smooth_fixed_rank_SPD_selector_stratum"
    ),
    "D11-C-EC-C-J0-LIFECYCLE": (
        "accepted_design_level_lifecycle_contract_with_runtime_conformance_still_pending"
    ),
    "D11-G9-EC-DIHEDRAL-COVARIANCE": (
        "accepted_design_level_combinatorial_covariance_with_runtime_verification_pending"
    ),
    "D11-G9-EC-LEGACY-DEFINED-DOMAIN": (
        "accepted_bounded_GRC9V4_compatibility_boundary_not_a_GRC9_or_GRC9V3_rewrite"
    ),
    "D11-G9-EC-LIFECYCLE-READMISSION": (
        "accepted_bounded_design_level_lifecycle_contract_with_runtime_conformance_pending"
    ),
}
PHASE_AUTHORIZATIONS = {
    "specification_writing": "GRCV4_GRC9V4_specification_writing",
    "successor_investigation": ("GRCV4_GRC9V4_D11_G9_ACTIVE_AFTER_D11_C_ACCEPTANCE"),
    "proposal_propagation": (
        "GRCV4_GRC9V4_D11_PROPOSAL_PROPAGATION_AFTER_D11_C_AND_D11_G9_ACCEPTANCE"
    ),
    "paper_propagation": (
        "GRCV4_GRC9V4_D11_PAPER_PROPAGATION_AFTER_D11_C_AND_D11_G9_ACCEPTANCE"
    ),
    "specification_propagation": (
        "GRCV4_GRC9V4_D11_SPECIFICATION_PROPAGATION_AFTER_ACCEPTED_PAPER"
    ),
    "specification_correction": ("GRCV4_GRC9V4_SPECIFICATION_ENGINEERING_CORRECTION"),
    "implementation": "GRCV4_GRC9V4_implementation",
}

sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.forensic import (  # noqa: E402
    contract_provenance,
    negative_claims,
    object_dependents,
    reconstruction_path,
    write_trace,
)
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.successor import load_successor_forensic_context  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_bytes(*args: str, check: bool = True) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
    ).stdout


def git_lines(*args: str) -> list[str]:
    return git_bytes(*args).decode("utf-8").splitlines()


def validate_repository_path(path_text: str) -> Path:
    relative = Path(path_text)
    if relative.is_absolute() or ".." in relative.parts:
        raise RuntimeError(f"boundary contains unsafe path: {path_text}")
    resolved = (ROOT / relative).resolve()
    if ROOT != resolved and ROOT not in resolved.parents:
        raise RuntimeError(f"boundary path escapes repository: {path_text}")
    return resolved


def json_pointer(document: Any, pointer: str) -> Any:
    if not pointer.startswith("/"):
        raise RuntimeError(f"invalid authority JSON pointer: {pointer}")
    value = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or token not in value:
            raise RuntimeError(f"unresolved authority JSON pointer: {pointer}")
        value = value[token]
    return value


def validate_phase_boundary() -> tuple[str, int]:
    boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
    if boundary.get("schema") != "grcv4_grc9v4_post_d10_specification_boundary_v7":
        raise RuntimeError("unexpected post-D10 boundary schema")

    base = boundary["authorization_base_commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", base):
        raise RuntimeError("authorization base must be a full Git object ID")
    subprocess.run(
        ["git", "cat-file", "-e", f"{base}^{{commit}}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, "HEAD"],
        cwd=ROOT,
        capture_output=True,
    ).returncode:
        raise RuntimeError("authorization base is not an ancestor of HEAD")

    entry_state = boundary["post_d10_entry_state"]
    entry_path = validate_repository_path(entry_state["path"])
    if not entry_path.is_file():
        raise RuntimeError(f"missing post-D10 entry state: {entry_state['path']}")
    if sha256_file(entry_path) != entry_state["sha256"]:
        raise RuntimeError(f"post-D10 entry-state hash drift: {entry_state['path']}")
    entry_document = json.loads(entry_path.read_text(encoding="utf-8"))
    for pointer, expected in entry_state["assertions"].items():
        if json_pointer(entry_document, pointer) != expected:
            raise RuntimeError(
                f"post-D10 entry state does not satisfy {pointer}={expected!r}"
            )

    phase = boundary["active_phase"]
    if phase not in PHASE_AUTHORIZATIONS:
        raise RuntimeError(f"unsupported active phase: {phase}")
    expected_policy = {
        "specification_writing": {"src_and_tests": "frozen_to_authorization_base"},
        "successor_investigation": {
            "activation": (
                "requires_a_hash_bound_current_successor_authority_in_phase_authority"
            ),
            "src_and_tests": "frozen_to_authorization_base",
        },
        "proposal_propagation": {
            "activation": (
                "requires_hash_bound_accepted_D11_C_and_D11_G9_authority_plus_accepted_D11_forensic_overlay"
            ),
            "src_and_tests": "frozen_to_authorization_base",
            "specifications": (
                "frozen_pending_accepted_proposal_review_and_paper_propagation"
            ),
            "proposal": "mutable_only_at_authorized_proposal_paths",
            "paper": "frozen_pending_accepted_proposal_review",
            "exploratory_tool_UX": ("mutable_only_at_authorized_successor_UX_paths"),
        },
        "paper_propagation": {
            "activation": (
                "requires_hash_bound_accepted_D11_C_and_D11_G9_authority_plus_accepted_D11_forensic_overlay"
            ),
            "src_and_tests": "frozen_to_authorization_base",
            "specifications": "frozen_pending_paper_propagation",
            "proposal": "frozen_to_accepted_proposal_review",
            "paper": "mutable_only_at_authorized_paper_paths",
            "exploratory_tool_UX": ("mutable_only_at_authorized_successor_UX_paths"),
        },
        "specification_propagation": {
            "activation": (
                "requires_hash_bound_committed_D11_integrated_paper_and_accepted_D11_C_and_D11_G9_authority"
            ),
            "src_and_tests": "frozen_to_authorization_base",
            "specifications": (
                "mutable_only_at_authorized_specification_outputs_and_registry"
            ),
            "proposal": "frozen_to_accepted_proposal_review",
            "paper": "frozen_to_accepted_D11_integrated_paper",
            "exploratory_tool_UX": "frozen_to_accepted_D11_successor_UX",
        },
        "specification_correction": {
            "activation": (
                "requires_hash_bound_implementation_readiness_audit_and_accepted_D11_specification_release"
            ),
            "src_and_tests": "frozen_to_authorization_base",
            "specifications": (
                "mutable_only_at_authorized_V4_contract_schema_vector_and_release_outputs"
            ),
            "proposal": "frozen_to_accepted_proposal_review",
            "paper": "frozen_to_accepted_D11_integrated_paper",
            "exploratory_tool_UX": "frozen_to_accepted_D11_successor_UX",
        },
        "implementation": {
            "activation": (
                "requires_a_hash_bound_successor_authority_in_phase_authority"
            ),
            "src_and_tests": "allowed",
        },
    }
    if boundary.get("phase_policy") != expected_policy:
        raise RuntimeError("post-D10 phase policy drift")
    authority = boundary["phase_authority"]
    if authority.get("authorization") != PHASE_AUTHORIZATIONS[phase]:
        raise RuntimeError(f"phase authority does not authorize {phase}")
    authority_path = validate_repository_path(authority["path"])
    if not authority_path.is_file():
        raise RuntimeError(f"missing phase authority: {authority['path']}")
    if sha256_file(authority_path) != authority["sha256"]:
        raise RuntimeError(f"phase authority hash drift: {authority['path']}")
    prior_authority = boundary.get("prior_phase_authority", {})
    prior_authority_path = validate_repository_path(prior_authority.get("path", ""))
    if not prior_authority_path.is_file() or sha256_file(
        prior_authority_path
    ) != prior_authority.get("sha256"):
        raise RuntimeError("prior phase authority hash drift")
    required_assertions = {
        "specification_writing": {
            "/authorization_effect/specification_authorized": True,
            "/authorization_effect/implementation_authorized": False,
            "/authorization_effect/runtime_or_src_change_authorized": False,
        },
        "successor_investigation": {
            "/status": "accepted_bounded",
            "/decision/selected_candidate_id": "D11-C-T3a",
            "/authorization_effect/D11_G9_investigation_active": True,
            "/authorization_effect/implementation_authorized": False,
            "/authorization_effect/runtime_or_src_tests_change_authorized": False,
            "/authorization_effect/GRC9_or_GRC9V3_change_authorized": False,
        },
        "proposal_propagation": {
            "/status": "accepted_bounded",
            "/decision/selected_candidate_id": "D11-G9-P4a",
            "/propagation_state/next_gate": "D11-paper-propagation",
            "/authorization_effect/implementation_authorized": False,
            "/authorization_effect/runtime_or_src_tests_change_authorized": False,
            "/authorization_effect/GRC9_or_GRC9V3_change_authorized": False,
        },
        "paper_propagation": {
            "/status": "accepted_bounded",
            "/decision/selected_candidate_id": "D11-G9-P4a",
            "/propagation_state/next_gate": "D11-paper-propagation",
            "/authorization_effect/implementation_authorized": False,
            "/authorization_effect/runtime_or_src_tests_change_authorized": False,
            "/authorization_effect/GRC9_or_GRC9V3_change_authorized": False,
        },
        "specification_propagation": {
            "/status": "accepted_bounded",
            "/paper_source/commit_sha": ("073a8014c745426d164be5e7d81223cea0d5d370"),
            "/paper_source/paper_propagation_status": "propagated",
            "/authorization_effect/specification_propagation_authorized": True,
            "/authorization_effect/implementation_authorized": False,
            "/authorization_effect/runtime_or_src_tests_change_authorized": False,
            "/authorization_effect/GRC9_or_GRC9V3_change_authorized": False,
        },
        "specification_correction": {
            "/status": "accepted_bounded",
            "/audit_input/sha256": (
                "32cea1b2752361864b02651cb7d38df85929210adc213aa76ee1307babcb5196"
            ),
            "/authorization_effect/specification_correction_authorized": True,
            "/authorization_effect/implementation_authorized": False,
            "/authorization_effect/runtime_or_src_tests_change_authorized": False,
            "/authorization_effect/GRC9_or_GRC9V3_change_authorized": False,
        },
        "implementation": {
            "/authorization_effect/specification_authorized": True,
            "/authorization_effect/implementation_authorized": True,
            "/authorization_effect/runtime_or_src_change_authorized": True,
        },
    }[phase]
    if authority.get("assertions") != required_assertions:
        raise RuntimeError(f"phase authority assertions do not match {phase}")
    authority_document = json.loads(authority_path.read_text(encoding="utf-8"))
    for pointer, expected in required_assertions.items():
        if json_pointer(authority_document, pointer) != expected:
            raise RuntimeError(
                f"phase authority does not satisfy {pointer}={expected!r}"
            )
    if phase in {
        "successor_investigation",
        "proposal_propagation",
        "paper_propagation",
        "specification_propagation",
        "specification_correction",
        "implementation",
    }:
        authority_was_already_present = (
            subprocess.run(
                ["git", "cat-file", "-e", f"{base}:{authority['path']}"],
                cwd=ROOT,
                capture_output=True,
            ).returncode
            == 0
        )
        if authority_was_already_present:
            raise RuntimeError(
                f"{phase} requires a hash-bound successor authority "
                "created after the specification-writing base"
            )

    mutable = set(boundary["mutable_registry_paths"])
    frozen = boundary["frozen_preexisting_spec_sha256"]
    baseline_specs = set(git_lines("ls-tree", "-r", "--name-only", base, "--", "specs"))
    expected_frozen = baseline_specs - mutable
    if set(frozen) != expected_frozen:
        raise RuntimeError(
            "frozen pre-existing spec roster mismatch: "
            f"missing={sorted(expected_frozen - set(frozen))} "
            f"extra={sorted(set(frozen) - expected_frozen)}"
        )

    for path_text, expected_sha in frozen.items():
        path = validate_repository_path(path_text)
        baseline_bytes = git_bytes("show", f"{base}:{path_text}")
        if sha256_bytes(baseline_bytes) != expected_sha:
            raise RuntimeError(f"recorded baseline hash mismatch: {path_text}")
        if not path.is_file() or sha256_file(path) != expected_sha:
            raise RuntimeError(f"frozen pre-existing spec changed: {path_text}")

    outputs = boundary["authorized_specification_outputs"]
    if set(outputs) != {
        "specs/grc-common-interface-v4-ext.md",
        "specs/grc-v4-conformance-fixtures.json",
        "specs/grc-v4-conformance-vectors.json",
        "specs/grc-v4-contract-schema.json",
        "specs/grc-v4-source-manifest.json",
        "specs/grc-v4-specification-release.json",
        "specs/grc-v4-specification-release.sha256",
        "specs/grc-v4-spec.md",
        "specs/grc-9-v4-spec.md",
    }:
        raise RuntimeError("unexpected authorized specification output roster")
    for path_text in outputs:
        path = validate_repository_path(path_text)
        if not path.is_file():
            raise RuntimeError(f"missing authorized specification: {path_text}")
        if (
            subprocess.run(
                ["git", "cat-file", "-e", f"{base}:{path_text}"],
                cwd=ROOT,
                capture_output=True,
            ).returncode
            == 0
        ):
            raise RuntimeError(
                f"authorized output was not new at the base: {path_text}"
            )

    expected_maintenance = {
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "audit_grc9v4_d10_claim_topology.py",
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "audit_grcv4_post_d10_specifications.py",
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "audit_grc9v4_d11_successor_opening.py",
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "audit_grc9v4_d11_c_resolution.py",
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "audit_grc9v4_d11_g9_resolution.py",
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "audit_grcv4_d11_paper_propagation.py",
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "build_grcv4_specification_vectors.py",
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "build_grcv4_specification_release.py",
        "implementation/investigations/grc9v4-constitutive-design/"
        "specification/PostD10SpecificationBoundary.json",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/docs/AgenticQueryGuide.md",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/GRCV4ExploratorySideToolImplementationPlan.md",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/GRCV4ExploratorySideToolImplementationChecklist.md",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/GRCV4ExploratorySideToolD11SuccessorScenarios.md",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/records/ETC10D11SourceContract.json",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/records/ETC10D11SourceBundleManifest.json",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/records/ETC10D11GraphSnapshot.json",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/records/ETC10D11ForensicAdmission.json",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/records/ETC10D11ForensicAdmission.md",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/audit_iteration0_contract.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/build_iteration10_d11.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/audit_iteration10_d11.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/test_iteration10_d11.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/run.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/verify_iteration9.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/src/grcv4_explorer/__init__.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/src/grcv4_explorer/adapters.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/src/grcv4_explorer/forensic.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/src/grcv4_explorer/source_contract.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/src/grcv4_explorer/successor.py",
    }
    maintenance = set(boundary["authorized_verification_maintenance_paths"])
    if maintenance != expected_maintenance:
        raise RuntimeError("unexpected verification-maintenance path roster")
    for path_text in maintenance:
        validate_repository_path(path_text)

    expected_successor_ux_paths = {
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/GRCV4ExploratorySideToolD11UXScenarios.md",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/README.md",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/docs/D11UXGuide.md",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/records/ETC11D11SuccessorUXBundle.json",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/records/ETC11D11SuccessorUXCandidate.json",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/records/ETC11D11UXCandidate.md",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/records/ETC11D11UXWebBuildManifest.json",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/notebooks/d11_successor_recipes.ipynb",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/audit_iteration11_d11_ux.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/build_iteration11_d11_ux.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/run_iteration11_d11_notebook.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/serve_iteration11_d11.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/test_iteration11_d11_browser.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/test_iteration11_d11_ux.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/src/grcv4_explorer/successor_ux.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/web/e2e/successor.spec.mjs",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/web/src/app.js",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/web/src/styles.css",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/web/src/successor.js",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/web/tests/static-authority.test.mjs",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/web/tests/successor.test.mjs",
    }
    successor_ux_paths = set(boundary["authorized_successor_UX_paths"])
    if successor_ux_paths != expected_successor_ux_paths:
        raise RuntimeError("unexpected successor-UX path roster")
    for path_text in successor_ux_paths:
        validate_repository_path(path_text)

    expected_successor_paths = {
        "implementation/investigations/grc9v4-constitutive-design/README.md",
        "implementation/investigations/grc9v4-constitutive-design/"
        "GRC9V4ConstitutiveDesignPlan.md",
        "implementation/investigations/grc9v4-constitutive-design/"
        "GRC9V4ConstitutiveDesignChecklist.md",
        "implementation/investigations/grc9v4-constitutive-design/"
        "GRC9V4ConstitutiveDesignDecisionLedger.md",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11SuccessorInvestigationOpening.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11SuccessorInvestigationOpening.md",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11ClaimDebtAndAuthorityRouting.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11ClaimDebtAndAuthorityRouting.md",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11CCandidateCBaselineTransportAndMobilityClosure.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11CCandidateCBaselineTransportAndMobilityClosure.md",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11G9CanonicalExpansionPortAllocationClosure.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11G9CanonicalExpansionPortAllocationClosure.md",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11CCandidateBaselineTransportAndMobilityResolution.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11CCandidateBaselineTransportAndMobilityResolution.md",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11CCandidateBaselineTransportProvenanceSupplement.json",
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "witness_d11_c_hm_stiffness_baseline.py",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11G9CanonicalExpansionPortAllocationResolution.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11G9CanonicalExpansionPortAllocationResolution.md",
        "implementation/investigations/grc9v4-constitutive-design/decisions/"
        "D11G9AxisPreservingExpansionProvenanceSupplement.json",
        "implementation/investigations/grc9v4-constitutive-design/scripts/"
        "witness_d11_g9_canonical_expansion.py",
    }
    successor_paths = set(boundary["authorized_successor_investigation_paths"])
    if successor_paths != expected_successor_paths:
        raise RuntimeError("unexpected successor-investigation path roster")
    for path_text in successor_paths:
        validate_repository_path(path_text)

    expected_paper_paths = {
        "implementation/investigations/grc9v4-constitutive-design/"
        "drafts/2026-09-GRC-V4.md"
    }
    paper_paths = set(boundary["authorized_paper_propagation_paths"])
    if paper_paths != expected_paper_paths:
        raise RuntimeError("unexpected paper-propagation path roster")
    for path_text in paper_paths:
        if not validate_repository_path(path_text).is_file():
            raise RuntimeError(f"missing authorized paper: {path_text}")

    expected_proposal_paths = {
        "implementation/investigations/grc9v4-constitutive-design/"
        "drafts/GRCV4-proposal.md"
    }
    proposal_paths = set(boundary["authorized_proposal_propagation_paths"])
    if proposal_paths != expected_proposal_paths:
        raise RuntimeError("unexpected proposal-propagation path roster")
    for path_text in proposal_paths:
        if not validate_repository_path(path_text).is_file():
            raise RuntimeError(f"missing authorized proposal: {path_text}")

    paper_frozen_specs = boundary["paper_phase_frozen_spec_sha256"]
    correction_only_outputs = {
        "specs/grc-v4-conformance-vectors.json",
        "specs/grc-v4-contract-schema.json",
        "specs/grc-v4-specification-release.json",
        "specs/grc-v4-specification-release.sha256",
    }
    expected_paper_frozen = (set(outputs) - correction_only_outputs) | mutable
    if set(paper_frozen_specs) != expected_paper_frozen:
        raise RuntimeError("paper-phase frozen specification roster mismatch")
    if phase in {"proposal_propagation", "paper_propagation"}:
        for path_text, expected_sha in paper_frozen_specs.items():
            path = validate_repository_path(path_text)
            if not path.is_file() or sha256_file(path) != expected_sha:
                raise RuntimeError(
                    f"specification changed during paper propagation: {path_text}"
                )

    proposal_frozen_papers = boundary["proposal_phase_frozen_paper_sha256"]
    if set(proposal_frozen_papers) != paper_paths:
        raise RuntimeError("proposal-phase frozen paper roster mismatch")
    if phase == "proposal_propagation":
        for path_text, expected_sha in proposal_frozen_papers.items():
            path = validate_repository_path(path_text)
            if not path.is_file() or sha256_file(path) != expected_sha:
                raise RuntimeError(
                    f"paper changed during proposal propagation: {path_text}"
                )

    paper_frozen_proposals = boundary["paper_phase_frozen_proposal_sha256"]
    if set(paper_frozen_proposals) != proposal_paths:
        raise RuntimeError("paper-phase frozen proposal roster mismatch")
    if phase in {
        "paper_propagation",
        "specification_propagation",
        "specification_correction",
        "implementation",
    }:
        for path_text, expected_sha in paper_frozen_proposals.items():
            path = validate_repository_path(path_text)
            if not path.is_file() or sha256_file(path) != expected_sha:
                raise RuntimeError(
                    f"proposal changed after review acceptance: {path_text}"
                )

    specification_frozen_papers = boundary["specification_phase_frozen_paper_sha256"]
    if set(specification_frozen_papers) != paper_paths:
        raise RuntimeError("specification-phase frozen paper roster mismatch")
    if phase in {
        "specification_propagation",
        "specification_correction",
        "implementation",
    }:
        for path_text, expected_sha in specification_frozen_papers.items():
            path = validate_repository_path(path_text)
            if not path.is_file() or sha256_file(path) != expected_sha:
                raise RuntimeError(
                    f"paper changed after D11 integration acceptance: {path_text}"
                )

    changed_paths = set(git_lines("diff", "--name-only", base))
    changed_paths.update(git_lines("ls-files", "--others", "--exclude-standard"))
    allowed_paths = set(outputs) | mutable | maintenance
    if phase in {
        "successor_investigation",
        "proposal_propagation",
        "paper_propagation",
        "specification_propagation",
        "specification_correction",
        "implementation",
    }:
        allowed_paths.update(successor_paths)
    if phase in {
        "proposal_propagation",
        "paper_propagation",
        "specification_propagation",
        "specification_correction",
        "implementation",
    }:
        allowed_paths.update(paper_paths)
        allowed_paths.update(successor_ux_paths)
    if phase in {
        "proposal_propagation",
        "paper_propagation",
        "specification_propagation",
        "specification_correction",
        "implementation",
    }:
        allowed_paths.update(proposal_paths)
    if phase in {
        "specification_propagation",
        "specification_correction",
        "implementation",
    }:
        allowed_paths.add(authority["path"])
    if phase in {"specification_correction", "implementation"}:
        allowed_paths.add(prior_authority["path"])
    unexpected_changes = {
        path
        for path in changed_paths
        if path not in allowed_paths
        and not (phase == "implementation" and path.startswith(("src/", "tests/")))
    }
    if unexpected_changes:
        raise RuntimeError(
            "changes exceed the active post-D10 phase envelope: "
            f"{sorted(unexpected_changes)}"
        )

    if phase in {
        "specification_writing",
        "successor_investigation",
        "proposal_propagation",
        "paper_propagation",
        "specification_propagation",
        "specification_correction",
    }:
        changed_runtime_paths = set(
            git_lines("diff", "--name-only", base, "--", "src", "tests")
        )
        changed_runtime_paths.update(
            git_lines(
                "ls-files",
                "--others",
                "--exclude-standard",
                "--",
                "src",
                "tests",
            )
        )
        if changed_runtime_paths:
            raise RuntimeError(
                f"src/tests changed during {phase}: {sorted(changed_runtime_paths)}"
            )

    return phase, len(frozen)


def safe_name(identifier: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", identifier) + ".json"


def validate_trace(identifier: str, trace: dict[str, Any]) -> None:
    if trace.get("output_class") != "forensic_evidence_trace":
        raise RuntimeError(f"{identifier}: unexpected forensic output class")
    if trace.get("row_count") != len(trace.get("rows", [])):
        raise RuntimeError(f"{identifier}: forensic row count mismatch")
    if not isinstance(trace.get("trace_digest"), str):
        raise RuntimeError(f"{identifier}: missing forensic trace digest")
    for index, row in enumerate(trace["rows"]):
        source_ref = row.get("source_ref", {})
        if not source_ref.get("record_id") or not source_ref.get("source_json_pointer"):
            raise RuntimeError(f"{identifier}:{index}: missing source reference")
        if not row.get("edge_refs"):
            raise RuntimeError(f"{identifier}:{index}: missing edge witnesses")


def query_all(
    context: Any,
    kind: str,
    identifiers: list[str],
    operation: Callable[[Any, str], dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    traces: dict[str, dict[str, Any]] = {}
    for identifier in identifiers:
        trace = operation(context, identifier)
        validate_trace(identifier, trace)
        write_trace(OUTPUT_DIR / kind / safe_name(identifier), trace)
        traces[identifier] = trace
    return traces


def reconstructed_claim(identifier: str, trace: dict[str, Any]) -> dict[str, Any]:
    matches = [
        node
        for row in trace["rows"]
        for node in row.get("payload", {}).get("nodes", [])
        if node.get("kind") == "current_claim" and node.get("identifier") == identifier
    ]
    if len(matches) != 1:
        raise RuntimeError(f"{identifier}: expected one reconstructed claim")
    return matches[0]


def github_slug(heading: str) -> str:
    value = re.sub(r"<[^>]+>", "", heading).strip().lower()
    value = value.replace("`", "")
    value = re.sub(r"[^\w\- ]", "", value, flags=re.UNICODE)
    return re.sub(r" +", "-", value)


def validate_markdown(path: Path, text: str) -> None:
    if text.count("```") % 2:
        raise RuntimeError(f"{path}: unbalanced fenced code blocks")
    if len(re.findall(r"(?m)^\$\$$", text)) % 2:
        raise RuntimeError(f"{path}: unbalanced display-math delimiters")
    if re.search(r"(?m)^#{1,6}(?![# ])", text):
        raise RuntimeError(f"{path}: malformed ATX heading")

    definitions = dict(re.findall(r"(?m)^\[([^\]]+)\]:[ \t]+(\S+)(?:[ \t]+.*)?$", text))
    uses = set(re.findall(r"\[[^\]]+\]\[([^\]]+)\]", text))
    missing = sorted(uses - set(definitions))
    if missing:
        raise RuntimeError(f"{path}: undefined reference links {missing}")
    targets = [definitions[label] for label in sorted(uses)]
    targets.extend(
        target
        for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^) \t]+)", text)
        if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)
    )
    for target in targets:
        target_path, separator, fragment = target.partition("#")
        resolved = (path.parent / target_path).resolve()
        if not resolved.is_file():
            raise RuntimeError(f"{path}: missing link target {target_path}")
        if separator:
            headings = {
                github_slug(match.group(1))
                for match in re.finditer(
                    r"(?m)^#{1,6}\s+(.+?)\s*$",
                    resolved.read_text(encoding="utf-8"),
                )
            }
            if fragment not in headings:
                raise RuntimeError(
                    f"{path}: fragment #{fragment} not found in {target_path}"
                )


def validate_pandoc_render(path: Path) -> None:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        raise RuntimeError("pandoc is required for the specification render audit")
    result = subprocess.run(
        [
            pandoc,
            "--from=gfm+tex_math_dollars",
            "--to=html5",
            "--mathjax",
            str(path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(f"pandoc failed for {path}: {result.stderr.strip()}")


def validate_v4_source_manifest() -> None:
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema") != "grcv4_specification_source_manifest_v2":
        raise RuntimeError("unexpected V4 source-manifest schema")
    if manifest.get("status") != "normative_source_identity":
        raise RuntimeError("V4 source manifest is not normative")
    audit_sha = manifest.get("audit_input", {}).get("sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", audit_sha):
        raise RuntimeError("V4 audit input is not digest-bound")
    readiness = manifest.get("implementation_readiness_audit", {})
    if readiness.get("sha256") != (
        "32cea1b2752361864b02651cb7d38df85929210adc213aa76ee1307babcb5196"
    ):
        raise RuntimeError("V4 readiness audit is not digest-bound")
    if manifest.get("release_manifest") != str(RELEASE_MANIFEST.relative_to(ROOT)):
        raise RuntimeError("V4 source manifest does not name the release manifest")

    expected_roles = {
        "canonical_grcv4_substrate_paper",
        "proposal_and_provenance_companion",
        "d10_specification_authority",
        "d10_2_provenance_and_promotion_authority",
        "unchanged_common_interface",
        "grc9v3_disabled_reduction_target",
        "grc9_mechanical_provenance_source",
    }
    sources = manifest.get("sources", [])
    if {source.get("role") for source in sources} != expected_roles:
        raise RuntimeError("V4 source-manifest role roster mismatch")
    for source in sources:
        path_text = source.get("path", "")
        path = validate_repository_path(path_text)
        commit = source.get("commit_sha", "")
        expected_sha = source.get("file_sha256", "")
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise RuntimeError(f"invalid source commit binding: {path_text}")
        if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
            raise RuntimeError(f"invalid source file digest: {path_text}")
        committed = git_bytes("show", f"{commit}:{path_text}")
        if sha256_bytes(committed) != expected_sha:
            raise RuntimeError(f"source commit/file binding mismatch: {path_text}")
        if not path.is_file() or sha256_file(path) != expected_sha:
            raise RuntimeError(f"source worktree drift: {path_text}")

    accepted_successors = manifest.get("accepted_successor_sources", [])
    expected_successor_roles = {
        "D11_C_accepted_resolution",
        "D11_C_append_only_provenance",
        "D11_G9_accepted_resolution",
        "D11_G9_append_only_provenance",
    }
    if {
        source.get("role") for source in accepted_successors
    } != expected_successor_roles:
        raise RuntimeError("V4 accepted-successor source roster mismatch")
    for source in accepted_successors:
        path_text = source.get("path", "")
        path = validate_repository_path(path_text)
        commit = source.get("commit_sha", "")
        expected_sha = source.get("file_sha256", "")
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise RuntimeError(f"invalid successor commit binding: {path_text}")
        if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
            raise RuntimeError(f"invalid successor file digest: {path_text}")
        committed = git_bytes("show", f"{commit}:{path_text}")
        if sha256_bytes(committed) != expected_sha:
            raise RuntimeError(
                f"successor source commit/file binding mismatch: {path_text}"
            )
        if not path.is_file() or sha256_file(path) != expected_sha:
            raise RuntimeError(f"successor source worktree drift: {path_text}")

    history = manifest.get("successor_investigation_history", [])
    if len(history) != 4 or any(
        row.get("semantic_status", "").startswith(("active_", "queued_"))
        for row in history
    ):
        raise RuntimeError("V4 successor history still presents D11 as open")

    closures = manifest.get("post_d10_v4_closures", [])
    if {closure.get("closure_id") for closure in closures} != {
        "V4-AUDIT-C-BASELINE-TRANSPORT",
        "V4-AUDIT-G9-PORT-ALLOCATION",
    }:
        raise RuntimeError("V4 post-D10 closure roster mismatch")
    if any(closure.get("backward_evidence") is not False for closure in closures):
        raise RuntimeError("V4 audit closure was promoted to backward evidence")
    if any(closure.get("accepted_by_D11") is not True for closure in closures):
        raise RuntimeError("V4 accepted D11 closure remains provisional")
    expected_profiles = {
        "V4-AUDIT-C-BASELINE-TRANSPORT": "C-HM-STIFFNESS-BASELINE-v1",
        "V4-AUDIT-G9-PORT-ALLOCATION": (
            "grc9v4_axis_preserving_chiral_same_port_expansion_v1"
        ),
    }
    if any(
        closure.get("selected_profile_id") != expected_profiles[closure["closure_id"]]
        for closure in closures
    ):
        raise RuntimeError("V4 accepted D11 closure profile drift")


def validate_v4_conformance_fixtures(profiles: set[str]) -> None:
    fixtures = json.loads(CONFORMANCE_FIXTURES.read_text(encoding="utf-8"))
    if fixtures.get("schema") != "grcv4_conformance_fixture_contract_v1":
        raise RuntimeError("unexpected V4 conformance-fixture schema")
    if fixtures.get("status") != "normative_preimplementation_fixture_contract":
        raise RuntimeError("V4 conformance fixtures have unexpected status")
    if fixtures.get("implementation_evidence") is not False:
        raise RuntimeError("preimplementation fixtures claim runtime evidence")
    authority = fixtures.get("authority_boundary", {})
    if set(authority.get("accepted_D11_claim_ids", [])) != {
        "D11-C-CL-O-001",
        "D11-G9-CL-N-001",
    }:
        raise RuntimeError("V4 fixture D11 claim authority mismatch")
    if any(
        authority.get(key) is not True
        for key in (
            "candidate_c_specification_authority_complete",
            "GRC9V4_expansion_specification_authority_complete",
            "D11_dependent_rows_are_conformance_authority",
        )
    ):
        raise RuntimeError("V4 fixture D11 authority remains provisional")
    if set(fixtures.get("profile_families", [])) != profiles:
        raise RuntimeError("V4 fixture profile roster mismatch")

    required_group_sizes = {
        "common_cases": 8,
        "candidate_a_cases": 9,
        "candidate_c_cases": 14,
        "realization_cases": 5,
        "lifecycle_cases": 10,
    }
    for key, count in required_group_sizes.items():
        if len(fixtures.get(key, [])) != count:
            raise RuntimeError(f"V4 fixture group {key} must contain {count} cases")

    candidate_c_cases = fixtures.get("candidate_c_cases", [])
    candidate_c_ids = {
        row.get("id") if isinstance(row, dict) else row for row in candidate_c_cases
    }
    required_candidate_c_ids = {
        "C-TR-REFERENCE-MAP",
        "C-BASELINE-EXACT",
        "C-BASELINE-DERIVATIVE-COVARIANCE",
        "C-RETAINED-VS-PHYSICAL-CONDITIONING",
        "C-KAPPA-M-ZERO",
        "C-CHI-ZERO",
        "C-ZETA-ZERO",
        "C-LIFECYCLE-REFERENCE-MAP",
    }
    if not required_candidate_c_ids <= candidate_c_ids:
        raise RuntimeError("V4 Candidate C D11 fixture coverage is incomplete")
    if any(
        isinstance(row, dict)
        and row.get("authority_status", "").startswith("preregistered_")
        for row in candidate_c_cases
    ):
        raise RuntimeError("V4 Candidate C fixture remains preregistered")

    expansion = fixtures.get("grc9_expansion_fixture", {})
    if expansion.get("policy_id") != (
        "grc9v4_axis_preserving_chiral_same_port_expansion_v1"
    ):
        raise RuntimeError("V4 expansion fixture has wrong policy")
    event_id = expansion.get("event_id", "")
    if not re.fullmatch(r"grc-event-sha256:[0-9a-f]{64}", event_id):
        raise RuntimeError("V4 expansion fixture event ID grammar drift")
    redirected = expansion.get("redirected_source_endpoints", [])
    expected_redirected = [[f"s{1 + ((port - 1) % 3)}", port] for port in range(1, 10)]
    if redirected != expected_redirected:
        raise RuntimeError("V4 expansion fixture column redirection drift")
    if len(redirected) != 9:
        raise RuntimeError("V4 expansion fixture does not redirect nine ports")
    spines = expansion.get("primary_spines", {})
    expected_spines = {
        "positive": {
            "module_chirality": 1,
            "growth_phase": None,
            "internal_edges": [
                [["c", 2], ["s1", 2]],
                [["c", 6], ["s2", 6]],
                [["c", 7], ["s3", 7]],
            ],
        },
        "negative": {
            "module_chirality": -1,
            "growth_phase": None,
            "internal_edges": [
                [["c", 3], ["s1", 3]],
                [["c", 4], ["s2", 4]],
                [["c", 8], ["s3", 8]],
            ],
        },
    }
    if spines != expected_spines:
        raise RuntimeError("V4 expansion fixture chiral primary spine drift")
    for spine in spines.values():
        endpoints = [
            tuple(endpoint) for edge in spine["internal_edges"] for endpoint in edge
        ]
        endpoints.extend(tuple(endpoint) for endpoint in redirected)
        if len(endpoints) != len(set(endpoints)):
            raise RuntimeError("V4 expansion fixture contains a port collision")
        if any(edge[0][1] != edge[1][1] for edge in spine["internal_edges"]):
            raise RuntimeError("V4 expansion fixture violates same-port authority")
    if set(expansion.get("required_failure_dispositions", [])) != {
        "module_chirality_required",
        "module_growth_phase_required",
        "reject_noncanonical_inactive_growth_phase",
    }:
        raise RuntimeError("V4 expansion phase failure roster drift")
    assertions = expansion.get("assertions", {})
    required_true_assertions = {
        "unique_live_endpoint_occupancy",
        "column_family_preserved_for_old_boundary",
        "same_port_internal_edges",
        "primary_row_and_column_counts_equal_one",
        "rotation_preserves_chirality",
        "reflection_flips_chirality",
        "whole_lifecycle_target_readmission_required",
        "partial_K4_zero_fill_forbidden",
        "candidate_C_target_W_C_tr_complete_before_rederivation",
        "primary_resource_sum_equals_source",
    }
    if any(assertions.get(key) is not True for key in required_true_assertions):
        raise RuntimeError("V4 expansion fixture assertion drift")
    if assertions.get("core_resource") != 0:
        raise RuntimeError("V4 expansion fixture core resource drift")
    if assertions.get("additional_node_resource") != 0:
        raise RuntimeError("V4 expansion fixture additional-node resource drift")

    additional = fixtures.get("grc9_additional_node_fixture", {})
    expected_additional_edges = [
        {
            "edge_id": f"{event_id}/internal/extra/{branch}/1",
            "endpoints": [
                [f"{event_id}/satellite/{branch}", port],
                [f"{event_id}/extra/{branch}/1", port],
            ],
        }
        for branch, port in ((1, 3), (2, 4), (3, 8))
    ]
    if additional.get("desired_external_capacity") != 45:
        raise RuntimeError("V4 additional-node fixture capacity drift")
    if additional.get("expected_canonical_node_count") != 7:
        raise RuntimeError("V4 additional-node fixture node-count drift")
    if additional.get("event_id") != event_id:
        raise RuntimeError("V4 additional-node fixture event identity drift")
    if additional.get("module_chirality") != 1:
        raise RuntimeError("V4 additional-node chirality fixture drift")
    if additional.get("growth_phase") is not None:
        raise RuntimeError("V4 inactive growth phase is not canonical")
    if additional.get("branch_extra_counts") != {"1": 1, "2": 1, "3": 1}:
        raise RuntimeError("V4 branch extra-count fixture drift")
    if additional.get("additional_edges") != expected_additional_edges:
        raise RuntimeError("V4 additional-node allocation fixture drift")
    if additional.get("orientation") != "parent_to_child":
        raise RuntimeError("V4 additional-node orientation fixture drift")
    if additional.get("fixed_bond_seed_positive") is not True:
        raise RuntimeError("V4 fixed-bond fixture drift")
    if additional.get("expected_tree_edges") != 6:
        raise RuntimeError("V4 tree edge-count fixture drift")
    if additional.get("expected_external_capacity") != 51:
        raise RuntimeError("V4 external-capacity fixture drift")
    if any(
        additional.get(key) is not True
        for key in (
            "row_count_imbalance_at_most_one",
            "column_count_imbalance_at_most_one",
        )
    ):
        raise RuntimeError("V4 axis-balance fixture drift")
    if additional.get("additional_node_resource") != 0:
        raise RuntimeError("V4 additional-node resource fixture drift")

    disabled = fixtures.get("disabled_compatibility", {})
    matrix = disabled.get("matrix", [])
    if {row.get("profile") for row in matrix} != profiles:
        raise RuntimeError("disabled fixture profile roster mismatch")
    if set(disabled.get("surfaces", [])) != {
        "transition",
        "state",
        "observable",
        "lifecycle",
    }:
        raise RuntimeError("disabled fixture surface roster mismatch")
    if disabled.get("independent_case_count") != 40:
        raise RuntimeError("disabled fixture matrix is not 10x4")
    expected_disabled_ids = {
        f"D10.2-EC-DISABLED-{row['profile']}-{surface.upper()}"
        for row in matrix
        for surface in disabled["surfaces"]
    }
    actual_disabled_ids = {
        row[surface] for row in matrix for surface in disabled["surfaces"]
    }
    if actual_disabled_ids != expected_disabled_ids:
        raise RuntimeError("disabled fixture contract IDs do not match the matrix")
    if disabled.get("legacy_target_modified") is not False:
        raise RuntimeError("V4 fixture contract modifies the legacy target")
    legacy_failure = disabled.get("legacy_undefined_expansion_case", {})
    if (
        legacy_failure.get("expected_disposition")
        != "legacy_expansion_target_undefined"
        or legacy_failure.get("committed") is not False
        or legacy_failure.get("prestate_sha256_equals_poststate_sha256") is not True
        or legacy_failure.get("enabled_v4_rule_substituted") is not False
    ):
        raise RuntimeError("V4 legacy-defined-domain fixture drift")


def validate_v4_conformance_contracts(profiles: set[str]) -> None:
    """Validate the corrected catalog, schemas, vectors, and release bundle."""
    fixtures = json.loads(CONFORMANCE_FIXTURES.read_text(encoding="utf-8"))
    if fixtures.get("schema") != "grcv4_conformance_fixture_catalog_v2":
        raise RuntimeError("unexpected V4 conformance catalog schema")
    if fixtures.get("status") != "normative_coverage_catalog_not_executable_vectors":
        raise RuntimeError("V4 conformance catalog claims the wrong authority")
    if fixtures.get("implementation_evidence") is not False:
        raise RuntimeError("preimplementation catalog claims runtime evidence")
    if fixtures.get("implementation_readiness_audit_sha256") != (
        "32cea1b2752361864b02651cb7d38df85929210adc213aa76ee1307babcb5196"
    ):
        raise RuntimeError("V4 catalog readiness-audit binding drift")
    if set(fixtures.get("profile_families", [])) != profiles:
        raise RuntimeError("V4 fixture profile roster mismatch")
    execution = fixtures.get("execution_contract", {})
    if execution.get("catalog_is_not_an_execution_oracle") is not True:
        raise RuntimeError("V4 coverage catalog is presented as an oracle")
    if execution.get("concrete_vector_file") != str(
        CONFORMANCE_VECTORS.relative_to(ROOT)
    ):
        raise RuntimeError("V4 catalog does not bind the concrete vector file")
    if execution.get("machine_schema_file") != str(CONTRACT_SCHEMA.relative_to(ROOT)):
        raise RuntimeError("V4 catalog does not bind the machine schema")

    disabled = fixtures.get("disabled_compatibility", {})
    if disabled.get("independent_case_count") != 40:
        raise RuntimeError("disabled fixture matrix is not 10x4")
    if disabled.get("concrete_vector_status") != (
        "required_before_disabled_compatibility_capability_may_be_advertised"
    ):
        raise RuntimeError("absent disabled vectors are not capability-gated")
    matrix = disabled.get("matrix", [])
    if {row.get("profile") for row in matrix} != profiles:
        raise RuntimeError("disabled fixture profile roster mismatch")
    if disabled.get("legacy_target_modified") is not False:
        raise RuntimeError("V4 fixture catalog modifies the legacy target")

    schema = json.loads(CONTRACT_SCHEMA.read_text(encoding="utf-8"))
    if schema.get("schema_version") != "grcv4-implementation-contract-schema-v1":
        raise RuntimeError("unexpected V4 implementation-contract schema")
    required_schema_definitions = {
        "resolved_params",
        "profile_identity_payload",
        "profile_template_payload",
        "resolved_specialization",
        "specialization_identity_payload",
        "complete_model_identity_payload",
        "port_graph_payload",
        "reset_payload",
        "scientific_state_payload",
        "lifecycle_envelope_payload",
        "expansion_event_request",
        "migration_request",
        "mapped_topology_event_request",
        "migration_policy",
        "history_event_policy",
        "resource_event_map",
        "expansion_event_identity_payload",
        "commit_payload",
        "receipt_core",
        "step_commit_receipt_identity_payload",
        "reset_receipt_identity_payload",
        "rebase_receipt_identity_payload",
        "profile_migration_receipt_identity_payload",
        "topology_event_receipt_identity_payload",
        "charge_receipt_identity_payload",
        "history_disposition_receipt_identity_payload",
        "legacy_compatibility_receipt_identity_payload",
        "successful_receipt_identity_payload",
        "successful_receipt_envelope",
        "failure_receipt_identity_payload",
        "failure_receipt",
    }
    if not required_schema_definitions <= set(schema.get("$defs", {})):
        raise RuntimeError(
            "implementation-contract schema definition roster incomplete"
        )

    jsonschema_cli = shutil.which("jsonschema")
    if jsonschema_cli is None:
        raise RuntimeError("jsonschema CLI is required for contract validation")
    schema_instances: dict[str, list[Any]] = {}

    def validate_schema(definition: str, payload: Any) -> None:
        schema_instances.setdefault(definition, []).append(payload)

    def validate_schema_batches() -> None:
        for definition, payloads in schema_instances.items():
            focused_schema = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "array",
                "items": {"$ref": f"#/$defs/{definition}"},
                "$defs": schema["$defs"],
            }
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", suffix=".json"
            ) as schema_file:
                json.dump(focused_schema, schema_file, allow_nan=False)
                schema_file.flush()
                result = subprocess.run(
                    [
                        jsonschema_cli,
                        "--validator",
                        "Draft202012Validator",
                        schema_file.name,
                    ],
                    input=json.dumps(payloads, ensure_ascii=False, allow_nan=False),
                    capture_output=True,
                    text=True,
                    check=False,
                )
            if result.returncode:
                raise RuntimeError(
                    f"{definition} schema validation failed: "
                    f"{result.stdout.strip()} {result.stderr.strip()}"
                )

    vectors = json.loads(CONFORMANCE_VECTORS.read_text(encoding="utf-8"))
    if vectors.get("schema") != "grcv4_conformance_vectors_v1":
        raise RuntimeError("unexpected concrete-vector schema")
    if vectors.get("implementation_evidence") is not False:
        raise RuntimeError("preimplementation vectors claim runtime execution")
    bindings = vectors.get("bindings", {})
    vector_builder = INVESTIGATION / "scripts/build_grcv4_specification_vectors.py"
    if bindings.get("builder_path") != str(vector_builder.relative_to(ROOT)):
        raise RuntimeError("vector builder path binding drift")
    if bindings.get("builder_sha256") != sha256_file(vector_builder):
        raise RuntimeError("vector builder hash binding drift")
    if bindings.get("contract_schema_sha256") != sha256_file(CONTRACT_SCHEMA):
        raise RuntimeError("vector/schema binding drift")
    if bindings.get("fixture_catalog_sha256") != sha256_file(CONFORMANCE_FIXTURES):
        raise RuntimeError("vector/catalog binding drift")

    expected_canonicalization = {
        "JCS-ASCII-ORDER-AND-FINITE-NUMBERS": (
            '{"a":"é","m":{"a":null,"b":true},"z":[0,0.5,1,-1]}'
        ),
        "JCS-UTF16-PROPERTY-ORDER": '{"😀":2,"":1}',
        "JCS-ECMASCRIPT-SMALL-NUMBER-THRESHOLD": ('{"numbers":[1e-7,0.000001]}'),
    }
    canonicalization_rows = vectors.get("canonicalization_vectors", [])
    if {row["vector_id"] for row in canonicalization_rows} != set(
        expected_canonicalization
    ):
        raise RuntimeError("cross-language canonicalization-vector roster drift")
    for row in canonicalization_rows:
        canonical = row["canonical_jcs_utf8"]
        if canonical != expected_canonicalization[row["vector_id"]]:
            raise RuntimeError(f"{row['vector_id']}: RFC 8785 spelling drift")
        if canonical.encode("utf-8").hex() != row["canonical_jcs_utf8_hex"]:
            raise RuntimeError(f"{row['vector_id']}: canonical byte/hex mismatch")
        if row["expected_identifier"] != (
            f"jcs-example-sha256:{sha256_bytes(canonical.encode('utf-8'))}"
        ):
            raise RuntimeError(f"{row['vector_id']}: canonical identity drift")

    identity_definitions = {
        "IDENTITY-GRCV4-PARAMS-C-OS": ("resolved_params", "grcv4-params-sha256"),
        "IDENTITY-GRCV4-PROFILE-C-OS": (
            "profile_identity_payload",
            "grcv4-profile-sha256",
        ),
        "IDENTITY-GRCV4-PROFILE-TEMPLATE-C-OS": (
            "profile_template_payload",
            "grcv4-profile-template-sha256",
        ),
        "IDENTITY-GRC9V4-PARAMS": ("resolved_specialization", "grc9v4-params-sha256"),
        "IDENTITY-GRC9V4-SPECIALIZATION": (
            "specialization_identity_payload",
            "grc9v4-specialization-sha256",
        ),
        "IDENTITY-GRC9V4-COMPLETE-MODEL": (
            "complete_model_identity_payload",
            "grc9v4-model-sha256",
        ),
        "IDENTITY-GRC9V4-SOURCE-GRAPH": ("port_graph_payload", "grc-graph-sha256"),
        "IDENTITY-GRC9V4-RESET": ("reset_payload", "grcv4-reset-sha256"),
        "IDENTITY-GRCV4-STATE": ("scientific_state_payload", "grcv4-state-sha256"),
        "IDENTITY-GRCV4-LIFECYCLE": (
            "lifecycle_envelope_payload",
            "grcv4-lifecycle-sha256",
        ),
    }
    identity_rows = vectors.get("identity_vectors", [])
    if {row.get("vector_id") for row in identity_rows} != set(identity_definitions):
        raise RuntimeError("identity-vector roster drift")
    for row in identity_rows:
        definition, prefix = identity_definitions[row["vector_id"]]
        validate_schema(definition, row["payload"])
        canonical = row["canonical_jcs_utf8"].encode("utf-8")
        if canonical.hex() != row["canonical_jcs_utf8_hex"]:
            raise RuntimeError(f"{row['vector_id']}: canonical byte/hex mismatch")
        expected = f"{prefix}:{sha256_bytes(canonical)}"
        if row["expected_identifier"] != expected:
            raise RuntimeError(f"{row['vector_id']}: computed identity drift")

    expansion_rows = vectors.get("grc9_expansion_vectors", [])
    if len(expansion_rows) != 10:
        raise RuntimeError("expected ten concrete GRC9 expansion vectors")
    event_ids: set[str] = set()
    covered = set()
    for row in expansion_rows:
        validate_schema("expansion_event_request", row["request"])
        validate_schema(
            "expansion_event_identity_payload", row["event_identity_payload"]
        )
        canonical = row["event_identity_canonical_jcs_utf8"].encode("utf-8")
        event_id = f"grc-event-sha256:{sha256_bytes(canonical)}"
        expected = row["expected"]
        if expected.get("event_id") != event_id:
            raise RuntimeError(f"{row['fixture_id']}: computed event ID drift")
        if event_id in event_ids:
            raise RuntimeError("distinct expansion requests share an event ID")
        event_ids.add(event_id)
        event = row["event_identity_payload"]
        covered.add(
            (
                event["target_effective_degree"],
                event["module_chirality"],
                event["growth_phase"],
            )
        )
        live_nodes = expected["target_live_node_ids"]
        if "source-s" in live_nodes or expected.get("source_node_live_after_commit"):
            raise RuntimeError(f"{row['fixture_id']}: source node survived expansion")
        endpoints = []
        edge_ids = []
        for edge in expected["target_edges"]:
            edge_ids.append(edge["edge_id"])
            endpoints.extend(
                (endpoint["node_id"], endpoint["port"])
                for endpoint in (edge["tail"], edge["head"])
            )
            if (
                edge["kind"] != "boundary"
                and edge["tail"]["port"] != edge["head"]["port"]
            ):
                raise RuntimeError(f"{row['fixture_id']}: non-same-port internal edge")
        if len(endpoints) != len(set(endpoints)):
            raise RuntimeError(f"{row['fixture_id']}: endpoint-port collision")
        if len(edge_ids) != len(set(edge_ids)):
            raise RuntimeError(f"{row['fixture_id']}: duplicate edge identity")
        if sum(expected["target_resource_by_node"].values()) != 3:
            raise RuntimeError(f"{row['fixture_id']}: resource map is not conservative")
        payloads = expected["identity_payloads"]
        if payloads["target_graph"] != {
            "schema_version": "grc9v4-port-graph-v1",
            "live_node_ids": live_nodes,
            "edges": expected["target_edges"],
        }:
            raise RuntimeError(f"{row['fixture_id']}: target graph payload drift")
        payload_contracts = {
            "target_graph": (
                "port_graph_payload",
                "grc-graph-sha256",
                "target_graph_digest",
            ),
            "target_params": (
                "resolved_params",
                "grcv4-params-sha256",
                "target_params_id",
            ),
            "target_profile": (
                "profile_identity_payload",
                "grcv4-profile-sha256",
                "target_complete_profile_id",
            ),
            "target_model": (
                "complete_model_identity_payload",
                "grc9v4-model-sha256",
                "target_model_identity",
            ),
            "target_reset": (
                "reset_payload",
                "grcv4-reset-sha256",
                "target_reset_digest",
            ),
            "target_state": (
                "scientific_state_payload",
                "grcv4-state-sha256",
                "target_state_digest",
            ),
            "receipt": (
                "topology_event_receipt_identity_payload",
                "grc-receipt-sha256",
                "emitted_receipt_ids",
            ),
            "commit": ("commit_payload", "grc-commit-sha256", "commit_id"),
            "target_lifecycle": (
                "lifecycle_envelope_payload",
                "grcv4-lifecycle-sha256",
                "target_lifecycle_digest",
            ),
        }
        for payload_name, (
            definition,
            prefix,
            expected_field,
        ) in payload_contracts.items():
            payload = payloads[payload_name]
            validate_schema(definition, payload)
            canonical_payload = json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
            computed = f"{prefix}:{sha256_bytes(canonical_payload)}"
            recorded = expected[expected_field]
            if isinstance(recorded, list):
                recorded = recorded[0]
            if computed != recorded:
                raise RuntimeError(
                    f"{row['fixture_id']}: {payload_name} identity drift"
                )
        for receipt in expected["emitted_receipts"]:
            validate_schema("successful_receipt_envelope", receipt)
            identity_payload = receipt["identity_payload"]
            canonical_receipt = json.dumps(
                identity_payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
            # All current receipt identity values use the JSON/JCS common subset.
            if receipt["receipt_id"] != (
                f"grc-receipt-sha256:{sha256_bytes(canonical_receipt)}"
            ):
                raise RuntimeError(f"{row['fixture_id']}: receipt identity drift")
            if receipt["commit_id"] != expected["commit_id"]:
                raise RuntimeError(f"{row['fixture_id']}: receipt/commit mismatch")

    required_coverage = (
        {(30, chirality, None) for chirality in (-1, 1)}
        | {(31, chirality, phase) for chirality in (-1, 1) for phase in (1, 2, 3)}
        | {(45, chirality, None) for chirality in (-1, 1)}
    )
    if covered != required_coverage:
        raise RuntimeError("chirality/phase/deeper-tree vector coverage drift")

    failures = vectors.get("atomic_failure_vectors", [])
    if len(failures) != 5 or any(
        row.get("expected", {}).get("prestate_digest")
        != row.get("expected", {}).get("poststate_digest")
        or row.get("expected", {}).get("pre_lifecycle_digest")
        != row.get("expected", {}).get("post_lifecycle_digest")
        or row.get("expected", {}).get("persistent_receipt_append_count") != 0
        for row in failures
    ):
        raise RuntimeError("atomic-failure vector contract drift")
    for row in failures:
        receipt = row["expected"]["failure_receipt"]
        validate_schema("failure_receipt", receipt)
        failure_payload = receipt["identity_payload"]
        canonical_failure = json.dumps(
            failure_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        if receipt["receipt_id"] != (
            f"grc-receipt-sha256:{sha256_bytes(canonical_failure)}"
        ):
            raise RuntimeError(f"{row['fixture_id']}: failure receipt identity drift")
    if len(vectors.get("migration_policy_matrix", [])) != 7:
        raise RuntimeError("migration policy matrix is incomplete")
    required_holds = {
        "candidate_a_numeric_vectors",
        "per_realization_step_vectors",
        "RG2b_vectors",
        "child_stabilization_vectors",
        "disabled_GRC9V3_delegate_vectors",
        "lifecycle_snapshot_reset_migration_vectors",
        "generic_mapped_topology_vectors",
        "charge_precision_edge_vectors",
        "deep_immutability_runtime_tests",
        "runtime_execution_receipts",
    }
    if set(vectors.get("coverage_holds", {})) != required_holds:
        raise RuntimeError("preimplementation vector capability holds drift")

    validate_schema_batches()

    release = json.loads(RELEASE_MANIFEST.read_text(encoding="utf-8"))
    if release.get("schema") != "grcv4_specification_release_manifest_v1":
        raise RuntimeError("unexpected specification release schema")
    if release.get("status") != "normative_preimplementation_release":
        raise RuntimeError("specification release overstates implementation status")
    expected_release_artifacts = {
        str(path.relative_to(ROOT))
        for path in (
            GRCV4_SPEC,
            GRC9V4_SPEC,
            V4_INTERFACE_EXTENSION,
            CONFORMANCE_FIXTURES,
            CONFORMANCE_VECTORS,
            CONTRACT_SCHEMA,
            SOURCE_MANIFEST,
            SPECS_README,
            BOUNDARY_PATH,
            INVESTIGATION
            / "specification/D11PaperPropagationAndSpecificationExtractionGate.json",
            INVESTIGATION
            / "specification/GRCV4SpecificationEngineeringCorrectionGate.json",
            INVESTIGATION / "scripts/audit_grcv4_post_d10_specifications.py",
        )
    }
    if {
        row["path"] for row in release["artifact_members"]
    } != expected_release_artifacts:
        raise RuntimeError("specification release artifact roster drift")
    release_members = [
        *release["artifact_members"],
        *release["packaged_source_bytes"],
        *release["creation_tools"],
    ]
    for row in release_members:
        path = validate_repository_path(row["path"])
        if sha256_file(path) != row["sha256"]:
            raise RuntimeError(f"release member drift: {row['path']}")
    canonical_release = release["release_identity_canonical_jcs_utf8"].encode("utf-8")
    reconstructed_release = json.dumps(
        release["release_identity_payload"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    if canonical_release != reconstructed_release:
        raise RuntimeError("specification release canonical payload drift")
    expected_release_id = f"grcv4-spec-release-sha256:{sha256_bytes(canonical_release)}"
    if release["release_id"] != expected_release_id:
        raise RuntimeError("specification release identity drift")
    if release.get("bundle_digest") != f"sha256:{sha256_bytes(canonical_release)}":
        raise RuntimeError("specification release bundle digest drift")
    checksum_line = RELEASE_CHECKSUM.read_text(encoding="utf-8")
    expected_line = (
        f"{sha256_file(RELEASE_MANIFEST)}  {RELEASE_MANIFEST.relative_to(ROOT)}\n"
    )
    if checksum_line != expected_line:
        raise RuntimeError("specification release detached checksum drift")


def validate_forensic_specification_content() -> tuple[int, int, int, int, int]:
    if repository_root() != ROOT:
        raise RuntimeError("repository root discovery disagrees with audit location")
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        raise RuntimeError("run with the repository .venv Python")

    context = load_successor_forensic_context(ROOT, SIDE_TOOL_ROOT)
    if context.source_bundle_digest != EXPECTED_SOURCE_BUNDLE_DIGEST:
        raise RuntimeError("accepted source bundle digest changed")
    if context.graph_digest != EXPECTED_GRAPH_DIGEST:
        raise RuntimeError("accepted forensic graph digest changed")

    identifiers = {
        kind: sorted(
            row["identifier"] for row in context.nodes.values() if row["kind"] == kind
        )
        for kind in EXPECTED_COUNTS
    }
    counts = {kind: len(rows) for kind, rows in identifiers.items()}
    if counts != EXPECTED_COUNTS:
        raise RuntimeError(f"unexpected accepted populations: {counts}")

    claim_traces = query_all(
        context, "claims", identifiers["current_claim"], reconstruction_path
    )
    query_all(context, "objects", identifiers["normative_object"], object_dependents)
    contract_traces = query_all(
        context,
        "contracts",
        identifiers["equation_contract"],
        contract_provenance,
    )
    negative_trace = negative_claims(context)
    validate_trace("negative_claims", negative_trace)
    write_trace(OUTPUT_DIR / "negative-claims.json", negative_trace)
    if negative_trace["row_count"] != 14:
        raise RuntimeError("unexpected negative-claim row population")

    claim_counts = Counter(
        reconstructed_claim(identifier, trace)["attributes"]["claim_class"]
        for identifier, trace in claim_traces.items()
    )
    if claim_counts != EXPECTED_CLAIM_COUNTS:
        raise RuntimeError(f"unexpected claim partition: {claim_counts}")

    contracts: list[dict[str, Any]] = []
    for identifier, trace in contract_traces.items():
        row = trace["rows"][0]
        if identifier.startswith("D11-C-"):
            expected_successor_semantic = (
                EXPECTED_D11_SUPPORT_DISPOSITION_OVERRIDES.get(
                    identifier, "accepted_bounded_D11_C_successor"
                )
            )
        elif identifier.startswith("D11-G9-"):
            expected_successor_semantic = (
                EXPECTED_D11_SUPPORT_DISPOSITION_OVERRIDES.get(
                    identifier, "accepted_bounded_GRC9V4_successor"
                )
            )
        else:
            expected_successor_semantic = None
        if expected_successor_semantic is None:
            semantics = {
                edge["support_semantic"]
                for trace_row in trace["rows"]
                for edge in trace_row["edge_refs"]
                if edge["relation"] in {"accepted_claim", "parent_object"}
            }
            if semantics != {"indeterminate_requires_review"}:
                raise RuntimeError(
                    f"{identifier}: unexpected support semantics {semantics}"
                )
            if row["payload"]["support_disposition"] != "indeterminate_requires_review":
                raise RuntimeError(f"{identifier}: support disposition was flattened")
        else:
            if row["payload"].get("support_disposition") != [
                expected_successor_semantic
            ]:
                raise RuntimeError(
                    f"{identifier}: accepted successor disposition drift"
                )
            if row["payload"].get("accepted_claim_support_semantics") != [
                expected_successor_semantic
            ]:
                raise RuntimeError(
                    f"{identifier}: accepted successor edge semantics drift"
                )
        contracts.append(row["payload"]["contract"])

    try:
        reconstruction_path(context, "D10_2_CL_N_001")
    except KeyError:
        pass
    else:
        raise RuntimeError("source-local D10_2_CL_N_001 resolved as a claim node")

    grcv4_text = GRCV4_SPEC.read_text(encoding="utf-8")
    grc9v4_text = GRC9V4_SPEC.read_text(encoding="utf-8")
    interface_extension_text = V4_INTERFACE_EXTENSION.read_text(encoding="utf-8")
    for path, text in (
        (GRCV4_SPEC, grcv4_text),
        (GRC9V4_SPEC, grc9v4_text),
        (V4_INTERFACE_EXTENSION, interface_extension_text),
    ):
        validate_markdown(path, text)
        validate_pandoc_render(path)
    if EXPECTED_SOURCE_BUNDLE_DIGEST not in grcv4_text:
        raise RuntimeError("GRCV4 spec is missing the accepted source bundle digest")
    if EXPECTED_GRAPH_DIGEST not in grcv4_text:
        raise RuntimeError("GRCV4 spec is missing the accepted forensic graph digest")
    if (
        "(grc-v4-spec.md)" not in grc9v4_text
        or "is imported unchanged" not in grc9v4_text
    ):
        raise RuntimeError("GRC9V4 spec does not import the GRCV4 authority")
    if "(grc-common-interface-v4-ext.md)" not in grcv4_text:
        raise RuntimeError("GRCV4 spec does not bind the V4 interface extension")
    if "(grc-common-interface-v4-ext.md)" not in grc9v4_text:
        raise RuntimeError("GRC9V4 spec does not bind the V4 interface extension")
    required_extension_markers = (
        "(grc-common-interface.md)",
        "(grc-v4-spec.md)",
        "(grc-9-v4-spec.md)",
        "class GRCV4(GRCModel): ...",
        "class GRC9V4(GRCV4): ...",
        "does not alter the interface or behavior of `GRCV2`, `GRCV3`,",
    )
    if any(
        marker not in interface_extension_text for marker in required_extension_markers
    ):
        raise RuntimeError("V4 interface extension is incomplete")
    required_audit_closure_markers = (
        "Accepted Candidate C baseline transport",
        "C-HM-STIFFNESS-BASELINE-v1",
        "D11-C-CL-O-001",
        "D11-C-EC-C-J0-CURRENT",
        r"J_{0,C}(C,T_C(h),h,U)",
        "def step_v4(self, request: GRCV4StepRequest)",
        "def list_supported_profiles(self) -> frozenset[str]",
        "EnabledGRC9V4State | DisabledGRC9V3State",
        "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
        "D11-G9-CL-N-001",
        "D11-G9-EC-PRIMARY-LATIN-TRANSVERSAL",
        r"(c,2)\leftrightarrow(s_1,2)",
        r"(c,6)\leftrightarrow(s_2,6)",
        r"(c,7)\leftrightarrow(s_3,7)",
        r"(c,3)\leftrightarrow(s_1,3)",
        r"(c,4)\leftrightarrow(s_2,4)",
        r"(c,8)\leftrightarrow(s_3,8)",
        "legacy_expansion_target_undefined",
    )
    all_v4_text = "\n".join((grcv4_text, grc9v4_text, interface_extension_text))
    missing_closure_markers = [
        marker for marker in required_audit_closure_markers if marker not in all_v4_text
    ]
    if missing_closure_markers:
        raise RuntimeError(
            f"V4 audit closures are incomplete: {missing_closure_markers}"
        )

    spec_claims = set(re.findall(r"D(?:10|11-C|11-G9)-CL-[A-Z]+-[0-9]{3}", grcv4_text))
    if spec_claims != set(identifiers["current_claim"]):
        raise RuntimeError(
            "GRCV4 claim roster mismatch: "
            f"missing={sorted(set(identifiers['current_claim']) - spec_claims)} "
            f"extra={sorted(spec_claims - set(identifiers['current_claim']))}"
        )

    successor_profiles = {
        "C-HM-STIFFNESS-BASELINE-v1",
        "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
    }
    profiles = set(identifiers["profile"]) - successor_profiles
    if len(profiles) != 10 or not successor_profiles <= set(identifiers["profile"]):
        raise RuntimeError("V4 complete/successor profile partition drift")
    if "C-HM-STIFFNESS-BASELINE-v1" not in grcv4_text:
        raise RuntimeError("GRCV4 spec is missing the accepted D11-C profile")
    if "grc9v4_axis_preserving_chiral_same_port_expansion_v1" not in grc9v4_text:
        raise RuntimeError("GRC9V4 spec is missing the accepted D11-G9 profile")
    validate_v4_source_manifest()
    validate_v4_conformance_contracts(profiles)
    for name, text in (("GRCV4", grcv4_text), ("GRC9V4", grc9v4_text)):
        mentioned = {
            profile
            for profile in profiles
            if re.search(
                rf"(?<![A-Za-z0-9_]){re.escape(profile)}(?![A-Za-z0-9_])",
                text,
            )
        }
        if mentioned != profiles:
            raise RuntimeError(f"{name} profile roster mismatch: {sorted(mentioned)}")

    specialization_contracts = {
        row["identifier"]
        for row in contracts
        if row["attributes"].get("specification_destination") == "GRC9V4_specialization"
    }
    mentioned_contracts = set(re.findall(r"D10\.2-EC-[A-Za-z0-9._-]+", grc9v4_text))
    if mentioned_contracts != specialization_contracts:
        raise RuntimeError(
            "GRC9V4 contract roster mismatch: "
            f"missing={sorted(specialization_contracts - mentioned_contracts)} "
            f"extra={sorted(mentioned_contracts - specialization_contracts)}"
        )
    disabled = {
        row["identifier"]
        for row in contracts
        if row["identifier"].startswith("D10.2-EC-DISABLED-")
    }
    if len(disabled) != 40 or not disabled <= mentioned_contracts:
        raise RuntimeError("GRC9V4 disabled reduction roster mismatch")

    d11_c_contracts = {
        identifier
        for identifier in identifiers["equation_contract"]
        if identifier.startswith("D11-C-")
    }
    d11_g9_contracts = {
        identifier
        for identifier in identifiers["equation_contract"]
        if identifier.startswith("D11-G9-")
    }
    mentioned_d11_c = set(re.findall(r"D11-C-EC-[A-Za-z0-9._-]+", grcv4_text))
    mentioned_d11_g9 = set(re.findall(r"D11-G9-EC-[A-Za-z0-9._-]+", grc9v4_text))
    if mentioned_d11_c != d11_c_contracts:
        raise RuntimeError(
            "GRCV4 D11-C contract roster mismatch: "
            f"missing={sorted(d11_c_contracts - mentioned_d11_c)} "
            f"extra={sorted(mentioned_d11_c - d11_c_contracts)}"
        )
    if mentioned_d11_g9 != d11_g9_contracts:
        raise RuntimeError(
            "GRC9V4 D11-G9 contract roster mismatch: "
            f"missing={sorted(d11_g9_contracts - mentioned_d11_g9)} "
            f"extra={sorted(mentioned_d11_g9 - d11_g9_contracts)}"
        )

    expansion_markers = (
        r"D_{\mathrm{ext,max}}(n)=9n-2(n-1)=7n+2",
        r"\left\lceil\frac{D_{\mathrm{eff}}(s)-2}{7}\right\rceil",
        r"\max\!\left(4,n_{\mathrm{cap}}\right)",
    )
    if any(marker not in grc9v4_text for marker in expansion_markers):
        raise RuntimeError("GRC9V4 canonical expansion equation is incomplete")
    if r"\left\lceil\frac{D_{\mathrm{eff}}(s)}{7}\right\rceil" in grc9v4_text:
        raise RuntimeError("deprecated GRC9V4 expansion formula survived")

    readme = SPECS_README.read_text(encoding="utf-8")
    if not all(
        name in readme
        for name in (
            "grc-common-interface-v4-ext.md",
            "grc-v4-conformance-fixtures.json",
            "grc-v4-conformance-vectors.json",
            "grc-v4-contract-schema.json",
            "grc-v4-source-manifest.json",
            "grc-v4-specification-release.json",
            "grc-v4-spec.md",
            "grc-9-v4-spec.md",
        )
    ):
        raise RuntimeError("spec registry does not name all V4 specifications")

    return (
        len(spec_claims),
        len(identifiers["normative_object"]),
        len(contracts),
        len(profiles),
        len(disabled),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--boundary-only", action="store_true")
    args = parser.parse_args()
    phase, frozen_count = validate_phase_boundary()
    if args.boundary_only:
        print(
            "POST_D10_PHASE_BOUNDARY_PASS "
            f"phase={phase} frozen_preexisting_specs={frozen_count} "
            "entry_state=D10.2_accepted_bounded"
        )
        return 0
    if phase == "successor_investigation":
        successor_audit = INVESTIGATION / "scripts/audit_grc9v4_d11_g9_resolution.py"
        result = subprocess.run(
            [sys.executable, str(successor_audit)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                f"D11-G9 resolution audit failed:\n{result.stdout}\n{result.stderr}"
            )
        print(result.stdout.strip())
        return 0
    if phase in {"proposal_propagation", "paper_propagation"}:
        paper_audit = INVESTIGATION / "scripts/audit_grcv4_d11_paper_propagation.py"
        result = subprocess.run(
            [sys.executable, str(paper_audit)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                f"D11 paper-propagation audit failed:\n{result.stdout}\n{result.stderr}"
            )
        print(result.stdout.strip())
        return 0
    claims, objects, contracts, profiles, disabled = (
        validate_forensic_specification_content()
    )
    print(
        "POST_D10_SPECIFICATION_AUDIT_PASS "
        f"phase={phase} frozen_preexisting_specs={frozen_count} "
        f"source_bundle_digest={EXPECTED_SOURCE_BUNDLE_DIGEST} "
        f"graph_digest={EXPECTED_GRAPH_DIGEST} claims={claims} "
        f"objects={objects} contracts={contracts} profiles={profiles} "
        f"disabled_surfaces={disabled}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
