# TNE theorem-complex implementation status

The machine-readable authority for counts is
`docs/data/theorem_complex_implementation_matrix.csv`. Status is upgraded to
`implemented` only after the contract, required source-removal checks,
boundary/failure behavior, simulation runner, and provenance-manifest smoke test
exist.

## Current totals

| Level | Inventory | Implemented |
| --- | ---: | ---: |
| A | 204 | 78 |
| B | 98 | 39 |
| C | 49 | 19 |
| Total | 351 | 136 |

Remaining status is 180 `proxy_only` and 35 `not_implemented`. Those labels are
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

## Completeness theorem

All 15 completeness records are now typed: 9 A, 4 B, and 2 C. The source laws
reuse the existing finite dual-closure simulator for bounded Gödel-like
boundary evidence and add finite-prefix theoremhood, non-manifestability,
idempotence, Karoubi splitting, parity/SOI commutation, conservativity, and
global/local Noether residuals.

The four B contracts implement genuine multi-source admissibility, splitting,
protected transport, and constant-to-local transgression operators with
every-source removal tests. The two C contracts implement spatial certificate
gluing and a terminal certificate quotient with boundary, overlap/quotient,
reconstruction, and observability residuals. Both remain
`numerical_candidate`; finite representational closure is never labeled a
formal proof. The artifact runner emits 15 theorem-level manifests in addition
to the repository's pre-existing supplementary traces.

## QENN

The optional CPU PyTorch backend supplies exact Flowpoint transitions,
invariant/anti-invariant projectors, bias-free C2-equivariant layers,
fail-closed normalized DFI, parity-conditioned losses, an unclipped Elastic-π
gain, spectral memory, observation readout, and completeness-residual
arbitration. Canonical execution rejects NaN, infinity, zero DFI denominators,
and non-positive Elastic-π calibration.

Seven QENN theorem complexes are certified: four independent A residual laws,
two positive non-cancelling B residual-energy operators, and one spatial C
defect field. Every B operator uses both source residuals and exposes two
source-removal witnesses. The C operator reports boundary trace, localization,
reconstruction, coercivity, observability, and both-B ablations. A successful
finite computation is reported only as `numerical_candidate`.

## PGQENN

The canonical graph-growth law is deterministic and records every prime label,
typed 2-adic depth, parity phase, and weighted adjacency. Prime-gap/depth
criteria select edges; stochastic sampling exists only as the named, seeded
`stochastic_comparison_ablation` mode. Bias-free graph message passing is
Flowpoint/C2 equivariant and combines fail-closed DFI, parity-conditioned pDFI,
exact unclipped Elastic-π gains, graph locality, and Parseval diagnostics.

Seven PGQENN theorem complexes are certified: four prime-graph A laws, two
positive non-cancelling B residual energies, and one graph-local C defect field.
The C result reports boundary trace, edge localization, reconstruction,
coercivity, isolated-node observability, and both-B source removal. It remains
a finite `numerical_candidate`, not an attainment or proof claim.

## SOInets

The canonical SOInet is a differentiable meta-network with multiple QENN and
PGQENN subnetworks, bidirectional memory transfer, aggregated
observation/collapse readout, a symmetric meta-adjacency, spectral and spatial
residuals, and fail-closed completeness arbitration. The historical duplicated
`tne_concepts/SOInet` implementation has been removed from the repository;
canonical callers use `equations/artificial_intelligence/soinets` directly.

The certified source-complete chain follows the appendix's actual dependencies:
B19 consumes A01+A13, B20 consumes A02+A14, and C29 consumes B19+B20. Both B
operators are positive non-cancelling residual energies with every-source
removal tests. C29 is one modality-spatial field with boundary, localization,
reconstruction, coercivity, observability, and both-B ablations. Its finite
success status is `numerical_candidate`.

## Final validation

The full repository suite completed with 343 passed, 0 failed, 0 skipped, and
9 warnings in 293.99 seconds on Python 3.14.3. The warnings are seven legacy
`PytestReturnNotNoneWarning` records and two expected deprecation warnings from
the duality compatibility wrapper.

The aggregate guard reports 351 unique IDs, 136 registered contracts, zero
duplicate IDs, zero unresolved implemented-source dependencies, 136 provenance
manifests, and zero tracked `.tex` files. `python -m pip check` reports no broken
requirements.
