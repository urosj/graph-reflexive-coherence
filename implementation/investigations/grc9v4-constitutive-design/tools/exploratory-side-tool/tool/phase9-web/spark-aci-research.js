import {canonicalBasin} from './basin.js';
const reportDigest='706f60b3852e0913694724ccc08acb4c5e5d63cc5805d9482f530f337792fbd5';
const hash=async body=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',
  new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');

export async function checkedSparkACIResearch(value) {
  const {projection_digest,...body}=value;
  const {record_digest,...r}=value.report??{};
  if(value.schema!=='grc9v4_spark_aci_research_surface_v1' || await hash(body)!==projection_digest ||
     value.report_record_digest!==reportDigest || record_digest!==reportDigest || await hash(r)!==reportDigest ||
     r.family!=='A_CI' || r.status!=='demonstrated_bounded_pending_review' || r.accepted_authority!==false ||
     r.native_completion!==false || r.G4_accepted!==false || r.full_dimension!==30 || r.conductance_dimension!==16 ||
     JSON.stringify(r.full_state)!=='["C","W_A"]' || r.proof?.implicit_geometry_derivative!==true ||
     r.proof?.stationary_writer_self_consistent!==true || r.proof?.OS_derivative_reused!==false ||
     r.proof?.OS_trajectory_reused!==false || r.decisions?.current?.local_gain!==1 || r.decisions?.reset?.local_gain!==0 ||
     JSON.stringify(r.accepted_scientific_families)!=='["C_OS","C_CI","C_PC","C_CI_PC","A_OS"]' ||
     value.check_mode!=='retained_source_integrity_no_numerical_rerun')
    throw new Error('Unbound A_CI research or changed scientific scope');
  if(value.source_refs.length!==r.sources.length+1 || JSON.stringify(value.source_refs.slice(1))!==JSON.stringify(r.sources))
    throw new Error('A_CI source index differs');
  for(const ref of value.source_refs)
    if(!/^(implementation|specs|src)\//.test(ref.path) || ref.path.split('/').includes('..') || !/^[0-9a-f]{64}$/.test(ref.sha256))
      throw new Error('Invalid A_CI source');
  return value;
}

export function sparkACIResearchLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking A_CI research…';
    try {
      const response=await fetcher('/api/spark-completion/applicability/a-ci/research');
      if(!response.ok)throw new Error('A_CI research unavailable');
      const value=await checkedSparkACIResearch(await response.json());if(ticket!==sequence)return;
      const r=value.report;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','A_CI: bounded source-to-completion construction, pending scientific review.');
      add('p','One selected joint current/geometry root supplies continuity and the final-resource conductance writer.');
      add('p','Full-state return: 14 resource directions and all 16 conductance directions.');
      for(const role of ['current','reset']) {
        const d=r.decisions[role];
        add('p',`${role}: entry ${d.first_certified_entry}; two-beat window ends at ${d.target_completion_step}; live gain ${d.local_gain}.`);
      }
      add('p','The anisotropic shape is borrowed from A_OS. The implicit derivative, source beat, event root and both interval trajectories are fresh A_CI evidence.');
      add('p','Old-edge conductances are preserved, three internal edges start at one, and resource shares are 1/128, 63/64, 1/128.');
      for(const limit of r.review_limits)add('p',limit);
      for(const ref of value.source_refs) {
        const a=add('a',ref.path.split('/').at(-1));
        a.href='/api/spark-completion/applicability/a-ci/research/source?path='+encodeURIComponent(ref.path);
        a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='A_CI sources verified. Review pending; five scientific families remain accepted.';
    } catch(error) {
      if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);
    }
  };
}

if(typeof document!=='undefined')document.getElementById('spark-aci-research-refresh')?.addEventListener('click',
  sparkACIResearchLoader(document.getElementById('spark-aci-research-output'),document.getElementById('spark-aci-research-status')));
