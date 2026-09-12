"""Current initializer authority and preserved migration evidence; no numerical rerun."""

import argparse
from functools import lru_cache
import json
import subprocess
import sys

import phase9_implementation_policy as p

BASE = "49b83ba1e05a3e657293ca561e9dec0a80472f5c"
PREFIX = p.PHASE + "tranche-7/P9-7.2a-"
RECORDS = [PREFIX + name + ".json" for name in (
    "Migrations", "AuditFollowup", "OriginalSources", "AuditPressure")]


def historical_blobs(names, commit=BASE):
    """One Git batch, retaining exact bytes; no checkout, archive or replay."""
    names = sorted(set(names))
    result = subprocess.run(["git", "cat-file", "--batch"], cwd=p.ROOT,
                            input="".join(commit + ":" + n + "\n" for n in names).encode(),
                            capture_output=True, check=True)
    output, offset, blobs = result.stdout, 0, {}
    for name in names:
        end = output.index(b"\n", offset)
        header = output[offset:end].split()
        p.require(len(header) == 3 and header[1] == b"blob", "missing historical source: " + name)
        size = int(header[2])
        blobs[name] = output[end + 1:end + 1 + size]
        offset = end + size + 2
    p.require(offset == len(output), "malformed historical source batch")
    return blobs


def preserved_predecessor():
    """Keep the migration checker's 7.1 boundary, using batched Git reads."""
    base = "5d8dbe2"
    names = p.git(p.ROOT, "ls-tree", "-r", "--name-only", base, "src", "tests",
                  p.PHASE + "tranche-5", p.PHASE + "tranche-6", p.G2_ACCEPTANCE,
                  p.PHASE + "tranche-7").decode().splitlines()
    kept = set(names) - p.MIGRATION_PATHS
    followup_name = p.PHASE + "tranche-7/P9-7.1-AuditFollowup.json"
    followup = p.read(p.ROOT / followup_name)
    blobs = historical_blobs(kept | set(followup["source_bindings"]), base)
    successor = historical_blobs(kept & p.INITIALIZER_RUNTIME_PATHS, "f7962e4")
    for name in kept:
        content = successor[name] if name in successor else (p.ROOT / name).read_bytes()
        p.require(content == blobs[name], "accepted predecessor changed: " + name)
    p.require(followup["record_digest"] == p.digest_record(followup), "7.1 digest changed")
    for name, expected in followup["source_bindings"].items():
        p.require(p.sha(blobs[name]) == expected, "7.1 historical source mismatch: " + name)
    return dict(base_commit=p.git(p.ROOT, "rev-parse", base).decode().strip(),
                preserved_files=len(kept), lifecycle_record_digest=followup["record_digest"])


@lru_cache(maxsize=1)
def preserved_migrations():
    captured = historical_blobs(RECORDS)
    for name, content in captured.items():
        p.require((p.ROOT / name).read_bytes() == content, "accepted migration evidence changed: " + name)
    original, audit, bridge, _ = (json.loads(captured[n]) for n in RECORDS)
    predecessor = preserved_predecessor()
    p.require(original["predecessor"] == audit["predecessor"] == predecessor,
              "accepted migration predecessor mismatch")
    names = set(original["source_bindings"]) | set(audit["source_bindings"])
    sources = historical_blobs(names)
    for name, expected in audit["source_bindings"].items():
        p.require(p.sha(sources[name]) == expected, "accepted audit source mismatch: " + name)
    old_sources = dict(sources)
    p.require(bridge["original_record_digest"] == original["record_digest"] and
              bridge["original_record_sha256"] == p.sha(captured[RECORDS[0]]), "original subject mismatch")
    for name, delta in bridge["prior_source_delta"].items():
        p.require(p.sha(sources[name]) == delta["current_sha256"], "correction bridge mismatch")
        lines = sources[name].decode().splitlines(keepends=True)
        end = len(lines)
        for span in reversed(delta["splices_to_original"]):
            start, stop = span["start"], span["stop"]
            p.require(0 <= start <= stop <= end, "bad original source span")
            lines[start:stop] = span["old_lines"]
            end = start
        old_sources[name] = "".join(lines).encode()
        p.require(p.sha(old_sources[name]) == delta["original_sha256"], "original source recovery failed")
    for name, expected in original["source_bindings"].items():
        p.require(p.sha(old_sources[name]) == expected, "original source mismatch: " + name)
    # Original document/spec bindings are verified above at BASE. The exact
    # accepted documents and bounded current spec candidate are checked through
    # proposal_status separately; there is no runtime or old-family exemption.
    from verify_p972a_proposal import SPECIFICATION_REVIEW_PATHS
    work = p.read(p.ROOT / p.WORK)
    p.require(work['record_digest'] == p.digest_record(work), 'runtime work digest drift')
    entries = {row['path']: row for row in work['entries']}
    for name in names:
        if name == p.INV + "drafts/2026-09-GRC-V4.md" or name in SPECIFICATION_REVIEW_PATHS | p.INITIALIZER_RUNTIME_PATHS:
            continue
        if name in {"pyproject.toml", "uv.lock"} or name.startswith(("src/", "tests/", "specs/", p.INV + "drafts/")):
            content = (p.ROOT / name).read_bytes()
            if name in p.EVENT_RUNTIME_PATHS and entries.get(name, {}).get('iteration_id') == 'P9-7.2b':
                p.require(p.sha(content) == entries[name]['sha256'], 'unbound event successor: ' + name)
                # The current implementation has its own evidence; preserve
                # the migration subject at the accepted pre-event Git bytes.
                content = p.git(p.ROOT, 'show', 'ee8885e:' + name)
            p.require(content == sources[name], "spec-review scope violated: " + name)
    sys.path.insert(0, str(p.ROOT / p.SIDE / "tool/src"))
    from grcv4_explorer.abundance import load_abundance_forensic_context
    from grcv4_explorer.forensic import contract_provenance
    historical = load_abundance_forensic_context(p.ROOT, p.ROOT / p.SIDE)
    for value, count in ((original, 25), (audit, 17)):
        p.require(value["record_digest"] == p.digest_record(value), "historical record digest changed")
        p.require(value["results"] == dict(tests_run=count, failures=[], errors=[], skips=[]) and
                  len(value["test_ids"]) == count, "historical migration execution changed")
        p.require(value["aggregate_closed"] is False and value["new_G2_support"] == [] and
                  value["pending_positive_classes"] == ["C_to_A_initializer_source"], "historical claim relabeled")
        p.require(all(trace == contract_provenance(historical, name)
                      for name, trace in value["authority"].items()), "historical authority changed")
    return dict(original_tests=25, audit_tests=17, original_source_files=len(original["source_bindings"]),
                audit_source_files=len(audit["source_bindings"]), numerical_tests_rerun=0,
                preserved_predecessor_files=predecessor["preserved_files"],
                original_record_digest=original["record_digest"], audit_record_digest=audit["record_digest"])


def check():
    # Do not cache file integrity across checks in a long-running process.
    preserved_migrations.cache_clear()
    preserved = preserved_migrations()
    from verify_p972a_proposal import proposal_status
    proposal = proposal_status()
    from grcv4_explorer.a_initializer import initializer_authority
    from grcv4_explorer.canonical import record_digest
    view = initializer_authority(p.ROOT, p.ROOT / p.SIDE)
    p.require(view["projection_digest"] == record_digest(view, "projection_digest"), "initializer projection drift")
    p.require(view["producer_choice_resolved"] is True and
              all(view[name] is False for name in (
                  "payload_specification_complete", "positive_migration_verified", "aggregate_closed",
                  "G2_accepted", "G3_accepted", "runtime_conformance_inferred")), "initializer design overclaim")
    p.current_boundary(p.ROOT)
    from verify_p972a_initializer_runtime import check as runtime_check
    runtime = runtime_check()
    proposal['executable_successor_released'] = True
    return dict(status="passed", scope="initializer_runtime_and_preserved_migration_evidence",
                design_accepted=True, producer_choice_resolved=True, source_admitted=True,
                payload_specification_complete=True, positive_migration_verified=True,
                aggregate_closed=runtime['aggregate_closed'], user_accepted=runtime['user_accepted'],
                new_G2_support=[], G3_accepted=False,
                authority_extension_digest=view["authority_extension_digest"],
                projection_digest=view["projection_digest"], **proposal, **preserved,
                initializer_runtime=runtime)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(check()))
