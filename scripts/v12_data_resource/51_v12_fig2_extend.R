#!/usr/bin/env Rscript
# v12: extend Figure 2 with (D) common-gene sensitivity per module and (E) composition collinearity per cohort.
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2); library(patchwork)})
R <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
F <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/02_figures"
W <- 6.7
th <- function(base=10.5) theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_line(colour="grey93", linewidth=.25),
        legend.position="bottom", legend.title=element_text(size=base-2), legend.text=element_text(size=base-2),
        plot.title=element_text(face="bold", hjust=0, size=base), plot.margin=margin(6,16,6,6),
        axis.text=element_text(size=base-1), axis.title=element_text(size=base-1))
cg <- read.csv(file.path(R,"v12_common_gene_sensitivity_summary.csv"), stringsAsFactors=FALSE)
flagcol <- names(cg)[grep("flag", names(cg), ignore.case=TRUE)][1]
spcol   <- names(cg)[grep("spearman", names(cg), ignore.case=TRUE)][1]
cg$spearman <- suppressWarnings(as.numeric(cg[[spcol]]))
cg$flag <- as.character(cg[[flagcol]])
cg$status <- ifelse(grepl("insufficient", cg$flag, ignore.case=TRUE), "too few shared genes",
             ifelse(grepl("disagreement", cg$flag, ignore.case=TRUE), "direction disagreement >=20% cohorts", "consistent"))
cg$spearman_plot <- ifelse(is.na(cg$spearman), 0, cg$spearman)
cg$lab_txt <- ifelse(is.na(cg$spearman), "n.a.", sprintf("%.2f", cg$spearman))
pD <- ggplot(cg, aes(spearman_plot, reorder(module, spearman_plot), fill=status)) + geom_col(width=.65) +
  geom_text(aes(label=lab_txt), hjust=-0.12, size=2.9, colour="grey25") +
  geom_vline(xintercept=median(cg$spearman, na.rm=TRUE), linetype="dashed", colour="grey45") +
  scale_fill_manual(values=c("consistent"="#14457B","direction disagreement"="#A6123C",
                             "too few shared genes"="grey65"), guide="none") +
  scale_x_continuous(limits=c(0,1.15), expand=expansion(mult=c(0,.02))) +
  labs(x="Spearman rho: full vs common-gene scoring", y=NULL,
       title="D  Common-gene sensitivity (red = direction disagreement; grey = not scorable)") + th(9.5) +
  theme(axis.text.y=element_text(size=8), plot.margin=margin(6,12,6,6))
col <- read.csv(file.path(R,"v12_qc_composition_collinearity.csv"), stringsAsFactors=FALSE)
pE <- ggplot(col, aes(r2_disease_on_composition)) + geom_histogram(bins=12, fill="#7FA8C9", colour="white") +
  geom_vline(xintercept=median(col$r2_disease_on_composition), linetype="dashed", colour="#A6123C") +
  labs(x="R2 (disease ~ composition)", y="cohorts",
       title="E  Collinearity: disease status vs composition") + th(10)
# rebuild Fig2 with panels A-C plus D and E
scc <- read.csv(file.path(R,"v12_sc_comparisons.csv"), stringsAsFactors=FALSE)
exc <- data.frame(label=c("Adenocarcinoma samples excluded\nfrom squamous oesophageal layer",
                          "In utero cells excluded\n(gastric dataset)",
                          "Tumour-only cells excluded\n(lung dataset, no control arm)",
                          "Malignant-labelled cells in\nnon-tumour colorectal samples (flagged)",
                          "Single-cell comparisons\nnot testable (donor overlap <5, not disjoint)"),
                  n=c(89,1277,117266,358,80),
                  kind=c("excluded","excluded","excluded","flagged","not testable"))
pA <- ggplot(exc, aes(factor(label, levels=rev(label)), n, fill=kind)) + geom_col(width=.65) +
  geom_text(aes(label=format(n, big.mark=",")), hjust=-0.07, size=3.1, colour="grey25") + coord_flip() +
  scale_fill_manual(values=c("excluded"="#A6123C","flagged"="#D98C4A","not testable"="#7FA8C9"), guide="none") +
  scale_y_log10(expand=expansion(mult=c(0,.3))) + labs(x=NULL, y="records (log scale)",
  title="A  Exclusions, flags and non-testable comparisons") + th(10) + theme(axis.text.y=element_text(size=8))
tt <- as.data.frame(table(scc$test_used)); names(tt) <- c("test","n")
pB <- ggplot(tt, aes(n, reorder(test, n), fill=test)) + geom_col(width=.65, show.legend=FALSE) +
  geom_text(aes(label=n), hjust=-0.15, size=3.1, colour="grey25") +
  scale_fill_manual(values=rep(c("#14457B","#A6123C","#7FA8C9","grey70"), 2)) +
  scale_x_continuous(expand=expansion(mult=c(0,.2))) +
  labs(x="number of comparisons", y=NULL, title="B  Single-cell comparison design actually used") + th(10) +
  theme(axis.text.y=element_text(size=8))
pc <- read.csv(file.path(R,"v12_percohort_effects.csv"), stringsAsFactors=FALSE)
pC <- ggplot(pc[is.finite(pc$yi),], aes(yi, fill=measure)) + geom_histogram(bins=32, position="identity", alpha=.75) +
  geom_vline(xintercept=0, linetype="dashed", colour="grey40") +
  scale_fill_manual(values=c("#14457B","#A6123C"), name="effect measure") +
  labs(x="per-cohort standardized effect (SD units)", y="cohort-module pairs",
       title="C  Estimates layer: all per-cohort effects (incl. non-significant)") + th(10)
fig2 <- pA / pB / pC / pD / pE +
  plot_annotation(title="Technical validation of the resource",
                  theme=theme(plot.title=element_text(face="bold", size=11)))
h <- 2.35*5
ggsave(file.path(F,"Fig2_technical_validation.png"), fig2, width=W, height=h, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"Fig2_technical_validation.pdf"), fig2, width=W, height=h)
cat("Fig2 rebuilt with 5 panels (height", h, "in )\n")
cat("common-gene statuses:", paste(names(table(cg$status)), table(cg$status), collapse=" | "), "\n")
cat("median collinearity R2:", round(median(col$r2_disease_on_composition, na.rm=TRUE),3), "\n")
