// Generated from ProfileG2Registry.json; checked by the registry validator.
export const G2_REGISTRY = {
  "materializers": [
    {
      "dependency": "profile_conformance_review",
      "kind": "local",
      "module": "verify_p977_a_os_local",
      "view_key": "a_os_local_product"
    },
    {
      "dependency": "a_os_local_product",
      "kind": "crossing",
      "module": "verify_p977_a_os_acceptance",
      "view_key": "a_os_crossings"
    },
    {
      "dependency": "a_os_crossings",
      "kind": "g2",
      "module": "verify_p977_a_os_g2",
      "view_key": "a_os_g2_review"
    },
    {
      "dependency": "profile_conformance_review",
      "kind": "local",
      "module": "verify_p977_a_ci_local",
      "view_key": "a_ci_local_product"
    },
    {
      "dependency": "a_ci_local_product",
      "kind": "crossing",
      "module": "verify_p977_a_ci_acceptance",
      "view_key": "a_ci_crossings"
    },
    {
      "dependency": "a_ci_crossings",
      "kind": "g2",
      "module": "verify_p977_a_ci_g2",
      "view_key": "a_ci_g2_review"
    },
    {
      "dependency": "profile_conformance_review",
      "kind": "local",
      "module": "verify_p977_c_ci_local",
      "view_key": "c_ci_local_product"
    },
    {
      "dependency": "c_ci_local_product",
      "kind": "crossing",
      "module": "verify_p977_c_ci_acceptance",
      "view_key": "c_ci_crossings"
    },
    {
      "dependency": "c_ci_crossings",
      "kind": "g2",
      "module": "verify_p977_c_ci_g2",
      "view_key": "c_ci_g2_review"
    },
    {
      "dependency": "profile_conformance_review",
      "kind": "local",
      "module": "verify_p977_a_pc_local",
      "view_key": "a_pc_local_product"
    },
    {
      "dependency": "a_pc_local_product",
      "kind": "crossing",
      "module": "verify_p977_a_pc_acceptance",
      "view_key": "a_pc_crossings"
    }
  ],
  "reconciliation_views": {
    "a_ci_crossings": {
      "G2_accepted": false,
      "G3_accepted": false,
      "acceptance_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_CI-CrossingReview.md",
      "acceptance_sha256": "f08c2d2017702d2d36cf1c3e2bf8ed90dae0a7003e809395c23a03e082a25a0c",
      "aggregate_closed": false,
      "all_ordered_pairs_verified": false,
      "complete_profile_id": "grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946",
      "local_cells": 21,
      "matrix_scope": "exact_positive_and_negative_endpoints; separate_PC_pairs; not_all_pairs",
      "new_G2_support": [],
      "new_execution_cases": 6,
      "numerical_tests_rerun": 0,
      "ordered_migration_classes": 7,
      "reconciled_crossing_cells": 7,
      "record_digest": "a5d8a9ea17843359b57e094cacb7f8d0dde1fa9ab46480f1eae6632acd2aba80",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_CI-Crossings.json",
      "retained_alias_count": 5,
      "status": "accepted_bounded_reconciliation",
      "test_count": 3,
      "user_accepted": true
    },
    "a_ci_local_product": {
      "G2_accepted": false,
      "G3_accepted": false,
      "aggregate_closed": false,
      "complete_profile_id": "grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946",
      "new_G2_support": [],
      "numerical_tests_rerun": 0,
      "record_digest": "9a7e34069d40b391d71a47c89a184a445e757383409747bd03cdd4d2a9c350d3",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_CI-LocalProduct.json",
      "remaining_catalog_cases": [
        "A-MIGRATION-HISTORY-RECEIPT",
        "ALL-MIGRATION-CLASSES",
        "HISTORY-DISPOSITION",
        "RESET-AFTER-EVENT",
        "RESET-AFTER-MIGRATION",
        "TARGET-READMISSION-FAILURE",
        "WHOLE-LIFECYCLE-TUPLE-MAP"
      ],
      "status": "local_product_verified_pending_review",
      "test_count": 3,
      "user_accepted": false,
      "verified_local_cells": 21
    },
    "a_os_crossings": {
      "G2_accepted": false,
      "G3_accepted": false,
      "acceptance_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_OS-CrossingReview.md",
      "acceptance_sha256": "980f8676b89c45e2d027b7c76f73324c5d759a3b6d161f66db6681709004e657",
      "aggregate_closed": false,
      "all_ordered_pairs_verified": false,
      "complete_profile_id": "grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4",
      "local_cells": 21,
      "matrix_scope": "exact_positive_and_negative_endpoints; separate_PC_pairs; not_all_pairs",
      "new_G2_support": [],
      "new_execution_cases": 6,
      "numerical_tests_rerun": 0,
      "ordered_migration_classes": 7,
      "reconciled_crossing_cells": 7,
      "record_digest": "2322b1a2f8b6b4904b38200f2f9018356db2698fbaafd53fe6c9ef8497afc351",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_OS-Crossings.json",
      "retained_alias_count": 5,
      "status": "accepted_bounded_reconciliation",
      "test_count": 3,
      "user_accepted": true
    },
    "a_os_local_product": {
      "G2_accepted": false,
      "G3_accepted": false,
      "aggregate_closed": false,
      "complete_profile_id": "grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4",
      "new_G2_support": [],
      "numerical_tests_rerun": 0,
      "record_digest": "21328fd2ae791fdc875a5f874153e876ec2a94d690cf42da014df20f9d3eada8",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_OS-LocalProduct.json",
      "remaining_catalog_cases": [
        "A-MIGRATION-HISTORY-RECEIPT",
        "ALL-MIGRATION-CLASSES",
        "HISTORY-DISPOSITION",
        "RESET-AFTER-EVENT",
        "RESET-AFTER-MIGRATION",
        "TARGET-READMISSION-FAILURE",
        "WHOLE-LIFECYCLE-TUPLE-MAP"
      ],
      "status": "local_product_verified_pending_review",
      "test_count": 3,
      "user_accepted": false,
      "verified_local_cells": 21
    },
    "a_pc_crossings": {
      "G2_accepted": false,
      "G3_accepted": false,
      "acceptance_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_PC-CrossingReview.md",
      "acceptance_sha256": "23a4cc11997d9035a6d3d89442be2b65b717cd522cb621ca2127d5164956e957",
      "aggregate_closed": false,
      "all_ordered_pairs_verified": false,
      "complete_profile_id": "grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75",
      "local_cells": 21,
      "matrix_scope": "exact_PC_pairs_and_two_channel_losses; separate_nonhistory_and_initializer_endpoints; not_all_pairs",
      "new_G2_support": [],
      "new_execution_cases": 5,
      "numerical_tests_rerun": 0,
      "ordered_migration_classes": 7,
      "reconciled_crossing_cells": 7,
      "record_digest": "4cf4b3405f775a790d7535891e32747378f3b4cac2e1cdf0d736f2225b619edc",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_PC-Crossings.json",
      "retained_alias_count": 7,
      "status": "accepted_bounded_reconciliation",
      "test_count": 3,
      "user_accepted": true
    },
    "a_pc_local_product": {
      "G2_accepted": false,
      "G3_accepted": false,
      "aggregate_closed": false,
      "complete_profile_id": "grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75",
      "new_G2_support": [],
      "numerical_tests_rerun": 0,
      "record_digest": "fb13a73a10e3ffb7cfde778ce86b89e238ae0c893eb11f5f0ed5d8352c2ff6e7",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_PC-LocalProduct.json",
      "remaining_catalog_cases": [
        "A-MIGRATION-HISTORY-RECEIPT",
        "ALL-MIGRATION-CLASSES",
        "HISTORY-DISPOSITION",
        "RESET-AFTER-EVENT",
        "RESET-AFTER-MIGRATION",
        "TARGET-READMISSION-FAILURE",
        "WHOLE-LIFECYCLE-TUPLE-MAP"
      ],
      "status": "local_product_verified_pending_review",
      "test_count": 4,
      "user_accepted": false,
      "verified_local_cells": 21
    },
    "c_ci_crossings": {
      "G2_accepted": false,
      "G3_accepted": false,
      "acceptance_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI-CrossingReview.md",
      "acceptance_sha256": "6855f835006f1502acae874189b0476cb307ce4bc1dec0e8467ebf2fa3e2ab5c",
      "aggregate_closed": false,
      "all_ordered_pairs_verified": false,
      "complete_profile_id": "grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e",
      "local_cells": 26,
      "matrix_scope": "exact_declared_endpoints_and_reset_failure; separate_PC_pairs; not_all_pairs",
      "new_G2_support": [],
      "new_execution_cases": 5,
      "numerical_tests_rerun": 0,
      "ordered_migration_classes": 7,
      "reconciled_crossing_cells": 7,
      "record_digest": "0bb8587f208e05121d517670468611c5f0c82f8935886f6e0b2c3b0976beec21",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI-Crossings.json",
      "retained_alias_count": 5,
      "status": "accepted_bounded_reconciliation",
      "test_count": 3,
      "user_accepted": true
    },
    "c_ci_local_product": {
      "G2_accepted": false,
      "G3_accepted": false,
      "aggregate_closed": false,
      "complete_profile_id": "grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e",
      "new_G2_support": [],
      "numerical_tests_rerun": 0,
      "record_digest": "156ddbcd49040082d992d7c0c8532a6beb93409812e65f518ceab812f078fbfa",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI-LocalProduct.json",
      "remaining_catalog_cases": [
        "ALL-MIGRATION-CLASSES",
        "C-LIFECYCLE-REFERENCE-MAP",
        "HISTORY-DISPOSITION",
        "RESET-AFTER-EVENT",
        "RESET-AFTER-MIGRATION",
        "TARGET-READMISSION-FAILURE",
        "WHOLE-LIFECYCLE-TUPLE-MAP"
      ],
      "status": "local_product_verified_pending_review",
      "test_count": 4,
      "user_accepted": false,
      "verified_local_cells": 26
    }
  },
  "record_digest": "f6a6b2557456eb7131ad080faf159abf4a95692731b62c713636524139cf3a1a",
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
    },
    {
      "acceptance": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI-G2Acceptance.json",
        "record_digest": "9ccd568fea897089fd94ea4174247a4421dc2bdba675421f7c8abe2995904de6"
      },
      "adapter": "exact_profile_v1",
      "bounded_view_key": "c_ci_crossings",
      "complete_profile_id": "grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e",
      "gate": "P9-G2[C_CI]",
      "profile_family_id": "C_CI",
      "review": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI-G2Review.json",
        "record_digest": "56edc8d0a725a693a0363bf66f23bdcbe000357403928f9fd84da991c542bedc"
      },
      "review_metrics": {
        "catalog_cells": 33,
        "numerical_tests_rerun": 0,
        "supplemental_interface_methods": 1
      },
      "state": "accepted",
      "view_key": "c_ci_g2_review"
    }
  ],
  "schema": "phase9_exact_profile_g2_registry_v1"
};
