#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
P=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\01_稿件正文\Manuscript_draft_v11.md"
s=open(P,encoding="utf-8").read()
pairs=[
 ("scored by GSVA (Gaussian kernel, minSize \\u2265 3).","scored by GSVA (Gaussian kernel, minSize \\u2265 3) [44]."),
 ("Differential testing used limma eBayes with a matched-patient factor for the twelve matched cohorts.",
  "Differential testing used limma eBayes with a matched-patient factor for the twelve matched cohorts [45]."),
 ("Effect sizes were computed with metafor so that paired and unpaired cohorts share the same standardization denominator",
  "Effect sizes were computed with metafor [46] so that paired and unpaired cohorts share the same standardization denominator"),
 ("DerSimonian-Laird pooling and the non-shrinking Knapp-Hartung variant were computed as sensitivity analyses",
  "DerSimonian-Laird pooling [47] and the non-shrinking Knapp-Hartung variant were computed as sensitivity analyses"),
 ("Tissue composition was estimated by xCell v1.1.0 (64 immune/stromal cell types plus ImmuneScore)",
  "Tissue composition was estimated by xCell v1.1.0 [48] (64 immune/stromal cell types plus ImmuneScore)"),
 ("with a factor-loading nearest-centroid rule derived from published PDAC subtype programs",
  "with a factor-loading nearest-centroid rule derived from published PDAC subtype programs [49,50,51]"),
]
missing=[]
for a,b in pairs:
    if a in s: s=s.replace(a,b,1)
    else: missing.append(a[:70])
# abstract trim to <=255 words
s=s.replace("but how they compare across diseases, how much of a bulk signal reflects tissue composition, and whether surviving signals replicate remain unclear.",
            "but how they compare across diseases, how much bulk signal reflects tissue composition, and whether surviving signals replicate remain unclear.")
s=s.replace("TCGA module-OS associations (108 tests) were assessed with age/stage sensitivity, a driver screen restricted to mutation-profiled samples, and external validation in independent cohorts with tissue-type and stage correction.",
            "TCGA module-OS associations (108 tests) were assessed with age/stage sensitivity, a driver screen restricted to mutation-profiled samples, and external validation with tissue-type and stage correction.")
s=s.replace("Single-cell analysis yielded 16 same-cell-type comparisons (10 paired, median 15 pairs) and 12 separately labelled cell-identity contrasts.",
            "Single-cell analysis yielded 16 same-cell-type comparisons (10 paired; median 15 pairs) and 12 labelled cell-identity contrasts.")
s=re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1),16)), s)
open(P,"w",encoding="utf-8").write(s)
print("missing anchors:", missing if missing else "none")
w=len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1)))
print("abstract words:", w)
body,_,ref=s.partition("## References")
def expand(t):
    out=[]
    for part in t.split(","):
        part=part.strip()
        if "-" in part:
            a,b=part.split("-"); out+=list(range(int(a),int(b)+1))
        else: out.append(int(part))
    return out
order=[]
for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
    for v in expand(m.group(1)):
        if v not in order: order.append(v)
rn=[int(m.group(1)) for l in ref.splitlines() if (m:=re.match(r"\s*(\d+)\.",l))]
print("cited:",len(order),"of",len(rn),"| violations:",sum(1 for i in range(1,len(order)) if order[i]<order[i-1]),
      "| uncited:",[n for n in rn if n not in set(order)])
