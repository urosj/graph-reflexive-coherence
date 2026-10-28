"""Execute an explicitly pinned native selection through the public GRC9V4 API."""

import argparse
import json
from pathlib import Path

from examples.grcv4.catalog import Catalog, ROOT, json_read


def configuration_from_selection(saved, *, exact_backend, numerical_policy, root=ROOT):
    """Decode a verified public declaration for any of the ten native families.

    This does not construct a runtime owner, solve a root, or grant execution.
    """
    catalog = Catalog(saved["catalog"], root=root)
    catalog.verify_selection(saved)
    if saved["recorded_evidence"]["model"] != "GRC9V4":
        raise ValueError("this runner requires a native GRC9V4 selection")
    from pygrc.models.grc_9_v4 import GRC9V4Configuration, GRC9V4ExecutionOptions
    from pygrc.models.grc_9_v4_lifecycle import GRC9V4Specialization
    from pygrc.models.grc_v4_geometry import GRCV4ReferenceGeometry
    from pygrc.models.grc_v4_state import GRCV4AuthoritativeState, FrozenJSONMap

    selected = saved["configuration"]
    if "inputs" in selected:
        science = selected["inputs"]
        reference = science["reference"]
    else:
        entry = catalog.entry(saved["recorded_evidence"]["id"])
        if entry["format"] != "native-oracle":
            raise ValueError("selection has no complete native configuration adapter")
        oracle = catalog.artifact(entry["data"], parse=True)[saved["side"]]
        science = oracle["scientific_payload"]
        reference = selected["reference"]
    spec = selected["specialization"]
    specialization = GRC9V4Specialization(
        FrozenJSONMap(spec["resolved"]), FrozenJSONMap(spec["identity_payload"])
    )
    if (
        "specialization_id" in spec
        and specialization.specialization_id != spec["specialization_id"]
    ):
        raise ValueError("oracle specialization identity mismatch")
    return GRC9V4Configuration(
        reference=GRCV4ReferenceGeometry.from_payload(reference),
        specialization=specialization,
        current=GRCV4AuthoritativeState(**selected["roles"]["current"]),
        reset=GRCV4AuthoritativeState(**selected["roles"]["reset"]),
        budget_target=science["Q_target"],
        step_index=science["step_index"],
        time=science["time"],
        execution=GRC9V4ExecutionOptions(exact_backend, numerical_policy),
    )


def construct(saved, *, exact_backend, numerical_policy, root=ROOT):
    configuration = configuration_from_selection(
        saved, exact_backend=exact_backend, numerical_policy=numerical_policy, root=root
    )
    from pygrc.models import GRC9V4

    model = GRC9V4.from_config(configuration)
    # A new construction has no historical receipts. Its scientific authority
    # and clock must nevertheless match the selected, pinned example exactly.
    state = model.state.lifecycle
    selected = saved["configuration"]
    if (
        state.active_model_identity != selected["model_identity"]
        or state.scientific_state_digest != selected["scientific_digest"]
        or state.reset.reset_digest != selected["reset_digest"]
    ):
        raise ValueError("selection reconstruction identity mismatch")
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("selection")
    parser.add_argument(
        "--requests",
        required=True,
        help="JSON array of explicit V4 step inputs; [] constructs/observes only",
    )
    parser.add_argument("--exact-backend", required=True, choices=("flint", "python"))
    parser.add_argument("--numerical-policy", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError("output already exists")
    saved = json_read(Path(args.selection).read_bytes())
    requests = json_read(Path(args.requests).read_bytes())
    if type(requests) is not list:
        raise ValueError("ordered request array required")
    from pygrc.models.grc_v4 import GRCV4StepRequestInput

    requests = [GRCV4StepRequestInput.from_payload(r) for r in requests]
    model = construct(
        saved, exact_backend=args.exact_backend, numerical_policy=args.numerical_policy
    )
    results = []
    for request in requests:
        result = model.step_v4_input(request)
        results.append(result.to_payload())
        if not result.committed:
            break
    value = dict(
        schema="grc9v4-public-selection-run-v1",
        selection_digest=saved["selection_digest"],
        support=model.support_status(),
        results=results,
        snapshot=model.snapshot(),
    )
    raw = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()
    if len(raw) > 1_000_000:
        import lzma

        if output.suffix != ".xz":
            output = output.with_suffix(output.suffix + ".xz")
        raw = lzma.compress(raw)
    with output.open("xb") as stream:
        stream.write(raw)
    print(
        json.dumps(
            dict(
                output=str(output),
                committed_steps=sum(r["committed"] for r in results),
                support=value["support"]["disposition"],
            )
        )
    )


if __name__ == "__main__":
    main()
