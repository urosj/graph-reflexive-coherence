// Generated from ProfileG2Registry.json; checked by the registry validator.
export const G2_REGISTRY = {
  "record_digest": "56f47a0c704a5ced85345e0422d61a0928b12bf0a0022519b7df1af1a8876474",
  "records": [
    {
      "acceptance": {
        "path": "implementation/phase-9-grcv4/tranche-4/P9-4.8B-G2Acceptance.json",
        "record_digest": "e7165dc2f4cfe159d397c7aa61ccfbc89a30909db888e6638ef1ffe5905ec6dd"
      },
      "adapter": "historical_c_os",
      "bounded_view_key": null,
      "complete_profile_id": "grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d",
      "gate": "P9-G2[C_OS]",
      "profile_family_id": "C_OS",
      "review": {
        "path": "implementation/phase-9-grcv4/tranche-4/P9-4.8B-GateReview.json",
        "record_digest": "cd41ab0453b3e82b8e50530b4c8ddca2b8c307ace704e5a3eaa0e8d2726afa68"
      },
      "review_metrics": null,
      "state": "accepted",
      "view_key": "g2_acceptance"
    },
    {
      "acceptance": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_OS-G2Acceptance.json",
        "record_digest": "bb84b02362a6b5ac1e1a4b5ba921f63ff3f454c27c82fb99d3da1836d088a2bb"
      },
      "adapter": "historical_a_os",
      "bounded_view_key": "a_os_crossings",
      "complete_profile_id": "grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4",
      "gate": "P9-G2[A_OS]",
      "profile_family_id": "A_OS",
      "review": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_OS-G2Review.json",
        "record_digest": "f5d40d78fc8f3d96bbf6e78b5087527b5712aa4179d3f43b94456da05c7d4dc4"
      },
      "review_metrics": {
        "catalog_cells": 28,
        "numerical_tests_rerun": 0,
        "supplemental_interface_methods": 1
      },
      "state": "accepted",
      "view_key": "a_os_g2_review"
    },
    {
      "acceptance": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_CI-G2Acceptance.json",
        "record_digest": "aa3dc998282ac66bd7ff5d6865fb9175242f44d52ea2c9b5b7b5a6e91657e5cb"
      },
      "adapter": "exact_profile_v1",
      "bounded_view_key": "a_ci_crossings",
      "complete_profile_id": "grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946",
      "gate": "P9-G2[A_CI]",
      "profile_family_id": "A_CI",
      "review": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_CI-G2Review.json",
        "record_digest": "2a1211974eaa047456c9a8f791c501e4c3087d2d2037ff1e8bf577b38ae093ae"
      },
      "review_metrics": {
        "catalog_cells": 28,
        "numerical_tests_rerun": 0,
        "supplemental_interface_methods": 1
      },
      "state": "accepted",
      "view_key": "a_ci_g2_review"
    }
  ],
  "schema": "phase9_exact_profile_g2_registry_v1"
};
