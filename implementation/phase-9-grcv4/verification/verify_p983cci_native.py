"""Reproduce bounded C_CI identity, certificate and path-effect observations.

This inspects native output against the unchanged independent P9-8.0 interval
owner. It does not generate oracle expectations from production output.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT, ROOT / "src", Path(__file__).resolve().parent):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import numpy as np

from tests.models.test_grc_9_v4_cci import (
    RADIUS,
    TOLERANCE,
    CandidateCIRoot,
    ExactBackend,
    GRC9V4CCIOperation,
    certify,
    exact_backend,
    fixture,
    separation,
)


def provenance():
    side = (
        ROOT
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
    )
    sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.forensic import contract_provenance
    from grcv4_explorer.successor import load_successor_forensic_context

    context = load_successor_forensic_context(ROOT, side)
    result = []
    for identifier in (
        "D11-G9-EC-LIFECYCLE-READMISSION",
        "D11-G9-EC-FIXED-BOND-SEED",
        "D11-C-EC-C-J0-LIFECYCLE",
        "D10.2-EC-PARENT-REAL-CI",
        "D10.2-EC-PARENT-L-ATOMICITY",
    ):
        trace = contract_provenance(context, identifier)
        if trace["row_count"] != 1:
            raise ValueError("ambiguous contract provenance")
        row = trace["rows"][0]
        result.append(
            {
                "contract_id": identifier,
                "trace_digest": trace["trace_digest"],
                "source_bundle_digest": trace["source_bundle_digest"],
                "source_ref": row["source_ref"],
                "edge_refs": row["edge_refs"],
                "support_disposition": row["payload"]["support_disposition"],
            }
        )
    return result


def observations():
    backend = (
        ExactBackend.FLINT if importlib.util.find_spec("flint") else ExactBackend.PYTHON
    )
    with exact_backend(backend):
        seed, request, initial = fixture()
        owner = GRC9V4CCIOperation(seed)
        result = owner.expand(request)
        if not result.committed:
            raise ValueError(str(result.failure))
        values = {
            "backend": str(backend),
            "native_domain": {
                "norm": "frobenius",
                "radius": RADIUS,
                "joint_residual_tolerance": TOLERANCE,
            },
            "independent_research_root_ball": {"norm": "infinity", "radius": 2**-20},
            "initial_inputs": initial.to_payload(),
            "request": request.to_payload(),
            "checkpoint": json.loads(owner.checkpoint()),
            "roots": [],
            "side_tool_provenance": provenance(),
        }
        for label, state in (("source", seed), ("target", owner.state)):
            for role in ("current", "reset"):
                inputs = replace(state.inputs, current=getattr(state.inputs, role))
                root = CandidateCIRoot(inputs)
                model, output, truth = certify(inputs, root)
                bounds = root.certificate.bounds
                row = {
                    "graph": label,
                    "role": role,
                    "evaluations": root.evaluations,
                    "native_bounds": {key: str(value) for key, value in bounds.items()},
                    "independent_errors": {
                        key: str(value) for key, value in truth["certificate"].items()
                    },
                    "joint_residual_squared": str(root.selected.residual_squared),
                    "fixed_selected_geometry_path_effects": {},
                }
                if label == "target":
                    for channel in ("modulation", "feedback", "geometry"):
                        control = model.read(
                            "C",
                            np.array(inputs.current.C),
                            None,
                            output["H"],
                            **{channel: False},
                        )
                        exact = truth["high"].read(
                            "C", truth["c"], None, truth["H"], **{channel: False}
                        )
                        row["fixed_selected_geometry_path_effects"][channel] = (
                            separation(
                                output["J"],
                                control["J"],
                                truth["read"]["J"],
                                exact["J"],
                            )
                        )
                # Fractions remain exact in the record; the summary is presentation only.
                row["bound_summary"] = {
                    key: float(Fraction(bounds[key]))
                    for key in (
                        "displacement_upper",
                        "contraction_upper",
                        "selector_gap_lower",
                    )
                }
                values["roots"].append(row)
        return values


if __name__ == "__main__":
    print(json.dumps(observations(), indent=2))
