"""Pinned native C_CI endpoint evidence with lossless compressed primary records."""

import hashlib
import json
import lzma
from pathlib import Path

from .canonical import digest, record_digest
from .errors import SourceAdmissionError
from .spark_native_cci import checked_record as preflight_record
from .spark_native_cci_pressure import checked_record as pressure_record

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CCI.5-Campaign.json.xz"
COST = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CCI.5-Cost.json"
RECORD_DIGEST = "d030ba7f5673fd6eae6c78881c683bac153f1377632b8218f7f626e600949483"
CONTENT_DIGEST = "d030ba7f5673fd6eae6c78881c683bac153f1377632b8218f7f626e600949483"


def load_record(path):
    with lzma.open(path, "rt") as stream:
        return json.load(stream)


def checked_record(root):
    import sys
    sys.path.insert(0, str(Path(root)/"implementation/phase-9-grcv4/verification"))
    from p991a6_cpc_epoch import previous_bytes
    root = Path(root).resolve()
    value = load_record(root / RECORD)
    if (
        value.get("record_digest") != RECORD_DIGEST
        or record_digest(value, "record_digest") != CONTENT_DIGEST
        or value.get("schema") != "grc9v4-native-cci-campaign-v1"
        or value.get("family") != "C_CI"
        or value.get("native_endpoint_verified") is not True
        or value.get("native_completion_support") is not False
        or value.get("full_trajectory_runs") != 2
        or value.get("physical_supporting_tail_steps") != 0
        or value.get("roles", {}).get("current", {}).get("local_gain") != 1
        or value.get("roles", {}).get("reset", {}).get("local_gain") != 0
    ):
        raise SourceAdmissionError("Unbound C_CI campaign or changed endpoint scope")
    for row in [*value["source_bindings"], *value["streams"]]:
        p = root / row["path"]
        try:
            raw = previous_bytes(root, row["path"])
        except ValueError as error:
            raise SourceAdmissionError(str(error)) from error
        if (
            not p.resolve().is_relative_to(root)
            or hashlib.sha256(raw).hexdigest() != row["sha256"]
        ):
            raise SourceAdmissionError(
                "Changed C_CI campaign source/evidence: " + row["path"]
            )
    cost = json.loads((root / COST).read_bytes())
    if (
        cost["record_digest"] != value["final_cost_record_digest"]
        or preflight_record(root)["record_digest"] != cost["preflight_record_digest"]
        or pressure_record(root)["record_digest"] != cost["pressure_record_digest"]
    ):
        raise SourceAdmissionError("Changed C_CI prerequisite chain")
    return value


def native_cci_campaign(root):
    value = checked_record(root)
    keys = (
        "status",
        "family",
        "native_endpoint_verified",
        "native_completion_support",
        "user_accepted",
        "full_trajectory_runs",
        "physical_supporting_tail_steps",
        "target_vertices",
        "target_edges",
        "exact_charge",
        "duration",
        "roles",
        "elapsed_seconds",
        "cap_seconds",
        "peak_rss_mib",
        "exact_backend",
        "native_precision_bits",
        "oracle_precision_bits",
        "pressure",
        "accounting_scope",
        "global_cross_process_uniqueness",
        "next_leaf",
    )
    body = {k: value[k] for k in keys}
    body.update(
        schema="grc9v4_native_cci_campaign_surface_v1",
        record_digest=value["record_digest"],
        compressed_evidence_bytes=sum(x["compressed_bytes"] for x in value["streams"]),
        source_url="/api/native-spark/c-ci/campaign/source",
    )
    return dict(body, projection_digest=digest(body))


def native_cci_campaign_source(root):
    checked_record(root)
    return lzma.decompress((Path(root) / RECORD).read_bytes())
