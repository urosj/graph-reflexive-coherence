# Catalogs And Evidence Reference Guide

Last updated: 2026-05-04.

This guide explains how PyGRC records evidence, diagnostic results, selector
validation, reviewed motif catalogs, corrected growth catalogs, source-language
handoffs, landscape-inference reports, and motion catalogs.

Catalogs are review artifacts. They do not create runtime behavior. They
organize evidence already produced by runtime, telemetry, selector, inference,
or visual-review sessions.

## Scope

Use this guide when you want to:

- find accepted, strong-candidate, diagnostic, rejected, or superseded records,
- understand mechanism ledgers and hypothesis catalogs,
- inspect selector manifests and selector reports,
- locate reviewed motif catalogs for GRC9, GRC9V3, GRCL-9, GRCL-9V3, and motion,
- distinguish source-language handoffs from runtime evidence,
- understand legacy-growth supersession and diagnostic-only records.

For row/event/checkpoint formats, see `Telemetry-ReferenceGuide.md`. For
runtime behavior, see `GRC-Runtime-ReferenceGuide.md`. For GRCL replay and
selector validation commands, see `GRCL-ReferenceGuide.md`.

## Contents

- [Quick Start](#quick-start)
- [Authority Order](#authority-order)
- [Common Evidence Terms](#common-evidence-terms)
- [Evidence Pipeline](#evidence-pipeline)
- [Mechanism Ledgers](#mechanism-ledgers)
- [Hypothesis And Seed Catalogs](#hypothesis-and-seed-catalogs)
- [Selector Validation](#selector-validation)
- [Reviewed Runtime Motif Catalogs](#reviewed-runtime-motif-catalogs)
- [GRCL Lowered Motif Catalogs](#grcl-lowered-motif-catalogs)
- [Corrected Growth Supersession](#corrected-growth-supersession)
- [Landscape Inference Reports](#landscape-inference-reports)
- [Motion Catalog](#motion-catalog)
- [Locating Accepted Vs Diagnostic Vs Rejected Evidence](#locating-accepted-vs-diagnostic-vs-rejected-evidence)
- [Finding The Latest Session](#finding-the-latest-session)
- [Troubleshooting](#troubleshooting)

## Quick Start

To inspect the current reviewed GRCL-9V3 lowered catalog:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
import json
from pathlib import Path

path = Path("outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json")
catalog = json.loads(path.read_text(encoding="utf-8"))

print(catalog["summary"])
print("accepted:", len(catalog["accepted_motifs"]))
print("strong:", len(catalog["strong_candidate_motifs"]))
print("superseded:", len(catalog["superseded_motifs"]))
print("rejected:", len(catalog["rejected_motifs"]))
PY
```

To inspect the current motion catalog:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
import json
from pathlib import Path

path = Path("outputs/motion/sessions/S0006/reviewed_motion_catalog.json")
catalog = json.loads(path.read_text(encoding="utf-8"))

print(catalog["aggregate"]["status_counts"])
print(catalog["aggregate"]["accepted_motion_kind_counts"])
PY
```

The examples are shell snippets with embedded Python heredocs, so they are
tagged as `bash`.

## Authority Order

Evidence review follows this order:

1. Runtime state transition and emitted events.
2. Telemetry rows, run summaries, and graph checkpoints.
3. Field-backed selectors and inference classifiers.
4. Visual artifacts as supporting review evidence only.
5. Reviewed catalogs and handoffs.
6. Source-language examples and seeds as preconditions only.

Catalogs may promote, reject, supersede, or preserve evidence, but they must
link back to underlying artifacts.

## Common Evidence Terms

| Term | Meaning |
|---|---|
| `accepted` | Reviewed evidence is strong enough for the catalog's stated claim. |
| `strong_candidate` | Selector-backed or review-backed evidence is strong, but not accepted by the current policy. |
| `candidate` | Evidence is present but weaker or less complete than strong candidate. |
| `weak_candidate` | Partial evidence, missing selectors, or reduced confidence. |
| `ambiguous` | Evidence is real but admits more than one interpretation. |
| `diagnostic` | Useful observation that is not accepted evidence for the main claim. |
| `diagnostic_comparator` | Diagnostic comparison surface, usually for backend or parameter contrasts. |
| `rejected` | Reviewed evidence fails the expected predicate or claim boundary. |
| `duplicate` | Same evidence as another reviewed record; retained as link, not accepted twice. |
| `needs_rerun` | Run artifacts were insufficient or stale for review. |
| `superseded` | Short catalog bucket for evidence retained as historical or diagnostic after a stronger replacement exists. |
| `superseded_by_growth_semantics_correction` | Legacy growth evidence preserved as history after corrected front-capacity semantics. |

Exact labels vary by catalog family. Always inspect `review_policy`,
`summary.review_status_counts`, or `catalog_decision`.

In growth-correction catalogs, `superseded_by_growth_semantics_correction` is
the explicit reason. In summary buckets and quick counts, this may appear under
the shorter `superseded` category.

## Evidence Pipeline

The common discovery/review pipeline is:

```text
paper/theory mechanism
  -> mechanism ledger
  -> hypothesis/seed catalog
  -> deterministic runtime or source replay session
  -> telemetry rows + checkpoints
  -> selector validation
  -> reviewed catalog
  -> source-language handoff or downstream guide
```

For GRCL and motion, the pipeline begins from source/lowering or synthetic
motion examples but still uses telemetry/inference artifacts as the evidence
boundary.

## Mechanism Ledgers

Mechanism ledgers translate theory mechanisms into graph-local conditions,
predicted telemetry fields, runtime status, and expected selector surfaces.

Main modules:

| Family | Module | Typical Artifact |
|---|---|---|
| GRC9 | `src/pygrc/discovery/grc9_mechanism_ledger.py` | `outputs/grc9/phenomenology_discovery/sessions/S0001/reports/mechanism_ledger.json` |
| GRC9V3 | `src/pygrc/discovery/grc9v3_mechanism_ledger.py` | `outputs/grc9v3/phenomenology_discovery/sessions/S0001/reports/mechanism_ledger.json` |

Ledger records are not runtime evidence. They say what should be tested and
which runtime support exists.

Inspect:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
import json
from pathlib import Path

path = Path("outputs/grc9/phenomenology_discovery/sessions/S0001/reports/mechanism_ledger.json")
data = json.loads(path.read_text())
print(data.keys())
PY
```

## Hypothesis And Seed Catalogs

Hypothesis catalogs define seed families and expected selector signatures.
Generated seed catalogs record concrete deterministic seeds.

Typical artifacts:

- `outputs/grc9/phenomenology_discovery/sessions/S0002/reports/hypothesis_catalog.json`
- `outputs/grc9/phenomenology_discovery/sessions/S0003/reports/generated_seed_catalog.json`
- `outputs/grc9v3/phenomenology_discovery/sessions/S0002/reports/hypothesis_catalog.json`
- `outputs/grc9v3/phenomenology_discovery/sessions/S0003/reports/generated_seed_catalog.json`

These catalogs are setup artifacts. They become evidence only after replay and
selector validation.

## Selector Validation

Selector sessions apply field-backed predicates to replayed telemetry.

Typical artifacts:

- `selector_manifest.json`
- `reports/selector_validation_report.json`
- `reports/selector_validation_summary.md`

Selector result fields usually include:

- `selector_id`
- `field_path`
- `passed`
- `observed_value`
- `failure_kind`

Important `failure_kind` values:

| Failure Kind | Meaning |
|---|---|
| `predicate_failed` | The telemetry surface existed, but the selector predicate did not pass. |
| `missing_surface` | Required field path was absent. |
| `none` or null-equivalent | Selector passed or failure kind is not applicable. |

Selector labels such as `strong_candidate`, `ambiguous`, or `rejected` are
intermediate validation labels, not final catalog status.

Inspect selector status counts:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
import json
from pathlib import Path

path = Path("outputs/grc9v3/phenomenology_discovery/sessions/S0009/selector_manifest.json")
data = json.loads(path.read_text())
print(data.keys())
print(data.get("summary", data.get("aggregate", {})))
PY
```

## Reviewed Runtime Motif Catalogs

Reviewed motif catalogs promote selector-backed runtime motifs and preserve
non-accepted records.

### GRC9

Main module:

- `src/pygrc/discovery/grc9_reviewed_motif_catalog.py`

Current anchor:

- `outputs/grc9/phenomenology_discovery/sessions/S0025/reviewed_motif_catalog.json`
- `outputs/grc9/phenomenology_discovery/sessions/S0025/reviewed_manifest.json`
- `outputs/grc9/phenomenology_discovery/sessions/S0025/reports/reviewed_motif_catalog_summary.md`

S0025 summary:

- 57 motifs reviewed in the implementation record,
- 10 accepted GRC9-native motifs,
- strong candidates and rejected motifs remain in the reviewed manifest,
- `reviewed_motif_catalog.json` contains accepted motifs only plus status counts.

Rebuild:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_reviewed_motif_catalog \
  --session-id S0025 \
  --selector-session-id S0022
```

### GRC9V3

Main module:

- `src/pygrc/discovery/grc9v3_reviewed_motif_catalog.py`

Current runtime motif anchor:

- `outputs/grc9v3/phenomenology_discovery/sessions/S0012/reviewed_motif_catalog.json`
- `outputs/grc9v3/phenomenology_discovery/sessions/S0012/reviewed_motif_catalog.md`
- `outputs/grc9v3/phenomenology_discovery/sessions/S0012/reports/reviewed_motif_catalog_summary.md`

S0012 summary:

- 7 reviewed runtime motif records,
- 3 accepted lifecycle motifs,
- 2 strong candidates,
- 2 diagnostic comparators,
- 0 rejected.

Rebuild:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9v3_reviewed_motif_catalog \
  --session-id S0012 \
  --selector-session-id S0009 \
  --visual-session-id S0010 \
  --hessian-review-session-id S0011
```

GRC9V3 breadth expansion and source-language handoff:

- `outputs/grc9v3/phenomenology_discovery/sessions/S0013/expanded_motif_catalog.json`
- `outputs/grc9v3/phenomenology_discovery/sessions/S0014/source_language_handoff.json`

The handoff is not a runtime catalog. It translates reviewed runtime motifs into
source-language planning inputs.

## GRCL Lowered Motif Catalogs

GRCL catalogs review source/lowering/replay evidence. They do not prove source
truth; they accept selector-backed lowered-source examples.

### GRCL-9

Main module:

- `src/pygrc/telemetry/grcl9_lowered_motif_catalog.py`

Current reviewed lowered catalog anchor:

- `outputs/grcl9/lowering/sessions/S0025/reviewed_grcl9_lowered_motif_catalog.json`
- `outputs/grcl9/lowering/sessions/S0025/reports/reviewed_grcl9_lowered_motif_catalog_summary.md`

S0025 summary:

- 12 accepted lowered motifs,
- 0 rejected motifs,
- 12 collapse-adjacent diagnostic records,
- 7 ambiguous collapse-like diagnostics and 5 runtime-collapse-like diagnostics.

Rebuild:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_lowered_motif_catalog \
  --session-id S0025 \
  --source-session-id S0024
```

Legacy sessions are refused unless explicitly forced:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_lowered_motif_catalog \
  --session-id S9999 \
  --source-session-id S0030 \
  --force-legacy-growth
```

Forced legacy catalogs remain historical diagnostics.

### GRCL-9 Corrected Growth Catalog

Main module:

- `src/pygrc/telemetry/grcl9_corrected_growth_catalog.py`

Current anchor:

- `outputs/grcl9/lowering/sessions/S0036/corrected_grcl9_growth_catalog.json`
- `outputs/grcl9/lowering/sessions/S0036/reports/corrected_grcl9_growth_catalog_summary.md`

S0036 summary:

- 21 accepted corrected growth motifs,
- 7 accepted corrected control motifs,
- 0 accepted legacy broad-growth motifs,
- 13 supersession links from corrected evidence to preserved legacy history,
- supersession links preserve legacy history as non-evidence.

Rebuild:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_corrected_growth_catalog \
  --session-id S0036
```

### GRCL-9V3

Main module:

- `src/pygrc/telemetry/grcl9v3_lowered_motif_catalog.py`

Current reviewed lowered catalog anchor:

- `outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json`
- `outputs/grcl9v3/lowering/sessions/S0072/reports/reviewed_grcl9v3_lowered_motif_catalog_summary.md`

S0072 summary:

- 56 reviewed lowered-source records,
- 28 accepted motifs,
- 2 strong candidates,
- 26 superseded legacy-growth diagnostics,
- 12 accepted growth records,
- 0 rejected.

Rebuild:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_lowered_motif_catalog \
  --session-id S0072 \
  --selector-session-id S0076
```

## Corrected Growth Supersession

Corrected growth catalogs supersede legacy broad-growth evidence.

Main modules:

- `src/pygrc/discovery/grc9_corrected_growth_catalog.py`
- `src/pygrc/telemetry/grcl9_corrected_growth_catalog.py`
- `src/pygrc/telemetry/grc9_grcl9_growth_supersession_summary.py`

Key anchors:

- `outputs/grc9/phenomenology_discovery/sessions/S0035/corrected_grc9_growth_catalog.json`
- `outputs/grcl9/lowering/sessions/S0036/corrected_grcl9_growth_catalog.json`

Accepted growth evidence requires:

- front-capacity parent eligibility,
- lowest-port attachment where applicable,
- selector-backed growth provenance,
- no accepted legacy broad-growth count.

Legacy broad-growth records remain replayable but are not accepted evidence.

## Landscape Inference Reports

Landscape inference currently emits classifier reports rather than one reviewed
catalog.

Important artifacts:

- `outputs/landscape_inference/sessions/S0006/basin_inference_report.json`
- `outputs/landscape_inference/sessions/S0007/valley_ranking_report.json`
- `outputs/landscape_inference/sessions/S0008/ridge_inference_report.json`
- `outputs/landscape_inference/sessions/S0009/junction_inference_report.json`
- `outputs/landscape_inference/sessions/S0010/pheromone_inference_report.json`
- `outputs/landscape_inference/sessions/S0011/comparison_summary.json`
- `outputs/landscape_inference/sessions/S0014/*/revival_probe_report.json`

Common classifier statuses:

- `accepted`
- `ambiguous`
- `rejected`
- `weak`
- diagnostic-only via substrate metadata

Short checkpoint windows can intentionally downgrade valley, ridge, and
pheromone claims to diagnostic or ambiguous status. The revival probe in S0014
is diagnostic only.

## Motion Catalog

Main module:

- `src/pygrc/landscapes/motion_catalog.py`

Current anchor:

- `outputs/motion/sessions/S0006/reviewed_motion_catalog.json`
- `outputs/motion/sessions/S0006/reviewed_motion_catalog.md`

S0006 aggregate:

- accepted motion kinds include boundary, coherence, identity, representative,
  and topological records,
- accepted entries include structural controls, authored seed projections,
  long-window examples, and dense confirmed fission,
- diagnostic entries preserve dense branching and landscape-derived contrasts,
- ambiguous entries preserve identity/topology disagreements,
- rejected entries preserve failed continuity controls.

Rebuild:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.landscapes.motion_catalog \
  --session-id S0006
```

Motion catalog authority:

- reviews existing motion artifacts only,
- emits no new motion records,
- preserves visual artifacts as support only,
- keeps dense branching diagnostic unless promoted by membership/provenance
  linkage.

## Locating Accepted Vs Diagnostic Vs Rejected Evidence

Use these fields first:

| Artifact Type | Where To Look |
|---|---|
| Reviewed GRC9 catalog | `reviewed_manifest.json` for all statuses; `reviewed_motif_catalog.json` for accepted motifs. |
| Reviewed GRC9V3 catalog | `summary.review_status_counts`, `records[*].catalog_category`, `diagnostic_records`. |
| GRCL-9 lowered catalog | `summary`, `accepted_motifs`, `rejected_motifs`, `collapse_diagnostics`. |
| GRCL-9 corrected growth catalog | `accepted_corrected_growth_motifs`, `accepted_corrected_control_motifs`, `rejected_motifs`, `summary.accepted_legacy_broad_growth_count`, `summary.supersession_link_count`. |
| GRCL-9V3 lowered catalog | `accepted_motifs`, `strong_candidate_motifs`, `diagnostic_motifs`, `superseded_motifs`, `rejected_motifs`. |
| Motion catalog | `entries[*].status`, `entries[*].catalog_decision`, `aggregate.*_entry_ids`. |
| Landscape inference | classifier report `candidates[*].status` and substrate `diagnostic_only`. |

Minimal catalog shape:

```json
{
  "catalog_version": "catalog_family_version",
  "summary_or_aggregate": {
    "accepted_count": 0,
    "rejected_count": 0
  },
  "accepted_motifs": [],
  "diagnostic_motifs": [],
  "rejected_motifs": [],
  "review_policy": {}
}
```

Exact top-level keys differ by family. Use the family section above to choose
the status fields to inspect first.

Example:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
import json
from pathlib import Path

path = Path("outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json")
catalog = json.loads(path.read_text())

print("summary:", catalog["summary"])
print("accepted:", len(catalog["accepted_motifs"]))
print("strong:", len(catalog["strong_candidate_motifs"]))
print("superseded:", len(catalog["superseded_motifs"]))
print("rejected:", len(catalog["rejected_motifs"]))
PY
```

Motion example:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
import json
from pathlib import Path

path = Path("outputs/motion/sessions/S0006/reviewed_motion_catalog.json")
catalog = json.loads(path.read_text())

print(catalog["aggregate"]["status_counts"])
print("accepted entries:", len(catalog["aggregate"]["accepted_entry_ids"]))
print("diagnostic entries:", len(catalog["aggregate"]["diagnostic_entry_ids"]))
PY
```

## Claim Boundaries

Do not promote:

- source preconditions without replay,
- selector failures with missing surfaces,
- visual-only observations,
- legacy broad-growth rows,
- diagnostic comparators,
- motion dense branching without continuity/membership promotion,
- landscape inference diagnostic probes,
- handoff records without downstream source/lowering replay.

Accepted catalogs should preserve non-claims such as:

- source declares preconditions, not outcomes,
- visuals support review but never promote,
- catalog acceptance is selector-backed telemetry evidence,
- legacy growth records are historical diagnostics after correction.

## Quick Reference: Current Anchors

| Surface | Anchor |
|---|---|
| GRC9 reviewed runtime motifs | `outputs/grc9/phenomenology_discovery/sessions/S0025/reviewed_motif_catalog.json` |
| GRC9 corrected growth | `outputs/grc9/phenomenology_discovery/sessions/S0035/corrected_grc9_growth_catalog.json` |
| GRC9 to GRCL-9 handoff | `outputs/grc9/phenomenology_discovery/sessions/S0026/grcl9_suitability_catalog.json` |
| GRC9V3 reviewed runtime motifs | `outputs/grc9v3/phenomenology_discovery/sessions/S0012/reviewed_motif_catalog.json` |
| GRC9V3 source handoff | `outputs/grc9v3/phenomenology_discovery/sessions/S0014/source_language_handoff.json` |
| GRCL-9 reviewed lowered motifs | `outputs/grcl9/lowering/sessions/S0025/reviewed_grcl9_lowered_motif_catalog.json` |
| GRCL-9 corrected growth | `outputs/grcl9/lowering/sessions/S0036/corrected_grcl9_growth_catalog.json` |
| GRCL-9V3 reviewed lowered motifs | `outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json` |
| Motion reviewed catalog | `outputs/motion/sessions/S0006/reviewed_motion_catalog.json` |
| Landscape inference revival diagnostics | `outputs/landscape_inference/sessions/S0014/` |

These anchors are workspace evidence points, not immutable API promises. Prefer
the replay commands in session manifests when regenerating.

## Finding The Latest Session

Session ids are ordered `S####` strings inside a family-specific session root.
To list the most recent local sessions:

```bash
find outputs/grcl9v3/lowering/sessions -maxdepth 1 -type d -name 'S*' | sort | tail
find outputs/grc9/phenomenology_discovery/sessions -maxdepth 1 -type d -name 'S*' | sort | tail
find outputs/motion/sessions -maxdepth 1 -type d -name 'S*' | sort | tail
```

Latest is not automatically best. Prefer sessions with the expected catalog
file, selector manifest, and summary report for the task:

```bash
find outputs/grcl9v3/lowering/sessions -name reviewed_grcl9v3_lowered_motif_catalog.json | sort
find outputs/motion/sessions -name reviewed_motion_catalog.json | sort
```

When in doubt, open `session_manifest.json` or `README.md` in the session root.
Those files usually include replay commands and source-session links.

## Validation Commands

Check anchor files exist:

```bash
for path in \
  outputs/grc9/phenomenology_discovery/sessions/S0025/reviewed_motif_catalog.json \
  outputs/grc9v3/phenomenology_discovery/sessions/S0012/reviewed_motif_catalog.json \
  outputs/grcl9/lowering/sessions/S0036/corrected_grcl9_growth_catalog.json \
  outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json \
  outputs/motion/sessions/S0006/reviewed_motion_catalog.json
do
  test -f "$path" && echo "ok $path"
done
```

Summarize catalog counts:

```bash
PYTHONPATH=src ./.venv/bin/python - <<'PY'
import json
from pathlib import Path

paths = [
    "outputs/grc9/phenomenology_discovery/sessions/S0025/reviewed_motif_catalog.json",
    "outputs/grc9v3/phenomenology_discovery/sessions/S0012/reviewed_motif_catalog.json",
    "outputs/grcl9/lowering/sessions/S0036/corrected_grcl9_growth_catalog.json",
    "outputs/grcl9v3/lowering/sessions/S0072/reviewed_grcl9v3_lowered_motif_catalog.json",
    "outputs/motion/sessions/S0006/reviewed_motion_catalog.json",
]

for raw in paths:
    data = json.loads(Path(raw).read_text())
    print(raw)
    print(data.get("summary") or data.get("aggregate") or data.get("review_status_counts"))
PY
```

## Troubleshooting

Common issues:

- Missing anchor file: the workspace may not have generated that session.
  Search for nearby sessions with `find ... -name <catalog-file>.json`.
- Stale session id: use the session's `session_manifest.json`, `README.md`, or
  replay command to understand what source sessions it reviewed.
- Selector-backed catalog has fewer accepted records than expected: inspect the
  selector report first. `missing_surface` means telemetry did not expose the
  required field; `predicate_failed` means the field existed but failed.
- Legacy growth records are present: they should remain diagnostic or
  superseded unless the command was explicitly forced for historical review.
- Visual artifacts look convincing but the catalog rejected the record: keep the
  catalog decision. Visuals are support only.
- Landscape inference reports differ from reviewed catalogs: landscape
  inference emits observer classifications; catalog acceptance is a separate
  review layer.

## Related Guides

- `Telemetry-ReferenceGuide.md`
- `GRC-Runtime-ReferenceGuide.md`
- `GRCL-ReferenceGuide.md`
- `LandscapeInference-ReferenceGuide.md`
- `Motion-ReferenceGuide.md`
- `GraphVisualization-ReferenceGuide.md`
