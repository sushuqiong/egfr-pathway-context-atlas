#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os
P = r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\01_稿件正文\Manuscript_draft_v10.md"
s = open(P, encoding="utf-8").read()
# 1) fix literal \uXXXX escapes (single-backslash form)
s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1),16)), s)
# 2) compress abstract
i=s.find("## Abstract"); j=s.find("## 1. Introduction")
new_abs = """## Abstract

**Background.** Receptor-tyrosine-kinase (RTK) pathway transcriptional states are context dependent, yet how they compare across cancers and chronic benign diseases, how much bulk signal reflects tissue composition, and whether surviving signals replicate remain unclear.

**Methods.** Seventeen growth-factor pathway modules were scored in 27 public case-control cohorts spanning ten contexts, with discovery-validation separation. Effects were pooled on a common two-group scale (matched cohorts as standardized mean changes using the empirical within-pair correlation; fixed-correlation sensitivity), with REML/Hartung-Knapp and DerSimonian-Laird inference. Composition was addressed in joint models adjusting for epithelial, fibroblast, endothelial and immune scores simultaneously with disease status. Patient-level single-cell data localized surviving signals, and TCGA module-OS associations (108 tests) were assessed with age/stage sensitivity, driver stratification and external validation in independent CRC, PDAC and gastric cohorts with tissue-type and stage correction.

**Results.** Fifty-five of 170 states were per-cohort robust; conservative meta-analysis retained 7 states (20 under DerSimonian-Laird), and joint composition models retained 21 (CRC 10, STAD 9, ESCC 1, IBD 1; no PAAD state). In TCGA, 17/108 associations were FDR<0.05 and 11 of 15 testable signals survived age+stage adjustment. No module passed strict external replication: CRC VEGF/PDGF was directionally consistent (HR 1.16, p=0.042) but not significant after stage adjustment (1.09, p=0.22), three of five gastric vascular/stromal signals were directionally consistent, and no PAAD signal was reproduced.

**Conclusions.** Most bulk RTK-related transcriptional differences track tissue composition and clinical background. A minority of composition-robust states provide composition-aware, evidence-tiered hypotheses rather than evidence of pathway activation or therapeutic actionability; strict external replication remains the exception.

"""
s = s[:i] + new_abs + s[j:]
# 3) figure legends block
i=s.find("## Figure legends"); j=s.find("## Tables")
leg = """## Figure legends

**Figure 1. Analysis pipeline.** Twenty-seven case-control cohorts (ten contexts), 17 modules, and the graded evidence layers: per-cohort robustness (55/170 states); unified-scale meta-analysis (REML/Hartung-Knapp 7; DerSimonian-Laird 20); joint composition models (21 robust); single-cell localization (12 hits); TCGA prognosis (17/108); external validation (CRC GSE39582 556/187; PDAC GSE21501 102/66; ACRG 300/152). Descriptive anchors (DepMap, CPTAC) are supplementary.

**Figure 2. Module states before and after composition adjustment.** (A) Raw median standardized mean difference across ten contexts (asterisk = per-cohort-robust; digits = number of cohorts with FDR<0.05). (B) Joint models (module ~ disease + epithelial/fibroblast/endothelial/immune scores [+ matched-patient factor]); fill = median adjusted difference in SD units; digits = cohorts with joint FDR<0.05; filled diamonds = joint-composition-robust states; "n.e." = not estimable. Module labels are harmonised across panels. The two-step xCell residualization version is a sensitivity analysis (Supplementary Figure S2).

**Figure 3. Raw versus joint-model effects.** Raw median SMD against joint-model adjusted difference for all 170 states; red = joint-composition-robust; dashed line = identity. Values on the two axes use different standardizing denominators and are not an attenuation fraction (Methods 2.4).

**Figure 4. TCGA module-OS associations.** Forest plot of the 17 FDR<0.05 module-OS associations (hazard ratio per 1 SD with 95% CI), coloured by cancer context.

**Figure 5. Molecular context.** (A) EGFR/ERBB2 high-level amplification; (B) TP53/KRAS/EGFR mutation prevalence across six cancers. Both panels are generated from the same frozen result tables as the text.

**Figure 6. Single-cell source hits.** Patient-level case-control module differences by cell type reaching global BH-FDR<0.05; labels give module | cell type (number of case vs control patients); CRC is paired, IBD/STAD are unpaired.

**Supplementary Figure S1. Marker-proxy versus xCell medians.**

**Supplementary Figure S2. xCell two-step residualization heatmap (sensitivity).**

"""
s = s[:i] + leg + s[j:]
# 4) tables block
i=s.find("## Tables"); j=s.find("## Keywords")
tabs = """## Tables

**Table 1.** Context-module summary (per-cohort robust states; unified-scale meta-analysis; joint composition robustness; external OS status).

**Supplementary Table S1.** Cohort registry and origin-publication PMIDs.
**Supplementary Table S2.** Module gene membership, per-platform coverage, xCell overlap, drug-class map.
**Supplementary Table S3.** TCGA module-OS (univariable, multivariable, CNA, mutation).
**Supplementary Table S4.** Driver-module interactions and CRC subtype survival.
**Supplementary Table S5.** External validation and descriptive anchors.
**Supplementary Table S6.** Single-cell datasets and source-validation rows.
**Supplementary Table S7.** PAAD subtype calls and purity-proxy files.
**Supplementary Table S8.** Leave-one-gene-out robustness. A per-key-state recheck (10 states, 11 cohorts, 112 tests) found two cohort-level sign changes, both in small-magnitude states (CRC ERBB ligands after removing NRG1; COPD SRC/FAK after removing YES1).
**Supplementary Table S9.** Per-state evidence matrix (raw / per-cohort / unified meta / joint models / single-cell / prognosis / external), with explicit not-estimable entries.
**Supplementary Table S10.** Paired-effect verification records (per-cohort paired means, SDs, empirical correlation, standardized mean change) and reproducibility checks.

"""
s = s[:i] + tabs + s[j:]
# 5) declarations: update code statement to mention corrected pipeline + verification
s = s.replace("Analysis code (scripts for the original pipeline and for the v9 re-analyses) and processed result tables are available under an MIT licence at https://github.com/sushuqiong/egfr-pathway-context-atlas; all primary data are already public and no additional data deposit is required.",
 "Analysis code (corrected pipeline, including the paired-effect and joint-model implementations and reproducibility checks) and processed result tables are available under an MIT licence at https://github.com/sushuqiong/egfr-pathway-context-atlas; all primary data are already public and no additional data deposit is required. A corrections note describing the paired-indexing, joint-summary inclusion and external-cohort tissue/stage fixes is included with the code.")
# 6) add metafor reference at end of reference list (before nothing, append after last numbered line)
mref = "\n51. Viechtbauer W. Conducting meta-analyses in R with the metafor package. J Stat Softw. 2010;36(3):1-48. doi:10.18637/jss.v036.i03.\n"
s = s.rstrip() + mref
open(P,"w",encoding="utf-8").write(s)
print("finish edits applied")
print("abstract words:", len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1))))
print("leftover escapes:", len(re.findall(r"\\u[0-9a-fA-F]{4}", s)))
