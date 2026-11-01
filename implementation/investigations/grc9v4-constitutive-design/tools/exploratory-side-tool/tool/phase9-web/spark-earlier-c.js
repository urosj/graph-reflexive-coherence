import {canonicalBasin} from './basin.js';
export async function checkedSparkEarlierC(value) {
  const {projection_digest,...body}=value;
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');
  if(projection_digest!=='3eecf3e0ada74250314b53e18ddbd54b0a856ab6319db7946702f17fe9f69ca3' || hash!==projection_digest || value.schema!=='grc9v4_spark_earlier_c_surface_v1' ||
     value.report.accepted_authority!==false || value.report.native_completion!==false || value.report.G4_accepted!==false ||
     value.report.additional_event_gain!==0 || value.report.ordinary_duration!=='32')
    throw new Error('Unbound earlier-closure report or changed scope');
  return value;
}
export function sparkEarlierCLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking earlier closure…';
    try {
      const response=await fetcher('/api/spark-completion/applicability/earlier-c');
      if(!response.ok)throw new Error('Earlier-closure evidence unavailable');
      const value=await checkedSparkEarlierC(await response.json());if(ticket!==sequence)return;
      const add=(tag,text,parent=output)=>{const e=create(tag);e.textContent=text;parent.append(e);return e;};
      add('p','Earlier witnesses pending review; accepted baseline views remain unchanged. Uniform duration 32, two-beat windows, zero additional event gain.');
      const table=add('table','');const header=add('tr','',table);
      for(const title of ['Family','Accepted current endpoint','Earlier current endpoint','Earlier reset endpoint','Status'])add('th',title,header);
      for(const row of value.report.comparison){const tr=add('tr','',table);for(const x of [row.family,row.baseline_current_completion,row.earlier_current_completion,row.earlier_reset_completion,row.status])add('td',String(x),tr);}
      add('p','The four C-family certificates require no trajectory after the selected completion window. Historical executions keep their original counts; selected prefixes end at 376/377.');
      for(const limit of value.report.review_limits)add('p',limit);
      for(const ref of value.source_refs){
        if(!/^(implementation|specs|src)\//.test(ref.path)||ref.path.split('/').includes('..'))throw new Error('Invalid bound source');
        const link=add('a',ref.path.split('/').at(-1));link.href='/api/spark-completion/applicability/earlier-c/source?path='+encodeURIComponent(ref.path);link.target='_blank';link.rel='noopener';add('span',' · ');
      }
      status.textContent='Earlier-closure evidence verified. Review and native work remain separate.';
    }catch(error){if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}
if(typeof document!=='undefined')document.getElementById('spark-earlier-c-refresh')?.addEventListener('click',sparkEarlierCLoader(document.getElementById('spark-earlier-c-output'),document.getElementById('spark-earlier-c-status')));
