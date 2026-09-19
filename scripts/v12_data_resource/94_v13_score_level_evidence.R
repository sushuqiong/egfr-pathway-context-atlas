#!/usr/bin/env Rscript
# v13.1: ship score-level reproducibility evidence (per-sample Spearman per module) for the three checked cohorts.
suppressPackageStartupMessages({library(GSVA); library(dplyr)})
V13 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v13"
PK <- file.path(V13,"dataset_package"); R <- file.path(V13,"results")
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
sets <- read.csv(file.path(PK,"04_modules","module_definitions.csv"), stringsAsFactors=FALSE)
gene_sets <- lapply(split(toupper(sets$gene), sets$module), unique)
shipped <- read.csv(file.path(PK,"04_modules","sample_module_scores_gsva_z.csv"), stringsAsFactors=FALSE)
rows <- list()
for (acc in c("GSE13911","GSE44076","GSE47460")) {
  f <- unlist(lapply(ROOTS, function(d) list.files(d, pattern=paste0("^",acc,"_processed[.]rds$"), full.names=TRUE)))[1]
  if (is.na(f)) next
  ex <- readRDS(f)$gene_expression
  usable <- names(gene_sets)[sapply(gene_sets, function(g) length(intersect(g, toupper(rownames(ex)))) >= 3)]
  sc <- GSVA::gsva(GSVA::gsvaParam(ex, gene_sets[usable], minSize=3, kcdf="Gaussian"), verbose=FALSE)
  z <- t(scale(t(sc)))
  sh <- shipped[shipped$accession==acc, , drop=FALSE]; sh$sample_id <- as.character(sh$sample_id)
  common <- intersect(colnames(z), sh$sample_id)
  for (m in intersect(rownames(z), names(sh))) {
    a <- as.numeric(z[m, common]); b <- suppressWarnings(as.numeric(sh[[m]][match(common, sh$sample_id)]))
    if (length(a) < 5) next
    rows[[length(rows)+1]] <- data.frame(accession=acc, module=m, n_samples=length(common),
      spearman=round(suppressWarnings(cor(a,b,method="spearman")),4), pearson=round(suppressWarnings(cor(a,b)),4),
      max_abs_z_diff=round(max(abs(a-b)),4), stringsAsFactors=FALSE)
  }
  cat("[OK]", acc, "modules compared:", sum(sapply(rows, function(r) r$accession[1])==acc), "\n")
}
res <- bind_rows(rows)
write.csv(res, file.path(PK,"08_qc","qc_bulk_score_level_reproducibility.csv"), row.names=FALSE)
write.csv(res, file.path(R,"v13_qc_bulk_score_level_reproducibility.csv"), row.names=FALSE)
cat("rows:", nrow(res), "| min Spearman:", min(res$spearman), "| min Pearson:", min(res$pearson),
    "| max abs z difference:", max(res$max_abs_z_diff), "\n")
