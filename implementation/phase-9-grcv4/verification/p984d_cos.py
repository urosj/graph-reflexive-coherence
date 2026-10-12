"""Bounded C_OS deep expansion: named fixtures, not arbitrary-depth support.

Independent target/preflight equations precede native execution. The accepted
OS consumer checker is reused unchanged. Only --run executes trajectories;
--check recomputes saved dense expectations with native producers disabled.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction
from importlib.metadata import version
import json
import platform
from unittest.mock import patch

import p984c_cos as previous

b, consumer = previous.base, previous.consumer
SELF = b.HERE + "p984d_cos.py"
TEST = b.HERE + "test_p984d_cos.py"
INPUTS = b.BASE + "P9-8.4d-COSCases.json"
RESULTS = b.BASE + "P9-8.4d-COSResults.json"
REVIEW = b.BASE + "P9-8.4d-COSReview.md"
DEGREES = (59, 66, 73, 94)
ROLES = ("current", "reset")
CONTRACTS = tuple(
    "D11-G9-EC-" + s
    for s in (
        "BRANCH-BFS-PARENT",
        "RECURSIVE-NONSTALL",
        "ROW-COLUMN-BALANCE",
        "RESOURCE-DISTRIBUTION",
        "LIFECYCLE-READMISSION",
    )
)


def authority():
    side = (
        b.ROOT
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
    )
    if str(side / "tool/src") not in b.sys.path:
        b.sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.successor import load_successor_forensic_context
    from grcv4_explorer.forensic import contract_provenance

    context = load_successor_forensic_context(b.ROOT, side)
    return {key: contract_provenance(context, key) for key in CONTRACTS}


def layouts():
    rows = []
    for degree in DEGREES:
        n = max(4, (degree + 4) // 7)
        q, remainder = divmod(n - 4, 3)
        for chirality in (-1, 1):
            for phase in (1, 2, 3) if remainder else (None,):
                extras = [q] * 3
                for j in range(remainder):
                    extras[(phase - 1 + chirality * j) % 3] += 1
                shares = [22 / 64, 21 / 64, 21 / 64]
                if degree == 94:
                    for j, share in enumerate((17 / 64, 24 / 64, 23 / 64)):
                        shares[(phase - 1 + chirality * j) % 3] = share
                rows.append(
                    dict(
                        id=f"P984D-D{degree}-E{chirality}-P{phase}",
                        degree=degree,
                        chirality=chirality,
                        phase=phase,
                        shares=shares,
                        expected=dict(
                            module_nodes=n,
                            branch_extras=extras,
                            capacity=7 * n + 2,
                            maximum_core_depth=4 if degree == 94 else 3,
                        ),
                    )
                )
    return rows


def mechanics(layout):
    """Literal chart/full creation-order scan, not production FIFO allocation."""
    tree = previous.independent_tree(
        tuple(layout["expected"]["branch_extras"]), layout["chirality"]
    )
    depth = {"core": 0}
    pending = list(tree)
    while pending:
        ready = [e for e in pending if e[1] in depth]
        b.require(ready, "independent tree disconnected or cyclic")
        for edge in ready:
            _, parent, child, _ = edge
            b.require(child not in depth, "duplicate child")
            depth[child] = depth[parent] + 1
            pending.remove(edge)
    rows = Counter((e[3] - 1) // 3 + 1 for e in tree)
    cols = Counter((e[3] - 1) % 3 + 1 for e in tree)
    b.require(
        len(depth) == layout["expected"]["module_nodes"]
        and len(tree) == len(depth) - 1
        and max(depth.values()) == layout["expected"]["maximum_core_depth"]
        and max(rows.values()) - min(rows.values()) <= 1
        and max(cols.values()) - min(cols.values()) <= 1,
        "independent layout invariant",
    )
    return dict(
        tree=[list(e) for e in tree],
        depths=depth,
        row_counts=[rows[i] for i in (1, 2, 3)],
        column_counts=[cols[i] for i in (1, 2, 3)],
    )


def make_manifest():
    old = b.read(previous.INPUTS)
    b.check_digest(old)
    b.check_bindings(old["source_bindings"])
    b.require(
        b.sha((b.ROOT / previous.REVIEW).read_bytes())
        == "66ff1d9a0e829cc0fb2349e1bc7e182236cc0e0196db5496af61e4201f067af9",
        "C_OS predecessor review drift",
    )
    declared = layouts()
    layout_digest = b.digest(declared)
    cases = []
    for layout in declared:
        template = next(
            c
            for c in old["cases"]
            if c["request"]["module_chirality"] == layout["chirality"]
            and c["request"]["growth_phase"] == 1
        )
        template = deepcopy(template)
        template["oracle"]["event_identity"]["resource_distribution"] = layout["shares"]
        case = deepcopy(template)
        case.update(
            case_id=layout["id"] + "::C_OS",
            fixture_id=layout["id"],
            subject_kind="named_deep_single_event_companion",
            coverage_binding=dict(
                record_digest=layout_digest,
                cell_ids=[layout["id"] + "::C_OS::" + role for role in ROLES],
            ),
        )
        case["request"].update(
            target_effective_degree=layout["degree"],
            module_chirality=layout["chirality"],
            growth_phase=layout["phase"],
            resource_distribution=layout["shares"],
            operation_id="p984d-cos-" + layout["id"],
        )
        case["oracle"] = previous.target_oracle(
            old["expected_source"], template, case["request"], layout
        )
        case["changes_from_frozen"] = [
            "deep_layout",
            "explicit_depth_dependent_simplex_tuple",
            "fresh_event_identity",
        ]
        case["mechanics"] = mechanics(layout)
        cases.append(case)
    paths = {r["path"] for r in old["source_bindings"]} | {
        SELF,
        TEST,
        previous.INPUTS,
        previous.REVIEW,
        previous.SELF,
        consumer.SELF,
        "specs/grc-9-v4-spec.md",
        "specs/grc-v4-spec.md",
        "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
    }
    traces = authority()
    paths |= {
        row["source_ref"]["path"] for trace in traces.values() for row in trace["rows"]
    }
    return b.seal(
        dict(
            schema="p984d-cos-cases-v1",
            family="C_OS",
            source_bindings=b.bind(paths),
            initial_inputs=old["initial_inputs"],
            expected_source=old["expected_source"],
            layouts=declared,
            cases=cases,
            authority=traces,
            scope=dict(
                required_cases=20,
                required_history_cells=40,
                target_beats_per_role=10,
                successive_events=False,
                arbitrary_depth=False,
                all_ten_closed=False,
                retention_budget_bytes=64_000_000,
                consumer="p984b_runtime.validate_results + p984b_cos_successor.check_consumption",
            ),
            user_accepted=False,
            aggregate_closed=False,
        )
    )


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "deep subjects/law/budget drift")


def target(manifest, case, shares=None):
    candidate = deepcopy(case)
    if shares is not None:
        candidate["request"]["resource_distribution"] = shares
    return b.independent_target(manifest, candidate)


def preflight(manifest):
    result = []
    source = b.GeometryStageInputs.from_payload(manifest["expected_source"]["inputs"])
    for case in manifest["cases"]:
        proposed = target(manifest, case)
        n = len(proposed.geometry.reference.graph.live_node_ids)
        # Connected unit tree: lambda_2 >= 2/[N(N-1)]. This reference bound
        # is not a rounded generated-H certificate; native strict tests remain.
        gap = Fraction(2, n * (n - 1)) - Fraction(
            proposed.geometry.reference.profile.params_resolved.candidate.Lambda_C
        )
        b.require(gap > 0, "reference selector lower gap")
        for role in ROLES:
            b.require(
                sum(map(Fraction, getattr(proposed, role).C))
                == sum(map(Fraction, getattr(source, role).C)),
                "represented event charge mismatch",
            )
        result.append(
            dict(
                case_id=case["case_id"],
                target_digest=b.digest(proposed.to_payload()),
                reference_selector_gap_lower=str(gap),
                dense_screen=consumer.dense_preflight(proposed),
            )
        )
    return result


def status(manifest, record):
    check_manifest(manifest)
    b.check_digest(record)
    b.require(
        record["schema"] == "p984d-cos-results-v1"
        and record["manifest_digest"] == manifest["record_digest"]
        and record["user_accepted"] is False
        and record["aggregate_closed"] is False,
        "deep result scope drift",
    )
    execution = previous.expand(record["execution"])
    b.check_digest(execution)
    b.require(
        execution["manifest_digest"] == manifest["record_digest"]
        and execution["user_accepted"] is False
        and execution["aggregate_closed"] is False,
        "execution scope drift",
    )
    ids = [c["case_id"] for c in manifest["cases"]]
    b.require(
        execution["requested_case_ids"] == ids
        and [r["case_id"] for r in execution["cases"]] == ids
        and [r["case_id"] for r in record["preflight"]] == ids,
        "deep roster drift",
    )
    for case, row in zip(manifest["cases"], execution["cases"], strict=True):
        b.require(
            row["input_digest"] == b.digest(case)
            and row["coverage_binding"] == case["coverage_binding"]
            and row["user_accepted"] is False
            and row["aggregate_closed"] is False,
            "case input/scope drift",
        )
        b.require(
            row["case_passed"] is True
            and row["outcome"] == "passed_named_case"
            and row["event_committed"] is True
            and row["first_failure"] is None
            and not row["unexecuted_dependent_stages"]
            and len(row["stages"]) == 16
            and all(s["outcome"] == "passed_named_stage" for s in row["stages"])
            and len(row["observations"]) == len(row["consumption_evidence"]) == 23,
            "incomplete deep case",
        )
    return dict(
        family="C_OS",
        status="executed_pending_review",
        required_cells=40,
        passed_cases=20,
        passing_pending_cells=40,
        accepted_cells=0,
        degrees=list(DEGREES),
        maximum_core_depth=4,
        new_events=20,
        target_steps=400,
        final_reads=40,
        successive_events=False,
        native_trajectories_rerun=False,
        dense_comparisons_rerun=False,
        cases=[
            {
                k: r[k]
                for k in ("case_id", "case_passed", "event_committed", "first_failure")
            }
            for r in execution["cases"]
        ],
    )


def check(manifest, record):
    summary = status(manifest, record)
    b.require(record["preflight"] == preflight(manifest), "deep preflight drift")
    execution = previous.expand(record["execution"])
    b.validate_results(manifest, execution)
    for case, row in zip(manifest["cases"], execution["cases"], strict=True):
        consumer.check_consumption(row, manifest, case)
    return dict(summary, retained_integrity="passed", dense_comparisons_rerun=True)


def run_case(job):
    manifest, case = job
    row = consumer.execute(manifest, case)
    print(case["case_id"], row["outcome"], row["first_failure"], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    b.require(1 <= args.workers <= 4, "workers outside 1..4")
    if args.prepare:
        b.write_new(INPUTS, make_manifest())
        print("deep C_OS subjects frozen; no native execution")
        return
    manifest = b.read(INPUTS)
    check_manifest(manifest)
    if args.check:
        with ExitStack() as stack:
            for module, name in (
                (b, "CandidateCOSPass"),
                (b, "ProvisionalCandidateCOSStep"),
                (b.native, "GRC9V4COSOperation"),
            ):
                stack.enter_context(
                    patch.object(
                        module,
                        name,
                        side_effect=AssertionError("native producer forbidden"),
                    )
                )
            print(json.dumps(check(manifest, b.read(RESULTS)), indent=2))
        return
    b.require(not (b.ROOT / RESULTS).exists(), "refuse to overwrite completed evidence")
    screens = preflight(manifest)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(
            pool.map(run_case, [(manifest, case) for case in manifest["cases"]])
        )
    b.require(
        all(r["case_passed"] for r in rows),
        "incomplete campaign; no final record published",
    )
    execution = b.seal(
        dict(
            manifest_digest=manifest["record_digest"],
            requested_case_ids=[r["case_id"] for r in rows],
            cases=rows,
            user_accepted=False,
            aggregate_closed=False,
        )
    )
    record = b.seal(
        dict(
            schema="p984d-cos-results-v1",
            manifest_digest=manifest["record_digest"],
            preflight=screens,
            execution=previous.compact(execution),
            environment=dict(
                python=platform.python_version(),
                numpy=version("numpy"),
                python_flint=version("python-flint"),
            ),
            user_accepted=False,
            aggregate_closed=False,
        )
    )
    b.require(previous.expand(record["execution"]) == execution, "lossy compaction")
    checked = check(manifest, record)
    b.require(
        len(b.canonical_json_bytes(record))
        < manifest["scope"]["retention_budget_bytes"],
        "retention budget",
    )
    b.write_new(RESULTS, record)
    print(json.dumps(checked, indent=2))


if __name__ == "__main__":
    main()
