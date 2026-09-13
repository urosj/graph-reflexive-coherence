"""Run the bounded event suite or inspect its retained evidence; no file writes."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import sys
import unittest

import phase9_implementation_policy as p

RECORD = p.PHASE + "tranche-7/P9-7.2b-Runtime.json"
CURRENT_RECORD = p.PHASE + "tranche-7/P9-7.2b-RuntimeAuditCorrection.json"
ORIGINAL_SOURCES = p.PHASE + "tranche-7/P9-7.2b-RuntimeOriginalSources.json"
ORIGINAL_DIGEST = "c3fb9823ae040408fd86963754ce6b3f7acbc897c7a5a88504582193d0cc4391"
SCRIPT = p.HERE + "verify_p972b_runtime.py"
TEST = "tests.models.test_grc_v4_events"
AUDIT_TEST = "tests.models.test_grc_v4_event_audit"


def bindings():
    names = {n for n in p.git(p.ROOT, "ls-files", "src", "tests").decode().splitlines()
             if n.endswith('.py') and ('grc_v4' in n or n.startswith('src/pygrc/core/')
                                      or n in {'src/pygrc/__init__.py', 'src/pygrc/models/__init__.py',
                                               'tests/__init__.py', 'tests/models/__init__.py'})}
    names |= p.EVENT_RUNTIME_PATHS | {SCRIPT, ORIGINAL_SOURCES, "pyproject.toml", "uv.lock", "specs/grc-v4-event-contract-release.json"}
    return {n: p.sha((p.ROOT / n).read_bytes()) for n in sorted(names)}


def roster():
    from tests.models.test_grc_v4_events import EventRuntimeTests
    from tests.models.test_grc_v4_event_audit import RuntimeAuditRegressions
    return [module + '.' + cls.__name__ + '.' + n
            for module, cls in ((TEST, EventRuntimeTests), (AUDIT_TEST, RuntimeAuditRegressions))
            for n in unittest.TestLoader().getTestCaseNames(cls)]


def preserved_original():
    """Recover the submitted source subject exactly; never relabel its run."""
    value = p.read(p.ROOT / RECORD)
    p.require(value['record_digest'] == p.digest_record(value) == ORIGINAL_DIGEST,
              'original event execution changed')
    bridge = p.read(p.ROOT / ORIGINAL_SOURCES)
    p.require(bridge['record_digest'] == p.digest_record(bridge)
              and bridge['original_record_digest'] == ORIGINAL_DIGEST, 'original source bridge drift')
    sources = bindings()
    sources.pop(ORIGINAL_SOURCES)
    sources.pop('tests/models/test_grc_v4_event_audit.py')
    for name, delta in bridge['prior_source_delta'].items():
        content = (p.ROOT / name).read_bytes()
        if sources.get(name) != delta['current_sha256']:
            p.require(p.g2_bindings_match({name: delta['current_sha256']}, {name: sources.get(name)}),
                      'unreviewed discovery correction source: ' + name)
            from a_os_g2_source_reuse import BASE
            content = p.git(p.ROOT, 'show', BASE + ':' + name)
            sources[name] = p.sha(content)
        p.require(sources.get(name) == delta['current_sha256'], 'correction source drift: ' + name)
        lines = content.decode().splitlines(keepends=True)
        end = len(lines)
        for span in reversed(delta['splices_to_original']):
            start, stop = span['start'], span['stop']
            p.require(0 <= start <= stop <= end, 'invalid original source span')
            lines[start:stop] = span['old_lines']
            end = start
        sources[name] = p.sha(''.join(lines).encode())
        p.require(sources[name] == delta['original_sha256'], 'original source recovery failed')
    p.require(p.g2_bindings_match(value['source_bindings'], sources), 'original execution source mismatch')
    return ORIGINAL_DIGEST


def check():
    from pygrc.models.grc_v4_event_codec import EVENT_RELEASE_ID, load_event_schemas
    load_event_schemas()
    original = preserved_original()
    value = p.read(p.ROOT / CURRENT_RECORD)
    p.require(value['record_digest'] == p.digest_record(value), 'event evidence digest drift')
    p.require(p.g2_bindings_match(value['source_bindings'], bindings()), 'event execution source drift')
    p.require(value['original_record_digest'] == original, 'correction predecessor drift')
    p.require(value['release_id'] == EVENT_RELEASE_ID and value['iteration_id'] == 'P9-7.2b', 'event execution subject drift')
    p.require(value['test_ids'] == roster() and value['results'] == dict(tests_run=len(roster()), failures=[], errors=[], skips=[]), 'event execution incomplete')
    p.require(value['user_accepted'] is False and value['aggregate_closed'] is False
              and value['new_G2_support'] == [] and value['G3_accepted'] is False, 'event evidence overclaim')
    expected = {prefix + c + '_' + r for prefix in ('reconstruction_', 'representation_')
                for c in ('A', 'C') for r in ('OS', 'CI', 'RG2b', 'PC', 'CI_PC')}
    expected |= {'A_loss_' + r for r in ('OS', 'CI', 'RG2b', 'PC', 'CI_PC')}
    expected |= {'signed_parallel_loop', 'legacy_migration_event'}
    p.require(set(value['cases']) == expected, 'missing executed event cases')
    return dict(status='implemented_verified_pending_review', record_path=CURRENT_RECORD, record_digest=value['record_digest'],
                original_record_path=RECORD, original_record_digest=original,
                test_count=len(roster()), case_count=len(expected), release_id=EVENT_RELEASE_ID,
                user_accepted=False, aggregate_closed=False, new_G2_support=[], G3_accepted=False)


def run():
    from tests.models.test_grc_v4_events import EVIDENCE
    from pygrc.models.grc_v4_event_codec import EVENT_RELEASE_ID
    before = bindings()
    original = preserved_original()
    EVIDENCE.clear()
    ids = roster()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    p.require(before == bindings(), 'sources changed during event execution')
    p.require(result.wasSuccessful() and not result.skipped, 'event tests failed; no passing evidence emitted')
    value = dict(schema='phase9_event_execution_v1', iteration_id='P9-7.2b', status='verified_pending_review',
        user_accepted=False, aggregate_closed=False, new_G2_support=[], G3_accepted=False,
        captured_at=datetime.now(timezone.utc).isoformat(), source_bindings=before, release_id=EVENT_RELEASE_ID,
        original_record_digest=original,
        test_ids=ids, results=dict(tests_run=result.testsRun, failures=[], errors=[], skips=[]), cases=EVIDENCE,
        environment=dict(python=platform.python_version(), dependencies={n: importlib.metadata.version(n) for n in ('numpy', 'jsonschema', 'rfc8785')}),
        scope='Finite reconstruction and representation executions, not all-pairs or arbitrary-graph conformance; previous runs unchanged.')
    value['record_digest'] = p.digest_record(value)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run() if args.run else check(), indent=2))
