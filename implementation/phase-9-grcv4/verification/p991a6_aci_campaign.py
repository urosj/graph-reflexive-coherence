"""One public native A_CI campaign, measured guards and compressed exact evidence."""

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

import p991a6_aci_preflight as preflight
from cos_native_spark_oracle import matrix
from flint import ctx
from flint import fmpq as Q
from p991a4_native_spark_preflight import summary
from p991a5_native_spark_campaign import Stream, endpoint_controls
from p991a5_native_spark_verify import (
    need,
)
from p991a6_aci_campaign_verify import (
    Capture,
    classification_digest,
    classify_and_membership,
    compact,
    conductance_bits,
    expand,
    membership_bounds,
    validate_staging,
    verify,
)
from p991a6_aci_subjects import (
    certificate_pair,
    configuration,
    request,
)

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_spark_carrier import exact_state
from pygrc.models.grc_v4_spark_conductance import ACI_NUMERICAL_POLICY
from pygrc.models.grc_v4_state import FrozenJSONMap

BASE = "implementation/phase-9-grcv4/tranche-9/"
HERE = "implementation/phase-9-grcv4/verification/"
RECORD = BASE + "P9-9.1a.6-ACI.5-Campaign.json.xz"
FILES = {
    name: BASE + "P9-9.1a.6-ACI.5-" + name + ".jsonl.xz"
    for name in ("current", "reset", "checkpoints", "inputs", "diagnostics")
}
EXPECTED = {"current": (375, 377), "reset": (372, 374)}
PROFILE_WARNINGS = set()


def profile(ok, message):
    if not ok and message not in PROFILE_WARNINGS:
        PROFILE_WARNINGS.add(message)
        print(json.dumps({"profiling_warning": message, "continues": True}), flush=True)


from pygrc.models.grc_v4_spark_aci import SparkACIKernel


class PairedCold:
    """One isolated authority registry, shared by two genuinely cold journals."""

    def __init__(self):
        self.registry = {}
        self.models = []

    def __call__(self, checkpoint):
        calls = []
        original = SparkACIKernel.step

        def counted(k, *args, **kwargs):
            calls.append(1)
            return original(k, *args, **kwargs)

        expected = sum(
            a["kind"] == "step" for a in checkpoint["owner"]["publication"]["journal"]
        )
        start = time.perf_counter()
        with (
            patch.object(owner, "_SCOPES", self.registry),
            patch.object(SparkACIKernel, "step", counted),
        ):
            restored = GRC9V4.from_state(checkpoint)
            need(
                restored.snapshot()["owner"]["publication"]
                == checkpoint["owner"]["publication"],
                "paired cold replay changed publication",
            )
        need(
            len(calls) == expected,
            "paired cold replay must execute every ordinary journal step",
        )
        self.models.append(restored)
        return {
            "seconds": time.perf_counter() - start,
            "ordinary_journal_steps": expected,
            "replayed_steps": len(calls),
            "whole_publication_equal": True,
            "shared_accounting_reconciled": True,
            "scope": "isolated shared authority; current completion reconstructed before reset fork",
        }


def cold_restore(checkpoint):
    return PairedCold()(checkpoint)


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=sha256(canonical_json_bytes(body)).hexdigest())


def delivery(role, beat):
    return GRCV4StepRequestInput(
        "grcv4-step-request-input-v1", f"aci-{role}-{beat}", 32, FrozenJSONMap({})
    )


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
    certificates, _ = certificate_pair(current)
    need(
        current.install_completion_certificates(*certificates).committed,
        "certificates rejected",
    )
    target = current.configuration
    from aci_native_spark_audit import audit_event
    from p991a6_aci_campaign_verify import decoded

    event = current._operation._published.completion.event.to_dict()
    event_audit = audit_event(before_event, target, event)
    source_error = verify(config, source_stage)
    # Map both source resource error and retained log-W error into the target chart.
    # The event copies every old edge exactly and initializes new edges exactly.
    U = matrix(certificates[0].operands["U"])
    transfer = matrix(event["transfer"])
    step = decoded(source_stage)
    from flint import fmpq_mat

    ce = transfer * fmpq_mat([[Q(x)] for x in step.componentwise_error_bounds])
    old = set(before_event.reference.graph.live_edge_ids)
    le = [
        Q(step.log_conductance_component_error) if e in old else Q(0)
        for e in target.reference.graph.live_edge_ids
    ]
    errors = list(ce.entries()) + le
    source_bound = max(
        sum(abs(U[i, j]) * errors[j] for j in range(len(errors)))
        for i in range(U.nrows())
    )
    source_error["transported_full_C_logW_uniform_bound"] = str(source_bound)
    source_error["old_edge_logW_error_retained"] = True
    source_error["new_edge_conversion_error"] = "0"
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
            "event_audit": event_audit,
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
    for phase in (
        "incoming_read",
        "poststate_read",
        "conductance_writer",
        "after_numerics",
        "after_window",
        "before_publication",
    ):
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
        if phase in ("incoming_read", "poststate_read"):
            from pygrc.models.grc_v4_spark_aci import SparkACIKernel

            original_root = SparkACIKernel._admitted_read
            incoming = fork.configuration.current

            def fail_root(
                k, state, incoming=incoming, phase=phase, original_root=original_root
            ):
                # A stationary fixture can have equal-valued incoming and
                # returned states; their physical state objects remain distinct.
                if (state is incoming) == (phase == "incoming_read"):
                    raise ValueError("actual checkpoint injected " + phase)
                return original_root(k, state)

            with patch.object(SparkACIKernel, "_admitted_read", fail_root):
                result = fork.step_v4_input(req)
        elif phase == "conductance_writer":
            from pygrc.models.grc_v4_spark_aci import SparkACIKernel

            with patch.object(SparkACIKernel, "_writer", side_effect=fail):
                result = fork.step_v4_input(req)
        else:
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


def campaign():
    need(
        not any((ROOT / p).exists() for p in (RECORD, *FILES.values())),
        "campaign record already exists; do not overwrite a primary run",
    )
    from p991a6_aci_campaign_cost import RECORD as COST
    from p991a6_aci_campaign_cost import check as check_cost

    timing = check_cost(ROOT)
    need(
        timing["estimate"]["time_limit_policy"] == "profiling_only_user_authorized",
        "complete-path profiling required",
    )
    ctx.threads = 1
    started = time.perf_counter()
    deadline = started + timing["estimate"]["campaign_cap_seconds"]
    pressure, progress, boundaries, forks = [], {}, {r: {} for r in EXPECTED}, []
    paths = {
        COST,
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
                recent, costs, entry, window, gains, maximum_error = (
                    [],
                    [],
                    None,
                    [],
                    0,
                    Q(0),
                )
                fixed_reset = model.configuration.reset
                before_snapshot = None
                previous_full = None
                previous_restart = None
                previous_observation = classify_and_membership(
                    model.configuration.current, model.configuration.policy, cert
                )
                base_step_limit = (
                    2.0 * timing["roles"][role]["native_seconds"]["maximum"]
                )
                for beat in range(1, 401):
                    profile(
                        time.perf_counter() < deadline,
                        "campaign exceeds 30-minute profiling allowance",
                    )
                    req = delivery(role, beat)
                    # Snapshot the actual predecessor only near the domain; expected beats never select admission.
                    if Q(previous_observation["norm"]) <= 4:
                        before_snapshot = model.snapshot()
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
                    audit = verify(model.configuration, data, cert, role)
                    error = audit["full_step_error_upper"]
                    maximum_error = max(maximum_error, Q(error))
                    observation = classify_and_membership(
                        model.configuration.current, model.configuration.policy, cert
                    )
                    if observation["inside"]:
                        if entry is None:
                            entry = beat
                            need(
                                before_snapshot is not None,
                                "entry predecessor checkpoint unavailable",
                            )
                            boundaries[role]["before_entry"] = before_snapshot
                            streams["checkpoints"].write(
                                {
                                    "role": role,
                                    "beat": beat - 1,
                                    "label": "before_entry",
                                    "checkpoint": before_snapshot,
                                }
                            )
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
                            "stage": compact(data, previous_restart),
                            "independent_error_upper": error,
                            "independent_history_and_error_audit": audit,
                            "membership": observation,
                            "receipts": [
                                r.to_payload() for r in result.emitted_receipts
                            ],
                            "local_gain": result.local_gain,
                            "native_window_observations": len(cp.observations),
                            "ordinary_seconds": ordinary_seconds,
                        }
                    )
                    if beat == 1 or observation["inside"]:
                        streams["diagnostics"].write(
                            {"role": role, "beat": beat, "stage": data}
                        )
                    if (
                        observation["inside"]
                        and len(window) == 1
                        and previous_full is not None
                    ):
                        streams["diagnostics"].write(
                            {"role": role, "beat": beat - 1, "stage": previous_full}
                        )
                    previous_full = data
                    previous_restart = compact(data)["restart_read"]
                    label = {1: "entry", 2: "first_window", 3: "complete"}.get(
                        len(window)
                    )
                    if label:
                        checkpoint = model.snapshot()
                        streams["checkpoints"].write(
                            {
                                "role": role,
                                "beat": beat,
                                "label": label or "periodic",
                                "checkpoint": checkpoint,
                            }
                        )
                        if label:
                            boundaries[role][label] = checkpoint
                    previous_observation = observation
                    ordinary_audited_seconds = time.perf_counter() - t
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
                    recent.append(ordinary_seconds)
                    recent = recent[-8:]
                    costs.append(ordinary_audited_seconds)
                    profile(
                        len(recent) < 8 or statistics.mean(recent) <= base_step_limit,
                        "rolling native cost exceeds preflight; report updated estimate",
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
                        bits <= 2 * timing["roles"][role]["maximum_resource_bits"],
                        "resource bit growth exceeds preflight",
                    )
                    need(
                        conductance_bits(model.configuration.current)
                        <= 2 * timing["roles"][role]["maximum_conductance_bits"],
                        "conductance bit growth exceeds preflight",
                    )
                    remaining = (400 - beat) * max(
                        timing["roles"][role]["upper_seconds"] / 400,
                        1.5 * statistics.mean(costs[-8:]),
                    )
                    if role == "current":
                        remaining += timing["roles"]["reset"]["upper_seconds"]
                    profile(
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
                            "timing_seconds": summary(costs),
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
            cold = {}
            paired_cold = PairedCold()
            for role in EXPECTED:
                print(
                    json.dumps(
                        {
                            "cold_checkpoint": role,
                            "status": "starting",
                            "elapsed_seconds": time.perf_counter() - started,
                        }
                    ),
                    flush=True,
                )
                cold[role] = paired_cold(boundaries[role]["complete"])
                print(json.dumps({"cold_checkpoint": role, **cold[role]}), flush=True)
            profile(
                time.perf_counter() < deadline,
                "campaign exceeds 30-minute profiling allowance",
            )
    finally:
        for stream in streams.values():
            stream.close()
    value = seal(
        {
            "schema": "grc9v4-native-aci-campaign-v1",
            "leaf": "P9-9.1a.6-A_CI.5",
            "family": "A_CI",
            "status": "verified_pending_review",
            "entry_revision": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "native_endpoint_verified": True,
            "native_completion_support": False,
            "user_accepted": False,
            "full_trajectory_runs": 2,
            "stopped_attempts": [],
            "primary_current_trajectories": 1,
            "reset_comparison_trajectories": 1,
            "physical_supporting_tail_steps": 0,
            "evidence_format": "compact_state_root_and_rounding_witnesses_v2",
            "full_diagnostic_samples": 10,
            "target_vertices": 15,
            "target_edges": 16,
            "exact_charge": "21",
            "duration": "32",
            "numerical_policy_id": ACI_NUMERICAL_POLICY,
            "exact_backend": "flint",
            "oracle_precision_bits": 768,
            "native_precision_bits": 256,
            "flint_threads": ctx.threads,
            "target_graph_digest": target.reference.graph.graph_digest,
            "target_profile_id": target.reference.profile.complete_profile_id,
            "certificate_ids": [certs[r].certificate_id for r in EXPECTED],
            "roles": progress,
            "completion": current_observation,
            "pressure": pressure,
            "final_cost_record_digest": timing["record_digest"],
            "preflight_record_digest": timing["preflight_record_digest"],
            "elapsed_seconds": time.perf_counter() - started,
            "cap_seconds": 1800,
            "profiling_target_seconds": 1800,
            "time_limit_policy": "profiling_only_user_authorized",
            "profiling_target_exceeded": time.perf_counter() - started > 1800,
            "profiling_warnings": sorted(PROFILE_WARNINGS),
            "cold_checkpoint_validation": cold,
            "peak_rss_mib": preflight.rss(),
            "streams": [s.reference() for s in streams.values()],
            "source_bindings": source_bindings,
            "accounting_scope": "process_shared_publication_v1",
            "global_cross_process_uniqueness": False,
            "next_leaf": "P9-9.1a.6-A_PC.1",
        }
    )
    with lzma.open(ROOT / RECORD, "wb", preset=3) as output:
        output.write(canonical_json_bytes(value))
    return value


def check(root=ROOT, numerical=False):
    from p991a6_apc_epoch import previous_bytes

    root = Path(root)
    with lzma.open(root / RECORD, "rb") as stream:
        value = json.load(stream)
    need(
        value == seal(value) and value["schema"] == "grc9v4-native-aci-campaign-v1",
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
        previous_restart = None
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

                    from aci_native_spark_audit import audit_event

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
                        and compact(
                            row["stage"],
                            compact(row["stage"])["consumed_read"]
                            if compact_samples[key]["consumed_read"]
                            == {"previous_restart": True}
                            else None,
                        )
                        == compact_samples[key],
                        "full diagnostic differs from primary compact trace",
                    )
                    diagnostic_keys.append(key)
                if name in EXPECTED:
                    if C is None:
                        C = source["initial_roles"][name]
                    data = expand(row["stage"], C, previous_restart)
                    previous_restart = data["restart_read"]
                    need(
                        row["beat"] == count and data["before"] == C,
                        "disconnected native trajectory",
                    )
                    step = validate_staging(data)
                    compact_samples[(name, count)] = row["stage"]
                    C = data["after"]
                    need(sum(map(Q, C["C"])) == 21, "trace charge mismatch")
                    from aci_native_spark_oracle import round_even
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


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--smoke", action="store_true")
    parser.add_argument("--numerical", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        capture = Capture()
        with capture.installed():
            models, certs, _ = setup(capture)
            for role, model in models.items():
                need(model.step_v4_input(delivery(role, 1)).committed, "smoke step")
                print(
                    json.dumps(
                        {
                            "role": role,
                            "audit": verify(
                                model.configuration,
                                capture.payload(),
                                certs[role],
                                role,
                            ),
                        }
                    ),
                    flush=True,
                )
        return

    def stop(signum, frame):
        raise RuntimeError("campaign interrupted; compressed partial evidence retained")

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
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
