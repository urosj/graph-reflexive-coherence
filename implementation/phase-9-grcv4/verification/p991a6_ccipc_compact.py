"""Publish and verify compact audit evidence, without running physical steps."""

import argparse
import json
import lzma
import shutil
import tempfile
import time
from hashlib import sha256
from pathlib import Path

import p991a6_ccipc_campaign as campaign
from ccipc_compact_evidence import Evidence
from flint import ctx
from flint import fmpq as Q
from p991a5_native_spark_campaign import Stream
from p991a5_native_spark_verify import need

ROOT = campaign.ROOT
SELF = campaign.HERE + "p991a6_ccipc_compact.py"
SAMPLES = campaign.BASE + "P9-9.1a.6-CCIPC.5-DiagnosticSamples.jsonl.xz"
FORMAT = "compact_native_ccipc_witness_v1"
SELECTED = {"current": {1, 373, 374, 375, 376}, "reset": {1, 374, 375, 376, 377}}


def read_stream(name, root=ROOT):
    path = SAMPLES if name == "samples" else campaign.FILES[name]
    with lzma.open(Path(root) / path, "rt") as stream:
        for line in stream:
            yield json.loads(line)


def context(root=ROOT):
    return Evidence(next(read_stream("inputs", root)))


def full_samples(role=None, root=ROOT):
    for row in read_stream("samples", root):
        if role is None or row["role"] == role:
            yield row["transition"]


def check(root=ROOT, numerical=False):
    root = Path(root)
    with lzma.open(root / campaign.RECORD, "rt") as f:
        value = json.load(f)
    need(value == campaign.seal(value), "sealed compact campaign")
    storage = value["storage"]
    need(
        storage["format"] == FORMAT and storage["all_exact_states_preserved"] is True,
        "compact evidence format",
    )
    for ref in [*value["source_bindings"], *value["streams"]]:
        need(
            sha256((root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
            "changed compact source/evidence: " + ref["path"],
        )
    original = {k: v for k, v in value.items() if k != "storage"}
    original.update(
        streams=storage["original_streams"],
        source_bindings=storage["original_source_bindings"],
        record_digest=storage["original_record_digest"],
    )
    need(original == campaign.seal(original), "original execution summary provenance")
    e = context(root)
    need(
        storage["carrier_pairs"] == [list(p) for p in e.pairs]
        and storage["root_domain"] == e.domain,
        "complete shared mathematical declaration",
    )
    expected_digests = {}
    seen_samples = set()
    for name in (*campaign.FILES, "samples"):
        path = SAMPLES if name == "samples" else campaign.FILES[name]
        ref = next(x for x in value["streams"] if x["path"] == path)
        previous = None
        count = 0
        original_previous = None
        if name in campaign.EXPECTED:
            before = e.initial(name)
            entry = None
            window = []
            gains = 0
        for row in read_stream(name, root):
            count += 1
            need(
                row == campaign.seal(row) and row["previous_record_digest"] == previous,
                "compact stream chain",
            )
            previous = row["record_digest"]
            if name in campaign.EXPECTED:
                need(
                    row["beat"] == count
                    and row["original_previous_record_digest"] == original_previous,
                    "ordered exact trajectory",
                )
                original_previous = row["original_record_digest"]
                before, report = e.verify(before, row, name, numerical=numerical)
                if numerical:
                    need(
                        report == row["independent_compact_audit"],
                        "retained compact audit differs",
                    )
                need(
                    Q(row["independent_compact_audit"]["full_step_error_upper"])
                    <= Q(e.certs[name].proof["full_step_error"]),
                    "retained error budget",
                )
                if row["membership"]["inside"]:
                    entry = entry or count
                    window.append(count)
                else:
                    window = []
                gains += row["local_gain"]
                need(
                    row["native_window_observations"]
                    == (len(window) if name == "current" else 0),
                    "native completion window",
                )
                if count in SELECTED[name]:
                    expected_digests[(name, count)] = row["original_record_digest"]
            elif name == "samples":
                full = row["transition"]
                key = (row["role"], full["beat"])
                need(
                    key in expected_digests
                    and key not in seen_samples
                    and full == campaign.seal(full)
                    and full["record_digest"] == expected_digests[key],
                    "complete diagnostic sample provenance",
                )
                seen_samples.add(key)
        need(
            count == ref["records"] and previous == ref["last_record_digest"],
            "complete compact stream",
        )
        if name in campaign.EXPECTED:
            role = value["roles"][name]
            need(
                (entry, count) == campaign.EXPECTED[name]
                and role["entry"] == entry
                and role["completion"] == count
                and role["local_gain"] == gains == (1 if name == "current" else 0)
                and role["window"] == window,
                "actual endpoint and once-only gains",
            )
            orig = next(x for x in storage["original_streams"] if x["path"] == path)
            need(
                original_previous == orig["last_record_digest"],
                "original trajectory provenance",
            )
    need(
        seen_samples == set(expected_digests) and len(seen_samples) == 10,
        "ten complete boundary diagnostics",
    )
    need(
        value["native_endpoint_verified"] is True
        and value["native_completion_support"] is False
        and value["full_trajectory_runs"] == 2
        and value["physical_supporting_tail_steps"] == 0,
        "unchanged campaign scope",
    )
    return value


def run():
    ctx.threads = 1
    # The full streams and original verifier are used only before projection.
    original = campaign.check(ROOT)
    need("storage" not in original, "compact evidence already published")
    e = context()
    start = time.perf_counter()
    backup = Path(tempfile.mkdtemp(prefix="grcv4-ccipc-full-evidence-"))
    for name in (campaign.RECORD, campaign.FILES["current"], campaign.FILES["reset"]):
        shutil.copy2(ROOT / name, backup / Path(name).name)
    refs = {}
    count = 0
    with tempfile.TemporaryDirectory(
        prefix=".ccipc-compact-", dir=ROOT / campaign.BASE
    ) as tmp:
        samples = Stream(str(Path(tmp) / "samples.jsonl.xz"))
        try:
            for role in campaign.EXPECTED:
                stream = Stream(str(Path(tmp) / (role + ".jsonl.xz")))
                before = e.initial(role)
                try:
                    for full in read_stream(role):
                        need(
                            full == campaign.seal(full)
                            and before.to_payload() == full["stage"]["before"],
                            "original actual input and trace integrity",
                        )
                        row = e.project(full)
                        before, report = e.verify(before, row, role)
                        row["independent_compact_audit"] = report
                        stream.write(row)
                        count += 1
                        if row["beat"] in SELECTED[role]:
                            samples.write({"role": role, "transition": full})
                        if row["beat"] % 100 == 0:
                            print(
                                json.dumps(
                                    {
                                        "compact_verified": role,
                                        "beat": row["beat"],
                                        "seconds": time.perf_counter() - start,
                                    }
                                ),
                                flush=True,
                            )
                finally:
                    stream.close()
                refs[role] = dict(stream.reference(), path=campaign.FILES[role])
        finally:
            samples.close()
        refs["samples"] = dict(samples.reference(), path=SAMPLES)
        need(count == 753, "every exact target transition independently checked")
        value = dict(original)
        value["streams"] = [
            refs.get(name, ref)
            for name in campaign.FILES
            for ref in original["streams"]
            if ref["path"] == campaign.FILES[name]
        ] + [refs["samples"]]
        paths = {r["path"] for r in original["source_bindings"]} | {
            SELF,
            campaign.HERE + "ccipc_compact_evidence.py",
            campaign.HERE + "test_p991a6_ccipc_compact.py",
        }
        value["source_bindings"] = [
            {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
            for p in sorted(paths)
        ]
        value["storage"] = {
            "format": FORMAT,
            "all_exact_states_preserved": True,
            "independently_verified_transitions": count,
            "complete_diagnostic_samples": 10,
            "carrier_pairs": [list(p) for p in e.pairs],
            "root_domain": e.domain,
            "original_record_digest": original["record_digest"],
            "original_streams": original["streams"],
            "original_source_bindings": original["source_bindings"],
            "original_compressed_bytes": sum(
                x["compressed_bytes"] for x in original["streams"]
            ),
            "retained_compressed_bytes": sum(
                x["compressed_bytes"] for x in value["streams"]
            ),
            "independent_storage_audit_seconds": time.perf_counter() - start,
            "omitted": "per-beat expanded H/J/flat/S arrays, writer ideal/source matrices, duplicate before states/graphs and derivable full classification rows",
            "retained": "exact signed C/Z, proposal/residual/Banach witnesses for both roots, current and writer midpoints, exact flux, uniform-error checks, staging/receipt provenance, full boundary samples and checkpoints",
        }
        pending = Path(tmp) / "campaign.json.xz"
        pending.write_bytes(lzma.compress(canonical(value), preset=3))
        for name in ("current", "reset"):
            (Path(tmp) / (name + ".jsonl.xz")).replace(ROOT / campaign.FILES[name])
        (Path(tmp) / "samples.jsonl.xz").replace(ROOT / SAMPLES)
        pending.replace(ROOT / campaign.RECORD)
    result = check(ROOT)
    print(
        json.dumps(
            {
                "compact_evidence_pass": count,
                "original_mib": result["storage"]["original_compressed_bytes"] / 2**20,
                "retained_mib": result["storage"]["retained_compressed_bytes"] / 2**20,
                "temporary_originals": str(backup),
            }
        ),
        flush=True,
    )
    return result


def canonical(value):
    from pygrc.models.grc_v4_codec import canonical_json_bytes

    return canonical_json_bytes(campaign.seal(value))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", action="store_true")
    p.add_argument("--numerical", action="store_true")
    a = p.parse_args()
    run() if a.run else check(numerical=a.numerical)
