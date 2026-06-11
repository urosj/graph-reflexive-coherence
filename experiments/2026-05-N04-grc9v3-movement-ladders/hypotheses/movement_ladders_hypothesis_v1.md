# N04 Movement Ladders Hypothesis v1

This document records the initial hypotheses for
`2026-05-N04-grc9v3-movement-ladders`.

## Handoff Assumption

N04 starts from the N03/E3 result:

```text
native LGRC9V3 packetized causal execution can produce a D2.3-equivalent
self-rearming packet pulse under controls.
```

Available input loop level:

```text
loop_ladder_level = L5
```

In this N04 context, L5 means that N03/E3 provides a native LGRC9V3
self-rearming packetized pulse substrate. It does not mean that boundary
coupling, displacement, or movement has been shown.

This is a pulse-substrate result, not a movement result. N04 must independently
test whether pulse activity couples to boundary, front/rear geometry, identity
continuity, and displacement.

Explicit claim inheritance flag:

```text
movement_claim_inherited_from_n03 = false
```

## Null Hypothesis

For U0 and B0 fixed-substrate lanes:

```text
Uniform or symmetric basin states should not produce directed movement above
the null displacement envelope.
```

Expected:

- no directed centroid displacement beyond numerical/null envelope;
- no coordinated front/rear boundary change;
- no shape-preserving movement claim;
- no loop-driven movement claim.

## Movement-Response Hypothesis

For B1 and K1 fixed-substrate lanes:

```text
A locally asymmetric basin initialization or one-time conserved kick may
produce a transient movement response, but not loop-driven or locomotion-like
movement.
```

Expected if positive:

- measurable centroid displacement above null envelope;
- budget conserved;
- identity continuity preserved at the configured level;
- shape gates determine whether the claim reaches M3;
- reversed lanes reverse direction or are reported as substrate-biased.

Claim ceiling:

```text
movement response / identity-basin movement
```

## Loop-Driven Movement Hypothesis

For later E3 pulse lanes:

```text
The native LGRC9V3 E3 self-rearming packet pulse may drive repeated movement
only if pulse activity measurably couples to movement-relevant geometry and
front/rear boundary metrics.
```

Equivalently:

```text
E3 is eligible as an internal pulse drive candidate, but movement remains
unopened until boundary-coupled displacement is independently measured.
```

Required before any loop-driven movement claim:

- packet-loop geometry coupling audit passes;
- E3 pulse-active / boundary-coupling-disabled control does not claim movement;
- boundary coupling is state-mediated, not directly scripted;
- node-plus-packet budget is conserved;
- identity, shape, and topology gates pass;
- controls remain negative for the correct gate reasons.

Claim ceiling if positive:

```text
loop-driven movement / conserved pulse-driven displacement
```

## Blocked Claims

N04 does not start with permission to claim:

- biological locomotion;
- agency;
- intention;
- decision-making;
- movement through absolute Euclidean space;
- adaptive-topology movement;
- graph topology change as movement itself.

These remain blocked unless the movement-ladder gates explicitly open them.
