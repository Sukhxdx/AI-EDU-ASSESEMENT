#!/usr/bin/env python3
"""Generate a schema-less product-review JSONL corpus for the MongoDB lab."""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dataset" / "product_reviews.jsonl"

RNG = random.Random(24070126505)

PRODUCTS = [
    ("EL-8821", "Noise-cancelling headphones", "SonicPulse", "electronics", 8999),
    ("EL-4410", "USB-C power bank 20000mAh", "VoltNest", "electronics", 2499),
    ("EL-1102", "Wireless mouse", "Clickora", "electronics", 799),
    ("EL-9904", "Bluetooth speaker", "BoomKart", "electronics", 3299),
    ("GR-2201", "Organic basmati rice 5kg", "Annapurna Mills", "grocery", 649),
    ("GR-3308", "Cold-pressed coconut oil 1L", "KeraHarvest", "grocery", 429),
    ("GR-1180", "Dark chocolate 70%", "CacaoLane", "grocery", 199),
    ("CL-5501", "Cotton oversized tee", "StreetMint", "clothing", 899),
    ("CL-7720", "Running shorts", "PaceForm", "clothing", 1299),
    ("CL-6403", "Denim jacket", "IndigoYard", "clothing", 2499),
    ("BE-4102", "Vitamin C serum", "GlowTheory", "beauty", 1199),
    ("BE-8807", "SPF 50 sunscreen", "Sunveil", "beauty", 649),
    ("BK-1022", "Introduction to Big Data", "SIT Press", "books", 750),
    ("BK-3341", "NoSQL Distilled", "DataCraft", "books", 899),
    ("HM-2210", "Ceramic coffee mug", "HearthCo", "home", 349),
]

CITIES = ["Pune", "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata"]
CHANNELS = ["android-app", "ios-app", "web", "marketplace-api", "email-ingest"]
LANGUAGES = ["en", "en", "en", "hi", "mr"]
HANDLES = [
    "neha_pune", "arjun.k", "meera_reads", "rahul_tech", "isha.m",
    "dev_codes", "priya_skincare", "kabir.s", "ananya_fit", "omkar_grocery",
    "sara.b", "vivek_audio", "tanya_style", "aditya.r", "kavya_home",
]
TITLES = [
    "Worth the money", "Not what I expected", "Daily driver now",
    "Packaging was crushed", "Would buy again", "Average, nothing special",
    "Exceeded expectations", "Returned after a week", "Gift that landed well",
    "Battery life is the story", "Too pricey for the quality",
]
BODIES = [
    "Used it on a Pune–Delhi flight. Noise cancel worked, battery lasted the whole hop.",
    "The description promised organic certification but the packet had no FSSAI hologram.",
    "Fits oversized as advertised. Washed twice, no shrink. Colour is slightly darker in person.",
    "Mouse stuttered on Ubuntu 24.04 until I switched the USB receiver to a front port.",
    "Serum feels light. Saw less dullness after 10 days. Bottle leaked once in the gym bag.",
    "Rice grains were long and did not clump. One stone in the 5kg pack though.",
    "Speaker is loud for the size. Bass distorts above 70 percent volume.",
    "Book is a clean intro. Chapter on CAP theorem helped before the MongoDB lab.",
    "Sunscreen pills on the nose. Fine for office AC, not for a noon cricket match.",
    "Mug handle is thick and comfortable. Print started fading after the dishwasher.",
    "Power bank charged a phone 4 times. Gets warm. Cable in the box is short.",
    "Jacket sizing runs small. Exchanged for L. Stitching on the cuff was loose.",
    "Chocolate bloomed because the courier left it in the sun. Taste still decent.",
    "Headphones pairing on Android was instant. iOS needed a reset once.",
    "Delivery note said 2-day but it took 6. Product itself is okay.",
]
TAGS_POOL = [
    "battery", "travel", "noise-cancel", "fit", "packaging", "value",
    "organic", "ubuntu", "delivery", "gift", "return", "fading", "loud",
    "lab-prep", "skin", "sizing", "warm", "hologram", "bluetooth",
]
SELLER_REPLIES = [
    "Sorry about the hologram — we will ship a replacement batch.",
    "Glad the chapter helped. Do leave an ISBN photo if the print is blurry.",
    "We have flagged the courier delay with the Pune hub.",
    "Please share a short video of the stutter and we will RMA the dongle.",
]


def maybe(p: float) -> bool:
    return RNG.random() < p


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone(timedelta(hours=5, minutes=30))).strftime(
        "%Y-%m-%dT%H:%M:%S+05:30"
    )


def build_doc(i: int) -> dict:
    sku, name, brand, category, price = RNG.choice(PRODUCTS)
    rating = RNG.choices([1, 2, 3, 4, 5], weights=[8, 10, 18, 32, 32])[0]
    captured = datetime(2026, 1, 4, 9, 0) + timedelta(
        days=RNG.randint(0, 240), minutes=RNG.randint(0, 24 * 60)
    )
    city = RNG.choice(CITIES)
    doc: dict = {
        "review_id": f"REV-{i:04d}",
        "captured_at": iso(captured),
        "channel": RNG.choice(CHANNELS),
        "product": {
            "sku": sku,
            "name": name,
            "brand": brand,
            "category": category,
        },
        "customer": {
            "handle": RNG.choice(HANDLES),
            "city": city,
        },
        "rating": rating,
        "body": RNG.choice(BODIES),
        "language": RNG.choice(LANGUAGES),
    }

    # schema-less variation — fields appear only on some documents
    if maybe(0.72):
        doc["title"] = RNG.choice(TITLES)
    if maybe(0.80):
        doc["tags"] = sorted(RNG.sample(TAGS_POOL, k=RNG.randint(1, 4)))
    if maybe(0.55):
        doc["customer"]["verified_purchase"] = maybe(0.7)
    if maybe(0.40):
        doc["helpful_votes"] = RNG.randint(0, 48)
    if maybe(0.22):
        doc["media"] = [{"type": "image", "n": RNG.randint(1, 3)}]
    if maybe(0.18):
        doc["product"]["mrp_inr"] = price
    if maybe(0.12) and rating <= 2:
        doc["return_reason"] = RNG.choice(
            ["damaged", "not-as-described", "sizing", "late-delivery"]
        )
    if maybe(0.10):
        doc["seller_reply"] = {
            "at": iso(captured + timedelta(hours=RNG.randint(4, 72))),
            "text": RNG.choice(SELLER_REPLIES),
        }
    if maybe(0.08):
        doc["ingest_meta"] = {
            "source_file": f"dump_{captured.strftime('%Y%m%d')}.json",
            "parser": "reviews-etl-v3",
            "malformed_keys_dropped": RNG.randint(0, 3),
        }
    if maybe(0.15):
        # extra nested junk that a relational schema would reject
        doc["raw_payload_excerpt"] = {
            "ua": "Mozilla/5.0 Ubuntu",
            "ip_region": city,
            "stars_text": f"{rating} stars",
        }
    return doc


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    docs = [build_doc(i) for i in range(1, 301)]
    with OUT.open("w", encoding="utf-8") as fh:
        for doc in docs:
            fh.write(json.dumps(doc, ensure_ascii=False) + "\n")
    keys = {}
    for d in docs:
        for k in d:
            keys[k] = keys.get(k, 0) + 1
    print(f"wrote {len(docs)} documents → {OUT}")
    print("field presence (schema-less):")
    for k, n in sorted(keys.items(), key=lambda kv: -kv[1]):
        print(f"  {k:22s} {n:3d}/300  ({100*n/300:.0f}%)")


if __name__ == "__main__":
    main()
