from loan_agent import LoanOriginationAgent
from robo_advisor import RoboAdvisor


PAN_TEXT = (
    "INCOME TAX DEPARTMENT GOVT OF INDIA Permanent Account Number Card ABCDE1234F "
    "Name RAHUL SHARMA Father's Name VIJAY SHARMA Date of Birth 12/03/1992"
)


def _base_application(**overrides):
    payload = {
        "application_id": "APP-T1",
        "customer_id": "CUST001",
        "kyc_text": PAN_TEXT,
        "age": 34,
        "annual_income": 1400000,
        "employment_years": 8,
        "existing_debt": 90000,
        "loan_amount": 280000,
        "loan_term_months": 24,
        "credit_history_years": 9,
        "late_payments_24m": 0,
        "credit_utilization": 0.2,
        "dependents": 1,
    }
    payload.update(overrides)
    return payload


def test_clean_file_can_auto_approve():
    decision = LoanOriginationAgent().run(_base_application())
    assert decision.outcome in {"approve", "refer_credit"}
    assert decision.kyc["accepted"] is True
    assert len(decision.steps) == 4


def test_failed_kyc_is_rejected():
    decision = LoanOriginationAgent().run(_base_application(kyc_text="parking ticket slot B4 amount 40"))
    assert decision.outcome == "reject"
    assert "KYC" in decision.rationale[0]


def test_high_fraud_is_referred_to_fico():
    txn = {
        "amount": 99000,
        "hour": 3,
        "merchant_category": "crypto",
        "is_international": True,
        "is_card_present": False,
        "failed_pin_attempts": 4,
        "velocity_1h": 10,
        "distance_from_home_km": 900,
        "avg_amount": 900,
        "channel": "card",
        "direction": "out",
        "counterparty_country": "KY",
        "hours_since_inflow": 1,
    }
    decision = LoanOriginationAgent().run(
        _base_application(sample_transaction=txn, recent_transactions=[txn])
    )
    assert decision.outcome in {"refer_fico", "reject"}


def test_robo_aggressive_young_saver():
    result = RoboAdvisor().advise(
        {
            "age": 25,
            "horizon_years": 20,
            "monthly_surplus": 60000,
            "emergency_months": 10,
            "loss_tolerance": 5,
            "market_knowledge": 5,
        }
    )
    assert result.bucket in {"growth", "aggressive"}
    assert result.weights["equity"] >= 0.45
    assert abs(sum(result.weights.values()) - 1.0) < 1e-6
