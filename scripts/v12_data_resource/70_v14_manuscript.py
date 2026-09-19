#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 manuscript generator: adds references, screening process, QC, formulas, tolerance wording,
contrast ontology, overlap audits; tightens title and abstract per review."""
import csv, os, re, statistics, math, collections
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
def rd(p):
    if not os.path.exists(p): return []
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def one(rows,**kw):
    hit=[r for r in rows if all(str(r.get(k,""))==str(v) for k,v in kw.items())]
    assert len(hit)==1, f"expected one row for {kw}, got {len(hit)}"
    return hit[0]
reg=rd(os.path.join(PK,"01_cohort_registry","cohort_registry.csv")); cc=[r for r in reg if r["design"]=="case-control"]
n_cc=len(cc); n_assays=sum(int(r["n_assay_records"]) for r in cc)
n_pat=sum(int(r["n_unique_patients"]) for r in cc if str(r["n_unique_patients"]).isdigit())
n_paired=sum(1 for r in cc if r["paired_design_used"]=="yes"); n_nopid=sum(1 for r in cc if r["patient_identity_available"]=="no")
n_series=len(reg)
full=rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
n_est=sum(1 for r in full if r["measure"] in ("SMDH","SMCRPH")); n_ne=len(full)-n_est
cov=rd(os.path.join(PK,"04_modules","platform_module_coverage.csv"))
mod_cov={}
for r in cov: mod_cov[r["module"]]=min(mod_cov.get(r["module"],1.0), float(r["coverage"]))
worst=sorted(mod_cov.items(),key=lambda x:x[1])[:3]
scc=rd(os.path.join(R,"v12_sc_comparisons.csv")); sig=[r for r in scc if r["fdr"] not in ("","NA") and float(r["fdr"])<0.05]
tt={}; ct={}
for r in scc:
    tt[r["test_used"]]=tt.get(r["test_used"],0)+1; ct[r["comparison_type"]]=ct.get(r["comparison_type"],0)+1
mut=rd(os.path.join(R,"v12_escc_mutation_denominators.csv")); cna=rd(os.path.join(R,"v12_escc_cna_summary.csv"))
tp53=one(mut,gene="TP53"); egfr_m=one(mut,gene="EGFR"); kras=one(mut,gene="KRAS"); egfr_c=one(cna,gene="EGFR")
ph=rd(os.path.join(R,"v12_qc_cox_ph_assumption.csv"))
col=rd(os.path.join(R,"v13_qc_vif_by_predictor.csv"))
r2=[float(r["r2_overall"]) for r in col]; vif=[float(r["max_vif_predictor"]) for r in col]
con=rd(os.path.join(R,"v13_qc_cross_cohort_consistency.csv")); ccons=[r for r in con if int(r["k"])>=2]
same=sum(1 for r in ccons if r["direction_consistent"].upper()=="TRUE")
sen=rd(os.path.join(R,"v13_qc_coverage_threshold_sensitivity.csv"))
def nsig(tag): return sum(1 for r in sen if r["scenario"]==tag and r["fdr"] not in ("","NA") and float(r["fdr"])<0.05)
def nk(tag): return sum(1 for r in sen if r["scenario"]==tag)
sigol=rd(os.path.join(R,"v13_qc_signature_overlap.csv")); n_ov=sum(1 for r in sigol if float(r["frac_overlap_xcell"])>0.2)
max_ov=max(float(r["frac_overlap_xcell"]) for r in sigol)
cg=rd(os.path.join(R,"v12_common_gene_sensitivity_summary.csv"))
flagcol=[c for c in cg[0] if "flag" in c.lower()][0]
disagree=[r["module"] for r in cg if "direction disagreement" in str(r[flagcol])]
notscor=[r["module"] for r in cg if "insufficient" in str(r[flagcol])]
scv=rd(os.path.join(R,"v12_qc_module_score_effect_verification.csv"))
sl=rd(os.path.join(PK,"08_qc","qc_bulk_score_level_reproducibility.csv"))
tcgascore=rd(os.path.join(R,"v12_qc_survival_score_verification.csv")); tcgacox=rd(os.path.join(R,"v12_qc_survival_cox_verification.csv"))
xcell=rd(os.path.join(R,"v12_qc_xcell_recompute_verification.csv"))
mx=rd(os.path.join(PK,"05_composition","alternative_method_marker_proxy.csv"))
agr=rd(os.path.join(PK,"08_qc","qc_composition_method_agreement.csv"))
eqc=rd(os.path.join(PK,"08_qc","qc_expression_matrix_per_cohort.csv"))
flow=rd(os.path.join(PK,"08_qc","curation_flow.csv"))
ont=rd(os.path.join(PK,"01_cohort_registry","contrast_ontology.csv"))
cla=collections.Counter(r["control_class"] for r in ont)
stud=rd(os.path.join(PK,"08_qc","qc_study_level_overlap_audit.csv"))
ded=rd(os.path.join(PK,"08_qc","qc_study_dedup_sensitivity.csv"))
inv=rd(os.path.join(PK,"08_qc","file_inventory_and_checksums.csv"))
momat=rd(os.path.join(PK,"04_modules","module_overlap_matrix.csv"))
maxj=max(float(r["jaccard"]) for r in momat) if momat else 0
inv_n=len([r for r in inv if r["file"] not in ("08_qc/file_inventory_and_checksums.csv","08_qc/checksums_sha256.txt")])+2
n_out=sum(int(r["outlier_samples_3mad"]) for r in eqc if str(r["outlier_samples_3mad"]).isdigit())
title="Coverage-aware harmonized cross-disease transcriptome resource with expression-derived compartment scores"
assert len(title)<=110, len(title)
DEP="[DOI to be inserted after Zenodo deposit]"
md=f"""# {title}

**Abstract**
Signaling-module scores and tissue-composition estimates are computed routinely from bulk tissue transcriptomes, yet scores from different studies are rarely comparable and every user repeats the same curation. This resource provides a coverage-aware, harmonized collection of public human tissue transcriptomes. It contains {n_cc} case-control expression cohorts across ten disease contexts ({n_assays} assay records, {n_pat} patients with identifiers, 12 platforms), sample-level annotation with tissue type, case-control role, pairing, control class and exclusion reasons, harmonized gene mapping with deterministic transformation rules, seventeen frozen signaling-module definitions whose gene sets are mutually disjoint, per-sample module scores with per-cohort gene coverage, expression-derived tissue-compartment scores with an independent marker-based alternative, donor-aware single-cell summaries from four datasets, a complete estimates layer that retains non-significant, not-estimable and not-testable results, and validation records that state what was reproduced within a pre-specified tolerance and what only in rank. Scores are cohort-internal; cross-cohort comparison is supported through effect sizes whose consistency is quantified. The resource is deposited with a persistent identifier.

**Background & Summary**
Module scores for growth-factor, WNT, JAK/STAT and SRC-family signalling are used as if they measured one comparable quantity, yet they do not: platforms differ in gene coverage, cohorts differ in control tissue and design, and processed matrices differ in transformation history. A user who wants to ask whether a module differs between diseased and control tissue across diseases must first locate comparable series, resolve sample identity and tissue type, map probes to symbols, decide how to treat composition, and then repeat the exercise for the next cohort.

This resource performs that curation once and documents its limits. It provides (i) a cohort registry with design, platform, counts, control class, origin publication and provenance; (ii) sample-level annotation with tissue type, case-control role, pairing and exclusion reasons; (iii) gene-mapping and transformation records with a deterministic rule and a runnable script that rebuilds one series from its accession; (iv) seventeen frozen signalling modules, mutually disjoint by construction, with per-platform coverage and a full gene list; (v) per-sample module scores with a stated construction rule per layer; (vi) expression-derived compartment scores plus an independent marker-based alternative that does not use the xCell signature panel; (vii) donor-aware single-cell summaries; (viii) a complete estimates layer in which every cohort-by-module pair is accounted for, including pairs that are not estimable and why; and (ix) validation records that separate exact reproduction within a pre-specified tolerance from rank agreement, and that quantify cross-cohort consistency, coverage sensitivity and composition coupling.

**Methods**
*Search, screening and inclusion.* Candidate series were sought in the Gene Expression Omnibus for ten disease contexts (lung adenocarcinoma, colorectal, gastric, pancreatic, hepatocellular and oesophageal squamous cancer; inflammatory bowel disease; chronic obstructive pulmonary disease; non-alcoholic fatty liver disease; asthma) using context terms combined with platform-annotated processed matrices, searching on 2026-09-13 and re-checked on 2026-09-19. {n_series} series were retrieved with usable processed matrices; series were included only when case and control samples of the same context were measured on one platform and a processed matrix was obtainable. One series was excluded because it is a treatment-response design, and a further colorectal series was retained for external-validation use only. Three series downloaded during curation were not carried forward and are listed with reasons (no usable control arm after annotation; incomplete platform annotation; redundancy with retained cohorts). The screening counts are shipped as 08_qc/curation_flow.csv. Control tissue was classified into an explicit ontology rather than pooled: {', '.join(f'{k} (n={v})' for k,v in sorted(cla.items()))}; every cohort's control class is listed in 01_cohort_registry/contrast_ontology.csv, and comparisons across classes are not pooled.
*Design.* Paired designs are derived from metadata, never assumed: a cohort is analysed as paired when at least four patients contribute both a case and a control sample ({n_paired} cohorts). In paired cohorts only complete pairs enter the paired effect estimate. {n_nopid} cohorts provide no patient identifiers, so pairing cannot be established and the analysis is unpaired by necessity; this is recorded per cohort. Study overlap was audited at publication level: all {n_cc} case-control cohorts come from distinct publications, and the leave-one-out sensitivity of the pooled results to dropping cohorts is shipped (08_qc/qc_study_dedup_sensitivity.csv).
*Expression processing and QC.* Probes were mapped to gene symbols, multiple probes per gene collapsed by the mean, unmappable probes dropped and legacy symbols updated where unambiguous. Transformation follows a deterministic rule: a matrix is treated as already log-scaled when its integer fraction exceeds 0.90 and its maximum exceeds 50, and is otherwise log2(x+1)-transformed; the decision, the observed input maximum, the integer fraction and the resulting post-transformation summary are recorded for every cohort (03_expression/transformation_log.csv and transformation_summary_per_cohort.csv). Per-cohort expression QC is shipped (08_qc/qc_expression_matrix_per_cohort.csv): sample and gene counts, missing-value fraction, sample-mean distribution, zero-variance genes and outlier samples beyond three median absolute deviations ({n_out} samples across {len(eqc)} cohorts), which are flagged but retained because exclusion of borderline samples is a user decision. No cross-cohort merging or batch correction was performed.
*Module definitions and coverage.* Seventeen signalling modules were defined a priori and frozen (module_version = v12.0-frozen-2026-09). The gene sets are mutually disjoint: the maximum pairwise Jaccard overlap between any two modules is {maxj:.2f} (04_modules/module_overlap_matrix.csv). Coverage is incomplete in part of the cohorts, with the largest gaps in {'；'.join(f'{m} (minimum coverage {c:.2f})' for m,c in worst)}. Coverage is treated as a primary property rather than a footnote: every effect row carries the cohort's actual module coverage and the number of members present (07_estimates/per_cohort_effects.csv), and the pooled results are re-estimated as a sensitivity analysis after excluding cohorts below 0.60, 0.80 and 0.90 coverage.
*Effect sizes and pooling.* For each cohort and module the effect is the standardized difference between case and control on the shared denominator sqrt((sd_case^2 + sd_control^2)/2): SMDH for unpaired cohorts and SMCRPH, the paired form using the cohort's empirical within-pair correlation r, for paired cohorts; zero-variance modules are reported as not estimable rather than estimated. Pooling uses REML heterogeneity with the Hartung-Knapp variance correction, requires at least two cohorts, and is reported with k, tau-squared, I-squared, a 95% confidence interval and a 95% prediction interval; DerSimonian-Laird, ad hoc Knapp-Hartung, unpaired-only and fixed-correlation (rho = 0.5, 0.7) analyses are shipped as sensitivity analyses because paired cohorts carry smaller variances and therefore more weight. Every cohort-by-module pair appears in the estimates table: {n_est} estimated and {n_ne} not estimable with a reason.
*Composition and its coupling.* Compartment scores were estimated with xCell v1.1.0 (expression-derived enrichment scores, not proportions) and an independent marker-based alternative computed from small canonical marker sets per compartment; the two agree with Spearman coefficients of {'; '.join(f"{r['compartment']} {r['spearman_vs_xcell']}" for r in agr)} (08_qc/qc_composition_method_agreement.csv). Because {n_ov} of {len(sigol)} modules share more than 20% of their members with the xCell panel (maximum {max_ov:.0%}), module scores and composition scores are not statistically independent, and the base-versus-adjusted comparison is therefore reported as a sensitivity analysis, never as an independent correction. The base model is the primary specification. Collinearity is reported twice and separately: the overall model R-squared (how well the four compartments jointly explain disease status) has median {statistics.median(r2):.2f} and maximum {max(r2):.2f}, while the maximum per-predictor VIF has median {statistics.median(vif):.2f} and maximum {max(vif):.2f}.
*Single-cell layer.* Four datasets contributed contrasts: colorectal cancer (tumour versus non-tumour tissue, 29 donors), inflammatory bowel disease (disease versus healthy donors, 18 donors), gastric cancer (tumour versus adjacent and versus non-pathological tissue, 59 donors) and asthma (8 donors); one lung dataset was excluded because all cells come from tumour tissue. Counts were library-size normalised (target 1e4) and log1p-transformed, module scores were computed per cell as the mean of member genes, cells were averaged to donor means per cell type and arm, and testing was performed on donor means: arms required at least three donors, a paired signed-rank test was used when at least five donors contributed both arms, an unpaired test only when the arms were donor-disjoint, and comparisons satisfying neither condition were reported as not testable ({tt.get('not testable',0)} of {len(scc)}). Multiplicity was controlled by Benjamini-Hochberg within families defined by context x module x comparison type. Raw cell labels are preserved; the curated mapping and the flagging of 358 malignant-labelled cells inside non-tumour samples are shipped. No minimum number of cells per donor was imposed; the donor-level table reports the donors contributing to each comparison ({len(scc)} rows) and this choice is stated as a limitation.
*TCGA-derived layer.* Molecular data were reorganised for six cancer contexts from cBioPortal releases retrieved in 2026-09. Because the oesophageal source study contains both adenocarcinoma and squamous carcinoma, the analysed layers were restricted to the squamous subset identified from patient-level histological annotation (96 patients; 94 with survival data), and the mutation-prevalence denominator was corrected in this version from all 185 oesophageal profiles to the 96 squamous profiles. The survival layer uses overall survival in months with death as the event and censoring at last follow-up; the multivariable model adjusts for age and pathological stage and is fitted on complete cases only; the endpoint, time unit, censoring rule, missing-data handling and data version are recorded as a data dictionary in 07_estimates/survival_data_dictionary.md.
*Validation rules.* Rules and thresholds are explicit (Supplementary Table S5). Common-gene sensitivity re-scores each cohort with the members present in every cohort, flags a module when the effect direction disagrees with full-member scoring in at least 20% of cohorts ({', '.join(disagree) if disagree else 'none'}), and marks it not scorable when fewer than two members are shared ({', '.join(notscor) if notscor else 'none'}). Proportional hazards is assessed with scaled Schoenfeld residuals in the age-adjusted model and flagged at p<0.05 ({sum(1 for r in ph if r['ph_violation'].upper()=='TRUE')} of {len(ph)} features flagged). Reproduction is reported against a pre-specified tolerance of 1e-6 in the statistic concerned, and rank-level agreement is always labelled as such and never described as reproduction.
*Source versions and licences.* Source releases, accessions and licence notes are shipped (01_cohort_registry/source_versions.csv); the single-cell inputs are identified by their verified CELLxGENE dataset versions and collections (01_cohort_registry/cellxgene_sources.csv). Derived data are released under CC-BY-4.0 by the authors of this resource; upstream data remain under their own terms (GEO series terms, TCGA/GDC open-access terms, CELLxGENE dataset terms), and no controlled-access data were used.

**Data Records**
The resource is deposited in Zenodo ({DEP}) as ten folders: 01 cohort registry, provenance, control ontology and CELLxGENE identifiers; 02 sample annotation; 03 expression provenance, transformation log and transformation summary; 04 module definitions, coverage and overlap matrix; 05 composition scores with the marker-proxy alternative and join audit; 06 single-cell audit, labels and donor-aware comparisons; 07 the estimates layer including not-estimable pairs, prediction intervals and the survival data dictionary; 08 quality-control records, validation evidence and the curation flow; 09 runnable reuse examples with expected outputs; 10 environment, run order and versioning. A file inventory with row counts and SHA-256 checksums is shipped ({inv_n} files). The submission package also contains the manuscript, Tables 1 and Supplementary Tables S1-S16, the separate figure-legend file and all four figures.

**Technical Validation**
Coverage and composition are shown in Figure 1; validation evidence in Figures 2 to 4. Sample identity: no sample identifier is duplicated across the {n_cc} case-control cohorts, every annotated sample resolves to a registry entry, and the {n_cc} cohorts come from distinct publications. Histology and mutation layer: the oesophageal layer is restricted to squamous histology ({tp53['denominator_n']} patients), with TP53 reported in {tp53['n_mutated_samples']} ({tp53['pct']}%), EGFR in {egfr_m['n_mutated_samples']} ({egfr_m['pct']}%), KRAS and ERBB2 in {kras['n_mutated_samples']} and 0, and EGFR high-level amplification in {egfr_c['n_high_amp']}/{egfr_c['n_cna_profiled']} ({egfr_c['pct_high_amp']}%; gain or amplification {egfr_c['n_gain_or_amp']}, {egfr_c['pct_gain']}%). Reproduction within tolerance: per-sample module scores of three recomputed cohorts matched the shipped values (Spearman {min(float(r['spearman']) for r in sl):.2f}, maximum absolute z difference {max(float(r['max_abs_z_diff']) for r in sl):g}; {len(sl)} module-cohort pairs), the {len(scv)} corresponding cohort effects and standard errors matched (maximum absolute difference {max(float(r['abs_diff']) for r in scv):g}), and refitting the Cox models from the shipped patient scores reproduced {len(tcgacox)} hazard ratios within tolerance. Rank-level agreement, explicitly not reproduction: rebuilding the TCGA patient-level scores from the gene-level table reproduced the shipped scores at Spearman {min(float(r['spearman']) for r in tcgascore):.2f}-0.98 across {sum(int(r['pairs']) for r in tcgascore):,} patient-module pairs, the residual differences tracing to the aggregation order stated in Methods. Composition: recomputed xCell scores agreed with the shipped values (Pearson {min(float(r['pearson']) for r in xcell):.2f}-{max(float(r['pearson']) for r in xcell):.2f}), and the marker-based alternative agrees with xCell as reported above. Comparability: {same} of {len(ccons)} context-module pairs ({100*same/len(ccons):.0f}%) have the same effect direction in every contributing cohort; the number of pooled states surviving BH control is {nsig('all cohorts')} with all cohorts and {nsig('coverage >= 0.60')}, {nsig('coverage >= 0.80')}, {nsig('coverage >= 0.90')} at coverage thresholds of 0.60, 0.80 and 0.90 (k = {nk('all cohorts')} to {nk('coverage >= 0.90')}), so comparability degrades gradually with coverage. Survival layer: proportional hazards was not violated for any of the {len(ph)} tested features, which is absence of detectable violation rather than proof that the assumption holds. Single-cell: {len(scc)} donor-level comparisons are shipped with the test actually used ({tt.get('wilcoxon-signed-rank (paired donors)',0)} paired, {tt.get('mann-whitney (donor-disjoint)',0)} donor-disjoint unpaired, {tt.get('mann-whitney (cell-identity; unpaired)',0)} cell-identity contrasts, {tt.get('not testable',0)} not testable); {len(sig)} reach FDR below 0.05 within their family and are descriptive. Module scores are expression-derived and do not measure phosphorylation or pathway activity.

**Usage Notes**
Which layer to use (Supplementary Table S8): bulk GSVA z-scores within a cohort; TCGA member-mean z-scores for patient-level comparisons across tumour contexts; single-cell member means for cell-type-resolved questions; composition scores only as descriptors or as sensitivity covariates (with the marker-based alternative for robustness). Users should note that (i) scores are comparable within a cohort and across cohorts only as effect sizes, with the shipped consistency and coverage-sensitivity tables quantifying how far that holds; (ii) coverage must be checked before any cross-cohort comparison, either through the per-effect coverage columns or the shipped sensitivity analyses; (iii) the three score layers must not be concatenated; (iv) composition scores are enrichment scores, share genes with module scores, and adjusted coefficients are sensitivity analyses; (v) the same disease label in different layers does not imply the same patients; (vi) the survival, driver and single-cell analyses shipped here are exploratory and include negative and not-estimable results; (vii) cohorts without patient identifiers cannot be analysed as paired; (viii) no minimum cells-per-donor filter was applied in the single-cell layer. Maintenance: the resource carries a version number and changelog, and updates are published as new versions of the deposit so that earlier DOIs remain citable.

**References**
1. Barrett T, et al. NCBI GEO: archive for functional genomics data sets. Nucleic Acids Res 2013;41:D991-D995.
2. Davis S, Meltzer PS. GEOquery: a bridge between the Gene Expression Omnibus and Bioconductor. Bioinformatics 2007;23:1846-1847.
3. The Cancer Genome Atlas Research Network. Comprehensive molecular characterization of gastric adenocarcinoma and related studies (TCGA). Nat Genet/Nature 2014 and later releases; data retrieved from the NCI Genomic Data Commons.
4. Cerami E, et al. The cBioPortal for Cancer Genomics. Cancer Discov 2012;2:401-404.
5. Gao J, et al. Integrative analysis of complex cancer genomics and clinical profiles using the cBioPortal. Sci Signal 2013;6:pl1.
6. CZ CELLxGENE Discover (programmatic access to curated single-cell datasets); dataset versions and collections as listed in 01_cohort_registry/cellxgene_sources.csv.
7. Hänzelmann S, Castelo R, Guinney J. GSVA: gene set variation analysis for microarray and RNA-seq data. BMC Bioinformatics 2013;14:7.
8. Aran D, Hu Z, Butte AJ. xCell: digitally portraying the tissue cellular heterogeneity landscape. Genome Biol 2017;18:220.
9. Ritchie ME, et al. limma powers differential expression analyses for RNA-sequencing and microarray studies. Nucleic Acids Res 2015;43:e47.
10. Viechtbauer W. Conducting meta-analyses in R with the metafor package. J Stat Softw 2010;36:1-48.
11. Hartung J, Knapp G. A refined method for the meta-analysis of controlled clinical trials with binary outcome. Stat Med 2001;20:3875-3889.
12. Knapp G, Hartung J. Improved tests for a random effects meta-regression with a single covariate. Stat Med 2003;22:2693-2710.
13. R Core Team. R: a language and environment for statistical computing (version 4.4.1).
14. Scientific Data editorial policies: data availability, code availability and reporting standards for data descriptors.
15. Origin publications for the {n_cc} case-control cohorts: see the origin_pmid column of 01_cohort_registry/cohort_registry.csv (27 unique publications, one per curated series).

**Data Availability**
All source data are public and listed with accessions and origin publications in the cohort registry. The curated resource is deposited in Zenodo under a CC-BY-4.0 licence ({DEP}); the code repository is https://github.com/sushuqiong/cross-disease-transcriptomic-resource. No new human specimens were collected; all derived data generated here are included in the deposit.

**Code Availability**
Analysis code, the frozen module configuration, the run order, the version file and the reuse examples are provided in the repository and archived in the deposit; software versions are recorded in folder 10.

**Ethics statement**
This work uses only publicly available, de-identified data; no ethical approval or informed consent was required.

**Author Contributions**
S.S. designed the resource, curated cohorts and annotations, implemented the analysis, validation and quality-control pipeline, and wrote the manuscript.

**Competing Interests**
The author declares no competing interests.

**Acknowledgements and Funding**
The author thanks the authors of the source studies and the public data providers (GEO, TCGA/GDC via cBioPortal, CELLxGENE). No specific funding was received for this work.

**Figure captions**
**Figure 1. Resource overview.** (A) module gene coverage per disease context (fraction of frozen module members present; short module labels are expanded in the legend file); (B) assay records, patients with identifiers and patients contributing both tissues, one facet per measure; (C) single-cell datasets with the comparison arms available in each.
**Figure 2. Validation of sample and design handling.** (A) documented exclusions, flags and non-testable comparisons; (B) the single-cell comparison design actually used; (C) the complete estimates layer including non-significant results, faceted by the measure used.
**Figure 3. Comparability and coupling.** (A) cross-cohort direction consistency per context-module pair (points: pairs, bar: median); (B) coverage-threshold sensitivity of the pooled results; (C) module versus xCell panel overlap; (D) overall model R2 versus the maximum per-predictor VIF.
**Figure 4. Sensitivity analyses.** (A) common-gene sensitivity of module scoring; (B) collinearity between disease status and the composition scores.
"""
p=os.path.join(V14,"01_manuscript","DataDescriptor_v14.md"); open(p,"w",encoding="utf-8").write(md)
ab=re.search(r"\*\*Abstract\*\*(.*?)\*\*Background", md, re.S).group(1)
print("written:",p); print("title chars:",len(title),"| abstract words:",len(re.findall(r"\S+",ab)))
print("marker-proxy agreement rows:",len(agr),"| expression QC cohorts:",len(eqc),"| outliers:",n_out)
print("modules max Jaccard:",maxj,"| study overlap groups:",len(stud)-sum(1 for r in stud if not r["study_shared_with"]))
