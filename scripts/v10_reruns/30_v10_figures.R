#!/usr/bin/env Rscript
# v10 figures generated strictly from frozen result tables
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(ggplot2)})
A <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
V <- "C:/Users/fengq/Desktop/EGFR/EGFR的v10/reruns/results"
F10 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v10/02_图片"
dir.create(F10, recursive=TRUE, showWarnings=FALSE)
ctx <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma")
lab <- function(x){ x <- gsub("_AXIS$","",x); x <- gsub("_RECEPTORS","",x)
  m <- c("ERBB_LIGANDS"="ERBB-L","PDGFR_KIT_CSF1R"="PDGFR-KIT","RET_ALK_NTRK"="RET/ALK","VEGF_PDGF"="VEGF/PDGF",
         "TIE_ANGPT"="TIE/Ang","HGF_MET"="HGF/MET","TAM_AXL"="TAM/AXL","IGF_INSR"="IGF/INSR","TGFB_SMAD"="TGF\u03b2",
         "WNT_CTNNB1"="WNT/\u03b2-cat","PI3K_AKT"="PI3K-AKT","RAS_MAPK"="RAS-MAPK","JAK_STAT"="JAK-STAT",
         "SRC_FAK"="SRC/FAK","ERBB"="ERBB"); ifelse(x %in% names(m), m[x], x) }
th <- function(base=12) theme_bw(base_size=base) +
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_line(colour="grey93", linewidth=.25),
        legend.position="bottom", strip.background=element_rect(fill="grey92", colour=NA),
        strip.text=element_text(face="bold"), plot.title=element_text(face="bold", hjust=0, size=base+1))

# ---- Fig2A raw ----
raw <- read.csv(file.path(A,"context_atlas_summary.csv"), stringsAsFactors=FALSE)
raw$disease <- factor(raw$disease, levels=ctx)
raw$flab <- factor(lab(raw$feature), levels=rev(sort(unique(lab(raw$feature)))))
raw$txtc <- ifelse(abs(raw$median_smd)>1.0,"white","grey20")
g2a <- ggplot(raw, aes(disease, flab)) + geom_tile(aes(fill=median_smd), colour="white", linewidth=.4) +
  geom_text(aes(label=ifelse(n_fdr_raw>=1, n_fdr_raw, ""), colour=txtc), size=2.5) +
  geom_point(data=raw[raw$robust_consistent,], shape=8, size=1.7, colour="black") +
  scale_colour_identity() +
  scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0, name="raw median SMD") +
  scale_x_discrete(position="top") + labs(x=NULL,y=NULL,title="A  Raw module states (per-cohort analysis)") +
  th() + theme(axis.text.x=element_text(angle=35,hjust=0,size=10))
ggsave(file.path(F10,"fig2a_raw_v10.png"), g2a, width=8.2, height=7.0, dpi=300)
ggsave(file.path(F10,"fig2a_raw_v10.pdf"), g2a, width=8.2, height=7.0)

# ---- Fig2B joint models (with explicit not-estimable) ----
js <- read.csv(file.path(V,"v10_joint_summary.csv"), stringsAsFactors=FALSE)
js$flab <- lab(js$feature)
raw$flab_chr <- as.character(raw$flab); js$flab_chr <- js$flab
grid <- expand.grid(disease=ctx, flab_chr=unique(raw$flab_chr), stringsAsFactors=FALSE)
m2 <- merge(grid, js[,c("disease","flab_chr","n_analysed","n_fdr","median_d_adj","joint_robust")],
            by=c("disease","flab_chr"), all.x=TRUE)
m2$flab <- factor(m2$flab_chr, levels=levels(raw$flab))
m2$disease <- factor(m2$disease, levels=ctx); m2$flab <- factor(m2$flab, levels=levels(raw$flab))
m2$txtc <- ifelse(!is.na(m2$median_d_adj) & abs(m2$median_d_adj)>1.0,"white","grey20")
m2$lab_txt <- ifelse(is.na(m2$median_d_adj), "n.e.", ifelse(m2$n_fdr>=1, as.character(m2$n_fdr), ""))
g2b <- ggplot(m2, aes(disease, flab)) + geom_tile(aes(fill=median_d_adj), colour="white", linewidth=.4) +
  geom_text(aes(label=lab_txt, colour=txtc), size=2.5) +
  geom_point(data=m2[!is.na(m2$joint_robust) & m2$joint_robust,], shape=23, size=2.3, fill="black", colour="white", stroke=.5) +
  scale_colour_identity() +
  scale_fill_gradient2(low="#14457B", mid="white", high="#A6123C", midpoint=0, na.value="grey85",
                       name="joint-model adjusted difference (SD)") +
  scale_x_discrete(position="top") + labs(x=NULL,y=NULL,title="B  Composition-adjusted (joint models; n.e. = not estimable)") +
  th() + theme(axis.text.x=element_text(angle=35,hjust=0,size=10))
ggsave(file.path(F10,"fig2b_joint_v10.png"), g2b, width=8.2, height=7.0, dpi=300)
ggsave(file.path(F10,"fig2b_joint_v10.pdf"), g2b, width=8.2, height=7.0)

# ---- Fig3 raw vs joint scatter ----
ev <- read.csv(file.path(V,"v10_evidence_matrix.csv"), stringsAsFactors=FALSE)
e3 <- ev[is.finite(ev$median_smd) & is.finite(ev$median_d_adj),]
e3$class <- ifelse(e3$joint_robust %in% TRUE, "joint-robust","not joint-robust")
g3 <- ggplot(e3, aes(median_smd, median_d_adj, colour=class)) +
  geom_hline(yintercept=0, linetype="dotted", colour="grey60") + geom_vline(xintercept=0, linetype="dotted", colour="grey60") +
  geom_abline(slope=1, intercept=0, linetype="22", colour="grey55") +
  geom_point(size=2, alpha=.85) +
  scale_colour_manual(values=c("joint-robust"="#A6123C","not joint-robust"="grey55")) +
  labs(x="raw median SMD", y="joint-model adjusted difference (SD)", colour=NULL,
       title="Composition adjustment: raw vs joint models (n=170 states)") + th() +
  guides(colour=guide_legend(override.aes=list(size=2.6)))
ggsave(file.path(F10,"fig3_composition_v10.png"), g3, width=6.6, height=5.6, dpi=300)
ggsave(file.path(F10,"fig3_composition_v10.pdf"), g3, width=6.6, height=5.6)

# ---- Fig4 TCGA forest ----
sv <- read.csv(file.path(A,"cbio_v3_survival_cox.csv"), stringsAsFactors=FALSE)
f4 <- sv[sv$fdr<0.05,]
f4$context <- factor(f4$context, levels=c("LUAD","CRC","STAD","PAAD","HCC","ESCC"))
f4$label <- paste0(lab(f4$feature), " (", f4$context, ")")
f4<-f4[order(f4$context, f4$hazard_ratio_per_1sd),]
f4$label<-factor(f4$label, levels=f4$label)
g4 <- ggplot(f4, aes(hazard_ratio_per_1sd, label, colour=context)) +
  geom_vline(xintercept=1, linetype="dashed", colour="grey50") +
  geom_errorbarh(aes(xmin=ci_low, xmax=ci_high), height=.25) + geom_point(size=2.4) +
  labs(x="hazard ratio per 1 SD (95% CI)", y=NULL, colour="context",
       title="TCGA module-OS associations (FDR<0.05)") + th(11)
ggsave(file.path(F10,"fig4_survival_v10.png"), g4, width=7.4, height=6.6, dpi=300)
ggsave(file.path(F10,"fig4_survival_v10.pdf"), g4, width=7.4, height=6.6)

# ---- Fig5 molecular: amplification + mutation panels ----
cna <- read.csv(file.path(A,"cbio_v3_cna_summary.csv"), stringsAsFactors=FALSE) %>% filter(gene %in% c("EGFR","ERBB2"))
mut <- read.csv(file.path(A,"cbio_v3_mutation_summary.csv"), stringsAsFactors=FALSE) %>% filter(gene %in% c("TP53","KRAS","EGFR"))
cna$context <- factor(cna$context, levels=c("LUAD","CRC","STAD","PAAD","HCC","ESCC"))
mut$context <- factor(mut$context, levels=c("LUAD","CRC","STAD","PAAD","HCC","ESCC"))
pA <- ggplot(cna, aes(context, high_amp_percent)) + geom_col(fill="#A6123C", width=.62) +
  geom_text(aes(label=sprintf("%.1f", high_amp_percent)), vjust=-0.4, size=2.5) +
  facet_wrap(~gene, nrow=1, scales="free_y") + labs(x=NULL,y="high-level amplification (%)",title="A  Amplification") +
  th(10.5) + theme(axis.text.x=element_text(angle=35,hjust=1,size=9))
pB <- ggplot(mut, aes(context, mutated_percent)) + geom_col(fill="#14457B", width=.62) +
  geom_text(aes(label=sprintf("%.0f", mutated_percent)), vjust=-0.4, size=2.5) +
  facet_wrap(~gene, nrow=1, scales="free_y") + labs(x=NULL,y="mutation (%)",title="B  Mutation") +
  th(10.5) + theme(axis.text.x=element_text(angle=35,hjust=1,size=9))
library(patchwork)
g5 <- pA / pB + plot_annotation(title="Molecular context across six cancers")
ggsave(file.path(F10,"fig5_molecular_v10.png"), g5, width=8.4, height=7.4, dpi=300)
ggsave(file.path(F10,"fig5_molecular_v10.pdf"), g5, width=8.4, height=7.4)

# ---- Fig6 single-cell hits with patient numbers ----
sc <- read.csv(file.path(A,"sc_top_hit_cell_source_validation.csv"), stringsAsFactors=FALSE)
h <- sc %>% filter(fdr<0.05) %>% mutate(diff=case_patient_mean-control_patient_mean,
     item=paste0(module," | ",cell_type," (",n_case_patients,"v",n_control_patients,")"))
h$context <- factor(h$context, levels=c("CRC","IBD","STAD"))
h <- h %>% arrange(context, diff); h$item <- factor(h$item, levels=h$item)
g6 <- ggplot(h, aes(diff, item, fill=diff>0)) + geom_col(width=.6) +
  geom_vline(xintercept=0, colour="grey40") +
  scale_fill_manual(values=c("TRUE"="#A6123C","FALSE"="#14457B"), guide="none") +
  facet_grid(context~., scales="free_y", space="free_y") +
  labs(x="patient-level mean difference (case - control)", y=NULL,
       title="Single-cell source hits (global FDR<0.05); labels show module | cell type (n cases v controls)") +
  th(10.5)
ggsave(file.path(F10,"fig6_sc_v10.png"), g6, width=8.0, height=max(4.5, 0.34*nrow(h)+2), dpi=300)
ggsave(file.path(F10,"fig6_sc_v10.pdf"), g6, width=8.0, height=max(4.5, 0.34*nrow(h)+2))
cat("figures written to", F10, "\n")
