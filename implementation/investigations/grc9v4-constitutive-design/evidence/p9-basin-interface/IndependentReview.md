# P9-10.1a basin interface proposal — independent review

## Disposition

**Mathematical PASS for the finite represented-flow rule; support the proposed diagnostic direction. Tighten three contract points before freezing its authority/specification.** No counterexample was found to terminal classification, disjoint assignment, or covariance under transported represented inputs. The findings below are not demonstrated production defects: this is an unimplemented proposal, and the original conditional checker was not supplied/retrieved.

The findings are: (1) the stated bundle does not guarantee retention of nonterminal-cycle evidence; (2) represented-read/observation/replay identity needs an explicit binding; and (3) the boundary between the new diagnostic labels and D4 identity/event accounting needs a precise bridge. None calls for changing the SCC membership rule, adding an epsilon, restarting P9-8.0, or requiring a stability theorem for an explicitly diagnostic interface.

## Reviewed sources and execution boundary

Primary basis: the four supplied files, `P9BasinInterfaceAuthorityProposal.md`, `D4GeometryMobilityAndTopologyOwnership(2).json`, `AuthorityAudit.json`, and `ConditionalChecks.json`.

The supplied proposal and D4 raw-byte SHA256 values exactly match AuthorityAudit.source_refs. The proposal also matches ConditionalChecks.source_refs. The two record digests reproduce under sorted compact JSON with the record_digest member removed, and ConditionalChecks correctly links the authority record digest. See `integrity.json`.

These checks do not authenticate the Git baseline, rerun the forensic queries, establish current paper/spec/runtime bytes, or rerun the six submitted conditional tests. Their checker `check_p9_basin_interface_proposal.py` was not supplied or retrieved. Its existence and hash in a report are not an implementation audit.

## 1. What the finite-graph definition establishes

Let D be the directed support of the captured represented current. Ignore both signed zeros, preserve distinct opposite parallel arcs, and reject nonfinite operands. Let T be the terminal SCCs. For each node v let R(v) be its reachable terminal-component set, including its own component when terminal. Define B_s = {v : R(v) = {{s}}} for each terminal singleton sink s.

Every nonempty component reaches a terminal: repeatedly following edges in a finite condensation DAG cannot continue forever. The terminal kinds are exhaustive and mutually exclusive. A nonsingleton or nonzero-loop singleton is recirculating; otherwise a singleton terminal has either an external incoming arc (sink) or no nonzero incident arc (quiescent).

The partial assignment is well-defined. Different B_s are disjoint. In fact each assigned region is forward-closed in D: if v belongs to B_s and v -> w, then the nonempty R(w) is a subset of R(v), hence w also belongs to B_s. Each node has a directed path to s within B_s. These are frozen-input graph properties, not temporal invariance under V4 evolution.

A quiescent terminal cannot be reached by a different vertex, because that would supply an incoming nonzero arc. Thus quiescent status cannot propagate upstream. A node can, however, lead to a recirculating terminal without itself lying on a cycle.

The explicit distinction between unique reachable terminal and eventual convergence is correct. An upstream cycle with an exit to s is assigned to B_s even though an unconstrained infinite walk can keep traversing the cycle. No probability, fairness or attraction assertion follows.

Zero current gives no assigned flow regions; all nodes are quiescent. A closed circulating current can also give no assigned regions. More generally, on a closed graph any exactly divergence-free represented current (B J = 0) has no assigned region: a singleton sink s with nonzero incoming arcs and no outgoing arcs has (B J)_s = -sum(incoming magnitudes) < 0, a contradiction. This implication holds for arbitrary positive arc magnitudes, not only the unit-current examples in the pressure script. Those are deliberate policy consequences, not failed admission or evidence that the system has no stable dynamical structures. Separate geometric seed flags do not repair or override membership.

## 2. BIF-1 — nonterminal cycle evidence is not guaranteed by the stated bundle

**Concrete output-completeness gap; the membership computation is correct.**

Proposal section 2 says an upstream current-cycle does not disappear from the evidence. Section 4 requires terminal components, reachable-terminal/status/optional-ID records and assigned regions, but does not explicitly require nonterminal SCCs or cyclic flags.

Compare:

    a -> b -> s
    a <-> b -> s

Both have only terminal {s}, of kind sink. Every node reaches only {s}; every node is assigned to the same B_s. All mandated terminal/assignment records therefore coincide despite the different upstream SCCs.

The same example can use one fixed multigraph with oriented edges (a,b), (b,a), (b,s). Currents (1,0,1) and (2,1,1) both have outward node-divergence (1,0,-1), but only the second has the upstream cyclic SCC {a,b}. A net-flux summary does not generally recover the missing cycle. This is an abstract represented-input example, not two claimed runtime-reached substrate states.

Observed state digests may distinguish observations, but an opaque digest does not expose which nonterminal component is cyclic. If the intent is that evidence must be recovered through some other current-read record, bind that record explicitly instead of promising that terminal records alone retain it.

**Minimal correction:** retain the full SCC partition (terminal and nonterminal) or equivalent explicit cycle evidence. Provide each node's own component reference and distinguish component cyclicity from reachable-terminal status. Cyclicity must include a nonzero singleton self-loop. No trajectory tracking or new dynamics is needed. A full condensation-edge listing is optional if the existing read witness supplies those arcs.

## 3. BIF-2 — bind the actual represented observation and its replay semantics

**Unclosed contract implication, not a demonstrated nondeterministic native read.**

The policy intentionally depends on represented current signs and correctly disclaims exact-real sign certification. It also reconstructs on queries/load and requires any serialized derived bundle to agree with reconstruction. State identity plus an error tolerance does not by itself prove that the same sign graph will be reconstructed.

On one edge u--v, if an exact-zero current is approximated by either +delta or -delta within an admitted absolute error, the two represented observations produce opposite sinks. A returned zero instead produces two quiescent vertices. Thus two accurate current evaluations need not produce the same classification. This is a counterexample to deriving repeatable labels from accuracy alone; it does not establish that the actual admitted runtime is nonrepeatable.

**Minimal correction:** explicitly bind each observation to one captured fresh read, the current/reset role, complete context/evaluation binding and numerical policy. All membership and flux-derived fields for that observation must consume that same read. Use an existing read/certificate identity or a derived operand digest when available; this is not a new authoritative current or hidden history.

State the applicable exact-replay guarantee, or reference the existing contract that supplies it. If the numerical policy already guarantees the required deterministic reconstruction on its supported execution scope, a precise reference and inherited conformance check are sufficient. Otherwise state how compatible replay and a new observation are distinguished; do not silently promise exact snapshot-derived-label equality from a tolerance certificate alone.

Define the observed-state digest projection explicitly so it cannot include the new bundle containing that same digest. The bundle should be derived from an already defined immutable scientific/lifecycle input binding. A state-content digest is also not a unique temporal occurrence ID: reset/replay can revisit the same content. No persistent identity is needed here; replace ambiguous "membership epoch" language with a state/observation binding unless occurrence identity is actually intended.

Keep covariance conditional on transported represented operands. Orientation reversal with exact current-sign reversal and coordinate reindexing preserves the sign graph. Re-solving after reordering at finite precision is a separate numerical obligation. Do not add an epsilon or infer exact-real sign robustness.

## 4. BIF-3 — make the D4 boundary explicit when reusing basin_identity

**Authority/consumer clarification; no contradiction with the diagnostic design has been proved.**

D4.decision.object_registry includes topology_and_basin_hierarchy as derived unless natively consumed. That supports a non-authoritative observer. But D4.decision.topology_and_basin_contract.event_boundary explicitly requires typed interspace maps and event accounting for topology/rank/selector/basin-identity changes before post-event state comparison. Its wording is broader than a rule applying only once a label directly drives dynamics.

The proposal's last paragraph of section 4 refers to an identity that becomes causally consumed later. Make clear that this does not waive D4 for a future analysis or lifecycle comparison that uses regions to index state spaces, even without direct feedback into current.

A precise successor bridge can say:

> These flow-region labels are derived diagnostic references, not transported physical basin identities. Recomputing them supplies no interspace identification. Any use of regions or their changes to define causal state, normalization, hierarchy, events, or cross-state comparisons invoking D4/D9 must satisfy the separately applicable transport and accounting contract.

The retained basin_id can stay the same while membership changes, so equality of that hash cannot authorize a comparison of basin-indexed coordinates either. Conversely, an unrelated graph edit can change every graph-scoped label without constituting a physical basin birth.

The schema successor should mark the public field's derived status unambiguously, preserve old snapshot meaning, and reject any unreviewed use as an authoritative admission/spark/writer input. Do not add an event for every harmless diagnostic relabel. Valid ambiguous/quiescent/recirculating results remain successful observations; classifier/serialization failures can still abort a transaction as the proposal requires.

## 5. Small schema/scope items to settle during propagation

Preserve type-sensitive node IDs in every serialized record. A Python map with keys 0 and "0" cannot safely be serialized by blindly converting both keys to JSON object-member strings. Prefer typed per-node entries or the existing typed map encoding. The supported empty string remains an ordinary ID, not absence. Specify canonical ordering of SCC/member/terminal references independently of any semantic tie-break, and distinguish absent assignment from absent node information.

Enumerate the four selected implementation families or link an exact accepted support record. The attached proposal says four selected and six excluded but does not identify the four. The shared finite-graph argument does not implicitly grant native conformance to unnamed families.

The existing strict seed test is sound for the declared diagonal row Hessian. Square both represented gradient coordinates and the represented threshold exactly; do not first form an underflowing/overflowing rounded square. Resolve thresholds and sign convention through the declared binding. Seed existence must not change membership or admission. These are propagation requirements, not new scientific choices.

## 6. Executed independent pressure

`pressure.py` is an independent implementation of the written definition, not a patch or rerun of the submitting checker. It compares Tarjan SCC/condensation evaluation with a separate bitset transitive-closure oracle.

- All 66,067 directed support graphs on zero through four vertices, including every possible self-loop: 1 + 2 + 16 + 512 + 65,536 cases. Agreement, status coverage, forward closure and quiescent isolation hold throughout.
- 98,304 relabeling checks: all 24 permutations for each of the 4,096 loop-free four-vertex support graphs.
- 32,768 orientation/sign-reversal checks over 1,024 signed-current input vectors, including both signed zeros, subnormals, a self-loop and the distinct node labels empty string, integer zero and string zero.
- Opposite parallel currents, zero-current structural loop, nonzero terminal self-loop, nonfinite rejection, strict seed equality and exact squaring at underflow/overflow-sensitive represented values.
- A verified upstream-cycle example and a subnormal extra branch which changes unique assignment to ambiguity, consistent with the declared represented-sign policy.

All assertions pass. Native model runs: zero. No claim of native branch reachability, lifecycle conformance, stable attraction, empirical robustness, or independent execution of the original six tests is made.

## Recommendation

Retain the all-route SCC policy and separate seed layer. It is a coherent answer to a specifically chosen present-flow diagnostic interface, not a uniquely forced consequence of earlier theory. Add the three contract clarifications above before freezing the successor and finish the named-family/schema bindings during propagation. Then follow the stated authority -> paper -> spec/schema -> native conformance sequence. Keep abundance, stable attraction, identity persistence, completed sparks and hierarchy outside this acceptance. No rerun of the completed tranche-8 feasibility work is indicated by these findings.
