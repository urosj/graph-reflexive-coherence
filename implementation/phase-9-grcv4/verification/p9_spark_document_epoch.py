"""Exact spark document succession for older basin/release provenance readers.

The five named documents keep their accepted basin-era subjects. Later spark
additions are pinned to a committed checkpoint; only the checklist and the three
reader repairs below may additionally use the current, finite SC-3 metadata
record. No mathematical contract, runtime or execution record is projected.
"""
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import sys

INV = 'implementation/investigations/grc9v4-constitutive-design/'
HERE = 'implementation/phase-9-grcv4/verification/'
BASIN_COMMIT = 'b30e630c5c8312e0e2b5caa6f0a490a2a7816217'
SPARK_COMMIT = '4d247e7bbcfd0c8251b5b40b6971ef904e0c2e76'
# (basin-era SHA-256, committed spark SHA-256)
DOCUMENTS = {
    INV + 'README.md': (
        '71fef6a44b22634c88058e62ca7eff31a4f44da9fc034168823b76493977a2b1',
        '8083bfb960527e3af38bfc944763e20096c35ab8068a577498d68f2b2f48265f'),
    'specs/README.md': (
        '1effe5b7af0209cc871d905e268c44a54e885d65446969a954cb41bb243d6964',
        '2fe7a4da3a3f7de2e1cf7e97b3ca8b9d16c783f597c064a79eb78c7418790726'),
    INV + 'GRC9V4ConstitutiveDesignPlan.md': (
        '07870ce3c58adb5953975d0d8adae8807488720ac4eeb2fccb1fd070d08d25ca',
        '9f5b7df179c3802b35b7742c335feb443743b47af4e21754f2b054207ca0a653'),
    INV + 'GRC9V4ConstitutiveDesignChecklist.md': (
        'bb1d2e3f2dfceed1f86dde2e5a659dabcda0fd561fe27148736ffc3ef882fbe1',
        '6dc27195b1043cb405b3079a54074459ea1966fd110d04a17d9595a786321e3e'),
    INV + 'GRC9V4ConstitutiveDesignDecisionLedger.md': (
        'a6aeeff425ab9c38f2aa195edbdf1351620f24c8e9f814bacc235d75bc82983a',
        'f28b774c155cf6342dcc742c27dc2f05a5b08fc95a2ddc6e4601242f72b1cb05'),
}
READERS = {
    HERE + 'p994b_runtime_successor.py': '96314146047673b756f9ac1dc47bd9230a99c538d212444c3240ea7bb6d6e474',
    HERE + 'p9103_source_epoch.py': 'a60a6d9908422d5fccf6a989161af6f61fffd3cf02b8de13321cbcc6b0312cd2',
    HERE + 'verify_p9101a_propagation.py': '742dbb3394749c04918bdaa436a8666321c5a0c89193463c799c0ba176d22e56',
}
CHECKLIST = INV + 'GRC9V4ConstitutiveDesignChecklist.md'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@lru_cache(maxsize=16)
def committed(root, revision, name, expected):
    """Cache immutable Git blobs only; live bytes are checked on every call."""
    raw = subprocess.check_output(['git', 'show', revision + ':' + name], cwd=root)
    if sha(raw) != expected:
        raise ValueError('spark document predecessor mismatch: ' + name)
    return raw


def checked_metadata(root, name, before, current):
    # Metadata imports the side-tool before the later native provenance readers.
    # Resolve their shared pygrc package from this checkout, not an older wheel.
    for directory in (root / 'src', root / INV / 'tools/exploratory-side-tool/tool/src'):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
    from grcv4_explorer.spark_earlier_sc3_metadata import checked_epoch
    from grcv4_explorer.errors import SourceAdmissionError
    try:
        rows = {row['path']: row for row in checked_epoch(root)['sources']}
        row = rows.get(name)
        if row is None or row['before_sha256'] != before or row['after_sha256'] != current:
            raise ValueError('spark document/reader metadata does not bind these bytes: ' + name)
    except SourceAdmissionError as error:
        raise ValueError('unbound spark document/reader successor: ' + name) from error


def previous_bytes(root, name):
    root = Path(root).resolve()
    path = root / name
    if Path(name).is_absolute() or '..' in Path(name).parts or not path.resolve().is_relative_to(root):
        raise ValueError('spark document path escapes repository')
    raw = path.read_bytes()
    current = sha(raw)
    if name in READERS:
        before = READERS[name]
        if current == before:
            return raw
        checked_metadata(root, name, before, current)
        return committed(root, SPARK_COMMIT, name, before)
    if name not in DOCUMENTS:
        return raw
    before, after = DOCUMENTS[name]
    if current == before:
        return raw
    if current != after:
        if name != CHECKLIST:
            raise ValueError('unbound spark document successor: ' + name)
        checked_metadata(root, name, after, current)
    committed(root, SPARK_COMMIT, name, after)
    return committed(root, BASIN_COMMIT, name, before)


def peel_sha(root, name, present):
    if name not in DOCUMENTS and name not in READERS:
        return present
    previous = previous_bytes(root, name)
    live = sha((Path(root) / name).read_bytes())
    return sha(previous) if present == live else present
