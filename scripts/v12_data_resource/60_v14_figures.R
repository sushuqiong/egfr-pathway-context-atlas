#!/usr/bin/env Rscript
# v14 figures: fix label overlap flagged by review.
#  Fig1: B facets stacked vertically with readable context labels; C labels moved into the axis labels.
#  Fig3: A replaced by a per-context concordance summary (the 165-pair detail moves to Supplementary Table S10).
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2); library(patchwork)})
V14 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v14"
R <- file.path(V14,"results"); F <- file.path(V14,"02_figures"); W <- 6.7
th <- function(base=10) theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_line(colour="grey93", linewidth=.25),
        legend.position="none", strip.background=element_rect(fill="grey94", colour=NA),
        strip.text=element_text(face="bold", size=base-1), plot.title=element_text(face="bold", hjust=0, size=base-0.3),
        plot.margin=margin(5,14,5,5), axis.text=element_text(size=base-1), axis.title=element_text(size=base-1))

wrap_title <- function(x, width = 38) vapply(as.character(x), function(s) paste(strwrap(s, width = width), collapse = "\n"), character(1))
tlab <- function(x, width = 46) labs(title = wrap_title(x, width))
shortmod <- function(x) {
  y <- gsub("_AXIS$", "", x); y <- gsub("_NTRK$", "", y); y <- gsub("_CSF1R$", "", y)
  y <- gsub("RECEPTORS$", "REC", y); y <- gsub("LIGANDS$", "LIG", y)
  y <- gsub("PDGFR_KIT$", "PDGFR", y); y <- gsub("VEGF_PDGF$", "VEGF_PDGF", y)
  y
}
ctxmap <- c(GSE32863="LUAD",GSE19804="LUAD",GSE10072="LUAD",GSE44076="CRC",GSE41258="CRC",GSE23878="CRC",
            GSE75214="IBD",GSE87473="IBD",GSE179285="IBD",GSE4302="Asthma",GSE43696="Asthma",GSE67472="Asthma",
            GSE27342="STAD",GSE63089="STAD",GSE13911="STAD",GSE15471="PAAD",GSE28735="PAAD",GSE62452="PAAD",
            GSE57957="HCC",GSE62232="HCC",GSE23400="ESCC",GSE20347="ESCC",GSE76925="COPD",GSE47460="COPD",
            GSE33814="NAFLD",GSE66676="NAFLD",GSE16879="IBD")
ord <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma")
## ---------------- Figure 1 ----------------
cov <- read.csv(file.path(R,"v12_gene_coverage.csv"), stringsAsFactors=FALSE); cov$context <- ctxmap[cov$accession]
pA <- ggplot(cov, aes(factor(context, levels=ord), factor(shortmod(module), levels=rev(unique(shortmod(module[order(module)])))))) +
  geom_tile(aes(fill=coverage), colour="white", linewidth=.35) +
  scale_fill_gradient(low="#A6123C", high="#EAF2FB", limits=c(0.3,1)) +
  labs(x=NULL, y="module (short labels; see legend file)", title=wrap_title("A  Module gene coverage per disease context (dark red = low, pale = complete)")) + th() +
  theme(axis.text.x=element_text(size=8.5), axis.text.y=element_text(size=8.3))
reg <- read.csv(file.path(R,"v12_cohort_registry.csv"), stringsAsFactors=FALSE); reg$context <- ctxmap[reg$accession]
cc <- reg %>% filter(accession!="GSE16879")
long <- cc %>% group_by(context) %>%
  summarise(`assay records`=sum(as.integer(n_assay_records)),
            `patients with identifiers`=sum(as.integer(ifelse(is.na(suppressWarnings(as.integer(n_unique_patients))),0,as.integer(n_unique_patients)))),
            `patients with both tissues`=sum(as.integer(ifelse(paired_design_used=="yes", patients_with_both_arms, 0))), .groups="drop") %>%
  pivot_longer(-context, names_to="measure", values_to="n")
pB <- ggplot(long, aes(factor(context, levels=ord), n)) + geom_col(fill="#3C6E9F", width=.68) +
  facet_wrap(~measure, nrow=3, scales="free_y") +
  labs(x=NULL, y=NULL, title=wrap_title("B  Cohort composition by context")) + th() +
  theme(axis.text.x=element_text(size=8.5))
aud <- read.csv(file.path(R,"v12_sc_dataset_audit.csv"), stringsAsFactors=FALSE)
aud$lab <- ifelse(aud$arms=="excluded",
                  paste0(aud$context, ": excluded, tumour tissue only"),
                  paste0(aud$context, ": ", aud$arms, " (", aud$donors, " donors)"))
pC <- ggplot(aud, aes(reorder(lab, cells_used), cells_used)) + geom_col(fill="#7FA8C9", width=.66) + coord_flip() +
  scale_y_continuous(expand=expansion(mult=c(0,.12))) +
  labs(x=NULL, y="single cells used", title=wrap_title("C  Single-cell datasets and comparison arms")) + th() +
  theme(axis.text.y=element_text(size=8.3))
fig1 <- pA / pB / pC
ggsave(file.path(F,"Fig1_resource_overview.png"), fig1, width=W, height=9.3, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"Fig1_resource_overview.pdf"), fig1, width=W, height=9.3)
## ---------------- Figure 2 (unchanged panels, re-rendered) ----------------
scc <- read.csv(file.path(R,"v12_sc_comparisons.csv"), stringsAsFactors=FALSE)
exc <- data.frame(label=c("Adenocarcinoma samples excluded (squamous oesophageal layer)",
                          "In utero cells excluded (gastric dataset)",
                          "Tumour-only cells excluded (lung dataset, no control arm)",
                          "Malignant-labelled cells in non-tumour colorectal samples (flagged)",
                          "Single-cell comparisons not testable (donor overlap <5, not disjoint)"),
                  n=c(89,1277,117266,358,80))
p2a <- ggplot(exc, aes(factor(label, levels=rev(label)), n)) + geom_col(fill="#A6123C", width=.62) +
  geom_text(aes(label=format(n, big.mark=",")), hjust=-0.08, size=3.2, colour="#1A1A1A") + coord_flip() +
  scale_y_log10(expand=expansion(mult=c(0,.32))) +
  labs(x=NULL, y="records (log scale)", title=wrap_title("A  Exclusions, flags and non-testable comparisons")) + th() +
  theme(axis.text.y=element_text(size=8.3))
tt <- as.data.frame(table(scc$test_used)); names(tt) <- c("test","n")
p2b <- ggplot(tt, aes(n, reorder(test, n))) + geom_col(fill="#14457B", width=.62) +
  geom_text(aes(label=n), hjust=-0.15, size=3.2, colour="#1A1A1A") + scale_x_continuous(expand=expansion(mult=c(0,.2))) +
  labs(x="number of comparisons", y=NULL, title=wrap_title("B  Single-cell comparison design used")) + th() +
  theme(axis.text.y=element_text(size=8.3))
pc <- read.csv(file.path(R,"v12_percohort_effects.csv"), stringsAsFactors=FALSE)
p2c <- ggplot(pc[is.finite(pc$yi),], aes(yi)) + geom_histogram(bins=26, fill="#3C6E9F", colour="white", linewidth=.2) +
  facet_wrap(~measure, nrow=2, scales="free_y") + geom_vline(xintercept=0, linetype="dashed", colour="grey35") +
  labs(x="per-cohort standardized effect (SD units)", y="cohort-module pairs",
       title=wrap_title("C  Estimates layer (all effects, including non-significant)")) + th()
ggsave(file.path(F,"Fig2_technical_validation.png"), p2a / p2b / p2c, width=W, height=8.2, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"Fig2_technical_validation.pdf"), p2a / p2b / p2c, width=W, height=8.2)
## ---------------- Figure 3 (panel A summarised; detail -> Supplementary Table S10) ----------------
con <- read.csv(file.path(R,"v13_qc_cross_cohort_consistency.csv"), stringsAsFactors=FALSE) %>% filter(k>=2) %>%
  mutate(concordance=suppressWarnings(as.numeric(as.character(concordance))), k=as.integer(k)) %>%
  filter(is.finite(concordance), disease!="")
p3a <- ggplot(con, aes(factor(disease, levels=ord), concordance)) +
  geom_jitter(width=.16, height=.02, size=1.1, colour="#3C6E9F", alpha=.75) +
  stat_summary(fun=median, geom="crossbar", width=.45, colour="#A6123C", linewidth=.45) +
  labs(x=NULL, y="fraction same direction", tag="165 pairs",
       title=wrap_title("A  Cross-cohort direction consistency (points: pairs, bar: median)")) + th(9.5) +
  theme(axis.text.x=element_text(size=8.5))
sen <- read.csv(file.path(R,"v13_qc_coverage_threshold_sensitivity.csv"), stringsAsFactors=FALSE)
sen$scenario <- factor(sen$scenario, levels=c("all cohorts","coverage >= 0.60","coverage >= 0.80","coverage >= 0.90"))
summ <- sen %>% group_by(scenario) %>% summarise(pairs=n(), sig=sum(fdr<0.05, na.rm=TRUE), .groups="drop") %>%
  pivot_longer(c(pairs, sig), names_to="measure", values_to="n")
p3b <- ggplot(summ, aes(scenario, n, fill=measure)) + geom_col(position=position_dodge(width=.76), width=.66) +
  geom_text(aes(label=n), position=position_dodge(width=.76), vjust=-0.45, size=3.1) +
  scale_fill_manual(values=c(pairs="#9FBFD8", sig="#A6123C")) + scale_y_continuous(expand=expansion(mult=c(0,.18))) +
  labs(x="cohorts below the coverage threshold excluded", y="count",
       title=wrap_title("B  Coverage-threshold sensitivity (light: pairs, red: significant)")) + th(9.5) +
  theme(axis.text.x=element_text(size=8.2))
so <- read.csv(file.path(R,"v13_qc_signature_overlap.csv"), stringsAsFactors=FALSE)
p3c <- ggplot(so, aes(reorder(shortmod(module), as.numeric(frac_overlap_xcell)), as.numeric(frac_overlap_xcell))) +
  geom_col(width=.6, fill="#7FA8C9") + coord_flip() + geom_hline(yintercept=0.2, linetype="dashed", colour="#A6123C") +
  labs(x=NULL, y="fraction of members in xCell panel",
       title=wrap_title("C  Module vs xCell overlap (20% dashed)")) + th(9.5) +
  theme(axis.text.y=element_text(size=8.3))
vif <- read.csv(file.path(R,"v13_qc_vif_by_predictor.csv"), stringsAsFactors=FALSE)
vif$r2 <- as.numeric(vif$r2_overall); vif$v <- as.numeric(vif$max_vif_predictor)
p3d <- ggplot(vif, aes(r2, v)) + geom_point(size=1.8, colour="#14457B") + geom_hline(yintercept=5, linetype="dashed", colour="#A6123C") +
  labs(x="overall R2 (disease ~ composition)", y="max VIF",
       title=wrap_title("D  Model R2 versus VIF")) + th(9.5)
fig3 <- (p3a / p3b) | (p3c / p3d)
ggsave(file.path(F,"Fig3_comparability_checks.png"), fig3, width=W, height=8.6, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"Fig3_comparability_checks.pdf"), fig3, width=W, height=8.6)
## ---------------- Figure 4 ----------------
cg <- read.csv(file.path(R,"v12_common_gene_sensitivity_summary.csv"), stringsAsFactors=FALSE)
flagcol <- names(cg)[grep("flag", names(cg), ignore.case=TRUE)][1]; spcol <- names(cg)[grep("spearman", names(cg), ignore.case=TRUE)][1]
cg$spearman <- suppressWarnings(as.numeric(cg[[spcol]])); cg$flag <- as.character(cg[[flagcol]])
cg$status <- ifelse(grepl("insufficient", cg$flag, ignore.case=TRUE), "grey",
             ifelse(grepl("disagreement", cg$flag, ignore.case=TRUE), "red", "blue"))
cg$v <- ifelse(is.na(cg$spearman), 0, cg$spearman); cg$lab <- ifelse(is.na(cg$spearman), "n.a.", sprintf("%.2f", cg$spearman))
p4a <- ggplot(cg, aes(reorder(shortmod(module), v), v, fill=status)) + geom_col(width=.62) + coord_flip() +
  scale_fill_manual(values=c(blue="#14457B", red="#A6123C", grey="#9A9A9A")) +
  geom_text(aes(label=lab), hjust=-0.12, size=3.2, colour="#1A1A1A") + scale_y_continuous(limits=c(0,1.15)) +
  labs(x=NULL, y="Spearman rho (full vs common-gene scoring)",
       title=wrap_title("A  Common-gene sensitivity (red: disagreement in >=20% of cohorts; grey: not scorable)")) + th(9.5) +
  theme(axis.text.y=element_text(size=8.3))
col <- read.csv(file.path(R,"v13_qc_vif_by_predictor.csv"), stringsAsFactors=FALSE)
p4b <- ggplot(col, aes(as.numeric(r2_overall))) + geom_histogram(bins=12, fill="#7FA8C9", colour="white") +
  geom_vline(xintercept=median(as.numeric(col$r2_overall)), linetype="dashed", colour="#A6123C") +
  labs(x="R2 (disease ~ composition)", y="cohorts", title=wrap_title("B  Disease status versus composition")) + th(9.5)
ggsave(file.path(F,"Fig4_sensitivity_checks.png"), p4a / p4b, width=W, height=7.4, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"Fig4_sensitivity_checks.pdf"), p4a / p4b, width=W, height=7.4)
cat("v14 figures written\n")
