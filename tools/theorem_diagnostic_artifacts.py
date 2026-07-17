"""Materialize compact, deterministic theorem-complex diagnostic artifacts.

The plots produced here are diagnostics, not physical geometry or proof objects.  A
3-D or five-coordinate projection is emitted only to expose the numerical output,
residual and source-necessity structure of an evaluated contract.  Every figure is
labelled with that claim boundary.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import (
    ContractEvaluation,
)
from the_nothingness_effect._runtime.theorem_complex_runtime.types import (
    ComplexContract,
    SourceRemovalResult,
)


CLAIM_BOUNDARY = (
    "finite diagnostic projection; not a proof, physical embedding, or empirical validation"
)
_STATUS_CODE = {
    "satisfied": 1.0,
    "closed": 1.0,
    "numerical_candidate": 0.5,
    "open": 0.0,
    "blocked": -0.5,
    "singular": -1.0,
    "invalid_domain": -1.0,
    "invalid_codomain": -1.0,
}


def _safe(identifier: str) -> str:
    return identifier.replace("::", "__").replace(":", "_")


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return {
                "real": np.real(value).tolist(),
                "imag": np.imag(value).tolist(),
                "shape": list(value.shape),
            }
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if is_dataclass(value):
        return {item.name: _jsonable(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _numeric_vector(value: Any, *, limit: int = 4096) -> np.ndarray:
    collected: list[float] = []

    def visit(item: Any) -> None:
        if len(collected) >= limit:
            return
        if isinstance(item, Enum) or isinstance(item, (str, bytes, bool)) or item is None:
            return
        if isinstance(item, np.ndarray):
            array = np.asarray(item)
            if np.iscomplexobj(array):
                flat = np.concatenate((np.real(array).ravel(), np.imag(array).ravel()))
            else:
                flat = array.astype(float, copy=False).ravel()
            finite = flat[np.isfinite(flat)]
            collected.extend(float(number) for number in finite[: max(0, limit - len(collected))])
            return
        if isinstance(item, np.generic):
            visit(item.item())
            return
        if isinstance(item, (int, float)):
            number = float(item)
            if np.isfinite(number):
                collected.append(number)
            return
        if is_dataclass(item):
            for entry in fields(item):
                visit(getattr(item, entry.name))
            return
        if isinstance(item, dict):
            for key in sorted(item, key=str):
                visit(item[key])
            return
        if isinstance(item, (list, tuple)):
            for entry in item:
                visit(entry)

    visit(value)
    return np.asarray(collected, dtype=float)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _residual_vector(evaluation: ContractEvaluation) -> np.ndarray:
    if evaluation.residual is not None:
        return np.asarray(evaluation.residual.vector, dtype=float)
    if evaluation.invariant is not None:
        return np.asarray((evaluation.invariant.residual,), dtype=float)
    return np.zeros(1, dtype=float)


def materialize_contract_diagnostics(
    destination: Path,
    contract: ComplexContract,
    value: Any,
    evaluation: ContractEvaluation,
    removals: Iterable[SourceRemovalResult],
) -> tuple[str, ...]:
    """Write one compact evidence bundle and return generated relative names."""

    identifier = str(contract.complex_id)
    safe = _safe(identifier)
    destination.mkdir(parents=True, exist_ok=True)
    removal_items = list(removals)
    residual = _residual_vector(evaluation)
    output = _numeric_vector(evaluation.output)
    output_norm = float(np.linalg.norm(output)) if output.size else 0.0
    residual_norm = float(np.linalg.norm(residual))
    tolerance = (
        float(evaluation.residual.tolerance)
        if evaluation.residual is not None
        else float(evaluation.invariant.tolerance)
        if evaluation.invariant is not None
        else 0.0
    )

    status_path = destination / f"{safe}_status.json"
    status_payload = {
        "schema_version": "1.0",
        "theorem_complex_id": identifier,
        "appendix_filename": contract.appendix,
        "appendix_source_sha256": contract.appendix_source_sha256,
        "level": contract.level.value,
        "source_ids": [str(item) for item in contract.source_ids],
        "closure_status": evaluation.status.value,
        "exact_semantics": bool(evaluation.exact_semantics),
        "detail": evaluation.detail,
        "residual_norm": residual_norm,
        "tolerance": tolerance,
        "output_norm": output_norm,
        "claim_boundary": CLAIM_BOUNDARY,
        "input_summary": _jsonable(value),
        "output_summary": _jsonable(evaluation.output),
    }
    status_path.write_text(
        json.dumps(status_payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    residual_path = destination / f"{safe}_residual_vector.json"
    residual_path.write_text(
        json.dumps(
            {
                "theorem_complex_id": identifier,
                "values": residual.tolist(),
                "norm": residual_norm,
                "tolerance": tolerance,
                "passed": residual_norm <= tolerance if tolerance > 0.0 else residual_norm == 0.0,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    removal_rows = [
        {
            "theorem_complex_id": identifier,
            "source_id": str(item.source_id),
            "baseline_response": item.baseline_response,
            "removed_response": item.removed_response,
            "necessity_residual": item.necessity_residual,
            "necessary": item.necessary,
            "closure_status": evaluation.status.value,
        }
        for item in removal_items
    ]
    if not removal_rows:
        removal_rows = [
            {
                "theorem_complex_id": identifier,
                "source_id": "A_SOURCE_LAW",
                "baseline_response": output_norm,
                "removed_response": output_norm,
                "necessity_residual": 0.0,
                "necessary": True,
                "closure_status": evaluation.status.value,
            }
        ]
    removal_path = destination / f"{safe}_source_removal.csv"
    _write_csv(removal_path, removal_rows)

    metrics_rows = [
        {
            "theorem_complex_id": identifier,
            "probe": "baseline",
            "output_norm": output_norm,
            "residual_norm": residual_norm,
            "tolerance": tolerance,
            "necessity_residual": 0.0,
            "status_code": _STATUS_CODE.get(evaluation.status.value, -0.25),
            "exact_semantics": bool(evaluation.exact_semantics),
        }
    ]
    metrics_rows.extend(
        {
            "theorem_complex_id": identifier,
            "probe": f"remove:{item.source_id}",
            "output_norm": float(item.removed_response),
            "residual_norm": residual_norm,
            "tolerance": tolerance,
            "necessity_residual": float(item.necessity_residual),
            "status_code": _STATUS_CODE.get(evaluation.status.value, -0.25),
            "exact_semantics": bool(evaluation.exact_semantics),
        }
        for item in removal_items
    )
    metrics_path = destination / f"{safe}_metrics.csv"
    _write_csv(metrics_path, metrics_rows)

    trace_path = destination / f"{safe}_trace.npz"
    np.savez_compressed(
        trace_path,
        output_vector=output,
        residual_vector=residual,
        source_removal_residuals=np.asarray(
            [item.necessity_residual for item in removal_items], dtype=float
        ),
        source_removed_responses=np.asarray(
            [item.removed_response for item in removal_items], dtype=float
        ),
    )

    generated = [status_path, residual_path, removal_path, metrics_path, trace_path]

    plot_path = destination / f"{safe}_diagnostic_2d.png"
    figure, axis = plt.subplots(figsize=(9, 5))
    values = np.abs(residual) if residual.size else np.zeros(1)
    axis.bar(np.arange(values.size), values)
    if tolerance > 0.0:
        axis.axhline(tolerance, linestyle="--", label="declared tolerance")
        axis.legend()
    axis.set_yscale("log" if np.any(values > 0.0) and np.max(values) / max(np.min(values[values > 0.0]), 1e-300) > 100 else "linear")
    axis.set_xlabel("residual component")
    axis.set_ylabel("absolute residual")
    axis.set_title(f"{identifier}\nstatus={evaluation.status.value}; exact={evaluation.exact_semantics}")
    axis.text(0.01, 0.01, CLAIM_BOUNDARY, transform=axis.transAxes, fontsize=7)
    figure.tight_layout()
    figure.savefig(plot_path, dpi=140)
    plt.close(figure)
    generated.append(plot_path)

    if output.size >= 3:
        projection = output[: min(output.size, 256)]
        coordinate = np.arange(projection.size, dtype=float)
        gradient = np.abs(np.gradient(projection)) if projection.size >= 3 else np.zeros_like(projection)
        path_3d = destination / f"{safe}_diagnostic_3d.png"
        figure = plt.figure(figsize=(9, 6))
        axis = figure.add_subplot(111, projection="3d")
        axis.plot(coordinate, projection, gradient)
        axis.set_xlabel("component index")
        axis.set_ylabel("output value")
        axis.set_zlabel("absolute discrete gradient")
        axis.set_title(f"{identifier}\n3-D diagnostic projection; not physical geometry")
        figure.tight_layout()
        figure.savefig(path_3d, dpi=140)
        plt.close(figure)
        generated.append(path_3d)

    if len(metrics_rows) >= 2:
        columns = (
            "output_norm",
            "residual_norm",
            "tolerance",
            "necessity_residual",
            "status_code",
        )
        matrix = np.asarray(
            [[float(row[column]) for column in columns] for row in metrics_rows], dtype=float
        )
        minimum = np.min(matrix, axis=0)
        span = np.max(matrix, axis=0) - minimum
        span[span == 0.0] = 1.0
        normalized = (matrix - minimum) / span
        path_5d = destination / f"{safe}_diagnostic_5d_parallel.png"
        figure, axis = plt.subplots(figsize=(10, 5))
        for index, row in enumerate(normalized):
            axis.plot(np.arange(len(columns)), row, marker="o", label=metrics_rows[index]["probe"])
        axis.set_xticks(np.arange(len(columns)), columns, rotation=20, ha="right")
        axis.set_ylim(-0.05, 1.05)
        axis.set_ylabel("per-axis normalized value")
        axis.set_title(f"{identifier}\nfive-coordinate diagnostic projection")
        if len(metrics_rows) <= 8:
            axis.legend(fontsize=7)
        axis.text(0.01, 0.01, CLAIM_BOUNDARY, transform=axis.transAxes, fontsize=7)
        figure.tight_layout()
        figure.savefig(path_5d, dpi=140)
        plt.close(figure)
        generated.append(path_5d)

    checksum_path = destination / f"{safe}_checksums.json"
    checksum_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "theorem_complex_id": identifier,
                "files": {path.name: _sha256(path) for path in generated},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    generated.append(checksum_path)
    return tuple(path.name for path in generated)
