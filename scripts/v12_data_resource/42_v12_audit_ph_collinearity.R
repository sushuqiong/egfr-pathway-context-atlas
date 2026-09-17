#!/usr/bin/env Rscript
# v12 audit B: proportional-hazards assumption for the TCGA survival layer, and collinearity diagnostics
# for the composition models (disease status vs the four compartment scores).
suppressPackageStartupMessages({library(dplyr); library(tidyr); library(survival)})
R <- "C:/Users/fengq/Desktop/EGFR/EGFR的v12/results"
A <- "C:/Users/fengq/Desktop/EGFR/EGFR_pathway_context_atlas/results"
## ---- 1. PH assumption: squamous oesophageal subset ----
d <- read.csv(file.path(R,"v12_escc_squamous_module_os_input.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM")
clin <- read.csv(file.path(A,"cbio_v3_clinical_patient.csv"), stringsAsFactors=FALSE, fileEncoding="UTF-8-BOM") %>% filter(context=="ESCC")
w <- clin %>% select(patient_id, clinical_attribute_id, value) %>%
  filter(clinical_attribute_id %in% c("OS_MONTHS","OS_STATUS","AGE")) %>%
  pivot_wider(names_from=clinical_attribute_id, values_from=value, values_fn=function(x) paste(unique(x), collapse=";"))
sv <- d %>% select(patient_id, module, score) %>% pivot_wider(names_from=module, values_from=score) %>% left_join(w, by="patient_id")
sv$time <- suppressWarnings(as.numeric(sv$OS_MONTHS)); sv$event <- as.integer(grepl("DECEASED", sv$OS_STATUS, ignore.case=TRUE))
sv$age <- suppressWarnings(as.numeric(sv$AGE)); sv <- sv[is.finite(sv$time) & sv$time>0 & !is.na(sv$event),]
feats <- setdiff(names(sv), c("patient_id","OS_MONTHS","OS_STATUS","AGE","time","event","age"))
ph <- list()
for (f in feats) {
  dd <- sv; dd$z <- as.numeric(scale(dd[[f]]))
  fit <- tryCatch(coxph(Surv(time,event) ~ z + age, data=dd), error=function(e) NULL); if (is.null(fit)) next
  zph <- tryCatch(cox.zph(fit), error=function(e) NULL); if (is.null(zph)) next
  ph[[length(ph)+1]] <- data.frame(feature=f, n=nrow(dd), events=sum(dd$event),
    ph_p_z=zph$table["z","p"], ph_p_global=zph$table["GLOBAL","p"], stringsAsFactors=FALSE)
}
phdf <- bind_rows(ph); phdf$ph_violation <- phdf$ph_p_z < 0.05
write.csv(phdf, file.path(R,"v12_qc_cox_ph_assumption.csv"), row.names=FALSE)
cat("PH tests:", nrow(phdf), "| features violating PH at p<0.05:", sum(phdf$ph_violation), "\n")
ord <- order(phdf$ph_p_z)[seq_len(min(5, nrow(phdf)))]
print(phdf[ord, ], row.names=FALSE, digits=3)
## ---- 2. collinearity: disease status vs composition compartments ----
comp_files <- c(file.path(A,"xcell","xcell_composition_scores.csv"), file.path(A,"xcell_composition_scores.csv"))
cf <- comp_files[file.exists(comp_files)][1]
out <- NULL
if (!is.na(cf)) {
  x <- read.csv(cf, stringsAsFactors=FALSE)
  grpcol <- intersect(c("group","case_control","group_label"), names(x))[1]
  diag <- list()
  for (acc in unique(x$accession)) {
    s <- x[x$accession==acc, ]
    need <- c("epi","fib","end","imm", grpcol)
    if (!all(need %in% names(s))) next
    s$case <- as.integer(tolower(as.character(s[[grpcol]])) %in% c("case","tumour","tumor","1","yes"))
    dd <- s[, c("case","epi","fib","end","imm")]; dd <- dd[complete.cases(dd),]
    if (nrow(dd) < 12 || length(unique(dd$case)) < 2) next
    m <- lm(case ~ epi + fib + end + imm, data=dd)
    r2 <- summary(m)$r.squared
    vif <- tryCatch({ v <- diag(solve(cor(dd[,c("epi","fib","end","imm")]))); max(v) }, error=function(e) NA_real_)
    diag[[length(diag)+1]] <- data.frame(accession=acc, n=nrow(dd), r2_disease_on_composition=r2, max_vif=max(vif), stringsAsFactors=FALSE)
  }
  out <- bind_rows(diag)
  write.csv(out, file.path(R,"v12_qc_composition_collinearity.csv"), row.names=FALSE)
  cat("\ncomposition collinearity: cohorts=", nrow(out),
      "| median R2(disease~composition)=", round(median(out$r2_disease_on_composition, na.rm=TRUE),3),
      "| max R2=", round(max(out$r2_disease_on_composition, na.rm=TRUE),3),
      "| median max-VIF=", round(median(out$max_vif, na.rm=TRUE),2), "\n")
} else cat("\n[WARN] composition score file not found\n")
