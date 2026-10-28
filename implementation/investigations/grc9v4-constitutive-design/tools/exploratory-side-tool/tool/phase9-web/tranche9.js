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
      status.textContent='Public API evidence verified; see the separate conflict and support review status.';
    } catch(error) {
      container.replaceChildren();status.textContent='Unavailable — not admitted.';
    }
  };
}
if(typeof document!=='undefined') {
  const button=document.getElementById('tranche9-public-refresh');
  if(button)button.addEventListener('click',publicLoader(document.getElementById('tranche9-public-output'),document.getElementById('tranche9-public-status')));
}

export function checkedConflict(v) {
  const families=['C_OS','C_CI','A_CI','A_PC'];
  if(v.schema!=='p995-public-conflict-status-v1' || v.iteration!=='P9-9.5' ||
     JSON.stringify(v.families)!==JSON.stringify(families) ||
     v.public_api!==true || v.user_accepted!==true || v.aggregate_closed!==false ||
     v.full_GRC9V4_conformance!==false || v.state!=='bounded_accepted' ||
     v.acceptance_digest!=='792f1b9640edf2e4ae1e958f09662107ec7fd88ab46110e7820b146661a20bec' ||
     v.check_level!=='retained_integrity_only_no_native_rerun' ||
     !Array.isArray(v.records) || v.records.length!==4 ||
     v.records.some((r,i)=>r.family!==families[i] || r.tests!==3 || r.outcome!=='passed' ||
       r.failure_code!=='legacy_expansion_target_undefined' || r.rollback!==true ||
       r.boundary_controls!==6 || !/^[a-f0-9]{64}$/.test(r.record_digest)))
    throw new Error('Invalid public conflict evidence');
  return v;
}

export function conflictLoader(container,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;container.replaceChildren();status.textContent='Checking retained conflict evidence…';
    try {
      const response=await fetcher('/api/tranche9/conflict');if(!response.ok)throw new Error('Unavailable');
      const v=checkedConflict(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;container.append(e);return e;};
      add('p','P9-9.5: the requested legacy expansion is rejected. Tests pass because refusal is atomic; no expansion is committed. Bounded acceptance recorded on 2026-10-28.');
      for(const r of v.records)add('p',`${r.family}: ${r.tests} tests and ${r.boundary_controls} trigger-boundary controls; ${r.failure_code}; full rollback, replay and reset verified.`);
      add('p','Retained integrity only; no native rerun. GRC9V3 is unchanged. This does not grant full GRC9V4 conformance.');
      for(const ref of v.source_refs){
        if(!ref.path.startsWith('implementation/phase-9-grcv4/tranche-9/') || ref.path.includes('..'))throw new Error('Invalid source path');
        const a=add('a',ref.path.split('/').at(-1));a.href='/api/tranche9/conflict/source?path='+encodeURIComponent(ref.path);a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='Conflict evidence verified; bounded acceptance recorded. Next: P9-9.6.';
    }catch(error){if(ticket!==sequence)return;container.replaceChildren();status.textContent=String(error);}
  };
}
if(typeof document!=='undefined') {
  const button=document.getElementById('tranche9-conflict-refresh');
  if(button)button.addEventListener('click',conflictLoader(document.getElementById('tranche9-conflict-output'),document.getElementById('tranche9-conflict-status')));
}

export function checkedSupport(v) {
  const families=['C_OS','C_CI','A_CI','A_PC'];
  const others=publicFamilies.filter(f=>!families.includes(f));
  if(v.schema!=='p996-support-status-v1' || v.iteration!=='P9-9.6' ||
     v.verdict!=='bounded_evidence_reconciled_full_conformance_held' ||
     JSON.stringify(v.families)!==JSON.stringify(families) ||
     JSON.stringify(v.unselected_families)!==JSON.stringify(others) ||
     v.state!=='bounded_accepted' || v.user_accepted!==true ||
     v.acceptance_digest!=='8676df0db54680ca97417fb9bcf657e0cf84fc907bccd2b7c5db47264d8ab861' ||
     v.aggregate_closed!==false || v.full_GRC9V4_conformance!==false ||
     v.compatibility_capability_advertised!==false || v.G4_accepted!==false ||
     v.check_level!=='retained_reconciliation_only_no_native_rerun' ||
     v.optional_completion?.selected!==false || v.optional_completion?.executed!==false ||
     v.optional_completion?.blocking_selected_scope!==false ||
     v.matrix_counts?.total!==40 || v.matrix_counts?.bounded_accepted!==16 ||
     v.matrix_counts?.unselected_not_executed!==24 ||
     v.matrix_counts?.failed!==0 || v.matrix_counts?.unaccounted!==0 ||
     JSON.stringify(v.open_items?.map(r=>r.id))!==JSON.stringify(['basin_surface','umbrella_compatibility','target_identity_scope']) ||
     JSON.stringify(v.rows?.map(r=>r.family))!==JSON.stringify(families) ||
     !/^[a-f0-9]{64}$/.test(v.record_digest))throw new Error('Invalid bounded support review');
  for(const r of v.rows) {
    if(r.disposition!=='bounded_partial_support_evidence_reconciled' ||
       JSON.stringify(r.missing_mandatory_capabilities)!==JSON.stringify(['basin_attributes']) ||
       r.readable_state_missing_basin_identity!==true ||
       r.expanded_target_disabled_surfaces!=='not_executed_for_this_exact_target_identity' ||
       r.complete_profile_is_not_family_wide_support!==true ||
       !/^grcv4-profile-sha256:[a-f0-9]{64}$/.test(r.source?.complete_profile_id) ||
       !/^grc9v4-model-sha256:[a-f0-9]{64}$/.test(r.source?.model_identity))
      throw new Error('Support identity or hold mismatch');
  }
  return v;
}

export function supportLoader(container,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;container.replaceChildren();status.textContent='Checking exact accepted subjects…';
    try {
      const response=await fetcher('/api/tranche9/support');if(!response.ok)throw new Error('Unavailable');
      const v=checkedSupport(await response.json());if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;container.append(e);return e;};
      add('p','Historical P9-9.6 checkpoint, before the accepted basin and target successors. Inspect P9-10.1c for current resolved holds and restrictions.');
      for(const r of v.rows){
        add('p',`${r.family}: enabled lifecycle, four source-model delegate surfaces, both crossings, public API and conflict refusal verified from retained evidence.`);
        add('code',r.source.model_identity);
      }
      for(const h of v.open_items)add('p',`${h.id}: ${h.detail}`);
      add('p','16 compatibility cells accepted, 24 unselected. Optional completion/hierarchy is unselected and does not block this scope. No native rerun or support promotion.');
      for(const ref of v.source_refs){
        if(!ref.path.startsWith('implementation/phase-9-grcv4/tranche-9/') || ref.path.includes('..'))throw new Error('Invalid source path');
        const a=add('a',ref.path.split('/').at(-1));a.href='/api/tranche9/support/source?path='+encodeURIComponent(ref.path);a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='Historical P9-9.6 accepted. Full conformance held. Current reconciliation: P9-10.1c.';
    }catch(error){if(ticket!==sequence)return;container.replaceChildren();status.textContent=String(error);}
  };
}
if(typeof document!=='undefined') {
  const button=document.getElementById('tranche9-support-refresh');
  if(button)button.addEventListener('click',supportLoader(document.getElementById('tranche9-support-output'),document.getElementById('tranche9-support-status')));
}
