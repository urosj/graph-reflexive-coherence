# A_CI+PC coupled successor

CIP-0 and CIP-1 now have independent scientific PASS, recorded in the
separate [review/CIP-2 successor](../atc-cip-successor/README.md). Their reviewed
certificate bytes and historical pending flags remain unchanged. Scoped
adjudication/source admission is separate; CI/PC inventories are unchanged.

- [Program and mathematical argument](../../decisions/ATCCIPCoupledProgram.md)
- [User's coupled-program direction](CIP-CoupledProgram-Direction.md)
- [User's composite-domain direction](CIP-CompositeDomain-Direction.md)
- [CIP-0 retained certificate](ATCCIP0Certificate.json)
- [Exact rational bounds](../../research/atc_cip_domains.py)
- [Native staging / certificate checker](../../scripts/check_atc_cip_opening.py)
- [CIP-1 mathematical argument](../../decisions/ATCCIP1CausalChain.md)
- [CIP-1 input frozen before execution](CIP1-Preregistration.json)
- [CIP-1 retained causal certificate](ATCCIP1Certificate.json)
- [CIP-1 checker](../../scripts/check_atc_cip_chain.py)

The direction documents are retained proposals, not authority. In particular,
their reset-control shorthand is qualified in the program: one-time Z=0 does
not disable subsequent PC writes. The certificate's pending ROOT-00 claim and
debt links do not discharge any CIP-local or global debt. A later reviewed
adjudication must process all 28 realization-local dispositions.

From repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_cip_opening.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_cip_opening.py --check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_cip_chain.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_atc_cip_chain.py --check
```

Each default command re-executes its bounded check and prints a new record;
each `--check` checks retained record/source identities only. Use both retained
checks to validate the predecessor chain as well. Neither writes
files or substitutes a rerun for retained evidence. Source paths are relative
to the repository. Typed predecessor queries preserve claim class, support
disposition, source references, trace identities and edge counts/digests;
full traces can be reconstructed using their recorded queries.

The native five-node fixture checks ordinary-step semantics, not the
nonlinear CAN-LSF witness or public ATC lifecycle. Mathematical bounds cover
the declared paired nonlinear root domains, not every native profile.

CIP-1 executes the nonlinear coupled witness: one source onset, two target
beats for each actual role, and one further beat for each one-time control.
Indefinite return and the 71-proposal obstruction use uniform proofs, not long
simulations. Its negative carrier fixture is strictly inside the old PC ball
but outside CIP's, so rejection is required to come from the CIP bound, not
an outward-rounding artifact at the old PC endpoint. Full independent
reference/representation/lifecycle pressure is now completed by CIP-2;
see its [scientific PASS and local integrity disposition](../atc-cip-review/README.md).
Scoped claim/debt adjudication and source admission are now completed in the
separate [CIP admission](../atc-cip-admission/README.md), without rewriting
these historical certificates.
