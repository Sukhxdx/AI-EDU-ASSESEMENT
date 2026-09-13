"""Resolved locations for datasets, models, and configuration."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "dataset"
MODELS_DIR = ROOT / "models"
CONFIG_PATH = ROOT / "config" / "settings.yaml"
