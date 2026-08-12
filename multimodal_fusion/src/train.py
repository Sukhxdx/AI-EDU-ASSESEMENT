"""Training and evaluation utilities for multimodal fusion models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from torch.utils.data import DataLoader
from tqdm import tqdm


def collate_fn(batch):
    images = torch.stack([b[0] for b in batch])
    tokens = torch.stack([b[1] for b in batch])
    labels = torch.stack([b[2] for b in batch])
    texts = [b[3] for b in batch]
    return images, tokens, labels, texts


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
) -> Dict[str, float]:
    model.eval()
    all_preds: List[int] = []
    all_labels: List[int] = []
    all_probs: List[float] = []
    total_loss = 0.0
    criterion = nn.CrossEntropyLoss()

    for images, tokens, labels, _ in loader:
        images = images.to(device)
        tokens = tokens.to(device)
        labels = labels.to(device)
        logits = model(images, tokens)
        loss = criterion(logits, labels)
        total_loss += loss.item() * labels.size(0)
        probs = torch.softmax(logits, dim=-1)[:, 1]
        preds = logits.argmax(dim=-1)
        all_preds.extend(preds.cpu().tolist())
        all_labels.extend(labels.cpu().tolist())
        all_probs.extend(probs.cpu().tolist())

    n = max(len(all_labels), 1)
    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)
    y_prob = np.array(all_probs)

    metrics = {
        "loss": total_loss / n,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    try:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
    except ValueError:
        metrics["roc_auc"] = 0.0

    metrics["confusion_matrix"] = confusion_matrix(y_true, y_pred).tolist()
    metrics["classification_report"] = classification_report(
        y_true, y_pred, target_names=["real", "fake"], zero_division=0
    )
    metrics["y_true"] = y_true.tolist()
    metrics["y_pred"] = y_pred.tolist()
    metrics["y_prob"] = y_prob.tolist()
    return metrics


def train_one_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    device: torch.device,
    epochs: int = 8,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    patience: int = 3,
) -> Tuple[nn.Module, List[dict], dict]:
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss()
    history: List[dict] = []
    best_f1 = -1.0
    best_state = None
    wait = 0

    for epoch in range(1, epochs + 1):
        model.train()
        running = 0.0
        n_seen = 0
        pbar = tqdm(train_loader, desc=f"{getattr(model, 'name', 'model')} epoch {epoch}", leave=False)
        for images, tokens, labels, _ in pbar:
            images = images.to(device)
            tokens = tokens.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            logits = model(images, tokens)
            loss = criterion(logits, labels)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            running += loss.item() * labels.size(0)
            n_seen += labels.size(0)
            pbar.set_postfix(loss=f"{loss.item():.3f}")

        train_loss = running / max(n_seen, 1)
        val_metrics = evaluate(model, val_loader, device)
        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_metrics["loss"],
            "val_accuracy": val_metrics["accuracy"],
            "val_f1": val_metrics["f1"],
            "val_roc_auc": val_metrics["roc_auc"],
        }
        history.append(row)
        print(
            f"  [{getattr(model, 'name', 'model')}] epoch {epoch}: "
            f"train_loss={train_loss:.4f} val_acc={val_metrics['accuracy']:.4f} "
            f"val_f1={val_metrics['f1']:.4f}"
        )

        if val_metrics["f1"] > best_f1:
            best_f1 = val_metrics["f1"]
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            wait = 0
        else:
            wait += 1
            if wait >= patience:
                print(f"  Early stopping at epoch {epoch}")
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    best_val = evaluate(model, val_loader, device)
    return model, history, best_val


def save_metrics(path: Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def _sanitize(obj):
        if isinstance(obj, dict):
            return {k: _sanitize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_sanitize(v) for v in obj]
        if isinstance(obj, (np.floating, float)):
            return float(obj)
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    with open(path, "w", encoding="utf-8") as f:
        json.dump(_sanitize(payload), f, indent=2)
