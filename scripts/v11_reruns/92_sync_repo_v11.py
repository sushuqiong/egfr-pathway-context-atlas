#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, shutil
REPO=r"C:\Users\fengq\Desktop\EGFR\egfr-pathway-context-atlas"
V11 =r"C:\Users\fengq\Desktop\EGFR\EGFR的v11"
os.makedirs(os.path.join(REPO,"scripts","v11_reruns"), exist_ok=True)
for f in os.listdir(os.path.join(V11,"reruns","scripts")):
    shutil.copy(os.path.join(V11,"reruns","scripts",f), os.path.join(REPO,"scripts","v11_reruns",f))
for f in os.listdir(os.path.join(V11,"reruns","results")):
    if f.endswith(".csv"): shutil.copy(os.path.join(V11,"reruns","results",f), os.path.join(REPO,"results",f))
shutil.copy(os.path.join(V11,"01_稿件正文","Manuscript_draft_v11.md"), os.path.join(REPO,"manuscript"))
shutil.copy(os.path.join(V11,"04_评审记录与报告","v18_v11_corrections.md"), os.path.join(REPO,"reports"))
p=os.path.join(REPO,"README.md"); s=open(p,encoding="utf-8").read()
note=("\n> **Corrections (v11)**: effect sizes now use one common denominator (unpaired SMDH, matched SMCRPH); "
      "composition is reported as a base-versus-adjusted model comparison; single-cell tests are paired where complete "
      "patient pairs exist with cell-identity contrasts labelled separately; mutation prevalence and driver analyses use "
      "mutation-profiled samples only. See `ERRATA_v11.md`. Headline v11 numbers: per-cohort 55/170; meta REML/Knapp-Hartung "
      "**17** (DL **74**; non-shrinking KH **6**; unpaired-only **3**); composition-robust **21** (CRC 10, STAD 9, ESCC 1, IBD 1; "
      "PAAD 0) with a median adjusted/base coefficient ratio of 0.87; no module passed pre-specified external replication.\n")
s=s.replace("Analysis and reproduction package accompanying the manuscript **v10**.",
            "Analysis and reproduction package accompanying the manuscript **v11**." + note)
s += ("\n## Automated consistency check\n"
      "`python tests/check_v11_consistency.py` verifies that every headline number in the manuscript matches the frozen v11 "
      "result tables, that no superseded numbers reappear, and that citations are sequential and fully cited. "
      "`Rscript tests/check_paired_effect.R` verifies the paired-effect implementation (hand calculation vs metafor, "
      "sample-order shuffle with ID joins, repeated runs).\n")
open(p,"w",encoding="utf-8").write(s)
print("repo files updated")
