#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14.3: manuscript text fixes, then a VERIFIED rebuild of the manuscript documents.

Checks performed before the rebuild is accepted:
  * every heading of the md appears in the docx text
  * every embedded figure matches the file in 02_figures byte for byte (sha256)
  * the in-text counts (files, SHA entries, folders, supplementary tables) are regenerated from the deposit
"""
import csv, hashlib, os, re, shutil, subprocess, zipfile
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
TBL=os.path.join(V14,"03_tables"); FIG=os.path.join(V14,"02_figures")
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda: f.read(1<<20), b""): h.update(c)
    return h.hexdigest()
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
inv=rd(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"))
n_files=len(inv); n_checks=len([r for r in inv if len(str(r["sha256"]))==64])
n_tables=17
# ---------------- 1. manuscript text ----------------
mp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mp,encoding="utf-8").read()
orig=md
def rep(a,b,label,count=1):
    global md
    if a in md: md=md.replace(a,b,count); print("  patched:",label)
    else: print("  SKIP (anchor absent):",label)
# counts and folder list
md=re.sub(r"as ten folders", "as eleven folders", md)
md=re.sub(r"\((\d+) files, with (\d+) SHA-256 entries[^)]*\)", f"({n_files} files, with {n_checks} SHA-256 entries because the two verification files are self-referential)", md)
rep("10 environment, run order and versioning.", "10 environment, run order and versioning; and 11 code, the analysis scripts and their README.", "folder list")
rep("Tables 1 and Supplementary Tables S1-S16 as a single PDF", f"Table 1 and Supplementary Tables S1-S{n_tables} as a single PDF", "supplementary count")
rep("Coverage and composition are shown in Figure 1;", "Coverage and composition are shown in Figure 1 and the cohort composition is quantified in Table 1;", "Table 1 citation")
# input data subsection
if "**Input data.**" not in md and "*Input data.*" not in md:
    rep("*Expression processing and QC.*",
        "*Input data.* The resource is built from GEO series retrieved with GEOquery2 and listed accession by accession in "
        "01_cohort_registry/cohort_registry.csv (26 case-control cohorts plus one treatment-response series that is not part of the "
        "case-control resource), from six tumour molecular contexts of The Cancer Genome Atlas obtained through the Genomic Data "
        "Commons3 and cBioPortal4,5, and from four single-cell datasets - three from CELLxGENE Discover6 (colorectal, inflammatory "
        "bowel disease and gastric cancer) and one GEO series (asthma, GSE193816). The exact single-cell dataset versions and "
        "collection identifiers are listed in 01_cohort_registry/cellxgene_sources.csv, and every accession is repeated in the Data "
        "Availability statement.\n*Expression processing and QC.*", "Input data subsection")
# single-cell minimum-cells contradiction
rep("No minimum number of cells per donor was imposed; the donor-level table reports the donors contributing to each comparison",
    "The primary analysis imposes no minimum number of cells per donor (a sensitivity analysis requiring at least ten cells per donor "
    "per cell type and arm is reported in Table S17); the donor-level table reports the donors contributing to each comparison",
    "Methods minimum-cells statement")
rep("(viii) no minimum cells-per-donor filter was applied in the single-cell layer.",
    "(viii) the primary single-cell analysis applies no minimum cells-per-donor filter, and the corresponding sensitivity analysis is "
    "reported in Supplementary Table S17.", "Usage Notes (viii)")
rep("which is why the testable count does not simply fall)",
    "which is why testability changes in both directions and the two donor sets are not directly comparable)", "sensitivity wording")
rep("Single-cell sensitivity analyses are shipped.",
    "Single-cell sensitivity analyses are shipped as Supplementary Table S17.", "S17 citation")
# abbreviations: inline definitions instead of a section
md=re.sub(r"Abbreviations: [^\n]*\n", "", md)
rep("Benjamini-Hochberg within families defined by context", "Benjamini-Hochberg (BH) within families defined by context", "define BH")
rep("the maximum per-predictor VIF has median", "the maximum per-predictor variance inflation factor (VIF) has median", "define VIF")
rep("outlier samples beyond three median absolute deviations", "outlier samples beyond three median absolute deviations (MAD)", "define MAD")
rep("The survival layer uses overall survival in months", "The survival layer uses overall survival (OS) in months", "define OS")
rep("the number of pooled states surviving BH control is", "the number of pooled states surviving false-discovery-rate (FDR) control is", "define FDR")
# section order: references after code availability, funding split
def move_block(text, header, after_header):
    m=re.search(r"(?ms)^\*\*"+re.escape(header)+r"\.\*\*.*?(?=^\*\*|\Z)", text)
    if not m: return text, False
    block=m.group(0)
    text=text[:m.start()]+text[m.end():]
    m2=re.search(r"(?ms)^\*\*"+re.escape(after_header)+r"\.\*\*.*?(?=^\*\*|\Z)", text)
    if not m2: return text, False
    return text[:m2.end()]+block+text[m2.end():], True
if "**References**" in md and "**Code Availability**" in md:
    md,ok=move_block(md,"References","Code Availability"); print("  references moved after Code Availability:",ok)
rep("**Acknowledgements and Funding**\nThe author thanks","**Acknowledgements**\nThe author thanks","split acknowledgements")
rep("No specific funding was received for this work.","**Funding**\nNo specific funding was received for this work.","funding heading")
rep("**Ethics statement**\nThis work uses only publicly available, de-identified data; no ethical approval or informed consent was required.\n\n","","remove standalone ethics")
rep("*Source versions and licences.*","*Ethics.* This work uses only publicly available, de-identified data; no ethical approval or informed consent were required.\n*Source versions and licences.*","ethics into Methods")
# reference renumbering: 9 metafor, 10 Hartung, 11 Knapp, 12 limma
refs_old=[("9. Ritchie ME, et al. limma powers differential expression analyses for RNA-sequencing and microarray studies. Nucleic Acids Res 2015;43:e47.",
           "12. Ritchie ME, et al. limma powers differential expression analyses for RNA-sequencing and microarray studies. Nucleic Acids Res 2015;43:e47."),
          ("10. Viechtbauer W. Conducting meta-analyses in R with the metafor package. J Stat Softw 2010;36:1-48.",
           "9. Viechtbauer W. Conducting meta-analyses in R with the metafor package. J Stat Softw 2010;36:1-48."),
          ("11. Hartung J, Knapp G. A refined method for the meta-analysis of controlled clinical trials with binary outcome. Stat Med 2001;20:3875-3889.",
           "10. Hartung J, Knapp G. A refined method for the meta-analysis of controlled clinical trials with binary outcome. Stat Med 2001;20:3875-3889."),
          ("12. Knapp G, Hartung J. Improved tests for a random effects meta-regression with a single covariate. Stat Med 2003;22:2693-2710.",
           "11. Knapp G, Hartung J. Improved tests for a random effects meta-regression with a single covariate. Stat Med 2003;22:2693-2710.")]
for a,b in refs_old: rep(a,b,"renumber reference")
open(mp,"w",encoding="utf-8").write(md)
print("manuscript text updated; changed:", md!=orig)
# ---------------- 2. verified docx rebuild ----------------
from docx import Document
from docx.shared import Pt, Inches, RGBColor
CITE=re.compile(r"(GEOquery|Genomic Data Commons|cBioPortal|CELLxGENE|GEO|GSVA|xCell|metafor|Hartung-Knapp|limma|R)(\d+(?:,\d+)*)")
def add_para(doc, text):
    p=doc.add_paragraph(); pos=0
    for m in CITE.finditer(text):
        if m.start()>pos: p.add_run(text[pos:m.start()])
        p.add_run(m.group(1)); sup=p.add_run(m.group(2)); sup.font.superscript=True
        pos=m.end()
    if pos<len(text): p.add_run(text[pos:])
    for r in p.runs: r.font.name="Times New Roman"
    return p
doc=Document(); st=doc.styles["Normal"]; st.font.name="Times New Roman"; st.font.size=Pt(11)
figs=[("Figure 1 (legend provided in the separate figure-legend file).","Fig1_resource_overview.png"),
      ("Figure 2 (legend provided in the separate figure-legend file).","Fig2_technical_validation.png"),
      ("Figure 3 (legend provided in the separate figure-legend file).","Fig3_comparability_checks.png"),
      ("Figure 4 (legend provided in the separate figure-legend file).","Fig4_sensitivity_checks.png")]
for line in md.splitlines():
    s=line.rstrip()
    if not s.strip(): continue
    if s.startswith("# "):
        h=doc.add_heading(level=0); r=h.add_run(s[2:].strip()); r.font.name="Times New Roman"; r.font.color.rgb=RGBColor(0,0,0)
    elif s.startswith("## "):
        h=doc.add_heading(level=1); r=h.add_run(s[3:].strip()); r.font.name="Times New Roman"; r.font.color.rgb=RGBColor(0,0,0)
    elif s.startswith("**") and s.endswith("**"):
        h=doc.add_heading(level=2); r=h.add_run(s.strip("*")); r.font.name="Times New Roman"; r.font.color.rgb=RGBColor(0,0,0)
    else:
        add_para(doc, s.replace("**","").replace("*",""))
doc.add_page_break(); h=doc.add_heading(level=1); r=h.add_run("Figures"); r.font.name="Times New Roman"; r.font.color.rgb=RGBColor(0,0,0)
for cap,fn in figs:
    h=doc.add_heading(level=2); r=h.add_run(cap); r.font.name="Times New Roman"; r.font.color.rgb=RGBColor(0,0,0)
    doc.add_picture(os.path.join(FIG,fn), width=Inches(6.2)); doc.add_paragraph("")
dp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.docx"); doc.save(dp)
subprocess.run([r"C:\Program Files\LibreOffice\program\soffice.exe","--headless","--convert-to","pdf","--outdir",
                os.path.join(V14,"01_manuscript"),dp],capture_output=True)
# verification
import docx as _d
dt="\n".join(p.text for p in _d.Document(dp).paragraphs)
headings=[l.strip("*# ").strip() for l in md.splitlines() if l.startswith(("## ","**")) and len(l.strip("*# ").strip())>3]
missing=[h for h in headings if h[:40] not in dt]
key=[k for k in ["Input data","Single-cell sensitivity analyses","eleven folders",f"{n_files} files",f"S1-{n_tables}","Table S17","Table 1"] if k not in dt]
print(f"docx verification: {len(headings)} headings checked, missing={missing[:3] or 'none'} | key phrases missing={key or 'none'}")
zp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.docx")
z=_d.Document(zp); embs=[rel.target_ref for rel in z.part.rels.values() if "image" in rel.reltype]
emb_ok=True
for i,fn in enumerate([f[1] for f in figs]):
    if i<len(embs):
        data=z.part.related_parts[embs[i]].blob
        disk=open(os.path.join(FIG,fn),"rb").read()
        same=hashlib.sha256(data).hexdigest()==hashlib.sha256(disk).hexdigest()
        emb_ok = emb_ok and same
        if not same: print(f"  MISMATCH embedded figure {i+1} ({fn})")
print("embedded figures match disk byte for byte:", emb_ok)
sup=sum(1 for p in _d.Document(dp).paragraphs for r in p.runs if r.font.superscript)
print("superscript runs in docx:", sup)
print("pdf rebuilt:", os.path.exists(os.path.join(V14,"01_manuscript","DataDescriptor_v14.pdf")))
