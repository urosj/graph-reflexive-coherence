export function endReviewLoader(container,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let generation=0;
  return async()=>{
    const current=++generation;container.replaceChildren();status.textContent='Checking retained final reviews…';
    try {
      const response=await fetcher('/api/tranche8/end');
      if(!response.ok)throw Error('Final review evidence unavailable');
      const value=await response.json();
      if(current!==generation)return;
      if(value.schema!=='phase9_tranche8_end_reviews_v1'||value.final_review_user_accepted!==true
        ||value.first_group_closed!==true||value.aggregate_closed!==false
        ||JSON.stringify(value.families)!==JSON.stringify(['C_OS','C_CI','A_CI','A_PC']))throw Error('Unexpected review scope');
      const m=value.records.mechanisms,p=value.records.performance;
      if(m.new_native_steps!==0||m.new_support!==false||p.new_cache_implementation!==false)
        throw Error('Unexpected review claim');
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;container.append(e);return e;};
      add('p','8.6 accepted. Final reviews accepted; bounded first-group Tranche 8 is closed. No new trajectories or support.');
      for(const family of value.families){add('h3',family);add('p',m[family].disposition);if(m[family].limitation)add('p',m[family].limitation);}
      add('p',p.disposition);
      for(const [label,path] of [['Mechanism evidence','P9-Tranche8-FirstGroupMechanisms.json'],['Performance evidence','P9-Tranche8-FirstGroupPerformance.json'],['Final review','P9-Tranche8-FirstGroupEndResults.md']]) {
        const a=add('a',label+' ');a.href='/api/tranche8/end/source?path='+encodeURIComponent('implementation/phase-9-grcv4/tranche-8/'+path);
      }
      status.textContent='Final review evidence verified; bounded scope retained.';
    } catch(error){if(current===generation){container.replaceChildren();status.textContent='Unavailable: '+error.message;}}
  };
}
if(typeof document!=='undefined'&&document.querySelector('#tranche8-end')){
  document.querySelector('#tranche8-end-refresh').addEventListener('click',endReviewLoader(document.querySelector('#tranche8-end'),document.querySelector('#tranche8-end-status')));
}
