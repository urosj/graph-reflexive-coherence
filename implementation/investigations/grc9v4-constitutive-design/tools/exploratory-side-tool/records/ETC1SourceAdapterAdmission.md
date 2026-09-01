# ET-C1 Source Adapter And Bundle Admission

**Status:** Accepted

Iteration 1 admits schema-specific, read-only source adapters and a
versioned bundle manifest. It does not construct graph semantics.

## Result

- admitted source records: `33`
- source observation: `current_bundle_exact`
- source-bundle digest: `79e84f7839e1b65f3e55eeadb980e6d8d9b57d240aced93a8bf3a7e82851dffc`
- reference checks: `3753`
- relationship witness contract: `14 families / 2073 relationships`
- relationship witness digest: `1793217d1f0726e8735a1c8d18c1b8c70148d30559037e293a33fc799b47997f`
- accepted populations: `39 current claims / 29 historical claims / 29 debt transformations / 11 verification obligations`
- provenance populations: `67 parent objects / 152 equation-contracts`
- lifecycle coverage: `10 profiles / 26 operations / 260 cells`
- embedded identities: `70 repository-local byte-verified / 4 external attestations`
- record digest: `85a1dfd45d5c68f84aa63f06bc792d1b09075c1ad9fcaeeda953278dae3b0c35`
- accepted source bytes: `unchanged`
- claim authority classifications: `39/39 exact agreement`
- Iteration 2: `authorized; not implemented`

## Evolution Boundary

New, changed, missing, or unreadable records are reported through a
separate observation receipt. They are never auto-parsed or inserted
into the admitted bundle. A successor adapter/readmission and complete
rebuild cycle is required before current-state labeling.

External theory identities remain frozen attestations; this portable
tool does not depend on or resolve an adjacent repository checkout.
D10.1 remains an explicitly filename-admitted legacy-schema record;
adding or changing its schema requires source readmission.

## Claim Boundary

This gate validates source identity and references only. Support-edge
semantics, graph construction, ripple behavior, and scientific claim
promotion remain closed.

Human-accepted ET-C0 is the explicit root of trust. ET-C1 verifies its
accepted status and exact digest; it does not attempt to derive the
human acceptance decision. No browser runtime exists in this iteration.
Independent acceptance audit must rederive and exactly match every
relationship-witness family count and digest; matching aggregate
population counts alone is insufficient.
