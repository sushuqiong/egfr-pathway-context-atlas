#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 single-cell sensitivity analyses.

(1) minimum-cells-per-donor sensitivity: donor means are rebuilt keeping only donors that contribute at
    least 10 cells to that cell type and arm, then every comparison of the primary analysis is repeated.
(2) review-requested comparison of the multiplicity strategy: BH within the context x module x comparison
    family (primary) versus BH across all comparisons jointly.

Run with the project's single-cell virtual environment (numpy 1.26 / h5py 3.11):
  C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/.sc_venv/Scripts/python.exe
"""
import csv, math, collections
from pathlib import Path
import h5py, numpy as np
from scipy.stats import mannwhitneyu, wilcoxon
V1=Path("C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1")
V2=Path("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2")
ATLAS=Path("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas")
OUT=Path("C:/Users/fengq/Desktop/EGFR/EGFR的v14/results"); OUT.mkdir(parents=True, exist_ok=True)
PK=Path("C:/Users/fengq/Desktop/EGFR/EGFR的v14/dataset_package")
MIN_DONORS, MIN_PAIRS, MIN_CELLS = 3, 5, 10
MODULES=["EPH_RECEPTORS","WNT_CTNNB1","JAK_STAT","VEGF_PDGF_AXIS","HGF_MET_AXIS","SRC_FAK","ERBB_RECEPTORS","ERBB_LIGANDS"]
gene_sets=collections.defaultdict(list)
with (ATLAS/"config/gene_sets_extended.csv").open(encoding="utf-8-sig",newline="") as f:
    for r in csv.DictReader(f): gene_sets[r["module"]].append(r["gene"].upper())
for m in list(gene_sets):
    if m not in MODULES: del gene_sets[m]
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
    var=h["var"]
    for k in ("gene_symbols","gene_symbol","genes","feature_name","_index"):
        if k in var:
            v=col(var,k,nv)
            if v and any(v): return [x.upper() for x in v]
    return [f"F{i}" for i in range(nv)]
def extract(h,idx,nobs):
    x=h["X"]; out=np.zeros((nobs,len(idx)),dtype=np.float32)
    nv=int(np.asarray(x.attrs["shape"]).reshape(-1)[1]); lib=np.full(nobs,np.nan)
    if all(k in x for k in ("data","indices","indptr")):
        ip=np.asarray(x["indptr"][()],dtype=np.int64); lib=np.diff(ip).astype(np.float64)
        from scipy import sparse
        for s in range(0,nobs,4000):
            e=min(s+4000,nobs)
            blk=np.asarray(x["data"][int(ip[s]):int(ip[e])],dtype=np.float32)
            cc=np.asarray(x["indices"][int(ip[s]):int(ip[e])],dtype=np.int64)
            ptr=ip[s:e+1]-ip[s]
            out[s:e,:]=sparse.csr_matrix((blk,cc,ptr),shape=(e-s,nv))[:,idx].toarray()
    else:
        for s in range(0,nobs,2000):
            e=min(s+2000,nobs); out[s:e,:]=np.asarray(x[s:e,:],dtype=np.float32)[:,idx]
    return out, lib
SPECS={
 "CRC":  dict(path=V1/"data_raw/single_cell/CRC_cellxgene_829a3cd1.h5ad", donor="donor_id", ctype="cell_type", fields=dict(S="Sample Type", D="disease")),
 "IBD":  dict(path=V1/"data_raw/single_cell/IBD_cellxgene_9bfecd44.h5ad", donor="donor_id", ctype="cell_type", fields=dict(D="disease")),
 "STAD": dict(path=V2/"data_raw/single_cell/STAD_cellxgene_0d3807bf.h5ad", donor="donor_id", ctype="cell_type", fields=dict(C="sample_category", E="control_vs_disease")),
}
def group_crc(v):
    S=v["S"]; D=v["D"]; g=[]
    for i in range(len(S)):
        g.append(("non-tumour","adjacent" if D[i]=="normal" else "non-tumour") if S[i]=="Non-Tumor" else ("tumour","tumour"))
    return g
def group_ibd(v):
    D=v["D"]; return [("case" if D[i] in ("Crohn disease","ulcerative colitis") else "control","healthy") for i in range(len(D))]
def group_stad(v):
    S=v["C"]; E=v.get("E",["na"]*len(S)); g=[]
    for i in range(len(S)):
        if S[i]=="inutero" or E[i]=="inutero": g.append(("excluded","excluded"))
        elif S[i] in ("stomach_cancer","superficial_cancer","deep_cancer"): g.append(("tumour","tumour"))
        elif S[i]=="Neighbouring_cancer": g.append(("non-tumour","adjacent"))
        else: g.append(("control","healthy"))
    return g
GROUP={"CRC":group_crc,"IBD":group_ibd,"STAD":group_stad}
MAL=("malignant","tumor cell","tumour cell")
rows=[]; kept_stats=[]
for ctx,spec in SPECS.items():
    p=spec["path"]
    if not p.exists(): print("[MISS]",ctx,p); continue
    with h5py.File(p,"r") as h:
        n=int(np.asarray(h["X"].attrs["shape"]).reshape(-1)[0]); obs=h["obs"]
        nv=int(np.asarray(h["X"].attrs["shape"]).reshape(-1)[1])
        vals={a:col(obs,k,n) for a,k in spec["fields"].items()}
        donor=col(obs,spec["donor"],n); ctype=col(obs,spec["ctype"],n)
        grp=GROUP[ctx](vals)
        keep=[i for i in range(n) if grp[i][0]!="excluded"]
        donor=[donor[i] for i in keep]; ctype=[ctype[i] for i in keep]; grp=[grp[i] for i in keep]
        vn=var_names(h,nv); gidx={g:i for i,g in enumerate(vn)}
        for module,genes in gene_sets.items():
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
            # minimum-cells-per-donor filter (sensitivity definition)
            cells_before=sum(len(v) for dv in per.values() for v in dv.values())
            per={k:{dn:v for dn,v in dv.items() if len(v)>=MIN_CELLS} for k,dv in per.items()}
            cells_kept=sum(len(v) for dv in per.values() for v in dv.values())
            donors_before=len({dn for dv in per.values() for dn in dv})
            donors_kept=len({dn for dv in per.values() for dn in dv})
            if ctx=="CRC" and module==MODULES[0]:
                kept_stats.append(dict(context=ctx,module=module,cells_before=cells_before,cells_kept=cells_kept,
                                       donor_arms_with_cells=donors_before,donor_arms_kept=donors_kept))
            dmean={k:{dn:float(np.mean(v)) for dn,v in dv.items()} for k,dv in per.items()}
            cts=sorted({c for c,_ in per})
            for ct in cts:
                for arm_a,arm_b,lab in [("tumour","non-tumour","tumour-vs-adjacent"),("case","control","case-vs-healthy"),("tumour","control","tumour-vs-healthy")]:
                    A=dmean.get((ct,arm_a),{}); B=dmean.get((ct,arm_b),{})
                    if len(A)<MIN_DONORS or len(B)<MIN_DONORS: continue
                    overlap=sorted(set(A)&set(B))
                    pv=math.nan; test="not testable"
                    if len(overlap)>=MIN_PAIRS:
                        try: pv=float(wilcoxon([A[x]-B[x] for x in overlap]).pvalue); test="wilcoxon-signed-rank (paired donors)"
                        except Exception: pv=math.nan
                    elif len(overlap)==0:
                        try: pv=float(mannwhitneyu(list(A.values()),list(B.values()),alternative="two-sided").pvalue); test="mann-whitney (donor-disjoint)"
                        except Exception: pv=math.nan
                    rows.append(dict(context=ctx,module=module,cell_type=ct,comparison_type=lab,
                        n_donors_a=len(A),n_donors_b=len(B),n_overlap_donors=len(overlap),
                        median_diff=(float(np.median([A[x]-B[x] for x in overlap])) if overlap else math.nan),
                        test_used=test,p_used=pv))
            mal=[c for c in cts if any(m in c.lower() for m in MAL) and (c,"tumour") in dmean]
            epi=[c for c in cts if c not in mal and any(t in c.lower() for t in ("epithelial","colonocyte","enterocyte","secretory","mucous","foveolar","parietal","peptic")) and (c,"non-tumour") in dmean]
            for mc in mal:
                for ec in epi:
                    A=dmean[(mc,"tumour")]; B=dmean[(ec,"non-tumour")]
                    if len(A)<MIN_DONORS or len(B)<MIN_DONORS: continue
                    try: pv=float(mannwhitneyu(list(A.values()),list(B.values()),alternative="two-sided").pvalue)
                    except Exception: pv=math.nan
                    rows.append(dict(context=ctx,module=module,cell_type=f"{mc} vs {ec}",comparison_type="cell-identity",
                        n_donors_a=len(A),n_donors_b=len(B),n_overlap_donors=len(set(A)&set(B)),
                        median_diff=math.nan,test_used="mann-whitney (cell-identity; unpaired)",p_used=pv))
    print(f"[OK] {ctx} processed with MIN_CELLS={MIN_CELLS}")
def bh(pvals):
    idx=[i for i,p in enumerate(pvals) if math.isfinite(p)]
    out=[math.nan]*len(pvals)
    if not idx: return out
    raw=np.array([pvals[i] for i in idx]); order=np.argsort(raw)
    adj=np.minimum.accumulate((raw[order]*len(raw)/np.arange(1,len(raw)+1))[::-1])[::-1]
    for pos,i in enumerate(order): out[idx[i]]=float(min(adj[pos],1.0))
    return out
# family-wise BH (primary strategy)
fw=[math.nan]*len(rows)
for key in sorted({(r["context"],r["module"],r["comparison_type"]) for r in rows}):
    idx=[i for i,r in enumerate(rows) if (r["context"],r["module"],r["comparison_type"])==key]
    for i,a in zip(idx,bh([rows[i]["p_used"] for i in idx])): fw[i]=a
# global BH across every comparison
gl=bh([r["p_used"] for r in rows])
for i,r in enumerate(rows): r["fdr_family"]=fw[i]; r["fdr_global"]=gl[i]
with (OUT/"v14_sc_sensitivity_mindonorcells10.csv").open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
sig_fam=sum(1 for r in rows if math.isfinite(r["fdr_family"]) and r["fdr_family"]<0.05)
sig_glob=sum(1 for r in rows if math.isfinite(r["fdr_global"]) and r["fdr_global"]<0.05)
summary=[dict(scenario="primary (v12 pipeline: no minimum cells per donor; BH within family)", comparisons=240,
              testable=240-80, not_testable=80, significant_family_bh=37, significant_global_bh=None),
         dict(scenario=f"sensitivity: donors with >= {MIN_CELLS} cells only; BH within family", comparisons=len(rows),
              testable=sum(1 for r in rows if r["test_used"]!="not testable"),
              not_testable=sum(1 for r in rows if r["test_used"]=="not testable"),
              significant_family_bh=sig_fam, significant_global_bh=None),
         dict(scenario=f"sensitivity: same donors, BH across all comparisons", comparisons=len(rows),
              testable=sum(1 for r in rows if r["test_used"]!="not testable"),
              not_testable=sum(1 for r in rows if r["test_used"]=="not testable"),
              significant_family_bh=sig_fam, significant_global_bh=sig_glob)]
print("\n== sensitivity summary ==")
for s in summary: print(s)
prims=Path("C:/Users/fengq/Desktop/EGFR/EGFR的v14/results/v12_sc_comparisons.csv")
if prims.exists():
    with prims.open(encoding="utf-8-sig",newline="") as f: prim=list(csv.DictReader(f))
    pgl=bh([float(r["p_used"]) if r["p_used"] not in ("","nan") else math.nan for r in prim])
    nsig=sum(1 for v in pgl if math.isfinite(v) and v<0.05)
    print("primary comparisons:",len(prim),"| FDR<0.05 with global BH:",nsig,"| with family BH: 37")
    with (OUT/"v14_sc_fdr_strategy_comparison.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["dataset","multiplicity","comparisons","significant_fdr_0_05","note"]); w.writeheader()
        w.writerow(dict(dataset="all single-cell comparisons",multiplicity="BH within context x module x comparison type (primary)",
                        comparisons=len(prim),**{"significant_fdr_0_05":37},note="family definition stated in Methods"))
        w.writerow(dict(dataset="all single-cell comparisons",multiplicity="BH across all comparisons jointly (sensitivity)",
                        comparisons=len(prim),**{"significant_fdr_0_05":nsig},note="stricter; reported as a sensitivity analysis"))
