"""A separately declared positive geometric seed, not an attracting-basin proof.

The accepted expansion fixtures intentionally use different seed thresholds.
This new configuration makes that choice explicit and binds a new model identity.
It never changes a live owner's frozen policy or fits an event to target success.
"""
from dataclasses import replace
from fractions import Fraction
import json

from pygrc.models import GRC9V4
from pygrc.models.grc_9_v4_identity import specialization_identity
from pygrc.models.grc_9_v4_lifecycle import GRC9V4Specialization
from pygrc.models.grc_v4_state import FrozenJSONMap
from examples.grc9v4.fixtures import configuration
from examples.grc9v4.tour import committed, require, signals


def run():
    original = configuration("C_OS")
    # Prescribed resource redistribution: +9/256 at the center and -1/256 at
    # each of nine leaves. This leaves the represented total exactly unchanged.
    values = list(original.current.C)
    values[0] += 9/256
    for i in range(1, 10):
        values[i] -= 1/256
    require(sum(map(Fraction, values)) == sum(map(Fraction, original.current.C)),
            "example redistribution changed charge")
    params = original.specialization.resolved.to_dict()
    params["spark"]["basin_hessian_tolerance"] = .01
    identity = original.specialization.identity_payload.to_dict()
    identity["specialization_params_hash"] = specialization_identity("resolved_specialization", params)
    spec = GRC9V4Specialization(FrozenJSONMap(params), FrozenJSONMap(identity))
    cfg = replace(original, current=replace(original.current, C=tuple(values)), specialization=spec)
    model = GRC9V4.from_config(cfg)
    diagnostic = signals(model)
    center = diagnostic["assessments"][0]
    require(center["basin_seed"] and not center["hybrid_spark_candidate"],
            "declared center is not a seed-only example")
    committed(model.migrate_basin_policy("seed-example-basin-policy"))
    observation = model.compute_observables()["basin_attributes"]
    return dict(schema="grc9v4-positive-seed-example-v1", configuration=cfg.to_payload(),
        original_specialization_id=original.specialization.specialization_id,
        selected_specialization_id=spec.specialization_id,
        exact_charge_preserved=True, diagnostic=diagnostic, basin_observation=observation,
        topology_events=0, completed_spark=False, attracting_basin_claimed=False,
        scope="New explicit bounded seed observation; unchanged frozen expansion fixtures.")


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, allow_nan=False))
