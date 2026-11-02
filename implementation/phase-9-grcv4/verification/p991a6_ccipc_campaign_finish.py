"""Paired cold validation: reconstruct current authority before its reset fork.

The primary harness is frozen by the cost record. --fresh applies this corrected
verification sequence to a new campaign. --finish validates retained completed
primary streams after the original isolated-reset restore rejected shared claims.
Neither mode alters native mathematics or manufactures a physical trajectory.
"""

import argparse
import json
import lzma
import math
import time
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

import p991a6_ccipc_campaign as campaign
from flint import ctx
from flint import fmpq as Q
from p991a4_native_spark_preflight import rss, summary
from p991a5_native_spark_campaign import endpoint_controls
from p991a5_native_spark_verify import need
from p991a6_ccipc_campaign_cost import RECORD as COST
from p991a6_ccipc_campaign_cost import check as check_cost
from p991a6_ccipc_campaign_verify import Capture

from pygrc.models import grc_9_v4_spark_owner as owner
from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_spark_ccipc import SparkCCIPCKernel
from pygrc.models.grc_v4_spark_state import CIPC_NUMERICAL_POLICY
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = campaign.ROOT
SELF = campaign.HERE + "p991a6_ccipc_campaign_finish.py"


class PairedCold:
    """One isolated authority registry, shared by two genuinely cold journals."""

    def __init__(self):
        self.registry = {}
        self.models = []

    def __call__(self, checkpoint):
        calls = []
        original = SparkCCIPCKernel.step

        def counted(k, *args, **kwargs):
            calls.append(1)
            return original(k, *args, **kwargs)

        expected = sum(
            a["kind"] == "step" for a in checkpoint["owner"]["publication"]["journal"]
        )
        start = time.perf_counter()
        with (
            patch.object(owner, "_SCOPES", self.registry),
            patch.object(SparkCCIPCKernel, "step", counted),
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


def rows(name):
    previous = None
    with lzma.open(ROOT / campaign.FILES[name], "rt") as stream:
        for line in stream:
            row = json.loads(line)
            need(
                row == campaign.seal(row) and row["previous_record_digest"] == previous,
                "broken completed primary stream",
            )
            previous = row["record_digest"]
            yield row


def publish(value):
    path = ROOT / campaign.RECORD
    path.write_bytes(
        lzma.compress(canonical_json_bytes(campaign.seal(value)), preset=3)
    )
    return campaign.check(ROOT)


def fresh():
    pair = PairedCold()
    with patch.object(campaign, "cold_restore", pair):
        value = campaign.campaign()
    value["source_bindings"].append(
        {"path": SELF, "sha256": sha256((ROOT / SELF).read_bytes()).hexdigest()}
    )
    return publish(value)


def finish(log_path, anchor_path):
    need(not (ROOT / campaign.RECORD).exists(), "do not overwrite completed campaign")
    log_path, anchor_path = Path(log_path), Path(anchor_path)
    log = log_path.read_text()
    need(
        log.rstrip().endswith(
            "ValueError: checkpoint accounting needs its shared authority"
        ),
        "only the diagnosed shared-accounting restore rejection is recoverable here",
    )
    anchor = json.loads(anchor_path.read_text())
    # The saved progress flush anchors the original monotonic elapsed clock to
    # the log's filesystem timestamp. Round outward by one second; keep provenance.
    initial_seconds = math.ceil(
        log_path.stat().st_mtime - anchor["inferred_start_unix_seconds"] + 1
    )
    ctx.threads = 1
    timing = check_cost(ROOT)
    start = time.perf_counter()
    progress = [json.loads(line) for line in log.splitlines() if line.startswith("{")]
    primary_end = next(
        row["elapsed_seconds"]
        for row in progress
        if row.get("role") == "reset" and row.get("beat") == 377
    )
    cold_start = next(
        row["elapsed_seconds"]
        for row in progress
        if row.get("cold_checkpoint") == "current" and row.get("status") == "starting"
    )
    pending = {
        row["beat"]: row["elapsed_seconds"]
        for row in progress
        if row.get("role") == "current" and row.get("beat") in (374, 375)
    }
    estimate = {
        "cold_replay_seconds": 755
        * timing["checkpoint_restore_seconds"]
        / timing["cold_replay"]["replayed_steps"],
        "measured_pending_control_seconds": pending[375] - pending[374],
        "measured_endpoint_control_seconds": cold_start - primary_end,
        "reserve_seconds": 60,
    }
    estimate["central_seconds"] = sum(estimate.values())
    estimate["upper_seconds"] = 1.5 * estimate["central_seconds"]
    estimate["combined_upper_seconds"] = initial_seconds + estimate["upper_seconds"]
    print(json.dumps({"paired_validation_estimate": estimate}), flush=True)
    inputs = next(rows("inputs"))
    checkpoints = list(rows("checkpoints"))
    boundaries = {r: {} for r in campaign.EXPECTED}
    for row in checkpoints:
        if row["label"] != "periodic":
            boundaries[row["role"]][row["label"]] = row["checkpoint"]
    roles, refs = {}, []
    for role in campaign.EXPECTED:
        data = list(rows(role))
        inside = [r["beat"] for r in data if r["membership"]["inside"]]
        need(
            (inside[0], len(data)) == campaign.EXPECTED[role],
            "primary endpoint missing",
        )
        roles[role] = {
            "entry": inside[0],
            "completion": len(data),
            "target_steps": len(data),
            "local_gain": sum(r["local_gain"] for r in data),
            "window": inside[-3:],
            "duration": "32",
            "elapsed_window": "64",
            "maximum_step_error": str(
                max(Q(r["independent_error_upper"]) for r in data)
            ),
            "final_membership": data[-1]["membership"],
            "native_timing_seconds": summary([r["ordinary_seconds"] for r in data]),
        }
    for name in campaign.FILES:
        data = list(rows(name))
        path = campaign.FILES[name]
        raw = (ROOT / path).read_bytes()
        refs.append(
            {
                "path": path,
                "sha256": sha256(raw).hexdigest(),
                "compressed_bytes": len(raw),
                "records": len(data),
                "last_record_digest": data[-1]["record_digest"],
            }
        )
    certs = dict(
        zip(
            campaign.EXPECTED,
            (CompletionCertificate.from_payload(c) for c in inputs["certificates"]),
            strict=True,
        )
    )
    pair, cold, pressure, cap = PairedCold(), {}, [], Capture()
    with cap.installed():
        for role in campaign.EXPECTED:
            print(
                json.dumps(
                    {
                        "paired_cold": role,
                        "status": "starting",
                        "elapsed_seconds": time.perf_counter() - start,
                    }
                ),
                flush=True,
            )
            cold[role] = pair(boundaries[role]["complete"])
            print(json.dumps({"paired_cold": role, **cold[role]}), flush=True)
        models = dict(zip(campaign.EXPECTED, pair.models, strict=True))
        with patch.object(owner, "_SCOPES", pair.registry):
            pending = GRC9V4.from_state(boundaries["current"]["first_window"])
            before, root = pending.snapshot(), pending._operation._spark_scope.published
            duplicate = pending.step_v4_input(campaign.delivery("current", 375))
            zero = pending.step_v4_input(
                GRCV4StepRequestInput(
                    "grcv4-step-request-input-v1", "paired-zero", 0, FrozenJSONMap({})
                )
            )
            pending.compute_observables()
            need(
                not duplicate.committed
                and not zero.committed
                and pending.snapshot() == before
                and pending._operation._spark_scope.published is root,
                "paired pending no-op altered publication",
            )
            pressure.append(
                {
                    "fault": "duplicate_zero_read",
                    "target_beat": 375,
                    "whole_root_unchanged": True,
                }
            )
            forks = campaign.fail_before_completion(pending, "current", 375, pressure)
            endpoint_controls(models, certs, boundaries, forks, pressure)
        need(cap.backends == {"flint"}, "paired validation left FLINT")
    completion = models["current"].compute_observables()["completion"]
    need(
        len(completion["children"]) == len(completion["consumed_occurrences"]) == 1,
        "paired authority lost once-only child",
    )
    target = models["current"].configuration
    elapsed = initial_seconds + time.perf_counter() - start
    paths = {
        SELF,
        COST,
        campaign.HERE + "test_p991a6_ccipc_campaign_finish.py",
        *(r["path"] for r in timing["source_bindings"]),
    }
    for row in refs:
        need(
            sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
            "primary stream changed during validation",
        )
    value = {
        "schema": "grc9v4-native-ccipc-campaign-v1",
        "leaf": "P9-9.1a.6-C_CI_PC.5",
        "family": "C_CI_PC",
        "status": "verified_pending_review",
        "entry_revision": "4061a53a",
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
        "numerical_policy_id": CIPC_NUMERICAL_POLICY,
        "exact_backend": "flint",
        "oracle_precision_bits": 768,
        "native_precision_bits": 256,
        "flint_threads": 1,
        "target_graph_digest": target.reference.graph.graph_digest,
        "target_profile_id": target.reference.profile.complete_profile_id,
        "certificate_ids": [certs[r].certificate_id for r in campaign.EXPECTED],
        "roles": roles,
        "completion": completion,
        "pressure": pressure,
        "cold_checkpoint_validation": cold,
        "final_cost_record_digest": timing["record_digest"],
        "preflight_record_digest": timing["preflight_record_digest"],
        "elapsed_seconds": elapsed,
        "cap_seconds": 3600,
        "profiling_target_seconds": 3600,
        "time_limit_policy": "profiling_only_user_authorized",
        "profiling_target_exceeded": elapsed > 3600,
        "profiling_warnings": [
            "paired current/reset accounting required for cold restore"
        ],
        "peak_rss_mib": rss(),
        "memory_scope": "paired validation process; original progress samples reported separately",
        "checkpoint_validation_repair": {
            "reason": "reset accounting refers to current's child; restore current authority before reset",
            "primary_streams_unchanged": True,
            "initial_elapsed_seconds_upper": initial_seconds,
            "paired_validation_seconds": time.perf_counter() - start,
            "initial_log": log,
            "clock_anchor": anchor,
            "preflight_forecast": estimate,
            "initial_peak_observed_in_progress_mib": max(
                row.get("peak_rss_mib", 0) for row in progress
            ),
            "elapsed_scope": "initial run including rejected isolated reset restore, plus paired validation and controls; no physical prefix repeated",
        },
        "streams": refs,
        "source_bindings": [
            {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
            for p in sorted(paths)
        ],
        "accounting_scope": "process_shared_publication_v1",
        "global_cross_process_uniqueness": False,
        "next_leaf": "P9-9.1a.6-A_OS.1",
    }
    return publish(value)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--fresh", action="store_true")
    g.add_argument("--finish", action="store_true")
    p.add_argument("--initial-log")
    p.add_argument("--clock-anchor")
    a = p.parse_args()
    v = fresh() if a.fresh else finish(a.initial_log, a.clock_anchor)
    print(
        json.dumps({k: v[k] for k in ("status", "elapsed_seconds", "peak_rss_mib")}),
        flush=True,
    )
