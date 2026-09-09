# CA2: Concept-to-Application Mind Map

**Student:** Sukhada Dhingra  
**Programme:** B.Tech. (Artificial Intelligence and Machine Learning)  
**Institute:** Symbiosis Institute of Technology, Pune  
**Assessment:** CA2 — Concept-to-Application Mind Map  
**Date:** 9 September 2026  
**Mode:** Online submission

## Submit these files

- `Sukhada_Dhingra_CA2_Concept_to_Application_MindMap.pdf` — print-ready A2 landscape poster (use this for LMS upload)
- `Sukhada_Dhingra_CA2_Concept_to_Application_MindMap.png` — same poster as an image, if the portal wants a picture

## Fill in your PRN before upload

The PRN is left as a dotted field on the letterhead (it is not a public identifier).

1. Open `poster.html` in a text editor.
2. Find the line with `class="prn"` and type your PRN inside the span.
3. Run `bash generate_poster.sh` to rebuild the PDF and PNG.

## What the poster covers

Two-track mind map from one graph `G = (V, E)`:

1. Node embeddings  
2. Shallow embeddings  
3. Random walk  
4. node2vec  
5. Link analysis  
6. PageRank  
7. Label propagation  

Each node of the map follows **concept → method/formula → application**. The running example is an original **SIT Fest Collaboration Graph** (six committees, nine working edges), not a copied textbook figure.

## Rebuild

```bash
bash generate_poster.sh
```

Requires Google Chrome (headless).
