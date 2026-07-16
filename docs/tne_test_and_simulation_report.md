# TNE test and simulation report

Full pytest gate: **805 passed**, **0 failed**, **0 skipped**, **8 warnings** in **483.64 seconds**.

Producer entrypoints: test 37/37 passed; simulation 37/37 passed. Nine focused AI artifact producers were also regenerated after the implementation checkpoint, including both multimodal SOInet producers and the PGQENN contract suite. Legacy heavy renderers with canonical-name collisions are recorded as bounded contract-inventory fallbacks; typed contract/evidence suites are preferred when present.

Commands: `python -m pytest -q`, `python tools/run_repository_entrypoints.py test`, `python tools/run_repository_entrypoints.py simulation`, and `python tools/verify_tne_repository_layout.py`.
