"""Retained A_OS evidence reader for the original execution package.

The execution harness is frozen by its cost/trajectory source bindings. This
reader uses the public exact_state codec (the frozen generator's readback helper
mistakenly names a nonexistent class factory). No runtime, source sample, primary
state or mathematical witness changes.
"""

import argparse
import json
import lzma
from hashlib import sha256
from pathlib import Path

from flint import fmpq as Q
from p991a5_native_spark_verify import need
from p991a6_aos_campaign import EXPECTED, FILES, RECORD, ROOT, seal
from p991a6_aos_campaign_verify import (
    classification_digest,
    compact,
    expand,
    membership_bounds,
    validate_staging,
    verify,
)

from pygrc.models.grc_v4_spark_carrier import exact_state

SELF = "implementation/phase-9-grcv4/verification/p991a6_aos_evidence.py"


def check(root=ROOT, numerical=False):
    from p991a6_aci_epoch import previous_bytes

    root = Path(root)
    with lzma.open(root / RECORD, "rb") as stream:
        value = json.load(stream)
    need(
        value == seal(value) and value["schema"] == "grc9v4-native-aos-campaign-v1",
        "unsealed campaign",
    )
    for ref in [*value["source_bindings"], *value["streams"]]:
        need(
            sha256(previous_bytes(root, ref["path"])).hexdigest() == ref["sha256"],
            "changed campaign input: " + ref["path"],
        )
    source = None
    compact_samples = {}
    diagnostic_keys = []
    for name in ("inputs", "current", "reset", "checkpoints", "diagnostics"):
        ref = next(x for x in value["streams"] if x["path"] == FILES[name])
        count = 0
        previous = None
        C = None
        gains = 0
        window = []
        entry = None
        with lzma.open(root / ref["path"], "rt") as stream:
            for line in stream:
                row = json.loads(line)
                count += 1
                need(
                    row == seal(row) and row["previous_record_digest"] == previous,
                    "broken trace chain",
                )
                previous = row["record_digest"]
                if name == "inputs":
                    from dataclasses import replace

                    from aos_native_spark_audit import audit_event

                    from pygrc.models.grc_9_v4_spark_contracts import (
                        GRC9V4SparkConfiguration,
                    )

                    source = row
                    config = GRC9V4SparkConfiguration.from_payload(
                        source["source_configuration"]
                    )
                    target = GRC9V4SparkConfiguration.from_payload(
                        source["target_configuration"]
                    )
                    state = exact_state(source["source_stage"]["after"])
                    need(
                        audit_event(
                            replace(config, current=state), target, source["event"]
                        )
                        == source["event_audit"],
                        "retained source/event lineage",
                    )
                    if numerical:
                        audit = verify(config, source["source_stage"])
                        need(
                            all(
                                v == source["source_error_in_target_chart"][k]
                                for k, v in audit.items()
                            ),
                            "source audit changed",
                        )
                if name == "diagnostics":
                    key = (row["role"], row["beat"])
                    need(
                        key not in diagnostic_keys
                        and compact(row["stage"]) == compact_samples[key],
                        "full diagnostic differs from primary compact trace",
                    )
                    diagnostic_keys.append(key)
                if name in EXPECTED:
                    if C is None:
                        C = source["initial_roles"][name]
                    data = expand(row["stage"], C)
                    need(
                        row["beat"] == count and data["before"] == C,
                        "disconnected native trajectory",
                    )
                    step = validate_staging(data)
                    compact_samples[(name, count)] = row["stage"]
                    C = data["after"]
                    need(sum(map(Q, C["C"])) == 21, "trace charge mismatch")
                    from aos_native_spark_oracle import round_even
                    from cos_native_spark_oracle import incidence, vector

                    need(
                        tuple(
                            str(round_even(x, 128))
                            for x in data["consumed_read"]["current_midpoint"]
                        )
                        == step.flux,
                        "retained nearest-even flux",
                    )
                    need(
                        vector(step.after.C)
                        == vector(step.before.C)
                        - 32
                        * incidence(step.before.graph.to_payload())
                        * vector(step.flux),
                        "retained exact incidence",
                    )
                    need(
                        tuple(
                            str(round_even(x, 192)) for x in data["writer"]["midpoint"]
                        )
                        == step.after.W_A,
                        "retained nearest-even W",
                    )
                    need(
                        classification_digest(step.after, target.policy)
                        == row["membership"]["classification_digest"]
                        == row["independent_history_and_error_audit"][
                            "weighted_classification_digest"
                        ],
                        "retained weighted classification",
                    )
                    cert = source["certificates"][0 if name == "current" else 1]
                    lower, upper = membership_bounds(exact_state(C), cert["operands"])
                    inside = upper <= 1
                    need(inside or lower > 1, "retained membership unresolved")
                    need(
                        row["membership"]["independent_lower"] == str(lower)
                        and row["membership"]["independent_upper"] == str(upper)
                        and row["membership"]["inside"] == inside,
                        "trace membership mismatch",
                    )
                    if inside:
                        entry = entry or count
                        window.append(count)
                    else:
                        window = []
                    gains += row["local_gain"]
                    need(
                        row["stage"]["physical_writes"] == 1
                        and len(row["stage"]["read_inputs"]) == 2
                        and row["stage"]["writer_calls"] == 1,
                        "trace staging mismatch",
                    )
                    need(
                        Q(row["independent_error_upper"])
                        <= Q(cert["proof"]["full_step_error"]),
                        "trace error exceeds admitted budget",
                    )
                    if numerical:
                        from pygrc.models.grc_9_v4_completion_certificate import (
                            CompletionCertificate,
                        )
                        from pygrc.models.grc_9_v4_spark_contracts import (
                            GRC9V4SparkConfiguration,
                        )

                        audit = verify(
                            GRC9V4SparkConfiguration.from_payload(
                                source["target_configuration"]
                            ),
                            data,
                            CompletionCertificate.from_payload(cert),
                            name,
                            compact=True,
                        )
                        need(
                            all(
                                audit[k]
                                == row["independent_history_and_error_audit"][k]
                                for k in audit
                                if k != "full_diagnostics_checked"
                            ),
                            "retained independent audit differs",
                        )
        need(
            count == ref["records"] and previous == ref["last_record_digest"],
            "truncated stream",
        )
        if name in EXPECTED:
            role = value["roles"][name]
            need(
                (entry, count) == EXPECTED[name]
                and role["entry"] == entry
                and role["completion"] == count
                and role["window"] == window
                and role["local_gain"] == gains,
                "endpoint summary differs",
            )
    need(
        set(diagnostic_keys)
        == {
            (r, b)
            for r, (entry, end) in EXPECTED.items()
            for b in (1, entry - 1, entry, entry + 1, end)
        },
        "selected complete diagnostics roster",
    )
    need(
        value["roles"]["current"]["local_gain"] == 1
        and value["roles"]["reset"]["local_gain"] == 0
        and value["physical_supporting_tail_steps"] == 0,
        "campaign scope mismatch",
    )
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--numerical", action="store_true")
    args = parser.parse_args()
    value = check(numerical=args.numerical)
    print(
        json.dumps(
            {
                "status": value["status"],
                "target_steps": sum(r["target_steps"] for r in value["roles"].values()),
                "compressed_bytes": sum(
                    r["compressed_bytes"] for r in value["streams"]
                ),
            }
        ),
        flush=True,
    )
