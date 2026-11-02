import {canonicalBasin} from './basin.js';

export async function checkedNativeAPC(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x => x.toString(16).padStart(2, '0')).join('');
  if (projection_digest !== '1c23a69caaa5edcae663abca7ca274072c03ee41a77115efb4b79a6bc832d917' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_apc_preflight_surface_v1' ||
      value.native_completion_support !== false || value.native_endpoint_verified !== false ||
      value.full_trajectory_runs !== 0 || value.endpoint_expectations_verified !== false ||
      value.source_url !== '/api/native-spark/a-pc/preflight/source')
    throw new Error('Unbound native preflight or changed endpoint scope');
  return value;
}

export function nativeAPCLoader(output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence = 0;
  return async () => {
    const ticket = ++sequence;
    output.replaceChildren(); status.textContent = 'Checking measured A_PC preflight…';
    try {
      const response = await fetcher('/api/native-spark/a-pc/preflight');
      if (!response.ok) throw new Error('Native preflight unavailable');
      const value = await checkedNativeAPC(await response.json());
      if (ticket !== sequence) return;
      const add = (tag, text) => {const e=create(tag); e.textContent=text; output.append(e); return e;};
      add('p', `${value.target_vertices} vertices / ${value.target_edges} edges; ${value.sample_counts.current} current and ${value.sample_counts.reset} reset changing-state steps. FLINT ${value.flint_version}, ${value.flint_threads} thread.`);
      for (const role of ['current', 'reset']) {
        const cost=value.estimate.roles[role];
        add('p', `${role}: mean ${cost.step_seconds.mean.toFixed(3)} s/step; ${cost.horizon}-step planning estimate ${(cost.central_seconds/60).toFixed(1)} minutes, conservative allowance ${(cost.upper_seconds/60).toFixed(1)} minutes.`);
      }
      add('p', `Combined estimate ${(value.estimate.central_seconds/60).toFixed(1)} minutes; upper allowance ${(value.estimate.upper_seconds/60).toFixed(1)} minutes against a ${value.estimate.profiling_target_seconds/60}-minute profiling target. This is a planning envelope, not a confidence interval.`);
      add('p', `Measured peak memory ${value.memory.final_peak_mib.toFixed(1)} MiB. Static graph, weighted fixed-row, decay and certificate reuse verified. Each step has two fresh selected PC reads and two same-read writers, publishing complete C/W/Z together at 256 bits.`);
      add('p', 'This bounded preflight contains no endpoint run. The 400-step count is a planning horizon. Entry and completion remain to be measured in step .5.');
      add('p', `${value.tests.count} native tests; full ${value.full_domain_dimension}-dimensional C/logW/Z certificate, with independent finite-segment checks in every direction at the center and a nonstationary state.`);
      add('p', 'The earlier timing estimate uses the preflight audit path. Re-estimate the complete campaign checking and checkpoint workload before step .5.');
      add('p', 'The selected current consumes incoming W and signed Z; both writers consume that same read. The full derivative includes both H appearances and the inverse-geometry term. Floor crossings and wider conductance domains remain outside this smooth native profile.');
      add('p', `${value.pressure.tests_passed} bounded A_PC pressure tests; ${value.pressure.mutations} mutation detectors and ${value.pressure.measurements.derivatives.segments} finite segments. Both algebraic history probes, frozen-source writers, signed covariance and complete rollback pass.`);
      add('p', 'The pressure oracle uses explicit polynomial multiplication for zero-crossing intervals. Runtime and original preflight evidence remain unchanged; reprofile this checker before .5.');
      const pressureLink=add('a', 'Retained A_PC pressure'); pressureLink.href=value.pressure.source_url; pressureLink.target='_blank'; pressureLink.rel='noopener';
      for (const condition of value.stop_conditions) add('p', condition);
      const link=add('a', 'Retained native preflight'); link.href=value.source_url; link.target='_blank'; link.rel='noopener';
      status.textContent='Bounded native preflight verified; endpoint run remains separate.';
    } catch (error) {
      if (ticket !== sequence) return;
      output.replaceChildren(); status.textContent=String(error);
    }
  };
}

if (typeof document !== 'undefined') document.getElementById('spark-native-apc-refresh')?.addEventListener('click',
  nativeAPCLoader(document.getElementById('spark-native-apc-output'), document.getElementById('spark-native-apc-status')));
