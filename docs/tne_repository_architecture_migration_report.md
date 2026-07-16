# TNE repository architecture migration report

Repository start commit: `b97a2da379ff9fc503c4c43185030674f887b85c`. Working branch: `codex/tne-architecture-and-theorem-complex-migration`. The canonical package now follows the seven appendix-aligned top-level architectures plus a private shared runtime.

All obsolete `framework`, `equations`, `tne_concepts`, root `figures`, and `figures_mccrackn` paths are absent. Artifacts are producer-local. The audit's 170-row file plan was reviewed row-by-row: 27 `reviewed_partial_alternative`, 9 `reviewed_present`, 130 `reviewed_relocated`, 4 `reviewed_removed_superseded`.

Theorem layout, import migration, tests/simulations, artifacts, open gaps, decision ledger, and final QA are documented in the companion `docs/tne_*` reports.
