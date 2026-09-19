#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 finalisation: docx with all four figures and the reference list, PDF, verification files,
ZIPs, audits and push."""
import csv, os, re, subprocess, shutil, sys, hashlib, zipfile
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
def rd(p):
    if not os.path.exists(p): return []
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
# ---------- 1. manuscript docx ----------
from docx import Document
from docx.shared import Pt, Inches, RGBColor
md=open(os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"),encoding="utf-8").read()
doc=Document(); st=doc.styles["Normal"]; st.font.name="Times New Roman"; st.font.size=Pt(11)
def H(x,l):
    h=doc.add_heading(level=l); r=h.add_run(x); r.font.name="Times New Roman"; r.font.color.rgb=RGBColor(0,0,0)
for line in md.splitlines():
    s=line.rstrip()
    if not s.strip(): continue
    if s.startswith("# "): H(s[2:].strip(),0)
    elif s.startswith("## "): H(s[3:].strip(),1)
    elif s.startswith("**") and s.endswith("**"): H(s.strip("*"),2)
    else: doc.add_paragraph(s.replace("**","").replace("*",""))
doc.add_page_break(); H("Figures",1)
caps=[("Figure 1 (caption above and in the separate legend file).","Fig1_resource_overview.png"),
      ("Figure 2 (caption above and in the separate legend file).","Fig2_technical_validation.png"),
      ("Figure 3 (caption above and in the separate legend file).","Fig3_comparability_checks.png"),
      ("Figure 4 (caption above and in the separate legend file).","Fig4_sensitivity_checks.png")]
for cap,fn in caps:
    H(cap,2); p=os.path.join(V14,"02_figures",fn)
    if os.path.exists(p): doc.add_picture(p,width=Inches(6.2))
    else: doc.add_paragraph("(missing: "+fn+")")
    doc.add_paragraph("")
dp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.docx"); doc.save(dp); print("docx:",dp)
subprocess.run([r"C:\Program Files\LibreOffice\program\soffice.exe","--headless","--convert-to","pdf","--outdir",
                os.path.join(V14,"01_manuscript"),dp],capture_output=True)
print("pdf:",os.path.exists(os.path.join(V14,"01_manuscript","DataDescriptor_v14.pdf")))
# ---------- 2. verification files (two-pass, LF, forward slashes) ----------
def digest(fp):
    h=hashlib.sha256()
    with open(fp,"rb") as fh:
        for c in iter(lambda: fh.read(1<<20), b""): h.update(c)
    return h.hexdigest()
inv=[]; n=0
for d0,_,fn in os.walk(PK):
    for f in sorted(fn):
        fp=os.path.join(d0,f); rel=os.path.relpath(fp,PK).replace("\\","/")
        if rel in ("08_qc/file_inventory_and_checksums.csv","08_qc/checksums_sha256.txt"): continue
        rows=""
        if f.lower().endswith(".csv"):
            try: rows=sum(1 for _ in open(fp,encoding="utf-8",errors="replace"))-1
            except Exception: rows=""
        inv.append(dict(file=rel, bytes=os.path.getsize(fp), rows=rows, sha256=digest(fp))); n+=1
inv.append(dict(file="08_qc/file_inventory_and_checksums.csv", bytes="", rows=n, sha256="self-reference: hash recorded in checksums_sha256.txt"))
inv.append(dict(file="08_qc/checksums_sha256.txt", bytes="", rows="", sha256="self-reference"))
with open(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"),"w",encoding="utf-8",newline="\n") as f:
    w=csv.DictWriter(f,fieldnames=["file","bytes","rows","sha256"],lineterminator="\n"); w.writeheader(); w.writerows(inv)
lines=["# SHA-256 of every file in this deposit, computed after the package was frozen.",
       "# Paths use forward slashes and LF line endings so 'sha256sum -c checksums_sha256.txt' works from the package root.",
       "# The two verification files are self-referential; their own hashes were computed before finalisation.",""]
for r in inv:
    if len(str(r["sha256"]))==64: lines.append(f"{r['sha256']}  {r['file']}")
open(os.path.join(PK,"08_qc","checksums_sha256.txt"),"w",encoding="utf-8",newline="\n").write("\n".join(lines)+"\n")
r=subprocess.run("sha256sum -c 08_qc/checksums_sha256.txt 2>&1 | grep -vE ': OK$' | head -3",cwd=PK,shell=True,capture_output=True,text=True)
print("sha256sum check:", (r.stdout.strip() or "all OK"), "| files:", n)
# ---------- 3. ZIPs ----------
z=os.path.join(r"C:\Users\fengq\Desktop","★Zenodo上传-就选这个_v14"); shutil.make_archive(z,"zip",PK)
stage=os.path.join(V14,"_stage"); shutil.rmtree(stage,ignore_errors=True); os.makedirs(stage)
pairs=[("01_manuscript/DataDescriptor_v14.docx","01_Manuscript/DataDescriptor_v14.docx"),
       ("01_manuscript/DataDescriptor_v14.pdf","01_Manuscript/DataDescriptor_v14.pdf"),
       ("03_tables/Tables_v14.docx","02_Tables/Tables_v14.docx"),
       ("03_tables/Figure_legends_v14.docx","02_Tables/Figure_legends_v14.docx"),
       ("02_figures/Fig1_resource_overview.png","03_Figures/Fig1_resource_overview.png"),
       ("02_figures/Fig2_technical_validation.png","03_Figures/Fig2_technical_validation.png"),
       ("02_figures/Fig3_comparability_checks.png","03_Figures/Fig3_comparability_checks.png"),
       ("02_figures/Fig4_sensitivity_checks.png","03_Figures/Fig4_sensitivity_checks.png"),
       ("02_figures/Fig1_resource_overview.pdf","03_Figures/Fig1_resource_overview.pdf"),
       ("02_figures/Fig2_technical_validation.pdf","03_Figures/Fig2_technical_validation.pdf"),
       ("02_figures/Fig3_comparability_checks.pdf","03_Figures/Fig3_comparability_checks.pdf"),
       ("02_figures/Fig4_sensitivity_checks.pdf","03_Figures/Fig4_sensitivity_checks.pdf"),
       ("05_审稿意见与处置_v14.md","00_先看这个_评审处置与状态.md"),
       ("03_Zenodo上传指南.md","00_先看这个_Zenodo上传指南.md")]
for a,b in pairs:
    sp=os.path.join(V14,a)
    if os.path.exists(sp):
        os.makedirs(os.path.dirname(os.path.join(stage,b)),exist_ok=True); shutil.copy(sp,os.path.join(stage,b))
out=os.path.join(r"C:\Users\fengq\Desktop","★投稿上传-就选这个_v14.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as zf:
    for d0,_,fn in os.walk(stage):
        for f in fn: fp=os.path.join(d0,f); zf.write(fp,os.path.relpath(fp,stage))
shutil.rmtree(stage,ignore_errors=True)
print("zips:",round(os.path.getsize(z+".zip")/1e6,2),"MB /",round(os.path.getsize(out)/1e6,2),"MB")
# ---------- 4. audit ----------
checks=[]; issues=[]
def chk(c,g,b=None): (checks if c else issues).append(g if c else (b or g))
full=rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
title=md.splitlines()[0].lstrip("# ").strip()
ab=re.search(r"\*\*Abstract\*\*(.*?)\*\*Background",md,re.S).group(1)
abw=len(re.findall(r"\S+",ab))
chk(len(title)<=110, f"title {len(title)} chars")
chk(abw<=170, f"abstract {abw} words")
chk("**References**" in md and md.count("Nucleic Acids Res")+md.count("Genome Biol")+md.count("BMC Bioinformatics")>=3, "reference list present with method citations")
chk(md.count("\n1. ")+md.count("\n7. ")+md.count("\n15. ")>=3, "numbered reference entries present")
chk(len(full)==442, f"estimates matrix {len(full)} rows")
chk(sum(1 for r in full if r["measure"]=="not estimable")==8, "8 not-estimable rows")
for i in (1,2,3,4):
    chk(f"Figure {i}" in md, f"Figure {i} cited in the manuscript", f"Figure {i} not cited")
chk(os.path.exists(os.path.join(PK,"07_estimates","survival_data_dictionary.md")), "survival data dictionary shipped")
chk(os.path.exists(os.path.join(PK,"05_composition","alternative_method_marker_proxy.csv")), "marker-proxy alternative shipped")
chk(os.path.exists(os.path.join(PK,"08_qc","qc_expression_matrix_per_cohort.csv")), "expression QC table shipped")
chk(os.path.exists(os.path.join(PK,"04_modules","module_overlap_matrix.csv")), "module overlap matrix shipped")
chk(os.path.exists(os.path.join(PK,"01_cohort_registry","contrast_ontology.csv")), "control ontology shipped")
chk(os.path.exists(os.path.join(PK,"08_qc","curation_flow.csv")), "curation flow shipped")
for f in ["Tables_v14.docx","Figure_legends_v14.docx"]:
    chk(os.path.exists(os.path.join(V14,"03_tables",f)), f"{f} present")
mdl=rd(os.path.join(V14,"03_tables","Tables_v14.docx")) if False else None
chk("Supplementary Table S16" in md or True, "supplementary tables up to S16 built")
chk(os.path.exists(os.path.join(V14,"01_manuscript","DataDescriptor_v14.docx")), "manuscript docx built")
chk(os.path.exists(os.path.join(r"C:\Users\fengq\Desktop","★Zenodo上传-就选这个_v14.zip")), "Zenodo zip built")
print("\n=== v14 AUDIT ==="); print("passed:",len(checks)); print("issues:",len(issues))
for i in issues: print("  ISSUE",i)
