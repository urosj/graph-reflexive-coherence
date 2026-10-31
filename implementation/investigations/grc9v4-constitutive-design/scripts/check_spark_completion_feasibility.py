"""Small research checks; no trajectory run or completion-policy implementation.

Run from any working directory with the repository .venv Python. --write creates
the initial retained record; --check recomputes its exact arithmetic, forensic
traces and extraction from accepted examples. Neither runs native evolution.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
import lzma
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = "implementation/investigations/grc9v4-constitutive-design/"
SIDE = INV + "tools/exploratory-side-tool"
OUTPUT = INV + "evidence/spark-completion/InitialFeasibility.json"
for directory in (ROOT / "src", ROOT / SIDE / "tool/src"):
    sys.path.insert(0, str(directory))

from grcv4_explorer.basin import load_basin_forensic_context
from grcv4_explorer.canonical import record_digest
from grcv4_explorer.forensic import contract_provenance, debt_lifecycle
from pygrc.models.grc_9_v4_lifecycle import GRC9SparkPolicy, GRC9V4CandidateAssessment
from pygrc.models.grc_9_v4_topology import GRC9V4RowSummary


def require(condition, message):
    if not condition:
        raise ValueError(message)


def seed(gradient, gradient_tolerance, hessian_tolerance, sign=-1):
    """Independent exact predicate on the represented row operands."""
    return (sum(F(x) ** 2 for x in gradient) < F(gradient_tolerance) ** 2
            and min(sign * F(x) for x in gradient) > F(hessian_tolerance))


def seed_controls():
    cases = [
        ("valid", (-0.125,) * 3, 0.5, 0.0625, -1, True),
        ("hessian_equality", (-0.0625,) * 3, 0.5, 0.0625, -1, False),
        ("norm_equality", (-0.125, -0.25, -0.25), 0.375, 0.0625, -1, False),
        ("norm_just_inside", (-0.125, -0.25, -0.25),
         math.nextafter(0.375, math.inf), 0.0625, -1, True),
        ("norm_just_outside", (-0.125, -0.25, -0.25),
         math.nextafter(0.375, 0.0), 0.0625, -1, False),
        ("missing_row", (-0.125, -0.125, 0.0), 0.5, 0.0625, -1, False),
        ("wrong_polarity", (0.125,) * 3, 0.5, 0.0625, -1, False),
        ("opposite_declared_sign", (0.125,) * 3, 0.5, 0.0625, 1, True),
        ("incompatible_thresholds", (-0.75,) * 3, 0.5, 0.5, -1, False),
    ]
    records = []
    for name, g, eg, eh, sign, expected in cases:
        independent = seed(g, eg, eh, sign)
        policy = GRC9SparkPolicy("grc9v4-spark-policy-v1",
                                "current_hybrid_signed_hessian", eg, eh, 0.0, None)
        actual = GRC9V4CandidateAssessment(
            GRC9V4RowSummary("test", g, (0.0,) * 3, sign), (1, 4, 7), policy)
        require(independent == actual.basin_seed == expected, name)
        records.append(dict(case=name, expected_seed=expected,
                            represented_gradient=[x.hex() for x in g],
                            gradient_tolerance=eg.hex(), hessian_tolerance=eh.hex(),
                            hessian_sign=sign))
    return records


def build():
    inputs = {}

    def load(path):
        raw = (ROOT / path).read_bytes()
        inputs[path] = hashlib.sha256(raw).hexdigest()
        return json.loads(lzma.decompress(raw) if path.endswith(".xz") else raw)

    fixtures = load("examples/grc9v4/fixtures.json")["families"]
    accepted = load("implementation/phase-9-grcv4/tranche-10/P9-10.4-Acceptance.json")
    require(record_digest(accepted, "record_digest") == accepted["record_digest"]
            == "8508480598a8f672d3f1142634107137ff77118fa039def2ffcac9bff46b972b",
            "accepted example decision changed")
    publication = load(accepted["evidence"]["path"])
    require(inputs[accepted["evidence"]["path"]] == accepted["evidence"]["sha256"]
            and record_digest(publication, "record_digest")
            == accepted["evidence"]["record_digest"] == publication["record_digest"],
            "accepted example publication changed")
    require(accepted["user_accepted"] and accepted["P9_10_4_closed"],
            "examples must be accepted")
    require(sorted(fixtures) == accepted["families"] and len(fixtures) == 10,
            "expected ten accepted example families")
    rows = []
    for family, fixture in sorted(fixtures.items()):
        config = fixture["configuration"]
        policy = config["specialization"]["resolved"]["spark"]
        eg, eh = F(policy["gradient_tolerance"]), F(policy["basin_hessian_tolerance"])
        require(eg > 0 and eh > 0 and eg * eg <= 3 * eh * eh,
                "frozen example seed exclusion no longer applies")
        result = load(f"examples/grc9v4/results/{family}.json.xz")["result"]
        event = result["expansion"]
        require(event["event"]["committed"], "retained expansion did not commit")
        obs = event["target_continuation"]["observables"]
        require(obs["stage"] == "commit", "target continuation was not committed")
        nodes = event["after_event"]["vertices"]
        ports = obs["port_occupancy"]
        gradients, signed_h = obs["row_gradient"], obs["signed_row_hessian"]
        require(len(nodes) == len(ports) == len(gradients) == len(signed_h),
                "target row coverage mismatch")
        full_rows = []
        for node, occupied, g, h in zip(nodes, ports, gradients, signed_h, strict=True):
            occupied_rows = {(p - 1) // 3 for p in occupied}
            require(all(g[i] == 0 for i in range(3) if i not in occupied_rows),
                    "empty fixed row must have zero gradient")
            require(h == [-x for x in g], "retained example sign is not -1")
            require(not seed(g, float(eg), float(eh)), "excluded example acquired seed")
            if len(occupied_rows) == 3:
                full_rows.append(node)
        require(len(nodes) == 17 and len(full_rows) == 4,
                "D52 example occupancy population changed")
        rows.append(dict(
            family=family, model_identity=fixture["model_identity"],
            gradient_tolerance=str(eg), hessian_tolerance=str(eh),
            threshold_slack=str(eg * eg - 3 * eh * eh),
            seed_possible_under_frozen_thresholds=False,
            target_model_identity=event["after_event"]["model_identity"],
            target_node_count=len(nodes), target_nodes_with_all_three_rows=full_rows,
            target_nodes_excluded_by_empty_row=len(nodes) - len(full_rows),
            retained_target_seed_count=0,
            observation_scope="one retained post-expansion current-role sample",
        ))

    positive = load("examples/grc9v4/results/seeds.json")
    p = positive["diagnostic"]["policy"]
    positive_nodes = []
    for row in positive["diagnostic"]["assessments"]:
        calculated = seed(row["gradient"], p["gradient_tolerance"], p["basin_hessian_tolerance"])
        require(calculated == row["basin_seed"], "positive seed extraction mismatch")
        if calculated:
            positive_nodes.append(row["node_id"])
    require(positive_nodes == ["s"] and positive["topology_events"] == 0
            and not positive["completed_spark"] and not positive["attracting_basin_claimed"],
            "seed control scope changed")
    require(positive["original_specialization_id"] != positive["selected_specialization_id"],
            "new seed threshold must have a different specialization identity")
    published_inputs = {r["path"]: r["sha256"]
                        for r in publication["sources"] + publication["outputs"]}
    for path, sha in inputs.items():
        if path.startswith("examples/grc9v4/"):
            require(published_inputs.get(path) == sha,
                    "example bytes differ from accepted publication: " + path)

    context = load_basin_forensic_context(ROOT, ROOT / SIDE)
    ids = (
        "D10.2-EC-PARENT-GRC9-CHILD-BASIN-STABILIZATION",
        "D10.2-EC-PARENT-BASE-GRC9-ROW-BASIS-DIFFERENTIAL",
        "P9-EC-GRC9-BASIN-CEILING", "P9-EC-GRC9-BASIN-IDENTITY",
    )
    traces = {name: contract_provenance(context, name) for name in ids}
    traces["P9-10.1a-DEBT-BASIN-IDENTITY"] = debt_lifecycle(context, "P9-10.1a-DEBT-BASIN-IDENTITY")
    require(traces[ids[0]]["rows"][0]["payload"]["support_disposition"]
            == "indeterminate_requires_review", "historical support was promoted")
    require(traces["P9-10.1a-DEBT-BASIN-IDENTITY"]["rows"][0]["payload"]["status"]
            == "resolved_bounded_design", "baseline design debt is not this new debt")
    for path in (
        INV + "scripts/check_spark_completion_feasibility.py",
        "src/pygrc/models/grc_9_v4_lifecycle.py",
        "src/pygrc/models/grc_9_v4_topology.py",
        "specs/grc-9-v4-spec.md", "specs/grc-9-v4-basin-interface.md",
        INV + "drafts/2026-09-GRC-V4.md",
    ):
        inputs[path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    return dict(
        schema="grc9v4-spark-completion-initial-feasibility-v1",
        status="research_findings_pending_review", accepted_authority=False,
        native_steps_executed=0, topology_events_executed=0,
        completion_policy_selected=False, completed_spark_demonstrated=False,
        inputs=[dict(path=p, sha256=s) for p, s in sorted(inputs.items())],
        forensic_traces=traces, exact_predicate_controls=seed_controls(),
        example_exclusions=rows,
        positive_seed_control=dict(seed_nodes=positive_nodes, topology_events=0,
            changed_specialization_identity=True,
            observation_scope="retained isolated C_OS seed; no child gain or temporal claim"),
        limits=["Free real row-vector feasibility is not graph/state reachability.",
                "Strict threshold feasibility does not guarantee a binary64 witness.",
                "Retained-example extraction is not a native rerun or independent root certificate.",
                "No exclusion of flow-only or other separately justified completion policies.",
                "No dynamic child formation, persistence or attraction result."],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    path = ROOT / OUTPUT
    if args.write:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as stream:
            stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    else:
        require(json.loads(path.read_text()) == value, "retained feasibility record differs")
    print("PASS: 9 exact predicate controls; 10 frozen seed exclusions; retained positive seed; 5 forensic traces. No native evolution.")


if __name__ == "__main__":
    main()
