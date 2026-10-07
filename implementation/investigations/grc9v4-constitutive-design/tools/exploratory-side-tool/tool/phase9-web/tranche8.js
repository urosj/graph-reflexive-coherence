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
  append(container, 'p', `8.4b: ${c.accepted_cells}/${c.required_cells} accepted history cells; ${c.pending_cells} pending. P9-8.4 remains open. No new support or execution permission.`);
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
  append(container, 'p', 'C_OS uses bounded dense comparisons; A_OS, C_CI, A_CI, C_PC, A_PC, C_CI_PC, A_CI_PC, C_RG2b and A_RG2b also have pointwise interval checks. Both RG2b families retain signed inverse chains and completion-relative section bounds. A_RG2b also checks scaled-log-W state, history lineage and the composed writer’s next read. None is a uniform parameter tube.');
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
    if (run.rg_claim_restrictions) { link(p, run.claim_source, ' RG claim source'); details(section, 'RG completion and C1 claim restrictions', run.rg_claim_restrictions); }
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
  const boundary = c.boundary_contract;
  append(container, 'h3', '8.4c boundary preregistration — no runtime credit');
  append(container, 'p', `${boundary.counts.layouts} layouts across ${boundary.counts.families} families; ${boundary.counts.history_cells} current/reset obligations: ${boundary.counts.new_history_cells} new, ${boundary.counts.reuse_candidates} exact-reuse candidates. ${boundary.counts.executed_cells} executed; ${boundary.counts.accepted_cells} accepted. Matrix and budgets accepted; target-domain and oracle prerequisites remain open.`);
  const boundaryLinks = append(container, 'p', '');
  link(boundaryLinks, boundary.record, 'Full matrix, recipes and authority traces');
  append(boundaryLinks, 'span', ' · '); link(boundaryLinks, boundary.review, 'Boundary review');
  details(container, 'Independent capacity/phase expectations', boundary.layouts);
  details(container, 'All-ten required comparison ceilings — not new target certificates', boundary.families);
  details(container, 'Bounded schedule, retention budget and prerequisites', {schedule:boundary.schedule, retention:boundary.retention, prerequisites:boundary.prerequisites});
  const mechanical = boundary.mechanics;
  append(container, 'h3', '8.4c shared mechanics — accepted mechanical scope only');
  append(container, 'p', `${mechanical.observations.shared_layouts} layouts checked once; ${mechanical.observations.exact_real_resource_maps} exact-real resource maps. All ten receiver routes checked with mocked numerical reads, detection and target construction. No numerical admission or continuation credit; integrity check does not rerun tests.`);
  const mechanicalLinks = append(container, 'p', '');
  link(mechanicalLinks, mechanical.record, 'Completed mechanical checks');
  append(mechanicalLinks, 'span', ' · '); link(mechanicalLinks, mechanical.review, 'Mechanical review and reproduction');
  details(container, 'Shared negatives, outliers and explicitly mocked receiver probes', mechanical.observations);
  for (const run of boundary.family_results) {
    append(container, 'h3', `8.4c ${run.family} — ${run.status}`);
    append(container, 'p', `${run.native_cases} new native cases (${run.passed_cases} passed); ${run.exact_reuse_cases} exact accepted-case reuses. ${run.accepted_cells}/${run.required_cells} accepted history cells; ${run.passing_pending_cells} passing cells pending acceptance. Status is retained integrity only: no dense, interval or native rerun. Comparison scope: ${run.comparison_scope}.`);
    const links = append(container, 'p', '');
    for (const [key, label] of [['inputs','Bound subjects'],['results','Completed operands'],['review','Scope and reproduction'],['acceptance','Scoped acceptance'],['reuse_evidence','Exact historical reuse']]) {
      if (run[key]) { link(links, run[key], label); append(links, 'span', ' · '); }
    }
    for (const row of run.cases) append(container, 'p', `${row.case_id}: ${row.case_passed ? 'CASE PASSED' : 'INCOMPLETE CASE'}; event committed=${row.event_committed}; first failure=${JSON.stringify(row.first_failure)}`);
  }
  for (const oracle of boundary.oracle_preparations) {
    append(container, 'h3', `8.4c ${oracle.family} oracle — ${oracle.status}`);
    const reusedNative = oracle.exact_accepted_target_reuses || 0;
    const summary = reusedNative ? `${oracle.oracle_cases_passed}/${oracle.oracle_cases_required} target expectations available (${oracle.new_oracle_cases} new independent oracle cases; ${reusedNative} exact accepted native target reuses, not new oracle executions)` : `${oracle.oracle_cases_passed}/${oracle.oracle_cases_required} independent oracle expectations pass (${oracle.new_oracle_cases} new, ${oracle.exact_reuse_cases} exact reuses)`;
    append(container, 'p', `${summary}; ${oracle.native_steps} native steps and ${oracle.runtime_cells_closed} runtime cells closed by this oracle. Saved-entry full-formula bounds, not a uniform trajectory bound. Oracle scope ${oracle.oracle_scope_accepted ? 'accepted' : 'pending review'}; native runtime acceptance remains separate and original execution flags are unchanged.`);
    const links=append(container, 'p', '');
    for (const [key,label] of [['inputs','Bound oracle subjects'],['results','Oracle expectations and certificates'],['review','Scope, pressure and reproduction'],['acceptance','Oracle-scope acceptance']]) {
      if (oracle[key]) { link(links,oracle[key],label); append(links,'span',' · '); }
    }
  }
  for (const prepared of boundary.target_preparations) {
    append(container, 'h3', `8.4c ${prepared.family} target preparation — ${prepared.status}`);
    append(container, 'p', `${prepared.passed_cases} new target preparations pass; ${prepared.exact_reuse_cases} exact reused targets. ${prepared.new_native_root_reads} new read-only native joint-root proposals, checked by independent interval equations. ${prepared.topology_events} topology events, ${prepared.native_steps} native steps and ${prepared.runtime_cells_closed} runtime cells closed. Nominal continuation predictions are not a native campaign or a uniform trajectory bound. Status does not rerun roots or interval equations.`);
    const links=append(container, 'p', '');
    for (const [key,label] of [['inputs','Bound C_CI targets'],['results','Joint roots and nominal predictions'],['review','Preparation scope and reproduction']]) {
      link(links,prepared[key],label); append(links,'span',' · ');
    }
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
