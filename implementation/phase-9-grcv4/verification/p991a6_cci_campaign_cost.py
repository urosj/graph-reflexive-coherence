"""Final bounded C_CI cost gate using the exact campaign verification path."""

import argparse
import json
import statistics
import tempfile
import time
from hashlib import sha256
from pathlib import Path

import p991a6_cci_preflight as preflight
import p991a6_cci_pressure as pressure
from flint import ctx
from flint import fmpq as Q
from p991a4_native_spark_preflight import rss, summary
from p991a5_native_spark_verify import classify_and_membership, need
from p991a6_cci_campaign import BASE, HERE, ROOT, Stream, delivery, seal, setup
from p991a6_cci_campaign_verify import Capture, verify

from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate, _verify
from pygrc.models.grc_v4_spark_cci import SparkCCIKernel

RECORD = BASE + "P9-9.1a.6-CCI.5-Cost.json"


def forecast(rows, setup_seconds, checkpoint_seconds):
    roles = {}
    for role, samples in rows.items():
        costs = [x["seconds"] for x in samples]
        # 50% headroom for late state/ledger costs, plus checkpoint and pressure reserve.
        roles[role] = {
            "total_seconds": summary(costs),
            "native_seconds": summary([x["native_seconds"] for x in samples]),
            "maximum_resource_bits": max(x["resource_bits"] for x in samples),
            "upper_seconds": 400 * max(1.5 * statistics.mean(costs), max(costs)),
            "central_seconds": 400 * statistics.mean(costs),
        }
    reserve = max(120, 30 * checkpoint_seconds)
    central = (
        setup_seconds + sum(r["central_seconds"] for r in roles.values()) + reserve
    )
    upper = setup_seconds + sum(r["upper_seconds"] for r in roles.values()) + reserve
    return roles, {
        "central_seconds": central,
        "upper_seconds": upper,
        "reserve_seconds": reserve,
        "campaign_cap_seconds": 1800,
        "within_budget": upper < 1800,
        "maximum_target_beats_per_role": 400,
    }


def run(count=20):
    need(not (ROOT / RECORD).exists(), "do not overwrite final cost record")
    prior = preflight.check(ROOT)
    pressured = pressure.check(ROOT)
    ctx.threads = 1
    start = time.perf_counter()
    cap = Capture()
    rows = {r: [] for r in ("current", "reset")}
    with tempfile.TemporaryDirectory(prefix="cci-final-cost-") as tmp, cap.installed():
        models, certs, _ = setup(cap)
        setup_seconds = time.perf_counter() - start
        cold = SparkCCIKernel.root_cache_info()
        proof_cold = _verify.cache_info()._asdict()
        GRC9V4(models["current"].configuration)
        for c in certs.values():
            CompletionCertificate.from_payload(c.to_payload())
        warm = SparkCCIKernel.root_cache_info()
        proof_warm = _verify.cache_info()._asdict()
        need(
            warm["hits"] > cold["hits"]
            and proof_warm["hits"] >= proof_cold["hits"] + 2,
            "static caches inactive",
        )
        stream = Stream(str(Path(tmp) / "samples.jsonl.xz"))
        try:
            for beat in range(1, count + 1):
                for role, model in models.items():
                    need(time.perf_counter() - start < 180, "final cost sampling cap")
                    t = time.perf_counter()
                    result = model.step_v4_input(delivery("cost-" + role, beat))
                    native = time.perf_counter() - t
                    need(
                        result.committed and not result.local_gain,
                        "bounded prefix unexpectedly completed",
                    )
                    data = cap.payload()
                    audit = verify(model.configuration, data, certs[role], role)
                    obs = classify_and_membership(
                        model.configuration.current,
                        model.configuration.policy,
                        certs[role],
                    )
                    stream.write(
                        {
                            "beat": beat,
                            "role": role,
                            "stage": data,
                            "independent_root_and_error_audit": audit,
                            "membership": obs,
                        }
                    )
                    # Includes the snapshot path used dynamically near entry, conservatively at every sample.
                    snapshot = model.snapshot()
                    rows[role].append(
                        {
                            "seconds": time.perf_counter() - t,
                            "native_seconds": native,
                            "resource_bits": max(
                                max(
                                    abs(Q(x).numerator).bit_length(),
                                    Q(x).denominator.bit_length(),
                                )
                                for x in model.configuration.current.C
                            ),
                            "record_digest": stream.last,
                        }
                    )
                if beat in (1, count):
                    print(
                        json.dumps(
                            {
                                "cost_sample": beat,
                                "elapsed_seconds": time.perf_counter() - start,
                            }
                        ),
                        flush=True,
                    )
        finally:
            stream.close()
        t = time.perf_counter()
        GRC9V4.from_state(snapshot)
        checkpoint_seconds = time.perf_counter() - t
        need(cap.backends == {"flint"}, "native root admission left FLINT")
        reference = stream.reference()
        reference.pop("path")
    roles, estimate = forecast(rows, setup_seconds, checkpoint_seconds)
    paths = {
        r["path"] for r in prior["source_bindings"] if r["path"].startswith("src/")
    } | {
        HERE + n
        for n in (
            "p991a6_cci_campaign.py",
            "p991a6_cci_campaign_verify.py",
            "p991a6_cci_campaign_cost.py",
            "p991a6_cci_subjects.py",
            "p991a6_cci_preflight.py",
            "cci_native_spark_oracle.py",
            "cci_native_spark_pressure_oracle.py",
            "p991a5_native_spark_campaign.py",
            "p991a5_native_spark_verify.py",
            "cos_native_spark_oracle.py",
            "p991a2_native_spark_numerics.py",
        )
    }
    target = models["current"].configuration
    value = seal(
        {
            "schema": "grc9v4-native-cci-final-cost-v1",
            "leaf": "P9-9.1a.6-C_CI.5",
            "family": "C_CI",
            "native_endpoint_verified": False,
            "native_completion_support": False,
            "full_trajectory_runs": 0,
            "samples": rows,
            "roles": roles,
            "estimate": estimate,
            "setup_seconds": setup_seconds,
            "checkpoint_restore_seconds": checkpoint_seconds,
            "elapsed_seconds": time.perf_counter() - start,
            "sampling_cap_seconds": 180,
            "peak_rss_mib": rss(),
            "sample_trace_digest": reference,
            "sample_trace_scope": "discarded bounded timing prefix; primary trajectory retained separately",
            "caches": {
                "root_before": cold,
                "root_after": warm,
                "proof_before": proof_cold,
                "proof_after": proof_warm,
            },
            "exact_backend": "flint",
            "native_precision_bits": 256,
            "oracle_precision_bits": 768,
            "target_graph_digest": target.reference.graph.graph_digest,
            "target_profile_id": target.reference.profile.complete_profile_id,
            "certificate_ids": [c.certificate_id for c in certs.values()],
            "preflight_record_digest": prior["record_digest"],
            "pressure_record_digest": pressured["record_digest"],
            "source_bindings": [
                {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
                for p in sorted(paths)
            ],
        }
    )
    need(
        value["elapsed_seconds"] < 180 and value["peak_rss_mib"] < 1024,
        "bounded cost check exceeded limits",
    )
    (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")
    return value


def check(root=ROOT):
    from p991a6_cpc_epoch import previous_bytes
    root = Path(root)
    v = json.loads((root / RECORD).read_bytes())
    need(v == seal(v), "unsealed final cost check")
    need(all(len(x) == 20 for x in v["samples"].values()), "bounded sample count")
    need(
        (v["roles"], v["estimate"])
        == forecast(v["samples"], v["setup_seconds"], v["checkpoint_restore_seconds"]),
        "changed final forecast",
    )
    for r in v["source_bindings"]:
        need(
            sha256(previous_bytes(root, r["path"])).hexdigest() == r["sha256"],
            "changed final cost source: " + r["path"],
        )
    return v


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", action="store_true")
    args = p.parse_args()
    value = run() if args.run else check()
    print(json.dumps(value["estimate"]), flush=True)
