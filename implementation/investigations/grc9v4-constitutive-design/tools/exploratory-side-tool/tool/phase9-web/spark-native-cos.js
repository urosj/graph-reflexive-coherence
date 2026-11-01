import {canonicalBasin} from './basin.js';

export async function checkedNativeCOS(value) {
  const {projection_digest, ...body} = value;
  const raw = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(raw)].map(x => x.toString(16).padStart(2, '0')).join('');
  if (projection_digest !== 'd3851a5178f48de6ca8104062d07f8991d7798a251a18175408ac731f5dfd4f3' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_spark_numerical_surface_v1' ||
      value.native_completion_support !== false || value.native_endpoint_verified !== false ||
      value.user_accepted !== false || value.native_owner_steps !== 0 ||
      value.source_url !== '/api/native-spark/c-os/numerical-bridge/source')
    throw new Error('Unbound native numerical evidence or changed scope');
  return value;
}

export function nativeCOSLoader(output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence = 0;
  return async () => {
    const ticket = ++sequence;
    output.replaceChildren(); status.textContent = 'Checking native numerical evidence…';
    try {
      const response = await fetcher('/api/native-spark/c-os/numerical-bridge');
      if (!response.ok) throw new Error('Native numerical evidence unavailable');
      const value = await checkedNativeCOS(await response.json());
      if (ticket !== sequence) return;
      const add = (tag, text) => { const e = create(tag); e.textContent = text; output.append(e); return e; };
      add('p', `C_OS: ${value.source_vertices} vertices / ${value.source_edges} edges → ${value.target_vertices} vertices / ${value.target_edges} edges; duration ${value.duration}.`);
      add('p', `Exact charge ${value.charge}; full-step error ≤ ${value.error_display} in the certificate norm; strict image margin ${value.margin_display}. Diagnostic evaluation error: ${value.diagnostic_error}.`);
      add('p', `${value.native_kernel_steps} bounded kernel steps checked. Reference caching verified. Numerical bridge awaits review; public completion and endpoint verification are pending.`);
      add('p', `Measured target steps: ${value.timings_seconds.current}s current, ${value.timings_seconds.reset}s reset, ${value.timings_seconds.current_second}s changing current. ${value.timing_scope}.`);
      const link = add('a', 'Retained numerical evidence'); link.href = value.source_url;
      link.target = '_blank'; link.rel = 'noopener';
      status.textContent = 'Numerical evidence verified. Next: certificates and atomic lifecycle.';
    } catch (error) {
      if (ticket !== sequence) return;
      output.replaceChildren(); status.textContent = String(error);
    }
  };
}

if (typeof document !== 'undefined') document.getElementById('spark-native-cos-refresh')?.addEventListener('click',
  nativeCOSLoader(document.getElementById('spark-native-cos-output'), document.getElementById('spark-native-cos-status')));
