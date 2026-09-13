"""Banking customer copilot: TF-IDF intent classifier plus templated replies."""

from __future__ import annotations

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

REPLIES = {
    "greeting": "Hello. I am the NexusBank assistant. I can help with cards, transfers, KYC, loans and fraud alerts.",
    "balance_inquiry": "Your ledger balance is available in the mobile app under Accounts. I can also raise a mini-statement request if you share the last four digits.",
    "mini_statement": "I have queued a five-transaction mini-statement. It will arrive on your registered SMS and email within a few minutes.",
    "fund_transfer": "IMPS and UPI transfers are instant within limits. NEFT runs in half-hourly batches. Confirm the beneficiary IFSC before you send.",
    "card_block": "I can hot-list the card immediately. After blocking, set up a replacement from Cards > Manage. Pending e-commerce authorisations will be reversed.",
    "card_unblock": "Unblocking needs a one-time OTP on the registered mobile number. If the card was blocked for fraud, a branch officer must clear it.",
    "pin_reset": "PIN reset is allowed after OTP plus debit-card CVV. Never share the PIN with callers claiming to be the bank.",
    "loan_inquiry": "I can check personal-loan eligibility and EMI. Typical processing is one working day after KYC and bureau pull.",
    "emi_help": "Use the EMI calculator in Loans, or type tenure and amount. Prepayment of floating-rate personal loans has no foreclosure fee after 12 months.",
    "kyc_update": "Re-KYC accepts Aadhaar XML, PAN and a current address proof. Upload from Profile > KYC. Video KYC slots open 8:00–20:00.",
    "fraud_report": "I am raising a fraud incident. Please confirm the amount, channel and approximate time. The card will be blocked as a precaution.",
    "investment_advice": "The robo-advisor module can map a SIP mix to your risk score. Mutual fund investments are subject to market risk.",
    "complaint": "I have opened a service request. You will receive a ticket ID by SMS. Banking ombudsman timelines apply if it stays unresolved.",
    "branch_locator": "Share your PIN code and I will list the nearest branch and cash-deposit machine. Most metro branches follow 10:00–16:00 hours.",
    "goodbye": "Thank you for banking with NexusBank. Stay alert to phishing links and never share OTP.",
    "fallback": "I did not catch that. Try phrases like 'block my card', 'update KYC', or 'personal loan EMI'.",
}


@dataclass
class ChatReply:
    intent: str
    confidence: float
    reply: str
    needs_handoff: bool = False
    alternatives: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "confidence": round(self.confidence, 4),
            "reply": self.reply,
            "needs_handoff": self.needs_handoff,
            "alternatives": self.alternatives,
        }


class BankingChatbot:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or (MODELS_DIR / "chatbot.joblib")
        self.pipeline: Pipeline | None = None
        if self.model_path.exists():
            self.pipeline = joblib.load(self.model_path)

    def fit(self, frame: pd.DataFrame) -> dict[str, float]:
        x_train, x_test, y_train, y_test = train_test_split(
            frame["text"],
            frame["intent"],
            test_size=0.2,
            random_state=42,
            stratify=frame["intent"],
        )
        pipeline = Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(
                        lowercase=True,
                        ngram_range=(1, 2),
                        min_df=1,
                        max_features=4000,
                    ),
                ),
                (
                    "clf",
                    LogisticRegression(max_iter=500),
                ),
            ]
        )
        pipeline.fit(x_train, y_train)
        accuracy = float(accuracy_score(y_test, pipeline.predict(x_test)))
        self.pipeline = pipeline
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, self.model_path)
        return {"accuracy": accuracy, "intents": float(frame["intent"].nunique())}

    def respond(self, text: str) -> ChatReply:
        if self.pipeline is None:
            raise RuntimeError("Chatbot model is not trained. Run python src/train_models.py")

        cfg = get_section("chatbot")
        proba = self.pipeline.predict_proba([text])[0]
        classes = list(self.pipeline.classes_)
        ranked = sorted(zip(classes, proba), key=lambda item: item[1], reverse=True)
        intent, confidence = ranked[0]
        alternatives = [name for name, score in ranked[1:4] if score > 0.08]
        confidence = float(confidence)

        if intent == cfg["fallback_intent"] or confidence < cfg["confidence_min"]:
            intent = cfg["fallback_intent"]
            reply = REPLIES[intent]
            return ChatReply(intent, confidence, reply, needs_handoff=True, alternatives=alternatives)

        reply = REPLIES.get(intent, REPLIES["fallback"])
        handoff = intent in {"fraud_report", "complaint"}
        return ChatReply(intent, float(confidence), reply, needs_handoff=handoff, alternatives=alternatives)
