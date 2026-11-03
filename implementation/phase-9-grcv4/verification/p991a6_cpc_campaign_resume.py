"""Recover the timing-stopped PC comparison through public checkpoint replay.

The completed primary current trace is immutable. A reset checkpoint replays
its retained prefix exactly before new transitions are appended. Cold replay
and actual-window controls are recorded separately from primary trajectories.
"""

import argparse
import json
import lzma
import math
import statistics
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from flint import ctx
from flint import fmpq as Q
from p991a4_native_spark_preflight import summary
from p991a5_native_spark_campaign import endpoint_controls
from p991a5_native_spark_verify import need
from p991a6_cpc_campaign import (
    BASE,
    EXPECTED,
    FILES,
    RECORD,
    ROOT,
    Stream,
    delivery,
    fail_before_completion,
    seal,
)
from p991a6_cpc_campaign_verify import (
    Capture,
    carrier_bits,
    classify_and_membership,
    verify,
)
from p991a6_cpc_preflight import rss
from p991a6_cpc_resume_cost import RECORD as COST
from p991a6_cpc_resume_cost import STOP, rows, stopped
from p991a6_cpc_resume_cost import check as check_cost

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_spark_state import PC_NUMERICAL_POLICY
from pygrc.models.grc_v4_state import FrozenJSONMap

PROFILE_WARNINGS = set()


def profile(ok, message):
    """User-authorized profiling signals never waive numerical admission."""
    if not ok and message not in PROFILE_WARNINGS:
        PROFILE_WARNINGS.add(message)
        print(json.dumps({"profiling_warning": message, "continues": True}), flush=True)


def reference(path, data):
    raw = (ROOT / path).read_bytes()
    return {
        "path": path,
        "sha256": sha256(raw).hexdigest(),
        "compressed_bytes": len(raw),
        "records": len(data),
        "last_record_digest": data[-1]["record_digest"],
    }


def checked_copy(stream, data):
    previous = None
    for row in data:
        need(
            row == seal(row) and row["previous_record_digest"] == previous,
            "broken retained prefix",
        )
        stream.write(row)
        need(stream.last == row["record_digest"], "prefix rewrite changed content")
        previous = stream.last


def run():
    need(not (ROOT / RECORD).exists(), "do not overwrite completed campaign")
    timing = check_cost()
    stop = stopped()
    profile(timing["estimate"]["within_budget"], "recovery exceeds profiling target")
    start = time.perf_counter()
    deadline = start + 1800 - stop["elapsed_seconds_budget"]
    ctx.threads = 1
    inputs = rows(FILES["inputs"])[0]
    original = {
        r: rows(stop["streams"][r]["path"]) for r in ("current", "reset", "checkpoints")
    }
    certs = dict(
        zip(
            EXPECTED,
            (CompletionCertificate.from_payload(c) for c in inputs["certificates"]),
            strict=True,
        )
    )
    boundaries = {r: {} for r in EXPECTED}
    for row in original["checkpoints"]:
        if row["label"] != "periodic":
            boundaries[row["role"]][row["label"]] = row["checkpoint"]
    reset_checkpoint = original["checkpoints"][-1]
    need(
        reset_checkpoint["role"] == "reset" and reset_checkpoint["beat"] == 150,
        "recovery checkpoint selection",
    )
    pressure = []
    capture = Capture()
    replay = []
    cold = []
    with (
        tempfile.TemporaryDirectory(prefix="cpc-resumed-streams-") as tmp,
        capture.installed(),
    ):
        streams = {
            name: Stream(str(Path(tmp) / (name + ".jsonl.xz")))
            for name in ("reset", "checkpoints")
        }
        try:
            for name, stream in streams.items():
                checked_copy(stream, original[name])
            pending = boundaries["current"]["first_window"]
            need(
                pending["owner"]["origin"] not in owner._SCOPES,
                "recovery needs fresh process accounting",
            )
            t = time.perf_counter()
            current = GRC9V4.from_state(pending)
            cold.append(
                {
                    "role": "current",
                    "checkpoint_beat": 375,
                    "seconds": time.perf_counter() - t,
                    "ordinary_journal_steps": sum(
                        a["kind"] == "step"
                        for a in pending["owner"]["publication"]["journal"]
                    ),
                }
            )
            print(
                json.dumps(
                    {
                        "recovery": "current pending checkpoint validated",
                        "elapsed_seconds": time.perf_counter() - start,
                    }
                ),
                flush=True,
            )
            before, root = current.snapshot(), current._operation._spark_scope.published
            duplicate = current.step_v4_input(delivery("current", 375))
            zero = current.step_v4_input(
                GRCV4StepRequestInput(
                    "grcv4-step-request-input-v1",
                    "zero-at-real-window",
                    0,
                    FrozenJSONMap({}),
                )
            )
            current.compute_observables()
            need(
                not duplicate.committed
                and not zero.committed
                and current.snapshot() == before
                and current._operation._spark_scope.published is root,
                "recovered duplicate/zero/read changed window",
            )
            pressure.append(
                {
                    "fault": "duplicate_zero_read",
                    "target_beat": 375,
                    "whole_root_unchanged": True,
                }
            )
            forks = fail_before_completion(current, "current", 375, pressure)
            result = current.step_v4_input(delivery("current", 376))
            data = capture.payload()
            need(
                result.committed
                and result.local_gain == 1
                and canonical_json_bytes(data)
                == canonical_json_bytes(original["current"][-1]["stage"]),
                "primary endpoint replay differs",
            )
            need(
                verify(current.configuration, data, certs["current"])
                == original["current"][-1]["independent_history_and_error_audit"],
                "primary endpoint audit differs",
            )
            replay.append(
                {
                    "role": "current",
                    "beat": 376,
                    "stage_digest": sha256(canonical_json_bytes(data)).hexdigest(),
                    "matches_original": True,
                    "scope": "isolated checkpoint replay; not a second primary claim",
                }
            )
            t = time.perf_counter()
            reset = GRC9V4.from_state(reset_checkpoint["checkpoint"])
            cold.append(
                {
                    "role": "reset",
                    "checkpoint_beat": 150,
                    "seconds": time.perf_counter() - t,
                    "ordinary_journal_steps": sum(
                        a["kind"] == "step"
                        for a in reset_checkpoint["checkpoint"]["owner"]["publication"][
                            "journal"
                        ]
                    ),
                }
            )
            print(
                json.dumps(
                    {
                        "recovery": "reset checkpoint validated",
                        "elapsed_seconds": time.perf_counter() - start,
                    }
                ),
                flush=True,
            )
            for row in original["reset"][150:]:
                profile(
                    time.perf_counter() < deadline,
                    "recovery replay exceeds profiling target",
                )
                result = reset.step_v4_input(delivery("reset", row["beat"]))
                data = capture.payload()
                need(
                    result.committed
                    and result.local_gain == 0
                    and canonical_json_bytes(data)
                    == canonical_json_bytes(row["stage"]),
                    "reset prefix replay differs",
                )
                need(
                    verify(reset.configuration, data, certs["reset"], "reset")
                    == row["independent_history_and_error_audit"],
                    "reset replay audit differs",
                )
                replay.append(
                    {
                        "role": "reset",
                        "beat": row["beat"],
                        "stage_digest": sha256(canonical_json_bytes(data)).hexdigest(),
                        "matches_original": True,
                    }
                )
            print(
                json.dumps(
                    {
                        "recovery": "retained prefix matched",
                        "reset_beat": len(original["reset"]),
                        "elapsed_seconds": time.perf_counter() - start,
                    }
                ),
                flush=True,
            )
            cert = certs["reset"]
            fixed_reset = reset.configuration.reset
            window = []
            entry = None
            costs = []
            recent = []
            prior = classify_and_membership(
                reset.configuration.current, reset.configuration.policy, cert
            )
            max_error = max(
                Q(row["independent_error_upper"]) for row in original["reset"]
            )
            max_bits = max(
                carrier_bits(capture.step.before), carrier_bits(capture.step.after)
            )
            for beat in range(len(original["reset"]) + 1, 401):
                profile(
                    time.perf_counter() < deadline,
                    "combined active execution exceeds profiling target",
                )
                checkpoint = reset.snapshot() if Q(prior["norm"]) <= 4 else None
                t = time.perf_counter()
                result = reset.step_v4_input(delivery("reset", beat))
                cert.require_binding(
                    owner.kernel(reset.configuration),
                    reset.configuration.policy,
                    "reset",
                    reset.configuration.current.charge,
                )
                cert.membership(reset.configuration.current)
                owner.classify(reset.configuration.current, reset.configuration.policy)
                native = time.perf_counter() - t
                need(
                    result.committed
                    and result.local_gain == 0
                    and reset._operation._published.completion.event is None,
                    "reset continuation gained or failed",
                )
                need(reset.configuration.reset == fixed_reset, "reset baseline changed")
                data = capture.payload()
                audit = verify(reset.configuration, data, cert, "reset")
                error = audit["full_step_error_upper"]
                max_error = max(max_error, Q(error))
                observation = classify_and_membership(
                    reset.configuration.current, reset.configuration.policy, cert
                )
                if observation["inside"]:
                    if entry is None:
                        entry = beat
                        need(checkpoint is not None, "missing actual predecessor")
                        boundaries["reset"]["before_entry"] = checkpoint
                        streams["checkpoints"].write(
                            {
                                "role": "reset",
                                "beat": beat - 1,
                                "label": "before_entry",
                                "checkpoint": checkpoint,
                            }
                        )
                    window.append(beat)
                else:
                    window = []
                streams["reset"].write(
                    {
                        "beat": beat,
                        "step_index": reset.configuration.step_index,
                        "time": reset.configuration.time,
                        "stage": data,
                        "independent_error_upper": error,
                        "independent_history_and_error_audit": audit,
                        "membership": observation,
                        "receipts": [r.to_payload() for r in result.emitted_receipts],
                        "local_gain": result.local_gain,
                        "native_window_observations": 0,
                        "ordinary_seconds": native,
                    }
                )
                label = {1: "entry", 2: "first_window", 3: "complete"}.get(len(window))
                if beat % 50 == 0 or label:
                    saved = reset.snapshot()
                    streams["checkpoints"].write(
                        {
                            "role": "reset",
                            "beat": beat,
                            "label": label or "periodic",
                            "checkpoint": saved,
                        }
                    )
                    if label:
                        boundaries["reset"][label] = saved
                prior = observation
                costs.append(time.perf_counter() - t)
                recent = (recent + [native])[-8:]
                profile(
                    len(recent) < 8
                    or statistics.mean(recent)
                    <= timing["estimate"]["native_rolling_limit_seconds"],
                    "late native rolling limit exceeded",
                )
                need(
                    rss() < 1024
                    and carrier_bits(reset.configuration.current) <= 2 * max_bits,
                    "recovery memory/carrier bits",
                )
                need(
                    max(
                        max(
                            abs(Q(x).numerator).bit_length(),
                            Q(x).denominator.bit_length(),
                        )
                        for x in reset.configuration.current.C
                    )
                    <= 288,
                    "recovery resource bits",
                )
                remaining = (400 - beat) * max(
                    timing["estimate"]["per_beat_upper_seconds"],
                    1.5 * statistics.mean(costs[-8:]),
                ) + 120
                profile(
                    time.perf_counter() + remaining < deadline,
                    "recovery remaining projection exceeds combined budget",
                )
                if beat % 25 == 0 or observation["inside"]:
                    print(
                        json.dumps(
                            {
                                "role": "reset",
                                "beat": beat,
                                "norm": float(Q(observation["norm"])),
                                "inside": observation["inside"],
                                "local_gain": 0,
                                "combined_active_seconds": stop[
                                    "elapsed_seconds_budget"
                                ]
                                + time.perf_counter()
                                - start,
                            }
                        ),
                        flush=True,
                    )
                if len(window) == 3:
                    need((entry, beat) == EXPECTED["reset"], "reset endpoint shifted")
                    break
            else:
                raise ValueError("400 beats without reset entry/window")
            endpoint_controls(
                {"current": current, "reset": reset}, certs, boundaries, forks, pressure
            )
            need(capture.backends == {"flint"}, "recovery backend")
            profile(
                time.perf_counter() < deadline,
                "combined active execution exceeds profiling target",
            )
        finally:
            for stream in streams.values():
                stream.close()
        # Only successful recovery replaces the primary reset/checkpoint files;
        # exact stopped prefixes remain independently retained and pinned.
        for name, stream in streams.items():
            Path(stream.path).replace(ROOT / FILES[name])
    all_reset = rows(FILES["reset"])
    checkpoints = rows(FILES["checkpoints"])
    roles = {}
    for role, data_rows in [("current", original["current"]), ("reset", all_reset)]:
        inside = [r["beat"] for r in data_rows if r["membership"]["inside"]]
        roles[role] = {
            "entry": inside[0],
            "completion": data_rows[-1]["beat"],
            "target_steps": len(data_rows),
            "local_gain": sum(r["local_gain"] for r in data_rows),
            "window": inside[-3:],
            "duration": "32",
            "elapsed_window": "64",
            "maximum_step_error": str(
                max(Q(r["independent_error_upper"]) for r in data_rows)
            ),
            "final_membership": data_rows[-1]["membership"],
            "native_timing_seconds": summary(
                [r["ordinary_seconds"] for r in data_rows]
            ),
        }
    target = current.configuration
    refs = [
        reference(FILES[n], r)
        for n, r in [
            ("current", original["current"]),
            ("reset", all_reset),
            ("checkpoints", checkpoints),
            ("inputs", [inputs]),
        ]
    ]
    paths = {r["path"] for r in timing["source_bindings"]} | {
        COST,
        "implementation/phase-9-grcv4/verification/p991a6_cpc_resume_epoch.py",
        BASE + "P9-9.1a.6-CPC.5-ResumeSourceEpoch.json",
    }
    recovery = {
        "cold_checkpoint_validation": cold,
        "cold_ordinary_journal_steps": sum(r["ordinary_journal_steps"] for r in cold),
        "exact_prefix_replays": replay,
        "checkpoint_replay_target_steps": len(replay),
        "resumed_from_reset_beat": 150,
        "verified_prefix_before_continuation": 191,
        "first_new_reset_beat": 192,
        "completed_current_trace_unchanged": True,
        "scope": "same exact primary trajectories; cold public replay plus bounded controls; no physical supporting tail",
    }
    elapsed = time.perf_counter() - start
    value = seal(
        {
            "schema": "grc9v4-native-cpc-campaign-v1",
            "leaf": "P9-9.1a.6-C_PC.5",
            "family": "C_PC",
            "status": "verified_pending_review",
            "entry_revision": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "native_endpoint_verified": True,
            "native_completion_support": False,
            "user_accepted": False,
            "full_trajectory_runs": 2,
            "stopped_attempts": [
                {
                    "path": STOP,
                    "reason": stop["reason"],
                    "current_verified_steps": 376,
                    "reset_verified_steps": 191,
                }
            ],
            "primary_current_trajectories": 1,
            "reset_comparison_trajectories": 1,
            "physical_supporting_tail_steps": 0,
            "target_vertices": 15,
            "target_edges": 16,
            "exact_charge": "21",
            "duration": "32",
            "numerical_policy_id": PC_NUMERICAL_POLICY,
            "exact_backend": "flint",
            "oracle_precision_bits": 768,
            "native_precision_bits": 256,
            "flint_threads": 1,
            "target_graph_digest": target.reference.graph.graph_digest,
            "target_profile_id": target.reference.profile.complete_profile_id,
            "certificate_ids": [certs[r].certificate_id for r in EXPECTED],
            "roles": roles,
            "completion": current.compute_observables()["completion"],
            "pressure": pressure,
            "recovery": recovery,
            "final_cost_record_digest": timing["record_digest"],
            "preflight_record_digest": timing["preflight_record_digest"],
            "elapsed_seconds": stop["elapsed_seconds_budget"] + elapsed,
            "resume_elapsed_seconds": elapsed,
            "wall_seconds_including_investigation_pause": math.ceil(
                time.time() - stop["start_unix_seconds"]
            ),
            "elapsed_scope": "combined active campaign phases including cold replay and controls; investigation and bounded re-estimation pause reported separately",
            "profiling_target_seconds": 1800,
            "time_limit_policy": "profiling_only_user_authorized",
            "profiling_target_exceeded": stop["elapsed_seconds_budget"] + elapsed
            > 1800,
            "profiling_warnings": sorted(PROFILE_WARNINGS),
            "peak_rss_mib": max(rss(), 304.53125),
            "streams": refs,
            "source_bindings": [
                {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
                for p in sorted(paths)
            ],
            "accounting_scope": "process_shared_publication_v1",
            "global_cross_process_uniqueness": False,
            "next_leaf": "P9-9.1a.6-C_CI_PC.1",
        }
    )
    (ROOT / RECORD).write_bytes(lzma.compress(canonical_json_bytes(value), preset=3))
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", required=True)
    parser.parse_args()
    value = run()
    print(
        json.dumps(
            {
                k: value[k]
                for k in (
                    "status",
                    "elapsed_seconds",
                    "resume_elapsed_seconds",
                    "peak_rss_mib",
                )
            }
        ),
        flush=True,
    )
