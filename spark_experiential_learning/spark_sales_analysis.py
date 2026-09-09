#!/usr/bin/env python3
"""
E-commerce sales performance briefing built with Apache Spark.

The script loads 5,000 order records, answers the experiential-learning
questions with the DataFrame API, repeats one report in Spark SQL, then
writes a management PDF.

This is an original walkthrough (inspect → aggregate → derive → SQL),
not a pasted classroom notebook.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuOblique", "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))

ROOT = Path(__file__).resolve().parent
DATA_CSV = ROOT / "data" / "ecommerce_sales_5000.csv"
CHARTS = ROOT / "charts"
OUTPUTS = ROOT / "outputs"
PDF_PATH = ROOT / "Ecommerce_Sales_Performance_Report_Spark.pdf"

NAVY = colors.HexColor("#0F4C81")
TEAL = colors.HexColor("#1B7A6E")
GOLD = colors.HexColor("#C9A227")
INK = colors.HexColor("#1F2933")
MUTED = colors.HexColor("#52606D")
PALE = colors.HexColor("#F4F7FB")
ROW_ALT = colors.HexColor("#E8EEF5")
WHITE = colors.white
RED = colors.HexColor("#9B1B30")

CHARTS.mkdir(parents=True, exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)


def money(value, decimals=2):
    if value is None:
        return "—"
    return f"₹{float(value):,.{decimals}f}"


def crore(value):
    if value is None:
        return "—"
    return f"₹{float(value) / 1e7:.2f} Cr"


def num(value, decimals=0):
    if value is None:
        return "—"
    if decimals == 0:
        return f"{int(round(float(value))):,}"
    return f"{float(value):,.{decimals}f}"


def pct(value, decimals=2):
    if value is None:
        return "—"
    return f"{float(value) * 100:.{decimals}f}%"


def rows(sdf):
    return [r.asDict(recursive=True) for r in sdf.collect()]


def start_spark():
    os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
    return (
        SparkSession.builder.master("local[*]")
        .appName("EcommerceSalesPerformance")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.warehouse.dir", str(ROOT / "spark-warehouse"))
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )


def load_orders(spark):
    """Task 1 — load the CSV that was converted from the Excel workbook."""
    df = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .option("timestampFormat", "yyyy-MM-dd HH:mm:ss")
        .csv(str(DATA_CSV))
    )
    return df.withColumn("order_date", F.to_date(col("order_date")))


def inspect_dataset(df):
    schema = [{"column": f.name, "type": f.dataType.simpleString()} for f in df.schema.fields]
    sample = rows(df.orderBy("order_id").limit(8))
    nulls = rows(
        df.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in df.columns])
    )[0]
    status_mix = rows(
        df.groupBy("order_status")
        .agg(
            F.count("*").alias("orders"),
            F.round(F.sum("revenue"), 2).alias("revenue"),
            F.round(F.sum("profit"), 2).alias("profit"),
        )
        .orderBy(F.col("orders").desc())
    )
    extras = rows(
        df.agg(
            F.countDistinct("city").alias("cities"),
            F.countDistinct("category").alias("categories"),
            F.countDistinct("product").alias("products"),
            F.countDistinct("customer_id").alias("customers"),
            F.min("order_date").alias("first_date"),
            F.max("order_date").alias("last_date"),
            F.round(F.sum("revenue"), 2).alias("total_revenue"),
            F.round(F.sum("profit"), 2).alias("total_profit"),
            F.round(F.avg("customer_rating"), 2).alias("avg_rating"),
            F.sum(F.when(col("revenue") <= 0, 1).otherwise(0)).alias("zero_revenue_orders"),
        )
    )[0]
    return {
        "columns": df.columns,
        "schema": schema,
        "sample": sample,
        "nulls": nulls,
        "status_mix": status_mix,
        "extras": extras,
    }


def add_profit_margin(df):
    """Task 8 — never divide by zero or null revenue."""
    return df.withColumn(
        "profit_margin",
        F.when(col("revenue").isNull() | (col("revenue") <= 0), F.lit(None).cast("double")).otherwise(
            F.round(col("profit") / col("revenue"), 4)
        ),
    )


def run_spark_reports(df):
    total_orders = df.count()

    by_city = (
        df.groupBy("city")
        .agg(
            F.count("*").alias("orders"),
            F.round(F.sum("revenue"), 2).alias("total_revenue"),
            F.round(F.sum("profit"), 2).alias("total_profit"),
        )
        .withColumn(
            "profit_margin",
            F.when(col("total_revenue") <= 0, F.lit(None)).otherwise(
                F.round(col("total_profit") / col("total_revenue"), 4)
            ),
        )
        .orderBy(F.col("total_revenue").desc())
    )

    by_category = (
        df.groupBy("category")
        .agg(
            F.count("*").alias("total_orders"),
            F.round(F.sum("revenue"), 2).alias("total_revenue"),
            F.round(F.sum("profit"), 2).alias("total_profit"),
            F.round(F.avg("customer_rating"), 2).alias("avg_rating"),
        )
        .withColumn(
            "profit_margin",
            F.when(col("total_revenue") <= 0, F.lit(None)).otherwise(
                F.round(col("total_profit") / col("total_revenue"), 4)
            ),
        )
        .orderBy(F.col("total_revenue").desc())
    )

    top_products = (
        df.groupBy("product", "category")
        .agg(
            F.count("*").alias("orders"),
            F.round(F.sum("revenue"), 2).alias("total_revenue"),
            F.round(F.sum("profit"), 2).alias("total_profit"),
        )
        .withColumn(
            "profit_margin",
            F.when(col("total_revenue") <= 0, F.lit(None)).otherwise(
                F.round(col("total_profit") / col("total_revenue"), 4)
            ),
        )
        .orderBy(F.col("total_profit").desc())
        .limit(10)
    )

    city_category = (
        df.groupBy("city", "category")
        .agg(
            F.count("*").alias("orders"),
            F.round(F.sum("revenue"), 2).alias("total_revenue"),
            F.round(F.sum("profit"), 2).alias("total_profit"),
        )
        .orderBy(F.col("total_revenue").desc())
        .limit(15)
    )

    monthly = (
        df.withColumn("month", F.date_format(col("order_date"), "yyyy-MM"))
        .groupBy("month")
        .agg(
            F.count("*").alias("orders"),
            F.round(F.sum("revenue"), 2).alias("total_revenue"),
            F.round(F.sum("profit"), 2).alias("total_profit"),
        )
        .orderBy("month")
    )

    margin_examples = (
        df.select(
            "order_id",
            "city",
            "category",
            "product",
            "order_status",
            "revenue",
            "profit",
            "profit_margin",
        )
        .orderBy(F.col("profit_margin").desc_nulls_last())
        .limit(8)
    )

    cancelled_null_margin = df.filter(col("profit_margin").isNull()).count()

    df.createOrReplaceTempView("orders")
    sql_category = spark_sql_category(df.sparkSession)

    return {
        "total_orders": total_orders,
        "by_city": rows(by_city),
        "by_category": rows(by_category),
        "top_products": rows(top_products),
        "city_category": rows(city_category),
        "monthly": rows(monthly),
        "margin_examples": rows(margin_examples),
        "cancelled_null_margin": cancelled_null_margin,
        "sql_category": sql_category,
    }


def spark_sql_category(spark):
    """Task 9 — same category briefing, expressed as Spark SQL."""
    sql_text = (
        "SELECT\n"
        "    category,\n"
        "    COUNT(*) AS total_orders,\n"
        "    ROUND(SUM(revenue), 2) AS total_revenue,\n"
        "    ROUND(SUM(profit), 2) AS total_profit,\n"
        "    ROUND(AVG(customer_rating), 2) AS avg_rating,\n"
        "    ROUND(SUM(profit) / NULLIF(SUM(revenue), 0), 4) AS profit_margin\n"
        "FROM orders\n"
        "GROUP BY category\n"
        "ORDER BY total_revenue DESC"
    )
    result = spark.sql(sql_text)
    return {"sql": sql_text, "rows": rows(result)}


def save_charts(reports):
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#7B8794",
            "axes.labelcolor": "#1F2933",
            "xtick.color": "#1F2933",
            "ytick.color": "#1F2933",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )
    paths = {}

    cities = reports["by_city"]
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    ax.bar([r["city"] for r in cities], [r["total_revenue"] / 1e6 for r in cities], color="#0F4C81")
    ax.set_ylabel("Revenue (₹ million)")
    ax.set_title("Revenue by city")
    fig.tight_layout()
    paths["city"] = CHARTS / "revenue_by_city.png"
    fig.savefig(paths["city"], dpi=160)
    plt.close(fig)

    cats = reports["by_category"]
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    x = range(len(cats))
    width = 0.38
    ax.bar([i - width / 2 for i in x], [r["total_revenue"] / 1e6 for r in cats], width, label="Revenue", color="#0F4C81")
    ax.bar([i + width / 2 for i in x], [r["total_profit"] / 1e6 for r in cats], width, label="Profit", color="#1B7A6E")
    ax.set_xticks(list(x))
    ax.set_xticklabels([r["category"] for r in cats], rotation=15)
    ax.set_ylabel("₹ million")
    ax.set_title("Revenue and profit by category")
    ax.legend(frameon=False)
    fig.tight_layout()
    paths["category"] = CHARTS / "category_revenue_profit.png"
    fig.savefig(paths["category"], dpi=160)
    plt.close(fig)

    months = reports["monthly"]
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    ax.plot(
        [r["month"] for r in months],
        [r["total_revenue"] / 1e6 for r in months],
        color="#0F4C81",
        marker="o",
        linewidth=2,
    )
    ax.fill_between(
        [r["month"] for r in months],
        [r["total_revenue"] / 1e6 for r in months],
        color="#0F4C81",
        alpha=0.12,
    )
    ax.set_ylabel("Revenue (₹ million)")
    ax.set_title("Monthly revenue in 2025")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    paths["monthly"] = CHARTS / "monthly_revenue.png"
    fig.savefig(paths["monthly"], dpi=160)
    plt.close(fig)

    products = reports["top_products"]
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    labels = [r["product"] for r in reversed(products)]
    values = [r["total_profit"] / 1e6 for r in reversed(products)]
    ax.barh(labels, values, color="#1B7A6E")
    ax.set_xlabel("Profit (₹ million)")
    ax.set_title("Top 10 products by profit")
    fig.tight_layout()
    paths["products"] = CHARTS / "top_products_profit.png"
    fig.savefig(paths["products"], dpi=160)
    plt.close(fig)

    return {k: str(v) for k, v in paths.items()}


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "CoverKicker",
            fontName="DejaVuBold",
            fontSize=11,
            textColor=GOLD,
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "CoverTitle",
            fontName="DejaVuBold",
            fontSize=26,
            leading=32,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "CoverSub",
            fontName="DejaVuOblique",
            fontSize=13,
            leading=18,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            "Section",
            fontName="DejaVuBold",
            fontSize=16,
            leading=20,
            textColor=NAVY,
            spaceBefore=6,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "Body",
            fontName="DejaVu",
            fontSize=11,
            leading=15.5,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "Caption",
            fontName="DejaVu",
            fontSize=9,
            leading=12,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceBefore=3,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            "KPIValue",
            fontName="DejaVuBold",
            fontSize=11,
            leading=14,
            textColor=NAVY,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            "KPILabel",
            fontName="DejaVu",
            fontSize=8,
            leading=11,
            textColor=MUTED,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            "TableCell",
            fontName="DejaVu",
            fontSize=8.5,
            leading=11,
            textColor=INK,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            "TableCellRight",
            fontName="DejaVu",
            fontSize=8.5,
            leading=11,
            textColor=INK,
            alignment=TA_RIGHT,
        )
    )
    styles.add(
        ParagraphStyle(
            "TableHead",
            fontName="DejaVuBold",
            fontSize=8.5,
            leading=11,
            textColor=WHITE,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            "SparkCode",
            fontName="DejaVuMono",
            fontSize=7.6,
            leading=10.2,
            textColor=INK,
            backColor=PALE,
            leftIndent=6,
            rightIndent=6,
            spaceBefore=4,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "Footer",
            fontName="DejaVu",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            "SmallCenter",
            fontName="DejaVu",
            fontSize=10,
            leading=14,
            textColor=INK,
            alignment=TA_CENTER,
        )
    )
    return styles


def table(data, col_widths, right_align_from=1):
    styles = build_styles()
    formatted = []
    for i, row in enumerate(data):
        out = []
        for j, cell in enumerate(row):
            if i == 0:
                out.append(Paragraph(str(cell), styles["TableHead"]))
            elif j >= right_align_from:
                out.append(Paragraph(str(cell), styles["TableCellRight"]))
            else:
                out.append(Paragraph(str(cell), styles["TableCell"]))
        formatted.append(out)

    tbl = Table(formatted, colWidths=col_widths, repeatRows=1)
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuBold"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD2D9")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for idx in range(1, len(formatted)):
        if idx % 2 == 0:
            commands.append(("BACKGROUND", (0, idx), (-1, idx), ROW_ALT))
        else:
            commands.append(("BACKGROUND", (0, idx), (-1, idx), WHITE))
    tbl.setStyle(TableStyle(commands))
    return tbl


def kpi_band(items):
    styles = build_styles()
    cells = []
    for label, value in items:
        inner = Table(
            [[Paragraph(str(value), styles["KPIValue"])], [Paragraph(label, styles["KPILabel"])]],
            colWidths=[90],
        )
        inner.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), PALE),
                    ("BOX", (0, 0), (-1, -1), 0.6, TEAL),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        cells.append(inner)
    band = Table([cells], colWidths=[96] * len(items))
    band.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return band


def code_block(text):
    styles = build_styles()
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
        .replace(" ", "&nbsp;")
    )
    para = Paragraph(escaped, styles["SparkCode"])
    wrap = Table([[para]], colWidths=[170 * mm])
    wrap.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD2D9")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return wrap


def draw_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 16, A4[0], 16, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, A4[1] - 18, A4[0], 2, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("DejaVu", 8)
    canvas.drawString(18 * mm, A4[1] - 11, "E-commerce Sales Performance Report  |  Apache Spark")
    canvas.drawRightString(A4[0] - 18 * mm, A4[1] - 11, "Experiential Learning")
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], 14, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("DejaVu", 8)
    canvas.drawString(18 * mm, 5, "Junior data analyst briefing  •  5,000 orders  •  calendar year 2025")
    canvas.drawRightString(A4[0] - 18 * mm, 5, f"Page {doc.page}")
    canvas.restoreState()


def d(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def build_pdf(inspect, reports, charts):
    styles = build_styles()
    extras = inspect["extras"]
    total_revenue = extras["total_revenue"]
    total_profit = extras["total_profit"]
    blended_margin = total_profit / total_revenue if total_revenue else None
    cancelled = next(r for r in inspect["status_mix"] if r["order_status"] == "Cancelled")
    returned = next(r for r in inspect["status_mix"] if r["order_status"] == "Returned")
    delivered = next(r for r in inspect["status_mix"] if r["order_status"] == "Delivered")

    peak_month = max(reports["monthly"], key=lambda r: r["total_revenue"])
    quiet_month = min(reports["monthly"], key=lambda r: r["total_revenue"])
    top_city = reports["by_city"][0]
    top_combo = reports["city_category"][0]
    top_product = reports["top_products"][0]
    lead_category = reports["by_category"][0]

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title="E-commerce Sales Performance Report (Apache Spark)",
        author="Junior Data Analyst",
    )
    story = []

    story.append(Spacer(1, 8))
    story.append(Paragraph("EXPERIENTIAL LEARNING  •  APACHE SPARK", styles["CoverKicker"]))
    story.append(Paragraph("E-commerce Sales<br/>Performance Report", styles["CoverTitle"]))
    story.append(
        Paragraph(
            "A junior-analyst briefing for management, built from 5,000 order records "
            "using Spark DataFrames and Spark SQL.",
            styles["CoverSub"],
        )
    )
    story.append(
        kpi_band(
            [
                ("Total orders", num(reports["total_orders"])),
                ("Total revenue", crore(total_revenue)),
                ("Total profit", crore(total_profit)),
                ("Blended margin", pct(blended_margin)),
                ("Avg. rating", num(extras["avg_rating"], 2)),
            ]
        )
    )
    story.append(Spacer(1, 14))
    story.append(
        Paragraph(
            "Scenario. Management asked for a quick sales-performance view of the 2025 order book. "
            "The workbook <font face='DejaVuOblique'>ecommerce_sales_5000.xlsx</font> was converted to CSV "
            "and loaded into a local Spark session. Aggregations use the DataFrame API "
            "(<font face='DejaVuMono'>groupBy</font>, <font face='DejaVuMono'>agg</font>, "
            "<font face='DejaVuMono'>withColumn</font>). One core briefing is then rebuilt with Spark SQL "
            "to show the same numbers from a temporary view.",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            f"Coverage. Orders run from {d(extras['first_date'])} to {d(extras['last_date'])} across "
            f"{extras['cities']} cities, {extras['categories']} categories, {extras['products']} products "
            f"and {num(extras['customers'])} customers. There are no missing values. "
            f"{num(extras['zero_revenue_orders'])} orders have zero revenue — all of them are Cancelled.",
            styles["Body"],
        )
    )

    story.append(Paragraph("1. Load and inspect the dataset", styles["Section"]))
    story.append(
        Paragraph(
            "The Excel file was saved as CSV so Spark could infer types without an Excel connector. "
            "A local session then read the file with a header row and a date conversion on "
            "<font face='DejaVuMono'>order_date</font>.",
            styles["Body"],
        )
    )
    story.append(
        code_block(
            "spark = SparkSession.builder.master(\"local[*]\").appName(\"EcommerceSales\").getOrCreate()\n"
            "orders = (spark.read.option(\"header\", True).option(\"inferSchema\", True)\n"
            "               .csv(\"data/ecommerce_sales_5000.csv\")\n"
            "               .withColumn(\"order_date\", to_date(col(\"order_date\"))))\n"
            "orders.printSchema()\n"
            "orders.show(5, truncate=False)\n"
            "print(orders.count(), len(orders.columns))"
        )
    )

    left_schema = inspect["schema"][:10]
    right_schema = inspect["schema"][10:]
    schema_data = [["#", "Column", "Type", "#", "Column", "Type"]]
    for i in range(len(left_schema)):
        row = [str(i + 1), left_schema[i]["column"], left_schema[i]["type"]]
        if i < len(right_schema):
            row.extend([str(i + 11), right_schema[i]["column"], right_schema[i]["type"]])
        else:
            row.extend(["", "", ""])
        schema_data.append(row)
    schema_table = table(schema_data, [14 * mm, 40 * mm, 22 * mm, 14 * mm, 42 * mm, 22 * mm], right_align_from=99)
    story.append(
        KeepTogether(
            [
                schema_table,
                Paragraph(
                    "Figure: inferred Spark schema after CSV load (19 columns, 5,000 rows).",
                    styles["Caption"],
                ),
            ]
        )
    )

    sample_data = [["Order ID", "Date", "City", "Category", "Product", "Revenue", "Status"]]
    for r in inspect["sample"]:
        sample_data.append(
            [
                r["order_id"],
                str(d(r["order_date"])),
                r["city"],
                r["category"],
                r["product"],
                money(r["revenue"]),
                r["order_status"],
            ]
        )
    story.append(table(sample_data, [28 * mm, 24 * mm, 24 * mm, 30 * mm, 26 * mm, 28 * mm, 20 * mm], right_align_from=5))
    story.append(Paragraph("Table: first eight rows after ordering by order_id (inspection sample).", styles["Caption"]))

    status_data = [["Order status", "Orders", "Share of book", "Revenue", "Profit"]]
    for r in inspect["status_mix"]:
        status_data.append(
            [
                r["order_status"],
                num(r["orders"]),
                pct(r["orders"] / reports["total_orders"]),
                money(r["revenue"]),
                money(r["profit"]),
            ]
        )
    story.append(table(status_data, [40 * mm, 30 * mm, 35 * mm, 35 * mm, 30 * mm], right_align_from=1))
    story.append(
        Paragraph(
            "Quality note. Cancelled lines are booked at ₹0. Returned lines still carry revenue and profit, "
            "so a ‘realized sales’ view would need an extra filter on order_status.",
            styles["Caption"],
        )
    )

    story.append(Paragraph("2. Total number of orders", styles["Section"]))
    story.append(
        Paragraph(
            f"<font face='DejaVuBold'>There are {num(reports['total_orders'])} orders</font> in the file — "
            "one unique <font face='DejaVuMono'>order_id</font> per row, so a simple "
            "<font face='DejaVuMono'>orders.count()</font> is the order count. "
            f"Of these, {num(delivered['orders'])} were delivered "
            f"({pct(delivered['orders'] / reports['total_orders'])}), "
            f"{num(returned['orders'])} returned and {num(cancelled['orders'])} cancelled.",
            styles["Body"],
        )
    )

    story.append(Paragraph("3. Total revenue and total profit by city", styles["Section"]))
    story.append(
        Paragraph(
            "City totals are a grouped sum of revenue and profit. A safe blended margin "
            "(profit ÷ revenue) is attached only when the city revenue is positive.",
            styles["Body"],
        )
    )
    story.append(
        code_block(
            "orders.groupBy(\"city\").agg(\n"
            "    count(\"*\").alias(\"orders\"),\n"
            "    round(sum(\"revenue\"), 2).alias(\"total_revenue\"),\n"
            "    round(sum(\"profit\"), 2).alias(\"total_profit\")\n"
            ").orderBy(col(\"total_revenue\").desc())"
        )
    )
    city_data = [["City", "Orders", "Total revenue", "Total profit", "Margin"]]
    for r in reports["by_city"]:
        city_data.append(
            [
                r["city"],
                num(r["orders"]),
                money(r["total_revenue"]),
                money(r["total_profit"]),
                pct(r["profit_margin"]),
            ]
        )
    story.append(table(city_data, [38 * mm, 28 * mm, 40 * mm, 38 * mm, 26 * mm], right_align_from=1))
    story.append(Spacer(1, 6))
    story.append(Image(charts["city"], width=170 * mm, height=62 * mm))
    story.append(
        Paragraph(
            f"Delhi leads on revenue ({money(top_city['total_revenue'])}), followed by Pune and Hyderabad. "
            "The eight-city spread is tight: Ahmedabad at the bottom is still about 85% of Delhi’s revenue, "
            "so the book is national rather than metro-concentrated.",
            styles["Caption"],
        )
    )

    story.append(Paragraph("4. Orders, revenue, profit and average rating by category", styles["Section"]))
    story.append(
        Paragraph(
            "Category is the natural merchandise cut. Rating is averaged from "
            "<font face='DejaVuMono'>customer_rating</font> (1–5).",
            styles["Body"],
        )
    )
    cat_data = [["Category", "Orders", "Revenue", "Profit", "Avg rating", "Margin"]]
    for r in reports["by_category"]:
        cat_data.append(
            [
                r["category"],
                num(r["total_orders"]),
                money(r["total_revenue"]),
                money(r["total_profit"]),
                num(r["avg_rating"], 2),
                pct(r["profit_margin"]),
            ]
        )
    story.append(table(cat_data, [38 * mm, 22 * mm, 38 * mm, 32 * mm, 22 * mm, 18 * mm], right_align_from=1))
    story.append(Image(charts["category"], width=170 * mm, height=62 * mm))
    story.append(
        Paragraph(
            f"{lead_category['category']} is the largest category by revenue "
            f"({money(lead_category['total_revenue'])}, {num(lead_category['total_orders'])} orders). "
            "Average ratings sit in a narrow band around 4.0, so rating does not currently separate winners from the rest.",
            styles["Caption"],
        )
    )

    story.append(Paragraph("5. Top 10 products by profit", styles["Section"]))
    story.append(
        Paragraph(
            "Products are ranked on summed profit, not unit price. That answers ‘which SKUs actually make money’ "
            "rather than which ones simply sell at a high list price.",
            styles["Body"],
        )
    )
    prod_data = [["Rank", "Product", "Category", "Orders", "Revenue", "Profit", "Margin"]]
    for i, r in enumerate(reports["top_products"], start=1):
        prod_data.append(
            [
                str(i),
                r["product"],
                r["category"],
                num(r["orders"]),
                money(r["total_revenue"]),
                money(r["total_profit"]),
                pct(r["profit_margin"]),
            ]
        )
    story.append(table(prod_data, [14 * mm, 32 * mm, 32 * mm, 20 * mm, 32 * mm, 28 * mm, 18 * mm], right_align_from=3))
    story.append(Image(charts["products"], width=170 * mm, height=68 * mm))
    story.append(
        Paragraph(
            f"{top_product['product']} ({top_product['category']}) is the profit leader at "
            f"{money(top_product['total_profit'])}. Grocery staples and a few high-velocity Beauty and Sports SKUs "
            "fill most of the top ten.",
            styles["Caption"],
        )
    )

    story.append(Paragraph("6. Best city / category combinations by revenue", styles["Section"]))
    story.append(
        Paragraph(
            "Crossing city with category shows where the catalog actually converts, which is more useful for "
            "inventory and campaign planning than either dimension alone.",
            styles["Body"],
        )
    )
    story.append(
        code_block(
            "orders.groupBy(\"city\", \"category\").agg(\n"
            "    count(\"*\").alias(\"orders\"),\n"
            "    round(sum(\"revenue\"), 2).alias(\"total_revenue\"),\n"
            "    round(sum(\"profit\"), 2).alias(\"total_profit\")\n"
            ").orderBy(col(\"total_revenue\").desc()).limit(15)"
        )
    )
    combo_data = [["City", "Category", "Orders", "Revenue", "Profit"]]
    for r in reports["city_category"]:
        combo_data.append(
            [
                r["city"],
                r["category"],
                num(r["orders"]),
                money(r["total_revenue"]),
                money(r["total_profit"]),
            ]
        )
    story.append(table(combo_data, [36 * mm, 42 * mm, 26 * mm, 36 * mm, 30 * mm], right_align_from=2))
    story.append(
        Paragraph(
            f"The strongest pair is {top_combo['city']} × {top_combo['category']} "
            f"({money(top_combo['total_revenue'])} revenue, {num(top_combo['orders'])} orders).",
            styles["Caption"],
        )
    )

    story.append(Paragraph("7. Monthly revenue", styles["Section"]))
    story.append(
        Paragraph(
            "A year-month key is derived with <font face='DejaVuMono'>date_format(order_date, 'yyyy-MM')</font> "
            "and revenue is summed. The series covers every calendar month of 2025.",
            styles["Body"],
        )
    )
    month_data = [["Month", "Orders", "Revenue", "Profit"]]
    for r in reports["monthly"]:
        month_data.append(
            [r["month"], num(r["orders"]), money(r["total_revenue"]), money(r["total_profit"])]
        )
    story.append(table(month_data, [40 * mm, 35 * mm, 50 * mm, 45 * mm], right_align_from=1))
    story.append(Image(charts["monthly"], width=170 * mm, height=62 * mm))
    story.append(
        Paragraph(
            f"Revenue peaks in {peak_month['month']} at {money(peak_month['total_revenue'])} and is quietest in "
            f"{quiet_month['month']} ({money(quiet_month['total_revenue'])}). The year is commercially active throughout; "
            "there is no collapsed off-season.",
            styles["Caption"],
        )
    )

    story.append(Paragraph("8. Profit-margin column, created safely", styles["Section"]))
    story.append(
        Paragraph(
            "A row-level margin of profit ÷ revenue is useful, but 845 cancelled orders have revenue = 0. "
            "Dividing blindly would throw Infinity or crash a job. The column is therefore wrapped in "
            "<font face='DejaVuMono'>when / otherwise</font>: null revenue or revenue ≤ 0 becomes a SQL null, "
            "not a number. The same idea at aggregate level uses <font face='DejaVuMono'>NULLIF(SUM(revenue), 0)</font>.",
            styles["Body"],
        )
    )
    story.append(
        code_block(
            "orders = orders.withColumn(\n"
            "    \"profit_margin\",\n"
            "    when(col(\"revenue\").isNull() | (col(\"revenue\") <= 0), lit(None).cast(\"double\"))\n"
            "    .otherwise(round(col(\"profit\") / col(\"revenue\"), 4))\n"
            ")"
        )
    )
    story.append(
        Paragraph(
            f"Spark stored a null margin on {num(reports['cancelled_null_margin'])} rows — matching the cancelled "
            "zero-revenue population. Delivered and returned rows keep a finite ratio.",
            styles["Body"],
        )
    )
    margin_data = [["order_id", "Status", "City", "Product", "Revenue", "Profit", "Margin"]]
    for r in reports["margin_examples"]:
        margin_data.append(
            [
                r["order_id"],
                r["order_status"],
                r["city"],
                r["product"],
                money(r["revenue"]),
                money(r["profit"]),
                pct(r["profit_margin"]) if r["profit_margin"] is not None else "null",
            ]
        )
    story.append(table(margin_data, [28 * mm, 24 * mm, 24 * mm, 28 * mm, 26 * mm, 24 * mm, 16 * mm], right_align_from=4))
    story.append(Paragraph("Table: eight highest finite profit-margin orders after the safe column is added.", styles["Caption"]))

    story.append(Paragraph("9. Repeat an important report in Spark SQL", styles["Section"]))
    story.append(
        Paragraph(
            "The category briefing from Task 4 is the report management is most likely to reuse, so it is rebuilt "
            "from a temporary view. The SQL uses <font face='DejaVuMono'>NULLIF</font> so a zero-revenue group cannot "
            "divide by zero — the same safety rule as Task 8, written in SQL.",
            styles["Body"],
        )
    )
    story.append(code_block(reports["sql_category"]["sql"]))
    sql_data = [["Category", "Orders", "Revenue", "Profit", "Avg rating", "Margin"]]
    for r in reports["sql_category"]["rows"]:
        sql_data.append(
            [
                r["category"],
                num(r["total_orders"]),
                money(r["total_revenue"]),
                money(r["total_profit"]),
                num(r["avg_rating"], 2),
                pct(r["profit_margin"]),
            ]
        )
    story.append(table(sql_data, [38 * mm, 22 * mm, 38 * mm, 32 * mm, 22 * mm, 18 * mm], right_align_from=1))
    story.append(
        Paragraph(
            "The Spark SQL table matches the DataFrame category table. That is the point of the exercise: "
            "the same business question, two Spark APIs, identical totals.",
            styles["Caption"],
        )
    )

    story.append(Paragraph("10. What the data suggests", styles["Section"]))
    story.append(
        Paragraph(
            f"The 5,000-order book generated {money(total_revenue)} in revenue and {money(total_profit)} in profit, "
            f"a blended margin of {pct(blended_margin)}. That is a commercially healthy year on paper, but it is "
            f"not fully collected cash: {num(cancelled['orders'])} cancelled orders "
            f"({pct(cancelled['orders'] / reports['total_orders'])}) contribute nothing, and another "
            f"{num(returned['orders'])} returned orders still sit in the ledger with {money(returned['revenue'])} "
            "of revenue attached.",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            f"Demand is geographically balanced. {top_city['city']} is the revenue leader, yet the gap to the "
            "smallest city is modest, so the catalog is not dependent on one metro. Category mix is similarly even; "
            f"{lead_category['category']} leads, but no vertical is a rounding error. The profit ranking is more "
            f"concentrated at SKU level: {top_product['product']}, Snacks, Face Wash and Cooking Oil should be "
            "protected on availability and discounting because they do the heavy lifting on profit.",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            f"The best city–category pair is {top_combo['city']} / {top_combo['category']}. That is a practical "
            "place to test bundles, paid acquisition and warehouse depth. Monthly revenue stays in a workable "
            f"band, peaking in {peak_month['month']} and dipping in {quiet_month['month']}, so planning can assume "
            "a steady run-rate rather than a single festival spike.",
            styles["Body"],
        )
    )
    story.append(
        Paragraph(
            "Customer rating averages about 4.0 in every category and therefore does not currently tell management "
            "where quality is failing. The sharper operational levers are reducing cancellations (zero-revenue leakage), "
            "deciding whether returned GMV belongs in the headline P&amp;L, and keeping the top-profit grocery, beauty "
            "and sports SKUs in stock in Delhi, Pune and Hyderabad.",
            styles["Body"],
        )
    )

    story.append(
        KeepTogether(
            [
                Paragraph("How to reproduce", styles["Section"]),
                Paragraph(
                    "From the <font face='DejaVuMono'>spark_experiential_learning</font> folder, with Java and PySpark installed:",
                    styles["Body"],
                ),
                code_block("python3 spark_sales_analysis.py"),
                Paragraph(
                    "The script writes this PDF, plus chart PNGs under <font face='DejaVuMono'>charts/</font>. "
                    "Numbers are computed in Spark; matplotlib is used only to draw the figures that go into the PDF.",
                    styles["Body"],
                ),
            ]
        )
    )

    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    return PDF_PATH


def main():
    spark = start_spark()
    spark.sparkContext.setLogLevel("ERROR")
    try:
        orders = load_orders(spark)
        inspect = inspect_dataset(orders)
        orders = add_profit_margin(orders)
        reports = run_spark_reports(orders)
        extras = inspect["extras"]
        extras["first_date"] = d(extras["first_date"])
        extras["last_date"] = d(extras["last_date"])
        payload = {"inspect": inspect, "reports": reports}
        (OUTPUTS / "spark_results.json").write_text(
            json.dumps(payload, default=str, indent=2), encoding="utf-8"
        )
        charts = save_charts(reports)
        pdf = build_pdf(inspect, reports, charts)
        print(f"Total orders: {reports['total_orders']}")
        print(f"PDF written to: {pdf}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
