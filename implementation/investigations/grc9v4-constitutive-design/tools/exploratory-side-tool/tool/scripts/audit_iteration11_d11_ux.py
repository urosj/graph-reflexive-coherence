#!/usr/bin/env python3
"""Audit the ET-C11 API/notebook/browser presentation candidate."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    repo_root = repository_root()
    records = SIDE_TOOL_ROOT / "records"
    admission = load_json_object(records / D11_FORENSIC_ADMISSION)
    context = load_successor_forensic_context(repo_root, SIDE_TOOL_ROOT)
    accepted_bundle = load_json_object(records / D11_UX_BUNDLE)
    rebuilt_bundle = build_d11_ux_bundle(context, admission)
    validate_d11_ux_bundle(accepted_bundle, admission)
    require(
        canonical_bytes(rebuilt_bundle) == canonical_bytes(accepted_bundle),
        "D11 UX bundle does not rebuild byte-exactly from the Python API",
    )

    candidate = load_json_object(records / D11_UX_CANDIDATE)
    require(
        candidate.get("schema") == D11_UX_CANDIDATE_SCHEMA
        and candidate.get("status") == "candidate",
        "D11 UX candidate lifecycle",
    )
    require(
        candidate.get("record_digest") == record_digest(candidate, "record_digest"),
        "D11 UX candidate digest",
    )
    require(
        candidate["predecessor"]["record_digest"] == admission["record_digest"],
        "D11 UX candidate predecessor",
    )
    require(
        candidate["compiled_surface"]["bundle_digest"]
        == accepted_bundle["bundle_digest"],
        "D11 UX candidate bundle identity",
    )
    for row in candidate["source_files"].values():
        require(
            file_sha256(repo_root / row["path"]) == row["sha256"],
            f"D11 UX source identity: {row['path']}",
        )

    manifest = load_json_object(records / D11_UX_WEB_MANIFEST)
    require(
        manifest.get("schema") == D11_UX_WEB_MANIFEST_SCHEMA
        and manifest.get("status") == "candidate",
        "D11 UX web manifest lifecycle",
    )
    require(
        manifest.get("manifest_digest") == record_digest(manifest, "manifest_digest"),
        "D11 UX web manifest digest",
    )
    dist = TOOL_ROOT / "web/dist"
    actual_files = [path for path in sorted(dist.rglob("*")) if path.is_file()]
    require(len(actual_files) == manifest["file_count"], "D11 UX dist file count")
    manifest_files = {row["path"]: row for row in manifest["files"]}
    require(
        {path.relative_to(dist).as_posix() for path in actual_files}
        == set(manifest_files),
        "D11 UX dist file identities",
    )
    for path in actual_files:
        relative = path.relative_to(dist).as_posix()
        require(
            file_sha256(path) == manifest_files[relative]["sha256"],
            f"D11 UX dist hash: {relative}",
        )
    require(
        "data/ETC11D11SuccessorUXBundle.json" in manifest_files,
        "D11 UX data missing from browser distribution",
    )

    notebook = json.loads(
        (TOOL_ROOT / "notebooks/d11_successor_recipes.ipynb").read_text(
            encoding="utf-8"
        )
    )
    require(notebook.get("nbformat") == 4, "D11 UX notebook format")
    require(
        len([row for row in notebook["cells"] if row["cell_type"] == "code"]) == 3,
        "D11 UX notebook orchestration cells",
    )
    scenarios = (
        SIDE_TOOL_ROOT / "GRCV4ExploratorySideToolD11UXScenarios.md"
    ).read_text(encoding="utf-8")
    require(
        all(f"## UX{index}." in scenarios for index in range(1, 9)),
        "D11 UX scenario definitions",
    )
    documentation = {
        "plan": SIDE_TOOL_ROOT / "GRCV4ExploratorySideToolImplementationPlan.md",
        "checklist": (
            SIDE_TOOL_ROOT / "GRCV4ExploratorySideToolImplementationChecklist.md"
        ),
        "README": SIDE_TOOL_ROOT / "README.md",
        "agentic guide": SIDE_TOOL_ROOT / "docs/AgenticQueryGuide.md",
        "D11 UX guide": SIDE_TOOL_ROOT / "docs/D11UXGuide.md",
    }
    documentation_text = {
        label: path.read_text(encoding="utf-8") for label, path in documentation.items()
    }
    require(
        "### Iteration 11. D11 API, Notebook, And Browser UX"
        in documentation_text["plan"],
        "D11 UX implementation plan",
    )
    require(
        "## Iteration 11. D11 API, Notebook, And Browser UX"
        in documentation_text["checklist"],
        "D11 UX implementation checklist",
    )
    require(
        "serve-iteration11-d11" in documentation_text["README"],
        "D11 UX README entry point",
    )
    require(
        "notebook-iteration11-d11" in documentation_text["agentic guide"],
        "D11 UX agentic notebook workflow",
    )
    require(
        "browser-iteration11-d11" in documentation_text["D11 UX guide"],
        "D11 UX focused browser workflow",
    )

    scope_counts = Counter(row["scope"] for row in accepted_bundle["catalog"])
    require(scope_counts == {"D11-C": 25, "D11-G9": 44}, "D11 UX scopes")
    output_counts = Counter(row["output_class"] for row in accepted_bundle["catalog"])
    require(
        output_counts
        == {"forensic_evidence_trace": 60, "source_bound_graph_projection": 9},
        "D11 UX output classes",
    )
    require(
        all(
            view["output"].get("authority_extension_digest")
            == admission["record_digest"]
            for view in accepted_bundle["views"].values()
        ),
        "D11 UX outputs do not retain ET-C10 authority identity",
    )
    print(
        "ET_C11_D11_UX_AUDIT_PASS "
        "catalog=69 D11_C=25 D11_G9=44 API_outputs=60 projections=9 "
        f"dist_files={len(actual_files)} bundle={accepted_bundle['bundle_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
