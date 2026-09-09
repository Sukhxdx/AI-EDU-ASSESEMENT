#!/usr/bin/env python3
"""Generate architecture and fusion diagrams for the multimodal wildfire report."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

OUT = Path(__file__).resolve().parent
NAVY = "#1B365D"
EMBER = "#C45C26"
GOLD = "#D4A017"
TEAL = "#1D6A7A"
GREEN = "#2D6A4F"
MAGENTA = "#8B3A62"
AMBER = "#C47A12"
SLATE = "#3D4A5C"
LIGHT = "#F6F1E8"
BOX_FACE = "#FFFFFF"
INK = "#1A1A1A"
MUTED = "#5A6573"


def rounded(ax, x, y, w, h, facecolor, edgecolor, lw=1.4, radius=0.08, z=3):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.012,rounding_size={radius}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
        zorder=z,
        mutation_aspect=0.4,
    )
    ax.add_patch(patch)
    return patch


def text(ax, x, y, s, size=8.2, color=INK, weight="medium", ha="center", va="center", wrap=None):
    ax.text(
        x,
        y,
        s,
        fontsize=size,
        color=color,
        fontweight=weight,
        ha=ha,
        va=va,
        zorder=5,
        fontfamily="DejaVu Sans",
        linespacing=1.25,
        wrap=False,
    )


def layer_band(ax, y, h, color, alpha=0.08):
    ax.add_patch(Rectangle((0.18, y), 15.64, h, facecolor=color, edgecolor="none", alpha=alpha, zorder=0))


def arrow(ax, x1, y1, x2, y2, color=NAVY):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=1.15,
            color=color,
            zorder=2,
        )
    )


def make_architecture():
    fig, ax = plt.subplots(figsize=(16.2, 11.4), dpi=180)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11.4)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.text(
        8.0,
        11.08,
        "EMBER-Net  ·  Multimodal Processing Workflow & System Architecture",
        ha="center",
        va="center",
        fontsize=15.5,
        fontweight="bold",
        color=NAVY,
        fontfamily="DejaVu Sans",
    )
    ax.text(
        8.0,
        10.68,
        "Hybrid fusion of text, image, audio, and video for early wildfire detection and emergency response",
        ha="center",
        va="center",
        fontsize=9.2,
        color=MUTED,
        fontfamily="DejaVu Sans",
        style="italic",
    )

    # ----- Layer 1: Sensing -----
    layer_band(ax, 8.72, 1.72, TEAL, 0.07)
    rounded(ax, 0.28, 10.18, 2.15, 0.32, TEAL, TEAL, lw=0)
    text(ax, 1.35, 10.34, "1  SENSING & INGESTION", size=7.4, color="white", weight="bold")

    sensors = [
        (0.45, "Satellite\nIR / RGB", "Image", TEAL),
        (3.05, "Tower PTZ\n360° cameras", "Video", MAGENTA),
        (5.65, "UAV live\nvideo + stills", "Video", MAGENTA),
        (8.25, "IoT acoustic\n& wind sensors", "Audio", AMBER),
        (10.85, "911 / radio /\nsocial posts", "Text", GREEN),
        (13.45, "Weather, GIS\n& fuel maps", "Text", GREEN),
    ]
    for x, label, modality, color in sensors:
        rounded(ax, x, 8.88, 2.15, 1.18, BOX_FACE, color, lw=1.6, radius=0.1)
        ax.add_patch(Rectangle((x, 9.82), 2.15, 0.24, facecolor=color, edgecolor=color, zorder=4))
        text(ax, x + 1.075, 9.94, modality.upper(), size=6.6, color="white", weight="bold")
        text(ax, x + 1.075, 9.32, label, size=8.0, color=INK, weight="medium")

    # arrows down to encoders
    for x in [1.525, 4.125, 6.725, 9.325, 11.925, 14.525]:
        arrow(ax, x, 8.84, x if x < 15 else x, 8.42, SLATE)

    # ----- Layer 2: Encoders -----
    layer_band(ax, 6.78, 1.58, NAVY, 0.06)
    rounded(ax, 0.28, 8.12, 2.55, 0.32, NAVY, NAVY, lw=0)
    text(ax, 1.55, 8.28, "2  UNIMODAL ENCODERS", size=7.4, color="white", weight="bold")

    encoders = [
        (0.70, 3.20, "Vision Transformer / CNN\nsmoke, flame, heat signatures\nRGB + infrared embeddings", "Image encoder", TEAL),
        (4.30, 3.20, "Video transformer (TimeSformer)\ntemporal smoke growth, wind\ndrift, and fire-front motion", "Video encoder", MAGENTA),
        (7.90, 3.20, "Audio spectrogram + AST\ncrackle, roar, wind, sirens\n911-call speech-to-text", "Audio encoder", AMBER),
        (11.50, 3.70, "LLM / text encoder\nNER for location, weather\nseverity, and eyewitness claims", "Text encoder", GREEN),
    ]
    for x, w, body, title, color in encoders:
        rounded(ax, x, 6.90, w, 1.12, BOX_FACE, color, lw=1.6, radius=0.1)
        text(ax, x + w / 2, 7.78, title, size=8.3, color=color, weight="bold")
        text(ax, x + w / 2, 7.28, body, size=7.2, color=SLATE)

    for x in [2.30, 5.90, 9.50, 13.35]:
        arrow(ax, x, 6.86, x, 6.42, SLATE)

    # ----- Layer 3: Hybrid fusion -----
    layer_band(ax, 4.58, 1.78, EMBER, 0.08)
    rounded(ax, 0.28, 6.10, 3.35, 0.32, EMBER, EMBER, lw=0)
    text(ax, 1.95, 6.26, "3  HYBRID MULTIMODAL FUSION", size=7.4, color="white", weight="bold")

    fusion_boxes = [
        (0.55, "Early fusion", "Concatenate co-located\nRGB + IR + microphone\nfeatures before classifying.\nBest for one tower station."),
        (5.75, "Cross-attention fusion", "Query-key attention across\nmodalities aligns smoke in\nvideo with wind text and\nheat in satellite tiles."),
        (10.95, "Late fusion", "Independent unimodal scores\n(social rumor, satellite,\ncamera) are combined by a\ncalibrated meta-classifier."),
    ]
    for x, title, body in fusion_boxes:
        rounded(ax, x, 4.68, 4.50, 1.32, BOX_FACE, EMBER, lw=1.55, radius=0.1)
        text(ax, x + 2.25, 5.72, title, size=8.6, color=EMBER, weight="bold")
        text(ax, x + 2.25, 5.18, body, size=7.15, color=SLATE)

    arrow(ax, 8.0, 4.64, 8.0, 4.22, EMBER)

    # combiner
    rounded(ax, 4.55, 3.72, 6.90, 0.48, EMBER, EMBER, lw=0, radius=0.08)
    text(
        ax,
        8.0,
        3.96,
        "Gated hybrid combiner  ·  reliability weights + missing-modality masking  ·  human-in-the-loop gate",
        size=8.0,
        color="white",
        weight="bold",
    )

    arrow(ax, 8.0, 3.68, 8.0, 3.28, SLATE)

    # ----- Layer 4: Decision -----
    layer_band(ax, 2.22, 1.00, NAVY, 0.06)
    rounded(ax, 0.28, 2.96, 2.55, 0.28, NAVY, NAVY, lw=0)
    text(ax, 1.55, 3.10, "4  REASONING & DECISION", size=7.2, color="white", weight="bold")

    decisions = [
        (0.50, "Ignition probability\n& confidence interval"),
        (4.50, "GPS triangulation\n& fire-front estimate"),
        (8.50, "Spread forecast using\nweather + fuel maps"),
        (12.50, "Analyst review queue\n& false-alarm filter"),
    ]
    for x, label in decisions:
        rounded(ax, x, 2.28, 3.10, 0.62, BOX_FACE, NAVY, lw=1.35, radius=0.08)
        text(ax, x + 1.55, 2.59, label, size=7.6, color=NAVY)

    for x in [2.05, 6.05, 10.05, 14.05]:
        arrow(ax, x, 2.24, x, 1.88, SLATE)

    # ----- Layer 5: Outputs -----
    layer_band(ax, 0.28, 1.52, GREEN, 0.07)
    rounded(ax, 0.28, 1.54, 2.15, 0.28, GREEN, GREEN, lw=0)
    text(ax, 1.35, 1.68, "5  SYSTEM OUTPUTS", size=7.2, color="white", weight="bold")

    outputs = [
        (0.50, "Priority alert to\nfire agency CAD"),
        (4.50, "Live map: location,\nperimeter, assets"),
        (8.50, "Dispatch recommendation\n(helitack / engine)"),
        (12.50, "Public warning &\nevacuation guidance"),
    ]
    for x, label in outputs:
        rounded(ax, x, 0.42, 3.10, 1.02, BOX_FACE, GREEN, lw=1.5, radius=0.1)
        text(ax, x + 1.55, 0.93, label, size=8.0, color=GREEN, weight="bold")

    fig.tight_layout(pad=0.25)
    path = OUT / "figure1_architecture.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def make_fusion():
    fig, ax = plt.subplots(figsize=(16.0, 8.4), dpi=180)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8.4)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        8.0,
        8.05,
        "Representation & Fusion Methods  ·  Why EMBER-Net Uses Hybrid Fusion",
        ha="center",
        va="center",
        fontsize=14.6,
        fontweight="bold",
        color=NAVY,
        fontfamily="DejaVu Sans",
    )
    ax.text(
        8.0,
        7.62,
        "Early, late, and cross-modal attention are combined because wildfire data arrive at different times, rates, and reliability levels",
        ha="center",
        va="center",
        fontsize=8.8,
        color=MUTED,
        fontfamily="DejaVu Sans",
        style="italic",
    )

    columns = [
        {
            "x": 0.40,
            "title": "Early fusion",
            "subtitle": "Feature-level",
            "color": TEAL,
            "chosen": False,
            "flow": [
                "Raw / low-level features\nfrom RGB + IR + mic",
                "Concatenate or project\ninto one vector",
                "Single classifier\n(smoke vs. not smoke)",
            ],
            "pros": "Captures fine cross-sensor\ncorrelations at one site",
            "cons": "Fails if a sensor is down;\nhard with unsynchronized\nsocial-media text",
        },
        {
            "x": 5.55,
            "title": "Late fusion",
            "subtitle": "Decision-level",
            "color": AMBER,
            "chosen": False,
            "flow": [
                "Separate model per\nmodality (vision, text…)",
                "Each model emits a\nscore or class",
                "Weighted vote / stacking\nmeta-classifier",
            ],
            "pros": "Robust to missing sources;\neasy to add a new feed",
            "cons": "Misses low-level cues\n(e.g. heat + faint smoke\nthat neither model trusts)",
        },
        {
            "x": 10.70,
            "title": "Hybrid fusion  ✓",
            "subtitle": "Chosen method",
            "color": EMBER,
            "chosen": True,
            "flow": [
                "Early fuse co-located\ntower RGB + IR + audio",
                "Cross-attention across\nvideo, satellite, text",
                "Late fuse agency-level\nscores + human review",
            ],
            "pros": "Uses the right fusion for\neach data pair; graceful\ndegradation if a feed fails",
            "cons": "More engineering; needs\ncalibration and monitoring\nof modality weights",
        },
    ]

    for col in columns:
        x = col["x"]
        face = "#FFF6EF" if col["chosen"] else "#FFFFFF"
        rounded(ax, x, 0.28, 4.90, 7.10, face, col["color"], lw=2.1 if col["chosen"] else 1.4, radius=0.12)
        ax.add_patch(Rectangle((x, 6.72), 4.90, 0.66, facecolor=col["color"], edgecolor=col["color"], zorder=4))
        text(ax, x + 2.45, 7.18, col["title"], size=12.0, color="white", weight="bold")
        text(ax, x + 2.45, 6.86, col["subtitle"], size=7.6, color="#FFE8D6")

        y = 6.35
        for i, step in enumerate(col["flow"], start=1):
            rounded(ax, x + 0.35, y - 0.95, 4.20, 0.95, BOX_FACE, col["color"], lw=1.2, radius=0.08)
            text(ax, x + 0.62, y - 0.48, str(i), size=11, color=col["color"], weight="bold", ha="center")
            text(ax, x + 2.55, y - 0.48, step, size=7.8, color=INK, ha="center")
            if i < 3:
                arrow(ax, x + 2.45, y - 0.98, x + 2.45, y - 1.18, col["color"])
            y -= 1.22

        rounded(ax, x + 0.35, 1.55, 4.20, 0.85, "#EAF6F4", GREEN, lw=1.0, radius=0.08)
        text(ax, x + 2.45, 2.18, "Strength", size=7.2, color=GREEN, weight="bold")
        text(ax, x + 2.45, 1.82, col["pros"], size=7.1, color=SLATE)

        rounded(ax, x + 0.35, 0.48, 4.20, 0.95, "#F8EEE8", EMBER, lw=1.0, radius=0.08)
        text(ax, x + 2.45, 1.20, "Limitation", size=7.2, color=EMBER, weight="bold")
        text(ax, x + 2.45, 0.82, col["cons"], size=7.1, color=SLATE)

    fig.tight_layout(pad=0.3)
    path = OUT / "figure2_fusion.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def make_io():
    fig, ax = plt.subplots(figsize=(16.0, 6.6), dpi=180)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 6.6)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        8.0,
        6.28,
        "System Inputs and Outputs",
        ha="center",
        va="center",
        fontsize=15.0,
        fontweight="bold",
        color=NAVY,
        fontfamily="DejaVu Sans",
    )

    # Inputs panel
    rounded(ax, 0.35, 0.35, 6.55, 5.55, "#FFFFFF", TEAL, lw=1.8, radius=0.12)
    ax.add_patch(Rectangle((0.35, 5.32), 6.55, 0.58, facecolor=TEAL, edgecolor=TEAL, zorder=4))
    text(ax, 3.62, 5.61, "INPUTS  (heterogeneous streams)", size=10.2, color="white", weight="bold")

    inputs = [
        (TEAL, "Image", "Satellite IR/RGB tiles, drone stills, lookout photos, thermal frames"),
        (MAGENTA, "Video", "PTZ 360° tower streams, UAV live feed, time-lapse smoke columns"),
        (AMBER, "Audio", "IoT crackle/wind mics, 911 voice, firefighter radio traffic"),
        (GREEN, "Text", "Weather bulletins, 911 transcripts, social posts, GIS/fuel metadata"),
    ]
    y = 4.55
    for color, title, body in inputs:
        rounded(ax, 0.60, y - 0.78, 6.05, 0.88, BOX_FACE, color, lw=1.3, radius=0.08)
        rounded(ax, 0.78, y - 0.52, 1.35, 0.38, color, color, lw=0, radius=0.06)
        text(ax, 1.45, y - 0.33, title, size=7.6, color="white", weight="bold")
        text(ax, 4.15, y - 0.33, body, size=7.3, color=SLATE, ha="center")
        y -= 1.05

    # Outputs panel
    rounded(ax, 9.10, 0.35, 6.55, 5.55, "#FFFFFF", GREEN, lw=1.8, radius=0.12)
    ax.add_patch(Rectangle((9.10, 5.32), 6.55, 0.58, facecolor=GREEN, edgecolor=GREEN, zorder=4))
    text(ax, 12.38, 5.61, "OUTPUTS  (actionable products)", size=10.2, color="white", weight="bold")

    outputs = [
        ("Alert packet", "Time, GPS, probability, images, recommended resources"),
        ("Situation map", "Live perimeter, assets at risk, wind overlay, camera views"),
        ("Narrative brief", "Plain-language summary for dispatchers and incident command"),
        ("Public products", "Map pins, evacuation zones, and verified warning messages"),
    ]
    y = 4.55
    for i, (title, body) in enumerate(outputs, start=1):
        rounded(ax, 9.35, y - 0.78, 6.05, 0.88, BOX_FACE, GREEN, lw=1.3, radius=0.08)
        text(ax, 9.72, y - 0.33, f"{i}", size=11, color=GREEN, weight="bold", ha="center")
        text(ax, 11.35, y - 0.18, title, size=8.4, color=GREEN, weight="bold", ha="left")
        text(ax, 11.35, y - 0.48, body, size=7.2, color=SLATE, ha="left")
        y -= 1.05

    # center arrow
    ax.annotate(
        "",
        xy=(8.85, 3.15),
        xytext=(7.15, 3.15),
        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2.2, mutation_scale=18),
    )
    text(ax, 8.0, 3.48, "EMBER-Net", size=7.4, color=NAVY, weight="bold")

    fig.tight_layout(pad=0.25)
    path = OUT / "figure3_io.png"
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


if __name__ == "__main__":
    p1 = make_architecture()
    p2 = make_fusion()
    p3 = make_io()
    print(p1)
    print(p2)
    print(p3)
