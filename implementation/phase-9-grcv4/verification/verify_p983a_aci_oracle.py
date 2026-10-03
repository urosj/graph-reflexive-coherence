"""Independent A_CI A.1 expectations; no native CI/event numerical execution.

Shared A constitutive/history equations come from the accepted A_OS oracle;
this producer solves the simultaneous CI equation and has no OS pass. Separate
interval equations certify every result and a whole Frobenius root domain.
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
import test_p980_realization_numerical as numerical
import verify_p983a_aos_oracle as common
from test_p980_os_effect_witness import (
    IV,
    PARAMS,
    IntervalRows,
    endpoint,
    full_error,
    inverse,
    number,
    separation,
    upper_abs,
    vector,
)
from test_p980_os_numerical_feasibility import StagedRows

from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry
from pygrc.models.grc_v4_profile import resolve_profile

ROOT = Path(__file__).resolve().parents[3]
PHASE = common.PHASE
RECORD = PHASE + "tranche-8/P9-8.3A.1-ACI-Oracle.json"
A_G2 = "grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946"
DT = common.DT
RADIUS = (
    2**-20
)  # Proposed native Frobenius domain, separate from research infinity ball.
TOLERANCE = 2**-44
CURRENT_ERROR = RESOURCE_ERROR = Q(1, 2**40)
HISTORY_ERROR = GEOMETRY_ERROR = Q(1, 2**48)
SOURCE_ERROR = Q(1, 2**64)
SOURCES = (
    *common.SOURCES,
    PHASE + "tranche-7/P9-7.7-A_CI-G2Acceptance.json",
    PHASE + "tranche-8/P9-8.0-CI-ConstructionInputs.json",
    PHASE + "tranche-8/P9-8.0-CIEventConstruction.md",
    PHASE + "tranche-8/P9-8.0-CIEventIndependentReview.md",
    PHASE + "verification/test_p980_ci_event_companion.py",
    PHASE + "verification/test_p980_realization_numerical.py",
    PHASE + "verification/test_p980_revised_realization_bounds.py",
    PHASE + "verification/verify_p983a_aos_oracle.py",
)
require, digest = common.require, common.digest
graph_payload, descriptor = common.graph_payload, common.descriptor
authority, native_identity = common.authority, common.native_identity
history_policy, candidate_content = common.history_policy, common.candidate_content
transfer, adjacent_charge = common.transfer, common.adjacent_charge


class PaperACI(common.PaperAOS):
    """100-digit fixed point of H=I+S(C,W,H)/2, using fresh G_W each trial."""

    def root(self, c, w, *, source=True, geometry=True, feedback=True):
        c, w = tuple(c), tuple(w)
        h = self.I.copy()
        for _ in range(8):
            read = self.read(c, w, h, geometry=geometry, feedback=feedback)
            h = self.I + read["source"] / 2 if source else self.I.copy()
        read = self.read(c, w, h, geometry=geometry, feedback=feedback)
        return h, read

    def step(self, c, w):
        c, w = tuple(c), tuple(w)
        h, read = self.root(c, w)
        cn = self.mp.matrix(c) - self.mp.mpf(DT) * self.B * read["current"]
        wn = self.write(cn, w, read["current"])
        return {
            "C": list(map(float, cn)),
            "W_A": list(map(float, wn)),
            "current": list(map(float, read["current"])),
            "baseline": list(map(float, read["baseline"])),
            "H": [[float(x) for x in row] for row in h.tolist()],
            "source": [[float(x) for x in row] for row in read["source"].tolist()],
        }


def reference(graph):
    """Identity-only reuse; replace the complete realization/solver declaration."""
    ref = common.reference(graph)
    params = ref.profile.params_resolved.to_payload()
    identity = ref.profile.identity_payload.to_payload()
    # Literal identity grammar from the accepted generic CI domain descriptor.
    params["realization"] = {
        "schema_version": "grcv4-ci-params-v1",
        "contraction_domain_id": "ci_reference_frobenius_ball_v1:"
        + float(RADIUS).hex(),
        "root_selector_id": "unique_admitted_root_v1",
        "iteration_limit": 60,
        "residual_norm_id": "joint_current_geometry_l2_v1",
        "tolerance": TOLERANCE,
    }
    params["solver"].update(solver_kind="fixed_point", iteration_limit=60)
    identity.update(
        profile_family_id="A_CI",
        realization="CI",
        solver_id="ci_reduced_fixed_point_v1",
        params_hash=payload_identity("resolved_params", params),
    )
    return GRCV4ReferenceGeometry(
        ref.graph,
        resolve_profile(params, identity),
        ref.context,
        ref.K4_base,
        ref.edge_weights,
    )


def provenance():
    # common.provenance installs the repository's side-tool import path.
    result = common.provenance()
    from grcv4_explorer.forensic import contract_provenance
    from grcv4_explorer.successor import load_successor_forensic_context

    side = (
        ROOT
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
    )
    context = load_successor_forensic_context(ROOT, side)
    trace = contract_provenance(context, "D10.2-EC-PARENT-REAL-CI")
    require(trace["row_count"] == 1, "ambiguous CI provenance")
    row = trace["rows"][0]
    result.append(
        {
            "contract_id": "D10.2-EC-PARENT-REAL-CI",
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


def frobenius_domain(graph, c, w, radius=Q(RADIUS)):
    """Independent l2/Frobenius self-map and Lipschitz sufficient bounds.

    Incoming rows depend on exact C,W only. A baseline component's H derivative
    is bounded by w_e*||row_e(B^T B)||_2*||B^T C||_2/2. The remaining diagonal
    current and flattened-read bounds propagate that derivative over the whole
    symmetric ball. The star mask's entries have magnitude <=1.
    """
    model = IntervalRows(model_for(graph))
    ci, wi = vector(c), vector(w)
    require(0 < radius < 1, "invalid Frobenius radius")
    require(
        len(c) == len(model.nodes) and len(w) == len(model.edges), "coordinate mismatch"
    )
    require(all(Q(x) > 0 for x in w), "positive W required")
    d = model.B.T * ci
    norm_d = sqrt_upper(sum(upper_abs(x) ** 2 for x in d))
    jref = -IV.diag(list(wi)) * model.D * IV.diag(list(wi)) * d
    lips = [
        Q(x)
        * sqrt_upper(sum(upper_abs(model.D[i, k]) ** 2 for k in range(len(w))))
        * norm_d
        / 2
        for i, x in enumerate(w)
    ]
    jr = IV.matrix(
        [
            IV.mpf([(x - number(lip * radius)).a, (x + number(lip * radius)).b])
            for x, lip in zip(jref, lips, strict=True)
        ]
    )
    drive = model.conductance(
        ci, wi, jr
    )  # Also certifies inactive floor over the entire ball.
    q = IV.matrix([(x - g) / (x + g) for x, g in zip(wi, drive, strict=True)])
    margin = min(endpoint(1 - x / 32, 0) for x in q)
    require(margin > 0, "current block not certified")
    condition = max(endpoint(1 - x / 32, 1) for x in q) / margin
    require(condition <= 10**8, "whole-domain conditioning unresolved")
    qmax = max(upper_abs(x) for x in q)
    qlip = max(
        Q(1, 2**24) * upper_abs(x) * lip / 2 for x, lip in zip(jr, lips, strict=True)
    )
    j0 = sqrt_upper(sum(upper_abs(x) ** 2 for x in jr))
    l0 = sqrt_upper(sum(x * x for x in lips))
    j = j0 / margin
    lj = l0 / margin + j0 * qlip / (32 * margin**2)
    lower = 1 - radius
    flat = qmax * j / (16 * lower)
    lip = (qmax * j / lower**2 + (qlip * j + qmax * lj) / lower) / 16
    displacement = flat**2 / 4
    contraction = flat * lip / 2
    require(displacement <= radius, "Frobenius self-map not certified")
    require(contraction < 1, "Frobenius contraction unresolved")
    return {
        "radius": str(radius),
        "norm": "frobenius",
        "displacement_upper": str(displacement),
        "contraction_upper": str(contraction),
        "current_margin_lower": str(margin),
        "conditioning_upper": str(condition),
        "floor_chart": "inactive",
    }


def check_step(graph, c, w, observed):
    """Check saved operands against independent full-formula interval equations."""
    c, w = tuple(c), tuple(w)
    model = model_for(graph)
    observed = deepcopy(observed)
    read = {
        "J": np.array(observed["current"]),
        "baseline": np.array(observed["baseline"]),
        "source": np.array(observed["source"]),
    }
    domain = frobenius_domain(graph, c, w)
    high = IntervalRows(model)
    ci, wi = vector(c), vector(w)
    m = len(w)
    h = np.array(observed["H"])
    numerical.finite_array(h, (m, m))
    require(
        np.array_equal(h, h.T) and np.all(h[model.mask == 0] == 0),
        "geometry structure mismatch",
    )
    hi_point = IV.matrix(h.tolist())
    norm = lambda matrix: sqrt_upper(sum(upper_abs(x) ** 2 for x in matrix))
    require(norm(hi_point - high.I) <= Q(RADIUS), "geometry outside root ball")
    # The declared joint norm uses the represented J, not the exactly eliminated
    # current. Check both equations before using a reduced-map root enclosure.
    point = high.read("A", ci, wi, hi_point)
    drive = high.conductance(ci, wi, point["baseline"])
    contrast = [(x - g) / (x + g) for x, g in zip(wi, drive, strict=True)]
    represented_j = vector(observed["current"])
    causal = IV.matrix(
        [x * j / 16 for x, j in zip(contrast, represented_j, strict=True)]
    )
    fj = represented_j - point["baseline"] - causal / 2
    flat = inverse(hi_point) * causal
    source_j = IV.matrix(
        [
            [number(model.mask[i, k]) * flat[i] * flat[k] / 2 for k in range(m)]
            for i in range(m)
        ]
    )
    fh = hi_point - high.I - source_j / 2
    joint_residual = sqrt_upper(
        sum(upper_abs(x) ** 2 for x in fj) + sum(upper_abs(x) ** 2 for x in fh)
    )
    require(joint_residual <= Q(TOLERANCE), "joint residual exceeds declared tolerance")
    q = Q(domain["contraction_upper"])
    image = high.I + high.read("A", ci, wi, hi_point)["source"] / 2
    residual = norm(hi_point - image)
    root_error = residual / (1 - q)
    require(root_error < GEOMETRY_ERROR, "geometry error budget unresolved")
    padding = q * root_error
    hi = IV.matrix(
        [
            [
                IV.mpf(
                    [
                        (image[i, j] - number(padding)).a,
                        (image[i, j] + number(padding)).b,
                    ]
                )
                if model.mask[i, j]
                else number(0)
                for j in range(m)
            ]
            for i in range(m)
        ]
    )
    enclosed = high.read("A", ci, wi, hi)
    for field, key, limit in [
        ("current", "J", CURRENT_ERROR),
        ("baseline", "baseline", CURRENT_ERROR),
        ("source", "source", SOURCE_ERROR),
    ]:
        values = read[key]
        numerical.finite_array(values, (m, m) if field == "source" else (m,))
        error = (
            numerical.matrix_error(values, enclosed[key])
            if field == "source"
            else full_error(values, enclosed[key])
        )
        require(error < limit, "entry-referenced " + field + " expectation failed")
    truth = {
        "high": high,
        "H": hi,
        "read": enclosed,
        "c": ci,
        "w": wi,
        "certificate": {
            "contraction": q,
            "residual": residual,
            "joint_residual": joint_residual,
            "root_error": root_error,
        },
    }
    cn = truth["c"] - number(DT) * truth["high"].B * truth["read"]["J"]
    wn = truth["high"].write(cn, truth["w"], truth["read"]["J"])
    for field, value, limit in [("C", cn, RESOURCE_ERROR), ("W_A", wn, HISTORY_ERROR)]:
        require(
            full_error(observed[field], value) < limit,
            "entry-referenced " + field + " expectation failed",
        )
    require(
        min(observed["C"]) > 0 and min(observed["W_A"]) > 0,
        "positive continuation failed",
    )
    return {"truth": truth, "C": cn, "W_A": wn, "domain": domain}


def build():
    shared = json.loads(
        (ROOT / (PHASE + "tranche-8/P9-8.0-COS-ConstructionInputs.json")).read_text()
    )
    source = graph_payload(
        shared["source_graph"]["nodes"], shared["source_graph"]["edges"]
    )
    paper = PaperACI(source)
    initial = {
        "current": authority(
            [193 / 64] * 9 + [3.0], [1023 / 1024 + (i - 4) / 2**40 for i in range(9)]
        ),
        "reset": authority(
            [201 / 64] * 8 + [193 / 64, 2.0],
            [1023 / 1024 - (i - 4) / 2**40 for i in range(9)],
        ),
    }
    source_step = paper.step(initial["current"]["C"], initial["current"]["W_A"])
    current, reset = authority(source_step["C"], source_step["W_A"]), initial["reset"]
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
        "profile_family_id": "A_CI",
        "topology_dependent_map_policy_id": "initialize_target_W_A_over_complete_live_edge_set_v1",
        "geometry_reference_policy_id": "rebuild_reference_hodge_from_target_candidate_A_reference_v1",
    }
    history = history_policy(current, reset)
    request = {
        "schema_version": "grc9v4-expansion-event-request-input-v1",
        "operation_id": "native-aci-oracle-expand-1",
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
        "resource_distribution": [0.5, 0.25, 0.25],
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
    target_ref, target_paper = reference(target), PaperACI(target)
    targets, reads, continuation = {}, {}, {}
    for role, state in (("current", current), ("reset", reset)):
        reads[role] = paper.step(state["C"], state["W_A"])
        targets[role] = transfer(source, target, event, state, reads[role]["current"])
        c, w = (
            targets[role]["authoritative"]["C"],
            targets[role]["authoritative"]["W_A"],
        )
        continuation[role] = []
        for _ in range(10):
            step = target_paper.step(c, w)
            continuation[role].append(step)
            c, w = step["C"], step["W_A"]
        continuation[role].append({"final_read": target_paper.step(c, w)})
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
    negative_source = authority(current["C"], [0.995] * 9)
    negative_read = paper.step(negative_source["C"], negative_source["W_A"])
    negative_target = transfer(
        source, target, event, negative_source, negative_read["current"]
    )["authoritative"]
    record = {
        "schema": "p983a_aci_oracle_v1",
        "phase": "P9-8.3A.1",
        "profile_family_id": "A_CI",
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
            "native_frobenius_radius": RADIUS,
            "independent_frobenius_radius": RADIUS,
            "historical_research_infinity_radius": 2**-20,
            "joint_residual_tolerance": TOLERANCE,
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
            "target_domain": {
                "source_role": negative_source,
                "mapped_target_role": negative_target,
                "role_cases": ["current_only", "reset_only"],
                "identity_scope": "role_normalized_numerical_probe_recompute_all_native_event_identities_in_A2",
                "expected_stage": "target_readmission",
                "expected_disposition": "domain_failure",
                "reason": "reference_point_geometry_image_outside_declared_Frobenius_ball",
            },
            "history_policy": {
                "mutations": [
                    "stale_current_W",
                    "stale_reset_W",
                    "wrong_initializer",
                    "claimed_loss",
                    "claimed_carrier",
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
                "disposition": "not_applicable",
                "source_history_digest": None,
                "target_history_digest": None,
                "information_loss": "none",
            },
            "information_losses": [],
            "step_index": 1,
            "time": DT,
            "Q_target": 30.140625,
        },
    }
    record["domain_certificates"] = {
        label: {
            role: frobenius_domain(part["port_graph"], state["C"], state["W_A"])
            for role, state in (
                ((role, part[role]) for role in ("current", "reset"))
                if label == "source"
                else (
                    (role, part["roles"][role]["authoritative"])
                    for role in ("current", "reset")
                )
            )
        }
        for label, part in (("source", record["source"]), ("target", record["target"]))
    }
    record["A2_proof_bridge"] = {
        "owner": "src/pygrc/models/grc_v4_ci.py",
        "function": "_a_descriptors_exact",
        "current_assumption": "WLS positions, regularization, reference_weights, dimension",
        "required": "exact fixed-port row ratios at incoming C,W for analytic residual AND domain proof",
        "serialization": "dispatch the fixed-row descriptor explicitly in root/step replay recipes",
        "no_substitution": "neither WLS descriptors nor rounded row output can replace the analytic fixed-row operands",
        "native_execution": False,
    }
    record["rejection_expectations"]["target_domain"]["certificate"] = check_negative(
        record
    )
    record["record_digest"] = digest(record)
    return record


def check_negative(record):
    """An actual point in the target ball has an image outside it.

    A lower bound disproves the self-map property itself; a loose sufficient
    upper bound alone would not. This does not assert that no root exists.
    """
    negative = record["rejection_expectations"]["target_domain"]
    source = record["source"]["port_graph"]
    target = record["target"]["port_graph"]
    before, after = negative["source_role"], negative["mapped_target_role"]
    frobenius_domain(source, before["C"], before["W_A"])
    point = PaperACI(source).step(before["C"], before["W_A"])
    check_step(source, before["C"], before["W_A"], point)
    expected = transfer(source, target, record["event_id"], before, point["current"])[
        "authoritative"
    ]
    require(
        canonical_json_bytes(after) == canonical_json_bytes(expected),
        "negative history/resource map mismatch",
    )
    high = IntervalRows(model_for(target))
    read = high.read("A", vector(after["C"]), vector(after["W_A"]), high.I)
    lower = (
        sum(max(endpoint(x, 0), -endpoint(x, 1), Q(0)) ** 2 for x in read["source"]) / 4
    )
    require(lower > Q(RADIUS) ** 2, "target image exit not certified by a lower bound")
    require(read["regularity"] > Q(1, 2), "negative current must remain regular")
    return {
        "image_frobenius_squared_lower": str(lower),
        "radius_squared": str(Q(RADIUS) ** 2),
        "current_regularity_lower": str(read["regularity"]),
    }


def validate(record, expected=None, *, numerical_checks=True, gates=True):
    if gates:
        require(
            A_G2 in admission.accepted(ROOT)["accepted_generic_runtime_support"],
            "A_CI G2 absent from accepted G3 consumed set",
        )
    expected = build() if expected is None else expected
    require(
        canonical_json_bytes(record) == canonical_json_bytes(expected),
        "oracle declaration/output drift (even if rehashed)",
    )
    certificates = []
    if numerical_checks:
        source, target = record["source"]["port_graph"], record["target"]["port_graph"]
        first = record["initial"]["current"]
        certificates.append(
            check_step(source, first["C"], first["W_A"], record["source_step"])
        )
        for role in ("current", "reset"):
            state = record["source"][role]
            certificates.append(
                check_step(
                    source,
                    state["C"],
                    state["W_A"],
                    record["source_reference_reads"][role],
                )
            )
            state = record["target"]["roles"][role]["authoritative"]
            for row in record["continuation"][role]:
                result = row.get("final_read", row)
                certificates.append(
                    check_step(target, state["C"], state["W_A"], result)
                )
                if "final_read" not in row:
                    state = result
        check_negative(record)
    return certificates


def effects(record):
    """Fixed-root path controls, a source-off root, and correctly bound A writers."""
    result = []
    for label in ("source", "target"):
        graph = record[label]["port_graph"]
        paper = PaperACI(graph)
        for role in ("current", "reset"):
            state = (
                record["source"][role]
                if label == "source"
                else record["target"]["roles"][role]["authoritative"]
            )
            c, w = tuple(state["C"]), tuple(state["W_A"])
            step = paper.step(c, w)
            checked = check_step(graph, c, w, step)
            truth = checked["truth"]
            high = truth["high"]
            h, read = paper.root(c, w)
            for channel in ("geometry", "feedback"):
                control = paper.read(c, w, h, **{channel: False})
                exact = high.read(
                    "A", truth["c"], truth["w"], truth["H"], **{channel: False}
                )
                result.append(
                    dict(
                        graph=label,
                        role=role,
                        effect=channel,
                        **separation(
                            step["current"],
                            list(map(float, control["current"])),
                            truth["read"]["J"],
                            exact["J"],
                        ),
                    )
                )
            _h0, off = paper.root(c, w, source=False)
            exact = high.read("A", truth["c"], truth["w"], high.I)
            result.append(
                dict(
                    graph=label,
                    role=role,
                    effect="entire_root_source_off",
                    **separation(
                        step["current"],
                        list(map(float, off["current"])),
                        truth["read"]["J"],
                        exact["J"],
                    ),
                )
            )
            if label == "target":
                fresh = (
                    paper.mp.matrix(c) - paper.mp.mpf(DT) * paper.B * read["current"]
                )
                for name, control, exact in (
                    (
                        "stale_resource_writer",
                        paper.write(c, w, read["current"]),
                        high.write(truth["c"], truth["w"], truth["read"]["J"]),
                    ),
                    (
                        "baseline_current_writer",
                        paper.write(fresh, w, read["baseline"]),
                        high.write(checked["C"], truth["w"], truth["read"]["baseline"]),
                    ),
                ):
                    result.append(
                        dict(
                            graph=label,
                            role=role,
                            effect=name,
                            **separation(
                                step["W_A"],
                                list(map(float, control)),
                                checked["W_A"],
                                exact,
                            ),
                        )
                    )
                # Same represented post-step C; each branch owns its exact W operands.
                new, held = paper.step(step["C"], step["W_A"]), paper.step(step["C"], w)
                cn = check_step(graph, step["C"], step["W_A"], new)["truth"]["read"][
                    "J"
                ]
                ch = check_step(graph, step["C"], w, held)["truth"]["read"]["J"]
                result.append(
                    dict(
                        graph=label,
                        role=role,
                        effect="next_root_consumes_written_W",
                        **separation(new["current"], held["current"], cn, ch),
                    )
                )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit",
        action="store_true",
        help="Write independently generated expectations; never use in A.2.",
    )
    args = parser.parse_args()
    expected = build()
    certificates = validate(expected, expected)
    margins = effects(expected)
    if args.emit:
        (ROOT / RECORD).write_text(json.dumps(expected, indent=2) + "\n")
    else:
        record = json.loads((ROOT / RECORD).read_text())
        validate(record, expected, numerical_checks=False)
    print(
        json.dumps(
            {
                "result": "P983A_ACI_ORACLE_PASS",
                "comparisons": len(certificates),
                "effect_controls": len(margins),
                "minimum_effect_margin": min(
                    x["minimum_margin_ratio"] for x in margins
                ),
                "negative": check_negative(expected),
                "record_digest": expected["record_digest"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
