"""Read-only entry to the public native completion tutorial and existing evidence."""

import sys
import json
from pathlib import Path
from .canonical import digest

ACCEPTANCE_PATH = "implementation/phase-9-grcv4/tranche-10/P9-10.4-NativeSpark-Acceptance.json"
ACCEPTANCE_DIGEST = '63faee50ad908a96b8b4ee2ecb2369a4d1ce06f7b4cc811dde2fe3e292edce30'


def accepted_decision(value, publication):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    if (
        value.get("record_digest") != digest(body)
        or value["record_digest"] != ACCEPTANCE_DIGEST
        or value["publication_record_digest"] != publication["record_digest"]
        or value["families"] != [r["family"] for r in publication["families"]]
    ):
        raise ValueError("changed native workflow acceptance")
    return value


def checker(root):
    root = Path(root).resolve()
    sys.path[:0] = [str(root), str(root / "implementation/phase-9-grcv4/verification")]
    import p9104_native_spark_examples as c
    if c.ROOT != root:
        raise ValueError("native tutorial checkout mismatch")
    return c


def native_spark_workflow(root):
    c = checker(root)
    value = c.checked(root)
    acceptance = accepted_decision(json.loads((Path(root) / ACCEPTANCE_PATH).read_bytes()), value)
    body = dict(schema="native-spark-workflow-view-v1", publication=value,
                status=acceptance["status"], user_accepted=acceptance["user_accepted"],
                acceptance=dict(path=ACCEPTANCE_PATH, **acceptance),
                guide_url="/api/native-spark/workflow/source?name=guide",
                code_url="/api/native-spark/workflow/source?name=code",
                inspect_command="PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.native_spark inspect",
                prepare_command="PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.native_spark prepare",
                run_command="PYTHONPATH=src:. .venv/bin/python -m examples.grc9v4.native_spark run --family C_OS --max-steps 400 --output outputs/examples/native-spark-cos",
                limits="Inspection executes no trajectory. Prepare executes source/event/proof admission. Run and cold replay are explicit numerical operations; no web request starts them.")
    return dict(body, projection_digest=digest(body))


def native_spark_workflow_source(root, name):
    c = checker(root)
    native_spark_workflow(root)
    path = {"guide": c.GUIDE, "code": c.CODE, "publication": c.PATH, "acceptance": ACCEPTANCE_PATH}[name]
    return (Path(root) / path).read_bytes()
