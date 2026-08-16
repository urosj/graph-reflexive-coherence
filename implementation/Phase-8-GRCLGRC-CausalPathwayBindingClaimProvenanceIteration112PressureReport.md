# Phase 8 GRC/LGRC Causal Pathway Binding And Claim Provenance Iteration 112

**Status:** Passed

**Source behavior changed:** No

## Acceptance Question

Can one structural model bind an admitted native-mechanics pathway, a
producer-mediated registered composition, and an unregistered candidate while
preserving exact mechanism-specific execution and conservative claims without
becoming a generic dispatcher?

The answer is yes for an explicit verified-callable linker. The binder records
declared identity and invocation provenance around the current callable. It
does not translate an intent into a pathway and does not normalize arguments or
results across mechanisms.

## Case A: Admitted Pathway Only

Authority:

```text
pathway = lgrc9v3.explicit_packet_transport
composition = none
mechanism ownership = native_with_configured_semantics
activation = explicit_call
```

The consumer binds the exact pathway and required stages, freezes those
declarations, obtains verified links to the current packet schedule/debit/
arrival symbols, and calls those symbols using their existing signatures. The
receipt records only stages actually invoked through those links.

The model does not create a composition merely because scheduling, debit, and
credit form one pathway. Its claim ceiling remains native packet accounting and
queue-processing mechanics; route endpoints, amount, and times remain supplied.

Result: passed.

## Case B: Producer-Mediated CMP-20

Authority:

```text
composition = CMP-20
from = lgrc9v3.feedback_eligibility_producer.feedback_packet_schedule
to = lgrc9v3.explicit_packet_transport.packet_schedule/source_debit/target_credit
status = producer_mediated
adapter ID = feedback_eligibility_producer
adapter owner = installed_producer
```

The registered composition binding imports its endpoint and stage requirements
from the exact matrix row. Callable links expose the existing feedback-surface,
producer, packet-schedule, and runtime-commit entrypoints. The use edge exists
only because `CMP-20` was explicitly declared; endpoint co-use cannot create it.

The lock and receipt retain producer-owned eligibility, direction, threshold,
and scheduling. The native packet mutation remains native. The combined claim
is exactly the matrix ceiling: producer-mediated feedback eligibility followed
by native packet mechanics. `lawful_native` and native feedback admission stay
blocked.

Result: passed.

## Case C: Unregistered Candidate

Fixture identity:

```text
candidate ID = experiment.i112.source_local_packet_admission
kind = composition
promotion status = none
claim ceiling = experimental_unregistered
```

Calling `bind_pathway` or `bind_composition` with this identity must reject it
because it is absent from the canonical registry and matrix. A separate
candidate declaration may name admitted constituent pathways, its proposed
source/target relation, owner, all six authority coordinates, configured/
producer/adapter residue, evidence owner, unresolved authority, and blocked
native/admitted claims.

The candidate may then use separately bound admitted callables, but the
candidate relation remains a visually distinct node or edge and forces the
enclosing claim envelope to `experimental_unregistered`. It cannot manufacture
a canonical ID or inherit the constituents' native status.

Result: passed.

## Dynamic Choice Pressure

The session declares an allowed pathway set before lock and separately records
selection authority. Runtime consumer code—not the binder—chooses one declared
handle. The receipt records the alternative actually invoked and reports the
others as declared but unused. An undeclared alternative fails closed.

Native route arbitration can be one bound pathway when its exact contract is
intended. That does not make candidate formation native and does not give the
binder selection authority.

Result: passed.

## Rejected Alternatives

- A generic `execute(pathway_id, **kwargs)` surface was rejected because it
  normalizes unlike mechanisms and becomes a dispatcher.
- Intent routing was rejected because the binder must not choose semantics.
- Implicit call tracing or monkey-patching was rejected because direct Python
  calls could masquerade as declared evidence and stage identity would be
  inferred after execution.
- Adding Python symbols to the canonical registry was rejected because it
  collapses knowledge-plane pathway authority into environment-specific
  linkage.
- Automatic composition from two used endpoints was rejected because endpoint
  evidence is not crossing evidence.
- Candidate insertion into the registry/matrix was rejected because
  declaration is not promotion.

## Accepted Model

```text
explicit identity declaration
-> separate binding-symbol resolution
-> pre-execution lock
-> verified real-callable delegation
-> actual-use graph and receipt
-> authority-derived structured claim envelope
```

The wrapper may implement Python callable delegation, but it has no generic
causal-work operation. Its arguments and result remain those of the linked
mechanism-specific source symbol.

## I113 Handoff

Iteration 113 may add the binding-symbol map, immutable authority loader,
binding session, admitted pathway/composition declarations, candidate schema,
allowed alternative sets, and verified callable links. It must keep broad
enforcement, locks, receipts, and claim closeout in their planned later stages.

No runtime behavior, generic admission, ownership model, L04 mechanism, N32
candidate, or consolidation authority changed in I112.
