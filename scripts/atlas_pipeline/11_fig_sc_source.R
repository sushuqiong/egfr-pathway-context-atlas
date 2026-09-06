#!/usr/bin/env Rscript
# Single-cell source figure (closes dangling Fig): case-control patient-level module differences by cell type.
suppressPackageStartupMessages({library(dplyr); library(ggplot2)})
ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
RES <- file.path(ROOT, "results"); FIG <- file.path(ROOT, "figures")
d <- read.csv(file.path(RES, "sc_top_hit_cell_source_validation.csv"), stringsAsFactors=FALSE, check.names=FALSE, fileEncoding="UTF-8-BOM")
d <- d %>% filter(context %in% c("CRC","IBD","STAD"), n_case_patients >= 3, n_control_patients >= 3)
d$diff <- suppressWarnings(as.numeric(d$case_patient_mean)) - suppressWarnings(as.numeric(d$control_patient_mean))
d$fdr <- suppressWarnings(as.numeric(d$fdr))
keep <- d %>% group_by(context, module) %>% summarise(maxabs = max(abs(diff), na.rm=TRUE), .groups="drop") %>% filter(maxabs > 0.01)
d <- inner_join(d, keep[, c("context","module")], by=c("context","module"))
d$ct <- gsub("_", " ", d$cell_type)
d$sig <- ifelse(!is.na(d$fdr) & d$fdr < 0.05, "FDR<0.05", "")
d <- d %>% mutate(context = factor(context, levels=c("CRC","IBD","STAD")))
g <- ggplot(d, aes(ct, module, fill=diff)) +
  geom_tile(colour="white") +
  geom_text(aes(label=sig), size=2.6, colour="black") +
  scale_fill_gradient2(low="#1B5E9C", mid="white", high="#B02040", midpoint=0, name="patient-level\nmean diff (case-control)") +
  facet_grid(. ~ context, scales="free_x", space="free_x") +
  labs(x=NULL, y=NULL, title="Single-cell source: module differences (case vs control) by cell type") +
  theme_minimal(base_size=9) + theme(axis.text.x=element_text(angle=45, hjust=1, size=7),
    panel.grid=element_blank(), strip.background=element_rect(fill="grey92", colour=NA))
ggsave(file.path(FIG,"fig_paper_sc_source.png"), g, width=11, height=5.5, dpi=300)
ggsave(file.path(FIG,"fig_paper_sc_source.pdf"), g, width=11, height=5.5)
cat("sc figure rows:", nrow(d), "\n")
