#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12 final checks: manuscript numbers vs frozen tables; Data Descriptor limits; package integrity."""
import csv, os, re, sys
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results"); PK=os.path.join(V12,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
md=open(os.path.join(V12,"01_manuscript","DataDescriptor_v12.md"),encoding="utf-8").read()
ok=[]; bad=[]
def chk(c,good,badder):(ok if c else bad).append(good if c else badder)
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv"))
cc=[r for r in reg if r.get("design")=="case-control"]; ex=[r for r in reg if r.get("design")!="case-control"]
n_c=len(cc); n_a=sum(int(r["n_assay_records"]) for r in cc)
n_p=sum(int(r["n_unique_patients"]) for r in cc if str(r["n_unique_patients"]).isdigit())
n_pair=sum(1 for r in cc if r.get("paired_design_used")=="yes")
n_nopid=sum(1 for r in cc if r.get("patient_identity_available")=="no")
cov=rd(os.path.join(R,"v12_gene_coverage.csv")); scc=rd(os.path.join(R,"v12_sc_comparisons.csv"))
pc=rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
ph=rd(os.path.join(R,"v12_qc_cox_ph_assumption.csv")); col=rd(os.path.join(R,"v12_qc_composition_collinearity.csv"))
title=md.splitlines()[0].lstrip("# ").strip(); ab=re.search(r"\*\*Abstract\*\*(.*?)\*\*Background", md, re.S).group(1)
abw=len(re.findall(r"\S+", ab))
chk(len(title)<=110, f"title {len(title)} chars (<=110)", f"title too long: {len(title)}")
chk(abw<=170, f"abstract {abw} words (<=170)", f"abstract too long: {abw}")
for phrase in [f"{n_c} case-control expression cohorts", f"{n_a} assay records", f"{n_p} patients with available identifiers",
               f"{n_pair} paired cohorts", f"{len(scc)} comparisons", f"{len(pc)} cohort-module rows"]:
    chk(phrase in md, f"manuscript states '{phrase}'", f"missing: {phrase}")
chk(len(ex)==1 and "treatment-response" in ex[0]["design"], "one treatment-response series excluded and flagged", "excluded series not flagged")
chk(n_nopid==9, f"nine cohorts without patient identifiers recorded ({n_nopid})", f"unexpected count of cohorts without patient ids: {n_nopid}")
chk(sum(1 for r in ph if r["ph_violation"].upper()=="TRUE")==0, "no PH violations (table)", "PH violations present")
chk(len(col)>0, f"composition collinearity diagnostics for {len(col)} cohorts", "collinearity diagnostics missing")
for d in ["01_cohort_registry","02_sample_annotation","03_expression","04_modules","05_composition","06_single_cell",
          "07_estimates","08_qc","09_reuse_examples","10_environment"]:
    chk(os.path.isdir(os.path.join(PK,d)), f"package folder {d}", f"MISSING folder {d}")
for f in ["00_README.md","08_qc/file_inventory_and_checksums.csv","08_qc/checksums_sha256.txt",
          "05_composition/composition_scores_per_sample.csv","07_estimates/per_cohort_effects.csv",
          "09_reuse_examples/example_input/demo_expression_matrix.csv","09_reuse_examples/expected_output/example2_composition_ratio.csv"]:
    chk(os.path.exists(os.path.join(PK,f)), f"file present: {f}", f"MISSING: {f}")
inv=rd(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"))
chk(len(inv)>=45, f"inventory covers {len(inv)} files", "inventory too small")
comp=rd(os.path.join(PK,"05_composition","composition_scores_per_sample.csv"))
chk(all("sample_id" in r for r in comp[:5]), "composition table carries sample keys", "composition table lacks sample keys")
print("=== v12 FINAL CHECKS ==="); print("passed:",len(ok)); [print("  OK  ",x) for x in ok]
print("issues:",len(bad)); [print("  ISSUE",x) for x in bad]
sys.exit(1 if bad else 0)
