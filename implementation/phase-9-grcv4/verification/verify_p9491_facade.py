"""Focused public C_OS verification; reuse the existing exact-source capture.

--capture creates a new generated run. --check reads the retained run without
executing numerical tests; neither command grants G2 or replaces prior runs.
"""

import argparse
from datetime import datetime, timezone
import importlib
import json
import unittest

import verify_p9492_parents as parent

ROOT = parent.ROOT
RUN = "implementation/phase-9-grcv4/evidence/P9-4.9.1/facade/run.json"
SCRIPT = "implementation/phase-9-grcv4/verification/verify_p9491_facade.py"
METHODS = (
    "test_construction_protocols_and_exact_discovery",
    "test_construction_and_restoration_fail_closed",
    "test_strict_input_duration_edges_and_atomic_rejection",
    "test_fixed_default_common_run_and_missing_request",
    "test_run_v4_is_lazy_and_does_not_rollback_consumed_commits",
    "test_observables_are_fresh_staged_detached_and_prepublication",
    "test_public_lifecycle_restore_assignment_and_receipt_parent_delegation",
    "test_save_load_defaults_and_actual_crossings",
)
REQUIRED = {
    "tests.models.test_grc_v4.PublicFacadeTests." + name for name in METHODS
} | {
    "tests.models.test_grc_v4.FoundationIntegrationTests." + name for name in (
        "test_consumed_legacy_imports_and_replacement_boundary",
        "test_explicit_legacy_baseline_and_package_exports_remain_unchanged",
        "test_duration_validation_still_does_not_admit_a_profile_or_context",
    )
} | {
    "tests.models.test_grc_v4.RequestTests.test_harness_payload_is_not_a_production_request_or_hidden_hook",
    "tests.models.test_grc_v4_lifecycle.CandidateCOSOperationTests.test_exact_dyadic_receipts_commit_and_whole_state_identity",
    "tests.models.test_grc_v4_lifecycle.CandidateCOSOperationTests.test_no_cache_input_and_immutable_detached_observations",
}


def source_hashes():
    hashes = parent.source_hashes()
    hashes[SCRIPT] = parent.sha((ROOT / SCRIPT).read_bytes())
    return dict(sorted(hashes.items()))


def capture(destination):
    from tests.models.test_grc_v4_candidate_c import _p941_execute
    from pygrc.models.grc_v4_codec import RELEASE_ID

    importlib.import_module("tests.models.test_grc_v4_transport")
    importlib.import_module("pygrc.models.grc_v4_lifecycle")
    destination = (ROOT / destination).resolve()
    if not destination.is_relative_to(ROOT / parent.SIDE / "tool/generated") or destination.exists():
        raise ValueError("capture requires a fresh repository-relative generated directory")
    suite = unittest.defaultTestLoader.loadTestsFromNames(sorted(REQUIRED))
    before = source_hashes()
    record = {
        "schema": "phase9_leaf_focused_run_v1",
        "iteration_id": "P9-4.9.1", "release_id": RELEASE_ID,
        "base_commit": "d8f26d925272c83c2e289261c6fd988a2b05b4a5",
        "source_bindings": before, "required_ids": sorted(REQUIRED),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "python": parent.platform.python_version(),
        "platform": parent.platform.platform(),
        "dependencies": sorted(f"{d.metadata['Name']}=={d.version}" for d in parent.importlib.metadata.distributions()),
        "environment": {k: parent.os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "PYTHONHASHSEED")},
        "replay_command": ".venv/bin/python " + SCRIPT + " --capture " + str(destination.relative_to(ROOT)),
        "replay_semantics": "Use a fresh generated directory at the commit retaining this run; verify source_bindings. A rerun is a new record, never a replacement of accepted evidence.",
        "claim_ceiling": "Focused C_OS public facade integration, not the 33-case fixture reconciliation or G2 conformance. Abundance is explicitly unavailable: no accepted V4 definition.",
        "G2_accepted": False, "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
    }
    record.update(_p941_execute(
        ROOT, before, REQUIRED, suite, source_hashes,
        extra_modules=frozenset({
            "pygrc.models.grc_v4", "pygrc.models.grc_v4_lifecycle",
            "tests.models.test_grc_v4", "tests.models.test_grc_v4_lifecycle",
        }),
    ))
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "run.json").write_text(json.dumps(record, indent=2).replace(str(ROOT) + "/", "") + "\n")
    print(json.dumps({k: record.get(k) for k in ("status", "results", "capture_error", "failure_output")}))
    return record["status"] == "passed"


def inspect():
    """Accepted facade evidence is historical after the abundance successor."""
    import phase9_implementation_policy as policy
    return {"status": "passed", "scope": "historical_facade_subject",
            **policy.facade_runtime_evidence(ROOT)}


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
