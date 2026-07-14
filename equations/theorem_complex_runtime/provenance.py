"""Deterministic provenance-manifest construction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping

from .types import ArtifactManifest, SimulationResult


def parameter_hash(parameters: Mapping[str, Any]) -> str:
    payload = json.dumps(parameters, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def git_commit(repository: str | Path = ".") -> str:
    completed = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def build_manifest(
    result: SimulationResult,
    *,
    appendix_filename: str,
    appendix_source_sha256: str,
    repository_start_commit: str,
    repository_result_commit: str,
    regeneration_command: str,
) -> ArtifactManifest:
    return ArtifactManifest(
        theorem_complex_id=str(result.complex_id),
        appendix_filename=appendix_filename,
        appendix_source_sha256=appendix_source_sha256,
        repository_start_commit=repository_start_commit,
        repository_result_commit=repository_result_commit,
        parameters=result.parameters,
        parameter_hash=parameter_hash(result.parameters),
        seed=result.seed,
        numeric_tolerances=result.numeric_tolerances,
        residual_vector=result.residual_vector,
        closure_status=result.closure_status.value,
        generated_files=result.generated_files,
        regeneration_command=regeneration_command,
        approximation_metadata=result.approximation_metadata,
    )
