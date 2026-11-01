import {canonicalBasin} from './basin.js';
const reportDigest='c3d641283e60bdbce96252a07be8f39acb626a4ad8afd80f47703de65f15644c';
const hash=async body=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',
  new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');

export async function checkedSparkCRG2bResearch(value) {
  const {projection_digest,...body}=value;
  const {record_digest,...r}=value.report??{};
  if(value.schema!=='grc9v4_spark_crg2b_research_surface_v1' || await hash(body)!==projection_digest ||
     value.report_record_digest!==reportDigest || record_digest!==reportDigest || await hash(r)!==reportDigest ||
     r.family!=='C_RG2b' || r.status!=='demonstrated_bounded_pending_review' || r.accepted_authority!==false ||
     r.native_completion!==false || r.G4_accepted!==false || r.full_dimension!==14 || r.ordinary_duration!=='8' ||
     r.duration_choice?.universal_impossibility_claimed!==false || r.duration_choice?.same_completion_uniform_Lipschitz_inverse_at_32!==false ||
     JSON.stringify(r.full_state)!=='["C"]' || r.proof?.full_return_difference_bound!==true ||
     r.proof?.completion_relative!==true || r.proof?.section_C1_claimed!==false ||
     r.proof?.geometry_history_transported!==false || r.proof?.earlier_family_trajectory_reused!==false ||
     r.historical_baseline?.numerical_payloads_retained!==false ||
     r.historical_baseline?.status!=='historical_summary_only' || r.faster?.entry!==390 || r.faster?.completion!==392 || r.faster?.ordinary_duration!=='8' ||
     r.faster?.uniform_duration_32_certified!==false || r.faster?.accepted_authority!==false ||
     r.faster?.proof?.relative_dimension!==14 || r.faster?.proof?.component_radius!=='1/32768' ||
     r.faster?.proof?.original_SC1_contract_unchanged!==true || r.faster?.complete_fresh_trajectory_replays!==2 ||
     r.faster?.decisions?.current?.local_gain!==1 || r.faster?.decisions?.reset?.local_gain!==0 ||
     r.faster?.status!=='historical_summary_only' || r.faster?.numerical_payloads_retained!==false ||
     r.selected_proof!=='direct_continuous_domain' || r.direct?.entry!==390 || r.direct?.completion!==392 ||
     r.direct?.last_executed_step!==392 || r.direct?.retained_states!==784 ||
     r.direct?.supporting_trajectory_steps_after_completion!==0 || r.direct?.future_trajectory_required!==false ||
     r.direct?.proof?.trajectory_inputs_to_domain_checker!==0 || r.direct?.proof?.relative_dimension!==14 ||
     r.direct?.proof?.radius!=='1/4096' || r.direct?.proof?.original_SC1_contract_unchanged!==true ||
     r.direct?.proof?.all_parameters_certified_continuously!==true || r.direct?.proof?.section_C1_claimed!==false ||
     r.direct?.proof?.full_return_difference_bound!==true || r.direct?.proof?.common_contraction?.both_H_consumers!==true ||
     r.direct?.complete_fresh_trajectory_replays!==2 || r.direct?.accepted_authority!==false ||
     r.direct?.ordinary_duration!=='8' || r.direct?.uniform_duration_32_certified!==false ||
     r.direct?.decisions?.current?.local_gain!==1 || r.direct?.decisions?.reset?.local_gain!==0 ||
     r.decisions?.current?.local_gain!==1 || r.decisions?.reset?.local_gain!==0 ||
     JSON.stringify(r.accepted_scientific_families)!=='["C_OS","C_CI","C_PC","C_CI_PC","A_OS","A_CI","A_PC","A_CI_PC"]' ||
     value.check_mode!=='retained_source_integrity_no_numerical_rerun')
    throw new Error('Unbound C_RG2b research or changed scientific scope');
  if(value.source_refs.length!==r.sources.length+1 || JSON.stringify(value.source_refs.slice(1))!==JSON.stringify(r.sources))
    throw new Error('C_RG2b source index differs');
  for(const ref of value.source_refs)
    if(!/^(implementation|specs|src)\//.test(ref.path) || ref.path.split('/').includes('..') || !/^[0-9a-f]{64}$/.test(ref.sha256))
      throw new Error('Invalid C_RG2b source');
  return value;
}

export function sparkCRG2bResearchLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking C_RG2b research…';
    try {
      const response=await fetcher('/api/spark-completion/applicability/c-rg2b/research');
      if(!response.ok)throw new Error('C_RG2b research unavailable');
      const value=await checkedSparkCRG2bResearch(await response.json());if(ticket!==sequence)return;
      const r=value.report;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','C_RG2b: direct closure at 390 → 392 beats for both roles; no later supporting trajectory. Scientific review pending.');
      const f=r.direct;
      add('p',`The selected construction uses uniform duration ${f.ordinary_duration}; elapsed ordinary time to completion is ${f.elapsed_from_event}. Uniform duration 32 remains uncertified.`);
      add('p',`A continuous degree-${f.proof.curve_degree} polynomial curve with full 14-dimensional metric radius ${f.proof.radius} is invariant. Exact bounds cover every parameter and every pair of states; the SC-1 contract is unchanged.`);
      add('p','This strengthens the certificate for the same faster trajectories. Source preparation, event allocation, physical coefficients, graph and invariant-section completion are unchanged.');
      for(const role of ['current','reset'])add('p',`${role}: selected entry ${f.entry}; completion ${f.completion}; last executed step ${f.last_executed_step}; subsequent supporting steps ${f.supporting_trajectory_steps_after_completion}; live gain ${f.decisions[role].local_gain}.`);
      add('p','Section enclosures propagate by the proved invariance equation, with center-shift error and fresh reconstruction checks. Geometry is derived data; the physical state remains C.');
      add('p','Both 392-step prefixes were freshly replayed in full. The domain checker takes no trajectory input. Earlier run summaries follow; their full trajectory files were removed.');
      add('p','Historical finite-union proof: entry 390, completion 392, but supporting runs through 2089. Its original certificate, run summaries, check records and generators remain; its full payloads are superseded.');
      add('p','A unique bounded Lipschitz section supplies geometry on each graph. The proof uses differences without assuming a differentiable section.');
      add('p','The full return covers all 14 independent resource directions. Source and target geometry are derived separately.');
      for(const role of ['current','reset']) {
        const d=r.decisions[role];
        add('p',`${role}: entry ${d.first_certified_entry}; two-beat window ends at ${d.target_completion_step}; live gain ${d.local_gain}.`);
        const elapsed=r.elapsed_from_event[role];
        add('p',`Elapsed ordinary time from expansion: entry ${elapsed.entry}, completion ${elapsed.completion}.`);
      }
      add('p','The historical baseline used certified error tubes and stationary radius 1/8192. Its run records and generating code remain; only the selected direct prefixes are retained in full.');
      add('p','Ordinary duration is 8 and the positive two-beat window lasts 16. Baseline shares are 1/64, 31/32, 1/64; selected shares are 5/2048, 1021/1024, 1/2048. No geometry history is transported across the event.');
      add('p','Changing duration changes the discrete map and its invariant section; equal elapsed time does not identify the trajectories.');
      add('p','Duration 32 cannot support a uniformly Lipschitz inverse on this auxiliary completion. A different completion or agreement domain would need a fresh proof; no universal impossibility is claimed.');
      for(const limit of r.review_limits)add('p',limit);
      for(const ref of value.source_refs) {
        const a=add('a',ref.path.split('/').at(-1));
        a.href='/api/spark-completion/applicability/c-rg2b/research/source?path='+encodeURIComponent(ref.path);
        a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='C_RG2b sources verified. Review pending; eight scientific families remain accepted.';
    } catch(error) {
      if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);
    }
  };
}

if(typeof document!=='undefined')document.getElementById('spark-crg2b-research-refresh')?.addEventListener('click',
  sparkCRG2bResearchLoader(document.getElementById('spark-crg2b-research-output'),document.getElementById('spark-crg2b-research-status')));
