#!/usr/bin/env python3
"""Execute the orchestration-only I3 notebook without a Jupyter dependency."""

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

from grcv4_explorer.canonical import load_json_object  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402


EXCLUDED_PARTS = {
    "generated",
    ".cache",
    ".tooling",
    "__pycache__",
    ".ipynb_checkpoints",
}


def require_repository_venv(repo_root: Path) -> None:
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


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
    require_repository_venv(repo_root)
    notebook_path = TOOL_ROOT / "notebooks/forensic_recipes.ipynb"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    if notebook.get("nbformat") != 4:
        raise RuntimeError("I3 notebook format is not admitted")
    cells = cast(list[dict[str, Any]], notebook.get("cells"))
    code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]
    if len(code_cells) != 2:
        raise RuntimeError("I3 notebook must remain a two-cell recipe")

    output_dir = TOOL_ROOT / "generated/iteration3-notebook"
    output_dir.mkdir(parents=True, exist_ok=True)
    unexpected = [
        path
        for path in output_dir.iterdir()
        if path.name not in {"normative-claim.json", "candidate-B.json"}
    ]
    if unexpected:
        raise RuntimeError("notebook output envelope contains unexpected files")
    before = _protected_snapshot()
    namespace = {
        "repo_root": repo_root,
        "side_tool_root": SIDE_TOOL_ROOT,
        "output_dir": output_dir,
    }
    for index, cell in enumerate(code_cells):
        source = "".join(cast(list[str], cell.get("source", [])))
        exec(compile(source, f"forensic_recipes.ipynb:{index}", "exec"), namespace)
    after = _protected_snapshot()
    if before != after:
        raise RuntimeError("notebook execution changed files outside generated output")
    outputs = [
        load_json_object(output_dir / name)
        for name in ("normative-claim.json", "candidate-B.json")
    ]
    if any(row.get("output_class") != "forensic_evidence_trace" for row in outputs):
        raise RuntimeError("notebook emitted a non-forensic output class")
    print(
        "ET_C3_NOTEBOOK_PASS "
        f"recipes={len(outputs)} output={output_dir.relative_to(SIDE_TOOL_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
