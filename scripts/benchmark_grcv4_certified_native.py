"""One capped production C_OS pass: explicit policy, no research callbacks.

Retains successful numerical completion separately from bounded child teardown.
The large source is unchanged; this is not a complete step or P9-8.4g closure.
"""

import argparse
from dataclasses import replace
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DECLARATION = "implementation/phase-9-grcv4/tranche-8/larger-graph-examples/C_OS.json"
PREDECESSOR = (
    "implementation/evidence/grcv4-performance/weighted_split_os_pass_probe.json"
)


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def point(p):
    return {
        "current": list(p.current.values),
        "baseline": list(p.algebra.baseline.values),
        "read_flux": list(p.read.flux.values),
        "causal_flat": list(p.read.causal_flat.values),
        "closure_residual_squared": p.closure_residual_squared,
        "selector_rank": p.algebra.selector.rank,
        "current_block_digest": digest(p.algebra.current_block),
        "input_hodge_digest": digest(p.inputs.geometry.one_form_hodge.matrix),
        "retained_hodge_digest": digest(p.algebra.retained_hodge.matrix),
    }


def worker(connection):
    from pygrc.models.grc_v4_numerics import (
        ExactBackend,
        exact_backend,
        NumericalPolicy,
        numerical_policy,
    )
    from pygrc.models.grc_v4_realizations import CandidateCOSPass
    from pygrc.models.grc_v4_certification import CertificationInconclusive

    sys.path.insert(0, str(ROOT / "implementation/phase-9-grcv4/verification"))
    from prepare_p983_all_realizations import materialize

    try:
        with (
            exact_backend(ExactBackend.FLINT),
            numerical_policy(NumericalPolicy.CERTIFIED_ARB_256),
        ):
            record = json.loads((ROOT / DECLARATION).read_text())
            start = time.monotonic()
            state = materialize(record, "source")
            inputs = replace(
                state.inputs,
                stage="pre_read",
                dt=record["selected_configuration"]["ordinary_dt"],
            )
            setup = time.monotonic() - start
            connection.send(("progress", {"materialized_seconds": setup}))
            start = time.monotonic()
            result = CandidateCOSPass(inputs)
            elapsed = time.monotonic() - start
            old = json.loads((ROOT / PREDECESSOR).read_text())["result"]
            predictor, corrector = point(result.predictor), point(result.corrector)
            if predictor != old["predictor"] or corrector != old["corrector"]:
                raise ValueError(
                    "production points differ from retained research result"
                )
            if digest(result.residual.exact_values) != old["split_exact_values_digest"]:
                raise ValueError("production split operands changed")
            connection.send(
                (
                    "result",
                    {
                        "setup_seconds": setup,
                        "pass_seconds": elapsed,
                        "complete_os_pass": True,
                        "split_admitted": result.residual.admitted,
                        "selector_path_segments": result.selector_path_segments,
                        "split_certificate": result.residual.execution_certificate.to_dict(),
                        "predictor": predictor,
                        "corrector": corrector,
                        "split_exact_values_digest": digest(
                            result.residual.exact_values
                        ),
                        "matches_research_points": True,
                    },
                )
            )
    except Exception as exc:
        connection.send(
            (
                "error",
                {
                    "type": "certificate_inconclusive"
                    if isinstance(exc, CertificationInconclusive)
                    else type(exc).__name__,
                    "message": str(exc),
                },
            )
        )
    finally:
        connection.close()


def supervised(seconds):
    ctx = mp.get_context("spawn")
    receive, send = ctx.Pipe(duplex=False)
    process = ctx.Process(target=worker, args=(send,))
    start = time.monotonic()
    process.start()
    send.close()
    result = {"outcome": "resource_limit", "events": []}
    try:
        while time.monotonic() - start < seconds:
            if receive.poll(min(0.1, max(0, seconds - (time.monotonic() - start)))):
                try:
                    kind, payload = receive.recv()
                except EOFError:
                    result["outcome"] = "worker_exit_without_result"
                    break
                if kind == "progress":
                    result["events"].append(payload)
                    print(json.dumps(payload), flush=True)
                else:
                    result.update(
                        outcome="completed" if kind == "result" else "failed",
                        **{kind: payload},
                    )
                    break
            elif not process.is_alive():
                result["outcome"] = "worker_exit_without_result"
                break
    finally:
        # Teardown has an explicit bounded allowance and a separate outcome.
        process.join(min(5, max(0, seconds - (time.monotonic() - start))))
        terminated = process.is_alive()
        if terminated:
            process.terminate()
            process.join(1)
        if process.is_alive():
            process.kill()
            process.join()
        receive.close()
    return {
        **result,
        "worker_wall_seconds": time.monotonic() - start,
        "worker_exitcode": process.exitcode,
        "cleanup_terminated": terminated,
        "deadline_seconds": seconds,
        "fallback_attempted": False,
    }


def main():
    from pygrc.models.grc_v4_certification import NumericalPolicy
    import flint

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--policy", required=True, choices=[NumericalPolicy.CERTIFIED_ARB_256.value]
    )
    parser.add_argument("--seconds", required=True, type=float)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not 0 < args.seconds < float("inf"):
        raise ValueError("positive finite deadline required")
    output = args.output.resolve().relative_to(ROOT)
    if (ROOT / output).exists():
        raise ValueError("output already exists")
    sources = [
        Path(__file__).relative_to(ROOT).as_posix(),
        DECLARATION,
        "implementation/phase-9-grcv4/verification/prepare_p983_all_realizations.py",
        "implementation/phase-9-grcv4/verification/prepare_p983_graph_admission.py",
    ]
    sources += sorted(
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "src/pygrc/models").glob("*grc*v4*.py")
    )
    report = {
        "schema": "grcv4-certified-native-probe-v1",
        "execution_policy": args.policy,
        "exact_backend": "flint",
        "python_flint": flint.__version__,
        "flint_threads": flint.ctx.threads,
        "thread_settings": {
            k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")
        },
        "source_bindings": {
            p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources
        },
        "predecessor_record_digest": json.loads((ROOT / PREDECESSOR).read_text())[
            "record_digest"
        ],
        "production_code_path": True,
        "research_callbacks": False,
        "native_steps": 0,
        "native_events": 0,
        "aggregate_closed": False,
        **supervised(args.seconds),
    }
    report["record_digest"] = digest(report)
    with (ROOT / output).open("x") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "outcome",
                    "worker_wall_seconds",
                    "worker_exitcode",
                    "cleanup_terminated",
                )
            }
        )
    )
    if report["outcome"] != "completed":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
