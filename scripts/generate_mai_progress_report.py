#!/usr/bin/env python3
"""B.Tech Project CA-4 monthly progress report (Multimodal AI)."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor, Emu

ROOT = Path(__file__).resolve().parents[1]
OUT_DOCX = ROOT / "documentation" / "BTech_Project_Monthly_Progress_Report_September_2026.docx"
FIG = ROOT / "documentation" / "figures_mai"


def set_run_font(run, name="Times New Roman", size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_page_number(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)
    set_run_font(run, size=10)


def shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def set_cell_border(cell):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tc_pr.append(borders)


def para(doc, text, *, size=12, bold=False, italic=False, align="justify", space_after=6, space_before=0, indent=True):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing = 1.15
    p.alignment = {
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }[align]
    if indent and align == "justify":
        pf.first_line_indent = Cm(0.75)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def center(doc, text, size=12, bold=False, italic=False, space_after=4, space_before=0):
    return para(doc, text, size=size, bold=bold, italic=italic, align="center", space_after=space_after, space_before=space_before, indent=False)


def heading(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(text)
    set_run_font(run, size=13, bold=True)
    return p


def subhead(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(text)
    set_run_font(run, size=12, bold=True)
    return p


def add_table(doc, headers, rows, col_widths=None, header_fill="1F4E79", font=9):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        set_run_font(run, size=font, bold=True, color=RGBColor(255, 255, 255))
        shade_cell(cell, header_fill)
        set_cell_border(cell)
    for r_i, row in enumerate(rows):
        fill = "F2F2F2" if r_i % 2 == 0 else "FFFFFF"
        for c_i, val in enumerate(row):
            cell = table.rows[r_i + 1].cells[c_i]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(str(val))
            set_run_font(run, size=font)
            shade_cell(cell, fill)
            set_cell_border(cell)
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Cm(w)
    return table


def add_picture(doc, path, width_cm=16.2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run()
    run.add_picture(str(path), width=Cm(width_cm))
    return p


def build():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.3)
    section.right_margin = Cm(2.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)

    hp = section.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = hp.add_run("Department of Artificial Intelligence & Machine Learning  |  B.Tech. Project  |  Monthly Progress Report")
    set_run_font(r, size=9, italic=True)

    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run("Multimodal Fusion Framework for Image–Text Fake News Detection  —  Page ")
    set_run_font(r, size=9)
    add_page_number(fp)

    # ---------- COVER ----------
    center(doc, "Project ID: ________", size=12, bold=True, space_after=10, space_before=8)
    center(doc, "B. Tech. Project", size=16, bold=True, space_after=10)
    center(doc, "“Multimodal Fusion Framework for Image–Text Fake News Detection”", size=16, bold=True, space_after=12)
    center(doc, "Monthly Progress Report – September 2026", size=14, bold=True, space_after=8)
    center(doc, "Semester VII  |  B.Tech. (Artificial Intelligence and Machine Learning)", size=12, bold=True, space_after=16)
    center(doc, "Under the Guidance of", size=12, italic=True, space_after=8)
    center(doc, "Dr. Nivedita Mishra", size=14, bold=True, space_after=2)
    center(doc, "(Internal Guide)", size=11, italic=True, space_after=14)

    center(doc, "Group Members", size=13, bold=True, space_before=8, space_after=8)
    add_table(
        doc,
        ["Sr. No.", "Name of the Student", "PRN"],
        [
            ["1", "Sukhada Dhingra", "24070126505"],
            ["2", "Dipti Kothari", "23070126040"],
            ["3", "Khurinji Malar", "23070126059"],
            ["4", "Akhil Chivukula", "26070126009"],
        ],
        col_widths=[2.5, 7.5, 6.0],
        font=11,
    )
    center(doc, "DEPARTMENT OF ARTIFICIAL INTELLIGENCE & MACHINE LEARNING", size=12, bold=True, space_before=18)
    center(doc, "Symbiosis Institute of Technology, Pune", size=12, space_after=4)
    center(doc, "Symbiosis International (Deemed University)", size=12, space_after=4)
    center(doc, "Academic Year 2026–27", size=12, bold=True, space_after=8)

    doc.add_page_break()

    # ---------- TOC ----------
    heading(doc, "TABLE OF CONTENTS")
    add_table(
        doc,
        ["SN", "Particulars", "Page No"],
        [
            ["1", "Names of all the group members and their work distribution", "1"],
            ["2", "Introduction", "2"],
            ["3", "Problem Statement", "3"],
            ["4", "Objectives of the Project", "3"],
            ["5", "Literature Review", "4"],
            ["6", "Gap in the Research / Technology / Methodology", "6"],
            ["7", "Description of the proposed solution", "7"],
            ["8", "Requirement Analysis", "8"],
            ["9", "Technology Stack", "9"],
            ["10", "Design", "10"],
            ["11", "Development / Implementation", "12"],
            ["12", "Testing & Debugging", "13"],
            ["13", "Project plan and progress", "13"],
            ["14", "Project Outcome", "14"],
            ["15", "Conclusion", "15"],
            ["16", "REFERENCES (in APA format)", "16"],
            ["", "APPENDICES — Similarity Report, AI Plagiarism Report", "—"],
        ],
        col_widths=[1.5, 12.5, 2.5],
        font=10,
    )

    heading(doc, "1. NAMES OF ALL THE GROUP MEMBERS AND THEIR WORK DISTRIBUTION")
    para(
        doc,
        "The project has three technical parts: preparing paired image–text data, building unimodal and fusion models, and running the training and evaluation pipeline. System integration, literature reading, documentation, testing and the final presentation will be done by all members together. Each member will still be able to explain the full pipeline during reviews.",
        indent=False,
    )
    add_table(
        doc,
        ["Group Member", "Primary Responsibility", "Major Tasks"],
        [
            [
                "Sukhada Dhingra\nPRN 24070126505",
                "Problem framing, dataset pairing and report",
                "Definition of REAL/FAKE pairing rules (matched, mismatched, sensational); literature table; monthly report; coordination of experiments and figures.",
            ],
            [
                "Dipti Kothari\nPRN 23070126040",
                "Fusion models",
                "Early fusion (concat + MLP), late fusion (average of class probabilities), hybrid fusion (learnable gates + concat); comparison against unimodal baselines.",
            ],
            [
                "Khurinji Malar\nPRN 23070126059",
                "Image modality",
                "CNN image encoder; image preprocessing; class-discriminative visual samples; confusion-matrix and training-curve plots for the vision path.",
            ],
            [
                "Akhil Chivukula\nPRN 26070126009",
                "Text modality and evaluation",
                "BiGRU text encoder; vocabulary and padding; accuracy, precision, recall, F1 and ROC-AUC logging; train/val/test split and debugging of the training loop.",
            ],
        ],
        col_widths=[4.0, 4.2, 8.3],
        font=9,
    )

    heading(doc, "2. INTRODUCTION")
    para(
        doc,
        "A lot of content that people read today is not text alone. A news post on social media almost always has a photograph and a caption together. The photograph may be genuine, but the caption can twist it. The caption may be mild, but the image can be edited. If a detector looks at only one of these, it can be fooled. This is the practical reason for taking up a multimodal problem rather than a text-only classifier.",
    )
    para(
        doc,
        "Multimodal machine learning is the study of models that use more than one type of signal at the same time, for example vision and language (Baltrušaitis et al., 2019). The usual design is to encode each modality, then combine the encodings. Combination can be done early, by joining feature vectors before a classifier, or late, by mixing the decisions of separate models, or in a hybrid way that uses both ideas (Arevalo et al., 2017). For fake news, several papers have already shown that image and text together work better than either one on its own (Jin et al., 2017; Wang et al., 2018; Singhal et al., 2019).",
    )
    para(
        doc,
        "Our group is working on this as the Semester VII B.Tech. project in AIML, under the internal guidance of Dr. Nivedita Mishra. The task is binary: decide whether a post is REAL or FAKE using the image and the caption. REAL samples use a caption that matches the image. FAKE samples use a sensational caption, an image–text mismatch, or both. Five models are compared: image-only CNN, text-only BiGRU, early fusion, late fusion and hybrid fusion.",
    )
    para(
        doc,
        "The motivation is straightforward. Students and later, fact-checkers, need a method that does not ignore the picture when the words look fine, and does not ignore the words when the picture looks fine. We are not claiming a new backbone like CLIP (Radford et al., 2021). We are claiming a fair comparison of fusion choices on a paired dataset that we can train on a laptop CPU in a few hours, with metrics that a reviewer can read.",
    )
    para(
        doc,
        "This September report covers literature, the research gap, the proposed design, requirements, the technology stack, the architecture, the work completed so far (including an initial experiment), testing status, the remaining plan, expected outcomes and APA references. Ten research papers are reviewed in Section 5.",
    )

    heading(doc, "3. PROBLEM STATEMENT")
    para(
        doc,
        "“Multimodal Fusion Framework for Image–Text Fake News Detection”",
        italic=True,
        indent=False,
    )
    para(
        doc,
        "Fake posts on social media often mix a visual claim with a textual claim. A text-only model misses out-of-context photographs. An image-only model misses sensational wording. Existing research describes several fusion methods, but student implementations frequently report only one fusion style and skip unimodal baselines, which makes it hard to say whether fusion actually helped.",
    )
    para(
        doc,
        "This project builds a small, repeatable framework that (i) builds paired image–text samples with known REAL/FAKE labels, (ii) trains unimodal baselines and three fusion models under the same split and training budget, and (iii) reports accuracy, precision, recall, F1 and ROC-AUC. The aim is to check whether early or hybrid fusion reduces errors that unimodal models still make, especially on mismatched image–text pairs.",
    )

    heading(doc, "4. OBJECTIVES OF THE PROJECT")
    para(doc, "1. To prepare a paired image–text dataset in which REAL samples have matched captions and FAKE samples use mismatch and/or sensational wording.", indent=False)
    para(doc, "2. To implement an image-only CNN baseline and a text-only BiGRU baseline for binary REAL/FAKE classification.", indent=False)
    para(doc, "3. To implement early fusion (feature concatenation), late fusion (probability averaging) and hybrid fusion (gated combination) on the same encoders.", indent=False)
    para(doc, "4. To compare all five models using accuracy, precision, recall, F1-score and ROC-AUC on a held-out test split.", indent=False)
    para(doc, "5. To document failure cases (for example mismatch vs sensational text) and to state clearly what the current synthesised data can and cannot say about real social-media streams.", indent=False)
    para(doc, "6. To produce a reproducible training script, figures and this progress report for project evaluation.", indent=False)

    heading(doc, "5. LITERATURE REVIEW")
    para(
        doc,
        "The papers below were selected because they either define multimodal fusion, or they apply image and text to rumour / fake-news detection. Abstracts are not copied. The table records the aim, the method and what we take from each paper.",
        indent=False,
    )
    add_table(
        doc,
        ["Year", "Journal / Conference", "Objective", "Methodology", "Key Contributions"],
        [
            [
                "2019",
                "IEEE TPAMI — Multimodal Machine Learning: A Survey and Taxonomy (Baltrušaitis et al.)",
                "To organise problems that arise when more than one modality is used.",
                "Taxonomy of representation, alignment, translation, fusion and co-learning.",
                "Gives a common language for early vs late fusion and for missing-modality issues. Used as the base reading for this project.",
            ],
            [
                "2017",
                "ACM MM — Multimodal fusion with RNNs for rumour detection on microblogs (Jin et al.)",
                "To detect rumours using tweet text together with attached images.",
                "Attentive RNN over text plus visual features; fusion inside a recurrent model.",
                "Showed that visual evidence changes rumour decisions. Supports our choice of a joint image–text task rather than text only.",
            ],
            [
                "2018",
                "KDD — EANN: Event Adversarial Neural Networks for multi-modal fake news (Wang et al.)",
                "To stop a detector from overfitting to a particular news event.",
                "Text CNN + image CNN with an event discriminator (adversarial).",
                "Warns that high accuracy on one event may not transfer. Our prototype stays on a controlled set first, then plans a shift to a public set such as Fakeddit.",
            ],
            [
                "2019",
                "WWW — MVAE: Multimodal variational autoencoder for fake news (Khattar et al.)",
                "To learn a shared latent space of text and image for fake news.",
                "VAE reconstructs both modalities; classifier on the shared code.",
                "Shared latent fusion is a third family besides concat and score averaging. Hybrid gating in our work is a lighter stand-in for this idea.",
            ],
            [
                "2019",
                "IEEE BigMM — SpotFake: A multi-modal framework for fake news detection (Singhal et al.)",
                "To classify news as fake or real from article text and the lead image.",
                "Pretrained language features fused with a pretrained image network.",
                "A widely cited practical pipeline: separate encoders, then fusion. Close to our early-fusion design, but we train smaller encoders for a CPU budget.",
            ],
            [
                "2020",
                "PAKDD — SAFE: Similarity-aware multi-modal fake news detection (Zhou, Wu & Zafarani)",
                "To use disagreement between image and text as a fake-news clue.",
                "Measures cross-modal similarity and treats low similarity as a risk feature.",
                "Directly motivates our mismatched-pair fake class. Late fusion that only averages scores may miss this; early/hybrid fusion can see both vectors at once.",
            ],
            [
                "2020",
                "ICWSM — Fakeddit: A new multimodal benchmark dataset for fine-grained fake news (Nakamura, Levy & Wang)",
                "To release a large Reddit-based set with text, images and 2/3/6-way labels.",
                "Collects posts, images and metadata; defines coarse and fine fake types.",
                "This is the public dataset we intend to try after the synthesised prototype. It is too heavy for the first CPU runs.",
            ],
            [
                "2021",
                "ICML — CLIP: Learning transferable visual models from natural language supervision (Radford et al.)",
                "To train an image encoder with natural language supervision at scale.",
                "Contrastive matching of image and text batches (400 million pairs).",
                "State of the art for image–text alignment. Too large to fine-tune here. Listed so that the report does not pretend a small CNN/BiGRU is CLIP.",
            ],
            [
                "2017",
                "NIPS workshop / arXiv — Gated multimodal units for information fusion (Arevalo et al.)",
                "To let the model decide how much each modality should contribute.",
                "Learned gates mix modality features before classification.",
                "This is the idea behind our hybrid fusion block. Gates can down-weight a noisy image or a generic caption.",
            ],
            [
                "2017",
                "SIGKDD Explorations — Fake news detection on social media: A data mining perspective (Shu et al.)",
                "To survey why fake news spreads and how it has been detected.",
                "Reviews content, social context and evaluation issues.",
                "Places our work in the content-based family (image + text). We do not model user graphs in this semester.",
            ],
            [
                "2019",
                "arXiv — Supervised multimodal bitransformers for classifying images and text (Kiela et al.)",
                "To classify image–text pairs with a transformer that sees both.",
                "MMBT feeds visual embeddings into a BERT-like backbone.",
                "Shows a stronger (and heavier) alternative to CNN+BiGRU. Kept as future work if GPU time becomes available.",
            ],
            [
                "2011",
                "ICML — Multimodal deep learning (Ngiam et al.)",
                "To learn shared representations across video, audio and other views.",
                "Deep autoencoders trained on more than one modality.",
                "Early evidence that joint hidden layers help when one view is missing or weak. Supports keeping unimodal baselines in the comparison.",
            ],
        ],
        col_widths=[1.4, 3.6, 3.4, 3.6, 4.0],
        font=8,
    )

    heading(doc, "6. GAP IN THE RESEARCH / TECHNOLOGY / METHODOLOGY")
    para(
        doc,
        "The survey of Baltrušaitis et al. (2019) and the fake-news papers of Jin et al. (2017), Wang et al. (2018), Khattar et al. (2019) and Singhal et al. (2019) already show that fusion helps. The remaining gap for a student project is not “nobody has fused image and text”. The gap is that many course projects either (a) report only a single fusion model with no unimodal baseline, or (b) jump to a very large pretrained pair such as CLIP without a small controlled study of early vs late vs hybrid fusion.",
    )
    para(
        doc,
        "A second gap is mismatch. Zhou et al. (2020) argued that image–text disagreement is itself a signal. Public sets such as Fakeddit (Nakamura et al., 2020) contain this phenomenon, but they are large and noisy. We first build a labelled mismatch class on purpose, so that we can see whether fusion actually uses both modalities on that class, before we move to the public set.",
    )
    para(
        doc,
        "A third gap is reporting. Papers quote accuracy, but student reports often skip ROC-AUC and the confusion matrix. Without those, a text-only model that always predicts REAL on mild captions can look “quite good”. Our methodology fixes the split, the epoch budget and the metric list so that the five models are comparable.",
    )
    para(
        doc,
        "The proposed work fills these gaps with a laptop-scale prototype: synthesised but class-controlled image–text pairs, five models, the same evaluation protocol, and a written limit (no user-graph features, no CLIP fine-tuning in this phase).",
    )

    heading(doc, "7. DESCRIPTION OF THE PROPOSED SOLUTION")
    para(
        doc,
        "The system takes one image and one caption. The image goes through a small CNN. The caption is tokenised, padded and passed through a BiGRU. From here five heads are trained.",
        indent=False,
    )
    para(
        doc,
        "Image-only uses the CNN vector. Text-only uses the BiGRU vector. Early fusion concatenates the two vectors and sends them through an MLP. Late fusion trains the two unimodal classifiers and averages their softmax scores at test time. Hybrid fusion learns a gate for each modality, multiplies the gate with the vector, concatenates, and then classifies. All heads predict REAL or FAKE.",
    )
    para(
        doc,
        "The dataset is built so that the label is known. Half the posts are REAL: the caption describes the image. FAKE posts are a mix of (i) a sensational caption on a genuine-looking image, (ii) a caption taken from another class (mismatch), and (iii) both. This follows the similarity idea in SAFE (Zhou et al., 2020) without downloading the full Fakeddit dump in the first month.",
    )
    para(
        doc,
        "Training uses a fixed seed, a 70/15/15 style split, and a small number of epochs so that CPU runs finish in a lab session. Metrics are written to JSON. Plots of training loss, ROC curves and confusion matrices are stored for the report. If fusion is only copying the text model, the confusion matrices will show it. If fusion helps on mismatched fakes, that should appear as fewer FAKE→REAL mistakes than text-only.",
    )

    heading(doc, "8. REQUIREMENT ANALYSIS")
    subhead(doc, "8.1 Functional Requirements")
    add_table(
        doc,
        ["Requirement", "Description"],
        [
            ["Paired input", "The system shall accept one image and one caption as a single sample."],
            ["Labelling", "The system shall support REAL and FAKE labels, including mismatch and sensational fake types during data creation."],
            ["Image encoding", "The system shall compute a visual embedding with a CNN."],
            ["Text encoding", "The system shall compute a textual embedding with a BiGRU."],
            ["Unimodal inference", "The system shall classify using image-only and text-only heads."],
            ["Early fusion", "The system shall concatenate embeddings and classify with an MLP."],
            ["Late fusion", "The system shall average unimodal class probabilities."],
            ["Hybrid fusion", "The system shall apply learned modality gates before concatenation."],
            ["Evaluation", "The system shall report accuracy, precision, recall, F1 and ROC-AUC on a test split."],
            ["Logging", "The system shall save metrics, confusion matrices and training curves."],
        ],
        col_widths=[4.0, 12.5],
        font=10,
    )
    subhead(doc, "8.2 Non-Functional Requirements")
    add_table(
        doc,
        ["Requirement", "Description"],
        [
            ["Reproducibility", "A fixed random seed and documented split ratios shall be used."],
            ["Performance", "A full five-model run should complete on a CPU laptop within a reasonable lab session for the chosen sample size."],
            ["Fair comparison", "All fusion models shall reuse the same encoder sizes and epoch budget as far as the design allows."],
            ["Maintainability", "Dataset, models and training loop shall sit in separate modules."],
            ["Clarity", "Figures must be readable in a printed A4 report."],
            ["Honesty of scope", "Limitations of synthesised images versus real camera photographs shall be stated in the report."],
        ],
        col_widths=[4.0, 12.5],
        font=10,
    )
    subhead(doc, "8.3 Hardware and Software Requirements")
    para(
        doc,
        "Hardware. A normal development laptop is enough. GPU is useful but not mandatory; the September experiment ran on CPU. Disk space is needed for images, model checkpoints and figures. Internet is needed only to install Python packages.",
        indent=False,
    )
    para(
        doc,
        "Software. Python 3.10+, PyTorch, torchvision, NumPy, scikit-learn, Matplotlib, and python-docx for this report. Git and GitHub for version control.",
        indent=False,
    )

    heading(doc, "9. TECHNOLOGY STACK")
    add_table(
        doc,
        ["Tool", "Specific Utilisation"],
        [
            ["Python", "Main language for dataset building, models, training and metric scripts."],
            ["PyTorch", "CNN, BiGRU, fusion layers, loss, optimiser and GPU/CPU device handling."],
            ["torchvision", "Image transforms (resize, tensor conversion) for the visual branch."],
            ["NumPy", "Array handling while creating and splitting the paired samples."],
            ["scikit-learn", "Train/test split helpers, classification report, ROC-AUC."],
            ["Matplotlib", "Training curves, ROC plots, confusion matrices, architecture figures."],
            ["JSON", "Saved experiment results for the report tables."],
            ["Git & GitHub", "Source control and sharing of scripts among the four members."],
        ],
        col_widths=[3.5, 13.0],
        font=10,
    )

    heading(doc, "10. DESIGN")
    subhead(doc, "10.1 System Architecture")
    para(
        doc,
        "Figure 1 shows the two encoders, the three fusion options and the final REAL/FAKE head. Unimodal baselines share the same encoders so that a gain from fusion is not confused with a bigger network.",
        indent=False,
    )
    add_picture(doc, FIG / "architecture.png", 16.0)

    subhead(doc, "10.2 State Diagram")
    para(
        doc,
        "Figure 2 is the process the group follows in a training run. If metrics look unstable, hyperparameters are changed and the unimodal models are trained again before fusion is repeated.",
        indent=False,
    )
    add_picture(doc, FIG / "state_diagram.png", 16.0)

    subhead(doc, "10.3 Fusion Workflow")
    para(doc, "Figure 3 is the sample-level path from a paired post to a logged metric.", indent=False)
    add_picture(doc, FIG / "workflow.png", 16.0)

    subhead(doc, "10.4 Design Summary")
    para(
        doc,
        "The design keeps encoding and fusion separate. Khurinji’s CNN and Akhil’s BiGRU can be tested alone. Dipti’s fusion heads plug in without changing the encoders. Sukhada’s pairing rules control what “FAKE” means, so that mismatch is not an accident in the data. This matches the project objective of a fair comparison rather than a single large black-box model.",
        indent=False,
    )

    heading(doc, "11. DEVELOPMENT / IMPLEMENTATION")
    para(
        doc,
        "Work in September followed the plan: finish the reading, freeze the architecture, and get a first training run on CPU. The code is split into dataset creation, model definitions and a training script.",
        indent=False,
    )
    subhead(doc, "11.1 Literature Study and Problem Analysis")
    para(
        doc,
        "Twelve papers were read (Section 5 and References). The group agreed to stay with CNN + BiGRU + three fusion styles, and to treat CLIP and Fakeddit as later stages rather than month-one deliverables.",
        indent=False,
    )
    subhead(doc, "11.2 Dataset")
    para(
        doc,
        "A paired set of 3000 samples was generated for the first experiment (2100 train, 450 validation, 450 test). Images are class-discriminative RGB pictures from ten object categories. Captions are short news-style lines. Pair types: matched REAL (1500), mismatched FAKE (514), sensational FAKE (498), sensational+mismatch FAKE (488). Vocabulary size in this run was 555 tokens, maximum caption length 32.",
        indent=False,
    )
    subhead(doc, "11.3 Model Implementation")
    para(
        doc,
        "Five models were trained for 6 epochs on CPU: image-only, text-only, early fusion, late fusion and hybrid fusion. Early fusion concatenates embeddings. Late fusion averages unimodal probabilities. Hybrid fusion uses learned gates.",
        indent=False,
    )
    subhead(doc, "11.4 Initial Experimental Numbers")
    para(
        doc,
        "These numbers are from the first controlled run. They are not the final claim of the project. They are recorded here as monthly progress.",
        indent=False,
    )
    add_table(
        doc,
        ["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"],
        [
            ["Image-only CNN", "0.629", "0.614", "0.729", "0.667", "0.708"],
            ["Text-only BiGRU", "0.818", "1.000", "0.642", "0.782", "0.805"],
            ["Early fusion", "0.951", "1.000", "0.904", "0.950", "0.978"],
            ["Late fusion", "0.829", "—", "—", "0.800", "0.887"],
            ["Hybrid fusion", "0.942", "—", "—", "0.940", "0.965"],
        ],
        col_widths=[4.0, 2.5, 2.5, 2.5, 2.5, 2.5],
        font=10,
    )
    para(
        doc,
        "Early fusion was the strongest in this run. Image-only was weak, which is expected when pictures are simple category cues and the fake signal is often in the caption or in the mismatch. Text-only already does well, but recall on FAKE is lower than early fusion. Late fusion sits close to text-only, which suggests that averaging scores does not fully use the joint feature space. Hybrid fusion is close to early fusion. These readings match what the literature said: concat and gated fusion usually beat score averaging on mismatch-style tasks (Arevalo et al., 2017; Zhou et al., 2020).",
        indent=False,
        space_before=8,
    )

    heading(doc, "12. TESTING & DEBUGGING")
    para(
        doc,
        "Formal testing on a public social-media dump has not started. What has been tested is the prototype pipeline: the five models train without crashing, metrics are written to JSON, and confusion matrices / ROC curves can be plotted. Bugs fixed in September included mismatched tensor sizes at the fusion concat layer, a missing “query/passage” style issue that does not apply here, and a seed that was not passed into the split function on an early draft. Next tests: (1) freeze encoders and retrain only fusion, (2) hold out only mismatch fakes and measure recall, (3) replace synthesised images with a Fakeddit subset if disk and time allow.",
        indent=False,
    )

    heading(doc, "13. PROJECT PLAN AND PROGRESS")
    para(
        doc,
        "The plan is for the odd semester of 2026–27. September was research, design and the first CPU experiment. October–November are for cleaner data, extra runs and error analysis. December is for the remaining report, demo and viva.",
        indent=False,
    )
    add_table(
        doc,
        ["Week / period", "Work package", "Status (end of Sep 2026)", "Lead"],
        [
            ["1–2 Sep", "Topic freeze, 10+ papers, problem and objectives", "Done", "Sukhada"],
            ["3 Sep", "Dataset pairing rules and first 3000-sample set", "Done", "Sukhada / Khurinji"],
            ["3–4 Sep", "CNN and BiGRU baselines", "Done (first run)", "Khurinji / Akhil"],
            ["4 Sep", "Early, late, hybrid fusion + metric JSON", "Done (first run)", "Dipti / Akhil"],
            ["Oct W1–W2", "Error analysis on mismatch vs sensational fakes", "Planned", "All"],
            ["Oct W3–W4", "Hyperparameter sweep, extra epochs, seed repeats", "Planned", "Dipti / Akhil"],
            ["Nov W1–W2", "Optional Fakeddit subset or stronger image encoder", "Planned", "Khurinji"],
            ["Nov W3–W4", "Final figures, comparison table, code cleanup", "Planned", "Sukhada / Dipti"],
            ["Dec", "Report update, demo, viva rehearsal", "Planned", "All"],
        ],
        col_widths=[3.0, 6.5, 3.8, 3.2],
        font=9,
    )
    para(
        doc,
        "Current progress is in line with the first phases of the plan. Literature, gap, architecture, requirements, stack and an initial five-model run are complete. Public-data testing and repeated seeds are the next work.",
        indent=False,
        space_before=8,
    )

    heading(doc, "14. PROJECT OUTCOME")
    para(doc, "The planned outcome is a working multimodal prototype and a written comparison of fusion choices.", indent=False)
    para(doc, "• Paired image–text dataset with explicit REAL / mismatch / sensational labels.", indent=False)
    para(doc, "• Image-only, text-only, early, late and hybrid models under one training script.", indent=False)
    para(doc, "• Metric tables and plots (accuracy, F1, ROC-AUC, confusion matrices).", indent=False)
    para(doc, "• A documented finding on which fusion style helped on this data (early fusion led the first run).", indent=False)
    para(doc, "• Source code on GitHub so the experiment can be repeated by the group.", indent=False)

    heading(doc, "15. CONCLUSION")
    para(
        doc,
        "This project studies a multimodal problem: deciding if a post is real or fake when both a picture and a caption are present. The literature is clear that fusion can help, but it is also clear that fusion style and dataset construction matter. Our design puts unimodal baselines next to early, late and hybrid fusion so that any gain can be seen.",
    )
    para(
        doc,
        "The September experiment, run on CPU with 3000 paired samples, showed early fusion ahead of the other heads (about 0.95 accuracy and 0.98 ROC-AUC in that run), with image-only much weaker and late fusion close to text-only. These figures will be checked again with more seeds and, if possible, with a public set. The next months will focus on error analysis and on stating honestly where synthesised images differ from real photographs.",
    )
    para(
        doc,
        "The group of four has a split of work that matches the two modalities and the fusion block. One report is submitted for the group.",
    )

    heading(doc, "16. REFERENCES")
    refs = [
        "Arevalo, J., Solorio, T., Montes-y-Gómez, M., & González, F. A. (2017). Gated multimodal units for information fusion. arXiv:1702.01992.",
        "Baltrušaitis, T., Ahuja, C., & Morency, L.-P. (2019). Multimodal machine learning: A survey and taxonomy. IEEE Transactions on Pattern Analysis and Machine Intelligence, 41(2), 423–443. https://doi.org/10.1109/TPAMI.2018.2798607",
        "Jin, Z., Cao, J., Guo, H., Zhang, Y., & Luo, J. (2017). Multimodal fusion with recurrent neural networks for rumor detection on microblogs. In Proceedings of the 25th ACM International Conference on Multimedia (pp. 795–816). https://doi.org/10.1145/3123266.3123454",
        "Khattar, D., Goud, J. S., Gupta, M., & Varma, V. (2019). MVAE: Multimodal variational autoencoder for fake news detection. In The World Wide Web Conference (pp. 2915–2921). https://doi.org/10.1145/3308558.3313552",
        "Kiela, D., Bhooshan, S., Firooz, H., Perez, E., & Testuggine, D. (2019). Supervised multimodal bitransformers for classifying images and text. arXiv:1909.02950.",
        "Nakamura, K., Levy, S., & Wang, W. Y. (2020). Fakeddit: A new multimodal benchmark dataset for fine-grained fake news detection. In Proceedings of the 12th Language Resources and Evaluation Conference (pp. 6149–6157).",
        "Ngiam, J., Khosla, A., Kim, M., Nam, J., Lee, H., & Ng, A. Y. (2011). Multimodal deep learning. In Proceedings of the 28th International Conference on Machine Learning (pp. 689–696).",
        "Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Askell, A., Mishkin, P., Clark, J., Krueger, G., & Sutskever, I. (2021). Learning transferable visual models from natural language supervision. In Proceedings of the 38th International Conference on Machine Learning (pp. 8748–8763).",
        "Shu, K., Sliva, A., Wang, S., Tang, J., & Liu, H. (2017). Fake news detection on social media: A data mining perspective. ACM SIGKDD Explorations Newsletter, 19(1), 22–36. https://doi.org/10.1145/3137597.3137600",
        "Singhal, S., Shah, R. R., Chakraborty, T., Kumaraguru, P., & Satoh, S. (2019). SpotFake: A multi-modal framework for fake news detection. In 2019 IEEE Fifth International Conference on Multimedia Big Data (BigMM) (pp. 39–47). https://doi.org/10.1109/BigMM.2019.00-44",
        "Wang, Y., Ma, F., Jin, Z., Yuan, Y., Xun, G., Jha, K., Su, L., & Gao, J. (2018). EANN: Event adversarial neural networks for multi-modal fake news detection. In Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (pp. 849–857). https://doi.org/10.1145/3219819.3219903",
        "Zhou, X., Wu, J., & Zafarani, R. (2020). SAFE: Similarity-aware multi-modal fake news detection. In Pacific-Asia Conference on Knowledge Discovery and Data Mining (pp. 354–367). https://doi.org/10.1007/978-3-030-47426-3_28",
    ]
    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-1.0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(f"{i}. {ref}")
        set_run_font(run, size=11)

    heading(doc, "APPENDICES")
    para(
        doc,
        "Similarity Report and AI Plagiarism Report are to be attached after the Turnitin (or institute) scan of this file. They are not generated inside this document.",
        indent=False,
    )
    para(doc, "Declaration. We, the members listed on the cover page, state that this monthly progress report is the work of our group. Sources are listed in APA in Section 16. One copy is submitted for the group.", indent=False, space_before=8)
    para(doc, "Date: _______________     Place: Pune", indent=False, space_before=10)
    para(doc, "Sukhada Dhingra (24070126505) _____________     Dipti Kothari (23070126040) _____________", indent=False)
    para(doc, "Khurinji Malar (23070126059) _____________     Akhil Chivukula (26070126009) _____________", indent=False)

    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT_DOCX)
    print(f"Wrote {OUT_DOCX}")


if __name__ == "__main__":
    build()
