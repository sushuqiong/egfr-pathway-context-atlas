#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13: resolve and verify CELLxGENE identifiers live (collection -> datasets -> version ids),
matching the local file handles (first 8 characters of the download UUID)."""
import json, os, csv, urllib.request, ssl
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; PK=os.path.join(V13,"dataset_package")
COLLECTIONS={"CRC":"1cbfb478-2c7f-4d15-b522-9f74e9fe52a8","IBD":"7c7bd6c2-925b-4034-baab-620ef1b760e1",
             "LUAD":"0bebef1a-4607-4584-9070-dacf89a0d635","STAD":"f11cb29c-b546-4738-9bd8-66ea621a7bd5"}
HANDLES={"CRC":"829a3cd1","IBD":"9bfecd44","LUAD":"01ff5cf0","STAD":"0d3807bf"}
ctx=ssl.create_default_context()
def api(url):
    req=urllib.request.Request(url, headers={"User-Agent":"resource-verification/1.0"})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r: return json.loads(r.read().decode())
rows=[]
for cname,cid in COLLECTIONS.items():
    try:
        coll=api(f"https://api.cellxgene.cziscience.com/curation/v1/collections/{cid}")
    except Exception as e:
        rows.append(dict(context=cname, collection_id=cid, status=f"collection fetch failed: {type(e).__name__}")); continue
    ds=coll.get("datasets",[]) or []
    handle=HANDLES[cname]; m=None
    for d in ds:
        if str(d.get("dataset_version_id","")).startswith(handle) or str(d.get("dataset_id","")).startswith(handle):
            m=d; break
    if m is None and ds:
        m=ds[0]  # fall back to the collection's dataset; note the version difference
    if m is None:
        rows.append(dict(context=cname, collection_id=cid, collection_name=coll.get("name",""), status="no dataset in collection")); continue
    lic=m.get("license")
    if isinstance(lic,dict): lic=lic.get("name") or lic.get("license") or str(lic)[:60]
    rows.append(dict(context=cname, collection_id=cid, collection_name=coll.get("name","")[:80],
        collection_doi=(coll.get("doi") or ""), dataset_id=m.get("dataset_id",""),
        dataset_version_id=m.get("dataset_version_id",""),
        version_prefix_matches_local_file=str(m.get("dataset_version_id","")).startswith(handle),
        dataset_title=(m.get("title") or "")[:80], cell_count=m.get("cell_count",""),
        licence=lic or "", status="verified live"))
    print(f"[LIVE] {cname}: collection '{coll.get('name','')[:46]}' | dataset_version_id={m.get('dataset_version_id','')[:38]} | prefix_match={str(m.get('dataset_version_id','')).startswith(handle)} | cells={m.get('cell_count','')}")
with open(os.path.join(PK,"01_cohort_registry","cellxgene_sources.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
ok=sum(1 for r in rows if r.get("status")=="verified live")
print("\nverified live:",ok,"of",len(rows))
print("prefix matches with local file names:",sum(1 for r in rows if r.get("version_prefix_matches_local_file") is True))
