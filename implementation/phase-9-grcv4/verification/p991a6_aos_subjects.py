"""Declared A_OS native inputs; research operands never advance the model."""

import json
from pathlib import Path

from p991a2_native_spark_numerics import subjects

from pygrc.models.grc_9_v4_completion_codec import CompletionPolicy
from pygrc.models.grc_9_v4_lifecycle import GRC9V4Specialization
from pygrc.models.grc_9_v4_spark_contracts import (
    GRC9V4SparkConfiguration,
    SparkReference,
)
from pygrc.models.grc_v4_codec import payload_identity
from pygrc.models.grc_v4_profile import (
    get_supported_profile,
    list_supported_profiles,
    resolve_profile,
)
from pygrc.models.grc_v4_spark_conductance import (
    AOS_NUMERICAL_POLICY,
    ExactConductanceState,
    QuarticAOSProfile,
    descriptor_identity,
)
from pygrc.models.grc_v4_spark_state import QuarticSite
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[3]


def profile(graph, **changes):
    old = next(
        p
        for p in map(get_supported_profile, sorted(list_supported_profiles()))
        if p.identity_payload.profile_family_id == "A_OS"
    )
    p, identity = old.params_resolved.to_payload(), old.identity_payload.to_payload()
    p["candidate"].update(
        eta=1 / 1024,
        kappa_c=1 / 64,
        kappa_Ah=1 / 64,
        chi_A=1 / 2,
        zeta_A=1 / 2,
        alpha=1 / 32768,
        beta=1 / 32768,
        gamma=1 / 32768,
        W_floor=1 / 2,
        tau_A=32,
        descriptor_backend_id=descriptor_identity(graph),
    )
    weights = {e: 1 for e in graph.live_edge_ids}
    m = len(weights)
    p["geometry"].update(
        kappa_H=1 / 2,
        K4_base_digest=payload_identity(
            "k4_identity_payload",
            {
                "schema_version": "grcv4-k4-identity-v1",
                "K4_base": [[0] * m for _ in range(m)],
            },
        ),
        reference_hodge_digest=payload_identity(
            "reference_hodge_identity_payload",
            {
                "schema_version": "grcv4-reference-hodge-identity-v1",
                "edge_weights": weights,
            },
        ),
    )
    p["realization"]["tolerance"] = 1e-11
    p["solver"].update(
        conditioning_limit=10**12, absolute_tolerance=1e-11, relative_tolerance=1e-11
    )
    for section, updates in changes.items():
        (identity if section == "identity" else p[section]).update(updates)
    identity["params_hash"] = payload_identity("resolved_params", p)
    return QuarticAOSProfile(
        resolve_profile(p, identity),
        QuarticSite(units_id="resource_potential_site_units_v1"),
    )


def configuration():
    _, graph, states, _ = subjects()
    vectors = json.loads((ROOT / "specs/grc-v4-conformance-vectors.json").read_bytes())
    declarations = {v["vector_id"]: v["payload"] for v in vectors["identity_vectors"]}
    params = declarations["IDENTITY-GRC9V4-PARAMS"]
    params["expansion"]["bond_seed"] = 1
    params["spark"].update(
        gradient_tolerance=4,
        spark_hessian_tolerance=1 / 8,
        basin_hessian_tolerance=1 / 4,
    )
    identity = declarations["IDENTITY-GRC9V4-SPECIALIZATION"]
    identity.update(
        hessian_sign=-1,
        specialization_params_hash=payload_identity("resolved_specialization", params),
    )
    spec = GRC9V4Specialization(
        FrozenJSONMap(params), FrozenJSONMap(identity)
    ).with_completion_policy(CompletionPolicy(numerical_policy_id=AOS_NUMERICAL_POLICY))
    return GRC9V4SparkConfiguration(
        SparkReference(graph, profile(graph)),
        spec,
        initial_conductance(states["current"], "current"),
        initial_conductance(states["reset"], "reset"),
    )


def initial_conductance(state, role):
    value = "4097/4096" if role == "current" else "8191/8192"
    return ExactConductanceState(
        state.graph, state.C, state.charge, (value,) * len(state.graph.live_edge_ids)
    )


def request(model, chirality=1):
    from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
    from pygrc.models.grc_9_v4_spark_conductance_event import history_policy
    from tests.models.test_grc_9_v4_spark_completion import request as base_request

    value = base_request(model, chirality).to_payload()
    value["resource_distribution"] = [1 / 128, 63 / 64, 1 / 128]
    value["history_policy"] = history_policy(model.configuration)
    return GRC9V4ExpansionRequestInput.from_payload(value)


def certificate_pair(model):
    import lzma

    from flint import arb, ctx
    from flint import fmpq as Q
    from flint import fmpq_mat as M

    from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
    from pygrc.models.grc_9_v4_spark_owner import kernel
    from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
    from pygrc.models.grc_v4_spark_cos import _rows
    from pygrc.models.grc_v4_spark_state import round_flux

    base = (
        ROOT
        / "implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability"
    )
    original = json.loads(lzma.decompress((base / "AOS-current.json.xz").read_bytes()))[
        "checks"
    ]
    proposal = json.loads(
        (base / "earlier-closure/AOSAnisotropicDomain.json").read_bytes()
    )
    graph = model.configuration.reference.graph
    event = model._operation._published.completion.event
    chi = str(model._operation._published.journal[-1]["request"]["module_chirality"])
    declared = original["targets"][chi]
    nodes = declared["graph"]["live_node_ids"]
    edges = declared["graph"]["edges"]
    mapping = dict(zip(nodes, nodes))
    mapping.update(zip(declared["module"], event["module"], strict=True))
    node_order = [
        next(i for i, x in enumerate(nodes) if mapping[x] == y)
        for y in graph.live_node_ids
    ]

    def signature(edge, rename):
        return frozenset(
            (rename[e["node_id"]], e["port"]) for e in (edge["tail"], edge["head"])
        )

    identity = {x: x for x in graph.live_node_ids}
    signatures = [signature(edge, mapping) for edge in edges]
    edge_order = [
        signatures.index(signature(edge, identity))
        for edge in graph.to_payload()["edges"]
    ]
    n, m = len(nodes), len(edges)
    d = n - 1 + m
    E = M(
        [
            [
                int(i == j)
                if i < n - 1
                else -int(j < n - 1)
                if i == n - 1
                else int(j == i - 1)
                for j in range(d)
            ]
            for i in range(n + m)
        ]
    )
    R = M(
        [
            [int(i == j) if i < n - 1 else int(j == i + 1) for j in range(n + m)]
            for i in range(d)
        ]
    )
    T = M([[Q(x) for x in row] for row in proposal["basis"]])
    radii = list(map(Q, proposal["axis_radii"]))
    D = M([[radii[i] if i == j else 0 for j in range(d)] for i in range(d)])
    S = E * T * D
    U = D.inv() * T.inv() * R
    order = node_order + [n + i for i in edge_order]
    S = M([[S[i, j] for j in range(d)] for i in order])
    U = M([[U[i, j] for j in order] for i in range(d)])
    proof = original["proof"]
    center = tuple(proof["center"][nodes[i]] for i in node_order)
    logs = tuple(proof["logW_center"][i] for i in edge_order)
    pair = tuple(
        CompletionCertificate.create_aos(
            kernel(model.configuration),
            model.configuration.policy,
            role,
            center,
            logs,
            _rows(S),
            _rows(U),
        )
        for role in ("current", "reset")
    )
    with _ARB_CONTEXT_LOCK, ctx.workprec(256):
        W = tuple(
            str(round_flux(arb(Q(x)).exp().mid().fmpq() * 2**64) / 2**64) for x in logs
        )
    state = ExactConductanceState(graph, center, "21", W)
    return pair, state
