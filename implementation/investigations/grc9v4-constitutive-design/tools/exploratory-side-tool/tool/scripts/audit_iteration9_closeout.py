#!/usr/bin/env python3
"""Independently audit ET-C9 coverage, authority, and source boundaries."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import (  # noqa: E402
    file_sha256,
    load_json_object,
    record_digest,
)
from grcv4_explorer.paths import repository_root  # noqa: E402


checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise RuntimeError(f"ET-C9 independent audit failed: {message}")


def expected_scenarios() -> set[str]:
    return {
        *(f"F{index}" for index in range(1, 10)),
        *(f"N{index}" for index in range(1, 7)),
        *(f"C{index}" for index in range(1, 10)),
        *(f"D{index}" for index in range(1, 8)),
        *(f"E{index}" for index in range(1, 5)),
    }


def expected_owners() -> dict[str, int]:
    rows = {
        1: ("D1",),
        2: ("F9",),
        3: ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "E3", "E4"),
        4: ("C1", "C4", "C5", "C6", "D2", "D3", "D4", "D5", "D6"),
        5: ("C2", "C3", "C7", "C9"),
        6: ("N1", "N2", "N3"),
        7: ("N5", "N6", "D7", "E2"),
        8: ("N4", "C8", "E1"),
    }
    return {
        scenario_id: iteration
        for iteration, scenario_ids in rows.items()
        for scenario_id in scenario_ids
    }


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    records = SIDE_TOOL_ROOT / "records"
    coverage = load_json_object(records / "ETC9ScenarioCoverageAndUsability.json")
    environment = load_json_object(records / "ETC9EnvironmentConformance.json")
    disposition = load_json_object(records / "ETC9CloseoutDisposition.json")
    check(
        coverage["coverage_digest"] == record_digest(coverage, "coverage_digest"),
        "coverage digest",
    )
    check(
        disposition["record_digest"] == record_digest(disposition, "record_digest"),
        "disposition digest",
    )
    check(
        environment["environment_digest"]
        == record_digest(environment, "environment_digest"),
        "environment digest",
    )
    check(coverage["status"] == "accepted", "coverage lifecycle")
    check(environment["status"] == "accepted", "environment lifecycle")
    check(disposition["status"] == "accepted", "accepted lifecycle")
    check(
        disposition["selected_disposition"]
        == "accepted_bounded_read_only_exploratory_tool",
        "selected bounded disposition",
    )
    check(
        disposition["authority"]
        == {
            "human_acceptance_recorded": True,
            "scientific_claim_added": False,
            "source_automatically_admitted": False,
        },
        "human acceptance authority",
    )
    check(
        disposition["acceptance_requirements"]
        == {
            "independent_verification_receipt": "passed",
            "human_review": "accepted",
        },
        "acceptance requirements",
    )
    check(
        all(
            row["status"] == "passed_browser_pressure"
            for row in coverage["usability_tasks"]
        ),
        "accepted usability pressure",
    )

    scenario_doc = SIDE_TOOL_ROOT / "GRCV4ExploratorySideToolUserScenarios.md"
    documented = re.findall(
        r"^### ([FNCDE]\d+)\.", scenario_doc.read_text(encoding="utf-8"), re.M
    )
    expected = expected_scenarios()
    check(len(documented) == 35, "documented scenario count")
    check(len(set(documented)) == 35, "documented scenario uniqueness")
    check(set(documented) == expected, "documented scenario population")
    check(
        coverage["source_scenarios"]["file_sha256"] == file_sha256(scenario_doc),
        "scenario document identity",
    )

    rows = coverage["scenario_rows"]
    check(len(rows) == 35, "compiled scenario count")
    check({row["scenario_id"] for row in rows} == expected, "compiled population")
    owners = expected_owners()
    check(set(owners) == expected, "owner population")
    gate_files = {
        1: "ETC1SourceAdapterAdmission.json",
        2: "ETC2ValidatedGraphKernel.json",
        3: "ETC3ForensicReconstructionSurface.json",
        4: "ETC4BoundedCounterfactualKernel.json",
        5: "ETC5RippleAndScenarioContract.json",
        6: "ETC6StaticNavigationSurface.json",
        7: "ETC7ClaimCeilingAlternativeNavigation.json",
        8: "ETC8LineageAndRippleNavigation.json",
    }
    gates = {
        iteration: load_json_object(records / filename)
        for iteration, filename in gate_files.items()
    }
    for row in rows:
        scenario_id = row["scenario_id"]
        iteration = owners[scenario_id]
        check(row["owner_iteration"] == iteration, f"owner {scenario_id}")
        check(row["owner_gate_id"] == gates[iteration]["gate_id"], f"gate {scenario_id}")
        check(
            row["owner_record_digest"] == gates[iteration]["record_digest"],
            f"gate digest {scenario_id}",
        )
        check(row["status"] == "passed_reconciled", f"status {scenario_id}")
        check(row["scientific_claim_added"] is False, f"authority {scenario_id}")

    forensic_path = TOOL_ROOT / "src/grcv4_explorer/forensic.py"
    tree = ast.parse(forensic_path.read_text(encoding="utf-8"))
    exported_functions = {
        node.name for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    expected_apis = {
        "gate_act",
        "debt_lifecycle",
        "reconstruction_path",
        "candidate_career",
        "pruned_choices_at",
        "negative_claims",
        "object_dependents",
        "contract_provenance",
        "gate_contribution",
    }
    check(set(coverage["forensic_api_coverage"]) == expected_apis, "API manifest")
    check(expected_apis <= exported_functions, "API implementation")
    for api, scenario_ids in coverage["forensic_api_coverage"].items():
        check(bool(scenario_ids), f"API exercised {api}")
        check(set(scenario_ids) <= expected, f"API scenario identity {api}")

    expected_documentation = {
        "agentic_query_guide": "docs/AgenticQueryGuide.md",
        "user_guide": "docs/UserGuide.md",
        "examples": ["docs/examples/agentic_query_walkthrough.py"],
        "screenshots": [
            "docs/images/claim-locks.png",
            "docs/images/explore-workbench.png",
            "docs/images/mobile-lineage-and-fork.png",
            "docs/images/source-lineage.png",
            "docs/images/speculative-alternatives.png",
            "docs/images/speculative-fork.png",
        ],
    }
    check(
        disposition["documentation"] == expected_documentation,
        "documentation manifest",
    )
    committed = set(disposition["artifact_policy"]["committed"])
    expected_committed_docs = {
        expected_documentation["agentic_query_guide"],
        expected_documentation["user_guide"],
        *expected_documentation["examples"],
        *expected_documentation["screenshots"],
    }
    check(expected_committed_docs <= committed, "documentation artifact policy")
    agent_guide = (SIDE_TOOL_ROOT / expected_documentation["agentic_query_guide"]).read_text(
        encoding="utf-8"
    )
    user_guide = (SIDE_TOOL_ROOT / expected_documentation["user_guide"]).read_text(
        encoding="utf-8"
    )
    for api in expected_apis:
        check(f"`{api}`" in agent_guide, f"agent guide API {api}")
    for required in (
        "load_forensic_context",
        "agentic_query_walkthrough.py",
        "source_ref",
        "edge_refs",
        "result_statuses",
        "unknown_beyond_evidence_frontier",
        "new_unprocessed_source_available",
    ):
        check(required in agent_guide, f"agent guide boundary {required}")
    for index in range(1, 13):
        check(
            f"Use Case {index}:" in agent_guide,
            f"agent guide complete use case {index}",
        )
    for required in (
        "Explore",
        "Lineage",
        "Source",
        "Speculative",
        "evidence frontier",
        "discover-sources",
    ):
        check(required in user_guide, f"user guide workflow {required}")
    for index in range(1, 14):
        check(
            f"Use Case {index}:" in user_guide,
            f"user guide complete use case {index}",
        )
    for text, label in ((agent_guide, "agent"), (user_guide, "user")):
        for term in (
            "spine",
            "companion branch",
            "bearing debt",
            "claim ceiling",
            "provenance hardening",
            "resolved negative",
        ):
            check(term in text.lower(), f"{label} guide glossary {term}")
        check(
            "../GRCV4ExploratorySideToolUserScenarios.md" in text,
            f"{label} guide canonical scenario contract",
        )
        check("serve-iteration8" in text, f"{label} guide ET-C8 browser command")
        check("verify-iteration9" in text, f"{label} guide ET-C9 verifier command")
        for notebook_term in (
            "forensic_recipes.ipynb",
            "notebook-iteration3",
            "normative-claim.json",
            "candidate-B.json",
            "counterfactual-authoring notebook",
        ):
            check(
                notebook_term in text,
                f"{label} guide notebook boundary {notebook_term}",
            )
        check(
            "Jupyter" in text and "dependency" in text,
            f"{label} guide Jupyter dependency boundary",
        )
    check(
        "between theory, substrate design, and code" in user_guide,
        "user guide theory substrate code boundary",
    )
    check(
        "## All 35 Governed Scenario Paths" not in user_guide,
        "user guide canonical scenario catalog not duplicated",
    )
    check(
        "## Dispatch For All 35 Governed Scenarios" not in agent_guide,
        "agent guide canonical scenario catalog not duplicated",
    )
    for relative in expected_documentation["examples"]:
        example = SIDE_TOOL_ROOT / relative
        check(example.is_file(), f"documentation example exists {relative}")
        example_text = example.read_text(encoding="utf-8")
        check(
            "AGENTIC_QUERY_WALKTHROUGH_PASS" in example_text,
            f"documentation example terminal result {relative}",
        )
        for api in expected_apis:
            check(api in example_text, f"documentation example API {api}")
    for text, label in ((agent_guide, "agent"), (user_guide, "user")):
        check("/home/" not in text, f"{label} guide absolute home path")
        check("Documents/RC-github" not in text, f"{label} guide local path")
    image_links = {
        f"docs/{value.removeprefix('./')}"
        for value in re.findall(r"!\[[^]]*\]\((\./images/[^)]+)\)", user_guide)
    }
    check(
        image_links == set(expected_documentation["screenshots"]),
        "user guide screenshot links",
    )
    for relative in expected_documentation["screenshots"]:
        screenshot = SIDE_TOOL_ROOT / relative
        check(screenshot.is_file(), f"screenshot exists {relative}")
        check(screenshot.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), f"PNG {relative}")

    expected_views = {
        "focused_navigator",
        "family_navigation",
        "triangulation",
        "dependency_reach",
        "claim_ceiling",
        "alternative_layer",
        "lineage_scrubber",
        "ripple_view",
    }
    check(set(coverage["web_view_coverage"]) == expected_views, "web view manifest")
    for view, scenario_ids in coverage["web_view_coverage"].items():
        check(bool(scenario_ids), f"view exercised {view}")
        check(set(scenario_ids) <= expected, f"view scenario identity {view}")

    app_source = (TOOL_ROOT / "web/src/app.js").read_text(encoding="utf-8")
    all_js = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((TOOL_ROOT / "web/src").glob("*.js"))
    )
    for required in (
        'data-surface="explorer"',
        'data-surface="lineage"',
        'data-tab="lenses"',
        'data-tab="reach"',
        'data-tab="ceilings"',
        'data-view="locks"',
        'data-view="alternatives"',
        "lineage-scrubber",
        "scenario-select",
    ):
        check(required in app_source, f"web surface {required}")
    for forbidden in (
        "compileRipple",
        "compile_ripple",
        "evaluateMutation",
        "evaluate_mutation",
        "computeFrontier",
        "compute_frontier",
        "promotion_allowed = true",
        "browser_may_predict_rerun = true",
    ):
        check(forbidden not in all_js, f"browser authority {forbidden}")

    et_c1 = gates[1]
    check(
        et_c1["source_observation"]["state"] == "current_bundle_exact",
        "source observation",
    )
    check(
        et_c1["source_observation"]["automatic_admission_allowed"] is False,
        "automatic admission",
    )
    check(
        disposition["source_state"]["successor_processing_cycle"]
        == [
            "classify_schema_and_authority",
            "implement_or_update_schema_specific_adapter",
            "admit_successor_source_bundle_identity",
            "rerun_reference_and_graph_conformance",
            "rebuild_all_derived_artifacts",
            "accept_successor_processing_cycle",
        ],
        "successor processing cycle",
    )
    check(
        disposition["provisional_disposition"]
        == "accepted_bounded_read_only_exploratory_tool",
        "bounded candidate disposition",
    )
    check(len(disposition["blocked_claims"]) == 6, "blocked claim population")
    check(
        disposition["compatibility"]["tested_closeout_python_versions"]
        == ["3.12.3"],
        "tested Python range",
    )
    check(
        disposition["compatibility"]["untested_versions_claimed_conformant"]
        is False,
        "untested Python boundary",
    )
    check(environment["ET_C0_is_historical_setup_snapshot"] is True, "ET-C0 snapshot")
    check(environment["changed_dependency_count"] == 3, "successor dependency count")
    check(
        environment["successor_gate_id"] == gates[6]["gate_id"],
        "ET-C6 successor gate",
    )
    check(
        environment["scientific_source_identity_changed"] is False,
        "environment/scientific boundary",
    )
    for row in environment["current_dependency_rows"]:
        check(
            row["current_file_sha256"] == file_sha256(repo_root / row["path"]),
            f"current dependency identity {row['path']}",
        )
    print(f"ET_C9_INDEPENDENT_AUDIT_PASS checks={checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
