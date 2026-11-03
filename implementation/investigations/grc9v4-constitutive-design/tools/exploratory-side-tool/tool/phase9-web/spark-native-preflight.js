import {canonicalBasin} from './basin.js';

export async function checkedNativePreflight(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x => x.toString(16).padStart(2, '0')).join('');
  if (projection_digest !== '05500b7d4c5177389b2594b89640873d61dc3f973db100dbc6838c4a258a7dc9' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_spark_preflight_surface_v1' ||
      value.native_completion_support !== false || value.native_endpoint_verified !== false ||
      value.full_trajectory_runs !== 0 || value.endpoint_expectations_verified !== false ||
      value.source_url !== '/api/native-spark/c-os/preflight/source')
    throw new Error('Unbound native preflight or changed endpoint scope');
  return value;
}

export function nativePreflightLoader(output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence = 0;
  return async () => {
    const ticket = ++sequence;
    output.replaceChildren(); status.textContent = 'Checking measured C_OS preflight…';
    try {
      const response = await fetcher('/api/native-spark/c-os/preflight');
      if (!response.ok) throw new Error('Native preflight unavailable');
      const value = await checkedNativePreflight(await response.json());
      if (ticket !== sequence) return;
      const add = (tag, text) => {const e=create(tag); e.textContent=text; output.append(e); return e;};
      add('p', `${value.target_vertices} vertices / ${value.target_edges} edges; ${value.sample_counts.current} current and ${value.sample_counts.reset} reset changing-state steps. FLINT ${value.flint_version}, ${value.flint_threads} thread.`);
      for (const role of ['current', 'reset']) {
        const cost=value.estimate.roles[role];
        add('p', `${role}: mean ${cost.step_seconds.mean.toFixed(3)} s/step; ${cost.horizon}-step planning estimate ${(cost.central_seconds/60).toFixed(1)} minutes, conservative allowance ${(cost.upper_seconds/60).toFixed(1)} minutes.`);
      }
      add('p', `Combined estimate ${(value.estimate.central_seconds/60).toFixed(1)} minutes; upper allowance ${(value.estimate.upper_seconds/60).toFixed(1)} minutes against a ${value.estimate.campaign_cap_seconds/60}-minute cap. This is a planning envelope, not a confidence interval.`);
      add('p', `Measured peak memory ${value.memory.final_peak_mib.toFixed(1)} MiB. Graph and certificate reuse verified; changing geometry is freshly solved.`);
      add('p', 'Entry/completion 374→376 and reset 375→377 remain unverified. Full campaign has not started.');
      for (const condition of value.stop_conditions) add('p', condition);
      const link=add('a', 'Retained native preflight'); link.href=value.source_url; link.target='_blank'; link.rel='noopener';
      status.textContent='Measured native preflight verified; review pending.';
    } catch (error) {
      if (ticket !== sequence) return;
      output.replaceChildren(); status.textContent=String(error);
    }
  };
}

if (typeof document !== 'undefined') document.getElementById('spark-native-preflight-refresh')?.addEventListener('click',
  nativePreflightLoader(document.getElementById('spark-native-preflight-output'), document.getElementById('spark-native-preflight-status')));
