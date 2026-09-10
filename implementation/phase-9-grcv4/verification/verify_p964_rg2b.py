#!/usr/bin/env python3
"""One bounded RG2b a/b campaign and source check; no conformance promotion."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import io
import json
import platform
import time
import unittest

import phase9_implementation_policy as p
import verify_p961_ci as ci
import verify_p962_pc as pc
import verify_p963_cipc as cipc

ROOT = p.ROOT
BASE = "ba45482"
SCRIPT = p.HERE + "verify_p964_rg2b.py"
REVIEW = p.PHASE + "tranche-6/P9-6.4ab-Review.md"
RECORD = p.PHASE + "tranche-6/P9-6.4ab-ExecutionRecord.json"
TESTS = ["tests.models.test_grc_v4_rg2b"]
REGRESSIONS = [
    "tests.models.test_grc_v4_candidate_a",
    "tests.models.test_grc_v4_cipc.CandidateACIPCTests",
]
CONTRACTS = (
    "D10.2-EC-PARENT-REAL-RG2B",
    "D10.2-EC-RG-INVARIANCE",
    "D10.2-EC-RG-LIPSCHITZ-CONTRACTION",
    "D10.2-EC-RG-DETERMINISM",
    "D10.2-EC-RG-CLAIM-CEILING",
)
RUNTIME = {
    "src/pygrc/models/grc_v4_rg2b.py",
    "src/pygrc/models/grc_v4_candidate_a.py",
    "tests/models/test_grc_v4_rg2b.py",
}


def sources():
    names = {
        SCRIPT,
        REVIEW,
        cipc.SCRIPT,
        p.INV
        + "decisions/GeometryTemporalRealizationSuccessorReconstructedGeometry.md",
        p.INV
        + "decisions/GeometryTemporalRealizationSuccessorReconstructedGeometry.json",
    }
    return {
        **ci.sources(),
        **{n: p.sha((ROOT / n).read_bytes()) for n in sorted(names)},
    }


def source_contracts():
    import sys

    sys.path.insert(0, str(ROOT / p.SIDE / "tool/src"))
    from grcv4_explorer.abundance import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance

    context = load_current_forensic_context(ROOT, ROOT / p.SIDE)
    rows = []
    for name in CONTRACTS:
        trace = contract_provenance(context, name)
        p.require(trace["row_count"] == 1, "missing RG2b source contract")
        row = trace["rows"][0]
        p.require(
            row["classification"] == "source_exact_contract_provenance",
            "changed RG2b contract authority",
        )
        contract = row["payload"]["contract"]
        rows.append(
            dict(
                contract_id=name,
                classification=row["classification"],
                source_record_id=contract["source_record_id"],
                source_json_pointer=contract["source_json_pointer"],
                trace_digest=p.sha(p.canonical(trace)),
                blocked_overread=contract["attributes"]["blocked_overread"],
            )
        )
    return rows


def fixtures():
    from tests.models.test_grc_v4_rg2b import strong_fixture

    rows = []
    for candidate in ("C", "A"):
        inputs, _ = strong_fixture(candidate)
        profile = inputs.geometry.reference.profile
        rows.append(
            dict(
                candidate=candidate,
                construction=dict(
                    module=TESTS[0], function="strong_fixture", argument=candidate
                ),
                profile_identity=profile.identity_payload.to_payload(),
                state=dict(
                    C=list(inputs.current.C),
                    W_A=(
                        list(inputs.current.W_A)
                        if inputs.current.W_A is not None
                        else None
                    ),
                    Z_4=None,
                ),
                realization=profile.params_resolved.realization.to_payload(),
                expected="Nonzero-coupling section differs from CI beyond combined error; native one-current/one-continuity/ordered-A-writer beat meets the independently derived invariance error bound.",
            )
        )
    return rows


def capture():
    p.require(not (ROOT / RECORD).exists(), "preserve the retained RG2b run")
    before, contracts, concrete = sources(), source_contracts(), fixtures()
    results = {}
    for key, names, count in (
        ("rg2b", TESTS, 29),
        ("affected_A_regressions", REGRESSIONS, 52),
    ):
        tests, ids = pc.suite(names)
        p.require(len(ids) == count, "changed RG2b campaign roster")
        stream = io.StringIO()
        started, clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
        run = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
        elapsed = round(time.monotonic() - clock, 3)
        print(stream.getvalue(), end="", flush=True)
        p.require(
            run.wasSuccessful()
            and run.testsRun == count
            and not run.skipped
            and not run.expectedFailures,
            "RG2b campaign failed",
        )
        p.require(sources() == before, "source drift during RG2b execution")
        results[key] = dict(
            started_utc=started,
            completed_utc=datetime.now(timezone.utc).isoformat(),
            elapsed_seconds=elapsed,
            tests_run=count,
            failures=0,
            errors=0,
            skips=0,
            executed_ids=ids,
            output_sha256=p.sha(stream.getvalue().encode()),
            command=[".venv/bin/python", "-m", "unittest", "-v", *names],
        )
    record = dict(
        schema="phase9_controlled_batch_execution_v1",
        iteration_ids=["P9-6.4a", "P9-6.4b"],
        status="implemented_verified_pending_independent_review",
        authority="User requested P9-6.4a/b after accepting and committing P9-6.3a/b/c. Shared c review, user acceptance and commit remain separate.",
        source_git_base=p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
        release_id=p.current_abundance_release(ROOT),
        command=[".venv/bin/python", SCRIPT, "--capture"],
        environment=dict(
            python=platform.python_version(),
            platform=platform.platform(),
            dependencies={
                n: importlib.metadata.version(n)
                for n in ("numpy", "jsonschema", "rfc8785")
            },
        ),
        source_bindings=before,
        source_contracts=contracts,
        concrete_fixtures=concrete,
        results=results,
        children={
            leaf: dict(
                profile=profile,
                implementation_result="passed",
                independent_review="pending",
                user_accepted=False,
            )
            for leaf, profile in (("P9-6.4a", "C_RG2b"), ("P9-6.4b", "A_RG2b"))
        },
        P9_6_4c="pending_unexecuted",
        user_accepted=False,
        RG2b_G2_accepted=False,
        G3_accepted=False,
        accepted_generic_runtime_support=[],
        admitted_specialization_support_sets=[],
        implementation_limits=[
            "Two vertices, one non-loop edge, unit vertex measure; no general-graph evaluator.",
            "Frozen positive ordinary-beat duration and context; strict A floor/C selector/whole-chart admission.",
            "Lipschitz section only; no classical section derivative or spectrum.",
            "No live lifecycle, formation authentication, topology/context events, endpoint or G2/G3.",
        ],
        predecessor_evidence=dict(
            accepted_composition=BASE,
            records_preserved=True,
            scope="Historical subjects only. The 52 selected A consumers are freshly rerun; no historical result is relabeled as current execution.",
        ),
        reconstruction="Provision root .venv from uv.lock and use PYTHONPATH=src:. with the recorded commands from repository root. Fixture functions and source bindings reconstruct complete profiles and pressure. --check verifies records/current sources/accepted Git subjects without rerunning scientific tests. No external files or source archive. Timings/output hashes are observations, not reproduction promises.",
        claim_ceiling="Provisional finite, completion-relative A_RG2b and C_RG2b scalar-graph evaluators with computed global-extension inverse, value/Lipschitz/contraction/containment bounds and finite approximation error. Wider graph support, c reconciliation, lifecycle and acceptance remain separate.",
    )
    record["record_digest"] = p.digest_record(record)
    (ROOT / RECORD).write_text(json.dumps(record, indent=2) + "\n")


def historical_sources(value, follow, successor=None):
    """Recover the original uncommitted subject from minimal reverse spans."""
    current = {}
    deltas = ([successor["prior_source_delta"]] if successor else []) + [
        follow["prior_source_delta"]
    ]
    for name in value["source_bindings"]:
        raw = (ROOT / name).read_bytes()
        for delta in deltas:
            if name not in delta:
                continue
            entry = delta[name]
            p.require(
                p.sha(raw) == entry["current_sha256"], "changed corrected RG2b source"
            )
            lines = raw.decode().splitlines(keepends=True)
            end = len(lines)
            for span in reversed(entry["splices_to_original"]):
                start, stop = span["start"], span["stop"]
                p.require(0 <= start <= stop <= end, "invalid RG2b original span")
                lines[start:stop] = span["old_lines"]
                end = start
            raw = "".join(lines).encode()
        current[name] = p.sha(raw)
    return current


def check():
    value = p.read(ROOT / RECORD)
    p.require(value["record_digest"] == p.digest_record(value), "changed RG2b record")
    follow = p.read(ROOT / (p.PHASE + "tranche-6/P9-6.4c-ExecutionRecord.json"))
    successor_path = ROOT / (p.PHASE + "tranche-6/P9-6.4d-AuditFollowup.json")
    successor = p.read(successor_path) if successor_path.exists() else None
    if successor:
        p.require(
            successor["record_digest"] == p.digest_record(successor),
            "changed RG2b reconciliation",
        )
    p.require(
        follow["record_digest"] == p.digest_record(follow), "changed RG2b followup"
    )
    p.require(
        value["source_bindings"] == historical_sources(value, follow, successor),
        "changed original RG2b sources",
    )
    p.require(value["source_contracts"] == source_contracts(), "changed RG2b contracts")
    p.require(
        value["concrete_fixtures"] == fixtures(), "changed RG2b concrete profiles"
    )
    for key, names, count in (
        ("rg2b", TESTS, 29),
        ("affected_A_regressions", REGRESSIONS, 52),
    ):
        _, ids = pc.suite(names)
        result = value["results"][key]
        if key == "rg2b":
            _, added = pc.suite(
                [TESTS[0] + ".RG2bAuditRegressions", TESTS[0] + ".RG2bBoundaryPressure"]
            )
            p.require(
                set(ids) == set(result["executed_ids"]) | set(added)
                and not set(result["executed_ids"]) & set(added),
                "changed scalar audit roster",
            )
            ids = result["executed_ids"]
        p.require(
            result["executed_ids"] == ids
            and result["tests_run"] == len(ids) == count
            and result["failures"] == result["errors"] == result["skips"] == 0,
            "changed RG2b results/roster",
        )
    p.require(
        value["iteration_ids"] == ["P9-6.4a", "P9-6.4b"]
        and value["status"] == "implemented_verified_pending_independent_review"
        and value["P9_6_4c"] == "pending_unexecuted"
        and value["user_accepted"] is False
        and value["RG2b_G2_accepted"] is False
        and value["G3_accepted"] is False
        and value["accepted_generic_runtime_support"] == []
        and value["admitted_specialization_support_sets"] == [],
        "RG2b execution cannot grant review, acceptance or support",
    )
    p.git(ROOT, "merge-base", "--is-ancestor", BASE, "HEAD")
    changed = set(
        p.git(ROOT, "diff", "--name-only", BASE, "--", "src", "tests")
        .decode()
        .splitlines()
    )
    changed.update(
        p.git(ROOT, "ls-files", "--others", "--exclude-standard", "--", "src", "tests")
        .decode()
        .splitlines()
    )
    p.require(
        changed
        == RUNTIME
        | {
            "src/pygrc/models/grc_v4_rg2b_graph.py",
            "tests/models/test_grc_v4_rg2b_graph.py",
        },
        "RG2b changed unrelated numerical owners",
    )
    ready, _ = p.leaf_permissions(ROOT)
    p.require(
        {"P9-6.4a", "P9-6.4b", "P9-6.4c"} <= set(ready)
        and ("P9-6.4d" in ready) == (successor is not None),
        "RG2b review authority changed",
    )
    prior = cipc.check()
    return dict(
        status="passed",
        RG2b_methods=29,
        affected_A_regression_methods=52,
        scientific_tests_rerun=0,
        children="historical_original_subject_only",
        old_shared_c_audit="relocated_to_P9_6_4d",
        prior_composition=prior["P9_6_3c"],
        RG2b_G2_accepted=False,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--capture", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.capture:
        capture()
    else:
        print(json.dumps(check()))
