#!/usr/bin/env Rscript
# v10 evidence matrix + full lists
suppressPackageStartupMessages({library(dplyr); library(tidyr)})
A <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
V <- "C:/Users/fengq/Desktop/EGFR/EGFR的v10/reruns/results"
E <- "C:/Users/fengq/Desktop/EGFR/EGFR_external_validation/results"
raw <- read.csv(file.path(A,"context_atlas_summary.csv"), stringsAsFactors=FALSE)
xc  <- read.csv(file.path(A,"xcell/context_atlas_summary_xcell_adjusted.csv"), stringsAsFactors=FALSE)
meta<- read.csv(file.path(V,"v10_meta_empirical_ri.csv"), stringsAsFactors=FALSE)
joint<-read.csv(file.path(V,"v10_joint_summary.csv"), stringsAsFactors=FALSE)
sc  <- read.csv(file.path(A,"sc_top_hit_cell_source_validation.csv"), stringsAsFactors=FALSE)
sv  <- read.csv(file.path(A,"cbio_v3_survival_cox.csv"), stringsAsFactors=FALSE)
crc <- read.csv(file.path(V,"v10_external_crc_gse39582.csv"), stringsAsFactors=FALSE)
m <- raw %>% select(disease, feature, n_cohorts, robust_consistent, n_fdr_raw, median_smd, composition_robust, direction_preserved)
m <- merge(m, xc %>% select(disease, feature, robust_xcell), by=c("disease","feature"), all.x=TRUE)
m <- merge(m, meta %>% select(disease, feature, k, est_REML, p_REML_KHNA, fdr, est_DL, p_DL, ci_lo, ci_hi, I2),
           by=c("disease","feature"), all.x=TRUE)
m <- merge(m, joint %>% select(disease, feature, n_analysed, n_fdr, median_d_adj, joint_robust, status),
           by=c("disease","feature"), all.x=TRUE)
sc2 <- sc %>% filter(fdr<0.05) %>% group_by(context, module) %>% summarise(sc_hits=n(),
        sc_celltypes=paste(unique(cell_type), collapse="; "), .groups="drop") %>% rename(disease=context, feature=module)
m <- merge(m, sc2, by=c("disease","feature"), all.x=TRUE)
svs <- sv %>% group_by(context, feature) %>% summarise(tcga_hr=first(hazard_ratio_per_1sd), tcga_fdr=first(fdr), .groups="drop") %>% rename(disease=context)
m <- merge(m, svs, by=c("disease","feature"), all.x=TRUE)
crcs <- crc %>% filter(model=="age+stage") %>% transmute(disease="CRC", feature=feature, ext_hr=HR, ext_lo=lo, ext_hi=hi, ext_p=p, ext_fdr=fdr)
m <- merge(m, crcs, by=c("disease","feature"), all.x=TRUE)
write.csv(m, file.path(V,"v10_evidence_matrix.csv"), row.names=FALSE)
cat("matrix rows:", nrow(m), "\n")
cat("\n== meta REML/Knha significant (k>=2) ==\n")
print(meta[meta$k>=2 & meta$fdr<0.05, c("disease","feature","k","est_REML","ci_lo","ci_hi","p_REML_KHNA","fdr","est_DL")], row.names=FALSE, digits=3)
cat("\n== joint robust (21) ==\n")
print(joint[joint$joint_robust %in% TRUE, c("disease","feature","n_analysed","n_fdr","median_d_adj")], row.names=FALSE, digits=3)
cat("\n== status table ==\n"); print(table(joint$status))
cat("\n== CRC external (age+stage) key ==\n")
print(crc[crc$model=="age+stage" & crc$feature %in% c("VEGF_PDGF_AXIS","FGFR_AXIS","IGF_INSR_AXIS","ERBB_LIGANDS","WNT_CTNNB1","EPH_RECEPTORS"),c("feature","n","events","HR","lo","hi","p","fdr")], row.names=FALSE, digits=3)
