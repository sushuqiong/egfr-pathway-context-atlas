#!/usr/bin/env python3
# -*- coding: utf-8 -*-
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v9\01_稿件正文\Manuscript_draft_v09.md"
s=open(p,encoding="utf-8").read()
i=s.find("**Figure 6.")
j=s.find("## Tables")
if i>=0 and j>i:
    seg=s[i:j]
    # end of figure6 paragraph = first blank line after its text
    k=seg.find("\n\n")
    if k<0: k=len(seg)
    ins=("\n\n**Supplementary Figure S1. Marker-proxy vs xCell medians.** Adjusted medians by the marker-proxy "
         "sensitivity version versus xCell residualization across 170 states (Spearman rho = 0.81).\n\n"
         "**Supplementary Figure S2. xCell two-step residualization heatmap (sensitivity).** Module effects re-tested "
         "after residualization on expression-derived compartment scores; digits = number of cohorts with FDR<0.05, "
         "asterisks = states robust under this sensitivity version.")
    s=s[:i+k]+ins+s[i+k:]
    open(p,"w",encoding="utf-8").write(s)
    print("supp legends inserted; S1 count:",s.count("Supplementary Figure S1"),"S2:",s.count("Supplementary Figure S2"))
else:
    print("anchor issue", i, j)
