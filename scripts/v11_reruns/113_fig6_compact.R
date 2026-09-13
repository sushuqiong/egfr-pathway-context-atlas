#!/usr/bin/env Rscript
# Fig6 compact rebuild: two stacked panels, annotation column inside limits, page-friendly size
suppressPackageStartupMessages({library(dplyr); library(ggplot2); library(patchwork)})
V <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/reruns/results"
F11 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/02_图片"
lab <- function(x){ x<-gsub("_AXIS$","",x); x<-gsub("_RECEPTORS","",x)
  m<-c("ERBB_LIGANDS"="ERBB-L","PDGFR_KIT_CSF1R"="PDGFR-KIT","RET_ALK_NTRK"="RET/ALK","VEGF_PDGF"="VEGF/PDGF",
       "TIE_ANGPT"="TIE/Ang","HGF_MET"="HGF/MET","TAM_AXL"="TAM/AXL","IGF_INSR"="IGF/INSR","TGFB_SMAD"="TGF-beta",
       "WNT_CTNNB1"="WNT/b-cat","PI3K_AKT"="PI3K-AKT","RAS_MAPK"="RAS-MAPK","JAK_STAT"="JAK-STAT","SRC_FAK"="SRC/FAK")
  ifelse(x %in% names(m), m[x], x) }
th <- function(base=12) theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(), panel.grid.major.y=element_blank(),
        panel.grid.major.x=element_line(colour="grey93", linewidth=.25),
        plot.title=element_text(face="bold", hjust=0, size=base),
        plot.margin=margin(6,10,6,6), axis.text.y=element_text(size=8.6))
sc <- read.csv(file.path(V,"sc_v11_patient_paired.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
sig <- sc[is.finite(sc$fdr) & sc$fdr<0.05, ]
sig$diff <- sig$case_patient_mean - sig$control_patient_mean
sig <- sig[is.finite(sig$diff), ]
sig$block <- ifelse(sig$comparison_type=="same-cell-type","A  Same-cell-type comparisons (FDR<0.05)","B  Cell-identity contrasts (malignant vs normal epithelium; FDR<0.05)")
sig$annot <- ifelse(sig$n_pairs>0, paste0(sig$n_pairs," pairs"), paste0(sig$n_case_patients,"v",sig$n_control_patients))
sig$ylab <- paste0(sig$disease, " | ", lab(sig$module), " | ", substr(gsub("_"," ",sig$cell_type),1,30))
panels <- list()
for (b in unique(sig$block)) {
  d <- sig[sig$block==b, ]; d <- d[order(d$diff), ]
  d$ylab <- factor(d$ylab, levels=d$ylab)
  m <- max(abs(d$diff)); lim <- m*1.75
  panels[[b]] <- ggplot(d, aes(diff, ylab)) +
    geom_col(aes(fill=diff>0), width=.62) + geom_vline(xintercept=0, colour="grey45") +
    geom_text(aes(x=ifelse(diff>0, -m*0.06, m*0.06), label=annot), hjust=ifelse(d$diff>0,1,0), size=2.9, colour="grey25") +
    scale_fill_manual(values=c("TRUE"="#A6123C","FALSE"="#14457B"), guide="none") +
    scale_x_continuous(limits=c(-lim,lim)) +
    labs(x="patient-level mean difference (case - control)", y=NULL, title=b) + th()
}
g <- panels[[1]] / panels[[2]] + plot_layout(heights=c(sum(sig$block==names(panels)[1]), sum(sig$block==names(panels)[2])))
h <- 0.25*nrow(sig) + 2.4
ggsave(file.path(F11,"fig6_sc_v11.png"), g, width=8.6, height=h, dpi=300, limitsize=FALSE)
ggsave(file.path(F11,"fig6_sc_v11.pdf"), g, width=8.6, height=h, limitsize=FALSE)
cat(sprintf("fig6 rebuilt: rows=%d height=%.1f in (%.1f cm)\n", nrow(sig), h, h*2.54))
