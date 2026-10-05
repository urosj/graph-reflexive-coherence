"""P9-8.4b A_OS native campaign against its accepted sixteen-layout oracle.

--prepare binds inputs, code and acceptance. --run alone executes native work.
--check-retained validates stored consumption/identities and nominal comparisons;
--recheck-numerics also recomputes independent interval bounds, not native runs.
No mode confers runtime acceptance or all-ten closure.
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

import p984b_aos_capture as capture
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from pygrc.models.grc_v4_geometry import GeometryStageInputs, GRCV4ReferenceGeometry
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState

oracle, base, aos = capture.oracle, capture.base, capture.aos
SELF = base.HERE + "p984b_aos_runtime.py"
CAPTURE = base.HERE + "p984b_aos_capture.py"
TEST = base.HERE + "test_p984b_aos_runtime.py"
INPUTS = base.BASE + "P9-8.4b-AOSCases.json"
RESULTS = base.BASE + "P9-8.4b-AOSResults.json"
REVIEW = base.BASE + "P9-8.4b-AOSRuntimeReview.md"
ACCEPTANCE_SHA = "fe06b0713881ee0dae4f438d49c634d7380e5bc1a7b5d0b023d3670fd51bfd3c"
ORACLE_INPUT_DIGEST = "1e86a813f07087736434e2ab1fe55a198b49f2fa651ea058d77cf91485b0be40"
ORACLE_RESULT_DIGEST = (
    "419d8fc73b39198834a24db2011a5617996005bdb7b24da5cc448cad9a5df44d"
)


def accepted_oracle():
    base.require(
        base.sha((base.ROOT / oracle.REVIEW).read_bytes()) == ACCEPTANCE_SHA,
        "accepted A_OS oracle review changed",
    )
    inputs, results = base.read(oracle.INPUTS), base.read(oracle.RESULTS)
    for value, digest in (
        (inputs, ORACLE_INPUT_DIGEST),
        (results, ORACLE_RESULT_DIGEST),
    ):
        base.check_digest(value)
        base.require(
            value["record_digest"] == digest, "accepted oracle content changed"
        )
    base.check_bindings(inputs["source_bindings"])
    base.require(
        results["manifest_digest"] == inputs["record_digest"], "oracle link drift"
    )
    base.require(
        aos.A_G2
        in aos.admission.accepted(base.ROOT)["accepted_generic_runtime_support"],
        "A_OS G2 prerequisite missing",
    )
    return inputs, results


def state(value):
    base.require(value["Z_4"] is None, "A_OS cannot import carrier state")
    return GRCV4AuthoritativeState(tuple(value["C"]), tuple(value["W_A"]), None)


def seed_from_payload(value):
    spec = value["specialization"]
    result = native.GRC9V4AOSState(
        GeometryStageInputs.from_payload(value["inputs"]),
        native.GRC9V4Specialization(
            FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])
        ),
    )
    base.require(result.to_payload() == value, "native state identity preimage drift")
    return result


def make_manifest():
    accepted, results = accepted_oracle()
    shared = accepted["shared"]
    ref = GRCV4ReferenceGeometry.from_payload(shared["source"]["reference"])
    initial = GeometryStageInputs(
        ref.geometry(),
        ref.context,
        state(shared["initial"]["current"]),
        state(shared["initial"]["reset"]),
        "aos-seed",
        30.140625,
        (),
        0,
        0,
        aos.DT,
        "pre_read",
        0,
        None,
    )
    spec = shared["specialization"]
    paths = {r["path"] for r in accepted["source_bindings"]} | {
        oracle.INPUTS,
        oracle.RESULTS,
        oracle.REVIEW,
        SELF,
        CAPTURE,
        TEST,
        base.BASE + "P9-8.4b-AOSScientificPressure.json",
        "pyproject.toml",
    }
    paths.update(
        str(p.relative_to(base.ROOT))
        for p in (base.ROOT / "src/pygrc/models").glob("grc*v4*.py")
    )
    paths.update(
        str(p.relative_to(base.ROOT)) for p in (base.ROOT / "src/pygrc").rglob("*.json")
    )
    return base.seal(
        {
            "schema": "p984b-aos-runtime-inputs-v1",
            "source_bindings": base.bind(paths),
            "oracle_inputs_digest": accepted["record_digest"],
            "oracle_results_digest": results["record_digest"],
            "acceptance": {
                "path": oracle.REVIEW,
                "sha256": ACCEPTANCE_SHA,
                "scope": "oracle_only",
            },
            "initial_inputs": initial.to_payload(),
            "specialization": spec,
            "source_steps": 1,
            "source_execution": "one_shared_native_beat_then_detached_event_owners",
            "cases": [
                {
                    "case_id": "P984B-AOS-RUNTIME-" + c["fixture_id"],
                    "fixture_id": c["fixture_id"],
                    "oracle_case_digest": base.digest(c),
                    "coverage_binding": c["coverage_binding"],
                    "target_steps_per_role": 10,
                    "final_read_only": True,
                    "execution_budget_seconds": 120,
                }
                for c in accepted["cases"]
            ],
            "exact_backend": "flint",
            "public_support_widened": False,
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )


def check_manifest(value):
    base.check_digest(value)
    base.check_bindings(value["source_bindings"])
    base.require(value == make_manifest(), "runtime manifest/request population drift")


def checked_step(before, backend, expected):
    value, following = capture.take_step(before, backend)
    base.require(
        capture.check_step(value, before, backend) == following, "step capture mismatch"
    )
    graph = before.geometry.reference.graph.port_graph.to_payload()
    out = capture.outputs(value)
    value["certificate"] = oracle.interval_certificate(
        graph, before.current.C, before.current.W_A, out
    )
    value["final_certificate"] = capture.final_certificate(before, value)
    value["nominal_errors"] = compare_nominal(out, expected)
    return value, following


def compare_nominal(actual, expected):
    return {
        name: capture.close(values, expected[name], oracle.LIMITS[name], name)
        for name, values in actual.items()
    }


def checked_read(before, backend, expected):
    value = capture.read_pass(before, backend)
    capture.check_pass(value, before, backend)
    value["certificate"] = capture.read_certificate(before, value)
    value["nominal_errors"] = compare_nominal(capture.outputs(value), expected)
    return value


def run_source(manifest, expected):
    before = GeometryStageInputs.from_payload(manifest["initial_inputs"])
    spec = manifest["specialization"]
    specialization = native.GRC9V4Specialization(
        FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])
    )
    seed = native.GRC9V4AOSState(before, specialization)
    native.GRC9V4AOSOperation(replace(seed, inputs=replace(before, dt=0)))
    row, after = checked_step(
        before,
        seed.differential_reference,
        expected["shared_observations"][0]["output"],
    )
    actual = native.GRC9V4AOSState(replace(after, dt=0), specialization)
    return {"source_step": row, "actual_source": actual.to_payload()}, actual


def fresh_request(seed, oracle_case):
    request = deepcopy(oracle_case["request"])
    request.update(
        source_state_digest=seed.scientific_digest,
        history_policy=aos.history_policy(
            capture.authority(seed.inputs.current), capture.authority(seed.inputs.reset)
        ),
        expected_event_id=None,
        expected_target_graph_digest=None,
    )
    return GRC9V4ExpansionRequestInput.from_payload(request)


def independent_target(seed, request, oracle_case, source_reads):
    """Literal accepted graph + independent actual-input resource/history maps."""
    data = request.to_payload()
    identity = deepcopy(oracle_case["event_identity_payload"])
    for key in identity:
        if key in data and key != "schema_version":
            identity[key] = data[key]
    for subject in ("candidate", "carrier"):
        key = subject + "_history_policy_digest"
        identity[key] = data["history_policy"][key]
    event = aos.payload_identity("expansion_event_identity_payload", identity)
    old_event = oracle_case["event_id"]
    graph = deepcopy(oracle_case["target"]["port_graph"])

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
    reference = aos.reference(graph)
    source = seed.inputs.geometry.reference.graph
    shares = {
        event + f"/satellite/{i}": Q(v)
        for i, v in enumerate(data["resource_distribution"], 1)
    }
    roles = {}
    for role in oracle.ROLES:
        initial = getattr(seed.inputs, role)
        c = dict(zip(source.live_node_ids, initial.C, strict=True))
        w = dict(zip(source.live_edge_ids, initial.W_A, strict=True))
        j = dict(zip(source.live_edge_ids, source_reads[role], strict=True))
        roles[role] = {
            "authoritative": aos.authority(
                [
                    c[n]
                    if n in c
                    else float(Q(c[data["source_node_id"]]) * shares.get(n, 0))
                    for n in graph["live_node_ids"]
                ],
                [w.get(e["edge_id"], 1.0) for e in graph["edges"]],
            ),
            "incoming_reference_current": [
                j.get(e["edge_id"], 0.0) for e in graph["edges"]
            ],
        }
        base.require(
            sum(map(Q, roles[role]["authoritative"]["C"])) == sum(map(Q, initial.C)),
            "exact event charge drift",
        )
    ids = aos.native_identity(
        reference,
        seed.specialization.specialization_id,
        roles["current"]["authoritative"],
        roles["reset"]["authoritative"],
    )
    return {
        "event_id": event,
        "event_identity": identity,
        "port_graph": graph,
        "reference": reference.to_payload(),
        "roles": roles,
        **ids,
    }


def event_capture(seed, request):
    owner = native.GRC9V4AOSOperation(seed)
    before_checkpoint = owner.checkpoint()
    reads, publications = [], []
    original_receipts = native._event_receipts

    def observe_pass(inputs, backend):
        with capture.Trace() as trace:
            passed = capture.realizations.CandidateAOSPass(inputs, backend)
        reads.append(
            {
                "graph_digest": inputs.geometry.reference.graph.graph_digest,
                "role_state": capture.authority(inputs.current),
                "published_state": owner.state.scientific_digest,
                "pass": capture.capture_pass(passed, trace),
            }
        )
        return passed

    def observe_receipts(*args):
        publications.append(
            {
                "admission_reads_before_receipts": len(reads),
                "published_state": owner.state.scientific_digest,
            }
        )
        return original_receipts(*args)

    with (
        patch.object(native, "CandidateAOSPass", observe_pass),
        patch.object(native, "_event_receipts", observe_receipts),
        patch.object(
            capture.steps,
            "CandidateAWriter",
            side_effect=AssertionError("event must not write history"),
        ),
        patch.object(
            capture.candidate,
            "candidate_a_log_interpolation",
            side_effect=AssertionError("event log write"),
        ),
    ):
        result = owner.expand(request)
    return (
        owner,
        result,
        {
            "source_checkpoint": json.loads(before_checkpoint),
            "admission_reads": reads,
            "publication_observations": publications,
            "checkpoint": json.loads(owner.checkpoint()),
            "failure": None if result.failure is None else result.failure.to_payload(),
        },
    )


def check_event(value, seed, request, oracle_case):
    expected_request = fresh_request(seed, oracle_case)
    base.require(
        request.to_payload() == expected_request.to_payload(),
        "stale/altered native request",
    )
    reads = value["admission_reads"]
    base.require(len(reads) == 4, "event lacks complete both-role admission")
    source_reads = {
        r: reads[i]["pass"]["corrector"]["current"] for i, r in enumerate(oracle.ROLES)
    }
    target = independent_target(seed, request, oracle_case, source_reads)
    inputs = replace(
        seed.inputs,
        geometry=GRCV4ReferenceGeometry.from_payload(target["reference"]).geometry(),
        current=state(target["roles"]["current"]["authoritative"]),
        reset=state(target["roles"]["reset"]["authoritative"]),
        operation_id=request.operation_id,
        dt=0,
    )
    after = native.GRC9V4AOSState(inputs, seed.specialization)
    for i, (which, role) in enumerate(
        (s, r) for s in (seed, after) for r in oracle.ROLES
    ):
        read = reads[i]
        operand = replace(which.inputs, current=getattr(which.inputs, role), dt=1)
        base.require(
            read["graph_digest"] == operand.geometry.reference.graph.graph_digest
            and read["role_state"] == capture.authority(operand.current)
            and read["published_state"] == seed.scientific_digest,
            "event admission operand/publication drift",
        )
        capture.check_pass(read["pass"], operand, which.differential_reference)
    base.require(
        value["publication_observations"]
        == [
            {
                "admission_reads_before_receipts": 4,
                "published_state": seed.scientific_digest,
            }
        ],
        "premature receipt publication",
    )
    checkpoint = value["checkpoint"]
    base.require(
        checkpoint["descriptor_version"] == native.GRC9V4AOSOperation.CHECKPOINT
        and checkpoint["initial"] == seed.to_payload()
        and checkpoint["state"] == after.to_payload()
        and checkpoint["requests"] == [request.to_payload()],
        "checkpoint state/request drift",
    )
    base.require(
        value["source_checkpoint"]
        == {
            "descriptor_version": native.GRC9V4AOSOperation.CHECKPOINT,
            "initial": seed.to_payload(),
            "state": seed.to_payload(),
            "requests": [],
            "receipts": [],
            "reference_currents": [],
            "lifecycle_digest": seed.lifecycle_digest(()),
        },
        "source checkpoint drift",
    )
    base.require(
        value["actual_target"] == after.to_payload(),
        "actual target differs from independent map",
    )
    base.require(
        after.scientific_digest == target["scientific_digest"]
        and after.reset_digest == target["reset_digest"],
        "target identity drift",
    )
    refs = checkpoint["reference_currents"]
    base.require(
        len(refs) == 1
        and refs[0]["event_id"] == target["event_id"]
        and refs[0]["source_graph_digest"]
        == seed.inputs.geometry.reference.graph.graph_digest
        and refs[0]["target_graph_digest"]
        == after.inputs.geometry.reference.graph.graph_digest,
        "reference-current lineage drift",
    )
    for role in oracle.ROLES:
        base.require(
            refs[0]["roles"][role]
            == {
                "source": source_reads[role],
                "target": target["roles"][role]["incoming_reference_current"],
            },
            "signed reference-current transfer drift",
        )
    receipts = value["receipts"]
    _, checked_receipts = native.make_commit_receipts(
        [r["identity_payload"] for r in receipts],
        operation_id=request.operation_id,
        source_state_digest=seed.scientific_digest,
        target_state_digest=after.scientific_digest,
        target_step_index=after.inputs.step_index,
        target_time=after.inputs.time,
    )
    base.require(
        [r.to_payload() for r in checked_receipts] == receipts
        and checkpoint["lifecycle_digest"] == after.lifecycle_digest(checked_receipts),
        "receipt/commit/lifecycle identity drift",
    )
    base.require(
        len(receipts) == 4 and checkpoint["receipts"] == receipts,
        "event ledger mismatch",
    )
    receipt = receipts[0]["identity_payload"]
    core = receipt["core"]
    for prefix, item in (("source", seed), ("target", after)):
        for suffix, expected in (
            ("state_digest", item.scientific_digest),
            ("reset_digest", item.reset_digest),
            ("model_identity", item.model_identity),
            ("graph_digest", item.inputs.geometry.reference.graph.graph_digest),
        ):
            base.require(
                core[prefix + "_" + suffix] == expected,
                "receipt scientific binding drift",
            )
    history = receipt["history"]
    expected_candidate = {
        "subject": "candidate",
        "disposition": "exact_transport",
        "information_loss": "none",
        "source_history_digest": aos.payload_identity(
            "history_content_identity_payload",
            aos.candidate_content(
                capture.authority(seed.inputs.current),
                capture.authority(seed.inputs.reset),
            ),
        ),
        "target_history_digest": aos.payload_identity(
            "history_content_identity_payload",
            aos.candidate_content(
                capture.authority(after.inputs.current),
                capture.authority(after.inputs.reset),
            ),
        ),
    }
    base.require(
        receipt["event_id"] == target["event_id"]
        and core["information_losses"] == []
        and history["candidate"] == expected_candidate
        and history["carrier"]
        == {
            "subject": "carrier",
            "disposition": "not_applicable",
            "source_history_digest": None,
            "target_history_digest": None,
            "information_loss": "none",
        },
        "history receipt drift",
    )
    base.require(
        value["failure"] is None and value["replay_identical"] is True,
        "event/replay incomplete",
    )
    return after


def execute_case(seed, case, oracle_case, expected, source_expected):
    result = {
        "case_id": case["case_id"],
        "input_digest": base.digest(case),
        "coverage_binding": case["coverage_binding"],
        "outcome": "incomplete_case",
        "case_passed": False,
        "event_committed": False,
        "first_failure": None,
        "continuation": [],
        "final_reads": {},
        "user_accepted": False,
        "aggregate_closed": False,
    }
    stage, role, index = "fresh_request", "both", 0
    start = time.monotonic()
    try:
        with base.budget(case["execution_budget_seconds"]):
            request = fresh_request(seed, oracle_case)
            result["actual_request"] = request.to_payload()
            stage = "event"
            owner, outcome, event = event_capture(seed, request)
            result["event"] = event
            result["event_committed"] = outcome.committed
            if not outcome.committed:
                raise ValueError("native event rejected: " + outcome.failure.message)
            event.update(
                actual_target=owner.state.to_payload(),
                receipts=[r.to_payload() for r in outcome.emitted_receipts],
                replay_identical=native.GRC9V4AOSOperation.replay(
                    owner.checkpoint()
                ).checkpoint()
                == owner.checkpoint(),
            )
            target = check_event(event, seed, request, oracle_case)
            for i, (which, role) in enumerate(
                (s, r) for s in (seed, target) for r in oracle.ROLES
            ):
                operand = replace(
                    which.inputs, current=getattr(which.inputs, role), dt=1
                )
                read = event["admission_reads"][i]["pass"]
                expected_read = (
                    source_expected[1 + i]["output"]
                    if i < 2
                    else expected["expectations"][0 if role == "current" else 11][
                        "output"
                    ]
                )
                read["certificate"] = capture.read_certificate(operand, read)
                read["nominal_errors"] = compare_nominal(
                    capture.outputs(read), expected_read
                )
            for role in oracle.ROLES:
                inputs = replace(
                    target.inputs, current=getattr(target.inputs, role), dt=aos.DT
                )
                for index in range(1, 11):
                    stage = "target_continuation"
                    nominal = expected["expectations"][
                        (0 if role == "current" else 11) + index - 1
                    ]["output"]
                    value, inputs = checked_step(
                        inputs, target.differential_reference, nominal
                    )
                    result["continuation"].append(
                        {"role": role, "index": index, "step": value}
                    )
                stage, index = "final_read", 0
                nominal = expected["expectations"][10 if role == "current" else 21][
                    "output"
                ]
                result["final_reads"][role] = checked_read(
                    inputs, target.differential_reference, nominal
                )
            base.require(
                owner.state.to_payload() == event["actual_target"],
                "detached continuation mutated event owner",
            )
            result.update(outcome="passed_named_case", case_passed=True)
    except Exception as exc:
        result["first_failure"] = {
            "stage": stage,
            "role": role,
            "index": index,
            "type": type(exc).__name__,
            "message": str(exc).replace(str(base.ROOT), "<repository>"),
            "kind": "operational_timeout"
            if isinstance(exc, base.BudgetExpired)
            else "numerical_or_lifecycle_failure",
        }
    result["elapsed_seconds"] = time.monotonic() - start
    return result


def check_read_record(before, value, nominal, *, numerics):
    cert = value["certificate"]
    base.require(
        cert["kind"] == "read_only"
        and cert["input_identity"] == before.identity
        and cert["output_digest"] == base.digest(capture.outputs(value))
        and set(cert["errors"]) == set(capture.outputs(value))
        and all(0 <= Q(e) < oracle.LIMITS[k] for k, e in cert["errors"].items())
        and 0 <= Q(cert["split_upper"]) < Q(aos.SPLIT),
        "read certificate binding/bounds drift",
    )
    base.require(
        value["nominal_errors"] == compare_nominal(capture.outputs(value), nominal),
        "read nominal comparison drift",
    )
    if numerics:
        base.require(
            cert == capture.read_certificate(before, value),
            "read interval evidence drift",
        )


def check_step_record(before, value, backend, nominal, *, numerics):
    following = capture.check_step(value, before, backend)
    out = capture.outputs(value)
    cert = value["certificate"]
    oracle.check_certificate(cert)
    graph = before.geometry.reference.graph.port_graph.to_payload()
    base.require(
        cert["operand_digest"]
        == base.digest(
            {
                "graph": graph,
                "C": list(before.current.C),
                "W_A": list(before.current.W_A),
            }
        )
        and cert["output_digest"] == base.digest(out),
        "step interval operand/output drift",
    )
    final = value["final_certificate"]
    base.require(
        final["input_digest"]
        == base.digest({"state": value["poststate"], "H": value["pass"]["H"]})
        and final["output_digest"]
        == base.digest({k: value[k] for k in ("final", "restart")})
        and set(final["errors"]) == {"final", "restart"}
        and all(
            set(errors) == {"current", "baseline", "readback", "flat"}
            and all(0 <= Q(e) < aos.CURRENT_ERROR for e in errors.values())
            for errors in final["errors"].values()
        ),
        "written-state interval binding/bounds drift",
    )
    base.require(
        value["nominal_errors"] == compare_nominal(out, nominal),
        "step nominal comparison drift",
    )
    if numerics:
        base.require(
            cert
            == oracle.interval_certificate(
                graph, before.current.C, before.current.W_A, out
            )
            and final == capture.final_certificate(before, value),
            "step interval evidence drift",
        )
    return following


def validate(manifest, results, *, numerics=False):
    accepted, expected = accepted_oracle()
    base.check_digest(results)
    base.require(
        results["manifest_digest"] == manifest["record_digest"]
        and results["native_runtime_executed"] is True
        and results["user_accepted"] is False
        and results["aggregate_closed"] is False,
        "runtime scope/manifest drift",
    )
    base.require(
        [r["case_id"] for r in results["cases"]]
        == [c["case_id"] for c in manifest["cases"]],
        "missing/reordered runtime cases",
    )
    source = results["shared"]
    seed = seed_from_payload(source["actual_source"])
    initial = GeometryStageInputs.from_payload(manifest["initial_inputs"])
    following = check_step_record(
        initial,
        source["source_step"],
        seed.differential_reference,
        expected["shared_observations"][0]["output"],
        numerics=numerics,
    )
    base.require(
        seed.inputs == replace(following, dt=0),
        "actual source borrows nominal oracle state",
    )
    passed = 0
    for case, value, oracle_case, nominal_case in zip(
        manifest["cases"],
        results["cases"],
        accepted["cases"],
        expected["cases"],
        strict=True,
    ):
        base.require(
            value["input_digest"] == base.digest(case)
            and value["coverage_binding"] == case["coverage_binding"]
            and value["user_accepted"] is False
            and value["aggregate_closed"] is False,
            "case binding/scope drift",
        )
        if not value["case_passed"]:
            base.require(
                value["outcome"] == "incomplete_case"
                and value["first_failure"] is not None,
                "incomplete case marked successful",
            )
            continue
        base.require(
            value["event_committed"] is True
            and value["outcome"] == "passed_named_case"
            and value["first_failure"] is None,
            "false native case success",
        )
        request = GRC9V4ExpansionRequestInput.from_payload(value["actual_request"])
        target = check_event(value["event"], seed, request, oracle_case)
        for i, (which, role) in enumerate(
            (s, r) for s in (seed, target) for r in oracle.ROLES
        ):
            before = replace(which.inputs, current=getattr(which.inputs, role), dt=1)
            nominal = (
                expected["shared_observations"][i + 1]["output"]
                if i < 2
                else nominal_case["expectations"][0 if role == "current" else 11][
                    "output"
                ]
            )
            check_read_record(
                before,
                value["event"]["admission_reads"][i]["pass"],
                nominal,
                numerics=numerics,
            )
        base.require(
            [(r["role"], r["index"]) for r in value["continuation"]]
            == [(r, i) for r in oracle.ROLES for i in range(1, 11)]
            and set(value["final_reads"]) == set(oracle.ROLES),
            "native history schedule incomplete",
        )
        for role in oracle.ROLES:
            before = replace(
                target.inputs, current=getattr(target.inputs, role), dt=aos.DT
            )
            for i, row in enumerate(
                r for r in value["continuation"] if r["role"] == role
            ):
                nominal = nominal_case["expectations"][
                    (0 if role == "current" else 11) + i
                ]["output"]
                before = check_step_record(
                    before,
                    row["step"],
                    target.differential_reference,
                    nominal,
                    numerics=numerics,
                )
            final = value["final_reads"][role]
            capture.check_pass(final, before, target.differential_reference)
            check_read_record(
                before,
                final,
                nominal_case["expectations"][10 if role == "current" else 21]["output"],
                numerics=numerics,
            )
        passed += 1
    return {
        "retained_integrity": "passed",
        "cases_passed": passed,
        "cases_required": 16,
        "successful_history_cells": 2 * passed,
        "native_trajectories_rerun": False,
        "interval_equations_recomputed": numerics,
        "user_accepted": False,
        "aggregate_closed": False,
    }


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
    base.require(
        not args.recheck_numerics or args.check_retained,
        "recheck requires retained mode",
    )
    for value in (args.manifest, args.output):
        path = base.Path(value)
        base.require(
            not path.is_absolute() and ".." not in path.parts,
            "repository-relative path required",
        )
    if args.prepare:
        base.write_new(args.manifest, make_manifest())
        print("A_OS runtime inputs bound; no native execution")
        return
    manifest = base.read(args.manifest)
    check_manifest(manifest)
    if args.check_retained:
        print(
            json.dumps(
                validate(
                    manifest, base.read(args.output), numerics=args.recheck_numerics
                ),
                indent=2,
            )
        )
        return
    base.require(
        not (base.ROOT / args.output).exists(), "refusing to overwrite native evidence"
    )
    accepted, expected = accepted_oracle()
    with base.exact_backend(base.ExactBackend.FLINT):
        shared, seed = run_source(manifest, expected)
        results = {
            "schema": "p984b-aos-runtime-results-v1",
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
        for case, oracle_case, nominal in zip(
            manifest["cases"], accepted["cases"], expected["cases"], strict=True
        ):
            row = execute_case(
                seed, case, oracle_case, nominal, expected["shared_observations"]
            )
            results["cases"].append(row)
            print(case["fixture_id"], row["outcome"], row["first_failure"], flush=True)
    results = base.seal(results)
    base.write_new(args.output, results)
    report = validate(manifest, results)
    print(json.dumps({**report, "native_execution_in_this_command": True}, indent=2))
    if report["cases_passed"] != 16:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
