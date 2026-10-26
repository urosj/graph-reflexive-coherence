"""Authenticate named historical 8.4b inputs, never current-code conformance.

The record itself must equal the bytes in its pinned ancestor commit. Its
complete source roster then resolves at that same commit. Two large result
inputs were retained by hash before their later byte-exact archive migration;
only those explicit inputs use retained bytes instead of a Git source blob.
No historical Python is imported and no numerical checker is replaced.
"""
from functools import lru_cache
import hashlib
import json
from pathlib import PurePosixPath
import subprocess

BASE='implementation/phase-9-grcv4/tranche-8/'
REVISIONS={
    'COSCases':'0a79ece5848b3d76c0542d2a58526e79727296c5',
    'COSPhaseOneCases':'0a79ece5848b3d76c0542d2a58526e79727296c5',
    'AOSCases':'dbfcd311b8ee67ad9a5d8ea0f38670d88b8d57b1',
    'CCICompletionCases':'b8d1dd33732d7e38fb9e48403c600c138557aebc',
    'ACICases':'83952bf22dd16d397b08aca22151df63ef77d1d2',
    'CPCCases':'7820bbffa9ebbf456c96618654e36cd80bab12ac',
    'CPCScientificPressure':'7820bbffa9ebbf456c96618654e36cd80bab12ac',
    'APCCases':'a6d16c2237c799ecb28699284421c020f998e1c7',
    'CCIPCCases':'9670d97eaceee7e225be7fb31fa09ed1356bed3f',
    'CCIPCNumericalRecheck':'9670d97eaceee7e225be7fb31fa09ed1356bed3f',
    'ACIPCCases':'7639c5caf3c398d828355cbe84a91d9f43702e97',
    'ACIPCNumericalRecheck':'7639c5caf3c398d828355cbe84a91d9f43702e97',
    'CRG2bCases':'5ff017cf29119aff9cb52257a24cd6b925b9fd85',
    'CRG2bNumericalRecheck':'5ff017cf29119aff9cb52257a24cd6b925b9fd85',
    'ARG2bCases':'3b140a60effd90030deb8d14c427a18135a63137',
    'ARG2bNumericalRecheck':'3b140a60effd90030deb8d14c427a18135a63137',
}
REVISIONS={BASE+'P9-8.4b-'+name+'.json':rev for name,rev in REVISIONS.items()}
RETAINED_RESULT_INPUTS={
    (BASE+'P9-8.4b-'+family+'NumericalRecheck.json',BASE+'P9-8.4b-'+family+'Results.json')
    for family in ('CRG2b','ARG2b')
}


def require(value,message):
    if not value:raise ValueError(message)


def safe_name(name):
    require(type(name) is str and name and str(PurePosixPath(name))==name
        and not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
        and '\\' not in name and all(ord(c)>=32 for c in name),'unsafe historical source path')


def git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.PIPE)


@lru_cache(maxsize=4096)
def git_sha(root,revision,name):
    # Immutable objects only; live records and archive inputs are checked afresh.
    safe_name(name)
    try:return hashlib.sha256(git(root,'show',revision+':'+name)).hexdigest()
    except subprocess.CalledProcessError as error:
        raise ValueError('missing historical source: '+name+' at '+revision) from error


def verify(sources,name):
    require(name in REVISIONS,'unregistered historical execution record')
    revision=REVISIONS[name]
    try:git(sources.root,'merge-base','--is-ancestor',revision,'HEAD')
    except subprocess.CalledProcessError as error:raise ValueError('historical execution commit is not an available ancestor') from error
    raw=sources.raw(name)
    require(hashlib.sha256(raw).hexdigest()==git_sha(sources.root,revision,name),'historical execution record changed: '+name)
    rows=json.loads(raw)['source_bindings'];seen=set()
    for row in rows:
        path=row['path'];safe_name(path)
        require(path not in seen,'duplicate historical source binding');seen.add(path)
        actual=(hashlib.sha256(sources.current_bytes(path)).hexdigest()
                if (name,path) in RETAINED_RESULT_INPUTS else git_sha(sources.root,revision,path))
        require(actual==row['sha256'],'historical execution source mismatch: '+path)
    return dict(revision=revision,source_bindings=len(rows),current_runtime_conformance_inferred=False)


# All 39 src/spec inputs of the accepted .c-.f records have these exact
# identities at the final pre-optimization epoch. This is a closed roster,
# never a prefix-wide exemption or a current execution policy.
BOUNDARY_REVISION = '5b9836358af2873e524e6ceae7256639e8a6bbce'
BOUNDARY_SOURCES = (
    'specs/grc-9-v4-spec.md',
    'specs/grc-v4-conformance-vectors.json',
    'specs/grc-v4-contract-schema.json',
    'specs/grc-v4-spec.md',
    'src/pygrc/models/grc_9_v4_arg2b.py',
    'src/pygrc/models/grc_9_v4_expansion.py',
    'src/pygrc/models/grc_9_v4_lifecycle.py',
    'src/pygrc/models/grc_9_v4_rg2b.py',
    'src/pygrc/models/grc_9_v4_topology.py',
    'src/pygrc/models/grc_v4.py',
    'src/pygrc/models/grc_v4_assets/asset-index.json',
    'src/pygrc/models/grc_v4_assets/grc-v4-a-initializer-release.json',
    'src/pygrc/models/grc_v4_assets/grc-v4-a-initializer-schema.json',
    'src/pygrc/models/grc_v4_assets/grc-v4-contract-schema.json',
    'src/pygrc/models/grc_v4_assets/grc-v4-event-contract-release.json',
    'src/pygrc/models/grc_v4_assets/grc-v4-representation-transport-schema.json',
    'src/pygrc/models/grc_v4_assets/grc-v4-specification-release.json',
    'src/pygrc/models/grc_v4_assets/grc-v4-topology-event-schema.json',
    'src/pygrc/models/grc_v4_candidate_a.py',
    'src/pygrc/models/grc_v4_candidate_c.py',
    'src/pygrc/models/grc_v4_ci.py',
    'src/pygrc/models/grc_v4_codec.py',
    'src/pygrc/models/grc_v4_event_codec.py',
    'src/pygrc/models/grc_v4_events.py',
    'src/pygrc/models/grc_v4_exact.py',
    'src/pygrc/models/grc_v4_geometry.py',
    'src/pygrc/models/grc_v4_initializer.py',
    'src/pygrc/models/grc_v4_lifecycle.py',
    'src/pygrc/models/grc_v4_linear.py',
    'src/pygrc/models/grc_v4_migration.py',
    'src/pygrc/models/grc_v4_numerics.py',
    'src/pygrc/models/grc_v4_pc.py',
    'src/pygrc/models/grc_v4_profile.py',
    'src/pygrc/models/grc_v4_realizations.py',
    'src/pygrc/models/grc_v4_rg2b.py',
    'src/pygrc/models/grc_v4_rg2b_graph.py',
    'src/pygrc/models/grc_v4_state.py',
    'src/pygrc/models/grc_v4_step.py',
    'src/pygrc/models/grc_v4_transport.py',
)


def boundary_bindings(root):
    try:git(root,'merge-base','--is-ancestor',BOUNDARY_REVISION,'HEAD')
    except subprocess.CalledProcessError as error:
        raise ValueError('historical boundary epoch is not an available ancestor') from error
    return {name:git_sha(root,BOUNDARY_REVISION,name) for name in BOUNDARY_SOURCES}


def historical_g3(root, read_bytes=None):
    """Original accepted support consumed by old evidence, never permission today."""
    import phase9_specialization_acceptance as admission
    from pathlib import Path
    read_bytes=read_bytes or (lambda name:(Path(root)/name).read_bytes())
    raw=read_bytes(admission.RECORD)
    require(hashlib.sha256(raw).hexdigest()==git_sha(root,BOUNDARY_REVISION,admission.RECORD),
            'historical G3 acceptance changed')
    value=json.loads(raw)
    require(value['record_digest']==admission.DIGEST and value['reviewed_commit']==admission.CHECKPOINT,
            'historical G3 identity drift')
    for row in (value['review'],value['review_text']):
        require(hashlib.sha256(read_bytes(row['path'])).hexdigest()
                ==row['sha256']==git_sha(root,admission.CHECKPOINT,row['path']),
                'historical G3 review changed')
    return value
