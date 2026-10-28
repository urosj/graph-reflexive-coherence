import {canonicalBasin} from './basin.js';

export async function checkedTargets(value) {
  const {record_digest,...body}=value;
  const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonicalBasin(body)));
  const actual=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(record_digest!=='05ceba81064f1e4bb336a2b89dc2fbd7d8a4f1516baf30f3a6082b459422f2aa' || record_digest!==actual ||
     value.schema!=='p9101b-target-compatibility-accepted-status-v1' ||
     value.check_mode!=='retained_integrity_not_native_rerun' ||
     value.user_accepted!==true || value.P9_10_1b_closed!==true || value.P9_10_1_closed!==false ||
     value.full_GRC9V4_conformance!==false || value.compatibility_capability_advertised!==false ||
     value.G4_accepted!==false || value.other_six_source_cells_executed!==0 || value.new_support.length!==0 ||
     JSON.stringify(value.families)!==JSON.stringify(['C_OS','C_CI','A_CI','A_PC']))
    throw new Error('Expanded-target evidence unavailable or scope changed');
  return value;
}

export function targetLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking retained target evidence…';
    try {
      const response=await fetcher('/api/tranche10/targets');
      if(!response.ok)throw new Error('Expanded-target evidence unavailable');
      const v=await checkedTargets(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const el=create(tag);el.textContent=text;output.append(el);return el;};
      add('p','Bounded P9-10.1b accepted; overall P9-10.1 remains open. This view checks retained evidence and does not rerun native operations.');
      add('p',v.scope);
      for(const row of v.rows) {
        add('h3',row.family);
        for(const version of row.versions) {
          add('p',`${version.version}: ${version.outcome}; ${Object.entries(version.surfaces).map(([k,s])=>`${k}: ${s}`).join(', ')}`);
          add('pre',JSON.stringify(version.subject,null,2));
        }
        add('p',`${row.rejection_controls} rejection controls, separate from successful compatibility.`);
      }
      for(const r of [...v.records,...v.source_refs]) {
        const a=add('a',r.path.split('/').at(-1));
        a.href='/api/tranche10/targets/source?path='+encodeURIComponent(r.path);a.target='_blank';a.rel='noopener';
        add('span',' · ');
      }
      add('p','The other 24 source cells and all-forty umbrella capability remain open; aggregate reconciliation follows in P9-10.1c.');
      status.textContent='Retained target checks passed; bounded accepted. P9-10.1 remains open.';
    } catch(error) {if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined') {
  document.getElementById('targets-refresh')?.addEventListener('click',targetLoader(document.getElementById('targets-output'),document.getElementById('targets-status')));
}
