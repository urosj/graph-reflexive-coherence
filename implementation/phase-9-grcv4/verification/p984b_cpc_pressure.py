"""Independent signed Read-Back/flat pressure on retained C_PC execution.

The structural outer product alone cannot detect a simultaneous sign reversal
of the lowered vector. Certify both intermediate vectors themselves without
rerunning or rewriting native trajectories. Source pins are portable.
"""

import argparse
import json
from dataclasses import replace
from fractions import Fraction as Q

import p984b_cpc_runtime as r
from test_p980_os_effect_witness import IV, full_error, inverse, number

b = r.b
SELF = b.HERE + "p984b_cpc_pressure.py"
TEST = b.HERE + "test_p984b_cpc_pressure.py"
RESULT = b.BASE + "P9-8.4b-CPCScientificPressure.json"
CLAIMS = "implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"
LIMIT = Q(1, 2**36)


def check_vectors(before, value):
    truth = r.truth(before)
    high = truth["high"]
    mean_exp = IV.exp(2 * sum(truth["c"]) / len(before.current.C))
    t = IV.exp(number(Q(1, 2**24)) * (mean_exp - 1) / (mean_exp + 1))
    chi = before.geometry.reference.profile.params_resolved.candidate.chi_C
    readback = (
        number(chi) * inverse(high.I + t * truth["H"] * high.D) * truth["read"]["J"]
    )
    flat = inverse(truth["H"]) * readback
    errors = {
        "readback_error": full_error(value["readback"], readback),
        "flat_error": full_error(value["flat"], flat),
    }
    b.require(
        all(0 <= x < LIMIT for x in errors.values()),
        "signed intermediate full error unresolved",
    )
    return {
        "input_identity": before.identity,
        "read_record_digest": value["record_digest"],
        **{k: str(v) for k, v in errors.items()},
    }


def read_rows(manifest, results):
    initial = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])

    def step_rows(label, before, step):
        yield label + "/read", before, step["read"]
        yield label + "/reset", r.role_input(before, "reset"), step["reset_read"]
        following = b.GeometryStageInputs.from_payload(step["poststate"])
        yield label + "/restart", replace(following, dt=0), step["restart"]

    yield from step_rows("source", initial, results["shared"]["source_step"])
    seed = r.state(results["shared"]["actual_source"])
    for case, row in zip(manifest["cases"], results["cases"], strict=True):
        target = r.state(row["event"]["actual_target"])
        label = case["case_id"]
        for side, parent, admission in zip(
            ("source", "target"),
            (seed, target),
            row["event"]["admission_reads"],
            strict=True,
        ):
            yield label + "/" + side + "/read", parent.inputs, admission["read"]
            yield (
                label + "/" + side + "/reset",
                r.role_input(parent.inputs, "reset"),
                admission["reset_read"],
            )
        for role in r.ROLES:
            before = r.role_input(target.inputs, role, dt=b.DT)
            for item in (v for v in row["continuation"] if v["role"] == role):
                yield from step_rows(
                    label + "/" + role + "/" + str(item["index"]), before, item["step"]
                )
                before = b.GeometryStageInputs.from_payload(item["step"]["poststate"])
            yield (
                label + "/" + role + "/final",
                replace(before, dt=0),
                row["final_reads"][role],
            )


def generate(manifest, results):
    b.require(
        len(results["cases"]) == 17 and all(x["case_passed"] for x in results["cases"]),
        "complete retained C_PC execution required",
    )
    rows = [
        {"stage": label, **check_vectors(before, value)}
        for label, before, value in read_rows(manifest, results)
    ]
    b.require(len(rows) == 1125, "read roster drift")
    return b.seal(
        {
            "schema": "p984b-cpc-signed-stage-pressure-v1",
            "native_trajectories_rerun": False,
            "manifest_digest": manifest["record_digest"],
            "runtime_digest": results["record_digest"],
            "absolute_error_limit": str(LIMIT),
            "interval_digits": 60,
            "reads": rows,
            "source_bindings": b.bind(
                [r.INPUTS, r.RESULTS, r.SELF, SELF, TEST, CLAIMS]
            ),
            "claim_restrictions": {
                "D10-CL-O-006": "scalar_ZOH_PC_only",
                "D10-CL-C-004": "no_committed_endpoint_hysteresis_inferred",
                "D10-CL-C-012": "no_universal_realization_or_graph_support",
            },
            "user_accepted": False,
            "aggregate_closed": False,
        }
    )


def validate(report, manifest, results, *, numerics=False):
    b.check_digest(report)
    b.check_bindings(report["source_bindings"])
    b.require(
        report["manifest_digest"] == manifest["record_digest"]
        and report["runtime_digest"] == results["record_digest"]
        and report["absolute_error_limit"] == str(LIMIT)
        and report["user_accepted"] is False
        and report["aggregate_closed"] is False
        and report["native_trajectories_rerun"] is False,
        "pressure scope/binding drift",
    )
    expected = [
        (label, before.identity, value["record_digest"])
        for label, before, value in read_rows(manifest, results)
    ]
    b.require(
        len(expected) == 1125
        and expected
        == [
            (v["stage"], v["input_identity"], v["read_record_digest"])
            for v in report["reads"]
        ],
        "pressure stage roster drift",
    )
    b.require(
        all(
            0 <= Q(v[k]) < LIMIT
            for v in report["reads"]
            for k in ("readback_error", "flat_error")
        ),
        "pressure error ceiling drift",
    )
    if numerics:
        b.require(
            report == generate(manifest, results), "signed interval evidence drift"
        )
    return {
        "signed_readback_and_flat": "passed",
        "reads": len(expected),
        "native_trajectories_rerun": False,
        "interval_equations_recomputed": numerics,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check-retained", action="store_true")
    parser.add_argument("--recheck-numerics", action="store_true")
    args = parser.parse_args()
    b.require(
        not args.recheck_numerics or args.check_retained, "recheck needs retained mode"
    )
    manifest, results = b.read(r.INPUTS), b.read(r.RESULTS)
    r.check_manifest(manifest)
    b.check_digest(results)
    if args.write:
        b.require(
            not (b.ROOT / RESULT).exists(), "refusing to overwrite signed pressure"
        )
        report = generate(manifest, results)
        r.write_new(RESULT, report)
    else:
        report = b.read(RESULT)
    print(
        json.dumps(
            validate(report, manifest, results, numerics=args.recheck_numerics),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
