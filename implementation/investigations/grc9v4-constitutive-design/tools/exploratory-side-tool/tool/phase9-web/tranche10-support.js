import {canonical} from './verification.js';

export async function checkedReconciledSupport(value) {
  const {record_digest,...body}=value;
  const bytes=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(body)));
  const actual=[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if(record_digest!=='d37eeef3f4306e7f8a290bf0e4566e021e2f75e9fb10effba5089cfeb99ca5b6' || record_digest!==actual ||
     value.schema!=='p9101c-support-accepted-status-v1' || value.user_accepted!==true ||
     value.P9_10_1c_closed!==true || value.P9_10_1_closed!==true ||
     value.full_GRC9V4_conformance!==false || value.compatibility_capability_advertised!==false ||
     value.G4_accepted!==false || value.native_execution!==false ||
     value.exact_target_basin_checks?.role_captures!==16 ||
     value.exact_target_basin_checks?.user_accepted!==true ||
     value.source_matrix_counts?.bounded_accepted!==16 || value.source_matrix_counts?.unselected_not_executed!==24 ||
     JSON.stringify(value.resolved_holds?.map(h=>h.id))!==JSON.stringify(['basin_surface','target_identity_scope']) ||
     JSON.stringify(value.open_items?.map(h=>h.id))!==JSON.stringify(['umbrella_compatibility']) ||
     JSON.stringify(value.families)!==JSON.stringify(['C_OS','C_CI','A_CI','A_PC']))
    throw new Error('Support reconciliation unavailable or scope changed');
  return value;
}

export function reconciledSupportLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking accepted subjects and current holds…';
    try {
      const response=await fetcher('/api/tranche10/support');if(!response.ok)throw new Error('Support reconciliation unavailable');
      const v=await checkedReconciledSupport(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','P9-10.1a/b/c are accepted; bounded P9-10.1 is closed. No native rerun is performed by this view.');
      for(const h of v.resolved_holds)add('p',`${h.id}: ${h.disposition}. ${h.scope}`);
      for(const row of v.rows) {
        add('h3',row.family);
        add('p','Baseline basin diagnostic: explicit v2 source. Original v1 declarations are unchanged.');
        add('code',row.source_basin_v2.subject.model_identity);
        for(const t of row.expanded_target_compatibility) {
          add('p',`${t.version} exact target: ${t.outcome}. ${t.basin.status}`);
          add('pre',JSON.stringify(t.subject,null,2));
          if(t.basin.direct_independent_check) {
            const d=t.basin.direct_independent_check;
            add('p','New direct independent basin checks: this exact v2 target, both roles immediately after basin-policy migration and immediately after disabled return. Accepted within bounded P9-10.1c.');
            for(const b of d.boundaries) {
              add('p',b.label);
              add('pre',JSON.stringify({role_equations:b.role_equations,realization_checks:b.realization_checks},null,2));
            }
            add('p',`Return: distinct resources; W histories ${d.distinct_return_W_A?'distinct':'absent'}; carrier ${d.return_carrier}. Fixed-H sign bounds do not certify exact CI-root signs.`);
          }
        }
        add('p','The earlier independently pressured basin expansion remains a different exact target. Its evidence is preserved separately; the new direct checks close the coverage gap without transferring that earlier numerical pressure.');
        add('code',row.basin_pressure_expansion_v2.subject.model_identity);
        add('pre',JSON.stringify(row.inherited_limits,null,2));
      }
      add('p','Source matrix: 16 of 40 accepted, 24 unselected. Additional target cells: 16 v1 + 16 v2; these do not fill the other source cells.');
      for(const h of v.open_items)add('p',`${h.id}: ${h.detail} This restricts the umbrella capability and full conformance, not bounded four-family closure.`);
      add('p',v.numerical_limits);
      add('p','D10.2 authority remains indeterminate_requires_review. Optional completion/hierarchy and six-family execution remain unselected; no G4 or full-conformance grant.');
      for(const r of v.source_refs) {
        const a=add('a',r.path.split('/').at(-1));a.href='/api/tranche10/support/source?path='+encodeURIComponent(r.path);a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='Two holds resolved within accepted four-family scope; all-forty restriction retained; bounded P9-10.1 closed. Current work: A_OS through Tranches 8–9; P9-10.2 deferred.';
    } catch(error) {if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined') {
  document.getElementById('tranche10-support-refresh')?.addEventListener('click',reconciledSupportLoader(document.getElementById('tranche10-support-output'),document.getElementById('tranche10-support-status')));
}
