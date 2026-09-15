// Generated from the checked P9-7.8 review; not runtime authority.
export const SPECIALIZATION_REVIEW = {
  "status": "accepted",
  "user_accepted": true,
  "tranche_7_closed": true,
  "G3_accepted": true,
  "admitted_specialization_support_sets": [
    [
      "grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75",
      "grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b",
      "grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946",
      "grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b",
      "grcv4-profile-sha256:413497bec4f219ec402d82d5cd2aced01dca25a58d2ab906c348472b98d596b0",
      "grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689",
      "grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f",
      "grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e",
      "grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d",
      "grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4"
    ]
  ],
  "new_runtime_iterations_authorized": [
    "P9-8.1a"
  ],
  "specialization_runtime_conformance": false,
  "proposed_consumed_support": [
    "grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75",
    "grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b",
    "grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946",
    "grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b",
    "grcv4-profile-sha256:413497bec4f219ec402d82d5cd2aced01dca25a58d2ab906c348472b98d596b0",
    "grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689",
    "grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f",
    "grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e",
    "grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d",
    "grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4"
  ],
  "decision": "User accepted P9-7.8 and closed Tranche 7. Exact consumed-set G3 admission with only P9-8.1a entry; no specialization runtime conformance or other leaf authorization.",
  "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.8-SpecializationReview.json",
  "record_digest": "64b84f298089551389937f0445ced594d3315af011e29723470ac55f4e0cade4",
  "review_path": "implementation/phase-9-grcv4/tranche-7/P9-7.8-SpecializationReview.md",
  "profile_count": 10,
  "disabled_cells": 40,
  "contract_count": 73,
  "pending_A_expansion_oracle": true,
  "a_expansion_work": {
    "parent": "P9-8.3A",
    "oracle_owner": "P9-8.3A.1",
    "runtime_owner": "P9-8.3A.2",
    "oracle_entry": [
      "accepted_exact_A_G2",
      "accepted_consumed_set_G3",
      "accepted_port_chart_fixed_row_initializer_and_D11_G9_contracts"
    ],
    "oracle_requires_production_runtime": false,
    "runtime_entry": [
      "accepted_P9-8.3A.1_same_exact_scope",
      "accepted_exact_A_G2",
      "accepted_consumed_set_G3",
      "implemented_and_verified_P9-8.1a",
      "implemented_and_verified_P9-8.1b",
      "implemented_and_verified_P9-8.1c",
      "implemented_and_verified_P9-8.2"
    ],
    "parent_closure": "both_children_accepted_for_same_exact_A_scope",
    "generic_authority_gap_route": "Hold affected child and return the exact missing graph-generic contract to a bounded Tranche 7 correction through established authority/paper/spec/runtime propagation; no specialization workaround or unrelated claim reopening.",
    "independent_C_work_blocked": false
  },
  "optional_capabilities_selected": [],
  "numerical_tests_rerun": 0,
  "runtime_paths": [
    "src/pygrc/models/grc_9_v4_topology.py",
    "tests/models/test_grc_9_v4_topology.py"
  ],
  "execution_scope": "P9-8.1a fixed chart and port graph only. No row differential/weight bridge, trigger, coarse/Split, expansion, disabled compatibility, optional completion, facade or legacy mutation. New work requires a hash-bound work-manifest entry; paths do not authorize unrelated contents.",
  "acceptance_path": "implementation/phase-9-grcv4/tranche-7/P9-7.8-G3Acceptance.json",
  "acceptance_digest": "5175491685e067a8653f561d497c88f587f90ba2c27926f64d598ce502a57c16"
};
