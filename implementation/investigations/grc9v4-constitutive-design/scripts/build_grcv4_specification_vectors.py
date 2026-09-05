#!/usr/bin/env python3
"""Build deterministic preimplementation GRCV4 conformance vectors."""

from __future__ import annotations

import hashlib
import json
import math
from collections import deque
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SCHEMA = ROOT / "specs/grc-v4-contract-schema.json"
CATALOG = ROOT / "specs/grc-v4-conformance-fixtures.json"
OUTPUT = ROOT / "specs/grc-v4-conformance-vectors.json"
WITNESS = (
    ROOT / "implementation/investigations/grc9v4-constitutive-design/scripts/"
    "witness_d11_c_hm_stiffness_baseline.py"
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jcs_number(value: int | float) -> str:
    if isinstance(value, bool):
        raise TypeError("Boolean is not a number in the vector canonicalizer")
    if isinstance(value, int):
        if abs(value) > 9_007_199_254_740_991:
            raise ValueError("integer outside the I-JSON exact range")
        return str(value)
    if not math.isfinite(value) or (value == 0 and math.copysign(1, value) < 0):
        raise ValueError("nonfinite and negative-zero values are forbidden")
    if value == 0:
        return "0"
    text = repr(value).lower()
    if 1e-6 <= abs(value) < 1e21:
        fixed = format(Decimal(text), "f")
        if "." in fixed:
            fixed = fixed.rstrip("0").rstrip(".")
        return fixed
    if "e" in text:
        coefficient, exponent = text.split("e")
        if coefficient.endswith(".0"):
            coefficient = coefficient[:-2]
        exponent_value = int(exponent)
        text = f"{coefficient}e{'+' if exponent_value >= 0 else ''}{exponent_value}"
    return text


def jcs(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return jcs_number(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "[" + ",".join(jcs(row) for row in value) + "]"
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("JCS object keys must be strings")
        return (
            "{"
            + ",".join(
                f"{jcs(key)}:{jcs(value[key])}"
                for key in sorted(
                    value,
                    key=lambda item: item.encode("utf-16-be", errors="surrogatepass"),
                )
            )
            + "}"
        )
    raise TypeError(f"unsupported JCS value: {type(value)!r}")


def identity(prefix: str, payload: dict[str, Any]) -> str:
    digest = hashlib.sha256(jcs(payload).encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def identity_vector(
    vector_id: str,
    schema_ref: str,
    prefix: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    canonical = jcs(payload)
    return {
        "vector_id": vector_id,
        "schema_ref": schema_ref,
        "payload": payload,
        "canonical_jcs_utf8": canonical,
        "canonical_jcs_utf8_hex": canonical.encode("utf-8").hex(),
        "expected_identifier": identity(prefix, payload),
    }


def wrapped_payload(schema_version: str, field: str, payload: Any) -> dict[str, Any]:
    return {"schema_version": schema_version, field: payload}


def wrapped_digest(prefix: str, schema_version: str, field: str, payload: Any) -> str:
    return identity(prefix, wrapped_payload(schema_version, field, payload))


def common_params() -> dict[str, Any]:
    return {
        "schema_version": "grcv4-common-params-v1",
        "differential_backend_id": "oriented_incidence_d0_equals_BT_v1",
        "boundary_policy_id": "closed_no_flux_v1",
        "measure_profile_id": "unit_vertex_measure_v1",
        "context_contract_id": "constant_zero_context_v1",
        "units_id": "grcv4_nondimensional_reference_v1",
        "gauge_id": "component_zero_mean_potential_v1",
        "normalization_id": "unnormalized_vertex_stiffness_v1",
        "domain_id": "fixed_graph_strict_gap_spd_v1",
        "default_step_request": None,
    }


def c_params(weights: dict[str, float]) -> dict[str, Any]:
    return {
        "schema_version": "grcv4-candidate-c-params-v1",
        "transport_id": "C-HM-STIFFNESS-BASELINE-v1",
        "Lambda_C": 1,
        "selector_boundary_policy_id": "strict_rank_gap_fail_closed_v1",
        "C_ref": 1,
        "kappa_M_C": 0.5,
        "kappa_Phi_C": 1,
        "eta_C": 0.5,
        "W_C_tr": weights,
        "W_C_tr_content_digest": wrapped_digest(
            "grcv4-wctr-sha256", "grcv4-wctr-identity-v1", "W_C_tr", weights
        ),
        "potential_evaluator_id": "quadratic_site_potential_zero_derivative_v1",
        "tau_C": 0,
        "chi_C": 1,
        "zeta_C": 0.5,
        "current_conditioning_policy_id": "strict_invertible_current_block_v1",
        "E_H_policy_id": "diag_W_C_tr_structural_hodge_v1",
        "E_M_policy_id": "eta_C_diag_W_C_tr_mobility_v1",
    }


def resolved_params(
    weights: dict[str, float], profile_family: str = "C_OS"
) -> dict[str, Any]:
    if profile_family == "C_OS":
        realization = {
            "schema_version": "grcv4-os-params-v1",
            "predictor_policy_id": "reference_geometry_predictor_v1",
            "corrector_policy_id": "one_fresh_geometry_corrector_v1",
            "split_residual_norm_id": "edge_l2_v1",
            "tolerance": 0,
        }
    elif profile_family == "C_PC":
        realization = {
            "schema_version": "grcv4-pc-params-v1",
            "tau_PC": 2,
            "radius": 1,
            "carrier_norm_id": "edge_l2_v1",
            "source_envelope_id": "authoritative_current_magnitude_v1",
            "writer_id": "zero_order_hold_exponential_v1",
        }
    else:
        raise ValueError(f"unsupported concrete vector profile: {profile_family}")
    return {
        "schema_version": "grcv4-resolved-params-v1",
        "common": common_params(),
        "candidate": c_params(weights),
        "realization": realization,
        "geometry": {
            "schema_version": "grcv4-geometry-profile-params-v1",
            "K4_base_digest": wrapped_digest(
                "grcv4-k4-sha256",
                "grcv4-k4-identity-v1",
                "K4_base",
                [[1, 0], [0, 1]],
            ),
            "reference_hodge_digest": wrapped_digest(
                "grcv4-hodge-sha256",
                "grcv4-reference-hodge-identity-v1",
                "edge_weights",
                weights,
            ),
            "star_cover_id": "vertex_star_exact_overlap_v1",
            "overlap_normalization_id": "edge_multiplicity_inverse_sqrt_v1",
            "candidate_adapter_id": "candidate_c_exact_star_adapter_v1",
            "flat_sharp_solver_id": "spd_direct_v1",
            "geometry_domain_id": "positive_hodge_fixed_graph_v1",
            "kappa_H": 0.5,
        },
        "solver": {
            "schema_version": "grcv4-solver-policy-v1",
            "solver_kind": "direct",
            "root_selector_id": "unique_admitted_root_v1",
            "iteration_limit": 1,
            "conditioning_limit": 100,
            "residual_norm_id": "edge_l2_v1",
            "absolute_tolerance": 0,
            "relative_tolerance": 0,
            "failure_policy_id": "fail_closed_no_fallback_v1",
        },
        "charge": {
            "schema_version": "grcv4-charge-policy-v1",
            "policy_id": "stable_pairwise_binary64_charge_v1",
            "accumulation_order": "canonical_live_vertex_balanced_binary_tree",
            "rounding_mode": "IEEE754_binary64_roundTiesToEven",
            "absolute_tolerance": 0,
            "relative_tolerance": 0,
            "repair_policy": "never_mutate_resource",
            "remainder_policy": "compatibility_projection_is_none",
        },
        "lifecycle": {
            "schema_version": "grcv4-lifecycle-policy-v1",
            "migration_policy_id": "typed_bidirectional_profile_migration_v1",
            "mapped_event_policy_id": "caller_mapped_atomic_topology_event_v1",
            "reset_policy_id": "restore_current_baseline_append_receipt_v1",
            "rebase_policy_id": "replace_baseline_append_receipt_v1",
            "history_policy_id": "candidate_c_no_independent_history_v1",
            "receipt_policy_id": "operation_delta_plus_persistent_ledger_v1",
            "target_readmission_policy_id": "full_target_fail_closed_v1",
        },
    }


def resolved_a_os_params() -> dict[str, Any]:
    payload = resolved_params({"old-1": 1})
    payload["candidate"] = {
        "schema_version": "grcv4-candidate-a-params-v1",
        "eta": 1,
        "kappa_c": 0,
        "site_potential_id": "quadratic_site_potential_zero_derivative_v1",
        "W_floor": 0.1,
        "alpha": 1,
        "beta": 1,
        "gamma": 1,
        "kappa_Ah": 0.5,
        "chi_A": 1,
        "zeta_A": 0.5,
        "tau_A": 2,
        "descriptor_backend_id": "curvature_disabled_descriptor_v1",
        "conductance_evaluator_id": "curvature_disabled_G_W_v1",
    }
    payload["geometry"]["candidate_adapter_id"] = "candidate_a_exact_star_adapter_v1"
    payload["lifecycle"]["history_policy_id"] = "candidate_a_exact_or_initialized_v1"
    return payload


def resolved_a_pc_params() -> dict[str, Any]:
    payload = resolved_a_os_params()
    payload["realization"] = {
        "schema_version": "grcv4-pc-params-v1",
        "tau_PC": 2,
        "radius": 1,
        "carrier_norm_id": "edge_l2_v1",
        "source_envelope_id": "authoritative_current_magnitude_v1",
        "writer_id": "zero_order_hold_exponential_v1",
    }
    return payload


def profile_payload(params_id: str, profile_family: str = "C_OS") -> dict[str, Any]:
    realization = {"C_OS": "OS", "C_PC": "PC"}[profile_family]
    return {
        "schema_version": "grcv4-profile-identity-v1",
        "profile_family_id": profile_family,
        "candidate": "C",
        "realization": realization,
        "differential_backend_id": "oriented_incidence_d0_equals_BT_v1",
        "charge_profile_id": "unit_vertex_measure_v1",
        "geometry_profile_id": "affine_reference_relative_v1",
        "context_contract_id": "constant_zero_context_v1",
        "units_id": "grcv4_nondimensional_reference_v1",
        "gauge_id": "component_zero_mean_potential_v1",
        "normalization_id": "unnormalized_vertex_stiffness_v1",
        "domain_id": "fixed_graph_strict_gap_spd_v1",
        "solver_id": "direct_unique_root_v1",
        "lifecycle_policy_id": "grcv4-lifecycle-policy-v1",
        "candidate_c_transport_id": "C-HM-STIFFNESS-BASELINE-v1",
        "composition_gain": None,
        "params_hash": params_id,
    }


def candidate_a_profile_payload(
    params_id: str, profile_family: str = "A_OS"
) -> dict[str, Any]:
    payload = profile_payload(params_id)
    realization = {"A_OS": "OS", "A_PC": "PC"}[profile_family]
    payload.update(
        {
            "profile_family_id": profile_family,
            "candidate": "A",
            "realization": realization,
            "candidate_c_transport_id": None,
        }
    )
    return payload


def profile_template(
    source_profile_id: str, profile_family: str = "C_OS"
) -> dict[str, Any]:
    return {
        "schema_version": "grcv4-profile-template-v1",
        "source_complete_profile_id": source_profile_id,
        "profile_family_id": profile_family,
        "topology_dependent_map_policy_id": (
            "preserve_old_stable_edges_seed_new_internal_edges_v1"
        ),
        "geometry_reference_policy_id": "rebuild_reference_hodge_from_target_W_C_tr_v1",
    }


def candidate_a_profile_template(source_profile_id: str) -> dict[str, Any]:
    return {
        "schema_version": "grcv4-profile-template-v1",
        "source_complete_profile_id": source_profile_id,
        "profile_family_id": "A_OS",
        "topology_dependent_map_policy_id": (
            "initialize_target_W_A_over_complete_live_edge_set_v1"
        ),
        "geometry_reference_policy_id": (
            "rebuild_reference_hodge_from_target_candidate_A_reference_v1"
        ),
    }


def specialization_params() -> dict[str, Any]:
    return {
        "schema_version": "grc9v4-resolved-specialization-v1",
        "row_weight": {
            "schema_version": "grc9v4-row-weight-policy-v1",
            "candidate_a_source": "committed_postbeat_W_A",
            "candidate_c_source": "stable_edge_W_C_tr",
            "disabled_source": "exact_delegate_native_base_conductance",
            "evaluation_stage": "fresh_postbeat_candidate_detection",
        },
        "spark": {
            "schema_version": "grc9v4-spark-policy-v1",
            "lane": "current_hybrid_signed_hessian",
            "gradient_tolerance": 0.5,
            "basin_hessian_tolerance": 0.5,
            "spark_hessian_tolerance": 0,
            "child_stabilization": None,
        },
        "expansion": {
            "schema_version": "grc9v4-expansion-policy-v1",
            "policy_id": "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
            "boundary_policy": "reserve_exact_old_port_map_first",
            "primary_spine_policy": "chiral_latin_same_port_transversal",
            "recursive_tree_policy": "creation_order_bfs_same_port_rotor",
            "stable_id_policy": "grc_event_sha256_role_grammar_v1",
            "bond_seed": 2,
            "resource_distribution_schema": "event_supplied_simplex3",
            "source_self_loop_policy": "reject_before_target_construction",
        },
        "coarse_graining": {
            "schema_version": "grc9v4-coarse-policy-v1",
            "nonnegative_field_mode": "simplex_profile",
            "signed_flux_mode": "positive_negative_split",
        },
        "compatibility": {
            "schema_version": "grc9v4-legacy-compatibility-policy-v1",
            "target_spec_version": "grc9v3-spec-2026-09-v1",
            "transition_policy_id": "exact_profile_scoped_delegate_v1",
            "state_policy_id": "exact_candidate_specific_projection_v1",
            "observable_policy_id": "exact_legacy_observable_set_v1",
            "lifecycle_policy_id": "typed_atomic_delegate_crossing_v1",
            "undefined_expansion_disposition": "legacy_expansion_target_undefined",
        },
    }


def specialization_payload(params_id: str) -> dict[str, Any]:
    return {
        "schema_version": "grc9v4-specialization-identity-v1",
        "port_count": 9,
        "port_chart_id": "fixed_3x3_row_column",
        "frame_mode": "fixed_port_chart",
        "hessian_backend": "row_basis_diagonal",
        "hessian_sign": 1,
        "spark_lane": "current_hybrid_signed_hessian",
        "expansion_policy_id": "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
        "row_weight_policy_id": "grc9v4-row-weight-policy-v1",
        "coarse_policy_id": "grc9v4-coarse-policy-v1",
        "grc9v3_target_spec_version": "grc9v3-spec-2026-09-v1",
        "specialization_params_hash": params_id,
    }


def port_row(port: int) -> int:
    return 1 + (port - 1) // 3


def port_column(port: int) -> int:
    return 1 + (port - 1) % 3


def add3(value: int, offset: int) -> int:
    return 1 + ((value - 1 + offset) % 3)


def port_of(row: int, column: int) -> int:
    return column + 3 * (row - 1)


def canonical_node_count(target_effective_degree: int) -> int:
    return max(4, math.ceil((target_effective_degree - 2) / 7))


def branch_counts(
    extra_count: int, chirality: int, phase: int | None
) -> dict[int, int]:
    base, remainder = divmod(extra_count, 3)
    counts = {1: base, 2: base, 3: base}
    if remainder:
        assert phase in (1, 2, 3)
        for index in range(remainder):
            counts[add3(phase, chirality * index)] += 1
    else:
        assert phase is None
    return counts


def source_graph() -> dict[str, Any]:
    return {
        "schema_version": "grc9v4-port-graph-v1",
        "live_node_ids": [*(f"outside-{port}" for port in range(1, 10)), "source-s"],
        "edges": [
            {
                "edge_id": f"old-{port}",
                "kind": "boundary",
                "tail": {"node_id": "source-s", "port": port},
                "head": {"node_id": f"outside-{port}", "port": port},
            }
            for port in range(1, 10)
        ],
    }


def build_target_plan(
    event_id: str, target_effective_degree: int, chirality: int, phase: int | None
) -> dict[str, Any]:
    node_count = canonical_node_count(target_effective_degree)
    extra_count = node_count - 4
    counts = branch_counts(extra_count, chirality, phase)
    width = max(1, len(str(extra_count)))
    core = f"{event_id}/core"
    satellites = {branch: f"{event_id}/satellite/{branch}" for branch in (1, 2, 3)}
    nodes = {core, *satellites.values(), *(f"outside-{port}" for port in range(1, 10))}
    edges: list[dict[str, Any]] = []
    occupied: set[tuple[str, int]] = set()
    for port in range(1, 10):
        satellite = satellites[port_column(port)]
        occupied.add((satellite, port))
        edges.append(
            {
                "edge_id": f"old-{port}",
                "kind": "boundary",
                "tail": {"node_id": satellite, "port": port},
                "head": {"node_id": f"outside-{port}", "port": port},
            }
        )
    incoming: dict[str, int] = {}
    for branch in (1, 2, 3):
        satellite = satellites[branch]
        column = add3(branch, chirality)
        port = port_of(branch, column)
        occupied.update({(core, port), (satellite, port)})
        edges.append(
            {
                "edge_id": f"{event_id}/internal/{branch}",
                "kind": "spine",
                "tail": {"node_id": core, "port": port},
                "head": {"node_id": satellite, "port": port},
            }
        )
        incoming[satellite] = column
    for branch in (1, 2, 3):
        satellite = satellites[branch]
        candidates = deque(
            column
            for column in (
                add3(incoming[satellite], chirality),
                add3(incoming[satellite], -chirality),
            )
            if (satellite, port_of(branch, column)) not in occupied
        )
        frontier: deque[tuple[str, deque[int]]] = deque([(satellite, candidates)])
        for ordinal in range(1, counts[branch] + 1):
            while frontier and not frontier[0][1]:
                frontier.popleft()
            parent, rotor = frontier[0]
            column = rotor.popleft()
            port = port_of(branch, column)
            child = f"{event_id}/extra/{branch}/{ordinal:0{width}d}"
            edge_id = f"{event_id}/internal/extra/{branch}/{ordinal:0{width}d}"
            nodes.add(child)
            occupied.update({(parent, port), (child, port)})
            edges.append(
                {
                    "edge_id": edge_id,
                    "kind": "tree",
                    "tail": {"node_id": parent, "port": port},
                    "head": {"node_id": child, "port": port},
                }
            )
            frontier.append(
                (
                    child,
                    deque([add3(column, chirality), add3(column, -chirality)]),
                )
            )
    return {
        "schema_version": "grc9v4-port-graph-v1",
        "live_node_ids": sorted(nodes),
        "edges": sorted(edges, key=lambda row: row["edge_id"]),
        "canonical_module_node_count": node_count,
        "branch_extra_counts": {str(key): counts[key] for key in sorted(counts)},
    }


def transport_covariant_plan(
    base: dict[str, Any],
    target: dict[str, Any],
    port_permutation: dict[str, int],
    branch_permutation: dict[str, int],
) -> dict[str, Any]:
    """Transport a D11-G9 plan into the target event/role namespace."""

    base_event_id = base["expected"]["event_id"]
    target_event_id = target["expected"]["event_id"]

    def map_port(port: int) -> int:
        return port_permutation[str(port)]

    def map_branch(branch: str) -> str:
        return str(branch_permutation[branch])

    def map_node(node_id: str) -> str:
        if node_id == f"{base_event_id}/core":
            return f"{target_event_id}/core"
        if node_id.startswith(f"{base_event_id}/satellite/"):
            branch = node_id.rsplit("/", 1)[1]
            return f"{target_event_id}/satellite/{map_branch(branch)}"
        if node_id.startswith(f"{base_event_id}/extra/"):
            branch, ordinal = node_id.removeprefix(f"{base_event_id}/extra/").split(
                "/", 1
            )
            return f"{target_event_id}/extra/{map_branch(branch)}/{ordinal}"
        if node_id.startswith("outside-"):
            return f"outside-{map_port(int(node_id.removeprefix('outside-')))}"
        raise ValueError(f"unrecognized covariant node role: {node_id}")

    def map_edge_id(edge_id: str) -> str:
        if edge_id.startswith("old-"):
            return f"old-{map_port(int(edge_id.removeprefix('old-')))}"
        if edge_id.startswith(f"{base_event_id}/internal/extra/"):
            branch, ordinal = edge_id.removeprefix(
                f"{base_event_id}/internal/extra/"
            ).split("/", 1)
            return f"{target_event_id}/internal/extra/{map_branch(branch)}/{ordinal}"
        if edge_id.startswith(f"{base_event_id}/internal/"):
            branch = edge_id.removeprefix(f"{base_event_id}/internal/")
            return f"{target_event_id}/internal/{map_branch(branch)}"
        raise ValueError(f"unrecognized covariant edge role: {edge_id}")

    transported_edges = []
    for edge in base["expected"]["target_edges"]:
        transported_edges.append(
            {
                "edge_id": map_edge_id(edge["edge_id"]),
                "kind": edge["kind"],
                "tail": {
                    "node_id": map_node(edge["tail"]["node_id"]),
                    "port": map_port(edge["tail"]["port"]),
                },
                "head": {
                    "node_id": map_node(edge["head"]["node_id"]),
                    "port": map_port(edge["head"]["port"]),
                },
            }
        )
    return {
        "live_node_ids": sorted(
            map_node(node_id) for node_id in base["expected"]["target_live_node_ids"]
        ),
        "edges": sorted(transported_edges, key=lambda row: row["edge_id"]),
    }


def history_channel(
    subject: str,
    policy_id: str,
    disposition: str,
    *,
    source_history_digest: str | None = None,
    target_initializer_id: str | None = None,
    information_loss: str = "none",
) -> dict[str, Any]:
    return {
        "schema_version": "grcv4-history-channel-policy-v1",
        "subject": subject,
        "policy_id": policy_id,
        "disposition": disposition,
        "source_history_digest": source_history_digest,
        "target_initializer_id": target_initializer_id,
        "information_loss": information_loss,
    }


def history_channel_digest(policy: dict[str, Any]) -> str:
    return wrapped_digest(
        "grcv4-history-policy-sha256",
        "grcv4-history-channel-policy-identity-v1",
        "policy",
        policy,
    )


def resource_transform(
    source_nodes: list[str],
    target_nodes: list[str],
    event_id: str,
    shares: tuple[float, float, float],
) -> dict[str, Any]:
    coefficients: list[float] = []
    for target in target_nodes:
        for source in source_nodes:
            coefficient = 0.0
            if target == source and source != "source-s":
                coefficient = 1.0
            for branch, share in zip((1, 2, 3), shares, strict=True):
                if target == f"{event_id}/satellite/{branch}" and source == "source-s":
                    coefficient = share
            coefficients.append(coefficient)
    return {
        "schema_version": "grcv4-resource-event-transform-v1",
        "policy_id": "grc9v4_source_to_primary_satellite_affine_v1",
        "source_vertex_ids": source_nodes,
        "target_vertex_ids": target_nodes,
        "row_major_coefficients": coefficients,
        "target_increment": [0 for _ in target_nodes],
    }


def persistent_expansion_vector(
    *,
    g9_id: str,
    expansion_policy_digest: str,
) -> dict[str, Any]:
    vector_id = "G9-EXPAND-C-PC-CARRIER-RESET"
    degree, chirality, phase = 30, 1, None
    source_weights = {f"old-{port}": 1 for port in range(1, 10)}
    source_params = resolved_params(source_weights, "C_PC")
    source_params_id = identity("grcv4-params-sha256", source_params)
    source_profile_payload = profile_payload(source_params_id, "C_PC")
    source_profile_id = identity("grcv4-profile-sha256", source_profile_payload)
    template = profile_template(source_profile_id, "C_PC")
    template_id = identity("grcv4-profile-template-sha256", template)
    source_model_payload = {
        "schema_version": "grc9v4-complete-identity-v1",
        "grcv4_complete_profile_id": source_profile_id,
        "specialization_id": g9_id,
    }
    source_model_id = identity("grc9v4-model-sha256", source_model_payload)
    graph_payload = source_graph()
    source_graph_id = identity("grc-graph-sha256", graph_payload)
    source_nodes = graph_payload["live_node_ids"]
    source_resource = [3 if node == "source-s" else 0 for node in source_nodes]
    source_carrier = [0.5, -0.25]
    source_carrier_payload = {
        "schema_version": "grcv4-history-content-identity-v1",
        "subject": "carrier",
        "content": source_carrier,
    }
    source_carrier_digest = identity(
        "grcv4-history-content-sha256", source_carrier_payload
    )
    target_carrier = [0, 0]
    target_carrier_payload = {
        "schema_version": "grcv4-history-content-identity-v1",
        "subject": "carrier",
        "content": target_carrier,
    }
    target_carrier_digest = identity(
        "grcv4-history-content-sha256", target_carrier_payload
    )
    source_authoritative = {
        "C": source_resource,
        "W_A": None,
        "Z_4": source_carrier,
    }
    source_reset_payload = {
        "schema_version": "grc9v4-reset-baseline-v1",
        "active_model_identity": source_model_id,
        "graph_digest": source_graph_id,
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "authoritative": source_authoritative,
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
    }
    source_reset_id = identity("grcv4-reset-sha256", source_reset_payload)
    source_state_payload = {
        "schema_version": "grcv4-scientific-state-v1",
        "active_model_identity": source_model_id,
        "graph_digest": source_graph_id,
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "step_index": 1,
        "time": 1,
        "authoritative": source_authoritative,
        "reset_digest": source_reset_id,
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
        "context_value_digest": None,
    }
    source_state_id = identity("grcv4-state-sha256", source_state_payload)
    candidate_policy = history_channel(
        "candidate", "candidate_c_rederive_no_history_v1", "rederived"
    )
    carrier_policy = history_channel(
        "carrier",
        "whole_carrier_reset_with_loss_receipt_v1",
        "whole_carrier_reset",
        source_history_digest=source_carrier_digest,
        target_initializer_id="zero_carrier_v1",
        information_loss="carrier_history_loss",
    )
    candidate_policy_digest = history_channel_digest(candidate_policy)
    carrier_policy_digest = history_channel_digest(carrier_policy)
    history_policy = {
        "schema_version": "grc9v4-expansion-history-policy-v2",
        "candidate": candidate_policy,
        "carrier": carrier_policy,
        "candidate_history_policy_digest": candidate_policy_digest,
        "carrier_history_policy_digest": carrier_policy_digest,
    }
    event_payload = {
        "schema_version": "grc9v4-expansion-event-identity-v1",
        "source_state_digest": source_state_id,
        "source_graph_digest": source_graph_id,
        "source_node_id": "source-s",
        "target_profile_template_id": template_id,
        "target_specialization_id": g9_id,
        "target_effective_degree": degree,
        "canonical_module_node_count": canonical_node_count(degree),
        "module_chirality": chirality,
        "growth_phase": phase,
        "expansion_policy_id": "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
        "expansion_policy_digest": expansion_policy_digest,
        "bond_seed": 2,
        "resource_distribution": [0.5, 0.25, 0.25],
        "candidate_history_policy_digest": candidate_policy_digest,
        "carrier_history_policy_digest": carrier_policy_digest,
    }
    event_id = identity("grc-event-sha256", event_payload)
    plan = build_target_plan(event_id, degree, chirality, phase)
    target_graph_payload = {
        key: value
        for key, value in plan.items()
        if key not in {"canonical_module_node_count", "branch_extra_counts"}
    }
    target_graph_id = identity("grc-graph-sha256", target_graph_payload)
    target_weights = {
        edge["edge_id"]: (1 if edge["kind"] == "boundary" else 2)
        for edge in plan["edges"]
    }
    target_params = resolved_params(target_weights, "C_PC")
    target_params_id = identity("grcv4-params-sha256", target_params)
    target_profile_payload = profile_payload(target_params_id, "C_PC")
    target_profile_id = identity("grcv4-profile-sha256", target_profile_payload)
    target_model_payload = {
        "schema_version": "grc9v4-complete-identity-v1",
        "grcv4_complete_profile_id": target_profile_id,
        "specialization_id": g9_id,
    }
    target_model_id = identity("grc9v4-model-sha256", target_model_payload)
    resource_by_node = {node: 0 for node in plan["live_node_ids"]}
    for branch, share in zip((1, 2, 3), (0.5, 0.25, 0.25), strict=True):
        resource_by_node[f"{event_id}/satellite/{branch}"] = 3 * share
    target_resource = [resource_by_node[node] for node in plan["live_node_ids"]]
    transform = resource_transform(
        source_nodes, plan["live_node_ids"], event_id, (0.5, 0.25, 0.25)
    )
    transform_digest = wrapped_digest(
        "grcv4-resource-transform-sha256",
        "grcv4-resource-transform-identity-v1",
        "transform",
        transform,
    )
    history_bundle_digest = wrapped_digest(
        "grcv4-history-map-sha256",
        "grc9v4-expansion-history-identity-v1",
        "history_policy",
        history_policy,
    )
    target_authoritative = {
        "C": target_resource,
        "W_A": None,
        "Z_4": target_carrier,
    }
    target_reset_payload = {
        "schema_version": "grc9v4-reset-baseline-v1",
        "active_model_identity": target_model_id,
        "graph_digest": target_graph_id,
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "authoritative": target_authoritative,
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
    }
    target_reset_id = identity("grcv4-reset-sha256", target_reset_payload)
    target_state_payload = {
        "schema_version": "grcv4-scientific-state-v1",
        "active_model_identity": target_model_id,
        "graph_digest": target_graph_id,
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "step_index": 1,
        "time": 1,
        "authoritative": target_authoritative,
        "reset_digest": target_reset_id,
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
        "context_value_digest": None,
    }
    target_state_id = identity("grcv4-state-sha256", target_state_payload)
    receipt_payload = {
        "schema_version": "grcv4-topology-event-receipt-v1",
        "core": {
            "operation_id": f"operation:{vector_id}",
            "source_state_digest": source_state_id,
            "target_state_digest": target_state_id,
            "source_graph_digest": source_graph_id,
            "target_graph_digest": target_graph_id,
            "source_model_identity": source_model_id,
            "target_model_identity": target_model_id,
            "source_authoritative_digest": wrapped_digest(
                "grcv4-authoritative-sha256",
                "grcv4-authoritative-state-identity-v1",
                "authoritative",
                source_authoritative,
            ),
            "target_authoritative_digest": wrapped_digest(
                "grcv4-authoritative-sha256",
                "grcv4-authoritative-state-identity-v1",
                "authoritative",
                target_authoritative,
            ),
            "source_reset_digest": source_reset_id,
            "target_reset_digest": target_reset_id,
            "resource_transform_digest": transform_digest,
            "history_bundle_digest": history_bundle_digest,
            "actual_charge_delta": 0,
            "information_losses": ["carrier_history_loss"],
            "disposition": "committed",
            "parent_receipt_ids": [],
        },
        "event_id": event_id,
        "history": {
            "schema_version": "grcv4-history-bundle-receipt-v1",
            "candidate": {
                "subject": "candidate",
                "disposition": "rederived",
                "source_history_digest": None,
                "target_history_digest": None,
                "information_loss": "none",
            },
            "carrier": {
                "subject": "carrier",
                "disposition": "whole_carrier_reset",
                "source_history_digest": source_carrier_digest,
                "target_history_digest": target_carrier_digest,
                "information_loss": "carrier_history_loss",
            },
        },
    }
    receipt_id = identity("grc-receipt-sha256", receipt_payload)
    commit_payload = {
        "schema_version": "grcv4-commit-payload-v1",
        "operation_id": f"operation:{vector_id}",
        "source_state_digest": source_state_id,
        "target_state_digest": target_state_id,
        "emitted_receipt_ids": [receipt_id],
        "target_step_index": 1,
        "target_time": 1,
    }
    commit_id = identity("grc-commit-sha256", commit_payload)
    target_lifecycle_payload = {
        "schema_version": "grcv4-lifecycle-envelope-v1",
        "scientific_state_digest": target_state_id,
        "receipt_ids": [receipt_id],
    }
    target_lifecycle_id = identity("grcv4-lifecycle-sha256", target_lifecycle_payload)
    return {
        "fixture_id": vector_id,
        "profile_family_id": "C_PC",
        "request": {
            "schema_version": "grc9v4-expansion-event-request-v1",
            "operation_id": f"operation:{vector_id}",
            "source_state_digest": source_state_id,
            "source_graph_digest": source_graph_id,
            "source_node_id": "source-s",
            "target_profile_template_id": template_id,
            "target_specialization_id": g9_id,
            "expansion_policy_id": "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
            "target_effective_degree": degree,
            "module_chirality": chirality,
            "growth_phase": phase,
            "resource_distribution": [0.5, 0.25, 0.25],
            "history_policy": history_policy,
            "expected_event_id": event_id,
            "expected_target_graph_digest": target_graph_id,
        },
        "event_identity_payload": event_payload,
        "event_identity_canonical_jcs_utf8": jcs(event_payload),
        "expected": {
            "disposition": "committed",
            "committed": True,
            "event_id": event_id,
            "canonical_module_node_count": canonical_node_count(degree),
            "branch_extra_counts": plan["branch_extra_counts"],
            "target_live_node_ids": plan["live_node_ids"],
            "target_edges": plan["edges"],
            "target_graph_digest": target_graph_id,
            "target_params_id": target_params_id,
            "target_complete_profile_id": target_profile_id,
            "target_model_identity": target_model_id,
            "target_W_C_tr": target_weights,
            "target_resource_by_node": resource_by_node,
            "resource_transform": transform,
            "resource_transform_digest": transform_digest,
            "history_bundle_digest": history_bundle_digest,
            "source_carrier": source_carrier,
            "target_carrier": target_carrier,
            "source_carrier_digest": source_carrier_digest,
            "target_carrier_digest": target_carrier_digest,
            "target_reset_digest": target_reset_id,
            "target_state_digest": target_state_id,
            "emitted_receipt_ids": [receipt_id],
            "emitted_receipts": [
                {
                    "schema_version": "grcv4-successful-receipt-envelope-v1",
                    "receipt_id": receipt_id,
                    "commit_id": commit_id,
                    "identity_payload": receipt_payload,
                }
            ],
            "commit_id": commit_id,
            "target_lifecycle_digest": target_lifecycle_id,
            "source_node_live_after_commit": False,
            "prestate_digest_equals_poststate_digest": False,
            "identity_payloads": {
                "target_graph": target_graph_payload,
                "target_params": target_params,
                "target_profile": target_profile_payload,
                "target_model": target_model_payload,
                "target_reset": target_reset_payload,
                "target_state": target_state_payload,
                "resource_transform": wrapped_payload(
                    "grcv4-resource-transform-identity-v1", "transform", transform
                ),
                "candidate_history_policy": wrapped_payload(
                    "grcv4-history-channel-policy-identity-v1",
                    "policy",
                    candidate_policy,
                ),
                "carrier_history_policy": wrapped_payload(
                    "grcv4-history-channel-policy-identity-v1",
                    "policy",
                    carrier_policy,
                ),
                "history_bundle": wrapped_payload(
                    "grc9v4-expansion-history-identity-v1",
                    "history_policy",
                    history_policy,
                ),
                "source_carrier": source_carrier_payload,
                "target_carrier": target_carrier_payload,
                "receipt": receipt_payload,
                "commit": commit_payload,
                "target_lifecycle": target_lifecycle_payload,
            },
        },
        "numeric_comparison_policy": {
            "kind": "exact_for_combinatorial_and_identity_fields",
            "resource_absolute_tolerance": 0,
            "resource_relative_tolerance": 0,
        },
    }


def build() -> dict[str, Any]:
    source_weights = {f"old-{port}": 1 for port in range(1, 10)}
    source_params = resolved_params(source_weights)
    source_params_id = identity("grcv4-params-sha256", source_params)
    source_profile_payload = profile_payload(source_params_id)
    source_profile_id = identity("grcv4-profile-sha256", source_profile_payload)
    template = profile_template(source_profile_id)
    template_id = identity("grcv4-profile-template-sha256", template)
    a_params = resolved_a_os_params()
    a_params_id = identity("grcv4-params-sha256", a_params)
    a_profile_payload = candidate_a_profile_payload(a_params_id)
    a_profile_id = identity("grcv4-profile-sha256", a_profile_payload)
    a_template = candidate_a_profile_template(a_profile_id)
    a_pc_params = resolved_a_pc_params()
    a_pc_params_id = identity("grcv4-params-sha256", a_pc_params)
    a_pc_profile_payload = candidate_a_profile_payload(a_pc_params_id, "A_PC")
    a_pc_profile_id = identity("grcv4-profile-sha256", a_pc_profile_payload)

    g9_params = specialization_params()
    g9_params_id = identity("grc9v4-params-sha256", g9_params)
    g9_payload = specialization_payload(g9_params_id)
    g9_id = identity("grc9v4-specialization-sha256", g9_payload)
    source_model_payload = {
        "schema_version": "grc9v4-complete-identity-v1",
        "grcv4_complete_profile_id": source_profile_id,
        "specialization_id": g9_id,
    }
    source_model_id = identity("grc9v4-model-sha256", source_model_payload)
    a_pc_model_payload = {
        "schema_version": "grc9v4-complete-identity-v1",
        "grcv4_complete_profile_id": a_pc_profile_id,
        "specialization_id": g9_id,
    }
    a_pc_model_id = identity("grc9v4-model-sha256", a_pc_model_payload)

    graph_payload = source_graph()
    source_graph_id = identity("grc-graph-sha256", graph_payload)
    source_graph_envelope = {**graph_payload, "graph_digest": source_graph_id}
    port_graph_envelope_vectors = [
        {
            "vector_id": "GRC9V4-PORT-GRAPH-PAYLOAD-DIGEST-ENVELOPE",
            "payload_schema_ref": "port_graph_payload",
            "envelope_schema_ref": "serialized_port_graph",
            "payload": graph_payload,
            "serialized_port_graph": source_graph_envelope,
            "expected": {
                "graph_digest": source_graph_id,
                "graph_digest_omitted_from_preimage": True,
                "envelope_payload_projection_equal": True,
            },
        }
    ]
    source_nodes = graph_payload["live_node_ids"]
    source_resource = [3 if node == "source-s" else 0 for node in source_nodes]
    source_reset_payload = {
        "schema_version": "grc9v4-reset-baseline-v1",
        "active_model_identity": source_model_id,
        "graph_digest": source_graph_id,
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "authoritative": {"C": source_resource, "W_A": None, "Z_4": None},
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
    }
    source_reset_id = identity("grcv4-reset-sha256", source_reset_payload)
    source_state_payload = {
        "schema_version": "grcv4-scientific-state-v1",
        "active_model_identity": source_model_id,
        "graph_digest": source_graph_id,
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "step_index": 1,
        "time": 1,
        "authoritative": {"C": source_resource, "W_A": None, "Z_4": None},
        "reset_digest": source_reset_id,
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
        "context_value_digest": None,
    }
    source_state_id = identity("grcv4-state-sha256", source_state_payload)
    a_pc_authoritative = {
        "C": source_resource,
        "W_A": [1 for _ in graph_payload["edges"]],
        "Z_4": [0.5],
    }
    a_pc_reset_payload = {
        "schema_version": "grc9v4-reset-baseline-v1",
        "active_model_identity": a_pc_model_id,
        "graph_digest": source_graph_id,
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "authoritative": a_pc_authoritative,
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
    }
    a_pc_reset_id = identity("grcv4-reset-sha256", a_pc_reset_payload)
    a_pc_state_payload = {
        "schema_version": "grcv4-scientific-state-v1",
        "active_model_identity": a_pc_model_id,
        "graph_digest": source_graph_id,
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "step_index": 1,
        "time": 1,
        "authoritative": a_pc_authoritative,
        "reset_digest": a_pc_reset_id,
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
        "context_value_digest": None,
    }
    a_pc_state_id = identity("grcv4-state-sha256", a_pc_state_payload)
    source_lifecycle_payload = {
        "schema_version": "grcv4-lifecycle-envelope-v1",
        "scientific_state_digest": source_state_id,
        "receipt_ids": [],
    }
    source_lifecycle_id = identity("grcv4-lifecycle-sha256", source_lifecycle_payload)

    expansion_policy = g9_params["expansion"]
    expansion_policy_id = wrapped_digest(
        "grc9v4-expansion-policy-sha256",
        "grc9v4-expansion-policy-identity-v1",
        "policy",
        expansion_policy,
    )
    candidate_history_policy = history_channel(
        "candidate",
        "candidate_c_rederive_no_history_v1",
        "rederived",
    )
    carrier_history_policy = history_channel(
        "carrier",
        "carrier_not_applicable_v1",
        "not_applicable",
    )
    candidate_history_id = history_channel_digest(candidate_history_policy)
    carrier_history_id = history_channel_digest(carrier_history_policy)
    expansion_history_policy = {
        "schema_version": "grc9v4-expansion-history-policy-v2",
        "candidate": candidate_history_policy,
        "carrier": carrier_history_policy,
        "candidate_history_policy_digest": candidate_history_id,
        "carrier_history_policy_digest": carrier_history_id,
    }
    candidate_loss_source_id = identity(
        "grcv4-history-content-sha256",
        {
            "schema_version": "grcv4-history-content-identity-v1",
            "subject": "candidate",
            "content": [1],
        },
    )
    carrier_loss_source_id = identity(
        "grcv4-history-content-sha256",
        {
            "schema_version": "grcv4-history-content-identity-v1",
            "subject": "carrier",
            "content": [1],
        },
    )
    candidate_loss_policy = history_channel(
        "candidate",
        "candidate_history_explicit_loss_v1",
        "explicit_loss",
        source_history_digest=candidate_loss_source_id,
        information_loss="candidate_history_loss",
    )
    carrier_loss_policy = history_channel(
        "carrier",
        "carrier_history_explicit_loss_v1",
        "explicit_loss",
        source_history_digest=carrier_loss_source_id,
        information_loss="carrier_history_loss",
    )
    multi_loss_history_policy = {
        "schema_version": "grcv4-history-bundle-policy-v1",
        "candidate": candidate_loss_policy,
        "carrier": carrier_loss_policy,
    }
    multi_loss_history_digest = wrapped_digest(
        "grcv4-history-map-sha256",
        "grcv4-history-bundle-identity-v1",
        "history_bundle",
        multi_loss_history_policy,
    )
    identity_resource_transform = {
        "schema_version": "grcv4-resource-event-transform-v1",
        "policy_id": "identity_resource_transport_v1",
        "source_vertex_ids": ["source-s"],
        "target_vertex_ids": ["source-s"],
        "row_major_coefficients": [1],
        "target_increment": [0],
    }
    identity_resource_transform_id = wrapped_digest(
        "grcv4-resource-transform-sha256",
        "grcv4-resource-transform-identity-v1",
        "transform",
        identity_resource_transform,
    )
    a_pc_authoritative_id = wrapped_digest(
        "grcv4-authoritative-sha256",
        "grcv4-authoritative-state-identity-v1",
        "authoritative",
        a_pc_authoritative,
    )
    target_authoritative_id = wrapped_digest(
        "grcv4-authoritative-sha256",
        "grcv4-authoritative-state-identity-v1",
        "authoritative",
        source_state_payload["authoritative"],
    )
    multi_loss_receipt_payload = {
        "schema_version": "grcv4-profile-migration-receipt-v1",
        "core": {
            "operation_id": "operation:IDENTITY-GRCV4-MULTI-LOSS-RECEIPT",
            "source_state_digest": a_pc_state_id,
            "target_state_digest": source_state_id,
            "source_graph_digest": source_graph_id,
            "target_graph_digest": source_graph_id,
            "source_model_identity": a_pc_model_id,
            "target_model_identity": source_model_id,
            "source_authoritative_digest": a_pc_authoritative_id,
            "target_authoritative_digest": target_authoritative_id,
            "source_reset_digest": a_pc_reset_id,
            "target_reset_digest": source_reset_id,
            "resource_transform_digest": identity_resource_transform_id,
            "history_bundle_digest": multi_loss_history_digest,
            "actual_charge_delta": 0,
            "information_losses": [
                "candidate_history_loss",
                "carrier_history_loss",
            ],
            "disposition": "committed",
            "parent_receipt_ids": [],
        },
        "history": {
            "schema_version": "grcv4-history-bundle-receipt-v1",
            "candidate": {
                "subject": "candidate",
                "disposition": "explicit_loss",
                "source_history_digest": candidate_loss_source_id,
                "target_history_digest": None,
                "information_loss": "candidate_history_loss",
            },
            "carrier": {
                "subject": "carrier",
                "disposition": "explicit_loss",
                "source_history_digest": carrier_loss_source_id,
                "target_history_digest": None,
                "information_loss": "carrier_history_loss",
            },
        },
    }

    identity_vectors = [
        identity_vector(
            "IDENTITY-GRCV4-PARAMS-C-OS",
            "#/$defs/resolved_params",
            "grcv4-params-sha256",
            source_params,
        ),
        identity_vector(
            "IDENTITY-GRCV4-PROFILE-C-OS",
            "#/$defs/profile_identity_payload",
            "grcv4-profile-sha256",
            source_profile_payload,
        ),
        identity_vector(
            "IDENTITY-GRCV4-PROFILE-TEMPLATE-C-OS",
            "#/$defs/profile_template_payload",
            "grcv4-profile-template-sha256",
            template,
        ),
        identity_vector(
            "IDENTITY-GRCV4-PROFILE-TEMPLATE-A-OS",
            "#/$defs/profile_template_payload",
            "grcv4-profile-template-sha256",
            a_template,
        ),
        identity_vector(
            "IDENTITY-GRC9V4-PARAMS",
            "#/$defs/resolved_specialization",
            "grc9v4-params-sha256",
            g9_params,
        ),
        identity_vector(
            "IDENTITY-GRC9V4-SPECIALIZATION",
            "#/$defs/specialization_identity_payload",
            "grc9v4-specialization-sha256",
            g9_payload,
        ),
        identity_vector(
            "IDENTITY-GRC9V4-COMPLETE-MODEL",
            "#/$defs/complete_model_identity_payload",
            "grc9v4-model-sha256",
            source_model_payload,
        ),
        identity_vector(
            "IDENTITY-GRC9V4-SOURCE-GRAPH",
            "port_graph_payload",
            "grc-graph-sha256",
            graph_payload,
        ),
        identity_vector(
            "IDENTITY-GRC9V4-RESET",
            "#/$defs/reset_payload",
            "grcv4-reset-sha256",
            source_reset_payload,
        ),
        identity_vector(
            "IDENTITY-GRCV4-STATE",
            "#/$defs/scientific_state_payload",
            "grcv4-state-sha256",
            source_state_payload,
        ),
        identity_vector(
            "IDENTITY-GRCV4-LIFECYCLE",
            "#/$defs/lifecycle_envelope_payload",
            "grcv4-lifecycle-sha256",
            source_lifecycle_payload,
        ),
        identity_vector(
            "IDENTITY-GRCV4-MULTI-LOSS-RECEIPT",
            "#/$defs/profile_migration_receipt_identity_payload",
            "grc-receipt-sha256",
            multi_loss_receipt_payload,
        ),
    ]

    expansion_vectors: list[dict[str, Any]] = []
    event_cases = [
        ("G9-EXPAND-D30-CHIRALITY-POSITIVE", 30, 1, None),
        ("G9-EXPAND-D30-CHIRALITY-NEGATIVE", 30, -1, None),
    ]
    event_cases.extend(
        (
            f"G9-EXPAND-D31-CHIRALITY-{'POSITIVE' if chirality == 1 else 'NEGATIVE'}-PHASE-{phase}",
            31,
            chirality,
            phase,
        )
        for chirality in (-1, 1)
        for phase in (1, 2, 3)
    )
    event_cases.extend(
        [
            ("G9-EXPAND-D45-CHIRALITY-POSITIVE", 45, 1, None),
            ("G9-EXPAND-D45-CHIRALITY-NEGATIVE", 45, -1, None),
        ]
    )
    event_cases.extend(
        (
            f"G9-EXPAND-D52-CHIRALITY-{'POSITIVE' if chirality == 1 else 'NEGATIVE'}-PHASE-{phase}",
            52,
            chirality,
            phase,
        )
        for chirality in (-1, 1)
        for phase in (1, 2, 3)
    )
    for vector_id, degree, chirality, phase in event_cases:
        node_count = canonical_node_count(degree)
        event_payload = {
            "schema_version": "grc9v4-expansion-event-identity-v1",
            "source_state_digest": source_state_id,
            "source_graph_digest": source_graph_id,
            "source_node_id": "source-s",
            "target_profile_template_id": template_id,
            "target_specialization_id": g9_id,
            "target_effective_degree": degree,
            "canonical_module_node_count": node_count,
            "module_chirality": chirality,
            "growth_phase": phase,
            "expansion_policy_id": "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
            "expansion_policy_digest": expansion_policy_id,
            "bond_seed": 2,
            "resource_distribution": [0.5, 0.25, 0.25],
            "candidate_history_policy_digest": candidate_history_id,
            "carrier_history_policy_digest": carrier_history_id,
        }
        event_id = identity("grc-event-sha256", event_payload)
        plan = build_target_plan(event_id, degree, chirality, phase)
        target_graph_payload = {
            key: value
            for key, value in plan.items()
            if key not in {"canonical_module_node_count", "branch_extra_counts"}
        }
        target_graph_id = identity("grc-graph-sha256", target_graph_payload)
        target_weights = {
            edge["edge_id"]: (1 if edge["kind"] == "boundary" else 2)
            for edge in plan["edges"]
        }
        target_params = resolved_params(target_weights)
        target_params_id = identity("grcv4-params-sha256", target_params)
        target_profile_payload = profile_payload(target_params_id)
        target_profile_id = identity("grcv4-profile-sha256", target_profile_payload)
        target_model_payload = {
            "schema_version": "grc9v4-complete-identity-v1",
            "grcv4_complete_profile_id": target_profile_id,
            "specialization_id": g9_id,
        }
        target_model_id = identity("grc9v4-model-sha256", target_model_payload)
        resource_by_node = {node: 0 for node in plan["live_node_ids"]}
        for branch, share in zip((1, 2, 3), (0.5, 0.25, 0.25), strict=True):
            resource_by_node[f"{event_id}/satellite/{branch}"] = 3 * share
        target_resource = [resource_by_node[node] for node in plan["live_node_ids"]]
        event_resource_transform = resource_transform(
            source_nodes,
            plan["live_node_ids"],
            event_id,
            (0.5, 0.25, 0.25),
        )
        event_resource_transform_digest = wrapped_digest(
            "grcv4-resource-transform-sha256",
            "grcv4-resource-transform-identity-v1",
            "transform",
            event_resource_transform,
        )
        history_bundle_digest = wrapped_digest(
            "grcv4-history-map-sha256",
            "grc9v4-expansion-history-identity-v1",
            "history_policy",
            expansion_history_policy,
        )
        target_reset_payload = {
            "schema_version": "grc9v4-reset-baseline-v1",
            "active_model_identity": target_model_id,
            "graph_digest": target_graph_id,
            "orientation_identity": "tail_to_head_edge_id_order_v1",
            "authoritative": {"C": target_resource, "W_A": None, "Z_4": None},
            "Q_target": 3,
            "context_contract_id": "constant_zero_context_v1",
        }
        target_reset_id = identity("grcv4-reset-sha256", target_reset_payload)
        target_state_payload = {
            "schema_version": "grcv4-scientific-state-v1",
            "active_model_identity": target_model_id,
            "graph_digest": target_graph_id,
            "orientation_identity": "tail_to_head_edge_id_order_v1",
            "step_index": 1,
            "time": 1,
            "authoritative": {"C": target_resource, "W_A": None, "Z_4": None},
            "reset_digest": target_reset_id,
            "Q_target": 3,
            "context_contract_id": "constant_zero_context_v1",
            "context_value_digest": None,
        }
        target_state_id = identity("grcv4-state-sha256", target_state_payload)
        receipt_identity_payload = {
            "schema_version": "grcv4-topology-event-receipt-v1",
            "core": {
                "operation_id": f"operation:{vector_id}",
                "source_state_digest": source_state_id,
                "target_state_digest": target_state_id,
                "source_graph_digest": source_graph_id,
                "target_graph_digest": target_graph_id,
                "source_model_identity": source_model_id,
                "target_model_identity": target_model_id,
                "source_authoritative_digest": wrapped_digest(
                    "grcv4-authoritative-sha256",
                    "grcv4-authoritative-state-identity-v1",
                    "authoritative",
                    source_state_payload["authoritative"],
                ),
                "target_authoritative_digest": wrapped_digest(
                    "grcv4-authoritative-sha256",
                    "grcv4-authoritative-state-identity-v1",
                    "authoritative",
                    target_state_payload["authoritative"],
                ),
                "source_reset_digest": source_reset_id,
                "target_reset_digest": target_reset_id,
                "resource_transform_digest": event_resource_transform_digest,
                "history_bundle_digest": history_bundle_digest,
                "actual_charge_delta": 0,
                "information_losses": [],
                "disposition": "committed",
                "parent_receipt_ids": [],
            },
            "event_id": event_id,
            "history": {
                "schema_version": "grcv4-history-bundle-receipt-v1",
                "candidate": {
                    "subject": "candidate",
                    "disposition": "rederived",
                    "source_history_digest": None,
                    "target_history_digest": None,
                    "information_loss": "none",
                },
                "carrier": {
                    "subject": "carrier",
                    "disposition": "not_applicable",
                    "source_history_digest": None,
                    "target_history_digest": None,
                    "information_loss": "none",
                },
            },
        }
        receipt_id = identity("grc-receipt-sha256", receipt_identity_payload)
        commit_payload = {
            "schema_version": "grcv4-commit-payload-v1",
            "operation_id": f"operation:{vector_id}",
            "source_state_digest": source_state_id,
            "target_state_digest": target_state_id,
            "emitted_receipt_ids": [receipt_id],
            "target_step_index": 1,
            "target_time": 1,
        }
        commit_id = identity("grc-commit-sha256", commit_payload)
        finalized_receipt = {
            "schema_version": "grcv4-successful-receipt-envelope-v1",
            "receipt_id": receipt_id,
            "commit_id": commit_id,
            "identity_payload": receipt_identity_payload,
        }
        target_lifecycle_payload = {
            "schema_version": "grcv4-lifecycle-envelope-v1",
            "scientific_state_digest": target_state_id,
            "receipt_ids": [receipt_id],
        }
        target_lifecycle_id = identity(
            "grcv4-lifecycle-sha256", target_lifecycle_payload
        )
        expansion_vectors.append(
            {
                "fixture_id": vector_id,
                "request": {
                    "schema_version": "grc9v4-expansion-event-request-v1",
                    "operation_id": f"operation:{vector_id}",
                    "source_state_digest": source_state_id,
                    "source_graph_digest": source_graph_id,
                    "source_node_id": "source-s",
                    "target_profile_template_id": template_id,
                    "target_specialization_id": g9_id,
                    "expansion_policy_id": "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
                    "target_effective_degree": degree,
                    "module_chirality": chirality,
                    "growth_phase": phase,
                    "resource_distribution": [0.5, 0.25, 0.25],
                    "history_policy": expansion_history_policy,
                    "expected_event_id": event_id,
                    "expected_target_graph_digest": target_graph_id,
                },
                "event_identity_payload": event_payload,
                "event_identity_canonical_jcs_utf8": jcs(event_payload),
                "expected": {
                    "disposition": "committed",
                    "committed": True,
                    "event_id": event_id,
                    "canonical_module_node_count": node_count,
                    "branch_extra_counts": plan["branch_extra_counts"],
                    "target_live_node_ids": plan["live_node_ids"],
                    "target_edges": plan["edges"],
                    "target_graph_digest": target_graph_id,
                    "target_params_id": target_params_id,
                    "target_complete_profile_id": target_profile_id,
                    "target_model_identity": target_model_id,
                    "target_W_C_tr": target_weights,
                    "target_resource_by_node": resource_by_node,
                    "resource_transform": event_resource_transform,
                    "resource_transform_digest": event_resource_transform_digest,
                    "history_bundle_digest": history_bundle_digest,
                    "target_reset_digest": target_reset_id,
                    "target_state_digest": target_state_id,
                    "emitted_receipt_ids": [receipt_id],
                    "emitted_receipts": [finalized_receipt],
                    "commit_id": commit_id,
                    "target_lifecycle_digest": target_lifecycle_id,
                    "source_node_live_after_commit": False,
                    "prestate_digest_equals_poststate_digest": False,
                    "identity_payloads": {
                        "target_graph": target_graph_payload,
                        "target_params": target_params,
                        "target_profile": target_profile_payload,
                        "target_model": target_model_payload,
                        "target_reset": target_reset_payload,
                        "target_state": target_state_payload,
                        "resource_transform": wrapped_payload(
                            "grcv4-resource-transform-identity-v1",
                            "transform",
                            event_resource_transform,
                        ),
                        "candidate_history_policy": wrapped_payload(
                            "grcv4-history-channel-policy-identity-v1",
                            "policy",
                            candidate_history_policy,
                        ),
                        "carrier_history_policy": wrapped_payload(
                            "grcv4-history-channel-policy-identity-v1",
                            "policy",
                            carrier_history_policy,
                        ),
                        "history_bundle": wrapped_payload(
                            "grc9v4-expansion-history-identity-v1",
                            "history_policy",
                            expansion_history_policy,
                        ),
                        "receipt": receipt_identity_payload,
                        "commit": commit_payload,
                        "target_lifecycle": target_lifecycle_payload,
                    },
                },
                "numeric_comparison_policy": {
                    "kind": "exact_for_combinatorial_and_identity_fields",
                    "resource_absolute_tolerance": 0,
                    "resource_relative_tolerance": 0,
                },
            }
        )

    expansion_vectors.append(
        persistent_expansion_vector(
            g9_id=g9_id,
            expansion_policy_digest=expansion_policy_id,
        )
    )

    generic_source_graph = {
        "schema_version": "grcv4-serialized-graph-v1",
        "live_node_ids": ["u", "v"],
        "oriented_edges": [
            {"edge_id": "e-uv", "tail_node_id": "u", "head_node_id": "v"}
        ],
    }
    generic_source_graph_id = identity("grc-graph-sha256", generic_source_graph)
    generic_source_params = resolved_params({"e-uv": 1})
    generic_source_params_id = identity("grcv4-params-sha256", generic_source_params)
    generic_source_profile_payload = profile_payload(generic_source_params_id)
    generic_source_profile_id = identity(
        "grcv4-profile-sha256", generic_source_profile_payload
    )
    generic_source_authoritative = {"C": [1, 2], "W_A": None, "Z_4": None}
    generic_source_reset_payload = {
        "schema_version": "grcv4-reset-baseline-v1",
        "active_model_identity": generic_source_profile_id,
        "graph_digest": generic_source_graph_id,
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "authoritative": generic_source_authoritative,
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
    }
    generic_source_reset_id = identity(
        "grcv4-reset-sha256", generic_source_reset_payload
    )
    generic_source_state_payload = {
        "schema_version": "grcv4-scientific-state-v1",
        "active_model_identity": generic_source_profile_id,
        "graph_digest": generic_source_graph_id,
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "step_index": 0,
        "time": 0,
        "authoritative": generic_source_authoritative,
        "reset_digest": generic_source_reset_id,
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
        "context_value_digest": None,
    }
    generic_source_state_id = identity(
        "grcv4-state-sha256", generic_source_state_payload
    )
    generic_target_graph = {
        "schema_version": "grcv4-serialized-graph-v1",
        "live_node_ids": ["u", "v", "w"],
        "oriented_edges": [
            {"edge_id": "e-uv", "tail_node_id": "u", "head_node_id": "v"},
            {"edge_id": "e-vw", "tail_node_id": "v", "head_node_id": "w"},
        ],
    }
    generic_target_graph_id = identity("grc-graph-sha256", generic_target_graph)
    generic_target_params = resolved_params({"e-uv": 1, "e-vw": 2})
    generic_target_params_id = identity("grcv4-params-sha256", generic_target_params)
    generic_target_profile_payload = profile_payload(generic_target_params_id)
    generic_target_profile_id = identity(
        "grcv4-profile-sha256", generic_target_profile_payload
    )
    generic_transform = {
        "schema_version": "grcv4-resource-event-transform-v1",
        "policy_id": "identity_embedding_plus_external_increment_v1",
        "source_vertex_ids": ["u", "v"],
        "target_vertex_ids": ["u", "v", "w"],
        "row_major_coefficients": [1, 0, 0, 1, 0, 0],
        "target_increment": [0, 0, 0.5],
    }
    generic_transform_digest = wrapped_digest(
        "grcv4-resource-transform-sha256",
        "grcv4-resource-transform-identity-v1",
        "transform",
        generic_transform,
    )
    generic_history_bundle = {
        "schema_version": "grcv4-history-bundle-policy-v1",
        "candidate": candidate_history_policy,
        "carrier": carrier_history_policy,
    }
    generic_history_digest = wrapped_digest(
        "grcv4-history-map-sha256",
        "grcv4-history-bundle-identity-v1",
        "history_bundle",
        generic_history_bundle,
    )
    mapped_event_payload = {
        "schema_version": "grcv4-mapped-topology-event-identity-v1",
        "source_state_digest": generic_source_state_id,
        "source_graph_digest": generic_source_graph_id,
        "target_graph_digest": generic_target_graph_id,
        "target_profile_id": generic_target_profile_id,
        "resource_transform_digest": generic_transform_digest,
        "history_bundle_digest": generic_history_digest,
    }
    mapped_event_id = identity("grc-event-sha256", mapped_event_payload)
    mapped_event_vectors = [
        {
            "fixture_id": "GENERIC-MAPPED-EVENT-NONZERO-RESOURCE-INCREMENT",
            "request": {
                "schema_version": "grcv4-mapped-topology-event-request-v1",
                "operation_id": "operation:GENERIC-MAPPED-EVENT-NONZERO-RESOURCE-INCREMENT",
                "source_state_digest": generic_source_state_id,
                "source_graph_digest": generic_source_graph_id,
                "target_graph": generic_target_graph,
                "target_profile_id": generic_target_profile_id,
                "resource_transform": generic_transform,
                "history_policy": generic_history_bundle,
                "metadata": {"note": "excluded_from_event_identity"},
            },
            "event_identity_payload": mapped_event_payload,
            "event_identity_canonical_jcs_utf8": jcs(mapped_event_payload),
            "expected": {
                "event_id": mapped_event_id,
                "source_resource": [1, 2],
                "target_resource": [1, 2, 0.5],
                "source_charge": 3,
                "target_charge": 3.5,
                "actual_charge_delta": 0.5,
                "target_Q_target": 3.5,
                "metadata_affects_event_id": False,
                "resource_transform_digest": generic_transform_digest,
                "history_bundle_digest": generic_history_digest,
            },
        }
    ]

    first_expansion_payloads = expansion_vectors[0]["expected"]["identity_payloads"]
    subdigest_vectors = [
        identity_vector(
            "SUBDIGEST-AUTHORITATIVE-STATE",
            "#/$defs/authoritative_state_identity_payload",
            "grcv4-authoritative-sha256",
            wrapped_payload(
                "grcv4-authoritative-state-identity-v1",
                "authoritative",
                source_state_payload["authoritative"],
            ),
        ),
        identity_vector(
            "SUBDIGEST-W-C-TR",
            "#/$defs/wctr_identity_payload",
            "grcv4-wctr-sha256",
            wrapped_payload("grcv4-wctr-identity-v1", "W_C_tr", source_weights),
        ),
        identity_vector(
            "SUBDIGEST-RESOURCE-TRANSFORM",
            "#/$defs/resource_transform_identity_payload",
            "grcv4-resource-transform-sha256",
            first_expansion_payloads["resource_transform"],
        ),
        identity_vector(
            "SUBDIGEST-CANDIDATE-HISTORY-POLICY",
            "#/$defs/history_channel_policy_identity_payload",
            "grcv4-history-policy-sha256",
            first_expansion_payloads["candidate_history_policy"],
        ),
        identity_vector(
            "SUBDIGEST-CARRIER-HISTORY-POLICY",
            "#/$defs/history_channel_policy_identity_payload",
            "grcv4-history-policy-sha256",
            first_expansion_payloads["carrier_history_policy"],
        ),
        identity_vector(
            "SUBDIGEST-EXPANSION-HISTORY-BUNDLE",
            "#/$defs/expansion_history_identity_payload",
            "grcv4-history-map-sha256",
            first_expansion_payloads["history_bundle"],
        ),
        identity_vector(
            "SUBDIGEST-GENERIC-HISTORY-BUNDLE",
            "#/$defs/history_bundle_identity_payload",
            "grcv4-history-map-sha256",
            wrapped_payload(
                "grcv4-history-bundle-identity-v1",
                "history_bundle",
                generic_history_bundle,
            ),
        ),
        identity_vector(
            "SUBDIGEST-GRC9-EXPANSION-POLICY",
            "#/$defs/expansion_policy_identity_payload",
            "grc9v4-expansion-policy-sha256",
            wrapped_payload(
                "grc9v4-expansion-policy-identity-v1",
                "policy",
                expansion_policy,
            ),
        ),
        identity_vector(
            "SUBDIGEST-K4-BASE",
            "#/$defs/k4_identity_payload",
            "grcv4-k4-sha256",
            wrapped_payload("grcv4-k4-identity-v1", "K4_base", [[1, 0], [0, 1]]),
        ),
        identity_vector(
            "SUBDIGEST-REFERENCE-HODGE",
            "#/$defs/reference_hodge_identity_payload",
            "grcv4-hodge-sha256",
            wrapped_payload(
                "grcv4-reference-hodge-identity-v1",
                "edge_weights",
                source_weights,
            ),
        ),
    ]

    c_witness = {
        "fixture_id": "C-D11-T3A-THREE-NODE-ALGEBRA-WITNESS",
        "source_script": str(WITNESS.relative_to(ROOT)),
        "source_script_sha256": file_sha256(WITNESS),
        "inputs": {
            "incidence": [[-1, 0], [1, -1], [0, 1]],
            "H0_diagonal": [1, 1.5, 0.8],
            "W_C_tr": [2, 3],
            "eta_C": 0.6,
            "C": [1.2, 1, 0.8],
            "kappa_M_C": 0.35,
            "kappa_Phi_C": 1,
            "resolvent_tau_C": 0.2,
            "zeta_C": 0.4,
            "chi_C": 1,
            "Vprime_C_U": [0, 0, 0],
        },
        "expected": {
            "baseline_potential": [
                0.5276883364946887,
                0.24387147731873257,
                -0.7715598138134211,
            ],
            "baseline_current": [0.34058023101114737, 1.8277763240378764],
            "total_current": [0.5228440005212419, 2.226934257041781],
            "read_current": [0.4556594237752364, 0.9978948325097617],
            "retained_h1_diagonal": [2.6384416824734442, 3.8577990690671062],
            "closure_residual_l2": 6.206335383118183e-17,
            "charge_residual_absolute": 0,
            "baseline_dissipation": 1.952643684081568,
            "retained_geometry_off_effect_l2": 0.4006081131911638,
            "orientation_covariance_error_l2": 0,
        },
        "numeric_comparison_policy": {
            "kind": "binary64_absolute",
            "absolute_tolerance": 1e-12,
            "relative_tolerance": 0,
        },
        "claim_ceiling": "finite_algebra_witness_not_runtime_or_stability_evidence",
    }

    base_request = dict(expansion_vectors[0]["request"])
    base_request["schema_version"] = "grc9v4-expansion-event-request-input-v1"

    def invalid_expansion_input(fixture_id: str, **overrides: Any) -> dict[str, Any]:
        request = dict(base_request)
        request["operation_id"] = f"operation:{fixture_id}"
        request.update(overrides)
        return request

    self_loop_graph = source_graph()
    self_loop_graph["edges"] = [
        edge
        for edge in self_loop_graph["edges"]
        if edge["edge_id"] not in {"old-1", "old-2"}
    ]
    self_loop_graph["edges"].append(
        {
            "edge_id": "source-self-loop",
            "kind": "tree",
            "tail": {"node_id": "source-s", "port": 1},
            "head": {"node_id": "source-s", "port": 2},
        }
    )
    self_loop_graph_id = identity("grc-graph-sha256", self_loop_graph)
    self_loop_reset_payload = {
        **source_reset_payload,
        "graph_digest": self_loop_graph_id,
    }
    self_loop_reset_id = identity("grcv4-reset-sha256", self_loop_reset_payload)
    self_loop_state_payload = {
        **source_state_payload,
        "graph_digest": self_loop_graph_id,
        "reset_digest": self_loop_reset_id,
    }
    self_loop_state_id = identity("grcv4-state-sha256", self_loop_state_payload)
    self_loop_lifecycle_payload = {
        "schema_version": "grcv4-lifecycle-envelope-v1",
        "scientific_state_digest": self_loop_state_id,
        "receipt_ids": [],
    }
    self_loop_lifecycle_id = identity(
        "grcv4-lifecycle-sha256", self_loop_lifecycle_payload
    )

    failure_vectors = [
        {
            "fixture_id": "COMMON-NEGATIVE-DURATION",
            "request_input": {
                "schema_version": "grcv4-step-request-input-v1",
                "operation_id": "operation:COMMON-NEGATIVE-DURATION",
                "dt": -0.25,
                "context_value": {},
                "boundary_input": None,
                "external_source": None,
            },
            "expected": {
                "stage": "admission",
                "code": "invalid_duration",
                "solver_disposition": None,
                "committed": False,
            },
        },
        {
            "fixture_id": "COMMON-CHARGE-MISMATCH",
            "request_input": {
                "schema_version": "grcv4-step-request-input-v1",
                "operation_id": "operation:COMMON-CHARGE-MISMATCH",
                "dt": 0.25,
                "context_value": {},
                "boundary_input": None,
                "external_source": None,
            },
            "harness_fault": {
                "schema_version": "grcv4-conformance-harness-fault-v1",
                "stage": "charge_admission",
                "kind": "force_charge_mismatch",
            },
            "expected": {
                "stage": "charge_admission",
                "code": "charge_failure",
                "solver_disposition": "valid_root",
                "committed": False,
            },
        },
        {
            "fixture_id": "G9-FAIL-MISSING-CHIRALITY",
            "base_vector_id": "G9-EXPAND-D30-CHIRALITY-POSITIVE",
            "request_input": invalid_expansion_input(
                "G9-FAIL-MISSING-CHIRALITY", module_chirality=None
            ),
            "expected": {
                "stage": "admission",
                "code": "module_chirality_required",
                "solver_disposition": None,
                "committed": False,
            },
        },
        {
            "fixture_id": "G9-FAIL-MISSING-ACTIVE-PHASE",
            "base_vector_id": "G9-EXPAND-D31-CHIRALITY-POSITIVE-PHASE-1",
            "request_input": invalid_expansion_input(
                "G9-FAIL-MISSING-ACTIVE-PHASE",
                target_effective_degree=31,
                module_chirality=1,
                growth_phase=None,
            ),
            "expected": {
                "stage": "admission",
                "code": "module_growth_phase_required",
                "solver_disposition": None,
                "committed": False,
            },
        },
        {
            "fixture_id": "G9-FAIL-NONCANONICAL-INACTIVE-PHASE",
            "base_vector_id": "G9-EXPAND-D30-CHIRALITY-POSITIVE",
            "request_input": invalid_expansion_input(
                "G9-FAIL-NONCANONICAL-INACTIVE-PHASE", growth_phase=1
            ),
            "expected": {
                "stage": "admission",
                "code": "reject_noncanonical_inactive_growth_phase",
                "solver_disposition": None,
                "committed": False,
            },
        },
        {
            "fixture_id": "G9-FAIL-SOURCE-SELF-LOOP",
            "base_vector_id": "G9-EXPAND-D30-CHIRALITY-POSITIVE",
            "source_graph_fixture": self_loop_graph,
            "source_state_fixture": self_loop_state_payload,
            "request_input": invalid_expansion_input(
                "G9-FAIL-SOURCE-SELF-LOOP",
                source_graph_digest=self_loop_graph_id,
                source_state_digest=self_loop_state_id,
            ),
            "pre_lifecycle_digest": self_loop_lifecycle_id,
            "expected": {
                "stage": "admission",
                "code": "source_self_loop_unsupported",
                "solver_disposition": None,
                "committed": False,
            },
        },
        {
            "fixture_id": "G9-FAIL-TARGET-READMISSION",
            "base_vector_id": "G9-EXPAND-D30-CHIRALITY-POSITIVE",
            "request_input": invalid_expansion_input("G9-FAIL-TARGET-READMISSION"),
            "harness_fault": {
                "schema_version": "grcv4-conformance-harness-fault-v1",
                "stage": "target_readmission",
                "kind": "remove_target_W_C_tr_entry",
            },
            "expected": {
                "stage": "target_readmission",
                "code": "target_readmission_failure",
                "solver_disposition": None,
                "committed": False,
            },
        },
    ]
    for row in failure_vectors:
        row_source_state_id = row["request_input"].get(
            "source_state_digest", source_state_id
        )
        failure_payload = {
            "schema_version": "grcv4-failure-receipt-v1",
            "operation_id": f"operation:{row['fixture_id']}",
            "stage": row["expected"]["stage"],
            "code": row["expected"]["code"],
            "source_state_digest": row_source_state_id,
            "observed_poststate_digest": row_source_state_id,
        }
        failure_receipt_id = identity("grc-receipt-sha256", failure_payload)
        row["expected"].update(
            {
                "operation_disposition": "rejected",
                "prestate_digest": row_source_state_id,
                "poststate_digest": row_source_state_id,
                "pre_lifecycle_digest": row.get(
                    "pre_lifecycle_digest", source_lifecycle_id
                ),
                "post_lifecycle_digest": row.get(
                    "pre_lifecycle_digest", source_lifecycle_id
                ),
                "persistent_receipt_append_count": 0,
                "failure_receipt": {
                    "schema_version": "grcv4-failure-receipt-envelope-v1",
                    "receipt_id": failure_receipt_id,
                    "identity_payload": failure_payload,
                },
            }
        )

    failure_by_id = {row["fixture_id"]: row for row in failure_vectors}

    def rejected_step_result(fixture_id: str) -> dict[str, Any]:
        expected = failure_by_id[fixture_id]["expected"]
        failure_receipt = expected["failure_receipt"]
        return {
            "schema_version": "grcv4-step-result-v1",
            "step_index": 1,
            "time": 1,
            "events": [],
            "observables": {},
            "active_profile_id": source_profile_id,
            "active_model_identity": source_model_id,
            "operation_disposition": "rejected",
            "solver_disposition": expected["solver_disposition"],
            "committed": False,
            "commit_id": None,
            "failure": {
                "stage": expected["stage"],
                "solver_disposition": expected["solver_disposition"],
                "code": expected["code"],
                "message": f"normative rejection for {fixture_id}",
                "prestate_digest": source_state_id,
                "poststate_digest": source_state_id,
                "pre_lifecycle_digest": source_lifecycle_id,
                "post_lifecycle_digest": source_lifecycle_id,
                "failure_receipt": failure_receipt,
            },
            "emitted_receipts": [failure_receipt],
        }

    step_result_vectors = [
        {
            "fixture_id": "STEP-RESULT-PRESOLVER-REJECTION",
            "source_failure_fixture_id": "COMMON-NEGATIVE-DURATION",
            "result": rejected_step_result("COMMON-NEGATIVE-DURATION"),
            "assertion": "solver_disposition_is_null_before_solver",
        },
        {
            "fixture_id": "STEP-RESULT-POSTSOLVER-CHARGE-REJECTION",
            "source_failure_fixture_id": "COMMON-CHARGE-MISMATCH",
            "result": rejected_step_result("COMMON-CHARGE-MISMATCH"),
            "assertion": "valid_root_solver_with_rejected_operation",
        },
    ]

    migration_matrix = [
        {
            "class": "same_candidate_nonhistory_to_nonhistory",
            "candidate": {
                "allowed_dispositions": ["exact_transport", "rederived"],
                "information_loss": "none",
            },
            "carrier": {
                "disposition": "not_applicable",
                "information_loss": "none",
            },
        },
        {
            "class": "same_candidate_nonhistory_to_history",
            "candidate": {
                "allowed_dispositions": ["exact_transport", "rederived"],
                "information_loss": "none",
            },
            "carrier": {
                "disposition": "target_initializer",
                "information_loss": "none",
            },
        },
        {
            "class": "same_candidate_history_to_nonhistory",
            "candidate": {
                "allowed_dispositions": ["exact_transport", "rederived"],
                "information_loss": "none",
            },
            "carrier": {
                "disposition": "explicit_loss",
                "information_loss": "carrier_history_loss",
            },
        },
        {
            "class": "PC_to_CI_PC",
            "candidate": {
                "allowed_dispositions": ["exact_transport", "rederived"],
                "information_loss": "none",
            },
            "carrier": {
                "disposition": "exact_transport",
                "information_loss": "none",
            },
        },
        {
            "class": "CI_PC_to_PC",
            "candidate": {
                "allowed_dispositions": ["exact_transport", "rederived"],
                "information_loss": "none",
            },
            "carrier": {
                "disposition": "exact_transport",
                "information_loss": "none",
            },
        },
        {
            "class": "A_to_C",
            "candidate": {
                "disposition": "explicit_loss",
                "information_loss": "candidate_history_loss",
            },
            "carrier": {
                "allowed_dispositions": [
                    "not_applicable",
                    "explicit_loss",
                    "target_initializer",
                ],
                "information_loss": "profile_dependent",
            },
        },
        {
            "class": "C_to_A",
            "candidate": {
                "disposition": "target_initializer",
                "information_loss": "none",
            },
            "carrier": {
                "allowed_dispositions": [
                    "not_applicable",
                    "exact_transport",
                    "target_initializer",
                ],
                "information_loss": "profile_dependent",
            },
        },
    ]

    schema_negative_vectors = [
        {
            "vector_id": "SCHEMA-REJECT-PROFILE-FIELD-MISMATCH",
            "schema_ref": "profile_identity_payload",
            "invariant": "profile_fields_agree",
            "input": {**source_profile_payload, "candidate": "A"},
            "expected": {
                "schema_valid": False,
                "rejection_layer": "json_schema",
                "semantic_validator_invoked": False,
            },
        },
        {
            "vector_id": "SCHEMA-REJECT-HISTORY-SUBJECT-MISMATCH",
            "schema_ref": "history_bundle_policy",
            "invariant": "history_channel_subjects_agree",
            "input": {
                "schema_version": "grcv4-history-bundle-policy-v1",
                "candidate": {**candidate_history_policy, "subject": "carrier"},
                "carrier": {**carrier_history_policy, "subject": "candidate"},
            },
            "expected": {
                "schema_valid": False,
                "rejection_layer": "json_schema",
                "semantic_validator_invoked": False,
            },
        },
    ]

    semantic_admission_vectors = [
        {
            "vector_id": "SEMANTIC-REJECT-RESOURCE-DISTRIBUTION-SUM",
            "validator_id": "grcv4-contract-semantic-admission-v1",
            "invariant": "resource_distribution_unit_sum",
            "input": {
                **base_request,
                "resource_distribution": [0.5, 0.5, 0.5],
            },
            "expected": {
                "admitted": False,
                "code": "resource_distribution_not_unit_sum",
            },
        },
        {
            "vector_id": "SEMANTIC-REJECT-RESOURCE-TRANSFORM-DIMENSIONS",
            "validator_id": "grcv4-contract-semantic-admission-v1",
            "invariant": "resource_transform_dimensions",
            "input": {
                **generic_transform,
                "target_increment": [0, 0],
            },
            "expected": {
                "admitted": False,
                "code": "resource_transform_dimension_mismatch",
            },
        },
        {
            "vector_id": "SEMANTIC-REJECT-GROWTH-PHASE-REMAINDER",
            "validator_id": "grcv4-contract-semantic-admission-v1",
            "invariant": "growth_phase_matches_remainder",
            "input": {
                **base_request,
                "target_effective_degree": 31,
                "growth_phase": None,
            },
            "expected": {
                "admitted": False,
                "code": "module_growth_phase_required",
            },
        },
        {
            "vector_id": "SEMANTIC-REJECT-WCTR-EDGE-SET-MISMATCH",
            "validator_id": "grcv4-contract-semantic-admission-v1",
            "invariant": "target_W_C_tr_matches_live_edges",
            "input": {
                "target_graph": first_expansion_payloads["target_graph"],
                "target_W_C_tr": {
                    key: value
                    for index, (key, value) in enumerate(
                        expansion_vectors[0]["expected"]["target_W_C_tr"].items()
                    )
                    if index
                },
            },
            "expected": {
                "admitted": False,
                "code": "target_W_C_tr_edge_set_mismatch",
            },
        },
        {
            "vector_id": "SEMANTIC-REJECT-PROFILE-PARAMS-HASH-MISMATCH",
            "validator_id": "grcv4-contract-semantic-admission-v1",
            "invariant": "identity_payload_matches_resolved_parameters",
            "input": {
                "resolved_params": source_params,
                "profile_identity": {
                    **source_profile_payload,
                    "params_hash": generic_target_params_id,
                },
            },
            "expected": {
                "admitted": False,
                "code": "resolved_parameters_identity_mismatch",
            },
        },
    ]

    covariance_normalization_policy_id = (
        "grc9v4-event-namespace-and-role-covariance-normalization-v1"
    )
    metamorphic_normalization_policies = {
        covariance_normalization_policy_id: {
            "schema_version": "grc9v4-metamorphic-normalization-policy-v1",
            "policy_id": covariance_normalization_policy_id,
            "event_id_namespaces": (
                "replace the base expected event-ID namespace with the target "
                "expected event-ID namespace"
            ),
            "branch_indexed_node_role_ids": (
                "transport satellite/<b> and extra/<b>/<ordinal> with the "
                "declared branch permutation; core remains core"
            ),
            "branch_indexed_edge_role_ids": (
                "transport internal/<b> and internal/extra/<b>/<ordinal> with "
                "the declared branch permutation"
            ),
            "old_boundary_edge_ids": ("transport old-<p> to old-<port_permutation[p]>"),
            "external_node_labels": (
                "transport outside-<p> to outside-<port_permutation[p]>"
            ),
            "endpoint_ports": "transport every endpoint port p by port_permutation[p]",
            "module_chirality": (
                "cyclic_chart_rotation preserves input chirality; "
                "reflection_chirality_conjugacy negates it"
            ),
            "growth_phase": (
                "transport an active input phase by branch_permutation; "
                "an inactive null phase remains null"
            ),
            "comparison": (
                "sort transported live node IDs and transported edges by edge_id, "
                "then require exact equality with the referenced target plan"
            ),
        }
    }
    metamorphic_vectors = [
        {
            "vector_id": "G9-METAMORPHIC-SOURCE-EDGE-ORDER-PERMUTATION",
            "kind": "source_edge_input_order_permutation",
            "base_vector_id": "G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-1",
            "input": {
                "source_graph": source_graph(),
                "permuted_source_graph": {
                    **source_graph(),
                    "edges": list(reversed(source_graph()["edges"])),
                },
            },
            "expected": {
                "normalized_port_plan_equal": True,
                "event_identity_recomputed_from_permuted_source_digest": True,
            },
        },
        {
            "vector_id": "G9-METAMORPHIC-CYCLIC-CHART-ROTATION",
            "kind": "cyclic_chart_rotation",
            "base_vector_id": "G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-1",
            "expected_target_vector_id": ("G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-2"),
            "normalization_policy_id": covariance_normalization_policy_id,
            "input": {
                "module_chirality": 1,
                "growth_phase": 1,
                "port_permutation": {
                    "1": 5,
                    "2": 6,
                    "3": 4,
                    "4": 8,
                    "5": 9,
                    "6": 7,
                    "7": 2,
                    "8": 3,
                    "9": 1,
                },
                "branch_permutation": {"1": 2, "2": 3, "3": 1},
            },
            "expected": {
                "module_chirality": 1,
                "growth_phase": 2,
                "normalized_port_plan_equal": True,
            },
        },
        {
            "vector_id": "G9-METAMORPHIC-REFLECTION-CHIRALITY-CONJUGACY",
            "kind": "reflection_chirality_conjugacy",
            "base_vector_id": "G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-1",
            "expected_target_vector_id": ("G9-EXPAND-D52-CHIRALITY-NEGATIVE-PHASE-3"),
            "normalization_policy_id": covariance_normalization_policy_id,
            "input": {
                "module_chirality": 1,
                "growth_phase": 1,
                "port_permutation": {
                    "1": 9,
                    "2": 8,
                    "3": 7,
                    "4": 6,
                    "5": 5,
                    "6": 4,
                    "7": 3,
                    "8": 2,
                    "9": 1,
                },
                "branch_permutation": {"1": 3, "2": 2, "3": 1},
            },
            "expected": {
                "module_chirality": -1,
                "growth_phase": 3,
                "normalized_port_plan_equal": True,
            },
        },
    ]
    expansion_by_id = {
        row["fixture_id"]: row
        for row in expansion_vectors
        if row["fixture_id"].startswith("G9-EXPAND-D52-")
    }
    for row in metamorphic_vectors:
        if row["kind"] == "source_edge_input_order_permutation":
            continue
        base = expansion_by_id[row["base_vector_id"]]
        target = expansion_by_id[row["expected_target_vector_id"]]
        transported = transport_covariant_plan(
            base,
            target,
            row["input"]["port_permutation"],
            row["input"]["branch_permutation"],
        )
        target_plan = {
            "live_node_ids": target["expected"]["target_live_node_ids"],
            "edges": target["expected"]["target_edges"],
        }
        if transported != target_plan:
            raise RuntimeError(
                f"{row['vector_id']}: transported D52 plan does not equal target"
            )
        if (
            target["event_identity_payload"]["module_chirality"]
            != row["expected"]["module_chirality"]
            or target["event_identity_payload"]["growth_phase"]
            != row["expected"]["growth_phase"]
        ):
            raise RuntimeError(
                f"{row['vector_id']}: target chirality or growth phase drift"
            )

    return {
        "schema": "grcv4_conformance_vectors_v2",
        "status": "normative_preimplementation_identity_algebra_and_allocator_vectors",
        "implementation_evidence": False,
        "canonicalization": {
            "standard": "RFC8785_JCS",
            "input_profile": "I_JSON",
            "unicode_normalization": "none",
            "negative_zero": "rejected_before_canonicalization",
            "duplicate_keys": "rejected_before_canonicalization",
        },
        "bindings": {
            "builder_path": str(Path(__file__).resolve().relative_to(ROOT)),
            "builder_sha256": file_sha256(Path(__file__).resolve()),
            "contract_schema_path": str(SCHEMA.relative_to(ROOT)),
            "contract_schema_sha256": file_sha256(SCHEMA),
            "fixture_catalog_path": str(CATALOG.relative_to(ROOT)),
            "fixture_catalog_sha256": file_sha256(CATALOG),
        },
        "canonicalization_vectors": [
            identity_vector(
                "JCS-ASCII-ORDER-AND-FINITE-NUMBERS",
                "RFC8785",
                "jcs-example-sha256",
                {"z": [0, 0.5, 1, -1], "a": "é", "m": {"b": True, "a": None}},
            ),
            identity_vector(
                "JCS-UTF16-PROPERTY-ORDER",
                "RFC8785",
                "jcs-example-sha256",
                {"\ue000": 1, "😀": 2},
            ),
            identity_vector(
                "JCS-ECMASCRIPT-SMALL-NUMBER-THRESHOLD",
                "RFC8785",
                "jcs-example-sha256",
                {"numbers": [1e-7, 1e-6]},
            ),
        ],
        "identity_vectors": identity_vectors,
        "port_graph_envelope_vectors": port_graph_envelope_vectors,
        "subdigest_identity_vectors": subdigest_vectors,
        "candidate_c_algebra_vectors": [c_witness],
        "grc9_expansion_vectors": expansion_vectors,
        "grcv4_mapped_topology_event_vectors": mapped_event_vectors,
        "atomic_failure_vectors": failure_vectors,
        "step_result_vectors": step_result_vectors,
        "migration_policy_matrix": migration_matrix,
        "semantic_admission": {
            "validator_id": "grcv4-contract-semantic-admission-v1",
            "json_schema_validity_is_necessary_not_sufficient": True,
            "schema_negative_vectors": schema_negative_vectors,
            "negative_vectors": semantic_admission_vectors,
        },
        "grc9_metamorphic_normalization_policies": metamorphic_normalization_policies,
        "grc9_metamorphic_vectors": metamorphic_vectors,
        "coverage_holds": {
            "candidate_a_numeric_vectors": "required_before_candidate_A_runtime_conformance",
            "candidate_a_GRC9V4_expansion_vectors": "A_template_identity_is_frozen_but_A_expansion_is_not_advertised_before_a_concrete_target_vector",
            "per_realization_step_vectors": "required_for_each_advertised_complete_profile",
            "RG2b_vectors": "required_before_A_RG2b_or_C_RG2b_capability",
            "child_stabilization_vectors": "required_before_completed_spark_or_hierarchy_tracking_capability",
            "disabled_GRC9V3_delegate_vectors": "40_exact_vectors_required_before_disabled_compatibility_capability",
            "lifecycle_snapshot_reset_migration_vectors": "required_before_snapshot_reset_or_migration_runtime_conformance",
            "generic_mapped_topology_vectors": "one_preimplementation_affine_identity_vector_present_runtime_execution_still_required",
            "deep_recursive_expansion_and_covariance_runtime": "D52_and_metamorphic_preimplementation_vectors_present_runtime_execution_required_before_arbitrary_size_mechanical_refinement_conformance",
            "charge_precision_edge_vectors": "required_before_cross_implementation_charge_conformance",
            "deep_immutability_runtime_tests": "required_before_snapshot_or_duplication_conformance",
            "runtime_execution_receipts": "absent_preimplementation",
        },
    }


def main() -> int:
    payload = build()
    OUTPUT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        "GRCV4_SPECIFICATION_VECTORS_BUILT "
        f"identity={len(payload['identity_vectors'])} "
        f"expansion={len(payload['grc9_expansion_vectors'])} "
        f"failures={len(payload['atomic_failure_vectors'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
