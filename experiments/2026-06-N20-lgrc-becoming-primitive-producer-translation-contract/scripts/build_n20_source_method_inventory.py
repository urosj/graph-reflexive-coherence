#!/usr/bin/env python3
"""Build N20 Iteration 1 source and method inventory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-22T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract"
)
OUTPUT = EXPERIMENT / "outputs" / "n20_source_method_inventory.json"
REPORT = EXPERIMENT / "reports" / "n20_source_method_inventory.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "scripts/build_n20_source_method_inventory.py"
)

INVARIANTS = {
    "primitive_evidence_opened": False,
    "agency_claim_opened": False,
    "phase8_opened": False,
    "native_support_opened": False,
    "sentience_opened": False,
    "ant_ecology_spec_opened": False,
    "src_diff_empty_required": True,
}

UNSAFE_CLAIM_KEYS = [
    "agency",
    "semantic_intention",
    "semantic_choice",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "phase8_implementation",
    "organism_life",
    "sentience",
    "consciousness",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy",
]

ALLOWED_SOURCE_ROLES = {
    "method_source",
    "diagnostic_vocabulary_source",
    "boundary_source",
    "implementation_boundary_source",
    "roadmap_source",
    "future_application_context",
}

LOCAL_SOURCE_PATHS = {
    "n19_closeout_artifact": (
        "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
        "outputs/n19_closeout_and_handoff.json"
    ),
    "n19_closeout_report": (
        "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
        "reports/n19_closeout_and_handoff.md"
    ),
    "n19_phase8_matrix": (
        "experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/"
        "outputs/n19_phase8_readiness_matrix.json"
    ),
    "n20_n29_roadmap": "experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md",
    "n12_n18_roadmap": "experiments/N12-N18-LGRC-AgencyPrerequisitesRoadmap.md",
    "n12_n18_handoff": "experiments/N12-N18-LGRC-AgencyPrerequisitesHandoff.md",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def unsafe_flags() -> dict[str, bool]:
    return {key: False for key in UNSAFE_CLAIM_KEYS}


def local_record(path_key: str) -> dict[str, Any]:
    path = LOCAL_SOURCE_PATHS[path_key]
    record: dict[str, Any] = {
        "record_type": "relative_path_digest",
        "path": path,
        "sha256": sha256_file(path),
    }
    if path.endswith(".json"):
        data = load_json(path)
        record["parseable_json"] = True
        record["output_digest"] = str(data.get("output_digest", "not_recorded"))
        record["status"] = str(data.get("status", "not_recorded"))
    return record


def title_record(source_repo_id: str, collection: str) -> dict[str, str]:
    return {
        "record_type": "title_record_only",
        "source_repo_id": source_repo_id,
        "collection": collection,
    }


def row(
    *,
    row_id: str,
    source_id: str,
    source_title: str,
    source_role: str,
    may_consume_as: list[str],
    must_not_consume_as: list[str],
    diagnostics_or_method_terms: list[str],
    source_digest_or_title_record: dict[str, Any],
    relative_path_or_repo_id: str,
    claim_boundary: str,
    source_consumption_rule: str,
) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "source_id": source_id,
        "source_title": source_title,
        "source_role": source_role,
        "may_consume_as": may_consume_as,
        "must_not_consume_as": must_not_consume_as,
        "diagnostics_or_method_terms": diagnostics_or_method_terms,
        "claim_boundary": claim_boundary,
        "unsafe_claim_flags": unsafe_flags(),
        "primitive_evidence_status": "not_primitive_evidence",
        "agency_proof_status": "not_agency_proof",
        "source_consumption_rule": source_consumption_rule,
        "source_digest_or_title_record": source_digest_or_title_record,
        "relative_path_or_repo_id": relative_path_or_repo_id,
        "row_decision": "supported",
        "contract_status": "complete",
    }


def source_rows() -> list[dict[str, Any]]:
    return [
        row(
            row_id="n20_i1_row_01_n19_implementation_boundary",
            source_id="N19",
            source_title="LGRC Native Naturalization Review AP3-AP8",
            source_role="implementation_boundary_source",
            may_consume_as=[
                "native-readiness boundary",
                "AP4/AP5 NAT4 gap source",
                "Phase 8 and native-support blocker source",
            ],
            must_not_consume_as=[
                "Phase 8 implementation",
                "native support",
                "primitive evidence",
                "agency proof",
                "AP4/AP5 NAT4 gap resolution",
            ],
            diagnostics_or_method_terms=[
                "current implementation boundary",
                "AP4/AP5 NAT4 gaps",
                "Phase 8 unopened",
                "native support unopened",
            ],
            source_digest_or_title_record={
                "primary": local_record("n19_closeout_artifact"),
                "report": local_record("n19_closeout_report"),
                "phase8_matrix": local_record("n19_phase8_matrix"),
            },
            relative_path_or_repo_id=LOCAL_SOURCE_PATHS["n19_closeout_artifact"],
            claim_boundary=(
                "N19 is consumed only as native-readiness boundary and gap source; "
                "it does not make the AP3-AP8 ladder natively generatable."
            ),
            source_consumption_rule="implementation_boundary_only_no_primitive_evidence",
        ),
        row(
            row_id="n20_i1_row_02_n20_n29_roadmap",
            source_id="N20_N29_ROADMAP",
            source_title="N20-N29 LGRC Becoming-Agency Ecology Roadmap",
            source_role="roadmap_source",
            may_consume_as=[
                "local experiment arc definition",
                "claim boundary source",
                "N29 convergence boundary",
            ],
            must_not_consume_as=[
                "primitive evidence",
                "agency proof",
                "Phase 8 implementation plan",
                "ant ecology specification before N29",
            ],
            diagnostics_or_method_terms=[
                "N20 contract",
                "N21-N28 primitive order",
                "N29 first formal ecology bridge",
            ],
            source_digest_or_title_record=local_record("n20_n29_roadmap"),
            relative_path_or_repo_id=LOCAL_SOURCE_PATHS["n20_n29_roadmap"],
            claim_boundary="Roadmap defines order and boundaries; it is not evidence.",
            source_consumption_rule="roadmap_not_evidence",
        ),
        row(
            row_id="n20_i1_row_03_classification_of_becoming_method",
            source_id="ARC_CLASSIFICATION_OF_BECOMING",
            source_title="Classification of Becoming",
            source_role="method_source",
            may_consume_as=[
                "method for naming expressed primitives",
                "method for non-promoting result classification",
            ],
            must_not_consume_as=[
                "proof of LGRC primitive evidence",
                "agency proof",
                "native support proof",
            ],
            diagnostics_or_method_terms=[
                "name primitives without semantic promotion",
                "classify what appeared",
                "preserve value without overclaiming",
            ],
            source_digest_or_title_record=title_record(
                "geometric-reflexive-coherence", "arc-of-becoming"
            ),
            relative_path_or_repo_id="geometric-reflexive-coherence",
            claim_boundary="Method only; classification is not proof.",
            source_consumption_rule="method_only_not_evidence",
        ),
        row(
            row_id="n20_i1_row_04_interrogation_of_becoming_method",
            source_id="ARC_INTERROGATION_OF_BECOMING",
            source_title="Interrogation of Becoming",
            source_role="method_source",
            may_consume_as=[
                "method for bounded probes",
                "method for failure and control design",
            ],
            must_not_consume_as=[
                "probe result proof",
                "primitive evidence",
                "agency proof",
            ],
            diagnostics_or_method_terms=[
                "bounded probe",
                "control design",
                "withdrawal as question",
            ],
            source_digest_or_title_record=title_record(
                "geometric-reflexive-coherence", "arc-of-becoming"
            ),
            relative_path_or_repo_id="geometric-reflexive-coherence",
            claim_boundary="Method only; probes remain questions until artifacts exist.",
            source_consumption_rule="method_only_not_evidence",
        ),
        row(
            row_id="n20_i1_row_05_naturalization_of_becoming_method",
            source_id="ARC_NATURALIZATION_OF_BECOMING",
            source_title="Naturalization of Becoming",
            source_role="method_source",
            may_consume_as=[
                "method for separating substrate-carried state",
                "method for identifying producer-mediated support",
                "method for naming naturalization debt",
            ],
            must_not_consume_as=[
                "native support proof",
                "Phase 8 proof",
                "primitive evidence",
            ],
            diagnostics_or_method_terms=[
                "naturalization gap",
                "support translation",
                "proxy-localization trap",
            ],
            source_digest_or_title_record=title_record(
                "geometric-reflexive-coherence", "arc-of-becoming"
            ),
            relative_path_or_repo_id="geometric-reflexive-coherence",
            claim_boundary="Method only; naturalization must be source-backed later.",
            source_consumption_rule="method_only_not_native_support",
        ),
        row(
            row_id="n20_i1_row_06_cultivation_of_becoming_method",
            source_id="ARC_CULTIVATION_OF_BECOMING",
            source_title="Cultivation of Becoming",
            source_role="method_source",
            may_consume_as=[
                "method for minimal producer-surface design",
                "method for integrate-after-probe sequencing",
            ],
            must_not_consume_as=[
                "permission to retune until success",
                "primitive evidence",
                "agency proof",
            ],
            diagnostics_or_method_terms=[
                "orient",
                "observe",
                "classify",
                "probe",
                "withdraw",
                "naturalize",
                "integrate",
            ],
            source_digest_or_title_record=title_record(
                "geometric-reflexive-coherence", "arc-of-becoming"
            ),
            relative_path_or_repo_id="geometric-reflexive-coherence",
            claim_boundary="Method only; cultivation cannot relabel scaffolded success.",
            source_consumption_rule="method_only_not_evidence",
        ),
        row(
            row_id="n20_i1_row_07_agency_of_becoming_diagnostics",
            source_id="ESSAY_AGENCY_OF_BECOMING",
            source_title="Agency of Becoming: An Interpretation Through Reflexive Coherence",
            source_role="diagnostic_vocabulary_source",
            may_consume_as=[
                "diagnostic vocabulary",
                "bounded interpretation source",
                "withdrawal/naturalization/transfer/proxy-pressure vocabulary",
            ],
            must_not_consume_as=[
                "proof of agency",
                "proof of LGRC primitive evidence",
                "proof of native support",
                "semantic intention proof",
            ],
            diagnostics_or_method_terms=[
                "withdrawal resistance",
                "naturalization depth",
                "configuration or substrate transfer",
                "proxy pressure",
                "generative versus extractive persistence",
            ],
            source_digest_or_title_record=title_record(
                "geometric-reflexive-coherence", "essays"
            ),
            relative_path_or_repo_id="geometric-reflexive-coherence",
            claim_boundary="Diagnostic vocabulary only; no agency claim opened.",
            source_consumption_rule="diagnostic_vocabulary_only_not_proof",
        ),
        row(
            row_id="n20_i1_row_08_agency_after_choice_vocabulary",
            source_id="ESSAY_AGENCY_AFTER_CHOICE",
            source_title="Agency After Choice",
            source_role="diagnostic_vocabulary_source",
            may_consume_as=[
                "scaffolded/native/proxy/wounded/extractive/generative vocabulary",
                "claim-boundary vocabulary",
            ],
            must_not_consume_as=[
                "semantic choice proof",
                "agency proof",
                "native agency proof",
                "primitive evidence",
            ],
            diagnostics_or_method_terms=[
                "scaffolded agency vocabulary",
                "native agency vocabulary",
                "proxy agency vocabulary",
                "wounded agency vocabulary",
                "extractive agency vocabulary",
                "generative agency vocabulary",
            ],
            source_digest_or_title_record=title_record(
                "geometric-reflexive-coherence", "essays"
            ),
            relative_path_or_repo_id="geometric-reflexive-coherence",
            claim_boundary="Vocabulary only; vocabulary labels cannot become proof.",
            source_consumption_rule="diagnostic_vocabulary_only_not_proof",
        ),
        row(
            row_id="n20_i1_row_09_structural_abundance_boundary",
            source_id="ESSAY_FROM_STRUCTURAL_ABUNDANCE_TO_AGENCY",
            source_title="From Structural Abundance to Agency",
            source_role="diagnostic_vocabulary_source",
            may_consume_as=[
                "abundance vocabulary",
                "surplus possibility boundary",
                "basin proliferation context",
            ],
            must_not_consume_as=[
                "abundance proof",
                "agency proof",
                "primitive evidence",
                "reward maximization proof",
            ],
            diagnostics_or_method_terms=[
                "structural abundance",
                "basin proliferation",
                "surplus possibility",
                "abundance is not yet agency",
            ],
            source_digest_or_title_record=title_record(
                "geometric-reflexive-coherence", "essays"
            ),
            relative_path_or_repo_id="geometric-reflexive-coherence",
            claim_boundary="Abundance opens a question; it does not prove agency.",
            source_consumption_rule="diagnostic_vocabulary_only_not_proof",
        ),
        row(
            row_id="n20_i1_row_10_sentience_as_readback_boundary",
            source_id="ESSAY_SENTIENCE_AS_READBACK",
            source_title="Sentience as Read-Back",
            source_role="boundary_source",
            may_consume_as=[
                "boundary source separating agency from sentience",
                "read-back and interiority blocker source",
            ],
            must_not_consume_as=[
                "sentience proof",
                "consciousness proof",
                "interiority proof",
                "primitive evidence",
                "agency proof",
            ],
            diagnostics_or_method_terms=[
                "sentience boundary",
                "read-back blocked",
                "interiority blocked",
            ],
            source_digest_or_title_record=title_record(
                "geometric-reflexive-coherence", "essays"
            ),
            relative_path_or_repo_id="geometric-reflexive-coherence",
            claim_boundary="Boundary-only; sentience and read-back claims remain closed.",
            source_consumption_rule="boundary_only_no_sentience_claim",
        ),
        row(
            row_id="n20_i1_row_11_agentic_ecology_future_context",
            source_id="AGENTIC_ECOLOGY_CONTEXT",
            source_title="Agentic Ecology / Ants Project",
            source_role="future_application_context",
            may_consume_as=[
                "future application context",
                "N29 convergence target",
                "medium-debt placeholder context",
            ],
            must_not_consume_as=[
                "ant ecology implementation spec before N29",
                "native ant agency proof",
                "native colony agency proof",
                "primitive evidence",
            ],
            diagnostics_or_method_terms=[
                "future multi-basin ecology context",
                "medium debt deferred until N28/N29",
                "N29 first bridge",
            ],
            source_digest_or_title_record={
                "record_type": "context_record_only",
                "source_repo_id": "reflexive-coherence-agentic-ecology",
            },
            relative_path_or_repo_id="reflexive-coherence-agentic-ecology",
            claim_boundary="Future context only; no ant ecology spec opened in N20.",
            source_consumption_rule="future_context_only_until_N29",
        ),
        row(
            row_id="n20_i1_row_12_n12_n18_prerequisites_roadmap",
            source_id="N12_N18_ROADMAP",
            source_title="N12-N18 LGRC Agency Prerequisites Roadmap",
            source_role="boundary_source",
            may_consume_as=[
                "closed prerequisite stack context",
                "AP3-AP8 artifact-claim boundary source",
            ],
            must_not_consume_as=[
                "native implementation evidence",
                "primitive evidence",
                "agency proof",
            ],
            diagnostics_or_method_terms=[
                "artifact-level prerequisite stack",
                "Phase 8 unopened",
                "claim-boundary discipline",
            ],
            source_digest_or_title_record=local_record("n12_n18_roadmap"),
            relative_path_or_repo_id=LOCAL_SOURCE_PATHS["n12_n18_roadmap"],
            claim_boundary="Closed prerequisite context only; does not solve N19 gaps.",
            source_consumption_rule="historical_boundary_context_only",
        ),
        row(
            row_id="n20_i1_row_13_n12_n18_prerequisites_handoff",
            source_id="N12_N18_HANDOFF",
            source_title="N12-N18 LGRC Agency Prerequisites Handoff",
            source_role="boundary_source",
            may_consume_as=[
                "closed-stack handoff context",
                "N19 and N20 transition boundary",
            ],
            must_not_consume_as=[
                "primitive evidence",
                "Phase 8 implementation",
                "native support",
                "agency proof",
            ],
            diagnostics_or_method_terms=[
                "closed N12-N19 documentation/review stack",
                "N20-N29 roadmap transition",
            ],
            source_digest_or_title_record=local_record("n12_n18_handoff"),
            relative_path_or_repo_id=LOCAL_SOURCE_PATHS["n12_n18_handoff"],
            claim_boundary="Handoff context only; not primitive or agency evidence.",
            source_consumption_rule="historical_boundary_context_only",
        ),
    ]


def n19_boundary_status(n19_closeout: dict[str, Any]) -> dict[str, Any]:
    return {
        "full_ap3_ap8_nat4_ladder_generation_supported": bool(
            n19_closeout["full_ap3_ap8_nat4_ladder_generation_supported"]
        ),
        "current_implementation_can_generate_claimed_ap_ladder": bool(
            n19_closeout["current_implementation_can_generate_claimed_ap_ladder"]
        ),
        "claimed_ladder_generation_status": str(
            n19_closeout["claimed_ladder_generation_status"]
        ),
        "phase8_opened": bool(n19_closeout["phase8_opened"]),
        "native_support_opened": bool(n19_closeout["native_support_opened"]),
        "ap9_opened": bool(n19_closeout["ap9_opened"]),
        "boundary_source_path": LOCAL_SOURCE_PATHS["n19_closeout_artifact"],
    }


def coverage_by_ap(n19_closeout: dict[str, Any], ap_level: str) -> dict[str, Any]:
    coverage = n19_closeout["ap_level_nat4_coverage"]
    for row_data in coverage:
        if row_data.get("ap_level") == ap_level:
            return row_data
    raise KeyError(f"Missing N19 coverage for {ap_level}")


def ap_gap_map(n19_closeout: dict[str, Any]) -> dict[str, Any]:
    ap4 = coverage_by_ap(n19_closeout, "AP4")
    ap5 = coverage_by_ap(n19_closeout, "AP5")
    ap4_gap = ap4["nat4_gap_explanation"]
    ap5_gap = ap5["nat4_gap_explanation"]
    return {
        "ap4_gap_carried_forward": True,
        "ap5_gap_carried_forward": True,
        "gap_status": "carried_forward_not_resolved",
        "ap4_gap": {
            "source": [
                "N19",
                str(ap4_gap.get("source_experiment", ap4.get("source_experiment", "N14"))),
            ],
            "ap_level": "AP4",
            "best_nat_level": ap4["best_nat_level"],
            "coverage_status": ap4["coverage_status"],
            "nat4_evidence_present": ap4["nat4_evidence_present"],
            "gap": "route consequence selection is not yet source-current native policy",
            "gap_summary": "route consequence selection is not yet source-current native policy",
            "best_current_evidence": ap4_gap["best_current_evidence"],
            "source_rows": ap4_gap["source_rows"],
            "missing_for_nat4": ap4_gap["missing_for_nat4"],
            "why_this_blocks_ladder_generation": ap4_gap[
                "why_this_blocks_ladder_generation"
            ],
            "blocked_relabels": [
                "semantic_choice",
                "intention",
                "producer_preference",
            ],
            "source_specific_blockers": [
                "constructed_followout_as_native_support",
            ],
            "affected_primitives": [
                "susceptibility_update",
                "live_continuation_collapse",
            ],
        },
        "ap5_gap": {
            "source": [
                "N19",
                str(ap5_gap.get("source_experiment", ap5.get("source_experiment", "N15"))),
            ],
            "ap_level": "AP5",
            "best_nat_level": ap5["best_nat_level"],
            "coverage_status": ap5["coverage_status"],
            "nat4_evidence_present": ap5["nat4_evidence_present"],
            "gap": "proxy derivation depends on lower-stack artifact surfaces",
            "gap_summary": "proxy derivation depends on lower-stack artifact surfaces",
            "best_current_evidence": ap5_gap["best_current_evidence"],
            "source_rows": ap5_gap["source_rows"],
            "missing_for_nat4": ap5_gap["missing_for_nat4"],
            "why_this_blocks_ladder_generation": ap5_gap[
                "why_this_blocks_ladder_generation"
            ],
            "blocked_relabels": [
                "semantic_goal",
                "goal_ownership",
                "hidden_proxy_policy",
            ],
            "source_specific_blockers": [
                "readiness_only_context_as_native_support",
            ],
            "affected_primitives": [
                "proxy_divergence_proxy_collapse",
            ],
        },
        "propagation_rule": (
            "Any later primitive depending on route selection, proxy derivation, "
            "target formation, or lower-stack source-currentness must carry the "
            "relevant N19 gap until source-backed naturalization evidence removes it."
        ),
    }


def build_checks(rows: list[dict[str, Any]], artifact: dict[str, Any]) -> list[dict[str, Any]]:
    local_records = [
        record
        for row_data in rows
        for record in flatten_records(row_data["source_digest_or_title_record"])
        if record.get("record_type") == "relative_path_digest"
    ]
    arc_rows = [row_data for row_data in rows if row_data["source_id"].startswith("ARC_")]
    essay_rows = [row_data for row_data in rows if row_data["source_id"].startswith("ESSAY_")]
    checks = [
        {
            "check_id": "all_source_roles_allowed",
            "passed": all(row_data["source_role"] in ALLOWED_SOURCE_ROLES for row_data in rows),
            "detail": sorted({row_data["source_role"] for row_data in rows}),
        },
        {
            "check_id": "all_local_source_records_have_relative_paths",
            "passed": all(
                not str(record["path"]).startswith(("/", "file://")) for record in local_records
            ),
            "detail": [record["path"] for record in local_records],
        },
        {
            "check_id": "all_source_rows_have_consumption_rules",
            "passed": all(
                row_data["may_consume_as"]
                and row_data["must_not_consume_as"]
                and row_data["source_consumption_rule"]
                for row_data in rows
            ),
            "detail": len(rows),
        },
        {
            "check_id": "unsafe_claim_flags_false_per_row",
            "passed": all(
                all(value is False for value in row_data["unsafe_claim_flags"].values())
                for row_data in rows
            ),
            "detail": len(rows),
        },
        {
            "check_id": "arc_sources_method_only",
            "passed": all(
                row_data["source_role"] == "method_source"
                and "method_only" in row_data["source_consumption_rule"]
                for row_data in arc_rows
            ),
            "detail": [row_data["row_id"] for row_data in arc_rows],
        },
        {
            "check_id": "agency_essays_are_vocabulary_or_boundary_only",
            "passed": all(
                row_data["source_role"]
                in {"diagnostic_vocabulary_source", "boundary_source"}
                and any("proof" in item for item in row_data["must_not_consume_as"])
                for row_data in essay_rows
            ),
            "detail": [row_data["row_id"] for row_data in essay_rows],
        },
        {
            "check_id": "sentience_boundary_only",
            "passed": (
                artifact["sentience_opened"] is False
                and artifact["readback_claim_opened"] is False
                and any(
                    row_data["row_id"] == "n20_i1_row_10_sentience_as_readback_boundary"
                    and row_data["source_role"] == "boundary_source"
                    and "boundary_only" in row_data["source_consumption_rule"]
                    for row_data in rows
                )
            ),
            "detail": "Sentience as Read-Back is boundary-only.",
        },
        {
            "check_id": "n19_boundary_status_carried_forward",
            "passed": (
                artifact["n19_boundary_status"][
                    "full_ap3_ap8_nat4_ladder_generation_supported"
                ]
                is False
                and artifact["n19_boundary_status"][
                    "current_implementation_can_generate_claimed_ap_ladder"
                ]
                is False
                and artifact["n19_boundary_status"]["claimed_ladder_generation_status"]
                == "blocked_by_ap4_ap5_nat4_evidence_gaps"
                and artifact["n19_boundary_status"]["phase8_opened"] is False
                and artifact["n19_boundary_status"]["native_support_opened"] is False
            ),
            "detail": artifact["n19_boundary_status"],
        },
        {
            "check_id": "ap4_ap5_gap_map_started",
            "passed": (
                artifact["ap_gap_propagation_map"]["ap4_gap_carried_forward"]
                and artifact["ap_gap_propagation_map"]["ap5_gap_carried_forward"]
                and artifact["ap_gap_propagation_map"]["gap_status"]
                == "carried_forward_not_resolved"
            ),
            "detail": {
                "ap4": artifact["ap_gap_propagation_map"]["ap4_gap"][
                    "affected_primitives"
                ],
                "ap5": artifact["ap_gap_propagation_map"]["ap5_gap"][
                    "affected_primitives"
                ],
            },
        },
        {
            "check_id": "roadmap_is_not_evidence",
            "passed": any(
                row_data["row_id"] == "n20_i1_row_02_n20_n29_roadmap"
                and "roadmap_not_evidence" == row_data["source_consumption_rule"]
                for row_data in rows
            ),
            "detail": "N20-N29 roadmap defines arc order and boundaries only.",
        },
        {
            "check_id": "agentic_ecology_future_context_only",
            "passed": (
                artifact["ant_ecology_spec_opened"] is False
                and any(
                    row_data["row_id"] == "n20_i1_row_11_agentic_ecology_future_context"
                    and row_data["source_role"] == "future_application_context"
                    for row_data in rows
                )
            ),
            "detail": "N29 remains first formal ecology bridge.",
        },
        {
            "check_id": "no_primitive_evidence_or_classification_opened",
            "passed": (
                artifact["primitive_evidence_opened"] is False
                and artifact["primitive_rows_classified"] is False
                and all(
                    row_data["primitive_evidence_status"] == "not_primitive_evidence"
                    for row_data in rows
                )
            ),
            "detail": {
                "primitive_evidence_opened": artifact["primitive_evidence_opened"],
                "primitive_rows_classified": artifact["primitive_rows_classified"],
            },
        },
        {
            "check_id": "artifact_invariants_preserved",
            "passed": artifact["artifact_invariants"] == INVARIANTS,
            "detail": artifact["artifact_invariants"],
        },
        {
            "check_id": "no_absolute_paths",
            "passed": no_absolute_paths(artifact),
            "detail": "all inventory paths are relative or title records",
        },
    ]
    return checks


def flatten_records(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        records: list[dict[str, Any]] = []
        if "record_type" in value:
            records.append(value)
        for item in value.values():
            records.extend(flatten_records(item))
        return records
    if isinstance(value, list):
        records = []
        for item in value:
            records.extend(flatten_records(item))
        return records
    return []


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    slash = chr(47)
    blocked_fragments = [
        slash + "home" + slash,
        slash + "Users" + slash,
        "file:" + slash + slash,
        "C:" + "\\\\",
    ]
    return not any(fragment in text for fragment in blocked_fragments)


def render_report(artifact: dict[str, Any]) -> None:
    lines = [
        "# N20 Iteration 1 - Source And Method Inventory",
        "",
        "Status:",
        "",
        "```text",
        f"status = {artifact['status']}",
        f"acceptance_state = {artifact['acceptance_state']}",
        f"row_count = {artifact['row_count']}",
        f"primitive_evidence_opened = {str(artifact['primitive_evidence_opened']).lower()}",
        f"primitive_rows_classified = {str(artifact['primitive_rows_classified']).lower()}",
        f"agency_claim_opened = {str(artifact['agency_claim_opened']).lower()}",
        f"phase8_opened = {str(artifact['phase8_opened']).lower()}",
        f"native_support_opened = {str(artifact['native_support_opened']).lower()}",
        f"sentience_opened = {str(artifact['sentience_opened']).lower()}",
        f"ant_ecology_spec_opened = {str(artifact['ant_ecology_spec_opened']).lower()}",
        "```",
        "",
        "N19 boundary status:",
        "",
        "```text",
        "full_ap3_ap8_nat4_ladder_generation_supported = "
        + str(
            artifact["n19_boundary_status"][
                "full_ap3_ap8_nat4_ladder_generation_supported"
            ]
        ).lower(),
        "current_implementation_can_generate_claimed_ap_ladder = "
        + str(
            artifact["n19_boundary_status"][
                "current_implementation_can_generate_claimed_ap_ladder"
            ]
        ).lower(),
        "claimed_ladder_generation_status = "
        + artifact["n19_boundary_status"]["claimed_ladder_generation_status"],
        "```",
        "",
        "Source rows:",
        "",
        "| Row | Source | Role | Consumption Rule |",
        "| --- | --- | --- | --- |",
    ]
    for row_data in artifact["source_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    row_data["row_id"],
                    row_data["source_title"],
                    row_data["source_role"],
                    row_data["source_consumption_rule"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "AP4/AP5 gap propagation:",
            "",
            "```text",
            "ap4_gap_carried_forward = "
            + str(artifact["ap_gap_propagation_map"]["ap4_gap_carried_forward"]).lower(),
            "ap4_affected_primitives = "
            + ", ".join(
                artifact["ap_gap_propagation_map"]["ap4_gap"]["affected_primitives"]
            ),
            "ap5_gap_carried_forward = "
            + str(artifact["ap_gap_propagation_map"]["ap5_gap_carried_forward"]).lower(),
            "ap5_affected_primitives = "
            + ", ".join(
                artifact["ap_gap_propagation_map"]["ap5_gap"]["affected_primitives"]
            ),
            "gap_status = " + artifact["ap_gap_propagation_map"]["gap_status"],
            "```",
            "",
            "Checks:",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for check in artifact["checks"]:
        lines.append(f"| {check['check_id']} | {str(check['passed']).lower()} |")
    lines.extend(
        [
            "",
            "Claim boundary:",
            "",
            "```text",
            artifact["claim_boundary"],
            "```",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    n19_closeout = load_json(LOCAL_SOURCE_PATHS["n19_closeout_artifact"])
    rows = source_rows()
    artifact: dict[str, Any] = {
        "artifact_id": "n20_source_method_inventory",
        "schema_version": "n20_source_method_inventory_v1",
        "experiment": "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract",
        "iteration": 1,
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "purpose": (
            "Inventory N20 source, method, diagnostic, roadmap, boundary, and "
            "future-context sources before primitive classification."
        ),
        "artifact_invariants": INVARIANTS,
        "source_rows": rows,
        "row_count": len(rows),
        "n19_boundary_status": n19_boundary_status(n19_closeout),
        "ap_gap_propagation_map": ap_gap_map(n19_closeout),
        "source_role_policy": {
            "allowed_roles": sorted(ALLOWED_SOURCE_ROLES),
            "method_sources_are_not_evidence": True,
            "diagnostic_sources_are_not_proof": True,
            "boundary_sources_do_not_open_claims": True,
            "future_application_context_not_specification": True,
        },
        "primitive_evidence_opened": False,
        "primitive_rows_classified": False,
        "agency_claim_opened": False,
        "phase8_opened": False,
        "native_support_opened": False,
        "sentience_opened": False,
        "readback_claim_opened": False,
        "ant_ecology_spec_opened": False,
        "native_ant_agency_claim_opened": False,
        "native_colony_agency_claim_opened": False,
        "ready_for_iteration_2_schema": True,
        "claim_boundary": (
            "N20 Iteration 1 inventories sources and method only. It does not "
            "classify primitives, open primitive evidence, prove agency, open "
            "Phase 8, open native support, open sentience/read-back claims, or "
            "start ant ecology specifications before N29."
        ),
        "output_digest": "pending",
    }
    checks = build_checks(rows, artifact)
    failed_checks = [check["check_id"] for check in checks if not check["passed"]]
    artifact["checks"] = checks
    artifact["failed_checks"] = failed_checks
    artifact["status"] = "passed" if not failed_checks else "failed"
    artifact["acceptance_state"] = (
        "accepted_source_method_inventory_no_primitive_evidence"
        if not failed_checks
        else "failed_source_method_inventory"
    )
    digest_input = dict(artifact)
    digest_input.pop("output_digest", None)
    artifact["output_digest"] = digest_value(digest_input)
    OUTPUT.write_text(canonical_json(artifact), encoding="utf-8")
    render_report(artifact)


if __name__ == "__main__":
    main()
