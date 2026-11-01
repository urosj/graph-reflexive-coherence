import {canonicalBasin} from './basin.js';

export async function checkedSparkEarlierAccepted(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(n => n.toString(16).padStart(2, '0')).join('');
  if (projection_digest !== '3e3d732016df00e62ebea0b69fb7d12e859af9c8e5be04f0fb3ea3ee94a5b248' || actual !== projection_digest ||
      value.schema !== 'grc9v4_spark_earlier_accepted_surface_v1' ||
      value.scope.native_completed_spark_support !== false || value.scope.G4_accepted !== false ||
      value.scope.additional_event_gain !== 0 || value.endpoints.length !== 5)
    throw new Error('Unbound adopted endpoint evidence or changed scope');
  return value;
}

export function sparkEarlierAcceptedLoader(output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence = 0;
  return async () => {
    const ticket = ++sequence;
    output.replaceChildren(); status.textContent = 'Checking adopted endpoints…';
    try {
      const response = await fetcher('/api/spark-completion/applicability/earlier-accepted');
      if (!response.ok) throw new Error('Adopted endpoint evidence unavailable');
      const value = await checkedSparkEarlierAccepted(await response.json());
      if (ticket !== sequence) return;
      const add = (tag, text, parent=output) => {
        const element = create(tag); element.textContent = text; parent.append(element); return element;
      };
      add('p', 'Primary accepted witnesses at duration 32. Every row includes the full physical state and a positive two-beat window.');
      const table = add('table', ''); const head = add('tr', '', table);
      for (const title of ['Family', 'Current entry → completion', 'Reset entry → completion', 'Elapsed target time (current)', 'Physical dimensions']) add('th', title, head);
      for (const row of value.endpoints) {
        const tr = add('tr', '', table);
        for (const cell of [row.family, `${row.current_entry} → ${row.current_completion}`,
          `${row.reset_entry} → ${row.reset_completion}`, row.current_elapsed_target_time, row.full_dimension]) add('td', String(cell), tr);
      }
      add('p', 'No later supporting evolution is required. These same-event certificates earn no additional gain; reset earns no live gain.');
      const details = add('details', ''); add('summary', 'Initial longer results and retained provenance', details);
      for (const row of value.endpoints) add('p', `${row.family}: initial current completion ${row.initial_current_completion}; ${row.evidence_mode}. Original execution counts are preserved.`, details);
      for (const limit of value.review_limits) add('p', limit, details);
      for (const ref of value.source_refs) {
        if (!/^(implementation|specs)\//.test(ref.path) || ref.path.split('/').includes('..')) throw new Error('Invalid adopted source');
        const link = add('a', ref.path.split('/').at(-1));
        link.href = '/api/spark-completion/applicability/earlier-accepted/source?path=' + encodeURIComponent(ref.path);
        link.target = '_blank'; link.rel = 'noopener'; add('span', ' · ');
      }
      status.textContent = 'Accepted endpoint contracts verified. Native implementation remains separate.';
    } catch (error) {
      if (ticket !== sequence) return;
      output.replaceChildren(); status.textContent = String(error);
    }
  };
}

if (typeof document !== 'undefined') document.getElementById('spark-earlier-accepted-refresh')?.addEventListener('click',
  sparkEarlierAcceptedLoader(document.getElementById('spark-earlier-accepted-output'), document.getElementById('spark-earlier-accepted-status')));
