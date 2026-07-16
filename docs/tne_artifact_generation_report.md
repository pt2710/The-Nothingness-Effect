# TNE artifact generation report

Deterministic seed 0 generated 173 theorem manifests, 229 tables, and 221 static figures from a clean external evidence root. Producer-local outputs include 186 manifests, 49 tracked GIFs, and 20 audio files.

Regenerate the theorem evidence outside Git with `python tools/generate_artifact_provenance.py --output-root <external-output-root> --aggregate docs/data/artifact_provenance_manifest.json --representative-dir docs/figures`. Producer-local AI and subject outputs are regenerated through the entrypoint runner.
