#!/usr/bin/env Rscript
# v9 stage2a: paired-correlation sensitivity for unified meta (rho 0.5 / 0.7 fixed)
suppressPackageStartupMessages({library(dplyr)})
V9 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v9/reruns/results"
df <- read.csv(file.path(V9,"v9_percohort_joint_unified.csv"), stringsAsFactors=FALSE)
df <- df[df$role %in% c("discovery","validation") & is.finite(df$var_unified) & df$var_unified>0 & is.finite(df$smd_unified), ]
# reconstruct paired dz from empirical-r g (g = dz*sqrt(2(1-r))); unpaired stays Hedges g
recon <- function(rho){
  d <- df
  pai <- d$paired & is.finite(d$r_emp) & d$r_emp>=0.05 & d$r_emp<0.995
  d$dz <- NA_real_
  d$dz[pai] <- d$smd_unified[pai]/sqrt(2*(1-d$r_emp[pai]))
  d$g <- d$smd_unified
  d$v <- d$var_unified
  # paired rows: rebuild g & v at fixed rho (using empirical rho fallback if provided to keep, else rho)
  for(i in which(d$paired & !is.na(d$npair) & d$npair>=3)){
    r <- d$r_emp[i]
    if(!is.finite(r) || r<0.05 || r>=0.995) r <- rho
    gi <- if(is.finite(d$dz[i])) d$dz[i]*sqrt(2*(1-rho)) else d$g[i]*sqrt((1-rho)/(1-r))
    d$g[i] <- gi
    d$v[i] <- 2*(1-rho)/d$npair[i] + gi^2/(2*(d$npair[i]-2))
  }
  d
}
reml_tau <- function(y,v){ k<-length(y); t<-0
  for(i in 1:500){ w<-1/(v+t); mu<-sum(w*y)/sum(w)
    num<-sum(w^2*(k/(k-1)*(y-mu)^2 - v)); den<-sum(w^2)
    if(!is.finite(num)||!is.finite(den)||den<=0) break
    nt<-max(0,num/den); if(!is.finite(nt)) break
    if(abs(nt-t)<1e-9){ t<-nt; break }; t<-nt }; if(!is.finite(t)) 0 else t }
hk <- function(y,v,t){ k<-length(y); w<-1/(v+t); mu<-sum(w*y)/sum(w)
  if(k<=1) return(c(mu,NA,NA,NA,NA)); q<-sum(w*(y-mu)^2); se<-sqrt(max(q/((k-1)*sum(w)),1e-12))
  p<-2*pt(-abs(mu/se),k-1); tc<-qt(0.975,k-1); c(mu,se,p,mu-tc*se,mu+tc*se) }
runmeta <- function(d, tag){
  rows<-list()
  for(grp in split(d, list(d$disease,d$feature), drop=TRUE)){
    if(nrow(grp)==0) next
    y<-grp$g; v<-grp$v; k<-nrow(grp); tr<-reml_tau(y,v); h<-hk(y,v,tr)
    rows[[length(rows)+1]]<-data.frame(disease=grp$disease[1],feature=grp$feature[1],k=k,
      smd_REML=h[1],se_HK=h[2],p_REML_HK=h[3],ci_lo=h[4],ci_hi=h[5],tau2=tr)
  }
  res<-bind_rows(rows); res$fdr<-NA_real_
  for(dis in unique(res$disease)){ ix<-res$disease==dis&res$k>=2&is.finite(res$p_REML_HK); if(sum(ix)) res$fdr[ix]<-p.adjust(res$p_REML_HK[ix],"BH") }
  write.csv(res, file.path(V9, sprintf("context_meta_v9_unified_%s.csv",tag)), row.names=FALSE)
  s<-res[res$k>=2&res$fdr<0.05,]
  cat("== rho",tag," REML/HK sig:",nrow(s),"\n")
  print(s[order(s$disease),c("disease","feature","k","smd_REML","ci_lo","ci_hi","fdr")], row.names=FALSE)
}
runmeta(recon(0.5),"rho05")
runmeta(recon(0.7),"rho07")
