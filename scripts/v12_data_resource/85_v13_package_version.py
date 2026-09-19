#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13: refresh the dataset package (complete estimates layer, new QC, versioning, README guidance),
then rebuild the Word tables/legend file and the v13 audits."""
import csv, os, shutil, hashlib, subprocess, sys
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results"); PK=os.path.join(V13,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# ---------- estimates layer: complete 442-row matrix ----------
full=rd(os.path.join(R,"v13_percohort_effects_complete.csv")); wr(full, os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
shutil.copy(os.path.join(R,"v13_not_estimable_pairs.csv"), os.path.join(PK,"07_estimates","not_estimable_pairs.csv"))
# ---------- QC ----------
qc=[("v13_qc_cross_cohort_consistency.csv","qc_cross_cohort_consistency.csv"),
    ("v13_qc_coverage_threshold_sensitivity.csv","qc_coverage_threshold_sensitivity.csv"),
    ("v13_qc_signature_overlap.csv","qc_module_vs_xcell_signature_overlap.csv"),
    ("v13_qc_vif_by_predictor.csv","qc_vif_by_predictor.csv"),
    ("v13_qc_curation_flow.csv","curation_flow.csv")]
for s,d in qc: shutil.copy(os.path.join(R,s), os.path.join(PK,"08_qc",d))
# ---------- versioning ----------
VERSION=("cross-disease transcriptomic resource\nversion: v13.0\nreleased: 2026-09-19\n"
         "frozen configuration: module_version = v12.0-frozen-2026-09\n"
         "supersedes: v12.0 (this version adds the corrected mutation denominator for the squamous oesophageal layer, "
         "a complete cohort-by-module estimates matrix including not-estimable pairs, cross-cohort consistency and "
         "coverage-threshold sensitivity tables, a module-versus-xCell signature overlap audit, per-predictor VIF, "
         "curation-flow counts and explicit score-construction rules)\n"
         "update policy: new versions are published as new Zenodo versions; earlier DOIs remain citable\n")
open(os.path.join(PK,"00_VERSION.txt"),"w",encoding="utf-8").write(VERSION)
CHANGELOG=("# Changelog\n\n## v13.0 (2026-09-19)\n"
 "- correct the mutation-prevalence denominator for the squamous oesophageal layer (185 profiles including 89 adenocarcinomas -> 96 squamous profiles); TP53 86/96 (89.6%), EGFR 2/96, KRAS 0/96, ERBB2 0/96\n"
 "- add the complete cohort-by-module estimates matrix (442 rows = 434 estimated + 8 not estimable, each with a reason)\n"
 "- add cross-cohort direction consistency per context-module pair (112 of 165 pairs, 68%, share the same sign in every cohort)\n"
 "- add coverage-threshold sensitivity of the pooled results (BH-significant states: 13 / 13 / 12 / 6 at coverage 0.60 / 0.80 / 0.90)\n"
 "- add module-versus-xCell signature overlap audit (all 17 modules share >20% of members with the xCell panel; maximum 100%) and reframe composition adjustment as a sensitivity analysis\n"
 "- add per-predictor VIF within the disease-status model (median 2.09, maximum 4.53) alongside the overall model R-squared, with an explicit explanation of the difference\n"
 "- state the score-construction rule for each layer and add a layer-selection table\n"
 "- add curation-flow counts and the source-version/licence table\n"
 "- separate exact reproduction from rank agreement in all validation statements\n\n"
 "## v12.0\n- pivot to a data-resource description; metadata-driven pairing; donor-aware single-cell design; complete estimates with negative results; SHA-256 inventory\n")
open(os.path.join(PK,"00_CHANGELOG.md"),"w",encoding="utf-8").write(CHANGELOG)
# ---------- README: append guidance, versioning and licence sections ----------
rdm=os.path.join(PK,"00_README.md"); txt=open(rdm,encoding="utf-8").read()
txt=txt.replace("# Cross-disease growth-factor and tissue-composition transcriptomic resource (v12)",
                "# Cross-disease growth-factor and tissue-composition transcriptomic resource (v13)")
add="""
## Which score layer to use
| Question | Layer | File | Notes |
|---|---|---|---|
| Does a module differ between case and control within this cohort? | bulk GSVA z-scores | `04_modules/sample_module_scores_gsva_z.csv` | cohort-internal; cross-cohort only as effect sizes |
| Does a module differ across tumour contexts at patient level? | TCGA member-mean z-scores | `07_estimates/per_cohort_effects.csv` (TCGA context rows) + `cbio_v3_patient_module_scores.csv` | construction rule in Methods |
| Does a module differ between cell types or within a cell type between conditions? | single-cell member means | `06_single_cell/` | donor-level means tested, not cells |
| Is tissue composition a confounder here? | xCell compartment scores | `05_composition/composition_scores_per_sample.csv` | enrichment scores, not proportions; shares genes with module scores -> sensitivity analysis only |

## Versioning and maintenance
The deposit carries a version number (`00_VERSION.txt`) and a changelog (`00_CHANGELOG.md`). Updates are published as new Zenodo versions so older DOIs stay citable. The frozen module configuration is identified by `module_version` in `04_modules/module_definitions.csv`.

## Licence compliance
Derived data in this package are released under CC-BY-4.0 by the authors of this resource. Upstream data remain under their own terms: GEO series terms as declared by each submitter, TCGA/GDC open-access terms (no controlled-access data were used), and CELLxGENE dataset terms. Redistributing source matrices requires observing those upstream terms; see `01_cohort_registry/source_versions.csv`.
"""
txt = txt + add
open(rdm,"w",encoding="utf-8").write(txt)
# ---------- inventory ----------
inv=[]
for d0,_,fn in os.walk(PK):
    for f in sorted(fn):
        fp=os.path.join(d0,f); rel=os.path.relpath(fp,PK); h=hashlib.sha256()
        with open(fp,"rb") as fh:
            for c in iter(lambda: fh.read(1<<20), b""): h.update(c)
        nr=""
        if f.lower().endswith(".csv"):
            try: nr=sum(1 for _ in open(fp,encoding="utf-8-sig"))-1
            except Exception: nr=""
        inv.append(dict(file=rel, bytes=os.path.getsize(fp), rows=nr, sha256=h.hexdigest()))
wr(inv, os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"))
with open(os.path.join(PK,"08_qc","checksums_sha256.txt"),"w",encoding="utf-8") as f:
    for r in inv: f.write(f"{r['sha256']}  {r['file']}\n")
print("package: files",len(inv),"| MB",round(sum(int(r['bytes']) for r in inv)/1e6,2))
# ---------- Word tables + legends ----------
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv")); cov=rd(os.path.join(PK,"04_modules","platform_module_coverage.csv"))
ne=rd(os.path.join(PK,"07_estimates","not_estimable_pairs.csv")); con=rd(os.path.join(R,"v13_qc_cross_cohort_consistency.csv"))
sen=rd(os.path.join(R,"v13_qc_coverage_threshold_sensitivity.csv")); so=rd(os.path.join(R,"v13_qc_signature_overlap.csv"))
vif=rd(os.path.join(R,"v13_qc_vif_by_predictor.csv")); flow=rd(os.path.join(R,"v13_qc_curation_flow.csv"))
scv=rd(os.path.join(R,"v12_qc_module_score_effect_verification.csv")); coxv=rd(os.path.join(R,"v12_qc_survival_cox_verification.csv"))
subprocess.run([sys.executable, os.path.join(V13,"scripts","76_v12_word_outputs.py")],capture_output=True,text=True)  # base tables (S1-S5)
print("base Word tables rebuilt")
