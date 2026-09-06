#!/usr/bin/env Rscript
# v9 Rerun 3b : GSE39582 identity audit + age/stage-adjusted module-OS with 95% CI
suppressPackageStartupMessages({library(Biobase); library(GEOquery); library(survival); library(dplyr)})
options(timeout=300)
OUT <- "C:/Users/fengq/Desktop/EGFR/EGFR_external_validation"; cache <- file.path(OUT,"data_raw")
ann <- readRDS("C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_raw/geo/platform_annotations/GPL570_annotation.rds")
cat("ann cols:", paste(colnames(ann), collapse=" | "), "\n")
symcol <- if("gene_symbol" %in% colnames(ann)) "gene_symbol" else if("Gene symbol" %in% colnames(ann)) "Gene symbol" else colnames(ann)[1]
clean_sym <- function(v){ v<-as.character(v); amb<-grepl("///|//|;|,",v,perl=TRUE); s<-toupper(trimws(v)); ok<-!is.na(s)&nzchar(s)&!amb&s!="---"&grepl("^[A-Z0-9][A-Z0-9._-]*$",s); s[!ok]<-NA; s }
ps <- clean_sym(ann[[symcol]]); pid <- as.character(ann[[if("ID" %in% colnames(ann)) "ID" else colnames(ann)[1]]])
collapse <- function(expr){ mi<-match(rownames(expr),pid); sy<-ps[mi]; keep<-!is.na(sy)
  e<-expr[keep,,drop=FALSE]; s<-sy[keep]; sp<-split(seq_len(nrow(e)),s)
  out<-do.call(rbind, lapply(sp, function(ii) colMeans(e[ii,,drop=FALSE])))
  rownames(out)<-names(sp); out }
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
mods <- split(toupper(gs$gene), gs$module)
g <- getGEO("GSE39582", GSEMatrix=TRUE, destdir=cache, AnnotGPL=FALSE, getGPL=FALSE); p <- pData(g[[1]])
expr <- exprs(g[[1]]); if(max(expr,na.rm=T)>100) expr <- log2(expr+1); ge <- collapse(expr); cat("ge class",class(ge),"dim",paste(dim(ge),collapse="x"),"mode",mode(ge),"\n")
z <- t(scale(t(ge)))
cn <- colnames(p)
lab <- if("source_name_ch1" %in% cn) as.character(p$source_name_ch1) else if("characteristics_ch1" %in% cn) as.character(p[[grep("characteristics_ch1$",cn)[1]]]) else as.character(p$title)
is_norm <- grepl("normal|adjacent|non-tumor", lab, ignore.case=TRUE)
os <- suppressWarnings(as.numeric(p[["os.delay (months):ch1"]])); ev <- suppressWarnings(as.numeric(p[["os.event:ch1"]]))
inc <- !is.na(os) & os>0 & ev %in% c(0,1)
cat("== GSE39582 == total",nrow(p)," normal-like",sum(is_norm)," tumour-like",sum(!is_norm),
    " analysable",sum(inc)," analysable&normal",sum(inc&is_norm),"\n")
stg <- as.character(p[["tnm.stage:ch1"]])
roman <- function(x){ x<-toupper(trimws(gsub("Stage|stage","",x))); m<-sapply(strsplit(x,""), function(ch){ v<-switch(ch,"I"=1,"II"=2,"III"=3,"IV"=4,NA); v; }); sapply(seq_along(x), function(i){ vals<-if(is.list(m)) unlist(m[i]) else m; if(all(is.na(vals))) NA_real_ else max(vals,na.rm=TRUE) }) }
# simpler: map prefixes
stage_num <- sapply(stg, function(s){ s<-gsub("Stage ","",s); if(grepl("^IV",s)) 4 else if(grepl("^III",s)) 3 else if(grepl("^II",s)) 2 else if(grepl("^I",s)) 1 else NA }, USE.NAMES=FALSE)
d <- data.frame(geo=rownames(p), time=os, event=ev, age=suppressWarnings(as.numeric(p[["age.at.diagnosis (year):ch1"]])), stage=stage_num, stringsAsFactors=FALSE)
rows <- list()
for (mod in c("VEGF_PDGF_AXIS","ERBB_LIGANDS","WNT_CTNNB1","EPH_RECEPTORS")) {
  sc <- score <- colMeans(z[intersect(mods[[mod]], rownames(z)),,drop=FALSE], na.rm=TRUE)
  d$score <- as.numeric(sc)
  dd <- d[is.finite(d$score)&is.finite(d$time)&d$time>0&!is.na(d$event), ]
  if(nrow(dd)<50||sum(dd$event)<10) next
  dd$z <- scale(dd$score)[,1]
  f_uni <- coxph(Surv(time,event)~z, data=dd)
  f_age <- tryCatch(coxph(Surv(time,event)~z+age, data=dd), error=function(e) NULL)
  f_full <- tryCatch(coxph(Surv(time,event)~z+age+stage, data=dd), error=function(e) NULL)
  for (nm in c("uni","age","age+stage")) {
    f <- get(paste0("f_", switch(nm, uni="uni", age="age", "age+stage"="full")))
    if(is.null(f)) next
    cf<-coef(summary(f)); ci<-exp(confint(f)["z",])
    rows[[length(rows)+1]] <- data.frame(cohort="GSE39582", feature=mod, model=nm, n=nrow(dd), events=sum(dd$event),
      HR=exp(cf["z","coef"]), lo=ci[1], hi=ci[2], p=cf["z","Pr(>|z|)"])
  }
}
res <- bind_rows(rows); print(res, row.names=FALSE, digits=3)
write.csv(res, file.path(OUT,"results","external_crc_gse39582_refined.csv"), row.names=FALSE)
cat("GSE39582 refined done\n")
