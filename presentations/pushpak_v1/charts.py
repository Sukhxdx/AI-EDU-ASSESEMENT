"""Engineering charts for Pushpak V1 — dark aerospace theme."""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

BG = "#0A1220"
CARD = "#121C30"
CYAN = "#00D4E8"
AMBER = "#F5B942"
TEAL = "#2EE6A6"
ORANGE = "#FF7A45"
OFF = "#D7DFEA"
MUTED = "#8A97AD"
STROKE = "#243450"
RED = "#FF5C6A"


def _ax_style(ax, fig):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD)
    ax.tick_params(colors=MUTED, labelsize=8)
    for sp in ax.spines.values():
        sp.set_color(STROKE)
    ax.yaxis.label.set_color(MUTED)
    ax.xaxis.label.set_color(MUTED)
    ax.title.set_color(OFF)


def naca4412(path=OUT / "naca4412.png"):
    m, p, t = 0.04, 0.4, 0.12
    x = np.linspace(0, 1, 300)
    yt = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
    yc = np.where(
        x < p,
        m / p**2 * (2 * p * x - x**2),
        m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x**2),
    )
    dyc = np.where(x < p, 2 * m / p**2 * (p - x), 2 * m / (1 - p) ** 2 * (p - x))
    th = np.arctan(dyc)
    xu, yu = x - yt * np.sin(th), yc + yt * np.cos(th)
    xl, yl = x + yt * np.sin(th), yc - yt * np.cos(th)
    fig, ax = plt.subplots(figsize=(8.4, 3.2), dpi=180)
    _ax_style(ax, fig)
    ax.fill(np.r_[xu, xl[::-1]], np.r_[yu, yl[::-1]], color=CYAN, alpha=0.18, zorder=2)
    ax.plot(xu, yu, color=CYAN, lw=1.8)
    ax.plot(xl, yl, color=CYAN, lw=1.8)
    ax.plot(x, yc, color=AMBER, lw=1.0, ls="--", label="Mean camber")
    ax.set_aspect("equal")
    ax.set_xlim(-0.02, 1.05)
    ax.set_ylim(-0.12, 0.18)
    ax.set_xlabel("x/c")
    ax.set_ylabel("z/c")
    ax.set_title("NACA 4412  ·  t/c = 12%  ·  camber = 4% at 0.4c", loc="left", fontsize=10, pad=8)
    ax.grid(True, color=STROKE, lw=0.6)
    ax.legend(facecolor=CARD, edgecolor=STROKE, labelcolor=OFF, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()


def mass_budget(path=OUT / "mass_budget.png"):
    items = [
        ("Battery", 1.25, CYAN),
        ("Motors", 0.80, CYAN),
        ("Fuselage", 0.40, TEAL),
        ("Tilt system", 0.30, TEAL),
        ("Wing", 0.30, TEAL),
        ("ESCs", 0.25, AMBER),
        ("Electronics", 0.20, AMBER),
        ("Landing gear", 0.15, AMBER),
        ("Payload", 1.00, ORANGE),
    ]
    fig, ax = plt.subplots(figsize=(8.6, 4.6), dpi=180)
    _ax_style(ax, fig)
    y = np.arange(len(items))
    ax.barh(y, [v for _, v, _ in items], color=[c for *_, c in items], height=0.62, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([n for n, *_ in items], color=OFF, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Mass (kg)")
    ax.axvline(3.5, color=AMBER, ls="--", lw=1.1, label="Empty-airframe target 3.5 kg")
    ax.set_xlim(0, 1.6)
    ax.grid(True, axis="x", color=STROKE, lw=0.6)
    ax.legend(facecolor=CARD, edgecolor=STROKE, labelcolor=OFF, fontsize=8)
    for i, (_, v, _) in enumerate(items):
        ax.text(v + 0.03, i, f"{v:.2f}", va="center", color=OFF, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()


def power_compare(path=OUT / "power_compare.png"):
    labels = [
        "Hover OGE\n(rotor-borne)",
        "Wing-off\nforward 20 m/s",
        "Wing-on cruise\n70% wing lift",
        "Wing-on cruise\n(drag-sized thrust)",
    ]
    p_lo = [520, 680, 300, 190]
    p_hi = [640, 820, 380, 240]
    mid = [(a + b) / 2 for a, b in zip(p_lo, p_hi)]
    yerr = [(b - a) / 2 for a, b in zip(p_lo, p_hi)]
    colors = [ORANGE, RED, CYAN, TEAL]
    fig, ax = plt.subplots(figsize=(8.8, 4.4), dpi=180)
    _ax_style(ax, fig)
    x = np.arange(len(labels))
    ax.bar(x, mid, yerr=yerr, color=colors, width=0.55, capsize=5, zorder=3, error_kw=dict(ecolor=OFF, lw=1))
    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=OFF, fontsize=8.5)
    ax.set_ylabel("Electrical power (W)")
    ax.set_ylim(0, 1000)
    ax.grid(True, axis="y", color=STROKE, lw=0.6)
    ax.set_title("Estimated electrical power  ·  MTOW 4.5 kg  ·  6S", loc="left", fontsize=10, pad=8)
    for i, m in enumerate(mid):
        ax.text(i, m + yerr[i] + 30, f"{p_lo[i]}–{p_hi[i]} W", ha="center", color=OFF, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()


def hover_cascade(path=OUT / "hover_cascade.png"):
    fig, ax = plt.subplots(figsize=(9.2, 3.6), dpi=180)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    steps = [
        ("MTOW", "4.50 kg", CYAN),
        ("Weight", "44.15 N", CYAN),
        ("Per motor", "11.04 N", AMBER),
        ("Hover load", "1.125 kgf", AMBER),
        ("Design thrust", "2.25 kgf", TEAL),
        ("Total static", "≈ 9 kgf", TEAL),
    ]
    n = len(steps)
    for i, (lab, val, col) in enumerate(steps):
        x = 0.02 + i * 0.165
        box = FancyBboxPatch(
            (x, 0.28),
            0.145,
            0.50,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            linewidth=1.0,
            edgecolor=col,
            facecolor=CARD,
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(x + 0.0725, 0.62, val, ha="center", va="center", color=OFF, fontsize=10, fontweight="bold", transform=ax.transAxes)
        ax.text(x + 0.0725, 0.40, lab.upper(), ha="center", va="center", color=col, fontsize=7, transform=ax.transAxes)
        if i < n - 1:
            ax.annotate(
                "",
                xy=(x + 0.158, 0.53),
                xytext=(x + 0.148, 0.53),
                xycoords=ax.transAxes,
                textcoords=ax.transAxes,
                arrowprops=dict(arrowstyle="->", color=CYAN, lw=1.2),
            )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()


def timeline(path=OUT / "timeline.png"):
    phases = [
        ("Requirements &\nconfig freeze", 0, 1.0, CYAN),
        ("Aero + propulsion\nsizing", 0.7, 1.6, CYAN),
        ("Tilt mechanism\nCAD", 1.5, 2.4, TEAL),
        ("Airframe CAD\n& structures", 2.0, 3.4, TEAL),
        ("Avionics\nintegration", 3.0, 4.6, AMBER),
        ("Prototype\nmanufacture", 3.6, 5.6, AMBER),
        ("Ground test", 5.2, 6.6, ORANGE),
        ("Flight test &\nPDR closeout", 6.2, 8.0, ORANGE),
    ]
    fig, ax = plt.subplots(figsize=(10.6, 4.4), dpi=180)
    _ax_style(ax, fig)
    for i, (name, a, b, col) in enumerate(phases):
        ax.barh(i, b - a, left=a, height=0.55, color=col, alpha=0.9, zorder=3)
        ax.text(8.15, i, name.replace("\n", " "), va="center", ha="left", color=OFF, fontsize=8)
    ax.set_yticks([])
    ax.set_xlim(0, 11.2)
    ax.set_xlabel("Months from kickoff")
    ax.set_xticks(range(0, 9))
    ax.set_xticklabels(["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"], color=MUTED)
    ax.grid(True, axis="x", color=STROKE, lw=0.6)
    ax.set_title("8-month design–build–test programme", loc="left", fontsize=10, pad=8)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()


def cl_bar(path=OUT / "lift_target.png"):
    fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=180)
    _ax_style(ax, fig)
    labs = ["Required CL\n(70% weight)", "NACA 4412\nCL @ 4–6° (typ.)", "Design margin"]
    vals = [0.395, 0.70, 0.30]
    cols = [CYAN, TEAL, AMBER]
    ax.bar(labs, vals, color=cols, width=0.55, zorder=3)
    ax.set_ylabel("CL  /  ΔCL")
    ax.set_ylim(0, 1.0)
    ax.grid(True, axis="y", color=STROKE, lw=0.6)
    ax.set_title("Cruise lift coefficient vs airfoil capability", loc="left", fontsize=10)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.03, f"{v:.3f}" if i == 0 else f"{v:.2f}", ha="center", color=OFF, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    naca4412()
    mass_budget()
    power_compare()
    hover_cascade()
    timeline()
    cl_bar()
    print("charts written to", OUT)
