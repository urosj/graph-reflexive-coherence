"""Reconcile exact P9-7.7 coverage without rerunning or promoting evidence.

This is a bounded review of the retained corpus, not a new acceptance engine.
--emit prints the review; default verifies it against its unchanged sources.
"""

import argparse
import json
import sys

import phase9_implementation_policy as p

RECORD = p.PHASE + 'tranche-7/P9-7.7-ProfileReview.json'
SCRIPT = p.HERE + 'verify_p977_profile_review.py'
TEST = p.HERE + 'test_p977_profile_review.py'
CATALOG = 'specs/grc-v4-conformance-fixtures.json'
REGISTER = p.PHASE + 'tranche-1/P9-1.4-SupportAndDependencies.json'
ROUTING = p.PHASE + 'tranche-6/P9-6.5-RealizationRouting.json'
SOURCES = {
    'lifecycle': p.PHASE + 'tranche-7/P9-7.1-Lifecycle.json',
    'migration': p.PHASE + 'tranche-7/P9-7.2a-Migrations.json',
    'initializer': p.PHASE + 'tranche-7/P9-7.2a-InitializerRuntime.json',
    'event': p.PHASE + 'tranche-7/P9-7.2b-RuntimeAuditCorrection.json',
    'history': p.PHASE + 'tranche-7/P9-7.3-HistoryPolicy.json',
    'history_regressions': p.PHASE + 'tranche-7/P9-7.3-SharpRegressions.json',
    'reference': p.PHASE + 'tranche-7/P9-7.4-TargetReference.json',
    'failure': p.PHASE + 'tranche-7/P9-7.5-FailureSequences.json',
    'lineage': p.PHASE + 'tranche-7/P9-7.6-LineageOwnership.json',
}
REALIZATION_CASE = dict(CI='CI-BRANCH', OS='OS-ONE-PASS', RG2b='RG2B-SECTION',
                        PC='PC-ZOH', CI_PC='CI-PC-SAME-SOURCE')


def read(path):
    return p.read(p.ROOT / path)


def ref(path, pointer):
    return dict(path=path, json_pointer=pointer)


def resolve(reference):
    value = read(reference['path'])
    for part in reference['json_pointer'].strip('/').split('/'):
        if part:
            part = part.replace('~1', '/').replace('~0', '~')
            value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def required_cases(family):
    candidate, realization = family.split('_', 1)
    catalog = read(CATALOG)
    return [r['id'] for group in ('common_cases', 'candidate_' + candidate.lower() + '_cases')
            for r in catalog[group]] + [REALIZATION_CASE[realization]] + [r['id'] for r in catalog['lifecycle_cases']]


def bindings():
    from verify_p972b_runtime import bindings as runtime_bindings
    routing = read(ROUTING)
    names = set(SOURCES.values()) | {SCRIPT, TEST, CATALOG, REGISTER, ROUTING, p.G2_ACCEPTANCE,
        'specs/grc-v4-conformance-vectors.json', 'specs/grc-v4-spec.md',
        'specs/grc-common-interface-v4-ext.md', 'specs/grc-v4-topology-event-spec.md',
        'specs/grc-v4-representation-transport-spec.md', p.INV + 'drafts/2026-09-GRC-V4.md',
        p.PHASE + 'tranche-1/P9-1.2-DebtInventory.json',
        p.PHASE + 'tranche-1/P9-1.3-VerificationRouting.json',
        p.PHASE + 'tranche-4/P9-4.8-GateReview.json',
        p.PHASE + 'tranche-4/P9-4.8B-GateReview.json',
        p.PHASE + 'tranche-5/P9-5.4-AuditFollowup.json',
        read(p.G2_ACCEPTANCE)['fixture_run']['path']}
    names.update(r['path'] for r in routing['accepted_records'].values())
    return {**runtime_bindings(), **{n: p.sha((p.ROOT / n).read_bytes()) for n in sorted(names)}}


def authority():
    sys.path.insert(0, str(p.ROOT / p.SIDE / 'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT / p.SIDE)
    return {
        'C_baseline': contract_provenance(context, 'D11-C-EC-C-J0-CURRENT'),
        'A_initializer': contract_provenance(context, 'P9-EC-A-INITIALIZER-REFERENCE-PASS'),
        'parent_ceiling': contract_provenance(context, 'P9-EC-RECEIPT-PARENT-CEILING'),
    }


def predecessor():
    from verify_p976_acceptance import check
    return check()


def reconcile():
    """Literal source locations and identities, not family-label joins."""
    catalog, register, routing = read(CATALOG), read(REGISTER), read(ROUTING)
    runs = {name: read(path) for name, path in SOURCES.items()}
    accepted = p.accepted_g2(p.ROOT)
    old_run = read(accepted['fixture_run']['path'])
    profiles, migrations = [], []
    for key, row in runs['migration']['cases'].items():
        migrations.append(dict(source_family=row['source_family'], target_family=row['target_family'],
            source_profile_id=row['before']['scientific_state']['active_model_identity'],
            target_profile_id=row['after']['scientific_state']['active_model_identity'],
            migration_class=row['migration_class'], evidence=ref(SOURCES['migration'], '/cases/' + key)))
    for family in ('A_OS', 'A_CI', 'A_PC', 'A_CI_PC', 'A_RG2b'):
        row = runs['initializer']['cases'][family]
        migrations.append(dict(source_family=row['initial']['reference']['profile']['identity_payload']['profile_family_id'],
            target_family=family, source_profile_id=row['initial']['reference']['profile']['complete_profile_id'],
            target_profile_id=row['target_reference']['profile']['complete_profile_id'],
            migration_class='C_to_A', evidence=ref(SOURCES['initializer'], '/cases/' + family)))

    for declared in register['profiles']:
        family = declared['profile_family']
        ids = required_cases(family)
        p.require(ids == declared['required_catalog_case_ids'], 'catalog/register applicability drift')
        seed = runs['lifecycle']['families'][family]
        profile = seed['initial']['reference']['profile']
        nominated = accepted['accepted_profile'] if family == 'C_OS' else profile
        identity = nominated['complete_profile_id']
        numerical = ([ref(ROUTING, '/prior_OS_scope/' + family)] if family.endswith('_OS') else
                     [ref(ROUTING, '/profiles/' + str(i)) for i,r in enumerate(routing['profiles'])
                      if r['profile_family'] == family])
        event = runs['event']['cases']['reconstruction_' + family]
        event_id = event['request']['target_profile_id']
        representation = runs['event']['cases']['representation_' + family]['primary']['identity_payload']
        cells = []
        for case in ids:
            if family == 'C_OS':
                matches = [i for i,r in enumerate(old_run['fixture_results'])
                           if r['fixture_id'] == case and r['complete_profile_id'] == identity]
                p.require(len(matches) == 1, 'accepted C_OS product missing/duplicate row')
                row = old_run['fixture_results'][matches[0]]
                p.require(set(catalog['execution_contract']['required_result_fields']) <= set(row),
                          'accepted C_OS result fields absent')
                cells.append(dict(fixture_id=case, disposition='accepted_alias',
                    evidence=[ref(accepted['fixture_run']['path'], '/fixture_results/' + str(matches[0]))]))
                continue
            if case in ('COMMON-VALID-ORDINARY-STEP', 'SNAPSHOT-LOAD-REPLAY', 'RESET-AFTER-ORDINARY',
                        'DUPLICATION-INDEPENDENCE', 'RECEIPT-OWNERSHIP'):
                refs, scope = [ref(SOURCES['lifecycle'], '/families/' + family)], 'exact_seed_lifecycle_witness'
            elif case.startswith('COMMON-'):
                refs, scope = [ref(SOURCES['lifecycle'], '/test_ids')], 'family_pressure_test_roster_not_result_row'
            elif case.startswith(('A-', 'C-')) or case == REALIZATION_CASE[family.split('_', 1)[1]]:
                refs, scope = numerical, 'accepted_numerical_routing_not_exact_catalog_product'
                if case in ('C-LIFECYCLE-REFERENCE-MAP', 'C-TR-REFERENCE-MAP'):
                    refs = [ref(SOURCES['reference'], '/cases/five_targets/' + str(i))
                            for i,r in enumerate(runs['reference']['cases']['five_targets']) if r['family'] == family]
                    scope = 'target_reference_witness_requires_complete_case_projection'
                elif case == 'A-MIGRATION-HISTORY-RECEIPT':
                    refs = [r['evidence'] for r in migrations if r['source_family'] == family or r['target_family'] == family]
                    scope = 'ordered_endpoint_witnesses_not_complete_migration_matrix'
            elif case in ('ALL-MIGRATION-CLASSES', 'RESET-AFTER-MIGRATION'):
                refs = [r['evidence'] for r in migrations if r['source_family'] == family or r['target_family'] == family]
                scope = 'ordered_endpoint_witnesses_not_complete_migration_matrix'
            elif case in ('WHOLE-LIFECYCLE-TUPLE-MAP', 'RESET-AFTER-EVENT', 'HISTORY-DISPOSITION'):
                refs = [ref(SOURCES['event'], '/cases/reconstruction_' + family),
                        ref(SOURCES['event'], '/cases/representation_' + family)]
                scope = 'crossing_witness_not_reset_after_event_result' if case == 'RESET-AFTER-EVENT' else 'crossing_witness_requires_endpoint_reconciliation'
            else:
                refs = [ref(SOURCES['reference'], '/cases/atomic_rejections'),
                        ref(SOURCES['failure'], '/cases/mixed_readmission')]
                scope = 'bounded_shared_failure_pressure_not_every_target_profile'
            cells.append(dict(fixture_id=case, disposition='reconciliation_pending', evidence=refs,
                              evidence_scope=scope, remaining='Bind exact inputs/controls and required result fields; execute only genuinely uncovered assertions.'))

        profiles.append(dict(profile_family=family, gate='P9-G2[' + family + ']',
            complete_profile_id=identity, nomination=nominated,
            reference_scope=(ref(accepted['fixture_run']['path'], '/objects/' + accepted['fixture_run']['nominated_prestate_object'])
                             if family == 'C_OS' else ref(SOURCES['lifecycle'], '/families/' + family + '/initial')),
            lifecycle_seed_profile_id=profile['complete_profile_id'],
            event_target_profile_id=event_id, event_target_matches_nomination=event_id == identity,
            representation_source_profile_id=representation['core']['source_model_identity'],
            representation_target_profile_id=representation['core']['target_model_identity'],
            verdict='ACCEPTED_ALIAS' if family == 'C_OS' else 'HOLD',
            required_case_count=len(ids), cells=cells,
            blockers=[] if family == 'C_OS' else ['G2-EXACT-PRODUCT', 'G2-ORDERED-ENDPOINTS', 'G2-INTEGRATED-REVIEW'],
            new_execution_credit=0, new_G2_support=[]))
    return dict(profiles=profiles, ordered_migration_witnesses=migrations,
        migration_classes=register['migration_classes'],
        required_result_fields=catalog['execution_contract']['required_result_fields'],
        original_C_OS_hold=ref(p.PHASE + 'tranche-4/P9-4.8-GateReview.json', ''),
        C_OS_successor=ref(p.G2_ACCEPTANCE, ''),
        shared_followthrough={k: ref(SOURCES[k], '/cases') for k in ('history', 'history_regressions', 'reference', 'failure', 'lineage')},
        residual_debt_routing=ref(p.PHASE + 'tranche-1/P9-1.3-VerificationRouting.json', ''),
        summary=dict(profile_count=10, required_cells=sum(len(r['cells']) for r in profiles),
                     accepted_aliases=['C_OS'], held_profiles=[r['profile_family'] for r in profiles if r['verdict'] == 'HOLD'],
                     accepted_alias_cells=33, unresolved_new_profile_cells=272,
                     numerical_tests_rerun=0, new_execution_credit=0))


def build(prior=None):
    prior = predecessor() if prior is None else prior
    p.require(prior['user_accepted'] and prior['aggregate_closed'], 'P9-7.6 not accepted')
    value = dict(schema='phase9_profile_conformance_review_v1', iteration_id='P9-7.7',
        status='reviewed_hold_pending_independent_review', user_accepted=False, aggregate_closed=False,
        new_G2_support=[], G3_accepted=False, source_bindings=p.g2_retained_bindings(bindings()),
        predecessor={k: prior[k] for k in ('record_digest', 'acceptance_sha256')},
        authority=authority(), **reconcile())
    value['record_digest'] = p.digest_record(value)
    return value


def validate(value, expected):
    p.require(value['record_digest'] == p.digest_record(value), 'profile review digest drift')
    p.require(value == expected, 'profile review differs from exact retained evidence; no inferred acceptance')
    for row in value['profiles']:
        for cell in row['cells']:
            p.require(cell['evidence'], 'vacuous evidence link')
            for reference in cell['evidence']:
                p.require(resolve(reference) is not None, 'unresolved evidence pointer')


def check(prior=None):
    value = read(RECORD)
    validate(value, build(prior))
    return dict(status=value['status'], record_path=RECORD, record_digest=value['record_digest'],
                user_accepted=False, aggregate_closed=False, new_G2_support=[], G3_accepted=False,
                **value['summary'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    print(json.dumps(build() if parser.parse_args().emit else check(), indent=2))
