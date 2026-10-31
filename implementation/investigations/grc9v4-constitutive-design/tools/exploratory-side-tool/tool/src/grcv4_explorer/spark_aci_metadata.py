"""Finite A_CI research successor; older scientific evidence stays immutable."""
from pathlib import Path
import hashlib,subprocess
from .basin import _bound_file
from .canonical import load_json_object,record_digest,file_sha256
from .errors import SourceAdmissionError
INV='implementation/investigations/grc9v4-constitutive-design/'
SOURCE=INV+'evidence/spark-completion/applicability/ACIMetadataSources.json'
DIGEST='69f72f0a652d9403f64f9a2c768d588887db22ebb2cd186b397c659a40100d4e'
BASELINE='8d1a0e12'
HISTORICAL_HELPER=INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_aos_earlier_metadata.py'
PATHS=frozenset({
    'implementation/Phase-9-GRCV4-Handoff.md',
    'implementation/Phase-9-GRCV4-ImplementationChecklist.md',
    INV+'GRC9V4ConstitutiveDesignChecklist.md',
    INV+'decisions/SparkCompletionAllTenApplicability.md',
    INV+'tools/exploratory-side-tool/tool/phase9-web/index.html',
    INV+'tools/exploratory-side-tool/tool/scripts/serve_phase9.py',
    INV+'tools/exploratory-side-tool/tool/notebooks/phase9_verification.ipynb',
    HISTORICAL_HELPER,
    INV+'tools/exploratory-side-tool/tool/src/grcv4_explorer/spark_aos_earlier.py',
    'implementation/phase-9-grcv4/verification/phase9_implementation_policy.py',
})


def need(ok,message):
    if not ok:raise SourceAdmissionError(message)


def checked_preimages(root,rows):
    """One Git process for the finite preimage batch; current files stay fresh."""
    requests=''.join(BASELINE+':'+path+'\n' for path in rows).encode()
    data=subprocess.check_output(['git','cat-file','--batch'],input=requests,cwd=root)
    offset=0
    for path,row in rows.items():
        end=data.find(b'\n',offset);need(end>=offset,'invalid metadata preimage response')
        header=data[offset:end].split()
        need(len(header)==3 and header[1]==b'blob' and header[2].isdigit(),'missing metadata preimage blob')
        size=int(header[2]);offset=end+1;before=data[offset:offset+size];offset+=size
        need(len(before)==size and data[offset:offset+1]==b'\n','truncated metadata preimage')
        offset+=1
        need(hashlib.sha256(before).hexdigest()==row['before_sha256'],'A_CI metadata preimage differs')
    need(offset==len(data),'extra metadata preimage response')


def checked_epoch(root):
    root=Path(root);v=load_json_object(root/SOURCE)
    need(v.get('record_digest')==record_digest(v,'record_digest')==DIGEST,'unbound A_CI metadata')
    need(v['schema']=='spark-completion-aci-metadata-v1' and v['baseline_commit']==BASELINE and
         not v['accepted_authority'] and not v['execution_relabelled'] and not v['native_runtime_changed'],'A_CI metadata scope')
    rows={r['path']:r for r in v['sources']}
    need(len(rows)==len(v['sources']) and set(rows)==PATHS,'A_CI metadata paths')
    checked_preimages(root,rows)
    for path,row in rows.items():_bound_file(root,path,row['after_sha256'])
    validation=load_json_object(root/(INV+'evidence/spark-completion/applicability/earlier-closure/AOSEarlierValidation.json'))
    need(validation['record_digest']==record_digest(validation,'record_digest'),'earlier A_OS validation digest')
    for ref in validation['sources']:
        current=file_sha256(root/ref['path'])
        if current!=ref['sha256']:
            row=rows.get(ref['path'])
            need(row is not None and row['before_sha256']==ref['sha256'] and row['after_sha256']==current,'unbound earlier validation successor')
    return v


def bound_metadata_files(root,expected):
    root=Path(root);changed={p:h for p,h in expected.items() if file_sha256(root/p)!=h}
    rows={r['path']:r for r in checked_epoch(root)['sources']} if changed else {}
    for path,sha in expected.items():
        if path not in changed:_bound_file(root,path,sha)
        else:
            row=rows.get(path)
            need(row is not None and row['before_sha256']==sha,'unbound A_CI metadata succession')
            _bound_file(root,path,row['after_sha256'])


def reviewed_source_bytes(root,path,expected):
    root=Path(root)
    if file_sha256(root/path)==expected:return _bound_file(root,path,expected).read_bytes()
    need(path==HISTORICAL_HELPER,'source changed outside the finite A_CI helper successor')
    rows={r['path']:r for r in checked_epoch(root)['sources']}
    need(rows[path]['before_sha256']==expected,'wrong historical helper subject')
    data=subprocess.check_output(['git','show',BASELINE+':'+path],cwd=root)
    need(hashlib.sha256(data).hexdigest()==expected,'historical A_OS helper bytes differ')
    return data
