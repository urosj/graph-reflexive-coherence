import {canonicalBasin} from './basin.js';

export async function checkedNativeARG2b(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x => x.toString(16).padStart(2, '0')).join('');
  if (projection_digest !== '2491917f6ee92f35c54f0b9a4e2a74a16627261acbce6b8b84a534c7c02f55a6' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_arg2b_preflight_surface_v1' ||
      value.native_completion_support !== false || value.native_endpoint_verified !== false ||
      value.full_trajectory_runs !== 0 || value.endpoint_expectations_verified !== false ||
      value.source_url !== '/api/native-spark/a-rg2b/preflight/source')
    throw new Error('Unbound native preflight or changed endpoint scope');
  return value;
}

export function nativeARG2bLoader(output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence = 0;
  return async () => {
    const ticket = ++sequence;
    output.replaceChildren(); status.textContent = 'Checking measured A_RG2b preflight…';
    try {
      const response = await fetcher('/api/native-spark/a-rg2b/preflight');
      if (!response.ok) throw new Error('Native preflight unavailable');
      const value = await checkedNativeARG2b(await response.json());
      if (ticket !== sequence) return;
      const add = (tag, text) => {const e=create(tag); e.textContent=text; output.append(e); return e;};
      add('p', `${value.target_vertices} vertices / ${value.target_edges} edges; ${value.sample_counts.current} current and ${value.sample_counts.reset} reset changing-state steps. FLINT ${value.flint_version}, ${value.flint_threads} thread.`);
      for (const role of ['current', 'reset']) {
        const cost=value.estimate.roles[role];
        add('p', `${role}: mean ${cost.mean_audited_seconds.toFixed(3)} s/audited step; ${cost.horizon}-step planning estimate ${(cost.central_seconds/60).toFixed(1)} minutes, conservative allowance ${(cost.upper_seconds/60).toFixed(1)} minutes.`);
      }
      add('p', `Combined estimate ${(value.estimate.central_seconds/60).toFixed(1)} minutes; upper allowance ${(value.estimate.upper_seconds/60).toFixed(1)} minutes against a ${value.estimate.profiling_target_seconds/60}-minute profiling target. This is a planning envelope, not a confidence interval.`);
      add('p', `Measured peak memory ${value.memory.final_peak_mib.toFixed(1)} MiB. Immutable graph, domain, exact-subject section and certificate reuse verified. Each duration-16 beat has two separately admitted section reads and one exact resource/conductance update at 256 bits.`);
      add('p', 'This bounded preflight contains no endpoint run. Research entry 300 and completion 302 remain expectations. Both C_RG2b.5 and A_RG2b.5 are deferred.');
      add('p', `${value.tests.count} native tests; full ${value.full_domain_dimension}-dimensional continuous curved charge-tangent domain, with no supporting trajectory tail.`);
      add('p', 'The selected geometry is a derived Lipschitz section. The proof does not differentiate that section. Every inverse-chain residual and the full tail are checked independently at 768 bits. Additional depth-24 solves cross-check the initial and final samples; the complete proof checker runs on every beat.');
      add('p', 'Re-estimate late-step, audit, evidence and checkpoint costs before the full campaign.');
      add('p', 'The joint inverse includes all C and 64 log W coordinates and the complete fresh-resource writer. H is derived geometry. FLINT matrix derivatives avoid Python loops over every direction.');
      add('p', `${value.pressure.tests_passed} additional bounded pressure tests; ${value.pressure.measurements.mutations.length} rejected faults. The independent audit checks every inverse-history coordinate, manufactured joint chains, writer timing, scaled-history clipping, the shared curve parameter and atomic failures. Both full campaigns remain deferred.`);
      const pressureLink=add('a', 'Retained A_RG2b pressure audit'); pressureLink.href=value.pressure.source_url; pressureLink.target='_blank'; pressureLink.rel='noopener';
      for (const condition of value.stop_conditions) add('p', condition);
      const link=add('a', 'Retained native preflight'); link.href=value.source_url; link.target='_blank'; link.rel='noopener';
      status.textContent='Bounded native preflight verified; endpoint run remains separate.';
    } catch (error) {
      if (ticket !== sequence) return;
      output.replaceChildren(); status.textContent=String(error);
    }
  };
}

if (typeof document !== 'undefined') document.getElementById('spark-native-arg2b-refresh')?.addEventListener('click',
  nativeARG2bLoader(document.getElementById('spark-native-arg2b-output'), document.getElementById('spark-native-arg2b-status')));
