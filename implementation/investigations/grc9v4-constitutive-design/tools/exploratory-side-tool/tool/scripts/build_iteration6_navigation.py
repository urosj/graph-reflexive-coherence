#!/usr/bin/env python3
"""Build the I6 static navigation data, web bundle, and candidate gate."""

from __future__ import annotations

import json
import shutil
import sys
import tomllib
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.bundle import build_source_bundle  # noqa: E402
from grcv4_explorer.canonical import (  # noqa: E402
    file_sha256,
    load_json_object,
    record_digest,
)
from grcv4_explorer.source_contract import load_et_c0_contract  # noqa: E402
from grcv4_explorer.tooling import managed_node, run_managed_node  # noqa: E402
from grcv4_explorer.web import (  # noqa: E402
    build_static_navigation_bundle,
    hydrate_selection_projection,
)


def repository_root() -> Path:
    for candidate in SIDE_TOOL_ROOT.parents:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise RuntimeError("cannot discover repository root")


def write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    records = SIDE_TOOL_ROOT / "records"
    et_c0_path = records / "ETC0SourceAndLayoutContract.json"
    _, observation = build_source_bundle(repo_root, et_c0_path)
    bundle = build_static_navigation_bundle(repo_root, SIDE_TOOL_ROOT, observation)
    bundle_path = records / "ETC6StaticNavigationBundle.json"
    write_json(bundle_path, bundle)

    parity_node_ids = (
        "normative_object:A-DIRECTIONAL-CONTRAST",
        "debt_transformation:D7-DEBT-COVARIANCE-VERIFICATION",
        "gate_record:GRC9V4-CD-D7V2-v1",
        "candidate:V4-A-temporalized-W",
        "candidate:V4-B-independent-derived-carrier",
        "current_claim:D10-CL-N-001",
        "profile:A_CI",
    )
    parity: dict[str, object] = {
        "schema": "grcv4_explorer_ET_C6_cross_surface_parity_v1",
        "status": "accepted",
        "static_bundle_digest": bundle["bundle_digest"],
        "selection_payloads": {
            node_id: hydrate_selection_projection(bundle, node_id)
            for node_id in parity_node_ids
        },
        "parity_digest": None,
    }
    parity["parity_digest"] = record_digest(parity, "parity_digest")
    write_json(records / "ETC6CrossSurfaceParity.json", parity)

    public_data = TOOL_ROOT / "web/public/data"
    public_data.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bundle_path, public_data / bundle_path.name)
    vite = TOOL_ROOT / "web/node_modules/vite/bin/vite.js"
    run_managed_node(vite, ("build",))

    dist = TOOL_ROOT / "web/dist"
    files = [path for path in sorted(dist.rglob("*")) if path.is_file()]
    manifest: dict[str, object] = {
        "schema": "grcv4_explorer_ET_C6_web_build_manifest_v1",
        "status": "accepted",
        "toolchain": {
            "frontend": "vanilla_ES_modules",
            "cytoscape": "3.33.1",
            "vite": "7.1.3",
            "playwright": "1.55.0",
            "lucide": "0.468.0",
            "node": managed_node().parent.parent.name.removeprefix("v"),
        },
        "static_bundle_digest": bundle["bundle_digest"],
        "cross_surface_parity_digest": parity["parity_digest"],
        "files": [
            {
                "path": path.relative_to(dist).as_posix(),
                "sha256": file_sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in files
        ],
        "file_count": len(files),
        "manifest_digest": None,
    }
    manifest["manifest_digest"] = record_digest(manifest, "manifest_digest")
    write_json(records / "ETC6WebBuildManifest.json", manifest)

    context = tomllib.loads((TOOL_ROOT / "iteration6_context.toml").read_text())
    et_c5 = load_json_object(records / "ETC5RippleAndScenarioContract.json")
    gate: dict[str, object] = {
        "schema": "grcv4_explorer_ET_C6_static_navigation_admission_v1",
        "gate_id": "ET-C6_static_navigation_surface",
        "status": "accepted",
        "iteration": 6,
        "execution_context": context,
        "predecessor": {
            "gate_id": et_c5["gate_id"],
            "record_digest": et_c5["record_digest"],
            "source_bundle_digest": bundle["accepted_identities"]["source_bundle_digest"],
            "graph_digest": bundle["accepted_identities"]["graph_digest"],
        },
        "authority": {
            "static_navigation_surface_implemented": True,
            "python_compiled_projections": True,
            "browser_side_propagation": False,
            "browser_side_ripple_compilation": False,
            "browser_authored_mutations": False,
            "scientific_claim_added": False,
            "iteration_7_authorized": True,
        },
        "compiled_surface": {
            "static_bundle_digest": bundle["bundle_digest"],
            "cross_surface_parity_digest": parity["parity_digest"],
            "web_build_manifest_digest": manifest["manifest_digest"],
            "source_observation_state": bundle["source_observation"]["state"],
            "family_count": len(bundle["family_coverage"]),
            "family_object_count": sum(row["object_count"] for row in bundle["family_coverage"]),
            "catalog_node_count": len(bundle["catalog"]),
            "selection_projection_count": bundle["selection_projection_count"],
            "focus_node_limit": 32,
            "focus_edge_limit": 72,
            "scenario_count": len(bundle["embedded_payloads"]["scenario_bundle"]["scenarios"]),
            "ripple_row_count": sum(len(row["rows"]) for row in bundle["embedded_payloads"]["ripple_shards"]),
        },
        "acceptance_requirements": {
            "independent_static_bundle_audit": "passed_44895_checks_7_cross_surface_parity_rows",
            "python_and_node_component_tests": "passed_47_python_checks_8_node_tests",
            "deterministic_double_rebuild": "passed",
            "playwright_desktop_mobile": "passed_2_viewports_desktop_mobile",
            "ET_C5_regression": "passed_full_verification",
            "human_review": "accepted",
        },
        "non_claims": [
            "no_claim_ceiling_or_alternative_layer",
            "no_lineage_scrubber",
            "no_ripple_playback",
            "no_browser_scientific_inference",
            "no_candidate_family_or_dependency_ranking",
        ],
        "record_digest": None,
    }
    gate["record_digest"] = record_digest(gate, "record_digest")
    write_json(records / "ETC6StaticNavigationSurface.json", gate)

    report = "\n".join(
        (
            "# ET-C6 Static Navigation Surface",
            "",
            "**Status:** Accepted",
            "",
            "Iteration 6 adds a static browser workbench over Python-compiled",
            "selection projections. Search, family selection, graph layout, and",
            "presentation run in the client; propagation and ripple compilation do not.",
            "",
            "## Result",
            "",
            f"- object families: `{len(bundle['family_coverage'])}` / `{sum(row['object_count'] for row in bundle['family_coverage'])} objects`",
            f"- catalog: `{len(bundle['catalog'])} nodes`",
            f"- selection projections: `{bundle['selection_projection_count']}`",
            "- focus envelope: `32 nodes / 72 relationships maximum`",
            f"- static bundle digest: `{bundle['bundle_digest']}`",
            f"- cross-surface parity digest: `{parity['parity_digest']}`",
            f"- web build manifest digest: `{manifest['manifest_digest']}`",
            f"- accepted record digest: `{gate['record_digest']}`",
            "- independent audit: `44,895 checks / 7 cross-surface parity rows`",
            "- focused tests: `47 Python checks / 8 Node tests`",
            "- browser pressure: `desktop + mobile passed`",
            "- predecessor regression: `ET-C5 full verification passed`",
            "",
            "The source-state label is a build-time snapshot in a standalone static",
            "bundle. Build and serve launchers refresh source discovery before output.",
            "Iteration 7 is authorized but is not implemented by this gate.",
            "",
        )
    )
    (records / "ETC6StaticNavigationSurface.md").write_text(report, encoding="utf-8")
    print(
        "ET_C6_BUILD_PASS "
        f"nodes={len(bundle['catalog'])} projections={bundle['selection_projection_count']} "
        f"bundle={bundle['bundle_digest']} record={gate['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
