# TNE artifact generation report

Deterministic seed 0 generated 173 theorem manifests, 277 tables, and 333 static figures. Producer-local outputs include 137 GIFs and 20 audio files.

Regenerate the theorem evidence outside Git with `python tools/generate_artifact_provenance.py --output-root <external-output-root> --aggregate docs/data/artifact_provenance_manifest.json --representative-dir docs/figures`. Producer-local AI and subject outputs are regenerated through the entrypoint runner.
