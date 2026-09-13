# Experiential Learning: Unstructured Data into a NoSQL Database

**Course:** Big Data Analytics  
**Student:** Sukhada Dhingra  
**PRN:** 24070126505  
**Batch:** A3  
**Institute:** Symbiosis Institute of Technology, Pune  
**Submission PDF:** [report/Sukhada_Dhingra_BDA_Unstructured_Data_NoSQL_MongoDB.pdf](report/Sukhada_Dhingra_BDA_Unstructured_Data_NoSQL_MongoDB.pdf)

This folder contains the unstructured JSON corpus, mongosh scripts, Ubuntu execution transcripts, screenshots, and the official submission report.

## What is in the PDF

- Cover page with **name** Sukhada Dhingra, **PRN** 24070126505 and **Batch A3**
- Theory: unstructured / semi-structured data, document NoSQL, CAP, BSON
- Lab actually executed on **Ubuntu 24.04.4 LTS** + **MongoDB 8.0.32**
  - 300 JSONL product-review documents (schema-less optional fields)
  - `mongoimport` — 300 imported, 0 failed
  - CRUD (count 300 → 301 → 300)
  - Aggregations: `$group` by category, `$match` Pune, `$unwind` tags, `$facet` histogram
- Terminal screenshots of version, JSON sample, createCollection, import, CRUD and aggregations
- Source listings, viva notes, conclusion, references

**PRN 24070126505** and **Batch A3** are printed on the cover, running header, declaration, and identity table.

## Run the lab (optional)

Requires MongoDB Community (`mongod`, `mongosh`, `mongoimport`) on `PATH`.

```bash
# start mongod if it is not already running
mongod --dbpath /var/lib/mongodb --bind_ip 127.0.0.1 --fork --logpath /var/log/mongodb/mongod.log

cd experiential-learning/unstructured-nosql
bash scripts/run_lab.sh
```

## Regenerate the PDF

```bash
python3 report/generate_report.py
```

Needs `reportlab`, `pillow`, and `matplotlib`. Screenshots are rebuilt from the saved transcripts under `results/`.
