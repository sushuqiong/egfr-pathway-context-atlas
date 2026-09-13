#!/usr/bin/env Rscript
# v11 figures, generated strictly from frozen result tables
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2); library(patchwork)})
A <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
V <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/reruns/results"
F11 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/02_图片"
dir.create(F11, recursive=TRUE, showWarnings=FALSE)
ctx <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma")
lab <- function(x){ x<-gsub("_AXIS$","",x); x<-gsub("_RECEPTORS","",x)
  m<-c("ERBB_LIGANDS"="ERBB-L","PDGFR_KIT_CSF1R"="PDGFR-KIT","RET_ALK_NTRK"="RET/ALK","VEGF_PDGF"="VEGF/PDGF",
       "TIE_ANGPT"="TIE/Ang","HGF_MET"="HGF/MET","TAM_AXL"="TAM/AXL","IGF_INSR"="IGF/INSR","TGFB_SMAD"="TGFb",
       "WNT_CTNNB1"="WNT/b-cat","PI3K_AKT"="PI3K-AKT","RAS_MAPK"="RAS-MAPK","JAK_STAT"="JAK-STAT","SRC_FAK"="SRC/FAK")
  ifelse(x %in% names(m), m[x], x) }
th <- function(base=12) theme_bw(base_size=base) + theme(panel.grid.minor=element_blank(),
  panel.grid.major=element_line(colour="grey93", linewidth=.25), legend.position="bottom",
  strip.background=element_rect(fill="grey92", colour=NA), strip.text=element_text(face="bold"),
  plot.title=element_text(face="bold", hjust=0, size=base+1))

raw <- read.csv(file.path(A,"context_atlas_summary.csv"), stringsAsFactors=FALSE)
raw$disease <- factor(raw$disease, levels=ctx); raw$flab <- factor(lab(raw$feature))
levels_f <- rev(levels(raw$flab))
raw$flab <- factor(raw$flab, levels=levels_f)

## Fig2A raw
g2a <- ggplot(raw, aes(disease, flab)) + geom_tile(aes(fill=median_smd), colour="white", linewidth=.4) +
  geom_text(aes(label=ifelse(n_fdr_raw>=1, n_fdr_raw, ""), colour=ifelse(abs(median_smd)>1,"white","grey20")), size=2.5) +
  geom_point(data=raw[raw$robust_consistent,], shape=8, size=1.7, colour="black") +
  scale_colour_identity() + scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0, name="raw median SMD") +
  scale_x_discrete(position="top") + labs(x=NULL,y=NULL,title="A  Raw states (per-cohort analysis)") + th() +
  theme(axis.text.x=element_text(angle=35,hjust=0,size=10))
ggsave(file.path(F11,"fig2a_raw_v11.png"), g2a, width=8.2, height=7.0, dpi=300)
ggsave(file.path(F11,"fig2a_raw_v11.pdf"), g2a, width=8.2, height=7.0)

## Fig2B adjusted (two-model)
js <- read.csv(file.path(V,"v11_joint_summary.csv"), stringsAsFactors=FALSE); js$flab <- lab(js$feature)
grid <- expand.grid(disease=ctx, flab=levels_f, stringsAsFactors=FALSE)
m2 <- merge(grid, js[,c("disease","flab","n_analysed","n_fdr","median_d_adj","joint_robust")], by=c("disease","flab"), all.x=TRUE)
m2$disease <- factor(m2$disease, levels=ctx); m2$flab <- factor(m2$flab, levels=levels_f)
m2$lab_txt <- ifelse(is.na(m2$median_d_adj),"n.e.", ifelse(m2$n_fdr>=1, as.character(m2$n_fdr), ""))
g2b <- ggplot(m2, aes(disease, flab)) + geom_tile(aes(fill=median_d_adj), colour="white", linewidth=.4) +
  geom_text(aes(label=lab_txt, colour=ifelse(!is.na(median_d_adj)&abs(median_d_adj)>1,"white","grey20")), size=2.5) +
  geom_point(data=m2[!is.na(m2$joint_robust)&m2$joint_robust,], shape=23, size=2.3, fill="black", colour="white", stroke=.5) +
  scale_colour_identity() + scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0, na.value="grey85",
      name="adjusted coefficient (SD units)") + scale_x_discrete(position="top") +
  labs(x=NULL,y=NULL,title="B  Adjusted model (base vs adjusted; n.e. = not estimable)") + th() +
  theme(axis.text.x=element_text(angle=35,hjust=0,size=10))
ggsave(file.path(F11,"fig2b_adjusted_v11.png"), g2b, width=8.2, height=7.0, dpi=300)
ggsave(file.path(F11,"fig2b_adjusted_v11.pdf"), g2b, width=8.2, height=7.0)

## Fig3 base vs adjusted coefficients
pc <- read.csv(file.path(V,"v11_percohort_effects.csv"), stringsAsFactors=FALSE)
st <- pc %>% group_by(disease, feature) %>% summarise(beta_base=median(beta_base, na.rm=TRUE),
       beta_adj=median(beta_adj, na.rm=TRUE), .groups="drop") %>%
  left_join(js %>% select(disease, feature, joint_robust), by=c("disease","feature"))
st$class <- ifelse(st$joint_robust %in% TRUE, "composition-robust","not robust")
g3 <- ggplot(st, aes(beta_base, beta_adj, colour=class)) +
  geom_hline(yintercept=0, linetype="dotted", colour="grey60") + geom_vline(xintercept=0, linetype="dotted", colour="grey60") +
  geom_abline(slope=1, intercept=0, linetype="22", colour="grey55") + geom_point(size=2, alpha=.85) +
  scale_colour_manual(values=c("composition-robust"="#A6123C","not robust"="grey55")) +
  labs(x="base-model disease coefficient", y="adjusted-model disease coefficient", colour=NULL,
       title="Base vs adjusted coefficients (same outcome units; n=170 states)") + th()
ggsave(file.path(F11,"fig3_base_vs_adjusted_v11.png"), g3, width=6.6, height=5.6, dpi=300)
ggsave(file.path(F11,"fig3_base_vs_adjusted_v11.pdf"), g3, width=6.6, height=5.6)

## Fig4 forest (unchanged numbers)
sv <- read.csv(file.path(A,"cbio_v3_survival_cox.csv"), stringsAsFactors=FALSE); f4 <- sv[sv$fdr<0.05,]
f4$context <- factor(f4$context, levels=c("LUAD","CRC","STAD","PAAD","HCC","ESCC"))
f4$label <- paste0(lab(f4$feature), " (", f4$context, ")"); f4 <- f4[order(f4$context, f4$hazard_ratio_per_1sd),]
f4$label <- factor(f4$label, levels=f4$label)
g4 <- ggplot(f4, aes(hazard_ratio_per_1sd, label, colour=context)) + geom_vline(xintercept=1, linetype="dashed", colour="grey50") +
  geom_errorbarh(aes(xmin=ci_low, xmax=ci_high), height=.25) + geom_point(size=2.4) +
  labs(x="hazard ratio per 1 SD (95% CI)", y=NULL, colour="context", title="TCGA module-OS associations (FDR<0.05)") + th(11)
ggsave(file.path(F11,"fig4_survival_v11.png"), g4, width=7.4, height=6.6, dpi=300)
ggsave(file.path(F11,"fig4_survival_v11.pdf"), g4, width=7.4, height=6.6)

## Fig5 profiled-only denominators
cna <- read.csv(file.path(A,"cbio_v3_cna_summary.csv"), stringsAsFactors=FALSE) %>% filter(gene %in% c("EGFR","ERBB2"))
mutd <- read.csv(file.path(V,"v11_mutation_denominators.csv"), stringsAsFactors=FALSE) %>% filter(gene %in% c("TP53","KRAS","EGFR"))
ord <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC")
cna$context <- factor(cna$context, levels=ord); mutd$context <- factor(mutd$context, levels=ord)
pA <- ggplot(cna, aes(context, high_amp_percent)) + geom_col(fill="#A6123C", width=.62) +
  geom_text(aes(label=sprintf("%.1f", high_amp_percent)), vjust=-0.4, size=2.5) + facet_wrap(~gene, nrow=1, scales="free_y") +
  labs(x=NULL, y="high-level amplification (%)", title="A  Amplification (CNA-profiled samples)") + th(10.5) +
  theme(axis.text.x=element_text(angle=35,hjust=1,size=9))
pB <- ggplot(mutd, aes(context, pct)) + geom_col(fill="#14457B", width=.62) +
  geom_text(aes(label=sprintf("%.0f", pct)), vjust=-0.4, size=2.5) + facet_wrap(~gene, nrow=1, scales="free_y") +
  labs(x=NULL, y="mutation (%) among mutation-profiled samples", title="B  Mutation (profiled-only denominators)") + th(10.5) +
  theme(axis.text.x=element_text(angle=35,hjust=1,size=9))
g5 <- pA / pB + plot_annotation(title="Molecular context across six cancers")
ggsave(file.path(F11,"fig5_molecular_v11.png"), g5, width=8.4, height=7.4, dpi=300)
ggsave(file.path(F11,"fig5_molecular_v11.pdf"), g5, width=8.4, height=7.4)

## Fig6 single cell: same-cell-type (with pairs) vs cell-identity
sc <- read.csv(file.path(V,"sc_v11_patient_paired.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
sig <- sc[is.finite(sc$fdr) & sc$fdr<0.05, ]
mk <- function(d, ttl){
  if(!nrow(d)) return(ggplot() + theme_void() + labs(title=ttl))
  d$diff <- d$case_patient_mean - d$control_patient_mean
  d$lab <- paste0(lab(d$module), " | ", substr(d$cell_type,1,30),
                  ifelse(d$n_pairs>0, paste0("  (", d$n_pairs, " pairs)"), paste0("  (", d$n_case_patients, "v", d$n_control_patients, ")")))
  d <- d[order(d$diff), ]; d$lab <- factor(d$lab, levels=d$lab)
  ggplot(d, aes(diff, lab, fill=diff>0)) + geom_col(width=.62) + geom_vline(xintercept=0, colour="grey40") +
    scale_fill_manual(values=c("TRUE"="#A6123C","FALSE"="#14457B"), guide="none") +
    labs(x="patient-level mean difference (case - control)", y=NULL, title=ttl) + th(9.5)
}
pL <- mk(sig[sig$comparison_type=="same-cell-type",], "A  Same-cell-type comparisons (family-wise FDR<0.05)")
pR <- mk(sig[sig$comparison_type=="cell-identity",], "B  Cell-identity contrasts (malignant vs normal epithelium; FDR<0.05)")
g6 <- pL / pR + plot_layout(heights=c(max(2,sum(sig$comparison_type=="same-cell-type")), max(2,sum(sig$comparison_type=="cell-identity"))))
ggsave(file.path(F11,"fig6_sc_v11.png"), g6, width=8.6, height=11, dpi=300, limitsize=FALSE)
ggsave(file.path(F11,"fig6_sc_v11.pdf"), g6, width=8.6, height=11, limitsize=FALSE)
cat("v11 figures written to", F11, "\n")
