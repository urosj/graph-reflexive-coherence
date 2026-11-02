import {canonicalBasin} from './basin.js';

export async function checkedNativeCCI(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x => x.toString(16).padStart(2, '0')).join('');
  if (projection_digest !== 'bf6adc7b96e57d0585dc0137a5fe4f9d0be3039be99274f8a7cdca0740226424' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_cci_preflight_surface_v1' ||
      value.native_completion_support !== false || value.native_endpoint_verified !== false ||
      value.full_trajectory_runs !== 0 || value.endpoint_expectations_verified !== false ||
      value.source_url !== '/api/native-spark/c-ci/preflight/source')
    throw new Error('Unbound native preflight or changed endpoint scope');
  return value;
}

export function nativeCCILoader(output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence = 0;
  return async () => {
    const ticket = ++sequence;
    output.replaceChildren(); status.textContent = 'Checking measured C_CI preflight…';
    try {
      const response = await fetcher('/api/native-spark/c-ci/preflight');
      if (!response.ok) throw new Error('Native preflight unavailable');
      const value = await checkedNativeCCI(await response.json());
      if (ticket !== sequence) return;
      const add = (tag, text) => {const e=create(tag); e.textContent=text; output.append(e); return e;};
      add('p', `${value.target_vertices} vertices / ${value.target_edges} edges; ${value.sample_counts.current} current and ${value.sample_counts.reset} reset changing-state steps. FLINT ${value.flint_version}, ${value.flint_threads} thread.`);
      for (const role of ['current', 'reset']) {
        const cost=value.estimate.roles[role];
        add('p', `${role}: mean ${cost.step_seconds.mean.toFixed(3)} s/step; ${cost.horizon}-step planning estimate ${(cost.central_seconds/60).toFixed(1)} minutes, conservative allowance ${(cost.upper_seconds/60).toFixed(1)} minutes.`);
      }
      add('p', `Combined estimate ${(value.estimate.central_seconds/60).toFixed(1)} minutes; upper allowance ${(value.estimate.upper_seconds/60).toFixed(1)} minutes against a ${value.estimate.campaign_cap_seconds/60}-minute cap. This is a planning envelope, not a confidence interval.`);
      add('p', `Measured peak memory ${value.memory.final_peak_mib.toFixed(1)} MiB. Static graph/root-domain and certificate reuse verified; both joint roots are freshly certified per step at 256 bits.`);
      add('p', 'Entry/completion 374→376 and reset 375→377 remain unverified. Full campaign has not started.');
      add('p', `${value.pressure.tests_passed} bounded CI pressure tests; ${value.pressure.root_mutations} rehashed root mutations; all ${value.pressure.finite_segment_directions} charge directions checked.`);
      const pressureLink=add('a', 'Retained C_CI pressure'); pressureLink.href=value.pressure.source_url; pressureLink.target='_blank'; pressureLink.rel='noopener';
      for (const condition of value.stop_conditions) add('p', condition);
      const link=add('a', 'Retained native preflight'); link.href=value.source_url; link.target='_blank'; link.rel='noopener';
      status.textContent='Measured native preflight verified; review pending.';
    } catch (error) {
      if (ticket !== sequence) return;
      output.replaceChildren(); status.textContent=String(error);
    }
  };
}

if (typeof document !== 'undefined') document.getElementById('spark-native-cci-refresh')?.addEventListener('click',
  nativeCCILoader(document.getElementById('spark-native-cci-output'), document.getElementById('spark-native-cci-status')));
