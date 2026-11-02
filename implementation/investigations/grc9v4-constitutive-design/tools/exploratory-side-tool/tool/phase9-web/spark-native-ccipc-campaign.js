import {canonicalBasin} from './basin.js';

export async function checkedNativeCCIPCCampaign(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
  if (projection_digest !== '5eab052fd7633aa80df151b8b04f9d3e0dc708191fc99f80bae1b1a9285864d7' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_ccipc_campaign_surface_v1' || value.family !== 'C_CI_PC' ||
      value.native_endpoint_verified !== true || value.native_completion_support !== false ||
      value.full_trajectory_runs !== 2 || value.physical_supporting_tail_steps !== 0 ||
      value.roles.current.local_gain !== 1 || value.roles.reset.local_gain !== 0 ||
      value.source_url !== '/api/native-spark/c-ci-pc/campaign/source')
    throw new Error('Unbound C_CI_PC campaign or changed endpoint scope');
  return value;
}

export function nativeCCIPCCampaignLoader(output,status,fetcher=fetch,create=tag=>document.createElement(tag)) {
  let sequence=0;
  return async()=>{
    const ticket=++sequence;
    output.replaceChildren();status.textContent='Checking native C_CI_PC completion evidence…';
    try {
      const response=await fetcher('/api/native-spark/c-ci-pc/campaign');
      if (!response.ok) throw new Error('Native C_CI_PC campaign unavailable');
      const value=await checkedNativeCCIPCCampaign(await response.json());
      if(ticket!==sequence)return;
      const add=(tag,text)=>{const e=create(tag);e.textContent=text;output.append(e);return e;};
      add('p',`${value.target_vertices} vertices / ${value.target_edges} edges, duration ${value.duration}, exact charge ${value.exact_charge}. Native FLINT/Arb${value.native_precision_bits}; independent Arb${value.oracle_precision_bits} whole C/Z history checks on every step.`);
      for(const role of ['current','reset']) {
        const r=value.roles[role];
        add('p',`${role}: entry ${r.entry} → completion ${r.completion}; ${r.target_steps} actual target steps, gain ${r.local_gain}.`);
      }
      add('p',`Active execution ${(value.elapsed_seconds/60).toFixed(1)} minutes against a ${value.profiling_target_seconds/60}-minute profiling target. Timing overruns are reported, not used to discard valid results. No supporting trajectory tail.`);
      add('p',`Both completed journals passed cold replay: ${Object.values(value.cold_checkpoint_validation).reduce((n,r)=>n+r.replayed_steps,0)} ordinary transitions revalidated. These are checkpoint controls, not supporting physical tails.`);
      if (value.evidence_storage) add('p',`Compact evidence: ${(value.evidence_storage.retained_compressed_bytes/1048576).toFixed(2)} MiB; all ${value.evidence_storage.independently_verified_transitions} exact transitions independently checked, plus ${value.evidence_storage.complete_diagnostic_samples} complete diagnostic samples. Expanded intermediate matrices are omitted.`);
      if (value.validation_repair) add('p', 'Cold reset validation required the shared current authority to be restored first. Both primary traces are unchanged; elapsed time includes the initial check and the corrected paired validation.');
      add('p','One primary current trajectory and one reset comparison. Current creates one child; reset has no live event. Aggregate native support remains deferred.');
      add('p',`${value.pressure.length} checkpoint control reports; shared occurrence accounting is process-local.`);
      const a=add('a','Retained C_CI_PC campaign summary');a.href=value.source_url;a.target='_blank';a.rel='noopener';
      status.textContent='Native C_CI_PC endpoint verified; retained execution evidence.';
    }catch(error){if(ticket!==sequence)return;output.replaceChildren();status.textContent=String(error);}
  };
}

if(typeof document!=='undefined')document.getElementById('spark-native-ccipc-campaign-refresh')?.addEventListener('click',
  nativeCCIPCCampaignLoader(document.getElementById('spark-native-ccipc-campaign-output'),document.getElementById('spark-native-ccipc-campaign-status')));
