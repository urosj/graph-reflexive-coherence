"""Sixteen C_RG2b expansion companions with retained complete inverse chains.

Native execution, independent interval recomputation and scoped acceptance are
separate. The signed argument completion is the accepted R6/native successor,
not the paper's compact-support extension and not an instantaneous CI root.
"""

import argparse
import json
import platform
import time
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

import numpy as np
import p984b_runtime as b
import test_p980_rg2b_completion as proof
import test_p980_rg2b_numerical as oracle
from p984b_cci_runtime import represented_continuity
from test_p980_os_effect_witness import (
    IV,
    PARAMS,
    IntervalRows,
    endpoint,
    full_error,
    infinity,
    inverse,
    number,
    separation,
    upper_abs,
    vector,
)

from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models import grc_9_v4_rg2b as signed
from pygrc.models import grc_v4_rg2b as rg
from pygrc.models.grc_9_v4_expansion import crg2b_profile_template
from pygrc.models.grc_v4_candidate_c import CandidateCCurrent
from pygrc.models.grc_v4_ci import _source
from tests.models.test_grc_9_v4_crg2b import configure

SELF = b.HERE + "p984b_crg2b_runtime.py"
TEST = b.HERE + "test_p984b_crg2b_runtime.py"
INPUTS = b.BASE + "P9-8.4b-CRG2bCases.json"
RESULTS = b.BASE + "P9-8.4b-CRG2bResults.json"
REVIEW = b.BASE + "P9-8.4b-CRG2bRuntimeReview.md"
PREDECESSOR = b.BASE + "P9-8.3C-RG2b-Validation.json"
DECLARATION = b.BASE + "P9-8.4b-COSCases.json"
ROLES = ("current", "reset")
LIMITS = {
    "geometry_error": Q(1, 2**48),
    "current_error": Q(1, 2**40),
    "baseline_error": Q(1, 2**40),
    "source_error": Q(1, 2**64),
    "readback_error": Q(1, 2**40),
    "flat_error": Q(1, 2**40),
    "resource_error": Q(1, 2**40),
}


def state(payload):
    spec = payload["specialization"]
    return native.GRC9V4CRG2bState(
        b.GeometryStageInputs.from_payload(payload["inputs"]),
        native.GRC9V4Specialization(
            b.FrozenJSONMap(spec["resolved"]), b.FrozenJSONMap(spec["identity_payload"])
        ),
    )


def model(inputs):
    graph = inputs.geometry.reference.graph.port_graph
    return oracle.RepresentedAuxiliary(
        graph.live_node_ids, [e.to_payload() for e in graph.edges], PARAMS
    )


def global_record():
    values = proof.global_bounds("C")
    section = proof.section_budgets(values)
    names = {
        "base_X_lipschitz": "A_X",
        "base_h_lipschitz": "A_H",
        "base_displacement_upper": "M_f",
        "source_upper": "M_S",
        "source_X_lipschitz": "B_X",
        "source_h_lipschitz": "B_H",
        "current_upper": "J",
    }
    native_bounds = {k: str(values[v]) for k, v in names.items()}
    native_bounds.update(
        inverse_lipschitz=str(section["inverse_lip"]),
        contraction_upper=str(section["q_section"]),
        section_lipschitz=str(proof.SECTION_LIP),
        section_radius=str(proof.RHO),
        section_value_radius=str(section["value_radius"]),
        image_lipschitz=str(section["image_lip"]),
        current_inverse_upper=str(1 / values["current_margin"]),
    )
    return {
        "global_bounds": {k: str(v) for k, v in values.items()},
        "section_bounds": {k: str(v) for k, v in section.items()},
        "native_bounds": native_bounds,
    }


def chart_record(inputs):
    """Actual graph hypotheses, not a cardinality-only admission shortcut."""
    m = model(inputs)
    oracle.checked_model(m)
    n, edges = len(m.nodes), len(m.edges)
    adjacency = {v: set() for v in m.nodes}
    for edge in m.edges:
        u, v = edge["tail"]["node_id"], edge["head"]["node_id"]
        b.require(u != v, "signed graph self-loop")
        adjacency[u].add(v)
        adjacency[v].add(u)
    reached = {m.nodes[0]}
    for _ in m.nodes:
        reached |= {v for u in tuple(reached) for v in adjacency[u]}
    bn, dn, mn = (infinity(IV.matrix(x.tolist())) for x in (m.B, m.D, m.mask))
    b.require(
        2 <= n <= 17
        and edges == n - 1
        and len(reached) == n
        and bn <= 9
        and dn <= 10
        and mn <= 5,
        "signed graph hypotheses fail",
    )
    ref = inputs.geometry.reference
    p = ref.profile.params_resolved
    expected = {
        "Lambda_C": 2**-9,
        "C_ref": 1,
        "kappa_M_C": 2**-24,
        "kappa_Phi_C": 1,
        "eta_C": 1,
        "tau_C": 1,
        "chi_C": 16,
        "zeta_C": 2**-37,
    }
    b.require(
        all(getattr(p.candidate, k) == v for k, v in expected.items())
        and p.geometry.kappa_H == 0.5
        and all(v == 1 for v in ref.edge_weights.values())
        and all(v == 0 for row in ref.K4_base for v in row),
        "signed parameter/reference drift",
    )
    b.require(
        p.realization.extension_evaluator_id == signed.EXTENSION
        and p.realization.approximation_policy_id == signed.APPROXIMATION
        and p.realization.containment_certificate_id == signed.CONTAINMENT
        and p.realization.error_norm_id == signed.ERROR_NORM
        and p.realization.error_tolerance == 2**-48
        and p.realization.iteration_limit == 222,
        "signed completion/recipe drift",
    )
    gap = (1 - proof.RHO) / (n * (n - 1))
    b.require(gap > Q(p.candidate.Lambda_C), "constant selector gap unresolved")
    b.require(
        (1 + proof.RHO) / (1 - proof.RHO) <= Q(p.solver.conditioning_limit),
        "Hodge conditioning not certified",
    )
    b.require(inputs.dt in (0, b.DT), "fixed completion beat drift")
    return {
        "vertices": n,
        "edges": edges,
        "incidence_norm": str(bn),
        "gram_norm": str(dn),
        "mask_norm": str(mn),
        "selector_gap_lower": str(gap),
        "completion": signed.EXTENSION,
        "graph_digest": ref.graph.graph_digest,
    }


def bind_case(seed, original):
    case = deepcopy(original)
    case["request"]["source_state_digest"] = seed.scientific_digest
    vector_row = next(
        v
        for v in b.read(b.VECTORS)["grc9_expansion_vectors"]
        if v["fixture_id"] == case["fixture_id"]
    )
    case["oracle"] = b.construction_oracle(
        vector_row, case["request"], seed.to_payload()["specialization"]
    )
    case["independent_graph_chart"] = chart_record(
        b.independent_target({"expected_source": seed.to_payload()}, case)
    )
    return case


def make_manifest():
    old = b.read(PREDECESSOR)
    b.require(
        old["acceptance"]["status"] == "accepted_by_user",
        "native C_RG2b predecessor not accepted",
    )
    declaration = b.read(DECLARATION)
    b.check_digest(declaration)
    initial = configure(
        b.GeometryStageInputs.from_payload(declaration["initial_inputs"])
    )
    nominal = state(
        {
            "inputs": replace(initial, dt=0).to_payload(),
            "specialization": declaration["expected_source"]["specialization"],
        }
    )
    b.require(
        initial.geometry.reference.profile.complete_profile_id
        == old["numerical_observations"]["source_profile"],
        "accepted native declaration mismatch",
    )
    coverage = b.read(b.COVERAGE)
    b.check_digest(coverage)
    wanted = {
        r["fixture_id"]
        for r in coverage["coverage_cells"]
        if r["owner"] == "P9-8.4b" and r["family"] == "C_RG2b" and r["applicable"]
    }
    cases = []
    for v in b.read(b.VECTORS)["grc9_expansion_vectors"]:
        if v["fixture_id"] not in wanted:
            continue
        request = deepcopy(declaration["cases"][0]["request"])
        request.update(
            {
                k: v["request"][k]
                for k in ("target_effective_degree", "module_chirality", "growth_phase")
            }
        )
        request.update(
            operation_id="p984b-crg2b-" + v["fixture_id"],
            source_state_digest=nominal.scientific_digest,
            target_profile_template_id=crg2b_profile_template(
                initial.geometry.reference
            ).profile_template_id,
            resource_distribution=[0.25, 0.5, 0.25]
            if (request["target_effective_degree"], request["growth_phase"]) == (52, 1)
            else [0.5, 0.25, 0.25],
        )
        case = {
            "case_id": "P984B-CRG2B-" + v["fixture_id"],
            "fixture_id": v["fixture_id"],
            "family": "C_RG2b",
            "subject_kind": "native_companion",
            "request": request,
            "coverage_binding": {
                "record_digest": coverage["record_digest"],
                "cell_ids": [v["fixture_id"] + "::C_RG2b::" + role for role in ROLES],
            },
            "schedule": {
                "source_current_beats": 1,
                "source_reset_beats": 0,
                "target_beats_per_role": 10,
                "dt": b.DT,
                "final_read": True,
            },
            "execution_budget_seconds": 900,
            "comparison": {
                "kind": "complete_native_chain_and_independent_interval_equations",
                "budgets": {k: str(x) for k, x in LIMITS.items()},
                "section_norm": "induced_infinity",
                "current_bridge_norm": "edge_l2",
                "depth": 6,
                "sweeps": 18,
                "accumulated_trajectory_error_bound": False,
                "uniform_parameter_tube": False,
            },
        }
        case = bind_case(nominal, case)
        target = b.independent_target({"expected_source": nominal.to_payload()}, case)
        case["independent_graph_chart"] = chart_record(target)
        cases.append(case)
    b.require(len(cases) == 16, "all sixteen C_RG2b layouts required")
    paths = [
        SELF,
        TEST,
        b.SELF,
        b.HERE + "p984b_cci_runtime.py",
        b.HERE + "verify_p983crg2b_native.py",
        DECLARATION,
        PREDECESSOR,
        b.BASE + "P9-8.3C-RG2b-RuntimeReview.md",
        b.COVERAGE,
        b.VECTORS,
        b.BASE + "P9-8.0-RG2bCompletion.md",
        b.BASE + "P9-8.0-RG2bNumericalFeasibility.md",
        coverage["scientific_claim_mapping"]["paper"]["path"],
        coverage["scientific_claim_mapping"]["side_tool_source"],
        "implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json",
        "pyproject.toml",
        "uv.lock",
    ]
    paths += [
        str(p.relative_to(b.ROOT))
        for pattern in (
            "src/pygrc/models/grc*v4*.py",
            "src/pygrc/models/grc_v4_assets/*.json",
            "tests/models/test_grc*v4*.py",
            b.HERE + "test_p980*.py",
        )
        for p in b.ROOT.glob(pattern)
    ]
    return b.seal(
        {
            "schema": "p984b-crg2b-case-manifest-v1",
            "family": "C_RG2b",
            "initial_inputs": initial.to_payload(),
            "nominal_source": nominal.to_payload(),
            "cases": cases,
            "source_bindings": b.bind(paths),
            "independent_source_chart": chart_record(initial),
            "independent_global_proof": global_record(),
            "claim_traces": old["numerical_observations"]["side_tool"],
            "scientific_contracts": {
                "completion": "accepted_signed_argument_retraction_not_compact_support",
                "claim_restrictions": {
                    "GTRS-RG-DEBT-C1-SECTION-REGULARITY": "narrowed_unresolved",
                    "D10.2-EC-RG-CLAIM-CEILING": "completion_relative_Lipschitz_no_spectrum_or_indefinite_positivity",
                    "D10-CL-C-012": "no_arbitrary_graph_or_future_exhaustive_support",
                },
            },
            "source_rule": "one actual RG source beat; rebind actual event identities before execution",
            "resource_recipe": "accepted [1/2,1/4,1/4]; explicit D52 phase-one [1/4,1/2,1/4] companion, independently checked",
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )


def check_manifest(value):
    b.check_digest(value)
    b.check_bindings(value["source_bindings"])
    b.require(value == make_manifest(), "C_RG2b manifest/case/budget drift")


@contextmanager
def capture_chains():
    rows = []
    real = signed.certify_chain

    def captured(cert, query, x, h):
        error, bounds = real(cert, query, x, h)
        b.require(
            cert.bounds.to_dict() == global_record()["native_bounds"],
            "native global proof mismatch",
        )
        rows.append(
            {
                "input_identity": cert.inputs.identity,
                "query": list(query),
                "x": [a.tolist() for a in x],
                "h": [a.tolist() for a in h],
                "native_chain_error": str(error),
                "native_chain_bounds": {k: str(v) for k, v in bounds.items()},
                "native_global_digest": b.digest(cert.bounds.to_dict()),
            }
        )
        return error, bounds

    with patch.object(signed, "certify_chain", captured):
        yield rows


def chain(value):
    return oracle.Chain(
        [np.asarray(x, dtype=np.float64) for x in value["chain"]["x"]],
        [np.asarray(h, dtype=np.float64) for h in value["chain"]["h"]],
    )


def level_residuals(m, work):
    """Literal full equations at each signed inverse state, in declared norms."""
    levels = []
    for i in range(1, 7):
        projected = [
            min(proof.C_HIGH, max(proof.C_LOW, Q(float(z)))) for z in work.x[i]
        ]
        f, s = proof.literal_signed_increment(
            m, "C", vector(projected), IV.matrix(work.h[i].tolist())
        )
        levels.append(
            {
                "level": i,
                "state_residual": str(
                    infinity(vector(work.x[i]) + f - vector(work.x[i - 1]))
                ),
                "geometry_residual": str(
                    infinity(
                        IV.matrix(work.h[i - 1].tolist()) - (m.I + number(Q(1, 2)) * s)
                    )
                ),
            }
        )
    return levels


def truth(before, value):
    m = model(before)
    work = chain(value)
    h, certificate = oracle.certify_chain(
        proof.auxiliary(m), "C", work, vector(before.current.C)
    )
    high = IntervalRows(m)
    c = vector(before.current.C)
    read = high.read("C", c, None, h)
    exp = IV.exp(2 * sum(c) / len(c))
    t = IV.exp(number(Q(1, 2**24)) * (exp - 1) / (exp + 1))
    readback = 16 * inverse(high.I + t * h * high.D) * read["J"]
    flat = inverse(h) * readback
    return {
        "model": m,
        "high": high,
        "H": h,
        "certificate": certificate,
        "read": read,
        "readback": readback,
        "flat": flat,
    }


def independent_certificate(before, value):
    exact = truth(before, value)
    cert = exact["certificate"]
    h_error = min(cert["total_error"], infinity(IV.matrix(value["H"]) - exact["H"]))
    errors = {
        "geometry_error": h_error,
        "current_error": full_error(value["J"], exact["read"]["J"]),
        "baseline_error": full_error(value["baseline"], exact["read"]["baseline"]),
        "source_error": full_error(
            np.asarray(value["source"]).ravel(),
            IV.matrix(list(exact["read"]["source"])),
        ),
        "readback_error": full_error(value["readback"], exact["readback"]),
        "flat_error": full_error(value["flat"], exact["flat"]),
    }
    levels = level_residuals(proof.auxiliary(exact["model"]), chain(value))
    b.require(
        max(Q(x["state_residual"]) for x in levels) == cert["state_residual"]
        and max(Q(x["geometry_residual"]) for x in levels) == cert["geometry_residual"],
        "per-level residual mismatch",
    )
    global_bounds = proof.global_bounds("C")
    section = proof.section_budgets(global_bounds)
    first_tail = (
        section["inverse_lip"]
        * global_bounds["A_H"]
        * section["q_section"] ** 5
        * section["value_radius"]
    )
    zero = [i for i, v in enumerate(before.current.C) if v == 0]
    upper = {
        str(i): str(Q(value["chain"]["x"][1][i]) + cert["state_error"] + first_tail)
        for i in zero
    }
    return {
        "input_identity": before.identity,
        "selected_read_digest": value["record_digest"],
        "bounds": {k: str(v) for k, v in errors.items()},
        "chain": {k: str(v) for k, v in cert.items()},
        "level_residuals": levels,
        "first_inverse_tail": str(first_tail),
        "zero_core_first_predecessor_upper": upper,
    }


def read_record(section, point, record):
    b.require(
        record["input_identity"] == section.inputs.identity,
        "captured chain operand mismatch",
    )
    result = b.seal(
        {
            "input_identity": section.inputs.identity,
            "identity": section.identity,
            "selected_inputs_identity": point.inputs.identity,
            "point_identity": point.identity,
            "read_source": point.read.source_identity,
            "read_current": list(point.read.current.values),
            "H": [list(r) for r in section.geometry.one_form_hodge.matrix],
            "J": list(point.current.values),
            "baseline": list(point.algebra.baseline.values),
            "readback": list(point.read.flux.values),
            "flat": list(point.read.causal_flat.values),
            "source": [list(r) for r in _source(point, point.current).increment],
            "levels": section.levels,
            "evaluations": section.evaluations,
            "error_upper": section.error_upper,
            "enclosure": list(section.enclosure),
            "recipe": section.to_payload()["numerics"],
            "chain": record,
        }
    )
    result["independent_certificate"] = independent_certificate(section.inputs, result)
    check_read(section.inputs, result)
    return result


def native_read(before):
    with capture_chains() as rows:
        section = rg.CandidateRG2bSection(before)
    point = CandidateCCurrent(
        replace(before, geometry=section.geometry, stage="rg2b_section")
    )
    b.require(len(rows) == 1, "read section count drift")
    return read_record(section, point, rows[0])


def check_read(before, value, *, numerics=False):
    b.check_digest({k: v for k, v in value.items() if k != "independent_certificate"})
    chart_record(before)
    b.require(
        all(0 <= Q(c) <= Q(9, 2) for c in before.current.C),
        "physical section query outside K",
    )
    b.require(
        before.current.W_A is None and before.current.Z_4 is None, "invented RG history"
    )
    work = chain(value)
    m = model(before)
    b.require(
        value["input_identity"] == before.identity
        and value["recipe"] == signed.APPROXIMATION
        and value["levels"] == 6
        and value["evaluations"] == 222,
        "section input/recipe/depth drift",
    )
    b.require(
        value["identity"]
        == "grcv4-rg2b-section-sha256:"
        + b.digest(
            {
                "numerics": signed.APPROXIMATION,
                "inputs": before.to_payload(),
                "differential_reference": None,
            }
        ),
        "section identity drift",
    )
    b.require(
        value["chain"]["input_identity"] == before.identity
        and value["chain"]["query"] == list(before.current.C)
        and np.array_equal(work.x[0], before.current.C)
        and len(work.x) == 7
        and len(work.h) == 7,
        "inverse chain query/depth drift",
    )
    for x in work.x:
        oracle.finite_array(x, (len(m.nodes),))
    for h in work.h:
        oracle.finite_array(h, m.I.shape)
        b.require(
            np.array_equal(h, h.T)
            and np.all(h[m.mask == 0] == 0)
            and infinity(IV.matrix(h.tolist()) - IV.matrix(m.I.tolist())) <= proof.RHO,
            "chain geometry symmetry/support/norm drift",
        )
    b.require(
        np.array_equal(work.h[-1], m.I) and np.array_equal(value["H"], work.h[0]),
        "chain terminal/selected geometry drift",
    )
    native_bounds = value["chain"]["native_chain_bounds"]
    cert = value["independent_certificate"]
    b.require(
        value["chain"]["native_global_digest"]
        == b.digest(global_record()["native_bounds"]),
        "global proof identity drift",
    )
    recalculated = oracle.chain_error_bounds(
        "C",
        6,
        Q(native_bounds["state_residual"]),
        Q(native_bounds["geometry_residual"]),
    )
    b.require(
        all(
            Q(native_bounds[k]) == recalculated[k]
            for k in ("state_error", "geometry_error", "truncation_error")
        ),
        "native chain error algebra drift",
    )
    b.require(
        Q(value["chain"]["native_chain_error"])
        == Q(native_bounds["geometry_error"]) + Q(native_bounds["truncation_error"])
        and Q(value["chain"]["native_chain_error"])
        <= Q(value["error_upper"])
        <= LIMITS["geometry_error"],
        "section error/tail budget drift",
    )
    b.require(
        Q(value["enclosure"][0]) == -Q(value["error_upper"])
        and Q(value["enclosure"][1]) == Q(value["error_upper"]),
        "section enclosure drift",
    )
    selected = replace(
        before,
        geometry=b.GRCV4Geometry(
            before.geometry.reference,
            b.OneFormHodge(
                before.geometry.reference.graph, tuple(map(tuple, value["H"]))
            ),
        ),
        stage="rg2b_section",
    )
    b.require(
        value["selected_inputs_identity"] == selected.identity
        and value["read_current"] == value["J"]
        and value["read_source"] == value["point_identity"],
        "selected Read-Back operand drift",
    )
    source = [
        [
            float(Q(1, 2**37) * Q(float(Q(float(m.mask[i, j])) * Q(x) * Q(y))))
            for j, y in enumerate(value["flat"])
        ]
        for i, x in enumerate(value["flat"])
    ]
    b.require(value["source"] == source, "signed flat/source assembly drift")
    b.require(
        cert["input_identity"] == before.identity
        and cert["selected_read_digest"] == value["record_digest"]
        and set(cert["bounds"]) == set(LIMITS) - {"resource_error"},
        "independent read binding drift",
    )
    b.require(
        all(0 <= Q(x) < LIMITS[k] for k, x in cert["bounds"].items()),
        "full read error budget unresolved",
    )
    cc = cert["chain"]
    levels = cert["level_residuals"]
    b.require(
        [x["level"] for x in levels] == list(range(1, 7))
        and max(Q(x["state_residual"]) for x in levels) == Q(cc["state_residual"])
        and max(Q(x["geometry_residual"]) for x in levels)
        == Q(cc["geometry_residual"]),
        "per-level residual binding drift",
    )
    recalc = oracle.chain_error_bounds(
        "C", 6, Q(cc["state_residual"]), Q(cc["geometry_residual"])
    )
    b.require(
        all(Q(cc[k]) == v for k, v in recalc.items())
        and Q(cc["input_error"]) == 0
        and Q(cc["total_error"])
        == recalc["geometry_error"] + recalc["truncation_error"]
        and Q(cc["total_error"]) < LIMITS["geometry_error"],
        "independent chain/tail/input error drift",
    )
    b.require(
        Q(cc["state_residual"]) <= Q(native_bounds["state_residual"])
        and Q(cc["geometry_residual"]) <= Q(native_bounds["geometry_residual"]),
        "native chain residual understates independent equations",
    )
    gb = proof.global_bounds("C")
    sb = proof.section_budgets(gb)
    expected_tail = (
        sb["inverse_lip"] * gb["A_H"] * sb["q_section"] ** 5 * sb["value_radius"]
    )
    b.require(
        Q(cert["first_inverse_tail"]) == expected_tail, "first predecessor tail drift"
    )
    expected_upper = {
        str(i): str(Q(value["chain"]["x"][1][i]) + Q(cc["state_error"]) + expected_tail)
        for i, c in enumerate(before.current.C)
        if c == 0
    }
    b.require(
        cert["zero_core_first_predecessor_upper"] == expected_upper,
        "signed predecessor bound drift",
    )
    if numerics:
        b.require(
            cert == independent_certificate(before, value),
            "independent section equations drift",
        )


def bridge(before, value):
    """Independent physical bridge and lagged invariance, with distinct norms."""
    high = IntervalRows(model(before))
    h = IV.matrix(value["read"]["H"])
    c = vector(before.current.C)
    actual = high.read("C", c, None, h)
    j_errors = [
        upper_abs(number(x) - y)
        for x, y in zip(value["read"]["J"], actual["J"], strict=True)
    ]
    je = endpoint(IV.sqrt(number(sum(x * x for x in j_errors))), 1)
    jn = endpoint(IV.sqrt(number(sum(upper_abs(x) ** 2 for x in actual["J"]))), 1)
    xe = infinity(
        vector(value["poststate"]["current"]["C"])
        - c
        + number(b.DT) * high.B * actual["J"]
    )
    he = infinity(
        IV.matrix(value["generated"]) - high.I - number(Q(1, 2)) * actual["source"]
    )
    bounds = proof.global_bounds("C")
    e = Q(value["read"]["independent_certificate"]["chain"]["total_error"])
    last = Q(value["restart"]["independent_certificate"]["chain"]["total_error"])
    bound = (
        last
        + he
        + Q(1, 2) * bounds["B_H"] * e
        + proof.SECTION_LIP * (xe + bounds["A_H"] * e)
    )
    residual = infinity(
        IV.matrix(value["restart"]["H"]) - IV.matrix(value["generated"])
    )
    exact = truth(before, value["read"])
    ce = full_error(
        value["poststate"]["current"]["C"],
        c - number(b.DT) * high.B * exact["read"]["J"],
    )
    return {
        k: str(v)
        for k, v in {
            "current_l2_error": je,
            "current_l2_upper": jn,
            "state_error": xe,
            "geometry_error": he,
            "invariance_residual": residual,
            "invariance_error_bound": bound,
            "resource_error": ce,
        }.items()
    }


def perform_step(before):
    with capture_chains() as rows:
        step = rg.ProvisionalCandidateRG2bStep(before)
    b.require(
        len(rows) == 3 and step.writer is None, "ordinary section count/history drift"
    )
    value = {
        "prestate": before.to_payload(),
        "poststate": step.next_inputs.to_payload(),
        "reset_read": read_record(step.reset_section, step.reset_point, rows[0]),
        "read": read_record(step.section, step.point, rows[1]),
        "restart": read_record(step.restart, step.restart_point, rows[2]),
        "generated": [list(row) for row in step.generated.one_form_hodge.matrix],
        "diagnostics": step.diagnostics.to_dict(),
    }
    value["independent_bridge"] = bridge(before, value)
    check_step(before, value)
    return value, step.next_inputs


def check_step(before, value, *, numerics=False):
    b.require(
        value["prestate"] == before.to_payload() and before.dt == b.DT,
        "step operand/beat drift",
    )
    b.require(
        all(0 <= Q(c) <= Q(17, 4) for role in ROLES for c in getattr(before, role).C),
        "ordinary current/reset outside K_minus",
    )
    after = b.GeometryStageInputs.from_payload(value["poststate"])
    expected = replace(
        before,
        current=replace(
            before.current, C=represented_continuity(before, value["read"]["J"])
        ),
        step_index=before.step_index + 1,
        time=float(Q(before.time) + Q(before.dt)),
    )
    b.require(after == expected, "continuity/clock/reset/single-write drift")
    check_read(before, value["read"], numerics=numerics)
    check_read(
        replace(before, current=before.reset), value["reset_read"], numerics=numerics
    )
    check_read(after, value["restart"], numerics=numerics)
    m = len(value["read"]["H"])
    generated = [
        [
            float(Q(i == j) + Q(1, 2) * Q(value["read"]["source"][i][j]))
            for j in range(m)
        ]
        for i in range(m)
    ]
    b.require(
        value["generated"] == generated,
        "generated geometry did not consume same read source",
    )
    diag = value["diagnostics"]
    independent = value["independent_bridge"]
    b.require(
        diag["regularity"] == "Lipschitz_only"
        and diag["continuity_evaluations"] == 1
        and diag["carrier_writes"] == 0
        and diag["section_error_upper"] == value["read"]["error_upper"],
        "ordinary stage counts drift",
    )
    b.require(
        all(Q(v) >= 0 for v in independent.values())
        and Q(independent["resource_error"]) < LIMITS["resource_error"]
        and Q(independent["invariance_residual"])
        <= Q(independent["invariance_error_bound"]),
        "independent invariance/resource error unresolved",
    )
    p = before.geometry.reference.profile.params_resolved.solver
    b.require(
        Q(independent["current_l2_error"])
        <= Q(p.absolute_tolerance)
        + Q(p.relative_tolerance) * Q(independent["current_l2_upper"])
        and Q(independent["geometry_error"]) <= LIMITS["geometry_error"]
        and proof.SECTION_LIP * Q(independent["state_error"])
        <= LIMITS["geometry_error"],
        "independent native arithmetic bridge unresolved",
    )
    b.require(
        Q(diag["invariance_residual"]) == Q(independent["invariance_residual"])
        and Q(diag["invariance_residual"]) <= Q(diag["invariance_error_bound"]),
        "native invariance residual/bound drift",
    )
    for key in ("current", "state", "geometry"):
        name = "current_l2_error" if key == "current" else key + "_error"
        b.require(
            Q(independent[name]) <= Q(diag["native_" + key + "_error"]),
            "native bridge understates independent error",
        )
    if numerics:
        b.require(independent == bridge(before, value), "bridge equations drift")
    return after


def effect_checks(before, value):
    exact = truth(before, value)
    m, high = exact["model"], exact["high"]
    c = np.asarray(before.current.C)
    h = np.asarray(value["H"])
    controls = {}
    for name in ("geometry", "feedback", "modulation"):
        actual = m.read("C", c.copy(), None, h.copy(), **{name: False})
        expected = high.read("C", vector(c), None, exact["H"], **{name: False})
        for field in ("J",) if name == "feedback" else ("J", "baseline"):
            controls[name + "_" + field] = separation(
                np.asarray(value[field]),
                actual[field],
                exact["read"][field],
                expected[field],
            )
    image = np.asarray(
        [
            [float(Q(i == j) + Q(1, 2) * Q(v)) for j, v in enumerate(row)]
            for i, row in enumerate(value["source"])
        ]
    )
    exact_image = high.I + number(Q(1, 2)) * exact["read"]["source"]
    controls["section_vs_instantaneous_image"] = separation(
        h.ravel(),
        image.ravel(),
        IV.matrix(list(exact["H"])),
        IV.matrix(list(exact_image)),
    )
    return controls


def check_effects(before, value, controls, *, numerics=False):
    b.require(
        set(controls)
        == {
            "geometry_J",
            "geometry_baseline",
            "feedback_J",
            "modulation_J",
            "modulation_baseline",
            "section_vs_instantaneous_image",
        }
        and all(
            x["minimum_margin_ratio"] > 1 and x["exact_effect_lower"] > 0
            for x in controls.values()
        ),
        "fixed-section effect unresolved",
    )
    if numerics:
        b.require(controls == effect_checks(before, value), "effect equations drift")


def run_source(manifest):
    initial = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    step, after = perform_step(initial)
    seed = replace(state(manifest["nominal_source"]), inputs=replace(after, dt=0))
    reads = {
        role: native_read(replace(seed.inputs, current=getattr(seed.inputs, role)))
        for role in ROLES
    }
    controls = {
        role: effect_checks(
            replace(seed.inputs, current=getattr(seed.inputs, role)), reads[role]
        )
        for role in ROLES
    }
    return {
        "source_step": step,
        "actual_source": seed.to_payload(),
        "source_reads": reads,
        "source_effects": controls,
    }, seed


def preflight(target):
    """Independent proposal trajectories precede native event/continuation."""
    out = {}
    for role in ROLES:
        c = np.asarray(getattr(target.inputs, role).C)
        m = model(target.inputs)
        rows = []
        for i in range(10):
            before = c.copy()
            c, _, truth_value = oracle.ordinary(m, "C", c)
            b.require(
                np.all(c >= 0) and np.all(c <= 4.25),
                "independent continuation leaves physical K_minus",
            )
            rows.append(
                {
                    "C": c.tolist(),
                    "entry_C": before.tolist(),
                    "section_error": str(truth_value["certificate"]["total_error"]),
                    "current_error": str(truth_value["current_error"]),
                    "resource_error": str(truth_value["resource_error"]),
                }
            )
        out[role] = rows
    return out


def event_capture(seed, request):
    owner = native.GRC9V4CRG2bOperation(seed)
    initial = json.loads(owner.checkpoint())
    reads = []
    publication = []
    detections = []
    real_readmit = native._crg2b_readmit
    real_section = rg.CandidateRG2bSection
    real_point = native.CandidateCCurrent
    real_receipts = native.make_commit_receipts
    real_detection = native.GRC9V4CandidateDetection

    def observed_readmit(subject):
        sections = []
        points = []

        def section(*args, **kwargs):
            result = real_section(*args, **kwargs)
            sections.append(result)
            return result

        def point(*args, **kwargs):
            result = real_point(*args, **kwargs)
            if result.inputs.stage == "rg2b_section":
                points.append(result)
            return result

        with (
            capture_chains() as rows,
            patch.object(rg, "CandidateRG2bSection", section),
            patch.object(native, "CandidateCCurrent", point),
        ):
            result = real_readmit(subject)
        b.require(
            len(rows) == len(points) == len(sections) == 2,
            "both-role event section count drift",
        )
        a, z = (
            read_record(ss, pp, cc)
            for ss, pp, cc in zip(sections, points, rows, strict=True)
        )
        reads.append(
            {
                "inputs": subject.inputs.to_payload(),
                "read": a,
                "reset_read": z,
                "published_state": owner.state.scientific_digest,
            }
        )
        return result

    def observed_receipts(*args, **kwargs):
        publication.append(
            {
                "admission_pairs": len(reads),
                "published_state": owner.state.scientific_digest,
            }
        )
        return real_receipts(*args, **kwargs)

    def observed_detection(postbeat, policy):
        result = real_detection(postbeat, policy)
        detections.append(
            {
                "identity": result.identity,
                "row_inputs_identity": postbeat.identity,
                "current": list(postbeat.physical_current),
                "candidate_node_ids": list(result.candidate_node_ids()),
                "published_state": owner.state.scientific_digest,
            }
        )
        return result

    forbidden = AssertionError("event must not execute ordinary/CI/OS/writer work")
    with (
        patch.object(native, "_crg2b_readmit", observed_readmit),
        patch.object(native, "make_commit_receipts", observed_receipts),
        patch.object(native, "GRC9V4CandidateDetection", observed_detection),
        patch.object(rg, "ProvisionalCandidateRG2bStep", side_effect=forbidden),
        patch.object(native, "ProvisionalCandidateCIStep", side_effect=forbidden),
        patch.object(native, "CandidateCOSPass", side_effect=forbidden),
    ):
        outcome = owner.expand(request)
    value = {
        "source_checkpoint": initial,
        "admission_reads": reads,
        "publication": publication,
        "detections": detections,
        "checkpoint": json.loads(owner.checkpoint()),
        "actual_target": owner.state.to_payload(),
        "receipts": [r.to_payload() for r in outcome.emitted_receipts],
        "failure": None if outcome.committed else outcome.failure.to_payload(),
        "replay_identical": False,
    }
    if outcome.committed:
        value["replay_identical"] = (
            native.GRC9V4CRG2bOperation.replay(owner.checkpoint()).checkpoint()
            == owner.checkpoint()
        )
    return owner, outcome, value


def check_event(seed, case, value, *, numerics=False):
    expected = b.independent_target({"expected_source": seed.to_payload()}, case)
    target = replace(seed, inputs=expected)
    b.require(
        value["actual_target"] == target.to_payload(),
        "independent graph/reference/resource transfer drift",
    )
    b.require(len(value["admission_reads"]) == 2, "missing source/target admission")
    for parent, observed in zip((seed, target), value["admission_reads"], strict=True):
        b.require(
            observed["inputs"] == parent.inputs.to_payload()
            and observed["published_state"] == seed.scientific_digest,
            "admission operand/publication drift",
        )
        check_read(parent.inputs, observed["read"], numerics=numerics)
        check_read(
            replace(parent.inputs, current=parent.inputs.reset),
            observed["reset_read"],
            numerics=numerics,
        )
    detection = value["detections"]
    b.require(
        len(detection) == 1
        and detection[0]["current"] == value["admission_reads"][0]["read"]["J"]
        and case["request"]["source_node_id"] in detection[0]["candidate_node_ids"]
        and detection[0]["published_state"] == seed.scientific_digest,
        "fresh trigger/current binding drift",
    )
    b.require(
        value["publication"]
        == [{"admission_pairs": 2, "published_state": seed.scientific_digest}],
        "publication preceded both-role admission",
    )
    cp = value["checkpoint"]
    b.require(
        cp["initial"] == seed.to_payload()
        and cp["state"] == target.to_payload()
        and cp["requests"] == [case["request"]]
        and cp["receipts"] == value["receipts"],
        "checkpoint drift",
    )
    refs = cp["reference_currents"]
    source_ref, target_ref = (
        seed.inputs.geometry.reference,
        target.inputs.geometry.reference,
    )
    b.require(
        len(refs) == 1
        and refs[0]["event_id"] == case["oracle"]["event_id"]
        and refs[0]["source_graph_digest"] == source_ref.graph.graph_digest
        and refs[0]["target_graph_digest"] == target_ref.graph.graph_digest,
        "reference lineage identity drift",
    )
    for role, key in (("current", "read"), ("reset", "reset_read")):
        old = value["admission_reads"][0][key]["J"]
        currents = dict(zip(source_ref.graph.live_edge_ids, old, strict=True))
        expected_j = [currents.get(e, 0.0) for e in target_ref.graph.live_edge_ids]
        b.require(
            refs[0]["roles"][role] == {"source": old, "target": expected_j},
            "reference current map drift",
        )
        b.require(
            sum(map(Q, getattr(seed.inputs, role).C))
            == sum(map(Q, getattr(target.inputs, role).C)),
            "exact event charge changed",
        )
    receipts = value["receipts"]
    b.require(len(receipts) == 4, "event receipt count drift")
    _, checked = native.make_commit_receipts(
        [r["identity_payload"] for r in receipts],
        operation_id=case["request"]["operation_id"],
        source_state_digest=seed.scientific_digest,
        target_state_digest=target.scientific_digest,
        target_step_index=target.inputs.step_index,
        target_time=target.inputs.time,
    )
    b.require(
        [r.to_payload() for r in checked] == receipts
        and cp["lifecycle_digest"] == target.lifecycle_digest(checked),
        "receipt/commit digest drift",
    )
    first = receipts[0]["identity_payload"]
    b.require(
        first["event_id"] == case["oracle"]["event_id"]
        and first["core"]["information_losses"] == [],
        "event/loss drift",
    )
    for channel, disposition in (
        ("candidate", "rederived"),
        ("carrier", "not_applicable"),
    ):
        b.require(
            first["history"][channel]
            == {
                "subject": channel,
                "disposition": disposition,
                "source_history_digest": None,
                "target_history_digest": None,
                "information_loss": "none",
            },
            "C_RG2b history receipt drift",
        )
    b.require(
        value["failure"] is None and value["replay_identical"] is True,
        "event/replay incomplete",
    )
    b.require(
        "carrier_archives" not in cp
        and all(
            getattr(target.inputs, r).W_A is None
            and getattr(target.inputs, r).Z_4 is None
            for r in ROLES
        ),
        "invented RG persistent history",
    )
    return target


def execute_case(seed, original):
    case = bind_case(seed, original)
    row = {
        "case_id": case["case_id"],
        "input_digest": b.digest(original),
        "executed_case": case,
        "coverage_binding": case["coverage_binding"],
        "family": "C_RG2b",
        "outcome": "incomplete_case",
        "case_passed": False,
        "event_committed": False,
        "first_failure": None,
        "continuation": [],
        "final_reads": {},
        "entry_effects": {},
        "final_effects": {},
        "user_accepted": False,
        "aggregate_closed": False,
    }
    stage, role, index = "independent_preflight", "both", 0
    start = time.monotonic()
    try:
        with b.budget(case["execution_budget_seconds"]):
            expected = replace(
                seed,
                inputs=b.independent_target(
                    {"expected_source": seed.to_payload()}, case
                ),
            )
            row["predictions"] = preflight(expected)
            stage = "event"
            _owner, outcome, event = event_capture(
                seed, b.GRC9V4ExpansionRequestInput.from_payload(case["request"])
            )
            row.update(event=event, event_committed=outcome.committed)
            b.require(
                outcome.committed, "native event rejected: " + str(event["failure"])
            )
            target = check_event(seed, case, event)
            for role in ROLES:
                before = replace(
                    target.inputs, current=getattr(target.inputs, role), dt=b.DT
                )
                stage = "target_continuation"
                for index in range(1, 11):
                    step, following = perform_step(before)
                    if index == 1:
                        row["entry_effects"][role] = effect_checks(before, step["read"])
                        first = step["read"]["independent_certificate"][
                            "zero_core_first_predecessor_upper"
                        ]
                        b.require(
                            first and any(Q(v) < 0 for v in first.values()),
                            "negative signed first predecessor not resolved",
                        )
                    prediction = row["predictions"][role][index - 1]
                    error = max(
                        abs(Q(x) - Q(y))
                        for x, y in zip(
                            prediction["C"], following.current.C, strict=True
                        )
                    )
                    b.require(
                        error < Q(1, 2**39), "independent nominal trajectory mismatch"
                    )
                    row["continuation"].append(
                        {
                            "role": role,
                            "index": index,
                            "step": step,
                            "nominal_resource_error": str(error),
                        }
                    )
                    before = following
                stage = "final_read"
                row["final_reads"][role] = native_read(replace(before, dt=0))
                row["final_effects"][role] = effect_checks(
                    replace(before, dt=0), row["final_reads"][role]
                )
            row.update(outcome="passed_named_case", case_passed=True)
    except Exception as exc:  # noqa: BLE001 - retain every failed campaign case
        row["first_failure"] = {
            "stage": stage,
            "role": role,
            "index": index,
            "kind": type(exc).__name__,
            "message": str(exc),
        }
    row["elapsed_seconds"] = time.monotonic() - start
    return row


def validate(manifest, result, *, numerics=False):
    b.check_digest(result)
    b.require(
        result["manifest_digest"] == manifest["record_digest"]
        and result["native_runtime_executed"] is True
        and result["user_accepted"] is False
        and result["aggregate_closed"] is False,
        "runtime binding/scope drift",
    )
    shared = result["shared"]
    initial = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    after = check_step(initial, shared["source_step"], numerics=numerics)
    seed = state(shared["actual_source"])
    b.require(
        seed == replace(state(manifest["nominal_source"]), inputs=replace(after, dt=0)),
        "source schedule drift",
    )
    for role in ROLES:
        entry = replace(seed.inputs, current=getattr(seed.inputs, role))
        check_read(entry, shared["source_reads"][role], numerics=numerics)
        check_effects(
            entry,
            shared["source_reads"][role],
            shared["source_effects"][role],
            numerics=numerics,
        )
    b.require(
        [r["case_id"] for r in result["cases"]]
        == [c["case_id"] for c in manifest["cases"]],
        "case roster drift",
    )
    passed = 0
    for original, row in zip(manifest["cases"], result["cases"], strict=True):
        case = bind_case(seed, original)
        b.require(
            row["input_digest"] == b.digest(original)
            and row["executed_case"] == case
            and row["coverage_binding"] == case["coverage_binding"]
            and row["user_accepted"] is False
            and row["aggregate_closed"] is False,
            "case input/scope drift",
        )
        if not row["case_passed"]:
            b.require(
                row["outcome"] == "incomplete_case"
                and row["first_failure"] is not None,
                "incomplete case overclaim",
            )
            continue
        b.require(
            row["outcome"] == "passed_named_case"
            and row["event_committed"] is True
            and row["first_failure"] is None,
            "false success",
        )
        target = check_event(seed, case, row["event"], numerics=numerics)
        b.require(
            [(v["role"], v["index"]) for v in row["continuation"]]
            == [(r, i) for r in ROLES for i in range(1, 11)]
            and set(row["final_reads"]) == set(ROLES),
            "both-role schedule incomplete",
        )
        if numerics:
            b.require(
                row["predictions"] == preflight(target),
                "independent preflight equations drift",
            )
        for role in ROLES:
            before = replace(
                target.inputs, current=getattr(target.inputs, role), dt=b.DT
            )
            for entry in (x for x in row["continuation"] if x["role"] == role):
                if entry["index"] == 1:
                    check_effects(
                        before,
                        entry["step"]["read"],
                        row["entry_effects"][role],
                        numerics=numerics,
                    )
                    first = entry["step"]["read"]["independent_certificate"][
                        "zero_core_first_predecessor_upper"
                    ]
                    b.require(
                        first and any(Q(v) < 0 for v in first.values()),
                        "signed predecessor effect unresolved",
                    )
                before = check_step(before, entry["step"], numerics=numerics)
                prediction = row["predictions"][role][entry["index"] - 1]
                error = max(
                    abs(Q(x) - Q(y))
                    for x, y in zip(prediction["C"], before.current.C, strict=True)
                )
                b.require(
                    error == Q(entry["nominal_resource_error"]) and error < Q(1, 2**39),
                    "nominal resource comparison drift",
                )
                last = entry["step"]["restart"]
            final = replace(before, dt=0)
            observed = row["final_reads"][role]
            check_read(final, observed, numerics=numerics)
            for key in ("H", "J", "baseline", "readback", "flat", "source"):
                b.require(
                    observed[key] == last[key],
                    "fresh deterministic section/restart mismatch",
                )
            check_effects(
                final, observed, row["final_effects"][role], numerics=numerics
            )
        passed += 1
    return {
        "retained_integrity": "passed",
        "cases_passed": passed,
        "cases_required": len(manifest["cases"]),
        "successful_history_cells": 2 * passed,
        "native_trajectories_rerun": False,
        "interval_equations_recomputed": numerics,
        "user_accepted": False,
        "aggregate_closed": False,
    }


def write_new(name, value):
    path = b.ROOT / name
    with path.open("x") as out:
        out.write(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--manifest", default=INPUTS)
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    b.require(
        not args.recheck_numerics or args.check_retained,
        "recheck requires retained mode",
    )
    for name in (args.manifest, args.output):
        b.require(
            not Path(name).is_absolute() and ".." not in Path(name).parts,
            "repository-relative path required",
        )
    if args.prepare:
        write_new(args.manifest, make_manifest())
        print("C_RG2b inputs bound; no native execution")
        return
    manifest = b.read(args.manifest)
    check_manifest(manifest)
    if args.check_retained:
        print(
            json.dumps(
                validate(manifest, b.read(args.output), numerics=args.recheck_numerics),
                indent=2,
            )
        )
        return
    b.require(
        not (b.ROOT / args.output).exists(), "refusing to overwrite native evidence"
    )
    journal = b.ROOT / (args.output + ".progress.jsonl")
    b.require(not journal.exists(), "existing progress requires explicit recovery")
    with b.exact_backend(b.ExactBackend.FLINT):
        shared, seed = run_source(manifest)
        results = {
            "schema": "p984b-crg2b-runtime-results-v1",
            "manifest_digest": manifest["record_digest"],
            "environment": {
                "python": platform.python_version(),
                "numpy": version("numpy"),
                "mpmath": version("mpmath"),
                "python_flint": version("python-flint"),
            },
            "shared": shared,
            "cases": [],
            "native_runtime_executed": True,
            "user_accepted": False,
            "aggregate_closed": False,
        }
        with journal.open("x") as progress:
            progress.write(b.canonical_json_bytes(b.seal(results)).decode() + "\n")
            progress.flush()
            for case in manifest["cases"]:
                row = execute_case(seed, case)
                progress.write(b.canonical_json_bytes(b.seal(row)).decode() + "\n")
                progress.flush()
                results["cases"].append(row)
                print(
                    case["fixture_id"], row["outcome"], row["first_failure"], flush=True
                )
                if not row["case_passed"]:
                    break
    results = b.seal(results)
    # Never publish an incomplete roster as a completed campaign.
    write_new(args.output, results)
    report = validate(manifest, results)
    b.require(report["cases_passed"] == 16, "campaign contains incomplete cases")
    journal.unlink()
    print(json.dumps({**report, "native_execution_in_this_command": True}, indent=2))


if __name__ == "__main__":
    main()
