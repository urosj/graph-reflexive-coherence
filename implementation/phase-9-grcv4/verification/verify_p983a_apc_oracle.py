"""Independent A_PC A.1 oracle; identity helpers only, no native PC execution.

The native-scoped chart is distinct from P9-8.0's local research ball. Point
expectations use 100 digits; independent interval equations and analytic
whole-chart inequalities certify them. Both W and Z retain their own stage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path

import numpy as np
import phase9_specialization_acceptance as admission
import verify_p983a_aos_oracle as common
from test_p980_os_effect_witness import (
    IV,
    PARAMS,
    IntervalRows,
    endpoint,
    full_error,
    number,
    separation,
    upper_abs,
    vector,
)
from test_p980_os_numerical_feasibility import StagedRows

from pygrc.models.grc_v4_codec import (
    canonical_json_bytes,
    payload_identity,
    validate_payload,
)
from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry
from pygrc.models.grc_v4_profile import resolve_profile

ROOT = Path(__file__).resolve().parents[3]
PHASE = common.PHASE
RECORD = PHASE + "tranche-8/P9-8.3A.1-APC-Oracle.json"
A_G2 = "grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75"
DT = common.DT
RADIUS, KAPPA_H = 2048, 2**-14
RESOURCE_RADIUS, W_MIN, W_MAX = 16, 0.5, 1 + 2**-9
CURRENT_ERROR = RESOURCE_ERROR = CARRIER_ERROR = Q(1, 2**40)
HISTORY_ERROR = GEOMETRY_ERROR = Q(1, 2**48)
SOURCE_ERROR = Q(1, 2**56)
SOURCES = (
    *common.SOURCES,
    PHASE + "tranche-7/P9-7.7-A_PC-G2Acceptance.json",
    PHASE + "tranche-8/P9-8.0-CarrierEventInputs.json",
    PHASE + "tranche-8/P9-8.0-CarrierEventConstruction.md",
    PHASE + "tranche-8/P9-8.0-CarrierEventIndependentReview.md",
    PHASE + "verification/test_p980_carrier_event_companion.py",
    PHASE + "verification/test_p980_revised_realization_bounds.py",
    PHASE + "verification/verify_p983a_aos_oracle.py",
)
require, digest = common.require, common.digest
graph_payload, descriptor = common.graph_payload, common.descriptor
native_identity, candidate_content = common.native_identity, common.candidate_content
adjacent_charge = common.adjacent_charge


def authority(c, w, z):
    return {"C": list(c), "W_A": list(w), "Z_4": np.asarray(z).reshape(-1).tolist()}


def seed(graph, role):
    ends = [{e[k]["node_id"] for k in ("tail", "head")} for e in graph["edges"]]
    sign = {"current": 1, "reset": -1}[role]
    return [
        [
            sign
            * RADIUS
            / 16
            * (1 if i == j else 0.5 if a & b else 0)
            * (-1) ** (i + j)
            for j, b in enumerate(ends)
        ]
        for i, a in enumerate(ends)
    ]


class PaperAPC(common.PaperAOS):
    """Old Z read, one selected J, independent W and same-source Z writers."""

    def step(self, c, w, z):
        c, w = tuple(c), tuple(w)
        z = self.mp.matrix(np.asarray(z).reshape(len(w), len(w)).tolist())
        h = self.I + self.mp.mpf(KAPPA_H) * z
        read = self.read(c, w, h)
        cn = self.mp.matrix(c) - self.mp.mpf(DT) * self.B * read["current"]
        wn = self.write(cn, w, read["current"])
        decay = self.mp.exp(-self.mp.mpf(DT))
        zn = decay * z + (1 - decay) * read["source"]
        return {
            "C": list(map(float, cn)),
            "W_A": list(map(float, wn)),
            "Z_4": [float(x) for row in zn.tolist() for x in row],
            "current": list(map(float, read["current"])),
            "baseline": list(map(float, read["baseline"])),
            "H": [[float(x) for x in row] for row in h.tolist()],
            "source": [[float(x) for x in row] for row in read["source"].tolist()],
        }


def reference(graph):
    ref = common.reference(graph)
    params, identity = (
        ref.profile.params_resolved.to_payload(),
        ref.profile.identity_payload.to_payload(),
    )
    params["geometry"]["kappa_H"] = KAPPA_H
    params["realization"] = {
        "schema_version": "grcv4-pc-params-v1",
        "tau_PC": 1,
        "radius": RADIUS,
        "carrier_norm_id": "symmetric_star_frobenius_v1",
        "source_envelope_id": "pc_compact_base_chart_v1:"
        + ":".join(float(x).hex() for x in (RESOURCE_RADIUS, W_MIN, W_MAX)),
        "writer_id": "zero_order_hold_exponential_v1",
    }
    identity.update(
        profile_family_id="A_PC",
        realization="PC",
        solver_id="direct_unique_root_v1",
        params_hash=payload_identity("resolved_params", params),
    )
    return GRCV4ReferenceGeometry(
        ref.graph,
        resolve_profile(params, identity),
        ref.context,
        ref.K4_base,
        ref.edge_weights,
    )


def carrier_content(current, reset):
    return {
        "schema_version": "grcv4-history-content-identity-v1",
        "subject": "carrier",
        "content": current["Z_4"] + reset["Z_4"],
    }


def history_policy(current, reset):
    policy = common.history_policy(current, reset)
    policy["carrier"] = {
        "schema_version": "grcv4-history-channel-policy-v1",
        "subject": "carrier",
        "policy_id": "whole_carrier_reset_with_loss_receipt_v1",
        "disposition": "whole_carrier_reset",
        "source_history_digest": payload_identity(
            "history_content_identity_payload", carrier_content(current, reset)
        ),
        "target_initializer_id": "zero_carrier_v1",
        "information_loss": "carrier_history_loss",
    }
    policy["carrier_history_policy_digest"] = payload_identity(
        "history_channel_policy_identity_payload",
        {
            "schema_version": "grcv4-history-channel-policy-identity-v1",
            "policy": policy["carrier"],
        },
    )
    return validate_payload("expansion_history_policy", policy)


def transfer(source, target, event, state, reference_current):
    result = common.transfer(source, target, event, state, reference_current)
    source_resource = state["C"][source["live_node_ids"].index("source-s")]
    for k, share in enumerate((Q(1, 4), Q(3, 8), Q(3, 8)), 1):
        index = target["live_node_ids"].index(event + "/satellite/" + str(k))
        result["authoritative"]["C"][index] = float(Q(source_resource) * share)
    result["authoritative"]["Z_4"] = [0.0] * len(target["edges"]) ** 2
    return result


def provenance():
    result = common.provenance()
    from grcv4_explorer.forensic import contract_provenance
    from grcv4_explorer.successor import load_successor_forensic_context

    side = (
        ROOT
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
    )
    context = load_successor_forensic_context(ROOT, side)
    trace = contract_provenance(context, "D10.2-EC-PARENT-REAL-PC")
    require(trace["row_count"] == 1, "ambiguous PC provenance")
    row = trace["rows"][0]
    result.append(
        {
            "contract_id": "D10.2-EC-PARENT-REAL-PC",
            "trace_digest": trace["trace_digest"],
            "source_bundle_digest": trace["source_bundle_digest"],
            "source_ref": row["source_ref"],
            "edge_refs": row["edge_refs"],
            "support_disposition": row["payload"]["support_disposition"],
        }
    )
    return result


def model_for(graph):
    return StagedRows(graph["live_node_ids"], deepcopy(graph["edges"]), PARAMS)


def sqrt_upper(x):
    return endpoint(IV.sqrt(number(x)), 1)


def opnorm(matrix):
    rows = max(
        sum(upper_abs(matrix[i, j]) for j in range(matrix.cols))
        for i in range(matrix.rows)
    )
    cols = max(
        sum(upper_abs(matrix[i, j]) for i in range(matrix.rows))
        for j in range(matrix.cols)
    )
    return sqrt_upper(rows * cols)


def whole_chart(
    graph,
    *,
    radius=Q(RADIUS),
    kappa=Q(KAPPA_H),
    resource=Q(RESOURCE_RADIUS),
    low=Q(W_MIN),
    high=Q(W_MAX),
):
    """Euclidean current and Frobenius source bounds on the entire declared chart.

    Each fixed row is a positive-weight convex average of neighbor differences.
    A component is bounded by sqrt(2)*M, hence ||gradient||2<=sqrt(6)*M,
    including empty rows and loops (whose differences vanish). No WLS frame.
    |(W-G)/(W+G)|<1 gives a floor-independent inverse margin of 31/32.
    """
    require(radius > 0 and resource > 0 and 0 < low <= high, "invalid compact chart")
    m = IntervalRows(model_for(graph))
    rho = abs(kappa) * radius
    require(rho < 1, "whole carrier ball not SPD")
    lower = 1 - rho
    baseline = high * opnorm(m.D) * (high + rho / 2) * opnorm(m.B.T) * resource
    margin = Q(31, 32)
    current = baseline / margin
    descriptor_bound = sqrt_upper(Q(6)) * resource
    exponent = Q(1, 2**25) * (
        sqrt_upper(Q(2)) * resource + (2 * descriptor_bound) ** 2 + current**2
    )
    source_bound = (current / (16 * lower)) ** 2 / 2
    require(exponent <= 700, "conductance overflow bound unresolved")
    require(source_bound <= radius, "uniform source envelope exceeds carrier radius")
    return {
        k: str(v)
        for k, v in {
            "carrier_radius": radius,
            "geometry_radius": rho,
            "resource_radius": resource,
            "weight_lower": low,
            "weight_upper": high,
            "hodge_lower": lower,
            "hodge_upper": 1 + rho,
            "current_margin_lower": margin,
            "current_condition_upper": Q(33, 31),
            "descriptor_norm_upper": descriptor_bound,
            "conductance_exponent_absolute_upper": exponent,
            "current_norm_upper": current,
            "source_frobenius_upper": source_bound,
        }.items()
    }


def carrier_admitted(graph, z, radius=Q(RADIUS)):
    m = len(graph["edges"])
    z = np.asarray(z, dtype=float)
    require(z.size == m * m and np.all(np.isfinite(z)), "carrier shape/finite mismatch")
    z = z.reshape(m, m)
    require(np.array_equal(z, z.T), "carrier symmetry mismatch")
    ends = [{e[k]["node_id"] for k in ("tail", "head")} for e in graph["edges"]]
    require(
        all(
            z[i, j] == 0
            for i, a in enumerate(ends)
            for j, b in enumerate(ends)
            if not a & b
        ),
        "carrier star support mismatch",
    )
    squared = sum(Q(float(x)) ** 2 for x in z.flat)
    require(squared <= radius**2 and radius > 0, "carrier Frobenius ball exceeded")
    return squared


def check_step(graph, c, w, z, observed):
    """Independent interval equations at entry-owned C/W/Z, including both writers."""
    c, w, z = deepcopy(c), deepcopy(w), deepcopy(z)
    require(
        len(c) == len(graph["live_node_ids"]) and len(w) == len(graph["edges"]),
        "coordinate mismatch",
    )
    require(
        all(np.isfinite(x) and x >= 0 for x in c)
        and sum(Q(x) ** 2 for x in c) <= RESOURCE_RADIUS**2,
        "resource chart exceeded",
    )
    require(all(np.isfinite(x) and W_MIN <= x <= W_MAX for x in w), "W chart exceeded")
    carrier_admitted(graph, z)
    cert = whole_chart(graph)
    high = IntervalRows(model_for(graph))
    ci, wi = vector(c), vector(w)
    zi = IV.matrix(np.asarray(z).reshape(len(w), len(w)).tolist())
    h = high.I + number(KAPPA_H) * zi
    read = high.read("A", ci, wi, h)
    cn = ci - number(DT) * high.B * read["J"]
    wn = high.write(cn, wi, read["J"])
    decay = IV.exp(-number(DT))
    zn = decay * zi + (1 - decay) * read["source"]
    exact = {
        "C": cn,
        "W_A": wn,
        "Z_4": zn,
        "current": read["J"],
        "baseline": read["baseline"],
        "H": h,
        "source": read["source"],
    }
    limits = {
        "C": RESOURCE_ERROR,
        "W_A": HISTORY_ERROR,
        "Z_4": CARRIER_ERROR,
        "current": CURRENT_ERROR,
        "baseline": CURRENT_ERROR,
        "H": GEOMETRY_ERROR,
        "source": SOURCE_ERROR,
    }
    errors = {}
    require(set(observed) == set(exact), "step output fields mismatch")
    for key, truth in exact.items():
        point = np.asarray(observed[key], dtype=float)
        require(
            point.size == truth.rows * truth.cols and np.all(np.isfinite(point)),
            key + " output shape/finite mismatch",
        )
        error = full_error(point.reshape(-1), IV.matrix(list(truth)))
        require(error < limits[key], key + " full error budget unresolved")
        errors[key] = error
    carrier_admitted(graph, observed["Z_4"])
    require(all(endpoint(x, 0) >= 0 for x in cn), "negative next resource")
    require(
        all(W_MIN <= endpoint(x, 0) <= endpoint(x, 1) <= W_MAX for x in wn),
        "next W chart exceeded",
    )
    return {
        "errors": errors,
        "domain": cert,
        "high": high,
        "c": ci,
        "w": wi,
        "z": zi,
        "H": h,
        "read": read,
        "C": cn,
        "W_A": wn,
        "Z_4": zn,
    }


def build():
    shared = json.loads(
        (ROOT / (PHASE + "tranche-8/P9-8.0-COS-ConstructionInputs.json")).read_text()
    )
    source = graph_payload(
        shared["source_graph"]["nodes"], shared["source_graph"]["edges"]
    )
    paper = PaperAPC(source)
    initial = {
        "current": authority(
            [193 / 64] * 9 + [3.0],
            [15 / 16 + (i - 4) / 2**40 for i in range(9)],
            seed(source, "current"),
        ),
        "reset": authority(
            [201 / 64] * 8 + [193 / 64, 2.0],
            [15 / 16 - (i - 4) / 2**40 for i in range(9)],
            seed(source, "reset"),
        ),
    }
    source_step = paper.step(
        initial["current"]["C"], initial["current"]["W_A"], initial["current"]["Z_4"]
    )
    current, reset = (
        authority(source_step["C"], source_step["W_A"], source_step["Z_4"]),
        initial["reset"],
    )
    vectors = json.loads((ROOT / "specs/grc-v4-conformance-vectors.json").read_text())
    values = {v["vector_id"]: v["payload"] for v in vectors["identity_vectors"]}
    resolved = deepcopy(values["IDENTITY-GRC9V4-PARAMS"])
    resolved["expansion"]["bond_seed"] = 1
    spec_payload = deepcopy(values["IDENTITY-GRC9V4-SPECIALIZATION"])
    spec_payload.update(
        hessian_sign=-1,
        specialization_params_hash=payload_identity(
            "resolved_specialization", resolved
        ),
    )
    specialization = payload_identity("specialization_identity_payload", spec_payload)
    ref = reference(source)
    source_ids = native_identity(ref, specialization, current, reset)
    template = {
        "schema_version": "grcv4-profile-template-v1",
        "source_complete_profile_id": ref.profile.complete_profile_id,
        "profile_family_id": "A_PC",
        "topology_dependent_map_policy_id": "initialize_target_W_A_over_complete_live_edge_set_v1",
        "geometry_reference_policy_id": "rebuild_reference_hodge_from_target_candidate_A_reference_v1",
    }
    history = history_policy(current, reset)
    request = {
        "schema_version": "grc9v4-expansion-event-request-input-v1",
        "operation_id": "native-apc-oracle-expand-1",
        "source_state_digest": source_ids["scientific_digest"],
        "source_graph_digest": ref.graph.graph_digest,
        "source_node_id": "source-s",
        "target_profile_template_id": payload_identity(
            "profile_template_payload", template
        ),
        "target_specialization_id": specialization,
        "expansion_policy_id": resolved["expansion"]["policy_id"],
        "target_effective_degree": 52,
        "module_chirality": 1,
        "growth_phase": 3,
        "resource_distribution": [0.25, 0.375, 0.375],
        "history_policy": history,
        "expected_event_id": None,
        "expected_target_graph_digest": None,
    }
    event_payload = {
        k: v
        for k, v in request.items()
        if k
        not in (
            "schema_version",
            "operation_id",
            "history_policy",
            "expected_event_id",
            "expected_target_graph_digest",
        )
    }
    event_payload.update(
        schema_version="grc9v4-expansion-event-identity-v1",
        canonical_module_node_count=8,
        expansion_policy_digest=payload_identity(
            "expansion_policy_identity_payload",
            {
                "schema_version": "grc9v4-expansion-policy-identity-v1",
                "policy": resolved["expansion"],
            },
        ),
        bond_seed=1,
        candidate_history_policy_digest=history["candidate_history_policy_digest"],
        carrier_history_policy_digest=history["carrier_history_policy_digest"],
    )
    event = payload_identity("expansion_event_identity_payload", event_payload)
    # Frozen D52 role topology supplies the oracle; no native allocator is called.
    roles = shared["expected_target_roles"]

    def node(n):
        return n if n.startswith("outside-") else event + "/" + n

    edges = []
    for e in roles["edges"]:
        old = e["edge_id"].startswith("old-")
        edges.append(
            dict(
                edge_id=e["edge_id"] if old else event + "/" + e["edge_id"],
                kind="boundary"
                if old
                else "tree"
                if "/extra/" in e["edge_id"]
                else "spine",
                **{
                    end: {"node_id": node(e[end]["node_id"]), "port": e[end]["port"]}
                    for end in ("tail", "head")
                },
            )
        )
    target = graph_payload(
        sorted(map(node, roles["nodes"])), sorted(edges, key=lambda e: e["edge_id"])
    )
    target_ref, target_paper = reference(target), PaperAPC(target)
    targets, reads, continuation = {}, {}, {}
    for role, state in (("current", current), ("reset", reset)):
        reads[role] = paper.step(state["C"], state["W_A"], state["Z_4"])
        targets[role] = transfer(source, target, event, state, reads[role]["current"])
        c, w, z = (
            targets[role]["authoritative"]["C"],
            targets[role]["authoritative"]["W_A"],
            targets[role]["authoritative"]["Z_4"],
        )
        continuation[role] = []
        for _ in range(10):
            step = target_paper.step(c, w, z)
            continuation[role].append(step)
            c, w, z = step["C"], step["W_A"], step["Z_4"]
        continuation[role].append({"final_read": target_paper.step(c, w, z)})
    target_ids = native_identity(
        target_ref,
        specialization,
        targets["current"]["authoritative"],
        targets["reset"]["authoritative"],
    )
    target_history = payload_identity(
        "history_content_identity_payload",
        candidate_content(
            targets["current"]["authoritative"], targets["reset"]["authoritative"]
        ),
    )
    record = {
        "schema": "p983a_apc_oracle_v1",
        "profile_family_id": "A_PC",
        "phase": "P9-8.3A.1",
        "status": "oracle_only_no_native_execution",
        "generic_prerequisite": A_G2,
        "prerequisite_is_fixture_acceptance": False,
        "source_bindings": [
            {"path": p, "sha256": hashlib.sha256((ROOT / p).read_bytes()).hexdigest()}
            for p in SOURCES
        ],
        "side_tool_provenance": provenance(),
        "numerical_scope": {
            "dt": DT,
            "target_steps_per_role": 10,
            "carrier_radius": RADIUS,
            "kappa_H": KAPPA_H,
            "resource_radius": RESOURCE_RADIUS,
            "W_bounds": [W_MIN, W_MAX],
            "source_absolute_error": str(SOURCE_ERROR),
            "carrier_absolute_error": str(CARRIER_ERROR),
            "geometry_absolute_error": str(GEOMETRY_ERROR),
            "resource_absolute_error": str(RESOURCE_ERROR),
            "current_absolute_error": str(CURRENT_ERROR),
            "history_absolute_error": str(HISTORY_ERROR),
            "native_runtime_executed": False,
            "earlier_chronology_authenticated": False,
        },
        "initial": initial,
        "source_step": source_step,
        "source": dict(
            port_graph=source,
            reference=ref.to_payload(),
            descriptor=descriptor(source),
            current=current,
            reset=reset,
            **source_ids,
        ),
        "specialization": {
            "resolved": resolved,
            "identity_payload": spec_payload,
            "specialization_id": specialization,
        },
        "template": template,
        "request": request,
        "event_identity_payload": event_payload,
        "event_id": event,
        "target": dict(
            port_graph=target,
            reference=target_ref.to_payload(),
            descriptor=descriptor(target),
            roles=targets,
            **target_ids,
        ),
        "source_reference_reads": reads,
        "candidate_detection": {
            "stage": "fresh_postbeat_candidate_detection",
            "weight_source": "committed_postbeat_W_A",
            "source_gradient": list(
                map(float, paper.rows(current["C"], current["W_A"])[-1])
            ),
            "source_signed_hessian_diagonal": [
                -float(x) for x in paper.rows(current["C"], current["W_A"])[-1]
            ],
            "source_active_ports": 9,
            "candidate_node_ids": ["source-s"],
        },
        "continuation": continuation,
        "rejection_expectations": {
            "domain": {
                "mutations": [
                    "out_of_chart_W",
                    "out_of_chart_C",
                    "nonsymmetric_Z",
                    "unsupported_Z_entry",
                    "carrier_norm_overflow",
                    "underdeclared_whole_chart",
                ],
                "role_cases": ["current_only", "reset_only"],
                "expected_stage": "admission_or_target_readmission",
                "native_execution": "required_in_A2",
            },
            "history_policy": {
                "mutations": [
                    "stale_current_W",
                    "stale_reset_W",
                    "wrong_initializer",
                    "candidate_loss_instead_of_carrier_loss",
                    "hidden_carrier_loss",
                    "partial_carrier_preservation",
                    "wrong_source_archive_stage",
                    "whole_target_history_free_substitution",
                ],
                "expected_stage": "admission",
            },
            "atomic_publication": {
                "mutations": [
                    "target_current_charge_failure",
                    "target_reset_charge_failure",
                    "late_receipt_failure",
                    "replay_W_reference_or_receipt_tampering",
                ],
                "unchanged": [
                    "source_graph",
                    "both_authoritative_roles",
                    "profile",
                    "scientific_digest",
                    "reset_digest",
                    "lifecycle_digest",
                    "checkpoint",
                    "successful_receipts",
                ],
                "native_execution": "required_in_A2_not_claimed_by_this_oracle",
            },
        },
        "receipt_expectations": {
            "event_id": event,
            "operation_id": request["operation_id"],
            "source_state_digest": source_ids["scientific_digest"],
            "target_state_digest": target_ids["scientific_digest"],
            "source_model_identity": source_ids["model_identity"],
            "target_model_identity": target_ids["model_identity"],
            "source_reset_digest": source_ids["reset_digest"],
            "target_reset_digest": target_ids["reset_digest"],
            "actual_charge_delta": float(
                Q(adjacent_charge(targets["current"]["authoritative"]["C"]))
                - Q(adjacent_charge(current["C"]))
            ),
            "role_charge": {
                role: {
                    "target_charge": 30.140625,
                    "admitted_charge": adjacent_charge(
                        targets[role]["authoritative"]["C"]
                    ),
                    "residual": float(
                        Q(adjacent_charge(targets[role]["authoritative"]["C"]))
                        - Q(30.140625)
                    ),
                }
                for role in ("current", "reset")
            },
            "candidate": {
                "disposition": "exact_transport",
                "source_history_digest": history["candidate"]["source_history_digest"],
                "target_history_digest": target_history,
                "information_loss": "none",
            },
            "carrier": {
                "disposition": "whole_carrier_reset",
                "source_history_digest": history["carrier"]["source_history_digest"],
                "target_history_digest": payload_identity(
                    "history_content_identity_payload",
                    carrier_content(
                        targets["current"]["authoritative"],
                        targets["reset"]["authoritative"],
                    ),
                ),
                "information_loss": "carrier_history_loss",
            },
            "information_losses": ["carrier_history_loss"],
            "step_index": 1,
            "time": DT,
            "Q_target": 30.140625,
        },
    }
    record["domain_certificates"] = {
        name: whole_chart(graph)
        for name, graph in (("source", source), ("target", target))
    }
    record["carrier_archive"] = {
        "descriptor_version": "grc9v4-carrier-archive-v1",
        "event_id": event,
        "source_state_digest": source_ids["scientific_digest"],
        "source_graph_digest": ref.graph.graph_digest,
        "source_edge_ids": [e["edge_id"] for e in source["edges"]],
        "history_content": carrier_content(current, reset),
        "history_digest": history["carrier"]["source_history_digest"],
    }
    record["fixture_distinction"] = {
        "research": "unchanged P9-8.0 local carrier construction",
        "native": "separate R=2048, kappa_H=2^-14, M=16, W in [1/2,513/512]; initial W=15/16 plus signed 2^-40 offsets; satellite shares [1/4,3/8,3/8]",
        "reason": "uniform full compact chart admission with observable W/Z consumer effects; not a promotion of the small local research ball",
    }
    record["boundary_witnesses"] = boundary_witnesses(record)
    record["record_digest"] = digest(record)
    return record


def boundary_witnesses(record):
    """Interval disproofs; neither a failed upper bound nor a float is a witness."""
    graph = record["source"]["port_graph"]
    model = IntervalRows(model_for(graph))
    c = [0.0] * len(graph["live_node_ids"])
    c[graph["live_node_ids"].index("source-s")] = 16.0
    w = [0.5] * len(graph["edges"])
    read = model.read("A", vector(c), vector(w), model.I)
    # A diagonal coordinate lower bound already lower-bounds the Frobenius norm.
    source_lower = max(endpoint(read["source"][i, i], 0) for i in range(len(w)))
    require(
        source_lower > Q(1, 2**22), "small research radius counterexample unresolved"
    )
    source = {
        "C": list(record["source"]["current"]["C"]),
        "W_A": [0.75] * len(w),
        "Z_4": list(record["source"]["current"]["Z_4"]),
    }
    carrier_admitted(graph, source["Z_4"])
    fresh = PaperAPC(graph).step(source["C"], source["W_A"], source["Z_4"])
    check_step(graph, source["C"], source["W_A"], source["Z_4"], fresh)
    target = transfer(
        graph,
        record["target"]["port_graph"],
        record["event_id"],
        source,
        fresh["current"],
    )["authoritative"]
    high = IntervalRows(model_for(record["target"]["port_graph"]))
    tr = high.read("A", vector(target["C"]), vector(target["W_A"]), high.I)
    after = vector(target["C"]) - number(DT) * high.B * tr["J"]
    index = min(range(after.rows), key=lambda i: endpoint(after[i], 1))
    require(endpoint(after[index], 1) < 0, "negative target resource not certified")
    return {
        "small_research_radius_on_full_chart": {
            "C": c,
            "W_A": w,
            "Z_4": [0.0] * len(w) ** 2,
            "source_diagonal_lower": str(source_lower),
            "rejected_radius": str(Q(1, 2**22)),
            "interpretation": "this state lies in the full native base chart, outside the older local research neighborhoods; no contradiction of that research",
        },
        "admitted_event_negative_next_step": {
            "source_role": source,
            "mapped_target_role": target,
            "negative_node_id": record["target"]["port_graph"]["live_node_ids"][index],
            "next_resource_upper": str(endpoint(after[index], 1)),
            "expected_event": "admitted_with_zero_carrier",
            "expected_next_physical_step": "charge_admission_rejection_no_repair",
            "native_execution": "required_in_A2_not_claimed_here",
        },
    }


def check_event_stage(record):
    """CEC-F1: reconstruct declared physical source without trusting event inputs."""
    source, target = record["source"]["port_graph"], record["target"]["port_graph"]
    paper = PaperAPC(source)
    # Literal role schedule and seeds; caller's initial/state/archive are not oracles.
    initial = {
        "current": authority(
            [193 / 64] * 9 + [3.0],
            [15 / 16 + (i - 4) / 2**40 for i in range(9)],
            seed(source, "current"),
        ),
        "reset": authority(
            [201 / 64] * 8 + [193 / 64, 2.0],
            [15 / 16 - (i - 4) / 2**40 for i in range(9)],
            seed(source, "reset"),
        ),
    }
    step = paper.step(
        c=initial["current"]["C"],
        w=initial["current"]["W_A"],
        z=initial["current"]["Z_4"],
    )
    current = authority(step["C"], step["W_A"], step["Z_4"])
    require(
        record["initial"] == initial and record["source_step"] == step,
        "declared source schedule mismatch",
    )
    expected = {"current": current, "reset": initial["reset"]}
    for role, state in expected.items():
        require(record["source"][role] == state, "source physical stage mismatch")
        read = paper.step(state["C"], state["W_A"], state["Z_4"])
        require(
            record["source_reference_reads"][role] == read,
            "fresh source reference mismatch",
        )
        mapped = transfer(source, target, record["event_id"], state, read["current"])
        require(
            record["target"]["roles"][role] == mapped,
            "event W/C/Z/reference map mismatch",
        )
    require(
        record["carrier_archive"]["history_content"]
        == carrier_content(current, initial["reset"]),
        "archive physical stage mismatch",
    )
    require(
        record["carrier_archive"]["source_edge_ids"]
        == [e["edge_id"] for e in source["edges"]],
        "archive edge order mismatch",
    )


def validate(record, expected=None, *, numerical_checks=True, gates=True):
    if gates:
        require(
            A_G2 in admission.accepted(ROOT)["accepted_generic_runtime_support"],
            "A_PC G2 absent from accepted G3 consumed set",
        )
    expected = build() if expected is None else expected
    require(
        canonical_json_bytes(record) == canonical_json_bytes(expected),
        "oracle declaration/output drift (even if rehashed)",
    )
    check_event_stage(record)
    require(
        record["boundary_witnesses"] == boundary_witnesses(record),
        "boundary witness drift",
    )
    certs = []
    if numerical_checks:
        graph = record["source"]["port_graph"]
        state = record["initial"]["current"]
        certs.append(
            check_step(
                graph, state["C"], state["W_A"], state["Z_4"], record["source_step"]
            )
        )
        for role in ("current", "reset"):
            state = record["source"][role]
            certs.append(
                check_step(
                    graph,
                    state["C"],
                    state["W_A"],
                    state["Z_4"],
                    record["source_reference_reads"][role],
                )
            )
            state = record["target"]["roles"][role]["authoritative"]
            for row in record["continuation"][role]:
                result = row.get("final_read", row)
                certs.append(
                    check_step(
                        record["target"]["port_graph"],
                        state["C"],
                        state["W_A"],
                        state["Z_4"],
                        result,
                    )
                )
                if "final_read" not in row:
                    state = result
    return certs


def effects(record):
    """Each named consumer is separated using composed full errors and 8 ULPs."""
    result = []
    for label in ("source", "target"):
        graph = record[label]["port_graph"]
        paper = PaperAPC(graph)
        for role in ("current", "reset"):
            state = (
                record["source"][role]
                if label == "source"
                else record["target"]["roles"][role]["authoritative"]
            )
            c, w, z = state["C"], state["W_A"], state["Z_4"]
            step = paper.step(c, w, z)
            truth = check_step(graph, c, w, z, step)
            high = truth["high"]
            h = paper.I + paper.mp.mpf(KAPPA_H) * paper.mp.matrix(
                np.asarray(z).reshape(len(w), len(w)).tolist()
            )
            read = paper.read(c, w, h)

            def compare(name, a, b, ai, bi, label=label, role=role):
                result.append(
                    dict(
                        graph=label,
                        role=role,
                        effect=name,
                        **separation(
                            np.asarray(a, dtype=float).reshape(-1),
                            np.asarray(b, dtype=float).reshape(-1),
                            IV.matrix(list(ai)),
                            IV.matrix(list(bi)),
                        ),
                    )
                )

            for channel in (
                ("geometry", "feedback") if label == "source" else ("feedback",)
            ):
                off = paper.read(c, w, h, **{channel: False})
                off_i = high.read(
                    "A", truth["c"], truth["w"], truth["H"], **{channel: False}
                )
                compare(
                    channel,
                    step["current"],
                    list(off["current"]),
                    truth["read"]["J"],
                    off_i["J"],
                )
            if label == "source":
                continue
            require(h == paper.I, "zero-carrier PC entry must have reference geometry")

            # Compare both represented trajectories to composed exact inputs, not
            # a rounded control accepted as its own expectation.
            def point_next(wv, zv, paper=paper, step=step, w=w, **flags):
                hm = paper.I + paper.mp.mpf(KAPPA_H) * paper.mp.matrix(
                    np.asarray(zv, dtype=float).reshape(len(w), len(w)).tolist()
                )
                return paper.read(step["C"], list(map(float, wv)), hm, **flags)[
                    "current"
                ]

            def exact_next(wv, zv, high=high, truth=truth, **flags):
                return high.read(
                    "A", truth["C"], wv, high.I + number(KAPPA_H) * zv, **flags
                )["J"]

            nxt = point_next(step["W_A"], step["Z_4"])
            ni = exact_next(truth["W_A"], truth["Z_4"])
            zero = np.zeros((len(w), len(w)))
            compare(
                "written_carrier_next_current",
                list(nxt),
                list(point_next(step["W_A"], zero)),
                ni,
                exact_next(truth["W_A"], IV.matrix(zero.tolist())),
            )
            compare(
                "next_geometry",
                list(nxt),
                list(point_next(step["W_A"], step["Z_4"], geometry=False)),
                ni,
                exact_next(truth["W_A"], truth["Z_4"], geometry=False),
            )
            wrong = paper.read(step["C"], step["W_A"], h)["source"]
            wrong_i = high.read("A", truth["C"], truth["W_A"], truth["H"])["source"]
            decay = paper.mp.exp(-paper.mp.mpf(DT))
            wrong_z = (1 - decay) * wrong  # target entry Z is exactly zero
            wrong_zi = (1 - IV.exp(-number(DT))) * wrong_i
            compare(
                "same_source_carrier",
                step["Z_4"],
                [float(x) for row in wrong_z.tolist() for x in row],
                truth["Z_4"],
                wrong_zi,
            )
            compare(
                "same_source_next_current",
                list(nxt),
                list(point_next(step["W_A"], wrong_z.tolist())),
                ni,
                exact_next(truth["W_A"], wrong_zi),
            )
            fresh = paper.mp.matrix(c) - paper.mp.mpf(DT) * paper.B * read["current"]
            for name, cv, jv, ci, ji in (
                (
                    "stale_resource_writer",
                    c,
                    read["current"],
                    truth["c"],
                    truth["read"]["J"],
                ),
                (
                    "baseline_current_writer",
                    fresh,
                    read["baseline"],
                    truth["C"],
                    truth["read"]["baseline"],
                ),
            ):
                wc = paper.write(cv, w, jv)
                wci = high.write(ci, truth["w"], ji)
                compare(name + "_W", step["W_A"], list(wc), truth["W_A"], wci)
                compare(
                    name + "_next_current",
                    list(nxt),
                    list(point_next(wc, step["Z_4"])),
                    ni,
                    exact_next(wci, truth["Z_4"]),
                )
            compare(
                "next_current_consumes_written_W",
                list(nxt),
                list(point_next(w, step["Z_4"])),
                ni,
                exact_next(truth["w"], truth["Z_4"]),
            )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit",
        action="store_true",
        help="Write independent A.1 expectations; never use in A.2.",
    )
    args = parser.parse_args()
    expected = build()
    certs = validate(expected, expected)
    margins = effects(expected)
    if args.emit:
        (ROOT / RECORD).write_text(json.dumps(expected, indent=2) + "\n")
    else:
        validate(
            json.loads((ROOT / RECORD).read_text()), expected, numerical_checks=False
        )
    print(
        json.dumps(
            {
                "result": "P983A_APC_ORACLE_PASS",
                "comparisons": len(certs),
                "effect_controls": len(margins),
                "minimum_effect_margin": min(
                    x["minimum_margin_ratio"] for x in margins
                ),
                "maximum_errors": {
                    k: float(max(c["errors"][k] for c in certs))
                    for k in certs[0]["errors"]
                },
                "chart_bounds": {
                    name: {k: float(Q(v)) for k, v in cert.items()}
                    for name, cert in expected["domain_certificates"].items()
                },
                "effects": margins,
                "record_digest": expected["record_digest"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
