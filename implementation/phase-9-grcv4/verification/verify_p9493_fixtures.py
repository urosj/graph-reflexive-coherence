"""Focused P9-4.9.3 fixture reconciliation; never a G2 acceptance checker.

Capture once at the final sources. --check validates retained content and exact
source attribution without numerical execution or browser/historical reruns.
"""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import importlib
import json
import unittest

import verify_p9491a_abundance as abundance

parent = abundance.parent
ROOT = parent.ROOT
SCRIPT = "implementation/phase-9-grcv4/verification/verify_p9493_fixtures.py"
RUN = "implementation/phase-9-grcv4/evidence/P9-4.9.3/complete-profile/run.json"
BASE = "1f5f5e9"
NOMINATED = "grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d"
CATALOG = "specs/grc-v4-conformance-fixtures.json"
VECTORS = "specs/grc-v4-conformance-vectors.json"
METHODS = {
    "test_grc_v4.CompleteProfileCatalogTests": (
        "test_common_product_and_fresh_second_beat",
        "test_candidate_fixed_stage_product",
        "test_public_stage_and_lifecycle_product",
        "test_public_crossing_product_and_exact_dimension_vector",
        "test_published_mapped_event_through_public_facade",
    ),
    "test_grc_v4_lifecycle.CandidateCOSCrossingTests": (
        "test_unregistered_target_families_and_stale_identity_are_explicit",
        "test_separate_history_channels_reject_invented_retention_loss_and_initializers",
        "test_map_shape_conservation_order_and_numeric_wire_domains",
        "test_native_negative_reset_and_unrepresentable_affine_charge_fail_atomically",
        "test_native_target_current_and_reset_singularities_have_distinct_pressure",
        "test_split_removal_negative_increment_and_stable_identifier_permutation",
        "test_metadata_exclusion_and_crossing_receipt_semantic_corruption",
        "test_target_charge_readmission_checks_reset_independently",
    ),
    "test_grc_v4_lifecycle.CandidateCOSOperationTests": (
        "test_native_solver_geometry_selector_and_split_failures_are_atomic",
        "test_native_postsolve_resource_domain_overflow_and_charge_failures",
    ),
    "test_grc_v4_lifecycle.CandidateCOSAuditCorrectionTests": (
        "test_unreceipted_assignment_preserves_snapshot_continuation_replay",
    ),
    "test_grc_v4_lifecycle.CandidateCOSParentPolicyTests": (
        "test_hash_coherent_wrong_parents_fail_before_atomic_publication",
    ),
    "test_grc_v4_candidate_c.CandidateCControlDerivativeTests": (
        "test_complete_resource_geometry_and_joint_derivatives",
    ),
    "test_grc_v4_candidate_c.CandidateCCurrentTests": (
        "test_actual_current_rejects_lost_physical_conditioning_margin",
    ),
    "test_grc_v4_codec.CodecTests": (
        "test_schema_negatives_and_no_remote_schema_selection",
    ),
    "test_grc_v4_profile.ProfileTests": (
        "test_published_wctr_live_edge_negative",
        "test_published_semantic_parameter_digest_negative",
    ),
}
REQUIRED = {
    "tests.models." + cls + "." + method
    for cls, methods in METHODS.items()
    for method in methods
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    return json.loads((ROOT / name).read_text())


def source_hashes():
    result = abundance.source_hashes()
    result[SCRIPT] = parent.sha((ROOT / SCRIPT).read_bytes())
    return dict(sorted(result.items()))


def check_product(record):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    from pygrc.models.grc_v4_profile import resolve_profile

    catalog = read(CATALOG)
    required_fields = set(catalog["execution_contract"]["required_result_fields"])
    ids = {
        r["id"]
        for group in ("common_cases", "candidate_c_cases", "lifecycle_cases")
        for r in catalog[group]
    } | {"OS-ONE-PASS"}
    require(
        record["nominated_complete_profiles"] == [NOMINATED],
        "empty/family/expanded nomination",
    )
    require(
        record["G2_accepted"] is False
        and record["accepted_generic_runtime_support"] == []
        and record["admitted_specialization_support_sets"] == [],
        "premature support/acceptance",
    )
    rows = record["fixture_results"]
    require(
        len(rows) == 35 and len({r["fixture_id"] for r in rows}) == len(rows),
        "missing/duplicate fixture",
    )
    require(
        {
            (r["complete_profile_id"], r["fixture_id"])
            for r in rows
            if r["fixture_id"] in ids
        }
        == {(NOMINATED, name) for name in ids},
        "incomplete exact-profile Cartesian product",
    )
    objects = record["objects"]
    for key, obj in objects.items():
        require(
            parent.sha(canonical_json_bytes(obj)) == key,
            "changed content-addressed object",
        )
    for row in rows:
        require(required_fields <= row.keys(), "missing required execution field")
        before, after = (
            objects[row[k]] for k in ("prestate_object", "poststate_object")
        )
        profile = before["reference"]["profile"]
        resolved = resolve_profile(
            profile["params_resolved"], profile["identity_payload"]
        )
        require(
            row["complete_profile_id"]
            == resolved.complete_profile_id
            == row["active_model_identity"]
            == before["scientific_state"]["active_model_identity"]
            and row["resolved_params_id"] == resolved.params_resolved.params_hash,
            "borrowed source profile/parameters",
        )
        require(
            row["prestate_digest"] == before["scientific_state_digest"]
            and row["poststate_digest"] == after["scientific_state_digest"]
            and row["target_active_model_identity"]
            == after["scientific_state"]["active_model_identity"],
            "result subject differs from captured snapshots",
        )
        old = [r["receipt_id"] for r in before["receipt_ledger"]]
        new = [r["receipt_id"] for r in after["receipt_ledger"]]
        if row["committed"]:
            require(
                new == old + row["emitted_receipt_ids"]
                and bool(row["emitted_receipt_ids"]),
                "wrong receipt delta",
            )
        else:
            require(before == after, "noncommit mutated full lifecycle")
        if row["result_object"] is not None:
            result = objects[row["result_object"]]
            require(
                result["committed"] == row["committed"]
                and result["operation_disposition"] == row["operation_disposition"]
                and result.get("solver_disposition") == row["solver_disposition"]
                and [r["receipt_id"] for r in result["emitted_receipts"]]
                == row["emitted_receipt_ids"],
                "recorded result projection differs",
            )
        for key in ("request_object", "result_object"):
            require(row[key] is None or row[key] in objects, "unresolved input/output")
    indexed = {r["fixture_id"]: r for r in rows}
    for case in catalog["common_cases"]:
        row = indexed[case["id"]]
        for field in (
            "operation_disposition",
            "solver_disposition",
            "committed",
            "failure_code",
        ):
            if "required_" + field in case:
                require(
                    row[field] == case["required_" + field],
                    "wrong common outcome: " + case["id"],
                )
    stale = indexed["COMMON-STALE-CACHE"]
    require(
        (
            stale["operation_disposition"],
            stale["solver_disposition"],
            stale["committed"],
        )
        == ("committed", "valid_root", True)
        and stale["observation"]["postcondition"] == "cache_rebuilt_before_consumer"
        and stale["observation"]["stale_value_never_consumed"] is True,
        "stale-cache outcome missing",
    )
    negative = read(VECTORS)["semantic_admission"]["negative_vectors"][1]
    row = indexed[negative["vector_id"]]
    require(
        objects[row["request_object"]]["resource_transform"]
        == negative["input"]
        == objects[row["observation"]["exact_vector_input_object"]]
        and row["observation"]["semantic_diagnostic"] == negative["expected"]["code"]
        and row["failure_code"] == "invalid_topology_event"
        and not row["committed"],
        "exact dimension semantic/operation boundary missing",
    )
    vector = read(VECTORS)["grcv4_mapped_topology_event_vectors"][0]
    row = indexed[vector["fixture_id"]]
    require(
        objects[row["request_object"]] == vector["request"]
        and row["observation"]["event_id"] == vector["expected"]["event_id"]
        and row["committed"] is True,
        "borrowed or unexecuted mapped-event identity",
    )
    return {
        "nominated_profiles": 1,
        "catalog_product_rows": len(ids),
        "additional_exact_vectors": 2,
    }


def pressure(record):
    controls = {
        "missing_row": lambda r: r["fixture_results"].pop(),
        "duplicate_row": lambda r: r["fixture_results"].append(r["fixture_results"][0]),
        "empty_nomination": lambda r: r.update(nominated_complete_profiles=[]),
        "family_nomination": lambda r: r.update(nominated_complete_profiles=["C_OS"]),
        "borrowed_profile": lambda r: r["fixture_results"][0].update(
            complete_profile_id="grcv4-profile-sha256:" + "0" * 64
        ),
        "altered_result": lambda r: r["fixture_results"][0].update(committed=True),
        "premature_G2": lambda r: r.update(G2_accepted=True),
        "borrowed_event": lambda r: next(
            x
            for x in r["fixture_results"]
            if x["fixture_id"] == "GENERIC-MAPPED-EVENT-NONZERO-RESOURCE-INCREMENT"
        )["observation"].update(event_id="grc-event-sha256:" + "0" * 64),
    }
    check_product(record)  # Valid product control; not a positive gate review.
    for name, mutation in controls.items():
        changed = deepcopy(record)
        mutation(changed)
        try:
            check_product(changed)
        except (ValueError, KeyError):
            continue
        raise ValueError("fixture mutation escaped: " + name)
    return list(controls)


def capture(destination):
    from tests.models.test_grc_v4_candidate_c import _p941_execute
    from tests.models.test_grc_v4 import CompleteProfileCatalogTests
    from pygrc.models.grc_v4_codec import RELEASE_ID

    for cls in METHODS:
        importlib.import_module("tests.models." + cls.split(".")[0])
    for name in ("tests.models.test_grc_v4_transport", "pygrc.models.grc_v4_lifecycle"):
        importlib.import_module(name)
    destination = (ROOT / destination).resolve()
    require(
        destination.is_relative_to(ROOT / abundance.SIDE / "tool/generated")
        and not destination.exists(),
        "capture needs a fresh repository-relative generated destination",
    )
    before = source_hashes()
    record = {
        "schema": "phase9_leaf_focused_run_v1",
        "iteration_id": "P9-4.9.3",
        "base_commit": BASE,
        "release_id": RELEASE_ID,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "source_bindings": before,
        "required_ids": sorted(REQUIRED),
        "python": parent.platform.python_version(),
        "platform": parent.platform.platform(),
        "dependencies": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in parent.importlib.metadata.distributions()
        ),
        "environment": {
            k: parent.os.environ.get(k)
            for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "PYTHONHASHSEED")
        },
        "replay_command": ".venv/bin/python "
        + SCRIPT
        + " --capture "
        + str(destination.relative_to(ROOT)),
        "replay_semantics": "Use this exact source_bindings subject and a fresh destination. Never replace the original run.",
        "nominated_complete_profiles": [NOMINATED],
        "G2_accepted": False,
        "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
        "claim_ceiling": "One nominated exact C_OS profile product, explicit fault and reidentified controls, separately attributed transition targets. No family-wide, specialization, detector or G2 acceptance.",
    }
    suite = unittest.defaultTestLoader.loadTestsFromNames(sorted(REQUIRED))
    record.update(
        _p941_execute(
            ROOT,
            before,
            REQUIRED,
            suite,
            source_hashes,
            extra_modules=frozenset(
                {
                    "pygrc.models.grc_v4",
                    "pygrc.models.grc_v4_lifecycle",
                    "tests.models.test_grc_v4",
                    "tests.models.test_grc_v4_lifecycle",
                }
            ),
        )
    )
    record["fixture_results"] = CompleteProfileCatalogTests.rows
    record["objects"] = CompleteProfileCatalogTests.objects
    if record["status"] == "passed":
        try:
            record["product_check"] = check_product(record)
            record["rejected_product_mutations"] = pressure(record)
        except Exception as exc:
            record.update(status="failed", product_error=str(exc))
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "run.json").write_text(
        json.dumps(record, indent=2).replace(str(ROOT) + "/", "") + "\n"
    )
    print(
        json.dumps(
            {
                k: record.get(k)
                for k in (
                    "status",
                    "results",
                    "capture_error",
                    "failure_output",
                    "product_error",
                    "product_check",
                )
            }
        )
    )
    return record["status"] == "passed"


def inspect():
    import phase9_implementation_policy as policy

    record = read(RUN)
    require(
        record["iteration_id"] == "P9-4.9.3"
        and record["base_commit"] == BASE
        and record["release_id"] == policy.current_abundance_release(ROOT)
        and record["status"] == "passed"
        and record["source_unchanged"] is True
        and record["coverage"]["passed"] is True
        and record["source_bindings"] == source_hashes()
        and record["required_ids"] == sorted(REQUIRED)
        and record["results"]["tests_run"] == len(REQUIRED)
        and not any(record["results"][k] for k in ("failures", "errors", "skips"))
        and all(
            record["loaded_sources_after"].get(name) == value
            for name, value in record["loaded_sources_before"].items()
        ),
        "fixture execution does not match exact current sources/roster",
    )
    result = check_product(record)
    require(
        record["rejected_product_mutations"] == pressure(record),
        "changed mutation roster",
    )
    policy.abundance_runtime_evidence(ROOT)
    ready, owners = policy.leaf_permissions(ROOT)
    require(
        "P9-4.9.3" in ready and "P9-4.8B" not in ready, "fixture permission/gate drift"
    )
    return {
        "status": "passed",
        "tests": len(REQUIRED),
        **result,
        "G2_accepted": False,
        "numerical_tests_rerun": 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        print(json.dumps(inspect()))
    else:
        raise SystemExit(0 if capture(args.capture) else 1)
