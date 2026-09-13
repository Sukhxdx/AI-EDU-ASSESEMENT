# NexusBank AI

AI-assisted retail banking operations desk: fraud scoring, credit underwriting, AML screening, KYC intake, a customer copilot, spend categorisation, news sentiment, a robo-advisor, and an origination agent that chains those tools.

This repository is the working software and short report for a FinTech assignment focused on **AI in banking and finance** (Units 3 and 4). It is a **simulator**. It does not connect to a live core-banking system.

## Repository layout

```
README.md
requirements.txt
Dockerfile
docker-compose.yml
config/settings.yaml
dataset/                 # synthetic CSVs + generator
docs/REPORT.md           # short report (need, functions, architecture, usage, impact)
examples/                # command-line walkthroughs
models/                  # trained sklearn artifacts (created by training)
src/                     # application code
tests/                   # pytest suite
```

## What the modules do

| Module | AI approach | Banking job |
| --- | --- | --- |
| Fraud Sentinel | Isolation Forest + policy rules | Card / UPI anomaly scoring |
| Credit Underwriting | Gradient boosting PD model | Personal-loan grade and decision |
| AML Watch | Typology scoring | Structuring, rapid in-out, geo-risk |
| Customer Copilot | TF-IDF + logistic regression | Intent detection for retail chat |
| KYC Intake | Text classifier + regex fields | PAN / Aadhaar / passport typing |
| Spend Insights | Character n-gram classifier | Merchant-string categories |
| Market Pulse | TF-IDF sentiment + lexicon | Financial headline tone |
| Robo-Advisor | Risk score + K-Means clusters | SIP sleeve (equity, debt, gold, liquid) |
| Loan Origination Agent | Tool-using workflow | KYC → credit → fraud → AML memo |

## Quick start

Python 3.10+ is enough. No cloud API keys are required.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python dataset/generate_data.py
python src/train_models.py
```

### Operations console (Streamlit)

```bash
PYTHONPATH=src streamlit run src/app.py
```

Open http://localhost:8501. Use the sidebar to move between modules. Each screen accepts a live input; Fraud Sentinel and the origination agent also have canned scenarios.

### HTTP API (FastAPI)

```bash
PYTHONPATH=src uvicorn api:app --app-dir src --host 0.0.0.0 --port 8000
```

Docs: http://localhost:8000/docs

```bash
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"text":"block my debit card"}'
```

### Tests and examples

```bash
PYTHONPATH=src pytest
python examples/score_fraud.py
python examples/originate_loan.py
python examples/chat_session.py
python examples/robo_sip.py
```

### Docker

```bash
docker compose up --build console
# API on the side:
docker compose up --build api
```

## Configuration

Thresholds live in `config/settings.yaml` (fraud cut-offs, PD bands, AML amounts, KYC accept list, SIP floors). Retrain after data changes:

```bash
python dataset/generate_data.py
python src/train_models.py
```

## Report

The short assignment report is [docs/REPORT.md](docs/REPORT.md). It covers need analysis, technical functionality, architecture, usage/scope and impact.

**Submit this PDF** (name, PRN, report text, and screenshots of the running app):

[docs/Sukhada_Dhingra_24070126505_NexusBank_AI_Report.pdf](docs/Sukhada_Dhingra_24070126505_NexusBank_AI_Report.pdf)

Student: **Sukhada Dhingra** · PRN **24070126505**

## Disclaimer

Outputs are educational. They are not a credit decision, investment advice, or a substitute for RBI/PMLA controls in a licensed bank.
