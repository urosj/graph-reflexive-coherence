"""P9-4.8B integrated review checks, reusing execution rather than rerunning it.

A consistent PASS proposal is not accepted G2. This checker permits a justified
HOLD too, and never edits a decision, source claim, gate or support register.
"""

import argparse
import ast
from copy import deepcopy
import json
import subprocess
import sys

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
STATUS_CORRECTIONS = {
    policy.SIDE + "tool/phase9-web/verification.js": (
        '"P9-4.9.2","P9-7.2a-C_OS-NH-NH"',
        '"P9-4.9.2","P9-4.9.3","P9-7.2a-C_OS-NH-NH"',
    ),
    policy.SIDE + "tool/src/grcv4_explorer/phase9_verification.py": (
        "P9-4.9.1a abundance availability authority accepted and propagated; "
        "bounded C_OS projection implemented, no numeric definition. Next: "
        "final P9-4.9.3 evidence reconciliation, then one P9-4.8B review. "
        "P9-G2/G3 remain held.",
        "P9-4.9.3 fixture reconciliation accepted; P9-4.8B proposes PASS for "
        "one exact C_OS profile, pending user acceptance. P9-G2/G3 remain "
        "held; accepted support stays empty. No numeric abundance definition.",
    ),
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
    """Reuse the original run, permitting only the two exact status corrections.

    No source binding in the accepted capture is edited or ignored. Scientific
    code, tests, checker and authority implementation must remain byte-exact.
    """
    captured = policy.read(ROOT / fixtures.RUN)["source_bindings"]
    current = fixtures.source_hashes() if current is None else current
    require(set(current) == set(captured), "captured source population changed")
    corrections = []
    for name, expected in captured.items():
        if name not in STATUS_CORRECTIONS:
            require(current[name] == expected, "reused source changed: " + name)
            continue
        original = policy.git(ROOT, "show", SUBJECT + ":" + name)
        require(policy.sha(original) == expected, "original status source changed")
        old, new = (text.encode() for text in STATUS_CORRECTIONS[name])
        require(original.count(old) == 1, "ambiguous status-only correction")
        require(
            policy.sha(original.replace(old, new)) == current[name],
            "change exceeds exact status correction: " + name,
        )
        corrections.append(
            {
                "path": name,
                "original_sha256": expected,
                "current_sha256": current[name],
                "change": "readiness_or_navigation_only_separately_surface_tested",
            }
        )
    return {
        "original_subject": SUBJECT,
        "unchanged_capture_bindings": len(captured) - len(corrections),
        "status_only_corrections": corrections,
    }


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
        require(
            (ROOT / name).read_bytes() == policy.git(ROOT, "show", commit + ":" + name),
            "reused public/codec implementation changed: " + name,
        )
        result.append({**binding(name), "unchanged_since": commit})
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
    from pygrc.models.grc_v4_profile import list_supported_profiles

    policy.git(ROOT, "merge-base", "--is-ancestor", SUBJECT, "HEAD")
    require(
        issubclass(GRCV4, GRCModel) and not GRCV4.__abstractmethods__,
        "public facade incomplete",
    )
    require(not list_supported_profiles(), "unreviewed global runtime support")
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
            "global_accepted_support": [],
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
    require(record["checker"] == binding(SCRIPT), "changed review checker")
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
    for name in [*STATUS_CORRECTIONS, "src/pygrc/models/grc_v4.py"]:
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
        "rejected_source_changes": [*STATUS_CORRECTIONS, "src/pygrc/models/grc_v4.py"],
    }


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
    return {
        "status_notebook_API": "passed",
        "authority_notebook_HTTP_browser_validator": "passed",
        "full_browser_campaign": "not_rerun",
    }


def inspect():
    record = policy.read(ROOT / RECORD)
    boundary = policy.current_boundary(ROOT)
    reused = retained_fixture_evidence()
    actual = review_inputs()
    controls = pressure(record, actual)
    surfaces = scoped_surfaces()
    require(
        policy.current_boundary(ROOT) == boundary and review_inputs() == actual,
        "review inputs changed during verification",
    )
    return {
        "status": "passed",
        "review_verdict": record["verdict"],
        "G2_accepted": False,
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
