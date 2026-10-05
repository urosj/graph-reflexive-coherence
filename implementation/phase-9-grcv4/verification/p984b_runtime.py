"""Bounded P9-8.4b runner: frozen mechanics and separately named live cases.

The shared capture/comparison contract currently has a C_OS adapter. Other
families remain explicit pending rows, never successes inferred from C_OS.
No production module or accepted predecessor record is rewritten.
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
from unittest.mock import patch
import platform
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
for directory in (ROOT, ROOT / "src"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import numpy as np

from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_9_v4_expansion import (
    GRC9ExpansionPolicy,
    GRC9V4ExpansionPlan,
    GRC9V4ExpansionRequestInput,
)
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import (
    GeometryStageInputs,
    GRCV4Geometry,
    GRCV4Graph,
    GRCV4ReferenceGeometry,
    OneFormHodge,
)
from pygrc.models.grc_v4_profile import resolve_profile
from pygrc.models.grc_v4_realizations import CandidateCOSPass
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ProvisionalCandidateCOSStep
from tests.models.test_grc_v4_candidate_c import dense_current_oracle

BASE = "implementation/phase-9-grcv4/tranche-8/"
COVERAGE = BASE + "P9-8.4a-Coverage.json"
SEEDS = BASE + "P9-8.3-CatalogSmallCInputs.json"
VECTORS = "specs/grc-v4-conformance-vectors.json"
HERE = "implementation/phase-9-grcv4/verification/"
SELF = HERE + "p984b_runtime.py"
INPUTS = BASE + "P9-8.4b-COSCases.json"
RESULTS = BASE + "P9-8.4b-COSResults.json"
PINNED = "G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-3"
DT = 1 / 4096
STAGES = (
    "source_admission",
    "source_schedule",
    "fresh_trigger_request",
    "mechanical_history_transfer",
    "target_readmission",
    "receipt_publication",
    "target_continuation",
    "final_read",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads((ROOT / path).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(canonical_json_bytes(value))


def authority_payload(state):
    return {
        "C": list(state.C),
        "W_A": None if state.W_A is None else list(state.W_A),
        "Z_4": None if state.Z_4 is None else list(state.Z_4),
    }


def seal(value):
    value = deepcopy(value)
    value.pop("record_digest", None)
    return {**value, "record_digest": digest(value)}


def check_digest(value):
    require(value == seal(value), "record digest mismatch")


def bind(paths):
    return [
        {"path": p, "sha256": sha((ROOT / p).read_bytes())} for p in sorted(set(paths))
    ]


def check_bindings(rows):
    require(len(rows) == len({r["path"] for r in rows}), "duplicate bindings")
    for row in rows:
        path = Path(row["path"])
        require(
            not path.is_absolute() and ".." not in path.parts, "nonportable binding"
        )
        require(
            sha((ROOT / path).read_bytes()) == row["sha256"],
            "source drift: " + str(path),
        )


def construction_oracle(vector, request, specialization):
    """Rebind the frozen expected graph, never call the production allocator.

    The explicit bijection is outside-p -> integer p, old-p -> ep, source-s
    -> s, and old event namespace -> independently hashed new namespace.
    All ports, kinds, orientations and branch/rotor structure are preserved.
    """
    identity = deepcopy(vector["event_identity_payload"])
    for key in identity:
        if key in request and key != "schema_version":
            identity[key] = request[key]
    policy = specialization["resolved"]["expansion"]
    identity.update(
        bond_seed=policy["bond_seed"],
        expansion_policy_digest=payload_identity(
            "expansion_policy_identity_payload",
            {"schema_version": "grc9v4-expansion-policy-identity-v1", "policy": policy},
        ),
    )
    for channel in ("candidate", "carrier"):
        field = channel + "_history_policy_digest"
        identity[field] = request["history_policy"][field]
    event = "grc-event-sha256:" + digest(identity)
    old_event = vector["expected"]["event_id"]

    def rename(value):
        if value.startswith(old_event + "/"):
            return event + value[len(old_event) :]
        if value.startswith("outside-"):
            return int(value.removeprefix("outside-"))
        if value.startswith("old-"):
            return "e" + value.removeprefix("old-")
        raise ValueError("unbound frozen name: " + value)

    graph = deepcopy(vector["expected"]["identity_payloads"]["target_graph"])
    graph["live_node_ids"] = sorted(
        map(rename, graph["live_node_ids"]),
        key=lambda n: (type(n) is str, canonical_json_bytes(n)),
    )
    for edge in graph["edges"]:
        edge["edge_id"] = rename(edge["edge_id"])
        for end in ("tail", "head"):
            edge[end]["node_id"] = rename(edge[end]["node_id"])
    graph["edges"].sort(key=lambda e: e["edge_id"].encode("utf-16-be"))
    return {"event_identity": identity, "event_id": event, "target_graph": graph}


def make_manifest():
    coverage = read(COVERAGE)
    check_digest(coverage)
    check_bindings(coverage["source_bindings"])
    seed = read(SEEDS)["states"]["C_OS"]
    initial = GeometryStageInputs.from_payload(seed["source"]["inputs"])
    initial = replace(
        initial,
        current=GRCV4AuthoritativeState((3.0, *((193 / 64,) * 9)), None, None),
        step_index=0,
        time=0,
        dt=DT,
    )
    cases = []
    for vector in read(VECTORS)["grc9_expansion_vectors"]:
        if (
            next(
                v
                for v in coverage["fixture_inventory"]
                if v["id"] == vector["fixture_id"]
            )["literal_family"]
            != "C_OS"
        ):
            # The seventeenth fixture is the literal C_PC reset subject.
            continue
        request = deepcopy(seed["request"])
        for field in ("target_effective_degree", "module_chirality", "growth_phase"):
            request[field] = vector["request"][field]
        if vector["fixture_id"] != PINNED:
            request["operation_id"] = "p984b-cos-" + vector["fixture_id"]
        case = {
            "case_id": "P984B-COS-" + vector["fixture_id"],
            "fixture_id": vector["fixture_id"],
            "family": "C_OS",
            "subject_kind": "native_companion",
            "coverage_binding": {
                "record_digest": coverage["record_digest"],
                "cell_ids": [
                    vector["fixture_id"] + "::C_OS::" + r for r in ("current", "reset")
                ],
            },
            "request": request,
            "oracle": construction_oracle(
                vector, request, seed["source"]["specialization"]
            ),
            "schedule": {
                "source_current_beats": 1,
                "source_reset_beats": 0,
                "target_beats_per_role": 10,
                "dt": DT,
                "final_read": True,
            },
            "comparison": {
                "kind": "bounded_independent_dense_crosscheck_not_certified_full_error",
                "norm": "componentwise_abs_plus_relative",
                "atol": 2e-13,
                "rtol": 2e-13,
                "quantities": [
                    "C",
                    "predictor_J",
                    "predictor_readback",
                    "H",
                    "corrector_J",
                    "corrector_readback",
                ],
                "roles": ["current", "reset"],
                "stages": [
                    "source_schedule",
                    "target_readmission",
                    "target_continuation",
                    "final_read",
                ],
                "domain": "this_named_graph_and_reference_only; native_strict_selector_OS_split_charge_at_each_executed_stage",
                "precision": "binary64_dense; exact_dyadic_continuity; FLINT_native",
                "oracle": "dense_current_oracle + independent OS assembly/continuity in p984b_runtime.py",
                "effect_claim": False,
            },
            "execution_budget_seconds": 120,
            "literal_identity_replay": False,
            "changes_from_frozen": [
                "source_labels",
                "profile_cutoff_and_couplings",
                "source_histories",
                "specialization_and_bond_seed",
                "event_and_target_identities",
            ],
        }
        cases.append(case)
    require(len(cases) == 16, "expected sixteen C_OS companions")
    rows = [
        {
            "cell_id": row["id"],
            "family": row["family"],
            "role": row["role"],
            "fixture_id": row["fixture_id"],
            "disposition": "scheduled_C_OS_companion"
            if row["family"] == "C_OS"
            else "pending_family_adapter_and_case_prerequisites",
            "required": coverage["families"][row["family"]]["prerequisites"],
        }
        for row in coverage["coverage_cells"]
        if row["owner"] == "P9-8.4b" and row["applicable"]
    ]
    paths = [
        COVERAGE,
        SEEDS,
        VECTORS,
        SELF,
        HERE + "test_p984b_runtime.py",
        "pyproject.toml",
    ]
    paths += [
        str(p.relative_to(ROOT))
        for pattern in (
            "src/pygrc/models/grc*v4*.py",
            "src/pygrc/models/grc_v4_assets/*.json",
            "tests/models/test_grc_v4*.py",
        )
        for p in ROOT.glob(pattern)
    ]
    return seal(
        {
            "schema": "p984b-cos-case-manifest-v1",
            "source_bindings": bind(paths),
            "initial_inputs": initial.to_payload(),
            "expected_source": seed["source"],
            "cases": cases,
            "coverage_rows": rows,
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )


def independent_target(manifest, case):
    """Complete target reference and both affine resource images before runtime."""
    source = GeometryStageInputs.from_payload(manifest["expected_source"]["inputs"])
    graph = GRCV4Graph.from_payload(case["oracle"]["target_graph"])
    weights = {edge: 1 for edge in graph.live_edge_ids}
    ref = source.geometry.reference
    params = ref.profile.params_resolved.to_payload()
    params["candidate"]["W_C_tr"] = weights
    params["candidate"]["W_C_tr_content_digest"] = payload_identity(
        "wctr_identity_payload",
        {"schema_version": "grcv4-wctr-identity-v1", "W_C_tr": weights},
    )
    params["geometry"]["reference_hodge_digest"] = payload_identity(
        "reference_hodge_identity_payload",
        {
            "schema_version": "grcv4-reference-hodge-identity-v1",
            "edge_weights": weights,
        },
    )
    base = tuple((0.0,) * len(weights) for _ in weights)
    params["geometry"]["K4_base_digest"] = payload_identity(
        "k4_identity_payload",
        {"schema_version": "grcv4-k4-identity-v1", "K4_base": [list(r) for r in base]},
    )
    identity = ref.profile.identity_payload.to_payload()
    identity["params_hash"] = payload_identity("resolved_params", params)
    target = GRCV4ReferenceGeometry(
        graph,
        resolve_profile(params, identity),
        ref.context,
        base,
        FrozenJSONMap(weights),
    )
    states = {}
    for role in ("current", "reset"):
        old = dict(zip(ref.graph.live_node_ids, getattr(source, role).C, strict=True))
        image = {n: old.get(n, 0.0) for n in graph.live_node_ids}
        for b, share in enumerate(case["request"]["resource_distribution"], 1):
            image[case["oracle"]["event_id"] + f"/satellite/{b}"] = float(
                Fraction(old["s"]) * Fraction(share)
            )
        states[role] = GRCV4AuthoritativeState(
            tuple(image[n] for n in graph.live_node_ids), None, None
        )
    return replace(
        source,
        geometry=target.geometry(),
        **states,
        operation_id=case["request"]["operation_id"],
        dt=0,
    )


def dense_os(inputs):
    """Independent stage equations; never consume a native current or geometry."""
    first = dense_current_oracle(inputs)
    ref = inputs.geometry.reference
    b = np.asarray(ref.graph.incidence)
    overlap = abs(b).T @ abs(b) / 2
    lowered = np.linalg.solve(
        np.asarray(inputs.geometry.one_form_hodge.matrix), first["read"]
    )
    assembly = np.array(
        [
            [
                float(Fraction(float(w)) * Fraction(float(x)) * Fraction(float(y)))
                for w, y in zip(row, lowered, strict=True)
            ]
            for row, x in zip(overlap, lowered, strict=True)
        ]
    )
    h = np.asarray(
        ref.pairings.one_form.matrix
    ) + ref.profile.params_resolved.geometry.kappa_H * (
        ref.profile.params_resolved.candidate.zeta_C * assembly
    )
    second = dense_current_oracle(
        replace(
            inputs,
            geometry=GRCV4Geometry(ref, OneFormHodge(ref.graph, tuple(map(tuple, h)))),
        )
    )
    c = np.array(
        [
            float(
                Fraction(c0)
                - Fraction(inputs.dt)
                * sum(
                    (
                        Fraction(float(a)) * Fraction(float(j))
                        for a, j in zip(row, second["current"], strict=True)
                    ),
                    Fraction(),
                )
            )
            for c0, row in zip(inputs.current.C, b, strict=True)
        ]
    )
    return {
        "C": c,
        "predictor_J": first["current"],
        "predictor_readback": first["read"],
        "H": h,
        "corrector_J": second["current"],
        "corrector_readback": second["read"],
    }


def comparison(actual, expected, policy, name):
    a, b = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
    require(a.shape == b.shape and a.size > 0, "shape mismatch: " + name)
    require(
        np.isfinite(a).all() and np.isfinite(b).all(), "nonfinite comparison: " + name
    )
    require(
        policy["norm"] == "componentwise_abs_plus_relative", "unbound comparison norm"
    )
    atol, rtol = policy["atol"], policy["rtol"]
    require(
        type(atol) in (int, float)
        and type(rtol) in (int, float)
        and np.isfinite([atol, rtol]).all()
        and min(atol, rtol) >= 0,
        "invalid comparison budget",
    )
    error, allowance = abs(a - b), atol + rtol * abs(b)
    require((error <= allowance).all(), "independent comparison failed: " + name)
    return {
        "quantity": name,
        "norm": policy["norm"],
        "atol": atol,
        "rtol": rtol,
        "actual": a.tolist(),
        "expected": b.tolist(),
        "maximum_error": float(error.max()),
        "passed": True,
        "certified_full_error": False,
    }


def compare_pass(passed, expected, policy):
    values = {
        "predictor_J": passed.predictor.current.values,
        "predictor_readback": passed.predictor.read.flux.values,
        "H": passed.corrector.inputs.geometry.one_form_hodge.matrix,
        "corrector_J": passed.corrector.current.values,
        "corrector_readback": passed.corrector.read.flux.values,
    }
    return [
        comparison(value, expected[key], policy, key) for key, value in values.items()
    ]


class BudgetExpired(TimeoutError):
    pass


@contextmanager
def budget(seconds):
    def expired(*_):
        raise BudgetExpired("case operational budget exhausted")

    prior = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, prior)


def execute_cos(manifest, case):
    start = time.monotonic()
    rows = [
        {"role": r, "stage": s, "outcome": "not_run"}
        for s in STAGES
        for r in ("current", "reset")
    ]
    result = {
        "case_id": case["case_id"],
        "input_digest": digest(case),
        "coverage_binding": case["coverage_binding"],
        "family": "C_OS",
        "stages": rows,
        "observations": [],
        "event_committed": False,
        "first_failure": None,
        "user_accepted": False,
        "aggregate_closed": False,
    }
    owner = None
    stage, role = "source_admission", "both"

    def mark(s, r, **details):
        row = next(x for x in rows if x["stage"] == s and x["role"] == r)
        row.update(outcome="passed_named_stage", **details)

    try:
        with (
            budget(case["execution_budget_seconds"]),
            exact_backend(ExactBackend.FLINT),
        ):
            # Complete independent construction is bound before executing the subject.
            expected_target = independent_target(manifest, case)
            result["independent_target"] = expected_target.to_payload()
            inputs = GeometryStageInputs.from_payload(manifest["initial_inputs"])
            spec = manifest["expected_source"]["specialization"]
            specialization = native.GRC9V4Specialization(
                FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])
            )
            native.GRC9V4COSOperation(
                native.GRC9V4COSState(replace(inputs, dt=0), specialization)
            )
            for role in ("current", "reset"):
                mark(stage, role)
            stage, role = "source_schedule", "current"
            expected = dense_os(inputs)
            step = ProvisionalCandidateCOSStep(inputs)
            checks = compare_pass(step.os_pass, expected, case["comparison"])
            checks.append(
                comparison(
                    step.next_inputs.current.C, expected["C"], case["comparison"], "C"
                )
            )
            require(
                step.next_inputs.reset == inputs.reset,
                "reset changed during source beat",
            )
            require(
                (step.next_inputs.step_index, step.next_inputs.time) == (1, DT),
                "source clock/write count",
            )
            seed = native.GRC9V4COSState(
                replace(step.next_inputs, dt=0), specialization
            )
            require(
                seed.to_payload() == manifest["expected_source"],
                "source no longer matches bound actual postbeat identity",
            )
            result["actual_source"] = seed.to_payload()
            result["observations"].append(
                {"stage": stage, "role": role, "comparisons": checks}
            )
            mark(stage, "current", beats=1)
            mark(stage, "reset", beats=0, preserved=True)
            stage, role = "fresh_trigger_request", "both"
            request = GRC9V4ExpansionRequestInput.from_payload(case["request"])
            require(
                request.source_state_digest == seed.scientific_digest
                and request.expected_event_id is None
                and request.expected_target_graph_digest is None,
                "request is stale or receives oracle authority",
            )
            graph = seed.inputs.geometry.reference.graph.port_graph
            detection = native.GRC9V4CandidateDetection(
                native.GRC9V4PostbeatRows(
                    graph,
                    seed.inputs.geometry.reference.profile,
                    seed.inputs.current,
                    native.CandidateCCurrent(seed.inputs).current.values,
                    seed.inputs.step_index,
                    specialization.identity_payload["hessian_sign"],
                ),
                native.GRC9SparkPolicy.from_payload(specialization.resolved["spark"]),
            )
            require(
                request.source_node_id in detection.candidate_node_ids(),
                "not a fresh candidate",
            )
            result["actual_request"] = request.to_payload()
            result["candidate_nodes"] = list(detection.candidate_node_ids())
            for role in ("current", "reset"):
                mark(stage, role)
            stage, role = "mechanical_history_transfer", "both"
            owner = native.GRC9V4COSOperation(seed)
            observed_reads = []

            def observed_surface(operand):
                # Observe actual production admission operands, not fabricated stage flags.
                point = CandidateCOSPass(operand)
                observed_reads.append(
                    {
                        "graph": operand.geometry.reference.graph.graph_digest,
                        "authority": authority_payload(operand.current),
                        "published_state": owner.state.scientific_digest,
                        "split_admitted": point.residual.admitted,
                    }
                )
                return point

            with patch.object(native, "CandidateCOSPass", observed_surface):
                outcome = owner.expand(request)
            result["actual_admission_reads"] = observed_reads
            result["event_committed"] = outcome.committed
            if not outcome.committed:
                result["native_failure"] = outcome.failure.to_payload()
                raise ValueError("native event rejected: " + outcome.failure.message)
            actual = owner.state.inputs
            require(
                actual.geometry.reference.to_payload()
                == expected_target.geometry.reference.to_payload(),
                "independent target reference mismatch",
            )
            require(
                actual.current == expected_target.current
                and actual.reset == expected_target.reset,
                "independent role transfer mismatch",
            )
            required_reads = [
                (
                    seed.inputs.geometry.reference.graph.graph_digest,
                    authority_payload(getattr(seed.inputs, r)),
                )
                for r in ("current", "reset")
            ]
            required_reads += [
                (
                    expected_target.geometry.reference.graph.graph_digest,
                    authority_payload(getattr(expected_target, r)),
                )
                for r in ("current", "reset")
            ]
            require(
                [(r["graph"], r["authority"]) for r in observed_reads]
                == required_reads,
                "missing/foreign actual admission operand",
            )
            require(
                all(
                    r["published_state"] == seed.scientific_digest
                    and r["split_admitted"]
                    for r in observed_reads
                ),
                "admission not before publication",
            )
            for role in ("current", "reset"):
                require(
                    sum(map(Fraction, getattr(actual, role).C))
                    == sum(map(Fraction, getattr(seed.inputs, role).C)),
                    "exact event charge changed",
                )
                mark(stage, role)
                mark(
                    "target_readmission",
                    role,
                    evidence="native expand calls complete OS admission for both roles before commit",
                )
            stage, role = "receipt_publication", "both"
            receipts = [r.to_payload() for r in outcome.emitted_receipts]
            primary = outcome.emitted_receipts[0].identity_payload.to_dict()
            require(
                primary["event_id"] == case["oracle"]["event_id"],
                "independent event identity mismatch",
            )
            require(
                primary["core"]["information_losses"] == [],
                "C_OS has unexpected history loss",
            )
            require(
                primary["history"]["candidate"]["disposition"] == "rederived"
                and primary["history"]["carrier"]["disposition"] == "not_applicable",
                "history receipt mismatch",
            )
            require(
                (actual.time, actual.step_index)
                == (seed.inputs.time, seed.inputs.step_index),
                "event advances clock",
            )
            result["actual_receipts"] = receipts
            result["actual_target"] = owner.state.to_payload()
            for role in ("current", "reset"):
                mark(stage, role)
            for role in ("current", "reset"):
                incoming = replace(actual, current=getattr(actual, role), dt=DT)
                oracle = replace(
                    expected_target, current=getattr(expected_target, role), dt=DT
                )
                stage = "target_continuation"
                for beat in range(case["schedule"]["target_beats_per_role"]):
                    expected = dense_os(oracle)
                    step = ProvisionalCandidateCOSStep(incoming)
                    checks = compare_pass(step.os_pass, expected, case["comparison"])
                    checks.append(
                        comparison(
                            step.next_inputs.current.C,
                            expected["C"],
                            case["comparison"],
                            "C",
                        )
                    )
                    require(
                        step.next_inputs.reset == actual.reset,
                        "reset baseline mutated by continuation",
                    )
                    require(
                        step.next_inputs.current.W_A is None
                        and step.next_inputs.current.Z_4 is None,
                        "C_OS gained history",
                    )
                    require(min(step.next_inputs.current.C) >= 0, "negative poststate")
                    require(
                        step.next_inputs.step_index == incoming.step_index + 1
                        and step.next_inputs.time == incoming.time + DT,
                        "continuation clock/write count",
                    )
                    result["observations"].append(
                        {
                            "stage": stage,
                            "role": role,
                            "beat": beat + 1,
                            "time": step.next_inputs.time,
                            "comparisons": checks,
                        }
                    )
                    incoming = step.next_inputs
                    # Independent trajectory, not a fresh oracle seeded from native C.
                    oracle = replace(
                        oracle,
                        current=GRCV4AuthoritativeState(
                            tuple(map(float, expected["C"])), None, None
                        ),
                        step_index=oracle.step_index + 1,
                        time=oracle.time + DT,
                    )
                mark(stage, role, beats=10, resource_writes=10, W_writes=0, Z_writes=0)
                stage = "final_read"
                expected = dense_os(oracle)
                passed = CandidateCOSPass(incoming)
                checks = compare_pass(passed, expected, case["comparison"])
                # Re-admit both histories without writing either or the clock.
                native.GRC9V4COSOperation(
                    native.GRC9V4COSState(replace(incoming, dt=0), specialization)
                )
                result["observations"].append(
                    {
                        "stage": stage,
                        "role": role,
                        "comparisons": checks,
                        "final_inputs": incoming.to_payload(),
                    }
                )
                mark(stage, role, beats=0, state_digest=digest(incoming.to_payload()))
    except Exception as exc:
        failure = (
            "incomplete_budget"
            if isinstance(exc, BudgetExpired)
            else "comparison_or_execution_failure"
        )
        result["first_failure"] = {
            "stage": stage,
            "role": role,
            "outcome": failure,
            "type": type(exc).__name__,
            "message": str(exc).replace(str(ROOT), "<repository>"),
            "owner": "GRC9V4COSOperation/ProvisionalCandidateCOSStep/P984b comparator",
        }
        for row in rows:
            if (
                row["stage"] == stage
                and row["outcome"] == "not_run"
                and role in ("both", row["role"])
            ):
                row["outcome"] = failure
    finally:
        if owner is not None:
            # Preserve real publication even if a later comparison/continuation fails.
            result["event_committed"] = bool(owner.receipts)
            result["checkpoint"] = json.loads(owner.checkpoint())
        result["elapsed_seconds"] = time.monotonic() - start
        result["execution_budget_seconds"] = case["execution_budget_seconds"]
        result["unexecuted_dependent_stages"] = [
            {"role": r["role"], "stage": r["stage"]}
            for r in rows
            if r["outcome"] == "not_run"
        ]
        result["outcome"] = (
            "passed_named_case"
            if all(r["outcome"] == "passed_named_stage" for r in rows)
            and result["first_failure"] is None
            else "incomplete_case"
        )
    return result


def frozen_mechanics():
    """Exact literal construction, deliberately not a numerical event."""
    vectors = read(VECTORS)
    from pygrc.models.grc_9_v4_topology import GRC9V4PortGraph

    graph = GRC9V4PortGraph.from_payload(
        vectors["port_graph_envelope_vectors"][0]["payload"]
    )
    policy = next(
        r["payload"]["policy"]
        for r in vectors["subdigest_identity_vectors"]
        if r["vector_id"] == "SUBDIGEST-GRC9-EXPANSION-POLICY"
    )
    results = []
    for v in vectors["grc9_expansion_vectors"]:
        request = GRC9V4ExpansionRequestInput.from_payload(
            {
                **v["request"],
                "schema_version": "grc9v4-expansion-event-request-input-v1",
            }
        )
        plan = GRC9V4ExpansionPlan(
            graph,
            request.source_state_digest,
            request,
            GRC9ExpansionPolicy.from_payload(policy),
        )
        require(
            plan.event_identity_payload() == v["event_identity_payload"]
            and plan.target_graph.to_payload()
            == v["expected"]["identity_payloads"]["target_graph"],
            "frozen construction mismatch",
        )
        require(
            canonical_json_bytes(plan.event_identity_payload()).decode()
            == v["event_identity_canonical_jcs_utf8"],
            "frozen JCS mismatch",
        )
        results.append(
            {
                "fixture_id": v["fixture_id"],
                "event_id": plan.event_id,
                "target_graph_digest": plan.target_graph.graph_digest,
                "passed": True,
                "event_committed": False,
                "numerical_executed": False,
            }
        )
    return results


def check_manifest(manifest):
    check_digest(manifest)
    check_bindings(manifest["source_bindings"])
    require(manifest == make_manifest(), "manifest differs from declared case builder")


def validate_results(manifest, results):
    """Retained integrity/comparison check, not proof that a new run occurred."""
    check_digest(results)
    require(
        results["manifest_digest"] == manifest["record_digest"],
        "foreign result manifest",
    )
    require(
        results["user_accepted"] is False and results["aggregate_closed"] is False,
        "unreviewed acceptance promotion",
    )
    cases = {c["case_id"]: c for c in manifest["cases"]}
    selected = results["requested_case_ids"]
    require(
        bool(selected)
        and len(selected) == len(set(selected))
        and set(selected) <= set(cases),
        "invalid requested case roster",
    )
    require(
        [r["case_id"] for r in results["cases"]] == selected,
        "missing or reordered requested case",
    )
    require(
        len(results["cases"]) == len({r["case_id"] for r in results["cases"]}),
        "duplicate result case",
    )
    for row in results["cases"]:
        case = cases[row["case_id"]]
        require(
            row["input_digest"] == digest(case)
            and row["coverage_binding"] == case["coverage_binding"],
            "foreign case binding",
        )
        require(
            [(x["stage"], x["role"]) for x in row["stages"]]
            == [(s, r) for s in STAGES for r in ("current", "reset")],
            "missing/duplicate stage or role",
        )
        success = row["outcome"] == "passed_named_case"
        require(
            row["family"] == case["family"]
            and row["user_accepted"] is False
            and row["aggregate_closed"] is False,
            "case scope/acceptance promotion",
        )
        if success:
            require(
                row["event_committed"]
                and row["first_failure"] is None
                and not row["unexecuted_dependent_stages"]
                and all(s["outcome"] == "passed_named_stage" for s in row["stages"]),
                "false positive case",
            )
            expected_order = [("source_schedule", "current", None)] + [
                (stage, role, beat)
                for role in ("current", "reset")
                for stage, beat in [("target_continuation", n) for n in range(1, 11)]
                + [("final_read", None)]
            ]
            require(
                [(o["stage"], o["role"], o.get("beat")) for o in row["observations"]]
                == expected_order,
                "observation schedule mismatch",
            )
            require(
                row["actual_target"] == row["checkpoint"]["state"]
                and row["actual_receipts"] == row["checkpoint"]["receipts"],
                "checkpoint/result mismatch",
            )
            require(
                row["actual_source"] == manifest["expected_source"]
                and row["actual_request"] == case["request"],
                "actual subject substitution",
            )
            target = independent_target(manifest, case)
            require(
                row["independent_target"] == target.to_payload(),
                "independent target substitution",
            )
            actual = row["actual_target"]["inputs"]
            require(
                actual["reference"] == target.geometry.reference.to_payload()
                and actual["current"] == authority_payload(target.current)
                and actual["reset"] == authority_payload(target.reset),
                "target graph/reference/history substitution",
            )
            source = manifest["expected_source"]
            observations = row["actual_admission_reads"]
            expected_reads = [
                (case["request"]["source_graph_digest"], source["inputs"][r])
                for r in ("current", "reset")
            ]
            expected_reads += [
                (
                    target.geometry.reference.graph.graph_digest,
                    authority_payload(getattr(target, r)),
                )
                for r in ("current", "reset")
            ]
            require(
                [(r["graph"], r["authority"]) for r in observations] == expected_reads
                and all(
                    r["split_admitted"]
                    and r["published_state"] == source["scientific_digest"]
                    for r in observations
                ),
                "admission observation substitution",
            )
            initial = GeometryStageInputs.from_payload(manifest["initial_inputs"])
            oracle_inputs = {
                "current": replace(target, dt=DT),
                "reset": replace(target, current=target.reset, dt=DT),
            }
        for observation in row["observations"]:
            expected_quantities = (
                case["comparison"]["quantities"]
                if observation["stage"] != "final_read"
                else case["comparison"]["quantities"][1:]
            )
            require(
                set(c["quantity"] for c in observation["comparisons"])
                == set(expected_quantities)
                and len(observation["comparisons"]) == len(expected_quantities),
                "missing numerical quantity",
            )
            for c in observation["comparisons"]:
                require(
                    c
                    == comparison(
                        c["actual"], c["expected"], case["comparison"], c["quantity"]
                    ),
                    "comparison was widened or corrupted",
                )
            if success:
                role = observation["role"]
                operand = (
                    initial
                    if observation["stage"] == "source_schedule"
                    else oracle_inputs[role]
                )
                independently_recomputed = dense_os(operand)
                for c in observation["comparisons"]:
                    require(
                        c["expected"]
                        == independently_recomputed[c["quantity"]].tolist(),
                        "retained oracle operand/result drift",
                    )
                if observation["stage"] == "target_continuation":
                    oracle_inputs[role] = replace(
                        operand,
                        current=GRCV4AuthoritativeState(
                            tuple(map(float, independently_recomputed["C"])), None, None
                        ),
                        step_index=operand.step_index + 1,
                        time=operand.time + DT,
                    )
                if observation["stage"] == "final_read":
                    final = observation["final_inputs"]
                    require(
                        final["step_index"] == 11
                        and final["time"] == 11 * DT
                        and final["reset"] == actual["reset"],
                        "final clock/reset mismatch",
                    )
                    comparison(
                        final["current"]["C"],
                        operand.current.C,
                        case["comparison"],
                        "final_C",
                    )
    return {
        "executed_cases": len(results["cases"]),
        "passed_cases": sum(
            r["outcome"] == "passed_named_case" for r in results["cases"]
        ),
    }


def write_new(path, value):
    path = Path(path)
    require(
        not path.is_absolute() and ".." not in path.parts,
        "output must be repository-relative",
    )
    with (ROOT / path).open("x") as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--prepare", action="store_true")
    actions.add_argument("--run", action="store_true")
    actions.add_argument("--check", action="store_true")
    parser.add_argument("--manifest", default=INPUTS)
    parser.add_argument("--output", default=RESULTS)
    parser.add_argument(
        "--case",
        help="single exact case id; omitted runs the sixteen declared C_OS companions",
    )
    args = parser.parse_args()
    for path in (args.manifest, args.output):
        require(
            not Path(path).is_absolute() and ".." not in Path(path).parts,
            "artifact paths must be repository-relative",
        )
    if args.prepare:
        write_new(args.manifest, make_manifest())
        print("P984B_CASES_BOUND runtime_executed=false")
        return
    manifest = read(args.manifest)
    check_manifest(manifest)
    if args.check:
        print("P984B_RETAINED_PASS", validate_results(manifest, read(args.output)))
        return
    require(
        not (ROOT / args.output).exists(),
        "refusing to replace a retained run; choose a fresh output name",
    )
    cases = [
        c for c in manifest["cases"] if args.case is None or c["case_id"] == args.case
    ]
    require(bool(cases), "unknown case")
    results = {
        "schema": "p984b-native-runtime-results-v1",
        "manifest_digest": manifest["record_digest"],
        "command": [".venv/bin/python", SELF, *sys.argv[1:]],
        "dependencies": {
            "python": platform.python_version(),
            **{
                p: version(p)
                for p in ("numpy", "python-flint", "rfc8785", "jsonschema")
            },
        },
        "backend": "flint",
        "actual_owner": "pygrc.models.grc_9_v4_lifecycle.GRC9V4COSOperation",
        "requested_case_ids": [c["case_id"] for c in cases],
        "thread_environment": {
            k: __import__("os").environ.get(k)
            for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")
        },
        "frozen_mechanics": frozen_mechanics(),
        "cases": [],
        "user_accepted": False,
        "aggregate_closed": False,
        "limits": "C_OS named finite companions only; dense crosschecks are not rigorous error/effect certificates; other nine families, literal C_PC and P984c-i remain open",
    }
    for case in cases:
        row = execute_cos(manifest, case)
        results["cases"].append(row)
        print(case["case_id"], row["outcome"], row["first_failure"], flush=True)
    results = seal(results)
    validate_results(manifest, results)
    write_new(args.output, results)
    print("P984B_RUNTIME_RESULT", validate_results(manifest, results))
    if any(r["outcome"] != "passed_named_case" for r in results["cases"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
