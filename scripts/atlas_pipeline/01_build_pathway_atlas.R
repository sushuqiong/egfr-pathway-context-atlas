#!/usr/bin/env Rscript
# Pathway x Context Atlas (B'): expanded receptor/pathway modules x 16 bulk cohorts (5 contexts),
# with tissue-composition residual adjustment, cross-context consensus, and drug-class mapping.
suppressPackageStartupMessages({
  library(Biobase); library(GSVA); library(limma)
  library(dplyr); library(ggplot2); library(tidyr)
})

ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
V1P  <- "C:/Users/fengq/Desktop/EGFR胃癌/EGFR_ERBB_context_project_v1/data_processed/bulk"
V2P  <- "C:/Users/fengq/Desktop/EGFR/EGFR_ERBB_context_project_v2/data_processed/bulk"
V3P  <- "C:/Users/fengq/Desktop/EGFR/EGFR_context_expansion/data_processed/bulk"
dir.create(file.path(ROOT, "results"), recursive = TRUE, showWarnings = FALSE)
dir.create(file.path(ROOT, "figures"), recursive = TRUE, showWarnings = FALSE)
dir.create(file.path(ROOT, "reports"), recursive = TRUE, showWarnings = FALSE)

cohorts <- data.frame(
  accession = c("GSE32863","GSE19804","GSE10072","GSE44076","GSE41258","GSE23878",
                "GSE75214","GSE87473","GSE179285","GSE16879","GSE4302","GSE43696","GSE67472",
                "GSE27342","GSE63089","GSE13911",
                "GSE15471","GSE28735","GSE62452","GSE57957","GSE62232",
                "GSE23400","GSE20347","GSE76925","GSE47460","GSE33814","GSE66676"),
  disease = c(rep("LUAD",3), rep("CRC",3), rep("IBD",4), rep("Asthma",3), rep("STAD",3),
              rep("PAAD",3), rep("HCC",2), rep("ESCC",2), rep("COPD",2), rep("NAFLD",2)),
  role = c("discovery","validation","validation","discovery","validation","validation",
           "discovery","validation","validation","secondary_treatment_response",
           "discovery","validation","validation","discovery","validation","validation",
           "discovery","validation","validation","discovery","validation",
           "discovery","validation","discovery","validation","discovery","validation"),
  stringsAsFactors = FALSE)
paired_accessions <- c("GSE32863","GSE19804","GSE10072","GSE44076","GSE27342","GSE63089",
                       "GSE15471","GSE28735","GSE62452","GSE57957","GSE23400","GSE20347")

gene_sets_frame <- read.csv(file.path(ROOT,"config","gene_sets_extended.csv"), stringsAsFactors = FALSE, check.names = FALSE)
gene_sets <- split(toupper(gene_sets_frame$gene), gene_sets_frame$module)
gene_sets <- lapply(gene_sets, unique)

markers <- list(
  EPITHELIAL = c("EPCAM","KRT8","KRT18","KRT19","CDH1","KRT7"),
  IMMUNE = c("PTPRC","CD3D","CD3E","CD68","CD79A","LYZ"),
  STROMA = c("COL1A1","COL3A1","DCN","LUM","PDGFRB"),
  ENDOTHELIAL = c("PECAM1","VWF","CDH5","ENG","CLDN5"))

locate_rds <- function(acc) {
  for (d in c(V2P, V3P, V1P)) {
    f <- list.files(d, pattern = paste0("^", acc, "_processed\\.rds$"), full.names = TRUE)
    if (length(f)) return(f[1])
  }
  NA_character_
}
available_covariates <- function(meta) {
  out <- character()
  if ("age" %in% names(meta) && all(is.finite(meta$age)) && sd(meta$age) > 0) out <- c(out, "age_scaled")
  if ("sex" %in% names(meta) && all(!is.na(meta$sex)) && length(unique(meta$sex)) == 2) out <- c(out, "sex")
  if ("batch" %in% names(meta) && all(!is.na(meta$batch))) {
    lv <- length(unique(meta$batch))
    if (lv >= 2 && lv <= max(3, floor(nrow(meta) / 5))) out <- c(out, "batch")
  }
  out
}
std_effect <- function(x, meta, positive, reference, paired) {
  if (paired) {
    pv <- x[meta$group == positive]; rv <- x[meta$group == reference]
    pid <- meta$patient_id[meta$group == positive]; rid <- meta$patient_id[meta$group == reference]
    common <- intersect(pid, rid)
    d <- pv[match(common, pid)] - rv[match(common, rid)]
    if (length(d) > 1 && sd(d) > 0) mean(d)/sd(d) else NA_real_
  } else {
    a <- x[meta$group == positive]; b <- x[meta$group == reference]
    n1 <- length(a); n0 <- length(b)
    pool <- sqrt(((n1-1)*var(a) + (n0-1)*var(b)) / (n1+n0-2))
    if (is.finite(pool) && pool > 0) (1 - 3/(4*(n1+n0)-9)) * (mean(a)-mean(b))/pool else NA_real_
  }
}
fit_module_inner <- function(scores, meta, positive, reference, paired) {
  meta$grp <- stats::relevel(factor(meta$group), ref = reference)
  if (paired) {
    meta$pf <- factor(meta$patient_id)
    design <- model.matrix(~ pf + grp, data = meta)
    block <- NULL
  } else {
    meta$age_scaled <- as.numeric(scale(meta$age))
    terms <- c("grp", available_covariates(meta))
    if (exists("last_acc", envir = globalenv())) message("[DBG] ", get("last_acc", envir = globalenv()), " covs=", paste(terms, collapse = "+"))
    design <- model.matrix(as.formula(paste("~", paste(terms, collapse = "+"))), data = meta)
    block <- NULL
    if (!is.null(meta$patient_id) && anyDuplicated(meta$patient_id)) {
      corfit <- limma::duplicateCorrelation(scores, design, block = meta$patient_id)
      block <- meta$patient_id
    }
  }
  if (qr(design)$rank < ncol(design)) { # fallback to group-only if singular
    design <- model.matrix(~ grp, data = meta)
    block <- NULL
  }
  fit <- if (is.null(block)) limma::lmFit(scores, design) else
    limma::lmFit(scores, design, block = block, correlation = corfit$consensus.correlation)
  fit <- limma::eBayes(fit, trend = TRUE, robust = TRUE)
  coef <- paste0("grp", make.names(positive))
  if (!coef %in% colnames(fit$coefficients)) stop("missing coefficient")
  est <- fit$coefficients[, coef]; se <- fit$stdev.unscaled[, coef] * sqrt(fit$s2.post)
  df <- fit$df.total; if (length(df) == 1) df <- rep(df, length(est))
  p <- fit$p.value[, coef]
  data.frame(feature = rownames(scores), estimate = est, ci_low = est - qt(0.975, df)*se,
             ci_high = est + qt(0.975, df)*se, p_value = p, fdr = p.adjust(p, "BH"),
             stringsAsFactors = FALSE)
}

fit_error_log <- list()
fit_module <- function(scores, meta, positive, reference, paired) {
  tryCatch(
    fit_module_inner(scores, meta, positive, reference, paired),
    error = function(e) {
      acc <- if (exists("last_acc", envir = globalenv())) get("last_acc", envir = globalenv()) else "?"
      fit_error_log[[length(fit_error_log) + 1L]] <<- data.frame(accession = acc, error = conditionMessage(e),
        timestamp = format(Sys.time(), tz = "UTC", usetz = TRUE), stringsAsFactors = FALSE)
      data.frame(feature = rownames(scores), estimate = NA_real_, ci_low = NA_real_, ci_high = NA_real_,
                 p_value = NA_real_, fdr = NA_real_, stringsAsFactors = FALSE)
    })
}

raw_rows <- list(); adj_rows <- list(); cov_rows <- list(); comp_rows <- list(); cov_comp_rows <- list(); cover_rows <- list()
for (i in seq_len(nrow(cohorts))) {
  acc <- cohorts$accession[i]; dis <- cohorts$disease[i]; role <- cohorts$role[i]
  rds <- locate_rds(acc)
  if (is.na(rds)) { message("[MISS] ", acc); next }
  obj <- readRDS(rds)
  expr <- obj$gene_expression; meta <- obj$sample_metadata
  if (!all(c("group","sample_id") %in% names(meta))) { message("[SKIP meta] ", acc); next }
  if (!all(c("Case","Control") %in% meta$group) && !all(c("Responder","NonResponder") %in% meta$group)) next
  positive <- if (all(c("Case","Control") %in% meta$group)) "Case" else "Responder"
  reference <- if (positive == "Case") "Control" else "NonResponder"
  meta$age <- suppressWarnings(as.numeric(meta$age))
  idx <- match(meta$sample_id, colnames(expr))
  if (anyNA(idx)) { message("[SKIP colmatch] ", acc); next }
  expr <- expr[, idx]
  paired <- acc %in% paired_accessions
  assign("last_acc", acc, envir = globalenv())

  # composition scores
  comp_scores <- sapply(names(markers), function(m) {
    g <- intersect(markers[[m]], rownames(expr))
    if (length(g) < 3) return(rep(NA_real_, ncol(expr)))
    colMeans(expr[g, , drop = FALSE])
  })
  comp_scores <- as.data.frame(comp_scores)
  for (m in names(markers)) {
    vals <- comp_scores[[m]]
    if (all(is.finite(vals))) {
      smd <- std_effect(vals, meta, positive, reference, paired)
      comp_rows[[length(comp_rows)+1]] <- data.frame(accession=acc, disease=dis, role=role, compartment=m,
        genes_present = length(intersect(markers[[m]], rownames(expr))),
        smd = smd, case_mean = mean(vals[meta$group==positive]), control_mean = mean(vals[meta$group==reference]))
    }
  }

  # module scores via GSVA
  present_sets <- lapply(gene_sets, function(g) intersect(g, rownames(expr)))
  usable <- names(present_sets)[lengths(present_sets) >= 3]
  if (!length(usable)) { message("[SKIP gsva] ", acc); next }
  for (m in names(gene_sets))
    cover_rows[[length(cover_rows)+1]] <- data.frame(accession=acc, disease=dis, module=m,
      genes_present = length(present_sets[[m]]), genes_expected = length(gene_sets[[m]]),
      present = paste(present_sets[[m]], collapse=";"))
  gsva_out <- GSVA::gsva(GSVA::gsvaParam(expr, gene_sets[usable], minSize=3, maxSize=Inf, kcdf="Gaussian"), verbose=FALSE)
  rownames(gsva_out) <- usable

  raw <- fit_module(gsva_out, meta, positive, reference, paired)
  raw$smd <- vapply(rownames(gsva_out), function(m) std_effect(gsva_out[m,], meta, positive, reference, paired), numeric(1))
  raw$accession <- acc; raw$disease <- dis; raw$role <- role
  raw_rows[[length(raw_rows)+1]] <- raw

  # composition residual adjustment
  comp_ok <- names(markers)[vapply(names(markers), function(m) all(is.finite(comp_scores[[m]])), logical(1))]
  if (length(comp_ok) >= 2) {
    cmat <- as.data.frame(comp_scores[, comp_ok, drop=FALSE])
    adj <- t(apply(gsva_out, 1, function(row) {
      fit <- stats::lm(row ~ ., data = cmat)
      stats::residuals(fit)
    }))
    meta_adj <- meta
    adj_fit <- fit_module(adj, meta_adj, positive, reference, paired)
    adj_fit$smd <- vapply(rownames(adj), function(m) std_effect(adj[m,], meta_adj, positive, reference, paired), numeric(1))
    adj_fit$accession <- acc; adj_fit$disease <- dis; adj_fit$role <- role
    adj_fit$compartments_adjusted <- paste(comp_ok, collapse=";")
    adj_rows[[length(adj_rows)+1]] <- adj_fit
    cov_comp_rows[[length(cov_comp_rows)+1]] <- data.frame(accession=acc, disease=dis, role=role,
      compartments_adjusted = paste(comp_ok, collapse=";"))
  } else {
    cov_comp_rows[[length(cov_comp_rows)+1]] <- data.frame(accession=acc, disease=dis, role=role,
      compartments_adjusted = "insufficient_compartments")
  }
  message("[OK] ", acc)
}

write_out <- function(rows, file) write.csv(do.call(rbind, rows), file, row.names = FALSE)
if (length(fit_error_log)) write_out(fit_error_log, file.path(ROOT, "results/model_fit_errors.csv"))
raw_df <- do.call(rbind, raw_rows); write_out(raw_rows, file.path(ROOT,"results/module_effects_raw.csv"))
if (length(adj_rows)) write_out(adj_rows, file.path(ROOT,"results/module_effects_composition_adjusted.csv"))
write_out(comp_rows, file.path(ROOT,"results/composition_scores_summary.csv"))
write_out(cover_rows, file.path(ROOT,"results/module_coverage_extended.csv"))
write_out(cov_comp_rows, file.path(ROOT,"results/composition_adjustment_audit.csv"))

# ---- sanity vs v1 on the four original modules ----
v1mod <- read.csv("C:/Users/fengq/Desktop/EGFR胃癌/EGFR_ERBB_context_project_v1/results/bulk_module_differential.csv",
                  stringsAsFactors=FALSE, check.names=FALSE)
v1mod <- v1mod[v1mod$feature %in% names(gene_sets), c("accession","feature","standardized_effect")]
cmp <- merge(raw_df[raw_df$feature %in% c("ERBB_RECEPTORS","ERBB_LIGANDS","RAS_MAPK","PI3K_AKT"), c("accession","feature","smd")],
             v1mod, by=c("accession","feature"))
cat("v1 parity rows:", nrow(cmp), " spearman:", round(suppressWarnings(cor(cmp$smd, cmp$standardized_effect, method="spearman")),3), "\n")

# ---- cross-context atlas summary (discovery+validation only) ----
main <- raw_df[raw_df$role %in% c("discovery","validation"), ]
adj_main <- if (length(adj_rows)) do.call(rbind, adj_rows)[do.call(rbind, adj_rows)$role %in% c("discovery","validation"), ] else NULL
atlas <- main %>% group_by(disease, feature) %>% summarise(
  n_cohorts = n(), positive = sum(smd > 0, na.rm=TRUE), negative = sum(smd < 0, na.rm=TRUE),
  consistency = max(sum(smd>0,na.rm=TRUE), sum(smd<0,na.rm=TRUE))/n(),
  n_fdr_raw = sum(fdr < 0.05, na.rm=TRUE), median_smd = median(smd, na.rm=TRUE),
  median_p = median(p_value, na.rm=TRUE), .groups="drop")
atlas$direction <- ifelse(atlas$positive > atlas$negative, "up", ifelse(atlas$negative > atlas$positive, "down", "mixed"))
atlas$robust_consistent <- atlas$consistency >= 2/3 & atlas$n_fdr_raw >= 2
if (!is.null(adj_main)) {
  a2 <- adj_main %>% group_by(disease, feature) %>% summarise(n_fdr_adj = sum(fdr < 0.05, na.rm=TRUE),
    sign_keep = sum((smd>0) == (atlas$direction[1]=="up"), na.rm=TRUE), .groups="drop") # placeholder; recompute below
}
if (!is.null(adj_main)) {
  a2 <- adj_main %>% group_by(disease, feature) %>% summarise(
    n_fdr_adj = sum(fdr < 0.05, na.rm=TRUE),
    n_up_adj = sum(smd > 0, na.rm=TRUE), n_down_adj = sum(smd < 0, na.rm=TRUE), .groups="drop")
  atlas <- merge(atlas, a2, by=c("disease","feature"), all.x=TRUE)
  atlas$composition_robust <- atlas$n_fdr_adj >= 2 & pmax(atlas$n_up_adj, atlas$n_down_adj) >= 2
  # direction preserved if sign of majority raw equals sign of majority adjusted
  atlas$direction_preserved <- (atlas$positive >= atlas$negative) == (atlas$n_up_adj >= atlas$n_down_adj)
}
write.csv(as.data.frame(atlas), file.path(ROOT,"results/context_atlas_summary.csv"), row.names=FALSE)

# ---- heatmaps ----
atlas$feature <- factor(atlas$feature, levels = rev(sort(unique(atlas$feature))))
atlas$disease <- factor(atlas$disease, levels = c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma"))
g <- ggplot(atlas, aes(disease, feature, fill = median_smd)) +
  geom_tile(colour = "white") +
  geom_text(aes(label = ifelse(is.na(n_fdr_raw), "", ifelse(n_fdr_raw >= 2, paste0(n_fdr_raw, "*"), as.character(n_fdr_raw)))), size = 3.2) +
  scale_fill_gradient2(low = "#1B5E9C", mid = "white", high = "#B02040", midpoint = 0, name = "median SMD") +
  labs(x = NULL, y = NULL, title = "Growth-factor signalling module state by disease context (bulk, 27 cohorts)") +
  theme_minimal(base_size = 11) + theme(axis.text.x = element_text(angle = 45, hjust = 1), panel.grid = element_blank())
ggsave(file.path(ROOT,"figures/atlas_heatmap_raw.png"), g, width = 9, height = 9, dpi = 300)
ggsave(file.path(ROOT,"figures/atlas_heatmap_raw.pdf"), g, width = 9, height = 9)

if (!is.null(adj_main)) {
  atlas2 <- atlas; atlas2$median_smd <- NULL
  am <- adj_main %>% group_by(disease, feature) %>% summarise(median_smd = median(smd, na.rm=TRUE), n_fdr = sum(fdr < 0.05, na.rm=TRUE), .groups="drop")
  am$feature <- factor(am$feature, levels = levels(atlas$feature)); am$disease <- factor(am$disease, levels = c("LUAD","CRC","STAD","PAAD","HCC","ESCC","IBD","COPD","NAFLD","Asthma"))
  g2 <- ggplot(am, aes(disease, feature, fill = median_smd)) + geom_tile(colour="white") +
    geom_text(aes(label = ifelse(is.na(n_fdr), "", ifelse(n_fdr >= 2, paste0(n_fdr,"*"), as.character(n_fdr)))), size=3.2) +
    scale_fill_gradient2(low="#1B5E9C", mid="white", high="#B02040", midpoint=0, name="median SMD") +
    labs(x=NULL, y=NULL, title="Composition-adjusted module state by disease context") +
    theme_minimal(base_size=11) + theme(axis.text.x=element_text(angle=45, hjust=1), panel.grid=element_blank())
  ggsave(file.path(ROOT,"figures/atlas_heatmap_composition_adjusted.png"), g2, width=9, height=9, dpi=300)
  ggsave(file.path(ROOT,"figures/atlas_heatmap_composition_adjusted.pdf"), g2, width=9, height=9)
}

# ---- ecological link: cohort-level module smd vs composition smd ----
comp_sum <- do.call(rbind, comp_rows)
eco <- merge(main[, c("accession","disease","feature","smd")], comp_sum[, c("accession","compartment","smd")], by="accession")
eco_cor <- eco %>% filter(is.finite(smd.x) & is.finite(smd.y)) %>% group_by(feature, compartment) %>%
  summarise(n = n(), rho = suppressWarnings(cor(smd.x, smd.y, method="spearman")), .groups="drop")
eco_cor$p <- NA_real_
if (nrow(eco_cor)) {
  eco_split <- split(eco, list(eco$feature, eco$compartment), drop=TRUE)
  eco_cor$p <- vapply(seq_len(nrow(eco_cor)), function(i) {
    f <- eco_cor$feature[i]; cc <- eco_cor$compartment[i]
    sub <- eco[eco$feature==f & eco$compartment==cc & is.finite(eco$smd.x) & is.finite(eco$smd.y), ]
    if (nrow(sub) >= 6) suppressWarnings(cor.test(sub$smd.x, sub$smd.y, method="spearman")$p.value) else NA_real_
  }, numeric(1))
  eco_cor$fdr <- p.adjust(eco_cor$p, "BH")
}
write.csv(as.data.frame(eco_cor), file.path(ROOT,"results/ecological_module_vs_composition_correlations.csv"), row.names=FALSE)
cat("Atlas rows:", nrow(atlas), " robust_consistent:", sum(atlas$robust_consistent, na.rm=TRUE), "\n")
print(atlas[atlas$robust_consistent %in% TRUE, c("disease","feature","positive","negative","n_fdr_raw","median_smd")], row.names=FALSE)
