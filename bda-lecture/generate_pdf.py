#!/usr/bin/env python3
"""Generate a BDA lecture SQL attendance PDF."""

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = Path(__file__).resolve().parent / "Sukhada_Dhingra_BDA_Lecture_SQL.pdf"

NAVY = HexColor("#1B3A4B")
TEAL = HexColor("#0F6C8C")
LIGHT = HexColor("#F4F7F9")
CODE_BG = HexColor("#EEF3F6")
BORDER = HexColor("#C5D0D6")
TEXT = HexColor("#1F2A30")
MUTED = HexColor("#5B6B73")

TASKS = [
    (
        "Task 1",
        "Show all delivered orders.",
        "SELECT *\nFROM orders\nWHERE order_status = 'Delivered';",
    ),
    (
        "Task 2",
        "Show Electronics orders with revenue above 50,000.",
        "SELECT *\nFROM orders\nWHERE category = 'Electronics'\n  AND revenue > 50000;",
    ),
    (
        "Task 3",
        "Count orders by customer_segment.",
        "SELECT\n    customer_segment,\n    COUNT(*) AS order_count\nFROM orders\nGROUP BY customer_segment;",
    ),
    (
        "Task 4",
        "Calculate total revenue by sales_channel.",
        "SELECT\n    sales_channel,\n    SUM(revenue) AS total_revenue\nFROM orders\nGROUP BY sales_channel;",
    ),
    (
        "Task 5",
        "Calculate total profit by payment_method.",
        "SELECT\n    payment_method,\n    SUM(profit) AS total_profit\nFROM orders\nGROUP BY payment_method;",
    ),
    (
        "Task 6",
        "Find average customer rating by city.",
        "SELECT\n    city,\n    AVG(customer_rating) AS avg_customer_rating\nFROM orders\nGROUP BY city;",
    ),
    (
        "Task 7",
        "Find the top 10 products by total profit.",
        "SELECT\n    product,\n    SUM(profit) AS total_profit\nFROM orders\nGROUP BY product\nORDER BY total_profit DESC\nLIMIT 10;",
    ),
    (
        "Task 8",
        "Find the top 10 city/category combinations by revenue.",
        "SELECT\n    city,\n    category,\n    SUM(revenue) AS total_revenue\nFROM orders\nGROUP BY city, category\nORDER BY total_revenue DESC\nLIMIT 10;",
    ),
]


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "CoverTitle",
            fontName="Times-Bold",
            fontSize=18,
            leading=22,
            textColor=white,
            alignment=TA_CENTER,
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            "CoverSub",
            fontName="Times-Italic",
            fontSize=11,
            leading=14,
            textColor=white,
            alignment=TA_CENTER,
            spaceBefore=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "MetaLabel",
            fontName="Times-Bold",
            fontSize=10,
            leading=13,
            textColor=MUTED,
        )
    )
    styles.add(
        ParagraphStyle(
            "MetaValue",
            fontName="Times-Roman",
            fontSize=11,
            leading=14,
            textColor=TEXT,
        )
    )
    styles.add(
        ParagraphStyle(
            "SectionHead",
            fontName="Times-Bold",
            fontSize=13,
            leading=16,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            "Body",
            fontName="Times-Roman",
            fontSize=10.5,
            leading=14,
            textColor=TEXT,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "TaskTitle",
            fontName="Times-Bold",
            fontSize=11.5,
            leading=15,
            textColor=TEAL,
            spaceBefore=2,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            "TaskPrompt",
            fontName="Times-Italic",
            fontSize=10.5,
            leading=14,
            textColor=TEXT,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "SqlCode",
            fontName="Courier",
            fontSize=9,
            leading=12.5,
            textColor=NAVY,
            leftIndent=6,
            rightIndent=6,
            spaceBefore=2,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            "FooterNote",
            fontName="Times-Roman",
            fontSize=8.5,
            leading=11,
            textColor=MUTED,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            "SmallCenter",
            fontName="Times-Roman",
            fontSize=8,
            leading=10,
            textColor=MUTED,
            alignment=TA_CENTER,
        )
    )
    return styles


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Times-Bold", 8.5)
    canvas.drawString(18 * mm, A4[1] - 7.5 * mm, "BDA Lecture — SQL Queries")
    canvas.setFont("Times-Roman", 8.5)
    canvas.drawRightString(
        A4[0] - 18 * mm,
        A4[1] - 7.5 * mm,
        "Sukhada Dhingra  |  PRN 24070126505  |  09 September 2026",
    )
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Times-Roman", 8)
    canvas.drawString(18 * mm, 5 * mm, "Big Data Analytics  |  Attendance / In-class SQL worksheet")
    canvas.drawRightString(A4[0] - 18 * mm, 5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def sql_block(sql, styles):
    pre = Preformatted(sql, styles["SqlCode"])
    inner = Table([[pre]], colWidths=[162 * mm])
    inner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return inner


def build():
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="BDA Lecture SQL Queries — Sukhada Dhingra",
        author="Sukhada Dhingra",
    )

    story = []

    banner = Table(
        [
            [
                Paragraph("Big Data Analytics (BDA)", styles["CoverTitle"]),
            ],
            [
                Paragraph("In-class SQL Queries — Lecture Attendance Submission", styles["CoverSub"]),
            ],
        ],
        colWidths=[174 * mm],
    )
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("TOPPADDING", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(banner)
    story.append(Spacer(1, 8 * mm))

    meta = Table(
        [
            [
                Paragraph("Student Name", styles["MetaLabel"]),
                Paragraph("PRN", styles["MetaLabel"]),
                Paragraph("Date", styles["MetaLabel"]),
                Paragraph("Course", styles["MetaLabel"]),
            ],
            [
                Paragraph("Sukhada Dhingra", styles["MetaValue"]),
                Paragraph("24070126505", styles["MetaValue"]),
                Paragraph("09 September 2026", styles["MetaValue"]),
                Paragraph("Big Data Analytics", styles["MetaValue"]),
            ],
        ],
        colWidths=[48 * mm, 42 * mm, 42 * mm, 42 * mm],
    )
    meta.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(meta)
    story.append(Spacer(1, 5 * mm))
    story.append(HRFlowable(width="100%", thickness=0.6, color=TEAL, spaceAfter=6))
    story.append(Paragraph("Assumptions", styles["SectionHead"]))
    story.append(
        Paragraph(
            "Queries are written for a single denormalized retail table named <b>orders</b>, "
            "using the column names from the worksheet: <font face='Courier' size='9'>"
            "order_status, category, revenue, customer_segment, sales_channel, "
            "payment_method, profit, customer_rating, city, product</font>. "
            "If the Hive / Spark table in your notebook has a different name, replace "
            "<font face='Courier' size='9'>orders</font> with that table name. "
            "Syntax is Spark SQL / HiveQL compatible (<font face='Courier' size='9'>LIMIT</font>).",
            styles["Body"],
        )
    )

    for number, prompt, sql in TASKS:
        story.append(Paragraph(f"{number}", styles["TaskTitle"]))
        story.append(Paragraph(prompt, styles["TaskPrompt"]))
        story.append(sql_block(sql, styles))
        story.append(Spacer(1, 3.5 * mm))

    story.append(HRFlowable(width="100%", thickness=0.6, color=TEAL, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph("Notes", styles["SectionHead"]))
    story.append(
        Paragraph(
            "If a column in your notebook differs (for example <font face='Courier' size='9'>product_name</font> "
            "instead of <font face='Courier' size='9'>product</font>, or "
            "<font face='Courier' size='9'>status</font> instead of "
            "<font face='Courier' size='9'>order_status</font>), change only that identifier.",
            styles["Body"],
        )
    )

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()
