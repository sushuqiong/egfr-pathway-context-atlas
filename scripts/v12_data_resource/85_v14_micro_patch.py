#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 micro-patch: remaining manuscript citations/abbreviations/limitations plus small data-file corrections."""
import os, re, csv
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; PK=os.path.join(V14,"dataset_package")
p=os.path.join(V14,"scripts","70_v14_manuscript.py"); s=open(p,encoding="utf-8").read()
applied=[]
# 1. GSVA citation by pattern
m=re.search(r"GSVA value", s)
if m and "GSVA7 value" not in s:
    s=s[:m.start()]+"GSVA7 value"+s[m.end():]; applied.append("cite GSVA (pattern)")
# 2. abbreviation list before the validation-rules paragraph
for anchor in ["*Validation rules and thresholds.*","*Validation rules.* Reported checks","Validation rules and thresholds."]:
    if anchor in s:
        s=s.replace(anchor, "Abbreviations: BH (Benjamini-Hochberg), FDR (false discovery rate), VIF (variance inflation factor), MAD (median absolute deviation), OS (overall survival), GSVA (gene set variation analysis), SMDH (standardized mean difference, Hedges), SMCRPH (standardized mean change, paired).\n"+anchor,1)
        applied.append("abbreviations via "+anchor); break
# 3. limitations sentence (pattern on the cells-per-donor phrase)
mm=re.search(r"no minimum number of cells per donor was imposed[;.]", s)
if mm:
    ins=("one cohort (GSE62232, hepatocellular carcinoma) contributes only five control samples; zero-variance genes are absent by construction, "
         "which is why that QC column is zero everywhere; ")
    s=s[:mm.start()]+ins+s[mm.start():]; applied.append("limitations (pattern)")
open(p,"w",encoding="utf-8").write(s); print("applied:",applied if applied else "none")
# 4. small data corrections
demo=os.path.join(PK,"09_reuse_examples","example1_replace_module_gene_set.R")
t=open(demo,encoding="utf-8").read().replace("1500 genes x 20 samples","1298 genes x 20 samples (a real subset of GSE13911)").replace("# Input:","# Input:")
open(demo,"w",encoding="utf-8").write(t)
mfile=os.path.join(PK,"09_reuse_examples","README_examples.md")
t=open(mfile,encoding="utf-8").read()
if "real subset" not in t:
    t=t.rstrip()+("\n\n## Note on the demo matrix\n\nThe demo matrix shipped for example 1 is a real 1,298-gene x 20-sample subset of GSE13911 (its GSM identifiers match the sample annotation table),\n"
                  "not synthetic data; `demo_sample_metadata.csv` carries the corresponding sample identifiers and case/control labels.\n")
    open(mfile,"w",encoding="utf-8").write(t); print("demo note added")
# coverage sensitivity: add the number of pairs excluded by each threshold
cs=os.path.join(PK,"08_qc","qc_coverage_threshold_sensitivity.csv")
rows=list(csv.DictReader(open(cs,encoding="utf-8-sig")))
base=[r for r in rows if r["scenario"]=="all cohorts"]
base_pairs=int(base[0]["k"]) if base and base[0].get("k","").isdigit() else None
for r in rows:
    r["cohort_module_pairs_pooled"]=r.get("k","")
    r["note"]="threshold applied to the module coverage of each cohort-module pair" if "coverage" in r["scenario"] else "reference scenario (no threshold)"
with open(cs,"w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator="\n"); w.writeheader(); w.writerows(rows)
print("coverage sensitivity annotated")
# driver denominators: document the universe mismatch explicitly
dp=os.path.join(PK,"07_estimates","driver_eligibility.csv")
if os.path.exists(dp):
    drows=list(csv.DictReader(open(dp,encoding="utf-8-sig")))
    for r in drows:
        r["denominator_note"]=("mutation-profiled universe from the source study; excluded_not_profiled counts samples outside it and is therefore disjoint from n_analysed "
                               "only when the two tables use the same release - they are reported side by side here for transparency")
    with open(dp,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(drows[0].keys()),lineterminator="\n"); w.writeheader(); w.writerows(drows)
    print("driver eligibility annotated")
