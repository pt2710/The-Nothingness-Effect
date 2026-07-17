"""Run a multi-seed synthetic multimodal robustness and OOD-style benchmark.

This benchmark measures finite model behaviour under controlled corruption and
leave-one-modality-out conditions. It is synthetic validation evidence, not an
empirical theorem proof or a substitute for real-world datasets.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from the_nothingness_effect.artificial_intelligence.multimodal.data import (
    MultimodalBatch,
    make_synthetic_multimodal_dataset,
)
from the_nothingness_effect.artificial_intelligence.multimodal.evaluation import (
    evaluate_multimodal_model,
    evaluate_source_removals,
)
from the_nothingness_effect.artificial_intelligence.multimodal.model import (
    TNETrainableMultimodalModel,
)
from the_nothingness_effect.artificial_intelligence.multimodal.training import (
    train_multimodal_model,
)


CLAIM_BOUNDARY=(
    "synthetic multi-seed robustness evidence; not empirical validation or theorem proof"
)


def corrupt_batch(batch: MultimodalBatch, scenario: str, *, seed: int) -> MultimodalBatch:
    generator=torch.Generator().manual_seed(seed)
    modalities={name:value.clone() for name,value in batch.modalities.items()}
    if scenario=="clean":
        pass
    elif scenario.startswith("gaussian_"):
        scale=float(scenario.split("_",1)[1])
        modalities={
            name:value+scale*torch.randn(value.shape,generator=generator,dtype=value.dtype)
            for name,value in modalities.items()
        }
    elif scenario.startswith("remove_"):
        name=scenario.removeprefix("remove_")
        if name not in modalities: raise ValueError(f"unknown modality: {name}")
        modalities[name]=torch.zeros_like(modalities[name])
    elif scenario=="sound_phase_shift":
        modalities["sound"]=torch.roll(modalities["sound"],shifts=7,dims=-1)
    elif scenario=="vision_occlusion":
        modalities["vision"][...,2:6,2:6]=0.0
    elif scenario=="color_channel_permutation":
        modalities["color"]=modalities["color"][...,[1,2,0]]
    else:
        raise ValueError(f"unknown corruption scenario: {scenario}")
    return MultimodalBatch(modalities,batch.labels.clone()).validate()


def _write_csv(path: Path,rows: list[dict[str,object]]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def run(output: Path,seeds: Iterable[int],epochs: int) -> dict[str,object]:
    output.mkdir(parents=True,exist_ok=True)
    scenarios=(
        "clean","gaussian_0.05","gaussian_0.15","remove_color","remove_sound",
        "remove_vision","sound_phase_shift","vision_occlusion",
        "color_channel_permutation",
    )
    rows=[]
    ablation_rows=[]
    for seed in seeds:
        torch.manual_seed(seed)
        dataset=make_synthetic_multimodal_dataset(samples_per_class=10,seed=seed)
        model=TNETrainableMultimodalModel()
        training=train_multimodal_model(
            model,dataset.train,dataset.validation,epochs=epochs,seed=seed,
            optimize_K_D=True,adaptive_learning_rate=True,
        )
        for scenario in scenarios:
            batch=corrupt_batch(dataset.test,scenario,seed=seed+101)
            evaluation=evaluate_multimodal_model(model,batch)
            rows.append({
                "seed":seed,"scenario":scenario,"epochs":epochs,
                **evaluation.metrics,
                "closure_status":evaluation.output.closure_status.value,
                "residual_l2":sum(value*value for value in evaluation.residuals.values())**0.5,
                "final_validation_loss":training.history[-1].validation_loss,
                "final_validation_accuracy":training.history[-1].validation_accuracy,
            })
        for record in evaluate_source_removals(model,dataset.test):
            ablation_rows.append({"seed":seed,"epochs":epochs,**record})

    metric_names=(
        "accuracy","cross_entropy","brier_score","expected_calibration_error",
        "mean_reconstruction_rmse","residual_l2",
    )
    aggregate=[]
    for scenario in scenarios:
        selected=[row for row in rows if row["scenario"]==scenario]
        for metric in metric_names:
            values=[float(row[metric]) for row in selected]
            aggregate.append({
                "scenario":scenario,"metric":metric,"count":len(values),
                "mean":mean(values),"population_std":pstdev(values),
                "minimum":min(values),"maximum":max(values),
            })

    _write_csv(output/"multiseed_scenario_metrics.csv",rows)
    _write_csv(output/"multiseed_metric_summary.csv",aggregate)
    _write_csv(output/"multiseed_source_removal.csv",ablation_rows)

    accuracy=[item for item in aggregate if item["metric"]=="accuracy"]
    figure,axis=plt.subplots(figsize=(11,5),constrained_layout=True)
    axis.errorbar(
        range(len(accuracy)),[float(item["mean"]) for item in accuracy],
        yerr=[float(item["population_std"]) for item in accuracy],fmt="o",capsize=4,
    )
    axis.set_xticks(range(len(accuracy)),[str(item["scenario"]) for item in accuracy],rotation=35,ha="right")
    axis.set_ylim(0.0,1.05)
    axis.set_ylabel("accuracy mean ± population SD")
    axis.set_title("Multimodal synthetic robustness across seeds")
    axis.text(0.01,0.01,CLAIM_BOUNDARY,transform=axis.transAxes,fontsize=7)
    figure.savefig(output/"multiseed_accuracy_robustness.png",dpi=160)
    plt.close(figure)

    clean=[row for row in rows if row["scenario"]=="clean"]
    figure,axis=plt.subplots(figsize=(8,5),constrained_layout=True)
    axis.scatter(
        [float(row["expected_calibration_error"]) for row in clean],
        [float(row["mean_reconstruction_rmse"]) for row in clean],
    )
    for row in clean:
        axis.annotate(str(row["seed"]),(float(row["expected_calibration_error"]),float(row["mean_reconstruction_rmse"])))
    axis.set_xlabel("expected calibration error")
    axis.set_ylabel("mean reconstruction RMSE")
    axis.set_title("Clean-test seed dispersion")
    axis.text(0.01,0.01,CLAIM_BOUNDARY,transform=axis.transAxes,fontsize=7)
    figure.savefig(output/"seed_calibration_reconstruction.png",dpi=160)
    plt.close(figure)

    report={
        "schema_version":"1.0","seeds":list(seeds),"epochs":epochs,
        "scenarios":list(scenarios),"claim_boundary":CLAIM_BOUNDARY,
        "records":len(rows),"source_removal_records":len(ablation_rows),
        "all_metrics_finite":all(
            torch.isfinite(torch.tensor(float(row[name])))
            for row in rows for name in metric_names
        ),
        "outputs":[
            "multiseed_scenario_metrics.csv","multiseed_metric_summary.csv",
            "multiseed_source_removal.csv","multiseed_accuracy_robustness.png",
            "seed_calibration_reconstruction.png",
        ],
    }
    (output/"multiseed_robustness_manifest.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    if not report["all_metrics_finite"]: raise RuntimeError("non-finite robustness metric")
    return report


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--seeds",type=int,nargs="+",default=[0,1,2])
    parser.add_argument("--epochs",type=int,default=6)
    args=parser.parse_args()
    report=run(args.output,tuple(args.seeds),args.epochs)
    print(f"multimodal_robustness=passed seeds={report['seeds']} records={report['records']}")
    return 0


if __name__=="__main__": raise SystemExit(main())
