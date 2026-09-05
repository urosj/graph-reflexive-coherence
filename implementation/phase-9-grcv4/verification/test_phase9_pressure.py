#!/usr/bin/env python3
"""P9-1.7 pressure matrix. All adversarial writes use a disposable local clone.

Runtime-positive cases are isolated synthetic approval fixtures, never an
installation of runtime authority in the active checkout.
"""

from contextlib import contextmanager
from copy import deepcopy
import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

import phase9_policy as p
import pressure_evidence as evidence


@contextmanager
def changed(root, name, content):
    path = root / name
    before = path.read_bytes() if path.exists() else None
    path.parent.mkdir(parents=True, exist_ok=True)
    if evidence.ACTIVE is not None:
        evidence.ACTIVE.mutation(name, before, content)
    if content is None:
        path.unlink()
    else:
        path.write_bytes(content)
    try:
        yield path
    finally:
        if before is None:
            path.unlink(missing_ok=True)
        else:
            if path.is_symlink():
                path.unlink()
            path.write_bytes(before)


def main():
    suite = evidence.ProbeSuite()
    rows, case = suite.rows, suite.case

    with tempfile.TemporaryDirectory(prefix="grcv4-p917-pressure-") as scratch:
        root = Path(scratch) / "repository"
        suite.root = root
        subprocess.run(
            [
                "git",
                "clone",
                "--shared",
                "--no-checkout",
                "--quiet",
                str(p.ROOT),
                str(root),
            ],
            check=True,
        )
        p.git(root, "checkout", "--quiet", p.prior.CHECKPOINT)
        snapshot = p.predecessor(p.ROOT)
        for row in snapshot["files"]:
            target = root / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(row["utf8"].encode())
        (root / ".venv").symlink_to(
            Path(sys.prefix).resolve(), target_is_directory=True
        )

        def replay_predecessor():
            result = suite.command(
                [sys.executable, str(root / p.HERE / "test_phase9_dispatch.py")],
                cwd=root,
            )
            p.require(
                result.returncode == 0
                and "Ran 13 tests" in result.stderr
                and "OK" in result.stderr,
                "unchanged P9-1.6 replay failed: " + result.stdout + result.stderr,
            )

        case(
            "unchanged_p916_dispatch_suite_replayed",
            2,
            replay_predecessor,
            scope="reconstructed_p916_snapshot_13_tests",
        )

        for name in p.PATHS:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((p.ROOT / name).read_bytes())
        policy = p.read(root / p.POLICY)
        case("legitimate_current_planning", 2, lambda: p.current_boundary(root))
        case("unchanged_p916_snapshot", 2, lambda: p.predecessor(root))

        spec = importlib.util.spec_from_file_location(
            "p917_dispatch_fixture", root / p.SCRIPTS / "active_phase.py"
        )
        dispatch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dispatch)

        def route():
            p.require(
                dispatch.verification_script(root)
                == root / p.HERE / "audit_phase9_successor.py",
                "normal route did not select the V2 successor",
            )

        case("legitimate_successor_dispatch", 2, route)

        def missing_marker_route():
            with changed(root, p.prior.OPENING, None):
                route()

        case("deleted_marker_cannot_downgrade_dispatch", 6, missing_marker_route)

        def flag_rejection():
            result = suite.command(
                [
                    sys.executable,
                    str(root / p.HERE / "audit_phase9_successor.py"),
                    "--runtime-authorized",
                ],
            )
            p.require(
                result.returncode == 2 and "unrecognized arguments" in result.stderr,
                "flag supplied authority",
            )

        case("CLI_has_no_authorizing_flag", 1, flag_rejection)

        def mutate(name, content, *, boundary=True):
            with changed(root, name, content):
                return (
                    p.current_boundary(root)
                    if boundary
                    else p.validate_tree(root, policy)
                )

        for key, value in [
            ("baseline_commit", "0" * 40),
            ("release_id", "stale"),
            ("accepted_generic_runtime_support", ["C_OS"]),
            ("P9_G1_accepted", True),
        ]:

            def stale_record(key=key, value=value):
                record = p.read(root / p.RECORD)
                record[key] = value
                mutate(p.RECORD, p.canonical(record))

            case("execution_record_" + key, 6, stale_record, reject=True)

        for name in [
            "src/pygrc/models/grc_v4.py",
            "tests/models/test_grc_v4.py",
            "pyproject.toml",
        ]:
            before = (root / name).read_bytes() if (root / name).exists() else b""
            case(
                "planning_rejects_" + name.replace("/", "_"),
                1,
                lambda name=name, before=before: mutate(
                    name, before + b"\n# unauthorized runtime work\n"
                ),
                reject=True,
            )
        frozen = "specs/grc-v4-spec.md"
        case(
            "changed_frozen_spec",
            6,
            lambda: mutate(frozen, (root / frozen).read_bytes() + b"\nforged\n"),
            reject=True,
        )
        case("deleted_frozen_spec", 6, lambda: mutate(frozen, None), reject=True)
        case(
            "permitted_path_wrong_content",
            6,
            lambda: mutate(p.SCRIPTS + "run.py", b"print('PASS')\n"),
            reject=True,
        )
        case("deleted_successor_record", 6, lambda: mutate(p.POLICY, None), reject=True)
        case(
            "deleted_phase_marker",
            6,
            lambda: mutate(p.prior.OPENING, None),
            reject=True,
        )
        case(
            "modified_prior_review",
            6,
            lambda: mutate(
                p.PHASE + "tranche-1/P9-1.4-SupportReview.md", b"accepted\n"
            ),
            reject=True,
        )

        def hidden_index():
            p.git(root, "update-index", "--assume-unchanged", frozen)
            try:
                return mutate(frozen, b"hidden by index metadata\n")
            finally:
                p.git(root, "update-index", "--no-assume-unchanged", frozen)

        case("assume_unchanged_cannot_hide_bytes", 6, hidden_index, reject=True)

        def staged_addition():
            name = "src/pygrc/models/grc_v4_rogue.py"
            with changed(root, name, b"# staged unauthorized addition\n"):
                p.git(root, "add", name)
                try:
                    p.validate_tree(root, policy)
                finally:
                    p.git(root, "update-index", "--force-remove", name)

        case("staged_runtime_addition_rejected", 1, staged_addition, reject=True)

        def ignored_addition():
            exclude = root / ".git/info/exclude"
            with changed(
                root,
                ".git/info/exclude",
                exclude.read_bytes() + b"\n/src/pygrc/models/grc_v4_hidden.py\n",
            ):
                mutate(
                    "src/pygrc/models/grc_v4_hidden.py",
                    b"# ignored is not authorized\n",
                )

        case("ignored_runtime_addition_rejected", 1, ignored_addition, reject=True)

        def symlink():
            with changed(root, frozen, None) as path:
                path.symlink_to(root / "specs/README.md")
                p.validate_tree(root, policy)

        case("protected_symlink_rejected", 6, symlink, reject=True)

        def mode_change():
            path = root / frozen
            old = path.stat().st_mode
            path.chmod(old ^ 0o100)
            try:
                p.validate_tree(root, policy)
            finally:
                path.chmod(old)

        case("protected_mode_rejected", 6, mode_change, reject=True)

        for key, value in [
            ("status", "accepted"),
            ("baseline_commit", "0" * 40),
            ("release_id", "stale"),
            ("trusted_runtime_approval", "0" * 64),
            ("accepted_generic_runtime_support", ["C_OS"]),
            ("active_phase", "runtime_implementation"),
        ]:

            def forged(key=key, value=value):
                altered = deepcopy(policy)
                altered[key] = value
                altered["record_digest"] = p.digest_record(altered)
                mutate(p.POLICY, p.canonical(altered))

            case(
                "rehashed_policy_" + key,
                1 if key == "active_phase" else 6,
                forged,
                reject=True,
            )
        altered = deepcopy(policy)
        altered["artifact_bindings"][0]["sha256"] = "0" * 64
        case(
            "stale_digest_rejected",
            6,
            lambda: mutate(p.POLICY, p.canonical(altered)),
            reject=True,
        )
        case(
            "green_marker_not_policy",
            6,
            lambda: mutate(p.POLICY, b'{"passed":true,"runtime_authorized":false}'),
            reject=True,
        )
        case(
            "duplicate_json_key",
            6,
            lambda: mutate(p.POLICY, b'{"status":"held","status":"passed"}'),
            reject=True,
        )
        case(
            "runtime_flag_not_authority",
            1,
            lambda: p.runtime_targets(
                None,
                None,
                release_id=p.prior.RELEASE_ID,
                predecessor_digest=policy["record_digest"],
            ),
            reject=True,
        )

        # Synthetic future approval is separately pinned by the test harness.
        # It is intentionally NOT written to the active policy or source tree.
        pairs = [
            ("src/pygrc/models/grc_v4.py", None, b"# V4-only fixture\n", "add"),
            ("tests/models/test_grc_9_v4.py", None, b"# V4-only test fixture\n", "add"),
            (
                "src/pygrc/models/__init__.py",
                b"from .grc_9_v3 import GRC9V3\n",
                b"from .grc_9_v3 import GRC9V3\nfrom .grc_v4 import GRCV4\n",
                "additive_integration",
            ),
            (
                "pyproject.toml",
                b'[project]\nname="fixture"\ndependencies=["numpy"]\n[project.optional-dependencies]\ndev=[]\n',
                b'[project]\nname="fixture"\ndependencies=["numpy"]\n[project.optional-dependencies]\ndev=[]\nv4=["scipy"]\n',
                "additive_integration",
            ),
        ]
        authority = {
            "schema": "phase9_runtime_mutation_authority_v1",
            "status": "accepted_by_user",
            "P9_G1_accepted": True,
            "runtime_authorized": True,
            "release_id": p.prior.RELEASE_ID,
            "predecessor_policy_digest": policy["record_digest"],
            "targets": [
                {
                    "path": name,
                    "operation": op,
                    "before_sha256": p.sha(before) if before else None,
                    "after_sha256": p.sha(after),
                }
                for name, before, after, op in pairs
            ],
        }
        authority["record_digest"] = p.digest_record(authority)
        trusted = authority["record_digest"]

        def admit_runtime(value=authority, anchor=trusted):
            return p.runtime_targets(
                value,
                anchor,
                release_id=p.prior.RELEASE_ID,
                predecessor_digest=policy["record_digest"],
            )

        case(
            "future_explicit_approval_exact_targets",
            2,
            admit_runtime,
            scope="synthetic_future_approval_not_live_authority",
        )
        for row, (_, before, after, _) in zip(authority["targets"], pairs):
            case(
                "future_content_" + row["path"].replace("/", "_"),
                2,
                lambda row=row, before=before, after=after: p.validate_runtime_change(
                    row, before, after
                ),
                scope="synthetic_future_approval_not_live_authority",
            )
        case(
            "self_declared_runtime_no_external_anchor",
            1,
            lambda: admit_runtime(anchor=None),
            reject=True,
        )
        forged = deepcopy(authority)
        forged["targets"][0]["after_sha256"] = "1" * 64
        forged["record_digest"] = p.digest_record(forged)
        case(
            "self_rehashed_runtime_approval",
            6,
            lambda: admit_runtime(forged),
            reject=True,
        )
        for target in [
            "src/pygrc/models/grc_9_v3.py",
            "src/pygrc/models/grc_v40.py",
            "tests/core/test_unknown.py",
            "../src/pygrc/models/grc_v4.py",
        ]:

            def bad_target(target=target):
                value = deepcopy(authority)
                value["targets"][0]["path"] = target
                value["record_digest"] = p.digest_record(value)
                admit_runtime(value, value["record_digest"])

            case(
                "runtime_wrong_target_" + target.replace("/", "_"),
                6,
                bad_target,
                reject=True,
            )
        case(
            "approved_path_changed_runtime_bytes",
            6,
            lambda: p.validate_runtime_change(
                authority["targets"][0], None, b"wrong\n"
            ),
            reject=True,
        )

        def legacy_integration(index, after):
            row = deepcopy(authority["targets"][index])
            row["after_sha256"] = p.sha(after)
            p.validate_runtime_change(row, pairs[index][1], after)

        case(
            "legacy_dependency_not_additive",
            6,
            lambda: legacy_integration(3, pairs[3][2].replace(b"numpy", b"changed")),
            reject=True,
        )
        case(
            "legacy_export_rebound",
            6,
            lambda: legacy_integration(
                2, pairs[2][1] + b"from .grc_v4 import GRCV4 as GRC9V3\n"
            ),
            reject=True,
        )

        expected = p.read(
            root / p.PHASE / "tranche-1/P9-1.4-SupportAndDependencies.json"
        )
        edges = p.validate_composition(expected, expected)

        def composition(edit):
            value = deepcopy(expected)
            edit(value)
            suite.mutation("projection:support_dependencies", expected, value)
            p.validate_composition(value, expected)

        case(
            "legitimate_exact_children_and_c_os_path",
            4,
            lambda: p.validate_composition(expected, expected),
            scope="planning_dependency_graph",
        )
        case(
            "required_child_deleted",
            3,
            lambda: composition(lambda x: x["child_iterations"].pop()),
            reject=True,
        )
        case(
            "matching_count_child_substitution",
            3,
            lambda: composition(
                lambda x: x["child_iterations"][-1].update(iteration_id="P9-FAKE")
            ),
            reject=True,
        )
        case(
            "forged_evidence_alias",
            3,
            lambda: composition(
                lambda x: x["child_iterations"][0].update(evidence_alias_of="P9-5.4")
            ),
            reject=True,
        )
        case(
            "unresolved_dependency",
            3,
            lambda: composition(
                lambda x: x["dependency_edges"][0]["requires"].append("P9-NOT-A-NODE")
            ),
            reject=True,
        )
        case(
            "dependency_cycle",
            3,
            lambda: composition(
                lambda x: x["dependency_edges"][0]["requires"].append(
                    x["dependency_edges"][0]["iteration_id"]
                )
            ),
            reject=True,
        )
        for barrier in ["P9-G2[A_OS]", "P9-G2[C_PC]", "P9-G2[C_RG2b]"]:

            def barrier_edit(value, barrier=barrier):
                # Independent synthetic provider: do not let a pre-existing A
                # cycle or a missing RG2b gate reject before the scope check.
                provider = "P9-PROBE-UNRELATED-" + barrier
                value["dependency_edges"].append(
                    {"iteration_id": provider, "requires": []}
                )
                next(
                    r
                    for r in value["dependency_edges"]
                    if r["iteration_id"] == "P9-G2[C_OS]"
                )["requires"].append(provider)

            case(
                "unrelated_c_os_barrier_" + barrier,
                4,
                lambda edit=barrier_edit: composition(edit),
                reject=True,
            )
        case(
            "unexecuted_exact_profile",
            4,
            lambda: composition(
                lambda x: x["profiles"][0]["exact_accepted_profile_ids"].append(
                    "fixture-not-executed"
                )
            ),
            reject=True,
        )
        case(
            "unexecuted_support_set",
            4,
            lambda: composition(
                lambda x: x["accepted_generic_runtime_support"].append("C_OS")
            ),
            reject=True,
        )
        case(
            "universal_optional_completion",
            5,
            lambda: composition(
                lambda x: next(
                    r for r in x["dependency_edges"] if r["iteration_id"] == "P9-9.6"
                )["requires"].append("P9-9.1a")
            ),
            reject=True,
        )
        mandatory = p.dependency_closure(edges, "P9-9.6") - {"P9-9.6", "P9-G1"}

        def completion(evidence=mandatory, held=False, **kwargs):
            result = p.completion_gate(
                edges,
                evidence,
                evidence_scope="synthetic_exact_C_OS",
                required_scope="synthetic_exact_C_OS",
                **kwargs,
            )
            p.require(result["held"] is held, "wrong conditional evidence disposition")

        case(
            "completion_off_all_mandatory_present",
            5,
            completion,
            scope="synthetic_scoped_evidence",
        )
        for capability in sorted(p.OPTIONAL):
            for surface in ["advertised", "handoff"]:
                case(
                    f"{surface}_{capability}_without_own_evidence_held",
                    5,
                    lambda capability=capability, surface=surface: completion(
                        held=True, **{surface: [capability]}
                    ),
                    scope="synthetic_scoped_evidence",
                )
                case(
                    f"{surface}_{capability}_with_own_evidence",
                    5,
                    lambda capability=capability, surface=surface: completion(
                        mandatory | {"P9-9.1a"}, **{surface: [capability]}
                    ),
                    scope="synthetic_scoped_evidence",
                )
        for required in [
            "P9-8.1c",
            "P9-8.1d",
            "P9-8.3C-OS",
            "P9-8.4",
            "P9-9.1b",
            "P9-9.2-C_OS-state",
            "P9-9.2-C_OS-observable",
            "P9-9.2-C_OS-lifecycle",
        ]:
            case(
                "completion_off_missing_" + required,
                5,
                lambda required=required: completion(mandatory - {required}, held=True),
                scope="synthetic_scoped_evidence",
            )
        case(
            "completion_cannot_borrow_other_profile_evidence",
            5,
            lambda: p.completion_gate(
                edges,
                mandatory | {"P9-9.1a"},
                evidence_scope="synthetic_exact_C_PC",
                required_scope="synthetic_exact_C_OS",
                advertised=["completed_spark"],
            ),
            reject=True,
        )
        from test_phase9_gap_pressure import extend

        extend(suite, root, policy, changed)

        case(
            "original_checkout_still_planning",
            1,
            lambda: p.current_boundary(p.ROOT),
            scope="live_read_only",
        )

    report = suite.finish()
    destination = (
        p.ROOT / p.SIDE / "tool/generated/phase9-verification/pressure-results.json"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(p.canonical(report) + b"\n")
    retained = destination.parent / "runs" / report["run_id"]
    retained.mkdir(parents=True, exist_ok=True)
    (retained / "pressure-results.json").write_bytes(p.canonical(report) + b"\n")
    destination.with_name("pressure-summary.json").write_bytes(
        p.canonical(evidence.summary(report)) + b"\n"
    )
    for batch in report["batches"]:
        destination.with_name("batch-" + batch["batch_id"] + ".json").write_bytes(
            p.canonical(
                {
                    "run_id": report["run_id"],
                    "report_digest": report["report_digest"],
                    **batch,
                }
            )
            + b"\n"
        )
    for row in rows:
        if not row["passed"]:
            print(
                json.dumps(
                    {
                        k: row[k]
                        for k in [
                            "case_id",
                            "expected_decision",
                            "candidate_decision",
                            "actual_reason",
                            "intended_check_reached",
                        ]
                    }
                )
            )
    p.require(
        report["status"] == "passed",
        "P9-1.7 pressure failures; inspect generated report",
    )
    print(
        f"PHASE9_PRESSURE_PASS cases={len(rows)} review_pressures=6 runtime_authorized=false synthetic_runtime_approval_only=true"
    )


if __name__ == "__main__":
    main()
