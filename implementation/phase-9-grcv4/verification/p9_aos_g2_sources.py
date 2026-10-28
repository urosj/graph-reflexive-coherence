"""Authenticate older G2 inputs across the already committed performance work.

Only these named source epochs are projected. Live kernels are never replaced,
and historical G2 execution does not certify a newer implementation.
"""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess

CURRENT = '02528b5d'
PRE_PERFORMANCE = '5b9836358af2873e524e6ceae7256639e8a6bbce'
ROSTER_BASE = 'ffbcabf108ccf2f4e71e0cfbd9d122b2fe017f40'
EPOCHS = {
    **{'src/pygrc/models/'+name+'.py': '5b9836358af2873e524e6ceae7256639e8a6bbce'
       for name in ('grc_v4', 'grc_v4_candidate_c', 'grc_v4_ci',
                    'grc_v4_geometry', 'grc_v4_lifecycle', 'grc_v4_realizations',
                    '_grc_v4_matrix', 'grc_9_v4_lifecycle', 'grc_v4_exact',
                    'grc_v4_linear', 'grc_v4_numerics')},
    **{name: '1275bd1f' for name in (
        'specs/README.md',
        'implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md',
        'implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md')},
    'src/pygrc/models/__init__.py': '7b16696a',
    'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/tranche8.py': '7fed33a0fd868ec4e1c31b4da3b088d76978a5b7',
}
ADDITIONS = {
    'src/pygrc/models/grc_v4_interval.py',
    'src/pygrc/models/grc_v4_certification.py',
    'tests/models/_grc_v4_research_sources.py',
    *('tests/models/test_grc_v4_'+name+'.py' for name in (
        'split_certificate', 'ci_residual_policy', 'certified_policy',
        'exact_direct_probe', 'resolvent_predictor_probe', 'hodge_positive_probe',
        'interval', 'arb_policy', 'scalar_kernels', 'solve_reuse',
        'dyadic_rounding', 'os_pass_probe')),
}
SIDE = 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/'
VALIDATED_ADDITIONS = {
    *('src/pygrc/models/grc_9_v4_'+n+'.py' for n in
      ('legacy','api_lifecycle','crossing','owner','basin','identity','contracts')),
    'src/pygrc/models/grc_9_v4.py',
    *('tests/models/test_grc_9_v4_'+n+'.py' for n in
      ('owner','contracts','crossing','basin','architecture','legacy','aos_integration')),
    'tests/models/test_grc_9_v4.py', 'tests/test_evidence_storage.py',
    *(SIDE+n+'.py' for n in ('tranche9','basin_native','tranche10_support',
                            'target_compatibility','tranche8_end','basin','aos')),
}
VALIDATION = 'implementation/phase-9-grcv4/tranche-9/P9-AOS-Validation.json'
VALIDATION_DIGEST = '665f337be56a31cfdd11bfca5c5e9198192277998d6e8c6c2d046083ac5bb712'
INITIALIZER_REVISION = '1afbc02aa4282a1575aef491700312cc1774dae7'
INITIALIZER_READER = 'implementation/phase-9-grcv4/verification/verify_p972a_initializer_runtime.py'
EPOCHS[INITIALIZER_READER] = CURRENT
READER_SHA = '10b4a6e027915b4386320b0035a28b7c9cad7f6eea66f6dcc911c20b00d99248'


def initializer_package(root):
    """Read the unchanged accepted package and authenticate every original input."""
    root = Path(root).resolve()
    release = 'specs/grc-v4-a-initializer-release.json'
    paths = (release, 'src/pygrc/models/grc_v4_assets/grc-v4-a-initializer-release.json',
             'src/pygrc/models/grc_v4_assets/grc-v4-a-initializer-schema.json')
    result = {}
    for name in paths:
        raw = (root/name).read_bytes()
        if sha(raw) != original(root, INITIALIZER_REVISION, name):
            raise ValueError('accepted initializer package drift: '+name)
        result[name] = raw
    for row in json.loads(result[release])['release_identity_payload']['artifact_bindings']:
        if original(root, INITIALIZER_REVISION, row['path']) != row['sha256']:
            raise ValueError('initializer package historical input drift: '+row['path'])
    return result


def validated_sources(root):
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    value = json.loads((root/VALIDATION).read_bytes())
    body = {k:v for k,v in value.items() if k!='record_digest'}
    if value['record_digest'] != VALIDATION_DIGEST or sha(canonical_json_bytes(body)) != VALIDATION_DIGEST:
        raise ValueError('unregistered A_OS validation epoch')
    refs = {r['path']:r['sha256'] for r in value['source_bindings']}
    review = 'implementation/phase-9-grcv4/tranche-8/P9-AOS-Tranches8-9-Review.json'
    raw = (root/review).read_bytes()
    if sha(raw) != refs[review]:
        raise ValueError('A_OS source review drift')
    for row in json.loads(raw)['source_bindings']:
        if row['path'] in refs and refs[row['path']] != row['sha256']:
            raise ValueError('contradictory A_OS source epochs')
        refs[row['path']] = row['sha256']
    return refs


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@lru_cache(maxsize=128)
def original(root, revision, name):
    # Cache only immutable Git bytes; live source is read on every projection.
    return sha(subprocess.check_output(['git', 'show', revision+':'+name], cwd=root))


def project(root, current, changes):
    root = Path(root).resolve()
    result = dict(current)
    validated = validated_sources(root) if VALIDATED_ADDITIONS & result.keys() else {}
    for name in (ADDITIONS | VALIDATED_ADDITIONS) & result.keys():
        latest = validated[name] if name in validated else original(root, CURRENT, name)
        if result[name] != latest or sha((root/name).read_bytes()) != latest:
            raise ValueError('unregistered historical G2 roster addition: '+name)
        prior = ROSTER_BASE if name in VALIDATED_ADDITIONS else PRE_PERFORMANCE
        original(root, prior, 'pyproject.toml')  # The predecessor must exist.
        before = subprocess.run(['git', 'cat-file', '-e', prior+':'+name],
                                cwd=root, capture_output=True)
        if before.returncode == 0:
            raise ValueError('G2 roster addition existed in its predecessor: '+name)
        del result[name]
    for name, revision in EPOCHS.items():
        if name not in result:
            continue
        present = sha((root/name).read_bytes())
        latest = READER_SHA if name == INITIALIZER_READER else original(root, CURRENT, name)
        earlier = original(root, revision, name)
        allowed = {latest, earlier}
        if name in changes:
            allowed |= {changes[name]['before_sha256'], changes[name]['after_sha256']}
            if earlier != changes[name]['after_sha256']:
                raise ValueError('G2 predecessor does not meet the Tranche 8 bridge: '+name)
        if present != latest or result[name] not in allowed:
            raise ValueError('unregistered post-Tranche-8 G2 source: '+name)
        if result[name] == latest:
            result[name] = earlier
    return result


METADATA_SUCCESSORS = {'implementation/phase-9-grcv4/verification/tranche8_evidence.py': '3bc525683bd6c8a043d922978702cc91a5af67b7015c6e2b3b05cc7017ee60d5', 'implementation/phase-9-grcv4/verification/p984i_first_group.py': 'b8b43aad96db2cca0d804788a651b5cb2b95db0f098d3be27fd8abba41962fa6'}


def metadata_source(root, name, expected):
    """Two named index readers only; authenticate their earlier source bytes."""
    if name not in METADATA_SUCCESSORS:
        return None
    root=Path(root).resolve()
    if sha((root/name).read_bytes())!=METADATA_SUCCESSORS[name]:
        return None
    old=original(root,CURRENT,name)
    revision=CURRENT if expected==old else None
    if revision is None:
        from p994b_runtime_successor import SOURCES
        row=SOURCES.get(name)
        if row is not None and row['current_sha256']==old:
            revision=row['predecessors'].get(expected)
    if revision is None:
        return None
    raw=subprocess.check_output(['git','show',revision+':'+name],cwd=root)
    return raw if sha(raw)==expected else None
