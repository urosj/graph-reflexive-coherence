import {canonical} from './verification.js';
const VERIFICATION_DIGEST='e8551be42f0c01736382c02922ad9c0a3ebc9dc207a7e09ad9abe7960566fe93';
const ACCEPTED_VIEW_DIGEST='92103a8b0e6eaf76cb783a8ead3037cc5583a30e62345f43fbee4951a73865b8';

export async function checkedVerification(value) {
  const {record_digest,...body}=value;
  const hash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(body)));
  const actual=[...new Uint8Array(hash)].map(x=>x.toString(16).padStart(2,'0')).join('');
  const accepted=value.schema==='p9102-retained-verification-accepted-status-v1';
  const validState=accepted
    ? record_digest===ACCEPTED_VIEW_DIGEST && value.state==='accepted_bounded_retained_verification' &&
      value.user_accepted===true && value.P9_10_2_closed===true && value.all_ten_P9_10_2_closed===false &&
      value.evidence_record_digest===VERIFICATION_DIGEST
    : record_digest===VERIFICATION_DIGEST && value.schema==='p9102-retained-verification-v1' &&
      value.state==='passed_bounded_pending_acceptance' && value.user_accepted===false && value.P9_10_2_closed===false;
  if(actual!==record_digest || !validState || value.G4_accepted!==false || value.full_GRC9V4_conformance!==false ||
     value.native_steps!==0 || value.native_replays!==0 || value.new_support?.length!==0 ||
     JSON.stringify(value.families)!==JSON.stringify(['C_OS','C_CI','A_CI','A_PC']) ||
     JSON.stringify(value.families_checked?.map(r=>r.family))!==JSON.stringify(value.families) ||
     !value.families_checked.every(r=>r.versions.length===2 && r.independent_charge_checks.length===4 &&
       r.independent_equations_recomputed===4 && r.native_steps===0 && r.native_replays===0 &&
       r.exact_CI_root_signs_claimed===false) || value.shared_charge_edges.evaluations!==24)
    throw new Error('P9-10.2 record identity, coverage or scope mismatch');
  return value;
}

export function verificationLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence; output.replaceChildren(); status.textContent='Checking retained evidence…';
    try {
      const response=await fetcher('/api/tranche10/verification');
      if(!response.ok)throw new Error('P9-10.2 verification unavailable');
      const v=await checkedVerification(await response.json()); if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p',`${v.user_accepted?'Bounded four-family verification accepted.':'Bounded checks passed; user acceptance pending.'} Native steps: 0. Native replays: 0. Original accepted executions are reused, not relabelled.`);
      for(const row of v.families_checked){
        add('h3',row.family);
        add('p','Four independent saved-equation and charge checks; exact v1/v2 targets; accepted replay plus receipt-chain checks.');
        for(const version of row.versions)
          add('p',`${version.version}: ${version.ledger.receipts} receipts in ${version.ledger.commit_groups} commits; emitted delta and final endpoint checked.`);
        for(const ref of [row.execution_ref,row.exact_target_ref]){
          const link=add('a',ref.path.split('/').at(-1));
          link.href='/api/tranche10/verification/source?path='+encodeURIComponent(ref.path);
        }
      }
      add('p','Shared charge controls: 12 cases under both Python and FLINT. Fixed-H bounds do not certify exact CI-root signs. No G4 or full-conformance grant.');
      if(v.acceptance){const link=add('a','Bounded acceptance decision');link.href='/api/tranche10/verification/source?path='+encodeURIComponent(v.acceptance.path);}
      add('p',v.next_work);status.textContent=v.user_accepted?'Accepted within the four-family scope; other six remain separate.':'Passed within the four-family scope; awaiting acceptance.';
    }catch(error){if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined')document.getElementById('tranche10-verification-refresh')?.addEventListener(
  'click',verificationLoader(document.getElementById('tranche10-verification-output'),document.getElementById('tranche10-verification-status')));
