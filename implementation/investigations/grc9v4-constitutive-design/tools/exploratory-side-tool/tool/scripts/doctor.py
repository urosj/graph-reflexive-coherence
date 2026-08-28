#!/usr/bin/env python3
"""Validate the Iteration 0 local environment and write boundaries."""

from __future__ import annotations

import json
import os
import platform
import site
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]


def repository_root() -> Path:
    for candidate in SIDE_TOOL_ROOT.parents:
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "implementation/investigations/grc9v4-constitutive-design"
        ).is_dir():
            return candidate
    raise RuntimeError("cannot discover repository root")


REPO_ROOT = repository_root()
DECISIONS = (
    REPO_ROOT / "implementation/investigations/grc9v4-constitutive-design/decisions"
)


def inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(
        int(part) for part in value.removeprefix("v").split(".") if part.isdigit()
    )


def node_root(toolchain: dict[str, Any]) -> Path:
    return TOOL_ROOT / ".tooling/node" / f"v{toolchain['node']['managed_version']}"


def node_executable(root: Path) -> Path:
    return root / ("node.exe" if os.name == "nt" else "bin/node")


def npm_executable(root: Path) -> Path:
    return root / ("npm.cmd" if os.name == "nt" else "bin/npm")


def main() -> int:
    toolchain = tomllib.loads((TOOL_ROOT / "toolchain.toml").read_text())
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append((name, bool(condition), detail))

    venv_root = REPO_ROOT / ".venv"
    check(
        "python_in_repository_venv",
        Path(sys.prefix).resolve() == venv_root.resolve(),
        sys.prefix,
    )
    check(
        "python_minimum",
        sys.version_info >= version_tuple(toolchain["python"]["minimum"]),
        platform.python_version(),
    )
    check("user_site_disabled", not site.ENABLE_USER_SITE, str(site.ENABLE_USER_SITE))
    user_site = Path(site.getusersitepackages())
    check(
        "no_user_site_on_sys_path",
        all(
            Path(entry).resolve() != user_site.resolve() for entry in sys.path if entry
        ),
        str(user_site),
    )
    foreign_site_packages = []
    for entry in sys.path:
        if not entry or "site-packages" not in entry:
            continue
        path = Path(entry)
        if not inside(path, venv_root):
            foreign_site_packages.append(path.as_posix())
    check(
        "no_foreign_site_packages",
        not foreign_site_packages,
        repr(foreign_site_packages),
    )
    decisions = sorted(DECISIONS.glob("*.json"))
    check("accepted_source_count_33", len(decisions) == 33, str(len(decisions)))
    for path in decisions:
        data = json.loads(path.read_text(encoding="utf-8"))
        check(f"source_status_present:{path.name}", "status" in data)
        check(
            f"source_digest_present:{path.name}",
            "decision_record_digest" in data or "artifact_digest" in data,
        )
    generated = TOOL_ROOT / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    probe = generated / ".doctor-write-probe"
    probe.write_text("probe\n", encoding="ascii")
    check("derived_directory_writable", probe.read_text(encoding="ascii") == "probe\n")
    probe.unlink()
    root = node_root(toolchain)
    if node_executable(root).is_file():
        node_version = subprocess.run(
            [str(node_executable(root)), "--version"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        npm_version = subprocess.run(
            [str(npm_executable(root)), "--version"],
            capture_output=True,
            text=True,
            env={
                **os.environ,
                "PATH": str(root / "bin") + os.pathsep + os.environ.get("PATH", ""),
            },
            check=True,
        ).stdout.strip()
        check(
            "managed_node_version",
            node_version == f"v{toolchain['node']['managed_version']}",
            node_version,
        )
        check(
            "managed_npm_version",
            npm_version == toolchain["node"]["package_manager_version"],
            npm_version,
        )
        check("managed_node_tool_local", inside(root, TOOL_ROOT), root.as_posix())
    failures = [row for row in checks if not row[1]]
    for name, _, detail in failures:
        print(f"FAIL {name}: {detail}")
    print(
        f"doctor_checks={len(checks)} passed={len(checks) - len(failures)} failed={len(failures)}"
    )
    if failures:
        return 1
    print("GRCV4_EXPLORER_DOCTOR_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
