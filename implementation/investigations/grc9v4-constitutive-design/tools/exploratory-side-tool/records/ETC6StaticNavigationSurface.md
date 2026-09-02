# ET-C6 Static Navigation Surface

**Status:** Accepted

Iteration 6 adds a static browser workbench over Python-compiled
selection projections. Search, family selection, graph layout, and
presentation run in the client; propagation and ripple compilation do not.

## Result

- object families: `9` / `67 objects`
- catalog: `436 nodes`
- selection projections: `436`
- focus envelope: `32 nodes / 72 relationships maximum`
- static bundle digest: `45a96e782a1ecdd5fb693e171052a020bfdbffa76d21ca07e0a307b9cc96684c`
- cross-surface parity digest: `341efa17d6c03c6235aca45141736302d418c162dd88ac6bd7a4cb7d50170b20`
- web build manifest digest: `20f1dca4094c3ff3c8743694455d545ca0c56c7f5bd1fc7c786a6ce9047a03c2`
- accepted record digest: `6353caaf1cb67b4228bfd9d74a4898a72a8ba886dcb84b55757d019b0d1c3629`
- independent audit: `44,895 checks / 7 cross-surface parity rows`
- focused tests: `47 Python checks / 8 Node tests`
- browser pressure: `desktop + mobile passed`
- predecessor regression: `ET-C5 full verification passed`

The source-state label is a build-time snapshot in a standalone static
bundle. Build and serve launchers refresh source discovery before output.
Iteration 7 is authorized but is not implemented by this gate.
