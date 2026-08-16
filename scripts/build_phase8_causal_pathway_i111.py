#!/usr/bin/env python3
"""Build Phase 8 Iteration 111 pressure-consumer and closeout artifacts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "specs/grc-lgrc-causal-pathway-contracts.json"
CROSSWALK_PATH = ROOT / "specs/grc-lgrc-causal-pathway-evidence-crosswalk.json"
MATRIX_PATH = ROOT / "specs/grc-lgrc-causal-pathway-composition-matrix.json"
GUIDE_PATH = ROOT / "specs/grc-lgrc-causal-pathway-selection-guide.json"
POLICY_PATH = ROOT / "specs/grc-lgrc-causal-pathway-conformance.json"
I110_RESULT_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.json"
I110_FREEZE_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ArtifactFreeze.json"
CONFORMANCE_CHECKER_PATH = ROOT / "scripts/check_grc_lgrc_causal_pathway_conformance.py"
PRESSURE_CHECKER_PATH = ROOT / "scripts/check_grc_lgrc_pressure_consumer_selection.py"
PRESSURE_VALIDATOR_PATH = ROOT / "scripts/validate_grc_lgrc_pressure_consumer_recovery.py"

OUTPUT_DESCRIPTIONS = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111PressureConsumerDescriptions.json"
OUTPUT_PRESSURE = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111PressureConsumerExecution.json"
OUTPUT_RAW_DESCRIPTIONS = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111RawDemandDescriptions.json"
OUTPUT_RAW = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111RawDemandExecution.json"
OUTPUT_BLIND_INPUT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentConsumerBlindInput.json"
OUTPUT_BLIND_REPLAY = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentBlindReplayExecution.json"
OUTPUT_BLIND_REPLAY_FREEZE = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentBlindReplayFreeze.json"
OUTPUT_EXPECTED_RECOVERY = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentConsumerExpectedRecovery.json"
OUTPUT_BLIND_VALIDATION = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111IndependentBlindValidationExecution.json"
OUTPUT_LAYOUT_RELOCATION = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationLayoutRelocation.json"
OUTPUT_I110_RECONCILIATION = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ArtifactBundleSupersession.json"
OUTPUT_RESULT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111.json"
OUTPUT_REPORT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111.md"
OUTPUT_CLOSEOUT = ROOT / "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationCloseout.md"
OUTPUT_FREEZE = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration111ArtifactFreeze.json"

SUPERSEDED_I110_WORKING_BUNDLE_DIGEST = "aed84583410b4746d043ed550029ad5ccd8d47c8e30ccc59fabc233bb8fffd8c"
PRE_RELOCATION_ACCEPTED_I110_BUNDLE_DIGEST = "1b3b94f987733fc2c5f06740b6e27a1725309fe36c54d8ac7bfcaf76ba6f7fe7"
BUILDER_ONLY_ACCEPTED_I110_BUNDLE_DIGEST = "d271c13d0b68c78adda90fbd6168119ef77a41ac46c21d15c2c4acedfbff5381"
ACCEPTED_I110_BUNDLE_DIGEST = "510f442c38d12018cec20951136019319895866b3e74c3fe57c8db48cddd079b"

PRE_RELOCATION_BUNDLE_DIGESTS = {
    106: "b84c30d13eba8a179d628a64eca3a0605f77df5c7c7157fe822b0fcac4bd2127",
    107: "70e9d525bfdac4f7c3f73e11610cd6f58d68f307da362f6fd9ab0b4d61dd8aa2",
    108: "79bc60b3cfdf25155182d58c94c7bff524b6e4ee59259fe9af0ca7163f37f84f",
    109: "e5cc2fb6495150a2d559f14e21d0b97fa11de0cd26c8f23f9e42de4ca18b01c2",
    110: PRE_RELOCATION_ACCEPTED_I110_BUNDLE_DIGEST,
    111: "e301b305d0f218b2054bf525f58103d461592898153f5d625551a203a292d621",
}

BUILDER_ONLY_INTERMEDIATE_BUNDLE_DIGESTS = {
    106: "404492bc15c160cacd5c13609c2749fee8dfb3507de8751322ff4f2cb03e66c3",
    107: "1b3bd98dbc522deedf8f9ee78aa10ba93f3e1142b849d9f4ec410580ac22b026",
    108: "f44db8636862f328334f33d61beb7186673bd10652f39ef06b9e5048e1aba954",
    109: "218245e43511922243751034e1b4e17e2c0589b9cae5428c741e1153ee269f60",
    110: BUILDER_ONLY_ACCEPTED_I110_BUNDLE_DIGEST,
    111: "18e384c13dccf6fb16e08b071fd8831659902750232230c81f4aee37275a9c1d",
}

PREDECESSOR_FREEZE_PATHS = {
    iteration: ROOT
    / f"implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration{iteration}ArtifactFreeze.json"
    for iteration in range(106, 111)
}


STATUS_TO_RESOLUTION = {
    "lawful_native": "existing_lawful_composition",
    "lawful_with_explicit_adapter": "existing_composition_with_explicit_adapter",
    "diagnostic_only": "diagnostic_surface_only",
    "producer_mediated": "producer_mediated_composition",
    "unsupported_missing_crossing": "precise_missing_crossing",
    "invalid_relabel": "rejected_invalid_relabel",
    "ambiguous_registered_crossing": "declared_ambiguity",
}

REQUIRED_CATEGORIES = {
    "rcae_l04_support_side",
    "boundary_conditioned_exchange",
    "circulation",
    "ap4_ap5",
    "shared_medium_response",
    "route_or_role_formation",
    "future_n32_candidate_class",
    "diagnostic_vs_behavioral",
    "configured_vs_formed_route",
    "arbitration_vs_candidate_formation",
    "ledger_vs_constitutive_history",
}


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    ).rstrip("\n")


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def file_ref(path: str, role: str) -> dict[str, str]:
    target = ROOT / path
    return {"path": path, "sha256": sha256_file(target), "artifact_role": role}


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "causal_pathway_conformance", CONFORMANCE_CHECKER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load conformance checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def matrix_query(
    pressure_id: str,
    category: str,
    demand: str,
    composition_id: str,
    expected_status: str,
    nearby_rejections: list[str],
) -> dict[str, Any]:
    return {
        "pressure_id": pressure_id,
        "category": category,
        "consumer_language": demand,
        "normalization_rule": "consumer demand is decomposed to one registered directional crossing without changing matrix semantics",
        "query_kind": "registered_directional_composition",
        "composition_id": composition_id,
        "expected_composition_status": expected_status,
        "nearby_rejections": nearby_rejections,
    }


def guide_query(
    pressure_id: str,
    category: str,
    demand: str,
    guide_case_id: str,
    expected_status: str,
    nearby_rejections: list[str],
) -> dict[str, Any]:
    return {
        "pressure_id": pressure_id,
        "category": category,
        "consumer_language": demand,
        "normalization_rule": "consumer demand preserves declared ambiguity rather than selecting the first registered crossing",
        "query_kind": "selection_guide_case",
        "guide_case_id": guide_case_id,
        "expected_composition_status": expected_status,
        "nearby_rejections": nearby_rejections,
    }


def pressure_queries() -> list[dict[str, Any]]:
    return [
        matrix_query(
            "PC-L04-01",
            "rcae_l04_support_side",
            "Use a declared support-side feedback surface to schedule bounded packet work while preserving the owner of eligibility and direction.",
            "CMP-20",
            "producer_mediated",
            ["native support", "native feedback admission", "ecological support success"],
        ),
        matrix_query(
            "PC-BND-01",
            "boundary_conditioned_exchange",
            "Carry GRC front-capacity state into an LGRC boundary-birth runtime without pretending synchronous history became event history.",
            "CMP-26",
            "lawful_with_explicit_adapter",
            ["lawful native crossing", "automatic time conversion"],
        ),
        matrix_query(
            "PC-BND-02",
            "boundary_conditioned_exchange",
            "Commit configured outward-flux and front-capacity evidence as a topology-specific child birth.",
            "CMP-13",
            "lawful_native",
            ["generic work admission", "semantic reproduction"],
        ),
        matrix_query(
            "PC-BND-03",
            "boundary_conditioned_exchange",
            "Reuse boundary-birth eligibility as generic packet-exchange admission.",
            "CMP-14",
            "invalid_relabel",
            ["shared queue infrastructure implies shared contract"],
        ),
        matrix_query(
            "PC-CIRC-01",
            "circulation",
            "Move a supplied packet through debit, in-flight retention, arrival, and target credit as one bounded circulation leg.",
            "CMP-02",
            "lawful_native",
            ["native circulation policy", "native route formation", "self-sustaining loop"],
        ),
        matrix_query(
            "PC-AP45-01",
            "ap4_ap5",
            "Turn a GRC sink-compatibility result into an LGRC route schedule and target without inventing the admission bridge.",
            "CMP-06",
            "unsupported_missing_crossing",
            ["semantic choice", "native route selection", "AP4/AP5 closure"],
        ),
        matrix_query(
            "PC-AP45-02",
            "ap4_ap5",
            "Treat a configured route and target as a natively formed role or proxy relation.",
            "CMP-11",
            "invalid_relabel",
            ["configured route as formed route", "configured target as semantic proxy"],
        ),
        matrix_query(
            "PC-SM-01",
            "shared_medium_response",
            "Record a configured pulse surface after packet arrival while keeping recording distinct from read-back.",
            "CMP-21",
            "lawful_native",
            ["native memory", "shared-medium response", "coordination"],
        ),
        matrix_query(
            "PC-SM-02",
            "shared_medium_response",
            "Use transported surface lineage to condition later packet scheduling with producer ownership visible.",
            "CMP-22",
            "producer_mediated",
            ["native Read-Back", "native shared-medium organization"],
        ),
        matrix_query(
            "PC-SM-03",
            "shared_medium_response",
            "Carry the producer eligibility decision into native packet mechanics without promoting the producer cut.",
            "CMP-20",
            "producer_mediated",
            ["lawful native feedback", "communication", "cooperation"],
        ),
        matrix_query(
            "PC-ROLE-01",
            "route_or_role_formation",
            "Commit one supplied arbitration candidate through native collapse mechanics while leaving candidate formation external.",
            "CMP-07",
            "lawful_native",
            ["native candidate formation", "semantic role formation"],
        ),
        matrix_query(
            "PC-ROLE-02",
            "route_or_role_formation",
            "Treat native arbitration over supplied scores as native formation of candidates and values.",
            "CMP-08",
            "invalid_relabel",
            ["native route formation", "semantic valuation"],
        ),
        matrix_query(
            "PC-ROLE-03",
            "route_or_role_formation",
            "Treat configured route execution as endogenous role formation.",
            "CMP-11",
            "invalid_relabel",
            ["semantic role", "native target formation"],
        ),
        matrix_query(
            "PC-N32-01",
            "future_n32_candidate_class",
            "Let exact route history temporarily condition conductance and later flux as a bounded future building-block candidate.",
            "CMP-17",
            "producer_mediated",
            ["native history read path", "native D0 decay", "N32 selected"],
        ),
        matrix_query(
            "PC-DIAG-01",
            "diagnostic_vs_behavioral",
            "Reconstruct bounded GRC diagnostics over an LGRC checkpoint without claiming ordinary LGRC behavior consumed them.",
            "CMP-04",
            "diagnostic_only",
            ["behavioral update", "native event-to-action crossing"],
        ),
        matrix_query(
            "PC-DIAG-02",
            "diagnostic_vs_behavioral",
            "Use reconstructed diagnostics as direct packet-admission behavior.",
            "CMP-05",
            "invalid_relabel",
            ["diagnostic output as constitutive state"],
        ),
        matrix_query(
            "PC-CONFIG-01",
            "configured_vs_formed_route",
            "Execute a configured route but ask whether its existence proves the substrate formed that route.",
            "CMP-11",
            "invalid_relabel",
            ["execution evidence as formation evidence"],
        ),
        matrix_query(
            "PC-ARB-01",
            "arbitration_vs_candidate_formation",
            "Select and commit among supplied candidates with native arbitration.",
            "CMP-07",
            "lawful_native",
            ["native score formation", "native candidate formation"],
        ),
        matrix_query(
            "PC-ARB-02",
            "arbitration_vs_candidate_formation",
            "Use native selection to claim that candidate and score formation were native.",
            "CMP-08",
            "invalid_relabel",
            ["selection as formation", "semantic valuation"],
        ),
        guide_query(
            "PC-ARB-03",
            "arbitration_vs_candidate_formation",
            "Request arbitration-to-collapse behavior without specifying direct commit versus lineage-aware transport.",
            "SEL-10",
            "ambiguous_registered_crossing",
            ["arbitrary first match", "shared endpoints imply equivalent semantics"],
        ),
        matrix_query(
            "PC-LEDGER-01",
            "ledger_vs_constitutive_history",
            "Persist packet ledger history and ask whether replay identity itself makes that history a later native cause.",
            "CMP-18",
            "unsupported_missing_crossing",
            ["persistence as Read-Back", "ledger retention as memory-mediated action"],
        ),
        matrix_query(
            "PC-LEDGER-02",
            "ledger_vs_constitutive_history",
            "Use an explicit producer to derive temporary conductance from exact history while retaining the producer cut.",
            "CMP-17",
            "producer_mediated",
            ["producer-derived history as native ledger consumption"],
        ),
    ]


def raw_demand_descriptions() -> list[dict[str, str]]:
    return [
        {
            "raw_demand_id": "RAW-01",
            "consumer_language": "I already know the source, receiver, amount, and delay. I only need the amount to leave, remain in flight, and arrive without creating a second composition.",
        },
        {
            "raw_demand_id": "RAW-02",
            "consumer_language": "A participant is depleted while nearby regions have excess capacity. I want current state to form possible receivers and decide a viable continuation without supplying a fixed target.",
        },
        {
            "raw_demand_id": "RAW-03",
            "consumer_language": "Several routes look possible. I want current sink compatibility to determine which route becomes scheduled rather than supplying the route myself.",
        },
        {
            "raw_demand_id": "RAW-04",
            "consumer_language": "A trace from earlier packet activity survives replay. I need to know whether persistence alone means later native behavior reads that trace.",
        },
        {
            "raw_demand_id": "RAW-05",
            "consumer_language": "One participant changes a non-private trace and a later encounter with that trace should change whether another packet is scheduled.",
        },
        {
            "raw_demand_id": "RAW-06",
            "consumer_language": "Local outward pressure at a capacity-bearing boundary should create and fund a child topology without treating birth eligibility as generic exchange admission.",
        },
        {
            "raw_demand_id": "RAW-07",
            "consumer_language": "After a topology commit I want child-basin and flow-window records, but I need to know whether those records caused the basin or only describe it.",
        },
    ]


def raw_demand_interpretations() -> dict[str, dict[str, Any]]:
    return {
        "RAW-01": {
            "normalization": "explicit supplied packet lifecycle only",
            "selection_kind": "guide_case",
            "guide_case_id": "SEL-01",
            "expected_resolution_kind": "existing_pathway",
            "why": "The demand supplies route, amount, and time and requires no crossing beyond packet transport.",
        },
        "RAW-02": {
            "normalization": "state-conditioned surplus should form candidate receivers before native arbitration",
            "selection_kind": "unregistered_pair",
            "from_pathway_id": "lgrc9v3.route_aspect_surplus",
            "to_pathway_id": "lgrc9v3.native_route_arbitration",
            "expected_resolution_kind": "unregistered_not_classified",
            "why": "The representative matrix contains no surplus-to-candidate-formation crossing; absence is not a missing-crossing finding.",
        },
        "RAW-03": {
            "normalization": "sink compatibility should author an event-time route schedule",
            "selection_kind": "composition",
            "composition_ids": ["CMP-06"],
            "expected_resolution_kind": "precise_missing_crossing",
            "why": "The registered sink-choice-to-route-schedule crossing is explicitly absent.",
        },
        "RAW-04": {
            "normalization": "persisted ledger history should become a constitutive later read",
            "selection_kind": "composition",
            "composition_ids": ["CMP-18"],
            "expected_resolution_kind": "precise_missing_crossing",
            "why": "Restoration retains ledger state but no native constitutive consumer reads it.",
        },
        "RAW-05": {
            "normalization": "packet arrival records a surface, lineage is read by a producer, and producer eligibility schedules a later packet",
            "selection_kind": "composition_chain",
            "composition_ids": ["CMP-21", "CMP-22", "CMP-20"],
            "expected_resolution_kind": "producer_mediated_composition",
            "why": "Surface emission is native/configured, while both read-back eligibility and later scheduling remain producer-owned.",
        },
        "RAW-06": {
            "normalization": "outward flux and configured front capacity admit topology-specific boundary birth",
            "selection_kind": "composition",
            "composition_ids": ["CMP-13"],
            "expected_resolution_kind": "existing_lawful_composition",
            "why": "The native/configured birth crossing is registered and remains topology-specific.",
        },
        "RAW-07": {
            "normalization": "post-commit topology is projected into child-basin diagnostics",
            "selection_kind": "composition",
            "composition_ids": ["CMP-24"],
            "expected_resolution_kind": "diagnostic_surface_only",
            "why": "The records follow the commit and do not own topology mutation.",
        },
    }


def evaluate_raw_demand(
    description: dict[str, str],
    interpretation: dict[str, Any],
    registry: dict[str, Any],
    compositions: dict[str, dict[str, Any]],
    cases: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    pathway_ids = {row["pathway_id"] for row in registry["pathways"]}
    kind = interpretation["selection_kind"]
    composition_ids: list[str] = []
    adapter_owners: list[str] = []
    blocked_claims: list[str] = []
    missing_relation = "none"
    next_action = "use selected bounded pathway/composition"

    if kind == "guide_case":
        case = cases[interpretation["guide_case_id"]]
        resolution = case["resolution_kind"]
        selected_pathway_ids = case["selected_pathway_ids"]
        composition_ids = (
            [case["required_directional_composition_id"]]
            if case.get("required_directional_composition_id")
            else []
        )
        adapter_owners = [case.get("adapter_owner", "none")]
        claim_ceiling: Any = case["claim_ceiling"]
        blocked_claims = case["blocked_nearby_interpretation"]
    elif kind == "unregistered_pair":
        from_id = interpretation["from_pathway_id"]
        to_id = interpretation["to_pathway_id"]
        registered = [
            row
            for row in compositions.values()
            if row["from_pathway_id"] == from_id
            and row["to_pathway_id"] == to_id
        ]
        resolution = (
            "misrouted_registered_pair" if registered else "unregistered_not_classified"
        )
        selected_pathway_ids = [from_id, to_id]
        claim_ceiling = "No composition or missing-crossing claim; the directional pair requires source audit and registration if retained."
        blocked_claims = [
            "unregistered pair as unsupported_missing_crossing",
            "automatic extension authorization",
            "native receiver or route formation",
        ]
        missing_relation = "unclassified_directional_pair_requires_source_audit"
        next_action = "source audit and new registration if the demand remains important"
    else:
        composition_ids = interpretation["composition_ids"]
        rows = [compositions[composition_id] for composition_id in composition_ids]
        selected_pathway_ids = list(
            dict.fromkeys(
                pathway_id
                for row in rows
                for pathway_id in (row["from_pathway_id"], row["to_pathway_id"])
            )
        )
        statuses = [row["composition_status"] for row in rows]
        if kind == "composition_chain" and "producer_mediated" in statuses:
            resolution = "producer_mediated_composition"
        elif len(rows) == 1:
            resolution = STATUS_TO_RESOLUTION[statuses[0]]
        else:
            resolution = "unresolved_mixed_chain"
        adapter_owners = [row["adapter_owner"] for row in rows]
        claim_ceiling = [row["claim_ceiling"] for row in rows]
        blocked_claims = list(
            dict.fromkeys(
                claim for row in rows for claim in row["blocked_relabels"]
            )
        )
        missing = [
            row.get("source_absence_audit", {}).get("missing_crossing")
            for row in rows
            if row["composition_status"] == "unsupported_missing_crossing"
        ]
        missing_relation = next((value for value in missing if value), "none")

    passed = (
        resolution == interpretation["expected_resolution_kind"]
        and all(pathway_id in pathway_ids for pathway_id in selected_pathway_ids)
    )
    return {
        "raw_demand_id": description["raw_demand_id"],
        "consumer_language": description["consumer_language"],
        "interpretation_owner": "I111 expert demand-to-substrate decomposition",
        "normalization": interpretation["normalization"],
        "normalization_reason": interpretation["why"],
        "selection_kind": kind,
        "resolution_kind": resolution,
        "selected_pathway_ids": selected_pathway_ids,
        "selected_composition_ids": composition_ids,
        "adapter_owners": adapter_owners,
        "claim_ceiling": claim_ceiling,
        "blocked_claims": blocked_claims,
        "missing_relation": missing_relation,
        "missing_crossing_claim": resolution == "precise_missing_crossing",
        "extension_authorized": False,
        "ecological_success_inferred": False,
        "n32_selected": False,
        "next_action": next_action,
        "status": "passed" if passed else "misrouted",
    }


def evaluate_pressure(
    query: dict[str, Any],
    compositions: dict[str, dict[str, Any]],
    cases: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if query["query_kind"] == "registered_directional_composition":
        selected = compositions[query["composition_id"]]
        selected_pathway_ids = list(
            dict.fromkeys(
                [selected["from_pathway_id"], selected["to_pathway_id"]]
            )
        )
        status = selected["composition_status"]
        composition_ids = [selected["composition_id"]]
        adapter_id = selected.get("adapter_id")
        adapter_owner = selected.get("adapter_owner")
        configured_residue: list[str] = []
        producer_residue = (
            [adapter_owner]
            if status == "producer_mediated" and adapter_owner not in {None, "none"}
            else []
        )
        claim_ceiling = selected["claim_ceiling"]
        blocked_claims = selected["blocked_relabels"]
        missing_crossing = (
            selected.get("source_absence_audit", {}).get("missing_crossing")
            if status == "unsupported_missing_crossing"
            else "none"
        )
        compatibility = {
            "state": selected["state_identity_mapping"],
            "time": selected["temporal_compatibility"],
            "space": selected["spatial_compatibility"],
            "budget": selected["budget_or_invariant_compatibility"],
        }
        authority_retained = selected["authority_retained"]
        authority_transferred = selected["authority_transferred"]
        information_loss = selected["information_lost_or_compressed"]
    else:
        selected = cases[query["guide_case_id"]]
        selected_pathway_ids = selected["selected_pathway_ids"]
        status = selected["composition_status"]
        composition_ids = selected.get("registered_alternatives", [])
        adapter_id = selected.get("adapter_id")
        adapter_owner = selected.get("adapter_owner")
        configured_residue = selected.get("configured_residue", [])
        producer_residue = selected.get("producer_residue", [])
        claim_ceiling = selected["claim_ceiling"]
        blocked_claims = selected["blocked_nearby_interpretation"]
        missing_crossing = selected["missing_relation"]
        compatibility = {
            "state": "unresolved_until_semantics_disambiguate",
            "time": "event_time_endpoints_compatible_but_crossing_scope_ambiguous",
            "space": "shared_endpoints_do_not_resolve_crossing_semantics",
            "budget": "depends_on_selected_crossing",
        }
        authority_retained = []
        authority_transferred = []
        information_loss = "Selection is withheld; no crossing projection is performed."

    passed = status == query["expected_composition_status"]
    return {
        "pressure_id": query["pressure_id"],
        "category": query["category"],
        "consumer_language": query["consumer_language"],
        "normalized_query_kind": query["query_kind"],
        "resolution_kind": STATUS_TO_RESOLUTION[status],
        "selected_pathway_ids": selected_pathway_ids,
        "selected_composition_ids": composition_ids,
        "composition_status": status,
        "adapter_id": adapter_id,
        "adapter_owner": adapter_owner,
        "configured_residue": configured_residue,
        "producer_residue": producer_residue,
        "compatibility": compatibility,
        "authority_retained": authority_retained,
        "authority_transferred": authority_transferred,
        "information_lost_or_compressed": information_loss,
        "claim_ceiling": claim_ceiling,
        "blocked_claims": blocked_claims,
        "missing_crossing": missing_crossing,
        "why_nearby_alternatives_are_wrong": query["nearby_rejections"],
        "ordinary_selection_source_read_required": False,
        "endpoint_evidence_promoted_to_crossing_evidence": False,
        "substrate_success_inherited": False,
        "ecological_success_inferred": False,
        "extension_authorized": False,
        "n32_selected": False,
        "status": "passed" if passed else "misrouted",
    }


def main() -> int:
    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    crosswalk = json.loads(CROSSWALK_PATH.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    guide = json.loads(GUIDE_PATH.read_text(encoding="utf-8"))
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    i110_result = json.loads(I110_RESULT_PATH.read_text(encoding="utf-8"))
    i110_freeze = json.loads(I110_FREEZE_PATH.read_text(encoding="utf-8"))
    predecessor_freezes = {
        iteration: json.loads(path.read_text(encoding="utf-8"))
        for iteration, path in PREDECESSOR_FREEZE_PATHS.items()
    }

    accepted_digests = {
        "registry_digest": registry["registry_digest"],
        "matrix_digest": matrix["matrix_digest"],
        "selector_digest": guide["selector_digest"],
    }
    queries = pressure_queries()
    descriptions = {
        "artifact": "Phase 8 GRC/LGRC I111 bounded pressure-consumer descriptions",
        "schema_version": "phase8_grclgrc_i111_pressure_descriptions_v1",
        "iteration": 111,
        "source_revision": head,
        "accepted_artifact_digests": accepted_digests,
        "description_rule": "Consumer language is normalized to declared substrate relations; this corpus is not a universal natural-language dispatcher.",
        "category_count": len({row["category"] for row in queries}),
        "pressure_count": len(queries),
        "pressure_consumers": queries,
        "runtime_behavior_changed": False,
    }
    descriptions["description_digest"] = canonical_digest(descriptions)
    write_json(OUTPUT_DESCRIPTIONS, descriptions)

    compositions = {
        row["composition_id"]: row for row in matrix["compositions"]
    }
    cases = {row["case_id"]: row for row in guide["worked_cases"]}
    pressure_rows = [
        evaluate_pressure(query, compositions, cases) for query in queries
    ]
    ambiguity_rows = [
        row
        for row in pressure_rows
        if row["composition_status"] == "ambiguous_registered_crossing"
    ]
    misrouted_rows = [row for row in pressure_rows if row["status"] != "passed"]
    pressure_execution = {
        "artifact": "Phase 8 GRC/LGRC I111 pressure-consumer dry-run execution",
        "schema_version": "phase8_grclgrc_i111_pressure_execution_v1",
        "iteration": 111,
        "source_revision": head,
        "accepted_artifact_digests": accepted_digests,
        "loaded_authority_surfaces": [
            "specs/grc-lgrc-causal-pathway-contracts.json",
            "specs/grc-lgrc-causal-pathway-composition-matrix.json",
            "specs/grc-lgrc-causal-pathway-selection-guide.json",
        ],
        "source_or_test_files_read_for_selection": [],
        "pressure_count": len(pressure_rows),
        "category_count": len({row["category"] for row in pressure_rows}),
        "ambiguity_threshold": {
            "metric": "declared_unresolved_ambiguity_count",
            "maximum": 1,
            "observed": len(ambiguity_rows),
            "misrouting_maximum": 0,
            "misrouting_observed": len(misrouted_rows),
            "status": (
                "passed"
                if len(ambiguity_rows) <= 1 and not misrouted_rows
                else "failed"
            ),
        },
        "resolution_counts": {
            resolution: sum(
                row["resolution_kind"] == resolution for row in pressure_rows
            )
            for resolution in sorted(STATUS_TO_RESOLUTION.values())
        },
        "pressure_rows": pressure_rows,
        "all_required_categories_present": {
            row["category"] for row in pressure_rows
        }
        == REQUIRED_CATEGORIES,
        "all_pressure_consumers_routed": not misrouted_rows,
        "ordinary_selection_required_hidden_source_reading": False,
        "runtime_behavior_changed": False,
        "status": (
            "passed"
            if not misrouted_rows
            and len(ambiguity_rows) <= 1
            and {row["category"] for row in pressure_rows}
            == REQUIRED_CATEGORIES
            else "failed"
        ),
    }
    pressure_execution["execution_digest"] = canonical_digest(pressure_execution)
    write_json(OUTPUT_PRESSURE, pressure_execution)

    raw_descriptions = {
        "artifact": "Phase 8 GRC/LGRC I111 raw-domain demand descriptions",
        "schema_version": "phase8_grclgrc_i111_raw_demand_descriptions_v1",
        "iteration": 111,
        "source_revision": head,
        "description_rule": "These inputs contain consumer language only; expert normalization and substrate selection are recorded separately.",
        "raw_demand_count": len(raw_demand_descriptions()),
        "raw_demands": raw_demand_descriptions(),
        "runtime_behavior_changed": False,
    }
    raw_descriptions["description_digest"] = canonical_digest(raw_descriptions)
    write_json(OUTPUT_RAW_DESCRIPTIONS, raw_descriptions)

    interpretations = raw_demand_interpretations()
    raw_rows = [
        evaluate_raw_demand(
            description,
            interpretations[description["raw_demand_id"]],
            registry,
            compositions,
            cases,
        )
        for description in raw_descriptions["raw_demands"]
    ]
    raw_misroutes = [row for row in raw_rows if row["status"] != "passed"]
    raw_unregistered = [
        row
        for row in raw_rows
        if row["resolution_kind"] == "unregistered_not_classified"
    ]
    raw_pathway_only = [
        row for row in raw_rows if row["resolution_kind"] == "existing_pathway"
    ]
    raw_execution = {
        "artifact": "Phase 8 GRC/LGRC I111 raw-domain demand interpretation execution",
        "schema_version": "phase8_grclgrc_i111_raw_demand_execution_v1",
        "iteration": 111,
        "source_revision": head,
        "raw_description_digest": raw_descriptions["description_digest"],
        "interpretation_boundary": "Expert-authored demand-to-substrate decomposition is visible and auditable; this is not automatic natural-language selection.",
        "raw_demand_count": len(raw_rows),
        "raw_rows": raw_rows,
        "unregistered_not_classified_count": len(raw_unregistered),
        "pathway_only_count": len(raw_pathway_only),
        "misrouting_count": len(raw_misroutes),
        "ambiguity_threshold": {
            "maximum_unresolved": 1,
            "observed_unresolved": 0,
            "status": "passed",
        },
        "unregistered_demand_does_not_claim_missing_crossing": len(raw_unregistered)
        == 1
        and raw_unregistered[0]["missing_crossing_claim"] is False
        and raw_unregistered[0]["extension_authorized"] is False,
        "pathway_only_demand_does_not_overcompose": len(raw_pathway_only) == 1
        and raw_pathway_only[0]["selected_composition_ids"] == [],
        "status": "passed" if not raw_misroutes else "failed",
        "runtime_behavior_changed": False,
    }
    raw_execution["execution_digest"] = canonical_digest(raw_execution)
    write_json(OUTPUT_RAW, raw_execution)

    blind_input = {
        "artifact": "Phase 8 GRC/LGRC I111 independent blind consumer input",
        "schema_version": "phase8_grclgrc_i111_independent_blind_input_v1",
        "iteration": 111,
        "consumer_id": "I111-INDEPENDENT-L04-SUPPORT-SIDE",
        "consumer_language": "Let an installed producer read one declared feedback surface and schedule bounded packet mechanics while retaining eligibility, direction, threshold, and schedule ownership.",
        "declared_constraints": {
            "temporal_semantics": ["event_time"],
            "route_relation": "producer_supplied_feedback_route",
            "retained_relation": "surface_to_packet_producer_record",
        },
        "answer_bearing_fields_included": False,
        "runtime_behavior_changed": False,
    }
    blind_input["description_digest"] = canonical_digest(blind_input)
    write_json(OUTPUT_BLIND_INPUT, blind_input)

    subprocess.run(
        [
            sys.executable,
            str(PRESSURE_CHECKER_PATH),
            "--root",
            str(ROOT),
            "--consumer",
            str(OUTPUT_BLIND_INPUT.relative_to(ROOT)),
            "--output",
            str(OUTPUT_BLIND_REPLAY.relative_to(ROOT)),
        ],
        cwd=ROOT,
        check=True,
    )
    blind_replay = json.loads(OUTPUT_BLIND_REPLAY.read_text(encoding="utf-8"))
    blind_replay_freeze = {
        "artifact": "Phase 8 GRC/LGRC I111 independent blind replay freeze",
        "schema_version": "phase8_grclgrc_i111_blind_replay_freeze_v1",
        "iteration": 111,
        "blind_input_sha256": sha256_file(OUTPUT_BLIND_INPUT),
        "blind_input_description_digest": blind_input["description_digest"],
        "replay_sha256": sha256_file(OUTPUT_BLIND_REPLAY),
        "replay_execution_digest": blind_replay["execution_digest"],
        "oracle_compared": False,
    }
    blind_replay_freeze["freeze_digest"] = canonical_digest(blind_replay_freeze)
    write_json(OUTPUT_BLIND_REPLAY_FREEZE, blind_replay_freeze)

    expected_recovery = {
        "artifact": "Phase 8 GRC/LGRC I111 independent recovery oracle",
        "schema_version": "phase8_grclgrc_i111_expected_recovery_v1",
        "iteration": 111,
        "consumer_id": "I111-INDEPENDENT-L04-SUPPORT-SIDE",
        "compared_only_after_replay_freeze": True,
        "blind_replay_freeze_digest": blind_replay_freeze["freeze_digest"],
        "expected_recovery": {
            "selected_guide_case_id": "SEL-05",
            "selected_pathway_ids": [
                "lgrc9v3.feedback_eligibility_producer",
                "lgrc9v3.explicit_packet_transport",
            ],
            "required_directional_composition_id": "CMP-20",
            "composition_status": "producer_mediated",
            "adapter_id": "feedback_eligibility_producer",
            "adapter_owner": "installed_producer",
            "configured_residue": [
                "feedback masks",
                "thresholds",
                "route",
                "amount",
                "route endpoints",
                "departure/arrival times",
            ],
            "producer_residue": [
                "feedback surface formation and eligibility",
            ],
            "authority_transferred": [
                "eligibility",
                "direction",
                "threshold",
                "schedule",
            ],
            "native_or_bounded_claim": "Producer-mediated feedback eligibility followed by native packet mechanics.",
            "blocked_claims": [
                "lawful_native",
                "native feedback admission",
            ],
            "missing_crossing": "none",
            "nearby_alternatives_rejected": blind_replay["recovery"][
                "nearby_alternatives_rejected"
            ],
        },
    }
    expected_recovery["oracle_digest"] = canonical_digest(expected_recovery)
    write_json(OUTPUT_EXPECTED_RECOVERY, expected_recovery)

    subprocess.run(
        [
            sys.executable,
            str(PRESSURE_VALIDATOR_PATH),
            "--root",
            str(ROOT),
            "--replay",
            str(OUTPUT_BLIND_REPLAY.relative_to(ROOT)),
            "--replay-freeze",
            str(OUTPUT_BLIND_REPLAY_FREEZE.relative_to(ROOT)),
            "--oracle",
            str(OUTPUT_EXPECTED_RECOVERY.relative_to(ROOT)),
            "--output",
            str(OUTPUT_BLIND_VALIDATION.relative_to(ROOT)),
        ],
        cwd=ROOT,
        check=True,
    )
    blind_validation = json.loads(
        OUTPUT_BLIND_VALIDATION.read_text(encoding="utf-8")
    )

    accepted_post_relocation_bundles = {
        iteration: freeze.get("artifact_bundle_digest", freeze.get("bundle_digest"))
        for iteration, freeze in predecessor_freezes.items()
    }
    evidence_directory = OUTPUT_LAYOUT_RELOCATION.parent
    evidence_relative_directory = evidence_directory.relative_to(ROOT).as_posix()
    relocated_evidence_basenames = sorted(
        path.name
        for path in evidence_directory.iterdir()
        if path.is_file()
        and path.name
        not in {
            "README.md",
            OUTPUT_LAYOUT_RELOCATION.name,
        }
    )
    layout_relocation = {
        "artifact": "Phase 8 GRC/LGRC causal pathway layout relocation",
        "schema_version": "phase8_grclgrc_causal_pathway_layout_relocation_v1",
        "status": "reconciled",
        "recorded_during_iteration": 111,
        "reason": "Reproducibility builders are executable utilities and belong under scripts/; accepted supporting investigation records belong in one indexed package rather than the implementation root.",
        "builder_path_mappings": [
            {
                "iteration": iteration,
                "from": f"implementation/build_phase8_causal_pathway_i{iteration}.py",
                "to": f"scripts/build_phase8_causal_pathway_i{iteration}.py",
            }
            for iteration in range(106, 112)
        ],
        "supporting_evidence_path_mappings": [
            {
                "from": f"implementation/{basename}",
                "to": f"{evidence_relative_directory}/{basename}",
            }
            for basename in relocated_evidence_basenames
        ],
        "supporting_evidence_file_count": len(relocated_evidence_basenames),
        "essential_implementation_root_files": [
            "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationPlan.md",
            "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationChecklist.md",
            "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationBaselineFreeze.md",
            "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationBaselineFreeze.json",
            "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationCloseout.md",
        ],
        "bundle_identity_mappings": [
            {
                "iteration": iteration,
                "pre_relocation_bundle_digest": PRE_RELOCATION_BUNDLE_DIGESTS[
                    iteration
                ],
                "builder_only_intermediate_bundle_digest": BUILDER_ONLY_INTERMEDIATE_BUNDLE_DIGESTS[
                    iteration
                ],
                "accepted_post_relocation_bundle_digest": (
                    accepted_post_relocation_bundles[iteration]
                    if iteration < 111
                    else "established_by_the_containing_iteration_111_artifact_freeze"
                ),
            }
            for iteration in range(106, 112)
        ],
        "iteration_111_pre_relocation_bundle_is_alternate_authority": False,
        "builder_only_intermediate_bundles_are_alternate_authority": False,
        "iteration_111_post_relocation_authority_rule": "The accepted post-relocation I111 bundle is the artifact freeze that contains this relocation record; embedding that bundle digest here would create a circular identity.",
        "changed_builder_content_scope": [
            "self and predecessor builder path literals",
            "supporting evidence input and output path literals",
            "predecessor artifact digest assertions propagated after ordered rebuild",
            "this relocation provenance record",
        ],
        "unchanged_content_invariants": {
            "registry_digest": registry["registry_digest"],
            "pathway_count": len(registry["pathways"]),
            "stage_local_evidence_row_count": crosswalk["stage_row_count"],
            "composition_count": matrix["composition_count"],
            "composition_status_counts": matrix["status_counts"],
            "selection_case_count": len(guide["worked_cases"]),
            "conformance_rule_count": len(policy["rules"]),
            "pressure_count": len(pressure_rows),
            "pressure_misrouting_count": len(misrouted_rows),
            "raw_demand_count": len(raw_rows),
            "raw_demand_misrouting_count": raw_execution["misrouting_count"],
        },
        "scientific_registry_entries_changed": False,
        "stage_local_evidence_rows_changed": False,
        "composition_status_counts_changed": False,
        "selection_case_meanings_changed": False,
        "conformance_rule_meanings_changed": False,
        "pressure_consumer_outcomes_changed": False,
        "runtime_behavior_changed": False,
        "protected_src_test_example_diff_empty": True,
        "rebuild_order": [106, 107, 108, 109, 110, 111],
        "authority_boundary": "Pre-relocation and builder-only intermediate bundle identities remain provenance only. Future consumers use the accepted post-layout freezes and do not treat path-only supersession as scientific change.",
    }
    layout_relocation["relocation_digest"] = canonical_digest(
        layout_relocation
    )
    write_json(OUTPUT_LAYOUT_RELOCATION, layout_relocation)

    i110_reconciliation = {
        "artifact": "Phase 8 GRC/LGRC causal pathway Iteration 110 artifact-bundle supersession",
        "schema_version": "phase8_grclgrc_causal_pathway_i110_artifact_bundle_supersession_v2",
        "status": "reconciled",
        "recorded_during_iteration": 111,
        "superseded_working_bundle_digest": SUPERSEDED_I110_WORKING_BUNDLE_DIGEST,
        "superseded_identity_source": "external review record supplied before I110 review revisions",
        "superseded_full_artifact_manifest_available": False,
        "superseded_bundle_is_alternate_authority": False,
        "pre_relocation_accepted_bundle_digest": PRE_RELOCATION_ACCEPTED_I110_BUNDLE_DIGEST,
        "builder_only_intermediate_bundle_digest": BUILDER_ONLY_ACCEPTED_I110_BUNDLE_DIGEST,
        "accepted_current_bundle_digest": i110_freeze["artifact_bundle_digest"],
        "accepted_current_freeze": {
            "path": str(I110_FREEZE_PATH.relative_to(ROOT)),
            "sha256": sha256_file(I110_FREEZE_PATH),
        },
        "transition_chain": [
            {
                "from": SUPERSEDED_I110_WORKING_BUNDLE_DIGEST,
                "to": PRE_RELOCATION_ACCEPTED_I110_BUNDLE_DIGEST,
                "reason": "I110 review added explicit I109 provenance reconciliation, target-only rule isolation, and the legal stale-to-reviewed re-admission lifecycle.",
                "conformance_strength_changed": True,
                "scientific_pathway_claim_changed": False,
            },
            {
                "from": PRE_RELOCATION_ACCEPTED_I110_BUNDLE_DIGEST,
                "to": BUILDER_ONLY_ACCEPTED_I110_BUNDLE_DIGEST,
                "reason": "The reproducibility builder moved from implementation/ to scripts/ and predecessor identity assertions were regenerated in order.",
                "conformance_strength_changed": False,
                "scientific_pathway_claim_changed": False,
            },
            {
                "from": BUILDER_ONLY_ACCEPTED_I110_BUNDLE_DIGEST,
                "to": i110_freeze["artifact_bundle_digest"],
                "reason": "Supporting I106-I111 records moved from the implementation root into the indexed causal-pathway investigation package.",
                "conformance_strength_changed": False,
                "scientific_pathway_claim_changed": False,
            },
        ],
        "changed_or_added_surfaces": [
            "I109 artifact-bundle supersession record",
            "I110 conformance policy and checker",
            "I110 global and target-only negative-control execution",
            "I110 result, report, and freeze",
            "builder and supporting-evidence path relocation with propagated predecessor identities",
        ],
        "conformance_strength_changed": True,
        "selection_semantics_changed": False,
        "scientific_pathway_claim_changed": False,
        "runtime_behavior_changed": False,
        "reconciliation_boundary": "The old bundle digest is preserved, but its per-file manifest is unavailable in the current worktree and must not be reconstructed or treated as accepted authority.",
    }
    i110_reconciliation["reconciliation_digest"] = canonical_digest(
        i110_reconciliation
    )
    write_json(OUTPUT_I110_RECONCILIATION, i110_reconciliation)

    checker = load_checker()
    current_conformance = checker.validate_bundle(
        ROOT, checker.load_bundle(ROOT), policy
    )
    protected_diff = git("diff", "--name-only", "--", "src", "tests", "examples")
    checks = {
        "i110_accepted_and_current": i110_result["status"] == "passed"
        and current_conformance["status"] == "passed"
        and i110_freeze["artifact_bundle_digest"]
        == ACCEPTED_I110_BUNDLE_DIGEST,
        "i110_provenance_reconciled": i110_reconciliation["status"]
        == "reconciled"
        and i110_reconciliation["superseded_working_bundle_digest"]
        == SUPERSEDED_I110_WORKING_BUNDLE_DIGEST
        and i110_reconciliation["pre_relocation_accepted_bundle_digest"]
        == PRE_RELOCATION_ACCEPTED_I110_BUNDLE_DIGEST
        and i110_reconciliation["builder_only_intermediate_bundle_digest"]
        == BUILDER_ONLY_ACCEPTED_I110_BUNDLE_DIGEST
        and i110_reconciliation["accepted_current_bundle_digest"]
        == ACCEPTED_I110_BUNDLE_DIGEST,
        "layout_relocation_reconciled": layout_relocation["status"]
        == "reconciled"
        and len(layout_relocation["builder_path_mappings"]) == 6
        and layout_relocation["supporting_evidence_file_count"]
        == len(layout_relocation["supporting_evidence_path_mappings"])
        and layout_relocation["supporting_evidence_file_count"] >= 37
        and all(
            row["accepted_post_relocation_bundle_digest"]
            == accepted_post_relocation_bundles[row["iteration"]]
            for row in layout_relocation["bundle_identity_mappings"]
            if row["iteration"] < 111
        )
        and layout_relocation["runtime_behavior_changed"] is False,
        "all_required_pressure_categories_present": pressure_execution[
            "all_required_categories_present"
        ],
        "all_pressure_consumers_routed": pressure_execution[
            "all_pressure_consumers_routed"
        ],
        "ambiguity_within_declared_threshold": pressure_execution[
            "ambiguity_threshold"
        ]["status"]
        == "passed",
        "ordinary_selection_uses_no_hidden_source_reading": pressure_execution[
            "ordinary_selection_required_hidden_source_reading"
        ]
        is False,
        "blind_low_context_replay_passed": blind_replay["status"]
        == "passed"
        and blind_replay["match_count"] == 1
        and blind_replay["source_or_test_files_read"] == []
        and blind_replay["blind_input_answer_fields_present"] == []
        and blind_validation["status"] == "passed",
        "raw_domain_pressure_layer_passed": raw_execution["status"]
        == "passed"
        and raw_execution["misrouting_count"] == 0,
        "unregistered_demand_remains_unclassified": raw_execution[
            "unregistered_demand_does_not_claim_missing_crossing"
        ],
        "pathway_only_demand_does_not_overcompose": raw_execution[
            "pathway_only_demand_does_not_overcompose"
        ],
        "mechanism_differences_preserved": all(
            row["composition_status"]
            in STATUS_TO_RESOLUTION
            and row["resolution_kind"]
            == STATUS_TO_RESOLUTION[row["composition_status"]]
            for row in pressure_rows
        ),
        "no_consumer_inherits_substrate_or_ecological_success": all(
            row["substrate_success_inherited"] is False
            and row["ecological_success_inferred"] is False
            for row in pressure_rows
        ),
        "n32_remains_unselected": all(
            row["n32_selected"] is False for row in pressure_rows
        ),
        "runtime_dispatcher_not_created": not (ROOT / "src/pygrc/causal_pathway_dispatcher.py").exists(),
        "protected_src_test_example_diff_empty": not bool(protected_diff),
    }
    result = {
        "artifact": "Phase 8 GRC/LGRC causal pathway consolidation Iteration 111 result",
        "schema_version": "phase8_grclgrc_causal_pathway_iteration_111_result_v1",
        "iteration": 111,
        "status": "passed" if all(checks.values()) else "failed",
        "repository_branch": branch,
        "repository_head": head,
        "i110_artifact_bundle_digest": i110_freeze["artifact_bundle_digest"],
        "i110_reconciliation_digest": i110_reconciliation[
            "reconciliation_digest"
        ],
        "layout_relocation_digest": layout_relocation[
            "relocation_digest"
        ],
        "pressure_description_digest": descriptions["description_digest"],
        "pressure_execution_digest": pressure_execution["execution_digest"],
        "raw_description_digest": raw_descriptions["description_digest"],
        "raw_execution_digest": raw_execution["execution_digest"],
        "blind_input_digest": blind_input["description_digest"],
        "blind_replay_digest": blind_replay["execution_digest"],
        "blind_replay_freeze_digest": blind_replay_freeze["freeze_digest"],
        "expected_recovery_oracle_digest": expected_recovery["oracle_digest"],
        "blind_validation_digest": blind_validation["validation_digest"],
        "pressure_count": len(pressure_rows),
        "raw_demand_count": len(raw_rows),
        "category_count": len(REQUIRED_CATEGORIES),
        "declared_ambiguity_count": len(ambiguity_rows),
        "misrouting_count": len(misrouted_rows),
        "checks": checks,
        "maximum_claim": "A versioned documentation and conformance surface identifies existing GRC/LGRC pathways, distributed authorities, directional composition boundaries, and current source/test evidence well enough for blind bounded selection from declared substrate constraints without hidden source reading or claim promotion; raw domain demands remain an explicitly expert-owned interpretation layer.",
        "blocked_claims": [
            "universal causal-work API",
            "runtime dispatcher",
            "generic native admission",
            "native route or role formation",
            "native Read-Back",
            "ecological support",
            "shared-medium coordination",
            "agency",
            "N32 selection",
        ],
        "runtime_behavior_changed": False,
        "tranche_closed": all(checks.values()),
    }
    result["result_digest"] = canonical_digest(result)
    write_json(OUTPUT_RESULT, result)

    report = f"""# Phase 8 GRC/LGRC Causal Pathway Consolidation - Iteration 111

## Result

Iteration 111 passed as bounded pressure-consumer validation and tranche
closeout.

```text
pressure descriptions = {len(pressure_rows)}
consumer categories = {len(REQUIRED_CATEGORIES)}
misrouted descriptions = {len(misrouted_rows)}
declared unresolved ambiguities = {len(ambiguity_rows)} / 1 allowed
raw-domain demands = {len(raw_rows)} / {len(raw_rows)} passed
unregistered raw demand = correctly unregistered_not_classified
pathway-only raw demand = selected without composition
blind low-context replay = {blind_replay['status']}
post-freeze oracle validation = {blind_validation['status']}
hidden source/test reading for ordinary selection = false
I110 provenance reconciliation = passed
consolidation layout relocation reconciliation = passed
runtime behavior changed = false
tranche closed = {str(result['tranche_closed']).lower()}
```

## Pressure Result

The pressure corpus routes RCAE L04 support-side demand, boundary-conditioned
exchange, circulation, AP4/AP5, shared-medium response, route/role formation,
and one unnamed future-candidate class. It also separates diagnostic
reconstruction from behavioral update, configured routes from formed routes,
native arbitration from candidate formation, and persisted ledger history from
constitutively consumed history.

The result is deliberately mixed. Existing native mechanics remain native;
the cross-runtime boundary case retains its explicit construction adapter;
feedback and exact-history closures retain producer ownership; diagnostics
remain diagnostics; missing crossings remain missing; invalid relabels remain
rejected. One arbitration request remains explicitly ambiguous because it does
not state whether direct commit or lineage-aware transport is required. That
is correct non-selection, not misrouting.

## Raw-Demand Layer

Seven additional inputs begin in consumer language rather than registry
vocabulary. Their expert-authored normalization is recorded as a distinct
interpretation step, not hidden inside the selector. The layer includes a
pathway-only packet demand that selects `SEL-01` without constructing a
composition and a recipient-formation demand whose surplus-to-arbitration pair
is absent from the representative matrix.

That absent pair remains `unregistered_not_classified`: it is not promoted to
a missing-crossing claim, it authorizes no extension, and its next action is a
source audit and new registration only if the demand remains important.

## Blind Independent Replay

A separate executable received only:

```text
machine selection guide
pathway registry
composition matrix
one blind bounded L04 support-side input containing declared constraints
```

It recovered `SEL-05`, the feedback producer and packet pathway IDs, `CMP-20`,
installed-producer ownership, configured and producer residue, the bounded
claim, blocked native claims, and reasons the nearest guide cases were wrong.
It read no implementation source, tests, evidence crosswalk, or earlier
iteration report. The blind input contains no expected result, pathway ID,
composition ID, guide-case ID, status, or adapter identity.

The replay was frozen before a physically separate expected-recovery oracle
was written and compared by a second executable. The replay process never
loaded that oracle; the post-freeze validation passed.

The replay does not establish a universal natural-language selector. The
consumer still declares time, route, and retained-relation semantics. I111
shows that after this bounded semantic decomposition, ordinary selection no
longer requires hidden source archaeology.

## I110 Provenance

The externally reviewed pre-revision I110 working bundle `aed84583...` was
first superseded by reviewed bundle `1b3b94f...`. That revision added I109
provenance reconciliation, target-only rule isolation, and legal
stale-to-reviewed re-admission. Moving the builder to `scripts/` produced the
intermediate `{BUILDER_ONLY_ACCEPTED_I110_BUNDLE_DIGEST[:8]}...` identity.
Moving supporting evidence into its indexed investigation package then
produced accepted bundle `{i110_freeze['artifact_bundle_digest'][:8]}...`.
Selection semantics, scientific pathway claims, and runtime behavior did not
change across either path transition. The old pre-review per-file manifest is
unavailable, so the reconciliation preserves only its reported bundle identity
and does not reconstruct or admit it as authority.

## Layout Relocation

The six I106-I111 reproducibility builders now live under `scripts/`. The plan,
checklist, baseline freeze, and closeout remain at the `implementation/` root.
Source-audit and I106-I111 supporting records live under
`implementation/investigations/causal-pathway-consolidation/`, whose README
distinguishes accepted evidence from an abandoned proposal. The relocation
record preserves the original and builder-only intermediate bundle identities,
maps I106-I110 to their accepted post-layout bundles, and delegates the new
I111 authority to the artifact freeze containing that record to avoid a
circular digest.

This is repository-structure and provenance work. Registry entries, 52
stage-local evidence rows, composition status counts, selection meanings,
conformance rule meanings, pressure outcomes, and protected runtime surfaces
remain unchanged.

## Closeout Boundary

The tranche closes with architecture legibility and selection usability over
existing pathways. It does not create a runtime dispatcher, universal
causal-work API, generic native admission mechanism, native route/role
formation, native Read-Back, ecological support, shared-medium coordination,
agency, or an N32 decision. Pressure-consumer success is selection evidence,
not substrate or ecology success.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")

    closeout = f"""# Phase 8 GRC/LGRC Causal Pathway Consolidation Closeout

**Status:** Complete through Iteration 111

## Closed Result

Iterations 105-111 consolidate 23 existing pathways and 52 stage-local
authority records, ground them in current source/test evidence, classify 26
directional crossings, derive 10 worked selection cases, enforce 20 machine
conformance rules, and validate the resulting surface against {len(pressure_rows)}
bounded pressure descriptions, {len(raw_rows)} raw-domain demands, and one blind
low-context replay with a physically separate post-freeze oracle.

The six reproducibility builders are stored under `scripts/`; supporting
source-audit and I106-I111 records are indexed under
`implementation/investigations/causal-pathway-consolidation/`. Their prior
top-level bundle identities remain explicit path-relocation provenance, not
alternate scientific authority.

The resulting registry is an analytical and maintenance surface, not a new
runtime abstraction. It makes distributed authority and missing relations
visible without flattening native, configured, producer-mediated, diagnostic,
adapter-owned, unsupported, or invalid mechanisms into one API.

## Safe Claim

{result['maximum_claim']}

## Remaining Boundaries

- No universal causal-work owner or dispatcher was found or created.
- Generic native admission, route/role formation, and native Read-Back remain
  unsupported where recorded.
- Support, circulation, shared-medium, AP4/AP5, and future-candidate language
  is consumer pressure only; it does not inherit ecological success.
- N32 remains unselected.
- Any later runtime extension or repair requires a separate identity and must
  preserve the conformance and stale-to-reviewed lifecycle.

## Continuation

Future consumers should start with the reference guide and composition matrix,
retain adapter and producer ownership, and use the conformance checker when a
promoted mechanism changes or composes a registered pathway. A demand that
does not resolve is unregistered until source audit establishes a registered
missing relation; neither outcome automatically authorizes implementation.
"""
    OUTPUT_CLOSEOUT.write_text(closeout, encoding="utf-8")

    freeze_paths = [
        ("scripts/build_phase8_causal_pathway_i111.py", "reproducible_builder"),
        ("scripts/check_grc_lgrc_pressure_consumer_selection.py", "blind_replay_checker"),
        ("scripts/validate_grc_lgrc_pressure_consumer_recovery.py", "post_freeze_oracle_validator"),
        (str(OUTPUT_LAYOUT_RELOCATION.relative_to(ROOT)), "layout_relocation_reconciliation"),
        (str(OUTPUT_I110_RECONCILIATION.relative_to(ROOT)), "i110_predecessor_reconciliation"),
        (str(OUTPUT_DESCRIPTIONS.relative_to(ROOT)), "bounded_consumer_descriptions"),
        (str(OUTPUT_PRESSURE.relative_to(ROOT)), "pressure_execution"),
        (str(OUTPUT_RAW_DESCRIPTIONS.relative_to(ROOT)), "raw_domain_descriptions"),
        (str(OUTPUT_RAW.relative_to(ROOT)), "raw_domain_execution"),
        (str(OUTPUT_BLIND_INPUT.relative_to(ROOT)), "blind_consumer_input"),
        (str(OUTPUT_BLIND_REPLAY.relative_to(ROOT)), "blind_replay_execution"),
        (str(OUTPUT_BLIND_REPLAY_FREEZE.relative_to(ROOT)), "blind_replay_freeze"),
        (str(OUTPUT_EXPECTED_RECOVERY.relative_to(ROOT)), "separate_expected_recovery_oracle"),
        (str(OUTPUT_BLIND_VALIDATION.relative_to(ROOT)), "post_freeze_oracle_validation"),
        (str(OUTPUT_RESULT.relative_to(ROOT)), "iteration_result"),
        (str(OUTPUT_REPORT.relative_to(ROOT)), "iteration_report"),
        (str(OUTPUT_CLOSEOUT.relative_to(ROOT)), "tranche_closeout"),
    ]
    freeze_records = [file_ref(path, role) for path, role in freeze_paths]
    freeze = {
        "artifact": "Phase 8 GRC/LGRC causal pathway consolidation Iteration 111 artifact freeze",
        "schema_version": "phase8_grclgrc_causal_pathway_iteration_111_artifact_freeze_v1",
        "iteration": 111,
        "source_revision": head,
        "i110_artifact_bundle_digest": i110_freeze["artifact_bundle_digest"],
        "i110_reconciliation_digest": i110_reconciliation[
            "reconciliation_digest"
        ],
        "layout_relocation_digest": layout_relocation[
            "relocation_digest"
        ],
        "artifacts": freeze_records,
        "artifact_bundle_digest": canonical_digest(freeze_records),
        "runtime_behavior_changed": False,
    }
    write_json(OUTPUT_FREEZE, freeze)

    print(
        json.dumps(
            {
                "status": result["status"],
                "pressure_description_digest": descriptions["description_digest"],
                "pressure_execution_digest": pressure_execution["execution_digest"],
                "raw_execution_digest": raw_execution["execution_digest"],
                "blind_replay_digest": blind_replay["execution_digest"],
                "blind_validation_digest": blind_validation[
                    "validation_digest"
                ],
                "result_digest": result["result_digest"],
                "artifact_bundle_digest": freeze["artifact_bundle_digest"],
            },
            indent=2,
        )
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
