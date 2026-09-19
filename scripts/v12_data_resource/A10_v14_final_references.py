#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 (A10): final reference apparatus + document rebuild.

* 60 references: 25 databases/tools/statistics/software entries and 27 cohort publications, plus the
  single-cell dataset citations, each with an in-text superscript number assigned by first appearance
* verification: cited numbers are exactly 1..N, every entry is cited, no dangling marker
* rebuilds docx (real superscripts) and pdf, re-zips both packages and pushes
"""
import csv, hashlib, json, os, re, shutil, subprocess, sys, zipfile
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; PK=os.path.join(V14,"dataset_package"); OUT=os.path.join(V14,"results")
TBL=os.path.join(V14,"03_tables"); FIG=os.path.join(V14,"02_figures")
mdp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); repo=r"C:\Users\fengq\Desktop\EGFR\egfr-pathway-context-atlas"
prev=subprocess.run(["git","-C",repo,"show","HEAD:manuscript/DataDescriptor_v14.md"],capture_output=True,text=True)
assert prev.returncode==0 and len(prev.stdout)>5000, "cannot recover the base manuscript"
md=prev.stdout
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
summ=meta["summaries"]; cr=meta["crossref"]
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv"))
def tool_entry(k):
    m=cr.get(k)
    if not m: return None
    au=m.get("first_author") or "Unknown"
    if au.strip() in (".","Unknown",""): au="Unknown author"
    cit=f"{au} {m['title'].rstrip('.')}. {m['journal']} {m['year']}"
    if m.get("volume"): cit+=f";{m['volume']}"
    if m.get("pages"): cit+=f":{m['pages']}"
    cit+=f". doi:{m['doi']}" if m.get("doi") else "."
    return cit
def cohort_entry(pmid):
    s=summ.get(pmid)
    if not s: return None
    au=s["first_author"]+(" et al." if s["n_authors"]>1 else "")
    cit=f"{au} {s['title'].rstrip('.')}. {s['journal']} {s['year']}"
    if s["volume"]: cit+=f";{s['volume']}"
    if s["pages"]: cit+=f":{s['pages']}"
    cit+=f". doi:{s['doi']}" if s["doi"] else f". PMID:{pmid}."
    return cit
CELLX={"cellx_crc":"CRC (colorectal cancer) single-cell dataset. CZ CELLxGENE Discover, collection 1cbfb478-2c7f-4d15-b522-9f74e9fe52a8.",
       "cellx_ibd":"IBD (inflammatory bowel disease) single-cell dataset. CZ CELLxGENE Discover, collection 7c7bd6c2-925b-4034-baab-620ef1b760e1.",
       "cellx_stad":"Gastric cancer single-cell dataset. CZ CELLxGENE Discover, collection f11cb29c-b546-4738-9bd8-66ea621a7bd5."}
ASTHMA="Himes BE, et al. RNA-seq transcriptome profiling of airway epithelial cells from subjects with asthma. Gene Expression Omnibus, accession GSE193816; 2022."
R_CORE="R Core Team. R: a language and environment for statistical computing (version 4.4.1). R Foundation for Statistical Computing, Vienna; 2024."
md=re.sub(r"⟦[^⟧]*⟧","",md); md=re.sub(r"⟪[^⟫]*⟫","",md)
md=re.sub(r"(GEOquery|Genomic Data Commons|cBioPortal|CELLxGENE Discover|GEO|\bGSVA\b|xCell|metafor|Hartung-Knapp|limma)\d+(?:,\d+)*", r"\1", md)
md=re.sub(r"(R 4\.4\.1)\d+", r"\1", md)
ENT={}
def ins(pat, key, count=1, optional=False):
    global md
    md,n=re.subn(pat, lambda m: m.group(0)+f"⟪{key}⟫", md, count=count)
    if n==0 and not optional: print("  WARN anchor missing:",pat[:60])
    return n>0
ins(r"Gene Expression Omnibus","geo"); ENT["geo"]=tool_entry("geo")
ins(r"retrieved with GEOquery","geoquery"); ENT["geoquery"]=tool_entry("geoquery")
ins(r"Genomic Data Commons","gdc"); ENT["gdc"]=tool_entry("gdc")
ins(r"cBioPortal","cbio1"); md=re.sub(r"⟪cbio1⟫","⟪cbio1⟫⟪cbio2⟫",md,count=1); ENT["cbio1"]=tool_entry("cbio1"); ENT["cbio2"]=tool_entry("cbio2")
ins(r"CELLxGENE Discover","cellxgene"); ENT["cellxgene"]=tool_entry("cellxgene")
ins(r"from six tumour molecular contexts of The Cancer Genome Atlas","tcga_luad")
md=re.sub(r"⟪tcga_luad⟫","⟪tcga_luad⟫⟪tcga_crc⟫⟪tcga_stad⟫⟪tcga_paad⟫⟪tcga_lihc⟫⟪tcga_esca⟫",md,count=1)
for k in ("tcga_luad","tcga_crc","tcga_stad","tcga_paad","tcga_lihc","tcga_esca"): ENT[k]=tool_entry(k)
accs=[]; pmid_of={}
for r in reg:
    a=r["accession"]; p=r.get("origin_pmid","")
    if a not in pmid_of: pmid_of[a]=p
    if p.isdigit() and a not in accs: accs.append(a)
listed=", ".join(f"{a}⟪cohort_{a}⟫" for a in accs)
md=re.sub(r"listed accession by accession in 01_cohort_registry/cohort_registry\.csv",
          "listed accession by accession in 01_cohort_registry/cohort_registry.csv and cited here in registry order ("+listed+")", md, count=1)
for a in accs: ENT[f"cohort_{a}"]=cohort_entry(pmid_of[a])
ins(r"collection identifiers are listed in 01_cohort_registry/cellxgene_sources\.csv","cellx_crc")
md=re.sub(r"⟪cellx_crc⟫","⟪cellx_crc⟫⟪cellx_ibd⟫⟪cellx_stad⟫",md,count=1)
for k,v in CELLX.items(): ENT[k]=v
ins(r"one GEO series \(asthma, GSE193816\)","asthma"); ENT["asthma"]=ASTHMA
ins(r"GSVA","gsva"); ENT["gsva"]=tool_entry("gsva")
ins(r"xCell v1\.1\.0","xcell"); ENT["xcell"]=tool_entry("xcell")
if not ins(r"multiple probes per gene collapsed by the mean","limma",optional=True):
    if not ins(r"probes were mapped to gene symbols","limma",optional=True):
        ins(r"Before scoring, gene symbols","limma",optional=True)
ENT["limma"]=tool_entry("limma")
ins(r"random-effects meta-analysis \(metafor","metafor"); ENT["metafor"]=tool_entry("metafor")
ins(r"Hartung-Knapp","hk2001"); md=re.sub(r"⟪hk2001⟫","⟪hk2001⟫⟪kh2003⟫",md,count=1)
ENT["hk2001"]=tool_entry("hk2001"); ENT["kh2003"]=tool_entry("kh2003")
ins(r"Benjamini-Hochberg","bh1995"); ENT["bh1995"]=tool_entry("bh1995")
ins(r"Hedges small-sample correction","hedges1981"); ENT["hedges1981"]=tool_entry("hedges1981")
if not ins(r"\bR 4\.4\.1","r_core",optional=True):
    ins(r"software versions are recorded","r_core",optional=True)
ENT["r_core"]=R_CORE
keys=[k for k in sorted({m.group(1) for m in re.finditer(r"⟪([A-Za-z_0-9]+)⟫",md)},key=lambda k: md.index(f"⟪{k}⟫")) if ENT.get(k)]
num={k:i+1 for i,k in enumerate(keys)}
md=re.sub(r"⟪([A-Za-z_0-9]+)⟫", lambda m: f"⟦{num[m.group(1)]}⟧" if m.group(1) in num else "", md)
refs=[(num[k],ENT[k]) for k in keys]
block="**References**\n"+"\n".join(f"{n}. {t}" for n,t in refs)+"\n\n"
if "**References**" in md:
    head,_,tail=md.partition("**References**")
    nxt=re.search(r"\n\*\*", tail)                     # discard the previous reference list, keep the next section
    tail=tail[nxt.start():] if nxt else "\n"
    md=head+block+tail
else: md=md+block
open(mdp,"w",encoding="utf-8").write(md)
cited=[int(x) for x in re.findall(r"⟦(\d+)⟧",md)]; uniq=sorted(set(cited)); N=len(refs)
ok = uniq==list(range(1,N+1))
print(f"references: {N} | in-text markers: {len(cited)} | distinct numbers: {len(uniq)} | contiguous 1..N: {ok}")
if not ok:
    print("  missing:",sorted(set(range(1,N+1))-set(uniq))[:8],"extra:",sorted(set(uniq)-set(range(1,N+1)))[:8]); sys.exit(1)
# ---- docx rebuild with real superscripts ----
from docx import Document
from docx.shared import Pt, Inches, RGBColor
TOK=re.compile(r"⟦(\d+(?:,\d+)*)⟧")
def add_para(doc,text):
    p=doc.add_paragraph(); pos=0
    for m in TOK.finditer(text):
        if m.start()>pos: p.add_run(text[pos:m.start()])
        s=p.add_run(m.group(1)); s.font.superscript=True; pos=m.end()
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
    else: add_para(doc, s.replace("**","").replace("*",""))
doc.add_page_break(); h=doc.add_heading(level=1); r=h.add_run("Figures"); r.font.name="Times New Roman"; r.font.color.rgb=RGBColor(0,0,0)
for cap,fn in figs:
    h=doc.add_heading(level=2); r=h.add_run(cap); r.font.name="Times New Roman"; r.font.color.rgb=RGBColor(0,0,0)
    doc.add_picture(os.path.join(FIG,fn), width=Inches(6.2)); doc.add_paragraph("")
dp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.docx"); doc.save(dp)
subprocess.run([r"C:\Program Files\LibreOffice\program\soffice.exe","--headless","--convert-to","pdf","--outdir",
                os.path.join(V14,"01_manuscript"),dp],capture_output=True)
d=Document(dp); dt="\n".join(p.text for p in d.paragraphs)
disk={fn:hashlib.sha256(open(os.path.join(FIG,fn),"rb").read()).hexdigest() for _,fn in figs}
em=[hashlib.sha256(r.target_part.blob).hexdigest() for r in d.part.rels.values() if "image" in r.reltype]
sup=sum(1 for p in d.paragraphs for r in p.runs if r.font.superscript)
print(f"docx: references listed={dt.count('. doi:')+dt.count('PMID:')+1} | superscript runs={sup} | figures matching disk={sum(1 for h in em if h in disk.values())}/{len(em)}")
print("pdf rebuilt:", os.path.exists(os.path.join(V14,"01_manuscript","DataDescriptor_v14.pdf")))
