"""Exact historical G2 input reconstruction after accepted Tranche 8 changes.

This is a provenance bridge, NOT proof that old executions certify new code.
Only enumerated before/after hashes qualify; fresh executions keep live hashes.
"""

import phase9_implementation_policy as p
from functools import lru_cache
import importlib

RECORD = p.PHASE + "tranche-8/P9-8-SideToolSourceBridge.json"
EXPECTED_DIGEST = "f9c4450eccc148b0c7680c12f962952c1d7543578d2756009e9328728a6587f8"


def record():
    value = p.read(p.ROOT / RECORD)
    p.require(value["record_digest"] == p.digest_record(value) == EXPECTED_DIGEST,
              "Tranche 8 source bridge drift")
    for commit in (value["base_commit"], value["accepted_checkpoint"]):
        p.git(p.ROOT, "merge-base", "--is-ancestor", commit, "HEAD")
    return value


def retained_bindings(current):
    value = record()
    result = dict(current)
    for name, expected in value["additions"].items():
        if name in result:
            p.require(result[name] == expected == p.sha(p.safe_path(p.ROOT, name).read_bytes()),
                      "unreviewed historical-roster addition: " + name)
            del result[name]
    for name, row in value["changes"].items():
        if name not in result:
            continue
        p.require(p.sha(p.safe_path(p.ROOT, name).read_bytes()) == row["after_sha256"],
                  "unreviewed change after Tranche 8 source bridge: " + name)
        p.require(p.sha(p.git(p.ROOT, "show", value["base_commit"] + ":" + name)) == row["before_sha256"],
                  "unrecoverable historical G2 input: " + name)
        p.require(result[name] in (row["before_sha256"], row["after_sha256"]),
                  "unrelated identity cannot use Tranche 8 bridge: " + name)
        result[name] = row["before_sha256"]
    return result


@lru_cache(maxsize=2048)
def historical_hash(root, revision, name):
    # Only immutable Git objects are cached. Live files and decisions are reread.
    return p.sha(p.git(root, "show", revision + ":" + name))


STAGES = ("c_rg2b_g2_source_reuse", "a_rg2b_g2_source_reuse",
          "c_ci_pc_g2_source_reuse", "a_ci_pc_g2_source_reuse",
          "c_pc_g2_source_reuse", "a_pc_g2_source_reuse",
          "c_ci_g2_source_reuse", "g2_source_reuse", "a_os_g2_source_reuse")


def projections(current):
    """Compose the existing finite tables once, newest to oldest.

    Equivalent to the old recursive projection: each stage requires live bytes
    projected by every successor, and an exact before/after input. This avoids
    repeatedly traversing the whole chain for every path and every comparison.
    """
    result = retained_bindings(current)
    live = retained_bindings({n: p.sha(p.safe_path(p.ROOT, n).read_bytes()) for n in result})
    yield "tranche8", dict(result)
    for stage in STAGES:
        module = importlib.import_module(stage)
        value = p.read(p.ROOT / module.RECORD)
        p.require(value["record_digest"] == p.digest_record(value) == module.EXPECTED_DIGEST
                  and value["base_commit"] == module.BASE, "historical source bridge drift: " + stage)
        p.git(p.ROOT, "merge-base", "--is-ancestor", module.BASE, "HEAD")
        for name, row in value["changes"].items():
            if name not in result:
                continue
            p.require(live[name] == row["after_sha256"], "unreviewed source after " + stage + ": " + name)
            p.require(historical_hash(p.ROOT, module.BASE, name) == row["before_sha256"],
                      "unrecoverable historical input: " + name)
            p.require(result[name] in (row["before_sha256"], row["after_sha256"]),
                      "unrelated historical source identity: " + name)
            result[name] = live[name] = row["before_sha256"]
        yield stage, dict(result)


def through(current, stop):
    for stage, value in projections(current):
        if stage == stop:
            return value
    raise ValueError("unknown source bridge stage")
