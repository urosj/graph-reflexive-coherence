import {canonicalBasin} from './basin.js';

export async function checkedNativeCCICampaign(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if (projection_digest !== 'bcbcc4783cda83fcce9d0418c98c1e6180341f56c95ef1c5ff2f4d837009fc30' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_cci_campaign_surface_v1' || value.family !== 'C_CI' ||
      value.native_endpoint_verified !== true || value.native_completion_support !== false ||
      value.full_trajectory_runs !== 2 || value.physical_supporting_tail_steps !== 0 ||
      value.roles.current.local_gain !== 1 || value.roles.reset.local_gain !== 0 ||
      value.source_url !== '/api/native-spark/c-ci/campaign/source')
    throw new Error('Unbound C_CI campaign or changed endpoint scope');
  return value;
}

export function nativeCCICampaignLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;
    output.replaceChildren();status.textContent='Checking native C_CI completion evidence…';
    try {
      const response=await fetcher('/api/native-spark/c-ci/campaign');
      if (!response.ok) throw new Error('Native C_CI campaign unavailable');
      const value=await checkedNativeCCICampaign(await response.json());
      if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p',`${value.target_vertices} vertices / ${value.target_edges} edges, duration ${value.duration}, exact charge ${value.exact_charge}. Native FLINT/Arb${value.native_precision_bits}; independent Arb${value.oracle_precision_bits} root checks on every step.`);
      for(const role of ['current','reset']) {
        const r=value.roles[role];
        add('p',`${role}: entry ${r.entry} → completion ${r.completion}; ${r.target_steps} actual target steps, gain ${r.local_gain}.`);
      }
      add('p',`Elapsed ${(value.elapsed_seconds/60).toFixed(1)} minutes against a ${value.cap_seconds/60}-minute cap. No supporting trajectory tail.`);
      add('p','One primary current trajectory and one reset comparison. Current creates one child; reset has no live event. Aggregate native support remains deferred.');
      add('p',`${value.pressure.length} checkpoint control reports; shared occurrence accounting is process-local.`);
      const a=add('a','Retained C_CI campaign summary');a.href=value.source_url;a.target='_blank';a.rel='noopener';
      status.textContent='Native C_CI endpoint verified; user review pending.';
    }catch(error){if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined')document.getElementById('spark-native-cci-campaign-refresh')?.addEventListener('click',
  nativeCCICampaignLoader(document.getElementById('spark-native-cci-campaign-output'),document.getElementById('spark-native-cci-campaign-status')));
