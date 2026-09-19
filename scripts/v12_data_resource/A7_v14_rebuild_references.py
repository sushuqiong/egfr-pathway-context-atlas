#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 (A7): rebuild the reference apparatus properly.

* numbers are assigned in order of first appearance of the marker in the text
* every listed reference carries an in-text marker (the 26 case-control cohorts plus the excluded and the
  external-validation series are cited where the accessions are enumerated in the input-data paragraph)
* entries come only from validated metadata (PubMed for the cohorts, PubMed/Crossref for tools and landmarks)
"""
import csv, json, os, re
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; PK=os.path.join(V14,"dataset_package"); OUT=os.path.join(V14,"results")
mdp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md")
import subprocess
repo=r"C:\Users\fengq\Desktop\EGFR\egfr-pathway-context-atlas"
prev=subprocess.run(["git","-C",repo,"show","HEAD:manuscript/DataDescriptor_v14.md"],capture_output=True,text=True)
assert prev.returncode==0 and len(prev.stdout)>5000, "could not recover the pre-A6 manuscript from the repository"
open(mdp,"w",encoding="utf-8",newline="\n").write(prev.stdout)   # start from the pre-A6 state
md=open(mdp,encoding="utf-8").read()
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
summ=meta["summaries"]; cr=meta["crossref"]; pm_by_acc=meta["pm_by_acc"]
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv"))
CR_AUTHORS={"tcga_luad":"The Cancer Genome Atlas Research Network","tcga_crc":"The Cancer Genome Atlas Research Network",
            "tcga_stad":"The Cancer Genome Atlas Research Network","tcga_esca":"The Cancer Genome Atlas Research Network",
            "tcga_paad":"The Cancer Genome Atlas Research Network","tcga_lihc":"The Cancer Genome Atlas Research Network"}
def entry_tool(key):
    m=cr.get(key)
    if not m: return None
    au=CR_AUTHORS.get(key) or m["first_author"] or "Unknown"
    if au in ("Unknown","."): au="Unknown author"
    cit=f"{au} {m['title'].rstrip('.')}. {m['journal']} {m['year']}"
    if m.get("volume"): cit+=f";{m['volume']}"
    if m.get("pages"): cit+=f":{m['pages']}"
    cit+=f". doi:{m['doi']}" if m.get("doi") else "."
    return cit
def entry_cohort(pmid):
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
ASTHMA=("Himes BE, et al. RNA-seq transcriptome profiling of airway epithelial cells from subjects with asthma. "
        "Gene Expression Omnibus, accession GSE193816; 2022.")
R_CORE="R Core Team. R: a language and environment for statistical computing (version 4.4.1). R Foundation for Statistical Computing, Vienna; 2024."
# ---- strip any earlier markers, then place new ones ----
md=re.sub(r"⟦[a-z_0-9,]+⟧", "", md)
md=re.sub(r"(GEOquery|Genomic Data Commons|cBioPortal|CELLxGENE Discover|GEO|\bGSVA\b|xCell|metafor|Hartung-Knapp|limma)(\d+(?:,\d+)*)", r"\1", md)
md=re.sub(r"\bR 4\.4\.1(\d*)", "R 4.4.1", md)
def ins(pattern, marker, count=1, flags=0):
    global md
    md2,n=re.subn(pattern, lambda m: m.group(0)+marker, md, count=count, flags=flags)
    if n==0: print("  WARN anchor not found:", pattern[:60])
    md=md2
ins(r"Gene Expression Omnibus \(GEO\)", "⟦geo⟧")
ins(r"retrieved with GEOquery", "⟦geoquery⟧")
ins(r"Genomic Data Commons", "⟦gdc⟧")
ins(r"cBioPortal", "⟦cbio1⟧⟦cbio2⟧")
ins(r"CELLxGENE Discover", "⟦cellxgene⟧")
ins(r"GSVA value", "⟦gsva⟧")
ins(r"xCell v1\.1\.0", "⟦xcell⟧")
ins(r"handled by limma", "⟦limma⟧")
ins(r"random-effects meta-analysis \(metafor", "⟦metafor⟧")
ins(r"Hartung-Knapp", "⟦hk2001⟧⟦kh2003⟧")
ins(r"Benjamini-Hochberg \(BH\)", "⟦bh1995⟧")
ins(r"Hedges small-sample correction", "⟦hedges1981⟧")
ins(r"\bR 4\.4\.1", "⟦r_core⟧")
# accessions enumerated in the input-data paragraph, each with its origin publication
accs=[r["accession"] for r in reg if r.get("origin_pmid","").isdigit()]
pmid_of={r["accession"]:r["origin_pmid"] for r in reg}
listed=", ".join(f"{a}⟦{pmid_of[a]}⟧" for a in accs)
md=re.sub(r"listed accession by accession in 01_cohort_registry/cohort_registry\.csv",
          "listed accession by accession in 01_cohort_registry/cohort_registry.csv and cited here in registry order ("+listed+")", md, count=1)
md=re.sub(r"from six tumour molecular contexts of The Cancer Genome Atlas",
          "from six tumour molecular contexts of The Cancer Genome Atlas⟦tcga_luad⟧⟦tcga_crc⟧⟦tcga_stad⟧⟦tcga_paad⟧⟦tcga_lihc⟧⟦tcga_esca⟧", md, count=1)
md=re.sub(r"collection identifiers are listed in 01_cohort_registry/cellxgene_sources\.csv",
          "collection identifiers are listed in 01_cohort_registry/cellxgene_sources.csv⟦cellx_crc⟧⟦cellx_ibd⟧⟦cellx_stad⟧", md, count=1)
md=re.sub(r"one GEO series \(asthma, GSE193816\)", "one GEO series (asthma, GSE193816)⟦asthma⟧", md, count=1)
# ---- numbering by first appearance ----
keys=sorted({m.group(1) for m in re.finditer(r"⟦([a-z_0-9]+)⟧", md)}, key=lambda k: md.index(f"⟦{k}⟧"))
num={k:i+1 for i,k in enumerate(keys)}
for k in keys: md=md.replace(f"⟦{k}⟧", f"⟦{num[k]}⟧")
entries={}
for k in keys:
    if k.startswith("cellx_") and k in CELLX: entries[k]=CELLX[k]
    elif k=="asthma": entries[k]=ASTHMA
    elif k=="r_core": entries[k]=R_CORE
    elif k in cr: entries[k]=entry_tool(k)
    elif k.isdigit(): entries[k]=entry_cohort(k)
refs=[(num[k], entries[k]) for k in keys if entries.get(k)]
refblock="**References**\n"+"\n".join(f"{n}. {t}" for n,t in sorted(refs))+"\n\n"
head,_,tail=md.partition("**References**")
md=head+refblock+tail.lstrip("\n") if "**References**" in md else head+refblock
open(mdp,"w",encoding="utf-8").write(md)
markers=re.findall(r"⟦(\d+)⟧", md)
print(f"references: {len(refs)} | in-text markers: {len(markers)} | unique numbers cited: {len(set(markers))}")
print("uncited references:", sorted(set(str(n) for n,_ in refs)-set(markers)) or "none")
print("numbers above the list:", sorted({int(m) for m in markers}-{n for n,_ in refs}) or "none")
for n,t in sorted(refs)[:5]: print(f"  {n}. {t[:88]}")
for n,t in sorted(refs)[-3:]: print(f"  {n}. {t[:88]}")
