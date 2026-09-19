#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 fix pass 2 (manuscript): numbered in-text citations, input-data subsection with accessions,
corrected screening wording, defined abbreviations with effect-size and variance formulas, section order,
half-width punctuation, US spelling, compressed Usage Notes, limitations, file count from the inventory."""
import os, csv
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; PK=os.path.join(V14,"dataset_package")
p=os.path.join(V14,"scripts","70_v14_manuscript.py"); s=open(p,encoding="utf-8").read()
def rep(old,new,label):
    global s
    assert old in s, f"anchor missing: {label}"
    s=s.replace(old,new,1); print("patched:",label)
# 0. inventory-derived file counts
rep("inv=rd(os.path.join(PK,\"08_qc\",\"file_inventory_and_checksums.csv\"))",
    "inv=rd(os.path.join(PK,\"08_qc\",\"file_inventory_and_checksums.csv\"))\n"
    "n_files=len([r for r in inv if r[\"file\"] not in (\"08_qc/file_inventory_and_checksums.csv\",\"08_qc/checksums_sha256.txt\")])+2\n"
    "n_checks=len(inv)-2","file counts")
rep('inv_n=len([r for r in inv if r["file"] not in ("08_qc/file_inventory_and_checksums.csv","08_qc/checksums_sha256.txt")])+2',
    'inv_n=n_files','inv_n reuse')
# 1. citations in Methods and elsewhere
rep("*Search, screening and inclusion.* Candidate series were sought in the Gene Expression Omnibus",
    "*Search, screening and inclusion.* Candidate series were sought in the Gene Expression Omnibus (GEO)1", "cite GEO")
rep("using context terms combined with platform-annotated processed matrices",
    "using context terms combined with platform-annotated processed matrices, retrieved with GEOquery2", "cite GEOquery")
rep("*Expression processing and QC.* Probes were mapped",
    "*Input data.* The resource is built from {n_series} GEO series whose accessions are listed one by one in 01_cohort_registry/cohort_registry.csv "
    "(26 case-control cohorts plus one treatment-response series that is not part of the case-control resource), from six tumour molecular contexts of "
    "The Cancer Genome Atlas obtained through the Genomic Data Commons3 and cBioPortal4,5, and from four single-cell datasets, three from CELLxGENE "
    "Discover6 (CRC, IBD, STAD) and one GEO series (asthma, GSE193816); the exact dataset versions and collection identifiers are listed in "
    "01_cohort_registry/cellxgene_sources.csv, and every accession is repeated in the Data Availability statement.\n"
    "*Expression processing and QC.* Probes were mapped","input data subsection")
rep("in the bulk cohorts it is a GSVA value z-scored within the cohort",
    "in the bulk cohorts it is a GSVA value7 z-scored within the cohort","cite GSVA")
rep("Compartment scores were estimated with xCell v1.1.0",
    "Compartment scores were estimated with xCell8","cite xCell")
rep("Pooling uses REML heterogeneity with the Hartung-Knapp variance correction",
    "Pooling uses random-effects meta-analysis9 with REML heterogeneity estimation and the Hartung-Knapp10,11 variance correction","cite metafor/HK")
rep("Probes were mapped to gene symbols, multiple probes per gene collapsed by the mean",
    "(probe-to-symbol mapping and probe collapsing used the platform annotation handled by limma12) Probes were mapped to gene symbols, multiple probes per gene collapsed by the mean",
    "cite limma")
rep("software versions are recorded in folder 10.","software versions are recorded in folder 10 (R 4.4.113).","cite R")
# 2. screening wording correction
rep("One series was excluded because it is a treatment-response design, and a further colorectal series was retained for external-validation use only.",
    "One series (GSE16879, inflammatory bowel disease) was excluded because it is a treatment-response design (risponder versus non-responder) and is not part of the "
    "case-control resource, while a further colorectal series (GSE39582) was retained for external-validation use only and is not one of the 26 cohorts.","screening wording")
# 3. single-cell dataset wording (asthma contributed no testable comparison)
rep("astma (8 donors)","asthma (8 donors)")
rep("and asthma (8 donors); one lung dataset was excluded because all cells come from tumour tissue.",
    "and asthma (8 donors). The asthma dataset was prepared with the same pipeline but contributed no comparison to the shipped table because no comparison "
    "satisfied the donor rules after aggregation; one lung dataset was excluded because all cells come from tumour tissue.","asthma wording")
rep("Four datasets contributed contrasts:","Four single-cell datasets were processed and three contributed testable contrasts:","four-to-three wording")
# 4. abbreviations and formulas
rep("the effect is the standardized difference between case and control on the shared denominator sqrt((sd_case^2 + sd_control^2)/2): SMDH for unpaired cohorts and SMCRPH, the paired form using the cohort's empirical within-pair correlation r, for paired cohorts;",
    "the effect is the standardized mean difference between case and control on the shared denominator sqrt((sd_case^2 + sd_control^2)/2), with the small-sample "
    "correction J(df) = 1 - 3/(4 df - 1) (Hedges correction, df = n_case + n_control - 2), giving SMDH in unpaired cohorts; in paired cohorts the same denominator "
    "is applied to the mean paired change with the cohort's empirical within-pair correlation r, giving SMCRPH. The sampling variance follows escalc in metafor "
    "(v = 1/n_case + 1/n_control + yi^2/(2(n_case + n_control)) for SMDH; the paired form replaces the two group sizes with the number of complete pairs and the "
    "correlation r). Abbreviations used below: RELM denotes restricted maximum likelihood, BH Benjamini-Hochberg, FDR false discovery rate, VIF variance inflation factor, "
    "MAD median absolute deviation, OS overall survival, and k the number of cohorts contributing to a pooled estimate;","formulas")
# 5. k=1 handling statement
rep("Pooling uses random-effects meta-analysis9",
    "Pooled estimates are reported only when at least two cohorts contribute; cohort-module pairs with a single contributing cohort are listed in the same table but "
    "are labelled 'single cohort; not a pooled estimate' and carry no p-value, confidence interval or prediction interval. Pooling uses random-effects meta-analysis9",
    "k=1 statement")
# 6. Usage Notes: compress the worked example mention
rep("An external reuse example is shipped and was executed end to end: a gastric cancer series that is not part of the resource "
    "(GSE54129; 111 tumour and 21 adjacent-normal samples) was downloaded from its accession, mapped to gene symbols, transformed by the "
    "same deterministic rule, scored with the frozen modules and compared with the pooled gastric estimates of the resource. "
    "All 17 modules were scorable, the effect direction agreed for 9 of 17 modules, and the complete path took 1.6 minutes on a desktop "
    "workstation (09_reuse_examples/example3_external_cohort_summary.txt). This is reported as an illustration of reuse cost and of the "
    "limits of cross-cohort direction agreement, not as an external validation of the resource. ",
    "Three reusable examples are shipped, including one that rebuilds module scores for a gastric cohort outside the resource from its accession "
    "(09_reuse_examples/example3_external_cohort_summary.txt records the runtime and the observed cross-cohort direction agreement as reuse-cost metrics). ",
    "usage notes compression")
# 7. limitations additions
rep("No minimum number of cells per donor was imposed;",
    "One cohort (GSE62232, hepatocellular carcinoma) contributes only five control samples, so its control-side variance rests on very few samples; "
    "zero-variance genes are absent by construction because matrices were filtered before scoring, which is why the QC column reports zero everywhere; "
    "no minimum number of cells per donor was imposed;","limitations")
# 8. supplementary pointer
rep("The submission package also contains the manuscript, Tables 1 and Supplementary Tables S1-S16, the separate figure-legend file and all four figures.",
    "The submission package also contains the manuscript, Tables 1 and Supplementary Tables S1-S16 as a single PDF with the same tables also shipped here in "
    "machine-readable form, the separate figure-legend file and all four figures; the 165-row consistency detail table is deposited here rather than printed as a "
    "supplementary table.","supplementary pointer")
# 9. section order: move References after Code Availability, Ethics into Methods
rep("**References**\n1. Barrett T", "__REFERENCES_PLACEHOLDER__\n**References**\n1. Barrett T","mark references")
s=s.replace("**Data Availability**","**Data Availability**",1)
rep("**Ethics statement**\nThis work uses only publicly available, de-identified data; no ethical approval or informed consent was required.\n\n",
    "","move ethics")
rep("*Source versions and licences.* Source releases, accessions and licence notes are shipped",
    "*Ethics.* This work uses only publicly available, de-identified data; no ethical approval or informed consent were required.\n*Source versions and licences.* Source releases, accessions and licence notes are shipped",
    "ethics into methods")
# place the references block after Code Availability
s=s.replace("__REFERENCES_PLACEHOLDER__\n**References**\n1. Barrett T","**References**\n1. Barrett T",1)
# 10. punctuation and spelling
s=s.replace("；","; ").replace("signalling","signaling").replace("Signalling","Signaling")
# 11. figure legend error treatment
rep("**Figure 3. Comparability and coupling.**","**Figure 3. Comparability and coupling.**","figure3 noop")
rep("Figure 1 shows coverage and composition","Figure 1 shows coverage and composition","figtext noop")
open(p,"w",encoding="utf-8").write(s); print("generator patched")
