"""Run an unchanged boundary checker with operation-local prerequisite reuse."""

import importlib
from contextlib import redirect_stdout, nullcontext
from io import StringIO
from pathlib import Path
import sys

from tranche8_validation import BOUNDARY_MODULES, ROOT, validation_session


# Successor research checkers have explicit retained-only entry points. Never
# infer permission from a filename prefix or admit prepare/run/derive actions.
EXTRA_MODES = {
    'p984g_cos': ('check',),
    'p984g_cos_bounds': ('check',),
    'p984e_cos': ('check',),
    'p984f_cos': ('check',),
    'p984f_cci': ('check',),
    'p984f_apc': ('check',),
    'p984f_aci': ('check',),
    'p984e_cci': ('check',),
    'p984e_aci': ('check',),
    'p984e_apc': ('check',),
    'p984d_apc_feasibility': ('--check',),
    'p984d_apc_companion': ('--check',),
    'p984d_apc_companion_runtime': ('--check',),
    'p984d_apc_history': ('--check', '--check-pressure'),
    'p984d_apc_joint': ('check', 'check-derivation'),
    'p984d_apc_joint_successor': ('check',),
    'p984d_apc_full': ('check',),
}


def main():
    import tranche8_evidence as index
    import phase9_implementation_policy as policy
    if len(sys.argv) < 3:
        raise ValueError("select a boundary checker and retained mode")
    script = Path(sys.argv[1])
    name = script.stem
    expected = ROOT / index.HERE / (name + ".py")
    index.require(name in (*BOUNDARY_MODULES, *EXTRA_MODES) and script.resolve() == expected,
        "unknown retained checker")
    options = sys.argv[2:]
    dense_cos = name in ("p984c_cos", "p984d_cos")
    expected_mode = "--check" if dense_cos else "--check-retained"
    modes = EXTRA_MODES.get(name, (expected_mode,))
    index.require(any(options in ([mode], [mode, "--recheck-numerics"]) for mode in modes)
        and (not dense_cos or len(options) == 1), "retained-only arguments required")
    policy.restore_packed_evidence(ROOT)
    module = importlib.import_module(name)
    output = StringIO()
    with validation_session((name,)):
        sources = index.Sources(ROOT)
        # Authenticate selected inputs/results before dispatch, not a self-signed
        # status payload. The unchanged checker validates its transitive bindings.
        fields = ['INPUTS', 'RESULTS', 'REVIEW']
        if name == 'p984d_apc_feasibility': fields.remove('INPUTS')
        if name == 'p984d_apc_history': fields.append('PRESSURE')
        if name == 'p984d_apc_joint': fields.append('DERIVATION')
        for field in fields:
            sources.raw(getattr(module, field))
        original = sys.argv
        try:
            sys.argv = [str(expected), *options]
            with redirect_stdout(output), (module.b.exact_backend(module.b.ExactBackend.FLINT)
                    if name in ("p984c_crg2b_runtime", "p984c_arg2b_runtime") else nullcontext()):
                module.main()
        finally:
            sys.argv = original
    print(output.getvalue(), end="")


if __name__ == "__main__":
    main()
