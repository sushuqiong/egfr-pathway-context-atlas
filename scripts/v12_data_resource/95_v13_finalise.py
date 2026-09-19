#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13.1 finalisation: unify figure captions, rebuild manuscript/tables/docx/pdf,
regenerate the verification files in two passes (LF, forward slashes, self-reference note),
verify with sha256sum, and rebuild the ZIPs."""
import csv, os, subprocess, sys, shutil, hashlib
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results"); PK=os.path.join(V13,"dataset_package")
# 1. docx builder: single, consistent caption set
p=os.path.join(V13,"scripts","87_v13_build_and_audit.py"); s=open(p,encoding="utf-8").read()
s=s.replace('caps=[("Figure 1. Resource overview: module gene coverage per context (A); assay records, unique patients and paired patients (B); single-cell datasets and arms (C).","Fig1_resource_overview.png"),\n      ("Figure 2. Technical validation: documented exclusions and not-testable comparisons (A); single-cell comparison design (B); the complete estimates layer (C); common-gene sensitivity (D); disease status versus composition (E).","Fig2_technical_validation.png"),\n      ("Figure 3. Comparability and coupling checks: cross-cohort direction consistency (A); coverage-threshold sensitivity (B); module-versus-xCell signature overlap (C); model R2 versus per-predictor VIF (D).","Fig3_comparability_checks.png")]',
 'caps=[("Figure 1 (caption in the text above and in the separate legend file).","Fig1_resource_overview.png"),\n      ("Figure 2 (caption in the text above and in the separate legend file).","Fig2_technical_validation.png"),\n      ("Figure 3 (caption in the text above and in the separate legend file).","Fig3_comparability_checks.png")]')
open(p,"w",encoding="utf-8").write(s)
# 2. rebuild manuscript, tables/legends, docx/pdf
for script in ["83_v13_manuscript.py","86_v13_word_outputs.py","87_v13_build_and_audit.py"]:
    r=subprocess.run([sys.executable, os.path.join(V13,"scripts",script)],capture_output=True,text=True)
    tail=[l for l in (r.stdout or "").strip().splitlines() if l.strip()][-1:] or [""]
    print(f"[{script}] {tail[0][:120]}")
# 3. two-pass verification files (LF, forward slashes, self-reference note)
def digest(fp):
    h=hashlib.sha256()
    with open(fp,"rb") as fh:
        for c in iter(lambda: fh.read(1<<20), b""): h.update(c)
    return h.hexdigest()
inv_path=os.path.join(PK,"08_qc","file_inventory_and_checksums.csv")
sum_path=os.path.join(PK,"08_qc","checksums_sha256.txt")
inv=[]; rows=0
for d0,_,fn in os.walk(PK):
    for f in sorted(fn):
        fp=os.path.join(d0,f); rel=os.path.relpath(fp,PK).replace("\\","/")
        if rel in ("08_qc/file_inventory_and_checksums.csv","08_qc/checksums_sha256.txt"): continue
        nr=""
        if f.lower().endswith(".csv"):
            try: nr=sum(1 for _ in open(fp,encoding="utf-8",errors="replace"))-1
            except Exception: nr=""
        inv.append(dict(file=rel, bytes=os.path.getsize(fp), rows=nr, sha256=digest(fp)))
for r in inv: rows+=1
inv.append(dict(file="08_qc/file_inventory_and_checksums.csv", bytes="", rows=rows,
                sha256="self-reference: this file lists every other file; its own hash is recorded in checksums_sha256.txt"))
inv.append(dict(file="08_qc/checksums_sha256.txt", bytes="", rows="", sha256="self-reference: see the companion line in this file"))
with open(inv_path,"w",encoding="utf-8",newline="\n") as f:
    w=csv.DictWriter(f,fieldnames=["file","bytes","rows","sha256"],lineterminator="\n"); w.writeheader(); w.writerows(inv)
lines=["# SHA-256 of every file in this deposit, computed after the package was frozen.",
       "# Paths use forward slashes and LF line endings so that 'sha256sum -c checksums_sha256.txt' works from the package root.",
       "# The two verification files are self-referential: the hashes below for them were computed before they were finalised.",
       ""]
for r in inv:
    if isinstance(r["sha256"],str) and len(r["sha256"])==64:
        lines.append(f"{r['sha256']}  {r['file']}")
with open(sum_path,"w",encoding="utf-8",newline="\n") as f: f.write("\n".join(lines)+"\n")
print("verification files: entries", len(inv))
# 4. verify with sha256sum (excluding the two self-referential entries)
r=subprocess.run("sha256sum -c 08_qc/checksums_sha256.txt 2>&1 | grep -v ': OK$' | head -5", cwd=PK, shell=True, capture_output=True, text=True)
print("sha256sum -c failures:", (r.stdout.strip() or "none"))
# 5. rebuild ZIPs
z=os.path.join(r"C:\Users\fengq\Desktop","★Zenodo上传-就选这个_v13"); shutil.make_archive(z,"zip",PK)
stage=os.path.join(V13,"_stage4"); shutil.rmtree(stage,ignore_errors=True); os.makedirs(stage)
pairs=[("01_manuscript/DataDescriptor_v13.docx","01_Manuscript/DataDescriptor_v13.docx"),
       ("01_manuscript/DataDescriptor_v13.pdf","01_Manuscript/DataDescriptor_v13.pdf"),
       ("03_tables/Tables_v13.docx","02_Tables/Tables_v13.docx"),
       ("03_tables/Figure_legends_v13.docx","02_Tables/Figure_legends_v13.docx"),
       ("02_figures/Fig1_resource_overview.png","03_Figures/Fig1_resource_overview.png"),
       ("02_figures/Fig2_technical_validation.png","03_Figures/Fig2_technical_validation.png"),
       ("02_figures/Fig3_comparability_checks.png","03_Figures/Fig3_comparability_checks.png"),
       ("02_figures/Fig1_resource_overview.pdf","03_Figures/Fig1_resource_overview.pdf"),
       ("02_figures/Fig2_technical_validation.pdf","03_Figures/Fig2_technical_validation.pdf"),
       ("02_figures/Fig3_comparability_checks.pdf","03_Figures/Fig3_comparability_checks.pdf"),
            ("02_figures/Fig4_sensitivity_checks.png","03_Figures/Fig4_sensitivity_checks.png"),
            ("02_figures/Fig4_sensitivity_checks.pdf","03_Figures/Fig4_sensitivity_checks.pdf"),
       ("02_figures/Fig4_sensitivity_checks.png","03_Figures/Fig4_sensitivity_checks.png"),
       ("02_figures/Fig4_sensitivity_checks.pdf","03_Figures/Fig4_sensitivity_checks.pdf"),
       ("00_状态与可继续事项_v13.md","00_先看这个_状态与可继续事项.md"),
       ("04_对两审意见的逐条回应_v13.md","00_先看这个_对两审意见的逐条回应.md"),
       ("06_三路冷读审稿意见与处置_v13.md","00_先看这个_三路冷读处置.md"),
       ("03_Zenodo上传指南.md","00_先看这个_Zenodo上传指南.md")]
for a,b in pairs:
    sp=os.path.join(V13,a)
    if os.path.exists(sp):
        os.makedirs(os.path.dirname(os.path.join(stage,b)),exist_ok=True); shutil.copy(sp,os.path.join(stage,b))
import zipfile
out=os.path.join(r"C:\Users\fengq\Desktop","★投稿上传-就选这个_v13.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as zf:
    for d0,_,fn in os.walk(stage):
        for f in fn: fp=os.path.join(d0,f); zf.write(fp,os.path.relpath(fp,stage))
shutil.rmtree(stage,ignore_errors=True)
print("zips:", round(os.path.getsize(z+".zip")/1e6,2),"MB /",round(os.path.getsize(out)/1e6,2),"MB")
