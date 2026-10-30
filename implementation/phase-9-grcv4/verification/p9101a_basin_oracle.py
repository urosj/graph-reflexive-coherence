"""Independent small-graph and saved-state basin oracle; no production classifier.

Reachability closure differs from the producer's Kosaraju algorithm. Fixed-row
operands use Fraction, and native currents use the existing independent interval
equations on their explicitly checked parameter/graph domain.
"""

from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256

import numpy as np
from pygrc.models.grc_v4_codec import canonical_json_bytes


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def digest(value):
    return sha256(canonical_json_bytes(value)).hexdigest()


def typed(value):
    return {"kind": "int" if type(value) is int else "str", "value": value}


def key(value):
    return (0 if type(value) is int else 1, canonical_json_bytes(typed(value)))


def classification(witness, graph_digest):
    nodes = sorted((r["node"]["value"] for r in witness["rows"]), key=key)
    arcs = set()
    for edge in witness["edges"]:
        j = float.fromhex(edge["current"])
        u, v = edge["tail"]["value"], edge["head"]["value"]
        if j:
            arcs.add((u, v) if j > 0 else (v, u))
    reach = {(u, v): u == v or (u, v) in arcs for u in nodes for v in nodes}
    for k in nodes:
        for u in nodes:
            for v in nodes:
                reach[u, v] |= reach[u, k] and reach[k, v]
    parts = {tuple(v for v in nodes if reach[u, v] and reach[v, u]) for u in nodes}
    parts = sorted(parts, key=lambda s: tuple(map(key, s)))
    owner = {u: i for i, s in enumerate(parts) for u in s}
    components = []
    for i, s in enumerate(parts):
        cyclic = len(s) > 1 or (s[0], s[0]) in arcs
        terminal = not any(u in s and v not in s for u, v in arcs)
        incoming = any(v in s and u not in s for u, v in arcs)
        kind = (
            None
            if not terminal
            else "recirculating"
            if cyclic
            else "sink"
            if incoming
            else "quiescent"
        )
        components.append(
            dict(
                component_ref=i,
                members=list(map(typed, s)),
                cyclic=cyclic,
                is_terminal=terminal,
                terminal_kind=kind,
            )
        )
    rows = {r["node"]["value"]: r for r in witness["rows"]}
    records, regions = [], {}
    for u in nodes:
        ends = [
            i
            for i, s in enumerate(parts)
            if components[i]["is_terminal"] and reach[u, s[0]]
        ]
        status = "ambiguous" if len(ends) > 1 else components[ends[0]]["terminal_kind"]
        sink = parts[ends[0]][0] if status == "sink" else None
        g = tuple(Q(float.fromhex(x)) for x in rows[u]["gradient"])
        h = tuple(Q(float.fromhex(x)) for x in rows[u]["signed_hessian_diagonal"])
        seed = sum(x * x for x in g) < Q(
            float.fromhex(witness["gradient_tolerance"])
        ) ** 2 and min(h) > Q(float.fromhex(witness["hessian_tolerance"]))
        label = (
            None
            if sink is None
            else "grc9v4-flow-basin-sha256:"
            + digest(
                dict(
                    policy_id="grc9v4-terminal-flow-regions-v1",
                    graph_digest=graph_digest,
                    sink_node_id=typed(sink),
                )
            )
        )
        records.append(
            dict(
                node=typed(u),
                component_ref=owner[u],
                reachable_terminals=ends,
                status=status,
                assigned_sink=None if sink is None else typed(sink),
                basin_id=label,
                seed=seed,
            )
        )
        if sink is not None:
            r = regions.setdefault(
                sink,
                dict(
                    sink_node_id=typed(sink),
                    basin_id=label,
                    members=[],
                    seed_members=[],
                ),
            )
            r["members"].append(typed(u))
            if seed:
                r["seed_members"].append(typed(u))
    return dict(
        components=components,
        nodes=records,
        regions=[regions[n] for n in sorted(regions, key=key)],
    )


def compare_classification(value):
    expected = classification(value["witness"], value["binding"]["graph_digest"])
    for field in expected:
        require(value[field] == expected[field], "independent classification: " + field)
    return [
        dict(node=n["node"], basin_id=n["basin_id"])
        for n in expected["nodes"]
        if n["basin_id"] is not None
    ]


def row_witness(saved, role, values):
    ref = saved.inputs.geometry.reference
    graph = ref.graph.port_graph
    authority = getattr(saved.inputs, role)
    resources = dict(zip(graph.live_node_ids, map(Q, authority.C), strict=True))
    weights = authority.W_A or tuple(
        ref.profile.params_resolved.candidate.W_C_tr[e.edge_id] for e in graph.edges
    )
    rows = {n: [[] for _ in range(3)] for n in graph.live_node_ids}
    for e, w, j in zip(graph.edges, weights, values, strict=True):
        for here, other, sign in ((e.tail, e.head, 1), (e.head, e.tail, -1)):
            rows[here.node_id][(here.port - 1) // 3].append(
                (Q(w), resources[other.node_id] - resources[here.node_id], sign * Q(j))
            )
    sign = saved.specialization.identity_payload["hessian_sign"]
    output = []
    for n in sorted(rows, key=key):
        g = []
        flux = []
        for row in rows[n]:
            denominator = sum((w for w, _, _ in row), Q())
            g.append(
                float(sum((w * d for w, d, _ in row), Q()) / denominator)
                if denominator
                else 0.0
            )
            flux.append(float(sum((j for _, _, j in row), Q())))
        output.append(
            dict(
                node=typed(n),
                gradient=[x.hex() for x in g],
                signed_hessian_diagonal=[float(sign * Q(x)).hex() for x in g],
                row_net_flux=[x.hex() for x in flux],
            )
        )
    return output


def root_payload(read, point):
    values = point.current.values
    root = dict(
        recipe=point.to_payload(),
        current=[float(j).hex() for j in values],
        H1_form=[
            [float(x).hex() for x in r]
            for r in point.inputs.geometry.one_form_hodge.matrix
        ],
    )
    certificate = None
    real = point.inputs.geometry.reference.profile.identity_payload.realization
    if real == "CI":
        selected = read.selected
        require(
            selected.point is point and selected.inputs == point.inputs,
            "native joint root ownership",
        )
        root.update(
            recipe=read.to_payload(),
            evaluations=read.evaluations,
            selected_inputs=selected.inputs.to_payload(),
            generated_H1=[
                [float(x).hex() for x in r]
                for r in selected.generated.one_form_hodge.matrix
            ],
            residual_squared=str(
                sum(
                    (
                        Q(str(x.magnitude)) ** 2
                        for x in selected.analytic_current_residual
                    ),
                    Q(),
                )
                + sum(
                    (
                        Q(str(x.magnitude)) ** 2
                        for row in selected.analytic_geometry_residual
                        for x in row
                    ),
                    Q(),
                )
            ),
            certificate=read.certificate.bounds.to_dict(),
        )
        certificate = "grc9v4-basin-joint-root-sha256:" + digest(root)
    elif real == "PC":
        root["certificate"] = read.certificate.bounds.to_dict()
        certificate = "grc9v4-basin-pc-read-sha256:" + digest(root)
    return root, certificate


def captured_inputs(saved, role, value, read, point):
    """Compare output with immutable state saved BEFORE invoking the producer."""
    ref = saved.inputs.geometry.reference
    graph = ref.graph.port_graph
    authority = getattr(saved.inputs, role)
    require(
        read.inputs.current == authority and point.inputs.current == authority,
        "native role/state input",
    )
    require(
        read.inputs.context == saved.inputs.context
        and read.inputs.geometry.reference == ref,
        "native context/profile input",
    )
    require(
        read.inputs.dt == 0 and read.inputs.stage == "pre_read", "native read stage"
    )
    values = point.current.values
    expected_edges = [
        dict(
            edge_id=e.edge_id,
            tail=typed(e.tail.node_id),
            head=typed(e.head.node_id),
            current=float(j).hex(),
        )
        for e, j in zip(graph.edges, values, strict=True)
    ]
    require(value["witness"]["edges"] == expected_edges, "native edge witness")
    expected_rows = row_witness(saved, role, values)
    require(value["witness"]["rows"] == expected_rows, "native row witness")
    spark = saved.specialization.resolved["spark"]
    for field, param in (
        ("gradient_tolerance", "gradient_tolerance"),
        ("hessian_tolerance", "basin_hessian_tolerance"),
    ):
        require(
            value["witness"][field] == float(spark[param]).hex(),
            "native seed threshold",
        )
    require(
        value["witness"]["hessian_sign"]
        == saved.specialization.identity_payload["hessian_sign"],
        "native Hessian sign",
    )
    root, certificate = root_payload(read, point)
    from pygrc.models.grc_v4_codec import RELEASE_ID

    expected = dict(
        role=role,
        role_state_digest=digest(
            saved.scientific_payload if role == "current" else saved.reset_payload
        ),
        profile_id=ref.profile.complete_profile_id,
        model_identity=saved.model_identity,
        graph_digest=graph.graph_digest,
        orientation_identity=graph.orientation_identity,
        context_contract_id=saved.inputs.context.contract_id,
        context_value_digest=digest(saved.inputs.context.value.to_dict()),
        numerical_policy_id="legacy_exact_v1",
        scalar_backend_id="flint",
        evaluator_id="grc9v4-native-fresh-basin-capture-v1",
        release_id=RELEASE_ID,
        stage="fresh_poststate_readmission",
        root_certificate_binding=certificate,
        read_identity="grc9v4-basin-read-sha256:" + digest(root),
    )
    require(value["binding"] == expected, "native full capture binding")
    require(
        value["operand_digest"] == digest(value["witness"]), "native operand digest"
    )
    require(
        value["observation_digest"]
        == digest(
            {
                k: value[k]
                for k in ("schema_version", "policy_id", "binding", "operand_digest")
            }
        ),
        "native observation digest",
    )
    return compare_classification(value)


def equation_check(saved, role, point):
    """Independent interval current/geometry equations on the pinned small chart.

    Full current error here is at the captured represented geometry. CI's joint
    geometry residual is reported separately; no exact-root sign certification
    is inferred from a current-only bound.
    """
    from test_p980_os_effect_witness import (
        IV,
        PARAMS,
        IntervalRows,
        number,
        vector,
        full_error,
        infinity,
        endpoint,
        inverse,
    )
    from test_p980_os_numerical_feasibility import StagedRows

    ref = saved.inputs.geometry.reference
    profile = ref.profile
    cp = profile.params_resolved.candidate
    gp = profile.params_resolved.geometry
    graph = ref.graph.port_graph
    authority = getattr(saved.inputs, role)
    href = IV.diag([number(ref.edge_weights[e.edge_id]) for e in graph.edges])
    require(
        ref.geometry().one_form_hodge.matrix
        == tuple(
            tuple(float(href[i, j].mid) for j in range(len(graph.edges)))
            for i in range(len(graph.edges))
        ),
        "diagonal reference H",
    )
    if profile.identity_payload.candidate == "A":
        require(all(x == 1 for x in ref.edge_weights.values()), "A reference H=I")
    require(all(x == 0 for row in ref.K4_base for x in row), "interval K base")
    if profile.identity_payload.candidate == "C":
        require(
            cp.kappa_M_C == 2**-24
            and cp.chi_C == 16
            and cp.zeta_C == (2**-30 if profile.identity_payload.profile_family_id == "C_PC" else 2**-37)
            and cp.tau_C == cp.eta_C == cp.kappa_Phi_C == cp.C_ref == 1
            and cp.Lambda_C == 1 / 512
            and all(v > 0 for v in cp.W_C_tr.values()),
            "pinned C equation parameters",
        )
    else:
        require(
            cp.alpha == cp.beta == cp.gamma == 2**-24
            and cp.eta == cp.kappa_c == 1
            and cp.kappa_Ah == cp.zeta_A == cp.W_floor == 0.5
            and cp.chi_A == 1 / 16,
            "pinned A equation parameters",
        )
    model = StagedRows(
        graph.live_node_ids, [e.to_payload() for e in graph.edges],
        replace(PARAMS, zeta_c=Q(cp.zeta_C)) if profile.identity_payload.candidate == "C" else PARAMS
    )
    high = IntervalRows(model)
    c = vector(authority.C)
    w = None if authority.W_A is None else vector(authority.W_A)
    h = IV.matrix([list(row) for row in point.inputs.geometry.one_form_hodge.matrix])
    if profile.identity_payload.candidate == "C":
        # Connected unweighted Laplacian: lambda_2 >= 4/(n*diameter) >=
        # 4/(n*(n-1)). H within 1/2 of I preserves the constant-only selector.
        reached = {graph.live_node_ids[0]}
        for _ in graph.live_node_ids:
            for e in graph.edges:
                if e.tail.node_id in reached or e.head.node_id in reached:
                    reached.update((e.tail.node_id, e.head.node_id))
        n = len(reached)
        require(
            n == len(graph.live_node_ids)
            and infinity(h - high.I) < Q(1, 2)
            and Q(2, n * (n - 1)) > Q(cp.Lambda_C),
            "constant-selector interval gap",
        )
    truth = high.read(profile.identity_payload.candidate, c, w, h)
    if profile.identity_payload.candidate == "C" and any(
        v != 1 for v in cp.W_C_tr.values()
    ):
        # Same constant-sector law, with the independently specified stable-edge
        # mobility map. Neither H nor the modulation scalar supplies these weights.
        exp = IV.exp(2 * sum(c) / len(c))
        t = IV.exp(number(cp.kappa_M_C) * (exp - 1) / (exp + 1))
        mobility = IV.diag([number(cp.W_C_tr[e.edge_id]) for e in graph.edges])
        baseline = -mobility * high.B.T * high.B * (t * h) * high.B.T * c
        response = inverse(high.I + t * h * high.D)
        current = inverse(high.I - number(cp.zeta_C * cp.chi_C) * response) * baseline
        flat = inverse(h) * (number(cp.chi_C) * response * current)
        source = IV.matrix(
            [
                [
                    number(cp.zeta_C) * number(high.mask[i, k]) * flat[i] * flat[k]
                    for k in range(len(flat))
                ]
                for i in range(len(flat))
            ]
        )
        truth.update(J=current, baseline=baseline, source=source)
    error = full_error(point.current.values, truth["J"])
    require(error < Q(1, 2**40), "independent current equation")
    real = profile.identity_payload.realization
    base = href
    if real == "PC":
        base = base + number(gp.kappa_H) * IV.matrix(
            np.array(authority.Z_4).reshape(len(graph.edges), -1).tolist()
        )
    image = base + number(gp.kappa_H) * truth["source"] if real == "CI" else base
    residual = infinity(h - image)
    limit = (
        Q(profile.params_resolved.realization.tolerance)
        if real == "CI"
        else Q(1, 2**48)
    )
    require(residual < limit, "independent geometry equation")
    signs = sum(abs(Q(j)) > error for j in point.current.values)
    result = dict(
        current_error_upper=str(error),
        geometry_residual_upper=str(residual),
        represented_nonzero=sum(j != 0 for j in point.current.values),
        certified_fixed_geometry_signs=signs,
        exact_root_signs_claimed=False,
    )
    if profile.identity_payload.candidate == "A":
        drive = high.conductance(c, w, truth["baseline"])
        q = [(x - g) / (x + g) for x, g in zip(w, drive, strict=True)]
        margin = min(endpoint(1 - number(cp.zeta_A * cp.chi_A) * x, 0) for x in q)
        require(margin > 0, "A positive denominator")
        result.update(
            positive_denominator_lower=str(margin),
            exact_fixed_geometry_cycle_exclusion=True,
        )
    return result
