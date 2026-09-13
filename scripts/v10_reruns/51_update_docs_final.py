#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
V10=r"C:\Users\fengq\Desktop\EGFR\EGFR的v10"
REPO=r"C:\Users\fengq\Desktop\EGFR\egfr-pathway-context-atlas"
def patch(path, pairs, must=False):
    s=open(path,encoding="utf-8").read(); n=0
    for a,b in pairs:
        if a in s: s=s.replace(a,b); n+=1
        elif must: print("MISS in",os.path.basename(path),":",a[:60])
    open(path,"w",encoding="utf-8").write(s); return n
# checklist v10
patch(os.path.join(V10,"06_投稿清单与流程","Submission_readiness_checklist_v10.md"), [
 ("**REML/Hartung-Knapp 7**（IBD 6 + COPD 1）、**DerSimonian-Laird 20**（IBD 11/COPD 5/Asthma 4）",
  "**REML/Hartung-Knapp 18**（CRC 8、IBD 6、LUAD 2、PAAD 1、COPD 1；固定 ρ=0.5/0.7 下为 19）、**DerSimonian-Laird 76**"),
 ("- [x] 配对效应量 200/200 可估（median ri=0.99），固定 ρ=0.5/0.7 结果一致（7=7=7）",
  "- [x] 配对效应量 200/200 可估（median ri=0.11），固定 ρ=0.5/0.7 得到 19 vs 实证 18（敏感性披露）"),
 ("- [ ] 洗牌样本顺序后按 ID 连接结果一致（脚本已备，投前跑一次留档）",
  "- [x] 洗牌样本顺序后按 ID 连接结果一致（tests/check_paired_effect.R：yi/vi 完全一致）"),
 ("- [ ] 从原始输入完整运行两次核心结果一致（同上）",
  "- [x] 重复运行结果一致（同上，第二次完全一致）"),
])
# v16 report numbers
patch(os.path.join(V10,"04_评审记录与报告","v16_bugfix_recompute.md"), [
 ("| Meta REML/Hartung–Knapp（BH）| 11 | **7**（IBD 6：ERBB-R↓/HGF-MET/JAK-STAT/SRC-FAK/TIE/VEGF + COPD SRC-FAK↓）|",
  "| Meta REML/Hartung–Knapp（BH）| 11 | **18**（CRC 8、IBD 6、LUAD 2、PAAD 1 RAS-MAPK、COPD 1；固定 ρ=0.5/0.7 下 19）|"),
 ("| Meta DL（BH）| 31 | **20**（IBD 11、COPD 5、Asthma 4）|",
  "| Meta DL（BH）| 31 | **76**（CRC 12、LUAD 12、IBD 11、STAD 9、PAAD 8、ESCC 7、HCC 7、COPD 5、Asthma 5）|"),
 ("现 **200/200 配对记录全部可估**（median r_emp=0.99）",
  "现 **200/200 配对记录全部可估**（median r_emp=0.11；另经第二轮修复：先取子集值再按 ID 匹配，并用 tests/check_paired_effect.R 三检验验证）"),
])
# repo README numbers
patch(os.path.join(REPO,"README.md"), [
 ("unified-scale meta REML/Hartung-Knapp **7** (DL **20**)","unified-scale meta REML/Hartung-Knapp **18** (DL **76**; 19 at fixed rho 0.5/0.7)"),
])
# repo ERRATA second-pass note
p=os.path.join(REPO,"ERRATA_v10.md"); s=open(p,encoding="utf-8").read()
s += """

## Second-pass correction (within v10)
After the first v10 re-analysis, the verification suite (hand calculation vs metafor; sample-order shuffle; repeated run) revealed that the paired fix was still incomplete: `y[match(cc, case_ids)]` indexes the full vector with positions from the case subset, which is only correct when cases happen to occupy the leading rows. The implementation now subsets first and then matches values (`y_case <- y[case]; yc <- y_case[match(cc, id_case)]`). With the corrected indexing the median empirical within-pair correlation is **0.11** (not 0.99), and the final v10 numbers are: per-cohort 55/170; unified-scale meta **REML/Hartung-Knapp 18** (19 at fixed rho 0.5/0.7), **DL 76**; joint-model composition-robust **21** (CRC 10, STAD 9, ESCC 1, IBD 1; PAAD 0); CRC external 556/187 with VEGF/PDGF directionally consistent but not stage-robust. Verification logs are in `tests/check_paired_effect_log.txt`.
"""
open(p,"w",encoding="utf-8").write(s)
print("docs updated")
