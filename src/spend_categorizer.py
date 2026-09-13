"""Merchant-description spend categorisation for personal finance insights."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from paths import MODELS_DIR
from settings import get_section


@dataclass
class SpendInsight:
    category: str
    confidence: float
    monthly_total: float | None = None
    budget_flag: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "confidence": round(self.confidence, 4),
            "monthly_total": self.monthly_total,
            "budget_flag": self.budget_flag,
        }


class SpendCategorizer:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or (MODELS_DIR / "spend_categorizer.joblib")
        self.pipeline: Pipeline | None = None
        if self.model_path.exists():
            self.pipeline = joblib.load(self.model_path)

    def fit(self, frame: pd.DataFrame) -> dict[str, float]:
        x_train, x_test, y_train, y_test = train_test_split(
            frame["description"],
            frame["category"],
            test_size=0.2,
            random_state=42,
            stratify=frame["category"],
        )
        pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)),
                ("clf", LogisticRegression(max_iter=400, class_weight="balanced")),
            ]
        )
        pipeline.fit(x_train, y_train)
        accuracy = float(accuracy_score(y_test, pipeline.predict(x_test)))
        self.pipeline = pipeline
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, self.model_path)
        return {"accuracy": accuracy, "categories": float(frame["category"].nunique())}

    def classify(self, description: str) -> SpendInsight:
        if self.pipeline is None:
            raise RuntimeError("Spend model is not trained. Run python src/train_models.py")
        proba = self.pipeline.predict_proba([description])[0]
        classes = list(self.pipeline.classes_)
        category, confidence = max(zip(classes, proba), key=lambda item: item[1])
        return SpendInsight(category, float(confidence))

    def summarise(self, frame: pd.DataFrame) -> pd.DataFrame:
        if self.pipeline is None:
            raise RuntimeError("Spend model is not trained. Run python src/train_models.py")
        work = frame.copy()
        work["category"] = self.pipeline.predict(work["description"])
        grouped = work.groupby("category", as_index=False)["amount"].sum()
        grouped = grouped.sort_values("amount", ascending=False)
        total = grouped["amount"].sum()
        share_cut = get_section("spend")["budget_alert_share"]
        grouped["share"] = grouped["amount"] / max(total, 1)
        grouped["budget_flag"] = grouped["share"] >= share_cut
        return grouped
