#!/usr/bin/env Rscript
# cbio_v3 unified molecular layer: 17-module scores, OS Cox, CNA and mutation summaries
# across six TCGA cancer contexts (LUAD, CRC, STAD, PAAD, HCC/LIHC, ESCC/ESCA-filtered).
suppressPackageStartupMessages({library(dplyr); library(survival)})
ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
RES <- file.path(ROOT, "results")
read_csv <- function(f) read.csv(f, stringsAsFactors=FALSE, check.names=FALSE, fileEncoding="UTF-8-BOM")
write_csv <- function(df, f) write.csv(df, f, row.names=FALSE)

gs <- read_csv(file.path(ROOT, "config/gene_sets_extended.csv"))
modules <- split(toupper(gs$gene), gs$module)
mods <- names(modules)
expr <- read_csv(file.path(RES, "cbio_v3_expression_gene_sample.csv"))
cna  <- read_csv(file.path(RES, "cbio_v3_cna_gene_sample.csv"))
mut  <- read_csv(file.path(RES, "cbio_v3_mutations.csv"))
clin <- read_csv(file.path(RES, "cbio_v3_clinical_patient.csv"))

# ESCC subtype filter (Esophagus Squamous Cell Carcinoma)
subtype <- clin %>% filter(context == "ESCC") %>% group_by(patient_id) %>%
  summarise(hist = paste(unique(value[clinical_attribute_id %in% c("DISEASE_TYPE","PRIMARY_DIAGNOSIS")]), collapse=";"), .groups="drop")
escc_pat <- unique(subtype$patient_id[grepl("Squamous", subtype$hist)])
escc_expr_pat <- unique(expr$patient_id[expr$context=="ESCC"])
escc_pat <- intersect(escc_pat, escc_expr_pat)

# per-gene z-scores within context (ESCC uses the ESCC-only patient subset)
expr_num <- expr
expr_num$value <- suppressWarnings(as.numeric(expr_num$value))
expr_num$log2v <- log2(pmax(expr_num$value, 0) + 1)
if (nrow(expr_num)) {
  expr_keep <- expr_num[!is.na(expr_num$log2v), ]
  z <- expr_keep %>% group_by(context, gene) %>%
    mutate(z = (log2v - mean(log2v)) / (sd(log2v) + 1e-9)) %>% ungroup()
} else z <- expr_num
# ESCC: restrict patients (whole row set) to escc_pat
z <- z %>% filter(!(context == "ESCC" & !(patient_id %in% escc_pat)))
# patient-level expression wide for module scoring (mean of member z-scores)
# first aggregate per patient per gene
pat_gene <- z %>% group_by(context, patient_id, gene) %>% summarise(z = mean(z, na.rm=TRUE), .groups="drop")

module_scores <- list()
for (m in mods) {
  mem <- intersect(modules[[m]], unique(pat_gene$gene))
  if (length(mem) < 2) next
  sub <- pat_gene %>% filter(gene %in% mem) %>% group_by(context, patient_id) %>%
    summarise(score = mean(z, na.rm=TRUE), n_genes = n(), .groups="drop") %>%
    filter(n_genes >= 2) %>% select(context, patient_id, score)
  sub$module <- m
  module_scores[[length(module_scores)+1]] <- sub
}
ms <- bind_rows(module_scores)
write_csv(ms, file.path(RES, "cbio_v3_patient_module_scores.csv"))

# survival
clin_wide <- clin %>% select(context, patient_id, clinical_attribute_id, value) %>%
  filter(clinical_attribute_id %in% c("OS_MONTHS","OS_STATUS","DISEASE_TYPE","PRIMARY_DIAGNOSIS")) %>%
  tidyr::pivot_wider(names_from = clinical_attribute_id, values_from = value, values_fn = function(x) paste(unique(x), collapse=";"))
clin_wide <- clin_wide %>% mutate(time = suppressWarnings(as.numeric(OS_MONTHS)),
  event = as.integer(grepl("DECEASED", OS_STATUS, ignore.case=TRUE)),
  cancer = suppressWarnings(as.numeric(NA)))
if (nrow(clin_wide)) {
  ms_wide <- ms %>% tidyr::pivot_wider(id_cols = c(context, patient_id), names_from = module, values_from = score)
  egfr_pat <- pat_gene %>% filter(gene == "EGFR") %>% select(context, patient_id, EGFR = z)
  surv_rows <- list()
  for (ctx in unique(ms_wide$context)) {
    cc <- clin_wide %>% filter(context == ctx) %>% select(patient_id, time, event)
    dat <- merge(cc, ms_wide[ms_wide$context == ctx, ], by = "patient_id", all = FALSE)
    eg <- egfr_pat %>% filter(context == ctx)
    dat$EGFR <- eg$EGFR[match(dat$patient_id, eg$patient_id)]
    dat <- dat[is.finite(dat$time) & dat$time > 0 & !is.na(dat$event), ]
    feats <- intersect(c("EGFR", mods), names(dat))
    for (f in feats) {
      keep <- is.finite(dat[[f]])
      if (sum(keep) < 40) next
      dd <- dat[keep, ]
      if (sum(dd$event) < 10) next
      fit <- tryCatch(coxph(Surv(time, event) ~ scale(dd[[f]]), data = dd), error = function(e) NULL)
      if (is.null(fit)) next
      surv_rows[[length(surv_rows)+1]] <- data.frame(context = ctx, feature = f, n = sum(keep),
        events = sum(dd$event), hazard_ratio_per_1sd = exp(coef(fit)),
        ci_low = exp(confint(fit)[1]), ci_high = exp(confint(fit)[2]),
        p_value = coef(summary(fit))[, "Pr(>|z|)"])
    }
  }
  surv <- bind_rows(surv_rows)
  surv$fdr <- p.adjust(surv$p_value, "BH")
  write_csv(surv, file.path(RES, "cbio_v3_survival_cox.csv"))
  cat("survival rows:", nrow(surv), " FDR<0.05:", sum(surv$fdr < 0.05, na.rm=TRUE), "\n")
}

# CNA summaries (curated receptor list)
rec_genes <- c("EGFR","ERBB2","ERBB3","ERBB4","MET","FGFR1","FGFR2","FGFR3","FGFR4","PDGFRA","PDGFRB",
  "KIT","CSF1R","AXL","MERTK","TYRO3","RET","ALK","ROS1","NTRK1","EPHA1","EPHA2","EPHB2","EPHB4",
  "TEK","IGF1R","INSR","FLT1","KDR","FLT4")
cna$value <- suppressWarnings(as.numeric(cna$value))
cna_ok <- cna[!is.na(cna$value) & cna$gene %in% rec_genes, ]
# ESCC sample->patient via expression map
map_ep <- unique(expr_num[, c("context","sample_id","patient_id")])
cna_ok <- cna_ok %>% left_join(map_ep, by=c("context","sample_id")) %>%
  mutate(patient_id = ifelse(is.na(patient_id.y), patient_id.x, patient_id.y)) %>% select(-patient_id.x, -patient_id.y)
cna_ok <- cna_ok %>% filter(!(context == "ESCC" & !(patient_id %in% escc_pat)))
cna_sum <- cna_ok %>% group_by(context, gene) %>% summarise(
  n_samples = n(), gain_or_amp_n = sum(value >= 1), high_amp_n = sum(value == 2), .groups="drop") %>%
  mutate(gain_or_amp_percent = 100 * gain_or_amp_n / n_samples, high_amp_percent = 100 * high_amp_n / n_samples)
write_csv(as.data.frame(cna_sum), file.path(RES, "cbio_v3_cna_summary.csv"))
cat("cna summary rows:", nrow(cna_sum), "\n")

# mutation summaries (any module gene + TP53)
mut_genes <- unique(c(TP53 = "TP53", unlist(modules)))
mut$gene <- toupper(mut$gene)
mut_sub <- mut[mut$gene %in% mut_genes, ]
mut_sub <- mut_sub %>% left_join(map_ep, by=c("context","sample_id")) %>%
  mutate(patient_id = ifelse(is.na(patient_id.y), patient_id.x, patient_id.y)) %>% select(-patient_id.x, -patient_id.y)
mut_sub <- mut_sub %>% filter(!(context == "ESCC" & !(patient_id %in% escc_pat)))
seq_n <- cna_ok %>% group_by(context) %>% summarise(n_sequenced = n_distinct(sample_id), .groups="drop")
mut_rows <- mut_sub %>% distinct(context, sample_id, gene) %>%
  group_by(context, gene) %>% summarise(n_mutated = n(), .groups="drop")
mut_sum <- mut_rows %>% left_join(seq_n, by="context") %>% mutate(mutated_percent = 100 * n_mutated / n_sequenced)
write_csv(as.data.frame(mut_sum), file.path(RES, "cbio_v3_mutation_summary.csv"))
cat("mutation summary rows:", nrow(mut_sum), "\n")

cat("ESCC patients (squamous):", length(escc_pat), "\n")
cat("patient-module score rows:", nrow(ms), "\n")
