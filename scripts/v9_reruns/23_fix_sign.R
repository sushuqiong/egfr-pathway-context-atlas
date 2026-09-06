#!/usr/bin/env Rscript
# fix sign convention: lm coef was Control-Case; d_adj must be Case-Control
suppressPackageStartupMessages({library(dplyr)})
V9 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v9/reruns/results"
sm <- read.csv(file.path(V9,"v9_composition_joint_summary.csv"), stringsAsFactors=FALSE)
tmp <- sm$pos_joint; sm$pos_joint <- sm$neg_joint; sm$neg_joint <- tmp
sm$median_d_adj <- -sm$median_d_adj
sm$majority <- pmax(sm$pos_joint, sm$neg_joint)
sm$joint_robust <- sm$n_fdr_joint>=2 & (sm$majority/sm$n >= ifelse(sm$n==2,1,2/3))
write.csv(sm, file.path(V9,"v9_composition_joint_summary.csv"), row.names=FALSE)
# also fix per-cohort d_adj sign in raw file for downstream
d <- read.csv(file.path(V9,"v9_percohort_joint_unified.csv"), stringsAsFactors=FALSE)
d$d_adj <- -d$d_adj
write.csv(d, file.path(V9,"v9_percohort_joint_unified.csv"), row.names=FALSE)
cat("fixed. joint-robust:", sum(sm$joint_robust), "\n")
print(sm[sm$joint_robust, c("disease","feature","n_fdr_joint","median_d_adj","pos_joint","neg_joint")], row.names=FALSE)
