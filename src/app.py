"""NexusBank AI — Streamlit operations console."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aml_monitor import AmlMonitor
from banking_chatbot import BankingChatbot
from credit_scoring import CreditScorer
from fraud_detection import FraudDetector
from kyc_classifier import KycClassifier
from loan_agent import LoanOriginationAgent
from news_sentiment import NewsSentiment
from paths import DATASET_DIR
from robo_advisor import RoboAdvisor
from settings import load_settings
from spend_categorizer import SpendCategorizer

st.set_page_config(page_title="NexusBank AI", page_icon="🏦", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:wght@600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background: radial-gradient(1200px 600px at 10% -10%, #12324a 0%, #0b1220 42%, #070b14 100%); color: #e8eef7; }
[data-testid="stSidebar"] { background: #0a1624; border-right: 1px solid #1e3a4c; }
h1, h2, h3 { font-family: 'IBM Plex Serif', serif; letter-spacing: -0.02em; }
.hero { padding: 1.2rem 1.4rem; border: 1px solid #1f4b63; border-radius: 16px;
  background: linear-gradient(135deg, rgba(18,92,120,0.35), rgba(12,24,40,0.9)); margin-bottom: 1rem; }
.hero h1 { margin: 0; font-size: 2.1rem; color: #f4fbff; }
.hero p { margin: 0.35rem 0 0; color: #b7c9d6; }
.card { border: 1px solid #1d3d52; border-radius: 14px; padding: 0.9rem 1rem; background: rgba(9,18,30,0.7); }
.ok { color: #3ee0a2; font-weight: 600; }
.warn { color: #f5c15d; font-weight: 600; }
.bad { color: #ff7a7a; font-weight: 600; }
.stButton>button { background: #1b6b8a; color: white; border: 0; border-radius: 10px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource
def load_engines():
    return {
        "fraud": FraudDetector(),
        "credit": CreditScorer(),
        "chat": BankingChatbot(),
        "kyc": KycClassifier(),
        "spend": SpendCategorizer(),
        "news": NewsSentiment(),
        "robo": RoboAdvisor(),
        "aml": AmlMonitor(),
        "agent": LoanOriginationAgent(),
        "cfg": load_settings(),
    }


ENG = load_engines()


def badge(text: str, kind: str) -> str:
    klass = {"ok": "ok", "warn": "warn", "bad": "bad"}.get(kind, "ok")
    return f'<span class="{klass}">{text}</span>'


def page_home() -> None:
    cfg = ENG["cfg"]["app"]
    st.markdown(
        f"<div class='hero'><h1>{cfg['name']}</h1><p>{cfg['tagline']}</p></div>",
        unsafe_allow_html=True,
    )
    tx = pd.read_csv(DATASET_DIR / "transactions.csv")
    loans = pd.read_csv(DATASET_DIR / "loan_applications.csv")
    news = pd.read_csv(DATASET_DIR / "news_headlines.csv")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sample card/UPI events", f"{len(tx):,}")
    c2.metric("Loan files in simulator", f"{len(loans):,}")
    c3.metric("Planted fraud rate", f"{tx['is_fraud'].mean():.1%}")
    c4.metric("News headlines", f"{len(news):,}")

    left, right = st.columns((1.1, 1))
    with left:
        st.subheader("What this console does")
        st.markdown(
            """
Nine related modules sit behind one operations desk:

1. **Fraud Sentinel** — Isolation Forest plus policy rules on card/UPI events  
2. **Credit Underwriting** — gradient-boosted probability of default and grade  
3. **AML Watch** — structuring, rapid in-out, high-risk geography  
4. **Customer Copilot** — TF-IDF intent classifier for retail banking chat  
5. **KYC Intake** — document typing and PAN/Aadhaar field extraction  
6. **Spend Insights** — merchant-string categorisation  
7. **Market Pulse** — financial news sentiment  
8. **Robo-Advisor** — risk clustering and SIP sleeve weights  
9. **Loan Origination Agent** — chains KYC → credit → fraud → AML into one memo  

The stack is a **simulator**. Models are trained on synthetic Indian retail data
so the application runs without bureau files, production logs or paid APIs.
            """
        )
    with right:
        st.subheader("Risk mix in the sample book")
        fraud_by_cat = tx.groupby("merchant_category")["is_fraud"].mean().reset_index()
        fig = px.bar(
            fraud_by_cat,
            x="merchant_category",
            y="is_fraud",
            labels={"is_fraud": "planted fraud rate", "merchant_category": "MCC bucket"},
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#d7e4ee", height=340)
        st.plotly_chart(fig, use_container_width=True)

    st.info("Open a module from the sidebar. Each screen accepts a live input and can load a canned example.")


def page_fraud() -> None:
    st.header("Fraud Sentinel")
    st.caption("Unsupervised anomaly model with readable rule overlays.")
    col, demo = st.columns((1.2, 1))
    cats = ["grocery", "fuel", "utilities", "dining", "shopping", "travel", "electronics", "crypto", "gambling", "jewelry", "atm_cash", "other"]
    defaults = {
        "fraud_amount": 2400.0, "fraud_hour": 13, "fraud_merchant": "shopping",
        "fraud_fx": False, "fraud_present": True, "fraud_pin": 0,
        "fraud_vel": 1, "fraud_dist": 6.0, "fraud_avg": 2000.0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    with demo:
        st.markdown("**Load a scenario**")
        if st.button("Typical grocery UPI"):
            st.session_state.update(
                {
                    "fraud_amount": 640.0, "fraud_hour": 19, "fraud_merchant": "grocery",
                    "fraud_fx": False, "fraud_present": False, "fraud_pin": 0,
                    "fraud_vel": 1, "fraud_dist": 4.0, "fraud_avg": 700.0,
                }
            )
            st.rerun()
        if st.button("Suspicious night crypto spend"):
            st.session_state.update(
                {
                    "fraud_amount": 86000.0, "fraud_hour": 2, "fraud_merchant": "crypto",
                    "fraud_fx": True, "fraud_present": False, "fraud_pin": 3,
                    "fraud_vel": 8, "fraud_dist": 620.0, "fraud_avg": 1800.0,
                }
            )
            st.rerun()
    with col:
        amount = st.number_input("Amount (INR)", 1.0, 500000.0, key="fraud_amount")
        hour = st.slider("Hour of day", 0, 23, key="fraud_hour")
        merchant = st.selectbox("Merchant category", cats, key="fraud_merchant")
        international = st.checkbox("International", key="fraud_fx")
        present = st.checkbox("Card present", key="fraud_present")
        pin = st.number_input("Failed PIN attempts", 0, 6, key="fraud_pin")
        velocity = st.number_input("Authorisations in last hour", 1, 20, key="fraud_vel")
        distance = st.number_input("Distance from home (km)", 0.0, 2000.0, key="fraud_dist")
        avg = st.number_input("Customer typical amount", 50.0, 100000.0, key="fraud_avg")
        if st.button("Score transaction", type="primary"):
            result = ENG["fraud"].predict(
                {
                    "amount": amount, "hour": hour, "merchant_category": merchant,
                    "is_international": international, "is_card_present": present,
                    "failed_pin_attempts": pin, "velocity_1h": velocity,
                    "distance_from_home_km": distance, "avg_amount": avg,
                }
            )
            kind = "bad" if result.label == "high_risk" else "warn" if result.label == "review" else "ok"
            st.markdown(badge(f"{result.label.upper()}  ·  {result.decision}  ·  {result.risk_score:.0f}/100", kind), unsafe_allow_html=True)
            st.write("Reasons")
            for reason in result.reasons:
                st.write(f"- {reason}")
            st.json(result.to_dict())


def page_credit() -> None:
    st.header("Credit Underwriting")
    st.caption("Supervised PD model trained on synthetic personal-loan files.")
    c1, c2, c3 = st.columns(3)
    age = c1.slider("Age", 21, 62, 33)
    income = c1.number_input("Annual income (INR)", 150000, 5000000, 850000, step=10000)
    emp = c1.slider("Employment years", 0.0, 25.0, 5.0)
    debt = c2.number_input("Existing debt (INR)", 0, 4000000, 180000, step=10000)
    amount = c2.number_input("Requested amount (INR)", 25000, 2500000, 420000, step=10000)
    term = c2.selectbox("Tenor (months)", [12, 24, 36, 48, 60], index=2)
    hist = c3.slider("Bureau history (years)", 0.5, 20.0, 6.0)
    late = c3.slider("Late payments (24m)", 0, 10, 1)
    util = c3.slider("Revolving utilisation", 0.05, 0.99, 0.32)
    deps = c3.slider("Dependents", 0, 6, 1)
    if st.button("Run underwriting", type="primary"):
        result = ENG["credit"].predict(
            {
                "age": age, "annual_income": income, "employment_years": emp,
                "existing_debt": debt, "loan_amount": amount, "loan_term_months": term,
                "credit_history_years": hist, "late_payments_24m": late,
                "credit_utilization": util, "dependents": deps,
            }
        )
        kind = "ok" if result.decision == "approve" else "warn" if result.decision == "manual_review" else "bad"
        st.markdown(badge(f"Grade {result.grade}  ·  PD {result.pd_score:.1%}  ·  {result.decision}", kind), unsafe_allow_html=True)
        for reason in result.reasons:
            st.write(f"- {reason}")
        fig = px.bar(
            x=list(result.feature_contributions.keys()),
            y=list(result.feature_contributions.values()),
            labels={"x": "feature", "y": "weighted contribution"},
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#d7e4ee", height=320)
        st.plotly_chart(fig, use_container_width=True)


def page_aml() -> None:
    st.header("AML Watch")
    st.caption("Typology scoring over a short customer ledger (PMLA-style red flags).")
    ledger = pd.read_csv(DATASET_DIR / "aml_ledger.csv")
    customer = st.selectbox("Customer", sorted(ledger["customer_id"].unique()))
    subset = ledger[ledger["customer_id"] == customer]
    st.dataframe(subset, use_container_width=True, hide_index=True)
    alert = ENG["aml"].evaluate_customer(subset.to_dict(orient="records"), customer)
    kind = "bad" if alert.severity == "high" else "warn" if alert.severity in {"medium", "watch"} else "ok"
    st.markdown(badge(f"{alert.severity.upper()}  ·  score {alert.alert_score:.0f}", kind), unsafe_allow_html=True)
    st.write("Typologies:", ", ".join(alert.typologies) or "none")
    for line in alert.evidence:
        st.write(f"- {line}")


def page_chat() -> None:
    st.header("Customer Copilot")
    st.caption("Intent classification for retail-banking chat. Low confidence hands off to an officer.")
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []
    prompt = st.chat_input("Ask about cards, KYC, loans, fraud…")
    for role, text in st.session_state.chat_log:
        st.chat_message(role).write(text)
    if prompt:
        reply = ENG["chat"].respond(prompt)
        st.session_state.chat_log.append(("user", prompt))
        extra = f"\n\n_intent: `{reply.intent}` ({reply.confidence:.0%})"
        if reply.needs_handoff:
            extra += " · handoff_"
        else:
            extra += "_"
        st.session_state.chat_log.append(("assistant", reply.reply + extra))
        st.rerun()


def page_kyc() -> None:
    st.header("KYC Intake")
    sample = (
        "INCOME TAX DEPARTMENT GOVT OF INDIA Permanent Account Number Card ABCDE1234F "
        "Name RAHUL SHARMA Father's Name VIJAY SHARMA Date of Birth 12/03/1992"
    )
    text = st.text_area("Paste OCR / extracted document text", sample, height=160)
    if st.button("Classify document", type="primary"):
        result = ENG["kyc"].assess(text)
        kind = "ok" if result.accepted else "bad"
        st.markdown(badge(f"{result.doc_type}  ·  {result.confidence:.0%}  ·  {'accepted' if result.accepted else 'rejected'}", kind), unsafe_allow_html=True)
        st.json(result.to_dict())


def page_spend() -> None:
    st.header("Spend Insights")
    frame = pd.read_csv(DATASET_DIR / "spend_merchants.csv").sample(80, random_state=7)
    summary = ENG["spend"].summarise(frame)
    fig = px.pie(summary, names="category", values="amount", hole=0.45)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#d7e4ee", height=380)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(summary, use_container_width=True, hide_index=True)
    desc = st.text_input("Classify a merchant string", "SWIGGY *ORDER #882")
    if st.button("Classify"):
        st.json(ENG["spend"].classify(desc).to_dict())


def page_news() -> None:
    st.header("Market Pulse")
    news = pd.read_csv(DATASET_DIR / "news_headlines.csv")
    scored = [ENG["news"].score(row) for row in news["headline"].head(24)]
    view = pd.DataFrame([item.to_dict() for item in scored])
    st.dataframe(view, use_container_width=True, hide_index=True)
    counts = view["label"].value_counts().reset_index()
    counts.columns = ["label", "count"]
    fig = px.bar(counts, x="label", y="count", color="label")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#d7e4ee", height=300)
    st.plotly_chart(fig, use_container_width=True)
    headline = st.text_input("Score a headline", "Private bank profits beat street estimates after NPA decline")
    if st.button("Score headline", type="primary"):
        st.json(ENG["news"].score(headline).to_dict())


def page_robo() -> None:
    st.header("Robo-Advisor")
    c1, c2 = st.columns(2)
    age = c1.slider("Age", 22, 65, 31)
    horizon = c1.slider("Investment horizon (years)", 1, 25, 10)
    surplus = c1.number_input("Monthly surplus (INR)", 2000, 150000, 25000, step=1000)
    emergency = c2.slider("Emergency fund (months of expense)", 0.0, 18.0, 5.0)
    loss = c2.slider("Loss tolerance (1 = anxious, 5 = calm)", 1, 5, 3)
    knowledge = c2.slider("Market knowledge", 1, 5, 3)
    if st.button("Build SIP sleeve", type="primary"):
        result = ENG["robo"].advise(
            {
                "age": age, "horizon_years": horizon, "monthly_surplus": surplus,
                "emergency_months": emergency, "loss_tolerance": loss, "market_knowledge": knowledge,
            }
        )
        st.markdown(badge(f"{result.bucket.upper()}  ·  risk {result.risk_score:.0f}/100", "ok"), unsafe_allow_html=True)
        weights = pd.DataFrame({"asset": list(result.weights), "weight": list(result.weights.values())})
        fig = px.bar(weights, x="asset", y="weight")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#d7e4ee", height=320)
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Illustrative expected return", f"{result.expected_return:.1%}")
        st.metric("Illustrative volatility", f"{result.expected_volatility:.1%}")
        for note in result.notes:
            st.write(f"- {note}")


def page_agent() -> None:
    st.header("Loan Origination Agent")
    st.caption("One planner calls KYC, credit, fraud and AML, then writes a decision memo.")
    app_id = st.text_input("Application ID", "APP-24091")
    kyc_text = st.text_area(
        "KYC document text",
        "Unique Identification Authority of India Aadhaar 2345 6789 0123 Name Priya Nair DOB 1994 Address 12 MG Road Bengaluru 560001",
        height=120,
    )
    c1, c2, c3 = st.columns(3)
    income = c1.number_input("Annual income", 200000, 4000000, 960000, step=10000)
    amount = c2.number_input("Loan amount", 50000, 2000000, 350000, step=10000)
    late = c3.slider("Late payments", 0, 8, 0)
    util = c1.slider("Utilisation", 0.05, 0.95, 0.22)
    debt = c2.number_input("Existing debt", 0, 2000000, 90000, step=5000)
    risky = st.checkbox("Inject a high-risk recent card event")
    sample_txn = None
    if risky:
        sample_txn = {
            "amount": 92000, "hour": 3, "merchant_category": "crypto",
            "is_international": True, "is_card_present": False, "failed_pin_attempts": 4,
            "velocity_1h": 9, "distance_from_home_km": 800, "avg_amount": 1200,
            "channel": "card", "direction": "out", "counterparty_country": "CY",
            "hours_since_inflow": 1.0,
        }
    if st.button("Run origination agent", type="primary"):
        payload = {
            "application_id": app_id,
            "customer_id": "CUST041",
            "kyc_text": kyc_text,
            "age": 29,
            "annual_income": income,
            "employment_years": 6,
            "existing_debt": debt,
            "loan_amount": amount,
            "loan_term_months": 36,
            "credit_history_years": 7,
            "late_payments_24m": late,
            "credit_utilization": util,
            "dependents": 0,
            "sample_transaction": sample_txn,
            "recent_transactions": [sample_txn] if sample_txn else None,
        }
        decision = ENG["agent"].run(payload)
        kind = "ok" if decision.outcome == "approve" else "bad" if decision.outcome == "reject" else "warn"
        st.markdown(badge(decision.outcome.replace("_", " ").upper(), kind), unsafe_allow_html=True)
        st.write("**Rationale**")
        for line in decision.rationale:
            st.write(f"- {line}")
        for step in decision.steps:
            with st.expander(f"{step.name} · {step.status}"):
                st.json(step.detail)


PAGES = {
    "Overview": page_home,
    "Fraud Sentinel": page_fraud,
    "Credit Underwriting": page_credit,
    "AML Watch": page_aml,
    "Customer Copilot": page_chat,
    "KYC Intake": page_kyc,
    "Spend Insights": page_spend,
    "Market Pulse": page_news,
    "Robo-Advisor": page_robo,
    "Loan Origination Agent": page_agent,
}


def main() -> None:
    st.sidebar.markdown("### NexusBank AI")
    st.sidebar.caption("Retail banking intelligence")
    choice = st.sidebar.radio("Modules", list(PAGES), index=0)
    st.sidebar.markdown("---")
    st.sidebar.write("Config:", ENG["cfg"]["app"]["version"])
    st.sidebar.write("Currency:", ENG["cfg"]["app"]["currency"])
    PAGES[choice]()


main()
