from fraud_detection import FraudDetector


def test_typical_spend_is_not_blocked():
    result = FraudDetector().predict(
        {
            "amount": 540,
            "hour": 18,
            "merchant_category": "grocery",
            "is_international": False,
            "is_card_present": True,
            "failed_pin_attempts": 0,
            "velocity_1h": 1,
            "distance_from_home_km": 3,
            "avg_amount": 600,
        }
    )
    assert result.risk_score < 70
    assert result.decision in {"allow", "step_up_auth"}


def test_night_crypto_blast_is_high_risk():
    result = FraudDetector().predict(
        {
            "amount": 95000,
            "hour": 2,
            "merchant_category": "crypto",
            "is_international": True,
            "is_card_present": False,
            "failed_pin_attempts": 4,
            "velocity_1h": 9,
            "distance_from_home_km": 740,
            "avg_amount": 1200,
        }
    )
    assert result.risk_score >= 70
    assert result.label == "high_risk"
    assert result.reasons
