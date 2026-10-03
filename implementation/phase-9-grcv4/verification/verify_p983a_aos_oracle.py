"""P9-8.3A.1: independent native-scoped A_OS oracle, never runtime execution.

Production imports below provide admitted identity/serialization primitives only.
No A constitutive, realization, writer, event planner or row evaluator produces
an expectation. Point equations use a private 100-digit context; the retained
P9-8.0 interval evaluator independently checks every ordinary/read expectation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path

import numpy as np
import phase9_specialization_acceptance as admission
from mpmath.ctx_mp import MPContext
from test_p980_os_effect_witness import (
    IV,
    PARAMS,
    IntervalRows,
    endpoint,
    full_error,
    split_admitted,
    vector,
)
from test_p980_os_numerical_feasibility import StagedRows

from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph
from pygrc.models.grc_v4_codec import (
    canonical_json_bytes,
    payload_identity,
    validate_payload,
)
from pygrc.models.grc_v4_geometry import (
    GRCV4Context,
    GRCV4Graph,
    GRCV4ReferenceGeometry,
)
from pygrc.models.grc_v4_profile import get_supported_profile, resolve_profile
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[3]
PHASE = "implementation/phase-9-grcv4/"
RECORD = PHASE + "tranche-8/P9-8.3A.1-AOS-Oracle.json"
REVIEW = PHASE + "tranche-8/P9-8.3A.1-AOS-OracleReview.md"
A_G2 = "grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4"
DT = 2**-12
SPLIT = 2**-40
CURRENT_ERROR = Q(1, 2**40)
RESOURCE_ERROR = Q(1, 2**40)
HISTORY_ERROR = Q(1, 2**48)
SOURCES = (
    "specs/grc-9-v4-spec.md",
    "specs/grc-v4-spec.md",
    "specs/grc-v4-contract-schema.json",
    "specs/grc-v4-conformance-vectors.json",
    "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
    "implementation/investigations/grc9v4-constitutive-design/decisions/D11G9CanonicalExpansionPortAllocationResolution.md",
    PHASE + "tranche-8/P9-8.0-AOS-ConstructionInputs.json",
    PHASE + "tranche-8/P9-8.0-COS-ConstructionInputs.json",
    PHASE + "tranche-8/P9-8.0-AEventConstruction.md",
    PHASE + "tranche-8/P9-8.0-AEventIndependentReview.md",
    PHASE + "verification/test_p980_a_event_companion.py",
    PHASE + "verification/test_p980_os_effect_witness.py",
    PHASE + "verification/test_p980_os_numerical_feasibility.py",
    PHASE + "verification/test_p980_fixed_row_bounds.py",
    PHASE + "tranche-7/P9-7.7-A_OS-G2Acceptance.json",
    PHASE + "tranche-7/P9-7.8-G3Acceptance.json",
    "implementation/investigations/grc9v4-constitutive-design/decisions/D11G9AxisPreservingExpansionProvenanceSupplement.json",
    "implementation/investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def provenance():
    side = (
        ROOT
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
    )
    sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.forensic import contract_provenance
    from grcv4_explorer.successor import load_successor_forensic_context

    context = load_successor_forensic_context(ROOT, side)
    result = []
    for identifier in (
        "D11-G9-EC-LIFECYCLE-READMISSION",
        "D11-G9-EC-FIXED-BOND-SEED",
        "D10.2-EC-PARENT-BASE-GRC9-ROW-BASIS-DIFFERENTIAL",
        "D10.2-EC-PARENT-L-A-INITIALIZER-GRC9V3",
        "D10.2-EC-PARENT-L-ATOMICITY",
    ):
        trace = contract_provenance(context, identifier)
        require(trace["row_count"] == 1, "ambiguous authority trace")
        row = trace["rows"][0]
        result.append(
            {
                "contract_id": identifier,
                "trace_digest": trace["trace_digest"],
                "source_bundle_digest": trace["source_bundle_digest"],
                "source_ref": row["source_ref"],
                "edge_refs": row["edge_refs"],
                "support_disposition": row["payload"]["support_disposition"],
            }
        )
    return result


class PaperAOS:
    """Literal fixed-row A equations, no production numerical dispatch."""

    def __init__(self, graph):
        self.graph = deepcopy(graph)
        self.nodes = self.graph["live_node_ids"]
        self.edges = self.graph["edges"]
        self.index = {n: i for i, n in enumerate(self.nodes)}
        self.mp = MPContext()
        self.mp.dps = 100
        self.B = self.mp.matrix(len(self.nodes), len(self.edges))
        for k, e in enumerate(self.edges):
            self.B[self.index[e["tail"]["node_id"]], k] += 1
            self.B[self.index[e["head"]["node_id"]], k] -= 1
        # The declared fixture has no loops. Endpoint multiplicity is explicit.
        self.mask = self.B.apply(abs).T * self.B.apply(abs) / 2
        self.I = self.mp.eye(len(self.edges))

    def rows(self, c, w):
        c, w = list(map(self.mp.mpf, c)), list(map(self.mp.mpf, w))
        numerator = [[self.mp.mpf(0) for _ in range(3)] for _ in c]
        denominator = [[self.mp.mpf(0) for _ in range(3)] for _ in c]
        require(
            len(w) == len(self.edges) and all(x > 0 for x in w), "positive W required"
        )
        for k, e in enumerate(self.edges):
            for here, there in ((e["tail"], e["head"]), (e["head"], e["tail"])):
                i, j = self.index[here["node_id"]], self.index[there["node_id"]]
                row = (here["port"] - 1) // 3
                numerator[i][row] += w[k] * (c[j] - c[i])
                denominator[i][row] += w[k]
        return [
            [
                numerator[i][r] / denominator[i][r]
                if denominator[i][r]
                else self.mp.mpf(0)
                for r in range(3)
            ]
            for i in range(len(c))
        ]

    def conductance(self, c, w, j):
        c, j = list(map(self.mp.mpf, c)), list(map(self.mp.mpf, j))
        rows = self.rows(c, w)
        result = []
        for e, flux in zip(self.edges, j, strict=True):
            u, v = (self.index[e[end]["node_id"]] for end in ("tail", "head"))
            exponent = (
                -(
                    c[u]
                    + c[v]
                    + sum((x - y) ** 2 for x, y in zip(rows[u], rows[v]))
                    + flux**2
                )
                / 2**25
            )
            result.append(max(self.mp.mpf(".5"), self.mp.exp(exponent)))
        return self.mp.matrix(result)

    def read(self, c, w, h=None, *, geometry=True, feedback=True):
        mp, b = self.mp, self.B
        c, w = mp.matrix(c), mp.matrix(w)
        h = self.I if h is None else mp.matrix(h)
        dc = b.T * c
        phi = b * mp.diag(w) * dc
        if geometry:
            phi += b * (h - self.I) * dc / 2
        baseline = -mp.diag(w) * b.T * phi
        drive = self.conductance(c, w, baseline)
        q = [(x - y) / (x + y) for x, y in zip(w, drive)]
        denominators = [1 - x / 32 if feedback else mp.mpf(1) for x in q]
        require(min(denominators) > 0, "A current singularity")
        current = mp.matrix([x / d for x, d in zip(baseline, denominators)])
        causal = mp.matrix(
            [x * y / 16 if feedback else mp.mpf(0) for x, y in zip(q, current)]
        )
        flat = mp.lu_solve(h, causal)
        source = mp.matrix(
            [
                [self.mask[i, k] * flat[i] * flat[k] / 2 for k in range(len(w))]
                for i in range(len(w))
            ]
        )
        return {
            "current": current,
            "baseline": baseline,
            "source": source,
            "drive": drive,
            "regularity": min(denominators),
        }

    def write(self, c, w, j):
        drive = self.conductance(c, w, j)
        decay = self.mp.exp(-self.mp.mpf(DT))
        return self.mp.matrix(
            [
                self.mp.exp(decay * self.mp.log(x) + (1 - decay) * self.mp.log(y))
                for x, y in zip(w, drive)
            ]
        )

    def step(self, c, w):
        c, w = tuple(c), tuple(w)  # Caller arrays cannot become scratch storage.
        predictor = self.read(c, w)
        h = self.I + predictor["source"] / 2
        corrector = self.read(c, w, h)
        regenerated = self.I + corrector["source"] / 2
        cn = self.mp.matrix(c) - self.mp.mpf(DT) * self.B * corrector["current"]
        wn = self.write(cn, w, corrector["current"])
        return {
            "C": list(map(float, cn)),
            "W_A": list(map(float, wn)),
            "current": list(map(float, corrector["current"])),
            "baseline": list(map(float, corrector["baseline"])),
            "H": [[float(x) for x in row] for row in h.tolist()],
            "regenerated": [[float(x) for x in row] for row in regenerated.tolist()],
        }


def graph_payload(nodes, edges):
    return {
        "schema_version": "grc9v4-port-graph-v1",
        "live_node_ids": nodes,
        "edges": edges,
    }


def descriptor(graph):
    """Proposed native binding, distinct from the admitted host-frame WLS ID.

    Retained W is a stage operand, never frozen into a backend or reference map.
    The hash authenticates this declared recipe, not implemented runtime support.
    """
    return {
        "descriptor_version": "grc9v4-candidate-a-fixed-row-v1",
        "port_graph": graph,
        "frame_mode": "fixed_port_chart",
        "hessian_backend": "row_basis_diagonal",
        "curvature_backend": "none",
        "read_weights": "incoming_W_A",
        "writer_weights": "incoming_W_A",
        "writer_resources": "admitted_final_C",
        "writer_current": "selected_physical_current",
        "empty_row": "exact_zero",
        "rounding": "exact_row_ratio_then_binary64_v1",
    }


def descriptor_id(graph):
    return "grcv4-a-descriptor-sha256:" + digest(descriptor(graph))


def reference(graph):
    typed = GRCV4Graph.from_port_graph(GRC9V4PortGraph.from_payload(graph))
    params = get_supported_profile(A_G2).params_resolved.to_payload()
    identity = get_supported_profile(A_G2).identity_payload.to_payload()
    weights = {e["edge_id"]: 1 for e in graph["edges"]}
    base = [[0] * len(weights) for _ in weights]
    params["candidate"].update(
        eta=1,
        kappa_c=1,
        W_floor=0.5,
        alpha=2**-24,
        beta=2**-24,
        gamma=2**-24,
        kappa_Ah=0.5,
        chi_A=1 / 16,
        zeta_A=0.5,
        tau_A=1,
        descriptor_backend_id=descriptor_id(graph),
    )
    params["geometry"].update(
        kappa_H=0.5,
        K4_base_digest=payload_identity(
            "k4_identity_payload",
            {"schema_version": "grcv4-k4-identity-v1", "K4_base": base},
        ),
        reference_hodge_digest=payload_identity(
            "reference_hodge_identity_payload",
            {
                "schema_version": "grcv4-reference-hodge-identity-v1",
                "edge_weights": weights,
            },
        ),
    )
    params["realization"]["tolerance"] = SPLIT
    params["solver"].update(
        conditioning_limit=1e8, absolute_tolerance=1e-11, relative_tolerance=1e-11
    )
    params["charge"].update(absolute_tolerance=1e-11, relative_tolerance=0)
    identity["params_hash"] = payload_identity("resolved_params", params)
    return GRCV4ReferenceGeometry(
        typed,
        resolve_profile(params, identity),
        GRCV4Context("constant_zero_context_v1", FrozenJSONMap({})),
        tuple(map(tuple, base)),
        FrozenJSONMap(weights),
    )


def authority(c, w):
    return {"C": list(c), "W_A": list(w), "Z_4": None}


def native_identity(ref, specialization, current, reset):
    model = payload_identity(
        "complete_model_identity_payload",
        {
            "schema_version": "grc9v4-complete-identity-v1",
            "grcv4_complete_profile_id": ref.profile.complete_profile_id,
            "specialization_id": specialization,
        },
    )
    common = {
        "active_model_identity": model,
        "graph_digest": ref.graph.graph_digest,
        "orientation_identity": ref.graph.orientation_identity,
        "Q_target": 30.140625,
        "context_contract_id": "constant_zero_context_v1",
    }
    reset_payload = dict(
        schema_version="grc9v4-reset-baseline-v1", **common, authoritative=reset
    )
    reset_id = payload_identity("grc9v4_reset_payload", reset_payload)
    state_payload = dict(
        schema_version="grcv4-scientific-state-v1",
        **common,
        authoritative=current,
        reset_digest=reset_id,
        step_index=1,
        time=DT,
        context_value_digest=None,
    )
    return {
        "model_identity": model,
        "reset_payload": reset_payload,
        "reset_digest": reset_id,
        "scientific_payload": state_payload,
        "scientific_digest": payload_identity(
            "scientific_state_payload", state_payload
        ),
    }


def candidate_content(current, reset):
    return {
        "schema_version": "grcv4-history-content-identity-v1",
        "subject": "candidate",
        "content": current["W_A"] + reset["W_A"],
    }


def adjacent_charge(values):
    """Independent prescribed binary64 adjacent-pair tree in live-node order."""
    level = list(values)
    while len(level) > 1:
        level = [
            float(Q(level[i]) + Q(level[i + 1])) if i + 1 < len(level) else level[i]
            for i in range(0, len(level), 2)
        ]
    return level[0] if level else 0.0


def history_policy(current, reset):
    candidate = {
        "schema_version": "grcv4-history-channel-policy-v1",
        "subject": "candidate",
        "policy_id": "candidate_a_exact_old_edge_lineage_positive_bond_seed_v1",
        "disposition": "exact_transport",
        "source_history_digest": payload_identity(
            "history_content_identity_payload", candidate_content(current, reset)
        ),
        "target_initializer_id": "grc9v4_new_internal_edge_positive_bond_seed_v1",
        "information_loss": "none",
    }
    carrier = {
        "schema_version": "grcv4-history-channel-policy-v1",
        "subject": "carrier",
        "policy_id": "carrier_not_applicable_v1",
        "disposition": "not_applicable",
        "source_history_digest": None,
        "target_initializer_id": None,
        "information_loss": "none",
    }
    return validate_payload(
        "expansion_history_policy",
        dict(
            schema_version="grc9v4-expansion-history-policy-v2",
            candidate=candidate,
            carrier=carrier,
            **{
                s + "_history_policy_digest": payload_identity(
                    "history_channel_policy_identity_payload",
                    {
                        "schema_version": "grcv4-history-channel-policy-identity-v1",
                        "policy": v,
                    },
                )
                for s, v in (("candidate", candidate), ("carrier", carrier))
            },
        ),
    )


def transfer(source, target, event, state, reference_current):
    """Literal P and E maps, independent of the production reconstruction."""
    cs = dict(zip(source["live_node_ids"], state["C"], strict=True))
    ws = dict(zip((e["edge_id"] for e in source["edges"]), state["W_A"], strict=True))
    js = dict(
        zip((e["edge_id"] for e in source["edges"]), reference_current, strict=True)
    )
    shares = {
        event + "/satellite/1": Q(1, 2),
        event + "/satellite/2": Q(1, 4),
        event + "/satellite/3": Q(1, 4),
    }
    c = [
        cs[node] if node in cs else float(Q(cs["source-s"]) * shares.get(node, 0))
        for node in target["live_node_ids"]
    ]
    w = [ws.get(e["edge_id"], 1.0) for e in target["edges"]]
    j = [js.get(e["edge_id"], 0.0) for e in target["edges"]]
    return {"authoritative": authority(c, w), "incoming_reference_current": j}


def build():
    shared = json.loads(
        (ROOT / (PHASE + "tranche-8/P9-8.0-COS-ConstructionInputs.json")).read_text()
    )
    source = graph_payload(
        shared["source_graph"]["nodes"], shared["source_graph"]["edges"]
    )
    paper = PaperAOS(source)
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
        "profile_family_id": "A_OS",
        "topology_dependent_map_policy_id": "initialize_target_W_A_over_complete_live_edge_set_v1",
        "geometry_reference_policy_id": "rebuild_reference_hodge_from_target_candidate_A_reference_v1",
    }
    history = history_policy(current, reset)
    request = {
        "schema_version": "grc9v4-expansion-event-request-input-v1",
        "operation_id": "native-aos-oracle-expand-1",
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
    target_ref, target_paper = reference(target), PaperAOS(target)
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
    negative_source = authority(current["C"], [0.99] * 9)
    negative_read = paper.step(negative_source["C"], negative_source["W_A"])
    negative_target = transfer(
        source, target, event, negative_source, negative_read["current"]
    )["authoritative"]
    record = {
        "schema": "p983a_aos_oracle_v1",
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
            "split_tolerance": SPLIT,
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
            "target_split": {
                "source_role": negative_source,
                "mapped_target_role": negative_target,
                "role_cases": ["current_only", "reset_only"],
                "identity_scope": "role_normalized_numerical_probe_recompute_all_native_event_identities_in_A2",
                "expected_stage": "target_readmission",
                "expected_disposition": "domain_failure",
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
    record["record_digest"] = digest(record)
    return record


def check_step(graph, c, w, observed):
    """Check against saved entry operands and the accepted interval equations."""
    c, w = tuple(c), tuple(w)
    model = StagedRows(graph["live_node_ids"], deepcopy(graph["edges"]), PARAMS)
    high = IntervalRows(model)
    exact_c, exact_w, stages = high.ordinary_os("A", vector(c), vector(w))
    for key, truth, limit in [
        ("C", exact_c, RESOURCE_ERROR),
        ("W_A", exact_w, HISTORY_ERROR),
        ("current", stages["read"]["J"], CURRENT_ERROR),
        ("baseline", stages["read"]["baseline"], CURRENT_ERROR),
        ("H", stages["H"], HISTORY_ERROR),
        ("regenerated", high.I + 0.5 * stages["read"]["source"], HISTORY_ERROR),
    ]:
        require(
            full_error(np.array(observed[key]).reshape(-1), IV.matrix(list(truth)))
            < limit,
            "entry-referenced " + key + " expectation failed",
        )
    require(
        stages["split_bound"] < Q(SPLIT)
        and stages["geometry_bound"] < Q(1, 2)
        and stages["read"]["regularity"] > Q(1, 2),
        "interval A_OS admission failed",
    )
    require(
        split_admitted(
            np.array(observed["H"]),
            np.array(observed["regenerated"]),
            model.I,
            Q(SPLIT),
        ),
        "represented split failed",
    )
    require(
        min(observed["C"]) >= 0 and min(observed["W_A"]) > 0, "output domain failed"
    )
    return float(stages["split_bound"])


def validate(record, expected=None, *, numerical=True, gates=True):
    if gates:
        require(
            A_G2 in admission.accepted(ROOT)["accepted_generic_runtime_support"],
            "A_OS G2 absent from accepted G3 consumed set",
        )
    expected = build() if expected is None else expected
    require(
        canonical_json_bytes(record) == canonical_json_bytes(expected),
        "oracle declaration/output drift (even if rehashed)",
    )
    if numerical:
        source, target = record["source"]["port_graph"], record["target"]["port_graph"]
        initial = record["initial"]["current"]
        check_step(source, initial["C"], initial["W_A"], record["source_step"])
        for role in ("current", "reset"):
            state = record["source"][role]
            check_step(
                source, state["C"], state["W_A"], record["source_reference_reads"][role]
            )
            state = record["target"]["roles"][role]["authoritative"]
            for row in record["continuation"][role]:
                result = row.get("final_read", row)
                check_step(target, state["C"], state["W_A"], result)
                if "final_read" not in row:
                    state = result
        check_negative(record)
    return record


def check_negative(record):
    """Prove a real target OS defect; an upper bound above tolerance is insufficient."""
    source, target = record["source"]["port_graph"], record["target"]["port_graph"]
    negative = record["rejection_expectations"]["target_split"]
    before, after = negative["source_role"], negative["mapped_target_role"]
    point = PaperAOS(source).step(before["C"], before["W_A"])
    check_step(source, before["C"], before["W_A"], point)
    model = StagedRows(target["live_node_ids"], deepcopy(target["edges"]), PARAMS)
    high = IntervalRows(model)
    cn, wn, stages = high.ordinary_os("A", vector(after["C"]), vector(after["W_A"]))
    defect = stages["H"] - high.I - stages["read"]["source"] / 2
    lower = max(max(endpoint(x, 0), -endpoint(x, 1), Q(0)) for x in defect)
    require(
        lower > Q(SPLIT),
        "target split failure not certified by an entry norm lower bound",
    )
    require(
        stages["read"]["regularity"] > Q(1, 2)
        and min(endpoint(x, 0) for x in cn) > 0
        and min(endpoint(x, 0) for x in wn) > 0,
        "negative target must retain regular current and positive updates",
    )
    point = PaperAOS(target).step(after["C"], after["W_A"])
    require(
        not split_admitted(
            np.array(point["H"]), np.array(point["regenerated"]), model.I, Q(SPLIT)
        ),
        "represented negative target did not reject",
    )
    return lower


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit",
        action="store_true",
        help="Write a newly reviewed oracle, never runtime output.",
    )
    args = parser.parse_args()
    expected = build()
    record = expected if args.emit else json.loads((ROOT / RECORD).read_text())
    validate(record, expected)
    if args.emit:
        (ROOT / RECORD).write_text(json.dumps(record, indent=2) + "\n")
    print(
        "P983A_AOS_ORACLE_PASS numerical_reads=25 physical_expectations=21 native_runtime_executed=false record_digest="
        + record["record_digest"]
    )


if __name__ == "__main__":
    main()
