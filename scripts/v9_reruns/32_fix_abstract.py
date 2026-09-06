#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
p=r"C:\Users\fengq\Desktop\EGFR\EGFR的v9\01_稿件正文\Manuscript_draft_v09.md"
s=open(p,encoding="utf-8").read()
i=s.find("## Abstract"); j=s.find("## 1. Introduction")
new_abs=("## Abstract\n\n"
"**Background.** Receptor-tyrosine-kinase (RTK) pathway transcriptional states are context dependent, yet how they "
"compare across cancers and chronic benign diseases, how much bulk tissue signal reflects cellular composition, and "
"whether surviving signals carry reproducible prognostic value remain unclear.\n\n"
"**Methods.** Seventeen growth-factor pathway modules were scored in 27 public case-control cohorts spanning ten "
"contexts (six cancers, four chronic diseases), with discovery-validation separation, per-cohort BH-FDR, and "
"within-context random-effects meta-analysis on a unified two-group effect scale (matched cohorts converted using "
"estimated within-pair correlation). Composition was estimated by xCell, and module effects were re-tested in joint "
"models adjusting for composition simultaneously with disease status. Patient-level single-cell data localized "
"surviving signals. TCGA module-OS associations (108 tests) were assessed with age/stage sensitivity, driver "
"stratification and external validation in independent CRC (GSE39582), PDAC (GSE21501) and gastric (ACRG/GSE62254) cohorts.\n\n"
"**Results.** Fifty-five of 170 states were per-cohort robust; conservative REML/Hartung-Knapp pooling retained 11 "
"pooled states (31 under DerSimonian-Laird). In joint composition models only six states remained robust (CRC "
"WNT/\u03b2-catenin, EPH, FGFR and IGF/INSR loss, VEGF/PDGF; IBD JAK-STAT), and all PAAD bulk effects were strongly "
"attenuated. In TCGA, 17/108 module-OS associations were FDR<0.05 and 11/15 testable signals survived age+stage "
"adjustment. Externally, CRC VEGF/PDGF (HR 1.21) and three of five STAD vascular/stromal signals were replicated, "
"whereas CRC ERBB-ligand and all seven PAAD module-OS signals were not reproduced.\n\n"
"**Conclusions.** Most bulk RTK-related transcriptional differences track tissue composition and clinical "
"background. A minority of composition-robust, cell-source-localized states provide composition-aware, "
"evidence-tiered hypotheses for context-dependent biology rather than direct evidence of pathway activation or "
"therapeutic actionability.\n\n")
s=s[:i]+new_abs+s[j:]
# driver sentence fix via regex
pat=re.compile(r"None of the 108 module .*?8 events\)\.")
rep="None of the 108 module \u00d7 driver interaction tests survived BH-FDR, indicating that no statistically supported effect modification of module-OS associations across KRAS/EGFR/TP53/amplification backgrounds was detected; interaction analyses were, however, underpowered (several strata had \u2264 8 events), so this screen does not prove stability across driver backgrounds."
s2,n=pat.subn(rep, s, count=1)
print("driver replaced:",n)
s=s2
open(p,"w",encoding="utf-8").write(s)
words=len(re.findall(r"\S+", re.search(r"## Abstract(.*?)## 1\.", s, re.S).group(1)))
print("abstract words:", words)
for probe in ["v9: unified-scale","joint composition models","six states remained","REML/Hartung-Knapp pooling retained 11","composition-aware"]:
    print(probe,"->",s.count(probe))
