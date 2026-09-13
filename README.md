# egfr-pathway-context-atlas

**Growth-factor pathway architecture across human tissue contexts: a composition-aware transcriptional atlas spanning six cancers and four chronic diseases** (manuscript under review; npj Precision Oncology).

Analysis and reproduction package accompanying the manuscript **v11**.
> **Corrections (v11)**: effect sizes now use one common denominator (unpaired SMDH, matched SMCRPH); composition is reported as a base-versus-adjusted model comparison; single-cell tests are paired where complete patient pairs exist with cell-identity contrasts labelled separately; mutation prevalence and driver analyses use mutation-profiled samples only. See `ERRATA_v11.md`. Headline v11 numbers: per-cohort 55/170; meta REML/Knapp-Hartung **17** (DL **74**; non-shrinking KH **6**; unpaired-only **3**); composition-robust **21** (CRC 10, STAD 9, ESCC 1, IBD 1; PAAD 0) with a median adjusted/base coefficient ratio of 0.87; no module passed pre-specified external replication.

> **Corrections (v10)**: three implementation errors found in an external audit (paired-effect indexing, joint-model inclusion filter, external-cohort tissue/stage handling) are fixed; see `ERRATA_v10.md`. Corrected headline numbers: per-cohort 55/170; unified-scale meta REML/Hartung-Knapp **18** (DL **76**; 19 at fixed rho 0.5/0.7); joint-model composition-robust **21** (CRC 10, STAD 9, ESCC 1, IBD 1; PAAD 0); no module passed strict external replication (CRC VEGF/PDGF directionally consistent but not stage-robust).


## Overview
We scored 17 growth-factor pathway modules in 27 public case-control cohorts across ten tissue contexts (LUAD, CRC, STAD, PAAD, HCC, ESCC; IBD, COPD, NAFLD, asthma) and adjudicated every candidate signal across:

1. **Cross-cohort reproducibility** — per-cohort direction-consistency rule + within-context random-effects meta-analysis on a unified two-group effect scale (matched cohorts converted with the estimated within-pair correlation; REML/Hartung-Knapp inference).
2. **Composition adjustment** — joint models (`module ~ disease + epithelial/fibroblast/endothelial/immune scores [+ matched-patient factor]`); two-step xCell residualization retained as sensitivity.
3. **Single-cell source localization** — patient-level comparisons (global BH-FDR) in five datasets.
4. **Prognosis** — TCGA module-OS (per-context BH-FDR families), age/stage sensitivity, driver-stratified effect-modification screen, and external validation in independent CRC (GSE39582), PDAC (GSE21501) and gastric ACRG/GSE62254 cohorts.

**Headline results (v9):** 55/170 per-cohort-robust states; 11 pooled-significant under REML/Hartung-Knapp on the unified scale; 6 states composition-robust in joint models (CRC WNT/β-catenin, EPH, FGFR loss, IGF/INSR loss, VEGF/PDGF; IBD JAK-STAT); PAAD bulk effects fully attenuated by composition; externally, CRC VEGF/PDGF (HR 1.21) and three of five STAD vascular/stromal signals replicated, whereas CRC ERBB-ligand and all seven PAAD module-OS signals did not.

## Repository layout
```
manuscript/        Manuscript_draft_v09.md (250-word abstract; citations by first appearance)
scripts/
  atlas_pipeline/  Original analysis scripts 01-13 (atlas build, TCGA, deconvolution, single-cell, figures)
  v9_reruns/       v9 re-analysis scripts 10-51 (joint models, unified meta, rho sensitivity,
                   external audits, evidence matrix, citation renumbering, figure rebuilds)
results/           Processed result tables (evidence matrix Table S9, unified meta, joint composition,
                   external validation refinements, cohort accession registry, references)
reports/           Reviewer-visible analysis/decision records v7-v15
```

## Run order (reproduction)
1. `scripts/atlas_pipeline/01_build_pathway_atlas.R` — GSVA module scores, per-cohort limma, discovery/validation summaries (results/context_atlas_summary.csv).
2. `scripts/atlas_pipeline/08_xcell_deconvolution.R` + `09_fig_xcell_vs_marker.R` — composition scores and marker-proxy comparison.
3. `scripts/atlas_pipeline/03-07` — cBioPortal/TCGA retrieval, OS, driver stratification, meta.
4. `scripts/atlas_pipeline/02,11,12` — single-cell source validation and figure generation.
5. `scripts/v9_reruns/10_v9_joint_unified.R` → `20_v9_meta.R` → `21_rho_sensitivity.R` → `22_evidence_matrix.R` — v9 joint models, unified meta (empirical rho + 0.5/0.7 sensitivity), evidence matrix.
6. `scripts/v9_reruns/11_external_audit.R`, `12_ext_refined.R` — external-cohort identity/sample-count audits and refined OS models.
7. `scripts/v9_reruns/40_joint_heatmap.R`, `41-42` — v9 figures and legends.

Data: all primary data are public (GEO series; cBioPortal/TCGA; CPTAC; CELLxGENE; DepMap 24Q4; registry in `results/TableS1_accessions.csv` with origin-publication PMIDs). No raw data are redistributed here beyond small processed result tables.

## Manuscript status
Under review (internal v9). Latest manuscript, figures (PNG 300 dpi + PDF) and supplementary tables are maintained in the project working package; processed tables needed for the evidence matrix are mirrored in `results/`.

## License
MIT (code). Result tables derive from public data (see accession registry for original citations).

## Paths, configuration and reproducibility
- `config/gene_sets_extended.csv` contains the 17 module definitions used throughout.
- Scripts read GEO/cBioPortal processed objects via a `ROOTS` vector (three processed-data directories). Edit `ROOTS` at the top of each script to your local layout; the paths shipped are examples from the analysis machine.
- v10 corrected pipeline: `scripts/v10_reruns/10_v10_effects_joint.R` (metafor SMD/SMCRH effects + joint composition models, sample-ID joins, explicit control reference) -> `20_v10_meta.R` (metafor REML/Knha + DL + fixed-rho sensitivity + joint summary with per-layer inclusion) -> `12_v10_crc_external.R` (tissue filter, numeric stage, unadjusted/age/age+stage with CI) -> `22_v10_matrix.R` (evidence matrix) -> `30_v10_figures.R` (all figures).
- Verification checks: `tests/check_paired_effect.R` (hand calculation vs metafor SMCRH; sample-order shuffle with ID join; repeated-run stability). Run `Rscript tests/check_paired_effect.R` after adjusting `ROOTS`.

## Automated consistency check
`python tests/check_v11_consistency.py` verifies that every headline number in the manuscript matches the frozen v11 result tables, that no superseded numbers reappear, and that citations are sequential and fully cited. `Rscript tests/check_paired_effect.R` verifies the paired-effect implementation (hand calculation vs metafor, sample-order shuffle with ID joins, repeated runs).
