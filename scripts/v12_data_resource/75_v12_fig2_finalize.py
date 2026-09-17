#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12: verify Fig2 layout by OCR, refresh the Figure 2 caption, rebuild docx/pdf/zips and re-run audits."""
import csv, os, shutil, subprocess, sys
from PIL import Image
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results"); PK=os.path.join(V12,"dataset_package")
TESS=r"C:\Program Files\Tesseract-OCR\tesseract.exe"; TMP=r"C:\Users\fengq\ocr_tmp"
shutil.rmtree(TMP,ignore_errors=True); os.makedirs(TMP)
def ocr(path):
    env=dict(os.environ, TESSDATA_PREFIX=r"C:\Program Files\Tesseract-OCR\tessdata")
    r=subprocess.run([TESS,path,"stdout","--psm","11","tsv"],capture_output=True,env=env)
    out=[]
    for row in csv.DictReader(r.stdout.decode("utf-8","replace").splitlines(), delimiter="\t"):
        t=(row.get("text") or "").strip()
        if not t: continue
        try: out.append(dict(t=t,c=float(row.get("conf") or -1),x=int(row["left"]),y=int(row["top"]),w=int(row["width"]),h=int(row["height"])))
        except Exception: pass
    return [w for w in out if w["c"]>30]
print("== OCR layout check ==")
for f in ["Fig1_resource_overview.png","Fig2_technical_validation.png"]:
    dst=os.path.join(TMP,f); shutil.copy(os.path.join(V12,"02_figures",f),dst)
    W,H=Image.open(dst).size; ws=ocr(dst)
    clip=[w["t"] for w in ws if w["x"]<=2 or w["y"]<=2 or w["x"]+w["w"]>=W-2 or w["y"]+w["h"]>=H-2]
    print(f"  {f}: {W}x{H} ({W/300*2.54:.1f} x {H/300*2.54:.1f} cm) words={len(ws)} clipped={len(clip)} {clip[:4]}")
# refresh the Figure 2 caption
p=os.path.join(V12,"01_manuscript","DataDescriptor_v12.md"); s=open(p,encoding="utf-8").read()
old="**Figure 2. Technical validation.** (A) Documented exclusions, flags and non-testable comparisons (log scale). (B) The single-cell comparison design actually used, by test type. (C) The complete estimates layer: all per-cohort standardized effects, including non-significant results."
new=("**Figure 2. Technical validation.** (A) Documented exclusions, flags and non-testable comparisons (log scale). "
     "(B) The single-cell comparison design actually used, by test type. (C) The complete estimates layer: all per-cohort standardized effects, "
     "including non-significant results. (D) Common-gene sensitivity: Spearman correlation between full-member and cross-cohort common-gene scoring "
     "for each module, coloured by whether effect directions disagreed in at least 20% of cohorts or too few genes are shared to re-score. "
     "(E) Collinearity between disease status and the four composition scores, per cohort, with the median marked.")
if old in s:
    s=s.replace(old,new); open(p,"w",encoding="utf-8").write(s); print("caption updated")
else:
    print("caption anchor NOT found (will reword manually)")
# rebuild docx + zips + pdf
for script in ["80_build_docx_zip.py"]:
    r=subprocess.run([sys.executable, os.path.join(V12,"scripts",script)],capture_output=True,text=True)
    print(r.stdout.strip()[-200:])
pdf=os.path.join(V12,"01_manuscript","DataDescriptor_v12.pdf")
if os.path.exists(pdf): os.remove(pdf)
subprocess.run([r"C:\Program Files\LibreOffice\program\soffice.exe","--headless","--convert-to","pdf",
                "--outdir",os.path.join(V12,"01_manuscript"),os.path.join(V12,"01_manuscript","DataDescriptor_v12.docx")],capture_output=True)
# refresh inventory inside the package, then audits
inv=[]
import hashlib
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
for s2 in ["90_v12_checks.py","91_v12_lowlevel_audit.py"]:
    r=subprocess.run([sys.executable, os.path.join(V12,"scripts",s2)],capture_output=True,text=True)
    tail=[l for l in r.stdout.strip().splitlines() if l.startswith(("issues:","  ISSUE","passed:"))]
    print(s2,"->"," | ".join(tail))
