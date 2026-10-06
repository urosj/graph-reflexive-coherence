"""Recompute every completed A_RG2b case; publish only the complete final report."""

import argparse
import time
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy

import p984b_arg2b_runtime as r

SELF = r.b.HERE + "p984b_arg2b_recheck.py"
OUTPUT = r.b.BASE + "P9-8.4b-ARG2bNumericalRecheck.json"


def check_case(index):
    manifest, result = r.b.read(r.INPUTS), r.b.read(r.RESULTS)
    r.b.check_digest(manifest)
    r.b.check_digest(result)
    row = result["cases"][index]
    case = manifest["cases"][index]
    r.b.require(row["case_id"] == case["case_id"], "case selection drift")
    # Slice only the roster. validate still checks the unchanged full-manifest
    # identity and authenticates every original case and shared-source operand.
    subset = deepcopy(manifest)
    subset["cases"] = [case]
    selected = r.b.seal({**result, "cases": [row]})
    with r.b.exact_backend(r.b.ExactBackend.FLINT), r.native_disabled():
        checked = r.validate(subset, selected, numerics=True)
    r.b.require(checked["cases_passed"] == 1, "missing completed numerical case")
    return {
        "case_id": row["case_id"],
        "case_digest": r.b.digest(row),
        "shared_digest": r.b.digest(result["shared"]),
        "successful_history_cells": 2,
        "interval_equations_recomputed": True,
        "native_trajectories_rerun": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=4)
    args = parser.parse_args()
    started = time.monotonic()
    manifest, result = r.b.read(r.INPUTS), r.b.read(r.RESULTS)
    r.check_manifest(manifest)
    r.b.check_digest(result)
    # Each worker runs the complete validator on its original case plus the
    # shared source. Exact partition/identity checks replace a redundant
    # parent pass over all the same chains; no numerical check is omitted.
    r.b.require(
        len(result["cases"]) == 16
        and [row["case_id"] for row in result["cases"]]
        == [case["case_id"] for case in manifest["cases"]],
        "complete all-layout result required",
    )
    bindings = r.b.bind([SELF, r.SELF, r.TEST, r.INPUTS, r.RESULTS])
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        checks = []
        for check in pool.map(check_case, range(16)):
            checks.append(check)
            print("ARG2b_RECHECK_PASS " + check["case_id"], flush=True)
    r.b.check_bindings(bindings)
    r.b.check_bindings(manifest["source_bindings"])
    r.b.require(
        [c["case_id"] for c in checks] == [v["case_id"] for v in result["cases"]]
        and all(
            c["case_digest"] == r.b.digest(row)
            and c["shared_digest"] == r.b.digest(result["shared"])
            for c, row in zip(checks, result["cases"], strict=True)
        ),
        "numerical case/shared source binding drift",
    )
    report = r.b.seal(
        {
            "schema": "p984b-arg2b-independent-recheck-v1",
            "manifest_digest": manifest["record_digest"],
            "runtime_digest": result["record_digest"],
            "cases_passed": 16,
            "successful_history_cells": 32,
            "cases": checks,
            "interval_equations_recomputed": True,
            "native_entry_points_disabled": True,
            "native_trajectories_rerun": False,
            "user_accepted": False,
            "aggregate_closed": False,
            "source_bindings": bindings,
            "workers": args.workers,
            "elapsed_seconds": time.monotonic() - started,
        }
    )
    r.write_new(OUTPUT, report)
    print(
        f"ARG2b_RECHECK_COMPLETE cases=16 cells=32 seconds={report['elapsed_seconds']:.1f}"
    )


if __name__ == "__main__":
    main()
