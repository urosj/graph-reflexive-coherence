"""Evidence recorder for isolated probes; expectations are independent of policy."""

from contextlib import contextmanager
from functools import wraps
from pathlib import Path
import os
import traceback
import uuid

import phase9_policy as p


# Expected decisive rules, not merely any exception. New named probes supply
# their own rule explicitly. These bind the original 79 cases to real checks.
RULES = {
    "execution_record_baseline_commit": "execution record predecessor/entry mismatch",
    "execution_record_release_id": "execution record predecessor/entry mismatch",
    "execution_record_accepted_generic_runtime_support": "execution record advertises unexecuted support",
    "execution_record_P9_G1_accepted": "execution record promotes authority",
    "planning_rejects_src_": "unauthorized source/test/planning addition",
    "planning_rejects_tests_": "unauthorized source/test/planning addition",
    "planning_rejects_pyproject": "frozen bytes changed",
    "changed_frozen_spec": "frozen bytes changed",
    "deleted_frozen_spec": "missing protected file",
    "permitted_path_wrong_content": "unauthorized content at permitted path",
    "deleted_successor_record": "missing protected file",
    "deleted_phase_marker": "missing protected file",
    "modified_prior_review": "frozen bytes changed",
    "assume_unchanged_": "frozen bytes changed",
    "staged_runtime_": "unauthorized source/test/planning addition",
    "ignored_runtime_": "unauthorized source/test/planning addition",
    "protected_symlink_": "symlink at protected path",
    "protected_mode_": "frozen mode changed",
    "rehashed_policy_status": "contradictory successor status",
    "rehashed_policy_baseline_commit": "stale successor predecessor",
    "rehashed_policy_release_id": "stale successor predecessor",
    "rehashed_policy_trusted_runtime_approval": "planning cannot grant runtime authority",
    "rehashed_policy_accepted_generic_runtime_support": "unexecuted support advertised",
    "rehashed_policy_active_phase": "unsupported live successor state",
    "stale_digest_": "successor digest mismatch",
    "green_marker_not_policy": "unsupported successor fields",
    "duplicate_json_key": "duplicate JSON key",
    "runtime_flag_not_authority": "runtime authority absent",
    "self_declared_runtime_": "runtime authority absent",
    "self_rehashed_runtime_": "untrusted runtime authority",
    "runtime_wrong_target_..": "unsafe runtime target",
    "runtime_wrong_target_": "non-V4 or non-new runtime addition",
    "approved_path_changed_": "runtime target content mismatch",
    "legacy_dependency_": "non-additive dependency integration",
    "legacy_export_": "legacy export rebound",
    "required_child_": "required child missing or substituted",
    "matching_count_child_": "required child missing or substituted",
    "forged_evidence_alias": "forged child parent/evidence alias",
    "unresolved_dependency": "unresolved dependency",
    "dependency_cycle": "dependency cycle",
    "unrelated_c_os_barrier_": "C_OS prerequisites omitted or unrelated profile barrier",
    "unexecuted_exact_profile": "unexecuted exact identity advertised",
    "unexecuted_support_set": "unexecuted support advertised",
    "universal_optional_completion": "mandatory lifecycle lost or optional completion universal",
    "completion_cannot_borrow_": "completion evidence belongs to a different exact profile scope",
}
ACTIVE = None


def assertion_matches(actual, expected, intended_rule_reached):
    return actual == expected and intended_rule_reached


def normalized(value, root):
    if isinstance(value, bytes):
        return {"sha256": p.sha(value), "utf8": value.decode("utf-8", errors="replace")}
    if isinstance(value, Path):
        return (
            str(value)
            .replace(str(root), "<fixture>")
            .replace(str(p.ROOT), "<checkout>")
        )
    if isinstance(value, dict):
        return {str(k): normalized(v, root) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [
            normalized(v, root)
            for v in (sorted(value) if isinstance(value, set) else value)
        ]
    if isinstance(value, str):
        return value.replace(str(root), "<fixture>").replace(str(p.ROOT), "<checkout>")
    return value


def protected_manifest(root):
    names = set(
        p.git(root, "ls-files", "--cached", "--others", "-z").decode().split("\0")
    )
    rows = []
    for name in sorted(
        n for n in names if n and p.prior.in_scope(n) and not p.prior.generated(n)
    ):
        path = root / name
        if path.is_symlink():
            row = {
                "path": name,
                "type": "symlink",
                "target": normalized(os.readlink(path), root),
            }
        elif path.is_file():
            row = {
                "path": name,
                "sha256": p.sha(path.read_bytes()),
                "mode": oct(path.stat().st_mode & 0o777),
            }
        else:
            row = {"path": name, "type": "missing"}
        rows.append(row)
    return rows


class ProbeSuite:
    def __init__(self):
        self.root = p.ROOT
        self.rows, self.objects, self.trace, self.mutations = [], {}, [], []
        self.run_id = "p9-pressure-" + uuid.uuid4().hex
        self.input_policy, self.input_tree = p.current_boundary(p.ROOT)
        self.current_case = None

    def keep(self, value):
        value = normalized(value, self.root)
        digest = p.sha(p.canonical(value))
        self.objects[digest] = value
        return digest

    def mutation(self, name, before, after):
        self.mutations.append(
            {"target": name, "before": self.keep(before), "after": self.keep(after)}
        )

    @contextmanager
    def trace_checks(self):
        originals = {}
        names = [
            "current_boundary",
            "validate_policy",
            "validate_tree",
            "predecessor",
            "runtime_targets",
            "validate_runtime_change",
            "validate_composition",
            "completion_gate",
        ]
        for name in names:
            original = getattr(p, name)
            originals[name] = original

            def wrapper(*args, _name=name, _original=original, **kwargs):
                outer = not getattr(self, "depth", 0)
                self.depth = getattr(self, "depth", 0) + 1
                before = self.keep(protected_manifest(self.root)) if outer else None
                event = {
                    "check": _name,
                    "arguments": self.keep({"args": args, "kwargs": kwargs}),
                }
                self.trace.append(event)
                try:
                    result = _original(*args, **kwargs)
                    event["disposition"] = "returned"
                    if _name == "completion_gate":
                        event["candidate_decision"] = (
                            "held" if result["held"] else "admitted"
                        )
                    return result
                except Exception as error:
                    event.update(
                        disposition="raised",
                        reason=normalized(str(error), self.root),
                        exception=type(error).__name__,
                    )
                    raise
                finally:
                    self.depth -= 1
                    if outer:
                        after = self.keep(protected_manifest(self.root))
                        event["protected_state"] = {
                            "before": before,
                            "after": after,
                            "unchanged": before == after,
                        }

            setattr(p, name, wraps(original)(wrapper))
        try:
            yield
        finally:
            for name, original in originals.items():
                setattr(p, name, original)

    def case(
        self,
        name,
        pressure,
        operation,
        *,
        reject=False,
        scope="isolated_planning_boundary",
        rule=None,
        decision=None,
        batch=None,
    ):
        global ACTIVE
        ACTIVE = self
        self.current_case, self.trace, self.mutations = name, [], []
        before = self.keep(protected_manifest(self.root))
        git_state = self.keep(
            {
                "head": p.git(self.root, "rev-parse", "HEAD").decode().strip(),
                "status": p.git(
                    self.root, "status", "--porcelain", "--untracked-files=all"
                ).decode(),
                "index_diff": p.git(self.root, "diff", "--cached", "--raw").decode(),
                "worktree_diff": p.git(self.root, "diff", "--raw").decode(),
            }
        )
        expected = decision or (
            "rejected"
            if reject
            else (
                "held"
                if "without_own_evidence_held" in name
                or "completion_off_missing_" in name
                else "admitted"
            )
        )
        rule = rule or next(
            (
                v
                for k, v in sorted(RULES.items(), key=lambda pair: -len(pair[0]))
                if name.startswith(k)
            ),
            None,
        )
        actual, reason, frames = "admitted", "required checks returned normally", []
        try:
            with self.trace_checks():
                returned = operation()
                if isinstance(returned, dict) and "candidate_decision" in returned:
                    actual, reason = (
                        returned["candidate_decision"],
                        returned.get("reason", reason),
                    )
                elif any(e.get("candidate_decision") == "held" for e in self.trace):
                    actual, reason = (
                        "held",
                        "required scoped completion evidence absent",
                    )
        except (ValueError, KeyError, TypeError) as error:
            actual, reason = "rejected", normalized(str(error), self.root)
            frames = [
                {
                    "file": normalized(f.filename, self.root),
                    "function": f.name,
                    "line": f.lineno,
                }
                for f in traceback.extract_tb(error.__traceback__)
            ]
        except Exception as error:
            actual, reason = (
                "unverifiable",
                normalized(f"{type(error).__name__}: {error}", self.root),
            )
        after = self.keep(protected_manifest(self.root))
        reached = (rule in reason) if rule else not reject
        passed = (
            assertion_matches(actual, expected, reached)
            and before == after
            and all(
                e.get("protected_state", {}).get("unchanged", True) for e in self.trace
            )
        )
        self.rows.append(
            {
                "case_id": name,
                "review_pressure": f"P9-REVIEW-PRESSURE-8.{pressure}",
                "batch": batch
                or (
                    "baseline_permission"
                    if pressure in {1, 2}
                    else "integrity_authority_semantics"
                ),
                "expected_decision": expected,
                "candidate_decision": actual,
                "assertion_result": "passed" if passed else "failed",
                "passed": passed,
                "decisive_rule": rule or "positive/held scoped assertion",
                "actual_reason": reason,
                "intended_check_reached": reached,
                "scope": scope,
                "evidence_kind": "isolated_governance_probe_not_runtime_execution",
                "project_effect": {
                    "runtime_authorized": False,
                    "P9_G1_accepted": False,
                    "scientific_promotion": False,
                },
                "run_id": self.run_id,
                "base_fixture_identity": before,
                "git_input_identity": git_state,
                "mutations": self.mutations,
                "trace": self.trace,
                "exception_trace": frames,
                "protected_pre_post": {
                    "before": before,
                    "after": after,
                    "unchanged": before == after,
                },
                "authority": {
                    "release_id": p.prior.RELEASE_ID,
                    "policy_digest": self.input_policy["record_digest"],
                    "historical_revision": p.prior.HISTORICAL,
                    "current_input_tree": self.input_tree,
                },
                "verifier_identity": {
                    n: p.sha((p.ROOT / n).read_bytes())
                    for n in [
                        p.HERE + "phase9_policy.py",
                        p.HERE + "audit_phase9_successor.py",
                        p.SCRIPTS + "active_phase.py",
                        p.SCRIPTS + "run.py",
                    ]
                },
                "command": [".venv/bin/python", p.HERE + "test_phase9_pressure.py"],
                "execution_mode": "in_process_callable_unless_trace_records_subprocess",
                "exit_code": None,
                "review_disposition": "pending_user_review",
                "limitation": "Bounded Linux fixture and declared trust root; not a universal security or runtime conformance proof.",
            }
        )
        ACTIVE = None

    def command(self, command, *, cwd=None):
        import subprocess

        result = subprocess.run(
            command, cwd=cwd or self.root, capture_output=True, text=True, timeout=120
        )
        self.trace.append(
            {
                "check": "actual_subprocess",
                "command": normalized(command, self.root),
                "cwd": normalized(cwd or self.root, self.root),
                "exit_code": result.returncode,
                "stdout": normalized(result.stdout, self.root),
                "stderr": normalized(result.stderr, self.root),
            }
        )
        return result

    def finish(self):
        batches = [
            {
                "batch_id": b,
                "case_ids": [r["case_id"] for r in self.rows if r["batch"] == b],
                "passed": all(r["passed"] for r in self.rows if r["batch"] == b),
            }
            for b in [
                "baseline_permission",
                "integrity_authority_semantics",
                "staleness_route_fault_sensitivity",
            ]
        ]
        p.require(
            all(b["case_ids"] for b in batches), "missing independently retained batch"
        )
        report = {
            "schema": "phase9_successor_pressure_results_v2",
            "run_id": self.run_id,
            "status": "passed" if all(r["passed"] for r in self.rows) else "failed",
            "case_count": len(self.rows),
            "passed_count": sum(r["passed"] for r in self.rows),
            "review_pressures": p.PRESSURES,
            "runtime_authorized": False,
            "P9_G1_accepted": False,
            "policy_digest": self.input_policy["record_digest"],
            "tree": self.input_tree,
            "cases": self.rows,
            "objects": self.objects,
            "batches": batches,
        }
        report["report_digest"] = p.digest_record(report, "report_digest")
        return report


def summary(report):
    """Stable retained coverage index; actual run identities stay in raw evidence.

    This avoids a policy->result->policy hash cycle without stripping raw traces.
    The verifier compares this index AND validates the raw run's exact inputs.
    """
    return {
        "schema": "phase9_pressure_coverage_index_v2",
        "status": report["status"],
        "case_count": report["case_count"],
        "passed_count": report["passed_count"],
        "review_pressures": report["review_pressures"],
        "runtime_authorized": False,
        "P9_G1_accepted": False,
        "batches": report["batches"],
        "cases": [
            {
                k: row[k]
                for k in [
                    "case_id",
                    "review_pressure",
                    "batch",
                    "expected_decision",
                    "candidate_decision",
                    "assertion_result",
                    "passed",
                    "decisive_rule",
                    "intended_check_reached",
                    "scope",
                    "project_effect",
                    "limitation",
                ]
            }
            for row in report["cases"]
        ],
        "raw_evidence": p.SIDE
        + "tool/generated/phase9-verification/pressure-results.json",
    }
