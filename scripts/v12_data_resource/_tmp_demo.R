
suppressPackageStartupMessages({library(dplyr)})
o <- readRDS("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk/GSE13911_processed.rds")
ex <- o$gene_expression; md <- o$sample_metadata
v <- apply(log2(ex+1), 1, var, na.rm=TRUE)
keep <- names(sort(v, decreasing=TRUE))[1:1500]
sub <- ex[keep, 1:min(20, ncol(ex))]
sub <- round(log2(sub+1), 4)
write.csv(sub, "09_reuse_examples/example_input/demo_expression_matrix.csv")
meta <- data.frame(sample_id=colnames(sub), group=as.character(md$group[1:ncol(sub)]))
write.csv(meta, "09_reuse_examples/example_input/demo_sample_metadata.csv", row.names=FALSE)
cat("demo matrix:", nrow(sub), "genes x", ncol(sub), "samples\n")
