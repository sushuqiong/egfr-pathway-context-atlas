#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(dplyr); library(ggplot2)})
ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
RES <- file.path(ROOT, "results"); FIG <- file.path(ROOT, "figures")
d <- read.csv(file.path(RES, "xcell/context_atlas_summary_xcell_adjusted.csv"), stringsAsFactors=FALSE, check.names=FALSE)
d$median_smd <- as.numeric(d$median_smd); d$n_fdr_adj <- as.numeric(d$n_fdr_adj)
lvl <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma")
d$disease <- factor(d$disease, levels=lvl)
d$feature <- factor(d$feature, levels=rev(sort(unique(d$feature))))
g <- ggplot(d, aes(disease, feature, fill=median_smd)) + geom_tile(colour="white") +
  geom_text(aes(label=ifelse(is.na(n_fdr_adj), "", ifelse(n_fdr_adj>=2, paste0(n_fdr_adj,"*"), as.character(n_fdr_adj)))), size=3.1) +
  scale_fill_gradient2(low="#1B5E9C", mid="white", high="#B02040", midpoint=0, name="median SMD") +
  labs(x=NULL, y=NULL, title="Composition-adjusted module state (xCell residualization, 27 cohorts)") +
  theme_minimal(base_size=11) + theme(axis.text.x=element_text(angle=45, hjust=1), panel.grid=element_blank())
ggsave(file.path(FIG,"fig_paper_xcell_heatmap.png"), g, width=9, height=9, dpi=300)
ggsave(file.path(FIG,"fig_paper_xcell_heatmap.pdf"), g, width=9, height=9)
cat("xcell heatmap done; robust-xcell cells:", sum(d$robust_xcell=="TRUE", na.rm=TRUE), "\n")
