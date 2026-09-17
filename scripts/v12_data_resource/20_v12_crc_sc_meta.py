#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12: inspect CRC single-cell source metadata to rebuild case/control grouping and pairing."""
import csv, os, collections
import h5py, numpy as np
V1 = r"C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1"
H5 = os.path.join(V1, "data_raw/single_cell/CRC_cellxgene_829a3cd1.h5ad")
OUT= r"C:\Users\fengq\Desktop\EGFR\EGFR的v12\results"; os.makedirs(OUT, exist_ok=True)
def decode(v):
    if isinstance(v,(bytes,)): return v.decode("utf-8","replace")
    if isinstance(v,np.bytes_): return bytes(v).decode("utf-8","replace")
    return "" if v is None else str(v)
with h5py.File(H5,"r") as h:
    obs=h["obs"]
    keys=list(obs.keys())
    print("obs columns:", keys)
    n=int(np.asarray(h["X"].attrs["shape"]).reshape(-1)[0])
    def col(k):
        o=obs[k]
        if isinstance(o,h5py.Dataset): return [decode(v) for v in o[()]]
        if "codes" in o and "categories" in o:
            codes=np.asarray(o["codes"][()]); cats=[decode(v) for v in o["categories"][()]]
            return [cats[int(c)] if int(c)>=0 else "" for c in codes]
        return [""]*n
    print("n_obs:", n)
    interesting=[k for k in keys if any(t in k.lower() for t in ("sample","tissue","disease","group","type","donor","patient","stage","library","condition","cell_type","annotation"))]
    for k in interesting:
        vals=col(k); c=collections.Counter(vals)
        show=dict(list(c.most_common(8)))
        print(f"  {k}: n_unique={len(c)} top={show}")
    # cross-tab: candidate grouping vs candidate cell type & dataset
    for gk in [k for k in keys if k.lower() in ("sample_type","tissue","tissue_type","disease","group","condition","donor_disease_status")]:
        for ck in [k for k in keys if "cell_type" in k.lower() or "celltype" in k.lower()]:
            g=col(gk); c=col(ck)
            tab=collections.Counter((a,b) for a,b in zip(g,c))
            mal={k:v for k,v in tab.items() if "malignant" in k[1].lower()}
            if mal: print(f"  crosstab {gk} x {ck}: malignant cells by group -> {mal}")
    # per-sample composition to spot normal/tumour pairs
    for sk in [k for k in keys if "sample" in k.lower() and "id" in k.lower()]:
        s=col(sk); d=[k for k in keys if k.lower() in ("sample_type","tissue","tissue_type","disease")]
        if not d: continue
        dd=col(d[0]); per=collections.defaultdict(collections.Counter)
        for a,b in zip(s,dd): per[a][b]+=1
        print(f"  samples x {d[0]}: {len(per)} samples;", dict(list(per.items())[:5]))
