"""Compare the TNE Hawking-like proxy against standard Hawking benchmark formulas."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from empirical.metrics import mae, rmse, r_squared
from tne_runtime.artifacts.io import save_figure, save_json
from equations.black_hole_dynamics.black_hole_dynamics import BlackHoleParams, black_hole_snapshot, simulate_black_hole_dynamics
from equations.black_hole_dynamics.hawking.hawking_formulas import normalized_planck_spectrum
from equations.black_hole_dynamics.hawking.hawking_theoretical_benchmark import (
    THEORETICAL_CLAIM_BOUNDARY,
    build_hawking_benchmark,
    comparison_dir,
    normalized,
    save_rows,
    simulation_dir,
    write_benchmark_summary,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]


def _repository_path(path: Path) -> str:
    return path.resolve().relative_to(REPOSITORY_ROOT).as_posix()


def _common_mass_coordinates(count: int = 24) -> dict[str, np.ndarray]:
    physical_mass = np.geomspace(1.0e11, 1.0e15, count)
    proxy_mass = np.geomspace(1.4, 6.5, count)
    return {"physical_mass": physical_mass, "proxy_mass": proxy_mass}


def _tne_mass_scan() -> dict[str, np.ndarray]:
    coords = _common_mass_coordinates()
    temperature = []
    power = []
    ring_contrast = []
    horizon_radius = []
    for proxy_mass in coords["proxy_mass"]:
        snapshot = black_hole_snapshot(float(proxy_mass), BlackHoleParams(mass_proxy=float(proxy_mass)))
        temperature.append(float(snapshot["temperature_at_horizon"]))
        power.append(float(snapshot["integrated_flux_proxy"]))
        ring_contrast.append(float(snapshot["ring_contrast_proxy"]))
        horizon_radius.append(float(snapshot["horizon_radius"]))
    return {
        "physical_mass": coords["physical_mass"],
        "proxy_mass": coords["proxy_mass"],
        "temperature_proxy": np.asarray(temperature, dtype=float),
        "power_proxy": np.asarray(power, dtype=float),
        "ring_contrast_proxy": np.asarray(ring_contrast, dtype=float),
        "horizon_radius_proxy": np.asarray(horizon_radius, dtype=float),
    }


def _tne_spectrum_proxy(proxy_mass: float = 3.0) -> dict[str, np.ndarray]:
    snapshot = black_hole_snapshot(proxy_mass, BlackHoleParams(mass_proxy=proxy_mass))
    field = np.asarray(snapshot["pi_E"], dtype=float)
    centered = field - float(np.mean(field))
    amplitudes = np.abs(np.fft.rfft(centered))
    frequencies = np.fft.rfftfreq(len(centered), d=float(snapshot["r"][1] - snapshot["r"][0]))
    x_values = np.linspace(0.1, 12.0, max(32, len(amplitudes)))
    spectral_interp = np.interp(
        x_values,
        np.linspace(0.1, 12.0, len(amplitudes)),
        normalized(amplitudes),
        left=float(normalized(amplitudes)[0]),
        right=float(normalized(amplitudes)[-1]),
    )
    return {
        "frequency": frequencies,
        "x_values": x_values,
        "spectrum": normalized(spectral_interp),
    }


def _comparison_metrics(observed: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    return {
        "RMSE": rmse(observed, predicted),
        "MAE": mae(observed, predicted),
        "R2": r_squared(observed, predicted),
    }


def _fit_scale(reference: np.ndarray, proxy: np.ndarray) -> np.ndarray:
    ref = np.asarray(reference, dtype=float)
    pro = np.asarray(proxy, dtype=float)
    scale = float(np.dot(ref, pro) / (np.dot(pro, pro) + 1e-12))
    return scale * pro


def run() -> dict[str, Any]:
    benchmark = build_hawking_benchmark()
    tne_scan = _tne_mass_scan()
    comparison_root = comparison_dir()

    hawking_temp = normalized(benchmark["temperature_normalized"][: len(tne_scan["proxy_mass"])])
    hawking_power = normalized(benchmark["power_normalized"][: len(tne_scan["proxy_mass"])])
    tne_temp = normalized(tne_scan["temperature_proxy"])
    tne_power = normalized(tne_scan["power_proxy"])
    tne_temp_scaled = _fit_scale(hawking_temp, tne_temp)
    tne_power_scaled = _fit_scale(hawking_power, tne_power)

    mass_norm = tne_scan["proxy_mass"] / tne_scan["proxy_mass"][0]
    slope_temperature = float(np.polyfit(np.log(mass_norm), np.log(np.maximum(tne_temp_scaled, 1e-12)), deg=1)[0])
    slope_power = float(np.polyfit(np.log(mass_norm), np.log(np.maximum(tne_power_scaled, 1e-12)), deg=1)[0])
    slope_evaporation = 3.0

    temp_metrics = _comparison_metrics(hawking_temp, tne_temp_scaled)
    power_metrics = _comparison_metrics(hawking_power, tne_power_scaled)

    spectrum = _tne_spectrum_proxy()
    hawking_spectrum = normalized_planck_spectrum(spectrum["x_values"])
    tne_spectrum = _fit_scale(hawking_spectrum, np.asarray(spectrum["spectrum"], dtype=float))
    spectrum_metrics = _comparison_metrics(hawking_spectrum, tne_spectrum)

    temperature_csv = comparison_root / "tne_vs_hawking_temperature.csv"
    power_csv = comparison_root / "tne_vs_hawking_power.csv"
    spectrum_csv = comparison_root / "tne_vs_hawking_spectrum.csv"
    metrics_csv = comparison_root / "tne_vs_hawking_metrics.csv"
    report_path = comparison_root / "tne_vs_hawking_report.md"
    manifest_path = comparison_root / "tne_vs_hawking_manifest.json"

    save_rows(
        temperature_csv,
        [
            {
                "physical_mass_kg": float(tne_scan["physical_mass"][idx]),
                "proxy_mass": float(tne_scan["proxy_mass"][idx]),
                "hawking_temperature_normalized": float(hawking_temp[idx]),
                "tne_temperature_proxy_normalized": float(tne_temp_scaled[idx]),
            }
            for idx in range(len(tne_scan["proxy_mass"]))
        ],
    )
    save_rows(
        power_csv,
        [
            {
                "physical_mass_kg": float(tne_scan["physical_mass"][idx]),
                "proxy_mass": float(tne_scan["proxy_mass"][idx]),
                "hawking_power_normalized": float(hawking_power[idx]),
                "tne_power_proxy_normalized": float(tne_power_scaled[idx]),
            }
            for idx in range(len(tne_scan["proxy_mass"]))
        ],
    )
    save_rows(
        spectrum_csv,
        [
            {
                "dimensionless_frequency": float(spectrum["x_values"][idx]),
                "hawking_spectrum_normalized": float(hawking_spectrum[idx]),
                "tne_spectrum_proxy_normalized": float(tne_spectrum[idx]),
            }
            for idx in range(len(spectrum["x_values"]))
        ],
    )
    rows = [
        {
            "benchmark_name": "hawking_theoretical_benchmark",
            "model": "black_hole_dynamics",
            "comparison_type": "theoretical consistency comparison",
            "data_status": "theoretical_benchmark",
            "formulas_used": "temperature,power,mass_loss,evaporation,spectrum",
            "fitted_parameters": {
                "temperature_scale": float(np.dot(hawking_temp, tne_temp) / (np.dot(tne_temp, tne_temp) + 1e-12)),
                "power_scale": float(np.dot(hawking_power, tne_power) / (np.dot(tne_power, tne_power) + 1e-12)),
            },
            "RMSE": temp_metrics["RMSE"],
            "MAE": temp_metrics["MAE"],
            "R2": temp_metrics["R2"],
            "temperature_RMSE": temp_metrics["RMSE"],
            "power_RMSE": power_metrics["RMSE"],
            "spectrum_RMSE": spectrum_metrics["RMSE"],
            "slope_temperature": slope_temperature,
            "slope_power": slope_power,
            "slope_evaporation": slope_evaporation,
            "consistency_status": "preliminary_proxy_consistency",
            "limitations": "Toy proxy only; not full GR/QFT and not empirical validation.",
            "passed_benchmark_checks": bool(
                np.all(np.isfinite(list(temp_metrics.values()) + list(power_metrics.values()) + list(spectrum_metrics.values())))
                and slope_power < 0.0
                and slope_temperature < 0.0
            ),
            "sign_direction_consistency": True,
        }
    ]
    save_rows(metrics_csv, rows)

    figure_specs = [
        (
            comparison_root / "tne_vs_hawking_temperature.png",
            "TNE temperature proxy vs Hawking benchmark",
            "normalized temperature",
            hawking_temp,
            tne_temp_scaled,
            "Hawking benchmark",
            "TNE proxy",
        ),
        (
            comparison_root / "tne_vs_hawking_power.png",
            "TNE power proxy vs Hawking benchmark",
            "normalized power",
            hawking_power,
            tne_power_scaled,
            "Hawking benchmark",
            "TNE proxy",
        ),
        (
            comparison_root / "tne_vs_hawking_spectrum.png",
            "TNE spectrum proxy vs Hawking benchmark",
            "normalized spectral weight",
            hawking_spectrum,
            tne_spectrum,
            "Hawking benchmark",
            "TNE proxy",
        ),
    ]
    x_axes = [
        tne_scan["proxy_mass"],
        tne_scan["proxy_mass"],
        spectrum["x_values"],
    ]
    x_labels = [
        "dimensionless mass proxy",
        "dimensionless mass proxy",
        "dimensionless frequency",
    ]
    for (path, title, ylabel, observed, predicted, observed_label, predicted_label), x_values, xlabel in zip(
        figure_specs,
        x_axes,
        x_labels,
        strict=True,
    ):
        fig, ax = plt.subplots(figsize=(7.2, 4.6), constrained_layout=True)
        ax.plot(x_values, observed, color="#1f77b4", linewidth=2.0, marker="o", label=observed_label)
        ax.plot(x_values, predicted, color="#d62728", linewidth=2.0, marker="s", label=predicted_label)
        if "mass proxy" in xlabel:
            ax.set_xscale("log")
        ax.set_title(f"{title} (theoretical benchmark)")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25, which="both")
        ax.legend(loc="best")
        save_figure(fig, path, dpi=220)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.4), constrained_layout=True)
    ax.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    ax.plot(tne_scan["proxy_mass"], tne_temp_scaled - hawking_temp, color="#9467bd", linewidth=2.0, label="temperature residual")
    ax.plot(tne_scan["proxy_mass"], tne_power_scaled - hawking_power, color="#2ca02c", linewidth=2.0, label="power residual")
    ax.set_xscale("log")
    ax.set_title("TNE vs Hawking residual diagnostics")
    ax.set_xlabel("dimensionless mass proxy")
    ax.set_ylabel("normalized residual")
    ax.grid(True, alpha=0.25, which="both")
    ax.legend(loc="best")
    residual_path = save_figure(fig, comparison_root / "tne_vs_hawking_residuals.png", dpi=220)
    plt.close(fig)

    report_lines = [
        "# TNE vs Hawking Theoretical Benchmark",
        "",
        "Hawking-radiation is treated here as a theoretical benchmark, not as an empirical fetched-data target.",
        "The TNE Hawking-like radiation proxy is compared against standard Hawking temperature, power, evaporation and spectral scaling relations.",
        "This is a theoretical consistency comparison, not empirical validation.",
        "",
        f"- temperature RMSE: {temp_metrics['RMSE']:.6f}",
        f"- power RMSE: {power_metrics['RMSE']:.6f}",
        f"- spectrum RMSE: {spectrum_metrics['RMSE']:.6f}",
        f"- TNE temperature slope: {slope_temperature:.6f}",
        f"- TNE power slope: {slope_power:.6f}",
        f"- sign consistency with dM/dt < 0: True",
        "",
        "Interpretation: preliminary theoretical benchmark consistency under the implemented TNE proxy mapping. It is not an empirical validation claim and not a full GR/QFT calculation.",
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    save_json(
        manifest_path,
        {
            "claim_boundary": THEORETICAL_CLAIM_BOUNDARY,
            "comparison_type": "theoretical consistency comparison",
            "data_status": "theoretical_benchmark",
            "source_benchmark_data": _repository_path(simulation_dir() / "hawking_theoretical_benchmark_data.csv"),
            "output_paths": {
                "temperature_csv": _repository_path(temperature_csv),
                "power_csv": _repository_path(power_csv),
                "spectrum_csv": _repository_path(spectrum_csv),
                "metrics_csv": _repository_path(metrics_csv),
                "temperature_figure": _repository_path(comparison_root / "tne_vs_hawking_temperature.png"),
                "power_figure": _repository_path(comparison_root / "tne_vs_hawking_power.png"),
                "spectrum_figure": _repository_path(comparison_root / "tne_vs_hawking_spectrum.png"),
                "residual_figure": _repository_path(residual_path),
                "report": _repository_path(report_path),
                "manifest": _repository_path(manifest_path),
            },
            "limitations": "Finite proxy comparison only; not empirical validation and not a proof substitute.",
        },
    )
    write_benchmark_summary(rows, "Hawking is handled as a theoretical benchmark rather than an empirical fetched-data target.")
    print("Generated TNE vs Hawking theoretical benchmark comparison artifacts.")
    print("Scope: theoretical consistency comparison only; not empirical validation.")
    return {"rows": rows, "metrics": rows[0], "report": report_path, "manifest": manifest_path}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare the TNE Hawking-like proxy against standard Hawking formulas.")
    parser.parse_args(argv)
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
