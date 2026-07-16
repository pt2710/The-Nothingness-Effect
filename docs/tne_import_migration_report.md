# TNE import migration report

Canonical imports use the `the_nothingness_effect` package and remain independent of the checkout directory name. Cross-cutting runtime code is under `the_nothingness_effect._runtime`; domain artifact code is owned by its subject package.

The layout verifier confirms all implementation modules import from the repository root and a foreign working directory. Removed roots `equations` and `tne_concepts` are not import authorities. Compatibility wrappers are retained only where explicitly documented.
