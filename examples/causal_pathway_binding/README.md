# Causal-Pathway Binding Examples

These five scripts demonstrate the stable evidence-bearing binder workflow:

1. [admitted_pathway.py](admitted_pathway.py) binds and executes one admitted
   packet-transport pathway;
2. [registered_composition.py](registered_composition.py) exercises registered
   composition `CMP-02` inside one evidence scope;
3. [dynamic_choice.py](dynamic_choice.py) declares two allowed pathways while
   leaving the actual branch to consumer code;
4. [unregistered_candidate.py](unregistered_candidate.py) records a distinct
   executable relation as `experimental_unregistered`; and
5. [direct_unbound.py](direct_unbound.py) contrasts valid direct execution with
   an evidence-bearing bound invocation.

Run them from the repository root with the repository environment:

```bash
PYTHONPATH=src:. .venv/bin/python examples/causal_pathway_binding/admitted_pathway.py
PYTHONPATH=src:. .venv/bin/python examples/causal_pathway_binding/registered_composition.py
PYTHONPATH=src:. .venv/bin/python examples/causal_pathway_binding/dynamic_choice.py --choice snapshot
PYTHONPATH=src:. .venv/bin/python examples/causal_pathway_binding/unregistered_candidate.py
PYTHONPATH=src:. .venv/bin/python examples/causal_pathway_binding/direct_unbound.py
```

Each script prints a small JSON summary. Add `--output-dir
outputs/examples/causal_pathway_binding` to write its canonical lock and receipt.
Generated artifacts are run-specific evidence, so they are not tracked here.

## Trust Inputs

The shared helper reads the example anchor record from the repository but pins
its expected digest separately in source. This separation is intentional: a
submitted anchor cannot authenticate its own digest. Production consumers
should obtain the anchor record and expected digest from independently trusted
configuration.

The candidate example also includes:

- [candidate_mechanism.py](candidate_mechanism.py), the distinct executable
  module-function entrypoint; and
- [candidate_mechanism_evidence.json](candidate_mechanism_evidence.json), the
  version-2 content-addressed mechanism artifact.

The candidate remains experimental. Neither its executable evidence nor a
successful receipt adds a registry entry, admits a composition, or promotes a
native claim.

## Provenance Boundary

`claim_scope = bound_invocations_only` is literal. A receipt certifies only
the represented calls made through its verified handles. It does not certify
whole-run causal closure, prove the absence of unbound influences, or qualify
direct execution. The direct-unbound example makes that distinction explicit.

Read the [user and agent guide](../../docs/reference/GRC-LGRC-CausalPathwayBinding-User-Agent-Guide.md)
for the full `select -> bind -> lock -> execute -> seal -> validate` workflow,
and use the [stable reference](../../docs/reference/GRC-LGRC-CausalPathwayBinding-ReferenceGuide.md)
for exact API and artifact-field details.
