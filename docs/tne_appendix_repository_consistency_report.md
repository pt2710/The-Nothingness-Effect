# TNE appendix–repository consistency report

## Baseline record

- Repository: `https://github.com/pt2710/The-Nothingness-Effect.git`
- Default branch: `main`
- Start commit: `b97a2da379ff9fc503c4c43185030674f887b85c`
- Work branch: `codex/tne-appendix-consistency`
- Python: `3.14.3` (matches `.python-version`)
- Dependency check: `python -m pip check` reported no broken requirements
- Optional environment note: `uv` is not installed; both Python 3.14 and 3.11 are available

The initial clone used the repository display name as its directory. Because that
name contains hyphens, pytest imported the root `__init__.py` without package
context and produced 162 setup errors. No source file had been changed. The
untouched checkout was moved to the valid local package path
`repo/the_nothingness_effect`, after which the full baseline completed with:

```text
162 passed, 0 failed, 0 skipped, 7 warnings in 257.90s
```

The seven warnings are pre-existing `PytestReturnNotNoneWarning` instances.
Runtime measured around the command was 260.957 seconds.

## External reference security

The audit bundle and appendix bundle were extracted outside the repository Git
root. The audit checksum manifest validated all seven files it describes. The
appendix ZIP digest is
`8960c2cee5aacbe97e6f0975515d5b842b7d87be56036e75270d1efd4f11d2df`,
which equals the digest recorded by the audit. The seven authoritative appendix
file digests and theorem-label verification results are recorded as metadata in
`docs/data/source_law_registry.json` and
`docs/data/appendix_source_verification.json`; no LaTeX source text is stored in
the repository.

## Inventory verification

The audit matrix contains 351 rows: 204 A, 98 B, and 49 C. Every row's
`first_label` and every declared equation label was found in the corresponding
authoritative external appendix. The audit contained four colliding slug IDs.
The repository registry disambiguates every member of those collisions with a
module prefix and retains the original slug in `source_complex_id`. The resulting
registry has 351 unique IDs and zero duplicates.

Initial strict implementation status remains honest: 277 complexes are
`proxy_only`, 74 are `not_implemented`, and zero are yet certified as exact
theorem-contract implementations. Status changes require a typed operator,
invariant/residual, required source-removal tests, simulation evidence, and a
provenance manifest.

## Checkpoint status

The Flowpoint, mathematical-closure, foundational-duality, DFI, pDFI,
Elastic-π, Elastic-π Norm, selected physical-dynamics, and completeness
checkpoints plus source-complete QENN, PGQENN, and SOInet chains certify 136
theorem complexes: 78 A, 39 B, and 19 C. The remaining matrix contains 180
`proxy_only` and 35
`not_implemented` records. Every
upgraded B contract has all-source removal
tests, and every upgraded C contract has an explicit spatial/local operator,
boundary or leakage diagnostics, all-B-source ablations, and a
`numerical_candidate` distinction where finite computation does not establish
mathematical attainment.

The canonical DFI and Elastic-π source paths are now fail closed. DFI returns a
typed singular witness instead of neutralized non-finite values. Elastic-π
underflow/overflow is explicit, and optional exponent clipping preserves both
the exact and evaluated exponents in approximation metadata.

The physical checkpoint implements bounded 4A→2B→1C chains for Elastic Dubler
Effect, Elastic Dubler Interferometry, Locality-Driven Gravity, Black-Hole
Dynamics, Elastic-π Ripples, Cosmological Spark Dynamics, and Discrete-Time
Quasicrystals. Legacy simulators remain proxy evidence for every non-upgraded
row and are not presented as complete theorem implementations.

All 15 completeness-theorem records are typed, but finite dual-closure traces,
fixed points, certificate gluing, and terminal quotients retain the explicit
boundary that they are computational support rather than formal proof.

The QENN checkpoint adds an optional CPU PyTorch backend and certifies a bounded
4A→2B→1C chain. Its B-level residual energies are genuine positive couplings of
both A sources, and its C-level output is a single boundary-sensitive defect
field. The remaining QENN rows stay explicitly at proxy status.

The PGQENN checkpoint adds a deterministic prime/parity/2-adic growth law,
Flowpoint-equivariant message passing, pDFI conditioning, and exact Elastic-π
edge gains. Legacy random sampling is retained only as a seeded comparison
ablation. Its bounded 4A→2B→1C chain has all-source ablations and an explicit
graph-local numerical-candidate boundary; all other PGQENN rows remain proxy.

The SOInet checkpoint composes multiple canonical QENN/PGQENN subnetworks with
bidirectional memory, observation aggregation, spectral/spatial meta-residuals,
and fail-closed arbitration. Appendix verification corrected the bounded source
selection to B19=A01+A13 and B20=A02+A14; C29 consumes those two complete B
laws. The older duplicated `tne_concepts/SOInet` stack is compatibility-only.
