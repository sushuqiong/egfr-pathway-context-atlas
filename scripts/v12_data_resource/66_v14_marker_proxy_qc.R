#!/usr/bin/env Rscript
# v14 analysis: (a) marker-proxy alternative composition scores (independent of the xCell panel),
# (b) per-cohort expression QC, (c) per-cohort transformation before/after summaries.
suppressPackageStartupMessages({library(dplyr)})
V14 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v14"; PK <- file.path(V14,"dataset_package"); R <- file.path(V14,"results")
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
CTX <- c(GSE32863="LUAD",GSE19804="LUAD",GSE10072="LUAD",GSE44076="CRC",GSE41258="CRC",GSE23878="CRC",
         GSE75214="IBD",GSE87473="IBD",GSE179285="IBD",GSE16879="IBD",GSE4302="Asthma",GSE43696="Asthma",
         GSE67472="Asthma",GSE27342="STAD",GSE63089="STAD",GSE13911="STAD",GSE15471="PAAD",GSE28735="PAAD",
         GSE62452="PAAD",GSE57957="HCC",GSE62232="HCC",GSE23400="ESCC",GSE20347="ESCC",GSE76925="COPD",
         GSE47460="COPD",GSE33814="NAFLD",GSE66676="NAFLD")
markers <- list(
  epithelial  = c("EPCAM","KRT18","KRT8","CDH1","KRT19"),
  fibroblast  = c("COL1A1","COL1A2","COL3A1","DCN","LUM","FAP"),
  endothelial = c("PECAM1","VWF","CDH5","CLDN5","KDR"),
  immune      = c("PTPRC","CD3D","CD3E","CD19","MS4A1","LYZ","CD68","NKG7"))
mods <- read.csv(file.path(PK,"04_modules","module_definitions.csv"), stringsAsFactors=FALSE)
module_genes <- unique(toupper(mods$gene))
comp <- list(); qc <- list(); tr <- list()
for (acc in names(CTX)) {
  f <- unlist(lapply(ROOTS, function(d) list.files(d, pattern=paste0("^",acc,"_processed[.]rds$"), full.names=TRUE)))[1]
  if (is.na(f)) next
  obj <- readRDS(f); ex <- obj$gene_expression; md <- obj$sample_metadata
  rn <- toupper(rownames(ex)); sid <- as.character(md$sample_id)
  raw_max <- suppressWarnings(max(as.numeric(ex[1:min(2000,nrow(ex)), 1:min(5,ncol(ex))]), na.rm=TRUE))
  frac_int <- mean(abs(as.numeric(ex[1:min(2000,nrow(ex)), 1:min(5,ncol(ex))]) - round(as.numeric(ex[1:min(2000,nrow(ex)), 1:min(5,ncol(ex))]))) < 1e-8, na.rm=TRUE)
  logged <- !(frac_int > 0.9 && raw_max > 50)
  # (b) expression QC
  sm <- colMeans(ex, na.rm=TRUE); smad <- mad(sm, na.rm=TRUE); med <- median(sm, na.rm=TRUE)
  outlier <- which(abs(sm - med) > 3*smad)
  qc[[length(qc)+1]] <- data.frame(accession=acc, context=CTX[[acc]], n_samples=ncol(ex), n_genes=nrow(ex),
     missing_fraction=round(mean(is.na(ex)),4), sample_mean_median=round(med,3), sample_mean_mad=round(smad,3),
     outlier_samples_3mad=length(outlier), outlier_flag=ifelse(length(outlier)>0, paste(sid[outlier], collapse=";"), ""),
     gene_sd_zero=sum(apply(ex,1,sd,na.rm=TRUE)==0, na.rm=TRUE), stringsAsFactors=FALSE)
  # (c) transformation summary
  v <- as.numeric(ex); tr[[length(tr)+1]] <- data.frame(accession=acc, log2_applied=!logged,
     input_max=round(raw_max,2), integer_fraction=round(frac_int,3),
     post_min=round(min(v,na.rm=TRUE),3), post_median=round(median(v,na.rm=TRUE),3), post_max=round(max(v,na.rm=TRUE),3),
     stringsAsFactors=FALSE)
  # (a) marker-proxy composition (mean of available marker genes, z across samples within cohort)
  pr <- list()
  for (cn in names(markers)) {
    gm <- intersect(markers[[cn]], rn)
    if (length(gm) < 2) next
    s <- colMeans(ex[match(gm, rn), , drop=FALSE], na.rm=TRUE)
    pr[[cn]] <- as.numeric(scale(s))
  }
  if (length(pr)) {
    comp[[length(comp)+1]] <- data.frame(accession=acc, context=CTX[[acc]], sample_id=sid,
        epi_proxy=if (!is.null(pr$epithelial)) pr$epithelial else NA_real_,
        fib_proxy=if (!is.null(pr$fibroblast)) pr$fibroblast else NA_real_,
        end_proxy=if (!is.null(pr$endothelial)) pr$endothelial else NA_real_,
        imm_proxy=if (!is.null(pr$immune)) pr$immune else NA_real_, stringsAsFactors=FALSE)
  }
  cat("[OK]", acc, "\n")
}
pcd <- bind_rows(comp); write.csv(pcd, file.path(PK,"05_composition","alternative_method_marker_proxy.csv"), row.names=FALSE)
qcd <- bind_rows(qc);  write.csv(qcd, file.path(PK,"08_qc","qc_expression_matrix_per_cohort.csv"), row.names=FALSE)
trd <- bind_rows(tr);  write.csv(trd, file.path(PK,"03_expression","transformation_summary_per_cohort.csv"), row.names=FALSE)
# agreement between the marker-proxy and the shipped xCell compartments
xcell <- read.csv(file.path(PK,"05_composition","xcell_composition_scores.csv"), stringsAsFactors=FALSE)
m <- merge(pcd, xcell[,c("accession","sample_id","epi","fib","end","imm")], by=c("accession","sample_id"))
ag <- data.frame()
for (p in c("epi","fib","end","imm")) {
  a <- suppressWarnings(cor(m[[paste0(p,"_proxy")]], m[[p]], method="spearman", use="complete.obs"))
  b <- suppressWarnings(cor(m[[paste0(p,"_proxy")]], m[[p]], use="complete.obs"))
  ag <- rbind(ag, data.frame(compartment=p, n=sum(complete.cases(m[[paste0(p,"_proxy")]], m[[p]])),
                             spearman_vs_xcell=round(a,3), pearson_vs_xcell=round(b,3)))
}
write.csv(ag, file.path(PK,"08_qc","qc_composition_method_agreement.csv"), row.names=FALSE)
overlap_marker <- length(intersect(unlist(markers), module_genes))
cat("\nmarker-proxy vs xCell agreement:\n"); print(ag, row.names=FALSE)
cat("marker genes that also occur in module definitions:", overlap_marker, "of", length(unique(unlist(markers))), "\n")
cat("cohorts with expression QC:", nrow(qcd), "| outlier samples total:", sum(qcd$outlier_samples_3mad), "\n")
