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
