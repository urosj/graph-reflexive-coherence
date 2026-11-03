"""Declared C_PC native inputs; no saved target advances the public model."""

import json
from pathlib import Path

from p991a2_native_spark_numerics import profile as cos_profile
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
from pygrc.models.grc_v4_spark_carrier import ExactCarrierState
from pygrc.models.grc_v4_spark_cpc import SOURCE_ENVELOPE
from pygrc.models.grc_v4_spark_state import (
    PC_NUMERICAL_POLICY,
    QuarticCPCProfile,
    QuarticSite,
)
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[3]


def profile(graph, **changes):
    predecessor = next(
        p
        for p in map(get_supported_profile, sorted(list_supported_profiles()))
        if p.identity_payload.profile_family_id == "C_PC"
    )
    p = cos_profile(graph).baseline.params_resolved.to_payload()
    identity = predecessor.identity_payload.to_payload()
    p["realization"] = predecessor.params_resolved.realization.to_payload()
    p["realization"].update(
        tau_PC=32, radius=1 / 64, source_envelope_id=SOURCE_ENVELOPE
    )
    p["solver"] = predecessor.params_resolved.solver.to_payload()
    p["solver"].update(iteration_limit=60, conditioning_limit=10**12)
    for section, updates in changes.items():
        (identity if section == "identity" else p[section]).update(updates)
    identity["params_hash"] = payload_identity("resolved_params", p)
    return QuarticCPCProfile(
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
    ).with_completion_policy(CompletionPolicy(numerical_policy_id=PC_NUMERICAL_POLICY))
    return GRC9V4SparkConfiguration(
        SparkReference(graph, profile(graph)),
        spec,
        initial_carrier(states["current"], "current"),
        initial_carrier(states["reset"], "reset"),
    )


def initial_carrier(state, role):
    m = len(state.graph.oriented_edges)
    value = "1/65536" if role == "current" else "-1/131072"
    return ExactCarrierState(
        state.graph,
        state.C,
        state.charge,
        tuple(tuple(value if i == j else "0" for j in range(m)) for i in range(m)),
    )


def request(model, chirality=1):
    from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
    from pygrc.models.grc_9_v4_spark_carrier_event import history_policy
    from tests.models.test_grc_9_v4_spark_completion import request as base_request

    value = base_request(model, chirality).to_payload()
    value["history_policy"] = history_policy(model.configuration)
    return GRC9V4ExpansionRequestInput.from_payload(value)


def certificate_pair(model):
    from flint import fmpq as Q
    from flint import fmpq_mat as M

    from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
    from pygrc.models.grc_9_v4_spark_owner import kernel
    from pygrc.models.grc_v4_spark_cos import _rows
    from pygrc.models.grc_v4_spark_state import ExactResources

    _, _, _, domain = subjects()
    config = model.configuration
    graph = config.reference.graph
    nodes = domain["graphs"]["1"]["live_node_ids"]
    event = model._operation._published.completion.event
    mapping = {x: x for x in nodes}
    for old, new in zip(
        (
            "sc2-positive-module/core",
            *["sc2-positive-module/satellite/" + str(i) for i in (1, 2, 3)],
        ),
        event["module"],
    ):
        mapping[old] = new
    order = [
        next(i for i, x in enumerate(nodes) if mapping[x] == y)
        for y in graph.live_node_ids
    ]
    n, d = len(nodes), len(nodes) - 1
    T = M([[Q(x) for x in row] for row in domain["basis"]])
    radii = list(map(Q, domain["axis_radii"]))
    D = M([[radii[i] if i == j else 0 for j in range(d)] for i in range(d)])
    S = M([[int(i == j) if i < d else -1 for j in range(d)] for i in range(n)]) * T * D
    U = D.inv() * T.inv() * M([[int(i == j) for j in range(n)] for i in range(d)])
    S, U = (
        M([[S[i, j] for j in range(d)] for i in order]),
        M([[U[i, j] for j in order] for i in range(d)]),
    )
    center = ExactCarrierState.zero(
        ExactResources(graph, tuple(domain["center"][nodes[i]] for i in order), "21")
    )
    pair = tuple(
        CompletionCertificate.create(
            kernel(config), config.policy, role, center, _rows(S), _rows(U)
        )
        for role in ("current", "reset")
    )
    return pair, center
