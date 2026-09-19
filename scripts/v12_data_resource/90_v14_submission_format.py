#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v14 submission formatting: figures exported as cairo PDFs with embedded fonts, Supplementary_Information.pdf
produced from the tables document, and the 165-row detail table replaced by a repository pointer."""
import csv, os, shutil, subprocess
V14=r"C:\Users\fengq\Desktop\EGFR\EGFR的v14"; R=os.path.join(V14,"results"); PK=os.path.join(V14,"dataset_package")
TBL=os.path.join(V14,"03_tables")
# 1. printfigure script: use cairo_pdf for the PDF outputs so fonts are embedded
p=os.path.join(V14,"scripts","60_v14_figures.R"); s=open(p,encoding="utf-8").read()
if "cairo_pdf" not in s:
    s=s.replace('ggsave(file.path(F,"Fig1_resource_overview.pdf"), fig1, width=W, height=9.3)',
                'ggsave(file.path(F,"Fig1_resource_overview.pdf"), fig1, width=W, height=9.3, device=cairo_pdf)')
    s=s.replace('ggsave(file.path(F,"Fig2_technical_validation.pdf"), p2a / p2b / p2c, width=W, height=8.2)',
                'ggsave(file.path(F,"Fig2_technical_validation.pdf"), p2a / p2b / p2c, width=W, height=8.2, device=cairo_pdf)')
    s=s.replace('ggsave(file.path(F,"Fig3_comparability_checks.pdf"), fig3, width=W, height=8.6)',
                'ggsave(file.path(F,"Fig3_comparability_checks.pdf"), fig3, width=W, height=8.6, device=cairo_pdf)')
    s=s.replace('ggsave(file.path(F,"Fig4_sensitivity_checks.pdf"), p4a / p4b, width=W, height=7.4)',
                'ggsave(file.path(F,"Fig4_sensitivity_checks.pdf"), p4a / p4b, width=W, height=7.4, device=cairo_pdf)')
    open(p,"w",encoding="utf-8").write(s); print("figure script switched to cairo_pdf")
# 2. tables document: replace the 165-row S10 with a pointer (large tables belong in the repository)
q=os.path.join(V14,"scripts","71_v14_tables_legends.py"); t=open(q,encoding="utf-8").read()
old = '''head(doc,"Supplementary Table S10. Cross-cohort direction consistency, all context-module pairs")
con=[r for r in rd(os.path.join(R,"v13_qc_cross_cohort_consistency.csv")) if int(r["k"])>=2]
three_line(doc,["Context","Module","Cohorts","Cohorts with positive effect","Cohorts with negative effect","Median effect","Same direction in all cohorts"],
  [[r["disease"],r["feature"],r["k"],r["n_pos"],r["n_neg"],round(float(r["median_yi"]),3),r["direction_consistent"]] for r in con],7.5)'''
new = '''head(doc,"Supplementary Table S10. Cross-cohort direction consistency (summary; detail deposited)")
con=[r for r in rd(os.path.join(R,"v13_qc_cross_cohort_consistency.csv")) if int(r["k"])>=2]
same=sum(1 for r in con if str(r["direction_consistent"]).upper()=="TRUE")
three_line(doc,["Statistic","Value"],[
 ["Context-module pairs with at least two cohorts", len(con)],
 ["Pairs whose effect direction is the same in every contributing cohort", f"{same} ({100*same/max(1,len(con)):.0f}%)"],
 ["Detail (one row per pair with cohort counts, sign counts and median effect)","deposited as 08_qc/qc_cross_cohort_consistency.csv (165 rows); not printed here because oversized tables are deposited rather than printed"]],8)'''
if old in t:
    t=t.replace(old,new); open(q,"w",encoding="utf-8").write(t); print("S10 replaced by a pointer in the tables builder")
else:
    print("WARNING: S10 block not found in the tables builder")
