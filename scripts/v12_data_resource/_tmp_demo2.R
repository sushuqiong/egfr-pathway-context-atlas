suppressPackageStartupMessages(library(dplyr))
roots <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
f <- unlist(lapply(roots, function(d) list.files(d, pattern="GSE13911_processed[.]rds$", full.names=TRUE)))[1]
cat("using", f, "
")
o <- readRDS(f)
ex <- o$gene_expression; md <- o$sample_metadata
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
members <- unique(toupper(gs$gene))
v <- apply(log2(ex + 1), 1, var, na.rm = TRUE)
top <- names(sort(v, decreasing = TRUE))[1:1200]
keep <- unique(c(top, intersect(members, toupper(rownames(ex)))))
sub <- ex[rownames(ex) %in% keep, 1:min(20, ncol(ex))]
sub <- round(log2(sub + 1), 4)
write.csv(sub, "dataset_package/09_reuse_examples/example_input/demo_expression_matrix.csv")
meta <- data.frame(sample_id = colnames(sub), group = as.character(md$group[1:ncol(sub)]))
write.csv(meta, "dataset_package/09_reuse_examples/example_input/demo_sample_metadata.csv", row.names = FALSE)
m <- intersect(members, toupper(rownames(sub)))
cat("demo matrix:", nrow(sub), "genes x", ncol(sub), "samples | module members present:", length(m), "of", length(members), "\n")
cat("ERBB_RECEPTORS members present:", sum(c("EGFR","ERBB2","ERBB3","ERBB4") %in% toupper(rownames(sub))), "of 4\n")
