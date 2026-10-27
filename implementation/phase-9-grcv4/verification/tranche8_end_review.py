"""Extract bounded mechanism conclusions from accepted evidence; no native rerun."""
import argparse
from fractions import Fraction as Q
import json
import lzma
import math
from pathlib import Path
import p986_first_group as h

ROOT, BASE, HERE = h.ROOT, h.BASE, h.HERE
SELF = HERE + 'tranche8_end_review.py'
RESULT = BASE + 'P9-Tranche8-FirstGroupMechanisms.json'


def ratio(numerator, denominator):
    n, d = Q(numerator), Q(denominator)
    h.require(n >= 0 and d >= 0, 'negative effect/error magnitude')
    return {'kind': 'finite', 'value': str(n/d)} if d else {
        'kind': 'positive_effect_zero_error' if n else 'zero_over_zero', 'value': None}


def mechanisms(root=ROOT):
    refs = {}
    def read(name):
        path = BASE + name
        raw = h.safe(root, path).read_bytes()
        refs[path] = h.handoff.reference(root, path)
        value = json.loads(lzma.decompress(raw) if name.endswith('.xz') else raw)
        if 'record_digest' in value:
            h.require(value == h.seal(value), 'source seal drift: '+path)
        return value

    group = read('P9-8.6-FirstGroup.json')
    acceptance = read('P9-8.6-FirstGroupAcceptance.json')
    h.require(acceptance['decision_digest'] == group['record_digest'] and acceptance['user_accepted'],
              'unaccepted first group')
    # This earlier validation retains native roots, separate interval path controls,
    # test results and explicit user acceptance; it is not a fresh-code execution.
    old = read('P9-8.3C-CI-Validation.json')
    h.require(old['acceptance']['status'] == 'accepted_by_user', 'C_CI predecessor unaccepted')
    cci = []
    for item in old['numerical_observations']['roots']:
        if item['graph'] != 'target':
            continue
        effects = item['fixed_selected_geometry_path_effects']
        h.require(item['evaluations'] >= 2 and set(effects) == {'modulation','feedback','geometry'},
                  'C_CI root/control coverage')
        for value in effects.values():
            h.require(value['exact_effect_lower'] > 0 and value['minimum_margin_ratio'] > 1,
                      'unresolved C_CI path control')
        cci.append(dict(role=item['role'], evaluations=item['evaluations'],
            joint_residual_squared=item['joint_residual_squared'],
            independent_errors=item['independent_errors'], path_effects=effects))
    h.require({r['role'] for r in cci} == {'current','reset'}, 'missing C_CI role')

    staged = read('P9-8.4g-ACIStagedResults.json.xz')
    aci = []
    for case in staged['cases']:
        graph, role, oracle = case['graph'], case['role'], case['result']
        record = read('P9-8.4g-ACINativeSuccessor/'+graph+'-'+role+'.json.xz')
        h.require(record['outcome']=='completed' and record['exit_code']==0, 'incomplete A_CI execution')
        native = record['result']['roots']['current']
        h.require(native['evaluations']==2 and native['native_stopping_matches_oracle'], 'A_CI stopping mismatch')
        h.require(native['selected_joint_point_digest']==oracle['selected_joint_point_digest']
            and native['represented_geometry_digest']==oracle['represented_geometry_digest']
            and set(native['actual']) == {'potential','baseline','drive','current','flux','flat'}
            and all(v == oracle['confirming'][k] for k,v in native['actual'].items())
            and native['independent_stages']==oracle['stages'], 'A_CI full-point/native linkage')
        for stage in ('current', 'final'):
            o = oracle if stage=='current' else record['result']['final_oracle']
            r = record['result']['roots'][stage]
            h.require(r['selected_joint_point_digest']==o['selected_joint_point_digest']
                and all(v == o['confirming'][k] for k,v in r['actual'].items()) and r['evaluations']==2, 'A_CI continuation linkage')
        witness = oracle['separated_effect_witness']
        effect, error = Q(witness['lower']), Q(witness['selected_coordinate_error_upper'])
        h.require(effect > error >= 0 and oracle['feedback_coordinates_above_selected_error']>0,
                  'A_CI feedback separation missing')
        aci.append(dict(graph=graph,role=role,staged_point_digest=oracle['selected_joint_point_digest'],
            native_root_identity=native['identity'],native_state_digest=native['state_digest'],evaluations=2,
            separated_coordinates=oracle['feedback_coordinates_above_selected_error'],
            changed_diagonals=oracle['generated_changed_diagonals'],
            nonzero_offdiagonals=oracle['generated_nonzero_offdiagonals'],witness=witness,
            effect_error_ratio=ratio(effect,error),native_final_point_digest=record['result']['roots']['final']['selected_joint_point_digest'],
            reset_unchanged=record['result']['reset_unchanged'],minimum_poststep_resource=min(record['result']['after_C'])))

    apc = []
    for role in ('current','reset'):
        for step in (1,10):
            record = read(f'P9-8.4h-APC-{role}-{step}.json.xz')
            execution = record['execution']; separation = execution['carrier_separation']
            effect, error, margin = (Q(separation[k]) for k in ('effect_lower','two_read_error_upper','margin'))
            h.require(effect-error==margin>0 and separation['changed_current_coordinates']>0,
                      'A_PC unresolved or inconsistent effect')
            point = execution['reads']['final']['actual']; index = separation['witness']
            scale = abs(Q(point['current'][index])); ulp = Q(math.ulp(point['current'][index]))
            apc.append(dict(role=role,step=step,stage='poststep final C/W/Z read',
                before_digest=execution['before_digest'],point_digest=point['point_digest'],
                separation=separation,enabled_current=point['current'][index],
                effect_error_ratio=ratio(effect,error),relative_effect_lower=ratio(effect,scale),
                enabled_current_ulp=str(ulp),effect_in_enabled_ulps_lower=str(effect/ulp)))

    # Bind the algorithms explaining what each retained comparison actually measures.
    for name in ('tests/models/test_grc_9_v4_cci.py',HERE+'test_p980_os_effect_witness.py',
                 HERE+'p984g_aci_native_check.py',HERE+'p984g_apc_hardening.py',SELF):
        refs[name] = h.handoff.reference(root,name)
    return h.seal(dict(schema='tranche8-first-group-mechanism-review-v1',date='2026-10-27',
        families=list(h.FAMILIES),acceptance_digest=acceptance['record_digest'],
        evidence_kind='accepted retained evidence extraction and exact rational arithmetic; no new numerical execution',
        C_OS=dict(disposition='existing accepted reference; no new campaign'),
        C_CI=dict(disposition='existing evidence sufficient for named fixed-selected-geometry path discrimination',
            observations=cci,control='independent formula ablations at the admitted native geometry; not alternative CI roots',
            limitation='large first-pass/reference-geometry runs still do not resolve CI feedback above rounding; smaller path evidence does not remove that limit'),
        A_CI=dict(disposition='existing staged effects bound to native full roots, two-pass stopping and final-C/W continuation',
            observations=aci,control='exact-root current minus reference-H current; selected-coordinate error bound',
            limitation='four prepared .g subjects, not every .h postbeat state; largest-effect coordinates and source diagonals need not resolve'),
        A_PC=dict(disposition='resolved pointwise carrier effects; small absolute margins alone do not imply fragility',
            observations=apc,control='same final C/W, carrier-generated H versus reference H; both read errors included',
            neighboring_input_pressure='not applicable: no wider input domain selected or claimed',
            limitation='same-coordinate ratios are local lower/upper-bound comparisons, not uniform robustness or trajectory enclosures'),
        numerical_trajectories_rerun=False,new_native_steps=0,new_support=False,limits=h.LIMITS,
        source_refs=list(refs.values())))


def check(root=ROOT):
    value = h.load(root,RESULT)
    h.require(value==mechanisms(root), 'mechanism review drift')
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('record','check'));args=parser.parse_args()
    if args.action=='record':
        h.write(RESULT,mechanisms())
    else:
        check()
    print('Bounded mechanism review verified; no numerical rerun')
