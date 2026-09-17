#!/usr/bin/env Rscript
# v12 effects + meta, metadata-driven pairing (no hardcoded cohort list)
#   paired cohorts  -> SMCRPH (denominator sqrt((sd1^2+sd2^2)/2), empirical within-pair r)
#   unpaired cohorts-> SMDH  (same denominator)
# Cohorts without patient identifiers are unpaired by necessity and flagged.
# GSE16879 (treatment-response series, Responder vs NonResponder) is excluded from case-control analyses.
suppressPackageStartupMessages({library(GSVA); library(metafor); library(dplyr)})
R <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
EXCLUDE <- c("GSE16879")   # treatment-response design (Responder vs NonResponder), not case-control
CTX <- c(GSE32863="LUAD",GSE19804="LUAD",GSE10072="LUAD",GSE44076="CRC",GSE41258="CRC",GSE23878="CRC",
         GSE75214="IBD",GSE87473="IBD",GSE179285="IBD",GSE4302="Asthma",GSE43696="Asthma",GSE67472="Asthma",
         GSE27342="STAD",GSE63089="STAD",GSE13911="STAD",GSE15471="PAAD",GSE28735="PAAD",GSE62452="PAAD",
         GSE57957="HCC",GSE62232="HCC",GSE23400="ESCC",GSE20347="ESCC",GSE76925="COPD",GSE47460="COPD",
         GSE33814="NAFLD",GSE66676="NAFLD",GSE16879="IBD(treatment-response)")
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
gene_sets <- lapply(split(toupper(gs$gene), gs$module), unique)
locate <- function(acc) { for (d in ROOTS) { f <- list.files(d, pattern=paste0("^",acc,"_processed\\.rds$"), full.names=TRUE); if (length(f)) return(f[1]) }; NA_character_ }
files <- unlist(lapply(ROOTS, function(d) list.files(d, pattern="_processed\\.rds$", full.names=TRUE)))
accs <- setdiff(sub("_processed\\.rds$","",basename(files)), EXCLUDE)
rows <- list()
for (acc in accs) {
  f <- locate(acc); if (is.na(f)) next
  obj <- readRDS(f); ex <- obj$gene_expression; md <- obj$sample_metadata
  sid <- if ("sample_id" %in% names(md)) as.character(md$sample_id) else colnames(ex)
  has_pid <- "patient_id" %in% names(md)
  pid <- if (has_pid) as.character(md$patient_id) else sid
  grp <- factor(if ("group" %in% names(md)) as.character(md$group) else NA, levels=c("Control","Case"))
  iscase <- grp == "Case"
  n_both <- if (has_pid) length(intersect(pid[iscase], pid[!iscase])) else 0L
  paired <- has_pid && n_both >= 4
  present <- lapply(gene_sets, function(g) intersect(g, toupper(rownames(ex))))
  usable <- names(present)[lengths(present)>=3]
  sc <- GSVA::gsva(GSVA::gsvaParam(ex, gene_sets[usable], minSize=3, kcdf="Gaussian"), verbose=FALSE)
  for (m in rownames(sc)) {
    y <- as.numeric(sc[m,]); ri <- NA_real_; npr <- NA_integer_
    if (paired) {
      cc <- intersect(pid[iscase], pid[!iscase]); npr <- length(cc)
      yc <- y[iscase][match(cc, pid[iscase])]; yr <- y[!iscase][match(cc, pid[!iscase])]
      ri <- suppressWarnings(cor(yc,yr)); ri <- if (is.finite(ri)) min(max(ri,-0.99),0.99) else 0.2
      es <- tryCatch(metafor::escalc(measure="SMCRPH", m1i=mean(yc), m2i=mean(yr), sd1i=sd(yc), sd2i=sd(yr), ri=ri, ni=npr), error=function(e) NULL)
      meas <- "SMCRPH"
    } else {
      yc <- y[iscase]; yr <- y[!iscase]
      es <- tryCatch(metafor::escalc(measure="SMDH", m1i=mean(yc), sd1i=sd(yc), n1i=length(yc), m2i=mean(yr), sd2i=sd(yr), n2i=length(yr)), error=function(e) NULL)
      meas <- "SMDH"
    }
    if (is.null(es)) next
    dat <- data.frame(y=y, group=grp, stringsAsFactors=FALSE)
    use_pid <- has_pid && length(unique(pid))>5
    if (use_pid) dat$pid <- factor(pid)
    fb <- tryCatch(lm(if (use_pid) y ~ group + pid else y ~ group, data=dat), error=function(e) NULL)
    fb2 <- tryCatch(lm(if (use_pid) y ~ group + pid else y ~ group, data=dat), error=function(e) NULL)
    rows[[length(rows)+1]] <- data.frame(accession=acc, disease=CTX[[acc]], feature=m,
      paired=paired, patient_ids_available=has_pid, n_both_arm_patients=n_both,
      n_case=sum(iscase), n_control=sum(!iscase), npair=npr, r_emp=ri, measure=meas,
      yi=as.numeric(es$yi), vi=as.numeric(es$vi),
      mean_case=mean(y[iscase]), sd_case=sd(y[iscase]), mean_ctrl=mean(y[!iscase]), sd_ctrl=sd(y[!iscase]),
      beta_base=coef(fb)[["groupCase"]], se_base=summary(fb)$coefficients["groupCase","Std. Error"],
      p_base=summary(fb)$coefficients["groupCase","Pr(>|t|)"],
      stringsAsFactors=FALSE)
  }
  cat(sprintf("[%s] paired=%s patients_with_both_arms=%d\n", acc, paired, n_both))
}
res <- bind_rows(rows)
write.csv(res, file.path(R,"v12_percohort_effects.csv"), row.names=FALSE)
cat("\ncohorts:", length(unique(res$accession)), "| rows:", nrow(res),
    "| paired cohorts:", length(unique(res$accession[res$paired])), "\n")
cat("paired cohorts:", paste(sort(unique(res$accession[res$paired])), collapse=", "), "\n")
cat("cohorts without patient ids:", paste(sort(unique(res$accession[!res$patient_ids_available])), collapse=", "), "\n")
# ---- meta layer ----
df <- res[is.finite(res$yi) & is.finite(res$vi) & res$vi>0, ]
pool <- function(d, tag, method="REML", test="knha") {
  out <- list()
  for (key in split(d, list(d$disease, d$feature), drop=TRUE)) {
    if (!nrow(key)) next
    m <- tryCatch(rma.uni(yi, vi, data=key, method=method, test=test), error=function(e) NULL); if (is.null(m)) next
    out[[length(out)+1]] <- data.frame(disease=key$disease[1], feature=key$feature[1], k=nrow(key),
      est=as.numeric(m$beta), se=m$se, p=m$pval, ci_lo=m$ci.lb, ci_hi=m$ci.ub, I2=m$I2, tau2=m$tau2,
      measures=paste(names(table(key$measure)), table(key$measure), collapse="|"),
      cohorts=paste(key$accession, collapse=";"), stringsAsFactors=FALSE)
  }
  r <- bind_rows(out); r$fdr <- NA_real_
  for (dis in unique(r$disease)) { ix <- r$disease==dis & r$k>=2 & is.finite(r$p); if (any(ix)) r$fdr[ix] <- p.adjust(r$p[ix], "BH") }
  write.csv(r, file.path(R, sprintf("v12_meta_%s.csv", tag)), row.names=FALSE)
  cat(sprintf("[%s] k>=2: %d | BH-significant: %d\n", tag, sum(r$k>=2), sum(r$k>=2 & r$fdr<0.05, na.rm=TRUE)))
  r
}
cat("\n== meta ==\n")
m1 <- pool(df, "primary_reml_knha")
pool(df, "DL", method="DL", test="z")
pool(df, "adhoc", test="adhoc")
pool(df[!df$paired,], "unpaired_only")
for (rho in c(0.5,0.7)) {
  d <- df
  ix <- which(d$paired & is.finite(d$npair) & is.finite(d$mean_case))
  if (length(ix)) {
    e <- metafor::escalc(measure="SMCRPH", m1i=d$mean_case[ix], m2i=d$mean_ctrl[ix],
                         sd1i=d$sd_case[ix], sd2i=d$sd_ctrl[ix], ri=rho, ni=d$npair[ix])
    d$yi[ix] <- as.numeric(e$yi); d$vi[ix] <- as.numeric(e$vi)
  }
  pool(d, sprintf("rho%.1f", rho))
}
sig <- m1[m1$k>=2 & m1$fdr<0.05, c("disease","feature","k","est","ci_lo","ci_hi","p","fdr","I2","measures")]
cat("\n== primary significant states ==\n"); print(sig, row.names=FALSE, digits=3)
cat("by disease:", paste(names(table(sig$disease)), table(sig$disease), collapse=" | "), "\n")
