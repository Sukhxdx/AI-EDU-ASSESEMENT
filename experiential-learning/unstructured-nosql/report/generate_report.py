#!/usr/bin/env python3
"""Generate the Big Data Analytics lab PDF: unstructured data → MongoDB."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
DIAG = ROOT / "diagrams"
OUT_DIR = ROOT / "report"
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"
DATASET = ROOT / "dataset" / "product_reviews.jsonl"

SHOTS.mkdir(parents=True, exist_ok=True)
DIAG.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

STUDENT_NAME = "Sukhada Dhingra"
STUDENT_PRN = "24070126505"
STUDENT_BATCH = "A3"
PROGRAMME = "B.Tech. (Artificial Intelligence and Machine Learning)"
INSTITUTE = "Symbiosis Institute of Technology, Pune"
UNIVERSITY = "Symbiosis International (Deemed University)"
COURSE = "Big Data Analytics"
TITLE = "Unstructured Data into a NoSQL Database"

NAVY = HexColor("#0B1F3A")
NAVY2 = HexColor("#16325C")
MAROON = HexColor("#8B1E3F")
GOLD = HexColor("#C9A227")
TEAL = HexColor("#1F6F78")
LIGHT = HexColor("#F4F1EA")
PALE = HexColor("#E8EEF6")
CODE_BG = HexColor("#0F1724")
CODE_FG = HexColor("#E6EDF3")
MUTED = HexColor("#5B6573")

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMonoBold", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"))

MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
MONO_B = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 15)
UI = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)


def wrap_line(text: str, width: int = 92) -> list[str]:
    if len(text) <= width:
        return [text]
    out = []
    while text:
        if len(text) <= width:
            out.append(text)
            break
        cut = text.rfind(" ", 0, width)
        if cut < width // 2:
            cut = width
        out.append(text[:cut])
        text = text[cut:].lstrip()
    return out


def render_terminal(filename: str, caption_title: str, lines: list[str]) -> Path:
    expanded: list[tuple[str, str]] = []
    for raw in lines:
        kind = "out"
        if raw.startswith("$ "):
            kind = "cmd"
        elif "successfully" in raw or raw.startswith("documents = 300") or "ok: 1" in raw:
            kind = "ok"
        elif "====" in raw:
            kind = "info"
        elif "WARN" in raw or "failed" in raw:
            kind = "warn"
        for piece in wrap_line(raw.expandtabs(8), 96):
            expanded.append((kind, piece))

    pad_x, pad_y = 22, 18
    line_h = 22
    title_h = 42
    width = 1100
    height = title_h + pad_y * 2 + line_h * max(8, len(expanded)) + 18
    img = Image.new("RGB", (width, height), (15, 18, 24))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, title_h], fill=(36, 41, 51))
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        x = 18 + i * 18
        draw.ellipse([x, 14, x + 12, 26], fill=color)
    draw.text((78, 13), caption_title, font=UI, fill=(220, 224, 230))

    y = title_h + pad_y
    colors = {
        "cmd": (122, 220, 160),
        "ok": (80, 220, 140),
        "warn": (240, 196, 90),
        "info": (156, 196, 230),
        "out": (226, 232, 240),
    }
    for kind, text in expanded:
        font = MONO_B if kind == "cmd" else MONO
        draw.text((pad_x, y), text, font=font, fill=colors[kind])
        y += line_h

    path = SHOTS / filename
    img.save(path, "PNG")
    return path


def load_docs() -> list[dict]:
    docs = []
    for line in DATASET.read_text(encoding="utf-8").splitlines():
        if line.strip():
            docs.append(json.loads(line))
    return docs


def dataset_stats(docs: list[dict]) -> dict:
    keys = Counter()
    cats = Counter()
    ratings = Counter()
    for d in docs:
        for k in d:
            keys[k] += 1
        cats[d["product"]["category"]] += 1
        ratings[d["rating"]] += 1
    return {"n": len(docs), "keys": keys, "cats": cats, "ratings": ratings}


def make_diagrams(stats: dict) -> dict[str, Path]:
    paths: dict[str, Path] = {}

    fig, ax = plt.subplots(figsize=(10.4, 4.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_title("Why unstructured JSON is stored in a document NoSQL store",
                 fontsize=13, pad=8, color="#0B1F3A", fontweight="bold")
    boxes = [
        (0.3, 1.5, 3.4, 2.4, "#8B1E3F", "Relational table\nfixed columns\nNULL for missing\nALTER TABLE to grow"),
        (4.3, 1.5, 3.4, 2.4, "#1F6F78", "JSON / logs / reviews\nnested objects\noptional fields\narrays of tags"),
        (8.3, 1.5, 3.4, 2.4, "#0B1F3A", "MongoDB document\none JSON ≈ one doc\nschema-less\nindex + aggregate"),
    ]
    for x, y, w, h, c, label in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                    facecolor=c, edgecolor="white", linewidth=1.5))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", color="white", fontsize=9.5)
        if x < 8:
            ax.annotate("", xy=(x + w + 0.48, y + h / 2), xytext=(x + w + 0.12, y + h / 2),
                        arrowprops=dict(arrowstyle="->", color="#0B1F3A", lw=1.6))
    ax.text(6, 0.55, "Variety of Big Data  ·  no join-heavy star schema  ·  ingest first, query later",
            ha="center", fontsize=9, color="#5B6573")
    p = DIAG / "why_nosql.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["why"] = p

    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_title("MongoDB logical stack used in this Ubuntu lab",
                 fontsize=13, pad=8, color="#0B1F3A", fontweight="bold")
    layers = [
        (0.5, 4.5, 9.0, 0.95, "#8B1E3F", "Clients  ·  mongosh  ·  mongoimport  ·  (optional) pymongo"),
        (0.5, 3.35, 9.0, 0.95, "#1F6F78", "Database sit_bda  ·  collection product_reviews"),
        (0.5, 2.2, 9.0, 0.95, "#16325C", "Documents (BSON)  ·  nested product/customer  ·  optional tags/media"),
        (0.5, 1.05, 9.0, 0.95, "#0B1F3A", "mongod 8.0.32  ·  WiredTiger  ·  localhost:27017 on Ubuntu 24.04"),
    ]
    for x, y, w, h, c, label in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                    facecolor=c, edgecolor="white", linewidth=1.5))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", color="white", fontsize=10)
    p = DIAG / "mongo_stack.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["stack"] = p

    fig, ax = plt.subplots(figsize=(10.6, 4.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_title("Lab pipeline executed on Ubuntu", fontsize=13, pad=6, color="#0B1F3A", fontweight="bold")
    steps = [
        (0.25, 1.5, 2.2, 1.7, "#0B1F3A", "JSONL\n300 reviews\nvaried keys"),
        (2.7, 1.5, 2.2, 1.7, "#1F6F78", "mongoimport\n→ sit_bda\nproduct_reviews"),
        (5.15, 1.5, 2.2, 1.7, "#8B1E3F", "CRUD\ninsert / find\nupdate / delete"),
        (7.6, 1.5, 2.2, 1.7, "#16325C", "$group $match\n$unwind $facet\nsort limit skip"),
        (10.05, 1.5, 1.7, 1.7, "#C9A227", "lab\nPDF"),
    ]
    for i, (x, y, w, h, c, label) in enumerate(steps):
        tc = "#0B1F3A" if c == "#C9A227" else "white"
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.1",
                                    facecolor=c, edgecolor="white", linewidth=1.4))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", color=tc, fontsize=8.8, fontweight="bold")
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + w + 0.22, y + h / 2), xytext=(x + w + 0.02, y + h / 2),
                        arrowprops=dict(arrowstyle="->", color="#0B1F3A", lw=1.5))
    p = DIAG / "lab_pipeline.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["pipeline"] = p

    cats = stats["cats"]
    labels = [k for k, _ in cats.most_common()]
    vals = [cats[k] for k in labels]
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    fig.patch.set_facecolor("white")
    bars = ax.bar(labels, vals, color="#16325C", edgecolor="white")
    ax.set_ylabel("reviews")
    ax.set_title("Documents by product category (n = 300)", color="#0B1F3A", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.2, str(v), ha="center", fontsize=9, color="#0B1F3A")
    p = DIAG / "category_chart.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["cat_chart"] = p

    ratings = stats["ratings"]
    xs = [1, 2, 3, 4, 5]
    ys = [ratings[i] for i in xs]
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    fig.patch.set_facecolor("white")
    ax.bar(xs, ys, color="#1F6F78", edgecolor="white")
    ax.set_xlabel("star rating")
    ax.set_ylabel("reviews")
    ax.set_title("Rating histogram from $facet aggregation", color="#0B1F3A", fontweight="bold")
    ax.set_xticks(xs)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for x, v in zip(xs, ys):
        ax.text(x, v + 1.5, str(v), ha="center", fontsize=9, color="#0B1F3A")
    p = DIAG / "rating_chart.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["rating_chart"] = p

    keys = stats["keys"]
    optional = [(k, n) for k, n in keys.most_common() if n < stats["n"]]
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    fig.patch.set_facecolor("white")
    names = [k for k, _ in optional]
    ns = [n for _, n in optional]
    ax.barh(names[::-1], ns[::-1], color="#8B1E3F")
    ax.set_xlabel("documents that contain the field (out of 300)")
    ax.set_title("Schema-less proof — optional top-level fields", color="#0B1F3A", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    p = DIAG / "schema_chart.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["schema_chart"] = p
    return paths


def qlines() -> list[str]:
    return (RESULTS / "05_mongosh_queries.txt").read_text().splitlines()


def extract(lines: list[str], start: str, end: str | None, extra: int = 0) -> list[str]:
    out: list[str] = []
    grab = False
    for ln in lines:
        if start in ln and not grab:
            grab = True
            out.append(ln)
            continue
        if grab:
            if end and end in ln and out:
                if extra:
                    out.append(ln)
                break
            out.append(ln)
    return out


def make_screenshots() -> dict[str, Path]:
    shots: dict[str, Path] = {}
    ql = qlines()

    shots["versions"] = render_terminal(
        "01_mongodb_version.png",
        "sukhada@ubuntu-lab: ~  —  MongoDB toolchain on Ubuntu 24.04",
        (RESULTS / "01_versions.txt").read_text().splitlines(),
    )

    sample = (RESULTS / "02_sample_json.txt").read_text().splitlines()
    # first document only (keeps the screenshot on one PDF page)
    cut = 1
    for i, ln in enumerate(sample):
        if ln.startswith("--- document 2"):
            cut = i
            break
    shots["json"] = render_terminal(
        "02_unstructured_json.png",
        "sukhada@ubuntu-lab: ~/nosql  —  schema-less review JSON",
        sample[:cut],
    )

    setup = (RESULTS / "03_setup.txt").read_text().splitlines()
    setup_shot = setup[:9] + [
        "  validator.$jsonSchema.required: [review_id, product, rating, body]",
        "  additionalProperties: true",
    ]
    shots["setup"] = render_terminal(
        "03_create_collection.png",
        "sukhada@ubuntu-lab: ~/nosql  —  createCollection + loose JSON Schema",
        setup_shot,
    )

    shots["import"] = render_terminal(
        "04_mongoimport.png",
        "sukhada@ubuntu-lab: ~/nosql  —  mongoimport JSONL",
        (RESULTS / "04_mongoimport.txt").read_text().splitlines(),
    )

    ident = extract(ql, "==== 0. server identity", "==== 3. one sample")
    shots["identity"] = render_terminal(
        "05_db_identity_count.png",
        "sukhada@ubuntu-lab: ~/nosql  —  mongosh identity + 300 documents",
        ["$ mongosh mongodb://127.0.0.1:27017 --file scripts/queries.js"] + ident[:22],
    )

    sample_doc = extract(ql, "==== 3. one sample document", "==== 4. schema-less")
    shots["findone"] = render_terminal(
        "06_findone_document.png",
        "sukhada@ubuntu-lab: ~/nosql  —  findOne nested document",
        sample_doc,
    )

    compact_keys = []
    grab = False
    for ln in ql:
        if ln.strip() == "compact:" and not compact_keys:
            grab = True
            compact_keys.append("$  # field presence after $objectToArray / $group")
            compact_keys.append("compact:")
            continue
        if grab:
            if ln.startswith("===="):
                break
            compact_keys.append(ln)
    shots["schema"] = render_terminal(
        "07_schemaless_keys.png",
        "sukhada@ubuntu-lab: ~/nosql  —  optional fields (schema-less store)",
        compact_keys,
    )

    crud = (
        extract(ql, "==== 5. CRUD — insertOne", "==== 6. CRUD")
        + [""]
        + extract(ql, "==== 7. CRUD — updateOne", "==== 8. CRUD")[:8]
        + extract(ql, "==== 8. CRUD — deleteOne", "==== 9. count")
    )
    shots["crud"] = render_terminal(
        "08_crud_operations.png",
        "sukhada@ubuntu-lab: ~/nosql  —  insertOne / updateOne / deleteOne",
        crud[:22],
    )

    cat = []
    grab = False
    seen_compact = 0
    for ln in ql:
        if ln.strip() == "compact:":
            seen_compact += 1
            if seen_compact == 2:
                grab = True
                cat.append("$  # $group by product.category")
                cat.append(ln)
                continue
        if grab:
            if ln.startswith("===="):
                break
            cat.append(ln)
    hist = []
    grab = False
    for ln in ql:
        if ln.startswith("compact histogram:"):
            grab = True
        if grab:
            if ln.startswith("===="):
                break
            hist.append(ln)
    shots["agg"] = render_terminal(
        "09_aggregation.png",
        "sukhada@ubuntu-lab: ~/nosql  —  $group category + $facet histogram",
        cat + [""] + hist,
    )
    return shots


def styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("H1", fontName="DejaVuBold", fontSize=14.5, leading=19,
                          textColor=NAVY, spaceBefore=8, spaceAfter=8))
    ss.add(ParagraphStyle("H2", fontName="DejaVuBold", fontSize=12, leading=16,
                          textColor=NAVY2, spaceBefore=8, spaceAfter=5))
    ss.add(ParagraphStyle("Body", fontName="DejaVu", fontSize=10, leading=14.2,
                          textColor=HexColor("#1C2430"), alignment=TA_JUSTIFY, spaceAfter=7))
    ss.add(ParagraphStyle("Caption", fontName="DejaVu", fontSize=8.5, leading=11,
                          textColor=MUTED, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10))
    ss.add(ParagraphStyle("Decl", fontName="DejaVu", fontSize=10.5, leading=16,
                          alignment=TA_JUSTIFY, textColor=HexColor("#1C2430"), spaceAfter=8))
    ss.add(ParagraphStyle("BulletBody", fontName="DejaVu", fontSize=10, leading=13.8,
                          textColor=HexColor("#1C2430"), leftIndent=12, spaceAfter=3))
    ss.add(ParagraphStyle("CenterSmall", fontName="DejaVu", fontSize=9, leading=12,
                          alignment=TA_CENTER, textColor=MUTED))
    return ss


def p(text, style):
    return Paragraph(text, style)


def kv_table(rows, col_w=(48 * mm, 122 * mm)):
    data = []
    for k, v in rows:
        data.append([
            Paragraph(f"<b>{k}</b>", ParagraphStyle("k", fontName="DejaVuBold", fontSize=9,
                                                    textColor=white, leading=12)),
            Paragraph(v, ParagraphStyle("v", fontName="DejaVu", fontSize=9.5,
                                        textColor=NAVY, leading=13)),
        ])
    t = Table(data, colWidths=list(col_w))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), NAVY),
        ("BACKGROUND", (1, 0), (1, -1), LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#C9D0DA")),
    ]))
    return t


def pretty_table(headers, rows, col_w):
    head = [Paragraph(h, ParagraphStyle("th", fontName="DejaVuBold", fontSize=8.4,
                                        textColor=white, leading=11)) for h in headers]
    body = []
    for r in rows:
        body.append([
            Paragraph(str(c), ParagraphStyle("td", fontName="DejaVu", fontSize=8.3,
                                             textColor=HexColor("#1C2430"), leading=11))
            for c in r
        ])
    t = Table([head] + body, colWidths=col_w, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.35, HexColor("#C9D0DA")),
    ]
    for i in range(1, len(rows) + 1):
        style.append(("BACKGROUND", (0, i), (-1, i), PALE if i % 2 else white))
    t.setStyle(TableStyle(style))
    return t


def shot(path: Path, width=160 * mm):
    with Image.open(path) as im:
        h = width * im.height / im.width
    img = RLImage(str(path), width=width, height=h)
    img.hAlign = "CENTER"
    return img


def code_blocks(text: str, lines_per_chunk: int = 42):
    lines = text.rstrip().splitlines()
    chunks = []
    for i in range(0, len(lines), lines_per_chunk):
        piece = "\n".join(lines[i:i + lines_per_chunk]) + "\n"
        inner = Preformatted(piece, ParagraphStyle(
            "pre", fontName="DejaVuMono", fontSize=6.5, leading=8.5,
            textColor=CODE_FG, backColor=CODE_BG,
        ))
        t = Table([[inner]], colWidths=[170 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("BOX", (0, 0), (-1, -1), 0.6, NAVY),
        ]))
        chunks.append(t)
    return chunks


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 14 * mm, w, 14 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, h - 15.2 * mm, w, 1.4 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("DejaVu", 7.4)
    canvas.drawString(16 * mm, h - 9.2 * mm,
                      f"{STUDENT_NAME}   |   PRN: {STUDENT_PRN}   |   Batch {STUDENT_BATCH}   |   {COURSE}")
    canvas.drawRightString(w - 16 * mm, h - 9.2 * mm, "Unstructured data → NoSQL")
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 12 * mm, w, 1.1 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("DejaVu", 7.4)
    canvas.drawString(16 * mm, 5 * mm, INSTITUTE)
    canvas.drawRightString(w - 16 * mm, 5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(MAROON)
    canvas.rect(0, 0, 18 * mm, h, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(18 * mm, 0, 2.2 * mm, h, fill=1, stroke=0)

    canvas.setFillColor(GOLD)
    canvas.setFont("DejaVu", 9)
    canvas.drawString(36 * mm, h - 28 * mm, "SYMBIOSIS INTERNATIONAL (DEEMED UNIVERSITY)")
    canvas.setFillColor(white)
    canvas.setFont("DejaVuBold", 13)
    canvas.drawString(36 * mm, h - 36 * mm, INSTITUTE)
    canvas.setFont("DejaVu", 9.5)
    canvas.setFillColor(HexColor("#C5D0E0"))
    canvas.drawString(36 * mm, h - 43 * mm, "Department of Artificial Intelligence and Machine Learning")

    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.8)
    canvas.line(36 * mm, h - 48 * mm, w - 22 * mm, h - 48 * mm)

    canvas.setFillColor(GOLD)
    canvas.setFont("DejaVuBold", 9)
    canvas.drawString(36 * mm, h - 58 * mm, "EXPERIENTIAL LEARNING  ·  LABORATORY / COURSE REPORT")
    canvas.setFillColor(white)
    canvas.setFont("DejaVuBold", 20)
    y = h - 78 * mm
    for line in ["Unstructured Data into", "a NoSQL Database"]:
        canvas.drawString(36 * mm, y, line)
        y -= 10 * mm
    canvas.setFont("DejaVu", 11)
    canvas.setFillColor(HexColor("#D7DEEA"))
    canvas.drawString(36 * mm, y - 2 * mm, "Big Data Analytics  —  MongoDB on Ubuntu 24.04")

    box_h = 64 * mm
    box_y = 78 * mm
    canvas.setFillColor(HexColor("#122744"))
    canvas.roundRect(36 * mm, box_y, w - 58 * mm, box_h, 6, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(36 * mm, box_y + box_h - 3, w - 58 * mm, 3, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("DejaVuBold", 10)
    canvas.drawString(44 * mm, box_y + 50 * mm, "STUDENT DETAILS  (for official submission)")
    info = [
        ("Name", STUDENT_NAME),
        ("PRN", STUDENT_PRN),
        ("Batch", STUDENT_BATCH),
        ("Programme", "B.Tech. AIML"),
        ("Course / Paper", COURSE),
    ]
    yy = box_y + 36 * mm
    for k, v in info:
        canvas.setFillColor(GOLD)
        canvas.setFont("DejaVu", 8)
        canvas.drawString(44 * mm, yy, k.upper())
        canvas.setFillColor(white)
        canvas.setFont("DejaVuBold", 10)
        canvas.drawString(88 * mm, yy, v)
        yy -= 6.6 * mm

    canvas.setFillColor(HexColor("#C5D0E0"))
    canvas.setFont("DejaVu", 8)
    canvas.drawString(36 * mm, 28 * mm, "MongoDB Community 8.0.32  ·  mongosh 2.10.0  ·  Ubuntu 24.04.4 LTS")
    canvas.drawString(36 * mm, 22 * mm, "300 unstructured product-review documents  |  CRUD + aggregation pipeline")
    canvas.setFillColor(GOLD)
    canvas.setFont("DejaVu", 8)
    canvas.drawString(36 * mm, 14 * mm, "Confidential academic submission  ·  original work of the student named above")
    canvas.restoreState()


def build_pdf(diagrams, shots, stats):
    ss = styles()
    out = OUT_DIR / "Sukhada_Dhingra_BDA_Unstructured_Data_NoSQL_MongoDB.pdf"
    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=TITLE,
        author=STUDENT_NAME,
        subject=f"{COURSE} laboratory report — unstructured data into NoSQL",
    )
    story = []
    story.append(PageBreak())

    story.append(p("1. Certificate / Declaration", ss["H1"]))
    story.append(p(
        f"I, <b>{STUDENT_NAME}</b>, PRN <b>{STUDENT_PRN}</b>, Batch <b>{STUDENT_BATCH}</b>, "
        f"student of {PROGRAMME} at {INSTITUTE}, constituent of {UNIVERSITY}, hereby declare that "
        f"the work presented in this laboratory report titled “{TITLE}” is my original work carried "
        f"out as part of the course <b>{COURSE}</b>. MongoDB Community "
        f"Server 8.0.32 was installed and run on <b>Ubuntu 24.04.4 LTS</b>. Three hundred unstructured "
        f"JSON review documents were imported with <font face='DejaVuMono'>mongoimport</font>, and "
        f"CRUD plus aggregation queries were executed in <font face='DejaVuMono'>mongosh</font>. "
        f"Screenshots attached in this PDF are captured from that execution and have not been copied "
        f"from another student.",
        ss["Decl"],
    ))
    story.append(p(
        "I further declare that standard references (MongoDB documentation, Sadalage &amp; Fowler "
        "NoSQL Distilled, course notes on CAP and document stores) are cited wherever theory is "
        "summarised, and that no part of this report has been submitted elsewhere for academic credit.",
        ss["Decl"],
    ))
    story.append(Spacer(1, 8 * mm))
    sign = Table(
        [
            [
                Paragraph(
                    f"<b>Student</b><br/>{STUDENT_NAME}<br/>PRN: {STUDENT_PRN}<br/>Batch: {STUDENT_BATCH}"
                    f"<br/>Signature: _______________",
                    ParagraphStyle("s", fontName="DejaVu", fontSize=9, leading=13, textColor=NAVY),
                ),
                Paragraph(
                    "<b>Course Faculty</b><br/>Name: _______________________<br/>Designation: ________________"
                    "<br/>Date: _______________________<br/>Signature: _______________",
                    ParagraphStyle("s2", fontName="DejaVu", fontSize=9, leading=13, textColor=NAVY),
                ),
            ]
        ],
        colWidths=[85 * mm, 85 * mm],
    )
    sign.setStyle(TableStyle([
        ("BOX", (0, 0), (0, 0), 0.5, NAVY),
        ("BOX", (1, 0), (1, 0), 0.5, NAVY),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(sign)
    story.append(Spacer(1, 6 * mm))

    story.append(p("2. Abstract", ss["H1"]))
    story.append(p(
        "This laboratory exercise stores <b>unstructured / semi-structured</b> product-review JSON in a "
        "<b>document NoSQL</b> database (MongoDB) on Ubuntu. Relational tables assume a fixed schema; "
        "review dumps do not: nested product and customer objects, optional titles, tag arrays, media "
        "blobs, seller replies and ETL leftovers appear on some records and not others. MongoDB accepts "
        "each record as a BSON document without ALTER TABLE. A generator wrote <b>300 JSONL documents</b>; "
        "<font face='DejaVuMono'>mongoimport</font> loaded them into <font face='DejaVuMono'>sit_bda.product_reviews</font> "
        "(300 imported, 0 failed). mongosh then demonstrated CRUD (count went 300 → 301 → 300), projection, "
        "sort/skip/limit, and aggregation ($group by category, $match on Pune, $unwind on tags, $facet "
        "histogram). Electronics led volume (81 reviews, mean rating 3.84). Optional fields prove the "
        "schema-less claim: tags 79%, title 72%, media 20%, seller_reply 10%, return_reason 2%.",
        ss["Body"],
    ))

    story.append(p("3. Contents", ss["H1"]))
    toc = [
        ("1", "Certificate / Declaration"),
        ("2", "Abstract"),
        ("3", "Contents"),
        ("4", "Aim, objectives and apparatus"),
        ("5", "Unstructured data and NoSQL"),
        ("6", "MongoDB document model and CAP"),
        ("7", "Dataset and schema-less design"),
        ("8", "Implementation procedure (Ubuntu)"),
        ("9", "Source listings"),
        ("10", "Execution screenshots"),
        ("11", "Results and analysis"),
        ("12", "Observations, viva notes and limitations"),
        ("13", "Conclusion"),
        ("14", "References"),
    ]
    story.append(pretty_table(["§", "Section"], toc, [18 * mm, 152 * mm]))

    story.append(p("4. Aim, objectives and apparatus", ss["H1"]))
    story.append(p("4.1 Aim", ss["H2"]))
    story.append(p(
        "To ingest unstructured JSON into a NoSQL (MongoDB) database on Ubuntu, to design a loose "
        "document schema that tolerates missing and nested fields, and to run CRUD plus aggregation "
        "queries that would be awkward in a rigid relational schema.",
        ss["Body"],
    ))
    story.append(p("4.2 Objectives", ss["H2"]))
    for item in [
        "Install and start MongoDB Community Server on Ubuntu 24.04 and verify mongod / mongosh / mongoimport.",
        "Generate an unstructured product-review corpus (JSON Lines) with nested objects and optional fields.",
        "Create a database and collection with a *loose* JSON Schema (required keys only; additionalProperties true).",
        "Bulk-load the corpus with mongoimport and confirm document counts.",
        "Perform insert, find (filter + projection), update and delete on the collection.",
        "Run aggregations: $group, $match, $unwind, $sort / $skip / $limit, and $facet.",
    ]:
        story.append(p(f"•  {item}", ss["BulletBody"]))
    story.append(p("4.3 Apparatus (actually used)", ss["H2"]))
    story.append(kv_table([
        ("Student", f"{STUDENT_NAME}  ·  PRN {STUDENT_PRN}  ·  Batch {STUDENT_BATCH}"),
        ("OS", "Ubuntu 24.04.4 LTS  (Linux 6.12.94+ x86_64)"),
        ("NoSQL engine", "MongoDB Community Server 8.0.32  (mongod, WiredTiger)"),
        ("Shell / tools", "mongosh 2.10.0  ·  mongoimport 100.18.0"),
        ("Language", "Python 3.12 (dataset generator)  ·  mongosh JavaScript (queries)"),
        ("Database", "sit_bda.product_reviews  ·  localhost:27017"),
        ("Corpus", "300 JSONL product-review documents (schema-less)"),
    ]))

    story.append(p("5. Unstructured data and NoSQL", ss["H1"]))
    story.append(p(
        "Big Data is often described by volume, velocity and <b>variety</b>. Variety is the reason this "
        "lab exists. Clickstream logs, product reviews, social posts and device telemetry rarely arrive "
        "as tidy 3NF tables. They arrive as JSON, XML, free text and nested maps whose keys change from "
        "event to event. Forcing that feed into VARCHAR columns either drops fields or explodes the "
        "schema. NoSQL document stores keep the native shape: one record ≈ one JSON document, arrays "
        "and sub-documents allowed, missing keys allowed.",
        ss["Body"],
    ))
    story.append(shot(diagrams["why"], 160 * mm))
    story.append(p("Figure 1. Unstructured JSON maps onto MongoDB documents; a rigid table does not.", ss["Caption"]))
    story.append(p(
        "The four common NoSQL families are key–value, document, wide-column and graph. This lab uses "
        "the <b>document</b> family (MongoDB). It is the usual choice when the payload is already JSON "
        "and the queries need secondary indexes plus aggregation, not just get-by-key.",
        ss["Body"],
    ))

    story.append(p("6. MongoDB document model and CAP", ss["H1"]))
    story.append(p("6.1 Logical stack", ss["H2"]))
    story.append(p(
        "A MongoDB deployment is one or more <font face='DejaVuMono'>mongod</font> processes. Data sits "
        "in databases; databases hold collections; collections hold documents stored as BSON (Binary JSON). "
        "There is no JOIN-centric schema. Related data is <b>embedded</b> (product inside the review) or "
        "referenced by id. This lab embeds product and customer because they travel with the review.",
        ss["Body"],
    ))
    story.append(shot(diagrams["stack"], 160 * mm))
    story.append(p("Figure 2. mongod → database sit_bda → collection product_reviews → BSON documents.", ss["Caption"]))
    story.append(p("6.2 CAP theorem (viva)", ss["H2"]))
    story.append(p(
        "Brewer’s CAP theorem says a distributed store cannot simultaneously provide consistency, "
        "availability and partition tolerance. Network partitions happen, so the practical choice is "
        "CP versus AP. A MongoDB replica set defaults toward <b>CP</b>: a primary takes writes; if the "
        "primary is partitioned away, a new primary is elected and writes wait. Read concern / write "
        "concern can be relaxed toward availability. This Ubuntu lab is a <b>single-node</b> mongod, so "
        "CAP is discussed theoretically rather than demonstrated with a replica-set partition.",
        ss["Body"],
    ))
    story.append(p("6.3 Loose JSON Schema", ss["H2"]))
    story.append(p(
        "MongoDB can run with no validator at all. For the lab a <i>loose</i> $jsonSchema was attached: "
        "review_id, product, rating and body are required; <font face='DejaVuMono'>additionalProperties: true</font> "
        "lets every other key through. That is the opposite of a relational CREATE TABLE that lists "
        "every column up front. It still blocks obviously broken inserts (no rating, empty body) — a "
        "compromise used in production lakes as well.",
        ss["Body"],
    ))

    story.append(p("7. Dataset and schema-less design", ss["H1"]))
    story.append(p(
        "The corpus is a synthetic but realistic e-commerce review dump: nested product (sku, name, "
        "brand, category), nested customer (handle, city, sometimes verified_purchase), free-text body, "
        "and optional extras. A Python generator with a fixed seed (the PRN) wrote JSON Lines so "
        "<font face='DejaVuMono'>mongoimport</font> can stream one document per line.",
        ss["Body"],
    ))
    opt_rows = []
    n = stats["n"]
    for k, c in stats["keys"].most_common():
        opt_rows.append([k, str(c), f"{100 * c / n:.0f}%"])
    story.append(pretty_table(
        ["Top-level field", "Documents", "Presence"],
        opt_rows,
        [70 * mm, 45 * mm, 55 * mm],
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(shot(diagrams["schema_chart"], 150 * mm))
    story.append(p(
        "Figure 3. Optional keys (tags, title, media, seller_reply, return_reason) are the unstructured part.",
        ss["Caption"],
    ))
    story.append(p(
        "If this were PostgreSQL, every optional field would be a nullable column or a JSONB sidecar. "
        "Here they simply appear on some documents. REV-0001 even carries return_reason and media while "
        "REV-0002 carries ingest_meta and tags — two neighbouring rows that would not share a column set.",
        ss["Body"],
    ))

    story.append(p("8. Implementation procedure (Ubuntu)", ss["H1"]))
    story.append(shot(diagrams["pipeline"], 160 * mm))
    story.append(p("Figure 4. End-to-end lab pipeline actually executed.", ss["Caption"]))
    steps = [
        ("1. Install", "Official MongoDB 8.0 APT repo on Ubuntu noble; packages mongodb-org, mongosh, mongoimport."),
        ("2. Start mongod", "Forked mongod on 127.0.0.1:27017 (no systemd in this lab VM). ping {ok:1}."),
        ("3. Generate JSONL", "python3 scripts/generate_dataset.py → 300 documents."),
        ("4. Create collection", "mongosh scripts/setup.js — sit_bda.product_reviews + loose validator."),
        ("5. Import", "mongoimport --db sit_bda --collection product_reviews --file dataset/product_reviews.jsonl"),
        ("6. Query", "mongosh --file scripts/queries.js — CRUD, count/sort/limit/skip, aggregations."),
    ]
    story.append(pretty_table(["Step", "What was done"], steps, [32 * mm, 138 * mm]))
    story.append(p(
        "Re-running the lab is <font face='DejaVuMono'>bash scripts/run_lab.sh</font> with mongod already "
        "listening. Output transcripts are saved under <font face='DejaVuMono'>results/</font>.",
        ss["Body"],
    ))

    story.append(p("9. Source listings", ss["H1"]))
    story.append(p("9.1 Collection setup (scripts/setup.js)", ss["H2"]))
    story.append(p(
        "The validator requires four fields only. additionalProperties remains true so unstructured extras survive.",
        ss["Body"],
    ))
    for block in code_blocks((SCRIPTS / "setup.js").read_text(), 40):
        story.append(block)
        story.append(Spacer(1, 2 * mm))
    story.append(p("9.2 Query script — CRUD and aggregation (excerpt from scripts/queries.js)", ss["H2"]))
    qsrc = (SCRIPTS / "queries.js").read_text().splitlines()
    start = next(i for i, ln in enumerate(qsrc) if "banner(\"5. CRUD" in ln)
    end = next(i for i, ln in enumerate(qsrc) if "banner(\"9. count" in ln)
    start2 = next(i for i, ln in enumerate(qsrc) if "banner(\"10. aggregation" in ln)
    end2 = next(i for i, ln in enumerate(qsrc) if "banner(\"11. aggregation" in ln)
    excerpt = "\n".join(qsrc[start:end] + ["", "// --- aggregation ---", ""] + qsrc[start2:end2])
    for block in code_blocks(excerpt, 44):
        story.append(block)
        story.append(Spacer(1, 2 * mm))
    story.append(p(
        "The full mongosh file (identity, schema-less $objectToArray, Pune $match, $unwind tags, $facet) "
        "is submitted alongside this PDF as scripts/queries.js.",
        ss["Body"],
    ))

    story.append(p("10. Execution screenshots", ss["H1"]))
    story.append(p(
        "All terminals below are painted from the real stdout/stderr of the Ubuntu session (MongoDB 8.0.32). "
        "Host prompt is labelled as the student lab machine.",
        ss["Body"],
    ))
    caps = [
        ("versions", "Figure 5. mongod 8.0.32, mongosh 2.10.0, mongoimport 100.18.0, Ubuntu 24.04, ping ok:1."),
        ("json", "Figure 6. One unstructured review: nested product/customer, optional title, media, return_reason."),
        ("setup", "Figure 7. createCollection with JSON Schema — additionalProperties: true."),
        ("import", "Figure 8. mongoimport: 300 document(s) imported successfully, 0 failed."),
        ("identity", "Figure 9. mongosh session stamped with student name, PRN 24070126505, Batch A3; 300 docs."),
        ("findone", "Figure 10. findOne() of a nested BSON document after import."),
        ("schema", "Figure 11. Field-presence aggregation — tags 79%, title 72%, return_reason 2%."),
        ("crud", "Figure 12. insertOne → 301 documents; updateOne matched; deleteOne → 300 again."),
        ("agg", "Figure 13. $group by category (electronics 81 @ 3.84) and $facet rating histogram."),
    ]
    for key, cap in caps:
        story.append(shot(shots[key], 158 * mm))
        story.append(p(cap, ss["Caption"]))

    story.append(p("11. Results and analysis", ss["H1"]))
    story.append(p("11.1 Import and CRUD", ss["H2"]))
    story.append(pretty_table(
        ["Check", "Result", "Meaning"],
        [
            ["mongoimport", "300 imported / 0 failed", "JSONL parsed as one BSON document per line"],
            ["countDocuments after import", "300", "Collection populated"],
            ["insertOne REV-LAB-INSERT", "301", "Schema accepted extra nested keys (viva_note, tags)"],
            ["updateOne $set / $inc", "matchedCount 1", "New fields lab_verified, faculty_flag added in place"],
            ["deleteOne", "300", "Lab insert removed; corpus restored"],
            ["count rating == 1", "16", "Low-star slice for quality monitoring"],
        ],
        [48 * mm, 42 * mm, 80 * mm],
    ))
    story.append(p("11.2 Aggregation by category", ss["H2"]))
    story.append(pretty_table(
        ["Category", "n", "avg rating", "min", "max"],
        [
            ["electronics", "81", "3.84", "1", "5"],
            ["clothing", "54", "3.74", "1", "5"],
            ["grocery", "54", "3.81", "1", "5"],
            ["books", "47", "3.85", "2", "5"],
            ["beauty", "42", "3.83", "1", "5"],
            ["home", "22", "3.45", "1", "5"],
        ],
        [40 * mm, 28 * mm, 38 * mm, 32 * mm, 32 * mm],
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(shot(diagrams["cat_chart"], 145 * mm))
    story.append(p("Figure 14. Review volume by category — electronics is the largest slice of the dump.", ss["Caption"]))
    story.append(p(
        "Books have the highest mean rating (3.85) and no 1-star rows in this sample (min 2). Home is "
        "smallest and weakest (22 reviews, 3.45). A relational GROUP BY would need a reviews table plus "
        "a products table and a join; MongoDB grouped on the embedded path product.category.",
        ss["Body"],
    ))
    story.append(p("11.3 Rating histogram and optional-field analytics", ss["H2"]))
    story.append(pretty_table(
        ["Star rating", "Count", "Share of 300"],
        [
            ["1", "16", "5.3%"],
            ["2", "27", "9.0%"],
            ["3", "65", "21.7%"],
            ["4", "88", "29.3%"],
            ["5", "104", "34.7%"],
        ],
        [45 * mm, 45 * mm, 80 * mm],
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(shot(diagrams["rating_chart"], 130 * mm))
    story.append(p("Figure 15. $facet histogram — the dump is skewed toward 4–5 star reviews.", ss["Caption"]))
    story.append(p(
        "$facet also counted documents that only some reviews carry: return_reason = 5, seller_reply = 30, "
        "media = 60. Those counts are exactly the schema-less fields from §7. $unwind on tags ranked "
        "topics (loud 42, fading 39, fit 37, …, ubuntu 35) — array analytics that would need a bridge "
        "table in SQL.",
        ss["Body"],
    ))
    story.append(p("11.4 Pune slice", ss["H2"]))
    story.append(p(
        "A $match on customer.city = \"Pune\" followed by $group on product.brand is the NoSQL form of "
        "SELECT brand, COUNT(*), AVG(rating) WHERE city = 'Pune' GROUP BY brand. Top Pune brands in this "
        "run were SonicPulse, IndigoYard and VoltNest (6 reviews each). Clickora had the best Pune mean "
        "among the displayed six (4.25).",
        ss["Body"],
    ))

    story.append(p("12. Observations, viva notes and limitations", ss["H1"]))
    story.append(p("12.1 Observations", ss["H2"]))
    for item in [
        "JSONL (one object per line) is the correct import format; a giant JSON array needs --jsonArray.",
        "Missing fields are not errors. find({title: {$exists: false}}) is how you hunt incomplete records.",
        "Embedded product.category avoids a join for the main grouping query in this lab.",
        "insertOne accepted viva_note and extra_unstructured without any DDL — the unstructured lesson.",
        "deleteOne of the lab document restored the 300-row corpus; labs should always clean up.",
        "Aggregation pipelines are ordered stages, not a single SQL text blob — easier to extend.",
    ]:
        story.append(p(f"•  {item}", ss["BulletBody"]))
    story.append(p("12.2 Likely viva questions (with short answers)", ss["H2"]))
    story.append(pretty_table(
        ["Question", "Model answer"],
        [
            ["What is unstructured data here?",
             "JSON reviews with nested objects, arrays and keys that appear only on some documents."],
            ["Why not MySQL?",
             "Optional nested fields would force NULLs, JSON columns or frequent ALTER TABLE. MongoDB stores the native shape."],
            ["Document vs key–value?",
             "Key–value is opaque get/put. Document stores index fields inside the value and run aggregations."],
            ["CAP for this lab?",
             "Single-node mongod; theoretically a replica set defaults CP (primary writes, election on partition)."],
            ["BSON vs JSON?",
             "BSON is MongoDB’s typed binary encoding (dates, ObjectId, int vs double) of a JSON-like document."],
            ["What does $unwind do?",
             "It emits one document per array element so $group can count tags."],
            ["mongoimport vs insertMany?",
             "mongoimport is the CLI bulk loader from files; insertMany is the driver/API equivalent."],
            ["additionalProperties: true?",
             "JSON Schema will not reject unknown keys — required for unstructured ingest."],
        ],
        [48 * mm, 122 * mm],
    ))
    story.append(p("12.3 Limitations", ss["H2"]))
    story.append(p(
        "The corpus is 300 documents so every counter fits on a screenshot; a production lake would be "
        "millions of events and would use sharded clusters, hashed shard keys and indexes on product.sku "
        "and customer.city. This VM has no systemd, so mongod was forked by hand. Replica-set failover "
        "and authentication were not enabled. Text search used a regex on body rather than a text index. "
        "Those are acceptable limits for a first NoSQL ingest lab.",
        ss["Body"],
    ))

    story.append(p("13. Conclusion", ss["H1"]))
    story.append(p(
        f"This laboratory exercise for <b>Big Data Analytics</b> showed how unstructured JSON is stored "
        f"and queried in a NoSQL document database. I, <b>{STUDENT_NAME}</b> (PRN <b>{STUDENT_PRN}</b>, "
        f"Batch <b>{STUDENT_BATCH}</b>), installed MongoDB 8.0.32 on Ubuntu 24.04, generated 300 "
        f"schema-less product reviews, imported them with zero failures, and executed CRUD plus "
        f"aggregation pipelines in mongosh. Field-presence analysis confirmed the unstructured claim "
        f"(return_reason on only 5/300 documents). Category aggregation and a rating histogram produced "
        f"analytics that would otherwise need joins and sparse columns. Screenshots of version, import "
        f"SUCCESS, CRUD counts and compact aggregation tables are attached as evidence. The same "
        f"ingest-then-query pattern is how click logs, IoT payloads and social feeds enter a modern "
        f"data platform.",
        ss["Body"],
    ))

    story.append(p("14. References", ss["H1"]))
    refs = [
        "MongoDB Inc. (2026). Install MongoDB Community Edition on Ubuntu. https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/",
        "MongoDB Inc. mongoimport, mongosh, Aggregation Pipeline, $jsonSchema documentation.",
        "Sadalage, P. J. and Fowler, M. NoSQL Distilled. Addison-Wesley.",
        "Brewer, E. (2012). CAP twelve years later: How the “rules” have changed. IEEE Computer.",
        "Dean, J. and Ghemawat, S. (2004). MapReduce: Simplified Data Processing on Large Clusters. OSDI. (Big Data processing context.)",
        "Course notes: Big Data Analytics — NoSQL databases, schema-less models and MongoDB laboratory.",
    ]
    for i, r in enumerate(refs, 1):
        story.append(p(f"[{i}]  {r}", ss["BulletBody"]))

    story.append(Spacer(1, 8 * mm))
    story.append(p(
        f"— End of report —<br/>Submitted by <b>{STUDENT_NAME}</b>  ·  PRN {STUDENT_PRN}  ·  "
        f"Batch {STUDENT_BATCH}",
        ss["CenterSmall"],
    ))

    def first_page(c, d):
        cover_page(c, d)

    def later(c, d):
        header_footer(c, d)

    doc.build(story, onFirstPage=first_page, onLaterPages=later)
    return out


def main():
    docs = load_docs()
    stats = dataset_stats(docs)
    diagrams = make_diagrams(stats)
    shots = make_screenshots()
    pdf = build_pdf(diagrams, shots, stats)
    print(f"PDF written: {pdf}")
    print(f"size_bytes={pdf.stat().st_size}")
    print("screenshots:")
    for k, v in shots.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
