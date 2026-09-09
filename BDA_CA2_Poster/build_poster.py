#!/usr/bin/env python3
"""Fill the official BDA CA2 poster template with completed project content."""
import os

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Pt, Emu

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "Template-BDA_CA2_poster.pptx")
OUTPUT = os.path.join(HERE, "BDA_CA2_Poster_Sukhada_Dhingra_24070126505.pptx")
RESULTS_IMG = os.path.join(HERE, "assets", "results_panel.png")

TITLE = "Real-Time Credit Card Fraud Detection using Apache Spark Streaming"

ABSTRACT = [
    "Credit-card networks produce high-velocity, highly imbalanced transaction streams that batch analytics cannot score in time to block fraud.",
    "This project builds an Apache Spark Structured Streaming and MLlib pipeline on the ULB Credit Card Fraud dataset (284,807 transactions; only 0.172% fraud).",
    "A class-weighted Random Forest flags suspicious payments in 2-second micro-batches with AUC-ROC 0.968 and F1-score 0.84, enabling near real-time bank alerts.",
]

OBJECTIVES = [
    "Ingest and clean large-scale, imbalanced card-transaction data using Apache Spark.",
    "Engineer amount, time and PCA-based features that capture rare fraud patterns.",
    "Train and compare Logistic Regression, Random Forest and GBT models in Spark MLlib.",
    "Deploy a Structured Streaming scorer with micro-batch latency under two seconds.",
]

METHODOLOGY = [
    "Dataset: ULB/Kaggle Credit Card Fraud (Sept 2013; 31 features — Time, Amount, V1–V28 PCA components).",
    "ETL: Spark DataFrame load, null handling, StandardScaler, 70:30 stratified split and class-weighting for the 0.172% fraud rate.",
    "Models: Spark MLlib Logistic Regression, Random Forest (100 trees) and Gradient-Boosted Trees, evaluated with Precision, Recall, F1 and AUC-ROC.",
    "Streaming: Structured Streaming (2 s micro-batches) applies the fitted pipeline and emits fraud probability plus an alert to a monitoring dashboard.",
    "Stack: Apache Spark 3.5, PySpark, Spark MLlib and Python 3.11 on a local cluster-style workflow.",
]

REFERENCES = [
    "Dal Pozzolo, A., et al. (2015). IEEE SSCI.    Carcillo, F., et al. (2018). Information Fusion, 41, 182–194.",
    "Apache Software Foundation. (2024). Spark MLlib guide.  https://spark.apache.org/docs/latest/ml-guide.html",
]


def iter_shapes(shapes):
    for shape in shapes:
        yield shape
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from iter_shapes(shape.shapes)


def set_run_font(run, name, size_pt, bold=False, underline=False, color=None):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = False
    rPr = run._r.get_or_add_rPr()
    if underline:
        rPr.set("u", "sng")
    elif rPr.get("u") is not None:
        del rPr["u"]
    # latin/ea typeface
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rPr, qn(tag))
        el.set("typeface", name)
    if color is not None:
        run.font.color.rgb = color


def _remove_bullet_nodes(pPr):
    for child in list(pPr):
        tag = child.tag
        if tag in (
            qn("a:buFont"),
            qn("a:buChar"),
            qn("a:buNone"),
            qn("a:buAutoNum"),
            qn("a:buBlip"),
            qn("a:buClr"),
            qn("a:buSzPts"),
            qn("a:buSzPct"),
        ):
            pPr.remove(child)


def apply_bullet(paragraph, enabled=True, mar_l=142875, indent=-114300):
    pPr = paragraph._p.get_or_add_pPr()
    _remove_bullet_nodes(pPr)
    if not enabled:
        etree.SubElement(pPr, qn("a:buNone"))
        if "marL" in pPr.attrib:
            del pPr.attrib["marL"]
        if "indent" in pPr.attrib:
            del pPr.attrib["indent"]
        return
    pPr.set("marL", str(mar_l))
    pPr.set("indent", str(indent))
    bu_font = etree.SubElement(pPr, qn("a:buFont"))
    bu_font.set("typeface", "Wingdings")
    bu_font.set("pitchFamily", "2")
    bu_font.set("charset", "2")
    bu_char = etree.SubElement(pPr, qn("a:buChar"))
    bu_char.set("char", "l")  # filled round bullet in Wingdings


def write_paragraphs(shape, items, font="Verdana", size=10, bold=False, align=PP_ALIGN.JUSTIFY, bullets=True):
    tf = shape.text_frame
    tf.word_wrap = True
    # drop extra paragraphs from XML
    sp = shape._element
    tx_body = sp.find(qn("p:txBody"))
    p_els = tx_body.findall(qn("a:p"))
    first_p = p_els[0]
    for extra in p_els[1:]:
        tx_body.remove(extra)
    # clear runs in first paragraph
    for child in list(first_p):
        if child.tag != qn("a:pPr"):
            first_p.remove(child)

    def fill_p(p_el, text):
        # reuse existing pPr if present
        pPr = p_el.find(qn("a:pPr"))
        if pPr is None:
            pPr = etree.SubElement(p_el, qn("a:pPr"))
        if align == PP_ALIGN.JUSTIFY:
            pPr.set("algn", "just")
        elif align == PP_ALIGN.LEFT:
            pPr.set("algn", "l")
        elif align == PP_ALIGN.CENTER:
            pPr.set("algn", "ctr")
        r = etree.SubElement(p_el, qn("a:r"))
        rPr = etree.SubElement(r, qn("a:rPr"))
        rPr.set("lang", "en-US")
        rPr.set("sz", str(int(size * 100)))
        rPr.set("dirty", "0")
        if bold:
            rPr.set("b", "1")
        latin = etree.SubElement(rPr, qn("a:latin"))
        latin.set("typeface", font)
        ea = etree.SubElement(rPr, qn("a:ea"))
        ea.set("typeface", font)
        t = etree.SubElement(r, qn("a:t"))
        t.text = text

    fill_p(first_p, items[0])
    # python-pptx paragraph wrapper for bullet helper
    from pptx.text.text import _Paragraph

    p0 = shape.text_frame.paragraphs[0]
    apply_bullet(p0, enabled=bullets)
    p0.space_before = Pt(0)
    p0.space_after = Pt(3 if bullets else 1)

    for text in items[1:]:
        p = shape.text_frame.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = text
        set_run_font(run, font, size, bold=bold)
        apply_bullet(p, enabled=bullets)
        p.space_before = Pt(1)
        p.space_after = Pt(3 if bullets else 1)


def set_single_line(shape, text, font="Verdana", size=15, bold=True, align=None):
    tf = shape.text_frame
    p = tf.paragraphs[0]
    # clear extra paragraphs
    sp = shape._element
    tx_body = sp.find(qn("p:txBody"))
    p_els = tx_body.findall(qn("a:p"))
    for extra in p_els[1:]:
        tx_body.remove(extra)
    for child in list(p_els[0]):
        if child.tag != qn("a:pPr"):
            p_els[0].remove(child)
    run = p.add_run()
    run.text = text
    set_run_font(run, font, size, bold=bold, underline=True)
    if align is not None:
        p.alignment = align


def write_student_box(shape):
    tf = shape.text_frame
    sp = shape._element
    tx_body = sp.find(qn("p:txBody"))
    p_els = tx_body.findall(qn("a:p"))
    for extra in p_els[1:]:
        tx_body.remove(extra)
    for child in list(p_els[0]):
        if child.tag != qn("a:pPr"):
            p_els[0].remove(child)

    def add_line(first, parts, space_before=0):
        if first:
            p = shape.text_frame.paragraphs[0]
        else:
            p = shape.text_frame.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_before = Pt(space_before)
        p.space_after = Pt(2)
        apply_bullet(p, enabled=False)
        for text, bold, underline, size in parts:
            run = p.add_run()
            run.text = text
            set_run_font(run, "Calibri", size, bold=bold, underline=underline)

    add_line(
        True,
        [
            ("Student Name (PRN):  ", True, True, 11),
            ("Sukhada Dhingra  (24070126505)", False, False, 11),
        ],
    )
    add_line(
        False,
        [
            ("Programme:  ", True, False, 11),
            ("B.Tech — Artificial Intelligence and Machine Learning  |  AY 2026–27", False, False, 11),
        ],
        space_before=4,
    )
    add_line(
        False,
        [
            ("Subject Teacher:  ", True, True, 11),
            ("Dr. Archana Choudary", False, False, 11),
        ],
        space_before=4,
    )


def main():
    prs = Presentation(TEMPLATE)
    slide = prs.slides[0]
    by_id = {s.shape_id: s for s in iter_shapes(slide.shapes)}

    set_single_line(by_id[86], TITLE, font="Verdana", size=14, bold=True)

    write_paragraphs(by_id[93], ABSTRACT, font="Verdana", size=10, bullets=True)
    write_paragraphs(by_id[10], OBJECTIVES, font="Verdana", size=10, bullets=True)
    write_paragraphs(by_id[17], METHODOLOGY, font="Verdana", size=9.5, bullets=True)

    write_student_box(by_id[85])

    # Place results composite inside the screenshot/results frame (slight inset so the border remains).
    results = by_id[6]
    inset = Emu(70000)  # ~0.077"
    slide.shapes.add_picture(
        RESULTS_IMG,
        results.left + inset,
        results.top + inset,
        results.width - 2 * inset,
        results.height - 2 * inset,
    )

    # Overlay APA citations in a slide-level box (grouped template frame clips overflow).
    ref_box = slide.shapes.add_textbox(
        Emu(6080000),
        Emu(5200000),  # below "References: (APA Style)"
        Emu(5980000),
        Emu(320000),   # stay inside the template references frame
    )
    tf = ref_box.text_frame
    tf.word_wrap = True
    body_pr = ref_box._element.find(qn("p:txBody")).find(qn("a:bodyPr"))
    if body_pr is not None:
        body_pr.set("anchor", "t")
        body_pr.set("wrap", "square")
        body_pr.set("lIns", "36000")
        body_pr.set("tIns", "8000")
        body_pr.set("rIns", "20000")
        body_pr.set("bIns", "8000")
    for i, text in enumerate(REFERENCES):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_before = Pt(0)
        p.space_after = Pt(0)
        apply_bullet(p, enabled=False)
        run = p.add_run()
        run.text = text
        set_run_font(run, "Calibri", 8, bold=False, color=RGBColor(0x00, 0x00, 0x00))

    prs.save(OUTPUT)
    print("Wrote", OUTPUT)


if __name__ == "__main__":
    main()
