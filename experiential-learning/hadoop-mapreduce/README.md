# Experiential Learning: Hadoop MapReduce Paradigm

**Course:** Big Data Analytics  
**Student:** Sukhada Dhingra  
**Institute:** Symbiosis Institute of Technology, Pune  
**Submission PDF:** [report/Sukhada_Dhingra_BDA_Hadoop_MapReduce_Experiential_Learning.pdf](report/Sukhada_Dhingra_BDA_Hadoop_MapReduce_Experiential_Learning.pdf)

This folder contains the Java MapReduce programs, datasets, execution screenshots, and the official 18-page submission report.

## What is in the PDF

- Cover page with **name** Sukhada Dhingra and **PRN** 24070126505 on the cover, header, declaration, and identity table
- Theory: Big Data, HDFS, YARN, MapReduce (map → shuffle/sort → reduce)
- Two jobs actually executed on **Apache Hadoop 3.5.0** + **OpenJDK 21**
  - `WordCount` — 316 map records, 197 distinct words
  - `SalesAnalysis` — grocery 170, electronics 125, clothing 82
- Seven terminal screenshots of version, compile, job SUCCESS, and `part-r-00000`
- Source listings, counters, charts, viva notes, conclusion, references

**PRN 24070126505** is printed on the cover, running header, declaration, and identity table.

## Run the jobs (optional)

Requires JDK 11+ and Hadoop 3.x on `PATH` with `JAVA_HOME` set.

```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64   # adjust
export HADOOP_HOME=/path/to/hadoop-3.5.0
export PATH="$HADOOP_HOME/bin:$PATH"

cd experiential-learning/hadoop-mapreduce
hadoop com.sun.tools.javac.Main -d work src/WordCount.java
jar cf work/wordcount.jar -C work WordCount.class \
  -C work 'WordCount$TokenizerMapper.class' \
  -C work 'WordCount$IntSumReducer.class'
rm -rf work/output_wc
hadoop jar work/wordcount.jar WordCount data work/output_wc
# WordCount reads any files in the input directory; copy the text corpus first:
# mkdir -p work/input_wc && cp data/hadoop_intro.txt work/input_wc
# hadoop jar work/wordcount.jar WordCount work/input_wc work/output_wc
cat work/output_wc/part-r-00000
```

## Regenerate the PDF

```bash
python3 report/generate_report.py
```

Needs `reportlab`, `pillow`, and `matplotlib`. Screenshots are rebuilt from the saved job outputs under `work/output_*`.
