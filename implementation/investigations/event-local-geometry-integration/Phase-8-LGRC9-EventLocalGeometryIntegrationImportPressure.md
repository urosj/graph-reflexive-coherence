# Phase 8 LGRC9 Event-Local Geometry Integration Import Pressure

**Date:** 2026-08-16
**Status:** Completed before preparation-document integration
**Local authority:** `main@47a8a096e86a33b36466bee92738c52bf966ec50`

## Purpose

Pressure-test the external event-local geometry-integration preparation package
against the real Graph RC repository before any package document is adopted or
any source-changing work is authorized.

This record creates local review authority only. It does not reproduce Gate A
or Gate B, execute C0/C1, authorize an event-local geometry mechanism, open a
Phase 8 source-changing iteration, or select N32.

## Package Verification

```text
logical package id:
  2026-08-16-Phase8-LGRC9-EventLocalGeometryIntegration-PreparationPackage

outer archive sha256:
  e71b5326fcafc19ff61f3d6975d25fa9a79d54ea367aee5d7196c82f3a43fead

outer adjacent checksum:
  unavailable

outer gzip integrity:
  passed

package CHECKSUMS.sha256:
  35/35 passed

package manifest:
  32/32 declared package files present
  undeclared non-administrative files = 0

nested archive gzip integrity:
  5/5 passed

nested archive sha256:
  5/5 passed

nested internal checksum manifests:
  5/5 passed
  3,592/3,592 recorded files passed

JSON parse audit:
  2,398/2,398 passed

missing or unreadable load-bearing files:
  none
```

Three bundled checksum sidecars retain stale machine-local absolute names.
Their recorded digest values equal the corresponding bundled files, but the
sidecars cannot be executed directly from the extracted layout. This is a
non-blocking package-path defect because the package-level manifest and
checksums, nested archive digests, and nested internal manifests independently
close the content identities. The stale paths are not imported.

## Repository State

```text
branch = main
HEAD = 47a8a096e86a33b36466bee92738c52bf966ec50
archive Graph RC source = 47a8a096e86a33b36466bee92738c52bf966ec50
archive source is ancestor of HEAD = true
HEAD equals archive source = true
load-bearing source drift = none
worktree before this record = clean
proposed file-name collision = none
next unused Phase 8 iteration = 95
```

Because local `HEAD` exactly equals the archived Graph RC source, there are no
intervening changes to classify for Gate A, Gate B, C0/C1, LGRC timing or packet
execution, GRC transport, route arbitration, restoration, or Phase 8 authority.

## Pressure Matrix

| Pressure axis | Archive assumption | Current repository evidence | Consequence and adaptation | Status |
|---|---|---|---|---|
| Source revision | Graph RC `47a8a096...` | Local `HEAD` is exactly `47a8a096...` | No source rebinding or reproduction is required solely because of drift. | non-blocking agreement |
| Worktree authority | Clean source expected | Worktree was clean before this record | Iteration 95 may activate only if candidate source surfaces remain unchanged. | non-blocking agreement |
| Iteration numbering | 95-104 proposed | 95 and 96 are unused; 90-94 are the restoration-identity tranche | Retain 95 and 96; leave 97-104 unopened. | non-blocking agreement |
| Existing Phase 8 authority | Snippets propose additions | Current plan, checklist, and handoff contain later restoration/reset-baseline authority absent from package precedents | Merge small source-current addenda; never replace current authority wholesale. | adaptation required |
| Experiment versus implementation | C0/C1 precede implementation | Current Phase 8 precedents distinguish evidence gates from source-changing work | Store local registration and evidence beside the Phase 8 tranche; do not call them implementation evidence. | non-blocking agreement |
| External versus local evidence | Gate A/B are bundled external results | Checksums and exact source close provenance, but claim-bearing runs were not rerun locally | Admit both externally at their existing ceilings; do not write `locally reproduced` or `locally verified`. | bounded external admission |
| Gate A ceiling | Bounded synchronous-limit state-mediated readout | No native LGRC event-local read-back path exists | Preserve producer-orchestrated reconstruction and count sensitivity. | ceiling preserved |
| Gate B ceiling | Bounded synchronous-limit flux packetization in direct-funding domain | No native current-to-packet event recurrence exists | Preserve experiment-owned adapter/invocation and funding-domain boundary. | ceiling preserved |
| C0/C1 status | Prospective requirements only | No C0/C1 claim run or local registration exists | Bind a new registration to current `HEAD`, execute each claim matrix once, preserve raw output, then reconstruct independently. | evidence required |
| LGRC timing/packets | Native queue, packet, event, checkpoint, and proper-time surfaces exist | Current timing and packet modules expose those surfaces but no event-local geometry policy/current lifecycle | Reuse existing semantics in evidence; do not install new behavior in Iteration 96. | non-blocking agreement |
| GRC transport | Native synchronous reconstruction and flux exist | Current GRC transport can produce state-conditioned current | Use explicit reconstruction only in the producer-mediated C0/C1 probe. | non-blocking agreement |
| Native versus producer ownership | External global orchestration remains visible | No ordinary LGRC trigger owns reconstruction or flux packetization | Record the orchestrator as the missing ownership layer even if C1 is positive. | load-bearing boundary |
| Source-change envelope | Candidate and optional files proposed | One candidate module, `lgrc_9_v3_geometry.py`, does not exist | Freeze it as a possible future new file, not as an existing source surface. No envelope file may change in this task. | adaptation required |
| Restoration identity | Proposed mechanism may add replay state later | Restoration identity and reset-baseline corrections are current authority | I96 must use current snapshot/restoration behavior; any future identity change belongs to a separate source-changing iteration. | current authority supersedes precedent detail |
| Proposed specification | Complete conditional specification | Current normative LGRC spec does not install C2 | Adopt as prospective requirements; add only a non-behavioral pointer to the normative spec. | adopt with adaptation |
| N32 boundary | N32 remains downstream and unselected | Current repository also leaves N32 unselected | Preserve false in all records regardless of gate outcome. | hard boundary |
| Public claims | Candidate substrate continuation | Current project indexes do not claim it | Do not add a capability claim or update RCAE during I95/I96. | hard boundary |

## Additional Load-Bearing Tensions

### C2 identifier collision

N31 already uses `Candidate C.2` for a pre-native coherence-derived
susceptibility construction. This tranche's `C2` names a different prospective
Phase 8 event-local geometry-integration layer. All local records must use the
qualified name `event-local geometry integration C2` where ambiguity is
possible. Neither result may inherit the other's evidence or claim ceiling.

### Existing causal-availability vocabulary

Current LGRC surfaces already use `causal_availability_buffers` and a
`causal_availability_source` field in packet-arrival eligibility. Those fields
do not provide the proposed dependency-closed geometry-proposal authority or
current-realization lifecycle. The new specification must not claim that the
repository lacks all causal-availability vocabulary; it may claim that the
candidate event-local geometry authority record is absent.

### Full-drain and event-local evidence are not capability evidence

C0/C1 may establish pressure to naturalize an external orchestrator. They do
not establish that LGRC already owns that mechanism. A positive gate makes a
separate source-changing owner decision eligible; it does not open the change
automatically.

## Evidence Admission Decisions

### Gate A

```text
path = bounded_external_admission
source match = exact
archive integrity = passed
local claim-bearing rerun = false
ceiling = bounded_positive_state_mediated_synchronous_limit_readout
```

Local reproduction is not required for Iteration 95 because the evidence source
is exactly current `HEAD`, the complete artifact chain is readable and
checksum-clean, and C0/C1 will provide the source-current composition gate.

### Gate B

```text
path = bounded_external_admission
source match = exact
archive integrity = passed
local claim-bearing rerun = false
ceiling = B-DOMAIN
```

The same rationale applies. External identity and producer ownership remain
explicit; admission does not convert the run into local reproduction.

### Large external archives

The five nested archives remain external evidence inputs. They are not copied
into the repository. Committed local records retain their logical identities,
digests, source revisions, admission decisions, and claim ceilings without
machine-local paths.

## Archive Document Dispositions

| Archive document | Disposition | Local treatment |
|---|---|---|
| Event-local geometry-integration specification | adopt with source-current adaptation | Preserve full context; qualify C2; update local status after I96. |
| Dedicated implementation plan | adopt with source-current adaptation | Mark I95/I96 actual state and 97+ blocked. |
| Dedicated implementation checklist | adopt with source-current adaptation | Record completed checks and hard stop. |
| Baseline freeze Markdown/JSON | adopt with source-current adaptation | Replace inactive draft values with activated I95 evidence. |
| Contract schema Markdown/JSON | adopt with source-current adaptation | Retain as prospective, non-runtime C2 schema; no policy selection. |
| Evidence handoff | adopt with source-current adaptation | Record bounded admissions and local C0/C1 disposition. |
| Status JSON | superseded by current repository state | Replace with source-current machine state. |
| Phase 8 plan/checklist/handoff snippets | merge into existing authority | Use only as comparison aids; append manually. |
| Main LGRC spec snippet | merge into existing authority | Add prospective, non-behavioral reference only. |
| Gate A/B packages | retain only as external evidence | Record digests and bounded admissions; do not copy archives. |
| C0/C1 bridge and requirements contract | retain only as external evidence | Consume as requirements inputs to local registration. |
| Post-N31 and N26-N29 archives | retain only as external evidence | Preserve digest identities and source-role boundary. |
| Package precedents | superseded by current repository state | Current Phase 8 authority governs; precedents remain package context. |

## Source-Change Boundary

```text
Iteration 95 source behavior changes = forbidden
Iteration 96 source behavior changes = forbidden
event-local geometry integration C2 implemented = false
Phase 8 runtime implementation opened = false
post-implementation validation opened = false
N32 selected = false
```

The pressure review is non-blocking for conditional document integration and
Iteration 95. It does not decide the C2 source-change gate.
