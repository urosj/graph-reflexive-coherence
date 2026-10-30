export function crg2bRows(value) {
  const accepted = value.user_accepted === true;
  const decision = 'b4c76c8c0cfd206e1951c833276df50aaae93dfb639772d86697079ff4a81a98';
  if (typeof value.user_accepted !== 'boolean' || value.bounded_scope_closed !== accepted ||
      (accepted ? value.stage !== 'bounded_accepted' ||
        value.acceptance?.record_digest !== decision ||
        value.acceptance?.path !== 'implementation/phase-9-grcv4/tranche-9/P9-CRG2b-Acceptance.json' :
        value.acceptance !== null || !['native_execution_in_progress','bounded_native_pass_pending_acceptance'].includes(value.stage))) {
    throw new Error('Unexpected C_RG2b acceptance');
  }
  if (value.schema !== 'phase9_crg2b_work_v2' || value.family !== 'C_RG2b' ||
      value.aggregate_closed !== false || value.research_native_steps !== 0 || value.research_native_events !== 0 ||
      !Array.isArray(value.G3_support_added) || value.G3_support_added.length !== 0 ||
      value.graph_certificates !== 54 || value.prepared_sections.length !== 4 ||
      value.check_level !== 'retained_integrity_only_no_numerical_rerun' ||
      value.remaining_family !== 'A_RG2b' || value.tranche10 !== 'deferred' || value.uniform_trajectory_enclosure !== false ||
      JSON.stringify(value.large_covariance_selected) !== JSON.stringify(['combined','reflect','rotate']) ||
      JSON.stringify(value.large_covariance_deferred) !== JSON.stringify(['edge_order','node_order','relabel','signed','rotate_twice'])) {
    throw new Error('Unexpected C_RG2b research scope');
  }
  const allowed = ['8.4d','8.4e','8.4f','8.4g','8.4h','8.4i','8.5','8.6','tranche8_end','9.1b','9.2','9.3','9.4a','9.4b','9.5','9.6'];
  if (!value.native_execution || !Object.keys(value.native_execution).every(k => allowed.includes(k)) ||
      !Object.values(value.native_execution).every(v => v.outcome === 'passed') ||
      ((accepted || value.stage === 'bounded_native_pass_pending_acceptance') && Object.keys(value.native_execution).length !== allowed.length)) {
    throw new Error('Incomplete native coverage or widened scope');
  }
  if (accepted && (JSON.stringify(value.native_execution['9.3'].counts) !== JSON.stringify({bounded_accepted:36,passed_pending_acceptance:0,unselected_not_executed:4}) ||
      JSON.stringify(value.native_execution['9.3'].execution_counts) !== JSON.stringify({bounded_accepted:32,passed_pending_acceptance:4,unselected_not_executed:4}))) {
    throw new Error('C_RG2b compatibility acceptance drift');
  }
  const expected = ['source/current', 'source/reset', 'target/current', 'target/reset'];
  return value.prepared_sections.map((row, i) => {
    if (`${row.graph}/${row.role}` !== expected[i] ||
        typeof row.section_passed !== 'boolean' || typeof row.exact_real_first_step_positive !== 'boolean' ||
        !Number.isFinite(row.section_error_upper) || row.section_error_upper < 0 ||
        !Number.isFinite(row.exact_real_resource_lower)) throw new Error('Incomplete C_RG2b research subjects');
    return row;
  });
}

if (typeof document !== 'undefined') {
  document.getElementById('crg2b-refresh')?.addEventListener('click', async () => {
    const status = document.getElementById('crg2b-status');
    const output = document.getElementById('crg2b-output');
    output.replaceChildren();
    status.textContent = 'Checking retained C_RG2b evidence…';
    try {
      const response = await fetch('/api/crg2b', {cache:'no-store'});
      const value = await response.json();
      if (!response.ok) throw new Error(value.error ?? 'Evidence unavailable');
      const rows = crg2bRows(value);
      status.textContent = `${value.graph_certificates} research graph certificates; ${Object.keys(value.native_execution).length} native checkpoints passed. ${value.user_accepted ? 'Bounded scope accepted.' : 'Acceptance pending.'} ${value.debt_status}. ${value.next_work}`;
      const table = document.createElement('table');
      const head = table.createTHead().insertRow();
      for (const title of ['Prepared query', 'Section certified', 'Exact-real resource lower bound']) {
        const th = document.createElement('th'); th.scope = 'col'; th.textContent = title; head.append(th);
      }
      const body = table.createTBody();
      for (const row of rows) {
        const tr = body.insertRow();
        for (const text of [`${row.graph}/${row.role}`, row.section_passed ? 'yes' : 'no', row.exact_real_resource_lower]) {
          tr.insertCell().textContent = String(text);
        }
      }
      output.append(table);
      const native = document.createElement('ul');
      for (const [key, row] of Object.entries(value.native_execution)) {
        const li = document.createElement('li');
        const details = document.createElement('details'); const summary = document.createElement('summary');
        summary.textContent = `${key}: ${row.outcome}`;
        const body = document.createElement('pre'); body.textContent = JSON.stringify(row, null, 2);
        details.append(summary, body); li.append(details); native.append(li);
      }
      output.append(native);
      const scope = document.createElement('p');
      scope.textContent = `Large covariance: ${value.large_covariance_selected.join(', ')}. ` +
        `Deferred: ${value.large_covariance_deferred.join(', ')}. ` +
        'Certificates apply at saved inputs; no uniform trajectory enclosure. A_RG2b and Tranche 10 remain outside this result.';
      output.append(scope);
      const sources = document.createElement('ul');
      for (const ref of value.source_refs) {
        const li = document.createElement('li'); const a = document.createElement('a');
        a.href = `/api/crg2b/source?path=${encodeURIComponent(ref.path)}`;
        a.textContent = ref.path.split('/').at(-1); li.append(a); sources.append(li);
      }
      const details = document.createElement('details'); const summary = document.createElement('summary');
      summary.textContent = 'Execution, research and authority sources'; details.append(summary, sources); output.append(details);
    } catch (error) {
      output.replaceChildren(); status.textContent = `C_RG2b check failed: ${error.message}`;
    }
  });
}
