import {canonicalBasin} from './basin.js';

export async function checkedNativeCPC(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x => x.toString(16).padStart(2, '0')).join('');
  if (projection_digest !== '53ecabd6eb43122ea90edc8c6d06f51ef0935967b66aa0dd9039841ef26f37e9' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_cpc_preflight_surface_v1' ||
      value.native_completion_support !== false || value.native_endpoint_verified !== false ||
      value.full_trajectory_runs !== 0 || value.endpoint_expectations_verified !== false ||
      value.source_url !== '/api/native-spark/c-pc/preflight/source')
    throw new Error('Unbound native preflight or changed endpoint scope');
  return value;
}

export function nativeCPCLoader(output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence = 0;
  return async () => {
    const ticket = ++sequence;
    output.replaceChildren(); status.textContent = 'Checking measured C_PC preflight…';
    try {
      const response = await fetcher('/api/native-spark/c-pc/preflight');
      if (!response.ok) throw new Error('Native preflight unavailable');
      const value = await checkedNativeCPC(await response.json());
      if (ticket !== sequence) return;
      const add = (tag, text) => {const e=create(tag); e.textContent=text; output.append(e); return e;};
      add('p', `${value.target_vertices} vertices / ${value.target_edges} edges; ${value.sample_counts.current} current and ${value.sample_counts.reset} reset changing-state steps. FLINT ${value.flint_version}, ${value.flint_threads} thread.`);
      for (const role of ['current', 'reset']) {
        const cost=value.estimate.roles[role];
        add('p', `${role}: mean ${cost.step_seconds.mean.toFixed(3)} s/step; ${cost.horizon}-step planning estimate ${(cost.central_seconds/60).toFixed(1)} minutes, conservative allowance ${(cost.upper_seconds/60).toFixed(1)} minutes.`);
      }
      add('p', `Combined estimate ${(value.estimate.central_seconds/60).toFixed(1)} minutes; upper allowance ${(value.estimate.upper_seconds/60).toFixed(1)} minutes against a ${value.estimate.campaign_cap_seconds/60}-minute cap. This is a planning envelope, not a confidence interval.`);
      add('p', `Measured peak memory ${value.memory.final_peak_mib.toFixed(1)} MiB. Static graph, carrier-domain, decay and certificate reuse verified. Each step has fresh C/Z reads and one same-read writer at 256 bits.`);
      add('p', 'This bounded preflight contains no endpoint run. The 400-step budget is a planning horizon; its endpoint result is published separately in the C_PC campaign.');
      add('p', `${value.tests.count} native tests; full ${value.full_domain_dimension}-dimensional C/Z certificate, including all 46 signed carrier directions.`);
      add('p', `${value.pressure.tests_passed} bounded PC pressure tests; ${value.pressure.mutations} explicit mutation detectors; all ${value.pressure.finite_segment_directions} derivative directions checked. Source/target carrier spaces have 58/46 coordinates.`);
      const pressureLink=add('a', 'Retained C_PC pressure'); pressureLink.href=value.pressure.source_url; pressureLink.target='_blank'; pressureLink.rel='noopener';
      for (const condition of value.stop_conditions) add('p', condition);
      const link=add('a', 'Retained native preflight'); link.href=value.source_url; link.target='_blank'; link.rel='noopener';
      const campaignLink=add('a', 'Native C_PC completion campaign'); campaignLink.href='/api/native-spark/c-pc/campaign';
      status.textContent='Bounded native preflight verified; see separate campaign for endpoints.';
    } catch (error) {
      if (ticket !== sequence) return;
      output.replaceChildren(); status.textContent=String(error);
    }
  };
}

if (typeof document !== 'undefined') document.getElementById('spark-native-cpc-refresh')?.addEventListener('click',
  nativeCPCLoader(document.getElementById('spark-native-cpc-output'), document.getElementById('spark-native-cpc-status')));
