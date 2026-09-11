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
    names |= p.INITIALIZER_RUNTIME_PATHS | {SCRIPT, p.HERE + "build_p972a_initializer_release.py",
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


def validate(value, sources):
    from pygrc.models.grc_v4_codec import initializer_identity, payload_identity
    from tests.models.test_grc_v4_initializer import FAMILIES
    p.require(value['record_digest'] == p.digest_record(value), "initializer execution digest drift")
    p.require(value['schema'] == 'phase9_a_initializer_execution_v1' and value['iteration_id'] == 'P9-7.2a'
              and value['status'] == 'verified_pending_review' and value['user_accepted'] is False
              and value['aggregate_closed'] is False and value['new_G2_support'] == []
              and value['G3_accepted'] is False, "initializer execution overclaim")
    p.require(value['source_bindings'] == sources, "initializer execution source drift")
    p.require(value['release_id'] == package(), "initializer execution package mismatch")
    p.require(value['test_ids'] == roster() and value['results'] == dict(
        tests_run=len(roster()), failures=[], errors=[], skips=[]), "incomplete initializer execution")
    before, after = value['loaded_sources_before'], value['loaded_sources_after']
    p.require(before and after and all(after.get(k) == v for k, v in before.items()), "loaded source changed")
    p.require(all(sources.get(v['path']) == v['sha256'] for v in after.values()), "unbound loaded source")
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


def check():
    value = p.read(p.ROOT / RECORD)
    validate(value, bindings())
    return dict(status='verified_pending_review', record_path=RECORD, record_digest=value['record_digest'],
                release_id=value['release_id'], tests_run=value['results']['tests_run'],
                positive_target_families=['A_OS', 'A_CI', 'A_PC', 'A_CI_PC', 'A_RG2b'],
                producer_implemented=True, payload_specification_complete=True, positive_migration_verified=True,
                aggregate_closed=False, user_accepted=False, new_G2_support=[], G3_accepted=False,
                numerical_tests_rerun=0)


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
