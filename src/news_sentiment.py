"""Financial news tone scoring for a lightweight market-pulse feed."""

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

POSITIVE = {
    "rally",
    "surge", "surges", "gain", "gains", "profit", "profits", "upgrade",
    "beat", "beats", "record", "strong", "growth", "expand", "expansion",
    "inflow", "inflows", "cut rates", "rate cut", "stable", "surplus",
}
NEGATIVE = {
    "crash", "fall", "falls", "slump", "loss", "losses", "downgrade",
    "miss", "misses", "weak", "fraud", "default", "npa", "inflation",
    "hike", "outflow", "outflows", "recession", "probe", "penalty",
    "volatile", "warning", "slowdown",
}


@dataclass
class SentimentResult:
    label: str
    confidence: float
    lexicon_score: float
    headline: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "confidence": round(self.confidence, 4),
            "lexicon_score": round(self.lexicon_score, 4),
            "headline": self.headline,
        }


class NewsSentiment:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or (MODELS_DIR / "news_sentiment.joblib")
        self.pipeline: Pipeline | None = None
        if self.model_path.exists():
            self.pipeline = joblib.load(self.model_path)

    def fit(self, frame: pd.DataFrame) -> dict[str, float]:
        x_train, x_test, y_train, y_test = train_test_split(
            frame["headline"],
            frame["label"],
            test_size=0.25,
            random_state=42,
            stratify=frame["label"],
        )
        pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=4000)),
                ("clf", LogisticRegression(max_iter=400, class_weight="balanced")),
            ]
        )
        pipeline.fit(x_train, y_train)
        accuracy = float(accuracy_score(y_test, pipeline.predict(x_test)))
        self.pipeline = pipeline
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, self.model_path)
        return {"accuracy": accuracy, "rows": float(len(frame))}

    def score(self, headline: str) -> SentimentResult:
        if self.pipeline is None:
            raise RuntimeError("Sentiment model is not trained. Run python src/train_models.py")
        proba = self.pipeline.predict_proba([headline])[0]
        classes = list(self.pipeline.classes_)
        label, confidence = max(zip(classes, proba), key=lambda item: item[1])
        lexicon = lexicon_score(headline)
        cfg = get_section("sentiment")
        if abs(lexicon) >= 0.4 and label == "neutral":
            label = "positive" if lexicon > cfg["positive_cut"] else "negative"
        return SentimentResult(label, float(confidence), lexicon, headline)

    def score_many(self, headlines: list[str]) -> list[SentimentResult]:
        return [self.score(item) for item in headlines]


def lexicon_score(text: str) -> float:
    tokens = text.lower()
    pos = sum(1 for word in POSITIVE if word in tokens)
    neg = sum(1 for word in NEGATIVE if word in tokens)
    if pos + neg == 0:
        return 0.0
    return (pos - neg) / (pos + neg)
