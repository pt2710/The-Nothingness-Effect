"""Small output helpers for deterministic repository-linked artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np


CLAIM_BOUNDARY = (
    "finite illustrative simulation; repository-linked computational artifact; "
    "not a formal proof substitute"
)


def ensure_dir(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_json(path: str | Path, data: dict[str, Any]) -> Path:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    output_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return output_path


def save_csv(path: str | Path, rows: Iterable[dict[str, Any]]) -> Path:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    rows = list(rows)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key, "")) for key in fieldnames})
    return output_path


def save_npz(path: str | Path, **arrays: Any) -> Path:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    np.savez_compressed(output_path, **arrays)
    return output_path


def save_figure(fig: Any, path: str | Path, dpi: int = 300) -> Path:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    return output_path


def write_metadata(path: str | Path, metadata: dict[str, Any]) -> Path:
    payload = {
        "claim_boundary": CLAIM_BOUNDARY,
        **metadata,
    }
    return save_json(path, payload)


def _csv_value(value: Any) -> Any:
    if isinstance(value, (list, tuple, set)):
        return "|".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return value
