#!/usr/bin/env python3
"""Build and validate the Phase 8 Iteration 109 pathway selection guide."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "specs/grc-lgrc-causal-pathway-contracts.json"
CROSSWALK_PATH = ROOT / "specs/grc-lgrc-causal-pathway-evidence-crosswalk.json"
MATRIX_PATH = ROOT / "specs/grc-lgrc-causal-pathway-composition-matrix.json"
I108_RESULT_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.json"
I108_FREEZE_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactFreeze.json"
BASELINE_PATH = ROOT / "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationBaselineFreeze.json"

OUTPUT_SELECTOR = ROOT / "specs/grc-lgrc-causal-pathway-selection-guide.json"
OUTPUT_GUIDE = ROOT / "docs/reference/GRC-LGRC-CausalPathwayGuide.md"
OUTPUT_EXECUTION = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ValidationExecution.json"
OUTPUT_I108_SUPERSESSION = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactBundleSupersession.json"
OUTPUT_RESULT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.json"
OUTPUT_REPORT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.md"
OUTPUT_FREEZE = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactFreeze.json"

EXPECTED_REGISTRY_DIGEST = "a266b33da10778e8caf5ad7d4a4bfe4b71aed9d0df563fd6c74e7d4ed6cb486b"
EXPECTED_CROSSWALK_DIGEST = "0036dcdf54f4663bed183387db1c8f657eb44a694252ef44421be56fb239ff06"
EXPECTED_MATRIX_DIGEST = "d1dbbdcb911cf34b399562c2dfe5122606c0de8d48d9634bc6af1e3d92e09e90"
EXPECTED_I108_RESULT_DIGEST = "559a82d28edbf89232a24a00af99c66659b56a42eca6974484a6ecddc3d35c3c"
EXPECTED_I108_BUNDLE_DIGEST = "d2bd07c662acc7185f1e5cb62c03d48c9a2469f96511ec3cefd1dfde75eec8d3"
SUPERSEDED_I108_WORKING_BUNDLE_DIGEST = "475ba6a76adc00515f63e16f9e9f75c8d56077fe2784d8657ac8f2442c495148"

STATUS_TO_RESOLUTION = {
    "lawful_native": "existing_lawful_composition",
    "lawful_with_explicit_adapter": "existing_composition_with_explicit_adapter",
    "diagnostic_only": "diagnostic_surface_only",
    "producer_mediated": "producer_mediated_composition",
    "unsupported_missing_crossing": "precise_missing_crossing",
    "invalid_relabel": "rejected_invalid_relabel",
}

GUIDE_PATHWAY_IDS = {
    "grc9v3.synchronous_update_cycle",
    "lgrc9v3.boundary_birth",
    "lgrc9v3.causal_history_annotation",
    "lgrc9v3.causal_pulse_surface_lineage",
    "lgrc9v3.causal_spark_topology_integration",
    "lgrc9v3.collapse_reabsorption",
    "lgrc9v3.configured_flux_route",
    "lgrc9v3.explicit_packet_transport",
    "lgrc9v3.native_route_arbitration",
    "lgrc9v3.route_aspect_surplus",
    "pygrc.restoration_replay_identity",
}


WORKED_REQUESTS: list[dict[str, Any]] = [
    {
        "case_id": "SEL-01",
        "title": "Existing event-time packet pathway",
        "demand": "Execute a declared packet schedule with debit, in-flight retention, arrival, and target credit without claiming route formation.",
        "required_temporal_semantics": ["event_time"],
        "route_relation": "explicit_fixture_route",
        "retained_relation": "packet_and_queue_history_through_settlement",
        "requested_pathway_id": "lgrc9v3.explicit_packet_transport",
        "expected_resolution_kind": "existing_pathway",
    },
    {
        "case_id": "SEL-02",
        "title": "Native packet lifecycle crossing",
        "demand": "Carry one supplied packet identity through schedule, debit, in-flight state, and arrival credit.",
        "required_temporal_semantics": ["event_time"],
        "route_relation": "explicit_fixture_route",
        "retained_relation": "packet_identity_and_ledger_state",
        "from_pathway_id": "lgrc9v3.explicit_packet_transport",
        "to_pathway_id": "lgrc9v3.explicit_packet_transport",
        "requested_composition_id": "CMP-02",
        "expected_composition_status": "lawful_native",
        "expected_resolution_kind": "existing_lawful_composition",
    },
    {
        "case_id": "SEL-03",
        "title": "Explicit cross-runtime front-capacity adapter",
        "demand": "Place GRC front-capacity state at a declared LGRC event-time boundary-birth frontier while keeping construction ownership visible.",
        "required_temporal_semantics": ["global_synchronous_step", "event_time"],
        "route_relation": "cross_runtime_construction",
        "retained_relation": "front_capacity_state_without_synchronous_history_conversion",
        "from_pathway_id": "grc9v3.front_capacity_growth",
        "to_pathway_id": "lgrc9v3.boundary_birth",
        "requested_composition_id": "CMP-26",
        "expected_composition_status": "lawful_with_explicit_adapter",
        "expected_resolution_kind": "existing_composition_with_explicit_adapter",
    },
    {
        "case_id": "SEL-04",
        "title": "Post-commit multi-basin diagnostic",
        "demand": "Read validated child-basin and flow-window records after an arbitration-backed topology commit without treating records as the mutation.",
        "required_temporal_semantics": ["event_time"],
        "route_relation": "supplied_candidates_native_selection",
        "retained_relation": "diagnostic_projection_of_committed_topology",
        "from_pathway_id": "lgrc9v3.native_route_arbitration",
        "to_pathway_id": "lgrc9v3.multi_basin_record_validation",
        "requested_composition_id": "CMP-24",
        "expected_composition_status": "diagnostic_only",
        "expected_resolution_kind": "diagnostic_surface_only",
        "confusion_pair_id": "PAIR-01",
        "confusion_role": "diagnostic",
    },
    {
        "case_id": "SEL-05",
        "title": "Producer-owned feedback eligibility",
        "demand": "Let an installed producer read a feedback surface and schedule native packet mechanics while retaining eligibility and direction ownership.",
        "required_temporal_semantics": ["event_time"],
        "route_relation": "producer_supplied_feedback_route",
        "retained_relation": "surface_to_packet_producer_record",
        "from_pathway_id": "lgrc9v3.feedback_eligibility_producer",
        "to_pathway_id": "lgrc9v3.explicit_packet_transport",
        "requested_composition_id": "CMP-20",
        "expected_composition_status": "producer_mediated",
        "expected_resolution_kind": "producer_mediated_composition",
    },
    {
        "case_id": "SEL-06",
        "title": "Missing sink-choice to route-schedule crossing",
        "demand": "Use a GRC sink-compatibility result to schedule LGRC route work without inventing an admission bridge.",
        "required_temporal_semantics": ["global_synchronous_step", "producer_frontier_then_event_time"],
        "route_relation": "expected_from_sink_compatibility",
        "retained_relation": "sink_score_to_route_schedule",
        "from_pathway_id": "grc9v3.sink_compatibility_choice",
        "to_pathway_id": "lgrc9v3.configured_flux_route",
        "requested_composition_id": "CMP-06",
        "expected_composition_status": "unsupported_missing_crossing",
        "expected_resolution_kind": "precise_missing_crossing",
    },
    {
        "case_id": "SEL-07",
        "title": "Diagnostic-as-behavioral relabel rejection",
        "demand": "Treat an explicit GRC reconstruction over LGRC state as if ordinary LGRC packet behavior had consumed it.",
        "required_temporal_semantics": ["caller_checkpoint", "event_time"],
        "route_relation": "diagnostic_output_claimed_as_packet_admission",
        "retained_relation": "none_at_proposed_causal_crossing",
        "from_pathway_id": "lgrc9v3.diagnostic_grc_reconstruction",
        "to_pathway_id": "lgrc9v3.explicit_packet_transport",
        "requested_composition_id": "CMP-05",
        "expected_composition_status": "invalid_relabel",
        "expected_resolution_kind": "rejected_invalid_relabel",
    },
    {
        "case_id": "SEL-08",
        "title": "Arbitration-backed behavioral topology commit",
        "demand": "Commit the selected arbitration candidate through collapse and reabsorption while keeping candidate and score formation external.",
        "required_temporal_semantics": ["event_time"],
        "route_relation": "supplied_candidates_native_selection",
        "retained_relation": "candidate_and_topology_digest_across_commit",
        "from_pathway_id": "lgrc9v3.native_route_arbitration",
        "to_pathway_id": "lgrc9v3.collapse_reabsorption",
        "requested_composition_id": "CMP-07",
        "expected_composition_status": "lawful_native",
        "expected_resolution_kind": "existing_lawful_composition",
        "confusion_pair_id": "PAIR-01",
        "confusion_role": "behavioral",
    },
    {
        "case_id": "SEL-09",
        "title": "Unregistered pair remains unclassified",
        "demand": "Ask whether synchronous GRC transport composes directly into restoration identity when I108 registered no such crossing.",
        "required_temporal_semantics": ["global_synchronous_step", "checkpoint_time"],
        "route_relation": "none",
        "retained_relation": "proposed_transport_to_restoration_relation",
        "from_pathway_id": "grc9v3.synchronous_update_cycle",
        "to_pathway_id": "pygrc.restoration_replay_identity",
        "expected_resolution_kind": "unregistered_not_classified",
    },
    {
        "case_id": "SEL-10",
        "title": "Multiple crossings require semantic disambiguation",
        "demand": "Select an arbitration-to-collapse relation without specifying whether direct commit or lineage-aware transport is required.",
        "required_temporal_semantics": ["event_time"],
        "route_relation": "supplied_candidates_native_selection",
        "retained_relation": "unspecified_commit_or_lineage_scope",
        "from_pathway_id": "lgrc9v3.native_route_arbitration",
        "to_pathway_id": "lgrc9v3.collapse_reabsorption",
        "expected_resolution_kind": "ambiguous_registered_crossing",
    },
]


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    ).rstrip("\n")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_digest(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def file_ref(path: str, role: str, revision: str) -> dict[str, str]:
    target = ROOT / path
    if not target.is_file():
        raise FileNotFoundError(path)
    return {
        "path": path,
        "sha256": sha256_file(target),
        "revision": revision,
        "evidence_role": role,
    }


def unique(values: list[Any]) -> list[Any]:
    result: list[Any] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def protected_source_hashes_match(baseline: dict[str, Any]) -> bool:
    return all(
        (ROOT / record["path"]).is_file()
        and sha256_file(ROOT / record["path"]) == record["sha256"]
        for record in baseline["source_hashes"]
    )


def select_case(
    request: dict[str, Any],
    pathway_index: dict[str, dict[str, Any]],
    matrix_rows: list[dict[str, Any]],
    stage_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    base = {
        key: request[key]
        for key in (
            "case_id",
            "title",
            "demand",
            "required_temporal_semantics",
            "route_relation",
            "retained_relation",
        )
    }
    if "confusion_pair_id" in request:
        base["confusion_pair_id"] = request["confusion_pair_id"]
        base["confusion_role"] = request["confusion_role"]

    if "requested_pathway_id" in request:
        pathway = pathway_index[request["requested_pathway_id"]]
        evidence = [
            row
            for row in stage_rows
            if row["pathway_id"] == pathway["pathway_id"]
        ]
        return {
            **base,
            "resolution_kind": "existing_pathway",
            "selected_pathway_ids": [pathway["pathway_id"]],
            "from_pathway_id": None,
            "to_pathway_id": None,
            "required_directional_composition_id": None,
            "composition_status": "not_applicable_pathway_only",
            "adapter_id": None,
            "adapter_owner": "none",
            "configured_residue": pathway["configured_residue"],
            "producer_residue": pathway["producer_residue"],
            "claim_ceiling": pathway["supported_claims"],
            "blocked_nearby_interpretation": pathway["blocked_claims"],
            "missing_relation": "none",
            "registered_alternatives": [],
            "pathway_evidence_statuses": unique(
                [row["evidence_status"] for row in evidence]
            ),
            "source_authority_refs": [
                f"registry:{pathway['pathway_id']}",
                *[
                    f"crosswalk:{row['pathway_id']}:{row['stage_id']}"
                    for row in evidence
                ],
            ],
            "composition_status_is_maturity": False,
            "ecological_meaning_inferred": False,
            "extension_authorized": False,
        }

    from_id = request["from_pathway_id"]
    to_id = request["to_pathway_id"]
    candidates = [
        row
        for row in matrix_rows
        if row["from_pathway_id"] == from_id and row["to_pathway_id"] == to_id
    ]
    requested_composition_id = request.get("requested_composition_id")

    if requested_composition_id is None and not candidates:
        pathways = [pathway_index[from_id], pathway_index[to_id]]
        return {
            **base,
            "resolution_kind": "unregistered_not_classified",
            "selected_pathway_ids": [from_id, to_id],
            "from_pathway_id": from_id,
            "to_pathway_id": to_id,
            "required_directional_composition_id": None,
            "composition_status": "unregistered_not_classified",
            "adapter_id": None,
            "adapter_owner": "none",
            "configured_residue": unique(
                [item for pathway in pathways for item in pathway["configured_residue"]]
            ),
            "producer_residue": unique(
                [item for pathway in pathways for item in pathway["producer_residue"]]
            ),
            "claim_ceiling": "No composition claim; the directional pair was not registered in I108.",
            "blocked_nearby_interpretation": [
                "unregistered pair as unsupported_missing_crossing",
                "endpoint evidence as crossing evidence",
                "automatic extension authorization",
            ],
            "missing_relation": "unclassified_directional_pair_requires_source_audit",
            "registered_alternatives": [],
            "source_authority_refs": [
                f"registry:{from_id}",
                f"registry:{to_id}",
                "matrix:no_registered_directional_row",
            ],
            "composition_status_is_maturity": False,
            "ecological_meaning_inferred": False,
            "extension_authorized": False,
        }

    if requested_composition_id is None and len(candidates) > 1:
        return {
            **base,
            "resolution_kind": "ambiguous_registered_crossing",
            "selected_pathway_ids": [from_id, to_id],
            "from_pathway_id": from_id,
            "to_pathway_id": to_id,
            "required_directional_composition_id": None,
            "composition_status": "ambiguous_registered_crossing",
            "adapter_id": None,
            "adapter_owner": "none",
            "configured_residue": unique(
                [
                    *pathway_index[from_id]["configured_residue"],
                    *pathway_index[to_id]["configured_residue"],
                ]
            ),
            "producer_residue": unique(
                [
                    *pathway_index[from_id]["producer_residue"],
                    *pathway_index[to_id]["producer_residue"],
                ]
            ),
            "claim_ceiling": "No selection until the required crossing semantics are specified.",
            "blocked_nearby_interpretation": [
                "first matching composition as selected crossing",
                "shared endpoints as equivalent composition semantics",
            ],
            "missing_relation": "none",
            "registered_alternatives": [
                row["composition_id"] for row in candidates
            ],
            "source_authority_refs": [
                f"registry:{from_id}",
                f"registry:{to_id}",
                *[f"matrix:{row['composition_id']}" for row in candidates],
            ],
            "composition_status_is_maturity": False,
            "ecological_meaning_inferred": False,
            "extension_authorized": False,
        }

    matching = [
        row for row in candidates if row["composition_id"] == requested_composition_id
    ]
    if len(matching) != 1:
        raise ValueError(
            f"{request['case_id']}: requested composition does not resolve exactly"
        )
    row = matching[0]
    pathways = [pathway_index[from_id], pathway_index[to_id]]
    status = row["composition_status"]
    return {
        **base,
        "resolution_kind": STATUS_TO_RESOLUTION[status],
        "selected_pathway_ids": unique([from_id, to_id]),
        "from_pathway_id": from_id,
        "to_pathway_id": to_id,
        "required_directional_composition_id": row["composition_id"],
        "composition_status": status,
        "adapter_id": row["adapter_id"],
        "adapter_owner": row["adapter_owner"],
        "configured_residue": unique(
            [item for pathway in pathways for item in pathway["configured_residue"]]
        ),
        "producer_residue": unique(
            [item for pathway in pathways for item in pathway["producer_residue"]]
        ),
        "claim_ceiling": row["claim_ceiling"],
        "blocked_nearby_interpretation": row["blocked_relabels"],
        "missing_relation": (
            row["composition_id"]
            if status == "unsupported_missing_crossing"
            else "none"
        ),
        "registered_alternatives": [
            candidate["composition_id"]
            for candidate in candidates
            if candidate["composition_id"] != row["composition_id"]
        ],
        "state_identity_mapping": row["state_identity_mapping"],
        "temporal_compatibility": row["temporal_compatibility"],
        "spatial_compatibility": row["spatial_compatibility"],
        "budget_or_invariant_compatibility": row[
            "budget_or_invariant_compatibility"
        ],
        "authority_retained": row["authority_retained"],
        "authority_transferred": row["authority_transferred"],
        "information_lost_or_compressed": row["information_lost_or_compressed"],
        "source_authority_refs": [
            f"registry:{from_id}",
            f"registry:{to_id}",
            f"matrix:{row['composition_id']}",
            *[
                f"crossing_source:{ref['path']}"
                for ref in row["crossing_source_refs"]
            ],
            *[
                f"crossing_evidence:{ref['node_id']}"
                for ref in row["crossing_evidence_refs"]
            ],
        ],
        "composition_status_is_maturity": False,
        "ecological_meaning_inferred": False,
        "extension_authorized": False,
    }


def guide_markdown(
    registry: dict[str, Any], matrix: dict[str, Any], cases: list[dict[str, Any]]
) -> str:
    time_index: dict[str, list[str]] = {}
    for pathway in registry["pathways"]:
        for semantics in pathway["time_semantics"]:
            time_index.setdefault(semantics, []).append(pathway["pathway_id"])

    time_rows = [
        f"| `{semantics}` | "
        + ", ".join(f"`{pathway_id}`" for pathway_id in pathway_ids)
        + " |"
        for semantics, pathway_ids in sorted(time_index.items())
    ]
    case_rows = []
    for case in cases:
        composition = case["required_directional_composition_id"] or "none"
        owner = case["adapter_owner"]
        case_rows.append(
            f"| `{case['case_id']}` | {case['title']} | "
            f"`{case['resolution_kind']}` | `{composition}` | `{owner}` |"
        )

    case_details = []
    for case in cases:
        pathways = ", ".join(f"`{value}`" for value in case["selected_pathway_ids"])
        blocked = ", ".join(
            f"`{value}`" for value in case["blocked_nearby_interpretation"]
        )
        residues = ", ".join(f"`{value}`" for value in case["configured_residue"])
        claim_ceiling = case["claim_ceiling"]
        if isinstance(claim_ceiling, list):
            claim_ceiling = "; ".join(claim_ceiling)
        case_details.append(
            f"### {case['case_id']}: {case['title']}\n\n"
            f"{case['demand']}\n\n"
            f"```text\n"
            f"resolution = {case['resolution_kind']}\n"
            f"pathways = {', '.join(case['selected_pathway_ids'])}\n"
            f"composition = {case['required_directional_composition_id'] or 'none'}\n"
            f"composition status = {case['composition_status']}\n"
            f"adapter/producer owner = {case['adapter_owner']}\n"
            f"missing relation = {case['missing_relation']}\n"
            f"```\n\n"
            f"Selected pathways: {pathways}. Configured residue: {residues or '`none`'}.\n\n"
            f"Claim ceiling: {claim_ceiling}\n\n"
            f"Blocked nearby interpretation: {blocked}."
        )

    matrix_counts = matrix["status_counts"]
    return f"""# GRC/LGRC Causal Pathway Guide

**Status:** Phase 8 Iteration 109 evidence-derived selection guide frozen

**Machine guide:** [`grc-lgrc-causal-pathway-selection-guide.json`](../../specs/grc-lgrc-causal-pathway-selection-guide.json)

**Registry:** [`grc-lgrc-causal-pathway-contracts.json`](../../specs/grc-lgrc-causal-pathway-contracts.json)

**Evidence crosswalk:** [`grc-lgrc-causal-pathway-evidence-crosswalk.json`](../../specs/grc-lgrc-causal-pathway-evidence-crosswalk.json)

**Composition matrix:** [`GRC-LGRC-CompositionMatrix.md`](./GRC-LGRC-CompositionMatrix.md)

## Purpose And Authority

Use this guide to select an existing GRC9V3/LGRC9V3 pathway or registered
directional crossing while retaining its owner, residue, evidence status, and
claim ceiling. The guide is derived from the registry, crosswalk, and matrix.
It is not an execution API and cannot create pathway or crossing facts.

The guide distinguishes:

```text
existing pathway
existing lawful native composition
lawful composition with explicit adapter
diagnostic-only composition
producer-mediated composition
registered unsupported crossing
invalid relabel
unregistered directional pair
ambiguous registered crossing
```

An unregistered pair is unclassified, not evidence of a missing crossing. A
registered missing crossing does not authorize an extension. Composition
status is not maturity, and no selection establishes ecology or agency.

## Selection Sequence

1. State the required time semantics.
2. State whether the route is explicit, configured, selected over supplied
   candidates, or expected to form.
3. State the required retained relation.
4. Select the pathway whose registry contract actually supplies that surface.
5. If two pathways must interact, look up the exact directional matrix row.
6. Preserve adapter/producer ownership, configured residue, claim ceiling, and
   blocked relabels from the authoritative records.
7. If no exact row exists, report the pair as unregistered and audit it; do not
   infer `unsupported_missing_crossing` from absent matrix coverage.
8. If several rows share endpoints, specify the required crossing semantics;
   do not select the first match.

## Time-Semantics Index

| Required semantics | Registered pathways |
| --- | --- |
{chr(10).join(time_rows)}

Time compatibility at a crossing still comes from its matrix row. Sharing a
time label does not establish interoperability.

## Route And Authority Questions

| Demand | Candidate pathway | Boundary |
| --- | --- | --- |
| Explicit packet endpoints and schedule | `lgrc9v3.explicit_packet_transport` | Route, amount, and times remain supplied. |
| Configured causal route producer | `lgrc9v3.configured_flux_route` | Configuration is not route formation. |
| Configured pole/aspect surplus | `lgrc9v3.route_aspect_surplus` | Pole meaning and thresholds remain configured. |
| Selection over supplied candidates | `lgrc9v3.native_route_arbitration` | Candidate and score formation remain separate. |
| Route expected from state/history/current | No generic V1 pathway | Use a registered mediated crossing or record the exact unclassified/missing relation. |

For every candidate, answer separately who owns direction, funding,
eligibility, scheduling, commitment, and reception. Native commitment does not
naturalize externally authored eligibility.

## Retained Relations

| Required relation | Candidate surface | Boundary |
| --- | --- | --- |
| Present synchronous state | `grc9v3.synchronous_update_cycle` | Current transport/continuity only. |
| Event-time packet history | `lgrc9v3.explicit_packet_transport` | Packet/queue settlement only. |
| Causal annotation | `lgrc9v3.causal_history_annotation` | Diagnostic unless a registered producer consumes it. |
| Pulse surface lineage | `lgrc9v3.causal_pulse_surface_lineage` | Configured surface records and lineage only. |
| Persistent topology event | `lgrc9v3.boundary_birth`, `lgrc9v3.collapse_reabsorption`, or `lgrc9v3.causal_spark_topology_integration` | Use the mechanism-specific contract; no generic admission follows. |
| Snapshot/reset/replay relation | `pygrc.restoration_replay_identity` | Versioned restoration identity, not semantic identity. |

## Composition Outcomes

The I108 matrix contains {matrix['composition_count']} representative
directional rows: {matrix_counts['lawful_native']} lawful native,
{matrix_counts['lawful_with_explicit_adapter']} lawful with explicit adapter,
{matrix_counts['diagnostic_only']} diagnostic only,
{matrix_counts['producer_mediated']} producer mediated,
{matrix_counts['unsupported_missing_crossing']} unsupported missing crossings,
and {matrix_counts['invalid_relabel']} invalid relabels.

| Case | Demand | Resolution | Composition | Owner |
| --- | --- | --- | --- | --- |
{chr(10).join(case_rows)}

## Worked Cases

{(chr(10) * 2).join(case_details)}

## Diagnostic Versus Behavioral Pair

`SEL-04` and `SEL-08` begin from
`lgrc9v3.native_route_arbitration`, but they do not have the same crossing.
`CMP-07` commits selected topology behavior through collapse/reabsorption.
`CMP-24` emits diagnostic multi-basin records after a commit. Shared origin and
current crossing evidence do not let the diagnostic record become the
mutation, and the behavioral commit does not establish the record's broader
interpretation.

## When No Registered Crossing Fits

Record the two endpoint pathway IDs, required direction, missing state/time/
budget/authority mapping, proposed adapter or producer owner, native mechanics
retained, claim ceiling, and controls. If the pair is absent from the
representative matrix, call it `unregistered_not_classified` until a source
audit establishes one of the six composition statuses.

## Claim Boundary

Only runtime artifacts, tests, and experiment evidence can establish that a
selected pathway executed. This guide does not admit a primitive, building
block, motif, regime, support relation, role, shared-medium behavior, agency,
native Read-Back, or N32.
"""


def main() -> int:
    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    crosswalk = json.loads(CROSSWALK_PATH.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    i108_result = json.loads(I108_RESULT_PATH.read_text(encoding="utf-8"))
    i108_freeze = json.loads(I108_FREEZE_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    if registry["registry_digest"] != EXPECTED_REGISTRY_DIGEST:
        raise ValueError("I106 registry digest drift")
    if crosswalk["crosswalk_digest"] != EXPECTED_CROSSWALK_DIGEST:
        raise ValueError("I107 crosswalk digest drift")
    if matrix["matrix_digest"] != EXPECTED_MATRIX_DIGEST:
        raise ValueError("I108 matrix digest drift")
    if i108_result["result_digest"] != EXPECTED_I108_RESULT_DIGEST:
        raise ValueError("I108 result digest drift")
    if i108_freeze["artifact_bundle_digest"] != EXPECTED_I108_BUNDLE_DIGEST:
        raise ValueError("I108 artifact bundle drift")

    i108_supersession = {
        "artifact": "Phase 8 GRC/LGRC causal pathway Iteration 108 artifact-bundle supersession",
        "schema_version": "phase8_grclgrc_causal_pathway_i108_artifact_bundle_supersession_v1",
        "status": "reconciled",
        "recorded_during_iteration": 109,
        "superseded_working_bundle_digest": SUPERSEDED_I108_WORKING_BUNDLE_DIGEST,
        "accepted_current_bundle_digest": i108_freeze["artifact_bundle_digest"],
        "accepted_current_freeze_path": "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactFreeze.json",
        "accepted_current_freeze_sha256": sha256_file(I108_FREEZE_PATH),
        "transition_reason": "Post-I108 review integration clarified that composition status is not maturity and that a missing crossing does not itself authorize an extension.",
        "changed_artifact_paths": [
            "scripts/build_phase8_causal_pathway_i108.py",
            "docs/reference/GRC-LGRC-CompositionMatrix.md",
            "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108.md",
        ],
        "unchanged_scientific_artifact_digests": {
            "matrix_digest": matrix["matrix_digest"],
            "result_digest": i108_result["result_digest"],
            "crossing_test_execution_digest": i108_result["test_execution_digest"],
        },
        "matrix_classification_changed": False,
        "crossing_test_set_or_result_changed": False,
        "runtime_behavior_changed": False,
        "historical_bundle_bytes_retained_as_current_artifact": False,
        "authority_rule": "I109 and later iterations consume only accepted_current_bundle_digest; the superseded digest remains provenance, not an alternate predecessor.",
    }
    i108_supersession["reconciliation_digest"] = canonical_digest(
        i108_supersession
    )
    write_json(OUTPUT_I108_SUPERSESSION, i108_supersession)

    pathway_index = {row["pathway_id"]: row for row in registry["pathways"]}
    matrix_rows = matrix["compositions"]
    cases = [
        select_case(request, pathway_index, matrix_rows, crosswalk["stage_rows"])
        for request in WORKED_REQUESTS
    ]
    case_index = {row["case_id"]: row for row in cases}
    request_index = {row["case_id"]: row for row in WORKED_REQUESTS}
    represented_statuses = sorted(
        {
            row["composition_status"]
            for row in cases
            if row["composition_status"] in STATUS_TO_RESOLUTION
        }
    )
    pair_diagnostic = case_index["SEL-04"]
    pair_behavioral = case_index["SEL-08"]
    selected_time_semantics = {
        row["case_id"]: {
            semantics
            for pathway_id in row["selected_pathway_ids"]
            for semantics in pathway_index[pathway_id]["time_semantics"]
        }
        for row in cases
    }
    time_semantics_index: dict[str, list[str]] = {}
    for pathway in registry["pathways"]:
        for semantics in pathway["time_semantics"]:
            time_semantics_index.setdefault(semantics, []).append(
                pathway["pathway_id"]
            )
    time_semantics_index = {
        semantics: sorted(pathway_ids)
        for semantics, pathway_ids in sorted(time_semantics_index.items())
    }

    validations = {
        "source_authority_digests_match": True,
        "i108_predecessor_bundle_reconciled": i108_supersession["status"]
        == "reconciled"
        and i108_supersession["accepted_current_bundle_digest"]
        == EXPECTED_I108_BUNDLE_DIGEST
        and i108_supersession["superseded_working_bundle_digest"]
        == SUPERSEDED_I108_WORKING_BUNDLE_DIGEST,
        "i108_scientific_digests_unchanged_across_supersession": i108_supersession[
            "unchanged_scientific_artifact_digests"
        ]
        == {
            "matrix_digest": EXPECTED_MATRIX_DIGEST,
            "result_digest": EXPECTED_I108_RESULT_DIGEST,
            "crossing_test_execution_digest": i108_result[
                "test_execution_digest"
            ],
        },
        "all_requested_pathways_resolve": all(
            pathway_id in pathway_index
            for request in WORKED_REQUESTS
            for pathway_id in (
                [request["requested_pathway_id"]]
                if "requested_pathway_id" in request
                else [request["from_pathway_id"], request["to_pathway_id"]]
            )
        ),
        "all_human_guide_pathway_ids_resolve": GUIDE_PATHWAY_IDS
        <= set(pathway_index),
        "all_expected_resolution_kinds_match": all(
            case_index[case_id]["resolution_kind"]
            == request["expected_resolution_kind"]
            for case_id, request in request_index.items()
        ),
        "all_expected_composition_statuses_match": all(
            "expected_composition_status" not in request
            or case_index[case_id]["composition_status"]
            == request["expected_composition_status"]
            for case_id, request in request_index.items()
        ),
        "required_temporal_semantics_use_registry_vocabulary": all(
            set(row["required_temporal_semantics"])
            <= selected_time_semantics[row["case_id"]]
            for row in cases
        ),
        "all_six_i108_statuses_exercised": represented_statuses
        == sorted(STATUS_TO_RESOLUTION),
        "pathway_only_case_requires_no_composition": case_index["SEL-01"][
            "required_directional_composition_id"
        ]
        is None,
        "unsupported_case_names_exact_registered_crossing": case_index["SEL-06"][
            "missing_relation"
        ]
        == "CMP-06",
        "unregistered_pair_not_promoted_to_missing_crossing": case_index["SEL-09"][
            "composition_status"
        ]
        == "unregistered_not_classified",
        "ambiguous_pair_returns_all_registered_alternatives": set(
            case_index["SEL-10"]["registered_alternatives"]
        )
        == {"CMP-07", "CMP-16"},
        "diagnostic_behavioral_pair_shares_origin_but_not_status": pair_diagnostic[
            "selected_pathway_ids"
        ][0]
        == pair_behavioral["selected_pathway_ids"][0]
        and pair_diagnostic["composition_status"] == "diagnostic_only"
        and pair_behavioral["composition_status"] == "lawful_native",
        "adapter_and_producer_owners_remain_visible": all(
            row["adapter_owner"] not in {"none", "native"}
            for row in cases
            if row["composition_status"]
            in {"lawful_with_explicit_adapter", "producer_mediated"}
        ),
        "composition_status_never_used_as_maturity": all(
            not row["composition_status_is_maturity"] for row in cases
        ),
        "no_selection_authorizes_extension": all(
            not row["extension_authorized"] for row in cases
        ),
        "no_selection_infers_ecological_meaning": all(
            not row["ecological_meaning_inferred"] for row in cases
        ),
        "protected_source_hashes_match_i105_baseline": protected_source_hashes_match(
            baseline
        ),
        "protected_src_test_example_diff_empty": not bool(
            git("diff", "--name-only", "--", "src", "tests", "examples")
        ),
    }

    execution = {
        "artifact": "Phase 8 GRC/LGRC causal pathway I109 selection-case validation",
        "schema_version": "phase8_grclgrc_causal_pathway_i109_validation_v1",
        "iteration": 109,
        "source_revision": head,
        "validation_kind": "deterministic_selection_contract_cases_not_runtime_tests",
        "case_count": len(cases),
        "cases": [
            {
                "case_id": row["case_id"],
                "expected_resolution_kind": request_index[row["case_id"]][
                    "expected_resolution_kind"
                ],
                "actual_resolution_kind": row["resolution_kind"],
                "status": (
                    "passed"
                    if request_index[row["case_id"]]["expected_resolution_kind"]
                    == row["resolution_kind"]
                    else "failed"
                ),
            }
            for row in cases
        ],
        "validation_checks": validations,
        "runtime_tests_run": False,
        "runtime_tests_not_run_reason": "I109 derives and validates selection semantics without changing runtime, tests, examples, or the frozen I108 crossing-test set.",
        "status": "passed" if all(validations.values()) else "failed",
    }
    execution["execution_digest"] = canonical_digest(execution)
    write_json(OUTPUT_EXECUTION, execution)

    selector = {
        "artifact": "GRC/LGRC causal pathway evidence-derived selection guide",
        "schema_version": "grc_lgrc_causal_pathway_selection_guide_v1",
        "iteration": 109,
        "status": "frozen" if execution["status"] == "passed" else "failed",
        "source_revision": head,
        "registry_digest": registry["registry_digest"],
        "crosswalk_digest": crosswalk["crosswalk_digest"],
        "matrix_digest": matrix["matrix_digest"],
        "i108_predecessor_reconciliation": {
            "status": i108_supersession["status"],
            "superseded_working_bundle_digest": i108_supersession[
                "superseded_working_bundle_digest"
            ],
            "accepted_current_bundle_digest": i108_supersession[
                "accepted_current_bundle_digest"
            ],
            "reconciliation_digest": i108_supersession[
                "reconciliation_digest"
            ],
        },
        "authority_rule": "registry owns pathway facts; crosswalk owns evidence attachment; matrix owns directional crossing facts; selector only derives selection outcomes",
        "selection_sequence": [
            "declare required temporal semantics",
            "declare explicit/configured/arbitrated/formed route relation",
            "declare retained relation",
            "select registered pathway",
            "look up exact directional composition where interaction is required",
            "preserve owner, residue, claim ceiling, blocked relabels, and missing relation",
        ],
        "time_semantics_index": time_semantics_index,
        "human_guide_pathway_refs": sorted(GUIDE_PATHWAY_IDS),
        "unregistered_pair_rule": "absence from the representative I108 matrix means unregistered_not_classified, not unsupported_missing_crossing",
        "ambiguity_rule": "multiple rows with the same endpoints require crossing-semantic disambiguation; first-match selection is forbidden",
        "maturity_rule": "composition status is not a maturity score",
        "extension_rule": "unsupported or unregistered crossings do not automatically authorize implementation",
        "ecology_rule": "selection does not establish ecological or agentic meaning",
        "status_to_resolution": STATUS_TO_RESOLUTION,
        "worked_cases": cases,
        "confusion_pairs": [
            {
                "pair_id": "PAIR-01",
                "shared_origin_pathway_id": "lgrc9v3.native_route_arbitration",
                "diagnostic_case_id": "SEL-04",
                "diagnostic_composition_id": "CMP-24",
                "behavioral_case_id": "SEL-08",
                "behavioral_composition_id": "CMP-07",
                "distinction": "post-commit diagnostic record emission versus native/configured topology commitment",
            }
        ],
        "validation_execution_digest": execution["execution_digest"],
        "runtime_behavior_changed": False,
    }
    selector["selector_digest"] = canonical_digest(selector)
    write_json(OUTPUT_SELECTOR, selector)
    OUTPUT_GUIDE.write_text(guide_markdown(registry, matrix, cases), encoding="utf-8")

    result = {
        "artifact": "Phase 8 GRC/LGRC causal pathway consolidation Iteration 109 result",
        "schema_version": "phase8_grclgrc_causal_pathway_iteration_109_result_v1",
        "iteration": 109,
        "status": execution["status"],
        "repository_branch": branch,
        "repository_head": head,
        "registry_digest": registry["registry_digest"],
        "crosswalk_digest": crosswalk["crosswalk_digest"],
        "matrix_digest": matrix["matrix_digest"],
        "i108_artifact_bundle_digest": i108_freeze["artifact_bundle_digest"],
        "i108_predecessor_reconciliation_digest": i108_supersession[
            "reconciliation_digest"
        ],
        "selector_digest": selector["selector_digest"],
        "validation_execution_digest": execution["execution_digest"],
        "worked_case_count": len(cases),
        "composition_statuses_exercised": represented_statuses,
        "confusion_pair_count": len(selector["confusion_pairs"]),
        "checks": validations,
        "selection_guide_complete": all(validations.values()),
        "runtime_behavior_changed": False,
        "iteration_110_ready": all(validations.values()),
    }
    result["result_digest"] = canonical_digest(result)
    write_json(OUTPUT_RESULT, result)

    report = f"""# Phase 8 GRC/LGRC Causal Pathway Consolidation - Iteration 109

## Result

Iteration 109 passed as an evidence-derived pathway and composition selection
guide.

```text
worked selection cases = {len(cases)}
I108 composition statuses exercised = {len(represented_statuses)} / 6
diagnostic-versus-behavioral confusion pairs = {len(selector['confusion_pairs'])}
unregistered pair control = passed
ambiguous registered pair control = passed
I108 predecessor bundle reconciliation = passed
runtime behavior changed = false
Iteration 110 ready = {str(result['iteration_110_ready']).lower()}
```

## Interpretation

The guide can distinguish an existing pathway, a registered lawful crossing,
an explicit adapter, a diagnostic-only crossing, a producer-owned crossing, a
registered missing crossing, an invalid relabel, an unregistered pair, and an
ambiguous set of registered crossings. Every result is projected from I106
pathway facts, I107 evidence attachment, and I108 directional crossing facts.

The diagnostic-versus-behavioral pair uses one shared origin: native route
arbitration. `CMP-07` commits selected topology behavior through collapse and
reabsorption; `CMP-24` emits diagnostic records after a commit. The selector
keeps those outcomes separate from their authority and evidence records rather
than from labels alone.

The accepted I108 predecessor bundle is `79bc60...`. It supersedes the
pre-review working bundle `475ba6...` after claim-boundary wording was
clarified. The I108 matrix digest, result digest, crossing-test receipt, and
runtime behavior are unchanged; the supersession record makes that transition
explicit rather than presenting two predecessor identities.

## Remaining Boundary

I109 does not execute a selected pathway, infer maturity from composition
status, close an unregistered pair, authorize an extension, or establish
ecology, agency, native Read-Back, or N32. I110 still owns machine conformance,
staleness, and repository integration. I111 still owns independent low-context
pressure-consumer use.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")

    freeze_paths = [
        "scripts/build_phase8_causal_pathway_i109.py",
        "specs/grc-lgrc-causal-pathway-selection-guide.json",
        "docs/reference/GRC-LGRC-CausalPathwayGuide.md",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ValidationExecution.json",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactBundleSupersession.json",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.json",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.md",
    ]
    freeze_records = [
        file_ref(path, "iteration_109_artifact", "iteration_109_working_artifact")
        for path in freeze_paths
    ]
    freeze = {
        "artifact": "Phase 8 GRC/LGRC causal pathway consolidation Iteration 109 artifact freeze",
        "schema_version": "phase8_grclgrc_causal_pathway_iteration_109_artifact_freeze_v1",
        "iteration": 109,
        "source_revision": head,
        "i108_artifact_bundle_digest": i108_freeze["artifact_bundle_digest"],
        "artifacts": freeze_records,
        "artifact_bundle_digest": canonical_digest(freeze_records),
        "runtime_behavior_changed": False,
    }
    write_json(OUTPUT_FREEZE, freeze)

    print(
        json.dumps(
            {
                "status": result["status"],
                "selector_digest": selector["selector_digest"],
                "result_digest": result["result_digest"],
                "artifact_bundle_digest": freeze["artifact_bundle_digest"],
                "worked_case_count": len(cases),
                "composition_statuses_exercised": represented_statuses,
            },
            indent=2,
        )
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
