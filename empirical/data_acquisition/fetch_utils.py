"""Small utilities for public empirical data acquisition."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import urllib.request

from empirical.io import (
    ensure_cache_tree,
    fixture_path,
    manifest_output_path,
    public_data_path,
    repo_relative,
    write_manifest,
    write_text,
)


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Codex empirical acquisition; +https://github.com/pt2710/The-Nothingness-Effect)"
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def http_get_bytes(url: str, *, timeout: int = 30) -> bytes:
    request = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def http_get_text(url: str, *, timeout: int = 30, encoding: str = "utf-8") -> str:
    return http_get_bytes(url, timeout=timeout).decode(encoding, errors="replace")


def download_to_cache(
    url: str,
    destination: str | Path,
    *,
    timeout: int = 60,
    force: bool = False,
) -> Path:
    output_path = Path(destination)
    if output_path.exists() and not force:
        return output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=DEFAULT_HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        output_path.write_bytes(response.read())
    return output_path


def cache_raw_path(dataset_slug: str, filename: str, output_dir: str | None = None) -> Path:
    return ensure_cache_tree(output_dir)["raw"] / dataset_slug / filename


def cache_text_path(dataset_slug: str, filename: str, output_dir: str | None = None) -> Path:
    return ensure_cache_tree(output_dir)["text"] / dataset_slug / filename


def write_cached_text(
    dataset_slug: str,
    filename: str,
    text: str,
    output_dir: str | None = None,
) -> Path:
    return write_text(cache_text_path(dataset_slug, filename, output_dir), text)


def derived_output_path(filename: str, output_dir: str | None = None) -> Path:
    return public_data_path(filename, output_dir)


def dataset_manifest_output_path(filename: str, output_dir: str | None = None) -> Path:
    return manifest_output_path(filename, output_dir)


def provenance_manifest(
    *,
    dataset_name: str,
    source_name: str,
    source_url: str,
    script_name: str,
    status: str,
    output_dir: str | None = None,
    raw_file_path: str | Path | None = None,
    derived_file_path: str | Path | None = None,
    access_method: str = "public_fetch_or_curated",
    expected_file_type: str = "csv",
    license_note: str = "",
    citation_note: str = "",
    preprocessing_steps: list[str] | None = None,
    limitations: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "dataset_name": dataset_name,
        "source_name": source_name,
        "source_url": source_url,
        "access_date": utc_now_iso(),
        "license_note": license_note,
        "citation_note": citation_note,
        "script_used": script_name,
        "raw_file_path": repo_relative(raw_file_path) if raw_file_path else "",
        "derived_file_path": repo_relative(derived_file_path) if derived_file_path else "",
        "fixture_fallback_path": repo_relative(fixture_path(_fixture_filename_for(dataset_name))),
        "preprocessing_steps": preprocessing_steps or [],
        "status": status,
        "access_method": access_method,
        "expected_file_type": expected_file_type,
        "limitations": limitations,
    }
    if extra:
        payload.update(extra)
    return payload


def write_dataset_manifest(filename: str, payload: dict[str, Any], output_dir: str | None = None) -> Path:
    return write_manifest(dataset_manifest_output_path(filename, output_dir), payload)


def _fixture_filename_for(dataset_name: str) -> str:
    fixtures = {
        "redshift_clock": "redshift_clock_fixture.csv",
        "galaxy_rotation": "galaxy_rotation_fixture.csv",
        "eht_observables": "eht_observable_fixture.csv",
        "hawking_analogue_or_limits": "hawking_flux_fixture.csv",
        "ligo_waveforms": "ligo_ringdown_fixture.csv",
        "ligo_ringdown": "ligo_ringdown_fixture.csv",
    }
    return fixtures[dataset_name]
