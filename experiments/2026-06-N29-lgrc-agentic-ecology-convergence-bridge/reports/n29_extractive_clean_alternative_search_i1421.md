# N29 I14.2-1 Clean Extractive Alternative Search

## Result

```text
status = passed
acceptance_state = accepted_clean_extractive_alternative_search_no_admissible_replacement_found
clean_replacement_candidate_created = false
clean_source_candidate_found = false
best_merge_leakage_value = 0.033
best_merge_leakage_ceiling = 0.025
should_rerun_i14b_i14c_with_i14_2_1 = false
output_digest = 61a3fec4f97b5549fa1621451e68b3a1118d3f1e773584fe614ec168bd221b97
failed_checks = []
```

## Interpretation

I14.2-1 searched the source-backed N28 extractive portfolio for a cleaner
replacement for I14.2: an extractive source-current row whose merge/leakage
is below the declared N28 ceiling. It did not find one. The best available
positive extractive source remains the original I4-B row, with leakage
0.033 against a 0.025 ceiling. The later I4-C and I4-C2 extractive rows
strengthen extractive mechanism diversity, but their leakage is larger, not
cleaner.

Lower-leakage rows do exist in the N28 transition matrix, but those rows are
neutral-gap / unclassified control rows. They are not supported extractive
source-current candidates and cannot be used to replace I14.2.

## Candidate Sources

| Source row | Leakage | Ceiling | Clean candidate | Status |
| --- | ---: | ---: | --- | --- |
| n28_i4b_row_primary_extractive_contrast | 0.033 | 0.025 | false | blocked_by_merge_leakage_ceiling |
| n28_i4c_row_extractive_strengthening_contrast | 0.036 | 0.025 | false | blocked_by_merge_leakage_ceiling |
| n28_i4c2_row_extractive_mechanism_diversity_contrast | 0.043 | 0.025 | false | blocked_by_merge_leakage_ceiling |

## Consequence For I14-B/C

Because I14.2-1 did not create a replacement runtime candidate, I14-B and
I14-C should not be rerun just to include this row. A focused I14.2-1-B/C
or expanded I14-B/C rerun becomes necessary only after a future source-current
extractive row satisfies the clean bounded-leakage gate.
