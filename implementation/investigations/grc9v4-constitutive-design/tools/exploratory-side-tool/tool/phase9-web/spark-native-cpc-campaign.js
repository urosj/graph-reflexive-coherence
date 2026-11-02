import {canonicalBasin} from './basin.js';

export async function checkedNativeCPCCampaign(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if (projection_digest !== '81db30258e8b53b68c8e39166399b4f92243920ce86b1912b5d71c72701f59d7' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_cpc_campaign_surface_v1' || value.family !== 'C_PC' ||
      value.native_endpoint_verified !== true || value.native_completion_support !== false ||
      value.full_trajectory_runs !== 2 || value.physical_supporting_tail_steps !== 0 ||
      value.roles.current.local_gain !== 1 || value.roles.reset.local_gain !== 0 ||
      value.source_url !== '/api/native-spark/c-pc/campaign/source')
    throw new Error('Unbound C_PC campaign or changed endpoint scope');
  return value;
}

export function nativeCPCCampaignLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;
    output.replaceChildren();status.textContent='Checking native C_PC completion evidence…';
    try {
      const response=await fetcher('/api/native-spark/c-pc/campaign');
      if (!response.ok) throw new Error('Native C_PC campaign unavailable');
      const value=await checkedNativeCPCCampaign(await response.json());
      if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p',`${value.target_vertices} vertices / ${value.target_edges} edges, duration ${value.duration}, exact charge ${value.exact_charge}. Native FLINT/Arb${value.native_precision_bits}; independent Arb${value.oracle_precision_bits} whole C/Z history checks on every step.`);
      for(const role of ['current','reset']) {
        const r=value.roles[role];
        add('p',`${role}: entry ${r.entry} → completion ${r.completion}; ${r.target_steps} actual target steps, gain ${r.local_gain}.`);
      }
      add('p',`Active execution ${(value.elapsed_seconds/60).toFixed(1)} minutes against a ${value.profiling_target_seconds/60}-minute profiling target. Timing overruns are reported, not used to discard valid results. No supporting trajectory tail.`);
      add('p',`The completed current trace is preserved. Reset continues after exact checkpoint replay; ${value.recovery.checkpoint_replay_target_steps} retained target steps were matched before continuation. Journal validation and checkpoint controls are included in active execution time.`);
      add('p',`The total includes ${(value.failed_recovery_seconds/60).toFixed(1)} minutes from a recovery attempt whose evidence publication failed; the continuation evidence was regenerated.`);
      add('p','One primary current trajectory and one reset comparison. Current creates one child; reset has no live event. Aggregate native support remains deferred.');
      add('p',`${value.pressure.length} checkpoint control reports; shared occurrence accounting is process-local.`);
      const a=add('a','Retained C_PC campaign summary');a.href=value.source_url;a.target='_blank';a.rel='noopener';
      status.textContent='Native C_PC endpoint verified; user review pending.';
    }catch(error){if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined')document.getElementById('spark-native-cpc-campaign-refresh')?.addEventListener('click',
  nativeCPCCampaignLoader(document.getElementById('spark-native-cpc-campaign-output'),document.getElementById('spark-native-cpc-campaign-status')));
