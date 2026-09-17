#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v12 low-level-error audit: numbers, placeholders, figures, table structure, join keys, cross-file consistency."""
import csv, os, re, sys, collections
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results"); PK=os.path.join(V12,"dataset_package")
md=open(os.path.join(V12,"01_manuscript","DataDescriptor_v12.md"),encoding="utf-8").read()
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
ok=[]; bad=[]; warn=[]
def chk(c,good,badder=None):
    if c: ok.append(good)
    elif badder: bad.append(badder)
    else: bad.append(good)
# ---------- A. numbers vs tables ----------
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv")); cc=[r for r in reg if r["design"]=="case-control"]
n_cc=len(cc); n_a=sum(int(r["n_assay_records"]) for r in cc); n_p=sum(int(r["n_unique_patients"]) for r in cc if str(r["n_unique_patients"]).isdigit())
n_pair=sum(1 for r in cc if r["paired_design_used"]=="yes"); n_nopid=sum(1 for r in cc if r["patient_identity_available"]=="no")
sc=rd(os.path.join(R,"v12_sc_comparisons.csv")); sig=sum(1 for r in sc if r["fdr"] not in ("","NA") and float(r["fdr"])<0.05)
pc=rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv")); inv=rd(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"))
ph=rd(os.path.join(R,"v12_qc_cox_ph_assumption.csv"))
claims={f"{n_cc} case-control expression cohorts":"cohort count", f"{n_a} assay records":"assay count",
        f"{n_p} patients with available identifiers":"patient count", f"{n_pair} paired cohorts":"paired count",
        f"{n_nopid} cohorts provide no patient identifiers":"no-patient-id count", f"{len(sc)} comparisons":"sc comparison count",
        f"{len(pc)} cohort-module rows":"est row count", f"{len(inv)} files":"inventory file count",
        f"{len(ph)} module features":"PH feature count"}
for ph_,lbl in claims.items(): chk(ph_ in md, f"manuscript states {lbl}: '{ph_}'", f"missing/inconsistent: {lbl} ('{ph_}')")
chk("ten contexts" in md, "states ten contexts", "context count claim missing")
chk("Seventeen modules" in md or "seventeen modules" in md, "states seventeen modules", "module count claim missing")
chk(f"{sig} reach family-wise FDR" in md, f"sc significant count {sig} stated", f"sc significant count mismatch (expect {sig})")
chk("four single-cell datasets" in md or "Four datasets" in md, "states four single-cell datasets", "single-cell dataset count claim missing")
# stale v11 vocabulary / numbers that must not reappear
stale=["55 of 170","21 composition-robust","retained 17","17 states","0.87 of the","median r = 0.11","73 under DerSimonian",
       "squamous cells of the oesophagus were", "external replication was not achieved by any module"]
for st in stale:
    chk(st not in md, f"no stale phrase '{st}'", f"stale phrase present: '{st}'")
# ---------- B. placeholders ----------
allowed=["[DOI to be inserted after Zenodo deposit]"]
for token in ["TODO","TBD","XXX","YOUR_MATRIX","<insert","待定","占位","PLACEHOLDER"]:
    hits=[l.strip()[:90] for l in md.splitlines() if token.lower() in l.lower()]
    chk(not hits, f"no placeholder '{token}'", f"placeholder '{token}': {hits[:2]}")
chk(md.count("[DOI to be inserted after Zenodo deposit]")>=1, "DOI placeholder present as expected", None)
# ---------- C. figures ----------
figs=[f for f in os.listdir(os.path.join(V12,"02_figures")) if f.lower().endswith(".png")]
chk(len(figs)==2, f"two main figures ({len(figs)})", f"expected 2 main figures, found {len(figs)}")
for i in (1,2):
    chk(f"Figure {i}" in md, f"Figure {i} cited in text", f"Figure {i} not cited")
chk(re.search(r"\*\*Figure 1", md) and "Fig1" not in md, "figure captions use full labels", "caption label inconsistency")
# ---------- D. table structure ----------
def table_check(path, name, must_have, min_rows=1):
    if not os.path.exists(path): bad.append(f"missing table: {name}"); return
    rows=rd(path)
    chk(len(rows)>=min_rows, f"{name}: {len(rows)} rows", f"{name}: only {len(rows)} rows")
    if rows:
        cols=set(rows[0].keys())
        for c in must_have: chk(c in cols, f"{name} has column '{c}'", f"{name} missing column '{c}'")
        empty=[c for c in rows[0] if all((r.get(c,"") in ("","NA")) for r in rows)]
        if empty: warn.append(f"{name}: always-empty columns {empty}")
table_check(os.path.join(PK,"01_cohort_registry","cohort_registry.csv"),"registry",["accession","context","platform","design","paired_design_used"],3)
table_check(os.path.join(PK,"02_sample_annotation","sample_annotation_geo_cohorts.csv"),"sample_annotation",["accession","sample_id","patient_id","case_control_role"],100)
table_check(os.path.join(PK,"04_modules","platform_module_coverage.csv"),"coverage",["accession","module","coverage"],100)
table_check(os.path.join(PK,"05_composition","composition_scores_per_sample.csv"),"composition",["accession","sample_id","epi","fib","end","imm"],100)
table_check(os.path.join(PK,"06_single_cell","single_cell_comparisons.csv"),"sc",["context","module","cell_type","comparison_type","test_used","fdr"],50)
table_check(os.path.join(PK,"07_estimates","per_cohort_effects.csv"),"effects",["accession","feature","measure","yi","vi","paired"],100)
# ---------- E. cross-file consistency ----------
acc_reg={r["accession"] for r in reg}; acc_ann={r["accession"] for r in rd(os.path.join(PK,"02_sample_annotation","sample_annotation_geo_cohorts.csv"))}
acc_cov={r["accession"] for r in rd(os.path.join(PK,"04_modules","platform_module_coverage.csv"))}
acc_eff={r["accession"] for r in pc}
chk(acc_ann<=acc_reg, "annotation accessions subset of registry", f"annotation accessions not in registry: {sorted(acc_ann-acc_reg)}")
chk(acc_cov<=acc_reg, "coverage accessions subset of registry", f"coverage accessions not in registry: {sorted(acc_cov-acc_reg)}")
chk(acc_eff<=acc_reg, "effect accessions subset of registry", f"effect accessions not in registry: {sorted(acc_eff-acc_reg)}")
chk(len(acc_eff)==26, f"effects cover {len(acc_eff)} cohorts (26 expected)", f"effects cover {len(acc_eff)} cohorts")
ann=rd(os.path.join(PK,"02_sample_annotation","sample_annotation_geo_cohorts.csv"))
chk(all(r["sample_id"] for r in ann), "every annotation row has a sample_id", "annotation rows without sample_id")
comp=rd(os.path.join(PK,"05_composition","composition_scores_per_sample.csv"))
chk(all(r["sample_id"] for r in comp), "every composition row has a sample_id", "composition rows without sample_id")
# composition keys must exist in the annotation
annkeys={(r["accession"],r["sample_id"]) for r in ann}; compkeys={(r["accession"],r["sample_id"]) for r in comp}
chk(len(compkeys & annkeys)==len(compkeys), f"all {len(compkeys)} composition keys resolve in the annotation",
    f"{len(compkeys-annkeys)} composition keys do not resolve (e.g. {sorted(list(compkeys-annkeys))[:3]})")
# ---------- F. reproducibility pointers ----------
for f in ["10_environment/run_order.md","10_environment/environment.txt","09_reuse_examples/README_examples.md"]:
    chk(os.path.exists(os.path.join(PK,f)), f"present: {f}", f"missing: {f}")
env=open(os.path.join(PK,"10_environment","environment.txt"),encoding="utf-8",errors="replace").read()
chk("GSVA" in env and "metafor" in env, "environment records GSVA and metafor versions", "environment missing package versions")
print("=== v12 LOW-LEVEL AUDIT ===")
print("passed:",len(ok)); print("issues:",len(bad))
for b in bad: print("  ISSUE",b)
if warn:
    print("warnings:")
    for w in warn: print("  WARN",w)
sys.exit(1 if bad else 0)
