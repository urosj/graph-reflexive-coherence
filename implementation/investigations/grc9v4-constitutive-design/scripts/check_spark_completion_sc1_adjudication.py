"""Check SC-1 scientific adjudication bindings/ceilings, without native execution."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INV = "implementation/investigations/grc9v4-constitutive-design/"
RECORD = INV + "evidence/spark-completion/SC1Adjudication.json"
POLICY = "grc9v4-certified-geometric-child-basins-v1"
CLAIMS = {
    "SC1-CL-N-GEOMETRIC-IDENTITY": "normative_scientific_choice",
    "SC1-CL-C-SPATIAL-BASINS": "conditional_mathematical",
    "SC1-CL-C-RETURN": "conditional_mathematical",
    "SC1-CL-C-COMPLETION": "conditional_mathematical",
}
DEBTS = {
    "SC-DEBT-ORGANIZATION": "partially_resolved_scientific_definition",
    "SC-DEBT-STABILITY": "open",
    "SC-DEBT-NONEMPTY-DOMAIN": "open",
    "SC-DEBT-TEMPORAL-LIFECYCLE": "open",
}
SCOPE = dict(
    SC1_closed=True, scientific_definition_selected=True,
    conditional_A7_bridge_selected=True, SC2_closed=False, SC3_closed=False,
    accepted_forensic_graph_changed=False, paper_spec_propagated=False,
    nonlinear_site_binding_admitted=False, native_completion_policy_registered=False,
    completed_spark_support=False, hierarchy_support=False, G4_accepted=False,
    native_steps=0, native_events=0, aggregate_debts_closed=[],
    accepted_generic_runtime_support_added=[], admitted_specialization_support_added=[])


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def check_semantics(value):
    need(value['status'] == 'accepted_bounded_scientific_definition', 'decision status')
    need(value['policy_id'] == POLICY, 'selected policy')
    need(value.get('policy_definition') == {
        'path': INV + 'decisions/SparkCompletionSC1Contract.md',
        'sections': ['2', '3', '4', '5'],
        'numerical_example_is_not_a_selected_runtime_binding': True,
    }, 'selected policy definition changed')
    need(value['scope'] == SCOPE, 'adjudication scope widened or changed')
    rows = value['claim_dispositions']
    need(len(rows) == len(CLAIMS) and
         {r['claim_id']: r['claim_class'] for r in rows} == CLAIMS, 'claim roster/class')
    need(all(r['status'] == 'accepted_bounded_research' and r['remaining_limits']
             for r in rows), 'missing claim ceiling')
    need(rows[0]['predecessor_claim_id'] == 'SC1-CL-P-GEOMETRIC-IDENTITY',
         'scientific choice predecessor')
    rows = value['debt_dispositions']
    need(len(rows) == len(DEBTS) and {r['debt_id']: r['status'] for r in rows} == DEBTS,
         'debt overclosure or missing debt')
    need(all(r['remaining'] for r in rows), 'remaining debt obligations omitted')
    need(value['carried_forward'] == {'SC2-DEBT-NONLINEAR-SITE-BINDING': 'open'},
         'site binding silently admitted')


def check(value):
    need(value['schema'] == 'grc9v4-spark-sc1-adjudication-v1', 'schema')
    need(value['record_digest'] == digest(value), 'record digest')
    check_semantics(value)
    required = {
        INV + 'decisions/SparkCompletionSC1Adjudication.md',
        INV + 'scripts/check_spark_completion_sc1_adjudication.py',
        INV + 'evidence/spark-completion/SC1Checks.json',
        INV + 'evidence/spark-completion/SC1ClaimDebtLedger.json',
        INV + 'evidence/spark-completion/SC2MechanismChecks.json',
        INV + 'evidence/spark-completion/SC2ClaimDebtLedger.json',
        INV + 'decisions/SparkCompletionSC1Contract.md',
        INV + 'evidence/spark-completion/review/SC1ScientificPressureReview.md',
    }
    rows = value['sources']
    need(len(rows) == len(required) and {r['path'] for r in rows} == required,
         'incomplete decision/predecessor binding')
    # The prior evidence binds its full source set, including paper/spec and
    # research helpers. Verify bytes; do not repeat its numerical calculations.
    for record in ('SC1Checks.json', 'SC2MechanismChecks.json'):
        prior = json.loads((ROOT / INV / 'evidence/spark-completion' / record).read_bytes())
        rows = rows + prior['sources']
    for row in rows:
        path = Path(row['path'])
        need(not path.is_absolute() and '..' not in path.parts, 'nonportable source path')
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == row['sha256'],
             'changed source: ' + str(path))


def definition_selector_controls(value):
    """Audit regressions: fresh digests must not authorize another definition."""
    mutations = (
        lambda v: v.pop('policy_definition'),
        lambda v: v['policy_definition'].update(sections=['7']),
        lambda v: v['policy_definition'].update(numerical_example_is_not_a_selected_runtime_binding=False),
        lambda v: v['policy_definition'].update(path=INV + 'decisions/SparkCompletionSC2MechanismAnalysis.md'),
    )
    for mutate in mutations:
        changed = copy.deepcopy(value)
        mutate(changed)
        changed['record_digest'] = digest(changed)
        try:
            check(changed)
        except ValueError as exc:
            need(str(exc) == 'selected policy definition changed', 'wrong rejection stage')
        else:
            raise ValueError('altered definition selector accepted')
    return len(mutations)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', required=True)
    parser.parse_args()
    value = json.loads((ROOT / RECORD).read_bytes())
    check(value)
    definition_selector_controls(value)
    print('PASS: SC-1 bounded scientific selection; 4 definition-selector rejection controls; source/ledger bindings. No native completion.')
