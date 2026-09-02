#!/usr/bin/env python3
"""Focused route, correction, branch, and stale-scenario pressure for ET-C8."""

from __future__ import annotations

import copy
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import load_json_object  # noqa: E402
from grcv4_explorer.lineage import scenario_roundtrip_bytes  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402


checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise RuntimeError(message)


def expect_failure(callback, fragment: str) -> None:
    global checks
    checks += 1
    try:
        callback()
    except (RuntimeError, KeyError) as error:
        if fragment not in str(error):
            raise RuntimeError(f"unexpected failure: {error}") from error
        return
    raise RuntimeError(f"expected failure containing: {fragment}")


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    layer = load_json_object(SIDE_TOOL_ROOT / "records/ETC8LineagePlaybackLayer.json")
    lineage = layer["lineage"]
    check(lineage["spine_node_ids"][0] == "gate_record:GRC9V4-CD-D0-v1", "spine start")
    check(lineage["spine_node_ids"][-1] == "gate_record:GRC9V4-CD-D10.2-v1", "spine end")
    check("gate_record:GRC9V4-CD-D7G-post-v2-HODGE-TYPE-CORRECTION-v1" in lineage["branch_node_ids"], "correction branch")
    check(all(row["node_id"] != row["anchor_node_id"] for row in lineage["correction_markers"]), "correction distinct")
    check(all(row["relation"] == "superseded_by" for row in lineage["supersession_markers"]), "supersession types")
    check({row["target"] for row in lineage["supersession_markers"]} == {
        "gate_record:GRC9V4-CD-D4V2-v1",
        "gate_record:GRC9V4-CD-D5V2-v1",
        "gate_record:GRC9V4-CD-D6V2-v1",
        "gate_record:GRC9V4-CD-D7V2-v1",
    }, "supersession destinations")

    c1 = next(row for row in layer["playbacks"].values() if row["source_scenario_id"] == "C1")
    check(c1["baseline_scrub_position"]["index"] == 11, "C1 scrub freeze")
    check(any(row["category"] == "routes_changed" for row in c1["transitive_consequences"]), "C1 route change")
    check(not any("B_successor" in str(row["identifier"]) for row in c1["transitive_consequences"]), "no fabricated B successor")
    frontier = c1["frames"][-1]
    states = {row["node_id"]: row["state"] for row in frontier["node_states"]}
    check(states["gate_record:GRC9V4-CD-D7V2-v1"] == "reopening_gate", "C1 reopening state")
    check(states["gate_record:GRC9V4-CD-D10.2-v1"] == "evidence_frontier_unresolved", "C1 unresolved state")
    check(states["gate_record:GRC9V4-CD-D0-v1"] == "accepted_unaffected", "C1 unaffected history")

    for playback_id, playback in layer["playbacks"].items():
        check(scenario_roundtrip_bytes(layer, playback_id).decode("ascii") == playback["scenario_canonical_json"], "roundtrip identity")
        check(playback["browser_may_recompute"] is False, "browser recomputation")
        check(playback["browser_may_predict_rerun"] is False, "browser prediction")
        for frame in playback["frames"]:
            check(len(frame["node_states"]) == 33, "complete frame")

    stale_layer = copy.deepcopy(layer)
    stale_layer["source_identities"]["graph_digest"] = "0" * 64
    expect_failure(lambda: scenario_roundtrip_bytes(stale_layer, c1["playback_id"]), "layer digest mismatch")
    stale_playback = copy.deepcopy(layer)
    stale_playback["playbacks"][c1["playback_id"]]["scenario_digest"] = "0" * 64
    stale_playback["layer_digest"] = layer["layer_digest"]
    expect_failure(lambda: scenario_roundtrip_bytes(stale_playback, c1["playback_id"]), "layer digest mismatch")
    missing = copy.deepcopy(layer)
    expect_failure(lambda: scenario_roundtrip_bytes(missing, "missing"), "missing")
    check(layer["authority"]["source_mode_changed_by_playback"] is False, "source mode immutable")
    check(layer["orientation_path"]["steps"][1]["role"] == "substantive_nine_port_specialization", "nine-port role")
    print(f"ET_C8_FOCUSED_TEST_PASS checks={checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
