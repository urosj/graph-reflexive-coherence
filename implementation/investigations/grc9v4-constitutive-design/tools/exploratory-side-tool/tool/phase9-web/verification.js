import {G2_REGISTRY} from './g2-registry.js';
import {AGGREGATE_REVIEW} from './aggregate-review.js';
import {SPECIALIZATION_REVIEW} from './specialization-review.js';
const acceptedRows = G2_REGISTRY.records.filter(r => r.state === 'accepted');
const acceptedSupport = acceptedRows.map(r => r.complete_profile_id).sort();
const acceptedProfile = G2_REGISTRY.records.find(r => r.adapter === 'historical_c_os').complete_profile_id;
const equal = (a,b) => canonical(a) === canonical(b);

export function checkedG2(value, implementation) {
  const expected = G2_REGISTRY.records.map(r => ({
    ...Object.fromEntries(['profile_family_id','complete_profile_id','gate','state','review','acceptance'].map(k=>[k,r[k]])),
    G2_accepted:r.state==='accepted', G3_accepted:false, aggregate_closed:false,
    all_ordered_pairs_verified:false, new_runtime_iterations_authorized:[], admitted_specialization_support_sets:[]
  }));
  if (implementation ? !equal(value.profile_g2,expected) : value.profile_g2 !== undefined)
    throw new Error('Untrusted G2 registry projection');
  const preceding = [];
  for (const row of G2_REGISTRY.records) {
    const a = value[row.view_key];
    if (!implementation) {
      if (a !== undefined) throw new Error('Unverified boundary cannot publish a G2 view');
      continue;
    }
    if (!a) throw new Error('Missing registered G2 view');
    if (row.adapter !== 'historical_c_os') {
      const accepted = row.state === 'accepted';
      const obligations = {'G2-EXACT-PRODUCT':'satisfied_for_exact_declared_scope','G2-ORDERED-ENDPOINTS':'satisfied_for_exact_declared_scope','G2-INTEGRATED-REVIEW':'satisfied_for_exact_declared_scope'};
      if (value[row.bounded_view_key]?.user_accepted !== true ||
          a.status !== (accepted ? 'accepted' : 'pass_proposal_pending_G2_acceptance') ||
          a.gate !== row.gate || Object.entries(row.review_metrics).some(([k,v])=>a[k]!==v) ||
          a.user_accepted !== accepted || a.G2_accepted !== accepted ||
          a.G3_accepted !== false || a.aggregate_closed !== false || a.all_ordered_pairs_verified !== false ||
          !equal(a.new_G2_support, accepted ? [row.complete_profile_id] : []) ||
          !equal(a.proposed_additional_support,[row.complete_profile_id]) ||
          !equal(a.accepted_support_unchanged,[...preceding].sort()) || !equal(a.obligations,obligations) ||
          a.record_path !== row.review.path || a.record_digest !== row.review.record_digest)
        throw new Error('Unverified or widened registered G2 review');
      if (accepted) {
        if (a.acceptance_path !== row.acceptance.path || a.acceptance_digest !== row.acceptance.record_digest ||
            !equal(a.accepted_generic_runtime_support,acceptedSupport)) throw new Error('Untrusted G2 acceptance');
      } else if (a.acceptance_path !== undefined || a.acceptance_digest !== undefined ||
                 a.accepted_generic_runtime_support !== undefined) throw new Error('Proposal invented acceptance');
    }
    if (row.state === 'accepted') preceding.push(row.complete_profile_id);
  }
}

export function checkedReconciliation(value, implementation) {
  const expected = G2_REGISTRY.reconciliation_views;
  const keys = Object.keys(value).filter(k => k.endsWith('_local_product') || k.endsWith('_crossings'));
  if (!equal(keys.sort(), implementation ? Object.keys(expected).sort() : []))
    throw new Error('Missing or unregistered bounded reconciliation view');
  if (implementation) for (const [key, view] of Object.entries(expected)) {
    if (!equal(value[key], view)) throw new Error('Unverified or widened bounded reconciliation: ' + key);
  }
}

export function renderReconciliation(value, body, create = tag => document.createElement(tag)) {
  body.replaceChildren();
  for (const [key, expected] of Object.entries(G2_REGISTRY.reconciliation_views)) {
    if (!equal(value[key], expected)) continue;
    const row = create('tr');
    for (const text of [key, expected.verified_local_cells ?? expected.reconciled_crossing_cells,
                        expected.user_accepted ? 'Bounded reconciliation accepted' :
                          key.endsWith('_crossings') ? 'Crossing evidence pending review' : 'Local evidence pending review',
                        expected.record_path]) {
      const cell = create('td'); cell.textContent = String(text); row.append(cell);
    }
    body.append(row);
  }
}

export function checkedAggregate(value, implementation) {
  const current = value.profile_aggregate_reconciliation;
  if (implementation ? !equal(current, AGGREGATE_REVIEW) : current !== undefined)
    throw new Error('Missing, stale or widened aggregate reconciliation');
  if (implementation && !equal(current.accepted_generic_runtime_support, acceptedSupport))
    throw new Error('Aggregate support differs from accepted registry');
}

export function checkedSpecialization(value, implementation) {
  const review = value.specialization_admission_review;
  if (implementation ? !equal(review, SPECIALIZATION_REVIEW) : review !== undefined)
    throw new Error('Missing, stale or widened specialization admission review');
  if (implementation && !equal(review.proposed_consumed_support, acceptedSupport))
    throw new Error('Specialization review differs from accepted generic support');
}

export function checkedStatus(value) {
  if (!['phase9_governance_status_v1','phase9_governance_status_v2'].includes(value?.schema) || value.output_class !== "implementation_verification_status_not_forensic_trace") throw new Error("Unrecognized verification status");
  const implementation = value.schema === 'phase9_governance_status_v2' && value.current_boundary === 'passed';
  checkedG2(value, implementation);
  checkedAggregate(value, implementation);
  checkedSpecialization(value, implementation);
  if (typeof value.P9_G1_accepted !== 'boolean' || value.runtime_authorized !== implementation || (implementation && !value.P9_G1_accepted) || (value.schema === 'phase9_governance_status_v1' && value.P9_G1_accepted) || !Array.isArray(value.accepted_generic_runtime_support) || JSON.stringify(value.accepted_generic_runtime_support) !== JSON.stringify(implementation ? acceptedSupport : []) || !Array.isArray(value.admitted_specialization_support_sets) || value.admitted_specialization_support_sets.length !== 0) throw new Error("Unverified runtime authority or support");
  if (implementation && (value.g2_acceptance?.record_digest !== 'e7165dc2f4cfe159d397c7aa61ccfbc89a30909db888e6638ef1ffe5905ec6dd' || value.g2_acceptance?.gate !== 'P9-G2[C_OS]' || value.g2_acceptance?.alias !== 'P9-7.7-C_OS' || value.g2_acceptance?.G2_accepted !== true || value.g2_acceptance?.G3_accepted !== false || value.g2_acceptance?.tranche_4_status !== 'closed' || JSON.stringify(value.g2_acceptance?.accepted_generic_runtime_support) !== JSON.stringify([acceptedProfile]) || JSON.stringify(value.g2_acceptance?.new_runtime_iterations_authorized) !== '[]')) throw new Error('Missing or widened exact-profile G2 acceptance');
  if (!implementation && value.g2_acceptance !== undefined) throw new Error('Unverified boundary cannot advertise current G2 support');
  if (!implementation && value.initializer_runtime !== undefined) throw new Error('Unverified boundary cannot advertise migration acceptance');
  if (!implementation && value.event_runtime !== undefined) throw new Error('Unverified boundary cannot advertise event execution');
  checkedReconciliation(value, implementation);
  if (value.profile_conformance_review !== undefined) {
    const r = value.profile_conformance_review;
    if (!implementation || r.status !== 'reviewed_hold_pending_independent_review' || r.user_accepted !== false || r.aggregate_closed !== false || r.G3_accepted !== false || JSON.stringify(r.new_G2_support) !== '[]' || r.profile_count !== 10 || r.required_cells !== 305 || r.accepted_alias_cells !== 33 || r.unresolved_new_profile_cells !== 272 || r.numerical_tests_rerun !== 0 || r.new_execution_credit !== 0 || JSON.stringify(r.accepted_aliases) !== '["C_OS"]' || JSON.stringify(r.held_profiles) !== '["A_CI","C_CI","A_OS","A_RG2b","C_RG2b","A_PC","C_PC","A_CI_PC","C_CI_PC"]' || r.record_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.7-ProfileReview.json' || r.record_digest !== 'ce60e567de7a325f917444931e978fa142b2982cb911629532efd0c881d90cdc') throw new Error('Unverified or widened exact-profile review');
  }
  if (value.lineage_ownership_verification !== undefined) {
    const l = value.lineage_ownership_verification;
    if (!implementation || l.status !== 'accepted' || l.user_accepted !== true || l.aggregate_closed !== true || l.acceptance_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.6-Review.md' || l.acceptance_sha256 !== '2368d43b5fb7e4548dceffdb9b9fac92441170cf2730934fdf61a5ca0033e512' || l.G3_accepted !== false || JSON.stringify(l.new_G2_support) !== '[]' || l.test_count !== 4 || l.coherent_parent_rejections !== 10 || l.publication_rejections !== 3 || l.partition_rejections !== 3 || l.symbolic_rejections !== 16 || l.numerical_tests_rerun !== 0 || l.record_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.6-LineageOwnership.json' || l.record_digest !== '1321caf7fd2b532375b08e219285805475e77ce377785ca47a32b1cfa7a99354') throw new Error('Unverified or widened lineage-ownership scope');
  }
  if (value.failure_sequence_verification !== undefined) {
    const f = value.failure_sequence_verification;
    if (!implementation || f.status !== 'accepted' || f.user_accepted !== true || f.aggregate_closed !== true || f.acceptance_sha256 !== 'cfd83f4b1c5e9ae04f5deb04ca79788af04327660b82415f3d45306deb64a647' || f.acceptance_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.5-Review.md' || f.G3_accepted !== false || JSON.stringify(f.new_G2_support) !== '[]' || f.test_count !== 4 || f.rejection_cases !== 21 || f.numerical_tests_rerun !== 0 || JSON.stringify(f.reset_contexts) !== JSON.stringify(['ordinary','migration','event']) || f.record_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.5-FailureSequences.json' || f.record_digest !== '8563c051871a681654da4767031916357840a55e50f3cdb4b39e07089b843329') throw new Error('Unverified or widened failure-sequence scope');
  }
  if (value.target_reference_verification !== undefined) {
    const t = value.target_reference_verification;
    if (t.record_digest !== '547e2c932a121189dcc6b5ea8b33d3d6524167a74a142c526d6898a2be597e51') throw new Error('Target-reference execution identity changed');
    if (!implementation || t.status !== 'accepted' || t.user_accepted !== true || t.aggregate_closed !== true || t.acceptance_sha256 !== '40c38911b3a85a1863b2d1ee4a46ccc1a6daeda4d44f4bf97fa840a208c9b63f' || t.acceptance_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.4-Review.md' || t.G3_accepted !== false || JSON.stringify(t.new_G2_support) !== '[]' || t.test_count !== 4 || t.reference_rejections !== 40 || t.numerical_tests_rerun !== 0 || JSON.stringify(t.c_target_families) !== JSON.stringify(['C_OS','C_CI','C_RG2b','C_PC','C_CI_PC']) || t.record_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.4-TargetReference.json' || !/^[0-9a-f]{64}$/.test(t.record_digest)) throw new Error('Unverified or widened target-reference scope');
  }
  if (value.history_policy_verification !== undefined) {
    const h = value.history_policy_verification;
    if (!implementation || h.status !== 'accepted' || h.user_accepted !== true || h.aggregate_closed !== true || h.G3_accepted !== false || JSON.stringify(h.new_G2_support) !== '[]' || h.test_count !== 9 || h.baseline_test_count !== 6 || h.regression_test_count !== 3 || h.numerical_tests_rerun !== 0 || h.acceptance_sha256 !== '43dfc3b8be7c6183c6402eb2db9efa7378e0a0f1da684ebd614eac311977e7fb' || h.acceptance_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.3-Review.md' || h.record_digest !== '3dd332471957d0adae6597842ec6f2c90dfa2baa8c55e642b52fe6a3d03ba653' || h.regression_record_digest !== 'b42ecf99e7168b97d91502bcdc2b68d3213e4c6527255f5a628cd30ac9ff3498' || h.policy_cells !== 32 || h.native_crossings !== 5 || !/^[0-9a-f]{64}$/.test(h.record_digest)) throw new Error('Unverified or widened history-policy scope');
  }
  if (value.event_runtime !== undefined && (value.event_runtime.status !== 'accepted' || value.event_runtime.user_accepted !== true || value.event_runtime.aggregate_closed !== true || value.event_runtime.acceptance_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.2b-RuntimeReview.md' || value.event_runtime.acceptance_sha256 !== '9ac06f87275fe656a2650334517be319b9eb7c98c2b9710dae263a349237120d' || value.event_runtime.record_digest !== '420c4a6ed565edf48e61398f6dca8680b0b190915881e738085d410993bbd7db' || value.event_runtime.test_count !== 18 || value.event_runtime.case_count !== 27 || value.event_runtime.numerical_tests_rerun !== 0 || value.event_runtime.G3_accepted !== false || JSON.stringify(value.event_runtime.new_G2_support) !== '[]' || !Number.isInteger(value.event_runtime.test_count) || value.event_runtime.test_count <= 0 || !Number.isInteger(value.event_runtime.case_count) || value.event_runtime.case_count <= 0 || !/^[0-9a-f]{64}$/.test(value.event_runtime.record_digest))) throw new Error('Missing or widened event acceptance');
  if (value.P9_G1_accepted && value.approval_digest !== 'cd2c52f30477e1042bb903bd0553da237ddccc9cad373afecc1a84e4e0b37ea2') throw new Error('Missing recorded P9-G1 acceptance');
  if (implementation && (value.runtime_authority_state !== 'accepted_P9_G1_bounded_implementation_not_conformance' || !Array.isArray(value.implementation_scope) || value.implementation_scope.length !== (value.event_runtime === undefined ? 59 : 62))) throw new Error('Missing accepted P9-G1 scope');
  if (!implementation && value.P9_G1_accepted && (value.current_boundary !== 'failed_closed' || value.runtime_authority_state !== 'accepted_P9_G1_current_work_held' || value.implementation_scope !== undefined || value.permitted_runtime_paths !== undefined || value.dependency_ready_leaves !== undefined || value.foundation_acceptance !== undefined || value.request_acceptance !== undefined || value.result_acceptance !== undefined || value.harness_acceptance !== undefined || value.integration_acceptance !== undefined || value.geometry_acceptance !== undefined || value.stage_acceptance !== undefined || value.resource_acceptance !== undefined || value.numerical_pressure_acceptance !== undefined || value.preservation_acceptance !== undefined || value.reference_transport_acceptance !== undefined || value.c_current_acceptance !== undefined || value.c_controls_acceptance !== undefined || value.os_pass_acceptance !== undefined || value.os_operations_acceptance !== undefined || value.lifecycle_batch_authorization !== undefined || value.specification_correction !== undefined || value.receipt_parent_authority !== undefined || value.abundance_interface_authority !== undefined)) throw new Error('Held work cannot retain implementation permission');
  if (value.schema === 'phase9_governance_status_v2' && !['verified','unavailable','invalid'].includes(value.handoff_evidence?.status)) throw new Error('Unknown handoff evidence disposition');
  if (implementation && (value.foundation_acceptance?.record_digest !== '1e3f0ddb06b119fa46dc7609d05b7db0c3a4cbc07428c05b8a032da081ae9dd4' || JSON.stringify(value.foundation_acceptance?.accepted_iterations) !== JSON.stringify(['P9-2.1','P9-2.2']))) throw new Error('Missing accepted foundation');
  if (implementation && (value.request_acceptance?.record_digest !== 'ac07a2f7c93538454d9663aba78ca0eb5af385d7975582e4c21682f41ce4c17f' || JSON.stringify(value.request_acceptance?.accepted_iterations) !== JSON.stringify(['P9-2.3']))) throw new Error('Missing accepted requests');
  if (implementation && (value.result_acceptance?.record_digest !== '9d2fd4f0bb0445b9b3c46fd6f7e5b0ff710a8a85aceaeabacad44a477ff365a0' || JSON.stringify(value.result_acceptance?.accepted_iterations) !== JSON.stringify(['P9-2.4']))) throw new Error('Missing accepted results');
  if (implementation && (value.harness_acceptance?.record_digest !== 'e479a8e5935fc8740b59f96b31651070f842f73f92541bb84dbc1c9d63f59896' || JSON.stringify(value.harness_acceptance?.accepted_iterations) !== JSON.stringify(['P9-2.5']))) throw new Error('Missing accepted harness');
  if (implementation && (value.integration_acceptance?.record_digest !== 'e5ba16731e03dc916b8755c5999ab2b59acf431255612e76e0dcebe108104bc2' || JSON.stringify(value.integration_acceptance?.accepted_iterations) !== JSON.stringify(['P9-2.6']))) throw new Error('Missing accepted integration');
  if (implementation && (value.geometry_acceptance?.record_digest !== 'f119e1361500e72f58297bc8186f868954b4065c853fcdd089280a5d28f88618' || JSON.stringify(value.geometry_acceptance?.accepted_iterations) !== JSON.stringify(['P9-3.1']))) throw new Error('Missing accepted geometry');
  if (implementation && (value.stage_acceptance?.record_digest !== '425cd05eb85213185a4b531a09c16cefec4be992ac4755d404b5f263e09ebd0a' || JSON.stringify(value.stage_acceptance?.accepted_iterations) !== JSON.stringify(['P9-3.2']))) throw new Error('Missing accepted stages');
  if (implementation && (value.resource_acceptance?.record_digest !== '3e71b580090ba1712dbec4a1718653c2057e4062200f3367ba0c1ed7adeae6fa' || JSON.stringify(value.resource_acceptance?.accepted_iterations) !== JSON.stringify(['P9-3.3']))) throw new Error('Missing accepted resources');
  if (implementation && (value.numerical_pressure_acceptance?.record_digest !== '0626df41be15fdb2d5a5a7b4fa6f8be52693f8d3ba40297ae98acbe334f480c1' || JSON.stringify(value.numerical_pressure_acceptance?.accepted_iterations) !== JSON.stringify(['P9-3.4']))) throw new Error('Missing accepted numerical pressure');
  if (implementation && (value.preservation_acceptance?.record_digest !== 'b866b4b5d9b8b7ecdf087fd6f2a6d879810ec19464a9d3368ddddaf4d2edf43b' || JSON.stringify(value.preservation_acceptance?.accepted_iterations) !== JSON.stringify(['P9-3.5']))) throw new Error('Missing accepted prestate preservation');
  if (implementation && (value.reference_transport_acceptance?.record_digest !== 'ff07f5d71ad094d4c28f3fafdd0c0ca1d74f9f34f18678c8ff6909029b24358a' || JSON.stringify(value.reference_transport_acceptance?.accepted_iterations) !== JSON.stringify(['P9-4.1']))) throw new Error('Missing accepted C reference transport');
  if (implementation && (value.c_current_acceptance?.record_digest !== '5ce39f22e2999ee6f375648263a5902f883866420b497822cbf7daaa6e043b43' || JSON.stringify(value.c_current_acceptance?.accepted_iterations) !== JSON.stringify(['P9-4.2']))) throw new Error('Missing accepted C stage current');
  if (implementation && (value.c_controls_acceptance?.record_digest !== 'b2834e343fc50fa447ca430475a064157d27b431e27eb64ee721ff52e66a6f15' || JSON.stringify(value.c_controls_acceptance?.accepted_iterations) !== JSON.stringify(['P9-4.3']))) throw new Error('Missing accepted C control derivative');
  if (implementation && (value.os_pass_acceptance?.record_digest !== '37d61d733bf90b794e4c68f0b2d078f7d38b41aa3f4c0679457c24a3161ad074' || JSON.stringify(value.os_pass_acceptance?.accepted_iterations) !== JSON.stringify(['P9-4.4']))) throw new Error('Missing accepted C OS pass');
  if (implementation && (value.os_operations_acceptance?.record_digest !== 'b37b037f0baa0fe5e291c96deba0520933070077b8d5a6a64995fbca21b5e274' || JSON.stringify(value.os_operations_acceptance?.accepted_iterations) !== JSON.stringify(['P9-4.5']))) throw new Error('Missing accepted C OS operations');
  if (implementation && (value.lifecycle_batch_authorization?.record_digest !== 'fe11cfd2db36a9e1a74301aeaf89e316a3e93e7d3f5ea9d5f1197e199ee27d6b' || value.lifecycle_batch_authorization?.audit_status !== 'findings_closed_after_correction' || JSON.stringify(value.lifecycle_batch_authorization?.execution_order) !== JSON.stringify(['P9-4.7a','P9-4.7b']) || JSON.stringify(value.lifecycle_batch_authorization?.combined_audit_scope) !== JSON.stringify(['P9-4.6','P9-4.7a','P9-4.7b']))) throw new Error('Missing accepted lifecycle batch and audit closure');
  if (implementation && (value.specification_correction?.record_digest !== '56f1d4378eb8273d261b76aff3b128c526fb5064fa3bceace5c73fbb1f9f9903' || value.specification_correction?.release_id !== 'grcv4-spec-release-sha256:7b8b4d4e32e48fd35f70421cce7f547eebb21dd81389764061efe6e1a8c19886')) throw new Error('Missing accepted mapped-vector successor release');
  if (implementation && (value.receipt_parent_authority?.record_digest !== 'ba7d69189c527153828b02c2bb3311899b036a634446de9ad8f36af6592c28f8' || value.receipt_parent_authority?.policy_id !== 'grcv4-previous-successful-primary-v1' || value.receipt_parent_authority?.G2_accepted !== false || value.receipt_parent_authority?.release_id !== 'grcv4-spec-release-sha256:f777519824f86c3e9382bcf9b45cba28554351506f354d3f778746e2aaff5c6b')) throw new Error('Missing bounded receipt-parent successor');
  if (implementation && (value.abundance_interface_authority?.record_digest !== 'd9488700be9624da8500c1e533aa65d33b4f36a3307748ad12fd66449d8fe053' || value.abundance_interface_authority?.policy_id !== 'grcv4-family-abundance-diagnostic-v1' || value.abundance_interface_authority?.release_id !== 'grcv4-spec-release-sha256:e2acd9df0cc02c5fd4bbed4989ff5d7da3a819adeb2950d922b8a6ef4bf35f24' || value.abundance_interface_authority?.G2_accepted !== false || value.abundance_interface_authority?.numeric_definition_admitted !== false)) throw new Error('Missing bounded abundance successor');
  if (implementation && (JSON.stringify(value.dependency_ready_leaves) !== JSON.stringify(["P9-2.1","P9-2.2","P9-2.3","P9-2.4","P9-2.5","P9-2.6","P9-3.1","P9-3.2","P9-3.3","P9-3.4","P9-3.5","P9-4.1","P9-4.2","P9-4.3","P9-4.4","P9-4.5","P9-4.6","P9-4.7a","P9-4.7b","P9-4.9.1","P9-4.9.1a","P9-4.9.2","P9-4.9.3","P9-5.1","P9-5.2","P9-5.3","P9-5.4","P9-6.1a","P9-6.1b","P9-6.1c","P9-6.2a","P9-6.2b","P9-6.2c","P9-6.3a","P9-6.3b","P9-6.3c","P9-6.4a","P9-6.4b","P9-6.4c","P9-6.4d","P9-6.5","P9-7.1","P9-7.1-A_CI","P9-7.1-A_CI_PC","P9-7.1-A_OS","P9-7.1-A_PC","P9-7.1-A_RG2b","P9-7.1-C_CI","P9-7.1-C_CI_PC","P9-7.1-C_OS","P9-7.1-C_PC","P9-7.1-C_RG2b","P9-7.2a","P9-7.2a-A_CIPC_PC","P9-7.2a-A_C_DROP","P9-7.2a-A_C_NH","P9-7.2a-A_C_PC","P9-7.2a-A_NH_NH","P9-7.2a-A_NH_PC","P9-7.2a-A_PC_CIPC","P9-7.2a-A_PC_NH","P9-7.2a-C_CIPC_PC","P9-7.2a-C_NH_NH","P9-7.2a-C_NH_PC","P9-7.2a-C_OS-NH-NH","P9-7.2a-C_OS-UNSUPPORTED","P9-7.2a-C_PC_CIPC","P9-7.2a-C_PC_NH","P9-7.2a-C_TO_A_UNRESOLVED",...(value.event_runtime === undefined ? [] : ["P9-7.2b"]),"P9-7.2b-C_OS-MAPPED","P9-7.3-C_OS","P9-7.4-C_OS","P9-7.5-C_OS","P9-7.6-C_OS"]) || !Array.isArray(value.permitted_runtime_paths) || value.permitted_runtime_paths.length !== (value.event_runtime === undefined ? 47 : 50) || !['src/pygrc/models/__init__.py','pyproject.toml','tests/models/grcv4_conformance_harness.py','tests/models/grcv4_reference_oracles.py',"src/pygrc/models/grc_v4_geometry.py","src/pygrc/models/grc_v4_transport.py","tests/models/test_grc_v4_geometry.py","tests/models/test_grc_v4_transport.py","src/pygrc/models/grc_v4_candidate_c.py","tests/models/test_grc_v4_candidate_c.py","src/pygrc/models/grc_v4_realizations.py","tests/models/test_grc_v4_realizations.py","src/pygrc/models/grc_v4_lifecycle.py","tests/models/test_grc_v4_lifecycle.py","src/pygrc/models/grc_v4_candidate_a.py","tests/models/test_grc_v4_candidate_a.py","src/pygrc/models/grc_v4_ci.py","tests/models/test_grc_v4_ci.py","src/pygrc/models/grc_v4_pc.py","tests/models/test_grc_v4_pc.py","tests/models/test_grc_v4_cipc.py","src/pygrc/models/grc_v4_rg2b.py","tests/models/test_grc_v4_rg2b.py","src/pygrc/models/grc_v4_rg2b_graph.py","tests/models/test_grc_v4_rg2b_graph.py","tests/models/test_grc_v4_generic_lifecycle.py","src/pygrc/models/grc_v4_migration.py","tests/models/test_grc_v4_migration.py","src/pygrc/models/grc_v4_initializer.py","tests/models/test_grc_v4_initializer.py","src/pygrc/models/grc_v4_assets/grc-v4-a-initializer-release.json","src/pygrc/models/grc_v4_assets/grc-v4-a-initializer-schema.json"].concat(value.event_runtime === undefined ? [] : ["src/pygrc/models/grc_v4_events.py", "tests/models/test_grc_v4_events.py", "tests/models/test_grc_v4_event_audit.py"]).every(path => value.permitted_runtime_paths.includes(path)))) throw new Error('Invalid dependency-ready permission');
  if (!['passed', 'failed_closed'].includes(value.current_boundary)) throw new Error("Unknown boundary disposition");
  if (!['not_current', 'recorded_pass_matching_current_inputs'].includes(value.recorded_full_verification)) throw new Error("Unknown recorded evidence disposition");
  if (value.current_boundary !== 'passed' && value.recorded_full_verification !== 'not_current') throw new Error("Failed boundary cannot retain a passing receipt");
  if (value.current_boundary === 'passed') {
    if (implementation) {
      const runtime = value.initializer_runtime;
      if (runtime?.status !== 'accepted' || runtime.release_id !== 'grcv4-spec-release-sha256:e44dcd77a78a752c0e62f559243b88faff0bf90af1ee11a587f25d27e8a8abc7' ||
          runtime.record_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.2a-InitializerRuntime.json' || !/^[0-9a-f]{64}$/.test(runtime.record_digest) || runtime.tests_run !== 25 ||
          !['producer_implemented', 'payload_specification_complete', 'positive_migration_verified'].every(k => runtime[k] === true) ||
          !['aggregate_closed', 'user_accepted'].every(k => runtime[k] === true) || runtime.G3_accepted !== false || runtime.numerical_tests_rerun !== 0 ||
          runtime.acceptance_path !== 'implementation/phase-9-grcv4/tranche-7/P9-7.2a-InitializerRuntimeReview.md' || runtime.acceptance_sha256 !== 'a64bfe5e90e331495b7351d0b010c73b1de01f44332232b6b4d7b23046d23191' ||
          JSON.stringify(runtime.accepted_migration_classes) !== JSON.stringify(['nonhistory_to_nonhistory','nonhistory_to_persistent','persistent_to_nonhistory','PC_to_CI_PC','CI_PC_to_PC','A_to_C','C_to_A']) ||
          JSON.stringify(runtime.new_G2_support) !== '[]' || JSON.stringify(runtime.positive_target_families) !== JSON.stringify(['A_OS','A_CI','A_PC','A_CI_PC','A_RG2b'])) throw new Error('Missing or widened initializer runtime evidence');
    }
    if (!/^[0-9a-f]{64}$/.test(value.policy_digest) || !Array.isArray(value.source_refs) || !value.source_refs.length || !value.source_refs.every(r => typeof r.path === 'string' && /^[0-9a-f]{64}$/.test(r.sha256))) throw new Error('Missing verified source bindings');
    const ids = implementation ? ['P9-1.4','P9-1.5','P9-1.6','P9-1.7','P9-1.8','P9-1.9'] : ['P9-1.7','P9-1.8'];
    if (!Array.isArray(value.iterations) || value.iterations.length !== ids.length || !value.iterations.every((r, i) => r.iteration_id === ids[i] && ['in_progress', 'implemented_and_verified'].includes(r.status) && r.reviewer_decision === (implementation ? 'accepted_by_user' : 'pending_user_review'))) throw new Error('Invalid leaf authority');
  }
  return value;
}

// This is the sorted-key JSON format of planning status, not the V4 runtime codec.
export function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value !== null && typeof value === 'object') return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(',')}}`;
  return JSON.stringify(value);
}
export async function verifiedStatus(value) {
  checkedStatus(value);
  const { status_digest, ...body } = value;
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical(body)));
  const actual = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
  if (actual !== status_digest) throw new Error('Status digest mismatch');
  if (!Array.isArray(value.source_refs) || !Array.isArray(value.iterations)) throw new Error('Missing source or leaf records');
  return value;
}

export async function verifiedParents(value) {
  if (value?.authority_extension_digest !== 'd9ba802c9fd29169bcea4adac3adc83cad1f1ef6a79e2dba99b6dff3f1a10188') throw new Error('Unadmitted parent authority identity');
  if (value?.schema !== 'grcv4_p9492_parent_surface_v1' || value.policy_id !== 'grcv4-previous-successful-primary-v1' || value.G2_accepted !== false || value.runtime_conformance_inferred !== false || !Array.isArray(value.contracts) || value.contracts.length !== 3) throw new Error('Unknown parent authority or widened conformance');
  const {projection_digest, ...body} = value;
  const hash = async v => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical(v)))), b => b.toString(16).padStart(2, '0')).join('');
  if (await hash(body) !== projection_digest) throw new Error('Parent projection digest mismatch');
  for (const trace of [value.claim, value.debt, value.object, ...value.contracts]) {
    const {trace_digest, ...payload} = trace;
    if (trace.output_class !== 'forensic_evidence_trace' || trace.authority_extension_digest !== value.authority_extension_digest || await hash(payload) !== trace_digest || !trace.rows.length || trace.rows.some(r => !r.source_ref || !r.edge_refs.length)) throw new Error('Missing source-bound parent trace');
  }
  return value;
}

let parentGeneration = 0;
let parentValue = null;
function renderParents() {
  const output = document.querySelector('#parents-output');
  output.textContent = '';
  if (!parentValue) return;
  const key = document.querySelector('#parent-view').value;
  output.textContent = JSON.stringify(['claim', 'debt', 'object'].includes(key) ? parentValue[key] : parentValue.contracts[Number(key)], null, 2);
}
async function loadParents() {
  const generation = ++parentGeneration;
  parentValue = null;
  renderParents();
  const status = document.querySelector('#parents-status');
  status.textContent = 'Checking source-bound parent authority…';
  try {
    const response = await fetch('/api/receipt-parents', {cache: 'no-store'});
    if (!response.ok) throw new Error('Parent authority unavailable');
    const value = await verifiedParents(await response.json());
    if (generation !== parentGeneration) return;
    parentValue = value;
    status.textContent = `Accepted policy: ${value.policy_id}. Source authority only; runtime gate status is reported above.`;
    renderParents();
  } catch (error) {
    if (generation === parentGeneration) status.textContent = `Held: ${error.message}`;
  }
}
if (typeof document !== 'undefined') {
  document.querySelector('#parents-refresh')?.addEventListener('click', loadParents);
  document.querySelector('#parent-view')?.addEventListener('change', renderParents);
}

export async function verifiedAbundance(value) {
  if (value?.authority_extension_digest !== 'd9ba802c9fd29169bcea4adac3adc83cad1f1ef6a79e2dba99b6dff3f1a10188') throw new Error('Unadmitted abundance authority identity');
  if (value?.schema !== 'grcv4_p9491a_abundance_surface_v1' || value.policy_id !== 'grcv4-family-abundance-diagnostic-v1' || value.numeric_definition_admitted !== false || value.G2_accepted !== false || value.runtime_conformance_inferred !== false || !Array.isArray(value.contracts) || value.contracts.length !== 3) throw new Error('Unknown abundance authority or widened conformance');
  const {projection_digest, ...body} = value;
  const hash = async v => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical(v)))), b => b.toString(16).padStart(2, '0')).join('');
  if (await hash(body) !== projection_digest) throw new Error('Abundance projection digest mismatch');
  for (const trace of [value.claim, value.debt, value.object, ...value.contracts]) {
    const {trace_digest, ...payload} = trace;
    if (trace.output_class !== 'forensic_evidence_trace' || trace.authority_extension_digest !== value.authority_extension_digest || await hash(payload) !== trace_digest || !trace.rows.length || trace.rows.some(r => !r.source_ref || !r.edge_refs.length)) throw new Error('Missing source-bound abundance trace');
  }
  return value;
}

let abundanceGeneration = 0;
let abundanceValue = null;
function renderAbundance() {
  const output = document.querySelector('#abundance-output');
  output.textContent = '';
  if (!abundanceValue) return;
  const key = document.querySelector('#abundance-view').value;
  output.textContent = JSON.stringify(['claim', 'debt', 'object'].includes(key) ? abundanceValue[key] : abundanceValue.contracts[Number(key)], null, 2);
}
async function loadAbundance() {
  const generation = ++abundanceGeneration;
  abundanceValue = null;
  renderAbundance();
  const status = document.querySelector('#abundance-status');
  status.textContent = 'Checking source-bound abundance authority…';
  try {
    const response = await fetch('/api/abundance', {cache: 'no-store'});
    if (!response.ok) throw new Error('Abundance authority unavailable');
    const value = await verifiedAbundance(await response.json());
    if (generation !== abundanceGeneration) return;
    abundanceValue = value;
    status.textContent = `Accepted policy: ${value.policy_id}. Source authority only; runtime gate status is reported above.`;
    renderAbundance();
  } catch (error) {
    if (generation === abundanceGeneration) status.textContent = `Held: ${error.message}`;
  }
}
if (typeof document !== 'undefined') {
  document.querySelector('#abundance-refresh')?.addEventListener('click', loadAbundance);
  document.querySelector('#abundance-view')?.addEventListener('change', renderAbundance);
}

export async function verifiedInitializer(value) {
  const expected = 'fa59abda356446daca516b33028a07a48ec63aaacb8f961cd274a425dca48dd1';
  const {projection_digest, ...body} = value ?? {};
  const hash = async v => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical(v)))), b => b.toString(16).padStart(2, '0')).join('');
  // Pin the entire source-exact projection, not only rehashable status labels.
  if (projection_digest !== expected || await hash(body) !== expected ||
      value.schema !== 'grcv4_p972a_initializer_surface_v1' ||
      value.authority_extension_digest !== 'd9ba802c9fd29169bcea4adac3adc83cad1f1ef6a79e2dba99b6dff3f1a10188' ||
      value.producer_choice_resolved !== true ||
      ['payload_specification_complete', 'positive_migration_verified', 'aggregate_closed', 'G2_accepted', 'G3_accepted', 'runtime_conformance_inferred'].some(k => value[k] !== false)) {
    throw new Error('Unadmitted initializer authority or widened completion claim');
  }
  return value;
}

let initializerGeneration = 0;
let initializerValue = null;
function renderInitializer() {
  const output = document.querySelector('#initializer-output');
  output.textContent = '';
  if (!initializerValue) return;
  const key = document.querySelector('#initializer-view').value;
  output.textContent = JSON.stringify(key === 'contract' ? initializerValue.contracts[0] : initializerValue[key], null, 2);
}
async function loadInitializer() {
  const generation = ++initializerGeneration;
  initializerValue = null;
  renderInitializer();
  const status = document.querySelector('#initializer-status');
  status.textContent = 'Checking accepted initializer source…';
  try {
    const response = await fetch('/api/a-initializer', {cache: 'no-store'});
    if (!response.ok) throw new Error('Initializer authority unavailable');
    const value = await verifiedInitializer(await response.json());
    if (generation !== initializerGeneration) return;
    initializerValue = value;
    status.textContent = 'Accepted optional A design trace, not runtime evidence. Later seven-class P9-7.2a acceptance is shown in current verification above; wider G2/G3 remain separate.';
    renderInitializer();
  } catch (error) {
    if (generation === initializerGeneration) status.textContent = `Held: ${error.message}`;
  }
}
if (typeof document !== 'undefined') {
  document.querySelector('#initializer-refresh')?.addEventListener('click', loadInitializer);
  document.querySelector('#initializer-view')?.addEventListener('change', renderInitializer);
}

export function renderG2Profiles(value, body, createElement) {
  body.replaceChildren();
  for (const row of value.profile_g2 || []) {
    const tr = createElement('tr');
    for (const text of [row.profile_family_id, row.complete_profile_id,
      row.G2_accepted ? 'G2 accepted' : 'G2 proposal — not accepted', row.review.path]) {
      const td = createElement('td'); td.textContent = text; tr.append(td);
    }
    body.append(tr);
  }
}

let refreshGeneration = 0;
async function refresh() {
  const generation = ++refreshGeneration;
  const status = document.querySelector('#status');
  const button = document.querySelector('#download');
  button.disabled = true;
  document.querySelector('#boundary').textContent = 'Not verified';
  document.querySelector('#authority').textContent = 'Not verified / permission withheld';
  document.querySelector('#next-work').textContent = 'Next work not verified.';
  document.querySelector('#recorded').textContent = 'Not current';
  document.querySelector('#handoff').textContent = 'Not checked';
  document.querySelector('#sources').replaceChildren();
  document.querySelector('#g2-profiles').replaceChildren();
  document.querySelector('#reconciliation-views').replaceChildren();
  document.querySelector('#iterations').textContent = 'No verified leaf results.';
  document.querySelector('#policy').textContent = '';
  document.querySelector('#source-meaning').textContent = 'Not verified.';
  status.textContent = 'Checking current inputs…';
  try {
    const response = await fetch('/api/status', { cache: 'no-store' });
    if (!response.ok) throw new Error('Verification status unavailable');
    const value = await verifiedStatus(await response.json());
    if (generation !== refreshGeneration) return;
    const held = value.current_boundary !== 'passed';
    status.classList.toggle('error', held);
    status.textContent = held ? `Held: ${value.error || 'Current inputs failed verification'}. ${value.P9_G1_accepted ? 'Recorded P9-G1 acceptance remains intact.' : 'P9-G1 acceptance is not verified.'}` : value.P9_G1_accepted ? `G2 accepted for ${value.accepted_generic_runtime_support.length} exact declarations. Proposed profiles are not accepted; G3 remains separate.` : 'Current planning checks passed. Runtime remains unauthorized.';
    document.querySelector('#authority').textContent = value.P9_G1_accepted ? (held ? 'Accepted / current work held' : `G2 accepted / ${value.accepted_generic_runtime_support.length} exact declarations`) : 'Not accepted or not verified / not authorized';
    renderG2Profiles(value, document.querySelector('#g2-profiles'), name => document.createElement(name));
    renderReconciliation(value, document.querySelector('#reconciliation-views'));
    document.querySelector('#next-work').textContent = value.runtime_authorized ? `Accepted foundation: ${value.foundation_acceptance.accepted_iterations.join(', ')}. Accepted requests: ${value.request_acceptance.accepted_iterations.join(', ')}. Accepted results: ${value.result_acceptance.accepted_iterations.join(', ')}. Accepted harness: ${value.harness_acceptance.accepted_iterations.join(', ')}. Accepted integration: ${value.integration_acceptance.accepted_iterations.join(', ')}. Accepted geometry: ${value.geometry_acceptance.accepted_iterations.join(', ')}. Accepted stages: ${value.stage_acceptance.accepted_iterations.join(', ')}. Accepted resources: ${value.resource_acceptance.accepted_iterations.join(', ')}. Accepted numerical pressure: ${value.numerical_pressure_acceptance.accepted_iterations.join(', ')}. Accepted prestate preservation: ${value.preservation_acceptance.accepted_iterations.join(', ')}. Accepted C reference transport: ${value.reference_transport_acceptance.accepted_iterations.join(', ')}. Accepted C stage current: ${value.c_current_acceptance.accepted_iterations.join(', ')}. Accepted C control derivative: ${value.c_controls_acceptance.accepted_iterations.join(', ')}. Accepted C OS pass: ${value.os_pass_acceptance.accepted_iterations.join(', ')}. Accepted C OS operations: ${value.os_operations_acceptance.accepted_iterations.join(', ')}. Authorized lifecycle batch: P9-4.7a then P9-4.7b. Accepted after audit corrections: P9-4.6, P9-4.7a and P9-4.7b. Exact mapped vector verified under the successor release. ${value.next_gate} Execution-permitted leaves: ${value.dependency_ready_leaves.join(', ')}. ${value.permitted_runtime_paths.length} runtime paths are currently eligible under their owners. Later leaves remain gated.` : held ? 'Current work held; resolve the reported current-boundary failure.' : 'P9-G1 review remains pending.';
    document.querySelector('#boundary').textContent = held ? 'Failed · current work held' : 'Passed · current bytes';
    document.querySelector('#recorded').textContent = value.recorded_full_verification === 'not_current' ? 'Not current · rerun CLI' : 'Recorded pass · matching inputs';
    document.querySelector('#handoff').textContent = ({verified:'Verified · normalized archive and historical inputs', unavailable:'Unavailable · no archive integrity pass', invalid:'Invalid · archive integrity check failed'})[value.handoff_evidence?.status] || 'Not applicable to this historical phase';
    document.querySelector('#policy').textContent = value.policy_digest ? `Policy digest: ${value.policy_digest}` : '';
    document.querySelector('#ceiling').textContent = value.claim_ceiling;
    if (value.source_meaning) document.querySelector('#source-meaning').textContent = `${value.source_meaning.specification_authority} specification; ${value.source_meaning.association_count}/${value.source_meaning.association_denominator} source contract associations remain ${value.source_meaning.forensic_support_disposition}. These are source associations, not runtime tests. ${value.source_meaning.pending_source_obligations} source obligations remain pending.`;
    const sources = document.querySelector('#sources');
    for (const ref of value.source_refs) {
      const dt = document.createElement('dt'); dt.textContent = ref.path;
      const dd = document.createElement('dd'); dd.textContent = ref.sha256;
      sources.append(dt, dd);
    }
    const iterations = document.querySelector('#iterations'); iterations.replaceChildren();
    for (const row of value.iterations) {
      const p = document.createElement('p'); p.textContent = `${row.iteration_id}: ${row.status} — ${row.reviewer_decision}`; iterations.append(p);
    }
    button.disabled = false;
    button.onclick = () => {
      const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
      const a = document.createElement('a'); a.href = url; a.download = 'phase9-verification-status.json'; a.click(); URL.revokeObjectURL(url);
    };
  } catch (error) {
    if (generation !== refreshGeneration) return;
    status.classList.add('error'); status.textContent = `Held: ${error.message}`;
  }
}

export async function verifiedProbe(value, requested) {
  if (value?.schema !== 'phase9_pressure_projection_v1' || value.output_class !== 'isolated_probe_not_current_tree_admission' || value.case_id !== requested) throw new Error('Wrong probe schema or exact subject');
  if (!['admitted','rejected','held','unverifiable'].includes(value.candidate_decision) || !['passed','failed'].includes(value.assertion_result)) throw new Error('Unknown probe outcome');
  if (value.project_effect?.runtime_authorized !== false || value.project_effect?.P9_G1_accepted !== false || value.project_effect?.scientific_promotion !== false) throw new Error('Probe cannot grant authority');
  const {projection_digest, ...body} = value;
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical(body)));
  const actual = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2,'0')).join('');
  if (actual !== projection_digest) throw new Error('Probe digest mismatch');
  return value;
}
let probeGeneration = 0;
async function loadProbe() {
  const generation = ++probeGeneration;
  const id = document.querySelector('#probe').value;
  const button = document.querySelector('#probe-download'); button.disabled = true;
  document.querySelector('#probe-candidate').textContent = 'Not loaded';
  document.querySelector('#probe-assertion').textContent = 'Not loaded';
  document.querySelector('#probe-subject').textContent = '';
  document.querySelector('#probe-status').textContent = 'Loading recorded evidence…';
  try {
    const response = await fetch(`/api/probe?case_id=${encodeURIComponent(id)}`, {cache:'no-store'});
    if (!response.ok) throw new Error('Probe evidence unavailable or stale');
    const value = await verifiedProbe(await response.json(), id);
    if (generation !== probeGeneration || document.querySelector('#probe').value !== id) return;
    document.querySelector('#probe-status').textContent = 'Recorded isolated probe · no live permission created';
    document.querySelector('#probe-candidate').textContent = value.candidate_decision;
    document.querySelector('#probe-assertion').textContent = value.assertion_result;
    document.querySelector('#probe-subject').textContent = `${value.case_id} · ${value.run_id} · ${value.subject_scope} · ${value.projection_digest}`;
    button.disabled = false;
    button.onclick = () => {
      const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));
      const a=document.createElement('a'); a.href=url; a.download='phase9-probe.json'; a.click(); URL.revokeObjectURL(url);
    };
  } catch(error) {
    if (generation !== probeGeneration) return;
    document.querySelector('#probe-status').textContent = `Held: ${error.message}`;
  }
}
if (typeof document !== 'undefined') {
  document.querySelector('#refresh').addEventListener('click', refresh);
  refresh();
  document.querySelector('#probe-refresh').addEventListener('click', loadProbe);
  document.querySelector('#probe').addEventListener('change', loadProbe);
}
