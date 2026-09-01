#!/usr/bin/env python3
"""Create or validate the portable repository-local explorer toolchain."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import posixpath
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import urllib.request
import venv
import zipfile
from pathlib import Path
from typing import Any, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]


def repository_root() -> Path:
    for candidate in SIDE_TOOL_ROOT.parents:
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "implementation/investigations/grc9v4-constitutive-design"
        ).is_dir():
            return candidate
    raise RuntimeError("cannot discover repository root from bootstrap location")


REPO_ROOT = repository_root()
TOOLCHAIN_PATH = TOOL_ROOT / "toolchain.toml"


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(
        int(part) for part in value.removeprefix("v").split(".") if part.isdigit()
    )


def python_executable(venv_root: Path) -> Path:
    if os.name == "nt":
        return venv_root / "Scripts/python.exe"
    return venv_root / "bin/python"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_platform() -> tuple[str, str]:
    system = platform.system().lower()
    machine = platform.machine().lower()
    aliases = {
        "amd64": "x86_64" if system != "windows" else "amd64",
        "x64": "x86_64" if system != "windows" else "amd64",
        "arm64": "arm64" if system == "darwin" else "aarch64",
    }
    return system, aliases.get(machine, machine)


def selected_node_row(toolchain: dict[str, Any]) -> dict[str, str]:
    system, machine = normalized_platform()
    for row in toolchain["node"]["platforms"]:
        if row["platform"] == system and row["architecture"] == machine:
            return cast(dict[str, str], row)
    supported = ", ".join(
        f"{row['platform']}/{row['architecture']}"
        for row in toolchain["node"]["platforms"]
    )
    raise RuntimeError(
        f"managed Node is not admitted for {system}/{machine}; supported: {supported}"
    )


def ensure_safe_member(name: str) -> None:
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        raise RuntimeError(f"unsafe archive member: {name}")


def ensure_safe_link(member: tarfile.TarInfo) -> None:
    if member.issym():
        target = posixpath.normpath(
            posixpath.join(posixpath.dirname(member.name), member.linkname)
        )
    else:
        target = posixpath.normpath(member.linkname)
    if target.startswith("../") or target == ".." or target.startswith("/"):
        raise RuntimeError(f"unsafe archive link: {member.name} -> {member.linkname}")


def extract_archive(archive: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as bundle:
            for info in bundle.infolist():
                ensure_safe_member(info.filename)
            bundle.extractall(destination)
    else:
        with tarfile.open(archive, "r:*") as bundle:
            for member in bundle.getmembers():
                ensure_safe_member(member.name)
                if member.issym() or member.islnk():
                    ensure_safe_link(member)
            bundle.extractall(destination)
    roots = sorted(path for path in destination.iterdir() if path.is_dir())
    if len(roots) != 1:
        raise RuntimeError(f"expected one Node archive root, found {len(roots)}")
    return roots[0]


def download_node(row: dict[str, str], offline_cache: Path | None) -> Path:
    cache = TOOL_ROOT / ".cache/downloads"
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / row["archive"]
    if offline_cache is not None:
        source = offline_cache / row["archive"]
        if not source.is_file():
            raise RuntimeError(f"offline cache is missing {row['archive']}")
        if not archive.exists():
            shutil.copyfile(source, archive)
    elif not archive.exists():
        temporary = archive.with_suffix(archive.suffix + ".part")
        request = urllib.request.Request(
            row["url"], headers={"User-Agent": "grcv4-explorer-bootstrap/1"}
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                with temporary.open("wb") as output:
                    shutil.copyfileobj(response, output)
            temporary.replace(archive)
        finally:
            if temporary.exists():
                temporary.unlink()
    actual = file_sha256(archive)
    if actual != row["sha256"]:
        raise RuntimeError(
            f"Node archive checksum mismatch for {row['archive']}: {actual}"
        )
    return archive


def node_executable(node_root: Path) -> Path:
    if os.name == "nt":
        return node_root / "node.exe"
    return node_root / "bin/node"


def npm_executable(node_root: Path) -> Path:
    if os.name == "nt":
        return node_root / "npm.cmd"
    return node_root / "bin/npm"


def local_environment(node_root: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    cache = TOOL_ROOT / ".cache"
    paths = {
        "PIP_CACHE_DIR": cache / "pip",
        "NPM_CONFIG_CACHE": cache / "npm",
        "NPM_CONFIG_USERCONFIG": TOOL_ROOT / ".tooling/npmrc",
        "COREPACK_HOME": TOOL_ROOT / ".tooling/corepack",
        "PLAYWRIGHT_BROWSERS_PATH": TOOL_ROOT / ".tooling/playwright",
        "JUPYTER_CONFIG_DIR": cache / "jupyter/config",
        "JUPYTER_DATA_DIR": cache / "jupyter/data",
        "JUPYTER_RUNTIME_DIR": cache / "jupyter/runtime",
    }
    for key, path in paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    if node_root is not None:
        node_bin = node_root if os.name == "nt" else node_root / "bin"
        env["PATH"] = os.pathsep.join((str(node_bin), env.get("PATH", "")))
    return env


def ensure_repository_venv() -> Path:
    root = REPO_ROOT / ".venv"
    executable = python_executable(root)
    if root.exists() and not executable.is_file():
        raise RuntimeError(
            f"repository environment is incomplete: {root}; remove or repair it "
            "before rerunning bootstrap"
        )
    if not root.exists():
        temporary = root.with_name(f"{root.name}.bootstrap-{os.getpid()}")
        if temporary.exists():
            raise RuntimeError(f"stale bootstrap environment exists: {temporary}")
        try:
            venv.EnvBuilder(
                with_pip=True,
                clear=False,
                symlinks=os.name != "nt",
            ).create(temporary)
            temporary_executable = python_executable(temporary)
            if not temporary_executable.is_file():
                raise RuntimeError("temporary repository environment is incomplete")
            temporary.replace(root)
        except BaseException:
            if temporary.exists():
                shutil.rmtree(temporary)
            raise
        executable = python_executable(root)
    if Path(sys.prefix).resolve() != root.resolve():
        if os.environ.get("GRCV4_EXPLORER_BOOTSTRAP_REEXEC") == "1":
            raise RuntimeError("bootstrap failed to enter the repository .venv")
        env = os.environ.copy()
        env["GRCV4_EXPLORER_BOOTSTRAP_REEXEC"] = "1"
        completed = subprocess.run(
            [str(executable), str(SCRIPT), *sys.argv[1:]], env=env, check=False
        )
        raise SystemExit(completed.returncode)
    return root


def install_locked_python_dependencies(venv_root: Path) -> None:
    lock = TOOL_ROOT / "python-requirements.lock"
    requirements = [
        line.strip()
        for line in lock.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not requirements:
        return
    subprocess.run(
        [
            str(python_executable(venv_root)),
            "-m",
            "pip",
            "install",
            "--require-hashes",
            "--disable-pip-version-check",
            "-r",
            str(lock),
        ],
        cwd=REPO_ROOT,
        env=local_environment(),
        check=True,
    )


def ensure_node(toolchain: dict[str, Any], offline_cache: Path | None) -> Path:
    version = toolchain["node"]["managed_version"]
    target = TOOL_ROOT / ".tooling/node" / f"v{version}"
    executable = node_executable(target)
    if not executable.is_file():
        row = selected_node_row(toolchain)
        archive = download_node(row, offline_cache)
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="node-extract-", dir=target.parent
        ) as temporary:
            extracted = extract_archive(archive, Path(temporary))
            shutil.move(str(extracted), str(target))
    reported = subprocess.run(
        [str(executable), "--version"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if reported != f"v{version}":
        raise RuntimeError(f"managed Node version mismatch: {reported}")
    return target


def install_frontend_lock(node_root: Path) -> None:
    web_root = TOOL_ROOT / "web"
    subprocess.run(
        [
            str(npm_executable(node_root)),
            "ci",
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
        ],
        cwd=web_root,
        env=local_environment(node_root),
        check=True,
    )


def write_environment_receipt(node_root: Path | None) -> None:
    generated = TOOL_ROOT / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema": "grcv4_explorer_environment_receipt_v1",
        "authority": "ignored_diagnostic_only",
        "python_version": platform.python_version(),
        "python_environment": ".venv",
        "platform": platform.system().lower(),
        "architecture": platform.machine().lower(),
        "managed_node_present": node_root is not None,
        "managed_node_root": (
            node_root.relative_to(SIDE_TOOL_ROOT).as_posix()
            if node_root is not None
            else None
        ),
    }
    (generated / "environment-receipt.json").write_text(
        json.dumps(
            receipt,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--python-only",
        action="store_true",
        help="Prepare only the forensic Python environment; skip managed Node.",
    )
    parser.add_argument(
        "--offline-cache",
        type=Path,
        help="Use a directory containing the checksum-pinned Node archive.",
    )
    args = parser.parse_args()
    toolchain = tomllib.loads(TOOLCHAIN_PATH.read_text(encoding="utf-8"))
    if sys.version_info < version_tuple(toolchain["python"]["minimum"]):
        raise RuntimeError(
            f"Python {toolchain['python']['minimum']} or later is required"
        )
    venv_root = ensure_repository_venv()
    install_locked_python_dependencies(venv_root)
    node_root = None
    if not args.python_only:
        node_root = ensure_node(toolchain, args.offline_cache)
        install_frontend_lock(node_root)
    write_environment_receipt(node_root)
    subprocess.run(
        [str(python_executable(venv_root)), str(TOOL_ROOT / "scripts/doctor.py")],
        cwd=SIDE_TOOL_ROOT,
        env=local_environment(node_root),
        check=True,
    )
    print("bootstrap_status=passed")
    print("python=.venv/bin/python")
    print(
        "doctor=.venv/bin/python "
        + str((TOOL_ROOT / "scripts/doctor.py").relative_to(REPO_ROOT))
    )
    print(
        "iteration0_build=.venv/bin/python "
        + str(
            (TOOL_ROOT / "scripts/build_iteration0_contract.py").relative_to(REPO_ROOT)
        )
    )
    print(
        "iteration0_audit=.venv/bin/python "
        + str(
            (TOOL_ROOT / "scripts/audit_iteration0_contract.py").relative_to(REPO_ROOT)
        )
    )
    print(
        "source_discovery=.venv/bin/python "
        + str((TOOL_ROOT / "scripts/discover_sources.py").relative_to(REPO_ROOT))
    )
    print(
        "iteration1_build=.venv/bin/python "
        + str((TOOL_ROOT / "scripts/build_iteration1_bundle.py").relative_to(REPO_ROOT))
    )
    print(
        "iteration1_audit=.venv/bin/python "
        + str((TOOL_ROOT / "scripts/audit_iteration1_bundle.py").relative_to(REPO_ROOT))
    )
    print("notebooks=blocked_until_ET_C3_iteration_3")
    print("web_build=blocked_until_iteration_6")
    print("static_serving=blocked_until_iteration_6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
