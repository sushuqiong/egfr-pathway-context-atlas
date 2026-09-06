#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(dplyr); library(tidyr)})
V9 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v9/reruns/results"
df <- read.csv(file.path(V9,"v9_percohort_joint_unified.csv"), stringsAsFactors=FALSE)
df <- df[df$role %in% c("discovery","validation") & is.finite(df$var_unified) & df$var_unified>0, ]
df <- df[df$role %in% c("discovery","validation") & is.finite(df$var_unified) & df$var_unified>0 & is.finite(df$smd_unified), ]
reml_tau <- function(y,v){ k<-length(y); t<-0
  for(i in 1:300){ w<-1/(v+t); mu<-sum(w*y)/sum(w)
    num<-sum(w^2*(k/(k-1)*(y-mu)^2 - v)); den<-sum(w^2)
    if(!is.finite(num)||!is.finite(den)||den<=0) break
    nt<-max(0, num/den)
    if(!is.finite(nt)) break
    if(abs(nt-t)<1e-9){ t<-nt; break }; t<-nt }
  if(!is.finite(t)) 0 else t }
hk <- function(y,v,t){ k<-length(y); w<-1/(v+t); mu<-sum(w*y)/sum(w)
  if(k<=1) return(c(mu,NA,NA,NA,NA)); q<-sum(w*(y-mu)^2); se<-sqrt(max(q/((k-1)*sum(w)),1e-12))
  p<-2*pt(-abs(mu/se), df=k-1); tc<-qt(0.975,k-1); c(mu,se,p,mu-tc*se,mu+tc*se) }
dl_run <- function(y,v){ k<-length(y); w<-1/v; mu<-sum(w*y)/sum(w); Q<-sum(w*(y-mu)^2); C<-sum(w)-sum(w^2)/sum(w)
  t<-if(C>0) max(0,(Q-(k-1))/C) else 0; w2<-1/(v+t); mu2<-sum(w2*y)/sum(w2); se<-sqrt(1/sum(w2)); c(mu2,se,2*pnorm(-abs(mu2)/se)) }
rows <- list()
for (grp in split(df, list(df$disease, df$feature), drop=TRUE)) {
  if(nrow(grp)==0) next
  y<-grp$smd_unified; v<-grp$var_unified; k<-nrow(grp)
  d1<-dl_run(y,v); tr<-reml_tau(y,v); h<-hk(y,v,tr)
  w0<-1/v; muf<-sum(w0*y)/sum(w0); Q<-sum(w0*(y-muf)^2); I2<-if(Q>0) max(0,(Q-(k-1))/Q)*100 else 0
  rows[[length(rows)+1]] <- data.frame(disease=grp$disease[1], feature=grp$feature[1], k=k,
    accession=paste(grp$accession,collapse=";"), n_case=sum(grp$n_case), n_control=sum(grp$n_control),
    smd_min=min(y), smd_max=max(y), smd_DL=d1[1], se_DL=d1[2], p_DL=d1[3],
    smd_REML=h[1], se_HK=h[2], p_REML_HK=h[3], ci_lo=h[4], ci_hi=h[5], I2=I2, tau2_REML=tr)
}
res <- bind_rows(rows)
res$fdr_DL <- NA_real_; res$fdr_REML_HK <- NA_real_
for (dis in unique(res$disease)) {
  ix <- res$disease==dis & res$k>=2 & is.finite(res$p_DL)
  if(sum(ix)) res$fdr_DL[ix] <- p.adjust(res$p_DL[ix],"BH")
  ix2 <- res$disease==dis & res$k>=2 & is.finite(res$p_REML_HK)
  if(sum(ix2)) res$fdr_REML_HK[ix2] <- p.adjust(res$p_REML_HK[ix2],"BH")
}
write.csv(res, file.path(V9,"context_meta_v9_unified.csv"), row.names=FALSE)
sigD <- sum(res$k>=2 & res$fdr_DL<0.05, na.rm=TRUE); sigR <- sum(res$k>=2 & res$fdr_REML_HK<0.05, na.rm=TRUE)
cat("DL sig(k>=2):", sigD, " REML/HK sig:", sigR, "\n")
cat("REML/HK sig list:\n")
print(res[res$k>=2 & res$fdr_REML_HK<0.05, c("disease","feature","k","smd_REML","ci_lo","ci_hi","p_REML_HK","fdr_REML_HK")], row.names=FALSE)
# joint summary
df$fdr_joint <- NA_real_
for (acc in unique(df$accession)) { ix <- df$accession==acc & is.finite(df$p_adj)
  if(sum(ix)) df$fdr_joint[ix] <- p.adjust(df$p_adj[ix],"BH") }
sm <- df %>% group_by(disease, feature) %>% summarise(
  n=n(), n_fdr_joint=sum(fdr_joint<0.05, na.rm=TRUE), pos_joint=sum(d_adj>0, na.rm=TRUE),
  neg_joint=sum(d_adj<0, na.rm=TRUE), median_d_adj=median(d_adj, na.rm=TRUE), .groups="drop") %>%
  mutate(majority=pmax(pos_joint,neg_joint),
         joint_robust = n_fdr_joint>=2 & (majority/n >= ifelse(n==2,1,2/3)))
write.csv(sm, file.path(V9,"v9_composition_joint_summary.csv"), row.names=FALSE)
cat("joint-robust:", sum(sm$joint_robust), "\n"); print(table(sm$disease[sm$joint_robust]))
xc <- read.csv("C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results/xcell/context_atlas_summary_xcell_adjusted.csv", stringsAsFactors=FALSE)
xr <- unique(paste(xc$disease[xc$robust_xcell], xc$feature[xc$robust_xcell], sep="|"))
jr <- unique(paste(sm$disease[sm$joint_robust], sm$feature[sm$joint_robust], sep="|"))
cat("xCell19 vs joint-robust overlap:", length(intersect(xr,jr)), " xCell-only:", length(setdiff(xr,jr)),
    " joint-only:", length(setdiff(jr,xr)), "\n")
