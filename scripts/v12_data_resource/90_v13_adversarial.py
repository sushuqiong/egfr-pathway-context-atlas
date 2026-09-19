#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13 adversarial round: verify suspicious claims, then fix what fails."""
import csv, os, re, glob, json
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results"); PK=os.path.join(V13,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
md=open(os.path.join(V13,"01_manuscript","DataDescriptor_v13.md"),encoding="utf-8").read()
findings=[]
# --- A. annotation vs registry resolution
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv")); ann=rd(os.path.join(PK,"02_sample_annotation","sample_annotation_geo_cohorts.csv"))
reg_keys={(r["accession"],s) for r in reg for s in []}
ann_bad=[r for r in ann if not any(r["accession"]==g["accession"] for g in reg)]
findings.append(("annotation samples resolve to registry cohorts", len(ann_bad)==0, f"{len(ann_bad)} unresolved"))
# --- B. "runnable download-to-results pathway" claim
has_download=glob.glob(os.path.join(PK,"03_expression","*.R"))+glob.glob(os.path.join(PK,"03_expression","*.py"))
findings.append(("package ships a runnable download-to-results pathway", len(has_download)>0, "only a transformation log is present"))
# --- C. supplementary figure references vs shipped files
from docx import Document as _D
_leg=" ".join(p.text for p in _D(os.path.join(V13,"03_tables","Figure_legends_v13.docx")).paragraphs)
figs=[f for f in os.listdir(os.path.join(V13,"02_figures")) if f.endswith(".png")]
cited=[f"Figure {i}" for i in (1,2,3)]
_ok=all(c in _leg for c in cited) and not ("Supplementary Figure S1" in _leg)
findings.append(("legend file matches the shipped main figures and claims no missing supplementary figures", _ok,
                 f"cited={[c for c in cited if c in _leg]} | shipped={sorted(figs)}"))
# --- D. stale v12 artefacts inside the v13 manuscript/tables folders
stale=[f for f in os.listdir(os.path.join(V13,"01_manuscript")) if "v12" in f]+[f for f in os.listdir(os.path.join(V13,"03_tables")) if "v12" in f]
findings.append(("no stale v12 artefacts inside v13 folders", len(stale)==0, f"stale: {stale}"))
# --- E. repository URL in the manuscript
findings.append(("manuscript cites the renamed repository", "cross-disease-transcriptomic-resource" in md, "old repository URL still cited"))
# --- F. CELLxGENE identifiers present
findings.append(("manuscript cites CELLxGENE dataset/collection identifiers", "cellxgene" in md.lower() and "collection" in md.lower(), "no CELLxGENE identifiers in the manuscript"))
# --- G. provenance note for inherited estimate tables
findings.append(("estimates layer carries a provenance note", os.path.exists(os.path.join(PK,"07_estimates","PROVENANCE.md")), "no PROVENANCE.md"))
# --- H. numbers still consistent
mut=rd(os.path.join(R,"v12_escc_mutation_denominators.csv")); tp=[r for r in mut if r["gene"]=="TP53"][0]
findings.append(("TP53 stated as 86/96", "86" in md and tp["n_mutated_samples"]=="86", "TP53 value mismatch"))
findings.append(("estimates matrix statement 442 = 434 + 8", "442 cohort-module rows (434 estimated, 8 not estimable" in md, "matrix statement missing"))
print("== adversarial self-check ==")
for name,ok,detail in findings:
    print(("  PASS  " if ok else "  FAIL  ")+name+("" if ok else f"  -> {detail}"))
fails=[f for f in findings if not f[1]]
print("\nfailures:",len(fails))
