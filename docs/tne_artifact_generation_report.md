# TNE artifact generation report

Deterministic seed 0 generated 351 theorem manifests, 441 tables, and 353 static figures. Every theorem complex has a fresh JSON/CSV/NPZ/PNG core bundle. Producer-local outputs include 147 GIFs and 20 audio files.

Regenerate the theorem evidence outside Git with `python tools/generate_complete_theorem_artifacts.py --output-root <external-output-root> --aggregate docs/data/artifact_provenance_manifest.json --coverage reports/theorem_artifact_coverage.json`. Producer-local AI and subject outputs are regenerated through the entrypoint runner; aggregate animations are regenerated with `python -m tools.run_animation_artifacts --quick`.
