#!/usr/bin/env python3
"""Build the Pushpak V1 final-year design-review PowerPoint."""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Emu

import kit as k
from slides_01_10 import (
    s01_title,
    s02_overview,
    s03_problem,
    s04_why,
    s05_mission,
    s06_objectives,
    s07_sysreq,
    s08_config,
    s09_architecture,
    s10_propulsion,
)
from slides_11_20 import (
    s11_hover,
    s12_wing_method,
    s13_lift,
    s14_geometry,
    s15_rotors,
    s16_tilt_arch,
    s17_tilt_work,
    s18_electronics,
    s19_pixhawk,
    s20_control,
)
from slides_21_30 import (
    s21_sensors,
    s22_modes,
    s23_transition,
    s24_safety,
    s25_mass,
    s26_bom,
    s27_cad,
    s28_cfd,
    s29_structures,
    s30_mfg,
)
from slides_31_40 import (
    s31_ground,
    s32_flight,
    s33_expected,
    s34_power,
    s35_risks,
    s36_future,
    s37_timeline,
    s38_budget,
    s39_conclusion,
    s40_thanks,
)

OUT = Path(__file__).parent / "Pushpak_V1_Tilt_Rotor_VTOL_UAV_Design_Review.pptx"


def build():
    prs = Presentation()
    prs.slide_width = Inches(k.SW)
    prs.slide_height = Inches(k.SH)
    # 16:9 already set by inches

    builders = [
        s01_title, s02_overview, s03_problem, s04_why, s05_mission,
        s06_objectives, s07_sysreq, s08_config, s09_architecture, s10_propulsion,
        s11_hover, s12_wing_method, s13_lift, s14_geometry, s15_rotors,
        s16_tilt_arch, s17_tilt_work, s18_electronics, s19_pixhawk, s20_control,
        s21_sensors, s22_modes, s23_transition, s24_safety, s25_mass,
        s26_bom, s27_cad, s28_cfd, s29_structures, s30_mfg,
        s31_ground, s32_flight, s33_expected, s34_power, s35_risks,
        s36_future, s37_timeline, s38_budget, s39_conclusion, s40_thanks,
    ]
    for fn in builders:
        fn(prs)

    prs.save(OUT)
    print(f"Wrote {OUT}  ({len(prs.slides)} slides)")
    return OUT


if __name__ == "__main__":
    build()
