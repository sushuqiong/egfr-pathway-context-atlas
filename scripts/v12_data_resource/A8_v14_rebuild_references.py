#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 (A8): rebuild the reference apparatus in one pass with non-numeric keys and a single regex mapping.

Verification (must all hold, otherwise the script fails loudly):
  * the cited numbers are exactly 1..N with no gaps or duplicates
  * every reference entry is cited at least once
  * no marker points at a number that has no entry
"""
import csv, json, os, re, subprocess, sys
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; PK=os.path.join(V14,"dataset_package"); OUT=os.path.join(V14,"results")
mdp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md")
repo=r"C:\Users\fengq\Desktop\EGFR\egfr-pathway-context-atlas"
prev=subprocess.run(["git","-C",repo,"show","HEAD:manuscript/DataDescriptor_v14.md"],capture_output=True,text=True)
assert prev.returncode==0 and len(prev.stdout)>5000, "cannot recover the pre-A6 manuscript"
md=prev.stdout
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
summ=meta["summaries"]; cr=meta["crossref"]
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv"))
CR_AUTHORS={k:"The Cancer Genome Atlas Research Network" for k in ("tcga_luad","tcga_crc","tcga_stad","tcga_paad","tcga_lihc","tcga_esca")}
def tool_entry(key):
    m=cr.get(key)
    if not m: return None
    au=CR_AUTHORS.get(key) or (m.get("first_author") or "Unknown")
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
# ---- clean the text of any previous citation numbering ----
md=re.sub(r"⟦[^⟧]*⟧","",md); md=re.sub(r"⟪[^⟫]*⟫","",md)
md=re.sub(r"(GEOquery|Genomic Data Commons|cBioPortal|CELLxGENE Discover|GEO|\bGSVA\b|xCell|metafor|Hartung-Knapp|limma)\d+(?:,\d+)*", r"\1", md)
md=re.sub(r"(R 4\.4\.1)\d+", r"\1", md)
ENTRIES={}
def ins(pattern, marker, key=None, count=1):
    global md
    md,n=re.subn(pattern, lambda m: m.group(0)+marker, md, count=count)
    if n==0: print("  WARN anchor missing:",pattern[:55])
ins(r"Gene Expression Omnibus \(GEO\)","⟪geo⟫"); ENTRIES["geo"]=tool_entry("geo")
ins(r"retrieved with GEOquery","⟪geoquery⟫"); ENTRIES["geoquery"]=tool_entry("geoquery")
ins(r"Genomic Data Commons","⟪gdc⟫"); ENTRIES["gdc"]=tool_entry("gdc")
ins(r"cBioPortal","⟪cbio1⟫⟪cbio2⟫"); ENTRIES["cbio1"]=tool_entry("cbio1"); ENTRIES["cbio2"]=tool_entry("cbio2")
ins(r"CELLxGENE Discover","⟪cellxgene⟫"); ENTRIES["cellxgene"]=tool_entry("cellxgene")
ins(r"from six tumour molecular contexts of The Cancer Genome Atlas",
    "⟪tcga_luad⟫⟪tcga_crc⟫⟪tcga_stad⟫⟪tcga_paad⟫⟪tcga_lihc⟫⟪tcga_esca⟫")
for k in CR_AUTHORS: ENTRIES[k]=tool_entry(k)
# cohort accessions, each cited at the point where it is listed
accs=[]
for r in reg:
    a=r["accession"]; p=r.get("origin_pmid","")
    if p.isdigit() and a not in accs: accs.append(a)
pmid_of={r["accession"]:r["origin_pmid"] for r in reg}
listed=", ".join(f"{a}⟪cohort_{a}⟫" for a in accs)
md=re.sub(r"listed accession by accession in 01_cohort_registry/cohort_registry\.csv",
          "listed accession by accession in 01_cohort_registry/cohort_registry.csv and cited here in registry order ("+listed+")", md, count=1)
for a in accs:
    ENTRIES[f"cohort_{a}"]=cohort_entry(pmid_of[a])
ins(r"collection identifiers are listed in 01_cohort_registry/cellxgene_sources\.csv",
    "⟪cellx_crc⟫⟪cellx_ibd⟫⟪cellx_stad⟫")
for k,v in CELLX.items(): ENTRIES[k]=v
ins(r"one GEO series \(asthma, GSE193816\)","⟪asthma⟫"); ENTRIES["asthma"]=ASTHMA
ins(r"GSVA value","⟪gsva⟫"); ENTRIES["gsva"]=tool_entry("gsva")
ins(r"xCell v1\.1\.0","⟪xcell⟫"); ENTRIES["xcell"]=tool_entry("xcell")
ins(r"handled by limma","⟪limma⟫"); ENTRIES["limma"]=tool_entry("limma")
ins(r"random-effects meta-analysis \(metafor","⟪metafor⟫"); ENTRIES["metafor"]=tool_entry("metafor")
ins(r"Hartung-Knapp","⟪hk2001⟫⟪kh2003⟫"); ENTRIES["hk2001"]=tool_entry("hk2001"); ENTRIES["kh2003"]=tool_entry("kh2003")
ins(r"Benjamini-Hochberg \(BH\)","⟪bh1995⟫"); ENTRIES["bh1995"]=tool_entry("bh1995")
ins(r"Hedges small-sample correction","⟪hedges1981⟫"); ENTRIES["hedges1981"]=tool_entry("hedges1981")
ins(r"\bR 4\.4\.1","⟪r_core⟫"); ENTRIES["r_core"]=R_CORE
# ---- single-pass numbering by first appearance ----
keys=sorted({m.group(1) for m in re.finditer(r"⟪([A-Za-z_0-9]+)⟫", md)}, key=lambda k: md.index(f"⟪{k}⟫"))
num={k:i+1 for i,k in enumerate(keys)}
md=re.sub(r"⟪([A-Za-z_0-9]+)⟫", lambda m: f"⟦{num[m.group(1)]}⟧", md)
missing=[k for k in keys if not ENTRIES.get(k)]
refs=[(num[k], ENTRIES[k]) for k in keys if ENTRIES.get(k)]
refblock="**References**\n"+"\n".join(f"{n}. {t}" for n,t in sorted(refs))+"\n\n"
if "**References**" in md:
    head,_,tail=md.partition("**References**"); md=head+refblock+tail.lstrip("\n")
else:
    md=md+refblock
open(mdp,"w",encoding="utf-8").write(md)
# ---- verification ----
cited=[int(x) for x in re.findall(r"⟦(\d+)⟧", md)]
uniq=sorted(set(cited)); N=len(refs)
problems=[]
if missing: problems.append(f"keys without an entry: {missing}")
if uniq!=list(range(1,N+1)): problems.append(f"cited numbers not 1..{N}: missing {sorted(set(range(1,N+1))-set(uniq))[:6]} extra {sorted(set(uniq)-set(range(1,N+1)))[:6]}")
dups=[n for n in uniq if cited.count(n)>1]
print(f"references: {N} | markers in text: {len(cited)} | distinct numbers: {len(uniq)} | numbers cited more than once: {len(dups)}")
print("verification:", "PASS" if not problems else "FAIL -> "+"; ".join(problems))
print("\norder (first 8):")
for n,t in sorted(refs)[:8]: print(f"  {n}. {t[:92]}")
print("order (last 4):")
for n,t in sorted(refs)[-4:]: print(f"  {n}. {t[:92]}")
if problems: sys.exit(1)
