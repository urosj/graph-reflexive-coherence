"""Native A_OS steps 1–4: current-source-bound preflight, no endpoint grant."""

import hashlib
import json
import lzma
from pathlib import Path

from .canonical import digest, record_digest
from .errors import SourceAdmissionError
from .spark_native_aos_pressure import native_aos_pressure

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-AOS-Preflight.json.xz"
RECORD_DIGEST = "403f7454f8909bf01fbf867d2907e1273f0db37a8c012782614b58ddb0cb9e7e"


def load_json_object(path):
    try:
        value = json.loads(lzma.decompress(path.read_bytes()))
    except (OSError, lzma.LZMAError, ValueError) as error:
        raise SourceAdmissionError("Cannot read compressed A_OS preflight") from error
    if not isinstance(value, dict):
        raise SourceAdmissionError("A_OS preflight must be an object")
    return value


def checked_record(root):
    root = Path(root).resolve()
    value = load_json_object(root / RECORD)
    if (
        value.get("record_digest") != RECORD_DIGEST
        or record_digest(value, "record_digest") != RECORD_DIGEST
        or value.get("schema") != "grc9v4-native-aos-preflight-v1"
        or value.get("family") != "A_OS"
        or value.get("native_endpoint_verified") is not False
        or value.get("native_completion_support") is not False
        or value.get("full_trajectory_runs") != 0
        or value.get("user_accepted") is not False
    ):
        raise SourceAdmissionError("Unbound A_OS preflight or changed endpoint scope")
    for row in [*value["source_bindings"], value["evidence"]]:
        p = root / row["path"]
        try:
            raw = p.read_bytes()
        except ValueError as error:
            raise SourceAdmissionError(str(error)) from error
        if (
            not p.resolve().is_relative_to(root)
            or hashlib.sha256(raw).hexdigest() != row["sha256"]
        ):
            raise SourceAdmissionError("Changed current A_OS source: " + row["path"])
    return value


def native_aos(root):
    value = checked_record(root)
    keys = (
        "status",
        "native_endpoint_verified",
        "native_completion_support",
        "full_trajectory_runs",
        "endpoint_expectations_verified",
        "family",
        "target_vertices",
        "target_edges",
        "numerical_policy_id",
        "certificate_precision_bits",
        "sampling_cap_seconds",
        "elapsed_seconds",
        "estimate",
        "memory",
        "stop_conditions",
        "synthetic_window_scope",
        "reset_scope",
        "expected_endpoints",
    )
    body = {k: value[k] for k in keys}
    body.update(
        pressure=native_aos_pressure(root),
        schema="grc9v4_native_aos_preflight_surface_v1",
        record_digest=value["record_digest"],
        sample_counts={role: len(rows) for role, rows in value["samples"].items()},
        flint_version=value["machine"]["flint"],
        flint_threads=value["machine"]["flint_threads"],
        tests=value["tests"],
        domain_cache=value["caches"]["domain_final"],
        state_channels=value["state_channels"],
        evidence_storage=value["evidence_storage"],
        full_domain_dimension=value["full_domain_dimension"],
        precision_comparison_passed=value["precision_comparison"][
            "identical_represented_states"
        ],
        next_leaf="P9-9.1a.6-A_OS.5",
        source_url="/api/native-spark/a-os/preflight/source",
    )
    return dict(body, projection_digest=digest(body))


def native_aos_source(root):
    checked_record(root)
    return lzma.decompress((Path(root) / RECORD).read_bytes())
