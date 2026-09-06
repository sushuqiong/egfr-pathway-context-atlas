#!/usr/bin/env python3
"""Single-cell cross-validation: locate top atlas module hits (EPH, WNT, JAK-STAT, VEGF/PDGF, HGF/MET)
to cell-type sources across the five single-cell datasets (LUAD/CRC/IBD/asthma from v1, STAD from v2).
Reuses the v1/v2 patient-aware grouping (cell rows align 1:1 with saved cell_level CSV order)."""
import csv, math, sys
from collections import defaultdict
from pathlib import Path
import h5py
import numpy as np

V1 = Path(r"C:/Users/fengq/Desktop/EGFR胃癌/EGFR_ERBB_context_project_v1")
V2 = Path(r"C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2")
ATLAS = Path(r"C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas")
DATASETS = [
    ("LUAD", V1 / "data_raw/single_cell/LUAD_cellxgene_01ff5cf0.h5ad"),
    ("CRC", V1 / "data_raw/single_cell/CRC_cellxgene_829a3cd1.h5ad"),
    ("IBD", V1 / "data_raw/single_cell/IBD_cellxgene_9bfecd44.h5ad"),
    ("ASTHMA", V1 / "data_processed/single_cell/ASTHMA_GSE193816_AEC_data.h5ad"),
    ("STAD", V2 / "data_raw/single_cell/STAD_cellxgene_0d3807bf.h5ad"),
]
TARGET_MODULES = ["EPH_RECEPTORS", "WNT_CTNNB1", "JAK_STAT", "VEGF_PDGF_AXIS", "HGF_MET_AXIS"]
MIN_PATIENTS = 3

# load extended gene set
gene_sets = defaultdict(list)
with (ATLAS / "config/gene_sets_extended.csv").open(encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        gene_sets[row["module"]].append(row["gene"].upper())
for m in list(gene_sets):
    if m not in TARGET_MODULES:
        del gene_sets[m]

def decode(v):
    if isinstance(v, bytes): return v.decode("utf-8", errors="replace")
    if isinstance(v, np.bytes_): return bytes(v).decode("utf-8", errors="replace")
    return "" if v is None else str(v)

def read_col(group, key, n):
    if key not in group: return [""] * n
    obj = group[key]
    if isinstance(obj, h5py.Dataset):
        return [decode(v) for v in obj[()]]
    if "codes" in obj and "categories" in obj:
        codes = np.asarray(obj["codes"][()]); cats = [decode(v) for v in obj["categories"][()]]
        return [cats[int(c)] if int(c) >= 0 else "" for c in codes]
    return [""] * n

def choose(obs, cands):
    for c in cands:
        if c in obs: return c
    return None

def var_names(h5, n_vars):
    var = h5["var"]
    for k in ("gene_symbols", "gene_symbol", "genes", "feature_name", "_index"):
        if k in var:
            vals = read_col(var, k, n_vars)
            if any(vals): return [v.upper() for v in vals]
    return [f"F{i}" for i in range(n_vars)]

def extract_cols(h5, indices, n_obs):
    x = h5["X"]
    out = np.zeros((n_obs, len(indices)), dtype=np.float32)
    shape = np.asarray(x.attrs.get("shape", (0, 0))).reshape(-1)
    n_vars = int(shape[1])
    indptr = None
    if all(k in x for k in ("data", "indices", "indptr")):
        indptr = np.asarray(x["indptr"][()], dtype=np.int64)
        lib = np.diff(indptr).astype(np.float64)
        idx = np.asarray(indices, dtype=np.int64)
        for start in range(0, n_obs, 4000):
            stop = min(start + 4000, n_obs)
            block = np.asarray(x["data"][int(indptr[start]):int(indptr[stop])], dtype=np.float32)
            cols = np.asarray(x["indices"][int(indptr[start]):int(indptr[stop])], dtype=np.int64)
            ptr = indptr[start:stop + 1] - indptr[start]
            from scipy import sparse
            mat = sparse.csr_matrix((block, cols, ptr), shape=(stop - start, n_vars))
            out[start:stop, :] = mat[:, idx].toarray().astype(np.float32)
    else:
        lib = np.full(n_obs, np.nan)
        idx = np.asarray(indices, dtype=np.int64)
        for start in range(0, n_obs, 2000):
            stop = min(start + 2000, n_obs)
            out[start:stop, :] = np.asarray(x[start:stop, :], dtype=np.float32)[:, idx]
    return out, lib

def find_file(p):
    return p if p.exists() else None

rows_out = []
for context, path in DATASETS:
    if not path.exists():
        # fallback scan
        cands = list(V1.rglob(path.name)) + list(V2.rglob(path.name))
        path = cands[0] if cands else path
    if not path.exists():
        print(f"[MISS] {context}: {path}"); continue
    # meta from saved cell-level csv (same order as h5ad obs)
    csv_path = (V2 if context == "STAD" else V1) / "results/single_cell_cell_level.csv"
    meta = {"patient": [], "ctype": [], "group": [], "disease": []}
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["context"] != context: continue
            meta["patient"].append(row["patient_id"]); meta["ctype"].append(row["cell_type"])
            meta["group"].append(row["group"]); meta["disease"].append(row["disease"])
    n = len(meta["patient"])
    with h5py.File(path, "r") as h5:
        shape = np.asarray(h5["X"].attrs.get("shape", (0, 0))).reshape(-1)
        n_obs, n_vars = int(shape[0]), int(shape[1])
        if n != n_obs:
            print(f"[WARN] {context} meta {n} != obs {n_obs}")
        vn = var_names(h5, n_vars)
        gidx = {g: i for i, g in enumerate(vn)}
        for module, genes in gene_sets.items():
            present = [g for g in genes if g in gidx]
            if len(present) < 2: continue
            mat, lib = extract_cols(h5, [gidx[g] for g in present], n_obs)
            maxv = float(np.nanmax(mat)) if mat.size else 0.0
            intfrac = float(np.mean(np.isclose(mat, np.round(mat)))) if mat.size else 0.0
            raw_like = intfrac > 0.98 and maxv > 20
            if raw_like:
                lib = np.maximum(lib, 1.0)
                mat = np.log1p(mat / lib[:, None] * 10000.0)
            score = np.mean(mat, axis=1).astype(np.float64)
            # per patient x celltype x group means
            agg = defaultdict(list)
            for i in range(n_obs):
                agg[(meta["patient"][i], meta["ctype"][i], meta["group"][i])].append(score[i])
            pat_sum = defaultdict(list)
            for (pid, ct, grp), vals in agg.items():
                pat_sum[(pid, ct, grp)].append(float(np.mean(vals)))
            # cell-type expression in case cells (localization), then MWU Case vs Control per celltype
            celltype_case_mean = defaultdict(list); celltype_means = defaultdict(list)
            for i in range(n_obs):
                celltype_means[meta["ctype"][i]].append(float(score[i]))
                if meta["group"][i] == "Case": celltype_case_mean[meta["ctype"][i]].append(float(score[i]))
            top_ct = max(celltype_case_mean, key=lambda c: np.mean(celltype_case_mean[c])) if celltype_case_mean else ""
            per_ct_patient = defaultdict(lambda: defaultdict(list))
            for (pid, ct, grp), meanv in pat_sum.items():
                per_ct_patient[ct][grp].append(meanv)
            for ct in sorted(per_ct_patient):
                x = np.array(per_ct_patient[ct]["Case"]); y = np.array(per_ct_patient[ct]["Control"])
                pv = math.nan
                if len(x) >= MIN_PATIENTS and len(y) >= MIN_PATIENTS:
                    from scipy.stats import mannwhitneyu
                    pv = float(mannwhitneyu(x, y, alternative="two-sided").pvalue)
                rows_out.append({
                    "context": context, "module": module, "cell_type": ct,
                    "n_case_patients": len(x), "n_control_patients": len(y),
                    "case_patient_mean": float(np.mean(x)) if len(x) else math.nan,
                    "control_patient_mean": float(np.mean(y)) if len(y) else math.nan,
                    "p_mannwhitney": pv,
                    "all_cells_ct_mean": float(np.mean(celltype_means[ct])),
                    "top_case_celltype": top_ct,
                })
    print(f"[OK] {context}: {n_obs} cells, target modules scored")

# BH within context x module across cell types
if rows_out:
    keys = sorted({(r["context"], r["module"]) for r in rows_out})
    for (ctx, mod) in keys:
        sub = [r for r in rows_out if r["context"] == ctx and r["module"] == mod]
        ps = [r["p_mannwhitney"] for r in sub]
        ps_sorted = sorted([p for p in ps if math.isfinite(p)])
        m = len(ps_sorted)
        if m:
            order = np.argsort([r["p_mannwhitney"] if math.isfinite(r["p_mannwhitney"]) else np.inf for r in sub])
            idx_fin = [i for i in order if math.isfinite(sub[i]["p_mannwhitney"])]
            raw = np.array([sub[i]["p_mannwhitney"] for i in idx_fin])
            adj = np.minimum.accumulate((raw * m / np.arange(1, m + 1))[::-1])[::-1]
            for j, q in zip(idx_fin, adj):
                sub[j]["fdr"] = float(min(q, 1.0))
        for r in sub:
            if "fdr" not in r: r["fdr"] = math.nan

fields = ["context","module","cell_type","n_case_patients","n_control_patients","case_patient_mean",
          "control_patient_mean","p_mannwhitney","fdr","all_cells_ct_mean","top_case_celltype"]
out_dir = ATLAS / "results"
out_dir.mkdir(parents=True, exist_ok=True)
with (out_dir / "sc_top_hit_cell_source_validation.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows_out)
print("rows:", len(rows_out))
sig = [r for r in rows_out if math.isfinite(r.get("fdr", math.nan)) and r["fdr"] < 0.05]
print("FDR<0.05 comparisons:", len(sig))
for r in sig[:18]:
    print(f"  {r['context']:7} {r['module']:14} {r['cell_type'][:34]:34} nC={r['n_case_patients']} nN={r['n_control_patients']} case={float(r['case_patient_mean']):.3f} ctrl={float(r['control_patient_mean']):.3f} FDR={float(r['fdr']):.3f}")
