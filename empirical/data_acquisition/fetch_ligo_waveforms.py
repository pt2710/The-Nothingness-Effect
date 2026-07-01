"""Fetch a lightweight derived GW150914 ringdown segment from GWOSC public data."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt

from empirical.data_acquisition.fetch_utils import cache_raw_path, download_to_cache, provenance_manifest, write_dataset_manifest
from empirical.io import public_data_path, save_rows


try:
    import h5py
except Exception:  # pragma: no cover - optional runtime dependency
    h5py = None


GWOSC_URL = "https://gwosc.org/archive/data/O1/1126170624/H-H1_LOSC_4_V1-1126256640-4096.hdf5"
GWOSC_API_URL = "https://gwosc.org/api/v2/strain-files/H1-1126259446-4kHz"
GW150914_GPS = 1126259462.4


def _read_ringdown_rows(hdf5_path: Path) -> list[dict[str, float | str]]:
    if h5py is None:
        raise RuntimeError("h5py is required to derive the public ringdown segment from GWOSC HDF5.")
    with h5py.File(hdf5_path, "r") as handle:
        strain = np.asarray(handle["strain"]["Strain"], dtype=float)
        gps_start = float(handle["meta"]["GPSstart"][()])
        duration = float(handle["meta"]["Duration"][()])
    sample_rate = len(strain) / duration
    time = gps_start + np.arange(len(strain), dtype=float) / sample_rate
    ringdown_start = GW150914_GPS + 0.02
    ringdown_stop = GW150914_GPS + 0.32
    noise_mask = (time >= GW150914_GPS - 1.5) & (time < GW150914_GPS - 0.5)

    b, a = butter(4, [35.0 / (0.5 * sample_rate), 350.0 / (0.5 * sample_rate)], btype="band")
    filtered = filtfilt(b, a, strain)
    segment_mask = (time >= ringdown_start) & (time <= ringdown_stop)
    segment_time = time[segment_mask] - ringdown_start
    segment_strain = filtered[segment_mask]
    if segment_time.size == 0:
        raise RuntimeError("Derived GW150914 ringdown segment was empty.")

    step = max(1, segment_time.size // 64)
    segment_time = segment_time[::step]
    segment_strain = segment_strain[::step]
    amplitude_scale = np.max(np.abs(segment_strain)) + 1e-24
    normalized_strain = segment_strain / amplitude_scale
    noise_sigma = float(np.std(filtered[noise_mask]) / amplitude_scale)
    if not np.isfinite(noise_sigma) or noise_sigma <= 0.0:
        noise_sigma = 0.05

    rows: list[dict[str, float | str]] = []
    for t_value, s_value in zip(segment_time, normalized_strain, strict=True):
        rows.append(
            {
                "time": float(t_value),
                "strain": float(s_value),
                "strain_normalized": float(s_value),
                "strain_raw": float(segment_strain[len(rows)]),
                "strain_uncertainty": noise_sigma,
                "strain_uncertainty_raw": float(np.std(filtered[noise_mask])) if np.any(noise_mask) else noise_sigma * amplitude_scale,
                "event_id": "GW150914_H1_public",
                "detector": "H1",
                "source_status": "fetched",
            }
        )
    return rows


def run(
    output_dir: str | Path | None = None,
    *,
    offline: bool = False,
    force: bool = False,
    quick: bool = False,
) -> dict[str, object]:
    derived_path = public_data_path("ligo_gw150914_ringdown.csv", output_dir)
    manifest_name = "ligo_waveforms_manifest.json"

    if offline and derived_path.exists():
        payload = provenance_manifest(
            dataset_name="ligo_waveforms",
            source_name="GWOSC public strain archive",
            source_url=GWOSC_API_URL,
            script_name=Path(__file__).name,
            status="cached",
            output_dir=str(output_dir) if output_dir is not None else None,
            derived_file_path=derived_path,
            access_method="cached_public_fetch",
            expected_file_type="csv",
            license_note="Derived lightweight ringdown segment from GWOSC public strain data.",
            citation_note="Previously generated GW150914 ringdown segment.",
            preprocessing_steps=["Loaded previously generated compact ringdown CSV."],
            limitations="Offline mode does not refresh public GWOSC inputs.",
        )
        write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
        return payload

    if offline and not derived_path.exists():
        payload = provenance_manifest(
            dataset_name="ligo_waveforms",
            source_name="GWOSC public strain archive",
            source_url=GWOSC_API_URL,
            script_name=Path(__file__).name,
            status="fixture_only",
            output_dir=str(output_dir) if output_dir is not None else None,
            access_method="offline_fixture_fallback",
            expected_file_type="csv",
            license_note="Fixture fallback remains available when offline.",
            citation_note="Public GWOSC fetch skipped in offline mode.",
            preprocessing_steps=["Offline mode selected; no GWOSC download attempted."],
            limitations="No cached derived GW150914 ringdown CSV was available.",
        )
        write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
        return payload

    if h5py is None:
        payload = provenance_manifest(
            dataset_name="ligo_waveforms",
            source_name="GWOSC public strain archive",
            source_url=GWOSC_API_URL,
            script_name=Path(__file__).name,
            status="manual_required",
            output_dir=str(output_dir) if output_dir is not None else None,
            access_method="missing_optional_dependency",
            expected_file_type="csv",
            license_note="Install h5py to derive the compact ringdown segment.",
            citation_note="GWOSC public source remains the intended provenance.",
            preprocessing_steps=["Detected missing optional HDF5 reader dependency."],
            limitations="h5py was unavailable, so no derived public ringdown CSV was generated.",
        )
        write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
        return payload

    raw_hdf5_path = cache_raw_path("ligo_waveforms", "H-H1_LOSC_4_V1-1126256640-4096.hdf5", str(output_dir) if output_dir is not None else None)
    download_to_cache(GWOSC_URL, raw_hdf5_path, force=force)
    rows = _read_ringdown_rows(raw_hdf5_path)
    save_rows(derived_path, rows)
    payload = provenance_manifest(
        dataset_name="ligo_waveforms",
        source_name="GWOSC public strain archive",
        source_url=GWOSC_API_URL,
        script_name=Path(__file__).name,
        status="fetched",
        output_dir=str(output_dir) if output_dir is not None else None,
        raw_file_path=raw_hdf5_path,
        derived_file_path=derived_path,
        access_method="public_hdf5_download",
        expected_file_type="csv",
        license_note="Derived lightweight ringdown segment from GWOSC public strain data.",
        citation_note="Derived single-detector GW150914 ringdown segment from the H1 public strain file.",
        preprocessing_steps=[
            "Downloaded the public GWOSC H1 strain HDF5 for the O1 interval containing GW150914.",
            "Applied a simple 35-350 Hz Butterworth bandpass filter.",
            "Selected a short post-merger ringdown window.",
            "Stored both raw and normalized strain columns for fair residual comparison use.",
        ],
        limitations="Single-detector derived ringdown proxy only; not a full LIGO parameter-estimation product.",
        extra={"event_id": "GW150914_H1_public"},
    )
    write_dataset_manifest(manifest_name, payload, str(output_dir) if output_dir is not None else None)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch a lightweight derived GW150914 ringdown segment from GWOSC.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    run(output_dir=args.output_dir, offline=args.offline, force=args.force, quick=args.quick)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
