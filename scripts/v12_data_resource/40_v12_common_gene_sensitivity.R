#!/usr/bin/env Rscript
# v12: gene-coverage sensitivity — recompute per-cohort effects with the common (cross-cohort present) gene subset
# and compare with the full member-gene set. Addresses the concern that the same "module" can mean different
# gene sets on different platforms.
suppressPackageStartupMessages({library(dplyr)})
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
OUT <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
mods <- split(toupper(gs$gene), gs$module)
files <- unlist(lapply(ROOTS, function(d) list.files(d, pattern="_processed\\.rds$", full.names=TRUE)))
objs <- lapply(files, function(f) { o <- readRDS(f); list(acc=sub("_processed\\.rds$","",basename(f)), ex=o$gene_expression, md=o$sample_metadata) })
present <- lapply(objs, function(o) unique(toupper(rownames(o$ex))))
names(present) <- sapply(objs, function(o) o$acc)
zscore <- function(v){ s <- sd(v, na.rm=TRUE); if(!is.finite(s) || s==0) return(rep(NA_real_, length(v))); (v-mean(v,na.rm=TRUE))/s }
rows <- list(); summary_rows <- list()
for (m in names(mods)) {
  members <- mods[[m]]
  cov <- sapply(present, function(p) intersect(members, p))
  common <- Reduce(intersect, cov)
  if (length(common) < 2) { summary_rows[[length(summary_rows)+1]] <- data.frame(module=m, n_members=length(members), n_common=length(common), flag="insufficient common genes"); next }
  eff <- list()
  for (o in objs) {
    ex <- o$ex; md <- o$md
    grp <- if ("group" %in% names(md)) as.character(md$group) else rep(NA, ncol(ex))
    ids <- if ("sample_id" %in% names(md)) as.character(md$sample_id) else colnames(ex)
    pid <- if ("patient_id" %in% names(md)) as.character(md$patient_id) else ids
    ok <- grp %in% c("Case","Control")
    if (!any(ok)) next
    full <- intersect(members, toupper(rownames(ex))); comm <- intersect(common, toupper(rownames(ex)))
    if (length(full) < 2 || length(comm) < 2) next
    sc_full <- colMeans(ex[match(full, toupper(rownames(ex))), ok, drop=FALSE], na.rm=TRUE)
    sc_comm <- colMeans(ex[match(comm, toupper(rownames(ex))), ok, drop=FALSE], na.rm=TRUE)
    zf <- zscore(as.numeric(scale(sc_full))); zc <- zscore(sc_comm)
    g <- grp[ok]
    ef <- mean(sc_full[g=="Case"], na.rm=TRUE) - mean(sc_full[g=="Control"], na.rm=TRUE)
    ec <- mean(zc[g=="Case"] - mean(zc[g=="Control"], na.rm=TRUE), na.rm=TRUE)
    ef_s <- mean(zscore(sc_full)[g=="Case"], na.rm=TRUE) - mean(zscore(sc_full)[g=="Control"], na.rm=TRUE)
    ec_s <- mean(zc[g=="Case"], na.rm=TRUE) - mean(zc[g=="Control"], na.rm=TRUE)
    rows[[length(rows)+1]] <- data.frame(module=m, accession=o$acc, n_members=length(members), n_full=length(full),
      n_common=length(comm), effect_full=ef_s, effect_common=ec_s,
      sign_agree=sign(ef_s)==sign(ec_s), stringsAsFactors=FALSE)
  }
  d <- dplyr::bind_rows(rows); d <- d[d$module==m,]
  if (nrow(d) >= 3) {
    rho <- suppressWarnings(cor(d$effect_full, d$effect_common, method="spearman"))
    summary_rows[[length(summary_rows)+1]] <- data.frame(module=m, n_members=length(members), n_common=length(common),
      cohorts=nrow(d), spearman=round(rho,3), sign_agreement=round(mean(d$sign_agree),3),
      flag=ifelse(mean(d$sign_agree) < 0.8, "direction disagreement in >=20% cohorts", "consistent"))
  }
}
det <- bind_rows(rows); sm <- bind_rows(summary_rows)
write.csv(det, file.path(OUT,"v12_common_gene_sensitivity_per_cohort.csv"), row.names=FALSE)
write.csv(sm, file.path(OUT,"v12_common_gene_sensitivity_summary.csv"), row.names=FALSE)
cat("== common-gene sensitivity summary ==\n"); print(as.data.frame(sm), row.names=FALSE)
cat("\nmedian Spearman:", round(median(sm$spearman, na.rm=TRUE),3), "| modules flagged:",
    sum(grepl("disagreement", sm$flag, ignore.case=TRUE)), "\n")
