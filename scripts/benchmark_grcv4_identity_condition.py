"""Explicit exact near-identity certificate probe; never a production fallback.

For E=A/s-I and d=max(||E||_1,||E||_inf)<1, ||E||_2<=d. Thus
|s|(1-d)<=sigma_min(A)<=sigma_max(A)<=|s|(1+d). The condition
upper bound is (1+d)/(1-d). Failure of this sufficient certificate is
INCONCLUSIVE, not proof of singularity or excessive conditioning.
"""

import argparse
import hashlib
import math
import multiprocessing as mp
import time

from scripts import benchmark_grcv4_exact_direct as probe


def certify(a, scale, limit):
    scale, limit = probe.q(scale), probe.q(limit)
    n = a.nrows()
    probe.require(n > 0 and a.ncols() == n and scale != 0 and limit >= 1,
                  "nonempty square matrix, nonzero scale and limit >= 1 required")
    rows = [probe.q(0) for _ in range(n)]
    cols = rows.copy()
    for i in range(n):
        for j in range(n):
            value = abs(a[i, j] / scale - int(i == j))
            rows[i] += value
            cols[j] += value
    one, infinity = max(cols), max(rows)
    d = max(one, infinity)
    result = {"method": "exact_scaled_identity_induced_norm_v1", "scale": str(scale),
        "one_norm_deviation": str(one), "infinity_norm_deviation": str(infinity),
        "norm_2_deviation_upper": str(d), "limit": str(limit), "inverse_constructed": False}
    if d >= 1:
        return {**result, "outcome": "inconclusive", "reason": "positive_singular_value_lower_bound_unavailable"}
    bound = ((1 + d) / (1 - d)) ** 2
    result.update(singular_value_lower=str(abs(scale) * (1 - d)),
                  singular_value_upper=str(abs(scale) * (1 + d)),
                  condition_upper_squared=str(bound), nonsingular=True)
    if bound > limit**2:
        return {**result, "outcome": "inconclusive", "reason": "sufficient_bound_exceeds_limit"}
    return {**result, "outcome": "certified"}


def worker(connection, path):
    try:
        value, a, _ = probe.load_block(path)
        start = time.monotonic()
        result = certify(a, 1, value["policy"]["conditioning_limit"])
        connection.send(("result", {"certificate": result, "condition_seconds": time.monotonic() - start,
                                    "block_digest": value["block_digest"]}))
    except Exception as exc:
        connection.send(("error", {"type": type(exc).__name__, "message": str(exc)}))
    finally:
        connection.close()


def supervised(path, seconds):
    probe.require(math.isfinite(seconds) and seconds > 0, "positive finite deadline required")
    context = mp.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    process = context.Process(target=worker, args=(send, path))
    start = time.monotonic()
    process.start()
    send.close()
    result = {"outcome": "resource_limit"}
    try:
        if receive.poll(max(0, seconds - (time.monotonic() - start))):
            try:
                kind, payload = receive.recv()
                result = {"outcome": "completed" if kind == "result" else "failed", kind: payload}
            except EOFError:
                result = {"outcome": "worker_exit_without_result"}
    finally:
        process.join(.1)
        if process.is_alive():
            process.terminate()
            process.join(1)
        if process.is_alive():
            process.kill()
            process.join()
        receive.close()
    return {**result, "worker_wall_seconds": time.monotonic() - start,
            "worker_exitcode": process.exitcode, "deadline_seconds": seconds, "fallback_attempted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--block", required=True, type=probe.Path)
    parser.add_argument("--output", required=True, type=probe.Path)
    parser.add_argument("--seconds", required=True, type=float)
    args = parser.parse_args()
    block = args.block.resolve().relative_to(probe.ROOT)
    output = args.output.resolve().relative_to(probe.ROOT)
    probe.require(not (probe.ROOT / output).exists(), "report already exists")
    sources = ["scripts/benchmark_grcv4_identity_condition.py", "scripts/benchmark_grcv4_exact_direct.py"]
    result = {"schema": "grcv4-identity-condition-probe-v1", "block_path": block.as_posix(),
        "algorithm": "exact_scaled_identity_induced_norm_v1", "scale": "1",
        "source_bindings": {p: hashlib.sha256((probe.ROOT / p).read_bytes()).hexdigest() for p in sources},
        "production_admission": False,
        **supervised(probe.ROOT / block, args.seconds)}
    result["record_digest"] = probe.digest(result)
    probe.write_new(probe.ROOT / output, result)
    print(probe.json.dumps({k: v for k, v in result.items() if k in ("outcome", "worker_wall_seconds", "error")}))


if __name__ == "__main__":
    main()
