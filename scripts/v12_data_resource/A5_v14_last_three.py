#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: final three references via PubMed phrase search with a title-similarity guard."""
import difflib, json, os, subprocess, time, urllib.parse
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; OUT=os.path.join(V14,"results")
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
def eut(path,**p):
    url=f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{path}?"+urllib.parse.urlencode(p)
    return subprocess.run(["curl","-sS","--max-time","60",url],capture_output=True,text=True).stdout
NEED={"tcga_paad":"Integrated genomic characterization of pancreatic ductal adenocarcinoma",
      "tcga_lihc":"Comprehensive and integrative genomic characterization of hepatocellular carcinoma",
      "scipy":"SciPy 1.0: fundamental algorithms for scientific computing in Python"}
merged=meta.get("crossref",{})
for key,title in NEED.items():
    txt=eut("esearch.fcgi",db="pubmed",term=f'"{title}"[Title]',retmode="json",retmax=5)
    try: ids=json.loads(txt)["esearchresult"]["idlist"]
    except Exception: ids=[]
    if not ids:
        txt=eut("esearch.fcgi",db="pubmed",term=title,retmode="json",retmax=5)
        try: ids=json.loads(txt)["esearchresult"]["idlist"]
        except Exception: ids=[]
    js=json.loads(eut("esummary.fcgi",db="pubmed",id=",".join(ids),retmode="json") or "{}")
    best=None; score=0
    for uid,rec in (js.get("result") or {}).items():
        if uid=="uids": continue
        t=(rec.get("title") or "").strip().rstrip(".")
        r=difflib.SequenceMatcher(None,t.lower(),title.lower()).ratio()
        if r>score: score=r; best=(uid,rec,t)
    if best and score>=0.9:
        uid,rec,t=best; auth=rec.get("authors") or []
        doi=""
        for a in rec.get("articleids") or []:
            if a.get("idtype")=="doi": doi=a.get("value","")
        merged[key]=dict(first_author=(auth[0]["name"] if auth else "Unknown"),n_authors=len(auth),title=t,
                         journal=rec.get("source") or "",year=(rec.get("pubdate") or "")[:4],
                         volume=rec.get("volume") or "",pages=rec.get("pages") or "",doi=doi,pmid=uid)
        print(f"  {key:10s} OK {score:.3f} | {merged[key]['first_author']} {merged[key]['year']} {merged[key]['journal']} | {t[:58]}")
    else:
        print(f"  {key:10s} unresolved (best={score:.3f}) -> will not be cited")
    time.sleep(0.4)
meta["crossref"]=merged
json.dump(meta, open(os.path.join(OUT,"v14_reference_metadata.json"),"w",encoding="utf-8"), indent=1)
print("\nvalidated entries:", len(merged))
