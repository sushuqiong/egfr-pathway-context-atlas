#!/usr/bin/env python3
# -*- coding: utf-8 -*-
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v9\01_稿件正文\Manuscript_draft_v09.md"
s=open(p,encoding="utf-8").read()
n=0
def rep(a,b):
    global s,n
    if a in s: s=s.replace(a,b,1); n+=1
    else: print("STILL MISS:",a[:70])
# 1 lowercase anchor (data freeze line)
rep("external validation cohorts GSE39582 (CRC), GSE21501 (PDAC) and ACRG/GSE62254 (gastric) added September 2026.",
    "external validation cohorts GSE39582 (CRC), GSE21501 (PDAC) and ACRG/GSE62254 (gastric) added September 2026. v9: unified-scale meta-analysis and joint composition models (September 2026).")
# 2 abstract methods lowercase
rep("standardized effects were pooled by within-context random-effects meta-analysis. Cellular composition was estimated by xCell (EPIC cross-check) and module effects re-tested after expression-derived composition adjustment.",
    "standardized effects were pooled by within-context random-effects meta-analysis on a unified two-group effect scale (matched-pair cohorts converted using the estimated within-pair correlation). Cellular composition was estimated by xCell (EPIC cross-check), and module effects were re-tested in joint models adjusting for composition simultaneously with disease status, with two-step xCell residualization retained only as a sensitivity.")
# 3 methods 2.9 single-line variant
rep("Per-sample z-scores were averaged over each program's genes and the higher score assigned the subtype. Module-OS Cox models were re-fit within subtype strata and with subtype interactions.",
    "Per-sample z-scores were averaged over each program's genes and the higher score assigned the subtype; 178 of 179 classified samples had survival data. Module-OS Cox models were re-fit within subtype strata and with subtype interactions. A marker-based purity sensitivity used an expression-derived immune/stromal content score as a purity proxy (proxy = \u2212(immune + stromal z-scores)); this proxy is approximate and is not a measured purity estimate.")
# 4 driver sentence via slice (avoid unicode mismatch)
k="None of the 108 module "
i=s.find(k)
if i>=0:
    j=s.find("detected;", i)
    if j>=0:
        j2=s.find(" however", j)
        if j2<0: j2=s.find("; however", j)
        tail_end=s.find("underpowered (several strata had \u2264 8 events)", j)
        end=s.find(".", tail_end) if tail_end>0 else j+40
        if tail_end>0:
            s=s[:i]+"None of the 108 module \u00d7 driver interaction tests survived BH-FDR, indicating that no statistically supported effect modification of module-OS associations across KRAS/EGFR/TP53/amplification backgrounds was detected; interaction analyses were, however, underpowered (several strata had \u2264 8 events), so this screen does not prove stability across driver backgrounds."+s[end+1:]
            n+=1
        else: print("no tail")
    else: print("no detected")
else: print("no idx")
open(p,"w",encoding="utf-8").write(s)
print("applied", n)
import re
m=re.search(r"## Abstract(.*?)## 1\.", s, re.S)
print("abstract words:", len(re.findall(r"\S+", m.group(1))))
