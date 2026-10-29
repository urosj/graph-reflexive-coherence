import json
import unittest

import p9_ccipc_capture as capture


class CaptureTests(unittest.TestCase):
    def test_nested_immutable_bounds_roundtrip(self):
        original = dict(bounds=capture.b.FrozenJSONMap(dict(nested=dict(limit='1/256'))),
                        vectors=(0.0, -0.125, 1e-15), flag=False)
        result = capture.portable(original)
        self.assertEqual(capture.b.digest(original), capture.b.digest(json.loads(json.dumps(result))))
        self.assertEqual(result['bounds']['nested'], dict(limit='1/256'))


if __name__ == '__main__':
    unittest.main()
