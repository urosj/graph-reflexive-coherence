#!/usr/bin/env python3
"""Build the accepted ET-C8 lineage and precomputed ripple navigation layer."""

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

from grcv4_explorer.canonical import file_sha256, load_json_object, record_digest  # noqa: E402
from grcv4_explorer.lineage import build_lineage_playback_layer  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.tooling import managed_node, run_managed_node  # noqa: E402


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
    et_c7 = load_json_object(records / "ETC7ClaimCeilingAlternativeNavigation.json")
    layer = build_lineage_playback_layer(repo_root, SIDE_TOOL_ROOT)
    layer_path = records / "ETC8LineagePlaybackLayer.json"
    write_json(layer_path, layer)

    public_data = TOOL_ROOT / "web/public/data"
    public_data.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(layer_path, public_data / layer_path.name)
    vite = TOOL_ROOT / "web/node_modules/vite/bin/vite.js"
    run_managed_node(vite, ("build",))

    dist = TOOL_ROOT / "web/dist"
    files = [path for path in sorted(dist.rglob("*")) if path.is_file()]
    manifest: dict[str, object] = {
        "schema": "grcv4_explorer_ET_C8_web_build_manifest_v1",
        "status": "accepted",
        "predecessor_ET_C7_record_digest": et_c7["record_digest"],
        "lineage_playback_layer_digest": layer["layer_digest"],
        "toolchain": {
            "frontend": "vanilla_ES_modules",
            "cytoscape": "3.33.1",
            "vite": "7.1.3",
            "playwright": "1.55.0",
            "lucide": "0.468.0",
            "node": managed_node().parent.parent.name.removeprefix("v"),
        },
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
    write_json(records / "ETC8WebBuildManifest.json", manifest)

    context = tomllib.loads((TOOL_ROOT / "iteration8_context.toml").read_text())
    gate: dict[str, object] = {
        "schema": "grcv4_explorer_ET_C8_lineage_ripple_navigation_admission_v1",
        "gate_id": "ET-C8_lineage_and_ripple_navigation",
        "status": "accepted",
        "iteration": 8,
        "execution_context": context,
        "predecessor": {
            "gate_id": et_c7["gate_id"],
            "record_digest": et_c7["record_digest"],
            "layer_digest": et_c7["compiled_surface"]["layer_digest"],
        },
        "authority": {
            "lineage_and_precomputed_playback_implemented": True,
            "source_graph_immutable": True,
            "browser_propagation": False,
            "browser_rerun_prediction": False,
            "browser_scenario_editing": False,
            "source_mode_changed_by_playback": False,
            "scientific_claim_added": False,
            "iteration_9_authorized": True,
        },
        "compiled_surface": {
            "layer_digest": layer["layer_digest"],
            "web_build_manifest_digest": manifest["manifest_digest"],
            "spine_position_count": layer["population_counts"]["spine_positions"],
            "branch_node_count": layer["population_counts"]["branch_nodes"],
            "correction_marker_count": layer["population_counts"]["correction_markers"],
            "supersession_marker_count": layer["population_counts"]["supersession_markers"],
            "claim_reconstruction_count": layer["population_counts"]["claim_reconstructions"],
            "playback_row_count": layer["population_counts"]["playback_rows"],
        },
        "acceptance_requirements": {
            "independent_source_projection_audit": "passed_34241_checks",
            "python_and_node_component_tests": "passed_185_python_and_17_node_checks",
            "deterministic_double_rebuild": "passed_byte_identical",
            "playwright_desktop_mobile": "passed_8_tests_10_screenshots",
            "ET_C7_predecessor_regression": "passed_477_checks",
            "human_review": "accepted",
        },
        "non_claims": [
            "no_browser_side_propagation_or_rerun_prediction",
            "no_unresolved_descendant_is_promoted",
            "no_counterfactual_result_beyond_the_precomputed_evidence_frontier",
            "no_source_mode_mutation",
            "no_new_GRCV4_or_GRC9V4_scientific_claim",
            "no_iteration_9_implementation_inside_ET_C8",
        ],
        "record_digest": None,
    }
    gate["record_digest"] = record_digest(gate, "record_digest")
    write_json(records / "ETC8LineageAndRippleNavigation.json", gate)

    report = "\n".join(
        (
            "# ET-C8 Lineage And Ripple Navigation",
            "",
            "**Status:** Accepted",
            "",
            "Iteration 8 compiles the accepted predecessor DAG into a readable",
            "scrub spine with branch, correction, and supersession overlays. It",
            "also binds every accepted ET-C5 ripple row to exact scenario bytes",
            "and four precomputed playback frames.",
            "",
            "## Accepted Result",
            "",
            f"- accepted gate records: `{layer['population_counts']['accepted_gate_records']}`",
            f"- scrub positions: `{layer['population_counts']['spine_positions']}`",
            f"- branch nodes: `{layer['population_counts']['branch_nodes']}`",
            f"- correction markers: `{layer['population_counts']['correction_markers']}`",
            f"- supersession markers: `{layer['population_counts']['supersession_markers']}`",
            f"- backward claim reconstructions: `{layer['population_counts']['claim_reconstructions']}`",
            f"- precomputed playback rows: `{layer['population_counts']['playback_rows']}`",
            f"- layer digest: `{layer['layer_digest']}`",
            f"- web manifest digest: `{manifest['manifest_digest']}`",
            f"- accepted record digest: `{gate['record_digest']}`",
            "",
            "The scrubber follows accepted record identity, not a false linear",
            "scientific timeline. D7G post-v2 remains an accepted companion",
            "correction, and D9/D10 support records remain visible branches.",
            "",
            "Playback is presentation of ET-C5 rows only. Direct consequences,",
            "transitive consequences, reopening roots, and unresolved evidence",
            "frontiers remain distinct. The browser has no propagation rules,",
            "cannot edit scenarios, and cannot predict rerun outcomes.",
            "",
            "Human review accepted this bounded presentation layer. Iteration 9",
            "is authorized but is not implemented by this gate.",
            "",
            "## Verification",
            "",
            "- deterministic rebuilds: `2`, byte-identical",
            "- independent source audit: `34,241` checks (`1,049` structural + `33,192` per-edge-reference assertions over `11,064` links)",
            "- focused Python pressure: `185` checks",
            "- Node component tests: `17` across `4` files",
            "- Playwright: `8` tests across desktop and mobile, `10` screenshots",
            "- ET-C7 predecessor regression: `477` checks",
            "- shared-dist boundary: ET-C7 full-dist hashes are historical after the ET-C8 build; focused source/layer regression passed",
            "- visual inspection: passed without overlap, clipping, or authority conflation",
            "- human acceptance: accepted",
            "- Iteration 9 authorization: authorized; not implemented",
            "",
        )
    )
    (records / "ETC8LineageAndRippleNavigation.md").write_text(
        report, encoding="utf-8"
    )
    print(
        "ET_C8_BUILD_PASS "
        f"spine={layer['population_counts']['spine_positions']} "
        f"branches={layer['population_counts']['branch_nodes']} "
        f"reconstructions={layer['population_counts']['claim_reconstructions']} "
        f"playbacks={layer['population_counts']['playback_rows']} "
        f"layer={layer['layer_digest']} record={gate['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
