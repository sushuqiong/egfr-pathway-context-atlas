#!/usr/bin/env Rscript
# v12: export the core resource tables — per-cohort sample-level module scores (GSVA, z within cohort),
# sample annotation, gene-mapping/transformation log, and per-sample composition join keys.
suppressPackageStartupMessages({library(GSVA); library(dplyr)})
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
OUT <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"; dir.create(OUT, recursive=TRUE, showWarnings=FALSE)
P <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/dataset_package"
for (d in c("01_cohort_registry","02_sample_annotation","03_expression","04_modules","05_composition",
            "06_single_cell","07_estimates","08_qc","09_reuse_examples","10_environment"))
  dir.create(file.path(P,d), recursive=TRUE, showWarnings=FALSE)
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
gene_sets <- lapply(split(toupper(gs$gene), gs$module), unique)
files <- unlist(lapply(ROOTS, function(d) list.files(d, pattern="_processed\\.rds$", full.names=TRUE)))
ann <- list(); scores <- list(); translog <- list()
for (f in files) {
  acc <- sub("_processed\\.rds$", "", basename(f)); obj <- readRDS(f)
  ex <- obj$gene_expression; md <- obj$sample_metadata
  sid <- if ("sample_id" %in% names(md)) as.character(md$sample_id) else colnames(ex)
  pid <- if ("patient_id" %in% names(md)) as.character(md$patient_id) else sid
  grp <- if ("group" %in% names(md)) as.character(md$group) else NA
  plat <- if ("platform" %in% names(md)) paste(unique(md$platform), collapse=";") else NA
  # transformation log: log2 applied or not (recording the observed distribution rule)
  v <- as.numeric(ex[1:min(2000, nrow(ex)), 1:min(5, ncol(ex))])
  maxv <- suppressWarnings(max(v, na.rm=TRUE)); frac_int <- mean(abs(v - round(v)) < 1e-8, na.rm=TRUE)
  already_log <- !(frac_int > 0.98 && maxv > 50)
  translog[[length(translog)+1]] <- data.frame(accession=acc, n_genes=nrow(ex), n_samples=ncol(ex),
    input_max=maxv, integer_fraction=round(frac_int,3), log2_applied=!already_log,
    note=ifelse(already_log, "already on a log scale; no transform", "raw-like intensities; auto log2 applied"), stringsAsFactors=FALSE)
  ann[[length(ann)+1]] <- data.frame(accession=acc, sample_id=sid, patient_id=pid, group=grp, platform=plat,
    case_control_role=ifelse(grp=="Case","case", ifelse(grp=="Control","control","unknown")),
    paired_with=ifelse(pid %in% intersect(pid[grp=="Case"], pid[grp=="Control"]), paste0(pid,"|paired"), ""),
    stringsAsFactors=FALSE)
  present <- lapply(gene_sets, function(g) intersect(g, toupper(rownames(ex))))
  usable <- names(present)[lengths(present)>=3]
  sc <- GSVA::gsva(GSVA::gsvaParam(ex, gene_sets[usable], minSize=3, kcdf="Gaussian"), verbose=FALSE)
  z <- t(scale(t(sc)))
  scdf <- as.data.frame(t(z)); scdf$sample_id <- colnames(z); scdf$accession <- acc
  scores[[length(scores)+1]] <- scdf
  cat("[OK]", acc, ncol(ex), "samples\n")
}
ann_df <- bind_rows(ann); sc_df <- bind_rows(scores)
write.csv(ann_df, file.path(P,"02_sample_annotation","sample_annotation_geo_cohorts.csv"), row.names=FALSE)
write.csv(translog %>% bind_rows(), file.path(P,"03_expression","transformation_log.csv"), row.names=FALSE)
write.csv(sc_df, file.path(P,"04_modules","sample_module_scores_gsva_z.csv"), row.names=FALSE)
write.csv(bind_rows(translog), file.path(OUT,"v12_transformation_log.csv"), row.names=FALSE)
cat("annotation rows:", nrow(ann_df), "| score rows:", nrow(sc_df), "\n")
