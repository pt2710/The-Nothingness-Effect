"""Extend full TNE AI tuning with held-out metrics and visual artifacts."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import zipfile
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.decomposition import PCA
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.run_comprehensive_ai_evaluation import _evaluate_with_pgqenn_graph_metrics  # noqa: E402
from tools.run_full_ai_hyperparameter_evaluation import Config, build  # noqa: E402
from tools.run_tabular_ai_evaluation import _dataset  # noqa: E402
from the_nothingness_effect.artificial_intelligence.pgqenn.training_evaluation import (  # noqa: E402
    evaluate_pgqenn_graph_heads,
)

NAMES = {"fraud": ("legitimate", "fraud"), "breast-cancer": ("benign", "malignant")}
MODELS = ("QENN", "PGQENN", "SOInets", "Multimodal")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_model(path: Path, selected: dict[str, Any]) -> tuple[torch.nn.Module, int]:
    payload = torch.load(path, map_location="cpu", weights_only=False)
    model = build(Config(**selected))
    state = payload["model_state_dict"]
    for key, value in state.items():
        if "." not in key and not hasattr(model, key):
            model.register_buffer(key, torch.zeros_like(value))
    result = model.load_state_dict(state, strict=False)
    if result.missing_keys or result.unexpected_keys:
        raise RuntimeError(f"checkpoint mismatch: {result}")
    model.eval()
    return model, int(payload["seed"])


def metric_bundle(labels: np.ndarray, probabilities: np.ndarray) -> tuple[dict[str, float], np.ndarray]:
    predictions = probabilities.argmax(1)
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    tn, fp, fn, tp = matrix.ravel()
    positive = probabilities[:, 1]
    confidence = probabilities.max(1)
    ece = 0.0
    edges = np.linspace(0.0, 1.0, 11)
    for lower, upper in zip(edges[:-1], edges[1:], strict=True):
        mask = (confidence > lower) & (confidence <= upper)
        if mask.any():
            ece += mask.mean() * abs((predictions[mask] == labels[mask]).mean() - confidence[mask].mean())
    values = {
        "accuracy": accuracy_score(labels, predictions),
        "balanced_accuracy": balanced_accuracy_score(labels, predictions),
        "precision": precision_score(labels, predictions, zero_division=0),
        "recall_sensitivity": recall_score(labels, predictions, zero_division=0),
        "specificity": tn / max(1, tn + fp),
        "negative_predictive_value": tn / max(1, tn + fn),
        "f1": f1_score(labels, predictions, zero_division=0),
        "matthews_correlation": matthews_corrcoef(labels, predictions),
        "roc_auc": roc_auc_score(labels, positive),
        "pr_auc_average_precision": average_precision_score(labels, positive),
        "cross_entropy": log_loss(labels, probabilities, labels=[0, 1]),
        "brier_score": brier_score_loss(labels, positive),
        "expected_calibration_error": ece,
        "mean_confidence": confidence.mean(),
        "positive_prevalence": labels.mean(),
        "support": labels.size,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "true_positive": tp,
    }
    metrics = {key: float(value) for key, value in values.items()}
    if not all(math.isfinite(value) for value in metrics.values()):
        raise RuntimeError("non-finite extended metric")
    return metrics, matrix


def save_matrix(path: Path, frame: pd.DataFrame, title: str) -> None:
    figure, axis = plt.subplots(figsize=(11, max(5, 0.35 * len(frame))), constrained_layout=True)
    image = axis.imshow(frame.to_numpy(dtype=float), aspect="auto")
    axis.set(title=title, xticks=range(len(frame.columns)), yticks=range(len(frame.index)), xticklabels=frame.columns, yticklabels=frame.index)
    axis.tick_params(axis="x", rotation=35)
    figure.colorbar(image, ax=axis)
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def save_confusion(path: Path, matrix: np.ndarray, title: str, names: tuple[str, str]) -> None:
    frame = pd.DataFrame(matrix, index=names, columns=names)
    save_matrix(path, frame, title)


def save_curve(path: Path, curves: dict[str, tuple[np.ndarray, np.ndarray]], title: str, xlabel: str, ylabel: str, diagonal: bool = False) -> None:
    figure, axis = plt.subplots(figsize=(7, 6), constrained_layout=True)
    if diagonal:
        axis.plot([0, 1], [0, 1], linestyle="--", label="reference")
    for model, (x, y) in curves.items():
        axis.plot(x, y, marker="o" if "Calibration" in title else None, label=model)
    axis.set(title=title, xlabel=xlabel, ylabel=ylabel, xlim=(0, 1), ylim=(0, 1.05))
    axis.legend()
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def pca3(values: np.ndarray) -> np.ndarray:
    count = min(3, values.shape[0], values.shape[1])
    result = PCA(n_components=count, svd_solver="full").fit_transform(values)
    return np.pad(result, ((0, 0), (0, 3 - count))) if count < 3 else result


def save_3d(path: Path, points: np.ndarray, labels: np.ndarray, title: str) -> None:
    figure = plt.figure(figsize=(8, 7), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    for label in sorted(np.unique(labels)):
        chosen = labels == label
        axis.scatter(points[chosen, 0], points[chosen, 1], points[chosen, 2], s=14, label=f"class {label}")
    axis.set(title=title, xlabel="component 1", ylabel="component 2", zlabel="component 3")
    axis.legend()
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def save_gif(path: Path, points: np.ndarray, labels: np.ndarray, title: str) -> None:
    figure = plt.figure(figsize=(7, 6))
    axis = figure.add_subplot(111, projection="3d")
    for label in sorted(np.unique(labels)):
        chosen = labels == label
        axis.scatter(points[chosen, 0], points[chosen, 1], points[chosen, 2], s=12, label=f"class {label}")
    axis.set(title=title, xlabel="component 1", ylabel="component 2", zlabel="component 3")
    axis.legend()
    def update(frame: int) -> tuple[Any, ...]:
        axis.view_init(elev=24 + 8 * math.sin(2 * math.pi * frame / 36), azim=10 * frame)
        return (axis,)
    animation.FuncAnimation(figure, update, frames=36, interval=100).save(path, writer=animation.PillowWriter(fps=10))
    plt.close(figure)


def run(source: Path, dataset: str, root: Path) -> dict[str, Any]:
    summary_path = root / "evaluation_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    selected = summary["selected_hyperparameters"]
    seeds = [int(value) for value in summary["evaluation_seeds"]]
    plots, movies = root / "plots", root / "animations"
    plots.mkdir(exist_ok=True)
    movies.mkdir(exist_ok=True)
    blocks = {name: [] for name in ("QENN", "PGQENN", "Multimodal")}
    labels_by_model = {name: [] for name in blocks}
    seed_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    hidden, rbm_hidden, all_labels = [], [], []
    for seed in seeds:
        model, saved_seed = load_model(root / "checkpoints" / f"seed_{seed}_best.pt", selected)
        if saved_seed != seed:
            raise RuntimeError("checkpoint seed mismatch")
        data, _ = _dataset(source, dataset, seed)
        evaluation = _evaluate_with_pgqenn_graph_metrics(model, data.test)
        graph = evaluate_pgqenn_graph_heads(model, data.test)
        labels = data.test.labels.cpu().numpy().astype(int)
        soinet = evaluation.output.backbone_output.soinet_output
        qenn = torch.stack([item.observation.detach().cpu() for item in soinet.qenn_outputs]).mean(0).numpy()
        probabilities = {"QENN": qenn, "PGQENN": graph["probabilities"].cpu().numpy(), "Multimodal": evaluation.output.observation.cpu().numpy()}
        for name, values in probabilities.items():
            metrics, _ = metric_bundle(labels, values)
            seed_rows.append({"dataset": dataset, "model": name, "seed": seed, **metrics})
            blocks[name].append(values)
            labels_by_model[name].append(labels)
            for index, probability in enumerate(values):
                prediction_rows.append({"dataset": dataset, "model": name, "seed": seed, "sample_index": index, "true": int(labels[index]), "predicted": int(probability.argmax()), "probability_negative": float(probability[0]), "probability_positive": float(probability[1])})
        seed_rows.append({**seed_rows[-1], "model": "SOInets", "shares_predictions_with": "Multimodal"})
        hidden.append(evaluation.output.hidden.cpu().numpy())
        state = evaluation.output.global_rbm_state
        if state is None:
            raise RuntimeError("global RBM state missing")
        rbm_hidden.append(state.hidden_probability.cpu().numpy())
        all_labels.append(labels)
    aggregate, confusions, model_data = [], {}, {}
    for name in blocks:
        labels = np.concatenate(labels_by_model[name])
        probabilities = np.concatenate(blocks[name])
        metrics, matrix = metric_bundle(labels, probabilities)
        aggregate.append({"dataset": dataset, "model": name, "seed": "aggregate", **metrics})
        confusions[name] = matrix
        model_data[name] = (labels, probabilities)
    aggregate.append({**aggregate[-1], "model": "SOInets", "shares_predictions_with": "Multimodal"})
    confusions["SOInets"] = confusions["Multimodal"].copy()
    write_csv(root / "extended_model_metrics.csv", seed_rows + aggregate)
    write_csv(root / "extended_prediction_records.csv", prediction_rows)
    write_csv(root / "extended_confusion_matrices.csv", [{"model": name, "true": row, "predicted": column, "count": int(matrix[row, column])} for name, matrix in confusions.items() for row in range(2) for column in range(2)])
    metrics = ["accuracy", "balanced_accuracy", "precision", "recall_sensitivity", "specificity", "f1", "matthews_correlation", "roc_auc", "pr_auc_average_precision"]
    save_matrix(plots / "extended_model_metric_matrix.png", pd.DataFrame(aggregate).set_index("model").reindex(MODELS)[metrics], "Held-out model metric matrix")
    for name, matrix in confusions.items():
        save_confusion(plots / f"{name.lower()}_confusion_matrix.png", matrix, f"{name} held-out confusion matrix", NAMES[dataset])
    roc, pr, calibration = {}, {}, {}
    for name, (labels, probabilities) in model_data.items():
        positive = probabilities[:, 1]
        fpr, tpr, _ = roc_curve(labels, positive)
        precision, recall, _ = precision_recall_curve(labels, positive)
        fraction, predicted = calibration_curve(labels, positive, n_bins=10, strategy="quantile")
        roc[name], pr[name], calibration[name] = (fpr, tpr), (recall, precision), (predicted, fraction)
    save_curve(plots / "roc_curves.png", roc, "ROC curves", "false-positive rate", "true-positive rate", True)
    save_curve(plots / "precision_recall_curves.png", pr, "Precision-recall curves", "recall", "precision")
    save_curve(plots / "calibration_curves.png", calibration, "Calibration curves", "mean predicted probability", "observed fraction", True)
    search = pd.read_csv(root / "hyperparameter_search.csv").reset_index(drop=True)
    figure, axis = plt.subplots(figsize=(10, 5), constrained_layout=True)
    axis.plot(np.arange(len(search)), search["objective"], marker="o")
    axis.set(title="Validation objective across tuning trials", xlabel="trial", ylabel="objective")
    figure.savefig(plots / "hyperparameter_objective.png", dpi=180, bbox_inches="tight")
    plt.close(figure)
    numeric = search.select_dtypes(include=[np.number])
    numeric = numeric.loc[:, numeric.nunique() > 1]
    save_matrix(plots / "hyperparameter_correlation_matrix.png", numeric.corr(), "Hyperparameter/metric correlation matrix")
    figure = plt.figure(figsize=(8, 7), constrained_layout=True)
    axis = figure.add_subplot(111, projection="3d")
    axis.scatter(np.arange(len(search)), search["validation_macro_f1"], search["objective"], s=24)
    axis.set(title="3D tuning trajectory", xlabel="trial", ylabel="validation macro-F1", zlabel="objective")
    figure.savefig(plots / "hyperparameter_search_3d.png", dpi=180, bbox_inches="tight")
    plt.close(figure)
    for source_name, columns, title in (("split_metrics.csv", ["accuracy", "macro_f1", "balanced_accuracy", "expected_calibration_error"], "Integrated split metrics"), ("module_metrics.csv", ["accuracy", "macro_f1", "residual_l2"], "Module metric matrix"), ("global_rbm_metrics.csv", ["reconstruction_rmse", "contrastive_divergence", "mean_free_energy", "hidden_entropy"], "Global RBM split matrix")):
        table = pd.read_csv(root / source_name)
        index = "split" if "split" in table else "module"
        save_matrix(plots / source_name.replace(".csv", "_matrix.png"), table.groupby(index)[columns].mean(), title)
    source_table = pd.read_csv(root / "source_removal.csv")
    columns = [name for name in ("accuracy", "macro_f1", "cross_entropy", "mean_reconstruction_rmse") if name in source_table]
    pivot = source_table.groupby("variant")[columns].mean()
    save_matrix(plots / "source_removal_matrix.png", pivot.subtract(pivot.loc["complete"], axis=1), "Source-removal metric deltas")
    labels = np.concatenate(all_labels)
    latent, rbm = pca3(np.concatenate(hidden)), pca3(np.concatenate(rbm_hidden))
    save_3d(plots / "multimodal_latent_3d.png", latent, labels, "Multimodal latent manifold")
    save_3d(plots / "global_rbm_hidden_3d.png", rbm, labels, "Global RBM hidden manifold")
    save_gif(movies / "multimodal_latent_3d.gif", latent, labels, "Rotating multimodal latent manifold")
    save_gif(movies / "global_rbm_hidden_3d.gif", rbm, labels, "Rotating global RBM hidden manifold")
    write_csv(root / "multimodal_latent_3d.csv", [{"label": int(labels[index]), "x": float(latent[index, 0]), "y": float(latent[index, 1]), "z": float(latent[index, 2])} for index in range(len(labels))])
    write_csv(root / "global_rbm_hidden_3d.csv", [{"label": int(labels[index]), "x": float(rbm[index, 0]), "y": float(rbm[index, 1]), "z": float(rbm[index, 2])} for index in range(len(labels))])
    pngs, gifs = list(plots.glob("*.png")), list(movies.glob("*.gif"))
    if len(pngs) < 15 or len(gifs) < 2:
        raise RuntimeError(f"insufficient visuals: {len(pngs)} PNG, {len(gifs)} GIF")
    extended = {"schema_version": "2.0", "dataset": dataset, "models": list(MODELS), "aggregate_metrics": aggregate, "plot_count": len(pngs), "animation_count": len(gifs), "claim_boundary": "held-out finite benchmark; not deployment validation or theorem proof"}
    (root / "extended_evaluation_summary.json").write_text(json.dumps(extended, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary["extended_evaluation"] = extended
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = root / "artifact_manifest.json"
    files = sorted(path for path in root.rglob("*") if path.is_file() and path != manifest)
    manifest.write_text(json.dumps({"schema_version": "2.0", "files": [{"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": digest(path)} for path in files]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    archive_path = root.with_suffix(".zip")
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(root.parent))
    return {"dataset": dataset, "plots": len(pngs), "animations": len(gifs), "archive_sha256": digest(archive_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--dataset", choices=tuple(NAMES), required=True)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.source, args.dataset, args.root), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
