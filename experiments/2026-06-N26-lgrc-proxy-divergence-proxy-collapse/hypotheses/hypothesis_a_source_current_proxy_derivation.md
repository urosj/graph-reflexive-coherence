# Hypothesis A - Source-Current Proxy Derivation

N26 can derive a proxy metric from source-current LGRC lower-stack inputs on
the scoped N25.2 MB6 substrate, with the proxy metric definition, target digest,
lower-stack inputs, and replay policy declared before use.

Support requires:

```text
N20 proxy_divergence_proxy_collapse contract consumed
N25.2 scoped MB6 substrate consumed only in scoped mode
proxy_metric_definition_digest present
proxy_derivation_policy_digest present
proxy_target_digest_declared_before_use present
lower_stack_input_trace present
proxy_metric_trace present
basin_persistence_capacity_trace present
support_coherence_floor_trace present
artifact digests match file contents
derived_report_only = false for positive rows
AP5 dependency status recorded row-locally
unsafe claim flags false
```

Failure conditions:

```text
proxy metric introduced only as a label
target digest declared after outcome inspection
proxy policy hidden in producer code
lower-stack input trace missing
proxy metric not replayable
N25.2 consumed as unscoped multi-basin substrate
semantic goal or target ownership used as evidence
native support, agency, sentience, or Phase 8 relabel
```

Expected ceiling:

```text
PD2 or PD3 source-current proxy derivation / replay candidate
```

This hypothesis alone does not support proxy divergence, proxy collapse, AP5
closeout, agency, or native support.
