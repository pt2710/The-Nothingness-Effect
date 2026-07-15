"""Shared IO helpers for empirical-comparison artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from tne_runtime.artifacts.io import ensure_dir, save_csv, save_json


EMPIRICAL_CLAIM_BOUNDARY = (
    "fixture-backed comparison; empirical comparison pipeline; "
    "not an empirical validation claim; not a formal proof substitute"
)


def empirical_root() -> Path:
    return Path(__file__).resolve().parent


def fixtures_dir() -> Path:
    return empirical_root() / "fixtures"


def outputs_root(base: str | Path | None = None) -> Path:
    return Path(base) if base is not None else empirical_root() / "outputs"


def cache_root(base: str | Path | None = None) -> Path:
    root = outputs_root(base)
    return root.parent / "cache"


def ensure_output_tree(base: str | Path | None = None) -> dict[str, Path]:
    root = outputs_root(base)
    return {
        "root": ensure_dir(root),
        "data": ensure_dir(root / "data"),
        "metrics": ensure_dir(root / "metrics"),
        "figures": ensure_dir(root / "figures"),
        "reports": ensure_dir(root / "reports"),
        "manifests": ensure_dir(root / "manifests"),
    }


def ensure_cache_tree(base: str | Path | None = None) -> dict[str, Path]:
    root = cache_root(base)
    return {
        "root": ensure_dir(root),
        "raw": ensure_dir(root / "raw"),
        "text": ensure_dir(root / "text"),
    }


def fixture_path(filename: str) -> Path:
    return fixtures_dir() / filename


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_report(path: str | Path, text: str) -> Path:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    output_path.write_text(text, encoding="utf-8")
    return output_path


def write_manifest(path: str | Path, payload: dict[str, Any]) -> Path:
    return save_json(path, {"claim_boundary": EMPIRICAL_CLAIM_BOUNDARY, **payload})


def read_json(path: str | Path, default: Any | None = None) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return default
    return json.loads(file_path.read_text(encoding="utf-8"))


def write_text(path: str | Path, text: str) -> Path:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    output_path.write_text(text, encoding="utf-8")
    return output_path


def repo_relative(path: str | Path) -> str:
    target = Path(path)
    try:
        return target.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return target.as_posix()


def comparison_paths(slug: str, base: str | Path | None = None) -> dict[str, Path]:
    tree = ensure_output_tree(base)
    return {
        "data": tree["data"] / f"{slug}_comparison.csv",
        "metrics": tree["metrics"] / f"{slug}_metrics.csv",
        "figure": tree["figures"] / f"{slug}_comparison.png",
        "report": tree["reports"] / f"{slug}_report.md",
        "manifest": tree["manifests"] / f"{slug}_manifest.json",
    }


def residual_figure_path(slug: str, base: str | Path | None = None) -> Path:
    tree = ensure_output_tree(base)
    return tree["figures"] / f"{slug}_residuals.png"


def morphology_figure_path(slug: str, base: str | Path | None = None) -> Path:
    tree = ensure_output_tree(base)
    return tree["figures"] / f"{slug}_morphology_comparison.png"


def named_figure_path(slug: str, suffix: str, base: str | Path | None = None) -> Path:
    tree = ensure_output_tree(base)
    return tree["figures"] / f"{slug}_{suffix}.png"


def registry_output_path(base: str | Path | None = None) -> Path:
    return ensure_output_tree(base)["manifests"] / "source_registry.json"


def manifest_output_path(filename: str, base: str | Path | None = None) -> Path:
    return ensure_output_tree(base)["manifests"] / filename


def public_data_path(filename: str, base: str | Path | None = None) -> Path:
    return ensure_output_tree(base)["data"] / filename


def summary_paths(base: str | Path | None = None) -> dict[str, Path]:
    tree = ensure_output_tree(base)
    return {
        "metrics": tree["metrics"] / "empirical_comparison_summary.csv",
        "report": tree["reports"] / "empirical_comparison_summary.md",
        "manifest": tree["manifests"] / "empirical_comparison_metadata.json",
    }


def acquisition_summary_paths(base: str | Path | None = None) -> dict[str, Path]:
    tree = ensure_output_tree(base)
    return {
        "metrics": tree["metrics"] / "data_acquisition_summary.csv",
        "manifest": tree["manifests"] / "data_acquisition_summary.json",
    }


def audit_paths(base: str | Path | None = None) -> dict[str, Path]:
    tree = ensure_output_tree(base)
    return {
        "metrics": tree["metrics"] / "empirical_audit_run6.csv",
        "report": tree["reports"] / "empirical_audit_run6.md",
        "manifest": tree["manifests"] / "empirical_audit_run6.json",
    }


def save_rows(path: str | Path, rows: list[dict[str, Any]]) -> Path:
    return save_csv(path, rows)
