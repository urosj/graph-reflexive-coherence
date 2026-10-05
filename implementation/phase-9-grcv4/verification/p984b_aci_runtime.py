"""Bounded A_CI expansion counterparts using the accepted fixed-row equations.

No new production policy. Every case owns both histories and ten target steps.
Saved-input interval checks are not trajectory reruns or an accumulated bound.
"""

import argparse
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from functools import lru_cache
from importlib.metadata import version
import json
import platform
import time
from unittest.mock import patch

import numpy as np
import p984b_runtime as b
from p984b_cci_runtime import represented_continuity
import verify_p983a_aci_oracle as oracle
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models import grc_v4_candidate_a as candidate
from pygrc.models.grc_v4_ci import CandidateCIRoot, ProvisionalCandidateCIStep
from pygrc.models.grc_v4_geometry import PhysicalFlux
from tests.models.test_grc_9_v4_aci import fixture, authority, ORACLE_SHA

SELF = b.HERE + "p984b_aci_runtime.py"
TEST = b.HERE + "test_p984b_aci_runtime.py"
INPUTS = b.BASE + "P9-8.4b-ACICases.json"
RESULTS = b.BASE + "P9-8.4b-ACIResults.json"
REVIEW = b.BASE + "P9-8.4b-ACIRuntimeReview.md"
PREDECESSOR = b.BASE + "P9-8.3A.2-ACI-Validation.json"
ROLES = ("current", "reset")
RECIPE = "grc9v4_ci_fixed_rows_confirmed_joint_residual_v1"
LIMITS = dict(
    root_error=Q(1, 2**48),
    current_error=Q(1, 2**40),
    baseline_error=Q(1, 2**40),
    source_error=Q(1, 2**64),
    resource_error=Q(1, 2**40),
    history_error=Q(1, 2**48),
    readback_error=Q(1, 2**40),
    flat_error=Q(1, 2**40),
)


def predecessor():
    b.require(
        b.sha((b.ROOT / oracle.RECORD).read_bytes()) == ORACLE_SHA,
        "accepted A_CI oracle changed",
    )
    old = b.read(oracle.RECORD)
    b.check_digest(old)
    b.require(
        b.read(PREDECESSOR)["acceptance"]["status"] == "accepted_by_user",
        "native A_CI predecessor not accepted",
    )
    return old


def state(payload):
    spec = payload["specialization"]
    return native.GRC9V4ACIState(
        b.GeometryStageInputs.from_payload(payload["inputs"]),
        native.GRC9V4Specialization(
            b.FrozenJSONMap(spec["resolved"]), b.FrozenJSONMap(spec["identity_payload"])
        ),
    )


def bind_case(seed, case):
    """Fresh actual-state identities; frozen expected port graph supplies topology."""
    case = deepcopy(case)
    request = case["request"]
    request.update(
        source_state_digest=seed.scientific_digest,
        history_policy=oracle.history_policy(
            b.authority_payload(seed.inputs.current),
            b.authority_payload(seed.inputs.reset),
        ),
        expected_event_id=None,
        expected_target_graph_digest=None,
    )
    vector = next(
        v
        for v in b.read(b.VECTORS)["grc9_expansion_vectors"]
        if v["fixture_id"] == case["fixture_id"]
    )
    identity = deepcopy(predecessor()["event_identity_payload"])
    for key in identity:
        if key in request and key != "schema_version":
            identity[key] = request[key]
    identity["canonical_module_node_count"] = vector["event_identity_payload"][
        "canonical_module_node_count"
    ]
    for channel in ("candidate", "carrier"):
        key = channel + "_history_policy_digest"
        identity[key] = request["history_policy"][key]
    event = oracle.common.payload_identity("expansion_event_identity_payload", identity)
    graph = deepcopy(vector["expected"]["identity_payloads"]["target_graph"])
    old_event = vector["expected"]["event_id"]

    def rename(value):
        return (
            event + value[len(old_event) :]
            if value.startswith(old_event + "/")
            else value
        )

    graph["live_node_ids"] = sorted(map(rename, graph["live_node_ids"]))
    for edge in graph["edges"]:
        edge["edge_id"] = rename(edge["edge_id"])
        for end in ("tail", "head"):
            edge[end]["node_id"] = rename(edge[end]["node_id"])
    graph["edges"].sort(key=lambda e: e["edge_id"])
    case["oracle"] = dict(event_id=event, event_identity=identity, target_graph=graph)
    return case


def independent_target(seed, case):
    ref = oracle.reference(case["oracle"]["target_graph"])
    source = seed.inputs.geometry.reference.graph
    event = case["oracle"]["event_id"]
    shares = {
        event + f"/satellite/{i}": Q(s)
        for i, s in enumerate(case["request"]["resource_distribution"], 1)
    }
    roles = {}
    for role in ROLES:
        old = getattr(seed.inputs, role)
        c = dict(zip(source.live_node_ids, old.C, strict=True))
        w = dict(zip(source.live_edge_ids, old.W_A, strict=True))
        roles[role] = b.GRCV4AuthoritativeState(
            tuple(
                c[n]
                if n in c
                else float(Q(c[case["request"]["source_node_id"]]) * shares.get(n, 0))
                for n in ref.graph.live_node_ids
            ),
            tuple(
                w.get(e, seed.specialization.resolved["expansion"]["bond_seed"])
                for e in ref.graph.live_edge_ids
            ),
            None,
        )
        b.require(
            sum(map(Q, old.C)) == sum(map(Q, roles[role].C)), "exact event charge drift"
        )
    return replace(
        seed,
        inputs=replace(
            seed.inputs,
            geometry=ref.geometry(),
            **roles,
            operation_id=case["request"]["operation_id"],
            dt=0,
        ),
    )


def make_manifest():
    old = predecessor()
    seed, _ = fixture(old)
    initial = replace(
        seed.inputs,
        current=authority(old["initial"]["current"]),
        reset=authority(old["initial"]["reset"]),
        step_index=0,
        time=0,
        dt=b.DT,
    )
    coverage = b.read(b.COVERAGE)
    b.check_digest(coverage)
    wanted = {
        r["fixture_id"]
        for r in coverage["coverage_cells"]
        if r["owner"] == "P9-8.4b" and r["family"] == "A_CI" and r["applicable"]
    }
    cases = []
    for v in b.read(b.VECTORS)["grc9_expansion_vectors"]:
        if v["fixture_id"] not in wanted:
            continue
        request = deepcopy(old["request"])
        request.update(
            {
                k: v["request"][k]
                for k in ("target_effective_degree", "module_chirality", "growth_phase")
            }
        )
        request["operation_id"] = "p984b-aci-" + v["fixture_id"]
        if (request["target_effective_degree"], request["growth_phase"]) == (52, 1):
            request["resource_distribution"] = [0.25, 0.5, 0.25]
        cases.append(
            bind_case(
                seed,
                dict(
                    case_id="P984B-ACI-" + v["fixture_id"],
                    fixture_id=v["fixture_id"],
                    family="A_CI",
                    subject_kind="native_companion",
                    request=request,
                    coverage_binding=dict(
                        record_digest=coverage["record_digest"],
                        cell_ids=[v["fixture_id"] + "::A_CI::" + r for r in ROLES],
                    ),
                    schedule=dict(
                        source_current_beats=1,
                        source_reset_beats=0,
                        target_beats_per_role=10,
                        dt=b.DT,
                        final_read=True,
                    ),
                    execution_budget_seconds=600,
                    comparison=dict(
                        kind="pointwise_full_formula_interval_and_native_whole_Frobenius_ball",
                        budgets={k: str(v) for k, v in LIMITS.items()},
                        native_radius="2^-20",
                        joint_residual_tolerance="2^-44",
                        numerical_recipe=RECIPE,
                        accumulated_trajectory_error_bound=False,
                        uniform_parameter_tube=False,
                    ),
                ),
            )
        )
    b.require(len(cases) == 16, "all sixteen A_CI layouts required")
    paths = [
        *oracle.SOURCES,
        SELF,
        TEST,
        b.SELF,
        b.HERE + "p984b_cci_runtime.py",
        PREDECESSOR,
        oracle.RECORD,
        b.BASE + "P9-8.3A.1-ACI-Acceptance.json",
        b.BASE + "P9-8.3A.2-ACI-RuntimeReview.md",
        b.COVERAGE,
        b.VECTORS,
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
            b.HERE + "verify_p983a_*oracle.py",
        )
        for p in b.ROOT.glob(pattern)
    ]
    return b.seal(
        dict(
            schema="p984b-aci-case-manifest-v1",
            family="A_CI",
            initial_inputs=initial.to_payload(),
            nominal_source=seed.to_payload(),
            cases=cases,
            source_bindings=b.bind(paths),
            claim_traces=old["side_tool_provenance"],
            source_rule="one actual source beat; recompute event/history identities, never substitute nominal state",
            phase_one_recipe="explicit [1/4,1/2,1/4] companion shares, independently checked for A_CI",
            user_accepted=False,
            aggregate_closed=False,
        )
    )


def check_manifest(value):
    b.check_digest(value)
    b.check_bindings(value["source_bindings"])
    b.require(value == make_manifest(), "A_CI manifest drift")


def capture_root(root):
    t = root.selected
    return b.seal(
        dict(
            input_identity=root.inputs.identity,
            recipe=root.to_payload()["numerics"],
            identity=root.identity,
            selected_inputs_identity=t.inputs.identity,
            point_identity=t.point.identity,
            read_source=t.point.read.source_identity,
            read_current=list(t.point.read.current.values),
            J=list(root.current.values),
            H=[list(r) for r in t.inputs.geometry.one_form_hodge.matrix],
            generated=[list(r) for r in t.generated.one_form_hodge.matrix],
            baseline=list(t.point.baseline.values),
            readback=list(t.point.read.flux.values),
            flat=list(t.point.read.causal_flat.values),
            W_hat_A=list(t.point.W_hat_A),
            source=[list(r) for r in t.structural_source.increment],
            evaluations=root.evaluations,
            residual_squared=str(t.residual_squared),
            domain_id=root.inputs.geometry.reference.profile.params_resolved.realization.contraction_domain_id,
            bounds=dict(root.certificate.bounds),
        )
    )


@lru_cache(maxsize=2048)
def _root_certificate(key):
    """Memoize only pure independent equations at exact saved operands.

    This does not cache production roots or skip native reads. The hypothetical
    paper step only supplies the accepted checker's output slots; it is not an
    executed physical beat and is not counted as continuation evidence.
    """
    v = json.loads(key)
    paper = oracle.PaperACI(v["graph"])
    observed = paper.step(v["C"], v["W_A"])
    observed.update({k: v[k] for k in ("H", "current", "baseline", "source")})
    check = oracle.check_step(v["graph"], v["C"], v["W_A"], observed)
    truth = check["truth"]
    bounds = {k: str(x) for k, x in truth["certificate"].items()}
    for field, name in (
        ("current", "J"),
        ("baseline", "baseline"),
        ("source", "source"),
    ):
        error = (
            oracle.numerical.matrix_error(np.array(v[field]), truth["read"][name])
            if field == "source"
            else oracle.full_error(v[field], truth["read"][name])
        )
        bounds[field + "_error"] = str(error)
    high = truth["high"]
    drive = high.conductance(truth["c"], truth["w"], truth["read"]["baseline"])
    causal = oracle.IV.matrix(
        [
            (w - g) / (w + g) * j / 16
            for w, g, j in zip(truth["w"], drive, truth["read"]["J"], strict=True)
        ]
    )
    flat = oracle.inverse(truth["H"]) * causal
    for name, exact in (("readback", causal), ("flat", flat)):
        bounds[name + "_error"] = str(oracle.full_error(v[name], exact))
        b.require(
            Q(bounds[name + "_error"]) < LIMITS[name + "_error"],
            "independent " + name + " error",
        )
    return dict(bounds=bounds, domain=check["domain"])


def independent_certificate(before, raw):
    key = dict(
        graph=before.geometry.reference.graph.port_graph.to_payload(),
        C=list(before.current.C),
        W_A=list(before.current.W_A),
        current=raw["J"],
        H=raw["H"],
        baseline=raw["baseline"],
        source=raw["source"],
        readback=raw["readback"],
        flat=raw["flat"],
    )
    return dict(
        input_identity=before.identity,
        selected_root_digest=raw["record_digest"],
        **deepcopy(_root_certificate(json.dumps(key, sort_keys=True))),
    )


def certified_root(root):
    raw = capture_root(root)
    return {**raw, "independent_certificate": independent_certificate(root.inputs, raw)}


def check_root(before, backend, value, *, numerics=False):
    raw = {k: v for k, v in value.items() if k != "independent_certificate"}
    b.check_digest(raw)
    params = before.geometry.reference.profile.params_resolved.realization
    b.require(
        value["input_identity"] == before.identity
        and value["domain_id"] == params.contraction_domain_id,
        "joint root input/domain drift",
    )
    b.require(value["recipe"] == RECIPE, "wrong confirmed CI recipe")
    recipe = dict(
        schema_version="grcv4-ci-root-recipe-v1",
        numerics=RECIPE,
        inputs=before.to_payload(),
        differential_reference=backend.to_payload(),
    )
    b.require(
        value["identity"] == "grcv4-ci-root-sha256:" + b.digest(recipe),
        "root recipe identity drift",
    )
    b.require(
        type(value["evaluations"]) is int
        and 2 <= value["evaluations"] <= params.iteration_limit,
        "unconfirmed or exhausted root",
    )
    ref = before.geometry.reference
    selected = replace(
        before,
        geometry=b.GRCV4Geometry(
            ref, b.OneFormHodge(ref.graph, tuple(map(tuple, value["H"])))
        ),
        stage="ci_trial",
        evaluation_index=value["evaluations"] - 1,
        trial_current=PhysicalFlux(ref.graph, tuple(value["J"])),
    )
    b.require(
        selected.identity == value["selected_inputs_identity"],
        "selected joint point drift",
    )
    b.require(
        value["read_current"] == value["J"]
        and value["read_source"] == value["point_identity"],
        "Read-Back current/source drift",
    )
    causal = [
        float((Q(w) - Q(g)) / (Q(w) + Q(g)) * Q(j) / 16)
        for w, g, j in zip(
            before.current.W_A, value["W_hat_A"], value["J"], strict=True
        )
    ]
    b.require(value["readback"] == causal, "Read-Back operand consumption drift")
    model = oracle.model_for(ref.graph.port_graph.to_payload())
    flat = value["flat"]
    source = [
        [
            float(Q(1, 2) * Q(float(Q(float(model.mask[i, j])) * Q(x) * Q(y))))
            for j, y in enumerate(flat)
        ]
        for i, x in enumerate(flat)
    ]
    generated = [
        [float(Q(int(i == j)) + Q(1, 2) * Q(s)) for j, s in enumerate(row)]
        for i, row in enumerate(source)
    ]
    b.require(
        value["source"] == source and value["generated"] == generated,
        "same-root source/geometry consumption drift",
    )
    b.require(
        0 <= Q(value["residual_squared"]) <= Q(params.tolerance) ** 2,
        "joint residual not admitted",
    )
    bounds = value["bounds"]
    b.require(
        Q(bounds["radius"]) == Q(oracle.RADIUS)
        and 0 <= Q(bounds["displacement_upper"]) <= Q(oracle.RADIUS)
        and 0 <= Q(bounds["contraction_upper"]) < 1,
        "native whole-domain failure",
    )
    cert = value["independent_certificate"]
    b.require(
        cert["input_identity"] == before.identity
        and cert["selected_root_digest"] == raw["record_digest"],
        "independent root binding drift",
    )
    b.require(
        0 <= Q(cert["bounds"]["contraction"]) < 1
        and 0 <= Q(cert["bounds"]["joint_residual"]) <= Q(oracle.TOLERANCE),
        "independent joint/domain failure",
    )
    for k in (
        "root_error",
        "current_error",
        "baseline_error",
        "source_error",
        "readback_error",
        "flat_error",
    ):
        b.require(
            0 <= Q(cert["bounds"][k]) < LIMITS[k], "independent error budget: " + k
        )
    b.require(
        0 <= Q(cert["domain"]["displacement_upper"]) <= Q(oracle.RADIUS)
        and 0 <= Q(cert["domain"]["contraction_upper"]) < 1,
        "independent whole-domain failure",
    )
    if numerics:
        b.require(
            cert == independent_certificate(before, raw),
            "interval root certificate drift",
        )


def step_certificate(before, value):
    after = b.GeometryStageInputs.from_payload(value["poststate"])
    root = value["root"]
    observed = dict(
        C=after.current.C,
        W_A=after.current.W_A,
        current=root["J"],
        H=root["H"],
        baseline=root["baseline"],
        source=root["source"],
    )
    truth = oracle.check_step(
        before.geometry.reference.graph.port_graph.to_payload(),
        before.current.C,
        before.current.W_A,
        observed,
    )
    high = truth["truth"]["high"]
    drive = high.conductance(
        oracle.vector(after.current.C),
        oracle.vector(before.current.W_A),
        oracle.vector(root["J"]),
    )
    target_error = oracle.full_error(value["writer_targets"][0]["target"], drive)
    b.require(target_error < LIMITS["history_error"], "writer target equation mismatch")
    return dict(
        input_identity=before.identity,
        selected_root_digest=root["record_digest"],
        poststate_identity=after.identity,
        resource_error=str(oracle.full_error(after.current.C, truth["C"])),
        history_error=str(oracle.full_error(after.current.W_A, truth["W_A"])),
        writer_target_digest=b.digest(value["writer_targets"]),
        writer_target_error=str(target_error),
    )


def checked_step(before, backend):
    targets, writes = [], []
    original_target, original_write = (
        candidate.candidate_a_writer_target,
        candidate.candidate_a_log_interpolation,
    )

    def target(point, c):
        result = original_target(point, c)
        targets.append(
            dict(
                point_identity=point.identity,
                C=list(c.values),
                W_A=list(point.inputs.current.W_A),
                J=list(point.current.values),
                target=list(result[1]),
            )
        )
        return result

    def write(old, drive, dt, tau):
        result = original_write(old, drive, dt, tau)
        writes.append(
            dict(old=list(old), target=list(drive), dt=dt, tau=tau, result=list(result))
        )
        return result

    with (
        patch.object(candidate, "candidate_a_writer_target", target),
        patch.object(candidate, "candidate_a_log_interpolation", write),
    ):
        step = ProvisionalCandidateCIStep(before, backend)
    value = dict(
        root=certified_root(step.root),
        reset_root=certified_root(step.reset_root),
        restart=certified_root(step.restart),
        poststate=step.next_inputs.to_payload(),
        selection_current=list(step.resource.selection.current.values),
        writer_targets=targets,
        log_writes=writes,
        carrier_writes=step.carrier_writes,
    )
    value["output_certificate"] = step_certificate(before, value)
    check_step(before, backend, value)
    return value, step.next_inputs


def check_step(before, backend, value, *, numerics=False):
    b.require(before.dt == b.DT, "unexpected physical timestep")
    check_root(before, backend, value["root"], numerics=numerics)
    check_root(
        replace(before, current=before.reset),
        backend,
        value["reset_root"],
        numerics=numerics,
    )
    b.require(
        value["selection_current"] == value["root"]["J"],
        "continuity consumed wrong current",
    )
    after = b.GeometryStageInputs.from_payload(value["poststate"])
    expected = replace(
        before,
        current=b.GRCV4AuthoritativeState(
            represented_continuity(before, value["root"]["J"]), after.current.W_A, None
        ),
        step_index=before.step_index + 1,
        time=float(Q(before.time) + Q(before.dt)),
    )
    b.require(
        after == expected and min(after.current.C) > 0,
        "continuity/reset/clock/history drift",
    )
    b.require(
        value["carrier_writes"] == 0
        and len(value["writer_targets"]) == len(value["log_writes"]) == 1,
        "writer count/carrier drift",
    )
    target, write = value["writer_targets"][0], value["log_writes"][0]
    b.require(
        target
        == dict(
            point_identity=value["root"]["point_identity"],
            C=list(after.current.C),
            W_A=list(before.current.W_A),
            J=value["root"]["J"],
            target=target["target"],
        ),
        "writer operand substitution",
    )
    b.require(
        write
        == dict(
            old=list(before.current.W_A),
            target=target["target"],
            dt=b.DT,
            tau=1,
            result=list(after.current.W_A),
        ),
        "log writer operand/output drift",
    )
    # Separate 100-digit scalar evaluation of the declared finite-fixture
    # interpolation, at the actual represented drive, not a native writer.
    mp = oracle.PaperACI(before.geometry.reference.graph.port_graph.to_payload()).mp
    decay = mp.exp(-mp.mpf(before.dt))
    expected_w = [
        float(mp.exp(decay * mp.log(w) + (1 - decay) * mp.log(g)))
        for w, g in zip(before.current.W_A, target["target"], strict=True)
    ]
    b.require(
        expected_w == list(after.current.W_A), "represented log interpolation drift"
    )
    cert = value["output_certificate"]
    b.require(
        cert["input_identity"] == before.identity
        and cert["selected_root_digest"] == value["root"]["record_digest"]
        and cert["poststate_identity"] == after.identity,
        "output certificate binding drift",
    )
    b.require(
        cert["writer_target_digest"] == b.digest(value["writer_targets"])
        and 0 <= Q(cert["writer_target_error"]) < LIMITS["history_error"],
        "writer target certificate drift",
    )
    for k in ("resource_error", "history_error"):
        b.require(0 <= Q(cert[k]) < LIMITS[k], "output error budget: " + k)
    check_root(replace(after, dt=0), backend, value["restart"], numerics=numerics)
    if numerics:
        b.require(
            cert == step_certificate(before, value), "output interval certificate drift"
        )
    return after


def run_source(manifest):
    nominal = state(manifest["nominal_source"])
    before = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    row, after = checked_step(before, nominal.differential_reference)
    seed = replace(nominal, inputs=replace(after, dt=0))
    for key, limit in (("C", oracle.RESOURCE_ERROR), ("W_A", oracle.HISTORY_ERROR)):
        b.require(
            max(
                abs(Q(x) - Q(y))
                for x, y in zip(
                    getattr(seed.inputs.current, key),
                    getattr(nominal.inputs.current, key),
                    strict=True,
                )
            )
            < limit,
            "source beat differs from accepted nominal comparison",
        )
    return dict(source_step=row, actual_source=seed.to_payload()), seed


def preflight(target):
    graph = target.inputs.geometry.reference.graph.port_graph.to_payload()
    paper = oracle.PaperACI(graph)
    rows = {}
    for role in ROLES:
        old = getattr(target.inputs, role)
        c, w = old.C, old.W_A
        trajectory = []
        for i in range(10):
            out = paper.step(c, w)
            b.require(
                min(out["C"]) > 0 and min(out["W_A"]) > 0,
                "independent negative/nonpositive continuation",
            )
            # Prove the declared target domain, not merely a converged point.
            domain = oracle.frobenius_domain(graph, c, w)
            trajectory.append(dict(index=i + 1, output=out, domain=domain))
            c, w = out["C"], out["W_A"]
        rows[role] = trajectory
    return rows


def event_capture(seed, request):
    owner = native.GRC9V4ACIOperation(seed)
    reads, publication, detections, surfaces = [], [], [], []
    initial = json.loads(owner.checkpoint())
    original_step, original_receipts = (
        native.ProvisionalCandidateCIStep,
        native.make_commit_receipts,
    )
    original_detection, original_surface = (
        native.GRC9V4CandidateDetection,
        native.candidate_a_writer_target,
    )

    def observed_step(inputs, *args, **kwargs):
        result = original_step(inputs, *args, **kwargs)
        b.require(
            inputs.dt == 0 and result.next_inputs == inputs and result.writer is None,
            "event performed a physical step/write",
        )
        reads.append(
            dict(
                inputs=inputs.to_payload(),
                root=certified_root(result.root),
                reset_root=certified_root(result.reset_root),
                published_state=owner.state.scientific_digest,
            )
        )
        return result

    def observed_surface(point, c):
        result = original_surface(point, c)
        surfaces.append(
            dict(
                point_identity=point.identity,
                C=list(c.values),
                W_A=list(point.inputs.current.W_A),
                J=list(point.current.values),
                target=list(result[1]),
            )
        )
        return result

    def observed_receipts(*args, **kwargs):
        publication.append(
            dict(
                admission_pairs=len(reads),
                writer_surfaces=len(surfaces),
                published_state=owner.state.scientific_digest,
            )
        )
        return original_receipts(*args, **kwargs)

    def observed_detection(postbeat, policy):
        result = original_detection(postbeat, policy)
        detections.append(
            dict(
                identity=result.identity,
                current=list(postbeat.physical_current),
                candidate_node_ids=list(result.candidate_node_ids()),
                published_state=owner.state.scientific_digest,
            )
        )
        return result

    with (
        patch.object(native, "ProvisionalCandidateCIStep", observed_step),
        patch.object(native, "make_commit_receipts", observed_receipts),
        patch.object(native, "GRC9V4CandidateDetection", observed_detection),
        patch.object(native, "candidate_a_writer_target", observed_surface),
    ):
        outcome = owner.expand(request)
    value = dict(
        source_checkpoint=initial,
        admission_reads=reads,
        writer_surfaces=surfaces,
        publication=publication,
        checkpoint=json.loads(owner.checkpoint()),
        actual_target=owner.state.to_payload(),
        receipts=[r.to_payload() for r in outcome.emitted_receipts],
        failure=None if outcome.committed else outcome.failure.to_payload(),
        replay_identical=False,
        detections=detections,
    )
    if outcome.committed:
        value["replay_identical"] = (
            native.GRC9V4ACIOperation.replay(owner.checkpoint()).checkpoint()
            == owner.checkpoint()
        )
    return owner, outcome, value


def check_event(seed, case, value, *, numerics=False):
    target = independent_target(seed, case)
    b.require(
        value["actual_target"] == target.to_payload(),
        "independent graph/reference/resource/W map drift",
    )
    b.require(
        len(value["admission_reads"]) == 2 and len(value["writer_surfaces"]) == 4,
        "missing both-role root/writer-surface admission",
    )
    for index, (parent, observed) in enumerate(
        zip((seed, target), value["admission_reads"], strict=True)
    ):
        b.require(
            observed["inputs"] == parent.inputs.to_payload()
            and observed["published_state"] == seed.scientific_digest,
            "admission operand/publication drift",
        )
        for ri, (role, key) in enumerate(
            (("current", "root"), ("reset", "reset_root"))
        ):
            inputs = replace(parent.inputs, current=getattr(parent.inputs, role))
            check_root(
                inputs, parent.differential_reference, observed[key], numerics=numerics
            )
            surface = value["writer_surfaces"][2 * index + ri]
            b.require(
                surface
                == dict(
                    point_identity=observed[key]["point_identity"],
                    C=list(inputs.current.C),
                    W_A=list(inputs.current.W_A),
                    J=observed[key]["J"],
                    target=surface["target"],
                ),
                "event writer-surface operands drift",
            )
    detections = value["detections"]
    b.require(
        len(detections) == 1
        and detections[0]["current"] == value["admission_reads"][0]["root"]["J"]
        and case["request"]["source_node_id"] in detections[0]["candidate_node_ids"]
        and detections[0]["published_state"] == seed.scientific_digest,
        "stale trigger/current",
    )
    b.require(
        value["publication"]
        == [
            dict(
                admission_pairs=2,
                writer_surfaces=4,
                published_state=seed.scientific_digest,
            )
        ],
        "premature publication",
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
    for role, key in (("current", "root"), ("reset", "reset_root")):
        old = value["admission_reads"][0][key]["J"]
        currents = dict(zip(source_ref.graph.live_edge_ids, old, strict=True))
        b.require(
            refs[0]["roles"][role]
            == dict(
                source=old,
                target=[currents.get(e, 0.0) for e in target_ref.graph.live_edge_ids],
            ),
            "reference current map drift",
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

    def hist(s):
        return oracle.common.payload_identity(
            "history_content_identity_payload",
            oracle.candidate_content(
                b.authority_payload(s.inputs.current),
                b.authority_payload(s.inputs.reset),
            ),
        )

    expected_candidate = dict(
        subject="candidate",
        disposition="exact_transport",
        source_history_digest=hist(seed),
        target_history_digest=hist(target),
        information_loss="none",
    )
    b.require(
        first["event_id"] == case["oracle"]["event_id"]
        and first["core"]["information_losses"] == []
        and first["history"]["candidate"] == expected_candidate
        and first["history"]["carrier"]
        == dict(
            subject="carrier",
            disposition="not_applicable",
            source_history_digest=None,
            target_history_digest=None,
            information_loss="none",
        ),
        "A_CI history receipt drift",
    )
    b.require(
        value["failure"] is None and value["replay_identical"] is True,
        "event/replay incomplete",
    )
    return target


def nominal_errors(after, expected):
    return {
        k: max(
            abs(Q(x) - Q(y))
            for x, y in zip(getattr(after.current, k), expected[k], strict=True)
        )
        for k in ("C", "W_A")
    }


def execute_case(seed, declared):
    case = bind_case(seed, declared)
    row = dict(
        case_id=declared["case_id"],
        input_digest=b.digest(declared),
        actual_case=case,
        coverage_binding=case["coverage_binding"],
        family="A_CI",
        outcome="incomplete_case",
        case_passed=False,
        event_committed=False,
        first_failure=None,
        continuation=[],
        final_reads={},
        user_accepted=False,
        aggregate_closed=False,
    )
    stage, role, index = "independent_preflight", "both", 0
    start = time.monotonic()
    try:
        with b.budget(case["execution_budget_seconds"]):
            target = independent_target(seed, case)
            row["predictions"] = preflight(target)
            stage = "event"
            owner, outcome, event = event_capture(
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
                for index in range(1, 11):
                    stage = "target_continuation"
                    value, after = checked_step(before, target.differential_reference)
                    errors = nominal_errors(
                        after, row["predictions"][role][index - 1]["output"]
                    )
                    b.require(
                        errors["C"] < Q(1, 2**39) and errors["W_A"] < Q(1, 2**47),
                        "nominal independent trajectory comparison failed",
                    )
                    row["continuation"].append(
                        dict(
                            role=role,
                            index=index,
                            step=value,
                            nominal_errors={k: str(v) for k, v in errors.items()},
                        )
                    )
                    before = after
                stage = "final_read"
                fresh = certified_root(
                    CandidateCIRoot(
                        replace(before, dt=0), target.differential_reference
                    )
                )
                b.require(
                    fresh == row["continuation"][-1]["step"]["restart"],
                    "fresh full joint root differs from restart",
                )
                row["final_reads"][role] = fresh
            b.require(
                owner.state.to_payload() == event["actual_target"],
                "detached continuation mutated owner",
            )
            row.update(outcome="passed_named_case", case_passed=True)
    except Exception as exc:
        row["first_failure"] = dict(
            stage=stage,
            role=role,
            index=index,
            type=type(exc).__name__,
            message=str(exc).replace(str(b.ROOT), "<repository>"),
            kind="operational_timeout"
            if isinstance(exc, b.BudgetExpired)
            else "numerical_or_lifecycle_failure",
        )
    row["elapsed_seconds"] = time.monotonic() - start
    return row


def validate(manifest, results, *, numerics=False):
    b.check_digest(results)
    b.require(
        results["manifest_digest"] == manifest["record_digest"]
        and results["native_runtime_executed"] is True
        and results["user_accepted"] is False
        and results["aggregate_closed"] is False,
        "runtime binding/scope drift",
    )
    initial = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    seed = state(results["shared"]["actual_source"])
    after = check_step(
        initial,
        seed.differential_reference,
        results["shared"]["source_step"],
        numerics=numerics,
    )
    b.require(
        seed.inputs == replace(after, dt=0)
        and seed.specialization == state(manifest["nominal_source"]).specialization,
        "source schedule drift",
    )
    b.require(
        [r["case_id"] for r in results["cases"]]
        == [c["case_id"] for c in manifest["cases"]],
        "case roster drift",
    )
    passed = 0
    for declared, row in zip(manifest["cases"], results["cases"], strict=True):
        case = bind_case(seed, declared)
        b.require(
            row["actual_case"] == case
            and row["input_digest"] == b.digest(declared)
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
            [(r["role"], r["index"]) for r in row["continuation"]]
            == [(r, i) for r in ROLES for i in range(1, 11)]
            and set(row["final_reads"]) == set(ROLES),
            "incomplete both-role schedule",
        )
        for role in ROLES:
            before = replace(
                target.inputs, current=getattr(target.inputs, role), dt=b.DT
            )
            for record in (r for r in row["continuation"] if r["role"] == role):
                before = check_step(
                    before,
                    target.differential_reference,
                    record["step"],
                    numerics=numerics,
                )
                errors = nominal_errors(
                    before, row["predictions"][role][record["index"] - 1]["output"]
                )
                b.require(
                    record["nominal_errors"] == {k: str(v) for k, v in errors.items()}
                    and errors["C"] < Q(1, 2**39)
                    and errors["W_A"] < Q(1, 2**47),
                    "nominal comparison drift",
                )
                last = record["step"]["restart"]
            check_root(
                replace(before, dt=0),
                target.differential_reference,
                row["final_reads"][role],
                numerics=numerics,
            )
            b.require(
                row["final_reads"][role] == last, "fresh joint root/restart mismatch"
            )
        passed += 1
    return dict(
        retained_integrity="passed",
        cases_passed=passed,
        cases_required=16,
        successful_history_cells=2 * passed,
        native_trajectories_rerun=False,
        interval_equations_recomputed=numerics,
        user_accepted=False,
        aggregate_closed=False,
    )


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
            not b.Path(name).is_absolute() and ".." not in b.Path(name).parts,
            "repository-relative path required",
        )
    if args.prepare:
        b.write_new(args.manifest, make_manifest())
        print("A_CI inputs bound; no native execution")
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
    with b.exact_backend(b.ExactBackend.FLINT):
        shared, seed = run_source(manifest)
        results = dict(
            schema="p984b-aci-runtime-results-v1",
            manifest_digest=manifest["record_digest"],
            environment=dict(
                python=platform.python_version(),
                numpy=version("numpy"),
                mpmath=version("mpmath"),
                python_flint=version("python-flint"),
            ),
            shared=shared,
            cases=[],
            native_runtime_executed=True,
            user_accepted=False,
            aggregate_closed=False,
        )
        for case in manifest["cases"]:
            row = execute_case(seed, case)
            results["cases"].append(row)
            print(case["fixture_id"], row["outcome"], row["first_failure"], flush=True)
            if not row["case_passed"]:
                break
    results = b.seal(results)
    b.write_new(args.output, results)
    if len(results["cases"]) != len(manifest["cases"]):
        print("INCOMPLETE_CAMPAIGN: first failure retained; remaining cases not run")
        raise SystemExit(1)
    report = validate(manifest, results)
    print(json.dumps({**report, "native_execution_in_this_command": True}, indent=2))
    if report["cases_passed"] != 16:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
