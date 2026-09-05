#!/usr/bin/env python3
"""Execute the orchestration-only ET-C11 D11 notebook."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, load_json_object  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.successor_ux import D11_UX_BUNDLE  # noqa: E402


OUTPUTS = {
    "d11-c-claim.json": "current_claim:D11-C-CL-O-001",
    "d11-c-debt.json": ("debt_transformation:D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY"),
    "d11-c-contract.json": "equation_contract:D11-C-EC-C-J0-CURRENT",
    "d11-g9-claim.json": "current_claim:D11-G9-CL-N-001",
    "d11-g9-debt.json": ("debt_transformation:D11-G9-DEBT-CANONICAL-PORT-ALLOCATION"),
    "d11-g9-contract.json": ("equation_contract:D11-G9-EC-EXACT-OLD-PORT-MAP"),
}

EXCLUDED_PARTS = {
    "generated",
    ".cache",
    ".tooling",
    "__pycache__",
    ".ipynb_checkpoints",
    "dist",
    "public",
}


def _sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _protected_snapshot() -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(SIDE_TOOL_ROOT.rglob("*")):
        relative = path.relative_to(SIDE_TOOL_ROOT)
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        result[relative.as_posix()] = _sha256(path)
    return result


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    notebook_path = TOOL_ROOT / "notebooks/d11_successor_recipes.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    if notebook.get("nbformat") != 4:
        raise RuntimeError("ET-C11 notebook format is not admitted")
    cells = cast(list[dict[str, Any]], notebook.get("cells"))
    code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]
    if len(code_cells) != 3:
        raise RuntimeError("ET-C11 notebook must contain three orchestration cells")

    output_dir = TOOL_ROOT / "generated/iteration11-notebook"
    output_dir.mkdir(parents=True, exist_ok=True)
    unexpected = [path for path in output_dir.iterdir() if path.name not in OUTPUTS]
    if unexpected:
        raise RuntimeError("D11 notebook output envelope contains unexpected files")
    before = _protected_snapshot()
    namespace = {
        "repo_root": repo_root,
        "side_tool_root": SIDE_TOOL_ROOT,
        "output_dir": output_dir,
    }
    for index, cell in enumerate(code_cells):
        source = "".join(cast(list[str], cell.get("source", [])))
        exec(
            compile(source, f"d11_successor_recipes.ipynb:{index}", "exec"),
            namespace,
        )
    after = _protected_snapshot()
    if before != after:
        raise RuntimeError("D11 notebook changed files outside generated output")

    browser_bundle = load_json_object(SIDE_TOOL_ROOT / "records" / D11_UX_BUNDLE)
    for filename, node_id in OUTPUTS.items():
        output = load_json_object(output_dir / filename)
        if output.get("output_class") != "forensic_evidence_trace":
            raise RuntimeError(f"D11 notebook emitted non-forensic output: {filename}")
        browser_output = browser_bundle["views"][node_id]["output"]
        if canonical_bytes(output) != canonical_bytes(browser_output):
            raise RuntimeError(
                f"D11 notebook/browser/API trace identity mismatch: {filename}"
            )
    print(
        "ET_C11_D11_NOTEBOOK_PASS "
        f"recipes={len(OUTPUTS)} identity=API_notebook_browser_byte_exact "
        f"output={output_dir.relative_to(SIDE_TOOL_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
