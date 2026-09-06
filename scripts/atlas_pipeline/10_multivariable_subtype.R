#!/usr/bin/env Rscript
# v5 analyses responding to adversarial review:
# (1) multivariable OS Cox (age + pathological stage) for module scores, six cancers;
# (2) CRC SUBTYPE-stratified module-OS (COAD_CIN / COAD_MSI / GS / POLE);
# (3) confirm k>=2 meta counts (73/170 vs 75/170).
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(survival)})
ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
RES <- file.path(ROOT, "results")
rd <- function(f, ...) read.csv(file.path(RES, f), stringsAsFactors=FALSE, check.names=FALSE, ...)

clin <- rd("cbio_v3_clinical_patient.csv")
ms <- rd("cbio_v3_patient_module_scores.csv")
ms_wide <- ms %>% select(context, patient_id, module, score) %>%
  pivot_wider(id_cols=c(context, patient_id), names_from=module, values_from=score)
# stage ordinal & age & subtype from clinical attributes
extract_clin <- function(attr, context) {
  clin %>% filter(context == !!context & clinical_attribute_id == attr) %>%
    select(patient_id, value)
}
stage_map <- c("Stage 0"=0,"Stage I"=1,"Stage IA"=1,"Stage IB"=1,"Stage II"=2,"Stage IIA"=2,"Stage IIB"=2,
               "Stage III"=3,"Stage IIIA"=3,"Stage IIIB"=3,"Stage IIIC"=3,"Stage IV"=4,"Stage IVA"=4,"Stage IVB"=4)
to_stage <- function(v){ st <- stage_map[v]; ifelse(is.na(st), NA_real_, st) }
ctx <- c("LUAD","CRC","STAD","PAAD","HCC","ESCC")
out <- list()
for (c in ctx) {
  age <- extract_clin("AGE", c); names(age)[2] <- "age"
  stg <- extract_clin("PATH_STAGE", c)
  if (nrow(stg)==0 || all(is.na(to_stage(stg$value)))) stg <- extract_clin("AJCC_STAGING_EDITION", c)  # fallback rarely numeric; guard
  stg2 <- extract_clin("PATH_STAGE", c)
  surv <- clin %>% filter(context==c & clinical_attribute_id %in% c("OS_MONTHS","OS_STATUS")) %>%
    select(patient_id, clinical_attribute_id, value) %>%
    pivot_wider(names_from=clinical_attribute_id, values_from=value, values_fn=function(x) paste(unique(x), collapse=";")) %>%
    mutate(time=suppressWarnings(as.numeric(OS_MONTHS)), event=as.integer(grepl("DECEASED", OS_STATUS, ignore.case=TRUE)))
  dat <- surv %>% select(patient_id, time, event) %>% merge(ms_wide[ms_wide$context==c, ], by="patient_id", all=FALSE) %>%
    merge(age, by="patient_id", all.x=TRUE) %>% merge(stg2, by="patient_id", all.x=TRUE)
  dat$age <- suppressWarnings(as.numeric(dat$age)); dat$stage <- to_stage(dat$value)
  # if PATH_STAGE absent entirely, stage stays NA
  feats <- intersect(names(ms_wide), names(dat))
  feats <- setdiff(feats, c("patient_id","context","module","score"))
  for (f in feats) {
    dd <- dat[is.finite(dat[[f]]) & is.finite(dat$time) & dat$time>0 & !is.na(dat$event), ]
    if (nrow(dd) < 40 || sum(dd$event) < 10) next
    # model A: univariable for baseline; model B: +age; model C: +age+stage (only where stage non-NA)
    dd$zf <- scale(dd[[f]])[,1]
    mB <- tryCatch(coxph(Surv(time, event) ~ zf + age, data=dd), error=function(e) NULL)
    if (is.null(mB)) next
    HR_B <- exp(coef(mB)["zf"]); p_B <- coef(summary(mB))["zf","Pr(>|z|)"]
    n_s <- sum(!is.na(dd$stage) & is.finite(dd$stage))
    HR_C <- NA; p_C <- NA
    if (n_s >= 30 && sum(dd$event[!is.na(dd$stage)]) >= 8) {
      mC <- tryCatch(coxph(Surv(time, event) ~ zf + age + stage, data=dd), error=function(e) NULL)
      if (!is.null(mC)) { HR_C <- exp(coef(mC)["zf"]); p_C <- coef(summary(mC))["zf","Pr(>|z|)"] }
    }
    out[[length(out)+1]] <- data.frame(context=c, feature=f, n=nrow(dd), events=sum(dd$event),
      HR_uni=NA, p_uni=NA, HR_age=HR_B, p_age=p_B, HR_age_stage=HR_C, p_age_stage=p_C, n_with_stage=n_s)
  }
}
mv <- bind_rows(out)
mv$fdr_age <- p.adjust(mv$p_age, "BH")
mv$fdr_age_stage <- p.adjust(mv$p_age_stage, "BH")
write.csv(mv, file.path(RES, "cbio_v5_multivariable_survival.csv"), row.names=FALSE)
cat("multivariable rows:", nrow(mv), " age-adjusted FDR<0.05:", sum(mv$fdr_age<0.05, na.rm=TRUE),
    " age+stage FDR<0.05:", sum(mv$fdr_age_stage<0.05, na.rm=TRUE), "\n")

# CRC subtype stratification
sub <- clin %>% filter(context=="CRC" & grepl("SUBTYPE", clinical_attribute_id)) %>% select(patient_id, subtype=value)
sub <- sub %>% filter(grepl("COAD_|READ_", subtype)) %>% mutate(subtype = gsub("READ_.*","READ", subtype))
subtype_pat <- sub %>% filter(subtype %in% c("COAD_CIN","COAD_MSI","COAD_GS","COAD_POLE"))
surv_crc <- clin %>% filter(context=="CRC" & clinical_attribute_id %in% c("OS_MONTHS","OS_STATUS")) %>%
  select(patient_id, clinical_attribute_id, value) %>%
  pivot_wider(names_from=clinical_attribute_id, values_from=value, values_fn=function(x) paste(unique(x), collapse=";")) %>%
  mutate(time=suppressWarnings(as.numeric(OS_MONTHS)), event=as.integer(grepl("DECEASED", OS_STATUS, ignore.case=TRUE)))
sc_out <- list()
dat_crc <- surv_crc %>% merge(ms_wide[ms_wide$context=="CRC", ], by="patient_id", all=FALSE) %>%
  merge(subtype_pat, by="patient_id", all.x=TRUE)
for (f in c("ERBB_LIGANDS","WNT_CTNNB1","EPH_RECEPTORS","JAK_STAT","HGF_MET_AXIS","VEGF_PDGF_AXIS")) {
  for (st in c("COAD_CIN","COAD_MSI","COAD_GS")) {
    dd <- dat_crc[dat_crc$subtype==st & is.finite(dat_crc[[f]]) & is.finite(dat_crc$time) & dat_crc$time>0 & !is.na(dat_crc$event), ]
    if (nrow(dd) < 20 || sum(dd$event, na.rm=TRUE) < 6) next
    dd$zf <- scale(dd[[f]])[,1]
    fit <- tryCatch(coxph(Surv(time, event) ~ zf, data=dd), error=function(e) NULL)
    if (!is.null(fit)) sc_out[[length(sc_out)+1]] <- data.frame(feature=f, subtype=st, n=nrow(dd),
        events=sum(dd$event), HR=exp(coef(fit)["zf"]), p=coef(summary(fit))["zf","Pr(>|z|)"])
  }
}
scr <- bind_rows(sc_out)
write.csv(scr, file.path(RES, "cbio_v5_crc_subtype_survival.csv"), row.names=FALSE)
cat("CRC subtype rows:", nrow(scr), "\n")
if (nrow(scr)) print(scr, row.names=FALSE)

# meta k>=2 counts
meta <- rd("context_meta_summary.csv")
meta$k <- as.integer(meta$k)
sig2 <- meta[meta$fdr_RE < 0.05 & meta$k >= 2, ]
cat("meta sig k>=2:", nrow(sig2), " of", sum(meta$fdr_RE<0.05), "\n")
