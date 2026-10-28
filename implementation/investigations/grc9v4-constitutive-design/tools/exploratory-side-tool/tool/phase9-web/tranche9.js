export function checkedTranche9(value) {
  const expected=['C_OS','C_CI','A_CI','A_PC'];
  if (value.schema !== 'phase9_tranche9_first_group_v1' ||
      JSON.stringify(value.families) !== JSON.stringify(expected) ||
      value.iteration !== 'P9-9.1b' || value.user_accepted !== true ||
      value.aggregate_closed !== false || value.full_GRC9V4_conformance !== false ||
      value.check_level !== 'retained_integrity_only_no_numerical_rerun' ||
      value.state !== 'bounded_accepted' ||
      value.optional_completion !== 'unselected' ||
      value.disabled_compatibility !== 'pending_16_selected_cells' ||
      !Array.isArray(value.records) || value.records.length !== 4 ||
      value.records.some((r,i)=>r.family!==expected[i] || r.tests!==6 || r.outcome!=='passed' || !r.exact_replay))
    throw new Error('Unexpected or widened Tranche 9 evidence');
  return value;
}

export function lifecycleLoader(container,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;container.replaceChildren();status.textContent='Checking retained evidence…';
    try {
      const response=await fetcher('/api/tranche9');
      if(!response.ok)throw new Error('Unavailable');
      const v=checkedTranche9(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;container.append(e);return e;};
      add('p','P9-9.1b accepted for the bounded four-family scope. Integrity check only: no numerical rerun or full GRC9V4 conformance.');
      for(const r of v.records)add('p',`${r.family}: ${r.tests} tests passed; mixed lifecycle replay verified (${r.elapsed_seconds.toFixed(1)} s execution).`);
      add('p','Completion/hierarchy unselected. Current disabled compatibility is tracked in the separate P9-9.2 panel.');
      for(const ref of v.source_refs){
        if(!ref.path.startsWith('implementation/phase-9-grcv4/tranche-9/') || ref.path.includes('..'))throw new Error('Invalid source path');
        const a=add('a',ref.path.split('/').at(-1));a.href='/api/tranche9/source?path='+encodeURIComponent(ref.path);
        a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='Retained evidence verified; bounded acceptance recorded.';
    } catch(error) {if(ticket!==sequence)return;container.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined') {
  const button=document.getElementById('tranche9-refresh');
  if(button)button.addEventListener('click',lifecycleLoader(document.getElementById('tranche9-output'),document.getElementById('tranche9-status')));
}

export function checkedCompatibility(v) {
  const families=['C_OS','C_CI','A_CI','A_PC'],surfaces=['transition','state','observable','lifecycle'];
  if(v.schema!=='p992-compatibility-status-v1' || JSON.stringify(v.families)!==JSON.stringify(families) ||
    v.selected_cells!==16 || v.passed_cells!==16 || v.unselected_cells!==24 ||
    v.user_accepted!==true || v.full_GRC9V4_conformance!==false || v.aggregate_closed!==false || v.crossings_executed!==false ||
    v.check_level!=='retained_integrity_only_no_native_rerun' || !Array.isArray(v.cells) || v.cells.length!==40)
    throw new Error('Unexpected compatibility scope');
  const matrix=v.matrix_reconciliation;
  if(!matrix || matrix.iteration!=='P9-9.3' || matrix.outcome!=='passed' ||
    matrix.user_accepted!==true || matrix.native_execution!==false || !/^[a-f0-9]{64}$/.test(matrix.record_digest))
    throw new Error('Invalid matrix reconciliation');
  const seen=new Set(),population=['A','C'].flatMap(c=>['OS','CI','PC','CI_PC','RG2b'].map(r=>c+'_'+r));
  for(const row of v.cells){
    const key=row.family+'/'+row.surface,selected=families.includes(row.family);
    if(!population.includes(row.family) || !surfaces.includes(row.surface) || seen.has(key) ||
      row.iteration_id!==`P9-9.2-${row.family}-${row.surface}` ||
      row.state!==(selected?'bounded_accepted':'unselected') ||
      (selected?!/^[a-f0-9]{64}$/.test(row.record_digest):row.record_digest!==null))throw new Error('Invalid compatibility cell');
    seen.add(key);
  }
  return v;
}

export function compatibilityLoader(container,status,fetcher=fetch,create=tag=>document.createElement(tag)){
  let sequence=0;
  return async()=>{
    const ticket=++sequence;container.replaceChildren();status.textContent='Checking retained compatibility evidence…';
    try{
      const response=await fetcher('/api/tranche9/compatibility');if(!response.ok)throw new Error('Unavailable');
      const v=checkedCompatibility(await response.json());if(ticket!==sequence)return;
      const add=(tag,text,parent=container)=>{const e=create(tag);e.textContent=text;parent.append(e);return e;};
      add('p','16 exact native delegate cells passed; bounded acceptance recorded. 24 cells unselected. Integrity only; no native rerun, crossings or full conformance.');
      add('p','P9-9.3: all forty cells reconciled against the frozen catalog and accepted evidence; matrix acceptance recorded. No new native execution.');
      const table=add('table',''),head=add('tr','',table);
      for(const title of ['Family','Surface','Disposition'])add('th',title,head);
      for(const row of v.cells){const tr=add('tr','',table);for(const text of [row.family,row.surface,row.state])add('td',text,tr);}
      for(const ref of v.source_refs){
        if(!ref.path.startsWith('implementation/phase-9-grcv4/tranche-9/') || ref.path.includes('..'))throw new Error('Invalid source path');
        const a=add('a',ref.path.split('/').at(-1));a.href='/api/tranche9/compatibility/source?path='+encodeURIComponent(ref.path);a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='Compatibility evidence verified; bounded acceptance recorded.';
    }catch(error){if(ticket!==sequence)return;container.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined'){
  const button=document.getElementById('tranche9-compatibility-refresh');
  if(button)button.addEventListener('click',compatibilityLoader(document.getElementById('tranche9-compatibility-output'),document.getElementById('tranche9-compatibility-status')));
}

export function checkedCrossings(v){
  const families=['C_OS','C_CI','A_CI','A_PC'];
  if(v.schema!=='p994a-crossing-status-v1' || v.iteration!=='P9-9.4a' ||
    JSON.stringify(v.families)!==JSON.stringify(families) ||
    v.user_accepted!==true || v.public_api!==false || v.aggregate_closed!==false || v.full_GRC9V4_conformance!==false ||
    v.state!=='bounded_accepted' || v.check_level!=='retained_integrity_only_no_native_rerun' ||
    !Array.isArray(v.records) || v.records.length!==4 ||
    v.records.some((r,i)=>r.family!==families[i] || r.tests!==4 || r.outcome!=='passed' || !/^[a-f0-9]{64}$/.test(r.record_digest)))
    throw new Error('Unexpected crossing scope');
  return v;
}
export function crossingsLoader(container,status,fetcher=fetch,create=tag=>document.createElement(tag)){
  let sequence=0;
  return async()=>{
    const ticket=++sequence;container.replaceChildren();status.textContent='Checking retained crossing evidence…';
    try{
      const response=await fetcher('/api/tranche9/crossings');if(!response.ok)throw new Error('Unavailable');
      const v=checkedCrossings(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;container.append(e);return e;};
      add('p','P9-9.4a: both same-graph migration directions executed for four families. Bounded acceptance recorded. Integrity only; public API remains P9-9.4b.');
      for(const r of v.records)add('p',`${r.family}: ${r.tests} tests passed, including exact legacy parity, both-role return, rollback and replay.`);
      add('p','Larger legacy timestep: C_CI return admission rejects; the other three reject the next enabled step. No numerical thresholds weakened.');
      for(const ref of v.source_refs){
        if(!ref.path.startsWith('implementation/phase-9-grcv4/tranche-9/') || ref.path.includes('..'))throw new Error('Invalid source path');
        const a=add('a',ref.path.split('/').at(-1));a.href='/api/tranche9/crossings/source?path='+encodeURIComponent(ref.path);a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='Crossing evidence verified; bounded acceptance recorded.';
    }catch(error){if(ticket!==sequence)return;container.replaceChildren();status.textContent=String(error);}
  };
}
if(typeof document!=='undefined'){
  const button=document.getElementById('tranche9-crossings-refresh');
  if(button)button.addEventListener('click',crossingsLoader(document.getElementById('tranche9-crossings-output'),document.getElementById('tranche9-crossings-status')));
}

const publicFamilies = ['A','C'].flatMap(c=>['OS','CI','PC','CI_PC','RG2b'].map(r=>c+'_'+r));
const realizationSchemas = {OS:'os_params', CI:'ci_params', PC:'pc_params', 'CI+PC':'cipc_params', RG2b:'rg2b_params'};
export function checkedPublic(v) {
  if(v.schema!=='p994b-public-api-status-v1' || v.iteration!=='P9-9.4b' ||
     JSON.stringify(v.families)!==JSON.stringify(['C_OS','C_CI','A_CI','A_PC']) ||
     v.public_api!==true || v.user_accepted!==true || v.aggregate_closed!==false ||
     v.full_GRC9V4_conformance!==false || v.state!=='bounded_accepted' ||
     v.check_level!=='retained_integrity_only_no_native_rerun' ||
     v.acceptance_digest!=='eca188da8a0a75ad67e87124136dc89ff5c8d5642aa07ee5d0a15eda9f795c3c' ||
     JSON.stringify(v.records?.map(r=>r.family))!==JSON.stringify([...v.families,'boundary','contracts','architecture']) ||
     v.records.some(r=>r.tests!==(r.family==='contracts'?6:r.family==='architecture'?9:4) || r.outcome!=='passed' || !/^[0-9a-f]{64}$/.test(r.record_digest)))
    throw new Error('Invalid bounded public API evidence');
  if(JSON.stringify(v.contract_families)!==JSON.stringify(publicFamilies) ||
     JSON.stringify(v.contract_matrix?.map(r=>r.profile_family_id))!==JSON.stringify(publicFamilies))
    throw new Error('Incomplete public contract matrix');
  for(const r of v.contract_matrix){
    const candidate=r.profile_family_id[0], realization=r.profile_family_id.slice(2).replace('_','+');
    const fields=['C',...(candidate==='A'?['W_A']:[]),...(['PC','CI+PC'].includes(realization)?['Z_4']:[])];
    if(r.candidate!==candidate || r.realization!==realization || r.roundtrip!==true ||
       r.candidate_parameter_schema!==`candidate_${candidate.toLowerCase()}_params` ||
       r.realization_parameter_schema!==realizationSchemas[realization] ||
       JSON.stringify(r.authoritative_fields)!==JSON.stringify(fields))
      throw new Error('Invalid family contract axes');
  }
  const a=v.architecture;
  if(a?.execution_selection?.registered_owner_does_not_enable!==true ||
     a?.artifact_transfer?.complete_bundle_preserved!==true ||
     a?.artifact_transfer?.dropped_prefix_rejected!==true ||
     a?.accepted_replay?.checkpoint_bytes_equal!==true ||
     a?.accepted_crossing_replay?.checkpoint_bytes_equal!==true ||
     a?.branch_ownership?.no_nested_enabled_owner!==true ||
     a?.branch_ownership?.sole_receipt_ledger!==true ||
     a?.replay_assessment?.standalone_event_checkpoint_replays!==0)
    throw new Error('Incomplete owner-boundary evidence');
  return v;
}

export function publicLoader(container,status,fetcher=fetch) {
  return async function() {
    container.replaceChildren();status.textContent='Checking retained public API evidence…';
    try {
      const response=await fetcher('/api/tranche9/public');if(!response.ok)throw new Error('Unavailable');
      const v=checkedPublic(await response.json());
      const add=(tag,text)=>{const e=container.ownerDocument.createElement(tag);e.textContent=text;container.append(e);return e;};
      add('p','Public GRC9V4: ten typed family contracts; native execution covers C_OS, C_CI, A_CI and A_PC. Thirty-five contract/integration/architecture tests passed; bounded-accepted on 2026-10-28. Retained integrity only; no native rerun or full conformance grant.');
      for(const r of v.contract_matrix)add('p',`${r.profile_family_id}: ${r.authoritative_fields.join(', ')}; ${r.realization_parameter_schema}; ${v.families.includes(r.profile_family_id)?'native execution in scope':'contract only; native execution unavailable in this scope'}.`);
      for(const r of v.records)add('p',`${r.family}: ${r.tests} tests; ${r.outcome}.`);
      const replay=v.architecture.replay_assessment;
      add('p',`One branch publication and receipt ledger; small C_OS replay: ${replay.executed_actions.ordinary} ordinary steps, ${replay.executed_actions.expansion} expansion, ${replay.standalone_event_checkpoint_replays} nested event-checkpoint replays. Unifying standalone and branch checkpoint formats remains a future consideration after all ten are enabled.`);
      for(const ref of v.source_refs){
        const a=add('a',ref.path.split('/').at(-1));a.href='/api/tranche9/public/source?path='+encodeURIComponent(ref.path);a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='Checked bounded evidence; P9-9.5 and P9-9.6 remain.';
    } catch(error) {
      container.replaceChildren();status.textContent='Unavailable — not admitted.';
    }
  };
}
if(typeof document!=='undefined') {
  const button=document.getElementById('tranche9-public-refresh');
  if(button)button.addEventListener('click',publicLoader(document.getElementById('tranche9-public-output'),document.getElementById('tranche9-public-status')));
}
