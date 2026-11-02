"""One public native C_OS campaign, measured guards and compressed exact evidence."""

import argparse
import json
import lzma
import signal
import statistics
import subprocess
import sys
import time
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
for directory in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(directory))

import p991a4_native_spark_preflight as preflight
from cos_native_spark_oracle import incidence, infinity, matrix
from flint import ctx
from flint import fmpq as Q
from p991a5_native_spark_verify import (
    Capture,
    classify_and_membership,
    need,
    verify_step,
)

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_state import FrozenJSONMap
from tests.models.test_grc_9_v4_spark_completion import (
    certificate_pair,
    configuration,
    request,
)

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.5-Campaign.json"
FILES = {
    name: BASE + "P9-9.1a.5-" + name + ".jsonl.xz"
    for name in ("current", "reset", "checkpoints", "inputs")
}
EXPECTED = {"current": (374, 376), "reset": (375, 377)}


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=sha256(canonical_json_bytes(body)).hexdigest())


def delivery(role, beat):
    return GRCV4StepRequestInput(
        "grcv4-step-request-input-v1", f"cos-{role}-{beat}", 32, FrozenJSONMap({})
    )


class Stream:
    def __init__(self, path):
        self.path, self.last, self.count = path, None, 0
        self.file = lzma.open(ROOT / path, "wb", preset=3)  # noqa: SIM115 - closed by campaign's finally

    def write(self, value):
        value = seal(dict(value, previous_record_digest=self.last))
        self.file.write(canonical_json_bytes(value) + b"\n")
        self.last = value["record_digest"]
        self.count += 1

    def close(self):
        self.file.close()

    def reference(self):
        raw = (ROOT / self.path).read_bytes()
        return {
            "path": self.path,
            "sha256": sha256(raw).hexdigest(),
            "compressed_bytes": len(raw),
            "records": self.count,
            "last_record_digest": self.last,
        }


def verify_event(config, before, model):
    from cos_native_spark_oracle import classify as independent_classify
    from p991a2_native_spark_numerics import subjects

    _, _, _, domain = subjects()
    event = model._operation._published.completion.event
    expected_source = independent_classify(
        before.reference.graph.to_payload(),
        before.current.C,
        before.policy.to_payload(),
    )
    actual_source = owner.classify(before.current, before.policy)
    need(
        (
            actual_source.basins,
            actual_source.terminals,
            [r.to_dict() for r in actual_source.rows],
        )
        == expected_source,
        "source classifier differs from independent complete routes",
    )
    need("v" in dict(expected_source[0])["p"], "source lacks declared geometric parent")
    trigger = next(r for r in expected_source[2] if r["node_id"] == "v")
    need(
        Q(trigger["gradient_squared"]) < 16
        and Q(trigger["minimum_signed_gradient"]) < Q(1, 8),
        "fresh source trigger failed",
    )
    literal = json.loads(
        json.dumps(domain["graphs"]["1"]).replace(
            "sc2-positive-module", event["event_id"]
        )
    )
    literal["live_node_ids"].sort()
    literal["edges"].sort(key=lambda e: e["edge_id"])
    need(
        model.configuration.reference.graph.to_payload() == literal,
        "literal event topology mismatch",
    )
    module = list(event["module"])
    for role in ("current", "reset"):
        source = getattr(before, role)
        values = dict(zip(source.graph.live_node_ids, map(Q, source.C), strict=True))
        cv = values.pop("v")
        values.update(zip(module, (Q(0), cv / 64, cv * 31 / 32, cv / 64), strict=True))
        after = getattr(model.configuration, role)
        need(
            dict(zip(after.graph.live_node_ids, map(Q, after.C), strict=True))
            == values,
            role + " transfer mismatch",
        )
        need(sum(map(Q, after.C)) == 21, "event charge changed")
    need(before.reset == config.reset, "reset was source-advanced")


def setup(capture):
    config = configuration()
    current = GRC9V4(config)
    result = current.step_v4_input(delivery("source", 1))
    need(result.committed and not result.local_gain, "source step failed")
    source_stage = capture.payload()
    before_event = current.configuration
    event_result = current.expand(request(current))
    need(
        event_result.committed and event_result.local_gain == 0,
        "event failed or earned immediate gain",
    )
    verify_event(config, before_event, current)
    certificates, _ = certificate_pair(current)
    need(
        current.install_completion_certificates(*certificates).committed,
        "certificates rejected",
    )
    target = current.configuration
    U = matrix(certificates[0].operands["U"])
    transfer = matrix(current._operation._published.completion.event["transfer"])
    source_bound = (
        32
        * infinity(U * transfer * incidence(config.reference.graph.to_payload()))
        / Q(2**129)
    )
    source_error = verify_step(
        config.reference.graph.to_payload(),
        source_stage,
        U * transfer,
        str(source_bound),
    )
    reset = current.duplicate()
    need(
        reset.reset().committed
        and reset._operation._published.completion.event is None,
        "reset failed to invalidate live event",
    )
    return (
        {"current": current, "reset": reset},
        dict(zip(EXPECTED, certificates, strict=True)),
        {
            "source_configuration": config.to_payload(),
            "source_stage": source_stage,
            "source_error_in_target_chart": source_error,
            "source_uniform_bound_in_target_chart": str(source_bound),
            "event": current._operation._published.completion.event.to_dict(),
            "target_configuration": target.to_payload(),
            "certificates": [c.to_payload() for c in certificates],
            "initial_roles": {
                r: m.configuration.current.to_payload()
                for r, m in {"current": current, "reset": reset}.items()
            },
            "initial_conversion_error": "0",
            "reset_event_error": "0",
            "trajectory_relation": "each actual native transition independently certified; no global outside-domain ideal-orbit shadow bound claimed",
        },
    )


def fail_before_completion(model, role, beat, pressure):
    """Faults in a real pending fork; primary successful trajectory is untouched."""
    forks = []
    for phase in ("after_numerics", "after_window", "before_publication"):
        fork = model.duplicate()
        root, before = fork._operation._spark_scope.published, fork.snapshot()
        original = owner.progress

        def fail(*args, phase=phase, original=original):
            if phase == "after_window":
                original(*args)
            raise ValueError("actual checkpoint injected " + phase)

        target, attribute = (
            (type(fork._operation), "_publish")
            if phase == "before_publication"
            else (owner, "progress")
        )
        req = delivery("fault-" + phase, beat + 1)
        with patch.object(target, attribute, side_effect=fail):
            result = fork.step_v4_input(req)
        need(
            not result.committed
            and fork._operation._spark_scope.published is root
            and fork.snapshot() == before,
            "partial publication leaked at " + phase,
        )
        pressure.append(
            {
                "fault": phase,
                "role": role,
                "target_beat": beat,
                "rejected": True,
                "whole_root_unchanged": True,
            }
        )
        forks.append((fork, req))
    return forks


def endpoint_controls(models, certs, boundaries, forks, pressure):
    primary = models["current"]
    expected = primary.configuration.current
    for fork, req in forks:
        result = fork.step_v4_input(req)
        need(
            result.committed
            and result.local_gain == 0
            and fork.configuration.current == expected,
            "failed fork retry recredited or changed physical endpoint",
        )
    pressure.append(
        {
            "fault": "failed_fork_retry_after_primary_claim",
            "committed": len(forks),
            "additional_gain": 0,
        }
    )
    restored = {}
    for label, checkpoint in boundaries["current"].items():
        model = GRC9V4.from_state(checkpoint)
        need(
            model.snapshot()["owner"]["publication"]
            == checkpoint["owner"]["publication"],
            "checkpoint publication changed",
        )
        need(
            len(model.compute_observables()["completion"]["consumed_occurrences"]) == 1,
            "restore lost occurrence",
        )
        restored[label] = model
    before = restored["before_entry"]
    twin = before.duplicate()
    original = before.snapshot()
    for _ in range(4):
        before.compute_observables()
    need(before.snapshot() == original, "observation advanced state")
    a, b = before.step(), twin.step()
    need(
        a.committed
        and b.committed
        and a.local_gain == b.local_gain == 0
        and before.configuration == twin.configuration,
        "observer noninterference or shared consumption failed",
    )
    completed = restored["complete"]
    root, snapshot = completed._operation._spark_scope.published, completed.snapshot()
    bad = completed.install_completion_certificates(certs["reset"], certs["current"])
    need(
        not bad.committed
        and completed._operation._spark_scope.published is root
        and completed.snapshot() == snapshot,
        "wrong role certificate changed completed publication",
    )
    result = completed.install_completion_certificates(certs["current"], certs["reset"])
    need(result.committed and result.local_gain == 0, "replacement earned gain")
    result = completed.reset()
    need(
        result.committed
        and not result.local_gain
        and completed._operation._published.completion.event is None,
        "postcompletion reset retained live event",
    )
    need(
        len(completed.compute_observables()["completion"]["children"]) == 1,
        "postcompletion operation lost child",
    )
    pressure.extend(
        [
            {
                "fault": "four_actual_window_checkpoints",
                "restored": True,
                "additional_gain": 0,
            },
            {
                "fault": "observer_noninterference",
                "same_physical_state": True,
                "additional_gain": 0,
            },
            {"fault": "wrong_role_replacement_reset", "rejected_or_zero_gain": True},
        ]
    )


def campaign():
    need(
        not (ROOT / RECORD).exists(),
        "campaign record already exists; do not overwrite a primary run",
    )
    timing = preflight.check(ROOT)
    need(timing["estimate"]["within_budget"], "preflight exceeds budget")
    ctx.threads = 1
    started = time.perf_counter()
    deadline = started + timing["estimate"]["campaign_cap_seconds"]
    pressure, progress, boundaries, forks = [], {}, {r: {} for r in EXPECTED}, []
    paths = {
        HERE + "p991a5_native_spark_campaign.py",
        HERE + "p991a5_native_spark_verify.py",
        preflight.RECORD,
        *(r["path"] for r in timing["source_bindings"]),
    }
    source_bindings = [
        {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
        for p in sorted(paths)
    ]
    streams = {name: Stream(path) for name, path in FILES.items()}
    capture = Capture()
    try:
        with capture.installed():
            models, certs, inputs = setup(capture)
            target = models["current"].configuration
            need(
                target.reference.graph.graph_digest == timing["target_graph_digest"]
                and target.reference.profile.complete_profile_id
                == timing["target_profile_id"]
                and [certs[r].certificate_id for r in EXPECTED]
                == timing["certificate_ids"],
                "preflight subject changed",
            )
            streams["inputs"].write(inputs)
            for role, model in models.items():
                cert = certs[role]
                U = matrix(cert.operands["U"])
                graph = model.configuration.reference.graph.to_payload()
                recent, costs, entry, window, gains, maximum_error = (
                    [],
                    [],
                    None,
                    [],
                    0,
                    Q(0),
                )
                fixed_reset = model.configuration.reset
                expected_entry, expected_end = EXPECTED[role]
                labels = {
                    expected_entry - 1: "before_entry",
                    expected_entry: "entry",
                    expected_entry + 1: "first_window",
                    expected_end: "complete",
                }
                base_step_limit = (
                    1.5 * timing["estimate"]["roles"][role]["step_seconds"]["maximum"]
                )
                for beat in range(1, 401):
                    need(time.perf_counter() < deadline, "campaign wall cap reached")
                    req = delivery(role, beat)
                    t = time.perf_counter()
                    result = model.step_v4_input(req)
                    need(result.committed, result.reason)
                    if role == "reset":
                        cert.require_binding(
                            owner.kernel(model.configuration),
                            model.configuration.policy,
                            "reset",
                            model.configuration.current.charge,
                        )
                        cert.membership(model.configuration.current)
                        owner.classify(
                            model.configuration.current, model.configuration.policy
                        )
                    ordinary_seconds = time.perf_counter() - t
                    data = capture.payload()
                    need(
                        model.configuration.reset == fixed_reset,
                        "ordinary step changed reset baseline",
                    )
                    error = verify_step(graph, data, U, cert.proof["full_step_error"])
                    maximum_error = max(maximum_error, Q(error))
                    observation = classify_and_membership(
                        model.configuration.current, model.configuration.policy, cert
                    )
                    if observation["inside"]:
                        if entry is None:
                            entry = beat
                        window.append(beat)
                    else:
                        window = []
                    cp = model._operation._published.completion
                    if role == "current":
                        need(
                            len(cp.observations) == len(window),
                            "native window disagrees with actual membership",
                        )
                    else:
                        need(
                            cp.event is None and not result.local_gain,
                            "reset comparison earned live gain",
                        )
                    gains += result.local_gain
                    streams[role].write(
                        {
                            "beat": beat,
                            "step_index": model.configuration.step_index,
                            "time": model.configuration.time,
                            "stage": data,
                            "independent_error_upper": error,
                            "membership": observation,
                            "receipts": [
                                r.to_payload() for r in result.emitted_receipts
                            ],
                            "local_gain": result.local_gain,
                            "native_window_observations": len(cp.observations),
                            "ordinary_seconds": ordinary_seconds,
                        }
                    )
                    if beat % 50 == 0 or beat in labels:
                        checkpoint = model.snapshot()
                        streams["checkpoints"].write(
                            {
                                "role": role,
                                "beat": beat,
                                "label": labels.get(beat, "periodic"),
                                "checkpoint": checkpoint,
                            }
                        )
                        if beat in labels:
                            boundaries[role][labels[beat]] = checkpoint
                    if role == "current" and len(window) == 2:
                        before, root = (
                            model.snapshot(),
                            model._operation._spark_scope.published,
                        )
                        duplicate = model.step_v4_input(req)
                        zero = model.step_v4_input(
                            GRCV4StepRequestInput(
                                "grcv4-step-request-input-v1",
                                "zero-at-real-window",
                                0,
                                FrozenJSONMap({}),
                            )
                        )
                        model.compute_observables()
                        need(
                            not duplicate.committed
                            and not zero.committed
                            and model.snapshot() == before
                            and model._operation._spark_scope.published is root,
                            "duplicate/zero/read advanced actual window",
                        )
                        pressure.append(
                            {
                                "fault": "duplicate_zero_read",
                                "target_beat": beat,
                                "whole_root_unchanged": True,
                            }
                        )
                        forks = fail_before_completion(model, role, beat, pressure)
                    elapsed = time.perf_counter() - t
                    recent.append(ordinary_seconds)
                    recent = recent[-8:]
                    costs.append(elapsed)
                    need(
                        len(recent) < 8 or statistics.mean(recent) <= base_step_limit,
                        "rolling native cost exceeds preflight: stop/re-estimate",
                    )
                    need(
                        preflight.rss() <= 1024, "memory cap reached: stop/re-estimate"
                    )
                    bits = max(
                        max(
                            abs(Q(x).numerator).bit_length(),
                            Q(x).denominator.bit_length(),
                        )
                        for x in model.configuration.current.C
                    )
                    need(
                        bits
                        <= 2 * max(r["resource_bits"] for r in timing["samples"][role]),
                        "resource bit growth exceeds preflight",
                    )
                    remaining = (400 - beat) * max(
                        timing["estimate"]["roles"][role]["upper_seconds"] / 400,
                        1.5 * statistics.mean(costs[-8:]),
                    )
                    if role == "current":
                        remaining += timing["estimate"]["roles"]["reset"][
                            "upper_seconds"
                        ]
                    need(
                        time.perf_counter() + remaining + 60 < deadline,
                        "remaining upper projection exceeds campaign budget",
                    )
                    if beat == 1 or beat % 25 == 0 or observation["inside"]:
                        print(
                            json.dumps(
                                {
                                    "role": role,
                                    "beat": beat,
                                    "norm": float(Q(observation["norm"])),
                                    "inside": observation["inside"],
                                    "local_gain": result.local_gain,
                                    "elapsed_seconds": time.perf_counter() - started,
                                    "rolling_step_seconds": statistics.mean(recent),
                                    "peak_rss_mib": preflight.rss(),
                                }
                            ),
                            flush=True,
                        )
                    if (
                        role == "current"
                        and result.local_gain
                        or role == "reset"
                        and len(window) == 3
                    ):
                        need(
                            (entry, beat) == EXPECTED[role],
                            "native endpoint shifted: investigate, do not force expectation",
                        )
                        progress[role] = {
                            "entry": entry,
                            "completion": beat,
                            "target_steps": beat,
                            "local_gain": gains,
                            "window": window,
                            "duration": "32",
                            "elapsed_window": "64",
                            "maximum_step_error": str(maximum_error),
                            "final_membership": observation,
                            "timing_seconds": preflight.summary(costs),
                        }
                        break
                else:
                    raise ValueError(
                        "400 target beats without completion; no tail authorized"
                    )
            current_observation = models["current"].compute_observables()["completion"]
            need(
                progress["current"]["local_gain"] == 1
                and progress["reset"]["local_gain"] == 0
                and len(current_observation["children"])
                == len(current_observation["consumed_occurrences"])
                == 1,
                "once-only child registration failed",
            )
            endpoint_controls(models, certs, boundaries, forks, pressure)
            need(capture.backends == {"flint"}, "native reads left FLINT")
            need(time.perf_counter() < deadline, "campaign exceeded wall cap")
    finally:
        for stream in streams.values():
            stream.close()
    value = seal(
        {
            "schema": "grc9v4-native-cos-campaign-v1",
            "leaf": "P9-9.1a.5",
            "status": "verified_pending_review",
            "entry_revision": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "native_endpoint_verified": True,
            "native_completion_support": False,
            "user_accepted": False,
            "full_trajectory_runs": 2,
            "primary_current_trajectories": 1,
            "reset_comparison_trajectories": 1,
            "physical_supporting_tail_steps": 0,
            "target_vertices": 15,
            "target_edges": 16,
            "exact_charge": "21",
            "duration": "32",
            "numerical_policy_id": preflight.NUMERICAL_POLICY,
            "exact_backend": "flint",
            "oracle_precision_bits": 512,
            "flint_threads": ctx.threads,
            "target_graph_digest": target.reference.graph.graph_digest,
            "target_profile_id": target.reference.profile.complete_profile_id,
            "certificate_ids": [certs[r].certificate_id for r in EXPECTED],
            "roles": progress,
            "completion": current_observation,
            "pressure": pressure,
            "preflight_record_digest": timing["record_digest"],
            "elapsed_seconds": time.perf_counter() - started,
            "cap_seconds": 1800,
            "peak_rss_mib": preflight.rss(),
            "streams": [s.reference() for s in streams.values()],
            "source_bindings": source_bindings,
            "accounting_scope": "process_shared_publication_v1",
            "global_cross_process_uniqueness": False,
            "next_leaf": "P9-9.1a.6-C_CI",
        }
    )
    (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")
    return value


def check(root=ROOT, numerical=False):
    from p991a6_cci_epoch import previous_bytes
    root = Path(root)
    value = json.loads((root / RECORD).read_bytes())
    need(
        value == seal(value) and value["schema"] == "grc9v4-native-cos-campaign-v1",
        "unsealed campaign",
    )
    for ref in [*value["source_bindings"], *value["streams"]]:
        need(
            sha256(previous_bytes(root, ref["path"]) if ref in value["source_bindings"] else (root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
            "changed campaign source/evidence: " + ref["path"],
        )
    source = None
    for ref in sorted(
        value["streams"], key=lambda x: 0 if x["path"] == FILES["inputs"] else 1
    ):
        count, previous, C = 0, None, None
        with lzma.open(root / ref["path"], "rt") as stream:
            for line in stream:
                row = json.loads(line)
                count += 1
                need(
                    row == seal(row) and row["previous_record_digest"] == previous,
                    "broken exact trace chain",
                )
                previous = row["record_digest"]
                if ref["path"] == FILES["inputs"]:
                    source = row
                if ref["path"] in (FILES["current"], FILES["reset"]):
                    role = "current" if ref["path"] == FILES["current"] else "reset"
                    if C is None:
                        C = source["initial_roles"][role]["C"]
                    need(
                        row["beat"] == count and row["stage"]["before"] == C,
                        "trajectory transition disconnected",
                    )
                    C = row["stage"]["after"]
                    need(sum(map(Q, C)) == 21, "trace charge mismatch")
                    if numerical:
                        cert = source["certificates"][0 if role == "current" else 1]
                        error = verify_step(
                            source["target_configuration"]["reference"]["graph"],
                            row["stage"],
                            matrix(cert["operands"]["U"]),
                            cert["proof"]["full_step_error"],
                        )
                        need(
                            error == row["independent_error_upper"],
                            "retained oracle result differs",
                        )
        need(
            count == ref["records"] and previous == ref["last_record_digest"],
            "truncated trace",
        )
    need(
        value["roles"]["current"]["local_gain"] == 1
        and value["roles"]["reset"]["local_gain"] == 0,
        "role gain mismatch",
    )
    return value


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--smoke", action="store_true")
    parser.add_argument("--numerical", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        cap = Capture()
        with cap.installed():
            models, certs, _ = setup(cap)
            for role, model in models.items():
                need(
                    model.step_v4_input(delivery(role, 1)).committed,
                    "smoke step failed",
                )
                error = verify_step(
                    model.configuration.reference.graph.to_payload(),
                    cap.payload(),
                    matrix(certs[role].operands["U"]),
                    certs[role].proof["full_step_error"],
                )
                classify_and_membership(
                    model.configuration.current, model.configuration.policy, certs[role]
                )
                print(json.dumps({"smoke_role": role, "error_upper": error}))
        return

    def stop(signum, frame):
        raise RuntimeError("campaign interrupted; partial compressed evidence retained")

    signal.signal(signal.SIGTERM, stop)
    value = campaign() if args.run else check(numerical=args.numerical)
    print(
        json.dumps(
            {
                k: value[k]
                for k in (
                    "status",
                    "native_endpoint_verified",
                    "elapsed_seconds",
                    "peak_rss_mib",
                    "next_leaf",
                )
            }
        )
    )


if __name__ == "__main__":
    main()
