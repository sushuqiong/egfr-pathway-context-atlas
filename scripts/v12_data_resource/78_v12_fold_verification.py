#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12: fold the module-score/effect reprodubility check into the package and manuscript, rebuild outputs."""
import csv, os, shutil, subprocess, sys, hashlib
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results"); PK=os.path.join(V12,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
# 1. package QC
shutil.copy(os.path.join(R,"v12_qc_module_score_effect_verification.csv"),
            os.path.join(PK,"08_qc","qc_module_score_and_effect_verification.csv"))
v=rd(os.path.join(R,"v12_qc_module_score_effect_verification.csv"))
maxdiff=max(float(r["abs_diff"]) for r in v); n_cmp=len(v); cohorts=sorted({r["accession"] for r in v})
print("verification: rows",n_cmp,"cohorts",cohorts,"max abs diff",maxdiff)
# 2. manuscript
p=os.path.join(V12,"01_manuscript","DataDescriptor_v12.md"); s=open(p,encoding="utf-8").read()
add=(f" *Score and effect reproducibility:* module scores were independently recomputed from the processed matrices for three further "
     f"cohorts ({', '.join(cohorts)}; 69, 196 and 236 samples) and matched the shipped per-sample scores exactly (Spearman = 1.00 for every module), "
     f"and the {n_cmp} corresponding cohort effect sizes and standard errors were reproduced to a maximum absolute difference of "
     f"{maxdiff:g} (Supplementary Table S5 and 08_qc/qc_module_score_and_effect_verification.csv).")
anchor=" *Composition reproducibility:*"
s=s.replace(anchor, add+"\n"+anchor, 1)
s=s.replace("and representative effect sizes were reproduced by independent calculation and after shuffling sample order.",
            "and effect sizes were reproduced by independent calculation for three cohorts, by recomputing module scores and effects from the source matrices (exact agreement), and after shuffling sample order.")
open(p,"w",encoding="utf-8").write(s)
print("manuscript updated:", "Score and effect reproducibility" in s)
# 3. inventory + checksums
inv=[]
for d0,_,fn in os.walk(PK):
    for f in sorted(fn):
        fp=os.path.join(d0,f); rel=os.path.relpath(fp,PK); h=hashlib.sha256()
        with open(fp,"rb") as fh:
            for c in iter(lambda: fh.read(1<<20), b""): h.update(c)
        nrows=""
        if f.lower().endswith(".csv"):
            try: nrows=sum(1 for _ in open(fp,encoding="utf-8-sig"))-1
            except Exception: nrows=""
        inv.append(dict(file=rel, bytes=os.path.getsize(fp), rows=nrows, sha256=h.hexdigest()))
with open(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(inv[0].keys())); w.writeheader(); w.writerows(inv)
with open(os.path.join(PK,"08_qc","checksums_sha256.txt"),"w",encoding="utf-8") as f:
    for r in inv: f.write(f"{r['sha256']}  {r['file']}\n")
print("inventory:",len(inv),"files")
# 4. rebuild docx/pdf/zips and re-run audits
print(subprocess.run([sys.executable, os.path.join(V12,"scripts","71_v12_md_final.py")],capture_output=True,text=True).stdout.strip()[:120])
print(subprocess.run([sys.executable, os.path.join(V12,"scripts","80_build_docx_zip.py")],capture_output=True,text=True).stdout.strip()[-160:])
pdf=os.path.join(V12,"01_manuscript","DataDescriptor_v12.pdf")
if os.path.exists(pdf): os.remove(pdf)
subprocess.run([r"C:\Program Files\LibreOffice\program\soffice.exe","--headless","--convert-to","pdf",
                "--outdir",os.path.join(V12,"01_manuscript"),os.path.join(V12,"01_manuscript","DataDescriptor_v12.docx")],capture_output=True)
for s2 in ["90_v12_checks.py","91_v12_lowlevel_audit.py"]:
    r=subprocess.run([sys.executable, os.path.join(V12,"scripts",s2)],capture_output=True,text=True)
    tail=[l for l in r.stdout.strip().splitlines() if l.startswith(("issues:","  ISSUE","passed:"))]
    print(s2,"->"," | ".join(tail))
