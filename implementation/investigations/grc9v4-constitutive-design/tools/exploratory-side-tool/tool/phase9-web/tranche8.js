import {TRANCHE8_EVIDENCE} from './tranche8-evidence.js';

const canonical = value => JSON.stringify(value, (_, v) => v && typeof v === 'object' && !Array.isArray(v)
  ? Object.fromEntries(Object.keys(v).sort().map(k => [k, v[k]])) : v);

export function checkedTranche8(value) {
  if (canonical(value) !== canonical(TRANCHE8_EVIDENCE))
    throw new Error('Missing, stale or widened Tranche 8 evidence; no fallback');
  return value;
}

export function sourceURL(ref) {
  if (!TRANCHE8_EVIDENCE.source_refs.some(r => r.path === ref.path && r.sha256 === ref.sha256 && r.revision === ref.revision))
    throw new Error('Unindexed source');
  return '/api/tranche8/source?path=' + encodeURIComponent(ref.path);
}

export function renderTranche8(value, container, create = tag => document.createElement(tag)) {
  checkedTranche8(value);
  container.replaceChildren();
  const append = (parent, tag, text) => { const e = create(tag); e.textContent = text; parent.append(e); return e; };
  const link = (parent, ref, label) => { const e = append(parent, 'a', label); e.href = sourceURL(ref); e.target = '_blank'; e.rel = 'noopener'; return e; };
  const details = (parent, label, data) => { const e = append(parent, 'details', ''); append(e, 'summary', label); append(e, 'pre', JSON.stringify(data, null, 2)); };
  const c = value.coverage;
  append(container, 'p', `8.4b: ${c.accepted_cells}/${c.required_cells} accepted history cells; ${c.pending_cells} pending. Parent open. No new support or execution permission.`);
  if (c.executed_pending_cells) append(container, 'p', `${c.executed_pending_cells} additional cells have passing execution evidence pending review and acceptance; they are not accepted coverage.`);
  append(container, 'p', `Check level: ${value.verification.level}. No native trajectory rerun or interval-equation recomputation. Historical 8.3 runs do not certify later code.`);
  append(container, 'h3', 'Shared mechanics and bounded profile integrations');
  for (const row of value.mechanics) {
    const p = append(container, 'p', `${row.work_id}: ${row.scope}. `); link(p, row.acceptance, 'Recorded decision');
  }
  const table = append(container, 'table', '');
  const head = append(table, 'tr', '');
  for (const name of ['Family', '8.3 scope', '8.4b accepted / required', 'Pending', 'Retained sources']) append(head, 'th', name);
  for (const row of c.families) {
    const profile = value.profiles.find(r => r.family === row.family);
    const tr = append(table, 'tr', '');
    append(tr, 'td', row.family); append(tr, 'td', 'Accepted bounded integration');
    append(tr, 'td', `${row.accepted_cells} / ${row.required_cells}`);
    append(tr, 'td', String(row.pending_cells) + (row.executed_pending_cells ? ` (${row.executed_pending_cells} executed; unaccepted)` : ''));
    const td = append(tr, 'td', ''); link(td, profile.review, 'Review');
    if (profile.independent_A_oracle) { append(td, 'span', ' · '); link(td, profile.independent_A_oracle.review, 'A oracle'); }
    details(td, 'Exact subject, domain, schedule, budget and retained claim traces', profile);
  }
  append(container, 'h3', 'Recorded cases: event commit is not case success');
  append(container, 'p', 'C_OS uses bounded dense comparisons; A_OS, C_CI, A_CI, C_PC, A_PC and C_CI_PC also have pointwise interval checks. None is a uniform parameter tube.');
  const supplements = append(container, 'p', 'Expanded A_OS oracle and pressure: ');
  for (const ref of c.oracle_and_pressure) { link(supplements, ref, ref.path.split('/').at(-1)); append(supplements, 'span', ' · '); }
  for (const run of c.runs) {
    const section = append(container, 'details', '');
    append(section, 'summary', `${run.family}: ${run.passed_cases} passed, ${run.incomplete_cases} incomplete — ${run.results.path.split('/').at(-1)}`);
    const p = append(section, 'p', `${run.status}. `); link(p, run.results, 'Exact execution'); append(p, 'span', ' · ');
    link(p, run.inputs, 'Inputs and budgets'); append(p, 'span', ' · ');
    if (run.acceptance) link(p, run.acceptance, 'Separate scoped acceptance');
    else { link(p, run.review, 'Review pending acceptance'); append(p, 'span', ' · No accepted coverage credited.'); }
    if (run.signed_stage_pressure) { append(p, 'span', ' · '); link(p, run.signed_stage_pressure, 'Signed Read-Back/flat checks'); }
    if (run.pc_claim_restrictions) { link(p, run.claim_source, ' PC claim source'); details(section, 'PC claim restrictions', run.pc_claim_restrictions); }
    if (run.stage_evidence) details(section, run.stage_evidence_label || 'Signed reads, W/Z effects and declared chart', run.stage_evidence);
    if (run.numerical_recheck) { append(p, 'span', ' · '); link(p, run.numerical_recheck, 'Independent interval recomputation'); }
    if (run.original_attempt) {
      const original=append(section,'p','Original attempt retained: ');
      link(original,run.original_attempt.results,'Original execution and timeout');
      details(section,'Retained versus new execution',run.execution_partition);
      details(section,'Original incomplete cases — not passing evidence',run.original_attempt.failures);
    }
    for (const row of run.cases) append(section, 'p', `${row.case_id}: ${row.case_passed ? 'CASE PASSED' : 'INCOMPLETE CASE'}; event committed=${row.event_committed}; first failure=${JSON.stringify(row.first_failure)}`);
  }
  append(container, 'h3', 'Larger configurations: preparation is not runtime acceptance');
  append(container, 'p', `Retained probe outcomes: ${JSON.stringify(value.configuration.outcome_counts)}. Forty disabled-profile cells remain Tranche 9 work.`);
  for (const row of value.configuration.families) {
    const p = append(container, 'p', `${row.family}: ${JSON.stringify(row.outcomes)}. Owners: ${row.next_owners.join(', ')}. `);
    link(p, row.configuration, 'Configuration'); append(p, 'span', ' · '); link(p, row.numerical_report, 'Probe report');
  }
  details(container, '8.4 children and remaining owners', c.children);
  details(container, 'Paper/specification/claim associations — no authority promotion', value.scientific_claim_mapping);
  details(container, 'Source identities and exact Git checkpoint', value.source_refs);
}

// Independent of the slower full phase-boundary API; never implies that it passed.
export function tranche8Loader(container, status, fetcher = fetch, create) {
  let generation = 0;
  return async () => {
    const current = ++generation;
    container.replaceChildren(); status.textContent = 'Checking retained Tranche 8 sources…';
    try {
      const response = await fetcher('/api/tranche8', {cache: 'no-store'});
      if (!response.ok) throw new Error('Retained evidence unavailable');
      const value = checkedTranche8(await response.json());
      if (current !== generation) return;
      renderTranche8(value, container, create);
      status.textContent = 'Retained sources checked. Not a numerical rerun or a current phase-boundary pass.';
    } catch (error) {
      if (current !== generation) return;
      container.replaceChildren(); status.textContent = `Unavailable: ${error.message}`;
    }
  };
}

if (typeof document !== 'undefined' && document.querySelector('#tranche8-evidence')) {
  const load = tranche8Loader(document.querySelector('#tranche8-evidence'), document.querySelector('#tranche8-status'));
  document.querySelector('#tranche8-refresh').addEventListener('click', load);
  load();
}
