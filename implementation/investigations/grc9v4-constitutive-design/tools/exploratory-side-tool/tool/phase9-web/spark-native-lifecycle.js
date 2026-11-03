import {canonicalBasin} from './basin.js';

export async function checkedNativeLifecycle(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x => x.toString(16).padStart(2, '0')).join('');
  if (projection_digest !== 'db243f9f008940609dadea89ff3aeffbaf6483acc67f9e786d962ecfe7a223dd' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_spark_lifecycle_surface_v1' ||
      value.native_completion_support !== false || value.native_endpoint_verified !== false ||
      value.user_accepted !== false || value.full_trajectory_runs !== 0 ||
      value.source_url !== '/api/native-spark/c-os/lifecycle/source')
    throw new Error('Unbound native lifecycle evidence or changed scope');
  return value;
}

export function nativeLifecycleLoader(output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence = 0;
  return async () => {
    const ticket = ++sequence;
    output.replaceChildren(); status.textContent = 'Checking native lifecycle evidence…';
    try {
      const response = await fetcher('/api/native-spark/c-os/lifecycle');
      if (!response.ok) throw new Error('Native lifecycle evidence unavailable');
      const value = await checkedNativeLifecycle(await response.json());
      if (ticket !== sequence) return;
      const add = (tag, text) => { const e=create(tag); e.textContent=text; output.append(e); return e; };
      add('p', `${value.tests_passed} controls passed. Actual public source beats: ${value.actual_public_source_beats}; actual events: ${value.actual_public_events}.`);
      add('p', `Counts describe the canonical source/event fixture. ${value.pressure_tests_passed} additional pressure controls cover independent equations, exact charge, both chiral events and transaction faults. Repeated successful typed delivery is rejected without another beat.`);
      add('p', `Positive window tests: ${value.positive_window_fixture}.`);
      add('p', `Full-domain certificate verified with Arb${value.certificate_precision_bits}; exact rational charge ${value.exact_charge}; duration ${value.duration}.`);
      add('p', 'Duplicate-before-completion, atomic child insertion, late-failure rollback and checkpoint replay checked. Shared accounting applies within one process; global cross-process uniqueness is not claimed.');
      add('p', 'The full native trajectory and its endpoint remain unverified. Next: measured runtime preflight before a long run.');
      const link=add('a', 'Retained native lifecycle checks'); link.href=value.source_url;
      link.target='_blank'; link.rel='noopener';
      status.textContent='Native lifecycle checks verified; review pending.';
    } catch (error) {
      if (ticket !== sequence) return;
      output.replaceChildren(); status.textContent=String(error);
    }
  };
}

if (typeof document !== 'undefined') document.getElementById('spark-native-lifecycle-refresh')?.addEventListener('click',
  nativeLifecycleLoader(document.getElementById('spark-native-lifecycle-output'), document.getElementById('spark-native-lifecycle-status')));
