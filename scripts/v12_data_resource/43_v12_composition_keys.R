#!/usr/bin/env Rscript
# v12: rebuild the per-sample composition table WITH explicit sample identifiers and a join-status audit.
# The original composition table stored only (accession, disease, epi, fib, end, imm) in cohort order;
# this script joins it to the cohort sample metadata by position (reproducing the original analysis order)
# and records whether the join is complete, so that downstream users have an explicit key.
suppressPackageStartupMessages({library(dplyr)})
A <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
R <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
PK <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/dataset_package"
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
x <- read.csv(file.path(A,"results","xcell","xcell_composition_scores.csv"), stringsAsFactors=FALSE)
out <- list(); aud <- list()
for (acc in unique(x$accession)) {
  f <- unlist(lapply(ROOTS, function(d) list.files(d, pattern=paste0("^",acc,"_processed[.]rds$"), full.names=TRUE)))[1]
  s <- x[x$accession==acc, ]
  if (is.na(f)) { aud[[length(aud)+1]] <- data.frame(accession=acc, n_comp=nrow(s), n_samples=NA, join="cohort object not found", stringsAsFactors=FALSE); next }
  md <- readRDS(f)$sample_metadata
  sid <- if ("sample_id" %in% names(md)) as.character(md$sample_id) else NA_character_
  grp <- if ("group" %in% names(md)) as.character(md$group) else NA_character_
  ok <- !is.na(sid[1]) && length(sid) == nrow(s)
  aud[[length(aud)+1]] <- data.frame(accession=acc, n_comp=nrow(s), n_samples=length(sid),
    join=ifelse(ok, "by position (documented)", "count mismatch: identifiers not assigned"), stringsAsFactors=FALSE)
  if (!ok) next
  out[[length(out)+1]] <- data.frame(accession=acc, sample_id=sid, group=grp,
    epi=s$epi, fib=s$fib, end=s$end, imm=s$imm, stringsAsFactors=FALSE)
}
comp <- bind_rows(out); audit <- bind_rows(aud)
write.csv(comp, file.path(PK,"05_composition","composition_scores_per_sample.csv"), row.names=FALSE)
write.csv(audit, file.path(R,"v12_qc_composition_join_audit.csv"), row.names=FALSE)
cat("composition rows with identifiers:", nrow(comp), "of", nrow(x), "\n")
print(audit, row.names=FALSE)
## collinearity with disease status, now using the keyed table
clin <- read.csv(file.path(R,"v12_sample_ids_all.csv"), stringsAsFactors=FALSE)
m <- merge(comp, clin[, c("accession","sample_id","group")], by=c("accession","sample_id"), suffixes=c("",".md"))
diag <- list()
for (acc in unique(m$accession)) {
  s <- m[m$accession==acc, ]; s$case <- as.integer(s$group %in% c("Case"))
  dd <- s[, c("case","epi","fib","end","imm")]; dd <- dd[complete.cases(dd), ]
  if (nrow(dd) < 12 || length(unique(dd$case)) < 2) next
  r2 <- summary(lm(case ~ epi + fib + end + imm, data=dd))$r.squared
  vif <- tryCatch(max(diag(solve(cor(dd[, c("epi","fib","end","imm")])))), error=function(e) NA_real_)
  diag[[length(diag)+1]] <- data.frame(accession=acc, n=nrow(dd), r2_disease_on_composition=r2, max_vif=vif, stringsAsFactors=FALSE)
}
D <- bind_rows(diag)
write.csv(D, file.path(R,"v12_qc_composition_collinearity.csv"), row.names=FALSE)
if (nrow(D)) cat(sprintf("collinearity: cohorts=%d | median R2=%.3f | max R2=%.3f | median max-VIF=%.2f\n",
   nrow(D), median(D$r2_disease_on_composition, na.rm=TRUE), max(D$r2_disease_on_composition, na.rm=TRUE), median(D$max_vif, na.rm=TRUE)))
