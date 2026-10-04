"""Independent A_RG2b native-scoped oracle; no native realization/event execution.

Accepted signed research completion, literal fixed-row equations and independent
full interval residuals certify every saved chain and physical output. Production
imports supply identity/serialization only. Runtime A.2 consumes the pinned result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q

import numpy as np
import phase9_specialization_acceptance as admission
import test_p980_rg2b_completion as proof
import test_p980_rg2b_numerical as numerical
import verify_p983a_aos_oracle as common
from test_p980_os_effect_witness import (
    IV,
    PARAMS,
    IntervalRows,
    endpoint,
    full_error,
    number,
    separation,
    staged_write,
    vector,
)

from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_profile import get_supported_profile, resolve_profile

ROOT, PHASE, DT = common.ROOT, common.PHASE, common.DT
RECORD = PHASE + "tranche-8/P9-8.3A.1-ARG2b-Oracle.json"
A_G2 = "grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b"
EXTENSION = "grc9v4_a_rg2b_signed_argument_completion_v1"
APPROXIMATION = "grc9v4_a_rg2b_chain4_sweeps18_binary64_interval160_v1"
CONTAINMENT = "grc9v4_a_rg2b_signed_tree17_global_certificate_v1"
ERROR_NORM = "grc9v4_rg2b_hodge_induced_infinity_v1"
DEPTH, SWEEPS, MAP_BUDGET = 4, 18, 148
RESOURCE_ERROR, CURRENT_ERROR = Q(1, 2**40), Q(1, 2**40)
HISTORY_ERROR, SECTION_ERROR, SOURCE_ERROR = Q(1, 2**48), Q(1, 2**48), Q(1, 2**64)
SOURCES = tuple(
    dict.fromkeys(
        (
            *common.SOURCES,
            PHASE + "tranche-7/P9-7.7-A_RG2b-G2Acceptance.json",
            PHASE + "tranche-8/P9-8.0-RG2bCompletion.md",
            PHASE + "tranche-8/P9-8.0-RG2bNumericalFeasibility.md",
            PHASE + "tranche-8/P9-8.0-RG-ConstructionInputs.json",
            PHASE + "tranche-8/rg-numerical-review/SelfReview.md",
            PHASE + "tranche-8/P9-8.0-RGEventConstruction.md",
            PHASE + "tranche-8/P9-8.0-AllProfileFeasibility.md",
            PHASE + "verification/test_p980_revised_realization_bounds.py",
            PHASE + "verification/test_p980_rg2b_completion.py",
            PHASE + "verification/test_p980_rg2b_numerical.py",
            PHASE + "verification/test_p980_rg_event_companion.py",
            PHASE + "verification/test_p980_rg_implementation_review.py",
            PHASE + "verification/verify_p983a_aos_oracle.py",
        )
    )
)
require, digest = common.require, common.digest
authority, graph_payload = common.authority, common.graph_payload
descriptor, native_identity = common.descriptor, common.native_identity
history_policy, candidate_content = common.history_policy, common.candidate_content
transfer, adjacent_charge = common.transfer, common.adjacent_charge


def reference(graph):
    base = common.reference(graph)
    params = base.profile.params_resolved.to_payload()
    identity = get_supported_profile(A_G2).identity_payload.to_payload()
    params["realization"] = {
        "schema_version": "grcv4-rg2b-params-v1",
        "extension_evaluator_id": EXTENSION,
        "approximation_policy_id": APPROXIMATION,
        "error_norm_id": ERROR_NORM,
        "containment_certificate_id": CONTAINMENT,
        "error_tolerance": float(SECTION_ERROR),
        "iteration_limit": MAP_BUDGET,
        "failure_policy_id": "fail_closed_on_uncertified_section_v1",
    }
    identity["params_hash"] = payload_identity("resolved_params", params)
    return replace(base, profile=resolve_profile(params, identity))


def model_for(graph):
    return numerical.RepresentedAuxiliary(
        graph["live_node_ids"], deepcopy(graph["edges"]), PARAMS
    )


class PaperARG(common.PaperAOS):
    """Reuse independently certified research chains, never native RG dispatch."""

    def step(self, c, w):
        cn, wn, s = numerical.ordinary(
            model_for(self.graph), "A", np.array(c), np.array(w)
        )
        return {
            "C": cn.tolist(),
            "W_A": wn.tolist(),
            "current": s["read"]["J"].tolist(),
            "baseline": s["read"]["baseline"].tolist(),
            "source": s["read"]["source"].tolist(),
            "H": s["H"].tolist(),
            "chain": {
                "x": [v.tolist() for v in s["chain"].x],
                "h": [v.tolist() for v in s["chain"].h],
            },
        }


def provenance():
    side = (
        ROOT
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
    )
    sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance, debt_lifecycle

    context = load_current_forensic_context(ROOT, side)
    return {
        "contracts": {
            k: contract_provenance(context, k)
            for k in (
                "D11-G9-EC-RESOURCE-DISTRIBUTION",
                "D11-G9-EC-LIFECYCLE-READMISSION",
                "D11-G9-EC-FIXED-BOND-SEED",
                "D10.2-EC-PARENT-L-A-INITIALIZER-GRC9V3",
                "D10.2-EC-PARENT-BASE-GRC9-ROW-BASIS-DIFFERENTIAL",
                "D10.2-EC-PARENT-L-ATOMICITY",
                "D10.2-EC-PARENT-REAL-RG2B",
                "D10.2-EC-RG-INVARIANCE",
                "D10.2-EC-RG-LIPSCHITZ-CONTRACTION",
                "D10.2-EC-RG-DETERMINISM",
                "D10.2-EC-RG-CLAIM-CEILING",
            )
        },
        "debts": {
            "GTRS-RG-DEBT-C1-SECTION-REGULARITY": debt_lifecycle(
                context, "GTRS-RG-DEBT-C1-SECTION-REGULARITY"
            )
        },
    }


def proof_record():
    b = proof.global_bounds("A")
    s = proof.section_budgets(b)
    require(b["M_C"] < Q(1, 4) and b["M_Y"] < Q(1, 8), "containment")
    return {
        "global": {k: str(v) for k, v in b.items()},
        "section": {k: str(v) for k, v in s.items()},
        "K_minus_C": [-0.25, 4.25],
        "K_C": [-0.5, 4.5],
        "K_minus_Y": [-0.625, 0.625],
        "K_Y": [-0.75, 0.75],
        "auxiliary_C": [-1, 5],
        "auxiliary_Y": [-1, 1],
        "Y_scale": 512,
        "h_radius": str(proof.RHO),
        "section_lipschitz": str(proof.SECTION_LIP),
        "graph_class": "connected_port_trees_2_to_17_vertices_with_checked_B_D_mask_norms",
    }


def build():
    shared = json.loads(
        (ROOT / (PHASE + "tranche-8/P9-8.0-COS-ConstructionInputs.json")).read_text()
    )
    source = graph_payload(
        shared["source_graph"]["nodes"], shared["source_graph"]["edges"]
    )
    paper = PaperARG(source)
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
        "profile_family_id": "A_RG2b",
        "topology_dependent_map_policy_id": "initialize_target_W_A_over_complete_live_edge_set_v1",
        "geometry_reference_policy_id": "rebuild_reference_hodge_from_target_candidate_A_reference_v1",
    }
    history = history_policy(current, reset)
    request = {
        "schema_version": "grc9v4-expansion-event-request-input-v1",
        "operation_id": "native-arg2b-oracle-expand-1",
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
    target_ref, target_paper = reference(target), PaperARG(target)
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
    record = {
        "schema": "p983a_arg2b_oracle_v1",
        "phase": "P9-8.3A.1",
        "status": "oracle_only_no_native_execution",
        "generic_prerequisite": A_G2,
        "prerequisite_is_fixture_acceptance": False,
        "source_bindings": [
            {"path": p, "sha256": hashlib.sha256((ROOT / p).read_bytes()).hexdigest()}
            for p in SOURCES
        ],
        "side_tool_provenance": provenance(),
        "completion_proof": proof_record(),
        "numerical_scope": {
            "dt": DT,
            "target_steps_per_role": 10,
            "section_tolerance": float(SECTION_ERROR),
            "depth": DEPTH,
            "sweeps": SWEEPS,
            "map_budget": MAP_BUDGET,
            "source_absolute_error": str(SOURCE_ERROR),
            "section_absolute_error": str(SECTION_ERROR),
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
            "target_section": {
                "mutations": [
                    "wrong_graph_completion",
                    "transport_source_section",
                    "drop_W_from_base_map",
                    "positive_only_auxiliary",
                    "insufficient_budget",
                    "K_readmission_as_K_minus_step",
                ],
                "expected_stage": "target_readmission_or_ordinary_entry",
                "native_execution": "required_in_A2_not_claimed_by_this_oracle",
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

    # JSON identity admits a unique zero; signed floating scratch zeros carry
    # no mathematical authority. Normalize only zero at the evidence boundary.
    def wire(value):
        if type(value) is float and value == 0:
            return 0.0
        if isinstance(value, list):
            return [wire(v) for v in value]
        if isinstance(value, dict):
            return {k: wire(v) for k, v in value.items()}
        return value

    record = wire(record)
    record["record_digest"] = digest(record)
    return record


def chart_admitted(c, w, *, ordinary):
    """Independent physical K/K_minus membership in exact C/scaled-log-W.

    A.2 must enforce the selected chart for both roles, including ordinary dt=0.
    This helper checks declared oracle domains and does not dispatch runtime.
    """
    c, w = vector(c), vector(w)
    resource_upper, history_radius = (
        (Q(17, 4), Q(5, 8)) if ordinary else (Q(9, 2), Q(3, 4))
    )
    require(
        all(0 <= endpoint(z, 0) <= endpoint(z, 1) <= resource_upper for z in c),
        "physical C chart",
    )
    require(all(endpoint(z, 0) > 0 for z in w), "positive physical W")
    y = [number(512) * IV.ln(z) for z in w]
    require(
        all(
            -history_radius <= endpoint(z, 0) <= endpoint(z, 1) <= history_radius
            for z in y
        ),
        "scaled-log W chart",
    )


def check_step(graph, c, w, observed, *, ci=None, wi=None, require_positive=True):
    """Recompute every chain residual and formula from saved entry operands.

    Optional composed intervals describe the intended next input, not a fresh
    exact interpretation of rounded counterfactual writer output.
    """
    m = model_for(graph)
    numerical.checked_model(m)
    pc, pw = vector(c), vector(w)
    numerical.physical_input(pc, pw)
    require((ci is None) == (wi is None), "complete intended operands required")
    ci, wi = (pc, pw) if ci is None else (ci.copy(), wi.copy())
    numerical.physical_input(ci, wi)
    raw = observed["chain"]
    require(len(raw["x"]) == len(raw["h"]) == DEPTH + 1, "frozen depth mismatch")
    chain = numerical.Chain(
        [np.array(x) for x in raw["x"]], [np.array(h) for h in raw["h"]]
    )
    require(
        np.array_equal(np.array(observed["H"]), chain.h[0]), "section output mismatch"
    )
    hi, cert = numerical.certify_chain(
        proof.auxiliary(m), "A", chain, proof.state("A", ci, wi)
    )
    high = IntervalRows(m)
    read = high.read("A", ci, wi, hi)
    cn = ci - number(DT) * high.B * read["J"]
    wn = high.write(cn, wi, read["J"])
    truths = {
        "C": cn,
        "W_A": wn,
        "H": hi,
        "current": read["J"],
        "baseline": read["baseline"],
        "source": read["source"],
    }
    limits = {
        "C": RESOURCE_ERROR,
        "current": CURRENT_ERROR,
        "baseline": CURRENT_ERROR,
        "W_A": HISTORY_ERROR,
        "H": SECTION_ERROR,
        "source": SOURCE_ERROR,
    }
    errors = {}
    for key, truth in truths.items():
        arr = numerical.finite_array(
            np.array(observed[key]),
            (truth.rows, truth.cols) if key in ("H", "source") else (truth.rows,),
        )
        errors[key] = full_error(arr.ravel(), IV.matrix(list(truth)))
        require(errors[key] < limits[key], "full entry-referenced " + key + " error")
    require(read["regularity"] > Q(1, 2), "current regularity")
    require(min(observed["W_A"]) > 0, "positive writer result")
    if require_positive:
        require(
            min(observed["C"]) >= 0 and min(endpoint(z, 0) for z in cn) >= 0,
            "physical output resource negativity",
        )
    return {
        "errors": errors,
        "certificate": cert,
        "truth": truths,
        "high": high,
        "model": m,
        "c": ci,
        "w": wi,
        "read": read,
    }


def entries(record):
    graph = record["source"]["port_graph"]
    x = record["initial"]["current"]
    yield "source_physical", graph, x, record["source_step"]
    for role in ("current", "reset"):
        yield (
            "source_reference_" + role,
            graph,
            record["source"][role],
            record["source_reference_reads"][role],
        )
        x = record["target"]["roles"][role]["authoritative"]
        for i, row in enumerate(record["continuation"][role]):
            out = row.get("final_read", row)
            yield f"target_{role}_{i}", record["target"]["port_graph"], x, out
            if "final_read" not in row:
                x = out


def validate(record, expected=None, *, numerical_checks=True, gates=True):
    if gates:
        require(
            A_G2 in admission.accepted(ROOT)["accepted_generic_runtime_support"],
            "A_RG2b exact G2/G3 prerequisite",
        )
    expected = build() if expected is None else expected
    require(
        canonical_json_bytes(record) == canonical_json_bytes(expected),
        "oracle declaration/output drift even if rehashed",
    )
    if not numerical_checks:
        return []
    return [
        check_step(graph, x["C"], x["W_A"], out) for _, graph, x, out in entries(record)
    ]


def effects(record):
    results = []

    def compare(label, enabled, control, ei, oi):
        try:
            margin = separation(
                np.array(enabled).ravel(),
                np.array(control).ravel(),
                IV.matrix(list(ei)),
                IV.matrix(list(oi)),
            )
        except AssertionError as exc:
            raise AssertionError(label + ": " + str(exc)) from exc
        results.append({"control": label, **margin})

    for place in ("source", "target"):
        graph = record[place]["port_graph"]
        for role in ("current", "reset"):
            x = (
                record["source"][role]
                if place == "source"
                else record["target"]["roles"][role]["authoritative"]
            )
            out = (
                record["source_reference_reads"][role]
                if place == "source"
                else record["continuation"][role][0]
            )
            t = check_step(graph, x["C"], x["W_A"], out)
            high, m, c, w, h = (
                t["high"],
                t["model"],
                np.array(x["C"]),
                np.array(x["W_A"]),
                np.array(out["H"]),
            )
            prefix = place + "_" + role + "_"
            for name, flags in (
                ("geometry", {"geometry": False}),
                ("readback", {"feedback": False}),
            ):
                off = m.read("A", c.copy(), w.copy(), h.copy(), **flags)
                oi = high.read("A", t["c"], t["w"], t["truth"]["H"], **flags)
                compare(
                    prefix + name,
                    out["current"],
                    off["J"],
                    t["truth"]["current"],
                    oi["J"],
                )
            compare(
                prefix + "not_instantaneous_CI",
                h,
                m.I + 0.5 * np.array(out["source"]),
                t["truth"]["H"],
                high.I + number(Q(1, 2)) * t["truth"]["source"],
            )
            if place == "source":
                continue
            os = m.ordinary_os("A", c.copy(), w.copy())[2]
            osi = high.ordinary_os("A", t["c"], t["w"])[2]
            compare(
                prefix + "not_OS_current",
                out["current"],
                os["read"]["J"],
                t["truth"]["current"],
                osi["read"]["J"],
            )
            nxt = record["continuation"][role][1]
            nt = check_step(
                graph,
                out["C"],
                out["W_A"],
                nxt,
                ci=t["truth"]["C"],
                wi=t["truth"]["W_A"],
            )
            # Invariance is checked at the intended exact complete C/W poststate.
            defect = nt["truth"]["H"] - high.I - number(Q(1, 2)) * t["truth"]["source"]
            require(
                all(endpoint(v, 0) <= 0 <= endpoint(v, 1) for v in defect),
                "complete C/W invariance enclosure",
            )
            for name in ("stale_C_writer", "baseline_J_writer", "no_W_writer"):
                if name == "no_W_writer":
                    wc, wci = w.copy(), t["w"]
                else:
                    wc = staged_write(
                        m,
                        c.copy() if name == "stale_C_writer" else np.array(out["C"]),
                        w.copy(),
                        np.array(
                            out["baseline"]
                            if name == "baseline_J_writer"
                            else out["current"]
                        ),
                    )
                    wci = high.write(
                        t["c"] if name == "stale_C_writer" else t["truth"]["C"],
                        t["w"],
                        t["truth"]["baseline"]
                        if name == "baseline_J_writer"
                        else t["truth"]["current"],
                    )
                compare(prefix + name + "_W", out["W_A"], wc, t["truth"]["W_A"], wci)
                off = PaperARG(graph).step(out["C"], wc)
                ot = check_step(graph, out["C"], wc, off, ci=t["truth"]["C"], wi=wci)
                compare(
                    prefix + name + "_next_current",
                    nxt["current"],
                    off["current"],
                    nt["truth"]["current"],
                    ot["truth"]["current"],
                )
            # Incoming retained W is consumed by both the section and current.
            wc = np.ones(len(w))
            off = PaperARG(graph).step(c, wc)
            ot = check_step(graph, c, wc, off)
            compare(
                prefix + "retained_W_current",
                out["current"],
                off["current"],
                t["truth"]["current"],
                ot["truth"]["current"],
            )
            compare(
                prefix + "retained_W_section",
                out["H"],
                off["H"],
                t["truth"]["H"],
                ot["truth"]["H"],
            )
    return results


def signed_inverse(record):
    b, sb = proof.global_bounds("A"), proof.section_budgets(proof.global_bounds("A"))
    # The predecessor has one fewer section iteration than the returned H0.
    tail = (
        sb["inverse_lip"]
        * b["A_H"]
        * sb["q_section"] ** (DEPTH - 1)
        * sb["value_radius"]
    )
    result = {}
    for role in ("current", "reset"):
        graph, x = (
            record["target"]["port_graph"],
            record["target"]["roles"][role]["authoritative"],
        )
        out = record["continuation"][role][0]
        cert = check_step(graph, x["C"], x["W_A"], out)["certificate"]
        core = graph["live_node_ids"].index(record["event_id"] + "/core")
        upper = (
            Q(out["chain"]["x"][1][core])
            + cert["state_error"]
            + tail
            + sb["inverse_lip"] * cert["input_error"] / proof.SECTION_LIP
        )
        require(upper < 0, "signed first predecessor not certified negative")
        result[role] = {
            "first_predecessor_upper": str(upper),
            "inverse_section_tail": str(tail),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit",
        action="store_true",
        help="Write new independent A.1 expectations, never from native runtime.",
    )
    args = parser.parse_args()
    record = build()
    certs = validate(record, record)
    margins = effects(record)
    inv = signed_inverse(record)
    if args.emit:
        (ROOT / RECORD).write_text(json.dumps(record, indent=2) + "\n")
    else:
        validate(
            json.loads((ROOT / RECORD).read_text()), record, numerical_checks=False
        )
    print(
        json.dumps(
            {
                "result": "P983A_ARG2B_ORACLE_PASS",
                "comparisons": len(certs),
                "effect_controls": len(margins),
                "minimum_effect_margin": min(
                    r["minimum_margin_ratio"] for r in margins
                ),
                "maximum_errors": {
                    k: float(max(c["errors"][k] for c in certs))
                    for k in certs[0]["errors"]
                },
                "section_certificates": [
                    {k: str(v) for k, v in c["certificate"].items()} for c in certs
                ],
                "effects": margins,
                "signed_inverse": inv,
                "record_digest": record["record_digest"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
