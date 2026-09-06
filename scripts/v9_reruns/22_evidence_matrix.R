#!/usr/bin/env Rscript
# v9 stage2b: per-state evidence matrix
suppressPackageStartupMessages({library(dplyr); library(tidyr)})
A <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
V <- "C:/Users/fengq/Desktop/EGFR/EGFR的v9/reruns/results"
E <- "C:/Users/fengq/Desktop/EGFR/EGFR_external_validation/results"
raw <- read.csv(file.path(A,"context_atlas_summary.csv"), stringsAsFactors=FALSE)
xc  <- read.csv(file.path(A,"xcell/context_atlas_summary_xcell_adjusted.csv"), stringsAsFactors=FALSE)
meta<- read.csv(file.path(V,"context_meta_v9_unified.csv"), stringsAsFactors=FALSE)
joint<-read.csv(file.path(V,"v9_composition_joint_summary.csv"), stringsAsFactors=FALSE)
sc  <- read.csv(file.path(A,"sc_top_hit_cell_source_validation.csv"), stringsAsFactors=FALSE)
sv  <- read.csv(file.path(A,"cbio_v3_survival_cox.csv"), stringsAsFactors=FALSE)
base <- raw %>% select(disease, feature, n_cohorts, robust_consistent, n_fdr_raw, median_smd, composition_robust, direction_preserved)
m <- merge(base, xc %>% select(disease, feature, robust_xcell), by=c("disease","feature"), all.x=TRUE)
m <- merge(m, meta %>% select(disease, feature, k, smd_DL, p_DL, fdr_DL, smd_REML, p_REML_HK, fdr_REML_HK, ci_lo, ci_hi, I2), by=c("disease","feature"), all.x=TRUE)
m <- merge(m, joint %>% select(disease, feature, n, n_fdr_joint, median_d_adj, joint_robust), by=c("disease","feature"), all.x=TRUE)
# single-cell: any FDR<0.05 hit within disease+module
sc2 <- sc %>% filter(fdr<0.05) %>% group_by(context, module) %>%
  summarise(sc_n_hits=n(), sc_celltypes=paste(unique(cell_type), collapse="; "), .groups="drop") %>%
  rename(disease=context, feature=module)
m <- merge(m, sc2, by=c("disease","feature"), all.x=TRUE)
# TCGA prognosis (min fdr per context+feature)
sv$fdr <- suppressWarnings(as.numeric(sv$fdr)); sv$hazard_ratio_per_1sd <- suppressWarnings(as.numeric(sv$hazard_ratio_per_1sd))
svs <- sv %>% group_by(context, feature) %>% summarise(tcga_hr=first(hazard_ratio_per_1sd), tcga_fdr=first(fdr), .groups="drop") %>% rename(disease=context)
m <- merge(m, svs, by=c("disease","feature"), all.x=TRUE)
# external: CRC/PAAD/STAD statuses
extr <- read.csv(file.path(E,"external_crc_gse39582_refined.csv"), stringsAsFactors=FALSE) %>% filter(model=="age") %>% transmute(disease="CRC", feature=feature, ext_hr=HR, ext_p=p, ext_status=ifelse(p<0.05,"replicated","not"), ext_note="GSE39582 age-adj")
extp <- read.csv(file.path(E,"external_paad_gse21501_module_os.csv"), stringsAsFactors=FALSE) %>% transmute(disease="PAAD", feature=feature, ext_hr=HR, ext_p=p, ext_status=ifelse(p<0.05,"nominal-only","not"), ext_note="GSE21501")
exts <- read.csv(file.path(E,"external_stad_acrg_module_os.csv"), stringsAsFactors=FALSE) %>% filter(feature %in% c("TIE_ANGPT_AXIS","PDGFR_KIT_CSF1R","VEGF_PDGF_AXIS","RET_ALK_NTRK","TAM_AXL_AXIS","FGFR_AXIS")) %>% transmute(disease="STAD", feature=feature, ext_hr=HR, ext_p=p, ext_status=ifelse(p<0.05,"replicated","not"), ext_note="ACRG")
ext <- bind_rows(extr, extp, exts)
m <- merge(m, ext, by=c("disease","feature"), all.x=TRUE)
# evidence tier summary flags
m <- m %>% mutate(meta_sig_REMLHK = !is.na(fdr_REML_HK) & fdr_REML_HK<0.05,
                  tier = case_when(
                    is.na(median_d_adj) ~ "no data",
                    robust_consistent & joint_robust ~ "robust+joint",
                    joint_robust ~ "joint-robust",
                    robust_consistent ~ "per-cohort only",
                    composition_robust ~ "marker-adj only",
                    n_fdr_raw>=1 | !is.na(sc_n_hits) ~ "weak/partial",
                    TRUE ~ "null/uncertain"))
write.csv(m, "C:/Users/fengq/Desktop/EGFR/EGFR的v9/03_表格与补充数据/TableS9_evidence_matrix_v9.csv", row.names=FALSE)
cat("rows:", nrow(m), "\n")
cat("joint-robust:", sum(m$joint_robust, na.rm=TRUE), " xcell-robust:", sum(m$robust_xcell, na.rm=TRUE), " overlap:", sum(m$joint_robust & m$robust_xcell, na.rm=TRUE), "\n")
cat("REML/HK meta sig:", sum(m$meta_sig_REMLHK, na.rm=TRUE), "\n")
cat("tier counts:\n"); print(table(m$tier))
cat("\nStates with joint_robust OR (meta sig & sc hit):\n")
fl <- m %>% filter(joint_robust | meta_sig_REMLHK) %>% select(disease, feature, robust_consistent, median_smd, median_d_adj, n_fdr_joint, joint_robust, robust_xcell, meta_sig_REMLHK, sc_celltypes)
print(fl, row.names=FALSE)
