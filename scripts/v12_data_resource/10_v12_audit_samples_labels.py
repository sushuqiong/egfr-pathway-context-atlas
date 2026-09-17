#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12 audit: (1) ESCC histology scope, (2) CRC single-cell malignant-cell labels + patient overlap,
(3) sample registry counts (patients / tissue samples / assay records)."""
import csv, json, os, collections
RAW=r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\data_raw\cbio_v3"
A  =r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\results"
V  =r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\reruns\results"
OUT=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12\results"; os.makedirs(OUT,exist_ok=True)

print("=== (1) ESCC / TCGA-ESCA histology audit ===")
clin=json.load(open(os.path.join(RAW,"ESCC_clinical_sample_raw.json")))
keys=collections.Counter()
for r in clin: keys[r.get("clinicalAttributeId")]+=1
print("  clinical sample attributes:", dict(keys))
for attr in ("DISEASE_TYPE","PRIMARY_DIAGNOSIS","HISTOLOGY","TUMOR_TYPE","SAMPLE_TYPE","CANCER_TYPE"):
    vals=[(r.get("sampleId"), r.get("value")) for r in clin if r.get("clinicalAttributeId")==attr]
    if vals:
        c=collections.Counter(v for _,v in vals)
        print(f"  {attr}: n={len(vals)} -> {dict(c)}")
# expression/mutation sample lists for ESCC context
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
prof=rd(os.path.join(V,"v11_mut_profiled_samples.csv"))
print("  mutation-profiled ESCC samples:", sum(1 for r in prof if r["context"]=="ESCC"))
expr=rd(os.path.join(A,"cbio_v3_expression_gene_sample.csv"))
print("  expression samples (EGFR rows):", len({r["sample_id"] for r in expr if r["context"]=="ESCC"}))

print("\n=== (2) CRC single-cell labels and pairing/independence ===")
sc_cells=None
for cand in [r"C:\Users\fengq\Desktop\EGFR\EGFR胃癌\EGFR_ERBB_context_project_v1\results\single_cell_cell_level.csv",
             r"C:\Users\fengq\Desktop\EGFR\EGFR_ERBB_context_project_v1\results\single_cell_cell_level.csv"]:
    if os.path.exists(cand): sc_cells=cand; break
if not sc_cells:
    import glob
    g=glob.glob(r"C:\Users\fengq\Desktop\EGFR\**\single_cell_cell_level.csv", recursive=True)
    sc_cells=g[0] if g else None
print("  cell_level file:", sc_cells)
if sc_cells:
    rows=[r for r in rd(os.path.abspath(sc_cells)) if r.get("context")=="CRC"]
    print("  CRC cells:", len(rows))
    bygrp=collections.Counter((r["group"], r["cell_type"]) for r in rows)
    print("  Control-side cell types containing 'malignant':",
          {k[1]:v for k,v in bygrp.items() if k[0]=="Control" and "malignant" in k[1].lower()})
    print("  Case-side 'malignant cell' patients:", len({r["patient_id"] for r in rows if r["group"]=="Case" and "malignant" in r["cell_type"].lower()}))
    print("  Control-side 'malignant cell' patients:", len({r["patient_id"] for r in rows if r["group"]=="Control" and "malignant" in r["cell_type"].lower()}))
    ctrl_mal={r["patient_id"] for r in rows if r["group"]=="Control" and "malignant" in r["cell_type"].lower()}
    case_mal={r["patient_id"] for r in rows if r["group"]=="Case" and "malignant" in r["cell_type"].lower()}
    print("  patients in BOTH groups for malignant cell:", len(ctrl_mal & case_mal), sorted(ctrl_mal & case_mal)[:5])
    # patient overlap per cell type (independence check for unpaired tests)
    ov=[]
    for ct in {r["cell_type"] for r in rows}:
        cs={r["patient_id"] for r in rows if r["cell_type"]==ct and r["group"]=="Case"}
        ns={r["patient_id"] for r in rows if r["cell_type"]==ct and r["group"]=="Control"}
        if cs & ns: ov.append((ct, len(cs&ns), len(cs), len(ns)))
    print("  cell types with patient overlap between groups:", ov[:8] if ov else "none")

print("\n=== (3) sample registry counts ===")
clin_pat=rd(os.path.join(A,"cbio_v3_clinical_patient.csv"))
for ctx in ["LUAD","CRC","STAD","PAAD","HCC","ESCC"]:
    pts={r["patient_id"] for r in clin_pat if r["context"]==ctx}
    smp_any={r["sample_id"] for r in expr if r["context"]==ctx}
    muts={r["sample_id"] for r in prof if r["context"]==ctx}
    print(f"  {ctx}: patients(clinical)={len(pts)} expression_samples={len(smp_any)} mutation_profiled={len(muts)}")
# GEO cohorts: count patients per cohort from processed objects metadata if available
import glob
reg=[]
for d in [r"C:\Users\fengq\Desktop\EGFR\EGFR_ERBB_context_project_v2\data_processed\bulk",
          r"C:\Users\fengq\Desktop\EGFR\EGFR_context_expansion\data_processed\bulk",
          r"C:\Users\fengq\Desktop\EGFR\EGFR胃癌\EGFR_ERBB_context_project_v1\data_processed\bulk"]:
    if os.path.isdir(d): reg+=glob.glob(os.path.join(d,"*_processed.rds"))
print("  bulk processed objects found:", len(reg))
