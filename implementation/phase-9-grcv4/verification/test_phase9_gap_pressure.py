"""Guide-specific combined, semantic, real-route and checker-sensitivity probes."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import tempfile

import phase9_policy as p
from phase9_semantics import source_projection, validate_projection


def extend(suite, root, policy, changed):
    case = suite.case
    final_batch = "staleness_route_fault_sensitivity"
    expected = source_projection(root)

    def semantic(edit):
        candidate = deepcopy(expected)
        edit(candidate)
        suite.mutation("source_admitted_semantic_projection", expected, candidate)
        suite.trace.append(
            {
                "check": "validate_projection_after_source_admission",
                "source_binding": suite.keep(expected["source_bindings"]),
            }
        )
        validate_projection(candidate, expected)

    edits = [
        (
            "conditional_to_normative",
            "claims",
            lambda x: next(
                r
                for r in x["claims"]
                if r["source_claim"]["claim_class"] == "conditional"
            )["source_claim"].update(claim_class="normative"),
        ),
        (
            "indeterminate_to_supported",
            "contracts",
            lambda x: x["contracts"][0].update(support_disposition="supported"),
        ),
        (
            "candidate_C_optional_to_universal",
            "contracts",
            lambda x: next(
                r for r in x["contracts"] if r["contract_id"].startswith("D11-C-")
            )["source_contract"].update(profile_ids=["ALL_PROFILES"]),
        ),
        (
            "GRC9_specialization_to_generic",
            "contracts",
            lambda x: next(
                r for r in x["contracts"] if r["contract_id"].startswith("D11-G9-")
            ).update(planning_scope="graph_generic_all_profiles"),
        ),
        (
            "forty_cell_duplicate_same_count",
            "compatibility_cells",
            lambda x: x["compatibility_cells"].__setitem__(
                0, deepcopy(x["compatibility_cells"][1])
            ),
        ),
        (
            "planned_C_OS_to_runtime_supported",
            "profiles",
            lambda x: next(
                r for r in x["profiles"] if r["profile_family"] == "C_OS"
            ).update(current_support="accepted_runtime"),
        ),
        (
            "alias_as_second_execution",
            "evidence_aliases",
            lambda x: x["evidence_aliases"][0].update(
                evidence_alias_of=None, status="executed_independently"
            ),
        ),
        (
            "pending_obligation_to_nonapplicable",
            "obligations",
            lambda x: x["obligations"][-1]["phase9_route"].update(
                downstream_disposition="not_applicable"
            ),
        ),
        (
            "deferred_RG2b_to_scientific_rejection",
            "deferred",
            lambda x: x["deferred"].__setitem__(0, "RG2b scientifically rejected"),
        ),
        (
            "unknown_claim_not_fuzzy_resolved",
            "claims",
            lambda x: x["claims"][0].update(
                claim_id=x["claims"][0]["claim_id"] + "-unknown"
            ),
        ),
    ]
    case(
        "source_exact_semantic_projection",
        2,
        lambda: validate_projection(expected, expected),
        scope="source_bound_projection_not_new_claim_authority",
    )
    for name, field, edit in edits:
        case(
            name,
            6,
            lambda edit=edit: semantic(edit),
            reject=True,
            rule="semantic projection drift: " + field,
            scope="controlled_projection_after_source_admission",
        )

    for name, links in [
        ("self_referential_predecessor", {"candidate": ["candidate"]}),
        ("cyclic_predecessor_chain", {"candidate": ["next"], "next": ["candidate"]}),
    ]:

        def cycle(links=links):
            value = deepcopy(policy)
            value["predecessor_chain"] = links
            value["record_digest"] = p.digest_record(value)
            with changed(root, p.POLICY, p.canonical(value)):
                p.current_boundary(root)

        case(
            name,
            6,
            cycle,
            reject=True,
            rule="unsupported successor fields or candidate predecessor chain",
            scope="unsupported_candidate_chain_rejected_not_a_new_graph_protocol",
        )

    def conflict():
        name = p.HERE + "ConflictingRuntimeSuccessor.json"
        with changed(
            root,
            name,
            p.canonical(
                {
                    "runtime_authorized": True,
                    "P9_G1_accepted": True,
                    "release_id": p.prior.RELEASE_ID,
                }
            ),
        ):
            p.current_boundary(root)

    case(
        "conflicting_candidate_successors",
        6,
        conflict,
        reject=True,
        rule="unauthorized source/test/planning addition",
    )

    def normal_mutation(name, content):
        with changed(root, name, content):
            candidate_before = suite.keep(
                __import__("pressure_evidence").protected_manifest(root)
            )
            result = suite.command(
                [sys.executable, str(root / p.SCRIPTS / "run.py"), "verify-iteration9"],
                cwd=root.parent,
            )
            candidate_after = suite.keep(
                __import__("pressure_evidence").protected_manifest(root)
            )
            p.require(
                candidate_before == candidate_after,
                "normal rejection modified protected state",
            )
            p.require(
                result.returncode != 0, "normal route incorrectly admitted candidate"
            )
            return {
                "candidate_decision": "rejected",
                "reason": result.stdout + result.stderr,
            }

    case(
        "normal_entry_forbidden_source",
        1,
        lambda: normal_mutation(
            "src/pygrc/models/grc_v4.py", b"# unauthorized runtime fixture\n"
        ),
        decision="rejected",
        rule="unauthorized source/test/planning addition",
        batch=final_batch,
    )
    case(
        "normal_entry_frozen_corruption",
        6,
        lambda: normal_mutation("specs/grc-v4-spec.md", b"# corrupted frozen source\n"),
        decision="rejected",
        rule="frozen bytes changed",
        batch=final_batch,
    )

    def mixed_allowed_forbidden():
        # The exact allowed candidate additions are already present and bound.
        p.validate_policy(root)
        suite.trace.append(
            {
                "check": "authorized_review_additions_recognized",
                "policy_digest": policy["record_digest"],
            }
        )
        with changed(
            root,
            "src/pygrc/models/grc_9_v3.py",
            (root / "src/pygrc/models/grc_9_v3.py").read_bytes()
            + b"\n# forbidden legacy edit\n",
        ):
            p.current_boundary(root)

    case(
        "combined_allowed_review_and_legacy_corruption",
        6,
        mixed_allowed_forbidden,
        reject=True,
        rule="frozen bytes changed",
        batch=final_batch,
    )

    def all_rehashed_forgery():
        name = "src/pygrc/models/grc_v4.py"
        value = deepcopy(policy)
        value["authorization_effect"]["runtime_authorized"] = True
        value["trusted_runtime_approval"] = "f" * 64
        value["exact_mutation_paths"].append(name)
        content = b"# forged candidate runtime\n"
        value["artifact_bindings"].append({"path": name, "sha256": p.sha(content)})
        value["record_digest"] = p.digest_record(value)
        record = p.read(root / p.RECORD)
        record["policy_digest"] = value["record_digest"]
        record["runtime_authorized"] = True
        with (
            changed(root, name, content),
            changed(root, p.POLICY, p.canonical(value)),
            changed(root, p.RECORD, p.canonical(record)),
        ):
            p.current_boundary(root)

    case(
        "combined_rehashed_runtime_grant_and_source",
        6,
        all_rehashed_forgery,
        reject=True,
        rule="planning cannot grant runtime authority",
        batch=final_batch,
    )

    def stale_report():
        # Reuse only the recorded historical subject, never its old current-tree
        # conclusion. These are actual retained historical command results.
        from audit_phase9_successor import historical_evidence

        receipt = historical_evidence(p.ROOT)
        history = [
            c for c in receipt["commands"] if c["label"].startswith("historical_audit_")
        ]
        p.require(
            len(history) == 4 and all(c["exit_code"] == 0 for c in history),
            "recorded historical checks unavailable",
        )
        suite.trace.append(
            {
                "check": "recorded_green_history_not_current_attestation",
                "historical_subject": p.prior.HISTORICAL,
                "receipt_digest": receipt["evidence_digest"],
                "command_evidence": suite.keep(history),
            }
        )
        baseline, tree = p.current_boundary(root)
        suite.trace.append(
            {
                "check": "valid_current_baseline",
                "policy_digest": baseline["record_digest"],
                "tree": tree,
                "historical_subject": p.prior.HISTORICAL,
            }
        )
        name = p.PHASE + "tranche-1/P9-1.1-SourceCrosswalk.json"
        value = p.read(root / name)
        count = len(value["contracts"])
        value["contracts"][0]["support_disposition"] = "supported"
        p.require(
            len(value["contracts"]) == count, "fixture accidentally changed counts"
        )
        with changed(root, name, p.canonical(value)):
            result = suite.command(
                [sys.executable, str(root / p.SCRIPTS / "run.py"), "verify-iteration9"]
            )
            p.require(
                result.returncode != 0,
                "old valid subject substituted for changed current tree",
            )
            return {
                "candidate_decision": "rejected",
                "reason": result.stdout + result.stderr,
            }

    case(
        "combined_green_history_stale_current_unchanged_counts",
        6,
        stale_report,
        decision="rejected",
        rule="frozen bytes changed",
        batch=final_batch,
    )

    def sensitivity():
        with tempfile.TemporaryDirectory(prefix="grcv4-broken-checker-") as directory:
            folder = Path(directory) / "checker"
            folder.mkdir()
            original = (p.ROOT / p.HERE / "phase9_policy.py").read_text()
            needle = "blob_id(path.read_bytes()) == oid"
            p.require(
                original.count(needle) == 1, "broken-checker fixture target drift"
            )
            mutated = original.replace(needle, "True")
            (folder / "phase9_policy.py").write_text(mutated)
            (folder / "audit_phase9.py").write_bytes(
                (p.ROOT / p.HERE / "audit_phase9.py").read_bytes()
            )
            spec = importlib.util.spec_from_file_location(
                "deliberately_broken_checker", folder / "phase9_policy.py"
            )
            broken = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(broken)
            with changed(root, "specs/grc-v4-spec.md", b"# corrupted source\n"):
                from pressure_evidence import assertion_matches

                observed = {}
                for label, checker in [("intact", p), ("broken", broken)]:
                    try:
                        checker.current_boundary(root)
                        decision, reason = "admitted", "no rejection"
                    except ValueError as error:
                        decision, reason = "rejected", str(error)
                    matched = assertion_matches(
                        decision, "rejected", "frozen bytes changed" in reason
                    )
                    observed[label] = {
                        "candidate_decision": decision,
                        "assertion_result": "passed" if matched else "failed",
                        "reason": reason,
                    }
                p.require(
                    observed["intact"]["assertion_result"] == "passed"
                    and observed["broken"]["assertion_result"] == "failed",
                    "negative test is inert to removal of frozen guard",
                )
            suite.trace.append(
                {
                    "check": "broken_checker_negative_control",
                    "removed_protection": needle,
                    "original_sha256": p.sha(original.encode()),
                    "broken_sha256": p.sha(mutated.encode()),
                    "observed_assertions": observed,
                    "live_checker_modified": False,
                }
            )

    case(
        "broken_frozen_guard_makes_its_negative_assertion_fail",
        6,
        sensitivity,
        scope="isolated_broken_checker_control_not_admitted_live_authority",
        batch=final_batch,
    )

    def staged_then_unstaged():
        name = p.SCRIPTS + "active_phase.py"
        p.git(root, "add", name)
        try:
            with changed(root, name, b"print('unauthorized unstaged code')\n"):
                p.current_boundary(root)
        finally:
            p.git(root, "update-index", "--force-remove", name)

    case(
        "authorized_staged_bytes_do_not_hide_unstaged_helper",
        6,
        staged_then_unstaged,
        reject=True,
        rule="unauthorized content at permitted path",
    )

    for name in ["src/pygrc/models/grc_v40.py", p.HERE + "json.py"]:

        def extra(name=name):
            with changed(root, name, b"# unauthorized prefix or import shadow\n"):
                p.current_boundary(root)

        case(
            "untracked_scope_" + name.replace("/", "_"),
            6,
            extra,
            reject=True,
            rule="unauthorized source/test/planning addition",
        )

    def rename():
        old = "specs/grc-v4-spec.md"
        new = "specs/grc-v4-renamed.md"
        with changed(root, new, (root / old).read_bytes()), changed(root, old, None):
            p.current_boundary(root)

    case(
        "protected_rename_is_not_an_allowed_addition",
        6,
        rename,
        reject=True,
        rule="missing protected file",
    )

    # Explicit time-of-check/time-of-use injection at the final-subject guard;
    # no historical assertion or successful check is suppressed by this probe.
    from audit_phase9_successor import require_same_subject

    def toctou():
        before = p.current_boundary(root)
        with changed(root, p.RECORD, (root / p.RECORD).read_bytes() + b"\n"):
            after = p.current_boundary(root)
            suite.trace.append(
                {
                    "check": "final_subject_revalidation",
                    "before": suite.keep(before),
                    "after": suite.keep(after),
                }
            )
            require_same_subject(before, after)

    case(
        "mid_verification_subject_change",
        6,
        toctou,
        reject=True,
        rule="verification inputs changed during execution",
        batch=final_batch,
    )

    def unavailable_history():
        try:
            p.prior.ancestor(root, "0" * 40)
        except ValueError as error:
            return {"candidate_decision": "unverifiable", "reason": str(error)}

    case(
        "missing_historical_commit_is_unverifiable",
        6,
        unavailable_history,
        decision="unverifiable",
        rule="missing ancestor",
        batch=final_batch,
    )

    def committed_clean():
        with tempfile.TemporaryDirectory(prefix="grcv4-committed-probe-") as directory:
            target = Path(directory) / "repo"
            p.git(
                root,
                "clone",
                "--shared",
                "--quiet",
                "--no-checkout",
                str(p.ROOT),
                str(target),
            )
            p.git(target, "checkout", "--quiet", p.prior.CHECKPOINT)
            for name in p.PATHS:
                path = target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((p.ROOT / name).read_bytes())
            victim = "src/pygrc/models/grc_9_v3.py"
            (target / victim).write_bytes(
                (target / victim).read_bytes() + b"\n# unauthorized committed fixture\n"
            )
            p.git(target, "add", "--all")
            p.git(
                target,
                "-c",
                "user.name=Isolated pressure fixture",
                "-c",
                "user.email=fixture@invalid",
                "-c",
                "commit.gpgsign=false",
                "commit",
                "--quiet",
                "-m",
                "Disposable unauthorized candidate, not project authority",
            )
            p.require(
                p.git(target, "status", "--porcelain") == b"",
                "committed fixture is not clean",
            )
            suite.trace.append(
                {
                    "check": "clean_committed_candidate",
                    "head": p.git(target, "rev-parse", "HEAD").decode().strip(),
                    "dirty": False,
                    "mutation": victim,
                }
            )
            p.current_boundary(target)

    case(
        "unauthorized_committed_clean_tree",
        6,
        committed_clean,
        reject=True,
        rule="frozen bytes changed",
        batch=final_batch,
    )
