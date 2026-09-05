export function checkedStatus(value) {
  if (value?.schema !== "phase9_governance_status_v1" || value.output_class !== "implementation_verification_status_not_forensic_trace") throw new Error("Unrecognized verification status");
  if (value.runtime_authorized !== false || value.P9_G1_accepted !== false || !Array.isArray(value.accepted_generic_runtime_support) || value.accepted_generic_runtime_support.length !== 0 || !Array.isArray(value.admitted_specialization_support_sets) || value.admitted_specialization_support_sets.length !== 0) throw new Error("Unverified runtime authority or support");
  if (!['passed', 'failed_closed'].includes(value.current_boundary)) throw new Error("Unknown boundary disposition");
  if (!['not_current', 'recorded_pass_matching_current_inputs'].includes(value.recorded_full_verification)) throw new Error("Unknown recorded evidence disposition");
  if (value.current_boundary !== 'passed' && value.recorded_full_verification !== 'not_current') throw new Error("Failed boundary cannot retain a passing receipt");
  if (value.current_boundary === 'passed') {
    if (!/^[0-9a-f]{64}$/.test(value.policy_digest) || !Array.isArray(value.source_refs) || !value.source_refs.length || !value.source_refs.every(r => typeof r.path === 'string' && /^[0-9a-f]{64}$/.test(r.sha256))) throw new Error('Missing verified source bindings');
    if (!Array.isArray(value.iterations) || value.iterations.length !== 2 || !value.iterations.every((r, i) => r.iteration_id === ['P9-1.7', 'P9-1.8'][i] && ['in_progress', 'implemented_and_verified'].includes(r.status) && r.reviewer_decision === 'pending_user_review')) throw new Error('Invalid leaf authority');
  }
  return value;
}

// This is the sorted-key JSON format of planning status, not the V4 runtime codec.
export function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value !== null && typeof value === 'object') return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(',')}}`;
  return JSON.stringify(value);
}
export async function verifiedStatus(value) {
  checkedStatus(value);
  const { status_digest, ...body } = value;
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical(body)));
  const actual = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
  if (actual !== status_digest) throw new Error('Status digest mismatch');
  if (!Array.isArray(value.source_refs) || !Array.isArray(value.iterations)) throw new Error('Missing source or leaf records');
  return value;
}

let refreshGeneration = 0;
async function refresh() {
  const generation = ++refreshGeneration;
  const status = document.querySelector('#status');
  const button = document.querySelector('#download');
  button.disabled = true;
  document.querySelector('#boundary').textContent = 'Not verified';
  document.querySelector('#recorded').textContent = 'Not current';
  document.querySelector('#sources').replaceChildren();
  document.querySelector('#iterations').textContent = 'No verified leaf results.';
  document.querySelector('#policy').textContent = '';
  document.querySelector('#source-meaning').textContent = 'Not verified.';
  status.textContent = 'Checking current inputs…';
  try {
    const response = await fetch('/api/status', { cache: 'no-store' });
    if (!response.ok) throw new Error('Verification status unavailable');
    const value = await verifiedStatus(await response.json());
    if (generation !== refreshGeneration) return;
    if (value.current_boundary !== 'passed') throw new Error(value.error || 'Current inputs failed verification');
    status.classList.remove('error');
    status.textContent = 'Current planning checks passed. Runtime remains unauthorized.';
    document.querySelector('#boundary').textContent = 'Passed · current bytes';
    document.querySelector('#recorded').textContent = value.recorded_full_verification === 'not_current' ? 'Not current · rerun CLI' : 'Recorded pass · matching inputs';
    document.querySelector('#policy').textContent = `Policy digest: ${value.policy_digest}`;
    document.querySelector('#ceiling').textContent = value.claim_ceiling;
    if (value.source_meaning) document.querySelector('#source-meaning').textContent = `${value.source_meaning.specification_authority} specification; ${value.source_meaning.association_count}/${value.source_meaning.association_denominator} source contract associations remain ${value.source_meaning.forensic_support_disposition}. These are source associations, not runtime tests. ${value.source_meaning.pending_source_obligations} source obligations remain pending.`;
    const sources = document.querySelector('#sources');
    for (const ref of value.source_refs) {
      const dt = document.createElement('dt'); dt.textContent = ref.path;
      const dd = document.createElement('dd'); dd.textContent = ref.sha256;
      sources.append(dt, dd);
    }
    const iterations = document.querySelector('#iterations'); iterations.replaceChildren();
    for (const row of value.iterations) {
      const p = document.createElement('p'); p.textContent = `${row.iteration_id}: ${row.status} — ${row.reviewer_decision}`; iterations.append(p);
    }
    button.disabled = false;
    button.onclick = () => {
      const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
      const a = document.createElement('a'); a.href = url; a.download = 'phase9-verification-status.json'; a.click(); URL.revokeObjectURL(url);
    };
  } catch (error) {
    if (generation !== refreshGeneration) return;
    status.classList.add('error'); status.textContent = `Held: ${error.message}`;
  }
}

export async function verifiedProbe(value, requested) {
  if (value?.schema !== 'phase9_pressure_projection_v1' || value.output_class !== 'isolated_probe_not_current_tree_admission' || value.case_id !== requested) throw new Error('Wrong probe schema or exact subject');
  if (!['admitted','rejected','held','unverifiable'].includes(value.candidate_decision) || !['passed','failed'].includes(value.assertion_result)) throw new Error('Unknown probe outcome');
  if (value.project_effect?.runtime_authorized !== false || value.project_effect?.P9_G1_accepted !== false || value.project_effect?.scientific_promotion !== false) throw new Error('Probe cannot grant authority');
  const {projection_digest, ...body} = value;
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical(body)));
  const actual = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2,'0')).join('');
  if (actual !== projection_digest) throw new Error('Probe digest mismatch');
  return value;
}
let probeGeneration = 0;
async function loadProbe() {
  const generation = ++probeGeneration;
  const id = document.querySelector('#probe').value;
  const button = document.querySelector('#probe-download'); button.disabled = true;
  document.querySelector('#probe-candidate').textContent = 'Not loaded';
  document.querySelector('#probe-assertion').textContent = 'Not loaded';
  document.querySelector('#probe-subject').textContent = '';
  document.querySelector('#probe-status').textContent = 'Loading recorded evidence…';
  try {
    const response = await fetch(`/api/probe?case_id=${encodeURIComponent(id)}`, {cache:'no-store'});
    if (!response.ok) throw new Error('Probe evidence unavailable or stale');
    const value = await verifiedProbe(await response.json(), id);
    if (generation !== probeGeneration || document.querySelector('#probe').value !== id) return;
    document.querySelector('#probe-status').textContent = 'Recorded isolated probe · no live permission created';
    document.querySelector('#probe-candidate').textContent = value.candidate_decision;
    document.querySelector('#probe-assertion').textContent = value.assertion_result;
    document.querySelector('#probe-subject').textContent = `${value.case_id} · ${value.run_id} · ${value.subject_scope} · ${value.projection_digest}`;
    button.disabled = false;
    button.onclick = () => {
      const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));
      const a=document.createElement('a'); a.href=url; a.download='phase9-probe.json'; a.click(); URL.revokeObjectURL(url);
    };
  } catch(error) {
    if (generation !== probeGeneration) return;
    document.querySelector('#probe-status').textContent = `Held: ${error.message}`;
  }
}
if (typeof document !== 'undefined') {
  document.querySelector('#refresh').addEventListener('click', refresh);
  refresh();
  document.querySelector('#probe-refresh').addEventListener('click', loadProbe);
  document.querySelector('#probe').addEventListener('change', loadProbe);
}
