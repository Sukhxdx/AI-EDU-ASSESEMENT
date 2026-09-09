#!/usr/bin/env python3
"""Build the EMBER-Net multimodal AI technical report PDF."""

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "EMBER_Net_Multimodal_AI_Wildfire_Report.pdf"

NAVY = HexColor("#1B365D")
EMBER = HexColor("#C45C26")
TEAL = HexColor("#1D6A7A")
GREEN = HexColor("#2D6A4F")
SLATE = HexColor("#3D4A5C")
INK = HexColor("#1A1A1A")
MUTED = HexColor("#5A6573")
RULE = HexColor("#D8D2C8")
BAND = HexColor("#F6F1E8")
PALE = HexColor("#EEF4F6")

pdfmetrics.registerFont(TTFont("Inter", "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Med", "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Semi", "/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Bold", "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif", "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic", "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Serif-BI", "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"))


def styles():
    s = {}
    s["cover_kicker"] = ParagraphStyle(
        "cover_kicker",
        fontName="Inter-Semi",
        fontSize=9,
        leading=12,
        textColor=EMBER,
        alignment=TA_CENTER,
        tracking=1.4,
        spaceAfter=8,
    )
    s["cover_title"] = ParagraphStyle(
        "cover_title",
        fontName="Inter-Bold",
        fontSize=22,
        leading=27,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=8,
    )
    s["cover_sub"] = ParagraphStyle(
        "cover_sub",
        fontName="Serif-Italic",
        fontSize=12.5,
        leading=17,
        textColor=SLATE,
        alignment=TA_CENTER,
        spaceAfter=14,
    )
    s["cover_meta"] = ParagraphStyle(
        "cover_meta",
        fontName="Inter",
        fontSize=9.5,
        leading=14,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
    s["abstract_h"] = ParagraphStyle(
        "abstract_h",
        fontName="Inter-Bold",
        fontSize=10,
        leading=13,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceBefore=4,
        spaceAfter=6,
    )
    s["abstract"] = ParagraphStyle(
        "abstract",
        fontName="Serif",
        fontSize=10,
        leading=14.2,
        textColor=INK,
        alignment=TA_JUSTIFY,
    )
    s["h1"] = ParagraphStyle(
        "h1",
        fontName="Inter-Bold",
        fontSize=13.5,
        leading=17,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=8,
    )
    s["h2"] = ParagraphStyle(
        "h2",
        fontName="Inter-Semi",
        fontSize=11.5,
        leading=15,
        textColor=TEAL,
        spaceBefore=10,
        spaceAfter=5,
    )
    s["h3"] = ParagraphStyle(
        "h3",
        fontName="Inter-Semi",
        fontSize=10.5,
        leading=14,
        textColor=EMBER,
        spaceBefore=8,
        spaceAfter=4,
    )
    s["body"] = ParagraphStyle(
        "body",
        fontName="Serif",
        fontSize=10.5,
        leading=15.2,
        textColor=INK,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )
    s["bullet"] = ParagraphStyle(
        "bullet",
        fontName="Serif",
        fontSize=10.5,
        leading=14.6,
        textColor=INK,
        leftIndent=12,
        spaceAfter=3,
    )
    s["caption"] = ParagraphStyle(
        "caption",
        fontName="Inter",
        fontSize=8.6,
        leading=11.5,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=12,
    )
    s["toc_item"] = ParagraphStyle(
        "toc_item",
        fontName="Serif",
        fontSize=11,
        leading=18,
        textColor=INK,
    )
    s["ref"] = ParagraphStyle(
        "ref",
        fontName="Serif",
        fontSize=9.5,
        leading=13.2,
        textColor=INK,
        leftIndent=14,
        firstLineIndent=-14,
        spaceAfter=6,
    )
    s["table_cell"] = ParagraphStyle(
        "table_cell",
        fontName="Serif",
        fontSize=8.7,
        leading=11.6,
        textColor=INK,
    )
    s["table_head"] = ParagraphStyle(
        "table_head",
        fontName="Inter-Semi",
        fontSize=8.4,
        leading=11,
        textColor=white,
    )
    s["step_title"] = ParagraphStyle(
        "step_title",
        fontName="Inter-Semi",
        fontSize=10.4,
        leading=13.5,
        textColor=NAVY,
        spaceBefore=6,
        spaceAfter=2,
    )
    s["footer"] = ParagraphStyle(
        "footer",
        fontName="Inter",
        fontSize=8,
        textColor=MUTED,
    )
    s["quote"] = ParagraphStyle(
        "quote",
        fontName="Serif-Italic",
        fontSize=10.5,
        leading=15,
        textColor=SLATE,
        alignment=TA_LEFT,
        leftIndent=10,
        rightIndent=10,
        spaceBefore=4,
        spaceAfter=10,
    )
    return s


S = styles()


def P(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    flow = []
    for item in items:
        flow.append(Paragraph(f"•  {item}", S["bullet"]))
    flow.append(Spacer(1, 4))
    return flow


def figure(path, caption, width=172 * mm):
    from PIL import Image as PILImage

    with PILImage.open(path) as im:
        w, h = im.size
    img = Image(str(path), width=width, height=width * (h / float(w)))
    return KeepTogether([img, Paragraph(caption, S["caption"])])


def draw_cover(canvas, doc):
    canvas.saveState()
    W, H = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(EMBER)
    canvas.rect(0, H - 10 * mm, W, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#16304F"))
    canvas.rect(0, 0, W, 22 * mm, fill=1, stroke=0)
    card_x, card_y = 12 * mm, 28 * mm
    card_w, card_h = W - 24 * mm, H - 46 * mm
    canvas.setFillColor(white)
    canvas.roundRect(card_x, card_y, card_w, card_h, 7, fill=1, stroke=0)
    canvas.setFillColor(EMBER)
    canvas.rect(card_x, card_y + card_h - 3.6, card_w, 3.6, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#C9D3DE"))
    canvas.setFont("Inter", 8.2)
    canvas.drawCentredString(W / 2, 11 * mm, "Multimodal Artificial Intelligence  ·  Technical Report  ·  September 2026")
    canvas.restoreState()


def draw_inner(canvas, doc):
    canvas.saveState()
    W, H = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, H - 12 * mm, W, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(EMBER)
    canvas.rect(0, H - 13.4 * mm, W, 1.4 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Inter", 8)
    canvas.drawString(16 * mm, H - 8.2 * mm, "EMBER-Net  ·  Multimodal AI for Early Wildfire Detection")
    canvas.drawRightString(W - 16 * mm, H - 8.2 * mm, "Technical Report")
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.4)
    canvas.line(16 * mm, 12.5 * mm, W - 16 * mm, 12.5 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Inter", 8)
    canvas.drawString(16 * mm, 7.2 * mm, "Combining text, image, audio, and video")
    canvas.drawRightString(W - 16 * mm, 7.2 * mm, f"{doc.page}")
    canvas.restoreState()


def modality_table():
    head = [
        P("Modality", "table_head"),
        P("Typical sources", "table_head"),
        P("What the model extracts", "table_head"),
        P("Why it is needed", "table_head"),
    ]
    rows_raw = [
        [
            "Image (still)",
            "Satellite IR/RGB, drone stills, lookout photos, thermal frames",
            "Smoke plumes, flame, hot spots, land cover, infrastructure",
            "Wide-area detection, including places with no cameras or 911 coverage",
        ],
        [
            "Video",
            "PTZ 360° towers, UAV live streams, time-lapse columns",
            "Smoke growth over minutes, wind drift, fire-front motion",
            "Separates static clouds/fog from a developing ignition",
        ],
        [
            "Audio",
            "IoT mics, 911 voice, firefighter radio",
            "Crackle/roar, wind, sirens; spoken locations via ASR",
            "Works at night and in smoke; captures human reports in real time",
        ],
        [
            "Text",
            "Weather bulletins, 911 transcripts, social posts, GIS/fuel maps",
            "Place names, red-flag conditions, eyewitness claims, asset lists",
            "Adds context, coordinates, and intent that pixels alone cannot provide",
        ],
    ]
    data = [head]
    for row in rows_raw:
        data.append([P(c, "table_cell") for c in row])
    col_w = [28 * mm, 46 * mm, 48 * mm, 48 * mm]
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("BACKGROUND", (0, 1), (-1, 1), HexColor("#E8F3F5")),
                ("BACKGROUND", (0, 2), (-1, 2), HexColor("#F8F1F5")),
                ("BACKGROUND", (0, 3), (-1, 3), HexColor("#F8F3E8")),
                ("BACKGROUND", (0, 4), (-1, 4), HexColor("#EAF4EE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.35, RULE),
            ]
        )
    )
    return t


def io_table():
    head = [
        P("Interface", "table_head"),
        P("Examples", "table_head"),
        P("Format / consumer", "table_head"),
    ]
    rows = [
        [
            "Inputs",
            "Geotagged IR tiles; 1-minute panoramic video; microphone spectrograms; 911 transcripts; NWS red-flag text; fuel-model rasters",
            "Streams and batches into a feature store, keyed by time and lat/lon",
        ],
        [
            "Internal state",
            "Per-cell ignition probability, fused embedding, missing-modality mask, analyst decision",
            "Time-series store + vector index for similar past events",
        ],
        [
            "Outputs",
            "Alert packet (GPS, p, images); CAD recommendation; live map; public warning copy",
            "JSON/GeoJSON to dispatch; map tiles to command; SMS/app to the public",
        ],
    ]
    data = [head] + [[P(c, "table_cell") for c in r] for r in rows]
    t = Table(data, colWidths=[32 * mm, 78 * mm, 60 * mm], repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.35, RULE),
                ("BACKGROUND", (0, 1), (-1, 1), HexColor("#F7F8F4")),
                ("BACKGROUND", (0, 2), (-1, 2), white),
                ("BACKGROUND", (0, 3), (-1, 3), HexColor("#F7F8F4")),
            ]
        )
    )
    return t


def adv_table():
    head = [P("Advantages of the multimodal design", "table_head"), P("Limitations and risks", "table_head")]
    left = (
        "<b>Complementary coverage.</b> Satellites see remote terrain; towers see valleys; 911 and social posts capture human eyes; audio works when smoke hides flame.<br/><br/>"
        "<b>Fewer missed starts.</b> A faint smoke column plus a rising IR hotspot plus a 911 phrase such as “smoke on the ridge” is more reliable than any cue alone.<br/><br/>"
        "<b>Fewer naive false alarms.</b> Video temporal models reject stationary clouds; text context rejects industrial steam when weather is humid and no red-flag warning is in force.<br/><br/>"
        "<b>Actionable output.</b> Hybrid fusion yields not only a score but a location, a narrative, and a resource suggestion that dispatchers can use in minutes.<br/><br/>"
        "<b>Graceful degradation.</b> Missing-modality masking lets the system keep running if a tower, satellite pass, or social feed drops."
    )
    right = (
        "<b>False positives still occur.</b> Dust, fog, agricultural burns, and industrial stacks can mimic smoke. Human review remains necessary for high-impact alerts.<br/><br/>"
        "<b>Uneven sensor maps.</b> Rural and low-income regions often have fewer towers and weaker connectivity, which can bias detection toward well-instrumented areas.<br/><br/>"
        "<b>Latency and cost.</b> Video transformers and satellite downlinks are expensive. Edge models help, but cloud fusion still needs bandwidth.<br/><br/>"
        "<b>Label scarcity.</b> True early ignitions are rare, so models overfit to large, obvious plumes unless synthetic and hard-negative mining are used.<br/><br/>"
        "<b>Social-media noise and privacy.</b> Unverified posts can smear location. Voice and social data require strict minimization, consent, and retention limits."
    )
    data = [head, [P(left, "table_cell"), P(right, "table_cell")]]
    t = Table(data, colWidths=[85 * mm, 85 * mm], repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), GREEN),
                ("BACKGROUND", (1, 0), (1, 0), EMBER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("BOX", (0, 0), (-1, -1), 0.4, RULE),
                ("LINEBEFORE", (1, 0), (1, -1), 0.4, RULE),
                ("BACKGROUND", (0, 1), (0, 1), HexColor("#F3F8F4")),
                ("BACKGROUND", (1, 1), (1, 1), HexColor("#FBF4EE")),
            ]
        )
    )
    return t


def build_story():
    story = [NextPageTemplate("inner")]

    story += [
        Spacer(1, 12 * mm),
        P("TECHNICAL REPORT  ·  MULTIMODAL ARTIFICIAL INTELLIGENCE", "cover_kicker"),
        P("EMBER-Net: A Hybrid Multimodal AI System for Early Wildfire Detection and Emergency Response", "cover_title"),
        P(
            "How text, image, audio, and video can be combined so fires are found while they are still small enough to stop.",
            "cover_sub",
        ),
        HRFlowable(width="40%", thickness=1.2, color=EMBER, spaceBefore=2, spaceAfter=12, hAlign="CENTER"),
        P("Prepared as a design report on a real-world multimodal AI problem<br/>September 2026", "cover_meta"),
        Spacer(1, 8 * mm),
        P("Abstract", "abstract_h"),
        P(
            "Wildfires now regularly outrun 911-based discovery. By the time a plume is obvious to a passer-by, the fire may already be too large for a rapid initial attack. "
            "This report proposes <b>EMBER-Net</b> (Early Multimodal Bushfire and wildfire Emergency Recognition Network), a hybrid-fusion system that jointly reasons over "
            "<b>satellite and camera images</b>, <b>tower and UAV video</b>, <b>acoustic and 911 audio</b>, and <b>weather, GIS, and eyewitness text</b>. "
            "Unimodal encoders produce embeddings; co-located sensors are fused early; heterogeneous feeds are aligned with cross-attention; and agency-level scores are combined late, with a human analyst in the loop. "
            "The intended outputs are a calibrated ignition probability, triangulated coordinates, a short incident narrative, and a dispatch recommendation. "
            "The design is grounded in operating systems already used by fire agencies, including Pano AI camera networks, California’s ALERTCalifornia program with CAL FIRE, and Google Research’s FireSat constellation.",
            "abstract",
        ),
        Spacer(1, 6 * mm),
        P(
            "<b>Chosen problem:</b> early wildfire detection and emergency response<br/>"
            "<b>Modalities:</b> text, image, audio, video<br/>"
            "<b>Fusion method:</b> hybrid (early + cross-attention + late)<br/>"
            "<b>Primary real-world reference:</b> Pano AI, ALERTCalifornia / CAL FIRE, and FireSat",
            "cover_meta",
        ),
        PageBreak(),
        P("Contents", "h1"),
    ]

    toc = [
        "1.  Problem statement",
        "2.  Proposed multimodal AI solution",
        "3.  Modalities used (text, image, audio, video)",
        "4.  Input and output of the system",
        "5.  Multimodal processing workflow and architecture",
        "6.  Representation and fusion method (early / late / hybrid)",
        "7.  How the system works, step by step",
        "8.  Advantages and limitations",
        "9.  Real-world example and references",
        "10. Conclusion",
        "References",
    ]
    for item in toc:
        story.append(P(item, "toc_item"))

    # 1
    story += [
        P("1.  Problem statement", "h1"),
        P(
            "Wildfire is no longer a seasonal nuisance at the wildland–urban interface; it is a year-round public-safety, insurance, and climate problem. "
            "In 2024, wildfires burned on the order of a billion acres globally [1]. In the western United States, Canada, southern Europe, and Australia, fires now routinely "
            "make long-range runs on red-flag days, destroying homes, collapsing power grids, and filling cities with hazardous smoke. The operational bottleneck is not only suppression capacity. "
            "It is <b>time to awareness</b>: the minutes between ignition and the moment a fire agency knows, with enough confidence and location precision, that a start is real.",
        ),
        P(
            "Today’s discovery process is still dominated by 911 calls, lookouts, and coarse satellite products. Those channels fail in characteristic ways. A fire that starts on a remote ridge "
            "may burn for tens of minutes before anyone calls. Thermal satellites such as those feeding NASA FIRMS are invaluable, but legacy public products often cannot resolve a start until it is "
            "already the size of a sports field, and many sensors refresh only a few times per day [2][3]. Ground cameras without temporal reasoning confuse clouds, dust, and steam with smoke. "
            "Social media is fast but spatially noisy. Audio sensors and 911 speech contain gold—place names, “I smell smoke,” radio traffic—but they are rarely fused with what the cameras see.",
        ),
        P(
            "The result is a <b>multimodal evidence problem</b>, not a single-sensor computer-vision problem. No one modality is simultaneously wide-area, high-resolution, 24-hour, privacy-safe, and cheap. "
            "Images give spatial proof. Video gives change. Audio gives night-time and human-report cues. Text gives weather, place names, and intent. Combining them poorly (for example, OR-ing independent alarms) "
            "floods dispatch with false positives. Combining them well can surface the small starts that agencies actually want: the ones that can still be hit with a helicopter, an engine, or a hand crew "
            "before they become campaign fires.",
        ),
        P(
            "The design goal of this report is therefore concrete: <b>detect ignitions while they are still small, locate them well enough to dispatch, explain the evidence in language a duty officer trusts, "
            "and do so with fewer false alarms than any unimodal detector.</b> CAL FIRE has stated that roughly half of the fires seen on its AI-enabled camera network are detected before the first 911 call, "
            "and that this head start supports the department’s aim of keeping 95 percent of fires at 10 acres or less [4]. That is the performance regime EMBER-Net is built to serve.",
        ),
        # 2
        P("2.  Proposed multimodal AI solution", "h1"),
        P(
            "<b>EMBER-Net</b> is a proposed end-to-end system for agencies, utilities, and land managers. It is not a chatbot that “talks about fire.” It is a <b>perception-and-decision stack</b> that "
            "ingests live multimodal streams, maintains a geospatial risk field, and emits incident objects that can be dropped into computer-aided dispatch (CAD) and incident-command maps.",
        ),
        P("2.1&nbsp; Design principles", "h2"),
    ]
    story += bullets(
        [
            "<b>Detect early, not dramatically.</b> The valuable event is a five-metre start in dry grass, not a towering pyrocumulus that everyone can already see.",
            "<b>Every alert must be geospatial.</b> A smoke probability without coordinates is not an operational product. Towers triangulate; satellites georeference; text is geoparsed.",
            "<b>Humans remain in the loop for high-impact actions.</b> Models propose; trained analysts or duty officers confirm before a multi-resource dispatch, matching current Pano AI and ALERTCalifornia practice [1][5].",
            "<b>Degrade gracefully.</b> Night, cloud, a downed tower, or a missing satellite pass must reduce confidence—not crash the pipeline.",
            "<b>Optimize for minutes, not research leaderboards.</b> Edge models run on towers; heavier fusion runs in the cloud; the budget is wall-clock time to a usable alert.",
        ]
    )
    story += [
        P("2.2&nbsp; What EMBER-Net actually is", "h2"),
        P(
            "At a high level the system has five layers, shown in Figure 1 and detailed in Section 5: (1) sensing and ingestion, (2) unimodal encoders, (3) hybrid fusion, "
            "(4) reasoning and decision, and (5) outputs to agencies and the public. The novel claim is not that cameras or satellites can see smoke—that is already proven in the field. "
            "The claim is that <b>hybrid fusion of four modalities</b>, with explicit handling of missing and delayed data, produces a more calibrated incident object than vision-only smoke detectors.",
        ),
        P(
            "EMBER-Net is intended to sit beside existing tools rather than replace them. NASA FIRMS and national weather services remain inputs. CAD, radio, and incident-command software remain outputs. "
            "The AI layer is the glue: it watches more pixels and waveforms than a tired human can, then writes a short, sourced brief a human can accept or reject in under a minute.",
        ),
        # 3
        P("3.  Modalities used (text, image, audio, video)", "h1"),
        P(
            "Multimodal learning, in the sense surveyed by Baltrušaitis, Ahuja, and Morency, is the construction of models that can process and relate information from multiple heterogeneous sources [6]. "
            "EMBER-Net uses all four classical human-facing modalities. Each is represented differently, arrives on a different clock, and fails in a different weather regime. That diversity is the point.",
        ),
        Spacer(1, 2 * mm),
        modality_table(),
        Paragraph("Table 1. Modalities in EMBER-Net, their sources, extracted signals, and operational role.", S["caption"]),
        P("3.1&nbsp; Image", "h2"),
        P(
            "Still imagery is the backbone of wide-area detection. Multispectral satellite frames (especially short-wave and mid-wave infrared) reveal heat that RGB cameras miss at night or through thin smoke. "
            "Google Research’s FireSat program is designed so that, once a full constellation is on orbit, fires as small as about 5 × 5 metres can be revisited on the order of every 20 minutes, using AI that compares "
            "the current tile with a long history of the same location plus local weather [2][3]. EMBER-Net treats those tiles as an image stream: a vision transformer (or a CNN backbone with a temporal difference head) "
            "emits a heat/smoke embedding and a coarse geobox. Drone stills and lookout photographs fill gaps between satellite revisits. Representation is a 768–1024-dimensional patch embedding plus EXIF/geocode metadata.",
        ),
        P("3.2&nbsp; Video", "h2"),
        P(
            "Video is not “many images.” The signal of interest is <b>change</b>: a column that thickens, leans with the wind, or detaches from a ridgeline. Pano AI stations rotate high-resolution cameras to build "
            "a 360-degree panorama on a roughly one-minute cadence, with optical zoom and infrared for night [1][7]. ALERTCalifornia’s pan-tilt-zoom network performs 360-degree sweeps on a similar cadence and can view tens of miles [5]. "
            "EMBER-Net encodes short clips with a video transformer (for example TimeSformer or a VideoMAE-style encoder) so that motion features can veto cloud-like blobs that do not evolve. "
            "When two towers see the same plume, triangulation produces GPS coordinates—the same idea Pano AI patents as a core product feature [1].",
        ),
        P("3.3&nbsp; Audio", "h2"),
        P(
            "Audio is the most underused wildfire modality and the one that makes the system truly multimodal rather than “cameras plus metadata.” Two audio families matter. "
            "<b>Environmental audio</b> from low-power IoT microphones (and, in some deployments, from cameras that already have mics) can pick up crackle, roar, and abrupt wind shifts in canyons where line of sight is blocked. "
            "These waveforms are converted to log-mel spectrograms and encoded with an audio spectrogram transformer. "
            "<b>Speech audio</b> from 911 and tactical radio is passed through automatic speech recognition (ASR). The transcript then becomes text, but the raw audio still carries urgency, overlap, and background sirens "
            "that a transcript discards. Audio is especially valuable at night, in heavy smoke, and in the first seconds of a 911 call before an address is typed into CAD.",
        ),
        P("3.4&nbsp; Text", "h2"),
        P(
            "Text is both a sensor and a control surface. Weather and red-flag products from national meteorological services set a prior: the same faint plume is more suspicious on a 4 percent live-fuel-moisture day than after a soaking rain. "
            "GIS layers (fuel models, power lines, hospitals, campgrounds) are serialized as text plus rasters so a language model can name what is at risk. "
            "Eyewitness posts and 911 transcripts are geoparsed with named-entity recognition. A large language model is used <b>after</b> fusion, not as the detector: it writes the incident narrative and cites which camera, satellite tile, "
            "and weather product support the claim. That separation keeps the LLM from hallucinating a fire that the perception stack did not see.",
        ),
        # 4
        P("4.  Input and output of the system", "h1"),
        P(
            "A multimodal system is easiest to evaluate if inputs and outputs are specified as contracts, not as slogans. Figure 3 summarizes the interface; Table 2 lists the payloads.",
        ),
        figure(HERE / "figure3_io.png", "Figure 3. EMBER-Net inputs (left) and operational outputs (right)."),
        io_table(),
        Paragraph("Table 2. Input, internal state, and output contracts.", S["caption"]),
        P("4.1&nbsp; Inputs in operational terms", "h2"),
        P(
            "Each incoming record carries a time stamp, a spatial key (lat/lon, camera ID, or satellite tile ID), a modality tag, and a reliability prior (for example, a calibrated camera is trusted more than an anonymous social post). "
            "Image and video frames are stored as object-store blobs; audio as short clips plus spectrogram features; text as UTF-8 with language and source. "
            "The ingestion layer is deliberately asynchronous. A satellite pass may arrive 12 minutes after a tower clip. Fusion therefore happens on a sliding geospatial window, not on a single synchronized frame.",
        ),
        P("4.2&nbsp; Outputs in operational terms", "h2"),
        P(
            "The primary output is an <b>incident object</b>: identifier, first-seen time, fused probability with a confidence interval, point or polygon geometry, contributing sensors, two or three evidence thumbnails, "
            "a 120-word narrative, and a recommended initial response (for example “Type 3 helicopter + nearest engine; access via Forest Road 18; power line 400 m east”). "
            "Secondary outputs are a live map for incident command, a public-safe pin that does not reveal camera exploits, and a structured log for after-action review. "
            "Outputs are versioned so that as video continues, the perimeter and probability can update without creating duplicate incidents.",
        ),
        P(
            "What the system must <b>not</b> output is equally important: raw 911 audio to the public, unredacted social handles, or an automatic evacuation order. Those remain human and legal decisions. "
            "EMBER-Net can draft warning copy; it does not press the siren.",
        ),
        # 5
        P("5.  Multimodal processing workflow and architecture", "h1"),
        P(
            "Figure 1 is the reference architecture. Data rise through five layers. The important architectural choice is that fusion is not a single concatenate-and-classify block. "
            "It is a set of fusion operators chosen according to how tightly the sensors are coupled in space and time.",
        ),
        figure(HERE / "figure1_architecture.png", "Figure 1. EMBER-Net multimodal processing workflow and system architecture."),
        P("5.1&nbsp; Layer 1 — Sensing and ingestion", "h2"),
        P(
            "Physical sources include satellite IR/RGB, tower PTZ cameras, UAV video, IoT acoustic nodes, 911/radio/social text, and weather/GIS layers. "
            "A common geospatial index (typically a hierarchical grid such as H3) lets a smoke embedding from camera A meet a hot pixel from satellite tile B and a 911 phrase geocoded to the same cell. "
            "Quality-control drops corrupted frames, saturated mics, and bots. Edge devices can run a tiny smoke proposal network so that only suspicious clips are backhauled—essential on fire-season bandwidth.",
        ),
        P("5.2&nbsp; Layer 2 — Unimodal encoders", "h2"),
        P(
            "Each modality has a specialist encoder trained or adapted on wildfire data: a vision transformer or CNN for stills; a video transformer for clips; an audio spectrogram transformer plus ASR for sound; "
            "and a text encoder (and later an LLM) for language. Encoders are frozen or lightly fine-tuned so that a new camera vendor does not require retraining the entire stack. "
            "Outputs are embeddings of a shared dimension (for example 768) plus unimodal logits used later by late fusion. Normalization and temperature scaling are applied per encoder so that “0.7” from the video model "
            "means something comparable to “0.7” from the text model.",
        ),
        P("5.3&nbsp; Layer 3 — Hybrid fusion", "h2"),
        P(
            "This is the heart of the system and is specified in Section 6. Co-located RGB, infrared, and microphone features from one tower are fused early. "
            "Video, satellite, and text that describe the same cell but are not pixel-aligned are fused with cross-attention. Independent agency-level scores (including third-party FIRMS alerts) are fused late. "
            "A gated combiner applies reliability weights and a missing-modality mask, then optionally holds the incident for human review.",
        ),
        P("5.4&nbsp; Layer 4 — Reasoning and decision", "h2"),
        P(
            "Fusion produces a probability, not a plan. A reasoning module then (a) triangulates or geocodes a location, (b) grows a first-guess fire-front using wind and fuel, "
            "(c) scores assets at risk, and (d) places the event on an analyst queue ordered by probability × value-at-risk × time-since-ignition. "
            "This is where GIS stops being decoration and becomes part of the model’s loss: a 0.4-probability start next to a hospital on a red-flag day outranks a 0.8-probability agricultural burn in a known permit zone.",
        ),
        P("5.5&nbsp; Layer 5 — Outputs", "h2"),
        P(
            "Confirmed or high-confidence events are pushed to CAD, to a common operating picture, and—when policy allows—to public maps. "
            "The architecture keeps a bidirectional link: analysts can reject an alert, which becomes a hard negative for later training, exactly as 24/7 intelligence-center review does in commercial systems [1][7].",
        ),
        # 6
        P("6.  Representation and fusion method used (early / late / hybrid)", "h1"),
        P(
            "In multimodal machine learning, <b>early (feature-level) fusion</b> concatenates or jointly encodes raw or low-level features before classification. "
            "<b>Late (decision-level) fusion</b> trains unimodal models independently and combines their scores. "
            "<b>Hybrid fusion</b> uses both, often with an intermediate joint representation such as cross-modal attention [6]. "
            "EMBER-Net chooses <b>hybrid fusion</b> because wildfire data violate the assumptions of either pure strategy. Figure 2 compares the three options and marks the chosen path.",
        ),
        figure(HERE / "figure2_fusion.png", "Figure 2. Early, late, and hybrid fusion. EMBER-Net uses hybrid fusion."),
        P("6.1&nbsp; Why not early fusion alone?", "h2"),
        P(
            "Early fusion is excellent when sensors share a clock and a mounting bracket. A dual RGB–infrared camera with a co-located microphone is one physical event: concatenate the three feature maps, "
            "let a small MLP or a joint transformer see that a lukewarm IR blob coincides with a faint RGB stain and a crackle, and classify. "
            "That trick fails for social-media text that arrives minutes later, for a satellite that last imaged the cell 18 minutes ago, and for a tower that is offline. "
            "Forcing those sources into one fat vector either imputes fiction or drops the sample.",
        ),
        P("6.2&nbsp; Why not late fusion alone?", "h2"),
        P(
            "Late fusion is robust: if the satellite is missing, the camera model still votes. It is also how many agencies already think—independent “smoke alarm” products OR-ed together. "
            "The cost is lost cross-modal signal. A video model may assign 0.45 to a wispy column (below threshold). A satellite model may assign 0.45 to a barely warm pixel. "
            "Separately they are ignored; together they are an ignition. Late fusion cannot recover that unless the unimodal models are unusually well calibrated and the meta-classifier sees their joint score distribution, "
            "which starts to recreate intermediate fusion anyway.",
        ),
        P("6.3&nbsp; The hybrid recipe used by EMBER-Net", "h2"),
        P(
            "Representation is <b>joint embeddings plus unimodal logits</b>. Each encoder maps its input to a shared space. Three operators then run:",
        ),
    ]
    story += bullets(
        [
            "<b>Early fusion</b> inside a station: RGB, IR, and optional audio features from the same timestamp and pose are concatenated (or passed through a tiny joint encoder) to produce a station embedding.",
            "<b>Cross-attention fusion</b> across stations and satellites: satellite patch tokens query camera tokens and text tokens (weather + geoparsed 911) for the same H3 cell and a ±30-minute window. "
            "This is intermediate / hybrid representation fusion: modalities remain distinct sequences, but they attend to one another.",
            "<b>Late fusion</b> at the incident level: station scores, satellite scores, text-only rumor scores, and third-party alerts enter a calibrated logistic or gradient-boosted meta-classifier, with a missingness indicator for each source.",
            "<b>Human gate</b> as a final late-fusion voter with very high weight for any dispatch that moves aircraft or triggers public warning.",
        ]
    )
    story += [
        P(
            "Reliability weights are not uniform. A triangulating pair of calibrated cameras outranks a single tweet. A FireSat-class IR detection on a red-flag day outranks a daytime RGB false look-alike. "
            "Weights are estimated on held-out seasons and can be overridden by policy (for example, never auto-alert from social text alone). "
            "This is still hybrid fusion: the representation is mixed, and the decision is mixed, by design.",
        ),
        P("6.4&nbsp; Training objective", "h2"),
        P(
            "The primary loss is binary (or ordinal) ignition detection at the cell–time level, with focal loss to handle rarity. Auxiliary losses include localization (distance to true start), "
            "temporal earliness (reward detections that precede 911), and narrative faithfulness (the LLM must not mention a sensor that was not in the evidence set). "
            "Hard negatives—clouds, dust, prescribed burns, steam—are oversampled. Analyst rejects from production are recycled weekly. "
            "That closed loop is how fielded systems such as Pano AI report improving models across successive fire seasons [7].",
        ),
        # 7
        P("7.  How the system works, step by step", "h1"),
        P(
            "The following walk-through is the intended runtime path for a single ignition on a red-flag afternoon. It is written as an operational sequence, not as marketing.",
        ),
        P("Step 1 — Continuously watch", "step_title"),
        P(
            "Towers pan. Satellites downlink. IoT mics buffer 10-second windows. Weather feeds refresh. Nothing “starts” the AI; the encoders are already running at the edge on a low-power smoke proposal model. "
            "Most minutes produce no candidate. That is success: the system is quiet until the world is not.",
        ),
        P("Step 2 — Raise a unimodal proposal", "step_title"),
        P(
            "Suppose tower 14’s RGB model scores 0.41 on a pale stain above a canyon—below a naive 0.5 threshold. Simultaneously the IR head scores 0.36 on a slightly warm pixel. "
            "The video transformer, looking at four successive panoramas, sees the stain lengthen and drift with the forecast wind. Its temporal score is 0.62. "
            "Early fusion inside the station lifts the joint station score to 0.71. A candidate incident is opened in cell H3-r8.",
        ),
        P("Step 3 — Pull neighboring modalities", "step_title"),
        P(
            "The fusion worker queries the same cell and neighbors for ±30 minutes. A satellite tile from 11 minutes earlier is still cool; a new tile is due in 9 minutes. "
            "Weather text says red-flag, 8 percent humidity, 35 km/h gusts. GIS text notes a transmission corridor 600 metres east. "
            "No 911 yet. Social text is empty. Missing-modality masks are set for speech and social, not treated as zeros that “vote no.”",
        ),
        P("Step 4 — Cross-attend and locate", "step_title"),
        P(
            "Cross-attention lets the video tokens query weather tokens (wind direction should match plume lean) and GIS tokens (is this a known mill steam stack?). "
            "It is not. A second tower, 12 km west, is tasked to zoom. When it acquires the plume, triangulation yields a point with a few-hundred-metre error ellipse—good enough for a helicopter.",
        ),
        P("Step 5 — Reason about risk, not just smoke", "step_title"),
        P(
            "The spread module advects the point with wind and fuel. In 40 minutes the ellipse intersects the transmission corridor. Value-at-risk jumps. "
            "The incident is promoted on the analyst queue even though the burned area is still tiny. This is the difference between a detector and a decision system.",
        ),
        P("Step 6 — Human confirmation", "step_title"),
        P(
            "An analyst sees the zoomed frames, the IR chip, the wind overlay, and a two-sentence draft: “Probable vegetation start, canyon west of Forest Road 18; plume growing over 4 minutes; no 911; red-flag in force.” "
            "The analyst accepts (or rejects as a dust devil). Accepting writes the incident object to CAD. This step is optional only for low-stakes logging; it is mandatory for aircraft and public warning.",
        ),
        P("Step 7 — Dispatch and keep watching", "step_title"),
        P(
            "CAD receives GPS, photos, and a recommended helitack plus engine. As the helicopter lifts, EMBER-Net continues: new video updates the perimeter; the next satellite tile confirms heat; "
            "the first 911 call arrives and is attached as corroboration rather than as a new duplicate incident. If the fire is killed at a tenth of an acre, the event becomes a positive training example of "
            "<i>early</i> detection—the class that vision-only models trained on disaster footage never see.",
        ),
        P("Step 8 — After-action and learning", "step_title"),
        P(
            "Containment time, final acreage, and whether 911 preceded or followed the AI alert are stored. False alarms are labeled by type (cloud, steam, prescribed fire). "
            "Weights on social text, night IR, and particular towers are recalibrated. The loop is the product.",
        ),
        # 8
        P("8.  Advantages and limitations", "h1"),
        P(
            "A multimodal proposal that does not admit failure modes is not an engineering document. Table 3 sets advantages against limitations that would appear in a real procurement or ethics review.",
        ),
        CondPageBreak(125 * mm),
        KeepTogether(
            [
                adv_table(),
                Paragraph(
                    "Table 3. Advantages of hybrid multimodal detection versus limitations that remain after fusion.",
                    S["caption"],
                ),
            ]
        ),
        P("8.1&nbsp; Advantages, expanded", "h2"),
        P(
            "The central advantage is <b>complementary physics</b>. Optical video fails in cloud and at night; infrared and audio do not. Satellites fail under thick overcast and between revisits; towers do not. "
            "Towers fail in canyons and behind ridges; UAV and 911 speech can fill those shadows. Text weather priors stop the model from treating every humid-day cloud as a start. "
            "Hybrid fusion is what lets those complementarities show up in the score instead of in a slide deck. A second advantage is <b>operational fit</b>: the outputs are the artifacts fire agencies already use "
            "(a location, a picture, a recommended resource), which is why camera-AI programs in California are already trusted enough to start resource movement before 911 [4].",
        ),
        P("8.2&nbsp; Limitations, expanded", "h2"),
        P(
            "Fusion does not repeal the base-rate problem. Ignitions are rare; look-alikes are common. Without aggressive hard-negative mining and human review, precision collapses and duty officers ignore the tool. "
            "Coverage is political as well as technical: a county that cannot afford towers will not magically be saved by a paper architecture. "
            "Audio and social text create privacy and civil-liberty exposure; EMBER-Net therefore treats those streams as minimized, purpose-limited, and default-off for public products. "
            "Finally, climate non-stationarity means last year’s smoke statistics are not next year’s. Models must be retrained across seasons and geographies or they will silently drift.",
        ),
        P("8.3&nbsp; Ethical and safety constraints", "h2"),
        P(
            "The system must not be used to surveil people as a side effect of watching landscapes. Face blurring, short retention of speech, and prohibition on using the network for immigration or protest monitoring "
            "are design requirements, not footnotes. Evacuation messaging must be authorized by officials. Automated shutoff of electrical feeders, where utilities use similar intelligence, requires a separate safety case. "
            "These constraints are part of the architecture because a high-recall wildfire model that becomes a general-purpose camera grid has failed, even if its F1 score is excellent.",
        ),
        # 9
        P("9.  Real-world example and reference", "h1"),
        P(
            "EMBER-Net is a proposed architecture, but it is not speculative science fiction. Three fielded programs already implement large pieces of it. Together they are the reference implementation this report builds on.",
        ),
        P("9.1&nbsp; Primary example: Pano AI (cameras + IR + satellite + weather + human review)", "h2"),
        P(
            "Pano AI, founded in 2020 and based in San Francisco, deploys ultra-high-definition rotating cameras on high vantage points and runs cloud AI for day and night smoke and heat detection. "
            "Detections are reviewed by analysts in a 24/7 intelligence center before customers are alerted. The product fuses camera video with third-party satellite, emergency-service, GIS, and weather feeds, "
            "and it triangulates GPS coordinates of incidents [1][7]. MIT Technology Review named Pano AI among its 2024 climate-tech companies to watch, noting infrared night capability and continued "
            "situational awareness (zoomable video, satellite, weather) after ignition [8]. By mid-2025 the company reported covering nearly 30 million acres across the United States, Canada, and Australia, "
            "with contracted revenue over $100 million after a $44 million Series B [1].",
        ),
        P(
            "A concrete incident illustrates why multimodal, located, early detection matters. On a June 2024 red-flag day, Pano AI reported being the sole source of early smoke detection on a start, "
            "providing triangulated coordinates within minutes and enabling a helitack response. A 40-person ground crew would have hiked more than two hours; aerial response helped hold the fire to about three acres [1]. "
            "That is the EMBER-Net value function in one anecdote: minutes and coordinates, not a viral image of a catastrophe.",
        ),
        P("9.2&nbsp; Public-sector camera AI: ALERTCalifornia and CAL FIRE", "h2"),
        P(
            "ALERTCalifornia, associated with the University of California San Diego, operates a statewide natural-hazard camera network used heavily for fire. Cameras pan, tilt, and zoom through 360-degree sweeps "
            "roughly every two minutes, with near-infrared night capability and views of tens of miles [5]. In partnership with CAL FIRE and Digital Path, an AI tool flags likely ignitions with a confidence score and estimated location; "
            "trained watchstanders confirm before resources move [5]. CAL FIRE leadership has said the cameras detect fires before 911 about 50 percent of the time, citing an example near Fresno detected about 20 minutes "
            "before the first emergency call, and has stated that the department trusts the detections enough to begin sending resources when they arrive [4]. "
            "EMBER-Net’s human gate, CAD output, and emphasis on incipient-phase suppression are taken directly from this operating model.",
        ),
        P("9.3&nbsp; Space-based multimodal AI: FireSat (Google Research, Muon Space, Earth Fire Alliance)", "h2"),
        P(
            "Camera networks cannot cover oceans of fuel. FireSat is a purpose-built wildfire satellite constellation. A prototype launched in March 2025 on SpaceX Transporter-13 from Vandenberg; "
            "the design goal for the full constellation is detection of ~5 × 5 metre fires with updates every 20 minutes or less, using custom multispectral infrared sensors and AI that compares a location "
            "with a long history of itself plus weather and infrastructure context [2][3]. Google.org helped fund the first satellite; Muon Space builds and operates the spacecraft for the nonprofit Earth Fire Alliance [2]. "
            "This is image-plus-text (weather, context) fusion at planetary scale, and it is the satellite branch of EMBER-Net’s encoder layer. "
            "Until the constellation is dense, EMBER-Net still ingests coarser public products such as NASA FIRMS so that the late-fusion path is never empty [9].",
        ),
        P("9.4&nbsp; What the reference systems do not yet fully do—and where this proposal adds value", "h2"),
        P(
            "Fielded products are strongest on <b>image and video</b>, with weather and GIS as supporting layers. They are weaker, as a published architecture, on <b>environmental audio</b>, "
            "<b>911/radio speech as a first-class encoder</b>, and a explicitly documented <b>hybrid early/cross-attention/late</b> fusion policy with missing-modality math. "
            "EMBER-Net’s contribution is to treat those as equal citizens: a crackle in a canyon, a 911 fragment without a street address, and a sub-threshold IR pixel should be allowed to reinforce one another "
            "instead of waiting for a pretty RGB plume. The real-world systems prove that agencies will use AI alerts. This report specifies how to combine the remaining modalities without pretending that concatenation is a strategy.",
        ),
        # 10
        P("10.  Conclusion", "h1"),
        P(
            "Early wildfire detection is a multimodal problem because the physical event is multimodal. Heat is infrared. Smoke motion is video. Night and occluded terrain are partly acoustic. "
            "Place, weather, and human witness are language. A model that sees only pictures will be late or noisy; a model that reads only 911 will be blind in empty country; a model that ORs every feed will cry wolf.",
        ),
        P(
            "EMBER-Net answers that with a hybrid architecture: unimodal encoders for image, video, audio, and text; early fusion where sensors share a mast; cross-attention where they share only a map cell and a time window; "
            "late fusion where they share only an incident ID; and a human gate where the cost of a mistake is an aircraft or an evacuation. "
            "Inputs are geotagged streams. Outputs are incident objects that dispatchers already know how to use. "
            "The design is deliberately conservative relative to research fashion: it copies the human-in-the-loop discipline of Pano AI and ALERTCalifornia, and it treats FireSat-class satellites as a coming encoder, not as a completed substitute for ground truth.",
        ),
        P(
            "If the system works, the public will not see it. The fires that matter will be the ones that never make the evening news because they died at two acres on a ridgeline, after a camera, a satellite, a microphone, "
            "and a sentence of weather text agreed that something had started—and a person still made the call to go.",
        ),
        P("References", "h1"),
        P(
            "[1] Pano AI. “Wildfire Tech Comes of Age: Pano AI Raises $44M Series B…” GlobeNewswire, 16 June 2025. Company product description: https://www.pano.ai/solution",
            "ref",
        ),
        P(
            "[2] Google Research. “FireSat.” https://sites.research.google/gr/wildfires/firesat/ ; Google. “How Google Research and partners built FireSat…,” 17 March 2025. https://blog.google/innovation-and-ai/products/inside-firesat-launch-muon-space/",
            "ref",
        ),
        P(
            "[3] The Verge. “Satellite launch kicks off a new effort to monitor wildfires from space” (FireSat prototype on Transporter-13, Vandenberg, March 2025).",
            "ref",
        ),
        P(
            "[4] PBS NewsHour. “How satellites and AI cameras are detecting wildfires before they get out of control.” Interview with CAL FIRE and Pano AI on pre-911 detections and FireSat.",
            "ref",
        ),
        P(
            "[5] ALERTCalifornia. “Research & Technology.” https://alertcalifornia.org/technology/ (PTZ camera network, near-IR night vision, CAL FIRE / Digital Path AI detection, watchstander confirmation).",
            "ref",
        ),
        P(
            "[6] Baltrušaitis, T., Ahuja, C., and Morency, L.-P. “Multimodal Machine Learning: A Survey and Taxonomy.” IEEE Transactions on Pattern Analysis and Machine Intelligence, 41(2), 2019, pp. 423–443.",
            "ref",
        ),
        P(
            "[7] GovTech. “AI: A Wildland Firefighter’s New Best Friend?” Interview with Pano AI CEO Sonia Kastner on deep-learning smoke detection, 24/7 analyst review, and multi-season model improvement.",
            "ref",
        ),
        P(
            "[8] MIT Technology Review. “2024 Climate Tech Companies to Watch: Pano AI and its fire-detecting AI,” 1 October 2024. https://www.technologyreview.com/2024/10/01/1104375/2024-climate-tech-companies-pano-ai-fire-detecting-ai/",
            "ref",
        ),
        P(
            "[9] NASA FIRMS (Fire Information for Resource Management System). https://firms.modaps.eosdis.nasa.gov/ — public satellite hotspots used as a late-fusion input when high-resolution constellations are unavailable.",
            "ref",
        ),
        Spacer(1, 8 * mm),
        HRFlowable(width="100%", thickness=0.6, color=RULE, spaceBefore=4, spaceAfter=8),
        P(
            "Document control: EMBER-Net multimodal AI design report · September 2026 · Figures 1–3 generated with the accompanying diagram script. "
            "This document is a technical design proposal, not an operational product of Pano AI, CAL FIRE, ALERTCalifornia, Google, or NASA.",
            "caption",
        ),
    ]
    return story


def main():
    W, H = A4
    doc = BaseDocTemplate(
        str(OUT),
        pagesize=A4,
        title="EMBER-Net: A Hybrid Multimodal AI System for Early Wildfire Detection",
        author="Technical Report",
        subject="Multimodal AI — text, image, audio, video — wildfire detection",
    )
    cover_frame = Frame(18 * mm, 34 * mm, W - 36 * mm, H - 58 * mm, id="cover", showBoundary=0)
    inner_frame = Frame(16 * mm, 16 * mm, W - 32 * mm, H - 32 * mm, id="inner", showBoundary=0)
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
            PageTemplate(id="inner", frames=[inner_frame], onPage=draw_inner),
        ]
    )
    doc.build(build_story())
    print(OUT)
    print("pages written")


if __name__ == "__main__":
    main()
