"""Declared A_RG2b native inputs; research operands never advance the model."""

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
    ARG2B_NUMERICAL_POLICY,
    ExactConductanceState,
    QuarticARG2bProfile,
    descriptor_identity,
)
from pygrc.models.grc_v4_spark_state import QuarticSite
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[3]


def profile(graph, **changes):
    old = next(
        p
        for p in map(get_supported_profile, sorted(list_supported_profiles()))
        if p.identity_payload.profile_family_id == "A_RG2b"
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
    from pygrc.models.grc_v4_spark_arg2b_math import (
        APPROXIMATION_ID,
        COMPLETION_ID,
        DOMAIN_ID,
        ERROR_NORM,
    )

    p["realization"].update(
        extension_evaluator_id=COMPLETION_ID,
        approximation_policy_id=APPROXIMATION_ID,
        containment_certificate_id=DOMAIN_ID,
        error_norm_id=ERROR_NORM,
        error_tolerance=1e-11,
        iteration_limit=16,
    )
    p["solver"]["iteration_limit"] = 1
    p["solver"].update(
        conditioning_limit=10**12, absolute_tolerance=1e-11, relative_tolerance=1e-11
    )
    for section, updates in changes.items():
        (identity if section == "identity" else p[section]).update(updates)
    identity["params_hash"] = payload_identity("resolved_params", p)
    return QuarticARG2bProfile(
        resolve_profile(p, identity),
        QuarticSite(units_id="resource_potential_site_units_v1"),
    )


def configuration():
    from pygrc.models.grc_v4_spark_state import ExactResources

    _, graph, _, _ = subjects()
    declaration = json.loads(
        (
            ROOT
            / "implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/ARG2bDeclaration.json"
        ).read_bytes()
    )
    states = {
        role: ExactResources(
            graph,
            tuple(declaration["prepared_source"][role][n] for n in graph.live_node_ids),
            "21",
        )
        for role in ("current", "reset")
    }
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
    ).with_completion_policy(
        CompletionPolicy(
            numerical_policy_id=ARG2B_NUMERICAL_POLICY,
            step_duration="16",
            minimum_elapsed="32",
        )
    )
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
    value["resource_distribution"] = [5 / 2048, 1021 / 1024, 1 / 2048]
    value["history_policy"] = history_policy(model.configuration)
    return GRC9V4ExpansionRequestInput.from_payload(value)


def certificate_pair(model):
    from flint import arb, ctx, fmpq, fmpq_mat

    from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
    from pygrc.models.grc_9_v4_completion_crg2b import curve_at
    from pygrc.models.grc_9_v4_spark_owner import kernel
    from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK

    base = (
        ROOT
        / "implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability"
    )
    domain = json.loads((base / "ARG2bDirectDomain.json").read_bytes())
    need = lambda ok: (
        None if ok else (_ for _ in ()).throw(ValueError("common declared joint curve"))
    )
    need(domain["curves"]["current"] == domain["curves"]["reset"])
    event = model._operation._published.completion.event
    prefix = event["module"][0][: -len("/core")]

    def rename(name):
        return (
            prefix + name[len("sc2-positive-module") :]
            if name.startswith("sc2-positive-module/")
            else name
        )

    g = model.configuration.reference.graph
    node_order = [
        next(i for i, n in enumerate(domain["nodes"]) if rename(n) == v)
        for v in g.live_node_ids
    ]
    edge_order = [
        next(i for i, n in enumerate(domain["edge_ids"]) if rename(n) == v)
        for v in g.live_edge_ids
    ]
    order = node_order + [len(domain["nodes"]) + i for i in edge_order]
    curve = [domain["curves"]["current"][i] for i in order]
    origin = curve_at(fmpq_mat(curve), 0)
    n = len(g.live_node_ids)
    center = tuple(map(str, origin.entries()[:n]))
    logs = tuple(str(v / 64) for v in origin.entries()[n:])
    pair = tuple(
        CompletionCertificate.create_arg2b(
            kernel(model.configuration),
            model.configuration.policy,
            role,
            center,
            logs,
            curve,
        )
        for role in ("current", "reset")
    )
    with _ARB_CONTEXT_LOCK, ctx.workprec(256):
        weights = tuple(str(arb(fmpq(x)).exp().mid().fmpq()) for x in logs)
    return pair, ExactConductanceState(g, center, "21", weights)
