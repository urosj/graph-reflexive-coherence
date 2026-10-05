"""Reproduce the P9-8.3 larger-graph proposal, without numerical admission.

This checkout verification tool builds ordinary production wire declarations
and a detached mechanical plan. It never creates an operation or solves a
current/root/section. Its own record digest is evidence identity, not authority.
Fraction is independent preparation/proof arithmetic, not a runtime backend.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4ExpansionPlan,
    GRC9V4ExpansionRequestInput,
)
from pygrc.models.grc_9_v4_lifecycle import GRC9V4Specialization
from pygrc.models.grc_9_v4_topology import (
    GRC9V4PortEdge,
    GRC9V4PortEndpoint,
    GRC9V4PortGraph,
)
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_profile import (
    resolve_profile,
    resolve_profile_template,
    validate_profile_references,
)
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState

ROOT = Path(__file__).resolve().parents[3]
BASE = "implementation/phase-9-grcv4/tranche-8/"
REQUEST = BASE + "P9-8.3-LargerGraphRequest.json"
RECORD = BASE + "P9-8.3-LargerGraphPreparation.json"
VECTORS = "specs/grc-v4-conformance-vectors.json"
FAMILIES = (
    "C_OS",
    "C_PC",
    "A_OS",
    "C_CI",
    "A_CI",
    "A_PC",
    "C_CI_PC",
    "A_CI_PC",
    "C_RG2b",
    "A_RG2b",
)
SOURCES = (
    VECTORS,
    "specs/grc-9-v4-spec.md",
    "specs/grc-v4-spec.md",
    REQUEST,
    "src/pygrc/models/grc_9_v4_topology.py",
    "src/pygrc/models/grc_9_v4_expansion.py",
    "src/pygrc/models/grc_9_v4_lifecycle.py",
    "src/pygrc/models/grc_9_v4_rg2b.py",
    "src/pygrc/models/grc_9_v4_arg2b.py",
    "src/pygrc/models/grc_v4_profile.py",
    "src/pygrc/models/grc_v4_ci.py",
    "src/pygrc/models/grc_v4_pc.py",
    "implementation/phase-9-grcv4/verification/prepare_p983_graph_admission.py",
    "implementation/phase-9-grcv4/verification/test_p983_graph_admission.py",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ratio(value):
    value = Q(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def record_digest(record):
    return sha256(
        canonical_json_bytes({k: v for k, v in record.items() if k != "record_digest"})
    ).hexdigest()


def source_graph():
    """400 simple edges; one saturated node, one degree seven, 98 degree eight."""
    edges = []
    for node in range(100):
        for offset in range(1, 5):
            tail, port = (0, 9) if (node, offset) == (50, 4) else (node, offset)
            edges.append(
                GRC9V4PortEdge(
                    f"ring/{node:03d}/{offset}",
                    "boundary",
                    GRC9V4PortEndpoint(tail, port),
                    GRC9V4PortEndpoint((node + offset) % 100, offset + 4),
                )
            )
    return GRC9V4PortGraph(tuple(range(100)), tuple(edges))


def graph_facts(graph):
    """Independent endpoint counts, BFS, and exact sparse Gram/mask row sums.

    This proof recipe is intentionally restricted to simple loop-free graphs;
    multigraph/loop production admission has broader semantics.
    """
    nodes = graph.live_node_ids
    adjacency = {node: set() for node in nodes}
    pairs = set()
    for edge in graph.edges:
        u, v = edge.tail.node_id, edge.head.node_id
        pair = frozenset((u, v))
        require(u != v and pair not in pairs, "simple loop-free proof recipe required")
        pairs.add(pair)
        adjacency[u].add(v)
        adjacency[v].add(u)
    unseen, components = set(nodes), 0
    while unseen:
        components += 1
        pending = [unseen.pop()]
        while pending:
            for node in adjacency[pending.pop()] & unseen:
                unseen.remove(node)
                pending.append(node)
    degrees = {node: len(neighbors) for node, neighbors in adjacency.items()}
    gram = max(
        (degrees[e.tail.node_id] + degrees[e.head.node_id] for e in graph.edges),
        default=0,
    )
    n, m = len(nodes), len(graph.edges)
    return {
        "vertices": n,
        "edges": m,
        "components": components,
        "cycle_rank": m - n + components,
        "degree_histogram": {
            str(k): v for k, v in sorted(Counter(degrees.values()).items())
        },
        "saturated_nodes": [node for node in nodes if degrees[node] == 9],
        "unused_ports": 9 * n - 2 * m,
        "incidence_infinity_norm": max(degrees.values(), default=0),
        "edge_gram_infinity_norm": gram,
        "star_mask_infinity_norm": ratio(Q(gram, 2)),
        "dense_edge_matrix_entries": m * m,
        "one_binary64_edge_matrix_bytes_excluding_overhead": 8 * m * m,
    }


def validate_request(request):
    # Closed worked-example recipe, not an arbitrary runtime configuration API.
    fixed = {
        "schema": "p983-graph-preparation-request-v1",
        "purpose": "Reproducible new-configuration preparation; not a runtime admission token",
        "graph_recipe": "circulant_100_offsets_1_to_4_move_50_54_tail_to_0_port9_v1",
        "worked_family": "C_OS",
        "state_recipe": "C2_remote_dyadic_pulses_distinct_equal_charge_roles_v1",
        "parameter_selection_policy": "explicit_new_declaration_no_automatic_retuning",
        "history_policy": "C_rederive_no_W_no_Z",
    }
    configurable = {
        "candidate_overrides",
        "kappa_H",
        "os_split_tolerance",
        "conditioning_limit",
        "absolute_tolerance",
        "relative_tolerance",
        "charge_absolute_tolerance",
        "ordinary_dt",
        "event",
        "planned_target_steps_per_role",
        "required_families",
    }
    require(
        set(request) == set(fixed) | configurable,
        "unknown or missing preparation field",
    )
    for field, value in fixed.items():
        require(request[field] == value, f"unsupported preparation {field}")
    require(tuple(request["required_families"]) == FAMILIES, "ten-family scope changed")
    require(
        set(request["candidate_overrides"])
        == {
            "Lambda_C",
            "C_ref",
            "kappa_M_C",
            "kappa_Phi_C",
            "eta_C",
            "tau_C",
            "chi_C",
            "zeta_C",
        },
        "candidate override fields changed",
    )
    require(
        set(request["event"])
        == {
            "source_node_id",
            "target_effective_degree",
            "module_chirality",
            "growth_phase",
            "resource_distribution",
        },
        "event fields changed",
    )
    require(
        request["event"]["source_node_id"] == 0
        and request["event"]["target_effective_degree"] == 52,
        "worked proposal requires node zero and D52",
    )
    for field in (
        "ordinary_dt",
        "os_split_tolerance",
        "conditioning_limit",
        "absolute_tolerance",
        "relative_tolerance",
        "charge_absolute_tolerance",
    ):
        require(
            type(request[field]) in (int, float) and request[field] > 0,
            f"positive numeric {field} required",
        )
    require(
        type(request["planned_target_steps_per_role"]) is int
        and request["planned_target_steps_per_role"] > 0,
        "positive step count required",
    )


def profile_for(graph, request, vectors):
    rows = {r["vector_id"]: r["payload"] for r in vectors["identity_vectors"]}
    params = deepcopy(rows["IDENTITY-GRCV4-PARAMS-C-OS"])
    identity = deepcopy(rows["IDENTITY-GRCV4-PROFILE-C-OS"])
    weights = {e.edge_id: 1 for e in graph.edges}
    k4 = {
        "schema_version": "grcv4-k4-identity-v1",
        "K4_base": [[0] * len(graph.edges) for _ in graph.edges],
    }
    hodge = {
        "schema_version": "grcv4-reference-hodge-identity-v1",
        "edge_weights": weights,
    }
    params["candidate"].update(request["candidate_overrides"])
    params["candidate"].update(
        W_C_tr=weights,
        W_C_tr_content_digest=payload_identity(
            "wctr_identity_payload",
            {
                "schema_version": "grcv4-wctr-identity-v1",
                "W_C_tr": weights,
            },
        ),
    )
    params["geometry"].update(
        K4_base_digest=payload_identity("k4_identity_payload", k4),
        reference_hodge_digest=payload_identity(
            "reference_hodge_identity_payload", hodge
        ),
        kappa_H=request["kappa_H"],
    )
    params["realization"]["tolerance"] = request["os_split_tolerance"]
    for key in ("conditioning_limit", "absolute_tolerance", "relative_tolerance"):
        params["solver"][key] = request[key]
    params["charge"]["absolute_tolerance"] = request["charge_absolute_tolerance"]
    identity["params_hash"] = payload_identity("resolved_params", params)
    profile = resolve_profile(params, identity)
    validate_profile_references(
        profile,
        live_edge_ids=tuple(weights),
        k4_preimage=k4,
        reference_hodge_preimage=hodge,
    )
    return profile


def state_payload(graph, profile, specialization, current, reset):
    # Wire preimages are preparation only; no accepted native owner is implied.
    for role in (current, reset):
        GRCV4AuthoritativeState(tuple(role["C"]), None, None)
        require(len(role["C"]) == len(graph.live_node_ids), "state size mismatch")
        require(sum(map(Q, role["C"])) == 200, "proposal roles must share exact Q=200")
    model = payload_identity(
        "complete_model_identity_payload",
        {
            "schema_version": "grc9v4-complete-identity-v1",
            "grcv4_complete_profile_id": profile.complete_profile_id,
            "specialization_id": specialization.specialization_id,
        },
    )
    common = {
        "active_model_identity": model,
        "graph_digest": graph.graph_digest,
        "orientation_identity": graph.orientation_identity,
        "Q_target": 200,
        "context_contract_id": "constant_zero_context_v1",
    }
    baseline = {
        **common,
        "schema_version": "grc9v4-reset-baseline-v1",
        "authoritative": reset,
    }
    reset_id = payload_identity("grc9v4_reset_payload", baseline)
    scientific = {
        **common,
        "schema_version": "grcv4-scientific-state-v1",
        "authoritative": current,
        "reset_digest": reset_id,
        "step_index": 0,
        "time": 0,
        "context_value_digest": None,
    }
    return {
        "model_identity": model,
        "reset_payload": baseline,
        "reset_digest": reset_id,
        "scientific_payload": scientific,
        "scientific_digest": payload_identity("scientific_state_payload", scientific),
    }


def family_obligations():
    result = []
    for family in FAMILIES:
        needs = ["LG-VALIDATION", "LG-FACADE", "P9-8.4", "P9-8.5", "P9-8.6"]
        if family.startswith("A_"):
            needs += ["LG-A-ORACLE"]
        if family.endswith("PC"):
            needs += ["LG-PC-CHART"]
        if "CI" in family:
            needs += ["LG-CI-ROOT"]
        if family.endswith("RG2b"):
            needs += ["LG-RG-COMPLETION"]
        if family.startswith("C_"):
            needs += ["LG-C-SELECTOR"]
        if family.endswith("OS"):
            needs += ["LG-OS-SPLIT"]
        result.append(
            {
                "family": family,
                "declaration_record": BASE
                + "larger-graph-examples/"
                + family
                + ".json",
                "numerical_admission_record": BASE
                + "larger-graph-examples/"
                + family
                + "-Admission.json",
                "runtime_acceptance": "not_requested_by_this_record",
                "obligation_ids": needs,
            }
        )
    return result


def prepare(request=None):
    if request is None:
        request = json.loads((ROOT / REQUEST).read_text())
    validate_request(request)
    vectors = json.loads((ROOT / VECTORS).read_text())
    rows = {r["vector_id"]: r["payload"] for r in vectors["identity_vectors"]}
    graph = source_graph()
    profile = profile_for(graph, request, vectors)
    params = deepcopy(rows["IDENTITY-GRC9V4-PARAMS"])
    params["expansion"]["bond_seed"] = 1
    ident = deepcopy(rows["IDENTITY-GRC9V4-SPECIALIZATION"])
    ident.update(
        hessian_sign=-1,
        specialization_params_hash=payload_identity("resolved_specialization", params),
    )
    spec = GRC9V4Specialization(FrozenJSONMap(params), FrozenJSONMap(ident))
    roles = {}
    for role, plus, minus, delta in (
        ("current", 20, 70, 1 / 64),
        ("reset", 30, 80, 1 / 32),
    ):
        c = [2] * 100
        c[plus] += delta
        c[minus] -= delta
        roles[role] = {"C": c, "W_A": None, "Z_4": None}
    source_state = state_payload(graph, profile, spec, **roles)
    template = resolve_profile_template(
        {
            "schema_version": "grcv4-profile-template-v1",
            "source_complete_profile_id": profile.complete_profile_id,
            "profile_family_id": "C_OS",
            "topology_dependent_map_policy_id": "preserve_old_stable_edges_seed_new_internal_edges_v1",
            "geometry_reference_policy_id": "rebuild_reference_hodge_from_target_W_C_tr_v1",
        },
        source=profile,
    )
    event = deepcopy(vectors["grc9_expansion_vectors"][0]["request"])
    event.update(request["event"])
    event.update(
        schema_version="grc9v4-expansion-event-request-input-v1",
        operation_id="p983-larger-graph-proposal",
        source_state_digest=source_state["scientific_digest"],
        source_graph_digest=graph.graph_digest,
        target_profile_template_id=template.profile_template_id,
        target_specialization_id=spec.specialization_id,
        expected_event_id=None,
        expected_target_graph_digest=None,
    )
    plan = GRC9V4ExpansionPlan(
        graph,
        source_state["scientific_digest"],
        GRC9V4ExpansionRequestInput.from_payload(event),
        GRC9ExpansionPolicy.from_payload(params["expansion"]),
    )
    target_profile = profile_for(plan.target_graph, request, vectors)
    targets = {}
    source_index = graph.live_node_ids.index(request["event"]["source_node_id"])
    shares = {
        plan.event_id + f"/satellite/{i + 1}": share
        for i, share in enumerate(request["event"]["resource_distribution"])
    }
    for role, authority in roles.items():
        old = dict(zip(graph.live_node_ids, authority["C"], strict=True))
        values = [
            old[node]
            if node in old
            else float(Q(shares.get(node, 0)) * Q(authority["C"][source_index]))
            for node in plan.target_graph.live_node_ids
        ]
        targets[role] = {"C": values, "W_A": None, "Z_4": None}
    target_state = state_payload(plan.target_graph, target_profile, spec, **targets)
    facts = {"source": graph_facts(graph), "target": graph_facts(plan.target_graph)}
    cutoff = Q(request["candidate_overrides"]["Lambda_C"])
    selector = {}
    for name, g in (("source", graph), ("target", plan.target_graph)):
        n = len(g.live_node_ids)
        require(facts[name]["components"] == 1, "connected selector proof required")
        lower = Q(1, n * (n - 1))
        require(
            0 < cutoff < lower,
            "proposed reference constant-sector cutoff not certified",
        )
        selector[name] = {
            "nonzero_reference_laplacian_lower": ratio(lower),
            "cutoff": ratio(cutoff),
            "strict_slack": ratio(lower - cutoff),
            "scope": "unit-weight reference Hodge only; deformed read not certified",
        }
    pc = {}
    for name, values in (("source", roles), ("target", targets)):
        pc[name] = {
            role: {
                "resource_l2_squared": ratio(sum(Q(c) ** 2 for c in state["C"])),
                "accepted_M16_fits": sum(Q(c) ** 2 for c in state["C"]) <= 16**2,
                "proposed_M32_fits_resources_only": sum(Q(c) ** 2 for c in state["C"])
                <= 32**2,
            }
            for role, state in values.items()
        }
    result = {
        "schema": "p983-larger-graph-preparation-v1",
        "disposition": "prepared_declarations_and_mechanics_only",
        "request": request,
        "request_sha256": sha256(canonical_json_bytes(request)).hexdigest(),
        "source_bindings": [
            {"path": path, "sha256": sha256((ROOT / path).read_bytes()).hexdigest()}
            for path in SOURCES
        ],
        "source": {
            "port_graph": graph.to_envelope(),
            "profile": profile.to_payload(),
            "roles": roles,
            **source_state,
        },
        "specialization": spec.to_payload(),
        "reference_recipe": {
            "unit_vertex_measures": True,
            "unit_edge_weights": True,
            "K4_base": "exact zero m by m in each graph edge order",
            "context": {"contract_id": "constant_zero_context_v1", "values": {}},
        },
        "event_request": plan.request.to_payload(),
        "mechanical_plan": {
            "event_id": plan.event_id,
            "module_nodes": list(plan.module_node_ids),
            "internal_edges": list(plan.internal_edge_ids),
            "external_capacity": plan.external_capacity,
            "publication": "not_attempted",
        },
        "target": {
            "port_graph": plan.target_graph.to_envelope(),
            "profile": target_profile.to_payload(),
            "roles": targets,
            **target_state,
        },
        "graph_facts": facts,
        "reference_selector_proof": selector,
        "pc_resource_preflight": pc,
        "native_rg2b_scope_preflight": {
            name: {
                "tree17_hypothesis": f["vertices"] <= 17 and f["cycle_rank"] == 0,
                "gram_le_10": f["edge_gram_infinity_norm"] <= 10,
                "star_mask_le_5": f["edge_gram_infinity_norm"] <= 10,
                "status": "outside_current_native_completion",
            }
            for name, f in facts.items()
        },
        "families": family_obligations(),
        "execution": {
            "trigger_evaluation": "not_run",
            "current_or_root_or_section": "not_run",
            "physical_steps": 0,
            "events_committed": 0,
            "receipts": [],
            "performance_measured": False,
            "runtime_admitted": False,
            "supported_profiles_added": [],
        },
    }
    result["record_digest"] = record_digest(result)
    return result


def check_record(record):
    require(
        record.get("record_digest") == record_digest(record),
        "preparation digest mismatch",
    )
    expected = prepare()
    require(
        canonical_json_bytes(record) == canonical_json_bytes(expected),
        "preparation differs from current request/source reconstruction",
    )


def materialize_source(record):
    """Future execution handoff: typed source inputs, still no current solve.

    This allocates dense exact reference geometry. The closeout tests its
    identity reconstruction, without claiming a performance measurement.
    Numerical admission is performed subsequently by native operation/read owners.
    """
    from pygrc.models.grc_9_v4_lifecycle import GRC9V4COSState
    from pygrc.models.grc_v4_geometry import (
        GeometryStageInputs,
        GRCV4Context,
        GRCV4Graph,
        GRCV4ReferenceGeometry,
    )
    from pygrc.models.grc_v4_profile import GRCV4Profile

    check_record(record)
    source = record["source"]
    graph = GRC9V4PortGraph.from_envelope(source["port_graph"])
    profile = GRCV4Profile.from_canonical_bytes(canonical_json_bytes(source["profile"]))
    ref = GRCV4ReferenceGeometry(
        GRCV4Graph.from_port_graph(graph),
        profile,
        GRCV4Context("constant_zero_context_v1", FrozenJSONMap({})),
        tuple((0.0,) * len(graph.edges) for _ in graph.edges),
        FrozenJSONMap({e.edge_id: 1.0 for e in graph.edges}),
    )
    roles = {
        role: GRCV4AuthoritativeState(tuple(v["C"]), None, None)
        for role, v in source["roles"].items()
    }
    spec = record["specialization"]
    result = GRC9V4COSState(
        GeometryStageInputs(
            ref.geometry(),
            ref.context,
            roles["current"],
            roles["reset"],
            "p983-larger-graph-seed",
            200.0,
            (),
            0,
            0.0,
            0.0,
            "pre_read",
            0,
            None,
        ),
        GRC9V4Specialization(
            FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])
        ),
    )
    require(
        result.scientific_digest == source["scientific_digest"],
        "materialized source drift",
    )
    require(result.reset_digest == source["reset_digest"], "materialized reset drift")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="regenerate the repository proposal"
    )
    args = parser.parse_args()
    if args.write:
        (ROOT / RECORD).write_text(json.dumps(prepare(), indent=2) + "\n")
    else:
        check_record(json.loads((ROOT / RECORD).read_text()))
    print(
        "P983_GRAPH_PREPARATION_PASS source=100/400 target=107/407 "
        "numerical_admission=not_run runtime_support=unchanged"
    )


if __name__ == "__main__":
    main()
