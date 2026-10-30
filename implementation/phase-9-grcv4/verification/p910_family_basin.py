"""Per-family 10.1a-c -> 10.2; capture required boundaries once, reuse for verification.

--run executes two independent native jobs in parallel. Successful parts are
immutable and resumable. --check reads retained evidence and performs no native
trajectory, replay or constitutive solve.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import json
import lzma
from pathlib import Path
import platform
import subprocess
import time
import unittest

import p9102_verification as v
import p9101c_target_basin as direct

ROOT = v.ROOT
BASE = v.BASE + "tranche-10/"
VERIFY = v.BASE + "verification/"
SELF = VERIFY + "p910_family_basin.py"
TEST = VERIFY + "test_p910_aos_basin.py"
FAMILIES = ("A_OS",)
PARTS = ("Native", "Target")
BASELINE = "f2333b32"
PRIOR = v.BASE + "tranche-9/P9-AOS-Acceptance.json"
TARGET = v.BASE + "tranche-9/P9-9.1b-AOS.json.xz"
AUTHORITY = "implementation/investigations/grc9v4-constitutive-design/decisions/p9-basin-interface/Authority.json"
require, seal = v.require, v.seal


def references(root=ROOT):
    names = {SELF, TEST, PRIOR, TARGET, AUTHORITY,
             BASE + "P9-10-AOS-SourceEpochs.json", VERIFY + "p910_basin_source_epoch.py",
             "specs/grc-9-v4-basin-interface.md", "specs/grc-9-v4-spec.md",
             VERIFY + "p9101a_basin_oracle.py", VERIFY + "p9101c_target_basin.py",
             VERIFY + "test_p9101a_basin_pressure.py", VERIFY + "test_p9101b_target_compatibility.py",
             VERIFY + "p9102_verification.py", VERIFY + "p9101b_target_compatibility.py"}
    for pattern in ("src/pygrc/**/*.py", "src/pygrc/**/*.json", "tests/models/test_grc*.py"):
        names.update(p.relative_to(root).as_posix() for p in root.glob(pattern))
    for pattern in ("test_p980*.py", "verify_p983a_aos_oracle.py"):
        names.update(p.relative_to(root).as_posix() for p in (root / VERIFY).glob(pattern))
    return [v.reference(root, n) for n in sorted(names)]


def prerequisites(root=ROOT):
    from p9102_acceptance import PATH as accepted
    refs = []
    for name in (PRIOR, TARGET, AUTHORITY, accepted, v.PATH):
        raw = (root / name).read_bytes()
        require(raw == subprocess.check_output(["git", "show", BASELINE + ":" + name], cwd=root),
                "changed accepted predecessor: " + name)
        refs.append(v.reference(root, name))
    decision = json.loads((root / PRIOR).read_bytes())
    require(decision["family"] == "A_OS" and decision["user_accepted"] is True
            and decision["bounded_scope_closed"] is True, "missing A_OS Tranches 8-9 acceptance")
    return refs


def stem(family, part=None):
    require(family in FAMILIES and (part is None or part in PARTS), "unselected basin work")
    return BASE + "P9-10-" + family.replace("_", "") + ("-" + part if part else "-Verification") + ".json"


def load(family, part=None, root=ROOT):
    paths = [root / stem(family, part), root / (stem(family, part) + ".xz")]
    paths = [p for p in paths if p.exists()]
    require(len(paths) == 1, "one unambiguous family record required")
    p = paths[0]; raw = p.read_bytes()
    value = json.loads(lzma.decompress(raw) if p.suffix == ".xz" else raw)
    require(value == seal(value), "family record digest")
    return value, dict(**v.reference(root, p.relative_to(root).as_posix()), record_digest=value["record_digest"])


def write(value, family, part=None, root=ROOT):
    path = root / stem(family, part)
    require(not path.exists() and not path.with_suffix(".json.xz").exists(), "refuse to overwrite family evidence")
    raw = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()
    if len(raw) > 1_000_000:
        path = path.with_suffix(".json.xz"); raw = lzma.compress(raw, preset=6)
    with path.open("xb") as stream:
        stream.write(raw)
    return path


def run_part(family, part):
    import flint
    import test_p910_aos_basin as tests
    from pygrc.models.grc_v4_exact import ExactBackend, exact_backend

    prerequisites()
    paths = (ROOT / stem(family, part), ROOT / (stem(family, part) + ".xz"))
    if any(p.exists() for p in paths):
        value, _ = load(family, part)
        require(value["source_refs"] == references(), "completed part source drift")
        return part
    before = references()
    tests.EVIDENCE.clear(); tests.native.EVIDENCE.clear(); tests.targets.EVIDENCE.clear()
    cls = tests.AOSNativeBasin if part == "Native" else tests.AOSTargetCompatibility
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
    roster = [t.id() for t in suite]
    start = time.monotonic()
    with exact_backend(ExactBackend.FLINT):
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    require(result.wasSuccessful() and not result.skipped and result.testsRun == (5 if part == "Native" else 3),
            "native family checks failed; no success record written")
    require(before == references(), "execution sources changed during run")
    evidence = dict(native=deepcopy(tests.native.EVIDENCE), **deepcopy(tests.EVIDENCE)) if part == "Native" else dict(
        target_compatibility=deepcopy(tests.targets.EVIDENCE), **deepcopy(tests.EVIDENCE))
    value = seal(dict(schema="p910-family-basin-native-part-v1", family=family, part=part,
        status="passed_bounded_native_execution", tests=roster, tests_run=result.testsRun,
        source_refs=before, evidence=json.loads(json.dumps(evidence, allow_nan=False)),
        environment=dict(python=platform.python_version(), python_flint=flint.__version__,
                         exact_backend="flint", numerical_policy="legacy_exact_v1"),
        elapsed_seconds=round(time.monotonic()-start, 3), user_accepted=False,
        full_GRC9V4_conformance=False, G4_accepted=False, new_support=[]))
    write(value, family, part)
    return part


def exact_target(part):
    data = part["evidence"]
    old = data["target_compatibility"]["v2"]
    return direct.predecessor.seal(dict(schema="p9101c-exact-target-basin-v1", family=part["family"],
        status="passed_bounded_exact_target_check", subject=old["subject"],
        observations=data["exact_target"]["observations"], native_boundaries=2,
        native_role_captures=4, native_expansion_events=0, new_enabled_steps=0,
        disabled_steps=2, exact_backend="flint", numerical_policy="legacy_exact_v1",
        user_accepted=False, exact_root_signs_claimed=False, new_support=[]))


def verification_checks(target_part):
    from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
    data = target_part["evidence"]["target_compatibility"]
    checks = dict(ledgers={name: v.ledger_check(data[name]["final_checkpoint"]["owner"],
                                              data[name]["enabled_continuation"])
                           for name in ("v1", "v2")}, charges=[])
    for case in target_part["evidence"]["exact_target"]["observations"]:
        state = direct.restore_state(case["saved_native_state"], target_part["family"])
        with exact_backend(ExactBackend.FLINT):
            for role in ("current", "reset"):
                charge = v.charge_check(getattr(state.inputs, role).C, state.inputs.Q_target,
                                        state.inputs.geometry.reference.profile)
                require(charge["admitted"], "saved admitted charge rejected")
                checks["charges"].append(dict(boundary=case["label"], role=role, **charge))
    checks.update(native_steps_added_by_10_2=0, native_replays_added_by_10_2=0,
                  shared_charge_controls=v.reference(ROOT, v.PATH),
                  replay_basis="executed_in_this_family_10_1a_b_not_inferred_from_first_group")
    return checks


def consolidate(family):
    native, nr = load(family, "Native")
    target, tr = load(family, "Target")
    value = seal(dict(schema="p910-family-basin-verification-v1", family=family,
        status="passed_bounded_pending_acceptance", user_accepted=False,
        P9_10_1_closed=False, P9_10_2_closed=False, full_GRC9V4_conformance=False,
        G4_accepted=False, new_support=[], remaining_families=["C_PC", "C_CI_PC", "A_CI_PC", "C_RG2b", "A_RG2b"],
        prerequisites=prerequisites(), parts=[nr, tr], source_refs=references(),
        native_tests=native["tests_run"]+target["tests_run"],
        target_compatibility=target["evidence"]["target_compatibility"],
        direct_target=exact_target(target), verification=verification_checks(target),
        historical_evidence_relabelled=False,
        next_work="Bounded A_OS P9-10.1a-c and P9-10.2 review; then C_PC in the agreed six-family order."))
    validate(value)
    # The final view references the native parts; the repeated target payload is
    # removed from disk and reconstructed exactly by check() using its bound part.
    on_disk = dict(value)
    for key in ("target_compatibility", "direct_target"):
        del on_disk[key]
    on_disk["reconstruction"] = dict(schema="p910-family-basin-parts-v1", target_part=tr,
                                     reconstructed_record_digest=value["record_digest"])
    on_disk = seal(on_disk)
    write(on_disk, family)
    return value


def validate(value, *, equations=False, sources=True):
    require(value == seal(value) and value["schema"] == "p910-family-basin-verification-v1"
            and value["family"] in FAMILIES and value["status"] == "passed_bounded_pending_acceptance"
            and all(value[k] is False for k in ("user_accepted", "P9_10_1_closed", "P9_10_2_closed",
                                               "full_GRC9V4_conformance", "G4_accepted"))
            and value["new_support"] == [] and value["native_tests"] == 8,
            "family verification scope or identity")
    if sources:
        require(value["source_refs"] == references() and value["prerequisites"] == prerequisites(),
                "family source or prerequisite drift")
    native, nr = load(value["family"], "Native")
    target, tr = load(value["family"], "Target")
    require(value["parts"] == [nr, tr], "native execution part drift")
    require(native["source_refs"] == target["source_refs"] == value["source_refs"], "part source mismatch")
    n = native["evidence"]["native"]
    require(n["lifecycle"]["exact_replay"] and n["lifecycle"]["state_only"]
            and n["pressure"]["complete_publication_rollback"]
            and native["evidence"]["scientific"]["history_discrimination"], "missing native conformance")
    require(value["target_compatibility"] == target["evidence"]["target_compatibility"], "target execution substitution")
    for version in ("v1", "v2"):
        old = value["target_compatibility"][version]
        require(old["disabled_replay"] and old["enabled_replay"] and old["full_parent_DAG"]
                and old["surfaces"] == dict.fromkeys(("transition", "state", "observable", "lifecycle"), "passed"),
                "target compatibility incomplete")
    old = value["target_compatibility"]["v2"]
    with v.no_native_runs():
        direct.validate(value["direct_target"], old, equations=equations)
        require(value["verification"] == verification_checks(target), "retained verification drift")
    return value


def check(family="A_OS", *, equations=False):
    value, _ = load(family)
    require(value["reconstruction"]["schema"] == "p910-family-basin-parts-v1", "reconstruction schema")
    target, tr = load(family, "Target")
    require(value["reconstruction"]["target_part"] == tr, "reconstruction part substitution")
    expected = value.pop("reconstruction")["reconstructed_record_digest"]
    value.update(target_compatibility=target["evidence"]["target_compatibility"],
                 direct_target=exact_target(target))
    value = seal(value)
    require(value["record_digest"] == expected, "lossless part reconstruction")
    return validate(value, equations=equations)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--family", choices=FAMILIES, default="A_OS")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true"); mode.add_argument("--check", action="store_true")
    p.add_argument("--equations", action="store_true")
    args = p.parse_args()
    if args.run:
        with ProcessPoolExecutor(max_workers=2) as pool:
            list(pool.map(run_part, [args.family]*2, PARTS))
        value = consolidate(args.family)
    else:
        value = check(args.family, equations=args.equations)
    print(json.dumps(dict(family=value["family"], status=value["status"], record_digest=value["record_digest"],
                          native_tests=value["native_tests"], new_10_2_native_steps=0)))
