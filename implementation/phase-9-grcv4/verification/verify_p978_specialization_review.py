"""P9-7.8 admission review: exact predecessors and forward work, not conformance.

Rebuild from pinned accepted inputs and typed forensic queries. No numerical
campaign, runtime authorization, source mutation or historical evidence rewrite.
"""
import argparse
import json
import re
import sys

import phase9_implementation_policy as p
import profile_g2_registry as g
import verify_p977_aggregate as aggregate

BASE = '25b80f4'
RECORD = p.PHASE + 'tranche-7/P9-7.8-SpecializationReview.json'
TEXT = p.PHASE + 'tranche-7/P9-7.8-SpecializationReview.md'
BROWSER = p.SIDE + 'tool/phase9-web/specialization-review.js'
OWNERS = p.PHASE + 'tranche-1/P9-1.5-OwnershipAndLegacyBaseline.json'
SPEC = 'specs/grc-9-v4-spec.md'
VECTORS = 'specs/grc-v4-conformance-vectors.json'
FAMILIES = sorted(c + '_' + r for c in ('A', 'C') for r in ('OS', 'CI', 'PC', 'CI_PC', 'RG2b'))
SURFACES = ('TRANSITION', 'STATE', 'OBSERVABLE', 'LIFECYCLE')
# Each row is a future obligation; no result is manufactured by this review.
MATRIX = (
    ('P9-8.1a', 'ports/chart', 'Nine ordered ports, endpoint uniqueness, fixed 3x3 chart, malformed envelope rejection.'),
    ('P9-8.1b', 'differential', 'Independent fixed-row gradient/Hessian/flux and A/C/disabled stage-specific weight bridge; not generic-backend substitution.'),
    ('P9-8.1c', 'trigger', 'Nine active ports AND semantic degeneracy, fresh post-beat candidate; candidate is neither expansion nor completed spark.'),
    ('P9-8.1d', 'coarse/Split', 'Actual column coarse-graining and Split operator; cache refresh is not evidence.'),
    ('P9-8.2', 'allocator', 'D11-G9-P4a reserve-first same-port chiral primary spine, conditional phase, recursive BFS/rotor, capacity and deterministic event namespace; reject caller target allocation.'),
    ('P9-8.3C-OS', 'C nonpersistent expansion', 'Exact C_OS vector identities, complete target reference map and full rederivation; no W_A or carrier loss invented.'),
    ('P9-8.3C-PC', 'C persistent expansion', 'Execute nonnull carrier reset vector; whole-carrier zero reset and exactly carrier_history_loss, both digest preimages.'),
    ('P9-8.3A', 'A expansion aggregate', 'Close only after P9-8.3A.1 and P9-8.3A.2 are accepted for the same exact A scope; no inferred family-wide conformance.'),
    ('P9-8.3A.1', 'A specialization oracle production', 'Select and validate permitted A-history/initialization binding; independently construct concrete source/target, old/new-edge W, fixed-row/reference-current, distinct current/reset, W/Z loss, resource/receipt/readmission and rollback expectations outside the frozen release. Construction evidence, not production runtime output.'),
    ('P9-8.3A.2', 'A expansion implementation and comparison', 'Implement and test against the accepted pinned P9-8.3A.1 oracle for the same exact scope; independently verify current/reset reconstruction, W/Z history, readmission, receipts, rollback and replay. Do not replace the oracle with production results.'),
    ('P9-8.4', 'vectors/covariance', 'All D30/D31/D45/D52 chirality/phase vectors and three metamorphic cases, signed-edge reorientation and phase boundaries; D37/D44 additional probes cannot replace D31/D52.'),
    ('P9-8.5', 'readmission/rollback', 'Distinct current/reset resource map, occupancy, charge, independent target reconstruction, missing lineage/map failures, persistent ledger versus delta, whole-publication rollback.'),
    ('P9-8.6', 'arbitrary-size review', 'Runtime deep D52 plus covariance and nonstall/capacity invariants required; construction witnesses alone do not close conformance.'),
    ('P9-9.1b', 'mandatory lifecycle', 'After 8.6: separate beat and expansion transactions, target readmission, charge, receipts, reset/replay and deep duplicate ownership for every consumed exact profile.'),
    ('P9-9.2/P9-9.3', 'disabled matrix', 'Forty independent exact delegate/input/oracle/result cells, scoped to unchanged V3 defined domain; no row/column inference.'),
    ('P9-9.4', 'branch crossings', 'Both directions, distinct current/reset prestates, candidate/carrier loss channels, correct branch snapshot/reset semantics; no enabled event relabeled V3.'),
    ('P9-9.5/P9-9.6', 'legacy/full review', 'Unchanged legacy regressions and all applicable enabled, mandatory lifecycle and disabled evidence; enabled-only is not full GRC9V4 conformance.'),
    ('P9-9.1a', 'optional completion', 'Not selected: stabilization/completed-spark/hierarchy needs its own evidence if later advertised or explicitly required by a stronger handoff.'),
)

A_EXPANSION_WORK = dict(
    parent='P9-8.3A', oracle_owner='P9-8.3A.1', runtime_owner='P9-8.3A.2',
    oracle_entry=['accepted_exact_A_G2', 'accepted_consumed_set_G3',
                  'accepted_port_chart_fixed_row_initializer_and_D11_G9_contracts'],
    oracle_requires_production_runtime=False,
    runtime_entry=['accepted_P9-8.3A.1_same_exact_scope', 'accepted_exact_A_G2',
                   'accepted_consumed_set_G3', 'implemented_and_verified_P9-8.1a',
                   'implemented_and_verified_P9-8.1b', 'implemented_and_verified_P9-8.1c',
                   'implemented_and_verified_P9-8.2'],
    parent_closure='both_children_accepted_for_same_exact_A_scope',
    generic_authority_gap_route='Hold affected child and return the exact missing graph-generic contract to a bounded Tranche 7 correction through established authority/paper/spec/runtime propagation; no specialization workaround or unrelated claim reopening.',
    independent_C_work_blocked=False)


def build():
    p.git(p.ROOT, 'merge-base', '--is-ancestor', BASE, 'HEAD')
    bindings = {}

    def pin(name):
        content = p.safe_path(p.ROOT, name).read_bytes()
        p.require(content == p.git(p.ROOT, 'show', BASE + ':' + name), 'P9-7.8 input drift: ' + name)
        bindings[name] = p.sha(content)
        return content

    predecessor = aggregate.check()
    p.require(predecessor['aggregate_closed'] and predecessor['user_accepted'], 'P9-7.7 not accepted')
    pin(aggregate.RECORD)
    pin(aggregate.ACCEPTANCE)
    pin(g.REGISTRY)
    roster = g.registry(p.ROOT)
    support = g.checked(p.ROOT)['accepted_generic_runtime_support']
    p.require(len(support) == 10 and support == predecessor['accepted_generic_runtime_support'], 'G2 support mismatch')
    profiles = []
    for row in sorted(roster['records'], key=lambda r: r['profile_family_id']):
        accepted = json.loads(pin(row['acceptance']['path']))
        pin(row['review']['path'])
        p.require(row['state'] == 'accepted', 'unaccepted consumed profile')
        profiles.append(dict(profile_family_id=row['profile_family_id'],
                             nomination=accepted['accepted_profile'], acceptance=row['acceptance'],
                             review=row['review'], scope_policy='Only the accepted declaration and its recorded domains/endpoints; no new nine-port target identity or arbitrary parameter scope.'))
    p.require([r['profile_family_id'] for r in profiles] == FAMILIES, 'consumed family mismatch')
    for leaf in ('7.1', '7.2a', '7.3', '7.4', '7.5', '7.6'):
        pin(p.PHASE + 'tranche-7/P9-' + leaf + '-Review.md')
    pin(p.PHASE + 'tranche-7/P9-7.2b-RuntimeReview.md')
    spec = pin(SPEC).decode()
    for name in ('specs/grc-v4-spec.md', 'specs/grc-common-interface-v4-ext.md',
                 'specs/grc-v4-contract-schema.json', 'specs/grc-v4-conformance-fixtures.json',
                 'specs/grc-v4-specification-release.json',
                 p.INV + 'drafts/2026-09-GRC-V4.md'):
        pin(name)
    ownership = json.loads(pin(OWNERS))
    legacy = [r for r in ownership['legacy_bindings'] if '/grc_9' in r['path']]
    p.require(bool(legacy), 'missing legacy boundary')
    for row in legacy:
        p.require(p.sha(pin(row['path'])) == row['sha256'], 'legacy semantics changed: ' + row['path'])
    modules = [r for r in ownership['modules'] if r['module_id'].startswith('grc_9_v4')]
    p.require(len(modules) == 5, 'specialization ownership mismatch')

    sys.path.insert(0, str(p.ROOT / p.SIDE / 'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    context = load_current_forensic_context(p.ROOT, p.ROOT / p.SIDE)
    ids = sorted(set(re.findall(r'`((?:D11-G9-EC-|D10\.2-EC-PARENT-|D10\.2-EC-DISABLED-)[A-Za-z0-9_-]+)`', spec)))
    p.require(len(ids) == 73, 'specialization contract population changed')
    authority = []
    for identifier in ids:
        trace = contract_provenance(context, identifier)
        p.require(trace['row_count'] == 1, 'ambiguous specialization contract')
        row = trace['rows'][0]
        pin(row['source_ref']['path'])
        # A compact projection, not a new trace: original trace identity and
        # typed support semantics remain explicit and independently rebuildable.
        authority.append(dict(contract_id=identifier, trace_digest=trace['trace_digest'],
            classification=row['classification'], source_ref=row['source_ref'],
            edge_refs=[dict(edge_id=e['edge_id'], support_semantic=e['support_semantic']) for e in row['edge_refs']],
            support_disposition=row['payload']['support_disposition'],
            accepted_claim_support_semantics=row['payload']['accepted_claim_support_semantics']))
    vectors = json.loads(pin(VECTORS))
    vector_rows = []
    for section in ('grc9_expansion_vectors', 'grc9_metamorphic_vectors', 'atomic_failure_vectors'):
        for i, row in enumerate(vectors[section]):
            identifier = row.get('fixture_id', row.get('vector_id'))
            if identifier.startswith('G9-'):
                vector_rows.append(dict(vector_id=identifier, path=VECTORS, json_pointer=f'/{section}/{i}',
                                        evidence_kind='preimplementation_oracle_not_runtime_result'))
    matrix = [dict(iteration_id=leaf, subject=subject, required_evidence=scope,
                   state='pending_child_acceptances' if leaf == 'P9-8.3A' else
                         'pending_oracle_construction_and_review' if leaf == 'P9-8.3A.1' else
                         'held_pending_accepted_oracle_and_runtime_dependencies' if leaf == 'P9-8.3A.2' else
                         'not_selected' if leaf == 'P9-9.1a' else 'pending_execution')
              for leaf, subject, scope in MATRIX]
    disabled = [dict(profile_family_id=row['profile_family_id'],
                     complete_profile_id=row['nomination']['complete_profile_id'],
                     surface=surface, contract_id='D10.2-EC-DISABLED-' + row['profile_family_id'] + '-' + surface,
                     state='pending_exact_delegate_oracle_and_runtime', delegate='src/pygrc/models/grc_9_v3.py',
                     runtime_result=None)
                for row in profiles for surface in SURFACES]
    p.require(all(r['contract_id'] in ids for r in disabled), 'disabled contract missing')
    result = dict(schema='phase9_specialization_admission_review_v1', iteration_id='P9-7.8',
        status='reviewed_recommended_pending_acceptance', user_accepted=False, tranche_7_closed=False,
        G3_accepted=False, admitted_specialization_support_sets=[], new_runtime_iterations_authorized=[],
        new_G2_support=[], specialization_runtime_conformance=False, numerical_tests_rerun=0,
        reviewed_base_commit=BASE, predecessor=predecessor, proposed_consumed_support=support,
        profiles=profiles, source_bindings=bindings, authority=authority, modules=modules,
        legacy_bindings=legacy, test_matrix=matrix, disabled_matrix=disabled, vectors=vector_rows,
        a_expansion_work=A_EXPANSION_WORK,
        optional_capabilities_selected=[], stronger_handoff_selected=False,
        legacy_domain_failure='legacy_expansion_target_undefined; whole lifecycle unchanged; never execute enabled V4 repair as V3',
        inherited_debt='Preserve each accepted G2 domain, endpoints and RG2b C1 debt. D10.2 indeterminate_requires_review is not promoted. D11 forward obligations remain unexecuted.',
        decision='Recommend G3 implementation admission for the ten exact consumed generic declarations, with all recorded leaf prerequisites. No combined GRC9V4 runtime identity or conformance is admitted. User acceptance and a scoped execution-authorization successor are required before specialization source edits.')
    result['record_digest'] = p.digest_record(result)
    return result


def validate(value, expected):
    p.require(value['record_digest'] == p.digest_record(value), 'P9-7.8 digest mismatch')
    p.require(value == expected, 'P9-7.8 source/scope/obligation mismatch')


def view(value):
    from phase9_specialization_acceptance import accepted, RECORD as acceptance_path
    decision = accepted(p.ROOT)
    p.require(value['record_digest'] == decision['review']['record_digest'], 'G3 view subject mismatch')
    result = {k: value[k] for k in ('status', 'user_accepted', 'tranche_7_closed', 'G3_accepted',
            'admitted_specialization_support_sets', 'new_runtime_iterations_authorized',
            'specialization_runtime_conformance', 'proposed_consumed_support', 'decision')} | dict(
        record_path=RECORD, record_digest=value['record_digest'], review_path=TEXT,
        profile_count=len(value['profiles']), disabled_cells=len(value['disabled_matrix']),
        contract_count=len(value['authority']), pending_A_expansion_oracle=True,
        a_expansion_work=value['a_expansion_work'],
        optional_capabilities_selected=[], numerical_tests_rerun=0)
    result.update(status='accepted', user_accepted=True, tranche_7_closed=True, G3_accepted=True,
                  admitted_specialization_support_sets=decision['admitted_specialization_support_sets'],
                  new_runtime_iterations_authorized=decision['new_runtime_iterations_authorized'],
                  runtime_paths=decision['runtime_paths'], execution_scope=decision['execution_scope'],
                  acceptance_path=acceptance_path, acceptance_digest=decision['record_digest'],
                  decision='User accepted P9-7.8 and closed Tranche 7. Exact consumed-set G3 admission with only P9-8.1a entry; no specialization runtime conformance or other leaf authorization.')
    return result


def browser_source(value):
    return '// Generated from the checked P9-7.8 review; not runtime authority.\nexport const SPECIALIZATION_REVIEW = ' + json.dumps(view(value), indent=2) + ';\n'


def check():
    value = p.read(p.ROOT / RECORD)
    validate(value, build())
    p.require((p.ROOT / BROWSER).read_text() == browser_source(value), 'P9-7.8 browser projection drift')
    return view(value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='emit reconstructed review to stdout; no writes')
    args = parser.parse_args()
    print(json.dumps(build() if args.build else check(), indent=2))
