d<-read.csv("C:/Users/fengq/Desktop/EGFR/EGFR的v10/reruns/results/v10_meta_empirical_ri.csv",stringsAsFactors=FALSE)
d05<-read.csv("C:/Users/fengq/Desktop/EGFR/EGFR的v10/reruns/results/v10_meta_rho0.5.csv",stringsAsFactors=FALSE)
sig<-d[d$k>=2 & is.finite(d$fdr) & d$fdr<0.05,]
print(sig[,c("disease","feature","k","est_REML","ci_lo","ci_hi","p_REML_KHNA","fdr")],row.names=FALSE,digits=3)
cat("by disease:",paste(names(table(sig$disease)),as.integer(table(sig$disease)),collapse=" | "),"\n")
s05<-d05[d05$k>=2 & is.finite(d05$fdr) & d05$fdr<0.05,]
extra<-setdiff(paste(s05$disease,s05$feature),paste(sig$disease,sig$feature))
cat("states significant at rho=0.5 but not empirical:",paste(extra,collapse="; "),"\n")
cat("DL BH sig count:",sum(d$k>=2 & is.finite(d$p_DL) & p.adjust(d$p_DL,"BH")<0.05,na.rm=TRUE),"\n")
dl<-d[d$k>=2 & is.finite(d$p_DL),]; dl$fdr<-p.adjust(dl$p_DL,"BH")
cat("DL by disease:",paste(names(table(dl$disease[dl$fdr<0.05])),as.integer(table(dl$disease[dl$fdr<0.05])),collapse=" | "),"\n")
