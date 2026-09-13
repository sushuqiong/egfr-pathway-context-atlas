#!/usr/bin/env Rscript
# v11 driver-stratified module-OS re-analysis with corrected sample eligibility (GPT6 item 6)
# Rule: mutation drivers -> patients must be mutation-profiled (cBioPortal <study>_sequenced sample list)
#       driver-negative = profiled but no mutation record for that gene (explicit wild type)
#       non-profiled patients are excluded from the driver model (counted).
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(survival)})
ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"; RES <- file.path(ROOT,"results")
V11 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v11/reruns/results"
rd <- function(f) read.csv(file.path(RES,f), stringsAsFactors=FALSE, check.names=FALSE, fileEncoding="UTF-8-BOM")
ms <- rd("cbio_v3_patient_module_scores.csv")
ms_wide <- ms %>% select(context, patient_id, module, score) %>% pivot_wider(id_cols=c(context,patient_id), names_from=module, values_from=score)
clin <- rd("cbio_v3_clinical_patient.csv")
clin_wide <- clin %>% select(context, patient_id, clinical_attribute_id, value) %>%
  filter(clinical_attribute_id %in% c("OS_MONTHS","OS_STATUS")) %>%
  pivot_wider(names_from=clinical_attribute_id, values_from=value, values_fn=function(x) paste(unique(x), collapse=";")) %>%
  mutate(time=suppressWarnings(as.numeric(OS_MONTHS)), event=as.integer(grepl("DECEASED", OS_STATUS, ignore.case=TRUE)))
mut <- rd("cbio_v3_mutations.csv"); cna <- rd("cbio_v3_cna_gene_sample.csv"); cna$value <- suppressWarnings(as.numeric(cna$value))
prof <- read.csv(file.path(V11,"v11_mut_profiled_samples.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
map_sp <- rd("cbio_v3_expression_gene_sample.csv") %>% filter(gene=="EGFR") %>% distinct(context, sample_id, patient_id)
# profiled patients per context (mutation-profiled samples -> patients)
prof_pat <- merge(prof, map_sp, by=c("context","sample_id")) %>% distinct(context, patient_id)
cna_pat  <- cna %>% filter(!is.na(patient_id), nzchar(patient_id)) %>% distinct(context, patient_id)
pat_mut  <- mut %>% filter(!is.na(patient_id), nzchar(patient_id)) %>% distinct(context, patient_id, gene)
pat_amp  <- cna %>% filter(!is.na(patient_id), gene %in% c("EGFR","ERBB2","MET")) %>% group_by(context, patient_id, gene) %>%
  summarise(amp2=any(value==2), .groups="drop")
drivers <- data.frame(context=c("PAAD","CRC","LUAD","STAD","HCC","ESCC"),
                      driver =c("KRAS_mut","KRAS_mut","EGFR_mut","TP53_mut","TP53_mut","EGFR_amp"), stringsAsFactors=FALSE)
rows <- list(); elig <- list()
for (i in seq_len(nrow(drivers))) {
  ctx <- drivers$context[i]; dv <- drivers$driver[i]
  dat <- clin_wide %>% filter(context==ctx) %>% select(patient_id, time, event)
  dat <- dat[is.finite(dat$time) & dat$time>0 & !is.na(dat$event), ]
  dat <- merge(dat, ms_wide %>% filter(context==ctx) %>% select(-context), by="patient_id")
  if (grepl("_mut$", dv)) {
    g <- sub("_mut$", "", dv)
    pooled <- prof_pat %>% filter(context==ctx)
    dat <- merge(dat, pooled %>% mutate(profiled=1L), by="patient_id", all.x=TRUE)
    dat$profiled[is.na(dat$profiled)] <- 0L
    pos <- pat_mut %>% filter(context==ctx, gene==g) %>% pull(patient_id)
    dat$driver <- as.integer(dat$patient_id %in% pos)
    n_excl <- sum(dat$profiled==0); dat <- dat[dat$profiled==1,]
    driver_label <- paste0(g, " mutation (profiled-only)")
  } else {
    g <- sub("_amp$", "", dv)
    pooled <- cna_pat %>% filter(context==ctx)
    dat <- merge(dat, pooled %>% mutate(profiled=1L), by="patient_id", all.x=TRUE)
    dat$profiled[is.na(dat$profiled)] <- 0L
    pos <- pat_amp %>% filter(context==ctx, gene==g, amp2) %>% pull(patient_id)
    dat$driver <- as.integer(dat$patient_id %in% pos); n_excl <- sum(dat$profiled==0); dat <- dat[dat$profiled==1,]
    driver_label <- paste0(g, " amplification (CNA-profiled-only)")
  }
  n_plus <- sum(dat$driver==1); n_minus <- sum(dat$driver==0)
  elig[[length(elig)+1]] <- data.frame(context=ctx, driver=dv, label=driver_label, n_analysed=nrow(dat),
      n_driver_positive=n_plus, n_driver_negative_wildtype=n_minus, n_excluded_not_profiled=n_excl)
  mods <- setdiff(names(ms_wide), c("context","patient_id"))
  for (m in mods) {
    d <- dat[is.finite(dat[[m]]),]
    if (nrow(d)<40 || sum(d$event)<10 || length(unique(d$driver))<2) next
    d$z <- scale(d[[m]])[,1]
    fit <- tryCatch(coxph(Surv(time,event) ~ z*driver, data=d), error=function(e) NULL); if(is.null(fit)) next
    cs <- coef(summary(fit)); if(!("z:driver" %in% rownames(cs))) next
    rows[[length(rows)+1]] <- data.frame(context=ctx, driver=dv, feature=m, n=nrow(d), events=sum(d$event),
      n_plus=n_plus, n_minus=n_minus,
      HR_module=exp(cs["z","coef"]), p_module=cs["z","Pr(>|z|)"],
      HR_interaction=exp(cs["z:driver","coef"]), p_interaction=cs["z:driver","Pr(>|z|)"], stringsAsFactors=FALSE)
  }
}
out <- bind_rows(rows); out$fdr_interaction <- p.adjust(out$p_interaction, "BH")
write.csv(out, file.path(V11,"v11_driver_interactions.csv"), row.names=FALSE)
write.csv(bind_rows(elig), file.path(V11,"v11_driver_eligibility.csv"), row.names=FALSE)
cat("== eligibility (profiled-only rule) ==\n"); print(bind_rows(elig), row.names=FALSE)
cat("\ninteraction tests:", nrow(out), "| nominal p<0.05:", sum(out$p_interaction<0.05), "| BH-FDR<0.05:", sum(out$fdr_interaction<0.05), "\n")
print(out[out$p_interaction<0.05, c("context","driver","feature","n","events","HR_interaction","p_interaction","fdr_interaction")], row.names=FALSE, digits=3)
