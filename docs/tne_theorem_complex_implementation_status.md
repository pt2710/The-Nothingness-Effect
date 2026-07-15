# TNE theorem-complex implementation status

The machine-readable authority for counts is
`docs/data/theorem_complex_implementation_matrix.csv`. Status is upgraded to
`implemented` only after the contract, required source-removal checks,
boundary/failure behavior, simulation runner, and provenance-manifest smoke test
exist.

## Current totals

| Level | Inventory | Implemented |
| --- | ---: | ---: |
| A | 204 | 57 |
| B | 98 | 29 |
| C | 49 | 14 |
| Total | 351 | 100 |

Remaining status is 216 `proxy_only` and 35 `not_implemented`. Those labels are
deliberately not inferred upward from related legacy modules.

## Implemented Flowpoint complex chain

The seven Flowpoint records now form one traceable dependency chain:

```text
self-negating involution + parity/2-adic schedule
    -> scheduled spectral history
balance fiber + C2 phase clock
    -> phase-indexed kernel transport
both B laws
    -> affine history field
```

The A contracts define typed domains and codomains and include explicit zero,
binary-domain, positive-time-scale, and non-finite failure boundaries. The B
operators consume both complete A sources, implement new encoder/transport
laws, and have source-removal tests for each source. The C law carries a finite
discrete spatial domain, local internal gradients, boundary trace residual,
balance residual, exact reconstruction predicate, and both B-source ablations.

The artifact runner is:

```text
python -m equations.flowpoint.simulation --output <directory>
```

It writes one deterministic metrics table, one representative static figure,
and seven theorem-level provenance manifests.

## Foundational duality and mathematical closure

Six foundational-duality complexes now expose finite involutive relations,
minimal two-state actions, a genuine reciprocal double-cover law, free–cofree
duality, and a spatial invariant/anti-invariant orbit field. Fixed points remain
an explicit obstruction to the minimal double cover.

All seven mathematical-closure complexes are typed. Their two B laws implement
orientation-indexed operation transport and approximation-conditioned harmonic
geometry rather than carrying A outputs side by side. The C signed-polar field
has a declared spatial domain, local gradient, boundary trace, reconstruction
residual, and both-source ablations. Because finite calibration does not prove
attainment, its successful result remains `numerical_candidate`.

## DFI, pDFI, Elastic-π, and weighted-path closure

Thirty-one fluctuation/elastic contracts are now certified: 6 DFI, all 10
pDFI, all 7 Elastic-π, and all 8 Elastic-π Norm records. Canonical DFI returns
an explicit singular witness at a zero denominator and never masks NaN or
infinity. Legacy neutral coercion exists only behind an explicit compatibility
flag.

Elastic-π has one source law, `pi * exp(-S/K_D)` for `K_D > 0`. Exact exponent,
evaluated exponent, underflow/overflow status, and clipping metadata are
separate. Clipped results cannot be returned through the diagnostics-free
legacy tuple API. pDFI implements the integer orbit formula with nonzero
predecessors and the separately declared inverse recurrence. The weighted path
functional reports norm versus seminorm status and only compares with pDFI
through a common-input calibration residual.

Each B law has a new interaction operator and source-removal tests for every
complete A source. Each C law has a spatial domain, local operator, boundary or
leakage diagnostics, all B-source ablations, and `numerical_candidate` status.
The four artifact runners emit 31 theorem-level provenance manifests.

## Gravitational, cosmological, and quantum dynamics

Seven appendix-facing modules now expose a bounded 4A→2B→1C chain each:
Elastic Dubler Effect, Elastic Dubler Interferometry, Locality-Driven Gravity,
Black-Hole Dynamics, Elastic-π Ripples, Cosmological Spark Dynamics, and
Discrete-Time Quasicrystals. This adds 49 certified contracts while retaining
all other related legacy rows as `proxy_only` or `not_implemented`.

The selected A laws have typed uniform spatial grids, positive parameter
conditions, source responses, invariant residuals, and boundary traces. Each B
law applies a new bilinear field interaction and has non-cancellation energy
plus both-source removal tests. Each C law combines two complete B laws into a
local spatial operator with boundary and localization diagnostics, coercivity,
observability/reconstruction residuals, both-B ablations, and explicit
`numerical_candidate` status. Seven deterministic runners emit 49 additional
theorem-level manifests.
