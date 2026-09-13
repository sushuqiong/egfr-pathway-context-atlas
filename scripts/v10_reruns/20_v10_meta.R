#!/usr/bin/env Rscript
# v10 RERUN B: metafor-based pooling (REML/Knha, DL), rho sensitivity, joint summary with per-layer inclusion
suppressPackageStartupMessages({library(metafor); library(dplyr)})
V10 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v10/reruns/results"
df <- read.csv(file.path(V10,"v10_percohort_effects_joint.csv"), stringsAsFactors=FALSE)
cat("rows total:", nrow(df), " cohorts:", length(unique(df$accession)), "\n")

## ---------- Layer 1: meta-analysis (effect-level inclusion) ----------
runmeta <- function(d, tag){
  d <- d[d$role %in% c("discovery","validation") & is.finite(d$yi) & is.finite(d$vi) & d$vi>0, ]
  rows <- list()
  for (key in split(d, list(d$disease, d$feature), drop=TRUE)) {
    if(nrow(key)==0) next
    k <- nrow(key)
    m_re <- tryCatch(rma.uni(yi, vi, data=key, method="REML", test="knha"), error=function(e) NULL)
    m_dl <- tryCatch(rma.uni(yi, vi, data=key, method="DL"), error=function(e) NULL)
    if(is.null(m_re)) next
    rows[[length(rows)+1]] <- data.frame(disease=key$disease[1], feature=key$feature[1], k=k,
      est_REML=as.numeric(m_re$beta), se_REML=m_re$se, p_REML_KHNA=m_re$pval,
      ci_lo=m_re$ci.lb, ci_hi=m_re$ci.ub, I2=m_re$I2, tau2=m_re$tau2,
      est_DL=if(is.null(m_dl)) NA else as.numeric(m_dl$beta), p_DL=if(is.null(m_dl)) NA else m_dl$pval,
      cohorts=paste(key$accession, collapse=";"), n_case=sum(key$n_case), n_control=sum(key$n_control))
  }
  res <- bind_rows(rows); res$fdr <- NA_real_
  for (dis in unique(res$disease)) { ix <- res$disease==dis & res$k>=2 & is.finite(res$p_REML_KHNA)
    if(sum(ix)) res$fdr[ix] <- p.adjust(res$p_REML_KHNA[ix], "BH") }
  write.csv(res, file.path(V10, sprintf("v10_meta_%s.csv", tag)), row.names=FALSE)
  cat(sprintf("== meta [%s] REML/Knha sig(k>=2): %d ; DL sig: %d\n", tag,
      sum(res$k>=2 & res$fdr<0.05, na.rm=TRUE), sum(res$k>=2 & res$p_DL<0.05, na.rm=TRUE)))
  res
}
mEmp <- runmeta(df, "empirical_ri")
sig_list <- mEmp[mEmp$k>=2 & mEmp$fdr<0.05, c("disease","feature","k","est_REML","ci_lo","ci_hi")]
print(sig_list, row.names=FALSE, digits=3)
# rho sensitivity: rebuild paired yi/vi at fixed rho
for (rho in c(0.5,0.7)) {
  d <- df
  ix <- d$paired & is.finite(d$npair) & is.finite(d$mean_case)
  d$yi[ix] <- NA; d$vi[ix] <- NA
  if(any(ix)){
    es <- metafor::escalc(measure="SMCRH", m1i=d$mean_case[ix], m2i=d$mean_ctrl[ix],
                          sd1i=d$sd_case[ix], sd2i=d$sd_ctrl[ix], ri=rho, ni=d$npair[ix])
    d$yi[ix] <- as.numeric(es$yi); d$vi[ix] <- as.numeric(es$vi)
  }
  runmeta(d, sprintf("rho%.1f", rho))
}

## ---------- Layer 2: joint models (independent inclusion: finite p_adj) ----------
dj <- df[is.finite(df$p_adj), ]
dj$fdr_joint <- NA_real_
for (acc in unique(dj$accession)) { ix <- dj$accession==acc
  if(sum(ix)) dj$fdr_joint[ix] <- p.adjust(dj$p_adj[ix], "BH") }
sm <- dj %>% group_by(disease, feature) %>% summarise(
  n_analysed=n(), n_fdr=sum(fdr_joint<0.05, na.rm=TRUE), pos=sum(d_adj>0, na.rm=TRUE),
  neg=sum(d_adj<0, na.rm=TRUE), median_d_adj=median(d_adj, na.rm=TRUE), .groups="drop") %>%
  mutate(majority=pmax(pos,neg),
         joint_robust = n_fdr>=2 & (majority/n_analysed >= ifelse(n_analysed==2,1,2/3)))
# status classification incl cohorts attempted but not estimable
attempt <- df %>% group_by(disease, feature) %>% summarise(n_rows=n(), n_est=sum(is.finite(p_adj)), .groups="drop")
sm <- sm %>% full_join(attempt, by=c("disease","feature")) %>%
  mutate(status = case_when(is.na(n_analysed) & n_est==0 ~ "not analysed",
                            !is.na(n_analysed) & n_analysed < n_rows ~ "partly estimable",
                            !is.na(n_analysed) & n_fdr==0 ~ "estimated, not significant",
                            joint_robust ~ "robust", TRUE ~ "estimated"))
write.csv(sm, file.path(V10,"v10_joint_summary.csv"), row.names=FALSE)
cat("== joint (independent inclusion) robust states:", sum(sm$joint_robust, na.rm=TRUE), "\n")
print(table(sm$status))
print(sm[sm$joint_robust %in% TRUE, c("disease","feature","n_analysed","n_fdr","median_d_adj")], row.names=FALSE, digits=3)
cat("joint robust by disease:", paste(names(table(sm$disease[sm$joint_robust %in% TRUE])),
    table(sm$disease[sm$joint_robust %in% TRUE]), collapse=" | "), "\n")
