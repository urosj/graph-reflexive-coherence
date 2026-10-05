"""Independent C_CI+PC equations, compact-chart proof and native observations.

The native fixture is distinct from the accepted small local P9-8.0 chart.
No native current/root/certificate/writer supplies independent expected values.
"""

from __future__ import annotations

import sys
from fractions import Fraction as Q
from pathlib import Path

import numpy as np
from mpmath.ctx_mp import MPContext

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT, ROOT / "src", Path(__file__).resolve().parent):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from test_p980_os_effect_witness import (
    IV,
    IntervalRows,
    endpoint,
    full_error,
    infinity,
    inverse,
    number,
    upper_abs,
    vector,
)
from test_p980_os_numerical_feasibility import ResearchParameters, StagedRows

DT = 2**-12
RADIUS = 1
KAPPA = 2**-16
ROOT_RADIUS = 2**-15
TOLERANCE = 2**-44
RESOURCE_RADIUS = 16
ZETA = 2**-30
CHI = 16
MODULATION = 2**-24
CUTOFF = 2**-9
CURRENT_ERROR = RESOURCE_ERROR = Q(1, 2**40)
GEOMETRY_ERROR = Q(1, 2**48)
CARRIER_ERROR = Q(1, 2**48)
SOURCE_ERROR = Q(1, 2**52)


def require(value, message):
    if not value:
        raise ValueError(message)


def model(graph):
    ends = [
        frozenset((e["tail"]["node_id"], e["head"]["node_id"])) for e in graph["edges"]
    ]
    require(
        len(ends) == len(graph["live_node_ids"]) - 1
        and all(len(pair) == 2 for pair in ends)
        and len(set(ends)) == len(ends),
        "independent companion is scoped to simple source/target trees",
    )
    return StagedRows(
        graph["live_node_ids"],
        graph["edges"],
        ResearchParameters(coefficient=Q(MODULATION), chi_c=Q(CHI), zeta_c=Q(ZETA)),
    )


def sqrt_upper(x):
    return endpoint(IV.sqrt(number(x)), 1)


def norm_upper(matrix):
    return sqrt_upper(sum(upper_abs(x) ** 2 for x in matrix))


def chart(
    graph,
    *,
    radius=Q(RADIUS),
    geometry_radius=Q(ROOT_RADIUS),
    resource=Q(RESOURCE_RADIUS),
):
    """Independent constant-sector proof over every declared C and Z.

    Exact connected Laplacian + constant projector proves a nonzero gap.
    The selected sector is therefore the fixed constant vector throughout the
    Hodge ball. Its mean-C modulation is independent of trial geometry.
    Similarity to an SPD resolvent gives ||R||2 <= sqrt(u/l), avoiding the
    generic projector-Lipschitz certificate used in production.
    """
    high = IntervalRows(model(graph))
    n, m = len(high.nodes), len(high.edges)
    lap = high.B * high.B.T
    inv = inverse(
        lap + IV.matrix([[number(Q(1, n)) for _ in range(n)] for _ in range(n)])
    )
    gap = 1 / infinity(inv)
    lower, upper = 1 - geometry_radius, 1 + geometry_radius
    require(
        lower > 0 and lower * gap > Q(CUTOFF), "constant selector stratum not certified"
    )
    require(geometry_radius >= 2 * Q(KAPPA) * radius, "composite domain misses B_2R")
    b2 = infinity(high.D)
    b = sqrt_upper(b2)
    t = endpoint(IV.exp(number(MODULATION)), 1)
    response = sqrt_upper(upper / lower)
    response_lip = response**2 * t * b2
    margin = 1 - Q(ZETA) * CHI * response
    require(margin > 0, "whole-chart current inverse not certified")
    baseline = b2 * t * upper * b * resource
    baseline_lip = b2 * t * b * resource
    current = baseline / margin
    current_lip = (
        baseline_lip / margin + baseline * Q(ZETA) * CHI * response_lip / margin**2
    )
    flat = CHI * response * current / lower
    flat_lip = CHI * (
        response * current / lower**2
        + (response_lip * current + response * current_lip) / lower
    )
    source = Q(ZETA) * flat**2
    contraction = 2 * Q(KAPPA) * Q(ZETA) * flat * flat_lip
    displacement = Q(KAPPA) * (radius + source)
    require(source < radius, "strict uniform source slack missing")
    require(
        displacement <= geometry_radius and contraction < 1,
        "composite root not certified",
    )
    return {
        "reference_gap_lower": gap,
        "selector_gap_lower": lower * gap - Q(CUTOFF),
        "hodge_lower": lower,
        "hodge_upper": upper,
        "current_margin_lower": margin,
        "current_upper": current,
        "source_upper": source,
        "contraction_upper": contraction,
        "displacement_upper": displacement,
        "source_slack": radius - source,
        "root_radius": geometry_radius,
        "carrier_radius": radius,
        "dimension": m,
    }


def admitted(graph, c, z):
    high = IntervalRows(model(graph))
    m = len(high.edges)
    z = np.asarray(z, dtype=float).reshape(m, m)
    require(
        np.all(np.isfinite(z)) and np.array_equal(z, z.T),
        "carrier symmetry/finite mismatch",
    )
    require(np.all(z[high.mask == 0] == 0), "carrier star support mismatch")
    require(sum(Q(float(x)) ** 2 for x in z.flat) <= RADIUS**2, "carrier ball exceeded")
    require(
        all(np.isfinite(x) and x >= 0 for x in c)
        and sum(Q(float(x)) ** 2 for x in c) <= RESOURCE_RADIUS**2,
        "resource chart exceeded",
    )
    return high, vector(c), IV.matrix(z.tolist())


def interval_root(
    graph,
    c,
    z,
    h,
    *,
    instant=True,
    feedback=True,
    modulation=True,
    root_error_limit=GEOMETRY_ERROR,
):
    high, ci, zi = admitted(graph, c, z)
    cert = chart(graph)
    hp = IV.matrix(np.asarray(h).tolist())
    require(
        norm_upper(hp - high.I) <= ROOT_RADIUS, "root candidate outside geometry ball"
    )
    read = high.read("C", ci, None, hp, feedback=feedback, modulation=modulation)
    image = high.I + number(KAPPA) * (
        zi + (read["source"] if instant else IV.matrix(hp.rows))
    )
    q = cert["contraction_upper"] if instant else Q(0)
    residual = norm_upper(hp - image)
    error = residual / (1 - q)
    require(error < root_error_limit, "full root error budget unresolved")
    padding = q * error
    enclosed = IV.matrix(
        [
            [
                IV.mpf(
                    [
                        (image[i, j] - number(padding)).a,
                        (image[i, j] + number(padding)).b,
                    ]
                )
                if high.mask[i, j]
                else number(0)
                for j in range(hp.cols)
            ]
            for i in range(hp.rows)
        ]
    )
    truth = high.read("C", ci, None, enclosed, feedback=feedback, modulation=modulation)
    return {
        "high": high,
        "c": ci,
        "z": zi,
        "H": enclosed,
        "read": truth,
        "certificate": cert,
        "residual_upper": residual,
        "root_error_upper": error,
    }


def independent_root(graph, c, z, *, instant=True, feedback=True, modulation=True):
    """Separate 80-digit literal fixed point, never a native solver seed."""
    rows = model(graph)
    mp = MPContext()
    mp.dps = 80
    b = mp.matrix(rows.B.tolist())
    d = b.T * b
    ident = mp.eye(len(rows.edges))
    cc = mp.matrix(list(c))
    zz = mp.matrix(np.asarray(z).reshape(d.rows, d.cols).tolist())
    t = (
        mp.exp(mp.mpf(MODULATION) * mp.tanh(sum(cc) / len(cc)))
        if modulation
        else mp.mpf(1)
    )

    def read(h):
        baseline = -d * t * h * b.T * cc
        response = (ident + t * h * d) ** -1
        j = (
            (ident - mp.mpf(ZETA) * CHI * response) ** -1 * baseline
            if feedback
            else baseline
        )
        flat = h**-1 * (CHI * response * j) if feedback else mp.matrix(d.rows, 1)
        source = mp.matrix(
            [
                [
                    mp.mpf(ZETA) * mp.mpf(float(rows.mask[i, k])) * flat[i] * flat[k]
                    for k in range(d.cols)
                ]
                for i in range(d.rows)
            ]
        )
        return j, baseline, source

    h = ident.copy()
    for _ in range(100):
        j, base, source = read(h)
        following = ident + mp.mpf(KAPPA) * (
            zz + (source if instant else mp.matrix(d.rows))
        )
        if max(abs(x) for x in following - h) < mp.mpf("1e-65"):
            h = following
            j, base, source = read(h)
            return {
                "H": np.array(h.tolist(), dtype=float),
                "J": np.array(list(j), dtype=float),
                "baseline": np.array(list(base), dtype=float),
                "source": np.array(source.tolist(), dtype=float),
            }
        h = following
    raise ValueError("independent root did not converge")


def certify(
    graph,
    c,
    z,
    observed,
    *,
    instant=True,
    feedback=True,
    modulation=True,
    root_error_limit=GEOMETRY_ERROR,
):
    truth = interval_root(
        graph,
        c,
        z,
        observed["H"],
        instant=instant,
        feedback=feedback,
        modulation=modulation,
        root_error_limit=root_error_limit,
    )
    errors = {
        k: full_error(
            np.asarray(observed[k]).reshape(-1), IV.matrix(list(truth["read"][k]))
        )
        for k in ("J", "baseline", "source")
    }
    require(
        max(errors["J"], errors["baseline"]) < CURRENT_ERROR,
        "full current error budget unresolved",
    )
    require(errors["source"] < SOURCE_ERROR, "full source error budget unresolved")
    truth["errors"] = errors
    return truth


def step_truth(truth):
    after = truth["c"] - number(DT) * truth["high"].B * truth["read"]["J"]
    decay = IV.exp(-number(DT))
    z = decay * truth["z"] + (1 - decay) * truth["read"]["source"]
    return after, z


def provenance():
    side = (
        ROOT
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
    )
    if str(side / "tool/src") not in sys.path:
        sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.forensic import contract_provenance
    from grcv4_explorer.successor import load_successor_forensic_context

    context = load_successor_forensic_context(ROOT, side)
    result = []
    for identifier in (
        "D11-G9-EC-LIFECYCLE-READMISSION",
        "D11-G9-EC-FIXED-BOND-SEED",
        "D11-C-EC-C-J0-LIFECYCLE",
        "D10.2-EC-PARENT-REAL-CI",
        "D10.2-EC-PARENT-REAL-PC",
        "D10.2-EC-PARENT-REAL-CI-PC",
        "D10.2-EC-PARENT-L-ATOMICITY",
    ):
        trace = contract_provenance(context, identifier)
        require(trace["row_count"] == 1, "ambiguous contract provenance")
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


def observations():
    import hashlib
    import importlib.util
    import json
    from dataclasses import replace

    from tests.models.test_grc_9_v4_ccipc import (
        ExactBackend,
        GRC9V4CCIPCOperation,
        GRCV4AuthoritativeState,
        ResourceBoundaryError,
        ci,
        exact_backend,
        fixture,
        native_effects,
        outputs,
    )
    from tests.models.test_grc_9_v4_ccipc import (
        certify as native_certify,
    )

    kind = (
        ExactBackend.FLINT if importlib.util.find_spec("flint") else ExactBackend.PYTHON
    )
    with exact_backend(kind):
        seed, request, initial = fixture()
        owner = GRC9V4CCIPCOperation(seed)
        outcome = owner.expand(request)
        require(outcome.committed, str(outcome.failure))
        roots = []
        for label, state in (("source", seed), ("target", owner.state)):
            for role in ("current", "reset"):
                inputs = replace(state.inputs, current=getattr(state.inputs, role))
                root = ci.CandidateCIRoot(inputs)
                truth = native_certify(inputs, root)
                graph = inputs.geometry.reference.graph.port_graph.to_payload()
                independent = independent_root(
                    graph, inputs.current.C, inputs.current.Z_4
                )
                certify(graph, inputs.current.C, inputs.current.Z_4, independent)
                roots.append(
                    {
                        "graph": label,
                        "role": role,
                        "evaluations": root.evaluations,
                        "native_certificate": root.certificate.bounds.to_dict(),
                        "independent_certificate": {
                            k: str(v) for k, v in truth["certificate"].items()
                        },
                        "full_error_upper": {
                            k: str(v) for k, v in truth["errors"].items()
                        },
                        "root_error_upper": str(truth["root_error_upper"]),
                        "native_output": {
                            k: v.tolist() for k, v in outputs(root).items()
                        },
                        "independent_80_digit_root": {
                            k: v.tolist() for k, v in independent.items()
                        },
                    }
                )
        beats = []
        starts = [("source", "current", initial, 1)] + [
            (
                "target",
                role,
                replace(
                    owner.state.inputs, current=getattr(owner.state.inputs, role), dt=DT
                ),
                10,
            )
            for role in ("current", "reset")
        ]
        for label, role, inputs, count in starts:
            for index in range(count):
                step = ci.ProvisionalCandidateCIStep(inputs)
                truth = native_certify(inputs, step.root)
                cn, zn = step_truth(truth)
                ce = full_error(step.next_inputs.current.C, cn)
                ze = full_error(step.next_inputs.current.Z_4, IV.matrix(list(zn)))
                require(
                    ce < RESOURCE_ERROR and ze < CARRIER_ERROR, "physical step mismatch"
                )
                beats.append(
                    {
                        "graph": label,
                        "role": role,
                        "beat": index + 1,
                        "resource_full_error_upper": str(ce),
                        "carrier_full_error_upper": str(ze),
                        "root_error_upper": str(truth["root_error_upper"]),
                        "root_evaluations": step.root.evaluations,
                        "source_full_error_upper": str(truth["errors"]["source"]),
                        "current_full_error_upper": str(truth["errors"]["J"]),
                        "minimum_next_C": min(step.next_inputs.current.C),
                    }
                )
                if label == "source":
                    require(
                        step.next_inputs.current == seed.inputs.current,
                        "actual source stage differs",
                    )
                    archived = owner.carrier_archives[0]["history_content"]["content"]
                    require(
                        tuple(archived)
                        == step.next_inputs.current.Z_4 + step.next_inputs.reset.Z_4,
                        "archive is not exact physical stage",
                    )
                inputs = step.next_inputs
        negatives = []
        for shares in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
            receiver = GRC9V4CCIPCOperation(seed)
            event = receiver.expand(replace(request, resource_distribution=shares))
            require(event.committed, str(event.failure))
            before = receiver.checkpoint()
            for role in ("current", "reset"):
                inputs = replace(
                    receiver.state.inputs,
                    current=getattr(receiver.state.inputs, role),
                    dt=DT,
                )
                root = ci.CandidateCIRoot(inputs)
                truth = native_certify(inputs, root)
                cn, _ = step_truth(truth)
                upper = min(endpoint(v, 1) for v in cn)
                require(upper < 0, "negative continuation is not certified")
                try:
                    ci.ProvisionalCandidateCIStep(inputs)
                except ResourceBoundaryError as error:
                    stage = error.stage
                else:
                    raise ValueError("negative continuation accepted")
                require(
                    stage == "charge_admission" and receiver.checkpoint() == before,
                    "negative step altered event owner",
                )
                negatives.append(
                    {
                        "shares": list(shares),
                        "role": role,
                        "event_committed": True,
                        "independent_negative_C_upper": str(upper),
                        "physical_step_failure_stage": stage,
                        "unchanged_checkpoint_sha256": hashlib.sha256(
                            before
                        ).hexdigest(),
                    }
                )
        outliers = []
        for label, state in (("source", seed), ("target", owner.state)):
            inputs = state.inputs
            graph = inputs.geometry.reference.graph.port_graph.to_payload()
            for index, sign in ((0, 1), (len(inputs.current.C) - 1, -1)):
                c = [0.0] * len(inputs.current.C)
                c[index] = float(RESOURCE_RADIUS)
                z = [0.0] * len(inputs.current.Z_4)
                z[0] = float(sign)
                changed = replace(
                    inputs, current=GRCV4AuthoritativeState(tuple(c), None, tuple(z))
                )
                root = ci.CandidateCIRoot(changed)
                truth = certify(
                    graph, c, z, outputs(root), root_error_limit=Q(TOLERANCE)
                )
                outliers.append(
                    {
                        "graph": label,
                        "resource_vertex_index": index,
                        "resource_vertex_value": RESOURCE_RADIUS,
                        "carrier_diagonal_entry": sign,
                        "evaluations": root.evaluations,
                        "root_error_upper": str(truth["root_error_upper"]),
                        "root_error_limit": str(Q(TOLERANCE)),
                        "meets_nominal_tighter_geometry_budget": truth[
                            "root_error_upper"
                        ]
                        < GEOMETRY_ERROR,
                        "full_error_upper": {
                            k: str(v) for k, v in truth["errors"].items()
                        },
                    }
                )
        effects = native_effects(seed, owner.state)
        return {
            "schema": "p983ccipc_native_observations_v1",
            "result": "P983CCIPC_NATIVE_PASS",
            "backend": str(kind),
            "domain": {
                "carrier_norm": "frobenius",
                "carrier_radius": RADIUS,
                "geometry_radius": ROOT_RADIUS,
                "kappa_H": KAPPA,
                "base_resource_radius": RESOURCE_RADIUS,
                "W_C_tr": "unit",
                "zeta_C": ZETA,
                "tolerance": TOLERANCE,
                "iteration_limit": 60,
            },
            "initial_inputs": initial.to_payload(),
            "request": request.to_payload(),
            "checkpoint": json.loads(owner.checkpoint()),
            "roots": roots,
            "beats": beats,
            "exact_source_archive_stage": True,
            "certified_negative_continuations": negatives,
            "whole_chart_outliers": outliers,
            "native_effects": effects,
            "minimum_effect_margin": min(e["minimum_margin_ratio"] for e in effects),
            "side_tool_provenance": provenance(),
            "scope": "bounded native C_CI+PC event and finite continuation, no global stability or new public profile",
        }


if __name__ == "__main__":
    import json

    print(json.dumps(observations(), indent=2))
