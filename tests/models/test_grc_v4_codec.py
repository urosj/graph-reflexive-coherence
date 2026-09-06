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
from typing import Any
import unittest
from unittest.mock import patch
import venv

from pygrc.models import grc_v4_codec as codec
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "src/pygrc/models/grc_v4_assets"
VECTORS = ROOT / "specs/grc-v4-conformance-vectors.json"


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
        from tests.models.test_grc_v4_profile import fixture, reidentify

        params, identity = fixture()
        params["candidate"]["kappa_Phi_C"] = 1e20
        params["solver"]["iteration_limit"] = 10.0
        reidentify(params, identity)
        profile_bytes = resolve_profile(params, identity).to_canonical_bytes()
        wheelhouse = Path(os.environ["GRCV4_WHEELHOUSE"]).resolve()
        self.assertTrue(wheelhouse.is_dir())
        with tempfile.TemporaryDirectory(prefix="grcv4-p922-package-") as scratch:
            temp = Path(scratch)
            source = temp / "source"
            source.mkdir()
            shutil.copytree(ROOT / "src", source / "src",
                            ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
            for name in ["pyproject.toml", "README.md", "LICENSE"]:
                shutil.copyfile(ROOT / name, source / name)

            def run(command: list[str], cwd: Path) -> None:
                env = {k: v for k, v in os.environ.items()
                       if k not in {"PYTHONPATH", "PYTHONHOME"}}
                result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                        text=True, timeout=240)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            dist = temp / "dist"
            run([sys.executable, "-m", "build", "--no-isolation",
                 "--outdir", str(dist)], source)
            wheel = next(dist.glob("*.whl"))
            sdist = next(dist.glob("*.tar.gz"))
            for archive in [wheel, sdist]:
                with self.subTest(distribution=archive.suffix):
                    environment = temp / ("wheel-env" if archive == wheel else "sdist-env")
                    venv.EnvBuilder(with_pip=True).create(environment)
                    python = environment / "bin/python"
                    outside = temp / ("wheel-consumer" if archive == wheel else "sdist-consumer")
                    outside.mkdir()
                    run([str(python), "-m", "pip", "install", "--no-index",
                         "--find-links", str(wheelhouse), str(archive)], outside)
                    run([str(python), "-I", "-c", """
import sys
from pygrc.models import GRCV2, GRCV3, GRC9, GRC9V3
from pygrc.models.grc_v4_codec import canonical_json_bytes, V4DependencyError
from pygrc.models import grc_v4, grc_v4_step
assert 'rfc8785' not in sys.modules
assert 'jsonschema' not in sys.modules
try:
    canonical_json_bytes({'x': 1})
except V4DependencyError:
    pass
else:
    raise AssertionError('missing extra did not fail')
"""], outside)
                    run([str(python), "-m", "pip", "install", "--no-index",
                         "--find-links", str(wheelhouse), str(archive) + "[v4]"], outside)
                    run([str(python), "-I", "-c", """
from pathlib import Path
import operator
import sys
from pygrc.models import grc_v4_codec as c
from pygrc.models.grc_v4_profile import GRCV4Profile, list_supported_profiles
from pygrc.models.grc_v4 import decode_step_request_input
from pygrc.models.grc_v4_step import admit_step_request, FailureReceipt
assert not (Path.cwd() / 'specs').exists()
assert not (Path.cwd() / 'implementation').exists()
assert not (Path.cwd() / 'tests').exists()
assert 'site-packages' in c.__file__
assert c.canonical_json_bytes({'x': True}) == b'{"x":true}'
assert c.load_contract_schema()['schema_version'] == 'grcv4-implementation-contract-schema-v2'
assert list_supported_profiles() == frozenset()
raw = bytes.fromhex(sys.argv[1])
profile = GRCV4Profile.from_canonical_bytes(raw)
assert profile.to_canonical_bytes() == raw
assert operator.index(profile.params_resolved.solver.iteration_limit) == 10
assert c.canonical_json_bytes(c.decode_canonical_json(raw)) == raw
request = decode_step_request_input(b'{"schema_version":"grcv4-step-request-input-v1","operation_id":"installed","dt":-1,"context_value":{},"boundary_input":null,"external_source":null}')
failure = admit_step_request(request, source_state_digest='grcv4-state-sha256:' + '0' * 64)
assert isinstance(failure, FailureReceipt)
assert failure.identity_payload.code == 'invalid_duration'
""", profile_bytes.hex()], outside)
                    run([str(python), "-m", "pip", "check"], outside)


if __name__ == "__main__":
    unittest.main()
