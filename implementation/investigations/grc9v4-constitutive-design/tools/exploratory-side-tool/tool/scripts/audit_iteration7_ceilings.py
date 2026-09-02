#!/usr/bin/env python3
"""Independent raw-source audit of the ET-C7 claim-ceiling layer."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, file_sha256, load_json_object, record_digest  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402


def pointer_value(value: Any, pointer: str) -> Any:
    current = value
    if pointer in {"", "/"}:
        return current
    for token in pointer.removeprefix("/").split("/"):
        key = token.replace("~1", "/").replace("~0", "~")
        current = current[int(key)] if isinstance(current, list) else current[key]
    return current


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    arguments = set(sys.argv[1:])
    if arguments - {"--skip-dist-identity"}:
        raise RuntimeError(f"unsupported ET-C7 audit arguments: {sorted(arguments)}")
    skip_dist_identity = "--skip-dist-identity" in arguments
    checks = 0

    def require(condition: bool, label: str) -> None:
        nonlocal checks
        if not condition:
            raise RuntimeError(f"ET-C7 audit failed: {label}")
        checks += 1

    records = SIDE_TOOL_ROOT / "records"
    layer_path = records / "ETC7ClaimCeilingAlternativeLayer.json"
    layer = load_json_object(layer_path)
    manifest = load_json_object(records / "ETC7WebBuildManifest.json")
    gate = load_json_object(records / "ETC7ClaimCeilingAlternativeNavigation.json")
    et_c6 = load_json_object(records / "ETC6StaticNavigationSurface.json")
    source_manifest = load_json_object(records / "ETC1SourceBundleManifest.json")
    source_rows = {row["record_identifier"]: row for row in source_manifest["records"]}
    sources = {
        record_id: load_json_object(repo_root / row["path"])
        for record_id, row in source_rows.items()
    }
    topology = sources["GRC9V4-D10-CLAIM-TOPOLOGY-v2"]
    ledger = sources["GRC9V4-D10-DEBT-CLAIM-TRANSFORMATION-LEDGER-v2"]
    provenance = sources["GRC9V4-CD-D10.2-v1"]

    for path, value in (
        (layer_path, layer),
        (records / "ETC7WebBuildManifest.json", manifest),
        (records / "ETC7ClaimCeilingAlternativeNavigation.json", gate),
    ):
        require(path.read_bytes() == canonical_bytes(value) + b"\n", f"canonical:{path.name}")
    for value, field, label in (
        (layer, "layer_digest", "layer_digest"),
        (manifest, "manifest_digest", "manifest_digest"),
        (gate, "record_digest", "gate_digest"),
    ):
        require(value[field] == record_digest(value, field), label)
    require(et_c6["status"] == "accepted", "ET_C6_accepted")
    require(et_c6["record_digest"] == record_digest(et_c6, "record_digest"), "ET_C6_digest")
    require(gate["predecessor"]["record_digest"] == et_c6["record_digest"], "ET_C6_binding")
    require(layer["predecessor"]["record_digest"] == et_c6["record_digest"], "layer_ET_C6_binding")
    require(layer["status"] == manifest["status"] == gate["status"] == "accepted", "accepted_lifecycle")
    require(gate["authority"]["iteration_8_authorized"] is True, "I8_authorized")
    require(gate["acceptance_requirements"]["human_review"] == "accepted", "human_review")

    for record_id, row in source_rows.items():
        data = sources[record_id]
        require(data[row["digest_field"]] == row["canonical_digest"], f"source_digest:{record_id}")

    def verify_source_ref(source: dict[str, str], label: str) -> Any:
        require(source["record_id"] in sources, f"source_record:{label}")
        require(source["record_digest"] == source_rows[source["record_id"]]["canonical_digest"], f"source_digest_ref:{label}")
        value = pointer_value(sources[source["record_id"]], source["source_json_pointer"])
        require(value is not None, f"source_pointer:{label}")
        return value

    locks = {row["lock_id"]: row for row in layer["locks"]}
    require(len(locks) == len(layer["locks"]) == 90, "lock_population")
    require(layer["population_counts"] == {
        "locks": 90,
        "alternatives": 144,
        "negative_claims": 6,
        "object_blocked_overreads": 67,
        "provenance_blocked_relabels": 9,
        "targeted_hardenings": 8,
    }, "population_counts")
    lock_classes = Counter(row["lock_class"] for row in locks.values())
    require(lock_classes == Counter({
        "normative_object_blocked_overread": 67,
        "provenance_blocked_relabel": 9,
        "targeted_provenance_hardening": 8,
        "accepted_negative_claim": 6,
    }), "lock_classes")

    source_negative = {row["claim_id"]: row for row in topology["claims"] if row["claim_class"] == "negative"}
    for claim_id, claim in source_negative.items():
        lock = locks[f"negative:{claim_id}"]
        require(lock["stronger_blocked_claims"] == claim["blocked_relabels"], f"negative_relabels:{claim_id}")
        require(lock["bearing_debt_ids"] == claim["bearing_debt_ids"], f"negative_debts:{claim_id}")
        require(lock["source_reason"] == claim["statement"], f"negative_reason:{claim_id}")

    for value in provenance["normatively_load_bearing_objects"]:
        object_id = value["object_id"]
        lock = locks[f"object_overread:{object_id}"]
        require(lock["stronger_blocked_claims"] == [value["blocked_overread"]], f"object_overread:{object_id}")
        require(lock["target_node_ids"] == [f"normative_object:{object_id}"], f"object_target:{object_id}")

    hardening = provenance["targeted_type_and_provenance_hardening"]
    require(set(hardening) == {
        "core_K_vs_graph_K4",
        "M4_ontology",
        "Candidate_A_profile_scope",
        "Candidate_A_future_curvature_rule",
        "migration_split",
        "reference_Hodge_embedding",
        "differential_backend_scope",
        "destination_semantics",
    }, "hardening_keys")
    for key, value in hardening.items():
        lock = locks[f"hardening:{key}"]
        require(lock["hardening"] == {"key": key, "machine_value": value}, f"hardening:{key}")
        require(lock["source_reason"] == value, f"hardening_reason:{key}")
    require(locks["hardening:Candidate_A_future_curvature_rule"]["reopening_boundary_status"] == "source_named", "future_curvature_reopening")

    allowed_reason_kinds = {"evidence", "derivation", "contradiction", "routing", "out_of_scope"}
    for lock_id, lock in locks.items():
        require(lock["authority_status"] == "accepted_source_lock", f"lock_authority:{lock_id}")
        require(lock["promotion_allowed"] is False, f"lock_promotion:{lock_id}")
        require(lock["readable_annotation"] == {
            "authority": "non_authoritative_readability_annotation",
            "text": lock["source_reason"].replace("_", " "),
        }, f"annotation:{lock_id}")
        verify_source_ref(lock["source"], f"lock:{lock_id}")
        reason_value = verify_source_ref(lock["source_reason_ref"], f"reason:{lock_id}")
        for reason in lock["source_reason_kinds"]:
            require(reason["kind"] in allowed_reason_kinds, f"reason_kind:{lock_id}")
            exact = pointer_value(sources[lock["source_reason_ref"]["record_id"]], reason["source_json_pointer"])
            if reason["kind"] == "evidence":
                require(isinstance(exact, list) and bool(exact), f"reason_evidence:{lock_id}")
            else:
                require(reason["source_value"] in str(exact).lower(), f"reason_literal:{lock_id}")
        require(reason_value is not None, f"reason_value:{lock_id}")
        for boundary in lock["reopening_boundary_set"]:
            exact = pointer_value(sources[boundary["source_record_id"]], boundary["source_json_pointer"])
            require(exact == boundary["boundary_id"], f"boundary_exact:{lock_id}")

    alternatives = {row["alternative_id"]: row for row in layer["alternatives"]}
    require(len(alternatives) == len(layer["alternatives"]) == 144, "alternative_population")
    require(Counter(row["alternative_class"] for row in alternatives.values()) == Counter({
        "blocked_relabel": 96,
        "historical_claim": 29,
        "conditional_claim": 12,
        "rejected_alternative": 5,
        "routed_candidate": 1,
        "rejected_candidate": 1,
    }), "alternative_classes")
    for alternative_id, row in alternatives.items():
        require(row["promotion_allowed"] is False, f"alternative_promotion:{alternative_id}")
        require(row["ghost_style_required"] is True, f"alternative_style:{alternative_id}")
        require(row["presentation_order_semantic"] == "staged_disclosure_not_rank_priority_or_evidence_strength", f"alternative_order:{alternative_id}")
        verify_source_ref(row["source"], f"alternative:{alternative_id}")
    require(alternatives["routed:V4-B-independent-derived-carrier"]["immutable_status"] == "routed_not_rejected_no_lifecycle_profile", "B_routed")
    require(alternatives["rejected:V4-D-source-admitted-structural"]["immutable_status"] == "resolved_negative_uninstantiated_slot", "D_slot")

    careers = layer["candidate_careers"]
    require(set(careers) == {"V4-A-temporalized-W", "V4-B-independent-derived-carrier", "V4-C-constitutive-C-sector"}, "career_population")
    for candidate_id, career in careers.items():
        require(career["operation"] == "candidate_career", f"career_operation:{candidate_id}")
        for row in career["rows"]:
            verify_source_ref(row["source_ref"], f"career:{candidate_id}:{row['row_id']}")
    require(any(row["classification"] == "narrowed" for row in careers["V4-A-temporalized-W"]["rows"]), "A_narrowed")
    require(any(row["classification"] == "current_tranche_closed_missing_constitutive_derivation" for row in careers["V4-B-independent-derived-carrier"]["rows"]), "B_terminal_route")
    require(any(row["classification"] == "D7G_eligible_complete_candidate_transition" for row in careers["V4-C-constitutive-C-sector"]["rows"]), "C_D7G")

    readmission = layer["candidate_B_readmission"]
    require(readmission["earliest_counterfactual_reexecution_gate_ids"] == ["GRC9V4-CD-D7V2-v1"], "B_earliest_counterfactual_gate")
    require(readmission["accepted_route_boundary"] == "derive_and_admit_U_B_then_reopen_D2_through_D9_for_B", "B_route_boundary")
    require(readmission["outcome_status"] == "open_work_not_promised_success", "B_no_success_promise")
    require(layer["authority_populations"] == {
        "current_debt_transformations": 29,
        "verification_obligations": 11,
        "historical_claims": 29,
        "classification": "separate_populations_not_priority_or_current_blocker_score",
    }, "authority_populations")

    serialized = canonical_bytes(layer).decode("ascii")
    for forbidden in ('"score"', '"rank"', '"priority"'):
        require(forbidden not in serialized, f"hidden_ranking_field:{forbidden}")
    require(layer["authority"]["slider_changes_presentation_only"] is True, "slider_presentation")
    require(layer["authority"]["browser_scenario_serialization"] is False, "scenario_immutable")

    dist = TOOL_ROOT / "web/dist"
    require(manifest["claim_ceiling_layer_digest"] == layer["layer_digest"], "manifest_layer")
    require(manifest["base_static_bundle_digest"] == et_c6["compiled_surface"]["static_bundle_digest"], "manifest_base")
    require(manifest["file_count"] == len(manifest["files"]), "manifest_count")
    if not skip_dist_identity:
        for row in manifest["files"]:
            path = dist / row["path"]
            require(path.is_file(), f"dist_file:{row['path']}")
            require(path.stat().st_size == row["size_bytes"], f"dist_size:{row['path']}")
            require(file_sha256(path) == row["sha256"], f"dist_sha:{row['path']}")

    print(
        "ET_C7_AUDIT_PASS "
        f"checks={checks} locks={len(locks)} alternatives={len(alternatives)} "
        f"careers={len(careers)} "
        f"dist={'historical_skipped' if skip_dist_identity else 'exact'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
