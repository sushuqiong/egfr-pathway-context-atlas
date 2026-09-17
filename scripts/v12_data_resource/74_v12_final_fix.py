#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12 final fix pass: fill origin PMIDs, rebuild manuscript (captions + refreshed counts),
rebuild docx/pdf/zips, and re-run both audits."""
import csv, os, subprocess, shutil, sys
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results"); PK=os.path.join(V12,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p):
    with open(p,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# 1. PMIDs
pm={r["accession"]:(r.get("pubmed_id",""),r.get("first_author_year","")) for r in rd(os.path.join(PK,"01_cohort_registry","TableS1b_cohort_pubmed_map.csv"))}
for p in [os.path.join(PK,"01_cohort_registry","cohort_registry.csv"), os.path.join(R,"v12_cohort_registry.csv")]:
    rows=rd(p)
    for r in rows:
        pid,fa=pm.get(r["accession"],("",""))
        r["origin_pmid"]=pid; r["origin_reference"]=fa
    wr(rows,p)
print("PMIDs filled:",sum(1 for r in rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv")) if r["origin_pmid"]))
# 2. rebuild manuscript (refreshes inventory count and adds captions)
print(subprocess.run([sys.executable, os.path.join(V12,"scripts","71_v12_md_final.py")],capture_output=True,text=True).stdout.strip())
# 3. rebuild docx/pdf/zips
print(subprocess.run([sys.executable, os.path.join(V12,"scripts","80_build_docx_zip.py")],capture_output=True,text=True).stdout.strip())
pdf=os.path.join(V12,"01_manuscript","DataDescriptor_v12.pdf")
if os.path.exists(pdf): os.remove(pdf)
subprocess.run([r"C:\Program Files\LibreOffice\program\soffice.exe","--headless","--convert-to","pdf",
                "--outdir",os.path.join(V12,"01_manuscript"),os.path.join(V12,"01_manuscript","DataDescriptor_v12.docx")],
               capture_output=True)
print("pdf rebuilt:", os.path.exists(pdf))
# 4. re-run audits
for s in ["90_v12_checks.py","91_v12_lowlevel_audit.py"]:
    r=subprocess.run([sys.executable, os.path.join(V12,"scripts",s)],capture_output=True,text=True)
    tail=[l for l in r.stdout.strip().splitlines() if l.startswith(("issues:","  ISSUE","passed:"))]
    print(s,"->"," | ".join(tail))
