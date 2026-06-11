# N09 Hypotheses

N09 keeps regulation mechanisms separate so producer scaffolding does not
accidentally become intention or agency.

## Hypothesis A: Serialized Producer/Policy Goal-Proxy Regulation

Statement:

```text
Runtime-visible proxy state is measured, compared to a serialized target band,
and used by producer/policy or route-arbitration scaffolding to schedule or
select a corrective action. The response is validated by artifact replay.
```

Expected mechanism status tags:

```text
producer_mediated
threshold_authorized
native_route_arbitrated
memory_shaped
identity_anchored where N07 support evidence is consumed
native_policy_gap where the scaffolding identifies missing native support
```

What would support Hypothesis A:

```text
proxy measurement
-> error signal
-> proxy-conditioned route/producer evidence
-> scheduled or processed response
-> proxy state moves toward, stays within, or recovers toward target band
-> artifact-only replay reconstructs the chain
```

Hypothesis A may consume:

```text
N05 O5 oscillator/circuit background
N06 SC6 route-choice artifacts
N07 ID6 support/identity context
N08 Hypothesis A scoped serialized memory/trail evidence
```

It must not consume N08 Hypothesis B as native trail memory.

## Hypothesis B: Native Substrate-Mediated Goal-Proxy Regulation

Statement:

```text
The regulation loop is expressed by native substrate state or serialized
LGRC-native policies rather than experiment-local producer/control logic.
```

Expected blocker until tested:

```text
native_goal_proxy_regulation_policy_missing
```

Hypothesis B is staged in the initial N09 tranche, not rejected. The N05-N08
results do not yet identify a complete native LGRC goal-proxy regulation policy
surface, but they do provide possible substrate-mediated ingredients. N09
therefore separates:

```text
B0 inventory:
    native/substrate-mediated ingredients already available from N05-N08

B1 probe:
    geometry/substrate-mediated regulation attempt after the A-path identifies
    load-bearing proxy variables and response laws

B2 native absorption decision:
    record the missing LGRC policy surface if pure native regulation cannot be
    expressed without changing core LGRC
```

What would eventually distinguish Hypothesis B from Hypothesis A:

```text
proxy/error state is represented by existing or added LGRC-native surfaces
response law is serialized as native policy
no experiment-local if/else controls correction
producers, if present, only expose evidence already native to the substrate
artifact replay validates the native policy without private runtime state
```

## Current Status

```text
Hypothesis A:
    open
    initial path = Iterations 1-9
    strongest intended ceiling = artifact_only_goal_proxy_regulation_candidate

Hypothesis B:
    staged
    B0 inventory = open
    B1 probe = planned after load-bearing A-path variables are known
    expected blocker = native_goal_proxy_regulation_policy_missing
```

## Required Comparator

Because the roadmap sequence is:

```text
memory-shaped choice -> goal-proxy regulation
```

N09 must include a memory-shaped regulation lane and a no-memory comparator
before claiming that N08 memory was actually used.

```text
memory_shaped_lane:
    proxy-conditioned regulation with N08 memory surface evidence

no_memory_control_lane:
    same proxy / same target / same policy without N08 memory surface evidence
```

## Identity/Support Boundary

Identity/support preservation is an N10 handoff condition, not an N09 agency
claim. N09 should record:

```text
identity_not_tested_under_regulation
identity_preserved_under_regulation
identity_disrupted_under_regulation
support_preserved_under_regulation
support_disrupted_under_regulation
```

These tags decide whether N10 can consume a regulation lane for
identity-continuous integration.

## Claim Boundary

Neither hypothesis implies intention, agency, desire, reward optimization,
goal ownership, identity acceptance, ACO, locomotion, biological behavior, or
personhood.
