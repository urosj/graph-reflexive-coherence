# Hypothesis B - Replay / Stress Same-Basin Transfer

N27 can show that a source-current transfer candidate remains the same basin
under replay, mapping variants, and bounded stress.

Expected support requires:

```text
artifact replay passed
snapshot/load replay passed
duplicate replay passed
mapping-inversion control fails closed when unsupported
same-basin signature preserved under declared mapping
support floor preserved
coherence floor preserved
boundary distinguishability preserved
flux balance preserved
original fixture support changed or removed as declared
support reconstruction ledger recorded
hidden support reconstruction absent
mapping-variant stress does not erase the transfer signature
```

Failure conditions:

```text
replay only works in original fixture
replay depends on hidden producer state
mapping variant changes basin identity
support reconstruction replaces transfer
post-transfer state is rebuilt instead of transferred
boundary mapping is label-only
one-window artifact does not survive replay
stress matrix demotes the transfer below declared floor
```

Hypothesis B supports only bounded same-basin transfer evidence if Hypothesis C
also passes.

