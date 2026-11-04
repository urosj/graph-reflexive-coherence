import {canonicalBasin} from './basin.js';
const PIN='0af1748ea453dcfb68d2077006f33e752f47152691f3084ba8d1ea8b4a73132c';
export async function checkedSparkSupport(value) {
  const {projection_digest,...body}=value;
  const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonicalBasin(body)));
  const actual=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(actual!==projection_digest || projection_digest!==PIN || value.leaf!=='P9-9.1a.7' ||
     value.native_completion_support!==true || value.hierarchy_tracking!==false ||
     value.G4_accepted!==false || value.general_ATC!==false || value.new_numerical_trajectories!==0 ||
     value.families.length!==10 || new Set(value.families.map(r=>r.family)).size!==10 ||
     value.source_url!=='/api/native-spark/support/source') throw new Error('Changed native completion support');
  return value;
}
export function sparkSupportLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence; output.replaceChildren();status.textContent='Checking exact native completion support…';
    try {
      const response=await fetcher('/api/native-spark/support');
      if(!response.ok) throw new Error('Support evidence unavailable');
      const value=await checkedSparkSupport(await response.json());
      if(ticket!==sequence)return;
      const add=(tag,text)=>{const el=create(tag);el.textContent=text;output.append(el);return el;};
      add('p','Ten accepted bounded family campaigns; exact declarations and certificate domains. Capability does not imply that the current occurrence has completed or that every initial state will enter.');
      for(const row of value.families) {
        const current=row.roles.current,reset=row.roles.reset;
        add('p',`${row.family}: duration ${row.duration}; current ${current.entry} → ${current.completion} (gain ${current.local_gain}); reset ${reset.entry} → ${reset.completion} (gain ${reset.local_gain}).`);
        for(const subject of row.subjects) add('code',`${subject.role}: ${subject.model_identity}; declaration ${subject.declaration_digest}`);
      }
      add('p','Historical execution flags are preserved. Thirty native obligations have evidence for P9-10.5 adjudication; general ATC, hierarchy, full conformance and G4 remain separate.');
      const link=add('a','Support reconciliation and evidence references');link.href=value.source_url;
      status.textContent='All ten bounded completion families reconciled; Tranche 10 follow-through remains.';
    } catch(error) {if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}
if(typeof document!=='undefined') document.getElementById('spark-support-refresh')?.addEventListener('click',
  sparkSupportLoader(document.getElementById('spark-support-output'),document.getElementById('spark-support-status')));
