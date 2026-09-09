"""Agentic loan-origination workflow that chains KYC, credit, fraud and AML."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aml_monitor import AmlMonitor
from credit_scoring import CreditScorer
from fraud_detection import FraudDetector
from kyc_classifier import KycClassifier


@dataclass
class AgentStep:
    name: str
    status: str
    detail: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


@dataclass
class AgentDecision:
    application_id: str
    outcome: str
    rationale: list[str]
    steps: list[AgentStep] = field(default_factory=list)
    credit: dict[str, Any] = field(default_factory=dict)
    kyc: dict[str, Any] = field(default_factory=dict)
    fraud: dict[str, Any] = field(default_factory=dict)
    aml: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "application_id": self.application_id,
            "outcome": self.outcome,
            "rationale": self.rationale,
            "steps": [step.to_dict() for step in self.steps],
            "credit": self.credit,
            "kyc": self.kyc,
            "fraud": self.fraud,
            "aml": self.aml,
        }


class LoanOriginationAgent:
    """Deterministic planner: each tool is called in order, then a policy votes."""

    def __init__(self) -> None:
        self.kyc = KycClassifier()
        self.credit = CreditScorer()
        self.fraud = FraudDetector()
        self.aml = AmlMonitor()

    def run(self, application: dict[str, Any]) -> AgentDecision:
        from settings import get_section

        cfg = get_section("agent")
        app_id = str(application.get("application_id", "APP-UNKNOWN"))
        steps: list[AgentStep] = []

        kyc_result = self.kyc.assess(application.get("kyc_text", ""))
        steps.append(AgentStep("kyc_intake", "pass" if kyc_result.accepted else "fail", kyc_result.to_dict()))

        credit_result = self.credit.predict(application)
        steps.append(AgentStep("credit_underwrite", credit_result.decision, credit_result.to_dict()))

        txn_payload = application.get("sample_transaction") or _default_txn(application)
        fraud_result = self.fraud.predict(txn_payload)
        steps.append(AgentStep("fraud_screen", fraud_result.decision, fraud_result.to_dict()))

        aml_result = self.aml.evaluate_customer(
            application.get("recent_transactions") or [txn_payload],
            str(application.get("customer_id", "CUST-001")),
        )
        steps.append(AgentStep("aml_screen", aml_result.severity, aml_result.to_dict()))

        outcome, rationale = _policy(
            kyc_result.accepted,
            credit_result.pd_score,
            credit_result.decision,
            fraud_result.label,
            aml_result.severity,
            cfg,
        )
        return AgentDecision(
            application_id=app_id,
            outcome=outcome,
            rationale=rationale,
            steps=steps,
            credit=credit_result.to_dict(),
            kyc=kyc_result.to_dict(),
            fraud=fraud_result.to_dict(),
            aml=aml_result.to_dict(),
        )


def _policy(
    kyc_ok: bool,
    pd_score: float,
    credit_decision: str,
    fraud_label: str,
    aml_severity: str,
    cfg: dict[str, Any],
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if cfg["require_kyc_pass"] and not kyc_ok:
        return "reject", ["KYC document failed automated intake."]
    if pd_score >= cfg["auto_reject_pd_min"]:
        return "reject", [f"Probability of default {pd_score:.1%} is above the cut-off."]
    if fraud_label == "high_risk" or aml_severity == "high":
        reasons.append("Financial-crime screen is elevated; human investigation is mandatory.")
        return "refer_fico", reasons
    if credit_decision == "decline":
        return "reject", ["Credit policy decline independent of crime screens."]
    if pd_score <= cfg["auto_approve_pd_max"] and fraud_label == "typical" and aml_severity in {"clear", "watch"}:
        return "approve", ["KYC passed, PD inside auto-approve band, crime screens quiet."]
    reasons.append("Mixed signals: send to credit officer with the agent memo.")
    if credit_decision == "manual_review":
        reasons.append("PD sits in the grey band.")
    if fraud_label == "review":
        reasons.append("Fraud score asked for step-up authentication.")
    return "refer_credit", reasons


def _default_txn(application: dict[str, Any]) -> dict[str, Any]:
    return {
        "amount": float(application.get("loan_amount", 50000)) * 0.02,
        "hour": 14,
        "is_international": False,
        "is_card_present": True,
        "failed_pin_attempts": 0,
        "velocity_1h": 1,
        "distance_from_home_km": 4,
        "merchant_category": "other",
        "avg_amount": 2500,
        "channel": "upi",
        "direction": "out",
        "counterparty_country": "IN",
        "hours_since_inflow": 48,
    }
