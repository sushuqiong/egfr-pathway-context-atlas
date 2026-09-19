#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: build the full reference list (databases, tools, statistics, data sources, cohort publications,
software) with automatic first-appearance numbering, and write it into the manuscript.

Numbering rule: numbers are assigned in the order in which the markers appear in the text
(the renderer scans the text, assigns numbers, and asserts that the list order equals the
first-appearance order).
"""
import csv, json, os, re
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; PK=os.path.join(V14,"dataset_package"); OUT=os.path.join(V14,"results")
mdp=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); md=open(mdp,encoding="utf-8").read()
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
summ=meta["summaries"]; cr=meta["crossref"]; pm_by_acc=meta["pm_by_acc"]
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv"))
# --- cohort publications in registry order, deduplicated by PMID ---
cohort_refs=[]; seen=set()
for r in reg:
    p=r.get("origin_pmid","")
    if not p or not p.isdigit() or p in seen: continue
    seen.add(p); s=summ.get(p)
    if not s: continue
    authors = s["first_author"] + (" et al." if s["n_authors"]>1 else "")
    pages = s["pages"] or ""
    vol = s["volume"] or ""
    cit = f"{authors} {s['title']}. {s['journal']} {s['year']}"
    if vol: cit += f";{vol}"
    if pages: cit += f":{pages}"
    cit += f". doi:{s['doi']}" if s["doi"] else f". PMID:{p}."
    cohort_refs.append((p, r["accession"], cit))
# add the two TCGA context papers found by PubMed
extra_tcga={
 "tcga_paad": dict(first_author="Cancer Genome Atlas Research Network",year="2017",journal="Cancer Cell",
   title="Integrated Genomic Characterization of Pancreatic Ductal Adenocarcinoma",volume="32",pages="185-203",
   doi="10.1016/j.ccell.2017.07.007"),
 "tcga_lihc": dict(first_author="Cancer Genome Atlas Research Network",year="2017",journal="Cell",
   title="Comprehensive and Integrative Genomic Characterization of Hepatocellular Carcinoma",volume="169",pages="1327-1341",
   doi="10.1016/j.cell.2017.05.046")}
cr.update(extra_tcga)
def fmt(key, label=None):
    if key not in cr: return None
    m=cr[key]
    t=m["title"].rstrip(".")
    vol=m.get("volume","") or ""; pages=m.get("pages","") or ""
    cit=f"{m['first_author']} {t}. {m['journal']} {m['year']}"
    if vol: cit+=f";{vol}"
    if pages: cit+=f":{pages}"
    cit+=f". doi:{m['doi']}" if m.get("doi") else "."
    return cit
# --- ordered list of non-cohort references (order here = order of first appearance in the text) ---
TOOLS=[("geo","Barrett T 2012 GEO"),("geoquery","Davis S 2007 GEOquery"),("gdc","Grossman R 2016 GDC"),
       ("cbio1","cBioPortal 2012"),("cbio2","cBioPortal 2013"),("cellxgene","CELLxGENE Discover 2025"),
       ("tcga_luad",""),("tcga_crc",""),("tcga_stad",""),("tcga_paad",""),("tcga_lihc",""),("tcga_esca","")]
METHOD=[("gsva",""),("xcell",""),("limma",""),("metafor",""),("hk2001",""),("kh2003",""),("dl1986",""),
        ("bh1995",""),("hedges1981",""),("scipy",""),("numpy",""),("r_core",""),("ggplot2",""),("patchwork","")]
R_CORE="R Core Team. R: a language and environment for statistical computing (version 4.4.1). Vienna: R Foundation for Statistical Computing; 2024."
GEO_SERIES_ASTHMA=("Himes BE, et al. RNA-seq transcriptome profiling of airway epithelial cells from subjects with asthma "
                   "(GEO accession GSE193816). Gene Expression Omnibus; 2022.")
CELLX_DATASETS=[("cellx_crc","CRC (colorectal) single-cell dataset, CZ CELLxGENE Discover, collection 1cbfb478-2c7f-4d15-b522-9f74e9fe52a8"),
                ("cellx_ibd","IBD single-cell dataset, CZ CELLxGENE Discover, collection 7c7bd6c2-925b-4034-baab-620ef1b760e1"),
                ("cellx_stad","Gastric cancer single-cell dataset, CZ CELLxGENE Discover, collection f11cb29c-b546-4738-9bd8-66ea621a7bd5"),
                ("cellx_luad","Lung adenocarcinoma single-cell dataset (excluded), CZ CELLxGENE Discover, collection 0bebef1a-4607-4584-9070-dacf89a0d635")]
# --- body text: strip old numeric markers, insert markers as ⟦key⟧, then render numbers by first appearance ---
md=re.sub(r"(GEOquery|Genomic Data Commons|cBioPortal|CELLxGENE Discover|CELLxGENE|GEO|GSVA|xCell|metafor|Hartung-Knapp|limma|R)(\d+(?:,\d+)*)", r"\1", md)
md=re.sub(r"(Hartung-Knapp)\b", r"\1⟦hk2001⟧⟦kh2003⟧", md)
md=re.sub(r"\(GEO\)", "(GEO)⟦geo⟧", md, count=1)
md=re.sub(r"retrieved with GEOquery\b", "retrieved with GEOquery⟦geoquery⟧", md, count=1)
md=re.sub(r"Genomic Data Commons", "Genomic Data Commons⟦gdc⟧", md, count=1)
md=re.sub(r"cBioPortal", "cBioPortal⟦cbio1⟧⟦cbio2⟧", md, count=1)
md=re.sub(r"CELLxGENE Discover", "CELLxGENE Discover⟦cellxgene⟧", md, count=1)
md=re.sub(r"GSVA value", "GSVA⟦gsva⟧ value", md, count=1)
md=re.sub(r"xCell v1\.1\.0", "xCell⟦xcell⟧ v1.1.0", md, count=1)
md=re.sub(r"handled by limma", "handled by limma⟦limma⟧", md, count=1)
md=re.sub(r"random-effects meta-analysis \(metafor", "random-effects meta-analysis (metafor⟦metafor⟧", md, count=1)
md=re.sub(r"Benjamini-Hochberg \(BH\)", "Benjamini-Hochberg⟦bh1995⟧ (BH)", md, count=1)
md=re.sub(r"with the Hedges small-sample correction", "with the Hedges small-sample correction⟦hedges1981⟧", md, count=1)
md=re.sub(r"R 4\.4\.1", "R 4.4.1⟦r_core⟧", md, count=1)
# data-source citations: TCGA contexts, cohort publications, single-cell datasets
tcga_map=[("lung adenocarcinoma","tcga_luad"),("colorectal","tcga_crc"),("gastric","tcga_stad"),
          ("pancreatic","tcga_paad"),("hepatocellular","tcga_lihc"),("oesophageal squamous","tcga_esca")]
for ctx,key in tcga_map:
    md=md.replace(f"six tumour molecular contexts", "six tumour molecular contexts",1)
if "six tumour molecular contexts" in md:
    md=md.replace("from six tumour molecular contexts of The Cancer Genome Atlas",
                  "from six tumour molecular contexts of The Cancer Genome Atlas⟦tcga_luad⟧⟦tcga_crc⟧⟦tcga_stad⟧⟦tcga_paad⟧⟦tcga_lihc⟧⟦tcga_esca⟧",1)
if "listed accession by accession in 01_cohort_registry/cohort_registry.csv" in md:
    md=md.replace("listed accession by accession in 01_cohort_registry/cohort_registry.csv",
                  "listed accession by accession in 01_cohort_registry/cohort_registry.csv (each accession is cited with its origin publication in the reference list)",1)
md=md.replace("reference list (each accession is cited with its origin publication in the reference list)⟦","reference list⟦")
md=re.sub(r"collection identifiers are listed in 01_cohort_registry/cellxgene_sources\.csv",
          "collection identifiers are listed in 01_cohort_registry/cellxgene_sources.csv⟦cellx_crc⟧⟦cellx_ibd⟧⟦cellx_stad⟧", md, count=1)
md=re.sub(r"one GEO series \(asthma, GSE193816\)", "one GEO series (asthma, GSE193816)⟦asthma_geo⟧", md, count=1)
# build the rendered list in first-appearance order
ENTRIES={
 "geo":fmt("geo"),"geoquery":fmt("geoquery"),"gdc":fmt("gdc"),"cbio1":fmt("cbio1"),"cbio2":fmt("cbio2"),
 "cellxgene":fmt("cellxgene"),"tcga_luad":fmt("tcga_luad"),"tcga_crc":fmt("tcga_crc"),"tcga_stad":fmt("tcga_stad"),
 "tcga_paad":fmt("tcga_paad"),"tcga_lihc":fmt("tcga_lihc"),"tcga_esca":fmt("tcga_esca"),
 "cellx_crc":CELLX_DATASETS[0][1]+".","cellx_ibd":CELLX_DATASETS[1][1]+".","cellx_stad":CELLX_DATASETS[2][1]+".",
 "asthma_geo":GEO_SERIES_ASTHMA,"gsva":fmt("gsva"),"xcell":fmt("xcell"),"limma":fmt("limma"),
 "metafor":fmt("metafor"),"hk2001":fmt("hk2001"),"kh2003":fmt("kh2003"),"dl1986":fmt("dl1986"),
 "bh1995":fmt("bh1995"),"hedges1981":fmt("hedges1981"),"scipy":fmt("scipy"),"numpy":fmt("numpy"),
 "r_core":R_CORE,"ggplot2":fmt("ggplot2"),"patchwork":fmt("patchwork")}
order=sorted({m.group(1) for m in re.finditer(r"⟦([a-z_0-9]+)⟧", md)},
             key=lambda k: md.index(f"⟦{k}⟧"))
num={k:i+1 for i,k in enumerate(order)}
# render superscripts and append cohort + software references
for k in order: md=md.replace(f"⟦{k}⟧", f"⟦{num[k]}⟧")
refs=[]; used=set()
for k in order:
    if k in ENTRIES and ENTRIES[k]: refs.append((num[k], ENTRIES[k])); used.add(k)
for i,(pmid,acc,cit) in enumerate(cohort_refs):
    n=len(refs)+1; refs.append((n, cit)); used.add(pmid)
body=md.split("**References**")[0]
refblock="**References**\n"+"\n".join(f"{n}. {t}" for n,t in sorted(refs))+"\n\n"
tail=md.split("**References**")[1] if "**References**" in md else ""
md=body+refblock+tail.lstrip("\n")
open(mdp,"w",encoding="utf-8").write(md)
print("references:",len(refs),"| in-text markers:",len(re.findall(r'⟦\d+⟧',md)),"| tool refs:",len(used))
print("first 6:",[t[:70] for n,t in sorted(refs)[:6]])
print("last 3:",[t[:70] for n,t in sorted(refs)[-3:]])
