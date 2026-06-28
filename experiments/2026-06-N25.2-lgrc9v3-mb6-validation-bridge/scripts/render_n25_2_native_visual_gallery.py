#!/usr/bin/env python3
"""Build an experiment-local native visual gallery for N25.2."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from PIL import Image


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SOURCE_CLOSEOUT = OUTPUTS / "n25_2_closeout_and_n26_handoff.json"
SOURCE_POSITIVE = OUTPUTS / "n25_2_native_runtime_positive_probe.json"
SOURCE_REPLAY = OUTPUTS / "n25_2_multi_window_persistence_replay.json"
VISUAL_DIR = OUTPUTS / "n25_2_native_visual_gallery"
MANIFEST_PATH = OUTPUTS / "n25_2_native_visual_gallery.json"
REPORT_PATH = REPORTS / "n25_2_native_visual_gallery.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/"
    "scripts/render_n25_2_native_visual_gallery.py"
)

NATIVE_BUNDLES = [
    {
        "bundle_id": "multi_basin_formation_mb5_surface",
        "title": "Native MB5 multi-basin telemetry surface",
        "source_script": "examples/lgrc9v3/multi_basin_formation_bundle.py",
        "source_dir": "outputs/examples/lgrc9v3/lgrc9v3-multi-basin-formation-bundle/visualization",
        "copied_files": [
            {
                "source": "graph_sequence.png",
                "target": "n25_2_native_mb5_multi_basin_sequence.png",
                "role": "static_sequence",
            },
            {
                "source": "graph_animation.gif",
                "target": "n25_2_native_mb5_multi_basin_animation.gif",
                "role": "animation",
            },
            {
                "source": "graph_snapshots/step-000001--time-00001.0000--after_multi_basin_controls.png",
                "target": "n25_2_native_mb5_after_controls.png",
                "role": "final_snapshot",
            },
        ],
        "consumption_boundary": (
            "Native LGRC9V3 MB5 visual/telemetry surface; supports inspection of "
            "the runtime substrate but visual-only proof remains blocked."
        ),
    },
    {
        "bundle_id": "front_capacity_topology_birth_companion",
        "title": "Front-capacity topology birth visual companion",
        "source_script": "examples/lgrc9v3/front_capacity_topology_birth_visual_bundle.py",
        "source_dir": (
            "outputs/examples/lgrc9v3/"
            "lgrc9v3-front-capacity-topology-birth-visual-bundle/visualization"
        ),
        "copied_files": [
            {
                "source": "graph_sequence.png",
                "target": "n25_2_front_capacity_birth_sequence.png",
                "role": "static_sequence",
            },
            {
                "source": "graph_animation.gif",
                "target": "n25_2_front_capacity_birth_animation.gif",
                "role": "animation",
            },
            {
                "source": (
                    "graph_snapshots/"
                    "step-000001--time-00000.0000--after_front_capacity_boundary_birth.png"
                ),
                "target": "n25_2_front_capacity_after_birth.png",
                "role": "final_snapshot",
            },
        ],
        "consumption_boundary": (
            "Corrected front-capacity topology-birth visual companion. It is useful "
            "for topology-change inspection but cannot backfill MB6 child-basin "
            "runtime/replay/control gates."
        ),
    },
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def verify_image(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        extrema = image.convert("RGB").getextrema()
        nonblank = any(channel_min != channel_max for channel_min, channel_max in extrema)
        return {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "nonblank": nonblank,
        }


def run_native_examples(bundle_ids: set[str]) -> None:
    for bundle in NATIVE_BUNDLES:
        if bundle["bundle_id"] not in bundle_ids:
            continue
        script = ROOT / bundle["source_script"]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        subprocess.run([sys.executable, str(script)], cwd=ROOT, env=env, check=True)


def copy_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    source_dir = ROOT / bundle["source_dir"]
    if not source_dir.exists():
        raise FileNotFoundError(
            f"{bundle['source_dir']} does not exist; run with --regenerate-native-examples"
        )

    copied: list[dict[str, Any]] = []
    for file_record in bundle["copied_files"]:
        source = source_dir / file_record["source"]
        target = VISUAL_DIR / file_record["target"]
        if not source.exists():
            raise FileNotFoundError(
                f"{rel(source)} does not exist; run with --regenerate-native-examples"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(
            {
                "role": file_record["role"],
                "source_path": rel(source),
                "source_sha256": sha256_file(source),
                "copied_path": rel(target),
                "copied_sha256": sha256_file(target),
                "image_check": verify_image(target),
            }
        )

    return {
        "bundle_id": bundle["bundle_id"],
        "title": bundle["title"],
        "source_script": bundle["source_script"],
        "source_script_sha256": sha256_file(ROOT / bundle["source_script"]),
        "source_dir": bundle["source_dir"],
        "copied_visuals": copied,
        "consumption_boundary": bundle["consumption_boundary"],
    }


def write_report(manifest: dict[str, Any]) -> None:
    lines = [
        "# N25.2 Native Visual Gallery",
        "",
        "Experiment-local gallery for native LGRC9V3 visual outputs consumed as inspection aids for N25.2.",
        "",
        "## Bundles",
        "",
    ]
    for bundle in manifest["native_visual_bundles"]:
        static = next(
            visual for visual in bundle["copied_visuals"] if visual["role"] == "static_sequence"
        )
        animation = next(
            visual for visual in bundle["copied_visuals"] if visual["role"] == "animation"
        )
        lines.extend(
            [
                f"### {bundle['title']}",
                "",
                f"[![{bundle['title']}]({Path(static['copied_path']).relative_to(EXPERIMENT.relative_to(ROOT))})]({Path(animation['copied_path']).relative_to(EXPERIMENT.relative_to(ROOT))})",
                "",
                bundle["consumption_boundary"],
                "",
            ]
        )

    lines.extend(
        [
            "## Claim Boundary",
            "",
            manifest["claim_boundary"],
            "",
            "The copied native visuals are not proof by themselves. N25.2 MB6 support remains grounded in runtime records, replay persistence, fail-closed controls, and the closeout gate; visual-only success remains blocked.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--regenerate-native-examples",
        action="store_true",
        help="rerun the native example scripts before copying visual outputs",
    )
    args = parser.parse_args()

    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    if args.regenerate_native_examples:
        run_native_examples({bundle["bundle_id"] for bundle in NATIVE_BUNDLES})

    closeout = load_json(SOURCE_CLOSEOUT)
    positive = load_json(SOURCE_POSITIVE)
    replay = load_json(SOURCE_REPLAY)
    copied_bundles = [copy_bundle(bundle) for bundle in NATIVE_BUNDLES]

    source_artifacts = [
        {"path": rel(SOURCE_CLOSEOUT), "sha256": sha256_file(SOURCE_CLOSEOUT)},
        {"path": rel(SOURCE_POSITIVE), "sha256": sha256_file(SOURCE_POSITIVE)},
        {"path": rel(SOURCE_REPLAY), "sha256": sha256_file(SOURCE_REPLAY)},
    ]

    manifest: dict[str, Any] = {
        "artifact_id": "n25_2_native_visual_gallery",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "source_artifacts": source_artifacts,
        "native_visual_bundles": copied_bundles,
        "n25_2_acceptance_state": closeout["acceptance_state"],
        "mb6_supported": closeout.get("mb6_supported", True),
        "n26_consumption_scope": closeout["n26_handoff"]["allowed_n26_consumption"],
        "positive_probe_acceptance_state": positive["acceptance_state"],
        "multi_window_replay_acceptance_state": replay["acceptance_state"],
        "claim_boundary": (
            "scoped MB6 multi-basin substrate validation bridge only; not native "
            "support, agency, sentience, ant ecology implementation, or unscoped "
            "multi-basin consumption"
        ),
        "visual_status": "native_lgrc9v3_visual_corollary_only",
        "visual_only_proof_allowed": False,
        "visual_only_mb6_gate_satisfied": False,
        "front_capacity_companion_backfill_allowed": False,
        "unsafe_claims_supported": False,
    }
    manifest["output_digest"] = digest_value(manifest)
    MANIFEST_PATH.write_text(canonical_json(manifest), encoding="utf-8")
    write_report(manifest)


if __name__ == "__main__":
    main()
