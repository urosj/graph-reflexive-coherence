"""Native C_CI steps 1–4: current-source-bound preflight, no endpoint grant."""
from pathlib import Path
import hashlib
from .canonical import load_json_object, record_digest, digest
from .errors import SourceAdmissionError
from .spark_native_cci_pressure import native_cci_pressure

RECORD='implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CCI-Preflight.json'
RECORD_DIGEST='04267e3d233d8abbc22b86e32d691caaa32d516750e47f65ced0ff369af5a46c'


def checked_record(root):
    import sys
    sys.path.insert(0, str(Path(root)/"implementation/phase-9-grcv4/verification"))
    from p991a6_cci_campaign_epoch import previous_bytes
    root=Path(root).resolve();value=load_json_object(root/RECORD)
    if (value.get('record_digest')!=RECORD_DIGEST or record_digest(value,'record_digest')!=RECORD_DIGEST
        or value.get('schema')!='grc9v4-native-cci-preflight-v1' or value.get('family')!='C_CI'
        or value.get('native_endpoint_verified') is not False or value.get('native_completion_support') is not False
        or value.get('full_trajectory_runs')!=0 or value.get('user_accepted') is not False):
        raise SourceAdmissionError('Unbound C_CI preflight or changed endpoint scope')
    for row in [*value['source_bindings'],value['evidence']]:
        p=root/row['path']
        try:
            raw = previous_bytes(root, row["path"])
        except ValueError as error:
            raise SourceAdmissionError(str(error)) from error
        if not p.resolve().is_relative_to(root) or hashlib.sha256(raw).hexdigest()!=row['sha256']:
            raise SourceAdmissionError('Changed current C_CI source: '+row['path'])
    return value


def native_cci(root):
    value=checked_record(root)
    keys=('status','native_endpoint_verified','native_completion_support','full_trajectory_runs',
        'endpoint_expectations_verified','family','target_vertices','target_edges','numerical_policy_id',
        'certificate_precision_bits','sampling_cap_seconds','elapsed_seconds','estimate','memory','stop_conditions',
        'synthetic_window_scope','reset_scope','expected_endpoints')
    body={k:value[k] for k in keys}
    body.update(pressure=native_cci_pressure(root),schema='grc9v4_native_cci_preflight_surface_v1',record_digest=value['record_digest'],
        sample_counts={role:len(rows) for role,rows in value['samples'].items()},
        flint_version=value['machine']['flint'],flint_threads=value['machine']['flint_threads'],
        tests=value['tests'],root_cache=value['caches']['root_final'],
        precision_comparison_passed=value['precision_comparison']['identical_represented_states'],
        next_leaf='P9-9.1a.6-C_CI.5',source_url='/api/native-spark/c-ci/preflight/source')
    return dict(body,projection_digest=digest(body))


def native_cci_source(root):
    checked_record(root)
    return (Path(root)/RECORD).read_bytes()
