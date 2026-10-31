import {canonical} from './verification.js';
const EXPECTED='3c1b95f045a5f7a36a182dbf71b72cb971d2b721575c00af847f952ea9d11bab';
export async function checkedRegressions(value) {
  const {record_digest,...body}=value;
  const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(body)));
  const actual=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(actual!==record_digest || record_digest!==EXPECTED || value.schema!=='p9103-regression-view-v1' ||
     value.status!=='accepted_bounded_regressions' || value.user_accepted!==true || value.P9_10_3_closed!==true ||
     value.G4_accepted!==false || value.full_GRC9V4_conformance!==false || value.new_support?.length!==0 ||
     value.families?.length!==10 || value.reconciliation?.length!==10 ||
     value.regressions?.length!==4 || value.large_campaigns_rerun!==0)
    throw new Error('Regression evidence identity or scope mismatch');
  return value;
}

export function regressionsLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking retained regression evidence…';
    try {
      const response=await fetcher('/api/tranche10/regressions');
      if(!response.ok)throw new Error('Regression evidence unavailable');
      const value=await checkedRegressions(await response.json());
      if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p',value.tests_run+' focused regression tests passed; ten bounded acceptance records reconciled.');
      for(const row of value.regressions){add('h3',row.group);add('p',row.tests_run+' tests; '+row.elapsed_seconds+' seconds.');}
      add('p',value.unchanged_legacy_modules+' pre-V4 modules unchanged. Release: '+value.release_id);
      add('p','No large numerical campaigns rerun. Exact family limits, including CI-root and RG2b C1 limits, remain.');
      for(const row of value.reconciliation){add('h4',row.family);add('p',row.limits);}
      for(const ref of value.evidence){const a=add('a',ref.path.split('/').at(-1));
        a.href='/api/tranche10/regressions/source?path='+encodeURIComponent(ref.path);}
      add('p',value.next_work);status.textContent='P9-10.3 bounded-accepted. No G4 grant.';
    }catch(error){if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined') {
  const button=document.getElementById('tranche10-regressions-refresh');
  if(button)button.addEventListener('click',regressionsLoader(
    document.getElementById('tranche10-regressions-output'),document.getElementById('tranche10-regressions-status')));
}
