"""Reproduce A_CI native roots/effects against the unchanged accepted A.1 oracle."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT, ROOT / "src", Path(__file__).resolve().parent):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tests.models.test_grc_9_v4_aci import (
    ORACLE_SHA,
    RECORD,
    ExactBackend,
    GRC9V4ACIOperation,
    ProvisionalCandidateCIStep,
    authority,
    exact_backend,
    fixture,
    native_effects,
    oracle,
    outputs,
    request_for,
    simplex_observations,
)


def observations():
    if hashlib.sha256(RECORD.read_bytes()).hexdigest() != ORACLE_SHA:
        raise ValueError("accepted oracle changed")
    record = json.loads(RECORD.read_text())
    backend = (
        ExactBackend.FLINT if importlib.util.find_spec("flint") else ExactBackend.PYTHON
    )
    with exact_backend(backend):
        seed, request = fixture(record)
        owner = GRC9V4ACIOperation(seed)
        outcome = owner.expand(request)
        if not outcome.committed:
            raise ValueError(str(outcome.failure))
        roots = []
        for label, state in (("source", seed), ("target", owner.state)):
            for role in ("current", "reset"):
                inputs = replace(
                    state.inputs, current=getattr(state.inputs, role), dt=oracle.DT
                )
                saved_c, saved_w = tuple(inputs.current.C), tuple(inputs.current.W_A)
                step = ProvisionalCandidateCIStep(inputs, state.differential_reference)
                values = outputs(step)
                checked = oracle.check_step(
                    state.differential_reference.port_graph.to_payload(),
                    saved_c,
                    saved_w,
                    values,
                )
                roots.append(
                    {
                        "graph": label,
                        "role": role,
                        "evaluations": step.root.evaluations,
                        "numerical_recipe": step.root.to_payload()["numerics"],
                        "native_certificate": step.root.certificate.bounds.to_dict(),
                        "native_joint_residual_squared": str(
                            step.root.selected.residual_squared
                        ),
                        "independent_certificate": {
                            k: str(v)
                            for k, v in checked["truth"]["certificate"].items()
                        },
                        "independent_domain": checked["domain"],
                        "physical_probe": values,
                    }
                )
        failures = []
        negative = authority(
            record["rejection_expectations"]["target_domain"]["source_role"]
        )
        for role in ("current", "reset"):
            altered = replace(seed, inputs=replace(seed.inputs, **{role: negative}))
            receiver = GRC9V4ACIOperation(altered)
            before = receiver.checkpoint()
            rejected = receiver.expand(request_for(altered, request))
            if rejected.committed or receiver.checkpoint() != before:
                raise ValueError("certified negative did not roll back")
            failures.append(
                {
                    "role": role,
                    "failure": rejected.failure.to_payload(),
                    "unchanged_checkpoint_sha256": hashlib.sha256(before).hexdigest(),
                }
            )
        effects = native_effects(seed, owner.state)
        return {
            "schema": "p983a_aci_native_observations_v1",
            "result": "P983A_ACI_NATIVE_PASS",
            "backend": str(backend),
            "oracle_sha256": ORACLE_SHA,
            "oracle_record_digest": record["record_digest"],
            "native_domain": {
                "norm": "frobenius",
                "radius": oracle.RADIUS,
                "joint_residual_tolerance": oracle.TOLERANCE,
            },
            "request": request.to_payload(),
            "checkpoint": json.loads(owner.checkpoint()),
            "roots": roots,
            "certified_negative_failures": failures,
            "native_effects": effects,
            "simplex_boundary_controls": simplex_observations(seed, request),
            "minimum_effect_margin": min(x["minimum_margin_ratio"] for x in effects),
            "side_tool_provenance": oracle.provenance(),
            "scope": "bounded A_CI event/root/writer evidence; no global stability or public support promotion",
        }


if __name__ == "__main__":
    print(json.dumps(observations(), indent=2))
