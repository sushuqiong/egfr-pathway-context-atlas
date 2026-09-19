#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: merge the remaining validated metadata (PubMed lookups for GEOquery and CELLxGENE, plus the two
TCGA context papers) into the reference metadata file."""
import json, os, subprocess, time, urllib.parse
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; OUT=os.path.join(V14,"results")
p=os.path.join(OUT,"v14_reference_metadata.json"); meta=json.load(open(p,encoding="utf-8"))
def eut(path,**kw):
    url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"+path+"?"+urllib.parse.urlencode(kw)
    return subprocess.run(["curl","-sS","--max-time","60",url],capture_output=True,text=True).stdout
def esum(ids):
    js=json.loads(eut("esummary.fcgi",db="pubmed",id=",".join(ids),retmode="json") or "{}")
    out={}
    for uid,rec in (js.get("result") or {}).items():
        if uid=="uids": continue
        a=rec.get("authors") or []
        doi=""
        for x in rec.get("articleids") or []:
            if x.get("idtype")=="doi": doi=x.get("value","")
        out[uid]=dict(first_author=(a[0]["name"] if a else "Unknown"),n_authors=len(a),
                      title=(rec.get("title") or "").strip().rstrip("."),journal=rec.get("source") or "",
                      year=(rec.get("pubdate") or "")[:4],volume=rec.get("volume") or "",
                      pages=rec.get("pages") or "",doi=doi,pmid=uid)
    return out
cr=meta["crossref"]; look=meta.get("lookups",{})
add={}
for key,lookup in [("geoquery","geoquery"),("cellxgene","cellxgene")]:
    pid=look.get(lookup)
    if pid:
        rec=esum([pid]).get(pid)
        if rec: add[key]=rec; print(f"  {key:9s} from PubMed {pid}: {rec['first_author']} {rec['year']} {rec['journal']}")
    time.sleep(0.3)
for key,pid in [("tcga_paad","28810144"),("tcga_lihc","28622513")]:
    rec=esum([pid]).get(pid)
    if rec:
        rec["first_author"]="The Cancer Genome Atlas Research Network"
        add[key]=rec; print(f"  {key:9s} from PubMed {pid}: {rec['journal']} {rec['year']} | {rec['title'][:60]}")
    time.sleep(0.3)
cr.update(add); meta["crossref"]=cr
json.dump(meta, open(p,"w",encoding="utf-8"), indent=1)
print("\ncrossref keys now:", len(cr), "|", sorted(cr))
