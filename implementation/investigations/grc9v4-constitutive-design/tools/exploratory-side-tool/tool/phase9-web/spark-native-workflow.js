import {canonicalBasin} from './basin.js';
const PIN='bfcfcac99af7326c9b6ea41681eb64840f0b212185f2847182ed7c77e7a38f29';
export async function checkedWorkflow(value) {
  const {projection_digest,...body}=value;
  const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonicalBasin(body)));
  const actual=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(actual!==projection_digest || projection_digest!==PIN || value.publication.families.length!==10 ||
     value.publication.new_full_trajectory_runs!==0 || value.publication.G4_accepted!==false)
    throw new Error('Changed native workflow publication');
  return value;
}
export function workflowLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking tutorial sources…';
    try {
      const response=await fetcher('/api/native-spark/workflow');
      if(!response.ok)throw new Error('Workflow unavailable');
      const value=await checkedWorkflow(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','Source beat → explicit expansion → certificate admission → actual domain entry → two positive beats → completed spark.');
      add('p','Certificate installation earns no time or gain. Reset comparison endpoints earn zero gain.');
      add('a','Read the full public workflow').href=value.guide_url;
      add('a','Open the executable example').href=value.code_url;
      for(const row of value.publication.families) {
        const c=row.endpoints.current,r=row.endpoints.reset;
        add('p',`${row.family}: current ${c.entry} → ${c.completion}, gain ${c.local_gain}; reset comparison ${r.entry} → ${r.completion}, gain ${r.local_gain}; duration ${row.duration}.`);
      }
      add('h3','Inspect retained results');add('pre',value.inspect_command);
      add('h3','Execute source, expansion and certificate admission');add('pre',value.prepare_command);
      add('h3','Explicitly run the complete current history (may take minutes)');add('pre',value.run_command);
      add('p',value.limits);
      status.textContent=`Native spark workflow: accepted=${value.user_accepted}; sources checked; no trajectory executed.`;
    }catch(error){if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}
if(typeof document!=='undefined')document.getElementById('native-workflow-refresh')?.addEventListener('click',
  workflowLoader(document.getElementById('native-workflow-output'),document.getElementById('native-workflow-status')));
