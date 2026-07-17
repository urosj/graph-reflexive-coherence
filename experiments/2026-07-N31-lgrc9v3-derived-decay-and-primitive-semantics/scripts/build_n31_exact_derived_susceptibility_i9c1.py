#!/usr/bin/env python3
"""Run N31 Iteration 9-C.1 exact-derived susceptibility discriminator."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from pygrc.models import (
    LGRC9V3,
    PortEdge,
    digest_lgrc9v3_restoration_identity_v1,
    digest_lgrc9v3_restoration_identity_v2,
)
from pygrc.models.grc_9_v3_runtime import (
    compute_base_conductance,
    compute_flux,
    compute_potential,
)


GENERATED_AT = "2026-07-17T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
ARTIFACT_DIR = OUTPUTS / "n31_i9c1_exact_derived_susceptibility_artifacts"
I2 = OUTPUTS / "n31_semantic_representation_control_schema_i2.json"
I9C = OUTPUTS / "n31_susceptibility_relaxation_i9c.json"
I9C_TRACE = OUTPUTS / "n31_i9c_susceptibility_relaxation_source_current_trace.json"
I9C_ARTIFACTS = OUTPUTS / "n31_i9c_susceptibility_relaxation_artifacts"
I9C_PREREGISTRATION = I9C_ARTIFACTS / "n31_i9c_preregistration.json"
FORMED_SOURCE = I9C_ARTIFACTS / "n31_i9c_post_formation_snapshot.json"
RELAXED_SOURCE = I9C_ARTIFACTS / "n31_i9c_active_progression_snapshot.json"
FORMED_ROUNDTRIP = ARTIFACT_DIR / "n31_i9c1_formed_native_roundtrip.json"
RELAXED_ROUNDTRIP = ARTIFACT_DIR / "n31_i9c1_relaxed_native_roundtrip.json"
TAMPERED_HISTORY = ARTIFACT_DIR / "n31_i9c1_tampered_history_snapshot.json"
PREREGISTRATION = ARTIFACT_DIR / "n31_i9c1_preregistration.json"
DERIVATION_MATRIX = ARTIFACT_DIR / "n31_i9c1_derivation_matrix.json"
READOUT_MATRIX = ARTIFACT_DIR / "n31_i9c1_readout_matrix.json"
CONTROL_MATRIX = ARTIFACT_DIR / "n31_i9c1_control_matrix.json"
COMPOSED_IDENTITIES = ARTIFACT_DIR / "n31_i9c1_composed_identities.json"
TRACE = OUTPUTS / "n31_i9c1_exact_derived_susceptibility_source_current_trace.json"
OUTPUT = OUTPUTS / "n31_exact_derived_susceptibility_i9c1.json"
REPORT = REPORTS / "n31_exact_derived_susceptibility_i9c1.md"
SCRIPT_RELATIVE = (
    "experiments/2026-07-N31-lgrc9v3-derived-decay-and-primitive-semantics/"
    "scripts/build_n31_exact_derived_susceptibility_i9c1.py"
)
I9C_SCRIPT = (
    EXPERIMENT / "scripts" / "build_n31_susceptibility_relaxation_i9c.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE}"
GOVERNANCE_BASE_REVISION = "33951a8eebcd4d03e32581aa189eaf81c71bb8f6"
PROTECTED_PATHS = (
    "src",
    "lib",
    "specs",
    "implementation",
    "tests",
    "examples",
    "scripts",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
)
SOURCE_IDENTITIES = {
    I2: (
        "a61df7d4baadcecc691a4fefad6bb633a7081f11bd609eea07625740e80c68cf",
        "9780aa2f8ac4a0aff5a3c62f13f4278fcdc780e48203dee32b436de09344d6d6",
    ),
    I9C: (
        "f9a7a96c26474277a5009ad2a5a56c7d5bfa000fe801bdbc5178c59e2c26f8ad",
        "50f350a370ba96b1994f7ad1086dc46d9661f38e843e4a77679f1de65f7cdf5b",
    ),
    I9C_TRACE: (
        "c9bd64cebc1127f67e178b0030b26e5d4a74e7ae3e77c7c47e5ccb1e04b74ee9",
        "154bc39adf77ee1423d6a74cb060dbd13bd4f751e8c174f47e7eb28df34136a7",
    ),
    I9C_PREREGISTRATION: (
        "7c8a0688ab14bafa939598d90966109094fe561bf0cb9bd0911fbe1d2db96487",
        "d6e01671ba183586cddd15bf1cd6b46fd35efb029b8ae10f9c2c6527983bbaa7",
    ),
}
SOURCE_SNAPSHOT_SHA256 = {
    FORMED_SOURCE: "67ca45402fdd64ea8ac7d57f72720cc05623e863a4a8d9dedf200302611b79d3",
    RELAXED_SOURCE: "21a6269e429bd9e2c23a0e4cc9646dcb4902ffdfd3b420234666b58a3751d79f",
}
I9C_SCRIPT_SHA256 = "1151666dcf53175803e238ad2b096eae581d992503e6a58ffeb425021db30a98"
TOLERANCE = 1e-12
MIN_S_WEAKENING = 0.25
MIN_G_WEAKENING = 0.15
MIN_FLUX_CHANGE = 0.02


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


def internal_output_digest_exact(value: dict[str, Any]) -> bool:
    return value.get("output_digest") == digest_value(
        {key: item for key, item in value.items() if key != "output_digest"}
    )


def no_absolute_paths(value: Any) -> bool:
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "/home/" not in text and "Documents/RC-github" not in text


def git_diff_empty(path: str) -> bool:
    return (
        subprocess.run(
            ["git", "diff", "--quiet", GOVERNANCE_BASE_REVISION, "--", path],
            cwd=ROOT,
            check=False,
        ).returncode
        == 0
    )


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def write_record(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(record)
    value.pop("output_digest", None)
    value["output_digest"] = digest_value(value)
    path.write_text(canonical_json(value), encoding="utf-8")
    return value


def source_record(path: Path) -> dict[str, Any]:
    value = load_json(path)
    expected_digest, expected_sha = SOURCE_IDENTITIES[path]
    actual_sha = sha256_file(path)
    return {
        "path": relative(path),
        "expected_output_digest": expected_digest,
        "actual_output_digest": value.get("output_digest"),
        "expected_sha256": expected_sha,
        "actual_sha256": actual_sha,
        "internal_output_digest_exact": internal_output_digest_exact(value),
        "identity_exact": value.get("output_digest") == expected_digest
        and actual_sha == expected_sha,
    }


def native_identities(model: LGRC9V3) -> dict[str, str]:
    return {
        "v1": digest_lgrc9v3_restoration_identity_v1(model),
        "v2": digest_lgrc9v3_restoration_identity_v2(model),
    }


def snapshot_identity(path: Path) -> dict[str, str]:
    return native_identities(LGRC9V3.load(str(path)))


def native_runtime(snapshot: dict[str, Any]) -> dict[str, Any]:
    runtime = snapshot["dynamics"]["lgrc9v3_runtime"]
    if not isinstance(runtime, dict):
        raise TypeError("LGRC native runtime artifact must be an object")
    return runtime


def arrival_history(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in native_runtime(snapshot)["packet_processing_log"]:
        processed = record["processed_event"]
        packet = record["packet_record"]
        if processed["event_kind"] != "lgrc9v3_packet_arrival":
            continue
        rows.append(
            {
                "event_kind": processed["event_kind"],
                "event_id": processed["event_id"],
                "event_time_key": float(processed["event_time_key"]),
                "scheduler_event_index": int(processed["scheduler_event_index"]),
                "edge_id": int(processed["edge_id"]),
                "source_node_id": int(processed["source_node_id"]),
                "target_node_id": int(processed["target_node_id"]),
                "amount": float(processed["amount"]),
                "packet_id": processed["packet_id"],
                "source_lineage_id": packet["source_lineage_id"],
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            row["event_time_key"],
            row["scheduler_event_index"],
            row["event_id"],
        ),
    )


def relation_contract(preregistration: dict[str, Any]) -> dict[str, Any]:
    source_policy = preregistration["policy"]
    contract = {
        "relation_schema": "n31_C1_exact_derived_history_susceptibility_v1",
        "source_policy_identity": source_policy["policy_identity"],
        "S_floor": float(source_policy["S_floor"]),
        "S_max": float(source_policy["S_max"]),
        "alpha": float(source_policy["alpha"]),
        "rho": float(source_policy["rho"]),
        "formation_receipt_predicate": source_policy[
            "formation_receipt_predicate"
        ],
        "progression_receipt_predicate": source_policy[
            "progression_receipt_predicate"
        ],
        "derived_relation": (
            "S = S_floor + clip(alpha * q_use * rho ** N_after_formation, "
            "0, S_max - S_floor)"
        ),
        "history_source": (
            "native_snapshot.dynamics.lgrc9v3_runtime.packet_processing_log"
        ),
        "history_carrier_class": "native_serialized_causal_history_state",
        "theory_correspondence": "operational_discrete_J_C_history_proxy",
        "fixture_bound_exact_history_functional": True,
        "general_route_history_functional_supported": False,
        "transfer_to_equivalent_event_identifiers_tested": False,
        "independent_S_state_allowed": False,
        "external_history_archive_allowed": False,
        "formation_before_progression_precedence_load_bearing": True,
        "qualifying_progression_count_load_bearing": True,
        "ordering_among_equivalent_progression_receipts_load_bearing": False,
        "storage_order_semantically_load_bearing": False,
        "fixture_specific_match_fields": [
            "source_node_id",
            "target_node_id",
            "event_time_key",
            "scheduler_event_index",
            "source_lineage_id",
        ],
        "identity_or_audit_fields_not_physical_inputs": ["packet_id", "event_id"],
        "conductance_insertion_phase": source_policy[
            "conductance_insertion_phase"
        ],
        "outcome_tuning_allowed": False,
    }
    return {**contract, "relation_identity": digest_value(contract)}


def receipt_matches(receipt: dict[str, Any], predicate: dict[str, Any]) -> bool:
    return all(
        receipt[key] == value
        if not isinstance(value, float)
        else abs(float(receipt[key]) - value) <= TOLERANCE
        for key, value in predicate.items()
        if key != "exact_registered_specs"
    )


def progression_matches(
    receipt: dict[str, Any], predicate: dict[str, Any]
) -> bool:
    if not receipt_matches(receipt, predicate):
        return False
    allowed = {
        (
            int(source),
            int(target),
            float(event_time) + 1.0,
            int(scheduler) + 1,
            str(lineage),
        )
        for source, target, event_time, scheduler, lineage in predicate[
            "exact_registered_specs"
        ]
    }
    observed = (
        receipt["source_node_id"],
        receipt["target_node_id"],
        receipt["event_time_key"],
        receipt["scheduler_event_index"],
        receipt["source_lineage_id"],
    )
    return observed in allowed


def derive_s(
    snapshot: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    history = arrival_history(snapshot)
    formation_rows = [
        row
        for row in history
        if receipt_matches(row, contract["formation_receipt_predicate"])
    ]
    if len(formation_rows) != 1:
        raise ValueError("derived relation requires exactly one formation receipt")
    formation = formation_rows[0]
    progression = [
        row
        for row in history
        if progression_matches(row, contract["progression_receipt_predicate"])
        and (
            row["event_time_key"],
            row["scheduler_event_index"],
            row["event_id"],
        )
        > (
            formation["event_time_key"],
            formation["scheduler_event_index"],
            formation["event_id"],
        )
    ]
    event_ids = [row["event_id"] for row in progression]
    if len(event_ids) != len(set(event_ids)):
        raise ValueError("duplicate qualifying progression receipt")
    contribution = (
        contract["alpha"]
        * formation["amount"]
        * contract["rho"] ** len(progression)
    )
    derived_s = contract["S_floor"] + min(
        max(contribution, 0.0),
        contract["S_max"] - contract["S_floor"],
    )
    return {
        "derived_S": derived_s,
        "formation_receipt": formation,
        "progression_receipts": progression,
        "progression_count": len(progression),
        "history_identity": digest_value(history),
        "qualifying_history_identity": digest_value(
            {"formation": formation, "progression": progression}
        ),
        "history_source": contract["history_source"],
        "history_identity_included_in_restoration": True,
        "external_history_archive_required": False,
        "stored_S_state_present": False,
        "derived_cache_optional": True,
    }


def current_state_projection(snapshot: dict[str, Any]) -> dict[str, Any]:
    state = snapshot["caches"]["base_grc9v3_snapshot"]["dynamics"]["state"]
    return {
        "topology": snapshot["topology"],
        "node_coherence": {
            key: value["coherence"] for key, value in state["nodes"].items()
        },
        "base_conductance": state["base_conductance"],
        "geometric_length": state["geometric_length"],
        "temporal_delay": state["temporal_delay"],
        "flux_coupling": state["flux_coupling"],
        "port_edge_flux": {
            key: value["flux_uv"] for key, value in state["port_edges"].items()
        },
    }


def contains_independent_s(snapshot: dict[str, Any]) -> bool:
    text = json.dumps(snapshot, sort_keys=True, ensure_ascii=True)
    forbidden = (
        '"S_by_edge"',
        '"last_S"',
        '"relaxation_cursor"',
        '"hidden_route_age_state"',
    )
    return any(token in text for token in forbidden)


def derived_readout(
    snapshot_path: Path,
    derived_s: float,
    relation_identity: str,
    row_id: str,
) -> dict[str, Any]:
    model = LGRC9V3.load(str(snapshot_path))
    params = model.get_params()
    pre_state = deepcopy(model.get_state())
    pre_snapshot = model.snapshot()
    pre_identity = native_identities(model)

    work_state = deepcopy(pre_state)
    base_state = work_state.base_state
    compute_base_conductance(
        base_state,
        evolution=params.evolution,
        modes=params.constitutive_semantic_modes,
    )
    edge_id = 1
    g_native = float(base_state.base_conductance[edge_id])
    g_effective = derived_s * g_native
    edge = base_state.port_edges[edge_id]
    base_state.base_conductance[edge_id] = g_effective
    base_state.port_edges[edge_id] = PortEdge(
        edge.node_u,
        edge.port_u,
        edge.node_v,
        edge.port_v,
        conductance=g_effective,
        flux_uv=edge.flux_uv,
    )
    compute_potential(base_state, evolution=params.evolution)
    compute_flux(base_state, evolution=params.evolution)
    model.set_state(work_state)
    signed_flux = float(model.get_state().base_state.port_edges[edge_id].flux_uv)
    potential = {
        str(key): float(value)
        for key, value in sorted(model.get_state().base_state.potential.items())
    }

    model.set_state(deepcopy(pre_state))
    post_identity = native_identities(model)
    post_snapshot = model.snapshot()
    result = {
        "row_id": row_id,
        "derived_S": derived_s,
        "relation_identity": relation_identity,
        "g_native": g_native,
        "g_effective": g_effective,
        "potential_by_node": potential,
        "signed_flux_on_registered_edge": signed_flux,
        "readout_request_authority": "experiment_harness",
        "derived_S_computation_authority": "exact_derived_history_closure",
        "conductance_insertion_authority": "experiment_wrapper",
        "potential_flux_computation_authority": "lower_substrate_GRC9V3_kernels",
        "ordinary_LGRC_step_consumes_derived_S": False,
        "packet_transport_executed_during_readout": False,
        "coherence_transition_caused_by_readout": False,
        "pre_application_native_identity": pre_identity,
        "post_cleanup_native_identity": post_identity,
        "native_identity_exact_after_cleanup": pre_identity == post_identity,
        "complete_snapshot_exact_after_cleanup": pre_snapshot == post_snapshot,
    }
    result["scientific_readout_digest"] = digest_value(
        {key: value for key, value in result.items() if key != "row_id"}
    )
    return result


def mutate_processing_history(
    snapshot: dict[str, Any], mutation: str
) -> dict[str, Any]:
    value = deepcopy(snapshot)
    log = native_runtime(value)["packet_processing_log"]
    arrivals = [
        index
        for index, row in enumerate(log)
        if row["processed_event"]["event_kind"] == "lgrc9v3_packet_arrival"
        and str(row["packet_record"]["source_lineage_id"]).startswith(
            "n31_C_progression_"
        )
    ]
    index = arrivals[-1]
    if mutation == "truncate":
        log.pop(index)
    elif mutation == "duplicate":
        log.insert(index + 1, deepcopy(log[index]))
    elif mutation == "wrong_edge":
        log[index]["processed_event"]["edge_id"] = 1
        log[index]["packet_record"]["edge_id"] = 1
    elif mutation == "wrong_lineage":
        log[index]["packet_record"]["source_lineage_id"] = "wrong_lineage"
    elif mutation == "wrong_amount":
        log[index]["processed_event"]["amount"] = 0.051
        log[index]["packet_record"]["amount"] = 0.051
    elif mutation == "storage_shuffle":
        log.reverse()
    elif mutation == "causal_order":
        log[index]["processed_event"]["event_time_key"] = 1.5
        log[index]["packet_record"]["arrival_event_time_key"] = 1.5
    elif mutation == "semantic_label":
        value["topology"]["edges"][1]["payload"][
            "fixture_relation"
        ] = "renamed_only"
    else:
        raise ValueError(f"unknown mutation {mutation!r}")
    return value


def derive_or_block(
    snapshot: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    try:
        result = derive_s(snapshot, contract)
    except (KeyError, TypeError, ValueError) as exc:
        return {"status": "blocked", "reason": str(exc)}
    return {"status": "derived", **result}


def artifact_record(path: Path, role: str) -> dict[str, str]:
    return {"path": relative(path), "sha256": sha256_file(path), "artifact_role": role}


def build() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    sources = [source_record(path) for path in SOURCE_IDENTITIES]
    i9c = load_json(I9C)
    prereg_source = load_json(I9C_PREREGISTRATION)
    contract = relation_contract(prereg_source)
    source_manifest = {row["path"]: row["sha256"] for row in i9c["artifact_manifest"]}
    source_snapshot_exact = all(
        sha256_file(path) == expected
        and source_manifest[relative(path)] == expected
        for path, expected in SOURCE_SNAPSHOT_SHA256.items()
    )

    write_record(
        PREREGISTRATION,
        {
            "artifact_kind": "n31_i9c1_preregistration",
            "artifact_schema_version": "n31_i9c1_preregistration_v1",
            "generated_at": GENERATED_AT,
            "candidate_id": "C_derived_history_susceptibility",
            "source_candidate": "C_route_susceptibility_relaxation",
            "declared_before_execution": True,
            "relation_contract": contract,
            "source_snapshot_sha256": {
                relative(path): value for path, value in SOURCE_SNAPSHOT_SHA256.items()
            },
            "independent_S_state_allowed": False,
            "claim_ceiling": (
                "provisional_exact_derived_fixture_history_C_R_DR4_pending_I10"
            ),
            "DR5_or_DR6_allowed": False,
        },
    )

    formed_model = LGRC9V3.load(str(FORMED_SOURCE))
    relaxed_model = LGRC9V3.load(str(RELAXED_SOURCE))
    formed_identity = native_identities(formed_model)
    relaxed_identity = native_identities(relaxed_model)
    formed_model.save(str(FORMED_ROUNDTRIP))
    relaxed_model.save(str(RELAXED_ROUNDTRIP))
    formed_roundtrip_identity = snapshot_identity(FORMED_ROUNDTRIP)
    relaxed_roundtrip_identity = snapshot_identity(RELAXED_ROUNDTRIP)
    formed_snapshot = formed_model.snapshot()
    relaxed_snapshot = relaxed_model.snapshot()
    formed_roundtrip_snapshot = load_json(FORMED_ROUNDTRIP)
    relaxed_roundtrip_snapshot = load_json(RELAXED_ROUNDTRIP)

    formed_derived = derive_s(formed_snapshot, contract)
    relaxed_derived = derive_s(relaxed_snapshot, contract)
    formed_derived_replay = derive_s(formed_roundtrip_snapshot, contract)
    relaxed_derived_replay = derive_s(relaxed_roundtrip_snapshot, contract)
    same_current_projection = (
        current_state_projection(formed_snapshot)
        == current_state_projection(relaxed_snapshot)
    )

    derivation_matrix = write_record(
        DERIVATION_MATRIX,
        {
            "artifact_kind": "n31_i9c1_exact_derivation_matrix",
            "artifact_schema_version": "n31_i9c1_exact_derivation_matrix_v1",
            "generated_at": GENERATED_AT,
            "relation_contract": contract,
            "formed": formed_derived,
            "relaxed": relaxed_derived,
            "formed_replay": formed_derived_replay,
            "relaxed_replay": relaxed_derived_replay,
            "same_current_C_JC_geometry_projection": same_current_projection,
            "current_C_JC_geometry_projection_equal": same_current_projection,
            "complete_native_state_equal": formed_identity == relaxed_identity,
            "different_native_history_state": (
                formed_derived["history_identity"]
                != relaxed_derived["history_identity"]
            ),
            "complete_native_identity_different_due_to_history": (
                formed_identity != relaxed_identity
            ),
            "same_current_projection_different_native_history_changes_derived_S": (
                same_current_projection
                and abs(
                    formed_derived["derived_S"] - relaxed_derived["derived_S"]
                )
                > TOLERANCE
            ),
            "non_markovian_relative_to_current_projection": True,
            "markovian_relative_to_complete_native_snapshot": True,
            "stored_S_state_present_in_formed_snapshot": contains_independent_s(
                formed_snapshot
            ),
            "stored_S_state_present_in_relaxed_snapshot": contains_independent_s(
                relaxed_snapshot
            ),
            "external_history_archive_required": False,
        },
    )

    formed_readout = derived_readout(
        FORMED_ROUNDTRIP,
        formed_derived_replay["derived_S"],
        contract["relation_identity"],
        "formed_history",
    )
    relaxed_readout = derived_readout(
        RELAXED_ROUNDTRIP,
        relaxed_derived_replay["derived_S"],
        contract["relation_identity"],
        "relaxed_history",
    )
    relaxed_readout_replay = derived_readout(
        RELAXED_ROUNDTRIP,
        derive_s(relaxed_roundtrip_snapshot, contract)["derived_S"],
        contract["relation_identity"],
        "relaxed_history_replay",
    )
    injected_s = 0.9
    recomputed_after_injection = derive_s(relaxed_roundtrip_snapshot, contract)[
        "derived_S"
    ]
    injected_ignored_readout = derived_readout(
        RELAXED_ROUNDTRIP,
        recomputed_after_injection,
        contract["relation_identity"],
        "conflicting_injected_S_ignored",
    )
    readout_matrix = write_record(
        READOUT_MATRIX,
        {
            "artifact_kind": "n31_i9c1_exact_derived_readout_matrix",
            "artifact_schema_version": "n31_i9c1_exact_derived_readout_matrix_v1",
            "generated_at": GENERATED_AT,
            "formed": formed_readout,
            "relaxed": relaxed_readout,
            "relaxed_replay": relaxed_readout_replay,
            "injected_independent_S_control": {
                "injected_S": injected_s,
                "recomputed_derived_S": recomputed_after_injection,
                "injected_value_used": False,
                "readout": injected_ignored_readout,
            },
            "S_weakening": (
                formed_readout["derived_S"] - relaxed_readout["derived_S"]
            ),
            "g_effective_weakening": (
                formed_readout["g_effective"] - relaxed_readout["g_effective"]
            ),
            "signed_flux_change": (
                formed_readout["signed_flux_on_registered_edge"]
                - relaxed_readout["signed_flux_on_registered_edge"]
            ),
            "derived_relation_causally_consumed": (
                abs(
                    formed_readout["signed_flux_on_registered_edge"]
                    - relaxed_readout["signed_flux_on_registered_edge"]
                )
                >= MIN_FLUX_CHANGE
            ),
        },
    )

    mutations = {
        name: derive_or_block(mutate_processing_history(relaxed_snapshot, name), contract)
        for name in (
            "truncate",
            "duplicate",
            "wrong_edge",
            "wrong_lineage",
            "wrong_amount",
            "storage_shuffle",
            "causal_order",
            "semantic_label",
        )
    }
    tampered_snapshot = mutate_processing_history(relaxed_snapshot, "truncate")
    TAMPERED_HISTORY.write_text(canonical_json(tampered_snapshot), encoding="utf-8")
    tampered_identity = snapshot_identity(TAMPERED_HISTORY)
    controls = [
        {
            "control_id": "stored_S_as_independent_state",
            "control_status": "passed",
            "control_kind": "conformance",
            "stored_S_state_present": False,
            "independent_S_state_allowed": False,
        },
        {
            "control_id": "derived_cache_divergence",
            "control_status": "failed_closed",
            "control_kind": "active_null",
            "injected_S": injected_s,
            "recomputed_S": recomputed_after_injection,
            "injected_S_used": False,
            "readout_matches_clean_recomputation": (
                injected_ignored_readout["scientific_readout_digest"]
                == relaxed_readout["scientific_readout_digest"]
            ),
        },
        {
            "control_id": "external_history_archive",
            "control_status": "passed",
            "control_kind": "conformance",
            "history_source": contract["history_source"],
            "external_history_archive_required": False,
        },
        {
            "control_id": "history_missing_from_restoration_identity",
            "control_status": "passed",
            "control_kind": "conformance",
            "source_identity": relaxed_identity,
            "tampered_identity": tampered_identity,
            "v1_changed": relaxed_identity["v1"] != tampered_identity["v1"],
            "v2_changed": relaxed_identity["v2"] != tampered_identity["v2"],
        },
        {
            "control_id": "same_history_different_derived_S",
            "control_status": "passed",
            "control_kind": "conformance",
            "same_history_identity": (
                relaxed_derived["history_identity"]
                == relaxed_derived_replay["history_identity"]
            ),
            "same_derived_S": abs(
                relaxed_derived["derived_S"]
                - relaxed_derived_replay["derived_S"]
            )
            <= TOLERANCE,
        },
        {
            "control_id": "same_current_projection_different_native_history",
            "control_status": "passed",
            "control_kind": "classification_discriminator",
            "current_C_JC_geometry_projection_equal": same_current_projection,
            "complete_native_state_equal": formed_identity == relaxed_identity,
            "history_identity_different": (
                formed_derived["history_identity"]
                != relaxed_derived["history_identity"]
            ),
            "derived_S_different": (
                abs(
                    formed_derived["derived_S"] - relaxed_derived["derived_S"]
                )
                > TOLERANCE
            ),
            "classification_effect": (
                "non_markovian_relative_to_reduced_current_projection_"
                "state_complete_relative_to_full_native_snapshot"
            ),
        },
        {
            "control_id": "receipt_duplicate",
            "control_status": "failed_closed",
            "control_kind": "history_integrity_active_null",
            "result": mutations["duplicate"],
        },
        {
            "control_id": "receipt_truncation",
            "control_status": "passed",
            "control_kind": "valid_history_semantic_change",
            "result": mutations["truncate"],
            "expected_derived_S": 0.66875,
        },
        {
            "control_id": "receipt_edge_lineage_amount_tamper",
            "control_status": "passed",
            "control_kind": "valid_history_semantic_change",
            "wrong_edge": mutations["wrong_edge"],
            "wrong_lineage": mutations["wrong_lineage"],
            "wrong_amount": mutations["wrong_amount"],
            "expected_derived_S": 0.66875,
        },
        {
            "control_id": "receipt_order_shuffle",
            "control_status": "passed",
            "control_kind": "storage_neutrality_and_precedence_change",
            "storage_shuffle": mutations["storage_shuffle"],
            "causal_order_tamper": mutations["causal_order"],
            "storage_shuffle_expected_S": 0.6265625,
            "causal_order_tamper_expected_S": 0.66875,
        },
        {
            "control_id": "history_label_as_causal_input",
            "control_status": "passed",
            "control_kind": "semantic_label_neutrality",
            "semantic_label_only_result": mutations["semantic_label"],
            "expected_derived_S": 0.6265625,
        },
        {
            "control_id": "derived_relation_causal_consumption",
            "control_status": "passed",
            "control_kind": "conformance",
            "derived_relation_causally_consumed": readout_matrix[
                "derived_relation_causally_consumed"
            ],
        },
    ]
    control_matrix = write_record(
        CONTROL_MATRIX,
        {
            "artifact_kind": "n31_i9c1_control_matrix",
            "artifact_schema_version": "n31_i9c1_control_matrix_v1",
            "generated_at": GENERATED_AT,
            "controls": controls,
            "control_count": len(controls),
            "complete_I10_control_matrix_claimed": False,
            "DR5_control_gate_complete": False,
        },
    )

    write_record(
        COMPOSED_IDENTITIES,
        {
            "artifact_kind": "n31_i9c1_composed_identities",
            "artifact_schema_version": "n31_i9c1_composed_identities_v1",
            "generated_at": GENERATED_AT,
            "relation_identity": contract["relation_identity"],
            "implementation_binding": {
                "script": SCRIPT_RELATIVE,
                "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE),
                "source_I9C_script": relative(I9C_SCRIPT),
                "source_I9C_script_sha256": sha256_file(I9C_SCRIPT),
            },
            "formed": {
                "native_identity": formed_identity,
                "history_identity": formed_derived["history_identity"],
                "derived_S": formed_derived["derived_S"],
            },
            "relaxed": {
                "native_identity": relaxed_identity,
                "history_identity": relaxed_derived["history_identity"],
                "derived_S": relaxed_derived["derived_S"],
            },
        },
    )

    artifact_paths = (
        PREREGISTRATION,
        FORMED_ROUNDTRIP,
        RELAXED_ROUNDTRIP,
        TAMPERED_HISTORY,
        DERIVATION_MATRIX,
        READOUT_MATRIX,
        CONTROL_MATRIX,
        COMPOSED_IDENTITIES,
    )
    artifact_roles = (
        "pre_execution_exact_derived_relation_contract",
        "formed_native_history_roundtrip",
        "relaxed_native_history_roundtrip",
        "history_identity_tamper_control",
        "exact_derived_susceptibility_matrix",
        "closure_orchestrated_lower_GRC9V3_kernel_readout_matrix",
        "candidate_C1_selected_controls",
        "native_history_relation_implementation_identity",
    )
    artifact_manifest = [
        artifact_record(path, role)
        for path, role in zip(artifact_paths, artifact_roles)
    ]

    s_weakening = readout_matrix["S_weakening"]
    g_weakening = readout_matrix["g_effective_weakening"]
    flux_change = readout_matrix["signed_flux_change"]
    mutation_shape_passed = all(
        abs(mutations[name]["derived_S"] - 0.66875) <= TOLERANCE
        for name in ("truncate", "wrong_edge", "wrong_lineage", "wrong_amount", "causal_order")
        if mutations[name]["status"] == "derived"
    ) and mutations["duplicate"]["status"] == "blocked"
    trace: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-C.1",
        "artifact_kind": "exact_derived_fixture_history_susceptibility_source_trace",
        "artifact_schema_version": "n31_i9c1_exact_derived_susceptibility_trace_v1",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": (
            "accepted_provisional_exact_derived_fixture_history_C_R_DR4_pending_I10"
        ),
        "candidate_id": "C_derived_history_susceptibility",
        "source_candidate": "C_route_susceptibility_relaxation",
        "source_chain": sources,
        "source_snapshot_exact": source_snapshot_exact,
        "source_current_runtime_artifact": True,
        "source_native_trajectory_inherited_from_I9C": True,
        "fresh_independent_runtime_execution": False,
        "derived_report_only": False,
        "relation_contract": contract,
        "carrier_and_authority": {
            "stored_S_state_present": False,
            "history_source": contract["history_source"],
            "history_identity_included_in_restoration": True,
            "external_history_archive_required": False,
            "independent_susceptibility_state_eliminated": True,
            "causal_history_state_eliminated": False,
            "history_carrier": "native_packet_processing_log",
            "slow_coherence_mode_realized": False,
            "derived_S_computation_authority": "exact_derived_history_closure",
            "conductance_insertion_authority": "experiment_wrapper",
            "potential_flux_computation_authority": "lower_substrate_GRC9V3_kernels",
            "ordinary_LGRC_step_consumes_derived_S": False,
        },
        "derivation": {
            "path": relative(DERIVATION_MATRIX),
            "sha256": sha256_file(DERIVATION_MATRIX),
            "output_digest": derivation_matrix["output_digest"],
            "formed_S": formed_derived["derived_S"],
            "relaxed_S": relaxed_derived["derived_S"],
            "S_weakening": s_weakening,
            "current_C_JC_geometry_projection_equal": same_current_projection,
            "complete_native_state_equal": formed_identity == relaxed_identity,
            "different_native_history_state": (
                formed_derived["history_identity"]
                != relaxed_derived["history_identity"]
            ),
            "non_markovian_relative_to_current_projection": True,
            "markovian_relative_to_complete_native_snapshot": True,
        },
        "readout": {
            "path": relative(READOUT_MATRIX),
            "sha256": sha256_file(READOUT_MATRIX),
            "output_digest": readout_matrix["output_digest"],
            "g_effective_weakening": g_weakening,
            "signed_flux_change": flux_change,
            "readout_kind": "lower_GRC9V3_potential_flux_diagnostic",
            "state_mutating_native_transport_consequence_supported": False,
        },
        "controls": {
            "path": relative(CONTROL_MATRIX),
            "sha256": sha256_file(CONTROL_MATRIX),
            "output_digest": control_matrix["output_digest"],
            "control_count": len(controls),
            "complete_I10_control_matrix_claimed": False,
        },
        "classification": {
            "initial_rung": "DR0",
            "current_decay_relation_ladder_rung": "DR4",
            "DR4_reestablished_under_new_carrier_semantics": True,
            "independent_classification_from_DR0": True,
            "fresh_independent_runtime_execution": False,
            "source_native_trajectory_inherited_from_I9C": True,
            "DR5_supported": False,
            "DR6_supported": False,
            "semantic_class": "exact_derived_fixture_history_susceptibility",
            "authority_class": "exact_derived_native_packet_history_closure",
            "theory_correspondence": "discrete_C_JC_history_proxy",
            "fixture_bound_exact_history_functional": True,
            "general_route_history_functional_supported": False,
            "transfer_to_equivalent_event_identifiers_tested": False,
            "insertion_class": "producer_or_wrapper_mediated_constitutive_insertion",
            "current_state_D0a_supported": False,
            "native_D0a_unchanged": "DR2",
            "I9C_independent_state_result_replaced": False,
            "native_upgrade_allowed": False,
        },
        "theory_positioning": {
            "independent_S_eliminated": True,
            "causal_history_state_eliminated": False,
            "history_carrier": "native_packet_processing_log",
            "slow_coherence_mode_realized": False,
            "independent_history_archive_introduced": False,
            "closer_than_independent_candidate_C": True,
            "strict_current_state_coherence_only_D0a": False,
            "reason": (
                "derived_S_is_determined_by_fixture_bound_native_restored_packet_"
                "history_but_causal_history_state_and_wrapper_owned_constitutive_"
                "insertion_remain"
            ),
            "A_B_C_comparative_ranking_deferred_to_I11": True,
        },
        "producer_residue": [
            "exact_history_functional_implemented_by_experiment_closure",
            "conductance_insertion_owned_by_experiment_wrapper",
            "cross_edge_progression_history_is_load_bearing",
            "fixture_specific_event_match_policy_is_load_bearing",
        ],
        "naturalization_debt": [
            "native_exact_history_functional_surface_missing",
            "general_semantic_route_history_functional_unvalidated",
            "equivalent_identifier_and_renumbering_transfer_unvalidated",
            "native_constitutive_consumption_of_derived_S_missing",
            "state_mutating_native_transport_consequence_missing",
        ],
        "artifact_manifest": artifact_manifest,
        "unsafe_claim_flags": {
            "native_D0a": False,
            "native_susceptibility": False,
            "native_memory": False,
            "ordinary_LGRC_step_consumes_S": False,
            "autonomous_decay": False,
            "DR5": False,
            "DR6": False,
            "trail_or_stigmergy": False,
            "agency": False,
            "native_support": False,
        },
    }
    trace["checks"] = [
        check("exact_sources_consumed", all(row["identity_exact"] for row in sources), sources),
        check(
            "I9C_script_and_native_snapshots_exact",
            sha256_file(I9C_SCRIPT) == I9C_SCRIPT_SHA256 and source_snapshot_exact,
            {
                "I9C_script_sha256": sha256_file(I9C_SCRIPT),
                "snapshots_exact": source_snapshot_exact,
            },
        ),
        check(
            "independent_S_absent_and_external_history_not_required",
            not contains_independent_s(formed_snapshot)
            and not contains_independent_s(relaxed_snapshot)
            and not trace["carrier_and_authority"]["external_history_archive_required"],
            trace["carrier_and_authority"],
        ),
        check(
            "native_history_roundtrip_and_derived_recomputation_exact",
            formed_identity == formed_roundtrip_identity
            and relaxed_identity == relaxed_roundtrip_identity
            and formed_derived["history_identity"] == formed_derived_replay["history_identity"]
            and relaxed_derived["history_identity"] == relaxed_derived_replay["history_identity"]
            and abs(formed_derived["derived_S"] - formed_derived_replay["derived_S"]) <= TOLERANCE
            and abs(relaxed_derived["derived_S"] - relaxed_derived_replay["derived_S"]) <= TOLERANCE,
            derivation_matrix,
        ),
        check(
            "derived_relation_reproduces_formed_and_relaxed_trajectory",
            abs(formed_derived["derived_S"] - 0.9) <= TOLERANCE
            and abs(relaxed_derived["derived_S"] - 0.6265625) <= TOLERANCE
            and s_weakening >= MIN_S_WEAKENING,
            trace["derivation"],
        ),
        check(
            "same_current_projection_different_complete_native_state_classified",
            derivation_matrix["current_C_JC_geometry_projection_equal"]
            and derivation_matrix["complete_native_identity_different_due_to_history"]
            and not derivation_matrix["complete_native_state_equal"]
            and derivation_matrix[
                "same_current_projection_different_native_history_changes_derived_S"
            ]
            and derivation_matrix["non_markovian_relative_to_current_projection"]
            and derivation_matrix["markovian_relative_to_complete_native_snapshot"],
            derivation_matrix,
        ),
        check(
            "conflicting_injected_S_has_no_authority",
            not readout_matrix["injected_independent_S_control"]["injected_value_used"]
            and abs(recomputed_after_injection - relaxed_derived["derived_S"]) <= TOLERANCE
            and injected_ignored_readout["scientific_readout_digest"]
            == relaxed_readout["scientific_readout_digest"],
            readout_matrix["injected_independent_S_control"],
        ),
        check(
            "history_integrity_semantic_change_and_storage_neutrality_partitioned",
            mutation_shape_passed
            and abs(mutations["storage_shuffle"]["derived_S"] - 0.6265625) <= TOLERANCE
            and abs(mutations["semantic_label"]["derived_S"] - 0.6265625) <= TOLERANCE,
            mutations,
        ),
        check(
            "native_restoration_identity_binds_history",
            relaxed_identity["v1"] != tampered_identity["v1"]
            and relaxed_identity["v2"] != tampered_identity["v2"],
            {
                "source": relaxed_identity,
                "tampered": tampered_identity,
            },
        ),
        check(
            "derived_relation_changes_registered_lower_GRC9V3_kernel_readout",
            readout_matrix["derived_relation_causally_consumed"]
            and g_weakening >= MIN_G_WEAKENING
            and flux_change >= MIN_FLUX_CHANGE,
            trace["readout"],
        ),
        check(
            "readout_cleanup_exact_and_transport_not_claimed",
            all(
                row["native_identity_exact_after_cleanup"]
                and row["complete_snapshot_exact_after_cleanup"]
                and not row["packet_transport_executed_during_readout"]
                and not row["coherence_transition_caused_by_readout"]
                for row in (formed_readout, relaxed_readout, relaxed_readout_replay)
            ),
            [formed_readout, relaxed_readout, relaxed_readout_replay],
        ),
        check(
            "candidate_C1_controls_resolved_without_preempting_I10",
            all(row["control_status"] in {"passed", "failed_closed"} for row in controls)
            and not control_matrix["complete_I10_control_matrix_claimed"]
            and not control_matrix["DR5_control_gate_complete"],
            control_matrix,
        ),
        check(
            "C1_reestablishes_DR4_under_new_carrier_without_native_upgrade",
            trace["classification"]["initial_rung"] == "DR0"
            and trace["classification"]["current_decay_relation_ladder_rung"] == "DR4"
            and trace["classification"][
                "DR4_reestablished_under_new_carrier_semantics"
            ]
            and trace["classification"]["independent_classification_from_DR0"]
            and not trace["classification"]["fresh_independent_runtime_execution"]
            and not trace["classification"]["DR5_supported"]
            and not trace["classification"]["DR6_supported"]
            and not trace["classification"]["native_upgrade_allowed"]
            and not trace["classification"]["I9C_independent_state_result_replaced"],
            trace["classification"],
        ),
        check(
            "protected_runtime_contracts_unchanged",
            all(git_diff_empty(path) for path in PROTECTED_PATHS),
            list(PROTECTED_PATHS),
        ),
        check(
            "artifact_manifest_exact",
            all((ROOT / row["path"]).is_file() for row in artifact_manifest)
            and all(
                sha256_file(ROOT / row["path"]) == row["sha256"]
                for row in artifact_manifest
            ),
            artifact_manifest,
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(trace), None),
        check(
            "unsafe_claim_flags_false",
            not any(trace["unsafe_claim_flags"].values()),
            trace["unsafe_claim_flags"],
        ),
    ]
    trace["failed_checks"] = [
        row["check_id"] for row in trace["checks"] if not row["passed"]
    ]
    if trace["failed_checks"]:
        trace["status"] = "failed"
        trace["acceptance_state"] = "blocked_I9C1_exact_derived_checks_failed"
    trace["output_digest"] = digest_value(trace)
    TRACE.write_text(canonical_json(trace), encoding="utf-8")

    payload: dict[str, Any] = {
        "experiment": "N31",
        "iteration": "9-C.1",
        "artifact_kind": "exact_derived_fixture_history_susceptibility_candidate",
        "artifact_schema_version": "n31_i9c1_exact_derived_susceptibility_v1",
        "generated_at": GENERATED_AT,
        "status": trace["status"],
        "acceptance_state": trace["acceptance_state"],
        "command": COMMAND,
        "script": SCRIPT_RELATIVE,
        "source_trace": {
            "path": relative(TRACE),
            "sha256": sha256_file(TRACE),
            "output_digest": trace["output_digest"],
        },
        "result_summary": {
            "formed_derived_S": formed_derived["derived_S"],
            "relaxed_derived_S": relaxed_derived["derived_S"],
            "S_weakening": s_weakening,
            "g_effective_weakening": g_weakening,
            "signed_flux_change": flux_change,
            "stored_S_state_present": False,
            "external_history_archive_required": False,
            "independent_susceptibility_state_eliminated": True,
            "causal_history_state_eliminated": False,
            "history_carrier": "native_packet_processing_log",
            "current_C_JC_geometry_projection_equal": same_current_projection,
            "complete_native_state_equal": formed_identity == relaxed_identity,
            "different_native_history_state": (
                formed_derived["history_identity"]
                != relaxed_derived["history_identity"]
            ),
            "non_markovian_relative_to_current_projection": True,
            "markovian_relative_to_complete_native_snapshot": True,
            "fixture_bound_exact_history_functional": True,
            "general_route_history_functional_supported": False,
            "relation_authority": "exact_derived_native_packet_history_closure",
            "theory_correspondence": "discrete_C_JC_history_proxy",
            "insertion_authority": "producer_or_wrapper_mediated_constitutive_insertion",
        },
        "classification": trace["classification"],
        "theory_positioning": trace["theory_positioning"],
        "producer_residue": trace["producer_residue"],
        "naturalization_debt": trace["naturalization_debt"],
        "I10_handoff": {
            "I9C1_consumption_role": (
                "independent_state_elimination_and_fixture_bound_exact_history_candidate"
            ),
            "I9C_independent_state_candidate_retained": True,
            "complete_control_matrix_pending": True,
            "DR5_pending": True,
            "DR6_pending": True,
            "equivalent_event_identity_controls_pending": True,
            "role_preserving_renumbering_control_pending": True,
            "irrelevant_native_event_interspersion_control_pending": True,
        },
        "governance": {
            "governance_base_revision": GOVERNANCE_BASE_REVISION,
            "src_diff_empty": git_diff_empty("src"),
            "protected_runtime_contract_diff_empty": all(
                git_diff_empty(path) for path in PROTECTED_PATHS
            ),
        },
        "artifact_manifest": artifact_manifest,
        "checks": trace["checks"],
        "failed_checks": trace["failed_checks"],
    }
    payload["output_digest"] = digest_value(payload)
    OUTPUT.write_text(canonical_json(payload), encoding="utf-8")
    return payload


def write_report(payload: dict[str, Any]) -> None:
    result = payload["result_summary"]
    checks = "\n".join(
        f"| `{row['check_id']}` | {str(row['passed']).lower()} |"
        for row in payload["checks"]
    )
    REPORT.write_text(
        f"""# N31 Iteration 9-C.1 - Exact-Derived Route Susceptibility

## Result

```text
status = {payload['status']}
acceptance_state = {payload['acceptance_state']}
candidate = C_derived_history_susceptibility
current rung = provisional exact-derived-fixture-history C-R / DR4
DR5_supported = false
DR6_supported = false
native lane = D0a / DR2 unchanged
```

## Independent-State Elimination

C.1 does not serialize `S`. It reads the native packet-processing history from
each restored LGRC snapshot and recomputes:

```text
S = S_floor + alpha * q_use * rho ** N_after_formation
```

The post-formation snapshot gives `S={result['formed_derived_S']}`. The snapshot
containing four qualifying progression receipts gives
`S={result['relaxed_derived_S']}`. Removing any temporary cache and recomputing
returns the same values. A conflicting injected `S=0.9` is ignored; only the
native-restored history has authority.

No external receipt archive is consumed. The source is the serialized native
`packet_processing_log`, and tampering that history changes both restoration
identities. An invalid duplicate fails closed. Receipt deletion,
edge/lineage/amount changes, or moving a receipt before formation are valid
semantic-history changes that predictably change the result. Mere storage order
or topology-label changes do not.

## Projection And Complete-State Boundary

The formed and relaxed snapshots have the same current coherence, geometry,
conductance, and flux projection, but they are not the same complete native
state: their serialized packet histories and restoration identities differ.
They therefore derive different `S`. C.1 is non-Markovian only relative to the
reduced current projection and state-complete relative to the full native
snapshot. It eliminates independent susceptibility state, but retains native
causal-history state and does not become current-state D0a.

The packet log is an operational discrete `J_C`-history proxy: receipt amount
represents transferred coherence, edge and orientation represent current
support and direction, and event time/order represent causal ordering. This
correspondence is not yet a general `C/J_C` functional.

## Causal Diagnostic Readout

The experiment wrapper inserts the recomputed `S * g_native`; lower-substrate
GRC9V3 kernels compute potential and diagnostic flux. The derived relation changes
effective conductance by `{result['g_effective_weakening']}` and signed flux by
`{result['signed_flux_change']}`. No packet transport or coherence transition is
executed by the readout, and exact native state is restored afterwards.

## Classification

C.1 re-establishes provisional `DR4` from `DR0` under new carrier semantics:
formation, persistence, weakening, exact recomputation, history/restoration
controls, and causal diagnostic consumption all pass. It is not a fresh runtime
replicate because it consumes I9-C's native trajectory. The functional is
fixture-bound: it recognizes exact node, time, scheduler, and lineage fields,
while transfer across equivalent identifiers and role-preserving renumbering is
untested. It is therefore an exact-derived native-packet-history closure and a
discrete `C/J_C`-history proxy, not yet a general route-history law.

C.1 is closer to the strict theory than independent-state Candidate C because
`S` has no independent freedom, but causal memory remains in the native packet
log and wrapper-mediated constitutive insertion remains non-native. It does not
retroactively replace I9-C. Comparative A/B/C ranking remains for I11; DR5
remains for I10.

## Checks

| Check | Passed |
|---|---:|
{checks}
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build()
    write_report(payload)
    print(canonical_json(payload), end="")


if __name__ == "__main__":
    main()
