"""Recompute complete saved C_RG2b cases; optionally follow a running journal.

The journal is only a progress source. A successful final record requires the
complete final artifact, exact case agreement, source pins and full validation.
Native solver, step and event entry points are disabled during recomputation.
"""

import argparse
import json
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from unittest.mock import patch

import p984b_crg2b_resume as recovery
import p984b_crg2b_runtime as r

from pygrc.models import grc_9_v4_rg2b as signed
from pygrc.models import grc_v4_candidate_c as candidate
from pygrc.models import grc_v4_rg2b as rg

b = r.b
SELF = b.HERE + "p984b_crg2b_recheck.py"
RESULT = b.BASE + "P9-8.4b-CRG2bNumericalRecheck.json"


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
        patch.object(rg, "CandidateRG2bSection", side_effect=forbidden),
        patch.object(rg, "ProvisionalCandidateRG2bStep", side_effect=forbidden),
        patch.object(signed, "propose", side_effect=forbidden),
        patch.object(signed, "certify_chain", side_effect=forbidden),
        patch.object(signed, "literal", side_effect=forbidden),
        patch.object(candidate, "CandidateCCurrent", side_effect=forbidden),
        patch.object(r, "CandidateCCurrent", side_effect=forbidden),
        patch.object(r.native.GRC9V4CRG2bOperation, "expand", side_effect=forbidden),
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


CHECKPOINTS = b.BASE + "P9-8.4b-CRG2bRecheckProgress"


def checkpoint_context(manifest, shared):
    return {
        "schema": "p984b-crg2b-recheck-checkpoint-v1",
        "manifest_digest": manifest["record_digest"],
        "shared_digest": b.digest(shared),
        "source_bindings": b.bind(
            [
                SELF,
                recovery.SELF,
                recovery.TEST,
                r.SELF,
                r.TEST,
                r.INPUTS,
                b.HERE + "test_p980_rg2b_numerical.py",
            ]
        ),
    }


def check_checkpoint(record, context, case, row):
    b.check_digest(record)
    b.require(record["context"] == context, "recheck checkpoint source/subject drift")
    expected = {
        "case_id": case["case_id"],
        "case_digest": b.digest(row),
        "shared_digest": context["shared_digest"],
        "successful_history_cells": 2,
        "interval_equations_recomputed": True,
        "native_trajectories_rerun": False,
    }
    b.require(
        b.digest(record["check"]) == b.digest(expected),
        "recheck checkpoint case/scope drift",
    )
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--follow", action="store_true")
    parser.add_argument("--output", default=RESULT)
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=3)
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
    directory = b.ROOT / CHECKPOINTS
    directory.mkdir(exist_ok=True)
    checks, pending = {}, {}
    cache_key, shared, rows, context = None, None, [], None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        while len(checks) < len(manifest["cases"]):
            final_path = b.ROOT / r.RESULTS
            path = final_path if final_path.exists() else journal
            if not path.exists():
                b.require(args.follow, "final artifact required without --follow")
                time.sleep(1)
                continue
            stat = path.stat()
            key = (str(path), stat.st_size, stat.st_mtime_ns)
            if key != cache_key:
                if path == final_path:
                    final = b.read(r.RESULTS)
                    b.check_digest(final)
                    b.require(
                        final["manifest_digest"] == manifest["record_digest"],
                        "final manifest drift",
                    )
                    new_shared, new_rows = final["shared"], final["cases"]
                else:
                    b.require(args.follow, "final artifact required without --follow")
                    raw = path.read_bytes()
                    # Only terminated lines are evidence; retry any active write.
                    raw = raw[: raw.rfind(b"\n") + 1]
                    if not raw:
                        time.sleep(1)
                        continue
                    header, new_rows = recovery.decode_journal(raw, manifest)
                    new_shared = header["shared"]
                new_context = checkpoint_context(manifest, new_shared)
                b.require(
                    context is None or context == new_context,
                    "running recheck subject drift",
                )
                shared, rows, context, cache_key = (
                    new_shared,
                    new_rows,
                    new_context,
                    key,
                )
                b.require(len(rows) <= len(manifest["cases"]), "foreign cases")
                for index, row in enumerate(rows):
                    case = manifest["cases"][index]
                    b.require(
                        row["case_id"] == case["case_id"] and row["case_passed"],
                        "incomplete/reordered case",
                    )
                    if index in checks:
                        b.require(
                            checks[index]["case_digest"] == b.digest(row),
                            "previously checked case drift",
                        )
            active = set(pending.values())
            for index, row in enumerate(rows):
                if index in checks or index in active:
                    continue
                case = manifest["cases"][index]
                checkpoint = directory / (b.digest(case["case_id"]) + ".json")
                if checkpoint.exists():
                    checks[index] = check_checkpoint(
                        json.loads(checkpoint.read_text()), context, case, row
                    )
                    print(
                        "CRG2b_INTERVAL_CHECKPOINT_REUSED", case["case_id"], flush=True
                    )
                elif len(pending) < args.workers:
                    pending[pool.submit(recheck_case, manifest, shared, case, row)] = (
                        index
                    )
            done, _ = (
                wait(pending, timeout=1, return_when=FIRST_COMPLETED)
                if pending
                else (set(), set())
            )
            for future in done:
                index = pending.pop(future)
                check = future.result()
                case, row = manifest["cases"][index], rows[index]
                record = b.seal({"context": context, "check": check})
                check_checkpoint(record, context, case, row)
                recovery.publish(
                    directory / (b.digest(case["case_id"]) + ".json"), record
                )
                checks[index] = check
                print("CRG2b_INTERVAL_CASE_PASS", case["case_id"], flush=True)
            if not pending and len(checks) < len(manifest["cases"]):
                b.require(not final_path.exists(), "final campaign incomplete")
                time.sleep(1)
    while not (b.ROOT / r.RESULTS).exists():
        time.sleep(1)
    final = b.read(r.RESULTS)
    r.check_manifest(manifest)
    b.require(
        context == checkpoint_context(manifest, final["shared"]),
        "final recheck subject drift",
    )
    report = r.validate(manifest, final)
    ordered = [checks[i] for i in range(len(manifest["cases"]))]
    b.require(
        all(
            check["case_digest"] == b.digest(row)
            and check["shared_digest"] == b.digest(final["shared"])
            for check, row in zip(ordered, final["cases"], strict=True)
        ),
        "final cases differ from recomputed cases",
    )
    checkpoint_paths = [
        CHECKPOINTS + "/" + b.digest(case["case_id"]) + ".json"
        for case in manifest["cases"]
    ]
    record = b.seal(
        {
            "schema": "p984b-crg2b-independent-recheck-v1",
            "manifest_digest": manifest["record_digest"],
            "runtime_digest": final["record_digest"],
            "source_bindings": b.bind(
                [
                    *[ref["path"] for ref in context["source_bindings"]],
                    r.RESULTS,
                    *checkpoint_paths,
                ]
            ),
            "cases": ordered,
            "cases_passed": report["cases_passed"],
            "successful_history_cells": report["successful_history_cells"],
            "interval_equations_recomputed": True,
            "native_entry_points_disabled": True,
            "native_trajectories_rerun": False,
            "durable_case_checkpoints": checkpoint_paths,
            "workers": args.workers,
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )
    recovery.publish(b.ROOT / args.output, record)
    print(
        "CRG2b_FULL_INTERVAL_RECHECK_PASS cases=16 cells=32 native_rerun=false",
        flush=True,
    )


if __name__ == "__main__":
    main()
