#!/usr/bin/env Rscript
# v12: TCGA-ESCA squamous-only survival re-analysis (17 modules + single-gene EGFR), with age/stage adjustment
suppressPackageStartupMessages({library(dplyr); library(survival)})
V12 <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
A   <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
d <- read.csv(file.path(V12,"v12_escc_squamous_module_os_input.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
clin <- read.csv(file.path(A,"cbio_v3_clinical_patient.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM") %>% filter(context=="ESCC")
wide <- clin %>% select(patient_id, clinical_attribute_id, value) %>%
  filter(clinical_attribute_id %in% c("OS_MONTHS","OS_STATUS","AGE","PATH_STAGE","CLINICAL_STAGE","AJCC_STAGING_EDITION")) %>%
  tidyr::pivot_wider(names_from=clinical_attribute_id, values_from=value, values_fn=function(x) paste(unique(x), collapse=";"))
sv <- d %>% select(patient_id, module, score) %>% tidyr::pivot_wider(names_from=module, values_from=score) %>% left_join(wide, by="patient_id")
sv$time <- suppressWarnings(as.numeric(sv$OS_MONTHS)); sv$event <- as.integer(grepl("DECEASED", sv$OS_STATUS, ignore.case=TRUE))
sv$age  <- suppressWarnings(as.numeric(sv$AGE))
stage_raw <- ifelse(!is.na(sv$PATH_STAGE) & sv$PATH_STAGE!="", sv$PATH_STAGE, sv$CLINICAL_STAGE)
st <- toupper(gsub("[^IVX]", "", stage_raw)); st[st %in% c("","NA")] <- NA
sv$stage4 <- ifelse(st %in% c("I","II","III","IV"), match(st, c("I","II","III","IV")), NA)
sv <- sv[is.finite(sv$time) & sv$time>0 & !is.na(sv$event), ]
cat("eligible patients:", nrow(sv), "| deaths:", sum(sv$event), "| with age:", sum(is.finite(sv$age)), "| with stage:", sum(is.finite(sv$stage4)), "\n")
mods <- setdiff(names(d)[d$module!=""][0:0], NULL)
features <- setdiff(names(sv), c("patient_id","OS_MONTHS","OS_STATUS","AGE","PATH_STAGE","CLINICAL_STAGE","AJCC_STAGING_EDITION","time","event","age","stage4"))
rows <- list()
for (f in features) {
  for (mdl in c("uni","age","age+stage")) {
    dd <- sv
    dd$z <- as.numeric(scale(dd[[f]]))
    if (!is.finite(sd(dd[[f]], na.rm=TRUE)) || sd(dd[[f]], na.rm=TRUE)==0) next
    form <- switch(mdl, uni=Surv(time,event)~z, age=Surv(time,event)~z+age, `age+stage`=Surv(time,event)~z+age+stage4)
    dd <- dd[stats::complete.cases(dd[, c("z","time","event", if(mdl!="uni") "age" else NULL, if(mdl=="age+stage") "stage4" else NULL)]), ]
    if (nrow(dd) < 40 || sum(dd$event) < 10) next
    fit <- tryCatch(coxph(form, data=dd), error=function(e) NULL); if (is.null(fit)) next
    s <- summary(fit)
    rows[[length(rows)+1]] <- data.frame(feature=f, model=mdl, n=nrow(dd), events=sum(dd$event),
      HR=exp(coef(fit)["z"]), ci_lo=s$conf.int["z","lower .95"], ci_hi=s$conf.int["z","upper .95"],
      p=s$coefficients["z","Pr(>|z|)"], stringsAsFactors=FALSE)
  }
}
out <- bind_rows(rows)
out$fdr <- ave(out$p, out$model, FUN=function(x) p.adjust(x, "BH"))
write.csv(out, file.path(V12,"v12_escc_squamous_survival_cox.csv"), row.names=FALSE)
cat("\n== univariable (FDR<0.10) ==\n")
print(out[out$model=="uni" & out$fdr<0.10, c("feature","n","events","HR","ci_lo","ci_hi","p","fdr")], row.names=FALSE, digits=3)
cat("\n== multivariable (FDR<0.10) ==\n")
print(out[out$model!="uni" & out$fdr<0.10, c("feature","model","n","events","HR","ci_lo","ci_hi","p","fdr")], row.names=FALSE, digits=3)
cat("\nEGFR rows:\n"); print(out[out$feature=="EGFR",], row.names=FALSE, digits=3)
cat("\nany FDR<0.05:", sum(out$fdr<0.05), "| nominal p<0.05:", sum(out$p<0.05), "\n")
