"""One positive native step, with explicit family, duration and execution policy."""
from pygrc.models import GRC9V4
from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_state import FrozenJSONMap
from examples.grc9v4.fixtures import configuration


def main():
    model = GRC9V4.from_config(configuration("C_OS"))
    result = model.step_v4_input(GRCV4StepRequestInput(
        "grcv4-step-request-input-v1", "first-step", 2**-12, FrozenJSONMap({})))
    if not result.committed:
        raise RuntimeError(result.failure)
    print("family:", model.configuration.family.profile_family_id)
    print("C after:", model.configuration.current.C)
    print("consumed current:", result.observables["authoritative_current"])
    print("fresh read:", model.compute_observables()["authoritative_current"])
    print("receipts:", len(model.receipt_ledger))


if __name__ == "__main__":
    main()
