#!/usr/bin/env Rscript
# v13 Figure 3: comparability and coupling checks (no overall title, no top/bottom legends).
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2); library(patchwork)})
V13 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v13"
R <- file.path(V13,"results"); F <- file.path(V13,"02_figures"); W <- 6.7
th <- function(base=10) theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_line(colour="grey93", linewidth=.25),
        legend.position="none", strip.background=element_rect(fill="grey94", colour=NA),
        strip.text=element_text(face="bold", size=base-1), plot.title=element_text(face="bold", hjust=0, size=base),
        plot.margin=margin(5,12,5,5), axis.text=element_text(size=base-1), axis.title=element_text(size=base-1))
## A: direction consistency per context
con <- read.csv(file.path(R,"v13_qc_cross_cohort_consistency.csv"), stringsAsFactors=FALSE) %>% filter(k>=2)
A <- con %>% mutate(concordance=suppressWarnings(as.numeric(as.character(concordance)))) %>%
  filter(is.finite(concordance), !is.na(disease), disease!="") %>%
  arrange(disease, desc(concordance)) %>% mutate(label=paste0(disease,": ",feature))
pA <- ggplot(A, aes(reorder(label, concordance), concordance)) + geom_col(width=.6, fill="#3C6E9F") + coord_flip() +
  geom_vline(xintercept=1, linetype="dashed", colour="grey45") + facet_wrap(~disease, scales="free_y", ncol=3) +
  labs(x="fraction of cohorts with the majority effect direction", y=NULL,
       title="A  Cross-cohort direction consistency") + th(9.5) +
  theme(axis.text.y=element_text(size=5.6), strip.text=element_text(size=8))
## B: coverage-threshold sensitivity
sen <- read.csv(file.path(R,"v13_qc_coverage_threshold_sensitivity.csv"), stringsAsFactors=FALSE)
sen$scenario <- factor(sen$scenario, levels=c("all cohorts","coverage >= 0.60","coverage >= 0.80","coverage >= 0.90"))
summ <- sen %>% group_by(scenario) %>% summarise(pairs=n(), sig=sum(fdr<0.05, na.rm=TRUE), .groups="drop") %>%
  pivot_longer(c(pairs, sig), names_to="measure", values_to="n")
pB <- ggplot(summ, aes(scenario, n, fill=measure)) + geom_col(position=position_dodge(width=.75), width=.68) +
  geom_text(aes(label=n), position=position_dodge(width=.75), vjust=-0.4, size=3) +
  scale_fill_manual(values=c(pairs="#9FBFD8", sig="#A6123C")) +
  scale_y_continuous(expand=expansion(mult=c(0,.16))) +
  labs(x="cohort-module pairs retained", y="count",
       title="B  Coverage-threshold sensitivity (light: pairs; red: BH-significant)") + th(9.5) +
  theme(axis.text.x=element_text(angle=18, hjust=1, size=8))
## C: signature overlap and VIF
so <- read.csv(file.path(R,"v13_qc_signature_overlap.csv"), stringsAsFactors=FALSE)
C1 <- ggplot(so, aes(reorder(module, as.numeric(frac_overlap_xcell)), as.numeric(frac_overlap_xcell))) +
  geom_col(width=.6, fill="#7FA8C9") + coord_flip() + geom_hline(yintercept=0.2, linetype="dashed", colour="#A6123C") +
  labs(x="fraction of module members inside the xCell signature panel", y=NULL,
       title="C  Module vs xCell panel overlap (dashed: 20%)") + th(9.5) +
  theme(axis.text.y=element_text(size=6.5))
vif <- read.csv(file.path(R,"v13_qc_vif_by_predictor.csv"), stringsAsFactors=FALSE)
vif$r2 <- as.numeric(vif$r2_overall); vif$v <- as.numeric(vif$max_vif_predictor)
pC2 <- ggplot(vif, aes(r2, v)) + geom_point(size=1.8, colour="#14457B") +
  geom_hline(yintercept=5, linetype="dashed", colour="#A6123C") +
  labs(x="overall R2 (disease status ~ 4 compartment scores)", y="max per-predictor VIF",
       title="D  Model R2 vs per-predictor VIF") + th(9.5)
fig3 <- (pA / pB) | (C1 / pC2)
fig3 <- pA / pB / (C1 | pC2)
ggsave(file.path(F,"Fig3_comparability_checks.png"), fig3, width=W, height=8.9, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"Fig3_comparability_checks.pdf"), fig3, width=W, height=8.9)
cat("Fig3 written (4 panels)\n")
cat("consistency pairs:",nrow(A),"| coverage scenarios:",nrow(summ),"| overlap modules:",nrow(so),"| VIF cohorts:",nrow(vif),"\n")
