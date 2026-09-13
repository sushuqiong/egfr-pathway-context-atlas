#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch mutation-profiled sample IDs per context from cBioPortal sample lists (v11 eligibility rule)."""
import json, os, urllib.request, csv
RAW = r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\data_raw\cbio_v3"
OUT = r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\reruns\results"
os.makedirs(OUT, exist_ok=True)
API = "https://www.cbioportal.org/api"
def get(url):
    req=urllib.request.Request(url, headers={"Accept":"application/json","User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r: return json.loads(r.read().decode())
rows=[]
for ctx in ["LUAD","CRC","STAD","PAAD","HCC","ESCC"]:
    sl=json.load(open(os.path.join(RAW,f"{ctx}_sample_lists.json")))
    ids=[s["sampleListId"] for s in sl]
    study=[p for p in ids if "tcga" in p][0].rsplit("_",1)[0]
    cand=[i for i in ids if i.endswith("_sequenced")] or [i for i in ids if i.endswith("_mutations")] or [i for i in ids if i.endswith("_all")]
    sid=cand[0]
    # resolve study id from sample_lists metadata
    study_id=[s.get("studyId") for s in sl if s["sampleListId"]==sid][0]
    try:
        ids2=get(f"{API}/sample-lists/{sid}/sample-ids")
    except Exception as e:
        print(f"[WARN] {ctx}: API failed for {sid}: {e}"); ids2=[]
    print(f"{ctx}: list={sid} n={len(ids2)}")
    for s in ids2: rows.append(dict(context=ctx, sample_id=s, list_id=sid))
with open(os.path.join(OUT,"v11_mut_profiled_samples.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["context","sample_id","list_id"]); w.writeheader(); w.writerows(rows)
print("total profiled samples:", len(rows))
