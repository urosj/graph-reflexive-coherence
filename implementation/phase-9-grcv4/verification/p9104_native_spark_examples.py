"""Bind the native completion tutorial to accepted evidence, without rerunning it."""

from hashlib import sha256
import json
from pathlib import Path

from examples.grc9v4 import native_spark as example

ROOT = example.ROOT
BASE = "implementation/phase-9-grcv4/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/"
PATH = BASE + "tranche-10/P9-10.4-NativeSpark-Examples.json"
GUIDE = "examples/grc9v4/native_spark.md"
CODE = "examples/grc9v4/native_spark.py"
SELF = BASE + "verification/p9104_native_spark_examples.py"
SOURCES = (GUIDE, CODE, SELF, example.SUPPORT,
           BASE + "tranche-10/P9-10.3-NativeSpark-Regressions.json",
           BASE + "tranche-10/P9-10.3-NativeSpark-Acceptance.json",
           BASE + "verification/test_p9104_native_spark_examples.py")


def ref(root, name):
    return dict(path=name, sha256=sha256((root / name).read_bytes()).hexdigest())


def seal(value):
    return dict(value, record_digest=example.digest({k: v for k, v in value.items() if k != "record_digest"}))


def overview(root=ROOT):
    rows = []
    for family in example.FAMILIES:
        v = example.inspect(family, root)
        rows.append({k: v[k] for k in ("family", "state_channels", "duration", "endpoints", "sources", "recorded_campaign_seconds")})
    return rows


def checked(root=ROOT):
    root = Path(root).resolve()
    value = json.loads((root / PATH).read_bytes())
    example.require(value == seal(value) and value["schema"] == "p9104-native-spark-examples-v1", "tutorial publication digest/schema changed")
    example.require(value["sources"] == [ref(root, p) for p in SOURCES], "tutorial source changed")
    example.require(value["families"] == overview(root), "tutorial family/evidence coverage changed")
    example.require(value["new_full_trajectory_runs"] == 0 and value["user_accepted"] is False and value["G4_accepted"] is False and value["full_GRC9V4_conformance"] is False, "tutorial scope changed")
    return value


if __name__ == "__main__":
    value = checked()
    print("P9104_NATIVE_SPARK_EXAMPLES_PASS families=10 retained_inspection=true new_full_trajectory_runs=0")
