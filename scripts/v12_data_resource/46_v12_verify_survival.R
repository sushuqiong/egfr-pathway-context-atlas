#!/usr/bin/env Rscript
# v12 adversarial checkpoint 3: independent recomputation of the TCGA survival layer for three contexts.
# (a) rebuild patient-level module scores from the gene-level expression table and compare with the shipped table
# (b) refit univariable and age/age+stage-adjusted Cox models and compare HR/p with the shipped tables
# (c) for ESCC, restrict to the squamous subset and compare with the v12 squamous survival table
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(survival)})
A  <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
R  <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
PK <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/dataset_package"
gs <- read.csv(file.path(PK,"04_modules","module_definitions.csv"), stringsAsFactors=FALSE)
sets <- lapply(split(toupper(gs$gene), gs$module), unique)
expr <- read.csv(file.path(A,"cbio_v3_expression_gene_sample.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
shipped_scores <- read.csv(file.path(A,"cbio_v3_patient_module_scores.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
clin <- read.csv(file.path(A,"cbio_v3_clinical_patient.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
uni <- read.csv(file.path(A,"cbio_v3_survival_cox.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
mv  <- read.csv(file.path(A,"cbio_v5_multivariable_survival.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
hist <- read.csv(file.path(R,"v12_escc_squamous_samples.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
sq_pat <- unique(hist$patient_id)
score_cmp <- list(); cox_cmp <- list()
for (ctx in c("LUAD","CRC","ESCC")) {
  e <- expr[expr$context==ctx, ]
  e$v <- suppressWarnings(as.numeric(e$value))
  e <- e[is.finite(e$v) & !is.na(e$patient_id) & e$patient_id!="", ]
  e$log2v <- log2(pmax(e$v,0)+1)
  # member-mean z per patient, computed independently
  rec <- list()
  for (m in names(sets)) {
    gm <- intersect(sets[[m]], unique(toupper(e$gene)))
    sub <- e[toupper(e$gene) %in% gm, ]
    if (!nrow(sub)) next
    per <- sub %>% group_by(patient_id) %>% summarise(mean_expr=mean(log2v, na.rm=TRUE), .groups="drop")
    if (nrow(per) < 20) next
    per$z <- as.numeric(scale(per$mean_expr))
    rec[[length(rec)+1]] <- data.frame(context=ctx, patient_id=per$patient_id, module=m, z_recomputed=per$z, stringsAsFactors=FALSE)
  }
  rec <- bind_rows(rec)
  sh <- shipped_scores[shipped_scores$context==ctx, ]
  mrg <- merge(rec, sh, by=c("context","patient_id","module"))
  if (nrow(mrg)) {
    ct <- suppressWarnings(cor(mrg$z_recomputed, mrg$score, method="spearman"))
    score_cmp[[length(score_cmp)+1]] <- data.frame(context=ctx, pairs=nrow(mrg), spearman=round(ct,4),
      max_abs_diff=round(max(abs(mrg$z_recomputed - mrg$score)),4), stringsAsFactors=FALSE)
  }
  # ---- Cox refit
  w <- clin %>% filter(context==ctx) %>% select(patient_id, clinical_attribute_id, value) %>%
    filter(clinical_attribute_id %in% c("OS_MONTHS","OS_STATUS","AGE","PATH_STAGE","CLINICAL_STAGE")) %>%
    pivot_wider(names_from=clinical_attribute_id, values_from=value, values_fn=function(x) paste(unique(x), collapse=";"))
  s <- shipped_scores %>% filter(context==ctx) %>% select(patient_id, module, score) %>% pivot_wider(names_from=module, values_from=score) %>% left_join(w, by="patient_id")
  s$time <- suppressWarnings(as.numeric(s$OS_MONTHS)); s$event <- as.integer(grepl("DECEASED", s$OS_STATUS, ignore.case=TRUE))
  s$age <- suppressWarnings(as.numeric(s$AGE))
  stage_src <- if ("PATH_STAGE" %in% names(s)) as.character(s$PATH_STAGE) else rep(NA_character_, nrow(s))
  if ("CLINICAL_STAGE" %in% names(s)) stage_src <- ifelse(!is.na(stage_src) & stage_src != "", stage_src, as.character(s$CLINICAL_STAGE))
  st <- toupper(gsub("[^IVX]", "", stage_src))
  s$stage4 <- ifelse(st %in% c("I","II","III","IV"), match(st, c("I","II","III","IV")), NA)
  s <- s[is.finite(s$time) & s$time>0 & !is.na(s$event), ]
  if (ctx=="ESCC") s <- s[s$patient_id %in% sq_pat, ]
  feats <- intersect(names(shipped_scores) %>% unique(), names(s))
  feats <- setdiff(names(s), c("patient_id","OS_MONTHS","OS_STATUS","AGE","PATH_STAGE","CLINICAL_STAGE","time","event","age","stage4"))
  for (f in feats) {
    d <- s; d$z <- as.numeric(scale(d[[f]])); if (!is.finite(sd(d[[f]], na.rm=TRUE)) || sd(d[[f]], na.rm=TRUE)==0) next
    f1 <- tryCatch(coxph(Surv(time,event) ~ z, data=d), error=function(e) NULL); if (is.null(f1)) next
    f3 <- tryCatch(coxph(Surv(time,event) ~ z + age + stage4, data=d[complete.cases(d[, c("z","time","event","age","stage4")]),]), error=function(e) NULL)
    ref <- if (ctx=="ESCC") read.csv(file.path(R,"v12_escc_squamous_survival_cox.csv"), stringsAsFactors=FALSE) else NULL
    for (mdl in c("uni","age+stage")) {
      fit <- if (mdl=="uni") f1 else f3
      if (is.null(fit)) next
      hr <- exp(coef(fit)["z"]); pv <- summary(fit)$coefficients["z","Pr(>|z|)"]; nn <- fit$n
      sh_ref <- if (ctx=="ESCC") ref[ref$feature==f & ref$model==mdl, ] else if (mdl=="uni") uni[uni$context==ctx & uni$feature==f, ] else mv[mv$context==ctx & mv$feature==f & grepl("age", mv$model, ignore.case=TRUE), ]
      if (!nrow(sh_ref)) next
      hr_col <- intersect(c("HR","hazard_ratio_per_1sd","hazard_ratio"), names(sh_ref))[1]
      p_col  <- intersect(c("p","p_value","pval"), names(sh_ref))[1]
      if (is.na(hr_col)) next
      hr_sh <- as.numeric(sh_ref[[hr_col]][1])
      p_sh  <- if (!is.na(p_col)) as.numeric(sh_ref[[p_col]][1]) else NA_real_
      if (!is.finite(hr_sh)) next
      cox_cmp[[length(cox_cmp)+1]] <- data.frame(context=ctx, model=mdl, feature=f, n_recomputed=nn,
        HR_recomputed=round(hr,4), HR_shipped=round(hr_sh,4), HR_abs_diff=round(abs(hr-hr_sh),4),
        p_recomputed=signif(pv,4), p_shipped=signif(p_sh,4), stringsAsFactors=FALSE)
    }
  }
  cat("[OK]", ctx, "score pairs:", sum(score_cmp[[length(score_cmp)]]$pairs), "| cox rows so far:", length(cox_cmp), "\n")
}
sc <- bind_rows(score_cmp); cx <- bind_rows(cox_cmp)
write.csv(sc, file.path(R,"v12_qc_survival_score_verification.csv"), row.names=FALSE)
write.csv(cx, file.path(R,"v12_qc_survival_cox_verification.csv"), row.names=FALSE)
cat("\n== module score agreement (TCGA layer) ==\n"); print(sc, row.names=FALSE)
cat("\n== Cox agreement ==\n")
print(cx %>% group_by(context, model) %>% summarise(models=n(), max_HR_diff=max(HR_abs_diff), median_HR_diff=median(HR_abs_diff), .groups="drop") %>% as.data.frame(), row.names=FALSE)
cat("\nmax absolute HR difference across all comparisons:", max(cx$HR_abs_diff), "\n")
