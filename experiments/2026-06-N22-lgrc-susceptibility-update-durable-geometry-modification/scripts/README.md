# N22 Scripts

Reconstruction scripts for N22 belong here.

Scripts should use repository-relative paths, deterministic output ordering,
and explicit checks for:

```text
N20 I5 susceptibility_update contract consumption
N21 closeout consumed as context only
row-specific threshold declaration
source_current_inputs recorded
source-current pre/post/delta/re-entry traces
allowed delta fields versus same-basin invariant fields
peer/same-budget comparison for route- or region-conditioned rows
durability delta digests and persistence ratio
artifact, snapshot/load, and duplicate replay where applicable
route-label-only fail-closed controls
reinforcement-schedule-hidden-support controls
one-window-transient controls
AP4/AP5 gap dependency preservation
N21 ND6 bridge status at closeout only
unsafe claim flags false
```
