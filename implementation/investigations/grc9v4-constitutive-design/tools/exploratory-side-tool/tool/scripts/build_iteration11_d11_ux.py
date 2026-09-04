#!/usr/bin/env python3
"""Build the ET-C11 D11 notebook/browser presentation candidate."""

from __future__ import annotations

import json
import shutil
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
from grcv4_explorer.successor import (  # noqa: E402
    D11_FORENSIC_ADMISSION,
    load_successor_forensic_context,
)
from grcv4_explorer.successor_ux import (  # noqa: E402
    D11_UX_BUNDLE,
    D11_UX_CANDIDATE,
    D11_UX_CANDIDATE_SCHEMA,
    D11_UX_WEB_MANIFEST,
    D11_UX_WEB_MANIFEST_SCHEMA,
    build_d11_ux_bundle,
    validate_d11_ux_bundle,
)
from grcv4_explorer.tooling import managed_node, run_managed_node  # noqa: E402


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")

    records = SIDE_TOOL_ROOT / "records"
    admission = load_json_object(records / D11_FORENSIC_ADMISSION)
    context = load_successor_forensic_context(repo_root, SIDE_TOOL_ROOT)
    bundle = build_d11_ux_bundle(context, admission)
    validate_d11_ux_bundle(bundle, admission)
    bundle_path = records / D11_UX_BUNDLE
    write_json(bundle_path, bundle)

    public_data = TOOL_ROOT / "web/public/data"
    public_data.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bundle_path, public_data / D11_UX_BUNDLE)
    vite = TOOL_ROOT / "web/node_modules/vite/bin/vite.js"
    run_managed_node(vite, ("build",))

    dist = TOOL_ROOT / "web/dist"
    dist_files = [path for path in sorted(dist.rglob("*")) if path.is_file()]
    web_manifest: dict[str, Any] = {
        "schema": D11_UX_WEB_MANIFEST_SCHEMA,
        "status": "candidate",
        "bundle_digest": bundle["bundle_digest"],
        "predecessor_ET_C10_record_digest": admission["record_digest"],
        "toolchain": {
            "frontend": "vanilla_ES_modules",
            "node": managed_node().parent.parent.name.removeprefix("v"),
            "vite": "7.1.3",
            "playwright": "1.55.0",
        },
        "files": [
            {
                "path": path.relative_to(dist).as_posix(),
                "sha256": file_sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in dist_files
        ],
        "file_count": len(dist_files),
        "manifest_digest": None,
    }
    web_manifest["manifest_digest"] = record_digest(web_manifest, "manifest_digest")
    write_json(records / D11_UX_WEB_MANIFEST, web_manifest)

    notebook_path = TOOL_ROOT / "notebooks/d11_successor_recipes.ipynb"
    scenario_path = SIDE_TOOL_ROOT / "GRCV4ExploratorySideToolD11UXScenarios.md"
    candidate: dict[str, Any] = {
        "schema": D11_UX_CANDIDATE_SCHEMA,
        "gate_id": "ET-C11-D11-UX",
        "status": "candidate",
        "predecessor": {
            "gate_id": admission["gate_id"],
            "record_digest": admission["record_digest"],
            "graph_digest": admission["graph_digest"],
        },
        "compiled_surface": {
            "bundle_digest": bundle["bundle_digest"],
            "web_build_manifest_digest": web_manifest["manifest_digest"],
            "catalog_count": bundle["population_counts"]["catalog"],
            "forensic_API_output_count": bundle["population_counts"][
                "forensic_API_outputs"
            ],
            "source_bound_node_projection_count": bundle["population_counts"][
                "source_bound_node_projections"
            ],
            "notebook_recipe_count": 6,
            "browser_view_count": 3,
        },
        "source_files": {
            "notebook": {
                "path": notebook_path.relative_to(repo_root).as_posix(),
                "sha256": file_sha256(notebook_path),
            },
            "scenarios": {
                "path": scenario_path.relative_to(repo_root).as_posix(),
                "sha256": file_sha256(scenario_path),
            },
        },
        "authority": {
            "accepted_D11_source_authority_changed": False,
            "historical_ET_C0_through_ET_C9_artifacts_rewritten": False,
            "notebook_or_browser_is_evidence_engine": False,
            "browser_scientific_inference": False,
            "paper_specification_or_runtime_propagation_verified": False,
            "GRC9_or_GRC9V3_change_authorized": False,
        },
        "acceptance_requirements": {
            "deterministic_double_rebuild": "pending_verification",
            "Python_API_notebook_browser_trace_identity": "pending_verification",
            "Node_component_tests": "pending_verification",
            "Playwright_desktop_mobile": "pending_verification",
            "human_review": "pending",
        },
        "record_digest": None,
    }
    candidate["record_digest"] = record_digest(candidate, "record_digest")
    write_json(records / D11_UX_CANDIDATE, candidate)
    print(
        "ET_C11_D11_UX_BUILD_PASS "
        f"catalog={bundle['population_counts']['catalog']} "
        f"API_outputs={bundle['population_counts']['forensic_API_outputs']} "
        f"bundle={bundle['bundle_digest']} web={web_manifest['manifest_digest']} "
        f"candidate={candidate['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
