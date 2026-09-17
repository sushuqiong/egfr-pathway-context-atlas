#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12 single-cell re-analysis with explicit, source-derived grouping and donor-aware design.

Grouping (documented, from source obs; raw labels retained):
  CRC   : tumour = Sample Type in {Primary, Metastasis};  non-tumour = Non-Tumor
  IBD   : case   = disease in {Crohn disease, ulcerative colitis}; control = normal (healthy donors)
  STAD  : tumour = sample_category in {stomach_cancer, superficial_cancer, deep_cancer};
          adjacent = Neighbouring_cancer; healthy = Non_pathological (organ donor); inutero excluded
  ASTHMA: case   = group 'AA' (allergic asthma); control = 'AC'
  LUAD  : tumour = Sample Type / disease tumour labels; non-tumour = normal (source fields)
Comparisons:
  same-cell-type comparisons are tumour-vs-adjacent, tumour-vs-healthy or case-vs-healthy,
  paired signed-rank when >=5 donors contribute both arms, unpaired only when the arms are
  donor-disjoint, otherwise reported as not testable (independence respected).
  cell-identity contrasts (malignant vs normal epithelium) are labelled separately.
"""
import csv, math, os, collections
from pathlib import Path
import h5py, numpy as np
from scipy.stats import mannwhitneyu, wilcoxon
V1=Path("C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1")
V2=Path("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2")
ATLAS=Path("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas")
OUT=Path("C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"); OUT.mkdir(parents=True, exist_ok=True)
MODULES=["EPH_RECEPTORS","WNT_CTNNB1","JAK_STAT","VEGF_PDGF_AXIS","HGF_MET_AXIS","SRC_FAK","ERBB_RECEPTORS","ERBB_LIGANDS"]
MIN_DONORS, MIN_PAIRS = 3, 5
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

def group_crc(v):
    S=v["S"]; D=v["D"]; g=[]
    for i in range(len(S)):
        if S[i]=="Non-Tumor": g.append(("non-tumour","adjacent" if D[i]=="normal" else "non-tumour"))
        else: g.append(("tumour","tumour"))
    return g
def group_ibd(v):
    D=v["D"]; return [("case" if D[i] in ("Crohn disease","ulcerative colitis") else "control","healthy") for i in range(len(D))]
def group_stad(v):
    S=v["C"]; E=v.get("E", ["na"]*len(S)); g=[]
    for i in range(len(S)):
        if S[i]=="inutero" or E[i]=="inutero": g.append(("excluded","excluded"))
        elif S[i] in ("stomach_cancer","superficial_cancer","deep_cancer"): g.append(("tumour","tumour"))
        elif S[i]=="Neighbouring_cancer": g.append(("non-tumour","adjacent"))
        else: g.append(("control","healthy"))
    return g
def group_asthma(v):
    G=v["G"]; return [("case" if G[i]=="AA" else "control","case-vs-control") for i in range(len(G))]
def group_luad(v):
    # source dataset is tumour-only (disease = lung adenocarcinoma for all cells; tissue = lung parenchyma);
    # length is taken from the disease column so the grouping vector matches the cell count
    D=v["D"]; return [("tumour","tumour") for _ in range(len(D))]
SPECS={
 # LUAD: source dataset contains tumour cells only (disease = lung adenocarcinoma for all 117,266 cells;
 # tissue = lung parenchyma; no normal/adjacent field) -> no case-control contrast; excluded and documented.
 "CRC":  dict(path=V1/"data_raw/single_cell/CRC_cellxgene_829a3cd1.h5ad", donor="donor_id", ctype="cell_type",
              fields=dict(S="Sample Type", D="disease"), fn=group_crc),
 "IBD":  dict(path=V1/"data_raw/single_cell/IBD_cellxgene_9bfecd44.h5ad", donor="donor_id", ctype="cell_type",
              fields=dict(D="disease"), fn=group_ibd),
 "STAD": dict(path=V2/"data_raw/single_cell/STAD_cellxgene_0d3807bf.h5ad", donor="donor_id", ctype="cell_type",
              fields=dict(C="sample_category", E="control_vs_disease"), fn=group_stad),
 "ASTHMA": dict(path=V1/"data_processed/single_cell/ASTHMA_GSE193816_AEC_data.h5ad", donor=None, donor_from_index=True,
              ctype=None, fields=dict(G="group"), fn=group_asthma),
 "LUAD": dict(path=V1/"data_raw/single_cell/LUAD_cellxgene_01ff5cf0.h5ad", donor="donor_id", ctype="cell_type",
              fields=dict(D="disease"),
              fn=lambda v: [("excluded","excluded") for _ in range(len(v["D"]))]),
}
MAL=("malignant","tumor cell","tumour cell")
rows=[]; audit=[]; loc_rows=[]
for ctx,spec in SPECS.items():
    p=spec["path"]
    if not p.exists(): print("[MISS]",ctx,p); continue
    with h5py.File(p,"r") as h:
        n=int(np.asarray(h["X"].attrs["shape"]).reshape(-1)[0])
        obs=h["obs"]; nv=int(np.asarray(h["X"].attrs["shape"]).reshape(-1)[1])
        vals={}
        for alias,key in spec["fields"].items(): vals[alias]=col(obs,key,n)
        if spec["donor"]: donor=col(obs,spec["donor"],n)
        elif spec.get("donor_from_index"): donor=[x.split("_")[0] for x in col(obs,"_index",n)]
        else: donor=list(range(n))
        ctype=col(obs,spec["ctype"],n) if spec["ctype"] else col(obs,"cell_type",n) or ["epithelial cell"]*n
        grp=spec["fn"](vals)
        keep=[i for i in range(n) if grp[i][0] != "excluded"]
        donor=[donor[i] for i in keep]; ctype=[ctype[i] for i in keep]; grp=[grp[i] for i in keep]
        # audit
        audit.append(dict(context=ctx, cells_total=n, cells_used=len(keep),
            donors=len(set(donor)), cell_types=len(set(ctype)),
            arms=";".join(sorted({f"{a}" for a,_ in grp})),
            control_kinds=";".join(sorted({k for _,k in grp}))))
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
            dmean={k:{dn:float(np.mean(v)) for dn,v in dv.items()} for k,dv in per.items()}
            cts=sorted({c for c,_ in per})
            for ct in cts:
                for arm_a,arm_b,ctype_lab in [("tumour","non-tumour","tumour-vs-adjacent"),
                                              ("case","control","case-vs-healthy"),
                                              ("tumour","control","tumour-vs-healthy")]:
                    A=dmean.get((ct,arm_a),{}); B=dmean.get((ct,arm_b),{})
                    if len(A)<MIN_DONORS or len(B)<MIN_DONORS: continue
                    overlap=sorted(set(A)&set(B)); disj = len(overlap)==0
                    p_pair=math.nan; p_unp=math.nan; test="not testable"; pv=math.nan
                    if len(overlap)>=MIN_PAIRS:
                        d=np.array([A[x]-B[x] for x in overlap])
                        try: p_pair=float(wilcoxon(d).pvalue)
                        except Exception: p_pair=math.nan
                        test="wilcoxon-signed-rank (paired donors)"; pv=p_pair
                    elif disj:
                        try: p_unp=float(mannwhitneyu(list(A.values()),list(B.values()),alternative="two-sided").pvalue)
                        except Exception: p_unp=math.nan
                        test="mann-whitney (donor-disjoint)"; pv=p_unp
                    rows.append(dict(context=ctx,module=module,cell_type=ct,comparison_type=ctype_lab,
                        n_donors_a=len(A),n_donors_b=len(B),n_overlap_donors=len(overlap),n_pairs=len(overlap),
                        median_diff=(float(np.median([A[x]-B[x] for x in overlap])) if overlap else math.nan),
                        mean_a=float(np.mean(list(A.values()))),mean_b=float(np.mean(list(B.values()))),
                        p_paired=p_pair,p_unpaired=p_unp,test_used=test,p_used=pv))
            # localization: mean module score per cell type (all cells, for cell-source annotation)
            ctm=collections.defaultdict(list)
            for i in range(len(keep)): ctm[ctype[i]].append(float(score[i]))
            for ct,mv in ctm.items():
                if len(mv) < 20: continue
                loc_rows.append(dict(context=ctx, module=module, cell_type=ct, n_cells=len(mv), mean_score=float(np.mean(mv))))
            # cell-identity contrasts: malignant (tumour) vs normal epithelium (non-tumour)
            mal=[c for c in cts if any(m in c.lower() for m in MAL) and (c,"tumour") in dmean]
            epi=[c for c in cts if c not in mal and any(t in c.lower() for t in ("epithelial","colonocyte","enterocyte","secretory","mucous","foveolar","parietal","peptic")) and (c,"non-tumour") in dmean]
            for mc in mal:
                for ec in epi:
                    A=dmean[(mc,"tumour")]; B=dmean[(ec,"non-tumour")]
                    if len(A)<MIN_DONORS or len(B)<MIN_DONORS: continue
                    try: pv=float(mannwhitneyu(list(A.values()),list(B.values()),alternative="two-sided").pvalue)
                    except Exception: pv=math.nan
                    rows.append(dict(context=ctx,module=module,cell_type=f"{mc} vs {ec}",comparison_type="cell-identity",
                        n_donors_a=len(A),n_donors_b=len(B),n_overlap_donors=len(set(A)&set(B)),n_pairs=0,
                        median_diff=math.nan,mean_a=float(np.mean(list(A.values()))),mean_b=float(np.mean(list(B.values()))),
                        p_paired=math.nan,p_unpaired=pv,test_used="mann-whitney (cell-identity; unpaired)",p_used=pv))
    print(f"[OK] {ctx}: cells={n} used={len(keep)} donors={len(set(donor))}")
# BH within context x module x comparison_type family
keys=sorted({(r["context"],r["module"],r["comparison_type"]) for r in rows})
for k in keys:
    sub=[r for r in rows if (r["context"],r["module"],r["comparison_type"])==k]
    idx=[i for i,r in enumerate(sub) if math.isfinite(r["p_used"])]
    for i,r in enumerate(sub): r["fdr"]=math.nan
    if not idx: continue
    raw=np.array([sub[i]["p_used"] for i in idx]); order=np.argsort(raw)
    adj=np.minimum.accumulate((raw[order]*len(raw)/np.arange(1,len(raw)+1))[::-1])[::-1]
    for pos,i in enumerate(order): sub[idx[i]]["fdr"]=float(min(adj[pos],1.0))
with (OUT/"v12_sc_comparisons.csv").open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with (OUT/"v12_sc_localization.csv").open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(loc_rows[0].keys())); w.writeheader(); w.writerows(loc_rows)
with (OUT/"v12_sc_dataset_audit.csv").open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(audit[0].keys())); w.writeheader(); w.writerows(audit)
sig=[r for r in rows if math.isfinite(r["fdr"]) and r["fdr"]<0.05]
print("\ncomparisons:",len(rows),"| FDR<0.05:",len(sig))
print(" by context:",dict(collections.Counter(r['context'] for r in sig)))
print(" by comparison_type:",dict(collections.Counter(r['comparison_type'] for r in sig)))
print(" by test used:",dict(collections.Counter(r['test_used'] for r in sig)))
nt=[r for r in rows if r['test_used']=='not testable']
print(" not testable (donor overlap <5, not disjoint):",len(nt))
