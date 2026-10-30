export function arg2bRows(value) {
  const accepted = value.user_accepted === true;
  const decision = '254cdc1d64fba737b2c3e4cc659c3ea44271eed7f21e48167899738434dd4c14';
  if (typeof value.user_accepted !== 'boolean' || value.bounded_scope_closed !== accepted ||
      (accepted ? value.stage !== 'bounded_accepted' || value.acceptance?.record_digest !== decision ||
        value.acceptance?.path !== 'implementation/phase-9-grcv4/tranche-9/P9-ARG2b-Acceptance.json' :
        value.acceptance !== null || value.stage !== 'bounded_native_pass_pending_acceptance')) {
    throw new Error('Unexpected A_RG2b acceptance');
  }
  if (value.schema !== 'phase9_arg2b_work_v1' || value.family !== 'A_RG2b' ||
      value.aggregate_closed !== false || value.research_native_steps !== 0 || value.research_native_events !== 0 ||
      !Array.isArray(value.G3_support_added) || value.G3_support_added.length !== 0 ||
      value.graph_certificates !== 54 || value.prepared_sections.length !== 4 ||
      value.check_level !== 'retained_integrity_only_no_numerical_rerun' ||
      value.remaining_family !== null || value.tranche10 !== 'deferred' || value.uniform_trajectory_enclosure !== false ||
      JSON.stringify(value.large_covariance_selected) !== JSON.stringify(['combined','reflect','rotate']) ||
      JSON.stringify(value.large_covariance_deferred) !== JSON.stringify(['edge_order','node_order','relabel','signed','rotate_twice'])) {
    throw new Error('Unexpected A_RG2b research scope');
  }
  const allowed = ['8.4d','8.4e','8.4f','8.4g','8.4h','8.4i','8.5','8.6','tranche8_end','9.1b','9.2','9.3','9.4a','9.4b','9.5','9.6'];
  if (!value.native_execution || !Object.keys(value.native_execution).every(k => allowed.includes(k)) ||
      !Object.values(value.native_execution).every(v => v.outcome === 'passed') ||
      ((accepted || value.stage === 'bounded_native_pass_pending_acceptance') && Object.keys(value.native_execution).length !== allowed.length)) {
    throw new Error('Incomplete native coverage or widened scope');
  }
  const counts = value.native_execution['9.3'].counts;
  if (counts.bounded_accepted !== (accepted ? 40 : 36) || counts.passed_pending_acceptance !== (accepted ? 0 : 4) || counts.unselected_not_executed !== 0 ||
      value.original_reset_exclusion_preserved !== true || value.D94_componentwise_frontier_certificate !== true) throw new Error('A_RG2b scope drift');
  if (accepted && JSON.stringify(value.native_execution['9.3'].execution_counts) !==
      JSON.stringify({bounded_accepted:36,passed_pending_acceptance:4,unselected_not_executed:0})) {
    throw new Error('A_RG2b original execution counts changed');
  }
  if (value.tranches89_closeout) {
    const closure = value.tranches89_closeout;
    if (!accepted || closure.record_digest !== '3c198c83641fac16dc7de41086582c0b7824070e4144d3af11301ae5f0d8f8bc' ||
        closure.schema !== 'phase9_tranches89_closeout_view_v1' ||
        closure.path !== 'implementation/phase-9-grcv4/tranche-9/P9-Tranches8-9-AllTenAcceptance.json' ||
        closure.tranche8_closed !== true || closure.tranche9_closed !== true ||
        closure.user_accepted !== true || closure.aggregate_closed !== true ||
        closure.full_GRC9V4_conformance !== false || closure.G4_accepted !== false ||
        JSON.stringify(closure.families) !== JSON.stringify(['A_CI','A_CI_PC','A_OS','A_PC','A_RG2b','C_CI','C_CI_PC','C_OS','C_PC','C_RG2b']) ||
        closure.compatibility_counts.bounded_accepted !== 40 ||
        closure.compatibility_counts.passed_pending_acceptance !== 0 ||
        closure.compatibility_counts.unselected_not_executed !== 0 ||
        closure.optional_completion !== 'unselected_deferred_not_a_closure_blocker') {
      throw new Error('Tranches 8–9 closure scope drift');
    }
  }
  const expected = ['source/current', 'source/reset', 'target/current', 'target/reset'];
  return value.prepared_sections.map((row, i) => {
    if (`${row.graph}/${row.role}` !== expected[i] ||
        typeof row.section_passed !== 'boolean' || typeof row.exact_real_first_step_positive !== 'boolean' ||
        !Number.isFinite(row.section_error_upper) || row.section_error_upper < 0 ||
        !Number.isFinite(row.exact_real_resource_lower)) throw new Error('Incomplete A_RG2b research subjects');
    return row;
  });
}

if (typeof document !== 'undefined') {
  document.getElementById('arg2b-refresh')?.addEventListener('click', async () => {
    const status = document.getElementById('arg2b-status');
    const output = document.getElementById('arg2b-output');
    output.replaceChildren();
    status.textContent = 'Checking retained A_RG2b evidence…';
    try {
      const response = await fetch('/api/arg2b', {cache:'no-store'});
      const value = await response.json();
      if (!response.ok) throw new Error(value.error ?? 'Evidence unavailable');
      const rows = arg2bRows(value);
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
        'Certificates apply at saved inputs; no uniform trajectory enclosure. Tranche 10 remains outside this result.';
      output.append(scope);
      const sources = document.createElement('ul');
      for (const ref of value.source_refs) {
        const li = document.createElement('li'); const a = document.createElement('a');
        a.href = `/api/arg2b/source?path=${encodeURIComponent(ref.path)}`;
        a.textContent = ref.path.split('/').at(-1); li.append(a); sources.append(li);
      }
      const details = document.createElement('details'); const summary = document.createElement('summary');
      summary.textContent = 'Execution, research and authority sources'; details.append(summary, sources); output.append(details);
    } catch (error) {
      output.replaceChildren(); status.textContent = `A_RG2b check failed: ${error.message}`;
    }
  });
}
