import {canonicalBasin} from './basin.js';

export async function checkedNativeAOS(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x => x.toString(16).padStart(2, '0')).join('');
  if (projection_digest !== '0e8277d63f0f9871d56d6f7d2cd3ce65f8f04091ef913d5a02a4d6091f076869' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_aos_preflight_surface_v1' ||
      value.native_completion_support !== false || value.native_endpoint_verified !== false ||
      value.full_trajectory_runs !== 0 || value.endpoint_expectations_verified !== false ||
      value.source_url !== '/api/native-spark/a-os/preflight/source')
    throw new Error('Unbound native preflight or changed endpoint scope');
  return value;
}

export function nativeAOSLoader(output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence = 0;
  return async () => {
    const ticket = ++sequence;
    output.replaceChildren(); status.textContent = 'Checking measured A_OS preflight…';
    try {
      const response = await fetcher('/api/native-spark/a-os/preflight');
      if (!response.ok) throw new Error('Native preflight unavailable');
      const value = await checkedNativeAOS(await response.json());
      if (ticket !== sequence) return;
      const add = (tag, text) => {const e=create(tag); e.textContent=text; output.append(e); return e;};
      add('p', `${value.target_vertices} vertices / ${value.target_edges} edges; ${value.sample_counts.current} current and ${value.sample_counts.reset} reset changing-state steps. FLINT ${value.flint_version}, ${value.flint_threads} thread.`);
      for (const role of ['current', 'reset']) {
        const cost=value.estimate.roles[role];
        add('p', `${role}: mean ${cost.step_seconds.mean.toFixed(3)} s/step; ${cost.horizon}-step planning estimate ${(cost.central_seconds/60).toFixed(1)} minutes, conservative allowance ${(cost.upper_seconds/60).toFixed(1)} minutes.`);
      }
      add('p', `Combined estimate ${(value.estimate.central_seconds/60).toFixed(1)} minutes; upper allowance ${(value.estimate.upper_seconds/60).toFixed(1)} minutes against a ${value.estimate.profiling_target_seconds/60}-minute profiling target. This is a planning envelope, not a confidence interval.`);
      add('p', `Measured peak memory ${value.memory.final_peak_mib.toFixed(1)} MiB. Static graph, weighted fixed-row, decay and certificate reuse verified. Each step has two fresh full-state OS reads and one same-read conductance writer at 256 bits.`);
      add('p', 'This bounded preflight contains no endpoint run. The 400-step count is a planning horizon. Step .5 remains unrun.');
      add('p', `${value.tests.count} native tests; full ${value.full_domain_dimension}-dimensional C/logW certificate, with all 58 signed source/target conductance probes.`);
      add('p', 'The earlier timing estimate uses the preflight audit path. Re-estimate the complete campaign checking and checkpoint workload before step .5.');
      add('p', `${value.pressure.tests_passed} bounded W causal-loop pressure tests; ${value.pressure.mutations} explicit semantic mutation detectors. Unequal weighted rows, zero-current writing, next-read feedback, full C/logW derivatives and lossless edge lineage pass.`);
      add('p', 'The native Frobenius split bound is a sufficient certificate of the spectral condition. Floor crossings and wider conductance domains remain outside this smooth native profile.');
      const pressureLink=add('a', 'Retained A_OS pressure'); pressureLink.href=value.pressure.source_url; pressureLink.target='_blank'; pressureLink.rel='noopener';
      for (const condition of value.stop_conditions) add('p', condition);
      const link=add('a', 'Retained native preflight'); link.href=value.source_url; link.target='_blank'; link.rel='noopener';
      status.textContent='Bounded native preflight verified; endpoint campaign remains pending.';
    } catch (error) {
      if (ticket !== sequence) return;
      output.replaceChildren(); status.textContent=String(error);
    }
  };
}

if (typeof document !== 'undefined') document.getElementById('spark-native-aos-refresh')?.addEventListener('click',
  nativeAOSLoader(document.getElementById('spark-native-aos-output'), document.getElementById('spark-native-aos-status')));
