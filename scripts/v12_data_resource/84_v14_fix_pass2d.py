#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 fix pass 2d: tolerant per-item patches to the manuscript generator (writes even if some anchors are absent)."""
import os, re
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"
p=os.path.join(V14,"scripts","70_v14_manuscript.py"); s=open(p,encoding="utf-8").read()
applied=[]; skipped=[]
def rep(old,new,label,required=False):
    global s
    if old in s:
        s=s.replace(old,new,1); applied.append(label)
    else:
        (skipped if not required else skipped).append(label)
edits=[
 ("Four datasets contributed contrasts:",
  "Four single-cell datasets were processed with the same pipeline and three contributed testable contrasts:", "single-cell count"),
 ("and asthma (8 donors); one lung dataset was excluded because all cells come from tumour tissue.",
  "The asthma dataset (8 donors) produced no comparison that satisfied the donor rules after aggregation and therefore contributes no row to the shipped comparison table. One lung dataset was excluded because all cells come from tumour tissue.", "asthma note"),
 ("Pooling uses REML heterogeneity with the Hartung-Knapp variance correction, requires at least two cohorts, and is reported with k, tau-squared, I-squared, a 95% confidence interval and a 95% prediction interval;",
  "Pooling uses random-effects meta-analysis (metafor9) with REML (restricted maximum likelihood) heterogeneity and the Hartung-Knapp10,11 variance correction; pooled estimates are reported only when at least two cohorts contribute, whereas cohort-module pairs with a single contributing cohort stay in the same table labelled 'single cohort; not a pooled estimate' with no p-value, confidence interval or prediction interval. Each pooled estimate is reported with k, tau-squared, I-squared, a 95% confidence interval and a 95% prediction interval;", "pooling/k=1"),
 ("the effect is the standardized difference between case and control on the shared denominator sqrt((sd_case^2 + sd_control^2)/2): SMDH for unpaired cohorts",
  "the effect is the standardized mean difference on the shared denominator sqrt((sd_case^2 + sd_control^2)/2) with the Hedges small-sample correction J(df) = 1 - 3/(4df - 1), df = n_case + n_control - 2, giving SMDH for unpaired cohorts", "effect formula"),
 ("zero-variance modules are reported as not estimable rather than estimated.",
  "zero-variance modules are reported as not estimable rather than estimated; sampling variances follow escalc in metafor, v = 1/n_case + 1/n_control + yi^2/(2(n_case + n_control)) for SMDH, with the paired form using the number of complete pairs and the empirical correlation r.", "variance formula"),
 ("xCell v1.1.0 (expression-derived enrichment scores, not proportions)", "xCell8 v1.1.0 (expression-derived enrichment scores, not proportions)", "cite xCell"),
 ("in the bulk cohorts it is a GSVA value z-scored within the cohort", "in the bulk cohorts it is a GSVA7 value z-scored within the cohort", "cite GSVA"),
 ("Validation rules and thresholds.* Reported checks use explicit rules",
  "Abbreviations: BH (Benjamini-Hochberg), FDR (false discovery rate), VIF (variance inflation factor), MAD (median absolute deviation), OS (overall survival), GSVA (gene set variation analysis).\nValidation rules and thresholds.* Reported checks use explicit rules", "abbreviations"),
 ("An external reuse example is shipped and was executed end to end: a gastric cancer series that is not part of the resource (GSE54129; 111 tumour and 21 adjacent-normal samples) was downloaded from its accession, mapped to gene symbols, transformed by the same deterministic rule, scored with the frozen modules and compared with the pooled gastric estimates of the resource. All 17 modules were scorable, the effect direction agreed for 9 of 17 modules, and the complete path took 1.6 minutes on a desktop workstation (09_reuse_examples/example3_external_cohort_summary.txt). This is reported as an illustration of reuse cost and of the limits of cross-cohort direction agreement, not as an external validation of the resource.",
  "Three reusable examples are shipped; one of them rebuilds module scores for a gastric cohort outside the resource from its accession, and its summary file records the observed runtime and cross-cohort direction agreement as reuse-cost metrics rather than as validation.", "usage notes"),
 ("no minimum number of cells per donor was imposed;",
  "one cohort (GSE62232, hepatocellular carcinoma) contributes only five control samples; zero-variance genes are absent by construction because matrices were filtered before scoring, which is why that QC column is zero everywhere; no minimum number of cells per donor was imposed;", "limitations"),
 ("The submission package also contains the manuscript, Tables 1 and Supplementary Tables S1-S16",
  "The submission package also contains the manuscript, Tables 1 and Supplementary Tables S1-S16 as a single PDF (the same tables are also shipped here in machine-readable form; the 165-row consistency detail is deposited here rather than printed)", "supplementary pointer"),
]
for a,b,l in edits: rep(a,b,l)
s=s.replace("；","; ").replace("signalling","signaling").replace("Signalling","Signaling")
open(p,"w",encoding="utf-8").write(s)
print("applied:",len(applied)); [print("  +",x) for x in applied]
print("skipped (anchor absent):",len(skipped)); [print("  -",x) for x in skipped]
