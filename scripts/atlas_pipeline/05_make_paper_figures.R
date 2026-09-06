#!/usr/bin/env Rscript
# Paper figures (step 3): (A) OS survival effect matrix, (B) molecular context bars,
# (C) raw vs composition-adjusted module SMDs.
suppressPackageStartupMessages({library(dplyr); library(ggplot2); library(tidyr); library(patchwork)})
ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
RES <- file.path(ROOT, "results"); FIG <- file.path(ROOT, "figures")
rd <- function(f) read.csv(file.path(RES, f), stringsAsFactors=FALSE, check.names=FALSE, fileEncoding="UTF-8-BOM")
ctx_levels <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC")
ctx_lab <- c(LUAD="LUAD",CRC="CRC",STAD="STAD",PAAD="PAAD",HCC="HCC",ESCC="ESCC")
mods <- c("ERBB_RECEPTORS","ERBB_LIGANDS","RAS_MAPK","PI3K_AKT","FGFR_AXIS","VEGF_PDGF_AXIS",
          "PDGFR_KIT_CSF1R","HGF_MET_AXIS","TAM_AXL_AXIS","IGF_INSR_AXIS","RET_ALK_NTRK",
          "EPH_RECEPTORS","TIE_ANGPT_AXIS","JAK_STAT","SRC_FAK","TGFB_SMAD","WNT_CTNNB1")
mod_lab <- c(ERBB_RECEPTORS="ERBB rec",ERBB_LIGANDS="ERBB lig",RAS_MAPK="RAS/MAPK",PI3K_AKT="PI3K/AKT",
  FGFR_AXIS="FGFR",VEGF_PDGF_AXIS="VEGF/PDGF",PDGFR_KIT_CSF1R="PDGFR/KIT",HGF_MET_AXIS="HGF/MET",
  TAM_AXL_AXIS="AXL/TAM",IGF_INSR_AXIS="IGF/INSR",RET_ALK_NTRK="RET/ALK/NTRK",EPH_RECEPTORS="EPH",
  TIE_ANGPT_AXIS="Ang/Tie2",JAK_STAT="JAK-STAT",SRC_FAK="SRC/FAK",TGFB_SMAD="TGFb/SMAD",WNT_CTNNB1="WNT/bcat")

# ---------- A. OS survival effect matrix (six cancers, continuous module scores) ----------
s <- rd("cbio_v3_survival_cox.csv")
s$feature <- ifelse(s$feature == "EGFR", "EGFR", as.character(s$feature))
s$hr <- suppressWarnings(as.numeric(s$hazard_ratio_per_1sd)); s$fdr <- suppressWarnings(as.numeric(s$fdr))
s$logHR <- log(s$hr)
plotA <- s %>% filter(feature %in% c("EGFR", mods)) %>% mutate(
  feature = factor(feature, levels = rev(mods)),
  context = factor(context, levels = ctx_levels),
  sig = ifelse(!is.na(fdr) & fdr < 0.05, "FDR<0.05", ""))
gA <- ggplot(plotA, aes(context, feature, fill = logHR)) +
  geom_tile(colour="white") +
  geom_text(aes(label = ifelse(sig=="FDR<0.05", "*", "")), size = 4, colour="black") +
  scale_fill_gradient2(low="#1B5E9C", mid="white", high="#B02040", midpoint=0,
                       name="log(HR) per 1 SD (OS)") +
  labs(x=NULL, y=NULL, title="A. TCGA OS associations of growth-factor modules (six cancers)") +
  theme_minimal(base_size=11) + theme(axis.text.x=element_text(angle=45,hjust=1), panel.grid=element_blank())
ggsave(file.path(FIG,"fig_paper_survival_matrix.png"), gA, width=8, height=8.5, dpi=300)
ggsave(file.path(FIG,"fig_paper_survival_matrix.pdf"), gA, width=8, height=8.5)

# ---------- B. Molecular context bars (CNA high-level amp; mutations) ----------
cna <- rd("cbio_v3_cna_summary.csv"); mut <- rd("cbio_v3_mutation_summary.csv")
cna$context <- factor(cna$context, levels=ctx_levels)
for (g in c("EGFR","ERBB2")) {
  sub <- cna %>% filter(gene == g)
  p <- ggplot(sub, aes(context, high_amp_percent)) + geom_col(fill="#B02040", width=0.6) +
    geom_text(aes(label=sprintf("%.1f", high_amp_percent)), vjust=-0.3, size=3) +
    labs(x=NULL, y="High-level amplification (%)", title=paste("B1.", g, "high-level copy-number amplification (GISTIC +2)")) +
    theme_bw(base_size=11) + ylim(0, max(sub$high_amp_percent)*1.3) + theme(panel.grid.minor=element_blank())
  assign(paste0("pB1_",g), p)
}
for (g in c("TP53","KRAS")) {
  sub <- mut %>% filter(gene == g)
  p <- ggplot(sub, aes(context, mutated_percent)) + geom_col(fill="#2E6E9E", width=0.6) +
    geom_text(aes(label=sprintf("%.0f", mutated_percent)), vjust=-0.3, size=3) +
    labs(x=NULL, y="Mutated samples (%)", title=paste("B2.", g, "mutation prevalence")) +
    theme_bw(base_size=11) + ylim(0, max(sub$mutated_percent)*1.25) + theme(panel.grid.minor=element_blank())
  assign(paste0("pB2_",g), p)
}
gB <- (pB1_EGFR | pB1_ERBB2) / (pB2_TP53 | pB2_KRAS)
ggsave(file.path(FIG,"fig_paper_molecular_context.png"), gB, width=11, height=7.5, dpi=300)
ggsave(file.path(FIG,"fig_paper_molecular_context.pdf"), gB, width=11, height=7.5)

# ---------- C. Raw vs composition-adjusted median SMD (all 10 contexts x modules) ----------
at <- rd("context_atlas_summary.csv")
adj <- rd("module_effects_composition_adjusted.csv")
adj_main <- adj %>% filter(role %in% c("discovery","validation")) %>%
  group_by(disease, feature) %>% summarise(median_smd_adj = median(smd, na.rm=TRUE), .groups="drop")
cmp <- merge(at[, c("disease","feature","median_smd","robust_consistent","composition_robust")],
             adj_main, by=c("disease","feature"), all.x=TRUE)
cmp$robust <- ifelse(cmp$robust_consistent=="TRUE", "robust", "other")
cmp$comp_rob <- ifelse(!is.na(cmp$composition_robust) & cmp$composition_robust=="TRUE", "comp-robust", "no")
cmp$class <- ifelse(cmp$comp_rob=="comp-robust","composition-robust",
             ifelse(cmp$robust=="robust","robust (composition-sensitive)","not robust"))
cmp <- cmp %>% filter(is.finite(median_smd) & is.finite(median_smd_adj))
set.seed(1)
gC <- ggplot(cmp, aes(median_smd, median_smd_adj, colour=class)) +
  geom_hline(yintercept=0, linetype=2, colour="grey60") + geom_vline(xintercept=0, linetype=2, colour="grey60") +
  geom_abline(slope=1, intercept=0, linetype=3, colour="grey40") +
  geom_point(size=1.6, alpha=0.85) +
  scale_color_manual(values=c("composition-robust"="#B02040","robust (composition-sensitive)"="#E8A33D","not robust"="grey55")) +
  labs(x="Raw median SMD (Case vs Control)", y="Composition-adjusted median SMD",
       colour=NULL, title="C. Composition residual adjustment across 170 context-module effects") +
  theme_bw(base_size=11) + theme(legend.position="top")
ggsave(file.path(FIG,"fig_paper_composition_adjustment.png"), gC, width=7, height=6, dpi=300)
ggsave(file.path(FIG,"fig_paper_composition_adjustment.pdf"), gC, width=7, height=6)
cat("figures written.\n")
cat("A rows:", nrow(plotA), "B high-amp samples:", nrow(cna %>% filter(gene %in% c("EGFR","ERBB2"))),
    "C rows:", nrow(cmp), "\n")
