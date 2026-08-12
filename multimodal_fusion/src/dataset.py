"""
Paired image–text dataset for multimodal fake news detection.

Real-world framing
------------------
Social-media misinformation often pairs a sensational caption with an
unrelated or manipulated image.  This module builds a balanced paired
dataset in which:

* REAL samples have coherent image–text alignment (class visual + matching
  news-style caption).
* FAKE samples have deliberately mismatched image–text pairs and/or
  sensational / contradictory captions.

Images are synthesised programmatically with class-discriminative visual
patterns (public-reproducible, no large download required).  Captions are
curated news-style templates.  Together they form an explicit paired
image–text corpus for fusion experiments.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from torch.utils.data import Dataset
from torchvision import transforms

CLASS_NAMES = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
]

# Distinctive colour palettes per class (RGB)
CLASS_COLORS: Dict[str, Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = {
    "airplane": ((135, 206, 235), (220, 220, 230)),  # sky / metal
    "automobile": ((50, 50, 60), (200, 40, 40)),  # asphalt / red body
    "bird": ((120, 180, 80), (255, 200, 50)),  # foliage / beak yellow
    "cat": ((240, 220, 180), (80, 60, 40)),  # fur / dark
    "deer": ((90, 140, 70), (160, 110, 60)),  # forest / brown
    "dog": ((180, 140, 90), (40, 40, 40)),  # tan / black
    "frog": ((40, 140, 60), (200, 220, 100)),  # green / lily
    "horse": ((150, 110, 70), (100, 160, 80)),  # brown / grass
    "ship": ((20, 60, 120), (180, 200, 220)),  # ocean / hull grey
    "truck": ((70, 70, 80), (255, 160, 0)),  # road / orange
}

REAL_CAPTIONS: Dict[str, List[str]] = {
    "airplane": [
        "Commercial flight takes off on schedule amid clear skies.",
        "Aviation authorities confirm routine passenger aircraft departure.",
        "Airport officials report normal air-traffic operations today.",
        "Passenger jet photographed during a standard runway rollout.",
        "Airlines announce on-time departure for domestic route.",
    ],
    "automobile": [
        "New model sedan unveiled at the annual auto exposition.",
        "City traffic cameras capture regular weekday commute patterns.",
        "Manufacturers report steady sales of compact passenger cars.",
        "Transport department reviews urban vehicle safety standards.",
        "Local dealership showcases latest fuel-efficient automobile.",
    ],
    "bird": [
        "Wildlife photographers document migratory birds at the wetlands.",
        "Conservation group reports healthy bird populations this season.",
        "Ornithologists observe nesting activity in the protected reserve.",
        "Park rangers share images of native birds near the lake.",
        "Researchers track seasonal bird migration along the coast.",
    ],
    "cat": [
        "Animal shelter shares success story of adopted house cat.",
        "Veterinary clinic reports routine checkup for domestic feline.",
        "Pet owners advised on seasonal care for indoor cats.",
        "Community program promotes responsible cat adoption drives.",
        "Local rescue posts update on recovered stray cat health.",
    ],
    "deer": [
        "Forest department monitors deer population in national park.",
        "Wildlife cameras capture deer grazing in protected habitat.",
        "Ecologists study deer movement corridors across woodland areas.",
        "Park visitors reminded to keep distance from wild deer.",
        "Conservation report notes stable deer numbers this quarter.",
    ],
    "dog": [
        "City launches free vaccination camp for pet dogs this week.",
        "K-9 unit completes standard training exercise with service dogs.",
        "Animal welfare NGO highlights successful dog rescue mission.",
        "Veterinary association issues advisory on canine seasonal health.",
        "Community walk event encourages responsible dog ownership.",
    ],
    "frog": [
        "Biologists survey amphibian diversity in monsoon wetlands.",
        "Environmental study documents frog breeding in local ponds.",
        "Researchers note healthy frog habitats after rainfall season.",
        "Ecology students photograph frogs during field observation.",
        "Wetland restoration project supports native frog species.",
    ],
    "horse": [
        "Equestrian event draws riders for weekend championship trials.",
        "Farm report highlights proper care standards for horses.",
        "Police mounted unit conducts routine patrol demonstration.",
        "Rural development program supports horse breeding cooperatives.",
        "Veterinary team completes health screening of stable horses.",
    ],
    "ship": [
        "Port authority confirms smooth cargo ship docking operations.",
        "Coast guard monitors routine maritime traffic near harbour.",
        "Shipping companies report on-time freighter arrivals today.",
        "Naval observers photograph commercial vessel during transit.",
        "Harbour officials oversee standard container ship unloading.",
    ],
    "truck": [
        "Logistics firm expands fleet of heavy transport trucks.",
        "Highway authority reviews freight truck safety compliance.",
        "Supply-chain update shows timely truck deliveries nationwide.",
        "Transport union discusses working conditions for truck drivers.",
        "Municipal project uses dump trucks for road construction work.",
    ],
}

FAKE_CAPTIONS: Dict[str, List[str]] = {
    "airplane": [
        "BREAKING: Secret alien craft lands at major airport — officials silent!",
        "Exclusive: Passenger jet vanishes mid-air, government covers it up!",
        "Shocking leak: Airlines hide toxic cabin air that causes mass illness!",
        "URGENT: Hijacked plane heading toward city — panic spreading online!",
        "Insider claim: Military drones disguised as commercial flights!",
    ],
    "automobile": [
        "Exposed: New cars secretly track and sell your private conversations!",
        "Viral claim: Self-driving cars programmed to prefer certain passengers!",
        "Alert: Contaminated fuel in city cars causes sudden engine explosions!",
        "Scandal: Auto giants hide chips that disable brakes remotely!",
        "Unverified: Celebrity car crash was staged for insurance payout!",
    ],
    "bird": [
        "Conspiracy: Migratory birds are bio-engineered surveillance drones!",
        "Shock claim: Rare bird sightings linked to upcoming natural disaster!",
        "Viral post: Birds falling from sky due to secret weather weapon!",
        "Unproven: Government releasing diseased birds into cities overnight!",
        "Fake alert: Extinct bird species secretly revived in military lab!",
    ],
    "cat": [
        "Hoax: Stray cats spreading engineered virus across neighbourhoods!",
        "Clickbait: Celebrity's cat predicts stock crash — markets panic!",
        "False claim: Pet cats implanted with mind-control microchips!",
        "Rumours: Shelter cats stolen for illegal cloning experiments!",
        "Unverified: Giant mutated cat spotted attacking suburban homes!",
    ],
    "deer": [
        "Panic: Radioactive deer herd escaping from secret research facility!",
        "Fake report: Deer stampede caused by underground nuclear test!",
        "Viral lie: Forest spirits possessing deer caught on camera!",
        "Hoax alert: Contaminated deer meat flooding supermarket chains!",
        "Conspiracy: Military using deer as living chemical detectors!",
    ],
    "dog": [
        "BREAKING hoax: Police dogs replaced by robotic replicas citywide!",
        "False claim: Pet dogs turning aggressive after secret vaccine batch!",
        "Viral rumour: Stray dogs trained to steal phones for gangs!",
        "Unproven: Celebrity dog cloning farm exposed by anonymous leak!",
        "Scare post: Contaminated dog food linked to nationwide outages!",
    ],
    "frog": [
        "Shocking: Giant frogs invading suburbs after chemical spill cover-up!",
        "Fake science: Frogs predicting earthquake that experts deny!",
        "Hoax: Mutant frogs with human DNA released into city water!",
        "Viral claim: Amphibian plague spreading through packaged salads!",
        "Unverified: Secret lab breeding weaponized frogs for warfare!",
    ],
    "horse": [
        "Scandal: Race results fixed using hidden neural implants in horses!",
        "False alert: Plague among horses deliberately spread by rivals!",
        "Viral lie: Wild horses fleeing because of underground bomb tests!",
        "Hoax: Celebrity horse inheritance worth billions — documents forged!",
        "Conspiracy: Military cloning war horses in remote desert bases!",
    ],
    "ship": [
        "BREAKING fake: Ghost ship with no crew spotted near major port!",
        "Unverified: Cargo ship carrying banned bioweapons intercepted!",
        "Hoax: Cruise liner diverted after mysterious passenger disappearances!",
        "Scare claim: Oil tanker leak deliberately covered by authorities!",
        "Viral rumour: Naval vessel firing on civilian boats — denied!",
    ],
    "truck": [
        "False alarm: Fleet of unmanned trucks hijacked across highways!",
        "Clickbait: Toxic chemicals spilling from trucks into city reservoirs!",
        "Hoax: Truck drivers staging nationwide shutdown with no notice!",
        "Unproven: Military trucks moving undisclosed materials at night!",
        "Viral lie: Contaminated goods in trucks causing citywide blackout!",
    ],
}

MISMATCH_CAPTIONS = [
    "Officials deny reports of underwater city discovered beneath downtown.",
    "Anonymous source claims time-travel experiment succeeded last night.",
    "Unverified video shows floating landmark vanishing in broad daylight.",
    "Social media frenzy over rumoured portal opening in city park.",
    "Influencer insists ancient prophecy predicted tonight's blackout.",
]


def _draw_class_icon(draw: ImageDraw.ImageDraw, name: str, box, accent) -> None:
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if name == "airplane":
        draw.polygon([(cx, y0 + 8), (x1 - 6, cy), (cx, y1 - 8), (x0 + 6, cy)], fill=accent)
        draw.rectangle([cx - 3, y0 + 4, cx + 3, y1 - 4], fill=accent)
    elif name == "automobile":
        draw.rectangle([x0 + 8, cy - 6, x1 - 8, cy + 10], fill=accent)
        draw.ellipse([x0 + 12, cy + 6, x0 + 28, cy + 22], fill=(20, 20, 20))
        draw.ellipse([x1 - 28, cy + 6, x1 - 12, cy + 22], fill=(20, 20, 20))
    elif name == "bird":
        draw.ellipse([cx - 14, cy - 10, cx + 14, cy + 12], fill=accent)
        draw.polygon([(cx + 12, cy), (cx + 28, cy - 6), (cx + 12, cy + 4)], fill=(255, 180, 40))
    elif name == "cat":
        draw.ellipse([cx - 16, cy - 8, cx + 16, cy + 16], fill=accent)
        draw.polygon([(cx - 14, cy - 6), (cx - 6, y0 + 6), (cx - 2, cy - 2)], fill=accent)
        draw.polygon([(cx + 2, cy - 2), (cx + 6, y0 + 6), (cx + 14, cy - 6)], fill=accent)
    elif name == "deer":
        draw.ellipse([cx - 12, cy - 4, cx + 12, cy + 16], fill=accent)
        draw.line([(cx - 4, cy - 4), (cx - 14, y0 + 4)], fill=accent, width=3)
        draw.line([(cx + 4, cy - 4), (cx + 14, y0 + 4)], fill=accent, width=3)
    elif name == "dog":
        draw.ellipse([cx - 16, cy - 6, cx + 16, cy + 16], fill=accent)
        draw.ellipse([cx + 8, cy - 14, cx + 22, cy], fill=accent)
    elif name == "frog":
        draw.ellipse([cx - 18, cy - 8, cx + 18, cy + 16], fill=accent)
        draw.ellipse([cx - 14, cy - 14, cx - 4, cy - 4], fill=accent)
        draw.ellipse([cx + 4, cy - 14, cx + 14, cy - 4], fill=accent)
    elif name == "horse":
        draw.rectangle([x0 + 14, cy - 4, x1 - 14, cy + 12], fill=accent)
        draw.polygon([(x1 - 14, cy - 4), (x1 - 2, cy - 16), (x1 - 10, cy + 2)], fill=accent)
    elif name == "ship":
        draw.polygon([(x0 + 8, cy + 4), (x1 - 8, cy + 4), (x1 - 16, y1 - 8), (x0 + 16, y1 - 8)], fill=accent)
        draw.rectangle([cx - 3, y0 + 8, cx + 3, cy + 4], fill=(230, 230, 230))
    else:  # truck
        draw.rectangle([x0 + 6, cy - 8, x1 - 18, cy + 12], fill=accent)
        draw.rectangle([x1 - 18, cy - 2, x1 - 6, cy + 12], fill=accent)
        draw.ellipse([x0 + 12, cy + 8, x0 + 26, cy + 22], fill=(20, 20, 20))
        draw.ellipse([x1 - 30, cy + 8, x1 - 16, cy + 22], fill=(20, 20, 20))


def synthesise_image(class_idx: int, seed: int, size: int = 64) -> Image.Image:
    """Create a class-discriminative synthetic RGB image."""
    rng = random.Random(seed)
    name = CLASS_NAMES[class_idx]
    bg, accent = CLASS_COLORS[name]
    # slight colour jitter
    bg = tuple(max(0, min(255, c + rng.randint(-18, 18))) for c in bg)
    accent = tuple(max(0, min(255, c + rng.randint(-18, 18))) for c in accent)
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)
    # background texture
    for _ in range(rng.randint(8, 20)):
        x, y = rng.randint(0, size - 1), rng.randint(0, size - 1)
        r = rng.randint(2, 8)
        col = tuple(max(0, min(255, c + rng.randint(-30, 30))) for c in bg)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=col)
    margin = rng.randint(6, 12)
    _draw_class_icon(draw, name, (margin, margin, size - margin, size - margin), accent)
    # small label stripe (visual cue, not readable text dependency)
    stripe = tuple(max(0, min(255, c // 2)) for c in accent)
    draw.rectangle([0, size - 6, size, size], fill=stripe)
    return img


def _augment_fake_image(img: Image.Image, rng: random.Random) -> Image.Image:
    img = img.copy()
    ops = [
        lambda x: ImageEnhance.Color(x).enhance(rng.uniform(0.35, 1.9)),
        lambda x: ImageEnhance.Contrast(x).enhance(rng.uniform(0.55, 2.0)),
        lambda x: ImageEnhance.Brightness(x).enhance(rng.uniform(0.65, 1.45)),
        lambda x: x.filter(ImageFilter.GaussianBlur(radius=rng.uniform(0.4, 1.6))),
    ]
    for op in ops:
        if rng.random() < 0.55:
            img = op(img)
    if rng.random() < 0.4:
        draw = ImageDraw.Draw(img)
        w, h = img.size
        for _ in range(rng.randint(1, 3)):
            x0, y0 = rng.randint(0, w - 1), rng.randint(0, h - 1)
            x1, y1 = rng.randint(x0, w - 1), rng.randint(y0, h - 1)
            color = tuple(rng.randint(0, 255) for _ in range(3))
            draw.rectangle([x0, y0, x1, y1], outline=color, width=1)
    return img


@dataclass
class SampleRecord:
    image_label: int
    image_seed: int
    text: str
    target: int  # 0 = real, 1 = fake
    pair_type: str


def build_sample_index(n_samples: int = 4000, seed: int = 42) -> List[SampleRecord]:
    rng = random.Random(seed)
    half = n_samples // 2
    records: List[SampleRecord] = []

    for i in range(half):
        lab = rng.randrange(10)
        text = rng.choice(REAL_CAPTIONS[CLASS_NAMES[lab]])
        records.append(
            SampleRecord(
                image_label=lab,
                image_seed=seed + i,
                text=text,
                target=0,
                pair_type="matched_real",
            )
        )

    for i in range(n_samples - half):
        lab = rng.randrange(10)
        mode = rng.choice(["sensational", "mismatch", "both"])
        if mode == "sensational":
            text = rng.choice(FAKE_CAPTIONS[CLASS_NAMES[lab]])
            pair_type = "sensational_fake"
        elif mode == "mismatch":
            other = rng.choice([j for j in range(10) if j != lab])
            text = rng.choice(REAL_CAPTIONS[CLASS_NAMES[other]])
            pair_type = "mismatched_fake"
        else:
            other = rng.choice([j for j in range(10) if j != lab])
            text = rng.choice(FAKE_CAPTIONS[CLASS_NAMES[other]])
            if rng.random() < 0.3:
                text = rng.choice(MISMATCH_CAPTIONS)
            pair_type = "sensational_mismatch_fake"
        records.append(
            SampleRecord(
                image_label=lab,
                image_seed=seed + 100000 + i,
                text=text,
                target=1,
                pair_type=pair_type,
            )
        )

    rng.shuffle(records)
    return records


class MultimodalFakeNewsDataset(Dataset):
    def __init__(
        self,
        records: List[SampleRecord],
        word2idx: Dict[str, int],
        max_len: int = 32,
        image_transform=None,
        manipulate_fake: bool = True,
        seed: int = 42,
    ):
        self.records = records
        self.word2idx = word2idx
        self.max_len = max_len
        self.image_transform = image_transform or transforms.Compose(
            [
                transforms.Resize((64, 64)),
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            ]
        )
        self.manipulate_fake = manipulate_fake
        self.rng = random.Random(seed)

    def __len__(self) -> int:
        return len(self.records)

    def _tokenize_text(self, text: str) -> torch.Tensor:
        tokens = text.lower().replace("—", " ").replace("-", " ").split()
        ids = [
            self.word2idx.get(t.strip(".,!?:;\"'()"), self.word2idx["<unk>"])
            for t in tokens
        ]
        ids = ids[: self.max_len]
        if len(ids) < self.max_len:
            ids = ids + [self.word2idx["<pad>"]] * (self.max_len - len(ids))
        return torch.tensor(ids, dtype=torch.long)

    def __getitem__(self, i: int):
        rec = self.records[i]
        pil = synthesise_image(rec.image_label, rec.image_seed)
        if self.manipulate_fake and rec.target == 1 and self.rng.random() < 0.6:
            pil = _augment_fake_image(pil, self.rng)
        image = self.image_transform(pil)
        tokens = self._tokenize_text(rec.text)
        label = torch.tensor(rec.target, dtype=torch.long)
        return image, tokens, label, rec.text


def build_vocabulary(texts: List[str], min_freq: int = 1) -> Dict[str, int]:
    from collections import Counter

    counter: Counter = Counter()
    for t in texts:
        tokens = t.lower().replace("—", " ").replace("-", " ").split()
        counter.update(tok.strip(".,!?:;\"'()") for tok in tokens)
    word2idx = {"<pad>": 0, "<unk>": 1}
    for w, c in counter.items():
        if c >= min_freq and w not in word2idx:
            word2idx[w] = len(word2idx)
    return word2idx


def prepare_datasets(
    data_dir: Path,
    n_samples: int = 4000,
    max_len: int = 32,
    seed: int = 42,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
):
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    records = build_sample_index(n_samples=n_samples, seed=seed)
    texts = [r.text for r in records]
    word2idx = build_vocabulary(texts)

    n = len(records)
    n_test = int(n * test_ratio)
    n_val = int(n * val_ratio)
    n_train = n - n_val - n_test

    train_rec = records[:n_train]
    val_rec = records[n_train : n_train + n_val]
    test_rec = records[n_train + n_val :]

    train_ds = MultimodalFakeNewsDataset(train_rec, word2idx, max_len, seed=seed)
    val_ds = MultimodalFakeNewsDataset(
        val_rec, word2idx, max_len, manipulate_fake=True, seed=seed + 1
    )
    test_ds = MultimodalFakeNewsDataset(
        test_rec, word2idx, max_len, manipulate_fake=True, seed=seed + 2
    )

    # Persist a few preview images for the report
    preview_dir = data_dir / "preview_images"
    preview_dir.mkdir(exist_ok=True)
    for i, rec in enumerate(records[:8]):
        img = synthesise_image(rec.image_label, rec.image_seed)
        tag = "real" if rec.target == 0 else "fake"
        img.save(preview_dir / f"sample_{i}_{tag}_{CLASS_NAMES[rec.image_label]}.png")

    meta = {
        "n_samples": n,
        "n_train": n_train,
        "n_val": n_val,
        "n_test": n_test,
        "vocab_size": len(word2idx),
        "max_len": max_len,
        "num_classes": 2,
        "class_names": ["real", "fake"],
        "visual_source": "Programmatically synthesised class-discriminative RGB images (10 object categories)",
        "text_source": "Curated news-style captions (matched / sensational / mismatched)",
        "task": "Multimodal Fake News Detection (Image + Text Fusion)",
        "seed": seed,
        "pair_type_counts": {
            k: sum(1 for r in records if r.pair_type == k)
            for k in sorted({r.pair_type for r in records})
        },
    }
    with open(data_dir / "dataset_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    sample_rows = [
        {
            "label": "fake" if r.target == 1 else "real",
            "pair_type": r.pair_type,
            "image_class": CLASS_NAMES[r.image_label],
            "text": r.text,
        }
        for r in records[:40]
    ]
    with open(data_dir / "sample_preview.json", "w", encoding="utf-8") as f:
        json.dump(sample_rows, f, indent=2)

    return train_ds, val_ds, test_ds, word2idx, meta
