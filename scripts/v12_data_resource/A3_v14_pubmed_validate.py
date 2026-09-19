#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: re-resolve the doubtful reference matches through PubMed with strict validation
(title keywords AND journal AND year window must all match, otherwise the entry is dropped)."""
import json, os, subprocess, time, urllib.parse
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; OUT=os.path.join(V14,"results")
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
def eutils(path, **params):
    url=f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{path}?"+urllib.parse.urlencode(params)
    return subprocess.run(["curl","-sS","--max-time","60",url],capture_output=True,text=True).stdout
def esum(ids):
    if not ids: return {}
    js=json.loads(eutils("esummary.fcgi",db="pubmed",id=",".join(ids),retmode="json") or "{}")
    out={}
    for uid,rec in (js.get("result") or {}).items():
        if uid=="uids": continue
        auth=rec.get("authors") or []
        doi=""
        for a in rec.get("articleids") or []:
            if a.get("idtype")=="doi": doi=a.get("value","")
        out[uid]=dict(first_author=(auth[0]["name"] if auth else "Unknown"),n_authors=len(auth),
                      title=(rec.get("title") or "").strip().rstrip("."),journal=rec.get("source") or "",
                      year=(rec.get("pubdate") or "")[:4],volume=rec.get("volume") or "",
                      pages=rec.get("pages") or "",doi=doi)
    return out
TARGETS={
 "tcga_luad": ("Comprehensive molecular profiling of lung adenocarcinoma", ["lung adenocarcinoma"], ["nature"], (2013,2015)),
 "tcga_crc":  ("Comprehensive molecular characterization of human colon and rectal cancer", ["colon and rectal"], ["nature"], (2011,2014)),
 "tcga_stad": ("Comprehensive molecular characterization of gastric adenocarcinoma", ["gastric adenocarcinoma"], ["nature"], (2013,2015)),
 "tcga_paad": ("Integrated genomic characterization of pancreatic ductal adenocarcinoma", ["pancreatic"], ["cancer cell","nature"], (2016,2018)),
 "tcga_lihc": ("Comprehensive and integrative genomic characterization of hepatocellular carcinoma", ["hepatocellular carcinoma"], ["cell"], (2016,2018)),
 "tcga_esca": ("Integrated genomic characterization of oesophageal carcinoma", ["oesophageal carcinoma","esophageal carcinoma"], ["nature"], (2016,2018)),
 "scipy":     ("SciPy 1.0 fundamental algorithms for scientific computing in Python", ["scipy 1.0"], ["nature methods"], (2019,2021)),
 "numpy":     ("Array programming with NumPy", ["array programming with numpy"], ["nature"], (2019,2021)),
 "gdc":       ("Toward a Shared Vision for Cancer Genomic Data", ["shared vision for cancer genomic data"], [], (2015,2017)),
 "kh2003":    ("Improved tests for a random effects meta-regression with a single covariate", ["improved tests","random effects meta-regression"], ["statistics in medicine"], (2002,2004)),
 "dl1986":    ("Meta-analysis in clinical trials", ["meta-analysis in clinical trials"], ["controlled clinical trials"], (1985,1987)),
}
ok={}; dropped=[]
for key,(q,keys,journals,(y0,y1)) in TARGETS.items():
    txt=eutils("esearch.fcgi",db="pubmed",term=q,retmode="json",retmax=8)
    try: ids=json.loads(txt)["esearchresult"]["idlist"]
    except Exception: ids=[]
    summ=esum(ids)
    pick=None
    for uid in ids:
        r=summ.get(uid)
        if not r: continue
        tl=r["title"].lower()
        if not all(k.lower() in tl for k in keys): continue
        if journals and not any(j in (r["journal"] or "").lower() for j in journals): continue
        y=int(r["year"]) if r["year"].isdigit() else 0
        if not (y0<=y<=y1): continue
        pick=r; pick["pmid"]=uid; break
    if pick: ok[key]=pick; print(f"  {key:10s} OK   {pick['first_author']} {pick['year']} {pick['journal'][:28]} | {pick['title'][:58]}")
    else: dropped.append(key); print(f"  {key:10s} DROPPED (no validated match)")
    time.sleep(0.4)
merged=meta.get("crossref",{})
merged.update(ok)
# drop the entries that failed validation earlier and were replaced by nothing
for bad in ["eps","tmps"]: merged.pop(bad,None)
meta["crossref"]=merged; meta["crossref_unresolved"]=dropped
json.dump(meta, open(os.path.join(OUT,"v14_reference_metadata.json"),"w",encoding="utf-8"), indent=1)
print("\ntotal validated method/database entries:", len(merged), "| dropped:", dropped or "none")
