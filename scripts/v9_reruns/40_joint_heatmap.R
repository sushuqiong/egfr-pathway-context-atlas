#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2)})
V9 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v9"
sm <- read.csv(file.path(V9,"reruns/results","v9_composition_joint_summary.csv"), stringsAsFactors=FALSE)
sm$feature <- gsub("_AXIS$","",sm$feature)
ctx <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma")
feats <- rev(c("ERBB_RECEPTORS","ERBB_LIGANDS","RAS_MAPK","PI3K_AKT","FGFR","VEGF_PDGF","PDGFR_KIT_CSF1R",
               "HGF_MET","TAM_AXL","IGF_INSR","RET_ALK_NTRK","EPH","TIE_ANGPT","JAK_STAT","SRC_FAK","TGFB_SMAD","WNT_CTNNB1"))
grid <- expand.grid(disease=ctx, feature=feats, stringsAsFactors=FALSE)
m <- merge(grid, sm[,c("disease","feature","n","n_fdr_joint","median_d_adj","joint_robust")], by=c("disease","feature"), all.x=TRUE)
m$disease <- factor(m$disease, levels=ctx)
m$feature <- factor(m$feature, levels=feats)
m$txtc <- ifelse(!is.na(m$median_d_adj) & abs(m$median_d_adj)>1.0, "white","grey20")
m$lab <- ifelse(is.na(m$median_d_adj), "", ifelse(m$n_fdr_joint>=1, as.character(m$n_fdr_joint), ""))
g <- ggplot(m, aes(disease, feature)) +
  geom_tile(aes(fill=median_d_adj), colour="white", linewidth=.4) +
  geom_text(aes(label=lab, colour=txtc), size=2.6) +
  geom_point(data=m[!is.na(m$joint_robust) & m$joint_robust, ], aes(disease, feature),
             shape=23, fill="black", colour="white", size=2.2, stroke=.5) +
  scale_colour_identity() +
  scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0,
                       name="joint-model adjusted difference (SD units)") +
  scale_x_discrete(position="top") +
  labs(x=NULL, y=NULL,
       title="Composition adjustment in joint models (module ~ disease + composition [+ patient])") +
  theme_bw(base_size=12) + theme(panel.grid=element_blank(),
    axis.text.x=element_text(angle=35, hjust=0, size=10),
    legend.position="bottom", legend.key.width=unit(1.5,"cm"),
    strip.background=element_rect(fill="grey92"), plot.title=element_text(face="bold", hjust=0, size=12))
ggsave(file.path(V9,"02_图片","fig_paper_joint_heatmap.png"), g, width=8.4, height=7.4, dpi=300)
ggsave(file.path(V9,"02_图片","fig_paper_joint_heatmap.pdf"), g, width=8.4, height=7.4)
cat("joint heatmap written\n")
