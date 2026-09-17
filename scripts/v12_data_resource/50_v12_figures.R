#!/usr/bin/env Rscript
# v12 Data Descriptor figures (2 main figures; width <= 6.7 in = 17 cm at 300 dpi)
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2); library(patchwork)})
R  <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
V11<- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/reruns/results"
F  <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/02_figures"; dir.create(F, recursive=TRUE, showWarnings=FALSE)
W <- 6.7
th <- function(base=10.5) theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_line(colour="grey93", linewidth=.25),
        legend.position="bottom", legend.title=element_text(size=base-2), legend.text=element_text(size=base-2),
        strip.background=element_rect(fill="grey92", colour=NA), strip.text=element_text(face="bold", size=base-1),
        plot.title=element_text(face="bold", hjust=0, size=base), plot.margin=margin(6,10,6,6),
        axis.text=element_text(size=base-1), axis.title=element_text(size=base-1))
cov <- read.csv(file.path(R,"v12_gene_coverage.csv"), stringsAsFactors=FALSE)
reg <- read.csv(file.path(R,"v12_cohort_registry.csv"), stringsAsFactors=FALSE)
aud <- read.csv(file.path(R,"v12_sc_dataset_audit.csv"), stringsAsFactors=FALSE)
ctxmap <- c("GSE32863"="LUAD","GSE19804"="LUAD","GSE10072"="LUAD","GSE44076"="CRC","GSE41258"="CRC","GSE23878"="CRC",
            "GSE75214"="IBD","GSE87473"="IBD","GSE179285"="IBD","GSE4302"="Asthma","GSE43696"="Asthma","GSE67472"="Asthma",
            "GSE27342"="STAD","GSE63089"="STAD","GSE13911"="STAD","GSE15471"="PAAD","GSE28735"="PAAD","GSE62452"="PAAD",
            "GSE57957"="HCC","GSE62232"="HCC","GSE23400"="ESCC","GSE20347"="ESCC","GSE76925"="COPD","GSE47460"="COPD",
            "GSE33814"="NAFLD","GSE66676"="NAFLD","GSE16879"="IBD")
cov$context <- ctxmap[cov$accession]
ord <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma")
pA <- ggplot(cov, aes(factor(context, levels=ord), module)) +
  geom_tile(aes(fill=coverage), colour="white", linewidth=.35) +
  scale_fill_gradient(low="#A6123C", high="#EAF2FB", limits=c(0.3,1), name="gene coverage\n(fraction of module members)") +
  labs(x=NULL, y=NULL, title="A  Module gene coverage by disease context") + th(10) +
  theme(axis.text.x=element_text(angle=0, size=9), axis.text.y=element_text(size=8))

reg2 <- reg %>% mutate(context=ctxmap[accession]) %>%
  group_by(context) %>% summarise(assays=sum(n_assay_records), patients=sum(n_unique_patients),
                                  paired=sum(paired, na.rm=TRUE), .groups="drop") %>%
  pivot_longer(-context, names_to="measure", values_to="n")
pB <- ggplot(reg2, aes(factor(context, levels=ord), n, fill=measure)) +
  geom_col(position=position_dodge(width=.8), width=.7) +
  scale_fill_manual(values=c(assays="#14457B", patients="#A6123C", paired="#7FA8C9"), name=NULL) +
  labs(x=NULL, y="count", title="B  Assay records, unique patients and paired patients") + th(10) +
  theme(axis.text.x=element_text(angle=0, size=9))

aud$arms[aud$arms=="excluded"] <- "excluded (tumour-only, no control arm)"
pC <- ggplot(aud, aes(factor(context, levels=rev(aud$context)), cells_used, fill=arms)) +
  geom_col(width=.7) + geom_text(aes(label=sprintf("%s donors", donors)), hjust=-0.05, size=3.1, colour="grey25") +
  coord_flip() + scale_fill_manual(values=c("#14457B","#A6123C","#7FA8C9","grey70"), name="arms") +
  scale_y_continuous(expand=expansion(mult=c(0,.28))) +
  labs(x=NULL, y="single cells used", title="C  Single-cell datasets (arms available per dataset)") + th(10)
fig1 <- pA / pB / pC + plot_annotation(title="Resource overview: coverage, cohort composition and single-cell layers",
                                       theme=theme(plot.title=element_text(face="bold", size=11)))
ggsave(file.path(F,"Fig1_resource_overview.png"), fig1, width=W, height=10.5, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"Fig1_resource_overview.pdf"), fig1, width=W, height=10.5)

# Figure 2: validation — exclusions, test types, effect-size distribution
exc <- data.frame(label=c("Adenocarcinoma samples excluded\nfrom squamous oesophageal layer",
                          "In utero cells excluded\n(gastric dataset)",
                          "Tumour-only cells excluded\n(lung dataset, no control arm)",
                          "Malignant-labelled cells in\nnon-tumour colorectal samples (flagged)",
                          "Single-cell comparisons\nnot testable (donor overlap <5, not disjoint)"),
                  n=c(89,1277,117266,358,80), kind=c("excluded","excluded","excluded","flagged","not testable"))
p2a <- ggplot(exc, aes(factor(label, levels=rev(label)), n, fill=kind)) + geom_col(width=.65) +
  geom_text(aes(label=format(n, big.mark=",")), hjust=-0.07, size=3.1, colour="grey25") +
  coord_flip() + scale_fill_manual(values=c("excluded"="#A6123C","flagged"="#D98C4A","not testable"="#7FA8C9"), guide="none") +
  scale_y_log10(expand=expansion(mult=c(0,.3))) + labs(x=NULL, y="records (log scale)", title="A  Exclusions, flags and non-testable comparisons") + th(10) +
  theme(axis.text.y=element_text(size=8))
scc <- read.csv(file.path(R,"v12_sc_comparisons.csv"), stringsAsFactors=FALSE)
tt <- as.data.frame(table(scc$test_used)); names(tt) <- c("test","n")
p2b <- ggplot(tt, aes(n, reorder(test, n), fill=test)) + geom_col(width=.65, show.legend=FALSE) +
  geom_text(aes(label=n), hjust=-0.15, size=3.1, colour="grey25") +
  scale_fill_manual(values=rep(c("#14457B","#A6123C","#7FA8C9","grey70"), 2)) +
  scale_x_continuous(expand=expansion(mult=c(0,.2))) +
  labs(x="number of comparisons", y=NULL, title="B  Single-cell comparison design actually used") + th(10) +
  theme(axis.text.y=element_text(size=8))
pc <- read.csv(file.path(V11,"v11_percohort_effects.csv"), stringsAsFactors=FALSE)
p2c <- ggplot(pc[is.finite(pc$yi),], aes(yi, fill=measure)) + geom_histogram(bins=32, position="identity", alpha=.75) +
  geom_vline(xintercept=0, linetype="dashed", colour="grey40") +
  scale_fill_manual(values=c("#14457B","#A6123C"), name="effect measure") +
  labs(x="per-cohort standardized effect (SD units)", y="cohort-module pairs",
       title="C  Estimates layer: all per-cohort effects, including non-significant results") + th(10)
fig2 <- p2a / p2b / p2c + plot_annotation(title="Technical validation: sample verification, comparison design and estimates layer",
                                          theme=theme(plot.title=element_text(face="bold", size=11)))
ggsave(file.path(F,"Fig2_technical_validation.png"), fig2, width=W, height=10.5, dpi=300, limitsize=FALSE)
ggsave(file.path(F,"Fig2_technical_validation.pdf"), fig2, width=W, height=10.5)
cat("v12 figures written\n")
