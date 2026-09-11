"""Focused P9-7.1 evidence: --run captures; --check inspects without a rerun."""

from __future__ import annotations

import argparse
from copy import deepcopy
from functools import lru_cache
import json
import platform
from pathlib import Path
import importlib.metadata
import sys
import unittest

import phase9_implementation_policy as p

BASE = "b45d0af"
RECORD = p.PHASE + "tranche-7/P9-7.1-Lifecycle.json"
SCRIPT = p.HERE + "verify_p971_lifecycle.py"
FOLLOWUP = p.PHASE + "tranche-7/P9-7.1-AuditFollowup.json"
ORIGINAL = p.PHASE + "tranche-7/P9-7.1-OriginalSources.json"
PRESSURE = p.PHASE + "tranche-7/P9-7.1-AuditPressure.json"
CORRECTED = {SCRIPT, "src/pygrc/models/grc_v4_lifecycle.py",
             "tests/models/test_grc_v4_generic_lifecycle.py"}
TEST = "tests.models.test_grc_v4_generic_lifecycle"
LEGACY = [
    "tests.models.test_grc_v4_lifecycle.CandidateCOSOperationTests.test_exact_dyadic_receipts_commit_and_whole_state_identity",
    "tests.models.test_grc_v4_lifecycle.CandidateCOSOperationTests.test_native_reference_only_poststate_singularity_rejects_after_valid_consumed_final",
    "tests.models.test_grc_v4_lifecycle.CandidateCOSOperationTests.test_native_postsolve_resource_domain_overflow_and_charge_failures",
    "tests.models.test_grc_v4_lifecycle.CandidateCOSLifecycleTests.test_dyadic_snapshot_embeds_exact_preimages_and_acyclic_identities",
    "tests.models.test_grc_v4_lifecycle.CandidateCOSLifecycleTests.test_canonical_save_load_rejects_duplicate_keys_nonfinite_and_negative_zero",
    "tests.models.test_grc_v4.PublicFacadeTests.test_save_load_defaults_and_actual_crossings",
]


@lru_cache(maxsize=1)
def authority():
    """Typed forensic provenance retains claim class/support/source boundaries."""
    sys.path.insert(0, str(p.ROOT / p.SIDE / "tool/src"))
    from grcv4_explorer.abundance import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT / p.SIDE)
    return {key: contract_provenance(context, key) for key in (
        "D10.2-EC-PARENT-L-ATOMICITY", "D10.2-EC-PARENT-L-SNAPSHOT-RESET",
        "D10.2-EC-PARENT-L-ORDERED-RECEIPTS", "P9-EC-RECEIPT-PARENT-CHAIN",
        "P9-EC-RECEIPT-PARENT-ADMISSION", "P9-EC-RECEIPT-PARENT-CEILING",
    )}


def bindings():
    """Bind the runtime and its oracle/fixture inputs, not ambient machine paths."""
    names = {row["path"] for row in p.read(p.ROOT / p.WORK)["entries"]
             if row["path"].startswith(("src/", "tests/"))}
    names |= p.LIFECYCLE_PATHS | {SCRIPT, "pyproject.toml", "uv.lock",
        "specs/grc-v4-spec.md", "specs/grc-common-interface-v4-ext.md",
        p.INV + "drafts/2026-09-GRC-V4.md",
        p.PHASE + "tranche-6/P9-6.5-RealizationRouting.json"}
    # Include import origins/fixtures already tracked in the repository, not
    # merely the three changed files. The existing source guard consumes these.
    names |= {name for name in p.git(p.ROOT, "ls-files", "src", "tests", p.SIDE + "tool/src").decode().splitlines()
              if name.endswith(".py")}
    return {name: p.sha((p.ROOT / name).read_bytes()) for name in sorted(names)}


def loaded_sources(sources):
    importlib.import_module("tests.models.test_grc_v4_transport")  # shared guard prerequisite
    from tests.models.test_grc_v4_candidate_c import _p941_loaded_sources
    modules = frozenset(name for name in sys.modules if name.startswith(("pygrc.models.grc_v4", "tests.models.test_grc_v4")))
    return _p941_loaded_sources(p.ROOT, sources, extra_modules=modules)


def unchanged_predecessors():
    """Preserve all numerical owners/oracles and accepted evidence at their Git subject."""
    names = p.git(p.ROOT, "ls-tree", "-r", "--name-only", BASE, "src", "tests",
                  p.PHASE + "tranche-5", p.PHASE + "tranche-6", p.G2_ACCEPTANCE).decode().splitlines()
    for name in names:
        if name not in p.LIFECYCLE_PATHS:
            p.require((p.ROOT / name).read_bytes() == p.git(p.ROOT, "show", BASE + ":" + name),
                      "unrelated predecessor change: " + name)
    return len(names) - len(p.LIFECYCLE_PATHS - {"tests/models/test_grc_v4_generic_lifecycle.py"})


def roster():
    return sorted([TEST + ".GenericLifecycleTests.test_" + family + "_" + kind
                   for family in p.LIFECYCLE_FAMILIES for kind in ("lifecycle", "pressure")] + LEGACY)


def audit_roster():
    from tests.models.test_grc_v4_generic_lifecycle import P971AuditRegressions
    return sorted([TEST + ".P971AuditRegressions." + name for name in
                   unittest.TestLoader().getTestCaseNames(P971AuditRegressions)] + LEGACY)


def audit_sources():
    return {**bindings(), **{name: p.sha((p.ROOT / name).read_bytes())
                            for name in (ORIGINAL, PRESSURE)}}


def original_sources():
    """Recover the exact uncommitted original subject, never relabel its run."""
    bridge = p.read(p.ROOT / ORIGINAL)
    value = p.read(p.ROOT / RECORD)
    p.require(bridge["original_record_sha256"] == p.sha((p.ROOT / RECORD).read_bytes())
              and bridge["original_record_digest"] == value["record_digest"], "original run changed")
    p.require(set(bridge["prior_source_delta"]) == CORRECTED, "changed correction scope")
    sources = bindings()
    for name, entry in bridge["prior_source_delta"].items():
        p.require(sources[name] == entry["current_sha256"], "unrecorded audit source drift")
        lines = (p.ROOT / name).read_text().splitlines(keepends=True)
        end = len(lines)
        for span in reversed(entry["splices_to_original"]):
            start, stop = span["start"], span["stop"]
            p.require(0 <= start <= stop <= end, "invalid historical source span")
            lines[start:stop] = span["old_lines"]
            end = start
        sources[name] = p.sha("".join(lines).encode())
    p.require(sources == value["source_bindings"], "original subject is not recoverable")
    return sources


def validate_audit(value):
    p.require(value["record_digest"] == p.digest_record(value), "audit digest mismatch")
    p.require(value["iteration_id"] == "P9-7.1" and value["user_accepted"] is False
              and value["status"] == "verified_pending_user_acceptance"
              and value["new_G2_support"] == [] and value["G3_accepted"] is False,
              "audit execution cannot grant acceptance/support")
    p.require(value["original_record_digest"] == p.read(p.ROOT / RECORD)["record_digest"]
              and value["source_bindings"] == audit_sources(), "audit source/subject drift")
    p.require(value["authority"] == authority()
              and value["release_id"] == p.current_abundance_release(p.ROOT), "audit authority drift")
    p.require(value["test_ids"] == audit_roster()
              and value["results"] == dict(tests_run=len(audit_roster()), failures=[], errors=[], skips=[]),
              "incomplete native audit coverage")
    before, after = value["loaded_sources_before"], value["loaded_sources_after"]
    p.require(before and after and all(after.get(k) == row for k, row in before.items()),
              "audit loaded sources changed")
    for row in after.values():
        p.require(value["source_bindings"].get(row["path"]) == row["sha256"], "unbound loaded audit source")
    evidence = value["observations"]
    for key in ("two_commits", "zero_clock_mutations"):
        p.require(set(evidence[key]) == set(p.LIFECYCLE_FAMILIES), "missing ten-family audit evidence")
    for key in ("RG2b_core_exit", "frozen_beat_mutations"):
        p.require(set(evidence[key]) == {"A", "C"}, "missing candidate audit evidence")
    for row in evidence["RG2b_core_exit"].values():
        from fractions import Fraction
        p.require(Fraction(row["inner"]) < Fraction(row["radius"]) < Fraction(row["core"]),
                  "not a core-only boundary witness")
    p.require(set(evidence["rounded_positive_clock"]) == {g + "_" + c for g in ("scalar", "graph") for c in ("A", "C")},
              "missing scalar/graph rounded-clock controls")
    rollback = evidence["A_native_rollback"]
    p.require(rollback["before"] == rollback["after"] and rollback["failure_stage"] == "final_reconstruction"
              and rollback["solver_disposition"] == "valid_root" and rollback["emitted_receipts"] == 1,
              "native A publication rollback not demonstrated")


def validate(value, sources):
    from tests.models.test_grc_v4_generic_lifecycle import fixture, RECIPES
    from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
    p.require(value["record_digest"] == p.digest_record(value), "record digest mismatch")
    p.require(value["iteration_id"] == "P9-7.1" and value["status"] == "verified_pending_user_acceptance"
              and value["user_accepted"] is False and value["new_G2_support"] == []
              and value["G3_accepted"] is False, "lifecycle evidence cannot grant acceptance/support")
    p.require(value["source_bindings"] == sources, "focused source drift")
    p.require(value["authority"] == authority(), "forensic authority drift")
    p.require(value["release_id"] == p.current_abundance_release(p.ROOT), "release mismatch")
    p.require(value["base_commit"] == p.git(p.ROOT, "rev-parse", BASE).decode().strip(), "wrong predecessor")
    p.require(value["test_ids"] == roster() and value["results"] == dict(tests_run=26, failures=[], errors=[], skips=[]),
              "incomplete lifecycle campaign")
    p.require(value["loaded_sources_before"] and value["loaded_sources_after"]
              and all(value["loaded_sources_after"].get(k) == row for k, row in value["loaded_sources_before"].items()),
              "loaded source attribution changed")
    p.require(set(value["families"]) == set(p.LIFECYCLE_FAMILIES), "missing or extra profile family")
    for family, row in value["families"].items():
        inputs, backend = fixture(family)
        p.require(row["recipe"] == RECIPES[family]
                  and canonical_json_bytes(row["initial"]) == canonical_json_bytes(inputs.to_payload())
                  and row["differential_reference"] == (None if backend is None else backend.to_payload())
                  and row["initialization"] == "explicit_supplied_authority_not_formation"
                  and row["complete_profile_id"] == inputs.geometry.reference.profile.complete_profile_id,
                  "wrong input/profile/backend scope: " + family)
        for key, count in (("first", 1), ("replay", 2), ("reset", 3), ("rebase_then_reset", 4)):
            endpoint = row[key]
            state = endpoint["scientific_state"]
            p.require(len(endpoint["receipt_ids"]) == 4 * count
                      and len(set(endpoint["receipt_ids"])) == 4 * count
                      and len(endpoint["commit_ids"]) == count,
                      "incomplete operation/receipt sequence")
            for field in ("active_model_identity", "graph_digest", "orientation_identity", "Q_target",
                          "context_contract_id", "context_value_digest"):
                p.require(state[field] == inputs.scientific_state_preimage[field],
                          "lifecycle output changed fixed authority")
            p.require(endpoint["scientific_state_digest"] == payload_identity("scientific_state_payload", endpoint["scientific_state"])
                      and endpoint["reset_digest"] == payload_identity("grcv4_reset_payload", endpoint["reset"])
                      and endpoint["lifecycle_digest"] == payload_identity("lifecycle_envelope_payload", dict(
                          schema_version="grcv4-lifecycle-envelope-v1",
                          scientific_state_digest=endpoint["scientific_state_digest"], receipt_ids=endpoint["receipt_ids"])),
                      "endpoint identity mismatch")
        for key in ("reset", "rebase_then_reset"):
            p.require(all(row[key]["scientific_state"][field] == row["replay"]["scientific_state"][field]
                          for field in ("time", "step_index")), "administrative operation rewound clock")
        p.require(row["reset"]["scientific_state"]["authoritative"] == inputs.reset_preimage["authoritative"],
                  "reset did not restore the distinct baseline")
        p.require(row["rebase_then_reset"]["scientific_state"]["authoritative"] == row["replay"]["scientific_state"]["authoritative"],
                  "rebase/reset did not preserve the rebased live authority")


def check():
    value = p.read(p.ROOT / RECORD)
    sources = original_sources()
    validate(value, sources)
    followup = p.read(p.ROOT / FOLLOWUP)
    validate_audit(followup)
    preserved = unchanged_predecessors()
    p.current_boundary(p.ROOT)
    # Coherently rehashed misleading records must still be rejected.
    controls = []
    for label, mutation in (
        ("missing_family", lambda v: v["families"].pop("C_PC")),
        ("acceptance", lambda v: v.update(user_accepted=True)),
        ("support", lambda v: v.update(new_G2_support=["A_OS"])),
        ("missing_pressure", lambda v: v["test_ids"].pop()),
        ("borrowed_profile", lambda v: v["families"]["A_CI"].update(complete_profile_id=v["families"]["C_CI"]["complete_profile_id"])),
    ):
        bad = deepcopy(value)
        mutation(bad)
        bad["record_digest"] = p.digest_record(bad)
        try:
            validate(bad, sources)
        except (ValueError, KeyError, TypeError):
            controls.append(label)
        else:
            raise ValueError("accepted misleading lifecycle evidence: " + label)
    for label, mutation in (
        ("audit_missing_test", lambda v: v["test_ids"].pop()),
        ("audit_acceptance", lambda v: v.update(user_accepted=True)),
        ("audit_missing_boundary", lambda v: v["observations"]["RG2b_core_exit"].pop("A")),
    ):
        bad = deepcopy(followup)
        mutation(bad)
        bad["record_digest"] = p.digest_record(bad)
        try:
            validate_audit(bad)
        except (ValueError, KeyError, TypeError):
            controls.append(label)
        else:
            raise ValueError("accepted misleading audit evidence: " + label)
    return dict(status="passed", numerical_tests_rerun=0, original_scoped_tests=26,
                audit_scoped_tests=len(audit_roster()),
                families=10, preserved_predecessor_files=preserved, rejected_controls=controls,
                new_G2_support=[], user_accepted=False)


def run(output, *, audit=False):
    """A rerun is explicitly new evidence; never overwrite a retained record."""
    from tests.models.test_grc_v4_generic_lifecycle import EVIDENCE, AUDIT_EVIDENCE
    relative = Path(output)
    p.require(not relative.is_absolute() and ".." not in relative.parts
              and relative.suffix == ".json", "output must be a repository-relative JSON path")
    path = p.ROOT / relative
    p.require(path.resolve().is_relative_to(p.ROOT.resolve()), "output escapes repository")
    p.require(not path.exists(), "output already exists; choose a new repository-relative record")
    EVIDENCE.clear()
    AUDIT_EVIDENCE.clear()
    source_reader = audit_sources if audit else bindings
    before = source_reader()
    if audit:
        validate(p.read(p.ROOT / RECORD), original_sources())
    authority()  # Resolve required provenance before any numerical execution.
    unchanged_predecessors()
    tests = audit_roster() if audit else roster()
    suite = unittest.TestLoader().loadTestsFromNames(tests)
    loaded_before = loaded_sources(before)
    result = unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
    p.require(result.wasSuccessful() and not result.skipped and result.testsRun == len(tests), "focused execution failed")
    p.require(source_reader() == before, "source changed during execution")
    loaded_after = loaded_sources(before)
    record = dict(schema="phase9_generic_lifecycle_v1", iteration_id="P9-7.1",
        status="verified_pending_user_acceptance", user_accepted=False,
        base_commit=p.git(p.ROOT, "rev-parse", BASE).decode().strip(),
        release_id=p.current_abundance_release(p.ROOT), source_bindings=before,
        python_version=platform.python_version(), test_ids=tests,
        dependency_versions={name: importlib.metadata.version(name) for name in ("numpy", "jsonschema", "rfc8785")},
        loaded_sources_before=loaded_before, loaded_sources_after=loaded_after,
        results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]),
        families=EVIDENCE, authority=authority(), new_G2_support=[], G3_accepted=False,
        scope="ordinary lifecycle only; exact fixtures, not all-parameter/graph conformance",
        reconstruction="PYTHONPATH=src:. .venv/bin/python " + SCRIPT + " --run --output <new-repository-relative-json-path>")
    if audit:
        record.update(schema="phase9_generic_lifecycle_audit_v1",
                      original_record_digest=p.read(p.ROOT / RECORD)["record_digest"],
                      observations=AUDIT_EVIDENCE)
        record.pop("families")
        record["reconstruction"] = record["reconstruction"].replace(" --run ", " --audit-run ")
    record["record_digest"] = p.digest_record(record)
    if audit:
        validate_audit(record)
    else:
        validate(record, before)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n")
    return dict(status="passed", output=output, tests=result.testsRun)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--audit-run", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    if (args.run or args.audit_run) and not args.output:
        parser.error("capture requires a new repository-relative --output")
    print(json.dumps(run(args.output, audit=args.audit_run) if args.run or args.audit_run else check()))
