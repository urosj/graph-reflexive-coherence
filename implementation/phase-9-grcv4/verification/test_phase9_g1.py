#!/usr/bin/env python3
"""Bounded P9-G1 pressure on disposable checkouts, never on live runtime paths."""

from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

import phase9_implementation_policy as p
from pressure_evidence import protected_manifest


@contextmanager
def changed(path, content):
    before = path.read_bytes() if path.exists() else None
    mode = path.stat().st_mode if before is not None else None
    path.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        path.unlink()
    else:
        path.write_bytes(content)
    try:
        yield
    finally:
        if path.is_symlink() or (before is None and path.exists()):
            path.unlink()
        if before is not None:
            path.write_bytes(before)
            path.chmod(mode)


def main():
    boundary, tree = p.current_boundary(p.ROOT)
    original = protected_manifest(p.ROOT)
    run_id = "p9-g1-" + uuid.uuid4().hex
    cases = []
    with tempfile.TemporaryDirectory(prefix="grcv4-p919-pressure-") as scratch:
        root = Path(scratch) / "repository"
        subprocess.run(
            [
                "git",
                "clone",
                "--shared",
                "--quiet",
                "--no-checkout",
                str(p.ROOT),
                str(root),
            ],
            check=True,
        )
        fixture_revision = p.accepted_integration(p.ROOT)["baseline_commit"]
        subprocess.run(
            ["git", "checkout", "--quiet", "--detach", fixture_revision],
            cwd=root, check=True,
        )
        (root / ".venv").symlink_to(
            Path(sys.prefix).resolve(), target_is_directory=True
        )
        with (root / ".git/info/exclude").open("a") as f:
            f.write("\n/.venv\n")
        current_work_paths = set(p.work_entries(p.ROOT, p.acceptance(p.ROOT)))
        for name in p.PATHS | current_work_paths:
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p.ROOT / name, root / name)
        pristine = protected_manifest(root)
        mutations, traces = [], []

        @contextmanager
        def mutate(name, content):
            path = root / name
            mutations.append(
                {
                    "path": name,
                    "before_hex": path.read_bytes().hex() if path.exists() else None,
                    "after_hex": content.hex() if content is not None else None,
                }
            )
            with changed(path, content):
                yield

        def inspect():
            before = p.sha(p.canonical(protected_manifest(root)))
            try:
                return p.current_boundary(root)
            finally:
                after = p.sha(p.canonical(protected_manifest(root)))
                traces.append(
                    {
                        "check": "phase9_implementation_policy.current_boundary",
                        "before_digest": before,
                        "after_digest": after,
                        "read_only": before == after,
                    }
                )
                p.require(before == after, "checker modified candidate")

        def case(
            name,
            function,
            expected=None,
            *,
            scope="disposable_P9_G1_candidate_not_live_runtime",
        ):
            mutations.clear()
            traces.clear()
            error = None
            try:
                function()
            except (ValueError, KeyError, OSError) as failure:
                error = str(failure)
            passed = (
                (error is None)
                if expected is None
                else (error is not None and expected in error)
            )
            restored = protected_manifest(root) == pristine
            passed = passed and restored
            cases.append(
                {
                    "case_id": name,
                    "scope": scope,
                    "evidence_kind": "actual_checker_and_mutation",
                    "candidate_decision": "rejected" if error else "admitted",
                    "assertion_result": "passed" if passed else "failed",
                    "actual_reason": error or "exact accepted scope admitted",
                    "expected_reason": expected,
                    "intended_check_reached": passed,
                    "project_effect": {
                        "runtime_authorized": False,
                        "P9_G1_accepted": False,
                        "scientific_promotion": False,
                    },
                    "authority": {
                        "approval_digest": p.APPROVAL_DIGEST,
                        "scope": "existing_user_approval_not_created_by_probe",
                    },
                    "base_fixture_identity": {
                        "baseline_commit": p.BASELINE,
                        "fixture_revision": fixture_revision,
                        "policy_digest": boundary["record_digest"],
                        "tree": tree,
                    },
                    "protected_pre_post": {
                        "before_digest": p.sha(p.canonical(pristine)),
                        "after_digest": p.sha(p.canonical(protected_manifest(root))),
                        "restored": restored,
                    },
                    "mutations": deepcopy(mutations),
                    "trace": deepcopy(traces),
                }
            )

        def edit(name, content):
            with mutate(name, content):
                inspect()

        def manifest_edit(transform):
            value = p.read(root / p.WORK)
            transform(value)
            value["record_digest"] = p.digest_record(value)
            return mutate(p.WORK, p.canonical(value) + b"\n")

        def bind_entry(value, name, content, leaf="P9-2.1"):
            # Runtime may already exist; pressure must reach the intended
            # mutation check, not fail early on a duplicate manifest row.
            value["entries"] = [r for r in value["entries"] if r["path"] != name]
            value["entries"].append(
                {"path": name, "sha256": p.sha(content), "iteration_id": leaf}
            )

        def registered(name, content, *, extra=None, leaf="P9-2.1"):
            with mutate(name, content):

                def bind(value):
                    bind_entry(value, name, content, leaf)

                with manifest_edit(bind):
                    if extra:
                        extra()
                    else:
                        inspect()

        case("accepted_G1_current_tree", inspect)
        p.require(
            p.HANDOFF_PATHS.isdisjoint(p.PATHS), "archive still gates implementation"
        )
        case(
            "corrupt_handoff_does_not_revoke_implementation_permission",
            lambda: edit(p.HERE + "handoff/P9-G1-outputs.zip", b"corrupt archive"),
        )
        case(
            "missing_handoff_does_not_revoke_implementation_permission",
            inspect,
        )
        for filename, case_id in [
            (
                "P9-1.4-SupportAndDependencies.json",
                "portable_paths_cannot_change_dependencies",
            ),
            (
                "P9-1.5-OwnershipAndLegacyBaseline.json",
                "portable_paths_cannot_change_ownership",
            ),
        ]:

            def change_reviewed_content(filename=filename):
                name = p.PHASE + "tranche-1/" + filename
                value = p.read(root / name)
                if "dependency_edges" in value:
                    value["dependency_edges"][0]["requires"].append("invented_gate")
                else:
                    value["modules"][0]["path"] = "src/pygrc/models/grc_9_v3.py"
                edit(name, p.canonical(value))

            case(
                case_id,
                change_reviewed_content,
                "portability amendment changed reviewed content",
            )

        def changed_opening():
            value = p.read(root / p.prior.OPENING)
            value["planning_review"]["scientific_authority_added"] = True
            edit(p.prior.OPENING, p.canonical(value))

        case(
            "portable_opening_cannot_change_authority",
            changed_opening,
            "path normalization changed historical meaning",
        )

        def changed_snapshot():
            value = p.read(root / p.planning.SNAPSHOT)
            value["files"][0]["utf8"] += "\nScientific meaning changed\n"
            edit(p.planning.SNAPSHOT, p.canonical(value))

        case(
            "portable_snapshot_cannot_change_content",
            changed_snapshot,
            "path normalization changed historical meaning",
        )
        topology = p.INV + "scripts/audit_grc9v4_d10_claim_topology.py"
        case(
            "portable_checker_cannot_disable_claim_checks",
            lambda: edit(
                topology,
                (root / topology).read_bytes().replace(b"bool(condition)", b"True"),
            ),
            "path normalization changed historical meaning",
        )
        case(
            "portable_review_input_must_match_original_hash",
            lambda: edit(p.REVIEW_INPUT, b"different review"),
            "planning review input bytes changed",
        )
        source = "src/pygrc/models/grc_v4_state.py"
        content = b'"""Isolated authority fixture; not a runtime implementation."""\n'
        case("accepted_G1_exact_targets", lambda: registered(source, content))
        case(
            "accepted_G1_test_target",
            lambda: registered("tests/models/test_grc_v4_state.py", content),
        )
        def unregistered_path():
            with manifest_edit(lambda v: v.update(
                entries=[r for r in v["entries"] if r["path"] != source]
            )):
                edit(source, content)

        case(
            "published_permitted_path_cannot_drop_registration",
            unregistered_path,
            "published runtime/evidence deletion or rename forbidden",
        )
        case(
            "missing_acceptance",
            lambda: edit(p.APPROVAL, None),
            "P9-1.9-G1Acceptance.json",
        )

        def forged_approval():
            value = p.read(root / p.APPROVAL)
            value["runtime_targets"].append({"path": "src/pygrc/models/grc_9_v3.py"})
            value["record_digest"] = p.digest_record(value)
            edit(p.APPROVAL, p.canonical(value))

        case(
            "rehashed_expanded_acceptance",
            forged_approval,
            "untrusted P9-G1 acceptance",
        )
        for field, value in [
            ("accepted_generic_runtime_support", ["C_OS"]),
            ("admitted_specialization_support_sets", [["C_OS"]]),
            ("approval_digest", "0" * 64),
            ("new_runtime_authority", True),
        ]:

            def changed_manifest(field=field, value=value):
                with manifest_edit(lambda m: m.update({field: value})):
                    inspect()

            reason = (
                "cannot grant conformance"
                if field.endswith("support") or field.endswith("sets")
                else (
                    "stale work manifest"
                    if field == "approval_digest"
                    else "cannot add authority"
                )
            )
            case("manifest_" + field, changed_manifest, reason)
        case(
            "GRC9V4_before_G3",
            lambda: registered("src/pygrc/models/grc_9_v4.py", content),
            "specialization requires accepted P9-G3",
        )
        case(
            "GRC9V4_iteration_before_G3",
            lambda: registered(source, content, leaf="P9-8.2"),
            "specialization requires accepted P9-G3",
        )
        case(
            "unregistered_leaf",
            lambda: registered(source, content, leaf="P9-2.999"),
            "unregistered work iteration",
        )
        case(
            "unreviewed_new_V4_module",
            lambda: registered("src/pygrc/models/grc_v4_surprise.py", content),
            "unapproved runtime or evidence target",
        )
        case(
            "stale_work_bytes",
            lambda: registered(
                source, content, extra=lambda: edit(source, content + b"x=1\n")
            ),
            "work content binding mismatch",
        )
        case(
            "combined_good_and_frozen_edit",
            lambda: registered(
                source, content, extra=lambda: edit("specs/grc-v4-spec.md", b"changed")
            ),
            "frozen bytes changed",
        )
        legacy = "src/pygrc/models/grc_9_v3.py"
        case(
            "legacy_bytes",
            lambda: edit(legacy, (root / legacy).read_bytes() + b"\n# changed\n"),
            "frozen bytes changed",
        )
        case(
            "legacy_test_bytes",
            lambda: edit("tests/core/test_capabilities.py", b"# changed\n"),
            "frozen bytes changed",
        )
        case(
            "old_planning_policy",
            lambda: edit(p.planning.POLICY, b"{}"),
            "immutable predecessor changed",
        )
        init = "src/pygrc/models/__init__.py"
        before = (root / init).read_bytes()
        lazy = b'\n\ndef __getattr__(name):\n    if name == "GRCV4":\n        from .grc_v4 import GRCV4\n        return GRCV4\n    raise AttributeError(name)\n'

        def integration_contract(name, before, after):
            traces.append(
                {
                    "check": "isolated_integration_contract_not_leaf_permission",
                    "path": name,
                    "before_hex": before.hex(),
                    "after_hex": after.hex(),
                }
            )
            p.integration(name, before, after)

        def integration_case(name, filename, before, after, expected=None):
            case(
                name,
                lambda: integration_contract(filename, before, after),
                expected,
                scope="isolated_integration_contract_not_current_leaf_permission",
            )

        integration_case("additive_lazy_export", init, before, before + lazy)
        case(
            "eager_export_rejected",
            lambda: integration_contract(
                init, before, before + b"\nfrom .grc_v4 import GRCV4\n"
            ),
            "unreviewed or eager V4 export",
            scope="isolated_integration_contract_not_current_leaf_permission",
        )
        case(
            "legacy_export_rebinding",
            lambda: integration_contract(
                init, before, b"# legacy names removed\n" + lazy
            ),
            "legacy export prefix changed",
            scope="isolated_integration_contract_not_current_leaf_permission",
        )
        # Use the immutable integration baseline even after V4's extra exists.
        project = p.git(root, "show", p.BASELINE + ":pyproject.toml")
        # Insert into the existing optional-dependencies table, not a duplicate table.
        extra = project.replace(
            b"[project.optional-dependencies]\n",
            b'[project.optional-dependencies]\nv4 = ["numpy>=2.0", "rfc8785", "jsonschema"]\n',
        )
        p.require(extra != project, "fixture cannot locate optional-dependencies")
        integration_case(
            "additive_V4_dependency_extra", "pyproject.toml", project, extra
        )
        case(
            "unreviewed_dependency",
            lambda: integration_contract(
                "pyproject.toml", project, extra.replace(b'"rfc8785"', b'"unexpected"')
            ),
            "unreviewed V4 dependency",
            scope="isolated_integration_contract_not_current_leaf_permission",
        )
        case(
            "legacy_dependency_change",
            lambda: integration_contract(
                "pyproject.toml", project, extra + b"\n[unreviewed]\nflag=true\n"
            ),
            "non-additive dependency integration",
            scope="isolated_integration_contract_not_current_leaf_permission",
        )
        asset = "src/pygrc/models/grc_v4_assets/grc-v4-contract-schema.json"
        case(
            "exact_packaged_schema",
            lambda: registered(
                asset,
                (root / "specs/grc-v4-contract-schema.json").read_bytes(),
                leaf="P9-2.2",
            ),
        )
        case(
            "changed_packaged_schema",
            lambda: registered(asset, b"{}", leaf="P9-2.2"),
            "packaged accepted asset differs",
        )

        def mode():
            with mutate(source, content):
                (root / source).chmod(0o755)
                with manifest_edit(
                    lambda m: bind_entry(m, source, content)
                ):
                    inspect()

        case("runtime_mode", mode, "unapproved executable runtime mode")

        def symlink():
            with mutate(source, content):
                (root / source).unlink()
                (root / source).symlink_to(root / "specs/grc-v4-spec.md")
                with manifest_edit(
                    lambda m: bind_entry(m, source, content)
                ):
                    inspect()

        case("runtime_symlink", symlink, "symlink at protected path")

        def normal(name=None, bytes_=None):
            command = [
                sys.executable,
                str(root / p.SCRIPTS / "run.py"),
                "verify-phase9",
                "--boundary-only",
            ]
            result = subprocess.run(
                command, cwd=scratch, capture_output=True, text=True
            )
            traces.append(
                {
                    "check": "actual_subprocess",
                    "command": command,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            )
            if result.returncode:
                raise ValueError(result.stdout + result.stderr)

        def normal_bad():
            with mutate("src/pygrc/models/not_reviewed.py", content):
                normal()

        case(
            "normal_entry_forbidden_source",
            normal_bad,
            "unauthorized source/test/planning addition",
        )
        case("normal_entry_accepted_G1", normal)
        case(
            "normal_entry_accepted_runtime_target",
            lambda: registered(source, content, extra=normal),
        )

        case(
            "ready_identity_leaf",
            lambda: registered(
                "src/pygrc/models/grc_v4_codec.py", content, leaf="P9-2.2"
            ),
        )
        case(
            "accepted_foundation_enables_request_leaf",
            lambda: registered("src/pygrc/models/grc_v4.py", content, leaf="P9-2.3"),
        )
        case(
            "geometry_work_does_not_accept_next_leaf",
            lambda: registered(p.PHASE + "evidence/P9-3.2/probe/inputs.json",
                               b"{}", leaf="P9-3.2"),
            "owning leaf entry dependencies are not accepted",
        )
        for name in ["src/pygrc/models/grc_v4_state.py", "src/pygrc/models/grc_v4_step.py"]:
            case("accepted_requests_enable_result_owner_" + Path(name).stem,
                 lambda name=name: registered(name, content, leaf="P9-2.4"))
        for name in ["tests/models/grcv4_conformance_harness.py", "tests/models/grcv4_reference_oracles.py"]:
            case("accepted_results_enable_harness_owner_" + Path(name).stem,
                 lambda name=name: registered(name, content, leaf="P9-2.5"))
        for name in ['src/pygrc/models/grc_v4_geometry.py', 'src/pygrc/models/grc_v4_transport.py', 'tests/models/test_grc_v4_geometry.py', 'tests/models/test_grc_v4_transport.py']:
            case("accepted_integration_enables_" + Path(name).stem,
                 lambda name=name: registered(name, content, leaf="P9-3.1"))
        case("accepted_harness_enables_export_owner",
             lambda: registered(init, before + lazy, leaf="P9-2.6"))
        for key, replacement in [("status", "pending"), ("accepted_iterations", ["P9-2.5", "P9-2.6"]),
                                 ("accepted_generic_runtime_support", ["C_OS"]),
                                 ("baseline_commit", p.BASELINE), ("evidence_bindings", [])]:
            def forged_harness(key=key, replacement=replacement):
                value = p.read(root / p.HARNESS_ACCEPTANCE)
                value[key] = replacement
                value["record_digest"] = p.digest_record(value)
                with mutate(p.HARNESS_ACCEPTANCE, p.canonical(value)):
                    p.accepted_harness(root)
            case("harness_acceptance_cannot_self_authorize_" + key, forged_harness,
                 "untrusted harness acceptance", scope="isolated_harness_acceptance_authentication")
        case("missing_integration_acceptance",
             lambda: edit(p.INTEGRATION_ACCEPTANCE, None),
             "P9-2.6-AcceptanceRecord.json")
        for key, replacement in [("status", "pending"), ("accepted_iterations", ["P9-2.6", "P9-3.1"]),
                                 ("accepted_generic_runtime_support", ["C_OS"]),
                                 ("admitted_specialization_support_sets", [["C_OS"]]),
                                 ("baseline_commit", p.BASELINE), ("evidence_bindings", [])]:
            def forged_integration(key=key, replacement=replacement):
                value = p.read(root / p.INTEGRATION_ACCEPTANCE)
                value[key] = replacement
                value["record_digest"] = p.digest_record(value)
                with mutate(p.INTEGRATION_ACCEPTANCE, p.canonical(value)):
                    p.accepted_integration(root)
            case("integration_acceptance_cannot_self_authorize_" + key, forged_integration,
                 "untrusted integration acceptance", scope="isolated_integration_acceptance_authentication")
        for key, replacement in [("status", "pending"), ("accepted_iterations", ["P9-2.4", "P9-2.5"]),
                                 ("accepted_generic_runtime_support", ["C_OS"]),
                                 ("baseline_commit", p.BASELINE), ("evidence_bindings", [])]:
            def forged_results(key=key, replacement=replacement):
                value = p.read(root / p.RESULT_ACCEPTANCE)
                value[key] = replacement
                value["record_digest"] = p.digest_record(value)
                with mutate(p.RESULT_ACCEPTANCE, p.canonical(value)):
                    p.accepted_results(root)
            case("result_acceptance_cannot_self_authorize_" + key, forged_results,
                 "untrusted result acceptance", scope="isolated_result_acceptance_authentication")
        for key, replacement in [("status", "pending"), ("accepted_iterations", ["P9-2.3", "P9-2.4"]),
                                 ("accepted_generic_runtime_support", ["C_OS"]),
                                 ("baseline_commit", p.BASELINE), ("evidence_bindings", [])]:
            def forged_requests(key=key, replacement=replacement):
                value = p.read(root / p.REQUEST_ACCEPTANCE)
                value[key] = replacement
                value["record_digest"] = p.digest_record(value)
                with mutate(p.REQUEST_ACCEPTANCE, p.canonical(value)):
                    p.accepted_requests(root)
            case("request_acceptance_cannot_self_authorize_" + key, forged_requests,
                 "untrusted request acceptance", scope="isolated_request_acceptance_authentication")
        for key, replacement in [
            ("status", "pending"),
            ("accepted_iterations", ["P9-2.1", "P9-2.2", "P9-2.3"]),
            ("accepted_generic_runtime_support", ["C_OS"]),
            ("baseline_commit", p.BASELINE),
            ("evidence_bindings", []),
        ]:
            def forged_foundation(key=key, replacement=replacement):
                value = p.read(root / p.FOUNDATION)
                value[key] = replacement
                value["record_digest"] = p.digest_record(value)
                with mutate(p.FOUNDATION, p.canonical(value)):
                    p.accepted_foundation(root)

            case("foundation_cannot_self_authorize_" + key, forged_foundation,
                 "untrusted foundation acceptance",
                 scope="isolated_foundation_acceptance_authentication")
        case(
            "later_generic_leaf_held",
            lambda: registered(
                "src/pygrc/models/grc_v4_candidate_c.py", content, leaf="P9-4.1"
            ),
            "owning leaf entry dependencies are not accepted",
        )
        case(
            "path_cannot_borrow_ready_leaf",
            lambda: registered("src/pygrc/models/grc_v4_candidate_a.py", content),
            "runtime target belongs to a different owning leaf",
        )
        case(
            "accepted_harness_enables_integration_owner",
            lambda: registered("pyproject.toml", extra, leaf="P9-2.6"),
        )
        case("geometry_leaf_direct_numpy_dependency_owner",
             lambda: registered("pyproject.toml", extra, leaf="P9-3.1"))
        case(
            "identity_leaf_package_integration",
            lambda: registered("pyproject.toml", extra, leaf="P9-2.2"),
        )
        case(
            "identity_leaf_cannot_borrow_exports",
            lambda: registered(init, before + lazy, leaf="P9-2.2"),
            "runtime target belongs to a different owning leaf",
        )
        for key, replacement in [
            ("release_id", "different-release"),
            ("baseline_commit", p.prior.CHECKPOINT),
            ("user_authority", {"answer": "not accepted"}),
        ]:

            def approval_change(key=key, replacement=replacement):
                value = p.read(root / p.APPROVAL)
                value[key] = replacement
                value["record_digest"] = p.digest_record(value)
                edit(p.APPROVAL, p.canonical(value))

            case("acceptance_" + key, approval_change, "untrusted P9-G1 acceptance")
        case(
            "missing_consumed_surface_evidence",
            lambda: edit(p.PHASE + "tranche-1/P9-1.8-SurfaceInventory.json", None),
            "P9-1.8-SurfaceInventory.json",
        )
        case(
            "conflicting_G1_record",
            lambda: edit(
                p.PHASE + "tranche-1/P9-1.9-OtherAcceptance.json",
                (root / p.APPROVAL).read_bytes(),
            ),
            "unauthorized source/test/planning addition",
        )
        helper = p.HERE + "phase9_implementation_policy.py"
        case(
            "changed_verifier_after_pressure",
            lambda: edit(helper, (root / helper).read_bytes() + b"\n# altered\n"),
            "implementation maintenance binding drift",
        )
        case(
            "runtime_manifest_cannot_change_governance",
            lambda: registered(p.POLICY, (root / p.POLICY).read_bytes()),
            "unapproved runtime or evidence target",
        )

        def escaped():
            with manifest_edit(
                lambda v: v["entries"].append(
                    {
                        "path": "../escape.py",
                        "sha256": p.sha(content),
                        "iteration_id": "P9-2.1",
                    }
                )
            ):
                inspect()

        case("evidence_path_escape", escaped, "unsafe path")

        def repeated():
            first, second = inspect(), inspect()
            p.require(first == second, "repeat changed authority")

        case("identical_acceptance_is_idempotent", repeated)
        case(
            "partial_publication",
            lambda: edit(p.RECORD, None),
            "P9-1.9-ExecutionRecord.json",
        )

        def synthetic_acceptance():
            value = p.read(root / p.APPROVAL)
            value["user_authority"] = {
                "answer": "synthetic accepted fixture",
                "scope": "test only",
            }
            value["record_digest"] = p.digest_record(value)
            edit(p.APPROVAL, p.canonical(value))

        case(
            "synthetic_acceptance_not_live_authority",
            synthetic_acceptance,
            "untrusted P9-G1 acceptance",
        )

        def committed_wrong_tree():
            # Both commits and index restoration are confined to this private clone.
            baseline = p.git(root, "rev-parse", "HEAD").decode().strip()

            def git(*args):
                result = subprocess.run(
                    ["git", *args], cwd=root, capture_output=True, text=True
                )
                traces.append(
                    {
                        "check": "actual_subprocess",
                        "command": ["git", *args],
                        "cwd": str(root),
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    }
                )
                p.require(
                    result.returncode == 0,
                    "isolated Git fixture setup failed: " + result.stderr,
                )
                return result.stdout

            try:
                git("add", "--", *sorted(p.PATHS | current_work_paths))
                git(
                    "-c",
                    "user.name=P9 test fixture",
                    "-c",
                    "user.email=p9-fixture@example.invalid",
                    "commit",
                    "--quiet",
                    "-m",
                    "isolated accepted G1 fixture",
                )
                with mutate(
                    legacy,
                    (root / legacy).read_bytes() + b"\n# unauthorized committed edit\n",
                ):
                    git("add", "--", legacy)
                    git(
                        "-c",
                        "user.name=P9 test fixture",
                        "-c",
                        "user.email=p9-fixture@example.invalid",
                        "commit",
                        "--quiet",
                        "-m",
                        "isolated unauthorized fixture",
                    )
                    p.require(
                        git("status", "--porcelain") == "",
                        "fixture is not a clean committed tree",
                    )
                    inspect()
            finally:
                git("reset", "--mixed", baseline)

        case(
            "clean_committed_unauthorized_tree",
            committed_wrong_tree,
            "frozen bytes changed",
        )

        def published_work(name, bytes_, attempt):
            previous = p.git(root, "rev-parse", "HEAD").decode().strip()

            def local_git(*args):
                command = ["git", *args]
                result = subprocess.run(
                    command, cwd=root, capture_output=True, text=True
                )
                traces.append(
                    {
                        "check": "actual_subprocess",
                        "command": command,
                        "cwd": str(root),
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    }
                )
                p.require(
                    result.returncode == 0,
                    "published fixture Git failure: " + result.stderr,
                )

            with mutate(name, bytes_):
                with manifest_edit(
                    lambda v: bind_entry(v, name, bytes_)
                ):
                    try:
                        local_git("add", "--", *sorted(p.PATHS | current_work_paths | {name}))
                        local_git(
                            "-c",
                            "user.name=P9 test fixture",
                            "-c",
                            "user.email=p9-fixture@example.invalid",
                            "commit",
                            "--quiet",
                            "-m",
                            "isolated published work fixture",
                        )
                        attempt(local_git)
                    finally:
                        local_git("reset", "--mixed", previous)

        case(
            "published_runtime_update",
            lambda: published_work(
                source, content, lambda _: registered(source, content + b"x=1\n")
            ),
        )

        def delete_published(local_git):
            with mutate(source, None):
                with manifest_edit(
                    lambda v: v.update(
                        entries=[r for r in v["entries"] if r["path"] != source]
                    )
                ):
                    local_git("rm", "--cached", "--", source)
                    inspect()

        case(
            "published_runtime_deletion",
            lambda: published_work(source, content, delete_published),
            "published runtime/evidence deletion or rename forbidden",
        )
        evidence = p.PHASE + "evidence/P9-2.1/failed-fixture/stdout.txt"
        case(
            "published_failure_evidence_overwrite",
            lambda: published_work(
                evidence,
                b"failed original run\n",
                lambda _: registered(evidence, b"replacement success\n"),
            ),
            "published run evidence is immutable",
        )
        case(
            "new_evidence_run_preserves_failure",
            lambda: published_work(
                evidence,
                b"failed original run\n",
                lambda _: registered(
                    p.PHASE + "evidence/P9-2.1/new-fixture/stdout.txt",
                    b"new independent run\n",
                ),
            ),
        )

        def before_acceptance():
            with tempfile.TemporaryDirectory(
                prefix="grcv4-p919-before-acceptance-"
            ) as before_root:
                historical = Path(before_root) / "repository"
                subprocess.run(
                    [
                        "git",
                        "clone",
                        "--shared",
                        "--quiet",
                        "--no-checkout",
                        str(p.ROOT),
                        str(historical),
                    ],
                    check=True,
                )
                subprocess.run(
                    ["git", "checkout", "--quiet", "--detach", p.BASELINE],
                    cwd=historical,
                    check=True,
                )
                (historical / ".venv").symlink_to(
                    Path(sys.prefix).resolve(), target_is_directory=True
                )
                (historical / source).write_bytes(content)
                command = [
                    sys.executable,
                    str(historical / p.SCRIPTS / "run.py"),
                    "verify-post-d10-specifications",
                ]
                result = subprocess.run(
                    command, cwd=before_root, capture_output=True, text=True
                )
                traces.append(
                    {
                        "check": "actual_preacceptance_normal_command",
                        "command": command,
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "same_target": source,
                        "same_content_hex": content.hex(),
                        "historical_policy_digest": p.read(
                            historical / p.planning.POLICY
                        )["record_digest"],
                    }
                )
                p.require(
                    result.returncode != 0
                    and "unauthorized source/test/planning addition" in result.stderr,
                    "preacceptance normal route did not reject same addition",
                )
                raise ValueError("planning authority rejects the same runtime addition")

        case(
            "preacceptance_same_runtime_addition",
            before_acceptance,
            "planning authority rejects the same runtime addition",
            scope="exact_6e0a507_planning_subject_before_actual_G1_acceptance",
        )

    p.require(protected_manifest(p.ROOT) == original, "pressure modified live checkout")
    report = {
        "schema": p.REPORT_SCHEMA,
        "run_id": run_id,
        "policy_digest": boundary["record_digest"],
        "tree": tree,
        "approval_digest": p.APPROVAL_DIGEST,
        "cases": cases,
        "passed": sum(r["assertion_result"] == "passed" for r in cases),
        "failed": sum(r["assertion_result"] == "failed" for r in cases),
        "live_protected_manifest_before_after": original,
        "runtime_conformance_claimed": False,
    }
    report["report_digest"] = p.digest_record(report, "report_digest")
    destination = p.ROOT / p.GENERATED
    destination.mkdir(parents=True, exist_ok=True)
    (destination / p.REPORT_FILE).write_bytes(p.canonical(report) + b"\n")
    archive = destination / "runs" / run_id
    archive.mkdir(parents=True)
    (archive / p.REPORT_FILE).write_bytes(p.canonical(report) + b"\n")
    for row in cases:
        if row["assertion_result"] != "passed":
            print(
                "FAILED",
                row["case_id"],
                row["actual_reason"],
                "expected",
                row["expected_reason"],
            )
    p.require(report["failed"] == 0, "P9-G1 pressure failures")
    print(
        f"PHASE9_G1_PRESSURE_PASS cases={len(cases)} accepted_permission=true conformance_claimed=false live_runtime_unchanged=true"
    )


if __name__ == "__main__":
    main()
