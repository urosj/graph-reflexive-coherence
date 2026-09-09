"""Bounded parent-rule execution using the existing exact-source test capture.

--capture creates a NEW generated run; --check inspects retained evidence
without rerunning or substituting it. Neither grants G2 acceptance.
"""

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
BASE = "280f46cec28b06ffd65b6ee04ba8caadc3d8d069"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/"
RUN = "implementation/phase-9-grcv4/evidence/P9-4.9.2/parent-rule/run.json"
SCOPES = ["src", "tests", "specs", "pyproject.toml", "uv.lock"]
MODULE = "tests.models.test_grc_v4_lifecycle"
CLASSES = {
    "CandidateCOSOperationTests",
    "CandidateCOSLifecycleTests",
    "CandidateCOSReplayTests",
    "CandidateCOSAuditCorrectionTests",
    "CandidateCOSCrossingTests",
}
NEW_METHODS = (
    "test_every_primary_kind_can_root_and_step_after_crossings_uses_latest_primary",
    "test_nonwriting_operations_and_failures_do_not_advance_parent_head",
    "test_snapshot_declares_policy_release_and_rejects_legacy_or_guessed_admission",
    "test_auxiliary_and_partition_mutations_reject_without_observable_restore",
    "test_hash_coherent_wrong_parents_fail_before_atomic_publication",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_hashes():
    names = subprocess.check_output(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            *SCOPES,
        ],
        cwd=ROOT,
        text=True,
    ).splitlines()
    names += [str(Path(__file__).relative_to(ROOT))]
    return {name: sha((ROOT / name).read_bytes()) for name in sorted(set(names))}


def required_ids():
    old = ast.parse(
        subprocess.check_output(
            ["git", "show", BASE + ":tests/models/test_grc_v4_lifecycle.py"], cwd=ROOT
        )
    )
    old_classes = {c.name: c for c in old.body if isinstance(c, ast.ClassDef)}
    if not CLASSES <= old_classes.keys():
        raise ValueError("historical lifecycle test class missing")
    ids = {
        MODULE + "." + name + "." + f.name
        for name in CLASSES
        for f in old_classes[name].body
        if isinstance(f, ast.FunctionDef) and f.name.startswith("test_")
    }
    ids |= {MODULE + ".CandidateCOSParentPolicyTests." + name for name in NEW_METHODS}
    for module, classes in {
        "test_grc_v4": {"FoundationIntegrationTests", "RequestTests"},
        "test_grc_v4_codec": {"CodecTests"},
        "test_grc_v4_state": {"FrozenJSONTests", "LifecycleOwnershipTests"},
    }.items():
        old = ast.parse(
            subprocess.check_output(
                ["git", "show", BASE + ":tests/models/" + module + ".py"], cwd=ROOT
            )
        )
        ids |= {
            "tests.models." + module + "." + c.name + "." + f.name
            for c in old.body
            if isinstance(c, ast.ClassDef) and c.name in classes
            for f in c.body
            if isinstance(f, ast.FunctionDef) and f.name.startswith("test_")
        }
    return ids


def capture(destination):
    from tests.models.test_grc_v4_candidate_c import _p941_execute
    from pygrc.models.grc_v4_codec import RELEASE_ID
    import importlib

    importlib.import_module("tests.models.test_grc_v4_transport")

    destination = (ROOT / destination).resolve()
    if (
        not destination.is_relative_to(ROOT / SIDE / "tool/generated")
        or destination.exists()
    ):
        raise ValueError(
            "capture needs a fresh repository-relative generated destination"
        )
    before = source_hashes()
    required = required_ids()
    suite = unittest.defaultTestLoader.loadTestsFromNames(sorted(required))
    record = {
        "schema": "phase9_leaf_focused_run_v1",
        "iteration_id": "P9-4.9.2",
        "release_id": RELEASE_ID,
        "base_commit": BASE,
        "source_bindings": before,
        "required_ids": sorted(required),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "environment": {
            k: os.environ.get(k)
            for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "PYTHONHASHSEED")
        },
        "replay_command": ".venv/bin/python implementation/phase-9-grcv4/verification/verify_p9492_parents.py --capture "
        + str(destination.relative_to(ROOT)),
        "replay_semantics": "Use a fresh generated directory for reruns. Check out the commit retaining this run and verify all source_bindings first. Original evidence is never replaced by a rerun.",
        "claim_ceiling": "Bounded C_OS parent semantics, lifecycle regression and atomic rejection; not public facade, complete-profile/G2 conformance or authenticated uninterrupted history.",
        "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
        "G2_accepted": False,
    }
    record.update(
        _p941_execute(
            ROOT,
            before,
            required,
            suite,
            source_hashes,
            extra_modules=frozenset(
                {
                    MODULE,
                    "pygrc.models.grc_v4_lifecycle",
                    "pygrc.models.grc_v4_codec",
                    "pygrc.models.grc_v4_state",
                    "pygrc.models.grc_v4_step",
                    "pygrc.models.grc_v4_realizations",
                    "pygrc.models.grc_v4_geometry",
                    "pygrc.models.grc_v4_transport",
                    "tests.models.test_grc_v4_realizations",
                }
            ),
        )
    )
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    # Normalize diagnostic presentation only; all retained input hashes remain
    # hashes of repository bytes, not machine-local paths.
    encoded = json.dumps(record, indent=2).replace(str(ROOT) + "/", "") + "\n"
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "run.json").write_text(encoded)
    print(
        json.dumps(
            {
                "status": record["status"],
                "results": record.get("results"),
                "capture_error": record.get("capture_error"),
            }
        )
    )
    if record["status"] != "passed":
        print(record.get("failure_output", ""))
    return record["status"] == "passed"


def inspect(root=ROOT):
    from build_receipt_parent_release import verify

    record = json.loads((root / RUN).read_text())
    if (
        record["status"] != "passed"
        or record["iteration_id"] != "P9-4.9.2"
        or record["release_id"] != verify(root)
        or record["G2_accepted"] is not False
        or record["results"]["tests_run"] != len(required_ids())
        or any(record["results"][k] for k in ("failures", "errors", "skips"))
        or record["required_ids"] != sorted(required_ids())
        or record["source_bindings"] != source_hashes()
    ):
        raise ValueError(
            "retained parent evidence does not match current inputs/roster"
        )
    return {
        "status": "passed",
        "tests": record["results"]["tests_run"],
        "G2_accepted": False,
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
