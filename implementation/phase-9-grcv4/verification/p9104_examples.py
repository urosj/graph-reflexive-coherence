"""P9-10.4 publication bindings and bounded example execution.

--check reads retained outputs and verifies their bindings; it runs no native
trajectory. --run creates a new independently inspectable output directory.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import lzma
from pathlib import Path
import platform
import subprocess

from examples.grc9v4 import fixtures, tour, seeds

ROOT = Path(__file__).resolve().parents[3]
BASE = 'implementation/phase-9-grcv4/'
PATH = BASE+'tranche-10/P9-10.4-Examples.json'
SELF = BASE+'verification/p9104_examples.py'
GUIDE = 'examples/grc9v4/README.md'
RESULTS = ROOT/'examples/grc9v4/results'
SPEC = 'specs/grc-v4-conformance-fixtures.json'
require = tour.require


def sha(raw): return hashlib.sha256(raw).hexdigest()


def seal(value):
    body = {k:v for k,v in value.items() if k != 'record_digest'}
    return dict(body, record_digest=sha(tour.encoded(body)))


def reference(name):
    path = Path(name)
    require(not path.is_absolute() and '..' not in path.parts, 'repository-relative source required')
    return dict(path=path.as_posix(), sha256=sha((ROOT/path).read_bytes()))


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(lzma.decompress(raw) if path.suffix == '.xz' else raw)


def fixture_links():
    bundle = read(fixtures.PATH)
    require(reference(bundle['catalog']['path']) == bundle['catalog'], 'catalog changed')
    catalog = read(ROOT/bundle['catalog']['path'])
    entries = {r['id'] for r in catalog['entries']}
    links = []
    for family in fixtures.FAMILIES:
        row = fixtures.fixture(family)
        provenance = row['provenance']
        require(reference(provenance['path']) == {k:provenance[k] for k in ('path','sha256')}, 'source artifact changed')
        source = read(ROOT/provenance['path'])['evidence']['mixed_snapshot']
        original = source['initial']; inputs = original['inputs']
        cfg = fixtures.configuration(family)
        require(cfg.family.profile_family_id == family and cfg.reference.to_payload() == inputs['reference'], 'reference extraction differs')
        payload = cfg.to_payload()
        for role in ('current', 'reset'):
            require(payload[role] == inputs[role], 'authority extraction differs')
        require(payload['specialization'] == {k:original['specialization'][k] for k in ('resolved','identity_payload')}
            and cfg.budget_target == inputs['Q_target'] and cfg.time == inputs['time']
            and cfg.step_index == inputs['step_index'], 'specialization/budget/clock extraction differs')
        require(row['model_identity'] == original['model_identity'] and row['scientific_digest'] == original['scientific_digest'], 'extraction identity mismatch')
        require(row['expansion'] == next(a['request'] for a in source['journal'] if a['kind']=='expand')
            and row['prefix_step'] == source['journal'][0]['request'], 'saved request extraction differs')
        require(row['catalog_entry'] in entries, 'missing frozen catalog link')
        links.append(dict(family=family, catalog_entry=row['catalog_entry'],
            source=provenance, complete_profile_id=cfg.profile.complete_profile_id,
            model_identity=row['model_identity'], connected_RG2b_successor=family.endswith('RG2b')))
    return links


def validate_run(value, family):
    require(value['schema']=='grc9v4-tutorial-run-v1' and value['family']==family
        and value['lesson']=='all' and not value['user_accepted']
        and not value['full_GRC9V4_conformance'] and not value['G4_accepted'], 'example scope changed')
    r=value['result']
    require(set(r)==set(tour.LESSONS), 'missing lesson')
    evo=r['evolution']; require(len(evo['steps'])==3, 'retained three-step scope changed')
    for step in evo['steps']:
        require(step['transaction']['committed'] is True
            and step['after']['family']==family
            and step['after']['step_index']==step['before']['step_index']+1
            and step['transaction']['observables']['authoritative_current']['consumed_by_continuity'] is True
            and step['fresh_poststate_observables']['authoritative_current']['consumed_by_continuity'] is False,
            'missing positive evolution/consumed-versus-fresh read')
        require(step['after']['reset']==step['before']['reset'], 'ordinary step changed reset history')
        require((step['after']['W_A'] is not None)==family.startswith('A_')
            and (step['after']['Z_4'] is not None)==('PC' in family), 'family authority mismatch')
    for key in ('continuation_equal','duplicate_independent','reset_restored_all_authority',
                'reset_preserved_clock','rebase_restored_new_baseline'):
        require(r['checkpoint'][key] is True,'checkpoint assertion absent')
    e=r['expansion']
    require(e['event']['committed'] and e['target_continuation']['committed']
        and not e['stale_event_rejection']['committed'] and e['full_rollback']
        and len(e['after_event']['vertices'])==17 and len(e['after_event']['edges'])==16
        and len(e['reset_on_target']['C'])==17, 'event/continuation/reset distinction changed')
    require(r['sparks']['topology_unchanged'] and not r['sparks']['completed_spark']
        and r['sparks']['native_postbeat_candidates']==r['sparks']['after_positive_step']['candidate_node_ids'], 'spark observation widened')
    require(r['basin']['exact_replay'] and r['basin']['state_only_replay']
        and r['basin']['old_model_identity']!=r['basin']['new_model_identity'], 'basin version/replay mismatch')
    require(all(r['compatibility'][k]['committed'] for k in ('disable','enable','enabled_continuation'))
        and r['compatibility']['wrong_branch_rejected'], 'compatibility boundary missing')
    require(not r['rejection']['semantic_failure']['committed'] and r['rejection']['full_rollback']
        and r['rejection']['baseline_digest']==r['rejection']['final_digest'], 'rollback mismatch')
    return value


def result_paths():
    expected={*fixtures.FAMILIES,'discovery','migration','seeds'}
    paths=sorted(p for p in RESULTS.iterdir() if p.name.endswith(('.json','.json.xz')))
    require({p.name.split('.')[0] for p in paths}==expected and len(paths)==len(expected), 'result roster differs')
    return paths


def production_sources():
    # Exact tested production preimages; example publication changes no kernel.
    paths=subprocess.check_output(['git','ls-files','src/pygrc'],cwd=ROOT).decode().splitlines()
    return [reference(n) for n in paths if Path(n).suffix in ('.py','.json','.sha256')]


def validate_outputs():
    rows=[]
    for path in result_paths():
        family=path.name.split('.')[0]; value=read(path)
        if family in fixtures.FAMILIES:
            validate_run(value,family)
            rows.append(dict(family=family,lessons=list(tour.LESSONS),
                elapsed_seconds=value['elapsed_seconds'],output=reference(path.relative_to(ROOT))))
        elif family=='discovery':
            require(tour.encoded(value)==tour.encoded(tour.discovery()),'discovery drift')
        elif family=='migration':
            r=value['result']
            require(len(r['routes'])==3 and all(x['result']['committed'] for x in r['routes'])
                and r['full_rollback'] and not r['target_domain_exclusion']['committed'],'migration evidence missing')
        else:
            require(value['exact_charge_preserved'] and value['diagnostic']['assessments'][0]['basin_seed']
                and not value['diagnostic']['assessments'][0]['hybrid_spark_candidate']
                and value['topology_events']==0 and not value['attracting_basin_claimed'], 'seed example widened')
    return sorted(rows,key=lambda r:r['family'])


def publish():
    import flint
    sources=[reference(p.relative_to(ROOT)) for p in sorted((ROOT/'examples/grc9v4').glob('*')) if p.is_file()]
    numerical=validate_outputs()
    spec=read(ROOT/SPEC)
    case_ids=['COMMON-VALID-ORDINARY-STEP','COMMON-NEGATIVE-DURATION','COMMON-ATOMIC-FAILURE',
        'SNAPSHOT-LOAD-REPLAY','RESET-AFTER-ORDINARY','RESET-AFTER-EVENT','HISTORY-DISPOSITION',
        'TARGET-READMISSION-FAILURE','DUPLICATION-INDEPENDENCE']
    require(set(case_ids)<={r['id'] for key in ('common_cases','lifecycle_cases') for r in spec[key]}, 'unknown frozen fixture')
    return seal(dict(schema='p9104-example-publication-v1',status='implemented_pending_acceptance',
        families=sorted(fixtures.FAMILIES),lessons=list(tour.LESSONS),family_runs=numerical,
        fixture_links=fixture_links(),sources=sources,production_sources=production_sources(),
        checker=reference(SELF),outputs=[reference(p.relative_to(ROOT)) for p in result_paths()],
        frozen_fixture_catalog=reference(SPEC),illustrated_fixture_ids=case_ids,
        expansion_contract='GRC9V4-SATURATED-NINE-PORT-COLLISION-FREE',
        expansion_scope='D52 example reuses the accepted recursive specialization; not a rerun of every frozen D30 vector.',
        predecessor_acceptance=reference(BASE+'tranche-10/P9-10.3-Acceptance.json'),
        python=platform.python_version(),python_flint=flint.__version__, exact_backend='flint',
        numerical_policy='legacy_exact_v1',user_accepted=False,P9_10_4_closed=False,
        full_GRC9V4_conformance=False,G4_accepted=False,new_support=[],production_changed=False,
        completed_spark=False,hierarchy_tracking=False,general_ATC=False,
        next_work='Review P9-10.4 publication, then P9-10.5 debt reconciliation and P9-10.6 G4/handoff.'))


def check():
    value=read(ROOT/PATH)
    require(value==seal(value),'publication digest differs')
    current=publish()
    # An integrity check on a different machine need not have the run's Python
    # patch version; these fields describe execution, not admission authority.
    for key in ('python','python_flint'):
        current[key]=value[key]
    require(value==seal(current),'publication inputs, results or scope changed')
    return value


def run(output,workers=10):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        jobs={pool.submit(tour.run,'all',f):f for f in fixtures.FAMILIES}
        for job in as_completed(jobs):
            family=jobs[job]; value=validate_run(job.result(),family)
            tour.write_output(output/(family+'.json.xz'),value)
            print(family+' passed',flush=True)
    tour.write_output(output/'migration.json',tour.run('migration'))
    tour.write_output(output/'seeds.json',seeds.run())
    tour.write_output(output/'discovery.json',tour.discovery())


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check',action='store_true');mode.add_argument('--record',action='store_true')
    mode.add_argument('--run',action='store_true');p.add_argument('--output')
    p.add_argument('--workers',type=int,default=10,choices=range(1,13));a=p.parse_args()
    if a.run:
        if not a.output:p.error('--run requires a new --output directory')
        run(a.output,a.workers)
    elif a.record:
        with (ROOT/PATH).open('x') as f:json.dump(publish(),f,indent=2);f.write('\n')
        print('Publication recorded; pending acceptance.')
    else:
        v=check();print(v['status'],len(v['family_runs']),'families; retained-integrity check, no native rerun')
