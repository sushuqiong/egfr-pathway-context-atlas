#!/usr/bin/env Rscript
# v12: prepare a small self-contained demo dataset for the reuse examples (clean-room test)
suppressPackageStartupMessages({library(dplyr)})
OUT <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/01_数据包/08_reproduction"
dir.create(OUT, recursive=TRUE, showWarnings=FALSE)
rds <- (function(){
  cands <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk/GSE44076_processed.rds",
             "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk/GSE44076_processed.rds",
             "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk/GSE44076_processed.rds")
  hit <- cands[file.exists(cands)]; if(!length(hit)) stop("GSE44076_processed.rds not found"); hit[1] })()
obj <- readRDS(rds); ex <- obj$gene_expression; md <- obj$sample_metadata
set.seed(11)
grp <- as.character(md$group); sel_case <- sample(which(grp=="Case"), 20); sel_ctrl <- sample(which(grp=="Control"), 20)
sel <- c(sel_case, sel_ctrl)
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
keep_mods <- c("WNT_CTNNB1","EPH_RECEPTORS","VEGF_PDGF_AXIS","ERBB_RECEPTORS")
mod_genes <- unique(toupper(gs$gene[gs$module %in% keep_mods]))
mod_genes <- intersect(mod_genes, toupper(rownames(ex)))
extra <- setdiff(toupper(rownames(ex)), mod_genes)[1:400]
sel_genes <- c(mod_genes, extra)
demo <- ex[match(sel_genes, toupper(rownames(ex))), sel, drop=FALSE]
rownames(demo) <- sel_genes
demo <- data.frame(gene_symbol=rownames(demo), demo, check.names=FALSE)
write.csv(demo, file.path(OUT,"demo_expression_matrix.csv"), row.names=FALSE)
ann <- data.frame(sample_id=colnames(ex)[sel], group=grp[sel],
                  tissue=if ("tissue" %in% names(md)) as.character(md$tissue)[sel] else "colon",
                  stringsAsFactors=FALSE)
write.csv(ann, file.path(OUT,"demo_sample_annotation.csv"), row.names=FALSE)
# demo composition scores (subset of xCell compartment scores if available, else simulated)
xc <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results/xcell/xcell_composition_scores.csv"
x <- read.csv(xc, stringsAsFactors=FALSE) %>% filter(accession=="GSE44076")
  x <- x[sel, c("epi","fib","end","imm")]                      # xCell block order matches the matrix column order
  x <- data.frame(sample_id=ann$sample_id, x, stringsAsFactors=FALSE)
write.csv(x, file.path(OUT,"demo_composition_scores.csv"), row.names=FALSE)
cat("demo data written:", nrow(demo)-0, "genes x", length(sel), "samples ->", OUT, "\n")
cat("module members included:", length(mod_genes), "| extra genes:", length(extra), "\n")
