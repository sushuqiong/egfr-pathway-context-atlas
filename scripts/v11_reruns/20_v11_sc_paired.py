#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v11 single-cell reanalysis: explicit patient pairing and explicit comparison type.

Outputs (EGFR_pathway_context_atlas/results/sc_v11_patient_paired.csv):
  context, module, cell_type, comparison_type, n_pairs, n_case_patients, n_control_patients,
  paired_median_diff, case_patient_mean, control_patient_mean, p_paired, p_unpaired, test_used, fdr, top_case_celltype
Rules:
  * comparison_type = "same-cell-type"       -> the same cell_type label has patients in both groups
  * comparison_type = "cell-identity"        -> case cells are malignant/tumour-labelled and control cells are
                                                normal-tissue-labelled (different cell identities; not a
                                                same-cell-type disease effect)
  * test_used = "wilcoxon-signed-rank" when >=5 complete pairs exist, otherwise "mann-whitney (unpaired, reported as such)"
"""
import csv, math
from collections import defaultdict
from pathlib import Path
import h5py
import numpy as np
from scipy.stats import mannwhitneyu, wilcoxon

def find_v1():
    base = Path(r"C:/Users/fengq/Desktop")
    cands = list(base.rglob("EGFR_ERBB_context_project_v1"))
    for c in cands:
        if (c / "data_raw" / "single_cell").is_dir():
            return c
    return cands[0] if cands else base / "EGFR_ERBB_context_project_v1"
V1 = find_v1()
print("[v11] using V1 =", V1)
V2 = Path(r"C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2")
ATLAS = Path(r"C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas")
DATASETS = [("LUAD", V1/"data_raw/single_cell/LUAD_cellxgene_01ff5cf0.h5ad"),
            ("CRC",  V1/"data_raw/single_cell/CRC_cellxgene_829a3cd1.h5ad"),
            ("IBD",  V1/"data_raw/single_cell/IBD_cellxgene_9bfecd44.h5ad"),
            ("STAD", V2/"data_raw/single_cell/STAD_cellxgene_0d3807bf.h5ad")]
TARGET_MODULES = ["EPH_RECEPTORS","WNT_CTNNB1","JAK_STAT","VEGF_PDGF_AXIS","HGF_MET_AXIS","SRC_FAK"]
MIN_PATIENTS, MIN_PAIRS = 3, 5
MALIGNANT_HINT = ("malignant","tumor","tumour","cancer","epithelial(cancer)")
NORMAL_TISSUE_HINT = ("colonocyte","normal","adjacent","non-")

gene_sets = defaultdict(list)
with (ATLAS/"config/gene_sets_extended.csv").open(encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f): gene_sets[row["module"]].append(row["gene"].upper())
for m in list(gene_sets):
    if m not in TARGET_MODULES: del gene_sets[m]

def decode(v):
    if isinstance(v, bytes): return v.decode("utf-8","replace")
    if isinstance(v, np.bytes_): return bytes(v).decode("utf-8","replace")
    return "" if v is None else str(v)

def read_col(group, key, n):
    if key not in group: return [""]*n
    obj = group[key]
    if isinstance(obj, h5py.Dataset): return [decode(v) for v in obj[()]]
    if "codes" in obj and "categories" in obj:
        codes=np.asarray(obj["codes"][()]); cats=[decode(v) for v in obj["categories"][()]]
        return [cats[int(c)] if int(c)>=0 else "" for c in codes]
    return [""]*n

def var_names(h5, n_vars):
    var=h5["var"]
    for k in ("gene_symbols","gene_symbol","genes","feature_name","_index"):
        if k in var:
            vals=read_col(var,k,n_vars)
            if any(vals): return [v.upper() for v in vals]
    return [f"F{i}" for i in range(n_vars)]

def extract_cols(h5, indices, n_obs):
    x=h5["X"]; out=np.zeros((n_obs,len(indices)),dtype=np.float32)
    shape=np.asarray(x.attrs.get("shape",(0,0))).reshape(-1); n_vars=int(shape[1]); lib=np.full(n_obs,np.nan)
    if all(k in x for k in ("data","indices","indptr")):
        indptr=np.asarray(x["indptr"][()],dtype=np.int64); lib=np.diff(indptr).astype(np.float64)
        idx=np.asarray(indices,dtype=np.int64)
        from scipy import sparse
        for start in range(0,n_obs,4000):
            stop=min(start+4000,n_obs)
            block=np.asarray(x["data"][int(indptr[start]):int(indptr[stop])],dtype=np.float32)
            cols=np.asarray(x["indices"][int(indptr[start]):int(indptr[stop])],dtype=np.int64)
            ptr=indptr[start:stop+1]-indptr[start]
            mat=sparse.csr_matrix((block,cols,ptr),shape=(stop-start,n_vars)); out[start:stop,:]=mat[:,idx].toarray().astype(np.float32)
    else:
        idx=np.asarray(indices,dtype=np.int64)
        for start in range(0,n_obs,2000):
            stop=min(start+2000,n_obs); out[start:stop,:]=np.asarray(x[start:stop,:],dtype=np.float32)[:,idx]
    return out, lib

def is_malignant(ct): return any(h in ct.lower() for h in MALIGNANT_HINT)
def is_normalish(ct): return any(h in ct.lower() for h in NORMAL_TISSUE_HINT)

rows=[]
for context, path in DATASETS:
    if not path.exists():
        cands=list(V1.rglob(path.name))+list(V2.rglob(path.name)); path=cands[0] if cands else path
    if not path.exists(): print(f"[MISS] {context}"); continue
    csv_path=(V2 if context=="STAD" else V1)/"results/single_cell_cell_level.csv"
    meta={"patient":[],"ctype":[],"group":[]}
    with csv_path.open(encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            if r["context"]!=context: continue
            meta["patient"].append(r["patient_id"]); meta["ctype"].append(r["cell_type"]); meta["group"].append(r["group"])
    with h5py.File(path,"r") as h5:
        shape=np.asarray(h5["X"].attrs.get("shape",(0,0))).reshape(-1); n_obs,n_vars=int(shape[0]),int(shape[1])
        vn=var_names(h5,n_vars); gidx={g:i for i,g in enumerate(vn)}
        for module, genes in gene_sets.items():
            present=[g for g in genes if g in gidx]
            if len(present)<2: continue
            mat,lib=extract_cols(h5,[gidx[g] for g in present],n_obs)
            mx=float(np.nanmax(mat)) if mat.size else 0.0
            intfrac=float(np.mean(np.isclose(mat,np.round(mat)))) if mat.size else 0.0
            if intfrac>0.98 and mx>20:
                lib=np.maximum(lib,1.0); mat=np.log1p(mat/lib[:,None]*10000.0)
            score=np.mean(mat,axis=1).astype(np.float64)
            agg=defaultdict(list)
            for i in range(n_obs): agg[(meta["patient"][i],meta["ctype"][i],meta["group"][i])].append(score[i])
            pat=defaultdict(dict)
            for (pid,ct,grp),vals in agg.items(): pat[(ct,grp)][pid]=float(np.mean(vals))
            celltypes=sorted({ct for ct,g in pat})
            for ct in celltypes:
                case=pat.get((ct,"Case"),{}); ctrl=pat.get((ct,"Control"),{})
                if not case and not ctrl: continue
                # same-cell-type comparison (both arms present under the same label)
                if len(case)>=MIN_PATIENTS and len(ctrl)>=MIN_PATIENTS:
                    pairs=sorted(set(case)&set(ctrl))
                    p_pair=math.nan; p_unp=math.nan; n_pair=len(pairs)
                    if n_pair>=MIN_PAIRS:
                        d=np.array([case[p]-ctrl[p] for p in pairs])
                        try: p_pair=float(wilcoxon(d).pvalue)
                        except Exception: p_pair=math.nan
                    try: p_unp=float(mannwhitneyu(list(case.values()),list(ctrl.values()),alternative="two-sided").pvalue)
                    except Exception: p_unp=math.nan
                    if math.isfinite(p_pair): test="wilcoxon-signed-rank"; pv=p_pair; ctype="same-cell-type"
                    else: test="mann-whitney (unpaired; reported as such)"; pv=p_unp; ctype="same-cell-type"
                    rows.append(dict(context=context,module=module,cell_type=ct,comparison_type=ctype,n_pairs=n_pair,
                        n_case_patients=len(case),n_control_patients=len(ctrl),
                        paired_median_diff=float(np.median([case[p]-ctrl[p] for p in pairs])) if n_pair else math.nan,
                        case_patient_mean=float(np.mean(list(case.values()))),control_patient_mean=float(np.mean(list(ctrl.values()))),
                        p_paired=p_pair,p_unpaired=p_unp,test_used=test,p_used=pv))
            # explicit cell-identity contrast: malignant-labelled case cells vs normal-ish control epithelium
            mal_c = sorted({ct for (ct,grp) in pat if grp=="Case" and is_malignant(ct)})
            nor_c = sorted({ct for (ct,grp) in pat if grp=="Control" and (is_normalish(ct) or is_malignant(ct))})
            for mc in mal_c:
                for nc in nor_c:
                    if mc==nc: continue
                    a=pat.get((mc,"Case"),{}); b=pat.get((nc,"Control"),{})
                    if len(a)<MIN_PATIENTS or len(b)<MIN_PATIENTS: continue
                    try: pv=float(mannwhitneyu(list(a.values()),list(b.values()),alternative="two-sided").pvalue)
                    except Exception: pv=math.nan
                    rows.append(dict(context=context,module=module,cell_type=f"{mc} vs {nc}",comparison_type="cell-identity",
                        n_pairs=0,n_case_patients=len(a),n_control_patients=len(b),paired_median_diff=math.nan,
                        case_patient_mean=float(np.mean(list(a.values()))),control_patient_mean=float(np.mean(list(b.values()))),
                        p_paired=math.nan,p_unpaired=pv,test_used="mann-whitney (cell-identity contrast; unpaired)",p_used=pv))
    print(f"[OK] {context}")
keys=sorted({(r["context"],r["module"],r["comparison_type"]) for r in rows})
for ctx,mod,fam in keys:
    sub=[r for r in rows if r["context"]==ctx and r["module"]==mod and r["comparison_type"]==fam]
    # primary family test: paired signed-rank where >=MIN_PAIRS complete pairs, else unpaired MW (labelled)
    for col,pcol,outcol in [("p_used","p_used","fdr"),("p_unpaired","p_unpaired","fdr_unpaired")]:
        idx=[i for i,r in enumerate(sub) if math.isfinite(r[pcol])]
        if not idx:
            for i in idx: sub[i][outcol]=math.nan
            continue
        raw=np.array([sub[i][pcol] for i in idx]); order=np.argsort(raw)
        adj=np.minimum.accumulate((raw[order]*len(raw)/np.arange(1,len(raw)+1))[::-1])[::-1]
        for pos,i in enumerate(order): sub[idx[i]][outcol]=float(min(adj[pos],1.0))
    for r in sub:
        r.setdefault("fdr",math.nan); r.setdefault("fdr_unpaired",math.nan)
for r in rows:
    r.setdefault("comparison_type","same-cell-type")
out=ATLAS/"results/sc_v11_patient_paired.csv"
with out.open("w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["context","module","cell_type","comparison_type","n_pairs","n_case_patients",
        "n_control_patients","paired_median_diff","case_patient_mean","control_patient_mean","p_paired","p_unpaired",
        "test_used","p_used","fdr","fdr_unpaired"],extrasaction="ignore"); w.writeheader(); w.writerows(rows)
sig=[r for r in rows if math.isfinite(r["fdr"]) and r["fdr"]<0.05]
sig_u=[r for r in rows if math.isfinite(r.get("fdr_unpaired",math.nan)) and r["fdr_unpaired"]<0.05]
print("rows:",len(rows),"| primary FDR<0.05:",len(sig),"| unpaired-MW FDR<0.05 (sensitivity):",len(sig_u))
import collections
print("primary by family:",dict(collections.Counter(r["comparison_type"] for r in sig)))
print("primary by context:",dict(collections.Counter(r["context"] for r in sig)))
print("primary by test:",dict(collections.Counter(r["test_used"] for r in sig)))
print("sensitivity by context:",dict(collections.Counter(r["context"] for r in sig_u)))
paired_sig=[r for r in sig if r["test_used"].startswith("wilcoxon")]
print("significant paired tests:",len(paired_sig),"| median complete pairs:", (np.median([r["n_pairs"] for r in paired_sig]) if paired_sig else "n/a"))
