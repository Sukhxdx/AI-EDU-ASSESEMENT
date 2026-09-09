"""Transaction fraud scoring with Isolation Forest plus explainable rules.

The unsupervised model learns a typical spend envelope from historical
card and UPI activity. Rule overlays surface human-readable reasons so
operations staff can act without treating the model as a black box.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from paths import MODELS_DIR
from settings import get_section

FEATURE_COLUMNS = [
    "amount",
    "hour",
    "is_international",
    "is_card_present",
    "failed_pin_attempts",
    "velocity_1h",
    "distance_from_home_km",
    "merchant_risk",
    "amount_to_avg_ratio",
]

MERCHANT_RISK = {
    "grocery": 0.05,
    "fuel": 0.08,
    "utilities": 0.06,
    "dining": 0.12,
    "shopping": 0.18,
    "travel": 0.25,
    "electronics": 0.32,
    "crypto": 0.92,
    "gambling": 0.88,
    "jewelry": 0.55,
    "atm_cash": 0.40,
    "other": 0.20,
}


@dataclass
class FraudResult:
    risk_score: float
    label: str
    decision: str
    reasons: list[str] = field(default_factory=list)
    model_anomaly: float = 0.0
    features: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_score": round(self.risk_score, 2),
            "label": self.label,
            "decision": self.decision,
            "reasons": self.reasons,
            "model_anomaly": round(self.model_anomaly, 4),
            "features": self.features,
        }


class FraudDetector:
    """Score a single transaction or a batch of rows."""

    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or (MODELS_DIR / "fraud_detector.joblib")
        self.bundle: dict[str, Any] | None = None
        if self.model_path.exists():
            self.bundle = joblib.load(self.model_path)

    def fit(self, frame: pd.DataFrame) -> dict[str, float]:
        cfg = get_section("fraud")
        work = _prepare_features(frame)
        scaler = StandardScaler()
        matrix = scaler.fit_transform(work[FEATURE_COLUMNS])
        model = IsolationForest(
            n_estimators=180,
            contamination=cfg["contamination"],
            random_state=42,
            n_jobs=-1,
        )
        model.fit(matrix)
        self.bundle = {"model": model, "scaler": scaler, "features": FEATURE_COLUMNS}
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.bundle, self.model_path)

        preds = model.predict(matrix)
        flagged = float((preds == -1).mean())
        return {"flag_rate": flagged, "rows": float(len(work))}

    def predict(self, record: dict[str, Any]) -> FraudResult:
        if self.bundle is None:
            raise RuntimeError("Fraud model is not trained. Run python src/train_models.py")

        cfg = get_section("fraud")
        row = _record_to_row(record)
        features = {name: float(row[name]) for name in FEATURE_COLUMNS}
        matrix = self.bundle["scaler"].transform(pd.DataFrame([features])[FEATURE_COLUMNS])
        raw = float(self.bundle["model"].decision_function(matrix)[0])
        # Isolation Forest: lower decision_function => more anomalous.
        anomaly = float(1.0 / (1.0 + np.exp(4.0 * raw)))
        reasons = _rule_reasons(row, cfg)
        rule_boost = min(0.35, 0.08 * len(reasons))
        risk = 100.0 * min(1.0, anomaly + rule_boost)

        if risk >= cfg["high_risk_score"]:
            label, decision = "high_risk", "block_and_alert"
        elif risk >= cfg["review_score"]:
            label, decision = "review", "step_up_auth"
        else:
            label, decision = "typical", "allow"

        if not reasons:
            reasons = ["No rule breach; score driven by historical anomaly pattern."]

        return FraudResult(
            risk_score=risk,
            label=label,
            decision=decision,
            reasons=reasons,
            model_anomaly=anomaly,
            features=features,
        )

    def predict_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        results = [self.predict(row.to_dict()) for _, row in frame.iterrows()]
        scored = frame.copy()
        scored["risk_score"] = [item.risk_score for item in results]
        scored["fraud_label"] = [item.label for item in results]
        scored["fraud_decision"] = [item.decision for item in results]
        return scored


def _prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    work = frame.copy()
    work["merchant_risk"] = work["merchant_category"].map(MERCHANT_RISK).fillna(0.20)
    work["is_international"] = work["is_international"].astype(float)
    work["is_card_present"] = work["is_card_present"].astype(float)
    avg = work["avg_amount"].replace(0, 1.0)
    work["amount_to_avg_ratio"] = work["amount"] / avg
    return work


def _record_to_row(record: dict[str, Any]) -> pd.Series:
    merchant = str(record.get("merchant_category", "other"))
    amount = float(record.get("amount", 0))
    avg = float(record.get("avg_amount", max(amount, 1.0)))
    return pd.Series(
        {
            "amount": amount,
            "hour": int(record.get("hour", 12)),
            "is_international": int(bool(record.get("is_international", False))),
            "is_card_present": int(bool(record.get("is_card_present", True))),
            "failed_pin_attempts": int(record.get("failed_pin_attempts", 0)),
            "velocity_1h": int(record.get("velocity_1h", 1)),
            "distance_from_home_km": float(record.get("distance_from_home_km", 3.0)),
            "merchant_risk": MERCHANT_RISK.get(merchant, 0.20),
            "amount_to_avg_ratio": amount / max(avg, 1.0),
        }
    )


def _rule_reasons(row: pd.Series, cfg: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    night = int(row["hour"]) in cfg["night_hours"]
    if night and row["is_international"]:
        reasons.append("Night-time international card use.")
    if row["amount"] >= cfg["international_amount_flag"] and row["is_international"]:
        reasons.append("Large cross-border amount relative to policy threshold.")
    if row["velocity_1h"] >= cfg["velocity_flag"]:
        reasons.append(f"High velocity: {int(row['velocity_1h'])} attempts in one hour.")
    if row["failed_pin_attempts"] >= 3:
        reasons.append("Repeated PIN failures before this authorisation.")
    if row["distance_from_home_km"] >= 400 and not row["is_card_present"]:
        reasons.append("Card-not-present spend far from the customer's usual location.")
    if row["merchant_risk"] >= 0.8:
        reasons.append("Merchant category is on the enhanced-risk list.")
    if row["amount_to_avg_ratio"] >= 6:
        reasons.append("Amount is several times the customer's typical ticket size.")
    return reasons
