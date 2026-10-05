"""All sixteen bounded C_CI expansion companions; no new production policy.

Reuse the accepted whole-ball native certificate and independent interval
equations. Retained checking is not native execution. A commit followed by a
continuation failure remains an incomplete case. Acceptance is separate.
"""

import argparse
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
from importlib.metadata import version
import json
import platform
import time
from unittest.mock import patch

import numpy as np
import p984b_runtime as b
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_v4_ci import CandidateCIRoot, ProvisionalCandidateCIStep
from pygrc.models.grc_v4_geometry import PhysicalFlux
from tests.models.test_grc_9_v4_cci import independent_model
import test_p980_realization_numerical as numerical
from test_p980_os_effect_witness import full_error, number

SELF = b.HERE + "p984b_cci_runtime.py"
TEST = b.HERE + "test_p984b_cci_runtime.py"
INPUTS = b.BASE + "P9-8.4b-CCICases.json"
RESULTS = b.BASE + "P9-8.4b-CCIResults.json"
PREDECESSOR = b.BASE + "P9-8.3C-CI-Validation.json"
REVIEW = b.BASE + "P9-8.4b-CCIRuntimeReview.md"
ROLES = ("current", "reset")
LIMITS = dict(
    root_error=Q(1, 2**48),
    current_error=Q(1, 2**40),
    source_error=Q(1, 2**64),
    resource_error=Q(1, 2**40),
)


def state(payload):
    spec = payload["specialization"]
    return native.GRC9V4CCIState(
        b.GeometryStageInputs.from_payload(payload["inputs"]),
        native.GRC9V4Specialization(
            b.FrozenJSONMap(spec["resolved"]), b.FrozenJSONMap(spec["identity_payload"])
        ),
    )


def make_manifest():
    old = b.read(PREDECESSOR)
    b.require("acceptance" in old, "C_CI predecessor is not accepted")
    obs = old["numerical_observations"]
    coverage = b.read(b.COVERAGE)
    b.check_digest(coverage)
    source = obs["checkpoint"]["initial"]
    wanted = {
        r["fixture_id"]
        for r in coverage["coverage_cells"]
        if r["owner"] == "P9-8.4b" and r["family"] == "C_CI" and r["applicable"]
    }
    cases = []
    for vector in b.read(b.VECTORS)["grc9_expansion_vectors"]:
        if vector["fixture_id"] not in wanted:
            continue
        request = deepcopy(obs["request"])
        request.update(
            {
                k: vector["request"][k]
                for k in ("target_effective_degree", "module_chirality", "growth_phase")
            }
        )
        request["operation_id"] = "p984b-cci-" + vector["fixture_id"]
        if (request["target_effective_degree"], request["growth_phase"]) == (52, 1):
            request["resource_distribution"] = [0.25, 0.5, 0.25]
        case = dict(
            case_id="P984B-CCI-" + vector["fixture_id"],
            fixture_id=vector["fixture_id"],
            family="C_CI",
            subject_kind="native_companion",
            request=request,
            oracle=b.construction_oracle(vector, request, source["specialization"]),
            coverage_binding=dict(
                record_digest=coverage["record_digest"],
                cell_ids=[vector["fixture_id"] + "::C_CI::" + role for role in ROLES],
            ),
            schedule=dict(
                source_current_beats=1,
                source_reset_beats=0,
                target_beats_per_role=10,
                dt=b.DT,
                final_read=True,
            ),
            execution_budget_seconds=180,
            changes_from_frozen=[
                "C_CI_declaration",
                "source_labels_and_histories",
                "event_and_target_identities",
                "phase_one_D52_shares_only",
            ],
            comparison=dict(
                kind="pointwise_full_formula_interval_error_and_native_whole_ball_admission",
                budgets={k: str(v) for k, v in LIMITS.items()},
                native_geometry_domain="Frobenius ball radius 2^-18",
                independent_geometry_domain="infinity ball radius 2^-20",
                joint_residual_tolerance="2^-44",
                interval_digits=60,
                accumulated_trajectory_error_bound=False,
                uniform_parameter_tube=False,
            ),
        )
        cases.append(case)
    b.require(len(cases) == 16, "all sixteen C_CI layouts required")
    paths = [
        PREDECESSOR,
        b.BASE + "P9-8.3C-CI-RuntimeReview.md",
        b.COVERAGE,
        b.VECTORS,
        b.SELF,
        SELF,
        TEST,
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
        dict(
            schema="p984b-cci-case-manifest-v1",
            family="C_CI",
            initial_inputs=obs["initial_inputs"],
            expected_source=source,
            cases=cases,
            source_bindings=b.bind(paths),
            claim_traces=obs["side_tool_provenance"],
            stage_meaning="fresh source beat; both-role joint-root admission; detached ten-step role continuations; fresh final reads",
            phase_one_recipe="reuse explicit [1/4,1/2,1/4] companion shares; independently check C_CI, not infer it from OS",
            user_accepted=False,
            aggregate_closed=False,
        )
    )


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "C_CI inputs/cases/budgets drift")


def capture_root(root):
    t = root.selected
    result = dict(
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
        baseline=list(t.point.algebra.baseline.values),
        readback=list(t.point.read.flux.values),
        flat=list(t.point.read.causal_flat.values),
        source=[list(r) for r in t.structural_source.increment],
        evaluations=root.evaluations,
        residual_squared=str(t.residual_squared),
        domain_id=root.inputs.geometry.reference.profile.params_resolved.realization.contraction_domain_id,
        bounds=dict(root.certificate.bounds),
    )
    return b.seal(result)


def independent_certificate(before, value):
    """Full joint-root error at saved entry C, never just numerical residual."""
    model = independent_model(before)
    output = {k: np.array(value[k]) for k in ("H", "J", "baseline", "source")}
    truth = numerical.certify_read(
        model, "C", "CI", np.array(before.current.C), None, None, output["H"], output
    )
    return dict(
        input_identity=before.identity,
        selected_root_digest=value["record_digest"],
        bounds={k: str(v) for k, v in truth["certificate"].items()},
    )


def certified_root(root):
    value = capture_root(root)
    value["independent_certificate"] = independent_certificate(root.inputs, value)
    return value


def check_root(before, value, *, numerics=False):
    raw = {k: v for k, v in value.items() if k != "independent_certificate"}
    b.check_digest(raw)
    ref = before.geometry.reference
    params = ref.profile.params_resolved.realization
    b.require(
        value["input_identity"] == before.identity
        and value["domain_id"] == params.contraction_domain_id,
        "joint root input/domain drift",
    )
    b.require(
        value["recipe"] == "ci_analytic_residual_enclosure_binary64_v2",
        "wrong CI numerical recipe",
    )
    recipe = dict(
        schema_version="grcv4-ci-root-recipe-v1",
        numerics=value["recipe"],
        inputs=before.to_payload(),
        differential_reference=None,
    )
    b.require(
        value["identity"] == "grcv4-ci-root-sha256:" + b.digest(recipe),
        "root recipe identity drift",
    )
    b.require(
        type(value["evaluations"]) is int
        and 1 <= value["evaluations"] <= params.iteration_limit,
        "root evaluation budget drift",
    )
    geometry = b.GRCV4Geometry(
        ref, b.OneFormHodge(ref.graph, tuple(map(tuple, value["H"])))
    )
    selected = replace(
        before,
        geometry=geometry,
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
        "Read-Back does not consume the selected current",
    )
    # Bind the actual same-root lowered read to the structural adapter and
    # generated geometry. Full-error comparisons alone can miss tiny changes.
    model = independent_model(before)
    flat = value["flat"]
    zeta = Q(ref.profile.params_resolved.candidate.zeta_C)
    source = [
        [
            float(zeta * Q(float(Q(float(model.mask[i, j])) * Q(x) * Q(y))))
            for j, y in enumerate(flat)
        ]
        for i, x in enumerate(flat)
    ]
    generated = [
        [
            float(
                Q(int(i == j)) + Q(ref.profile.params_resolved.geometry.kappa_H) * Q(s)
            )
            for j, s in enumerate(row)
        ]
        for i, row in enumerate(source)
    ]
    b.require(
        source == value["source"] and generated == value["generated"],
        "same-root source/geometry consumption drift",
    )
    b.require(
        0 <= Q(value["residual_squared"]) <= Q(params.tolerance) ** 2,
        "joint residual not admitted",
    )
    bounds = value["bounds"]
    b.require(
        Q(bounds["radius"]) == Q(1, 2**18)
        and 0 <= Q(bounds["displacement_upper"]) <= Q(bounds["radius"])
        and 0 <= Q(bounds["contraction_upper"]) < 1
        and Q(bounds["selector_gap_lower"]) > 0,
        "whole-domain certificate not admitted",
    )
    cert = value["independent_certificate"]
    b.require(
        cert["input_identity"] == before.identity
        and cert["selected_root_digest"] == value["record_digest"],
        "independent certificate binding drift",
    )
    b.require(
        0 <= Q(cert["bounds"]["contraction"]) < 1, "independent contraction failure"
    )
    for key in ("root_error", "current_error", "source_error"):
        b.require(
            0 <= Q(cert["bounds"][key]) < LIMITS[key],
            "independent error budget: " + key,
        )
    if numerics:
        b.require(
            cert == independent_certificate(before, raw), "interval certificate drift"
        )


def represented_continuity(before, j):
    """Reassemble outward B by endpoints and honor each represented stage.

    The contract uses Python's binary64 sum, then binary64 multiplication and
    subtraction. A one-round rational C-dt*B*J is a different numerical law.
    Independent interval error still bounds the underlying exact expression.
    """
    graph = before.geometry.reference.graph
    return tuple(
        c
        - before.dt
        * sum(
            float(int(edge.tail_node_id == n) - int(edge.head_node_id == n)) * current
            for edge, current in zip(graph.oriented_edges, j, strict=True)
        )
        for n, c in zip(graph.live_node_ids, before.current.C, strict=True)
    )


def capture_step(step):
    b.require(
        step.writer is None and step.carrier_writes == 0, "C_CI acquired history writer"
    )
    value = dict(
        root=certified_root(step.root),
        reset_root=certified_root(step.reset_root),
        restart=certified_root(step.restart),
        poststate=step.next_inputs.to_payload(),
        selection_current=list(step.resource.selection.current.values),
        writer=None,
        carrier_writes=0,
    )
    value["resource_error"] = resource_error(
        step.inputs, value["root"], step.next_inputs.current.C
    )
    check_step(step.inputs, value)
    return value


def resource_error(before, root, after):
    model = independent_model(before)
    truth = numerical.certify_read(
        model,
        "C",
        "CI",
        np.array(before.current.C),
        None,
        None,
        np.array(root["H"]),
        {k: np.array(root[k]) for k in ("J", "baseline", "source")},
    )
    expected = truth["c"] - number(before.dt) * truth["high"].B * truth["read"]["J"]
    return str(full_error(after, expected))


def check_step(before, value, *, numerics=False):
    check_root(before, value["root"], numerics=numerics)
    check_root(
        replace(before, current=before.reset), value["reset_root"], numerics=numerics
    )
    b.require(
        value["selection_current"] == value["root"]["J"],
        "continuity consumed wrong current",
    )
    expected = replace(
        before,
        current=b.GRCV4AuthoritativeState(
            represented_continuity(before, value["root"]["J"]), None, None
        ),
        step_index=before.step_index + 1,
        time=float(Q(before.time) + Q(before.dt)),
    )
    b.require(
        expected.to_payload() == value["poststate"],
        "continuity/reset/clock/history drift",
    )
    b.require(
        value["writer"] is None and value["carrier_writes"] == 0,
        "unexpected C_CI history write",
    )
    b.require(
        min(expected.current.C) >= 0
        and 0 <= Q(value["resource_error"]) < LIMITS["resource_error"],
        "resource output error/admission failure",
    )
    check_root(replace(expected, dt=0), value["restart"], numerics=numerics)
    if numerics:
        b.require(
            value["resource_error"]
            == resource_error(before, value["root"], expected.current.C),
            "resource interval certificate drift",
        )
    return expected


def run_source(manifest):
    initial = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    step = ProvisionalCandidateCIStep(initial)
    seed = replace(
        state(manifest["expected_source"]), inputs=replace(step.next_inputs, dt=0)
    )
    b.require(
        seed.to_payload() == manifest["expected_source"],
        "fresh source differs from accepted predecessor",
    )
    return dict(source_step=capture_step(step), actual_source=seed.to_payload()), seed


def preflight(target):
    """Saved-input independent predictions before native event/continuation."""
    rows = {}
    for role in ROLES:
        c = np.array(getattr(target, role).C)
        model = independent_model(target)
        trajectory = []
        for index in range(10):
            result = numerical.produce_step(model, "C", "CI", c, None, None)
            trajectory.append(
                dict(
                    index=index + 1,
                    C=result["after"].tolist(),
                    J=result["read"]["J"].tolist(),
                )
            )
            b.require(
                np.isfinite(result["after"]).all() and min(result["after"]) >= 0,
                "independent continuation predicts a negative/nonfinite resource",
            )
            c = result["after"]
        rows[role] = trajectory
    return rows


def event_capture(seed, request):
    owner = native.GRC9V4CCIOperation(seed)
    initial = json.loads(owner.checkpoint())
    reads, publication, detections = [], [], []
    original_step, original_receipts = (
        native.ProvisionalCandidateCIStep,
        native.make_commit_receipts,
    )
    original_detection = native.GRC9V4CandidateDetection

    def observed_step(inputs, *args, **kwargs):
        result = original_step(inputs, *args, **kwargs)
        b.require(
            inputs.dt == 0 and result.next_inputs == inputs,
            "event performed a physical step",
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

    def observed_receipts(*args, **kwargs):
        publication.append(
            dict(
                admission_pairs=len(reads),
                published_state=owner.state.scientific_digest,
            )
        )
        return original_receipts(*args, **kwargs)

    def observed_detection(postbeat, policy):
        result = original_detection(postbeat, policy)
        detections.append(
            dict(
                identity=result.identity,
                row_inputs_identity=postbeat.identity,
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
    ):
        outcome = owner.expand(request)
    value = dict(
        source_checkpoint=initial,
        admission_reads=reads,
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
            native.GRC9V4CCIOperation.replay(owner.checkpoint()).checkpoint()
            == owner.checkpoint()
        )
    return owner, outcome, value


def check_event(seed, case, value, *, numerics=False):
    expected = b.independent_target(dict(expected_source=seed.to_payload()), case)
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
        check_root(parent.inputs, observed["root"], numerics=numerics)
        check_root(
            replace(parent.inputs, current=parent.inputs.reset),
            observed["reset_root"],
            numerics=numerics,
        )
    detection = value["detections"]
    b.require(
        len(detection) == 1
        and detection[0]["current"] == value["admission_reads"][0]["root"]["J"]
        and case["request"]["source_node_id"] in detection[0]["candidate_node_ids"]
        and detection[0]["published_state"] == seed.scientific_digest,
        "fresh trigger/current binding drift",
    )
    b.require(
        value["publication"]
        == [dict(admission_pairs=2, published_state=seed.scientific_digest)],
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
    for role, key in (("current", "root"), ("reset", "reset_root")):
        old = value["admission_reads"][0][key]["J"]
        currents = dict(zip(source_ref.graph.live_edge_ids, old, strict=True))
        expected_j = [currents.get(e, 0.0) for e in target_ref.graph.live_edge_ids]
        b.require(
            refs[0]["roles"][role] == dict(source=old, target=expected_j),
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
            == dict(
                subject=channel,
                disposition=disposition,
                source_history_digest=None,
                target_history_digest=None,
                information_loss="none",
            ),
            "C_CI history receipt drift",
        )
    b.require(
        value["failure"] is None and value["replay_identical"] is True,
        "event/replay incomplete",
    )
    return target


def execute_case(seed, case):
    row = dict(
        case_id=case["case_id"],
        input_digest=b.digest(case),
        coverage_binding=case["coverage_binding"],
        family="C_CI",
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
            target = b.independent_target(dict(expected_source=seed.to_payload()), case)
            row["predictions"] = preflight(target)
            stage = "event"
            request = b.GRC9V4ExpansionRequestInput.from_payload(case["request"])
            owner, outcome, event = event_capture(seed, request)
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
                    native_step = ProvisionalCandidateCIStep(before)
                    value = capture_step(native_step)
                    expected = row["predictions"][role][index - 1]
                    error = max(
                        abs(x - y)
                        for x, y in zip(
                            expected["C"],
                            native_step.next_inputs.current.C,
                            strict=True,
                        )
                    )
                    b.require(
                        error < 2**-39,
                        "nominal independent trajectory comparison failed",
                    )
                    row["continuation"].append(
                        dict(
                            role=role,
                            index=index,
                            step=value,
                            nominal_resource_error=error,
                        )
                    )
                    before = native_step.next_inputs
                stage = "final_read"
                fresh = certified_root(CandidateCIRoot(replace(before, dt=0)))
                b.require(
                    fresh == row["continuation"][-1]["step"]["restart"],
                    "fresh final joint root differs from restart",
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
    source = results["shared"]
    initial = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    after = check_step(initial, source["source_step"], numerics=numerics)
    seed = state(source["actual_source"])
    b.require(
        seed.inputs == replace(after, dt=0)
        and seed.to_payload() == manifest["expected_source"],
        "source schedule drift",
    )
    b.require(
        [r["case_id"] for r in results["cases"]]
        == [c["case_id"] for c in manifest["cases"]],
        "case roster drift",
    )
    passed = 0
    for case, row in zip(manifest["cases"], results["cases"], strict=True):
        b.require(
            row["input_digest"] == b.digest(case)
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
                before = check_step(before, record["step"], numerics=numerics)
                expected = row["predictions"][role][record["index"] - 1]
                error = max(
                    abs(x - y)
                    for x, y in zip(expected["C"], before.current.C, strict=True)
                )
                b.require(
                    error == record["nominal_resource_error"] and error < 2**-39,
                    "nominal comparison drift",
                )
                last = record["step"]["restart"]
            check_root(
                replace(before, dt=0), row["final_reads"][role], numerics=numerics
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
        print("C_CI inputs bound; no native execution")
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
            schema="p984b-cci-runtime-results-v1",
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
                # Retain the first failure and stop; do not spend the remaining
                # campaign on a common harness/domain defect. Never call this
                # partial roster a completed execution.
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
