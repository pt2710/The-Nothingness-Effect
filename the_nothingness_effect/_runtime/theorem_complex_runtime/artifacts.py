"""Artifact writes with mandatory theorem-level provenance."""

from __future__ import annotations

import json
from pathlib import Path

from .types import ArtifactManifest


def write_artifact_manifest(path: str | Path, manifest: ArtifactManifest) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = manifest.to_dict()
    repository_root = Path(__file__).resolve().parents[3]
    command = str(payload["regeneration_command"])
    for prefix in (str(repository_root), repository_root.as_posix()):
        command = command.replace(prefix + "\\", "").replace(prefix + "/", "")
    payload["regeneration_command"] = command.replace("\\", "/")
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output
