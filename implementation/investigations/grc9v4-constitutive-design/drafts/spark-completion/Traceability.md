# Spark publication — sections, accepted claims and remaining debts

2026-11-01. Editorial traceability companion for the
[current GRC-v4 manuscript](../2026-11-GRC-V4.md) and
[self-contained spark proposal](./Proposal.md).
The [manuscript succession entry](../README.md#manuscript-succession) owns the
current adopted edition. This cross-reference does not create scientific
authority or replace a frozen contract binding.

## Scientific acceptance and manuscript adoption

All ten constructions and the five revised shorter endpoints have bounded
scientific acceptance. The user's acceptance and commit request on 2026-11-01
adopts the corrected consolidated proposal and integrated manuscript. Appendix H explains the accepted definitions, complete
maps, proof methods and witnesses; it does not introduce new constitutive laws,
close additional debts or grant native completion support.

The normative chains remain authority → decision → family proposal → family
paper → specification, with the explicit earlier-endpoint successor for the
first five rows below. Those exact source documents remain bound to their
existing hashes. Future manuscript work follows the new full edition; source
contracts retain their original editions until explicitly rebound.

## Manuscript review corrections — 2026-11-01

The supplied review found the central construction sound and requested
corrections to the exposition and auxiliary proofs. The following changes are
applied to both the proposal and Appendix H; the corresponding main-text
statements in §15 are aligned. The user accepted this corrected edition on
2026-11-01 and requested commit.

| Finding | Corrected statement | Location in proposal / Appendix H |
| --- | --- | --- |
| F1: composite carrier radius | C_CI_PC uses the certified signed radius 1/128; C_PC retains its distinct 1/64 radius. | §5.1 / H.5.1 |
| F2: selected C sector | Nonconstant modes lie above the cutoff, so the selected sector is the constant mode. Generated-Hodge dependence and resolvent Read-Back remain active. | §4.1 / H.4.1 |
| F3: OS norm | The spectral norm defines admission; the stricter Frobenius bound certifies these witnesses. | §5 / H.5; main §15.4 |
| F4: stationary A_OS geometry | The staged flat-map contraction forces the predictor flat to zero after the corrector current vanishes. Its uniform read bound applies to the entire A_OS anisotropic domain. | §4.2 / H.4.2 |
| RG2b proof definitions | The geometry bound measures deviation from identity; finite residual indices, proposal-domain membership and the error recurrence are explicit. Local inverse sharpening requires a verified footprint self-map. | §§5.1–6 / H.5.1–H.6 |
| Precision | Incident-edge rows are orientation neutral; star support is permitted support; terminal arrival concerns maximal routes; image margins are relative to the same physical/charge space. | §§2–4 / H.2–H.4; main §§15.2–15.3 |

The retained [focused FLINT check](../../scripts/check_spark_publication_corrections.py)
reproduces the carrier estimates and larger-radius counterexample, proves the
nonconstant spectral bound by exact LDL elimination, checks the full A_OS
domain against the shared read chart, and checks proposal/Appendix H equation
parity. Its A_OS bounds are image < 4.041e-5 and contraction < 2.29e-6 on the
radius-1/32 flat ball. It performs no physical evolution and does not regenerate
every full-state certificate. The publication validation record binds this
check to the corrected documents; accepted trajectories, contracts and debt
dispositions retain their existing authority.

## Section-to-claim correspondence

The proposal's numbered sections correspond to Appendix H with the same suffix:
proposal §3 is H.3, proposal §8 is H.8, and so on. The main result is in paper
§15; §16.8 and Appendix G.6 state its claim scope and provenance.

| Scientific content | Proposal / Appendix H | Main paper | Accepted source |
| --- | --- | --- | --- |
| Fixed-row seed, complete descent basins, parent footprint and local gain | §§2–2.1 / H.2–H.2.1 | §15.2 | `SC1-CL-N-GEOMETRIC-IDENTITY`, `SC1-CL-C-SPATIAL-BASINS` in the [initial authority](../../decisions/spark-completion/Authority.json) |
| Full-state invariant contraction and positive completion window | §3 / H.3 | §15.3 | `SC1-CL-C-RETURN`, `SC1-CL-C-COMPLETION`; family full-return claims below |
| Quartic site law and no resource source | §4 / H.4 | §15.4 | `SC3-CL-N-QUARTIC-SITE-BINDING`; each family's domain contracts |
| Exact A/C reads, all five complete maps and root/section admission | §§4–6 / H.4–H.6 | §15.4 | Family domain/root claims and their specification manifests below |
| Source graph, actual source beat, event/history transfer and exact inputs | §§7, 13 / H.7, H.13 | §15.4 | `SC2-CL-C-EXACT-SPARK-COMPLETION` and family completion claims; earlier endpoints retain the same source/event subjects |
| Anisotropic and carrier-product full-state domains | §8 / H.8 | §15.5 | `SC-EARLY-*-CL-C-FULL-TRAP` for the revised first five; `SC-ACI/APC/ACIPC-CL-C-FULL-TRAP` for the other anisotropic cases |
| Direct continuous RG2b domains without supporting tails | §9 / H.9 | §15.5 | `SC-CRG2B-CL-C-FULL-TRAP`, `SC-ARG2B-CL-C-FULL-TRAP` |
| Accepted shorter endpoints, durations, dimensions and gain | §10 / H.10 | §15.6 | Current completion claims in the family table below |
| Verified numerics, represented-map limits and occurrence lifecycle | §§3.1, 11–12 / H.3.1, H.11–H.12 | §§15.3, 15.7, A.7 | `SC3-CL-N-COMPLETION-SCHEMA`, `SC-EARLY-EC-PROVENANCE-LIFECYCLE` and pending native obligations |

The wildcard notation in this overview abbreviates the exact IDs in the next
table; it is not a new claim identifier.

## Current family claims and specification chains

For the revised first five families, the endpoint successor supplies the primary
full-trap and completion claims. Their earlier family domain/admission and event
contracts continue to apply. For the other five, the accepted family authority
already carries the primary short witness. Current gain is one for the original
event; reset, replay and replacement certificates add zero live gain.

| Family | Current primary claims | Current entry → completion; reset | Duration | Bound specification chain |
| --- | --- | --- | ---: | --- |
| C_OS | `SC-EARLY-COS-CL-C-FULL-TRAP`, `SC-EARLY-COS-CL-C-COMPLETION` | 374 → 376; 375 → 377 | 32 | [Earlier endpoints](../../../../../specs/grc-9-v4-spark-completion-earlier-source-manifest.json), [initial C_OS](../../../../../specs/grc-9-v4-spark-completion-source-manifest.json) |
| C_CI | `SC-EARLY-CCI-CL-C-FULL-TRAP`, `SC-EARLY-CCI-CL-C-COMPLETION` | 374 → 376; 375 → 377 | 32 | [Earlier endpoints](../../../../../specs/grc-9-v4-spark-completion-earlier-source-manifest.json), [C_CI admission](../../../../../specs/grc-9-v4-spark-completion-applicability-source-manifest.json) |
| C_PC | `SC-EARLY-CPC-CL-C-FULL-TRAP`, `SC-EARLY-CPC-CL-C-COMPLETION` | 374 → 376; 375 → 377 | 32 | [Earlier endpoints](../../../../../specs/grc-9-v4-spark-completion-earlier-source-manifest.json), [C_PC admission](../../../../../specs/grc-9-v4-spark-completion-pc-source-manifest.json) |
| C_CI_PC | `SC-EARLY-CCIPC-CL-C-FULL-TRAP`, `SC-EARLY-CCIPC-CL-C-COMPLETION` | 374 → 376; 375 → 377 | 32 | [Earlier endpoints](../../../../../specs/grc-9-v4-spark-completion-earlier-source-manifest.json), [C_CI_PC admission](../../../../../specs/grc-9-v4-spark-completion-ci-pc-source-manifest.json) |
| A_OS | `SC-EARLY-AOS-CL-C-FULL-TRAP`, `SC-EARLY-AOS-CL-C-COMPLETION` | 375 → 377; 372 → 374 | 32 | [Earlier endpoints](../../../../../specs/grc-9-v4-spark-completion-earlier-source-manifest.json), [A_OS admission](../../../../../specs/grc-9-v4-spark-completion-a-os-source-manifest.json) |
| A_CI | `SC-ACI-CL-C-DOMAIN`, `SC-ACI-CL-C-FULL-TRAP`, `SC-ACI-CL-C-COMPLETION` | 375 → 377; 372 → 374 | 32 | [A_CI](../../../../../specs/grc-9-v4-spark-completion-a-ci-source-manifest.json) |
| A_PC | `SC-APC-CL-C-DOMAIN`, `SC-APC-CL-C-FULL-TRAP`, `SC-APC-CL-C-COMPLETION` | 375 → 377; 372 → 374 | 32 | [A_PC](../../../../../specs/grc-9-v4-spark-completion-a-pc-source-manifest.json) |
| A_CI_PC | `SC-ACIPC-CL-C-DOMAIN`, `SC-ACIPC-CL-C-FULL-TRAP`, `SC-ACIPC-CL-C-COMPLETION` | 375 → 377; 372 → 374 | 32 | [A_CI_PC](../../../../../specs/grc-9-v4-spark-completion-a-ci-pc-source-manifest.json) |
| C_RG2b | `SC-CRG2B-CL-C-DOMAIN`, `SC-CRG2B-CL-C-FULL-TRAP`, `SC-CRG2B-CL-C-COMPLETION` | 390 → 392; 390 → 392 | 8 | [C_RG2b](../../../../../specs/grc-9-v4-spark-completion-c-rg2b-source-manifest.json) |
| A_RG2b | `SC-ARG2B-CL-C-DOMAIN`, `SC-ARG2B-CL-C-FULL-TRAP`, `SC-ARG2B-CL-C-COMPLETION` | 300 → 302; 300 → 302 | 16 | [A_RG2b](../../../../../specs/grc-9-v4-spark-completion-a-rg2b-source-manifest.json) |

The [earlier-endpoint claim/debt ledger](../../evidence/spark-completion/applicability/earlier-closure/EarlierSC3ClaimDebtLedger.json)
retains the initial claims as history and adds the ten revised endpoint claims.
Its adoption-time `next` text is a historical workflow note; the
[current manuscript entry](../README.md) and handoff govern editorial continuation.

## Debt dispositions and forward owners

| Debt or obligation | Current disposition | Manuscript treatment / owner |
| --- | --- | --- |
| `SC-DEBT-ORGANIZATION` | Partially resolved at bounded scientific scope | H.2, H.7 and H.10 instantiate the chosen local organization; broader/native portions remain. |
| `SC-DEBT-STABILITY` | Partially resolved at bounded scientific scope | H.3, H.8 and H.9 prove the declared full-state local stability; no arbitrary-profile stability claim. |
| `SC-DEBT-NONEMPTY-DOMAIN` | Partially resolved at bounded scientific scope | Ten concrete constructions; no universal graph/parameter applicability. |
| `SC-DEBT-TEMPORAL-LIFECYCLE` | Partially resolved at bounded scientific scope | H.11 states the window and lifecycle obligations; native execution remains separate. |
| `SC2-DEBT-NONLINEAR-SITE-BINDING` | Resolved at bounded scientific/design scope | H.4 consumes the accepted homogeneous quartic law. |
| Nine `SC-APP-DEBT-*` rows, C_CI through A_RG2b | Resolved at bounded scientific scope | Family applicability is complete; each retains its own native numerics/lifecycle obligations. C_OS is covered by the initial SC-1–SC-3 authority, not an invented tenth applicability debt. |
| Five earlier endpoint adoptions | Resolved at bounded scientific scope | Ten successor claims and seven contracts; no additional event gain or aggregate-debt closure. |
| Native numerics and lifecycle for all ten families | Pending forward | P9-9.1a; represented full-map error, exact charge, predicates, history directions and atomic occurrence accounting. |
| Aggregate reconciliation and G4 | Open | P9-10.5/10.6; scientific completion does not imply aggregate closeout. |
| Native hierarchy execution | Open | Forward lifecycle/implementation work; Appendix A.7 retains this boundary. |

The two native IDs for C_OS are `SC-VO-NATIVE-NUMERICS` and
`SC-VO-NATIVE-LIFECYCLE`. For the remaining families they are
`SC-<code>-VO-NATIVE-NUMERICS` and `SC-<code>-VO-NATIVE-LIFECYCLE`, with codes
`CCI`, `CPC`, `CCIPC`, `AOS`, `ACI`, `APC`, `ACIPC`, `CRG2B`, `ARG2B`.
The earlier-endpoint successor additionally binds its selected endpoint
obligations without closing these native tasks.

The [aggregate reconciliation contribution](../../../../phase-9-grcv4/tranche-10/P9-10.5-10.6-SparkEarlierReconciliation.json)
explicitly leaves aggregate debts, native support, hierarchy and G4 open.
The adoption-time repository audit failure, `basin propagation source drift:
specs/README.md`, is resolved by the maintenance repair below. The original
authority retains its historical audit note; its scientific scope is unchanged.

## Repository boundary repair — 2026-11-01

The [document succession reader](../../../../phase-9-grcv4/verification/p9_spark_document_epoch.py)
authenticates the five named registry/planning successors and reconstructs their
exact basin-era Git bytes. The spark checkpoint is pinned; the later checklist
and three repaired provenance readers additionally require the finite SC-3
metadata binding. Every live read is checked, even when immutable Git blobs are
cached. The basin manifest, original insertions and packaged release keep their
existing hashes. No blanket document exemption is introduced.

The [regression checks](../../../../phase-9-grcv4/verification/test_p9_spark_document_epoch.py)
cover all 392 reconciliation context bindings, original document insertions,
unrelated edits, altered metadata, cached-read tampering and fresh-process import
order. All seven pass, as do the six basin authority/surface tests. The complete
boundary audit passes with ten accepted exact profiles and verified handoff
integrity, without numerical reruns. This clears the maintenance failure;
native spark completion, aggregate reconciliation and G4 keep their separate
dispositions above.

## Side-tool correspondence

The [inspection guide](../../tools/exploratory-side-tool/docs/SparkCompletionOverview.md)
maps each primary witness to its accepted API and browser panel. The
`earlier-accepted` surface provides the five adopted shorter endpoints;
the A_CI, A_PC, A_CI_PC, C_RG2b and A_RG2b surfaces retain their accepted short
witnesses. The earlier source panels remain historical views.

The browser's publication links and notebook reading cell expose this
cross-reference, the current manuscript, proposal and stable entry point as
**adopted editorial documents**. Their source route checks the current validation
hashes. These reading links are separate from the accepted scientific
projections, whose authority digests and frozen source downloads are preserved.

Synchronization checks compare all eleven specification manifests and their
contract bodies, the accepted all-ten and earlier-endpoint projections, the
family/debt dispositions, and the manuscript/proposal endpoint tables. This
establishes consistency with accepted subjects; it is not a new independent
mathematical review or a fresh physical campaign.
