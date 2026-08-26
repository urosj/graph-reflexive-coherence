#!/usr/bin/env python3
"""Audit the bounded GRC9V4 D10.1 preliminary provenance record."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
DECISIONS = ROOT / "implementation/investigations/grc9v4-constitutive-design/decisions"
RECORD_PATH = DECISIONS / "D10_1PreliminarySubstrateProvenance.json"
REPORT_PATH = DECISIONS / "D10_1PreliminarySubstrateProvenance.md"


def canonical_digest(data: dict[str, Any], digest_field: str) -> str:
    payload = {key: value for key, value in data.items() if key != digest_field}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


record = json.loads(RECORD_PATH.read_text())
report = REPORT_PATH.read_text()
checks: list[tuple[str, bool]] = []


def check(name: str, condition: bool) -> None:
    checks.append((name, bool(condition)))


check(
    "record_digest",
    record["decision_record_digest"]
    == canonical_digest(record, "decision_record_digest"),
)
check(
    "status_accepted",
    record["status"]
    == "accepted_preliminary_bounded_substrate_provenance_separation",
)
check(
    "human_acceptance_bound",
    record["human_acceptance"]
    == "accepted_preliminary_bounded_substrate_provenance_separation_2026-08-26",
)
check(
    "accepted_D10_predecessor",
    record["predecessor_decision_digest"]
    == "3e673b335ad428d01006f231765d060a9bdd5f134332b143048f774de94bad00",
)

source_ids = {row["source_id"] for row in record["source_identities"]}
check("source_count_16", len(record["source_identities"]) == 16)
check("source_ids_unique", len(source_ids) == 16)
for row in record["source_identities"]:
    path = ROOT / row["path"]
    check(f"source_exists:{row['source_id']}", path.is_file())
    check(f"source_SHA:{row['source_id']}", row["file_sha256"] == file_sha(path))
    check(f"source_repo_relative:{row['source_id']}", not Path(row["path"]).is_absolute())
    if "source_digest" in row:
        data = json.loads(path.read_text())
        digest_field = (
            "decision_record_digest"
            if "decision_record_digest" in data
            else "artifact_digest"
        )
        check(
            f"source_digest:{row['source_id']}",
            row["source_digest"] == data[digest_field]
            == canonical_digest(data, digest_field),
        )

findings = record["preliminary_findings"]
check("finding_ids_exact", {row["finding_id"] for row in findings} == {f"D10.1-P{i}" for i in range(1, 6)})
check("finding_count_5", len(findings) == 5)

schema = record["classification_schema"]
allowed_dispositions = set(schema["substrate_dispositions"])
allowed_promotions = set(schema["promotion_statuses"])
check(
    "substrate_dispositions_exact",
    allowed_dispositions
    == {
        "core_substrate_independent",
        "GRC_derived",
        "GRC9V3_derived_GRC_rederivation_required",
        "GRC9_specialization_specific",
        "GRC9_intrinsic",
    },
)
check(
    "promotion_statuses_exact",
    allowed_promotions == {"promotion_proved", "promotion_pending", "specialization_only"},
)

rows = record["representative_provenance_rows"]
check("representative_row_count_12", len(rows) == 12)
check("object_ids_unique", len({row["object_id"] for row in rows}) == len(rows))
required_row_fields = {
    "object_id",
    "object_kind",
    "premises_used",
    "source_lineage",
    "substrate_disposition",
    "promotion_status",
    "current_finding",
    "evidence_refs",
}
check("all_row_fields_present", all(required_row_fields <= set(row) for row in rows))
check("all_row_dispositions_valid", all(row["substrate_disposition"] in allowed_dispositions for row in rows))
check("all_row_promotions_valid", all(row["promotion_status"] in allowed_promotions for row in rows))
check("all_evidence_refs_resolve", all(set(row["evidence_refs"]) <= source_ids for row in rows))
check("all_source_lineage_refs_resolve", all(set(row["source_lineage"]) <= source_ids for row in rows))
check("GRC9_intrinsic_present", any(row["substrate_disposition"] == "GRC9_intrinsic" for row in rows))
check("GRC9_specialization_specific_present", any(row["substrate_disposition"] == "GRC9_specialization_specific" for row in rows))
check("GRC9V3_derived_present", any(row["substrate_disposition"] == "GRC9V3_derived_GRC_rederivation_required" for row in rows))
check("GRC_derived_present", any(row["substrate_disposition"] == "GRC_derived" for row in rows))
check("no_promotion_proved_rows", not any(row["promotion_status"] == "promotion_proved" for row in rows))
compatibility_row = next(
    row for row in rows
    if row["object_id"] == "legacy_disabled_transition_and_lifecycle_reduction"
)
check(
    "disabled_reduction_is_specialization_specific",
    compatibility_row["substrate_disposition"] == "GRC9_specialization_specific"
    and compatibility_row["promotion_status"] == "specialization_only",
)
gw_row = next(row for row in rows if row["object_id"] == "A_instantaneous_conductance_target_G_W")
check("G_W_functional_form_inherited", "inherited_GRC9V3_conductance_functional" in gw_row["premises_used"])
check("G_W_pre_read_staging_uses_fresh_J0", "enabled_A_pre_read_uses_fresh_J0_A_not_incoming_stored_current" in gw_row["premises_used"])
check("G_W_writer_staging_is_postcontinuity", "enabled_A_writer_uses_postcontinuity_C_and_solved_JC_A" in gw_row["premises_used"])

general_charge_row = next(row for row in rows if row["object_id"] == "general_GRC_continuity_and_charge_covector_accounting")
unit_charge_row = next(row for row in rows if row["object_id"] == "unit_measure_Q_equals_sum_C_reference_profile")
check("general_charge_is_GRC_derived", general_charge_row["substrate_disposition"] == "GRC_derived")
check("unit_measure_charge_is_reference_profile", unit_charge_row["object_kind"] == "current_reference_profile_contract" and unit_charge_row["promotion_status"] == "specialization_only")

realization_row = next(row for row in rows if row["object_id"] == "CI_OS_RG2b_PC_and_CI_PC_realization_contracts")
direct_realization_sources = {
    "GRC9V4-GTRS-CI-v1",
    "GRC9V4-GTRS-OS-v1",
    "GRC9V4-GTRS-RG-v1",
    "GRC9V4-GTRS-PC-v1",
    "GRC9V4-GTRS-CI-PC-v1",
}
check("realization_sources_bound_directly", direct_realization_sources <= set(realization_row["evidence_refs"]))

scope = record["scope"]
decision = record["decision"]
authorization = record["authorization_effect"]
factorization = record["working_factorization_hypothesis"]
check("D10_claim_topology_unchanged", scope["D10_claim_topology_unchanged"] is True)
check("audit_incomplete", scope["equation_by_equation_audit_complete"] is False)
check("promotion_not_proved", scope["promotion_proved"] is False and factorization["promotion_proved"] is False)
check("final_identity_open", scope["final_substrate_identity_closed"] is False)
check("GRC9V3_load_bearing", decision["GRC9V3_provenance_load_bearing"] is True)
check("nine_port_necessity_not_established", decision["intrinsic_nine_port_necessity_established"] is False)
check("nine_ports_unnecessary_not_established", decision["nine_ports_unnecessary_established"] is False)
check("final_audit_not_replaced", decision["final_audit_replaced"] is False)
check("lineage_authorization_unchanged", authorization["D10_lineage_local_specification_authorization_unchanged"] is True)
check("GRCV4_spec_not_authorized", authorization["GRCV4_specification_authorized"] is False)
check("implementation_not_authorized", authorization["implementation_authorized"] is False)
check("runtime_src_unchanged", authorization["runtime_or_src_changed"] is False)
check("final_audit_still_required", record["final_audit_handoff"]["still_required"] is True)
check("only_final_audit_open", record["open_obligations"] == ["D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT"])
check("control_count_15", len(record["controls"]) == 15 == len(set(record["controls"])))

taxonomy = record["taxonomy_contract"]
check("GRCV3_is_general_graph_GRC", taxonomy["GRCV3"] == "general_graph_GRC_without_the_nine_port_specialization")
check("GRC9V3_is_nine_port_specialization", taxonomy["GRC9V3"] == "nine_port_specialization_profile_of_GRCV3")
check("GraphGRCV4_not_distinct_family", taxonomy["historical_D10_generic_Graph_GRC_V4_phrase"] == "descriptive_reference_to_GRCV4_not_a_distinct_naming_family")

check("report_has_digest", record["decision_record_digest"] in report)
check("report_has_factorization", "GRCV4 ->[nine-port specialization] GRC9V4 ->[disabled V4 profile] GRC9V3" in report)
check("report_defines_GRCV3_taxonomy", "`GRCv3` for general graph GRC" in report)
check("report_maps_historical_name", "does not introduce a separate `GraphGRCV4` naming family" in report)
check("report_blocks_promotion", "promotion_proved = false" in report)
check("report_keeps_final_audit", "final pre-closure audit" in report)
check("report_says_lineage_not_intrinsic", "does not assert that the new V4 constitutive architecture intrinsically requires nine ports" in report)

failed = [name for name, passed in checks if not passed]
print(f"D10.1 audit: {len(checks) - len(failed)}/{len(checks)} checks passed")
if failed:
    for name in failed:
        print(f"FAIL {name}")
    raise SystemExit(1)
