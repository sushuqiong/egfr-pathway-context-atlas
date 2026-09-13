#!/usr/bin/env Rscript
# v10 RERUN A: corrected per-cohort effects (metafor escalc SMD/SMCRH) + joint composition models
# Fixes: (1) paired indexing bug -> explicit subsetting + metafor SMCRH with empirical ri
#        (2) explicit sample-ID joining of expression and xCell composition
#        (3) explicit Control reference level (no post-hoc sign flipping)
suppressPackageStartupMessages({library(GSVA); library(metafor); library(dplyr)})
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
V10 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v10/reruns/results"
dir.create(V10, recursive=TRUE, showWarnings=FALSE)
cohorts <- data.frame(
 accession=c("GSE32863","GSE19804","GSE10072","GSE44076","GSE41258","GSE23878","GSE75214","GSE87473",
   "GSE179285","GSE4302","GSE43696","GSE67472","GSE27342","GSE63089","GSE13911","GSE15471","GSE28735",
   "GSE62452","GSE57957","GSE62232","GSE23400","GSE20347","GSE76925","GSE47460","GSE33814","GSE66676"),
 disease=c(rep("LUAD",3),rep("CRC",3),rep("IBD",3),rep("Asthma",3),rep("STAD",3),rep("PAAD",3),
   rep("HCC",2),rep("ESCC",2),rep("COPD",2),rep("NAFLD",2)), stringsAsFactors=FALSE)
cohorts$role <- ifelse(!duplicated(cohorts$disease),"discovery","validation")
paired_acc <- c("GSE32863","GSE19804","GSE10072","GSE44076","GSE27342","GSE63089","GSE15471","GSE28735",
                "GSE62452","GSE57957","GSE23400","GSE20347")
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
gene_sets <- lapply(split(toupper(gs$gene), gs$module), unique)
xc <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results/xcell/xcell_composition_scores.csv", stringsAsFactors=FALSE)
locate <- function(acc) for (d in ROOTS){ f<-list.files(d, pattern=paste0("^",acc,"_processed\\.rds$"), full.names=TRUE); if(length(f)) return(f[1]) }
rows <- list(); diag <- list(); fallback_log <- list()
for (i in seq_len(nrow(cohorts))) {
  acc<-cohorts$accession[i]; rds<-locate(acc); if(is.na(rds)) { fallback_log[[length(fallback_log)+1]]<-data.frame(accession=acc,issue="rds missing"); next }
  obj<-readRDS(rds); expr<-obj$gene_expression; meta<-obj$sample_metadata
  if(!all(c("group","sample_id") %in% names(meta)) || !all(c("Case","Control") %in% meta$group)) next
  pid <- if("patient_id" %in% names(meta)) as.character(meta$patient_id) else as.character(meta$sample_id)
  xcr <- xc[xc$accession==acc,,drop=FALSE]
  if(nrow(xcr)!=ncol(expr)) { fallback_log[[length(fallback_log)+1]]<-data.frame(accession=acc,issue=sprintf("xcell rows %d vs expr cols %d",nrow(xcr),ncol(expr))); next }
  # attach IDs to composition by documented original ordering, then JOIN BY ID
  comp <- data.frame(sample_id=as.character(meta$sample_id), epi=xcr$epi, fib=xcr$fib, end=xcr$end, imm=xcr$imm,
                     stringsAsFactors=FALSE)
  common <- intersect(colnames(expr), comp$sample_id)
  if(length(common) < 0.9*ncol(expr)) { fallback_log[[length(fallback_log)+1]]<-data.frame(accession=acc,issue="ID join loss"); next }
  expr <- expr[, common, drop=FALSE]
  comp <- comp[match(common, comp$sample_id), , drop=FALSE]
  grp  <- factor(meta$group[match(common, meta$sample_id)], levels=c("Control","Case"))  # explicit ref
  pidv <- pid[match(common, meta$sample_id)]
  paired <- acc %in% paired_acc
  present <- lapply(gene_sets, function(g) intersect(g, rownames(expr)))
  usable <- names(present)[lengths(present)>=3]
  if(!length(usable)) next
  sc <- GSVA::gsva(GSVA::gsvaParam(expr, gene_sets[usable], minSize=3, kcdf="Gaussian"), verbose=FALSE)
  iscase <- grp=="Case"
  for (m in rownames(sc)) {
    y <- as.numeric(sc[m, ])
    mc <- sc_ <- mr <- sr <- NA_real_; npr <- NA_integer_
    # ---------------- effect size ----------------
    if (paired) {
      cc <- intersect(pidv[iscase], pidv[!iscase]); np <- length(cc)
      if (np>=4) {
        yc <- y[match(cc, pidv[iscase])]; yr <- y[match(cc, pidv[!iscase])]
        ri <- suppressWarnings(cor(yc, yr)); ri <- if(is.finite(ri)) min(max(ri,-0.99),0.99) else 0.5
        es <- tryCatch(metafor::escalc(measure="SMCRH", m1i=mean(yc), m2i=mean(yr), sd1i=sd(yc), sd2i=sd(yr),
                                       ri=ri, ni=np), error=function(e) NULL)
        if(is.null(es)) { fallback_log[[length(fallback_log)+1]]<-data.frame(accession=acc,issue=paste("escalc SMCRH failed",m)); next }
        yi <- es$yi; vi <- es$vi; effect_scale <- "SMCRH"; r_used <- ri
        mc<-mean(yc); sc_<-sd(yc); mr<-mean(yr); sr<-sd(yr); npr<-np
      } else { yi<-NA; vi<-NA; effect_scale<-"insufficient pairs"; r_used<-NA }
    } else {
      yc<-y[iscase]; yr<-y[!iscase]
      mc<-mean(yc); sc_<-sd(yc); mr<-mean(yr); sr<-sd(yr)
      es <- tryCatch(metafor::escalc(measure="SMD", m1i=mean(yc), sd1i=sd(yc), n1i=length(yc),
                                     m2i=mean(yr), sd2i=sd(yr), n2i=length(yr)), error=function(e) NULL)
      if(is.null(es)) next
      yi<-es$yi; vi<-es$vi; effect_scale<-"SMD"; r_used<-NA
    }
    # ---------------- joint models ----------------
    dat <- data.frame(y=y, group=grp, comp[,-1,drop=FALSE], stringsAsFactors=FALSE)
    has_pid <- paired && length(unique(pidv))>5
    if (has_pid) dat$pid <- factor(pidv)
    fml_full <- if (has_pid) y ~ group + epi + fib + end + imm + pid else y ~ group + epi + fib + end + imm
    fml_null <- if (has_pid) y ~ group + pid else y ~ group
    f_full <- tryCatch(lm(fml_full, data=dat), error=function(e) NULL)
    fb <- FALSE
    if(is.null(f_full)){ f_full<-tryCatch(lm(y ~ group + epi + fib + end + imm, data=dat), error=function(e) NULL); fb<-TRUE }
    f_null <- tryCatch(lm(fml_null, data=dat), error=function(e) NULL)
    if(is.null(f_full)||is.null(f_null)) next
    s_full<-summary(f_full); s_null<-summary(f_null)
    b_adj<-s_full$coefficients["groupCase","Estimate"]; se_adj<-s_full$coefficients["groupCase","Std. Error"]
    p_adj<-s_full$coefficients["groupCase","Pr(>|t|)"]
    b_una<-s_null$coefficients["groupCase","Estimate"]
    sig <- s_full$sigma
    d_adj <- b_adj/sig; se_d <- se_adj/sig
    d_una_same_den <- b_una/sig   # same denominator -> comparable magnitudes
    rank_ok <- isTRUE(f_full$rank == length(coef(f_full)))
    rows[[length(rows)+1]] <- data.frame(accession=acc, disease=cohorts$disease[i], role=cohorts$role[i], feature=m,
      n_case=sum(iscase), n_control=sum(!iscase), paired=paired, npair=if(paired) length(intersect(pidv[iscase],pidv[!iscase])) else NA,
      r_emp=r_used, effect_scale=effect_scale, yi=as.numeric(yi), vi=as.numeric(vi),
      mean_case=mc, sd_case=sc_, mean_ctrl=mr, sd_ctrl=sr,
      beta_adj=b_adj, se_beta_adj=se_adj, p_adj=p_adj, d_adj=d_adj, se_d_adj=se_d,
      beta_unadj=b_una, d_unadj_same_den=d_una_same_den, sigma_full=sig,
      joint_fallback=fb, rank_full=rank_ok, stringsAsFactors=FALSE)
  }
  message("[OK] ",acc)
}
res<-bind_rows(rows); write.csv(res, file.path(V10,"v10_percohort_effects_joint.csv"), row.names=FALSE)
if(length(fallback_log)) write.csv(bind_rows(fallback_log), file.path(V10,"v10_fallback_log.csv"), row.names=FALSE)
cat("cohorts ok:", length(unique(res$accession)), " rows:", nrow(res), "\n")
cat("paired rows with finite yi:", sum(res$paired & is.finite(res$yi)), " of", sum(res$paired), "\n")
cat("paired median r_emp:", round(median(res$r_emp[res$paired], na.rm=TRUE),3), "\n")
cat("joint sig p<0.05:", sum(res$p_adj<0.05, na.rm=TRUE), "\n")
