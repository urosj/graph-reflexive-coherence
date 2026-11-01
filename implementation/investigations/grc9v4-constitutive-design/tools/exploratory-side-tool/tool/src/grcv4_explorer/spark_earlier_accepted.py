"""Accepted shorter endpoints, with immutable initial and research records."""
from pathlib import Path
from .basin import _bound_file
from .canonical import load_json_object, record_digest, digest, file_sha256
from .spark_earlier_sc3_metadata import checked_epoch, need

INV = 'implementation/investigations/grc9v4-constitutive-design/'
BASE = INV + 'evidence/spark-completion/applicability/earlier-closure/'
SOURCE = INV + 'decisions/spark-completion-earlier/Authority.json'
AUTHORITY_DIGEST = '4e515019d17fc6a8699e2a02496017b46b0a7ba73e6369185104da473a6a23c6'
MANIFEST = 'specs/grc-9-v4-spark-completion-earlier-source-manifest.json'
MANIFEST_DIGEST = '87d3f62e11127a61fef7923ef4e87f52753c95e97c3b9518a4b1ccf7726baf82'
LEDGER = BASE + 'EarlierSC3ClaimDebtLedger.json'
LEDGER_DIGEST = 'de2142b92207998271c9fa0ed37367113765a6982b05be4fb5e453c51fac0b30'
RECONCILIATION = 'implementation/phase-9-grcv4/tranche-10/P9-10.5-10.6-SparkEarlierReconciliation.json'
RECONCILIATION_DIGEST = 'a04f729ce86be476a2c70279776e58db577be94eb87b9be85ad4d7569630abb4'
FAMILIES = ['C_OS', 'C_CI', 'C_PC', 'C_CI_PC', 'A_OS']


def sealed(root, path, expected=None):
    value = load_json_object(Path(root) / path)
    actual = record_digest(value, 'record_digest')
    need(value.get('record_digest') == actual and (expected is None or actual == expected),
         'unbound endpoint record: ' + path)
    return value


def spark_earlier_authority(root, side=None):
    root = Path(root)
    checked_epoch(root)
    authority = sealed(root, SOURCE, AUTHORITY_DIGEST)
    manifest = sealed(root, MANIFEST, MANIFEST_DIGEST)
    need(authority['schema'] == 'grc9v4-spark-earlier-authority-v1'
         and authority['status'] == 'accepted_bounded_scientific'
         and manifest['authority_record_digest'] == AUTHORITY_DIGEST, 'endpoint authority identity')
    stages = [r['stage'] for r in manifest['chain']]
    need(stages == ['authority', 'decision', 'proposal', 'paper', 'specification', 'inherited_schema'],
         'endpoint propagation stages')
    for ref in [manifest['predecessor_manifest'], *manifest['chain'], authority['predecessor'],
                authority['acceptance'], authority['design']]:
        _bound_file(root, ref['path'], ref['sha256'])
    ids = [c['equation_contract_id'] for c in authority['contracts']]
    need(manifest['contract_ids'] == ids and len(set(ids)) == 7, 'endpoint contracts')
    for row in manifest['chain']:
        if row['stage'] in ('decision', 'proposal', 'paper', 'specification'):
            text = (root / row['path']).read_text()
            for contract in authority['contracts']:
                header = contract['design_section'] + '\n'
                need(text.count(header) == 1, 'missing or repeated endpoint contract')
                body = text.split(header, 1)[1].split('\n## ', 1)[0].strip()
                need(body == contract['normative_equation_or_contract'], 'endpoint contract drift')
    scope = authority['scope']
    need(scope['adopted_earlier_endpoints'] == FAMILIES and len(scope['scientific_families']) == 10
         and not scope['SC1_reopened'] and not scope['native_completed_spark_support']
         and not scope['hierarchy_support'] and not scope['G4_accepted']
         and scope['additional_event_gain'] == 0 and scope['aggregate_debts_closed'] == []
         and scope['native_support_added'] == [], 'endpoint adoption widened scope')
    acceptance = sealed(root, authority['acceptance']['path'])
    need(acceptance['endpoints'] == authority['endpoints']
         and acceptance['original_execution_flags_preserved']
         and not acceptance['acceptance_runs_new_trajectories'], 'adopted endpoint subjects')
    for ref in acceptance['subjects']:
        _bound_file(root, ref['path'], ref['sha256'])
    # These adapters authenticate the unchanged research reports and all bound sources.
    from .spark_earlier_c import spark_earlier_c_status
    from .spark_aos_earlier import spark_aos_earlier_status
    c_view = spark_earlier_c_status(root, side)
    a_view = spark_aos_earlier_status(root, side)
    c = sealed(root, BASE + 'CEarlierResearch.json')
    proofs = sealed(root, BASE + 'CEarlierProofs.json')
    aos = sealed(root, BASE + 'AOSEarlierResearch.json')
    need(not c['accepted_authority'] and not aos['accepted_authority'], 'research history relabelled')
    need([r['family'] for r in authority['endpoints']] == FAMILIES, 'endpoint family roster')
    for row in authority['endpoints']:
        family = row['family']; is_a = family == 'A_OS'
        need((row['current_entry'], row['current_completion'], row['reset_entry'], row['reset_completion'])
             == ((375, 377, 372, 374) if is_a else (374, 376, 375, 377)), 'adopted endpoint count')
        need(row['full_dimension'] == (30 if is_a else 60 if family in ('C_PC', 'C_CI_PC') else 14)
             and row['ordinary_duration'] == 32 and row['window_beats'] == 2
             and row['window_elapsed'] == 64 and row['supporting_trajectory_steps_after_completion'] == 0
             and row['additional_event_gain'] == row['reset_live_gain'] == 0
             and row['inherited_current_gain'] == 1 and row['original_execution_counts_preserved'],
             'endpoint state, time, tail or gain')
        for role in ('current', 'reset'):
            need(row[role + '_elapsed_target_time'] == 32 * row[role + '_completion'], 'endpoint elapsed time')
            if is_a:
                decision = aos['decisions'][role]
                need((decision['anisotropic_entry'], decision['anisotropic_window_end'])
                     == (row[role + '_entry'], row[role + '_completion']), 'A_OS selected witness')
            else:
                prefix = proofs['prefixes'][family + '/' + role]
                need(prefix['path'].endswith('-prefix.json.xz'), 'C-family selected prefix')
        for ref in (row['research'], row['predecessor_authority']):
            _bound_file(root, ref['path'], ref['sha256'])
    reconciliation = sealed(root, RECONCILIATION, RECONCILIATION_DIGEST)
    for key in ('authority', 'ledger', 'manifest'):
        ref = reconciliation[key]; _bound_file(root, ref['path'], ref['sha256'])
    need(reconciliation['scope'] == scope, 'aggregate reconciliation scope')
    ledger = sealed(root, LEDGER, LEDGER_DIGEST)
    need(ledger['families'] == authority['family_dispositions'], 'endpoint ledger family drift')
    initial = sealed(root, ledger['predecessor_ledger']['path'])
    _bound_file(root, ledger['predecessor_ledger']['path'], ledger['predecessor_ledger']['sha256'])
    need(ledger['claims'][:len(initial['claims'])] == initial['claims']
         and ledger['debts'] == initial['debts'], 'initial claims or debt history changed')
    claims = [{k: v for k, v in r.items() if k != 'source_ref'} for r in ledger['claims'][len(initial['claims']):]]
    need(claims == authority['claims'] and len(claims) == 10, 'endpoint claim reconciliation')
    refs = [dict(path=p, sha256=file_sha256(root / p)) for p in (SOURCE, MANIFEST, LEDGER, RECONCILIATION)]
    refs += [authority['acceptance'], *manifest['chain'], *acceptance['subjects']]
    refs = list({r['path']: dict(path=r['path'], sha256=r['sha256']) for r in refs}.values())
    value = dict(schema='grc9v4_spark_earlier_accepted_surface_v1', authority_record_digest=AUTHORITY_DIGEST,
                 endpoints=authority['endpoints'], scope=scope, review_limits=acceptance['review_limits'],
                 original_research_projections={'C': c_view['projection_digest'], 'A_OS': a_view['projection_digest']},
                 source_refs=refs, check_mode='retained_source_integrity_no_numerical_rerun')
    value['projection_digest'] = digest(value)
    return value


def spark_earlier_source(root, side, path):
    value = spark_earlier_authority(root, side)
    ref = next((r for r in value['source_refs'] if r['path'] == path), None)
    if ref is None:
        raise KeyError('not an indexed adopted-endpoint source')
    return _bound_file(Path(root), path, ref['sha256']).read_bytes(), ref
