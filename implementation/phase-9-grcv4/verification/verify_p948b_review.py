"""P9-4.8B integrated review checks, reusing execution rather than rerunning it.

Validate the historical PASS proposal and the separate explicit user acceptance.
Retain original execution identities; recheck only the acceptance projection.
"""

import argparse
import ast
from copy import deepcopy
import json
import subprocess
import sys
from unittest.mock import patch

import phase9_implementation_policy as policy
import verify_p9493_fixtures as fixtures

ROOT = policy.ROOT
SUBJECT = "c01526c"
SCRIPT = policy.HERE + "verify_p948b_review.py"
RECORD = policy.PHASE + "tranche-4/P9-4.8B-GateReview.json"
OLD_REVIEW = policy.PHASE + "tranche-4/P9-4.8-GateReview.json"
OBLIGATIONS = ("G2-COS-INTERFACE", "G2-COS-PARENTS", "G2-COS-FIXTURES")
CONTRACTS = (
    "P9-EC-RECEIPT-PARENT-CHAIN",
    "P9-EC-RECEIPT-PARENT-ADMISSION",
    "P9-EC-RECEIPT-PARENT-CEILING",
    "P9-EC-ABUNDANCE-INTERFACE",
    "P9-EC-ABUNDANCE-OBSERVATION",
    "P9-EC-ABUNDANCE-FAILURE-AND-CEILING",
    "D10.2-EC-PARENT-L-ORDERED-RECEIPTS",
    "D10.2-EC-PARENT-L-ATOMICITY",
    "D10.2-EC-PARENT-L-SNAPSHOT-RESET",
    "D11-C-EC-C-J0-CURRENT",
)
DEBTS = ("P9-4.9.2-DEBT-PARENTS", "P9-4.9.1a-DEBT-ABUNDANCE")
# Finite byte bindings for separately tested acceptance/discovery/status changes.
# All other captured numerical source remains byte-exact. This is not a waiver
# for arbitrary edits or a relabeling of the historical run as a new execution.
ACCEPTANCE_PROJECTIONS = {
    "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/notebooks/phase9_verification.ipynb": "4789175b7d89d487185761ab9324c311e61e159b2cd789964d1867e6c6c44c69",
    "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/phase9-web/verification.js": "d4d058f8ed8574ef59ab5067d6acbc51bf2cb312e90ab7c9d7cdaa4a763dccc5",
    "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/phase9_verification.py": "1a039083fbaaad5f5282289380e26eb87065481cd80919d9a7c39cb33e0755c5",
    "src/pygrc/models/grc_v4.py": "338ad4195d4c27a492738820b6c88a44b570a9376c2ea5992c1a6fc62b5e5dc4",
    "src/pygrc/models/grc_v4_profile.py": "66441b1c1bd50bd64183dbc39980f2a013f1ce554a10d7364490ff3854ba9988",
    "tests/models/test_grc_v4.py": "54ca792640ccef324db22d9c9275a8ebe274de779a05b2463d802edf3d3d83d7",
    "tests/models/test_grc_v4_candidate_c.py": "c54488109204510e4df2e48b92b651dfcc243f488c1c653f9527742a626867c7",
    "tests/models/test_grc_v4_codec.py": "c9ffa5a9de7e97c1432ab67d308777c78f9982e3b0e9fbed39eb3389f1e16079",
    "tests/models/test_grc_v4_geometry.py": "d0d4f257a9cb991bd8a0b2a55d66914791fe0925182e4db6976c13acd38194d9",
    "tests/models/test_grc_v4_profile.py": "f88de45246927ca3e37a9c60db06eb11d91867b89f58c4b000e95545d8affe6f",
    "tests/models/test_grc_v4_step.py": "d060883a2b355e51eae035799461f6f030253b1e16269b207d9a66e6476c9c4f",
    "tests/models/test_grc_v4_transport.py": "51551796a0e6e344b66f21d1a5767afe39173e1a77639ba9e9271061bff02684"
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binding(name):
    return {
        "path": name,
        "sha256": policy.sha(policy.safe_path(ROOT, name).read_bytes()),
    }


def capture_reuse(current=None):
    """Reuse original evidence with exact separately checked projection bindings."""
    from verify_p95_regressions import TEST_SOURCES, corrected_test_source

    captured = policy.read(ROOT / fixtures.RUN)["source_bindings"]
    current = fixtures.source_hashes() if current is None else current
    # P9-5.1 adds a separate candidate module and tests. The accepted C_OS
    # facade and every old scientific binding remain exact; no A code is used
    # to earn C_OS credit, and this comparison does not grant A conformance.
    added = set(current) - set(captured)
    require(set(captured) <= set(current) and added <= {
        "src/pygrc/models/grc_v4_candidate_a.py",
        "tests/models/test_grc_v4_candidate_a.py",
    }, "captured source population changed")
    corrections = []
    for name, expected in captured.items():
        if name in TEST_SOURCES:
            content = policy.safe_path(ROOT, name).read_bytes()
            require(current[name] == policy.sha(content), "reused test source changed: " + name)
            original = corrected_test_source(name, content)
            require(policy.sha(original) == ACCEPTANCE_PROJECTIONS.get(name, expected),
                    "test correction has a different accepted baseline: " + name)
            corrections.append({"path": name, "original_sha256": expected,
                                "current_sha256": current[name],
                                "change": "finite test-maintenance correction after c61b37c; fresh focused checks in the handoff; historical numerical execution unchanged"})
            continue
        if name in A_EXTENSION_PATHS:
            content = policy.safe_path(ROOT, name).read_bytes()
            require(current[name] == policy.sha(content), "reused source changed: " + name)
            original = policy.git(ROOT, "show", "d5e1ede:" + name)
            require(policy.sha(original) == ACCEPTANCE_PROJECTIONS.get(name, expected),
                    "A extension has a different C baseline: " + name)
            a_extension_projection(name, content)
            corrections.append({"path": name, "original_sha256": expected,
                                "current_sha256": current[name],
                                "change": ("shared split diagnostic correction; exact admission preserved; fresh focused regressions in P9-5.3-AuditFollowup.json" if name in SPLIT_DIAGNOSTIC_PATHS else "A additions only; existing C executable AST preserved; focused C regressions recorded in P9-5.3")})
            continue
        if name not in ACCEPTANCE_PROJECTIONS:
            require(current[name] == expected, "reused source changed: " + name)
            continue
        require(current[name] == ACCEPTANCE_PROJECTIONS[name],
                "change exceeds exact acceptance projection: " + name)
        corrections.append({"path": name, "original_sha256": expected,
                            "current_sha256": current[name],
                            "change": "acceptance_discovery_or_status_separately_tested"})
    return {"original_subject": SUBJECT,
            "additional_candidate_A_sources_not_used_for_C_OS_credit": sorted(added),
            "unchanged_capture_bindings": len(captured) - len(corrections),
            "acceptance_projections": corrections}


# P9-5.3 extends the shared realization/step owners. This finite projection
# removes only the named new A definitions/imports and module documentation;
# every other existing executable statement must match accepted Git source.
# The two exact diagnostic projections below have separate fresh audit tests.
# Historical C execution is not relabeled as a new run of these extensions.
A_EXTENSION_PATHS = {
    "src/pygrc/models/grc_v4_lifecycle.py": (set(), {}),
    "src/pygrc/models/grc_v4_realizations.py": (
        {"_a_os_inputs", "_a_source_geometry", "CandidateAOSPass"},
        {
            (1, "grc_v4_candidate_a"): {("HISTORY_POLICY", None), ("CandidateACurrent", None), ("CandidateADifferentialReference", None), ("CandidateAStageError", None)},
            (1, "grc_v4_geometry"): {("_local_payload", None)},
        },
    ),
    "src/pygrc/models/grc_v4_step.py": (
        {"ProvisionalCandidateAOSStep"},
        {
            (1, "grc_v4_candidate_a"): {("CandidateACurrent", None), ("CandidateADifferentialReference", None), ("CandidateAStageError", None), ("CandidateAWriter", None)},
            (1, "grc_v4_realizations"): {("CandidateAOSPass", None), ("_a_os_inputs", None)},
        },
    ),
    "tests/models/test_grc_v4_realizations.py": (
        {"a_os_fixture", "a_scalar_pass", "a_dense_pass", "CandidateAOSIntegrationTests",
         "a_extreme_split_fixture", "a_split_source_geometry", "split_exact_difference",
         "split_positive_two_by_two", "CandidateAOSAuditTests", "OSSplitResidualAuditTests"},
        {
            (0, "pygrc.models.grc_v4_candidate_a"): {("CandidateACurrent", None), ("CandidateAStageError", None), ("CandidateAWriter", None)},
            (0, "pygrc.models.grc_v4_codec"): {("V4SchemaError", None)},
            (0, "pygrc.models.grc_v4_realizations"): {("CandidateAOSPass", None)},
            (0, "pygrc.models.grc_v4_step"): {("ProvisionalCandidateAOSStep", None)},
            (0, "tests.models.test_grc_v4_candidate_a"): {("current_fixture", "a_current_fixture"), ("scalar_oracle", "a_conductance_oracle"), ("log_writer_oracle", "a_writer_oracle")},
        },
    ),
}


# Only these reviewed diagnostic bodies may differ from the accepted C AST.
# Admission arithmetic, selector logic, receipt construction and publication
# order remain compared. Historical campaigns retain their original subject.
SPLIT_DIAGNOSTIC_PATHS = {
    "src/pygrc/models/grc_v4_realizations.py": "3dcee65572aa2148558bcdd31612860d954bde991ada32f8b5d0201d6303ac30",
    "src/pygrc/models/grc_v4_lifecycle.py": "ffb51ab1e968106a93360a34e10ad9a302f9935c11af2ae5864149716c899b26",
}


def split_diagnostic_projection(name, baseline, current):
    expected = SPLIT_DIAGNOSTIC_PATHS.get(name)
    if expected is None:
        return
    if name.endswith("grc_v4_realizations.py"):
        old = [n for n in baseline.body if isinstance(n, ast.ClassDef) and n.name == "OSSplitResidual"]
        new = [(i, n) for i, n in enumerate(current.body) if isinstance(n, ast.ClassDef) and n.name == "OSSplitResidual"]
        require(len(old) == len(new) == 1, "missing split residual definition")
        i, node = new[0]
        require(policy.sha(ast.dump(node).encode()) == expected,
                "split correction changes existing C beyond reviewed diagnostic: " + name)
        current.body[i] = deepcopy(old[0])
    else:
        def entries(tree):
            return [(n, i) for n in ast.walk(tree) if isinstance(n, ast.Dict)
                    for i, k in enumerate(n.keys)
                    if isinstance(k, ast.Constant) and k.value == "split_residual"]
        old, new = entries(baseline), entries(current)
        require(len(old) == len(new) == 1, "missing split residual observation")
        source, si = old[0]
        target, ti = new[0]
        require(policy.sha(ast.dump(target.values[ti]).encode()) == expected,
                "split correction changes existing C beyond reviewed diagnostic: " + name)
        target.values[ti] = deepcopy(source.values[si])


def a_extension_projection(name, content):
    baseline = ast.parse(policy.git(ROOT, "show", "d5e1ede:" + name))
    current = ast.parse(content)
    split_diagnostic_projection(name, baseline, current)
    additions, imports = A_EXTENSION_PATHS[name]
    found, body = [], []
    for node in current.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in additions:
            found.append(node.name)
            continue
        if isinstance(node, ast.ImportFrom):
            allowed = imports.get((node.level, node.module), set())
            node.names = [a for a in node.names if (a.name, a.asname) not in allowed]
            if not node.names:
                continue
        body.append(node)
    require(len(found) == len(additions) and set(found) == additions,
            "missing or duplicated A extension: " + name)
    current.body = body
    # Only the module's descriptive title changes; function/class docstrings
    # and executable bodies, including all C algorithms, remain compared.
    for tree in (baseline, current):
        require(isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str), "missing module description")
        tree.body = tree.body[1:]
    require(ast.dump(current) == ast.dump(baseline),
            "A extension changes existing C executable source: " + name)
    return policy.sha(ast.dump(baseline).encode())


def retained_fixture_evidence():
    """Current successor for a capture that also bound historical status code."""
    record = policy.read(ROOT / fixtures.RUN)
    require(
        (ROOT / fixtures.RUN).read_bytes()
        == policy.git(ROOT, "show", SUBJECT + ":" + fixtures.RUN),
        "original fixture execution replaced",
    )
    capture_reuse()
    require(
        record["iteration_id"] == "P9-4.9.3"
        and record["base_commit"] == fixtures.BASE
        and record["release_id"] == policy.current_abundance_release(ROOT)
        and record["status"] == "passed"
        and record["source_unchanged"] is True
        and record["coverage"]["passed"] is True
        and record["required_ids"] == sorted(fixtures.REQUIRED)
        and record["results"]["tests_run"] == len(fixtures.REQUIRED)
        and not any(record["results"][k] for k in ("failures", "errors", "skips"))
        and all(
            record["loaded_sources_after"].get(name) == value
            for name, value in record["loaded_sources_before"].items()
        ),
        "invalid retained fixture execution",
    )
    product = fixtures.check_product(record)
    require(
        record["rejected_product_mutations"] == fixtures.pressure(record),
        "changed fixture mutation roster",
    )
    policy.abundance_runtime_evidence(ROOT)
    ready, _ = policy.leaf_permissions(ROOT)
    require("P9-4.9.3" in ready and "P9-4.8B" not in ready, "fixture/gate drift")
    return {"tests": len(fixtures.REQUIRED), **product}


def source_queries():
    side = ROOT / policy.SIDE
    sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.abundance import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance, debt_lifecycle

    context = load_current_forensic_context(ROOT, side)
    return {
        **{key: contract_provenance(context, key) for key in CONTRACTS},
        **{key: debt_lifecycle(context, key) for key in DEBTS},
    }


def source_continuity():
    """Prove the reuse scope; do not relabel original tests as current runs."""
    result = []
    for name, commit in (
        ("src/pygrc/models/grc_v4.py", "7905e7e"),
        ("src/pygrc/models/grc_v4_codec.py", "1f5f5e9"),
    ):
        original = policy.git(ROOT, "show", commit + ":" + name)
        if name.endswith("grc_v4.py"):
            original = original.replace(
                b"Public C_OS adapter with one owner, not an accepted G2 support claim.",
                b"Public C_OS adapter; accepted G2 support is exact-profile, not family-wide.",
            )
        require((ROOT / name).read_bytes() == original,
                "reused public/codec implementation changed: " + name)
        result.append({**binding(name), "implementation_unchanged_since": commit})
    name = "src/pygrc/models/grc_v4_lifecycle.py"

    def definitions(raw):
        return {
            node.name: ast.dump(node, include_attributes=False)
            for node in ast.parse(raw).body
            if isinstance(node, (ast.ClassDef, ast.FunctionDef))
        }

    before = definitions(policy.git(ROOT, "show", "1f5f5e9:" + name))
    after = definitions((ROOT / name).read_bytes())
    changed = {k for k in before if before[k] != after.get(k)}
    added = set(after) - set(before)
    require(
        changed == {"_affine_resource"}
        and added
        == {
            "ResourceTransformDimensionError",
            "_validate_resource_transform_dimensions",
        },
        "lifecycle reuse exceeds the executed dimension correction",
    )
    result.append(
        {
            **binding(name),
            "comparison_subject": "1f5f5e9",
            "changed_definitions": sorted(changed),
            "added_definitions": sorted(added),
            "remaining_definition_ASTs_unchanged": True,
        }
    )
    return result


def review_inputs():
    """Read exact evidence subjects; no tests or numerical operations."""
    from pygrc.core.interfaces import GRCModel
    from pygrc.models.grc_v4 import GRCV4
    from pygrc.models.grc_v4_profile import get_supported_profile, list_supported_profiles

    policy.git(ROOT, "merge-base", "--is-ancestor", SUBJECT, "HEAD")
    require(
        issubclass(GRCV4, GRCModel) and not GRCV4.__abstractmethods__,
        "public facade incomplete",
    )
    acceptance = policy.accepted_g2(ROOT)
    require(sorted(list_supported_profiles()) == acceptance["accepted_generic_runtime_support"]
            and get_supported_profile(fixtures.NOMINATED).to_payload() == acceptance["accepted_profile"],
            "runtime discovery differs from accepted exact declaration")
    run = policy.read(ROOT / fixtures.RUN)
    require(
        binding(fixtures.RUN)["sha256"]
        == "a8f35e74366708bdc1d576e2b2e1f8646e8cf9579061172357b85f8f6f54ee1a",
        "original fixture run replaced",
    )
    require(
        (ROOT / OLD_REVIEW).read_bytes()
        == policy.git(ROOT, "show", SUBJECT + ":" + OLD_REVIEW),
        "historical HOLD changed",
    )
    catalog = policy.read(ROOT / fixtures.CATALOG)
    ids = {
        r["id"]
        for key in ("common_cases", "candidate_c_cases", "lifecycle_cases")
        for r in catalog[key]
    } | {"OS-ONE-PASS"}
    rows = [
        {
            "fixture_id": r["fixture_id"],
            "complete_profile_id": r["complete_profile_id"],
            "execution_pointer": "/fixture_results/" + str(i),
            "evidence_layer": r["evidence_layer"],
        }
        for i, r in enumerate(run["fixture_results"])
        if r["fixture_id"] in ids
    ]
    require(
        len(rows) == 33 and {r["fixture_id"] for r in rows} == ids,
        "incomplete fixture product",
    )
    vector = next(
        r
        for r in run["fixture_results"]
        if r["fixture_id"] == "GENERIC-MAPPED-EVENT-NONZERO-RESOURCE-INCREMENT"
    )
    names = [
        fixtures.RUN,
        OLD_REVIEW,
        policy.PHASE + "tranche-4/P9-4.9.3-ExecutionRecord.json",
        policy.PHASE + "tranche-4/P9-4.9.3-Review.md",
        "specs/grc-v4-spec.md",
        "specs/grc-common-interface-v4-ext.md",
        "specs/grc-common-interface.md",
        "specs/grc-v4-specification-release.json",
        policy.INV + "drafts/2026-09-GRC-V4.md",
        policy.INV + "drafts/GRCV4-proposal.md",
    ]
    for leaf, folder in (
        ("P9-4.9.1", "facade"),
        ("P9-4.9.1a", "abundance"),
        ("P9-4.9.2", "parent-rule"),
    ):
        names += [
            policy.PHASE + "tranche-4/" + leaf + "-Review.md",
            policy.PHASE + "tranche-4/" + leaf + "-ExecutionRecord.json",
            policy.PHASE + "evidence/" + leaf + "/" + folder + "/run.json",
        ]
    return {
        "reviewed_runtime_commit": policy.git(ROOT, "rev-parse", SUBJECT)
        .decode()
        .strip(),
        "release_id": policy.current_abundance_release(ROOT),
        "evidence_bindings": [binding(n) for n in sorted(names)],
        "source_continuity": source_continuity(),
        "capture_reuse": capture_reuse(),
        "source_queries": source_queries(),
        "nominated_complete_profiles": [fixtures.NOMINATED],
        "fixture_rows": rows,
        "mapped_vector": {
            "source_profile": vector["complete_profile_id"],
            "target_profile": vector["target_active_model_identity"],
            "event_id": vector["observation"]["event_id"],
            "request_object": vector["request_object"],
        },
        "public_surface": {
            "GRCModel": True,
            "abstract_methods": [],
            "global_accepted_support": sorted(list_supported_profiles()),
        },
    }


def check_decision(record, actual):
    require(
        record["record_digest"] == policy.digest_record(record),
        "changed review content",
    )
    require(
        record["schema"] == "phase9_g2_successor_review_v1"
        and record["iteration_id"] == "P9-4.8B"
        and record["gate"] == "P9-G2[C_OS]"
        and record["alias"] == "P9-7.7-C_OS",
        "wrong gate or duplicate credit",
    )
    acceptance = policy.accepted_g2(ROOT)
    original_checker = policy.git(ROOT, "show", acceptance["reviewed_commit"] + ":" + SCRIPT)
    require(record["checker"] == {"path": SCRIPT, "sha256": policy.sha(original_checker)},
            "changed historical review checker")
    require(record["inputs"] == actual, "incomplete/changed/borrowed review inputs")
    require(
        record["review_status"] == "proposed_pending_user_acceptance"
        and record["G2_accepted"] is False
        and record["accepted_generic_runtime_support"] == []
        and record["admitted_specialization_support_sets"] == []
        and record["new_runtime_authorization"] is False,
        "review is not user acceptance or new implementation permission",
    )
    obligations = record["obligations"]
    require(
        len(obligations) == 3 and {r["id"] for r in obligations} == set(OBLIGATIONS),
        "erased closure obligation",
    )
    for row in obligations:
        require(
            row["assessment"] in {"satisfied_for_nominated_scope", "open"}
            and bool(row["reason"])
            and bool(row["evidence"]),
            "missing substantive assessment",
        )
        require(
            set(row["evidence"]) <= {r["path"] for r in actual["evidence_bindings"]},
            "unbound assessment evidence",
        )
    open_ids = sorted(r["id"] for r in obligations if r["assessment"] == "open")
    require(record["open_blockers"] == open_ids, "unresolved blocker hidden")
    require(
        record["verdict"] == ("HOLD" if open_ids else "PASS"),
        "verdict contradicts assessment",
    )
    require(
        record["proposed_generic_runtime_support"]
        == ([] if open_ids else [fixtures.NOMINATED]),
        "unreviewed or family-wide proposed support",
    )
    require(
        record["source_debt_policy"]
        == "preserve_bounded_design_and_forward_rows_not_global_closure",
        "lineage debt silently erased",
    )


def pressure(record, actual):
    check_decision(record, actual)
    hold = deepcopy(record)
    hold["obligations"][2]["assessment"] = "open"
    hold.update(
        verdict="HOLD",
        open_blockers=["G2-COS-FIXTURES"],
        proposed_generic_runtime_support=[],
    )
    hold["record_digest"] = policy.digest_record(hold)
    check_decision(hold, actual)  # A valid HOLD too: not hard-coded PASS/HOLD.
    mutations = {
        "missing_fixture": lambda r: r["inputs"]["fixture_rows"].pop(),
        "duplicate_fixture": lambda r: r["inputs"]["fixture_rows"].append(
            r["inputs"]["fixture_rows"][0]
        ),
        "empty_population": lambda r: r["inputs"].update(
            nominated_complete_profiles=[]
        ),
        "family_substitution": lambda r: r["inputs"].update(
            nominated_complete_profiles=["C_OS"]
        ),
        "unreviewed_support": lambda r: r["proposed_generic_runtime_support"].append(
            "C_OS"
        ),
        "borrowed_mapped_identity": lambda r: r["inputs"]["mapped_vector"].update(
            event_id="grc-event-sha256:" + "0" * 64
        ),
        "erased_parent_debt": lambda r: r["inputs"]["source_queries"].pop(
            "P9-4.9.2-DEBT-PARENTS"
        ),
        "promoted_historical_contract": lambda r: r["inputs"]["source_queries"][
            "D10.2-EC-PARENT-L-ORDERED-RECEIPTS"
        ]["rows"][0]["payload"].update(support_disposition=["required"]),
        "erased_obligation": lambda r: r["obligations"].pop(1),
        "outstanding_blocker_PASS": lambda r: r["obligations"][2].update(
            assessment="open"
        ),
        "premature_acceptance": lambda r: r.update(G2_accepted=True),
        "premature_registry": lambda r: r["accepted_generic_runtime_support"].append(
            fixtures.NOMINATED
        ),
        "stale_release": lambda r: r["inputs"].update(
            release_id="grcv4-spec-release-sha256:" + "0" * 64
        ),
    }
    for label, mutate in mutations.items():
        changed = deepcopy(record)
        mutate(changed)
        changed["record_digest"] = policy.digest_record(changed)
        try:
            check_decision(changed, actual)
        except ValueError:
            continue
        raise ValueError("review mutation escaped: " + label)
    # Test actual capture-reuse validation, not just a rehashed review payload.
    hashes = fixtures.source_hashes()
    for name in [*ACCEPTANCE_PROJECTIONS, "src/pygrc/models/grc_v4_lifecycle.py"]:
        changed = {**hashes, name: "0" * 64}
        try:
            capture_reuse(changed)
        except ValueError:
            continue
        raise ValueError("unreviewed source change escaped: " + name)
    return {
        "valid_controls": [
            "PASS_proposal_without_acceptance",
            "HOLD_with_open_obligation",
        ],
        "rejected_mutations": sorted(mutations),
        "rejected_source_changes": [*ACCEPTANCE_PROJECTIONS, "src/pygrc/models/grc_v4_lifecycle.py"],
    }


def acceptance_pressure():
    original = policy.accepted_g2(ROOT)
    real_read = policy.read
    mutations = {
        "forged_acceptance": lambda r: r.update(status="proposed_pending_user_acceptance"),
        "family_support": lambda r: r.update(accepted_generic_runtime_support=["C_OS"]),
        "other_profile": lambda r: r["accepted_generic_runtime_support"].append("A_OS"),
        "G3_promotion": lambda r: r.update(G3_accepted=True),
        "new_runtime_work": lambda r: r.update(new_runtime_iterations_authorized=["P9-8.1"]),
        "borrowed_declaration": lambda r: r["accepted_profile"].update(complete_profile_id="C_OS"),
        "stale_release": lambda r: r.update(release_id="stale"),
        "erased_obligation": lambda r: r["closed_obligations"].pop(),
    }
    for label, mutate in mutations.items():
        changed = deepcopy(original)
        mutate(changed)
        changed["record_digest"] = policy.digest_record(changed)
        def altered(path):
            return changed if path == ROOT / policy.G2_ACCEPTANCE else real_read(path)
        with patch.object(policy, "read", side_effect=altered):
            try:
                policy.accepted_g2(ROOT)
            except ValueError:
                continue
        raise ValueError("acceptance mutation escaped: " + label)
    return sorted(mutations)


def scoped_surfaces():
    # Execute existing real status cells and authority HTTP/browser validators;
    # no socket, desktop/mobile or numerical campaign, and no new UX machinery.
    commands = [
        [
            sys.executable,
            str(ROOT / policy.SCRIPTS / "run_phase9_notebook.py"),
            "--status-only",
        ],
        [
            sys.executable,
            str(ROOT / policy.SCRIPTS / "test_p9491a_abundance.py"),
            "AbundanceAuthorityTests.test_actual_notebook_and_http_handler_match_api_and_fail_closed",
            "AbundanceAuthorityTests.test_actual_browser_validator_matches_api_and_rejects_overclaims",
        ],
    ]
    for cmd in commands:
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        require(
            result.returncode == 0,
            (result.stdout + result.stderr).replace(str(ROOT) + "/", ""),
        )
    sys.path.insert(0, str(ROOT / policy.SCRIPTS))
    from test_phase9_g1_surfaces import acceptance_status_check
    acceptance_status_check(ROOT)
    return {
        "accepted_status_API_browser_and_failure_cleanup": "passed",
        "status_notebook_API": "passed",
        "authority_notebook_HTTP_browser_validator": "passed",
        "full_browser_campaign": "not_rerun",
    }


def inspect():
    record = policy.read(ROOT / RECORD)
    boundary = policy.current_boundary(ROOT)
    reused = retained_fixture_evidence()
    actual = review_inputs()
    acceptance = policy.accepted_g2(ROOT)
    original = policy.git(ROOT, "show", acceptance["reviewed_commit"] + ":" + RECORD)
    require((ROOT / RECORD).read_bytes() == original, "historical review replaced")
    historical = json.loads(original)["inputs"]
    # Only discovery/status projections differ. Scientific authority, retained
    # product, release and all evidence references remain the reviewed inputs.
    for key in set(actual) - {"capture_reuse", "source_continuity", "public_surface"}:
        require(actual[key] == historical[key], "accepted review input drift: " + key)
    controls = pressure(record, historical)
    controls["rejected_acceptance_changes"] = acceptance_pressure()
    surfaces = scoped_surfaces()
    require(
        policy.current_boundary(ROOT) == boundary and review_inputs() == actual,
        "review inputs changed during verification",
    )
    return {
        "status": "passed",
        "review_verdict": record["verdict"],
        "G2_accepted": True,
        "accepted_generic_runtime_support": acceptance["accepted_generic_runtime_support"],
        "G3_accepted": False,
        "numerical_tests_rerun": 0,
        "reused_runtime_tests": reused["tests"],
        "catalog_rows": 33,
        "controls": controls,
        "surfaces": surfaces,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(inspect()))
