"""Native A_CI_PC steps 1–4: current-source-bound preflight, no endpoint grant."""

import hashlib
import json
import lzma
from pathlib import Path

from .canonical import digest, record_digest
from .errors import SourceAdmissionError
from .spark_native_acipc_pressure import native_acipc_pressure

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-ACIPC-Preflight.json.xz"
RECORD_DIGEST = "ff3d254bde200cf6e5b3635fa1007f2d6e581e787f29af840daadd870499f03d"


def load_json_object(path):
    try:
        value = json.loads(lzma.decompress(path.read_bytes()))
    except (OSError, lzma.LZMAError, ValueError) as error:
        raise SourceAdmissionError(
            "Cannot read compressed A_CI_PC preflight"
        ) from error
    if not isinstance(value, dict):
        raise SourceAdmissionError("A_CI_PC preflight must be an object")
    return value


def checked_record(root):
    root = Path(root).resolve()
    value = load_json_object(root / RECORD)
    if (
        value.get("record_digest") != RECORD_DIGEST
        or record_digest(value, "record_digest") != RECORD_DIGEST
        or value.get("schema") != "grc9v4-native-acipc-preflight-v1"
        or value.get("family") != "A_CI_PC"
        or value.get("native_endpoint_verified") is not False
        or value.get("native_completion_support") is not False
        or value.get("full_trajectory_runs") != 0
        or value.get("user_accepted") is not False
    ):
        raise SourceAdmissionError(
            "Unbound A_CI_PC preflight or changed endpoint scope"
        )
    for row in [*value["source_bindings"], value["evidence"]]:
        p = root / row["path"]
        try:
            from .basin import _bound_file
            raw = _bound_file(root, row["path"], row["sha256"]).read_bytes()
        except ValueError as error:
            raise SourceAdmissionError(str(error)) from error
        if (
            not p.resolve().is_relative_to(root)
            or hashlib.sha256(raw).hexdigest() != row["sha256"]
        ):
            raise SourceAdmissionError("Changed current A_CI_PC source: " + row["path"])
    return value


def native_acipc(root):
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
        schema="grc9v4_native_acipc_preflight_surface_v1",
        record_digest=value["record_digest"],
        sample_counts={role: len(rows) for role, rows in value["samples"].items()},
        flint_version=value["machine"]["flint"],
        flint_threads=value["machine"]["flint_threads"],
        tests=value["tests"],
        domain_cache=value["caches"]["domain_final"],
        root_domain_cache=value["caches"]["root_domain_final"],
        state_channels=value["state_channels"],
        evidence_storage=value["evidence_storage"],
        full_domain_dimension=value["full_domain_dimension"],
        precision_comparison_passed=value["precision_comparison"][
            "identical_represented_states"
        ],
        next_leaf="P9-9.1a.6-A_CI_PC.5",
        source_url="/api/native-spark/a-ci-pc/preflight/source",
        pressure=native_acipc_pressure(root),
    )
    return dict(body, projection_digest=digest(body))


def native_acipc_source(root):
    checked_record(root)
    return lzma.decompress((Path(root) / RECORD).read_bytes())
