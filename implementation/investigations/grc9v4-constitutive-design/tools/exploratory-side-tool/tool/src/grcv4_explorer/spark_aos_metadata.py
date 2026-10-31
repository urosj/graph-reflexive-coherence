"""Finite A_OS research metadata successor; scientific predecessors stay frozen."""
from pathlib import Path
import hashlib,subprocess
from .basin import _bound_file
from .canonical import load_json_object,record_digest,file_sha256
from .errors import SourceAdmissionError
SOURCE='implementation/investigations/grc9v4-constitutive-design/evidence/spark-completion/applicability/AOSMetadataSources.json'
DIGEST='47949e109fb321feaadba5ad63bb91c22ae2c1ae0d337c19d5964926ea632da4'
PREDECESSOR='d6b43c02694e56beb0c488df11c56143008ca420'
PATHS=frozenset(['implementation/Phase-9-GRCV4-Handoff.md', 'implementation/Phase-9-GRCV4-ImplementationChecklist.md', 'implementation/investigations/grc9v4-constitutive-design/GRC9V4ConstitutiveDesignChecklist.md', 'implementation/investigations/grc9v4-constitutive-design/decisions/SparkCompletionAllTenApplicability.md', 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/phase9-web/index.html', 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/serve_phase9.py', 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/notebooks/phase9_verification.ipynb', 'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_cipc_sc3_metadata.py', 'implementation/phase-9-grcv4/verification/phase9_implementation_policy.py'])

def need(ok,message):
    if not ok:raise SourceAdmissionError(message)

def checked_successor(root):
    root=Path(root);v=load_json_object(root/SOURCE)
    need(v.get('record_digest')==record_digest(v,'record_digest')==DIGEST,'unbound A_OS metadata')
    need(v['schema']=='spark-completion-aos-research-metadata-v1' and v['predecessor_commit']==PREDECESSOR and
         not v['native_runtime_changed'] and not v['execution_relabelled'],'A_OS metadata scope')
    rows={r['path']:r for r in v['sources']}
    need(set(rows)==PATHS and len(rows)==len(v['sources']),'A_OS metadata path set')
    for path,row in rows.items():
        before=subprocess.check_output(['git','show',PREDECESSOR+':'+path],cwd=root)
        need(hashlib.sha256(before).hexdigest()==row['before_sha256'],'A_OS metadata preimage')
        _bound_file(root,path,row['after_sha256'])
    return v

def bound_metadata_files(root,expected):
    root=Path(root);changed={p:h for p,h in expected.items() if file_sha256(root/p)!=h}
    rows={r['path']:r for r in checked_successor(root)['sources']} if changed else {}
    for path,sha in expected.items():
        if path not in changed:_bound_file(root,path,sha)
        else:
            row=rows.get(path)
            need(row is not None and row['before_sha256']==sha,'unbound A_OS metadata succession')
            _bound_file(root,path,row['after_sha256'])
