"""Recompute complete saved A_CI+PC cases; optionally follow a running journal.

The journal is only a progress source. A successful final record requires the
complete final artifact, exact case agreement, source pins and full validation.
Native solver, step and event entry points are disabled during recomputation.
"""

import argparse
import json
import time
from pathlib import Path
from unittest.mock import patch

import p984b_acipc_runtime as r

from pygrc.models import grc_v4_ci as ci

b = r.b
SELF = b.HERE + "p984b_acipc_recheck.py"
RESULT = b.BASE + "P9-8.4b-ACIPCNumericalRecheck.json"


def recheck_case(manifest, shared, case, row):
    """Reuse the frozen retained checker over exactly one identified case."""
    b.require(row["case_passed"], "cannot certify an incomplete case")
    subset = b.seal({**manifest, "cases": [case]})
    result = b.seal(
        {
            "manifest_digest": subset["record_digest"],
            "shared": shared,
            "cases": [row],
            "native_runtime_executed": True,
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )
    forbidden = AssertionError(
        "native execution forbidden during retained recomputation"
    )
    with (
        patch.object(ci, "CandidateCIRoot", side_effect=forbidden),
        patch.object(r, "CandidateCIRoot", side_effect=forbidden),
        patch.object(r, "ProvisionalCandidateCIStep", side_effect=forbidden),
        patch.object(ci, "ProvisionalCandidateCIStep", side_effect=forbidden),
        patch.object(r.native, "ProvisionalCandidateCIStep", side_effect=forbidden),
        patch.object(r.native.GRC9V4ACIPCOperation, "expand", side_effect=forbidden),
    ):
        report = r.validate(subset, result, numerics=True)
    b.require(
        report["cases_passed"] == 1 and report["successful_history_cells"] == 2,
        "single-case recomputation incomplete",
    )
    return {
        "case_id": case["case_id"],
        "case_digest": b.digest(row),
        "shared_digest": b.digest(shared),
        "successful_history_cells": 2,
        "interval_equations_recomputed": True,
        "native_trajectories_rerun": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--follow", action="store_true")
    parser.add_argument("--output", default=RESULT)
    args = parser.parse_args()
    b.require(
        not Path(args.output).is_absolute() and ".." not in Path(args.output).parts,
        "repository-relative output required",
    )
    b.require(
        not (b.ROOT / args.output).exists(), "refusing to overwrite numerical evidence"
    )
    manifest = b.read(r.INPUTS)
    r.check_manifest(manifest)
    journal = b.ROOT / (r.RESULTS + ".progress.jsonl")
    checks = []
    while len(checks) < len(manifest["cases"]):
        if (b.ROOT / r.RESULTS).exists():
            final = b.read(r.RESULTS)
            b.check_digest(final)
            shared, rows = final["shared"], final["cases"]
        else:
            b.require(args.follow, "final artifact required without --follow")
            # Only complete newline-terminated entries are eligible. A partial
            # write supplies no evidence and is reconsidered on the next pass.
            lines = journal.read_bytes().splitlines(keepends=True)
            records = [json.loads(line) for line in lines if line.endswith(b"\n")]
            for record in records:
                b.check_digest(record)
            b.require(
                records[0]["manifest_digest"] == manifest["record_digest"],
                "journal manifest drift",
            )
            shared = records[0]["shared"]
            rows = [
                {k: v for k, v in row.items() if k != "record_digest"}
                for row in records[1:]
            ]
        b.require(len(rows) <= len(manifest["cases"]), "foreign journal cases")
        for index in range(len(checks), len(rows)):
            case, row = manifest["cases"][index], rows[index]
            b.require(row["case_id"] == case["case_id"], "journal case order drift")
            checks.append(recheck_case(manifest, shared, case, row))
            print("ACIPC_INTERVAL_CASE_PASS", case["case_id"], flush=True)
        if (b.ROOT / r.RESULTS).exists():
            b.require(
                len(checks) == len(manifest["cases"]), "final campaign incomplete"
            )
        elif len(checks) < len(manifest["cases"]):
            time.sleep(1)
    # Completion cannot be inferred solely from a journal, even if its last
    # case has passed. The owner must publish and validate its final artifact.
    while not (b.ROOT / r.RESULTS).exists():
        time.sleep(1)
    final = b.read(r.RESULTS)
    r.check_manifest(manifest)
    report = r.validate(manifest, final)
    b.require(
        all(
            check["case_digest"] == b.digest(row)
            and check["shared_digest"] == b.digest(final["shared"])
            for check, row in zip(checks, final["cases"], strict=True)
        ),
        "final cases differ from recomputed cases",
    )
    record = b.seal(
        {
            "schema": "p984b-acipc-independent-recheck-v1",
            "manifest_digest": manifest["record_digest"],
            "runtime_digest": final["record_digest"],
            "source_bindings": b.bind(
                [
                    SELF,
                    r.SELF,
                    r.TEST,
                    r.INPUTS,
                    r.RESULTS,
                    b.HERE + "verify_p983a_acipc_oracle.py",
                ]
            ),
            "cases": checks,
            "cases_passed": report["cases_passed"],
            "successful_history_cells": report["successful_history_cells"],
            "interval_equations_recomputed": True,
            "native_entry_points_disabled": True,
            "native_trajectories_rerun": False,
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )
    r.write_new(args.output, record)
    print(
        "ACIPC_FULL_INTERVAL_RECHECK_PASS cases=16 cells=32 native_rerun=false",
        flush=True,
    )


if __name__ == "__main__":
    main()
