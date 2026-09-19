#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 (B5): finish the reference list and apply the editorial fixes found in the editor/reviewer pass.

Reference fixes : entries 37 and 46 forced to their verified citations.
Editorial fixes : Data Availability lists every accession; Code Availability names the repository tag and
                  the shipped code; an author/affiliation/correspondence block and keywords are added;
                  Technical Validation no longer presents biological findings as results.
"""
import os, re, subprocess, json
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; PK=os.path.join(V14,"dataset_package")
mdp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mdp,encoding="utf-8").read()
# ---------- 1. references 37 and 46 ----------
R37=("Cerami, E. et al. The cBio Cancer Genomics Portal: An Open Platform for Exploring Multidimensional Cancer "
     "Genomics Data. *Cancer Discov.* **2**, 401-404 (2012). https://doi.org/10.1158/2159-8290.CD-12-0095.")
R46=("Viechtbauer, W. et al. Conducting meta-analyses in R with the metafor package. *J. Stat. Softw.* **36**, "
     "1-48 (2010). https://doi.org/10.18637/jss.v036.i03.")
head,_,rest=md.partition("**References**")
nxt=re.search(r"\n\*\*",rest); tail=rest[nxt.start():] if nxt else "\n"; body=rest[:nxt.start()] if nxt else rest
chunks=re.split(r"\n(?=\d+\.\s)", body.strip())
out=[]
for ch in chunks:
    m=re.match(r"^(\d+)\.\s+(.*)$", ch, re.S)
    if not m: continue
    n,t=m.group(1), re.sub(r"\s+"," ",m.group(2)).strip()
    t=re.sub(r"</?(i|b|sub|sup)>","",t)
    if n=="37": t=R37
    if n=="46": t=R46
    out.append((n,t))
if len(out)<40: raise SystemExit(f"ABORT: only {len(out)} entries parsed")
block="**References**\n"+"\n".join(f"{n}. {t}" for n,t in out)+"\n\n"
md=head+block+tail.lstrip("\n")
print("references:",len(out),"| Correction left:",sum(1 for n,t in out if "Correction" in t),
      "| markup left:",sum(1 for n,t in out if re.search(r'</?(i|b)>',t)),
      "| links:",sum(1 for n,t in out if "https://" in t))
# ---------- 2. author block + keywords ----------
lines=md.split("\n")
if not any(l.startswith("**Author information**") for l in md.split("\n")):
    ti=next((i for i,l in enumerate(lines) if l.startswith("# ")),0)
    block_a=("","**Author information**",
      "Shuqiong Su^1,*  (ORCID: to be supplied by the author)",
      "",
      "^1 Department of Gastroenterology, Guangxi Medical University Cancer Hospital, Nanning, China",
      "",
      "*Correspondence: liuaiqun_2004@163.com  (confirm the corresponding author and add ORCID iDs before submission)",
      "","**Keywords**",
      "harmonized transcriptome resource; signaling module scores; tissue-compartment scores; cross-disease comparability;"
      " gene coverage; single-cell reference; data descriptor","")
    lines=lines[:ti+1]+list(block_a)+lines[ti+1:]
    md="\n".join(lines); print("author block and keywords inserted")
# ---------- 3. Data Availability ----------
ACC=["GSE32863","GSE19804","GSE10072","GSE44076","GSE41258","GSE23878","GSE75214","GSE87473","GSE179285","GSE4302",
     "GSE43696","GSE67472","GSE27342","GSE63089","GSE13911","GSE15471","GSE28735","GSE62452","GSE57957","GSE62232",
     "GSE23400","GSE20347","GSE76925","GSE47460","GSE33814","GSE66676"]
DA=("**Data Availability**\n"
    "All source data are public. The 26 case-control bulk cohorts are the GEO series "+", ".join(ACC)+"; the treatment-response series "
    "GSE16879 and the external-validation series GSE39582 were retrieved but are not part of the case-control resource. The single-cell inputs are the "
    "CZ CELLxGENE Discover collections 1cbfb478-2c7f-4d15-b522-9f74e9fe52a8 (colorectal cancer), 7c7bd6c2-925b-4034-baab-620ef1b760e1 (inflammatory bowel "
    "disease) and f11cb29c-b546-4738-9bd8-66ea621a7bd5 (gastric cancer) together with GEO series GSE193816 (asthma). The tumour molecular layers come from the "
    "NCI Genomic Data Commons projects TCGA-LUAD, TCGA-COADREAD, TCGA-STAD, TCGA-PAAD, TCGA-LIHC and TCGA-ESCA, accessed through cBioPortal. Every accession is "
    "cited together with its origin publication in the reference list, and the per-file registry is 01_cohort_registry/cohort_registry.csv. The curated resource, "
    "including the analysis code, is deposited in Zenodo under a CC-BY-4.0 licence: https://doi.org/[DOI to be inserted after deposit]. No new human specimens "
    "were collected and no controlled-access data were used. Upstream data remain under their own terms (GEO series terms, TCGA/GDC open-access terms and "
    "CELLxGENE dataset terms).\n\n")
md=re.sub(r"\*\*Data Availability\*\*.*?(?=\n\*\*)", DA.rstrip("\n")+"\n", md, flags=re.S)
# ---------- 4. Code Availability ----------
CA=("**Code Availability**\n"
    "The analysis code is in the repository https://github.com/sushuqiong/cross-disease-transcriptomic-resource (tag v14.0 of this manuscript) and is archived "
    "inside the deposit as 11_code/, with README_code.md describing each script, 10_environment/run_order.md giving the execution order, and environment.txt "
    "recording the software versions (R 4.4.1 with GSVA, metafor, survival, limma, GEOquery, xCell, ggplot2, patchwork; Python 3.11 with numpy, h5py, scipy, "
    "python-docx and Pillow). Paths inside the scripts point to the author's working directories and must be adjusted to the deposit layout; all inputs they "
    "require are shipped in the deposit except the raw source matrices, which are downloaded from the accessions above.\n\n")
md=re.sub(r"\*\*Code Availability\*\*.*?(?=\n\*\*)", CA.rstrip("\n")+"\n", md, flags=re.S)
# ---------- 5. Technical Validation: remove result-like biology, keep data-quality evidence ----------
md=md.replace("Histology and mutation layer: the oesophageal layer is restricted to squamous histology ({tp53['denominator_n']} patients)",
              "Annotation layers: the oesophageal layer is restricted to squamous histology ({tp53['denominator_n']} patients)")
md=re.sub(r"The resource presents no biological conclusions; the mutation and copy-number values describe the annotation layer only\.",
          "", md)
if "no biological conclusions" not in md:
    md=md.replace("Coverage and composition are shown in Figure 1",
                  "This section reports data-quality and consistency checks only; the resource makes no biological claims, and the mutation, "
                  "copy-number and single-cell counts below describe the annotation layers rather than study findings. Coverage and composition are shown in Figure 1",1)
# 6. explicit statement that cross-pooling is restricted to comparable control classes
if "control classes are not pooled" not in md:
    md=md.replace("Effect sizes and pooling.", "Effect sizes and pooling. Effects are pooled only within a context, and cohorts whose control tissue belongs to different control classes are never pooled silently. ",1)
open(mdp,"w",encoding="utf-8",newline="\n").write(md)
checks={
 "author block":"**Author information**" in md,
 "keywords":"**Keywords**" in md,
 "data availability accessions":md.count("GSE66676")>=2,
 "code tag":"tag v14.0" in md,
 "no biological claims line":"no biological claims" in md,
 "references":len(re.findall(r"(?m)^\d+\. ", md.split('**References**')[1].split("\n**")[0]))}
print("editorial checks:", checks)
