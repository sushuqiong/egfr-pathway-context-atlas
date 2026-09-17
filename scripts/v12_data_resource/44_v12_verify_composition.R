#!/usr/bin/env Rscript
# v12 adversarial checkpoint: independently recompute xCell adjusted ES for two cohorts using xCellAnalysis()
# and compare the four shipped compartments (epi = Epithelial cells, fib = Fibroblasts,
# end = Endothelial cells, imm = ImmuneScore) with the shipped per-sample table.
suppressPackageStartupMessages({library(xCell); library(dplyr)})
R <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
PK <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/dataset_package"
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
shipped <- read.csv(file.path(PK,"05_composition","composition_scores_per_sample.csv"), stringsAsFactors=FALSE)
out <- list()
for (acc in c("GSE13911","GSE32863","GSE44076")) {
  f <- unlist(lapply(ROOTS, function(d) list.files(d, pattern=paste0("^",acc,"_processed[.]rds$"), full.names=TRUE)))[1]
  if (is.na(f)) { cat("[MISS]", acc, "\n"); next }
  ex <- readRDS(f)$gene_expression; rownames(ex) <- toupper(rownames(ex))
  ex <- ex[!duplicated(rownames(ex)), , drop=FALSE]
  sc <- tryCatch(xCell::xCellAnalysis(as.matrix(ex)), error=function(e) { cat("[ERR]", acc, conditionMessage(e), "\n"); NULL })
  if (is.null(sc)) next
  need <- c(epi="Epithelial cells", fib="Fibroblasts", end="Endothelial cells", imm="ImmuneScore")
  have <- intersect(need, rownames(sc))
  if (length(have) < 4) { cat("[WARN] missing rows for", acc, ":", setdiff(need, rownames(sc)), "\n") }
  rec <- as.data.frame(t(sc[have, , drop=FALSE]))
  names(rec) <- paste0(names(need)[match(have, need)], "_re")
  rec$sample_id <- rownames(rec)
  sh <- shipped[shipped$accession==acc, c("sample_id","epi","fib","end","imm")]
  m <- merge(rec, sh, by="sample_id")
  for (p in c("epi","fib","end","imm")) {
    if (!paste0(p,"_re") %in% names(m)) { out[[length(out)+1]] <- data.frame(accession=acc, compartment=p, n=nrow(m), spearman=NA, pearson=NA); next }
    out[[length(out)+1]] <- data.frame(accession=acc, compartment=p, n=nrow(m),
      spearman=round(suppressWarnings(cor(m[[paste0(p,"_re")]], m[[p]], method="spearman")), 3),
      pearson=round(suppressWarnings(cor(m[[paste0(p,"_re")]], m[[p]])), 3), stringsAsFactors=FALSE)
  }
  cat("[OK]", acc, "recomputed and compared on", nrow(m), "samples\n")
}
res <- bind_rows(out)
write.csv(res, file.path(R,"v12_qc_xcell_recompute_verification.csv"), row.names=FALSE)
print(res, row.names=FALSE)
if (nrow(res)) cat("minimum Spearman across compartments/cohorts:", min(res$spearman, na.rm=TRUE), "\n")
