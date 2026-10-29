"""Portable retained JSON, including recursively immutable native mappings."""
import json

import p984b_runtime as b

SELF = b.HERE + 'p9_ccipc_capture.py'


def portable(value):
    result = json.loads(b.canonical_json_bytes(value))
    b.require(b.digest(result) == b.digest(value), 'capture normalization changed identity')
    return result
