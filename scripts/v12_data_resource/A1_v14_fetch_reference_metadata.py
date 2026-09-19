#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: fetch real citation metadata for every reference we intend to list.

Sources
  * the 27 cohort origin publications recorded in the registry (origin_pmid)
  * method, database and tool papers whose identifiers are looked up by PubMed search
Nothing is invented: each entry is taken from the NCBI E-utilities response.
"""
import csv, json, os, subprocess, time, urllib.parse
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; PK=os.path.join(V14,"dataset_package")
OUT=os.path.join(V14,"results"); os.makedirs(OUT,exist_ok=True)
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def eutils(path, **params):
    q=urllib.parse.urlencode(params)
    url=f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{path}?{q}"
    r=subprocess.run(["curl","-sS","--max-time","60",url],capture_output=True,text=True)
    return r.stdout
def fetch_summaries(pmids):
    out={}
    for i in range(0,len(pmids),100):
        chunk=pmids[i:i+100]
        txt=eutils("esummary.fcgi", db="pubmed", id=",".join(chunk), retmode="json")
        try: js=json.loads(txt)
        except Exception: print("  parse error for chunk", chunk[:3]); continue
        for uid,rec in (js.get("result") or {}).items():
            if uid=="uids": continue
            auth=rec.get("authors") or []
            first=auth[0]["name"] if auth else "Unknown"
            doi=""
            for aid in rec.get("articleids") or []:
                if aid.get("idtype")=="doi": doi=aid.get("value","")
            out[uid]=dict(uid=uid, first_author=first, n_authors=len(auth),
                          title=(rec.get("title") or "").strip().rstrip("."),
                          journal=rec.get("source") or "", year=(rec.get("pubdate") or "")[:4],
                          volume=rec.get("volume") or "", issue=rec.get("issue") or "",
                          pages=rec.get("pages") or "", doi=doi)
        time.sleep(0.4)
    return out
# 1. cohort origin publications
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv"))
pm_by_acc={r["accession"]: r.get("origin_pmid","") for r in reg}
pmids=sorted({p for p in pm_by_acc.values() if p and p.isdigit()}, key=int)
print("cohort origin PMIDs:", len(pmids))
# 2. method / database / tool papers: locate by title keywords through esearch
LOOKUP={
 "geo":           'Barrett T[Author] AND "NCBI GEO: archive for functional genomics data sets"[Title]',
 "geoquery":      'Davis S[Author] AND "GEOquery"[Title]',
 "gdc":           '"Genomic Data Commons"[Title] AND (data portal OR cancer)',
 "cbio1":         '"The cBio cancer genomics portal"[Title]',
 "cbio2":         '"Integrative analysis of complex cancer genomics and clinical profiles using the cBioPortal"[Title]',
 "cellxgene":     'CELLxGENE[Title] AND single-cell AND platform',
 "gsva":          '"GSVA: gene set variation analysis for microarray and RNA-seq data"[Title]',
 "xcell":         '"xCell: digitally portraying the tissue cellular heterogeneity landscape"[Title]',
 "limma":         '"limma powers differential expression analyses for RNA-sequencing and microarray studies"[Title]',
 "metafor":       '"Conducting meta-analyses in R with the metafor package"[Title]',
 "dl1986":        '"Meta-analysis in clinical trials"[Title] AND DerSimonian[Author]',
 "hk2001":        '"A refined method for the meta-analysis of controlled clinical trials with binary outcome"[Title]',
 "kh2003":        '"Improved tests for a random effects meta-regression with a single covariate"[Title]',
 "bh1995":        '"Controlling the false discovery rate"[Title] AND Benjamini[Author]',
 "hedges1981":    'Hedges LV[Author] AND 1981[dp] AND "Distribution theory for Glass\'s estimator of effect size"',
 "scipy":         '"SciPy 1.0: fundamental algorithms for scientific computing in Python"[Title]',
 "numpy":         '"Array programming with NumPy"[Title]',
 "h5py":          '"h5py"[Title] AND HDF5',
 "ggplot2":       'Wickham H[Author] AND "ggplot2"[Title] AND (Elegant graphics OR data analysis)',
 "patchwork":     'Pedersen TL[Author] AND patchwork[Title]',
 "dplyr":         'Wickham H[Author] AND dplyr[Title]',
 "tidyr":         'Wickham H[Author] AND tidyr[Title]',
 "esca":          'TCGA[Title] AND oesophageal AND (Integrated genomic characterization)',
 "luad":          'TCGA[Title] AND lung adenocarcinoma AND (Comprehensive molecular profiling OR Integrated genomic)',
 "crc":           'TCGA[Title] AND colorectal AND "Comprehensive molecular characterization"',
 "stad":          'TCGA[Title] AND (gastric adenocarcinoma) AND "Comprehensive molecular characterization"',
 "paad":          'TCGA[Title] AND pancreatic AND "Integrated genomic characterization"',
 "lihc":          'TCGA[Title] AND hepatocellular AND "Comprehensive and integrative genomic characterization"',
 "cellxgene_paper": 'CELLxGENE Discover[Title]',
 "asthma_geo":    'GSE193816 OR (Himes BE[Author] AND airway epithelium AND asthma)',
}
found={}
for key,term in LOOKUP.items():
    txt=eutils("esearch.fcgi", db="pubmed", term=term, retmode="json", retmax=3)
    try: ids=json.loads(txt)["esearchresult"]["idlist"]
    except Exception: ids=[]
    found[key]=ids[0] if ids else ""
    time.sleep(0.4)
print("resolved lookups:", sum(1 for v in found.values() if v), "/", len(found))
allids=sorted(set(pmids)|{v for v in found.values() if v}, key=int)
summ=fetch_summaries(allids)
print("metadata fetched for", len(summ), "of", len(allids))
json.dump(dict(pm_by_acc=pm_by_acc, lookups=found, summaries=summ),
          open(os.path.join(OUT,"v14_reference_metadata.json"),"w",encoding="utf-8"), indent=1)
miss=[k for k,v in found.items() if not v]
print("unresolved lookups:", miss or "none")
for k,v in list(found.items())[:6]:
    if v and v in summ: print(f"  {k}: {summ[v]['first_author']} {summ[v]['year']} {summ[v]['journal']} - {summ[v]['title'][:60]}")
