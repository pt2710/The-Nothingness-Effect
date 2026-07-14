# TNE consistency revision decision ledger

| ID | Decision | Evidence and consequence |
| --- | --- | --- |
| D-001 | Keep all nine uploaded appendix LaTeX files outside every repository Git root; only the specified seven participate in the 351-complex inventory. | External sources are read only. Repository outputs contain filenames, theorem IDs, labels, checksums, and bounded status metadata only. |
| D-002 | Use a Python-identifier-safe local checkout directory. | A hyphenated clone directory caused 162 setup errors before any source edit; the same commit passed 162 tests after relocation. Root import handling is also made checkout-name independent for CI. |
| D-003 | Disambiguate the audit's four duplicate slug IDs with module prefixes. | The audit has 351 rows but only 347 unique slugs. Both colliding records receive `module::source_slug`; the original audit value remains in `source_complex_id`. |
| D-004 | Treat finite residual reduction as evidence, never as proof by itself. | Runtime statuses distinguish `numerical_candidate`, `closed`, `open`, `blocked`, and `singular`; clipping is approximation metadata. |
| D-005 | Keep legacy/proxy coverage visible until every contract gate is present. | Existing related code maps to `proxy_only`; a file's existence alone does not upgrade a theorem-complex status. |
