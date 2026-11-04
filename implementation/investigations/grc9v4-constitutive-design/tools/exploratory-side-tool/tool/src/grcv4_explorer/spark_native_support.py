"""Current bounded support, separate from immutable family execution reports."""

import sys
from pathlib import Path
from .canonical import digest

RECORD_DIGEST = "16cac027d0534bd9c2b429cd639bee4f1690d268d8437d0ee73bf8ae270dac8e"


def native_spark_support(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root / "implementation/phase-9-grcv4/verification"))
    from p991a7_support import checked

    value = checked(root)
    if value["record_digest"] != RECORD_DIGEST:
        raise ValueError("changed native completion reconciliation")
    body = {
        k: value[k]
        for k in (
            "schema",
            "leaf",
            "status",
            "family_campaigns_accepted",
            "reconciliation_user_accepted",
            "native_completion_support",
            "completion_support_scope",
            "hierarchy_tracking",
            "general_ATC",
            "full_GRC9V4_conformance",
            "G4_accepted",
            "new_numerical_trajectories",
            "historical_execution_flags_preserved",
            "native_obligation_count",
            "next_tasks",
            "record_digest",
            "families",
            "evidence",
        )
    }
    body["source_url"] = "/api/native-spark/support/source"
    return dict(body, projection_digest=digest(body))


def native_spark_support_source(root):
    native_spark_support(root)
    from p991a7_support import RECORD

    return (Path(root) / RECORD).read_bytes()
