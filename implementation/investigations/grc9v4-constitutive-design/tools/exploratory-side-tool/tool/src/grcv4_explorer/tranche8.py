"""Read-only retained implementation evidence, not a scientific authority query."""

import importlib.util
from pathlib import Path
import sys


def _index(root):
    directory = Path(root).resolve() / "implementation/phase-9-grcv4/verification"
    sys.path.insert(0, str(directory))
    spec = importlib.util.spec_from_file_location("phase9_tranche8_index", directory / "tranche8_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tranche8_status(repo_root, *, family=None):
    """Authenticate pinned sources and structure; never execute numerical work.

    Raises on missing Git history, source drift or a stale generated projection.
    Does not authorize implementation or claim current full-boundary validity.
    """
    index = _index(repo_root)
    if family is not None:
        return index.family_status(Path(repo_root), family)
    return index.checked(Path(repo_root))


def tranche8_source(repo_root, path):
    """Read only an indexed source, at its advertised exact revision/hash."""
    index = _index(repo_root)
    value = index.checked(Path(repo_root))
    refs = {r["path"]: r for r in value["source_refs"]}
    if path not in refs:
        raise KeyError("source is not in the checked Tranche 8 index")
    ref = refs[path]
    sources = index.Sources(repo_root)
    raw = sources.raw(path, historical=ref["basis"] == "historical_git")
    index.require(sources.refs[path] == ref, "source identity changed during read")
    return raw, ref
