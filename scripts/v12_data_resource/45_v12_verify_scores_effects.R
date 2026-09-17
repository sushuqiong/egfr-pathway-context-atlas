#!/usr/bin/env Rscript
# v12 adversarial checkpoint 2: independent recomputation of module scores and cohort effect sizes
# for three cohorts (paired/unpaired, different platforms) and comparison with the shipped values.
suppressPackageStartupMessages({library(GSVA); library(metafor); library(dplyr)})
R  <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
PK <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/dataset_package"
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
sets <- read.csv(file.path(PK,"04_modules","module_definitions.csv"), stringsAsFactors=FALSE)
gene_sets <- lapply(split(toupper(sets$gene), sets$module), unique)
shipped_scores <- read.csv(file.path(PK,"04_modules","sample_module_scores_gsva_z.csv"), stringsAsFactors=FALSE)
shipped_eff <- read.csv(file.path(PK,"07_estimates","per_cohort_effects.csv"), stringsAsFactors=FALSE)
rows <- list()
for (acc in c("GSE13911","GSE44076","GSE47460")) {
  f <- unlist(lapply(ROOTS, function(d) list.files(d, pattern=paste0("^",acc,"_processed[.]rds$"), full.names=TRUE)))[1]
  if (is.na(f)) { cat("[MISS]", acc, "\n"); next }
  obj <- readRDS(f); ex <- obj$gene_expression; md <- obj$sample_metadata
  sid <- as.character(md$sample_id); pid <- if ("patient_id" %in% names(md)) as.character(md$patient_id) else sid
  grp <- factor(as.character(md$group), levels=c("Control","Case")); iscase <- grp=="Case"
  present <- lapply(gene_sets, function(g) intersect(g, toupper(rownames(ex))))
  usable <- names(present)[lengths(present)>=3]
  sc <- GSVA::gsva(GSVA::gsvaParam(ex, gene_sets[usable], minSize=3, kcdf="Gaussian"), verbose=FALSE)
  z  <- t(scale(t(sc)))
  # --- per-sample score agreement against the shipped table
  sh <- shipped_scores[shipped_scores$accession==acc, , drop=FALSE]
  sh$sample_id <- as.character(sh$sample_id)
  common <- intersect(colnames(z), sh$sample_id)
  sp <- c(); pr <- c()
  for (m in intersect(rownames(z), names(sh))) {
    a <- as.numeric(z[m, common]); b <- suppressWarnings(as.numeric(sh[[m]][match(common, sh$sample_id)]))
    if (length(a) < 5) next
    sp <- c(sp, suppressWarnings(cor(a, b, method="spearman"))); pr <- c(pr, suppressWarnings(cor(a, b)))
  }
  # --- effect size agreement
  n_both <- if (all(!is.na(pid) & pid != sid)) length(intersect(pid[iscase], pid[!iscase])) else 0L
  paired <- n_both >= 4
  for (m in rownames(z)) {
    y <- as.numeric(z[m, ])
    if (paired) {
      cc <- intersect(pid[iscase], pid[!iscase]); yc <- y[iscase][match(cc, pid[iscase])]; yr <- y[!iscase][match(cc, pid[!iscase])]
      ri <- suppressWarnings(cor(yc, yr)); ri <- if (is.finite(ri)) min(max(ri,-0.99),0.99) else 0.2
      e <- metafor::escalc(measure="SMCRPH", m1i=mean(yc), m2i=mean(yr), sd1i=sd(yc), sd2i=sd(yr), ri=ri, ni=length(cc))
    } else {
      yc <- y[iscase]; yr <- y[!iscase]
      e <- metafor::escalc(measure="SMDH", m1i=mean(yc), sd1i=sd(yc), n1i=length(yc), m2i=mean(yr), sd2i=sd(yr), n2i=length(yr))
    }
    shp <- shipped_eff[shipped_eff$accession==acc & shipped_eff$feature==m, ]
    if (!nrow(shp)) next
    rows[[length(rows)+1]] <- data.frame(accession=acc, feature=m, paired=paired,
      yi_recomputed=round(as.numeric(e$yi), 4), yi_shipped=round(as.numeric(shp$yi[1]), 4),
      abs_diff=round(abs(as.numeric(e$yi) - as.numeric(shp$yi[1])), 4),
      se_recomputed=round(sqrt(as.numeric(e$vi)), 4), se_shipped=round(sqrt(as.numeric(shp$vi[1])), 4), stringsAsFactors=FALSE)
  }
  cat(sprintf("[%s] samples=%d paired=%s | score agreement vs shipped: median Pearson %.3f / Spearman %.3f (min %.3f)\n",
              acc, ncol(z), paired, median(pr, na.rm=TRUE), median(sp, na.rm=TRUE), min(pr, na.rm=TRUE)))
}
res <- bind_rows(rows)
write.csv(res, file.path(R,"v12_qc_module_score_effect_verification.csv"), row.names=FALSE)
cat("\n== effect-size agreement (per cohort) ==\n")
print(res %>% group_by(accession) %>% summarise(rows=n(), max_abs_diff=max(abs_diff), median_abs_diff=median(abs_diff),
      max_se_diff=max(abs(se_recomputed-se_shipped)), .groups="drop") %>% as.data.frame(), row.names=FALSE)
cat("\nmax absolute difference across all compared effects:", max(res$abs_diff), "\n")
