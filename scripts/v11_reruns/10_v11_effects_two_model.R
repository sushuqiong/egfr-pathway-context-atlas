#!/usr/bin/env Rscript
# v11 RERUN A: effect sizes on a genuinely common denominator + two-model composition comparison
#   unpaired: metafor measure="SMDH"  (denominator sqrt((sd1^2+sd2^2)/2), Hedges-corrected)
#   paired  : metafor measure="SMCRPH" (same denominator, empirical ri, Hedges-corrected)
#   composition: base model (module ~ disease [+ patient]) vs adjusted model (+4 compartment scores), same samples
suppressPackageStartupMessages({library(GSVA); library(metafor); library(dplyr)})
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
OUT <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/reruns/results"
dir.create(OUT, recursive=TRUE, showWarnings=FALSE)
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
rows <- list(); log <- list()
for (i in seq_len(nrow(cohorts))) {
  acc <- cohorts$accession[i]; rds <- locate(acc)
  if (is.na(rds)) { log[[length(log)+1]] <- data.frame(accession=acc, issue="rds missing"); next }
  obj <- readRDS(rds); expr <- obj$gene_expression; meta <- obj$sample_metadata
  if(!all(c("group","sample_id") %in% names(meta))) { log[[length(log)+1]] <- data.frame(accession=acc, issue="metadata incomplete"); next }
  pid <- if("patient_id" %in% names(meta)) as.character(meta$patient_id) else as.character(meta$sample_id)
  xcr <- xc[xc$accession==acc,,drop=FALSE]
  if(nrow(xcr)!=ncol(expr)){ log[[length(log)+1]] <- data.frame(accession=acc, issue=sprintf("xcell %d vs expr %d",nrow(xcr),ncol(expr))); next }
  comp <- data.frame(sample_id=as.character(meta$sample_id), epi=xcr$epi, fib=xcr$fib, end=xcr$end, imm=xcr$imm, stringsAsFactors=FALSE)
  common <- intersect(colnames(expr), comp$sample_id)
  if(length(common) < 0.9*ncol(expr)){ log[[length(log)+1]] <- data.frame(accession=acc, issue="ID join loss"); next }
  expr <- expr[, common, drop=FALSE]; comp <- comp[match(common, comp$sample_id),,drop=FALSE]
  grp <- factor(meta$group[match(common, meta$sample_id)], levels=c("Control","Case"))
  pidv <- pid[match(common, meta$sample_id)]
  paired <- acc %in% paired_acc
  present <- lapply(gene_sets, function(g) intersect(g, rownames(expr)))
  usable <- names(present)[lengths(present)>=3]; if(!length(usable)) next
  sc <- GSVA::gsva(GSVA::gsvaParam(expr, gene_sets[usable], minSize=3, kcdf="Gaussian"), verbose=FALSE)
  iscase <- grp=="Case"
  for (m in rownames(sc)) {
    y <- as.numeric(sc[m,]); mc<-sc_<-mr<-sr<-NA_real_; npr<-NA_integer_
    if (paired) {
      cc <- intersect(pidv[iscase], pidv[!iscase]); np <- length(cc)
      if (np>=4) {
        yc <- y[iscase][match(cc, pidv[iscase])]; yr <- y[!iscase][match(cc, pidv[!iscase])]
        ri <- suppressWarnings(cor(yc,yr)); ri <- if(is.finite(ri)) min(max(ri,-0.99),0.99) else 0.2
        es <- tryCatch(metafor::escalc(measure="SMCRPH", m1i=mean(yc), m2i=mean(yr), sd1i=sd(yc), sd2i=sd(yr), ri=ri, ni=np), error=function(e) NULL)
        if(is.null(es)){ log[[length(log)+1]] <- data.frame(accession=acc, issue=paste("SMCRPH failed",m)); next }
        yi<-as.numeric(es$yi); vi<-as.numeric(es$vi); measure<-"SMCRPH"; mc<-mean(yc); sc_<-sd(yc); mr<-mean(yr); sr<-sd(yr); npr<-np
      } else { yi<-NA; vi<-NA; measure<-"insufficient pairs" }
    } else {
      yc <- y[iscase]; yr <- y[!iscase]; mc<-mean(yc); sc_<-sd(yc); mr<-mean(yr); sr<-sd(yr)
      es <- tryCatch(metafor::escalc(measure="SMDH", m1i=mean(yc), sd1i=sd(yc), n1i=length(yc), m2i=mean(yr), sd2i=sd(yr), n2i=length(yr)), error=function(e) NULL)
      if(is.null(es)) next
      yi<-as.numeric(es$yi); vi<-as.numeric(es$vi); measure<-"SMDH"
    }
    # ---- two-model composition comparison (same samples) ----
    dat <- data.frame(y=y, group=grp, comp[,-1,drop=FALSE], stringsAsFactors=FALSE)
    has_pid <- paired && length(unique(pidv))>5
    if (has_pid) dat$pid <- factor(pidv)
    f_base <- tryCatch(lm(if(has_pid) y ~ group + pid else y ~ group, data=dat), error=function(e) NULL)
    f_adj  <- tryCatch(lm(if(has_pid) y ~ group + epi + fib + end + imm + pid else y ~ group + epi + fib + end + imm, data=dat), error=function(e) NULL)
    fb <- FALSE
    if(is.null(f_adj)) { f_adj <- tryCatch(lm(y ~ group + epi + fib + end + imm, data=dat), error=function(e) NULL); fb <- TRUE }
    if(is.null(f_base) || is.null(f_adj)) next
    sb <- summary(f_base); sa <- summary(f_adj)
    sd_ref <- sd(y, na.rm=TRUE)   # common reference SD for standardising both coefficients
    rows[[length(rows)+1]] <- data.frame(accession=acc, disease=cohorts$disease[i], role=cohorts$role[i], feature=m,
      paired=paired, n_case=sum(iscase), n_control=sum(!iscase), npair=npr, r_emp=if(paired) ri else NA,
      measure=measure, yi=yi, vi=vi,
      beta_base=sb$coefficients["groupCase","Estimate"], se_base=sb$coefficients["groupCase","Std. Error"],
      p_base=sb$coefficients["groupCase","Pr(>|t|)"],
      beta_adj=sa$coefficients["groupCase","Estimate"], se_adj=sa$coefficients["groupCase","Std. Error"],
      p_adj=sa$coefficients["groupCase","Pr(>|t|)"],
      d_base=beta_base<-sb$coefficients["groupCase","Estimate"]/sd_ref,
      d_adj=sa$coefficients["groupCase","Estimate"]/sd_ref,
      sd_ref=sd_ref, sigma_adj=sa$sigma, joint_fallback=fb, rank_adj=isTRUE(f_adj$rank==length(coef(f_adj))),
      mean_case=mc, sd_case=sc_, mean_ctrl=mr, sd_ctrl=sr, stringsAsFactors=FALSE)
  }
  message("[OK] ", acc)
}
res <- bind_rows(rows); write.csv(res, file.path(OUT,"v11_percohort_effects.csv"), row.names=FALSE)
if(length(log)) write.csv(bind_rows(log), file.path(OUT,"v11_fallback_log.csv"), row.names=FALSE)
cat("cohorts:", length(unique(res$accession)), "rows:", nrow(res), "\n")
cat("paired rows estimable:", sum(res$paired & is.finite(res$yi)), "/", sum(res$paired), "| median empirical ri:", round(median(res$r_emp[res$paired], na.rm=TRUE),3), "\n")
cat("measures:", paste(names(table(res$measure)), table(res$measure), collapse=" | "), "\n")
cat("joint p<0.05:", sum(res$p_adj<0.05, na.rm=TRUE), "| base p<0.05:", sum(res$p_base<0.05, na.rm=TRUE), "\n")
cat("median |beta_adj|/|beta_base| (same SD):", round(median(abs(res$beta_adj)/pmax(abs(res$beta_base),1e-6), na.rm=TRUE),3), "\n")
