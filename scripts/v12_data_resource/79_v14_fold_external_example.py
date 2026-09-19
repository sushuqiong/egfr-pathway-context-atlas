#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14: fold the external-cohort reuse example into the manuscript, the package README and the reuse-example
documentation; harden the shipped download-and-rebuild script's probe-to-symbol mapping."""
import os, csv
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; PK=os.path.join(V14,"dataset_package")
# 1. manuscript: report the external reuse example honestly
p=os.path.join(V14,"scripts","70_v14_manuscript.py"); s=open(p,encoding="utf-8").read()
anchor="Maintenance: the resource carries a version number and changelog"
add=("An external reuse example is shipped and was executed end to end: a gastric cancer series that is not part of the resource "
     "(GSE54129; 111 tumour and 21 adjacent-normal samples) was downloaded from its accession, mapped to gene symbols, transformed by the "
     "same deterministic rule, scored with the frozen modules and compared with the pooled gastric estimates of the resource. "
     "All 17 modules were scorable, the effect direction agreed for 9 of 17 modules, and the complete path took 1.6 minutes on a desktop "
     "workstation (09_reuse_examples/example3_external_cohort_summary.txt). This is reported as an illustration of reuse cost and of the "
     "limits of cross-cohort direction agreement, not as an external validation of the resource. ")
assert anchor in s
s=s.replace(anchor, add+anchor, 1); open(p,"w",encoding="utf-8").write(s); print("manuscript generator updated")
# 2. shipped rebuild script: same annotation fallback as the executed example
q=os.path.join(PK,"03_expression","download_and_rebuild_one_series.R"); t=open(q,encoding="utf-8").read()
old='sym_col <- intersect(c("Gene symbol", "GENE_SYMBOL", "Symbol", "gene_assignment"), names(fd))[1]'
old2='sym_col <- intersect(c("Gene symbol","GENE_SYMBOL","Symbol","gene_assignment"), names(fd))[1]'
new=('sym_col <- intersect(c("Gene symbol","Gene Symbol","GENE_SYMBOL","Symbol","gene_assignment","ORF","ILMN_Gene"), names(fd))[1]\n'
     'if (is.na(sym_col)) {                      # fall back to the platform annotation table shipped with the series\n'
     '  gpl <- tryCatch(GEOquery::getGEO(Biobase::annotation(eset)), error = function(e) NULL)\n'
     '  if (!is.null(gpl)) {\n'
     '    tab <- GEOquery::Table(gpl)\n'
     '    cand <- intersect(c("Gene symbol","Gene Symbol","GENE_SYMBOL","Symbol","gene_assignment"), names(tab))\n'
     '    if (length(cand)) { fd <- data.frame(row.names = as.character(tab$ID), sym = as.character(tab[[cand[1]]])); sym_col <- "sym" }\n'
     '  }\n'
     '}\n'
     'cat("using annotation column:", ifelse(is.na(sym_col), "NONE", sym_col), "\\n")')
hit = old if old in t else (old2 if old2 in t else None)
assert hit, "shipped script anchor not found"
t=t.replace(hit,new); open(q,"w",encoding="utf-8").write(t); print("shipped rebuild script hardened")
# 3. reuse-example README
r=os.path.join(PK,"09_reuse_examples","README_examples.md"); c=open(r,encoding="utf-8").read()
c=c.rstrip()+"""

## Example 3 - external cohort rebuilt from its accession (executed)
`example3_external_cohort_rebuild.R` (kept in `scripts/` of the working folder) downloads a gastric cancer series that is **not** part of
the resource (GSE54129; 111 tumour and 21 adjacent-normal samples), maps probes to symbols, applies the same deterministic transformation
rule, scores the frozen modules and compares the effect directions with the pooled gastric estimates of the resource.

Result of the executed run (`example3_external_cohort_summary.txt`, `example3_external_cohort_rebuild.csv`):
all 17 modules were scorable, the direction agreed for 9 of 17 modules, and the complete path took **1.6 minutes**.
This documents reuse cost and the limits of cross-cohort direction agreement; it is not an external validation claim.
"""
open(r,"w",encoding="utf-8").write(c); print("reuse README updated")
# 4. copy the executed example script into the package for reproducibility
src=os.path.join(V14,"scripts","76_v14_external_reuse_example.R")
dst=os.path.join(PK,"09_reuse_examples","example3_external_cohort_rebuild.R")
open(dst,"w",encoding="utf-8").write(open(src,encoding="utf-8").read()); print("example 3 script shipped")
