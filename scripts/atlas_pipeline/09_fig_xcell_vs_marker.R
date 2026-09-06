#!/usr/bin/env Rscript
# Supplementary: xCell-deconvoluted vs marker-proxy composition adjustment (median SMD per disease-module)
suppressPackageStartupMessages({library(dplyr); library(ggplot2)})
ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
RES <- file.path(ROOT, "results"); FIG <- file.path(ROOT, "figures")
rd <- function(f, ...) read.csv(file.path(RES, f), stringsAsFactors=FALSE, check.names=FALSE, ...)
mk <- rd("module_effects_composition_adjusted.csv") %>% filter(role %in% c("discovery","validation")) %>%
  group_by(disease, feature) %>% summarise(marker_med = median(smd, na.rm=TRUE), .groups="drop")
xc <- rd("xcell/module_effects_composition_adjusted_xcell.csv") %>% filter(role %in% c("discovery","validation")) %>%
  group_by(disease, feature) %>% summarise(xcell_med = median(smd, na.rm=TRUE), .groups="drop")
xs <- rd("xcell/context_atlas_summary_xcell_adjusted.csv") %>% select(disease, feature, robust_xcell)
d <- merge(mk, xc, by=c("disease","feature")) %>% merge(xs, by=c("disease","feature")) %>%
  filter(is.finite(marker_med) & is.finite(xcell_med))
d$class <- ifelse(d$robust_xcell=="TRUE", "xCell-robust", "not robust")
g <- ggplot(d, aes(marker_med, xcell_med, colour=class)) +
  geom_hline(yintercept=0, linetype=2, colour="grey60") + geom_vline(xintercept=0, linetype=2, colour="grey60") +
  geom_abline(slope=1, intercept=0, linetype=3, colour="grey40") +
  geom_point(size=1.5, alpha=0.8) +
  scale_color_manual(values=c("xCell-robust"="#B02040","not robust"="grey55")) +
  labs(x="Marker-proxy adjusted median SMD", y="xCell-adjusted median SMD",
       colour=NULL, title="Composition adjustment: xCell deconvolution vs marker proxy (170 context-module effects)") +
  theme_bw(base_size=11) + theme(legend.position="top")
ggsave(file.path(FIG,"fig_paper_xcell_vs_marker.png"), g, width=7, height=6, dpi=300)
ggsave(file.path(FIG,"fig_paper_xcell_vs_marker.pdf"), g, width=7, height=6)
cat("n points:", nrow(d), " cor:", round(cor(d$marker_med, d$xcell_med, method="spearman"), 3), "\n")
