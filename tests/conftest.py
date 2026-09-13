"""Train artifacts before test collection so API module imports succeed."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DATASET = ROOT / "dataset"
MODELS = ROOT / "models"


def pytest_configure(config) -> None:  # noqa: ARG001
    if not (DATASET / "transactions.csv").exists():
        subprocess.check_call([sys.executable, str(DATASET / "generate_data.py")], cwd=ROOT)
    if not (MODELS / "credit_scorer.joblib").exists():
        subprocess.check_call([sys.executable, str(SRC / "train_models.py")], cwd=ROOT)
