"""Four bounded native C_OS numerical steps; not committed events or a campaign."""

import argparse
from dataclasses import replace
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import time

import p984g_cos as prior

ROOT, BASE, HERE = prior.ROOT, prior.BASE, prior.HERE
SELF = HERE + "p984g_cos_native.py"
PLAN = BASE + "P9-8.4g-COSNativePlan.md"
REVIEW = BASE + "P9-8.4g-COSNativeReview.md"
INPUTS = BASE + "P9-8.4g-COSNativeInputs.json"
RESULTS = BASE + "P9-8.4g-COSNativeResults.json"
DIRECTORY = BASE + "P9-8.4g-COSNative/"
POLICY = "certified_arb_256_weighted_v1"
BASELINE = "7ca0c368"
BOUNDS = BASE + "P9-8.4g-COSBoundsResults.json"
HISTORY = (prior.INPUTS, prior.RESULTS, BASE + "P9-8.4g-COSBoundsInputs.json", BOUNDS)
CASES = prior.CASES
require, read, seal, digest = prior.require, prior.read, prior.seal, prior.digest


def case_path(graph, role):
    require((graph, role) in CASES, "unknown native case")
    return DIRECTORY + graph + "-" + role + ".json"


def bindings():
    paths = [
        SELF,
        PLAN,
        prior.SELF,
        prior.PREPARED,
        *HISTORY,
        HERE + "prepare_p983_all_realizations.py",
        HERE + "prepare_p983_graph_admission.py",
        "specs/grc-v4-numerical-policy.md",
    ]
    paths += [
        str(p.relative_to(ROOT))
        for p in (ROOT / "src/pygrc/models").glob("*grc*v4*.py")
    ]
    return {
        p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
        for p in sorted(set(paths))
    }


def manifest():
    for name in HISTORY:
        original = subprocess.check_output(
            ["git", "show", BASELINE + ":" + name], cwd=ROOT
        )
        require(
            (ROOT / name).read_bytes() == original,
            "historical evidence changed: " + name,
        )
    return seal(
        dict(
            schema="p984g-cos-native-inputs-v1",
            cases=[list(c) for c in CASES],
            source_bindings=bindings(),
            numerical_policy=POLICY,
            exact_backend="flint",
            case_cap_seconds=600,
            max_concurrent_workers=2,
            retained_case_budget_bytes=500000,
            declaration_digest=read(prior.PREPARED)["record_digest"],
            historical_commit=BASELINE,
            bounds_digest=read(BOUNDS)["record_digest"],
            comparison=dict(atol=2e-11, rtol=2e-11),
            scope="four_point_numerical_admission_not_lifecycle_campaign",
        )
    )


def point(value):
    return dict(
        current=list(value.current.values),
        baseline=list(value.algebra.baseline.values),
        read_flux=list(value.read.flux.values),
        causal_flat=list(value.read.causal_flat.values),
        input_hodge_digest=digest(value.inputs.geometry.one_form_hodge.matrix),
        retained_hodge_digest=digest(value.algebra.retained_hodge.matrix),
        selector_rank=value.algebra.selector.rank,
        closure_residual_squared=value.closure_residual_squared,
    )


def independent_continuity(subject, role, current, dt):
    b, _ = prior.graph_data(subject)
    # Literal native scalar summation order, not a fused exact dot or BLAS call.
    return [
        float(c)
        - float(dt)
        * sum(float(w) * float(j) for w, j in zip(row, current, strict=True))
        for c, row in zip(subject["roles"][role]["C"], b, strict=True)
    ]


def compare_output(result, subject, role, bounds, dense, dt):
    import numpy as np
    from flint import fmpq

    q = lambda x: fmpq(x) if isinstance(x, str) else fmpq(*float(x).as_integer_ratio())
    for stage in ("predictor", "corrector", "final"):
        for key in ("current", "baseline", "read_flux", "causal_flat"):
            values = result[stage][key]
            require(
                len(values) == len(subject["graph"]["edges"])
                and np.isfinite(values).all(),
                "native vector shape/finiteness",
            )
        require(
            result[stage]["selector_rank"] == 1
            and q(result[stage]["closure_residual_squared"]) >= 0,
            "native selector/residual summary",
        )
    require(
        result["corrector"]["current"] == bounds["staged"]["uniquely_enclosed_current"],
        "native current differs from uniquely enclosed staged current",
    )
    c = result["after_C"]
    require(len(c) == len(bounds["staged"]["resources"]), "resource dimension")
    require(
        all(
            q(row["lower"]) <= q(x) <= q(row["upper"])
            for x, row in zip(c, bounds["staged"]["resources"], strict=True)
        ),
        "native resource outside staged enclosure",
    )
    require(
        c == independent_continuity(subject, role, result["corrector"]["current"], dt),
        "continuity stage/order/sign mismatch",
    )
    require(all(x >= 0 for x in c), "negative native resource")

    def charge(values):
        values = list(values)
        while len(values) > 1:
            values = [
                values[i] + values[i + 1] if i + 1 < len(values) else values[i]
                for i in range(0, len(values), 2)
            ]
        return values[0] if values else 0.0

    target = charge(subject["roles"]["current"]["C"])
    actual = charge(c)
    require(
        result["Q_target"] == target
        and result["charge"]
        == dict(
            target_charge=target,
            admitted_charge=actual,
            residual=float(q(actual) - q(target)),
        ),
        "pairwise charge fields differ",
    )
    policy = subject["profile"]["params_resolved"]["charge"]
    require(
        abs(q(actual) - q(target))
        <= q(policy["absolute_tolerance"])
        + q(policy["relative_tolerance"]) * max(abs(q(target)), fmpq(1)),
        "native charge outside tolerance",
    )
    for stage in ("predictor", "corrector"):
        for key in ("current", "baseline", "read_flux", "causal_flat"):
            require(
                np.allclose(
                    result[stage][key], dense[stage][key], atol=2e-11, rtol=2e-11
                ),
                "independent dense stage mismatch: " + stage + "/" + key,
            )
    for key in ("current", "baseline", "read_flux", "causal_flat"):
        require(
            np.allclose(
                result["final"][key], result["final_dense"][key], atol=2e-11, rtol=2e-11
            ),
            "independent final-C mismatch: " + key,
        )
    drift = sum(map(q, c), fmpq(0)) - sum(map(q, subject["roles"][role]["C"]), fmpq(0))
    require(
        str(drift) == result["exact_resource_sum_delta"], "exact charge drift mismatch"
    )
    require(
        result["final"]["input_hodge_digest"]
        == result["corrector"]["input_hodge_digest"],
        "final read consumed wrong geometry",
    )


def execute(graph, role, progress):
    from flint import fmpq
    from pygrc.models.grc_v4_numerics import (
        exact_backend,
        ExactBackend,
        numerical_policy,
        NumericalPolicy,
        matrix_operation,
    )
    from pygrc.models.grc_v4_step import ProvisionalCandidateCOSStep
    from prepare_p983_all_realizations import materialize

    with (
        exact_backend(ExactBackend.FLINT),
        numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),
        matrix_operation(),
    ):
        declaration = read(prior.PREPARED)
        start = time.monotonic()
        state = materialize(declaration, graph)
        inputs = replace(
            state.inputs,
            current=getattr(state.inputs, role),
            stage="pre_read",
            dt=declaration["selected_configuration"]["ordinary_dt"],
        )
        before_digest = digest(inputs.to_payload())
        progress(dict(stage="materialized", seconds=time.monotonic() - start))
        start = time.monotonic()
        step = ProvisionalCandidateCOSStep(inputs)
        elapsed = time.monotonic() - start
        progress(dict(stage="numerical_step_completed", seconds=elapsed))
        require(
            step.os_pass is not None and step.final is not None,
            "missing positive-step stages",
        )
        selected = step.os_pass.corrector
        after = step.next_inputs
        require(digest(inputs.to_payload()) == before_digest, "input mutation")
        require(step.resource.continuity_evaluations == 1, "multiple resource writes")
        require(
            after.reset == inputs.reset
            and after.current.W_A == inputs.current.W_A
            and after.current.Z_4 == inputs.current.Z_4,
            "authority/history changed",
        )
        require(
            after.step_index == inputs.step_index + 1
            and after.time == inputs.time + inputs.dt,
            "clock/index changed incorrectly",
        )
        require(
            after.geometry == inputs.geometry, "OS geometry persisted into continuation"
        )
        require(
            step.final.inputs.current == step.resource.provisional_state
            and step.final.inputs.geometry == selected.inputs.geometry,
            "wrong final-C stage/geometry",
        )
        b, params = prior.graph_data(declaration[graph])
        import numpy as np

        generated = prior.generated_h(
            b, step.os_pass.predictor.read.causal_flat.values, params
        )
        require(
            generated.tolist()
            == [list(r) for r in selected.inputs.geometry.one_form_hodge.matrix],
            "independently assembled consumed geometry differs",
        )
        final_dense = prior.dense_point(
            b, np.array(after.current.C), generated, params["candidate"]
        )
        q = lambda x: fmpq(*float(x).as_integer_ratio())
        result = dict(
            before_digest=before_digest,
            after_digest=digest(after.to_payload()),
            numerical_step_seconds=elapsed,
            predictor=point(step.os_pass.predictor),
            corrector=point(selected),
            final=point(step.final),
            final_dense=final_dense,
            after_C=list(after.current.C),
            exact_resource_sum_delta=str(
                sum(map(q, after.current.C), fmpq(0))
                - sum(map(q, inputs.current.C), fmpq(0))
            ),
            charge=step.resource.charge.receipt_values(),
            charge_remainder=step.resource.charge.remainder,
            Q_target=inputs.Q_target,
            minimum_resource=min(after.current.C),
            continuity_evaluations=step.resource.continuity_evaluations,
            selector_path_segments=step.os_pass.selector_path_segments,
            split_certificate=step.os_pass.residual.execution_certificate.to_dict(),
            split_exact_values_digest=digest(step.os_pass.residual.exact_values),
            split_admitted=step.os_pass.residual.admitted,
            reset_unchanged=True,
            continuation_reference_geometry=True,
            final_C_rebuilt=True,
            initial_reset_readmitted=True,
            input_unchanged=True,
            dt=inputs.dt,
            before_step_index=inputs.step_index,
            after_step_index=after.step_index,
            before_time=inputs.time,
            after_time=after.time,
        )
        bound = next(
            c for c in read(BOUNDS)["cases"] if (c["graph"], c["role"]) == (graph, role)
        )
        dense = next(
            c
            for c in read(prior.RESULTS)["cases"]
            if (c["graph"], c["role"]) == (graph, role)
        )
        compare_output(result, declaration[graph], role, bound, dense, inputs.dt)
        return result


def worker(send, graph, role):
    try:
        value = execute(graph, role, lambda event: send.send(("progress", event)))
        send.send(("result", value))
    except Exception as error:
        send.send(
            (
                "error",
                dict(
                    type=type(error).__name__,
                    message=str(error),
                    stage=getattr(error, "stage", None),
                    code=getattr(error, "code", None),
                ),
            )
        )
    finally:
        send.close()


def run_case(graph, role):
    import flint

    m = read(INPUTS)
    require(m == manifest(), "native input/source drift")
    require(
        not (ROOT / case_path(graph, role)).exists(), "no overwrite of native evidence"
    )
    require(
        all(
            os.environ.get(k) == "1"
            for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")
        ),
        "select one thread explicitly",
    )
    require(flint.ctx.threads == 1, "single FLINT thread required")
    ctx = mp.get_context("spawn")
    receive, send = ctx.Pipe(duplex=False)
    process = ctx.Process(target=worker, args=(send, graph, role))
    start = time.monotonic()
    process.start()
    send.close()
    events = []
    result = dict(outcome="resource_limit")
    try:
        while time.monotonic() - start < m["case_cap_seconds"]:
            if receive.poll(0.1):
                try:
                    kind, value = receive.recv()
                except EOFError:
                    result = dict(outcome="worker_exit_without_result")
                    break
                if kind == "progress":
                    events.append(value)
                    print(json.dumps(dict(graph=graph, role=role, **value)), flush=True)
                else:
                    result = dict(
                        outcome="completed" if kind == "result" else "failed",
                        **{kind: value},
                    )
                    break
            elif not process.is_alive():
                result = dict(outcome="worker_exit_without_result")
                break
    finally:
        process.join(min(5, max(0, m["case_cap_seconds"] - (time.monotonic() - start))))
        terminated = process.is_alive()
        if terminated:
            process.terminate()
            process.join(1)
        if process.is_alive():
            process.kill()
            process.join()
        receive.close()
    record = seal(
        dict(
            schema="p984g-cos-native-case-v1",
            inputs_digest=m["record_digest"],
            graph=graph,
            role=role,
            **result,
            events=events,
            worker_seconds=time.monotonic() - start,
            worker_exitcode=process.exitcode,
            cleanup_terminated=terminated,
            numerical_policy=POLICY,
            python_flint=flint.__version__,
            threads=1,
            native_events=0,
            committed_steps=0,
            fallback_attempted=False,
        )
    )
    write_new(case_path(graph, role), record)
    print(
        json.dumps(
            dict(
                graph=graph,
                role=role,
                outcome=record["outcome"],
                seconds=record["worker_seconds"],
            )
        ),
        flush=True,
    )


def check_case(record, m):
    from flint import fmpq

    require(
        record == seal(record)
        and record["schema"] == "p984g-cos-native-case-v1"
        and record["inputs_digest"] == m["record_digest"],
        "case identity/source drift",
    )
    graph, role = record["graph"], record["role"]
    require((graph, role) in CASES, "unknown case")
    require(
        record["outcome"] == "completed"
        and record["worker_exitcode"] == 0
        and not record["cleanup_terminated"],
        "native case did not complete cleanly",
    )
    require(
        record["numerical_policy"] == POLICY
        and record["threads"] == 1
        and not record["fallback_attempted"]
        and record["native_events"] == record["committed_steps"] == 0,
        "case scope widening",
    )
    result = record["result"]
    declaration = read(prior.PREPARED)
    subject = declaration[graph]
    bound = next(
        c for c in read(BOUNDS)["cases"] if (c["graph"], c["role"]) == (graph, role)
    )
    dense = next(
        c
        for c in read(prior.RESULTS)["cases"]
        if (c["graph"], c["role"]) == (graph, role)
    )
    dt = declaration["selected_configuration"]["ordinary_dt"]
    compare_output(result, subject, role, bound, dense, dt)
    require(
        all(
            result[k] is True
            for k in (
                "split_admitted",
                "reset_unchanged",
                "continuation_reference_geometry",
                "final_C_rebuilt",
                "initial_reset_readmitted",
                "input_unchanged",
            )
        ),
        "missing native stage obligation",
    )
    require(
        result["continuity_evaluations"] == 1
        and result["selector_path_segments"] > 0
        and result["dt"] == dt
        and result["after_step_index"] == result["before_step_index"] + 1
        and result["after_time"] == result["before_time"] + dt,
        "step/stage counts",
    )
    require(
        result["minimum_resource"] == min(result["after_C"])
        and result["charge_remainder"] is None,
        "resource summary",
    )
    proof = result["split_certificate"]
    tolerance = fmpq(
        *float(
            subject["profile"]["params_resolved"]["realization"]["tolerance"]
        ).as_integer_ratio()
    )
    require(
        proof["method"] == "exact_weighted_row_sum_v1"
        and fmpq(proof["tolerance_exact"]) == tolerance
        and 0 <= fmpq(proof["weighted_row_bound"]) <= tolerance
        and fmpq(proof["margin_lower"])
        == tolerance - fmpq(proof["weighted_row_bound"]),
        "split proof drift",
    )
    return dict(
        graph=graph,
        role=role,
        minimum_resource=result["minimum_resource"],
        exact_resource_sum_delta=result["exact_resource_sum_delta"],
        worker_seconds=record["worker_seconds"],
    )


def summarize(m):
    rows = []
    for graph, role in CASES:
        path = case_path(graph, role)
        record = read(path)
        row = check_case(record, m)
        rows.append(
            dict(
                **row,
                path=path,
                sha256=hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                record_digest=record["record_digest"],
            )
        )
    return seal(
        dict(
            schema="p984g-cos-native-results-v1",
            inputs_digest=m["record_digest"],
            cases=rows,
            family="C_OS",
            numerical_steps=4,
            native_events=0,
            committed_steps=0,
            native_admission=True,
            status="C_OS_prerequisites_complete_pending_acceptance",
            scientifically_ready_for_8_4h=True,
            ready_for_8_4h=False,
            user_accepted=False,
            aggregate_closed=False,
            other_family_credit=0,
            uniform_trajectory_enclosure=False,
        )
    )


def check(m=None, r=None):
    m = read(INPUTS) if m is None else m
    r = read(RESULTS) if r is None else r
    require(m == manifest(), "native source drift")
    require(r == summarize(m), "native summary drift")
    return {k: v for k, v in r.items() if k != "record_digest"}


def write_new(name, value):
    content = json.dumps(value, indent=2, allow_nan=False) + "\n"
    require(len(content.encode()) <= 500000, "native evidence exceeds declared budget")
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run-case", "summarize", "check"))
    parser.add_argument("--graph", choices=("source", "target"))
    parser.add_argument("--role", choices=("current", "reset"))
    args = parser.parse_args()
    if args.action == "prepare":
        write_new(INPUTS, manifest())
    elif args.action == "run-case":
        run_case(args.graph, args.role)
    elif args.action == "summarize":
        m = read(INPUTS)
        require(m == manifest(), "source drift")
        write_new(RESULTS, summarize(m))
    else:
        print(json.dumps(check(), indent=2))


if __name__ == "__main__":
    main()
