"""Artifact writes with mandatory theorem-level provenance."""

from __future__ import annotations

import json
from pathlib import Path

from .types import ArtifactManifest


def write_artifact_manifest(path: str | Path, manifest: ArtifactManifest) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output
