#!/usr/bin/env Rscript
# v12: sample-level registry for all bulk cohorts (deliverable: source registry + sample/pairing annotation)
suppressPackageStartupMessages({library(dplyr)})
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
OUT <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
files <- unlist(lapply(ROOTS, function(d) list.files(d, pattern="_processed\\.rds$", full.names=TRUE)))
rows <- list()
for (f in files) {
  acc <- sub("_processed\\.rds$", "", basename(f)); obj <- readRDS(f)
  md <- obj$sample_metadata; ex <- obj$gene_expression
  sid <- if ("sample_id" %in% names(md)) as.character(md$sample_id) else colnames(ex)
  pid_avail <- "patient_id" %in% names(md) && length(unique(as.character(md$patient_id))) > 1
  pid <- if (pid_avail) as.character(md$patient_id) else sid
  grp <- if ("group" %in% names(md)) as.character(md$group) else NA
  tis <- if ("tissue" %in% names(md)) as.character(md$tissue) else if ("sample_type" %in% names(md)) as.character(md$sample_type) else NA
  plat <- if ("platform" %in% names(md)) as.character(md$platform) else NA
  rows[[length(rows)+1]] <- data.frame(accession=acc, sample_id=sid, patient_id=pid, group=grp,
    patient_id_available=as.integer(pid_avail), tissue_or_sample_type=tis, platform=plat, n_genes=nrow(ex), stringsAsFactors=FALSE)
}
sm <- bind_rows(rows)
write.csv(sm, file.path(OUT,"v12_sample_level_registry.csv"), row.names=FALSE)
cat("sample records:", nrow(sm), "| cohorts:", length(unique(sm$accession)), "\n")
## cross-cohort duplicate check at sample-ID and patient-ID level
dup_s <- sm %>% group_by(sample_id) %>% summarise(n_cohorts=n_distinct(accession), cohorts=paste(unique(accession), collapse=";"), .groups="drop") %>% filter(n_cohorts>1)
dup_p <- sm %>% group_by(patient_id) %>% summarise(n_cohorts=n_distinct(accession), cohorts=paste(unique(accession), collapse=";"), .groups="drop") %>% filter(n_cohorts>1)
cat("sample IDs shared across cohorts:", nrow(dup_s), "| patient IDs shared across cohorts:", nrow(dup_p), "\n")
if (nrow(dup_p)) { print(head(as.data.frame(dup_p), 15), row.names=FALSE) }
## per-cohort summary with case/control and pairing
summ <- sm %>% group_by(accession) %>% summarise(n_assays=n(), n_samples=n_distinct(sample_id), n_patients=n_distinct(patient_id),
  n_case=sum(group=="Case", na.rm=TRUE), n_control=sum(group=="Control", na.rm=TRUE),
  patient_ids_available=as.integer(any(patient_id_available==1)),
  n_paired_patients=if (any(patient_id_available==1)) length(intersect(patient_id[group=="Case"], patient_id[group=="Control"])) else 0, platform=paste(unique(platform), collapse=";"), .groups="drop")
write.csv(summ, file.path(OUT,"v12_cohort_summary.csv"), row.names=FALSE)
cat("\n== cohort summary ==\n"); print(as.data.frame(summ), row.names=FALSE)
cat("\nTOTAL assays:", sum(summ$n_assays), "| unique samples:", n_distinct(sm$sample_id), "| unique patients:", n_distinct(sm$patient_id),
    "| paired-capable patients:", sum(summ$n_paired_patients), "\n")
write.csv(dup_s, file.path(OUT,"v12_duplicate_sample_ids.csv"), row.names=FALSE)
write.csv(dup_p, file.path(OUT,"v12_duplicate_patient_ids.csv"), row.names=FALSE)
