#!/usr/bin/env Rscript
# Reproducibility checks for the paired-effect implementation (GPT6 item 8)
# 1) hand calculation vs metafor SMCRH  2) sample-order shuffle via ID join  3) double-run stability
suppressPackageStartupMessages({library(GSVA); library(metafor)})
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",  # edit to your paths
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR\u80c3\u764c/EGFR_ERBB_context_project_v1/data_processed/bulk")
gs <- read.csv("config/gene_sets_extended.csv", stringsAsFactors=FALSE)   # repo-relative
mods <- lapply(split(toupper(gs$gene), gs$module), unique)
acc <- "GSE44076"; feat <- "WNT_CTNNB1"
locate <- function(a) for (d in ROOTS) { f <- list.files(d, pattern=paste0("^",a,"_processed\\.rds$"), full.names=TRUE); if(length(f)) return(f[1]) }
obj <- readRDS(locate(acc)); e <- obj$gene_expression; m <- obj$sample_metadata
e <- e[, match(m$sample_id, colnames(e)), drop=FALSE]
pid <- as.character(m$patient_id); grp <- factor(m$group, levels=c("Control","Case"))
score <- function(expr){ as.numeric(GSVA::gsva(GSVA::gsvaParam(expr, setNames(list(intersect(mods[[feat]], rownames(expr))), feat), minSize=3, kcdf="Gaussian"), verbose=FALSE)[1,]) }

run <- function(expr, meta_order=NULL){
  y <- score(expr)
  if(!is.null(meta_order)){ y <- y[match(meta_order, colnames(expr))]; p <- pid[match(meta_order, m$sample_id)]; g <- grp[match(meta_order, m$sample_id)]
  } else { p <- pid; g <- grp }
  cc <- intersect(p[g=="Case"], p[g=="Control"])
  yc <- y[match(cc, p[g=="Case"])]; yr <- y[match(cc, p[g=="Control"])]
  ri <- cor(yc, yr)
  es <- metafor::escalc(measure="SMCRH", m1i=mean(yc), m2i=mean(yr), sd1i=sd(yc), sd2i=sd(yr), ri=ri, ni=length(cc))
  hand <- (mean(yc)-mean(yr))/sqrt((var(yc)+var(yr))/2)
  c(yi=as.numeric(es$yi), vi=as.numeric(es$vi), ri=ri, dz=mean(yc-yr)/sd(yc-yr), hand=hand, n=length(cc))
}
a <- run(e)
cat(sprintf("[1] %s %s: yi=%.4f vi=%.6f ri=%.4f dz=%.4f hand(naive)=%.4f n=%d\n", acc, feat, a["yi"],a["vi"],a["ri"],a["dz"],a["hand"],a["n"]))
# shuffle columns
set.seed(1); perm <- sample(colnames(e))
b <- run(e[, perm], meta_order=colnames(e[, perm]))
cat(sprintf("[2] shuffled order: yi=%.4f vi=%.6f ri=%.4f  | identical to [1]: %s\n", b["yi"],b["vi"],b["ri"],
            isTRUE(all.equal(unname(a[c("yi","vi","ri")]), unname(b[c("yi","vi","ri")])))))
c2 <- run(e)
cat(sprintf("[3] repeat run: yi=%.4f vi=%.6f  | identical: %s\n", c2["yi"],c2["vi"], isTRUE(all.equal(unname(a[c("yi","vi")]),unname(c2[c("yi","vi")])))))
