# D2 Predictive Role Separation Target Definitions

Status: schema complete; final scoring deferred.

## Scope

This D2 pass defines feature families, target classes, controls, scoring
contracts, blocked-observation rules, and output schemas. It does not
run predictive scoring.

## Feature Families

| Family | Role | Evidence | Source Artifacts |
| --- | --- | --- | --- |
| degree_adjacency_baseline | H0 baseline | direct | topology, PortEdge records, edge labels |
| row | geometric/differential predictor | derived | Experiment A rows, port_to_rc, state/cached row artifacts |
| column | interface/refinement/multiscale predictor | derived | Experiments B, D, E; endpoint ports and expansion payloads |
| port | edge-local and row-column intersection predictor | direct | PortEdge records, Experiments D, F, G |
| random_grouping | negative semantic grouping control | derived | shared transform harness and D1 non-factorized controls |

## Target Classes

| Target Class | Expected Strongest Family | Current Sources | Status |
| --- | --- | --- | --- |
| geometric_differential | row | Experiment A rows | schema_defined_scoring_deferred |
| interface_routing_refinement | column | Experiments B, C, D | schema_defined_scoring_deferred |
| edge_local | port | Experiments F, G | schema_defined_scoring_deferred |
| generic_activity | degree_adjacency_baseline | A-G summaries and topology rows | schema_defined_scoring_deferred |
| identity_level_persistence | port_plus_column_plus_global_basin_context | Experiment D persistence rows; later D8 windows | partial_until_D8 |

## Controls

- `random_row_triples`: test true row grouping against arbitrary triples
- `random_column_triples`: test true column grouping against arbitrary triples
- `arbitrary_s9_port_relabeling`: test anonymous-port null against structured features
- `degree_only_features`: test whether ordinary graph structure explains all targets
- `shuffled_target_labels`: detect spurious predictive signal
- `cross_validation_by_fixture`: avoid memorizing one fixture or transform family

## Scoring Contract

- primary split: `cross_validation_by_fixture`
- scoring status: `blocked_until_enough_completed_run_data_exist`
- final scoring belongs to discriminator checklist Iteration 10.

## Blocked Rules

- `missing_feature_family`: mark family blocked for that target
- `missing_target_artifact`: mark target blocked
- `insufficient_fixture_count`: mark scoring inconclusive
- `source_intent_only`: do not promote to supported evidence

## Guardrail

D2 scoring is blocked in this iteration by design. This pass only
defines the schema so later D3-D8 outputs can conform to one target
and feature-family contract.
