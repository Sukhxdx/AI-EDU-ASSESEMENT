"""Build the synthetic Indian retail-banking datasets used to train models.

The generator is deterministic (seed 42) so training metrics stay stable.
Labels are planted from observable features; this is a simulator, not a
production bureau extract.
"""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dataset"
RNG = np.random.default_rng(42)
random.seed(42)

CITIES = ["Bengaluru", "Mumbai", "Pune", "Hyderabad", "Chennai", "Delhi", "Kolkata", "Ahmedabad"]
MERCHANTS = {
    "grocery": ["BIGBASKET", "D-MART", "RELIANCE FRESH", "MORE SUPERMARKET"],
    "fuel": ["IOCL PETROL", "HPCL PUMP", "BPCL STATION"],
    "utilities": ["BESCOM", "MSEDCL", "AIRTEL BROADBAND", "JIO PREPAID"],
    "dining": ["SWIGGY", "ZOMATO", "DOMINOS", "STARBUCKS"],
    "shopping": ["AMAZON", "FLIPKART", "MYNTRA", "AJIO"],
    "travel": ["IRCTC", "INDIGO", "MAKEMYTRIP", "UBER"],
    "electronics": ["CROMA", "RELIANCE DIGITAL", "VIJAY SALES"],
    "crypto": ["COINDCX", "WAZIRX", "BINANCE P2P"],
    "gambling": ["DREAM11", "RUMMYCIRCLE", "STAKE"],
    "jewelry": ["TANISHQ", "MALABAR GOLD"],
    "atm_cash": ["NEXUSBANK ATM", "NFS ATM"],
    "other": ["UPI COLLECT", "RENT UPI", "FRIEND IMPS"],
}

INTENTS = {
    "greeting": [
        "hello", "hi there", "good morning", "hey nexus", "namaste",
        "hi, I need help", "hello bank", "good evening",
    ],
    "balance_inquiry": [
        "what is my account balance", "show savings balance", "how much money do I have",
        "check ledger balance", "current account balance please", "available balance",
        "tell me my balance", "funds left in salary account",
        "account balance", "savings account balance", "check my balance",
    ],
    "mini_statement": [
        "send mini statement", "last five transactions", "recent debit list",
        "sms mini statement", "show last few spends", "account mini statement please",
    ],
    "fund_transfer": [
        "how do I transfer money", "send IMPS to beneficiary", "UPI limit today",
        "NEFT timing", "add a new payee", "transfer to another bank",
        "how long does RTGS take", "help with fund transfer",
    ],
    "card_block": [
        "block my debit card", "hotlist lost card", "freeze credit card now",
        "my card is stolen please block", "disable card immediately",
        "stop the card I lost my wallet", "block card ending 4412",
    ],
    "card_unblock": [
        "unblock my card", "enable the debit card again", "I found my card please activate",
        "remove temporary block", "reactivate credit card",
    ],
    "pin_reset": [
        "reset debit card pin", "forgot ATM pin", "change card pin",
        "generate new pin", "pin is locked help",
    ],
    "loan_inquiry": [
        "personal loan eligibility", "can I get a home loan", "loan interest rate",
        "apply for two wheeler loan", "pre-approved loan offer",
        "what documents for personal loan", "loan against FD",
    ],
    "emi_help": [
        "calculate EMI for 5 lakh", "reduce my EMI", "foreclosure charges",
        "how many EMIs left", "prepay personal loan", "EMI bounce what happens",
    ],
    "kyc_update": [
        "update KYC", "re kyc pending", "upload aadhaar for kyc",
        "video kyc slot", "change address in KYC", "PAN not updated",
    ],
    "fraud_report": [
        "I did not do this transaction", "unauthorised UPI debit", "report card fraud",
        "someone stole money from my account", "phishing debit please reverse",
        "fraud sms stole my otp", "chargeback this merchant",
    ],
    "investment_advice": [
        "where should I SIP", "mutual fund suggestion", "robo advisor portfolio",
        "is equity too risky for me", "gold vs debt allocation",
        "start a monthly SIP",
    ],
    "complaint": [
        "raise a complaint", "branch staff was rude", "cheque not cleared",
        "service request not closed", "I want to escalate", "ombudsman complaint",
    ],
    "branch_locator": [
        "nearest branch", "ATM near me", "branch in Koramangala",
        "cash deposit machine pincode 560001", "working hours of branch",
    ],
    "goodbye": [
        "thanks bye", "that is all", "thank you", "goodbye", "ok thanks",
    ],
    "fallback": [
        "asdfgh", "what is the weather", "play a song", "who won the match",
        "recipe for dosa", "random gibberish text",
    ],
}


def _choice(seq):
    return seq[int(RNG.integers(0, len(seq)))]


def generate_transactions(n: int = 4000) -> pd.DataFrame:
    rows = []
    cats = list(MERCHANTS)
    for i in range(n):
        cat = _choice(cats)
        typical = {
            "grocery": 1800, "fuel": 2200, "utilities": 1400, "dining": 650,
            "shopping": 2400, "travel": 4500, "electronics": 12000, "crypto": 18000,
            "gambling": 3500, "jewelry": 22000, "atm_cash": 8000, "other": 2000,
        }[cat]
        amount = max(50, RNG.lognormal(np.log(typical), 0.55))
        hour = int(RNG.integers(0, 24))
        international = bool(RNG.random() < 0.08)
        card_present = bool(RNG.random() < 0.7)
        velocity = int(RNG.integers(1, 4))
        distance = float(abs(RNG.normal(8, 12)))
        pin_fail = int(RNG.choice([0, 0, 0, 1, 2, 3], p=[0.7, 0.1, 0.08, 0.06, 0.04, 0.02]))
        avg = typical * float(RNG.uniform(0.8, 1.2))

        fraud = 0
        if international and hour <= 5 and amount > 25000:
            fraud = 1
        if velocity >= 7:
            fraud = 1
        if cat in {"crypto", "gambling"} and amount > 20000:
            fraud = 1
        if amount / avg >= 8 and not card_present:
            fraud = 1
        if pin_fail >= 3 and amount > 10000:
            fraud = 1
        if RNG.random() < 0.015:
            fraud = 1
        if fraud:
            amount *= float(RNG.uniform(1.8, 4.5))
            velocity = max(velocity, int(RNG.integers(5, 11)))
            if RNG.random() < 0.5:
                international = True
                hour = int(RNG.integers(0, 6))

        rows.append(
            {
                "txn_id": f"TXN{i:05d}",
                "customer_id": f"CUST{int(RNG.integers(1, 420)):03d}",
                "amount": round(float(amount), 2),
                "hour": hour,
                "merchant_category": cat,
                "merchant": _choice(MERCHANTS[cat]),
                "is_international": int(international),
                "is_card_present": int(card_present),
                "failed_pin_attempts": pin_fail,
                "velocity_1h": velocity,
                "distance_from_home_km": round(distance, 1),
                "avg_amount": round(avg, 2),
                "city": _choice(CITIES),
                "is_fraud": fraud,
            }
        )
    return pd.DataFrame(rows)


def generate_loans(n: int = 2500) -> pd.DataFrame:
    rows = []
    for i in range(n):
        age = int(np.clip(RNG.normal(36, 9), 21, 62))
        income = float(np.clip(RNG.lognormal(13.2, 0.45), 180000, 4500000))
        emp = float(max(0.2, RNG.normal(6, 4)))
        debt = float(max(0, RNG.normal(income * 0.25, income * 0.15)))
        amount = float(np.clip(RNG.lognormal(12.4, 0.5), 50000, 2500000))
        term = int(RNG.choice([12, 24, 36, 48, 60]))
        hist = float(max(0.5, RNG.normal(7, 3)))
        late = int(max(0, RNG.poisson(0.7)))
        util = float(np.clip(RNG.beta(2, 5), 0.02, 0.99))
        deps = int(RNG.integers(0, 5))
        dti = debt / income
        lti = amount / income
        p_default = 0.06
        p_default += 0.55 * max(0.0, dti - 0.35)
        p_default += 0.40 * max(0.0, util - 0.55)
        p_default += 0.12 * min(late, 6)
        p_default += 0.35 * max(0.0, lti - 0.7)
        p_default -= 0.03 * min(emp, 10)
        p_default -= 0.02 * min(hist, 12)
        if income < 350000:
            p_default += 0.12
        p_default = float(np.clip(p_default, 0.03, 0.92))
        if dti > 0.55 and late >= 2:
            defaulted = 1
        elif util > 0.8 and lti > 1.0:
            defaulted = 1
        elif dti < 0.18 and late == 0 and util < 0.28 and emp >= 5 and income >= 700000:
            defaulted = 0
        else:
            defaulted = int(RNG.random() < p_default)
        rows.append(
            {
                "application_id": f"LN{i:05d}",
                "age": age,
                "annual_income": round(income, 0),
                "employment_years": round(emp, 1),
                "existing_debt": round(debt, 0),
                "loan_amount": round(amount, 0),
                "loan_term_months": term,
                "credit_history_years": round(hist, 1),
                "late_payments_24m": late,
                "credit_utilization": round(util, 3),
                "dependents": deps,
                "defaulted": defaulted,
            }
        )
    return pd.DataFrame(rows)


def generate_aml(n: int = 1800) -> pd.DataFrame:
    rows = []
    for i in range(n):
        customer = f"CUST{int(RNG.integers(1, 80)):03d}"
        amount = float(np.clip(RNG.lognormal(10.5, 1.1), 500, 900000))
        country = str(RNG.choice(["IN", "IN", "IN", "IN", "US", "SG", "AE", "CY", "PA"], p=[0.62, 0.1, 0.08, 0.05, 0.04, 0.03, 0.04, 0.02, 0.02]))
        channel = str(RNG.choice(["upi", "neft", "imps", "cash", "rtgs"], p=[0.4, 0.2, 0.2, 0.12, 0.08]))
        direction = str(RNG.choice(["in", "out"]))
        hours = float(max(0.2, RNG.exponential(20)))
        if RNG.random() < 0.06:
            amount = float(RNG.uniform(430000, 498000))
        rows.append(
            {
                "txn_id": f"AML{i:05d}",
                "customer_id": customer,
                "amount": round(amount, 2),
                "counterparty_country": country,
                "channel": channel,
                "direction": direction,
                "hours_since_inflow": round(hours, 1),
            }
        )
    return pd.DataFrame(rows)


def generate_queries() -> pd.DataFrame:
    rows = []
    for intent, phrases in INTENTS.items():
        for phrase in phrases:
            rows.append({"text": phrase, "intent": intent})
            rows.append({"text": phrase.capitalize() + "?", "intent": intent})
            rows.append({"text": "please " + phrase, "intent": intent})
    return pd.DataFrame(rows)


def generate_kyc() -> pd.DataFrame:
    samples = []
    pans = ["ABCDE1234F", "PQRST5678L", "LMNOP2468K", "ZXCVB1357M"]
    for pan in pans:
        samples.append(
            (
                "pan",
                f"INCOME TAX DEPARTMENT GOVT OF INDIA Permanent Account Number Card {pan} "
                f"Name RAHUL SHARMA Father's Name VIJAY SHARMA Date of Birth 12/03/1992",
            )
        )
    for num in ["2345 6789 0123", "4455 6677 8899", "1122 3344 5566"]:
        samples.append(
            (
                "aadhaar",
                f"Unique Identification Authority of India Aadhaar {num} "
                f"Name Priya Nair DOB 1994 Address 12 MG Road Bengaluru 560001",
            )
        )
    for code in ["A1234567", "B7654321", "K9988776"]:
        samples.append(
            (
                "passport",
                f"REPUBLIC OF INDIA Passport No {code} Surname IYER Given Name ARJUN "
                f"Nationality INDIAN Place of Issue CHENNAI",
            )
        )
    for dl in ["KA-01-2019-0012345", "MH-12-2018-0099887"]:
        samples.append(
            (
                "driving_license",
                f"Indian Union Driving Licence {dl} Name MEERA PATIL Valid Till 2031 "
                f"RTO Pune Vehicle Class LMV",
            )
        )
    samples.extend(
        [
            ("utility_bill", "BESCOM electricity bill Account 998877 Consumer ANITA RAO Units 210 Amount 2450 Due 12 Aug"),
            ("utility_bill", "Mahanagar Gas invoice Customer 5566 Billing address Andheri West unpaid 1890"),
            ("bank_statement", "NexusBank statement Account 1122334455 Opening balance 54000 Closing 61220"),
            ("bank_statement", "Savings account statement IFSC NEXU0000123 credits 8 debits 21 available 88400"),
            ("bank_statement", "Passbook extract salary credit 72000 EMI debit 15400 closing balance 33010"),
            ("unknown", "Grocery receipt tomato onion milk total 430 thank you visit again"),
            ("unknown", "Parking ticket slot B4 amount 40 cash only"),
            ("unknown", "Handwritten note please call back regarding insurance"),
        ]
    )
    rows = []
    for doc_type, text in samples:
        rows.append({"text": text, "doc_type": doc_type})
        rows.append({"text": text.lower(), "doc_type": doc_type})
        rows.append({"text": "scanned copy " + text, "doc_type": doc_type})
    return pd.DataFrame(rows)


def generate_spend(n: int = 1600) -> pd.DataFrame:
    catalog = {
        "groceries": ["BIGBASKET BLR", "D-MART WHITEFIELD", "RELIANCE FRESH", "MORE HYPERMART"],
        "dining": ["SWIGGY *ORDER", "ZOMATO BANGALORE", "DOMINOS PIZZA", "CAFE COFFEE DAY"],
        "fuel": ["IOCL PETROL PUMP", "HPCL HIGHWAY", "BPCL AUTOCARE"],
        "utilities": ["BESCOM ONLINE", "AIRTEL BROADBAND", "JIO RECHARGE", "BWSSB WATER"],
        "shopping": ["AMAZON PAY", "FLIPKART INTERNET", "MYNTRA DESIGNS", "AJIO FASHION"],
        "travel": ["IRCTC TICKET", "INDIGO AIRLINES", "UBER TRIP", "MAKEMYTRIP HOTEL"],
        "healthcare": ["APOLLO PHARMACY", "PRACTO CONSULT", "FORTIS HOSPITAL"],
        "entertainment": ["NETFLIX.COM", "SPOTIFY INDIA", "PVR CINEMAS", "HOTSTAR"],
        "education": ["BYJUS CLASSES", "COURSERA INC", "UNIVERSITY FEE"],
        "transfers": ["UPI/RAHUL", "IMPS/FAMILY", "NEFT RENT LANDLORD"],
    }
    rows = []
    for i in range(n):
        cat = _choice(list(catalog))
        desc = _choice(catalog[cat])
        if RNG.random() < 0.3:
            desc = desc + f" #{int(RNG.integers(100, 999))}"
        amount = float(np.clip(RNG.lognormal(6.8, 0.7), 40, 80000))
        rows.append({"description": desc, "category": cat, "amount": round(amount, 2)})
    return pd.DataFrame(rows)


def generate_news() -> pd.DataFrame:
    positives = [
        "Nifty 50 rallies as FIIs record strong inflows",
        "Private bank profits beat street estimates in Q2",
        "RBI keeps rates stable; rupee gains against dollar",
        "UPI volumes hit a record high in festival month",
        "Insurer reports surplus and upgrades growth outlook",
        "Fintech lending platform announces expansion into three states",
        "Gold holds firm while equity markets surge on earnings",
        "Credit growth stays strong at scheduled commercial banks",
        "Mutual fund SIP inflows hit a fresh monthly record",
        "IT major announces buyback after profit beat",
    ]
    negatives = [
        "Bank NPAs rise after a string of corporate defaults",
        "RBI penalty on lender for KYC lapses sparks selloff",
        "Inflation surprise triggers rate hike fears",
        "Brokerage downgrades NBFC on funding stress warning",
        "Equity markets slump as foreign funds report outflows",
        "Probe opened into alleged card fraud ring",
        "Rupee falls to a weak close amid global recession talk",
        "Insurer posts losses after catastrophe claims",
        "Fintech slowdown as funding winter continues",
        "Volatile session wipes weekly gains in banking stocks",
    ]
    neutrals = [
        "RBI publishes discussion paper on digital lending",
        "SEBI schedules board meeting next week",
        "Government tables data on household financial savings",
        "NPCI issues circular on UPI transaction limits",
        "Banks to remain closed on account of regional holiday",
        "Ministry releases draft rules for account aggregators",
        "Exchange announces mock trading session on Saturday",
        "Credit bureau explains new score methodology",
        "IFSCA consults on overseas listing framework",
        "Central bank calendar lists upcoming policy dates",
    ]
    rows = []
    for label, headlines in (("positive", positives), ("negative", negatives), ("neutral", neutrals)):
        for headline in headlines:
            rows.append({"headline": headline, "label": label})
            rows.append({"headline": headline.replace("RBI", "the central bank"), "label": label})
            rows.append({"headline": "Market wrap: " + headline, "label": label})
    extra = [
        ("positive", "HDFC Bank shares gain after strong loan growth print"),
        ("negative", "Small finance bank warning on unsecured book quality"),
        ("neutral", "NSE issues technical bulletin for trading members"),
    ]
    for label, headline in extra:
        rows.append({"headline": headline, "label": label})
    return pd.DataFrame(rows)


def generate_profiles(n: int = 800) -> pd.DataFrame:
    rows = []
    for _ in range(n):
        rows.append(
            {
                "age": int(np.clip(RNG.normal(34, 10), 22, 65)),
                "horizon_years": int(np.clip(RNG.normal(8, 4), 1, 25)),
                "monthly_surplus": float(np.clip(RNG.lognormal(9.4, 0.6), 2000, 150000)),
                "emergency_months": float(np.clip(RNG.normal(5, 2), 0, 18)),
                "loss_tolerance": int(RNG.integers(1, 6)),
                "market_knowledge": int(RNG.integers(1, 6)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    generate_transactions().to_csv(OUT / "transactions.csv", index=False)
    generate_loans().to_csv(OUT / "loan_applications.csv", index=False)
    generate_aml().to_csv(OUT / "aml_ledger.csv", index=False)
    generate_queries().to_csv(OUT / "customer_queries.csv", index=False)
    generate_kyc().to_csv(OUT / "kyc_documents.csv", index=False)
    generate_spend().to_csv(OUT / "spend_merchants.csv", index=False)
    generate_news().to_csv(OUT / "news_headlines.csv", index=False)
    generate_profiles().to_csv(OUT / "investor_profiles.csv", index=False)
    print(f"Wrote datasets to {OUT}")


if __name__ == "__main__":
    main()
