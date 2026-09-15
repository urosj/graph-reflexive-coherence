"""P9-7.2a scoped execution and read-only evidence checks; C-to-A stays pending."""

from __future__ import annotations

import argparse
from copy import deepcopy
from functools import lru_cache
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import unittest

import phase9_implementation_policy as p
import verify_p971_lifecycle as lifecycle

BASE = "5d8dbe2"
SCRIPT = p.HERE + "verify_p972a_migrations.py"
RECORD = p.PHASE + "tranche-7/P9-7.2a-Migrations.json"
FOLLOWUP = p.PHASE + "tranche-7/P9-7.2a-AuditFollowup.json"
ORIGINAL = p.PHASE + "tranche-7/P9-7.2a-OriginalSources.json"
PRESSURE = p.PHASE + "tranche-7/P9-7.2a-AuditPressure.json"
CORRECTED = {SCRIPT, "src/pygrc/models/grc_v4_lifecycle.py", "tests/models/test_grc_v4_migration.py"}
MODULE = "tests.models.test_grc_v4_migration"
LEGACY = [lifecycle.LEGACY[0], lifecycle.LEGACY[3], lifecycle.LEGACY[-1]]


def bindings():
    names = {n for n in p.git(p.ROOT, "ls-files", "src", "tests", p.SIDE + "tool/src").decode().splitlines()
             if n.endswith(".py")}
    names |= p.MIGRATION_PATHS | {SCRIPT, lifecycle.SCRIPT, "pyproject.toml", "uv.lock",
        "specs/grc-v4-spec.md", "specs/grc-common-interface-v4-ext.md",
        p.INV + "drafts/2026-09-GRC-V4.md", p.PHASE + "tranche-5/P9-5.4-Review.md",
        p.PHASE + "tranche-7/P9-7.1-Review.md"}
    return {name: p.sha((p.ROOT / name).read_bytes()) for name in sorted(names)}


@lru_cache(maxsize=1)
def authority():
    sys.path.insert(0, str(p.ROOT / p.SIDE / "tool/src"))
    from grcv4_explorer.abundance import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT / p.SIDE)
    return {name: contract_provenance(context, name) for name in (
        "D10.2-EC-PARENT-L-PROFILE-MIGRATION", "D10.2-EC-PARENT-L-A-INITIALIZER-GRC",
        "D10.2-EC-PARENT-L-SNAPSHOT-RESET", "D10.2-EC-PARENT-L-ATOMICITY",
        "P9-EC-RECEIPT-PARENT-CHAIN", "P9-EC-RECEIPT-PARENT-CEILING")}


def predecessors():
    """Read retained 7.1 evidence at its accepted subject; no historical rerun."""
    names = p.git(p.ROOT, "ls-tree", "-r", "--name-only", BASE, "src", "tests",
                  p.PHASE + "tranche-5", p.PHASE + "tranche-6", p.G2_ACCEPTANCE,
                  p.PHASE + "tranche-7").decode().splitlines()
    kept = 0
    for name in names:
        if name not in p.MIGRATION_PATHS:
            p.require((p.ROOT / name).read_bytes() == p.git(p.ROOT, "show", BASE + ":" + name),
                      "unrelated accepted-source/evidence change: " + name)
            kept += 1
    followup = p.read(p.ROOT / lifecycle.FOLLOWUP)
    p.require(followup["record_digest"] == p.digest_record(followup), "historical 7.1 digest changed")
    # Metadata/runtime files may evolve here, but the old execution inputs
    # remain recoverable in Git; do not replace their recorded hashes.
    for name, digest in followup["source_bindings"].items():
        p.require(p.sha(p.git(p.ROOT, "show", BASE + ":" + name)) == digest,
                  "accepted 7.1 source binding mismatch: " + name)
    return dict(base_commit=p.git(p.ROOT, "rev-parse", BASE).decode().strip(),
                preserved_files=kept, lifecycle_record_digest=followup["record_digest"])


def roster():
    from tests.models.test_grc_v4_migration import MigrationTests
    return sorted([MODULE + ".MigrationTests." + name for name in
                   unittest.TestLoader().getTestCaseNames(MigrationTests)] + LEGACY,
                  key=lambda name: (".test_positive_" in name, name))


def validate(value, sources):
    from tests.models.test_grc_v4_migration import CASES, fixture
    from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
    p.require(value["record_digest"] == p.digest_record(value), "migration record digest mismatch")
    p.require(value["iteration_id"] == "P9-7.2a" and value["user_accepted"] is False
              and value["status"] == "scoped_verified_aggregate_pending"
              and value["aggregate_closed"] is False and value["new_G2_support"] == []
              and value["G3_accepted"] is False, "partial migration evidence cannot close the parent or grant support")
    p.require(value["pending_positive_classes"] == ["C_to_A_initializer_source"], "initializer obligation erased")
    p.require(p.g2_bindings_match(value["source_bindings"], sources), "migration source drift")
    p.require(value["authority"] == authority() and value["release_id"] == p.current_abundance_release(p.ROOT),
              "migration authority drift")
    p.require(value["test_ids"] == roster() and value["results"] == dict(tests_run=len(roster()), failures=[], errors=[], skips=[]),
              "incomplete scoped migration execution")
    before, after = value["loaded_sources_before"], value["loaded_sources_after"]
    p.require(before and after and all(after.get(k) == row for k, row in before.items()), "loaded source changed")
    p.require(all(sources.get(row["path"]) == row["sha256"] for row in after.values()), "unbound loaded source")
    p.require(set(value["cases"]) == set(CASES) == set(p.MIGRATION_CASES), "missing migration pair")
    for case, (source, target) in CASES.items():
        row = value["cases"][case]
        inputs, backend = fixture(source)
        ref = fixture(target)[0].geometry.reference
        p.require(row["source_family"] == source and row["target_family"] == target
                  and canonical_json_bytes(row["initial"]) == canonical_json_bytes(inputs.to_payload())
                  and canonical_json_bytes(row["target_reference"]) == canonical_json_bytes(ref.to_payload())
                  and row["differential_reference"] == (None if backend is None else backend.to_payload())
                  and row["accepted_G2"] is False, "wrong migration fixture/authority")
        old, new = row["before"]["scientific_state"], row["after"]["scientific_state"]
        p.require(all(new[key] == old[key] for key in ("time", "step_index", "Q_target", "graph_digest"))
                  and new["authoritative"]["C"] == old["authoritative"]["C"]
                  and new["active_model_identity"] == ref.profile.complete_profile_id, "migration changed fixed state")
        for key in ("before", "after", "reset", "continuation"):
            endpoint = row[key]
            p.require(endpoint["scientific_state_digest"] == payload_identity("scientific_state_payload", endpoint["scientific_state"])
                      and endpoint["reset_digest"] == payload_identity("grcv4_reset_payload", endpoint["reset"]), "wrong endpoint identity")
        p.require(row["reset"]["scientific_state"]["authoritative"] == row["after"]["reset"]["authoritative"],
                  "reset failed to restore transformed baseline")
        p.require(len(row["receipts"]) == 4 and len(row["after"]["receipt_ids"]) == 8
                  and row["after"]["receipt_ids"][:4] == row["before"]["receipt_ids"], "missing migration receipt delta")


def original_sources():
    """Recover the uncommitted 25-test subject; never relabel its execution."""
    value, bridge = p.read(p.ROOT / RECORD), p.read(p.ROOT / ORIGINAL)
    p.require(bridge["original_record_digest"] == value["record_digest"]
              and bridge["original_record_sha256"] == p.sha((p.ROOT / RECORD).read_bytes()), "original migration evidence changed")
    p.require(set(bridge["prior_source_delta"]) == CORRECTED, "unexpected audit correction scope")
    sources = bindings()
    for name, entry in bridge["prior_source_delta"].items():
        p.require(sources[name] == entry["current_sha256"], "unrecorded correction source drift")
        lines = (p.ROOT / name).read_text().splitlines(keepends=True)
        end = len(lines)
        for span in reversed(entry["splices_to_original"]):
            start, stop = span["start"], span["stop"]
            p.require(0 <= start <= stop <= end, "invalid original-source span")
            lines[start:stop] = span["old_lines"]
            end = start
        sources[name] = p.sha("".join(lines).encode())
        p.require(sources[name] == entry["original_sha256"], "original source reconstruction failed")
    p.require(sources == value["source_bindings"], "original execution subject not recovered")
    return sources


def audit_sources():
    return {**bindings(), **{name: p.sha((p.ROOT / name).read_bytes()) for name in (ORIGINAL, PRESSURE)}}


def audit_roster():
    from tests.models.test_grc_v4_migration import P972aAuditRegressions
    names = [MODULE + ".P972aAuditRegressions." + name for name in
             unittest.TestLoader().getTestCaseNames(P972aAuditRegressions)]
    names += [MODULE + ".MigrationTests.test_" + name for name in (
        "C_to_A_initializer_is_unresolved_not_fabricated",
        "missing_target_differential_recipe_is_typed_and_atomic",
        "reset_only_target_failure_is_atomic",
        "core_state_migration_readmission_does_not_require_another_RG_beat",
        "positive_C_PC_CIPC",
    )]
    return sorted(names + [LEGACY[0]])


def validate_audit(value):
    p.require(value["record_digest"] == p.digest_record(value), "audit record digest mismatch")
    p.require(value["source_bindings"] == audit_sources(), "audit source drift")
    p.require(value["original_record_digest"] == p.read(p.ROOT / RECORD)["record_digest"], "wrong audit subject")
    p.require(value["authority"] == authority() and value["predecessor"] == predecessors(), "audit authority/predecessor drift")
    p.require(value["test_ids"] == audit_roster()
              and value["results"] == dict(tests_run=len(audit_roster()), failures=[], errors=[], skips=[]), "missing native audit pressure")
    p.require(value["findings_closed"] == ["F1", "F2"] and value["aggregate_closed"] is False
              and value["user_accepted"] is False and value["new_G2_support"] == []
              and value["G3_accepted"] is False
              and value["pending_positive_classes"] == ["C_to_A_initializer_source"], "audit cannot waive the initializer or promote support")
    before, after = value["loaded_sources_before"], value["loaded_sources_after"]
    p.require(before and after and all(after.get(k) == row for k, row in before.items())
              and all(value["source_bindings"].get(row["path"]) == row["sha256"] for row in after.values()), "audit loaded-source drift")
    native = value["native_evidence"]
    p.require(set(native) == {"A_PC_archived_contradiction", "C_OS_archived_contradiction",
                             "lawful_assignment", "distinct_backend", "unknown_history_ceiling"}, "missing native outcome")
    for key in ("A_PC_archived_contradiction", "C_OS_archived_contradiction"):
        row = native[key]
        p.require(row["original"]["scientific_state"] == row["mutated"]["scientific_state"]
                  and row["original"]["receipt_ids"] != row["mutated"]["receipt_ids"]
                  and row["false_authority"] != row["known_authority"] and row["rejected"] is True,
                  "audit counterexample lost its contradiction or changed numeric state")
    p.require(native["distinct_backend"]["original"] != native["distinct_backend"]["target"], "backend switch not exercised")
    p.require(native["unknown_history_ceiling"]["inconsistent_rejected"] is True
              and native["unknown_history_ceiling"]["external_execution_authenticated"] is False, "historical trust ceiling changed")


def check():
    # The accepted producer source now has a current authority successor.
    # Preserve this checker's original 25/17-test source at its Git subject;
    # never relabel those executions against the new forensic context.
    from verify_p972a_initializer_authority import check as current_check
    return current_check()


def historical_check():
    value = p.read(p.ROOT / RECORD)
    sources = original_sources()
    validate(value, sources)
    followup = p.read(p.ROOT / FOLLOWUP)
    validate_audit(followup)
    p.require(value["predecessor"] == predecessors(), "predecessor mismatch")
    p.current_boundary(p.ROOT)
    rejected = []
    for name, mutation in (
        ("missing_pair", lambda v: v["cases"].pop("A_C_PC")),
        ("waived_initializer", lambda v: v.update(pending_positive_classes=[])),
        ("closed_parent", lambda v: v.update(aggregate_closed=True)),
        ("promoted_G2", lambda v: v.update(new_G2_support=["A_PC"])),
        ("missing_pressure", lambda v: v["test_ids"].pop()),
    ):
        bad = deepcopy(value)
        mutation(bad)
        bad["record_digest"] = p.digest_record(bad)
        try:
            validate(bad, sources)
        except (ValueError, TypeError, KeyError):
            rejected.append(name)
        else:
            raise ValueError("accepted misleading migration evidence: " + name)
    for name, mutation in (
        ("missing_native_regression", lambda v: v["test_ids"].pop()),
        ("missing_known_state_outcome", lambda v: v["native_evidence"].pop("C_OS_archived_contradiction")),
        ("audit_waived_initializer", lambda v: v.update(pending_positive_classes=[])),
    ):
        bad = deepcopy(followup)
        mutation(bad)
        bad["record_digest"] = p.digest_record(bad)
        try:
            validate_audit(bad)
        except (ValueError, TypeError, KeyError):
            rejected.append(name)
        else:
            raise ValueError("accepted misleading native audit evidence: " + name)
    return dict(status="passed", original_tests=len(roster()), audit_tests=len(audit_roster()), positive_pairs=13, numerical_tests_rerun=0,
                rejected_controls=rejected, pending_positive_classes=value["pending_positive_classes"],
                aggregate_closed=False, user_accepted=False, new_G2_support=[])


def run(output):
    from tests.models.test_grc_v4_migration import EVIDENCE
    path = Path(output)
    p.require(not path.is_absolute() and ".." not in path.parts and path.suffix == ".json", "output must be repository-relative JSON")
    path = p.ROOT / path
    p.require(path.resolve().is_relative_to(p.ROOT.resolve()) and not path.exists(), "output exists or escapes repository")
    sources = bindings()
    prior = predecessors()
    authority()
    EVIDENCE.clear()
    tests = roster()
    suite = unittest.TestLoader().loadTestsFromNames(tests)
    before = lifecycle.loaded_sources(sources)
    result = unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
    p.require(result.wasSuccessful() and not result.skipped and result.testsRun == len(tests), "scoped migration execution failed")
    after = lifecycle.loaded_sources(sources)
    p.require(bindings() == sources, "sources changed during capture")
    value = dict(schema="phase9_generic_migration_v1", iteration_id="P9-7.2a",
                 status="scoped_verified_aggregate_pending", user_accepted=False,
                 aggregate_closed=False, pending_positive_classes=["C_to_A_initializer_source"],
                 release_id=p.current_abundance_release(p.ROOT), predecessor=prior,
                 source_bindings=sources, authority=authority(), cases=EVIDENCE,
                 python_version=platform.python_version(),
                 dependency_versions={name: importlib.metadata.version(name) for name in ("numpy", "jsonschema", "rfc8785")},
                 loaded_sources_before=before, loaded_sources_after=after, test_ids=tests,
                 results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]),
                 new_G2_support=[], G3_accepted=False,
                 reconstruction="PYTHONPATH=src:. .venv/bin/python " + SCRIPT + " --run --output <new-repository-relative-json-path>")
    value["record_digest"] = p.digest_record(value)
    validate(value, sources)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
    return dict(status="passed", tests=result.testsRun, output=output, aggregate_closed=False)


def audit_run(output):
    from tests.models.test_grc_v4_migration import AUDIT_EVIDENCE
    validate(p.read(p.ROOT / RECORD), original_sources())
    path = Path(output)
    p.require(not path.is_absolute() and ".." not in path.parts and path.suffix == ".json", "output must be repository-relative JSON")
    path = p.ROOT / path
    p.require(path.resolve().is_relative_to(p.ROOT.resolve()) and not path.exists(), "output exists or escapes repository")
    sources = audit_sources()
    AUDIT_EVIDENCE.clear()
    tests = audit_roster()
    suite = unittest.TestLoader().loadTestsFromNames(tests)
    before = lifecycle.loaded_sources(sources)
    result = unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
    p.require(result.wasSuccessful() and not result.skipped and result.testsRun == len(tests), "native audit execution failed")
    after = lifecycle.loaded_sources(sources)
    p.require(audit_sources() == sources, "audit sources changed during capture")
    value = dict(schema="phase9_migration_audit_followup_v1", iteration_id="P9-7.2a",
                 original_record_digest=p.read(p.ROOT / RECORD)["record_digest"],
                 source_bindings=sources, authority=authority(), predecessor=predecessors(),
                 loaded_sources_before=before, loaded_sources_after=after, test_ids=tests,
                 results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]),
                 native_evidence=AUDIT_EVIDENCE, findings_closed=["F1", "F2"],
                 python_version=platform.python_version(),
                 dependency_versions={name: importlib.metadata.version(name) for name in ("numpy", "jsonschema", "rfc8785")},
                 aggregate_closed=False, user_accepted=False, new_G2_support=[], G3_accepted=False,
                 pending_positive_classes=["C_to_A_initializer_source"],
                 reproduction="PYTHONPATH=src:. .venv/bin/python " + SCRIPT + " --audit-run --output <new-repository-relative-json-path>")
    value["record_digest"] = p.digest_record(value)
    validate_audit(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
    return dict(status="passed", tests=result.testsRun, output=output, aggregate_closed=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--audit-run", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    if (args.run or args.audit_run) and not args.output:
        parser.error("execution requires a new relative --output")
    print(json.dumps(audit_run(args.output) if args.audit_run else run(args.output) if args.run else check()))
