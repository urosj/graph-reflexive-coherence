"""Native A_RG2b observations against the immutable oracle and full equations."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for p in (ROOT, ROOT / "src", Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import hashlib

from tests.models.test_grc_9_v4_arg2b import (
    DT,
    ORACLE_SHA,
    RECORD,
    ExactBackend,
    GRC9V4ARG2bOperation,
    ProvisionalCandidateRG2bStep,
    authority,
    check,
    exact_backend,
    fixture,
    native_effects,
    oracle,
    read,
    values,
)


def observations():
    assert hashlib.sha256(RECORD.read_bytes()).hexdigest() == ORACLE_SHA
    record = json.loads(RECORD.read_text())
    seed, request = fixture(record)
    owner = GRC9V4ARG2bOperation(seed)
    result = owner.expand(request)
    if not result.committed:
        raise AssertionError(result.failure)
    comparisons = []
    pinned = {name: output for name, graph, entry, output in oracle.entries(record)}

    def pinned_deltas(name, section, point, following=None):
        from fractions import Fraction as Q

        import numpy as np

        expected = pinned[name]
        limits = {
            "C": oracle.RESOURCE_ERROR,
            "W_A": oracle.HISTORY_ERROR,
            "H": oracle.SECTION_ERROR,
            "current": oracle.CURRENT_ERROR,
            "baseline": oracle.CURRENT_ERROR,
            "source": oracle.SOURCE_ERROR,
        }
        deltas = {}
        for key, observed in values(section, point, following).items():
            delta = max(
                abs(Q(float(a)) - Q(float(b)))
                for a, b in zip(
                    np.array(observed).ravel(),
                    np.array(expected[key]).ravel(),
                    strict=True,
                )
            )
            if delta >= limits[key]:
                raise AssertionError((name, key, "immutable oracle comparison failed"))
            deltas[key] = str(delta)
        return deltas

    initial = replace(
        seed.inputs,
        current=authority(record["initial"]["current"]),
        reset=authority(record["initial"]["reset"]),
        dt=DT,
        step_index=0,
        time=0,
    )
    step = ProvisionalCandidateRG2bStep(initial, seed.differential_reference)
    _, errors = check(initial, step.section, step.point, step.next_inputs)
    comparisons.append(
        {
            "query": "source_physical",
            "oracle_deltas": pinned_deltas(
                "source_physical", step.section, step.point, step.next_inputs
            ),
            "errors": {k: str(v) for k, v in errors.items()},
            "invariance": step.diagnostics.to_dict(),
        }
    )
    for role in ("current", "reset"):
        inputs = replace(seed.inputs, current=getattr(seed.inputs, role))
        section, point = read(inputs)
        _, errors = check(inputs, section, point)
        comparisons.append(
            {
                "query": "source_reference_" + role,
                "oracle_deltas": pinned_deltas(
                    "source_reference_" + role, section, point
                ),
                "errors": {k: str(v) for k, v in errors.items()},
            }
        )
        inputs = replace(
            owner.state.inputs, current=getattr(owner.state.inputs, role), dt=DT
        )
        for i in range(10):
            step = ProvisionalCandidateRG2bStep(
                inputs, owner.state.differential_reference
            )
            _, errors = check(inputs, step.section, step.point, step.next_inputs)
            comparisons.append(
                {
                    "query": f"target_{role}_{i}",
                    "oracle_deltas": pinned_deltas(
                        f"target_{role}_{i}", step.section, step.point, step.next_inputs
                    ),
                    "errors": {k: str(v) for k, v in errors.items()},
                    "invariance": step.diagnostics.to_dict(),
                }
            )
            inputs = step.next_inputs
        section, point = read(inputs)
        _, errors = check(inputs, section, point)
        comparisons.append(
            {
                "query": f"target_{role}_10",
                "oracle_deltas": pinned_deltas(f"target_{role}_10", section, point),
                "errors": {k: str(v) for k, v in errors.items()},
            }
        )
    effects = native_effects(seed, owner.state)
    section, _ = read(owner.state.inputs)
    return {
        "result": "P983A_ARG2B_NATIVE_PASS",
        "oracle_sha256": ORACLE_SHA,
        "oracle_record_digest": record["record_digest"],
        "comparisons": comparisons,
        "effects": effects,
        "minimum_effect_margin": min(x["minimum_margin_ratio"] for x in effects),
        "native_bounds": section.certificate.bounds.to_dict(),
        "checkpoint": json.loads(owner.checkpoint()),
        "side_tool": oracle.provenance(),
    }


if __name__ == "__main__":
    with exact_backend(ExactBackend.FLINT):
        print(json.dumps(observations(), indent=2))
