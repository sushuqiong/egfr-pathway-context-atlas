#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 fix pass 2c: final manuscript edits with verified anchors."""
import os
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"
p=os.path.join(V14,"scripts","70_v14_manuscript.py"); s=open(p,encoding="utf-8").read()
def rep(old,new,label):
    global s
    assert old in s, f"anchor missing: {label}"
    s=s.replace(old,new,1); print("patched:",label)
# 1. single-cell wording
rep("Four datasets contributed contrasts: colorectal cancer (tumour versus non-tumour tissue, 29 donors), inflammatory bowel disease (disease versus healthy donors, 18 donors), gastric cancer (tumour versus adjacent and versus non-pathological tissue, 59 donors) and asthma (8 donors); one lung dataset was excluded because all cells come from tumour tissue.",
    "Four single-cell datasets were processed with the same pipeline and three contributed testable contrasts: colorectal cancer (tumour versus non-tumour tissue, 29 donors), inflammatory bowel disease (disease versus healthy donors, 18 donors) and gastric cancer (tumour versus adjacent and versus non-pathological tissue, 59 donors). The asthma dataset (8 donors) produced no comparison that satisfied the donor rules after aggregation and therefore contributes no row to the shipped comparison table. One lung dataset was excluded because all cells come from tumour tissue.",
    "single-cell wording")
# 2. pooling sentence: citations, k=1 rule, defined abbreviations
rep("Pooling uses REML heterogeneity with the Hartung-Knapp variance correction, requires at least two cohorts, and is reported with k, tau-squared, I-squared, a 95% confidence interval and a 95% prediction interval;",
    "Pooling uses random-effects meta-analysis (metafor9) with REML (restricted maximum likelihood) heterogeneity estimation and the Hartung-Knapp10,11 variance correction; pooled estimates are reported only when at least two cohorts contribute, whereas cohort-module pairs with a single contributing cohort remain in the same table but are labelled 'single cohort; not a pooled estimate' and carry no p-value, confidence interval or prediction interval. Each pooled estimate is reported with k (the number of contributing cohorts), tau-squared, I-squared, a 95% confidence interval and a 95% prediction interval;",
    "pooling citations and k=1 rule")
# 3. effect-size formulas and abbreviation list
rep("the effect is the standardized difference between case and control on the shared denominator sqrt((sd_case^2 + sd_control^2)/2): SMDH for unpaired cohorts and SMCRPH, the paired form using the cohort's empirical within-pair correlation r, for paired cohorts;",
    "the effect is the standardized mean difference on the shared denominator sqrt((sd_case^2 + sd_control^2)/2) with the Hedges small-sample correction J(df) = 1 - 3/(4df - 1), df = n_case + n_control - 2, giving SMDH (standardized mean difference, Hedges) for unpaired cohorts; for paired cohorts the same denominator is applied to the mean paired change with the cohort's empirical within-pair correlation r, giving SMCRPH (standardized mean change, paired, with empirical correlation). Sampling variances follow escalc in metafor (v = 1/n_case + 1/n_control + yi^2/(2(n_case + n_control)) for SMDH, with the paired form using the number of complete pairs and r);",
    "effect-size formulas")
rep("Abbreviations used below:","Abbreviations used below:") if "Abbreviations used below:" in s else None
rep("Validation rules and thresholds.* Reported checks use explicit rules",
    "Abbreviations: BH (Benjamini-Hochberg), FDR (false discovery rate), VIF (variance inflation factor), MAD (median absolute deviation), OS (overall survival), GSVA (gene set variation analysis), ROC-free layers are described below.\n*Validation rules and thresholds.* Reported checks use explicit rules",
    "abbreviation list")
# 4. GSVA and xCell citations
rep("xCell v1.1.0 (expression-derived enrichment scores, not proportions)","xCell8 v1.1.0 (expression-derived enrichment scores, not proportions)","cite xCell")
rep("in the bulk cohorts it is a GSVA value z-scored within the cohort","in the bulk cohorts it is a GSVA7 value z-scored within the cohort","cite GSVA(alt)") if "in the bulk cohorts it is a GSVA value z-scored within the cohort" in s else print("GSVA anchor variant absent (handled below)")
for cand in ["a GSVA value z-scored within the cohort","GSVA value z-scored","bulk cohorts it is"]:
    if cand in s and "GSVA7" not in s:
        s=s.replace(cand, cand.replace("GSVA","GSVA7"),1); print("patched: cite GSVA via",cand); break
# 5. Usage Notes compression
rep("An external reuse example is shipped and was executed end to end: a gastric cancer series that is not part of the resource",
    "Three reusable examples are shipped, one of which rebuilds module scores for a gastric cohort outside the resource from its accession (09_reuse_examples/example3_external_cohort_summary.txt records the observed runtime and cross-cohort direction agreement as reuse-cost metrics).",
    "usage-notes compression (prefix)")
# 6. limitations additions
rep("no minimum number of cells per donor was imposed;",
    "one cohort (GSE62232, hepatocellular carcinoma) contributes only five control samples, so its control-side variance rests on very few samples; zero-variance genes are absent by construction because matrices were filtered before scoring, which is why that QC column is zero everywhere; no minimum number of cells per donor was imposed;",
    "limitations")
# 7. supplementary pointer
rep("The submission package also contains the manuscript, Tables 1 and Supplementary Tables S1-S16",
    "The submission package also contains the manuscript, Tables 1 and Supplementary Tables S1-S16 as a single PDF (the same tables are also shipped here in machine-readable form; the 165-row consistency detail table is deposited here rather than printed)",
    "supplementary pointer")
# 8. punctuation and spelling normalisation across the generated text
s=s.replace("；","; ")
s=s.replace("signalling","signaling").replace("Signalling","Signaling")
open(p,"w",encoding="utf-8").write(s); print("generator written")
