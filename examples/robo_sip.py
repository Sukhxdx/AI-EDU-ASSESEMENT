"""Illustrative SIP mix for two investor profiles."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from robo_advisor import RoboAdvisor

PROFILES = {
    "early-career": {
        "age": 26,
        "horizon_years": 18,
        "monthly_surplus": 18000,
        "emergency_months": 4,
        "loss_tolerance": 4,
        "market_knowledge": 3,
    },
    "near-retirement": {
        "age": 58,
        "horizon_years": 5,
        "monthly_surplus": 40000,
        "emergency_months": 12,
        "loss_tolerance": 2,
        "market_knowledge": 3,
    },
}


def main() -> None:
    advisor = RoboAdvisor()
    for name, profile in PROFILES.items():
        print(name)
        print(json.dumps(advisor.advise(profile).to_dict(), indent=2))
        print()


if __name__ == "__main__":
    main()
