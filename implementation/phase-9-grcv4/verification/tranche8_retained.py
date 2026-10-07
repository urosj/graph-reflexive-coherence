"""Run an unchanged boundary checker with operation-local prerequisite reuse."""

import importlib
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys

from tranche8_validation import BOUNDARY_MODULES, ROOT, validation_session


def main():
    import tranche8_evidence as index
    import phase9_implementation_policy as policy
    if len(sys.argv) < 3:
        raise ValueError("select a boundary checker and retained mode")
    script = Path(sys.argv[1])
    name = script.stem
    expected = ROOT / index.HERE / (name + ".py")
    index.require(name in BOUNDARY_MODULES and script.resolve() == expected,
        "unknown retained checker")
    options = sys.argv[2:]
    expected_mode = "--check" if name == "p984c_cos" else "--check-retained"
    index.require(options in ([expected_mode], [expected_mode, "--recheck-numerics"])
        and (name != "p984c_cos" or len(options) == 1), "retained-only arguments required")
    policy.restore_packed_evidence(ROOT)
    module = importlib.import_module(name)
    output = StringIO()
    with validation_session((name,)):
        sources = index.Sources(ROOT)
        # Authenticate selected inputs/results before dispatch, not a self-signed
        # status payload. The unchanged checker validates its transitive bindings.
        for path in (module.INPUTS, module.RESULTS, module.REVIEW):
            sources.raw(path)
        original = sys.argv
        try:
            sys.argv = [str(expected), *options]
            with redirect_stdout(output):
                module.main()
        finally:
            sys.argv = original
    print(output.getvalue(), end="")


if __name__ == "__main__":
    main()
