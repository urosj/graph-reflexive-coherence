"""Bounded native C_CI pressure evidence; never a completion endpoint grant."""
from pathlib import Path
import hashlib
from .canonical import load_json_object, record_digest, digest
from .errors import SourceAdmissionError

RECORD='implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CCI-Pressure.json'
RECORD_DIGEST='ffd8933a4446d15efb7ba5aad2b00d17dc6a7e431b51acb30f8a71a97e76b71d'


def checked_record(root):
    import sys
    sys.path.insert(0, str(Path(root)/"implementation/phase-9-grcv4/verification"))
    from p991a6_cci_campaign_epoch import previous_bytes
    root=Path(root).resolve();value=load_json_object(root/RECORD)
    if (value.get('record_digest')!=RECORD_DIGEST or record_digest(value,'record_digest')!=RECORD_DIGEST
        or value.get('schema')!='grc9v4-native-cci-pressure-v1' or value.get('family')!='C_CI'
        or value.get('native_endpoint_verified') is not False or value.get('native_completion_support') is not False
        or value.get('full_trajectory_runs')!=0 or value.get('tests_passed')!=22):
        raise SourceAdmissionError('Unbound C_CI pressure or changed endpoint scope')
    for row in [*value['source_bindings'],value['evidence']]:
        p=root/row['path']
        try:
            raw = previous_bytes(root, row["path"])
        except ValueError as error:
            raise SourceAdmissionError(str(error)) from error
        if not p.resolve().is_relative_to(root) or hashlib.sha256(raw).hexdigest()!=row['sha256']:
            raise SourceAdmissionError('Changed C_CI pressure source: '+row['path'])
    return value


def native_cci_pressure(root):
    value=checked_record(root)
    body=dict(schema='grc9v4_native_cci_pressure_surface_v1',record_digest=value['record_digest'],
        tests_passed=value['tests_passed'],root_mutations=len(value['measurements']['root_mutations']),
        finite_segment_directions=len(value['measurements']['finite_segments']),
        native_endpoint_verified=False,native_completion_support=False,full_trajectory_runs=0,
        scope=value['scope'],pending_campaign=value['pending_campaign'],
        source_url='/api/native-spark/c-ci/pressure/source')
    return dict(body,projection_digest=digest(body))


def native_cci_pressure_source(root):
    checked_record(root)
    return (Path(root)/RECORD).read_bytes()
