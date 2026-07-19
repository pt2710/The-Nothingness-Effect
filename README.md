# The Nothingness Effect

This repository contains the typed computational runtime for The Nothingness Effect (TNE).

The verified source package contains nine mathematical appendix files plus `TNE_APPENDIX_CANONICAL_INPUT_ORDER.tex`. Exact filenames and hashes are recorded in `docs/data/authoritative_archive_manifest.json`.

The verified inventory contains 351 theorem complexes: 204 A source laws, 98 B derivations, and 49 C spatial closures. All 351 are runtime implemented and bound to the current source hashes. Runtime implementation, mathematical closure, formal proof, numerical evidence, and empirical validation are tracked separately.

## Validation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
python -m tools.qa_guards
```

The implementation matrix is `docs/data/theorem_complex_implementation_matrix.csv`. Aggregate artifact provenance is generated at `docs/data/artifact_provenance_manifest.json`.

A passing numerical test or simulation is not automatically a formal proof. An `open` or `numerical_candidate` status remains visible until its declared mathematical closure obligations are established.
