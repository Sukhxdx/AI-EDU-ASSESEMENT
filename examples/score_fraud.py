"""Score a pair of card events from the command line."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fraud_detection import FraudDetector

CASES = [
    {
        "name": "salary-day grocery",
        "payload": {
            "amount": 820,
            "hour": 19,
            "merchant_category": "grocery",
            "is_international": False,
            "is_card_present": False,
            "failed_pin_attempts": 0,
            "velocity_1h": 1,
            "distance_from_home_km": 5,
            "avg_amount": 900,
        },
    },
    {
        "name": "3 a.m. overseas crypto",
        "payload": {
            "amount": 74000,
            "hour": 3,
            "merchant_category": "crypto",
            "is_international": True,
            "is_card_present": False,
            "failed_pin_attempts": 3,
            "velocity_1h": 7,
            "distance_from_home_km": 510,
            "avg_amount": 1500,
        },
    },
]


def main() -> None:
    detector = FraudDetector()
    for case in CASES:
        print(case["name"])
        print(json.dumps(detector.predict(case["payload"]).to_dict(), indent=2))
        print()


if __name__ == "__main__":
    main()
