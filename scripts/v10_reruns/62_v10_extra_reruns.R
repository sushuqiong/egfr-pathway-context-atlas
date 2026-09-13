#!/usr/bin/env Rscript
# v10 extra analyses with CORRECTED paired indexing:
#  A) same-cohort GSVA vs member-mean-z concordance
#  B) key-state stability: full module vs (i) minus composition-marker-overlap genes, (ii) leave-out top-3 influential genes
suppressPackageStartupMessages({library(GSVA); library(metafor); library(dplyr)})
ROOTS <- c("C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk",
           "C:/Users/fengq/Desktop/EGFR/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk")
V10 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v10/reruns/results"
gs <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/config/gene_sets_extended.csv", stringsAsFactors=FALSE)
mods <- lapply(split(toupper(gs$gene), gs$module), unique)
paired_acc <- c("GSE32863","GSE19804","GSE10072","GSE44076","GSE27342","GSE63089","GSE15471","GSE28735","GSE62452","GSE57957","GSE23400","GSE20347")
locate <- function(acc) for (d in ROOTS){ f<-list.files(d, pattern=paste0("^",acc,"_processed\\.rds$"), full.names=TRUE); if(length(f)) return(f[1]) }
CACHE <- new.env()
loadc <- function(acc){ if(!is.null(CACHE[[acc]])) return(CACHE[[acc]])
  obj<-readRDS(locate(acc)); e<-obj$gene_expression; m<-obj$sample_metadata
  e<-e[, match(m$sample_id, colnames(e)), drop=FALSE]
  z<-t(scale(t(e[rowSums(is.na(e))==0,,drop=FALSE])))
  v<-list(e=e,m=m,z=z); CACHE[[acc]]<-v; v }
comp_markers <- c("EPCAM","KRT8","KRT18","KRT19","CDH1","COL1A1","COL1A2","COL3A1","FAP","DCN",
                  "PECAM1","VWF","CDH5","PTPRC","CD3D","CD19","CD68")
effect <- function(acc, sc, m){
  grp <- factor(m$group, levels=c("Control","Case")); pid <- if("patient_id" %in% names(m)) as.character(m$patient_id) else as.character(m$sample_id)
  iscase <- grp=="Case"
  if (acc %in% paired_acc) {
    cc <- intersect(pid[iscase], pid[!iscase]); if(length(cc)<4) return(c(NA,NA))
    yc <- sc[iscase][match(cc, pid[iscase])]; yr <- sc[!iscase][match(cc, pid[!iscase])]
    ri <- suppressWarnings(cor(yc,yr)); ri <- if(is.finite(ri)) min(max(ri,-0.99),0.99) else 0.2
    es <- metafor::escalc(measure="SMCRH", m1i=mean(yc), m2i=mean(yr), sd1i=sd(yc), sd2i=sd(yr), ri=ri, ni=length(cc))
    c(as.numeric(es$yi), as.numeric(es$vi))
  } else {
    yc <- sc[iscase]; yr <- sc[!iscase]
    es <- metafor::escalc(measure="SMD", m1i=mean(yc), sd1i=sd(yc), n1i=length(yc), m2i=mean(yr), sd2i=sd(yr), n2i=length(yr))
    c(as.numeric(es$yi), as.numeric(es$vi))
  }
}
gscore <- function(expr, genes, tag){ if(length(genes)<3) return(NULL)
  GSVA::gsva(GSVA::gsvaParam(expr, setNames(list(genes), tag), minSize=3, kcdf="Gaussian"), verbose=FALSE)[1,] }

## ---- A) concordance ----
AACC <- c("GSE44076","GSE23878","GSE32863","GSE4302","GSE15471","GSE33814")
Ac <- list()
for (acc in AACC) { v<-loadc(acc); present<-names(mods)[lengths(lapply(mods,function(g) intersect(g,rownames(v$e))))>=3]
  if(!length(present)) next
  s1 <- GSVA::gsva(GSVA::gsvaParam(v$e, mods[present], minSize=3, kcdf="Gaussian"), verbose=FALSE)
  for (m in present){ g<-intersect(mods[[m]], rownames(v$z)); if(length(g)<2) next
    zs <- colMeans(v$z[g,,drop=FALSE], na.rm=TRUE)
    Ac[[length(Ac)+1]] <- data.frame(accession=acc, module=m, n_genes=length(g),
      rho=suppressWarnings(cor(as.numeric(s1[m,]), as.numeric(zs), method="spearman"))) } }
Ares <- bind_rows(Ac); write.csv(Ares, file.path(V10,"v10_gsva_vs_meanz.csv"), row.names=FALSE)
cat(sprintf("A) concordance median rho = %.3f (n=%d state-cohorts)\n", median(Ares$rho, na.rm=TRUE), nrow(Ares)))

## ---- B) key-state stability ----
KEY <- list(c("CRC","WNT_CTNNB1"),c("CRC","EPH_RECEPTORS"),c("CRC","VEGF_PDGF_AXIS"),c("CRC","FGFR_AXIS"),
  c("CRC","IGF_INSR_AXIS"),c("CRC","ERBB_LIGANDS"),c("CRC","PDGFR_KIT_CSF1R"),c("CRC","TGFB_SMAD"),c("CRC","TIE_ANGPT_AXIS"),
  c("STAD","EPH_RECEPTORS"),c("STAD","JAK_STAT"),c("STAD","RAS_MAPK"),c("STAD","HGF_MET_AXIS"),c("STAD","WNT_CTNNB1"),c("STAD","PI3K_AKT"),
  c("IBD","JAK_STAT"),c("IBD","HGF_MET_AXIS"),c("IBD","VEGF_PDGF_AXIS"),c("IBD","TIE_ANGPT_AXIS"),c("IBD","ERBB_RECEPTORS"),c("IBD","SRC_FAK"),
  c("PAAD","RAS_MAPK"),c("PAAD","HGF_MET_AXIS"),c("LUAD","FGFR_AXIS"),c("LUAD","JAK_STAT"),c("COPD","SRC_FAK"))
COH <- list(CRC=c("GSE44076","GSE41258","GSE23878"), STAD=c("GSE27342","GSE63089","GSE13911"),
            IBD=c("GSE75214","GSE87473","GSE179285"), PAAD=c("GSE15471","GSE28735","GSE62452"),
            LUAD=c("GSE32863","GSE19804","GSE10072"), COPD=c("GSE76925","GSE47460"))
rows <- list()
for (K in KEY) {
  dis <- K[1]; feat <- K[2]; members <- mods[[feat]]
  for (acc in COH[[dis]]) {
    v <- loadc(acc); gm <- intersect(members, rownames(v$e)); if(length(gm)<3) next
    iscase <- v$m$group=="Case"
    infl <- sapply(gm, function(g) mean(v$z[g,iscase],na.rm=TRUE) - mean(v$z[g,!iscase],na.rm=TRUE))
    top <- names(sort(abs(infl), decreasing=TRUE))[1:min(3,length(gm))]
    ov  <- intersect(gm, comp_markers)
    variants <- c(list(full=gm), list(minus_overlap=setdiff(gm, comp_markers)), setNames(lapply(top, function(g) setdiff(gm,g)), paste0("drop_",top)))
    variants <- variants[lengths(variants)>=3]
    for (nm in names(variants)) { sc <- gscore(v$e, variants[[nm]], feat); if(is.null(sc)) next
      ef <- effect(acc, as.numeric(sc), v$m)
      rows[[length(rows)+1]] <- data.frame(state=paste(dis,feat), accession=acc, variant=nm, n_genes=length(variants[[nm]]),
        yi=ef[1], vi=ef[2], stringsAsFactors=FALSE) }
  }
}
Bres <- bind_rows(rows); write.csv(Bres, file.path(V10,"v10_keystate_loogo_variants.csv"), row.names=FALSE)
## pooled per state x variant (REML/Knha)
pool <- list()
for (key in split(Bres, Bres$state)) {
  base <- key$yi[key$variant=="full"]
  for (vr in unique(key$variant)) {
    d <- key[key$variant==vr & is.finite(key$yi) & is.finite(key$vi) & key$vi>0, ]
    if(nrow(d)<2) next
    m <- tryCatch(rma.uni(yi, vi, data=d, method="REML", test="knha"), error=function(e) NULL); if(is.null(m)) next
    bs <- mean(base, na.rm=TRUE)
    pool[[length(pool)+1]] <- data.frame(state=key$state[1], variant=vr, k=nrow(d), est=as.numeric(m$beta), p=m$pval,
      sign_flip_vs_full = sign(as.numeric(m$beta)) != sign(bs), stringsAsFactors=FALSE)
  }
}
Pres <- bind_rows(pool); write.csv(Pres, file.path(V10,"v10_keystate_pooled.csv"), row.names=FALSE)
cat("B) cohort-level variants computed:", nrow(Bres), "| states:", length(unique(Bres$state)), "\n")
cat("B) pooled sign flips vs full:", sum(Pres$sign_flip_vs_full, na.rm=TRUE), "of", nrow(Pres), "\n")
print(Pres[Pres$variant!="full", c("state","variant","k","est","p","sign_flip_vs_full")], row.names=FALSE, digits=3)
