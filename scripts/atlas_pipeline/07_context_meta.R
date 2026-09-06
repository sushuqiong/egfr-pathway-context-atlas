#!/usr/bin/env Rscript
# Context-internal random-effects meta-analysis (DerSimonian-Laird) of module SMDs
# across discovery+validation cohorts per disease context. Inputs: module_effects_raw.csv,
# per-cohort case/control counts from the three projects' group-count CSVs.
# SMD variance: unpaired = (n1+n0)/(n1 n0) + g^2/(2(n1+n0)); paired mean-change = 1/np + d^2/(2 np)
# (assumes within-pair correlation 0.5; sensitivity note in output doc).
suppressPackageStartupMessages({library(dplyr)})
ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
RES <- file.path(ROOT, "results")
rd <- function(f, ...) read.csv(f, stringsAsFactors=FALSE, check.names=FALSE, ...)

eff <- rd(file.path(RES, "module_effects_raw.csv"))
# cohort counts: case/control per accession (consolidated from three projects)
count_files <- c(
 "C:/Users/fengq/Desktop/EGFR胃癌/EGFR_ERBB_context_project_v1/results/bulk_sample_group_counts.csv",
 "C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/results/bulk_sample_group_counts.csv",
 "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/results/bulk_sample_group_counts.csv")
cnt <- list()
for (f in count_files) if (file.exists(f)) cnt[[length(cnt)+1]] <- rd(f)
cnt <- do.call(rbind, cnt)
# counts for Case/Control (Responder rows ignored here)
case_n <- cnt %>% filter(group=="Case") %>% select(accession, n_case=n)
ctrl_n <- cnt %>% filter(group=="Control") %>% select(accession, n_control=n)
census <- merge(case_n, ctrl_n, by="accession", all=TRUE)

paired_acc <- c("GSE32863","GSE19804","GSE10072","GSE44076","GSE27342","GSE63089",
                "GSE15471","GSE28735","GSE62452","GSE57957","GSE23400","GSE20347")

eff <- eff %>% filter(role %in% c("discovery","validation")) %>%
  left_join(census, by="accession") %>% filter(is.finite(smd) & is.finite(n_case) & n_case>1)
eff$paired <- eff$accession %in% paired_acc
eff$np <- ifelse(eff$paired, eff$n_case, NA)
eff$var <- ifelse(eff$paired,
                  1/eff$np + eff$smd^2/(2*eff$np),
                  (eff$n_case+eff$n_control)/(eff$n_case*eff$n_control) + eff$smd^2/(2*(eff$n_case+eff$n_control)))

meta_rows <- list()
for (dis in unique(eff$disease)) {
  sub <- eff[eff$disease==dis, ]
  for (f in unique(sub$feature)) {
    d <- sub[sub$feature==f, ]
    d <- d[is.finite(d$var) & d$var>0, ]
    if (nrow(d) < 1) next
    y <- d$smd; v <- d$var; k <- nrow(d)
    w <- 1/v
    FE <- sum(w*y)/sum(w)
    Q <- sum(w*(y-FE)^2); dfQ <- max(k-1, 1)
    C <- sum(w) - sum(w^2)/sum(w)
    tau2 <- max(0, (Q-dfQ)/C)
    ws <- 1/(v+tau2)
    RE <- sum(ws*y)/sum(ws)
    se_re <- sqrt(1/sum(ws))
    z <- RE/se_re; p <- 2*pnorm(-abs(z))
    I2 <- 100*max(0, (Q-dfQ)/Q)
    meta_rows[[length(meta_rows)+1]] <- data.frame(
      disease=dis, feature=f, k=k, n_case=sum(d$n_case), n_control=sum(d$n_control),
      smd_min=min(y), smd_max=max(y), direction_consistency=max(sum(y>0), sum(y<0))/k,
      smd_FE=FE, smd_RE=RE, se_RE=se_re, ci_low=RE-1.96*se_re, ci_high=RE+1.96*se_re,
      p_RE=p, Q=Q, I2=I2, tau2=tau2, accession=paste(d$accession, collapse=";"), stringsAsFactors=FALSE)
  }
}
meta <- bind_rows(meta_rows)
meta$fdr_RE <- ave(meta$p_RE, meta$disease, FUN=function(x) p.adjust(x, "BH"))
meta <- meta[order(meta$disease, meta$fdr_RE), ]
write.csv(meta, file.path(RES, "context_meta_summary.csv"), row.names=FALSE)
cat("meta rows:", nrow(meta), "\n")
sig <- meta[meta$fdr_RE < 0.05, ]
cat("meta-significant (per-disease BH<0.05):", nrow(sig), "\n")
print(table(sig$disease))
# consistency with previous robust set
at <- rd(file.path(RES, "context_atlas_summary.csv"))
prev <- at %>% filter(robust_consistent=="TRUE") %>% select(disease, feature)
ov <- merge(prev, sig[, c("disease","feature","smd_RE","fdr_RE")], by=c("disease","feature"))
cat("overlap with previous 55 robust:", nrow(ov), "\n")
new <- sig[!duplicated(paste(sig$disease, sig$feature)) & !paste(sig$disease, sig$feature) %in% paste(prev$disease, prev$feature), ]
cat("newly meta-significant (not in previous robust):", nrow(new), "\n")
if (nrow(new)) print(new[, c("disease","feature","smd_RE","fdr_RE","k")])
