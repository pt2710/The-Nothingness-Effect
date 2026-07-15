# TNE open implementation gaps

## Current boundary

Of 351 verified theorem complexes, 136 are `implemented`, 180 remain
`proxy_only`, and 35 are `not_implemented`. Proxy status means related legacy
code exists but the complete source laws, required residuals, source-removal
tests, closure obligations, or provenance are not yet certified.

| Module/family | Total | Implemented | Proxy | Not implemented |
| --- | ---: | ---: | ---: | ---: |
| Foundational closure appendix | 79 | 6 | 65 | 8 |
| Gravitational/cosmological/quantum appendix | 136 | 49 | 60 | 27 |
| AI appendix | 71 | 21 | 50 | 0 |
| Fluctuation/elastic appendix | 36 | 31 | 5 | 0 |

The 35 absent canonical implementations are concentrated in:

- DTQC: 18;
- Elastic Dubler Interferometry: 8;
- foundational Flowpoint spatiality/symmetry/closure interfaces: 8;
- Cosmological Spark Dynamics: 1.

The largest proxy-only families are foundational symmetry, spatiality,
countable/uncountable infinity, Spectrum of Infinities, observation/collapse,
unselected physical derivations, and the remaining 50 AI complexes.

## Next safe implementation order

1. Complete the foundational symmetry, spatiality, infinity, SOI, and
   observation/collapse A laws before deriving their B/C families.
2. Expand physical modules only in source-complete 4A→2B→1C slices, preserving
   toy solvers as numerical backends rather than source laws.
3. Complete the remaining AI A dependencies before adding B residual energies
   and C spatial fields; do not infer contracts from neural finiteness.
4. Add property/refinement tests for every new coercivity, attainment,
   observability, reconstruction, and boundary obligation.

Every individual open row, proposed file, required test, artifact, and decision
note is preserved in `docs/data/theorem_complex_implementation_matrix.csv`.
The audit's 170-row repository file plan is separately recorded in
`docs/data/repository_file_revision_status.csv`: 42 exact planned paths are
present, 58 responsibilities are relocated or partially addressed through
conservative alternative paths, and 70 remain explicitly open.
