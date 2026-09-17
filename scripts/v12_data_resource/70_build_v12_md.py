#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the v12 Data Descriptor manuscript (numbers injected from the frozen v12 tables)."""
import csv, os, statistics
V12=r"C:\Users\fengq\Desktop\EGFR\EGFR的v12"
R=os.path.join(V12,"results"); OUTD=os.path.join(V12,"01_manuscript"); os.makedirs(OUTD,exist_ok=True)
def rd(p):
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def rdf(p):
    return rd(p) if os.path.exists(p) else []
reg=rdf(os.path.join(R,"v12_cohort_registry.csv"))
cov=rdf(os.path.join(R,"v12_gene_coverage.csv"))
sck=rdf(os.path.join(R,"v12_sc_dataset_audit.csv"))
scc=rdf(os.path.join(R,"v12_sc_comparisons.csv"))
esc_mut=rdf(os.path.join(R,"v12_escc_mutation_denominators.csv"))
esc_cna=rdf(os.path.join(R,"v12_escc_cna_summary.csv"))
esc_surv=rdf(os.path.join(R,"v12_escc_squamous_survival_cox.csv"))
n_cohorts=len(reg); n_assays=sum(int(r["n_assay_records"]) for r in reg); n_pat=sum(int(r["n_unique_patients"]) for r in reg)
plats=sorted({r["platform"] for r in reg if r["platform"]}); n_paired=sum(int(r["paired"]) for r in reg if r["paired"])
inc=[r for r in cov if int(r["n_present"])<int(r["n_members"])]
mod_min={}
for r in cov:
    m=r["module"]; c=float(r["coverage"])
    mod_min[m]=min(mod_min.get(m,1.0), c)
worst=sorted(mod_min.items(), key=lambda x: x[1])[:5]
sc_sig=[r for r in scc if r["fdr"] not in ("","NA") and float(r["fdr"])<0.05] if scc else []
sc_tests=sorted({r["test_used"] for r in scc}) if scc else []
not_testable=sum(1 for r in scc if r["test_used"]=="not testable")
paired_tests=sum(1 for r in scc if r["test_used"].startswith("wilcoxon")) if scc else 0
disjoint_tests=sum(1 for r in scc if "disjoint" in r["test_used"]) if scc else 0
esc_tp53=next((r for r in esc_mut if r["gene"]=="TP53"),None)
esc_egfr_cna=next((r for r in esc_cna if r["gene"]=="EGFR"),None)
esc_erbb2_cna=next((r for r in esc_cna if r["gene"]=="ERBB2"),None)
med_ratio="0.87"
title="A curated cross-disease transcriptomic resource with growth-factor and tissue-composition annotations"
assert len(title)<=110, len(title)

md=f"""# {title}

**Abstract**
We present a curated transcriptomic resource that reorganises public human tissue transcriptomes into a comparable, annotation-rich form for cross-disease reuse. The resource covers {n_cohorts} case-control expression cohorts spanning ten contexts (six cancers, four chronic benign diseases), with sample-level annotation (tissue type, case-control role, paired status, exclusion reason), harmonised gene mapping, 17 growth-factor signalling module definitions with per-platform coverage, module scores per sample, expression-derived tissue-composition scores with four aggregated compartments, and patient-level summaries derived from four single-cell datasets ({sum(int(r['donors']) for r in sck if r['arms']!='excluded') if sck else 0} donors). All {n_assays} assay records ({n_pat} unique patients) are traceable to their source series and origin publications; eligibility rules, exclusions and quality checks are recorded per sample. Scores are provided as per-cohort values with documented transformation provenance, and all cross-cohort comparisons are expressed as effect sizes rather than pooled values. The resource is deposited with a persistent identifier and includes runnable reuse examples, so that new gene sets, alternative composition-adjustment schemes or additional cohorts can be evaluated without repeating the data curation.

**Background & Summary**
Growth-factor and receptor-tyrosine-kinase (RTK) pathway modules are widely scored in bulk tumour transcriptomes, but a score computed in one cohort is rarely comparable with the same score computed in another: platforms differ in gene coverage, studies differ in tissue composition and case-control design, and processed matrices differ in transformation history. Reusers therefore commonly repeat the same curation work — locating comparable series, resolving sample identity and tissue type, mapping probes to gene symbols, deciding how to handle composition — before any new hypothesis can be tested.

This resource was built to remove that repeated curation and to make its own limitations explicit. Rather than reporting new biological conclusions, it provides: (i) a cohort registry with source series, platform, origin publication and download provenance; (ii) a sample annotation table with tissue type, case-control role, paired relations and documented exclusion reasons; (iii) harmonised expression matrices with a gene-mapping and transformation log; (iv) module definitions with per-platform coverage, so that a user can see which genes are actually represented in each cohort; (v) module scores per sample, labelled by scoring layer (bulk GSVA scores, member-mean z-scores, single-cell member-mean expression), which are not interchangeable across layers; (vi) expression-derived composition scores and four aggregated compartments; (vii) patient-level summaries from single-cell datasets, with raw and curated cell labels kept separate; and (viii) a complete estimates layer that includes non-significant and non-estimable results, together with the checks used to validate them.

**Methods**
*Cohort assembly.* Public case-control expression series were identified for ten contexts (lung adenocarcinoma, colorectal cancer, gastric cancer, pancreatic ductal adenocarcinoma, hepatocellular carcinoma, oesophageal squamous carcinoma, inflammatory bowel disease, chronic obstructive pulmonary disease, non-alcoholic fatty liver disease, asthma). Every series was required to contain both case and control samples measured on the same platform. {n_cohorts} cohorts met this requirement ({n_assays} assay records on {len(plats)} platform annotations; {n_pat} unique patients). Paired designs (tumour and adjacent tissue from the same patient) were identified from sample metadata in {n_paired} patients and recorded explicitly.
*Expression processing.* Within each cohort, probe identifiers were mapped to gene symbols using the platform annotation; multiple probes for one gene were collapsed by mean, ambiguous or unmappable probes were dropped, and legacy symbols were updated where an unambiguous current symbol existed. Matrices were log2-transformed when the input distribution indicated raw intensities; the decision rule and the outcome for every cohort are recorded in the transformation log. No cross-cohort matrix merging or batch correction was performed: values are comparable within a cohort, and across cohorts only through effect sizes.
*Module definitions and coverage.* Seventeen growth-factor pathway modules were defined a priori and frozen with a version identifier; membership is provided in full, together with the per-platform coverage table. Coverage is incomplete for several modules ({'; '.join(f'{m} (minimum coverage {c:.2f})' for m,c in worst)}), and users are expected to consult the coverage table before comparing a module across cohorts; a common-gene re-scoring option is provided for affected modules.
*Tissue-composition annotation.* Composition was estimated with xCell v1.1.0, which returns expression-derived enrichment scores rather than cell proportions. Scores are provided per sample, together with the four aggregated compartments (epithelial, fibroblast, endothelial, immune) and their construction rule. Agreement with a second deconvolution method is reported as method agreement only and is not used to claim proportion accuracy.
*Single-cell layers.* Four single-cell datasets contributed case-control contrasts: colorectal cancer (tumour versus non-tumour tissue; {next((r['donors'] for r in sck if r['context']=='CRC'),'')} donors), inflammatory bowel disease (disease versus healthy donors; {next((r['donors'] for r in sck if r['context']=='IBD'),'')} donors), gastric cancer (tumour versus adjacent tissue and versus non-pathological donors; {next((r['donors'] for r in sck if r['context']=='STAD'),'')} donors) and asthma (allergic asthma versus control; {next((r['donors'] for r in sck if r['context']=='ASTHMA'),'')} donors). One further dataset (lung adenocarcinoma, 117,266 cells) was reviewed and excluded because all cells come from tumour tissue and no control arm exists. Raw cell-type labels are preserved; curated labels and the mapping rules are provided separately. Cells annotated as malignant in non-tumour samples (358 cells) are flagged rather than reassigned. Comparisons use paired tests when at least five donors contribute both arms, unpaired tests only when the two arms are donor-disjoint, and are otherwise reported as not testable ({not_testable} such comparisons are recorded).
*TCGA-derived layer.* Tumour molecular data were reorganised for six cancer contexts. For the oesophageal context, the source study includes both adenocarcinoma and squamous carcinoma; the resource therefore restricts this layer to the {next((r['n_mutated_samples'] for r in esc_mut if r['gene']=='TP53'),'') }-patient squamous subset identified from patient-level histological annotation, and documents the exclusion of the adenocarcinoma samples. Mutation status is reported as 'mutation reported in the selected mutation data' or 'no mutation reported in the selected mutation data' only for samples present in the mutation-profiled sample list; samples outside that list are labelled not assayed/unknown.
*Quality control.* Checks cover sample identity and duplication, tissue-type and histology labels, paired relations, case-control labels, gene mapping and coverage, expression distributions and outlier samples (flagged, not removed), module score reproducibility across scoring implementations, and numerical reproduction of representative effect sizes by independent calculation.

**Data Records**
The dataset is deposited in Zenodo (DOI: [to be inserted after deposit]; GitHub-linked release) and is organised as ten top-level folders: (01) cohort registry and provenance; (02) sample annotation, including tissue type, case-control role, pairing and exclusion reasons; (03) harmonised expression matrices by cohort with the mapping and transformation log; (04) module definitions, per-platform coverage and sample-level scores; (05) composition scores and compartment definitions; (06) single-cell dataset audit, raw/curated label counts and patient-level summaries; (07) the complete estimates layer (per-cohort effects, meta-analytic summaries, composition models, driver interactions, external validation, single-cell comparisons), including non-significant and non-estimable results; (08) quality-control outputs; (09) runnable reuse examples with expected outputs; (10) environment and run order. Table 1 lists the cohorts with platform, assay and patient counts; Supplementary Table S1 lists module definitions and coverage; Supplementary Table S2 documents single-cell datasets and exclusions; Supplementary Table S3 lists every excluded sample with reason.

**Technical Validation**
Figure 1 summarises resource coverage. Across the {n_cohorts} cohorts, {n_assays} assay records map to {n_pat} unique patients, so cohort count should not be read as patient count; {n_paired} patients contribute paired tumour and adjacent samples. Module coverage is complete in most cohorts but incomplete for {len(set(r['module'] for r in inc))} of 17 modules in at least one cohort, with the largest gaps in {', '.join(m for m,_ in worst[:3])}; the coverage table exposes these gaps rather than hiding them behind a common score. Figure 2 reports the validation checks: sample-level exclusions are documented (89 adenocarcinoma samples excluded from the squamous oesophageal layer; 1,277 in utero cells excluded; 117,266 tumour-only cells from the excluded lung dataset; 358 malignant-labelled cells in non-tumour colorectal samples flagged), single-cell comparisons are labelled by test type ({paired_tests} paired by donor, {disjoint_tests} donor-disjoint unpaired, {not_testable} not testable), and representative effect sizes were reproduced by independent calculation, including after shuffling sample order. Mutation and copy-number prevalence for the squamous oesophageal subset are {esc_tp53['n_mutated_samples'] if esc_tp53 else ''}/{esc_tp53['denominator_n'] if esc_tp53 else ''} for TP53 ({esc_tp53['pct'] if esc_tp53 else ''}%) and {esc_egfr_cna['n_high_amp'] if esc_egfr_cna else ''}/{esc_egfr_cna['n_cna_profiled'] if esc_egfr_cna else ''} for EGFR high-level amplification ({esc_egfr_cna['pct_high_amp'] if esc_egfr_cna else ''}%), computed on mutation- and copy-number-profiled samples respectively. Module scores are expression-derived: they do not measure phosphorylation or pathway activity, and agreement with pathway databases or gene-perturbation resources is descriptive only.

**Usage Notes**
The resource supports at least three concrete reuse patterns, two of which are shipped as runnable examples: replacing the module gene sets and re-scoring cohorts, and recomputing composition adjustment under an alternative scheme. Users should note that (i) scores are comparable within a cohort and across cohorts only as effect sizes; (ii) module coverage must be checked before cross-cohort comparison, and the common-gene option should be used for modules with large coverage gaps; (iii) bulk GSVA scores, member-mean z-scores and single-cell member-mean values are different quantities and must not be concatenated; (iv) composition scores are enrichment scores, not proportions; (v) the same disease label across layers does not imply the same patients, and the resource is not a patient-level multi-omics resource; (vi) the module scores are not validated prognostic tools, and the included survival and driver analyses are exploratory and reported in full, including negative results.

**Data Availability**
All source data are public and are listed with accessions and origin publications in the cohort registry (Table 1). The curated resource described here is deposited in Zenodo under a CC-BY-4.0 licence (DOI: [to be inserted after deposit]); the corresponding code release is archived with a DOI and the development repository is at https://github.com/sushuqiong/egfr-pathway-context-atlas. No new human specimens were collected; new derived data (annotations, scores, quality-control records and estimates) were generated and are included in the deposit.

**Code Availability**
Analysis code, the frozen configuration (module definitions), the run order, and the reuse examples are provided in the GitHub repository and archived in the Zenodo deposit; software versions are recorded in the environment folder.

**Ethics statement**
This work uses only publicly available, de-identified data; no ethical approval or informed consent was required.

**Author Contributions**
S.S. designed the resource, curated the cohorts and sample annotations, implemented the analysis and quality-control pipeline, and wrote the manuscript.

**Competing Interests**
The author declares no competing interests.

**Acknowledgements and Funding**
The author thanks the authors of the source studies and the data providers (GEO, TCGA/GDC, CELLxGENE) whose public data made this resource possible. No specific funding was received for this work.
"""
p=os.path.join(OUTD,"DataDescriptor_v12.md"); open(p,"w",encoding="utf-8").write(md)
print("written:",p)
print("title chars:",len(title))
import re
ab=re.search(r"\*\*Abstract\*\*(.*?)\*\*Background", md, re.S).group(1)
print("abstract words:",len(re.findall(r"\S+",ab)))
print("cohorts:",n_cohorts,"assays:",n_assays,"patients:",n_pat,"paired:",n_paired,"platforms:",len(plats))
print("modules with any coverage gap:",len(set(r['module'] for r in inc)),"| worst:",worst[:3])
print("sc: sig",len(sc_sig),"| paired",paired_tests,"| disjoint",disjoint_tests,"| not testable",not_testable,"| tests",sc_tests)
