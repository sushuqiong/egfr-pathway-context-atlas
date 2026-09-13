# ERRATA — v11 (2026-09): effect-size denominator, composition reporting, single-cell pairing, mutation denominators

Four issues raised in an external computational review of v10 were confirmed and corrected. **The v10 numbers for these analyses are superseded.**

## 1. Paired and unpaired effects did not share a standardization denominator
- **Problem**: v10 combined unpaired SMD (pooled-SD denominator) with paired SMCRH (sd1 denominator) and described the result as one "common scale". Per the metafor documentation, SMD standardises by the pooled SD, SMCRH by sd1, and the average-variance measures are SMDH/SMCRPH.
- **Fix**: unpaired cohorts now use `escalc(measure="SMDH")` and matched cohorts `escalc(measure="SMCRPH")` with the empirical within-pair correlation; both use the root-mean-variance denominator √[(sd1²+sd2²)/2].
- **v10 → v11**: BH-significant states under REML/Knapp-Hartung 18 → **17**; DerSimonian-Laird 76 → **74**; additional pre-specified sensitivities: non-shrinking Knapp-Hartung (**6**, all CRC) and unpaired-cohorts-only (**3**, all IBD); fixed r = 0.5/0.7 gives 17.

## 2. Composition was reported as a single "unadjusted" coefficient
- **Problem**: the v10 text extracted an "unadjusted" disease coefficient from the adjusted model, which is a conditional coefficient, and described significance loss as attenuation/explanation.
- **Fix**: two models on identical samples — base (module ~ disease [+ patient]) and adjusted (+ four compartment scores) — with coefficients, standard errors and CIs reported for both, plus the ratio |beta_adjusted|/|beta_base|. No causal language: loss of significance can reflect smaller coefficients, larger standard errors or collinearity.
- **Result**: 21 composition-robust states (CRC 10, STAD 9, ESCC 1, IBD 1; none in PAAD); median adjusted/base ratio **0.87**.

## 3. Single-cell tests were unpaired while the Methods described paired testing
- **Problem**: the v10 pipeline used Mann-Whitney tests on patient-level means, whereas the text described paired Wilcoxon tests; patients present in both groups were not handled as pairs; and malignant-versus-normal-epithelium comparisons (different cell identities) were reported alongside same-cell-type comparisons.
- **Fix**: paired Wilcoxon signed-rank tests are used wherever ≥5 complete patient pairs exist (number of pairs reported; patients without the cell type in one group are excluded from the paired test and counted in the unpaired denominators); otherwise unpaired tests are used and labelled. Malignant-versus-normal-epithelium comparisons are labelled as **cell-identity contrasts** and are not interpreted as same-cell-type disease effects. BH is applied within each comparison-type family.
- **Result**: 16 same-cell-type significant comparisons (10 by paired signed-rank, median 15 complete pairs) plus 12 cell-identity contrasts; an unpaired-only sensitivity gives 29 significant comparisons.

## 4. Mutation prevalence and driver analyses used CNA-based denominators
- **Problem**: `n_sequenced` in the v10 pipeline counted samples with **CNA** data, so mutation percentages used a mismatched denominator, and samples without mutation data were treated as wild-type.
- **Fix**: denominators come from the cBioPortal mutation-profiled sample lists (`<study>_sequenced`); driver-positive = a mutation record, driver-negative = profiled with no record (explicit wild type), and non-profiled samples are excluded and counted.
- **Result**: mutation-profiled samples LUAD 559, CRC 534, STAD 431, PAAD 173, HCC 366, ESCC 185. PAAD KRAS 107/173 (**61.9%**), TP53 100/173 (57.8%), EGFR 1/173 (0.6%); the original TCGA PDAC study reported 140 KRAS-mutant tumours among 150 analysed cases, reflecting different subsets and mutation-calling pipelines. Driver screen: 102 tests, 5 nominal, **0** after BH-FDR (PAAD: 164 analysed, 98 mutant, 66 wild type, 13 non-profiled excluded).

## Consistency and presentation fixes
- All numbers in the manuscript, Table 1, figure legends and figures are regenerated from the frozen v11 result tables; the previous mismatch (CRC 573/190 in Methods versus 556/187 in Results) is resolved to 556/187 with the audit trail.
- Figure 1 is now drawn as **parallel evidence layers** (states can pass a later layer without passing an earlier one: STAD contributes nine composition-robust states and no meta-significant state).
- Figure 6 separates paired same-cell-type comparisons from cell-identity contrasts; Figure 5 uses profiled-only denominators.
- Decision rules (per-cohort, meta, composition-robust, external replication) and multiplicity scopes are stated in Methods; estimator sensitivity is reported rather than hidden.
