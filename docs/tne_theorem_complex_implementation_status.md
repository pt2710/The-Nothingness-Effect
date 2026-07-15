# TNE theorem-complex implementation status

The machine-readable authority for counts is
`docs/data/theorem_complex_implementation_matrix.csv`. Status is upgraded to
`implemented` only after the contract, required source-removal checks,
boundary/failure behavior, simulation runner, and provenance-manifest smoke test
exist.

## Current totals

| Level | Inventory | Implemented |
| --- | ---: | ---: |
| A | 204 | 4 |
| B | 98 | 2 |
| C | 49 | 1 |
| Total | 351 | 7 |

Remaining status is 270 `proxy_only` and 74 `not_implemented`. Those labels are
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
