import {canonicalBasin} from './basin.js';

const PINS = {"C_RG2b": "d565c0585cd37e700142db3eb5f6da15e43519646206218f194505c83ab502b3", "A_RG2b": "2cfdc5ef44fefb8fb7b7427cc1ba64a1cf4b4b372534ddcbce67e2740e080f41"}; // Locally checked projections.
const SLUGS = {C_RG2b:'c-rg2b', A_RG2b:'a-rg2b'};

export async function checkedRG2bCampaign(value, family) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if (!PINS[family] || projection_digest !== PINS[family] || actual !== projection_digest ||
      value.family !== family || value.schema !== 'grc9v4_native_rg2b_campaign_surface_v1' ||
      value.native_endpoint_verified !== true || value.native_completion_support !== false ||
      value.user_accepted !== false || value.full_trajectory_runs !== 2 ||
      value.physical_supporting_tail_steps !== 0 || value.roles.current.local_gain !== 1 ||
      value.roles.reset.local_gain !== 0 || value.source_url !== `/api/native-spark/${SLUGS[family]}/campaign/source`)
    throw new Error('Unbound RG2b campaign or widened support');
  return value;
}

export function rg2bCampaignLoader(family, output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;
    output.replaceChildren(); status.textContent=`Checking ${family} campaign…`;
    try {
      const response=await fetcher(`/api/native-spark/${SLUGS[family]}/campaign`);
      if(!response.ok) throw new Error('Campaign unavailable');
      const v=await checkedRG2bCampaign(await response.json(),family);
      if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p',`${family}: duration ${v.duration}; ${v.target_vertices} vertices / ${v.target_edges} edges; exact charge ${v.exact_charge}. FLINT/Arb${v.native_precision_bits}, independent Arb${v.oracle_precision_bits} proofs on every step.`);
      for(const role of ['current','reset']) {
        const r=v.roles[role];
        add('p',`${role}: entry ${r.entry} → window completion ${r.completion}; ${r.target_steps} steps, gain ${r.local_gain}. Cold replay: ${v.cold_replayed_steps[role]} ordinary steps.`);
      }
      add('p',`${v.elapsed_minutes} minutes including checks/recovery; ${v.peak_rss_mib} MiB peak memory; ${(v.compressed_bytes/1048576).toFixed(2)} MiB compressed evidence. ${v.pressure_controls} lifecycle control reports.`);
      add('p','Exact physical states, fluxes, error/proof summaries and diagnostic hashes are retained at every beat. Selected full diagnostics are available; omitted inverse chains require explicit numerical reconstruction. Integrity checking does not rerun them.');
      add('p','Bounded endpoint result pending separate review. No supporting physical tail, aggregate support grant, section differentiability claim or larger-graph claim.');
      const link=add('a','Retained campaign summary');link.href=v.source_url;
      status.textContent=`${family} retained endpoint verified; aggregate support remains separate.`;
    } catch(error) {
      if(ticket!==sequence)return;
      output.replaceChildren();status.textContent=String(error);
    }
  };
}

if(typeof document!=='undefined')for(const [family,slug] of Object.entries(SLUGS)) {
  document.getElementById(`spark-${slug}-campaign-refresh`)?.addEventListener('click',
    rg2bCampaignLoader(family,document.getElementById(`spark-${slug}-campaign-output`),document.getElementById(`spark-${slug}-campaign-status`)));
}
