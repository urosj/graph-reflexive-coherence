"""Bounded initializer execution or read-only validation of its retained result."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p

RECORD = p.PHASE + "tranche-7/P9-7.2a-InitializerRuntime.json"
SCRIPT = p.HERE + "verify_p972a_initializer_runtime.py"
TEST = "tests.models.test_grc_v4_initializer"
ACCEPTED_COMMIT = "1afbc02aa4282a1575aef491700312cc1774dae7"
ACCEPTED_RECORD_DIGEST = "446e37a1764f8863f973ad5443ccde3c68d4eecdc07242e3d7c1f64f82f8be61"
CODEC = "src/pygrc/models/grc_v4_codec.py"
CODEC_REFERENCE_FIX_SHA256 = "59b0d373f6ed682ef079d7e150ee3a108dc0b1d53a960a81d11109f87aaeab5f"
EVENT_PACKAGE_CODEC = "src/pygrc/models/grc_v4_event_codec.py"
EVENT_PACKAGE_CODEC_SHA256 = "6955698da860261a145a2b825ce217de010c814b579e076fabf324262a277f04"
STATUS_API = p.SIDE + "tool/src/grcv4_explorer/phase9_verification.py"
ACCEPTANCE_STATUS_SHA256 = "9ae0aca90df9b8deaa8fa2cbe1d039cce4c5192f95d57ca783bdb0ded196b7e5"
ACCEPTANCE_REVIEW = p.PHASE + "tranche-7/P9-7.2a-InitializerRuntimeReview.md"
ACCEPTANCE_SHA256 = "a64bfe5e90e331495b7351d0b010c73b1de01f44332232b6b4d7b23046d23191"
MIGRATION_CLASSES = ["nonhistory_to_nonhistory", "nonhistory_to_persistent",
                     "persistent_to_nonhistory", "PC_to_CI_PC", "CI_PC_to_PC",
                     "A_to_C", "C_to_A"]
LEGACY = ["tests.models.test_grc_v4_migration." + name for name in (
    "MigrationTests.test_positive_A_PC_CIPC",
    "MigrationTests.test_positive_A_C_NH",
    "MigrationTests.test_C_to_A_initializer_is_unresolved_not_fabricated",
    "P972aAuditRegressions.test_programmer_mapper_exceptions_propagate_without_failure_result",
    "P972aAuditRegressions.test_archived_preimage_contradiction_rejects_after_complete_rehash",
    "P972aAuditRegressions.test_repeated_unknown_state_claims_are_consistent_without_adjacency",
    "P972aAuditRegressions.test_prospective_ledger_rejects_known_state_contradiction_atomically",
)]


def bindings():
    names = {n for n in p.git(p.ROOT, "ls-files", "src", "tests", p.SIDE + "tool/src").decode().splitlines() if n.endswith('.py')}
    names |= p.INITIALIZER_RUNTIME_PATHS | p.EVENT_NEW_PATHS | {SCRIPT, EVENT_PACKAGE_CODEC, p.HERE + "build_p972a_initializer_release.py",
        "pyproject.toml", "uv.lock", "specs/grc-v4-a-initializer-release.json"}
    return {name: p.sha((p.ROOT / name).read_bytes()) for name in sorted(names)}


def roster():
    from tests.models.test_grc_v4_initializer import ProducerTests, CrossingTests
    return [TEST + '.' + cls.__name__ + '.' + method for cls in (ProducerTests, CrossingTests)
            for method in unittest.TestLoader().getTestCaseNames(cls)] + LEGACY


def package():
    from build_p972a_initializer_release import build
    from pygrc.models.grc_v4_codec import INITIALIZER_RELEASE_ID, load_initializer_schema
    for name, data in build().items():
        p.require((p.ROOT / name).read_bytes() == data, "initializer package drift: " + name)
    load_initializer_schema()  # Executes the actual installed codec binding, not an alternate validator.
    return INITIALIZER_RELEASE_ID


def execution_sources(value, sources):
    """Preserve the accepted run across the exact codec fix and acceptance UX.

    The original codec and checker remain recoverable at their accepted Git
    subject, alongside the original status API. Current acceptance is not a
    relabeling of that run. The checker is maintained by the implementation boundary;
    codec-reference regressions are separate from the old numerical execution.
    A deliberately new run still binds its own current sources directly.
    """
    if value['source_bindings'] == sources:
        return sources
    p.require(value['record_digest'] == ACCEPTED_RECORD_DIGEST,
              "initializer execution is not the accepted predecessor")
    # During the authorized event successor, current work is checked against
    # its own manifest; original migration inputs remain the accepted Git blobs.
    work = p.read(p.ROOT / p.WORK)
    entries = {row['path']: row for row in work['entries']}
    if any(row['iteration_id'] == 'P9-7.2b' for row in entries.values()):
        p.require(work['record_digest'] == p.digest_record(work), 'event work manifest drift')
        maintenance = p.read(p.ROOT / p.POLICY)
        p.require(maintenance['record_digest'] == p.digest_record(maintenance), 'event maintenance digest drift')
        pins = {row['path']: row['sha256'] for row in maintenance['artifact_bindings']}
        adopted = p.EVENT_RUNTIME_PATHS | {SCRIPT, STATUS_API}
        sources = dict(sources)
        for name in adopted:
            expected = entries[name]['sha256'] if name in p.EVENT_RUNTIME_PATHS else pins[name]
            p.require(sources.get(name) == expected == p.sha((p.ROOT / name).read_bytes()),
                      'event successor source is not bound: ' + name)
            if name in p.EVENT_NEW_PATHS:
                sources.pop(name)
            else:
                sources[name] = p.sha(p.git(p.ROOT, 'show', 'ee8885e:' + name))
    p.require(sources.get(CODEC) == CODEC_REFERENCE_FIX_SHA256,
              "initializer codec changed beyond the exact reference fix")
    p.require(sources.get(STATUS_API) == ACCEPTANCE_STATUS_SHA256,
              "initializer status changed beyond the accepted closure view")
    # Explicitly separate this new, independently pinned wire decoder from
    # the old execution. No old codec/producer/loaded source is exempted.
    p.require(sources.get(EVENT_PACKAGE_CODEC) == EVENT_PACKAGE_CODEC_SHA256,
              "event package decoder differs from the bounded additive source")
    sources = {name: digest for name, digest in sources.items() if name != EVENT_PACKAGE_CODEC}
    from verify_p972a_initializer_authority import historical_blobs
    original = historical_blobs((CODEC, SCRIPT, STATUS_API), ACCEPTED_COMMIT)
    retained = {**sources, **{name: p.sha(data) for name, data in original.items()}}
    p.require(value['source_bindings'] == retained, "initializer execution source drift")
    return retained


def validate(value, sources):
    from pygrc.models.grc_v4_codec import initializer_identity, payload_identity
    from tests.models.test_grc_v4_initializer import FAMILIES
    p.require(value['record_digest'] == p.digest_record(value), "initializer execution digest drift")
    p.require(value['schema'] == 'phase9_a_initializer_execution_v1' and value['iteration_id'] == 'P9-7.2a'
              and value['status'] == 'verified_pending_review' and value['user_accepted'] is False
              and value['aggregate_closed'] is False and value['new_G2_support'] == []
              and value['G3_accepted'] is False, "initializer execution overclaim")
    captured_sources = execution_sources(value, sources)
    p.require(value['release_id'] == package(), "initializer execution package mismatch")
    p.require(value['test_ids'] == roster() and value['results'] == dict(
        tests_run=len(roster()), failures=[], errors=[], skips=[]), "incomplete initializer execution")
    before, after = value['loaded_sources_before'], value['loaded_sources_after']
    p.require(before and after and all(after.get(k) == v for k, v in before.items()), "loaded source changed")
    p.require(all(captured_sources.get(v['path']) == v['sha256'] for v in after.values()), "unbound loaded source")
    p.require(set(value['cases']) == set(FAMILIES) | {'auxiliary_singular', 'nontrivial_migration',
              'target_construction', 'target_readmission', 'oracle_-0.3_False', 'oracle_-0.3_True',
              'oracle_0.3_False', 'oracle_0.3_True'}, "initializer evidence roster drift")
    for family in FAMILIES:
        row = value['cases'][family]
        pair = row['archive']['initializer_pair']
        initializer_identity('pair_payload', pair['payload'], expected=pair['initializer_pair_id'])
        for role in ('current', 'reset'):
            construction = pair['payload'][role]
            initializer_identity('construction_payload', construction['payload'], expected=construction['construction_id'])
            p.require(construction['payload']['role'] == role and construction['payload']['target_reference'] == row['target_reference'],
                      "initializer role/target mismatch")
            state = row['after']['scientific_state'] if role == 'current' else row['after']['reset']
            p.require(construction['payload']['W_A_init'] == state['authoritative']['W_A']
                      and construction['payload']['target_C'] == state['authoritative']['C'], "initializer endpoint mismatch")
        primary = row['receipts'][0]
        p.require(primary['identity_payload']['initializer_pair_id'] == pair['initializer_pair_id'], "initializer receipt linkage")
        payload_identity('initializer_migration_receipt', primary['identity_payload'], expected=primary['receipt_id'])
        p.require(primary['receipt_id'] in row['after']['receipt_ids'] and
                  primary['identity_payload']['core']['target_state_digest'] == row['after']['scientific_state_digest'],
                  "initializer receipt endpoint mismatch")


def acceptance():
    p.require(p.sha((p.ROOT / ACCEPTANCE_REVIEW).read_bytes()) == ACCEPTANCE_SHA256,
              "P9-7.2a aggregate acceptance missing or changed")
    return dict(acceptance_path=ACCEPTANCE_REVIEW, acceptance_sha256=ACCEPTANCE_SHA256,
                accepted_migration_classes=list(MIGRATION_CLASSES))


def check():
    value = p.read(p.ROOT / RECORD)
    p.require(value['record_digest'] == ACCEPTED_RECORD_DIGEST,
              "aggregate acceptance binds the original run, not a replacement execution")
    validate(value, bindings())
    return dict(status='accepted', record_path=RECORD, record_digest=value['record_digest'],
                release_id=value['release_id'], tests_run=value['results']['tests_run'],
                positive_target_families=['A_OS', 'A_CI', 'A_PC', 'A_CI_PC', 'A_RG2b'],
                producer_implemented=True, payload_specification_complete=True, positive_migration_verified=True,
                aggregate_closed=True, user_accepted=True, new_G2_support=[], G3_accepted=False,
                numerical_tests_rerun=0, **acceptance())


def run():
    """Emit a new run to stdout. No archive, mutation or overwrite of old runs."""
    from tests.models.test_grc_v4_initializer import EVIDENCE
    from verify_p971_lifecycle import loaded_sources
    from verify_p972a_proposal import proposal_status
    EVIDENCE.clear()
    documents, release = proposal_status(), package()
    dependencies = {}
    for name in ('numpy', 'scipy', 'jsonschema', 'referencing'):
        try:
            dependencies[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            dependencies[name] = None  # Explicit absence, not an invented version.
    environment = dict(python=platform.python_version(), implementation=platform.python_implementation(),
                       compiler=platform.python_compiler(), system=platform.system(), machine=platform.machine(),
                       libc=list(platform.libc_ver()), dependencies=dependencies)
    sources = bindings()
    names = roster()
    suite = unittest.TestLoader().loadTestsFromNames(names)
    loaded_before = loaded_sources(sources)
    result = unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
    p.require(result.wasSuccessful() and not result.skipped and result.testsRun == len(names), "initializer focused execution failed")
    p.require(bindings() == sources, "source changed during execution")
    value = dict(schema='phase9_a_initializer_execution_v1', iteration_id='P9-7.2a',
        status='verified_pending_review', user_accepted=False, aggregate_closed=False,
        new_G2_support=[], G3_accepted=False, release_id=release,
        base_commit=p.git(p.ROOT, 'rev-parse', 'HEAD').decode().strip(),
        created_utc=datetime.now(timezone.utc).isoformat(),
        environment=environment,
        document_subject=documents, source_bindings=sources, loaded_sources_before=loaded_before,
        loaded_sources_after=loaded_sources(sources), test_ids=names,
        results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]), cases=EVIDENCE)
    value['record_digest'] = p.digest_record(value)
    validate(value, sources)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = parser.parse_args()
    print(json.dumps(check() if args.check else run(), indent=2))
