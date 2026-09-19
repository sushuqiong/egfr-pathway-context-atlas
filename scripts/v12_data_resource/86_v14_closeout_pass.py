#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 close-out pass: final text edits applied to the deliverable markdown, plus rebuild of every artefact
(docx/pdf, tables, legends, PDF figures with embedded fonts, inventory/checksums, ZIPs) and the audit."""
import csv, os, re, subprocess, shutil, hashlib, zipfile
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
mdp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mdp,encoding="utf-8").read()
notes=[]
# 1. GSVA citation
if "GSVA7" not in md:
    md=md.replace("in the bulk cohorts it is a GSVA value", "in the bulk cohorts it is a GSVA7 value",1)
    md=md.replace("the bulk layer is a GSVA value", "the bulk layer is a GSVA7 value",1)
    if "GSVA7" in md: notes.append("GSVA citation added")
# 2. abbreviation list in Methods
if "Abbreviations: BH" not in md:
    for anchor in ["*Validation rules.*","*Validation rules and thresholds.*","Validation rules and thresholds."]:
        if anchor in md:
            md=md.replace(anchor, "Abbreviations: BH (Benjamini-Hochberg), FDR (false discovery rate), VIF (variance inflation factor), MAD (median absolute deviation), OS (overall survival), GSVA (gene set variation analysis), SMDH (standardized mean difference, Hedges), SMCRPH (standardized mean change paired with empirical correlation).\n"+anchor,1)
            notes.append("abbreviation list added"); break
# 3. limitations: HCC control samples + zero-variance note
if "five control samples" not in md:
    for anchor in ["no minimum number of cells per donor was imposed","No minimum number of cells per donor was imposed"]:
        if anchor in md:
            md=md.replace(anchor, "one cohort (GSE62232, hepatocellular carcinoma) contributes only five control samples; zero-variance genes are absent by construction (matrices were filtered before scoring), which is why that QC column is zero for every cohort; "+anchor,1)
            notes.append("limitations extended"); break
# 4. file count from the inventory
inv=rd=None
def _rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
inv=_rd(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"))
n_files=len(inv); n_checks=len([r for r in inv if len(str(r["sha256"]))==64])
md=re.sub(r"is shipped \(\d+ files\)", f"is shipped ({n_files} files, with {n_checks} SHA-256 entries because the two verification files are self-referential)", md)
open(mdp,"w",encoding="utf-8").write(md)
print("text edits:", notes or "none", "| file count in text: ", n_files, "/", n_checks)
# 5. PDF figures with embedded fonts (cairo) - regenerate the PDFs only
r=subprocess.run([r"D:\R-4.4.1\bin\Rscript.exe","-e",
    'suppressPackageStartupMessages(library(ggplot2)); cat("cairo:", capabilities("cairo"), "\\n")'],
    capture_output=True,text=True)
print("cairo capability:", (r.stdout or r.stderr).strip()[:80])
# 6. rebuild docx / pdf / tables / legends / zips / checksums
for script in ["71_v14_tables_legends.py","72_v14_finalise.py"]:
    rr=subprocess.run([os.sys.executable, os.path.join(V14,"scripts",script)],capture_output=True,text=True)
    tail=[l for l in (rr.stdout or "").strip().splitlines() if l.strip()][-1:]
    print(f"[{script}] {tail[0][:110] if tail else ''}")
rr=subprocess.run([os.sys.executable, os.path.join(V14,"scripts","75_v14_checksum_tidy.py")],capture_output=True,text=True)
print("checksum:", [l for l in rr.stdout.splitlines() if "non-OK" in l or "verified" in l or "zenodo" in l][:3])
# 7. audit
rr=subprocess.run([os.sys.executable, os.path.join(V14,"scripts","72_v14_finalise.py")],capture_output=True,text=True)
print([l for l in rr.stdout.splitlines() if l.startswith(("passed:","issues:","  ISSUE"))][:6])
