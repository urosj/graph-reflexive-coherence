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


def tranche8_status(repo_root, *, family=None, checkpoint="8.4c"):
    """Authenticate pinned sources and structure; never execute numerical work.

    Raises on missing Git history, altered retained evidence/source identities
    or a stale generated projection. Completed runs use their historical source
    epochs; current code need not equal those original bytes. Does not authorize
    implementation or claim current-code conformance/full-boundary validity.
    """
    index = _index(repo_root)
    if family is not None:
        return index.family_status(Path(repo_root), family, checkpoint)
    if checkpoint != "8.4c":
        raise ValueError("select a family for a checkpoint-specific query")
    return index.checked(Path(repo_root))


def tranche8_source(repo_root, path, *, family=None, checkpoint="8.4c"):
    """Read only an indexed source, at its advertised exact revision/hash."""
    index = _index(repo_root)
    value = (index.family_status(Path(repo_root), family, checkpoint)
             if family is not None else index.checked(Path(repo_root)))
    selected_refs = value["source_refs"]
    if checkpoint == '8.6':
        if family != 'first_group':
            selected_refs = value['decision']['source_refs'] + [r for r in selected_refs
                if r['path'].endswith(('P9-8.6-FirstGroup.json', 'P9-8.6-FirstGroupReview.md'))]
        matches = [r for r in selected_refs if r['path'] == path]
        if len({(r['sha256'], r.get('revision')) for r in matches}) > 1:
            raise KeyError('multiple execution epochs; select an individual family')
    refs = {r["path"]: r for r in selected_refs}
    if path not in refs:
        raise KeyError("source is not in the checked Tranche 8 index")
    ref = refs[path]
    if checkpoint in ('8.4i', '8.5', '8.6'):
        from p984i_first_group import authenticate
        return authenticate(Path(repo_root), ref), ref
    sources = index.Sources(repo_root)
    raw = sources.raw(path, historical=ref["basis"] == "historical_git")
    index.require(sources.refs[path] == ref, "source identity changed during read")
    return raw, ref
