"""Supervised credit underwriting: probability of default and grade."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from paths import MODELS_DIR
from settings import get_section

FEATURE_COLUMNS = [
    "age",
    "annual_income",
    "employment_years",
    "existing_debt",
    "loan_amount",
    "loan_term_months",
    "credit_history_years",
    "late_payments_24m",
    "credit_utilization",
    "dependents",
    "dti",
    "loan_to_income",
]


@dataclass
class CreditResult:
    pd_score: float
    grade: str
    decision: str
    reasons: list[str] = field(default_factory=list)
    feature_contributions: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pd_score": round(self.pd_score, 4),
            "grade": self.grade,
            "decision": self.decision,
            "reasons": self.reasons,
            "feature_contributions": {
                key: round(value, 4) for key, value in self.feature_contributions.items()
            },
        }


class CreditScorer:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or (MODELS_DIR / "credit_scorer.joblib")
        self.bundle: dict[str, Any] | None = None
        if self.model_path.exists():
            self.bundle = joblib.load(self.model_path)

    def fit(self, frame: pd.DataFrame) -> dict[str, float]:
        work = _enrich(frame)
        x_train, x_test, y_train, y_test = train_test_split(
            work[FEATURE_COLUMNS],
            work["defaulted"],
            test_size=0.25,
            random_state=42,
            stratify=work["defaulted"],
        )
        scaler = StandardScaler()
        model = GradientBoostingClassifier(
            n_estimators=140,
            max_depth=3,
            learning_rate=0.08,
            random_state=42,
        )
        model.fit(scaler.fit_transform(x_train), y_train, sample_weight=_sample_weights(y_train))
        proba = model.predict_proba(scaler.transform(x_test))[:, 1]
        auc = float(roc_auc_score(y_test, proba))
        self.bundle = {
            "model": model,
            "scaler": scaler,
            "features": FEATURE_COLUMNS,
            "importances": dict(zip(FEATURE_COLUMNS, model.feature_importances_)),
        }
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.bundle, self.model_path)
        return {"auc": auc, "rows": float(len(work)), "default_rate": float(work["defaulted"].mean())}

    def predict(self, record: dict[str, Any]) -> CreditResult:
        if self.bundle is None:
            raise RuntimeError("Credit model is not trained. Run python src/train_models.py")

        cfg = get_section("credit")
        row = _record_to_row(record)
        features = {name: float(row[name]) for name in FEATURE_COLUMNS}
        matrix = self.bundle["scaler"].transform(pd.DataFrame([features])[FEATURE_COLUMNS])
        pd_score = float(self.bundle["model"].predict_proba(matrix)[0, 1])
        grade = _grade(pd_score, cfg["grades"])
        decision = _decision(pd_score, cfg)
        reasons = _reasons(row, pd_score, cfg)
        importances = self.bundle["importances"]
        contributions = {
            name: float(importances[name] * features[name])
            for name in sorted(importances, key=importances.get, reverse=True)[:6]
        }
        return CreditResult(
            pd_score=pd_score,
            grade=grade,
            decision=decision,
            reasons=reasons,
            feature_contributions=contributions,
        )


def _sample_weights(y: pd.Series) -> np.ndarray:
    pos = float((y == 1).mean())
    pos = min(max(pos, 0.02), 0.5)
    weights = np.where(y.to_numpy() == 1, 0.5 / pos, 0.5 / (1.0 - pos))
    return weights


def _enrich(frame: pd.DataFrame) -> pd.DataFrame:
    work = frame.copy()
    work["dti"] = work["existing_debt"] / work["annual_income"].clip(lower=1)
    work["loan_to_income"] = work["loan_amount"] / work["annual_income"].clip(lower=1)
    return work


def _record_to_row(record: dict[str, Any]) -> pd.Series:
    income = float(record.get("annual_income", 500000))
    debt = float(record.get("existing_debt", 0))
    amount = float(record.get("loan_amount", 200000))
    return pd.Series(
        {
            "age": float(record.get("age", 32)),
            "annual_income": income,
            "employment_years": float(record.get("employment_years", 4)),
            "existing_debt": debt,
            "loan_amount": amount,
            "loan_term_months": float(record.get("loan_term_months", 36)),
            "credit_history_years": float(record.get("credit_history_years", 5)),
            "late_payments_24m": float(record.get("late_payments_24m", 0)),
            "credit_utilization": float(record.get("credit_utilization", 0.3)),
            "dependents": float(record.get("dependents", 1)),
            "dti": debt / max(income, 1.0),
            "loan_to_income": amount / max(income, 1.0),
        }
    )


def _grade(pd_score: float, grades: dict[str, float]) -> str:
    for letter, cutoff in grades.items():
        if pd_score <= cutoff:
            return letter
    return "E"


def _decision(pd_score: float, cfg: dict[str, Any]) -> str:
    if pd_score <= cfg["approve_pd_max"]:
        return "approve"
    if pd_score <= cfg["review_pd_max"]:
        return "manual_review"
    return "decline"


def _reasons(row: pd.Series, pd_score: float, cfg: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    if row["dti"] > cfg["max_dti"]:
        notes.append(f"Debt-to-income {row['dti']:.0%} exceeds policy cap {cfg['max_dti']:.0%}.")
    if row["late_payments_24m"] >= 3:
        notes.append("Repeated delinquencies in the last 24 months.")
    if row["credit_utilization"] >= 0.7:
        notes.append("Revolving utilisation is elevated.")
    if row["loan_to_income"] >= 1.2:
        notes.append("Requested ticket is large relative to stated income.")
    if row["employment_years"] < 1:
        notes.append("Short employment tenure.")
    if not notes:
        if pd_score <= cfg["approve_pd_max"]:
            notes.append("Income, leverage and repayment history sit inside policy.")
        else:
            notes.append("Model PD is above the auto-approve band; refer to credit policy.")
    return notes
