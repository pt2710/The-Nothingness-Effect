# TNE artifact provenance report

## Regenerated coverage

All 18 deterministic artifact suites were executed at seed 0 outside the Git
root. They produced:

| Artifact class | Count |
| --- | ---: |
| Theorem-level manifests | 136 |
| Numerical/metrics tables | 18 |
| Static figures | 18 |
| Canonical animation generators | 8 |

The manifest IDs match the 136 `implemented` inventory rows exactly, with zero
duplicates and zero missing entries. Every manifest records the appendix
filename and SHA-256, repository start/result commit, parameters and parameter
hash, seed, numerical tolerances, residual vector, closure status, generated
files, regeneration command, approximation metadata, and the claim boundary:

```text
finite computational support; not a formal proof substitute
```

## Retention policy

Large regenerable outputs remain outside Git. The repository tracks the
aggregate `docs/data/artifact_provenance_manifest.json`, generator code, compact
status data, and three representative AI figures:

- `docs/figures/qenn_spatial_closure.png`
- `docs/figures/pgqenn_prime_graph.png`
- `docs/figures/soinets_spatial_closure.png`

The aggregate manifest uses `<output-root>` placeholders, so regeneration
commands are portable and do not expose a workstation path.

## Validation

`python -m tools.qa_guards` requires exactly one aggregate manifest per
implemented complex, the canonical claim boundary, 351 unique inventory IDs,
all implemented source dependencies, and zero tracked `.tex` files. Artifact
smoke tests separately validate each generator's files and schema.
