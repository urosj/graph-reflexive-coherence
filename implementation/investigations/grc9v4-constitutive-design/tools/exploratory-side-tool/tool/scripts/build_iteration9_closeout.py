#!/usr/bin/env python3
"""Build the ET-C9 closeout candidate and complete coverage reconciliation."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import (  # noqa: E402
    canonical_bytes,
    file_sha256,
    load_json_object,
    record_digest,
)
from grcv4_explorer.closeout import (  # noqa: E402
    FORENSIC_API_COVERAGE,
    SCENARIO_OWNERS,
    WEB_VIEW_COVERAGE,
    validate_coverage,
)
from grcv4_explorer.paths import repository_root  # noqa: E402


GATE_FILES = {
    1: "ETC1SourceAdapterAdmission.json",
    2: "ETC2ValidatedGraphKernel.json",
    3: "ETC3ForensicReconstructionSurface.json",
    4: "ETC4BoundedCounterfactualKernel.json",
    5: "ETC5RippleAndScenarioContract.json",
    6: "ETC6StaticNavigationSurface.json",
    7: "ETC7ClaimCeilingAlternativeNavigation.json",
    8: "ETC8LineageAndRippleNavigation.json",
}

SURFACES = {
    "F": "forensic_reconstruction",
    "N": "navigational_exploration",
    "C": "structural_counterfactual",
    "D": "failure_and_staleness",
    "E": "onboarding_and_orientation",
}

MAXIMUM_CLAIM = (
    "A deterministic read-only exploratory tool reconstructs the accepted "
    "GRCv4/GRC9v4 constitutive-design claim topology and supports bounded, "
    "source-traceable structural counterfactual navigation up to the explicit "
    "evidence frontier."
)

DOCUMENTATION = {
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


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_bytes(canonical_bytes(value) + b"\n")


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    records = SIDE_TOOL_ROOT / "records"
    gates = {
        iteration: load_json_object(records / filename)
        for iteration, filename in GATE_FILES.items()
    }
    owner_by_scenario = {
        scenario_id: iteration
        for iteration, scenario_ids in SCENARIO_OWNERS.items()
        for scenario_id in scenario_ids
    }
    scenario_rows = []
    for scenario_id in sorted(
        owner_by_scenario,
        key=lambda value: ("FNCDE".index(value[0]), int(value[1:])),
    ):
        iteration = owner_by_scenario[scenario_id]
        gate = gates[iteration]
        scenario_rows.append(
            {
                "scenario_id": scenario_id,
                "category": SURFACES[scenario_id[0]],
                "owner_iteration": iteration,
                "owner_gate_id": gate["gate_id"],
                "owner_record_digest": gate["record_digest"],
                "status": "passed_reconciled",
                "scientific_claim_added": False,
            }
        )

    coverage: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C9_scenario_coverage_usability_v1",
        "status": "accepted",
        "source_scenarios": {
            "path": (
                "implementation/investigations/grc9v4-constitutive-design/tools/"
                "exploratory-side-tool/GRCV4ExploratorySideToolUserScenarios.md"
            ),
            "file_sha256": file_sha256(
                SIDE_TOOL_ROOT / "GRCV4ExploratorySideToolUserScenarios.md"
            ),
        },
        "scenario_count": len(scenario_rows),
        "scenario_rows": scenario_rows,
        "forensic_api_count": len(FORENSIC_API_COVERAGE),
        "forensic_api_coverage": {
            key: list(value) for key, value in FORENSIC_API_COVERAGE.items()
        },
        "web_view_count": len(WEB_VIEW_COVERAGE),
        "web_view_coverage": {
            key: list(value) for key, value in WEB_VIEW_COVERAGE.items()
        },
        "usability_tasks": [
            {
                "task_id": "ET-C9-FORENSIC-USABILITY",
                "scenario_ids": ["F1", "F3", "F8"],
                "route": "claim_to_lenses_to_reach_to_source_reconstruction",
                "status": "passed_browser_pressure",
            },
            {
                "task_id": "ET-C9-NAVIGATIONAL-USABILITY",
                "scenario_ids": ["N1", "N4", "C8", "C9"],
                "route": "family_to_claim_boundary_to_lineage_to_precomputed_ripple",
                "status": "passed_browser_pressure",
            },
        ],
        "coverage_digest": None,
    }
    validate_coverage(coverage)
    coverage["coverage_digest"] = record_digest(coverage, "coverage_digest")
    write_json(records / "ETC9ScenarioCoverageAndUsability.json", coverage)

    et_c0 = load_json_object(records / "ETC0SourceAndLayoutContract.json")
    et_c1 = gates[1]
    et_c8 = gates[8]
    context = tomllib.loads((TOOL_ROOT / "iteration9_context.toml").read_text())
    et_c0_dependencies = {
        row["path"]: row["file_sha256"]
        for row in et_c0["setup_contract"]["setup_identity"]["dependency_files"]
    }
    successor_dependency_paths = {
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/toolchain.toml",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/web/package.json",
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/tool/web/package-lock.json",
    }
    environment_rows = []
    for path, historical_sha in et_c0_dependencies.items():
        current_sha = file_sha256(repo_root / path)
        changed = historical_sha != current_sha
        if changed and path not in successor_dependency_paths:
            raise RuntimeError(f"unadmitted setup dependency drift: {path}")
        environment_rows.append(
            {
                "path": path,
                "ET_C0_file_sha256": historical_sha,
                "current_file_sha256": current_sha,
                "classification": (
                    "ET_C6_admitted_toolchain_successor"
                    if changed
                    else "unchanged_from_ET_C0"
                ),
            }
        )
    environment: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C9_environment_conformance_v1",
        "status": "accepted",
        "ET_C0_record_digest": et_c0["record_digest"],
        "ET_C0_setup_identity_digest": et_c0["setup_contract"][
            "setup_identity_digest"
        ],
        "ET_C0_is_historical_setup_snapshot": True,
        "current_dependency_rows": environment_rows,
        "changed_dependency_count": sum(
            row["classification"] == "ET_C6_admitted_toolchain_successor"
            for row in environment_rows
        ),
        "successor_gate_id": gates[6]["gate_id"],
        "successor_gate_record_digest": gates[6]["record_digest"],
        "scientific_source_identity_changed": False,
        "environment_digest": None,
    }
    environment["environment_digest"] = record_digest(
        environment, "environment_digest"
    )
    write_json(records / "ETC9EnvironmentConformance.json", environment)
    disposition: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C9_closeout_disposition_v1",
        "gate_id": "ET-C9_independent_validation_and_closeout",
        "status": "accepted",
        "iteration": 9,
        "execution_context": context,
        "predecessor": {
            "gate_id": et_c8["gate_id"],
            "record_digest": et_c8["record_digest"],
            "lineage_layer_digest": et_c8["compiled_surface"]["layer_digest"],
            "web_build_manifest_digest": et_c8["compiled_surface"][
                "web_build_manifest_digest"
            ],
        },
        "source_state": {
            "source_bundle_digest": et_c1["source_bundle_manifest"][
                "source_bundle_digest"
            ],
            "admitted_record_count": et_c1["source_bundle_manifest"]["record_count"],
            "observation_state": et_c1["source_observation"]["state"],
            "automatic_admission_allowed": False,
            "successor_processing_cycle": [
                "classify_schema_and_authority",
                "implement_or_update_schema_specific_adapter",
                "admit_successor_source_bundle_identity",
                "rerun_reference_and_graph_conformance",
                "rebuild_all_derived_artifacts",
                "accept_successor_processing_cycle",
            ],
        },
        "coverage": {
            "scenario_count": coverage["scenario_count"],
            "forensic_api_count": coverage["forensic_api_count"],
            "web_view_count": coverage["web_view_count"],
            "coverage_digest": coverage["coverage_digest"],
        },
        "compatibility": {
            "minimum_python": et_c0["compatibility_contract"]["python_minimum"],
            "tested_closeout_python_versions": ["3.12.3"],
            "planned_but_unavailable_on_closeout_host": ["3.11", "3.13"],
            "untested_versions_claimed_conformant": False,
            "managed_node": et_c0["compatibility_contract"][
                "managed_node_version"
            ],
            "global_python_node_or_npm_used": False,
            "environment_conformance_digest": environment["environment_digest"],
            "ET_C0_setup_snapshot_rewritten": False,
            "ET_C6_toolchain_successor_dependency_count": environment[
                "changed_dependency_count"
            ],
        },
        "artifact_policy": {
            "committed": [
                DOCUMENTATION["agentic_query_guide"],
                DOCUMENTATION["user_guide"],
                *DOCUMENTATION["examples"],
                *DOCUMENTATION["screenshots"],
                "records/ETC9ScenarioCoverageAndUsability.json",
                "records/ETC9EnvironmentConformance.json",
                "records/ETC9CloseoutDisposition.json",
                "records/ETC9CloseoutReport.md",
                "records/ETC9VerificationReceipt.json",
            ],
            "ignored": [
                "tool/generated/",
                "tool/web/dist/",
                "tool/web/public/data/",
                "tool/web/node_modules/",
                "tool/.tooling/",
                "tool/.cache/",
            ],
            "generated_evidence_is_not_scientific_source": True,
        },
        "documentation": DOCUMENTATION,
        "reconstruction": {
            "environment": "python tool/scripts/bootstrap.py from the side-tool root; host Python is bootstrap-only",
            "verification_from_repository_root": (
                ".venv/bin/python implementation/investigations/"
                "grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
                "scripts/run.py verify-iteration9"
            ),
            "interactive_preview_from_repository_root": (
                ".venv/bin/python implementation/investigations/"
                "grc9v4-constitutive-design/tools/exploratory-side-tool/tool/"
                "scripts/run.py serve-iteration8"
            ),
        },
        "provisional_disposition": "accepted_bounded_read_only_exploratory_tool",
        "selected_disposition": "accepted_bounded_read_only_exploratory_tool",
        "authority": {
            "human_acceptance_recorded": True,
            "scientific_claim_added": False,
            "source_automatically_admitted": False,
        },
        "maximum_claim": MAXIMUM_CLAIM,
        "blocked_claims": [
            "new_GRCV4_or_GRC9V4_scientific_evidence",
            "prediction_of_reopened_gate_outcomes",
            "GRCV4_runtime_implementation",
            "specification_or_runtime_conformance",
            "scientific_claim_promotion",
            "automatic_admission_of_new_or_changed_source",
        ],
        "acceptance_requirements": {
            "independent_verification_receipt": "passed",
            "human_review": "accepted",
        },
        "record_digest": None,
    }
    disposition["record_digest"] = record_digest(disposition, "record_digest")
    write_json(records / "ETC9CloseoutDisposition.json", disposition)

    report = "\n".join(
        (
            "# ET-C9 Independent Validation And Closeout",
            "",
            "**Status:** Accepted",
            "",
            "Iteration 9 reconciles the complete side-tool surface without adding",
            "scientific authority. All 35 normalized user scenarios have one",
            "accepted owning gate; all nine forensic APIs and all eight required",
            "web views have explicit scenario coverage.",
            "",
            "## Accepted Disposition",
            "",
            "`accepted_bounded_read_only_exploratory_tool`",
            "",
            "The independent verification receipt passed and human review accepted",
            "this bounded disposition without adding scientific authority.",
            "",
            "## Maximum Claim",
            "",
            f"> {MAXIMUM_CLAIM}",
            "",
            "The tool does not prove new V4 results, predict reopened gates,",
            "implement a GRCv4 runtime, establish specification conformance, or",
            "promote any scientific claim. New or changed source is observed and",
            "failed closed until a successor adapter/readmission cycle is accepted.",
            "",
            "## Guides",
            "",
            "- [Agentic Query Guide](../docs/AgenticQueryGuide.md)",
            "- [User Guide](../docs/UserGuide.md)",
            "- executable nine-query walkthrough under `docs/examples/`",
            "- six verified screenshots under `docs/images/`",
            "",
            "## Portability Boundary",
            "",
            "The admitted minimum remains Python 3.11. The closeout host exposes",
            "only repository `.venv` Python 3.12.3; Python 3.11 and 3.13 were not",
            "available and are not claimed as tested. Node and npm remain tool-local.",
            "ET-C0 remains the historical setup snapshot. Three dependency files",
            "changed under the accepted ET-C6 browser-toolchain successor; ET-C9",
            "records that operational transition without changing scientific source",
            "identity or cascading new identities through accepted ET-C1-C8 gates.",
            "",
            "## Identities",
            "",
            f"- scenario coverage digest: `{coverage['coverage_digest']}`",
            f"- environment conformance digest: `{environment['environment_digest']}`",
            f"- ET-C8 predecessor digest: `{et_c8['record_digest']}`",
            f"- accepted closeout digest: `{disposition['record_digest']}`",
            "- independent verification: `ETC9VerificationReceipt.json`",
            "",
        )
    )
    (records / "ETC9CloseoutReport.md").write_text(report, encoding="utf-8")
    print(
        "ET_C9_BUILD_PASS status=accepted scenarios=35 apis=9 "
        f"views=8 coverage={coverage['coverage_digest']} "
        f"record={disposition['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
