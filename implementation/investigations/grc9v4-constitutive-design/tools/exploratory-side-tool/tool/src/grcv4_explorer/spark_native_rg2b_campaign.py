"""Pinned independent RG2b campaigns; retained checks never rerun a trajectory."""

import json
import sys
from pathlib import Path

from .canonical import digest, file_sha256
from .errors import SourceAdmissionError

PINS = {
    "C_RG2b": "f84ac243ea09a53986b23c487513c49014c390917e653cafe8ce780b20c23a49",
    "A_RG2b": "94823f115876c5593318c5a881d8356c4e998630668d9c1938c14d740b341ab3",
}  # Completed campaign bytes, not incoming status.
FAMILIES = {"c-rg2b": "C_RG2b", "a-rg2b": "A_RG2b"}


def checked_record(root, family):
    root = Path(root).resolve()
    if family not in PINS:
        raise SourceAdmissionError("RG2b campaign not yet retained: " + family)
    sys.path.insert(0, str(root / "implementation/phase-9-grcv4/verification"))
    from p991a6_rg2b_campaign import Adapter, check

    adapter = Adapter(family)
    path = adapter.path("Campaign.json")
    if file_sha256(root / path) != PINS[family]:
        raise SourceAdmissionError("Changed pinned RG2b campaign")
    try:
        return check(adapter, root)
    except (ValueError, AssertionError, KeyError) as error:
        raise SourceAdmissionError(str(error)) from error


def native_rg2b_campaign(root, family):
    v = checked_record(root, family)
    slug = next(k for k, f in FAMILIES.items() if f == family)
    # String timing values avoid cross-language floating serialization drift.
    body = {
        k: v[k]
        for k in (
            "family",
            "status",
            "native_endpoint_verified",
            "native_completion_support",
            "user_accepted",
            "roles",
            "full_trajectory_runs",
            "physical_supporting_tail_steps",
            "target_vertices",
            "target_edges",
            "exact_charge",
            "duration",
            "native_precision_bits",
            "oracle_precision_bits",
            "check_scope",
            "next_leaf",
        )
    }
    body["roles"] = {
        r: {k: x for k, x in row.items() if k != "mean_audited_seconds"}
        for r, row in body["roles"].items()
    }
    body.update(
        schema="grc9v4_native_rg2b_campaign_surface_v1",
        elapsed_minutes=f"{v['elapsed_seconds'] / 60:.2f}",
        peak_rss_mib=f"{v['peak_rss_mib']:.1f}",
        compressed_bytes=sum(r["compressed_bytes"] for r in v["streams"]),
        pressure_controls=len(v["pressure"]),
        cold_replayed_steps={
            r: x["replayed_steps"] for r, x in v["cold_replay"].items()
        },
        evidence_format=v["evidence_format"],
        record_digest=v["record_digest"],
        source_url=f"/api/native-spark/{slug}/campaign/source",
    )
    return dict(body, projection_digest=digest(body))


def native_rg2b_campaign_source(root, family):
    return json.dumps(checked_record(root, family)).encode()
