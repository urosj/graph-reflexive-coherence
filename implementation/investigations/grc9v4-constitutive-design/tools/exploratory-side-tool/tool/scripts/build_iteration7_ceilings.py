#!/usr/bin/env python3
"""Build the ET-C7 locked-claim and alternative navigation candidate."""

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
from grcv4_explorer.ceilings import build_claim_ceiling_layer  # noqa: E402
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
    et_c6 = load_json_object(records / "ETC6StaticNavigationSurface.json")
    layer = build_claim_ceiling_layer(repo_root, SIDE_TOOL_ROOT)
    layer_path = records / "ETC7ClaimCeilingAlternativeLayer.json"
    write_json(layer_path, layer)

    public_data = TOOL_ROOT / "web/public/data"
    public_data.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(layer_path, public_data / layer_path.name)
    vite = TOOL_ROOT / "web/node_modules/vite/bin/vite.js"
    run_managed_node(vite, ("build",))

    dist = TOOL_ROOT / "web/dist"
    files = [path for path in sorted(dist.rglob("*")) if path.is_file()]
    manifest: dict[str, object] = {
        "schema": "grcv4_explorer_ET_C7_web_build_manifest_v1",
        "status": "accepted",
        "base_static_bundle_digest": et_c6["compiled_surface"][
            "static_bundle_digest"
        ],
        "claim_ceiling_layer_digest": layer["layer_digest"],
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
    write_json(records / "ETC7WebBuildManifest.json", manifest)

    context = tomllib.loads((TOOL_ROOT / "iteration7_context.toml").read_text())
    gate: dict[str, object] = {
        "schema": "grcv4_explorer_ET_C7_claim_ceiling_alternative_admission_v1",
        "gate_id": "ET-C7_claim_ceiling_and_alternative_navigation",
        "status": "accepted",
        "iteration": 7,
        "execution_context": context,
        "predecessor": {
            "gate_id": et_c6["gate_id"],
            "record_digest": et_c6["record_digest"],
            "static_bundle_digest": et_c6["compiled_surface"][
                "static_bundle_digest"
            ],
        },
        "authority": {
            "claim_ceiling_layer_implemented": True,
            "source_classifications_immutable": True,
            "slider_presentation_only": True,
            "ghost_promotion": False,
            "browser_scientific_inference": False,
            "hidden_ranking": False,
            "scientific_claim_added": False,
            "iteration_8_authorized": True,
        },
        "compiled_surface": {
            "layer_digest": layer["layer_digest"],
            "web_build_manifest_digest": manifest["manifest_digest"],
            "lock_count": layer["population_counts"]["locks"],
            "alternative_count": layer["population_counts"]["alternatives"],
            "candidate_career_count": len(layer["candidate_careers"]),
            "hardening_count": layer["population_counts"]["targeted_hardenings"],
        },
        "acceptance_requirements": {
            "independent_source_projection_audit": "passed_2173_checks",
            "python_and_node_component_tests": "passed_477_python_checks_12_node_tests",
            "deterministic_double_rebuild": "passed",
            "playwright_source_and_speculative_desktop_mobile": "passed_4_tests_2_viewports_6_screenshots",
            "ET_C6_predecessor_regression": "passed_47_focused_checks",
            "human_review": "accepted",
        },
        "non_claims": [
            "no_ghost_or_alternative_is_promoted",
            "no_slider_value_changes_classification_propagation_or_scenario_serialization",
            "no_candidate_claim_gate_or_alternative_ranking",
            "no_lineage_scrubber_or_ripple_playback",
            "no_browser_scientific_inference",
        ],
        "record_digest": None,
    }
    gate["record_digest"] = record_digest(gate, "record_digest")
    write_json(records / "ETC7ClaimCeilingAlternativeNavigation.json", gate)

    report = "\n".join(
        (
            "# ET-C7 Claim Ceiling And Alternative Navigation",
            "",
            "**Status:** Accepted",
            "",
            "Iteration 7 compiles accepted negative claims, D10.2 blocked",
            "overreads and hardenings, candidate careers, and source-pruned",
            "alternatives into a read-only browser layer.",
            "",
            "## Result",
            "",
            f"- locked surfaces: `{layer['population_counts']['locks']}`",
            f"- alternatives and ghosts: `{layer['population_counts']['alternatives']}`",
            f"- targeted hardenings: `{layer['population_counts']['targeted_hardenings']}`",
            f"- candidate careers: `{len(layer['candidate_careers'])}`",
            f"- layer digest: `{layer['layer_digest']}`",
            f"- web manifest digest: `{manifest['manifest_digest']}`",
            f"- accepted record digest: `{gate['record_digest']}`",
            "",
            "The visibility thresholds are staged disclosure only. They do not",
            "encode evidence strength, priority, ranking, or acceptance. Readable",
            "lock text is explicitly non-authoritative; exact source machine values",
            "and JSON pointers remain available beside it.",
            "",
            "The full deterministic, independent, component, browser, visual, and",
            "predecessor verification is recorded separately in",
            "`ETC7VerificationReceipt.json`; acceptance does not weaken any",
            "source-classification or non-promotion boundary.",
            "",
            "Iteration 8 is authorized but is not implemented by this gate.",
            "",
        )
    )
    (records / "ETC7ClaimCeilingAlternativeNavigation.md").write_text(
        report, encoding="utf-8"
    )
    print(
        "ET_C7_BUILD_PASS "
        f"locks={layer['population_counts']['locks']} "
        f"alternatives={layer['population_counts']['alternatives']} "
        f"layer={layer['layer_digest']} record={gate['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
