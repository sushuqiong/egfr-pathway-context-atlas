#!/usr/bin/env Rscript
# v9 Rerun 3 : external-cohort identity & sample-count audit (GPT6 point 4)
suppressPackageStartupMessages({library(Biobase); library(GEOquery)})
options(timeout=300)
OUT <- "C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/../EGFR_external_validation"  # placeholder replaced below
OUT <- "C:/Users/fengq/Desktop/EGFR/EGFR_external_validation"
cache <- file.path(OUT,"data_raw")
audit <- function(acc, label, os_cols=NULL){
  cat("\n=====", acc, "=====\n")
  g <- getGEO(acc, GSEMatrix=TRUE, destdir=cache, AnnotGPL=FALSE, getGPL=FALSE)
  p <- pData(g[[1]])
  cn <- colnames(p)
  cat("platform:", paste(unique(as.character(p$platform_id)), collapse=","), " total samples:", nrow(p), "\n")
  cat("unique geo:", length(unique(rownames(p))), " duplicated sample ids:", sum(duplicated(rownames(p))), "\n")
  # look for normal/adjacent marker
  fields <- c("source_name_ch1","characteristics_ch1","description")
  tab <- list()
  for (f in intersect(fields, cn)) {
    cat("sample label field ", f, " head:\n"); print(utils::head(table(as.character(p[[f]])),6))
  }
  cat("titles head:\n"); print(utils::head(as.character(p$title),5))
  if (acc=="GSE39582") {
    # normal detection from source or characteristics
    hit <- intersect(cn, c("source_name_ch1","characteristics_ch1"))
    txt <- if(length(hit)) tolower(paste(as.character(p[[hit[1]]]), collapse="|")) else ""
    norm <- grepl("normal|adjacent|non.?tumor", txt)
    cat("any normal-ish labels present (raw text):", norm, "\n")
    os <- suppressWarnings(as.numeric(p[["os.delay (months):ch1"]]))
    ev <- suppressWarnings(as.numeric(p[["os.event:ch1"]]))
    cat("OS months non-NA:", sum(!is.na(os)), " events 0/1:", sum(ev %in% c(0,1)), " events==1:", sum(ev==1, na.rm=TRUE), "\n")
    inc <- !is.na(os) & os>0 & ev %in% c(0,1)
    cat("analysable (time>0 & event 0/1):", sum(inc), "\n")
    write.csv(data.frame(geo=rownames(p), os=os, event=ev, included=inc), file.path(OUT,"results",paste0("audit_",acc,".csv")), row.names=FALSE)
  }
  if (acc=="GSE21501") {
    os <- suppressWarnings(as.numeric(p[["os time:ch2"]])); ev <- suppressWarnings(as.numeric(p[["os event:ch2"]]))
    cat("OS time non-NA:", sum(!is.na(os)), " event 0/1:", sum(ev %in% c(0,1)), " events==1:", sum(ev==1, na.rm=TRUE), "\n")
    inc <- !is.na(os) & os>0 & ev %in% c(0,1)
    cat("analysable:", sum(inc), "\n")
    write.csv(data.frame(geo=rownames(p), os=os, event=ev, included=inc), file.path(OUT,"results",paste0("audit_",acc,".csv")), row.names=FALSE)
  }
  if (acc=="GSE62254") {
    cl <- read.csv(file.path(OUT,"results","external_stad_acrg_os.csv"), stringsAsFactors=FALSE)
    cat("clinical rows:", nrow(cl), " unique patients:", length(unique(cl$patient)), " events main(2/3/4):", sum(cl$event_main==1), "\n")
    cat("os months NA:", sum(is.na(cl$os_months)), " duplicate patients:", sum(duplicated(cl$patient)), "\n")
  }
}
audit("GSE39582")
audit("GSE21501")
audit("GSE62254")
cat("\naudit done\n")
