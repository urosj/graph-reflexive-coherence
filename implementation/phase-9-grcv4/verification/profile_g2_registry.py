"""Exact-profile G2 records, not runtime permissions or scientific evaluators.

Historical acceptance adapters preserve their original records and checks.
New profiles use one common schema. The roster is pinned locally, never taken
from production discovery or a status response. Proposals publish no support.
"""

import json

import phase9_implementation_policy as p

REGISTRY = p.PHASE + 'tranche-7/ProfileG2Registry.json'
BROWSER = p.SIDE + 'tool/phase9-web/g2-registry.js'
REGISTRY_DIGEST = 'fe7809e9ae01124716588c278d1271421f2964abde43ce3ca899ae0a72d56196'
ACCEPTANCE_SCHEMA = 'phase9_exact_profile_g2_acceptance_v1'
FIELDS = {'profile_family_id', 'complete_profile_id', 'gate', 'state', 'adapter',
          'acceptance', 'review', 'view_key', 'bounded_view_key', 'review_metrics'}


def browser_source(value):
    return '// Generated from ProfileG2Registry.json; checked by the registry validator.\n' + \
        'export const G2_REGISTRY = ' + json.dumps(value, sort_keys=True, indent=2) + ';\n'


def validate_registry(value):
    p.require(set(value) == {'schema', 'records', 'reconciliation_views', 'materializers', 'record_digest'}
              and value['schema'] == 'phase9_exact_profile_g2_registry_v1'
              and value['record_digest'] == p.digest_record(value) == REGISTRY_DIGEST,
              'untrusted exact-profile G2 registry')
    views=value['reconciliation_views']
    p.require(isinstance(views,dict) and views,'missing bounded reconciliation views')
    for key,expected in views.items():
        p.require(key.endswith(('_local_product','_crossings'))
                  and expected['G2_accepted'] is False and expected['G3_accepted'] is False
                  and expected['aggregate_closed'] is False and expected['new_G2_support']==[]
                  and expected['numerical_tests_rerun']==0,'bounded view widened authority')
        p.safe_path(p.ROOT,expected['record_path'])
    ids, keys = set(), set()
    for row in value['records']:
        p.require(set(row) == FIELDS and row['complete_profile_id'] not in ids
                  and row['view_key'] not in keys, 'duplicate or malformed G2 registration')
        ids.add(row['complete_profile_id']); keys.add(row['view_key'])
        p.require(row['state'] in ('accepted', 'proposed')
                  and row['adapter'] in ('historical_c_os', 'historical_a_os', 'exact_profile_v1')
                  and row['gate'] == 'P9-G2[' + row['profile_family_id'] + ']'
                  and (row['acceptance'] is not None) == (row['state'] == 'accepted'),
                  'invalid G2 registration state')
        for ref in (row['review'], row['acceptance']):
            if ref is not None:
                p.require(set(ref) == {'path', 'record_digest'}, 'invalid G2 record reference')
                p.safe_path(p.ROOT, ref['path'])
    validate_materializers(value)


def validate_materializers(value):
    """A pinned ordered call graph, not module names supplied by status input."""
    import re
    gates={r['view_key']:r for r in value['records'] if r['adapter']!='historical_c_os'}
    expected=set(value['reconciliation_views']) | set(gates)
    seen={'profile_conformance_review'}
    for row in value['materializers']:
        p.require(set(row)=={'view_key','module','kind','dependency'}
                  and row['view_key'] in expected and row['view_key'] not in seen
                  and row['dependency'] in seen
                  and re.fullmatch(r'verify_p977_[a-z0-9_]+',row['module']) is not None,
                  'invalid or out-of-order profile materializer')
        key=row['view_key'];kind=row['kind']
        if kind=='local':
            p.require(key.endswith('_local_product') and row['dependency']=='profile_conformance_review',
                      'local materializer dependency changed')
        elif kind=='crossing':
            p.require(key.endswith('_crossings') and row['dependency']==key.removesuffix('_crossings')+'_local_product',
                      'crossing materializer dependency changed')
        else:
            p.require(kind=='g2' and key in gates and row['dependency']==gates[key]['bounded_view_key'],
                      'G2 materializer dependency changed')
        seen.add(key)
    p.require(seen-{'profile_conformance_review'}==expected,'missing profile materializer')


def _checker(root, name):
    """Resolve only current, maintenance-bound checker code under verification/."""
    import importlib
    path=p.HERE+name+'.py'
    source=p.safe_path(root,path)
    bindings={r['path']:r['sha256'] for r in p.read(p.safe_path(root,p.POLICY))['artifact_bindings']}
    p.require(path in p.PATHS and bindings.get(path)==p.sha(source.read_bytes()),'unbound profile checker')
    module=importlib.import_module(name)
    from pathlib import Path
    p.require(Path(module.__file__).resolve()==source.resolve(),'profile checker imported outside pinned source')
    return module.check


def materialize(root, initial_review):
    """Run distinct scientific checkers through one dispatch path.

    Results remain private until every checker and projection succeeds. Callers
    can track the returned keys for cleanup after any later status failure.
    """
    roster=registry(root)
    normalized=checked(root)
    gates={r['view_key']:r for r in roster['records'] if r['adapter']!='historical_c_os'}
    values={'profile_conformance_review':initial_review}
    arguments=dict(local='initial_review',crossing='local_product',g2='bounded_acceptance')
    for row in roster['materializers']:
        result=_checker(root,row['module'])(**{arguments[row['kind']]:values[row['dependency']]})
        if row['kind']=='g2':
            result=project_review(root,gates[row['view_key']],result,normalized['accepted_generic_runtime_support'])
        values[row['view_key']]=result
    checked_reconciliation(root,{key:values[key] for key in roster['reconciliation_views']})
    result={row['view_key']:values[row['view_key']] for row in roster['materializers']}
    result['profile_g2']=normalized['profiles']
    return result,normalized['accepted_generic_runtime_support']


def registry(root):
    value = p.read(p.safe_path(root, REGISTRY))
    validate_registry(value)
    p.require(p.safe_path(root, BROWSER).read_text() == browser_source(value),
              'browser G2 roster differs from trusted registry')
    return value


def bound_record(root, ref):
    value = p.read(p.safe_path(root, ref['path']))
    p.require(value['record_digest'] == p.digest_record(value) == ref['record_digest'],
              'G2 record identity changed: ' + ref['path'])
    return value


def checked_reconciliation(root, views):
    """Pin the display projection after each scientific checker has run.

    Historical status shapes remain intact. This grants no execution credit,
    acceptance or runtime permission and does not replace scientific checks.
    """
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    expected=registry(root)['reconciliation_views']
    p.require(canonical_json_bytes(views)==canonical_json_bytes(expected),
              'untrusted or incomplete bounded reconciliation projection')
    for value in views.values():
        bound_record(root,dict(path=value['record_path'],record_digest=value['record_digest']))
    return views


def support_before(root, complete_profile_id):
    """Stable predecessor scope; later acceptance never rewrites a proposal."""
    support = []
    for row in registry(root)['records']:
        if row['complete_profile_id'] == complete_profile_id:
            return sorted(support)
        if row['state'] == 'accepted':
            support.append(row['complete_profile_id'])
    raise ValueError('unregistered G2 review subject')


def common_acceptance(root, row):
    """One acceptance shape for future profiles; never creates acceptance."""
    value = bound_record(root, row['acceptance'])
    p.require(value['schema'] == ACCEPTANCE_SCHEMA, 'unknown profile acceptance schema')
    proposal = bound_record(root, row['review'])
    p.require(proposal['verdict'] == 'PASS_PROPOSAL'
              and proposal['G2_accepted'] is False and proposal['user_accepted'] is False
              and value['review']['path'] == row['review']['path']
              and value['review']['record_digest'] == row['review']['record_digest']
              and value['accepted_profile'] == proposal['nomination']
              and value['accepted_additional_support'] == proposal['proposed_additional_support']
              and value['predecessor_support'] == proposal['accepted_support_unchanged']
              and value['releases'] == proposal['releases'], 'acceptance differs from reviewed subject')
    p.git(root, 'merge-base', '--is-ancestor', value['reviewed_commit'], 'HEAD')
    for ref in (value['review'], value['review_text']):
        original = p.git(root, 'show', value['reviewed_commit'] + ':' + ref['path'])
        p.require(p.sha(original) == ref['sha256'] == p.sha(p.safe_path(root, ref['path']).read_bytes()),
                  'accepted review Git/current subject differs')
    p.require(value['accepted_generic_runtime_support'] ==
              sorted(set(value['predecessor_support'] + value['accepted_additional_support'])),
              'acceptance widened predecessor support')
    if 'source_reuse' in value:
        ref = value['source_reuse']
        p.require(p.sha(p.safe_path(root, ref['path']).read_bytes()) == ref['sha256'],
                  'accepted source-reuse subject changed')
        bound_record(root, {k: ref[k] for k in ('path', 'record_digest')})
    return value


def checked_profile(root, row):
    """Normalize legacy/current records without rewriting their evidence."""
    from pygrc.models.grc_v4_profile import resolve_profile
    review = bound_record(root, row['review'])
    expected_metrics = None if row['adapter'] == 'historical_c_os' else dict(
        catalog_cells=len(review['catalog_product']),
        supplemental_interface_methods=review['supplemental_interface_methods'],
        numerical_tests_rerun=review['numerical_tests_rerun'])
    p.require(row['review_metrics'] == expected_metrics, 'registered counts differ from bound review')
    if row['state'] == 'accepted':
        if row['adapter'] == 'historical_c_os':
            value = p.accepted_g2(root)
            added = value['accepted_generic_runtime_support']
        elif row['adapter'] == 'historical_a_os':
            value = p.accepted_a_os_g2(root)
            added = value['accepted_additional_support']
        else:
            value = common_acceptance(root, row)
            added = value['accepted_additional_support']
        p.require(value == bound_record(root, row['acceptance'])
                  and value['review']['path'] == row['review']['path']
                  and value['review']['record_digest'] == row['review']['record_digest']
                  and value['status'] == 'accepted_by_user' and value['G2_accepted'] is True
                  and value['gate'] == row['gate'] and added == [row['complete_profile_id']],
                  'accepted G2 scope differs from registry')
        p.require(value['G3_accepted'] is False
                  and value['admitted_specialization_support_sets'] == []
                  and value['new_runtime_iterations_authorized'] == []
                  and value.get('aggregate_closed', False) is False
                  and value.get('all_ordered_pairs_verified', False) is False,
                  'profile acceptance widened unrelated authority')
        if row['adapter'] == 'exact_profile_v1':
            p.require(value['aggregate_closed'] is False and value['all_ordered_pairs_verified'] is False,
                      'new acceptance must declare its scope ceilings')
        profile = value['accepted_profile']
    else:
        p.require(row['adapter'] == 'exact_profile_v1' and row['acceptance'] is None
                  and review['verdict'] == 'PASS_PROPOSAL' and review['gate'] == row['gate']
                  and review['user_accepted'] is False and review['G2_accepted'] is False
                  and review['G3_accepted'] is False and review['aggregate_closed'] is False
                  and review['new_G2_support'] == []
                  and review['ordered_scope']['all_ordered_pairs_verified'] is False
                  and review['proposed_additional_support'] == [row['complete_profile_id']],
                  'proposal cannot advertise accepted support')
        profile = review['nomination']
    resolved = resolve_profile(profile['params_resolved'], profile['identity_payload'])
    p.require(resolved.to_payload() == profile and resolved.complete_profile_id == row['complete_profile_id']
              and profile['identity_payload']['profile_family_id'] == row['profile_family_id'],
              'G2 declaration identity differs')
    return profile


def view(row):
    """Small common status shape shared with the browser; no evidence credit."""
    return {k: row[k] for k in ('profile_family_id', 'complete_profile_id', 'gate', 'state', 'review', 'acceptance')} | dict(
        G2_accepted=row['state'] == 'accepted', G3_accepted=False,
        aggregate_closed=False, all_ordered_pairs_verified=False,
        new_runtime_iterations_authorized=[], admitted_specialization_support_sets=[])


def check_discovery(profiles, supported, lookup):
    p.require(set(supported) == set(profiles), 'published G2 discovery differs from accepted declarations')
    for key, profile in profiles.items():
        p.require(lookup(key).to_payload() == profile, 'published G2 declaration differs: ' + key)


def project_review(root, row, reviewed, support):
    """Project a separately validated scientific review through its gate state."""
    p.require(reviewed['record_path'] == row['review']['path']
              and reviewed['record_digest'] == row['review']['record_digest']
              and reviewed['gate'] == row['gate']
              and reviewed['proposed_additional_support'] == [row['complete_profile_id']]
              and reviewed['G2_accepted'] is False and reviewed['user_accepted'] is False
              and reviewed['G3_accepted'] is False and reviewed['aggregate_closed'] is False
              and reviewed['all_ordered_pairs_verified'] is False and reviewed['new_G2_support'] == [],
              'scientific review differs from registered gate subject')
    p.require(all(reviewed[key] == expected for key, expected in row['review_metrics'].items()),
              'scientific review counts differ from registered evidence')
    if row['state'] == 'proposed':
        return reviewed
    checked_profile(root, row)
    result = dict(reviewed, status='accepted', user_accepted=True, G2_accepted=True,
                  acceptance_path=row['acceptance']['path'],
                  acceptance_digest=row['acceptance']['record_digest'],
                  accepted_generic_runtime_support=support,
                  new_G2_support=[row['complete_profile_id']])
    accepted = bound_record(root, row['acceptance'])
    if 'source_reuse' in accepted:
        result['source_reuse_record'] = accepted['source_reuse']
    return result


def checked(root):
    from pygrc.models.grc_v4_profile import list_supported_profiles, get_supported_profile
    rows = registry(root)['records']
    profiles = {}
    for row in rows:
        profile = checked_profile(root, row)
        if row['adapter'] != 'historical_c_os':
            proposal = bound_record(root, row['review'])
            p.require(proposal['accepted_support_unchanged'] == sorted(profiles),
                      'G2 predecessor support differs from registry order')
        if row['state'] == 'accepted':
            profiles[row['complete_profile_id']] = profile
    check_discovery(profiles, list_supported_profiles(), get_supported_profile)
    return dict(accepted_generic_runtime_support=sorted(profiles), profiles=[view(r) for r in rows])
