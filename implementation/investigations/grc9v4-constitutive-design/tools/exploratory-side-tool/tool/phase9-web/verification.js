export function checkedStatus(value) {
  if (!['phase9_governance_status_v1','phase9_governance_status_v2'].includes(value?.schema) || value.output_class !== "implementation_verification_status_not_forensic_trace") throw new Error("Unrecognized verification status");
  const implementation = value.schema === 'phase9_governance_status_v2' && value.current_boundary === 'passed';
  if (typeof value.P9_G1_accepted !== 'boolean' || value.runtime_authorized !== implementation || (implementation && !value.P9_G1_accepted) || (value.schema === 'phase9_governance_status_v1' && value.P9_G1_accepted) || !Array.isArray(value.accepted_generic_runtime_support) || value.accepted_generic_runtime_support.length !== 0 || !Array.isArray(value.admitted_specialization_support_sets) || value.admitted_specialization_support_sets.length !== 0) throw new Error("Unverified runtime authority or support");
  if (value.P9_G1_accepted && value.approval_digest !== 'cd2c52f30477e1042bb903bd0553da237ddccc9cad373afecc1a84e4e0b37ea2') throw new Error('Missing recorded P9-G1 acceptance');
  if (implementation && (value.runtime_authority_state !== 'accepted_P9_G1_bounded_implementation_not_conformance' || !Array.isArray(value.implementation_scope) || value.implementation_scope.length !== 43)) throw new Error('Missing accepted P9-G1 scope');
  if (!implementation && value.P9_G1_accepted && (value.current_boundary !== 'failed_closed' || value.runtime_authority_state !== 'accepted_P9_G1_current_work_held' || value.implementation_scope !== undefined || value.permitted_runtime_paths !== undefined || value.dependency_ready_leaves !== undefined || value.foundation_acceptance !== undefined || value.request_acceptance !== undefined || value.result_acceptance !== undefined || value.harness_acceptance !== undefined || value.integration_acceptance !== undefined || value.geometry_acceptance !== undefined)) throw new Error('Held work cannot retain implementation permission');
  if (value.schema === 'phase9_governance_status_v2' && !['verified','unavailable','invalid'].includes(value.handoff_evidence?.status)) throw new Error('Unknown handoff evidence disposition');
  if (implementation && (value.foundation_acceptance?.record_digest !== '1e3f0ddb06b119fa46dc7609d05b7db0c3a4cbc07428c05b8a032da081ae9dd4' || JSON.stringify(value.foundation_acceptance?.accepted_iterations) !== JSON.stringify(['P9-2.1','P9-2.2']))) throw new Error('Missing accepted foundation');
  if (implementation && (value.request_acceptance?.record_digest !== 'ac07a2f7c93538454d9663aba78ca0eb5af385d7975582e4c21682f41ce4c17f' || JSON.stringify(value.request_acceptance?.accepted_iterations) !== JSON.stringify(['P9-2.3']))) throw new Error('Missing accepted requests');
  if (implementation && (value.result_acceptance?.record_digest !== '9d2fd4f0bb0445b9b3c46fd6f7e5b0ff710a8a85aceaeabacad44a477ff365a0' || JSON.stringify(value.result_acceptance?.accepted_iterations) !== JSON.stringify(['P9-2.4']))) throw new Error('Missing accepted results');
  if (implementation && (value.harness_acceptance?.record_digest !== 'e479a8e5935fc8740b59f96b31651070f842f73f92541bb84dbc1c9d63f59896' || JSON.stringify(value.harness_acceptance?.accepted_iterations) !== JSON.stringify(['P9-2.5']))) throw new Error('Missing accepted harness');
  if (implementation && (value.integration_acceptance?.record_digest !== 'e5ba16731e03dc916b8755c5999ab2b59acf431255612e76e0dcebe108104bc2' || JSON.stringify(value.integration_acceptance?.accepted_iterations) !== JSON.stringify(['P9-2.6']))) throw new Error('Missing accepted integration');
  if (implementation && (value.geometry_acceptance?.record_digest !== 'f119e1361500e72f58297bc8186f868954b4065c853fcdd089280a5d28f88618' || JSON.stringify(value.geometry_acceptance?.accepted_iterations) !== JSON.stringify(['P9-3.1']))) throw new Error('Missing accepted geometry');
  if (implementation && (JSON.stringify(value.dependency_ready_leaves) !== JSON.stringify(['P9-2.1','P9-2.2','P9-2.3','P9-2.4','P9-2.5','P9-2.6','P9-3.1','P9-3.2']) || !Array.isArray(value.permitted_runtime_paths) || value.permitted_runtime_paths.length !== 23 || !['src/pygrc/models/__init__.py','pyproject.toml','tests/models/grcv4_conformance_harness.py','tests/models/grcv4_reference_oracles.py',"src/pygrc/models/grc_v4_geometry.py","src/pygrc/models/grc_v4_transport.py","tests/models/test_grc_v4_geometry.py","tests/models/test_grc_v4_transport.py"].every(path => value.permitted_runtime_paths.includes(path)))) throw new Error('Invalid dependency-ready permission');
  if (!['passed', 'failed_closed'].includes(value.current_boundary)) throw new Error("Unknown boundary disposition");
  if (!['not_current', 'recorded_pass_matching_current_inputs'].includes(value.recorded_full_verification)) throw new Error("Unknown recorded evidence disposition");
  if (value.current_boundary !== 'passed' && value.recorded_full_verification !== 'not_current') throw new Error("Failed boundary cannot retain a passing receipt");
  if (value.current_boundary === 'passed') {
    if (!/^[0-9a-f]{64}$/.test(value.policy_digest) || !Array.isArray(value.source_refs) || !value.source_refs.length || !value.source_refs.every(r => typeof r.path === 'string' && /^[0-9a-f]{64}$/.test(r.sha256))) throw new Error('Missing verified source bindings');
    const ids = implementation ? ['P9-1.4','P9-1.5','P9-1.6','P9-1.7','P9-1.8','P9-1.9'] : ['P9-1.7','P9-1.8'];
    if (!Array.isArray(value.iterations) || value.iterations.length !== ids.length || !value.iterations.every((r, i) => r.iteration_id === ids[i] && ['in_progress', 'implemented_and_verified'].includes(r.status) && r.reviewer_decision === (implementation ? 'accepted_by_user' : 'pending_user_review'))) throw new Error('Invalid leaf authority');
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
  document.querySelector('#authority').textContent = 'Not verified / permission withheld';
  document.querySelector('#next-work').textContent = 'Next work not verified.';
  document.querySelector('#recorded').textContent = 'Not current';
  document.querySelector('#handoff').textContent = 'Not checked';
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
    const held = value.current_boundary !== 'passed';
    status.classList.toggle('error', held);
    status.textContent = held ? `Held: ${value.error || 'Current inputs failed verification'}. ${value.P9_G1_accepted ? 'Recorded P9-G1 acceptance remains intact.' : 'P9-G1 acceptance is not verified.'}` : value.P9_G1_accepted ? 'P9-G1 accepted. Bounded implementation is authorized; runtime conformance remains pending.' : 'Current planning checks passed. Runtime remains unauthorized.';
    document.querySelector('#authority').textContent = value.P9_G1_accepted ? (held ? 'Accepted / current work held' : 'Accepted / bounded implementation only') : 'Not accepted or not verified / not authorized';
    document.querySelector('#next-work').textContent = value.runtime_authorized ? `Accepted foundation: ${value.foundation_acceptance.accepted_iterations.join(', ')}. Accepted requests: ${value.request_acceptance.accepted_iterations.join(', ')}. Accepted results: ${value.result_acceptance.accepted_iterations.join(', ')}. Accepted harness: ${value.harness_acceptance.accepted_iterations.join(', ')}. Accepted integration: ${value.integration_acceptance.accepted_iterations.join(', ')}. Accepted geometry: ${value.geometry_acceptance.accepted_iterations.join(', ')}. Dependency-ready leaves: ${value.dependency_ready_leaves.join(', ')}. ${value.permitted_runtime_paths.length} runtime paths are currently eligible under their owners. Later leaves remain gated.` : held ? 'Current work held; resolve the reported current-boundary failure.' : 'P9-G1 review remains pending.';
    document.querySelector('#boundary').textContent = held ? 'Failed · current work held' : 'Passed · current bytes';
    document.querySelector('#recorded').textContent = value.recorded_full_verification === 'not_current' ? 'Not current · rerun CLI' : 'Recorded pass · matching inputs';
    document.querySelector('#handoff').textContent = ({verified:'Verified · normalized archive and historical inputs', unavailable:'Unavailable · no archive integrity pass', invalid:'Invalid · archive integrity check failed'})[value.handoff_evidence?.status] || 'Not applicable to this historical phase';
    document.querySelector('#policy').textContent = value.policy_digest ? `Policy digest: ${value.policy_digest}` : '';
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
