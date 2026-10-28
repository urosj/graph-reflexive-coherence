export function aosRows(value) {
  if (value.schema !== 'phase9_aos_work_v1' || value.family !== 'A_OS' ||
      value.user_accepted !== false || value.aggregate_closed !== false) {
    throw new Error('Unexpected A_OS work scope');
  }
  if (value.checkpoints.length !== 16 || new Set(value.checkpoints.map(r => r.checkpoint)).size !== 16 ||
      value.checkpoints.some(r => r.user_accepted !== false)) {
    throw new Error('Incomplete A_OS checkpoint scope');
  }
  const evidence = row => {
    const e = row.execution ?? {};
    if (e.original_reset_excluded) return 'Original reset excluded; separate companion passed four native prerequisites';
    if (e.counts) return `${e.counts.bounded_accepted} accepted; ${e.counts.passed_pending_acceptance} pending acceptance; ${e.counts.unselected_not_executed} unselected`;
    if (e.vertices) return `${e.vertices} vertices / ${e.edges} edges; ${e.actual_target_steps} baseline + ${e.covariant_target_steps} covariance steps`;
    if (e.tests) return `${e.tests} tests`;
    if (e.small_tests) return `${e.small_tests} small checks; large replay, both roles`;
    if (e.successful_history_cells) return `${e.successful_history_cells} history cells`;
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
  document.getElementById('aos-refresh')?.addEventListener('click', async () => {
    const status = document.getElementById('aos-status');
    const output = document.getElementById('aos-output');
    output.replaceChildren();
    status.textContent = 'Checking retained A_OS evidence…';
    try {
      const response = await fetch('/api/aos', {cache: 'no-store'});
      const value = await response.json();
      if (!response.ok) throw new Error(value.error ?? 'A_OS evidence unavailable');
      const rows = aosRows(value);
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
        a.href = `/api/aos/source?path=${encodeURIComponent(ref.path)}`;
        a.textContent = ref.path.split('/').at(-1); li.append(a); sources.append(li);
      }
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = `${value.source_refs.length} checked sources`;
      details.append(summary); details.append(sources); output.append(details);
    } catch (error) {
      status.textContent = `A_OS check failed: ${error.message}`;
    }
  });
}
