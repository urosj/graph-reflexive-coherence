"""Bound native C_OS trajectory evidence; aggregate support remains separate."""

import importlib.util
from pathlib import Path

from .basin import _bound_file
from .canonical import digest, load_json_object, record_digest
from .errors import SourceAdmissionError

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.5-Campaign.json"
RECORD_DIGEST = "4972df8504845ba2a21e07a3fbe4326f2b4e1e70a55b5063076f534b3b592cfb"
# Execution uses RFC 8785; this surface separately pins its canonical JSON body.
CONTENT_DIGEST = "4972df8504845ba2a21e07a3fbe4326f2b4e1e70a55b5063076f534b3b592cfb"


def restore_evidence(root):
    """Restore the two byte-authenticated summary records on a fresh checkout."""
    spec = importlib.util.spec_from_file_location(
        "native_campaign_storage", root / "scripts/evidence_storage.py"
    )
    storage = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(storage)
    storage.restore(root, prefix="implementation/phase-9-grcv4/tranche-9/P9-9.1a.5-")


def checked_record(root):
    root = Path(root)
    restore_evidence(root)
    value = load_json_object(root / RECORD)
    if (
        record_digest(value, "record_digest") != CONTENT_DIGEST
        or value.get("record_digest") != RECORD_DIGEST
        or value.get("schema") != "grc9v4-native-cos-campaign-v1"
        or value.get("native_endpoint_verified") is not True
        or value.get("native_completion_support") is not False
        or value.get("user_accepted") is not False
        or value.get("full_trajectory_runs") != 2
        or value.get("physical_supporting_tail_steps") != 0
    ):
        raise SourceAdmissionError(
            "Unbound native campaign or changed acceptance scope"
        )
    for row in [*value["source_bindings"], *value["streams"]]:
        _bound_file(root, row["path"], row["sha256"])
    return value


def native_campaign(root):
    value = checked_record(root)
    body = {
        "schema": "grc9v4_native_spark_campaign_surface_v1",
        "record_digest": value["record_digest"],
        "status": value["status"],
        "family": "C_OS",
        "native_endpoint_verified": True,
        "native_completion_support": False,
        "user_accepted": False,
        "full_trajectory_runs": 2,
        "physical_supporting_tail_steps": 0,
        "target_vertices": value["target_vertices"],
        "target_edges": value["target_edges"],
        "exact_charge": value["exact_charge"],
        "duration": value["duration"],
        "roles": value["roles"],
        "elapsed_seconds": value["elapsed_seconds"],
        "cap_seconds": value["cap_seconds"],
        "peak_rss_mib": value["peak_rss_mib"],
        "exact_backend": value["exact_backend"],
        "oracle_precision_bits": value["oracle_precision_bits"],
        "pressure": value["pressure"],
        "accounting_scope": value["accounting_scope"],
        "global_cross_process_uniqueness": False,
        "next_leaf": value["next_leaf"],
        "source_url": "/api/native-spark/c-os/campaign/source",
    }
    return dict(body, projection_digest=digest(body))


def native_campaign_source(root):
    checked_record(root)
    return (Path(root) / RECORD).read_bytes()
