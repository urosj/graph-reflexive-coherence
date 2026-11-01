"""Finite metadata successor for the earlier-domain research, without acceptance."""
from pathlib import Path
import hashlib,subprocess
from .basin import _bound_file
from .canonical import load_json_object,record_digest,file_sha256
from .errors import SourceAdmissionError
INV='implementation/investigations/grc9v4-constitutive-design/'
SOURCE=INV+'evidence/spark-completion/applicability/earlier-closure/AOSEarlierMetadataSources.json'
DIGEST='b220b103f5771715ac78b68061a9e10f5c52a26d3431eea87dafa5e5cc965f2b'
BASELINE='fc723f2c'
PATHS=frozenset({
    'implementation/Phase-9-GRCV4-Handoff.md',
    'implementation/Phase-9-GRCV4-ImplementationChecklist.md',
    INV+'GRC9V4ConstitutiveDesignChecklist.md',
    INV+'decisions/SparkCompletionAllTenApplicability.md',
    INV+'tools/exploratory-side-tool/tool/phase9-web/index.html',
    INV+'tools/exploratory-side-tool/tool/scripts/serve_phase9.py',
    INV+'tools/exploratory-side-tool/tool/notebooks/phase9_verification.ipynb',
    INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_aos_sc3_metadata.py',
    'implementation/phase-9-grcv4/verification/phase9_implementation_policy.py',
})


def need(ok,message):
    if not ok:raise SourceAdmissionError(message)


def checked_epoch(root):
    root=Path(root);v=load_json_object(root/SOURCE)
    need(v.get('record_digest')==record_digest(v,'record_digest')==DIGEST,'unbound earlier-domain metadata')
    need(v['schema']=='spark-completion-aos-earlier-metadata-v1' and v['baseline_commit']==BASELINE and
         not v['accepted_authority'] and not v['execution_relabelled'] and not v['native_runtime_changed'],'earlier metadata scope')
    rows={r['path']:r for r in v['sources']}
    need(len(rows)==len(v['sources']) and set(rows)==PATHS,'earlier metadata paths')
    for path,row in rows.items():
        before=subprocess.check_output(['git','show',BASELINE+':'+path],cwd=root)
        need(hashlib.sha256(before).hexdigest()==row['before_sha256'],'earlier metadata preimage differs')
    from .spark_aci_metadata import bound_metadata_files as successor_files
    successor_files(root,{path:row['after_sha256'] for path,row in rows.items()})
    return v


def bound_metadata_files(root,expected):
    root=Path(root);changed={p:h for p,h in expected.items() if file_sha256(root/p)!=h}
    rows={r['path']:r for r in checked_epoch(root)['sources']} if changed else {}
    for path,sha in expected.items():
        if path not in changed:_bound_file(root,path,sha)
        else:
            row=rows.get(path)
            need(row is not None and row['before_sha256']==sha,'unbound earlier-domain metadata succession')
            # The whole postimage batch, including its finite A_CI successor,
            # was authenticated by checked_epoch above.
