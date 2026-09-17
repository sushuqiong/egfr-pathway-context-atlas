# Cross-disease growth-factor and tissue-composition transcriptomic resource (v12)

**Licence**
- Derivative data in this package (annotations, scores, coverage tables, estimates, quality-control records): **CC-BY-4.0**.
- Code: MIT (see the GitHub repository).
- Upstream data remain under the terms of their original repositories (GEO, TCGA/GDC via cBioPortal, CELLxGENE). Accessions and origin publications are listed in `01_cohort_registry/`.

**How to cite**
Cite the Data Descriptor (DOI to be inserted after deposit) and the dataset DOI (Zenodo). Cite the primary sources listed in `01_cohort_registry/` for the underlying measurements.

## What is in the package

| Folder | Contents | Key files |
|---|---|---|
| 01_cohort_registry | cohort registry and provenance | `v12_cohort_registry.csv`, `TableS1_accessions.csv`, `TableS1b_cohort_pubmed_map.csv` |
| 02_sample_annotation | sample-level annotation for the GEO cohorts and the squamous oesophageal TCGA subset | `sample_annotation_geo_cohorts.csv`, `sample_annotation_escc_squamous_tcga.csv` |
| 03_expression | gene-mapping and transformation provenance (processed matrices are regenerated from the public accessions listed in 01) | `transformation_log.csv` |
| 04_modules | frozen module definitions, per-platform coverage, sample-level scores | `module_definitions.csv`, `platform_module_coverage.csv`, `sample_module_scores_gsva_z.csv` |
| 05_composition | expression-derived composition scores | `xcell_composition_scores.csv` |
| 06_single_cell | dataset audit, raw/curated label notes, donor-aware comparisons | `single_cell_dataset_audit.csv`, `single_cell_comparisons.csv` |
| 07_estimates | complete estimates layer, including non-significant and non-estimable results | `per_cohort_effects.csv`, `meta_*.csv`, `composition_model_summary.csv`, `driver_interactions.csv`, `external_validation_crc.csv`, `tcga_escc_squamous_*.csv` |
| 08_qc | coverage gaps, exclusions and layout checks | `module_coverage_gaps.csv`, `exclusion_and_flag_log.csv`, `figure_layout_qa.csv` |
| 09_reuse_examples | two runnable reuse examples with expected outputs | `example1_replace_module_gene_set.R`, `example2_recompute_composition_scheme.R` |
| 10_environment | software versions and run order | `environment.txt`, `run_order.md` |

## Field dictionary (main tables)

`02_sample_annotation/sample_annotation_geo_cohorts.csv`
| field | meaning |
|---|---|
| accession | GEO series accession |
| sample_id | within-cohort sample identifier (GSM) |
| patient_id | patient identifier; equals `sample_id` when the source provides no separate patient field |
| group | source case/control label as recorded in the processed series |
| case_control_role | normalised role (`case`, `control`, `unknown`) |
| paired_with | `patient_id\|paired` when the patient contributes both case and control samples |
| platform | platform annotation of the series |

`04_modules/sample_module_scores_gsva_z.csv`
| field | meaning |
|---|---|
| accession, sample_id | join keys to the annotation table |
| <module names> | GSVA scores computed within the cohort and z-scored **within that cohort**. Values are comparable within a cohort; across cohorts use `07_estimates/per_cohort_effects.csv` (standardized effect sizes) |

`06_single_cell/single_cell_comparisons.csv`
| field | meaning |
|---|---|
| context, module, cell_type | dataset, module and cell type compared |
| comparison_type | `tumour-vs-adjacent`, `tumour-vs-healthy`, `case-vs-healthy` or `cell-identity` |
| n_donors_a, n_donors_b, n_overlap_donors, n_pairs | donors per arm, donors present in both arms, complete pairs used |
| test_used | `wilcoxon-signed-rank (paired donors)`, `mann-whitney (donor-disjoint)` or `not testable` |
| p_used, fdr | p-value and BH-FDR within the context x module x comparison-type family |

`07_estimates/per_cohort_effects.csv`
| field | meaning |
|---|---|
| measure | `SMDH` (unpaired) or `SMCRPH` (paired, empirical within-pair correlation); both use the root-mean-variance denominator |
| yi, vi | standardized effect and its sampling variance |
| beta_base, beta_adj, se_*, p_* | disease coefficients from the composition **base** and **adjusted** models on identical samples |
| r_emp, npair | empirical within-pair correlation and number of pairs (paired cohorts) |

## Scoring layers are not interchangeable
- bulk GSVA z-scores (`04_modules`) — cohort-internal
- member-mean z-scores (TCGA layer, `07_estimates`)
- single-cell member-mean expression (`06_single_cell`)
These are different quantities and must not be concatenated into one matrix.

## What is deliberately excluded
See `08_qc/exclusion_and_flag_log.csv`: 89 adenocarcinoma samples excluded from the squamous oesophageal layer; 1,277 in utero cells excluded; a tumour-only single-cell dataset (117,266 cells) excluded for having no control arm; 358 malignant-labelled cells in non-tumour colorectal samples flagged but not reassigned; 80 single-cell comparisons reported as not testable because donors overlap between arms without forming five complete pairs.

## Known limitations
Module gene coverage is incomplete in part of the cohorts (worst case: RET/ALK/NTRK modules down to 33% of members in one platform). Composition scores are enrichment scores, not cell proportions. Cohort count is not patient count (27 cohorts, 1,138 unique patients). The resource is not a patient-level multi-omics resource: the same disease label in different layers does not imply the same patients. Module scores are not validated prognostic or predictive tools.
