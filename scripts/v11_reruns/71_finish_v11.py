#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
P=r"C:\Users\fengq\Desktop\EGFR\EGFR的v11\01_稿件正文\Manuscript_draft_v11.md"
s=open(P,encoding="utf-8").read()
def sec(a,b,new):
    global s
    i=s.find(a); j=s.find(b); assert i>=0 and j>i,(a,b); s=s[:i]+new+s[j:]

# ---- abstract (<=255 words) ----
abs_new = """## Abstract

**Background.** Receptor-tyrosine-kinase (RTK) pathway transcriptional states are context dependent, yet how they compare across cancers and chronic benign diseases, how much of a bulk signal reflects tissue composition, and whether surviving signals replicate remain unclear.

**Methods.** Seventeen growth-factor pathway modules were scored in 27 public case-control cohorts across ten contexts. Effects were expressed on one common standardized scale (unpaired: Hedges-corrected SMDH; matched: Hedges-corrected SMCRPH with the empirical within-pair correlation; both use the root-mean-variance denominator) and pooled with REML/Hartung-Knapp inference. Composition was addressed by comparing base models (module ~ disease [+ patient]) with adjusted models adding four compartment scores on identical samples. Single-cell comparisons used paired signed-rank tests where complete patient pairs existed. TCGA module-OS associations (108 tests) were assessed with age/stage sensitivity, a driver screen restricted to mutation-profiled samples, and external validation in independent CRC, PDAC and gastric cohorts with tissue-type and stage correction.

**Results.** Fifty-five of 170 states were per-cohort robust; meta-analysis retained 17 states (74 under DerSimonian-Laird; 6 with non-shrinking Knapp-Hartung; 3 unpaired-only), and the base-versus-adjusted comparison retained 21 (CRC 10, STAD 9, ESCC 1, IBD 1; none in PAAD) with a median adjusted-to-base coefficient ratio of 0.87. In TCGA, 17/108 associations were FDR<0.05 and 11 of 15 testable signals survived age+stage adjustment. No module passed pre-specified external replication (CRC VEGF/PDGF HR 1.16, p=0.042, but 1.09, p=0.22 after stage adjustment). Single-cell analysis yielded 16 same-cell-type comparisons (10 paired, median 15 complete pairs) and 12 separately labelled cell-identity contrasts.

**Conclusions.** Most bulk RTK-related differences track tissue composition and clinical background, attenuation was typically modest rather than complete, and no surviving signal replicated externally. The atlas provides composition-aware, evidence-tiered hypotheses with explicit decision rules rather than direct evidence of pathway activation.

"""
sec("## Abstract","## 1. Introduction",abs_new)

# ---- Discussion 4.1 ----
d41 = """### 4.1 Principal findings
We assembled a transcriptional atlas of growth-factor pathway modules across six cancers and four chronic benign diseases and evaluated every candidate state through non-hierarchical evidence layers. Fifty-five of 170 states were per-cohort robust; 17 survived common-denominator conservative meta-analysis; 21 were composition-robust in base-versus-adjusted comparisons; and none met pre-specified external replication criteria. Because these layers answer different questions and are not nested (for example, STAD contributes nine composition-robust states but no meta-significant state), the atlas is best read as a composition-aware hypothesis generator with an explicit per-state evidence matrix (Table S9) that records why each state passed or failed each layer.

"""
sec("### 4.1 Principal findings","### 4.2 Composition shapes",d41)

# ---- Discussion 4.2 ----
d42 = """### 4.2 Composition shifts bulk inference without explaining it
Composition adjustment changed which states survived, but the average effect on coefficients was modest (median adjusted-to-base ratio 0.87), and attenuation was context dependent: PAAD showed the strongest attenuation, consistent with its large stromal fraction, whereas CRC and STAD retained their largest composition-robust sets. We deliberately avoid causal language here. A state can lose significance because its coefficient shrinks, because its standard error grows, or because disease status and composition scores are collinear by construction; module and composition scores are both derived from the same expression matrix; and adjusting for composition can remove part of the disease mechanism itself. xCell returns enrichment scores rather than cell proportions, and EPIC, which requires non-log linear input and has an uncharacterised compartment that is not equivalent to the xCell epithelial score, agreed only moderately with xCell; these are limitations, not cross-tool validation. The defensible statement is that composition is a major axis of variation in bulk tissue comparisons and must be modelled explicitly, not that it "drives" or "explains" the surviving differences.

"""
sec("### 4.2 Composition shapes","### 4.3 Surviving composition-robust",d42)

# ---- Discussion 4.3 ----
d43 = """### 4.3 Surviving composition-robust signals and their cellular sources
The composition-robust set comprises ten CRC states (WNT/\\u03b2-catenin, EPH, VEGF/PDGF and HGF/MET up; FGFR, IGF/INSR, ERBB ligands and RET/ALK/NTRK down; JAK-STAT and TAM/AXL up), nine STAD states, one ESCC state (VEGF/PDGF) and one benign state (IBD JAK-STAT). Single-cell data localize a subset of these to specific compartments: 16 same-cell-type comparisons were significant, of which ten used paired signed-rank tests on complete patient pairs (median 15 pairs), covering CRC epithelial and stromal/immune compartments, IBD epithelium and myeloid cells, and STAD epithelial compartments. A further 12 comparisons contrasted malignant-cell-labelled case cells with normal-tissue-labelled control epithelium; because these differ in cell identity as well as disease state, they are reported as cell-identity contrasts and are not interpreted as same-cell-type disease effects. Localization is transcript-level, paired only where the dataset permits, and does not test function.

"""
sec("### 4.3 Surviving composition-robust","### 4.4 PAAD:",d43)

# ---- Discussion 4.4 ----
d44 = """### 4.4 PAAD: composition-sensitive rather than composition-explained
PAAD showed the broadest raw module upregulation and the strongest attenuation in the base-versus-adjusted comparison: no PAAD state met the composition-robustness rule, and the TCGA-adverse module-OS associations were not reproduced in an independent PDAC cohort. Two qualifications are essential. First, loss of statistical robustness is not evidence that composition explains the signal; coefficients may shrink while standard errors grow, and the stromal compartment is itself part of PDAC biology. Second, the PDAC mutation landscape reported here is computed on mutation-profiled samples (107/173 KRAS-mutant, 61.9%) and is not directly comparable to the original TCGA PDAC report (140/150); different subsets and mutation-calling pipelines explain part of the difference. The accurate summary is that PAAD bulk module differences are strongly composition-associated and remain unvalidated, and that pathway scores in stroma-rich tumours should be composition-modelled before epithelial-intrinsic claims are made.

"""
sec("### 4.4 PAAD:","### 4.5 External validation",d44)

# ---- Discussion 4.5 ----
d45 = """### 4.5 External validation defines the limits of the atlas
After tissue-type filtering, numeric stage parsing and pairing corrections, no module passed pre-specified external replication. The CRC VEGF/PDGF signal was directionally consistent but lost significance after stage adjustment; CRC FGFR and IGF/INSR were nominally adverse after age+stage adjustment without FDR significance; three of five ACRG gastric vascular/stromal signals were directionally consistent without FDR significance; and no PDAC signal was reproduced. Failure to replicate is reported as such rather than as absence of effect, because the cohorts differ in outcome definition, treatment background, stage distribution and assay. The contribution of this study therefore lies in the comparison framework, the composition-aware and replication-explicit reporting rules, and the reusable per-state evidence resource - not in the correction of earlier analysis errors, which is reported transparently in the code documentation (Analysis revisions, Methods) and should be regarded as quality control rather than as a methodological advance.

"""
sec("### 4.5 External validation","### 4.6 ESCC",d45)

# ---- Discussion 4.6 ESCC wording ----
d46 = """### 4.6 ESCC EGFR dissociation
In ESCC, EGFR high-level amplification (the highest of the six contexts here) coexists with a protective single-gene EGFR expression association (HR 0.56). Stratification shows that this association is estimable in non-amplified patients (HR 0.48, p=0.001) while the amplified subgroup is too small to estimate (n=14, three events); because the amplified group is not estimable, we do not claim that the two groups differ. The dissociation is therefore reported as a cautionary example that amplification, expression and targetability are distinct measurements.

"""
sec("### 4.6 ESCC","### 4.7 Driver-stratified",d46)

# ---- Discussion 4.7 ----
d47 = """### 4.7 Driver-stratified effect modification is an underpowered screen
With profiled-only eligibility (non-profiled patients excluded and counted), 102 interaction tests were performed; five were nominally significant and none survived FDR. Because several strata contain few events, the screen cannot distinguish absent effect modification from insufficient power, and no claim of stability across driver backgrounds is made. Its value is documentary: it shows how driver analyses change when eligibility and denominators are defined explicitly.

"""
# ---- Discussion 4.8 limitations ----
d48 = """### 4.8 Limitations
Transcriptional proxies: module scores are expression states, not phosphorylation or pathway activity, and modules mix receptors, ligands and effectors, so a module mean does not carry a single biological meaning; membership and per-platform coverage are in Table S2. Effect sizes: paired cohorts required an empirical within-pair correlation (median 0.11) and a common-denominator standardized measure; fixed-correlation sensitivity (0.5/0.7) and an unpaired-only analysis are reported because the choice of estimator changes the number of surviving states (17, 74, 6 and 3 across REML/Knapp-Hartung, DerSimonian-Laird, non-shrinking Knapp-Hartung and unpaired-only analyses). Composition: xCell yields enrichment scores; disease and composition are correlated; residualization and joint adjustment answer different questions and agree for 18 of 19 residualization-robust states; EPIC agreed only moderately with xCell. External validation: after tissue-type and stage correction no state replicated, stage was unavailable for part of the PDAC analysis, and treatment exposure is not captured in public cohorts. Prognosis: associations were primarily univariable; subtype and interaction analyses were underpowered and the PDAC subtype classifier was a derived variant not validated against the original calls. Single cell: comparisons are transcript-level; where pairing was possible it was used and the number of complete pairs is reported, but paired analyses exclude patients without the cell type in both groups, and cell-identity contrasts are not disease effects. Mutation layers: prevalence and driver states are restricted to mutation-profiled samples, so they are not comparable to cohorts with different profiling scope. Meta-analysis: k is small in several contexts, so I\\u00b2 is unstable and the number of surviving states is estimator dependent. Analysis revisions: an earlier paired-indexing error, an earlier inclusion-filter error in the composition summary, and external-cohort tissue/stage handling were corrected; all numbers here come from the corrected pipeline, described in the code repository.

"""
sec("### 4.7 Driver-stratified","### 4.9 Conclusion",d47+d48)

# ---- Conclusion ----
d49 = """### 4.9 Conclusion
Across 27 public transcriptomic cohorts, growth-factor module expression was strongly context dependent. Fifty-five of 170 states were per-cohort robust, 17 survived common-denominator conservative meta-analysis, 21 were composition-robust in base-versus-adjusted comparisons, and no state passed pre-specified external replication. Attenuation by composition was typically modest rather than complete, and the surviving states were concentrated in colorectal and gastric cancer plus IBD JAK-STAT. The atlas therefore provides composition-aware, evidence-tiered hypotheses, explicit decision rules and a reusable per-state evidence matrix, rather than direct evidence of pathway activation or therapeutic actionability.

"""
sec("### 4.9 Conclusion","## Figure legends",d49)

s=re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1),16)), s)
open(P,"w",encoding="utf-8").write(s)
w=len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1)))
print("abstract words:", w)
for k in ["retained 17","median adjusted-to-base coefficient ratio of 0.87","16 same-cell-type","12 separately labelled cell-identity","no module passed","61.9%","profiled-only"]:
    print(" ",k,"->",s.count(k))
