#!/usr/bin/env Rscript
# v12 integrity audit A: full sample-ID export, cross-cohort duplicate detection,
# patient-identity availability and paired-design verification (vs the hardcoded paired list).
suppressPackageStartupMessages({library(dplyr)})
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
R <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
paired_hardcoded <- c("GSE32863","GSE19804","GSE10072","GSE44076","GSE27342","GSE63089","GSE15471","GSE28735",
                      "GSE62452","GSE57957","GSE23400","GSE20347")
files <- unlist(lapply(ROOTS, function(d) list.files(d, pattern="_processed\\.rds$", full.names=TRUE)))
all <- list(); aud <- list()
for (f in files) {
  acc <- sub("_processed\\.rds$", "", basename(f)); obj <- readRDS(f)
  md <- obj$sample_metadata; ex <- obj$gene_expression
  sid <- if ("sample_id" %in% names(md)) as.character(md$sample_id) else colnames(ex)
  has_pid <- "patient_id" %in% names(md)
  pid <- if (has_pid) as.character(md$patient_id) else rep(NA_character_, length(sid))
  grp <- if ("group" %in% names(md)) as.character(md$group) else rep(NA_character_, length(sid))
  all[[length(all)+1]] <- data.frame(accession=acc, sample_id=sid, patient_id=pid, group=grp, stringsAsFactors=FALSE)
  n_uniq_pid <- length(unique(pid[!is.na(pid) & pid!=""]))
  pid_missing <- sum(is.na(pid) | pid=="")
  pid_constant <- n_uniq_pid == 1 && length(sid) > 1
  both <- if (!pid_missing && !pid_constant) length(intersect(pid[grp=="Case"], pid[grp=="Control"])) else NA_integer_
  aud[[length(aud)+1]] <- data.frame(accession=acc, n_samples=length(sid), n_unique_sample_id=length(unique(sid)),
    patient_id_present=has_pid, n_unique_patient_id=n_uniq_pid, patient_id_missing=pid_missing,
    patient_id_constant=pid_constant, patients_with_both_arms=both,
    hardcoded_as_paired=acc %in% paired_hardcoded,
    case=sum(grp=="Case", na.rm=TRUE), control=sum(grp=="Control", na.rm=TRUE), group_na=sum(is.na(grp)),
    stringsAsFactors=FALSE)
  cat(sprintf("[%s] samples=%d uniq_pid=%d both_arms=%s hardcoded_paired=%s\n", acc, length(sid), n_uniq_pid,
              ifelse(is.na(both),"NA",both), acc %in% paired_hardcoded))
}
A <- bind_rows(all); B <- bind_rows(aud)
write.csv(A, file.path(R,"v12_sample_ids_all.csv"), row.names=FALSE)
B$paired_mismatch <- B$hardcoded_as_paired != (!is.na(B$patients_with_both_arms) & B$patients_with_both_arms >= 4)
write.csv(B, file.path(R,"v12_dedup_patient_audit.csv"), row.names=FALSE)
cat("\n== cross-cohort duplicate sample IDs ==\n")
tab <- table(A$sample_id); dup <- names(tab[tab>1])
cat("duplicated sample IDs across cohorts:", length(dup), "\n")
if (length(dup)) print(A[A$sample_id %in% dup, ] %>% arrange(sample_id) %>% head(20))
cat("\n== cohorts where patient identity is unavailable or constant ==\n")
print(B[!B$patient_id_present | B$patient_id_constant, c("accession","n_samples","n_unique_patient_id","patient_id_constant","hardcoded_as_paired")], row.names=FALSE)
cat("\n== PAIRED-FLAG MISMATCHES (hardcoded vs metadata) ==\n")
mm <- B[B$paired_mismatch %in% TRUE, c("accession","n_samples","n_unique_patient_id","patients_with_both_arms","hardcoded_as_paired","case","control")]
print(mm, row.names=FALSE)
cat("\ntotal sample rows:", nrow(A), "| cohorts:", nrow(B), "| mismatches:", sum(B$paired_mismatch %in% TRUE), "\n")
