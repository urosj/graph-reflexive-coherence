# ET-C8 Lineage And Ripple Navigation

**Status:** Accepted

Iteration 8 compiles the accepted predecessor DAG into a readable
scrub spine with branch, correction, and supersession overlays. It
also binds every accepted ET-C5 ripple row to exact scenario bytes
and four precomputed playback frames.

## Accepted Result

- accepted gate records: `33`
- scrub positions: `26`
- branch nodes: `7`
- correction markers: `1`
- supersession markers: `4`
- backward claim reconstructions: `68`
- precomputed playback rows: `24`
- layer digest: `5c5c29a9c636c5a91e2cf37921c323f97ef42ddb9d21442b4e44e17426b50faa`
- web manifest digest: `dc1456e975c0851d1ecc817422f2cedb9c25e0b182c3cbca2147b4d634f7bee7`
- accepted record digest: `003fa28d39e32babb60a673cbc5a119326afdec3072f5274663911f4f20088a2`

The scrubber follows accepted record identity, not a false linear
scientific timeline. D7G post-v2 remains an accepted companion
correction, and D9/D10 support records remain visible branches.

Playback is presentation of ET-C5 rows only. Direct consequences,
transitive consequences, reopening roots, and unresolved evidence
frontiers remain distinct. The browser has no propagation rules,
cannot edit scenarios, and cannot predict rerun outcomes.

Human review accepted this bounded presentation layer. Iteration 9
is authorized but is not implemented by this gate.

## Verification

- deterministic rebuilds: `2`, byte-identical
- independent source audit: `34,241` checks (`1,049` structural + `33,192` per-edge-reference assertions over `11,064` links)
- focused Python pressure: `185` checks
- Node component tests: `17` across `4` files
- Playwright: `8` tests across desktop and mobile, `10` screenshots
- ET-C7 predecessor regression: `477` checks
- shared-dist boundary: ET-C7 full-dist hashes are historical after the ET-C8 build; focused source/layer regression passed
- visual inspection: passed without overlap, clipping, or authority conflation
- human acceptance: accepted
- Iteration 9 authorization: authorized; not implemented
