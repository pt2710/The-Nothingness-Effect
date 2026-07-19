# The Nothingness Effect

This repository contains the typed computational runtime for The Nothingness Effect (TNE).

The verified source package contains nine mathematical appendix files plus `TNE_APPENDIX_CANONICAL_INPUT_ORDER.tex`. Exact filenames and hashes are recorded in `docs/data/authoritative_archive_manifest.json`.

The verified inventory contains 351 theorem complexes: 204 A source laws, 98 B derivations, and 49 C spatial closures. All 351 are runtime implemented and bound to the current source hashes. The regenerated closure ledger reports 302 `satisfied`, 49 `closed`, 0 `open`, and 0 `numerical_candidate`. Runtime implementation, mathematical closure, formal proof, numerical evidence, and empirical validation are tracked separately.

Formal machine-proof coverage is audited independently. The current inventory has 351/351 rows classified, 0 invalid proof claims, and 0 proof-assistant kernel certificates. The repository therefore makes no claim that its 351 executable theorem-complex certificates are formal machine proofs.

## Validation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
python -m tools.qa_guards
python -m tools.build_closure_obligation_ledger --require-zero
python -m tools.build_formal_proof_coverage
```

The implementation matrix is `docs/data/theorem_complex_implementation_matrix.csv`. Aggregate artifact provenance is generated at `docs/data/artifact_provenance_manifest.json`.

A passing numerical test or simulation is not automatically a formal proof. CI fails if an `open` or `numerical_candidate` status reappears, or if a formal-proof claim lacks a verifiable kernel certificate and assumptions hash.
