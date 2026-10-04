"""Native C_RG2b observations against independent complete interval equations.

The oracle retains the normative Q-similarity current, independently evaluated
backward chains, and the unchanged accepted global bounds. Runtime outputs
never provide its expected physical resources, currents, sources or sections.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT, ROOT / "src", Path(__file__).resolve().parent):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import numpy as np
import test_p980_rg2b_completion as proof
import test_p980_rg2b_numerical as oracle
from test_p980_os_effect_witness import (
    IV,
    PARAMS,
    IntervalRows,
    full_error,
    number,
    separation,
    vector,
)

from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
from pygrc.models.grc_v4_ci import _source
from pygrc.models.grc_v4_rg2b import CandidateRG2bSection, ProvisionalCandidateRG2bStep


def model(inputs):
    graph = inputs.geometry.reference.graph.port_graph
    return oracle.RepresentedAuxiliary(
        graph.live_node_ids, [e.to_payload() for e in graph.edges], PARAMS
    )


def expected(inputs):
    m = model(inputs)
    # Independent complete source/current read and completed section from saved C.
    _, _, truth = oracle.ordinary(m, "C", np.array(inputs.current.C))
    return m, truth


def actual(section, point):
    return {
        "H": np.array(section.geometry.one_form_hodge.matrix),
        "J": np.array(point.current.values),
        "baseline": np.array(point.algebra.baseline.values),
        "source": np.array(_source(point, point.current).increment),
    }


def check(section, point, truth, following=None):
    values = actual(section, point)
    errors = {
        "H": full_error(values["H"].ravel(), IV.matrix(list(truth["exact_H"]))),
        "J": full_error(values["J"], truth["exact_read"]["J"]),
        "baseline": full_error(values["baseline"], truth["exact_read"]["baseline"]),
        "source": full_error(
            values["source"].ravel(), IV.matrix(list(truth["exact_read"]["source"]))
        ),
    }
    if following is not None:
        errors["resource"] = full_error(following.current.C, truth["exact_after"])
    for key, value in errors.items():
        limit = (
            Q(1, 2**48)
            if key == "H"
            else Q(1, 2**64)
            if key == "source"
            else Q(1, 2**40)
        )
        if value >= limit:
            raise AssertionError(
                f"native {key} full error {float(value)} exceeds {float(limit)}"
            )
    return {key: str(value) for key, value in errors.items()}


def read(inputs):
    section = CandidateRG2bSection(inputs)
    return section, CandidateCCurrent(
        replace(inputs, geometry=section.geometry, stage="rg2b_section")
    )


def effects(inputs):
    """Fixed-section mechanism consumers and realization distinction, both roles."""
    m, truth = expected(inputs)
    section, point = read(inputs)
    check(section, point, truth)
    high, c = IntervalRows(m), np.array(inputs.current.C)
    h = np.array(section.geometry.one_form_hodge.matrix)
    values = actual(section, point)
    result = {}
    for name, switch in (
        ("geometry", "geometry"),
        ("feedback", "feedback"),
        ("modulation", "modulation"),
    ):
        control = m.read("C", c.copy(), None, h.copy(), **{switch: False})
        exact = high.read("C", vector(c), None, truth["exact_H"], **{switch: False})
        for field in ("J", "baseline") if name != "feedback" else ("J",):
            result[name + "_" + field] = separation(
                values[field], control[field], truth["exact_read"][field], exact[field]
            )
    # An instantaneous source image at the query is not the invariant section.
    ci_image = np.eye(len(h)) + 0.5 * values["source"]
    ci_exact = high.I + number(Q(1, 2)) * truth["exact_read"]["source"]
    result["section_vs_instantaneous_image"] = separation(
        h.ravel(),
        ci_image.ravel(),
        IV.matrix(list(truth["exact_H"])),
        IV.matrix(list(ci_exact)),
    )
    return result


def provenance():
    side = (
        ROOT
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
    )
    sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance, debt_lifecycle

    context = load_current_forensic_context(ROOT, side)
    return {
        "contracts": {
            k: contract_provenance(context, k)
            for k in (
                "D11-G9-EC-RESOURCE-DISTRIBUTION",
                "D11-G9-EC-LIFECYCLE-READMISSION",
                "D11-C-EC-C-J0-LIFECYCLE",
                "D10.2-EC-PARENT-REAL-RG2B",
                "D10.2-EC-RG-INVARIANCE",
                "D10.2-EC-RG-LIPSCHITZ-CONTRACTION",
                "D10.2-EC-RG-DETERMINISM",
                "D10.2-EC-RG-CLAIM-CEILING",
            )
        },
        "debts": {
            k: debt_lifecycle(context, k)
            for k in ("GTRS-RG-DEBT-C1-SECTION-REGULARITY",)
        },
    }


def observations(seed=None, request=None, initial=None):
    from tests.models.test_grc_9_v4_crg2b import DT, GRC9V4CRG2bOperation, fixture

    if seed is None:
        seed, request, initial = fixture()
    owner = GRC9V4CRG2bOperation(seed)
    result = owner.expand(request)
    if not result.committed:
        raise AssertionError(result.failure)
    comparisons, controls, inverse = [], {}, {}
    for label, entry, count in (
        ("source", initial, 1),
        ("target_current", replace(owner.state.inputs, dt=DT), 10),
        (
            "target_reset",
            replace(owner.state.inputs, current=owner.state.inputs.reset, dt=DT),
            10,
        ),
    ):
        for k in range(count):
            _m, truth = expected(entry)
            step = ProvisionalCandidateRG2bStep(entry)
            comparisons.append(
                {
                    "query": f"{label}_{k}",
                    **check(step.section, step.point, truth, step.next_inputs),
                    "native_invariance": step.diagnostics.to_dict(),
                }
            )
            if k == 0 and label.startswith("target"):
                b, sb = (
                    proof.global_bounds("C"),
                    proof.section_budgets(proof.global_bounds("C")),
                )
                tail = (
                    sb["inverse_lip"]
                    * b["A_H"]
                    * sb["q_section"] ** 5
                    * sb["value_radius"]
                )
                zero_index = list(entry.current.C).index(0)
                upper = (
                    Q(float(truth["chain"].x[1][zero_index]))
                    + truth["certificate"]["state_error"]
                    + tail
                )
                if upper >= 0:
                    raise AssertionError(
                        "signed first predecessor is not certified negative"
                    )
                inverse[label] = {
                    "first_predecessor_upper": str(upper),
                    "full_inverse_tail": str(tail),
                }
            entry = step.next_inputs
        _, truth = expected(entry)
        section, point = read(entry)
        comparisons.append(
            {"query": label + "_final_read", **check(section, point, truth)}
        )
    for label, inputs in (("source", seed.inputs), ("target", owner.state.inputs)):
        for role in ("current", "reset"):
            controls[label + "_" + role] = effects(
                replace(inputs, current=getattr(inputs, role))
            )
    section, _ = read(owner.state.inputs)
    return {
        "source_profile": seed.inputs.geometry.reference.profile.complete_profile_id,
        "target_profile": owner.state.inputs.geometry.reference.profile.complete_profile_id,
        "source_graph": seed.inputs.geometry.reference.graph.graph_digest,
        "target_graph": owner.state.inputs.geometry.reference.graph.graph_digest,
        "comparisons": comparisons,
        "effects": controls,
        "signed_inverse": inverse,
        "global_bounds": section.certificate.bounds.to_dict(),
        "side_tool": provenance(),
    }


if __name__ == "__main__":
    from pygrc.models.grc_v4_exact import ExactBackend, exact_backend

    with exact_backend(ExactBackend.FLINT):
        print(json.dumps(observations(), indent=2, sort_keys=True))
