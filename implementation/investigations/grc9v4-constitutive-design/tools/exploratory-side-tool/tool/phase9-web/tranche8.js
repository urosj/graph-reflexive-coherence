import {TRANCHE8_EVIDENCE} from './tranche8-evidence.js';

const canonical = value => JSON.stringify(value, (_, v) => v && typeof v === 'object' && !Array.isArray(v)
  ? Object.fromEntries(Object.keys(v).sort().map(k => [k, v[k]])) : v);

export function checkedTranche8(value) {
  if (canonical(value) !== canonical(TRANCHE8_EVIDENCE))
    throw new Error('Missing, stale or widened Tranche 8 evidence; no fallback');
  return value;
}

export function sourceURL(ref) {
  if (!TRANCHE8_EVIDENCE.source_refs.some(r => r.path === ref.path && r.sha256 === ref.sha256 && r.revision === ref.revision))
    throw new Error('Unindexed source');
  return '/api/tranche8/source?path=' + encodeURIComponent(ref.path);
}

export function renderTranche8(value, container, create = tag => document.createElement(tag)) {
  checkedTranche8(value);
  container.replaceChildren();
  const append = (parent, tag, text) => { const e = create(tag); e.textContent = text; parent.append(e); return e; };
  const link = (parent, ref, label) => { const e = append(parent, 'a', label); e.href = sourceURL(ref); e.target = '_blank'; e.rel = 'noopener'; return e; };
  const details = (parent, label, data) => { const e = append(parent, 'details', ''); append(e, 'summary', label); append(e, 'pre', JSON.stringify(data, null, 2)); };
  const c = value.coverage;
  append(container, 'p', `8.4b: ${c.accepted_cells}/${c.required_cells} accepted history cells; ${c.pending_cells} pending. P9-8.4 remains open. No new support or execution permission.`);
  if (c.executed_pending_cells) append(container, 'p', `${c.executed_pending_cells} additional cells have passing execution evidence pending review and acceptance; they are not accepted coverage.`);
  append(container, 'p', `Check level: ${value.verification.level}. No native trajectory rerun or interval-equation recomputation. Historical 8.3 runs do not certify later code.`);
  append(container, 'h3', 'Shared mechanics and bounded profile integrations');
  for (const row of value.mechanics) {
    const p = append(container, 'p', `${row.work_id}: ${row.scope}. `); link(p, row.acceptance, 'Recorded decision');
  }
  const table = append(container, 'table', '');
  const head = append(table, 'tr', '');
  for (const name of ['Family', '8.3 scope', '8.4b accepted / required', 'Pending', 'Retained sources']) append(head, 'th', name);
  for (const row of c.families) {
    const profile = value.profiles.find(r => r.family === row.family);
    const tr = append(table, 'tr', '');
    append(tr, 'td', row.family); append(tr, 'td', 'Accepted bounded integration');
    append(tr, 'td', `${row.accepted_cells} / ${row.required_cells}`);
    append(tr, 'td', String(row.pending_cells) + (row.executed_pending_cells ? ` (${row.executed_pending_cells} executed; unaccepted)` : ''));
    const td = append(tr, 'td', ''); link(td, profile.review, 'Review');
    if (profile.independent_A_oracle) { append(td, 'span', ' · '); link(td, profile.independent_A_oracle.review, 'A oracle'); }
    details(td, 'Exact subject, domain, schedule, budget and retained claim traces', profile);
  }
  append(container, 'h3', 'Recorded cases: event commit is not case success');
  append(container, 'p', 'C_OS uses bounded dense comparisons; A_OS, C_CI, A_CI, C_PC, A_PC, C_CI_PC, A_CI_PC, C_RG2b and A_RG2b also have pointwise interval checks. Both RG2b families retain signed inverse chains and completion-relative section bounds. A_RG2b also checks scaled-log-W state, history lineage and the composed writer’s next read. None is a uniform parameter tube.');
  const supplements = append(container, 'p', 'Expanded A_OS oracle and pressure: ');
  for (const ref of c.oracle_and_pressure) { link(supplements, ref, ref.path.split('/').at(-1)); append(supplements, 'span', ' · '); }
  for (const run of c.runs) {
    const section = append(container, 'details', '');
    append(section, 'summary', `${run.family}: ${run.passed_cases} passed, ${run.incomplete_cases} incomplete — ${run.results.path.split('/').at(-1)}`);
    const p = append(section, 'p', `${run.status}. `); link(p, run.results, 'Exact execution'); append(p, 'span', ' · ');
    link(p, run.inputs, 'Inputs and budgets'); append(p, 'span', ' · ');
    if (run.acceptance) link(p, run.acceptance, 'Separate scoped acceptance');
    else { link(p, run.review, 'Review pending acceptance'); append(p, 'span', ' · No accepted coverage credited.'); }
    if (run.signed_stage_pressure) { append(p, 'span', ' · '); link(p, run.signed_stage_pressure, 'Signed Read-Back/flat checks'); }
    if (run.pc_claim_restrictions) { link(p, run.claim_source, ' PC claim source'); details(section, 'PC claim restrictions', run.pc_claim_restrictions); }
    if (run.rg_claim_restrictions) { link(p, run.claim_source, ' RG claim source'); details(section, 'RG completion and C1 claim restrictions', run.rg_claim_restrictions); }
    if (run.stage_evidence) details(section, run.stage_evidence_label || 'Signed reads, W/Z effects and declared chart', run.stage_evidence);
    if (run.numerical_recheck) { append(p, 'span', ' · '); link(p, run.numerical_recheck, 'Independent interval recomputation'); }
    if (run.original_attempt) {
      const original=append(section,'p','Original attempt retained: ');
      link(original,run.original_attempt.results,'Original execution and timeout');
      details(section,'Retained versus new execution',run.execution_partition);
      details(section,'Original incomplete cases — not passing evidence',run.original_attempt.failures);
    }
    for (const row of run.cases) append(section, 'p', `${row.case_id}: ${row.case_passed ? 'CASE PASSED' : 'INCOMPLETE CASE'}; event committed=${row.event_committed}; first failure=${JSON.stringify(row.first_failure)}`);
  }
  const boundary = c.boundary_contract;
  const closeout = boundary.closeout;
  append(container, 'h3', '8.4c closed — accepted bounded capacity/phase coverage');
  append(container, 'p', `${closeout.accepted_cells}/${closeout.required_cells} accepted history cells across all ten families; ${closeout.new_history_cells} new and ${closeout.exact_reused_history_cells} exact reuses. 8.4d–i and 8.5/8.6 remain open.`);
  const closeoutLinks = append(container, 'p', '');
  link(closeoutLinks, closeout.record, 'Exact aggregate reconciliation');
  append(closeoutLinks, 'span', ' · '); link(closeoutLinks, closeout.review, 'Closeout scope');
  append(container, 'h3', '8.4c boundary preregistration — no runtime credit');
  append(container, 'p', `${boundary.counts.layouts} layouts across ${boundary.counts.families} families; ${boundary.counts.history_cells} current/reset obligations: ${boundary.counts.new_history_cells} new, ${boundary.counts.reuse_candidates} exact-reuse candidates. ${boundary.counts.executed_cells} executed; ${boundary.counts.accepted_cells} accepted at preregistration. These original planning counts are unchanged; completed family evidence and aggregate acceptance are reported separately.`);
  const boundaryLinks = append(container, 'p', '');
  link(boundaryLinks, boundary.record, 'Full matrix, recipes and authority traces');
  append(boundaryLinks, 'span', ' · '); link(boundaryLinks, boundary.review, 'Boundary review');
  details(container, 'Independent capacity/phase expectations', boundary.layouts);
  details(container, 'All-ten required comparison ceilings — not new target certificates', boundary.families);
  details(container, 'Bounded schedule, retention budget and prerequisites', {schedule:boundary.schedule, retention:boundary.retention, prerequisites:boundary.prerequisites});
  const mechanical = boundary.mechanics;
  append(container, 'h3', '8.4c shared mechanics — accepted mechanical scope only');
  append(container, 'p', `${mechanical.observations.shared_layouts} layouts checked once; ${mechanical.observations.exact_real_resource_maps} exact-real resource maps. All ten receiver routes checked with mocked numerical reads, detection and target construction. No numerical admission or continuation credit; integrity check does not rerun tests.`);
  const mechanicalLinks = append(container, 'p', '');
  link(mechanicalLinks, mechanical.record, 'Completed mechanical checks');
  append(mechanicalLinks, 'span', ' · '); link(mechanicalLinks, mechanical.review, 'Mechanical review and reproduction');
  details(container, 'Shared negatives, outliers and explicitly mocked receiver probes', mechanical.observations);
  for (const run of boundary.family_results) {
    append(container, 'h3', `8.4c ${run.family} — ${run.status}`);
    append(container, 'p', `${run.native_cases} new native cases (${run.passed_cases} passed); ${run.exact_reuse_cases} exact accepted-case reuses. ${run.accepted_cells}/${run.required_cells} accepted history cells; ${run.passing_pending_cells} passing cells pending acceptance. Status is retained integrity only: no dense, interval or native rerun. Comparison scope: ${run.comparison_scope}.`);
    const links = append(container, 'p', '');
    for (const [key, label] of [['inputs','Bound subjects'],['results','Completed operands'],['review','Scope and reproduction'],['acceptance','Scoped acceptance'],['reuse_evidence','Exact historical reuse']]) {
      if (run[key]) { link(links, run[key], label); append(links, 'span', ' · '); }
    }
    for (const row of run.cases) append(container, 'p', `${row.case_id}: ${row.case_passed ? 'CASE PASSED' : 'INCOMPLETE CASE'}; event committed=${row.event_committed}; first failure=${JSON.stringify(row.first_failure)}`);
  }
  for (const oracle of boundary.oracle_preparations) {
    append(container, 'h3', `8.4c ${oracle.family} oracle — ${oracle.status}`);
    const reusedNative = oracle.exact_accepted_target_reuses || 0;
    const summary = reusedNative ? `${oracle.oracle_cases_passed}/${oracle.oracle_cases_required} target expectations available (${oracle.new_oracle_cases} new independent oracle cases; ${reusedNative} exact accepted native target reuses, not new oracle executions)` : `${oracle.oracle_cases_passed}/${oracle.oracle_cases_required} independent oracle expectations pass (${oracle.new_oracle_cases} new, ${oracle.exact_reuse_cases} exact reuses)`;
    append(container, 'p', `${summary}; ${oracle.native_steps} native steps and ${oracle.runtime_cells_closed} runtime cells closed by this oracle. Saved-entry full-formula bounds, not a uniform trajectory bound. Oracle scope ${oracle.oracle_scope_accepted ? 'accepted' : 'pending review'}; native runtime acceptance remains separate and original execution flags are unchanged.`);
    const links=append(container, 'p', '');
    for (const [key,label] of [['inputs','Bound oracle subjects'],['results','Oracle expectations and certificates'],['review','Scope, pressure and reproduction'],['acceptance','Oracle-scope acceptance']]) {
      if (oracle[key]) { link(links,oracle[key],label); append(links,'span',' · '); }
    }
  }
  for (const prepared of boundary.target_preparations) {
    append(container, 'h3', `8.4c ${prepared.family} target preparation — ${prepared.status}`);
    append(container, 'p', `${prepared.passed_cases} new target preparations pass; ${prepared.exact_reuse_cases} exact reused targets. ${prepared.new_native_root_reads} new read-only native joint-root proposals, checked by independent interval equations. ${prepared.topology_events} topology events, ${prepared.native_steps} native steps and ${prepared.runtime_cells_closed} runtime cells closed. Nominal continuation predictions are not a native campaign or a uniform trajectory bound. Status does not rerun roots or interval equations.`);
    const links=append(container, 'p', '');
    for (const [key,label] of [['inputs','Bound C_CI targets'],['results','Joint roots and nominal predictions'],['review','Preparation scope and reproduction']]) {
      link(links,prepared[key],label); append(links,'span',' · ');
    }
  }
  const deep = c.deep_expansion;
  append(container, 'h3', '8.4d deeper expansion — partial family evidence');
  append(container, 'p', `First-group checkpoint: ${deep.first_group_closed ? 'accepted' : 'open'}, ${deep.first_group_accepted_cells} accepted history cells. All-ten closure remains open; six families follow first-group .e–h.`);
  for (const run of deep.family_results) {
    append(container, 'p', `${run.family}: ${run.passed_cases} single-event cases; ${run.accepted_cells}/${run.required_cells} accepted history cells, ${run.passing_pending_cells} passing pending acceptance. Degrees ${run.degrees.join(', ')}, maximum core depth ${run.maximum_core_depth}, ${run.target_steps} continuation steps. No successive-event or arbitrary-depth claim.`);
    const links=append(container, 'p', '');
    for (const [key,label] of [['inputs','Declared deep subjects'],['results','Completed operands'],['review','Scope and excluded share recipes']]) {
      link(links,run[key],label); append(links,'span',' · ');
    }
    details(container,'Named deep cases and numerical comparison limits',run);
    if (run.preflight_pressure) {
      const pressure=run.preflight_pressure;
      const original=run.frozen_source_preflight || run;
      append(container,'p',`${run.family} frozen-source PREFLIGHT HOLD: ${original.attempted_cases} case attempted, ${original.unattempted_cases} not attempted; ${original.native_cases} native events and ${original.target_steps} native continuation steps. ${pressure.certified_exclusions} independent resource exclusions do not establish general infeasibility.`);
      const refs=append(container,'p','');link(refs,pressure.evidence,'Enabled interval exclusion evidence');
    }
    if (run.allocation_feasibility) {
      const f=run.allocation_feasibility;
      append(container,'p',`${run.family} allocation exclusion: ${f.D94_cases} declared D94 layouts, entire closed simplex, at most ${f.max_updates} updates. Frozen source only; represented result is conditional on existing error budgets. Zero native or accepted-cell credit; not general A_PC impossibility.`);
      const refs=append(container,'p','');link(refs,f.evidence,'Allocation certificate');link(refs,f.review,' Proof and scope');
      if(f.acceptance)link(refs,f.acceptance,' Bounded exclusion acceptance');
    }
    if(run.source_companion) {
      const c=run.source_companion;
      append(container,'p',`${run.family} source companion: independent ten-step target pilot passes both histories, but the fresh source trigger rejects. ${c.native.source_steps} native source step; ${c.native.native_event_attempts} event attempt, ${c.native.committed_events} commits, ${c.native.target_steps} native target steps. Full lifecycle unchanged. No successful operational domain, accepted cells or uniform neighborhood follows.`);
      const refs=append(container,'p','');link(refs,c.plan,'Source preregistration');link(refs,c.results,' Independent target evidence');link(refs,c.native_results,' Native rejection and rollback');link(refs,c.review,' Claim and debt implications');
    }
    if(run.history_companion) {
      const h=run.history_companion;
      append(container,'p',`${run.family} history companion: fresh source eligible; current-role target preflight fails at step ${h.pressure.first_negative_step}. ${h.source_steps} native source step, ${h.native_cases} event attempts, ${h.target_steps} native target steps. Signed resource interval stays negative after the existing error allowance. Gated neighbors not run; no completed cells or general impossibility claim.`);
      const refs=append(container,'p','');link(refs,h.plan,'History preregistration');link(refs,h.results,' Source and held pilot');link(refs,h.diagnostic,' Signed target exclusion');link(refs,h.review,' Scope and next question');
    }
    if(run.full_campaign) {
      const f=run.full_campaign;
      append(container,'p',`${run.family} full coupled campaign: ${f.passed_cases}/${f.cases_required} cases, ${f.target_steps} native continuation steps, ${f.final_reads} final reads; ${f.passing_pending_cells}/${f.required_cells} passing-pending cells, ${f.accepted_cells} accepted. ${f.newly_executed_cases} newly executed cases and ${f.reused_cases} exact pilot reuse (${f.reused_target_steps} steps); no new source beat. Acceptance is separately recorded; no uniform domain inferred.`);
      const refs=append(container,'p','');link(refs,f.plan,'Full campaign plan');link(refs,f.results,' Full results');link(refs,f.review,' Review and limits');
    }
    if(run.joint_successor) {
      const j=run.joint_successor,p=run.joint_witness;
      append(container,'p',`${run.family} coupled successor: ${j.passed_cases} D94 case, ${j.target_steps} native target steps, ${j.final_reads} final reads; ${j.passing_pending_cells}/40 passing-pending cells, ${j.accepted_cells} accepted. Initial W ${j.initial_history_mean}; shares ${j.shares.join(', ')}. Earlier allocation witness: ${p.committed_events} event, ${p.target_steps} step, zero completed cases (fine source-staging effect separation). No uniform neighborhood or family closure.`);
      const refs=append(container,'p','');link(refs,j.plan,'Successor plan');link(refs,j.results,' Passing witness');link(refs,j.review,' Scope and limitations');link(refs,p.results,' Earlier partial run');
    }
    if (run.hardening) {
      const h=run.hardening;
      const detail = h.finite_probes !== undefined
        ? `${h.finite_probes} finite target probes, ${h.histories} histories, ${h.native_steps} native steps with pointwise joint-root/resource bounds`
        : `${h.pointwise_sign_certificates} pointwise sign enclosures; ${h.neighborhood_positive_roles}/18 positive finite-probe histories`;
      append(container,'p',`Bounded ${run.family} hardening: ${detail}. Native excluded cases and event rollback checked. No uniform tube or public ordinary-step owner claim.`);
      if (h.rounded_transfer_controls !== undefined) {
        append(container,'p',`${h.exact_charge_preserving_probes} probes preserve both-role exact coordinate charge; ${h.rounded_transfer_controls} are rounded-transfer controls, not exact-conserving event evidence.`);
      }
      const refs=append(container,'p','');
      for (const key of ['inputs','results','review']) { link(refs,h[key],`Hardening ${key}`); append(refs,'span',' · '); }
    }
  }
  for (const oracle of deep.oracle_preparations ?? []) {
    append(container,'p',`${oracle.family} independent deep oracle: ${oracle.passed_cases}/${oracle.cases_required} cases, ${oracle.independent_observations} joint-root observations; ${oracle.oracle_scope_accepted ? 'oracle scope accepted' : 'pending review'}. Zero native steps, events or accepted runtime cells from this oracle. Pointwise bounds, not a uniform trajectory tube.`);
    const refs=append(container,'p','');
    for (const key of ['inputs','results','review']) { link(refs,oracle[key],`Oracle ${key}`); append(refs,'span',' · '); }
  }
  append(container,'p',`Unexecuted 8.4d families: ${deep.families_not_executed.join(', ')}. No sibling credit; first group remains C_OS, C_CI, A_CI, A_PC.`);
  append(container,'h3','8.4f full chart rotation and reflection');
  append(container,'p',`First-group 8.4f checkpoint: ${c.chart_covariance.first_group_closed ? 'accepted' : 'open'}, ${c.chart_covariance.first_group_accepted_cells}/96 accepted cells. All-ten closure remains open.`);
  for(const row of c.chart_covariance.family_results) {
    append(container,'p',`${row.family}: ${row.passing_pending_cells}/${row.required_cells} chart covariance history cells passing pending acceptance, ${row.accepted_cells} accepted; ${row.native_events} numerical events, ${row.target_steps} target steps, ${row.final_reads} final reads. ${row.frozen_plan_executions} exact frozen mechanical-plan executions are separate, not numerical events. Maximum discrepancy ${row.maximum_covariance_error}.`);
    if(row.reused_frozen_plan_executions) append(container,'p',`${row.reused_frozen_plan_executions} frozen mechanical plans are reused from accepted evidence, not new ${row.family} executions.`);
    if(row.unsigned_candidate_history) append(container,'p',`Unsigned W_A and effective conductance, fixed-row differential reconstruction, both-role history transfer and writer covariance are checked; ${row.persistent_carrier ? 'whole-carrier archive, explicit loss, zero target initialization and fresh ZOH continuation are checked separately.' : 'no carrier credit.'}`);
    append(container,'p',row.full_joint_roots ? 'Complete joint-root covariance with pointwise independent interval certificates; no uniform parameter tube or whole-trajectory enclosure.' : row.persistent_carrier ? 'Complete PC read and W/Z writer checks with pointwise independent interval certificates; no uniform covariance or whole-trajectory enclosure.' : 'Bounded dense comparisons, not a rigorous full-error certificate.');
    append(container,'p',`Full rows/columns/branches, endpoint ports, external labels, namespace/roles, chirality, active phase and branch shares are transported together. Reflection is not edge reversal. ${row.persistent_carrier ? 'Both declared layouts have active phase; no inactive-phase numerical credit.' : 'Inactive phase remains None.'} No sibling credit.`);
    const refs=append(container,'p','');
    for(const key of ['inputs','results','plan','review']) {link(refs,row[key],key);append(refs,'span',' · ');}
  }
  append(container,'p',`Unexecuted 8.4f families: ${c.chart_covariance.families_not_executed.join(', ')}. Aggregate remains open.`);
  append(container, 'h3', '8.4e ordering and signed covariance');
  for (const row of c.ordering_covariance.family_results) {
    append(container, 'p', `${row.family}: ${row.passing_pending_cells}/${row.required_cells} covariance history cells passing pending acceptance, ${row.accepted_cells} accepted; ${row.native_events} events, ${row.target_steps} target steps and ${row.final_reads} final reads. Maximum covariance discrepancy ${row.maximum_covariance_error}. Two layouts, five transforms; no chart-symmetry or uniform-domain claim.`);
    if(row.full_joint_roots) append(container,'p','Full joint CI roots: current, H, generated geometry, structural source and Read-Back; selected, reset, restart and final roots. Individual interval certificates are not a whole-trajectory enclosure.');
    if(row.unsigned_candidate_history) append(container,'p','Unsigned Candidate-A history: W_A, conductance, writer targets and committed history permute without sign flips; currents and reference lineage remain signed.');
    if(row.persistent_carrier) append(container,'p','Persistent carrier: two-sided signed Z transport; complete current/reset source archive and explicit carrier-history loss at expansion, zero target initialization, then one held-source write per step. D59/D94 use the accepted coupled history/allocation witness; original-source exclusions remain.');
    const refs=append(container,'p','');
    for(const key of ['inputs','results','plan','review']) { link(refs,row[key],key); append(refs,'span',' · '); }
  }
  append(container,'p',`Unexecuted 8.4e families: ${c.ordering_covariance.families_not_executed.join(', ')}. Aggregate remains open.`);
  append(container, 'h3', 'Larger configurations: preparation is not runtime acceptance');
  for(const row of c.larger_prerequisites.family_results) {
    append(container,'h3',`8.4g ${row.family} — historical bounds and native prerequisites`);
    append(container,'p',`${row.cases} original independent equation points; ${row.exact_oracle_geometry_bounds} exact FLINT geometry bounds on represented oracle operands. The original preflight alone supplies no full error enclosure.`);
    const bounds=row.pointwise_bounds;
    append(container,'p',`Historical pointwise successor: ${bounds.exact_real_positive}/4 exact-real and ${bounds.staged_positive}/4 staged resource sign checks pass. Bounded research checkpoint accepted; its original execution flags remain unchanged.`);
    const native=row.native_prerequisites;
    if(native) {
      append(container,'p',`Native C_OS prerequisites: ${native.numerical_steps}/4 complete numerical steps through charge and final-C admission. Explicit certified FLINT/Arb policy integrated. ${native.committed_steps} committed lifecycle steps; ${native.native_events} events. ${native.status}. Scientific prerequisites ready: ${native.scientifically_ready_for_8_4h}; authorized 8.4h readiness: ${native.ready_for_8_4h}. No trajectory tube or other-family credit.`);
      details(container,'Native case evidence and exact resource-sum drift',native.cases);
      const nativeRefs=append(container,'p','Native successor: ');
      for(const key of ['inputs','results','plan','review']) {link(nativeRefs,native[key],key);append(nativeRefs,'span',' · ');}
    }
    details(container,'Resource lower bounds and dense-proposal sign separation',bounds.points);
    const boundRefs=append(container,'p','Bounds successor: ');
    for(const key of ['inputs','results','plan','review']) {link(boundRefs,bounds[key],key);append(boundRefs,'span',' · ');}
    details(container,'Remaining prerequisite obligations',row.open_obligations);
    const refs=append(container,'p','');
    for(const key of ['inputs','results','plan','review']) {link(refs,row[key],key);append(refs,'span',' · ');}
  }
  for(const research of c.larger_prerequisites.investigations || []) {
    append(container,'h3',`8.4g ${research.family} — research and separately bound native prerequisites`);
    append(container,'p',`Historical research: ${research.cases.length} whole-ball existence/uniqueness certificates. Native roots: ${research.native_roots}; steps: ${research.native_steps}; events: ${research.native_events}. 8.4h readiness: ${research.ready_for_8_4h}. Scalar certificates recomputed; no native trajectory rerun.`);
    append(container,'p','Reference-geometry pairs already satisfy the exact-real residual tolerance. This does not establish feedback discrimination or a represented joint root.');
    details(container,'Exact-real bounds and remaining obligations',{cases:research.cases,open:research.open_obligations});
    if(research.family==='A_CI') {
      append(container,'p','A_CI initial investigation, not accepted/native closure: the original target current has positive exact-real first-step resources; target reset-as-current has a certified negative resource. A unique joint root is not a successful continuation. The separately bound companion below supplies bounded feasibility, not staged/native closure.');
      append(container,'p','Displayed A_CI bounds are approximate; exact rational endpoints are in the linked evidence. No history substitution or tolerance relaxation is authorized.');
    }
    if(research.staged_bridge) {
      const bridge=research.staged_bridge;
      append(container,'p','Historical represented joint-root bridge: includes analytic current defect, geometry residual and contraction tail. Counterfactual feedback reads are not extra native iterations. This original record does not verify native stopping; see the separate successor below.');
      details(container,'Staged feedback discrimination (approximate display; exact bounds linked)',bridge.cases);
      details(container,'Historical staged-bridge obligations (see native successor below)',bridge.open_obligations);
      append(container,'p',`${bridge.continuation.excluded_target_roles} original target roles have certified negative exact-root first-step resources. At a zero-resource vertex this excludes every positive timestep at that state; no native rejection receipt is claimed.`);
      details(container,'Exact-root continuation exclusion (approximate display)',bridge.continuation.cases);
      link(container,bridge.continuation.results,'Exact continuity bound evidence');
      const links=append(container,'p','Staged successor: ');
      for(const key of ['results','plan','review']) {link(links,bridge[key],key);append(links,'span',' · ');}
    }
    if(research.feasibility) {
      const f=research.feasibility;
      append(container,'p',`${research.family} lawful feasibility companion: shares ${f.shares.join(', ')}, source deficit ${f.source_deficit} at node 0 compensated at node ${f.source_compensation_node}. This research record provides exact-real first-step bounds only; ${research.native_prerequisites ? 'separate native evidence follows' : research.staged_oracle ? 'separate staged research follows; native admission remains open' : 'staged/native admission remains open'}.`);
      append(container,'p',f.allocation_only_diagnostic_kind==='uncertified_exact_strict_margin'
        ? 'Allocation-only source intervals do not certify a strict trigger; the rounded-exact control also lacks a margin. This is not an exact-zero theorem or native receipt. The successor keeps both W histories unchanged, bounds the postbeat log writer and transfers live current while stored reset does not evolve.'
        : 'Allocation alone leaves the original staged source trigger at zero. The new source fixture has interior row margins; its full-ulp control is not native staged arithmetic. Current uses postbeat transfer; stored reset does not evolve.');
      details(container,'Companion bounds (approximate display; no numerical rerun)',f.cases);
      details(container,'Actual event role pairing, not an event receipt',f.event_pair);
      const links=append(container,'p','Feasibility successor: ');
      for(const key of ['results','plan','review']) {link(links,f[key],key);append(links,'span',' · ');}
    }
    if(research.staged_oracle) {
      const s=research.staged_oracle;
      append(container,'p',`${research.family} independent staged joint-root oracle: ${s.cases.length} prepared cases, two analytic residual passes each; ${s.native_roots} native roots. Fixed ${s.precision_bits}-bit rigorous Arb lowering with certified binary64 rounding, no fallback. Native stopping and whole-step admission are not verified.`);
      details(container,'Full joint-point identities, residuals, feedback separation and resources (approximate display)',s.cases);
      append(container,'p','Some feedback coordinates separate from their bounded numerical error in every case, not all coordinates. Source diagonal changes round away; off-diagonals survive. These are prebeat target controls, not a postbeat event receipt. Status does not rerun interval solves.');
      details(container,'Remaining native obligations',s.open_obligations);
      for(const key of ['results','plan','review']) {link(container,s[key],`Staged ${key}`);append(container,'span',' · ');}
    }
    if(research.native_attempt) {
      const n=research.native_attempt;
      append(container,'p',`${research.family} historical native prerequisite HOLD: one large source-current attempt timed out at 600 seconds; three large cases were not run in that attempt. ${n.native_steps} verified completed large steps, ${n.native_roots} verified completed large roots—not a claim that no internal work occurred. No numerical rejection or scientific infeasibility is inferred.`);
      append(container,'p','The original expected-failure test is not a conformance PASS: it exposed nonlinear endpoint collapse, alongside an exact analytic Hodge inverse bypass. These findings and the timeout remain historical; the separately bound corrected successor below reports current-runtime execution.');
      details(container,'Native attempt outcomes and open findings',{cases:n.cases,holds:n.known_implementation_holds});
      for(const key of ['results','plan','review','attempt']) {link(container,n[key],`Native investigation ${key}`);append(container,'span',' · ');}
    }
    if(research.native_successor) {
      const n=research.native_successor;
      append(container,'p',`${research.family} corrected native successor: ${n.native_steps} prepared numerical steps and ${n.native_roots} full joint roots, two evaluations each. Both residual corrections are implemented and the original enclosure regression passes. Acceptance: ${n.user_accepted}; 8.4h readiness: ${n.ready_for_8_4h}. No topology events or uniform-domain credit.`);
      append(container,'p','Whole selected points, final-C/W roots and writer staging match independent checks. A passing represented charge receipt is not exact conservation of the sum of stored binary64 resources; the exact drift is shown separately. Status does not rerun trajectories or the full native-evidence checker.');
      details(container,'Corrected native cases and exact stored-resource drift',n.cases);
      if(n.acceptance)link(container,n.acceptance,'Scoped A_CI prerequisite acceptance (original execution flags unchanged)');
      for(const key of ['results','plan','review']) {link(container,n[key],`Corrected successor ${key}`);append(container,'span',' · ');}
    }
    if(research.native_prerequisites) {
      const n=research.native_prerequisites;
      append(container,'p',`C_CI native prerequisite successor: ${n.native_steps} numerical steps, ${n.native_roots} full joint roots; ${n.native_events} events and ${n.committed_steps} live commits. Status: ${n.status}. 8.4h readiness: ${n.ready_for_8_4h}. Retained checks do not rerun trajectories.`);
      details(container,'Native C_CI cases, residuals and exact stored-resource drift',n.cases);
      append(container,'p','The old negative target and sub-rounding feedback limitations remain. These four fixed companion cases are not a uniform domain or a lifecycle campaign.');
      if(n.native_runtime_source_revision) append(container,'p',`Accepted C_CI execution remains bound to runtime ${n.native_runtime_source_revision}; it was not reexecuted under the later A_CI residual correction.`);
      for(const key of ['results','plan','review']) {link(container,n[key],`Native ${key}`);append(container,'span',' · ');}
    }
    const refs=append(container,'p','');
    for(const key of ['results','plan','review']) {link(refs,research[key],key);append(refs,'span',' · ');}
  }
  append(container, 'p', `Retained probe outcomes: ${JSON.stringify(value.configuration.outcome_counts)}. Forty disabled-profile cells remain Tranche 9 work.`);
  for (const row of value.configuration.families) {
    const p = append(container, 'p', `${row.family}: ${JSON.stringify(row.outcomes)}. Owners: ${row.next_owners.join(', ')}. `);
    link(p, row.configuration, 'Configuration'); append(p, 'span', ' · '); link(p, row.numerical_report, 'Probe report');
  }
  details(container, '8.4 children and remaining owners', c.children);
  details(container, 'Paper/specification/claim associations — no authority promotion', value.scientific_claim_mapping);
  details(container, 'Source identities and exact Git checkpoint', value.source_refs);
}

// Independent of the slower full phase-boundary API; never implies that it passed.
export function tranche8Loader(container, status, fetcher = fetch, create) {
  let generation = 0;
  return async () => {
    const current = ++generation;
    container.replaceChildren(); status.textContent = 'Checking retained Tranche 8 sources…';
    try {
      const response = await fetcher('/api/tranche8', {cache: 'no-store'});
      if (!response.ok) throw new Error('Retained evidence unavailable');
      const value = checkedTranche8(await response.json());
      if (current !== generation) return;
      renderTranche8(value, container, create);
      status.textContent = 'Retained sources checked. Not a numerical rerun or a current phase-boundary pass.';
    } catch (error) {
      if (current !== generation) return;
      container.replaceChildren(); status.textContent = `Unavailable: ${error.message}`;
    }
  };
}

if (typeof document !== 'undefined' && document.querySelector('#tranche8-evidence')) {
  const load = tranche8Loader(document.querySelector('#tranche8-evidence'), document.querySelector('#tranche8-status'));
  document.querySelector('#tranche8-refresh').addEventListener('click', load);
  load();
}
