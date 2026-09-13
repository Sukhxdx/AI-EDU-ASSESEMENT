"""Build the assignment submission PDF for Sukhada Dhingra (PRN 24070126505)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "docs" / "screenshots"
OUT = ROOT / "docs" / "Sukhada_Dhingra_24070126505_NexusBank_AI_Report.pdf"

NAVY = HexColor("#0b1220")
TEAL = HexColor("#1b6b8a")
GOLD = HexColor("#c9a227")
INK = HexColor("#1a2433")
MUTED = HexColor("#4a5a6a")
RULE = HexColor("#c5d0da")
BAND = HexColor("#e8f1f6")

NAME = "Sukhada Dhingra"
PRN = "24070126505"


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle(
            "cover_kicker", parent=base["Normal"], fontName="Times-Bold",
            fontSize=11, textColor=GOLD, alignment=TA_CENTER, tracking=1.2,
        ),
        "cover_title": ParagraphStyle(
            "cover_title", parent=base["Title"], fontName="Times-Bold",
            fontSize=26, leading=32, textColor=white, alignment=TA_CENTER, spaceAfter=8,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", parent=base["Normal"], fontName="Times-Italic",
            fontSize=12, leading=16, textColor=HexColor("#d7e4ee"), alignment=TA_CENTER,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta", parent=base["Normal"], fontName="Times-Roman",
            fontSize=12, leading=18, textColor=white, alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Times-Bold",
            fontSize=16, leading=20, textColor=NAVY, spaceBefore=14, spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Times-Bold",
            fontSize=13, leading=17, textColor=TEAL, spaceBefore=10, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Times-Roman",
            fontSize=11, leading=15, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName="Times-Italic",
            fontSize=9.5, leading=12, textColor=MUTED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=12,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"], fontName="Times-Roman",
            fontSize=11, leading=15, textColor=INK, leftIndent=8, spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "code", parent=base["Code"], fontName="Courier",
            fontSize=8.5, leading=12, textColor=NAVY, backColor=BAND,
            leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=8,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"], fontName="Times-Roman",
            fontSize=8, textColor=MUTED, alignment=TA_CENTER,
        ),
        "figtitle": ParagraphStyle(
            "figtitle", parent=base["Normal"], fontName="Times-Bold",
            fontSize=11, leading=14, textColor=NAVY, spaceBefore=6, spaceAfter=4,
        ),
    }


def _header_footer(canvas, doc) -> None:
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 14 * mm, w, 14 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, h - 14.8 * mm, w, 1.2 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Times-Bold", 9)
    canvas.drawString(16 * mm, h - 9 * mm, f"{NAME}  |  PRN {PRN}")
    canvas.setFont("Times-Roman", 9)
    canvas.drawRightString(w - 16 * mm, h - 9 * mm, "NexusBank AI  —  FinTech Assignment Report")
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Times-Roman", 8)
    canvas.drawString(16 * mm, 5 * mm, "AI in Banking and Finance  |  Units 3 and 4  |  CO3 / CO4")
    canvas.drawRightString(w - 16 * mm, 5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _cover_page(canvas, doc) -> None:
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, h - 22 * mm, w, 8 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, h - 22.8 * mm, w, 1.6 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 38 * mm, w, 2 * mm, fill=1, stroke=0)
    canvas.restoreState()
    _header_footer(canvas, doc)


def _shot(path: Path, max_w: float = 170 * mm, max_h: float = 105 * mm) -> Image | None:
    if not path.exists():
        return None
    img = PILImage.open(path)
    iw, ih = img.size
    scale = min(max_w / iw, max_h / ih)
    return Image(str(path), width=iw * scale, height=ih * scale)


def _figure(styles, filename: str, title: str, caption: str, max_h: float = 105 * mm):
    path = SHOTS / filename
    story = [Paragraph(title, styles["figtitle"])]
    image = _shot(path, max_h=max_h)
    if image is None:
        story.append(Paragraph(f"[Screenshot missing: {filename}]", styles["caption"]))
    else:
        story.append(image)
    story.append(Paragraph(caption, styles["caption"]))
    return KeepTogether(story)


def _p(styles, text: str):
    return Paragraph(text, styles["body"])


def build() -> Path:
    styles = _styles()
    SHOTS.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=20 * mm,
        bottomMargin=16 * mm,
        title=f"NexusBank AI — {NAME} — {PRN}",
        author=NAME,
    )
    story: list = []

    # Cover content sits on the first page; extra top padding so it clears the banner.
    story.append(Spacer(1, 18 * mm))
    story.append(Paragraph("ASSIGNMENT SUBMISSION", styles["cover_kicker"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("NexusBank AI", styles["cover_title"]))
    story.append(Paragraph(
        "An integrated artificial-intelligence platform for retail banking operations",
        styles["cover_sub"],
    ))
    story.append(Spacer(1, 14 * mm))

    meta = [
        [Paragraph("<b>Student name</b>", styles["cover_meta"]),
         Paragraph(NAME, styles["cover_meta"])],
        [Paragraph("<b>PRN</b>", styles["cover_meta"]),
         Paragraph(PRN, styles["cover_meta"])],
        [Paragraph("<b>Programme / paper</b>", styles["cover_meta"]),
         Paragraph("AI in Banking and Finance (Units 3 and 4)", styles["cover_meta"])],
        [Paragraph("<b>Course outcomes</b>", styles["cover_meta"]),
         Paragraph("CO3 — applied AI functions; CO4 — design, use and impact", styles["cover_meta"])],
        [Paragraph("<b>Application</b>", styles["cover_meta"]),
         Paragraph("NexusBank AI (simulator, Streamlit + FastAPI)", styles["cover_meta"])],
        [Paragraph("<b>GitHub repository</b>", styles["cover_meta"]),
         Paragraph("Sukhxdx/AI-EDU-ASSESEMENT — branch cursor/nexusbank-ai-fintech-38c8", styles["cover_meta"])],
        [Paragraph("<b>Pull request</b>", styles["cover_meta"]),
         Paragraph("https://github.com/Sukhxdx/AI-EDU-ASSESEMENT/pull/12", styles["cover_meta"])],
    ]
    table = Table(meta, colWidths=[52 * mm, 118 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#122033")),
        ("BOX", (0, 0), (-1, -1), 0.4, GOLD),
        ("INNERGRID", (0, 0), (-1, -1), 0.2, HexColor("#1f4b63")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 16 * mm))
    story.append(Paragraph(
        "This PDF is the short report required by the assignment: need analysis, "
        "technical functionality, architecture, usage/scope, impact, and original "
        "screenshots of the running software. The application is a simulator trained "
        "on synthetic Indian retail-banking data. It is not a live bank system.",
        styles["cover_sub"],
    ))
    story.append(PageBreak())

    # From page 2 onward, body uses dark text; cover used white text.
    story.append(Paragraph("1. Need analysis / statement of need", styles["h1"]))
    story.append(_p(styles,
        "Indian retail banking has moved a large share of daily activity onto UPI, cards, "
        "mobile origination and video KYC. That shift left four operational gaps that a "
        "single product team cannot close with static rule engines alone."
    ))
    story.append(_p(styles,
        "<b>Fraud and authorisation.</b> NPCI and member banks already run velocity and "
        "device checks, but new-merchant and cross-border patterns still leak into the "
        "authorisation stream. A night-time crypto purchase on a card that normally buys "
        "groceries is statistically rare; it is also easy for a first-line officer to miss "
        "if the only signal is a raw amount. The bank needs a score that combines an "
        "anomaly model with a short list of reasons."
    ))
    story.append(_p(styles,
        "<b>Credit decisioning at the edge of policy.</b> Digital personal loans are booked "
        "in minutes. Many files sit in a grey band: not clean enough for straight-through "
        "approve, not weak enough for an automatic decline. Officers need a probability of "
        "default (PD), a grade, and the two or three features that actually moved the file."
    ))
    story.append(_p(styles,
        "<b>AML and KYC load.</b> The Prevention of Money Laundering Act (PMLA) and RBI KYC "
        "Directions require banks to look for structuring, rapid movement of funds and "
        "high-risk geographies, and to classify identity documents before an account or loan "
        "is opened. Analysts cannot read every ledger line or every OCR dump."
    ))
    story.append(_p(styles,
        "<b>Advice and service at scale.</b> Call-centre intent routing, merchant "
        "categorisation, a simple SIP mix for first-time investors, and a headline tone feed "
        "are Unit 3 / Unit 4 problems: classification, clustering, and a light sentiment layer."
    ))
    story.append(_p(styles,
        "The statement of need is therefore: <b>build one simulator that can be run locally, "
        "in which several related AI modules share data conventions and can be composed into "
        "a loan-origination workflow.</b> The goal is not a new learning algorithm. The goal "
        "is to show that fraud, credit, AML, KYC and NLP can sit in one maintainable codebase "
        "with tests, a console and an API."
    ))
    story.append(_p(styles,
        "NexusBank AI is that simulator. Training rows are synthetic (INR amounts, Indian "
        "merchants, PAN/Aadhaar-shaped text, RBI/Nifty-style headlines). No customer secret "
        "leaves a bank. Accuracy on planted labels is not a claim about live books."
    ))

    story.append(Paragraph("2. Technical functionality", styles["h1"]))
    story.append(_p(styles,
        "The application is a library of functions behind two faces: a Streamlit operations "
        "console (<font face='Courier'>src/app.py</font>) and a FastAPI service "
        "(<font face='Courier'>src/api.py</font>). Nine modules live under "
        "<font face='Courier'>src/</font>. Thresholds are in "
        "<font face='Courier'>config/settings.yaml</font>."
    ))
    story.append(Paragraph("2.1 Fraud Sentinel", styles["h2"]))
    story.append(_p(styles,
        "Isolation Forest is trained on amount, hour, international flag, card-present flag, "
        "PIN failures, one-hour velocity, distance from home, a merchant-risk prior, and "
        "amount relative to the customer’s typical ticket. The decision function is mapped "
        "to a 0–100 risk. A rule layer adds reasons (night-time cross-border use, velocity, "
        "high-risk MCC) and can lift the score. Outputs are typical / review / high_risk and "
        "an action (allow, step_up_auth, block_and_alert)."
    ))
    story.append(Paragraph("2.2 Credit underwriting", styles["h2"]))
    story.append(_p(styles,
        "A gradient-boosting classifier estimates probability of default on enriched loan "
        "files (debt-to-income and loan-to-income are derived). The console shows PD, a "
        "letter grade A–E, and a policy decision (approve, manual_review, decline). Feature "
        "importances are shown so the officer can challenge the file."
    ))
    story.append(Paragraph("2.3 AML Watch", styles["h2"]))
    story.append(_p(styles,
        "Typology scoring covers amounts parked just under a cash-transaction-report style "
        "threshold (structuring), many geographies on a large turnover (layering), "
        "counterparties in a configured high-risk set, money leaving within a few hours of "
        "an inflow, and a high cash-channel share. Each hit adds to a 0–100 alert score."
    ))
    story.append(Paragraph("2.4 Customer Copilot (NLP)", styles["h2"]))
    story.append(_p(styles,
        "TF-IDF (unigrams and bigrams) plus logistic regression routes a closed intent set: "
        "greeting, balance, mini-statement, transfers, card block/unblock, PIN, loans, EMI, "
        "KYC, fraud report, investments, complaints, branch locator, goodbye, and fallback. "
        "Below a confidence floor the bot refuses to guess and marks a handoff. Replies are "
        "templates. The educational point is intent classification for a regulated channel, "
        "not open-ended generation."
    ))
    story.append(Paragraph("2.5 KYC Intake", styles["h2"]))
    story.append(_p(styles,
        "OCR-like text is typed into Aadhaar, PAN, passport, driving licence, utility bill, "
        "bank statement or unknown. Regular expressions pull PAN (AAAAA9999A), spaced Aadhaar "
        "groups, passport and DL patterns. Policy accepts only identity classes above a "
        "confidence floor. A grocery receipt therefore fails even if the language model is unsure."
    ))
    story.append(Paragraph("2.6 Spend Insights, Market Pulse, Robo-Advisor", styles["h2"]))
    story.append(_p(styles,
        "Character n-grams classify noisy merchant strings (SWIGGY *ORDER #882). Headlines "
        "are scored positive / negative / neutral with TF-IDF plus a small finance lexicon. "
        "A questionnaire maps to a 0–100 risk score and a SIP sleeve (conservative, moderate, "
        "growth, aggressive) over equity, debt, gold and liquid. K-Means on synthetic "
        "profiles supplies a nearest cluster id."
    ))
    story.append(Paragraph("2.7 Loan Origination Agent", styles["h2"]))
    story.append(_p(styles,
        "This is the composition layer the assignment calls agentic automation. A deterministic "
        "planner calls KYC, credit, fraud and AML in a fixed order, then applies policy: "
        "failed KYC → reject; PD above the auto-reject band → reject; high fraud or high AML → "
        "refer to financial-crime (FICO); low PD and quiet crime screens → approve; otherwise → "
        "refer to a credit officer with the memo. The console prints every step."
    ))

    story.append(Paragraph("3. Architecture", styles["h1"]))
    story.append(_p(styles,
        "Three layers: presentation (Streamlit console and FastAPI), intelligence (sklearn "
        "modules with fit/predict), and data (synthetic CSVs plus joblib artefacts). Policy "
        "numbers stay in YAML. Docker wraps the console (port 8501) and the API (port 8000). "
        "No paid LLM, vector database or bureau API is required so the work runs on a lab machine."
    ))
    story.append(Paragraph(
        "Streamlit console / FastAPI clients<br/>"
        "&nbsp;&nbsp;&nbsp;→&nbsp; src/* intelligence modules<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ config/settings.yaml &nbsp; dataset/*.csv &nbsp; models/*.joblib",
        styles["code"],
    ))
    story.append(_p(styles,
        "For a loan file, OCR text and application fields enter the agent. KYC returns type "
        "and accept/reject. Credit returns PD and grade. A related card event is scored for "
        "fraud. Recent ledger lines are scored for AML. Policy writes approve / reject / "
        "refer_credit / refer_fico."
    ))

    story.append(Paragraph("4. Usage / scope", styles["h1"]))
    story.append(Paragraph("4.1 How to run", styles["h2"]))
    story.append(Paragraph(
        "pip install -r requirements.txt<br/>"
        "python dataset/generate_data.py<br/>"
        "python src/train_models.py<br/>"
        "PYTHONPATH=src streamlit run src/app.py<br/><br/>"
        "Console: http://localhost:8501<br/>"
        "API: PYTHONPATH=src uvicorn api:app --app-dir src --port 8000<br/>"
        "Tests: PYTHONPATH=src pytest",
        styles["code"],
    ))
    story.append(_p(styles,
        "<b>In scope:</b> teaching demonstration of AI functions used in retail banks; local "
        "experimentation with thresholds; extension with new intents or MCC codes.<br/>"
        "<b>Out of scope:</b> live core-banking or bureau connectivity; fair-lending validation "
        "on real protected attributes; production AML graph analytics; investment advice to the "
        "public; generative free chat."
    ))

    story.append(Paragraph("5. Impact overview", styles["h1"]))
    story.append(_p(styles,
        "A fraud score with reasons shortens the time between authorisation and a block. A PD "
        "with a grade reduces bounce between sales and credit. AML typology tags give the "
        "financial-crime team a queue ordered by severity. KYC typing cuts the “please re-upload” "
        "loop when the file is clearly a utility bill. Customers get a faster card hot-list, a "
        "readable SIP sleeve, and spend categories that make a passbook usable."
    ))
    story.append(_p(styles,
        "The same tools can also delay a genuine customer if a model is mis-calibrated; that is "
        "why every score is paired with a reason and a human-referral path. Synthetic data hides "
        "a real fairness problem: PD models trained on bureau files can encode historic denial "
        "patterns. This student system must not be pointed at live applicants without that debate."
    ))
    story.append(_p(styles,
        "Measured behaviour locked by tests: a grocery UPI is not blocked; a night crypto blast "
        "is high risk; “block my debit card” maps to card_block; a PAN scrape is accepted; a "
        "parking ticket is not; three sub-threshold cash legs raise a structuring alert; failed "
        "KYC stops origination. Eighteen pytest cases passed on the submission build."
    ))

    story.append(Paragraph("6. Conclusion", styles["h1"]))
    story.append(_p(styles,
        "NexusBank AI treats AI as a set of bank jobs rather than as a single chatbot. Isolation "
        "Forest, gradient boosting, logistic text classifiers, typology rules and a four-step "
        "origination planner demonstrate the Unit 3 and Unit 4 outcomes: the software performs "
        "the intended tasks, the tree is readable, and this report states why the work exists, "
        "how it is built, how to run it, and what it can and cannot change in a real bank."
    ))

    story.append(Paragraph("References", styles["h1"]))
    for ref in [
        "Reserve Bank of India, Master Direction – Know Your Customer (KYC) Direction.",
        "Government of India, Prevention of Money Laundering Act, 2002, and PML Rules.",
        "NPCI, UPI product documentation (velocity, limits, dispute handling).",
        "Basel Committee on Banking Supervision, Sound credit risk assessment.",
        "Pedregosa et al., “Scikit-learn: Machine Learning in Python,” JMLR, 2011.",
        "Liu, Ting and Zhou, “Isolation Forest,” ICDM, 2008.",
    ]:
        story.append(Paragraph("• " + ref, styles["bullet"]))

    story.append(PageBreak())
    story.append(Paragraph("7. Original screenshots of the running application", styles["h1"]))
    story.append(_p(styles,
        "The figures below are screenshots of the Streamlit console running at "
        "http://localhost:8501. The sidebar and overview banner show the student name "
        f"<b>{NAME}</b> and <b>PRN {PRN}</b>. Each module was exercised with a live input, "
        "not only opened."
    ))

    figures = [
        ("01_overview.png", "Figure 1. Overview dashboard",
         "Home screen with KPIs (4,000 card/UPI events, 2,500 loan files), module list, "
         "and student identity on the banner and sidebar."),
        ("02_fraud_high_risk.png", "Figure 2. Fraud Sentinel — suspicious night crypto spend",
         "Scenario loads an international crypto authorisation at 02:00. Result: HIGH_RISK, "
         "block_and_alert, score 100/100, with readable policy reasons."),
        ("03_fraud_typical.png", "Figure 3. Fraud Sentinel — typical grocery UPI",
         "Same model on a grocery UPI. Result: TYPICAL, allow, score in the thirties. "
         "Shows the detector is not flagging ordinary spend."),
        ("04_credit.png", "Figure 4. Credit underwriting",
         "Gradient-boosted PD with letter grade and policy decision (approve / manual_review / "
         "decline) plus a feature-contribution chart."),
        ("05_aml.png", "Figure 5. AML Watch",
         "Customer ledger scored for structuring, high-risk geography, rapid in-out and cash intensity."),
        ("06_chat.png", "Figure 6. Customer Copilot",
         "Utterance “block my debit card” classified as card_block with a templated hot-list reply."),
        ("07_kyc.png", "Figure 7. KYC Intake",
         "PAN OCR text typed as pan, PAN pattern extracted, document accepted for digital KYC."),
        ("08_spend.png", "Figure 8. Spend Insights",
         "Merchant-string categorisation aggregated into a monthly mix (pie + table)."),
        ("09_news.png", "Figure 9. Market Pulse",
         "Financial headlines labelled positive / negative / neutral."),
        ("10_robo.png", "Figure 10. Robo-Advisor",
         "Questionnaire mapped to a risk bucket and SIP sleeve (equity, debt, gold, liquid)."),
        ("11_agent_approve.png", "Figure 11. Loan Origination Agent — clean file",
         "Planner chains KYC → credit → fraud → AML. Outcome APPROVE when screens are quiet."),
        ("12_agent_refer.png", "Figure 12. Loan Origination Agent — high-risk card event",
         "Same file with an injected night crypto event. Outcome REFER FICO: financial-crime "
         "screen elevated; human investigation mandatory."),
    ]
    for filename, title, caption in figures:
        story.append(_figure(styles, filename, title, caption))

    story.append(Paragraph("8. Declaration", styles["h1"]))
    story.append(_p(styles,
        f"I, {NAME}, PRN {PRN}, submit this report and the accompanying software as my "
        "FinTech assignment. The application is original work for this paper. Screenshots "
        "are of the running NexusBank AI console. The system is a teaching simulator and "
        "must not be used as a live credit, fraud, AML or investment decision engine."
    ))
    story.append(Spacer(1, 10 * mm))
    sign = [
        [Paragraph("<b>Name</b>", styles["body"]), Paragraph(NAME, styles["body"])],
        [Paragraph("<b>PRN</b>", styles["body"]), Paragraph(PRN, styles["body"])],
        [Paragraph("<b>Application</b>", styles["body"]), Paragraph("NexusBank AI", styles["body"])],
        [Paragraph("<b>GitHub PR</b>", styles["body"]),
         Paragraph("https://github.com/Sukhxdx/AI-EDU-ASSESEMENT/pull/12", styles["body"])],
    ]
    box = Table(sign, colWidths=[40 * mm, 130 * mm])
    box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, TEAL),
        ("BACKGROUND", (0, 0), (0, -1), BAND),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(box)

    def first_page(canvas, doc):
        _cover_page(canvas, doc)

    def later(canvas, doc):
        _header_footer(canvas, doc)

    doc.build(story, onFirstPage=first_page, onLaterPages=later)
    return OUT


if __name__ == "__main__":
    path = build()
    print(path, path.stat().st_size)
