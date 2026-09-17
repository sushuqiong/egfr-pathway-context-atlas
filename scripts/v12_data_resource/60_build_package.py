#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble the v12 dataset package (Zenodo-ready) with README, reuse examples and environment records."""
import csv, os, shutil, glob, subprocess, json
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"; R=os.path.join(V12,"results")
P=os.path.join(V12,"dataset_package")
A=r"C:\Users\fengq\Desktop\EGFR\EGFR_pathway_context_atlas"
V11=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\reruns\results"
V10=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\03_表格与补充数据"
GRS=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\03_表格与补充数据"
def cp(src,dst,newname=None):
    if os.path.exists(src):
        target=os.path.join(dst, newname or os.path.basename(src))
        if os.path.abspath(src)==os.path.abspath(target): return True
        os.makedirs(os.path.dirname(target),exist_ok=True); shutil.copy(src, target); return True
    return False
# 01 registry
cp(os.path.join(R,"v12_cohort_registry.csv"), os.path.join(P,"01_cohort_registry"))
for cand in ["TableS1_accessions.csv","TableS1b_cohort_pubmed_map.csv"]:
    for base in (GRS, V10):
        if cp(os.path.join(base,cand), os.path.join(P,"01_cohort_registry")): break
# 02 annotation
cp(os.path.join(P,"02_sample_annotation","sample_annotation_geo_cohorts.csv"), os.path.join(P,"02_sample_annotation"))
cp(os.path.join(R,"v12_escc_squamous_samples.csv"), os.path.join(P,"02_sample_annotation"),"sample_annotation_escc_squamous_tcga.csv")
# 03 expression
cp(os.path.join(P,"03_expression","transformation_log.csv"), os.path.join(P,"03_expression"))
# 04 modules
cp(os.path.join(A,"config","gene_sets_extended.csv"), os.path.join(P,"04_modules"),"module_definitions.csv")
cp(os.path.join(R,"v12_gene_coverage.csv"), os.path.join(P,"04_modules"),"platform_module_coverage.csv")
cp(os.path.join(P,"04_modules","sample_module_scores_gsva_z.csv"), os.path.join(P,"04_modules"))
# 05 composition
for cand in [os.path.join(A,"results","xcell","xcell_composition_scores.csv"),
             os.path.join(A,"results","xcell_composition_scores.csv")]:
    if cp(cand, os.path.join(P,"05_composition"),"xcell_composition_scores.csv"): break
# 06 single cell
cp(os.path.join(R,"v12_sc_dataset_audit.csv"), os.path.join(P,"06_single_cell"),"single_cell_dataset_audit.csv")
cp(os.path.join(R,"v12_sc_comparisons.csv"), os.path.join(P,"06_single_cell"),"single_cell_comparisons.csv")
# 07 estimates
est=[(os.path.join(V11,"v11_percohort_effects.csv"),"per_cohort_effects.csv"),
     (os.path.join(V11,"v11_meta_primary_reml_knha.csv"),"meta_primary_reml_knha.csv"),
     (os.path.join(V11,"v11_meta_DL.csv"),"meta_dersimonian_laird.csv"),
     (os.path.join(V11,"v11_meta_adhoc.csv"),"meta_adhoc_knapp_hartung.csv"),
     (os.path.join(V11,"v11_meta_unpaired_only.csv"),"meta_unpaired_only.csv"),
     (os.path.join(V11,"v11_joint_summary.csv"),"composition_model_summary.csv"),
     (os.path.join(V11,"v11_driver_interactions.csv"),"driver_interactions.csv"),
     (os.path.join(V11,"v11_driver_eligibility.csv"),"driver_eligibility.csv"),
     (os.path.join(V11,"v11_external_crc.csv"),"external_validation_crc.csv"),
     (os.path.join(V11,"v11_mutation_denominators.csv"),"mutation_denominators_all_contexts.csv"),
     (os.path.join(R,"v12_escc_squamous_survival_cox.csv"),"tcga_escc_squamous_survival_cox.csv"),
     (os.path.join(R,"v12_escc_mutation_denominators.csv"),"tcga_escc_squamous_mutation_denominators.csv"),
     (os.path.join(R,"v12_escc_cna_summary.csv"),"tcga_escc_squamous_cna_summary.csv"),
     (os.path.join(V11,"v11_evidence_matrix.csv"),"per_state_evidence_matrix.csv")]
for src,name in est: cp(src, os.path.join(P,"07_estimates"), name)
# 08 qc
cp(os.path.join(R,"v12_gene_coverage.csv"), os.path.join(P,"08_qc"),"module_coverage_gaps.csv")
cp(os.path.join(V11,"..","..","EGFR的v11","04_评审记录与报告","ocr_figure_qa.csv"), os.path.join(P,"08_qc"),"figure_layout_qa.csv")
# exclusion log (documented decisions)
excl=[dict(item="TCGA-ESCA adenocarcinoma samples excluded from the squamous oesophageal layer", n=89,
           reason="patient-level DISEASE_TYPE = adenocarcinoma; the source study contains both histologies", layer="TCGA-derived"),
      dict(item="In utero cells excluded from the gastric single-cell dataset", n=1277,
           reason="control_vs_disease = inutero; not a case or control tissue", layer="single-cell"),
      dict(item="Lung adenocarcinoma single-cell dataset excluded entirely", n=117266,
           reason="source dataset contains tumour tissue only (no normal/adjacent arm)", layer="single-cell"),
      dict(item="Malignant-labelled cells inside non-tumour colorectal samples flagged", n=358,
           reason="raw label inconsistent with tissue type; retained but flagged, not reassigned", layer="single-cell"),
      dict(item="Single-cell comparisons reported as not testable", n=80,
           reason="donor overlap below five complete pairs and arms not donor-disjoint; independence cannot be assumed", layer="single-cell"),
      dict(item="GSE16879 lacks case-control contrast for module scoring", n=43,
           reason="all assay records belong to one disease arm in the processed matrix used here; retained for registry transparency", layer="bulk")]
with open(os.path.join(P,"08_qc","exclusion_and_flag_log.csv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["item","n","reason","layer"]); w.writeheader(); w.writerows(excl)
# 09 reuse examples
ex1 = """#!/usr/bin/env Rscript
# Reuse example 1: replace a module gene set and re-score one cohort.
# Input: dataset_package/03_expression (or your own processed matrix) + 04_modules/module_definitions.csv
suppressPackageStartupMessages(library(GSVA))
expr <- as.matrix(read.csv("YOUR_MATRIX.csv", row.names=1, check.names=FALSE))   # genes x samples
genes <- read.csv("04_modules/module_definitions.csv")
my_set <- list(MY_MODULE = c("EGFR","ERBB2","ERBB3","AREG","HBEGF"))              # replace with your own set
# keep the frozen definition for the same module to compare
frozen <- unique(toupper(genes$gene[genes$module == "ERBB_RECEPTORS"]))
sets <- list(MY_MODULE = intersect(my_set$MY_MODULE, rownames(expr)),
             FROZEN_ERBB_RECEPTORS = intersect(frozen, rownames(expr)))
print(sapply(sets, length))                       # expect: how many members are actually present
sc <- GSVA::gsva(GSVA::gsvaParam(expr, sets, minSize=3, kcdf="Gaussian"), verbose=FALSE)
sc_z <- t(scale(t(sc)))
write.csv(as.data.frame(t(sc_z)), "expected_output/example1_module_scores.csv")
cat("example 1 done: scores written for", nrow(sc),"module(s)\\n")
"""
ex2 = """#!/usr/bin/env Rscript
# Reuse example 2: recompute the composition comparison under an alternative scheme.
# Reads the shipped per-cohort data, fits base and adjusted models, and writes the comparison table.
library(dplyr)
d <- read.csv("07_estimates/per_cohort_effects.csv")     # includes beta_base / beta_adj / sd_ref
res <- d %>% filter(is.finite(beta_base), is.finite(beta_adj)) %>%
  group_by(disease, feature) %>%
  summarise(median_base = median(beta_base), median_adjusted = median(beta_adj),
            ratio = median(abs(beta_adj))/median(abs(beta_base)), .groups="drop") %>%
  mutate(attenuation = 1 - ratio)
write.csv(res, "expected_output/example2_composition_ratio.csv", row.names=FALSE)
cat("example 2 done: median adjusted/base ratio =", round(median(res$ratio, na.rm=TRUE),3), "\\n")
"""
os.makedirs(os.path.join(P,"09_reuse_examples","expected_output"), exist_ok=True)
open(os.path.join(P,"09_reuse_examples","example1_replace_module_gene_set.R"),"w",encoding="utf-8").write(ex1)
open(os.path.join(P,"09_reuse_examples","example2_recompute_composition_scheme.R"),"w",encoding="utf-8").write(ex2)
open(os.path.join(P,"09_reuse_examples","README_examples.md"),"w",encoding="utf-8").write(
 "# Reuse examples\n\nRun from the dataset package root so that relative paths resolve.\n\n"
 "1. `example1_replace_module_gene_set.R` — swap in your own gene set, re-score one cohort, and compare with the frozen definition; prints how many members are actually present per set (coverage awareness).\n"
 "2. `example2_recompute_composition_scheme.R` — recompute the base-versus-adjusted comparison from the shipped estimates and report the median adjusted/base coefficient ratio.\n\n"
 "Both examples write to `expected_output/`. If a file is missing, the example did not complete.\n")
# 10 environment
try:
    rver=subprocess.run(["Rscript","-e","cat(R.version.string)"],capture_output=True,text=True,timeout=120).stdout.strip()
except Exception: rver="R version not captured"
pk=subprocess.run(["Rscript","-e","cat(paste(sapply(c('GSVA','metafor','survival','dplyr','ggplot2'), function(p) paste0(p,':',as.character(packageVersion(p)))), collapse='\\n'))"],capture_output=True,text=True,timeout=180).stdout
import sys
open(os.path.join(P,"10_environment","environment.txt"),"w",encoding="utf-8").write(
 f"{rver}\n{pk}\npython: {sys.version.split()[0]}\n")
open(os.path.join(P,"10_environment","run_order.md"),"w",encoding="utf-8").write(
 "# Run order\n\n"
 "1. `07_estimates/per_cohort_effects.csv` — per-cohort effects (SMDH / SMCRPH), produced by scripts 10_v11_effects_two_model.R\n"
 "2. `07_estimates/meta_*.csv` — meta-analytic summaries (REML/Knapp-Hartung primary; DerSimonian-Laird, ad hoc Knapp-Hartung and unpaired-only as sensitivity)\n"
 "3. `07_estimates/composition_model_summary.csv` — base-versus-adjusted composition models\n"
 "4. `06_single_cell/single_cell_comparisons.csv` — donor-aware single-cell contrasts\n"
 "5. `08_qc/*` — coverage, exclusions and layout checks\n")
print("package assembled")
for d in sorted(os.listdir(P)):
    if os.path.isdir(os.path.join(P,d)): print(" ",d,len(os.listdir(os.path.join(P,d))))
