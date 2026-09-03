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
SPECS_README = ROOT / "specs/README.md"

EXPECTED_SOURCE_BUNDLE_DIGEST = (
    "79e84f7839e1b65f3e55eeadb980e6d8d9b57d240aced93a8bf3a7e82851dffc"
)
EXPECTED_GRAPH_DIGEST = (
    "2776d2aa1aca51f7759c94ed0e9677a04934429b070bb8ea47683cbcd8f218ae"
)
EXPECTED_COUNTS = {
    "current_claim": 39,
    "normative_object": 67,
    "equation_contract": 152,
    "profile": 10,
}
EXPECTED_CLAIM_COUNTS = Counter(
    {
        "normative": 9,
        "optional": 7,
        "conditional": 12,
        "open": 5,
        "negative": 6,
    }
)
PHASE_AUTHORIZATIONS = {
    "specification_writing": "GRCV4_GRC9V4_specification_writing",
    "successor_investigation": (
        "GRCV4_GRC9V4_D11_G9_ACTIVE_AFTER_D11_C_ACCEPTANCE"
    ),
    "implementation": "GRCV4_GRC9V4_implementation",
}

sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.forensic import (  # noqa: E402
    contract_provenance,
    load_forensic_context,
    negative_claims,
    object_dependents,
    reconstruction_path,
    write_trace,
)
from grcv4_explorer.paths import repository_root  # noqa: E402


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
    if boundary.get("schema") != "grcv4_grc9v4_post_d10_specification_boundary_v2":
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
    if phase in {"successor_investigation", "implementation"}:
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
        "specs/grc-v4-source-manifest.json",
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
        "implementation/investigations/grc9v4-constitutive-design/"
        "specification/PostD10SpecificationBoundary.json",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/audit_iteration0_contract.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/run.py",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/scripts/verify_iteration9.py",
    }
    maintenance = set(boundary["authorized_verification_maintenance_paths"])
    if maintenance != expected_maintenance:
        raise RuntimeError("unexpected verification-maintenance path roster")
    for path_text in maintenance:
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

    changed_paths = set(git_lines("diff", "--name-only", base))
    changed_paths.update(git_lines("ls-files", "--others", "--exclude-standard"))
    allowed_paths = set(outputs) | mutable | maintenance
    if phase == "successor_investigation":
        allowed_paths.update(successor_paths)
    if phase == "implementation":
        allowed_paths.add(authority["path"])
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

    if phase in {"specification_writing", "successor_investigation"}:
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
                f"src/tests changed during {phase}: "
                f"{sorted(changed_runtime_paths)}"
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
    if manifest.get("schema") != "grcv4_specification_source_manifest_v1":
        raise RuntimeError("unexpected V4 source-manifest schema")
    if manifest.get("status") != "normative_source_identity":
        raise RuntimeError("V4 source manifest is not normative")
    audit_sha = manifest.get("audit_input", {}).get("sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", audit_sha):
        raise RuntimeError("V4 audit input is not digest-bound")

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

    closures = manifest.get("post_d10_v4_closures", [])
    if {closure.get("closure_id") for closure in closures} != {
        "V4-AUDIT-C-BASELINE-TRANSPORT",
        "V4-AUDIT-G9-PORT-ALLOCATION",
    }:
        raise RuntimeError("V4 post-D10 closure roster mismatch")
    if any(closure.get("backward_evidence") is not False for closure in closures):
        raise RuntimeError("V4 audit closure was promoted to backward evidence")


def validate_v4_conformance_fixtures(profiles: set[str]) -> None:
    fixtures = json.loads(CONFORMANCE_FIXTURES.read_text(encoding="utf-8"))
    if fixtures.get("schema") != "grcv4_conformance_fixture_contract_v1":
        raise RuntimeError("unexpected V4 conformance-fixture schema")
    if fixtures.get("status") != "normative_preimplementation_fixture_contract":
        raise RuntimeError("V4 conformance fixtures have unexpected status")
    if fixtures.get("implementation_evidence") is not False:
        raise RuntimeError("preimplementation fixtures claim runtime evidence")
    if set(fixtures.get("profile_families", [])) != profiles:
        raise RuntimeError("V4 fixture profile roster mismatch")

    required_group_sizes = {
        "common_cases": 8,
        "candidate_a_cases": 9,
        "candidate_c_cases": 10,
        "realization_cases": 5,
        "lifecycle_cases": 10,
    }
    for key, count in required_group_sizes.items():
        if len(fixtures.get(key, [])) != count:
            raise RuntimeError(f"V4 fixture group {key} must contain {count} cases")

    expansion = fixtures.get("grc9_expansion_fixture", {})
    if expansion.get("policy_id") != "grc9v4_collision_free_v1":
        raise RuntimeError("V4 expansion fixture has wrong policy")
    endpoint_rows = expansion.get("internal_edges", [])
    expected_internal_edges = [
        [["c", 2], ["s1", 5]],
        [["c", 5], ["s2", 6]],
        [["c", 8], ["s3", 4]],
    ]
    if endpoint_rows != expected_internal_edges:
        raise RuntimeError("V4 expansion fixture port allocation drift")
    endpoints = [tuple(endpoint) for edge in endpoint_rows for endpoint in edge]
    redirected = expansion.get("redirected_source_endpoints", [])
    expected_redirected = [
        [f"s{1 + ((port - 1) % 3)}", port] for port in range(1, 10)
    ]
    if redirected != expected_redirected:
        raise RuntimeError("V4 expansion fixture column redirection drift")
    endpoints.extend(tuple(endpoint) for endpoint in redirected)
    if len(endpoints) != len(set(endpoints)):
        raise RuntimeError("V4 expansion fixture contains a port collision")
    if len(redirected) != 9:
        raise RuntimeError("V4 expansion fixture does not redirect nine ports")
    assertions = expansion.get("assertions", {})
    required_true_assertions = {
        "unique_live_endpoint_occupancy",
        "column_family_preserved_for_old_boundary",
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
        [
            [f"fixture-expansion/satellite/{column}", parent_port],
            [f"fixture-expansion/extra/00{column}", 5],
        ]
        for column, parent_port in ((1, 2), (2, 1), (3, 1))
    ]
    if additional.get("desired_external_capacity") != 45:
        raise RuntimeError("V4 additional-node fixture capacity drift")
    if additional.get("expected_canonical_node_count") != 7:
        raise RuntimeError("V4 additional-node fixture node-count drift")
    if additional.get("additional_edges") != expected_additional_edges:
        raise RuntimeError("V4 additional-node allocation fixture drift")
    if additional.get("orientation") != "parent_to_child":
        raise RuntimeError("V4 additional-node orientation fixture drift")
    if additional.get("additional_node_resource") != 0:
        raise RuntimeError("V4 additional-node resource fixture drift")

    disabled = fixtures.get("disabled_compatibility", {})
    matrix = disabled.get("matrix", [])
    if {row.get("profile") for row in matrix} != profiles:
        raise RuntimeError("disabled fixture profile roster mismatch")
    if set(disabled.get("surfaces", [])) != {
        "transition", "state", "observable", "lifecycle"
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
        row[surface]
        for row in matrix
        for surface in disabled["surfaces"]
    }
    if actual_disabled_ids != expected_disabled_ids:
        raise RuntimeError("disabled fixture contract IDs do not match the matrix")
    if disabled.get("legacy_target_modified") is not False:
        raise RuntimeError("V4 fixture contract modifies the legacy target")


def validate_forensic_specification_content() -> tuple[int, int, int, int, int]:
    if repository_root() != ROOT:
        raise RuntimeError("repository root discovery disagrees with audit location")
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        raise RuntimeError("run with the repository .venv Python")

    context = load_forensic_context(ROOT, SIDE_TOOL_ROOT)
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
        "Candidate C V4 baseline transport closure",
        "candidate_c_log_sector_potential_flow_v1",
        r"J_{0,C}(C,T_C(h),h,U)",
        "def step_v4(self, request: GRCV4StepRequest)",
        "def list_supported_profiles(self) -> frozenset[str]",
        "EnabledGRC9V4State | DisabledGRC9V3State",
        "grc9v4_collision_free_v1",
        r"(c,2)\leftrightarrow(s_1,5)",
        r"(c,5)\leftrightarrow(s_2,6)",
        r"(c,8)\leftrightarrow(s_3,4)",
    )
    all_v4_text = "\n".join((grcv4_text, grc9v4_text, interface_extension_text))
    missing_closure_markers = [
        marker for marker in required_audit_closure_markers if marker not in all_v4_text
    ]
    if missing_closure_markers:
        raise RuntimeError(
            f"V4 audit closures are incomplete: {missing_closure_markers}"
        )

    spec_claims = set(re.findall(r"D10-CL-[A-Z]+-[0-9]{3}", grcv4_text))
    if spec_claims != set(identifiers["current_claim"]):
        raise RuntimeError(
            "GRCV4 claim roster mismatch: "
            f"missing={sorted(set(identifiers['current_claim']) - spec_claims)} "
            f"extra={sorted(spec_claims - set(identifiers['current_claim']))}"
        )

    profiles = set(identifiers["profile"])
    validate_v4_source_manifest()
    validate_v4_conformance_fixtures(profiles)
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
        if row["attributes"]["specification_destination"] == "GRC9V4_specialization"
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
            "grc-v4-source-manifest.json",
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
                "D11-G9 resolution audit failed:\n"
                f"{result.stdout}\n{result.stderr}"
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
