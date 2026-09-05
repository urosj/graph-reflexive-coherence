"""Read-only P9-1.4/P9-1.5 review validation, not runtime authorization.

Historical regression bindings are always checked against their Git revision.
--check-current-baseline additionally checks the present bytes, for a review
baseline diagnostic, including the reviewed plan/checklist snapshot; it is
not the future successor mutation policy or a freeze on later planning edits.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = "7c772d36bd4cf12b4a444b7b954b74612de2926f"
DATA = ["P9-1.4-SupportAndDependencies.json", "P9-1.5-OwnershipAndLegacyBaseline.json"]
DOCS = ["P9-1.4-SupportReview.md", "P9-1.5-OwnershipReview.md"]


def read(path):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def sha(content):
    return hashlib.sha256(content).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_bindings(rows):
    for row in rows:
        require(
            sha((ROOT / row["path"]).read_bytes()) == row["sha256"],
            f"binding drift: {row['path']}",
        )


def check_dag(edges, external=()):
    visited, active = set(), set()

    def visit(node):
        if node in external or node in visited:
            return
        require(node in edges, f"unresolved dependency: {node}")
        require(node not in active, f"dependency cycle at {node}")
        active.add(node)
        for predecessor in edges[node]:
            visit(predecessor)
        active.remove(node)
        visited.add(node)

    for node in edges:
        visit(node)


def planned_specialization_requirements(support, advertised=(), handoff=()):
    """Planning dependency closure only: never execution or capability authority."""
    edges = {
        r["iteration_id"]: list(r["requires"]) for r in support["dependency_edges"]
    }
    selected = set(advertised) | set(handoff)
    for rule in support["conditional_dependencies"]:
        if selected.intersection(rule["when_any_capability_selected"]):
            edges[rule["iteration_id"]].extend(rule["requires"])
    result = set()

    def visit(node):
        if node not in result:
            result.add(node)
            for predecessor in edges.get(node, []):
                visit(predecessor)

    visit("P9-9.6")
    return result


def validate_completion_dependencies(support, edges):
    optional = ["completed_spark", "hierarchy_tracking"]
    policy = support["specialization_policy"]
    require(
        policy["optional_completion_capabilities"] == optional
        and policy["explicit_project_handoff_capabilities"] == []
        and policy["current_advertised_optional_capabilities"] == [],
        "unrecorded optional capability selection",
    )
    require(
        edges["P9-9.1"] == ["P9-9.1a", "P9-9.1b"]
        and edges["P9-9.4"] == ["P9-9.1b", "P9-9.2-C_OS-lifecycle"],
        "completion/lifecycle split lost",
    )
    aggregates = support["aggregate_iterations"]
    require(
        len(aggregates) == 1
        and aggregates[0]["iteration_id"] == "P9-9.1"
        and aggregates[0]["children"] == edges["P9-9.1"]
        and aggregates[0]["role"]
        == "aggregate_register_not_executable_or_a_universal_crossing_prerequisite",
        "completion aggregate lost",
    )
    rules = support["conditional_dependencies"]
    require(len(rules) == 1, "conditional completion rule missing")
    rule = rules[0]
    require(
        rule["iteration_id"] == "P9-9.6"
        and rule["requires"] == ["P9-9.1a"]
        and rule["when_any_capability_selected"] == optional
        and rule["selection_surfaces"]
        == ["advertised_capabilities", "explicit_project_handoff_capabilities"]
        and rule["application"] == "per_exact_consumed_profile_and_capability_scope",
        "conditional completion scope drift",
    )
    mandatory = planned_specialization_requirements(support)
    require(
        not {"P9-9.1", "P9-9.1a"}.intersection(mandatory),
        "optional completion became universal",
    )
    anchors = {
        "P9-8.1a",
        "P9-8.1b",
        "P9-8.1c",
        "P9-8.1d",
        "P9-3.3",
        "P9-7.5-C_OS",
        "P9-7.6-C_OS",
        "P9-9.1b",
        "P9-9.4",
        "P9-9.5",
        "P9-4.8",
        *[
            f"P9-9.2-C_OS-{s}"
            for s in ["transition", "state", "observable", "lifecycle"]
        ],
    }
    require(anchors <= mandatory, "mandatory specialization evidence lost")
    for capability in optional:
        for surface in ["advertised", "handoff"]:
            selected = planned_specialization_requirements(
                support, **{surface: [capability]}
            )
            require(
                mandatory < selected and "P9-9.1a" in selected,
                "selected completion lacks its evidence prerequisite",
            )


def validate_follow_through(ownership, support, checklist):
    registered = {r["iteration_id"] for r in support["child_iterations"]}
    for key, prefix, count, status in [
        (
            "implementation_follow_through",
            "P9-REVIEW-FOLLOW-7",
            5,
            "registered_pending_implementation",
        ),
        (
            "successor_verification_follow_through",
            "P9-REVIEW-PRESSURE-8",
            6,
            "registered_pending_successor_verification",
        ),
    ]:
        rows = ownership[key]
        require(
            [r["id"] for r in rows] == [f"{prefix}.{i}" for i in range(1, count + 1)],
            "follow-through registration omitted or duplicated",
        )
        for row in rows:
            require(row["status"] == status, "future follow-through marked executed")
            require(row["requirement"] and row["iterations"], "unowned follow-through")
            require(row["id"] in checklist, "follow-through missing from checklist")
            for iteration in row["iterations"]:
                require(
                    iteration in checklist or iteration in registered,
                    "unknown follow-through leaf",
                )
    tau = ownership["implementation_follow_through"][2]["forensic_evidence"]
    crosswalk = read(HERE / "P9-1.1-SourceCrosswalk.json")
    evidence = next(
        r
        for r in crosswalk["contracts"]
        if r["contract_id"] == tau["query"]["contract_id"]
    )
    require(
        tau["trace_digest"] == evidence["forensic_evidence"]["trace_digest"]
        and tau["source_contract"] == evidence["source_contract"]
        and tau["source_ref"] == evidence["forensic_evidence"]["rows"][0]["source_ref"]
        and tau["support_disposition"] == evidence["support_disposition"]
        and [r["edge_id"] for r in tau["edge_refs"]]
        == evidence["forensic_evidence"]["rows"][0]["edge_ref_ids"],
        "tau control provenance drift",
    )


def validate_data(support, ownership):
    crosswalk = read(HERE / "P9-1.1-SourceCrosswalk.json")
    fixtures = read(ROOT / "specs/grc-v4-conformance-fixtures.json")
    vectors = read(ROOT / "specs/grc-v4-conformance-vectors.json")
    schema = read(ROOT / "specs/grc-v4-contract-schema.json")
    discriminants = {}
    for branch in schema["$defs"]["profile_identity_payload"]["oneOf"]:
        properties = branch["properties"]
        family = properties["profile_family_id"]["const"]
        require(family not in discriminants, "duplicate schema discriminant")
        discriminants[family] = (
            properties["candidate"]["const"],
            properties["realization"]["const"],
        )
    require(
        set(discriminants) == set(fixtures["profile_families"]),
        "schema roster mismatch",
    )
    for data in [support, ownership]:
        require(data["baseline_commit"] == BASE, "incorrect baseline")
        require(data["release_id"] == crosswalk["release_id"], "incorrect release")
        require(data["runtime_authorized"] is False, "review grants runtime authority")
        require(
            data["reviewer_decision"] == "pending_user_review",
            "unrecorded review acceptance",
        )
        check_bindings(data["source_review_bindings"])
    require(
        support["accepted_generic_runtime_support"] == [],
        "unsupported runtime admission",
    )
    require(
        support["admitted_specialization_support_sets"] == [],
        "unsupported G3 admission",
    )
    profiles = support["profiles"]
    require(
        [p["profile_family"] for p in profiles] == fixtures["profile_families"],
        "incomplete/reordered profile roster",
    )
    realization = {
        "CI": "CI-BRANCH",
        "OS": "OS-ONE-PASS",
        "RG2b": "RG2B-SECTION",
        "PC": "PC-ZOH",
        "CI+PC": "CI-PC-SAME-SOURCE",
    }
    for profile in profiles:
        require(
            (profile["candidate"], profile["realization"])
            == discriminants[profile["profile_family"]],
            "profile/schema discriminant mismatch",
        )
        expected = [r["id"] for r in fixtures["common_cases"]]
        expected += [
            r["id"] for r in fixtures[f"candidate_{profile['candidate'].lower()}_cases"]
        ]
        expected += [realization[profile["realization"]]]
        expected += [r["id"] for r in fixtures["lifecycle_cases"]]
        require(
            profile["required_catalog_case_ids"] == expected,
            f"case omission for {profile['profile_family']}",
        )
        require(
            profile["current_support"] == "unsupported_not_implemented"
            and profile["gate_state"] == "pending"
            and profile["exact_accepted_profile_ids"] == [],
            "profile admission inferred from planning",
        )
    require(
        [r["migration_class"] for r in support["migration_classes"]]
        == [r["class"] for r in vectors["migration_policy_matrix"]],
        "migration class omission",
    )
    seed = next(
        v
        for v in vectors["identity_vectors"]
        if v["vector_id"] == "IDENTITY-GRCV4-PROFILE-C-OS"
    )
    require(
        support["first_slice_identity_policy"]["seed_reference_id"]
        == seed["expected_identifier"],
        "seed identity drift",
    )
    edges = {r["iteration_id"]: r["requires"] for r in support["dependency_edges"]}
    require(len(edges) == len(support["dependency_edges"]), "duplicate dependency node")
    check_dag(edges, {r["id"] for r in support["external_dependencies"]})
    validate_completion_dependencies(support, edges)
    require(
        edges["P9-7.8-C_OS"] == ["P9-G2[C_OS]"]
        and edges["P9-G3[C_OS]"] == ["P9-7.8-C_OS"],
        "unrelated profile barrier at singleton G3",
    )
    children = support["child_iterations"]
    require(
        len({r["iteration_id"] for r in children}) == len(children), "duplicate child"
    )
    checklist = (
        ROOT / "implementation/Phase-9-GRCV4-ImplementationChecklist.md"
    ).read_text()
    validate_follow_through(ownership, support, checklist)
    for child in children:
        require(
            child["parent_id"] in checklist, f"unknown parent: {child['parent_id']}"
        )
        require(
            child["status"] == "planned_not_executed", "runtime child marked executed"
        )
        require(
            child["iteration_id"] in edges or child["evidence_alias_of"] in edges,
            f"unrouted child: {child['iteration_id']}",
        )
    require(
        support["specialization_policy"]["normative_degrees"] == [30, 31, 45, 52],
        "normative degree loss",
    )
    require(
        support["specialization_policy"]["additional_probes"] == [37, 44],
        "probe/normative conflation",
    )
    modules = ownership["modules"]
    module_edges = {m["module_id"]: m["dependencies"] for m in modules}
    require(len(module_edges) == len(modules), "duplicate module")
    check_dag(module_edges)
    assigned = Counter(g for m in modules for g in m["source_groups"])
    require(
        assigned == Counter(crosswalk["groups"].keys()),
        "crosswalk group lost or multiply owned",
    )
    for module in modules:
        name = module["module_id"]
        require(
            module["path"] == f"src/pygrc/models/{name}.py", "non-V4 production target"
        )
        require(name.startswith(("grc_v4", "grc_9_v4")), "legacy module selected")
        require(
            module["test_path"] == f"tests/models/test_{name}.py",
            "test target mismatch",
        )
        if name.startswith("grc_v4"):
            require(
                not any(d.startswith("grc_9_v4") for d in module["dependencies"]),
                "generic module depends on specialization",
            )
    require(
        ownership["proposed_integration_paths"]
        == ["src/pygrc/models/__init__.py", "pyproject.toml"]
        and ownership["core_edits_planned"] == [],
        "legacy core mutation proposed",
    )
    require(
        set(fixtures["execution_contract"]["required_result_fields"])
        <= set(ownership["retention_policy"]["required_fields"]),
        "runtime evidence fields missing",
    )
    return support, ownership


def validate_legacy(ownership, current):
    rows = ownership["legacy_bindings"]
    require(
        len(rows) == 135 and len({r["path"] for r in rows}) == 135,
        "legacy baseline membership drift",
    )
    required = subprocess.check_output(
        [
            "git",
            "ls-tree",
            "-r",
            "--name-only",
            BASE,
            "src/pygrc/core",
            "src/pygrc/models",
            "tests/core",
            "tests/models",
        ],
        cwd=ROOT,
        text=True,
    ).splitlines()
    required += [
        "specs/grc-common-interface.md",
        "specs/grc-v2-spec.md",
        "specs/grc-v3-spec.md",
        "specs/grc-9-spec.md",
        "specs/grc-9-v3-spec.md",
        "specs/lgrc-9-v3-spec.md",
        "pyproject.toml",
        "src/pygrc/__init__.py",
    ]
    require(
        {r["path"] for r in rows} == set(required), "legacy baseline target omitted"
    )
    for row in rows:
        content = subprocess.check_output(
            ["git", "show", f"{BASE}:{row['path']}"], cwd=ROOT
        )
        require(sha(content) == row["sha256"], f"incorrect Git baseline: {row['path']}")
        policy = (
            "separately_reviewed_additive_integration"
            if row["path"] in ownership["proposed_integration_paths"]
            else "frozen_legacy_reference"
        )
        require(row["policy"] == policy, "baseline policy mismatch")
    if current:
        check_bindings(rows)


def self_test(support, ownership):
    """Mutation probes affect copies only, never the review files or authority."""
    probes = [
        ("missing_profile", "profile roster", lambda s, o: s["profiles"].pop()),
        (
            "missing_fixture",
            "case omission",
            lambda s, o: s["profiles"][0]["required_catalog_case_ids"].pop(),
        ),
        (
            "missing_migration",
            "migration class omission",
            lambda s, o: s["migration_classes"].pop(),
        ),
        (
            "duplicate_owner",
            "multiply owned",
            lambda s, o: o["modules"][0]["source_groups"].append("state"),
        ),
        (
            "dependency_cycle",
            "dependency cycle",
            lambda s, o: o["modules"][0]["dependencies"].append("grc_v4"),
        ),
        (
            "runtime_promotion",
            "runtime authority",
            lambda s, o: s.update(runtime_authorized=True),
        ),
        (
            "unrelated_G3_barrier",
            "singleton G3",
            lambda s, o: next(
                r for r in s["dependency_edges"] if r["iteration_id"] == "P9-7.8-C_OS"
            )["requires"].append("P9-G2[A_OS]"),
        ),
        *[
            (
                f"noncanonical_{family}",
                "schema discriminant",
                lambda s, o, family=family: next(
                    p for p in s["profiles"] if p["profile_family"] == family
                ).update(realization="CI_PC"),
            )
            for family in ["A_CI_PC", "C_CI_PC"]
        ],
        (
            "wrong_candidate",
            "schema discriminant",
            lambda s, o: s["profiles"][0].update(candidate="C"),
        ),
        (
            "universal_completion",
            "became universal",
            lambda s, o: next(
                r for r in s["dependency_edges"] if r["iteration_id"] == "P9-9.6"
            )["requires"].append("P9-9.1a"),
        ),
        (
            "mixed_lifecycle",
            "split lost",
            lambda s, o: next(
                r for r in s["dependency_edges"] if r["iteration_id"] == "P9-9.4"
            ).update(requires=["P9-9.1", "P9-9.2-C_OS-lifecycle"]),
        ),
        (
            "missing_conditional",
            "rule missing",
            lambda s, o: s["conditional_dependencies"].clear(),
        ),
        (
            "missing_follow_through",
            "registration omitted",
            lambda s, o: o["implementation_follow_through"].pop(),
        ),
        (
            "missing_pressure",
            "registration omitted",
            lambda s, o: o["successor_verification_follow_through"].pop(),
        ),
        (
            "future_work_promotion",
            "marked executed",
            lambda s, o: o["implementation_follow_through"][0].update(
                status="completed"
            ),
        ),
    ]
    for name, expected, mutate in probes:
        altered_s, altered_o = deepcopy(support), deepcopy(ownership)
        mutate(altered_s, altered_o)
        try:
            validate_data(altered_s, altered_o)
        except ValueError as error:
            require(expected in str(error), f"unexpected rejection for {name}: {error}")
        else:
            raise ValueError(f"mutation was not rejected: {name}")
    print(
        f"PHASE9_ARCHITECTURE_NEGATIVE_PROBES_PASS cases={len(probes)} in_memory_only=true"
    )


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])


def check_rendering():
    cache = {}

    def parse(path):
        path = path.resolve()
        if path not in cache:
            result = subprocess.run(
                ["pandoc", "--from=gfm", "--to=html", "--no-highlight", str(path)],
                check=True,
                capture_output=True,
                text=True,
            )
            parsed = Links()
            parsed.feed(result.stdout)
            cache[path] = parsed
        return cache[path]

    files = [HERE / n for n in DOCS] + [
        ROOT / "implementation" / f"Phase-9-GRCV4-Implementation{x}.md"
        for x in ["Plan", "Checklist"]
    ]
    count = 0
    for path in files:
        for link in parse(path).links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                continue
            target = (
                (path.parent / unquote(parts.path)).resolve() if parts.path else path
            )
            require(target.exists(), f"missing local link: {link}")
            if parts.fragment and target.suffix == ".md":
                require(
                    unquote(parts.fragment) in parse(target).ids,
                    f"missing anchor: {link}",
                )
            count += 1
    print(
        f"PHASE9_ARCHITECTURE_RENDERING_PASS documents={len(files)} local_links={count}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-current-baseline", action="store_true")
    parser.add_argument("--check-rendering", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    subprocess.run(
        [sys.executable, str(HERE / "audit_source_review.py")], cwd=ROOT, check=True
    )
    support, ownership = validate_data(*(read(HERE / name) for name in DATA))
    validate_legacy(ownership, args.check_current_baseline)
    if args.self_test:
        self_test(support, ownership)
    record = read(HERE / "P9-1.4-1.5-ExecutionRecord.json")
    require(
        record["runtime_authorized"] is False
        and record["gate_effect"] == "none_P9_G1_pending",
        "execution record grants authority",
    )
    require(
        [r["iteration_id"] for r in record["iteration_results"]]
        == ["P9-1.4", "P9-1.5"],
        "separate result omitted",
    )
    for row in record["iteration_results"]:
        require(
            row["reviewer_decision"] == "pending_user_acceptance",
            "user acceptance inferred",
        )
    require(
        {Path(b["path"]).name for b in record["artifact_bindings"]}
        == set(DATA + DOCS + [Path(__file__).name]),
        "package binding omission",
    )
    require(len(record["artifact_bindings"]) == 5, "duplicate package binding")
    check_bindings(record["artifact_bindings"])
    require(
        [r["path"] for r in record["planning_bindings"]]
        == [
            f"implementation/Phase-9-GRCV4-Implementation{suffix}.md"
            for suffix in ["Plan", "Checklist"]
        ],
        "planning binding omission",
    )
    if args.check_current_baseline:
        check_bindings(record["planning_bindings"])
    require(
        [Path(r["path"]).name for r in record["independent_review"]["input_bindings"]]
        == [
            "P9-1.4-1.5-Independent-Review.md",
            "P9-1.4-1.5-independent-review-checks.json",
        ],
        "independent review input omitted",
    )
    check_bindings(record["independent_review"]["input_bindings"])
    if args.check_rendering:
        check_rendering()
    print(
        f"PHASE9_ARCHITECTURE_REVIEW_PASS profiles={len(support['profiles'])} registered_children={len(support['child_iterations'])} modules={len(ownership['modules'])} legacy_bindings=135 implementation_follow_ups=5 successor_pressure_checks=6 runtime_authorized=false"
    )


if __name__ == "__main__":
    main()
