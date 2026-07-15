# TNE source-law registry

## Authority and inventory

The seven authoritative appendix `.tex` files are external read-only inputs.
The repository registry stores only filenames, SHA-256 digests, theorem IDs,
labels, implementation paths, and bounded status metadata. The verified
inventory is 351 unique complexes: 204 A, 98 B, and 49 C.

| Appendix | Total | A | B | C | Implemented | Proxy | Not implemented |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Canonical Flowpoint | 7 | 4 | 2 | 1 | 7 | 0 | 0 |
| Mathematical Closure | 7 | 4 | 2 | 1 | 7 | 0 | 0 |
| Foundational Closure | 79 | 43 | 22 | 14 | 6 | 65 | 8 |
| Fluctuation and Elastic Dynamics | 36 | 22 | 10 | 4 | 31 | 5 | 0 |
| Gravitational/Cosmological/Quantum | 136 | 82 | 37 | 17 | 49 | 60 | 27 |
| Artificial Intelligence | 71 | 40 | 21 | 10 | 21 | 50 | 0 |
| Completeness | 15 | 9 | 4 | 2 | 15 | 0 | 0 |
| **Total** | **351** | **204** | **98** | **49** | **136** | **180** | **35** |

## Contract interpretation

An A record is `implemented` only when it has an independent typed operator,
domain, codomain, parameter conditions, residual/invariant, failure behavior,
and finite tolerance policy where applicable. A B record additionally requires
a new two-source law, non-cancellation, and removal of each complete A source.
A C record additionally requires a spatial domain/local operator,
boundary/leakage/localization diagnostics, all-B removal, and the applicable
coercivity, reconstruction, observability, or attainment boundary.

Canonical highlights include:

- Flowpoint `F(x)=-x`, finite parity/2-adic scheduling, fiber transport, and an
  affine history field;
- fail-closed normalized DFI, parity-conditioned pDFI, exact Elastic-π
  `pi*exp(-S/K_D)` for `K_D>0`, and weighted-path diagnostics;
- selected physical 4A→2B→1C chains across seven dynamics modules;
- all fifteen completeness contracts without promoting finite closure to
  formal proof;
- source-complete QENN, PGQENN, and SOInet chains.

The machine-readable authority is `docs/data/source_law_registry.json`. It
contains all 351 records and the verified source checksums.
