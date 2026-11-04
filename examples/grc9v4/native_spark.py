"""Public native spark workflow. Inspection never runs a physical trajectory.

Run from the repository root: PYTHONPATH=src:. .venv/bin/python -m
examples.grc9v4.native_spark inspect. See native_spark.md before using run/replay.
"""

import argparse
from hashlib import sha256
import json
import lzma
from pathlib import Path
import sys
import time

from pygrc.models.grc_9_v4 import GRC9V4
from pygrc.models.grc_9_v4_completion_certificate import CompletionCertificate
from pygrc.models.grc_9_v4_completion_codec import digest
from pygrc.models.grc_9_v4_expansion import GRC9V4ExpansionRequestInput
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.7-Support.json"
SUPPORT_DIGEST = "16cac027d0534bd9c2b429cd639bee4f1690d268d8437d0ee73bf8ae270dac8e"
FAMILIES = ("C_OS", "C_CI", "C_PC", "C_CI_PC", "A_OS", "A_CI", "A_PC", "A_CI_PC", "C_RG2b", "A_RG2b")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def checked_bytes(ref, root=ROOT):
    path = Path(ref["path"])
    require(not path.is_absolute() and ".." not in path.parts, "repository-relative input required")
    raw = (root / path).read_bytes()
    require(sha256(raw).hexdigest() == ref["sha256"], "retained input changed: " + str(path))
    return raw


def support(root=ROOT):
    value = json.loads((root / SUPPORT).read_bytes())
    require(value["record_digest"] == SUPPORT_DIGEST == digest({k: v for k, v in value.items() if k != "record_digest"}), "accepted support identity changed")
    require(value["reconciliation_user_accepted"] is True, "support not accepted")
    return value


def bundle(family="C_OS", root=ROOT):
    """Reuse exact inputs and expectations; do not import campaign/test helpers."""
    require(family in FAMILIES, "unknown family")
    value = support(root)
    subject = next(r for r in value["families"] if r["family"] == family)
    refs = next(r for r in value["evidence"] if r["family"] == family)
    raw = checked_bytes(refs["campaign"], root)
    campaign = json.loads(lzma.decompress(raw) if refs["campaign"]["path"].endswith(".xz") else raw)
    lines = lzma.decompress(checked_bytes(refs["input"], root)).splitlines()
    require(len(lines) == 1, "one immutable campaign input required")
    inputs = json.loads(lines[0])
    require([digest(c) for c in inputs["certificates"]] == subject["certificate_ids"], "target certificates differ")
    return subject, refs, campaign, inputs


def inspect(family="C_OS", root=ROOT):
    subject, refs, campaign, inputs = bundle(family, root)
    source = inputs["source_configuration"]
    target = inputs["target_configuration"]
    checkpoints = next(r for r in campaign["streams"] if r["path"].endswith("-checkpoints.jsonl.xz"))
    saved = [json.loads(line) for line in lzma.decompress(checked_bytes(checkpoints, root)).splitlines()]
    final = next(r for r in saved if r["role"] == "current" and r["beat"] == subject["roles"]["current"]["completion"])
    evidence = final["checkpoint"]["owner"]["publication"]["completion"]["evidence"]
    require(evidence["decision"] == "completed" and evidence["local_gain"] == 1, "missing recorded completion")
    request = inputs["event"]["receipt"]["identity_payload"]["action"]["request"]
    return dict(
        mode="retained_inspection_no_numerical_execution", family=family,
        accepted_support_digest=SUPPORT_DIGEST, sources={**{k: refs[k] for k in ("input", "campaign", "accepted_review")}, "checkpoints": checkpoints},
        numerical_policy=subject["numerical_policy"], duration=subject["duration"],
        state_channels=refs["state_channels"], subjects=subject["subjects"],
        source_vertices=len(source["reference"]["graph"]["live_node_ids"]),
        target_vertices=len(target["reference"]["graph"]["live_node_ids"]),
        roles_distinct=source["current"] != source["reset"],
        expansion=dict(source_node=request["source_node_id"], chirality=request["module_chirality"], shares=request["resource_distribution"], history_policy=request["history_policy"], event_id=inputs["event"]["event_id"]),
        certificates=[dict(certificate_id=digest(c), binding=c["operands"]["binding"], proof={k: c["proof"][k] for k in ("q", "image_margin", "full_step_error")}) for c in inputs["certificates"]],
        endpoints=subject["roles"],
        milestones=[dict(role=r["role"], label=r["label"], target_beat=r["beat"], checkpoint_digest=digest(r["checkpoint"])) for r in saved if r["beat"] >= subject["roles"][r["role"]]["entry"]],
        completion=dict(decision=evidence["decision"], local_gain=evidence["local_gain"], parent=evidence["parent"], new_child_anchors=evidence["new_child_anchors"], observations=[{k: o[k] for k in ("step_index", "time", "duration")} for o in evidence["observations"]]),
        recorded_campaign_seconds=campaign["elapsed_seconds"],
        limits="Pinned retained inspection; no new numerical proof, universal entry, hierarchy, full conformance or G4. Reset endpoint means a comparison window, not a second completed occurrence.",
    )


def committed(result, operation):
    require(result.committed, operation + " rejected: " + str(result.reason))
    return result


def prepare(family="C_OS"):
    """An actual ordinary source beat, explicit expansion and proof admission."""
    subject, _, _, inputs = bundle(family)
    model = GRC9V4.from_config(inputs["source_configuration"])
    action = inputs["event"]["source_receipt"]["identity_payload"]["action"]
    source_step = GRCV4StepRequestInput(
        "grcv4-step-request-input-v1", action["operation_id"],
        float(action["duration"]), FrozenJSONMap({}),
    )
    source_result = committed(model.step_v4_input(source_step), "ordinary source beat")
    request = GRC9V4ExpansionRequestInput.from_payload(
        inputs["event"]["receipt"]["identity_payload"]["action"]["request"]
    )
    require(model.configuration.scientific_digest == request.source_state_digest, "fresh source differs from the bound event input")
    event_result = committed(model.expand(request), "expansion")
    require(source_result.local_gain == event_result.local_gain == 0, "source/event incorrectly earned completion")
    require(model.configuration.to_payload() == inputs["target_configuration"], "target transfer/readmission differs from accepted input")
    certificates = tuple(CompletionCertificate.from_payload(c) for c in inputs["certificates"])
    installed = committed(model.install_completion_certificates(*certificates), "certificate pair")
    require(installed.local_gain == 0, "proof installation earned gain")
    return model, certificates, subject


def observation(model, target_beat, result=None):
    completion = model.compute_observables()["completion"]
    return dict(target_beat=target_beat, step_index=model.configuration.step_index,
                time=model.configuration.time, local_gain=0 if result is None else result.local_gain,
                membership=completion["membership"], window_observations=completion["window_observations"],
                decision=completion["evidence"]["decision"], reason=completion["evidence"].get("reason"),
                children=len(completion["children"]), consumed_occurrences=len(completion["consumed_occurrences"]))


def continue_to_completion(model, *, max_steps, emit=lambda value: None):
    """Stop on the actual public decision, never on a recorded endpoint number."""
    require(type(max_steps) is int and max_steps > 0, "positive execution bound required")
    trace = []
    for beat in range(1, max_steps + 1):
        result = committed(model.step(), "target beat " + str(beat))
        row = observation(model, beat, result)
        trace.append(row)
        if beat % 50 == 0 or row["window_observations"] or result.local_gain:
            emit(row)
        if row["decision"] == "completed":
            require(result.local_gain == 1, "completion did not emit the expected local increment")
            return trace
    raise RuntimeError("execution bound reached without a completed-spark decision; no completion claimed")


def write_compressed(path, value):
    # Store output once. All files use XZ even when small; never overwrite.
    with path.open("xb") as stream:
        stream.write(lzma.compress(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()))


def run(family, output, max_steps):
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    model, _, subject = prepare(family)
    initial = observation(model, 0)
    def emit(row):
        print(json.dumps(row), file=sys.stderr, flush=True)
    trace = continue_to_completion(model, max_steps=max_steps, emit=emit)
    completion = model.compute_observables()["completion"]
    # Resolve referenced proof/lineage objects through the public interface.
    evidence = completion["evidence"]
    proof = model.completion_evidence_object(evidence["proof"]["certificate"])
    require(digest(proof) == subject["certificate_ids"][0], "completion cited a different certificate")
    checkpoint = model.snapshot()
    duplicate = model.duplicate()
    require(duplicate.snapshot() == checkpoint, "warm duplicate differs")
    reset_result = committed(duplicate.reset(), "reset of duplicate")
    require(duplicate.configuration.current == model.configuration.reset and reset_result.local_gain == 0, "reset did not restore the full baseline")
    require(duplicate.compute_observables()["completion"]["evidence"]["decision"] == "not_applicable", "reset kept a live completion window")
    require(model.snapshot() == checkpoint, "duplicate reset mutated the original")
    write_compressed(output / "checkpoint.json.xz", checkpoint)
    report = dict(schema="grc9v4-native-spark-example-run-v1", family=family,
                  mode="new_public_execution", user_accepted=False,
                  full_GRC9V4_conformance=False, G4_accepted=False,
                  expected_endpoint=subject["roles"]["current"], initial=initial,
                  steps=trace, completion=completion, duplicate_reset_checked=True,
                  elapsed_seconds=time.monotonic()-started,
                  cold_replay_executed=False)
    write_compressed(output / "run.json.xz", report)
    return dict(family=family, target_steps=len(trace), local_gain=trace[-1]["local_gain"],
                checkpoint="checkpoint.json.xz", cold_replay_executed=False)


def replay(path):
    """In a fresh process this executes the saved journal and re-admits proofs."""
    raw = path.read_bytes()
    checkpoint = json.loads(lzma.decompress(raw) if path.suffix == ".xz" else raw)
    model = GRC9V4.from_state(checkpoint)
    require(model.snapshot() == checkpoint, "exact replay differs")
    return dict(mode="public_checkpoint_replay", exact_checkpoint_equal=True,
                completion=model.compute_observables()["completion"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inspect", "prepare", "run", "replay"))
    parser.add_argument("--family", choices=FAMILIES, default="C_OS")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-steps", type=int, default=400)
    parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args()
    if args.action == "inspect":
        result = inspect(args.family)
    elif args.action == "prepare":
        model, _, _ = prepare(args.family)
        result = dict(family=args.family, mode="actual_source_event_certificate_admission", **observation(model, 0))
    elif args.action == "run":
        if args.output is None:
            parser.error("run requires a new --output directory")
        result = run(args.family, args.output, args.max_steps)
    else:
        if args.checkpoint is None:
            parser.error("replay requires --checkpoint; cold replay executes its journal")
        result = replay(args.checkpoint)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
