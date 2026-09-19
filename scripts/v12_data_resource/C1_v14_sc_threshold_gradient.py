#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 (C1): single-cell sensitivity extension.

One pass over the three usable datasets computes, for four donor-abundance settings (no minimum, >=10, >=20,
>=50 cells per donor per cell type and arm), every comparison together with three multiplicity definitions:
  family               BH within context x module x comparison type   (primary in the manuscript)
  cell-type family     BH within context x module x cell type        (new)
  global               BH across all comparisons jointly
Run with the project single-cell environment (numpy 1.26 / h5py 3.11).
"""
import csv, math, collections
from pathlib import Path
import h5py, numpy as np
from scipy.stats import mannwhitneyu, wilcoxon
V1=Path("C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1")
V2=Path("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2")
ATLAS=Path("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas")
OUT=Path("C:/Users/fengq/Desktop/EGFR/EGFR的v14/results"); OUT.mkdir(parents=True, exist_ok=True)
PK=Path("C:/Users/fengq/Desktop/EGFR/EGFR的v14/dataset_package/06_single_cell")
MIN_DONORS, MIN_PAIRS = 3, 5
THRESHOLDS=[0,10,20,50]
MODULES=["EPH_RECEPTORS","WNT_CTNNB1","JAK_STAT","VEGF_PDGF_AXIS","HGF_MET_AXIS","SRC_FAK","ERBB_RECEPTORS","ERBB_LIGANDS"]
gs=collections.defaultdict(list)
with (ATLAS/"config/gene_sets_extended.csv").open(encoding="utf-8-sig",newline="") as f:
    for r in csv.DictReader(f): gs[r["module"]].append(r["gene"].upper())
for m in list(gs):
    if m not in MODULES: del gs[m]
def dec(v):
    if isinstance(v,(bytes,)): return v.decode("utf-8","replace")
    if isinstance(v,np.bytes_): return bytes(v).decode("utf-8","replace")
    return "" if v is None else str(v)
def col(obs,k,n):
    if k not in obs: return None
    o=obs[k]
    if isinstance(o,h5py.Dataset): return [dec(v) for v in o[()]]
    if "codes" in o and "categories" in o:
        codes=np.asarray(o["codes"][()]); cats=[dec(v) for v in o["categories"][()]]
        return [cats[int(c)] if int(c)>=0 else "" for c in codes]
    return [""]*n
def var_names(h,nv):
    for k in ("gene_symbols","gene_symbol","genes","feature_name","_index"):
        if k in h["var"]:
            v=col(h["var"],k,nv)
            if v and any(v): return [x.upper() for x in v]
    return [f"F{i}" for i in range(nv)]
def extract(h,idx,nobs):
    x=h["X"]; out=np.zeros((nobs,len(idx)),dtype=np.float32); nv=int(np.asarray(x.attrs["shape"]).reshape(-1)[1]); lib=np.full(nobs,np.nan)
    if all(k in x for k in ("data","indices","indptr")):
        ip=np.asarray(x["indptr"][()],dtype=np.int64); lib=np.diff(ip).astype(np.float64)
        from scipy import sparse
        for s in range(0,nobs,4000):
            e=min(s+4000,nobs)
            blk=np.asarray(x["data"][int(ip[s]):int(ip[e])],dtype=np.float32)
            cc=np.asarray(x["indices"][int(ip[s]):int(ip[e])],dtype=np.int64)
            out[s:e,:]=sparse.csr_matrix((blk,cc,ip[s:e+1]-ip[s]),shape=(e-s,nv))[:,idx].toarray()
    else:
        for s in range(0,nobs,2000):
            e=min(s+2000,nobs); out[s:e,:]=np.asarray(x[s:e,:],dtype=np.float32)[:,idx]
    return out, lib
SPECS={
 "CRC":  dict(path=V1/"data_raw/single_cell/CRC_cellxgene_829a3cd1.h5ad", donor="donor_id", ctype="cell_type", fields=dict(S="Sample Type", D="disease")),
 "IBD":  dict(path=V1/"data_raw/single_cell/IBD_cellxgene_9bfecd44.h5ad", donor="donor_id", ctype="cell_type", fields=dict(D="disease")),
 "STAD": dict(path=V2/"data_raw/single_cell/STAD_cellxgene_0d3807bf.h5ad", donor="donor_id", ctype="cell_type", fields=dict(C="sample_category", E="control_vs_disease")),
}
def g_crc(v):
    S=v["S"]; D=v["D"]
    return [(("non-tumour","adjacent" if D[i]=="normal" else "non-tumour") if S[i]=="Non-Tumor" else ("tumour","tumour")) for i in range(len(S))]
def g_ibd(v):
    D=v["D"]; return [("case" if D[i] in ("Crohn disease","ulcerative colitis") else "control","healthy") for i in range(len(D))]
def g_stad(v):
    S=v["C"]; E=v.get("E",["na"]*len(S)); out=[]
    for i in range(len(S)):
        if S[i]=="inutero" or E[i]=="inutero": out.append(("excluded","excluded"))
        elif S[i] in ("stomach_cancer","superficial_cancer","deep_cancer"): out.append(("tumour","tumour"))
        elif S[i]=="Neighbouring_cancer": out.append(("non-tumour","adjacent"))
        else: out.append(("control","healthy"))
    return out
GROUP={"CRC":g_crc,"IBD":g_ibd,"STAD":g_stad}
MAL=("malignant","tumor cell","tumour cell")
rows=[]
for ctx,spec in SPECS.items():
    p=spec["path"]
    if not p.exists(): print("[MISS]",ctx); continue
    with h5py.File(p,"r") as h:
        n=int(np.asarray(h["X"].attrs["shape"]).reshape(-1)[0]); obs=h["obs"]; nv=int(np.asarray(h["X"].attrs["shape"]).reshape(-1)[1])
        vals={a:col(obs,k,n) for a,k in spec["fields"].items()}
        donor=col(obs,spec["donor"],n); ctype=col(obs,spec["ctype"],n); grp=GROUP[ctx](vals)
        keep=[i for i in range(n) if grp[i][0]!="excluded"]
        donor=[donor[i] for i in keep]; ctype=[ctype[i] for i in keep]; grp=[grp[i] for i in keep]
        vn=var_names(h,nv); gidx={g:i for i,g in enumerate(vn)}
        for module,genes in gs.items():
            present=[g for g in genes if g in gidx]
            if len(present)<2: continue
            mat,lib=extract(h,[gidx[g] for g in present],n); mat=mat[keep,:]
            mx=float(np.nanmax(mat)) if mat.size else 0.0
            frac=float(np.mean(np.isclose(mat,np.round(mat)))) if mat.size else 0.0
            if frac>0.98 and mx>20:
                lib=np.maximum(lib,1.0)[keep]; mat=np.log1p(mat/lib[:,None]*10000.0)
            score=np.mean(mat,axis=1).astype(np.float64)
            per=collections.defaultdict(lambda: collections.defaultdict(list))
            for i in range(len(keep)): per[(ctype[i],grp[i][0])][donor[i]].append(score[i])
            for T in THRESHOLDS:
                dm={k:{dn:float(np.mean(v)) for dn,v in dv.items() if len(v)>=max(1,T)} for k,dv in per.items()}
                cts=sorted({c for c,_ in per})
                for ct in cts:
                    for a,b,lab in [("tumour","non-tumour","tumour-vs-adjacent"),("case","control","case-vs-healthy"),("tumour","control","tumour-vs-healthy")]:
                        A=dm.get((ct,a),{}); B=dm.get((ct,b),{})
                        if len(A)<MIN_DONORS or len(B)<MIN_DONORS: continue
                        ov=sorted(set(A)&set(B)); pv=math.nan; test="not testable"
                        if len(ov)>=MIN_PAIRS:
                            try: pv=float(wilcoxon([A[x]-B[x] for x in ov]).pvalue); test="paired"
                            except Exception: pv=math.nan
                        elif len(ov)==0:
                            try: pv=float(mannwhitneyu(list(A.values()),list(B.values()),alternative="two-sided").pvalue); test="unpaired"
                            except Exception: pv=math.nan
                        rows.append(dict(threshold=T,context=ctx,module=module,cell_type=ct,comparison_type=lab,
                                         n_donors_a=len(A),n_donors_b=len(B),n_testable=int(test!="not testable"),
                                         test_used=test,p_used=pv))
                mal=[c for c in cts if any(m in c.lower() for m in MAL) and (c,"tumour") in dm]
                epi=[c for c in cts if c not in mal and any(t in c.lower() for t in ("epithelial","colonocyte","enterocyte","secretory","mucous","foveolar","parietal","peptic")) and (c,"non-tumour") in dm]
                for mc in mal:
                    for ec in epi:
                        A=dm[(mc,"tumour")]; B=dm[(ec,"non-tumour")]
                        if len(A)<MIN_DONORS or len(B)<MIN_DONORS: continue
                        try: pv=float(mannwhitneyu(list(A.values()),list(B.values()),alternative="two-sided").pvalue)
                        except Exception: pv=math.nan
                        rows.append(dict(threshold=T,context=ctx,module=module,cell_type=f"{mc} vs {ec}",comparison_type="cell-identity",
                                         n_donors_a=len(A),n_donors_b=len(B),n_testable=int(math.isfinite(pv)),
                                         test_used="cell-identity unpaired",p_used=pv))
    print(f"[OK] {ctx}")
def bh(vals):
    idx=[i for i,p in enumerate(vals) if p is not None and math.isfinite(p)]
    out=[math.nan]*len(vals)
    if not idx: return out
    raw=np.array([vals[i] for i in idx]); order=np.argsort(raw)
    adj=np.minimum.accumulate((raw[order]*len(raw)/np.arange(1,len(raw)+1))[::-1])[::-1]
    for pos,i in enumerate(order): out[idx[i]]=float(min(adj[pos],1.0))
    return out
summary=[]
for T in THRESHOLDS:
    sub=[r for r in rows if r["threshold"]==T]
    fam=[math.nan]*len(sub)
    for key in sorted({(r["context"],r["module"],r["comparison_type"]) for r in sub}):
        idx=[i for i,r in enumerate(sub) if (r["context"],r["module"],r["comparison_type"])==key]
        for i,a in zip(idx,bh([sub[i]["p_used"] for i in idx])): fam[i]=a
    ctf=[math.nan]*len(sub)
    for key in sorted({(r["context"],r["module"],r["cell_type"]) for r in sub}):
        idx=[i for i,r in enumerate(sub) if (r["context"],r["module"],r["cell_type"])==key]
        for i,a in zip(idx,bh([sub[i]["p_used"] for i in idx])): ctf[i]=a
    gl=bh([r["p_used"] for r in sub])
    for i,r in enumerate(sub): r["fdr_family"]=fam[i]; r["fdr_celltype_family"]=ctf[i]; r["fdr_global"]=gl[i]
    ns=lambda key: sum(1 for r in sub if math.isfinite(r[key]) and r[key]<0.05)
    summary.append(dict(donor_set=("no minimum" if T==0 else f">= {T} cells per donor"),
                        comparisons=len(sub), testable=sum(r["n_testable"] for r in sub),
                        not_testable=sum(1 for r in sub if r["test_used"]=="not testable"),
                        significant_family_bh=ns("fdr_family"), significant_celltype_family_bh=ns("fdr_celltype_family"),
                        significant_global_bh=ns("fdr_global"), donors_min=MIN_DONORS, pairs_min=MIN_PAIRS))
    print(f"  threshold {T}: {len(sub)} comparisons, family BH {ns('fdr_family')}, cell-type family BH {ns('fdr_celltype_family')}, global BH {ns('fdr_global')}")
with (OUT/"v14_sc_threshold_gradient_detail.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator="\n"); w.writeheader(); w.writerows(rows)
with (PK/"single_cell_threshold_gradient.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0].keys()),lineterminator="\n"); w.writeheader(); w.writerows(summary)
# primary donor set with the cell-type-family FDR attached (for the shipped comparison table)
prim=[r for r in rows if r["threshold"]==0]
with (PK/"single_cell_comparisons_with_celltype_family_fdr.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(prim[0].keys()),lineterminator="\n"); w.writeheader(); w.writerows(prim)
print("\nsummary:")
for s in summary: print(" ",s)
