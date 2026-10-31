import {canonical} from './verification.js';
const REVIEWS={A_OS:'485e499f5500670944de798c873b8cab322932984d4e0c52df5f195acf4e6db9',C_PC:'f9937fa25a07eac6e61e06b5c0153232e6b5d6ce2603d58d801780b03e4950b7',C_CI_PC:'de9b3b958432c063db1af9159e60a7f11efe779ead4a3d5a7f7aa8cdbaa34ebb',A_CI_PC:'5273b53bcff71482518ba71cc0fc58809e39667a6e1b19a23860289cf799e34c',C_RG2b:'2a933e93a9edbeddf9e1808154e97f7513a936018d2effc7c361652d788f68d7'};
const VIEWS={A_OS:'6334c0f67f915efdc91035aa8bdea0c5d8c11c1f11a1b410440848a5922e45df',C_PC:'00b047918e0198c0238b978b358c1d90835e9e38ccd8dfed41cc831068400298',C_CI_PC:'2c691830f6c5227a4ceff4d2640384766f82c05013b416234d06e336101325c3',A_CI_PC:'21f01ac885c69f230abcf88e61db2f48d2842505d037d6f039181536cc9c3e4d',C_RG2b:'5329d797d77af28b34b4bd339ed3ee0f5ff641f217add57b467145e3664d76ee'};

export async function checkedFamilyBasin(value) {
  const {record_digest,...body}=value;
  const accepted=['A_OS','C_PC','C_CI_PC','A_CI_PC','C_RG2b'].includes(value.family);
  const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(body)));
  const actual=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(actual!==record_digest || record_digest!==VIEWS[value.family] || value.schema!=='p910-family-basin-view-v1' ||
     !REVIEWS[value.family] || value.verification_record_digest!==REVIEWS[value.family] ||
     value.status!==(accepted?'accepted_bounded_family_basin':'passed_bounded_pending_acceptance') || value.user_accepted!==accepted ||
     value.P9_10_1_closed!==accepted || value.P9_10_2_closed!==accepted || value.G4_accepted!==false ||
     (accepted && (value.all_ten_P9_10_1_closed!==false || value.all_ten_P9_10_2_closed!==false)) ||
     value.full_GRC9V4_conformance!==false || value.new_support?.length!==0 ||
     value.native_tests!==8 || value.boundaries?.length!==2 ||
     value.verification?.charges?.length!==4 || value.verification.native_steps_added_by_10_2!==0 ||
     value.verification.native_replays_added_by_10_2!==0)
    throw new Error('Family basin review identity or scope mismatch');
  return value;
}

export function familyBasinLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async(family='A_OS')=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking retained family evidence…';
    try {
      if(!REVIEWS[family])throw new Error('Unselected family basin review');
      const response=await fetcher('/api/tranche10/families?family='+encodeURIComponent(family));
      if(!response.ok)throw new Error('Family basin evidence unavailable');
      const value=await checkedFamilyBasin(await response.json());
      if(value.family!==family)throw new Error('Wrong family response');
      if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('h3',value.family+' — 10.1a–c and 10.2');
      add('p',value.family+' 10.1a–c and 10.2: '+(value.user_accepted?'bounded-accepted':'validated; acceptance pending')+'. Eight native tests passed. Earlier accepted evidence remains unchanged.');
      for(const row of value.boundaries){
        add('h4',row.label);add('pre',JSON.stringify({checks:row.realization_checks,equations:row.role_equations},null,2));
      }
      add('p','10.2 reuses this execution: four saved charge checks, two receipt ledgers; zero added native steps or replays.');
      add('p','Represented-flow diagnostic, not an attractor or family-wide conformance claim. No G4 grant.');
      for(const ref of value.evidence){
        const a=add('a',ref.path.split('/').at(-1));
        a.href='/api/tranche10/families/source?family='+encodeURIComponent(family)+'&path='+encodeURIComponent(ref.path);
      }
      add('p',value.next_work);status.textContent=value.user_accepted?'Accepted within bounded '+family+' scope; remaining families are separate.':'Validated within bounded '+family+' scope; acceptance pending.';
    }catch(error){if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined') {
  const select=document.getElementById('tranche10-family-select');
  if(select){for(const family of Object.keys(REVIEWS)){const o=document.createElement('option');o.value=family;o.textContent=family;select.append(o);}
    const load=familyBasinLoader(document.getElementById('tranche10-family-output'),document.getElementById('tranche10-family-status'));
    document.getElementById('tranche10-family-refresh')?.addEventListener('click',()=>load(select.value));}
}
