"""Walk a loan file through the origination agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from loan_agent import LoanOriginationAgent

APPLICATION = {
    "application_id": "APP-EX-01",
    "customer_id": "CUST077",
    "kyc_text": (
        "INCOME TAX DEPARTMENT GOVT OF INDIA Permanent Account Number Card ABCDE1234F "
        "Name RAHUL SHARMA Father's Name VIJAY SHARMA Date of Birth 12/03/1992"
    ),
    "age": 31,
    "annual_income": 1100000,
    "employment_years": 6,
    "existing_debt": 150000,
    "loan_amount": 400000,
    "loan_term_months": 36,
    "credit_history_years": 7,
    "late_payments_24m": 0,
    "credit_utilization": 0.28,
    "dependents": 0,
}


def main() -> None:
    decision = LoanOriginationAgent().run(APPLICATION)
    print(json.dumps(decision.to_dict(), indent=2))


if __name__ == "__main__":
    main()
