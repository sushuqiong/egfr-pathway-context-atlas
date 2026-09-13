#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build Manuscript_draft_v11.md from v10 with the corrected v11 numbers and GPT6-v10 fixes."""
import re, os
SRC=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\01_稿件正文\Manuscript_draft_v10.md"
DST=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\01_稿件正文\Manuscript_draft_v11.md"
os.makedirs(os.path.dirname(DST), exist_ok=True)
s=open(SRC,encoding="utf-8").read()
def sec(a,b,new):
    global s
    i=s.find(a); j=s.find(b); assert i>=0 and j>i,(a,b); s=s[:i]+new+s[j:]

# ---------- title / data freeze line ----------
s=s.replace("v9: unified-scale meta-analysis and joint composition models (September 2026).",
            "v11: effect sizes on a common denominator (SMDH/SMCRPH), two-model composition comparison, profiled-only driver eligibility (September 2026).")

# ---------- Abstract ----------
abs_new = """## Abstract

**Background.** Receptor-tyrosine-kinase (RTK) pathway transcriptional states are context dependent, yet how they compare across cancers and chronic benign diseases, how much of a bulk signal reflects tissue composition, and whether surviving signals replicate remain unclear.

**Methods.** Seventeen growth-factor pathway modules were scored in 27 public case-control cohorts spanning ten contexts with discovery-validation separation. Effects were expressed on a common two-group standardized scale (unpaired cohorts: Hedges-corrected SMDH; matched cohorts: Hedges-corrected SMCRPH with the empirical within-pair correlation; both use the root-mean-variance denominator) and pooled by random-effects meta-analysis with REML/Hartung-Knapp inference. Composition was addressed by comparing a base model (module ~ disease [+ patient]) with an adjusted model adding epithelial, fibroblast, endothelial and immune scores on the same samples. Patient-level single-cell data were analysed with paired signed-rank tests where complete patient pairs existed. TCGA module-OS associations (108 tests) were assessed with age/stage sensitivity, a driver-stratified screen restricted to mutation-profiled samples, and external validation in independent CRC, PDAC and gastric cohorts with tissue-type filtering and stage adjustment.

**Results.** Fifty-five of 170 states were per-cohort robust; conservative meta-analysis retained 17 states (74 under DerSimonian-Laird; 6 with non-shrinking Knapp-Hartung; 3 when restricted to unpaired cohorts), and the two-model composition comparison retained 21 states (CRC 10, STAD 9, ESCC 1, IBD 1; no PAAD state) with a median adjusted-to-base coefficient ratio of 0.87. In TCGA, 17/108 module-OS associations were FDR<0.05 and 11 of 15 testable signals survived age+stage adjustment. No module passed pre-specified external replication: CRC VEGF/PDGF was directionally consistent (HR 1.16, p=0.042) but not significant after stage adjustment (1.09, p=0.22), and the single-cell layer yielded 16 same-cell-type comparisons (10 by paired signed-rank, median 15 complete pairs) alongside 12 explicitly labelled cell-identity contrasts.

**Conclusions.** Most bulk RTK-related transcriptional differences track tissue composition and clinical background; attenuation was typically modest rather than complete, and no surviving signal replicated externally. The atlas provides composition-aware, evidence-tiered hypotheses rather than direct evidence of pathway activation, with explicit decision rules and a per-state evidence matrix.

"""
sec("## Abstract","## 1. Introduction",abs_new)

# ---------- Methods 2.3 (effect sizes + rules) ----------
m23 = """### 2.3 Bulk scoring, effect sizes and meta-analysis
Per cohort, probes were mapped to unambiguous gene symbols (multi-probe mean; platform annotation from GEO or parsed annotation tables where available), auto-log2 transformed where needed, and scored by GSVA (Gaussian kernel, minSize \\u2265 3). In representative cohorts spanning two microarray platforms, GSVA scores correlated highly with member-mean z-scores (median Spearman \\u03c1 = 0.94 over 102 state-cohort pairs). Differential testing used limma eBayes with a matched-patient factor for the twelve matched cohorts.

Effect sizes were computed with metafor so that paired and unpaired cohorts share the same standardization denominator (root mean variance, \\u221a[(sd_case\\u00b2+sd_control\\u00b2)/2]): measure SMDH for unpaired cohorts and measure SMCRPH for matched cohorts, which additionally uses the empirical within-pair correlation estimated per cohort and module (median r = 0.11; fixed r = 0.5 and 0.7 give identical verdicts). Pooling used random-effects meta-analysis with REML estimation and the Hartung-Knapp adjustment; DerSimonian-Laird pooling and the non-shrinking Knapp-Hartung variant were computed as sensitivity analyses, as was a unpaired-cohorts-only analysis. Heterogeneity is reported as I\\u00b2 and \\u03c4\\u00b2, and BH-FDR was applied within each disease across the 17 module features (k \\u2265 2 cohorts required for a pooled estimate; k = 1 estimates are reported but not treated as meta evidence).

"""
sec("### 2.3 Bulk scoring","### 2.4 Composition adjustment",m23)

# ---------- Methods 2.4 (two-model comparison) ----------
m24 = """### 2.4 Composition: base versus adjusted models
Tissue composition was estimated by xCell v1.1.0 (64 immune/stromal cell types plus ImmuneScore); xCell returns expression-derived enrichment scores, not cell proportions. For each cohort and module we fitted two models on exactly the same samples: a base model (module score ~ disease status [+ matched-patient factor]) and an adjusted model adding the four compartment scores (epithelial, fibroblast, endothelial, immune). Disease coefficients, standard errors and confidence intervals are reported for both models; because the two models share the same outcome scale, their coefficients are directly comparable, and we additionally report the ratio |beta_adjusted|/|beta_base| rather than interpreting a significance change as the fraction of signal "explained" by composition. Loss of significance can arise from a smaller coefficient, a larger standard error, or collinearity between disease status and composition; these possibilities are reported rather than conflated. Composition scores and expression matrices were joined by sample ID. Two-step xCell residualization is retained only as a sensitivity analysis (Methods 2.10), because it can over- or under-correct when disease and composition are correlated. A marker-proxy sensitivity version correlated with the xCell medians across the 170 states (Spearman \\u03c1 = 0.81). EPIC concordance was assessed in all 27 cohorts (endothelial \\u03c1 = 0.56, immune 0.44, fibroblast/CAF 0.28, epithelial/cancer 0.09); EPIC requires non-log linear input and its uncharacterised compartment is not equivalent to the xCell epithelial score, so it is reported as a limitation.

"""
sec("### 2.4 Composition adjustment","### 2.5 Single-cell source validation",m24)

# ---------- Methods 2.5 (single-cell pairing rules) ----------
m25 = """### 2.5 Single-cell source validation
Five public single-cell datasets (CRC, IBD, LUAD, STAD, asthma) were scored for the target modules as the mean of log-normalised member-gene expression per cell; cells were aggregated to patient-level means within each cell type and disease group. Each comparison is labelled by type. **Same-cell-type comparisons** contrast the same cell-type label between case and control patients. Where the same patient contributes to both groups, differences are tested with a Wilcoxon signed-rank test on the complete pairs (\\u2265 5 pairs required) and the number of complete pairs is reported; comparisons without enough complete pairs use an unpaired Mann-Whitney test and are labelled as unpaired. Patients lacking a cell type in one group are excluded from the paired test and counted in the unpaired denominators. **Cell-identity contrasts** compare malignant-cell-labelled case cells with normal-tissue-labelled control epithelium; these are explicitly labelled as cell-identity contrasts because they differ in cell identity as well as disease state, and they are not interpreted as same-cell-type disease effects. BH-FDR is applied separately within each comparison-type family of each context-module group. Localization is transcript-level and does not test function.

"""
sec("### 2.5 Single-cell source validation","### 2.6 TCGA survival layer",m25)

# ---------- Methods 2.6 (OS + multiplicity scope) ----------
m26 = """### 2.6 TCGA survival layer, multiplicities and decision rules
Module scores (member-mean z) were tested against overall survival by univariable Cox regression (HR per 1 SD; n \\u2265 40; \\u2265 10 events) for 17 module features plus a single-gene EGFR feature (108 tests across six contexts), with BH-FDR applied within each context-specific family of 18 tests and the EGFR single-gene feature analysed in the univariable layer only. Multivariable sensitivity re-fitted the 15 module features with covariate data (age; age+stage) and is reported as a candidate-set re-analysis rather than as genome-wide error control. Decision rules are pre-specified and applied without further filtering: **per-cohort robust** = \\u2265 2/3 of cohorts sharing the majority sign with \\u2265 2 cohorts at FDR < 0.05 (both cohorts for k = 2); **meta-significant** = pooled REML/Hartung-Knapp BH-FDR < 0.05 with k \\u2265 2; **composition-robust** = \\u2265 2 cohorts with adjusted-model FDR < 0.05 and the same majority-sign rule, with non-estimable states labelled; **externally replicated** = nominal p < 0.05 in the unadjusted model, consistent direction, and p < 0.05 after age+stage adjustment (FDR reported as secondary; failure to meet these criteria is reported as "not replicated", not as absence of effect).

"""
sec("### 2.6 TCGA survival layer","### 2.7 Driver-stratified models",m26)

# ---------- Methods 2.7 (driver eligibility) ----------
m27 = """### 2.7 Driver-stratified models with profiled-only eligibility
Driver status was defined only among mutation-profiled samples (cBioPortal `<study>_sequenced` sample list; 173-559 samples per context): driver-positive = a mutation record for the gene; driver-negative = profiled with no record for that gene (explicit wild type). Non-profiled samples are excluded and counted. Amplification drivers use CNA-profiled samples similarly. Module-by-driver interactions were tested by Cox regression (z \\u00d7 driver) and BH-corrected across all interaction tests; the screen is underpowered in small strata and is reported as exploratory.

"""
sec("### 2.7 Driver-stratified models","### 2.8 External validation",m27)

# ---------- Methods 2.8 (external, consistent counts) ----------
m28 = """### 2.8 External validation
External validation was retrospective and independent. For CRC (GSE39582), the public series contains 585 arrays, of which 566 are tumour and 19 adjacent non-tumour; non-tumour arrays were excluded, as were arrays without usable outcome annotation, leaving 556 tumour samples with 187 deaths for analysis (stage 1-4 available in 552; four stage-0 samples were excluded from stage-adjusted models). Cohort audit records are provided with the code. For PDAC (GSE21501; 102 patients, 66 deaths) and gastric cancer (ACRG/GSE62254; 300 tumours, 152 deaths) the analyses used all eligible samples. Module scores were computed as member-mean z within each cohort, and Cox models were fitted unadjusted, age-adjusted and age+stage-adjusted with 95% confidence intervals; BH-FDR is reported across the modules tested in each cohort.

"""
sec("### 2.8 External validation","### 2.9 PAAD molecular subtype",m28)

# ---------- Methods 2.9 (PAAD eligibility) ----------
m29 = """### 2.9 PAAD molecular subtype, purity and sample eligibility
TCGA-PAAD samples with RNA-seq were classified into basal-like and classical tumours with a factor-loading nearest-centroid rule derived from published PDAC subtype programs; this derived classifier was not validated against the original subtype calls and the analysis is therefore exploratory. Subtype-stratified OS models and subtype interactions are reported without claiming subtype independence. Tumour purity was addressed with an approximate expression-derived immune/stromal proxy; it is not a measured purity estimate. Mutation prevalence is reported on mutation-profiled samples only (PAAD: 173 profiled, KRAS mutated in 107, 61.9%), and we note that the original TCGA PDAC analysis reported 140 KRAS-mutant tumours among 150 analysed cases; the difference reflects different sample subsets and mutation-calling pipelines and is not reconciled here.

"""
sec("### 2.9 PAAD molecular subtype","### 2.10 Descriptive anchors",m29)

# ---------- Results 3.1 ----------
r31 = """### 3.1 Atlas overview and common-denominator meta-analysis [Fig 1, Fig 2; Table 1]
Across 170 context-module summaries, 55 states were per-cohort robust (LUAD 14, CRC 11, STAD 10, PAAD 10, ESCC 4, IBD 6; none in HCC, COPD, NAFLD or asthma under the per-cohort rule). With paired and unpaired cohorts expressed on the common root-mean-variance scale, conservative REML/Hartung-Knapp meta-analysis retained 17 states (CRC 11, IBD 3, LUAD 2, PAAD 1), whereas DerSimonian-Laird pooling identified 74, the non-shrinking Knapp-Hartung variant 6 (all CRC), and an unpaired-cohorts-only analysis 3 (all IBD); fixed-correlation sensitivity for the matched cohorts (r = 0.5/0.7) again retained 17. The CRC states were WNT/\\u03b2-catenin (+3.00), EPH (+2.22), HGF/MET (+0.94) and, in the opposite direction, FGFR (\\u22121.67), RET/ALK/NTRK (\\u22121.17), PDGFR-KIT (\\u22121.08), IGF/INSR (\\u22120.97), TGF\\u03b2/SMAD (\\u22120.54), ERBB ligands (\\u22120.45), TIE/Ang (\\u22120.22) and JAK-STAT (\\u22120.06); IBD states were VEGF/PDGF (+1.44), SRC/FAK (+0.47) and ERBB receptors (\\u22121.44); LUAD showed FGFR (\\u22122.01) and JAK-STAT (\\u22121.02) downregulation; and PAAD showed RAS-MAPK upregulation (+1.15). NAFLD remained null within the power of the available cohorts.

"""
sec("### 3.1 Atlas overview","### 3.2 Cancer architectures",r31)

# ---------- Results 3.3 ----------
r33 = """### 3.3 Benign contexts [Fig 2; Table 1]
Under the common-denominator meta-analysis the benign-context signal was IBD-dominant (three states: VEGF/PDGF +1.44, SRC/FAK +0.47, ERBB receptors \\u22121.44), and IBD JAK-STAT remained the single composition-robust benign state, localized by single-cell data to colonic epithelium and myeloid cells (Results 3.5). COPD, asthma and NAFLD produced no state that survived conservative meta-analysis; the COPD and asthma signals seen with DerSimonian-Laird pooling did not survive the conservative or composition layers.

"""
sec("### 3.3 Benign contexts","### 3.4 Composition adjustment",r33)

# ---------- Results 3.4 ----------
r34 = """### 3.4 Composition: base versus adjusted models [Fig 3; Table 1; Table S9]
In the two-model comparison, 21 of 170 states were composition-robust (CRC 10, STAD 9, ESCC 1, IBD 1); the remaining states were estimated but not significant (95), estimated without meeting the robustness rule (54), or not analysable (0). The median ratio of adjusted to base disease coefficients was 0.87 across all estimated states, indicating modest rather than complete attenuation on average; PAAD states showed the strongest attenuation and none met the composition-robustness rule, but we report this as loss of statistical robustness rather than as proof that composition explains the signal, because coefficients can shrink while standard errors grow and because disease status and composition scores are correlated by construction. The xCell two-step residualization sensitivity classified 19 states as robust, largely overlapping the joint-model set (18 of 19; CRC 10, STAD 8), with three joint-robust states not matched by residualization (CRC VEGF/PDGF, STAD VEGF/PDGF, IBD JAK-STAT) and one residualization-only state (ESCC SRC/FAK). Per-state details, including which layer each state passed or failed, are given in Table S9.

"""
sec("### 3.4 Composition adjustment","### 3.5 Single-cell localization",r34)

# ---------- Results 3.5 (single cell pairing) ----------
r35 = """### 3.5 Single-cell localization with explicit patient pairing [Fig 6]
Across the five single-cell datasets, 174 module-by-cell-type comparisons were tested. After family-wise BH correction, 16 same-cell-type comparisons were significant: in CRC, tumour versus normal epithelium and stromal/immune compartments for WNT/\\u03b2-catenin, EPH, VEGF/PDGF and HGF/MET; in IBD, JAK-STAT in epithelium and myeloid cells; in STAD, EPH and JAK-STAT. Ten of the 16 used paired signed-rank tests on complete patient pairs (median 15 pairs; the paired analyses exclude patients lacking that cell type in one group, and those patients are counted in the unpaired denominators), and six used unpaired Mann-Whitney tests where fewer than five complete pairs existed; these are labelled in Fig 6 and Table S6. Twelve further comparisons were significant when malignant-cell-labelled case cells were compared with normal-tissue-labelled control epithelium; because these contrast different cell identities as well as disease state, they are labelled as cell-identity contrasts and are not interpreted as same-cell-type disease effects. An unpaired-only sensitivity analysis of all comparisons gave 29 significant comparisons, indicating that paired testing (where available) is more conservative.

"""
sec("### 3.5 Single-cell localization","### 3.6 Prognosis and external validation",r35)

# ---------- Results 3.7 driver ----------
r37 = """### 3.7 Driver-stratified effect modification with profiled-only eligibility [Table S4]
Restricting to mutation-profiled samples (median 8.2% of patients excluded per context as non-profiled; for PAAD, 164 of 177 patients with expression and survival data were profiled, 98 KRAS-mutant and 66 wild-type), 102 module-by-driver interaction tests were performed. Five were nominally significant (PAAD KRAS \\u00d7 VEGF/PDGF HR 1.60, p=0.028; LUAD EGFR \\u00d7 EPH HR 1.74, p=0.033; LUAD EGFR \\u00d7 RAS-MAPK HR 1.90, p=0.045; HCC TP53 \\u00d7 PDGFR-KIT HR 1.50, p=0.038; HCC TP53 \\u00d7 TAM/AXL HR 1.81, p=0.002) and none survived BH-FDR. The screen cannot distinguish true absence of effect modification from insufficient power in small strata, and no claim of stability across driver backgrounds is made.

"""
sec("### 3.7 Driver-stratified effect-modification screen","### 3.8 PAAD molecular subtype",r37)

# ---------- Results 3.8 subtype ----------
r38 = """### 3.8 PAAD molecular subtype, purity and mutation denominators
In TCGA-PAAD, 179 samples with RNA-seq were classified by the derived rule (81 basal-like, 98 classical), of which 178 had survival data; overall survival did not differ between subtypes (HR 0.81, p=0.30) and no module-by-subtype interaction was significant. The TCGA-adverse module-OS associations were not materially attenuated by the approximate purity proxy, but because the proxy is expression-derived and no PDAC signal was reproduced externally, these remain TCGA-specific observations. On the mutation-profiled subset (173 samples) KRAS was mutated in 107 (61.9%), TP53 in 100 (57.8%) and EGFR in 1 (0.6%); the original TCGA PDAC study reported 140 KRAS-mutant tumours among 150 analysed cases, and the discrepancy is attributed to different sample subsets and mutation-calling pipelines (Methods 2.9).

"""
sec("### 3.8 PAAD molecular subtype","### 3.9 Descriptive anchors",r38)

# ---------- Results 3.6 external (rewrite) ----------
i=s.find("### 3.6 Prognosis and external validation"); j=s.find("### 3.7 Driver-stratified")
head=s[i:j]
k=head.find("External validation was reassessed")
assert i>0 and k>0
new_ext = """External validation was assessed against the pre-specified criteria (nominal significance, consistent direction, and survival of age+stage adjustment). In GSE39582 (556 tumour samples, 187 deaths after excluding 19 non-tumour arrays and arrays without usable outcome annotation; stage 1-4 in 552), the CRC VEGF/PDGF signal was directionally consistent but did not meet the criteria (HR 1.16, 95% CI 1.00-1.34, p=0.042; age-adjusted 1.15, p=0.049; age+stage-adjusted 1.09, p=0.22; BH-FDR 0.14-0.46 across modules). CRC FGFR (1.15, p=0.048) and IGF/INSR (1.16, p=0.045) were nominally adverse after age+stage adjustment without FDR significance; ERBB ligands, WNT/\\u03b2-catenin, PDGFR-KIT and EPH were null. In PDAC (GSE21501; 102 patients, 66 deaths) none of the seven TCGA-adverse module-OS associations was reproduced, and in gastric cancer (ACRG/GSE62254; 300 tumours, 152 deaths) three of five TCGA-adverse vascular/stromal modules were directionally consistent without FDR significance. **No module passed pre-specified external replication**; external non-significance is reported as failure to replicate rather than absence of effect.
"""
s=s[:i]+head[:k]+new_ext+"\n\n"+s[j:]

# ---------- Figure legends ----------
i=s.find("## Figure legends"); j=s.find("## Tables")
leg = """## Figure legends

**Figure 1. Parallel evidence layers.** Twenty-seven case-control cohorts (ten contexts) and 17 modules were assessed through non-hierarchical layers; numbers are per-cohort robust (55/170), common-denominator meta-analysis (REML/Hartung-Knapp 17; DerSimonian-Laird 74), two-model composition comparison (21 robust), single-cell localization (16 same-cell-type comparisons, of which 10 paired; 12 cell-identity contrasts labelled separately), TCGA prognosis (17/108 FDR<0.05) and external validation (CRC GSE39582 556/187; PDAC GSE21501 102/66; ACRG 300/152). Layers are shown in parallel because states can pass later layers without passing earlier ones (for example, STAD contributes nine composition-robust states but no meta-significant state).

**Figure 2. Module states before and after composition adjustment.** (A) Raw median standardized mean difference across ten contexts (asterisk = per-cohort-robust; digits = number of cohorts with FDR<0.05). (B) Adjusted-model estimates from the two-model comparison (fill = median adjusted coefficient in SD units of the shared reference SD; digits = cohorts with adjusted FDR<0.05; filled diamonds = composition-robust states; "n.e." = not estimable). Module labels are harmonised across panels; the xCell residualization sensitivity is Supplementary Figure S2.

**Figure 3. Base versus adjusted disease coefficients.** For all 170 states, the base-model coefficient (x-axis) is plotted against the adjusted-model coefficient (y-axis), both in the same outcome units; red = composition-robust; dashed line = identity. The median ratio is 0.87, i.e. attenuation is typically modest.

**Figure 4. TCGA module-OS associations.** Forest plot of the 17 FDR<0.05 module-OS associations (HR per 1 SD, 95% CI), coloured by cancer context.

**Figure 5. Molecular context with profiled-only denominators.** (A) EGFR and ERBB2 high-level amplification; (B) TP53, KRAS and EGFR mutation prevalence computed on mutation-profiled samples only (denominators: LUAD 559, CRC 534, STAD 431, PAAD 173, HCC 366, ESCC 185).

**Figure 6. Single-cell comparisons with pairing information.** Left: same-cell-type comparisons reaching family-wise FDR<0.05, labelled with the number of complete patient pairs (paired signed-rank) or with case/control patient numbers (unpaired). Right: cell-identity contrasts (malignant cells versus normal-tissue epithelium), labelled separately and not interpreted as same-cell-type disease effects.

**Supplementary Figure S1. Marker-proxy versus xCell medians.** **Supplementary Figure S2. xCell two-step residualization heatmap (sensitivity).**

"""
s=s[:i]+leg+s[j:]

# ---------- Tables ----------
i=s.find("## Tables"); j=s.find("## Keywords")
tabs = """## Tables

**Table 1.** Context-level summary (per-cohort robust; common-denominator meta-analysis with sensitivity estimators; composition-robust states; external status).

**Supplementary Table S1.** Cohort registry and origin-publication PMIDs.
**Supplementary Table S2.** Module membership, per-platform coverage, xCell overlap and drug-class map.
**Supplementary Table S3.** TCGA module-OS analyses (univariable, multivariable, CNA, mutation).
**Supplementary Table S4.** Driver-stratified interactions with profiled-only eligibility counts.
**Supplementary Table S5.** External validation (CRC, PDAC, ACRG) with confidence intervals and stage-adjusted models.
**Supplementary Table S6.** Single-cell comparisons with comparison type, complete pairs, test used and family-wise FDR.
**Supplementary Table S7.** PAAD subtype calls, purity proxy and mutation denominators.
**Supplementary Table S8.** Leave-one-gene-out and composition-marker-overlap stability.
**Supplementary Table S9.** Per-state evidence matrix with pass/fail reason for every layer.
**Supplementary Table S10.** Paired-effect verification records (cohort means, SDs, empirical correlation, SMDH/SMCRPH effects) and reproducibility checks.

"""
s=s[:i]+tabs+s[j:]
open(DST,"w",encoding="utf-8").write(s)
s2=re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1),16)), s)
open(DST,"w",encoding="utf-8").write(s2)
print("v11 written; abstract words:", len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s2, re.S).group(1))))
print("has 'retained 17':", s2.count("retained 17"), "| has 556:", s2.count("556"), "| stale 'retained 7':", s2.count("retained 7"))
