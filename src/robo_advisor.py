"""Risk-profile clustering and simple multi-asset SIP allocation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

from paths import MODELS_DIR
from settings import get_section

ASSETS = ("equity", "debt", "gold", "liquid")
EXPECTED_RETURN = {"equity": 0.12, "debt": 0.07, "gold": 0.08, "liquid": 0.06}
VOLATILITY = {"equity": 0.16, "debt": 0.04, "gold": 0.12, "liquid": 0.01}

QUESTIONS = [
    "age",
    "horizon_years",
    "monthly_surplus",
    "emergency_months",
    "loss_tolerance",
    "market_knowledge",
]


@dataclass
class Allocation:
    bucket: str
    risk_score: float
    weights: dict[str, float]
    expected_return: float
    expected_volatility: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "bucket": self.bucket,
            "risk_score": round(self.risk_score, 2),
            "weights": {key: round(value, 3) for key, value in self.weights.items()},
            "expected_return": round(self.expected_return, 4),
            "expected_volatility": round(self.expected_volatility, 4),
            "notes": self.notes,
        }


class RoboAdvisor:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or (MODELS_DIR / "robo_advisor.joblib")
        self.bundle: dict[str, Any] | None = None
        if self.model_path.exists():
            self.bundle = joblib.load(self.model_path)

    def fit(self, frame: pd.DataFrame) -> dict[str, float]:
        matrix = frame[QUESTIONS].astype(float)
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(matrix)
        model = KMeans(n_clusters=4, random_state=42, n_init=10)
        labels = model.fit_predict(scaled)
        self.bundle = {"model": model, "scaler": scaler, "centers": model.cluster_centers_}
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.bundle, self.model_path)
        return {"clusters": 4.0, "rows": float(len(frame)), "inertia": float(model.inertia_)}

    def advise(self, profile: dict[str, Any]) -> Allocation:
        cfg = get_section("robo")
        risk = _risk_score(profile)
        bucket = _bucket(risk)
        weights = _weights(bucket, cfg)
        exp_r = sum(weights[asset] * EXPECTED_RETURN[asset] for asset in ASSETS)
        exp_v = float(np.sqrt(sum((weights[asset] * VOLATILITY[asset]) ** 2 for asset in ASSETS)))
        notes = _notes(profile, bucket, weights)

        if self.bundle is not None:
            vector = pd.DataFrame([{q: float(profile.get(q, 0)) for q in QUESTIONS}])
            scaled = self.bundle["scaler"].transform(vector)
            cluster = int(self.bundle["model"].predict(scaled)[0])
            notes.append(f"Nearest historical investor cluster: {cluster}.")

        return Allocation(bucket, risk, weights, exp_r, exp_v, notes)


def _risk_score(profile: dict[str, Any]) -> float:
    age = float(profile.get("age", 35))
    horizon = float(profile.get("horizon_years", 7))
    surplus = float(profile.get("monthly_surplus", 15000))
    emergency = float(profile.get("emergency_months", 4))
    loss = float(profile.get("loss_tolerance", 3))  # 1-5
    knowledge = float(profile.get("market_knowledge", 3))
    age_term = max(0.0, (60 - age) / 40) * 25
    horizon_term = min(horizon / 15, 1.0) * 20
    surplus_term = min(surplus / 50000, 1.0) * 15
    buffer_term = min(emergency / 12, 1.0) * 10
    attitude = ((loss - 1) / 4) * 20
    know = ((knowledge - 1) / 4) * 10
    return float(np.clip(age_term + horizon_term + surplus_term + buffer_term + attitude + know, 0, 100))


def _bucket(score: float) -> str:
    if score < 30:
        return "conservative"
    if score < 50:
        return "moderate"
    if score < 72:
        return "growth"
    return "aggressive"


def _weights(bucket: str, cfg: dict[str, Any]) -> dict[str, float]:
    presets = {
        "conservative": {"equity": 0.25, "debt": 0.50, "gold": 0.10, "liquid": 0.15},
        "moderate": {"equity": 0.45, "debt": 0.35, "gold": 0.10, "liquid": 0.10},
        "growth": {"equity": 0.65, "debt": 0.20, "gold": 0.10, "liquid": 0.05},
        "aggressive": {"equity": 0.80, "debt": 0.10, "gold": 0.05, "liquid": 0.05},
    }
    weights = presets[bucket].copy()
    weights["equity"] = min(weights["equity"], cfg["equity_cap"])
    weights["debt"] = max(weights["debt"], cfg["debt_floor"] if bucket == "conservative" else weights["debt"])
    weights["gold"] = min(weights["gold"], cfg["gold_cap"])
    weights["liquid"] = max(weights["liquid"], cfg["liquid_floor"])
    total = sum(weights.values())
    return {key: value / total for key, value in weights.items()}


def _notes(profile: dict[str, Any], bucket: str, weights: dict[str, float]) -> list[str]:
    notes = [
        f"Mapped to the {bucket} sleeve from the risk questionnaire.",
        f"Equity share {weights['equity']:.0%} is capped by policy for this sleeve.",
    ]
    if float(profile.get("emergency_months", 4)) < 3:
        notes.append("Emergency corpus is thin; liquid sleeve is kept at the floor.")
    if float(profile.get("age", 35)) >= 55:
        notes.append("Age suggests a shorter recovery window; debt is emphasised.")
    notes.append("Illustrative long-run assumptions, not a guaranteed return.")
    return notes
