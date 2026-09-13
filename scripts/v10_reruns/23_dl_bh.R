d<-read.csv("C:/Users/fengq/Desktop/EGFR/EGFR的v10/reruns/results/v10_meta_empirical_ri.csv",stringsAsFactors=FALSE)
d$fdr_DL<-NA_real_
for(dis in unique(d$disease)){
  ix<-d$disease==dis & d$k>=2 & is.finite(d$p_DL)
  if(sum(ix)) d$fdr_DL[ix]<-p.adjust(d$p_DL[ix],"BH")
}
cat("DL BH-sig (k>=2):",sum(d$k>=2 & d$fdr_DL<0.05,na.rm=TRUE),"\n")
tb<-table(d$disease[d$k>=2 & d$fdr_DL<0.05])
cat("by disease:",paste(names(tb),as.integer(tb),collapse=" | "),"\n")
print(d[d$k>=2 & d$fdr_DL<0.05,c("disease","feature","k","est_DL","p_DL","fdr_DL")],row.names=FALSE,digits=3)
