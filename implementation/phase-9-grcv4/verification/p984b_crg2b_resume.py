"""Resume the interrupted C_RG2b campaign without changing its frozen owner."""

import argparse
import fcntl
import hashlib
import json
import os
import platform
import tempfile
from importlib.metadata import version
from pathlib import Path

import p984b_crg2b_runtime as r

b = r.b
SELF = b.HERE + "p984b_crg2b_resume.py"
TEST = b.HERE + "test_p984b_crg2b_recovery.py"
ARCHIVE = b.BASE + "P9-8.4b-CRG2bInterrupted.jsonl"
JOURNAL_SHA = "e9690eba9beebd5eeb4eeff730954f93473b591e1a94df12b814ae05f0929ec5"


def publish(path, value):
    """Publish a complete record atomically, refusing existing evidence."""
    path = Path(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as out:
        temporary = Path(out.name)
        out.write(b.canonical_json_bytes(value) + b"\n")
        out.flush()
        os.fsync(out.fileno())
    try:
        os.link(temporary, path)
    finally:
        temporary.unlink()


def decode_journal(raw, manifest):
    lines = raw.splitlines(keepends=True)
    b.require(lines and all(x.endswith(b"\n") for x in lines), "partial journal entry")
    records = [json.loads(x) for x in lines]
    for record in records:
        b.check_digest(record)
    header = records[0]
    b.require(
        header["manifest_digest"] == manifest["record_digest"]
        and header["cases"] == []
        and header["native_runtime_executed"] is True
        and header["user_accepted"] is False
        and header["aggregate_closed"] is False,
        "journal header drift",
    )
    rows = [
        {k: v for k, v in row.items() if k != "record_digest"} for row in records[1:]
    ]
    b.require(len(rows) <= len(manifest["cases"]), "foreign journal cases")
    for case, row in zip(manifest["cases"], rows):
        b.require(
            row["case_id"] == case["case_id"]
            and row["input_digest"] == b.digest(case)
            and row["case_passed"] is True
            and row["first_failure"] is None,
            "journal prefix order/input/failure drift",
        )
    return header, rows


def validate_prefix(manifest, header, rows):
    subset = b.seal({**manifest, "cases": manifest["cases"][: len(rows)]})
    value = b.seal(
        {**header, "manifest_digest": subset["record_digest"], "cases": rows}
    )
    report = r.validate(subset, value)
    b.require(report["cases_passed"] == len(rows), "incomplete retained prefix")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-prefix", action="store_true")
    args = parser.parse_args()
    manifest = b.read(r.INPUTS)
    r.check_manifest(manifest)
    b.require(
        not (b.ROOT / r.RESULTS).exists(), "refusing to overwrite native evidence"
    )
    journal = b.ROOT / (r.RESULTS + ".progress.jsonl")
    with journal.open("r+b") as progress:
        fcntl.flock(progress, fcntl.LOCK_EX | fcntl.LOCK_NB)
        raw = progress.read()
        archive = b.ROOT / ARCHIVE
        original = archive.read_bytes() if archive.exists() else raw
        b.require(
            hashlib.sha256(original).hexdigest() == JOURNAL_SHA,
            "interrupted prefix drift",
        )
        b.require(raw.startswith(original), "interrupted prefix was replaced")
        header, rows = decode_journal(raw, manifest)
        old_header, old_rows = decode_journal(original, manifest)
        b.require(
            len(old_rows) == 14 and header == old_header, "recovery subject drift"
        )
        report = validate_prefix(manifest, header, rows)
        print("CRG2b_RETAINED_PREFIX_PASS", len(rows), flush=True)
        if args.check_prefix:
            print(json.dumps(report, indent=2))
            return
        if not archive.exists():
            with archive.open("xb") as out:
                out.write(original)
                out.flush()
                os.fsync(out.fileno())
        recovery = {
            "reason": "user_requested_interruption",
            "interrupted_journal": ARCHIVE,
            "interrupted_journal_sha256": JOURNAL_SHA,
            "retained_case_digests": {
                row["case_id"]: b.digest(row) for row in old_rows
            },
            "resumed_case_ids": [case["case_id"] for case in manifest["cases"][14:]],
            "source_bindings": b.bind([SELF, TEST, ARCHIVE]),
            "resumed_environment": {
                "python": platform.python_version(),
                "numpy": version("numpy"),
                "mpmath": version("mpmath"),
                "python_flint": version("python-flint"),
            },
        }
        with b.exact_backend(b.ExactBackend.FLINT):
            seed = r.state(header["shared"]["actual_source"])
            progress.seek(0, os.SEEK_END)
            for case in manifest["cases"][len(rows) :]:
                row = r.execute_case(seed, case)
                progress.write(b.canonical_json_bytes(b.seal(row)) + b"\n")
                progress.flush()
                os.fsync(progress.fileno())
                rows.append(row)
                print(
                    case["fixture_id"], row["outcome"], row["first_failure"], flush=True
                )
                b.require(
                    row["case_passed"],
                    "failed case retained; explicit recovery required",
                )
        r.check_manifest(manifest)
        result = b.seal({**header, "cases": rows, "execution_recovery": recovery})
        report = r.validate(manifest, result)
        b.require(report["cases_passed"] == 16, "full campaign incomplete")
        publish(b.ROOT / r.RESULTS, result)
    journal.unlink()
    print(json.dumps({**report, "prior_native_cases_repeated": False}, indent=2))


if __name__ == "__main__":
    main()
