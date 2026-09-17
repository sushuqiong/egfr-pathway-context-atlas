#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12: inspect source metadata columns for all five single-cell datasets (grouping/pairing definitions)."""
import os, collections
import h5py, numpy as np
V1=r"C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1"
V2=r"C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2"
DS=[("LUAD", V1+"/data_raw/single_cell/LUAD_cellxgene_01ff5cf0.h5ad"),
    ("CRC",  V1+"/data_raw/single_cell/CRC_cellxgene_829a3cd1.h5ad"),
    ("IBD",  V1+"/data_raw/single_cell/IBD_cellxgene_9bfecd44.h5ad"),
    ("STAD", V2+"/data_raw/single_cell/STAD_cellxgene_0d3807bf.h5ad"),
    ("ASTHMA", V1+"/data_processed/single_cell/ASTHMA_GSE193816_AEC_data.h5ad")]
def dec(v):
    if isinstance(v,(bytes,)): return v.decode("utf-8","replace")
    if isinstance(v,np.bytes_): return bytes(v).decode("utf-8","replace")
    return "" if v is None else str(v)
KEY=["sample type","sample_type","tissue","disease","group","condition","donor_id","patient","patient_id",
     "primary site","site","treatment","tumor status","author cell type","cell_type","sample id","sample_id"]
for name,p in DS:
    if not os.path.exists(p): print(f"[MISS] {name} {p}"); continue
    with h5py.File(p,"r") as h:
        obs=h["obs"]; n=int(np.asarray(h["X"].attrs["shape"]).reshape(-1)[0])
        cols=list(obs.keys())
        def col(k):
            o=obs[k]
            if isinstance(o,h5py.Dataset): return [dec(v) for v in o[()]]
            if "codes" in o and "categories" in o:
                codes=np.asarray(o["codes"][()]); cats=[dec(v) for v in o["categories"][()]]
                return [cats[int(c)] if int(c)>=0 else "" for c in codes]
            return [""]*n
        print(f"\n===== {name}  cells={n}  cols={len(cols)}")
        for k in cols:
            if k.lower() in KEY or any(t in k.lower() for t in ("sample","type","disease","group","condition","donor","tissue","status")):
                c=collections.Counter(col(k))
                if 1 < len(c) <= 30:
                    print(f"   {k}: {dict(c.most_common(12))}")
                elif len(c)==1:
                    print(f"   {k}: constant = {list(c)[0]!r}")
