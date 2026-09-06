#!/usr/bin/env Rscript
# xCell-based composition adjustment: replace marker proxies with xCell deconvoluted
# tissue composition (epithelial, fibroblast, endothelial, immune) and re-test module SMDs.
suppressPackageStartupMessages({
  library(Biobase); library(GSVA); library(limma); library(dplyr); library(xCell)
})
ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
RES <- file.path(ROOT, "results"); dir.create(file.path(RES, "xcell"), showWarnings=FALSE)
V1P <- "C:/Users/fengq/Desktop/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk"
V2P <- "C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk"
V3P <- "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk"
rd <- function(f) read.csv(f, stringsAsFactors=FALSE, check.names=FALSE, fileEncoding="UTF-8-BOM")

cohorts <- data.frame(
 accession = c("GSE32863","GSE19804","GSE10072","GSE44076","GSE41258","GSE23878",
               "GSE75214","GSE87473","GSE179285","GSE16879","GSE4302","GSE43696","GSE67472",
               "GSE27342","GSE63089","GSE13911","GSE15471","GSE28735","GSE62452","GSE57957",
               "GSE62232","GSE23400","GSE20347","GSE76925","GSE47460","GSE33814","GSE66676"),
 disease = c(rep("LUAD",3), rep("CRC",3), rep("IBD",4), rep("Asthma",3), rep("STAD",3),
             rep("PAAD",3), rep("HCC",2), rep("ESCC",2), rep("COPD",2), rep("NAFLD",2)),
 role = c("discovery","validation","validation","discovery","validation","validation",
          "discovery","validation","validation","secondary_treatment_response",
          "discovery","validation","validation","discovery","validation","validation",
          "discovery","validation","validation","discovery","validation",
          "discovery","validation","discovery","validation","discovery","validation"),
 stringsAsFactors=FALSE)
paired_acc <- c("GSE32863","GSE19804","GSE10072","GSE44076","GSE27342","GSE63089",
                "GSE15471","GSE28735","GSE62452","GSE57957","GSE23400","GSE20347")
gs <- rd(file.path(ROOT, "config/gene_sets_extended.csv"))
gene_sets <- lapply(split(toupper(gs$gene), gs$module), unique)

locate <- function(acc) for (d in c(V2P,V3P,V1P)) { f <- list.files(d, pattern=paste0("^",acc,"_processed\\.rds$"), full.names=TRUE); if (length(f)) return(f[1]) }
std_effect <- function(x, meta, pos, ref, paired) {
  if (paired) { pv <- x[meta$group==pos]; rv <- x[meta$group==ref]
    pid <- meta$patient_id[meta$group==pos]; rid <- meta$patient_id[meta$group==ref]
    cm <- intersect(pid, rid); d <- pv[match(cm,pid)] - rv[match(cm,rid)]
    if (length(d)>1 && sd(d)>0) mean(d)/sd(d) else NA_real_
  } else { a <- x[meta$group==pos]; b <- x[meta$group==ref]
    n1 <- length(a); n0 <- length(b); pool <- sqrt(((n1-1)*var(a)+(n0-1)*var(b))/(n1+n0-2))
    if (is.finite(pool) && pool>0) (1-3/(4*(n1+n0)-9))*(mean(a)-mean(b))/pool else NA_real_ } }
p_effect <- function(x, meta, pos, ref, paired) {
  if (paired) { pv <- x[meta$group==pos]; rv <- x[meta$group==ref]
    pid <- meta$patient_id[meta$group==pos]; rid <- meta$patient_id[meta$group==ref]
    cm <- intersect(pid, rid); d <- pv[match(cm,pid)] - rv[match(cm,rid)]
    tryCatch(t.test(d)$p.value, error=function(e) NA_real_) }
  else tryCatch(t.test(x[meta$group==pos], x[meta$group==ref])$p.value, error=function(e) NA_real_) }

adj_rows <- list(); comp_rows <- list()
for (i in seq_len(nrow(cohorts))) {
  acc <- cohorts$accession[i]
  rds <- locate(acc)
  if (is.na(rds)) { message("[MISS] ", acc); next }
  obj <- readRDS(rds); expr <- obj$gene_expression; meta <- obj$sample_metadata
  if (!all(c("group","sample_id") %in% names(meta))) { message("[SKIP] ", acc); next }
  if (!all(c("Case","Control") %in% meta$group)) { message("[SKIP groups] ", acc); next }
  meta$age <- suppressWarnings(as.numeric(meta$age))
  pos <- "Case"; ref <- "Control"; paired <- acc %in% paired_acc
  expr <- expr[, match(meta$sample_id, colnames(expr)), drop=FALSE]
  # xCell composition (log2-free safe: pass matrix as-is; xCell handles microarray-style)
  xc <- tryCatch(xCellAnalysis(expr, rnaseq = FALSE, parallel.sz = 1),
                 error = function(e) { message("[xCell err] ", acc, ": ", conditionMessage(e)); NULL })
  if (is.null(xc) || nrow(xc) < 5) { message("[SKIP xcell] ", acc); next }
  xc <- as.data.frame(xc)  # rows = cell types, columns = samples (same order as expr)
  rn <- rownames(xc)
  pick_exact <- function(name) { if (name %in% rn) as.numeric(xc[name, ]) else NULL }
  pick_regex <- function(pat) { h <- grep(pat, rn, ignore.case=TRUE); if (length(h)) as.numeric(xc[h[1], ]) else NULL }
  comp_mat <- data.frame(epi = pick_exact("Epithelial cells"))
  fib <- pick_exact("Fibroblasts"); if (!is.null(fib)) comp_mat$fib <- fib
  end <- pick_exact("Endothelial cells"); if (is.null(end)) end <- pick_regex("^Endothelial cells$")
  if (!is.null(end)) comp_mat$end <- end
  imm <- pick_exact("ImmuneScore"); if (!is.null(imm)) comp_mat$imm <- imm
  if (ncol(comp_mat) < 2) { message("[SKIP comp] ", acc); next }
  comp_mat <- comp_mat[seq_len(nrow(meta)), , drop = FALSE]
  comp_rows[[length(comp_rows)+1]] <- data.frame(accession = acc, disease = cohorts$disease[i],
      comp_mat, check.names = FALSE, stringsAsFactors = FALSE)
  # GSVA module scores
  present <- lapply(gene_sets, function(g) intersect(g, rownames(expr)))
  usable <- names(present)[lengths(present) >= 3]
  if (!length(usable)) next
  sc <- GSVA::gsva(GSVA::gsvaParam(expr, gene_sets[usable], minSize=3, maxSize=Inf, kcdf="Gaussian"), verbose=FALSE)
  rownames(sc) <- usable
  # residualize on xCell comps
  cmat <- as.data.frame(comp_mat)
  adj <- t(apply(sc, 1, function(row) residuals(stats::lm(row ~ ., data=cmat))))
  for (m in rownames(adj)) {
    smd <- std_effect(adj[m,], meta, pos, ref, paired); pv <- p_effect(adj[m,], meta, pos, ref, paired)
    adj_rows[[length(adj_rows)+1]] <- data.frame(accession=acc, disease=cohorts$disease[i],
      role=cohorts$role[i], feature=m, smd=smd, p_value=pv, stringsAsFactors=FALSE)
  }
  message("[OK] ", acc)
}
if (length(adj_rows)) {
  a <- do.call(rbind, adj_rows)
  a <- a[!is.na(a$p_value), ]
  a$fdr <- ave(a$p_value, a$accession, FUN=function(x) p.adjust(x, "BH"))
  write.csv(a, file.path(RES, "xcell", "module_effects_composition_adjusted_xcell.csv"), row.names=FALSE)
  main <- a[a$role %in% c("discovery","validation"), ]
  sumx <- main %>% group_by(disease, feature) %>% summarise(
    n=sum(is.finite(smd)), positive=sum(smd>0, na.rm=TRUE), negative=sum(smd<0, na.rm=TRUE),
    n_fdr_adj=sum(fdr<0.05, na.rm=TRUE), median_smd=median(smd, na.rm=TRUE), .groups="drop") %>%
    mutate(consistency = pmax(positive, negative)/n, robust_xcell = consistency >= 2/3 & n_fdr_adj >= 2)
  write.csv(as.data.frame(sumx), file.path(RES, "xcell", "context_atlas_summary_xcell_adjusted.csv"), row.names=FALSE)
  cat("adjusted rows:", nrow(a), " robust_xcell:", sum(sumx$robust_xcell), "\n")
  print(table(sumx$disease[sumx$robust_xcell]))
}
if (length(comp_rows)) write.csv(bind_rows(comp_rows), file.path(RES, "xcell", "xcell_composition_scores.csv"), row.names=FALSE)
cat("done\n")
