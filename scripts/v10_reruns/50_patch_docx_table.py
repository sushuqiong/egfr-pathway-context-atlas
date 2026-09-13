#!/usr/bin/env python3
# -*- coding: utf-8 -*-
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\reruns\scripts\46_build_v10_docx.py"
s=open(p,encoding="utf-8").read()
pairs=[
 ("['LUAD','14','0','0','0','0','—']","['LUAD','14','2','12','0','0','—']"),
 ("['CRC','11','0','0','10','10','VEGF direction only (not stage-robust)']","['CRC','11','8','12','10','10','VEGF direction only (not stage-robust)']"),
 ("['STAD','10','0','0','9','8','3/5 direction only (ACRG)']","['STAD','10','0','9','9','8','3/5 direction only (ACRG)']"),
 ("['PAAD','10','0','0','0','0','none replicated (GSE21501)']","['PAAD','10','1','8','0','0','none replicated (GSE21501)']"),
 ("['HCC','0','0','0','0','0','—']","['HCC','0','0','7','0','0','—']"),
 ("['ESCC','4','0','0','1','1','—']","['ESCC','4','0','7','1','1','—']"),
 ("['IBD','6','6','11','1','0','—']","['IBD','6','6','11','1','0','—']"),
 ("['COPD','0','1','5','0','0','—']","['COPD','0','1','5','0','0','—']"),
 ("['Asthma','0','0','4','0','0','—']","['Asthma','0','0','5','0','0','—']"),
]
n=0
for a,b in pairs:
    if a in s:
        if a!=b: s=s.replace(a,b,1); n+=1
    else: print("MISS",a[:40])
open(p,"w",encoding="utf-8").write(s)
print("rows changed:",n)
