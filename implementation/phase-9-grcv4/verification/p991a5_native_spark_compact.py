"""Compact C_OS archival evidence with exact independent diagnostic reconstruction.

No native model is advanced. Each compact row retains its original record hash;
reconstructing its derived stage operands must recover that exact archived row.
"""

import argparse
import json
import lzma
import time
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from cos_native_spark_oracle import Equations, infinity, matrix, vector
from flint import ctx
from p991a5_native_spark_campaign import BASE, EXPECTED, FILES, HERE, RECORD, ROOT, seal
from p991a5_native_spark_verify import need, rows

from pygrc.models.grc_v4_codec import canonical_json_bytes

SELF = HERE + "p991a5_native_spark_compact.py"
MANIFEST = BASE + "P9-9.1a.5-Compact.json"
COMPACT = {r: BASE + "P9-9.1a.5-Compact-" + r + ".jsonl.xz" for r in EXPECTED}
SAMPLES = BASE + "P9-9.1a.5-DiagnosticSamples.jsonl.xz"
SELECTED = {r: {1, a - 1, a, a + 1, b} for r, (a, b) in EXPECTED.items()}
SOURCES = {
    SELF,
    HERE + "cos_native_spark_oracle.py",
    HERE + "p991a5_native_spark_verify.py",
}
FORMAT = "native-cos-exact-reconstructible-evidence-v1"


def stream(path, root=ROOT):
    with lzma.open(Path(root) / path, "rt") as source:
        for line in source:
            yield json.loads(line)


def compact_rows(role, root=ROOT):
    return stream(COMPACT[role], root)


def full_samples(role=None, root=ROOT):
    for row in stream(SAMPLES, root):
        if role is None or row["role"] == role:
            yield row["transition"]


class Reconstruction:
    """Literal rational equations, reusing only fixed operators within a read pair."""

    def __init__(self, graph):
        self.eq = Equations(graph)
        self.reference_inverse = (3 * self.eq.I / 4 + self.eq.L).inv()

    def read(self, C, H, inverse, h_inverse):
        e = self.eq
        site = e.M([[(c - 2) ** 3 - (c - 2)] for c in C.entries()])
        phi = e.B * H * e.B.transpose() * C / 64 - site
        baseline = -e.B.transpose() * phi / 1024
        y = inverse * baseline
        return baseline + y / 4, h_inverse * y / 2

    def stage(self, compact):
        e = self.eq
        C, after = vector(compact["before"]), vector(compact["after"])
        jp, fp = self.read(C, e.I, self.reference_inverse, e.I)
        H = e.geometry(fp)
        inverse, h_inverse = (3 * e.I / 4 + H * e.L).inv(), H.inv()
        jc, fc = self.read(C, H, inverse, h_inverse)
        read_pairs = [
            (jp, fp),
            (jc, fc),
            self.read(after, H, inverse, h_inverse),
            self.read(after, e.I, self.reference_inverse, e.I),
        ]
        split = H - e.geometry(fc)
        return dict(
            compact,
            H=rows(H),
            reads=[
                {"J": list(map(str, j.entries())), "f": list(map(str, f.entries()))}
                for j, f in read_pairs
            ],
            split_squared=str(sum(x * x for x in split.entries())),
        )

    def restore(self, compact):
        value = {
            k: v
            for k, v in compact.items()
            if k
            not in (
                "record_digest",
                "previous_record_digest",
                "original_record_digest",
                "original_previous_record_digest",
            )
        }
        value["stage"] = self.stage(compact["stage"])
        value["previous_record_digest"] = compact["original_previous_record_digest"]
        value = seal(value)
        need(
            value["record_digest"] == compact["original_record_digest"],
            "reconstructed diagnostics differ from original record",
        )
        return value


def project(original):
    value = {
        k: deepcopy(v)
        for k, v in original.items()
        if k not in ("record_digest", "previous_record_digest", "stage")
    }
    value["stage"] = {k: original["stage"][k] for k in ("before", "after", "flux")}
    value["original_record_digest"] = original["record_digest"]
    value["original_previous_record_digest"] = original["previous_record_digest"]
    return value


class Writer:
    def __init__(self, path):
        self.path, self.count, self.last = path, 0, None
        self.file = lzma.open(ROOT / path, "wb", preset=6)  # noqa: SIM115

    def write(self, row):
        row = seal(dict(row, previous_record_digest=self.last))
        self.file.write(canonical_json_bytes(row) + b"\n")
        self.count += 1
        self.last = row["record_digest"]
        return row

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


def original_record(root=ROOT):
    value = json.loads((Path(root) / RECORD).read_bytes())
    need(value == seal(value), "original campaign seal")
    return value


def build():
    ctx.threads = 1
    need(
        not any((ROOT / p).exists() for p in [MANIFEST, SAMPLES, *COMPACT.values()]),
        "refuse compact evidence overwrite",
    )
    original = original_record()
    inputs = next(stream(FILES["inputs"]))
    reconstruction = Reconstruction(
        inputs["target_configuration"]["reference"]["graph"]
    )
    start = time.perf_counter()
    samples = Writer(SAMPLES)
    refs, total = [], 0
    try:
        for role in EXPECTED:
            old = next(r for r in original["streams"] if r["path"] == FILES[role])
            raw = (ROOT / old["path"]).read_bytes()
            need(
                len(raw) == old["compressed_bytes"]
                and sha256(raw).hexdigest() == old["sha256"],
                "original archive changed",
            )
            writer = Writer(COMPACT[role])
            before, previous = inputs["initial_roles"][role]["C"], None
            expanded = sha256()
            expanded_size = 0
            try:
                for full in stream(FILES[role]):
                    need(
                        full == seal(full)
                        and full["previous_record_digest"] == previous,
                        "original trace chain",
                    )
                    need(
                        full["beat"] == writer.count + 1
                        and full["stage"]["before"] == before,
                        "original trajectory sequence",
                    )
                    row = writer.write(project(full))
                    rebuilt = reconstruction.restore(row)
                    need(rebuilt == full, "complete original row reconstruction")
                    data = canonical_json_bytes(rebuilt) + b"\n"
                    expanded.update(data)
                    expanded_size += len(data)
                    if full["beat"] in SELECTED[role]:
                        samples.write({"role": role, "transition": full})
                    before, previous = full["stage"]["after"], full["record_digest"]
                    total += 1
                    if writer.count % 50 == 0:
                        print(
                            json.dumps(
                                {
                                    "role": role,
                                    "exact_rows": writer.count,
                                    "seconds": time.perf_counter() - start,
                                }
                            ),
                            flush=True,
                        )
            finally:
                writer.close()
            need(
                writer.count == old["records"]
                and previous == old["last_record_digest"],
                "complete original stream",
            )
            ref = writer.reference()
            ref.update(
                original_stream=old,
                expanded_sha256=expanded.hexdigest(),
                expanded_bytes=expanded_size,
            )
            refs.append(ref)
    finally:
        samples.close()
    need(total == 753 and samples.count == 10, "complete evidence roster")
    value = seal(
        {
            "schema": FORMAT,
            "status": "verified_pending_review",
            "family": "C_OS",
            "original_campaign_digest": original["record_digest"],
            "original_campaign_sha256": sha256(
                (ROOT / RECORD).read_bytes()
            ).hexdigest(),
            "streams": refs,
            "diagnostic_samples": samples.reference(),
            "exact_reconstructed_transitions": total,
            "complete_diagnostic_samples": 10,
            "original_expanded_rows_reconstructed": True,
            "numerical_steps_executed": 0,
            "runtime_changed": False,
            "history_rewritten": False,
            "elapsed_seconds": time.perf_counter() - start,
            "source_bindings": [
                {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
                for p in sorted(SOURCES)
            ],
            "endpoints": {r: list(e) for r, e in EXPECTED.items()},
        }
    )
    (ROOT / MANIFEST).write_text(json.dumps(value, indent=2) + "\n")
    print(
        json.dumps(
            {
                "result": "COS_COMPACT_PASS",
                "seconds": value["elapsed_seconds"],
                "evidence_bytes": sum(r["compressed_bytes"] for r in refs)
                + value["diagnostic_samples"]["compressed_bytes"],
            }
        ),
        flush=True,
    )
    return value


def checked_manifest(root=ROOT):
    root = Path(root)
    value = json.loads((root / MANIFEST).read_bytes())
    need(value == seal(value) and value["schema"] == FORMAT, "compact manifest seal")
    original = original_record(root)
    need(
        value["original_campaign_digest"] == original["record_digest"]
        and value["original_campaign_sha256"]
        == sha256((root / RECORD).read_bytes()).hexdigest(),
        "compact original summary binding",
    )
    need(
        value["exact_reconstructed_transitions"] == 753
        and value["complete_diagnostic_samples"] == 10
        and value["original_expanded_rows_reconstructed"] is True
        and value["numerical_steps_executed"] == 0
        and value["runtime_changed"] is False
        and value["history_rewritten"] is False
        and value["endpoints"] == {r: list(e) for r, e in EXPECTED.items()},
        "compact scope",
    )
    need(
        {r["path"] for r in value["source_bindings"]} == SOURCES
        and len(value["source_bindings"]) == len(SOURCES),
        "compact source roster",
    )
    need(
        [r["path"] for r in value["streams"]] == list(COMPACT.values())
        and value["diagnostic_samples"]["path"] == SAMPLES,
        "compact stream roster",
    )
    for ref in [
        *value["source_bindings"],
        *value["streams"],
        value["diagnostic_samples"],
    ]:
        raw = (root / ref["path"]).read_bytes()
        need(
            sha256(raw).hexdigest() == ref["sha256"],
            "changed compact source/evidence: " + ref["path"],
        )
        if "compressed_bytes" in ref:
            need(
                len(raw) == ref["compressed_bytes"] < 10_000_000,
                "compact evidence size",
            )
    for role, ref in zip(EXPECTED, value["streams"], strict=True):
        need(
            ref["original_stream"]
            == next(r for r in original["streams"] if r["path"] == FILES[role]),
            "original stream identity",
        )
    return value


def check(root=ROOT, numerical=False):
    root = Path(root)
    value = checked_manifest(root)
    original = original_record(root)
    inputs = next(stream(FILES["inputs"], root))
    graph = inputs["target_configuration"]["reference"]["graph"]
    reconstruction = Reconstruction(graph)
    sample_hashes = {}
    for index, (role, ref) in enumerate(zip(EXPECTED, value["streams"], strict=True)):
        before = inputs["initial_roles"][role]["C"]
        previous, original_previous, count, entry, gains, window = (
            None,
            None,
            0,
            None,
            0,
            [],
        )
        cert = inputs["certificates"][index]
        U, center = matrix(cert["operands"]["U"]), vector(cert["operands"]["center"])
        expanded, expanded_size = sha256(), 0
        for row in compact_rows(role, root):
            count += 1
            need(
                row == seal(row)
                and row["previous_record_digest"] == previous
                and row["original_previous_record_digest"] == original_previous
                and row["beat"] == count
                and row["stage"]["before"] == before,
                "compact trajectory chain",
            )
            stage = row["stage"]
            need(
                set(stage) == {"before", "after", "flux"},
                "compact retained stage fields",
            )
            C, after, flux = (
                vector(before),
                vector(stage["after"]),
                vector(stage["flux"]),
            )
            need(
                sum(C.entries()) == sum(after.entries()) == 21
                and after == C - 32 * reconstruction.eq.B * flux,
                "compact exact charge/incidence",
            )
            norm = infinity(U * (after - center))
            need(
                row["membership"]["norm"] == str(norm)
                and row["membership"]["inside"] == (norm <= 1),
                "compact exact membership",
            )
            if norm <= 1:
                entry = entry or count
                window.append(count)
            else:
                window = []
            gains += row["local_gain"]
            need(
                row["native_window_observations"]
                == (len(window) if role == "current" else 0),
                "compact native window",
            )
            if numerical:
                raw = canonical_json_bytes(reconstruction.restore(row)) + b"\n"
                expanded.update(raw)
                expanded_size += len(raw)
            if count in SELECTED[role]:
                sample_hashes[(role, count)] = row["original_record_digest"]
            previous, original_previous, before = (
                row["record_digest"],
                row["original_record_digest"],
                stage["after"],
            )
        end = original["roles"][role]
        need(
            count == ref["records"]
            and previous == ref["last_record_digest"]
            and original_previous == ref["original_stream"]["last_record_digest"],
            "compact full chain",
        )
        need(
            (entry, count) == EXPECTED[role]
            and end["window"] == window
            and end["entry"] == entry
            and end["completion"] == count
            and gains == end["local_gain"] == int(role == "current"),
            "compact endpoints/gain",
        )
        if numerical:
            need(
                expanded.hexdigest() == ref["expanded_sha256"]
                and expanded_size == ref["expanded_bytes"],
                "complete expanded original trace",
            )
    ref = value["diagnostic_samples"]
    previous, seen = None, set()
    for row in stream(SAMPLES, root):
        full = row["transition"]
        key = (row["role"], full["beat"])
        need(
            row == seal(row)
            and row["previous_record_digest"] == previous
            and full == seal(full)
            and key not in seen
            and full["record_digest"] == sample_hashes[key],
            "diagnostic sample provenance",
        )
        seen.add(key)
        previous = row["record_digest"]
    need(
        seen == set(sample_hashes)
        and len(seen) == ref["records"] == 10
        and previous == ref["last_record_digest"],
        "complete diagnostic samples",
    )
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--numerical", action="store_true")
    args = parser.parse_args()
    result = build() if args.build else check(numerical=args.numerical)
    print(result["record_digest"])
