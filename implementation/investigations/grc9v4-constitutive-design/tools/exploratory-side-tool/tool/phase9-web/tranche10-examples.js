import {canonical} from './verification.js';
// Pin the projected publication. This page never runs the numerical examples.
export const EXPECTED='91259f0572cee16d08bfb9a0ddd3b48464bdd6788a0084376c384d95b8855ea5';
export async function checkedExamples(value) {
  const {record_digest,...body}=value;
  const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(body)));
  const actual=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(actual!==record_digest || record_digest!==EXPECTED || value.schema!=='p9104-example-view-v1' ||
      value.families?.length!==10 || value.family_runs?.length!==10 || value.lessons?.length!==7 ||
      value.user_accepted!==true || value.P9_10_4_closed!==true ||
      value.full_GRC9V4_conformance!==false || value.G4_accepted!==false ||
      value.completed_spark!==false || value.hierarchy_tracking!==false || value.general_ATC!==false)
    throw new Error('Example publication identity or scope mismatch');
  return value;
}

export function examplesLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking retained examples…';
    try {
      const response=await fetcher('/api/tranche10/examples');
      if(!response.ok)throw new Error('Example publication unavailable');
      const value=await checkedExamples(await response.json());
      if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','Seven progressive lessons for all ten families, plus cross-family migration and a positive geometric seed example.');
      add('p','Seeds and spark candidates are observations; completed sparks, hierarchy and general ATC are not enabled.');
      for(const row of value.family_runs) add('p',row.family+': '+row.lessons.join(', ')+'; '+row.elapsed_seconds+' s.');
      const guide=await fetcher('/api/tranche10/examples/source?path='+encodeURIComponent(value.guide.path));
      if(!guide.ok)throw new Error('Guide unavailable');
      const raw=await guide.text();
      const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw));
      const hash=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
      if(hash!==value.guide.sha256)throw new Error('Guide identity mismatch');
      if(ticket!==sequence)return;
      const details=add('details','');const title=create('summary');title.textContent='Read the complete guide';details.append(title);
      const body=create('pre');body.textContent=raw;body.style.whiteSpace='pre-wrap';details.append(body);
      for(const ref of [value.publication,value.acceptance,...value.examples,...value.outputs]) {
        const line=add('p','');const link=create('a');link.textContent=ref.path.split('/').at(-1);
        link.href='/api/tranche10/examples/source?path='+encodeURIComponent(ref.path);line.append(link);
      }
      add('p',value.next_work);status.textContent='P9-10.4 examples bounded-accepted. No numerical rerun on access.';
    } catch(error) {if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined') {
  const button=document.getElementById('tranche10-examples-refresh');
  if(button)button.addEventListener('click',examplesLoader(document.getElementById('tranche10-examples-output'),document.getElementById('tranche10-examples-status')));
}
