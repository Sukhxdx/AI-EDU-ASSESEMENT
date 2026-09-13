#!/usr/bin/env bash
# Execute the unstructured-data → MongoDB lab on Ubuntu and save raw transcripts.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATASET="$ROOT/dataset/product_reviews.jsonl"
RESULTS="$ROOT/results"
QUERIES="$ROOT/scripts/queries.js"
URI="mongodb://127.0.0.1:27017"

mkdir -p "$RESULTS"
rm -f "$RESULTS"/*

echo "== generate dataset =="
python3 "$ROOT/scripts/generate_dataset.py" | tee "$RESULTS/00_dataset_stats.txt"

echo "== mongod / mongosh versions =="
{
  echo "$ mongod --version | head -4"
  mongod --version | head -4
  echo
  echo "$ mongosh --version"
  mongosh --version
  echo
  echo "$ mongoimport --version | head -1"
  mongoimport --version | head -1
  echo
  echo "$ lsb_release -d && uname -srm"
  lsb_release -d
  uname -srm
  echo
  echo "$ mongosh --quiet --eval 'db.runCommand({ping:1})'"
  mongosh --quiet --eval 'printjson(db.runCommand({ping:1})); print("db.version() = " + db.version())'
} | tee "$RESULTS/01_versions.txt"

echo "== peek unstructured JSON (first 2 docs, pretty) =="
{
  echo "$ python3 - <<'PY'   # pretty-print first two JSONL records"
  DATASET="$DATASET" python3 - <<'PY'
import json, os
from pathlib import Path
p = Path(os.environ["DATASET"])
for i, line in enumerate(p.read_text().splitlines()[:2], 1):
    print(f"--- document {i} ---")
    print(json.dumps(json.loads(line), indent=2, ensure_ascii=False))
PY
} | tee "$RESULTS/02_sample_json.txt"

echo "== create database + collection =="
{
  echo "$ mongosh $URI --file scripts/setup.js"
  mongosh --quiet "$URI" --file "$ROOT/scripts/setup.js"
} | tee "$RESULTS/03_setup.txt"

echo "== mongoimport unstructured JSONL =="
{
  echo "$ mongoimport --uri $URI --db sit_bda --collection product_reviews --file dataset/product_reviews.jsonl"
  mongoimport --uri "$URI" \
    --db sit_bda \
    --collection product_reviews \
    --file "$DATASET"
} 2>&1 | tee "$RESULTS/04_mongoimport.txt"

echo "== mongosh query script =="
{
  echo "$ mongosh $URI --file scripts/queries.js"
  mongosh --quiet "$URI" --file "$QUERIES"
} | tee "$RESULTS/05_mongosh_queries.txt"

echo "== export aggregation tables =="
mongosh --quiet "$URI" --eval '
db = db.getSiblingDB("sit_bda");
printjson(db.product_reviews.aggregate([
  {$group:{_id:"$product.category", n:{$sum:1}, avg:{$avg:"$rating"}}},
  {$sort:{n:-1}},
  {$project:{_id:0, category:"$_id", n:1, avg:{$round:["$avg",2]}}}
]).toArray());
' | tee "$RESULTS/06_category_agg.json"

echo "lab transcripts written under $RESULTS"
