# TNE artifact provenance report

## Regenerated coverage

All 18 deterministic artifact suites were executed at seed 0 outside the Git
root. They produced:

| Artifact class | Count |
| --- | ---: |
| Theorem-level manifests | 136 |
| Producer-local manifests | 161 |
| Numerical/metrics tables | 105 |
| Static figures | 102 |
| Compact GIF animations | 38 |
| Representative WAV files | 20 |
| Animation-capable producer scripts | 29 |

The manifest IDs match the 136 `implemented` inventory rows exactly, with zero
duplicates and zero missing entries. Every manifest records the appendix
filename and SHA-256, repository start/result commit, parameters and parameter
hash, seed, numerical tolerances, residual vector, closure status, generated
files, regeneration command, approximation metadata, and the claim boundary:

```text
finite computational support; not a formal proof substitute
```

## Retention policy

Large frame dumps, videos, and regenerable datasets remain outside Git. The
repository tracks the aggregate `docs/data/artifact_provenance_manifest.json`,
generator code, compact status data, and selected producer-local figures,
tables, manifests, audio samples, and GIF evidence. The original three
aggregate theorem representatives remain:

- `docs/figures/qenn_spatial_closure.png`
- `docs/figures/pgqenn_prime_graph.png`
- `docs/figures/soinets_spatial_closure.png`

The aggregate manifest uses `<output-root>` placeholders, so regeneration
commands are portable and do not expose a workstation path.

## Colocated AI capability evidence

The six observable AI output groups add a separate, bounded evidence layer:

| Artifact class | Count |
| --- | ---: |
| Standalone capability manifests | 12 |
| Standalone capability result tables | 12 |
| Standalone capability static figures | 12 |
| Standalone compact animations | 6 |
| Architecture/mode suites | 6 |
| Architecture capability executions | 36 |

Unlike the theorem-level regeneration suites, these compact outputs are kept
beside their `test/` or `simulation/` producer to enforce the repository's
subject-local organization standard. Every capability manifest records the AI
appendix checksum, related theorem-complex IDs, parameters, tolerances,
residuals, closure status, generated files, regeneration command, source
status, and claim boundary. Details are in
`docs/tne_ai_output_capabilities.md`.

The producer-local aggregate also includes the six requested theorem modules,
DTQC's five regenerated static views plus phase-clock animation, and Hawking
benchmark evidence beneath `black_hole_dynamics/hawking`.

## Validation

`python -m tools.qa_guards` requires exactly one aggregate manifest per
implemented complex, the canonical claim boundary, 351 unique inventory IDs,
all implemented source dependencies, and zero tracked `.tex` files. Artifact
smoke tests separately validate each generator's files and schema.
