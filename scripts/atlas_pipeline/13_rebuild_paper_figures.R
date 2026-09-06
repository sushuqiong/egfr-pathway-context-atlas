#!/usr/bin/env Rscript
# Systematic professional rebuild of all paper figures (no empty panels, no overlap, no truncation)
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2)})
RES <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
FIG <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/figures"
rd <- function(f,...) read.csv(file.path(RES,f), stringsAsFactors=FALSE, check.names=FALSE, ...)
theme_ac <- function(base=12){
  theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(),
        panel.grid.major=element_line(colour="grey93", linewidth=.25),
        axis.text=element_text(colour="grey10"),
        axis.ticks=element_line(colour="grey40"),
        legend.position="bottom", legend.title=element_text(size=base-1),
        legend.text=element_text(size=base-1.5),
        strip.background=element_rect(fill="grey92", colour=NA),
        strip.text=element_text(face="bold", size=base-0.5),
        plot.title=element_text(face="bold", hjust=0, size=base+2, margin=margin(b=6)),
        plot.margin=margin(6,8,6,4))
}
ctx_levels <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma")

# ---------- 1) heatmap raw ----------
d <- rd("context_atlas_summary.csv")
d$disease <- factor(d$disease, levels=ctx_levels)
d$feature <- factor(d$feature, levels=rev(sort(unique(d$feature))))
d$txt_col <- ifelse(abs(d$median_smd)>1.1,"white","grey25")
g <- ggplot(d, aes(disease, feature)) + geom_tile(aes(fill=median_smd), colour="white", linewidth=.4) +
  geom_text(aes(label=sprintf("%.1f", median_smd), colour=txt_col), size=2.5) +
  geom_point(data=d[d$robust_consistent & d$n_fdr_raw>=2, ], aes(disease, feature), shape=8, size=1.6, colour="#111111") +
  scale_colour_identity() +
  scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0,
                       name="median SMD (lesion vs control)") +
  scale_x_discrete(position="top") +
  labs(x=NULL, y=NULL, title="A  Raw module states across ten contexts (27 GEO cohorts)") +
  theme_ac(12) + theme(axis.text.x=element_text(angle=35, hjust=0, size=10.5), legend.key.width=unit(1.5,"cm"))
ggsave(file.path(FIG,"atlas_heatmap_raw.png"), g, width=8.2, height=7.2, dpi=300)
ggsave(file.path(FIG,"atlas_heatmap_raw.pdf"), g, width=8.2, height=7.2)

# ---------- 2) xCell heatmap ----------
x <- rd("xcell/context_atlas_summary_xcell_adjusted.csv")
x$disease <- factor(x$disease, levels=ctx_levels)
x$feature <- factor(x$feature, levels=rev(sort(unique(x$feature))))
x$lab <- ifelse(is.na(x$n_fdr_adj) | x$n_fdr_adj==0, "", as.character(x$n_fdr_adj))
x$txtc <- ifelse(abs(x$median_smd)>1.1,"white","grey25")
g <- ggplot(x, aes(disease, feature)) + geom_tile(aes(fill=median_smd), colour="white", linewidth=.4) +
  geom_text(aes(label=lab, colour=txtc), size=2.6) +
  geom_point(data=x[x$robust_xcell, ], aes(disease, feature), shape=8, size=2, colour="#111111") +
  scale_colour_identity() +
  scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0,
                       name="xCell-adjusted median SMD") +
  scale_x_discrete(position="top") +
  labs(x=NULL, y=NULL, title="B  Composition-adjusted states (xCell residualization)") +
  theme_ac(12) + theme(axis.text.x=element_text(angle=35, hjust=0, size=10.5), legend.key.width=unit(1.5,"cm"))
ggsave(file.path(FIG,"fig_paper_xcell_heatmap.png"), g, width=8.2, height=7.2, dpi=300)
ggsave(file.path(FIG,"fig_paper_xcell_heatmap.pdf"), g, width=8.2, height=7.2)

# ---------- 3) composition scatter ----------
mk <- rd("module_effects_composition_adjusted.csv") %>% filter(role %in% c("discovery","validation")) %>%
  group_by(disease, feature) %>% summarise(marker_med=median(smd, na.rm=TRUE), .groups="drop")
xr <- rd("xcell/module_effects_composition_adjusted_xcell.csv") %>% filter(role %in% c("discovery","validation")) %>%
  group_by(disease, feature) %>% summarise(xcell_med=median(smd, na.rm=TRUE), .groups="drop")
xs <- rd("xcell/context_atlas_summary_xcell_adjusted.csv") %>% select(disease, feature, robust_xcell)
c2 <- merge(mk, xr, by=c("disease","feature")) %>% merge(xs, by=c("disease","feature")) %>%
  filter(is.finite(marker_med) & is.finite(xcell_med))
c2$class <- ifelse(c2$robust_xcell, "xCell-composition-robust", "not composition-robust")
g <- ggplot(c2, aes(marker_med, xcell_med, colour=class)) +
  geom_abline(slope=1, intercept=0, linetype="22", colour="grey55") +
  geom_hline(yintercept=0, linetype="dotted", colour="grey60") + geom_vline(xintercept=0, linetype="dotted", colour="grey60") +
  geom_point(size=2, alpha=.85) + scale_color_manual(values=c("xCell-composition-robust"="#A6123C","not composition-robust"="#7a7a7a")) +
  labs(x="Marker-proxy adjusted median SMD", y="xCell-adjusted median SMD",
       colour=NULL, title="Composition adjustment: xCell vs marker proxy (n=170)") +
  theme_ac(12) + guides(colour=guide_legend(override.aes=list(size=2.6)))
ggsave(file.path(FIG,"fig_paper_composition_adjustment.png"), g, width=6.4, height=5.6, dpi=300)
ggsave(file.path(FIG,"fig_paper_composition_adjustment.pdf"), g, width=6.4, height=5.6)

# ---------- 4) survival matrix ----------
sv <- rd("cbio_v3_survival_cox.csv")
sv$loghr <- log(sv$hazard_ratio_per_1sd)
sv$sig <- ifelse(sv$fdr<0.05,"*","")
sv$disease <- factor(sv$context, levels=rev(ctx_levels[1:6]))
feats <- c("TIE_ANGPT_AXIS","RET_ALK_NTRK","PDGFR_KIT_CSF1R","VEGF_PDGF_AXIS","TAM_AXL_AXIS",
           "HGF_MET_AXIS","ERBB_RECEPTORS","ERBB_LIGANDS","EPH_RECEPTORS","IGF_INSR_AXIS",
           "FGFR_AXIS","RAS_MAPK","PI3K_AKT","JAK_STAT","SRC_FAK","TGFB_SMAD","WNT_CTNNB1","EGFR")
sv$feature <- factor(sv$feature, levels=feats)
sv$txtc <- ifelse(abs(sv$loghr)>log(1.4),"white","grey20")
g <- ggplot(sv, aes(disease, feature)) + geom_tile(aes(fill=loghr), colour="white", linewidth=.35) +
  geom_text(aes(label=sprintf("%.2f%s", hazard_ratio_per_1sd, sig), colour=txtc), size=2.3) +
  scale_colour_identity() +
  scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0,
                       name="log HR per 1 SD (OS)") +
  labs(x=NULL, y=NULL, title="TCGA module-OS associations in six cancers (* FDR<0.05)") +
  theme_ac(12) + theme(axis.text.x=element_text(angle=35, hjust=0, size=10.5), legend.key.width=unit(1.3,"cm"))
ggsave(file.path(FIG,"fig_paper_survival_matrix.png"), g, width=8.0, height=7.6, dpi=300)
ggsave(file.path(FIG,"fig_paper_survival_matrix.pdf"), g, width=8.0, height=7.6)

# ---------- 5) molecular dot charts (no empty bars) ----------
cna <- rd("cbio_v3_cna_summary.csv") %>% filter(gene %in% c("EGFR","ERBB2"))
cna$disease <- factor(cna$context, levels=ctx_levels[1:6])
mut <- rd("cbio_v3_mutation_summary.csv") %>% filter(gene %in% c("TP53","KRAS","EGFR"))
mut$disease <- factor(mut$context, levels=ctx_levels[1:6])
pa <- ggplot(cna, aes(disease, high_amp_percent)) + geom_segment(aes(xend=disease, yend=0), colour="grey65") +
  geom_point(size=3.2, colour="#A6123C") +
  geom_text(aes(label=ifelse(high_amp_percent>0, sprintf("%.1f%%", high_amp_percent),"0")), nudge_y=0.8, size=2.4) +
  facet_wrap(~gene, ncol=2, scales="free_y") +
  labs(x=NULL, y="high-level amplification (%)", title="EGFR / ERBB2 amplification") +
  theme_ac(11) + theme(axis.text.x=element_text(angle=35, hjust=1, size=9.5))
pm <- ggplot(mut, aes(disease, mutated_percent)) + geom_segment(aes(xend=disease, yend=0), colour="grey65") +
  geom_point(size=3.2, colour="#14457B") +
  geom_text(aes(label=sprintf("%.0f%%", mutated_percent)), nudge_y=2.2, size=2.3) +
  facet_wrap(~gene, ncol=3, scales="free_y") +
  labs(x=NULL, y="mutated (%)", title="TP53 / KRAS / EGFR mutations") +
  theme_ac(11) + theme(axis.text.x=element_text(angle=35, hjust=1, size=9.5))
ggsave(file.path(FIG,"fig_paper_molecular_context.png"), pa, width=7.0, height=3.2, dpi=300)
ggsave(file.path(FIG,"fig_paper_molecular_context.pdf"), pa, width=7.0, height=3.2)
ggsave(file.path(FIG,"fig_paper_molecular_context_mut.png"), pm, width=9.0, height=3.4, dpi=300)
ggsave(file.path(FIG,"fig_paper_molecular_context_mut.pdf"), pm, width=9.0, height=3.4)

# ---------- 6) single-cell source (only FDR hits, compact) ----------
sc <- rd("sc_top_hit_cell_source_validation.csv") %>% filter(context %in% c("CRC","IBD","STAD"))
sc$diff <- suppressWarnings(as.numeric(sc$case_patient_mean)) - suppressWarnings(as.numeric(sc$control_patient_mean))
sc$fdr <- suppressWarnings(as.numeric(sc$fdr))
hits <- sc %>% filter(!is.na(fdr) & fdr<0.05 & is.finite(diff)) %>%
  mutate(ct=cell_type, dir=ifelse(diff>0,"up in case","down in case"),
         feats=paste(module, ct, sep="\n"))
if(nrow(hits)>0){
  hits <- hits %>% arrange(context, module, diff)
  hits$ord <- seq_len(nrow(hits))
  hits$context <- factor(hits$context, levels=c("CRC","IBD","STAD"))
  g <- ggplot(hits, aes(reorder(paste(module,ct,sep=" | "), ord), diff, fill=diff>0)) +
    geom_col(width=.62) + coord_flip() +
    geom_hline(yintercept=0, colour="grey40") +
    scale_fill_manual(values=c("TRUE"="#A6123C","FALSE"="#14457B"), guide="none") +
    facet_grid(context~., scales="free_y", space="free_y") +
    labs(x=NULL, y="patient-level mean difference (case-control)",
         title="Single-cell source hits (FDR<0.05), by cell type") +
    theme_ac(11) + theme(axis.text.y=element_text(size=8.5))
  ggsave(file.path(FIG,"fig_paper_sc_source.png"), g, width=7.6, height=ifelse(nrow(hits)>14, 8.2, 5.4), dpi=300)
  ggsave(file.path(FIG,"fig_paper_sc_source.pdf"), g, width=7.6, height=ifelse(nrow(hits)>14, 8.2, 5.4))
} else cat("no sc hits\n")

# ---------- 7) xCell-vs-marker ----------
g <- ggplot(c2, aes(marker_med, xcell_med)) + geom_abline(slope=1, linetype="22", colour="grey55") +
  geom_point(aes(colour=class), size=1.8, alpha=.85) +
  scale_color_manual(values=c("xCell-composition-robust"="#A6123C","not composition-robust"="#7a7a7a")) +
  labs(x="marker-proxy adjusted median SMD", y="xCell-adjusted median SMD", colour=NULL,
       title="Sensitivity: marker proxy vs xCell deconvolution") +
  theme_ac(11)
ggsave(file.path(FIG,"fig_paper_xcell_vs_marker.png"), g, width=5.6, height=4.8, dpi=300)
ggsave(file.path(FIG,"fig_paper_xcell_vs_marker.pdf"), g, width=5.6, height=4.8)
cat("all rebuilt\n")
