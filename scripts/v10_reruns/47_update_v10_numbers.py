#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
P=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10\01_稿件正文\Manuscript_draft_v10.md"
s=open(P,encoding="utf-8").read()
def sec(s, a, b, new):
    i=s.find(a); j=s.find(b); assert i>=0 and j>i, (a,b); return s[:i]+new+s[j:]
# abstract
s=s.replace("conservative meta-analysis retained 7 states (20 under DerSimonian-Laird), and joint composition models retained 21 (CRC 10, STAD 9, ESCC 1, IBD 1; no PAAD state)",
            "conservative meta-analysis retained 18 states (76 under DerSimonian-Laird), and joint composition models retained 21 (CRC 10, STAD 9, ESCC 1, IBD 1; no PAAD state)")
# 3.1
r31 = """### 3.1 Atlas overview, unified-scale meta-analysis [Fig 1, Fig 2; Table 1]
Across 170 context-module summaries, 55 states were per-cohort robust (LUAD 14, CRC 11, STAD 10, PAAD 10, ESCC 4, IBD 6; none in HCC, COPD, NAFLD or asthma by the per-cohort rule), which remains the pre-specified primary readout. For meta-analysis, effects were expressed on a common two-group scale (Hedges' g for unpaired cohorts; standardized mean change with empirically estimated within-pair correlation for matched cohorts: all 200 paired records were estimable, median ri = 0.11). Conservative REML/Hartung-Knapp inference retained 18 pooled-significant states (CRC 8, IBD 6, LUAD 2, PAAD 1, COPD 1; Fig 1), whereas DerSimonian-Laird pooling identified 76 (BH-FDR, k \\u2265 2). The CRC signals included WNT/\\u03b2-catenin (+2.71), EPH (+2.10) and coordinated downregulation of FGFR (\\u22121.58), PDGFR-KIT (\\u22121.01), IGF/INSR (\\u22120.91), TGF\\u03b2/SMAD (\\u22120.52), TIE/Ang (\\u22120.22) and ERBB ligands (\\u22120.44); IBD showed JAK-STAT (+1.78), HGF/MET (+1.52), VEGF/PDGF (+1.30), TIE/Ang (+1.14), SRC/FAK (+0.45) and ERBB-receptor downregulation (\\u22121.28); LUAD showed FGFR (\\u22121.88) and JAK-STAT (\\u22120.99) downregulation; PAAD showed RAS-MAPK (+1.11); and COPD showed SRC/FAK downregulation (\\u22120.28). Fixed-correlation sensitivity analyses (ri = 0.5 and 0.7) retained 19 states, adding CRC JAK-STAT. NAFLD remained null at every level within the power of the available cohorts.

"""
s=sec(s,"### 3.1 Atlas overview","### 3.2 Cancer architectures",r31)
# 3.3
r33 = """### 3.3 Benign contexts [Fig 2; Table 1]
IBD was the benign context with the strongest and most consistent signals (six of the 18 conservative meta-analysis states: JAK-STAT +1.78, HGF/MET +1.52, VEGF/PDGF +1.30, TIE/Ang +1.14, SRC/FAK +0.45 and ERBB-receptor downregulation \\u22121.28), of which only JAK-STAT was also composition-robust in joint models; single-cell data attribute this JAK-STAT state to colonic epithelium and myeloid cells (Results 3.5). COPD contributed one small conservative meta-analysis signal (SRC/FAK \\u22120.28) and asthma contributed none once the conservative inference was applied (five asthma states appeared at DerSimonian-Laird level only). No module difference was found for NAFLD in the available cohorts.

"""
s=sec(s,"### 3.3 Benign contexts","### 3.4 Composition adjustment",r33)
# 4.1
d41 = """### 4.1 Principal findings
We assembled a transcriptional atlas of growth-factor pathway modules across six cancers and four chronic benign diseases and subjected every candidate signal to cross-cohort, composition, single-cell and prognostic filters. The disciplined outcome is a graded evidence structure rather than a shortlist: 55 of 170 states were per-cohort robust, 18 survived conservative unified-scale meta-analysis (CRC 8, IBD 6, LUAD 2, PAAD 1, COPD 1), 21 were composition-robust in joint models (dominated by CRC and STAD), and no state passed strict external replication. This is best framed as a composition-aware hypothesis generator, with an explicit per-state evidence matrix (Table S9) that separates states that were not analysed, could not be estimated, were estimated without significance, and met robustness criteria.

"""
s=sec(s,"### 4.1 Principal findings","### 4.2 Composition shapes",d41)
# 4.8 fixes
s=s.replace("using an empirical within-pair correlation (median 0.99)","using an empirical within-pair correlation (median 0.11)")
s=s.replace("fixed-correlation sensitivity analyses gave identical pooled results but the assumption remains",
            "fixed-correlation sensitivity analyses retained 19 versus 18 states, and the common-correlation assumption remains")
open(P,"w",encoding="utf-8").write(s)
print("numbers updated")
