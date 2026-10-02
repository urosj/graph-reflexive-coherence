"""Export pinned repository bytes and local review evidence; no acceptance gate."""

import argparse
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path

SOURCE_COMMIT = "42976ed60da397a95de95b0361454e39ffbf9643"
SOURCE_PATHS = (
    "src/pygrc",
    "implementation/phase-9-grcv4/verification/test_p980*.py",
    "implementation/phase-9-grcv4/tranche-8",
    "implementation/phase-9-grcv4/tranche-7/ProfileG2Registry.json",
    "specs/grc-v4-conformance-vectors.json",
    "specs/grc-v4-spec.md",
    "specs/grc-9-v4-spec.md",
    "pyproject.toml",
    "README.md",
    "LICENSE",
)
CORRECTED_FILES = (
    "implementation/phase-9-grcv4/verification/test_p980_rg2b_numerical.py",
    "implementation/phase-9-grcv4/verification/test_p980_rg_implementation_review.py",
)
EVIDENCE_FILES = (
    "README.md",
    "export.py",
    "requirements.txt",
    "environment.json",
    "numerical-report.json",
    "numerical-run.txt",
    "event-report.json",
    "event-run.txt",
    "SelfReview.md",
    "numerical-correction.patch",
    "pressure-before.txt",
    "pressure-corrections.txt",
    "pressure-report.json",
    "pressure-run.txt",
    "numerical-corrected-report.json",
    "numerical-corrected-run.txt",
    "event-corrected-report.json",
    "event-corrected-run.txt",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    root = here.parents[3]
    output = args.output or root / "build/P9-8.0-RG-NumericalReview.zip"
    archive = subprocess.check_output(
        ["git", "archive", "--format=zip", SOURCE_COMMIT, *SOURCE_PATHS], cwd=root
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        files = {
            i.filename: source.read(i) for i in source.infolist() if not i.is_dir()
        }
    source_files = set(files)
    source_paths = {name: name for name in files}
    prefix = here.relative_to(root).as_posix()
    for name in CORRECTED_FILES:
        if name in files:
            baseline = f"{prefix}/baseline/{Path(name).name}"
            files[baseline] = files[name]
            source_files.add(baseline)
            source_paths[baseline] = name
            source_files.remove(name)
        files[name] = (root / name).read_bytes()
    for name in EVIDENCE_FILES:
        key = f"{prefix}/{name}"
        if key in files:
            raise ValueError(f"Review overlay must not replace pinned source: {key}")
        files[key] = (here / name).read_bytes()
    manifest = {
        "source_commit": SOURCE_COMMIT,
        "purpose": "Baseline plus explicit local corrections and own review; not external audit or acceptance",
        "files": {
            name: {
                **({"source_path": source_paths[name]} if name in source_files else {}),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "origin": (
                    "source_commit"
                    if name in source_files
                    else "local_review_correction"
                    if name in CORRECTED_FILES
                    else "local_review_evidence"
                ),
            }
            for name, data in sorted(files.items())
        },
    }
    manifest_bytes = (json.dumps(manifest, indent=2) + "\n").encode()
    (here / "manifest.json").write_bytes(manifest_bytes)
    files[f"{prefix}/manifest.json"] = manifest_bytes
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            target.writestr(info, data)
    print(f"Exported {len(files)} files to {output}")
    print(f"SHA256 {hashlib.sha256(output.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
