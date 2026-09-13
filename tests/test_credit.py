from credit_scoring import CreditScorer


def test_strong_file_is_investment_grade():
    result = CreditScorer().predict(
        {
            "age": 38,
            "annual_income": 1800000,
            "employment_years": 11,
            "existing_debt": 120000,
            "loan_amount": 300000,
            "loan_term_months": 24,
            "credit_history_years": 12,
            "late_payments_24m": 0,
            "credit_utilization": 0.18,
            "dependents": 1,
        }
    )
    assert result.pd_score < 0.25
    assert result.grade in {"A", "B", "C"}
    assert result.decision in {"approve", "manual_review"}


def test_stressed_file_has_higher_pd():
    strong = CreditScorer().predict(
        {
            "age": 40,
            "annual_income": 1500000,
            "employment_years": 10,
            "existing_debt": 80000,
            "loan_amount": 200000,
            "loan_term_months": 24,
            "credit_history_years": 10,
            "late_payments_24m": 0,
            "credit_utilization": 0.2,
            "dependents": 0,
        }
    )
    weak = CreditScorer().predict(
        {
            "age": 24,
            "annual_income": 280000,
            "employment_years": 0.4,
            "existing_debt": 260000,
            "loan_amount": 900000,
            "loan_term_months": 60,
            "credit_history_years": 1,
            "late_payments_24m": 6,
            "credit_utilization": 0.91,
            "dependents": 3,
        }
    )
    assert weak.pd_score > strong.pd_score
    assert weak.decision in {"manual_review", "decline"}
