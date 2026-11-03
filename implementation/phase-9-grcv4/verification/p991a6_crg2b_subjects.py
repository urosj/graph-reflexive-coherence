"""Declared C_RG2b native inputs; no saved target advances the public model."""

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
from pygrc.models.grc_v4_spark_crg2b_math import (
    APPROXIMATION_ID,
    COMPLETION_ID,
    DOMAIN_ID,
    ERROR_NORM,
)
from pygrc.models.grc_v4_spark_state import (
    CRG2B_NUMERICAL_POLICY,
    QuarticCRG2bProfile,
    QuarticSite,
)
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[3]


def profile(graph, **changes):
    predecessor = next(
        p
        for p in map(get_supported_profile, sorted(list_supported_profiles()))
        if p.identity_payload.profile_family_id == "C_RG2b"
    )
    p = cos_profile(graph).baseline.params_resolved.to_payload()
    identity = predecessor.identity_payload.to_payload()
    p["realization"] = predecessor.params_resolved.realization.to_payload()
    p["realization"].update(
        extension_evaluator_id=COMPLETION_ID,
        approximation_policy_id=APPROXIMATION_ID,
        containment_certificate_id=DOMAIN_ID,
        error_norm_id=ERROR_NORM,
        error_tolerance=1e-11,
        iteration_limit=12,
    )
    p["solver"] = predecessor.params_resolved.solver.to_payload()
    p["solver"].update(conditioning_limit=10**12)
    for section, updates in changes.items():
        (identity if section == "identity" else p[section]).update(updates)
    identity["params_hash"] = payload_identity("resolved_params", p)
    return QuarticCRG2bProfile(
        resolve_profile(p, identity),
        QuarticSite(units_id="resource_potential_site_units_v1"),
    )


def configuration():
    from pygrc.models.grc_v4_spark_state import ExactResources

    _, graph, _, _ = subjects()
    declared = json.loads(
        (
            ROOT
            / "implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/CRG2bDirectDeclaration.json"
        ).read_bytes()
    )
    states = {
        role: ExactResources(
            graph,
            tuple(declared["prepared_source"][role][n] for n in graph.live_node_ids),
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
            numerical_policy_id=CRG2B_NUMERICAL_POLICY,
            step_duration="8",
            minimum_elapsed="16",
        )
    )
    return GRC9V4SparkConfiguration(
        SparkReference(graph, profile(graph)), spec, states["current"], states["reset"]
    )


def request(model, chirality=1):
    from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
    from tests.models.test_grc_9_v4_spark_completion import request as base

    value = base(model, chirality).to_payload()
    value["resource_distribution"] = [5 / 2048, 1021 / 1024, 1 / 2048]
    return GRC9V4ExpansionRequestInput.from_payload(value)


def certificate_pair(model):
    from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
    from pygrc.models.grc_9_v4_completion_crg2b import curve_at
    from pygrc.models.grc_9_v4_spark_owner import kernel
    from pygrc.models.grc_v4_spark_cos import _matrix
    from pygrc.models.grc_v4_spark_state import ExactResources

    base = (
        ROOT
        / "implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability"
    )
    domain = json.loads((base / "CRG2bDirectDomain.json").read_bytes())
    event = model._operation._published.completion.event
    original = [n for n in domain["nodes"] if str(n).startswith("sc2-positive-module/")]
    # Core/satellites have stable scientific identities; actual event names are receipt-derived.
    originals = [
        "sc2-positive-module/core",
        *[f"sc2-positive-module/satellite/{i}" for i in (1, 2, 3)],
    ]
    assert set(originals) == set(original)
    mapping = dict(zip(originals, event["module"], strict=True))
    mapping.update({n: n for n in domain["nodes"] if n not in mapping})
    nodes = model.configuration.reference.graph.live_node_ids
    order = [
        next(i for i, n in enumerate(domain["nodes"]) if mapping[n] == target)
        for target in nodes
    ]
    curve = [domain["chebyshev_coefficients"][i] for i in order]
    center = tuple(str(x) for x in curve_at(_matrix(curve), 0).entries())
    pair = tuple(
        CompletionCertificate.create_crg2b(
            kernel(model.configuration), model.configuration.policy, role, center, curve
        )
        for role in ("current", "reset")
    )
    return pair, ExactResources(model.configuration.reference.graph, center, "21")
