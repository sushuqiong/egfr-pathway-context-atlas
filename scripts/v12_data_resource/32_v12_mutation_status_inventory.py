#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12 deliverables: (a) per-sample mutation assay status (not-assayed / assayed-no-variant / variant),
(b) resource inventory table across bulk, single-cell and TCGA layers."""
import csv, os, collections
RAW=r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\data_raw\cbio_v3"
A  =r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas\results"
V  =r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\reruns\results"
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12\results"
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p,fields=None):
    if not rows: return
    with open(p,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# ---------- (a) mutation assay status per sample x gene ----------
prof=rd(os.path.join(V,"v11_mut_profiled_samples.csv"))
mut=rd(os.path.join(A,"cbio_v3_mutations.csv"))
by_ctx=collections.defaultdict(list)
for r in prof: by_ctx[r["context"]].append(r["sample_id"])
mutset=collections.defaultdict(set)
for r in mut: mutset[(r["context"], r["gene"])] .add(r["sample_id"])
genes=["KRAS","TP53","EGFR","ERBB2"]
rows=[]
for ctx, samples in sorted(by_ctx.items()):
    for s in samples:
        for g in genes:
            present = s in mutset.get((ctx,g), set())
            profiled = True
            rows.append(dict(context=ctx, sample_id=s, gene=g,
                             assay_status="mutation_assayed_no_variant_reported" if not present else "variant_reported",
                             assayed=1, variant_reported=int(present)))
wr(rows, os.path.join(V12,"v12_mutation_status_by_sample.csv"))
status_counts=collections.Counter((r["context"],r["gene"],r["assay_status"]) for r in rows)
print("mutation status table rows:", len(rows))
for k in sorted(status_counts)[:8]: print("  ",k,status_counts[k])

# ---------- (b) resource inventory ----------
inv=[]
bulk=rd(os.path.join(V12,"v12_cohort_summary.csv"))
for r in bulk:
    inv.append(dict(layer="bulk_GEO", unit=r["accession"], n_assay_records=r["n_assays"], n_samples=r["n_samples"],
                    n_patients=r["n_patients"], n_cells="", case_definition="see sample registry",
                    control_definition="see sample registry", platform=r["platform"], notes=""))
sc=rd(os.path.join(V12,"v12_sc_dataset_audit.csv")) if os.path.exists(os.path.join(V12,"v12_sc_dataset_audit.csv")) else []
for r in sc:
    inv.append(dict(layer="single_cell", unit=r["context"], n_assay_records="", n_samples="",
                    n_patients=r["donors"], n_cells=r["cells_used"], case_definition=r["arms"],
                    control_definition=r["control_kinds"], platform="10x/CellxGene", notes=f"cells_total={r['cells_total']}"))
clin=rd(os.path.join(A,"cbio_v3_clinical_patient.csv"))
expr=rd(os.path.join(A,"cbio_v3_expression_gene_sample.csv"))
profiles=rd(os.path.join(V,"v11_mut_profiled_samples.csv"))
for ctx in ["LUAD","CRC","STAD","PAAD","HCC","ESCC"]:
    pts={r["patient_id"] for r in clin if r["context"]==ctx}
    smp={r["sample_id"] for r in expr if r["context"]==ctx}
    mp={r["sample_id"] for r in profiles if r["context"]==ctx}
    note="restricted to squamous-cell carcinoma (96 of 185 patients)" if ctx=="ESCC" else ""
    if ctx=="ESCC":
        sq=rd(os.path.join(V12,"v12_escc_squamous_samples.csv"))
        smp_sq={r["sample_id"] for r in sq}; smp=smp & smp_sq; mp=mp & smp_sq; pts={r["patient_id"] for r in sq}
    inv.append(dict(layer="TCGA", unit=ctx, n_assay_records=len(mp), n_samples=len(smp), n_patients=len(pts),
                    n_cells="", case_definition="tumour", control_definition="TCGA reference/normal where available",
                    platform="GDC (RNA-seq/mutation/CNA)", notes=note))
wr(inv, os.path.join(V12,"v12_resource_inventory.csv"))
print("\n== resource inventory ==")
for r in inv: print(f"  {r['layer']:11} {r['unit']:12} assays={r['n_assay_records']:>5} samples={r['n_samples']:>5} patients={r['n_patients']:>4} cells={r['n_cells']}")
print("\nTOTAL bulk assays:", sum(int(r["n_assay_records"]) for r in inv if r["layer"]=="bulk_GEO"))
print("TOTAL single-cell cells:", sum(int(r["n_cells"]) for r in inv if r["layer"]=="single_cell" and r["n_cells"]))
