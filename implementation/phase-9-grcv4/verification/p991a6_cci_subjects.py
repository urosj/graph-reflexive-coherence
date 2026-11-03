"""Declared C_CI native inputs; no saved target advances the public model."""

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
from pygrc.models.grc_v4_spark_cci import ROOT_DOMAIN
from pygrc.models.grc_v4_spark_state import (
    CI_NUMERICAL_POLICY,
    QuarticCCIProfile,
    QuarticSite,
)
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[3]


def profile(graph, **changes):
    predecessor = next(
        p
        for p in map(get_supported_profile, sorted(list_supported_profiles()))
        if p.identity_payload.profile_family_id == "C_CI"
    )
    p = cos_profile(graph).baseline.params_resolved.to_payload()
    identity = predecessor.identity_payload.to_payload()
    p["realization"] = predecessor.params_resolved.realization.to_payload()
    p["realization"].update(
        contraction_domain_id=ROOT_DOMAIN, iteration_limit=60, tolerance=1e-11
    )
    p["solver"] = predecessor.params_resolved.solver.to_payload()
    p["solver"].update(iteration_limit=60, conditioning_limit=10**12)
    for section, updates in changes.items():
        (identity if section == "identity" else p[section]).update(updates)
    identity["params_hash"] = payload_identity("resolved_params", p)
    return QuarticCCIProfile(
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
    ).with_completion_policy(CompletionPolicy(numerical_policy_id=CI_NUMERICAL_POLICY))
    return GRC9V4SparkConfiguration(
        SparkReference(graph, profile(graph)), spec, states["current"], states["reset"]
    )
