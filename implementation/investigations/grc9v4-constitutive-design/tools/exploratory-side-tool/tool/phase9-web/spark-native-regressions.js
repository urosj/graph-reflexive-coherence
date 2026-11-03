import {canonicalBasin} from './basin.js';
const PIN='9d1955583ad0c70becd0c165addb0621c06d1973450ced8c7770ed41371e3d4c';
export async function checkedNativeRegressions(value) {
  const {projection_digest,...body}=value;
  const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonicalBasin(body)));
  const actual=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(actual!==projection_digest || projection_digest!==PIN ||
     value.schema!=='p9103-native-spark-regressions-v1' || value.regressions.length!==4 ||
     value.reused_evidence.families.length!==10 || value.G4_accepted!==false ||
     value.source_to_completion_campaigns_rerun!==0 || value.new_support.length!==0 ||
     value.source_url!=='/api/native-spark/regressions/source') throw new Error('Changed native integration evidence');
  return value;
}
export function nativeRegressionsLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking retained integration results…';
    try {
      const response=await fetcher('/api/native-spark/regressions');
      if(!response.ok)throw new Error('Integration evidence unavailable');
      const value=await checkedNativeRegressions(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p',`${value.tests_run} focused integration tests passed in four parallel groups. Acceptance: ${value.user_accepted}.`);
      for(const row of value.regressions)add('p',`${row.group}: ${row.tests_run} tests, ${row.elapsed_seconds} seconds.`);
      add('p',value.scope);
      add('p','No source-to-completion campaign rerun; no broader support, hierarchy or G4 decision.');
      const link=add('a','Exact inputs, tests and reused evidence');link.href=value.source_url;
      status.textContent='P9-10.3-NATIVE-SPARK: bounded regressions passed and accepted.';
    }catch(error){if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}
if(typeof document!=='undefined')document.getElementById('native-regressions-refresh')?.addEventListener('click',
  nativeRegressionsLoader(document.getElementById('native-regressions-output'),document.getElementById('native-regressions-status')));
