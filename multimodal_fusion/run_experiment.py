#!/usr/bin/env python3
"""
Run the full Image + Text Data Fusion experiment.

Real-world problem
------------------
Multimodal Fake News Detection: classify social-media posts as REAL or FAKE
by fusing visual cues (post image) with textual cues (caption / claim).

Compares unimodal baselines (image-only, text-only) against early, late,
and hybrid fusion models.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.dataset import prepare_datasets
from src.models import build_model
from src.train import collate_fn, evaluate, save_metrics, train_one_model


def plot_history(histories: dict, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for name, hist in histories.items():
        epochs = [h["epoch"] for h in hist]
        axes[0].plot(epochs, [h["val_accuracy"] for h in hist], marker="o", label=name)
        axes[1].plot(epochs, [h["val_f1"] for h in hist], marker="o", label=name)
    axes[0].set_title("Validation Accuracy")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Accuracy")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)
    axes[1].set_title("Validation F1")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("F1")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_comparison(results: dict, out_path: Path) -> None:
    names = list(results.keys())
    metrics = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    x = np.arange(len(names))
    width = 0.15
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, m in enumerate(metrics):
        vals = [results[n]["test"][m] for n in names]
        ax.bar(x + i * width, vals, width, label=m)
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(names, rotation=15, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Test-set Comparison: Unimodal vs Fusion Models")
    ax.legend(ncols=5, fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_confusion(cm, title: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(4.5, 4))
    disp = ConfusionMatrixDisplay(np.array(cm), display_labels=["real", "fake"])
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_roc(results: dict, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    for name, payload in results.items():
        y_true = payload["test"]["y_true"]
        y_prob = payload["test"]["y_prob"]
        RocCurveDisplay.from_predictions(y_true, y_prob, name=name, ax=ax)
    ax.set_title("ROC Curves (Test Set)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-samples", type=int, default=4000)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--embed-dim", type=int, default=128)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    data_dir = ROOT / "data"
    out_dir = ROOT / "outputs"
    fig_dir = ROOT / "figures"
    model_dir = ROOT / "models"
    for d in (out_dir, fig_dir, model_dir):
        d.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    print("Preparing paired image–text dataset...")
    train_ds, val_ds, test_ds, word2idx, meta = prepare_datasets(
        data_dir, n_samples=args.n_samples, seed=args.seed
    )
    print(json.dumps(meta, indent=2))

    train_loader = DataLoader(
        train_ds, batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn, num_workers=0
    )
    val_loader = DataLoader(
        val_ds, batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn, num_workers=0
    )
    test_loader = DataLoader(
        test_ds, batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn, num_workers=0
    )

    model_names = [
        "image_only",
        "text_only",
        "early_fusion",
        "late_fusion",
        "hybrid_fusion",
    ]

    results = {}
    histories = {}

    for name in model_names:
        print(f"\n=== Training {name} ===")
        model = build_model(name, vocab_size=len(word2idx), embed_dim=args.embed_dim)
        model, history, best_val = train_one_model(
            model,
            train_loader,
            val_loader,
            device,
            epochs=args.epochs,
        )
        test_metrics = evaluate(model, test_loader, device)
        torch.save(model.state_dict(), model_dir / f"{name}.pt")
        histories[name] = history
        results[name] = {
            "val": {k: v for k, v in best_val.items() if k not in ("y_true", "y_pred", "y_prob", "classification_report")},
            "test": test_metrics,
            "history": history,
        }
        print(
            f"TEST [{name}] acc={test_metrics['accuracy']:.4f} "
            f"f1={test_metrics['f1']:.4f} auc={test_metrics['roc_auc']:.4f}"
        )
        plot_confusion(
            test_metrics["confusion_matrix"],
            f"Confusion Matrix — {name}",
            fig_dir / f"cm_{name}.png",
        )

    plot_history(histories, fig_dir / "training_curves.png")
    plot_comparison(results, fig_dir / "model_comparison.png")
    plot_roc(results, fig_dir / "roc_curves.png")

    # Compact summary table
    summary = {
        "meta": meta,
        "device": str(device),
        "epochs": args.epochs,
        "models": {},
    }
    for name, payload in results.items():
        t = payload["test"]
        summary["models"][name] = {
            "accuracy": t["accuracy"],
            "precision": t["precision"],
            "recall": t["recall"],
            "f1": t["f1"],
            "roc_auc": t["roc_auc"],
            "confusion_matrix": t["confusion_matrix"],
            "classification_report": t["classification_report"],
        }

    save_metrics(out_dir / "experiment_results.json", summary)

    # Also store full predictions for the best fusion model (for PDF)
    best_name = max(results.keys(), key=lambda n: results[n]["test"]["f1"])
    summary["best_model"] = best_name
    save_metrics(out_dir / "experiment_results.json", summary)

    print("\n===== SUMMARY (Test F1) =====")
    for name in model_names:
        print(f"  {name:16s}  F1={results[name]['test']['f1']:.4f}  Acc={results[name]['test']['accuracy']:.4f}")
    print(f"Best model: {best_name}")
    print(f"Results saved to {out_dir / 'experiment_results.json'}")
    print(f"Figures saved to {fig_dir}")


if __name__ == "__main__":
    main()
