#!/usr/bin/env Rscript
# v12 figures, submission format:
#   * no overall title, no legend blocks above or below the figure (legends live in a separate Word file)
#   * legends replaced by direct labelling, faceting or in-panel annotations
#   * all figures <= 6.7 in (17 cm) wide at 300 dpi
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2); library(patchwork)})
R  <- "C:/Users/fengq/Desktop/EGFR/EGFR的v13/results"
F  <- "C:/Users/fengq/Desktop/EGFR/EGFR的v13/02_figures"
W  <- 6.7
th <- function(base=10) theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_line(colour="grey93", linewidth=.25),
        legend.position="none", strip.background=element_rect(fill="grey94", colour=NA),
        strip.text=element_text(face="bold", size=base-1), plot.title=element_text(face="bold", hjust=0, size=base),
        plot.margin=margin(5,12,5,5), axis.text=element_text(size=base-1), axis.title=element_text(size=base-1))
ctxmap <- c(GSE32863="LUAD",GSE19804="LUAD",GSE10072="LUAD",GSE44076="CRC",GSE41258="CRC",GSE23878="CRC",
            GSE75214="IBD",GSE87473="IBD",GSE179285="IBD",GSE4302="Asthma",GSE43696="Asthma",GSE67472="Asthma",
            GSE27342="STAD",GSE63089="STAD",GSE13911="STAD",GSE15471="PAAD",GSE28735="PAAD",GSE62452="PAAD",
            GSE57957="HCC",GSE62232="HCC",GSE23400="ESCC",GSE20347="ESCC",GSE76925="COPD",GSE47460="COPD",
            GSE33814="NAFLD",GSE66676="NAFLD",GSE16879="IBD")
ord <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma")
## ---------- Figure 1 ----------
cov <- read.csv(file.path(R,"v12_gene_coverage.csv"), stringsAsFactors=FALSE); cov$context <- ctxmap[cov$accession]
pA <- ggplot(cov, aes(factor(context, levels=ord), module)) +
  geom_tile(aes(fill=coverage), colour="white", linewidth=.35) +
  scale_fill_gradient(low="#A6123C", high="#EAF2FB", limits=c(0.3,1)) +
  labs(x=NULL, y=NULL, title="A  Module gene coverage per disease context (red = 0.33, pale = 1.00)") + th() +
  theme(axis.text.x=element_text(size=9), axis.text.y=element_text(size=7.5))
reg <- read.csv(file.path(R,"v12_cohort_registry.csv"), stringsAsFactors=FALSE); reg$context <- ctxmap[reg$accession]
cc <- reg %>% filter(accession!="GSE16879")
long <- cc %>% group_by(context) %>%
  summarise(`assay records`=sum(as.integer(n_assay_records)), `unique patients`=sum(as.integer(ifelse(is.na(suppressWarnings(as.integer(n_unique_patients))),0,as.integer(n_unique_patients)))),
            `paired patients`=sum(as.integer(ifelse(paired_design_used=="yes", patients_with_both_arms, 0))), .groups="drop") %>%
  pivot_longer(-context, names_to="measure", values_to="n")
pB <- ggplot(long, aes(factor(context, levels=ord), n)) + geom_col(fill="#3C6E9F", width=.7) +
  facet_wrap(~measure, nrow=1, scales="free_y") +
  labs(x=NULL, y=NULL, title="B  Cohort composition by context") + th() + theme(axis.text.x=element_text(size=8))
aud <- read.csv(file.path(R,"v12_sc_dataset_audit.csv"), stringsAsFactors=FALSE)
aud$arm_lab <- ifelse(aud$arms=="excluded", "excluded: no control arm", paste0(aud$arms, "|", aud$donors, " donors"))
pC <- ggplot(aud, aes(factor(context, levels=rev(c("CRC","IBD","STAD","ASTHMA","LUAD"))), cells_used)) +
  geom_col(fill="#7FA8C9", width=.7) + geom_text(aes(label=arm_lab), hjust=-0.05, size=2.8, colour="grey25") +
  coord_flip() + scale_y_continuous(expand=expansion(mult=c(0,.45))) +
  labs(x=NULL, y="single cells used", title="C  Single-cell datasets (arms in each)") + th()
fig1 <- pA / pB / pC
ggsave(file.path(F,"Fig1_resource_overview.png"), fig1, width=W, height=8.9, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"Fig1_resource_overview.pdf"), fig1, width=W, height=8.9)
## ---------- Figure 2 ----------
scc <- read.csv(file.path(R,"v12_sc_comparisons.csv"), stringsAsFactors=FALSE)
exc <- data.frame(label=c("Adenocarcinoma samples excluded (squamous oesophageal layer)",
                          "In utero cells excluded (gastric dataset)",
                          "Tumour-only cells excluded (lung dataset, no control arm)",
                          "Malignant-labelled cells in non-tumour colorectal samples (flagged)",
                          "Single-cell comparisons not testable (donor overlap <5, not disjoint)"),
                  n=c(89,1277,117266,358,80),
                  kind=c("excluded","excluded","excluded","flagged","not testable"))
pA <- ggplot(exc, aes(factor(label, levels=rev(label)), n)) + geom_col(fill="#A6123C", width=.62) +
  geom_text(aes(label=format(n, big.mark=",")), hjust=-0.08, size=2.9, colour="grey25") + coord_flip() +
  scale_y_log10(expand=expansion(mult=c(0,.35))) +
  labs(x=NULL, y="records (log scale)", title="A  Exclusions, flags, not testable") + th() +
  theme(axis.text.y=element_text(size=7.5))
tt <- as.data.frame(table(scc$test_used)); names(tt) <- c("test","n")
pB <- ggplot(tt, aes(n, reorder(test, n))) + geom_col(fill="#14457B", width=.62) +
  geom_text(aes(label=n), hjust=-0.15, size=2.9, colour="grey25") + scale_x_continuous(expand=expansion(mult=c(0,.2))) +
  labs(x="number of comparisons", y=NULL, title="B  Single-cell comparison design") + th() +
  theme(axis.text.y=element_text(size=7.5))
pc <- read.csv(file.path(R,"v12_percohort_effects.csv"), stringsAsFactors=FALSE)
pC <- ggplot(pc[is.finite(pc$yi),], aes(yi)) + geom_histogram(bins=28, fill="#3C6E9F", colour="white", linewidth=.2) +
  facet_wrap(~measure, nrow=2, scales="free_y") + geom_vline(xintercept=0, linetype="dashed", colour="grey35") +
  labs(x="per-cohort standardized effect (SD units)", y="cohort-module pairs",
       title="C  Estimates layer (all effects)") + th()
cg <- read.csv(file.path(R,"v12_common_gene_sensitivity_summary.csv"), stringsAsFactors=FALSE)
flagcol <- names(cg)[grep("flag", names(cg), ignore.case=TRUE)][1]; spcol <- names(cg)[grep("spearman", names(cg), ignore.case=TRUE)][1]
cg$spearman <- suppressWarnings(as.numeric(cg[[spcol]])); cg$flag <- as.character(cg[[flagcol]])
cg$status <- ifelse(grepl("insufficient", cg$flag, ignore.case=TRUE), "grey",
             ifelse(grepl("disagreement", cg$flag, ignore.case=TRUE), "red", "blue"))
cg$v <- ifelse(is.na(cg$spearman), 0, cg$spearman); cg$lab <- ifelse(is.na(cg$spearman), "n.a.", sprintf("%.2f", cg$spearman))
pD <- ggplot(cg, aes(v, reorder(module, v), fill=status)) + geom_col(width=.62) +
  scale_fill_manual(values=c(blue="#14457B", red="#A6123C", grey="grey65")) +
  geom_text(aes(label=lab), hjust=-0.12, size=2.7, colour="grey25") +
  geom_vline(xintercept=median(cg$spearman, na.rm=TRUE), linetype="dashed", colour="grey45") +
  scale_x_continuous(limits=c(0,1.15)) +
  labs(x="Spearman rho (full vs common-gene scoring)", y=NULL,
       title="D  Common-gene sensitivity") + th(9.5) +
  theme(axis.text.y=element_text(size=7.5))
col <- read.csv(file.path(R,"v12_qc_composition_collinearity.csv"), stringsAsFactors=FALSE)
pE <- ggplot(col, aes(r2_disease_on_composition)) + geom_histogram(bins=12, fill="#7FA8C9", colour="white") +
  geom_vline(xintercept=median(col$r2_disease_on_composition), linetype="dashed", colour="#A6123C") +
  labs(x="R2 (disease ~ composition)", y="cohorts",
       title="E  Disease status vs composition") + th(9.5)
fig2 <- pA / pB / pC / pD / pE
ggsave(file.path(F,"Fig2_technical_validation.png"), fig2, width=W, height=8.8, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"Fig2_technical_validation.pdf"), fig2, width=W, height=8.8)
cat("clean figures written (no overall titles, no top/bottom legends)\n")
