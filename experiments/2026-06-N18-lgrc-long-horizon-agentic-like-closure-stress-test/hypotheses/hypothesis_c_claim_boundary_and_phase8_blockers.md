# Hypothesis C - Claim Boundary And Phase 8 Blockers

## Claim

N18 can classify any long-horizon AP8-style result while preserving the claim
boundary and keeping Phase 8/native implementation claims blocked unless a
separate native implementation task explicitly opens them.

## Required Evidence

```text
unsafe claim flags remain false
native support flags remain false
phase8_opened remains false
identity acceptance remains blocked
semantic agency relabels fail closed
goal ownership relabels fail closed
long-horizon drift outside source-backed envelope fails closed
resource/shared-medium merge relabels fail closed
final claim ceiling is explicit
```

## Boundary

This hypothesis is supported only if stronger unsafe claims remain blocked.
It does not mean agency, identity acceptance, native support, or Phase 8
implementation is supported.
