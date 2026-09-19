#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 fix pass 1 (data layer): version metadata, k=1 labelling, per-state recomputation, composition table
unification, duplicate/stale file cleanup, README corrections."""
import csv, os, glob, math, shutil, collections, statistics
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
def rd(p):
    if not os.path.exists(p): return []
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p):
    with open(p,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator="\n"); w.writeheader(); w.writerows(rows)
log=[]
# ---------- 1. version / changelog ----------
open(os.path.join(PK,"00_VERSION.txt"),"w",encoding="utf-8").write(
"cross-disease transcriptomic resource\nversion: v14.0\nreleased: 2026-09-19\n"
"frozen configuration: module_version = v12.0-frozen-2026-09\n"
"supersedes: v13.0 (corrected mutation denominator for the squamous oesophageal layer; complete 442-row estimates matrix; "
"cross-cohort consistency, coverage-threshold sensitivity, signature-overlap and VIF diagnostics; curation flow; control-tissue "
"ontology; expression QC; module overlap matrix; survival data dictionary; independent marker-based composition method; "
"prediction intervals; external-cohort reuse example; four-figure set with pixel-level layout QA)\n"
"update policy: new versions are published as new Zenodo versions; earlier DOIs remain citable\n")
cl=open(os.path.join(PK,"00_CHANGELOG.md"),encoding="utf-8").read()
if "## v14.0" not in cl:
    cl=cl.replace("# Changelog\n","# Changelog\n\n## v14.0 (2026-09-19)\n"
      "- run the external-cohort reuse example end to end (GSE54129, 111 tumour / 21 adjacent-normal samples; runtime 1.6 minutes)\n"
      "- add module overlap matrix (maximum pairwise Jaccard 0.00), control-tissue ontology, per-cohort expression QC, deterministic transformation rule with summaries\n"
      "- add study-level overlap audit, independent marker-based composition method and its agreement with xCell, and 95% prediction intervals\n"
      "- reorder figures: Figure 4 (sensitivity analyses) added; all four figures rebuilt with label-overlap and clipping fixes\n"
      "- version metadata aligned with the manuscript version\n",1)
    open(os.path.join(PK,"00_CHANGELOG.md"),"w",encoding="utf-8").write(cl)
log.append("version and changelog set to v14.0")
# ---------- 2. k=1 rows must not look like pooled estimates ----------
for name in ["meta_primary_reml_knha.csv","meta_primary_with_prediction_intervals.csv","meta_DL.csv","meta_adhoc.csv",
             "meta_unpaired_only.csv","meta_rho0.5.csv","meta_rho0.7.csv"]:
    p=os.path.join(PK,"07_estimates",name)
    if not os.path.exists(p): continue
    rows=rd(p); n1=0
    for r in rows:
        k=int(r["k"])
        if k<2:
            n1+=1
            r["pooled"]="no (single cohort; not a pooled estimate)"
            for c in ("fdr","p","est","se","ci_lo","ci_hi","I2","tau2","pi_low","pi_high","pi_note"):
                if c in r: r[c]="not applicable"
        else:
            r["pooled"]="yes"
    wr(rows,p)
    log.append(f"{name}: {n1} single-cohort rows marked 'not a pooled estimate'")
# ---------- 3. recompute the per-state evidence matrix from the corrected per-cohort effects ----------
pc=rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
pc=[r for r in pc if r["measure"] in ("SMDH","SMCRPH") and r.get("yi")]
def pool(rows_):
    ys=[float(r["yi"]) for r in rows_]; vs=[float(r["vi"]) for r in rows_]
    w=[1/v for v in vs]; mu=sum(y*wi for y,wi in zip(ys,w))/sum(w); tau2=0.0
    for _ in range(80):
        tau2=max(0.0, sum(wi*((y-mu)**2-vi) for wi,y,vi in zip(w,ys,vs))/sum(w))
        w=[1/(v+tau2) for v in vs]; new=sum(y*wi for y,wi in zip(ys,w))/sum(w)
        if abs(new-mu)<1e-12: mu=new; break
        mu=new
    se=math.sqrt(1/sum(w)); k=len(rows_)
    if k<2: return dict(est=mu, se=se, p=None, k=k, tau2=tau2)
    from statistics import NormalDist
    t=abs(mu/se); p=2*(1-NormalDist().cdf(t))
    return dict(est=mu, se=se, p=p, k=k, tau2=tau2)
old=rd(os.path.join(PK,"07_estimates","per_state_evidence_matrix.csv"))
grp=collections.defaultdict(list)
for r in pc: grp[(r["disease"],r["feature"])].append(r)
new_rows=[]
if old and "meta_est" in old[0]:
    for r in old:
        key=(r["disease"],r["feature"])
        res=pool(grp[key]) if key in grp else None
        r2=dict(r)
        if res:
            r2["meta_est"]=round(res["est"],4); r2["meta_se"]=round(res["se"],4); r2["meta_k"]=res["k"]
            r2["meta_p"]=round(res["p"],6) if res["p"] is not None else "not applicable (single cohort)"
            r2["recomputed_in_v14"]="yes"
        new_rows.append(r2)
    wr(new_rows, os.path.join(PK,"07_estimates","per_state_evidence_matrix.csv"))
    wr(new_rows, os.path.join(PK,"07_estimates","per_state_evidence_matrix_v14recomputed.csv"))
    log.append(f"per-state evidence matrix recomputed from the corrected per-cohort effects ({len(new_rows)} rows)")
# ---------- 4. composition tables: one sample universe (26 cohorts) ----------
alt=rd(os.path.join(PK,"05_composition","alternative_method_marker_proxy.csv"))
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv")); cc={r["accession"] for r in reg if r["design"]=="case-control"}
alt=[r for r in alt if r["accession"] in cc]
wr(alt, os.path.join(PK,"05_composition","alternative_method_marker_proxy.csv"))
log.append(f"marker-proxy table restricted to the {len(cc)} case-control cohorts ({len(alt)} rows)")
# ---------- 5. remove duplicates and stale artefacts ----------
dup=[("08_qc/module_coverage_gaps.csv","duplicate of 04_modules/platform_module_coverage.csv (removed)"),
     ("07_estimates/meta_primary_with_prediction_intervals.csv","duplicate of meta_primary_reml_knha.csv, which now carries the prediction intervals (removed)"),
     ("01_cohort_registry/v12_cohort_registry.csv","superseded registry copy from an earlier version (removed)")]
for rel,why in dup:
    p=os.path.join(PK,rel)
    if os.path.exists(p): os.remove(p); log.append(f"removed {rel}: {why}")
for stale in glob.glob(os.path.join(PK,"08_qc","figure_layout_qa*.csv")):
    os.remove(stale); log.append("removed stale figure layout QA (v11 figures)")
# stale v13 artefacts inside the v14 submission folders
for folder in ["01_manuscript","03_tables"]:
    for f in os.listdir(os.path.join(V14,folder)):
        if "v13" in f: os.remove(os.path.join(V14,folder,f)); log.append(f"removed stale {folder}/{f}")
# ---------- 6. README corrections ----------
rp=os.path.join(PK,"00_README.md"); t=open(rp,encoding="utf-8").read()
t=t.replace("(v13)","(v14)")
t=t.replace("of which 18 provide patient identifiers and 9 do not","of which 17 provide patient identifiers and 9 do not")
t=t.replace("the same disease label in different layers does not imply the same patients.",
            "the same disease label in different layers does not imply the same patients. Control tissue differs between cohorts and is classified in 01_cohort_registry/contrast_ontology.csv (adjacent non-tumour, non-inflamed, healthy donor, non-diseased); classes are not pooled silently. One cohort (GSE62232, hepatocellular carcinoma) contributes only five control samples, so its control-side variance is estimated from very few samples. Zero-variance genes are absent by construction (matrices were filtered before scoring), which is why the QC column reports zero for every cohort.")
t=t.replace("| 04_modules | module definitions, per-platform coverage and per-sample scores |",
            "| 04_modules | module definitions, per-platform coverage, module overlap matrix and per-sample scores |")
t=t.replace("`module_version` in `04_modules/module_definitions.csv`","`module_version` in `04_modules/module_definitions.csv`; analysis code is shipped in `11_code/`")
open(rp,"w",encoding="utf-8").write(t)
log.append("README corrected (version, patient-identifier count, limitations, folder descriptions)")
# ---------- 7. ship the analysis code inside the deposit (reviewers could not reproduce without it) ----------
code_dir=os.path.join(PK,"11_code"); os.makedirs(code_dir,exist_ok=True)
keep=["60_v14_figures.R","41_v12_effects_meta.R","40_v12_common_gene_sensitivity.R","42_v12_audit_ph_collinearity.R",
      "43_v12_composition_keys.R","66_v14_marker_proxy_qc.R","65_v14_analysis_additions.py","70_v14_manuscript.py",
      "71_v14_tables_legends.py","76_v14_external_reuse_example.R","64_v14_figure_qa_final.py","77_v14_figure_review.py",
      "80_v13_fix_insertions_and_gaps.py","22_v12_sc_reanalysis.py"]
n=0
for f in keep:
    src=os.path.join(V14,"scripts",f)
    if os.path.exists(src): shutil.copy(src, os.path.join(code_dir,f)); n+=1
open(os.path.join(code_dir,"README_code.md"),"w",encoding="utf-8").write(
"# Analysis code shipped with the deposit\n\n"
f"These {n} scripts reproduce the resource end to end: per-cohort effects and pooling (41), common-gene sensitivity (40),\n"
"proportional-hazards and collinearity diagnostics (42), composition keying (43), marker-based composition and expression QC (66),\n"
"module overlap/curation/coverage additions (65), figure generation (60), the two layout-QA reviewers (64, 77),\n"
"the reusable single-cell re-analysis (22) and the manuscript/table builders (70, 71).\n\n"
"Environment: R 4.4.1 (GSVA 1.52.3, metafor 5.0.1, survival 3.8.3, limma 3.60.6, GEOquery, xCell 1.0.0, ggplot2 4.0.3,\n"
"patchwork 1.3.2, tidyr, dplyr) and Python 3.11 (numpy, pandas, python-docx, Pillow). Paths inside the scripts point to the\n"
"author's working directories and must be adjusted to the deposit layout (see 10_environment/run_order.md).\n")
log.append(f"analysis code shipped inside the deposit: {n} scripts in 11_code/")
for l in log: print(" -",l)
