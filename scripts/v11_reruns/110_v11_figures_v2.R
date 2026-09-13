#!/usr/bin/env Rscript
# v11 figures v2: larger fonts, no label overlap, horizontal axis labels, Supp S2 regenerated from frozen tables
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
BASE <- 15
th <- function(base=BASE) theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_line(colour="grey93", linewidth=.25),
        panel.grid.major.x=element_blank(),
        legend.position="bottom", legend.title=element_text(size=base-3), legend.text=element_text(size=base-3),
        strip.background=element_rect(fill="grey92", colour=NA), strip.text=element_text(face="bold", size=base-1),
        plot.title=element_text(face="bold", hjust=0, size=base),
        plot.margin=margin(10,16,10,10),
        axis.text=element_text(size=base-2), axis.title=element_text(size=base-1))

# ---------- Fig2A raw ----------
raw <- read.csv(file.path(A,"context_atlas_summary.csv"), stringsAsFactors=FALSE)
raw$disease <- factor(raw$disease, levels=ctx); raw$flab <- lab(raw$feature)
raw$flab <- factor(raw$flab, levels=rev(sort(unique(raw$flab))))
g2a <- ggplot(raw, aes(disease, flab)) + geom_tile(aes(fill=median_smd), colour="white", linewidth=.5) +
  geom_text(aes(label=ifelse(n_fdr_raw>=1, n_fdr_raw, ""), colour=ifelse(abs(median_smd)>1,"white","grey15")), size=4.2) +
  geom_point(data=raw[raw$robust_consistent,], shape=8, size=2.4, colour="black") +
  scale_colour_identity() + scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0, name="raw median SMD") +
  scale_x_discrete(position="top") + labs(x=NULL,y=NULL,title="A  Raw module states (per-cohort analysis)") + th() +
  theme(axis.text.x=element_text(angle=0, size=BASE-2))
ggsave(file.path(F11,"fig2a_raw_v11.png"), g2a, width=8.6, height=7.6, dpi=300)
ggsave(file.path(F11,"fig2a_raw_v11.pdf"), g2a, width=8.6, height=7.6)

# ---------- Fig2B adjusted ----------
js <- read.csv(file.path(V,"v11_joint_summary.csv"), stringsAsFactors=FALSE); js$flab <- lab(js$feature)
lv <- levels(raw$flab)
grid <- expand.grid(disease=ctx, flab=lv, stringsAsFactors=FALSE)
m2 <- merge(grid, js[,c("disease","flab","n_fdr","median_d_adj","joint_robust")], by=c("disease","flab"), all.x=TRUE)
m2$disease <- factor(m2$disease, levels=ctx); m2$flab <- factor(m2$flab, levels=lv)
m2$lab_txt <- ifelse(is.na(m2$median_d_adj),"n.e.", ifelse(m2$n_fdr>=1, as.character(m2$n_fdr), ""))
g2b <- ggplot(m2, aes(disease, flab)) + geom_tile(aes(fill=median_d_adj), colour="white", linewidth=.5) +
  geom_text(aes(label=lab_txt, colour=ifelse(!is.na(median_d_adj)&abs(median_d_adj)>1,"white","grey15")), size=4.2) +
  geom_point(data=m2[!is.na(m2$joint_robust)&m2$joint_robust,], shape=23, size=3.0, fill="black", colour="white", stroke=.6) +
  scale_colour_identity() + scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0, na.value="grey85",
      name="adjusted coefficient (SD units)") + scale_x_discrete(position="top") +
  labs(x=NULL,y=NULL,title="B  Adjusted model (base vs adjusted; n.e. = not estimable)") + th() +
  theme(axis.text.x=element_text(angle=0, size=BASE-2))
ggsave(file.path(F11,"fig2b_adjusted_v11.png"), g2b, width=8.6, height=7.6, dpi=300)
ggsave(file.path(F11,"fig2b_adjusted_v11.pdf"), g2b, width=8.6, height=7.6)

# ---------- Fig3 base vs adjusted ----------
pc <- read.csv(file.path(V,"v11_percohort_effects.csv"), stringsAsFactors=FALSE)
st <- pc %>% group_by(disease, feature) %>% summarise(beta_base=median(beta_base, na.rm=TRUE),
        beta_adj=median(beta_adj, na.rm=TRUE), .groups="drop") %>%
  left_join(js %>% select(disease, feature, joint_robust), by=c("disease","feature"))
st$class <- ifelse(st$joint_robust %in% TRUE, "composition-robust","not robust")
g3 <- ggplot(st, aes(beta_base, beta_adj, colour=class)) +
  geom_hline(yintercept=0, linetype="dotted", colour="grey60") + geom_vline(xintercept=0, linetype="dotted", colour="grey60") +
  geom_abline(slope=1, intercept=0, linetype="22", colour="grey55") + geom_point(size=2.8, alpha=.85) +
  scale_colour_manual(values=c("composition-robust"="#A6123C","not robust"="grey55")) +
  labs(x="base-model disease coefficient", y="adjusted-model disease coefficient", colour=NULL,
       title="Base vs adjusted coefficients (same outcome units; 170 states)") + th()
ggsave(file.path(F11,"fig3_base_vs_adjusted_v11.png"), g3, width=7.2, height=6.2, dpi=300)
ggsave(file.path(F11,"fig3_base_vs_adjusted_v11.pdf"), g3, width=7.2, height=6.2)

# ---------- Fig4 forest: short labels, value column, no overlap ----------
sv <- read.csv(file.path(A,"cbio_v3_survival_cox.csv"), stringsAsFactors=FALSE); f4 <- sv[sv$fdr<0.05,]
f4$label <- paste0(lab(f4$feature), " (", f4$context, ")")
f4 <- f4[order(f4$context, f4$hazard_ratio_per_1sd), ]; f4$label <- factor(f4$label, levels=f4$label)
xmax <- max(f4$ci_high)*1.35
g4 <- ggplot(f4, aes(hazard_ratio_per_1sd, label, colour=context)) +
  geom_vline(xintercept=1, linetype="dashed", colour="grey50") +
  geom_errorbarh(aes(xmin=ci_low, xmax=ci_high), height=.22, linewidth=.7) + geom_point(size=3) +
  geom_text(aes(x=xmax, label=sprintf("%.2f", hazard_ratio_per_1sd)), hjust=1, size=4.2, colour="grey20") +
  scale_x_continuous(limits=c(min(f4$ci_low)*0.9, xmax), expand=expansion(mult=c(.02,.02))) +
  labs(x="hazard ratio per 1 SD (95% CI)", y=NULL, colour=NULL, title="TCGA module-OS associations (FDR<0.05)") + th(13) +
  theme(axis.text.y=element_text(size=11))
ggsave(file.path(F11,"fig4_survival_v11.png"), g4, width=8.2, height=7.4, dpi=300)
ggsave(file.path(F11,"fig4_survival_v11.pdf"), g4, width=8.2, height=7.4)

# ---------- Fig5 molecular (bigger annotation text) ----------
cna <- read.csv(file.path(A,"cbio_v3_cna_summary.csv"), stringsAsFactors=FALSE) %>% filter(gene %in% c("EGFR","ERBB2"))
mutd <- read.csv(file.path(V,"v11_mutation_denominators.csv"), stringsAsFactors=FALSE) %>% filter(gene %in% c("TP53","KRAS","EGFR"))
ord <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC")
cna$context <- factor(cna$context, levels=ord); mutd$context <- factor(mutd$context, levels=ord)
pA <- ggplot(cna, aes(context, high_amp_percent)) + geom_col(fill="#A6123C", width=.6) +
  geom_text(aes(label=sprintf("%.1f", high_amp_percent)), vjust=-0.35, size=4) + facet_wrap(~gene, nrow=1) +
  scale_y_continuous(expand=expansion(mult=c(0,.18))) +
  labs(x=NULL, y="high-level amplification (%)", title="A  Amplification (CNA-profiled samples)") + th(13)
pB <- ggplot(mutd, aes(context, pct)) + geom_col(fill="#14457B", width=.6) +
  geom_text(aes(label=sprintf("%.0f", pct)), vjust=-0.35, size=4) + facet_wrap(~gene, nrow=1) +
  scale_y_continuous(expand=expansion(mult=c(0,.18))) +
  labs(x=NULL, y="mutation (%) among profiled samples", title="B  Mutation (mutation-profiled denominators)") + th(13)
g5 <- pA / pB + plot_annotation(title="Molecular context across six cancers", theme=theme(plot.title=element_text(face="bold", size=15)))
ggsave(file.path(F11,"fig5_molecular_v11.png"), g5, width=9, height=8, dpi=300)
ggsave(file.path(F11,"fig5_molecular_v11.pdf"), g5, width=9, height=8)

# ---------- Fig6 single cell: labels wrapped, pair column separate, generous margins ----------
sc <- read.csv(file.path(V,"sc_v11_patient_paired.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
sig <- sc[is.finite(sc$fdr) & sc$fdr<0.05, ]
sig$diff <- sig$case_patient_mean - sig$control_patient_mean
sig$block <- ifelse(sig$comparison_type=="same-cell-type","A","B")
sig$cell <- ifelse(sig$n_pairs>0, paste0(sig$n_pairs," pairs"), paste0(sig$n_case_patients," vs ",sig$n_control_patients))
sig$ylab <- paste0(lab(sig$module), " | ", substr(gsub("_"," ",sig$cell_type),1,26))
wrapped <- function(x,n=26) vapply(strwrap(x, width=n, simplify=FALSE), paste, character(1), collapse="\n")
titles <- c(A="A  Same-cell-type comparisons (FDR<0.05; pair counts shown)",
            B="B  Cell-identity contrasts (malignant vs normal epithelium; FDR<0.05)")
plots <- list()
for (b in c("A","B")) {
  d <- sig[sig$block==b, ]
  if(!nrow(d)) { plots[[b]] <- ggplot()+theme_void(); next }
  d <- d[order(d$diff), ]; d$ylab <- factor(wrapped(d$ylab), levels=wrapped(d$ylab)[order(d$diff)])
  xmax <- max(abs(d$diff))*1.5
  plots[[b]] <- ggplot(d, aes(diff, ylab)) + geom_col(aes(fill=diff>0), width=.62) +
    geom_text(aes(x=ifelse(diff>0, -xmax*0.02, xmax*0.02), label=cell), hjust=ifelse(d$diff>0,1,0), size=4, colour="grey20") +
    geom_vline(xintercept=0, colour="grey45") +
    scale_fill_manual(values=c("TRUE"="#A6123C","FALSE"="#14457B"), guide="none") +
    scale_x_continuous(limits=c(-xmax, xmax)) +
    labs(x="patient-level mean difference (case - control)", y=NULL, title=titles[[b]]) + th(13) +
    theme(axis.text.y=element_text(size=11))
}
g6 <- plots$A / plots$B + plot_layout(heights=c(max(2,sum(sig$block=="A")), max(2,sum(sig$block=="B"))))
ggsave(file.path(F11,"fig6_sc_v11.png"), g6, width=9.5, height=12, dpi=300, limitsize=FALSE)
ggsave(file.path(F11,"fig6_sc_v11.pdf"), g6, width=9.5, height=12, limitsize=FALSE)

# ---------- Supp S1 marker vs xCell (rebuild with big fonts) ----------
mk <- read.csv(file.path(A,"context_atlas_summary.csv"), stringsAsFactors=FALSE)
xs <- read.csv(file.path(A,"xcell/context_atlas_summary_xcell_adjusted.csv"), stringsAsFactors=FALSE)
cmp <- merge(mk[,c("disease","feature","median_smd")], xs[,c("disease","feature","median_smd")],
             by=c("disease","feature"), suffixes=c("_marker","_xcell"))
gS1 <- ggplot(cmp, aes(median_smd_marker, median_smd_xcell)) + geom_hline(yintercept=0, linetype="dotted", colour="grey60") +
  geom_vline(xintercept=0, linetype="dotted", colour="grey60") + geom_point(size=2.4, colour="#14457B", alpha=.8) +
  geom_smooth(method="lm", se=FALSE, colour="#A6123C", linewidth=.8) +
  labs(x="marker-proxy adjusted median SMD", y="xCell-residualization adjusted median SMD",
       title="Marker-proxy vs xCell sensitivity (170 states)") + th(13)
ggsave(file.path(F11,"fig_paper_xcell_vs_marker.png"), gS1, width=7.4, height=6.4, dpi=300)
ggsave(file.path(F11,"fig_paper_xcell_vs_marker.pdf"), gS1, width=7.4, height=6.4)

# ---------- Supp S2 xCell-residualization heatmap (regenerated from frozen table) ----------
xs$disease <- factor(xs$disease, levels=ctx); xs$flab <- factor(lab(xs$feature), levels=rev(levels(raw$flab)))
gS2 <- ggplot(xs, aes(disease, flab)) + geom_tile(aes(fill=median_smd), colour="white", linewidth=.5) +
  geom_text(aes(label=ifelse(n_fdr_adj>=1, n_fdr_adj, ""), colour=ifelse(abs(median_smd)>1,"white","grey15")), size=4.2) +
  geom_point(data=xs[xs$robust_xcell %in% TRUE,], shape=8, size=2.4, colour="black") +
  scale_colour_identity() + scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0,
      name="adj. median SMD (xCell residualization)") + scale_x_discrete(position="top") +
  labs(x=NULL,y=NULL,title="Sensitivity: xCell two-step residualization (digits = cohorts FDR<0.05; asterisk = robust)") + th(13) +
  theme(axis.text.x=element_text(angle=0, size=11))
ggsave(file.path(F11,"fig_paper_xcell_heatmap.png"), gS2, width=8.6, height=7.6, dpi=300)
ggsave(file.path(F11,"fig_paper_xcell_heatmap.pdf"), gS2, width=8.6, height=7.6)
cat("v11 figures v2 written\n")
