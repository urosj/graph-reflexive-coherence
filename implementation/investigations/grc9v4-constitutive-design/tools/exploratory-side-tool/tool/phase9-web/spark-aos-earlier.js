import {canonicalBasin} from './basin.js';
const reportDigest='dec3d7189532bd937d7d3cf65084bb01f78107ea0e18dd325c2a713649e0f5a3';
const hash=async body=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',
  new TextEncoder().encode(canonicalBasin(body))))].map(n=>n.toString(16).padStart(2,'0')).join('');

export async function checkedSparkAOSEarlier(value) {
  const {projection_digest,...body}=value;
  const {record_digest,...r}=value.report??{};
  if(value.schema!=='grc9v4_spark_aos_earlier_surface_v1' || await hash(body)!==projection_digest ||
     value.report_record_digest!==reportDigest || record_digest!==reportDigest || await hash(r)!==reportDigest ||
     r.family!=='A_OS' || r.status!=='demonstrated_bounded_pending_review' ||
     r.accepted_authority!==false || r.native_completion!==false || r.G4_accepted!==false ||
     r.relative_dimension!==30 || r.conductance_dimension!==16 || r.additional_event_gain!==0 ||
     r.trajectory_reruns!==0 || value.check_mode!=='retained_source_integrity_no_numerical_rerun')
    throw new Error('Unbound earlier A_OS certificate or changed scope');
  if(value.source_refs.length!==r.sources.length+1 || JSON.stringify(value.source_refs.slice(1))!==JSON.stringify(r.sources))
    throw new Error('Earlier certificate source index differs');
  for(const ref of value.source_refs)
    if(!/^(implementation|specs|src)\//.test(ref.path) || ref.path.split('/').includes('..') || !/^[0-9a-f]{64}$/.test(ref.sha256))
      throw new Error('Invalid earlier certificate source');
  return value;
}

export function sparkAOSEarlierLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;output.replaceChildren();status.textContent='Checking earlier A_OS certificate…';
    try {
      const response=await fetcher('/api/spark-completion/applicability/a-os/earlier');
      if(!response.ok)throw new Error('Earlier A_OS certificate unavailable');
      const value=await checkedSparkAOSEarlier(await response.json());if(ticket!==sequence)return;
      const r=value.report;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p','Earlier A_OS closure: anisotropic certificate demonstrated, pending review.');
      const table=create('table');output.append(table);
      for(const cells of [['Event','Accepted entry → end','Enlarged ball','Anisotropic domain'],
        ...['current','reset'].map(role=>{const d=r.decisions[role];return [role,
          `${d.original_entry} → ${d.original_window_end}`,`${d.ball_entry} → ${d.ball_window_end}`,
          `${d.anisotropic_entry} → ${d.anisotropic_window_end}`];})]) {
        const row=create('tr');table.append(row);
        for(const text of cells){const cell=create(cells[0]==='Event'?'th':'td');cell.textContent=text;row.append(cell);}
      }
      add('p','About 64% fewer beats. The full 30-dimensional domain includes every resource and conductance direction; the positive window remains two beats.');
      add('p','The same retained event and trajectories are used. Additional event gain: 0; reset live gain: 0. Equations, timestep, allocation and tolerances are unchanged.');
      add('p','Current edge reversal: 364 → 365. New entry: 375. Global earliest completion is not established.');
      for(const limit of r.review_limits)add('p',limit);
      for(const ref of value.source_refs) {
        const a=add('a',ref.path.split('/').at(-1));
        a.href='/api/spark-completion/applicability/a-os/earlier/source?path='+encodeURIComponent(ref.path);
        a.target='_blank';a.rel='noopener';add('span',' · ');
      }
      status.textContent='Earlier certificate sources verified. Review pending; accepted baseline unchanged.';
    } catch(error) {
      if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);
    }
  };
}

if(typeof document!=='undefined')document.getElementById('spark-aos-earlier-refresh')?.addEventListener('click',
  sparkAOSEarlierLoader(document.getElementById('spark-aos-earlier-output'),document.getElementById('spark-aos-earlier-status')));
