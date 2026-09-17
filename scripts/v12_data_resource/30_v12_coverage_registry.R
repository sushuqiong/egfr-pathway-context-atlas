#!/usr/bin/env Rscript
# v12: per-cohort gene coverage report (platform x module) and cohort/sample registry with dedup checks
suppressPackageStartupMessages({library(dplyr)})
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
OUT <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"; dir.create(OUT, recursive=TRUE, showWarnings=FALSE)
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
mods <- split(toupper(gs$gene), gs$module)
files <- unlist(lapply(ROOTS, function(d) list.files(d, pattern="_processed\\.rds$", full.names=TRUE)))
cat("cohorts:", length(files), "\n")
cov_rows <- list(); reg_rows <- list()
for (f in files) {
  acc <- sub("_processed\\.rds$", "", basename(f))
  obj <- readRDS(f)
  ex <- obj$gene_expression; md <- obj$sample_metadata
  genes <- toupper(rownames(ex))
  n_smp <- ncol(ex)
  for (m in names(mods)) {
    need <- mods[[m]]; present <- intersect(need, genes)
    cov_rows[[length(cov_rows)+1]] <- data.frame(accession=acc, module=m, n_members=length(need),
      n_present=length(present), coverage=round(length(present)/length(need), 3),
      missing=paste(setdiff(need, present), collapse=";"), stringsAsFactors=FALSE)
  }
  grp <- if ("group" %in% names(md)) as.character(md$group) else NA
  sid <- if ("sample_id" %in% names(md)) as.character(md$sample_id) else colnames(ex)
  pid <- if ("patient_id" %in% names(md)) as.character(md$patient_id) else sid
  reg_rows[[length(reg_rows)+1]] <- data.frame(accession=acc, n_assay_records=n_smp,
    n_unique_samples=length(unique(sid)), n_unique_patients=length(unique(pid)),
    n_case=if(all(is.na(grp))) NA else sum(grp=="Case"), n_control=if(all(is.na(grp))) NA else sum(grp=="Control"),
    n_genes=length(genes), platform=if ("platform" %in% names(md)) paste(unique(md$platform), collapse=";") else NA,
    paired=if ("patient_id" %in% names(md)) length(intersect(pid[grp=="Case"], pid[grp=="Control"])) else NA,
    example_sample_ids=paste(head(sid,3), collapse=";"), stringsAsFactors=FALSE)
}
cv <- bind_rows(cov_rows); rg <- bind_rows(reg_rows)
write.csv(cv, file.path(OUT,"v12_gene_coverage.csv"), row.names=FALSE)
write.csv(rg, file.path(OUT,"v12_cohort_registry.csv"), row.names=FALSE)
cat("\n== coverage summary (modules with members missing in >=1 cohort) ==\n")
bad <- cv %>% filter(n_present < n_members) %>% group_by(module) %>% summarise(cohorts_incomplete=n(), min_cov=min(coverage), .groups="drop") %>% arrange(min_cov)
print(as.data.frame(head(bad, 25)), row.names=FALSE)
cat("\n== registry ==\n"); print(as.data.frame(rg), row.names=FALSE)
cat("\ntotal assays:", sum(rg$n_assay_records), "| total unique patients:", sum(rg$n_unique_patients), "\n")
