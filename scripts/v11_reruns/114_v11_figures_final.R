#!/usr/bin/env Rscript
# FINAL v11 figures: every figure <= 6.7 in (17 cm) wide at 300 dpi so printed point sizes hold.
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2); library(patchwork)})
A <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
V <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/reruns/results"
F <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/02_图片"
W <- 6.7   # 17.0 cm
ctx <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma")
lab <- function(x){ x<-gsub("_AXIS$","",x); x<-gsub("_RECEPTORS","",x)
  m<-c("ERBB_LIGANDS"="ERBB-L","PDGFR_KIT_CSF1R"="PDGFR-KIT","RET_ALK_NTRK"="RET/ALK","VEGF_PDGF"="VEGF/PDGF",
       "TIE_ANGPT"="TIE/Ang","HGF_MET"="HGF/MET","TAM_AXL"="TAM/AXL","IGF_INSR"="IGF/INSR","TGFB_SMAD"="TGF-beta",
       "WNT_CTNNB1"="WNT/b-cat","PI3K_AKT"="PI3K-AKT","RAS_MAPK"="RAS-MAPK","JAK_STAT"="JAK-STAT","SRC_FAK"="SRC/FAK")
  ifelse(x %in% names(m), m[x], x) }
th <- function(base=11) theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_line(colour="grey93", linewidth=.25),
        legend.position="bottom", legend.title=element_text(size=base-2), legend.text=element_text(size=base-2),
        strip.background=element_rect(fill="grey92", colour=NA), strip.text=element_text(face="bold", size=base-1),
        plot.title=element_text(face="bold", hjust=0, size=base), plot.margin=margin(6,10,6,6),
        axis.text=element_text(size=base-1), axis.title=element_text(size=base-1))

raw <- read.csv(file.path(A,"context_atlas_summary.csv"), stringsAsFactors=FALSE)
raw$disease <- factor(raw$disease, levels=ctx); raw$flab <- lab(raw$feature)
raw$flab <- factor(raw$flab, levels=rev(sort(unique(raw$flab))))
lv <- levels(raw$flab)
js <- read.csv(file.path(V,"v11_joint_summary.csv"), stringsAsFactors=FALSE); js$flab <- lab(js$feature)
pc <- read.csv(file.path(V,"v11_percohort_effects.csv"), stringsAsFactors=FALSE)

## Fig1 handled by graphviz (size-capped separately); Fig2A
g <- ggplot(raw, aes(disease, flab)) + geom_tile(aes(fill=median_smd), colour="white", linewidth=.4) +
  geom_text(aes(label=ifelse(n_fdr_raw>=1, n_fdr_raw, ""), colour=ifelse(abs(median_smd)>1,"white","grey15")), size=3.4) +
  geom_tile(data=raw[raw$robust_consistent,], fill=NA, colour="black", linewidth=1.1) + scale_colour_identity() +
  scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0, name="raw median SMD") +
  scale_x_discrete(position="top") + labs(x=NULL,y=NULL,title="A  Raw module states (per-cohort)") + th() +
  theme(axis.text.x=element_text(angle=0, size=10))
ggsave(file.path(F,"fig2a_raw_v11.png"), g, width=W, height=5.6, dpi=300); ggsave(file.path(F,"fig2a_raw_v11.pdf"), g, width=W, height=5.6)

## Fig2B
grid <- expand.grid(disease=ctx, flab=lv, stringsAsFactors=FALSE)
m2 <- merge(grid, js[,c("disease","flab","n_fdr","median_d_adj","joint_robust")], by=c("disease","flab"), all.x=TRUE)
m2$disease <- factor(m2$disease, levels=ctx); m2$flab <- factor(m2$flab, levels=lv)
m2$lab_txt <- ifelse(is.na(m2$median_d_adj),"n.e.", ifelse(m2$n_fdr>=1, as.character(m2$n_fdr), ""))
g <- ggplot(m2, aes(disease, flab)) + geom_tile(aes(fill=median_d_adj), colour="white", linewidth=.4) +
  geom_text(aes(label=lab_txt, colour=ifelse(!is.na(median_d_adj)&abs(median_d_adj)>1,"white","grey15")), size=3.4) +
  geom_tile(data=m2[!is.na(m2$joint_robust)&m2$joint_robust,], fill=NA, colour="black", linewidth=1.1) +
  scale_colour_identity() + scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0, na.value="grey85",
     name="adjusted coefficient (SD units)") + scale_x_discrete(position="top") +
  labs(x=NULL,y=NULL,title="B  Adjusted model (n.e. = not estimable)") + th() + theme(axis.text.x=element_text(angle=0, size=10))
ggsave(file.path(F,"fig2b_adjusted_v11.png"), g, width=W, height=5.6, dpi=300); ggsave(file.path(F,"fig2b_adjusted_v11.pdf"), g, width=W, height=5.6)

## Fig3
st <- pc %>% group_by(disease, feature) %>% summarise(beta_base=median(beta_base, na.rm=TRUE), beta_adj=median(beta_adj, na.rm=TRUE), .groups="drop") %>%
  left_join(js %>% select(disease, feature, joint_robust), by=c("disease","feature"))
st$class <- ifelse(st$joint_robust %in% TRUE, "composition-robust","not robust")
g <- ggplot(st, aes(beta_base, beta_adj, colour=class)) + geom_hline(yintercept=0, linetype="dotted", colour="grey60") +
  geom_vline(xintercept=0, linetype="dotted", colour="grey60") + geom_abline(slope=1, intercept=0, linetype="22", colour="grey55") +
  geom_point(size=2.1, alpha=.85) + scale_colour_manual(values=c("composition-robust"="#A6123C","not robust"="grey55")) +
  labs(x="base-model disease coefficient", y="adjusted-model disease coefficient", colour=NULL,
       title="Base vs adjusted coefficients (170 states)") + th()
ggsave(file.path(F,"fig3_base_vs_adjusted_v11.png"), g, width=W, height=5.0, dpi=300); ggsave(file.path(F,"fig3_base_vs_adjusted_v11.pdf"), g, width=W, height=5.0)

## Fig4
sv <- read.csv(file.path(A,"cbio_v3_survival_cox.csv"), stringsAsFactors=FALSE); f4 <- sv[sv$fdr<0.05,]
f4$label <- paste0(lab(f4$feature), " (", f4$context, ")")
f4 <- f4[order(f4$context, f4$hazard_ratio_per_1sd), ]; f4$label <- factor(f4$label, levels=f4$label)
xmax <- max(f4$ci_high)*1.4
g <- ggplot(f4, aes(hazard_ratio_per_1sd, label, colour=context)) + geom_vline(xintercept=1, linetype="dashed", colour="grey50") +
  geom_errorbarh(aes(xmin=ci_low, xmax=ci_high), height=.2, linewidth=.6) + geom_point(size=2.3) +
  geom_text(aes(x=xmax, label=sprintf("%.2f", hazard_ratio_per_1sd)), hjust=1, size=3.2, colour="grey20") +
  scale_x_continuous(limits=c(min(f4$ci_low)*0.9, xmax)) +
  labs(x="hazard ratio per 1 SD (95% CI)", y=NULL, colour=NULL, title="TCGA module-OS associations (FDR<0.05)") + th() +
  theme(axis.text.y=element_text(size=9))
ggsave(file.path(F,"fig4_survival_v11.png"), g, width=W, height=5.8, dpi=300); ggsave(file.path(F,"fig4_survival_v11.pdf"), g, width=W, height=5.8)

## Fig5
cna <- read.csv(file.path(A,"cbio_v3_cna_summary.csv"), stringsAsFactors=FALSE) %>% filter(gene %in% c("EGFR","ERBB2"))
mutd <- read.csv(file.path(V,"v11_mutation_denominators.csv"), stringsAsFactors=FALSE) %>% filter(gene %in% c("TP53","KRAS","EGFR"))
ord <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC"); cna$context<-factor(cna$context,levels=ord); mutd$context<-factor(mutd$context,levels=ord)
pA <- ggplot(cna, aes(context, high_amp_percent)) + geom_col(fill="#A6123C", width=.6) +
  geom_text(aes(label=sprintf("%.1f", high_amp_percent)), vjust=-0.35, size=3.2) + facet_wrap(~gene, nrow=1) +
  scale_y_continuous(expand=expansion(mult=c(0,.2))) + labs(x=NULL, y="high-level amplification (%)", title="A  Amplification (CNA-profiled)") + th(10.5)
pB <- ggplot(mutd, aes(context, pct)) + geom_col(fill="#14457B", width=.6) +
  geom_text(aes(label=sprintf("%.0f", pct)), vjust=-0.35, size=3.2) + facet_wrap(~gene, nrow=1) +
  scale_y_continuous(expand=expansion(mult=c(0,.2))) + labs(x=NULL, y="mutation (%) among profiled samples", title="B  Mutation (profiled denominators)") + th(10.5)
ggsave(file.path(F,"fig5_molecular_v11.png"), pA/pB, width=W, height=6.4, dpi=300); ggsave(file.path(F,"fig5_molecular_v11.pdf"), pA/pB, width=W, height=6.4)

## Fig6
sc <- read.csv(file.path(V,"sc_v11_patient_paired.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
sig <- sc[is.finite(sc$fdr) & sc$fdr<0.05, ]; sig$diff <- sig$case_patient_mean - sig$control_patient_mean; sig <- sig[is.finite(sig$diff),]
sig$block <- ifelse(sig$comparison_type=="same-cell-type","A  Same-cell-type comparisons (FDR<0.05)","B  Cell-identity contrasts (FDR<0.05)")
sig$annot <- ifelse(sig$n_pairs>0, paste0(sig$n_pairs," pairs"), paste0(sig$n_case_patients,"v",sig$n_control_patients))
sig$ylab <- paste0(lab(sig$module), " / ", substr(gsub("_"," ",sig$cell_type),1,26), " (", sig$context, ")")
panels <- list()
for (b in unique(sig$block)) { d <- sig[sig$block==b, ]; d <- d[order(d$diff), ]; d$ylab <- factor(d$ylab, levels=d$ylab)
  m <- max(abs(d$diff)); lim <- m*1.7
  panels[[b]] <- ggplot(d, aes(diff, ylab)) + geom_col(aes(fill=diff>0), width=.6) + geom_vline(xintercept=0, colour="grey45") +
    geom_text(aes(x=ifelse(diff>0, -m*0.06, m*0.06), label=annot), hjust=ifelse(d$diff>0,1,0), size=2.7, colour="grey25") +
    scale_fill_manual(values=c("TRUE"="#A6123C","FALSE"="#14457B"), guide="none") + scale_x_continuous(limits=c(-lim,lim)) +
    labs(x="patient-level mean difference (case - control)", y=NULL, title=b) + th(10.5) + theme(axis.text.y=element_text(size=7.6))
}
h6 <- 0.22*nrow(sig) + 2.6
ggsave(file.path(F,"fig6_sc_v11.png"), panels[[1]]/panels[[2]], width=W, height=h6, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"fig6_sc_v11.pdf"), panels[[1]]/panels[[2]], width=W, height=h6, limitsize=FALSE)

## Supp S1
xs <- read.csv(file.path(A,"xcell/context_atlas_summary_xcell_adjusted.csv"), stringsAsFactors=FALSE)
cmp <- merge(raw[,c("disease","feature","median_smd")], xs[,c("disease","feature","median_smd")], by=c("disease","feature"), suffixes=c("_marker","_xcell"))
g <- ggplot(cmp, aes(median_smd_marker, median_smd_xcell)) + geom_hline(yintercept=0, linetype="dotted", colour="grey60") +
  geom_vline(xintercept=0, linetype="dotted", colour="grey60") + geom_point(size=1.9, colour="#14457B", alpha=.8) +
  geom_smooth(method="lm", se=FALSE, colour="#A6123C", linewidth=.7) +
  labs(x="marker-proxy adjusted median SMD", y="xCell-residualization adjusted median SMD", title="Marker-proxy vs xCell sensitivity") + th()
ggsave(file.path(F,"fig_paper_xcell_vs_marker.png"), g, width=W, height=4.9, dpi=300); ggsave(file.path(F,"fig_paper_xcell_vs_marker.pdf"), g, width=W, height=4.9)

## Supp S2
xs$disease <- factor(xs$disease, levels=ctx); xs$flab <- factor(lab(xs$feature), levels=lv)
g <- ggplot(xs, aes(disease, flab)) + geom_tile(aes(fill=median_smd), colour="white", linewidth=.4) +
  geom_text(aes(label=ifelse(n_fdr_adj>=1, n_fdr_adj, ""), colour=ifelse(abs(median_smd)>1,"white","grey15")), size=3.4) +
  geom_tile(data=xs[xs$robust_xcell %in% TRUE,], fill=NA, colour="black", linewidth=1.1) + scale_colour_identity() +
  scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0, name="adjusted median SMD\n(xCell residualization)") +
  scale_x_discrete(position="top") + labs(x=NULL,y=NULL,title="Sensitivity: xCell two-step residualization",
    subtitle="digits = cohorts with FDR<0.05; asterisk = robust under this sensitivity") + th(10.5) +
  theme(axis.text.x=element_text(angle=0, size=9.5))
ggsave(file.path(F,"fig_paper_xcell_heatmap.png"), g, width=W, height=5.6, dpi=300); ggsave(file.path(F,"fig_paper_xcell_heatmap.pdf"), g, width=W, height=5.6)
cat("final v11 figures written (all <= 6.7 in wide)\n")
