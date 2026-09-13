#!/usr/bin/env Rscript
# v10 RERUN C: corrected CRC external validation (tumour-only, numeric stage, unadjusted/age/age+stage, CI)
suppressPackageStartupMessages({library(Biobase); library(GEOquery); library(survival); library(dplyr)})
options(timeout=300)
OUT <- "C:/Users/fengq/Desktop/EGFR/EGFR_external_validation"; cache <- file.path(OUT,"data_raw")
V10 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v10/reruns/results"
ann <- readRDS("C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_raw/geo/platform_annotations/GPL570_annotation.rds")
symcol <- if("gene_symbol" %in% colnames(ann)) "gene_symbol" else "Gene symbol"
clean_sym <- function(v){ v<-as.character(v); amb<-grepl("///|//|;|,",v,perl=TRUE); s<-toupper(trimws(v)); ok<-!is.na(s)&nzchar(s)&!amb&s!="---"&grepl("^[A-Z0-9][A-Z0-9._-]*$",s); s[!ok]<-NA; s }
ps <- clean_sym(ann[[symcol]]); pid <- as.character(ann[["ID"]])
collapse <- function(e){ mi<-match(rownames(e),pid); sy<-ps[mi]; keep<-!is.na(sy); e<-e[keep,,drop=FALSE]; s<-sy[keep]
  sp<-split(seq_len(nrow(e)),s); out<-do.call(rbind,lapply(sp,function(ii) colMeans(e[ii,,drop=FALSE]))); rownames(out)<-names(sp); out }
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
mods <- split(toupper(gs$gene), gs$module)
g <- getGEO("GSE39582", GSEMatrix=TRUE, destdir=cache, AnnotGPL=FALSE, getGPL=FALSE); p <- pData(g[[1]])
expr <- exprs(g[[1]]); if(max(expr,na.rm=TRUE)>100) expr <- log2(expr+1)
ge <- collapse(expr); z <- t(scale(t(ge)))
tissue <- as.character(p[["dataset:ch1"]]); if(all(is.na(tissue))) tissue <- as.character(p[["characteristics_ch1.1"]])
istum <- grepl("discovery|validation", tissue, ignore.case=TRUE) & !grepl("non.?tumou?ral", tissue, ignore.case=TRUE)
os <- suppressWarnings(as.numeric(p[["os.delay (months):ch1"]])); ev <- suppressWarnings(as.numeric(p[["os.event:ch1"]]))
stagec <- as.character(p[["tnm.stage:ch1"]])
stage <- suppressWarnings(as.numeric(gsub("[^0-9]", "", stagec)))
cat("== GSE39582 audit (v10) ==\n")
cat("total:", nrow(p), "| tumour:", sum(istum), "| non-tumour:", sum(!istum), "\n")
inc <- istum & !is.na(os) & os>0 & ev %in% c(0,1)
cat("tumour analysable:", sum(inc), "| events:", sum(ev[inc]==1), "| non-tumour excluded with OS:", sum(!istum & !is.na(os)), "\n")
cat("duplicate GEO ids:", sum(duplicated(rownames(p))), "| stage values:", paste(names(table(stagec)), collapse=","), "\n")
cat("tumour with stage 1-4:", sum(inc & stage %in% 1:4), "| stage 0:", sum(inc & stage==0), "| stage NA:", sum(inc & is.na(stage)), "\n")
d <- data.frame(geo=rownames(p), time=os, event=ev, age=suppressWarnings(as.numeric(p[["age.at.diagnosis (year):ch1"]])),
                stage=stage, stringsAsFactors=FALSE)[inc, ]
rows <- list()
zi <- z[, match(d$geo, colnames(z)), drop=FALSE]
for (m in names(mods)) {
  gm <- intersect(mods[[m]], rownames(zi)); if(length(gm)<2) next
  d$score <- colMeans(zi[gm,,drop=FALSE], na.rm=TRUE)
  dd <- d[is.finite(d$score) & is.finite(d$time) & d$time>0 & !is.na(d$event), ]
  if(nrow(dd)<50 || sum(dd$event)<10) next
  dd$z <- scale(dd$score)[,1]
  fits <- list(uni=coxph(Surv(time,event)~z, data=dd))
  if(sum(is.finite(dd$age))>=50) fits$age <- coxph(Surv(time,event)~z+age, data=dd)
  ds <- dd[dd$stage %in% 1:4, ]
  if(nrow(ds)>=50 && sum(ds$event)>=10) fits[["age+stage"]] <- coxph(Surv(time,event)~z+age+factor(stage), data=ds)
  for (nm in names(fits)) { f<-fits[[nm]]; cf<-coef(summary(f)); ci<-exp(confint(f)["z",])
    rows[[length(rows)+1]] <- data.frame(cohort="GSE39582", feature=m, model=nm, n=f$n, events=f$nevent,
      HR=exp(cf["z","coef"]), lo=ci[1], hi=ci[2], p=cf["z","Pr(>|z|)"], stringsAsFactors=FALSE) }
}
res <- bind_rows(rows); res$fdr <- NA_real_
for (nm in unique(res$model)) { ix <- res$model==nm; res$fdr[ix] <- p.adjust(res$p[ix], "BH") }
write.csv(res, file.path(V10,"v10_external_crc_gse39582.csv"), row.names=FALSE)
cat("\n== key CRC modules ==\n")
print(res[res$feature %in% c("VEGF_PDGF_AXIS","ERBB_LIGANDS","WNT_CTNNB1","EPH_RECEPTORS","FGFR_AXIS","IGF_INSR_AXIS","PDGFR_KIT_CSF1R"),],
      row.names=FALSE, digits=3)
