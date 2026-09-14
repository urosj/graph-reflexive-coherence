"""Independent published-byte and adversarial codec/installed-asset tests."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from copy import deepcopy
from hashlib import sha256
import importlib
from importlib import resources
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import tarfile
from typing import Any
import unittest
from unittest.mock import patch
import venv
import zipfile

from pygrc.models import grc_v4_codec as codec
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/pygrc/models/grc_v4_assets"
VECTORS = ROOT / "specs/grc-v4-conformance-vectors.json"

# Test-only external consumer, passed as source to an isolated interpreter.
# It imports only the actual installed distribution; fixture data arrives on
# stdin. Nothing here is shipped as a runtime adapter or support registration.
INSTALLED_CONSUMER = r'''
import copy, hashlib, importlib, importlib.metadata, importlib.util, inspect
import json, math, operator, sys, sysconfig
from pathlib import Path

data = json.load(sys.stdin)
mode, order = sys.argv[1:3]
checks = []
def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)
def rejects(name, exception, call):
    try:
        call()
    except exception as exc:
        checks.append(name + ':' + type(exc).__name__)
    else:
        raise AssertionError(name + ': guard did not reject')
def digest(value):
    from pygrc.core.serialization import canonical_json_dumps
    return hashlib.sha256(canonical_json_dumps(value).encode()).hexdigest()
def legacy_value(value):
    # Legacy observables legitimately have integer keys; do not run them
    # through V4 I-JSON or alter the legacy serializer to make that legal.
    if isinstance(value,dict):
        return ['mapping',[[legacy_value(k),legacy_value(v)] for k,v in
                          sorted(value.items(),key=lambda item:(type(item[0]).__name__,repr(item[0])))]]
    if isinstance(value,(list,tuple,set,frozenset)):
        items=sorted(value,key=repr) if isinstance(value,(set,frozenset)) else value
        return [type(value).__name__,[legacy_value(v) for v in items]]
    if value is None or type(value) in (str,int,float,bool):
        return [type(value).__name__,repr(value)]
    raise TypeError('unhandled legacy observation: '+type(value).__name__)
def imports():
    for name in ('grc_v4', 'grc_v4_state', 'grc_v4_profile', 'grc_v4_codec', 'grc_v4_step'):
        importlib.import_module('pygrc.models.' + name)
def legacy():
    from pygrc import models
    from pygrc.core import FAMILY_CAPABILITY_PROFILES
    from pygrc.core.serialization import canonical_json_dumps
    output = {}
    check('four-family-capability-roster', set(FAMILY_CAPABILITY_PROFILES) ==
          {'GRCV2', 'GRCV3', 'GRC9', 'GRC9V3'})
    for name in ('GRCV2', 'GRCV3', 'GRC9', 'GRC9V3', 'LGRC9V3'):
        cls = getattr(models, name)
        check('legacy-export:' + name, cls.__module__ == data['legacy_modules'][name])
        config = data['legacy_config'] if name == 'GRCV2' else {'dt': 0.1}
        model = cls.from_config(copy.deepcopy(config))
        initial = canonical_json_dumps(model.snapshot())
        first = model.step()
        more = model.run(1)
        check('legacy-run:' + name, len(more) == 1)
        current = canonical_json_dumps(model.snapshot())
        saved = Path(name + '-consumer.json')
        model.save(str(saved))
        restored = cls.load(str(saved))
        check('legacy-restoration:' + name,
              canonical_json_dumps(restored.snapshot()) == current)
        restored.step()
        check('legacy-restoration-independence:' + name,
              canonical_json_dumps(model.snapshot()) == current)
        model.reset()
        check('legacy-reset:' + name, canonical_json_dumps(model.snapshot()) == initial)
        rejects('legacy-negative-run:' + name, ValueError, lambda: model.run(-1))
        check('legacy-negative-run-no-mutation:' + name,
              canonical_json_dumps(model.snapshot()) == initial)
        output[name] = {
            'initial_snapshot_sha256': hashlib.sha256(initial.encode()).hexdigest(),
            'two_step_snapshot_sha256': hashlib.sha256(current.encode()).hexdigest(),
            'first_result_type': type(first).__name__,
            'capabilities': sorted(model.list_capabilities()),
            'observables': legacy_value(model.compute_observables()),
            'signatures': {n: str(inspect.signature(getattr(cls,n))) for n in
                           ('from_config','from_state','get_state','set_state',
                            'step','run','reset','snapshot','save','load')},
        }
    return output

check('no-checkout-imports-initially', not any(n.startswith(('tests.', 'grcv4_explorer'))
                                             for n in sys.modules))
if order == 'foundation-first':
    imports()
before = legacy()
if order != 'foundation-first':
    check('legacy-does-not-import-v4', not any(n.startswith('pygrc.models.grc_v4')
                                              for n in sys.modules))
imports()
from pygrc.models import grc_v4_codec as c, grc_v4_profile as p, grc_v4 as api
from pygrc.models import grc_v4_step as step, grc_v4_state as state
check('support-exact-accepted-singleton', p.list_supported_profiles() == frozenset({'grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d', 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4', 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946'}))
if mode in ('absent','rfc-only','validator-only'):
    for name in ('rfc8785', 'jsonschema'):
        present = (mode=='rfc-only' and name=='rfc8785') or (mode=='validator-only' and name=='jsonschema')
        check('actual-dependency-state:' + name, (importlib.util.find_spec(name) is not None)==present)
    if mode=='rfc-only':
        check('partial-extra-JCS-works',c.canonical_json_bytes({'x':1})==b'{"x":1}')
        rejects('missing-schema-dependency',c.V4DependencyError,
                lambda:c.validate_payload('step_request_input',data['prefix']['request']))
    else:
        rejects('missing-JCS-dependency', c.V4DependencyError,
                lambda: c.canonical_json_bytes({'x': 1}))
else:
    for name in ('rfc8785', 'jsonschema'):
        check('declared-dependency-present:' + name, importlib.util.find_spec(name) is not None)
    schema = c.load_contract_schema()
    schema.clear()
    check('schema-copy-isolation', '$defs' in c.load_contract_schema())
    for row in data['published']:
        check('published-bytes:' + row['vector_id'],
              c.canonical_json_bytes(row['payload']).hex() == row['canonical_jcs_utf8_hex'])
        if row['schema_ref'] != 'RFC8785':
            check('published-identity:' + row['vector_id'],
                  c.payload_identity(row['schema_ref'], row['payload']) == row['expected_identifier'])
    profile = p.GRCV4Profile.from_canonical_bytes(bytes.fromhex(data['profile_hex']))
    check('large-coefficient-count-roundtrip', profile.to_canonical_bytes().hex() == data['profile_hex']
          and type(profile.params_resolved.solver.iteration_limit) is int)
    for label in (profile.complete_profile_id, 'C_OS', 'grcv4-profile-sha256:'+'f'*64,
                  'grc9v4-model-sha256:'+'1'*64, data['template_id']):
        rejects('unsupported-lookup:' + label, c.V4IdentityError, lambda: p.get_supported_profile(label))
    for value in (True, 1.5, -0.0, 2**53):
        payload = profile.params_resolved.solver.to_payload()
        payload['iteration_limit'] = value
        rejects('invalid-original-count', (c.V4SchemaError,c.V4WireError),
                lambda: p.SolverPolicy.from_payload(payload))
    for count in (10, 10.0):
        payload = profile.params_resolved.solver.to_payload()
        payload['iteration_limit'] = count
        check('integral-count-stays-int', type(p.SolverPolicy.from_payload(payload).iteration_limit) is int)
    import numpy as np
    safe = np.array([2**53-1],dtype=np.int64)
    check('safe-integral-adapter', state.GRCV4AuthoritativeState(safe,None,None).C == (float(2**53-1),))
    for value in (np.int64(2**53+1),np.int64(-(2**63)),np.uint64(2**64-1)):
        rejects('unsafe-integral-adapter', (TypeError,ValueError),
                lambda: state.GRCV4AuthoritativeState([value],None,None))
    for bad in ({0:1}, {1}, '1', b'1'):
        rejects('unordered-or-raw-vector', (TypeError,ValueError),
                lambda: state.GRCV4AuthoritativeState(bad,None,None))
    a = np.array([1.,2.,3.,4.]); w = np.array([.5,.75]); z = np.array([.125,.25])
    owned = state.GRCV4AuthoritativeState(a[::2],w[::-1],z)
    a[:]=9; w[:]=9; z[:]=9
    check('all-coordinate-view-ownership', (owned.C,owned.W_A,owned.Z_4)==((1.,3.),(.75,.5),(.125,.25)))
    check('boolean-distinct', c.canonical_json_bytes({'x': True}) != c.canonical_json_bytes({'x': 1}))
    check('safe-number-equivalence', c.canonical_json_bytes({'x': 1.}) == b'{"x":1}')
    check('unicode-not-normalized', c.canonical_json_bytes('é') != c.canonical_json_bytes('e\u0301'))
    check('utf16-key-order', c.canonical_json_bytes({'\ue000':1,'\U00010000':2}) ==
          '{"\U00010000":2,"\ue000":1}'.encode())
    for suffix in ('\n', ' ', ':suffix'):
        payload = profile.to_payload(); payload['complete_profile_id'] += suffix
        rejects('whole-string-profile-id', (c.V4IdentityError,c.V4SchemaError),
                lambda: p.GRCV4Profile.from_canonical_bytes(c.canonical_json_bytes(payload)))
    for dt in (float(2**53),1e20,math.nextafter(1e21,0),5e-324):
        payload = copy.deepcopy(data['prefix']['request']); payload['dt']=dt
        raw = c.canonical_json_bytes(payload)
        check('canonical-request-roundtrip', api.decode_step_request_input(raw,encoding='canonical').to_canonical_bytes()==raw)
        if dt >= 2**53:
            rejects('no-automatic-configuration-fallback', c.V4WireError,
                    lambda: api.decode_step_request_input(raw))
    for token, valid in (('1e-4000',False),('0e-4000',True),('5e-324',True)):
        wire = json.dumps(data['prefix']['request']).replace('-0.25',token)
        if valid:
            check('zero-or-subnormal-wire', api.decode_step_request_input(wire).dt >= 0)
        else:
            rejects('nonzero-underflow',c.V4WireError,lambda: api.decode_step_request_input(wire))
    f = copy.deepcopy(data['prefix']); original = copy.deepcopy(f)
    request = api.GRCV4StepRequestInput.from_payload(f['request'])
    result,evidence = step.negative_duration_result(request,prestate=f['prestate'],
        receipt_ledger=f['pre_ledger'],active_profile_id=f['source_profile_id'])
    expected = data['expected_negative']
    check('actual-negative-prefix', result.operation_disposition=='rejected' and
          result.solver_disposition is None and not result.committed and result.commit_id is None)
    check('independent-failure-receipt', result.to_payload()['emitted_receipts']==expected['emitted_receipts'])
    check('complete-pre-post-and-ledger', evidence.prestate_bytes==evidence.poststate_bytes and
          evidence.pre_ledger_bytes==evidence.post_ledger_bytes and f==original)
    f['prestate']['authoritative']['C'][0]=999
    check('captured-evidence-owned', evidence.prestate_bytes==c.canonical_json_bytes(original['prestate']))
    # Successful content is reconstructed, not executed as an operation.
    payload=copy.deepcopy(data['successful_result'])
    reconstructed=state.GRCV4StepResult.from_payload(payload)
    captured=reconstructed.to_payload()
    payload['events'][0]['payload'].clear()
    event=reconstructed.events[0]; sibling=reconstructed.events[0]
    event.payload.clear()
    check('common-event-is-detached', bool(sibling.payload) and reconstructed.to_payload()==captured)
    for bad in ({},set(),' ',b'',iter([])):
        invalid=copy.deepcopy(data['successful_result']); invalid['events']=bad
        rejects('outer-event-container', (TypeError,ValueError),
                lambda: state.GRCV4StepResult(**{k:v for k,v in invalid.items() if k!='schema_version'}))
    projection=reconstructed.to_payload(); projection['observables'].clear()
    check('result-projection-owned', reconstructed.to_payload()==captured)
    check('support-not-expanded', p.list_supported_profiles()==frozenset({'grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d', 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4', 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946'}))
after=legacy()
check('mixed-legacy-behavior-unchanged',before==after)
check('no-test-or-investigation-imports',not any(n.startswith(('tests.','grcv4_explorer')) for n in sys.modules))
site=Path(sysconfig.get_path('purelib')).resolve()
origins=[]
for name,module in sorted(tuple(sys.modules.items())):
    if name=='pygrc' or name.startswith('pygrc.'):
        origin=Path(module.__file__).resolve()
        check('installed-origin:'+name,origin.is_relative_to(site/'pygrc'))
        relative='src/'+origin.relative_to(site).as_posix()
        sha=hashlib.sha256(origin.read_bytes()).hexdigest()
        check('source-bytes:'+name,data['source_members'][relative]==sha)
        origins.append({'module':name,'path':relative,'sha256':sha})
for relative,sha in data['source_members'].items():
    path=site/relative.removeprefix('src/')
    check('installed-member:'+relative,path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==sha)
print(json.dumps({'checks':checks,'legacy':before,'origins':origins,
 'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
 'prefix':result.to_payload() if mode=='full' else None,
 'evidence_class':'installed_foundation_consumer_not_profile_conformance',
 'runtime_support':[]},sort_keys=True))
'''

INSTALLED_ASSET_PRESSURE = r'''
from importlib.resources import files
import hashlib,json,subprocess,sys
from pathlib import Path
from pygrc.models import grc_v4_codec as c
assets=Path(str(files('pygrc.models.grc_v4_assets')))
names=['asset-index.json','grc-v4-contract-schema.json',
       'grc-v4-specification-release.json','grc-v4-specification-release.sha256']
originals={n:(assets/n).read_bytes() for n in names}
# These valid same-named neighbor files are deliberately not lookup authority.
neighbor=Path('specs'); neighbor.mkdir()
for name,raw in originals.items(): (neighbor/name).write_bytes(raw)
cold="""
from pygrc.models.grc_v4_codec import load_contract_schema,V4AssetError
try:
    load_contract_schema()
except V4AssetError:
    print('asset_rejected')
else:
    raise AssertionError('cold installed asset guard bypassed')
"""
cases=[]
for name in names:
    path=assets/name
    for action in ('missing','one-byte-change'):
        c.load_contract_schema()
        held=path.with_name(name+'.held')
        try:
            if action=='missing': path.rename(held)
            else: path.write_bytes(originals[name][:-1]+bytes([originals[name][-1]^1]))
            try: c.load_contract_schema()
            except c.V4AssetError: pass
            else: raise AssertionError('warm installed asset guard bypassed')
            result=subprocess.run([sys.executable,'-I','-c',cold],capture_output=True,text=True)
            assert result.returncode==0 and result.stdout.strip()=='asset_rejected',result.stderr
            cases.append({'asset':name,'fault':action,'warm':'V4AssetError','cold':'V4AssetError'})
        finally:
            if action=='missing': held.rename(path)
            else: path.write_bytes(originals[name])
        c.load_contract_schema()
for action in ('wrong-release','self-consistent-replacement'):
    try:
        index=json.loads(originals['asset-index.json'])
        if action=='wrong-release': index['release_id']='different-release'
        else:
            schema=json.loads(originals['grc-v4-contract-schema.json']); schema['title']='replacement'
            (assets/'grc-v4-contract-schema.json').write_text(json.dumps(schema))
            manifest=json.loads(originals['grc-v4-specification-release.json'])
            new_schema_sha=hashlib.sha256((assets/'grc-v4-contract-schema.json').read_bytes()).hexdigest()
            for row in manifest['release_identity_payload']['artifact_bindings']:
                if row['path']=='specs/grc-v4-contract-schema.json': row['sha256']=new_schema_sha
            preimage=c.canonical_json_bytes(manifest['release_identity_payload'])
            manifest['release_identity_canonical_jcs_utf8']=preimage.decode()
            manifest['release_id']='grcv4-spec-release-sha256:'+hashlib.sha256(preimage).hexdigest()
            index['release_id']=manifest['release_id']
            (assets/'grc-v4-specification-release.json').write_text(json.dumps(manifest))
            (assets/'grc-v4-specification-release.sha256').write_text(
                hashlib.sha256((assets/'grc-v4-specification-release.json').read_bytes()).hexdigest()+
                '  specs/grc-v4-specification-release.json\n')
            for row in index['files']:
                row['sha256']=hashlib.sha256((assets/row['name']).read_bytes()).hexdigest()
        (assets/'asset-index.json').write_text(json.dumps(index))
        result=subprocess.run([sys.executable,'-I','-c',cold],capture_output=True,text=True)
        assert result.returncode==0 and result.stdout.strip()=='asset_rejected',result.stderr
        cases.append({'asset':'asset-index.json','fault':action,'cold':'V4AssetError'})
    finally:
        for name,raw in originals.items(): (assets/name).write_bytes(raw)
    c.load_contract_schema()
print(json.dumps({'controls':cases,'nearby-valid-assets-ignored':True}))
'''

LAST_DISTRIBUTION_EVIDENCE: dict[str, Any] = {}


def vectors() -> dict[str, Any]:
    value = json.loads(VECTORS.read_text())
    assert isinstance(value, dict)
    return value


class CodecTests(unittest.TestCase):
    def test_canonical_numeric_reconstruction_closes_the_encoder_image(self) -> None:
        values = [0.0, 1.0, 0.125, float(2**53 - 1), float(2**53),
                  math.nextafter(float(2**53), math.inf), 1e16, 1e20,
                  2.0**68, math.nextafter(1e21, 0), 1e21,
                  math.nextafter(1e21, math.inf), 1e22, 1e-6, 1e-7,
                  5e-324, sys.float_info.max]
        values += [-value for value in values if value > 0]
        for value in values:
            with self.subTest(value=value):
                original = codec.canonical_json_bytes({"value": value})
                decoded = codec.decode_canonical_json(original)
                self.assertEqual(codec.canonical_json_bytes(decoded), original)
                self.assertEqual(decoded, {"value": value})
        # The strict configuration decoder keeps its original input policy.
        with self.assertRaises(codec.V4WireError):
            codec.decode_json("9007199254740992")
        self.assertEqual(codec.decode_json("9007199254740992.0"), float(2**53))

    def test_canonical_route_rejects_rounding_and_noncanonical_spellings(self) -> None:
        invalid = ["9007199254740993", "-9007199254740993", "1.0", "1e20",
                   "1e-324", "-0", "-0.0", "NaN", "Infinity", "1e999",
                   '{"x":1,"x":2}', '{"x":1,"\\u0078":2}', '"\\ud800"',
                   '{"z":0,"a":0}', " {}", "{}\n", "\ufeff{}"]
        for wire in invalid:
            with self.subTest(wire=wire), self.assertRaises(codec.V4WireError):
                codec.decode_canonical_json(wire)
        for raw in [b"\xff", b"\xef\xbb\xbf{}"]:
            with self.assertRaises(codec.V4WireError):
                codec.decode_canonical_json(raw)

    def test_canonical_numeric_tokens_still_obey_field_schemas(self) -> None:
        data = vectors()["identity_vectors"][0]["payload"]["solver"]
        for invalid in [float(2**53), True, 1.5]:
            data["iteration_limit"] = invalid
            decoded = codec.decode_canonical_json(codec.canonical_json_bytes(data))
            with self.assertRaises(codec.V4SchemaError):
                codec.validate_payload("solver_policy", decoded)

    def test_all_published_canonical_preimages(self) -> None:
        bundle = vectors()
        rows = (bundle["canonicalization_vectors"] + bundle["identity_vectors"]
                + bundle["subdigest_identity_vectors"])
        self.assertEqual(len(rows), 25)
        for row in rows:
            with self.subTest(vector=row["vector_id"]):
                actual = codec.canonical_json_bytes(row["payload"])
                self.assertEqual(actual, row["canonical_jcs_utf8"].encode("utf-8"))
                self.assertEqual(actual.hex(), row["canonical_jcs_utf8_hex"])
                self.assertEqual(sha256(actual).hexdigest(),
                                 row["expected_identifier"].split(":")[1])
                if row["schema_ref"] != "RFC8785":
                    self.assertEqual(
                        codec.payload_identity(row["schema_ref"], row["payload"]),
                        row["expected_identifier"],
                    )

    def test_independent_ecmascript_binary64_edges(self) -> None:
        # Published RFC 8785 Appendix B bit patterns; no production serializer
        # computes expected values. V4 rejects negative zero separately.
        cases = {
            "0000000000000001": b"5e-324",
            "8000000000000001": b"-5e-324",
            "7fefffffffffffff": b"1.7976931348623157e+308",
            "ffefffffffffffff": b"-1.7976931348623157e+308",
            "4340000000000000": b"9007199254740992",
            "4430000000000000": b"295147905179352830000",
            "44b52d02c7e14af5": b"9.999999999999997e+22",
            "44b52d02c7e14af6": b"1e+23",
            "44b52d02c7e14af7": b"1.0000000000000001e+23",
            "444b1ae4d6e2ef50": b"1e+21",
            "3eb0c6f7a0b5ed8d": b"0.000001",
        }
        for bits, expected in cases.items():
            with self.subTest(bits=bits):
                value = struct.unpack(">d", bytes.fromhex(bits))[0]
                self.assertEqual(codec.canonical_json_bytes(value), expected)

    def test_unicode_order_preservation_and_escapes(self) -> None:
        self.assertEqual(
            codec.canonical_json_bytes({"\ue000": 1, "😀": 2, "\r": 3}),
            '{"\\r":3,"😀":2,"\ue000":1}'.encode(),
        )
        self.assertNotEqual(codec.canonical_json_bytes("é"),
                            codec.canonical_json_bytes("e\u0301"))
        self.assertEqual(codec.canonical_json_bytes('"\\\n\t\x00'),
                         b'"\\"\\\\\\n\\t\\u0000"')

    def test_boolean_number_identity_is_distinct(self) -> None:
        for a, b in [(True, 1), (False, 0), ([True], [1]),
                     ({"x": False}, {"x": 0})]:
            self.assertNotEqual(codec.canonical_json_bytes(a),
                                codec.canonical_json_bytes(b))
        self.assertEqual(codec.canonical_json_bytes(1),
                         codec.canonical_json_bytes(1.0))

    def test_strict_wire_numbers_duplicates_and_unicode(self) -> None:
        bad = [
            '{"a":1,"a":2}', '{"nested":{"a":1,"\\u0061":2}}',
            "NaN", "Infinity", "-Infinity", "-0", "-0.0", "-0e8", "-1e-999",
            "9007199254740992", "-9007199254740992", "1e999",
            '"\\ud800"', '{"\\udfff":1}', '{"a":1,}', "\ufeff{}",
        ]
        for text in bad:
            with self.subTest(text=text), self.assertRaises(codec.V4WireError):
                codec.decode_json(text)
        for raw in [b"\xff", b"\xff\xfe{\x00}", b"\xef\xbb\xbf{}"]:
            with self.assertRaises(codec.V4WireError):
                codec.decode_json(raw)
        self.assertEqual(codec.decode_json('{"x":[true,null,0]}'),
                         {"x": [True, None, 0]})
        self.assertEqual(codec.decode_json("9007199254740991"), 2**53 - 1)
        self.assertEqual(codec.decode_json("9007199254740992.0"), float(2**53))

    def test_configuration_rejects_coercions_cycles_and_unordered_data(self) -> None:
        cycle: list[Any] = []
        cycle.append(cycle)
        invalid = [float("nan"), float("inf"), -0.0, 2**53, {1: "x"},
                   {1, 2}, b"123", iter([1, 2]), object(), cycle, "\udfff"]
        for value in invalid:
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(codec.V4WireError):
                    codec.canonical_json_bytes(value)

    def test_custom_mapping_duplicate_and_defensive_projection(self) -> None:
        class Duplicate(Mapping[str, int]):
            def __iter__(self) -> Iterator[str]:
                return iter(("x", "x"))

            def __len__(self) -> int:
                return 2

            def __getitem__(self, key: str) -> int:
                return 1

        with self.assertRaises(codec.V4WireError):
            codec.json_value(Duplicate())
        data = {"a": [{"b": 1}]}
        projected = codec.json_value(data)
        data["a"][0]["b"] = 2
        self.assertEqual(projected, {"a": [{"b": 1}]})

    def test_schema_negatives_and_no_remote_schema_selection(self) -> None:
        for row in vectors()["semantic_admission"]["schema_negative_vectors"]:
            with self.subTest(vector=row["vector_id"]):
                with self.assertRaises(codec.V4SchemaError):
                    codec.validate_payload(row["schema_ref"], row["input"])
        for ref in ["https://example.invalid/schema", "../schema", "$defs"]:
            with self.assertRaises(codec.V4SchemaError):
                codec.validate_payload(ref, {})

    def test_identity_tampering_unknown_fields_and_non_preimages(self) -> None:
        for row in vectors()["identity_vectors"]:
            with self.subTest(vector=row["vector_id"]):
                with self.assertRaises(codec.V4IdentityError):
                    codec.payload_identity(row["schema_ref"], row["payload"],
                                           expected="wrong")
                value = deepcopy(row["payload"])
                value["self_digest"] = row["expected_identifier"]
                with self.assertRaises(codec.V4SchemaError):
                    codec.payload_identity(row["schema_ref"], value)
        with self.assertRaises(codec.V4SchemaError):
            codec.payload_identity("candidate_c_params", {})

    def test_missing_optional_dependencies_are_typed(self) -> None:
        real_import = importlib.import_module
        for dependency in ["rfc8785", "jsonschema"]:
            def missing(name: str, *args: Any, **kwargs: Any) -> Any:
                if name == dependency:
                    raise ModuleNotFoundError(name)
                return real_import(name, *args, **kwargs)

            with patch.object(importlib, "import_module", side_effect=missing):
                with self.assertRaises(codec.V4DependencyError):
                    codec.validate_payload("resolved_params", {})

    def test_installed_assets_are_exact_release_copies_and_unshared(self) -> None:
        for name in ["grc-v4-contract-schema.json",
                     "grc-v4-specification-release.json",
                     "grc-v4-specification-release.sha256"]:
            self.assertEqual((ASSETS / name).read_bytes(),
                             (ROOT / "specs" / name).read_bytes())
        schema = codec.load_contract_schema()
        schema.clear()
        self.assertIn("$defs", codec.load_contract_schema())

    def test_missing_altered_wrong_release_assets_fail_closed(self) -> None:
        # An explicit test double exercises installed-resource reads, not a
        # production override or repository fallback.
        originals = {p.name: p.read_bytes() for p in ASSETS.iterdir() if p.is_file()}

        class Resource:
            def __init__(self, files: dict[str, bytes], name: str = ""):
                self.files, self.name = files, name

            def joinpath(self, name: str) -> Resource:
                return Resource(self.files, name)

            def read_bytes(self) -> bytes:
                if self.name not in self.files:
                    raise FileNotFoundError(self.name)
                return self.files[self.name]

        for name in [n for n in originals if n.endswith((".json", ".sha256"))]:
            for action in ["missing", "altered"]:
                modified = dict(originals)
                if action == "missing":
                    del modified[name]
                else:
                    modified[name] += b" "
                with self.subTest(name=name, action=action):
                    with patch.object(resources, "files",
                                      return_value=Resource(modified)):
                        with self.assertRaises(codec.V4AssetError):
                            codec.load_contract_schema()
        modified = dict(originals)
        index = json.loads(modified["asset-index.json"])
        index["release_id"] = "wrong-release"
        modified["asset-index.json"] = json.dumps(index).encode()
        with patch.object(resources, "files", return_value=Resource(modified)):
            with self.assertRaises(codec.V4AssetError):
                codec.load_contract_schema()

    def test_wide_frozen_maps_do_not_use_per_key_linear_lookup(self) -> None:
        # Structural scale check, not a machine-specific timing threshold.
        for size in [16, 256, 4096]:
            data = {f"edge-{i}": {"weight": i} for i in range(size)}
            left, right = FrozenJSONMap(data), FrozenJSONMap(data)
            with patch.object(FrozenJSONMap, "__getitem__",
                              side_effect=AssertionError("quadratic traversal")):
                self.assertEqual(left, right)
                self.assertEqual(FrozenJSONMap(left), right)
                self.assertEqual(codec.canonical_json_bytes(left),
                                 codec.canonical_json_bytes(data))


@unittest.skipUnless(os.environ.get("GRCV4_PACKAGE_TESTS") == "1",
                     "opt-in clean wheel/sdist installation test")
class DistributionTests(unittest.TestCase):
    def test_wheel_and_sdist_offline_clean_install(self) -> None:
        from pygrc.models.grc_v4_profile import resolve_profile
        from pygrc.models.grc_v4_state import GRCV4StepResult
        from tests.models.grcv4_reference_oracles import prefix_fixture, expected_negative
        from tests.models.test_grc_v4_profile import fixture, reidentify
        from tests.models.test_grc_v4_state import result_fixture, successful_fixture

        params, identity = fixture()
        params["candidate"]["kappa_Phi_C"] = 1e20
        params["solver"]["iteration_limit"] = 10.0
        reidentify(params, identity)
        prefix = prefix_fixture()
        prefix["pre_ledger"] = [successful_fixture()]
        members = {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest()
                   for p in sorted((ROOT / "src/pygrc").rglob("*.py"))}
        members.update({p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest()
                        for p in ASSETS.iterdir() if p.suffix in (".json", ".sha256")})
        supplied = {
            "profile_hex": resolve_profile(params, identity).to_canonical_bytes().hex(),
            "prefix": prefix,
            "expected_negative": expected_negative(prefix["request"], prefix["prestate"],
                                                   prefix["pre_ledger"]),
            "successful_result": GRCV4StepResult(**result_fixture()).to_payload(),
            "published": vectors()["canonicalization_vectors"] + vectors()["identity_vectors"],
            "template_id": next(r["expected_identifier"] for r in vectors()["identity_vectors"]
                                if r["schema_ref"] == "#/$defs/profile_template_payload"),
            "legacy_config": importlib.import_module(
                "tests.models.test_reset_baseline_persistence")._valid_grcv2_config(),
            "legacy_modules": dict(GRCV2="pygrc.models.grc_v2",GRCV3="pygrc.models.grc_v3",
                                   GRC9="pygrc.models.grc_9",GRC9V3="pygrc.models.grc_9_v3",
                                   LGRC9V3="pygrc.models.lgrc_9_v3_runtime"),
            "source_members": members,
        }
        wheelhouse = Path(os.environ["GRCV4_WHEELHOUSE"]).resolve()
        self.assertTrue(wheelhouse.is_dir())
        generated = ROOT / (
            "implementation/investigations/grc9v4-constitutive-design/tools/"
            "exploratory-side-tool/tool/generated")
        generated.mkdir(parents=True, exist_ok=True)
        records: dict[str, Any] = {
            "fixture": supplied, "consumer_sha256": sha256(INSTALLED_CONSUMER.encode()).hexdigest(),
            "archives": [], "cells": [], "origin_sets": {}, "legacy_baseline": None,
            "build_tools": {}, "asset_controls": [],
        }
        from importlib.metadata import version
        records["build_tools"] = {n: version(n) for n in ("build","setuptools","wheel","pip")}
        with tempfile.TemporaryDirectory(prefix="grcv4-p926-package-", dir=generated) as scratch:
            temp = Path(scratch)
            source = temp / "source"
            source.mkdir()
            shutil.copytree(ROOT / "src", source / "src",
                            ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
            for name in ["pyproject.toml", "README.md", "LICENSE"]:
                shutil.copyfile(ROOT / name, source / name)

            def run(command: list[str], cwd: Path, *, stdin: str | None = None) -> str:
                env = {k: v for k, v in os.environ.items()
                       if k not in {"PYTHONPATH", "PYTHONHOME"}}
                result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                        text=True, input=stdin, timeout=240)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout

            dist = temp / "dist"
            run([sys.executable, "-m", "build", "--no-isolation",
                 "--outdir", str(dist)], source)
            archives = [next(dist.glob("*.whl")), next(dist.glob("*.tar.gz"))]
            for archive in archives:
                if archive.suffix == ".whl":
                    with zipfile.ZipFile(archive) as package:
                        for relative, expected in members.items():
                            self.assertEqual(sha256(package.read(relative.removeprefix("src/"))).hexdigest(),expected)
                        self.assertFalse(any(n.startswith(("tests/","implementation/")) for n in package.namelist()))
                else:
                    with tarfile.open(archive) as source_package:
                        prefix_name = source_package.getnames()[0].split("/")[0]
                        for relative, expected in members.items():
                            stream = source_package.extractfile(prefix_name + "/" + relative)
                            self.assertIsNotNone(stream)
                            assert stream is not None
                            self.assertEqual(sha256(stream.read()).hexdigest(), expected)
                        self.assertFalse(any("/tests/" in n or "/implementation/" in n for n in source_package.getnames()))
                records["archives"].append({"name": archive.name,
                    "sha256": sha256(archive.read_bytes()).hexdigest(),
                    "production_members_verified": len(members)})
                for mode in ("absent", "full"):
                    cell = ("wheel" if archive.suffix == ".whl" else "sdist") + "-" + mode
                    environment = temp / (cell + "-env")
                    venv.EnvBuilder(with_pip=True).create(environment)
                    python = environment / "bin/python"
                    outside = temp / (cell + "-consumer")
                    outside.mkdir()
                    run([str(python), "-m", "pip", "install", "--no-index",
                         "--find-links", str(wheelhouse), str(archive) + ("[v4]" if mode == "full" else "")], outside)
                    def consume(selected_mode: str, order: str) -> None:
                        result = json.loads(run([str(python), "-I", "-c", INSTALLED_CONSUMER,
                                                 selected_mode, order], outside,
                                                stdin=json.dumps(supplied)))
                        if records["legacy_baseline"] is None:
                            records["legacy_baseline"] = result["legacy"]
                        self.assertEqual(result.pop("legacy"), records["legacy_baseline"],
                                         "legacy behavior changed with installation/import state")
                        origins = result.pop("origins")
                        origin_id = sha256(json.dumps(origins,sort_keys=True).encode()).hexdigest()
                        records["origin_sets"][origin_id] = origins
                        records["cells"].append({"cell": cell, "mode": selected_mode, "order": order,
                            "exit_code": 0, "origin_set_sha256": origin_id, **result})
                    for order in ("legacy-first","foundation-first","failure-then-legacy"):
                        consume(mode,order)
                    run([str(python), "-m", "pip", "check"], outside)
                    if mode == "absent":
                        run([str(python),"-m","pip","install","--no-index",
                             "--find-links",str(wheelhouse),"rfc8785==0.1.4"],outside)
                        consume("rfc-only","failure-then-legacy")
                        run([str(python),"-m","pip","uninstall","-y","rfc8785"],outside)
                        run([str(python),"-m","pip","install","--no-index",
                             "--find-links",str(wheelhouse),"jsonschema==4.26.0"],outside)
                        consume("validator-only","failure-then-legacy")
                    if mode == "full":
                        # Real installed assets, warmed reads and independent
                        # cold processes; valid neighboring files cannot rescue
                        # a missing installed asset.
                        output = run([str(python), "-I", "-c", INSTALLED_ASSET_PRESSURE],
                                     outside)
                        records["asset_controls"].append({"cell":cell, **json.loads(output)})
        LAST_DISTRIBUTION_EVIDENCE.clear()
        LAST_DISTRIBUTION_EVIDENCE.update(records)

if __name__ == "__main__":
    unittest.main()
