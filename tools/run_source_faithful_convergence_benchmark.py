"""Run grid-refinement diagnostics for the 23 source-faithful B/C contracts.

The benchmark evaluates the same finite laws on 9, 17 and 33 point grids, records
residual, boundary and source-necessity behaviour, and emits module-level plots.
Finite and stable refinement is numerical evidence only; it is not a proof of a
continuum theorem or empirical validation.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import fields, is_dataclass, replace
import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tools.theorem_diagnostic_artifacts import _numeric_vector
from the_nothingness_effect._runtime.theorem_complex_runtime.contracts import evaluate_contract
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_black_hole import black_hole_sample
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_dubler import elastic_dubler_sample
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_elastic_pi_ripples import elastic_pi_ripple_sample
from the_nothingness_effect._runtime.theorem_complex_runtime._source_samples_locality_gravity import locality_gravity_sample
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.black_holes_hawking_radiation_and_observer_horizons import source_faithful_contracts as black_hole
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.gravitational_ripples_as_elastic_pi_wavefronts import source_faithful_contracts as ripples
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.locality_driven_gravity import source_faithful_contracts as locality
from the_nothingness_effect.gravitational_cosmological_and_quantum_dynamics_architecture.the_elastic_dubler_effect import source_faithful_contracts as dubler


CLAIM_BOUNDARY=(
    "finite grid-refinement diagnostic; not continuum convergence proof or empirical validation"
)


def _coordinate_name(value: Any) -> str:
    for name in ("coordinates","coordinate","radius"):
        if hasattr(value,name): return name
    raise TypeError(f"no coordinate field for {type(value).__name__}")


def _interp_vector(old_x: np.ndarray,new_x: np.ndarray,value: np.ndarray) -> np.ndarray:
    if np.iscomplexobj(value):
        return np.interp(new_x,old_x,np.real(value))+1j*np.interp(new_x,old_x,np.imag(value))
    return np.interp(new_x,old_x,value.astype(float))


def _interp_square(old_x: np.ndarray,new_x: np.ndarray,value: np.ndarray) -> np.ndarray:
    rows=np.vstack([_interp_vector(old_x,new_x,row) for row in value])
    return np.vstack([_interp_vector(old_x,new_x,rows[:,column]) for column in range(rows.shape[1])]).T


def resample_input(value: Any,points: int) -> Any:
    if not is_dataclass(value): raise TypeError("resampling requires a dataclass input")
    coordinate_name=_coordinate_name(value)
    old_x=np.asarray(getattr(value,coordinate_name),dtype=float)
    new_x=np.linspace(float(old_x[0]),float(old_x[-1]),points)
    updates={coordinate_name:new_x}
    for field in fields(value):
        name=field.name
        if name==coordinate_name: continue
        item=getattr(value,name)
        if not isinstance(item,np.ndarray): continue
        array=np.asarray(item)
        if name in {"parity","flowpoint_parity"}:
            updates[name]=np.mod(np.arange(points),2).astype(array.dtype)
        elif array.ndim==1 and array.shape[0]==old_x.size:
            updates[name]=_interp_vector(old_x,new_x,array)
        elif array.ndim==2 and array.shape==(old_x.size,old_x.size):
            updates[name]=_interp_square(old_x,new_x,array)
        elif array.ndim>=2 and array.shape[-1]==old_x.size:
            flattened=array.reshape((-1,old_x.size))
            interpolated=np.vstack([_interp_vector(old_x,new_x,row) for row in flattened])
            updates[name]=interpolated.reshape((*array.shape[:-1],points))
    result=replace(value,**updates)
    coordinate=np.asarray(getattr(result,coordinate_name),dtype=float)
    if coordinate.size!=points or np.any(np.diff(coordinate)<=0):
        raise RuntimeError("invalid resampled coordinate")
    return result


def _write_csv(path: Path,rows: list[dict[str,object]]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def run(output: Path,resolutions: tuple[int,...]=(9,17,33)) -> dict[str,object]:
    output.mkdir(parents=True,exist_ok=True)
    families=(
        ("elastic_dubler",dubler,elastic_dubler_sample()),
        ("locality_driven_gravity",locality,locality_gravity_sample()),
        ("black_hole_dynamics",black_hole,black_hole_sample()),
        ("elastic_pi_ripples",ripples,elastic_pi_ripple_sample()),
    )
    rows=[]
    for family,module,base in families:
        contracts=[contract for contract in module.contracts() if contract.source_ids]
        for points in resolutions:
            value=resample_input(base,points)
            for contract in contracts:
                evaluation=evaluate_contract(contract,value)
                residual=(
                    np.asarray(evaluation.residual.vector,dtype=float)
                    if evaluation.residual is not None else np.zeros(1,dtype=float)
                )
                removals=[check(value) for check in contract.source_removal_checks]
                output_vector=_numeric_vector(evaluation.output)
                rows.append({
                    "family":family,"complex_id":str(contract.complex_id),
                    "level":contract.level.value,"grid_points":points,
                    "closure_status":evaluation.status.value,
                    "exact_semantics":evaluation.exact_semantics,
                    "residual_l2":float(np.linalg.norm(residual)),
                    "output_l2":float(np.linalg.norm(output_vector)),
                    "minimum_source_necessity":min((item.necessity_residual for item in removals),default=0.0),
                    "maximum_source_necessity":max((item.necessity_residual for item in removals),default=0.0),
                    "all_sources_necessary":all(item.necessary for item in removals),
                })
    _write_csv(output/"source_faithful_grid_refinement.csv",rows)

    summary=[]
    for family,module,_ in families:
        selected=[row for row in rows if row["family"]==family]
        for points in resolutions:
            current=[row for row in selected if row["grid_points"]==points]
            summary.append({
                "family":family,"grid_points":points,"contracts":len(current),
                "maximum_residual_l2":max(float(row["residual_l2"]) for row in current),
                "mean_residual_l2":float(np.mean([float(row["residual_l2"]) for row in current])),
                "minimum_source_necessity":min(float(row["minimum_source_necessity"]) for row in current),
                "all_finite":all(np.isfinite(float(row["residual_l2"])) and np.isfinite(float(row["output_l2"])) for row in current),
            })
        figure,axis=plt.subplots(figsize=(8,5),constrained_layout=True)
        identifiers=sorted({str(row["complex_id"]) for row in selected})
        for identifier in identifiers:
            series=[row for row in selected if row["complex_id"]==identifier]
            axis.plot([int(row["grid_points"]) for row in series],[max(float(row["residual_l2"]),1e-16) for row in series],marker="o",alpha=0.7)
        axis.set_yscale("log")
        axis.set_xlabel("grid points")
        axis.set_ylabel("residual L2")
        axis.set_title(f"{family}: finite grid-refinement residuals")
        axis.text(0.01,0.01,CLAIM_BOUNDARY,transform=axis.transAxes,fontsize=7)
        figure.savefig(output/f"{family}_grid_refinement.png",dpi=160)
        plt.close(figure)
    _write_csv(output/"source_faithful_grid_summary.csv",summary)

    report={
        "schema_version":"1.0","families":[item[0] for item in families],
        "resolutions":list(resolutions),"records":len(rows),
        "all_metrics_finite":all(bool(item["all_finite"]) for item in summary),
        "claim_boundary":CLAIM_BOUNDARY,
        "outputs":[
            "source_faithful_grid_refinement.csv","source_faithful_grid_summary.csv",
            *[f"{item[0]}_grid_refinement.png" for item in families],
        ],
    }
    (output/"source_faithful_convergence_manifest.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    if len(rows)!=23*len(resolutions):
        raise RuntimeError(f"expected {23*len(resolutions)} records, got {len(rows)}")
    if not report["all_metrics_finite"]: raise RuntimeError("non-finite grid metric")
    return report


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--resolutions",type=int,nargs="+",default=[9,17,33])
    args=parser.parse_args()
    report=run(args.output,tuple(args.resolutions))
    print(f"source_faithful_convergence=passed records={report['records']} resolutions={report['resolutions']}")
    return 0


if __name__=="__main__": raise SystemExit(main())
