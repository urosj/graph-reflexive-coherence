"""Late-state recovery estimate, preserving the original stopped campaign cost."""

import argparse
import json
import lzma
import statistics
import tempfile
import time
from dataclasses import replace
from hashlib import sha256
from io import BytesIO
from pathlib import Path

from flint import ctx
from p991a5_native_spark_verify import need
from p991a6_cpc_campaign import BASE, FILES, HERE, ROOT, Stream, delivery, seal
from p991a6_cpc_campaign_verify import Capture, classify_and_membership, decoded, verify
from p991a6_cpc_evidence_epoch import evidence_bytes
from p991a6_cpc_preflight import rss

from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_spark_cpc import SparkCPCKernel

STOP = BASE + "P9-9.1a.6-CPC.5-TimingStop.json.xz"
RECORD = BASE + "P9-9.1a.6-CPC.5-ResumeCost.json"


def rows(path):
    with lzma.open(BytesIO(evidence_bytes(ROOT, path)), "rt") as stream:
        return [json.loads(line) for line in stream]


def stopped():
    value = json.loads(lzma.decompress((ROOT / STOP).read_bytes()))
    need(value == seal(value), "unsealed timing stop")
    for ref in [*value["source_bindings"], *value["streams"].values()]:
        need(
            sha256(evidence_bytes(ROOT, ref["path"])).hexdigest() == ref["sha256"],
            "changed stopped input",
        )
    return value


def forecast(samples, stop, current, reset):
    # Preserve the observed late public ledger overhead and transient slowdown;
    # a fresh late-state timing model has no historical publication journal.
    observed_max = max(r["ordinary_seconds"] for r in reset)
    native_limit = 2 * max(observed_max, max(r["native_seconds"] for r in samples))
    per_beat = max(
        1.5 * statistics.mean(r["seconds"] for r in samples),
        max(r["seconds"] for r in samples),
        native_limit
        + statistics.mean(r["seconds"] - r["native_seconds"] for r in samples),
    )
    journal = (
        1.5
        * (
            sum(r["ordinary_seconds"] for r in current[:375])
            + sum(r["ordinary_seconds"] for r in reset[:150])
        )
        + 10
    )
    replay = len(reset) - 150
    upper = journal + (400 - len(reset) + replay) * per_beat + 240
    central = (
        journal / 1.5
        + (400 - len(reset) + replay) * statistics.mean(r["seconds"] for r in samples)
        + 240
    )
    return {
        "central_remaining_seconds": central,
        "upper_remaining_seconds": upper,
        "original_elapsed_seconds": stop["elapsed_seconds_budget"],
        "combined_upper_seconds": upper + stop["elapsed_seconds_budget"],
        "within_budget": upper + stop["elapsed_seconds_budget"] < 1800,
        "campaign_cap_seconds": 1800,
        "native_rolling_limit_seconds": native_limit,
        "per_beat_upper_seconds": per_beat,
        "cold_journal_replay_upper_seconds": journal,
        "pressure_reserve_seconds": 240,
        "maximum_target_beats_per_role": 400,
    }


def run():
    need(not (ROOT / RECORD).exists(), "do not overwrite recovery estimate")
    stop = stopped()
    current, reset = (rows(stop["streams"][r]["path"]) for r in ("current", "reset"))
    saved = rows(stop["streams"]["checkpoints"]["path"])[-1]["checkpoint"]
    inputs = rows(FILES["inputs"])[0]
    config = GRC9V4SparkConfiguration.from_payload(
        saved["owner"]["publication"]["configuration"]
    )
    config = replace(
        config,
        current=decoded(reset[-1]["stage"]).after,
        step_index=reset[-1]["step_index"],
        time=reset[-1]["time"],
    )
    cert = CompletionCertificate.from_payload(inputs["certificates"][1])
    ctx.threads = 1
    start = time.perf_counter()
    cap, samples = Capture(), []
    with tempfile.TemporaryDirectory(prefix="cpc-resume-cost-") as tmp, cap.installed():
        model = GRC9V4(config)
        cold = SparkCPCKernel.domain_cache_info()
        decay_cold = SparkCPCKernel.decay_cache_info()
        stream = Stream(str(Path(tmp) / "late-samples.jsonl.xz"))
        try:
            for beat in range(1, 21):
                need(time.perf_counter() - start < 180, "bounded recovery sampling cap")
                t = time.perf_counter()
                result = model.step_v4_input(delivery("late-cost", beat))
                native = time.perf_counter() - t
                need(result.committed and not result.local_gain, "late cost step")
                data = cap.payload()
                audit = verify(model.configuration, data, cert, "reset")
                membership = classify_and_membership(
                    model.configuration.current, model.configuration.policy, cert
                )
                stream.write({"stage": data, "audit": audit, "membership": membership})
                model.snapshot()
                samples.append(
                    {"seconds": time.perf_counter() - t, "native_seconds": native}
                )
        finally:
            stream.close()
        trace = stream.reference()
        trace.pop("path")
    warm = SparkCPCKernel.domain_cache_info()
    decay_warm = SparkCPCKernel.decay_cache_info()
    need(
        warm["hits"] > cold["hits"]
        and decay_warm["hits"] > decay_cold["hits"]
        and cap.backends == {"flint"},
        "late caching/backend",
    )
    estimate = forecast(samples, stop, current, reset)
    prior = json.loads((ROOT / BASE / "P9-9.1a.6-CPC.5-Cost.json").read_bytes())
    paths = {r["path"] for r in prior["source_bindings"]} | {
        STOP,
        HERE + "p991a6_cpc_resume_cost.py",
        HERE + "p991a6_cpc_campaign_resume.py",
        BASE + "P9-9.1a.6-CPC.5-Cost.json",
    }
    value = seal(
        {
            "schema": "grc9v4-native-cpc-resume-cost-v1",
            "samples": samples,
            "estimate": estimate,
            "late_state_digest": sha256(
                canonical_json_bytes(reset[-1]["stage"]["after"])
            ).hexdigest(),
            "late_state_beat": 191,
            "timing_scope": "same exact late C/Z subject; cold journal and historical publication overhead budgeted separately from observed native trace costs",
            "original_cost_record_digest": prior["record_digest"],
            "preflight_record_digest": prior["preflight_record_digest"],
            "pressure_record_digest": prior["pressure_record_digest"],
            "elapsed_seconds": time.perf_counter() - start,
            "sampling_cap_seconds": 180,
            "peak_rss_mib": rss(),
            "caches": {
                "domain_before": cold,
                "domain_after": warm,
                "decay_before": decay_cold,
                "decay_after": decay_warm,
            },
            "exact_backend": "flint",
            "native_precision_bits": 256,
            "oracle_precision_bits": 768,
            "sample_trace_digest": trace,
            "source_bindings": [
                {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
                for p in sorted(paths)
            ],
        }
    )
    need(value["elapsed_seconds"] < 180 and rss() < 1024, "bounded recovery gate")
    (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")
    return value


def check():
    from p991a6_cpc_resume_epoch import previous_bytes

    value = json.loads((ROOT / RECORD).read_bytes())
    need(value == seal(value), "unsealed recovery estimate")
    stop = stopped()
    need(
        value["estimate"]
        == forecast(
            value["samples"],
            stop,
            rows(stop["streams"]["current"]["path"]),
            rows(stop["streams"]["reset"]["path"]),
        ),
        "changed recovery forecast",
    )
    for ref in value["source_bindings"]:
        need(
            sha256(previous_bytes(ROOT, ref["path"])).hexdigest() == ref["sha256"],
            "changed recovery source: " + ref["path"],
        )
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    value = run() if args.run else check()
    print(json.dumps(value["estimate"]), flush=True)
