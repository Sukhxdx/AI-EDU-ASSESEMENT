# Spark experiential learning — e-commerce sales briefing

**Submission PDF:** [Ecommerce_Sales_Performance_Report_Spark.pdf](Ecommerce_Sales_Performance_Report_Spark.pdf)

Junior-analyst sales report built from `ecommerce_sales_5000.xlsx` with Apache Spark. Tasks 1–8 use the DataFrame API (`groupBy`, `agg`, `withColumn`). Task 9 rebuilds the category briefing in Spark SQL. Task 10 is the management interpretation.

## Headline results (5,000 orders, calendar 2025)

- Revenue **₹9.28 Cr**, profit **₹2.76 Cr**, blended margin **29.76%**
- **Delhi** leads city revenue; **Grocery** leads category revenue; **Rice** is the top product by profit
- Best city/category pair: **Delhi × Sports**
- 845 cancelled orders have zero revenue; the profit-margin column is therefore created with `when` / `otherwise` (and `NULLIF` in SQL)

## Reproduce

```bash
pip install -r requirements.txt
python3 spark_sales_analysis.py
```

Java is required for the local Spark session. The Excel workbook is also stored as `data/ecommerce_sales_5000.csv` so Spark can load it with a standard CSV reader.
