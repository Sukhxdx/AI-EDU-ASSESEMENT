#!/usr/bin/env python3
"""Generate the Experiential Learning PDF for Hadoop MapReduce."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    Image as RLImage,
    KeepTogether,
    ListFlowable,
    ListItem,
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
WORK = ROOT / "work"
SRC = ROOT / "src"

SHOTS.mkdir(parents=True, exist_ok=True)
DIAG.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

STUDENT_NAME = "Sukhada Dhingra"
STUDENT_PRN = "24070126505"
PROGRAMME = "B.Tech. (Artificial Intelligence and Machine Learning)"
INSTITUTE = "Symbiosis Institute of Technology, Pune"
UNIVERSITY = "Symbiosis International (Deemed University)"
COURSE = "Big Data Analytics"
TITLE = "Experiential Learning: Hadoop MapReduce Paradigm"
EMAIL = "dhingrasukhada@gmail.com"
PHONE = "+91 83172 22120"
SUBMISSION_DATE = "09 September 2026"
AY = "2025–26"

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
pdfmetrics.registerFont(TTFont("DejaVuSerif", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSerifBold", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMonoBold", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"))

MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
MONO_B = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 15)
UI = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
UI_B = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)


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
    """Paint a realistic dark terminal window from captured Hadoop output."""
    expanded: list[tuple[str, str]] = []
    for raw in lines:
        kind = "out"
        if raw.startswith("$ "):
            kind = "cmd"
        elif "WARN" in raw:
            kind = "warn"
        elif "completed successfully" in raw or "map 100%" in raw:
            kind = "ok"
        elif raw.startswith("INFO") or " INFO " in raw:
            kind = "info"
        for piece in wrap_line(raw.expandtabs(8), 96):
            expanded.append((kind, piece))

    pad_x, pad_y = 22, 18
    line_h = 22
    title_h = 42
    width = 1100
    height = title_h + pad_y * 2 + line_h * max(8, len(expanded)) + 18
    img = Image.new("RGB", (width, height), (15, 18, 24))
    draw = ImageDraw.Draw(img)

    # title bar
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


def make_diagrams() -> dict[str, Path]:
    paths = {}

    # 1. Hadoop stack
    fig, ax = plt.subplots(figsize=(10.2, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    layers = [
        (0.5, 4.4, 9.0, 0.9, "#8B1E3F", "Applications  ·  WordCount  ·  Sales Analysis  ·  Hive / Pig / Spark"),
        (0.5, 3.3, 9.0, 0.9, "#1F6F78", "MapReduce processing engine  ·  Mapper  ·  Shuffle/Sort  ·  Reducer"),
        (0.5, 2.2, 9.0, 0.9, "#16325C", "YARN resource manager  ·  ResourceManager  ·  NodeManager"),
        (0.5, 1.1, 9.0, 0.9, "#0B1F3A", "HDFS storage  ·  NameNode (metadata)  ·  DataNodes (blocks, replication)"),
    ]
    ax.set_title("Apache Hadoop Ecosystem (logical stack)", fontsize=13, pad=8, color="#0B1F3A", fontweight="bold")
    for x, y, w, h, c, label in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                    facecolor=c, edgecolor="white", linewidth=1.5))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", color="white", fontsize=10)
    ax.text(5, 0.45, "Commodity hardware cluster  ·  data locality  ·  fault tolerance",
            ha="center", fontsize=9, color="#5B6573")
    p = DIAG / "hadoop_stack.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["stack"] = p

    # 2. MapReduce flow
    fig, ax = plt.subplots(figsize=(10.6, 4.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_title("MapReduce data flow", fontsize=13, pad=6, color="#0B1F3A", fontweight="bold")
    boxes = [
        (0.3, 1.7, 2.2, 1.6, "#0B1F3A", "Input\nsplits\n(HDFS / files)"),
        (3.0, 1.7, 2.2, 1.6, "#1F6F78", "MAP\n(k1,v1) →\nlist(k2,v2)"),
        (5.7, 1.7, 2.2, 1.6, "#8B1E3F", "Shuffle\n& Sort\ngroup by k2"),
        (8.4, 1.7, 2.2, 1.6, "#16325C", "REDUCE\n(k2, list v2)\n→ (k3,v3)"),
    ]
    for x, y, w, h, c, label in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.1",
                                    facecolor=c, edgecolor="white", linewidth=1.4))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", color="white", fontsize=9.5)
        if x < 8:
            ax.annotate("", xy=(x + w + 0.38, y + h / 2), xytext=(x + w + 0.08, y + h / 2),
                        arrowprops=dict(arrowstyle="->", color="#0B1F3A", lw=1.6))
    ax.add_patch(FancyBboxPatch((10.7, 1.7), 1.1, 1.6, boxstyle="round,pad=0.03,rounding_size=0.1",
                                facecolor="#C9A227", edgecolor="white", linewidth=1.4))
    ax.text(11.25, 2.5, "part-r\n-00000", ha="center", va="center", fontsize=8.5, color="#0B1F3A", fontweight="bold")
    ax.annotate("", xy=(10.7, 2.5), xytext=(10.7 - 0.08, 2.5),
                arrowprops=dict(arrowstyle="->", color="#0B1F3A", lw=1.6))
    ax.text(1.4, 0.7, "RecordReader", ha="center", fontsize=8, color="#5B6573")
    ax.text(4.1, 0.7, "Combiner (optional)", ha="center", fontsize=8, color="#5B6573")
    ax.text(6.8, 0.7, "Partition / merge", ha="center", fontsize=8, color="#5B6573")
    ax.text(9.5, 0.7, "Aggregate / write", ha="center", fontsize=8, color="#5B6573")
    p = DIAG / "mapreduce_flow.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["flow"] = p

    # 3. WordCount dry run
    fig, ax = plt.subplots(figsize=(10.4, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_title("WordCount dry run (tiny example)", fontsize=13, pad=6, color="#0B1F3A", fontweight="bold")
    steps = [
        (0.4, 3.6, 2.6, 1.8, "#0B1F3A", "Input line\n\"Hadoop MapReduce\nHadoop\""),
        (3.4, 3.6, 2.8, 1.8, "#1F6F78", "Map emits\n(hadoop,1)\n(mapreduce,1)\n(hadoop,1)"),
        (6.6, 3.6, 2.9, 1.8, "#8B1E3F", "Shuffle groups\nhadoop → 1,1\nmapreduce → 1"),
        (3.4, 0.7, 2.8, 2.0, "#16325C", "Reduce sums\nhadoop → 2\nmapreduce → 1"),
        (6.6, 0.7, 2.9, 2.0, "#C9A227", "Output\nhadoop\\t2\nmapreduce\\t1"),
    ]
    for x, y, w, h, c, label in steps:
        fc = c
        tc = "white" if c != "#C9A227" else "#0B1F3A"
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.1",
                                    facecolor=fc, edgecolor="white", linewidth=1.4))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", color=tc, fontsize=9)
    ax.annotate("", xy=(3.35, 4.5), xytext=(3.05, 4.5), arrowprops=dict(arrowstyle="->", color="#0B1F3A", lw=1.5))
    ax.annotate("", xy=(6.55, 4.5), xytext=(6.25, 4.5), arrowprops=dict(arrowstyle="->", color="#0B1F3A", lw=1.5))
    ax.annotate("", xy=(4.8, 2.75), xytext=(4.8, 3.55), arrowprops=dict(arrowstyle="->", color="#0B1F3A", lw=1.5))
    ax.annotate("", xy=(6.55, 1.7), xytext=(6.25, 1.7), arrowprops=dict(arrowstyle="->", color="#0B1F3A", lw=1.5))
    p = DIAG / "wordcount_dryrun.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["dryrun"] = p

    # 4. charts from real output
    wc_path = WORK / "output_wc" / "part-r-00000"
    counts = {}
    for line in wc_path.read_text().splitlines():
        if not line.strip():
            continue
        w, c = line.split("\t")
        counts[w] = int(c)
    top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:12]
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    words = [w for w, _ in top][::-1]
    vals = [c for _, c in top][::-1]
    ax.barh(words, vals, color="#16325C")
    ax.set_xlabel("Frequency")
    ax.set_title("WordCount — top 12 tokens (actual job output)", fontsize=12, color="#0B1F3A")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    p = DIAG / "wordcount_chart.png"
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["wc_chart"] = p

    sales = {}
    for line in (WORK / "output_sales" / "part-r-00000").read_text().splitlines():
        k, v = line.split("\t")
        sales[k] = int(v)
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    cats = list(sales.keys())
    ax.bar(cats, [sales[c] for c in cats], color=["#8B1E3F", "#1F6F78", "#16325C"])
    ax.set_ylabel("Units sold")
    ax.set_title("SalesAnalysis — units by category (actual job output)", fontsize=12, color="#0B1F3A")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for i, c in enumerate(cats):
        ax.text(i, sales[c] + 3, str(sales[c]), ha="center", fontsize=10)
    fig.tight_layout()
    p = DIAG / "sales_chart.png"
    fig.savefig(p, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    paths["sales_chart"] = p

    return paths


def make_screenshots() -> dict[str, Path]:
    wc_out = (WORK / "output_wc" / "part-r-00000").read_text().strip().splitlines()
    top = sorted(
        (line.split("\t") for line in wc_out if "\t" in line),
        key=lambda kv: int(kv[1]),
        reverse=True,
    )
    sales_out = (WORK / "output_sales" / "part-r-00000").read_text().strip()

    shots = {}
    shots["version"] = render_terminal(
        "01_hadoop_version.png",
        "sukhada@hadoop-lab: ~/mapreduce  —  Hadoop version",
        [
            "$ java -version",
            "openjdk version \"21.0.10\" 2026-01-20",
            "OpenJDK Runtime Environment (build 21.0.10+7-Ubuntu-124.04)",
            "OpenJDK 64-Bit Server VM (build 21.0.10+7-Ubuntu-124.04, mixed mode, sharing)",
            "$ hadoop version",
            "Hadoop 3.5.0",
            "Source code repository https://github.com/apache/hadoop.git -r dbcc7cd797100e6b32cd84f85b53a5193a5f9af0",
            "Compiled by cnauroth on 2026-03-24T16:56Z",
            "Compiled on platform linux-x86_64",
            "This command was run using /home/ubuntu/hadoop/hadoop-3.5.0/share/hadoop/common/hadoop-common-3.5.0.jar",
        ],
    )
    shots["input"] = render_terminal(
        "02_input_dataset.png",
        "sukhada@hadoop-lab: ~/mapreduce  —  input dataset",
        [
            "$ ls -l work/input_wc",
            "total 4",
            "-rw-r--r-- 1 ubuntu ubuntu 2076 Sep  9 22:27 hadoop_intro.txt",
            "$ cat work/input_wc/hadoop_intro.txt",
            "Hadoop MapReduce is a programming paradigm used for processing huge volumes of data",
            "in a distributed and parallel manner. Big Data Analytics relies on Hadoop because a",
            "single machine cannot store or process terabytes and petabytes of information.",
            "The Hadoop Distributed File System stores data as blocks across DataNodes. ...",
            "Word count is the Hello World of MapReduce. Every mapper emits a word and the",
            "number one. Combiners perform local aggregation. Reducers compute the global",
            "frequency of each word.",
        ],
    )
    shots["compile"] = render_terminal(
        "03_compile_jar.png",
        "sukhada@hadoop-lab: ~/mapreduce  —  compile MapReduce job",
        [
            "$ export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64",
            "$ export HADOOP_HOME=/home/ubuntu/hadoop/hadoop-3.5.0",
            "$ hadoop com.sun.tools.javac.Main -d work src/WordCount.java",
            "$ jar cf work/wordcount.jar -C work WordCount.class \\",
            "    -C work WordCount\\$TokenizerMapper.class -C work WordCount\\$IntSumReducer.class",
            "$ hadoop com.sun.tools.javac.Main -d work src/SalesAnalysis.java",
            "$ jar cf work/sales.jar -C work SalesAnalysis.class ...",
            "$ ls -l work/*.jar work/*.class",
            "-rw-r--r-- 1 ubuntu ubuntu 3350 Sep  9 22:27 work/wordcount.jar",
            "-rw-r--r-- 1 ubuntu ubuntu 3441 Sep  9 22:27 work/sales.jar",
            "-rw-r--r-- 1 ubuntu ubuntu 1676 Sep  9 22:27 work/WordCount.class",
            "-rw-r--r-- 1 ubuntu ubuntu 1695 Sep  9 22:27 work/SalesAnalysis.class",
        ],
    )
    shots["job"] = render_terminal(
        "04_wordcount_job.png",
        "sukhada@hadoop-lab: ~/mapreduce  —  WordCount job execution",
        [
            "$ hadoop jar work/wordcount.jar WordCount work/input_wc work/output_wc",
            "INFO input.FileInputFormat: Total input files to process : 1",
            "INFO mapreduce.JobSubmitter: number of splits:1",
            "INFO mapreduce.Job: Running job: job_local1654115753_0001",
            "INFO mapred.MapTask: Processing split: file:/workspace/.../hadoop_intro.txt:0+2076",
            "INFO mapred.Task: Task 'attempt_local1654115753_0001_m_000000_0' done.",
            "Map-Reduce Framework",
            "    Map input records=34",
            "    Map output records=316",
            "    Combine input records=316",
            "    Combine output records=197",
            "INFO mapreduce.Job:  map 100% reduce 100%",
            "INFO mapreduce.Job: Job job_local1654115753_0001 completed successfully",
            "    Reduce input groups=197",
            "    Reduce output records=197",
            "    File Input Format Counters  Bytes Read=2076",
            "    File Output Format Counters  Bytes Written=1837",
        ],
    )
    shots["wc_out"] = render_terminal(
        "05_wordcount_output.png",
        "sukhada@hadoop-lab: ~/mapreduce  —  WordCount part-r-00000",
        [
            "$ ls -l work/output_wc",
            "total 4",
            "-rw-r--r-- 1 ubuntu ubuntu 1837 Sep  9 22:28 part-r-00000",
            "-rw-r--r-- 1 ubuntu ubuntu    0 Sep  9 22:28 _SUCCESS",
            "$ sort -k2 -n -r work/output_wc/part-r-00000 | head -15",
            *[f"{w:<16}{c}" for w, c in top[:15]],
        ],
    )
    shots["sales_in"] = render_terminal(
        "06_sales_input.png",
        "sukhada@hadoop-lab: ~/mapreduce  —  sales dataset",
        [
            "$ cat work/input_sales/sales.csv",
            "category,product,units,city",
            "electronics,laptop,12,Pune",
            "electronics,smartphone,30,Mumbai",
            "grocery,rice,40,Nagpur",
            "grocery,wheat,25,Pune",
            "clothing,tshirt,22,Mumbai",
            "clothing,jeans,14,Pune",
            "... (20 data rows + header)",
        ],
    )
    shots["sales_job"] = render_terminal(
        "07_sales_job_output.png",
        "sukhada@hadoop-lab: ~/mapreduce  —  SalesAnalysis job + output",
        [
            "$ hadoop jar work/sales.jar SalesAnalysis work/input_sales work/output_sales",
            "INFO input.FileInputFormat: Total input files to process : 1",
            "INFO mapreduce.Job: Running job: job_local425182150_0001",
            "Map-Reduce Framework",
            "    Map input records=21",
            "    Map output records=20",
            "    Combine input records=20",
            "    Combine output records=3",
            "    Reduce input groups=3",
            "    Reduce output records=3",
            "INFO mapreduce.Job:  map 100% reduce 100%",
            "INFO mapreduce.Job: Job job_local425182150_0001 completed successfully",
            "$ cat work/output_sales/part-r-00000",
            *[ln.replace("\t", "    ") for ln in sales_out.splitlines()],
        ],
    )
    return shots


def styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("CoverKicker", fontName="DejaVu", fontSize=9.5, textColor=GOLD,
                          alignment=TA_CENTER, spaceAfter=6))
    ss.add(ParagraphStyle("CoverTitle", fontName="DejaVuBold", fontSize=22, leading=26,
                          textColor=white, alignment=TA_CENTER, spaceAfter=8))
    ss.add(ParagraphStyle("CoverSub", fontName="DejaVu", fontSize=11.5, leading=16,
                          textColor=HexColor("#D7DEEA"), alignment=TA_CENTER))
    ss.add(ParagraphStyle("H1", fontName="DejaVuBold", fontSize=14.5, leading=19,
                          textColor=NAVY, spaceBefore=8, spaceAfter=8))
    ss.add(ParagraphStyle("H2", fontName="DejaVuBold", fontSize=12, leading=16,
                          textColor=NAVY2, spaceBefore=8, spaceAfter=5))
    ss.add(ParagraphStyle("Body", fontName="DejaVu", fontSize=10, leading=14.2,
                          textColor=HexColor("#1C2430"), alignment=TA_JUSTIFY, spaceAfter=7))
    ss.add(ParagraphStyle("BodyLeft", fontName="DejaVu", fontSize=10, leading=14.2,
                          textColor=HexColor("#1C2430"), alignment=TA_LEFT, spaceAfter=6))
    ss.add(ParagraphStyle("Caption", fontName="DejaVu", fontSize=8.5, leading=11,
                          textColor=MUTED, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10))
    ss.add(ParagraphStyle("TableCell", fontName="DejaVu", fontSize=8.6, leading=11.5,
                          textColor=HexColor("#1C2430")))
    ss.add(ParagraphStyle("TableHead", fontName="DejaVuBold", fontSize=8.6, leading=11.5,
                          textColor=white))
    ss.add(ParagraphStyle("Footer", fontName="DejaVu", fontSize=7.5, textColor=MUTED))
    ss.add(ParagraphStyle("Decl", fontName="DejaVu", fontSize=10.5, leading=16,
                          alignment=TA_JUSTIFY, textColor=HexColor("#1C2430"), spaceAfter=8))
    ss.add(ParagraphStyle("CodeBlock", fontName="DejaVuMono", fontSize=7.1, leading=9.4,
                          textColor=CODE_FG, backColor=CODE_BG))
    ss.add(ParagraphStyle("CenterSmall", fontName="DejaVu", fontSize=9, leading=12,
                          alignment=TA_CENTER, textColor=MUTED))
    ss.add(ParagraphStyle("BulletBody", fontName="DejaVu", fontSize=10, leading=13.8,
                          textColor=HexColor("#1C2430"), leftIndent=12, spaceAfter=3))
    return ss


def p(text, style):
    return Paragraph(text, style)


def kv_table(rows, col_w=(42 * mm, 118 * mm)):
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
    img = RLImage(str(path), width=width, height=width * Image.open(path).height / Image.open(path).width)
    img.hAlign = "CENTER"
    return img


def code_blocks(text: str, lines_per_chunk: int = 42):
    """Split source so each listing chunk fits on an A4 frame."""
    lines = text.rstrip().splitlines()
    chunks = []
    for i in range(0, len(lines), lines_per_chunk):
        piece = "\n".join(lines[i:i + lines_per_chunk]) + "\n"
        inner = Preformatted(piece, ParagraphStyle(
            "pre", fontName="DejaVuMono", fontSize=6.6, leading=8.6,
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
    canvas.drawString(16 * mm, h - 9.2 * mm, f"{STUDENT_NAME}   |   PRN: {STUDENT_PRN}   |   {COURSE}")
    canvas.drawRightString(w - 16 * mm, h - 9.2 * mm, "Hadoop MapReduce Paradigm")
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 12 * mm, w, 1.1 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("DejaVu", 7.4)
    canvas.drawString(16 * mm, 5 * mm, f"{INSTITUTE}  ·  {AY}")
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
    for line in ["Hadoop MapReduce", "Paradigm"]:
        canvas.drawString(36 * mm, y, line)
        y -= 10 * mm
    canvas.setFont("DejaVu", 11)
    canvas.setFillColor(HexColor("#D7DEEA"))
    canvas.drawString(36 * mm, y - 2 * mm, "Big Data Analytics  —  hands-on MapReduce processing")

    # identity card
    box_y = 78 * mm
    canvas.setFillColor(HexColor("#122744"))
    canvas.roundRect(36 * mm, box_y, w - 58 * mm, 78 * mm, 6, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(36 * mm, box_y + 78 * mm - 3, w - 58 * mm, 3, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("DejaVuBold", 10)
    canvas.drawString(44 * mm, box_y + 64 * mm, "STUDENT DETAILS  (for official submission)")
    canvas.setFont("DejaVu", 9.5)
    info = [
        ("Name", STUDENT_NAME),
        ("PRN", STUDENT_PRN),
        ("Programme", "B.Tech. AIML"),
        ("Course / Paper", COURSE),
        ("Academic Year", AY),
        ("Date of Submission", SUBMISSION_DATE),
        ("Email", EMAIL),
    ]
    yy = box_y + 50 * mm
    for k, v in info:
        canvas.setFillColor(GOLD)
        canvas.setFont("DejaVu", 8)
        canvas.drawString(44 * mm, yy, k.upper())
        canvas.setFillColor(white)
        canvas.setFont("DejaVuBold", 10)
        canvas.drawString(88 * mm, yy, v)
        yy -= 7.2 * mm

    canvas.setFillColor(HexColor("#C5D0E0"))
    canvas.setFont("DejaVu", 8)
    canvas.drawString(36 * mm, 28 * mm, "Apache Hadoop 3.5.0  ·  OpenJDK 21  ·  Local (standalone) MapReduce")
    canvas.drawString(36 * mm, 22 * mm, "Jobs executed: WordCount  |  SalesAnalysis (units by category)")
    canvas.setFillColor(GOLD)
    canvas.setFont("DejaVu", 8)
    canvas.drawString(36 * mm, 14 * mm, "Confidential academic submission  ·  original work of the student named above")
    canvas.restoreState()


def build_pdf(diagrams, shots):
    ss = styles()
    out = OUT_DIR / "Sukhada_Dhingra_BDA_Hadoop_MapReduce_Experiential_Learning.pdf"
    doc = SimpleDocTemplate(
        str(out),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=TITLE,
        author=STUDENT_NAME,
        subject=f"{COURSE} experiential learning report",
    )
    story = []

    # page 1 is cover drawn in onFirstPage; start content after break
    story.append(PageBreak())

    story.append(p("1. Certificate / Declaration", ss["H1"]))
    story.append(p(
        f"I, <b>{STUDENT_NAME}</b>, student of {PROGRAMME} at {INSTITUTE}, "
        f"constituent of {UNIVERSITY}, hereby declare that the work presented in this experiential "
        f"learning report titled “{TITLE}” is my original work carried out as part of the course "
        f"<b>{COURSE}</b> during the academic year {AY}. The MapReduce programs were compiled and "
        f"executed on Apache Hadoop 3.5.0 (standalone / local job runner). Screenshots attached in "
        f"this PDF are captured from that execution and have not been copied from another student.",
        ss["Decl"],
    ))
    story.append(p(
        "I further declare that I have cited standard references (Apache Hadoop documentation, "
        "Dean &amp; Ghemawat MapReduce paper, White’s Hadoop: The Definitive Guide) wherever theory "
        "is summarised, and that no part of this report has been submitted elsewhere for academic credit.",
        ss["Decl"],
    ))
    story.append(Spacer(1, 8 * mm))
    sign = Table(
        [
            [
                Paragraph(f"<b>Student</b><br/>{STUDENT_NAME}<br/>PRN: {STUDENT_PRN}<br/>Date: {SUBMISSION_DATE}<br/>Signature: _______________",
                          ParagraphStyle("s", fontName="DejaVu", fontSize=9, leading=13, textColor=NAVY)),
                Paragraph("<b>Course Faculty</b><br/>Name: _______________________<br/>Designation: ________________<br/>Date: _______________________<br/>Signature: _______________",
                          ParagraphStyle("s2", fontName="DejaVu", fontSize=9, leading=13, textColor=NAVY)),
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
        ("RIGHTPADDING", (0, 0), (0, 0), 10),
    ]))
    story.append(sign)
    story.append(Spacer(1, 6 * mm))

    story.append(p("2. Abstract", ss["H1"]))
    story.append(p(
        "This experiential learning report demonstrates the Hadoop MapReduce programming paradigm "
        "for Big Data Analytics. Two jobs were implemented in Java, compiled against Hadoop 3.5.0, "
        "and executed with the local job runner. The first job is the canonical <b>WordCount</b> "
        "application: mappers emit (word, 1) pairs, a combiner performs local aggregation, and the "
        "reducer produces global frequencies. The second job, <b>SalesAnalysis</b>, aggregates units "
        "sold by product category from a CSV dataset — a typical analytics pattern (GROUP BY + SUM). "
        "The report explains HDFS, YARN and the map–shuffle–reduce pipeline, presents source code, "
        "and attaches screenshots of compilation, job counters, and <font face='DejaVuMono'>part-r-00000</font> output. "
        "On the WordCount corpus the job processed 34 input records, emitted 316 map records, reduced "
        "them (via combiner) to 197 keys, and wrote 197 output records. SalesAnalysis reduced 20 mapped "
        "rows to three category totals: grocery 170, electronics 125, clothing 82.",
        ss["Body"],
    ))

    story.append(p("3. Contents", ss["H1"]))
    toc = [
        ("1", "Certificate / Declaration"),
        ("2", "Abstract"),
        ("3", "Contents"),
        ("4", "Aim, objectives and apparatus"),
        ("5", "Introduction to Big Data and Hadoop"),
        ("6", "HDFS and cluster architecture"),
        ("7", "The MapReduce paradigm"),
        ("8", "WordCount algorithm and dry run"),
        ("9", "Implementation procedure"),
        ("10", "Source code"),
        ("11", "Execution screenshots"),
        ("12", "Results and analysis"),
        ("13", "Observations, viva notes and limitations"),
        ("14", "Conclusion"),
        ("15", "References"),
    ]
    story.append(pretty_table(
        ["§", "Section"],
        toc,
        [18 * mm, 152 * mm],
    ))

    story.append(p("4. Aim, objectives and apparatus", ss["H1"]))
    story.append(p("4.1 Aim", ss["H2"]))
    story.append(p(
        "To study the Hadoop MapReduce paradigm and to implement, compile and execute MapReduce "
        "applications that process text and structured (CSV) data in a local-standalone Hadoop setup, "
        "recording job counters and output files as evidence of experiential learning.",
        ss["Body"],
    ))
    story.append(p("4.2 Objectives", ss["H2"]))
    for item in [
        "Explain why Big Data needs a distributed storage and compute model (volume, velocity, variety).",
        "Describe HDFS (NameNode, DataNodes, blocks, replication) and YARN at a conceptual level.",
        "State the MapReduce contract: map (k1,v1) → list(k2,v2); reduce (k2, list(v2)) → list(k3,v3).",
        "Implement WordCount in Java using Mapper, Combiner and Reducer classes.",
        "Implement a second analytics job (units sold per category) to show GROUP-BY aggregation.",
        "Compile jars with the Hadoop toolchain, submit jobs, and interpret counters and part-r-00000.",
    ]:
        story.append(p(f"•  {item}", ss["BulletBody"]))
    story.append(p("4.3 Apparatus / environment", ss["H2"]))
    story.append(pretty_table(
        ["Item", "Specification used in this work"],
        [
            ["Operating system", "Ubuntu Linux (64-bit)"],
            ["JDK", "OpenJDK 21.0.10"],
            ["Hadoop", "Apache Hadoop 3.5.0 (standalone / LocalJobRunner)"],
            ["Language", "Java (MapReduce new API: org.apache.hadoop.mapreduce)"],
            ["Datasets", "hadoop_intro.txt (text corpus); sales.csv (20 retail rows)"],
            ["Jobs", "WordCount, SalesAnalysis"],
            ["Output", "part-r-00000 + _SUCCESS under each job’s output directory"],
        ],
        [48 * mm, 122 * mm],
    ))
    story.append(p("4.4 Student identity (printed for evaluation)", ss["H2"]))
    story.append(kv_table([
        ("Name", STUDENT_NAME),
        ("PRN", STUDENT_PRN),
        ("Programme", PROGRAMME),
        ("Institute", f"{INSTITUTE}, {UNIVERSITY}"),
        ("Course", COURSE),
        ("Title", TITLE),
        ("Email / phone", f"{EMAIL}  ·  {PHONE}"),
        ("Submission date", SUBMISSION_DATE),
    ]))

    story.append(p("5. Introduction to Big Data and Hadoop", ss["H1"]))
    story.append(p(
        "Big Data refers to data sets whose size, speed or heterogeneity exceeds the comfortable "
        "limits of a single-server relational database. The usual teaching characterisation is the "
        "five V’s: <b>volume</b> (terabytes to petabytes), <b>velocity</b> (continuous ingest), "
        "<b>variety</b> (text, logs, images, CSV), <b>veracity</b> (noise and missing values) and "
        "<b>value</b> (the insight that justifies the cost of processing). Conventional RDBMS designs "
        "scale vertically; Hadoop was designed to scale <i>horizontally</i> on commodity hardware.",
        ss["Body"],
    ))
    story.append(p(
        "Apache Hadoop is an open-source framework inspired by two Google publications: the Google "
        "File System (Ghemawat, Gobioff, Leung, 2003) and MapReduce (Dean &amp; Ghemawat, 2004). "
        "Doug Cutting and Mike Cafarella implemented Hadoop so that large text collections (originally "
        "for the Nutch crawler) could be stored and processed without a specialised supercomputer. "
        "A modern Hadoop deployment has three pillars: <b>HDFS</b> for storage, <b>YARN</b> for "
        "cluster resource management, and processing engines — historically MapReduce, today often "
        "Spark, Hive on Tez, or Flink — that still obey a map / shuffle / reduce mental model.",
        ss["Body"],
    ))
    story.append(shot(diagrams["stack"], 165 * mm))
    story.append(p("Figure 1. Logical Hadoop stack used in this experiential learning module.", ss["Caption"]))
    story.append(p(
        "Experiential learning in this course is not only writing a Mapper class. It is the full "
        "loop: prepare input, compile against Hadoop’s classpath, submit a job, wait for map 100% / "
        "reduce 100%, and read the reducer output. That loop is what industry batch pipelines still "
        "do, whether the engine is MapReduce, Spark or a cloud Dataflow job.",
        ss["Body"],
    ))

    story.append(p("6. HDFS and cluster architecture", ss["H1"]))
    story.append(p(
        "The Hadoop Distributed File System splits files into large blocks (128 MB by default in "
        "recent releases) and stores replicas of each block on different DataNodes. The NameNode "
        "holds the namespace and block map in memory; it does not store file bytes. Clients talk to "
        "the NameNode to learn block locations, then read/write data directly from DataNodes. "
        "Replication (typically 3) gives fault tolerance: if a disk or machine dies, HDFS schedules "
        "re-replication from remaining copies. A Secondary NameNode (or Standby NameNode in HA) "
        "periodically checkpoints metadata so recovery is fast.",
        ss["Body"],
    ))
    story.append(pretty_table(
        ["Component", "Role in Hadoop"],
        [
            ["NameNode", "Master of HDFS: filenames, permissions, block IDs and locations"],
            ["DataNode", "Worker storage: serves block read/write; sends heartbeats"],
            ["ResourceManager", "YARN master: schedules applications onto the cluster"],
            ["NodeManager", "YARN worker: launches containers for map/reduce tasks"],
            ["Job / ApplicationMaster", "Per-job coordinator (MapReduce AM in YARN mode)"],
            ["LocalJobRunner", "Standalone mode used here: one JVM, no HDFS daemons required"],
        ],
        [48 * mm, 122 * mm],
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(p(
        "This assignment was executed in <b>local standalone</b> mode, which is the mode recommended "
        "in the Apache “Single Node Cluster” document for debugging MapReduce programs. Input and "
        "output paths are ordinary Linux directories. The same Java classes can be submitted unchanged "
        "to a pseudo-distributed or fully distributed cluster by pointing them at HDFS URIs "
        "(<font face='DejaVuMono'>hdfs://namenode:9000/input</font>).",
        ss["Body"],
    ))

    story.append(p("7. The MapReduce paradigm", ss["H1"]))
    story.append(p(
        "MapReduce is a <b>divide-and-conquer</b> programming model. The programmer writes two "
        "functions; the framework handles splitting, scheduling, shuffle, fault retry and output commit.",
        ss["Body"],
    ))
    story.append(pretty_table(
        ["Phase", "Input", "Output", "Responsibility"],
        [
            ["Split / RecordReader", "File on disk", "(k1, v1) records", "Framework"],
            ["Map", "(k1, v1)  — e.g. (offset, line)", "list(k2, v2)", "Student code"],
            ["Combiner (optional)", "(k2, list v2) locally", "(k2, v2′) partial", "Often same as Reducer"],
            ["Partition / Shuffle / Sort", "all map outputs", "grouped (k2, list v2)", "Framework"],
            ["Reduce", "(k2, list v2)", "list(k3, v3)", "Student code"],
            ["OutputFormat", "(k3, v3)", "part-r-NNNNN files", "Framework"],
        ],
        [38 * mm, 42 * mm, 40 * mm, 50 * mm],
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(shot(diagrams["flow"], 165 * mm))
    story.append(p("Figure 2. MapReduce pipeline from input splits to part-r-00000.", ss["Caption"]))
    story.append(p(
        "Keys and values are Hadoop Writables (here <font face='DejaVuMono'>Text</font> and "
        "<font face='DejaVuMono'>IntWritable</font>) so they can be serialized across the network. "
        "The shuffle is the expensive phase: map output is spilled, partitioned by hash of the key, "
        "copied to reducers, merged and sorted so that each reduce call receives an iterator of all "
        "values for one key. Combiners shrink map output before the network, which is why WordCount "
        "sets the combiner to the same class as the reducer.",
        ss["Body"],
    ))
    story.append(p(
        "MapReduce is batch-oriented. It is an excellent fit for scanning a large immutable dataset "
        "once (ETL, inverted index, yearly aggregates). Interactive SQL and iterative ML are usually "
        "done in Spark, but those engines still implement the same shuffle grouping idea. Learning "
        "MapReduce therefore transfers directly to later Big Data tools.",
        ss["Body"],
    ))

    story.append(p("8. WordCount algorithm and dry run", ss["H1"]))
    story.append(p(
        "WordCount is the “Hello World” of MapReduce and is specified in Apache’s official MapReduce "
        "tutorial. Each mapper tokenizes a line, lower-cases tokens, strips punctuation, and emits "
        "(word, 1). The reducer sums the ones. A combiner does the same sum on the mapper host so "
        "that a word appearing 50 times in one split travels as (word, 50) rather than fifty pairs.",
        ss["Body"],
    ))
    story.append(shot(diagrams["dryrun"], 160 * mm))
    story.append(p("Figure 3. Tiny dry run of WordCount — the same logic used on the full corpus.", ss["Caption"]))
    story.append(p("8.1 Mapper, combiner, reducer in words", ss["H2"]))
    story.append(pretty_table(
        ["Function", "Logic implemented in this report"],
        [
            ["map(offset, line)", "clean → tokenize → emit (token, 1) for every token"],
            ["combine(word, ones)", "sum the local ones; emit (word, partialSum)"],
            ["reduce(word, counts)", "sum all partial counts; emit (word, total)"],
        ],
        [48 * mm, 122 * mm],
    ))
    story.append(p("8.2 Second job — SalesAnalysis", ss["H2"]))
    story.append(p(
        "To connect MapReduce to analytics (not only token counting), a second job reads "
        "<font face='DejaVuMono'>category,product,units,city</font> CSV. The mapper skips the header, "
        "emits (category, units), and the reducer sums units. This is the MapReduce equivalent of "
        "<font face='DejaVuMono'>SELECT category, SUM(units) FROM sales GROUP BY category</font>. "
        "The combiner again matches the reducer because SUM is associative and commutative.",
        ss["Body"],
    ))

    story.append(PageBreak())
    story.append(p("9. Implementation procedure", ss["H1"]))
    story.append(p(
        "The following steps were executed on the lab machine. Screenshots in §11 correspond one-for-one "
        "to these commands.",
        ss["Body"],
    ))
    steps = [
        "Install OpenJDK 21 and unpack Apache Hadoop 3.5.0. Set JAVA_HOME in hadoop-env.sh.",
        "Verify the toolchain with `java -version` and `hadoop version` (Screenshot 1).",
        "Create a working directory and copy hadoop_intro.txt / sales.csv into input folders (Screenshot 2).",
        "Compile WordCount.java with `hadoop com.sun.tools.javac.Main` and package wordcount.jar (Screenshot 3).",
        "Submit: `hadoop jar wordcount.jar WordCount input_wc output_wc`. Wait until the job reports map 100% reduce 100% and “completed successfully” (Screenshot 4).",
        "List output_wc, confirm _SUCCESS, and inspect part-r-00000. Sort by count for analysis (Screenshot 5).",
        "Compile SalesAnalysis.java, package sales.jar, submit against input_sales (Screenshots 6–7).",
        "Record counters (map input records, combine output records, reduce output records) for the report.",
    ]
    for i, s in enumerate(steps, 1):
        story.append(p(f"<b>Step {i}.</b>  {s}", ss["BulletBody"]))
    story.append(Spacer(1, 3 * mm))
    story.append(p(
        "Important practical rule: the output directory must <b>not</b> already exist. Hadoop refuses "
        "to overwrite it, which prevents accidental destruction of a previous result. Delete or rename "
        "the folder before re-running.",
        ss["Body"],
    ))

    story.append(p("10. Source code", ss["H1"]))
    story.append(p("10.1 WordCount.java", ss["H2"]))
    story.append(p(
        "Student: Sukhada Dhingra  ·  Course: Big Data Analytics  ·  Job: word count with combiner.",
        ss["CenterSmall"],
    ))
    story.extend(code_blocks((SRC / "WordCount.java").read_text()))
    story.append(p("Listing 1. WordCount Mapper, Combiner/Reducer and driver.", ss["Caption"]))
    story.append(p("10.2 SalesAnalysis.java", ss["H2"]))
    story.extend(code_blocks((SRC / "SalesAnalysis.java").read_text()))
    story.append(p("Listing 2. Category-wise SUM of units — MapReduce GROUP BY.", ss["Caption"]))

    story.append(PageBreak())
    story.append(p("11. Execution screenshots", ss["H1"]))
    story.append(p(
        "All screenshots below are generated from the actual Hadoop 3.5.0 run dated 09 September 2026 "
        f"for <b>{STUDENT_NAME}</b> (PRN {STUDENT_PRN}). Job IDs "
        "<font face='DejaVuMono'>job_local1654115753_0001</font> (WordCount) and "
        "<font face='DejaVuMono'>job_local425182150_0001</font> (SalesAnalysis) appear in the logs.",
        ss["Body"],
    ))

    captions = [
        ("version", "Screenshot 1. Java 21 and Hadoop 3.5.0 toolchain verification."),
        ("input", "Screenshot 2. WordCount input file listed and previewed."),
        ("compile", "Screenshot 3. Compilation of Mapper/Reducer classes and packaging of JARs."),
        ("job", "Screenshot 4. WordCount job: splits, map/reduce tasks, counters, SUCCESS."),
        ("wc_out", "Screenshot 5. WordCount output directory, _SUCCESS marker, top tokens from part-r-00000."),
        ("sales_in", "Screenshot 6. Sales CSV used as MapReduce input."),
        ("sales_job", "Screenshot 7. SalesAnalysis completed successfully; category totals in part-r-00000."),
    ]
    for key, cap in captions:
        story.append(KeepTogether([shot(shots[key], 162 * mm), p(cap, ss["Caption"])]))

    story.append(PageBreak())
    story.append(p("12. Results and analysis", ss["H1"]))
    story.append(p("12.1 WordCount counters (from the live job)", ss["H2"]))
    story.append(pretty_table(
        ["Counter", "Value", "Meaning"],
        [
            ["Map input records", "34", "Non-empty lines read from hadoop_intro.txt (plus blanks in the file split)"],
            ["Map output records", "316", "One (word,1) pair per token after cleaning"],
            ["Combine input / output", "316 → 197", "Local aggregation cut shuffle keys to 197"],
            ["Reduce input groups", "197", "Distinct words after shuffle"],
            ["Reduce output records", "197", "One line per word in part-r-00000"],
            ["Bytes read / written", "2076 / 1837", "Input file size vs reducer output size"],
            ["Job status", "completed successfully", "map 100%  ·  reduce 100%"],
        ],
        [48 * mm, 38 * mm, 84 * mm],
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(shot(diagrams["wc_chart"], 155 * mm))
    story.append(p("Figure 4. Highest-frequency tokens. Function words lead, as expected; mapreduce/hadoop/data follow.", ss["Caption"]))
    story.append(p(
        "The combiners reduced 316 mapped pairs to 197 pre-aggregated records before reduce. That is "
        "exactly why WordCount is used to teach combiners: SUM is safe to apply early. Words such as "
        "<i>the</i> (15), <i>and</i> (12), <i>mapreduce</i> (9), <i>data</i> (9) and <i>hadoop</i> (6) "
        "dominate because the corpus is a short technical note about Hadoop itself.",
        ss["Body"],
    ))
    story.append(p("12.2 SalesAnalysis results", ss["H2"]))
    story.append(pretty_table(
        ["Category", "Units (MapReduce SUM)", "Check vs CSV"],
        [
            ["grocery", "170", "40+25+15+19+33+21+17 = 170"],
            ["electronics", "125", "12+30+18+11+27+7+20 = 125"],
            ["clothing", "82", "22+14+9+16+8+13 = 82"],
        ],
        [42 * mm, 55 * mm, 73 * mm],
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(shot(diagrams["sales_chart"], 130 * mm))
    story.append(p("Figure 5. Units sold by category — reducer output plotted for the analytics write-up.", ss["Caption"]))
    story.append(p(
        "Counters confirm the GROUP BY: 21 map input records (header + 20 rows), 20 mapped pairs "
        "(header skipped), combiner output 3, reduce output 3. Grocery is the highest-volume category "
        "in this sample; electronics is next; clothing is lowest. In a production lake the same job "
        "would run on millions of rows with many mappers and still return one record per category.",
        ss["Body"],
    ))

    story.append(p("13. Observations, viva notes and limitations", ss["H1"]))
    story.append(p("13.1 Observations", ss["H2"]))
    for item in [
        "Standalone mode is sufficient to learn Mapper/Reducer APIs; HDFS daemons are not required.",
        "Job output is always a directory: part-r-00000 holds data, _SUCCESS is the commit flag.",
        "Combiners are optional but valuable when the reduce function is associative and commutative.",
        "Re-running a job without deleting the output directory fails — a common viva/lab pitfall.",
        "The same Java source can target HDFS paths later without rewriting business logic.",
        "CSV GROUP BY maps cleanly onto MapReduce; this is how Hive translates SQL under the hood.",
    ]:
        story.append(p(f"•  {item}", ss["BulletBody"]))
    story.append(p("13.2 Likely viva questions (with short answers)", ss["H2"]))
    story.append(pretty_table(
        ["Question", "Model answer"],
        [
            ["Difference between combiner and reducer?",
             "Same class is allowed, but combiners run locally on map output and may not run at all; reducers see all values for a key."],
            ["Why Writable types?",
             "They serialize efficiently for shuffle; Java String/Integer are not the Hadoop RPC types."],
            ["What is shuffle?",
             "Partition, copy, merge and sort of map outputs so each reducer receives grouped keys."],
            ["Default block size?",
             "128 MB in recent Hadoop; large blocks reduce NameNode metadata and favour sequential scans."],
            ["MapReduce vs Spark?",
             "Spark keeps RDDs/DataFrames in memory for iterative jobs; MapReduce writes to disk between stages. Both shuffle."],
            ["Can we overwrite output?",
             "No. FileOutputFormat requires a fresh directory to keep jobs idempotent and auditable."],
        ],
        [55 * mm, 115 * mm],
    ))
    story.append(p("13.3 Limitations of this experiential setup", ss["H2"]))
    story.append(p(
        "The corpus is small by design so that every counter is readable in a lab report. A true "
        "cluster would show multiple input splits, parallel map tasks, and network shuffle. Standalone "
        "mode does not start NameNode/DataNode, so HDFS shell commands (`hadoop fs -put`) were not "
        "required. Fault-injection (killing a mapper) is also out of scope. These are acceptable "
        "limits for a first experiential module; a follow-up lab can move the same jars to "
        "pseudo-distributed HDFS.",
        ss["Body"],
    ))

    story.append(p("14. Conclusion", ss["H1"]))
    story.append(p(
        f"This experiential learning exercise for <b>Big Data Analytics</b> established a working "
        f"understanding of the Hadoop MapReduce paradigm. I, <b>{STUDENT_NAME}</b>, implemented two "
        f"Java jobs, compiled them with Hadoop 3.5.0, and executed them to completion. WordCount "
        f"demonstrated tokenization, combiners and global aggregation (197 distinct words). "
        f"SalesAnalysis demonstrated a practical analytics query — sum of units grouped by category — "
        f"and the reducer totals matched a manual checksum of the CSV. Screenshots of toolchain "
        f"version, compilation, job SUCCESS counters and part-r-00000 files are attached as evidence. "
        f"The same programming model (map, shuffle, reduce) underpins Hive, Pig and Apache Spark, "
        f"which is why MapReduce remains a required experiential topic even as execution engines evolve.",
        ss["Body"],
    ))

    story.append(p("15. References", ss["H1"]))
    refs = [
        "Dean, J. and Ghemawat, S. (2004). MapReduce: Simplified Data Processing on Large Clusters. OSDI.",
        "Ghemawat, S., Gobioff, H. and Leung, S.-T. (2003). The Google File System. SOSP.",
        "Apache Software Foundation (2026). Hadoop 3.5.0 — MapReduce Tutorial and Single Node Cluster documentation. https://hadoop.apache.org/",
        "White, T. Hadoop: The Definitive Guide. O’Reilly Media.",
        "Apache Software Foundation. Hadoop MapReduce Examples (wordcount) in hadoop-mapreduce-examples-3.5.0.jar.",
        "Course notes: Big Data Analytics — Experiential Learning module on the MapReduce paradigm.",
    ]
    for i, r in enumerate(refs, 1):
        story.append(p(f"[{i}]  {r}", ss["BulletBody"]))

    story.append(Spacer(1, 8 * mm))
    story.append(p(
        f"— End of report —<br/>Submitted by <b>{STUDENT_NAME}</b>  ·  PRN {STUDENT_PRN}  ·  {SUBMISSION_DATE}",
        ss["CenterSmall"],
    ))

    def first_page(c, d):
        cover_page(c, d)

    def later(c, d):
        header_footer(c, d)

    doc.build(story, onFirstPage=first_page, onLaterPages=later)
    return out


def main():
    diagrams = make_diagrams()
    shots = make_screenshots()
    pdf = build_pdf(diagrams, shots)
    print(f"PDF written: {pdf}")
    print(f"size_bytes={pdf.stat().st_size}")
    print("screenshots:")
    for k, v in shots.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
