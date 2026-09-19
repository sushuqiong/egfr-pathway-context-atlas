#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14.3 corrections: fix the supplementary range string, move the References block properly,
and verify the embedded figures with the correct python-docx API."""
import hashlib, os, re, subprocess
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; FIG=os.path.join(V14,"02_figures")
mp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mp,encoding="utf-8").read()
md=md.replace("Supplementary Tables S1-17","Supplementary Tables S1-S17")
md=md.replace("S1-17 as a single PDF","S1-S17 as a single PDF")
# move References after Code Availability
m=re.search(r"(?ms)^\*\*References\*\*.*?(?=^\*\*Data Availability\*\*)", md)
if m and md.index("**References**") < md.index("**Code Availability**"):
    block=m.group(0); md=md[:m.start()]+md[m.end():]
    m2=re.search(r"(?ms)^\*\*Code Availability\*\*.*?(?=^\*\*Author Contributions|\Z)", md)
    if m2:
        md=md[:m2.end()]+"\n"+block+md[m2.end():]
        print("references moved after Code Availability")
    else:
        print("WARNING: code availability block not found")
else:
    print("references already after code availability or block not found:", bool(m))
open(mp,"w",encoding="utf-8").write(md)
order=[h for h in re.findall(r"(?m)^\*\*([A-Za-z &]+)\.?\*\*", md)]
print("section order now:", " | ".join(order))
# rebuild docx quickly (reuse the builder from the previous script by importing its logic)
from docx import Document
from docx.shared import Pt, Inches, RGBColor
CITE=re.compile(r"(GEOquery|Genomic Data Commons|cBioPortal|CELLxGENE|GEO|GSVA|xCell|metafor|Hartung-Knapp|limma|R)(\d+(?:,\d+)*)")
def add_para(doc, text):
    p=doc.add_paragraph(); pos=0
    for m in CITE.finditer(text):
        if m.start()>pos: p.add_run(text[pos:m.start()])
        p.add_run(m.group(1)); sup=p.add_run(m.group(2)); sup.font.superscript=True; pos=m.end()
    if pos<len(text): p.add_run(text[pos:])
    for r in p.runs: r.font.name="Times New Roman"
doc=Document(); st=doc.styles["Normal"]; st.font.name="Times New Roman"; st.font.size=Pt(11)
figs=[("Figure 1 (legend in the separate figure-legend file).","Fig1_resource_overview.png"),
      ("Figure 2 (legend in the separate figure-legend file).","Fig2_technical_validation.png"),
      ("Figure 3 (legend in the separate figure-legend file).","Fig3_comparability_checks.png"),
      ("Figure 4 (legend in the separate figure-legend file).","Fig4_sensitivity_checks.png")]
for line in md.splitlines():
    s=line.rstrip()
    if not s.strip(): continue
    if s.startswith("# "):
        h=doc.add_heading(level=0); r=h.add_run(s[2:].strip()); r.font.name="Times New Roman"; r.font.color.rgb=RGBColor(0,0,0)
    elif s.startswith("## "):
        h=doc.add_heading(level=1); r=h.add_run(s[3:].strip()); r.font.name="Times New Roman"; r.font.color.rgb=RGBColor(0,0,0)
    elif s.startswith("**") and s.endswith("**") and not s.startswith("**Figure"):
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
# verification with the correct API
d=Document(dp); dt="\n".join(p.text for p in d.paragraphs)
key=["Input data","Single-cell sensitivity analyses","eleven folders","Table S17","Table 1","S1-S17",
     "not a pooled estimate" if "not a pooled estimate" in md else "BH"]
print("docx key phrases present:", {k:(k in dt) for k in key})
emb=[]
for rel in d.part.rels.values():
    if "image" in rel.reltype: emb.append(hashlib.sha256(rel.target_part.blob).hexdigest())
disk={fn: hashlib.sha256(open(os.path.join(FIG,fn),"rb").read()).hexdigest() for _,fn in figs}
match=[h for h in emb if h in disk.values()]
print(f"embedded images: {len(emb)} | matching shipped figures byte for byte: {len(match)}")
print("superscript runs:", sum(1 for p in d.paragraphs for r in p.runs if r.font.superscript))
print("pdf exists:", os.path.exists(os.path.join(V14,"01_manuscript","DataDescriptor_v14.pdf")))
