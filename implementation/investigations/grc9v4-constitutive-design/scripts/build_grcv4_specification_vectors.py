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


def content_digest(prefix: str, payload: Any) -> str:
    return identity(prefix, {"value": payload})


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
        "W_C_tr_content_digest": content_digest("grcv4-wctr-sha256", weights),
        "potential_evaluator_id": "quadratic_site_potential_zero_derivative_v1",
        "tau_C": 0,
        "chi_C": 1,
        "zeta_C": 0.5,
        "current_conditioning_policy_id": "strict_invertible_current_block_v1",
        "E_H_policy_id": "diag_W_C_tr_structural_hodge_v1",
        "E_M_policy_id": "eta_C_diag_W_C_tr_mobility_v1",
    }


def resolved_params(weights: dict[str, float]) -> dict[str, Any]:
    return {
        "schema_version": "grcv4-resolved-params-v1",
        "common": common_params(),
        "candidate": c_params(weights),
        "realization": {
            "schema_version": "grcv4-os-params-v1",
            "predictor_policy_id": "reference_geometry_predictor_v1",
            "corrector_policy_id": "one_fresh_geometry_corrector_v1",
            "split_residual_norm_id": "edge_l2_v1",
            "tolerance": 0,
        },
        "geometry": {
            "schema_version": "grcv4-geometry-profile-params-v1",
            "K4_base_digest": content_digest("grcv4-k4-sha256", [[1, 0], [0, 1]]),
            "reference_hodge_digest": content_digest(
                "grcv4-hodge-sha256", {"edge_weights": weights}
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


def profile_payload(params_id: str) -> dict[str, Any]:
    return {
        "schema_version": "grcv4-profile-identity-v1",
        "profile_family_id": "C_OS",
        "candidate": "C",
        "realization": "OS",
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


def profile_template(source_profile_id: str) -> dict[str, Any]:
    return {
        "schema_version": "grcv4-profile-template-v1",
        "source_complete_profile_id": source_profile_id,
        "profile_family_id": "C_OS",
        "topology_dependent_map_policy_id": (
            "preserve_old_stable_edges_seed_new_internal_edges_v1"
        ),
        "geometry_reference_policy_id": "rebuild_reference_hodge_from_target_W_C_tr_v1",
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


def build() -> dict[str, Any]:
    source_weights = {f"old-{port}": 1 for port in range(1, 10)}
    source_params = resolved_params(source_weights)
    source_params_id = identity("grcv4-params-sha256", source_params)
    source_profile_payload = profile_payload(source_params_id)
    source_profile_id = identity("grcv4-profile-sha256", source_profile_payload)
    template = profile_template(source_profile_id)
    template_id = identity("grcv4-profile-template-sha256", template)

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

    graph_payload = source_graph()
    source_graph_id = identity("grc-graph-sha256", graph_payload)
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
    source_lifecycle_payload = {
        "schema_version": "grcv4-lifecycle-envelope-v1",
        "scientific_state_digest": source_state_id,
        "receipt_ids": [],
    }
    source_lifecycle_id = identity("grcv4-lifecycle-sha256", source_lifecycle_payload)

    expansion_policy = g9_params["expansion"]
    expansion_policy_id = content_digest(
        "grc9v4-expansion-policy-sha256", expansion_policy
    )
    candidate_history_id = content_digest(
        "grcv4-history-policy-sha256", "candidate_c_rederive_no_history_v1"
    )
    carrier_history_id = content_digest(
        "grcv4-history-policy-sha256", "whole_carrier_reset_with_loss_receipt_v1"
    )
    expansion_history_policy = {
        "schema_version": "grc9v4-expansion-history-policy-v1",
        "candidate_history_policy_id": "candidate_c_rederive_no_history_v1",
        "carrier_history_policy_id": "whole_carrier_reset_with_loss_receipt_v1",
        "candidate_history_policy_digest": candidate_history_id,
        "carrier_history_policy_digest": carrier_history_id,
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
                "source_authoritative_digest": content_digest(
                    "grcv4-authoritative-sha256",
                    source_state_payload["authoritative"],
                ),
                "target_authoritative_digest": content_digest(
                    "grcv4-authoritative-sha256",
                    target_state_payload["authoritative"],
                ),
                "source_reset_digest": source_reset_id,
                "target_reset_digest": target_reset_id,
                "resource_map_digest": content_digest(
                    "grcv4-resource-map-sha256", [0.5, 0.25, 0.25]
                ),
                "history_map_digest": content_digest(
                    "grcv4-history-map-sha256", expansion_history_policy
                ),
                "actual_charge_delta": 0,
                "information_loss": "carrier_history_loss",
                "disposition": "committed",
                "parent_receipt_ids": [],
            },
            "event_id": event_id,
            "history_disposition": "whole_carrier_reset",
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

    failure_vectors = [
        {
            "fixture_id": "G9-FAIL-MISSING-CHIRALITY",
            "request_override": {
                "target_effective_degree": 30,
                "module_chirality": None,
                "growth_phase": None,
            },
            "expected": {
                "stage": "admission",
                "code": "module_chirality_required",
                "committed": False,
            },
        },
        {
            "fixture_id": "G9-FAIL-MISSING-ACTIVE-PHASE",
            "request_override": {
                "target_effective_degree": 31,
                "module_chirality": 1,
                "growth_phase": None,
            },
            "expected": {
                "stage": "admission",
                "code": "module_growth_phase_required",
                "committed": False,
            },
        },
        {
            "fixture_id": "G9-FAIL-NONCANONICAL-INACTIVE-PHASE",
            "request_override": {
                "target_effective_degree": 30,
                "module_chirality": 1,
                "growth_phase": 1,
            },
            "expected": {
                "stage": "admission",
                "code": "reject_noncanonical_inactive_growth_phase",
                "committed": False,
            },
        },
        {
            "fixture_id": "G9-FAIL-SOURCE-SELF-LOOP",
            "request_override": {"source_node_id": "source-with-self-loop"},
            "expected": {
                "stage": "admission",
                "code": "source_self_loop_unsupported",
                "committed": False,
            },
        },
        {
            "fixture_id": "G9-FAIL-TARGET-READMISSION",
            "request_override": {
                "target_reference_map_fault": "missing_one_internal_edge"
            },
            "expected": {
                "stage": "target_readmission",
                "code": "target_readmission_failure",
                "committed": False,
            },
        },
    ]
    for row in failure_vectors:
        failure_payload = {
            "schema_version": "grcv4-failure-receipt-v1",
            "operation_id": f"operation:{row['fixture_id']}",
            "stage": row["expected"]["stage"],
            "code": row["expected"]["code"],
            "source_state_digest": source_state_id,
            "observed_poststate_digest": source_state_id,
        }
        failure_receipt_id = identity("grc-receipt-sha256", failure_payload)
        row["expected"].update(
            {
                "prestate_digest": source_state_id,
                "poststate_digest": source_state_id,
                "pre_lifecycle_digest": source_lifecycle_id,
                "post_lifecycle_digest": source_lifecycle_id,
                "persistent_receipt_append_count": 0,
                "failure_receipt": {
                    "schema_version": "grcv4-failure-receipt-envelope-v1",
                    "receipt_id": failure_receipt_id,
                    "identity_payload": failure_payload,
                },
            }
        )

    migration_matrix = [
        {
            "class": "same_candidate_nonhistory_to_nonhistory",
            "history_disposition": "not_applicable",
        },
        {
            "class": "same_candidate_nonhistory_to_history",
            "history_disposition": "target_initializer",
        },
        {
            "class": "same_candidate_history_to_nonhistory",
            "history_disposition": "explicit_loss",
        },
        {"class": "PC_to_CI_PC", "history_disposition": "exact_transport"},
        {"class": "CI_PC_to_PC", "history_disposition": "exact_transport"},
        {"class": "A_to_C", "history_disposition": "explicit_loss"},
        {"class": "C_to_A", "history_disposition": "target_initializer"},
    ]

    return {
        "schema": "grcv4_conformance_vectors_v1",
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
        "candidate_c_algebra_vectors": [c_witness],
        "grc9_expansion_vectors": expansion_vectors,
        "atomic_failure_vectors": failure_vectors,
        "migration_policy_matrix": migration_matrix,
        "coverage_holds": {
            "candidate_a_numeric_vectors": "required_before_candidate_A_runtime_conformance",
            "per_realization_step_vectors": "required_for_each_advertised_complete_profile",
            "RG2b_vectors": "required_before_A_RG2b_or_C_RG2b_capability",
            "child_stabilization_vectors": "required_before_completed_spark_or_hierarchy_tracking_capability",
            "disabled_GRC9V3_delegate_vectors": "40_exact_vectors_required_before_disabled_compatibility_capability",
            "lifecycle_snapshot_reset_migration_vectors": "required_before_snapshot_reset_or_migration_runtime_conformance",
            "generic_mapped_topology_vectors": "required_before_generic_mapped_topology_runtime_conformance",
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
