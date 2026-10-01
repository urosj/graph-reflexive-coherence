# GRCV4 exact CPU backend

V4 keeps Python `Fraction` arithmetic as its default. The optional FLINT CPU
backend uses native exact `fmpq` scalars and `fmpq_mat` multiplication/inversion.
Solver policies, exact conditioning certificates, domain checks, public
schemas, receipts, and snapshot bytes are unchanged.

Install both V4 extras when selecting FLINT:

```bash
python -m pip install -e '.[v4,v4-flint]'
```

Select the backend **before constructing the declaration and owner**. The
scope covers both; the owner retains the choice after the scope exits:

```python
from examples.grcv4.grid_realizations_c import make_inputs
from pygrc.models.grc_v4 import GRCV4, GRCV4StepRequestInput
from pygrc.models.grc_v4_numerics import ExactBackend, exact_backend
from pygrc.models.grc_v4_state import FrozenJSONMap

with exact_backend(ExactBackend.FLINT):
    initial, differential_reference, _ = make_inputs("PC", 3, 4)
    model = GRCV4(initial, differential_reference=differential_reference)

request = GRCV4StepRequestInput(
    "grcv4-step-request-input-v1", "flint-example-0", initial.dt, FrozenJSONMap({})
)
result = model.step_v4_input(request)  # still uses FLINT
```

Omitting the scope preserves existing callers and uses `Fraction`. Selection is
an implementation choice, not part of the scientific declaration or public
wire format. A missing FLINT installation fails when entering the explicit
scope. Invalid choices fail before declaration construction.

The owner re-enters its backend for steps, observations, state assignment,
reset/rebase, and crossings. Duplication preserves the choice; restoration from
a serialized state selects the active backend of that restoration call. Private
matrix continuation facts carry a backend tag and cannot be seeded into another
backend's operation store. The selector and exact constructors are centralized
in `grc_v4_exact.py`; native FLINT matrix kernels remain behind the shared
`grc_v4_numerics.py` API. Numerical values are raw `Fraction` or raw `fmpq`
within one operation. Exact input conversion happens at construction, and
binary64/JSON conversion remains at existing public boundaries. `ExactScalar`
is the annotation for this backend-dependent value; `exact_number(...)` is its
constructor. A source-level test rejects direct `Fraction` imports or uses in
other V4 modules, so a new Python-only arithmetic path fails under the default
test suite rather than first failing when FLINT is selected. A nominal wrapper
would add a third runtime scalar representation and the prototype measured a
substantial cost for that approach.

## Decision: exact scalar API

**Status: accepted (2026-09-30).** Keep `Fraction` and `fmpq` as the two native
runtime representations, selected before owner construction. Use `ExactScalar`
only to annotate backend-dependent values, and `exact_number(...)` to construct
them. The V4 source guard in `test_grc_v4_exact_backend.py` rejects direct
`Fraction` imports and references outside `grc_v4_exact.py`, including when
only the default backend is installed. Owner binding and backend-tagged
continuation facts provide the runtime boundary.

`ExactScalar` is currently an `Any` type alias. It describes the role of a
value but does **not** provide static or nominal type safety; the source guard
addresses the specific risk of accidentally adding a Python-only `Fraction`
path. It does not prove that every value passed between helpers belongs to the
selected backend. The FLINT tests and public byte-parity checks remain
necessary.

An import-time alias to `Fraction` or `fmpq` would select one type per process,
while this API permits separate owners to retain different backends. It would
also leave their constructor inputs and numeric behavior unequal. We therefore
do not present a factory returning either type as a concrete `ExactScalar`
class. Do not add a wrapper solely to make the API look nominal: the
prototype showed a material arithmetic cost. Revisit this decision if further
development reveals a concrete semantic failure that owner binding, the source
guard, and parity tests do not adequately prevent, such as a mixed-backend
value crossing a numerical boundary. If strong nominal typing is then needed,
compare an explicit value wrapper with a backend-parameterized numerical API
against that failure. Either design needs renewed strict parity and measured
performance before adoption.

The [CPU backend evidence](../evidence/grcv4-performance/exact_cpu_backend_evaluation.md)
records the exploratory ten-realization parity and timings. Integrated
validation compared strict public digests for all ten realizations at one
step, and for C_PC and C_OS across five steps. A paired integrated C_PC 3×4
five-step run took 48.08 s on the default backend and 11.49 s on FLINT
(4.18×); these are single local samples. Focused tests cover optional
selection, native exact values, singular and conditioning failures,
continuation isolation, owner binding, and legacy public byte parity.
