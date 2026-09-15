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
    },
    {
      "dependency": "a_pc_crossings",
      "kind": "g2",
      "module": "verify_p977_a_pc_g2",
      "view_key": "a_pc_g2_review"
    },
    {
      "dependency": "profile_conformance_review",
      "kind": "local",
      "module": "verify_p977_c_pc_local",
      "view_key": "c_pc_local_product"
    },
    {
      "dependency": "c_pc_local_product",
      "kind": "crossing",
      "module": "verify_p977_c_pc_acceptance",
      "view_key": "c_pc_crossings"
    },
    {
      "dependency": "c_pc_crossings",
      "kind": "g2",
      "module": "verify_p977_c_pc_g2",
      "view_key": "c_pc_g2_review"
    },
    {
      "dependency": "profile_conformance_review",
      "kind": "local",
      "module": "verify_p977_a_ci_pc_local",
      "view_key": "a_ci_pc_local_product"
    },
    {
      "dependency": "a_ci_pc_local_product",
      "kind": "crossing",
      "module": "verify_p977_a_ci_pc_acceptance",
      "view_key": "a_ci_pc_crossings"
    },
    {
      "dependency": "a_ci_pc_crossings",
      "kind": "g2",
      "module": "verify_p977_a_ci_pc_g2",
      "view_key": "a_ci_pc_g2_review"
    },
    {
      "dependency": "profile_conformance_review",
      "kind": "local",
      "module": "verify_p977_c_ci_pc_local",
      "view_key": "c_ci_pc_local_product"
    },
    {
      "dependency": "c_ci_pc_local_product",
      "kind": "crossing",
      "module": "verify_p977_c_ci_pc_acceptance",
      "view_key": "c_ci_pc_crossings"
    },
    {
      "dependency": "c_ci_pc_crossings",
      "kind": "g2",
      "module": "verify_p977_c_ci_pc_g2",
      "view_key": "c_ci_pc_g2_review"
    },
    {
      "dependency": "profile_conformance_review",
      "kind": "local",
      "module": "verify_p977_a_rg2b_local",
      "view_key": "a_rg2b_local_product"
    },
    {
      "dependency": "a_rg2b_local_product",
      "kind": "crossing",
      "module": "verify_p977_a_rg2b_acceptance",
      "view_key": "a_rg2b_crossings"
    },
    {
      "dependency": "a_rg2b_crossings",
      "kind": "g2",
      "module": "verify_p977_a_rg2b_g2",
      "view_key": "a_rg2b_g2_review"
    },
    {
      "dependency": "profile_conformance_review",
      "kind": "local",
      "module": "verify_p977_c_rg2b_local",
      "view_key": "c_rg2b_local_product"
    },
    {
      "dependency": "c_rg2b_local_product",
      "kind": "crossing",
      "module": "verify_p977_c_rg2b_acceptance",
      "view_key": "c_rg2b_crossings"
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
    "a_ci_pc_crossings": {
      "G2_accepted": false,
      "G3_accepted": false,
      "acceptance_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_CI_PC-CrossingReview.md",
      "acceptance_sha256": "b4fde37466d1c222e02d7e4352e431fb569142e6d7658d7181455bc337875275",
      "aggregate_closed": false,
      "all_ordered_pairs_verified": false,
      "complete_profile_id": "grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689",
      "local_cells": 21,
      "matrix_scope": "exact_CI_PC_nonpersistent_pairs_and_retained_PC_pairs; separate_initializer_target; not_all_pairs",
      "new_G2_support": [],
      "new_execution_cases": 7,
      "numerical_tests_rerun": 0,
      "ordered_migration_classes": 7,
      "reconciled_crossing_cells": 7,
      "record_digest": "484beef4f47d73f0c255c50c5299fcb79179dfa59813a2dde1a2a868e461b4e5",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_CI_PC-Crossings.json",
      "retained_alias_count": 5,
      "status": "accepted_bounded_reconciliation",
      "test_count": 4,
      "user_accepted": true
    },
    "a_ci_pc_local_product": {
      "G2_accepted": false,
      "G3_accepted": false,
      "aggregate_closed": false,
      "complete_profile_id": "grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689",
      "new_G2_support": [],
      "numerical_tests_rerun": 0,
      "record_digest": "456ba01d2b25c9d035a40081f56d3afc482775fd8d0ebf5a9b89b64ac3f5938d",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_CI_PC-LocalProduct.json",
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
      "test_count": 5,
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
    "a_rg2b_crossings": {
      "G2_accepted": false,
      "G3_accepted": false,
      "acceptance_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_RG2b-CrossingReview.md",
      "acceptance_sha256": "a9bc7038055e03f836b4b5d9c538e1eb23d2fbc4f25bde21471d1379902de41a",
      "aggregate_closed": false,
      "all_ordered_pairs_verified": false,
      "complete_profile_id": "grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b",
      "local_cells": 21,
      "matrix_scope": "exact_graph_positive_and_negative_endpoints; scalar_PC_pairs_and_initializer_separate; not_all_pairs",
      "new_G2_support": [],
      "new_execution_cases": 9,
      "numerical_tests_rerun": 0,
      "ordered_migration_classes": 7,
      "reconciled_crossing_cells": 7,
      "record_digest": "73d4c7823d18e71464e61f377a1cb8a93c9654c47cd5b2ff4727d20b0b7093a2",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_RG2b-Crossings.json",
      "retained_alias_count": 4,
      "status": "accepted_bounded_reconciliation",
      "test_count": 3,
      "user_accepted": true
    },
    "a_rg2b_local_product": {
      "G2_accepted": false,
      "G3_accepted": false,
      "aggregate_closed": false,
      "complete_profile_id": "grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b",
      "new_G2_support": [],
      "numerical_tests_rerun": 0,
      "record_digest": "669ca8eec0cee1e3621f077bbea723f0861ef4060c6254627b1f84463920f14d",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_RG2b-LocalProduct.json",
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
    },
    "c_ci_pc_crossings": {
      "G2_accepted": false,
      "G3_accepted": false,
      "acceptance_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI_PC-CrossingReview.md",
      "acceptance_sha256": "8d41aa8203542c157a3593fbd6c938123aef0ef593885c81292c12b9caa33d7e",
      "aggregate_closed": false,
      "all_ordered_pairs_verified": false,
      "complete_profile_id": "grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b",
      "local_cells": 26,
      "matrix_scope": "exact_PC_pairs_and_two_channel_losses; separate_nonhistory_and_initializer_target; not_all_pairs",
      "new_G2_support": [],
      "new_execution_cases": 8,
      "numerical_tests_rerun": 0,
      "ordered_migration_classes": 7,
      "reconciled_crossing_cells": 7,
      "record_digest": "c15ae17c287fe89aab2f41cff778fa7a086d88f1e9713ed04e9564dacf173c5b",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI_PC-Crossings.json",
      "retained_alias_count": 3,
      "status": "accepted_bounded_reconciliation",
      "test_count": 4,
      "user_accepted": true
    },
    "c_ci_pc_local_product": {
      "G2_accepted": false,
      "G3_accepted": false,
      "aggregate_closed": false,
      "complete_profile_id": "grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b",
      "new_G2_support": [],
      "numerical_tests_rerun": 0,
      "record_digest": "abc34f0442d9e2bc1aeecb18c946e7fd894070a4be7a9894d6a79593fd23d5f6",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI_PC-LocalProduct.json",
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
      "test_count": 5,
      "user_accepted": false,
      "verified_local_cells": 26
    },
    "c_pc_crossings": {
      "G2_accepted": false,
      "G3_accepted": false,
      "acceptance_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_PC-CrossingReview.md",
      "acceptance_sha256": "442d9417d01b362a5531817b68f2c1d57343cc88d6b76055659535f0a18edbcd",
      "aggregate_closed": false,
      "all_ordered_pairs_verified": false,
      "complete_profile_id": "grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f",
      "local_cells": 26,
      "matrix_scope": "exact_PC_pairs_and_two_channel_losses; separate_nonhistory_and_initializer_target; not_all_pairs",
      "new_G2_support": [],
      "new_execution_cases": 4,
      "numerical_tests_rerun": 0,
      "ordered_migration_classes": 7,
      "reconciled_crossing_cells": 7,
      "record_digest": "d18e5fe2a2bba6b2a11992ab8f22edda423cb3c2f8934937e22ab77df3acad49",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_PC-Crossings.json",
      "retained_alias_count": 7,
      "status": "accepted_bounded_reconciliation",
      "test_count": 3,
      "user_accepted": true
    },
    "c_pc_local_product": {
      "G2_accepted": false,
      "G3_accepted": false,
      "aggregate_closed": false,
      "complete_profile_id": "grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f",
      "new_G2_support": [],
      "numerical_tests_rerun": 0,
      "record_digest": "9a57f0aa2bd77bca5298c517926906b3ff8f6c8d274c4856c1fb2fabf9283b7a",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_PC-LocalProduct.json",
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
      "test_count": 5,
      "user_accepted": false,
      "verified_local_cells": 26
    },
    "c_rg2b_crossings": {
      "G2_accepted": false,
      "G3_accepted": false,
      "acceptance_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_RG2b-CrossingReview.md",
      "acceptance_sha256": "3a8bda111dd99b55c7c99dadd11f9c9ce789a4ab1303e1945fc4216bc9e6b5a5",
      "aggregate_closed": false,
      "all_ordered_pairs_verified": false,
      "complete_profile_id": "grcv4-profile-sha256:413497bec4f219ec402d82d5cd2aced01dca25a58d2ab906c348472b98d596b0",
      "local_cells": 26,
      "matrix_scope": "exact_graph_endpoints_and_initializer_selected_A_OS; separate_PC_pairs; not_all_pairs",
      "new_G2_support": [],
      "new_execution_cases": 9,
      "numerical_tests_rerun": 0,
      "ordered_migration_classes": 7,
      "reconciled_crossing_cells": 7,
      "record_digest": "f6b717563826c8af1d333390b22cfaf7c6967ff01e5636a7b9b90dc7aff6feaf",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_RG2b-Crossings.json",
      "retained_alias_count": 2,
      "status": "accepted_bounded_reconciliation",
      "test_count": 3,
      "user_accepted": true
    },
    "c_rg2b_local_product": {
      "G2_accepted": false,
      "G3_accepted": false,
      "aggregate_closed": false,
      "complete_profile_id": "grcv4-profile-sha256:413497bec4f219ec402d82d5cd2aced01dca25a58d2ab906c348472b98d596b0",
      "new_G2_support": [],
      "numerical_tests_rerun": 0,
      "record_digest": "c1ae20f54de30316421125e1a24fce4c1cee36874c487b69350a75748b9c3ffd",
      "record_path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_RG2b-LocalProduct.json",
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
      "test_count": 5,
      "user_accepted": false,
      "verified_local_cells": 26
    }
  },
  "record_digest": "fbe958a22aed0143c7e57d95ef5d8c4120272d1442ab1ca4aab07f3936524d17",
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
    },
    {
      "acceptance": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_PC-G2Acceptance.json",
        "record_digest": "6ee6f66234395ff9559f87860de930c88556910f0a88132b3e938c4b0cd6a891"
      },
      "adapter": "exact_profile_v1",
      "bounded_view_key": "a_pc_crossings",
      "complete_profile_id": "grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75",
      "gate": "P9-G2[A_PC]",
      "profile_family_id": "A_PC",
      "review": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_PC-G2Review.json",
        "record_digest": "7077df309bb98e3e214667b0ca903cd318c4e9036ef8c61f7aeadb2bbfc95cac"
      },
      "review_metrics": {
        "catalog_cells": 28,
        "numerical_tests_rerun": 0,
        "supplemental_interface_methods": 1
      },
      "state": "accepted",
      "view_key": "a_pc_g2_review"
    },
    {
      "acceptance": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_PC-G2Acceptance.json",
        "record_digest": "c9ba763f85877febcaeb044b5e23fca20801f7bdac0fc8b189042e0432da6eb6"
      },
      "adapter": "exact_profile_v1",
      "bounded_view_key": "c_pc_crossings",
      "complete_profile_id": "grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f",
      "gate": "P9-G2[C_PC]",
      "profile_family_id": "C_PC",
      "review": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_PC-G2Review.json",
        "record_digest": "788b7de8d37828904967097270725057d83f1c5222e310ca466298902334b1f5"
      },
      "review_metrics": {
        "catalog_cells": 33,
        "numerical_tests_rerun": 0,
        "supplemental_interface_methods": 1
      },
      "state": "accepted",
      "view_key": "c_pc_g2_review"
    },
    {
      "acceptance": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_CI_PC-G2Acceptance.json",
        "record_digest": "ddec04e9d1829272d9fb0c106c69b945e1451b333e5164fdf5b13768f49642b6"
      },
      "adapter": "exact_profile_v1",
      "bounded_view_key": "a_ci_pc_crossings",
      "complete_profile_id": "grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689",
      "gate": "P9-G2[A_CI_PC]",
      "profile_family_id": "A_CI_PC",
      "review": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_CI_PC-G2Review.json",
        "record_digest": "abb89b7309b9978c107fb43b76ee4d0d3c9d3640543d5746d1c869ed27f669f6"
      },
      "review_metrics": {
        "catalog_cells": 28,
        "numerical_tests_rerun": 0,
        "supplemental_interface_methods": 1
      },
      "state": "accepted",
      "view_key": "a_ci_pc_g2_review"
    },
    {
      "acceptance": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI_PC-G2Acceptance.json",
        "record_digest": "7fa14783afb04f5a105f2dc35fe843c87c2a5a80efc414823494be37334b87b5"
      },
      "adapter": "exact_profile_v1",
      "bounded_view_key": "c_ci_pc_crossings",
      "complete_profile_id": "grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b",
      "gate": "P9-G2[C_CI_PC]",
      "profile_family_id": "C_CI_PC",
      "review": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-C_CI_PC-G2Review.json",
        "record_digest": "863730d90209e4813075c7b517a68df3e9587fe87c1ef4b04638a03f4a340858"
      },
      "review_metrics": {
        "catalog_cells": 33,
        "numerical_tests_rerun": 0,
        "supplemental_interface_methods": 1
      },
      "state": "accepted",
      "view_key": "c_ci_pc_g2_review"
    },
    {
      "acceptance": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_RG2b-G2Acceptance.json",
        "record_digest": "7887a2e24d38c58898527ac4eacb9836a2db165e0d033a5a85e61db08522790d"
      },
      "adapter": "exact_profile_v1",
      "bounded_view_key": "a_rg2b_crossings",
      "complete_profile_id": "grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b",
      "gate": "P9-G2[A_RG2b]",
      "profile_family_id": "A_RG2b",
      "review": {
        "path": "implementation/phase-9-grcv4/tranche-7/P9-7.7-A_RG2b-G2Review.json",
        "record_digest": "71c459901d2590022d44775b8101ac08a2b52e15334032fd8bd4b1735cb84b1f"
      },
      "review_metrics": {
        "catalog_cells": 28,
        "numerical_tests_rerun": 0,
        "supplemental_interface_methods": 1
      },
      "state": "accepted",
      "view_key": "a_rg2b_g2_review"
    }
  ],
  "schema": "phase9_exact_profile_g2_registry_v1"
};
