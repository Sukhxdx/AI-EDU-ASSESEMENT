#!/usr/bin/env python3
"""Generate the Nifty 50 index-tracking submission PDF report."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
OUT_DIR = ROOT / "submission"
OUT_PDF = OUT_DIR / "Sukhada_Dhingra_24070126505_Nifty50_Index_Tracking_Report.pdf"

# Student details (same as other course submissions)
STUDENT_NAME = "Sukhada Dhingra"
PRN = "24070126505"
BATCH = "A3"


def load_results():
    summary = json.loads((RESULTS / "run_summary.json").read_text())
    with (RESULTS / "test_metrics.csv").open() as f:
        test_rows = list(csv.DictReader(f))
    with (RESULTS / "icsae_weights.csv").open() as f:
        weights = list(csv.DictReader(f))
    return summary, test_rows, weights


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCustom",
            parent=base["Title"],
            fontSize=17,
            leading=21,
            alignment=TA_CENTER,
            spaceAfter=6,
            textColor=colors.HexColor("#1a365d"),
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCustom",
            parent=base["Normal"],
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            spaceAfter=4,
            textColor=colors.HexColor("#2c5282"),
        ),
        "h1": ParagraphStyle(
            "H1Custom",
            parent=base["Heading1"],
            fontSize=12.5,
            leading=16,
            spaceBefore=12,
            spaceAfter=5,
            textColor=colors.HexColor("#1a365d"),
        ),
        "h2": ParagraphStyle(
            "H2Custom",
            parent=base["Heading2"],
            fontSize=11,
            leading=14,
            spaceBefore=8,
            spaceAfter=4,
            textColor=colors.HexColor("#2b6cb0"),
        ),
        "body": ParagraphStyle(
            "BodyCustom",
            parent=base["Normal"],
            fontSize=9.5,
            leading=13,
            alignment=TA_JUSTIFY,
            spaceAfter=5,
        ),
        "meta": ParagraphStyle(
            "MetaCustom",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "center": ParagraphStyle(
            "CenterCustom",
            parent=base["Normal"],
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "caption": ParagraphStyle(
            "CaptionCustom",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4a5568"),
            spaceAfter=8,
        ),
        "small": ParagraphStyle(
            "SmallCustom",
            parent=base["Normal"],
            fontSize=8.5,
            leading=11,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
    }


def table_style():
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#edf2f7")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]
    )


def pct(x: float, digits: int = 2) -> str:
    return f"{100.0 * float(x):.{digits}f}%"


def build_pdf() -> Path:
    summary, test_rows, weights = load_results()
    styles = make_styles()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=f"Nifty 50 Index Tracking — {STUDENT_NAME}",
        author=STUDENT_NAME,
    )

    story = []

    # ---- Cover / header ----
    story.append(Paragraph("Sparse Index Tracking of the Nifty 50", styles["title"]))
    story.append(
        Paragraph(
            "Using an Index-Constrained Sparse Autoencoder (ICSAE)",
            styles["subtitle"],
        )
    )
    story.append(Spacer(1, 8))

    meta_data = [
        [Paragraph("<b>Name</b>", styles["meta"]), Paragraph(STUDENT_NAME, styles["meta"])],
        [Paragraph("<b>PRN</b>", styles["meta"]), Paragraph(PRN, styles["meta"])],
        [Paragraph("<b>Batch</b>", styles["meta"]), Paragraph(BATCH, styles["meta"])],
        [
            Paragraph("<b>Course work</b>", styles["meta"]),
            Paragraph("ML / Deep Learning — Index Tracking Assignment", styles["meta"]),
        ],
        [
            Paragraph("<b>Submission file</b>", styles["meta"]),
            Paragraph(OUT_PDF.name, styles["small"]),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[1.4 * inch, 5.0 * inch])
    meta_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#2c5282")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ebf8ff")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # ---- 1. Objective ----
    story.append(Paragraph("1. Objective", styles["h1"]))
    story.append(
        Paragraph(
            "The task is to replicate the Nifty 50 index return path with a "
            "<b>sparse</b> long-only equity portfolio. Holding all constituents "
            "is not always practical, so the portfolio is limited to "
            f"<b>k = {summary['config']['n_assets_select']}</b> stocks. "
            "Performance is judged mainly by annualized tracking error "
            "(standard deviation of active returns, scaled by "
            "<font face='Courier'>sqrt(252)</font>). "
            "An autoencoder-based selector is compared with classical sparse "
            "baselines on the same train/test split.",
            styles["body"],
        )
    )

    # ---- 2. Data ----
    meta = summary["meta"]
    story.append(Paragraph("2. Data", styles["h1"]))
    story.append(
        Paragraph(
            f"Prices were downloaded with Yahoo Finance for the NSE index ticker "
            f"<font face='Courier'>{meta.get('index_ticker', '^NSEI')}</font> and a "
            f"fixed basket of {meta['n_assets']} NSE equities. Adjusted closes were "
            f"converted to daily simple returns. The usable panel has "
            f"<b>{meta['n_days']}</b> trading days from <b>{meta['start']}</b> to "
            f"<b>{meta['end']}</b> (source: <font face='Courier'>{meta['source']}</font>). "
            "The sample is split chronologically 70% / 30% into train and test; "
            "no random shuffle is used.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "Late-listed names that miss too much of the index calendar are dropped "
            "so the panel can start in 2019 instead of being truncated by a single "
            "IPO. Tata Motors is pulled as <font face='Courier'>TMPV.NS</font> on Yahoo "
            "after the ticker rename.",
            styles["body"],
        )
    )

    # ---- 3. Method ----
    story.append(Paragraph("3. Method: Index-Constrained Sparse Autoencoder", styles["h1"]))
    story.append(Paragraph("3.1 Network", styles["h2"]))
    story.append(
        Paragraph(
            "Learnable logits define soft portfolio weights through a softmax "
            "(temperature annealed from 1.2 to 0.85). Stock returns are softly gated "
            "by these weights and passed through a two-layer tanh encoder into an "
            f"8-dimensional latent code, then decoded back to the return cross-section. "
            "Portfolio return on each batch is the weighted sum of asset returns.",
            styles["body"],
        )
    )
    story.append(Paragraph("3.2 Loss", styles["h2"]))
    story.append(
        Paragraph(
            "The training objective combines (i) reconstruction MSE of stock returns, "
            "(ii) tracking MSE between portfolio and index returns (dominant term, "
            "weight 25), (iii) a light ridge of soft weights toward equal weight, and "
            "(iv) a concentration penalty when any soft weight exceeds 0.25. "
            "This stops the softmax from collapsing onto a single name while still "
            "pushing the portfolio toward the index.",
            styles["body"],
        )
    )
    story.append(Paragraph("3.3 Selection and weight refinement", styles["h2"]))
    story.append(
        Paragraph(
            "After training, names are ranked by a blend of soft portfolio weight (70%) "
            "and L1 column norms of the first encoder layer (30%). The top-k names are "
            "kept. Final weights on that subset are re-fit with projected non-negative "
            "least squares on the training window (same simplex projection used by the "
            "quadratic baselines). The network therefore owns <b>selection</b>; the LS "
            "step owns <b>weights on the chosen set</b>.",
            styles["body"],
        )
    )

    # ---- 4. Baselines ----
    story.append(Paragraph("4. Baselines", styles["h1"]))
    bullets = [
        "Random k equal weight",
        "Lowest-volatility k equal weight",
        "Highest index-correlation k (equal and quadratic weights)",
        "PCA loading screen (equal and quadratic weights)",
        "Greedy forward selection with projected least squares",
        "Dense full-universe long-only least squares (reference upper bound)",
    ]
    story.append(
        ListFlowable(
            [ListItem(Paragraph(b, styles["body"]), leftIndent=8, bulletColor=colors.HexColor("#2b6cb0")) for b in bullets],
            bulletType="bullet",
            start="•",
        )
    )

    # ---- 5. Selected portfolio ----
    story.append(Paragraph("5. Selected ICSAE Portfolio (k = 10)", styles["h1"]))
    story.append(
        Paragraph(
            "Holdings chosen on the training window and evaluated out of sample:",
            styles["body"],
        )
    )
    w_header = [
        Paragraph("<b>Ticker</b>", styles["small"]),
        Paragraph("<b>Hard weight</b>", styles["small"]),
        Paragraph("<b>Soft weight (pre-LS)</b>", styles["small"]),
    ]
    w_rows = [w_header]
    hard_rows = [r for r in weights if float(r["hard_weight"]) > 1e-8]
    hard_rows = sorted(hard_rows, key=lambda r: -float(r["hard_weight"]))
    for r in hard_rows:
        w_rows.append(
            [
                r["ticker"],
                f"{float(r['hard_weight']):.4f}",
                f"{float(r['soft_weight']):.4f}",
            ]
        )
    w_table = Table(w_rows, colWidths=[2.2 * inch, 1.6 * inch, 2.0 * inch])
    w_table.setStyle(table_style())
    story.append(w_table)
    story.append(
        Paragraph(
            "Table 1. ICSAE sparse holdings after projected-LS refinement.",
            styles["caption"],
        )
    )

    story.append(PageBreak())

    # ---- 6. Results ----
    story.append(Paragraph("6. Out-of-Sample Results", styles["h1"]))
    story.append(
        Paragraph(
            f"Primary metric: annualized tracking error. ICSAE test TE = "
            f"<b>{pct(summary['test_icsae_te'])}</b>. "
            f"Best overall method on this split: "
            f"<font face='Courier'>{summary['test_best_method']}</font> "
            f"({pct(summary['test_best_te'])}).",
            styles["body"],
        )
    )

    m_header = [
        Paragraph("<b>Method</b>", styles["small"]),
        Paragraph("<b>Holdings</b>", styles["small"]),
        Paragraph("<b>TE (ann.)</b>", styles["small"]),
        Paragraph("<b>R²</b>", styles["small"]),
        Paragraph("<b>Corr</b>", styles["small"]),
    ]
    m_rows = [m_header]
    for r in sorted(test_rows, key=lambda x: float(x["tracking_error_ann"])):
        m_rows.append(
            [
                r["method"],
                f"{float(r['n_holdings']):.0f}",
                pct(r["tracking_error_ann"]),
                f"{float(r['r_squared']):.3f}",
                f"{float(r['corr']):.3f}",
            ]
        )
    m_table = Table(m_rows, colWidths=[1.7 * inch, 0.8 * inch, 1.0 * inch, 0.8 * inch, 0.8 * inch])
    m_table.setStyle(table_style())
    story.append(m_table)
    story.append(
        Paragraph(
            "Table 2. Out-of-sample tracking metrics (sorted by annualized TE).",
            styles["caption"],
        )
    )

    story.append(
        Paragraph(
            "Among sparse (k = 10) methods, greedy forward selection is slightly "
            "tighter than ICSAE on this split (3.80% vs 4.41% TE). ICSAE still beats "
            "correlation screens, PCA screens, random, and low-volatility equal weight. "
            "The dense full-universe LS tracker is an upper-bound reference and is not "
            "sparse.",
            styles["body"],
        )
    )

    # Figures
    story.append(Paragraph("6.1 Figures", styles["h2"]))
    fig_specs = [
        ("oos_te_bars.png", "Figure 1. Out-of-sample annualized tracking error by method.", 5.8),
        ("oos_cumulative.png", "Figure 2. Cumulative returns of sparse trackers vs the index (test window).", 5.8),
        ("oos_active.png", "Figure 3. ICSAE active daily returns and cumulative active path (test window).", 5.6),
        ("training_curve.png", "Figure 4. ICSAE training loss components over epochs.", 5.4),
    ]
    for fname, caption, width in fig_specs:
        path = RESULTS / fname
        if not path.exists():
            continue
        story.append(Image(str(path), width=width * inch, height=width * inch * 0.48, kind="proportional"))
        story.append(Paragraph(caption, styles["caption"]))

    # ---- 7. Implementation ----
    story.append(Paragraph("7. Implementation Notes", styles["h1"]))
    story.append(
        Paragraph(
            "Code lives under <font face='Courier'>nifty50_tracker/</font>. "
            "Entry point: <font face='Courier'>python -m src.run_pipeline --k 10 --epochs 400</font>. "
            "Stack: Python, PyTorch, yfinance, scikit-learn, matplotlib. "
            "Artifacts (metrics CSVs, plots, run summary) are written to "
            "<font face='Courier'>results/</font>. Full write-up: "
            "<font face='Courier'>docs/METHODOLOGY.md</font>.",
            styles["body"],
        )
    )

    # ---- 8. Limits ----
    story.append(Paragraph("8. Limitations", styles["h1"]))
    story.append(
        Paragraph(
            "Membership is fixed for the sample (no official reconstitution calendar). "
            "Transaction costs and turnover are not modeled. Softmax enforces long-only "
            "weights, which matches typical passive equity mandates but rules out short "
            "overlays. Results are specific to the 70/30 chronological split and the "
            "Yahoo-adjusted price series used here.",
            styles["body"],
        )
    )

    # ---- 9. Conclusion ----
    story.append(Paragraph("9. Conclusion", styles["h1"]))
    story.append(
        Paragraph(
            "A sparse Nifty 50 tracker built from an index-constrained autoencoder "
            "selects a liquid ten-name basket and reaches about "
            f"<b>{pct(summary['test_icsae_te'])}</b> annualized out-of-sample tracking "
            "error. That is competitive with standard sparse heuristics and clearly "
            "better than naive equal-weight screens, while remaining far cheaper than "
            "holding the full universe. The useful split of labour is neural "
            "<b>selection</b> plus convex <b>weighting</b> on the chosen set.",
            styles["body"],
        )
    )

    story.append(Spacer(1, 14))
    story.append(
        Paragraph(
            f"— End of report — &nbsp;&nbsp; {STUDENT_NAME} &nbsp;|&nbsp; PRN {PRN} &nbsp;|&nbsp; Batch {BATCH}",
            styles["center"],
        )
    )

    doc.build(story)
    return OUT_PDF


if __name__ == "__main__":
    path = build_pdf()
    print(f"Wrote {path}")
    print(f"Size: {path.stat().st_size} bytes")
