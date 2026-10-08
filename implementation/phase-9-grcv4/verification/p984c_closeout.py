"""Reconcile already checked/accepted boundary evidence; never rerun numerics.

Call only after authenticating the contract, family manifests, runtime status
and separate review decisions. This adds exact cross-family coverage checks.
"""
import hashlib
import json

BASE = 'implementation/phase-9-grcv4/tranche-8/'
RECORD = BASE + 'P9-8.4c-Closeout.json'
REVIEW = BASE + 'P9-8.4c-CloseoutReview.md'
FAMILIES = {'C_OS', 'A_OS', 'C_CI', 'A_CI', 'C_PC', 'A_PC',
            'C_CI_PC', 'A_CI_PC', 'C_RG2b', 'A_RG2b'}


def require(ok, message):
    if not ok:
        raise ValueError('8.4c closeout: ' + message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False).encode()).hexdigest()


def unique(rows, key, label):
    values = {row[key]: row for row in rows}
    require(len(values) == len(rows), 'duplicate ' + label)
    return values


def reconcile(contract, view, manifests):
    """Return a compact exact-coverage record from authenticated inputs."""
    require(contract['user_accepted'] is False and contract['aggregate_closed'] is False,
            'original planning flags changed')
    require(view['contract_accepted'] is True, 'contract not accepted')
    mechanics = view['mechanics']
    require(mechanics['status'] == 'accepted_shared_mechanics'
            and mechanics['numerical_history_credit'] == 0
            and mechanics['committed_events'] == 0, 'mechanics scope changed')
    require(mechanics['acceptance']['anchor'] == 'scoped-user-acceptance', 'mechanics decision missing')
    families = unique(view['family_results'], 'family', 'family')
    require(set(families) == set(manifests) == FAMILIES, 'all ten families required')
    required = unique(contract['cells'], 'id', 'required cell')
    cases = unique(contract['cases'], 'id', 'required case')
    require(len(required) == 640 and len(cases) == 320, 'required population changed')
    covered, rows = [], []
    for family in sorted(FAMILIES):
        row, manifest = families[family], manifests[family]
        require(row['status'] == 'accepted_bounded' and row['accepted_cells'] == 64
                and row['required_cells'] == 64 and row['passing_pending_cells'] == 0,
                'unaccepted family ' + family)
        require(row['acceptance'] == {**row['review'], 'anchor': 'scoped-user-acceptance'},
                'separate review identity changed')
        require(manifest['user_accepted'] is False and manifest['aggregate_closed'] is False,
                'original execution flags changed')
        subjects = unique(manifest['cases'], 'case_id', 'manifest subject')
        expected = {k: v for k, v in cases.items() if v['family'] == family}
        require(set(subjects) == set(expected) and len(subjects) == 32, 'subject coverage mismatch')
        reuse = unique(manifest['exact_reuse'], 'case_id', 'reuse')
        expected_reuse = {k: v['reuse_case_id'] for k, v in expected.items() if v['reuse_case_id']}
        # A_OS preregistration names the oracle; native acceptance names its
        # checked runtime companion. Keep both identities visible in closeout.
        runtime_reuse = {k: v.replace('P984B-AOS-ORACLE-', 'P984B-AOS-RUNTIME-')
                         if family == 'A_OS' else v for k, v in expected_reuse.items()}
        require({k: v['previous_case_id'] for k, v in reuse.items()} == runtime_reuse
                and len(reuse) == 2, 'exact historical reuse identity changed')
        observed = unique(row['cases'], 'case_id', 'executed case')
        require(set(observed) == set(subjects) - set(reuse) and len(observed) == 30,
                'new execution coverage mismatch')
        require(all(v['case_passed'] is True and v['event_committed'] is True
                    and v['first_failure'] is None for v in observed.values()), 'incomplete execution')
        require(row['native_cases'] == row['passed_cases'] == 30 and row['exact_reuse_cases'] == 2,
                'execution count mismatch')
        for name, subject in subjects.items():
            binding = subject['coverage_binding']
            require(binding['record_digest'] == contract['record_digest'], 'matrix binding drift')
            want = [name + '::' + role for role in ('current', 'reset')]
            require(binding['cell_ids'] == want, 'missing, duplicate or foreign history role')
            require(subject.get('family', family) == family, 'subject family drift')
            for cell in want:
                require(cell in required and required[cell]['case_id'] == name
                        and required[cell]['family'] == family
                        and required[cell]['role'] == cell.rsplit('::', 1)[1], 'required role drift')
            covered.extend(want)
        rows.append(dict(family=family, accepted_cells=64, new_cases=30, exact_reuse_cases=2,
                         comparison_scope=row['comparison_scope'],
                         reuse_links=[dict(case_id=k, planned_subject=expected_reuse[k],
                                           accepted_runtime_subject=runtime_reuse[k]) for k in sorted(reuse)],
                         **{k: row[k] for k in ('inputs', 'results', 'acceptance', 'reuse_evidence')}))
    require(len(covered) == len(set(covered)) == 640 and set(covered) == set(required),
            'missing, duplicate or extra history cells')
    result = dict(schema='p984c_closeout_v1', work_id='P9-8.4c', date='2026-10-08',
        status='accepted_bounded', aggregate_closed=True, required_cells=640,
        accepted_cells=640, pending_cells=0, new_history_cells=600, exact_reused_history_cells=40,
        new_cases=300, exact_reused_cases=20, coverage_digest=digest(sorted(covered)),
        contract=view['record'], contract_acceptance=view['acceptance'],
        mechanics={k: mechanics[k] for k in ('record', 'acceptance', 'scope')}, families=rows,
        native_trajectories_rerun=False, interval_equations_recomputed=False,
        scope='named_capacity_and_phase_boundaries_only',
        remaining=['P9-8.4' + c for c in 'defghi'] + ['P9-8.5', 'P9-8.6'],
        whole_8_4_closed=False, new_public_support=[], arbitrary_graph_support=False)
    result['record_digest'] = digest(result)
    return result
