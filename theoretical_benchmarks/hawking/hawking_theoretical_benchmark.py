"""Shared helpers for Hawking theoretical benchmark artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from equations.artifact_io import CLAIM_BOUNDARY, ensure_dir, save_figure, save_json
from theoretical_benchmarks.hawking.hawking_formulas import (
    hawking_evaporation_timescale,
    hawking_mass_loss_rate,
    hawking_power,
    hawking_temperature,
    normalized_planck_spectrum,
)


THEORETICAL_CLAIM_BOUNDARY = (
    "theoretical benchmark; repository-linked computational artifact; "
    "not an empirical validation claim; not a formal proof substitute"
)


def hawking_root() -> Path:
    return Path(__file__).resolve().parent


def simulation_dir() -> Path:
    return ensure_dir(hawking_root() / "simulation")


def comparison_dir() -> Path:
    return ensure_dir(hawking_root() / "comparison")


def summary_paths() -> dict[str, Path]:
    root = ensure_dir(hawking_root().parent)
    return {
        "csv": root / "benchmark_summary.csv",
        "md": root / "benchmark_summary.md",
        "json": root / "benchmark_summary_metadata.json",
    }


def save_rows(path: Path, rows: list[dict[str, Any]]) -> Path:
    ensure_dir(path.parent)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key, "")) for key in fieldnames})
    return path


def _csv_value(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        return "|".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    return value


def normalized(values: np.ndarray) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    maximum = float(np.max(np.abs(data))) + 1e-12
    return data / maximum


def loglog_slope(x: np.ndarray, y: np.ndarray) -> float:
    xx = np.asarray(x, dtype=float)
    yy = np.asarray(y, dtype=float)
    mask = (xx > 0.0) & (yy > 0.0) & np.isfinite(xx) & np.isfinite(yy)
    if np.count_nonzero(mask) < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log(xx[mask]), np.log(yy[mask]), deg=1)
    return float(slope)


def build_hawking_benchmark(mass_kg: np.ndarray | None = None) -> dict[str, Any]:
    mass_grid = np.asarray(mass_kg if mass_kg is not None else np.geomspace(1.0e11, 1.0e15, 48), dtype=float)
    temperature = hawking_temperature(mass_grid)
    power = hawking_power(mass_grid)
    mass_loss = hawking_mass_loss_rate(mass_grid)
    evaporation = hawking_evaporation_timescale(mass_grid)
    spectrum_x = np.linspace(0.1, 12.0, 240)
    spectrum = normalized_planck_spectrum(spectrum_x)
    return {
        "mass_kg": mass_grid,
        "temperature_K": temperature,
        "power_W": power,
        "mass_loss_rate_kg_per_s": mass_loss,
        "evaporation_time_s": evaporation,
        "temperature_normalized": normalized(temperature),
        "power_normalized": normalized(power),
        "evaporation_normalized": normalized(evaporation),
        "spectrum_x": spectrum_x,
        "spectrum_normalized": spectrum,
        "slope_temperature": loglog_slope(mass_grid, temperature),
        "slope_power": loglog_slope(mass_grid, power),
        "slope_evaporation": loglog_slope(mass_grid, evaporation),
    }


def write_benchmark_summary(rows: list[dict[str, Any]], note: str) -> dict[str, Path]:
    paths = summary_paths()
    save_rows(paths["csv"], rows)
    lines = [
        "# Theoretical Benchmark Summary",
        "",
        "These files are finite theoretical benchmark artifacts for repository-linked comparison work. They are not empirical validation and do not replace mathematical proofs.",
        "",
        f"Note: {note}",
        "",
        "Rows:",
    ]
    for row in rows:
        lines.append(
            f"- {row['benchmark_name']}: data_status={row['data_status']}, "
            f"RMSE={row['RMSE']:.6f}, slope_temperature={row['slope_temperature']:.6f}, "
            f"slope_power={row['slope_power']:.6f}"
        )
    paths["md"].write_text("\n".join(lines), encoding="utf-8")
    save_json(
        paths["json"],
        {
            "claim_boundary": THEORETICAL_CLAIM_BOUNDARY,
            "rows": rows,
            "note": note,
        },
    )
    return paths


def write_hawking_benchmark_outputs(benchmark: dict[str, Any]) -> dict[str, Path]:
    root = simulation_dir()
    csv_path = root / "hawking_theoretical_benchmark_data.csv"
    metrics_path = root / "hawking_theoretical_benchmark_metrics.csv"
    metadata_path = root / "hawking_theoretical_benchmark_metadata.json"
    rows = []
    for idx, mass_value in enumerate(benchmark["mass_kg"]):
        rows.append(
            {
                "mass_kg": float(mass_value),
                "temperature_K": float(benchmark["temperature_K"][idx]),
                "power_W": float(benchmark["power_W"][idx]),
                "mass_loss_rate_kg_per_s": float(benchmark["mass_loss_rate_kg_per_s"][idx]),
                "evaporation_time_s": float(benchmark["evaporation_time_s"][idx]),
                "temperature_normalized": float(benchmark["temperature_normalized"][idx]),
                "power_normalized": float(benchmark["power_normalized"][idx]),
                "evaporation_normalized": float(benchmark["evaporation_normalized"][idx]),
            }
        )
    save_rows(csv_path, rows)
    save_rows(
        metrics_path,
        [
            {
                "benchmark_name": "hawking_theoretical_benchmark",
                "data_status": "theoretical_benchmark",
                "slope_temperature": benchmark["slope_temperature"],
                "slope_power": benchmark["slope_power"],
                "slope_evaporation": benchmark["slope_evaporation"],
                "temperature_slope_error": benchmark["slope_temperature"] + 1.0,
                "power_slope_error": benchmark["slope_power"] + 2.0,
                "evaporation_slope_error": benchmark["slope_evaporation"] - 3.0,
                "passed_benchmark_checks": bool(
                    np.isclose(benchmark["slope_temperature"], -1.0, atol=1e-9)
                    and np.isclose(benchmark["slope_power"], -2.0, atol=1e-9)
                    and np.isclose(benchmark["slope_evaporation"], 3.0, atol=1e-9)
                ),
            }
        ],
    )
    save_json(
        metadata_path,
        {
            "claim_boundary": THEORETICAL_CLAIM_BOUNDARY,
            "mass_range_kg": [float(np.min(benchmark["mass_kg"])), float(np.max(benchmark["mass_kg"]))],
            "slope_temperature": benchmark["slope_temperature"],
            "slope_power": benchmark["slope_power"],
            "slope_evaporation": benchmark["slope_evaporation"],
            "limitations": "Analytic Hawking benchmark only; not an empirical validation layer.",
        },
    )

    paths = {
        "data": csv_path,
        "metrics": metrics_path,
        "metadata": metadata_path,
    }
    figure_specs = [
        ("temperature_K", "hawking_temperature_vs_mass.png", "Hawking temperature vs mass", "temperature (K)", True),
        ("power_W", "hawking_power_vs_mass.png", "Hawking power vs mass", "power (W)", True),
        ("evaporation_time_s", "hawking_evaporation_timescale_vs_mass.png", "Hawking evaporation timescale vs mass", "time (s)", True),
    ]
    for key, filename, title, ylabel, log_axes in figure_specs:
        fig, ax = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
        ax.plot(benchmark["mass_kg"], benchmark[key], color="#d62728", linewidth=2.0)
        if log_axes:
            ax.set_xscale("log")
            ax.set_yscale("log")
        ax.set_title(f"{title} (theoretical benchmark)")
        ax.set_xlabel("mass (kg)")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25, which="both")
        paths[key] = save_figure(fig, root / filename, dpi=220)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
    ax.plot(benchmark["spectrum_x"], benchmark["spectrum_normalized"], color="#1f77b4", linewidth=2.0)
    ax.set_title("Normalized Hawking spectrum benchmark")
    ax.set_xlabel("dimensionless frequency")
    ax.set_ylabel("normalized spectral weight")
    ax.grid(True, alpha=0.25)
    paths["spectrum"] = save_figure(fig, root / "hawking_normalized_spectrum.png", dpi=220)
    plt.close(fig)
    return paths
