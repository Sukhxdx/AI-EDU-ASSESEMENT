"""Train every NexusBank model from the CSV files in dataset/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aml_monitor import AmlMonitor  # noqa: E402
from banking_chatbot import BankingChatbot  # noqa: E402
from credit_scoring import CreditScorer  # noqa: E402
from fraud_detection import FraudDetector  # noqa: E402
from kyc_classifier import KycClassifier  # noqa: E402
from news_sentiment import NewsSentiment  # noqa: E402
from paths import DATASET_DIR, MODELS_DIR, ROOT as PROJECT_ROOT  # noqa: E402
from robo_advisor import RoboAdvisor  # noqa: E402
from spend_categorizer import SpendCategorizer  # noqa: E402


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    metrics: dict[str, dict[str, float]] = {}

    fraud = FraudDetector()
    metrics["fraud"] = fraud.fit(pd.read_csv(DATASET_DIR / "transactions.csv"))

    credit = CreditScorer()
    metrics["credit"] = credit.fit(pd.read_csv(DATASET_DIR / "loan_applications.csv"))

    chat = BankingChatbot()
    metrics["chatbot"] = chat.fit(pd.read_csv(DATASET_DIR / "customer_queries.csv"))

    kyc = KycClassifier()
    metrics["kyc"] = kyc.fit(pd.read_csv(DATASET_DIR / "kyc_documents.csv"))

    spend = SpendCategorizer()
    metrics["spend"] = spend.fit(pd.read_csv(DATASET_DIR / "spend_merchants.csv"))

    news = NewsSentiment()
    metrics["sentiment"] = news.fit(pd.read_csv(DATASET_DIR / "news_headlines.csv"))

    robo = RoboAdvisor()
    metrics["robo"] = robo.fit(pd.read_csv(DATASET_DIR / "investor_profiles.csv"))

    aml = AmlMonitor()
    alerts = aml.evaluate_batch(pd.read_csv(DATASET_DIR / "aml_ledger.csv"))
    metrics["aml"] = {key: float(value) for key, value in aml.summary(alerts).items()}

    out = PROJECT_ROOT / "models" / "training_metrics.json"
    out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Models saved under {MODELS_DIR}")


if __name__ == "__main__":
    main()
