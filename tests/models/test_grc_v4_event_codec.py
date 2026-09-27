"""Content reuse and per-lookup asset integrity for the additive event codec."""

import tempfile
import unittest
from copy import deepcopy
from importlib import resources
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import patch

from pygrc.models import grc_v4_codec as base
from pygrc.models import grc_v4_event_codec as codec

ASSETS = Path(__file__).resolve().parents[2] / "src/pygrc/models/grc_v4_assets"
PAYLOAD: dict[str, Any] = {
    "schema_version": "grcv4-coordinate-map-v1",
    "policy_id": codec.POLICY_ID,
    "source_graph_digest": "grc-graph-sha256:" + "a" * 64,
    "target_graph_digest": "grc-graph-sha256:" + "b" * 64,
    "vertex_map": [],
    "edge_map": [],
}
NAME = "representation/correspondence_payload"


class EventCodecCacheTests(unittest.TestCase):
    def test_warm_schemas_registry_and_validator_are_reused(self) -> None:
        codec.validate_event_payload(NAME, PAYLOAD)
        js = base._dependency("jsonschema")
        referencing = base._dependency("referencing")
        with (
            patch.object(base, "decode_json", side_effect=AssertionError("schema reparsed")),
            patch.object(codec, "deepcopy", side_effect=AssertionError("schema copied")),
            patch.object(js.validators, "extend", side_effect=AssertionError("validator rebuilt")),
            patch.object(referencing.Resource, "from_contents", side_effect=AssertionError("registry rebuilt")),
        ):
            self.assertEqual(codec.validate_event_payload(NAME, PAYLOAD), PAYLOAD)
        changed = deepcopy(PAYLOAD)
        changed["vertex_map"] = False
        with self.assertRaises(base.V4SchemaError):
            codec.validate_event_payload(NAME, changed)

    def test_public_schemas_and_outputs_are_detached(self) -> None:
        expected = codec.load_event_schemas()
        changed = codec.load_event_schemas()
        for schema in changed:
            schema["$defs"].clear()
        self.assertEqual(codec.load_event_schemas(), expected)
        result = codec.validate_event_payload(NAME, PAYLOAD)
        result["vertex_map"].append("changed")
        self.assertEqual(codec.validate_event_payload(NAME, PAYLOAD), PAYLOAD)

    def test_warm_event_validation_rejects_changed_and_missing_assets(self) -> None:
        originals = {p.name: p.read_bytes() for p in ASSETS.iterdir() if p.is_file()}
        names = (
            "asset-index.json", "grc-v4-contract-schema.json",
            "grc-v4-specification-release.json", "grc-v4-specification-release.sha256",
            "grc-v4-a-initializer-release.json", "grc-v4-a-initializer-schema.json",
            "grc-v4-event-contract-release.json", "grc-v4-topology-event-schema.json",
            "grc-v4-representation-transport-schema.json",
        )
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            for name, raw in originals.items():
                (package / name).write_bytes(raw)
            with patch.object(resources, "files", return_value=package):
                for name in names:
                    for missing in (False, True):
                        with self.subTest(name=name, missing=missing):
                            codec.validate_event_payload(NAME, PAYLOAD)
                            path = package / name
                            try:
                                if missing:
                                    path.unlink()
                                else:
                                    raw = originals[name]
                                    path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
                                with self.assertRaises(base.V4AssetError):
                                    codec.validate_event_payload(NAME, PAYLOAD)
                            finally:
                                path.write_bytes(originals[name])
                            self.assertEqual(codec.validate_event_payload(NAME, PAYLOAD), PAYLOAD)

    def test_cached_event_validation_still_requires_optional_dependencies(self) -> None:
        codec.validate_event_payload(NAME, PAYLOAD)
        real_dependency = base._dependency
        for dependency in ("rfc8785", "jsonschema", "referencing"):
            def missing(name: str, selected: str = dependency) -> ModuleType:
                if name == selected:
                    raise base.V4DependencyError(name)
                return real_dependency(name)
            with (
                patch.object(base, "_dependency", side_effect=missing),
                self.assertRaises(base.V4DependencyError),
            ):
                codec.validate_event_payload(NAME, PAYLOAD)
