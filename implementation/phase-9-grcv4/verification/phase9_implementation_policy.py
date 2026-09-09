"""Accepted P9-G1 scope; implementation integrity is not runtime conformance."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
import tomllib

_HERE = Path(__file__).resolve().parent
_presentation_spec = importlib.util.spec_from_file_location(
    "phase9_evidence_presentation", _HERE / "handoff_evidence.py"
)
_presentation = importlib.util.module_from_spec(_presentation_spec)
_presentation_spec.loader.exec_module(_presentation)
_paths_spec = importlib.util.spec_from_file_location(
    "phase9_evidence_paths", _HERE / "evidence_paths.py"
)
_paths = importlib.util.module_from_spec(_paths_spec)
_paths_spec.loader.exec_module(_paths)
REVIEW_INPUT = _presentation.REVIEW_INPUT
normalized_snapshot = _presentation.normalized_snapshot
_old = _HERE / "phase9_policy.py"
if (
    hashlib.sha256(_old.read_bytes()).hexdigest()
    != "c5a1ccb063b97a9a0b8525bf4a48b248aa783e2a3cac4a37403bbbd24596cf83"
):
    raise ValueError("accepted P9-1.7/P9-1.8 checker changed")
_spec = importlib.util.spec_from_file_location("p918_accepted_policy", _old)
planning = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(planning)
prior = planning.prior
ROOT, PHASE, HERE, INV, SIDE, SCRIPTS = (
    getattr(planning, n) for n in ["ROOT", "PHASE", "HERE", "INV", "SIDE", "SCRIPTS"]
)
require, read, sha, canonical, git, safe_path, digest_record = (
    getattr(planning, n)
    for n in [
        "require",
        "read",
        "sha",
        "canonical",
        "git",
        "safe_path",
        "digest_record",
    ]
)
BASELINE = "6e0a507c0fd7e0758392514acce5e79312a2069c"
APPROVAL = PHASE + "tranche-1/P9-1.9-G1Acceptance.json"
APPROVAL_DIGEST = "cd2c52f30477e1042bb903bd0553da237ddccc9cad373afecc1a84e4e0b37ea2"
POLICY = HERE + "Phase9ImplementationBoundary.json"
RECORD = PHASE + "tranche-1/P9-1.9-ExecutionRecord.json"
WORK = PHASE + "runtime/RuntimeWorkManifest.json"
FOUNDATION = PHASE + "tranche-2/P9-2.1-2.2-AcceptanceRecord.json"
FOUNDATION_DIGEST = "1e3f0ddb06b119fa46dc7609d05b7db0c3a4cbc07428c05b8a032da081ae9dd4"
REQUEST_ACCEPTANCE = PHASE + "tranche-2/P9-2.3-AcceptanceRecord.json"
REQUEST_ACCEPTANCE_DIGEST = "ac07a2f7c93538454d9663aba78ca0eb5af385d7975582e4c21682f41ce4c17f"
RESULT_ACCEPTANCE = PHASE + "tranche-2/P9-2.4-AcceptanceRecord.json"
RESULT_ACCEPTANCE_DIGEST = "9d2fd4f0bb0445b9b3c46fd6f7e5b0ff710a8a85aceaeabacad44a477ff365a0"
HARNESS_ACCEPTANCE = PHASE + "tranche-2/P9-2.5-AcceptanceRecord.json"
HARNESS_ACCEPTANCE_DIGEST = "e479a8e5935fc8740b59f96b31651070f842f73f92541bb84dbc1c9d63f59896"
INTEGRATION_ACCEPTANCE = PHASE + "tranche-2/P9-2.6-AcceptanceRecord.json"
INTEGRATION_ACCEPTANCE_DIGEST = "e5ba16731e03dc916b8755c5999ab2b59acf431255612e76e0dcebe108104bc2"
GEOMETRY_ACCEPTANCE = PHASE + "tranche-3/P9-3.1-AcceptanceRecord.json"
GEOMETRY_ACCEPTANCE_DIGEST = "f119e1361500e72f58297bc8186f868954b4065c853fcdd089280a5d28f88618"
STAGE_ACCEPTANCE = PHASE + "tranche-3/P9-3.2-AcceptanceRecord.json"
STAGE_ACCEPTANCE_DIGEST = "425cd05eb85213185a4b531a09c16cefec4be992ac4755d404b5f263e09ebd0a"
RESOURCE_ACCEPTANCE = PHASE + "tranche-3/P9-3.3-AcceptanceRecord.json"
RESOURCE_ACCEPTANCE_DIGEST = "3e71b580090ba1712dbec4a1718653c2057e4062200f3367ba0c1ed7adeae6fa"
NUMERICAL_ACCEPTANCE = PHASE + "tranche-3/P9-3.4-AcceptanceRecord.json"
NUMERICAL_ACCEPTANCE_DIGEST = "0626df41be15fdb2d5a5a7b4fa6f8be52693f8d3ba40297ae98acbe334f480c1"
PRESERVATION_ACCEPTANCE = PHASE + "tranche-3/P9-3.5-AcceptanceRecord.json"
PRESERVATION_ACCEPTANCE_DIGEST = "b866b4b5d9b8b7ecdf087fd6f2a6d879810ec19464a9d3368ddddaf4d2edf43b"
REFERENCE_ACCEPTANCE = PHASE + "tranche-4/P9-4.1-AcceptanceRecord.json"
REFERENCE_ACCEPTANCE_DIGEST = "ff07f5d71ad094d4c28f3fafdd0c0ca1d74f9f34f18678c8ff6909029b24358a"
CURRENT_ACCEPTANCE = PHASE + "tranche-4/P9-4.2-AcceptanceRecord.json"
CURRENT_ACCEPTANCE_DIGEST = "5ce39f22e2999ee6f375648263a5902f883866420b497822cbf7daaa6e043b43"
CONTROLS_ACCEPTANCE = PHASE + "tranche-4/P9-4.3-AcceptanceRecord.json"
CONTROLS_ACCEPTANCE_DIGEST = "b2834e343fc50fa447ca430475a064157d27b431e27eb64ee721ff52e66a6f15"
OS_PASS_ACCEPTANCE = PHASE + "tranche-4/P9-4.4-AcceptanceRecord.json"
OS_PASS_ACCEPTANCE_DIGEST = "37d61d733bf90b794e4c68f0b2d078f7d38b41aa3f4c0679457c24a3161ad074"
OPERATIONS_ACCEPTANCE = PHASE + "tranche-4/P9-4.5-AcceptanceRecord.json"
OPERATIONS_ACCEPTANCE_DIGEST = "b37b037f0baa0fe5e291c96deba0520933070077b8d5a6a64995fbca21b5e274"
LIFECYCLE_BATCH = PHASE + "tranche-4/P9-4.7ab-AuthorizationRecord.json"
LIFECYCLE_BATCH_DIGEST = "fe11cfd2db36a9e1a74301aeaf89e316a3e93e7d3f5ea9d5f1197e199ee27d6b"
SPECIFICATION_CORRECTION = PHASE + "tranche-4/P9-4.7b-SpecificationCorrection.json"
SPECIFICATION_CORRECTION_DIGEST = "56f1d4378eb8273d261b76aff3b128c526fb5064fa3bceace5c73fbb1f9f9903"
CORRECTED_RELEASE_ID = "grcv4-spec-release-sha256:7b8b4d4e32e48fd35f70421cce7f547eebb21dd81389764061efe6e1a8c19886"
CORRECTION_BUILDER = HERE + "build_mapped_vector_release.py"
PARENT_AUTHORITY = INV + "decisions/P9ReceiptParentAuthority.json"
PARENT_AUTHORITY_DIGEST = "ba7d69189c527153828b02c2bb3311899b036a634446de9ad8f36af6592c28f8"
PARENT_RELEASE_BUILDER = HERE + "build_receipt_parent_release.py"
PARENT_RELEASE_ID = "grcv4-spec-release-sha256:f777519824f86c3e9382bcf9b45cba28554351506f354d3f778746e2aaff5c6b"
PARENT_RUNTIME_PATHS = {
    "src/pygrc/models/grc_v4_codec.py", "src/pygrc/models/grc_v4_lifecycle.py",
    "tests/models/test_grc_v4.py", "tests/models/test_grc_v4_lifecycle.py",
    "tests/models/grcv4_reference_oracles.py", "tests/models/grcv4_conformance_harness.py",
    "src/pygrc/models/grc_v4_assets/asset-index.json",
    "src/pygrc/models/grc_v4_assets/grc-v4-specification-release.json",
    "src/pygrc/models/grc_v4_assets/grc-v4-specification-release.sha256",
}
PARENT_SOURCE_PATHS = {
    "implementation/Phase-9-GRCV4-Handoff.md",
    PARENT_AUTHORITY, PARENT_RELEASE_BUILDER,
    INV + "drafts/GRCV4-proposal.md", INV + "drafts/2026-09-GRC-V4.md",
    "specs/grc-v4-spec.md", "specs/grc-common-interface-v4-ext.md",
    "specs/grc-v4-source-manifest.json",
    SIDE + "records/P9492ReceiptParentAdmission.json",
    SIDE + "tool/src/grcv4_explorer/successor.py",
    SIDE + "tool/src/grcv4_explorer/receipt_parents.py",
    SIDE + "docs/AgenticQueryGuide.md",
    SIDE + "tool/scripts/serve_phase9.py",
    SIDE + "tool/scripts/test_p9492_parents.py",
    SIDE + "tool/scripts/discover_sources.py",
    SIDE + "tool/phase9-web/verification.css",
    HERE + "verify_p9492_parents.py",
}
CORRECTED_SPECIFICATION_PATHS = {
    "specs/README.md", "specs/grc-v4-conformance-vectors.json",
    "specs/grc-v4-specification-release.json", "specs/grc-v4-specification-release.sha256",
    INV + "scripts/build_grcv4_specification_vectors.py",
}
# Explicit user-authorized presentation maintenance after accepted P9-3.3
# ce83d7a. Only these original -> presented Git blobs may differ from HEAD.
# The run's /presentation binds the original repository revision and embedded
# audit source. This grants no general path rewrite or evidence-edit permission.
P931_AUDIT_SOURCE_PRESENTATIONS = {
    PHASE + "evidence/P9-3.1/audit-1-native-before/actual.json": (
        "5a0a1f9e7ecefb83990d000aeca8e1f4231195aa",
        "16e79b60efbbbfbd75bea36c570e29dfea83e437",
    ),
    PHASE + "evidence/P9-3.1/audit-1-native-before/run.json": (
        "e065f308d41e4fcc24f606cf4b69ace56fce6096",
        "0e2c18ce206cb1cd177ae9331f01ffd9168a4b4e",
    ),
}
GENERATED = SIDE + "tool/generated/phase9-verification/"
REPORT_SCHEMA = "phase9_G1_pressure_results_v1"
REPORT_FILE = "g1-pressure-results.json"
RECEIPT_SCHEMA = "phase9_verified_receipt_v3"
RECEIPT_FILE = "verification-v3.json"
PORTABLE_REVIEW_PATHS = {
    PHASE + "tranche-1/P9-1.1-SourceCrosswalk.json",
    PHASE + "tranche-1/P9-1.2-DebtInventory.json",
    PHASE + "tranche-1/P9-1.3-VerificationRouting.json",
    PHASE + "tranche-1/P9-1.1-1.3-Review.md",
    PHASE + "tranche-1/P9-1.1-1.3-ExecutionRecord.json",
    PHASE + "tranche-1/P9-1.4-SupportAndDependencies.json",
    PHASE + "tranche-1/P9-1.5-OwnershipAndLegacyBaseline.json",
    PHASE + "tranche-1/P9-1.4-1.5-ExecutionRecord.json",
}
PORTABLE_SOURCE_PATHS = {
    prior.OPENING,
    planning.SNAPSHOT,
    PHASE + "tranche-1/P9-1.6-SuccessorVerification.md",
    INV + "scripts/audit_grc9v4_d10_claim_topology.py",
}
# These publication files have their own integrity check. Their presence and
# bytes are not part of implementation permission or the current runtime tree.
HANDOFF_PATHS = {
    HERE + "handoff/P9-G1-manifest.json",
    HERE + "handoff/P9-G1-outputs.zip",
}
PATHS = {
    # User-authorized P9-4.8 gate review only. This does not add runtime-ready
    # leaves, editable runtime paths, or accepted profile support.
    PHASE + "tranche-4/P9-4.8-Review.md",
    PHASE + "tranche-4/P9-4.8-GateReview.json",
    PHASE + "tranche-4/P9-4.8-Handoff.md",
    HERE + "verify_p948_review.py",
    # Bounded closure inventory only; no runtime-ready leaf or support change.
    PHASE + "tranche-4/P9-4.9.3-EvidenceInventory.md",
    # User-approved P9-4.9.2 successor only; no facade or G2 permission inferred.
    *PARENT_SOURCE_PATHS,
    INV + "decisions/P9ReceiptParentAuthorityProposal.md",
    HERE + "check_p9492_parent_proposal.py",
    APPROVAL,
    POLICY,
    RECORD,
    WORK,
    FOUNDATION,
    REQUEST_ACCEPTANCE,
    RESULT_ACCEPTANCE,
    HARNESS_ACCEPTANCE,
    INTEGRATION_ACCEPTANCE,
    GEOMETRY_ACCEPTANCE,
    STAGE_ACCEPTANCE,
    RESOURCE_ACCEPTANCE,
    NUMERICAL_ACCEPTANCE,
    PRESERVATION_ACCEPTANCE,
    REFERENCE_ACCEPTANCE,
    CURRENT_ACCEPTANCE,
    CONTROLS_ACCEPTANCE,
    OS_PASS_ACCEPTANCE,
    OPERATIONS_ACCEPTANCE,
    LIFECYCLE_BATCH,
    SPECIFICATION_CORRECTION,
    CORRECTION_BUILDER,
    *CORRECTED_SPECIFICATION_PATHS,
    HERE + "phase9_implementation_policy.py",
    HERE + "audit_phase9_implementation.py",
    HERE + "test_phase9_g1.py",
    HERE + "handoff_evidence.py",
    HERE + "test_handoff_evidence.py",
    HERE + "evidence_paths.py",
    HERE + "test_evidence_paths.py",
    _paths.MANIFEST,
    PHASE + "tranche-1/P9-1.9-EvidenceHandoff.md",
    HERE + "inputs/P9-1.9-G1-Acceptance-And-Scoped-Authorization-Pressure-Guide.md",
    PHASE + "tranche-1/P9-1.9-G1Review.md",
    # Portable command presentations and their dependent package hashes only;
    # acceptance() continues to validate the original reviews at BASELINE.
    *PORTABLE_REVIEW_PATHS,
    *PORTABLE_SOURCE_PATHS,
    REVIEW_INPUT,
    "implementation/Phase-9-GRCV4-ImplementationPlan.md",
    "implementation/ImplementationPhases.md",
    "implementation/Phase-9-GRCV4-ImplementationChecklist.md",
    SIDE + "GRCV4ExploratorySideToolImplementationPlan.md",
    SIDE + "GRCV4ExploratorySideToolImplementationChecklist.md",
    SIDE + "docs/Phase9VerificationGuide.md",
    SCRIPTS + "active_phase.py",
    SCRIPTS + "run.py",
    SCRIPTS + "verify_iteration9.py",
    SCRIPTS + "test_phase9_surfaces.py",
    SCRIPTS + "test_phase9_g1_surfaces.py",
    SCRIPTS + "run_phase9_notebook.py",
    SIDE + "tool/src/grcv4_explorer/phase9_verification.py",
    SIDE + "tool/notebooks/phase9_verification.ipynb",
    SIDE + "tool/phase9-web/index.html",
    SIDE + "tool/phase9-web/verification.js",
    SIDE + "tool/phase9-web/verification.test.mjs",
    SIDE + "tool/phase9-web/browser.spec.mjs",
}


def recorded_acceptance(root):
    """Authenticate the user decision against its original historical subjects."""
    prior.ancestor(root, BASELINE)
    value = read(safe_path(root, APPROVAL))
    require(
        value["record_digest"] == digest_record(value) == APPROVAL_DIGEST,
        "untrusted P9-G1 acceptance",
    )
    require(
        value["baseline_commit"] == BASELINE
        and value["release_id"] == prior.RELEASE_ID,
        "stale P9-G1 release or predecessor",
    )
    for row in value["review_bindings"]:
        require(
            sha(git(root, "show", f"{BASELINE}:{row['path']}")) == row["sha256"],
            "accepted review binding changed",
        )
    return value


def acceptance(root):
    """Recorded acceptance plus current source fidelity; not archive retrieval."""
    value = recorded_acceptance(root)
    for row in value["review_bindings"]:
        if row["path"] not in PORTABLE_REVIEW_PATHS | PORTABLE_SOURCE_PATHS | CORRECTED_SPECIFICATION_PATHS | PARENT_SOURCE_PATHS:
            prior.git_exact(root, BASELINE, row["path"])
    check_portable_source_amendments(root)
    check_portable_review_amendments(root)
    return value


def handoff_status(root):
    return _presentation.status(root, root / HERE / "handoff/P9-G1-manifest.json")


def baseline_files(root):
    result = {}
    for item in filter(None, git(root, "ls-tree", "-r", "-z", BASELINE).split(b"\0")):
        header, name = item.split(b"\t", 1)
        mode, kind, oid = header.decode().split()
        name = name.decode()
        if prior.in_scope(name):
            require(kind == "blob", "unsupported protected object")
            result[name] = (mode, oid)
    return result


def check_portable_review_amendments(root):
    """Changing a command's input location cannot change reviewed source meaning."""
    for name in sorted(n for n in PORTABLE_REVIEW_PATHS if n.endswith(".json")):
        expected = json.loads(git(root, "show", f"{BASELINE}:{name}"))
        actual = dict(read(safe_path(root, name)))
        note = actual.pop("command_portability_note", None)
        require(
            note is None or isinstance(note, str), "invalid command portability note"
        )
        for section in ["validation", "correction_validation"]:
            for row in expected.get(section, []):
                if (
                    "audit_grcv4_specification_release_acceptance.py --audit-file "
                    in row.get("command", "")
                ):
                    row["command"] = (
                        row["command"].split(" --audit-file ")[0]
                        + " --audit-file "
                        + prior.INPUT
                    )
        for field in ["artifact_bindings", "source_review_bindings", "source_bindings"]:
            for row in expected.get(field, []):
                if row["path"] in PORTABLE_REVIEW_PATHS | {prior.OPENING}:
                    row["sha256"] = sha(safe_path(root, row["path"]).read_bytes())
        require(
            actual == expected,
            "portability amendment changed reviewed content: " + name,
        )


def check_portable_source_amendments(root):
    """Only the declared presentation changes; original Git subjects stay fixed."""
    for name in sorted(PORTABLE_SOURCE_PATHS):
        original = git(root, "show", f"{BASELINE}:{name}")
        actual = safe_path(root, name).read_bytes()
        if name == planning.SNAPSHOT:
            valid = json.loads(actual) == normalized_snapshot(original)
        elif name.endswith("P9-1.6-SuccessorVerification.md"):
            valid = actual.decode() == _presentation.normalize_text(original.decode())
        elif name == prior.OPENING:
            expected = json.loads(original)
            expected["planning_review"]["source"] = REVIEW_INPUT
            expected["path_normalization"] = {
                "original_revision": BASELINE,
                "original_sha256": sha(original),
                "change": "planning_review.source now locates the same SHA-256-bound bytes in the repository",
            }
            valid = json.loads(actual) == expected
            require(
                sha(safe_path(root, REVIEW_INPUT).read_bytes())
                == expected["planning_review"]["sha256"],
                "planning review input bytes changed",
            )
        else:
            # Generalize the old username-specific prohibition, without changing
            # any claim/topology check or updating a historical audit result.
            expected = re.sub(
                r'"/home/[^"/]+" not in all_text and "Documents/RC-github" not in all_text',
                'not any(prefix in all_text for prefix in ("/home/", "/Users/", "Documents/RC-github"))',
                original.decode(),
            ).encode()
            valid = actual == expected
        require(valid, "path normalization changed historical meaning: " + name)


def integration(name, before, after):
    """Only optional reviewed dependencies/package data or lazy V4 exports."""
    if name == "pyproject.toml":
        old, new = tomllib.loads(before.decode()), tomllib.loads(after.decode())
        extras = new.get("project", {}).get("optional-dependencies", {}).get("v4", [])
        require(
            isinstance(extras, list)
            and all(
                isinstance(s, str)
                and re.fullmatch(
                    r"(?:numpy|rfc8785|jsonschema)(?:(?:==|!=|~=|<=|>=|<|>)[0-9][A-Za-z0-9.,<>=!~*+-]*)?",
                    s,
                )
                for s in extras
            ),
            "unreviewed V4 dependency",
        )
        for value in [old, new]:
            value.get("project", {}).get("optional-dependencies", {}).pop("v4", None)
            package = (
                value.get("tool", {}).get("setuptools", {}).get("package-data", {})
            )
            data = package.pop("pygrc.models.grc_v4_assets", [])
            require(
                isinstance(data, list)
                and set(data)
                <= {
                    "*.json",
                    "*.sha256",
                    "asset-index.json",
                    "grc-v4-contract-schema.json",
                    "grc-v4-specification-release.json",
                    "grc-v4-specification-release.sha256",
                },
                "unreviewed package data",
            )
            if not package:
                value.get("tool", {}).get("setuptools", {}).pop("package-data", None)
        require(old == new, "non-additive dependency integration")
    else:
        old, new = ast.parse(before), ast.parse(after)
        require(
            len(new.body) == len(old.body) + 1
            and all(ast.dump(a) == ast.dump(b) for a, b in zip(old.body, new.body)),
            "legacy export prefix changed",
        )
        # No eager dependency on optional V4 packages when importing older families.
        expected = ast.parse(
            'def __getattr__(name):\n    if name == "GRCV4":\n        from .grc_v4 import GRCV4\n        return GRCV4\n    raise AttributeError(name)\n'
        ).body[0]
        require(
            ast.dump(new.body[-1]) == ast.dump(expected),
            "unreviewed or eager V4 export",
        )


def accepted_foundation(root):
    """The user's commit decisions accept their exact reviewed foundation.

    Current work and green tests cannot add an accepted leaf or runtime support.
    Historical subject bindings stay valid while later leaves extend the code.
    """
    value = read(safe_path(root, FOUNDATION))
    require(value["record_digest"] == digest_record(value) == FOUNDATION_DIGEST,
            "untrusted foundation acceptance")
    require(value["schema"] == "phase9_foundation_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["accepted_iterations"] == ["P9-2.1", "P9-2.2"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid foundation acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted foundation subject changed")
    return value


def accepted_requests(root):
    """User-accepted request foundation; preserve its original committed run."""
    value = read(safe_path(root, REQUEST_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == REQUEST_ACCEPTANCE_DIGEST,
            "untrusted request acceptance")
    require(value["schema"] == "phase9_request_foundation_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == FOUNDATION_DIGEST
            and value["accepted_iterations"] == ["P9-2.3"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid request acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted request subject changed")
    return value


def accepted_results(root):
    """Committed user acceptance, not an inferred passing-harness decision."""
    value = read(safe_path(root, RESULT_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == RESULT_ACCEPTANCE_DIGEST,
            "untrusted result acceptance")
    require(value["schema"] == "phase9_result_foundation_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == REQUEST_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-2.4"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid result acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted result subject changed")
    return value


def accepted_harness(root):
    """User acceptance of the bounded harness, not full-step conformance."""
    value = read(safe_path(root, HARNESS_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == HARNESS_ACCEPTANCE_DIGEST,
            "untrusted harness acceptance")
    require(value["schema"] == "phase9_harness_foundation_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == RESULT_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-2.5"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid harness acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted harness subject changed")
    return value


def accepted_integration(root):
    """Committed P9-2.6 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, INTEGRATION_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == INTEGRATION_ACCEPTANCE_DIGEST,
            "untrusted integration acceptance")
    require(value["schema"] == "phase9_integration_foundation_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == HARNESS_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-2.6"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid integration acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted integration subject changed")
    return value


def accepted_geometry(root):
    """Committed P9-3.1 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, GEOMETRY_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == GEOMETRY_ACCEPTANCE_DIGEST,
            "untrusted geometry acceptance")
    require(value["schema"] == "phase9_geometry_foundation_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == INTEGRATION_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-3.1"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid geometry acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted geometry subject changed")
    return value


def accepted_stages(root):
    """Committed P9-3.2 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, STAGE_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == STAGE_ACCEPTANCE_DIGEST,
            "untrusted stage acceptance")
    require(value["schema"] == "phase9_stage_geometry_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == GEOMETRY_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-3.2"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid stage acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted stage subject changed")
    return value


def accepted_resources(root):
    """Committed P9-3.3 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, RESOURCE_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == RESOURCE_ACCEPTANCE_DIGEST,
            "untrusted resource acceptance")
    require(value["schema"] == "phase9_resource_boundary_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == STAGE_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-3.3"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid resource acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted resource subject changed")
    return value


def accepted_numerical_pressure(root):
    """Committed P9-3.4 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, NUMERICAL_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == NUMERICAL_ACCEPTANCE_DIGEST,
            "untrusted numerical pressure acceptance")
    require(value["schema"] == "phase9_numerical_pressure_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == RESOURCE_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-3.4"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid numerical pressure acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted numerical pressure subject changed")
    return value


def accepted_preservation(root):
    """Committed P9-3.5 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, PRESERVATION_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == PRESERVATION_ACCEPTANCE_DIGEST,
            "untrusted prestate preservation acceptance")
    require(value["schema"] == "phase9_prestate_preservation_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == NUMERICAL_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-3.5"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid prestate preservation acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted prestate preservation subject changed")
    return value


def accepted_reference_transport(root):
    """Committed P9-4.1 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, REFERENCE_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == REFERENCE_ACCEPTANCE_DIGEST,
            "untrusted C reference transport acceptance")
    require(value["schema"] == "phase9_c_reference_transport_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == PRESERVATION_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-4.1"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid C reference transport acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted C reference transport subject changed")
    return value


def accepted_c_current(root):
    """Committed P9-4.2 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, CURRENT_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == CURRENT_ACCEPTANCE_DIGEST,
            "untrusted C stage current acceptance")
    require(value["schema"] == "phase9_c_stage_current_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == REFERENCE_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-4.2"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid C stage current acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted C stage current subject changed")
    return value


def accepted_c_controls(root):
    """Committed P9-4.3 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, CONTROLS_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == CONTROLS_ACCEPTANCE_DIGEST,
            "untrusted C control derivative acceptance")
    require(value["schema"] == "phase9_c_control_derivative_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == CURRENT_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-4.3"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid C control derivative acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted C control derivative subject changed")
    return value

def accepted_os_pass(root):
    """Committed P9-4.4 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, OS_PASS_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == OS_PASS_ACCEPTANCE_DIGEST,
            "untrusted C OS pass acceptance")
    require(value["schema"] == "phase9_c_os_pass_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == CONTROLS_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-4.4"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid C OS pass acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted C OS pass subject changed")
    return value


def accepted_os_operations(root):
    """Committed P9-4.5 acceptance opens only its dependency-ready successors."""
    value = read(safe_path(root, OPERATIONS_ACCEPTANCE))
    require(value["record_digest"] == digest_record(value) == OPERATIONS_ACCEPTANCE_DIGEST,
            "untrusted C OS operations acceptance")
    require(value["schema"] == "phase9_c_os_operations_acceptance_v1"
            and value["status"] == "accepted_by_user"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == OS_PASS_ACCEPTANCE_DIGEST
            and value["accepted_iterations"] == ["P9-4.5"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid C OS operations acceptance scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "accepted C OS operations subject changed")
    return value


def lifecycle_batch_authorization(root):
    """Ordered development grant with accepted, bounded audit-correction closure."""
    value = read(safe_path(root, LIFECYCLE_BATCH))
    require(value["record_digest"] == digest_record(value) == LIFECYCLE_BATCH_DIGEST,
            "untrusted C OS lifecycle batch authorization")
    require(value["schema"] == "phase9_lifecycle_batch_authorization_v1"
            and value["status"] == "user_authorized_batch_accepted_after_correction"
            and value["release_id"] == prior.RELEASE_ID
            and value["predecessor_record_digest"] == OPERATIONS_ACCEPTANCE_DIGEST
            and value["audit_status"] == "findings_closed_after_correction"
            and value["accepted_iterations"] == ["P9-4.6", "P9-4.7a", "P9-4.7b"]
            and value["current_release_id"] == CORRECTED_RELEASE_ID
            and value["execution_order"] == ["P9-4.7a", "P9-4.7b"]
            and value["combined_audit_scope"] == ["P9-4.6", "P9-4.7a", "P9-4.7b"]
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "invalid C OS lifecycle batch scope")
    prior.ancestor(root, value["baseline_commit"])
    for row in value["evidence_bindings"]:
        require(sha(git(root, "show", f"{value['baseline_commit']}:{row['path']}"))
                == row["sha256"], "committed lifecycle batch predecessor changed")
    row = value["audit_response"]
    require(sha(safe_path(root, row["path"]).read_bytes()) == row["sha256"],
            "combined lifecycle audit response changed")
    for row in value["acceptance_bindings"]:
        require(sha(safe_path(root, row["path"]).read_bytes()) == row["sha256"],
                "accepted lifecycle correction evidence changed")
    return value


def accepted_specification_correction(root):
    """Exact bounded successor; historical G1/release decisions are unchanged."""
    value = read(safe_path(root, SPECIFICATION_CORRECTION))
    require(value["record_digest"] == digest_record(value) == SPECIFICATION_CORRECTION_DIGEST,
            "untrusted mapped-vector specification correction")
    require(value["predecessor_release_id"] == prior.RELEASE_ID
            and value["status"] == "accepted_by_user_for_implementation"
            and value["paper_or_equation_change"] is False
            and value["schema_change"] is False,
            "invalid mapped-vector specification correction scope")
    # The old correction is historical authority, not a current-tree veto.
    # The parent successor binds that exact release and freezes all unrelated
    # members. Do not make the old builder reinterpret new paper/spec bytes.
    current_parent_release(root)
    return value


def accepted_parent_authority(root):
    value = read(safe_path(root, PARENT_AUTHORITY))
    require(value["record_digest"] == digest_record(value) == PARENT_AUTHORITY_DIGEST
            and value["status"] == "accepted_by_user_for_implementation"
            and value["G2_accepted"] is False
            and value["accepted_generic_runtime_support"] == []
            and value["admitted_specialization_support_sets"] == [],
            "untrusted receipt-parent implementation authority")
    return value


def current_parent_release(root):
    accepted_parent_authority(root)
    # Use the builder's own CLI/import context. API and notebook callers must
    # not depend on the verifier directory being in their sys.path, or mutate
    # process-global import paths while concurrent read-only queries execute.
    result = subprocess.run(
        [sys.executable, str(safe_path(root, PARENT_RELEASE_BUILDER)), "--check"],
        cwd=root, capture_output=True, text=True,
    )
    require(result.returncode == 0,
            "receipt-parent release check failed: " + result.stdout + result.stderr)
    require(result.stdout.strip() == "P9492_PARENT_RELEASE_PASS release_id=" + PARENT_RELEASE_ID,
            "untrusted receipt-parent successor release")
    return PARENT_RELEASE_ID


def parent_runtime_evidence(root):
    """Admission of retained run facts, not another runtime test implementation."""
    name = PHASE + "evidence/P9-4.9.2/parent-rule/run.json"
    record = read(safe_path(root, name))
    require(record["schema"] == "phase9_leaf_focused_run_v1"
            and record["iteration_id"] == "P9-4.9.2"
            and record["status"] == "passed"
            and record["source_unchanged"] is True
            and record["coverage"]["passed"] is True
            and record["release_id"] == current_parent_release(root)
            and record["G2_accepted"] is False
            and record["accepted_generic_runtime_support"] == []
            and record["admitted_specialization_support_sets"] == [],
            "parent evidence cannot promote scope or hide failed source attribution")
    for path, expected in record["source_bindings"].items():
        require(sha(safe_path(root, path).read_bytes()) == expected,
                "parent evidence input changed: " + path)
    require(all(record["loaded_sources_after"].get(name) == row
                for name, row in record["loaded_sources_before"].items()),
            "parent run loaded-source attribution changed")
    return {"path": name, "sha256": sha(safe_path(root, name).read_bytes()),
            "G2_accepted": False}


def leaf_permissions(root):
    """Readiness from accepted dependencies, never inferred from completion."""
    accepted = {"P9-G1", *accepted_foundation(root)["accepted_iterations"],
                *accepted_requests(root)["accepted_iterations"],
                *accepted_results(root)["accepted_iterations"],
                *accepted_harness(root)["accepted_iterations"],
                *accepted_integration(root)["accepted_iterations"],
                *accepted_geometry(root)["accepted_iterations"],
                *accepted_stages(root)["accepted_iterations"],
                *accepted_resources(root)["accepted_iterations"],
                *accepted_numerical_pressure(root)["accepted_iterations"],
                *accepted_preservation(root)["accepted_iterations"],
                *accepted_reference_transport(root)["accepted_iterations"],
                *accepted_c_current(root)["accepted_iterations"],
                *accepted_c_controls(root)["accepted_iterations"],
                *accepted_os_pass(root)["accepted_iterations"],
                *accepted_os_operations(root)["accepted_iterations"]}
    support = read(
        safe_path(root, PHASE + "tranche-1/P9-1.4-SupportAndDependencies.json")
    )
    crosswalk = read(safe_path(root, PHASE + "tranche-1/P9-1.1-SourceCrosswalk.json"))
    ownership = read(
        safe_path(root, PHASE + "tranche-1/P9-1.5-OwnershipAndLegacyBaseline.json")
    )
    ready = sorted(
        r["iteration_id"]
        for r in support["dependency_edges"]
        if r["requires"] and set(r["requires"]) <= accepted
    )
    # The user explicitly grouped these dependent leaves for one later audit.
    # Preserve the accepted dependency set; add bounded execution permission.
    ready = sorted(set(ready) | set(lifecycle_batch_authorization(root)["authorized_iterations"]))
    accepted_parent_authority(root)
    ready = sorted(set(ready) | {"P9-4.9.2"})
    owners = {}
    for module in ownership["modules"]:
        leaves = {
            leaf
            for group in module["source_groups"]
            for leaf in crosswalk["groups"][group]["implementation_iterations"]
        }
        if module["module_id"] == "grc_v4_codec":
            leaves = {"P9-2.2", "P9-2.3", "P9-2.6"}
        if module["module_id"] in {"grc_v4_state", "grc_v4_step"}:
            # The frozen checklist assigns result/disposition/receipt ownership
            # to P9-2.4, omitted from the coarse source-group iteration lists.
            # Refine only these existing record/composition owners, not lifecycle.
            leaves.add("P9-2.4")
        if module["module_id"] == "grc_v4_step":
            # P9-3.3 explicitly owns the provisional one-resource-write boundary
            # in the frozen checklist; the coarse step group omits this leaf.
            leaves.add("P9-3.3")
            # P9-4.4 explicitly composes the OS pass, single resource write
            # and final-C reconstruction in this provisional pipeline owner.
            leaves.add("P9-4.4")
        if module["module_id"] in {
            "grc_v4_lifecycle", "grc_v4_candidate_c", "grc_v4_geometry", "grc_v4_transport",
        }:
            # P9-4.5's committed positive/atomic-negative vectors need the
            # existing sole lifecycle commit owner and typed numerical failure
            # provenance. This does not open later lifecycle operations.
            leaves.add("P9-4.5")
        if module["module_id"] in {"grc_v4_lifecycle", "grc_v4_codec"}:
            # P9-4.6 owns the C_OS lifecycle receiver and closed snapshot codec.
            leaves.add("P9-4.6")
        if module["module_id"] in {"grc_v4", "grc_v4_codec", "grc_v4_state"}:
            # Mapped-event records, snapshot references and result ownership.
            leaves.add("P9-4.7b")
        for field in ["path", "test_path"]:
            owners[module[field]] = leaves
    for name in [
        "tests/models/grcv4_conformance_harness.py",
        "tests/models/grcv4_reference_oracles.py",
    ]:
        owners[name] = {"P9-2.5"}
    # The successor updates shared fixture binding and historical inspection.
    owners["tests/models/grcv4_reference_oracles.py"].add("P9-4.7b")
    owners["tests/models/grcv4_conformance_harness.py"].add("P9-4.7b")
    for row in read(safe_path(root, APPROVAL))["runtime_targets"]:
        if row["path"].startswith("src/pygrc/models/grc_v4_assets/"):
            owners[row["path"]] = {"P9-2.2", "P9-2.6", "P9-4.7b"}
        elif row["operation"] == "additive_integration":
            # P9-2.2 owns installed identity assets and their reviewed extras.
            # Facade exports remain with the later common-interface leaf.
            owners[row["path"]] = (
                {"P9-2.2", "P9-2.6", "P9-3.1"}
                if row["path"] == "pyproject.toml" else {"P9-2.6"}
            )
    for name in PARENT_RUNTIME_PATHS:
        require(name in owners, "parent successor invents a runtime target")
        # Source/test owners historically share a set. The parent task may
        # update a test without authorizing its paired facade source.
        owners[name] = owners[name] | {"P9-4.9.2"}
    return ready, owners


def work_entries(root, approval):
    value = read(safe_path(root, WORK))
    require(
        set(value)
        == {
            "schema",
            "approval_digest",
            "release_id",
            "entries",
            "accepted_generic_runtime_support",
            "admitted_specialization_support_sets",
            "claim_ceiling",
            "record_digest",
        },
        "work manifest cannot add authority",
    )
    require(
        value["schema"] == "phase9_runtime_work_manifest_v1"
        and value["approval_digest"] == APPROVAL_DIGEST
        and value["release_id"] == prior.RELEASE_ID
        and value["record_digest"] == digest_record(value),
        "stale work manifest",
    )
    require(
        value["accepted_generic_runtime_support"] == []
        and value["admitted_specialization_support_sets"] == [],
        "work manifest cannot grant conformance",
    )
    targets = {r["path"]: r for r in approval["runtime_targets"]}
    checklist = git(
        root,
        "show",
        f"{BASELINE}:implementation/Phase-9-GRCV4-ImplementationChecklist.md",
    ).decode()
    leaves = set(
        re.findall(r"P9-(?:[2-9]|10)\.\d+(?:[a-zA-Z]|-[A-Za-z0-9_-]+)?", checklist)
    )
    # The accepted baseline cannot contain later closure IDs. Register exactly
    # the user-approved successor, not a broad regex-based permission.
    leaves.add("P9-4.9.2")
    rows = value["entries"]
    require(len({r["path"] for r in rows}) == len(rows), "duplicate work target")
    result = {}
    ready, owners = leaf_permissions(root)
    for row in rows:
        require(
            set(row) == {"path", "sha256", "iteration_id"},
            "work entry cannot supply authority",
        )
        name, leaf = row["path"], row["iteration_id"]
        require(leaf in leaves, "unregistered work iteration")
        require(
            not leaf.startswith(("P9-8.", "P9-9.")),
            "specialization requires accepted P9-G3",
        )
        if name in targets:
            require(
                targets[name]["requires_gate"] == "P9-G1",
                "specialization requires accepted P9-G3",
            )
            require(
                leaf in owners.get(name, set()),
                "runtime target belongs to a different owning leaf",
            )
        require(leaf in ready, "owning leaf entry dependencies are not accepted")
        path = safe_path(root, name)
        require(
            not path.stat().st_mode & stat.S_IXUSR, "unapproved executable runtime mode"
        )
        content = path.read_bytes()
        require(sha(content) == row["sha256"], "work content binding mismatch")
        if name in targets:
            target = targets[name]
            require(
                target["requires_gate"] == "P9-G1",
                "specialization requires accepted P9-G3",
            )
            if target["operation"] == "additive_integration":
                before = git(root, "show", f"{BASELINE}:{name}")
                require(
                    sha(before) == target["before_sha256"], "integration baseline drift"
                )
                integration(name, before, content)
            elif name.endswith(".py"):
                ast.parse(content)
            if name.startswith("src/pygrc/models/grc_v4_assets/"):
                filename = Path(name).name
                if filename in {
                    "grc-v4-contract-schema.json",
                    "grc-v4-specification-release.json",
                    "grc-v4-specification-release.sha256",
                }:
                    require(
                        content == safe_path(root, "specs/" + filename).read_bytes(),
                        "packaged accepted asset differs",
                    )
        else:
            tranche = leaf.split("-")[1].split(".")[0]
            records = {
                PHASE + f"tranche-{tranche}/{leaf}-ExecutionRecord.json",
                PHASE + f"tranche-{tranche}/{leaf}-Review.md",
            }
            # The post-acceptance P9-4.3 audit needs a separate index so its
            # accepted review/execution bindings remain reconstructible intact.
            if leaf in {"P9-4.3", "P9-4.6"}:
                records.add(PHASE + "tranche-4/" + leaf + "-AuditFollowup.md")
            evidence = re.fullmatch(
                re.escape(PHASE + f"evidence/{leaf}/")
                + r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}/([^/]+)",
                name,
            )
            require(
                name in records
                or (
                    evidence
                    and evidence[1] in approval["execution_policy"]["evidence_files"]
                ),
                "unapproved runtime or evidence target: " + name,
            )
            if name.endswith("-ExecutionRecord.json"):
                record = json.loads(content)
                require(
                    record["iteration_id"] == leaf
                    and record["release_id"] == (
                        current_parent_release(root) if leaf == "P9-4.9.2" else prior.RELEASE_ID
                    ),
                    "execution record subject mismatch",
                )
                require(
                    record["accepted_generic_runtime_support"] == []
                    and record["admitted_specialization_support_sets"] == [],
                    "execution record cannot grant conformance",
                )
        result[name] = row
    return result


def current_boundary(root):
    approval = acceptance(root)
    policy = read(safe_path(root, POLICY))
    require(
        set(policy)
        == {
            "schema",
            "active_phase",
            "baseline_commit",
            "approval_digest",
            "release_id",
            "artifact_bindings",
            "record_digest",
        },
        "unsupported implementation policy fields",
    )
    require(
        policy["schema"] == "phase9_implementation_boundary_v1"
        and policy["active_phase"] == "implementation"
        and policy["baseline_commit"] == BASELINE
        and policy["approval_digest"] == APPROVAL_DIGEST
        and policy["release_id"] == prior.RELEASE_ID
        and policy["record_digest"] == digest_record(policy),
        "implementation policy binding drift",
    )
    rows = policy["artifact_bindings"]
    bound = PATHS - {POLICY, WORK}
    require(
        len(rows) == len(bound) and {r["path"] for r in rows} == bound,
        "implementation maintenance roster drift",
    )
    for row in rows:
        require(
            sha(safe_path(root, row["path"]).read_bytes()) == row["sha256"],
            "implementation maintenance binding drift: " + row["path"],
        )
    work = work_entries(root, approval)
    presentations = _paths.load_manifest(root)
    # G1 grants creation/update, not deletion/rename of published runtime work.
    # Deliberately published supporting evidence is immutable, apart from the
    # exact user-authorized presentation pairs above and in the path manifest.
    # Every path presentation is also recomputed from its Git preimage. This does NOT
    # require publishing routine failed attempts: relevant development failures
    # may be summarized in the leaf record (see P9-1.9-EvidenceHandoff.md).
    # Removing a manifest row or staging deletion cannot rewrite that evidence.
    runtime_names = {
        r["path"] for r in approval["runtime_targets"] if r["before_sha256"] is None
    }
    for item in filter(None, git(root, "ls-tree", "-r", "-z", "HEAD").split(b"\0")):
        header, raw_name = item.split(b"\t", 1)
        name = raw_name.decode()
        if name in runtime_names or name.startswith(PHASE + "evidence/"):
            require(
                name in work and (root / name).is_file(),
                "published runtime/evidence deletion or rename forbidden",
            )
            if name.startswith(PHASE + "evidence/"):
                oid = header.decode().split()[2]
                current_oid = planning.blob_id(safe_path(root, name).read_bytes())
                require(
                    current_oid == oid
                    or P931_AUDIT_SOURCE_PRESENTATIONS.get(name) == (oid, current_oid)
                    or _paths.permits(presentations, name, oid, current_oid),
                    "published run evidence is immutable",
                )
    _paths.verify(root, presentations)
    baseline = baseline_files(root)
    frozen = 0
    for name, (mode, oid) in baseline.items():
        if name in PATHS or name in work:
            continue
        path = safe_path(root, name)
        require(
            planning.blob_id(path.read_bytes()) == oid, "frozen bytes changed: " + name
        )
        actual_mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
        require(actual_mode == mode, "frozen mode changed: " + name)
        frozen += 1
    accepted_specification_correction(root)
    entries = set(
        filter(
            None,
            git(root, "ls-files", "--cached", "--others", "-z").decode().split("\0"),
        )
    )
    additions = {
        n
        for n in entries
        if prior.in_scope(n) and n not in baseline and not prior.generated(n)
    }
    require(
        additions <= PATHS | HANDOFF_PATHS | set(work),
        "unauthorized source/test/planning addition: "
        + str(sorted(additions - PATHS - HANDOFF_PATHS - set(work))),
    )
    for name in PATHS:
        path = safe_path(root, name)
        require(not path.stat().st_mode & stat.S_IXUSR, "maintenance mode drift")
    record = read(safe_path(root, RECORD))
    require(
        record["approval_digest"] == APPROVAL_DIGEST
        and record["P9_G1_accepted"] is True
        and record["runtime_authorized"] is True
        and record["accepted_generic_runtime_support"] == []
        and record["admitted_specialization_support_sets"] == [],
        "G1 record authority drift",
    )
    names = PATHS | set(work)
    return policy, {
        "protected_baseline_files": frozen,
        "current_artifact_digest": sha(
            canonical(
                [
                    {"path": n, "sha256": sha(safe_path(root, n).read_bytes())}
                    for n in sorted(names)
                ]
            )
        ),
        "registered_runtime_files": len(work),
    }
