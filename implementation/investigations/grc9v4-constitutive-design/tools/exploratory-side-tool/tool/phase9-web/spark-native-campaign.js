import {canonicalBasin} from './basin.js';

export async function checkedNativeCampaign(value) {
  const {projection_digest, ...body} = value;
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalBasin(body)));
  const actual = [...new Uint8Array(bytes)].map(x => x.toString(16).padStart(2, '0')).join('');
  if (projection_digest !== '170b50f7330fcead0c945cf86a9e0395c52abbefc70cf623800be3f70edb6ada' || actual !== projection_digest ||
      value.schema !== 'grc9v4_native_spark_campaign_surface_v1' ||
      value.native_endpoint_verified !== true || value.native_completion_support !== false ||
      value.user_accepted !== false || value.full_trajectory_runs !== 2 ||
      value.physical_supporting_tail_steps !== 0 ||
      value.source_url !== '/api/native-spark/c-os/campaign/source')
    throw new Error('Unbound native campaign or changed acceptance scope');
  return value;
}

export function nativeCampaignLoader(output, status, fetcher=fetch, create=tag=>document.createElement(tag)) {
  let sequence = 0;
  return async () => {
    const ticket = ++sequence;
    output.replaceChildren(); status.textContent = 'Checking native C_OS campaign…';
    try {
      const response = await fetcher('/api/native-spark/c-os/campaign');
      if (!response.ok) throw new Error('Native campaign unavailable');
      const value = await checkedNativeCampaign(await response.json());
      if (ticket !== sequence) return;
      const add = (tag, text) => {const e=create(tag); e.textContent=text; output.append(e); return e;};
      add('p', `${value.target_vertices} vertices / ${value.target_edges} edges; duration ${value.duration}; exact charge ${value.exact_charge} throughout.`);
      for (const role of ['current', 'reset']) {
        const row=value.roles[role];
        add('p', `${role}: entry ${row.entry}, completion window ends ${row.completion}; local gain ${row.local_gain}.`);
      }
      add('p', `${(value.elapsed_seconds/60).toFixed(1)} minutes against a ${value.cap_seconds/60}-minute cap; peak memory ${value.peak_rss_mib.toFixed(1)} MiB.`);
      add('p', 'Every step independently checked. No supporting trajectory tail. Current creates one child; reset is a comparison with zero live gain.');
      add('p', 'C_OS endpoint verified; user review and aggregate native capability adoption remain pending.');
      add('p', `${value.evidence_storage.exact_reconstructed_transitions} exact archived transitions; ${value.evidence_storage.complete_diagnostic_samples} full diagnostic samples; ${(value.evidence_storage.compressed_bytes/1048576).toFixed(2)} MiB compact evidence.`);
      const storageLink=add('a', 'Compact evidence and reconstruction provenance'); storageLink.href=value.evidence_storage.source_url; storageLink.target='_blank'; storageLink.rel='noopener';
      const link=add('a', 'Retained native campaign'); link.href=value.source_url; link.target='_blank'; link.rel='noopener';
      status.textContent='Native C_OS campaign verified; review pending.';
    } catch (error) {
      if (ticket !== sequence) return;
      output.replaceChildren(); status.textContent=String(error);
    }
  };
}

if (typeof document !== 'undefined') document.getElementById('spark-native-campaign-refresh')?.addEventListener('click',
  nativeCampaignLoader(document.getElementById('spark-native-campaign-output'), document.getElementById('spark-native-campaign-status')));
