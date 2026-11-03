"""Finite metadata successor for formal adoption of five earlier endpoints."""
from pathlib import Path
import hashlib
import subprocess
from .basin import _bound_file, native_predecessor
from .canonical import load_json_object, record_digest, file_sha256
from .errors import SourceAdmissionError

INV = 'implementation/investigations/grc9v4-constitutive-design/'
SIDE = INV + 'tools/exploratory-side-tool/'
SOURCE = INV + 'evidence/spark-completion/applicability/earlier-closure/EarlierSC3Sources.json'
DIGEST = '7cbb4f9584f95ffba45cb625d5af2644291c533cf525fa0e5fd67b8c5430ed40'
BASELINE = '4d247e7bbcfd0c8251b5b40b6971ef904e0c2e76'
HISTORICAL_HELPER = SIDE + 'tool/src/grcv4_explorer/spark_earlier_c_metadata.py'
PATHS = frozenset({
    'implementation/Phase-9-GRCV4-Handoff.md',
    'implementation/Phase-9-GRCV4-ImplementationChecklist.md',
    INV + 'GRC9V4ConstitutiveDesignChecklist.md',
    INV + 'decisions/SparkCompletionAllTenApplicability.md',
    SIDE + 'tool/phase9-web/index.html',
    SIDE + 'tool/scripts/serve_phase9.py',
    SIDE + 'tool/notebooks/phase9_verification.ipynb',
    SIDE + 'tool/src/grcv4_explorer/spark_earlier_c.py',
    HISTORICAL_HELPER,
    'implementation/phase-9-grcv4/verification/phase9_implementation_policy.py',
    'implementation/phase-9-grcv4/verification/p9103_source_epoch.py',
    'implementation/phase-9-grcv4/verification/p994b_runtime_successor.py',
    'implementation/phase-9-grcv4/verification/verify_p9101a_propagation.py',
})


def need(ok, message):
    if not ok:
        raise SourceAdmissionError(message)


def checked_epoch(root):
    root = Path(root)
    value = load_json_object(root / SOURCE)
    need(value.get('record_digest') == record_digest(value, 'record_digest') == DIGEST,
         'unbound earlier-endpoint acceptance metadata')
    need(value['schema'] == 'spark-completion-earlier-sc3-metadata-v1'
         and value['baseline_commit'] == BASELINE
         and not value['execution_relabelled'] and not value['native_runtime_changed'],
         'earlier-endpoint metadata scope')
    rows = {r['path']: r for r in value['sources']}
    need(len(rows) == len(value['sources']) and set(rows) == PATHS,
         'earlier-endpoint metadata paths')
    requests = ''.join(BASELINE + ':' + p + '\n' for p in rows).encode()
    data = subprocess.check_output(['git', 'cat-file', '--batch'], input=requests, cwd=root)
    offset = 0
    for path, row in rows.items():
        end = data.find(b'\n', offset)
        need(end >= offset, 'missing metadata preimage')
        header = data[offset:end].split()
        need(len(header) == 3 and header[1] == b'blob' and header[2].isdigit(),
             'invalid metadata preimage')
        size = int(header[2]); offset = end + 1
        before = data[offset:offset + size]; offset += size
        need(len(before) == size and data[offset:offset + 1] == b'\n', 'truncated metadata preimage')
        offset += 1
        need(hashlib.sha256(before).hexdigest() == row['before_sha256'], 'wrong metadata predecessor')
        _bound_file(root, path, row['after_sha256'])
    need(offset == len(data), 'extra metadata preimage')
    return value


def bound_metadata_files(root, expected):
    expected = {p: h for p, h in expected.items()
                if native_predecessor(root, p, h) is None}
    root = Path(root)
    changed = {p: h for p, h in expected.items() if file_sha256(root / p) != h}
    rows = {r['path']: r for r in checked_epoch(root)['sources']} if changed else {}
    for path, sha in expected.items():
        if path in changed:
            need(path in rows and rows[path]['before_sha256'] == sha,
                 'unbound earlier-endpoint metadata successor')
        else:
            _bound_file(root, path, sha)


def reviewed_source_bytes(root, path, expected):
    from .basin import native_predecessor
    original = native_predecessor(root, path, expected)
    if original is not None:
        return original
    root = Path(root)
    if file_sha256(root / path) == expected:
        return _bound_file(root, path, expected).read_bytes()
    need(path == HISTORICAL_HELPER, 'changed scientific source outside helper successor')
    rows = {r['path']: r for r in checked_epoch(root)['sources']}
    need(rows[path]['before_sha256'] == expected, 'wrong historical helper subject')
    data = subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=root)
    need(hashlib.sha256(data).hexdigest() == expected, 'historical helper bytes differ')
    return data
