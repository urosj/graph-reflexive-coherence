import {canonicalBasin} from './basin.js';
const PIN='0853a4df52375670234aaf958dbfe8dfec555f425abcfc99d0bd7f62a053f97d';
export async function checkedDebts(value) {
  const {projection_digest,...body}=value;
  const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonicalBasin(body)));
  const actual=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(actual!==projection_digest || projection_digest!==PIN || value.ledger.families.length!==10 ||
     value.ledger.counts.native_portions_discharged!==30 || value.ledger.scope.G4_accepted!==false)
    throw new Error('Changed native claim/debt reconciliation');
  return value;
}
export function debtLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking ledger and accepted evidence…';
    try {
      const response=await fetcher('/api/native-spark/debts');
      if(!response.ok)throw new Error('Debt reconciliation unavailable');
      const value=await checkedDebts(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','Scientific acceptance → exact native campaign → bounded discharge. No new scientific authority or numerical run.');
      add('a','Read the reconciliation decision').href=value.decision_url;
      add('a','Inspect the complete claim/debt ledger').href=value.ledger_url;
      add('a','Read bounded user acceptance').href='/api/native-spark/debts/source?name=acceptance';
      for(const row of value.ledger.families)
        add('p',`${row.family}: ${row.native_obligation_ids.length} native portions discharged; ${row.limitations}`);
      for(const row of value.ledger.debts)
        add('p',`${row.debt_id}: ${row.disposition}; residuals: ${row.residual_obligation_ids.join(', ') || 'none within this bounded scope'}.`);
      add('p','Broader hierarchy remains deferred. The 29 inherited D10 debt transformations retain their existing authority; no C1, abundance, general ATC or G4 grant.');
      status.textContent=`${value.status}; retained evidence checked, no native trajectory executed.`;
    }catch(error){if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}
if(typeof document!=='undefined')document.getElementById('native-debts-refresh')?.addEventListener('click',
  debtLoader(document.getElementById('native-debts-output'),document.getElementById('native-debts-status')));
