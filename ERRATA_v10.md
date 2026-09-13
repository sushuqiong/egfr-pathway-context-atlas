# ERRATA — corrections applied in v10 (2026-09)

Three implementation errors were found during an external computational audit and corrected. All affected results were recomputed; **the v9 numbers for these analyses are withdrawn**.

## 1. Paired-sample indexing error (meta-analysis)
- **Symptom**: in the v9 script `10_v9_joint_unified.R`, case/control patient identifiers were used to index a *full* module-score vector instead of the case and control subsets. For matched cohorts this subtracted a group from itself, producing a within-pair correlation of 1 and non-estimable variances; all 200 paired records were then dropped by the meta-analysis filter, silently removing the 12 matched cohorts (including all LUAD, PAAD and ESCC paired cohorts).
- **Fix**: explicit subsetting (`yc <- y[match(cc, pid[case])]`, `yr <- y[match(cc, pid[control])]`) and use of the standard implementation `metafor::escalc(measure="SMCRH", ri = empirical)` for matched cohorts; `metafor::rma.uni(method="REML", test="knha")` for pooling. All 200 paired records are now estimable (median empirical r = 0.99); fixed r = 0.5/0.7 sensitivity analyses give identical pooled results.
- **v9 → v10**: pooled-significant states 11 → **7** (REML/Hartung-Knapp); 31 → **20** (DerSimonian-Laird).

## 2. Inclusion-filter error in the joint-model summary
- **Symptom**: the v9 meta script filtered the per-cohort table to rows with a finite unified effect/variance *before* summarising the joint-model results, so cohorts whose effect size was missing were also dropped from the joint-model summary (this produced the erroneous "6 composition-robust states" and the disappearance of entire cancer contexts).
- **Fix**: each analysis layer now has its own inclusion criterion; the joint summary uses all rows with an estimable model (finite p), with statuses explicitly classified as *robust / estimated (not significant) / estimated without meeting the rule / not analysed*.
- **v9 → v10**: composition-robust states 6 → **21** (CRC 10, STAD 9, ESCC 1, IBD 1; PAAD 0).

## 3. External-cohort tissue-type and stage handling (GSE39582)
- **Symptom**: `is_norm` was computed but not used, so the 19 adjacent non-tumour arrays (17 with outcome annotation, 3 deaths) remained in the analysis; and stage was parsed only as Roman numerals although the public metadata encodes TNM stage as 1–4 (plus 0 and N/A), converting all valid stages to missing and prompting the incorrect statement that "stage was unavailable in the public record".
- **Fix**: filter by the explicit tissue field (`dataset:ch1` = Non Tumoral excluded), parse numeric stage, and re-fit unadjusted, age-adjusted and age+stage-adjusted models with 95% CI and BH-FDR.
- **v9 → v10**: analysable samples 573 (190 deaths) → **556 tumour samples (187 deaths)**; stage available in 552 (four stage-0 samples excluded from stage-adjusted models). The CRC VEGF/PDGF signal is nominal only (HR 1.16, p=0.042; age 1.15, p=0.049; **age+stage 1.09, p=0.22**) and is **not** a robust external replication.

## Additional changes
- Group reference level is now set explicitly (Control) in the model; the v9 post-hoc `-1` sign-flip script is deprecated.
- Composition scores and expression matrices are joined by sample ID rather than by row order.
- Adjusted and unadjusted effects are reported from the same model (identical residual SD) so that attenuation is not inferred from differently standardized estimates.


## Second-pass correction (within v10)
After the first v10 re-analysis, the verification suite (hand calculation vs metafor; sample-order shuffle; repeated run) revealed that the paired fix was still incomplete: `y[match(cc, case_ids)]` indexes the full vector with positions from the case subset, which is only correct when cases happen to occupy the leading rows. The implementation now subsets first and then matches values (`y_case <- y[case]; yc <- y_case[match(cc, id_case)]`). With the corrected indexing the median empirical within-pair correlation is **0.11** (not 0.99), and the final v10 numbers are: per-cohort 55/170; unified-scale meta **REML/Hartung-Knapp 18** (19 at fixed rho 0.5/0.7), **DL 76**; joint-model composition-robust **21** (CRC 10, STAD 9, ESCC 1, IBD 1; PAAD 0); CRC external 556/187 with VEGF/PDGF directionally consistent but not stage-robust. Verification logs are in `tests/check_paired_effect_log.txt`.
