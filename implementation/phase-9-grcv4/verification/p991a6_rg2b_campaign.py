"""Explicit, process-isolated RG2b source-to-completion campaigns.

All finite-chain proofs run during execution. Compact rows retain exact physical
states, outputs, proof summaries and complete diagnostic hashes. Reconstructing
an omitted chain is an explicit native calculation, never an integrity check.
"""

import argparse
import importlib
import json
import lzma
import statistics
import subprocess
import sys
import time
from contextlib import ExitStack, contextmanager
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from flint import ctx, fmpq as Q, fmpq_mat as M
from p991a4_native_spark_preflight import rss
from p991a5_native_spark_campaign import Stream, endpoint_controls, seal
from p991a5_native_spark_verify import need

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_state import FrozenJSONMap

HERE = "implementation/phase-9-grcv4/verification/"
BASE = "implementation/phase-9-grcv4/tranche-9/"
SELF = HERE + "p991a6_rg2b_campaign.py"
FAMILIES = {
    "C_RG2b": ("crg2b", "CRG2b", 8, (390, 392)),
    "A_RG2b": ("arg2b", "ARG2b", 16, (300, 302)),
}


def digest(value):
    return sha256(canonical_json_bytes(value)).hexdigest()


class Adapter:
    def __init__(self, family):
        self.family = family
        self.name, self.tag, self.duration, self.expected = FAMILIES[family]
        self.native = importlib.import_module("pygrc.models.grc_v4_spark_" + self.name)
        self.kernel = getattr(self.native, "Spark" + self.tag + "Kernel")
        self.subjects = importlib.import_module("p991a6_" + self.name + "_subjects")
        self.preflight = importlib.import_module("p991a6_" + self.name + "_preflight")
        self.oracle = importlib.import_module(self.name + "_native_spark_oracle")
        self.domain = importlib.import_module(
            "pygrc.models.grc_9_v4_completion_" + self.name
        )
        self.prefix = BASE + "P9-9.1a.6-" + self.tag + ".5-"

    def path(self, suffix):
        return self.prefix + suffix

    def delivery(self, role, beat):
        return GRCV4StepRequestInput(
            "grcv4-step-request-input-v1",
            f"{self.name}-{role}-{beat}",
            self.duration,
            FrozenJSONMap({}),
        )

    def audit(self, config, step, *, deep=False):
        need(
            step.profile_id == config.reference.profile.complete_profile_id
            and step.before.graph == config.reference.graph,
            "external public subject",
        )
        if self.family == "C_RG2b":
            report = self.oracle.verify_step(step, fresh=deep, diagnostic_overlap=True)
            # The original finite-chain checker proves the represented error;
            # also verify the exact selected nearest-even flux explicitly.
            with _ARB_CONTEXT_LOCK, ctx.workprec(768):
                from pygrc.models.grc_v4_spark_state import round_flux

                read = self.oracle.proof_read(
                    config.reference.graph.to_payload(),
                    config.reference.profile.to_payload(),
                    step.before,
                    step.section,
                )
                J = self.oracle.decoded(read["J"])
                need(
                    all(
                        round_flux(x.lower().fmpq())
                        == round_flux(x.upper().fmpq())
                        == Q(v)
                        for x, v in zip(J.entries(), step.flux, strict=True)
                    ),
                    "independent unique flux rounding",
                )
            report["unique_flux_rounding"] = True
        else:
            report = self.oracle.verify_step(
                config, step.before, step, fresh_check=deep
            )
        return report


class Capture:
    def __init__(self, adapter):
        self.a, self.step, self.reads, self.backends = adapter, None, [], set()

    @contextmanager
    def installed(self):
        original = self.a.kernel.step
        original_read = self.a.kernel._admitted_section

        def read(k, state):
            from pygrc.models.grc_v4_exact import current_exact_backend

            self.backends.add(current_exact_backend().value)
            self.reads.append(state.to_payload())
            return original_read(k, state)

        def step(k, *args, **kwargs):
            self.reads = []
            result = original(k, *args, **kwargs)
            need(
                self.reads == [result.before.to_payload(), result.after.to_payload()],
                "incoming and returned full-state section admission",
            )
            self.step = result
            return result

        with (
            patch.object(self.a.kernel, "step", step),
            patch.object(self.a.kernel, "_admitted_section", read),
        ):
            yield self


def classification(state, policy):
    if hasattr(state, "W_A"):
        from aos_native_spark_oracle import classify

        expected = classify(
            state.graph.to_payload(), state.C, state.W_A, policy.to_payload()
        )
    else:
        from cos_native_spark_oracle import classify

        expected = classify(state.graph.to_payload(), state.C, policy.to_payload())
    actual = owner.classify(state, policy)
    need(
        (actual.basins, actual.terminals, [r.to_dict() for r in actual.rows])
        == expected,
        "independent exhaustive classification",
    )
    return digest(expected)


def observation(a, state, policy, certificate):
    certificate.require_binding(
        a.kernel(state.graph, a.subjects.profile(state.graph)),
        policy,
        certificate.operands["binding"]["role"],
        state.charge,
    )
    actual = a.domain.membership_details(certificate, state)
    graph = state.graph.to_payload()
    s, radius = Q(actual["parameter"]), Q(certificate.operands["radius"])
    need(0 <= s <= 1, "curve parameter")
    if a.family == "A_RG2b":
        from arg2b_native_spark_pressure_oracle import joint_distances, state_X

        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            c, y = joint_distances(
                graph, certificate.operands["curve"], state_X(state), s
            )
            lo = max(c.lower().fmpq(), y.lower().fmpq()) / radius**2
            hi = max(c.upper().fmpq(), y.upper().fmpq()) / radius**2
        need(hi <= Q(actual["squared_norm"]), "independent joint metric upper bound")
    else:
        B = M(
            [
                [
                    int(e["tail"]["node_id"] == n) - int(e["head"]["node_id"] == n)
                    for e in graph["edges"]
                ]
                for n in graph["live_node_ids"]
            ]
        )
        n, m = B.nrows(), B.ncols()
        I = M([[int(i == j) for j in range(m)] for i in range(m)])
        A = B * (I + (3 * I / 4 + B.transpose() * B).inv() / 4) * B.transpose()
        P = (A + M([[Q(1, n)] * n for _ in range(n)])).inv()
        t = [Q(1), 2 * s - 1]
        rows = certificate.operands["curve"]
        for _ in range(2, len(rows[0])):
            t.append(2 * t[1] * t[-1] - t[-2])
        point = [sum(Q(c) * v for c, v in zip(row, t, strict=True)) for row in rows]
        delta = M([[Q(c) - p] for c, p in zip(state.C, point, strict=True)])
        lo = hi = (delta.transpose() * P * delta)[0, 0] / radius**2
        need(str(hi) == actual["squared_norm"], "independent exact curved metric")
    need(
        (actual["inside"] and hi <= 1) or (not actual["inside"] and lo > 1),
        "selected-parameter membership disagreement",
    )
    return dict(
        actual,
        independent_lower=str(lo),
        independent_upper=str(hi),
        classification_digest=classification(state, policy),
        exclusion_scope="outside at selected parameter; not global exclusion",
    )


def audit_event(a, original, source, target, event):
    classification(source.current, source.policy)
    need(
        source.reset == original.reset
        and event["source"] == source.current.to_payload(),
        "fresh source and independent unadvanced reset",
    )
    from p991a2_native_spark_numerics import subjects

    _, _, _, domain = subjects()
    expected = json.loads(
        json.dumps(domain["graphs"]["1"]).replace(
            "sc2-positive-module", event["event_id"]
        )
    )
    expected["live_node_ids"].sort()
    expected["edges"].sort(key=lambda e: e["edge_id"])
    need(target.reference.graph.to_payload() == expected, "literal D11 target topology")
    rows = owner.classify(source.current, source.policy)
    need("v" in dict(rows.basins)["p"], "qualified source parent")
    trigger = next(r for r in rows.rows if r["node_id"] == "v")
    need(
        Q(trigger["gradient_squared"]) < 16
        and Q(trigger["minimum_signed_gradient"]) < Q(1, 8),
        "fresh event trigger",
    )
    for role in ("current", "reset"):
        before, after = getattr(source, role), getattr(target, role)
        values = dict(zip(before.graph.live_node_ids, map(Q, before.C), strict=True))
        v = values.pop("v")
        values.update(
            zip(
                event["module"],
                (Q(0), v * Q(5, 2048), v * Q(1021, 1024), v * Q(1, 2048)),
                strict=True,
            )
        )
        need(
            values == dict(zip(after.graph.live_node_ids, map(Q, after.C), strict=True))
            and sum(map(Q, after.C)) == 21,
            "exact both-role resource allocation",
        )
        if a.family == "A_RG2b":
            old = dict(zip(before.graph.live_edge_ids, before.W_A, strict=True))
            need(
                after.W_A == tuple(old.get(e, "1") for e in after.graph.live_edge_ids),
                "old-edge W retention and new-edge seed",
            )
    return {
        "both_role_exact_transfer": True,
        "qualified_parent": True,
        "literal_D11_topology": True,
        "fresh_source_capture": True,
        "history": "exact_old_W_new_seed_one" if a.family == "A_RG2b" else "C_only",
    }


def setup(a, cap, *, deep=True):
    config = a.subjects.configuration()
    model = GRC9V4(config)
    r = model.step_v4_input(a.delivery("source", 1))
    need(r.committed and not r.local_gain, "source beat")
    source_step = cap.step
    source_audit = a.audit(config, source_step, deep=deep)
    source = model.configuration
    result = model.expand(a.subjects.request(model))
    need(
        result.committed and not result.local_gain,
        "lawful expansion without completion credit",
    )
    event = model._operation._published.completion.event.to_dict()
    event_audit = audit_event(a, config, source, model.configuration, event)
    pair, center = a.subjects.certificate_pair(model)
    need(
        model.install_completion_certificates(*pair).committed,
        "install both role certificates",
    )
    reset = model.duplicate()
    need(
        reset.reset().committed
        and reset._operation._published.completion.event is None,
        "public reset clears live event",
    )
    models = {"current": model, "reset": reset}
    inputs = {
        "source_configuration": config.to_payload(),
        "source_transition": a.preflight.transition(source_step),
        "source_audit": source_audit,
        "event": event,
        "event_audit": event_audit,
        "target_configuration": model.configuration.to_payload(),
        "certificates": [c.to_payload() for c in pair],
        "initial_snapshots": {r: m.snapshot() for r, m in models.items()},
        "trajectory_scope": "each represented transition independently certified; no global pre-entry ideal-orbit shadow bound",
    }
    return models, dict(zip(models, pair, strict=True)), center, inputs


def bindings(a):
    paths = {r["path"] for r in a.preflight.bindings()}
    paths.update(
        {
            SELF,
            HERE + "test_p991a6_rg2b_campaign.py",
            HERE + "p991a5_native_spark_campaign.py",
            HERE + "aos_native_spark_oracle.py",
            HERE + "arg2b_native_spark_pressure_oracle.py",
            "src/pygrc/models/grc_9_v4_api_lifecycle.py",
            a.path("Plan.md"),
            a.preflight.RECORD,
        }
    )
    return [
        {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
        for p in sorted(paths)
    ]


def check_bindings(rows, root=ROOT):
    need(
        rows and len({r["path"] for r in rows}) == len(rows),
        "nonempty unique source bindings",
    )
    for row in rows:
        path = root / row["path"]
        need(
            not Path(row["path"]).is_absolute()
            and path.resolve().is_relative_to(root.resolve()),
            "portable binding",
        )
        need(
            sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "changed source/evidence: " + row["path"],
        )


def cold_restore(a, checkpoint, registry):
    calls = []
    original = a.kernel.step

    def count(k, *args, **kwargs):
        calls.append(1)
        return original(k, *args, **kwargs)

    expected = sum(
        r["kind"] == "step" for r in checkpoint["owner"]["publication"]["journal"]
    )
    a.native._section_witness.cache_clear()
    t = time.perf_counter()
    with (
        patch.object(owner, "_SCOPES", registry),
        patch.object(a.kernel, "step", count),
    ):
        restored = GRC9V4.from_state(checkpoint)
        need(
            restored.snapshot()["owner"]["publication"]
            == checkpoint["owner"]["publication"],
            "cold publication mismatch",
        )
    need(len(calls) == expected, "cold replay skipped journal steps")
    return {
        "seconds": time.perf_counter() - t,
        "ordinary_journal_steps": expected,
        "replayed_steps": len(calls),
        "whole_publication_equal": True,
    }


def profile(a, count=4):
    path = ROOT / a.path("Cost.json")
    need(not path.exists(), "refuse cost overwrite")
    ctx.threads = 1
    t = time.perf_counter()
    cap = Capture(a)
    times = {r: [] for r in ("current", "reset")}
    with cap.installed():
        models, certs, center, _ = setup(a, cap)
        setup_seconds = time.perf_counter() - t
        cold = a.kernel.cache_info()
        GRC9V4(models["current"].configuration)
        warm = a.kernel.cache_info()
        need(
            all(
                warm[k]["hits"] > cold[k]["hits"]
                for k in ("graph", "domain", "section")
            ),
            "static/complete-subject cache inactive",
        )
        for role, model in models.items():
            for beat in range(1, count + 1):
                start = time.perf_counter()
                before = model.configuration
                r = model.step_v4_input(a.delivery("cost-" + role, beat))
                native = time.perf_counter() - start
                need(r.committed and not r.local_gain, "prefix step")
                audit = a.audit(before, cap.step, deep=beat == 1)
                obs = observation(
                    a,
                    model.configuration.current,
                    model.configuration.policy,
                    certs[role],
                )
                raw = a.preflight.transition(cap.step)
                compact = compact_step(a, raw, audit, obs)
                lzma.compress(canonical_json_bytes(compact), preset=3)
                model.snapshot()
                times[role].append(
                    {
                        "seconds": time.perf_counter() - start,
                        "native_seconds": native,
                        "deep": beat == 1,
                        "full_diagnostic_bytes": len(
                            lzma.compress(canonical_json_bytes(raw))
                        ),
                        "compact_bytes": len(
                            lzma.compress(canonical_json_bytes(compact))
                        ),
                    }
                )
            print(
                json.dumps(
                    {
                        "family": a.family,
                        "profile_role": role,
                        "prefix_steps": count,
                        "seconds": time.perf_counter() - t,
                    }
                ),
                flush=True,
            )
        # Separate synthetic late-domain timing only; it never supplies a campaign state.
        synthetic = GRC9V4(
            replace(models["current"].configuration, current=center, reset=center)
        )
        late = []
        for beat in (1, 2):
            start = time.perf_counter()
            before = synthetic.configuration
            r = synthetic.step_v4_input(a.delivery("late-cost", beat))
            need(r.committed, r.reason)
            native = time.perf_counter() - start
            a.audit(before, cap.step, deep=beat == 1)
            observation(
                a,
                synthetic.configuration.current,
                synthetic.configuration.policy,
                certs["current"],
            )
            late.append(
                {
                    "seconds": time.perf_counter() - start,
                    "native_seconds": native,
                    "deep": beat == 1,
                }
            )
        cold_result = cold_restore(a, models["current"].snapshot(), {})
    costs = [r["seconds"] for rows in times.values() for r in rows if not r["deep"]] + [
        late[-1]["seconds"]
    ]
    native_cost = max(r["native_seconds"] for rows in times.values() for r in rows)
    deep_extra = max(r["seconds"] for rows in times.values() for r in rows if r["deep"])
    horizon = 400
    # 20-beat deep cadence, entry/window boundaries, cold replay, endpoint pressure.
    central = (
        setup_seconds
        + 2 * horizon * statistics.mean(costs)
        + 50 * deep_extra
        + 2 * horizon * cold_result["seconds"] / (count + 1)
        + 180
    )
    upper = (
        setup_seconds
        + 2 * horizon * max(costs) * 1.5
        + 50 * deep_extra
        + 4 * horizon * cold_result["seconds"] / (count + 1)
        + 300
    )
    value = seal(
        {
            "schema": "native-rg2b-campaign-cost-v1",
            "family": a.family,
            "source_bindings": bindings(a),
            "prefix": times,
            "late_domain_probe": late,
            "late_probe_scope": "synthetic near-domain timings only; not source-to-entry evidence",
            "cache_cold": cold,
            "cache_warm": warm,
            "cold_replay": cold_result,
            "setup_seconds": setup_seconds,
            "elapsed_seconds": time.perf_counter() - t,
            "estimate": {
                "central_seconds": central,
                "conservative_seconds": upper,
                "maximum_target_steps_per_role": horizon,
                "maximum_sample_native_seconds": native_cost,
                "time_limit_policy": "profile_and_report; no correctness cutoff or automatic precision change",
            },
            "peak_rss_mib": rss(),
            "flint_threads": ctx.threads,
        }
    )
    path.write_text(json.dumps(value, indent=2) + "\n")
    print(
        json.dumps(
            {
                "family": a.family,
                "forecast_minutes": central / 60,
                "conservative_minutes": upper / 60,
                "cost_seconds": value["elapsed_seconds"],
            }
        ),
        flush=True,
    )
    return value


def compact_step(a, raw, audit, obs):
    keys = ["after", "flux", "componentwise_error_bounds"]
    if a.family == "A_RG2b":
        keys.append("log_conductance_component_error")
    state = raw["after"]
    # Graph stored once in inputs; every diagnostic is reproducible from exact inputs.
    physical = {k: state[k] for k in ("C", "W_A", "charge") if k in state}
    value = {k: raw[k] for k in keys if k != "after"}
    value.update(
        after=physical,
        before_state_digest=digest(raw["before"]),
        after_state_digest=digest(raw["after"]),
        full_transition_digest=digest(raw),
        incoming_section_digest=digest(raw["section"]),
        returned_section_digest=digest(raw["restart_section"]),
        independent_audit=audit,
        membership=obs,
        proof_summary={
            which: {
                k: raw[which][k]
                for k in (
                    "section_error",
                    "section_tail",
                    "residual_error",
                    "query_shift",
                )
            }
            for which in ("section", "restart_section")
        },
    )
    return value


def fail_pending(a, model, beat, pressure):
    phases = [
        "incoming_section",
        "returned_section",
        "after_numerics",
        "after_window",
        "before_publication",
    ]
    if a.family == "A_RG2b":
        phases.insert(2, "conductance_writer")
    forks = []
    for phase in phases:
        fork = model.duplicate()
        root = fork._operation._spark_scope.published
        before = fork.snapshot()
        req = a.delivery("fault-" + phase, beat + 1)
        original_progress = owner.progress

        def fail(*args, phase=phase, **kwargs):
            if phase == "after_window":
                original_progress(*args, **kwargs)
            raise ValueError("injected " + phase)

        with ExitStack() as stack:
            if phase in ("incoming_section", "returned_section"):
                original = a.kernel._admitted_section
                incoming = fork.configuration.current

                def read(k, state, original=original, incoming=incoming, phase=phase):
                    if (state is incoming) == (phase == "incoming_section"):
                        raise ValueError("injected " + phase)
                    return original(k, state)

                stack.enter_context(patch.object(a.kernel, "_admitted_section", read))
            elif phase == "conductance_writer":
                stack.enter_context(patch.object(a.kernel, "_writer", side_effect=fail))
            else:
                target, attr = (
                    (type(fork._operation), "_publish")
                    if phase == "before_publication"
                    else (owner, "progress")
                )
                stack.enter_context(patch.object(target, attr, side_effect=fail))
            r = fork.step_v4_input(req)
        need(
            not r.committed
            and fork._operation._spark_scope.published is root
            and fork.snapshot() == before,
            "full rollback at " + phase,
        )
        pressure.append(
            {
                "fault": phase,
                "whole_root_unchanged": True,
                "rejected": True,
                "target_beat": beat,
            }
        )
        forks.append((fork, req))
    return forks


def campaign(a):
    record = ROOT / a.path("Campaign.json")
    names = ("current", "reset", "inputs", "diagnostics", "checkpoints")
    paths = {n: a.path(n + ".jsonl.xz") for n in names}
    need(
        not record.exists() and not any((ROOT / p).exists() for p in paths.values()),
        "refuse primary overwrite",
    )
    cost = json.loads((ROOT / a.path("Cost.json")).read_bytes())
    need(cost == seal(cost) and cost["family"] == a.family, "cost seal/family")
    check_bindings(cost["source_bindings"])
    ctx.threads = 1
    start = time.perf_counter()
    cap = Capture(a)
    streams = {n: Stream(p) for n, p in paths.items()}
    progress = {}
    boundaries = {r: {} for r in ("current", "reset")}
    pressure = []
    forks = []
    try:
        with cap.installed():
            models, certs, _, inputs = setup(a, cap)
            streams["inputs"].write(inputs)
            for role, model in models.items():
                cert = certs[role]
                fixed_reset = model.configuration.reset
                entry = None
                window = []
                gains = 0
                previous_full = None
                prior_checkpoint = None
                times = []
                obs = observation(
                    a, model.configuration.current, model.configuration.policy, cert
                )
                for beat in range(1, 401):
                    near = Q(obs["squared_norm"]) <= 4
                    # The selected curve parameter can change discontinuously;
                    # an outside norm does not predict the next entry distance.
                    prior_checkpoint = model.snapshot()
                    t = time.perf_counter()
                    before = model.configuration
                    req = a.delivery(role, beat)
                    r = model.step_v4_input(req)
                    native_seconds = time.perf_counter() - t
                    need(r.committed, r.reason)
                    need(
                        model.configuration.reset == fixed_reset,
                        "reset baseline changed",
                    )
                    step = cap.step
                    need(
                        step.before == before.current
                        and step.after == model.configuration.current,
                        "public/captured state mismatch",
                    )
                    obs = observation(a, step.after, model.configuration.policy, cert)
                    deep = (
                        beat == 1
                        or beat % 20 == 0
                        or obs["inside"]
                        or (near and entry is None)
                    )
                    audit = a.audit(before, step, deep=deep)
                    raw = a.preflight.transition(step)
                    if obs["inside"]:
                        if entry is None:
                            entry = beat
                            need(
                                prior_checkpoint is not None,
                                "missing pre-entry checkpoint",
                            )
                            boundaries[role]["before_entry"] = prior_checkpoint
                            streams["checkpoints"].write(
                                {
                                    "role": role,
                                    "label": "before_entry",
                                    "beat": beat - 1,
                                    "checkpoint": prior_checkpoint,
                                }
                            )
                            if previous_full is not None:
                                streams["diagnostics"].write(
                                    {
                                        "role": role,
                                        "beat": beat - 1,
                                        "transition": previous_full,
                                    }
                                )
                        window.append(beat)
                    else:
                        window = []
                    cp = model._operation._published.completion
                    if role == "current":
                        need(len(cp.observations) == len(window), "window mismatch")
                    else:
                        need(
                            cp.event is None and r.local_gain == 0,
                            "reset credited live child",
                        )
                    gains += r.local_gain
                    streams[role].write(
                        dict(
                            compact_step(a, raw, audit, obs),
                            beat=beat,
                            local_gain=r.local_gain,
                            native_window_observations=len(cp.observations),
                            receipts=[v.to_payload() for v in r.emitted_receipts],
                            native_seconds=native_seconds,
                        )
                    )
                    if beat == 1 or obs["inside"]:
                        streams["diagnostics"].write(
                            {"role": role, "beat": beat, "transition": raw}
                        )
                    previous_full = raw
                    label = {1: "entry", 2: "first_window", 3: "complete"}.get(
                        len(window)
                    )
                    if label:
                        checkpoint = model.snapshot()
                        boundaries[role][label] = checkpoint
                        streams["checkpoints"].write(
                            {
                                "role": role,
                                "label": label,
                                "beat": beat,
                                "checkpoint": checkpoint,
                            }
                        )
                    if role == "current" and len(window) == 2:
                        snapshot = model.snapshot()
                        root = model._operation._spark_scope.published
                        duplicate = model.step_v4_input(req)
                        zero = model.step_v4_input(
                            GRCV4StepRequestInput(
                                "grcv4-step-request-input-v1",
                                "zero-window",
                                0,
                                FrozenJSONMap({}),
                            )
                        )
                        model.compute_observables()
                        need(
                            not duplicate.committed
                            and not zero.committed
                            and model.snapshot() == snapshot
                            and model._operation._spark_scope.published is root,
                            "duplicate/zero/read advanced window",
                        )
                        pressure.append(
                            {
                                "fault": "duplicate_zero_read",
                                "whole_root_unchanged": True,
                            }
                        )
                        forks = fail_pending(a, model, beat, pressure)
                    times.append(time.perf_counter() - t)
                    if beat == 1 or beat % 10 == 0 or obs["inside"]:
                        print(
                            json.dumps(
                                {
                                    "family": a.family,
                                    "role": role,
                                    "beat": beat,
                                    "inside": obs["inside"],
                                    "norm_squared": float(Q(obs["squared_norm"])),
                                    "gain": r.local_gain,
                                    "seconds": time.perf_counter() - start,
                                    "native_seconds": native_seconds,
                                    "peak_mib": rss(),
                                }
                            ),
                            flush=True,
                        )
                    if (role == "current" and r.local_gain) or (
                        role == "reset" and len(window) == 3
                    ):
                        progress[role] = {
                            "entry": entry,
                            "completion": beat,
                            "window": window,
                            "local_gain": gains,
                            "target_steps": beat,
                            "research_expectation": list(a.expected),
                            "matches_research_expectation": (entry, beat) == a.expected,
                            "elapsed_window": str(2 * a.duration),
                            "mean_audited_seconds": statistics.mean(times),
                        }
                        break
                else:
                    raise ValueError(
                        "400 target beats without completion; no silent extension"
                    )
            need(
                progress["current"]["local_gain"] == 1
                and progress["reset"]["local_gain"] == 0,
                "once-only role gain",
            )
            endpoint_controls(models, certs, boundaries, forks, pressure)
            registry = {}
            cold = {}
            for role in models:
                print(
                    json.dumps(
                        {"family": a.family, "cold_replay": role, "status": "starting"}
                    ),
                    flush=True,
                )
                cold[role] = cold_restore(a, boundaries[role]["complete"], registry)
                print(
                    json.dumps({"family": a.family, "cold_replay": role, **cold[role]}),
                    flush=True,
                )
            need(cap.backends == {"flint"}, "FLINT execution required")
    finally:
        for stream in streams.values():
            stream.close()
    refs = [streams[n].reference() for n in names]
    check_bindings(cost["source_bindings"])
    value = seal(
        {
            "schema": "native-rg2b-campaign-v1",
            "family": a.family,
            "leaf": "P9-9.1a.6-" + a.family + ".5",
            "status": "verified_pending_review",
            "native_endpoint_verified": True,
            "native_completion_support": False,
            "user_accepted": False,
            "roles": progress,
            "pressure": pressure,
            "cold_replay": cold,
            "streams": refs,
            "source_bindings": cost["source_bindings"],
            "cost_record_digest": cost["record_digest"],
            "entry_revision": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "elapsed_seconds": time.perf_counter() - start,
            "peak_rss_mib": rss(),
            "flint_threads": ctx.threads,
            "native_precision_bits": 256,
            "oracle_precision_bits": 768,
            "exact_charge": "21",
            "duration": str(a.duration),
            "full_trajectory_runs": 2,
            "physical_supporting_tail_steps": 0,
            "target_vertices": 15,
            "target_edges": 16,
            "evidence_format": "exact_states_outputs_chain_audit_summaries_and_full_diagnostic_hashes_v1",
            "check_scope": "retained integrity/exact incidence; omitted chains require explicit --reconstruct native execution",
            "next_leaf": "P9-9.1a.7 after separate review of both RG2b campaigns",
        }
    )
    record.write_text(json.dumps(value, indent=2) + "\n")
    print(
        json.dumps(
            {
                "family": a.family,
                "status": "campaign_complete",
                "roles": progress,
                "minutes": value["elapsed_seconds"] / 60,
                "compressed_bytes": sum(r["compressed_bytes"] for r in refs),
            }
        ),
        flush=True,
    )
    return value


def stream_rows(path):
    prior = None
    with lzma.open(path, "rt") as stream:
        for row in map(json.loads, stream):
            need(
                row == seal(row) and row["previous_record_digest"] == prior,
                "stream digest chain",
            )
            prior = row["record_digest"]
            yield row


def check(a, root=ROOT, *, numerical_samples=False):
    value = json.loads((root / a.path("Campaign.json")).read_bytes())
    need(
        value == seal(value)
        and value["schema"] == "native-rg2b-campaign-v1"
        and value["family"] == a.family,
        "campaign identity",
    )
    need(
        value["native_endpoint_verified"] is True
        and value["native_completion_support"] is False
        and value["user_accepted"] is False
        and value["full_trajectory_runs"] == 2
        and value["physical_supporting_tail_steps"] == 0,
        "bounded review scope",
    )
    check_bindings(value["source_bindings"], root)
    check_bindings(value["streams"], root)
    cost = json.loads((root / a.path("Cost.json")).read_bytes())
    need(
        cost == seal(cost) and cost["record_digest"] == value["cost_record_digest"],
        "cost binding",
    )
    streams = {
        r["path"].removeprefix(a.prefix).removesuffix(".jsonl.xz"): r
        for r in value["streams"]
    }
    data = {}
    for name, ref in streams.items():
        rows = list(stream_rows(root / ref["path"]))
        need(
            len(rows) == ref["records"]
            and rows[-1]["record_digest"] == ref["last_record_digest"],
            "stream count/terminal",
        )
        data[name] = rows
    inputs = data["inputs"][0]
    from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration
    from cos_native_spark_oracle import incidence

    config = GRC9V4SparkConfiguration.from_payload(inputs["target_configuration"])
    B = incidence(config.reference.graph.to_payload())
    for role in ("current", "reset"):
        before = getattr(config, role).to_payload()
        gains = 0
        for beat, row in enumerate(data[role], 1):
            need(
                row["beat"] == beat and row["before_state_digest"] == digest(before),
                "exact connected trajectory",
            )
            after = dict(before, **row["after"])
            need(digest(after) == row["after_state_digest"], "exact after identity")
            C = M([[Q(x)] for x in before["C"]]) - a.duration * B * M(
                [[Q(x)] for x in row["flux"]]
            )
            need(
                list(map(str, C.entries())) == list(after["C"])
                and sum(C.entries()) == 21
                and all(c >= 0 for c in C.entries()),
                "exact represented incidence/charge/positivity",
            )
            gains += row["local_gain"]
            before = after
        p = value["roles"][role]
        need(
            p["target_steps"] == p["completion"] == len(data[role])
            and p["local_gain"] == gains == (1 if role == "current" else 0),
            "role endpoint/gain",
        )
        need(
            p["window"] == list(range(p["entry"], p["completion"] + 1))
            and len(p["window"]) == 3,
            "positive window",
        )
        need(
            all(r["membership"]["inside"] for r in data[role][-3:]),
            "saved entry/window membership",
        )
        need(
            value["cold_replay"][role]["replayed_steps"] == len(data[role]) + 1
            and value["cold_replay"][role]["whole_publication_equal"],
            "full cold replay",
        )
    for sample in data["diagnostics"]:
        row = data[sample["role"]][sample["beat"] - 1]
        need(
            digest(sample["transition"]) == row["full_transition_digest"],
            "full sample identity",
        )
        if numerical_samples:
            step = a.preflight.decoded(sample["transition"])
            a.audit(config, step, deep=False)
    return value


def reconstruct(a, role, beat):
    """Explicit selected diagnostic reproduction; executes native numerics."""
    check(a)
    inputs = next(stream_rows(ROOT / a.path("inputs.jsonl.xz")))
    from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration

    config = GRC9V4SparkConfiguration.from_payload(inputs["target_configuration"])
    state = getattr(config, role)
    for row in stream_rows(ROOT / a.path(role + ".jsonl.xz")):
        if row["beat"] == beat:
            step = owner.kernel(config).step(state, str(a.duration))
            raw = a.preflight.transition(step)
            need(
                digest(raw) == row["full_transition_digest"],
                "diagnostic reproduction differs",
            )
            a.audit(config, step, deep=False)
            return {
                "family": a.family,
                "role": role,
                "beat": beat,
                "full_transition_digest": digest(raw),
                "native_executed": True,
            }
        state = type(state).from_canonical_bytes(
            canonical_json_bytes(dict(state.to_payload(), **row["after"]))
        )
    raise ValueError("unknown retained beat")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=FAMILIES)
    action = parser.add_mutually_exclusive_group(required=True)
    for flag in ("profile", "run", "check", "reconstruct"):
        action.add_argument("--" + flag, action="store_true")
    parser.add_argument("--numerical-samples", action="store_true")
    parser.add_argument("--role", choices=("current", "reset"), default="current")
    parser.add_argument("--beat", type=int, default=1)
    args = parser.parse_args()
    a = Adapter(args.family)
    if args.profile:
        profile(a)
    elif args.run:
        campaign(a)
    elif args.check:
        v = check(a, numerical_samples=args.numerical_samples)
        print(
            json.dumps(
                {
                    "family": a.family,
                    "status": "integrity_pass",
                    "roles": v["roles"],
                    "native_rerun": False,
                }
            )
        )
    else:
        print(json.dumps(reconstruct(a, args.role, args.beat)))
