#!/usr/bin/env Rscript
# v9 Rerun 1+2 : joint composition model per cohort + unified-scale effect sizes for meta
suppressPackageStartupMessages({
  library(Biobase); library(GSVA); library(dplyr); library(tidyr)
})
ROOTS <- c(
  "C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
  "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
  "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
V9  <- "C:/Users/fengq/Desktop/EGFR/EGFR的v9/reruns/results"
dir.create(V9, recursive=TRUE, showWarnings=FALSE)
cohorts <- data.frame(
 accession=c("GSE32863","GSE19804","GSE10072","GSE44076","GSE41258","GSE23878",
             "GSE75214","GSE87473","GSE179285","GSE4302","GSE43696","GSE67472",
             "GSE27342","GSE63089","GSE13911","GSE15471","GSE28735","GSE62452",
             "GSE57957","GSE62232","GSE23400","GSE20347","GSE76925","GSE47460",
             "GSE33814","GSE66676"),
 disease=c(rep("LUAD",3),rep("CRC",3),rep("IBD",3),rep("Asthma",3),rep("STAD",3),
           rep("PAAD",3),rep("HCC",2),rep("ESCC",2),rep("COPD",2),rep("NAFLD",2)),
 role=ifelse(!duplicated(c(rep("LUAD",3),rep("CRC",3),rep("IBD",3),rep("Asthma",3),rep("STAD",3),
           rep("PAAD",3),rep("HCC",2),rep("ESCC",2),rep("COPD",2),rep("NAFLD",2))), "discovery","validation"),
 stringsAsFactors=FALSE)
paired_acc <- c("GSE32863","GSE19804","GSE10072","GSE44076","GSE27342","GSE63089",
                "GSE15471","GSE28735","GSE62452","GSE57957","GSE23400","GSE20347")
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
gene_sets <- lapply(split(toupper(gs$gene), gs$module), unique)
xc <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results/xcell/xcell_composition_scores.csv", stringsAsFactors=FALSE)
locate <- function(acc) for (d in ROOTS) { f<-list.files(d, pattern=paste0("^",acc,"_processed\\.rds$"), full.names=TRUE); if(length(f)) return(f[1]) }

unpaired_g <- function(a,b){
  a<-a[is.finite(a)]; b<-b[is.finite(b)]; n1<-length(a); n0<-length(b)
  if(n1<2||n0<2) return(c(NA,NA))
  sp<-sqrt(((n1-1)*var(a)+(n0-1)*var(b))/(n1+n0-2))
  if(!is.finite(sp)||sp<=0) return(c(NA,NA))
  J<-1-3/(4*(n1+n0)-9)
  g<-J*(mean(a)-mean(b))/sp
  v<- (n1+n0)/(n1*n0)+ g^2/(2*(n1+n0))
  c(g,v)
}
emp_r_pair <- function(x,pv,rv){ cm<-intersect(pv,rv); if(length(cm)<8) return(NA_real_); d<-x[match(cm,pv)]-x[match(cm,rv)]; stats::cor(x[match(cm,pv)],x[match(cm,rv)]) }
rows <- list()
for (i in seq_len(nrow(cohorts))) {
  acc <- cohorts$accession[i]; rds <- locate(acc)
  if(is.na(rds)){ message("[MISS] ",acc); next }
  obj <- readRDS(rds); expr <- obj$gene_expression; meta <- obj$sample_metadata
  if(!all(c("group","sample_id") %in% names(meta))) { message("[SKIP meta]",acc); next }
  if(!all(c("Case","Control") %in% meta$group)) { message("[SKIP groups]",acc); next }
  pos<-"Case"; ref<-"Control"; paired <- acc %in% paired_acc
  expr <- expr[, match(meta$sample_id, colnames(expr)), drop=FALSE]
  # xCell comps aligned to sample order (same pipeline order)
  xc_row <- xc[xc$accession==acc, , drop=FALSE]
  if(nrow(xc_row)!=ncol(expr)) { message("[SKIP xc size] ",acc); next }
  comp <- data.frame(epi=xc_row$epi, fib=xc_row$fib, end=xc_row$end, imm=xc_row$imm)
  present <- lapply(gene_sets, function(g) intersect(g, rownames(expr)))
  usable <- names(present)[lengths(present)>=3]
  if(!length(usable)) next
  sc <- GSVA::gsva(GSVA::gsvaParam(expr, gene_sets[usable], minSize=3, maxSize=Inf, kcdf="Gaussian"), verbose=FALSE)
  rownames(sc) <- usable
  pid <- if("patient_id" %in% names(meta)) meta$patient_id else meta$sample_id
  g_case <- meta$group==pos; g_ref <- meta$group==ref
  for (m in rownames(sc)) {
    y <- sc[m,]
    # raw
    if(paired){
      pv<-pid[g_case]; rv<-pid[g_ref]; cm<-intersect(pv,rv); np<-length(cm)
      if(np>=3){ d<-y[match(cm,pv)]-y[match(cm,rv)]; dz<-mean(d)/sd(d)
        r_emp<-if(np>=8) emp_r_pair(y,pv,rv) else NA
        g_eq<- if(!is.na(r_emp)&&is.finite(r_emp)) dz*sqrt(2*(1-r_emp)) else dz*sqrt(2*(1-0.5))
        vg <- 2*(1-(if(!is.na(r_emp)) r_emp else 0.5))/np + g_eq^2/(2*(np-2))
        smd_unified<-g_eq; var_unified<-vg; r_used<-if(!is.na(r_emp)) r_emp else 0.5; npair<-np
      } else { smd_unified<-NA; var_unified<-NA; r_used<-NA; npair<-0 }
    } else {
      gu<-unpaired_g(y[g_case],y[g_ref]); smd_unified<-gu[1]; var_unified<-gu[2]; r_used<-NA; npair<-NA
    }
    # joint model
    dat <- data.frame(y=y, group=factor(meta$group), comp, stringsAsFactors=FALSE)
    if(paired && length(unique(pid))>5){
      dat$pid <- factor(pid)
      fit <- tryCatch(lm(y ~ group + epi + fib + end + imm + pid, data=dat), error=function(e) NULL)
      if(is.null(fit)) { fit <- tryCatch(lm(y ~ group + epi + fib + end + imm, data=dat), error=function(e) NULL); fallback<-TRUE } else fallback<-FALSE
    } else { fit <- tryCatch(lm(y ~ group + epi + fib + end + imm, data=dat), error=function(e) NULL); fallback <- if(paired) TRUE else FALSE }
    if(is.null(fit)) next
    cf <- summary(fit)$coefficients
    gi <- grep("groupCase", rownames(cf))
    if(!length(gi)) gi <- 2
    beta<-cf[gi[1],"Estimate"]; se<-cf[gi[1],"Std. Error"]; p<-cf[gi[1],"Pr(>|t|)"]; sigma<-summary(fit)$sigma
    d_adj<- if(is.finite(sigma)&&sigma>0) beta/sigma else NA
    se_adj<- if(is.finite(sigma)&&sigma>0) se/sigma else NA
    rank_ok <- isTRUE(fit$rank==length(coef(fit)))
    rows[[length(rows)+1]] <- data.frame(accession=acc, disease=cohorts$disease[i], role=cohorts$role[i],
      feature=m, n_case=sum(g_case), n_control=sum(g_ref), paired=paired, npair=npair,
      r_emp=r_used, smd_unified=smd_unified, var_unified=var_unified,
      d_adj=d_adj, se_adj=se_adj, p_adj=p, df_resid=fit$df.residual,
      joint_fallback=fallback, rank_full=rank_ok, stringsAsFactors=FALSE)
  }
  message("[OK] ", acc)
}
res <- bind_rows(rows)
write.csv(res, file.path(V9,"v9_percohort_joint_unified.csv"), row.names=FALSE)
cat("rows:", nrow(res), " cohorts processed OK. saved.\n")
cat("joint sig (p<0.05):", sum(res$p_adj<0.05, na.rm=TRUE), "\n")
