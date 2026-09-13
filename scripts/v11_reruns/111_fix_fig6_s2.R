#!/usr/bin/env Rscript
# Fix the two remaining layout problems: Fig6 (label density) and Supp S2 (clipped title)
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2); library(patchwork)})
A <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
V <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/reruns/results"
F11 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/02_图片"
ctx <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma")
lab <- function(x){ x<-gsub("_AXIS$","",x); x<-gsub("_RECEPTORS","",x)
  m<-c("ERBB_LIGANDS"="ERBB-L","PDGFR_KIT_CSF1R"="PDGFR-KIT","RET_ALK_NTRK"="RET/ALK","VEGF_PDGF"="VEGF/PDGF",
       "TIE_ANGPT"="TIE/Ang","HGF_MET"="HGF/MET","TAM_AXL"="TAM/AXL","IGF_INSR"="IGF/INSR","TGFB_SMAD"="TGF-beta",
       "WNT_CTNNB1"="WNT/b-cat","PI3K_AKT"="PI3K-AKT","RAS_MAPK"="RAS-MAPK","JAK_STAT"="JAK-STAT","SRC_FAK"="SRC/FAK")
  ifelse(x %in% names(m), m[x], x) }
th <- function(base=14) theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_line(colour="grey93", linewidth=.25),
        panel.grid.major.x=element_blank(), legend.position="bottom",
        plot.title=element_text(face="bold", hjust=0, size=base),
        plot.margin=margin(12,20,12,12), axis.text=element_text(size=base-2), axis.title=element_text(size=base-1))

## ---- Fig6 v3: context: module on the left; cell type + n in a right-hand column ----
sc <- read.csv(file.path(V,"sc_v11_patient_paired.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
sig <- sc[is.finite(sc$fdr) & sc$fdr<0.05, ]
sig$diff <- sig$case_patient_mean - sig$control_patient_mean
sig$block <- ifelse(sig$comparison_type=="same-cell-type","A","B")
sig$ct <- gsub("_"," ", sig$cell_type)
sig$annot <- ifelse(sig$n_pairs>0, paste0(sig$n_pairs," pairs"), paste0(sig$n_case_patients," vs ",sig$n_control_patients))
sig$ylab <- paste0(sig$disease, ": ", lab(sig$module), "\n", gsub("_"," ", sig$cell_type))
titles <- c(A="A  Same-cell-type comparisons (family-wise FDR<0.05)",
            B="B  Cell-identity contrasts (malignant vs normal epithelium; FDR<0.05)")
plots <- list()
for (b in c("A","B")) {
  d <- sig[sig$block==b, ]
  if(!nrow(d)) { plots[[b]] <- ggplot()+theme_void(); next }
  d <- d[order(d$diff), ]; d$ylab <- factor(d$ylab, levels=d$ylab)
  xmax <- max(abs(d$diff))*1.9; xr <- max(abs(d$diff))*1.1
  plots[[b]] <- ggplot(d, aes(diff, ylab)) + geom_col(aes(fill=diff>0), width=.6) +
    geom_text(aes(x=ifelse(diff>0, -xr*1.02, xr*1.02), label=annot), hjust=ifelse(d$diff>0,1,0), size=4.4, colour="grey25") +
    geom_vline(xintercept=0, colour="grey45") +
    scale_fill_manual(values=c("TRUE"="#A6123C","FALSE"="#14457B"), guide="none") +
    scale_x_continuous(limits=c(-xmax,xmax), breaks=c(-round(xr,1),0,round(xr,1))) +
    labs(x="patient-level mean difference (case - control)", y=NULL, title=titles[[b]]) + th(14) +
    theme(axis.text.y=element_text(size=12))
}
nA <- max(2, sum(sig$block=="A")); nB <- max(2, sum(sig$block=="B"))
g6 <- plots$A / plots$B + plot_layout(heights=c(nA,nB))
h6 <- 1.15*(nA+nB) + 3.2
ggsave(file.path(F11,"fig6_sc_v11.png"), g6, width=10.5, height=h6, dpi=300, limitsize=FALSE)
ggsave(file.path(F11,"fig6_sc_v11.pdf"), g6, width=10.5, height=h6, limitsize=FALSE)

## ---- Supp S2 v2: two-line title, wider margins, no clipping ----
raw <- read.csv(file.path(A,"context_atlas_summary.csv"), stringsAsFactors=FALSE)
raw$flab <- factor(lab(raw$feature)); lv <- rev(levels(raw$flab))
xs <- read.csv(file.path(A,"xcell/context_atlas_summary_xcell_adjusted.csv"), stringsAsFactors=FALSE)
xs$disease <- factor(xs$disease, levels=ctx); xs$flab <- factor(lab(xs$feature), levels=lv)
gS2 <- ggplot(xs, aes(disease, flab)) + geom_tile(aes(fill=median_smd), colour="white", linewidth=.5) +
  geom_text(aes(label=ifelse(n_fdr_adj>=1, n_fdr_adj, ""), colour=ifelse(abs(median_smd)>1,"white","grey15")), size=4.2) +
  geom_point(data=xs[xs$robust_xcell %in% TRUE,], shape=8, size=2.4, colour="black") +
  scale_colour_identity() + scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0,
      name="adjusted median SMD\n(xCell residualization)") + scale_x_discrete(position="top") +
  labs(x=NULL,y=NULL,
       title="Sensitivity analysis: xCell two-step residualization",
       subtitle="Digits = number of cohorts with FDR < 0.05; asterisk = robust under this sensitivity") + th(13.5) +
  theme(axis.text.x=element_text(angle=0, size=11), plot.margin=margin(14,22,14,14))
ggsave(file.path(F11,"fig_paper_xcell_heatmap.png"), gS2, width=9.2, height=8.2, dpi=300)
ggsave(file.path(F11,"fig_paper_xcell_heatmap.pdf"), gS2, width=9.2, height=8.2)
cat("fig6 + SuppS2 fixed\n")
