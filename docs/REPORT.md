# NexusBank AI: An Integrated Application of Machine Learning in Retail Banking Operations

**Student:** Sukhada Dhingra  
**PRN:** 24070126505  

**Submission PDF (report + screenshots):** [Sukhada_Dhingra_24070126505_NexusBank_AI_Report.pdf](./Sukhada_Dhingra_24070126505_NexusBank_AI_Report.pdf)

Short report (assignment reference guide). Course outcomes addressed: CO3 (applied AI functions in a FinTech system), CO4 (communication of design, use and impact).

---

## 1. Need analysis / statement of need

Indian retail banking has shifted a large share of daily activity onto UPI, cards, mobile origination and video KYC. That shift created four operational gaps that a single product team cannot close with rule engines alone.

**Fraud and authorisation.** NPCI and member banks already run velocity and device checks, but new-merchant and cross-border patterns still leak into the authorisation stream. A night-time crypto purchase on a card that normally buys groceries is statistically rare; it is also easy for a first-line officer to miss if the only signal is a raw amount. The bank needs a score that combines an anomaly model with a short list of reasons.

**Credit decisioning at the edge of policy.** Digital personal loans are booked in minutes. Bureau data and stated income are available, yet many files sit in a grey band: not clean enough for straight-through approve, not weak enough for an automatic decline. Officers need a probability of default (PD), a grade, and the two or three features that actually moved the file.

**AML and KYC load.** The Prevention of Money Laundering Act (PMLA) and RBI KYC Directions require banks to look for structuring, rapid movement of funds and high-risk geographies, and to classify identity documents before an account or loan is opened. Analysts cannot read every ledger line or every OCR dump. They need a first-pass typology score and a document type with extracted PAN/Aadhaar patterns.

**Advice and service at scale.** Call-centre intent routing, merchant categorisation for personal-finance views, a simple SIP mix for first-time investors, and a headline tone feed for the treasury desk are all “Unit 3 / Unit 4” problems: classification, clustering, and a light sentiment layer. They do not require a foundation model if the taxonomy is closed.

The statement of need is therefore: **build one simulator that a student or a bank operations intern can run locally, in which several related AI modules share data conventions and can be composed into a loan-origination workflow.** The goal is not to invent a new learning algorithm. The goal is to show that fraud, credit, AML, KYC and NLP can sit in one maintainable codebase with tests, a console and an API.

NexusBank AI is that simulator. All training rows are synthetic (INR amounts, Indian merchants, PAN/Aadhaar-shaped text, RBI/Nifty-style headlines). No customer secret leaves a bank. The limitation is stated up front in Section 5: accuracy on planted labels is not a claim about live books.

---

## 2. Technical functionality

The application is a library of functions behind two faces: a Streamlit operations console (`src/app.py`) and a FastAPI service (`src/api.py`). Nine modules live under `src/`. Thresholds are externalised in `config/settings.yaml`.

### 2.1 Fraud Sentinel

`FraudDetector` trains an Isolation Forest on numeric features: amount, hour, international flag, card-present flag, PIN failures, one-hour velocity, distance from home, a merchant-risk prior, and amount relative to the customer’s typical ticket. Isolation Forest is unsupervised; it learns a dense region of “normal” spend. At score time the decision function is mapped to a 0–100 risk. A small rule layer then adds reasons (night-time cross-border use, velocity, high-risk MCC, and so on) and can lift the score. Outputs are `typical / review / high_risk` and an action (`allow`, `step_up_auth`, `block_and_alert`). This matches how a real fraud desk works: a model score plus a narrative.

### 2.2 Credit underwriting

`CreditScorer` is a gradient-boosting classifier on enriched loan files (debt-to-income and loan-to-income are derived). The positive class is default. The console shows PD, a letter grade A–E from PD bands, and a policy decision (`approve`, `manual_review`, `decline`). Feature importances are shown so the officer can challenge the file. This is the Unit 3 credit-scoring pattern: supervised tabular learning plus a policy wrapper, not a raw model dump.

### 2.3 AML Watch

`AmlMonitor` does not pretend to be a deep graph model. It implements the typologies taught in financial-crime courses: amounts parked just under a cash-transaction-report style threshold (structuring), many geographies on a large turnover (layering), counterparties in a configured high-risk set, money leaving within a few hours of an inflow, and a high cash-channel share. Each hit adds to a 0–100 alert score. The module is deliberately readable so it can be defended in an internal audit.

### 2.4 Customer Copilot (NLP)

`BankingChatbot` uses a TF-IDF vectoriser (unigrams and bigrams) and multinomial logistic regression over a closed intent set: greeting, balance, mini-statement, transfers, card block/unblock, PIN, loans, EMI, KYC, fraud report, investments, complaints, branch locator, goodbye, and fallback. Below a confidence floor the bot refuses to guess and marks a handoff. Fraud and complaint intents also request a human. Replies are templates. The educational point is intent classification for a regulated channel, not open-ended generation.

### 2.5 KYC Intake

`KycClassifier` types OCR-like text into Aadhaar, PAN, passport, driving licence, utility bill, bank statement or unknown. Regular expressions then pull PAN (`AAAAA9999A`), spaced Aadhaar groups, passport and DL patterns. Policy accepts only the identity classes above a confidence floor. A grocery receipt therefore fails even if the language model is unsure. This is document intelligence at assignment scale: classify, extract, gate.

### 2.6 Spend Insights

Merchant strings in India are noisy (`SWIGGY *ORDER #882`, `IOCL PETROL PUMP`). A character n-gram classifier is a standard way to absorb that noise. The module also aggregates a sample month and flags any category that consumes more than a configured share of spend.

### 2.7 Market Pulse

Headlines are labelled positive / negative / neutral. A TF-IDF classifier is blended with a small finance lexicon (rally, NPA, downgrade, inflows, and similar). Treasury staff get a pulse, not a trading signal. Expected return figures elsewhere in the app are illustrative.

### 2.8 Robo-Advisor

A questionnaire (age, horizon, surplus, emergency months, loss tolerance, knowledge) is mapped to a 0–100 risk score and a sleeve: conservative, moderate, growth, aggressive. Weights over equity, debt, gold and liquid are clipped by policy caps. K-Means on historical synthetic profiles supplies a nearest cluster id so the student can see unsupervised grouping next to the rule sleeve. This is Unit 4 wealth-tech: profiling plus a constrained allocator.

### 2.9 Loan Origination Agent

`LoanOriginationAgent` is the composition layer the assignment calls “agentic automation.” It does not sample a large language model. It is a deterministic planner that calls KYC, credit, fraud and AML in a fixed order and then applies a policy:

- failed KYC → reject  
- PD above the auto-reject band → reject  
- high fraud or high AML → refer to financial-crime (FICO)  
- low PD and quiet crime screens → approve  
- otherwise → refer to a credit officer with the memo  

The console prints every step. That is the pedagogical core: models are useless in a bank if they cannot be chained into a workflow with an audit trail.

---

## 3. Architecture

The system is a three-layer desktop/server application.

```
[ Streamlit console ]     [ FastAPI clients / examples ]
           \                     /
            \                   /
             v                 v
            [ src/* intelligence modules ]
                    |
                    +-- config/settings.yaml
                    +-- dataset/*.csv
                    +-- models/*.joblib
```

**Presentation.** Streamlit hosts one page per module plus an overview dashboard (counts, planted fraud mix). FastAPI exposes the same functions as JSON for scripts and tests (`/fraud/score`, `/credit/score`, `/chat`, `/kyc/assess`, `/aml/evaluate`, `/spend/*`, `/news/sentiment`, `/wealth/advise`, `/agent/originate`).

**Intelligence.** Each module is a Python class with `fit` (where a model exists) and a `predict` / `assess` / `respond` method that returns a dataclass and a `to_dict()` for the API. Training is centralised in `src/train_models.py`. Sklearn pipelines (TfidfVectorizer + LogisticRegression, IsolationForest, GradientBoostingClassifier, KMeans) are stored with joblib.

**Data.** `dataset/generate_data.py` writes eight CSVs with a fixed RNG seed so metrics do not drift. Isolation Forest ignores the planted `is_fraud` label at train time; the label is only used to sanity-check that extreme synthetic events sit in the tail. Credit, NLP and sentiment models are supervised on the planted labels.

**Configuration and packaging.** YAML keeps policy numbers out of source. Docker and docker-compose wrap the console (port 8501) and the API (port 8000). Pytest uses `pythonpath = src` and trains artifacts before collection if they are missing.

**Design choices.** No paid LLM, vector database or bureau API. That is intentional. The assignment asks for a useful application with several modules, not a cloud bill. Offline sklearn models also make the work reproducible on a lab machine.

**Information flow for a loan file.** OCR text and application fields enter the agent. KYC returns type and accept/reject. Credit returns PD and grade. A related card event (or a harmless default event) is scored for fraud. Recent ledger lines are scored for AML. Policy writes `approve` / `reject` / `refer_credit` / `refer_fico`. The same path can be driven from the console or `POST /agent/originate`.

---

## 4. Usage / scope

### 4.1 How to run

From a clone with Python 3.10+:

```text
pip install -r requirements.txt
python dataset/generate_data.py
python src/train_models.py
PYTHONPATH=src streamlit run src/app.py
```

The console opens on port 8501. Sidebar entries map one-to-one to the modules in Section 2. Fraud Sentinel includes buttons for a grocery UPI and a night-time crypto spend so a demonstrator does not have to type. The origination agent has a checkbox that injects a high-risk card event to show a FICO referral.

The API is optional for the demo but required for the automated tests:

```text
PYTHONPATH=src uvicorn api:app --app-dir src --port 8000
```

Examples under `examples/` print JSON for fraud pairs, a full origination memo, a chat script, and two SIP profiles. `pytest` covers high versus low fraud, PD ordering, chatbot intents, PAN accept / receipt reject, AML structuring, agent KYC reject, and `/health`.

Docker: `docker compose up --build console`.

### 4.2 In scope

- Teaching and assignment demonstration of AI functions used in retail banks  
- Local experimentation with thresholds in `config/settings.yaml`  
- Extension (new intents, new MCC codes, a real CSV drop-in with the same columns)

### 4.3 Out of scope

- Live core-banking, UPI switch, or credit-bureau connectivity  
- Fair-lending validation on real protected attributes  
- Production AML graph analytics, device fingerprinting, or sanctioned-party screening  
- Investment advice to the public; expected returns in the robo module are textbook constants  
- Generative “free chat”; the copilot only routes closed intents  

If a bank were to industrialise this design, the next engineering steps would be model monitoring, maker-checker on policy YAML, encryption of document text, and a challenger model for PD. Those steps are deliberately left out so the repository stays small enough to mark.

---

## 5. Impact overview

**Operations.** A fraud score with reasons shortens the time between authorisation and a block. A PD with a grade reduces bounce between sales and credit. AML typology tags give the financial-crime team a queue ordered by severity instead of a raw dump of every NEFT. KYC typing cuts the “please re-upload” loop when the file is clearly a utility bill.

**Customers.** Faster card hot-list via the copilot, clearer SIP sleeves for people who will never open a mean-variance spreadsheet, and spend categories that make a passbook readable. The same tools can also deny or delay a genuine customer if the model is mis-calibrated; that is why every score is paired with a reason and a human-referral path.

**Compliance and teaching.** The agent memo is the artefact an auditor wants: which tool ran, what it returned, which rule fired. For the course, the same memo is evidence that Unit 3 (credit, fraud, AML, KYC) and Unit 4 (NLP, sentiment, robo-allocation, workflow automation) were implemented as working code, not as slides.

**Inclusion and harm.** Synthetic data hides a real problem: PD models trained on bureau files can encode historic denial patterns. A student system that only uses income, tenure and utilisation still needs a fairness discussion before it touches live applicants. Sentiment on headlines can amplify market rumour. The README disclaimer exists for that reason.

**Measured behaviour in this repo.** After training on the generator seed, the credit hold-out AUC, chatbot accuracy and document-type accuracy are written to `models/training_metrics.json`. Tests lock qualitative behaviour: a grocery UPI is not blocked; a night crypto blast is high risk; “block my debit card” maps to `card_block`; a PAN scrape is accepted; a parking ticket is not; three sub-threshold cash legs raise a structuring alert; failed KYC stops origination.

---

## 6. Conclusion

NexusBank AI is a compact FinTech application that treats AI as a set of bank jobs rather than as a single chatbot. Isolation Forest, gradient boosting, logistic text classifiers, typology rules and a four-step origination planner are enough to demonstrate the Unit 3 and Unit 4 outcomes: the software performs the intended tasks, the tree is readable, and this report states why the work exists, how it is built, how to run it, and what it can and cannot change in a real bank.

---

## References (for further reading)

1. Reserve Bank of India, *Master Direction – Know Your Customer (KYC) Direction*.  
2. Government of India, *Prevention of Money Laundering Act, 2002*, and PML Rules.  
3. NPCI, UPI product documentation (velocity, limits, dispute handling).  
4. Basel Committee on Banking Supervision, *Sound credit risk assessment* (PD as a policy input, not a sole decision).  
5. Pedregosa et al., “Scikit-learn: Machine Learning in Python,” *JMLR*, 2011.  
6. Liu, Ting and Zhou, “Isolation Forest,” *ICDM*, 2008.
