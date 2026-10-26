"""Exact-content memo parity, invalidation, limits and lifetime."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import p984h_validation_reuse as r


class ValidationReuseTests(unittest.TestCase):
    def test_large_success_parity_detachment_and_changed_content(self):
        c=r.codec;data=dict(schema_version='grcv4-k4-identity-v1',K4_base=[[0.]*64 for _ in range(64)])
        original=c.payload_identity('k4_identity_payload',data)
        _,raw=c._load_contract_schema();validator=c._contract_validator(raw,'k4_identity_payload')
        cache=c._VALIDATED_PAYLOADS;limit=c._VALIDATION_MAX_BYTES
        with r.validation_reuse():
            self.assertEqual(c.payload_identity('k4_identity_payload',data),original)
            with patch.object(type(validator),'iter_errors',side_effect=AssertionError('repeat schema validation')):
                self.assertEqual(c.payload_identity('k4_identity_payload',deepcopy(data)),original)
                detached=c.validate_payload('k4_identity_payload',data);detached['K4_base'][0][0]=3.
            self.assertEqual(data['K4_base'][0][0],0.)
            changed=deepcopy(data);changed['K4_base'][0][0]=1.
            self.assertNotEqual(c.payload_identity('k4_identity_payload',changed),original)
            changed['K4_base'][0][0]=True
            for _ in range(2):
                with self.assertRaises(c.V4SchemaError):c.payload_identity('k4_identity_payload',changed)
            with self.assertRaises(c.V4SchemaError):c.validate_payload('reference_hodge_identity_payload',data)
        self.assertIs(c._VALIDATED_PAYLOADS,cache);self.assertEqual(c._VALIDATION_MAX_BYTES,limit)

    def test_schema_keys_eviction_and_nested_scope(self):
        c=r.codec
        class Validator:
            def __init__(self):self.calls=0
            def iter_errors(self,data):self.calls+=1;return iter(())
        v=Validator()
        with r.validation_reuse():
            memo=c._VALIDATED_PAYLOADS
            for schema,name in ((b'a','a'),(b'b','a'),(b'b','b')):c._validation_result(v,{},(schema,),name)
            self.assertEqual(v.calls,3)
            with r.validation_reuse():self.assertIs(c._VALIDATED_PAYLOADS,memo)
            for i in range(12):c._validation_result(v,{'i':i},(b'a',),'a')
            self.assertEqual(len(memo),8)
            large={'text':'x'*(4*1024*1024)}
            for _ in range(2):c._validation_result(v,large,(b'a',),'a')
            self.assertEqual(v.calls,17);self.assertEqual(len(memo),8)


if __name__=='__main__':unittest.main()
