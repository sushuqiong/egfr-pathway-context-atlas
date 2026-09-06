#!/usr/bin/env Rscript
# Driver-stratified module-OS analysis (v4): does driver background modify module prognostic effects?
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(survival)})
ROOT <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas"
RES <- file.path(ROOT, "results")
rd <- function(f) read.csv(file.path(RES, f), stringsAsFactors=FALSE, check.names=FALSE, fileEncoding="UTF-8-BOM")

mods <- setdiff(names(rd("cbio_v3_patient_module_scores.csv")), c("context","patient_id","module","score"))
# build wide module scores
ms <- rd("cbio_v3_patient_module_scores.csv")
ms_wide <- ms %>% select(context, patient_id, module, score) %>%
  pivot_wider(id_cols=c(context, patient_id), names_from=module, values_from=score)

# expression sample->patient map
expr <- rd("cbio_v3_expression_gene_sample.csv")
map_ep <- unique(expr[expr$gene=="EGFR", c("context","sample_id","patient_id")])
# patient-level EGFR z per context
expr$log2v <- log2(pmax(suppressWarnings(as.numeric(expr$value)), 0) + 1)
egfr_z <- expr %>% filter(gene=="EGFR" & is.finite(log2v)) %>% group_by(context, gene) %>%
  mutate(z=(log2v-mean(log2v))/(sd(log2v)+1e-9)) %>% ungroup() %>%
  group_by(context, patient_id) %>% summarise(EGFR=mean(z), .groups="drop")

mut <- rd("cbio_v3_mutations.csv"); cna <- rd("cbio_v3_cna_gene_sample.csv")
cna$value <- suppressWarnings(as.numeric(cna$value))
# per-patient driver states
pat_mut <- mut %>% filter(!is.na(patient_id) & nzchar(patient_id)) %>% distinct(context, patient_id, gene)
pat_mut <- pat_mut %>% filter(gene %in% c("KRAS","TP53","EGFR","CTNNB1","PIK3CA"))
cna_ep <- cna %>% filter(!is.na(patient_id) & nzchar(patient_id))
pat_amp <- cna_ep %>% filter(gene %in% c("EGFR","ERBB2","MET")) %>% group_by(context, patient_id, gene) %>%
  summarise(amp2 = any(value==2), gain = any(value>=1), .groups="drop")
# sequencing denominator: patients appearing in expression AND in mutation-bearing or cna-bearing set
seqden <- union(unique(pat_mut$patient_id), unique(cna_ep$patient_id))
drivers <- data.frame(
  context = c("PAAD","CRC","LUAD","STAD","HCC","ESCC"),
  driver = c("KRAS_mut","KRAS_mut","EGFR_mut","TP53_mut","TP53_mut","EGFR_amp"),
  stringsAsFactors=FALSE)

clin <- rd("cbio_v3_clinical_patient.csv")
clin_wide <- clin %>% select(context, patient_id, clinical_attribute_id, value) %>%
  filter(clinical_attribute_id %in% c("OS_MONTHS","OS_STATUS")) %>%
  pivot_wider(names_from=clinical_attribute_id, values_from=value, values_fn=function(x) paste(unique(x), collapse=";")) %>%
  mutate(time=suppressWarnings(as.numeric(OS_MONTHS)), event=as.integer(grepl("DECEASED", OS_STATUS, ignore.case=TRUE)))
subtype <- clin %>% filter(context=="ESCC" & clinical_attribute_id %in% c("DISEASE_TYPE","PRIMARY_DIAGNOSIS")) %>%
  distinct(patient_id) 
escc_pat <- intersect(subtype$patient_id, unique(expr$patient_id[expr$context=="ESCC"]))

rows <- list()
for (i in seq_len(nrow(drivers))) {
  ctx <- drivers$context[i]; dv <- drivers$driver[i]
  dat <- clin_wide %>% filter(context==ctx) %>% select(patient_id, time, event)
  dat <- dat[is.finite(dat$time) & dat$time>0 & !is.na(dat$event), ]
  dat <- merge(dat, ms_wide %>% filter(context==ctx) %>% select(-context), by="patient_id", all=FALSE)
  eg <- egfr_z %>% filter(context==ctx); dat$EGFR <- eg$EGFR[match(dat$patient_id, eg$patient_id)]
  # driver state
  if (grepl("_mut$", dv)) {
    g <- sub("_mut$", "", dv)
    pm <- pat_mut %>% filter(context==ctx & gene==g) %>% pull(patient_id)
    dat$driver <- as.integer(dat$patient_id %in% pm)
    dat$driver_na <- as.integer(!(dat$patient_id %in% seqden | dat$patient_id %in% pat_mut$patient_id[pat_mut$context==ctx]))
  } else if (dv == "EGFR_amp") {
    amp <- pat_amp %>% filter(context==ctx & gene=="EGFR" & amp2) %>% pull(patient_id)
    dat$driver <- as.integer(dat$patient_id %in% amp)
    dat$driver_na <- 0L
  }
  if (ctx=="ESCC") dat <- dat[dat$patient_id %in% escc_pat, ]
  dat <- dat[dat$driver_na==0L, ]
  if (sum(dat$driver) < 8 || sum(dat$driver==0) < 8) { cat("[skip small]", ctx, dv, "\n"); next }
  for (f in intersect(c("EGFR", names(ms_wide)[-(1:2)]), names(dat))) {
    if (!is.numeric(dat[[f]])) next
    keep <- is.finite(dat[[f]]) & is.finite(dat$time) & !is.na(dat$event)
    dd <- dat[keep, ]
    if (sum(dd$event) < 10) next
    dd$z <- scale(dd[[f]])[,1]
    fit <- tryCatch(coxph(Surv(time, event) ~ z + driver + z:driver, data=dd), error=function(e) NULL)
    if (is.null(fit)) next
    cs <- summary(fit)$coefficients
    # within strata
    hr_pos <- NA; hr_neg <- NA; p_pos <- NA; p_neg <- NA
    sub_pos <- dd[dd$driver==1, ]; sub_neg <- dd[dd$driver==0, ]
    if (sum(sub_pos$event) >= 8) { fp <- tryCatch(coxph(Surv(time,event)~z, data=sub_pos), error=function(e) NULL); if(!is.null(fp)){hr_pos<-exp(coef(fp)); p_pos<-coef(summary(fp))[,5]} }
    if (sum(sub_neg$event) >= 8) { fn <- tryCatch(coxph(Surv(time,event)~z, data=sub_neg), error=function(e) NULL); if(!is.null(fn)){hr_neg<-exp(coef(fn)); p_neg<-coef(summary(fn))[,5]} }
    rows[[length(rows)+1]] <- data.frame(context=ctx, driver=dv, feature=f,
      n_plus=sum(dd$driver), n_minus=sum(dd$driver==0),
      events_plus=sum(sub_pos$event), events_minus=sum(sub_neg$event),
      HR_plus=hr_pos, p_plus=p_pos, HR_minus=hr_neg, p_minus=p_neg,
      HR_interaction=exp(coef(fit)["z:driver"]), p_interaction=cs["z:driver","Pr(>|z|)"])
  }
  cat("[done]", ctx, dv, " rows:", length(rows), "\n")
}
out <- bind_rows(rows)
if (nrow(out)) {
  out$fdr_interaction <- p.adjust(out$p_interaction, "BH")
  write.csv(out, file.path(RES, "cbio_v4_driver_module_interactions.csv"), row.names=FALSE)
  sig <- out[out$fdr_interaction < 0.05, ]
  cat("interaction rows:", nrow(out), " FDR<0.05:", nrow(sig), "\n")
  for (r in head(sig, 12)) cat(sprintf("  %s %s x %s: HR=%.2f p=%.4g fdr=%.3f (n+/n-=%d/%d)\n",
      r$context, r$driver, r$feature, r$HR_interaction, r$p_interaction, r$fdr_interaction, r$n_plus, r$n_minus))
} else cat("no rows\n")
