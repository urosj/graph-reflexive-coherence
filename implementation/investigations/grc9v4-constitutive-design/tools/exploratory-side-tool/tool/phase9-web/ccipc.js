export function ccipcRows(value) {
  const checkpoints = ['8.4d', '8.4e', '8.4f', '8.4g', '8.4h', '8.4i', '8.5', '8.6',
    'tranche8_end', '9.1b', '9.2', '9.3', '9.4a', '9.4b', '9.5', '9.6'];
  if (value.schema !== 'phase9_ccipc_work_v1' || value.family !== 'C_CI_PC' ||
      typeof value.user_accepted !== 'boolean' || value.aggregate_closed !== false) {
    throw new Error('Unexpected C_CI_PC work scope');
  }
  if (value.user_accepted !== false) throw new Error('C_CI+PC acceptance is pending');
  const accepted = false;
  if (value.checkpoints.length !== 16 ||
      value.checkpoints.some((r, i) => r.checkpoint !== checkpoints[i] || r.user_accepted !== accepted ||
        !(accepted ? ['bounded_accepted'] : ['pending', 'passed_pending_acceptance']).includes(r.state))) {
    throw new Error('Incomplete C_CI_PC checkpoint scope');
  }
  const evidence = row => {
    const e = row.execution ?? {};
    if (e.original_target_roles_excluded) return 'Original target excluded; prior split failed exact charge; charge-preserving companion selected';
    if (e.counts) return `${e.counts.bounded_accepted} accepted; ${e.counts.passed_pending_acceptance} pending acceptance; ${e.counts.unselected_not_executed} unselected`;
    if (e.vertices) return `${e.vertices} vertices / ${e.edges} edges; ${e.actual_target_steps} baseline + ${e.covariant_target_steps} covariance steps; ${e.large_covariance_deferred_unexecuted.length} large cases deferred`;
    if (e.tests) return `${e.tests} tests`;
    if (e.small_tests) return `${e.small_tests} small checks; large replay, both roles`;
    if (e.successful_history_cells) return `${e.successful_history_cells} history cells`;
    if (e.required_history_cells) return `${e.required_history_cells} history cells`;
    if (e.source) return 'Exact source and target identities; inherited support limits';
    return e.handoff ?? e.conformance ?? e.bounded_execution ?? e.status ?? 'See checked sources';
  };
  return value.checkpoints.map(row => ({
    checkpoint: row.checkpoint,
    state: row.state,
    evidence: evidence(row),
    accepted: row.user_accepted,
  }));
}

if (typeof document !== 'undefined') {
  document.getElementById('ccipc-refresh')?.addEventListener('click', async () => {
    const status = document.getElementById('ccipc-status');
    const output = document.getElementById('ccipc-output');
    output.replaceChildren();
    status.textContent = 'Checking retained C_CI_PC evidence…';
    try {
      const response = await fetch('/api/ccipc', {cache: 'no-store'});
      const value = await response.json();
      if (!response.ok) throw new Error(value.error ?? 'C_CI_PC evidence unavailable');
      const rows = ccipcRows(value);
      status.textContent = value.next_work;
      const table = document.createElement('table');
      const head = table.createTHead().insertRow();
      for (const title of ['Checkpoint', 'Execution', 'Evidence', 'User accepted']) {
        const th = document.createElement('th'); th.scope = 'col'; th.textContent = title; head.append(th);
      }
      const body = table.createTBody();
      for (const row of rows) {
        const tr = body.insertRow();
        for (const value of [row.checkpoint, row.state, row.evidence, row.accepted ? 'yes' : 'no']) {
          tr.insertCell().textContent = String(value);
        }
      }
      output.append(table);
      const sources = document.createElement('ul');
      for (const ref of value.source_refs) {
        const li = document.createElement('li'); const a = document.createElement('a');
        a.href = `/api/ccipc/source?path=${encodeURIComponent(ref.path)}`;
        a.textContent = ref.path.split('/').at(-1); li.append(a); sources.append(li);
      }
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = `${value.source_refs.length} checked sources`;
      details.append(summary); details.append(sources); output.append(details);
    } catch (error) {
      status.textContent = `C_CI_PC check failed: ${error.message}`;
    }
  });
}
