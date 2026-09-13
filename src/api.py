"""FastAPI surface for every NexusBank intelligence module."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aml_monitor import AmlMonitor
from banking_chatbot import BankingChatbot
from credit_scoring import CreditScorer
from fraud_detection import FraudDetector
from kyc_classifier import KycClassifier
from loan_agent import LoanOriginationAgent
from news_sentiment import NewsSentiment
from robo_advisor import RoboAdvisor
from settings import load_settings
from spend_categorizer import SpendCategorizer

app = FastAPI(
    title="NexusBank AI",
    description="AI modules for fraud, credit, AML, KYC, NLP and wealth.",
    version=load_settings()["app"]["version"],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

fraud_model = FraudDetector()
credit_model = CreditScorer()
chat_model = BankingChatbot()
kyc_model = KycClassifier()
spend_model = SpendCategorizer()
news_model = NewsSentiment()
robo_model = RoboAdvisor()
aml_model = AmlMonitor()
agent = LoanOriginationAgent()


class FraudRequest(BaseModel):
    amount: float
    hour: int = 12
    merchant_category: str = "shopping"
    is_international: bool = False
    is_card_present: bool = True
    failed_pin_attempts: int = 0
    velocity_1h: int = 1
    distance_from_home_km: float = 5
    avg_amount: float = 2000


class CreditRequest(BaseModel):
    age: int = 30
    annual_income: float
    employment_years: float = 4
    existing_debt: float = 0
    loan_amount: float
    loan_term_months: int = 36
    credit_history_years: float = 5
    late_payments_24m: int = 0
    credit_utilization: float = 0.3
    dependents: int = 0


class TextRequest(BaseModel):
    text: str = Field(min_length=1)


class AmlTxn(BaseModel):
    amount: float
    counterparty_country: str = "IN"
    channel: str = "upi"
    direction: str = "out"
    hours_since_inflow: float = 24


class AmlRequest(BaseModel):
    customer_id: str = "CUST001"
    transactions: list[AmlTxn]


class SpendRow(BaseModel):
    description: str
    amount: float


class RoboRequest(BaseModel):
    age: int = 32
    horizon_years: int = 8
    monthly_surplus: float = 20000
    emergency_months: float = 6
    loss_tolerance: int = 3
    market_knowledge: int = 3


class AgentRequest(BaseModel):
    application_id: str = "APP-1001"
    customer_id: str = "CUST001"
    kyc_text: str
    age: int = 31
    annual_income: float = 900000
    employment_years: float = 5
    existing_debt: float = 120000
    loan_amount: float = 400000
    loan_term_months: int = 36
    credit_history_years: float = 6
    late_payments_24m: int = 0
    credit_utilization: float = 0.25
    dependents: int = 1
    sample_transaction: dict[str, Any] | None = None
    recent_transactions: list[dict[str, Any]] | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "NexusBank AI"}


@app.post("/fraud/score")
def score_fraud(body: FraudRequest) -> dict[str, Any]:
    try:
        return fraud_model.predict(body.model_dump()).to_dict()
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/credit/score")
def score_credit(body: CreditRequest) -> dict[str, Any]:
    try:
        return credit_model.predict(body.model_dump()).to_dict()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/chat")
def chat(body: TextRequest) -> dict[str, Any]:
    return chat_model.respond(body.text).to_dict()


@app.post("/kyc/assess")
def kyc(body: TextRequest) -> dict[str, Any]:
    return kyc_model.assess(body.text).to_dict()


@app.post("/aml/evaluate")
def aml(body: AmlRequest) -> dict[str, Any]:
    payload = [item.model_dump() for item in body.transactions]
    return aml_model.evaluate_customer(payload, body.customer_id).to_dict()


@app.post("/spend/classify")
def spend_one(body: TextRequest) -> dict[str, Any]:
    return spend_model.classify(body.text).to_dict()


@app.post("/spend/summarise")
def spend_sum(rows: list[SpendRow]) -> list[dict[str, Any]]:
    import pandas as pd

    frame = pd.DataFrame([row.model_dump() for row in rows])
    return spend_model.summarise(frame).to_dict(orient="records")


@app.post("/news/sentiment")
def news(body: TextRequest) -> dict[str, Any]:
    return news_model.score(body.text).to_dict()


@app.post("/wealth/advise")
def wealth(body: RoboRequest) -> dict[str, Any]:
    return robo_model.advise(body.model_dump()).to_dict()


@app.post("/agent/originate")
def originate(body: AgentRequest) -> dict[str, Any]:
    return agent.run(body.model_dump()).to_dict()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
