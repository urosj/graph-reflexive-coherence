"""Complete C_CI without rerunning its eight retained passing cases.

Only the operational case budget changes (180 to 480 seconds). The original
timeout remains visible, not promoted. The source beat is explicitly reused
from its exact execution record; every remaining event reads it afresh.
"""

import argparse
from copy import deepcopy
from importlib.metadata import version
import json
import platform

import p984b_cci_runtime as r

b = r.b
SELF = b.HERE + "p984b_cci_completion.py"
TEST = b.HERE + "test_p984b_cci_completion.py"
INPUTS = b.BASE + "P9-8.4b-CCICompletionCases.json"
RESULTS = b.BASE + "P9-8.4b-CCICompletionResults.json"


def predecessor():
    manifest, results = b.read(r.INPUTS), b.read(r.RESULTS)
    r.check_manifest(manifest)
    b.check_digest(results)
    b.require(
        results["manifest_digest"] == manifest["record_digest"],
        "predecessor manifest drift",
    )
    b.require(
        len(results["cases"]) == 9
        and all(c["case_passed"] for c in results["cases"][:8]),
        "expected eight retained passes",
    )
    failed = results["cases"][8]
    b.require(
        not failed["case_passed"]
        and failed["event_committed"] is True
        and failed["first_failure"]["kind"] == "operational_timeout"
        and failed["first_failure"]["role"] == "reset",
        "original timeout disposition drift",
    )
    b.require(
        results["user_accepted"] is False and results["aggregate_closed"] is False,
        "predecessor scope drift",
    )
    return manifest, results


def make_manifest():
    old, execution = predecessor()
    value = deepcopy(old)
    value["schema"] = "p984b-cci-completion-inputs-v1"
    value["predecessor_execution"] = dict(
        path=r.RESULTS,
        record_digest=execution["record_digest"],
        retained_passing_cases=8,
        original_incomplete_cases=1,
        previously_unrun_cases=7,
    )
    value["shared_source_rule"] = (
        "reuse exact recorded native source beat; no new source beat claimed"
    )
    for case in value["cases"][8:]:
        case["case_id"] += "-BUDGET480"
        case["execution_budget_seconds"] = 480
    value["source_bindings"] += b.bind([r.INPUTS, r.RESULTS, SELF, TEST])
    return b.seal(value)


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(
        manifest == make_manifest(),
        "completion changed more than named operational budget",
    )


def validate(manifest, result, *, numerics=False):
    old, execution = predecessor()
    b.require(
        result["shared"] == execution["shared"], "retained source execution changed"
    )
    b.require(
        result["cases"][:8] == execution["cases"][:8],
        "retained successful execution changed",
    )
    b.require(
        result["execution_partition"]
        == dict(
            retained_cases=8,
            newly_executed_cases=8,
            retained_source_beats=1,
            new_source_beats=0,
            predecessor_record_digest=execution["record_digest"],
        ),
        "execution reuse/new-work scope drift",
    )
    b.require(
        result["original_first_failure"] == execution["cases"][8]["first_failure"],
        "original failure hidden",
    )
    for original, successor in zip(
        old["cases"][8:], manifest["cases"][8:], strict=True
    ):
        expected = {
            **original,
            "case_id": original["case_id"] + "-BUDGET480",
            "execution_budget_seconds": 480,
        }
        b.require(
            successor == expected, "scientific inputs changed in operational successor"
        )
    return {
        **r.validate(manifest, result, numerics=numerics),
        **result["execution_partition"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--output", default=RESULTS)
    args = parser.parse_args()
    b.require(
        not args.recheck_numerics or args.check_retained,
        "recheck requires retained mode",
    )
    b.require(
        not b.Path(args.output).is_absolute() and ".." not in b.Path(args.output).parts,
        "repository-relative output required",
    )
    if args.prepare:
        b.write_new(INPUTS, make_manifest())
        print("C_CI completion inputs bound; no native execution")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    if args.check_retained:
        print(
            json.dumps(
                validate(manifest, b.read(args.output), numerics=args.recheck_numerics),
                indent=2,
            )
        )
        return
    b.require(not (b.ROOT / args.output).exists(), "refusing to overwrite execution")
    _, execution = predecessor()
    results = dict(
        schema="p984b-cci-completion-results-v1",
        manifest_digest=manifest["record_digest"],
        environment=dict(
            python=platform.python_version(),
            numpy=version("numpy"),
            mpmath=version("mpmath"),
            python_flint=version("python-flint"),
        ),
        shared=execution["shared"],
        cases=deepcopy(execution["cases"][:8]),
        execution_partition=dict(
            retained_cases=8,
            newly_executed_cases=8,
            retained_source_beats=1,
            new_source_beats=0,
            predecessor_record_digest=execution["record_digest"],
        ),
        original_first_failure=execution["cases"][8]["first_failure"],
        native_runtime_executed=True,
        user_accepted=False,
        aggregate_closed=False,
    )
    with b.exact_backend(b.ExactBackend.FLINT):
        seed = r.state(execution["shared"]["actual_source"])
        for case in manifest["cases"][8:]:
            row = r.execute_case(seed, case)
            results["cases"].append(row)
            print(case["fixture_id"], row["outcome"], row["first_failure"], flush=True)
            if not row["case_passed"]:
                break
    results["execution_partition"]["newly_executed_cases"] = len(results["cases"]) - 8
    results = b.seal(results)
    b.write_new(args.output, results)
    if len(results["cases"]) != 16:
        print("INCOMPLETE_COMPLETION: first failure retained; remaining cases not run")
        raise SystemExit(1)
    report = validate(manifest, results)
    print(json.dumps({**report, "native_execution_in_this_command": True}, indent=2))
    if report["cases_passed"] != 16:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
