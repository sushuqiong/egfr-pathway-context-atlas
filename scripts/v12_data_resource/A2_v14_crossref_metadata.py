#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: resolve the remaining reference metadata through Crossref with strict keyword validation.

Every candidate title returned by Crossref must contain the expected keywords, otherwise the entry is
left unresolved (nothing is invented, and a wrong match cannot slip in silently).
"""
import json, os, subprocess, time, urllib.parse
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; OUT=os.path.join(V14,"results")
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
def crossref(query, expect, rows=4):
    url="https://api.crossref.org/works?rows=%d&query.bibliographic=%s" % (rows, urllib.parse.quote(query))
    r=subprocess.run(["curl","-sS","--max-time","45","-A","egfr-resource-build/1.0 (mailto:liuaiqun_2004@163.com)",url],
                     capture_output=True,text=True)
    try: items=json.loads(r.stdout)["message"]["items"]
    except Exception: return None
    for it in items:
        t=(it.get("title") or [""])[0]
        tl=t.lower()
        if all(k.lower() in tl for k in expect):
            auth=it.get("author") or []
            first=f"{auth[0].get('family','')} {auth[0].get('given','')[:1]}.".strip() if auth else "Unknown"
            yr=""
            for k in ("published-print","published-online","issued"):
                if it.get(k,{}).get("date-parts"): yr=str(it[k]["date-parts"][0][0]); break
            return dict(first_author=first, n_authors=len(auth), title=t.strip().rstrip("."),
                        journal=(it.get("container-title") or [""])[0], year=yr,
                        volume=it.get("volume",""), pages=it.get("page",""), doi=it.get("DOI",""))
    return None
TARGETS={
 "geo":        ("NCBI GEO archive for functional genomics data sets update", ["geo","functional genomics"]),
 "cbio1":      ("The cBio cancer genomics portal an open platform for exploring multidimensional cancer genomics data", ["cbio","cancer genomics"]),
 "cbio2":      ("Integrative analysis of complex cancer genomics and clinical profiles using the cBioPortal", ["integrative analysis","cbioportal"]),
 "gsva":       ("GSVA gene set variation analysis for microarray and RNA-seq data", ["gsva"]),
 "xcell":      ("xCell digitally portraying the tissue cellular heterogeneity landscape", ["xcell"]),
 "limma":      ("limma powers differential expression analyses for RNA-sequencing and microarray studies", ["limma"]),
 "metafor":    ("Conducting meta-analyses in R with the metafor package", ["metafor"]),
 "dl1986":     ("Meta-analysis in clinical trials DerSimonian Laird", ["meta-analysis in clinical trials"]),
 "hk2001":     ("A refined method for the meta-analysis of controlled clinical trials with binary outcome", ["refined method"]),
 "kh2003":     ("Improved tests for a random effects meta-regression with a single covariate", ["improved tests","random effects meta-regression"]),
 "bh1995":     ("Controlling the false discovery rate a practical and powerful approach to multiple testing", ["controlling the false discovery rate"]),
 "hedges1981": ("Distribution theory for Glass's estimator of effect size and related estimators", ["distribution theory","effect size"]),
 "scipy":      ("SciPy 1.0 fundamental algorithms for scientific computing in Python", ["scipy 1.0"]),
 "numpy":      ("Array programming with NumPy", ["array programming with numpy"]),
 "eps":        ("Efficient and accurate construction of genetic linkage maps", ["linkage maps"]),
 "ggplot2":    ("ggplot2 Elegant Graphics for Data Analysis", ["ggplot2"]),
 "patchwork":  ("patchwork the composer of plots", ["patchwork"]),
 "tcga_luad":  ("Comprehensive molecular profiling of lung adenocarcinoma", ["lung adenocarcinoma"]),
 "tcga_crc":   ("Comprehensive molecular characterization of human colon and rectal cancer", ["colon and rectal"]),
 "tcga_stad":  ("Comprehensive molecular characterization of gastric adenocarcinoma", ["gastric adenocarcinoma"]),
 "tcga_paad":  ("Integrated genomic characterization of pancreatic ductal adenocarcinoma", ["pancreatic ductal"]),
 "tcga_lihc":  ("Comprehensive and integrative genomic characterization of hepatocellular carcinoma", ["hepatocellular carcinoma"]),
 "tcga_esca":  ("Integrated genomic characterization of oesophageal carcinoma", ["oesophageal carcinoma"]),
 "gdc":        ("Genomic Data Commons National Cancer Institute", ["genomic data commons"]),
}
res={}
for key,(q,exp) in TARGETS.items():
    got=crossref(q,exp)
    res[key]=got
    print(f"  {key:11s} {'OK  '+got['first_author']+' '+got['year']+' '+got['journal'][:34] if got else 'UNRESOLVED'}")
    time.sleep(0.3)
meta["crossref"]={k:v for k,v in res.items() if v}
meta["crossref_unresolved"]=[k for k,v in res.items() if not v]
json.dump(meta, open(os.path.join(OUT,"v14_reference_metadata.json"),"w",encoding="utf-8"), indent=1)
print("\nresolved:", len(meta["crossref"]), "/", len(TARGETS), "| unresolved:", meta["crossref_unresolved"] or "none")
