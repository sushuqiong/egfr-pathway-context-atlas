#!/usr/bin/env Rscript
# v11 RERUN B: meta-analysis on the common-denominator effects (SMDH / SMCRPH) + joint summary
suppressPackageStartupMessages({library(metafor); library(dplyr)})
V <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/reruns/results"
df <- read.csv(file.path(V,"v11_percohort_effects.csv"), stringsAsFactors=FALSE)
pool <- function(d, tag, method="REML", test="knha", note=""){
  d <- d[is.finite(d$yi) & is.finite(d$vi) & d$vi>0, ]
  rows <- list()
  for (key in split(d, list(d$disease, d$feature), drop=TRUE)) {
    if(nrow(key)<1) next
    m <- tryCatch(rma.uni(yi, vi, data=key, method=method, test=test), error=function(e) NULL)
    if(is.null(m)) next
    rows[[length(rows)+1]] <- data.frame(disease=key$disease[1], feature=key$feature[1], k=nrow(key),
      est=as.numeric(m$beta), se=m$se, p=m$pval, ci_lo=m$ci.lb, ci_hi=m$ci.ub, I2=m$I2, tau2=m$tau2,
      measures=paste(names(table(key$measure)), table(key$measure), collapse="|"),
      cohorts=paste(key$accession, collapse=";"), note=note, stringsAsFactors=FALSE)
  }
  res <- bind_rows(rows); res$fdr <- NA_real_
  for (dis in unique(res$disease)) { ix <- res$disease==dis & res$k>=2 & is.finite(res$p)
    if(sum(ix)) res$fdr[ix] <- p.adjust(res$p[ix], "BH") }
  write.csv(res, file.path(V, sprintf("v11_meta_%s.csv", tag)), row.names=FALSE)
  cat(sprintf("[%s] k>=2 states: %d ; BH-significant: %d\n", tag, sum(res$k>=2), sum(res$k>=2 & res$fdr<0.05, na.rm=TRUE)))
  res
}
cat("== primary: REML + Hartung-Knapp (common denominator) ==\n")
m1 <- pool(df, "primary_reml_knha")
print(m1[m1$k>=2 & m1$fdr<0.05, c("disease","feature","k","est","ci_lo","ci_hi","p","fdr","I2","measures")], row.names=FALSE, digits=3)
cat("\n== sensitivity: DerSimonian-Laird ==\n");      pool(df, "DL", method="DL", test="z")
cat("\n== sensitivity: REML + ad hoc Knapp-Hartung (non-shrinking SE) ==\n"); pool(df, "adhoc", test="adhoc")
cat("\n== sensitivity: unpaired cohorts only (SMDH) ==\n")
pool(df[!df$paired,], "unpaired_only")
cat("\n== sensitivity: fixed rho for paired cohorts ==\n")
for (rho in c(0.5,0.7)) {
  d <- df
  ix <- d$paired & is.finite(d$npair) & is.finite(d$mean_case)
  es <- metafor::escalc(measure="SMCRPH", m1i=d$mean_case[ix], m2i=d$mean_ctrl[ix], sd1i=d$sd_case[ix], sd2i=d$sd_ctrl[ix], ri=rho, ni=d$npair[ix])
  d$yi[ix] <- as.numeric(es$yi); d$vi[ix] <- as.numeric(es$vi)
  pool(d, sprintf("rho%.1f", rho))
}
## joint summary (independent inclusion: finite p_adj), BH within cohort, four status classes
dj <- df[is.finite(df$p_adj), ]; dj$fdr_joint <- NA_real_
for (acc in unique(dj$accession)) { ix <- dj$accession==acc; dj$fdr_joint[ix] <- p.adjust(dj$p_adj[ix], "BH") }
sm <- dj %>% group_by(disease, feature) %>% summarise(n_analysed=n(), n_fdr=sum(fdr_joint<0.05), pos=sum(d_adj>0), neg=sum(d_adj<0),
      median_d_adj=median(d_adj), median_beta_base=median(beta_base), median_beta_adj=median(beta_adj), .groups="drop") %>%
  mutate(majority=pmax(pos,neg), joint_robust = n_fdr>=2 & (majority/n_analysed >= ifelse(n_analysed==2,1,2/3)))
attempt <- df %>% group_by(disease, feature) %>% summarise(n_rows=n(), n_est=sum(is.finite(p_adj)), .groups="drop")
sm <- sm %>% full_join(attempt, by=c("disease","feature")) %>%
  mutate(status = case_when(is.na(n_analysed) & n_est==0 ~ "not analysed",
                            !is.na(n_analysed) & n_analysed < n_rows ~ "partly estimable",
                            !is.na(n_analysed) & n_fdr==0 ~ "estimated, not significant",
                            joint_robust ~ "robust", TRUE ~ "estimated"))
write.csv(sm, file.path(V,"v11_joint_summary.csv"), row.names=FALSE)
cat("\n== joint (two-model, independent inclusion) ==\n")
cat("robust:", sum(sm$joint_robust, na.rm=TRUE), "\n"); print(table(sm$status))
print(sm[sm$joint_robust %in% TRUE, c("disease","feature","n_analysed","n_fdr","median_d_adj")], row.names=FALSE, digits=3)
cat("robust by disease:", paste(names(table(sm$disease[sm$joint_robust %in% TRUE])), table(sm$disease[sm$joint_robust %in% TRUE]), collapse=" | "), "\n")
