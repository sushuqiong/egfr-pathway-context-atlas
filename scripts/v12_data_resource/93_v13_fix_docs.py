#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v13.1: fix manuscript/table/document findings from the three cold reviews."""
import csv, os, re
V13=r"C:\Users\fengq\Desktop\EGFR\EGFR的v13"; R=os.path.join(V13,"results"); PK=os.path.join(V13,"dataset_package")
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
log=[]
# ---------- 1. manuscript generator: medians must be sorted; wording fixes ----------
p=os.path.join(V13,"scripts","83_v13_manuscript.py"); s=open(p,encoding="utf-8").read()
s=s.replace("import csv, os, re","import csv, os, re, statistics")
s=s.replace("r2=[float(r[\"r2_overall\"]) for r in col]; vif=[float(r[\"max_vif_predictor\"]) for r in col]",
            "r2=[float(r[\"r2_overall\"]) for r in col]; vif=[float(r[\"max_vif_predictor\"]) for r in col]\n"
            "r2_med=statistics.median(r2); vif_med=statistics.median(vif)   # sorted medians, never index[len//2]")
s=s.replace("overall model R-squared median {r2[len(r2)//2]:.2f}","overall model R-squared median {r2_med:.2f}")
s=s.replace("per-predictor VIF median {vif[len(vif)//2]:.2f}","per-predictor VIF median {vif_med:.2f}")
s=s.replace("(median R² = {r2[len(r2)//2]:.2f}","(median R² = {r2_med:.2f}")
# common-gene threshold: state the implemented rule and the low-information band
s=s.replace("and marks it not scorable when fewer than three members are shared;",
            "and marks it not scorable when fewer than two members are shared, with modules sharing only two members flagged as low-information;")
s=s.replace("common-gene sensitivity uses the module members present in every cohort, flags a module when the effect direction disagrees with full-member scoring in at least 20% of cohorts, and marks it not scorable when fewer than three members are shared;",
            "common-gene sensitivity uses the module members present in every cohort, flags a module when the effect direction disagrees with full-member scoring in at least 20% of cohorts, marks it not scorable when fewer than two members are shared, and reports modules with exactly two shared members as low-information;")
# patient-count definition made explicit
s=s.replace("({n_assays} assay records, {n_pat} patients with available identifiers, 12 platform annotations)",
            "({n_assays} assay records from 27 curated series of which 26 form the case-control resource, {n_pat} patients with available identifiers across those 26 cohorts, 12 platform annotations)")
# file count and table references
open(p,"w",encoding="utf-8").write(s)
log.append("manuscript generator: sorted medians, common-gene threshold states the implemented rule, patient-count definition explicit")
# ---------- 2. Word builder: S7 pair count, Table 1 footnote, S2 over 26 cohorts, S5 threshold ----------
q=os.path.join(V13,"scripts","86_v13_word_outputs.py"); t=open(q,encoding="utf-8").read()
t=t.replace("3 contexts; 29,451 patient-module pairs","3 contexts; 20,451 patient-module pairs")
t=t.replace('doc.add_paragraph("Case-control series only (26 cohorts). One treatment-response series (GSE16879, 43 samples) was reviewed and excluded (Supplementary Table S9).")',
            'doc.add_paragraph("Case-control series only (26 cohorts; 2,711 assay records; 1,086 patients with identifiers; 9 cohorts provide no patient identifiers and are analysed unpaired). One treatment-response series (GSE16879, 43 samples) was reviewed and excluded: see Supplementary Table S4 for every exclusion and flag.")')
t=t.replace('three_line(doc,["Module","Members","Minimum coverage","Cohorts with incomplete coverage"]',
            'three_line(doc,["Module","Members","Minimum coverage","Case-control cohorts with incomplete coverage (of 26)"]')
t=t.replace("""cov=rd(os.path.join(PK,"04_modules","platform_module_coverage.csv")); mods={}
for r in cov:
    m=r["module"]; c=float(r["coverage"]); d=mods.setdefault(m,dict(members=r["n_members"],minc=1.0,n_inc=0))""",
"""cov=rd(os.path.join(PK,"04_modules","platform_module_coverage.csv"))
_cc={r["accession"] for r in cc}
cov=[r for r in cov if r["accession"] in _cc]           # case-control cohorts only (26), not the excluded series
mods={}
for r in cov:
    m=r["module"]; c=float(r["coverage"]); d=mods.setdefault(m,dict(members=r["n_members"],minc=1.0,n_inc=0))""")
t=t.replace('["Common-gene sensitivity","re-score with members present in every cohort; flag when the direction disagrees in >=20% of cohorts; not scorable when <3 members are shared"]',
            '["Common-gene sensitivity","re-score with the members present in every cohort; flag when the effect direction disagrees with full-member scoring in >=20% of cohorts; not scorable when fewer than two members are shared; exactly two shared members is reported as low-information"]')
t=t.replace('["Bulk module scores and cohort effects","3 cohorts (GSE13911, GSE44076, GSE47460); 49 effects","Spearman 1.00 per module; maximum absolute difference in effect and standard error = 0","exact reproduction"]',
            '["Bulk module scores","3 cohorts (GSE13911, GSE44076, GSE47460); per-sample scores","Spearman 1.00 for every module (per-sample score table in 08_qc)","exact reproduction"]')
t=t.replace('''["Cox models refitted from shipped scores","LUAD, CRC, squamous oesophageal; 68 comparisons"''',
            '''["Bulk cohort effects and standard errors","3 cohorts; 49 effects","maximum absolute difference in effect and standard error = 0","exact reproduction"],\n ["Cox models refitted from shipped scores","LUAD and CRC univariable, squamous oesophageal univariable and age-plus-stage; 68 comparisons"''')
t=t.replace('["Collinearity: per-predictor VIF","median 2.09, maximum 4.53 (explains why a high overall R2 coexists with modest VIF)"]',
            '["Collinearity: per-predictor VIF","median 2.09, maximum 4.53; the overall model R-squared (how well the four scores jointly explain disease status) is a different quantity from the per-predictor VIF (how far the scores duplicate one another)"]')
open(q,"w",encoding="utf-8").write(t)
log.append("Word builder: S7 pair count 20,451, S2 coverage over 26 case-control cohorts, Table 1 footnote points to S4, S5 threshold and validation-evidence wording corrected")
# ---------- 3. README + Zenodo guide + source versions: one canonical set of numbers ----------
rm=open(os.path.join(PK,"00_README.md"),encoding="utf-8").read()
rm=rm.replace("| 01_cohort_registry | cohort registry and provenance | `v12_cohort_registry.csv`, `TableS1_accessions.csv`, `TableS1b_cohort_pubmed_map.csv` |",
              "| 01_cohort_registry | cohort registry, provenance, source versions and CELLxGENE identifiers | `cohort_registry.csv`, `source_versions.csv`, `cellxgene_sources.csv`, `TableS1_accessions.csv`, `TableS1b_cohort_pubmed_map.csv` |")
rm=rm.replace("`cbio_v3_patient_module_scores.csv`","`tcga_patient_module_scores.csv`")
rm=rm.replace("| 08_qc | coverage gaps, exclusions and layout checks | `module_coverage_gaps.csv`, `exclusion_and_flag_log.csv`, `figure_layout_qa.csv` |",
              "| 08_qc | coverage, exclusions, validation and layout checks | `module_coverage_gaps.csv`, `exclusion_and_flag_log.csv`, `figure_layout_qa.csv`, `qc_*` tables, `curation_flow.csv`, `file_inventory_and_checksums.csv`, `checksums_sha256.txt` |")
rm=rm.replace("Module gene coverage is incomplete in part of the cohorts (worst case: RET/ALK/NTRK modules down to 33% of members in one platform). Composition scores are enrichment scores, not cell proportions. Cohort count is not patient count (27 cohorts, 1,138 unique patients).",
              "Module gene coverage is incomplete in part of the cohorts (worst case: RET/ALK/NTRK modules down to 33% of members in one platform). Composition scores are enrichment scores, not cell proportions. Cohort count is not patient count: 27 curated series contain 26 case-control cohorts, of which 18 provide patient identifiers and 9 do not, so 1,086 is the number of patients with identifiers (the patient count of the remaining 9 cohorts is unknown, not one).")
rm=rm.replace("the resource is not a patient-level multi-omics resource: the same disease label in different layers does not imply the same patients.",
              "the resource is not a patient-level multi-omics resource: the same disease label in different layers does not imply the same patients. In `07_estimates/per_cohort_effects.csv` the columns mean_*/sd_* describe all case and control samples of the cohort, whereas yi and vi are computed on complete pairs only for paired cohorts.")
rm=rm.replace("## Licence compliance","## CSV encoding\nAll CSV files are UTF-8 without a byte-order mark. The `rows` column of `08_qc/file_inventory_and_checksums.csv` counts data rows (header excluded), and the two verification files record their own pre-finalisation hashes (a self-reference note is given in `checksums_sha256.txt`).\n\n## Licence compliance")
open(os.path.join(PK,"00_README.md"),"w",encoding="utf-8").write(rm)
g=os.path.join(V13,"03_Zenodo上传指南.md"); gt=open(g,encoding="utf-8").read()
gt=gt.replace("27 case-control expression cohorts (2,754 assay records, 1,138 unique patients, 12 platforms)",
              "26 case-control expression cohorts (2,711 assay records, 1,086 patients with identifiers, 12 platforms; 27 curated series in total, one of which is a treatment-response design excluded from the case-control resource)")
gt=gt.replace("Scope: 27 case-control expression cohorts","Scope: 26 case-control expression cohorts")
gt=gt.replace("github.com/sushuqiong/egfr-pathway-context-atlas","github.com/sushuqiong/cross-disease-transcriptomic-resource")
open(g,"w",encoding="utf-8").write(gt)
sv=rd(os.path.join(PK,"01_cohort_registry","source_versions.csv"))
cg=rd(os.path.join(PK,"01_cohort_registry","cellxgene_sources.csv"))
ids="; ".join(f"{r['context']}: dataset_version_id {r['dataset_version_id']} (collection {r['collection_id']})" for r in cg if r["dataset_version_id"])
for r in sv:
    if "CELLxGENE" in r["source"]:
        r["version_or_release"]=("current dataset versions verified against the CELLxGENE API on 2026-09-19 (cell counts and titles match the locally processed files): "+ids)
        r["licence"]="CELLxGENE terms of use, per dataset; dataset pages list the licence (CC-BY-4.0 for most datasets)"
with open(os.path.join(PK,"01_cohort_registry","source_versions.csv"),"w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(sv[0].keys())); w.writeheader(); w.writerows(sv)
log.append("README, Zenodo guide and source_versions.csv aligned on one set of numbers and on the verified CELLxGENE identifiers")
for line in log: print(" -",line)
