"""KYC document typing and light field extraction for Indian IDs."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
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

PAN_RE = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
AADHAAR_RE = re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b")
PASSPORT_RE = re.compile(r"\b[A-Z][0-9]{7}\b")
DL_RE = re.compile(r"\b[A-Z]{2}[-\s]?[0-9]{2}[-\s]?[0-9]{4}[-\s]?[0-9]{7}\b")


@dataclass
class KycResult:
    doc_type: str
    confidence: float
    accepted: bool
    fields: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_type": self.doc_type,
            "confidence": round(self.confidence, 4),
            "accepted": self.accepted,
            "fields": self.fields,
            "notes": self.notes,
        }


class KycClassifier:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or (MODELS_DIR / "kyc_classifier.joblib")
        self.pipeline: Pipeline | None = None
        if self.model_path.exists():
            self.pipeline = joblib.load(self.model_path)

    def fit(self, frame: pd.DataFrame) -> dict[str, float]:
        x_train, x_test, y_train, y_test = train_test_split(
            frame["text"],
            frame["doc_type"],
            test_size=0.25,
            random_state=42,
            stratify=frame["doc_type"],
        )
        pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=3000)),
                ("clf", LogisticRegression(max_iter=400, class_weight="balanced")),
            ]
        )
        pipeline.fit(x_train, y_train)
        accuracy = float(accuracy_score(y_test, pipeline.predict(x_test)))
        self.pipeline = pipeline
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, self.model_path)
        return {"accuracy": accuracy, "classes": float(frame["doc_type"].nunique())}

    def assess(self, text: str) -> KycResult:
        if self.pipeline is None:
            raise RuntimeError("KYC model is not trained. Run python src/train_models.py")

        cfg = get_section("kyc")
        proba = self.pipeline.predict_proba([text])[0]
        classes = list(self.pipeline.classes_)
        doc_type, confidence = max(zip(classes, proba), key=lambda item: item[1])
        fields = extract_fields(text)
        notes: list[str] = []
        accepted = bool(
            doc_type in cfg["accept_types"] and confidence >= cfg["min_confidence"]
        )

        if doc_type == "pan" and "pan" not in fields:
            notes.append("PAN pattern was not found in the OCR text.")
            accepted = False
        if doc_type == "aadhaar" and "aadhaar" not in fields:
            notes.append("Aadhaar number pattern missing; ask for a clearer scan.")
            accepted = False
        if doc_type == "utility_bill":
            notes.append("Utility bills support address only; pair with PAN or Aadhaar.")
            accepted = False
        if confidence < cfg["min_confidence"]:
            notes.append("Classifier confidence is below the onboarding threshold.")
            accepted = False
        if accepted and not notes:
            notes.append("Document type is accepted for digital KYC.")

        return KycResult(doc_type, float(confidence), accepted, fields, notes)


def extract_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    pan = PAN_RE.search(text.upper())
    if pan:
        fields["pan"] = pan.group(0)
    aadhaar = AADHAAR_RE.search(text)
    if aadhaar:
        fields["aadhaar"] = aadhaar.group(0)
    passport = PASSPORT_RE.search(text.upper())
    if passport:
        fields["passport"] = passport.group(0)
    driving = DL_RE.search(text.upper())
    if driving:
        fields["driving_license"] = driving.group(0).replace(" ", "")
    return fields
