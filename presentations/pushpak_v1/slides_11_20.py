"""Slides 11–20 — aero, geometry, tilt, electronics, control."""

from pathlib import Path

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

import kit as k

A = Path(__file__).parent / "assets"


def _base(prs, kicker, title, num, notes, subtitle=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    k.set_bg(s)
    k.header(s, kicker, title, subtitle)
    k.footer(s, num)
    k.notes(s, notes)
    return s


def s11_hover(prs):
    s = _base(
        prs, "10  /  HOVER", "Hover Thrust Analysis", 11,
        "Walk the cascade: 4.5 kg → 44.15 N → 11.04 N per motor → 1.125 kgf. That is the physics floor, not the design.\n"
        "Design is 2.25 kgf per motor, 9 kgf total — about 2.0× hover. We need that for climb, tilt transients, and one-motor-soft failures.\n"
        "16-inch disk at this loading is why 400KV / 6S was chosen.",
        "MTOW 4.5 kg  ·  g = 9.81 m/s²  ·  four equal motors",
    )
    k.picture(s, A / "hover_cascade.png", 0.35, 1.15, 12.6, 2.35)

    calcs = [
        ("W = mg", "4.50 × 9.81 = 44.15 N"),
        ("T_hover / motor", "44.15 / 4 = 11.04 N"),
        ("kgf equivalent", "11.04 / 9.81 = 1.125 kgf"),
        ("Design T / motor", "2.25 kgf  (≈ 22.1 N)"),
        ("Total static T", "≈ 9.0 kgf  (≈ 88 N)"),
        ("Thrust / weight", "9.0 / 4.5  ≈  2.0"),
    ]
    for i, (t, b) in enumerate(calcs):
        x = 0.42 + (i % 3) * 4.16
        y = 3.60 + (i // 3) * 1.70
        k.card(s, x, y, 3.98, 1.55, k.CYAN)
        k.textbox(s, x + 0.16, y + 0.16, 3.66, 0.32, t.upper(), 11, k.CYAN, True, k.MONO)
        k.textbox(s, x + 0.16, y + 0.55, 3.66, 0.72, b, 18, k.WHITE, True, k.MONO)


def s12_wing_method(prs):
    s = _base(
        prs, "11  /  WING", "Wing Design Methodology", 12,
        "Start from cruise lift, not from a pretty span. 70% of 44.15 N at 20 m/s fixes CL·S.\n"
        "S = 0.32 m² and AR 5.3 are a student-build compromise: enough span for induced-drag, short enough for 1.3 m transport.\n"
        "NACA 4412 is a known cambered section with gentle stall — appropriate for a first VTOL wing, not a racing foil.",
    )
    k.process_bar(
        s, 0.42, 1.22, 12.48, 0.48,
        ["Lift target", "Pick V, S", "Compute CL", "Select airfoil", "Fix AR / span", "Winglets"],
    )
    k.picture(s, A / "pushpak-wing.png", 0.42, 1.88, 6.4, 3.35)
    k.hud_corners(s, 0.42, 1.88, 6.4, 3.35)
    k.picture(s, A / "naca4412.png", 6.95, 1.88, 5.95, 2.35)

    params = [
        ("SPAN", "1300 mm"),
        ("AREA", "0.32 m²"),
        ("CHORD", "246 mm"),
        ("AR", "5.3"),
        ("FOIL", "4412"),
        ("TIPS", "2 winglets"),
    ]
    for i, (a, b) in enumerate(params):
        x = 0.42 + i * 2.12
        k.card(s, x, 5.40, 2.02, 1.70, k.CYAN)
        k.textbox(s, x + 0.10, y := 5.55, 1.82, 0.28, a, 10, k.CYAN, True, k.MONO)
        k.textbox(s, x + 0.10, 5.90, 1.82, 0.85, b, 16, k.WHITE, True, k.MONO)


def s13_lift(prs):
    s = _base(
        prs, "12  /  LIFT", "Lift Calculations", 13,
        "L = ½ ρ V² S CL. At 20 m/s, q = 245 Pa. For 70% of weight, L = 30.90 N → CL = 0.395.\n"
        "NACA 4412 produces that CL at a modest angle of attack with margin to stall.\n"
        "The remaining 30% of weight is residual rotor lift at 75° tilt — conservative, not minimum-power.",
    )
    k.card(s, 0.42, 1.22, 7.35, 2.15, k.CYAN)
    k.textbox(s, 0.62, 1.38, 7.0, 0.28, "CRUISE LIFT EQUATION", 11, k.CYAN, True, k.MONO)
    k.textbox(s, 0.62, 1.72, 7.0, 0.55, "L  =  ½ ρ V² S CL     →     CL  =  L / (q S)", 20, k.WHITE, True, k.MONO)
    k.textbox(s, 0.62, 2.40, 7.0, 0.7, "ρ = 1.225 kg/m³   ·   V = 20 m/s   ·   q = 245 Pa   ·   S = 0.32 m²   ·   L_target = 0.70 × 44.15 = 30.90 N", 13, k.OFF)

    tiles = [
        ("20 m/s", "CRUISE SPEED", k.CYAN),
        ("70%", "WING LIFT SHARE", k.AMBER),
        ("0.395", "REQUIRED CL", k.TEAL),
        ("30.90 N", "WING LIFT", k.CYAN),
    ]
    for i, (v, lab, col) in enumerate(tiles):
        k.kpi(s, 7.95, 1.22 + i * 1.42, 4.95, 1.30, v, lab, accent=col)

    k.picture(s, A / "lift_target.png", 0.42, 3.55, 7.35, 3.55)
    k.hud_corners(s, 0.42, 3.55, 7.35, 3.55)


def s14_geometry(prs):
    s = _base(
        prs, "13  /  GEOMETRY", "Aircraft Geometry", 14,
        "These envelopes bound CAD, not a freeze of every millimetre. Rotor span 1700–1900 mm is set by 16-inch props plus 50–75 mm clearance.\n"
        "Fuselage length carries battery, Pixhawk, and the 1 kg payload on CG.\n"
        "75° is a hard stop — never software-only.",
    )
    k.picture(s, A / "pushpak-sideview.png", 0.42, 1.22, 7.55, 4.05)
    k.hud_corners(s, 0.42, 1.22, 7.55, 4.05)
    data = [
        ["Station", "Dimension"],
        ["Fuselage length", "1200–1300 mm"],
        ["Wing span", "1300 mm"],
        ["Rotor span (tip-to-tip)", "1700–1900 mm"],
        ["Propeller diameter", "406 mm"],
        ["Mean chord", "246 mm"],
        ["Wing area", "0.32 m²"],
        ["Max rotor tilt", "75°"],
        ["Min prop clearance", "50–75 mm"],
    ]
    k.add_table(s, data, 8.15, 1.22, 4.75, 4.05, 12)
    k.card(s, 0.42, 5.45, 12.48, 1.65, k.CYAN)
    k.textbox(s, 0.62, 5.60, 12.1, 0.28, "LAYOUT INTENT", 11, k.CYAN, True, k.MONO)
    k.textbox(
        s, 0.62, 5.95, 12.1, 0.9,
        "High wing keeps the prop disks clear of the fuselage and simplifies landing-gear length. Front tilt shaft sits ahead of the leading edge; rear shaft sits aft of the trailing edge. CG is between the two shafts so hover moments stay small.",
        14, k.OFF,
    )


def s15_rotors(prs):
    s = _base(
        prs, "14  /  ROTORS", "Rotor Placement Layout", 15,
        "Top view is the configuration control drawing. Four disks, two shafts, wing in the middle.\n"
        "Clearance 50–75 mm is a hard CAD constraint — downwash and blade flex eat the lower number.\n"
        "Front-left / front-right share one shaft; they cannot tilt independently. Same at the rear.",
    )
    k.picture(s, A / "pushpak-topview.png", 0.42, 1.18, 8.15, 4.55)
    k.hud_corners(s, 0.42, 1.18, 8.15, 4.55)

    labels = [
        ("FRONT LEFT", "On front tilt shaft  ·  tilts with FR"),
        ("FRONT RIGHT", "On front tilt shaft  ·  1 servo"),
        ("REAR LEFT", "On rear tilt shaft  ·  tilts with RR"),
        ("REAR RIGHT", "On rear tilt shaft  ·  1 servo"),
    ]
    for i, (t, b) in enumerate(labels):
        y = 1.18 + i * 1.15
        k.card(s, 8.75, y, 4.15, 1.05, k.CYAN)
        k.textbox(s, 8.90, y + 0.12, 3.85, 0.32, t, 13, k.CYAN, True, k.MONO)
        k.textbox(s, 8.90, y + 0.48, 3.85, 0.42, b, 12, k.OFF)

    k.card(s, 0.42, 5.90, 12.48, 1.20, k.AMBER)
    k.textbox(
        s, 0.62, 6.15, 12.1, 0.75,
        "Minimum propeller clearance  50–75 mm   ·   rotor span  1700–1900 mm   ·   propeller D  406 mm   ·   wing span  1300 mm (between the two shafts)",
        14, k.WHITE, True,
    )


def s16_tilt_arch(prs):
    s = _base(
        prs, "15  /  TILT", "Tilt Mechanism Architecture", 16,
        "One mechanism, two copies. Front and rear are the same drawing with mirrored servo handedness.\n"
        "The shaft is the structural spine — motors never hang off the servo horn.\n"
        "Magnetic angle sensors close the loop; mechanical stops are the last line of defence at 0° and 75°.",
    )
    k.picture(s, A / "pushpak-tilt-exploded.png", 0.42, 1.18, 7.7, 4.35)
    k.hud_corners(s, 0.42, 1.18, 7.7, 4.35)

    chain = ["MOTOR", "MOUNT", "SHAFT", "BEARINGS", "LINKAGE", "SERVO"]
    k.process_bar(s, 0.42, 5.70, 12.48, 0.42, chain)

    parts = [
        ("PER AXIS", "1 shaft  ·  2 motor mounts  ·  4 bearings  ·  1 servo  ·  linkage  ·  stops  ·  1 angle sensor"),
        ("ACTUATOR", "STS3215-C018 serial bus servo  ·  one per axis  ·  not per motor"),
        ("STOPS", "Hard mechanical limits at hover (0°) and cruise (75°)  ·  independent of software"),
        ("SENSOR", "Absolute magnetic angle  ·  logged to Pixhawk / ESP32  ·  jam detection"),
    ]
    for i, (t, b) in enumerate(parts):
        y = 1.18 + i * 1.08
        k.card(s, 8.30, y, 4.60, 0.98, k.CYAN)
        k.textbox(s, 8.46, y + 0.08, 4.3, 0.26, t, 11, k.CYAN, True, k.MONO)
        k.textbox(s, 8.46, y + 0.38, 4.3, 0.50, b, 12, k.OFF)


def s17_tilt_work(prs):
    s = _base(
        prs, "16  /  TILT LOGIC", "Tilt Mechanism Working Principle", 17,
        "Hover: thrust vector vertical, wing is a passenger. Transition: tilt with airspeed, not with a timer.\n"
        "Cruise: 75° — rotors mostly axial for thrust, residual vertical component plus wing lift equal weight.\n"
        "The kinematic chain is Motor → Tilt shaft → Bearings → Linkage → Servo. The servo never carries rotor loads.",
    )
    k.picture(s, A / "pushpak-modes.png", 0.42, 1.18, 12.48, 3.15)
    k.hud_corners(s, 0.42, 1.18, 12.48, 3.15)
    modes = [
        ("01  HOVER", "Tilt 0°  ·  T vertical\nWing lift ≈ 0\nQuad mixer active"),
        ("02  TRANSITION", "Tilt scheduled vs airspeed\nWing loading rising\nCollective reducing"),
        ("03  CRUISE", "Tilt 75°  ·  T mostly axial\nWing ~70% of weight\nPower experiment window"),
    ]
    for i, (t, b) in enumerate(modes):
        x = 0.42 + i * 4.16
        k.card(s, x, 4.50, 3.98, 1.55, k.CYAN)
        k.textbox(s, x + 0.16, 4.62, 3.66, 0.30, t, 13, k.CYAN, True, k.MONO)
        k.multiline(s, x + 0.10, 4.95, 3.76, 0.95, b.split("\n"), 13, k.OFF)

    k.card(s, 0.42, 6.18, 12.48, 0.95, k.AMBER)
    k.multiline(
        s, 0.55, 6.28, 12.2, 0.78,
        [
            ("LOAD PATH      MOTOR → MOUNT → TILT SHAFT → BEARINGS → AIRFRAME", {"size": 13, "color": k.WHITE, "bold": True, "font": k.MONO}),
            ("COMMAND PATH   FC → SERVO → LINKAGE → SHAFT     (servo never carries rotor loads)", {"size": 13, "color": k.OFF, "bold": False, "font": k.MONO}),
        ],
    )


def s18_electronics(prs):
    s = _base(
        prs, "17  /  AVIONICS", "Electronics Architecture", 18,
        "Three layers: sense, decide, act. Pixhawk is the real-time flight computer. ESP32 is the companion for tilt telemetry, power sensing and experiment logging.\n"
        "Do not put motor PWM on the ESP32. ArduPilot owns the motors.\n"
        "Pitot is mandatory — transition is airspeed-scheduled.",
    )
    k.picture(s, A / "pushpak-avionics.png", 0.42, 1.18, 6.15, 3.45)
    k.hud_corners(s, 0.42, 1.18, 6.15, 3.45)

    layers = [
        (k.CYAN, "SENSE", "Pitot  ·  GPS  ·  compass  ·  mag angle ×2  ·  IMU  ·  V/I bus  ·  actuator current"),
        (k.AMBER, "DECIDE", "Pixhawk / ArduPilot flight laws  ·  ESP32 companion I/O and experiment log"),
        (k.TEAL, "ACT", "4 × ESC / motor  ·  front tilt servo  ·  rear tilt servo"),
    ]
    for i, (col, t, b) in enumerate(layers):
        y = 1.18 + i * 1.15
        k.card(s, 6.75, y, 6.15, 1.05, col)
        k.textbox(s, 6.92, y + 0.10, 5.8, 0.28, t, 12, col, True, k.MONO)
        k.textbox(s, 6.92, y + 0.42, 5.8, 0.50, b, 13, k.OFF)

    data = [
        ["Node", "Function"],
        ["Pixhawk", "Attitude, VTOL mixer, failsafes, logging"],
        ["ArduPilot", "QHOVER / QLOITER / FBWA / AUTO"],
        ["ESP32", "Tilt telemetry, power DAQ, experiment flags"],
        ["Pitot", "Calibrated airspeed for tilt schedule"],
        ["GPS + compass", "Position, heading, RTL"],
        ["Mag angle", "Absolute tilt on each shaft"],
    ]
    k.add_table(s, data, 0.42, 4.78, 12.48, 2.32, 11)


def s19_pixhawk(prs):
    s = _base(
        prs, "18  /  INTEGRATION", "Pixhawk–ESP32 Integration", 19,
        "Split of authority is a safety argument: if ESP32 locks, the aircraft must still hover and RTL as a quadrotor.\n"
        "Interface is serial (MAVLink or a framed UART) plus discrete experiment enable.\n"
        "Tilt servos can be driven from Pixhawk outputs with ESP32 monitoring the encoder — preferred for first flight.",
    )
    k.card(s, 0.42, 1.22, 5.85, 5.85, k.CYAN)
    k.textbox(s, 0.62, 1.40, 5.5, 0.30, "PIXHAWK  /  ARDUPILOT", 14, k.CYAN, True, k.MONO)
    k.bullet_block(s, 0.55, 1.85, 5.5, 4.9, [
        "Owns motor mixer and VTOL modes.",
        "Runs attitude / position loops.",
        "Issues front and rear tilt PWM / bus commands.",
        "Hosts failsafes: batt, GCS, geofence, RTL.",
        "Records onboard .bin log (IMU, GPS, RC).",
        "Reads pitot as airspeed sensor.",
        "If companion dies → freeze last tilt or revert to hover.",
    ], 14)

    k.arrow_right(s, 6.35, 3.85, 0.55, 0.28, k.CYAN)

    k.card(s, 7.05, 1.22, 5.85, 5.85, k.AMBER)
    k.textbox(s, 7.25, 1.40, 5.5, 0.30, "ESP32 COMPANION", 14, k.AMBER, True, k.MONO)
    k.bullet_block(s, 7.18, 1.85, 5.5, 4.9, [
        "Samples magnetic tilt encoders at high rate.",
        "Samples battery voltage, current, actuator current.",
        "Stamps experiment events (wing-on / wing-off run IDs).",
        "Forwards compact telemetry to GCS / SD.",
        "Does not command motor throttle.",
        "Watchdog heartbeats to Pixhawk.",
        "Can inhibit further tilt if encoder disagreement.",
    ], 14)


def s20_control(prs):
    s = _base(
        prs, "19  /  CONTROL", "Control System Architecture", 20,
        "This is an I/O context diagram, not a Simulink file. Left = measured and commanded inputs. Centre = mode logic. Right = the four effectors plus the two tilt axes.\n"
        "Vertical velocity, altitude and vertical acceleration are what keep transition from ballooning or settling.\n"
        "Battery current is both a health signal and the primary experiment observable.",
    )
    # inputs
    inputs = [
        "Pilot command", "Airspeed (pitot)", "Tilt angle ×2", "Vertical velocity",
        "Altitude", "RPM ×4", "Battery voltage", "Battery current",
        "Actuator current", "Roll rate", "Yaw rate", "Vert. acceleration",
    ]
    k.textbox(s, 0.42, 1.18, 3.4, 0.28, "INPUTS", 12, k.CYAN, True, k.MONO)
    for i, t in enumerate(inputs):
        y = 1.50 + i * 0.45
        k.rrect(s, 0.42, y, 3.35, 0.40, k.CARD, k.STROKE)
        k.textbox(s, 0.52, y, 3.15, 0.40, t, 12, k.OFF, False, k.FONT, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE)

    k.card(s, 4.05, 1.50, 5.20, 5.40, k.CYAN)
    k.textbox(s, 4.25, 1.70, 4.8, 0.32, "FLIGHT MODE LOGIC", 14, k.CYAN, True, k.MONO)
    k.bullet_block(s, 4.15, 2.15, 4.9, 4.5, [
        "Hover mixer (quad X / H).",
        "Tilt schedule vs calibrated airspeed.",
        "Front / rear tilt may use a slight split to manage pitch.",
        "Collective reduction as wing lift rises.",
        "Power experiment flag (wing-on / wing-off).",
        "Failsafe overlay (always on).",
        "ArduPilot VTOL state machine + ESP32 inhibit.",
    ], 14)

    k.textbox(s, 9.55, 1.18, 3.4, 0.28, "OUTPUTS", 12, k.AMBER, True, k.MONO)
    outputs = [
        ("Front tilt command", k.CYAN),
        ("Rear tilt command", k.CYAN),
        ("Motor throttle ×4", k.TEAL),
        ("Flight mode logic", k.AMBER),
    ]
    for i, (t, col) in enumerate(outputs):
        y = 1.55 + i * 1.32
        k.card(s, 9.50, y, 3.40, 1.15, col)
        k.textbox(s, 9.65, y + 0.32, 3.1, 0.50, t, 15, k.WHITE, True)
