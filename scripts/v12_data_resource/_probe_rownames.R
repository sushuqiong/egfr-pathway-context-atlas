roots <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
out <- data.frame()
for (r in roots) {
  fs <- list.files(r, pattern="_processed\\.rds$", full.names=TRUE)
  for (f in fs) {
    o <- readRDS(f); rn <- toupper(rownames(o$gene_expression))
    out <- rbind(out, data.frame(acc=sub("_processed\\.rds$","",basename(f)), n_genes=length(rn),
      symbol_like=any(rn %in% c("EGFR","TP53","ACTB")), head1=head(rn,1), stringsAsFactors=FALSE))
  }
}
print(out, row.names=FALSE)
cat("\ncohorts with gene-symbol rownames:", paste(out$acc[out$symbol_like], collapse=", "), "\n")
