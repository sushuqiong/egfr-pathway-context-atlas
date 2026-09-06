#!/usr/bin/env python3
# -*- coding: utf-8 -*-
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v9\01_稿件正文\Manuscript_draft_v09.md"
s=open(p,encoding="utf-8").read()
# 1) driver sentence explicit fix
i=s.find("None of the 108 module")
if i>=0:
    k=s.find("events)", i)
    if k>=0:
        end=s.find(".", k)
        if end>0:
            repl=("None of the 108 module \u00d7 driver interaction tests survived BH-FDR, indicating that no "
                  "statistically supported effect modification of module-OS associations across KRAS/EGFR/TP53/"
                  "amplification backgrounds was detected; interaction analyses were, however, underpowered "
                  "(several strata had \u2264 8 events), so this screen does not prove stability across driver backgrounds.")
            s=s[:i]+repl+s[end+1:]
            print("driver fixed")
# 2) sweep stale phrases
stale=["only 4 pooled-significant","73 at k \u2265 2","After xCell adjustment only 19","19 states remained composition-robust",
 "CRC 10, STAD 8, ESCC 1","eight composition-robust states","pooled HGF/MET +1.20, RAS-MAPK","carried entirely by non-amplified",
 "was prospective","Multi-axis activation","not explained by molecular subtype or by tumour purity","Methods 2.10). The TCGA-adverse PAAD",
 "remained composition-robust after xCell adjustment","19 remained composition","1.20, RAS-MAPK","ERBB ligands +0.39","Driver stratification as a negative control"]
for ph in stale:
    c=s.count(ph)
    if c: print("STALE",c,":",ph)
open(p,"w",encoding="utf-8").write(s)
print("done")
