# Image + Text Data Fusion — Multimodal Fake News Detection

**Subject:** MAI (Multimodal AI)  
**Student:** Sukhda Dhingra · **PRN:** 24070126505 · **Batch:** A3

## Real-world problem

Detect whether a social-media style post is **REAL** or **FAKE** by fusing:

- **Image** – post photograph (synthesised class-discriminative RGB images)
- **Text** – caption / claim (curated news-style paired text)

Fake samples use sensational captions, out-of-context (mismatched) image–text pairs, and mild visual edits.

## Fusion strategies

| Model | Description |
|-------|-------------|
| Image-only | CNN baseline |
| Text-only | BiGRU baseline |
| Early fusion | Concatenate embeddings → MLP |
| Late fusion | Average modality probabilities |
| Hybrid fusion | Learnable gates + concat |

## Quick start

```bash
cd multimodal_fusion
pip install -r requirements.txt
python run_experiment.py --n-samples 4000 --epochs 8
python generate_pdf_report.py
```

Outputs:

- `outputs/experiment_results.json` — metrics
- `figures/*.png` — curves, ROC, confusion matrices
- `outputs/Sukhda_Dhingra_24070126505_MAI_Image_Text_Fusion_Report.pdf` — assignment report

## Project layout

```
multimodal_fusion/
├── run_experiment.py
├── generate_pdf_report.py
├── requirements.txt
├── src/
│   ├── dataset.py
│   ├── models.py
│   └── train.py
├── data/
├── figures/
├── models/
└── outputs/
```
