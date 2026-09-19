#!/usr/bin/env Rscript
# v14 external reuse example: take a gastric cohort that is NOT part of the resource, rebuild module scores
# from its public accession, compare effect directions with the resource's pooled gastric estimates,
# and record the wall-clock runtime of the whole path.
suppressPackageStartupMessages({library(GEOquery); library(GSVA); library(limma); library(dplyr)})
V14 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v14"; PK <- file.path(V14,"dataset_package")
t0 <- Sys.time()
ACC <- "GSE54129"   # gastric cancer with adjacent normal tissue; not among the 26 curated cohorts
cat("== external reuse example:", ACC, "==\n")
gs <- read.csv(file.path(PK,"04_modules","module_definitions.csv"), stringsAsFactors=FALSE)
sets <- lapply(split(toupper(gs$gene), gs$module), unique)
gse <- getGEO(ACC, GSEMatrix=TRUE, getGPL=TRUE, destdir=tempdir())
eset <- gse[[1]]
expr <- Biobase::exprs(eset); fd <- Biobase::fData(eset); pd <- Biobase::pData(eset)
cat("downloaded:", nrow(expr), "probes x", ncol(expr), "samples\n")
sym_col <- intersect(c("Gene symbol","Gene Symbol","GENE_SYMBOL","Symbol","gene_assignment","ORF","ILMN_Gene"), names(fd))[1]
if (is.na(sym_col)) {   # fall back to the platform annotation table
  gpl_acc <- Biobase::annotation(eset)
  gpl <- tryCatch(GEOquery::getGEO(gpl_acc), error=function(e) NULL)
  if (!is.null(gpl)) { tab <- GEOquery::Table(gpl)
    cand <- intersect(c("Gene symbol","Gene Symbol","GENE_SYMBOL","Symbol","gene_assignment"), names(tab))
    if (length(cand)) { fd <- data.frame(row.names=as.character(tab), sym=as.character(tab[[cand[1]]])); sym_col <- "sym" } }
}
cat("annotation columns available:", paste(head(names(fd),12), collapse=", "), "| using:", ifelse(is.na(sym_col),"NONE",sym_col), "
")
sym <- toupper(as.character(fd[[sym_col]])); sym <- sub(" ?//.*$","",sym)
keep <- !is.na(sym) & sym!="" & sym!="NA" & !grepl("^---", sym)
expr <- expr[keep,,drop=FALSE]; rownames(expr) <- sym[keep]
expr <- limma::avereps(expr, ID=rownames(expr))
cat("after mapping to symbols:", nrow(expr), "genes\n")
# deterministic transformation rule (same as the resource)
v <- as.numeric(expr[1:min(2000,nrow(expr)), 1:min(5,ncol(expr))])
frac_int <- mean(abs(v-round(v))<1e-8, na.rm=TRUE); mx <- max(v, na.rm=TRUE)
logged <- frac_int>0.90 && mx>50
if (!logged) expr <- log2(expr+1)
cat(sprintf("integer fraction %.3f, input max %.2f -> log2 applied: %s\n", frac_int, mx, !logged))
# group labels from the series metadata (title text of each sample)
txt <- tolower(paste(pd$title, pd$source_name_ch1, pd$characteristics_ch1))
grp <- ifelse(grepl("normal|adjacent|non-?tumou?r|healthy", txt), "Control",
       ifelse(grepl("tumou?r|cancer|carcinoma|adenocarcinoma", txt), "Case", NA))
cat("group labels from metadata: Case", sum(grp=="Case", na.rm=TRUE), "| Control", sum(grp=="Control", na.rm=TRUE),
    "| unassigned", sum(is.na(grp)), "\n")
if (sum(grp=="Control", na.rm=TRUE) < 5) { cat("!! fewer than five control samples: this series cannot serve as an external control cohort\n") }
usable <- names(sets)[sapply(sets, function(g) length(intersect(g, rownames(expr))) >= 3)]
sc <- GSVA::gsva(GSVA::gsvaParam(expr, sets[usable], minSize=3, kcdf="Gaussian"), verbose=FALSE)
z <- t(scale(t(sc)))
eff <- data.frame()
for (m in rownames(z)) {
  y <- as.numeric(z[m,]); a <- y[grp=="Case"]; b <- y[grp=="Control"]
  if (length(a)<3 || length(b)<3) next
  e <- metafor::escalc(measure="SMDH", m1i=mean(a), sd1i=sd(a), n1i=length(a), m2i=mean(b), sd2i=sd(b), n2i=length(b))
  eff <- rbind(eff, data.frame(module=m, n_case=length(a), n_control=length(b), yi=as.numeric(e$yi), vi=as.numeric(e$vi)))
}
pooled <- read.csv(file.path(PK,"07_estimates","meta_primary_reml_knha.csv"), stringsAsFactors=FALSE) %>%
  filter(disease=="STAD")
cmp <- merge(eff, pooled[,c("feature","est","k","fdr")], by.x="module", by.y="feature", all.x=TRUE)
cmp$direction_external <- ifelse(cmp$yi>0,"positive","negative")
cmp$direction_resource <- ifelse(is.na(cmp$est), NA, ifelse(cmp$est>0,"positive","negative"))
cmp$direction_agrees <- ifelse(is.na(cmp$direction_resource), NA, cmp$direction_external==cmp$direction_resource)
write.csv(cmp, file.path(PK,"09_reuse_examples","example3_external_cohort_rebuild.csv"), row.names=FALSE)
runtime <- as.numeric(difftime(Sys.time(), t0, units="mins"))
writeLines(c(sprintf("external cohort: %s", ACC),
             sprintf("samples: %d case / %d control", sum(grp=="Case",na.rm=TRUE), sum(grp=="Control",na.rm=TRUE)),
             sprintf("modules scored: %d", length(usable)),
             sprintf("modules with a comparable resource estimate: %d", sum(!is.na(cmp$direction_resource))),
             sprintf("direction agreement: %d of %d", sum(cmp$direction_agrees, na.rm=TRUE), sum(!is.na(cmp$direction_agrees))),
             sprintf("wall-clock runtime: %.1f minutes", runtime)),
           file.path(PK,"09_reuse_examples","example3_external_cohort_summary.txt"))
cat("\n== comparison with the resource's pooled gastric estimates ==\n")
print(cmp %>% select(module, yi, est, direction_external, direction_resource, direction_agrees), row.names=FALSE, digits=3)
cat(sprintf("\nagreement: %d of %d modules share the effect direction (%.0f%%)\n",
    sum(cmp$direction_agrees, na.rm=TRUE), sum(!is.na(cmp$direction_agrees)),
    100*sum(cmp$direction_agrees, na.rm=TRUE)/max(1,sum(!is.na(cmp$direction_agrees)))))
cat(sprintf("total wall-clock runtime: %.1f minutes\n", runtime))
