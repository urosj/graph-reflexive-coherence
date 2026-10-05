"""Read-only Tranche 8 evidence index; never implementation permission or a rerun.

The committed checkpoint pins existing acceptance, not a new acceptance ledger.
Historical mutable handoffs are read from Git; immutable retained evidence must
still match on disk. Numerical checkers are exposed only by explicit CLI action.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
PHASE = "implementation/phase-9-grcv4/"
BASE = PHASE + "tranche-8/"
HERE = PHASE + "verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/"
ASSET = SIDE + "tool/phase9-web/tranche8-evidence.js"
CHECKPOINT = "dbfcd311b8ee67ad9a5d8ea0f38670d88b8d57b1"
HANDOFF = "implementation/Phase-9-GRCV4-Handoff.md"
PLAN = "implementation/Phase-9-GRCV4-ImplementationPlan.md"
FAMILIES = tuple(c + "_" + r for c in ("A", "C") for r in ("OS", "CI", "PC", "CI_PC", "RG2b"))
PROFILE_RECORDS = {
    "A_OS": ("A.2-AOS", "A.1-AOS"),
    "A_CI": ("A.2-ACI", "A.1-ACI"),
    "A_PC": ("A.2-APC", "A.1-APC"),
    "A_CI_PC": ("A.2-ACIPC", "A.1-ACIPC"),
    "A_RG2b": ("A.2-ARG2b", "A.1-ARG2b"),
    "C_CI": ("C-CI", None),
    "C_CI_PC": ("C-CI-PC", None),
    "C_RG2b": ("C-RG2b", None),
}
MECHANICS = (
    ("P9-8.0", "Accepted R1–R10 bounded feasibility, not native execution", "p9-81e-exact-backend-correction-and-p9-80-audit"),
    ("P9-8.1", "Accepted shared mechanics parent", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1a", "Fixed chart and immutable port graph", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1b", "Fixed-row differential and stage-specific weight bridge", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1c", "Fresh mechanical candidate trigger, not a completed spark", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1d", "Column coarse-graining and Split", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1e", "Exact-backend correction", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.2", "Pure allocator: 17 frozen vectors, three transforms; no event commit", "p9-82-pure-expansion-allocator"),
)
CHILDREN = {
    "a": "Coverage and comparison contracts",
    "b": "All-ten frozen expansion counterparts",
    "c": "Capacity and phase boundaries",
    "d": "Deeper recursive runtime expansion",
    "e": "Ordering, relabeling and signed-edge covariance",
    "f": "Chart rotation and reflection/chirality covariance",
    "g": "Larger-graph admission and independent oracles",
    "h": "Larger-graph runtime and covariance",
    "i": "Coverage reconciliation, side-tool catch-up and handoff",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


class Sources:
    def __init__(self, root):
        self.root, self.refs, self.values = Path(root).resolve(), {}, {}
        git(self.root, "merge-base", "--is-ancestor", CHECKPOINT, "HEAD")

    def raw(self, name, *, historical=False):
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "repository-relative source required")
        if name not in self.values:
            frozen = git(self.root, "show", CHECKPOINT + ":" + name)
            path = self.root / name
            require(not path.is_symlink() and path.resolve().is_relative_to(self.root), "unsafe source path")
            require(historical or path.read_bytes() == frozen, "Tranche 8 retained source drift: " + name)
            self.values[name] = frozen
            self.refs[name] = dict(path=name, sha256=hashlib.sha256(frozen).hexdigest(),
                                   revision=CHECKPOINT, basis="historical_git" if historical else "current_equals_accepted_checkpoint")
        return self.values[name]

    def read(self, name):
        return json.loads(self.raw(name))

    def ref(self, name, *, historical=False, anchor=None):
        self.raw(name, historical=historical)
        return {**self.refs[name], **({"anchor": anchor} if anchor else {})}


def build(root=ROOT):
    sources = Sources(root)
    handoff = sources.ref(HANDOFF, historical=True)
    sources.ref(PLAN, historical=True)
    coverage_path = BASE + "P9-8.4a-Coverage.json"
    coverage = sources.read(coverage_path)
    families = coverage["families"]
    require(set(families) == set(FAMILIES), "all-ten prerequisite population drift")
    mechanics = [dict(work_id=i, status="accepted_bounded", scope=label,
                       acceptance={**handoff, "anchor": anchor}, numerical_conformance_inferred=False)
                 for i, label, anchor in MECHANICS]
    mechanics[0]["acceptance"] = sources.ref(BASE + "P9-8.0-AggregateReview.md")
    profiles = []
    for family in FAMILIES:
        row = families[family]
        evidence = [sources.ref(r["path"]) for r in row["evidence"]]
        review = {**handoff, "anchor": {"C_OS": "p9-83c-os-native-event-integration", "C_PC": "p9-83c-pc-whole-carrier-event-integration"}.get(family)}
        oracle = None
        if family in PROFILE_RECORDS:
            runtime_name, oracle_name = PROFILE_RECORDS[family]
            stem = BASE + "P9-8.3" + runtime_name
            validation = sources.read(stem + "-Validation.json")
            require("acceptance" in validation, "missing recorded runtime decision: " + family)
            evidence.append(sources.ref(stem + "-Validation.json"))
            review = sources.ref(stem + "-RuntimeReview.md")
            if oracle_name:
                oracle_stem = BASE + "P9-8.3" + oracle_name
                oracle = dict(status="accepted_bounded", evidence=sources.ref(oracle_stem + "-Oracle.json"),
                              review=sources.ref(oracle_stem + "-OracleReview.md"))
                if family != "A_OS":
                    oracle["acceptance"] = sources.ref(oracle_stem + "-Acceptance.json")
        profiles.append(dict(family=family, work_id="P9-8.3[" + family + "]",
            status="accepted_bounded", review=review, evidence=evidence,
            independent_A_oracle=oracle, subject_bindings=row["subject_bindings"],
            baseline=sources.ref(row["baseline_data"]["path"]),
            schedule=row["baseline_schedule"], comparison_budget=row["comparison_budget"],
            scope=row["reusable_scope"], prerequisites=row["prerequisites"],
            claim_traces=row["retained_claim_traces"], claim_trace_scope=row["claim_trace_scope"],
            claim_trace_pointer="/families/" + family + "/retained_claim_traces",
            claim_trace_record=sources.ref(coverage_path),
            historical_source_bindings="Original validation source identities remain in the pinned record; later code is not retroactively certified by this view.",
            public_support_added=False))
    closeout_name = BASE + "P9-8.3-CloseoutValidation.json"
    closeout = sources.read(closeout_name)
    large = []
    for family in FAMILIES:
        row = closeout["examples"][family]
        large.append(dict(family=family, configuration=sources.ref(row["path"]),
                          numerical_report=sources.ref(row["numerical_report"]),
                          outcomes=row["outcomes"], runtime_accepted=False,
                          next_owners=["P9-8.4g[" + family + "]", "P9-8.4h[" + family + "]"]))

    cells = {r["id"]: r for r in coverage["coverage_cells"] if r["owner"] == "P9-8.4b" and r["applicable"]}
    require(len(cells) == 322, "8.4b required population drift")
    covered, runs = set(), []
    for family, tag, expected_pass, expected_failure in (("C_OS", "COS", 14, 2), ("C_OS", "COSPhaseOne", 2, 0), ("A_OS", "AOS", 16, 0)):
        input_name, result_name = (BASE + "P9-8.4b-" + tag + n + ".json" for n in ("Cases", "Results"))
        inputs, result = sources.read(input_name), sources.read(result_name)
        require(result["manifest_digest"] == inputs["record_digest"], "runtime manifest link drift")
        require(result["user_accepted"] is False and result["aggregate_closed"] is False, "execution flags rewritten")
        cases = []
        for case in result["cases"]:
            ids = case["coverage_binding"]["cell_ids"]
            require(len(ids) == 2 and all(i in cells and cells[i]["family"] == family for i in ids), "foreign runtime coverage")
            passed = case["outcome"] == "passed_named_case"
            require(not passed or case["event_committed"] is True, "success without event")
            if passed:
                require(not covered.intersection(ids), "duplicate success credit")
                covered.update(ids)
            cases.append(dict(case_id=case["case_id"], cells=ids, case_passed=passed,
                              event_committed=case["event_committed"], outcome=case["outcome"], first_failure=case["first_failure"]))
        require(sum(c["case_passed"] for c in cases) == expected_pass and len(cases) - expected_pass == expected_failure,
                "retained case disposition drift")
        review_name = BASE + ("P9-8.4b-AOSRuntimeReview.md" if family == "A_OS" else "P9-8.4b-RuntimeReview.md")
        require("## Scoped user acceptance" in sources.raw(review_name).decode(), "missing scoped runtime acceptance")
        runs.append(dict(family=family, inputs=sources.ref(input_name), results=sources.ref(result_name),
                         record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
                         passed_cases=expected_pass, incomplete_cases=expected_failure, cases=cases,
                         status="accepted_bounded"))
    rows = []
    for family in FAMILIES:
        required = sorted(i for i, r in cells.items() if r["family"] == family)
        accepted = sorted(set(required) & covered)
        rows.append(dict(family=family, required_cells=len(required), accepted_cells=len(accepted),
                         pending_cells=len(required) - len(accepted), required_cell_ids=required,
                         accepted_cell_ids=accepted, status="accepted_bounded" if len(accepted) == len(required) else "pending"))
    children = [dict(work_id="P9-8.4" + key, title=title,
                     status="accepted_inventory_not_execution" if key == "a" else "partial" if key == "b" else "pending",
                     accepted=key == "a") for key, title in CHILDREN.items()]
    # Retain the exact claim/spec/paper associations without promoting their statuses.
    mapping = coverage["scientific_claim_mapping"]
    sources.ref(mapping["paper"]["path"])
    sources.ref(mapping["side_tool_source"])
    for name in ("specs/grc-9-v4-spec.md", "specs/grc-v4-spec.md"):
        sources.ref(name)
    sources.ref(BASE + "P9-8.4a-CoverageReview.md")
    supplements = [sources.ref(BASE + "P9-8.4b-" + name) for name in (
        "AOSOracleInputs.json", "AOSOracleResults.json", "AOSOracleReview.md", "AOSScientificPressure.json")]
    sources.ref(BASE + "P9-8.3-GraphConfigurationGuide.md")
    sources.ref(BASE + "P9-8.3-CatalogValidation.json")
    sources.ref("examples/grcv4/configurations.json")
    # Protect all current transitive inputs of the active 8.4 campaigns without
    # pretending the historical 8.3 validations describe today's source bytes.
    for tag in ("COS", "COSPhaseOne", "AOS"):
        for ref in sources.read(BASE + "P9-8.4b-" + tag + "Cases.json")["source_bindings"]:
            require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                    "8.4 execution source drift: " + ref["path"])
    import phase9_implementation_policy as policy
    scope = sorted(policy.runtime_targets(policy.recorded_acceptance(sources.root)), key=lambda r: r["path"])
    work = sources.read(policy.WORK)
    work_paths = {r["path"] for r in work["entries"]}
    ready, owners = policy.leaf_permissions(sources.root)
    value = dict(schema="phase9_tranche8_evidence_v1", output_class="retained_implementation_evidence_not_forensic_authority",
        checkpoint=CHECKPOINT, mechanics=mechanics, profiles=profiles,
        runtime_scope_snapshot=scope,
        registered_runtime_paths=sorted(r["path"] for r in scope if r["path"] in work_paths),
        dependency_ready_snapshot=ready,
        permitted_paths_snapshot=sorted(r["path"] for r in scope if
            (r["requires_gate"] == "P9-G1" or r["path"] in work_paths) and set(ready) & owners[r["path"]]),
        runtime_scope_note="Display roster only; current policy must independently authenticate permission, dependency readiness and work bindings.",
        configuration=dict(status="accepted_preparation_not_large_runtime", review=sources.ref(closeout_name),
                           outcome_counts=closeout["outcome_counts"], families=large, catalog_size=42),
        coverage=dict(record=sources.ref(coverage_path), children=children, families=rows, runs=runs,
                      oracle_and_pressure=supplements,
                      required_cells=322, accepted_cells=len(covered), pending_cells=len(cells) - len(covered),
                      aggregate_closed=False, other_vector_cells=60, larger_history_cells=20),
        scientific_claim_mapping=mapping,
        verification=dict(level="pinned_sources_and_retained_structure", native_trajectories_rerun=False,
                          interval_equations_recomputed=False, historical_8_3_source_bindings_revalidated_against_current_code=False),
        future=dict(P9_8_5="pending_full_atomicity_campaign", P9_8_6="pending_conformance_review",
                    tranche_9="pending_public_lifecycle_and_compatibility", disabled_cells_pending=40,
                    new_public_support=[], general_ATC_inferred=False, arbitrary_graph_support=False),
        source_refs=sorted(sources.refs.values(), key=lambda r: r["path"]))
    value["view_digest"] = digest(value)
    return value


def browser_source(value):
    return "// Generated from checked retained Tranche 8 evidence; not new authority.\nexport const TRANCHE8_EVIDENCE = " + json.dumps(value, indent=2, ensure_ascii=False) + ";\n"


def checked(root=ROOT):
    value = build(root)
    require((Path(root) / ASSET).read_text() == browser_source(value), "Tranche 8 browser evidence drift")
    return value


def next_work(value):
    c = value["coverage"]
    return (f"Tranche 8: shared 8.1 mechanics and 8.2 allocator accepted; all ten 8.3 bounded profile integrations accepted. "
            f"8.4b has {c['accepted_cells']}/{c['required_cells']} accepted history cells; {c['pending_cells']} remain. "
            "8.4c–i and 8.5/8.6 remain open. Larger-graph preparation is not runtime acceptance; "
            "public lifecycle and forty disabled cells remain Tranche 9 work. No new support or execution permission follows from this view.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "check", "verify-retained"), default="status", nargs="?")
    parser.add_argument("--family", choices=("A_OS", "C_OS"))
    parser.add_argument("--recheck-numerics", action="store_true")
    args = parser.parse_args()
    value = checked()
    if args.action != "verify-retained":
        require(not args.family and not args.recheck_numerics, "numerical/checker options require verify-retained")
        print(json.dumps(value if args.action == "status" else dict(status="passed", view_digest=value["view_digest"],
              level=value["verification"]["level"], accepted_cells=value["coverage"]["accepted_cells"], native_trajectories_rerun=False), indent=2))
        return
    require(args.family is not None, "select one completed family explicitly")
    if args.family == "C_OS":
        require(not args.recheck_numerics, "C_OS retained checker always recomputes its dense comparisons, not native trajectories")
        commands = [[sys.executable, str(ROOT / HERE / "p984b_cos_successor.py"), "--check-retained", *extra] for extra in (["--original"], [])]
    else:
        commands = [[sys.executable, str(ROOT / HERE / "p984b_aos_runtime.py"), "--check-retained",
                     *(["--recheck-numerics"] if args.recheck_numerics else [])]]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
