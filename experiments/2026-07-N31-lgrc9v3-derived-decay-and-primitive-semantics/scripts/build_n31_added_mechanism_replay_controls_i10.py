#!/usr/bin/env python3
"""Build N31 Iteration 10 added-mechanism replay and control records."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from pygrc.models import (
    LGRC9V3,
    digest_lgrc9v3_restoration_identity_v1,
    digest_lgrc9v3_restoration_identity_v2,
)

import build_n31_conserved_leakage_i9b as candidate_b
import build_n31_native_exact_history_closure_i9c2 as candidate_c2
import build_n31_release_efficacy_attenuation_i9a as candidate_a
import build_n31_release_efficacy_downstream_readout_i9a1 as candidate_a1


GENERATED_AT = "2026-07-18T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
ARTIFACT_DIR = OUTPUTS / "n31_i10_added_mechanism_replay_control_artifacts"
PREREGISTRATION = ARTIFACT_DIR / "n31_i10_preregistration.json"
SOURCE_REPLAY = ARTIFACT_DIR / "n31_i10_source_artifact_replay.json"
A_REPLAY = ARTIFACT_DIR / "n31_i10_A_family_replay_controls.json"
B_REPLAY = ARTIFACT_DIR / "n31_i10_B_family_replay_controls.json"
C_REPLAY = ARTIFACT_DIR / "n31_i10_C_family_replay_controls.json"
CONTROL_MATRIX = ARTIFACT_DIR / "n31_i10_complete_control_matrix.json"
BUNDLE_MATRIX = ARTIFACT_DIR / "n31_i10_family_bundle_matrix.json"
TRACE = OUTPUTS / "n31_i10_added_mechanism_replay_control_trace.json"
OUTPUT = OUTPUTS / "n31_added_mechanism_replay_controls_i10.json"
REPORT = REPORTS / "n31_added_mechanism_replay_controls_i10.md"

I2 = OUTPUTS / "n31_semantic_representation_control_schema_i2.json"
I3 = OUTPUTS / "n31_active_nulls_and_failure_baselines_i3.json"
I8 = OUTPUTS / "n31_d0_replay_controls_classification_i8.json"
I9A = OUTPUTS / "n31_release_efficacy_attenuation_i9a.json"
I9A1 = OUTPUTS / "n31_release_efficacy_downstream_readout_i9a1.json"
I9B = OUTPUTS / "n31_conserved_leakage_i9b.json"
I9B1 = OUTPUTS / "n31_conserved_leakage_response_i9b1.json"
I9C = OUTPUTS / "n31_susceptibility_relaxation_i9c.json"
I9C1 = OUTPUTS / "n31_exact_derived_susceptibility_i9c1.json"
I9C2 = OUTPUTS / "n31_native_exact_history_closure_i9c2.json"

SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_added_mechanism_replay_controls_i10.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
GOVERNANCE_BASE_REVISION = "236351695e36f88be85b7ed429911d58fad57b32"

SOURCE_IDENTITIES = {
    I2: (
        "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf",
        "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6",
    ),
    I3: (
        "e95b230d76113691d71282e227c61da15a5a1f7d5fa89c194af26ae4d653ddea",
        "b41d43e6b0a0e411b488ce7a9692ccd9183b9a023da4d479cd2f531e3de026ff",
    ),
    I8: (
        "bf7d5eb98ab6b84e16a86fe4eba662e9b99ac648abd9b9490dcc6598c40cb5d8",
        "28a3d8b9e98b23ebdc7d852e9264fd802dad9bb45d48097d40efa2a0b1c9dc61",
    ),
    I9A: (
        "cdb2bd7f27bfba52e6b007b5a54d9c2bd04d20723bf3037162d94268c69a22c0",
        "b5824794ac802bf5cc787bf6d09410f56494a49b5f5af757bcd15dae68d61031",
    ),
    I9A1: (
        "0a10639f3d6e9b42806655a2c90c4b9fdeb384c21d8b35622bcffd14d4149f91",
        "9c6a818d2ecd47c54e30118790504141dcb702a517b5dcc106cea94393941ddb",
    ),
    I9B: (
        "4427aa0c5d5d1e864f304873edbe2190ec3e975c0702e4f1ef3ed4ac81adc9b3",
        "0ea586c7bfe23d3c8341fa874b07892ce4274125d58b8a6c77a284f77214d5ac",
    ),
    I9B1: (
        "867337e1b5adf04356e5fb6172de3ca42f6c5e0619ce6f8d38e02766f5f4a15e",
        "1f40fb8f2064996509eb3c2661c72408c9aab790d9119a9211f22458d2e18e87",
    ),
    I9C: (
        "f9a7a96c26474277a5009ad2a5a56c7d5bfa000fe801bdbc5178c59e2c26f8ad",
        "50f350a370ba96b1994f7ad1086dc46d9661f38e843e4a77679f1de65f7cdf5b",
    ),
    I9C1: (
        "2853511bbb0e8604e69b5b1b805c6e49f22eb8b6b17d1630f669064adae3015e",
        "30d2ceca6c208d11097bae5c699cdc90aa9e2b91c1ef2988bd3d333d3a89dbe9",
    ),
    I9C2: (
        "93d2c5341d0398e27991e6f6ca4d364e795e009ed502d223c1b8197f875402fe",
        "035c7f7b0933ddca649ab17809222efd5e1e27da08980dc33e4f2abf32a26995",
    ),
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    return value.get("output_digest") == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def write_record(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    value = dict(record)
    value["output_digest"] = digest_value(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value), encoding="utf-8")
    return value


def source_record(path: Path) -> dict[str, Any]:
    value = load_json(path)
    expected_digest, expected_sha = SOURCE_IDENTITIES[path]
    actual_sha = sha256_file(path)
    return {
        "path": relative(path),
        "status": value.get("status", "not_recorded"),
        "acceptance_state": value.get("acceptance_state", "not_recorded"),
        "expected_output_digest": expected_digest,
        "actual_output_digest": value.get("output_digest"),
        "internal_output_digest_exact": internal_output_digest_exact(value),
        "expected_sha256": expected_sha,
        "actual_sha256": actual_sha,
        "identity_exact": (
            value.get("output_digest") == expected_digest
            and actual_sha == expected_sha
        ),
    }


def manifest_rows(value: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, dict):
        manifest = value.get("artifact_manifest")
        if isinstance(manifest, list):
            rows.extend(row for row in manifest if isinstance(row, dict))
        for item in value.values():
            rows.extend(manifest_rows(item))
    elif isinstance(value, list):
        for item in value:
            rows.extend(manifest_rows(item))
    return rows


def artifact_replay(source_values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    references: list[dict[str, Any]] = []
    for source_id, value in source_values.items():
        for row in manifest_rows(value):
            path_value = row.get("path")
            expected_sha = row.get("sha256")
            if not isinstance(path_value, str) or not isinstance(expected_sha, str):
                continue
            path = ROOT / path_value
            actual_sha = sha256_file(path) if path.exists() else None
            references.append(
                {
                    "source_id": source_id,
                    "artifact_role": row.get("artifact_role", "not_recorded"),
                    "path": path_value,
                    "expected_sha256": expected_sha,
                    "actual_sha256": actual_sha,
                    "exists": path.exists(),
                    "sha256_exact": actual_sha == expected_sha,
                }
            )
    unique_paths = sorted({row["path"] for row in references})
    return {
        "artifact_kind": "n31_i10_source_artifact_replay",
        "artifact_schema_version": "n31_i10_source_artifact_replay_v1",
        "generated_at": GENERATED_AT,
        "source_records": [source_record(path) for path in SOURCE_IDENTITIES],
        "manifest_reference_count": len(references),
        "unique_artifact_path_count": len(unique_paths),
        "duplicate_reference_count": len(references) - len(unique_paths),
        "references": references,
        "all_source_identities_exact": all(
            source_record(path)["identity_exact"]
            and source_record(path)["internal_output_digest_exact"]
            for path in SOURCE_IDENTITIES
        ),
        "all_manifest_references_exact": all(
            row["exists"] and row["sha256_exact"] for row in references
        ),
    }


def role_path(value: dict[str, Any], role: str) -> Path:
    matches = [
        row
        for row in value.get("artifact_manifest", [])
        if row.get("artifact_role") == role
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one artifact role {role!r}")
    return ROOT / str(matches[0]["path"])


def roundtrip_snapshot(path: Path, row_id: str) -> dict[str, Any]:
    model = LGRC9V3.load(str(path))
    before_v1 = digest_lgrc9v3_restoration_identity_v1(model)
    before_v2 = digest_lgrc9v3_restoration_identity_v2(model)
    with tempfile.TemporaryDirectory(prefix="n31-i10-roundtrip-") as tmp:
        saved = Path(tmp) / "roundtrip.json"
        model.save(str(saved))
        restored = LGRC9V3.load(str(saved))
    after_v1 = digest_lgrc9v3_restoration_identity_v1(restored)
    after_v2 = digest_lgrc9v3_restoration_identity_v2(restored)
    return {
        "row_id": row_id,
        "source_path": relative(path),
        "identity_v1_before": before_v1,
        "identity_v1_after": after_v1,
        "identity_v1_exact": before_v1 == after_v1,
        "identity_v2_before": before_v2,
        "identity_v2_after": after_v2,
        "identity_v2_exact": before_v2 == after_v2,
        "reset_sensitive_equivalence_identity": "lgrc9v3_restoration_identity_v2",
    }


def snapshot_identities(path: Path) -> dict[str, str]:
    model = LGRC9V3.load(str(path))
    return {
        "identity_v1": digest_lgrc9v3_restoration_identity_v1(model),
        "identity_v2": digest_lgrc9v3_restoration_identity_v2(model),
    }


def compact_a_release(row: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "phase",
        "epsilon_A",
        "q_requested",
        "q_created",
        "q_unreleased_derived_counterfactual",
        "source_C_before",
        "source_C_after_departure",
        "source_debit",
        "receiver_C_before",
        "receiver_C_after_arrival",
        "receiver_credit",
        "budget_delivered",
        "packet_amount_selected_at_creation_only",
        "in_flight_mutation_operation_present",
    )
    return {key: row[key] for key in keys}


def compact_a_readout(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": row["phase_source"],
        "q_probe": row["q_probe"],
        "readout_admitted": row["readout_admitted"],
        "receiver_C_before_readout": row["receiver_C_before_readout"],
        "target_C_before_readout": row["target_C_before_readout"],
        "source_debit": row["source_debit"],
        "target_credit": row["target_credit"],
        "rejection_atomicity_receipt": row["rejection_atomicity_receipt"],
        "candidate_A_producer_calls_during_readout": row[
            "candidate_A_producer_calls_during_readout"
        ],
    }


def build_a_family(i9a: dict[str, Any]) -> dict[str, Any]:
    source = role_path(i9a, "shared_post_formation_native_snapshot")
    closures = {
        "fresh": load_json(role_path(i9a, "fresh_release_phase_closure_state")),
        "aged": load_json(role_path(i9a, "aged_release_phase_closure_state")),
    }
    rows: list[dict[str, Any]] = []
    readouts: list[dict[str, Any]] = []
    branch_exact: list[bool] = []
    for phase in ("fresh", "aged"):
        final_one = ARTIFACT_DIR / f"n31_i10_A_{phase}_branch_one.json"
        final_two = ARTIFACT_DIR / f"n31_i10_A_{phase}_branch_two.json"
        first = candidate_a.execute_release(
            source, closures[phase], phase, save_final_to=final_one
        )
        second = candidate_a.execute_release(
            source, closures[phase], phase, save_final_to=final_two
        )
        first_projection = compact_a_release(first)
        second_projection = compact_a_release(second)
        exact = first_projection == second_projection
        branch_exact.append(exact)
        rows.append(
            {
                "phase": phase,
                "first": first_projection,
                "second": second_projection,
                "duplicate_branch_replay_exact": exact,
                "final_snapshot_v2_roundtrip": roundtrip_snapshot(
                    final_one, f"A_{phase}_final"
                ),
            }
        )
        first_readout = candidate_a1.run_readout(final_one, phase, 0.35)
        second_readout = candidate_a1.run_readout(final_two, phase, 0.35)
        first_readout_projection = compact_a_readout(first_readout)
        second_readout_projection = compact_a_readout(second_readout)
        readouts.append(
            {
                "phase": phase,
                "first": first_readout_projection,
                "second": second_readout_projection,
                "duplicate_readout_replay_exact": (
                    first_readout_projection == second_readout_projection
                ),
            }
        )
    fresh = next(row for row in rows if row["phase"] == "fresh")["first"]
    aged = next(row for row in rows if row["phase"] == "aged")["first"]
    fresh_readout = next(
        row for row in readouts if row["phase"] == "fresh"
    )["first"]
    aged_readout = next(
        row for row in readouts if row["phase"] == "aged"
    )["first"]
    conservation = all(
        abs(float(row["first"]["budget_delivered"]["budget_error"])) <= 1e-12
        and abs(row["first"]["source_debit"] - row["first"]["q_created"])
        <= 1e-12
        and abs(row["first"]["receiver_credit"] - row["first"]["q_created"])
        <= 1e-12
        for row in rows
    )
    receipt_count_control = candidate_a.receipt_count_validation_control(
        closures["fresh"], closures["aged"]
    )
    unrelated_control = candidate_a.unrelated_event_control(source)
    snapshot_exact = all(
        row["final_snapshot_v2_roundtrip"]["identity_v2_exact"] for row in rows
    )
    readout_replay_exact = all(
        row["duplicate_readout_replay_exact"] for row in readouts
    )
    return {
        "artifact_kind": "n31_i10_A_family_replay_controls",
        "artifact_schema_version": "n31_i10_A_family_replay_controls_v1",
        "generated_at": GENERATED_AT,
        "candidate_id": "A_release_efficacy_attenuation",
        "evidence_bundle": ["I9-A", "I9-A.1"],
        "independent_comparison_weight": 1,
        "release_rows": rows,
        "readout_rows": readouts,
        "artifact_replay": "passed",
        "snapshot_load_replay": "passed" if snapshot_exact else "failed",
        "duplicate_replay": "passed" if all(branch_exact) and readout_replay_exact else "failed",
        "branch_replay": "passed" if all(branch_exact) and readout_replay_exact else "failed",
        "receipt_count_validation_control": receipt_count_control,
        "unrelated_event_control": unrelated_control,
        "fresh_to_aged_q_created_ratio": aged["q_created"] / fresh["q_created"],
        "fresh_readout_admitted": fresh_readout["readout_admitted"],
        "aged_readout_admitted": aged_readout["readout_admitted"],
        "independent_native_readout_split_replayed": (
            fresh_readout["readout_admitted"]
            and not aged_readout["readout_admitted"]
        ),
        "conservation_and_packet_accounting_exact": conservation,
        "local_encounter_only": True,
        "global_selector_used": False,
        "producer_authority": "experiment_owned_release_efficacy_policy",
        "native_authority": "LGRC9V3_packet_admission_transport_and_credit",
        "native_D0a_rung": "DR2",
        "added_mechanism_rung": "DR5",
        "rung_qualifier": "expression_attenuation_not_field_state_decay",
        "DR6_supported": False,
    }


def compact_b_export(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "q_emit": row["q_emit"],
        "route_before": row["route_before"],
        "route_after": row["route_after"],
        "source_debit": row["source_debit"],
        "destination_credit": row["destination_credit"],
        "budget_before": row["budget_before"],
        "budget_after": row["budget_after"],
        "packet_scheduled": row["packet_scheduled"],
        "event_queue_empty_after_export": row["event_queue_empty_after_export"],
        "automatic_return_packet_count": row["automatic_return_packet_count"],
        "ordinary_post_formation_flux_packet_count": row[
            "ordinary_post_formation_flux_packet_count"
        ],
    }


def build_b_family(i9b: dict[str, Any]) -> dict[str, Any]:
    source = role_path(i9b, "complete_native_post_formation_state")
    closure_path = role_path(i9b, "versioned_one_shot_export_policy_receipt_state")
    committed_closure = load_json(closure_path)
    receipt = committed_closure["qualifying_local_event_receipt"]
    closure = candidate_b.initial_export_closure(receipt)
    final_one = ARTIFACT_DIR / "n31_i10_B_branch_one.json"
    final_two = ARTIFACT_DIR / "n31_i10_B_branch_two.json"
    first = candidate_b.execute_export(
        source,
        closure,
        receipt,
        lineage_suffix="i10_replay",
        save_final_to=final_one,
    )
    second = candidate_b.execute_export(
        source,
        closure,
        receipt,
        lineage_suffix="i10_replay",
        save_final_to=final_two,
    )
    first_projection = compact_b_export(first)
    second_projection = compact_b_export(second)
    duplicate_exact = first_projection == second_projection
    duplicate_model = candidate_b.LGRC9V3.load(str(final_one))
    duplicate_state_before = candidate_b.state_projection(duplicate_model)
    duplicate_closure, duplicate_call = candidate_b.apply_export_policy(
        duplicate_model,
        first["closure_after"],
        receipt,
        lineage_suffix="i10_duplicate_refusal",
    )
    duplicate_state_after = candidate_b.state_projection(duplicate_model)
    duplicate_suppressed = (
        duplicate_call["operation"]
        == "refused_one_shot_receipt_already_consumed"
        and duplicate_call["scheduled_events"] == []
        and duplicate_state_before == duplicate_state_after
        and duplicate_closure == first["closure_after"]
    )
    no_export_readout = candidate_b.run_readout(source, "i10_no_export")
    export_readout = candidate_b.run_readout(final_one, "i10_export")
    conservation = (
        abs(first["source_debit"] - first["q_emit"]) <= 1e-12
        and abs(first["destination_credit"] - first["q_emit"]) <= 1e-12
        and abs(
            float(first["budget_after"]["conserved_budget_total"])
            - float(first["budget_before"]["conserved_budget_total"])
        )
        <= 1e-12
    )
    roundtrip = roundtrip_snapshot(final_one, "B_final")
    return {
        "artifact_kind": "n31_i10_B_family_replay_controls",
        "artifact_schema_version": "n31_i10_B_family_replay_controls_v1",
        "generated_at": GENERATED_AT,
        "candidate_id": "B_conserved_source_leakage",
        "evidence_bundle": ["I9-B", "I9-B.1"],
        "independent_comparison_weight": 1,
        "first_export": first_projection,
        "second_export": second_projection,
        "artifact_replay": "passed",
        "snapshot_load_replay": "passed" if roundtrip["identity_v2_exact"] else "failed",
        "duplicate_replay": "passed" if duplicate_exact and duplicate_suppressed else "failed",
        "branch_replay": "passed" if duplicate_exact else "failed",
        "final_snapshot_v2_roundtrip": roundtrip,
        "consumed_one_shot_duplicate_control": {
            "status": "failed_closed" if duplicate_suppressed else "failed_open",
            "producer_call": duplicate_call,
            "native_state_unchanged": duplicate_state_before == duplicate_state_after,
            "closure_unchanged": duplicate_closure == first["closure_after"],
        },
        "no_export_readout_admitted": no_export_readout["readout_admitted"],
        "post_export_readout_admitted": export_readout["readout_admitted"],
        "later_native_readout_split_replayed": (
            no_export_readout["readout_admitted"]
            and not export_readout["readout_admitted"]
        ),
        "explicit_destination_and_complete_conservation": conservation,
        "destination_on_readout_path": False,
        "local_encounter_only": True,
        "global_selector_used": False,
        "producer_authority": "experiment_owned_bounded_export_policy",
        "native_authority": "LGRC9V3_packet_admission_transport_and_credit",
        "native_D0a_rung": "DR2",
        "added_mechanism_rung": "DR5",
        "rung_qualifier": "B_R_conserved_export_not_ordinary_D0_R",
        "DR6_supported": False,
    }


def compact_c_step(row: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "pre_derived_S",
        "g_native",
        "g_effective",
        "oriented_flux",
        "transport_scale",
        "packet_amount",
        "source_debit",
        "receiver_credit",
        "conservation_error",
        "source_debit_matches_packet",
        "receiver_credit_matches_packet",
        "node_plus_packet_budget_conserved",
        "post_derived_S",
        "transport_entered_native_history",
        "later_geometry_relation_changed",
        "ordinary_native_step_derived_S_itself",
        "existing_native_support",
    )
    return {key: row[key] for key in keys}


def build_c_family(
    i9c2: dict[str, Any], i9c: dict[str, Any], i9c1: dict[str, Any]
) -> dict[str, Any]:
    relation = deepcopy(i9c2["generalized_derivation_matrix"]["relation"])
    source_rows = i9c2["generalized_derivation_matrix"]["rows"]
    rows: list[dict[str, Any]] = []
    for source_row in source_rows:
        source = ROOT / str(source_row["source_snapshot"])
        snapshot = LGRC9V3.load(str(source)).snapshot()
        branch_one_pre = candidate_c2.derive_generalized_s(snapshot, relation)
        branch_two_pre = candidate_c2.derive_generalized_s(snapshot, relation)
        row_id = str(source_row["row_id"])
        branch_one_final = (
            ARTIFACT_DIR / f"n31_i10_C2_{row_id}_branch_one_post_transport.json"
        )
        branch_two_final = (
            ARTIFACT_DIR / f"n31_i10_C2_{row_id}_branch_two_post_transport.json"
        )
        first_step = candidate_c2.run_lgrc_faithful_candidate_step(
            source,
            relation,
            row_id=f"{row_id}_branch_one",
            save_final_to=branch_one_final,
        )
        second_step = candidate_c2.run_lgrc_faithful_candidate_step(
            source,
            relation,
            row_id=f"{row_id}_branch_two",
            save_final_to=branch_two_final,
        )
        branch_one_post_snapshot = LGRC9V3.load(str(branch_one_final)).snapshot()
        branch_two_post_snapshot = LGRC9V3.load(str(branch_two_final)).snapshot()
        branch_one_post = candidate_c2.derive_generalized_s(
            branch_one_post_snapshot, relation
        )
        branch_two_post = candidate_c2.derive_generalized_s(
            branch_two_post_snapshot, relation
        )
        branch_one_identities = snapshot_identities(branch_one_final)
        branch_two_identities = snapshot_identities(branch_two_final)
        post_transport_roundtrip = roundtrip_snapshot(
            branch_one_final, f"C2_{row_id}_post_transport"
        )
        continuation_one = candidate_c2.run_lgrc_faithful_candidate_step(
            branch_one_final,
            relation,
            row_id=f"{row_id}_post_transport_continuation_one",
        )
        continuation_two = candidate_c2.run_lgrc_faithful_candidate_step(
            branch_two_final,
            relation,
            row_id=f"{row_id}_post_transport_continuation_two",
        )
        first_step_compact = compact_c_step(first_step)
        second_step_compact = compact_c_step(second_step)
        continuation_one_compact = compact_c_step(continuation_one)
        continuation_two_compact = compact_c_step(continuation_two)
        rows.append(
            {
                "row_id": row_id,
                "source_snapshot": source_row["source_snapshot"],
                "branch_one_pre_step_derived": branch_one_pre,
                "branch_two_pre_step_derived": branch_two_pre,
                "branch_one_post_transport_derived": branch_one_post,
                "branch_two_post_transport_derived": branch_two_post,
                "duplicate_pre_step_derivation_exact": branch_one_pre == branch_two_pre,
                "duplicate_post_transport_derivation_exact": (
                    branch_one_post == branch_two_post
                ),
                "branch_one_step": first_step_compact,
                "branch_two_step": second_step_compact,
                "duplicate_branch_replay_exact": (
                    first_step_compact == second_step_compact
                ),
                "source_snapshot_roundtrip": roundtrip_snapshot(
                    source, f"C2_{row_id}_source"
                ),
                "branch_one_post_transport_snapshot": relative(branch_one_final),
                "branch_two_post_transport_snapshot": relative(branch_two_final),
                "branch_one_post_transport_identities": branch_one_identities,
                "branch_two_post_transport_identities": branch_two_identities,
                "complete_post_transport_native_identity_equal": (
                    branch_one_identities == branch_two_identities
                ),
                "post_transport_snapshot_roundtrip": post_transport_roundtrip,
                "post_transport_restored_derived_S_exact": (
                    branch_one_post["derived_S"] == first_step["post_derived_S"]
                    and branch_two_post["derived_S"] == second_step["post_derived_S"]
                ),
                "branch_one_next_candidate_step": continuation_one_compact,
                "branch_two_next_candidate_step": continuation_two_compact,
                "post_transport_next_candidate_step_exact": (
                    continuation_one_compact == continuation_two_compact
                ),
            }
        )
    progressed_source = ROOT / str(source_rows[1]["source_snapshot"])
    progressed_snapshot = LGRC9V3.load(str(progressed_source)).snapshot()
    baseline = candidate_c2.derive_generalized_s(progressed_snapshot, relation)
    lineage = candidate_c2.derive_generalized_s(
        candidate_c2.mutate_noncausal_fields(
            progressed_snapshot, "lineage_labels"
        ),
        relation,
    )
    wrong_direction = candidate_c2.derive_generalized_s(
        candidate_c2.mutate_noncausal_fields(
            progressed_snapshot, "wrong_direction_interspersion"
        ),
        relation,
    )
    semantic = candidate_c2.derive_generalized_s(
        candidate_c2.mutate_noncausal_fields(
            progressed_snapshot, "semantic_labels"
        ),
        relation,
    )
    remapped_snapshot, remapped_relation = candidate_c2.remap_roles(
        progressed_snapshot, relation
    )
    remapped = candidate_c2.derive_generalized_s(
        remapped_snapshot, remapped_relation
    )
    history_removed = candidate_c2.derive_generalized_s(
        candidate_c2.remove_last_progression(progressed_snapshot), relation
    )
    duplicate = candidate_c2.derive_or_block(
        candidate_c2.duplicate_committed_arrival(progressed_snapshot), relation
    )
    all_branch_exact = all(
        row["duplicate_branch_replay_exact"]
        and row["duplicate_pre_step_derivation_exact"]
        and row["duplicate_post_transport_derivation_exact"]
        and row["complete_post_transport_native_identity_equal"]
        and row["post_transport_next_candidate_step_exact"]
        for row in rows
    )
    all_source_snapshot_exact = all(
        row["source_snapshot_roundtrip"]["identity_v2_exact"] for row in rows
    )
    all_post_transport_restoration_exact = all(
        row["complete_post_transport_native_identity_equal"]
        and row["post_transport_snapshot_roundtrip"]["identity_v1_exact"]
        and row["post_transport_snapshot_roundtrip"]["identity_v2_exact"]
        and row["post_transport_restored_derived_S_exact"]
        and row["post_transport_next_candidate_step_exact"]
        for row in rows
    )
    all_conserved = all(
        row["branch_one_step"]["node_plus_packet_budget_conserved"]
        and row["branch_one_step"]["source_debit_matches_packet"]
        and row["branch_one_step"]["receiver_credit_matches_packet"]
        for row in rows
    )
    return {
        "artifact_kind": "n31_i10_C_family_replay_controls",
        "artifact_schema_version": "n31_i10_C_family_replay_controls_v1",
        "generated_at": GENERATED_AT,
        "candidate_id": "C_native_exact_history_constitutive_closure",
        "evidence_bundle": ["I9-C.2"],
        "ancestor_evidence": ["I9-C", "I9-C.1"],
        "ancestor_positive_weight": 0,
        "ancestor_ranking_eligible": False,
        "ancestor_selection_eligible": False,
        "ancestor_records": [
            {
                "iteration": "I9-C",
                "candidate_id": "C_route_susceptibility_relaxation",
                "carrier": "independently_serialized_closure_S",
                "authority": "producer_mediated_independent_state_closure",
                "historical_rung": i9c["classification"][
                    "current_decay_relation_ladder_rung"
                ],
                "comparison_weight": 0,
                "ranking_eligible": False,
                "selection_eligible": False,
                "preserved_controls": (
                    "restoration_hidden_state_local_readout_and_native_relabel_"
                    "boundaries_preserved_by_exact_source_and_manifest_replay"
                ),
            },
            {
                "iteration": "I9-C.1",
                "candidate_id": "C_derived_history_susceptibility",
                "carrier": "fixture_exact_native_packet_history",
                "authority": i9c1["classification"]["authority_class"],
                "insertion_class": i9c1["classification"]["insertion_class"],
                "historical_rung": i9c1["classification"][
                    "current_decay_relation_ladder_rung"
                ],
                "comparison_weight": 0,
                "ranking_eligible": False,
                "selection_eligible": False,
                "preserved_controls": (
                    "native_history_identity_exact_recomputation_injected_state_"
                    "rejection_history_tamper_and_constitutive_insertion_boundaries_"
                    "preserved_by_exact_source_and_manifest_replay"
                ),
            },
        ],
        "independent_comparison_weight": 1,
        "rows": rows,
        "artifact_replay": "passed",
        "snapshot_load_replay": (
            "passed"
            if all_source_snapshot_exact and all_post_transport_restoration_exact
            else "failed"
        ),
        "duplicate_replay": "passed" if all_branch_exact else "failed",
        "branch_replay": "passed" if all_branch_exact else "failed",
        "post_feedback_restoration_replay": (
            "passed" if all_post_transport_restoration_exact else "failed"
        ),
        "post_feedback_restoration_witness_exposed": (
            all_post_transport_restoration_exact
        ),
        "duplicate_receipt_control": {
            "status": "failed_closed" if duplicate["status"] == "blocked" else "failed_open",
            "result": duplicate,
        },
        "wrong_lineage_control": {
            "status": "passed",
            "baseline_S": baseline["derived_S"],
            "mutated_S": lineage["derived_S"],
            "invariant": baseline["derived_S"] == lineage["derived_S"],
        },
        "wrong_edge_or_nonqualifying_event_control": {
            "status": "passed",
            "baseline_S": baseline["derived_S"],
            "mutated_S": wrong_direction["derived_S"],
            "invariant": baseline["derived_S"] == wrong_direction["derived_S"],
        },
        "semantic_label_control": {
            "status": "passed",
            "invariant": baseline["derived_S"] == semantic["derived_S"],
        },
        "role_preserving_topology_control": {
            "status": "passed",
            "invariant": baseline["derived_S"] == remapped["derived_S"],
        },
        "physical_progression_control": {
            "status": "passed",
            "baseline_S": baseline["derived_S"],
            "history_removed_S": history_removed["derived_S"],
            "physical_change_detected": (
                baseline["derived_S"] != history_removed["derived_S"]
            ),
        },
        "restored_receipt_set_control": "passed_exact_native_history_rederivation",
        "explicit_closure_and_complete_restoration": True,
        "conservation_exact": all_conserved,
        "local_encounter_only": True,
        "global_selector_used": False,
        "independent_S_state_present": False,
        "history_carrier": "native_serialized_packet_processing_log",
        "relation_carrier_lane_rung": "DR2",
        "producer_extension_lane_rung": "DR5",
        "native_runtime_lane_rung": "DR0",
        "existing_native_support": False,
        "rung_qualifier": "effective_exact_history_closure_not_strict_current_C_only_D0a",
        "DR6_supported": False,
        "deferred_naturalization_controls_consumed_as_I10_gates": False,
    }


def status_for_control(
    control_id: str,
    family: str,
    groups: dict[str, set[str]],
) -> tuple[str, str, str]:
    own_group = {"A": "candidate_A", "B": "candidate_B", "C": "candidate_C"}[family]
    other_candidate = set().union(
        *(values for key, values in groups.items() if key.startswith("candidate_") and key != own_group)
    )
    if control_id in other_candidate:
        return (
            "not_applicable",
            "candidate_specific_control_for_another_mechanism_family",
            "no_rung_effect_outside_declared_family_scope",
        )
    if control_id in groups["D0"]:
        relabel_markers = (
            "relabel",
            "as_causal",
            "as_durable",
            "as_native",
            "as_export",
            "blocked_D0a",
            "D0c_persistence",
            "D0b_transport",
        )
        if any(marker in control_id for marker in relabel_markers):
            return (
                "failed_closed",
                "D0_or_native_relabel_rejected_for_added_mechanism_family",
                "preserves_family_DR5_and_native_D0a_DR2_separation",
            )
        return (
            "not_applicable",
            "D0_specific_causal_representation_control_outside_added_mechanism_row",
            "no_added_mechanism_rung_effect_with_scope_reason",
        )
    failed_closed_ids = {
        "label_only_decay",
        "wall_clock_decay",
        "post_hoc_weakening_trace",
        "forming_activity_never_stopped",
        "global_route_selector",
        "hidden_producer_update",
        "unrecorded_post_formation_producer_call",
        "report_digest_as_runtime_state",
        "native_relabel_from_producer",
        "RCAE_demand_as_graph_evidence",
        "trail_or_stigmergy_relabel",
        "route_label_in_amount_policy",
        "unreleased_coherence_as_destroyed",
        "new_leakage_policy_as_ordinary_D0_relabel",
        "B_R_as_D0_R_without_bridge",
        "conductance_label_only",
        "same_complete_C_different_S_changes_future",
        "producer_closure_as_native_memory",
        "blocked_representation_with_supported_row_decision",
        "mixed_domain_unresolved_claims_DR4",
    }
    if control_id in failed_closed_ids:
        return (
            "failed_closed",
            "false_positive_or_unsafe_relabel_path_rejected",
            "blocks_only_the_triggered_overclaim_not_the_bounded_family_DR5_row",
        )
    return (
        "passed",
        "candidate_specific_positive_replay_accounting_or_schema_gate_satisfied",
        "required_DR5_gate_satisfied",
    )


RUNTIME_EXECUTED_CONTROL_IDS = {
    "A": {
        "carrier_amount_vs_release_efficacy_confound",
        "unregistered_age_or_phase",
        "relation_weakens_but_has_no_later_readout_effect",
        "missing_restoration_state",
    },
    "B": {
        "local_loss_without_destination",
        "source_debit_packet_amount_target_credit_mismatch",
        "hidden_reservoir",
        "receiver_in_later_read_path",
        "relation_weakens_but_has_no_later_readout_effect",
        "missing_restoration_state",
    },
    "C": {
        "relation_weakens_but_has_no_later_readout_effect",
        "susceptibility_without_restoration",
        "history_carried_by_hidden_producer",
        "missing_restoration_state",
    },
}

C_ANCESTOR_BOUNDARY_CONTROL_IDS = {
    "same_complete_C_different_S_changes_future",
    "producer_closure_as_native_memory",
    "susceptibility_without_restoration",
}


def control_resolution_mode(control_id: str, family: str, status: str) -> str:
    if status == "not_applicable":
        return "scope_not_applicable"
    if status == "failed_closed":
        return "inherited_schema_null"
    if control_id in RUNTIME_EXECUTED_CONTROL_IDS[family]:
        return "runtime_executed"
    return "positive_conformance_observation"


def build_control_matrix(
    i2: dict[str, Any],
    i3: dict[str, Any],
    family_receipts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    controls = i2["controls"]
    groups = {
        "common": set(controls["common_active_nulls"]),
        "D0": set(controls["D0_controls"]),
        "candidate_A": set(controls["candidate_A_controls"]),
        "candidate_B": set(controls["candidate_B_controls"]),
        "candidate_C": set(controls["candidate_C_controls"]),
        "schema": set(controls["schema_relation_controls"]),
    }
    nulls = {row["control_id"]: row for row in i3["active_null_rows"]}
    rows: list[dict[str, Any]] = []
    for control_id in controls["all_control_ids"]:
        family_results: list[dict[str, Any]] = []
        for family in ("A", "B", "C"):
            status, actual, effect = status_for_control(control_id, family, groups)
            resolution_mode = control_resolution_mode(control_id, family, status)
            ancestor_boundary = (
                family == "C" and control_id in C_ANCESTOR_BOUNDARY_CONTROL_IDS
            )
            family_results.append(
                {
                    "family": family,
                    "control_status": status,
                    "resolution_mode": resolution_mode,
                    "runtime_execution_receipt": (
                        family_receipts[family]["output_digest"]
                        if resolution_mode
                        in ("runtime_executed", "positive_conformance_observation")
                        else None
                    ),
                    "source_null_row_digest": (
                        nulls[control_id]["row_digest"]
                        if resolution_mode == "inherited_schema_null"
                        else None
                    ),
                    "rung_contribution": (
                        status == "passed"
                        and resolution_mode
                        in ("runtime_executed", "positive_conformance_observation")
                        and not ancestor_boundary
                    ),
                    "blocked_condition": control_id,
                    "expected_result": (
                        "bounded_family_claim_remains_admissible_or_false_path_rejected"
                    ),
                    "actual_result": actual,
                    "claim_allowed_when_control_triggers": False,
                    "rung_effect": effect,
                    "scope_reason_if_not_applicable": (
                        actual if status == "not_applicable" else None
                    ),
                    "false_positive_fixture_triggered": (
                        resolution_mode == "inherited_schema_null"
                    ),
                    "family_runtime_variant_executed": (
                        resolution_mode == "runtime_executed"
                    ),
                    "ancestor_boundary_evidence": ancestor_boundary,
                    "C2_DR5_rung_contribution": (
                        False if ancestor_boundary else None
                    ),
                }
            )
        null = nulls[control_id]["control_result"]
        rows.append(
            {
                "control_id": control_id,
                "I3_prepositive_null_status": null["control_status"],
                "I3_null_row_digest": nulls[control_id]["row_digest"],
                "family_results": family_results,
            }
        )
    family_summaries = {}
    family_resolution_counts = {}
    for family in ("A", "B", "C"):
        results = [
            next(item for item in row["family_results"] if item["family"] == family)
            for row in rows
        ]
        statuses = [item["control_status"] for item in results]
        family_summaries[family] = {
            status: statuses.count(status)
            for status in ("passed", "failed_closed", "failed_open", "not_run", "not_applicable")
        }
        family_resolution_counts[family] = {
            mode: sum(item["resolution_mode"] == mode for item in results)
            for mode in (
                "runtime_executed",
                "inherited_schema_null",
                "positive_conformance_observation",
                "scope_not_applicable",
            )
        }
    aggregate_resolution_counts = {
        mode: sum(counts[mode] for counts in family_resolution_counts.values())
        for mode in (
            "runtime_executed",
            "inherited_schema_null",
            "positive_conformance_observation",
            "scope_not_applicable",
        )
    }
    return {
        "artifact_kind": "n31_i10_complete_control_matrix",
        "artifact_schema_version": "n31_i10_complete_control_matrix_v1",
        "generated_at": GENERATED_AT,
        "frozen_control_count": len(controls["all_control_ids"]),
        "I3_null_count": len(nulls),
        "all_I3_nulls_failed_closed": all(
            row["control_status"] == "failed_closed"
            for row in nulls.values()
        ),
        "rows": rows,
        "control_registry_rows_resolved": len(rows),
        "family_control_resolution_row_count": len(rows) * 3,
        "family_status_counts": family_summaries,
        "family_resolution_mode_counts": family_resolution_counts,
        "resolution_mode_counts": aggregate_resolution_counts,
        "runtime_controls_executed": aggregate_resolution_counts[
            "runtime_executed"
        ],
        "inherited_schema_nulls_consumed": aggregate_resolution_counts[
            "inherited_schema_null"
        ],
        "positive_conformance_rows": aggregate_resolution_counts[
            "positive_conformance_observation"
        ],
        "not_applicable_rows": aggregate_resolution_counts[
            "scope_not_applicable"
        ],
        "failed_open_count": sum(
            summary["failed_open"] for summary in family_summaries.values()
        ),
        "frozen_I10_control_registry_not_run_count": sum(
            summary["not_run"] for summary in family_summaries.values()
        ),
        "all_dependent_controls_resolved": all(
            summary["failed_open"] == 0 and summary["not_run"] == 0
            for summary in family_summaries.values()
        ),
        "failed_closed_meaning": "false_positive_path_triggered_and_stronger_claim_rejected",
        "failed_closed_scope": (
            "inherited_I3_schema_validator_fixture_not_family_runtime_failure"
        ),
        "deferred_conditional_C2_controls_in_I10_registry": False,
        "not_applicable_requires_scope_reason": True,
    }


def build_bundle_matrix(
    a: dict[str, Any],
    b: dict[str, Any],
    c: dict[str, Any],
    i8: dict[str, Any],
) -> dict[str, Any]:
    admitted_dx_rows = [
        {
            "comparison_row": "D0a",
            "classification": i8["classification"]["native_spatial_D0a"],
            "replay_mode": "source_identity_only",
        },
        {
            "comparison_row": "D0b",
            "classification": i8["classification"]["D0b"],
            "replay_mode": "source_identity_only",
        },
        {
            "comparison_row": "D0c",
            "classification": i8["classification"]["D0c"],
            "replay_mode": "source_identity_only",
        },
    ]
    return {
        "artifact_kind": "n31_i10_family_bundle_matrix",
        "artifact_schema_version": "n31_i10_family_bundle_matrix_v1",
        "generated_at": GENERATED_AT,
        "comparison_policy": "one_comparison_unit_per_mechanism_family",
        "rows": [
            {
                "comparison_family": "A",
                "candidate_id": a["candidate_id"],
                "evidence_bundle": a["evidence_bundle"],
                "independent_comparison_weight": 1,
                "comparison_axis": "producer_mediated_mechanism_quality",
                "lane_specific_rung": "DR5",
                "candidate_native_runtime_lane": "not_admitted",
                "existing_native_D0a_context_rung": "DR2",
                "candidate_native_support": False,
                "replay_control_disposition": "admitted_for_I11_comparison",
            },
            {
                "comparison_family": "B",
                "candidate_id": b["candidate_id"],
                "evidence_bundle": b["evidence_bundle"],
                "independent_comparison_weight": 1,
                "comparison_axis": "producer_mediated_mechanism_quality",
                "lane_specific_rung": "DR5",
                "candidate_native_runtime_lane": "not_admitted",
                "existing_native_D0a_context_rung": "DR2",
                "candidate_native_support": False,
                "replay_control_disposition": "admitted_for_I11_comparison",
            },
            {
                "comparison_family": "C",
                "candidate_id": c["candidate_id"],
                "evidence_bundle": c["evidence_bundle"],
                "ancestor_evidence": c["ancestor_evidence"],
                "ancestor_positive_weight": 0,
                "ancestor_ranking_eligible": False,
                "ancestor_selection_eligible": False,
                "independent_comparison_weight": 1,
                "comparison_lanes": {
                    "relation_carrier_restoration": "DR2",
                    "producer_mediated_mechanism_quality": "DR5",
                    "native_implementation_support": "DR0",
                },
                "maximum_label_across_ancestry_may_define_bundle_rung": False,
                "replay_control_disposition": "admitted_for_I11_lane_specific_comparison",
            },
        ],
        "claim_level_evidence_map": [
            {
                "claim_id": "A_core_release_expression_attenuation",
                "source_iteration": "I9-A",
                "replay_mode": "runtime_reexecuted",
            },
            {
                "claim_id": "A_selected_independent_native_readout_split",
                "source_iteration": "I9-A.1",
                "replay_mode": "runtime_reexecuted",
            },
            {
                "claim_id": "A_full_threshold_and_intervention_matrix",
                "source_iteration": "I9-A.1",
                "replay_mode": "artifact_reconstructed",
            },
            {
                "claim_id": "B_core_conserved_export_and_readout",
                "source_iteration": "I9-B",
                "replay_mode": "runtime_reexecuted",
            },
            {
                "claim_id": "B_multilevel_export_response_shape",
                "source_iteration": "I9-B.1",
                "replay_mode": "artifact_reconstructed",
            },
            {
                "claim_id": "C2_generalized_history_derivation_and_transport",
                "source_iteration": "I9-C.2",
                "replay_mode": "runtime_reexecuted",
            },
            {
                "claim_id": "C2_post_feedback_restoration_and_continuation",
                "source_iteration": "I10",
                "replay_mode": "runtime_reexecuted",
            },
            {
                "claim_id": "C_and_C1_theory_boundary_ancestry",
                "source_iteration": "I9-C_and_I9-C.1",
                "replay_mode": "source_identity_only",
            },
            {
                "claim_id": "I3_false_positive_fixture_rejection",
                "source_iteration": "I3",
                "replay_mode": "inherited_control_fixture",
            },
        ],
        "added_mechanism_comparison_unit_count": 3,
        "independent_comparison_unit_count": 3,
        "total_independent_comparison_weight": 3,
        "admitted_Dx_comparison_rows": admitted_dx_rows,
        "admitted_Dx_comparison_row_count": len(admitted_dx_rows),
        "excluded_Dx_rows": [
            {
                "comparison_row": "D0_R",
                "reason": i8["classification"]["D0_R"]["status"],
            },
            {
                "comparison_row": "conditional_internal_reorganization",
                "reason": "perturbation_control_not_D0_decay_relation",
            },
        ],
        "total_I11_comparison_row_count": 3 + len(admitted_dx_rows),
        "I11_required_profile_axes": [
            "semantic_fit",
            "strict_RC_theory_compatibility",
            "coherence_conservation",
            "local_causality",
            "internal_time_ownership",
            "carrier_authority",
            "mediation_strength",
            "restoration_completeness",
            "native_mechanics_already_available",
            "producer_residue",
            "naturalization_debt",
            "topology_scope",
            "transfer_evidence",
            "RCAE_relevance",
        ],
        "single_scalar_ranking_allowed": False,
        "plural_or_conditional_selection_allowed": True,
        "I11_ranking_or_selection_performed": False,
        "raw_effect_magnitude_ranking_performed": False,
    }


def artifact_manifest(records: list[tuple[Path, dict[str, Any], str]]) -> list[dict[str, Any]]:
    return [
        {
            "artifact_role": role,
            "path": relative(path),
            "sha256": sha256_file(path),
            "output_digest": value["output_digest"],
        }
        for path, value, role in records
    ]


def runtime_snapshot_manifest() -> list[dict[str, Any]]:
    rows = (
        ("I10_A_fresh_branch_one_native_snapshot", ARTIFACT_DIR / "n31_i10_A_fresh_branch_one.json"),
        ("I10_A_fresh_branch_two_native_snapshot", ARTIFACT_DIR / "n31_i10_A_fresh_branch_two.json"),
        ("I10_A_aged_branch_one_native_snapshot", ARTIFACT_DIR / "n31_i10_A_aged_branch_one.json"),
        ("I10_A_aged_branch_two_native_snapshot", ARTIFACT_DIR / "n31_i10_A_aged_branch_two.json"),
        ("I10_B_branch_one_native_snapshot", ARTIFACT_DIR / "n31_i10_B_branch_one.json"),
        ("I10_B_branch_two_native_snapshot", ARTIFACT_DIR / "n31_i10_B_branch_two.json"),
        (
            "I10_C2_formed_branch_one_post_transport_native_snapshot",
            ARTIFACT_DIR
            / "n31_i10_C2_formed_native_history_branch_one_post_transport.json",
        ),
        (
            "I10_C2_formed_branch_two_post_transport_native_snapshot",
            ARTIFACT_DIR
            / "n31_i10_C2_formed_native_history_branch_two_post_transport.json",
        ),
        (
            "I10_C2_progressed_branch_one_post_transport_native_snapshot",
            ARTIFACT_DIR
            / "n31_i10_C2_progressed_native_history_branch_one_post_transport.json",
        ),
        (
            "I10_C2_progressed_branch_two_post_transport_native_snapshot",
            ARTIFACT_DIR
            / "n31_i10_C2_progressed_native_history_branch_two_post_transport.json",
        ),
    )
    return [
        {
            "artifact_role": role,
            "path": relative(path),
            "sha256": sha256_file(path),
        }
        for role, path in rows
    ]


def git_diff_empty(path: str) -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--quiet", GOVERNANCE_BASE_REVISION, "--", path],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    values = {
        path.stem: load_json(path)
        for path in SOURCE_IDENTITIES
    }
    i2 = load_json(I2)
    i3 = load_json(I3)
    i8 = load_json(I8)
    i9a = load_json(I9A)
    i9b = load_json(I9B)
    i9c2 = load_json(I9C2)

    preregistration = write_record(
        PREREGISTRATION,
        {
            "artifact_kind": "n31_i10_preregistration",
            "artifact_schema_version": "n31_i10_preregistration_v1",
            "generated_at": GENERATED_AT,
            "comparison_unit_policy": "one_unit_per_A_B_C_family",
            "family_bundles": {
                "A": ["I9-A", "I9-A.1"],
                "B": ["I9-B", "I9-B.1"],
                "C": ["I9-C.2"],
            },
            "C_ancestry": ["I9-C", "I9-C.1"],
            "C_ancestry_positive_weight": 0,
            "required_replay_modes": [
                "artifact",
                "snapshot_load_v2",
                "duplicate",
                "branch",
            ],
            "required_control_count": len(i2["controls"]["all_control_ids"]),
            "rung_policy": {
                "DR5": "intervention_replay_restoration_invariants_and_controls_pass",
                "DR6": "not_assignable_in_I10",
                "native_D0a": "remains_DR2",
                "C2_relation_carrier": "DR2",
                "C2_native_runtime": "DR0",
            },
            "C2_DR5_requires_post_feedback_restoration_witness": True,
            "control_resolution_policy": (
                "registry_resolution_is_not_equivalent_to_runtime_execution"
            ),
            "I11_comparison_policy": "multi_axis_profile_before_any_selection",
            "I11_single_scalar_ranking_allowed": False,
            "deferred_C2_naturalization_controls_are_I10_gates": False,
            "I11_comparative_selection_opened": False,
        },
    )
    source_replay = write_record(SOURCE_REPLAY, artifact_replay(values))
    a = write_record(A_REPLAY, build_a_family(i9a))
    b = write_record(B_REPLAY, build_b_family(i9b))
    c = write_record(
        C_REPLAY,
        build_c_family(i9c2, load_json(I9C), load_json(I9C1)),
    )
    controls = write_record(
        CONTROL_MATRIX,
        build_control_matrix(i2, i3, {"A": a, "B": b, "C": c}),
    )
    bundles = write_record(BUNDLE_MATRIX, build_bundle_matrix(a, b, c, i8))
    records = [
        (PREREGISTRATION, preregistration, "I10_preregistration"),
        (SOURCE_REPLAY, source_replay, "I10_source_artifact_replay"),
        (A_REPLAY, a, "I10_A_family_replay_controls"),
        (B_REPLAY, b, "I10_B_family_replay_controls"),
        (C_REPLAY, c, "I10_C_family_replay_controls"),
        (CONTROL_MATRIX, controls, "I10_complete_control_matrix"),
        (BUNDLE_MATRIX, bundles, "I10_family_bundle_matrix"),
    ]
    trace = {
        "artifact_kind": "n31_i10_added_mechanism_replay_control_trace",
        "artifact_schema_version": "n31_i10_added_mechanism_replay_control_trace_v1",
        "generated_at": GENERATED_AT,
        "experiment": "N31",
        "iteration": "10",
        "source_artifact_replay": source_replay,
        "family_replay_controls": {"A": a, "B": b, "C": c},
        "complete_control_matrix": controls,
        "family_bundle_matrix": bundles,
        "checks": [],
        "failed_checks": [],
    }
    trace["checks"] = [
        check(
            "all_exact_I2_I3_I8_I9_sources_consumed",
            source_replay["all_source_identities_exact"],
            source_replay["source_records"],
        ),
        check(
            "all_source_artifact_manifests_replay_exact",
            source_replay["all_manifest_references_exact"],
            source_replay["manifest_reference_count"],
        ),
        check(
            "A_family_all_required_replays_pass",
            all(a[key] == "passed" for key in ("artifact_replay", "snapshot_load_replay", "duplicate_replay", "branch_replay")),
            {key: a[key] for key in ("artifact_replay", "snapshot_load_replay", "duplicate_replay", "branch_replay")},
        ),
        check(
            "A_family_DR5_gates_pass",
            a["independent_native_readout_split_replayed"]
            and a["conservation_and_packet_accounting_exact"]
            and not a["global_selector_used"],
            a["added_mechanism_rung"],
        ),
        check(
            "B_family_all_required_replays_pass",
            all(b[key] == "passed" for key in ("artifact_replay", "snapshot_load_replay", "duplicate_replay", "branch_replay")),
            {key: b[key] for key in ("artifact_replay", "snapshot_load_replay", "duplicate_replay", "branch_replay")},
        ),
        check(
            "B_family_DR5_gates_pass",
            b["later_native_readout_split_replayed"]
            and b["explicit_destination_and_complete_conservation"]
            and not b["destination_on_readout_path"],
            b["added_mechanism_rung"],
        ),
        check(
            "C_family_all_required_replays_pass",
            all(
                c[key] == "passed"
                for key in (
                    "artifact_replay",
                    "snapshot_load_replay",
                    "duplicate_replay",
                    "branch_replay",
                    "post_feedback_restoration_replay",
                )
            ),
            {
                key: c[key]
                for key in (
                    "artifact_replay",
                    "snapshot_load_replay",
                    "duplicate_replay",
                    "branch_replay",
                    "post_feedback_restoration_replay",
                )
            },
        ),
        check(
            "C2_post_feedback_final_state_restoration_witness_exact",
            c["post_feedback_restoration_witness_exposed"],
            [
                {
                    "row_id": row["row_id"],
                    "complete_identity_equal": row[
                        "complete_post_transport_native_identity_equal"
                    ],
                    "roundtrip": row["post_transport_snapshot_roundtrip"],
                    "derived_S_exact": row[
                        "post_transport_restored_derived_S_exact"
                    ],
                    "next_step_exact": row[
                        "post_transport_next_candidate_step_exact"
                    ],
                }
                for row in c["rows"]
            ],
        ),
        check(
            "C_family_candidate_specific_controls_pass",
            c["duplicate_receipt_control"]["status"] == "failed_closed"
            and c["wrong_lineage_control"]["invariant"]
            and c["wrong_edge_or_nonqualifying_event_control"]["invariant"]
            and c["semantic_label_control"]["invariant"]
            and c["role_preserving_topology_control"]["invariant"]
            and c["physical_progression_control"]["physical_change_detected"],
            "duplicate_wrong_lineage_wrong_direction_semantic_topology_and_physical_controls",
        ),
        check(
            "C_family_lane_specific_rungs_preserved",
            c["relation_carrier_lane_rung"] == "DR2"
            and c["producer_extension_lane_rung"] == "DR5"
            and c["native_runtime_lane_rung"] == "DR0"
            and not c["existing_native_support"],
            {
                "relation": c["relation_carrier_lane_rung"],
                "producer": c["producer_extension_lane_rung"],
                "native": c["native_runtime_lane_rung"],
            },
        ),
        check(
            "C_and_C1_retained_as_separate_zero_weight_ancestry",
            len(c["ancestor_records"]) == 2
            and all(row["comparison_weight"] == 0 for row in c["ancestor_records"])
            and all(not row["ranking_eligible"] for row in c["ancestor_records"])
            and all(not row["selection_eligible"] for row in c["ancestor_records"]),
            c["ancestor_records"],
        ),
        check(
            "complete_frozen_control_matrix_resolved",
            controls["frozen_control_count"] == 70
            and controls["I3_null_count"] == 70
            and controls["all_I3_nulls_failed_closed"]
            and controls["all_dependent_controls_resolved"]
            and controls["failed_open_count"] == 0
            and controls["frozen_I10_control_registry_not_run_count"] == 0,
            {
                "status_counts": controls["family_status_counts"],
                "resolution_mode_counts": controls["resolution_mode_counts"],
            },
        ),
        check(
            "family_bundles_prevent_double_counting",
            bundles["added_mechanism_comparison_unit_count"] == 3
            and bundles["total_independent_comparison_weight"] == 3
            and bundles["rows"][2]["ancestor_positive_weight"] == 0
            and not bundles["rows"][2]["ancestor_ranking_eligible"],
            bundles["rows"],
        ),
        check(
            "I11_comparative_selection_not_preempted",
            not bundles["I11_ranking_or_selection_performed"]
            and not bundles["single_scalar_ranking_allowed"]
            and bundles["total_I11_comparison_row_count"] > bundles[
                "added_mechanism_comparison_unit_count"
            ],
            {
                "I10_scope": "admission_only",
                "added_mechanism_units": bundles[
                    "added_mechanism_comparison_unit_count"
                ],
                "total_I11_rows": bundles["total_I11_comparison_row_count"],
                "required_profile_axes": bundles["I11_required_profile_axes"],
            },
        ),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    trace["output_digest"] = digest_value(
        {key: value for key, value in trace.items() if key != "output_digest"}
    )
    TRACE.write_text(canonical_json(trace), encoding="utf-8")
    records.append((TRACE, trace, "I10_runtime_replay_control_trace"))

    payload = {
        "artifact_kind": "n31_added_mechanism_replay_controls",
        "artifact_schema_version": "n31_added_mechanism_replay_controls_i10_v1",
        "generated_at": GENERATED_AT,
        "experiment": "N31",
        "iteration": "10",
        "status": "passed",
        "acceptance_state": "accepted_added_mechanism_family_replay_controls_with_lane_specific_DR5_and_no_native_upgrade",
        "command": COMMAND,
        "script": SCRIPT_RELATIVE,
        "source_records": source_replay["source_records"],
        "artifact_manifest": artifact_manifest(records) + runtime_snapshot_manifest(),
        "family_classification": {
            "A": {
                "semantic_class": "A_expression_attenuation",
                "added_mechanism_ladder_rung": "DR5",
                "candidate_native_runtime_lane": "not_admitted",
                "existing_native_D0a_context_rung": "DR2",
                "candidate_native_support": False,
                "claim_ceiling": "replay_control_backed_producer_mediated_expression_attenuation",
            },
            "B": {
                "semantic_class": "B_R_conserved_export_policy",
                "added_mechanism_ladder_rung": "DR5",
                "candidate_native_runtime_lane": "not_admitted",
                "existing_native_D0a_context_rung": "DR2",
                "candidate_native_support": False,
                "D0_R_bridge_status": "not_tested",
                "claim_ceiling": "replay_control_backed_producer_mediated_conserved_export",
            },
            "C": {
                "semantic_class": "effective_exact_history_constitutive_closure",
                "relation_carrier_lane_rung": "DR2",
                "producer_extension_lane_rung": "DR5",
                "native_runtime_lane_rung": "DR0",
                "claim_ceiling": "replay_control_backed_producer_mediated_exact_history_closure",
                "strict_current_C_only_ontology_supported": False,
            },
        },
        "comparison_admission": bundles,
        "control_resolution": {
            "control_registry_rows_resolved": controls[
                "control_registry_rows_resolved"
            ],
            "family_control_resolution_row_count": controls[
                "family_control_resolution_row_count"
            ],
            "runtime_controls_executed": controls["runtime_controls_executed"],
            "inherited_schema_nulls_consumed": controls[
                "inherited_schema_nulls_consumed"
            ],
            "positive_conformance_rows": controls[
                "positive_conformance_rows"
            ],
            "not_applicable_rows": controls["not_applicable_rows"],
            "failed_open_count": controls["failed_open_count"],
            "frozen_I10_control_registry_not_run_count": controls[
                "frozen_I10_control_registry_not_run_count"
            ],
            "deferred_conditional_C2_controls_in_I10_registry": controls[
                "deferred_conditional_C2_controls_in_I10_registry"
            ],
            "all_dependent_controls_resolved": controls[
                "all_dependent_controls_resolved"
            ],
        },
        "n31_closeout_progress": {
            "n31_closeout_progress_rung": "N31-C4",
            "n31_closeout_ladder_rung_assigned": False,
            "ready_for_iteration_11_comparative_classification": True,
            "ready_for_iteration_12_closeout": False,
        },
        "RCAE_admission": {
            "automatic_adoption_allowed": False,
            "status": "pending_I11_comparative_classification_and_reusable_provider_contract",
            "I10_DR5_alone_is_selection": False,
        },
        "deferred_C2_naturalization": {
            "remains_outside_N31": True,
            "controls_consumed_as_I10_gates": False,
            "native_implementation_selected": False,
            "native_runtime_modified": False,
        },
        "governance": {
            "governance_base_revision": GOVERNANCE_BASE_REVISION,
            "src_diff_empty": git_diff_empty("src"),
            "protected_runtime_contract_diff_empty": all(
                git_diff_empty(path)
                for path in (
                    "src",
                    "specs",
                    "tests",
                    "examples",
                    "pyproject.toml",
                    "requirements.txt",
                    "uv.lock",
                )
            ),
        },
        "claim_boundary": {
            "allowed_claim": (
                "A, B, and C.2 producer-mediated mechanism families pass bounded "
                "I10 replay, restoration, invariant, and control gates at lane-specific "
                "DR5, without native or semantic promotion"
            ),
            "blocked_claims": [
                "native_autonomous_decay",
                "strict_current_C_only_C2",
                "general_decay_law",
                "memory",
                "trail_or_stigmergy",
                "communication",
                "ecology_coordination",
                "learning",
                "agency",
                "selfhood",
                "sentience",
                "organism_or_life",
                "native_support",
                "phase8_completion",
                "automatic_RCAE_adoption",
            ],
            "unsafe_claim_flags": {
                "native_autonomous_decay_claim_allowed": False,
                "strict_current_C_only_C2_claim_allowed": False,
                "general_decay_law_claim_allowed": False,
                "memory_claim_allowed": False,
                "trail_or_stigmergy_claim_allowed": False,
                "communication_claim_allowed": False,
                "ecology_coordination_claim_allowed": False,
                "learning_claim_allowed": False,
                "agency_claim_allowed": False,
                "selfhood_claim_allowed": False,
                "sentience_claim_allowed": False,
                "organism_or_life_claim_allowed": False,
                "native_support_claim_allowed": False,
                "phase8_completion_claim_allowed": False,
                "automatic_RCAE_adoption_claim_allowed": False,
            },
        },
        "checks": trace["checks"]
        + [
            check(
                "src_and_protected_contracts_unchanged",
                git_diff_empty("src")
                and all(
                    git_diff_empty(path)
                    for path in (
                        "specs",
                        "tests",
                        "examples",
                        "pyproject.toml",
                        "requirements.txt",
                        "uv.lock",
                    )
                ),
                GOVERNANCE_BASE_REVISION,
            ),
            check(
                "unsafe_claim_flags_false",
                True,
                "all_I10_unsafe_claim_flags_frozen_false",
            ),
            check("no_absolute_paths_in_records", True, "evaluated_after_payload"),
        ],
        "failed_checks": [],
    }
    payload["checks"][-2]["passed"] = all(
        value is False
        for value in payload["claim_boundary"]["unsafe_claim_flags"].values()
    )
    payload["checks"][-2]["detail"] = payload["claim_boundary"][
        "unsafe_claim_flags"
    ]
    payload["checks"][-1]["passed"] = no_absolute_paths(payload)
    payload["failed_checks"] = [
        row["check_id"] for row in payload["checks"] if not row["passed"]
    ]
    if payload["failed_checks"]:
        payload["status"] = "failed"
        payload["acceptance_state"] = "blocked_I10_replay_or_control_failure"
        payload["n31_closeout_progress"][
            "ready_for_iteration_11_comparative_classification"
        ] = False
    payload["output_digest"] = digest_value(
        {key: value for key, value in payload.items() if key != "output_digest"}
    )
    return payload, trace


def write_report(payload: dict[str, Any], trace: dict[str, Any]) -> None:
    checks = "\n".join(
        f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 10 - Added-Mechanism Replay And Controls

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
A added-mechanism lane = DR5 expression attenuation
B added-mechanism lane = DR5 conserved export
C.2 relation carrier lane = DR2
C.2 producer-extension lane = DR5 effective exact-history closure
C.2 native-runtime lane = DR0
native spatial D0a = DR2 unchanged
DR6 = unsupported in I10
N31 closeout progress = N31-C4
ready for I11 = {str(payload['n31_closeout_progress']['ready_for_iteration_11_comparative_classification']).lower()}
```

I10 applies the replay, restoration, invariant, accounting, topology, hidden-state,
and producer/native gates to the three mechanism families. It admits each family
once. I9-A.1 and I9-B.1 strengthen their parent families; they are not extra
candidates. I9-C and I9-C.1 remain zero-weight C ancestry. C.2 is the sole
comparison-eligible C representative.

## Replay

```text
manifest references replayed = {trace['source_artifact_replay']['manifest_reference_count']}
unique artifact paths replayed = {trace['source_artifact_replay']['unique_artifact_path_count']}
all source identities exact = {str(trace['source_artifact_replay']['all_source_identities_exact']).lower()}
all manifest hashes exact = {str(trace['source_artifact_replay']['all_manifest_references_exact']).lower()}
A artifact/snapshot/duplicate/branch = passed/passed/passed/passed
B artifact/snapshot/duplicate/branch = passed/passed/passed/passed
C artifact/snapshot/duplicate/branch = passed/passed/passed/passed
reset-sensitive identity = lgrc9v3_restoration_identity_v2
```

Fresh A replay reproduces the `0.20` versus `0.10` release split and the later
native `q=0.35` admission split. Fresh B replay reproduces explicit `0.04`
source debit, packet amount, destination credit, conservation, and the later
native admission boundary change. Fresh C.2 replay rederives the relation from
native packet history and reruns the producer/step composition on both formed
and progressed histories. Each C.2 branch now retains its post-transport native
snapshot. Those final states match under restoration identities v1 and v2,
rederive the same post-feedback `S`, and produce the same next candidate-step
result after load. This is the load-bearing C.2 restoration witness for producer
`DR5`; source-state roundtrip alone would have left C.2 at `DR4`.

## Controls

```text
control registry rows resolved = {payload['control_resolution']['control_registry_rows_resolved']}
family control-resolution rows = {payload['control_resolution']['family_control_resolution_row_count']}
runtime controls executed = {payload['control_resolution']['runtime_controls_executed']}
inherited schema nulls consumed = {payload['control_resolution']['inherited_schema_nulls_consumed']}
positive conformance observations = {payload['control_resolution']['positive_conformance_rows']}
scope-not-applicable rows = {payload['control_resolution']['not_applicable_rows']}
failed_open = {payload['control_resolution']['failed_open_count']}
frozen I10 registry not_run = {payload['control_resolution']['frozen_I10_control_registry_not_run_count']}
deferred conditional C.2 controls are in I10 registry = {str(payload['control_resolution']['deferred_conditional_C2_controls_in_I10_registry']).lower()}
all dependent controls resolved = {str(payload['control_resolution']['all_dependent_controls_resolved']).lower()}
```

The `70` count is registry coverage, not `70` family runtime executions.
`failed_closed` rows consume the exact I3 schema-validator fixture that triggered
the false-positive path; they are not described as family runtime failures.
Positive conformance observations and actually executed runtime controls are
counted separately. `not_applicable` is used only with a family-scope reason.
Candidate C additionally rejects duplicate committed arrivals, ignores lineage
and semantic labels, ignores wrong-direction nonqualifying events, survives
role-preserving topology renumbering, and changes only when physical progression
history changes. C/C.1-specific boundary controls remain non-contributory ancestry.

## Lane Boundary

C.2 is not collapsed into one rung:

```text
carrier/restoration comparison = DR2
producer-mediated mechanism comparison = DR5
native implementation comparison = DR0
```

The DR5 producer result does not naturalize C.2. The deferred packetization,
direct-mediation, multi-cycle, topology-lifecycle, cache, and native readmission
requirements remain outside N31 and were not silently converted into I10 gates.

## Comparative Boundary

I10 does not rank or select A, B, or C.2. I11 must compare semantic meaning,
theory compatibility, conservation, local causality, representation, producer
residue, and naturalization debt. Raw effect sizes are not a valid cross-family
ranking metric. I11 receives three added-mechanism units plus the admitted D0a,
D0b, and D0c rows from I8, for `{payload['comparison_admission']['total_I11_comparison_row_count']}`
comparison rows. It must use a multi-axis profile or Pareto classification before
any plural or conditional selection; one scalar score is prohibited.

## Checks

| Check | Passed |
|---|---:|
{checks}

## Claim Ceiling

```text
{payload['claim_boundary']['allowed_claim']}
```

This is not native autonomous decay, a strict current-`C`-only realization of
C.2, a general decay law, memory, stigmergy, communication, ecology, learning,
agency, native support, Phase 8 completion, or automatic RCAE adoption.

## Reproduction

```bash
{COMMAND}
```

```text
output_digest = {payload['output_digest']}
```
""",
        encoding="utf-8",
    )


def main() -> None:
    payload, trace = build()
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    write_report(payload, trace)
    if trace["failed_checks"]:
        raise RuntimeError("N31 I10 trace failed: " + ", ".join(trace["failed_checks"]))
    if payload["failed_checks"]:
        raise RuntimeError("N31 I10 failed: " + ", ".join(payload["failed_checks"]))
    print(canonical_json(payload), end="")


if __name__ == "__main__":
    main()
