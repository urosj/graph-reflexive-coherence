"""Repository-relative path discovery for the side tool."""

from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
TOOL_ROOT = PACKAGE_ROOT.parents[1]
SIDE_TOOL_ROOT = PACKAGE_ROOT.parents[2]


def repository_root(start: Path = SIDE_TOOL_ROOT) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "implementation/investigations/grc9v4-constitutive-design"
        ).is_dir():
            return candidate
    raise RuntimeError("cannot discover repository root")


def decisions_root(repo_root: Path) -> Path:
    return (
        repo_root / "implementation/investigations/grc9v4-constitutive-design/decisions"
    )


def et_c0_record_path(side_tool_root: Path = SIDE_TOOL_ROOT) -> Path:
    return side_tool_root / "records/ETC0SourceAndLayoutContract.json"


def repo_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as error:
        raise RuntimeError(f"path escapes repository: {path}") from error
