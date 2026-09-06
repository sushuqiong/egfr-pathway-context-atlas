#!/usr/bin/env python3
# -*- coding: utf-8 -*-
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v9\01_稿件正文\Manuscript_draft_v09.md"
s=open(p,encoding="utf-8").read()
a=("**Figure 2. Module atlas heatmaps.** (A) Raw median standardized mean difference (SMD) across ten contexts; "
   "(B) after xCell composition residualization. Digits = number of cohorts with FDR<0.05; asterisks = per-cohort "
   "robust states (A) or xCell-composition-robust states (B).")
b=("**Figure 2. Module atlas heatmaps.** (A) Raw median standardized mean difference (SMD) across ten contexts "
   "(asterisk = per-cohort-robust state; digits = cohorts with FDR<0.05). (B) Joint composition models "
   "(module ~ disease + epithelial/fibroblast/endothelial/immune scores [+ matched-patient factor]); fill = median "
   "adjusted difference in SD units, digits = cohorts with joint FDR<0.05, filled diamonds = joint-composition-robust "
   "states. The two-step xCell residualization version is provided as Supplementary Figure S2.")
if a in s:
    s=s.replace(a,b,1); print("Fig2 legend updated")
else: print("MISS Fig2 legend")
marker="**Supplementary Figure S1. Marker-proxy vs xCell medians.**"
add_s2=("**Supplementary Figure S1. Marker-proxy vs xCell medians.**\n\n"
        "**Supplementary Figure S2. xCell two-step residualization heatmap (sensitivity).** Module effects re-tested "
        "after residualization on expression-derived compartment scores; digits = number of cohorts with FDR<0.05, "
        "asterisks = states robust under this sensitivity.")
if marker in s:
    s=s.replace(marker, add_s2,1); print("Supp S2 legend added")
else: print("MISS supp anchor")
open(p,"w",encoding="utf-8").write(s)
print("done")
