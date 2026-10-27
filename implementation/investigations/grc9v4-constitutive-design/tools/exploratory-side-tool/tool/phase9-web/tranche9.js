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
      add('p','Completion/hierarchy unselected. Sixteen selected disabled-compatibility cells remain pending.');
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
