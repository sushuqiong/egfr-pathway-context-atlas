# Provenance of the tables in 07_estimates

| File | Produced by | Basis | Affected by the metadata-driven pairing correction? |
|---|---|---|---|
| per_cohort_effects.csv | v13 (script 80 + 41) | 26 case-control cohorts, 442 rows = 434 estimated + 8 not estimable | yes - it is the corrected version |
| not_estimable_pairs.csv | v13 (script 80) | membership/variance checks | yes |
| meta_primary_reml_knha.csv, meta_dersimonian_laird.csv, meta_adhoc_knapp_hartung.csv, meta_unpaired_only.csv, meta_rho0.5/rho0.7 | v12 (script 41) | pooled from the corrected per-cohort effects | yes - already recomputed after the pairing correction |
| composition_model_summary.csv | v11 joint layer | base versus adjusted models on identical samples | no - the composition models do not use the paired/unpaired classification, and the cohort set is unchanged |
| driver_interactions.csv, driver_eligibility.csv | v11 | TCGA driver stratification | no - TCGA layer, not cohort pairing |
| external_validation_crc.csv | v11 | independent colorectal series (GSE39582), analysed unpaired | no - the series has no paired design |
| tcga_escc_squamous_*.csv | v12 (scripts 11/12) | squamous oesophageal subset, 96 patients (94 with survival data) | no - TCGA layer |
| per_state_evidence_matrix.csv | v11 | state-level summary of per-cohort evidence | partially - it summarises effects that were corrected for three cohorts; where a state depends on those cohorts, the corrected per-cohort table supersedes it |
