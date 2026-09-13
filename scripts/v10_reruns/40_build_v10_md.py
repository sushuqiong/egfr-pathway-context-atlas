#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build Manuscript_draft_v10.md from v9 by section-level replacement with corrected v10 numbers."""
import re, os
SRC = r"C:\Users\fengq\Desktop\EGFR\EGFR的v9\01_稿件正文\Manuscript_draft_v09.md"
DST = r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\01_稿件正文\Manuscript_draft_v10.md"
os.makedirs(os.path.dirname(DST), exist_ok=True)
s = open(SRC, encoding="utf-8").read()

def replace_section(s, start, end, new):
    i = s.find(start); j = s.find(end)
    assert i >= 0 and j > i, (start, end)
    return s[:i] + new + s[j:]

# ---------------- Abstract ----------------
abs_new = """## Abstract

**Background.** Receptor-tyrosine-kinase (RTK) pathway transcriptional states are context dependent, yet how they compare across cancers and chronic benign diseases, how much of bulk tissue signal reflects cellular composition, and whether surviving signals carry reproducible prognostic value remain unclear.

**Methods.** Seventeen growth-factor pathway modules were scored in 27 public case-control cohorts spanning ten contexts (six cancers, four chronic diseases) with discovery-validation separation and per-cohort BH-FDR. Standardized effects were pooled by within-context random-effects meta-analysis on a common two-group scale (matched cohorts analysed as standardized mean changes using the empirical within-pair correlation; sensitivity at fixed correlations 0.5 and 0.7), with REML/Hartung-Knapp and DerSimonian-Laird inference. Composition was addressed in joint models that adjust for epithelial, fibroblast, endothelial and immune scores simultaneously with disease status (plus a matched-patient factor), with two-step xCell residualization retained as a sensitivity. Patient-level single-cell data localized surviving signals. TCGA module-overall-survival associations (108 tests; per-context FDR families) were assessed with age/stage sensitivity, a driver-stratified effect-modification screen, and external validation in independent CRC (GSE39582), PDAC (GSE21501) and gastric (ACRG/GSE62254) cohorts with explicit tissue-type filtering and stage adjustment.

**Results.** Fifty-five of 170 states were per-cohort robust. After effect-size unification, conservative REML/Hartung-Knapp meta-analysis retained 7 states (20 under DerSimonian-Laird; predominantly IBD), and joint composition models retained 21 states (CRC 10, STAD 9, ESCC 1, IBD 1); no PAAD state was composition-robust. In TCGA, 17/108 module-OS associations were FDR<0.05 and 11 of 15 testable signals survived age+stage adjustment. In external cohorts no module passed strict replication criteria: the CRC VEGF/PDGF signal was directionally consistent (HR 1.16, p=0.042) but not significant after stage adjustment (HR 1.09, p=0.22), CRC FGFR and IGF/INSR were nominally adverse, three of five STAD vascular/stromal signals were directionally consistent in ACRG, and none of seven PAAD signals was reproduced.

**Conclusions.** Most bulk RTK-related transcriptional differences track tissue composition and clinical background. A minority of composition-robust, cell-source-localized states provide composition-aware, evidence-tiered hypotheses rather than direct evidence of pathway activation or therapeutic actionability, and strict external replication remains the exception rather than the rule.

"""
s = replace_section(s, "## Abstract", "## 1. Introduction", abs_new)

# ---------------- Methods 2.3 ----------------
m23 = """### 2.3 Bulk scoring, differential testing and meta-analysis
Per cohort, probes were mapped to genes using unambiguous symbols (multi-probe mean; platform annotation from GEO or parsed gene_assignment/GENE_SYMBOL where annotated tables were absent), auto-log2 transformed where needed, and scored by GSVA (Gaussian kernel, minSize \\u2265 3) [44]. In representative cohorts spanning both microarray platforms, GSVA scores and member-mean z-scores were highly concordant within cohorts (median Spearman \\u03c1 = 0.94; range 0.72-0.98). Differential testing used limma eBayes (trend + robust) [45] with a matched-pair patient factor for the twelve matched cohorts or covariate designs otherwise. Per-cohort BH-FDR was applied. For meta-analysis, effects were expressed on a common two-group scale using metafor [51]: Hedges' g (measure SMD) for unpaired cohorts, and the standardized mean change (measure SMCRH, using the empirical within-pair correlation ri estimated from the matched module scores) for matched cohorts. Cohort-level effects were pooled by within-context random-effects meta-analysis; the primary inference used REML estimation of the between-study variance with the Hartung-Knapp adjustment, and DerSimonian-Laird pooling is reported for comparison. Sensitivity analyses re-estimated paired effects at fixed ri = 0.5 and 0.7. Heterogeneity is reported as I\\u00b2 and \\u03c4\\u00b2 and per-disease BH-FDR was applied to pooled p-values. Single-cohort (k=1) estimates are reported but not treated as meta evidence.

"""
s = replace_section(s, "### 2.3 Bulk scoring", "### 2.4 Composition adjustment", m23)

# ---------------- Methods 2.4 ----------------
m24 = """### 2.4 Composition adjustment
Tissue composition was estimated by xCell v1.1.0 [47] (64 immune/stromal cell types plus ImmuneScore); xCell outputs are expression-derived enrichment scores and are not measured cell proportions. Four compartment scores were used (Epithelial cells, Fibroblasts, Endothelial cells, ImmuneScore). Composition was addressed in joint linear models that adjust for composition simultaneously with disease status (module score ~ disease status + the four compartment scores, plus a matched-patient factor in the twelve paired cohorts); the disease coefficient used an explicitly defined control reference level, per-cohort FDR was derived across modules, and standardized adjusted differences were computed as the coefficient divided by the model residual SD. To make adjusted and unadjusted magnitudes comparable, the unadjusted disease coefficient was also extracted from the same model (identical residual SD) rather than from a separately standardized analysis; we do not interpret differences between separately standardized estimates as "how much signal composition explained". Two-step xCell residualization was retained only as a sensitivity because it can over- or under-correct when disease and composition are correlated. Composition scores and expression matrices were joined explicitly by sample ID. A marker-proxy sensitivity version (epithelial/immune/stromal/endothelial marker means) was compared by Spearman correlation across the 170 adjusted medians (\\u03c1 = 0.81). Concordance with EPIC was assessed across all 27 cohorts (sample-level Spearman vs xCell: endothelial \\u03c1 = 0.56, immune 0.44, fibroblast/CAF 0.28, epithelial/cancer 0.09); EPIC requires non-log linear expression input and its uncharacterised-cell compartment is not equivalent to the xCell epithelial score, so this is reported as a limitation rather than cross-tool validation. Composition adjustment is interpreted as evidence of composition-coupling, not as proof of cell-intrinsic absence, because tissue architecture itself can be part of disease biology (Discussion).

"""
s = replace_section(s, "### 2.4 Composition adjustment", "### 2.5 Single-cell", m24)

# ---------------- Methods 2.9 (softer) ----------------
m29 = """### 2.9 PAAD molecular subtype and purity sensitivity
TCGA-PAAD samples (179 with RNA-seq) were classified into basal-like versus classical tumours by a factor-loading nearest-centroid rule derived from the Moffitt basal-like/classical factorization [49] of the pancreatic cancer molecular subtypes [50] (top-150 positively loaded genes per program). Per-sample z-scores were averaged over each program's genes and the higher score assigned the subtype; 178 of 179 classified samples had survival data. This is a derived classifier variant and was not independently validated against the original subtype calls, so subtype analyses are exploratory. Module-OS Cox models were re-fit within subtype strata and with subtype interactions; the absence of significant interactions in this dataset is not interpreted as evidence against subtype-specific biology (Discussion 4.8). A marker-based purity sensitivity used an expression-derived immune/stromal content score as an approximate purity proxy (proxy = \\u2212(immune + stromal z-scores)); this proxy is not a measured purity estimate.

"""
s = replace_section(s, "### 2.9 PAAD molecular subtype", "### 2.10 Descriptive anchors", m29)

# ---------------- Results 3.1 ----------------
r31 = """### 3.1 Atlas overview, unified-scale meta-analysis [Fig 1, Fig 2; Table 1]
Across 170 context-module summaries, 55 states were per-cohort robust (LUAD 14, CRC 11, STAD 10, PAAD 10, ESCC 4, IBD 6; none in HCC, COPD, NAFLD or asthma by the per-cohort rule). The per-cohort rule remains the pre-specified primary readout. For meta-analysis, effects were first expressed on a common two-group scale (Hedges' g for unpaired cohorts; standardized mean change with empirically estimated within-pair correlation for matched cohorts; all 200 paired records were estimable, median ri = 0.99, and fixed-correlation sensitivity analyses at 0.5 and 0.7 gave identical pooled results). DerSimonian-Laird pooling identified 20 pooled-significant states (k \\u2265 2; IBD 11, COPD 5, asthma 4), whereas the conservative REML/Hartung-Knapp inference retained 7 (IBD ERBB receptors \\u22121.28, IBD HGF/MET +1.52, IBD JAK-STAT +1.78, IBD SRC/FAK +0.45, IBD TIE/Ang +1.14, IBD VEGF/PDGF +1.30, COPD SRC/FAK \\u22120.28). No CRC, LUAD, STAD or PAAD state survived the conservative meta-analysis. NAFLD remained null at every level within the power of the available cohorts.

"""
s = replace_section(s, "### 3.1 Atlas overview", "### 3.2 Cancer architectures", r31)

# ---------------- Results 3.2 ----------------
r32 = """### 3.2 Cancer architectures [Fig 2; Table 1]
Three patterns emerged. **Receptor-loss cancers (CRC, LUAD).** CRC lesions lost RTK receptors and ligands relative to normal colon at the raw level (FGFR, IGF/INSR, ERBB ligands, PDGFR-KIT) while upregulating WNT/\\u03b2-catenin and EPH receptors; after joint composition adjustment, CRC retained the largest composition-robust set of any cancer (10 states: WNT/\\u03b2-catenin +2.52, EPH +1.57, VEGF/PDGF +1.67 and HGF/MET +1.01 up; FGFR \\u22121.89, IGF/INSR \\u22120.90, ERBB ligands \\u22120.71, RET/ALK/NTRK \\u22120.81 down; JAK-STAT and TAM/AXL up), indicating that these signals are not simply explained by the stromal/immune content of colorectal tumours. LUAD was per-cohort robust for 14 states but no LUAD state was composition-robust in joint models, so its apparent architecture is composition- or cohort-dependent in this design. **Coordinated upregulation (STAD, PAAD).** STAD had 9 joint-robust states (EPH +1.90, JAK-STAT +1.12, RAS-MAPK +1.06, WNT +0.88, HGF/MET +0.72, PI3K-AKT +0.60 and VEGF/PDGF +0.65 up; ERBB receptors \\u22120.80 and RET/ALK/NTRK \\u22121.11 down), whereas PAAD's broad raw upregulation (10 per-cohort-robust modules) was entirely attenuated by joint composition adjustment — no PAAD state was composition-robust. **ESCC** contributed a single joint-robust state (VEGF/PDGF up) and retained its SRC/FAK/VEGF/IGF raw pattern.

"""
s = replace_section(s, "### 3.2 Cancer architectures", "### 3.3 Benign contexts", r32)

# ---------------- Results 3.3 ----------------
r33 = """### 3.3 Benign contexts [Fig 2; Table 1]
IBD was the only benign context with strong, reproducible transcriptional upregulation and it dominated the conservative meta-analysis (six of the seven REML/Hartung-Knapp states: JAK-STAT +1.78, HGF/MET +1.52, VEGF/PDGF +1.30, TIE/Ang +1.14, SRC/FAK +0.45 and ERBB-receptor downregulation \\u22121.28). Of these, only JAK-STAT was also composition-robust in joint models, localizing the defensible IBD signal to a composition-independent JAK-STAT state that single-cell data attribute to colonic epithelium and myeloid cells (Results 3.5). Asthma and COPD produced only DerSimonian-Laird-level signals (asthma four states; COPD five states including SRC/FAK downregulation, which was the single non-IBD conservative meta-analysis signal); none of the asthma states survived conservative meta-analysis or joint adjustment, and COPD signals were of small magnitude. No module difference was found for NAFLD in the available cohorts.

"""
s = replace_section(s, "### 3.3 Benign contexts", "### 3.4 Composition adjustment", r33)

# ---------------- Results 3.4 ----------------
r34 = """### 3.4 Composition adjustment [Fig 3; Table 1; Table S9]
In joint models adjusting for composition simultaneously with disease status, 21 of 170 states were composition-robust (CRC 10, STAD 9, ESCC 1, IBD 1); the remaining states were estimated but not significant (95) or estimated without meeting the robustness rule (54), and none was unanalysable. All PAAD states were attenuated to non-significance, indicating that PAAD bulk module differences are strongly composition-associated. Two-step xCell residualization, retained only as a sensitivity, classified 19 states as robust, of which only a minority (5) overlapped the joint-model set: residualization and joint adjustment answer different questions, and the joint models are reported as primary because they avoid removing disease-correlated composition before testing disease. Because raw effects are standardized by group SD and adjusted effects by model residual SD, we report adjusted and unadjusted coefficients from the same model rather than interpreting the numerical difference between separately standardized estimates as an attenuation fraction; the full per-state evidence matrix (Table S9) lists, for each state, the raw effect, per-cohort robustness, unified-scale meta-analysis, joint-model estimate, single-cell support, and prognostic/external results, with explicit "not estimable" labels.

"""
s = replace_section(s, "### 3.4 Composition adjustment", "### 3.5 Single-cell localization", r34)

# ---------------- Results 3.6 external (rewritten) ----------------
i = s.find("### 3.6 Prognosis and external validation"); j = s.find("### 3.7 ")
assert i>0 and j>i
r36_head = s[i:j]
# keep first paragraph (TCGA numbers unchanged) up to 'External validation was deliberately divergent'
k = r36_head.find("External validation was deliberately divergent")
assert k>0
new_ext = """External validation was reassessed after correcting cohort composition and stage handling, and is reported against pre-specified criteria (direction, nominal significance, and stage-adjusted significance). In GSE39582, the public series contains 585 arrays of which 566 are tumour and 19 adjacent non-tumour; after excluding non-tumour samples and arrays without outcome annotation, 556 tumour samples with 187 deaths were analysed (stage 1-4 in 552; four stage-0 samples excluded from stage-adjusted models). Under these corrected criteria, the previously reported CRC VEGF/PDGF replication is not robust: HR 1.16 (95% CI 1.00-1.34, p=0.042) unadjusted and 1.15 (1.00-1.33, p=0.049) after age adjustment, but 1.09 (0.95-1.26, p=0.22) after age+stage adjustment, with BH-FDR 0.14-0.46 across the tested CRC modules. CRC FGFR (1.15, p=0.048) and IGF/INSR (1.16, p=0.045) were nominally adverse after age+stage adjustment without FDR significance; ERBB ligands, WNT/\\u03b2-catenin, PDGFR-KIT and EPH were null. In PDAC (GSE21501; 102 patients, 66 deaths), none of the seven TCGA-adverse PAAD module-OS associations was reproduced. In gastric cancer (ACRG/GSE62254; 300 tumours, 152 deaths), three of five TCGA-adverse vascular/stromal modules were directionally consistent (TIE/Ang, PDGFR-KIT and VEGF/PDGF) but none met an FDR criterion. We therefore report that no module state passed strict external replication in this study; the consistent direction of the CRC VEGF/PDGF and ACRG vascular/stromal signals, and the nominal adverse CRC FGFR/IGF signals, are hypothesis-generating only.
"""
s = s[:i] + r36_head[:k] + new_ext + "\n\n" + s[j:]

# ---------------- Results 3.8 subtype (softer) ----------------
r38 = """### 3.8 PAAD molecular subtype and purity sensitivity
In TCGA-PAAD, 179 samples were classified by the Moffitt-derived factor-loading rule (81 basal-like, 98 classical), of which 178 had survival data; overall survival did not differ between subtypes (HR 0.81, p=0.30). No module-by-subtype interaction was significant, and no PDAC module-OS association was reproduced in the independent cohort. Tumour-purity adjustment used an approximate expression-derived proxy: the TCGA-adverse PAAD associations were not materially attenuated, but because the proxy is not a measured purity estimate and because external replication failed, these signals remain TCGA-specific observations. Because the classifier is a derived variant that was not validated against the original subtype calls, and the interaction analyses were underpowered, we do not claim that these signals are independent of molecular subtype; we report only that no subtype-specific modification was detected in this dataset.

"""
s = replace_section(s, "### 3.8 PAAD molecular subtype", "### 3.9 Descriptive anchors", r38)

# ---------------- Discussion 4.1 ----------------
d41 = """### 4.1 Principal findings
We assembled a transcriptional atlas of growth-factor pathway modules across six cancers and four chronic benign diseases and subjected every candidate signal to cross-cohort, composition, single-cell and prognostic filters. The disciplined outcome is a graded evidence structure rather than a shortlist: 55 of 170 states were per-cohort robust, 7 survived conservative unified-scale meta-analysis (dominated by IBD), 21 were composition-robust in joint models (dominated by CRC and STAD), and no state passed strict external replication. This is best framed as a composition-aware hypothesis generator, with an explicit per-state evidence matrix (Table S9) that separates states that were not analysed, could not be estimated, were estimated without significance, and met robustness criteria.

"""
s = replace_section(s, "### 4.1 Principal findings", "### 4.2 Composition dominates", d41)

# ---------------- Discussion 4.2 (remove strong causal wording) ----------------
d42 = """### 4.2 Composition shapes bulk inference
Previous pan-cancer pathway analyses scored oncogenic-signalling states within tumour-only cohorts without benign comparators or composition adjudication [11]. Our contribution is to quantify how much of a case-control module difference is attributable to tissue composition and clinical background, using joint models that keep disease and composition in the same regression. In these models PAAD bulk differences were fully attenuated and IBD signals were largely attenuated, whereas a subset of CRC and STAD states remained robust - a pattern consistent with composition-coupling rather than proof that cellular composition "drives" the signal. Several distinct situations produce attenuation and should not be conflated: a genuinely smaller disease coefficient; a similar coefficient with larger standard error; strong disease-composition correlation that leaves the model unable to separate the two; expression information shared between module genes and composition markers; and removal of a component of the disease mechanism itself. Module and composition scores are both derived from the same expression matrix and are therefore not independent measurements, and xCell reports enrichment scores rather than cell proportions; we therefore avoid the term pathway activation and do not interpret compositional attenuation as a mechanism.

"""
s = replace_section(s, "### 4.2 Composition dominates", "### 4.3 Surviving composition-robust", d42)

# ---------------- Discussion 4.3 ----------------
d43 = """### 4.3 Surviving composition-robust signals and their cellular sources
The joint-model-robust set (21 states) was concentrated in CRC (10 states: WNT/\\u03b2-catenin, EPH, VEGF/PDGF and HGF/MET up; FGFR, IGF/INSR, ERBB ligands and RET/ALK/NTRK down; JAK-STAT and TAM/AXL up) and STAD (9 states), with single states in ESCC (VEGF/PDGF) and IBD (JAK-STAT). Single-cell data provide localization support for a subset: CRC WNT/EPH and VEGF/PDGF differences were higher in malignant cells relative to paired normal colonocytes (colonocyte marker-based annotations, with the patient as the statistical unit), and IBD JAK-STAT was higher in colonic epithelium and myeloid cells. Localization support is transcript-level and, except for the paired CRC dataset, unpaired, and does not establish function.

"""
s = replace_section(s, "### 4.3 Surviving composition-robust", "### 4.4 PAAD:", d43)

# ---------------- Discussion 4.4 ----------------
d44 = """### 4.4 PAAD: composition-coupling, not tumour-cell-intrinsic activation
PAAD shows the broadest bulk module upregulation, but joint composition adjustment attenuated every PAAD state, and no PAAD state met the composition-robust rule. In a desmoplastic tumour with a large stromal fraction this is expected, and it carries a practical message: pathway scores in stroma-rich tumours should be composition-normalised before claims of epithelial-intrinsic expression. We do not claim that PAAD tumour cells lack these transcripts: composition scores are expression-derived, tissue architecture can be part of disease mechanism, and adjusting for composition may remove part of the disease signal itself. The accurate statement is that PAAD bulk module differences were strongly composition-associated and were attenuated after joint composition adjustment. The adverse-OS signal of module expression in TCGA was not reproduced in an independent PDAC cohort, and although it was not attenuated by an approximate marker-based purity proxy, it remains a TCGA-specific observation.

"""
s = replace_section(s, "### 4.4 PAAD:", "### 4.5 External validation", d44)

# ---------------- Discussion 4.5 ----------------
d45 = """### 4.5 External validation as the discipline, and its limits
After correcting tissue-type filtering, stage parsing and pairing in the external analyses, the external-validation contrast became more sober than in earlier versions of this work: no module state passed strict replication. The CRC VEGF/PDGF signal was directionally consistent but its significance did not survive stage adjustment (HR 1.09, p=0.22), and CRC FGFR and IGF/INSR were nominally adverse after age+stage adjustment; the CRC ERBB-ligand protective direction remained absent; three of five ACRG gastric vascular/stromal signals were directionally consistent without FDR significance; and all seven PAAD signals failed. External non-significance is reported as failure to replicate, not as absence of effect, and the analyses differed in outcome definitions, treatment background and stage distribution. We nonetheless regard this fully transparent accounting - including the withdrawal of an earlier "replicated" claim - as the central methodological contribution: transcriptomic module scores should not be treated as targetable biology without cohort-level replication that survives clinical adjustment.

"""
s = replace_section(s, "### 4.5 External validation", "### 4.6 ESCC", d45)

# ---------------- Discussion 4.7 (screen wording) ----------------
d47 = """### 4.7 Driver-stratified effect modification as an underpowered screen
None of the 108 module \\u00d7 driver interactions survived FDR. With several strata containing few events, this screen cannot distinguish true absence of effect modification from insufficient power, and we therefore make no claim that module-OS associations are stable across driver backgrounds.

"""

# ---------------- Discussion 4.8 limitations ----------------
d48 = """### 4.8 Limitations
Transcriptional proxies: module scores are expression states, not measures of protein phosphorylation or pathway function, and modules mix receptors, ligands and downstream effectors, so a mean score does not have a single biological meaning; module membership and per-platform coverage are reported in Supplementary Table S2. Composition: xCell reports enrichment scores, not proportions; disease and composition are correlated so joint models may not separate them; two-step residualization can over- or under-correct and classified a different, only partly overlapping set of states; EPIC agreed only moderately with xCell and its uncharacterised compartment is not equivalent to xCell epithelial scores. Effect sizes: paired cohorts were analysed as standardized mean changes using an empirical within-pair correlation (median 0.99), which assumes a common correlation across cohorts; fixed-correlation sensitivity analyses gave identical pooled results but the assumption remains. Adjusted and unadjusted effects use different standardizing denominators, so attenuation magnitudes are reported from the same model rather than as fractions removed. External validation: after tissue-type and stage correction no state passed strict replication, stage was unavailable for some TCGA-PAAD analyses, and treatment background is not captured in public cohorts. Prognosis: survival associations were primarily univariable; 11 of 15 testable signals survived age+stage adjustment; interaction and subtype analyses were underpowered and the PAAD subtype classifier was a derived variant that was not validated against the original calls. Single-cell: localization is transcript-level, unpaired for IBD/STAD, and does not test function. Meta-analysis: k is small in several contexts (I\\u00b2 unstable); NAFLD null results reflect available cohorts and are not equivalence evidence; descriptive anchor layers (DepMap, CPTAC, drug map) are hypothesis-generating only. Analysis revisions: a paired-indexing error (matched cohorts dropped from an earlier meta-analysis), an inclusion-filter error in an earlier joint-model summary, and external-cohort tissue/stage handling were corrected; all numbers here are from the corrected pipeline, and code is available at https://github.com/sushuqiong/egfr-pathway-context-atlas.

"""
s = replace_section(s, "### 4.7 Driver-stratified effect modification", "### 4.9 Conclusion", d47 + d48)

# ---------------- Conclusion ----------------
d49 = """### 4.9 Conclusion
Across 27 public transcriptomic cohorts, growth-factor module expression was strongly context dependent. Many lesion-control differences attenuated after joint composition adjustment; 7 of 170 states survived conservative unified-scale meta-analysis, 21 were composition-robust (concentrated in colorectal and gastric cancer plus IBD JAK-STAT), and no state passed strict external replication despite directional consistency for several vascular/stromal signals. These results provide composition-aware hypotheses rather than direct evidence of pathway activation or therapeutic actionability, and they argue that composition-aware, replication-explicit reporting should become standard for tissue-level pathway atlases.

"""
s = replace_section(s, "### 4.9 Conclusion", "## Figure legends", d49)

s = re.sub(r"\\\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
open(DST, "w", encoding="utf-8").write(s)
w = len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1)))
print("v10 written; abstract words:", w)