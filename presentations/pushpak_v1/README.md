# Pushpak V1 — Design Review Presentation

40-slide final-year engineering design review for **Pushpak V1**, a 4.5 kg tilt-rotor VTOL UAV demonstrator.

## Deliverable

- `Pushpak_V1_Tilt_Rotor_VTOL_UAV_Design_Review.pdf` — **use this on Mac** (Preview / Safari)
- `Pushpak_V1_Tilt_Rotor_VTOL_UAV_Design_Review.pptx` — widescreen 16:9 (needs Microsoft PowerPoint or Keynote; Preview cannot open `.pptx`)

Team on the title and close slides:

| Name | PRN |
|---|---|
| Ishaan Bafna | 23070125017 |
| Aman Ravat | 23070125004 |
| Krit Verma | 230701250 |

## Rebuild

```bash
cd presentations/pushpak_v1
python3 charts.py
python3 build_presentation.py
```

Requires: `python-pptx`, `matplotlib`, `numpy`, `Pillow`.
