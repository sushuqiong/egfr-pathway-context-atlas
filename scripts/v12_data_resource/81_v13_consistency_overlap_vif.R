#!/usr/bin/env Rscript
# v13: (A) cross-cohort/cross-platform consistency of module effects + coverage-threshold sensitivity
#      (B) signature-overlap audit between module gene sets and xCell compartment signatures
#      (C) per-predictor VIF within the disease-status model (to reconcile R2 and VIF reporting)
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(xCell); library(metafor)})
V13 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v13"
R   <- file.path(V13,"results")
PK  <- file.path(V13,"dataset_package")
pc  <- read.csv(file.path(R,"v13_percohort_effects_complete.csv"), stringsAsFactors=FALSE)
cov <- read.csv(file.path(PK,"04_modules","platform_module_coverage.csv"), stringsAsFactors=FALSE)
## ---- (A) consistency of effects across cohorts within a context -------------------------------
est <- pc %>% filter(measure %in% c("SMDH","SMCRPH"), is.finite(yi))
con <- est %>% group_by(disease, feature) %>%
  summarise(k=n(), n_pos=sum(yi>0), n_neg=sum(yi<0), frac_majority=max(sum(yi>0),sum(yi<0))/n(),
            median_yi=median(yi), I2=NA_real_, .groups="drop") %>%
  mutate(direction_consistent = n_pos==0 | n_neg==0,
         concordance = frac_majority)
write.csv(con, file.path(R,"v13_qc_cross_cohort_consistency.csv"), row.names=FALSE)
cat("== cross-cohort direction consistency (k>=2) ==\n")
cat("context-module pairs with k>=2:", sum(con$k>=2), "| all cohorts same sign:", sum(con$direction_consistent & con$k>=2),
    sprintf("(%.0f%%)\n", 100*sum(con$direction_consistent & con$k>=2)/sum(con$k>=2)))
print(con %>% filter(k>=2) %>% group_by(disease) %>%
      summarise(pairs=n(), same_sign=sum(direction_consistent), median_concordance=round(median(concordance),3), .groups="drop") %>%
      as.data.frame(), row.names=FALSE)
## ---- (A2) coverage-threshold sensitivity: re-pool excluding low-coverage cohort-module pairs
cov$coverage <- as.numeric(cov$coverage)
cv <- cov[,c("accession","module","coverage")]; names(cv) <- c("accession","feature","coverage")
est2 <- est %>% left_join(cv, by=c("accession","feature"))
pool <- function(d, tag) {
  out <- list()
  for (key in split(d, list(d$disease, d$feature), drop=TRUE)) {
    if (nrow(key)<2) next
    m <- tryCatch(rma.uni(yi, vi, data=key, method="REML", test="knha"), error=function(e) NULL); if (is.null(m)) next
    out[[length(out)+1]] <- data.frame(disease=key$disease[1], feature=key$feature[1], k=nrow(key),
      est=as.numeric(m$beta), p=m$pval, fdr=NA_real_, stringsAsFactors=FALSE)
  }
  r <- bind_rows(out)
  if (nrow(r)) for (dis in unique(r$disease)) { ix <- r$disease==dis; if (any(ix)) r$fdr[ix] <- p.adjust(r$p[ix],"BH") }
  r$scenario <- tag
  cat(sprintf("[%s] k>=2: %d | BH<0.05: %d\n", tag, nrow(r), sum(r$fdr<0.05, na.rm=TRUE)))
  r
}
cat("\n== coverage-threshold sensitivity ==\n")
sc <- bind_rows(pool(est2, "all cohorts"),
                pool(est2 %>% filter(coverage>=0.6), "coverage >= 0.60"),
                pool(est2 %>% filter(coverage>=0.8), "coverage >= 0.80"),
                pool(est2 %>% filter(coverage>=0.9), "coverage >= 0.90"))
write.csv(sc, file.path(R,"v13_qc_coverage_threshold_sensitivity.csv"), row.names=FALSE)
## ---- (B) signature overlap: module members vs xCell compartment signatures --------------------
gs <- read.csv(file.path(PK,"04_modules","module_definitions.csv"), stringsAsFactors=FALSE)
sets <- lapply(split(toupper(gs$gene), gs$module), unique)
xgenes <- toupper(xCell::xCell.data$genes)
comps <- list(epi="Epithelial cells", fib="Fibroblasts", end="Endothelial cells", imm="ImmuneScore")
sig <- list()
for (m in names(sets)) sig[[length(sig)+1]] <- data.frame(module=m, members=length(sets[[m]]),
  overlap_xcell_genes=length(intersect(sets[[m]], xgenes)),
  frac_overlap_xcell=round(length(intersect(sets[[m]], xgenes))/length(sets[[m]]),3), stringsAsFactors=FALSE)
sig <- bind_rows(sig)
# xCell signature rows are deconvolved cell types; use the compartment aggregate membership (all rows)
xt <- rownames(xCell::xCell.data$spill$K)
sig$compartment_scores_using_overlapping_genes <- NA_character_
sig$note <- "xCell derives all compartment scores from its 489-gene signature panel; overlap with module members creates a shared input between score and covariate"
write.csv(sig, file.path(R,"v13_qc_signature_overlap.csv"), row.names=FALSE)
cat("\n== signature overlap (module members vs xCell panel) ==\n")
print(sig %>% arrange(desc(frac_overlap_xcell)) %>% head(8) %>% as.data.frame(), row.names=FALSE)
cat("modules with >20% of members inside the xCell panel:", sum(sig$frac_overlap_xcell>0.2), "of", nrow(sig), "\n")
cat("max overlap fraction:", max(sig$frac_overlap_xcell), "\n")
## ---- (C) VIF within the disease-status model --------------------------------------------------
A <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
cf <- read.csv(file.path(A,"xcell","xcell_composition_scores.csv"), stringsAsFactors=FALSE)
key <- read.csv(file.path(V13,"dataset_package","05_composition","composition_scores_per_sample.csv"), stringsAsFactors=FALSE)
key$case <- as.integer(key$group %in% c("Case"))
viftab <- list()
for (acc in unique(key$accession)) {
  s <- key[key$accession==acc, c("case","epi","fib","end","imm")]; s <- s[complete.cases(s),]
  if (nrow(s)<15 || length(unique(s$case))<2) next
  m <- lm(case ~ epi + fib + end + imm, data=s)
  overall <- summary(m)$r.squared
  v <- sapply(c("epi","fib","end","imm"), function(p) {
    f <- as.formula(paste(p,"~",paste(setdiff(c("epi","fib","end","imm"),p), collapse="+")))
    1/(1-summary(lm(f, data=s))$r.squared)
  })
  viftab[[length(viftab)+1]] <- data.frame(accession=acc, n=nrow(s), r2_overall=overall,
     max_vif_predictor=round(max(v),2), vif_epi=round(v["epi"],2), vif_fib=round(v["fib"],2),
     vif_end=round(v["end"],2), vif_imm=round(v["imm"],2), stringsAsFactors=FALSE)
}
V <- bind_rows(viftab)
write.csv(V, file.path(R,"v13_qc_vif_by_predictor.csv"), row.names=FALSE)
cat("\n== VIF within the disease-status model ==\n")
cat(sprintf("cohorts: %d | overall model R2 median %.3f max %.3f | max per-predictor VIF median %.2f max %.2f\n",
   nrow(V), median(V$r2_overall), max(V$r2_overall), median(V$max_vif_predictor), max(V$max_vif_predictor)))
cat("note: overall model R2 measures how well the four scores jointly explain disease status; per-predictor VIF measures\n",
    "collinearity among the scores themselves. A high overall R2 with modest VIF means the model as a whole predicts\n",
    "case status well without the individual covariates being redundant.\n")
print(V %>% arrange(desc(r2_overall)) %>% head(5) %>% as.data.frame(), row.names=FALSE)
