import {canonicalBasin} from './basin.js';
const reportDigest='c4ecc07cb695391f6589d11e1d8508ddef3056d9fbce857e043eed5a40ed1a60';
const hash=async body=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',
  new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');
const families=['C_OS','C_CI','C_PC','C_CI_PC','A_OS','A_CI','A_PC','A_CI_PC','C_RG2b'];

export function validateARG2bResearch(value) {
  const r=value?.report;
  if (value?.schema!=='grc9v4_spark_arg2b_research_surface_v1' || value.report_record_digest!==reportDigest ||
      r?.record_digest!==reportDigest || r.family!=='A_RG2b' || r.status!=='demonstrated_bounded_pending_review' ||
      r.accepted_authority!==false || r.native_completion!==false || r.G4_accepted!==false ||
      JSON.stringify(r.full_state)!=='["C","W_A"]' || r.full_dimension!==30 || r.ordinary_duration!=='16' ||
      r.entry!==300 || r.completion!==302 || r.last_executed_step!==302 || r.retained_states!==604 ||
      r.supporting_trajectory_steps_after_completion!==0 || r.future_trajectory_required!==false ||
      r.proof?.physical?.full_writer_included!==true || r.proof?.physical?.both_H_consumers!==true ||
      r.proof?.section_C1_claimed!==false || r.proof?.trajectory_inputs_to_domain_checker!==0 ||
      r.decisions?.current?.local_gain!==1 || r.decisions?.reset?.local_gain!==0 ||
      r.verification?.complete_fresh_trajectory_replays!==2 ||
      JSON.stringify(r.accepted_scientific_families)!==JSON.stringify(families) ||
      value.check_mode!=='retained_source_integrity_no_numerical_rerun') {
    throw new Error('A_RG2b research evidence or scope does not match the retained report.');
  }
  return r;
}

export async function checkedSparkARG2bResearch(value) {
  validateARG2bResearch(value);
  const {projection_digest,...body}=value;
  const {record_digest,...report}=value.report;
  if (await hash(body)!==projection_digest || await hash(report)!==record_digest ||
      value.source_refs.length!==value.report.sources.length+1 ||
      JSON.stringify(value.source_refs.slice(1))!==JSON.stringify(value.report.sources))
    throw new Error('A_RG2b report, projection or source index differs.');
  for (const ref of value.source_refs)
    if (!/^(implementation|specs|src)\//.test(ref.path) || ref.path.split('/').includes('..') ||
        !/^[0-9a-f]{64}$/.test(ref.sha256)) throw new Error('Invalid A_RG2b source.');
  return value;
}

export function renderARG2bResearch(value,output,create=tag=>document.createElement(tag)) {
  const r=validateARG2bResearch(value); output.replaceChildren();
  const add=(tag,text)=>{const el=create(tag);el.textContent=text;output.append(el);return el;};
  add('p','A_RG2b: bounded scientific result, pending review. Nine earlier families remain accepted.');
  add('p','Both roles: entry 300 → completion 302. Duration 16; elapsed target time 4832. The two-beat window lasts 32.');
  add('p','Last executed step: 302. Subsequent supporting steps: 0. Current earns one local child; reset and inspection earn zero live gain.');
  add('p','The common curved domain covers all 14 resource and 16 conductance directions. Its proof includes the conductance writer and the Lipschitz invariant section.');
  add('p','Old-edge conductances are preserved and three internal edges start at one. Geometry is reconstructed on the target graph.');
  add('p','All 604 selected states are compressed. Inspection reads retained evidence and does not start a numerical run.');
  add('p','Scientific acceptance and native implementation remain separate. This is the final family awaiting scientific review.');
  for (const ref of value.source_refs) {
    const a=add('a',ref.path.split('/').at(-1));
    a.href='/api/spark-completion/applicability/a-rg2b/research/source?path='+encodeURIComponent(ref.path);
    a.target='_blank';a.rel='noopener';add('span',' · ');
  }
  return r;
}

export function sparkARG2bResearchLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking retained A_RG2b evidence…';
    try {
      const response=await fetcher('/api/spark-completion/applicability/a-rg2b/research',{cache:'no-store'});
      if (!response.ok) throw new Error('A_RG2b research unavailable.');
      const value=await checkedSparkARG2bResearch(await response.json());if (ticket!==sequence) return;
      renderARG2bResearch(value,output,create);status.textContent='A_RG2b research verified; nine scientific families remain accepted.';
    } catch(error) {
      if (ticket!==sequence) return;output.replaceChildren();status.textContent=String(error);
    }
  };
}

if (typeof document!=='undefined') document.getElementById('spark-arg2b-research-refresh')?.addEventListener('click',
  sparkARG2bResearchLoader(document.getElementById('spark-arg2b-research-output'),document.getElementById('spark-arg2b-research-status')));
