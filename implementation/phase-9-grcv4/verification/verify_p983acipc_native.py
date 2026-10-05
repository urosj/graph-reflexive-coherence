"""Reproduce native A_CI+PC observations against the immutable accepted A.1 oracle."""

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

from tests.models.test_grc_9_v4_acipc import (
    ORACLE_SHA,
    RECORD,
    ExactBackend,
    GRC9V4ACIPCOperation,
    GRC9V4ACIPCState,
    ResourceBoundaryError,
    altered_role,
    authority,
    checked,
    ci,
    corner_roots,
    exact_backend,
    fixture,
    native_effects,
    oracle,
    outputs,
    request_for,
    role_inputs,
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
        owner = GRC9V4ACIPCOperation(seed)
        outcome = owner.expand(request)
        if not outcome.committed:
            raise ValueError(str(outcome.failure))
        probes = []
        for label, state in (("source", seed), ("target", owner.state)):
            for role in ("current", "reset"):
                inputs = role_inputs(state.inputs, getattr(state.inputs, role))
                step, proof = checked(inputs, state.differential_reference)
                probes.append(
                    {
                        "graph": label,
                        "role": role,
                        "numerical_recipe": step.to_payload()["numerics"],
                        "native_certificate": step.root.certificate.bounds.to_dict(),
                        "independent_certificate": oracle.whole_chart(
                            state.differential_reference.port_graph.to_payload()
                        ),
                        "actual_input_interval_error_upper": {
                            k: str(v) for k, v in proof["errors"].items()
                        },
                        "physical_probe": outputs(step),
                        "evaluations": step.root.evaluations,
                        "joint_root_certificate": {
                            k: str(v) for k, v in proof["certificate"].items()
                        },
                    }
                )

        # Execute the real source beat. Archive actual committed bytes, not a
        # nearby oracle value or a fresh read's hypothetical next writer output.
        initial = authority(record["initial"]["current"])
        inputs = role_inputs(seed.inputs, initial)
        inputs = replace(
            inputs, reset=authority(record["initial"]["reset"]), step_index=0, time=0
        )
        source_step, source_proof = checked(inputs, seed.differential_reference)
        actual = GRC9V4ACIPCState(
            replace(source_step.next_inputs, dt=0), seed.specialization
        )
        actual_owner = GRC9V4ACIPCOperation(actual)
        actual_event = actual_owner.expand(request_for(actual, request))
        if not actual_event.committed:
            raise ValueError(str(actual_event.failure))
        content = actual_owner.carrier_archives[0].to_dict()["history_content"]
        if content["content"] != list(
            actual.inputs.current.Z_4 + actual.inputs.reset.Z_4
        ):
            raise ValueError("archive is not the actual source carrier pair")

        continuation = []
        for path, target in (
            ("pinned_oracle_entry", owner.state),
            ("actual_native_source_event", actual_owner.state),
        ):
            for role in ("current", "reset"):
                inputs = role_inputs(target.inputs, getattr(target.inputs, role))
                for index in range(11):
                    step, proof = checked(inputs, target.differential_reference)
                    continuation.append(
                        {
                            "path": path,
                            "role": role,
                            "step": index + 1,
                            "final_additional_probe": index == 10,
                            "actual_input_interval_error_upper": {
                                k: str(v) for k, v in proof["errors"].items()
                            },
                            "evaluations": step.root.evaluations,
                            "joint_root_certificate": {
                                k: str(v) for k, v in proof["certificate"].items()
                            },
                            "minimum_next_C": min(step.next_inputs.current.C),
                            "minimum_next_W": min(step.next_inputs.current.W_A),
                            "maximum_next_W": max(step.next_inputs.current.W_A),
                        }
                    )
                    inputs = step.next_inputs

        failures = []
        negative = authority(
            record["boundary_witnesses"]["admitted_event_negative_next_step"][
                "source_role"
            ]
        )
        for role in ("current", "reset"):
            changed = altered_role(seed, role, negative)
            receiver = GRC9V4ACIPCOperation(changed)
            event = receiver.expand(request_for(changed, request))
            if not event.committed:
                raise ValueError("negative continuation's event must admit")
            before = receiver.checkpoint()
            state = receiver.state
            inputs = role_inputs(state.inputs, getattr(state.inputs, role))
            high = oracle.IntervalRows(
                oracle.model_for(state.differential_reference.port_graph.to_payload())
            )
            root = ci.CandidateCIRoot(inputs, state.differential_reference)
            m = len(inputs.current.W_A)
            z = oracle.IV.matrix(
                [list(inputs.current.Z_4[i * m : (i + 1) * m]) for i in range(m)]
            )
            truth = oracle.enclosed_root(
                high,
                oracle.vector(inputs.current.C),
                oracle.vector(inputs.current.W_A),
                z,
                oracle.IV.matrix(root.selected.inputs.geometry.one_form_hodge.matrix),
            )
            after = (
                oracle.vector(inputs.current.C)
                - oracle.number(oracle.DT) * high.B * truth["read"]["J"]
            )
            upper = min(oracle.endpoint(x, 1) for x in after)
            if upper >= 0:
                raise ValueError("negative continuation is not independently certified")
            try:
                ci.ProvisionalCandidateCIStep(inputs, state.differential_reference)
            except ResourceBoundaryError as error:
                stage = error.stage
            else:
                raise ValueError("negative physical continuation was admitted")
            if stage != "charge_admission" or receiver.checkpoint() != before:
                raise ValueError("negative physical continuation altered the owner")
            failures.append(
                {
                    "role": role,
                    "event_committed": True,
                    "physical_step_failure_stage": stage,
                    "independent_negative_C_upper": str(upper),
                    "unchanged_checkpoint_sha256": hashlib.sha256(before).hexdigest(),
                }
            )
        effects = native_effects(seed, owner.state)
        return {
            "schema": "p983a_acipc_native_observations_v1",
            "result": "P983A_ACIPC_NATIVE_PASS",
            "backend": str(backend),
            "oracle_sha256": ORACLE_SHA,
            "oracle_record_digest": record["record_digest"],
            "native_domain": {
                "norm": "frobenius",
                "radius": oracle.RADIUS,
                "resource_radius": oracle.RESOURCE_RADIUS,
                "W_interval": [oracle.W_MIN, oracle.W_MAX],
                "kappa_H": oracle.KAPPA_H,
            },
            "request": request.to_payload(),
            "checkpoint": json.loads(owner.checkpoint()),
            "probes": probes,
            "actual_source_step": {
                "interval_error_upper": {
                    k: str(v) for k, v in source_proof["errors"].items()
                },
                "scientific_digest": actual.scientific_digest,
                "archive": actual_owner.carrier_archives[0].to_dict(),
                "exact_stage_equality": True,
            },
            "continuation": continuation,
            "certified_negative_continuations": failures,
            "native_effects": effects,
            "minimum_effect_margin": min(x["minimum_margin_ratio"] for x in effects),
            "chart_corner_roots": corner_roots(seed, owner.state),
            "side_tool_provenance": oracle.provenance(),
            "scope": "bounded native A_CI+PC whole-chart root and event with finite continuation; no global positivity, matched-forcing contraction, arbitrary-graph coverage or public support promotion",
        }


if __name__ == "__main__":
    print(json.dumps(observations(), indent=2))
