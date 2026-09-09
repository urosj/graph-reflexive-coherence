"""Lean P9-4.9.1a execution using the existing exact-source focused capture.

--capture creates a new run; --check checks retained current evidence plus the
original accepted facade/parent Git subjects. Neither accepts G2.
"""

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import sys
import unittest

import verify_p9491_facade as facade

parent = facade.parent
ROOT = parent.ROOT
SCRIPT = "implementation/phase-9-grcv4/verification/verify_p9491a_abundance.py"
RUN = "implementation/phase-9-grcv4/evidence/P9-4.9.1a/abundance/run.json"
SIDE = parent.SIDE
TOOL_TEST = SIDE + "tool/scripts/test_p9491a_abundance.py"
BASE = "7905e7e22bb2fb37f09d0de01f3f161b83332618"
METHODS = (
    "test_construction_protocols_and_exact_discovery",
    "test_observables_are_fresh_staged_detached_and_prepublication",
    "test_abundance_release_and_observation_failures_do_not_relabel_state",
    "test_abundance_protocol_controls_are_synthetic_not_admission",
    "test_public_lifecycle_restore_assignment_and_receipt_parent_delegation",
    "test_save_load_defaults_and_actual_crossings",
)
TOOL_METHODS = (
    "test_append_only_graph_and_typed_source_boundary",
    "test_source_propagation_and_legacy_immutability",
    "test_mutated_missing_or_unprocessed_authority_fails_closed",
    "test_actual_notebook_and_http_handler_match_api_and_fail_closed",
    "test_actual_browser_validator_matches_api_and_rejects_overclaims",
)
REQUIRED = {"tests.models.test_grc_v4.PublicFacadeTests." + n for n in METHODS} | {
    "p9491a_tool_controls.AbundanceAuthorityTests." + n for n in TOOL_METHODS
}


def source_hashes():
    result = facade.source_hashes()
    names = [SCRIPT, TOOL_TEST, "implementation/phase-9-grcv4/verification/build_abundance_release.py",
             SIDE + "tool/scripts/serve_phase9.py", SIDE + "tool/notebooks/phase9_verification.ipynb",
             SIDE + "tool/phase9-web/verification.js"]
    names += [str(p.relative_to(ROOT)) for p in (ROOT / SIDE / "tool/src/grcv4_explorer").glob("*.py")]
    names += ["implementation/investigations/grc9v4-constitutive-design/decisions/P9AbundanceInterfaceAuthority.json",
              SIDE + "records/P9491aAbundanceAdmission.json"]
    result.update({name: parent.sha((ROOT / name).read_bytes()) for name in names})
    return dict(sorted(result.items()))


def capture(destination):
    from tests.models.test_grc_v4_candidate_c import _p941_execute
    from pygrc.models.grc_v4_codec import RELEASE_ID
    importlib.import_module("tests.models.test_grc_v4_transport")
    importlib.import_module("tests.models.test_grc_v4_lifecycle")
    importlib.import_module("pygrc.models.grc_v4_lifecycle")
    spec = importlib.util.spec_from_file_location("p9491a_tool_controls", ROOT / TOOL_TEST)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    destination = (ROOT / destination).resolve()
    if not destination.is_relative_to(ROOT / SIDE / "tool/generated") or destination.exists():
        raise ValueError("capture requires a fresh repository-relative generated directory")
    suite = unittest.defaultTestLoader.loadTestsFromNames(sorted(REQUIRED))
    before = source_hashes()
    record = {
        "schema": "phase9_leaf_focused_run_v1", "iteration_id": "P9-4.9.1a",
        "release_id": RELEASE_ID, "base_commit": BASE,
        "source_bindings": before, "required_ids": sorted(REQUIRED),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "python": parent.platform.python_version(), "platform": parent.platform.platform(),
        "dependencies": sorted(f"{d.metadata['Name']}=={d.version}" for d in parent.importlib.metadata.distributions()),
        "environment": {k: parent.os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "PYTHONHASHSEED")},
        "replay_command": ".venv/bin/python " + SCRIPT + " --capture " + str(destination.relative_to(ROOT)),
        "replay_semantics": "Verify source_bindings at the commit retaining this run; use a fresh generated directory. A rerun never replaces the accepted original.",
        "claim_ceiling": "C_OS unavailable projection and synthetic numeric protocol controls, source propagation and actual API/notebook/HTTP-handler/browser-validator identity. No production detector, full browser campaign, complete-profile catalog or G2 claim.",
        "G2_accepted": False, "accepted_generic_runtime_support": [], "admitted_specialization_support_sets": [],
    }
    record.update(_p941_execute(ROOT, before, REQUIRED, suite, source_hashes,
        extra_modules=frozenset({"pygrc.models.grc_v4", "pygrc.models.grc_v4_lifecycle",
                                 "tests.models.test_grc_v4", "tests.models.test_grc_v4_lifecycle",
                                 "grcv4_explorer.abundance", "grcv4_explorer.receipt_parents"})))
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "run.json").write_text(json.dumps(record, indent=2).replace(str(ROOT) + "/", "") + "\n")
    print(json.dumps({k: record.get(k) for k in ("status", "results", "capture_error", "failure_output")}))
    return record["status"] == "passed"


def inspect():
    import phase9_implementation_policy as policy
    record = json.loads((ROOT / RUN).read_text())
    if (record["schema"] != "phase9_leaf_focused_run_v1" or record["iteration_id"] != "P9-4.9.1a"
        or record["base_commit"] != BASE or record["release_id"] != policy.current_abundance_release(ROOT)
        or record["status"] != "passed" or record["source_unchanged"] is not True
        or record["coverage"]["passed"] is not True or record["source_bindings"] != source_hashes()
        or record["required_ids"] != sorted(REQUIRED) or record["results"]["tests_run"] != len(REQUIRED)
        or any(record["results"][k] for k in ("failures", "errors", "skips"))
        or record["G2_accepted"] is not False or record["accepted_generic_runtime_support"] != []
        or record["admitted_specialization_support_sets"] != []
        or any(record["loaded_sources_after"].get(name) != row for name, row in record["loaded_sources_before"].items())):
        raise ValueError("abundance execution does not match current inputs or bounded roster")
    policy.parent_runtime_evidence(ROOT)
    historical = policy.facade_runtime_evidence(ROOT)
    ready, owners = policy.leaf_permissions(ROOT)
    if ("P9-4.9.1a" not in ready or "P9-4.9.3" in ready or "P9-4.8B" in ready
        or {p for p, leaves in owners.items() if "P9-4.9.1a" in leaves} != policy.ABUNDANCE_RUNTIME_PATHS):
        raise ValueError("abundance permission drift")
    return {"status": "passed", "tests": len(REQUIRED), "G2_accepted": False,
            "original_facade_subject": historical["subject_commit"]}


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
